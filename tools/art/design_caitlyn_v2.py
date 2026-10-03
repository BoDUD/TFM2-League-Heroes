#!/usr/bin/env python3
"""Caitlyn's second design: Codex's slim, long-legged body (v2 option A) under the first design's head (2026-10-03).

    python tools/art/design_caitlyn_v2.py [--check]

Players found the first design's legs too short and her too fat. Stretching its rows was rejected (「这么抽象」); Codex
redrew the idle after oppi's Caitlyn's proportions (assets/source/caitlyn/MODEL_V2.md, codex_model_v2/: options A / B /
C), the user picked A but not its face (「脸部细节眼睛要做好一点」), then asked for the first design's face on it
(「能把这个脸移植过去吗」), a smaller head (「头可以适当缩小点」) and A's rifle at its full length (「枪还是太短」):
「OK完美」. Steps, all from the repo:
  1. Codex's master A (codex_model_v2/caitlyn_design_A.png; about 18 px squares, ~80 rows) read at 40 rows, one game
     pixel per 2 x 2 of its squares, as tools/art/shrink_vi.py reads Vi's: a block is drawn when 35% of it is opaque,
     the outline's darks win a block they hold 40% of, else the commonest colour (snapped to the master's own 24); the
     column phase is the one whose read is one connected piece with the most squares; then the same grid read by
     plain majority (half the block opaque) keeps its cleaner colours, the outline read filling only its gaps (the
     thin legs broke into pieces: 「而且腿部缺失模型了」).
  2. The legs below the skirt (LEGS): both straight (a square's jog at the right knee read as bent: 「这版腿部就是这里
     有点歪」), outline both sides, the tights' navy, gold garters and boot tops, brown knee pads and boots, toes right.
     A gold square with no gold among its 8 neighbours and 4 drawn neighbours (rows 11-25) takes their commonest colour.
  3. The head: the first design's (assets/source/native/caitlyn_native.png: rows 0-19 of its figure, top hat, hair
     and the approved face) with rows HEAD_DROP and columns COL_DROP taken out (the crown, the brim's underside, the
     hair over the bangs and down the sides; never the face), its neck over A's, and its long hair (rows 20-27, left
     of column 9) behind A's back; A's body from its collar (row 11) down.
  4. A's rifle above the collar (rows 0-10 from column 13) back over the head.
The figure: 45 rows, 28 columns, 35 colours. Written at 8x on the first design's 128 x 128 canvas (soles on row 99, the
feet's middle on column 64, the standing point 11 rows over the soles): assets/source/caitlyn/design_v2/
caitlyn_design_v2.png, and _1x. --check compares with the files instead of writing them.
"""
import argparse
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
from strips import label  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "caitlyn")
MASTER = os.path.join(SRC, "codex_model_v2", "caitlyn_design_A.png")
OLD = os.path.join(ROOT, "assets", "source", "native", "caitlyn_native.png")
OUT = os.path.join(SRC, "design_v2", "caitlyn_design_v2.png")
Z = 8
ROWS = 40                         # A read at 40 rows
CANVAS, SOLES, MID = 128, 99, 64  # the 8x canvas: the soles' row, the feet's middle column
A_FROM, A_NECK, OLD_NECK = 11, 9, 15
HEAD_ROWS, HAIR_ROWS, RIFLE = 20, (20, 28), 13
HEAD_DROP = (2, 9, 10, 12)        # the crown's second row, the brim's underside, the hair over the bangs, the forehead
COL_DROP = (3, 4, 8, 21)          # the brim's left end and the hair down both sides
HAIR = {(0x27, 0x2A, 0x50), (0x1D, 0x1C, 0x34), (0x0A, 0x02, 0x0E), (0x10, 0x02, 0x16)}
GOLD = {(0xFD, 0xC4, 0x29), (0xFC, 0xBE, 0x2E), (0xFE, 0xEE, 0xA3), (0xFD, 0xD5, 0x77)}
P = {"c": (0x0D, 0x00, 0x12), "j": (0x30, 0x34, 0x5C), "m": (0x7A, 0x44, 0x29), "o": (0x91, 0x55, 0x26),
     "k": (0x68, 0x39, 0x34), "q": (0xFD, 0xC4, 0x29)}
# rows 26-39 of A, columns 0-17: "?" keeps the read, "." clears
LEGS = ["??????????????????",
        ".....cjjc..cjjc...",     # thighs, two squares apart
        ".....cjjc..cjjc...",
        ".....cqkc..cqkc...",     # garters
        ".....cmoc..cmoc...",     # knee pads
        ".....cjjc..cjjc...",     # shins
        ".....cjjc..cjjc...",
        ".....cqqc..cqqc...",     # boot tops
        ".....cmmc..cmmc...",
        ".....cmoc..cmoc...",
        ".....cmqc..cmqc...",     # buckles
        ".....cmmoc.cmmoc..",     # feet, toes right
        ".....ckmoc.ckmmoc.",
        ".....ccccc.cccccc."]


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


def read_blocks(src, left, bottom, px, W, H, cols, pal, solid, dark, darks):
    """An H x W picture whose square (r, c) reads src over [bottom - (H - r) * px, ...) x [left + c * px, ...)."""
    out = np.zeros((H, W, 4), np.uint8)
    for r in range(H):
        ya, yb = int(round(bottom - (H - r) * px)), int(round(bottom - (H - r - 1) * px))
        for c in range(W):
            xa, xb = int(round(left + c * px)), int(round(left + (c + 1) * px))
            blk = src[max(0, ya):max(0, yb), max(0, xa):max(0, xb)].reshape(-1, 4)
            if not len(blk):
                continue
            op = blk[blk[:, 3] > 128]
            if not len(op) or len(op) < solid * len(blk):
                continue
            k = np.argmin(((op[:, None, :3].astype(float) - pal[None]) ** 2).sum(-1), 1)
            counts = Counter(cols[i] for i in k)
            dk = {h: v for h, v in counts.items() if h in darks}
            best = max(dk, key=dk.get) if dk and sum(dk.values()) >= dark * len(k) else max(counts, key=counts.get)
            out[r, c, :3] = [int(best[i:i + 2], 16) for i in (0, 2, 4)]
            out[r, c, 3] = 255
    return out


def read_a():
    a = np.asarray(Image.open(lp(MASTER)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] >= 128)
    top, bottom = ys.min(), ys.max() + 1
    p = (bottom - top) / ROWS
    q = Image.fromarray(a[..., :3]).quantize(24, method=Image.Quantize.MEDIANCUT)
    raw = q.getpalette()
    pal = np.array(raw[:len(raw) // 3 * 3], float).reshape(-1, 3)
    cols = ["%02X%02X%02X" % tuple(int(v) for v in c) for c in pal]
    darks = {c for c in cols if sum(int(c[i:i + 2], 16) for i in (0, 2, 4)) < 90}
    W = int(np.ceil((xs.max() - xs.min() + 1) / p)) + 2
    best = None
    for ph in np.arange(0, p, 1.0):
        r = read_blocks(a, xs.min() - p + ph, bottom, p, W, ROWS, cols, pal, 0.35, 0.4, darks)
        _, n = label(r[..., 3] > 0)
        score = (n == 1, int((r[..., 3] > 0).sum()))
        if best is None or score > best[0]:
            best = (score, ph, r)
    _, ph, r = best
    m = read_blocks(a, xs.min() - p + ph, bottom, p, W, ROWS, cols, pal, 0.5, 1.01, darks)
    r = np.where(m[..., 3:4] > 0, m, r)
    ys, xs = np.nonzero(r[..., 3])
    return r[:, xs.min():xs.max() + 1]


def legs_and_specks(a):
    a = np.pad(a, ((0, 0), (0, max(0, 18 - a.shape[1])), (0, 0)))
    out = a.copy()
    for k, line in enumerate(LEGS):
        for x, ch in enumerate(line):
            y = 26 + k
            if ch == "?":
                continue
            out[y, x] = 0 if ch == "." else (*P[ch], 255)
    clean = out.copy()
    for y in range(11, 26):
        for x in range(1, out.shape[1] - 1):
            if not out[y, x, 3] or tuple(int(v) for v in out[y, x, :3]) not in GOLD:
                continue
            nb8 = [out[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if any(p[3] and tuple(int(v) for v in p[:3]) in GOLD for p in nb8):
                continue
            nb4 = [out[y - 1, x], out[y + 1, x], out[y, x - 1], out[y, x + 1]]
            if all(p[3] for p in nb4):
                clean[y, x, :3] = Counter(tuple(int(v) for v in p[:3]) for p in nb4).most_common(1)[0][0]
    return clean


def old_figure():
    a = np.asarray(Image.open(lp(OLD)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def transplant(a, old):
    head = np.delete(np.delete(old[:HEAD_ROWS, :24], list(HEAD_DROP), axis=0), list(COL_DROP), axis=1)
    hair = np.delete(old[HAIR_ROWS[0]:HAIR_ROWS[1], :9], [c for c in COL_DROP if c < 9], axis=1)
    body = a[A_FROM:]
    dx = OLD_NECK - sum(1 for c in COL_DROP if c < OLD_NECK) - A_NECK
    H, hy = head.shape[0] + body.shape[0], head.shape[0]
    W = max(head.shape[1], body.shape[1] + dx)
    out = np.zeros((H, W, 4), np.uint8)
    for y in range(hair.shape[0]):
        for x in range(hair.shape[1]):
            p = hair[y, x]
            if p[3] and tuple(int(v) for v in p[:3]) in HAIR:
                out[hy + y, x] = p
    b = out[hy:, dx:dx + body.shape[1]]
    m = body[..., 3] > 0
    b[m] = body[m]
    hm = head[..., 3] > 0
    out[:hy, :head.shape[1]][hm] = head[hm]
    top = a[:A_FROM, RIFLE:]
    for y, x in zip(*np.nonzero(top[..., 3])):
        out[hy - A_FROM + y, RIFLE + dx + x] = top[y, x]
    ys, xs = np.nonzero(out[..., 3])
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def on_canvas(fig):
    """The figure on the 128 x 128 canvas, its lowest row on SOLES, its feet's middle on MID."""
    H, W = fig.shape[:2]
    feet = np.nonzero(fig[H - 1, :, 3])[0]
    mid = (feet.min() + feet.max()) // 2
    c = np.zeros((CANVAS, CANVAS, 4), np.uint8)
    y0, x0 = SOLES - (H - 1), MID - mid
    c[y0:y0 + H, x0:x0 + W] = fig
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    fig = transplant(legs_and_specks(read_a()), old_figure())
    c = on_canvas(fig)
    big = np.repeat(np.repeat(c, Z, 0), Z, 1)
    n = len(np.unique(fig[fig[..., 3] > 0][:, :3], axis=0))
    print(f"design v2: {fig.shape[1]} x {fig.shape[0]}, {n} colours")
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
