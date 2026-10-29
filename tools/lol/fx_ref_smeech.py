r"""Smeech's own particle textures (TFT set 13) for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_smeech.py [--out C:/t/sm_work/fxref] [--lol "D:/Riot Games/League of Legends"]

Read from the Riot client's TFTSet13.wad.client: every .tex path his skin bin (data/characters/tft13_gremlin/skins/
skin0.bin, which also holds his particle systems: the claw slashes, the glow, the leap) names; the set's
shared particle textures it borrows (ASSETS/Maps/Particles/TFT/Set13/...) come from TFTCommon.wad.client when the
set's own WAD lacks them. Each is written as <out>/<file stem>.png on black where it has alpha, so the grey shapes read.
"""
import argparse
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402

BINS = ("data/characters/tft13_gremlin/skins/skin0.bin",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/sm_work/fxref")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "TFTSet13.wad.client"))
    common = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "TFTCommon.wad.client"))
    paths = set()
    for b in BINS:
        try:
            blob = w.read_path(b)
        except KeyError:
            print("no", b)
            continue
        paths |= {m.decode("latin1") for m in re.findall(rb"[A-Za-z0-9_/\.\-]+\.tex", blob)}
    n = 0
    for p in sorted(paths):
        try:
            src = w if w.has(p.lower()) else common
            im = pose_ref.read_tex(src.read_path(p.lower())).convert("RGBA")
        except Exception as e:   # textures neither WAD holds
            print("skip", p, type(e).__name__)
            continue
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.out, os.path.splitext(os.path.basename(p))[0].lower() + ".png"))
        n += 1
    print(n, "textures ->", a.out)


if __name__ == "__main__":
    main()
