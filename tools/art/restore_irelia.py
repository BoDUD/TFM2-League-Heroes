#!/usr/bin/env python3
"""Irelia's design restored from the picture the user picked (assets/source/irelia/codex_model/raw/irelia-front-B.png,
2026-10-11: 「这个就做的挺好的 为什么不能慢慢的按照这个来完美还原呢」「按照这版来还原」), the first pass of the 42-row design.

    python tools/art/restore_irelia.py OUT.txt [--head 1.3] [--height 42] [--ink 0.55] [--shade mode|mean]

Codex drew the picture at ~14 px a square, 89 rows crest to soles - twice the game size; its own nearest-neighbour
copies at 37 rows were specks (codex_model/irelia-*_1x.png, rejected 「全都不及格」). This pass:
  * two scales anchored on the chin's middle: the head (crest, hair dome, face) on S_BODY / HEAD_X picture pixels a
    square, the body and the blades behind the head on S_BODY - the face gets the pixels (the user, on Zeri: 「牺牲一点
    像素 重点做哪里的像素」), the crest tip to the soles HEIGHT rows;
  * every square: the MATERIAL most of its picture pixels belong to (hair, crimson, silver, skin, cyan; outline only when
    near-black is `ink` of the opaque part), then that material's commonest shade among exactly those pixels ("mode";
    "mean" = the shade nearest their mean lightness, which darkened the royal-blue hair);
  * tidy: lone squares of a foreign material take their neighbours', inner outline specks between one material go, the
    silhouette's outline closed (strips.complete_outline).
Writes a letter table (assets/source/irelia/design42/palette.json). The finished design (design42/irelia42.txt) was
then hand-finished square by square over this table and the picture (the face 7 squares wide with Irelia's sharp cyan
eyes under heavy brows, the torso's breastplate / heart / gem / tabard, the hair's sheen, the boots), and
tools/art/design_irelia.py --table writes assets/source/native/irelia_native.png from it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PIC = os.path.join(ROOT, "assets", "source", "irelia", "codex_model", "raw", "irelia-front-B.png")
PAL = json.load(open(os.path.join(ROOT, "assets", "source", "irelia", "design42", "palette.json")))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402


def rgb(letter):
    h = PAL[letter]
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
CREST, CHIN, SOLES = 219, 585, 1460       # picture rows: the crest's tip, the chin's bottom, the soles' bottom
FACE_X, FEET_X = 615, 617                  # the face's middle, the middle between the feet
CHIN_ROW = 17                              # the first body row (the chin's bottom on its top edge)
COLS, MID = 28, 14.5                       # table width, the column middle the anchors sit on
SHADE = "mean"                             # "mean": nearest the pixels' mean lightness; "mode": their commonest shade
TRIM = 0                                   # columns trimmed off the left by build() (view2 adds them back)
MATERIALS = {"hair": "HhmnN", "crimson": "RrqQ", "silver": "Wwvut", "skin": "SsoO", "cyan": "KCck"}
LUM = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def head_region(x, y):
    """The head in the picture: the hair dome and face, the crest; not the blades behind it nor the long hair below."""
    return (470 <= x <= 772 and 262 <= y < CHIN) or (436 <= x <= 578 and 210 <= y <= 330)


class Picture:
    def __init__(self):
        pic = np.asarray(Image.open(PIC).convert("RGBA")).astype(int)
        self.pic = pic
        letters = list(PAL)
        self.letters = letters
        cols = np.array([rgb(l) for l in letters])
        op = pic[..., 3] >= 128
        near = np.full(op.shape, -1, int)
        ys, xs = np.nonzero(op)
        near[ys, xs] = ((pic[ys, xs, None, :3] - cols[None]) ** 2).sum(-1).argmin(-1)
        self.near = near
        self.ink = letters.index("!")
        self.mat_of = {letters.index(l): m for m, ls in MATERIALS.items() for l in ls}

    def cell(self, x0, y0, x1, y1, ink_share, cover):
        H, W = self.near.shape
        xa, xb, ya, yb = max(0, int(round(x0))), min(W, int(round(x1))), max(0, int(round(y0))), min(H, int(round(y1)))
        if xb <= xa or yb <= ya:
            return "."
        cell = self.near[ya:yb, xa:xb]
        rgbc = self.pic[ya:yb, xa:xb, :3]
        opaque = cell >= 0
        if opaque.sum() < cover * cell.size:
            return "."
        if (cell == self.ink).sum() >= ink_share * opaque.sum():
            return "!"
        counts = {}
        for v, n in zip(*np.unique(cell[opaque & (cell != self.ink)], return_counts=True)):
            m = self.mat_of[int(v)]
            counts[m] = counts.get(m, 0) + n
        m = max(counts, key=counts.get)
        sel = np.zeros(cell.shape, bool)
        for v in np.unique(cell[opaque]):
            if v != self.ink and self.mat_of[int(v)] == m:
                sel |= cell == v
        if SHADE == "mode":      # the commonest shade of the material in the square
            vals, cnt = np.unique(cell[sel], return_counts=True)
            return self.letters[int(vals[cnt.argmax()])]
        lum = LUM(rgbc[sel].mean(0))
        return min(MATERIALS[m], key=lambda l: abs(LUM(rgb(l)) - lum))


def build(head_x=1.25, height=42, ink_share=0.55, cover=0.45):
    s_b = ((SOLES + 1 - CHIN) + (CHIN - CREST) * head_x) / height
    s_h = s_b / head_x
    p = Picture()
    rows_body = int(round((SOLES + 1 - CHIN) / s_b))
    top_head = CHIN_ROW - int(np.ceil((CHIN - 110) / s_h))      # room for the blade tips above
    grid = {}
    for r in range(top_head, CHIN_ROW + rows_body):
        for c in range(COLS):
            if r >= CHIN_ROW:
                y0 = CHIN + (r - CHIN_ROW) * s_b
                x0 = FEET_X + (c - MID - 0.5) * s_b
                grid[r, c] = p.cell(x0, y0, x0 + s_b, y0 + s_b, ink_share, cover)
                continue
            # the head band: the enlarged head where its source is the head, else the body scale (blades behind)
            hy0 = CHIN - (CHIN_ROW - r) * s_h
            hx0 = FACE_X + (c - MID - 0.5) * s_h
            if head_region(hx0 + s_h / 2, hy0 + s_h / 2):
                grid[r, c] = p.cell(hx0, hy0, hx0 + s_h, hy0 + s_h, ink_share, cover)
                continue
            by0 = CHIN - (CHIN_ROW - r) * s_b
            bx0 = FEET_X + (c - MID - 0.5) * s_b
            if head_region(bx0 + s_b / 2, by0 + s_b / 2):
                grid[r, c] = "."
                continue
            grid[r, c] = p.cell(bx0, by0, bx0 + s_b, by0 + s_b, ink_share, cover)
    rows = []
    for r in range(top_head, CHIN_ROW + rows_body):
        rows.append("".join(grid[r, c] for c in range(COLS)))
    while rows and set(rows[0]) == {"."}:
        rows.pop(0)
    used = [x for x in range(COLS) if any(r[x] != "." for r in rows)]
    c0, c1 = max(0, used[0] - 1), min(COLS, used[-1] + 2)
    global TRIM
    TRIM = c0
    return [r[c0:c1] for r in rows], s_b, s_h


MAT = {}
for m, ls in {"hair": "HhmnN", "crimson": "RrqQ", "silver": "Wwvut", "skin": "SsoO", "cyan": "KCck", "ink": "!"}.items():
    for l in ls:
        MAT[l] = m


def read(path):
    return [list(r.rstrip("\n")) for r in open(path) if r.strip("\n")]


def write(rows, path):
    open(path, "w").write("\n".join("".join(r) for r in rows) + "\n")


def mat(ch):
    return MAT.get(ch)


def despeckle(g):
    H, W = len(g), len(g[0])
    out = [r[:] for r in g]
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            m = mat(g[y][x])
            if m is None or m == "ink":
                continue
            ring = [g[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if any(mat(c) == m for c in ring):
                continue
            four = [g[y - 1][x], g[y + 1][x], g[y][x - 1], g[y][x + 1]]
            ms = [mat(c) for c in four if mat(c) not in (None, "ink")]
            for cand in set(ms):
                if ms.count(cand) >= 3:
                    shades = [c for c in four if mat(c) == cand]
                    out[y][x] = max(set(shades), key=shades.count)
                    n += 1
                    break
    return out, n


def thin_ink(g):
    H, W = len(g), len(g[0])
    out = [r[:] for r in g]
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if g[y][x] != "!":
                continue
            ring = [g[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if any(c == "." for c in ring):
                continue
            for a, b in ((g[y][x - 1], g[y][x + 1]), (g[y - 1][x], g[y + 1][x])):
                if mat(a) and mat(a) == mat(b) and mat(a) != "ink":
                    out[y][x] = a
                    n += 1
                    break
    return out, n


def outline(g):
    H, W = len(g), len(g[0])
    a = np.zeros((H + 2, W + 2, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            if g[y][x] in PAL:
                a[y + 1, x + 1, :3] = rgb(g[y][x])
                a[y + 1, x + 1, 3] = 255
    ink = rgb("!")
    can, added, _ = strips.complete_outline(a, color=ink, feet=H + 1)
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(W):
            if can[y + 1, x + 1, 3] and g[y][x] == ".":
                out[y][x] = "!"
            elif can[y + 1, x + 1, 3] and tuple(can[y + 1, x + 1, :3]) == ink and g[y][x] != "!":
                out[y][x] = "!"
    return out, added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--head", type=float, default=1.3)
    ap.add_argument("--height", type=int, default=42)
    ap.add_argument("--ink", type=float, default=0.55)
    ap.add_argument("--shade", default="mode")
    a = ap.parse_args()
    global SHADE
    SHADE = a.shade
    rows, s_b, s_h = build(a.head, a.height, a.ink)
    g = [list(r) for r in rows]
    g, n1 = despeckle(g)
    g, n2 = thin_ink(g)
    g, n3 = outline(g)
    open(a.out, "w").write("\n".join("".join(r) for r in g) + "\n")
    print(a.out, len(rows), "x", len(rows[0]), f"s_body {s_b:.2f} s_head {s_h:.2f}; tidy: despeckle {n1}, "
          f"inner ink {n2}, outline added {n3}")


if __name__ == "__main__":
    main()
