#!/usr/bin/env python3
"""Varus's dense (PPU 1.5) design: Codex's step-0 picture read back on its own grid (design_caitlyn_hd.py's way).

    python tools/art/design_varus_hd.py [--gen 1|2] [--review DIR] [--out PNG]

Asked (assets/source/varus/PICTURE_PROMPT_PPU.md) for 60 squares of 11 px from his head's top to his soles in League's
idle (the great bow low at his side), Codex's image_gen drew two 1254-px pictures (assets/source/varus/hd/raw/, its
HANDOFF.md): varus-generated (detailed, ~8.7-px squares, the head about a fifth of his height: read on twice its
square, 65 rows) and varus-generated-coarse (its pick, the chibi head, squares of 17.65 x 17.28: 59 rows). The
semi-transparent rim and specks are dropped at alpha 128; design_fiora_hd.grid() reads one fitted pitch and phase per
axis, the median of each square's middle half, the colours cut to COLOURS by k-means in Lab -> hd/design.png.
With --review: <dir>/varus_ppu_size_gen<n>.png (the design at PPU 1.5 next to Varus now and this pack's PPU heroes as
the game draws them, 3 screen pixels a game pixel) and <dir>/varus_ppu_closeup_gen<n>.png (Codex's picture and the
design at 8x).
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
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "varus", "hd")
GENS = {1: ("varus-generated.png", (16.0, 21.0)),        # twice its own ~8.7-px square
        2: ("varus-generated-coarse.png", (15.0, 21.0))}  # its own 17.65 x 17.28
COLOURS = 40
PEERS = ["varus", "caitlyn", "riven", "darius"]


def lp(path):
    return FD.lp(path)


def read(gen):
    name, pitch = GENS[gen]
    a = np.asarray(Image.open(lp(os.path.join(HD, "raw", name))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    FD.PITCH = pitch
    d, size = FD.grid(a)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out, size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", type=int, default=2)
    ap.add_argument("--review")
    ap.add_argument("--out", help="write the design here instead of hd/design.png")
    a = ap.parse_args()
    d, size = read(a.gen)
    Image.fromarray(d).save(lp(a.out or os.path.join(HD, "design.png")))
    print(f"generation-0{a.gen}: square {size[0]:.2f} x {size[1]:.2f}, design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    im = Image.fromarray(d)
    cells = [(f"new 1.5: {d.shape[0] / 1.5:.1f}px", FD.shown(im, 1.5, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == "varus" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"varus_ppu_size_gen{a.gen}.png"))
    raw = Image.open(lp(os.path.join(HD, "raw", GENS[a.gen][0]))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 8
    cdx = raw.resize((round(raw.width * d.shape[0] * z / raw.height), d.shape[0] * z), Image.LANCZOS)
    FD.strip([(f"Codex's picture (generation-0{a.gen})", cdx),
              (f"design {d.shape[1]}x{d.shape[0]} on its own squares", FD.shown(im, 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, f"varus_ppu_closeup_gen{a.gen}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
