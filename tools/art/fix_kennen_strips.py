#!/usr/bin/env python3
"""Kennen's action strips: Codex's step-2 delivery made clean (the user: "动作包有奇怪的地方请你调整 codex太笨了").

    python tools/art/fix_kennen_strips.py [--check] [--review DIR]

Codex drew the eight strips from the approved 37-row design (assets/source/kennen/MODEL_STRIPS.md) and pasted the
design's head into every frame (assets/source/kennen/codex_strips/, as delivered: 8x, its HANDOFF, manifest and checks).
Its checks passed (blocks, palette, alpha, feet line, the head square for square); what they did not see is fixed here:
1. The run (8 frames) drew the robe in the gloves' dark plum and the legs as one dark lump that hardly moved (its own
   HANDOFF: "移动腿部交换的幅度偏小"): rebuilt from the design - the idle's whole upper body (the shuriken, the head,
   the robe and the claws: one block, so nothing comes apart) up a row while a foot swings through, over two legs: a
   2-square shin (lit edge left, the shoes' violets) from a hip under the robe to each of the design's own shoes. The
   lead foot changes every half cycle (the user: "凯南走路没有交叉步" - the first rebuild only slid the shoes apart and
   together, the near one always behind): the near shoe, drawn in front with its shin's outline over the far leg, steps
   ahead of the far one and then falls behind it; the swinging shoe is lifted 1-2 rows.
2. E's dash (4 frames) was smeared into one-square streaks: the same design block crouched 2-3 rows over a long stride
   (the shoes swapping); the ball of lightning round him is an effect (step 3).
3. R's leap (frames 2-3) had stick legs under a dark column and the shuriken balanced on the hood: the design leaps
   (3 and 4 rows up, the shoes tucked a row), the shuriken staying on his back.
4. The attack's frames 2-3 held the shuriken with no arm (it floated beside and over the hood): frame 2 is frame 1 again
   (the hand reaching back to the shuriken still on his back - an arm drawn there would be hidden by the hood). Frame
   3 is Codex's: the star raised on top of the hood, its lower point on the hood, the hand hidden behind it - as
   League's frame 3. (An arm drawn from the near shoulder up to it was 17 squares long, a thin stick: the user, "中间有
   一帧手臂突然伸的很长 有点诡异".)
5. One-square strays: the brown tips over Q's shuriken (frames 1-2), the gold strand and the violet blob over the hood
   in W's crouch (frames 3-4), two gold squares beside the attack's frame 1.
6. The death's frames 3-8 turned the pasted head a quarter but drew the body under it in the gloves' darkest plum, so
   he seemed to lie there as half a figure (the user: "死亡后模型缺失右半身"): the design's whole figure is turned as one,
   as Tristana's death - 60 degrees in frame 3 (falling back, in the air, the shuriken still on his back as in frames
   1-2), 90 from frame 4 (on his back, face up; frame 4 two rows over the ground, then on it). The shuriken slips off
   his back: Codex's star lying on the ground (its frames 5-8) peeks out from under his head. Frames 1-2 are Codex's.
Writes assets/source/native/kennen_<tag>.png (8x) and kennen_cells.json (the pack's); then run
tools/art/import_native.py --hero kennen. --check compares with the files instead of writing them.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rig_nocturne import rotsprite  # noqa: E402
SRC = os.path.join(ROOT, "assets", "source", "kennen", "codex_strips")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "kennen_native.png")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["idle", "run", "attack", "skill", "skill2", "w", "ult", "hit", "dead"]
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas
UPPER = (63, 95)                # the design's rows above the shoes: the shuriken's tip to the robe's hem
NEAR_SHOE = (96, 99, 54, 60)    # rows, columns of the design's shoes
FAR_SHOE = (96, 99, 65, 73)
C = {"#": (0x0B, 0x06, 0x0E)}    # the design's outline

# the run: a two-step cycle (8 x 100 ms) - body rows down (up a row while a foot swings through), the shoes' middles
# in columns from the pivot (the near one ahead of the far one in frames 1-2 and 8, behind it in frames 4-6) and their
# lifts in rows (the swinging one)
RUN_DY = [0, -1, -1, 0, 0, -1, -1, 0]
RUN_NEAR = [4, 3, -1, -5, -6, -5, -1, 3]
RUN_FAR = [-4, -3, 1, 5, 6, 5, 1, -3]
RUN_NEAR_LIFT = [0, 0, 0, 0, 0, 1, 2, 1]
RUN_FAR_LIFT = [0, 1, 2, 1, 0, 0, 0, 0]
HIPS = {"near": (60, 91), "far": (66, 91)}     # design squares under the robe the shins hang from
LEG_STUB = [(94, 56), (94, 57), (95, 56), (95, 57), (95, 58), (95, 59)]   # the idle's near shin under the robe's back
# E's dash (4 x 75 ms): crouched 2-3 rows, a long stride that swaps
DASH_DY = [2, 3, 2, 3]
DASH_NEAR = [-4, -1, 4, 1]
DASH_FAR = [4, 1, -4, -1]
DASH_NEAR_LIFT = [0, 1, 0, 0]
DASH_FAR_LIFT = [0, 0, 0, 1]
# R's leap, frames 2 and 3 (0-based 1, 2): rows up, the shoes a row more
LEAP = {1: 3, 2: 4}
COPY = {("attack", 1): 0}       # (tag, frame) -> the frame whose pixels it takes
# strays: (tag, 0-based frame) -> cell (y, x) squares cleared
STRAYS = {("skill", 0): [(21, 38)],
          ("skill", 1): [(21, 36), (22, 39)],
          ("w", 2): [(32, 36), (33, 37), (33, 38), (34, 38), (34, 39), (35, 39)],
          ("w", 3): [(32, 41), (32, 42), (32, 43), (33, 40), (34, 41), (34, 42), (35, 43), (35, 44), (36, 44),
                     (36, 45), (37, 45)],
          ("attack", 0): [(36, 35), (37, 35)]}
# the death, frames 3-8 (0-based 2-7): the design's figure turned as one - (degrees counter-clockwise, rows over the
# ground, the figure's middle in columns from the pivot, the shuriken still on his back)
DEAD = {2: (60, 4, -4, True), 3: (90, 2, -5, False), 4: (90, 0, -5, False), 5: (90, 0, -5, False),
        6: (90, 0, -5, False), 7: (90, 0, -5, False)}
SOLES = 11                      # the soles' row under the pivot
STAR_UNDER = 6                  # columns of the lying star under his head
# the shuriken on the design's back: per row (63-81), its last column
BACK_STAR = {63: 62, 64: 62, 65: 62, 66: 62, 67: 62, 68: 62, 69: 58, 70: 57, 71: 57, 72: 58, 73: 57, 74: 56, 75: 55,
             76: 54, 77: 54, 78: 55, 79: 56, 80: 57, 81: 55}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def at1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def split(strip, n, cw, ch):
    cols, _ = layout(n)
    return [strip[(i // cols) * ch:(i // cols) * ch + ch, (i % cols) * cw:(i % cols) * cw + cw].copy() for i in range(n)]


def join(frames, cw, ch):
    cols, rows = layout(len(frames))
    out = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for i, f in enumerate(frames):
        out[(i // cols) * ch:(i // cols) * ch + ch, (i % cols) * cw:(i % cols) * cw + cw] = f
    return out


def paste(dst, src, x, y, under=False):
    """src's opaque squares onto dst with src's top-left at (x, y); under: only where dst is clear."""
    h, w = src.shape[:2]
    for yy in range(h):
        for xx in range(w):
            if src[yy, xx, 3] and 0 <= y + yy < dst.shape[0] and 0 <= x + xx < dst.shape[1]:
                if under and dst[y + yy, x + xx, 3]:
                    continue
                dst[y + yy, x + xx] = src[yy, xx]


def design_frame(des, pivot, dy, near=(0, 0), far=(0, 0), cw=80, ch=72):
    """The design at the cell's pivot: the shoes (near drawn in front) at their offsets/lifts, the upper block dy rows
    down and laid over them (the hem tucks over the shoe tops)."""
    f = np.zeros((ch, cw, 4), np.uint8)
    ox, oy = pivot[0] - PIVOT[0], pivot[1] - PIVOT[1]
    for (r0, r1, c0, c1), (dx, lift) in ((FAR_SHOE, far), (NEAR_SHOE, near)):
        paste(f, des[r0:r1 + 1, c0:c1 + 1], c0 + ox + dx, r0 + oy - lift)
    u0, u1 = UPPER
    paste(f, des[u0:u1 + 1], ox, u0 + oy + dy)
    return f


def shoe_of(des, leg):
    """The design's own shoe with its top outline."""
    if leg == "near":
        return des[96:100, 54:61].copy()
    s = des[96:100, 66:74].copy()
    s[0, 0] = 0                 # the robe's hem outline, not the shoe's
    return s


def run_frame(des, pivot, k, cw=80, ch=72):
    """The design's upper body RUN_DY[k] rows down over two legs: each a 2-square shin from its hip to the top of its
    shoe at the step; the near leg (shoe, shin and the shin's outline) laid over the far one."""
    f = np.zeros((ch, cw, 4), np.uint8)
    ox, oy = pivot[0] - PIVOT[0], pivot[1] - PIVOT[1]
    dy = RUN_DY[k]
    lit, dark = des[97, 56, :3], des[98, 55, :3]
    far = set()
    for leg, mid, lift in (("far", RUN_FAR[k], RUN_FAR_LIFT[k]), ("near", RUN_NEAR[k], RUN_NEAR_LIFT[k])):
        shoe = shoe_of(des, leg)
        h, w = shoe.shape[:2]
        top, left = 96 - lift + oy, PIVOT[0] + mid - w // 2 + ox
        mine = set()
        for yy, xx in zip(*np.nonzero(shoe[..., 3])):
            f[top + yy, left + xx] = shoe[yy, xx]
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
            if 0 <= y < ch and 0 <= x < cw and (not f[y, x, 3] or (y, x) in far):
                f[y, x, :3], f[y, x, 3] = C["#"], 255
        far = mine
    up = des[UPPER[0]:UPPER[1] + 1].copy()
    for y, x in LEG_STUB:
        up[y - UPPER[0], x] = 0
    paste(f, up, ox, UPPER[0] + oy + dy)
    return f


def pieces(m):
    """8-connected pieces of a mask (lists of (y, x))."""
    seen, out = set(), []
    for y0, x0 in zip(*np.nonzero(m)):
        if (y0, x0) in seen:
            continue
        st, piece = [(y0, x0)], []
        seen.add((y0, x0))
        while st:
            y, x = st.pop()
            piece.append((y, x))
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    q = (y + a, x + b)
                    if 0 <= q[0] < m.shape[0] and 0 <= q[1] < m.shape[1] and m[q] and q not in seen:
                        seen.add(q)
                        st.append(q)
        out.append(piece)
    return out


def figure(des, star):
    """The design's whole figure, with or without the shuriken on its back, cropped."""
    fig = des[63:100].copy()
    if not star:
        for y, last in BACK_STAR.items():
            fig[y - 63, :last + 1] = 0
    ys, xs = np.nonzero(fig[..., 3])
    return fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def turned(fig, deg):
    """The figure turned counter-clockwise (90 exact: the head goes left, the face looks up), cropped."""
    t = np.rot90(fig, 1).copy() if deg == 90 else rotsprite(fig, (fig.shape[1] // 2, fig.shape[0] - 1), deg)[0]
    ys, xs = np.nonzero(t[..., 3])
    return t[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def dead_frames(frs, piv, des, cw, ch):
    """Frames 3-8 of the death: the turned figure on the ground under each frame's pivot; once he lies, Codex's lying
    star (its frame 5's piece right of the body) under his head, its bottom on the ground."""
    f5 = frs[4]
    star_sq = [p for p in pieces(f5[..., 3] > 0) if min(x for _, x in p) >= 61]
    ys = [y for p in star_sq for y, _ in p]
    xs = [x for p in star_sq for _, x in p]
    star = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1, 4), np.uint8)
    for p in star_sq:
        for y, x in p:
            star[y - min(ys), x - min(xs)] = f5[y, x]
    for k, (deg, lift, mid, on_back) in DEAD.items():
        f = np.zeros((ch, cw, 4), np.uint8)
        t = turned(figure(des, on_back), deg)
        px, py = piv[k]
        left = px + mid - t.shape[1] // 2
        if not on_back:
            paste(f, star, left + STAR_UNDER - star.shape[1], py + SOLES - star.shape[0] + 1)
        paste(f, t, left, py + SOLES - lift - t.shape[0] + 1)
        frs[k] = f
    return frs


def build():
    cells = json.load(open(lp(os.path.join(SRC, "kennen_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    des = at1x(DESIGN)
    out = {}
    for tag in TAGS:
        frs = split(at1x(os.path.join(SRC, f"kennen_{tag}.png")), len(cells["tags"][tag]), cw, ch)
        piv = [fr["pivot"] for fr in cells["tags"][tag]]
        if tag == "run":
            frs = [run_frame(des, piv[k], k, cw, ch) for k in range(8)]
        elif tag == "skill2":
            frs = [design_frame(des, piv[k], DASH_DY[k], (DASH_NEAR[k], DASH_NEAR_LIFT[k]),
                                (DASH_FAR[k], DASH_FAR_LIFT[k]), cw, ch) for k in range(4)]
        elif tag == "ult":
            for k, up in LEAP.items():
                frs[k] = design_frame(des, piv[k], -up, (0, up + 1), (0, up + 1), cw, ch)
        elif tag == "dead":
            frs = dead_frames(frs, piv, des, cw, ch)
        for k in range(len(frs)):
            if (tag, k) in COPY:
                frs[k] = frs[COPY[(tag, k)]].copy()
            for y, x in STRAYS.get((tag, k), []):
                frs[k][y, x] = 0
        out[tag] = join(frs, cw, ch)
    return out, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a 4x review sheet of every strip into this folder")
    a = ap.parse_args()
    out, cells = build()
    same = True
    for tag, strip in out.items():
        big = np.repeat(np.repeat(strip, Z, 0), Z, 1)
        path = os.path.join(OUT, f"kennen_{tag}.png")
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            ok = np.array_equal(old, big)
            same &= ok
            print(tag, "same" if ok else "DIFFERS")
        else:
            Image.fromarray(big).save(lp(path))
    if not a.check:
        shutil.copyfile(lp(os.path.join(SRC, "kennen_cells.json")), lp(os.path.join(OUT, "kennen_cells.json")))
        print("written", ", ".join(out))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        cw, ch = cells["cell"]
        rows = []
        for tag in TAGS:
            frs = split(out[tag], len(cells["tags"][tag]), cw, ch)
            rows.append(np.concatenate([f[10:64] for f in frs], axis=1))
        W = max(r.shape[1] for r in rows)
        sheet = np.zeros((sum(r.shape[0] for r in rows), W, 4), np.uint8)
        y = 0
        for r in rows:
            sheet[y:y + r.shape[0], :r.shape[1]] = r
            y += r.shape[0]
        im = Image.fromarray(sheet).resize((W * 4, sheet.shape[0] * 4), Image.NEAREST)
        bg = Image.new("RGBA", im.size, (104, 112, 72, 255))
        bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(a.review, "kennen_strips_fixed.png"))
    if a.check and not same:
        sys.exit(1)


if __name__ == "__main__":
    main()
