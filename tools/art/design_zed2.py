#!/usr/bin/env python3
"""Zed's design 2 (assets/source/native/zed_native.png): Codex's on-grid redraw C placed on the canvas.

    python tools/art/design_zed2.py [--check]

2026-10-09: the user wanted League's proportions (「头部太大？也不像英雄联盟」) and, of the first redraw,
「你照着原图来啊」; Codex drew him again ON THE GAME GRID after picture A (26-px squares, one pixel per square in
codex_grid/zed-grid-B_1x.png): the hood's point, the dark mask with two red eyes, the back blades, the gold pauldrons
and bracers with their claws. B read as a blur at game size (「现在的劫感觉有点糊吧」: 338 of its 796 squares had no
neighbour of their own colour), so Codex redrew B flat on the same grid with the same silhouette square for square
(zed-grid-C_1x.png: 134 such squares, 9 colours; HANDOFF-C.md, validation-C.json). C is placed as B was: its lowest
row on the soles row 99, the middle of that row's squares on column 64. Two clean-ups, nothing redrawn (the rig's
finish does the same to every posed frame, so the idle would otherwise blink against them):
  - enclosed clear spots of 1-2 squares (eight: in the hood, between the mask and the back blades, in the torso and
    between the claws) take the commonest colour round them, the outline when nothing else touches them;
  - outline squares touching no colour (six: a stub left of the hood, one between the legs, the black tail under the
    tabard's hem) are cleared;
  - the outline closed (strips.complete_outline, as the import does to every frame: the silver blade tips had none)
    and the 1-2 square notches that closing walls in filled like the pinholes - done here once, so the idle's copies
    of the design and the posed frames (rigkit.finish) leave the import the same figure (it had walled in five
    pinholes in the copies only).
design_zed.py (the first design, from the generator draft) is superseded.

2026-10-10, the user: 「另外模型说不出来的糊 相比其他英雄角色 你看一下什么原因吧」. Measured against the 82 other heroes'
idles on the arena colour (the skill's olive-grey ARENA_BG): C's two armour greys sat on the floor's own colour -
#788393 (CIE Lab distance 20 from the floor) and #3A3D4E (23, and 22 from the outline as well) - so 45-47% of his
coloured squares were within 25 of the floor (the other heroes' median: 3%; only Amumu and Malphite more), and a
fifth of his silhouette's edge was those greys and his reds instead of the outline (the median hero: 4%), so his
legs, arms and blades melted into the floor and only scattered gold, white and red stayed. The fix keeps every
square where it is: the two greys become a cool silver and a deep blue steel (PALETTE: 34 and 36 from the floor, the
steel 25 from the outline), and the outline is closed round every edge square from luminance DARK up (complete_outline
counts a square from 70 up as needing one, which skipped his steel, reds and dark red): 0% near the floor, 98% of the
edge black.

2026-10-10, the user on the chest under the mask: 「这是什么 这么奇怪 红色方框？？」. It is the red cowl's front, which in
picture A falls from round the gold visor to a V on the chest between silver plates; C drew it as a red block with two
dark-red squares in its middle (a fold's shadow), and at game size the red ringed them like a square frame. CHEST: those
two squares red, and the row under them narrowed to two red squares between silver (the plates either side), so the
red ends in the V.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "zed", "codex_grid", "zed-grid-C_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "zed_native.png")
SOLE_ROW, MID_COL, Z = 99, 64, 8
# the armour greys off the arena floor's colour (2026-10-10): the light grey -> silver, the dark grey -> deep blue steel
PALETTE = {"#788393": "#9DAAC4", "#3A3D4E": "#2C3458"}
DARK = 30          # the outline closed round every edge square from this luminance up (his dark red is 31)
# the cowl's V on the chest (canvas row, column): colour - after PALETTE
CHEST = {(69, 65): "#AA1027", (69, 66): "#AA1027", (70, 64): "#9DAAC4", (70, 67): "#9DAAC4"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def build():
    a = np.asarray(Image.open(lp(SRC)).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    ys, xs = np.nonzero(a[..., 3] > 0)
    low = ys.max()
    feet = np.nonzero(a[low, :, 3] > 0)[0]
    dy, dx = SOLE_ROW - low, int(round(MID_COL - (feet.min() + feet.max()) / 2))
    can = np.zeros((128, 128, 4), np.uint8)
    can[dy:dy + a.shape[0], dx:dx + a.shape[1]] = a
    can = orphans(pinholes(can))
    for old, new in PALETTE.items():
        m = (can[..., 3] > 0) & (can[..., :3] == rgb(old)).all(-1)
        can[m, :3] = rgb(new)
    for (y, x), col in CHEST.items():
        assert can[y, x, 3], (y, x)
        can[y, x, :3] = rgb(col)
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import strips
    can, _, _ = strips.complete_outline(can, color=outline_of(can), dark=DARK, feet=SOLE_ROW)
    return orphans(pinholes(can))


def rgb(h):
    return np.frombuffer(bytes.fromhex(h.lstrip("#")), np.uint8)


N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)


def outline_of(can):
    from collections import Counter
    cnt = Counter(tuple(int(v) for v in p[:3]) for p in can[can[..., 3] > 0])
    return min(cnt, key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])


def pinholes(can, most=2):
    op = can[..., 3] > 0
    H, W = op.shape
    out = np.zeros((H, W), bool)
    stack = [(0, 0)]
    while stack:
        y, x = stack.pop()
        if not (0 <= y < H and 0 <= x < W) or out[y, x] or op[y, x]:
            continue
        out[y, x] = True
        stack.extend((y + a, x + b) for a, b in N4)
    hole = ~op & ~out
    seen = np.zeros((H, W), bool)
    ink = outline_of(can)
    for y, x in zip(*np.nonzero(hole)):
        if seen[y, x]:
            continue
        comp, stack = [], [(y, x)]
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            comp.append((cy, cx))
            for a, b in N4:
                q = (cy + a, cx + b)
                if hole[q] and not seen[q]:
                    seen[q] = True
                    stack.append(q)
        if len(comp) > most:
            continue
        for cy, cx in comp:
            w = {}
            for a, b in N8:
                q = (cy + a, cx + b)
                if op[q]:
                    c = tuple(int(v) for v in can[q][:3])
                    if c != ink:
                        w[c] = w.get(c, 0) + (2 if (a == 0 or b == 0) else 1)
            can[cy, cx, :3] = max(sorted(w), key=lambda c: w[c]) if w else ink
            can[cy, cx, 3] = 255
    return can


def orphans(can):
    ink = np.array(outline_of(can), np.uint8)
    op = can[..., 3] > 0
    isk = op & (can[..., :3] == ink).all(-1)
    col = np.pad(op & ~isk, 1)
    H, W = op.shape
    near = np.zeros((H, W), bool)
    for a, b in N8:
        near |= col[1 + a:1 + a + H, 1 + b:1 + b + W]
    can[isk & ~near] = 0
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    can = build()
    big = np.repeat(np.repeat(can, Z, 0), Z, 1)
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours")
    if args.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        same = old.shape == big.shape and np.array_equal(old, big)
        print("identical" if same else "DIFFERENT", info)
        sys.exit(0 if same else 1)
    Image.fromarray(big).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()
