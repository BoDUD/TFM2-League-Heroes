r"""League's particle textures for Ornn, for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_ornn.py [--lol D:\WeGameApps\lol] [--out C:/t/on_work/fxref]

Reads (never writes) Champions/Ornn.wad.client: every base-skin particle texture his bins name (Skins/Base/Particles/
*.tex) is written as <out>/<lowercase name>.png (on black where it has no alpha, so the grey shapes read).
"""
import argparse
import io
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--out", default="C:/t/on_work/fxref")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Ornn.wad.client"))
    skin = w.read_path("data/characters/ornn/skins/skin0.bin")
    bins = sorted(set(m.decode() for m in re.findall(rb"DATA/Characters/Ornn[A-Za-z0-9_]*/[A-Za-z0-9_]*\.bin", skin)))
    names = set()
    for p in bins:
        try:
            d = w.read_path(p.lower())
        except Exception:
            continue
        names |= {m.decode() for m in re.findall(rb"ASSETS/Characters/Ornn/Skins/Base/Particles/[A-Za-z0-9_\.\-]+\.tex", d,
                                                  re.I)}
    n = 0
    for p in sorted(names):
        try:
            im = pose_ref.read_tex(w.read_path(p.lower())).convert("RGBA")
        except Exception as e:
            print("skip", p, e)
            continue
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.out, os.path.basename(p).lower().replace(".tex", ".png")))
        n += 1
    print(n, "textures ->", a.out)


if __name__ == "__main__":
    main()
