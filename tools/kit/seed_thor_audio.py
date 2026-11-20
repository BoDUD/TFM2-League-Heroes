"""Copy Thor's clips from Codex's delivery into ragnarok/sound/sfx/ (git-ignored, like the league and tft packs' audio).

    python tools/kit/seed_thor_audio.py [--from <folder with ragnarok_thor_sfx_*.mp3 / ragnarok_thor_vo_*.mp3>]

The delivery (2026-11-20, Codex's branch codex/ragnarok-thor-assets-v01 in the local TeamFightMange2-mod-ragnarok-thor
checkout, commit 6f4833f): 16 original sound effects and ten Japanese voice lines cut from the official Record of
Ragnarok promotional recordings (Hikaru Midorikawa as Thor). Only the clips setup_thor.SOUNDS plays are copied; each is
checked to be an MP3 and not empty.
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from setup_thor import SOUNDS, MOD, lp  # noqa: E402

DEFAULT = r"D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-thor\mods\ragnarok_thor\sound\sfx"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default=DEFAULT)
    a = ap.parse_args()
    clips = sorted({c for plays in SOUNDS.values() for c, _, _ in plays})
    out = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out), exist_ok=True)
    missing = []
    for c in clips:
        src = os.path.join(a.src, c + ".mp3")
        if not os.path.isfile(src):
            missing.append(c)
            continue
        data = open(src, "rb").read()
        if len(data) < 1000 or not (data[:3] == b"ID3" or data[0] == 0xFF):
            sys.exit(f"{src}: not an MP3")
        shutil.copyfile(src, lp(os.path.join(out, c + ".mp3")))
    if missing:
        sys.exit(f"missing in {a.src}: {missing}")
    print(f"{len(clips)} clips -> {out}")


if __name__ == "__main__":
    main()
