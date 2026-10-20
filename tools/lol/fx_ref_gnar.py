r"""League's particle textures for Gnar (both forms), for the effects pack's reference sheet (Riot's art: kept local, never
committed).

    python tools/lol/fx_ref_gnar.py [--lol D:\WeGameApps\lol] [--out C:/t/gn_work/fxref]

Reads (never writes) Champions/Gnar.wad.client: every base-skin particle texture the bins of Gnar and GnarBig name
(Skins/Base/Particles/*.tex) is written as <out>/<lowercase name>.png (on black where it has no alpha, so the grey
shapes read), and Mini's boomerang and Mega's boulder props are rendered by pose_ref.py when the skin has them.
"""
import argparse
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pose_ref  # noqa: E402
from riot import Wad  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--out", default="C:/t/gn_work/fxref")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Gnar.wad.client"))
    bins = set()
    for char in ("gnar", "gnarbig"):
        try:
            skin = w.read_path(f"data/characters/{char}/skins/skin0.bin")
        except Exception:
            continue
        bins |= {m.decode() for m in re.findall(rb"DATA/Characters/Gnar[A-Za-z0-9_]*/[A-Za-z0-9_]*\.bin", skin)}
        bins.add(f"data/characters/{char}/skins/skin0.bin")
        bins.add(f"data/characters/{char}/{char}.bin")
    names = set()
    for p in sorted(bins):
        try:
            d = w.read_path(p.lower())
        except Exception:
            continue
        names |= {m.decode() for m in re.findall(rb"ASSETS/Characters/Gnar[A-Za-z]*/Skins/Base/Particles/[A-Za-z0-9_\.\-]+\.tex",
                                                  d, re.I)}
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
