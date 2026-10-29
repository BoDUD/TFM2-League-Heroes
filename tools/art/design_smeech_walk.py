#!/usr/bin/env python3
"""Smeech's upright walk, one body in all eight frames: hd/pose_run1-8.png (+ .json) for rig_smeech.

    python tools/art/design_smeech_walk.py [--sheet DIR]     # writes the eight frames (--sheet: also a 6x review)

Codex drew run1-8 one by one (assets/source/smeech/codex_poses), each with its own body: the torso, the arms and the
stilts a different size and bend in every frame, so the walk swelled and shrank under the design's head (the user,
2026-10-29: 「走路时身体和头有点不协调」「还是变形吧 你能好好修吗」; a crouched walk on the idle instead was refused:
「这个走路姿势还不如之前」). So the upright walk keeps Codex's look but is built from one frame's parts:
  - the upper body is run5's (design_smeech_poses: the design's head on Codex's chin; the cleanest torso and arms of the
    eight, no claw by the face) - everything down to the shorts' last row and the far claw's tips - the same in every
    frame;
  - each leg is drawn the way league_caitlyn's run was (run-legs-caitlyn-way: one leg in eight phases, only the ankle
    placed, the knee solved at one fixed thigh / shin length, the far leg the same phases four on and a step darker):
    run5's own thigh and shin lengths, its rods in its brass shades (a 2-square core lit from the upper left, the outline
    round it), its knee joint and its shoe (with the ankle joint) pasted whole and flat at the knee and the ankle;
  - the stance leg's foot is on the ground (rig_smeech stands every frame on its lowest shoe), so the body bobs with
    the stance leg: lowest when both feet are down, highest over the straight leg.
Each frame's json keeps where its picture's top-left square is on the pose pack's grid (grid_at, run5's) and where the
head's box is (head_at), as design_smeech_poses writes them.
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "smeech", "hd")
BASE = "run5"
# run5's squares (its cropped picture, read at 11-22x, 2026-10-29)
UPPER_ROWS = 88                   # the upper body: every square down to the shorts' last row ...
CLAW = (27, 92)                   # ... and the far claw's tips (columns up to 27) down to row 92
# where each thigh leaves the shorts: close together under them (run5's own thighs leave 9.5 squares apart, which
# crossed the legs into an X whenever the near foot was behind and the far one ahead; league_caitlyn's hips sit close)
HIPS = {"far": (40.0, 89.0), "near": (43.5, 89.5)}
KNEE = (49.5, 95.0)               # the near knee joint's middle (its sprite: KNEE_BOX)
KNEE_BOX = (45, 90, 54, 100)      # x0, y0, x1, y1 (ends exclusive)
ANKLE = (55.5, 115.0)             # where the near shin meets the ankle joint (the shoe sprite's anchor)
SHOE_BOX = (53, 114, 74, 128)     # the ankle joint and the shoe, flat
THIGH = math.dist(HIPS["near"], KNEE)       # 6.5 squares
SHIN = math.dist(KNEE, ANKLE)               # 20.9
# one leg's ankle in eight phases: (squares ahead of its hip, squares below it); 0-4 planted (contact, under the
# body, push-off: the leg straight or nearly), 5-7 swinging forward with the foot up and the knee bent ahead. The far
# leg runs four phases on, so 0 and 4 are both feet down
REACH = THIGH + SHIN
# (the swinging foot kicked up behind the planted one, not over it: two shoes stacked read as one tall boot)
PHASES = [(12.0, None), (6.0, None), (0.0, None), (-6.0, None), (-12.0, None), (-14.0, 18.5), (-2.0, 15.0), (10.0, 21.0)]
PHASES = [(x, y if y is not None else math.sqrt(REACH ** 2 - x ** 2) - 0.05) for x, y in PHASES]
INK = (7, 6, 10)
LIGHT, MID, DARK, DARKER = (227, 145, 42), (184, 105, 31), (139, 78, 28), (89, 47, 22)
CORE, RIM = 0.8, 1.7              # squares from a rod's line: its brass, then its outline
BAND = 7                          # a dark joint ring every this many squares along a rod
FAR_SHADE = 0.78                  # the far leg a step darker


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(name):
    return np.asarray(Image.open(lp(os.path.join(HD, name))).convert("RGBA")).copy()


def knee_of(hip, ankle):
    """The knee for a leg from `hip` to `ankle` with THIGH and SHIN, bent forward (to the image right)."""
    hx, hy = hip
    ax, ay = ankle
    d = min(max(math.dist(hip, ankle), abs(THIGH - SHIN) + 1e-3), REACH - 1e-3)
    phi = math.atan2(ay - hy, ax - hx)
    a = math.acos((THIGH ** 2 + d ** 2 - SHIN ** 2) / (2 * THIGH * d))
    ks = [(hx + THIGH * math.cos(phi + s * a), hy + THIGH * math.sin(phi + s * a)) for s in (1, -1)]
    return max(ks, key=lambda k: k[0])


def rod(can, p, q, shade=1.0):
    """A brass rod from p to q (squares) onto can: its outline first, then its core, lit from the upper left."""
    (px, py), (qx, qy) = p, q
    L = max(math.dist(p, q), 1e-6)
    ux, uy = (qx - px) / L, (qy - py) / L
    nx, ny = -uy, ux
    if nx + ny > 0:                       # the normal pointing up-left (toward the light)
        nx, ny = -nx, -ny
    x0, x1 = int(math.floor(min(px, qx) - 3)), int(math.ceil(max(px, qx) + 3))
    y0, y1 = int(math.floor(min(py, qy) - 3)), int(math.ceil(max(py, qy) + 3))
    for y in range(max(0, y0), min(can.shape[0], y1 + 1)):
        for x in range(max(0, x0), min(can.shape[1], x1 + 1)):
            cx, cy = x + 0.5 - px, y + 0.5 - py
            t = max(0.0, min(L, cx * ux + cy * uy))
            dist = math.hypot(cx - t * ux, cy - t * uy)
            if dist <= CORE:
                s = cx * nx + cy * ny
                c = LIGHT if s > 0.15 else MID
                if t % BAND < 1.0 and 1.5 < t < L - 1.5:
                    c = DARK
                can[y, x] = (*[int(v * shade) for v in c], 255)
            elif dist <= RIM and can[y, x, 3] == 0:
                can[y, x] = (*INK, 255)


def paste(can, sprite, at, shade=1.0):
    """A sprite's opaque squares onto can with its top-left at `at`, shaded."""
    ys, xs = np.nonzero(sprite[..., 3] > 0)
    ty, tx = ys + at[1], xs + at[0]
    ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
    px = sprite[ys[ok], xs[ok]].astype(float)
    ink = np.all(px[:, :3] == INK, axis=1)
    px[~ink, :3] *= shade
    can[ty[ok], tx[ok]] = px.astype(np.uint8)


def leg(can, hip, phase, knee_spr, shoe_spr, shade):
    ax, ay = PHASES[phase]
    ankle = (hip[0] + ax, hip[1] + ay)
    knee = knee_of(hip, ankle)
    rod(can, hip, knee, shade)
    rod(can, knee, ankle, shade)
    paste(can, shoe_spr, (round(ankle[0] - (ANKLE[0] - SHOE_BOX[0])), round(ankle[1] - (ANKLE[1] - SHOE_BOX[1]))), shade)
    paste(can, knee_spr, (round(knee[0] - (KNEE[0] - KNEE_BOX[0])), round(knee[1] - (KNEE[1] - KNEE_BOX[1]))), shade)


def base_pose():
    """run5 as design_smeech_poses reads it (the design's head on Codex's chin): computed here, never read back from
    hd/pose_run5.png, which this script writes."""
    import sys
    sys.path.insert(0, HERE)
    import design_smeech_poses as S
    d = S.design()
    t, tm, at = S.head_template(d)
    return S.pose(BASE, d, t, tm, at, S.hat_colours(d), S.head_only(d, t, tm, at))


def frames():
    base, meta = base_pose()
    H, W = base.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    upper = (base[..., 3] > 0) & ((yy <= UPPER_ROWS) | ((xx <= CLAW[0]) & (yy <= CLAW[1])))
    knee_spr = base[KNEE_BOX[1]:KNEE_BOX[3], KNEE_BOX[0]:KNEE_BOX[2]].copy()
    shoe_spr = base[SHOE_BOX[1]:SHOE_BOX[3], SHOE_BOX[0]:SHOE_BOX[2]].copy()
    pad = 24
    out = []
    for i in range(8):
        can = np.zeros((H + pad * 2, W + pad * 2, 4), np.uint8)
        off = lambda p: (p[0] + pad, p[1] + pad)
        leg(can, off(HIPS["far"]), (i + 4) % 8, knee_spr, shoe_spr, FAR_SHADE)
        near = np.zeros_like(can)
        leg(near, off(HIPS["near"]), i, knee_spr, shoe_spr, 1.0)
        m = near[..., 3] > 0
        can[m] = near[m]
        up = np.zeros_like(can)
        up[pad:pad + H, pad:pad + W][upper] = base[upper]
        m = up[..., 3] > 0
        can[m] = up[m]
        ys, xs = np.nonzero(can[..., 3] > 0)
        x0, y0 = xs.min(), ys.min()
        fig = can[y0:ys.max() + 1, x0:xs.max() + 1].copy()
        hx, hy = meta["head_at"]
        gx, gy = meta["grid_at"]
        out.append((fig, {"head_at": [int(hx + pad - x0), int(hy + pad - y0)],
                          "grid_at": [int(gx - pad + x0), int(gy - pad + y0)]}))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    fr = frames()
    if a.sheet:
        z = 6
        cells = []
        for fig, _ in fr:
            bg = np.zeros(fig.shape, np.uint8)
            bg[...] = (200, 200, 200, 255)
            m = fig[..., 3] > 0
            bg[m] = fig[m]
            cells.append(Image.fromarray(bg).resize((fig.shape[1] * z, fig.shape[0] * z), Image.NEAREST))
        W = max(c.width for c in cells) + 10
        H = max(c.height for c in cells)
        sheet = Image.new("RGB", (W * 4, H * 2), (255, 255, 255))
        for k, c in enumerate(cells):
            sheet.paste(c, ((k % 4) * W, (k // 4) * H + H - c.height))
        os.makedirs(lp(a.sheet), exist_ok=True)
        sheet.save(lp(os.path.join(a.sheet, "smeech_walk.png")))
        print(os.path.join(a.sheet, "smeech_walk.png"), sheet.size)
        return
    for k, (fig, meta) in enumerate(fr, 1):
        Image.fromarray(fig).save(lp(os.path.join(HD, f"pose_run{k}.png")))
        with open(lp(os.path.join(HD, f"pose_run{k}.json")), "w", encoding="utf-8") as fh:
            json.dump(meta, fh)
    print(len(fr), "walk frames ->", HD)


if __name__ == "__main__":
    main()
