"""Kai'Sa's walk legs from Codex's redraw (assets/source/kaisa/codex_walk/kaisa_walk.png, asked by
assets/source/kaisa/WALK_PROMPT_PPU.md: only the legs of tools/art/pack_kaisa_walk.py's 8-frame template redrawn, the
user: 「有点变形啊 让codex帮忙把」) read back square by square on the template's 6-px grid -> assets/source/kaisa/hd/
walk_legs.png (8 frames side by side, each design-sized with LEFT spare columns either side, only the legs: from the
hip line down). tools/art/rig_kaisa_hd.py's run puts the design's own upper body and arms over them.

    python tools/art/import_kaisa_walk.py

Codex kept the template's frames, ground lines and 6-px grid (a phase of a pixel or two per cell, found here by the
most uniform blocks over the legs) but redrew the upper body too (a third of its squares differ) and its edges are
soft, so: each square = the median of its block's middle 4 x 4, green keyed, snapped to the design's own leg colours
(the design from the hip plates' lowest rows down); the upper body is not taken.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_kaisa_walk as PW  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kaisa")
LEFT = 12                       # spare design columns on each side of a frame in walk_legs.png
# design square (c, r) of frame i sits in the template at pixel (cell x + X0 + 6c, cell y + Y0 + 6r)
X0, Y0 = 60, 104
HIP = 46                        # design row: the legs' top
RISE = [1, 2, 0, 0, 1, 2, 0, 0]  # rows the template's figure was up in each frame (its legs then start higher)
LEG_FROM = 44                   # design row: the leg colours from here down


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def green(col):
    return (col[1] > 150 and col[0] < 120 and col[2] < 120) or (col[1] > 90 and col[0] < 50 and col[2] < 50)


def main():
    design = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    H, W = design.shape[:2]
    leg = design[LEG_FROM:]
    pal = np.unique(leg[leg[..., 3] > 0][:, :3], axis=0).astype(int)
    sheet = np.asarray(Image.open(lp(os.path.join(SRC, "codex_walk", "kaisa_walk.png"))).convert("RGB")).astype(int)
    z = PW.CELL_PX
    FW = W + 2 * LEFT
    out = np.zeros((H, FW * 8, 4), np.uint8)
    for i in range(8):
        cx, cy = (i % PW.GRID[0]) * PW.CELL[0], (i // PW.GRID[0]) * PW.CELL[1]
        top_row = HIP - RISE[i]
        best = None
        for py in range(-2, 4):
            for px in range(-2, 4):
                x = cx + X0 + px                        # the design's own columns (inside every cell)
                ys = [cy + Y0 + py + r * z for r in range(top_row, H)]
                var = sum(float(sheet[y:y + z, x:x + W * z].reshape(z, W, z, 3).var(axis=(0, 2)).sum()) for y in ys)
                if best is None or var < best[0]:
                    best = (var, px, py)
        _, px, py = best
        for r in range(top_row, H):
            y = cy + Y0 + py + r * z
            if y + z > cy + PW.SOLE_Y + 3:
                continue
            for c in range(-LEFT, W + LEFT):
                x = cx + X0 + px + c * z
                if x < cx or x + z > cx + PW.CELL[0]:
                    continue
                col = np.median(sheet[y + 1:y + z - 1, x + 1:x + z - 1].reshape(-1, 3), axis=0)
                if green(col):
                    continue
                out[r, i * FW + c + LEFT, :3] = pal[int(np.argmin(((pal - col) ** 2).sum(1)))]
                out[r, i * FW + c + LEFT, 3] = 255
        print(f"frame {i}: phase ({px}, {py}), {int((out[:, i * FW:(i + 1) * FW, 3] > 0).sum())} leg squares")
    Image.fromarray(out).save(lp(os.path.join(SRC, "hd", "walk_legs.png")))
    print("written hd/walk_legs.png", out.shape)


if __name__ == "__main__":
    main()
