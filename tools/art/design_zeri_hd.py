#!/usr/bin/env python3
"""Zeri's dense design (PPU 3): Codex's pictures read on a 120-row grid, the base the hand-finished tables start from.

    python tools/art/design_zeri_hd.py --base      # write ppu3/idle_base.txt, level_base.txt and palette.json
    python tools/art/design_zeri_hd.py --finish    # idle.txt (the base with the face drawn, FACE_ROWS) and level.txt
    python tools/art/design_zeri_hd.py --sheet DIR # the finished tables at 4x beside the pictures

The user, 2026-10-12: 「用PPU的方法重做泽丽 刀妹亚索都重做了」, then PPU 3 (「PPU 3（120 行）」) in the
picture's own proportions (「照原图比例」), then a little smaller (「然后模型缩小点 现在太大」): 111 rows, 37 game rows. The pictures (assets/source/zeri/codex_picture/zeri-model-A.png: the rifle
upright; B: the rifle level in both hands) are painted, not drawn on a grid: each is read on a grid of ROWS rows from its
bun tips to its soles (8.2 of its pixels a square), its colours brought to one k-means palette of both pictures. A square
is ink where a third of it is near black, clear where less than half of it is opaque, else its commonest colour; in the
face (FACE: small marks the face is made of - brows, lashes, the green eyes, their glints, the cheek mark, the lips)
the rarer colour wins when it covers a fifth of the square, so the features are not voted away by the skin round them.
The outline is closed (strips.complete_outline). One head in every frame: the level pose carries A's head (assets/source/
zeri/ppu3/idle.txt), so only B's body is read for it. The finished tables (idle.txt, level.txt) are touched up by hand.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy.cluster.vq import kmeans2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

PIC = os.path.join(ROOT, "assets", "source", "zeri", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "zeri", "ppu3")
ROWS = 111                                # 37 game rows at PPU 3 (「然后模型缩小点 现在太大」: 40 -> 37)
K = 32
OUTLINE = (10, 4, 17)                     # the 1x design's outline
INK_LUM, INK_SHARE = 48, 0.35
FACE = {"A": (20, 33, 17, 31)}            # rows, columns (end exclusive) of the face on A's grid
LETTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# the face drawn square by square after the picture (its features are smaller than a square apart): row -> (first
# column, letters) on A's grid: brows, lashes, the green eyes with their pupils and whites, the cheek mark, the nose's
# shade, the smile line and the lips
FACE_ROWS = {21: (19, "vr0qqqqqk0"), 22: (19, "rk00qqqq00"), 23: (19, "00qq0qq000"), 24: (19, "k0000qq000"),
             25: (19, "k0odwqq0ow"), 26: (19, "kwkkqqqkk0"), 27: (19, "kwqqqkgqu0"), 28: (19, "kqge7eqk0"),
             29: (19, "6qqkkqk0")}
# the level pose under A's head: B's head is A's one column right; A's rows above HEAD_CUT go in, the hair to the
# columns before the upright rifle (HEAD_COLS: last column above row 18, from row 18 on), then only the piece joined
# to the body stays
HEAD_CUT, HEAD_COLS, HEAD_DX = 31, (39, 34), 1


def load(which):
    a = np.asarray(Image.open(os.path.join(PIC, f"zeri-model-{which}.png")).convert("RGBA")).astype(float)
    op = a[..., 3] > 128
    ys, xs = np.nonzero(op)
    return a, op, (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)


def palette():
    rng = np.random.default_rng(1)
    px = []
    for w in "AB":
        a, op, _ = load(w)
        lum = a[..., :3] @ [0.3, 0.59, 0.11]
        p = a[op & (lum >= INK_LUM)][:, :3]
        px.append(p[rng.choice(len(p), 50000, replace=False)])
    pal, _ = kmeans2(np.concatenate(px), K, minit="++", seed=1, iter=40)
    pal = np.clip(np.round(pal), 0, 255).astype(int)
    order = np.argsort(pal @ [0.3, 0.59, 0.11])
    return [OUTLINE] + [tuple(int(v) for v in pal[i]) for i in order]


def read(which, pal):
    a, op, (top, bot, left, right) = load(which)
    step = (bot - top) / ROWS
    lum = a[..., :3] @ [0.3, 0.59, 0.11]
    ink = op & (lum < INK_LUM)
    P = np.array(pal[1:], float)
    flat = a[..., :3].reshape(-1, 3)
    idx = np.empty(len(flat), int)
    for i in range(0, len(flat), 200000):
        idx[i:i + 200000] = ((flat[i:i + 200000, None] - P[None]) ** 2).sum(-1).argmin(1)
    idx = idx.reshape(a.shape[:2]) + 1
    cols = int(np.ceil((right - left) / step))
    out = np.zeros((ROWS, cols), int) - 1          # -1 clear, 0 outline, else palette index
    face = FACE.get(which)
    skin = None
    for r in range(ROWS):
        y0, y1 = int(round(top + r * step)), int(round(top + (r + 1) * step))
        for c in range(cols):
            x0, x1 = int(round(left + c * step)), int(round(left + (c + 1) * step))
            o = op[y0:y1, x0:x1]
            if o.mean() < 0.5:
                continue
            k = ink[y0:y1, x0:x1]
            inface = face and face[0] <= r < face[1] and face[2] <= c < face[3]
            if k.sum() > (0.2 if inface else INK_SHARE) * o.sum():
                out[r, c] = 0
                continue
            counts = np.bincount(idx[y0:y1, x0:x1][o & ~k], minlength=K + 1)
            best = counts.argmax()
            if inface:
                # a feature colour (far from the commonest) covering a fifth of the square wins
                n = counts.sum()
                far = [i for i in np.argsort(-counts) if counts[i] >= 0.2 * n and
                       np.abs(np.array(pal[i]) - np.array(pal[best])).sum() > 120]
                if far:
                    best = far[0]
            out[r, c] = best
    return out


def family(c):
    """A coarse material key: hue sector for coloured squares, 'grey'/'white' for the rest."""
    r, g, b = (v / 255.0 for v in c)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 0.12:
        return "white" if mx > 0.7 else "grey"
    if mx == r:
        h = ((g - b) / (mx - mn)) % 6
    elif mx == g:
        h = (b - r) / (mx - mn) + 2
    else:
        h = (r - g) / (mx - mn) + 4
    return int(h * 60 // 30)


def soften_ink(t, pal):
    """Ink inside one material (a strand line in the hair, a fold in the coat) becomes that material's darkest shade
    in the palette: the picture's three-pixel strokes read on 8-pixel squares as black crumbs all over the hair. Ink
    between two materials, and the ring round the figure, stay ink."""
    H, W = t.shape
    out = t.copy()
    fam = [None] + [family(c) for c in pal[1:]]
    lum = [0] + [c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11 for c in pal[1:]]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if t[y, x] != 0:
                continue
            nb = t[y - 1:y + 2, x - 1:x + 2].ravel()
            if (nb < 0).any():
                continue                      # on the silhouette
            cols = [v for v in nb if v > 0]
            if len(cols) < 4 or len({fam[v] for v in cols}) != 1:
                continue
            f = fam[cols[0]]
            darkest = min((i for i in range(1, len(pal)) if fam[i] == f), key=lambda i: lum[i])
            # only darken: a family whose darkest shade is still light keeps the ink
            if lum[darkest] < 110:
                out[y, x] = darkest
    return out


def to_rgba(t, pal):
    a = np.zeros(t.shape + (4,), np.uint8)
    for v in np.unique(t):
        if v >= 0:
            a[t == v] = (*pal[v], 255)
    return a


def from_rgba(a, pal):
    inv = {tuple(p): i for i, p in enumerate(pal)}
    t = np.full(a.shape[:2], -1)
    for y, x in zip(*np.nonzero(a[..., 3])):
        t[y, x] = inv[tuple(int(v) for v in a[y, x, :3])]
    return t


def write_table(path, t):
    rows = ["".join("." if v < 0 else LETTERS[v] for v in row) for row in t]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rows) + "\n")


def read_table(path):
    rows = [r for r in open(path, encoding="utf-8").read().splitlines() if r]
    return np.array([[-1 if ch == "." else LETTERS.index(ch) for ch in r] for r in rows])


def load_palette():
    return [tuple(v) for v in json.load(open(os.path.join(OUT, "palette.json")))["colours"]]


def finish():
    from scipy import ndimage
    pal = load_palette()
    t = read_table(os.path.join(OUT, "idle_base.txt"))
    for r, (c0, letters) in FACE_ROWS.items():
        for i, ch in enumerate(letters):
            t[r, c0 + i] = -1 if ch == "." else LETTERS.index(ch)
    write_table(os.path.join(OUT, "idle.txt"), t)
    b = read_table(os.path.join(OUT, "level_base.txt"))
    b[:HEAD_CUT, :] = -1
    for r in range(HEAD_CUT):
        lim = HEAD_COLS[0] if r < 18 else HEAD_COLS[1]
        for c in range(lim + 1):
            if t[r, c] >= 0:
                b[r, c + HEAD_DX] = t[r, c]
    rgba, _, _ = G.complete_outline(to_rgba(b, pal), color=OUTLINE)
    b = from_rgba(rgba, pal)
    lab, n = ndimage.label(b >= 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(b >= 0, lab, range(1, n + 1))
        b[(lab != int(np.argmax(sizes)) + 1) & (b >= 0)] = -1
    write_table(os.path.join(OUT, "level.txt"), b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="store_true")
    ap.add_argument("--finish", action="store_true")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    if a.base:
        os.makedirs(OUT, exist_ok=True)
        pal = palette()
        json.dump({"letters": LETTERS[:len(pal)], "colours": pal}, open(os.path.join(OUT, "palette.json"), "w"), indent=0)
        for which, name in (("A", "idle_base.txt"), ("B", "level_base.txt")):
            t = soften_ink(read(which, pal), pal)
            rgba, _, _ = G.complete_outline(to_rgba(t, pal), color=OUTLINE)
            write_table(os.path.join(OUT, name), from_rgba(rgba, pal))
            print(name, t.shape)
    if a.finish:
        finish()
        print("idle.txt, level.txt")
    if a.sheet:
        pal = load_palette()
        os.makedirs(a.sheet, exist_ok=True)
        ims = []
        for name in ("idle", "level"):
            p = os.path.join(OUT, name + ".txt")
            if not os.path.exists(p):
                p = os.path.join(OUT, name + "_base.txt")
            ims.append(Image.fromarray(to_rgba(read_table(p), pal), "RGBA"))
        z = 4
        W = sum(i.width for i in ims) * z + 40
        H = max(i.height for i in ims) * z
        sheet = Image.new("RGB", (W, H), (92, 98, 86))
        x = 0
        for i in ims:
            big = i.resize((i.width * z, i.height * z), Image.NEAREST)
            sheet.paste(big, (x, H - big.height), big)
            x += big.width + 40
        sheet.save(os.path.join(a.sheet, "zeri_hd_design.png"))


if __name__ == "__main__":
    main()
