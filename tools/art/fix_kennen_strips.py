#!/usr/bin/env python3
"""Kennen's action strips: Codex's step-2 delivery made clean (the user: "动作包有奇怪的地方请你调整 codex太笨了").

    python tools/art/fix_kennen_strips.py [--check] [--review DIR]

Codex drew the eight strips from the approved 37-row design (assets/source/kennen/MODEL_STRIPS.md) and pasted the
design's head into every frame (assets/source/kennen/codex_strips/, as delivered: 8x, its HANDOFF, manifest and checks).
Its checks passed (blocks, palette, alpha, feet line, the head square for square); what they did not see is fixed here:
1. The run (8 frames) drew the robe in the gloves' dark plum and the legs as one dark lump that hardly moved (its own
   HANDOFF: "移动腿部交换的幅度偏小"): rebuilt from the design - the idle's whole upper body (the shuriken, the head,
   the robe and the claws: one block, so nothing comes apart) on a step bob (lowest when both feet are down), the two
   shoes (the design's own) stepping in turn, the swinging one lifted a row, the near one drawn in front.
2. E's dash (4 frames) was smeared into one-square streaks: the same design block crouched 2-3 rows over a long stride
   (the shoes swapping); the ball of lightning round him is an effect (step 3).
3. R's leap (frames 2-3) had stick legs under a dark column and the shuriken balanced on the hood: the design leaps
   (3 and 4 rows up, the shoes tucked a row), the shuriken staying on his back.
4. The attack's frames 2-3 held the shuriken with no arm (it floated beside and over the hood): frame 2 is frame 1 again
   (the hand reaching back to the shuriken still on his back - an arm drawn there would be hidden by the hood), frame 3
   gets an arm from the near shoulder up behind the hood to a plum glove gripping the star (a sleeve 2 squares wide in
   the robe's violets inside the outline, only where the frame is clear: the arm goes behind the head).
5. One-square strays: the brown tips over Q's shuriken (frames 1-2), the gold strand and the violet blob over the hood
   in W's crouch (frames 3-4), two gold squares beside the attack's frame 1.
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
SRC = os.path.join(ROOT, "assets", "source", "kennen", "codex_strips")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "kennen_native.png")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["idle", "run", "attack", "skill", "skill2", "w", "ult", "hit", "dead"]
PIVOT = (64, 88)                # the design's standing point on its 128x128 canvas
UPPER = (63, 95)                # the design's rows above the shoes: the shuriken's tip to the robe's hem
NEAR_SHOE = (96, 99, 54, 60)    # rows, columns of the design's shoes
FAR_SHOE = (96, 99, 65, 73)
C = {"#": (0x0B, 0x06, 0x0E), "b": (0x5E, 0x23, 0x86), "d": (0x8A, 0x36, 0xB8), "v": (0x3A, 0x14, 0x52),
     "p": (0x45, 0x23, 0x48), "P": (0x25, 0x13, 0x24), "q": (0x6E, 0x3E, 0x75), "Y": (0xFE, 0xDC, 0x80)}

# the run: a two-step cycle (8 x 100 ms) - body rows down, shoe offsets (columns), shoe lifts (rows)
RUN_DY = [1, 0, 0, 1, 1, 0, 0, 1]
RUN_NEAR = [4, 2, -1, -3, -3, -1, 2, 4]
RUN_FAR = [-3, -1, 2, 4, 4, 2, -1, -3]
RUN_NEAR_LIFT = [0, 0, 0, 0, 0, 1, 1, 0]
RUN_FAR_LIFT = [0, 1, 1, 0, 0, 0, 0, 0]
# E's dash (4 x 75 ms): crouched 2-3 rows, a long stride that swaps
DASH_DY = [2, 3, 2, 3]
DASH_NEAR = [-4, -1, 4, 1]
DASH_FAR = [4, 1, -4, -1]
DASH_NEAR_LIFT = [0, 1, 0, 0]
DASH_FAR_LIFT = [0, 0, 0, 1]
# R's leap, frames 2 and 3 (0-based 1, 2): rows up, the shoes a row more
LEAP = {1: 3, 2: 4}
# arms for the attack's frames 2-3 (0-based 1, 2): shoulder and hand (cell x, y)
ARMS = {("attack", 2): ((35, 41), (36, 24))}
COPY = {("attack", 1): 0}       # (tag, frame) -> the frame whose pixels it takes
# strays: (tag, 0-based frame) -> cell (y, x) squares cleared
STRAYS = {("skill", 0): [(21, 38)],
          ("skill", 1): [(21, 36), (22, 39)],
          ("w", 2): [(32, 36), (33, 37), (33, 38), (34, 38), (34, 39), (35, 39)],
          ("w", 3): [(32, 41), (32, 42), (32, 43), (33, 40), (34, 41), (34, 42), (35, 43), (35, 44), (36, 44),
                     (36, 45), (37, 45)],
          ("attack", 0): [(36, 35), (37, 35)]}


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


def arm(f, a, b):
    """A sleeve from a (shoulder) to b (hand), 2 squares wide, violet with a light edge, outlined, only on clear
    squares; then a 2x2 plum glove at b over everything."""
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0)) * 3 + 1
    body = set()
    for k in range(n):
        t = k / (n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for dx in (0, 1):
            body.add((int(round(y)), int(round(x - 0.5)) + dx))
    ring = {(y + dy, x + dx) for y, x in body for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - body
    for y, x in ring:
        if 0 <= y < f.shape[0] and 0 <= x < f.shape[1] and not f[y, x, 3]:
            f[y, x, :3], f[y, x, 3] = C["#"], 255
    for y, x in body:
        if 0 <= y < f.shape[0] and 0 <= x < f.shape[1] and not f[y, x, 3]:
            left = (y, x - 1) not in body
            f[y, x, :3], f[y, x, 3] = (C["d"] if left else C["b"]), 255
    glove = {(y1, x1): "p", (y1, x1 + 1): "q", (y1 + 1, x1): "P", (y1 + 1, x1 + 1): "p"}
    for (y, x), c in glove.items():
        f[y, x, :3], f[y, x, 3] = C[c], 255
    for y, x in {(y + dy, x + dx) for (y, x) in glove for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - set(glove):
        if 0 <= y < f.shape[0] and 0 <= x < f.shape[1] and not f[y, x, 3]:
            f[y, x, :3], f[y, x, 3] = C["#"], 255
    return f


def build():
    cells = json.load(open(lp(os.path.join(SRC, "kennen_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    des = at1x(DESIGN)
    out = {}
    for tag in TAGS:
        frs = split(at1x(os.path.join(SRC, f"kennen_{tag}.png")), len(cells["tags"][tag]), cw, ch)
        piv = [fr["pivot"] for fr in cells["tags"][tag]]
        if tag == "run":
            frs = [design_frame(des, piv[k], RUN_DY[k], (RUN_NEAR[k], RUN_NEAR_LIFT[k]), (RUN_FAR[k], RUN_FAR_LIFT[k]),
                                cw, ch) for k in range(8)]
        elif tag == "skill2":
            frs = [design_frame(des, piv[k], DASH_DY[k], (DASH_NEAR[k], DASH_NEAR_LIFT[k]),
                                (DASH_FAR[k], DASH_FAR_LIFT[k]), cw, ch) for k in range(4)]
        elif tag == "ult":
            for k, up in LEAP.items():
                frs[k] = design_frame(des, piv[k], -up, (0, up + 1), (0, up + 1), cw, ch)
        for k in range(len(frs)):
            if (tag, k) in COPY:
                frs[k] = frs[COPY[(tag, k)]].copy()
            for y, x in STRAYS.get((tag, k), []):
                frs[k][y, x] = 0
            if (tag, k) in ARMS:
                frs[k] = arm(frs[k], *ARMS[(tag, k)])
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
