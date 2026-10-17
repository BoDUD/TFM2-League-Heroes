#!/usr/bin/env python3
"""Kennen's action strips, posed from the approved design (picture B's pose: the shuriken raised beside his head).

    python tools/art/rig_kennen.py [--review DIR]

The design (assets/source/native/kennen_native.png, tools/art/design_kennen.py) is the A37 head and slim robe
(codex_arm/base_unchanged_1x.png, "the base") with Codex's raised arm and shuriken on it (codex_arm/arm_only_B_1x.png,
"the arm"). Codex's earlier A-pose strips no longer fit (the shuriken was on his back), so every frame is made here from
those parts - the user's notes on the A strips kept: runs step across (「凯南走路没有交叉步」), the death turns the
whole figure (「死亡后模型缺失右半身」), no arm is drawn here (「手臂突然伸的很长」, four arms of mine were 「奇怪」):
  idle    the design six times (import_native's BOB breathes it);
  run     the design's upper body (head, raised arm, shuriken, robe, near claw: one block) a row up while a foot swings
          through, over two 2-square shins from hips under the robe to the design's own shoes; the near shoe (drawn in
          front, its shin's outline over the far leg) steps from ahead of the far one to behind it and back;
  skill2  E's dash: the same block crouched 2-3 rows over a long stride that swaps (the lightning ball is an effect);
  w       W's surge: a crouch (1, 2 rows), then up a row as the lightning bursts (frames 3-4), the design;
  ult     R: a crouch, a leap (3 and 4 rows up, the shoes tucked a row), the landing crouch, the design;
  hit     the design a column back and a row down, then the design;
  dead    the hit's recoil, the design turned back 30 degrees, then the base (no raised arm - it falls behind him) turned
          60 degrees in the air and 90 on his back (a row over the ground, then on it), the shuriken flying off and
          lying on the ground by his head;
  attack, skill (Q): the throw - Codex's four arm poses on the base (codex_throw/throw_arm_<k>_1x.png: wind-up,
          swing, release, follow-through; THROW_PROMPT.md) between two design frames; until they are there, the design.
          Codex's release and follow-through arms reached 13-15 squares past the body, as far as he is wide (League's
          claw reaches 4-6): 「凯南平A时手的长度有点怪啊」 - SHORTEN deletes sleeve columns there (the hand and the
          shuriken move in), the user's pick B of 4 / 6 / 8 squares.
Writes assets/source/native/kennen_<tag>.png (8x) and kennen_cells.json; then tools/art/import_native.py --hero kennen.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rig_nocturne import rotsprite  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kennen")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "kennen_native.png")
BASE = os.path.join(SRC, "codex_arm", "base_unchanged_1x.png")
ARM = os.path.join(SRC, "codex_arm", "arm_only_B_1x.png")
THROW = os.path.join(SRC, "codex_throw", "throw_arm_{}_1x.png")
Z = 8
CELL = (80, 72)                 # width, height
CPIV = (40, 48)                 # the standing point in every cell
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas
SOLES = 11                      # the soles' row under the pivot
OUTLINE = (0x0B, 0x06, 0x0E)
GOLD = {(0xF8, 0xA2, 0x3B), (0xFE, 0xDC, 0x80), (0xCB, 0x74, 0x20), (0x7A, 0x3E, 0x1C)}
MS = {"idle": [180] * 6, "run": [100] * 8, "attack": [60, 60, 60, 70, 70, 80], "skill": [50, 60, 70, 80, 90, 100],
      "skill2": [75] * 4, "w": [50, 50, 60, 60, 60], "ult": [60, 60, 60, 70, 70, 80], "hit": [100, 100],
      "dead": [100, 100, 110, 110, 120, 150, 300, 500]}
TAGS = list(MS)
SHORTEN = {3: (77, 6), 4: (76, 4)}   # throw arm k: (first canvas column, columns) deleted from the sleeve

UPPER = (60, 95)                # the design's rows above the shoes: the shuriken's tip to the robe's hem
NEAR_SHOE = (96, 99, 56, 60)    # rows, columns of the design's shoes (the near one narrowed by the slim robe)
FAR_SHOE = (96, 99, 66, 73)
LEG_STUB = [(94, 58), (95, 58), (95, 59)]   # the near shin showing under the robe's back
HIPS = {"near": (60, 91), "far": (66, 91)}  # design squares under the robe the shins hang from
STAND = (-6, 6)                 # the shoes' middles in the design, columns from the pivot (near, far)
# legs per frame: (body rows down, near shoe middle, far shoe middle, near lift, far lift)
RUN = [(0, 4, -4, 0, 0), (-1, 3, -3, 0, 1), (-1, -1, 1, 0, 2), (0, -5, 5, 0, 1),
       (0, -6, 6, 0, 0), (-1, -5, 5, 1, 0), (-1, -1, 1, 2, 0), (0, 3, -3, 1, 0)]
DASH = [(2, 5, -5, 0, 0), (3, 1, -1, 1, 0), (2, -5, 5, 0, 0), (3, -1, 1, 0, 1)]
W = [(1, -6, 6, 0, 0), (2, -6, 6, 0, 0), (-1, -6, 6, 0, 0), (-1, -6, 6, 0, 0), None]
ULT = [(2, -6, 6, 0, 0), (-3, -5, 5, 4, 4), (-4, -5, 5, 5, 5), (2, -6, 6, 0, 0), (1, -6, 6, 0, 0), None]
# the death: (degrees counter-clockwise, rows over the ground, the figure's middle in columns from the pivot, figure)
DEAD = {1: (30, 2, -3, "full"), 2: (60, 4, -5, "base"), 3: (90, 1, -6, "base"), 4: (90, 0, -6, "base"),
        5: (90, 0, -6, "base"), 6: (90, 0, -6, "base"), 7: (90, 0, -6, "base")}
# the shuriken in the death: its middle (from the pivot) and its turn per frame (2-7)
STAR_PATH = {2: ((-8, -30), 45), 3: ((-22, -6), 90), 4: ((-25, 5), 0), 5: ((-25, 5), 0), 6: ((-25, 5), 0),
             7: ((-25, 5), 0)}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def read1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    if a.shape[0] != 128:
        a = a[Z // 2::Z, Z // 2::Z]
    a = a.copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def paste(dst, src, x, y, under=False):
    """src's opaque squares onto dst with src's top-left at (x, y); under: only where dst is clear."""
    h, w = src.shape[:2]
    for yy, xx in zip(*np.nonzero(src[..., 3])):
        ty, tx = y + yy, x + xx
        if 0 <= ty < dst.shape[0] and 0 <= tx < dst.shape[1]:
            if under and dst[ty, tx, 3]:
                continue
            dst[ty, tx] = src[yy, xx]


def cell():
    return np.zeros((CELL[1], CELL[0], 4), np.uint8)


def whole(src, dx=0, dy=0):
    """A 128-canvas figure in a cell, its pivot on the cell's, moved dx, dy."""
    f = cell()
    paste(f, src, CPIV[0] - PIVOT[0] + dx, CPIV[1] - PIVOT[1] + dy)
    return f


def shoe(des, leg):
    if leg == "near":
        r0, r1, c0, c1 = NEAR_SHOE
        return des[r0:r1 + 1, c0:c1 + 1].copy()
    r0, r1, c0, c1 = FAR_SHOE
    s = des[r0:r1 + 1, c0:c1 + 1].copy()
    s[0, 0] = 0                 # the robe's hem outline, not the shoe's
    return s


def legs_frame(des, spec):
    """The design's upper body `dy` rows down over two legs: each a 2-square shin from its hip to the top of its shoe at
    its step (lit edge left, the shoes' violets); the near leg (shoe, shin, the shin's outline) laid over the far one."""
    dy, near_mid, far_mid, near_lift, far_lift = spec
    f = cell()
    ox, oy = CPIV[0] - PIVOT[0], CPIV[1] - PIVOT[1]
    lit, dark = des[97, 58, :3], des[98, 57, :3]
    far = set()
    for leg, mid, lift in (("far", far_mid, far_lift), ("near", near_mid, near_lift)):
        s = shoe(des, leg)
        h, w = s.shape[:2]
        top, left = 96 - lift + oy, PIVOT[0] + mid - w // 2 + ox
        mine = set()
        for yy, xx in zip(*np.nonzero(s[..., 3])):
            f[top + yy, left + xx] = s[yy, xx]
            mine.add((top + yy, left + xx))
        hx, hy = HIPS[leg][0] + ox, HIPS[leg][1] + oy + dy
        ax = left + (w - 1) / 2
        band = set()
        for y in range(hy, top + 1):
            c = int(round(hx + (ax - hx) * (y - hy) / max(top - hy, 1)))
            band |= {(y, c - 1), (y, c)}
        for y, x in band:
            f[y, x, :3], f[y, x, 3] = (lit if (y, x - 1) not in band else dark), 255
        mine |= band
        for y, x in {(y + a, x + b) for y, x in band for a in (-1, 0, 1) for b in (-1, 0, 1)} - mine:
            if 0 <= y < CELL[1] and 0 <= x < CELL[0] and (not f[y, x, 3] or (y, x) in far):
                f[y, x, :3], f[y, x, 3] = OUTLINE, 255
        far = mine
    up = des[UPPER[0]:UPPER[1] + 1].copy()
    for y, x in LEG_STUB:
        up[y - UPPER[0], x] = 0
    paste(f, up, ox, UPPER[0] + oy + dy)
    return f


def star_of(arm):
    """The shuriken in the arm layer: its gold squares and the outline squares touching them, cropped."""
    gold = np.array([[tuple(p[:3]) in GOLD and p[3] > 0 for p in row] for row in arm])
    near = np.zeros_like(gold)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= np.roll(np.roll(gold, dy, 0), dx, 1)
    outl = np.all(arm[..., :3] == OUTLINE, -1) & (arm[..., 3] > 0)
    m = gold | (outl & near)
    ys, xs = np.nonzero(m)
    s = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    for y, x in zip(ys, xs):
        s[y - ys.min(), x - xs.min()] = arm[y, x]
    return s


def crop(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def turned(fig, deg):
    t = np.rot90(fig, 1).copy() if deg == 90 else rotsprite(fig, (fig.shape[1] // 2, fig.shape[0] - 1), deg)[0]
    return crop(t)


def dead_frames(full, base, star):
    frs = [hit_frame(full)]
    for k in range(1, 8):
        deg, lift, mid, which = DEAD[k]
        fig = crop(full[60:100] if which == "full" else base[60:100])
        t = turned(fig, deg)
        f = cell()
        if k in STAR_PATH:
            (sx, sy), turn = STAR_PATH[k]
            st = star if turn == 0 else (np.rot90(star, turn // 90).copy() if turn % 90 == 0 else
                                         crop(rotsprite(star, (star.shape[1] // 2, star.shape[0] // 2), turn)[0]))
            paste(f, st, CPIV[0] + sx - st.shape[1] // 2, CPIV[1] + sy - st.shape[0] // 2)
        left = CPIV[0] + mid - t.shape[1] // 2
        paste(f, t, left, CPIV[1] + SOLES - lift - t.shape[0] + 1)
        frs.append(f)
    return frs


def hit_frame(full):
    return whole_recoil(full)


def whole_recoil(full):
    """The design a column back and a row down, the shoes kept on the ground (the hem over their tops)."""
    f = cell()
    ox, oy = CPIV[0] - PIVOT[0], CPIV[1] - PIVOT[1]
    for leg in ("far", "near"):
        r0, r1, c0, c1 = NEAR_SHOE if leg == "near" else FAR_SHOE
        paste(f, shoe(full, leg), c0 + ox, r0 + oy)
    paste(f, full[UPPER[0]:UPPER[1] + 1], ox - 1, UPPER[0] + oy + 1)
    return f


def throw_frames(full, base, order):
    """The design, Codex's throw arms on the base in `order` (1-4), the design."""
    frs = [whole(full)]
    for k in order:
        p = THROW.format(k)
        if os.path.exists(lp(p)):
            arm = read1x(p)
            if k in SHORTEN:
                c0, n = SHORTEN[k]
                short = np.zeros_like(arm)
                short[:, :c0] = arm[:, :c0]
                short[:, c0:arm.shape[1] - n] = arm[:, c0 + n:]
                arm = short
            fig = base.copy()
            m = arm[..., 3] > 0
            fig[m] = arm[m]
            frs.append(whole(fig))
        else:
            frs.append(whole(full))
    frs.append(whole(full))
    return frs


def build():
    full, base, arm = read1x(DESIGN), read1x(BASE), read1x(ARM)
    star = star_of(arm)
    out = {
        "idle": [whole(full) for _ in range(6)],
        "run": [legs_frame(full, s) for s in RUN],
        "attack": throw_frames(full, base, [1, 2, 3, 4]),
        "skill": throw_frames(full, base, [1, 2, 3, 4]),
        "skill2": [legs_frame(full, s) for s in DASH],
        "w": [legs_frame(full, s) if s else whole(full) for s in W],
        "ult": [legs_frame(full, s) if s else whole(full) for s in ULT],
        "hit": [whole_recoil(full), whole(full)],
        "dead": dead_frames(full, base, star),
    }
    for tag, frs in out.items():
        assert len(frs) == len(MS[tag]), (tag, len(frs))
    cells = {"cell": list(CELL), "tags": {t: [{"pivot": list(CPIV), "ms": ms} for ms in MS[t]] for t in TAGS}}
    return out, cells


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def join(frames):
    cols, rows = layout(len(frames))
    cw, ch = CELL
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frames):
        out[(i // cols) * ch:(i // cols) * ch + ch, (i % cols) * cw:(i % cols) * cw + cw] = f
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a 4x review sheet of every strip into this folder")
    a = ap.parse_args()
    out, cells = build()
    for tag, frs in out.items():
        strip = join(frs)
        Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1)).save(lp(os.path.join(NATIVE, f"kennen_{tag}.png")))
    with open(lp(os.path.join(NATIVE, "kennen_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    print("written", ", ".join(f"{t} {len(v)}" for t, v in out.items()))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        rows = [np.concatenate([f[14:64] for f in frs], axis=1) for frs in out.values()]
        W = max(r.shape[1] for r in rows)
        sheet = np.zeros((sum(r.shape[0] for r in rows), W, 4), np.uint8)
        y = 0
        for r in rows:
            sheet[y:y + r.shape[0], :r.shape[1]] = r
            y += r.shape[0]
        im = Image.fromarray(sheet).resize((W * 4, sheet.shape[0] * 4), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (104, 112, 72, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.review, "kennen_rig.png"))


if __name__ == "__main__":
    main()
