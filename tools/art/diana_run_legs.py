#!/usr/bin/env python3
"""Diana's run legs: the idle's legs on League's run poses, under Codex's upper body.

    python tools/art/diana_run_legs.py [--src assets/source/diana/codex_run] [--out assets/source/diana/run_legs]
    python tools/art/diana_run_legs.py --joints-from <native_pose anchors json>    # refresh lol_run_leg_joints.json

The user, after five Codex rounds on the run's legs: "你能好好做吗 待机的腿和跑步的腿都不一样", "要用待机的腿啊 跑步的
腿在魔改吗？", "还有走路姿势和英雄联盟一样吗". So the legs are no longer Codex's:
  - pose: League's own run. assets/source/diana/lol_run_leg_joints.json holds League's hip, knee, ankle (*_Foot) and
    toe joints per run frame (tools/lol/native_pose.py's "anchor", one joint at a time, through the references'
    camera; L_* is the near leg). They sit above the chibi-scaled legs of the render, so only each bone's direction
    is used: per frame and leg the thigh, shin and foot point League's way, laid out with the idle's lengths (THIGH,
    SHIN, FOOT) from hips under the skirt, HIP_GAP apart like League's.
  - look: the idle's leg, piece by piece (idle frame 1, rows 71-79): navy leggings, a gold knee guard, a silver
    greave down the shin, a navy boot, one outline round the whole leg; the far leg a shade darker and drawn first.
  - each frame then moves up or down so its lowest sole is on the soles row (League's frames do, "flat"): the body
    bobs -2..+1 rows.
Codex's frame (codex_run/, its align5) keeps everything down to KEEP_ROW, the skirt's hem below it and the blade's
arc left of BLADE_X; CLEAN first takes out the leftovers that looked odd (frames 4, 6, 8: a stick, specks and a cuff
under the right hand; frames 4 and 8: a dark line hanging under the left hand, League's inner blade edge drawn dark).
Writes <out>/native/diana_run_1x.png and <out>/manifest.json (the source's) for tidy_diana.py --run.
"""
import argparse
import json
import math
import os
import shutil

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SOURCE = os.path.join(ROOT, "assets", "source")
JOINTS = os.path.join(SOURCE, "diana", "lol_run_leg_joints.json")
SOLES = 79
THIGH, SHIN, FOOT = 7.5, 6.0, 3.5          # the idle's: hip ~64 -> knee ~71.5 -> ankle ~77.5, toe ~3.5 ahead
SOLE_BELOW = 1.5
HIP_GAP = 3.5                              # League's near hip is ~3.5 px in front of the far one in all 8 frames
HIP_Y = 63.5
R_THIGH, R_SHIN, R_BOOT = 1.15, 1.0, 1.15
KEEP_ROW, BLADE_X = 62, 27
INK = (0x0A, 0x04, 0x12, 255)
NAVY, NAVY_D = (0x33, 0x3B, 0x63, 255), (0x22, 0x23, 0x3C, 255)
SILVER, SILVER_D = (0xB8, 0xBF, 0xC7, 255), (0x60, 0x63, 0x7E, 255)
GOLD, GOLD_D = (0xF3, 0xD9, 0x8D, 255), (0xA7, 0x80, 0x4A, 255)
SKIRT = {(0x26, 0x46, 0x48), (0x1F, 0x50, 0x57), (0x50, 0x59, 0x45), (0x81, 0x87, 0x68), (0xB9, 0xB6, 0x90),
         (0xA7, 0x80, 0x4A), (0xF3, 0xD9, 0x8D)}
CLEAN = {4: [(54, 62), (55, 62), (56, 62), (28, 61), (29, 61), (27, 62), (28, 62), (27, 63), (28, 63), (27, 64), (28, 64),
             (27, 65), (27, 66)],
         6: [(53, 62)],
         8: [(52, 62), (53, 62), (54, 62), (55, 62), (51, 63), (53, 63), (54, 63), (51, 64), (26, 61), (27, 61), (25, 62),
             (26, 62), (28, 62), (25, 63), (25, 64), (25, 65), (25, 66)]}


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def unit(a, b):
    v = np.array(b, float) - np.array(a, float)
    return v / (np.linalg.norm(v) or 1)


def waist_x(f):
    xs = [x for y in range(58, 61) for x in range(32, 53) if f[y, x, 3]]
    return (min(xs) + max(xs)) / 2


def chain(J, f):
    """{side: [hip, knee, ankle, toe]} from League's bone directions with the idle's lengths."""
    cx = waist_x(f)
    legs = {}
    for side, dx in (("L", HIP_GAP / 2), ("R", -HIP_GAP / 2)):
        hip = np.array([cx + dx, HIP_Y])
        knee = hip + THIGH * unit(J[f"{side}_Hip"], J[f"{side}_Knee"])
        ankle = knee + SHIN * unit(J[f"{side}_Knee"], J[f"{side}_Foot"])
        toe = ankle + FOOT * unit(J[f"{side}_Foot"], J[f"{side}_Toe"])
        legs[side] = [hip, knee, ankle, toe]
    return legs


def seg_mask(h, w, a, b, r):
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs + 0.5, ys + 0.5
    vx, vy = b[0] - a[0], b[1] - a[1]
    t = np.clip(((px - a[0]) * vx + (py - a[1]) * vy) / max(vx * vx + vy * vy, 1e-6), 0, 1)
    d = np.hypot(px - (a[0] + t * vx), py - (a[1] + t * vy))
    return d <= r, t


def draw_leg(h, w, hip, knee, ankle, toe, far):
    fill = np.zeros((h, w, 4), np.uint8)
    m_thigh, _ = seg_mask(h, w, hip, knee, R_THIGH)
    m_shin, t_shin = seg_mask(h, w, knee, ankle, R_SHIN)
    m_boot, _ = seg_mask(h, w, ankle, toe, R_BOOT)
    m_ank, _ = seg_mask(h, w, ankle, ankle, R_BOOT + 0.2)
    fill[m_thigh] = NAVY_D if far else NAVY
    fill[m_shin] = SILVER
    fill[m_shin & (t_shin > (0.5 if far else 0.8))] = SILVER_D
    fill[m_boot | m_ank] = NAVY_D if far else NAVY
    m_knee, _ = seg_mask(h, w, knee, knee, 1.05)
    fill[m_knee] = GOLD_D if far else GOLD
    kx, ky = int(knee[0]), int(knee[1])
    if not far and 0 <= ky + 1 < h and 0 <= kx < w and fill[ky + 1, kx, 3]:
        fill[ky + 1, kx] = GOLD_D
    op = fill[..., 3] > 0
    p = np.pad(op, 1)
    fill[(p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~op] = INK
    return fill


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]


def upper_layer(f):
    up = np.zeros_like(f)
    up[:KEEP_ROW + 1] = f[:KEEP_ROW + 1]
    up[KEEP_ROW + 1:, :BLADE_X] = f[KEEP_ROW + 1:, :BLADE_X]
    for y in range(KEEP_ROW + 1, KEEP_ROW + 5):
        for x in range(BLADE_X, f.shape[1]):
            if f[y, x, 3] and tuple(int(v) for v in f[y, x, :3]) in SKIRT and (y == KEEP_ROW + 1 or up[y - 1, x, 3]):
                up[y, x] = f[y, x]
    return up


def build(run, joints):
    out = np.zeros_like(run)
    bob = []
    for k in range(8):
        y0, x0 = (k // 4) * 96, (k % 4) * 96
        f = run[y0:y0 + 96, x0:x0 + 96].copy()
        for x, y in CLEAN.get(k + 1, []):
            f[y, x] = 0
        legs = np.zeros_like(f)
        for side, pts in sorted(chain(joints[k], f).items(), key=lambda kv: kv[0] != "R"):   # far leg first
            over(legs, draw_leg(96, 96, *pts, far=side == "R"))
        dy = SOLES - int(np.nonzero(legs[..., 3].any(1))[0].max())
        frame = np.zeros_like(f)
        over(frame, legs)
        over(frame, upper_layer(f))
        frame = np.roll(frame, dy, 0)
        if dy < 0:
            frame[dy:] = 0
        elif dy > 0:
            frame[:dy] = 0
        out[y0:y0 + 96, x0:x0 + 96] = frame
        bob.append(dy)
    return out, bob


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(SOURCE, "diana", "codex_run"))
    ap.add_argument("--out", default=os.path.join(SOURCE, "diana", "run_legs"))
    ap.add_argument("--joints-from", help="native_pose anchor results ([{joint: [x, y]} per frame]) to store first")
    a = ap.parse_args()
    if a.joints_from:
        with open(a.joints_from, encoding="utf-8") as f:
            frames = json.load(f)
        with open(lp(JOINTS), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"_note": "League's Diana run, leg joints per frame (diana_run@0..875 every 125 ms) from "
                                "tools/lol/native_pose.py's anchor with assets/source/diana/poses.json; L_* = near leg",
                       "frames": frames}, f, indent=1)
    with open(lp(JOINTS), encoding="utf-8") as f:
        joints = json.load(f)["frames"]
    with open(lp(os.path.join(a.src, "manifest.json")), encoding="utf-8") as f:
        man = json.load(f)
    run = np.asarray(Image.open(lp(os.path.join(a.src, man["native_file"]))).convert("RGBA"))
    out, bob = build(run, joints)
    os.makedirs(lp(os.path.join(a.out, "native")), exist_ok=True)
    Image.fromarray(out).save(lp(os.path.join(a.out, "native", "diana_run_1x.png")))
    man = dict(man, native_file="native/diana_run_1x.png",
               note="legs rebuilt by tools/art/diana_run_legs.py from the idle's legs on League's run poses")
    with open(lp(os.path.join(a.out, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    print("run legs rebuilt; the body moves", bob)


if __name__ == "__main__":
    main()
