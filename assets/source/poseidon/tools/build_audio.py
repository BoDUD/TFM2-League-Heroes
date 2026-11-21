"""Build original Foley and cut reviewed excerpts from local source media."""
import argparse
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal
import soundfile as sf

from build_art import DIST, HERO, ROOT, sha, write_json


SR = 44100
RANDOM = np.random.default_rng(20261121)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
AUDIO = ROOT / "audio"
SOURCES = {
    "countdown": {
        "url": "https://twitter.com/ragnarok_PR/status/1402823584263905283",
        "evidence": "https://ragnarok-official.com/1st/news/127/",
        "background": "quiet official character countdown recording",
    },
    "duel": {
        "url": "https://www.youtube.com/watch?v=Yrlpp7fW6II",
        "evidence": "https://ragnarok-official.com/1st/movie/",
        "speaker_segment": [14.86, 27.99],
        "background": "official duel PV with music and ambient effects",
    },
}


def clock(seconds):
    return np.arange(round(SR * seconds)) / SR


def noise(t, low, high):
    filt = signal.butter(3, [low, high], btype="bandpass", fs=SR, output="sos")
    return signal.sosfilt(filt, RANDOM.normal(0, 1, len(t)))


def wind(seconds, pitch):
    t = clock(seconds)
    env = np.sin(np.pi * t / seconds) ** 2 * np.exp(-2.6 * t / seconds)
    return env * (.75 * noise(t, 420, 6700) + .1 * signal.chirp(t, pitch, seconds, 240))


def hit(seconds, weight, pitch):
    t = clock(seconds)
    pulse = np.sin(2 * np.pi * (pitch * t - 34 * t * t))
    return (noise(t, 450, 7200) * np.exp(-t * 93) * .55
            + noise(t, 110, 1200) * np.exp(-t * 29) * .44
            + pulse * np.exp(-t * 40) * weight)


def power(seconds, start, end, attack):
    t = clock(seconds)
    u = t / seconds
    env = u ** 1.4 if attack else np.exp(-6 * u)
    low = signal.chirp(t, start, seconds, end)
    metallic = signal.chirp(t, start * 3.1, seconds, end * 3.4)
    return (low * .42 + metallic * .09 + noise(t, 260, 4700) * .23) * env


def encode(name, samples, kind, peak):
    master = AUDIO / kind / f"{HERO}_{name}.wav"
    runtime = DIST / "sound/sfx" / master.with_suffix(".mp3").name
    master.parent.mkdir(parents=True, exist_ok=True)
    runtime.parent.mkdir(parents=True, exist_ok=True)
    data = samples.astype(np.float64)
    data -= data.mean()
    amplitude = float(np.abs(data).max())
    assert amplitude > 1e-4, name
    data *= peak / amplitude
    fade = min(round(.014 * SR), len(data) // 10)
    data[:fade] *= np.linspace(0, 1, fade)
    data[-fade:] *= np.linspace(1, 0, fade)
    sf.write(master, data, SR, subtype="PCM_16")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(master), "-c:a", "libmp3lame",
                    "-b:a", "160k", str(runtime)], check=True)
    return {"id": name, "wav": master.relative_to(ROOT).as_posix(),
            "mp3": runtime.relative_to(ROOT).as_posix(), "ms": round(len(data) / SR * 1000),
            "wav_sha256": sha(master), "mp3_sha256": sha(runtime)}


def effects():
    clips = {}
    for i in range(3):
        clips[f"thrust_wind_{1 + i}"] = wind(.135 + .018 * i, 1450 + 120 * i)
        clips[f"thrust_hit_{1 + i}"] = hit(.205 + .018 * i, .82 + .05 * i, 91 + 5 * i)
    clips.update({
        "undertow": power(.30, 340, 138, False),
        "flurry_wind": np.concatenate([wind(.08, 2050 + i * 190) for i in range(4)]),
        "flurry_hit": hit(.24, 1.12, 98),
        "rain_rise": power(.29, 350, 780, True),
        "rain_drop": wind(.26, 3080) + power(.26, 420, 140, False) * .35,
        "rain_hit": hit(.29, 1.16, 79) + power(.29, 205, 150, False) * .22,
        "flood_charge": power(.41, 112, 330, True) + wind(.41, 900) * .5,
        "flood_barrage": np.concatenate([wind(.05, 2300+i*180) for i in range(7)]),
        "flood_hit": hit(.35, 1.38, 67) + power(.35, 181, 55, False) * .47,
        "trident_drop": hit(.28, .58, 107) + power(.28, 910, 690, False) * .19,
        "body_fall": hit(.23, .62, 60),
    })
    return [dict(encode(f"sfx_{key}", samples, "sfx", .75), origin="original Foley")
            for key, samples in clips.items()]


def decoded(path):
    result = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                             "-af", "highpass=f=84,lowpass=f=9600", "-f", "f32le", "pipe:1"],
                            capture_output=True, check=True)
    return np.frombuffer(result.stdout, dtype=np.float32)


def voices(inputs):
    pcm = {name: decoded(path) for name, path in inputs.items()}
    hashes = {name: sha(path) for name, path in inputs.items()}
    cuts = json.loads((AUDIO / "voice_cuts.json").read_text(encoding="utf-8"))
    entries = []
    for cut in cuts:
        name, source = cut["id"], cut["source"]
        start, end = (round(cut[field] * SR) for field in ("start", "end"))
        assert 0 <= start < end <= len(pcm[source]), cut
        entries.append(dict(encode(f"vo_{name}", pcm[source][start:end], "voice_ja", .84),
                            **{key: val for key, val in cut.items() if key != "id"},
                            language="ja", speaker="Poseidon / Takahiro Sakurai", source_sha256=hashes[source]))
    return entries


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("countdown", type=Path)
    parser.add_argument("duel", type=Path)
    args = parser.parse_args()
    write_json(AUDIO / "manifest.json", {
        "format": {"sha": "sha256", "master": "PCM16 mono 44100 Hz", "runtime": "MP3 mono 160 kb/s"},
        "sources": SOURCES, "sfx": effects(), "voice": voices(vars(args)),
    })
