#!/usr/bin/env python3
"""Samira's design (assets/source/native/samira_native.png): Codex's generated draft attempt1_A read back on its own grid
and shrunk to 40 rows by whole rows and columns, every kept square the draft's own (tools/art/design_tryndamere.py's way).
A re-pose in oppi's idle stance (tools/art/pack_samira_pose.py -> codex_pose/) was tried and set aside: 「用左边的」.

    python tools/art/design_samira.py [--check]

How it came about (2026-10-06): the user picked Codex's picture A (codex_picture/samira-model-A.png: League's idle, hands
on her hips, the greatsword slung across her back). Codex's step 1 (codex_model/) came back too big - its drafts 53-81
squares tall - and its own 40-row cut of a later draft had changed her look. My first cuts kept the whole face (16 rows)
and squeezed the body from 65 rows to 26: the clothes broke into specks. The user: 「那这个慢慢调整啊 用工具 之前蛮王
赵兴不都调整了吗？」 (draft 1 attached), then 「40 行原样」 from an options sheet (40 as drawn / 40 with one_outline / 42 / 44).
Steps:
  1. codex_model/raw/attempt1_A.png read back on its own grid (the skill's regrid.py, alpha >= 128): 81 x 44 (8 px
     squares);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. to 40 rows: the rows in as many groups as are kept, in each group the rows most like a neighbour go
     (design_riven.keep_axis: three offsets of the grouping, the least loss kept), never the first or the last row nor
     EYE_ROWS (the eyepatch and the green eye); then the columns to WIDTH the same way, never EYE_COLS. Only the eyes
     are kept whole: head and body lose rows in proportion;
  4. strips.complete_outline where a deleted line held the outline (the eyes never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  6. WEAPONS (the user: 「武器有点看不清啊 你不好好调一下吗」「你可以参考隔壁oppi的怎么画的」): the cut had left the greatsword
     behind her as grey crumbs between the thigh and the braid. As oppi's Samira does, the weapons show OUTSIDE the
     silhouette: the old blade squares there (grey, under the hip, right of the front leg) go and a straight blade is
     drawn from BLADE_TOP to BLADE_TIP under the body - 3 wide: dark steel back, steel, a silver edge (the draft's own
     colours) - its point past the front leg; the near holster's pistol barrel runs 4 squares down the outer thigh
     (BARREL); the outline closed again, the face never touched;
  7. BOOTS (the user: 「你帮我挑挑干净 脚这里都是歪的」): the eye columns kept above them left the near leg uncut and the
     far leg's columns cut unevenly, so the shins stepped crookedly and the draft's boot texture came out as specks.
     Below the knees (rows 90-99) each boot is laid out row by row (LEFT_BOOT / RIGHT_BOOT: the outline squares, measured
     from the cut's own legs and set on straight lines): inside, the design's two greens (dark half, mid half), the red
     cuff row (CUFF) and a gold heel square, the soles' row all outline; loose squares round them go, the outline closed.
--check compares the result with the committed samira_native.png instead of writing it.
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
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "samira", "codex_model", "raw", "attempt1_A.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "samira_native.png")
K, HEIGHT, WIDTH = 28, 40, 27
EYE_ROWS = range(16, 21)           # on the 81 x 44 read-back: the eyepatch, the strap, the green eye
EYE_COLS = range(19, 28)
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3
BLADE_TOP, BLADE_TIP = (83.0, 72.0), (97.0, 82.0)     # canvas (row, column)
BARREL = (54, range(87, 91))                          # canvas column, rows
INK = (12, 8, 13)
LEFT_BOOT = {90: (55, 59), 91: (54, 59), 92: (54, 59), 93: (54, 59), 94: (53, 58), 95: (53, 58), 96: (53, 58),
             97: (53, 58), 98: (53, 59), 99: (53, 59)}
RIGHT_BOOT = {90: (67, 72), 91: (67, 72), 92: (67, 72), 93: (67, 72), 94: (67, 72), 95: (67, 72), 96: (67, 72),
              97: (67, 74), 98: (67, 76), 99: (67, 76)}
CUFF = 92
GREEN_D, GREEN_M, RED, RED_D, GOLD = (35, 43, 41), (56, 67, 61), (178, 4, 19), (110, 2, 15), (212, 118, 3)
STEEL_D, STEEL, SILVER, SILVER2 = (38, 41, 54), (119, 123, 144), (233, 235, 242), (181, 186, 210)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def build():
    raw = read_back()
    assert raw.shape[:2] == (81, 44), raw.shape
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    mid = R.keep_axis([idx[y] for y in range(1, H - 1)], HEIGHT - 2, range(EYE_ROWS.start - 1, EYE_ROWS.stop - 1))
    rows = [0] + [r + 1 for r in mid] + [H - 1]
    sub = idx[rows]
    cols = R.keep_axis([sub[:, x] for x in range(W)], WIDTH, EYE_COLS)
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in EYE_ROWS]
    fc = [cols.index(c) for c in EYE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return boots(weapons(out)), rows, cols, added


def is_blade(c):
    c = [int(v) for v in c]
    return (abs(c[0] - c[2]) < 45 and abs(c[1] - c[2]) < 45 and sum(c) > 150 and c[2] >= c[0]) or         tuple(c) in (STEEL_D, STEEL)


def boots(a):
    """Step 7: both boots below the knees laid out on straight edges in the design's own colours."""
    a = a.copy()
    for spans, (x0, x1) in ((LEFT_BOOT, (51, 62)), (RIGHT_BOOT, (65, 78))):
        for y in spans:
            for x in range(x0, x1):
                if a[y, x, 3] and not is_blade(a[y, x, :3]):
                    a[y, x, 3] = 0
    for spans in (LEFT_BOOT, RIGHT_BOOT):
        for y, (lft, rgt) in spans.items():
            inner = list(range(lft + 1, rgt))
            for x in range(lft, rgt + 1):
                if y == SOLE_ROW or x in (lft, rgt):
                    c = INK
                else:
                    i = inner.index(x)
                    c = GREEN_D if i < (len(inner) + 1) // 2 else GREEN_M
                    if y == CUFF:
                        c = RED_D if i == 0 else RED
                    if y == SOLE_ROW - 1 and i == 0:
                        c = GOLD
                a[y, x, :3], a[y, x, 3] = c, 255
    for _ in range(2):
        op = a[..., 3] > 0
        cnt = sum(np.roll(np.roll(op, dy, 0), dx, 1).astype(int) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        band = np.zeros_like(op)
        band[86:SOLE_ROW + 1, 50:84] = True
        a[op & (cnt <= 1) & band, 3] = 0
    keep = np.zeros(a.shape[:2], bool)
    keep[60:90] = True
    a, _, _ = strips.complete_outline(a, color=INK, feet=SOLE_ROW + 1, keep=keep)
    a[SOLE_ROW + 1:] = 0
    return a


def weapons(a):
    """Step 6: the blade under the hip redrawn straight and past the front leg, the near pistol's barrel down the thigh."""
    a = a.copy()
    col = a[..., :3].astype(int)
    op = a[..., 3] > 0
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    grey = (np.abs(col[..., 0] - col[..., 2]) < 45) & (np.abs(col[..., 1] - col[..., 2]) < 45) & (col.sum(-1) > 150)
    a[op & grey & (yy >= 82) & (xx >= 72), 3] = 0
    body = a[..., 3] > 0
    p0, tip = np.array(BLADE_TOP), np.array(BLADE_TIP)
    length = np.linalg.norm(tip - p0)
    u = (tip - p0) / length
    nrm = np.array([-u[1], u[0]])
    sword = np.zeros_like(a)
    for t in np.arange(0, length + 0.01, 0.2):
        p, left = p0 + u * t, length - t
        for k, c in ((-1, STEEL_D), (0, STEEL), (1, SILVER)):
            if (k == -1 and left < 2) or (k == 1 and left < 0.7):
                continue
            r, cc = (int(round(v)) for v in p + nrm * k)
            if r <= SOLE_ROW:
                sword[r, cc, :3], sword[r, cc, 3] = c, 255
    out = np.where(body[..., None], a, sword)
    c, rows = BARREL
    for r in rows:
        out[r, c, :3] = SILVER if r == rows.start else (SILVER2 if r < rows.stop - 1 else STEEL)
        out[r, c, 3] = 255
    keep = np.zeros(out.shape[:2], bool)
    keep[64:75, 57:73] = True                         # the face
    out, _, _ = strips.complete_outline(out, color=INK, feet=SOLE_ROW + 1, keep=keep)
    out[SOLE_ROW + 1:] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can, rows, cols, added = build()
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours, outline +{added}; rows kept {rows}; columns kept {cols}")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        return
    os.makedirs(os.path.dirname(lp(OUT)), exist_ok=True)
    Image.fromarray(can).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    # superseded 2026-10-09: the second design (tools/art/design_samira2.py, the user's ChatGPT picture) writes
    # samira_native.png now; running this would put the first design back
    if "--check" not in sys.argv:
        raise SystemExit("design_samira.py is superseded by tools/art/design_samira2.py (the second design)")
    main()
