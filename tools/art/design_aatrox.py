#!/usr/bin/env python3
"""Aatrox's design (assets/source/native/aatrox_native.png): Codex's generated slim draft brought to game size, with
the head and the greatsword of the first design.

    python tools/art/design_aatrox.py [--check] [--review OUT.png]

How it came about (2026-10-03):
  - first design (assets/source/aatrox/design_v1/aatrox_design_v1_1x.png, 44 x 40): Codex's A (codex_model/, its raw
    draft box-sampled to 40 rows) with the face A2 picked by the user (the grey face under the helm turned to its
    shadow #181F2B, the eyes #F2323B with a #8F0E2B glow under each), the greatsword and near foot redrawn by Codex
    (codex_sword_fix/: straight barbed blade, two-pronged tip, the orange eye by the guard) and the far leg's greave
    and clawed boot mirrored onto the near leg (the user: 「左右脚形状不一样」, then B: toes out);
  - the user: 「剑魔也有点肥胖瘦身一下」 (1084 squares, body and arms 27 wide). Codex's slim pass (codex_model_v2/)
    drew its A/B/C by polygons on the 40-row canvas; the user picked its generated draft A instead
    (codex_model_v2/aatrox_design_A_generated.png: 「用这个版本 这不是很完美吗？？」), then the crisp sampling 「1 清晰版」,
    then the straight sword held at the fist 「剑调一下 被做歪的」 -> 「1」.
Steps:
  1. the draft read back on its own grid (the skill's regrid.py, 15 px squares): 73 x 69, every square the nearest
     colour of the design palette (PALETTE, Codex's 21 colours) in CIELAB;
  2. down to 40 rows by area: every new square the colour covering most of it (clear when clear covers most);
  3. the sampled helm (OLD_HEAD) cleared and the first design's head pasted (HEAD, moved HEAD_SHIFT: its chin on the
     sampled chin) - at 40 rows the draft's red eyes were lost; strips.complete_outline;
  4. the sampled sword (bent by the sampling: its upper half at ~0.44, its lower at ~0.7, and its eye lost) cleared
     (CLEAR) and the first design's blade pasted, moved only (SWORD_SHIFT: the guard at the near fist), pinholes at
     the hilt filled with outline; strips.complete_outline;
  5. on the 128 x 128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
--check compares the result with the committed aatrox_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aatrox")
DRAFT = os.path.join(SRC, "codex_model_v2", "aatrox_design_A_generated.png")
FIRST = os.path.join(SRC, "design_v1", "aatrox_design_v1_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "aatrox_native.png")
# Codex's palette (codex_model/aatrox_palette.txt) and the letter of each colour in the tables below
KEYS = "o0123456789abcdefghij"
PALETTE = ["#0A0408", "#1F2A38", "#3B586B", "#5B8498", "#95C3D4", "#CDEBF0", "#4B0827", "#8F0E2B", "#BF1630",
           "#F2323B", "#270D28", "#42224C", "#68407A", "#865D9F", "#181F2B", "#263647", "#FF7A2A", "#FFD27A",
           "#655771", "#A895BA", "#C7BBD5"]
COL = {k: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for k, h in zip(KEYS, PALETTE)}
INV = {v: k for k, v in COL.items()}
ROWS = 40
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3
# the first design's head, row -> spans of columns: the horns, the helm, the shadow face with the red eyes, the chin
HEAD = {3: [(26, 26)], 4: [(25, 27)], 5: [(25, 28), (31, 31)], 6: [(25, 32)], 7: [(24, 33)], 8: [(23, 33)],
        9: [(23, 33)], 10: [(24, 33)], 11: [(24, 32)], 12: [(25, 31)], 13: [(26, 31)], 14: [(27, 30)]}
HEAD_SHIFT = (-2, 0)
# the sampled helm, row -> first, last column (cleared before the paste)
OLD_HEAD = {3: (26, 27), 4: (26, 30), 5: (26, 31), 6: (25, 32), 7: (24, 32), 8: (23, 32), 9: (25, 32), 10: (24, 31),
            11: (26, 31), 12: (27, 29)}
# the sampled sword: row -> last column cleared (the near leg begins one column further; rows 23-25 are the old hilt
# over the near fist)
CLEAR = {23: 22, 24: 22, 25: 22, 26: 22, 27: 23, 28: 22, 29: 22, 30: 21, 31: 21, 32: 21, 33: 21, 34: 21, 35: 20,
         36: 20, 37: 19, 38: 18, 39: 18}
SWORD_SHIFT = (-3, 2)
BLADE = set("56789abcfg")             # the blade's plum / red / orange letters
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    with Image.open(lp(path)) as im:
        return np.asarray(im.convert("RGBA"))


def letters(a):
    return [["." if a[r, c, 3] == 0 else INV[tuple(int(v) for v in a[r, c, :3])] for c in range(a.shape[1])]
            for r in range(a.shape[0])]


def image(g):
    a = np.zeros((len(g), len(g[0]), 4), np.uint8)
    for r, row in enumerate(g):
        for c, k in enumerate(row):
            if k != ".":
                a[r, c, :3] = COL[k]
                a[r, c, 3] = 255
    return a


def srgb2lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def sample(idx, rows):
    """Area sampling: every new square the palette index covering most of it (-1 = clear)."""
    H, W = idx.shape
    s = H / rows
    cols = int(round(W / s))
    out = np.full((rows, cols), -1)
    for r in range(rows):
        for c in range(cols):
            y0, y1, x0, x1 = r * s, (r + 1) * s, c * s, (c + 1) * s
            w = np.zeros(len(KEYS) + 1)
            for y in range(int(y0), min(H, int(np.ceil(y1)))):
                wy = min(y + 1, y1) - max(y, y0)
                for x in range(int(x0), min(W, int(np.ceil(x1)))):
                    wx = min(x + 1, x1) - max(x, x0)
                    w[idx[y, x] + 1] += wy * wx
            out[r, c] = -1 if w[0] > w[1:].max() else int(w[1:].argmax())
    return out


def outlined(a):
    """strips.complete_outline round the figure (2 clear squares of margin), cropped to the figure again."""
    can = np.zeros((a.shape[0] + 4, a.shape[1] + 4, 4), np.uint8)
    can[2:-2, 2:-2] = a
    sole = 2 + np.nonzero(a[..., 3].any(1))[0].max()
    can, _, _ = strips.complete_outline(can, color=COL["o"], feet=sole)
    ys, xs = np.nonzero(can[..., 3])
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def blade(first):
    """The first design's blade: every plum / red square of Codex's sword-fix box (rows 28-38, columns 0-19: the
    blade, the guard and its eye, the fork's two prongs, which outline squares cut off the blade) and the grip's end
    under the fists, with the outline squares round them; left of the near leg (columns 0-9) all of them, the fork's
    outline running on past its prongs."""
    g = letters(first)
    body = {(r, c) for r in range(28, 39) for c in range(0, 20) if g[r][c] in BLADE} | {(28, 20), (28, 21), (29, 20)}
    ring = {(r + dy, c + dx) for r, c in body for dy, dx in N8
            if 27 <= r + dy < 40 and 0 <= c + dx < 22 and g[r + dy][c + dx] == "o"}
    ring |= {(r, c) for r in range(28, 39) for c in range(0, 10) if g[r][c] == "o"}
    return {p: g[p[0]][p[1]] for p in body | ring}


def build():
    raw, _, _ = regrid(load(DRAFT))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    assert raw.shape[:2] == (69, 73), raw.shape
    P = np.array([COL[k] for k in KEYS])
    d = ((srgb2lab(raw[..., :3])[:, :, None, :] - srgb2lab(P)[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    idx[raw[..., 3] < 128] = -1
    g = [["." if i < 0 else KEYS[i] for i in row] for row in sample(idx, ROWS)]
    # the head
    first = load(FIRST)
    fl = letters(first)
    for r, (c0, c1) in OLD_HEAD.items():
        for c in range(c0, c1 + 1):
            g[r][c] = "."
    dr, dc = HEAD_SHIFT
    for r, spans in HEAD.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                if fl[r][c] != ".":
                    g[r + dr][c + dc] = fl[r][c]
    g = letters(outlined(image(g)))
    # the sword
    H, W = len(g), len(g[0])
    for r, last in CLEAR.items():
        for c in range(0, last + 1):
            g[r][c] = "."
    dr, dc = SWORD_SHIFT
    for (r, c), k in blade(first).items():
        rr, cc = r + dr, c + dc
        if 0 <= rr < H and 0 <= cc < W and (k != "o" or g[rr][cc] == "."):
            g[rr][cc] = k
    for r in range(24, 31):                 # pinholes between the hilt and the body
        for c in range(17, 26):
            if g[r][c] == "." and sum(0 <= r + dy < H and 0 <= c + dx < W and g[r + dy][c + dx] != "."
                                      for dy, dx in N4) >= 3:
                g[r][c] = "o"
    a = outlined(image(g))
    feet = np.nonzero((a[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    x0 = int(round(MID_COL - (feet.min() + feet.max()) / 2))
    y0 = SOLE_ROW + 1 - a.shape[0]
    can = np.zeros((128, 128, 4), np.uint8)
    can[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a 6x review picture")
    a = ap.parse_args()
    can = build()
    big = Image.fromarray(can).resize((1024, 1024), Image.NEAREST)
    ys, xs = np.nonzero(can[..., 3] > 0)
    cols = len({tuple(c) for c in can[can[..., 3] > 0][:, :3]})
    print(f"aatrox_native: {ys.max() - ys.min() + 1} rows x {xs.max() - xs.min() + 1} cols, {cols} colours, "
          f"{int((can[..., 3] > 0).sum())} squares, rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}")
    if a.check:
        same = np.array_equal(load(OUT), np.asarray(big))
        print("same as the committed file" if same else "DIFFERS from the committed file")
        sys.exit(0 if same else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    big.save(lp(OUT))
    if a.review:
        crop = can[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3]
        im = Image.fromarray(crop).resize((crop.shape[1] * 6, crop.shape[0] * 6), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (92, 98, 86, 255))
        bg.alpha_composite(im)
        ImageDraw.Draw(bg).text((4, 4), "aatrox_native", fill=(255, 255, 255))
        bg.convert("RGB").save(a.review)
    print(OUT)


if __name__ == "__main__":
    main()
