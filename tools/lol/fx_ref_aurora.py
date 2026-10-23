r"""League's particle textures for Aurora, for the effects pack's reference sheet (Riot's art: kept local,
never committed).

    python tools/lol/fx_ref_aurora.py [--lol D:\WeGameApps\lol] [--out C:/t/au_work/fxref]

Reads (never writes) Champions/Aurora.wad.client: every base-skin particle texture the bins of Aurora
name (ASSETS/Characters/Aurora*/Skins/Base/Particles/*.tex) is written as <out>/<lowercase name>.png (on black where it
has no alpha, so the grey shapes read).
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
    ap.add_argument("--out", default="C:/t/au_work/fxref")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    w = Wad(os.path.join(a.lol, "Game", "DATA", "FINAL", "Champions", "Aurora.wad.client"))
    bins = set()
    for champ in ("aurora",):
        skin = w.read_path(f"data/characters/{champ}/skins/skin0.bin")
        bins |= set(m.decode() for m in re.findall(rb"DATA/Characters/Aurora[A-Za-z0-9_]*/[A-Za-z0-9_/]*\.bin", skin, re.I))
        bins.add(f"data/characters/{champ}/skins/skin0.bin")
        bins.add(f"data/characters/{champ}/{champ}.bin")
    names = set()
    for p in sorted(bins):
        try:
            d = w.read_path(p.lower())
        except Exception:
            continue
        names |= {m.decode() for m in re.findall(
            rb"ASSETS/Characters/Aurora[A-Za-z0-9_]*/Skins/Base/Particles/[A-Za-z0-9_\.\-]+\.(?:tex|dds)", d, re.I)}
    n = 0
    for p in sorted(names):
        try:
            im = pose_ref.read_tex(w.read_path(p.lower())).convert("RGBA")
        except Exception as e:
            print("skip", p, e)
            continue
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        stem = os.path.splitext(os.path.basename(p).lower())[0]
        bg.convert("RGB").save(os.path.join(a.out, stem + ".png"))
        n += 1
    print(n, "textures ->", a.out)


if __name__ == "__main__":
    main()
