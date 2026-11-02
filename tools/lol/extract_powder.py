r"""Pull Powder's voice out of the local League of Legends installs.

    python tools/lol/extract_powder.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream path\vgmstream-cli.exe

Her sound effects stay the base game's own (tools/kit/setup_powder.py). Her voice (the user 2026-11-02: 「所有已经完成的tft
英雄都要补」, voice lines for every finished tft hero) is set 13's: MODE_TFT_Set13_Champs_VO holds one event for her,
Play_vo_TFT13_BlueSpell_OnCast (TFT13_Blue is Powder), three takes; the WeGame client's zh_CN Map22 keeps them under the
en_us path, the same takes as the Riot client's en_US (as Vander's), and is read first. One take a cast: the longest
(1.2 s) on the ult, the others on the monkey bomb and the run. Read, never written; decoded with vgmstream and written
as mono 16-bit WAVs to tft/sound/sfx/ (git-ignored: audio (c) Riot Games).
"""
import argparse
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "tft")
C = "tft_powder_sfx_"
VO = "Play_vo_TFT13_BlueSpell_OnCast"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "q_vo": ("tft13_vo", [VO], 2.0, -3, 1),
    C + "e_vo": ("tft13_vo", [VO], 2.0, -3, 2),
    C + "r_vo": ("tft13_vo", [VO], 2.0, -3, 0),   # the longest take (1.2 s)
}
VO13 = "assets/sounds/wwise2016/vo/{lang}/shared/mode_tft_set13_champs_vo_"


def banks_of(src, a, cache):
    """The set-13 voice banks (events + audio), read once."""
    if src in cache:
        return cache[src]
    tries = [(a.lol, "Map22.zh_CN.wad.client", "zh_cn"), (a.lol, "Map22.zh_CN.wad.client", "en_us"),
             (a.riot, "Map22.zh_CN.wad.client", "zh_cn"), (a.riot, "Map22.en_US.wad.client", "en_us")]
    for base, wad, lang in tries:
        path = os.path.join(base, "Game", "DATA", "FINAL", "Maps", "Shipping", wad)
        if not os.path.isfile(lp(path)):
            continue
        w = Wad(path)
        stem = VO13.format(lang=lang)
        if not w.has(stem + "events.bnk"):
            continue
        audio = w.read_path(stem + "audio.bnk")
        media = dict(bnk_media(audio))
        if w.has(stem + "audio.wpk"):
            media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
        cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
        print(f"voice from {wad} ({lang})")
        break
    else:
        sys.exit("no MODE_TFT_Set13_Champs_VO bank in either client")
    return cache[src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map22 with set 13)")
    ap.add_argument("--lol", required=True, help="the WeGame client's League of Legends folder")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (src, events, max_s, peak, *pick) in CLIPS.items():
        banks = banks_of(src, a, cache)
        event, variants = None, []
        for ev in events:
            variants = banks.event_media(ev)
            if variants:
                event = ev
                break
        if not variants:
            sys.exit(f"{name}: none of {events} resolves in {src} - game patch changed the bank?")
        sr, x = decode(banks.media[variants[pick[0] if pick else 0]], a.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:26s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
