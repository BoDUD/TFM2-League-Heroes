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
HEAD = os.path.join(OUT, "khazix_head_1x.png")     # the head pasted in every frame (the strips pack's)
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
FAR_HIP, FAR_FOOT = 89, 95          # the mid leg from under the knee (the knee stays on the body, as the user saw it)
CLAW_ROW = 88                       # the claws' parts from this row down lift off the ground
# per frame: near foot dx, near lift, far foot dx, far lift, back-claw lift, front-claw lift, body bob (rows down)
STRIDE = [(0, 0, 0, 0, 0, 0, 1), (4, 1, -3, 0, 2, 0, 0), (9, 2, -7, 0, 3, 0, 0), (14, 1, -11, 0, 2, 0, 0),
          (16, 0, -14, 0, 0, 0, 1), (12, 0, -10, 1, 0, 2, 0), (7, 0, -6, 2, 0, 3, 0), (3, 0, -2, 1, 0, 2, 0)]
BONE = {(242, 220, 212), (255, 246, 240), (200, 168, 168)}     # the claws' edge colours (never part of a leg)


def _rows(spec, op):
    m = np.zeros(op.shape, bool)
    for y, (x0, x1) in spec.items():
        m[y, x0:x1 + 1] = True
    return m & op


# The parts, as Codex cut them for its strips (codex_strips/raw/build_khazix_strips.py): the image-left arm with its
# claw, the image-right arm with its claw, the image-left leg, the mid leg. The first run used rough boxes: the mid
# leg's box took a piece of the image-right arm along, and claw-edge and outline squares no box held stayed behind
# when the legs moved - a loose piece and a hole showing the ground (the user: 「眼睛是瞎的吗」).
ARM_BACK = {**{y: (55, 60) for y in range(75, 77)}, **{y: (55, 61) for y in range(77, 80)},
            **{y: (56, 62) for y in range(80, 82)}, **{y: (57, 64) for y in range(82, 84)},
            **{y: (57, 65) for y in range(84, 86)}, **{y: (57, 64) for y in range(86, 88)}, 88: (58, 65), 89: (58, 64),
            90: (58, 63), 91: (58, 62), 92: (57, 62), 93: (58, 61), 94: (57, 61), 95: (57, 60), 96: (57, 60),
            97: (56, 59), 98: (56, 59), 99: (56, 58)}
ARM_FRONT = {**{y: (78, 84) for y in range(75, 78)}, **{y: (79, 87) for y in range(78, 82)},
             **{y: (81, 87) for y in range(82, 85)}, **{y: (77, 86) for y in range(85, 88)}, 88: (77, 85),
             89: (77, 84), 90: (79, 84), 91: (80, 85), 92: (80, 86), 93: (81, 86), 94: (81, 87), 95: (82, 87),
             96: (83, 88), 97: (84, 88), 98: (85, 88), 99: (86, 88)}
LEG_LEFT = {**{y: (56, 61) for y in range(83, 86)}, **{y: (52, 59) for y in range(86, 90)},
            **{y: (50, 56) for y in range(90, 95)}, **{y: (47, 54) for y in range(95, 100)}}
LEG_MID = {83: (68, 75), **{y: (68, 77) for y in range(84, 89)}, **{y: (64, 77) for y in range(89, 94)},
           **{y: (64, 81) for y in range(94, 100)}}
TORSO_LOW = 88                      # above this row a square no part holds is the torso's (its underside between legs)


def leg_masks(d):
    """near (the lit image-left leg), far (the shaded mid leg under its knee), back / front (the claws' parts from
    CLAW_ROW down): the first run's boxes (the user's 「之前那一版只是腿部有像素缺失」 - their shapes stay), with Codex's
    exact arm outlines taken out of the leg boxes (the mid leg's box took a piece of the image-right arm along) and the
    squares under CLAW_ROW that no box held (claw-edge and outline squares that stayed behind as loose pieces when the
    legs moved) given to the part they touch most."""
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    bone = np.zeros(op.shape, bool)
    for c in BONE:
        bone |= (d[..., :3] == c).all(-1)
    head = np.asarray(Image.open(HEAD).convert("RGBA"))[..., 3] > 0
    back_arm = _rows(ARM_BACK, op) & ~head
    front_arm = _rows(ARM_FRONT, op) & ~head
    near = op & ~bone & (((yy >= NEAR_HIP) & (xx <= 55)) | ((yy >= 82) & (yy < NEAR_HIP) & (xx >= 52) & (xx <= 55)))
    near &= ~back_arm
    far = op & ~bone & (yy >= FAR_HIP) & (xx >= 63) & (xx <= 80) & ~front_arm & ~back_arm
    back = op & ~near & ~far & (yy >= CLAW_ROW) & ((xx >= 53) & (xx <= 63) | back_arm)
    front = op & ~near & ~far & ~back & (yy >= CLAW_ROW) & ((xx >= 75) | front_arm)
    parts = [near, far, back, front]
    left = op & ~(near | far | back | front | head) & (yy >= CLAW_ROW)
    for y, x in zip(*np.nonzero(left)):
        touch = [sum(int(m[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                     if 0 <= y + dy < op.shape[0] and 0 <= x + dx < op.shape[1]) for m in parts]
        if max(touch):
            parts[touch.index(max(touch))][y, x] = True
    return near, far, back, front


def darker(d):
    """Each colour -> the design's next darker colour of a like hue (the outline stays)."""
    op = d[..., 3] > 0
    pal = np.unique(d[op][:, :3], axis=0).astype(int)
    lum = pal @ np.array([299, 587, 114]) / 1000
    out = {}
    for c, l in zip(pal, lum):
        # never the outline: the mid leg's darkest violet turned black read as a hole in the leg
        cand = [(p, pl) for p, pl in zip(pal, lum) if pl < l - 6 and pl >= 30]
        if l < 30 or not cand:
            out[tuple(c)] = tuple(c)
            continue
        cn = c / max(1, c.sum())
        out[tuple(c)] = tuple(min(cand, key=lambda q: 400 * np.abs(q[0] / max(1, q[0].sum()) - cn).sum() + (l - q[1]))[0])
    return out


INK = (11, 8, 20)        # the design's outline colour


def swung(d, mask, hip, foot, dx, lift, drop, shade=None):
    """The leg's squares sheared from the hip: rows above `foot` moved across in proportion to dx, the foot whole; the
    WHOLE leg lifted `lift` rows (its top goes under the body) - lifting only the lower rows in proportion pressed rows
    onto each other and lost up to 15 of the far leg's 110 squares; where the shear steps a row more than a square
    across, the row is bridged to the one above in its own colours, so the leg never breaks into pieces (the user:
    「腿部移动时缺失模型看不到？」, 「之前那一版只是腿部有像素缺失」)."""
    out = np.zeros_like(d)
    ys, _ = np.nonzero(mask)
    prev = None
    for r in range(int(ys.min()), int(ys.max()) + 1):
        cols = np.nonzero(mask[r])[0]
        if not len(cols):
            prev = None
            continue
        t = min(1.0, max(0, r - hip) / max(1, foot - hip))
        sh = int(math.floor(dx * t + 0.5))
        rr = r - lift + drop
        if not 0 <= rr < d.shape[0]:
            continue
        row = {}
        for c in cols:
            px = d[r, c].copy()
            if shade is not None:
                px[:3] = shade[tuple(int(v) for v in px[:3])]
            row[c + sh] = px
        if prev is not None:
            # bridge: this row's run must touch the run above (8-connected); if it does not, the squares between take
            # the row's own commonest inner colour
            lo, hi = min(row), max(row)
            plo, phi = prev
            inner = [tuple(int(v) for v in px) for px in row.values() if tuple(int(v) for v in px[:3]) != INK]
            fill = np.array(max(set(inner), key=inner.count) if inner else tuple(next(iter(row.values()))), np.uint8)
            gap = range(hi + 1, plo) if hi < plo - 1 else range(phi + 1, lo) if lo > phi + 1 else range(0)
            for c in gap:
                row[c] = fill
        for c, px in row.items():
            if 0 <= c < d.shape[1]:
                out[rr, c] = px
        prev = (min(row), max(row))
    return out


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


# ---- the whole figure smaller (the user: 「螳螂可以整体缩小一点」; 42 x 45 squares at the design's size, Darius 42 x 36):
# rig_pyke.py's shrink - one square row in every SHRINK above the soles and one column in every SHRINK each side of the
# standing column come out of every frame alike (in each band the one most like its neighbour over all the frames, the
# idle and the run counted thrice), the soles and the standing column stay. The head Codex pasted in every upright frame
# comes out first and the head shrunk once goes back where its spot landed, so the face is the same squares in every
# frame; the lying death frames (no upright head) shrink as they are. No resampling.
SHRINK = 6


def bands(start, stop, step):
    res, d = [], 1 if step > 0 else -1
    while True:
        b = [start + d * j for j in range(abs(step))]
        if (b[-1] - stop) * d > 0:
            return res
        res.append(b)
        start += step


def drops(frames, weights, k):
    """The rows and columns to drop: one per band, the least different from the square row / column beyond it, never
    two neighbours."""
    st = np.stack(frames).astype(int)
    W = np.array(weights, float)[:, None]
    alpha = st[..., 3] > 0
    ys = np.nonzero(alpha.any((0, 2)))[0]
    xs = np.nonzero(alpha.any((0, 1)))[0]

    def cost(axis, i, j):
        diff = np.abs(np.take(st, i, axis=axis + 1) - np.take(st, j, axis=axis + 1)).sum(-1) > 0
        return float((diff * W).sum())

    def pick(bs, key):
        got = []
        for b in bs:
            c = [r for r in b if all(abs(r - g) > 1 for g in got)]
            got.append(min(c, key=key))
        return sorted(got)

    rows = pick(bands(SOLES - 1, int(ys.min()), -k), lambda r: cost(0, r, r - 1))
    left = pick(bands(PIVOT[0] - 1, int(xs.min()), -k), lambda c: cost(1, c, c + 1))
    right = pick(bands(PIVOT[0] + 1, int(xs.max()), k), lambda c: cost(1, c, c - 1))
    return rows, left, right


def shrink(f, rows, left, right):
    h, w = f.shape[:2]
    g = f[[r for r in range(h) if r not in rows]][:, [c for c in range(w) if c not in left and c not in right]]
    out = np.zeros_like(f)
    out[len(rows):, len(left):len(left) + g.shape[1]] = g
    return out


def shrunk_xy(x, y, rows, left, right):
    """Where a canvas square (x, y) lands after shrink."""
    return (x + sum(1 for c in left if c > x) - sum(1 for c in right if c < x), y + sum(1 for r in rows if r > y))


def head_at(f, head):
    """The offset of the pasted head in f (every square of it there), or None."""
    hy, hx = np.nonzero(head[..., 3] > 0)
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            ys, xs = hy + dy, hx + dx
            if ys.min() < 0 or xs.min() < 0 or ys.max() >= f.shape[0] or xs.max() >= f.shape[1]:
                continue
            if (f[ys, xs] == head[hy, hx]).all():
                return dx, dy
    return None


def shrink_frame(f, head, cut, ink):
    off = head_at(f, head)
    if off is None:
        return K.finish(shrink(f, *cut), ink, SOLES)
    dx, dy = off
    body = f.copy()
    body[K.shifted(head, dx, dy)[..., 3] > 0] = 0
    g = shrink(body, *cut)
    hy, hx = np.nonzero(head[..., 3] > 0)
    ax, ay = shrunk_xy(int(hx.min()), int(hy.min()), *cut)
    bx, by = shrunk_xy(int(hx.min()) + dx, int(hy.min()) + dy, *cut)
    put = K.shifted(shrink(head, *cut), bx - ax, by - ay)
    keep = put[..., 3] > 0
    g[keep] = put[keep]
    return K.finish(g, ink, SOLES, keep=keep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(SRC, "khazix_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    design = at1x(DESIGN) if Image.open(DESIGN).size[0] != 128 else np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ink = outline_colour(design)
    sheets = {}
    for tag in TAGS:
        sheet = at1x(os.path.join(SRC, f"khazix_{tag}.png"))
        if tag == "run":
            cols = sheet.shape[1] // cw
            masks, shade = leg_masks(design), darker(design)
            for i in range(len(STRIDE)):
                fig = K.finish(run_frame(design, i, masks, shade), ink, SOLES)
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
        sheets[tag] = sheet
    if SHRINK:
        # every frame on the design's canvas (its pivot on PIVOT), the cut found over all of them, then back in its cell
        def frames(tag):
            cols = sheets[tag].shape[1] // cw
            for i, c in enumerate(cells["tags"][tag]):
                X, Y = (i % cols) * cw, (i // cols) * ch
                yield X, Y, c["pivot"]

        canv = {}
        for tag in TAGS:
            for X, Y, (px, py) in frames(tag):
                cv = np.zeros((128, 128, 4), np.uint8)
                K.put(cv, sheets[tag][Y:Y + ch, X:X + cw], PIVOT[0] - px, PIVOT[1] - py)
                canv[tag, X, Y] = cv
        cut = drops(list(canv.values()), [3 if t in ("idle", "run") else 1 for t, _, _ in canv], SHRINK)
        head = np.asarray(Image.open(HEAD).convert("RGBA")).copy()
        for tag in TAGS:
            for X, Y, (px, py) in frames(tag):
                cell = np.zeros((ch, cw, 4), np.uint8)
                K.put(cell, shrink_frame(canv[tag, X, Y], head, cut, ink), px - PIVOT[0], py - PIVOT[1])
                sheets[tag][Y:Y + ch, X:X + cw] = cell
        print("shrink: rows", cut[0], "columns", cut[1], cut[2])
    for tag in TAGS:
        if a.check:
            continue
        sheet = sheets[tag]
        big = Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1))
        big.save(os.path.join(OUT, f"khazix_{tag}.png"))
    if not a.check:
        shutil.copyfile(os.path.join(SRC, "khazix_cells.json"), os.path.join(OUT, "khazix_cells.json"))
        print("wrote", ", ".join(f"khazix_{t}.png" for t in TAGS), "and khazix_cells.json to assets/source/native")


if __name__ == "__main__":
    main()
