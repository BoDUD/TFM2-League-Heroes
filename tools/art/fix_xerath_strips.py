#!/usr/bin/env python3
"""Xerath's action strips: Codex's step-2 delivery (assets/source/xerath/codex_strips/) with the body moving.

    python tools/art/fix_xerath_strips.py [--check]

Codex re-posed the design's own parts (its HANDOFF: the arms cut out and turned by quarter turns, the body, pauldrons,
chains, seal and legs square for square the design's) - the casting body is the idle's, as the user's rule asks. But
the body never moves: every cast stands bolt upright, which the user called 「僵硬」 on Tryndamere and Sivir. As
tools/art/rig_tryndamere.py's accepted casts, the upper body leans over the hips here: each row from HIP_ROW up moves
round((HIP_ROW - row) x lean) columns (+ forward, to the image right), the hood moving whole with its chin row (never
sheared: the triangle eyes would go diagonal), the legs below HIP_ROW as drawn. LEAN gives each frame's lean: back
while he draws a throw or charges, forward into the release, a little forward in the channel; at most 0.12 (2 columns
at the chin: 「倾斜不要太大」).
The death's heap (frames 6-8) also had loose black dashes of 1-4 squares beside it, read as stray outline: pieces of at
most SPECK squares that are all outline go (DEAD_SPECKS).
The casts posed again from the design (2026-10-06, the user: 「泽拉斯 平A 放技能的时候模型有点变形」): wherever
Codex "raised" a claw it turned the claw up behind the pauldron and the hood, so only 14-20 of its 40 / 58 squares
showed - a hand gone, a shoulder with a blue stub - and the lean of up to 0.12 (two columns at the chin) bent the thin
body. POSES rebuilds every standing action (attack, Q, quick Q, E -> W, R, its loop and shot, hit) from the design:
the body square for square where Codex stood it (its step bx and hop dy, found by matching the hood), each claw
(NEAR / FAR: the floating hands, cut whole from the design) turned by exact quarter turns as Codex had it where Codex's
claw showed (pointing forward on a throw, hanging, flung out when hit - the baked flashes sit on those), and a hidden
claw replaced by UP: the claw lifted 5 rows and 2 columns out, unturned, beside the body. The lean is halved (at
most a column). The run and the death stay Codex's.
Reads codex_strips/xerath_<tag>.png (8x) and xerath_cells.json, writes assets/source/native/xerath_<tag>.png (8x) for
tools/art/import_native.py. --check compares instead of writing.
"""
import argparse
import json
import math
import os
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "xerath", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
# rows under / over the frame's pivot (the design's canvas: pivot row 88, the hood's chin row 68, the torso's lowest
# row 85 - under it the two legs)
HIP_DY, NECK_DY = -3, -20
SPECK = 4
LEAN = {   # at most 0.06: a column at the chin (0.12 bent him: 「平A 放技能的时候模型有点变形」)
    "attack": [-0.04, -0.04, 0.0, 0.06, 0.05, 0.02],
    "skill": [-0.03, -0.04, -0.04, -0.04, -0.04, 0.06, 0.02],
    "skill_quick": [-0.03, -0.04, -0.04, 0.06, 0.02],
    "skill2": [-0.03, -0.04, 0.06, 0.05, -0.03, 0.0],
    "ult": [0.0, -0.03, -0.04, -0.03, 0.02],
    "ult_loop": [0.02] * 6,
    "ult_shot": [0.06, 0.04, 0.02],
    "hit": [-0.05, -0.02],
    "run": [0.06] * 8,
}
DESIGN = os.path.join(OUT, "xerath_native.png")
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99)
# the floating hands on the design canvas (rows, columns; the near one image-right) and where each hangs from
NEAR = (range(76, 86), range(73, 79))
FAR = (range(75, 86), range(48, 56))
NEAR_J, FAR_J = (75.5, 76.0), (52.0, 75.0)
UP = {"near": (0, 2, -5), "far": (0, -2, -5)}   # a raised claw: (quarter turns, columns out, rows up) - option E
# per frame: (body step bx, hop dy, near claw, far claw) - a claw (quarter turns clockwise, dx, dy from its place) as
# Codex posed it (found by matching the claw in Codex's frames: 34-58 of its squares showing), or "UP" where Codex's
# claw was hidden (14-25 squares)
POSES = {
    "attack": [(-1, 0, 'UP', (0, 0, 0)), (-2, 0, 'UP', (0, 0, 0)), (0, 0, 'UP', (0, 0, 0)), (1, 0, (3, 0, -1), (0, 0, 0)), (1, 0, (3, 0, -1), (0, 0, 0)), (0, 0, (0, 0, 0), (0, 0, 0))],
    "skill": [(-1, 0, 'UP', 'UP'), (-1, 0, 'UP', 'UP'), (-1, 0, 'UP', 'UP'), (0, 0, 'UP', 'UP'), (-1, 0, 'UP', 'UP'), (2, 0, (3, 0, -1), (0, 0, 0)), (0, 0, (0, 0, 0), (0, 0, 0))],
    "skill_quick": [(-1, 0, 'UP', 'UP'), (-1, 0, 'UP', 'UP'), (-1, 0, 'UP', 'UP'), (2, 0, (3, 0, -1), (0, 0, 0)), (0, 0, (0, 0, 0), (0, 0, 0))],
    "skill2": [(-1, 0, 'UP', (0, 0, 0)), (-2, 0, 'UP', (0, 0, 0)), (2, 0, (3, 0, -1), (0, 0, 0)), (1, 0, (3, 0, -1), (0, 0, 0)), (0, 0, 'UP', 'UP'), (0, 0, (0, 0, 0), (0, 0, 0))],
    "ult": [(0, 0, 'UP', 'UP'), (0, -1, 'UP', 'UP'), (0, -1, 'UP', 'UP'), (0, -1, 'UP', 'UP'), (0, 0, (3, 0, -1), 'UP')],
    "ult_loop": [(0, 0, (3, 0, -1), 'UP'), (0, -1, (3, 0, -1), 'UP'), (0, -1, (3, 0, -1), 'UP'), (0, 0, (3, 0, -1), 'UP'), (0, 0, (3, 0, -1), 'UP'), (0, 0, (3, 0, -1), 'UP')],
    "ult_shot": [(1, 0, (3, 0, -1), 'UP'), (1, 0, (3, 0, -1), 'UP'), (0, 0, (3, 0, -1), 'UP')],
    "hit": [(-2, 0, (3, 0, -1), (1, 2, -1)), (0, 0, (0, 0, 0), (0, 0, 0))],
}
DEAD_SPECKS = [5, 6, 7]          # 0-based frames of the death


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def shift_of(dy, lean):
    """Columns a row (dy rows from the pivot) moves for a lean: 0 from the hips down, the hood as its chin row."""
    if not lean or dy >= HIP_DY:
        return 0
    v = (HIP_DY - max(dy, NECK_DY)) * lean
    return int(math.floor(abs(v) + 0.5)) * (1 if v > 0 else -1)


def lean_cell(c, pivot_y, lean):
    out = np.zeros_like(c)
    for y in range(c.shape[0]):
        d = shift_of(y - pivot_y, lean)
        if d > 0:
            out[y, d:] = c[y, :-d]
        elif d < 0:
            out[y, :d] = c[y, -d:]
        else:
            out[y] = c[y]
    return out


def drop_specks(c):
    """Pieces of at most SPECK squares that are all outline (luminance < 40) go."""
    op = c[..., 3] > 0
    lum = (c[..., :3].astype(int) * [299, 587, 114]).sum(-1) / 1000
    seen = np.zeros(op.shape, bool)
    H, W = op.shape
    gone = 0
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        q, pts = deque([(y, x)]), []
        seen[y, x] = True
        while q:
            a, b = q.popleft()
            pts.append((a, b))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    u, v = a + dy, b + dx
                    if 0 <= u < H and 0 <= v < W and op[u, v] and not seen[u, v]:
                        seen[u, v] = True
                        q.append((u, v))
        if len(pts) <= SPECK and all(lum[a, b] < 40 for a, b in pts):
            for a, b in pts:
                c[a, b] = 0
            gone += len(pts)
    return gone


def design_parts():
    """The design (128 x 128, a square a pixel), its body without the claws and the two claws as parts."""
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA")).copy()     # 128 x 128, a square a pixel
    if d.shape[0] != 128:
        d = d[Z // 2::Z, Z // 2::Z].copy()
    parts = {}
    body = d.copy()
    for name, (rows, cols), j in (("near", NEAR, NEAR_J), ("far", FAR, FAR_J)):
        m = np.zeros(d.shape[:2], bool)
        m[rows.start:rows.stop, cols.start:cols.stop] = True
        m &= d[..., 3] > 0
        if name == "far":                 # the pauldron's last purple square on row 75 stays on the body
            m &= ~((d[..., :3] == (0x4D, 0x1E, 0x62)).all(-1))
        ys, xs = np.nonzero(m)
        y0, x0 = ys.min(), xs.min()
        sp = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
        sp[ys - y0, xs - x0] = d[ys, xs]
        parts[name] = (sp, (j[0] - x0, j[1] - y0))
        body[m] = 0
    return body, parts


def rot90(sp, j, k):
    """Quarter turns clockwise about the joint (pixel centres at + 0.5): lossless."""
    jx, jy = j
    for _ in range(k % 4):
        H = sp.shape[0]
        sp = np.rot90(sp, -1)
        jx, jy = H - jy, jx
    return sp.copy(), (jx, jy)


def put(dst, sp, at, j, under=False):
    ox, oy = int(math.floor(at[0] - j[0] + 1e-9)), int(math.floor(at[1] - j[1] + 1e-9))
    ys, xs = np.nonzero(sp[..., 3])
    cy, cx = ys + oy, xs + ox
    ok = (cy >= 0) & (cy < dst.shape[0]) & (cx >= 0) & (cx < dst.shape[1])
    ys, xs, cy, cx = ys[ok], xs[ok], cy[ok], cx[ok]
    if under:
        free = dst[cy, cx, 3] == 0
        ys, xs, cy, cx = ys[free], xs[free], cy[free], cx[free]
    dst[cy, cx] = sp[ys, xs]


def posed(body, parts, pose, lean):
    """One standing frame on the design canvas: the body, the claws, the lean, then the step and hop."""
    bx, dy, near, far = pose
    c = body.copy()
    for name, p, base in (("far", far, FAR_J), ("near", near, NEAR_J)):
        k, ox, oy = UP[name] if p == "UP" else p
        sp, j = rot90(*parts[name], k)
        # the far claw behind the body unless it is raised beside it; the near one in front
        put(c, sp, (base[0] + ox, base[1] + oy), j, under=(name == "far" and p != "UP"))
    if lean:
        c = lean_cell(c, PIVOT[1], lean)
    out = np.zeros_like(c)
    H, W = c.shape[:2]
    out[max(0, dy):H + min(0, dy), max(0, bx):W + min(0, bx)] = c[max(0, -dy):H - max(0, dy), max(0, -bx):W - max(0, bx)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    cells = json.load(open(lp(os.path.join(SRC, "xerath_cells.json")), encoding="utf-8"))
    body, parts = design_parts()
    cw, ch = cells["cell"]
    for tag, frs in cells["tags"].items():
        big = np.asarray(Image.open(lp(os.path.join(SRC, f"xerath_{tag}.png"))).convert("RGBA"))
        one = big[Z // 2::Z, Z // 2::Z].copy()
        cols, _ = layout(len(frs))
        notes = []
        for i, fr in enumerate(frs):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c = one[y0:y0 + ch, x0:x0 + cw]
            lean = LEAN.get(tag, [0] * len(frs))[i]
            if tag in POSES:
                # the design posed, its pivot on the cell's: canvas (x, y) -> cell (x + px - 64, y + py - 88)
                f = posed(body, parts, POSES[tag][i], lean)
                px, py = fr["pivot"]
                c[:] = 0
                ox, oy = px - PIVOT[0], py - PIVOT[1]          # cell = canvas moved by (ox, oy)
                ys, xs = np.nonzero(f[..., 3])
                cy, cx = ys + oy, xs + ox
                ok = (cy >= 0) & (cy < ch) & (cx >= 0) & (cx < cw)
                c[cy[ok], cx[ok]] = f[ys[ok], xs[ok]]
                continue
            if lean:
                c[:] = lean_cell(c.copy(), fr["pivot"][1], lean)
            if tag == "dead" and i in DEAD_SPECKS:
                notes.append(f"frame {i + 1}: -{drop_specks(c)} speck squares")
        res = np.repeat(np.repeat(one, Z, 0), Z, 1)
        path = os.path.join(OUT, f"xerath_{tag}.png")
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            print(tag, "identical" if np.array_equal(old, res) else "DIFFERENT")
        else:
            Image.fromarray(res).save(lp(path))
            print(tag, LEAN.get(tag, "-"), "; ".join(notes))


if __name__ == "__main__":
    main()
