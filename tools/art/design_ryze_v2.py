#!/usr/bin/env python3
"""Ryze's second design: Codex's leaner body (v2 option B) under the first design's head (2026-10-03).

    python tools/art/design_ryze_v2.py [--check]

The user: 「瑞兹看起来也做的有点胖了 顺带也修复一下吧」 (the first design: 828 squares at 40 rows, arms 6 squares thick
hanging outside the body, the trousers one 18-square block, boots 5 rows; oppi's Brand / Ezreal 544-592). Codex redrew
the body after assets/source/ryze/MODEL_V2.md (codex_model_v2/: options A / B / C on about 19 px squares, ~52 rows; its
own readback.py and the B / C read-backs beside them) and the user left the pick to me (「你挑一版吧」): B, the lean
body that keeps Ryze's shoulders. Steps, all from the repo:
  1. Codex's master B read at 41 rows the way its own readback.py reads (one game pixel = the middle sample of a
     block), the block size and phase searched so the figure is 41 rows and the fewest samples land on a drawn
     square's border (a mixed colour); each sample snapped to the first design's 30 colours, the eyes' white kept out
     (the scroll's paper snapped to it).
  2. The first design's head (assets/source/native/ryze_native.png: rows 1-10 of its figure from column 7 - the
     crown, the runes, the eyes, the brows and the beard's top - the scroll left of it stays B's) over B's, placed by
     the near eye's white.
  3. The hands redrawn square by square (HANDS: the read left six loose squares each, 「这里还变形」).
  4. The slit of ground the far hand closed between its arm and the coat (Codex's master leaves it open below the
     hand; the wider redrawn hand walls it into a window, a hole at game size) and the near arm's two-square one
     filled with the outline (WINDOW): the arms lie against the coat, one dark seam between.
  5. The hips (HIPS): under the belt the read left the hips black - a bar from the far hand to the teal flap and two
     columns each side between the hands and the trousers, the trousers two or three squares wide - so the legs read
     as cut off the body (the user: 「瑞兹这腿和身体感觉是分割的」). The trousers drawn up to the belt instead, as wide
     as the thighs under them, one outline square left between them and each hand.
  6. The arms shortened (the user, 2026-10-04: 「瑞兹的手臂看起来可以稍微改短一点」): ARM_CUT rows taken out of each
     upper arm from CUT_FROM down, everything of the arm under them - the elbow, the bracer, the hand - moved up as
     many rows; the squares it leaves are ground (the hands hang beside the hips, outside the body).
     tools/art/rig_ryze.py cuts the arm parts and puts the joints by the same ARM_CUT, so every posed arm in the
     actions (tools/art/ryze_arms.py, the idle's own arm squares) is as much shorter as the idle's.
The figure: 41 rows, 24 columns. Written at 8x on the first design's 128 x 128 canvas (soles on row 99, the feet's
middle on column 64): assets/source/ryze/design_v2/ryze_design_v2.png, and _1x. --check compares with the files.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SRC = os.path.join(ROOT, "assets", "source", "ryze")
MASTER = os.path.join(SRC, "codex_model_v2", "ryze_design_B.png")
OLD = os.path.join(ROOT, "assets", "source", "native", "ryze_native.png")
OUT = os.path.join(SRC, "design_v2", "ryze_design_v2.png")
Z = 8
ROWS = 41
CANVAS, SOLES, MID = 128, 99, 64
HEAD_ROWS = (1, 10)               # the first design's figure rows pasted: the crown to the beard's top
HEAD_X0 = 7                       # ... from this column (the scroll is left of it)
WHITE = (0xFB, 0xFB, 0xFD)        # the eyes' white
PAPER = (0xF4, 0xEE, 0xEA)


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


def crop(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def old_figure():
    a = np.asarray(Image.open(lp(OLD)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return crop(a)


def samples(a, block, px, py):
    h, w = a.shape[:2]
    xs = np.clip(np.rint(np.arange(px + block / 2, w, block)).astype(int), 0, w - 1)
    ys = np.clip(np.rint(np.arange(py + block / 2, h, block)).astype(int), 0, h - 1)
    return a[ys[:, None], xs[None, :]].copy(), xs, ys


def read_master(pal):
    a = np.asarray(Image.open(lp(MASTER)).convert("RGBA"))
    op = a[..., 3] >= 128
    ys, _ = np.nonzero(op)
    H = ys.max() - ys.min() + 1
    rgb = a[..., :3].astype(int)
    edge = np.zeros(op.shape, bool)
    edge[:, :-1] |= np.abs(np.diff(rgb, axis=1)).max(2) > 36
    edge[:-1, :] |= np.abs(np.diff(rgb, axis=0)).max(2) > 36
    best = None
    for block in np.arange(H / (ROWS + 0.6), H / (ROWS - 0.6), 0.25):
        for py in np.arange(0, block, block / 6):
            for px in np.arange(0, block, block / 6):
                s, sx, sy = samples(a, block, px, py)
                m = s[..., 3] >= 128
                r = np.nonzero(m.any(1))[0]
                if not len(r) or r.max() - r.min() + 1 != ROWS:
                    continue
                key = ((edge[sy[:, None], sx[None, :]] & m).sum(), -int(m.sum()))
                if best is None or key < best[0]:
                    best = (key, s)
    s = best[1]
    m = s[..., 3] >= 128
    dist = ((s[..., None, :3].astype(float) - pal[None, None]) ** 2).sum(-1)
    for i, c in enumerate(pal):
        if tuple(int(v) for v in c) == WHITE:
            dist[..., i] = np.inf
    out = np.zeros(s.shape, np.uint8)
    out[m, :3] = pal[dist.argmin(-1)][m].astype(np.uint8)
    out[m, 3] = 255
    return crop(out)


def eye(a):
    w = np.all(a[..., :3] == WHITE, -1) & (a[..., 3] > 0)
    w[:, :10] = False
    ys, xs = np.nonzero(w)
    return int(ys.min()), int(xs.min())


def transplant(body, old):
    out = body.copy()
    w = np.all(out[..., :3] == WHITE, -1) & (out[..., 3] > 0)
    out[w, :3] = PAPER
    oy, ox = eye(old)
    # B's near eye: the first design's head is placed where B's head has its eyes (rows 6-7, columns 13-14 of B)
    by, bx = B_EYE
    dy, dx = by - oy, bx - ox
    y0, y1 = HEAD_ROWS
    out[max(0, y0 + dy):y1 + dy + 1, HEAD_X0 + dx:] = 0
    for y in range(y0, y1 + 1):
        for x in range(HEAD_X0, old.shape[1]):
            if old[y, x, 3] and 0 <= y + dy < out.shape[0] and 0 <= x + dx < out.shape[1]:
                out[y + dy, x + dx] = old[y, x]
    return crop(out)


B_EYE = (6, 13)                   # B's own near eye (its white 2 x 2) in the 41-row read

# the hands redrawn (the read left them six loose squares each, the near one open on its right: the user's crop
# 「这里还变形」): an open hand three squares wide hanging under the bracer, lit on its outer side, the fingertips
# a square lower, one outline round it; (x, y) from the standing point
HANDS = {
    # the near hand under its bracer (columns 7-9), lit on the right
    (7, -2): "9270F2", (8, -2): "A88CFB", (9, -2): "C8B5FD",
    (7, -1): "6B44CC", (8, -1): "9270F2", (9, -1): "A88CFB",
    (7, 0): "511AC4", (8, 0): "6B44CC", (9, 0): "9270F2",
    (8, 1): "511AC4",
    (6, -2): "0F0213", (10, -2): "0F0213", (6, -1): "0F0213", (10, -1): "0F0213", (6, 0): "0F0213",
    (10, 0): "0F0213", (7, 1): "0F0213", (9, 1): "0F0213", (8, 2): "0F0213",
    # the far hand under its bracer (columns -9..-7), lit on the left
    (-9, -2): "C8B5FD", (-8, -2): "A88CFB", (-7, -2): "9270F2",
    (-9, -1): "A88CFB", (-8, -1): "9270F2", (-7, -1): "6B44CC",
    (-9, 0): "9270F2", (-8, 0): "6B44CC", (-7, 0): "511AC4",
    (-8, 1): "511AC4",
    (-10, -2): "0F0213", (-6, -2): "0F0213", (-10, -1): "0F0213", (-6, -1): "0F0213", (-10, 0): "0F0213",
    (-6, 0): "0F0213", (-9, 1): "0F0213", (-7, 1): "0F0213", (-8, 2): "0F0213",
}


# the windows the hands close between the arms and the coat (strips.complete_outline's closed outline, holes found
# by work/ks2/frame_check.py), (x, y) from the standing point
WINDOW = [(-5, -7), (-5, -6), (-5, -5), (-6, -4), (-5, -4), (-6, -3), (-5, -3), (5, -3), (5, -2)]
SEAM = "0F0213"
# the hips under the belt: the trousers' navy (light outside, dark inside, as the thighs under them), (x, y) from the
# standing point's pivot
HIPS = {(-5, -4): "112A70", (-4, -4): "18235D", (-3, -4): "233D98", (-2, -4): "18235D", (4, -4): "233D98",
        (-5, -3): "233D98", (-4, -3): "18235D", (3, -3): "112A70", (4, -3): "233D98", (5, -3): "18235D",
        (-5, -2): "233D98", (5, -2): "233D98", (-5, -1): "233D98", (5, -1): "112A70", (-5, 0): "233D98",
        (5, 0): "112A70"}


# step 6: rows out of the upper arms (from the standing point)
ARM_CUT = 2
CUT_FROM = -11
# the hanging arms before the cut, as tools/art/rig_ryze.py's boxes cut them (x, y from the standing point), and the
# hands' lowest outline squares under them
ARM_BOX = {
    "far": lambda x, y: (-11 <= x <= -5 and -14 <= y <= -7) or (-12 <= x <= -6 and -6 <= y <= 1),
    "near": lambda x, y: ((5 <= x <= 8 and -13 <= y <= -7) or (x == 4 and -10 <= y <= -7)
                          or (5 <= x <= 10 and -6 <= y <= 1) or (x == 4 and -6 <= y <= -3)),
}
ARM_TIPS = [(-8, 2), (8, 2)]


def shorten(c):
    """Step 6: ARM_CUT rows out of each upper arm from CUT_FROM down, the arm under them moved up (the arm's own
    squares only: skin, outline, the bracer's leathers and golds - rig_ryze.ARM_KEEP)."""
    if not ARM_CUT:
        return c
    import rig_ryze as R                                    # (it imports this module: loaded here, not at the top)
    c = c.copy()
    py, px = SOLES - 11, MID
    arm = {}
    for side, box in ARM_BOX.items():
        for y in range(-16, 3):
            for x in range(-13, 12):
                q = c[py + y, px + x]
                if q[3] and (box(x, y) or (x, y) in ARM_TIPS) and R.code(q) in R.ARM_KEEP:
                    arm[(x, y)] = q.copy()
    for (x, y) in arm:
        c[py + y, px + x] = 0
    for (x, y), q in arm.items():
        if y < CUT_FROM:
            c[py + y, px + x] = q
        elif y >= CUT_FROM + ARM_CUT:
            c[py + y - ARM_CUT, px + x] = q
    return c


def on_canvas(fig):
    H, W = fig.shape[:2]
    feet = np.nonzero(fig[H - 1, :, 3])[0]
    mid = (feet.min() + feet.max()) // 2
    c = np.zeros((CANVAS, CANVAS, 4), np.uint8)
    y0, x0 = SOLES - (H - 1), MID - mid
    c[y0:y0 + H, x0:x0 + W] = fig
    return c


def hands(c):
    """The redrawn hands (HANDS), the windows they close (WINDOW) and the hips (HIPS) on the canvas, (x, y) from the
    standing point."""
    c = c.copy()
    for (x, y), h in list(HANDS.items()) + [(xy, SEAM) for xy in WINDOW] + list(HIPS.items()):
        c[SOLES - 11 + y, MID + x] = [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255]
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    old = old_figure()
    pal = np.unique(old[old[..., 3] > 0][:, :3], axis=0).astype(float)
    fig = transplant(read_master(pal), old)
    c = shorten(hands(on_canvas(fig)))
    fig = crop(c)
    big = np.repeat(np.repeat(c, Z, 0), Z, 1)
    n = len(np.unique(fig[fig[..., 3] > 0][:, :3], axis=0))
    print(f"design v2: {fig.shape[1]} x {fig.shape[0]}, {n} colours, {int((fig[..., 3] > 0).sum())} squares")
    one = OUT.replace(".png", "_1x.png")
    if args.check:
        same = all(os.path.exists(lp(p)) and np.array_equal(np.asarray(Image.open(lp(p)).convert("RGBA")), arr)
                   for p, arr in ((OUT, big), (one, c)))
        print("the files are what a run writes" if same else "DIFFERENT")
        sys.exit(0 if same else 1)
    os.makedirs(lp(os.path.dirname(OUT)), exist_ok=True)
    Image.fromarray(big).save(lp(OUT))
    Image.fromarray(c).save(lp(one))
    print("wrote", os.path.relpath(OUT, ROOT), "and", os.path.relpath(one, ROOT))


if __name__ == "__main__":
    main()
