#!/usr/bin/env python3
"""Bel'Veth's step-1 candidates for the user's pick: each read-back (design_belveth_model.py --options) shown at game
size - 40 game px from the head's outline row to the lowest claw, so a take cut to 82 rows is PPU 1.75 and a take as drawn
a higher PPU - next to the pack's junglers, claws on one line; above them the takes at 12x round the face.

    python tools/art/review_belveth_model.py --opts C:/t/bv_work/model_opts --out dist/belveth_packs [--scale 4]

Writes <out>/belveth_model_pick.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from review_belveth_size import BG, NEIGHBOURS, frame0, lp, shown  # noqa: E402

GAME = 40
# take -> (options file, head outline row, eyes' centre (x, y) on it)
TAKES = {"A-1 (82)": ("opt_A-1.png", 11, (55, 20)), "A-1 as drawn": ("opt_A-1_as_drawn.png", 16, (78, 27)),
         "A-2 (82)": ("opt_A-2.png", 11, (49, 19)), "A-2 as drawn": ("opt_A-2_as_drawn.png", 14, (63, 23))}


def face(a, ex, ey, h):
    hh = int(h * 0.11)
    y0, y1, x0, x1 = int(ey - hh), int(ey + hh * 0.8), int(ex - hh * 1.1), int(ex + hh * 1.1)
    im = Image.fromarray(a[y0:y1, x0:x1])
    k = max(1, round(160 / im.height))
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    cells, faces = [], []
    for name, (f, top, (ex, ey)) in TAKES.items():
        d = np.asarray(Image.open(lp(os.path.join(a.opts, f))).convert("RGBA"))
        ppu = (d.shape[0] - top) / GAME
        cells.append((f"{name} PPU {ppu:.2f}", f"{d.shape[1] / ppu:.0f}x{d.shape[0] / ppu:.0f}",
                      shown(Image.fromarray(d), ppu, a.scale)))
        faces.append((name, face(d, ex, ey, d.shape[0])))
    for hero in NEIGHBOURS:
        im, p = frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", shown(im, p, a.scale)))
    gap, top = 16, 34
    W = max(sum(c[2].width for c in cells), sum(f[1].width for f in faces)) + gap * (len(cells) + 1)
    fh = max(f[1].height for f in faces) + top + gap
    H = max(c[2].height for c in cells) + top + gap
    can = Image.new("RGBA", (W, fh + H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for label, im in faces:
        bg = Image.new("RGBA", im.size, BG)
        bg.alpha_composite(im.convert("RGBA"))
        can.alpha_composite(bg, (x, top))
        dr.text((x, 4), label + " face", fill=(30, 30, 30, 255))
        x += im.width + gap
    x = gap
    for label, size, im in cells:
        can.alpha_composite(im, (x, fh + H - gap - im.height))
        dr.text((x, fh + 4), label, fill=(30, 30, 30, 255))
        dr.text((x, fh + 18), size, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, fh + H - gap), (W, fh + H - gap)], fill=(120, 120, 120, 255))
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "belveth_model_pick.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()
