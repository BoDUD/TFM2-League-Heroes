#!/usr/bin/env python3
"""Kha'Zix's action strips: Codex's step-2 delivery (assets/source/khazix/codex_strips/) with the death redone.

    python tools/art/fix_khazix_strips.py [--check]

Codex re-posed the design's own parts (its HANDOFF: arms and claws cut out and turned whole by 45-degree steps, the
torso and legs square for square the design's, the head pasted in every frame) - the casting body is the idle's, as
the user's rule asks - and those strips go in as delivered. Its death did not: frames 3-4 tipped the body but kept the
head upright and left a leg hanging under it, and frames 5-8 stood the 90-degree figure on one leg instead of lying it
down (the user: 「完成下一步 有问题的地方你要灵活运用已有的工具来收尾」). DEAD rebuilds them as league_sivir's accepted
death (rig_samira.py's): frames 1-2 Codex's (struck, knocked back), then the WHOLE design turned 45 degrees back
(rigkit.turn, RotSprite, about the back foot), then a quarter turn counter-clockwise - on his back, the head to the
image left, the bent insect legs up at the right - first a row above the ground (the bounce), then on it.
The run was Codex's rows of the legs shifted in place - the feet slid, the legs never crossed, and the two scythe
claws that hang to the ground in the design (they read as two more legs) stood still: the user, 「走路时腿有点奇怪啊 这是
交叉步？」. RUN rebuilds it from the design (rig_samira.py's accepted run): the two insect legs cut out (NEAR_LEG, the
image-left one, and FAR_LEG under the body), each swung from its hip by row shear with the foot moved whole (STRIDE: the
feet cross, each lifted while it passes under the body, the lift spread along the shin so the foot never comes off),
the far leg one shade darker, the body (everything else, the pasted head with it) bobbing a row on each landing, and
the two claws (BACK_CLAW, FRONT_CLAW: their parts under CLAW_ROW) lifted in turn off the ground as the legs pass.
Reads codex_strips/khazix_<tag>.png (8x) and khazix_cells.json, writes assets/source/native/khazix_<tag>.png (8x) and
khazix_cells.json for tools/art/import_native.py. --check only prints what would change.
"""
import argparse
import math
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "khazix", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(OUT, "khazix_native.png")
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99)
SOLES = 99
BACK_FOOT = (50.0, 99.0)         # the turn's joint: the back foot's heel on the ground
# the death, per frame: Codex's frame, ("tilt", degrees counter-clockwise, dx), ("lying", rows above the ground, dx);
# dx = where the box's centre lies from the standing point (he falls back: to the image left)
DEAD = ["codex", "codex", ("tilt", 45, -6), ("lying", 1, -8), ("lying", 0, -8), ("lying", 0, -8), ("lying", 0, -8),
        ("lying", 0, -8)]


# ---- the run (the design's canvas: soles on row 99)
NEAR_HIP, NEAR_FOOT = 84, 95        # the image-left leg: from its hip (hidden under the body) to the toe claws' rows
FAR_HIP, FAR_FOOT = 89, 95
CLAW_ROW = 88                       # the claws' parts from this row down lift off the ground
# per frame: near foot dx, near lift, far foot dx, far lift, back-claw lift, front-claw lift, body bob (rows down)
STRIDE = [(0, 0, 0, 0, 0, 0, 1), (4, 1, -3, 0, 2, 0, 0), (9, 2, -7, 0, 3, 0, 0), (14, 1, -11, 0, 2, 0, 0),
          (16, 0, -14, 0, 0, 0, 1), (12, 0, -10, 1, 0, 2, 0), (7, 0, -6, 2, 0, 3, 0), (3, 0, -2, 1, 0, 2, 0)]
BONE = {(242, 220, 212), (255, 246, 240), (200, 168, 168)}     # the claws' edge colours (never part of a leg)


def leg_masks(d):
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    bone = np.zeros(op.shape, bool)
    for c in BONE:
        bone |= (d[..., :3] == c).all(-1)
    near = op & ~bone & (((yy >= NEAR_HIP) & (xx <= 55)) | ((yy >= 82) & (yy < NEAR_HIP) & (xx >= 52) & (xx <= 55)))
    far = op & ~bone & (yy >= FAR_HIP) & (xx >= 63) & (xx <= 80)
    back = op & ~near & ~far & (yy >= CLAW_ROW) & (xx >= 53) & (xx <= 63)
    front = op & ~near & ~far & (yy >= CLAW_ROW) & (xx >= 75)
    return near, far, back, front


def darker(d):
    """Each colour -> the design's next darker colour of a like hue (the outline stays)."""
    op = d[..., 3] > 0
    pal = np.unique(d[op][:, :3], axis=0).astype(int)
    lum = pal @ np.array([299, 587, 114]) / 1000
    out = {}
    for c, l in zip(pal, lum):
        cand = [(p, pl) for p, pl in zip(pal, lum) if pl < l - 6]
        if l < 30 or not cand:
            out[tuple(c)] = tuple(c)
            continue
        cn = c / max(1, c.sum())
        out[tuple(c)] = tuple(min(cand, key=lambda q: 400 * np.abs(q[0] / max(1, q[0].sum()) - cn).sum() + (l - q[1]))[0])
    return out


def swung(d, mask, hip, foot, dx, lift, drop, shade=None):
    """The leg's squares sheared from the hip: rows above `foot` moved in proportion (dx and lift), the foot whole."""
    out = np.zeros_like(d)
    for r, c in zip(*np.nonzero(mask)):
        t = min(1.0, max(0, r - hip) / max(1, foot - hip))
        sh = int(math.floor(dx * t + 0.5))
        up = int(math.floor(lift * t + 0.5))
        rr, cc = r - up + drop, c + sh
        if 0 <= rr < d.shape[0] and 0 <= cc < d.shape[1]:
            px = d[r, c].copy()
            if shade is not None:
                px[:3] = shade[tuple(int(v) for v in px[:3])]
            out[rr, cc] = px
    return out


def new_gaps_filled(a, d, bob, outline):
    """Gaps the swung legs enclose (between a leg, a claw and the body: the background showed through - the user:
    「腿部移动时缺失模型看不到？」) take the commonest colour round them; the design's own gaps (beside the jaw) stay."""
    own = set()
    for comp in K.holes(K.finish(d, outline, SOLES)):     # with its outline closed, as the idle is
        own |= {(y + bob, x) for y, x in comp}
    for comp in K.holes(a):
        if own & set(comp):
            continue
        nb = {}
        cs = set(comp)
        for y, x in comp:
            for dy, dx in K.N4:
                q = (y + dy, x + dx)
                if q not in cs and a[q][3] and tuple(int(v) for v in a[q][:3]) != tuple(outline):
                    key = tuple(int(v) for v in a[q])
                    nb[key] = nb.get(key, 0) + 1
        col = np.array(max(nb, key=nb.get) if nb else tuple(outline) + (255,), np.uint8)
        for y, x in comp:
            a[y, x] = col
    return a


def run_frame(d, k, masks, shade):
    near, far, back, front = masks
    nd, nl, fd, fl, bl, frl, bob = STRIDE[k]
    rest = d.copy()
    rest[near | far | back | front] = 0
    out = np.zeros_like(d)
    K.put(out, swung(d, far, FAR_HIP, FAR_FOOT, fd, fl, bob, shade), 0, 0)
    K.put(out, K.shifted(rest, 0, bob), 0, 0)
    claw = lambda m, lift: K.shifted(np.where(m[..., None], d, 0).astype(np.uint8), 0, bob - lift)
    K.put(out, claw(back, bl), 0, 0)
    # the near leg over the back claw (it is the leg nearest the viewer), under the front claw
    K.put(out, swung(d, near, NEAR_HIP, NEAR_FOOT, nd, nl, bob), 0, 0)
    K.put(out, claw(front, frl), 0, 0)
    out[SOLES + 1:] = 0
    return out


def at1x(path):
    a = np.asarray(Image.open(path).convert("RGBA"))
    a = a[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def outline_colour(a):
    op = a[..., 3] > 0
    cols, n = np.unique(a[op][:, :3], axis=0, return_counts=True)
    return min(cols, key=lambda c: int(c.sum())).tolist()


def on_ground(a, rise, dx):
    """On the ground line (rise rows above it), its box centred dx columns from the standing point."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    return K.shifted(a, PIVOT[0] + dx - (xs.min() + xs.max() + 1) // 2, SOLES - rise - ys.max())


def dead_frame(design, what):
    kind, amount, dx = what
    ys, xs = np.nonzero(design[..., 3] > 0)
    part = K.Part(design[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(),
                  (BACK_FOOT[0] - xs.min(), BACK_FOOT[1] - ys.min()))
    turned = K.turn(part, amount if kind == "tilt" else 90)
    out = np.zeros_like(design)
    K.place(out, turned, BACK_FOOT)
    return on_ground(out, 0 if kind == "tilt" else amount, dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(SRC, "khazix_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    design = at1x(DESIGN) if Image.open(DESIGN).size[0] != 128 else np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ink = outline_colour(design)
    for tag in TAGS:
        sheet = at1x(os.path.join(SRC, f"khazix_{tag}.png"))
        if tag == "run":
            cols = sheet.shape[1] // cw
            masks, shade = leg_masks(design), darker(design)
            for i in range(len(STRIDE)):
                fig = new_gaps_filled(K.finish(run_frame(design, i, masks, shade), ink, SOLES), design, STRIDE[i][6], ink)
                X, Y = (i % cols) * cw, (i // cols) * ch
                px, py = cells["tags"][tag][i]["pivot"]
                cell = np.zeros((ch, cw, 4), np.uint8)
                K.put(cell, fig, px - PIVOT[0], py - PIVOT[1])
                sheet[Y:Y + ch, X:X + cw] = cell
            print("run: 8 frames rebuilt from the design (crossing legs, claws lifted in turn)")
        if tag == "dead":
            cols = sheet.shape[1] // cw
            for i, what in enumerate(DEAD):
                if what == "codex":
                    continue
                fig = K.finish(dead_frame(design, what), ink, SOLES)
                X, Y = (i % cols) * cw, (i // cols) * ch
                px, py = cells["tags"][tag][i]["pivot"]
                cell = np.zeros((ch, cw, 4), np.uint8)
                K.put(cell, fig, px - PIVOT[0], py - PIVOT[1])
                sheet[Y:Y + ch, X:X + cw] = cell
            print(f"dead: frames {[i + 1 for i, w in enumerate(DEAD) if w != 'codex']} rebuilt from the design")
        if a.check:
            continue
        big = Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1))
        big.save(os.path.join(OUT, f"khazix_{tag}.png"))
    if not a.check:
        shutil.copyfile(os.path.join(SRC, "khazix_cells.json"), os.path.join(OUT, "khazix_cells.json"))
        print("wrote", ", ".join(f"khazix_{t}.png" for t in TAGS), "and khazix_cells.json to assets/source/native")


if __name__ == "__main__":
    main()
