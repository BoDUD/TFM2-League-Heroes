#!/usr/bin/env python3
"""Tristana's death, frames 5-8: the whole body turned with the head (the user: "死亡后头和身体分离了看起来").

    python tools/art/fix_tristana_dead.py <Codex's delivery folder>   (holds native/tristana_dead_1x.png, tristana_hit_1x.png)

Codex turned the pasted design head a quarter in frames 5-8 of the death but drew the body under it thin and small (a
leg or an arm), so the head seemed to lie there alone. Frame 3 is a whole body in the air under the upright design head;
here it gets the closed eyes of the hit's first frame (the same head, eyes shut), is turned as a whole - 45 degrees in
frame 5 (falling back), 90 in frames 6-8 (lying on her back, face up) - and put down: frame 5 in the air, frame 6 two rows
over the ground, frames 7-8 on it. The cannon lying on the ground stays where Codex drew it. Writes
assets/source/native/tristana_dead.png (8x); frames 1-4 are Codex's, unchanged.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "native")
CELL = 96
COLS = 4
SOLES = 11          # the soles' row under the pivot
EYES = (18, 12, 28, 17)   # the eyes' box in the design head (x0, y0, x1, y1 exclusive, head-local): lashes to amber


def lp(p):
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\?\\") else p


def cell(a, k, cols=COLS):
    return a[(k // cols) * CELL:(k // cols + 1) * CELL, (k % cols) * CELL:(k % cols + 1) * CELL]


def pieces(m):
    """8-connected components of a mask: list of boolean masks, biggest first."""
    lab = np.zeros(m.shape, int)
    out = []
    n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
        out.append(lab == n)
    return sorted(out, key=lambda p: -p.sum())


def find_head(c, head, hm):
    best = (0, 0, 0)
    for y in range(0, CELL - head.shape[0]):
        for x in range(0, CELL - head.shape[1]):
            s = (np.all(c[y:y + head.shape[0], x:x + head.shape[1]] == head, -1) & hm).sum()
            if s > best[0]:
                best = (s, x, y)
    return best


def rotate(fig, deg):
    """Turn an RGBA figure (nearest neighbour); 90 is exact."""
    if deg == 90:
        return np.rot90(fig, 1).copy()           # counter-clockwise: the head goes left, the face looks up
    im = Image.fromarray(fig).rotate(deg, resample=Image.NEAREST, expand=True)
    return np.asarray(im).copy()


def main():
    delivery = sys.argv[1]
    cells = json.load(open(os.path.join(SRC, "tristana_cells.json"), encoding="utf-8"))
    dead = np.asarray(Image.open(os.path.join(delivery, "native", "tristana_dead_1x.png")).convert("RGBA")).copy()
    hit = np.asarray(Image.open(os.path.join(delivery, "native", "tristana_hit_1x.png")).convert("RGBA"))
    design = np.asarray(Image.open(os.path.join(delivery, "approved_design", "tristana_head_1x.png")).convert("RGBA"))
    ys, xs = np.nonzero(design[..., 3])
    head = design[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hm = head[..., 3] > 0

    # frame 3's whole body (without the cannon on the ground) with the hit's shut eyes
    c3 = cell(dead, 2)
    parts = pieces(c3[..., 3] > 0)
    s3, hx, hy = find_head(c3, head, hm)
    body = [p for p in parts if p[hy:hy + head.shape[0], hx:hx + head.shape[1]].any()][0]
    fig = np.where(body[..., None], c3, 0).astype(np.uint8)
    h1 = cell(hit, 0, cols=2)
    s1, gx, gy = find_head(h1, head, hm)
    x0, y0, x1, y1 = EYES
    fig[hy + y0:hy + y1, hx + x0:hx + x1] = h1[gy + y0:gy + y1, gx + x0:gx + x1]
    fy, fx = np.nonzero(fig[..., 3])
    fig = fig[fy.min():fy.max() + 1, fx.min():fx.max() + 1]
    print(f"frame 3 body {fig.shape[1]}x{fig.shape[0]}, head match {s3}/{hm.sum()}, hit head {s1}/{hm.sum()}")

    ground = cell(dead, 4).copy()               # frame 5: its cannon on the ground (the same in frames 2-8)
    gparts = pieces(ground[..., 3] > 0)
    cannon = max(gparts, key=lambda p: np.nonzero(p)[0].mean())    # the lowest piece is the cannon
    # (turn, lift over the soles row, shift right from the pivot)
    plan = {4: (45, 9, 10), 5: (90, 2, 16), 6: (90, 0, 16), 7: (90, 0, 16)}
    for k, (deg, lift, dx) in plan.items():
        fr = cells["tags"]["dead"][k]
        px, py = fr["pivot"]
        out = np.where(cannon[..., None], cell(dead, k), 0).astype(np.uint8)
        f = rotate(fig, deg)
        fy, fx = np.nonzero(f[..., 3] > 0)
        f = f[fy.min():fy.max() + 1, fx.min():fx.max() + 1]
        bottom = py + SOLES - lift
        top = bottom - f.shape[0] + 1
        left = px + dx - f.shape[1] // 2
        reg = out[top:top + f.shape[0], left:left + f.shape[1]]
        m = f[..., 3] > 0
        reg[m] = f[m]
        r, c = divmod(k, COLS)
        dead[r * CELL:(r + 1) * CELL, c * CELL:(c + 1) * CELL] = out
        print(f"frame {k + 1}: turned {deg}, {f.shape[1]}x{f.shape[0]}, bottom row {bottom} (soles {py + SOLES})")
    big = np.repeat(np.repeat(dead, 8, 0), 8, 1)
    Image.fromarray(big).save(lp(os.path.join(SRC, "tristana_dead.png")))
    print("wrote", os.path.join(SRC, "tristana_dead.png"))


if __name__ == "__main__":
    main()
