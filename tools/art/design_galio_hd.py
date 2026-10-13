#!/usr/bin/env python3
"""league_galio's dense design (PPU 2.0) from Codex's step 1 (assets/source/galio/codex_model).

    python tools/art/design_galio_hd.py [--preview DIR]

The user picked picture A at 2.0 squares a game pixel and clenched fists (2026-10-13). Codex's step-1 front kept every
square of picture A's read-back but the fists - and drew them as black-ringed stone balls (「一圈黑框的椭圆石球」); the
user chose 「我按英雄联盟的拳头逐格手画」. So:
  1. front = Codex's galio-front.png read on its 12-px grid (85 x 128 squares), its fist balls cleared;
  2. one palette: the front's own 40 Lab k-means colours (design_varus.kmeans; the read-back had ~2500 near colours),
     side A snapped to it;
  3. the fists drawn here square for square (NEAR / FAR: as wide as the forearm above, three finger columns with dark
     creases, the knuckles rounded at the bottom, the thumb over the inner side toward the body, lit from the upper
     left), each on a box cleared first (Codex's ball and the spiral's leftovers);
  4. side A (the user's pick) = Codex's galio-side-A.png on the same grid, its ball fist replaced the same way.
  5. the outer outline grown by one square (edge), the one look's ~1 game pixel.
Writes assets/source/galio/hd/front.png and side.png (one square = one dense pixel, 85 x 128, soles row 115, standing
point column 49).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_varus as dv  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "galio")
CODEX = os.path.join(SRC, "codex_model")
OUT = os.path.join(SRC, "hd")
SQ, COLS, ROWS = 12, 85, 128
K = 40

# the fist, lit from the upper left; the inner side (toward the body) on the right, the knuckles at the bottom
SHADES = {"O": (3, 2, 1), "Y": (244, 250, 246), "X": (236, 251, 241), "F": (189, 208, 202), "Z": (149, 169, 168),
          "P": (125, 145, 147), "I": (110, 129, 132), "D": (86, 102, 106), "V": (59, 71, 76), "Q": (46, 56, 61)}
# the near fist (image left): the width of the forearm above it (20 squares), three finger columns with dark creases,
# the knuckles rounded at the bottom, the thumb over the inner side (toward the body, image right)
NEAR = [
    "OOOOOOOOOOOOOOOOOOOO",
    "OXXXXXXXXXFFFFFFFZPO",
    "OXYYYXXXXFFFFFFFZZPO",
    "OXXXXXFFFFFFFFFZZPIO",
    "OXFFFFFFFFFFFZZZPPIO",
    "OFFFFFFFFZZZZPPPOOIO",
    "OFFFZZZZZZPPPPPOXFIO",
    "OZFFFZPFFFZPFFZOXFPO",
    "OZFFFZPFFFZPFFZOFZPO",
    "OZFFFZPFFFZPFFZOZPIO",
    "OPZZZPIZZZPIZZPOPIDO",
    "OPPPPIDPPPIDPPIOOODO",
    ".OPPPOOPPPOOPPIOOOO.",
    "..OOO..OOO..OOO.....",
]
# the far fist (image right, 15 squares like its forearm): the thumb on its inner side (image left), lit the same way
FAR = [
    "OOOOOOOOOOOOOO.",
    "OFXXXXXXXFFFFZO",
    "OXXXXXXFFFFFZPO",
    "OXXFFFFFFFZZPIO",
    "OFFFFFFFZZZPPIO",
    "OIOOFFZZZPPPPIO",
    "OXFOZZFFZPFFZIO",
    "OXFOZPFFZPFFZIO",
    "OFZOZPFFZPFFZIO",
    "OZPOPIZZPIZZPDO",
    "OPIOOIPPIDPPIDO",
    ".OOOPOOPPOOPPO.",
    "....O..OO..OO..",
]
# side A's near fist (17 squares, its forearm 15): the back of the hand to the viewer, the thumb in front (image right)
SIDE = [
    "OOOOOOOOOOOOOOOOO",
    "OXXXXXXXXFFFFFZPO",
    "OXYYYXXXFFFFFZZPO",
    "OXXXXFFFFFFFZZPIO",
    "OXFFFFFFFFFZZPPIO",
    "OFFFFFFZZZZPPOOIO",
    "OFFZZZZZPPPPOXFIO",
    "OZFFZPFFFZPPOXFPO",
    "OZFFZPFFFZPPOFZPO",
    "OZFFZPFFFZPPOZPIO",
    "OPZZPIZZZPIIOPIDO",
    ".OPPOOPPPOOIOOOO.",
    "..OO..OOO..OO....",
]
SIDE_FISTS = [dict(rows=SIDE, at=(89, 32), clear=(89, 101, 31, 50))]
# where each fist goes (top-left square) and the box cleared first (Codex's ball, the old spiral's leftovers)
FRONT_FISTS = [dict(rows=NEAR, at=(91, 14), clear=(91, 104, 14, 37)),
               dict(rows=FAR, at=(92, 69), clear=(92, 107, 66, 85))]


def grid(path):
    a = np.array(Image.open(path).convert("RGBA"))
    g = a[SQ // 2::SQ, SQ // 2::SQ][:ROWS, :COLS].copy()
    g[..., 3] = np.where(g[..., 3] > 0, 255, 0)
    g[g[..., 3] == 0] = 0
    return g


def snap(g, pal):
    op = g[..., 3] > 0
    lab = dv.srgb2lab(g[op][:, :3].astype(float))
    pl = dv.srgb2lab(pal.astype(float))
    out = g.copy()
    out[op, :3] = pal[((lab[:, None] - pl[None]) ** 2).sum(-1).argmin(1)]
    return out


def readback():
    """Picture A read back on its own grid and laid on the step-1 grid (pack_galio_model.py's layout)."""
    import subprocess
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_rg_A.png")
    subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts", "regrid.py"),
                    os.path.join(SRC, "codex_picture", "galio-model-A.png"), tmp], check=True, capture_output=True)
    r = np.array(Image.open(tmp).convert("RGBA"))
    os.remove(tmp)
    r[..., 3] = np.where(r[..., 3] > 0, 255, 0)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[14:14 + r.shape[0], 1:1 + r.shape[1]] = r
    return can


def paint(g, spec):
    r0, r1, c0, c1 = spec["clear"]
    rows = spec["rows"]
    ar, ac = spec["at"]
    before = g.copy()
    g[r0:r1, c0:c1] = 0
    for i, line in enumerate(rows):
        for j, ch in enumerate(line):
            if ch != ".":
                g[ar + i, ac + j, :3] = SHADES[ch]
                g[ar + i, ac + j, 3] = 255
    # what the box cut off a neighbour (the leg beside the near fist) gets its outline back on that side
    near = np.zeros(g.shape[:2], bool)
    near[ar:ar + len(rows), ac:ac + len(rows[0])] = True
    for r in range(r0, r1):
        for c in range(c0, c1):
            if g[r, c, 3]:
                continue
            for dc in (-1, 1):
                cc = c + dc
                if 0 <= cc < g.shape[1] and g[r, cc, 3] and not near[r, cc] and not (c0 <= cc < c1)                         and g[r, cc, :3].sum() > 60:
                    g[r, c] = (*SHADES["O"], 255)
    # a cleared square left as a one-square crack between the fist and the body takes the outline (gap-check)
    for r in range(r0, r1):
        for c in range(c0, c1):
            if g[r, c, 3] or not before[r, c, 3]:
                continue
            if (g[r, c - 1, 3] and g[r, c + 1, 3]) or (g[r - 1, c, 3] and g[r + 1, c, 3]):
                g[r, c] = (*SHADES["O"], 255)
    return g


def pinholes(g, most=2):
    """Enclosed clear spots of at most `most` squares take the outline (gap-check: no ground through a pinhole)."""
    from scipy import ndimage
    lab, k = ndimage.label(g[..., 3] == 0)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    for i in range(1, k + 1):
        if i not in border and (lab == i).sum() <= most:
            g[lab == i] = (*SHADES["O"], 255)
    return g


def edge(g, n=1):
    """The outer outline grown by n squares (ppu_restyle.py's `edge`): the one look's outline is about 1 game pixel =
    2 squares at PPU 2, picture A's mostly 1."""
    for _ in range(n):
        op = g[..., 3] > 0
        grow = np.zeros_like(op)
        grow[1:] |= op[:-1]
        grow[:-1] |= op[1:]
        grow[:, 1:] |= op[:, :-1]
        grow[:, :-1] |= op[:, 1:]
        g[grow & ~op] = (*SHADES["O"], 255)
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    front = grid(os.path.join(CODEX, "galio-front.png"))
    changed = np.abs(front.astype(int) - readback().astype(int)).max(2) > 0
    assert not changed[:88].any() and not changed[108:].any(), "Codex changed squares away from the fists"
    idx, pal = dv.kmeans(front, K)
    front = snap(front, pal)
    for spec in FRONT_FISTS:
        paint(front, spec)
    pinholes(front)
    edge(front)
    side = snap(grid(os.path.join(CODEX, "galio-side-A.png")), pal)
    for spec in SIDE_FISTS:
        paint(side, spec)
    pinholes(side)
    edge(side)
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(front).save(os.path.join(OUT, "front.png"))
    Image.fromarray(side).save(os.path.join(OUT, "side.png"))
    if a.preview:
        Image.fromarray(front).resize((COLS * 8, ROWS * 8), Image.NEAREST).save(os.path.join(a.preview, "front_8x.png"))
    print("front", len({tuple(c) for c in front[front[..., 3] > 0][:, :3]}), "colours")


if __name__ == "__main__":
    main()
