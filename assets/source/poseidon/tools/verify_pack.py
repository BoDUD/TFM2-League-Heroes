"""Verify files reread from disk, update the offline preview, and package them."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
from PIL import Image

from build_art import CELL, DIST, HD, HERO, ROOT, sha, write_json
from build_art import dominant, make_bodies
import trident


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_sheet(stem, spans):
    sprites = DIST / "sprites"
    native = np.asarray(Image.open(sprites / f"{stem}_native#sheet.png"))
    hd = np.asarray(Image.open(sprites / f"{stem}#sheet.png"))
    size = (CELL * len(spans), CELL * 8, 4)
    assert native.shape == size and hd.shape == (size[0] * HD, size[1] * HD, 4)
    for y in range(HD):
        for x in range(HD):
            assert np.array_equal(hd[y::HD, x::HD], native)
    assert set(np.unique(native[:, :, 3])) == {0, 255}
    assert not native[native[:, :, 3] == 0, :3].any()
    assert len({v["row"] for v in spans.values()}) == len(spans)

    for scale, suffix in ((1, "_native"), (HD, "")):
        anim = read(sprites / f"{stem}{suffix}#anim.fanim")["anims"]
        cell = CELL * scale
        assert anim.keys() == spans.keys()
        for action, span in spans.items():
            row = span["row"]
            frames = anim[action]["frames"]
            distinct = set()
            assert len(frames) == span["frames"] == 8
            for col, frame in enumerate(frames):
                assert frame["data"] == {"x": col * cell, "y": row * cell, "w": cell, "h": cell}
                assert round(frame["duration"] * 1000) == span["ms"][col] > 0
                logical = native[row * CELL:(row + 1) * CELL, col * CELL:(col + 1) * CELL]
                box = Image.fromarray(logical).getbbox()
                assert box and list(box) == span["bounds"][col]
                assert box[0] >= 2 and box[1] >= 2 and box[2] <= 126 and box[3] <= 126
                distinct.add(logical.tobytes())
            assert len(distinct) == len(frames), action


def verify_stills(art):
    for icon in (DIST / "icons").glob("*.png"):
        assert Image.open(icon).size == (256, 256)
    assert len(list((DIST / "icons").glob(f"{HERO}_*.png"))) == 4
    card = np.asarray(Image.open(DIST / f"banpick_illustrations/{HERO}.png"))
    assert card.shape == (405, 304, 4) and not card[:48, :, 3].any() and (card[48:, :, 3] == 255).all()
    full = Image.open(ROOT / f"art/illustration/{HERO}_1216x1428.png")
    assert full.size == (1216, 1428)
    raw = Image.open(ROOT / "art/card.png").convert("RGB")
    assert list(raw.size) == art["card"]["original"]
    x, y = art["card"]["offset"]
    assert np.array_equal(full.crop((x, y, x + raw.width, y + raw.height)), raw)
    for name, digest in art["source_sha256"].items():
        assert sha(ROOT / "art" / name) == digest


def verify_audio(sound):
    import imageio_ffmpeg
    import soundfile as sf

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for clip in [*sound["voice"], *sound["sfx"]]:
        wav = ROOT / clip["wav"]
        mp3 = ROOT / clip["mp3"]
        assert sha(wav) == clip["wav_sha256"] and sha(mp3) == clip["mp3_sha256"]
        info = sf.info(wav)
        assert (info.channels, info.samplerate, info.subtype) == (1, 44100, "PCM_16")
        assert round(info.duration * 1000) == clip["ms"]
        if "source" in clip:
            assert clip["source"] in sound["sources"]
            assert abs(round(1000 * (clip["end"] - clip["start"])) - clip["ms"]) <= 1
        subprocess.run([ffmpeg, "-v", "error", "-i", str(mp3), "-f", "null", "-"], check=True)


def verify_cues(cues, art, sound):
    audio_ids = {clip["id"] for clip in sound["sfx"]}
    for cue in cues["cues"]:
        assert 0 <= cue["ms"] < sum(art["actor"][cue["action"]]["ms"])
        assert len(cue["anchor"]) == 2 and all(0 <= val < CELL for val in cue["anchor"])
        assert cue["sfx"] in audio_ids
        if "fx" in cue:
            assert cue["fx"] in art["fx"]


def verify_weapon(art):
    grips = ROOT / "grips.json"
    assert sha(grips) == art["weapon"]["grips_sha256"]
    raw = Image.open(ROOT / "art/trident.png").convert("RGBA")
    prop, axis = trident.template(dominant(raw, False))
    assert np.array_equal(prop, Image.open(ROOT / art["weapon"]["source"]))
    assert art["weapon"]["span_px"] == prop.width
    atlas = Image.open(DIST / f"sprites/{HERO}_native#sheet.png")
    sockets = read(grips)
    for action, frames in make_bodies().items():
        row = art["actor"][action]["row"]
        for col, body in enumerate(frames):
            equipped, tip = trident.attach(body, prop, axis, sockets[action][col])
            frame = atlas.crop((col * CELL, row * CELL, (col + 1) * CELL, (row + 1) * CELL))
            assert np.array_equal(equipped, frame), (action, col)
            assert tip == art["weapon"]["tip_by_frame"][action][col]
    drop_frames = sockets["dead"][3:]
    assert all(pose == drop_frames[0] and not pose[-1] for pose in drop_frames)
    assert all(sockets[action][i][2] == 0 for action in ("attack", "skill") for i in (3, 4))


def pack(output, audio):
    files = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(ROOT.rglob("*"))
             if p.is_file() and not ({".git", "__pycache__"} & set(p.relative_to(ROOT).parts))}
    local = output / "poseidon_assets"
    for name in files:
        dest = local / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
        assert sha(dest) == files[name]
    inventory = local / "checksums.json"
    write_json(inventory, {"bundle": "Poseidon", "local_audio": audio, "files": files})
    zip_path = output / "poseidon_assets.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for name in files:
            archive.write(local / name, name)
        archive.write(inventory, inventory.name)
    with ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        assert sorted(archive.namelist()) == sorted([*files, inventory.name])
    print(zip_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--art-only", action="store_true")
    parser.add_argument("--package", type=Path)
    args = parser.parse_args()
    art = read(ROOT / "art_manifest.json")
    cues = read(ROOT / "cues.json")
    sound = read(ROOT / "audio/manifest.json")
    verify_sheet(HERO, art["actor"])
    verify_sheet(f"{HERO}_fx", art["fx"])
    verify_stills(art)
    verify_cues(cues, art, sound)
    verify_weapon(art)
    if not args.art_only:
        verify_audio(sound)
    (ROOT / "preview-data.js").write_text(
        "window.poseidonPreview = " + json.dumps({"art": art, "cues": cues, "sound": sound}, ensure_ascii=False) + ";\n",
        encoding="utf-8", newline="\n",
    )
    print(f"{len(art['actor']) * 8} actor frames, {len(art['fx']) * 8} FX frames, 4 icons and a ban/pick card")
    if not args.art_only:
        print(f"{len(sound['voice'])} Japanese clips, {len(sound['sfx'])} Foley clips")
    if args.package:
        pack(args.package, not args.art_only)
