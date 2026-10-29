#!/usr/bin/env python3
"""Nomsy's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_nomsy_hd.py   # writes assets/source/nomsy/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/nomsy/codex_picture, 2026-10-29, Codex 2026-10-29/new-chat-6): asked 1536 and 11 px squares,
delivered raw/nomsy-A-generated.png (1535 x 1025, figure 1013 x 715) and raw/nomsy-B-generated.png (1254, figure
1190 x 708), soft alpha; Codex's own cut (nomsy-A/B.png, 62 x 42 / 74 x 44 point-sampled, *-grid.png) is muddy and not
used. Codex corrected the step-0 prompt: the long thin arm with the crescent membrane is her near WING (L_Wing1-3 in the
skeleton), the far wing rises behind her head, and her TAIL is short and thick with four spikes behind the hind legs
(Tail1-4; checked on the model 2026-10-29). The raws' colour edges repeat at ~10 px (regrid.profile, both axes) with
finer ~7.5 px steps on the outlines: A-1 / B-1 = each on ~7.5 / 7.0 px (regrid's own pick, the most detail), A-2 / B-2 =
on 10 px (a smaller figure).
Every picture is read on SIZE px squares, one pixel per drawn square; its colours cut to COLOURS by k-means in Lab
(design_varus.kmeans), alpha 0/255.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "nomsy", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "nomsy", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "raw/nomsy-A-generated.png", "A-2": "raw/nomsy-A-generated.png", "B-1": "raw/nomsy-B-generated.png",
         "B-2": "raw/nomsy-B-generated.png"}
SIZES = {"A-1": 7.5, "A-2": 10.0, "B-1": 7.0, "B-2": 10.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs="*", default=[], metavar="NAME=PX", help="another square for a picture")
    a = ap.parse_args()
    SIZES.update({k: float(v) for k, v in (x.split("=") for x in a.size)})
    os.makedirs(lp(OUT), exist_ok=True)
    for name in FILES:
        d = read(name, SIZES[name])
        op = d[..., 3] > 0
        idx, pal = V.kmeans(d, COLOURS[name])
        out = np.zeros_like(d)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
