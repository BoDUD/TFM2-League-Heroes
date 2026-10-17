#!/usr/bin/env python3
"""Kalista's step-2 frames: Codex's delivery (assets/source/kalista/codex_strips: 40 of 46 frames, one dense square a
pixel on the pack's 219 x 146 canvas) finished here -> assets/source/kalista/frames/<tag>_<n>.png + frames.json.

    python tools/art/import_kalista_strips.py [--review DIR]

Codex ran out of image quota after 40 frames (its HANDOFF.md, 2026-10-16: no death; heads redrawn per frame, sizes
drifting, the run's legs never crossing). The user: 「codex额度不够了还差几帧没画出来 你能画吗？用点工具和技术
然后弄到完美了喊我review」. So:
  1. size: each frame's head is matched against the design's at scales 0.85-1.2 (headfind below); the frames Codex
     drew bigger (SCALE) are brought back by taking whole rows and columns out (design_akali.dp_keep: never two
     neighbours, the soles' row kept), round the standing point - the Vayne / Akali way the user accepted;
  2. one head: the design's WHOLE head (helm, crest, black hair, face: design rows 0-39, columns 55-99) pasted where
     the frame's head matched, Codex's head under it and its crest (purple) and the crest's dark ring above the neck
     cleared (Elise's lesson: pasting only a face left Codex's crown beside it);
  3. run (all 8 frames, rebuilt): Codex's eight kept one foot ahead and one behind in every frame (+25..+50 and
     -12..-25 columns: a lunge sliding, never a step). The design's own upper body (pixel-identical to the idle: head,
     arms, spear, spares, skirt) over two legs drawn every frame from League's Run1 joints (tools/lol/pose_joints.py:
     hip, knee, ankle), the hips 10 apart under the skirt (the design's lunge has them 26 apart, too wide to cross),
     standing leg length (42 rows, design B), the body bobbing with League's hips (6 rows); thigh in the design's
     three skins, bronze knee, black shin guard with bronze rims, the design's own foot; the far leg a shade darker
     and under the near one. Near minus far foot x changes sign twice a cycle, lifts up to 13 rows;
  4. death (6 frames, none delivered), lossless only: 1 = the back hop's frame 1 (recoil) on the ground, 2 = the
     design's crouch 3 columns back (knees giving way), 3 = the back hop's frame 3 (falling back) a row over the
     ground; 4-6 = design B (upright; design A's head pasted) without its spear and the spares on its back, turned a
     quarter left: lying on her near side, head to the image left; 4 two rows up (the bounce); her spear (B's, a
     quarter right) planted tip down behind her head;
  5. tidy: specks (pieces under SPECK squares) off, the outline closed (strips.complete_outline, nothing under the
     soles), pinholes (1-2 clear squares walled in) filled with their commonest neighbour.
The idle (the design breathing) and hit come in the rig step (rig_kalista.py).
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
from design_akali import dp_keep  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kalista")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
COLS, ROWS, SOLE, PIV_X = 219, 146, 138, 130
DESIGN_AT = (44, 41)                     # design A on the canvas (its feet middle on the pivot)
OUTLINE = (2, 2, 2)
SPECK = 6


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def rgba(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


A = rgba(os.path.join(SRC, "hd", "A.png"))
B_ = rgba(os.path.join(SRC, "hd", "B.png"))


def is_purple(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return r > 50 and b > 0.8 * r and g < 0.6 * r


def is_skin(c):
    return c[2] > 150 and c[0] < 60


# ---------------------------------------------------------------------------------------------- the head
HR0, HR1, HC0, HC1 = 0, 40, 55, 100
HEAD = A[HR0:HR1, HC0:HC1].astype(int)
HM = HEAD[..., 3] > 0
CORE = HM.copy()
CORE[:12] = False
CORE[:, :76 - HC0] = False                # helm, face and hair: what every frame's head shares (the crest varies)


def find_head(a, guess=None, rng=30, template=HEAD, core=CORE):
    """(score, x, y): the top-left of the design head on the frame by the core's mean colour distance."""
    a = a.astype(int)
    H, W = a.shape[:2]
    ys, xs = np.nonzero(core)
    cols = template[ys, xs, :3]
    gx, gy = guess if guess else (DESIGN_AT[0] + HC0, DESIGN_AT[1] + HR0)
    best = None
    for oy in range(gy - rng, gy + rng + 1):
        for ox in range(gx - rng, gx + rng + 1):
            yy, xx = ys + oy, xs + ox
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            if ok.sum() < len(ys) * 0.9:
                continue
            px = a[yy[ok], xx[ok]]
            d = np.where(px[:, 3] > 0, np.abs(px[:, :3] - cols[ok]).sum(1), 400).mean()
            if best is None or d < best[0]:
                best = (d, ox, oy)
    return best


def paste_head(a):
    s, ox, oy = find_head(a)
    out = a.copy()
    H, W = a.shape[:2]
    big = ndimage.binary_dilation(HM, iterations=2)
    by, bx = np.nonzero(big)
    yy, xx = by + oy, bx + ox
    ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    out[yy[ok], xx[ok]] = 0
    neck = oy + 40
    gone = np.zeros((H, W), bool)
    for y in range(0, min(neck, H)):
        for x in np.nonzero(out[y, :, 3] > 0)[0]:
            if is_purple(out[y, x]):
                out[y, x] = 0
                gone[y, x] = True
    near = ndimage.binary_dilation(gone, iterations=2)
    near[neck:] = False
    out[near & (out[..., 3] > 0) & (out[..., :3].astype(int).sum(2) < 150)] = 0
    hy, hx = np.nonzero(HM)
    out[hy + oy, hx + ox] = HEAD[hy, hx].astype(np.uint8)
    ring = big & ~HM                           # Codex's arms, shoulders and spears in the ring round the head stay
    ry, rx = np.nonzero(ring)
    yy, xx = ry + oy, rx + ox
    ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    for y, x in zip(yy[ok], xx[ok]):
        c = a[y, x]
        if c[3] and not is_purple(c) and y >= oy + 22:
            out[y, x] = c
    return out, (ox, oy)


# ---------------------------------------------------------------------------------------------- the size
# headfind at scales 0.85-1.2 (2026-10-16): the frames Codex drew bigger than the design
SCALE = {"hop_f_1": 1.10, "hop_f_2": 1.10, "hop_f_3": 1.10, "ult_1": 1.10, "ult2_1": 1.10, "ult2_3": 1.15,
         "attack_3": 1.05, "attack_4": 1.05, "hop_b_2": 1.05, "skill2_2": 1.05, "skill2_3": 1.05, "skill2_4": 1.05,
         "run_3": 1.15, "run_4": 1.15, "run_5": 1.20, "run_6": 1.20, "run_7": 1.20, "run_8": 1.15}


def shrink(a, s):
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    f = a[y0:y1 + 1, x0:x1 + 1]
    h, w = f.shape[:2]
    key = ((f[..., 0].astype(np.int64) << 24) | (f[..., 1].astype(np.int64) << 16) |
           (f[..., 2].astype(np.int64) << 8) | f[..., 3])
    lum = 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]
    wt = np.where(f[..., 3] > 0, 1.0 + lum / 255.0, 0.2)
    rows, _ = dp_keep([key[r] for r in range(h)], [wt[r] for r in range(h)], round(h / s), hard=(h - 1,))
    f, key, wt = f[rows], key[rows], wt[rows]
    cols, _ = dp_keep([key[:, c] for c in range(w)], [wt[:, c] for c in range(w)], round(w / s))
    f = f[:, cols]
    out = np.zeros_like(a)
    nh, nw = f.shape[:2]
    ny1 = SOLE - round((SOLE - y1) / s)
    nx0 = PIV_X + round((x0 - PIV_X) / s)
    out[ny1 - nh + 1:ny1 + 1, nx0:nx0 + nw] = f
    return out


# ---------------------------------------------------------------------------------------------- the run
SQ = 2.05                                 # squares a game px (82 design rows = 40 game rows)
GROUND_Y = 9.8                            # League's planted toe (game px under the pivot)
STAND = 42                                # rows from the hips to the soles standing (design B)
# League Run1 at 0..700 ms (pose_joints.py assets/source/kalista/poses.json --tag run): near (L) hip, knee, foot, toe,
# far (R) hip, knee, foot, toe (x, y game px from the pivot)
JOINTS = [
    [(-1.5, -9.6), (0.2, 0.3), (-2.3, 7.9), (-1.3, 9.7), (2.4, -10.7), (5.4, -0.7), (-0.9, 3.3), (-1.3, 5.2)],
    [(-1.5, -10.6), (-3.5, -2.0), (-5.5, 6.9), (-5.2, 9.1), (2.5, -10.9), (7.8, -2.2), (4.3, 5.8), (4.3, 7.9)],
    [(-1.3, -13.0), (-2.5, -3.7), (-6.8, 1.3), (-7.2, 3.2), (2.7, -12.5), (6.9, -3.0), (7.2, 7.6), (8.2, 9.5)],
    [(-0.9, -10.5), (-1.0, -0.4), (-6.8, 1.8), (-7.5, 3.0), (3.1, -9.9), (7.0, -0.3), (3.1, 7.9), (4.4, 9.6)],
    [(-0.6, -10.1), (0.9, 0.3), (-4.0, 4.0), (-4.4, 5.8), (3.3, -10.4), (4.2, 0.0), (-0.5, 7.6), (0.5, 9.6)],
    [(-0.5, -10.1), (2.5, -0.1), (-1.3, 5.9), (-1.2, 8.0), (3.1, -11.2), (-0.1, -2.2), (-3.3, 7.0), (-3.3, 9.1)],
    [(-0.2, -11.9), (4.2, -2.4), (5.1, 7.9), (6.2, 9.8), (2.2, -14.1), (-1.0, -5.7), (-6.7, 0.2), (-6.8, 2.2)],
    [(-0.9, -9.3), (3.1, 0.2), (0.9, 8.1), (2.2, 9.7), (2.3, -11.3), (1.9, -1.5), (-4.9, 1.1), (-5.6, 2.9)],
]
RUN_HIP_X = 131                           # the hips' middle (League's +0.5 game px from the pivot)
SKIN = [(2, 246, 250), (0, 203, 232), (0, 170, 193), (2, 135, 168)]
SHIN = [(57, 53, 72), (35, 31, 45)]
BRONZE = [(167, 115, 91), (147, 104, 85), (120, 85, 74)]
SKIRT = {(89, 7, 48), (144, 19, 71), (122, 12, 61), (61, 7, 36), (35, 4, 43)}
LEG_CUT = 63                              # design rows from here down: the legs go, the skirt stays
LEG_COLS = [(48, 81), (99, 122)]          # the near and the far leg's columns below LEG_CUT
HIPS = (84, 61)                           # the hips' middle in the design (under the skirt's top)
HALF_GAP = 5
THIGH_R, SHIN_R, KNEE_R = 4.4, 3.7, 3.0
FOOT = A[90:98, 112:123].copy()           # the design's far foot, toes to the right; the ankle at (4, 0)
FOOT_ANKLE = (4, 0)
DARKER = {(2, 246, 250): (0, 203, 232), (0, 203, 232): (0, 170, 193), (0, 170, 193): (2, 135, 168),
          (2, 230, 243): (0, 203, 232)}


def run_body():
    a = A.copy()
    H, W = a.shape[:2]
    gone = np.zeros((H, W), bool)
    for c0, c1 in LEG_COLS:
        for y in range(LEG_CUT, H):
            for x in range(c0, c1):
                if a[y, x, 3] and tuple(int(v) for v in a[y, x, :3]) not in SKIRT:
                    gone[y, x] = True
    sk = np.array([[a[y, x, 3] > 0 and tuple(int(v) for v in a[y, x, :3]) in SKIRT for x in range(W)] for y in range(H)])
    ring = ndimage.binary_dilation(sk, structure=np.ones((3, 3))) & (a[..., :3].astype(int).sum(2) < 40)
    a[gone & ~ring] = 0
    return a


def seg(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    side = (dx * (py - ay) - dy * (px - ax)) / (L2 ** 0.5)
    return ((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2) ** 0.5, side, t


def leg_layer(hip, knee, ankle, dark):
    lay = np.zeros((ROWS, COLS, 4), np.uint8)
    sk = SKIN[1:] if dark else SKIN[:3]
    ys, xs = [hip[1], knee[1], ankle[1]], [hip[0], knee[0], ankle[0]]
    for y in range(max(0, int(min(ys)) - 6), min(ROWS, int(max(ys)) + 6)):
        for x in range(max(0, int(min(xs)) - 6), min(COLS, int(max(xs)) + 7)):
            px, py = x + 0.5, y + 0.5
            d1, s1, _ = seg(px, py, hip, knee)
            d2, s2, t2 = seg(px, py, knee, ankle)
            col = None
            if d2 <= SHIN_R:
                if t2 < 0.16:
                    col = BRONZE[2] if dark else BRONZE[1]
                elif t2 > 0.9:
                    col = BRONZE[2]
                else:
                    col = SHIN[0] if s2 < -1.6 else SHIN[1]
            elif d1 <= THIGH_R:
                col = sk[0] if s1 < -1.4 else sk[1] if s1 < 1.6 else sk[2]
            if ((px - knee[0]) ** 2 + (py - knee[1]) ** 2) ** 0.5 <= KNEE_R:
                col = BRONZE[1] if dark else BRONZE[0]
            if col is not None:
                lay[y, x, :3] = col
                lay[y, x, 3] = 255
    op = lay[..., 3] > 0
    ring = ndimage.binary_dilation(op, structure=np.ones((3, 3))) & ~op
    lay[ring] = (*OUTLINE, 255)
    return lay


def paste_foot(can, ankle, dark):
    ax, ay = int(round(ankle[0])) - FOOT_ANKLE[0], int(round(ankle[1])) - FOOT_ANKLE[1]
    for y in range(FOOT.shape[0]):
        for x in range(FOOT.shape[1]):
            p = FOOT[y, x]
            if not p[3]:
                continue
            c = tuple(int(v) for v in p[:3])
            if dark:
                c = DARKER.get(c, c)
            yy, xx = ay + y, ax + x
            if 0 <= yy < ROWS and 0 <= xx < COLS:
                can[yy, xx] = (*c, 255)


def run_frame(body, j):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    hip_ref = ((j[0][0] + j[4][0]) / 2, (j[0][1] + j[4][1]) / 2)
    scale = STAND / (20.3 * SQ)          # League's hips stand 20.3 game px over the planted toe: STAND rows here

    def cv(p):
        return (RUN_HIP_X + (p[0] - hip_ref[0]) * SQ * scale, SOLE - (GROUND_Y - p[1]) * SQ * scale)

    hx, hy = cv(hip_ref)
    for side, dark in ((1, True), (0, False)):           # far under, near over
        k = side * 4
        hip = (hx + (HALF_GAP if side else -HALF_GAP), hy + 2)
        knee, ankle = cv(j[k + 1]), cv(j[k + 2])
        ankle = (ankle[0], min(ankle[1], SOLE - (FOOT.shape[0] - 1)))
        lay = leg_layer(hip, knee, ankle, dark)
        m = lay[..., 3] > 0
        can[m] = lay[m]
        paste_foot(can, ankle, dark)
    dx = int(round(hx - (DESIGN_AT[0] + HIPS[0])))
    dy = int(round(hy - (DESIGN_AT[1] + HIPS[1])))
    ys, xs = np.nonzero(body[..., 3] > 0)
    yy, xx = ys + DESIGN_AT[1] + dy, xs + DESIGN_AT[0] + dx
    ok = (yy >= 0) & (yy < ROWS) & (xx >= 0) & (xx < COLS)
    can[yy[ok], xx[ok]] = body[ys[ok], xs[ok]]
    can[SOLE + 1:] = 0
    return can


# ---------------------------------------------------------------------------------------------- the death
TIP_B, HAND_B = (1.0, 102.5), (55.0, 63.0)     # design B's spear: the blade's tip and the near hand


def dist_line(x, y, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return ((x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2) ** 0.5


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def place(can, part, x0, y_bottom):
    h, w = part.shape[:2]
    y0 = y_bottom - h + 1
    for y in range(h):
        for x in range(w):
            if part[y, x, 3] and 0 <= y0 + y < ROWS and 0 <= x0 + x < COLS:
                can[y0 + y, x0 + x] = part[y, x]


def down_to(a, bottom):
    ys, xs = np.nonzero(a[..., 3] > 0)
    out = np.zeros_like(a)
    out[ys + bottom - ys.max(), xs] = a[ys, xs]
    return out


def lying_parts():
    """Design B with design A's head, its spear and back spares off: (lying body, planted spear)."""
    b = B_.copy()
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[20:20 + b.shape[0], 60:60 + b.shape[1]] = b
    _, ox, oy = find_head(can, guess=(60 + 55, 20), rng=20)
    hy, hx = np.nonzero(HM)
    can[hy + oy, hx + ox] = HEAD[hy, hx].astype(np.uint8)
    b = can[20:20 + b.shape[0], 60:60 + b.shape[1]].copy()
    H, W = b.shape[:2]
    sp = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if not b[y, x, 3]:
                continue
            if x <= 49 and y >= 58:
                sp[y, x] = True
            elif 50 <= x <= 68 and dist_line(x + 0.5, y + 0.5, (50.0, 69.5), (66.5, 56.0)) <= 2.3 and not is_skin(b[y, x]):
                sp[y, x] = True
    body, spear = b.copy(), b.copy()
    body[sp] = 0
    spear[~sp] = 0
    body[:45, 85:] = 0                    # the spare spears on her back: under her when she lies
    return np.rot90(crop(body), 1).copy(), np.rot90(crop(spear), -1).copy()


def dead_frames(f):
    out = [down_to(f["hop_b_1"], SOLE), np.roll(A_on_canvas(), -3, axis=1), np.roll(down_to(f["hop_b_3"], SOLE - 1), -4, axis=1)]
    lying, spear = lying_parts()
    for lift in (2, 0, 0):
        can = np.zeros((ROWS, COLS, 4), np.uint8)
        x0 = PIV_X - lying.shape[1] // 2 - 6
        place(can, spear, x0 - spear.shape[1] + 14, SOLE + 6)
        place(can, lying, x0, SOLE - lift)
        can[SOLE + 1:] = 0
        out.append(can)
    return out


def A_on_canvas():
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[DESIGN_AT[1]:DESIGN_AT[1] + A.shape[0], DESIGN_AT[0]:DESIGN_AT[0] + A.shape[1]] = A
    return can


# ---------------------------------------------------------------------------------------------- tidy
def tidy(a):
    out = a.copy()
    op = out[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        for i, s in enumerate(sizes, 1):
            if s < SPECK:
                out[lab == i] = 0
    out, _, _ = G.complete_outline(out, color=OUTLINE, feet=SOLE)
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) > 2:
            continue
        for y, x in zip(ys, xs):
            nb = [tuple(int(v) for v in out[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= yy < ROWS and 0 <= xx < COLS and out[yy, xx, 3]]
            if nb:
                out[y, x] = Counter(nb).most_common(1)[0][0]
    out[SOLE + 1:] = 0
    return out


# ---------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write contact sheets here")
    a = ap.parse_args()
    cells = json.load(open(lp(os.path.join(CODEX, "cells.json")), encoding="utf-8"))
    tags = {}
    for fr in cells["frames"]:
        tags.setdefault(fr["tag"], []).append(fr)
    frames = {}
    for tag, lst in tags.items():
        if tag in ("run", "dead"):
            continue
        for fr in lst:
            name = f"{tag}_{fr['index'] + 1}"
            f = rgba(os.path.join(CODEX, f"kalista_{name}_1x.png"))
            if name in SCALE:
                f = shrink(f, SCALE[name])
            frames[name], _ = paste_head(f)
    body = run_body()
    for i, j in enumerate(JOINTS):
        frames[f"run_{i + 1}"] = run_frame(body, j)
    for i, f in enumerate(dead_frames(frames)):
        frames[f"dead_{i + 1}"] = f
    os.makedirs(lp(OUT), exist_ok=True)
    table = {}
    for tag, lst in tags.items():
        table[tag] = []
        for fr in lst:
            name = f"{tag}_{fr['index'] + 1}"
            out = tidy(frames[name])
            Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
            table[tag].append({"file": f"{name}.png", "ms": fr["ms"]})
    with open(lp(os.path.join(OUT, "frames.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"canvas": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE], "tags": table}, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for tag, lst in table.items():
            ims = [Image.open(lp(os.path.join(OUT, e["file"]))).convert("RGBA") for e in lst]
            S = Image.new("RGBA", (COLS * len(ims), ROWS), (92, 98, 86, 255))
            for i, im in enumerate(ims):
                S.alpha_composite(im, (i * COLS, 0))
            S.resize((S.width * 3, S.height * 3), Image.NEAREST).save(os.path.join(a.review, f"kalista_{tag}.png"))
    print("frames:", ", ".join(f"{t} {len(l)}" for t, l in table.items()))


if __name__ == "__main__":
    main()
