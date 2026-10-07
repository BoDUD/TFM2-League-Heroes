#!/usr/bin/env python3
"""Viktor's game-size design from Codex's step-1 version B (the user's pick 2026-10-07: 「Codex B 30x42 精修」).

    python tools/art/design_viktor.py [--out assets/source/native/viktor_native.png] [--review dir]

Reads assets/source/viktor/codex_model/viktor_design_B_1x.png (128x128, the figure 30x42 at cols 49-78, rows 58-99,
soles on row 99) and writes the design on the same 128x128 canvas. The user's notes on Codex's B: 「法杖歪的 其他都挺好」
and 「清碎块、补描边 中间这个黑线也要处理」 - only these, nothing else redrawn:
  1. the staff: the shaft goes straight up its column (7 of the figure) and the hooked head sits on top of it (Codex
     drew the head beside the shaft, cols 0-5, and the shaft's top ran on into the mechanical arm's slant: a bent staff);
  1b. the shaft's kink (the user: 「法杖这一段有点歪 可以顺便修复了」, the crop found by pixel search): Codex's shaft runs on
     column 7 of the figure down to row 30 and on column 8 from row 31 to its foot (row 40); the lower piece (columns 6-9)
     moves one column left onto column 7, the column it leaves takes the cape's colour beside it, else ink;
  2. the waist's black line: row 27 of the figure, between the gold chest plate and the gold belt, takes the colour
     below it (above it where that is ink too);
  3. crumbs: a near-black square inside the figure joining no line (at most one near-black 4-neighbour, all
     4-neighbours opaque) takes its neighbours' commonest colour - the mask and eyes (FACE), the claw and the staff's head
     kept; no colour square is touched (v1 also evened every lone colour square: 「色素清太多了」);
  4. the outline closed (strips.complete_outline).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


SRC = os.path.join(REPO, "assets", "source", "viktor", "codex_model", "viktor_design_B_1x.png")
OUT = os.path.join(REPO, "assets", "source", "native", "viktor_native.png")
X0, Y0, W, H = 49, 58, 30, 42           # the figure's box on the canvas
INK = (11, 9, 16)
C = {"A": "#0B0910", "O": "#7E86B8", "K": "#5B6194", "b": "#FF8A1E", "Y": "#D49A1E", "a": "#F7D04A", "R": "#A0202A",
     "W": "#C8400A", "F": "#3A2C40"}
# step 1: the staff's head, rows 9-15 of the figure ('.' = left as it is)
HEAD = {
    9: (5, "AAA"),
    10: (4, "AaYbA"),
    11: (3, "AYAAAbA"),
    12: (3, "ARA.ARA"),
    13: (3, "AbYAYWA"),
    14: (4, "AAYAA"),
    15: (5, "AOA"),
}
STAFF_X = 7
OLD_HEAD = (slice(11, 22), slice(0, 6))  # Codex's head beside the shaft
KINK_ROWS, KINK_COLS = range(31, 41), (6, 10)  # the shaft's lower piece, moved one column left
CAPE = {hx(h) for h in ("#5A0A1E", "#95142E", "#C62A44")}
WAIST_ROW, WAIST_COLS = 27, range(12, 21)
FACE = (slice(7, 18), slice(16, 26))     # the mask and the eyes
CLAW = (slice(0, 9), slice(0, 11))       # the mechanical arm's gold claw and its cyan core
# accents (gold, cyan, orange, red) are details, never crumbs
ACCENT = {hx(h) for h in ("#8A5A10", "#D49A1E", "#F7D04A", "#FFF1A0", "#1A8AD0", "#4AD8F8", "#C8F6FF", "#FF8A1E",
                          "#C8400A", "#A0202A")}
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def put(c, y, x, ch):
    c[y, x, :3] = hx(C[ch])
    c[y, x, 3] = 255


def staff(c):
    c[OLD_HEAD] = 0
    for r, (x, s) in HEAD.items():
        for i, ch in enumerate(s):
            if ch != ".":
                put(c, r, x + i, ch)
    for r in range(16, 22):
        put(c, r, STAFF_X - 1, "A")
        put(c, r, STAFF_X, "O")
        if c[r, STAFF_X + 1, 3] == 0 or r < 18:
            put(c, r, STAFF_X + 1, "A")


def kink(c):
    a, b = KINK_COLS
    for r in KINK_ROWS:
        old = c[r].copy()
        c[r, a - 1:b - 1] = old[a:b]
        right = old[b]
        if right[3] and tuple(int(v) for v in right[:3]) in CAPE:
            c[r, b - 1] = right
        elif right[3]:
            put(c, r, b - 1, "A")
        else:
            c[r, b - 1] = 0


def is_ink(p):
    return p[3] > 0 and tuple(int(v) for v in p[:3]) == INK


def waist(c):
    y = WAIST_ROW
    for x in WAIST_COLS:
        if not is_ink(c[y, x]):
            continue
        below, above = c[y + 1, x], c[y - 1, x]
        src = below if below[3] and not is_ink(below) else above if above[3] and not is_ink(above) else None
        if src is not None:
            c[y, x] = src


def keep_mask():
    k = np.zeros((H, W), bool)
    k[FACE] = True
    k[CLAW] = True
    for r, (x, s) in HEAD.items():
        k[r, x:x + len(s)] = True
    return k


def lone(c, keep, rounds=2):
    for _ in range(rounds):
        b = c.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if c[y, x, 3] == 0 or keep[y, x] or is_ink(c[y, x]):
                    continue
                p = tuple(int(v) for v in c[y, x, :3])
                if p in ACCENT:
                    continue
                n8 = [c[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
                if any(q[3] == 0 for q in n8) or any(tuple(int(v) for v in q[:3]) == p for q in n8):
                    continue
                n4 = [tuple(int(v) for v in c[y + dy, x + dx, :3]) for dy, dx in N4]
                best = max(sorted(set(n4)), key=n4.count)
                if n4.count(best) >= 2 and best not in ACCENT:
                    b[y, x, :3] = best
        c = b
    return c


def lone_ink(c, keep):
    op = c[..., 3] > 0
    isk = op & (c[..., :3] == INK).all(-1)
    hits = []
    for y, x in zip(*np.nonzero(isk & ~keep)):
        nb = [(y + dy, x + dx) for dy, dx in N4]
        if not all(0 <= yy < H and 0 <= xx < W and op[yy, xx] for yy, xx in nb):
            continue
        if sum(isk[yy, xx] for yy, xx in nb) > 1:
            continue
        cols = [tuple(int(v) for v in c[yy, xx, :3]) for yy, xx in nb if not isk[yy, xx]]
        hits.append((y, x, max(sorted(set(cols)), key=cols.count)))
    for y, x, col in hits:
        c[y, x, :3] = col
    return len(hits)


def build(crumbs=False):
    a = np.array(Image.open(lp(SRC)).convert("RGBA"))
    c = a[Y0:Y0 + H, X0:X0 + W].copy()
    staff(c)
    kink(c)
    waist(c)
    # the user at v1 (lone() over every colour, then lone_ink): 「你这个改的不如之前一版本啊 色素清太多了」 - only the lone
    # near-black dots go, no colour square is touched
    if crumbs:
        print("lone ink dots", lone_ink(c, keep_mask()))
    out = np.zeros_like(a)
    out[Y0:Y0 + H, X0:X0 + W] = c
    out, _, _ = strips.complete_outline(out, color=INK, feet=Y0 + H - 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--review", help="write before / v3 (no crumbs cleared) / v2 (lone ink cleared) at 10x here")
    ap.add_argument("--crumbs", action="store_true", help="also clear the lone near-black dots (v2)")
    a = ap.parse_args()
    out = build(a.crumbs)
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    Image.fromarray(out).save(lp(a.out))
    if a.review:
        before = np.array(Image.open(lp(SRC)).convert("RGBA"))
        crop = lambda im: Image.fromarray(im[Y0 - 2:Y0 + H + 2, X0 - 3:X0 + W + 3]).resize(((W + 6) * 10, (H + 4) * 10),
                                                                                        Image.NEAREST)
        panes = [before, build(False), build(True)]
        sheet = Image.new("RGBA", ((W + 6) * 10 * 3 + 60, (H + 4) * 10), (255, 255, 255, 255))
        for i, im in enumerate(panes):
            sheet.alpha_composite(crop(im), (i * ((W + 6) * 10 + 30), 0))
        sheet.convert("RGB").save(os.path.join(a.review, "viktor_design_fix_v3.png"))
    ys, xs = np.nonzero(out[..., 3])
    print(a.out, f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}",
          len({tuple(p) for p in out[out[..., 3] > 0][:, :3]}), "colours")


if __name__ == "__main__":
    main()
