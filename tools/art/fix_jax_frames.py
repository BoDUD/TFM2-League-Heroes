#!/usr/bin/env python3
"""Jax's action frames after a frame-by-frame review (2026-10-02): step 5 of tools/art/shrink_jax.py.

The user found the near leg gone from the attack's frame 3 (「我发现贾克斯这里腿部也变形了」「这里啊 腿部看不到吗」) and
holes in the death's frame 6 (「还有这里也有模型缺失」), then asked for every frame to be checked (「贾克斯还是有点怪
请认真修复」「在详细检查贾克斯 还有没有哪里有问题的」). Every game frame was compared with League's own at game size
(tools/lol/native_pose.py): Codex's frames, read off its image-model drafts, left the ground showing through the body in
50 of the 74 frames, 347 pixels - 1-8 in the hood, the cape and the legs of most actions (the idle's hood too), 15-21
in the E burst and the lying death, 67 round the face in the death's frame 6.
  1. LEG: the attack's frame 3 kept only a floating piece of the near foot under the body. It goes, and frame 2's near
     leg (the lunge's back leg, as League's frame 3 has it) is put under the frame.
  2. HOLES: every clear pixel the figure encloses - in the frame, or once tools/art/import_native.py has closed the
     outline round it (strips.complete_outline, simulated here) - is painted from its neighbours, the outline the
     completion would have put round it included: onion peel, each pixel the commonest colour of its painted
     8-neighbours that are not the outline (the outline only where nothing else touches). A pinhole's (PIN pixels or
     fewer) own dark ring then takes the colour round it, so no black dot is left in the cape. The real gaps stay open
     (KEEP): between the arm and the body, the lamppost and the body or the hood, the legs and the lantern, the cape
     and a leg - open in League's frames too.
fix(tag, frames, pivots) -> (frames, {what: count}); frames HxWx4 uint8 cells, pivots (x, y) per frame.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SOLES = 11
OUTLINE = (0x11, 0x03, 0x15)     # the idle's outline (import_native closes the outline in it)
DARK = 30                        # luminance under which a pixel counts as the outline
PIN = 6
# real gaps, (x0, x1, y0, y1) from the pivot (inclusive): a hole touching one stays open. Measured on the game frames
# (league_jax#sheet.png), one pixel of slack for the outline the import puts round them
KEEP = {("idle", k): [(8, 9, 4, 7)] for k in range(1, 7)}                # the near shin and the lantern
KEEP.update({("run", k): [(8, 12, -8, -5)] for k in range(1, 9)})         # the arm holding the lamppost, the chest
KEEP.update({
    ("attack", 1): [(-18, -10, -25, -13)],       # the raised lamppost and the hood
    ("attack", 6): [(-20, -13, 2, 8)],           # the hook, the hand and the near leg
    ("attack_e", 2): [(-10, -7, 3, 5)],          # the cape and the near leg
    ("attack_e", 3): [(-10, -5, 0, 5)],
    ("attack_e", 6): [(-12, -7, -20, -17)],      # the lamppost over the shoulder and the plume
    ("skill", 2): [(11, 13, -24, -20)],          # the raised arm and the hood
    ("skill", 3): [(-12, -11, -19, -16)],        # two strands of the cape
    ("skill2_burst", 3): [(-13, -7, -13, -12)],  # the lamppost and the arm
    ("skill2_burst", 5): [(-17, -6, -11, 1)],    # the swung arm and the body
    ("ult", 2): [(-19, -11, -42, -27)],          # the arm, the lamppost and the lantern in the leap
    ("ult", 3): [(12, 16, -28, -16)],            # the raised lamppost and the arm
    ("ult", 5): [(2, 5, -2, 6)],                 # the planted lamppost and the body
    ("ult", 6): [(6, 8, -2, 8)],
    ("hit", 1): [(21, 22, 3, 6)],                # the shin and the lantern
    ("hit", 2): [(8, 9, 4, 6)],
    ("dead", 4): [(12, 15, -10, -4)],            # the face and the arm on the planted lamppost
    ("dead", 5): [(11, 14, -6, -4)],
    ("dead", 7): [(14, 17, -2, 0)],              # the arm and the lantern
})
# clear pixels (from the pivot) open to the outside here that the import's outline closes into a hole all the same
# (its clean-up redraws the outline's corners): painted like the holes
EXTRA = {("attack_e", 1): [(-15, 5), (-16, 6), (-15, 6)], ("dead", 4): [(14, 3), (14, 4)],
         ("ult", 4): [(-15, -10)], ("dead", 7): [(13, 1)]}


def lum(a):
    a = np.asarray(a, float)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def outside(op):
    """Clear pixels joined (4-way) to the frame's border."""
    H, W = op.shape
    out = np.zeros_like(op)
    st = [(y, x) for y in range(H) for x in (0, W - 1) if not op[y, x]] + \
         [(y, x) for y in (0, H - 1) for x in range(W) if not op[y, x]]
    for y, x in st:
        out[y, x] = True
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and not op[yy, xx] and not out[yy, xx]:
                out[yy, xx] = True
                st.append((yy, xx))
    return out


def components(m):
    lab = np.zeros(m.shape, int)
    out = []
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        k = len(out) + 1
        st = [(y0, x0)]
        lab[y0, x0] = k
        pix = []
        while st:
            y, x = st.pop()
            pix.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = k
                    st.append((yy, xx))
        out.append(pix)
    return out


def leg(frames, pivots):
    """1: attack frame 3's floating foot piece out, frame 2's near leg under the frame."""
    a2, a3 = frames[1], frames[2].copy()
    (px, py), (qx, qy) = pivots[2], pivots[1]
    n = 0
    for y in range(6, 11):                       # the floating piece: rows +6..+10, columns -7..+3
        for x in range(-7, 4):
            if a3[py + y, px + x, 3]:
                a3[py + y, px + x] = 0
                n += 1
    for y in range(5, 12):                       # frame 2's near leg: rows +5..+11, columns -12..0
        for x in range(-12, 1):
            s = a2[qy + y, qx + x]
            if s[3] and not a3[py + y, px + x, 3]:
                a3[py + y, px + x] = s
                n += 1
    frames[2] = a3
    return n


def to_fill(tag, k, f, pivot):
    """The pixels to paint: enclosed clear pixels (now or after the import's outline completion) with the outline the
    completion would put round them, by hole, minus the KEEP gaps; [(pixels, pinhole?)]."""
    px, py = pivot
    op = f[..., 3] > 0
    closed, _, _ = G.complete_outline(f, color=OUTLINE, feet=py + SOLES)
    cop = closed[..., 3] > 0
    enclosed = (~op & ~outside(op)) | (~cop & ~outside(cop))
    for x, y in EXTRA.get((tag, k + 1), []):
        enclosed[py + y, px + x] |= not op[py + y, px + x]
    ring = cop & ~op                                          # what the completion adds
    grow = enclosed.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow |= ring & np.roll(np.roll(enclosed, dy, 0), dx, 1)
    out = []
    for pix in components(grow):
        xs = [x - px for _, x in pix]
        ys = [y - py for y, _ in pix]
        if any(min(xs) <= x1 and max(xs) >= x0 and min(ys) <= y1 and max(ys) >= y0
               for x0, x1, y0, y1 in KEEP.get((tag, k + 1), [])):
            continue
        out.append((pix, len([p for p in pix if enclosed[p]]) <= PIN))
    return out


def paint(f, pix, pin):
    """Onion peel over pix; a pinhole's dark ring then takes the colour round it."""
    todo = set(pix)
    H, W = f.shape[:2]
    while todo:
        done = []
        for y, x in todo:
            light, dark = [], []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and 0 <= yy < H and 0 <= xx < W and f[yy, xx, 3] and (yy, xx) not in todo:
                        c = tuple(int(v) for v in f[yy, xx, :3])
                        (dark if lum(c) < DARK else light).append(c)
            if light or dark:
                pool = light or dark
                done.append((y, x, max(set(pool), key=pool.count)))
        if not done:
            break
        for y, x, c in done:
            f[y, x, :3], f[y, x, 3] = c, 255
            todo.discard((y, x))
    if not pin:
        return 0
    n = 0
    near = {(y + dy, x + dx) for y, x in pix for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - set(pix)
    for y, x in sorted(near):
        if not (0 < y < H - 1 and 0 < x < W - 1) or not f[y, x, 3] or lum(f[y, x, :3]) >= DARK:
            continue
        nb = [tuple(int(v) for v in f[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
              if (dy or dx) and f[y + dy, x + dx, 3]]
        if len(nb) < 8:                                       # on the silhouette's edge: the outline stays
            continue
        light = [c for c in nb if lum(c) >= DARK]
        if len(light) >= 6:                                   # a dot in the cape, not a line between two parts
            f[y, x, :3] = max(set(light), key=light.count)
            n += 1
    return n


def fix(tag, frames, pivots):
    frames = [f.copy() for f in frames]
    report = {}
    if tag == "attack":
        report["leg"] = leg(frames, pivots)
    for k, f in enumerate(frames):
        holes = to_fill(tag, k, f, pivots[k])
        for pix, pin in holes:
            report["ring"] = report.get("ring", 0) + paint(f, pix, pin)
            report["holes"] = report.get("holes", 0) + 1
            report["pixels"] = report.get("pixels", 0) + len(pix)
    return frames, report
