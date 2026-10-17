#!/usr/bin/env python3
"""Vi's design (2026-10-03): the user's approved master after oppi's Vi's structure, read onto the game grid at 40 rows,
her eyes and far cheek redrawn.

    python tools/art/design_vi.py [--out assets/source/native/vi_native.png] [--check]

The first design (A40: frontal, the gauntlets hanging) was rejected with its strips: 「头不连接身体」
「身体看起来很奇怪」, 「你可以参考隔壁oppi的蔚怎么做的」 - our own drawing after oppi's structure
(assets/source/vi/MODEL_V2.md): a 3/4 view facing right in a boxer's guard, the hair over the neck into the shoulders,
a clean body. Codex's image generation gave the master the user approved (codex_model_v2/vi_approved_master.png,
1254 px; read back on its own ~12.5 px grid it is 43 x 59 squares, codex_model_v2/vi_master_readback_1x.png - its
palette, 27 colours). Then:
1. read onto 40 rows by tools/art/shrink_vi.py (the user: 「codex做了一版挺大的 需要你慢慢调到合适的尺寸」,
   picked 40 of 42 / 40 / 38): the figure's 719 source rows over 40, the read-back's square aspect (548/43 by 719/59)
   kept, 30 columns centred on the figure; specks merged, the outline closed (strips.complete_outline);
2. the eyes (「40 但是眼睛要修一下」, option 1 of three; the first try put the far iris on the jaw's outline and it
   stuck out of the face): two rows under a dark lash row - the near eye a white beside the iris, the far eye an iris
   one column inside the outline, one skin column between; the near iris's top square #006CFB, a shade only it has
   (import_native EYES finds her face by it; the crystals use the other blues);
3. the far cheek (「方案1吧 但是这里有点奇怪」, fix A of two): the skin that rose into the fringe takes the fringe's
   pink, the cheek's light-brown outline the jaw's near-black;
4. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
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
import shrink_vi as S  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vi", "codex_model_v2")
MASTER = os.path.join(SRC, "vi_approved_master.png")
READBACK = os.path.join(SRC, "vi_master_readback_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "vi_native.png")
ROWS = 40
SQ_W, SQ_H = 548 / 43, 719 / 59               # the master's drawn square, source px
LASH, WHITE, SKIN = (0x1F, 0x1E, 0x2F), (0xFB, 0xF2, 0xE6), (0xFC, 0xC9, 0xA2)
NEAR_TOP, TOP, LOW = (0x00, 0x6C, 0xFB), (0x00, 0x5D, 0xE7), (0x00, 0x7C, 0xFC)
FRINGE, OUTLINE = (0xE2, 0x24, 0x67), (0x20, 0x0C, 0x05)
# (x, y) on the 30 x 40 figure: step 2's eyes (the face is columns 14-18 on row 8, 14-17 below), step 3's cheek
PATCH = {
    (14, 7): LASH, (15, 7): LASH, (16, 7): SKIN, (17, 7): LASH, (18, 7): SKIN,
    (14, 8): WHITE, (15, 8): NEAR_TOP, (16, 8): SKIN, (17, 8): TOP, (18, 8): SKIN,
    (14, 9): WHITE, (15, 9): LOW, (16, 9): SKIN, (17, 9): LOW,
    (18, 6): FRINGE, (19, 7): OUTLINE, (19, 8): OUTLINE, (18, 9): OUTLINE,
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def figure():
    """Steps 1-3: the 40-row figure, and the master's grid: (figure, (left, bottom, px_col, px_row), (cols, pal))."""
    src = np.asarray(Image.open(lp(MASTER)).convert("RGBA"))
    cols, pal = S.palette(lp(READBACK))
    ys, xs = np.nonzero(src[..., 3] > 128)
    bottom, x0, x1 = ys.max() + 1, xs.min(), xs.max() + 1
    px_row = (bottom - ys.min()) / ROWS
    px_col = px_row * SQ_W / SQ_H
    W = int(np.ceil((x1 - x0) / px_col))
    left = (x0 + x1) / 2 - W * px_col / 2
    fig, feat = S.read_blocks(src, left, bottom, px_col, px_row, W, ROWS, cols, pal)
    fig = S.despeckle(fig, feat)
    fig, _, _ = G.complete_outline(fig, feet=ROWS - 1)
    for (x, y), c in PATCH.items():
        fig[y, x] = (*c, 255)
    return fig, (left, bottom, px_col, px_row), (cols, pal)


def build():
    fig, _, _ = figure()
    canvas = np.zeros((128, 128, 4), np.uint8)
    cx = feet_left(fig)
    canvas[100 - ROWS:100, cx:cx + fig.shape[1]] = fig
    return canvas, fig


def feet_left(fig):
    """The canvas column of the figure's first column: the middle of the feet (its lowest row) on column 64."""
    feet = np.nonzero(fig[-1, :, 3] > 0)[0]
    return int(round(64 - (feet.min() + feet.max() + 1) / 2))


def grid():
    """The design's grid over a whole 1254 px picture drawn like the master: (left of canvas column 0, the source
    row under canvas row 99, px per column, px per row, palette names, palette rgb). Canvas column c reads source x
    from left + c * px_col; canvas row r reads source y from bottom - (100 - r) * px_row."""
    fig, (left, bottom, px_col, px_row), (cols, pal) = figure()
    return left - feet_left(fig) * px_col, bottom, px_col, px_row, cols, pal


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing it")
    a = ap.parse_args()
    canvas, fig = build()
    big = Image.fromarray(np.repeat(np.repeat(canvas, 8, 0), 8, 1))
    if a.check:
        old = np.asarray(Image.open(lp(a.out)).convert("RGBA"))
        same = old.shape == np.asarray(big).shape and (old == np.asarray(big)).all()
        print("identical" if same else "DIFFERENT", a.out)
        sys.exit(0 if same else 1)
    big.save(lp(a.out))
    op = fig[..., 3] > 0
    n = len(np.unique(fig[op][:, :3], axis=0))
    print(f"{a.out}: {fig.shape[1]}x{fig.shape[0]}, {n} colours, {int(op.sum())} px")


if __name__ == "__main__":
    main()
