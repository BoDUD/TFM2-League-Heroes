#!/usr/bin/env python3
"""Quinn's legs drawn on League's bones, frame by frame - league_riven's way (tools/art/rig_riven_hd.py drawn_frame,
from rig_fiora_hd): thigh and shin bands of constant width coloured across by a row of the idle's own leg (its thigh
row, its shin row), the idle's own boot stamped whole at the ankle (never turned, slid or resized), an outline ring
round the bands; each leg's thigh points the way League's thigh points in that frame and its shin the way League's
shin does (clamped), from hips that stay where the idle has them under her skirt; the whole figure is then set on the
ground by its lowest boot (or as high as League's feet leave the floor), the body drawn over the thighs' tops.

    python tools/art/quinn_legs.py --joints <dir>/quinn_joints.json --check DIR   # the idle's pose redrawn + every run frame, 8x

The user, 2026-10-19, after legs posed from the idle's own (「英雄联盟里面腿部动作一直在变换的 我们的不变」), two Codex leg
packs (「腿部各种变形 这叫改好了？」) and my own made-up run phases: 「你看看重做的锐雯怎么做的吧 别人做的很好」.
The joints: tools/lol/league_joints.py assets/source/quinn/poses.json (League's chibi Quinn through the spec's camera,
game px, x forward, y down; the r_* leg is the near one - its depth is the larger).
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "quinn", "hd")
CUT_ROW = 35                        # the idle's rows from here down (right of CAPE_X) are her legs; above: the body
CAPE_X = 7
INK = (0x09, 0x00, 0x13)
PPU = 1.3
# each leg measured on hd/idle.png (square edges): the hip under the skirt, the knee, the ankle; its thigh and shin rows
# (inner colours, left to right), the knee plate squares on its front, its boot (rows / cols, the outline included)
LEGS = {
    "near": dict(hip=(11.5, 34.5), knee=(10.5, 39.0), ankle=(10.0, 43.5), thigh_row=(37, 10, 12), shin_row=(41, 9, 10),
                 plate=[0xfacc4d, 0xf5b52e], boot=((44, 48), (8, 13)), side="r"),
    "far": dict(hip=(19.5, 35.0), knee=(19.5, 41.0), ankle=(21.0, 44.0), thigh_row=(38, 18, 20), shin_row=(42, 20, 21),
                plate=[0xfcdf68, 0xf5b52e], boot=((44, 48), (19, 26)), side="l"),
}
SHIN_BACK, SHIN_FWD = -75.0, 60.0   # degrees from straight down the shin may point (rig_riven_hd: -70 / 50)
GROUND = 49                         # the idle's soles' bottom edge


def load(name):
    return np.asarray(Image.open(os.path.join(SRC, name)).convert("RGBA")).copy()


def rgb(h):
    return np.array(((h >> 16) & 255, (h >> 8) & 255, h & 255, 255), np.uint8)


def parts(idle):
    """{"near" | "far": dict(thigh / shin profile, thigh / shin lengths, boot (offsets from the ankle, colours), drop: the
    boot's bottom under the ankle, plate)} from the idle's squares."""
    out = {}
    for key, L in LEGS.items():
        y, a, b = L["thigh_row"]
        thigh = idle[y, a:b + 1].copy()
        y, a, b = L["shin_row"]
        shin = idle[y, a:b + 1].copy()
        (r0, r1), (c0, c1) = L["boot"]
        ys, xs = np.nonzero(idle[r0:r1 + 1, c0:c1 + 1, 3] > 0)
        ys, xs = ys + r0, xs + c0
        ax, ay = L["ankle"]
        boot = (np.stack([xs + 0.5 - ax, ys + 0.5 - ay], 1), idle[ys, xs])
        out[key] = dict(thigh=thigh, shin=shin, boot=boot, drop=float(ys.max() + 1 - ay),
                        thigh_len=math.dist(L["hip"], L["knee"]), shin_len=math.dist(L["knee"], L["ankle"]),
                        plate=[rgb(h) for h in L["plate"]])
    return out


def band(cells, A, B, profile):
    """The squares within half the profile's width of the segment A -> B, each the profile's colour at its place across
    the band, left to right on screen for a bone pointing down (rig_riven_hd.band)."""
    n_ = len(profile)
    hw = n_ / 2.0 - 0.01
    vx, vy = B[0] - A[0], B[1] - A[1]
    n = math.hypot(vx, vy) or 1e-9
    for y in range(int(math.floor(min(A[1], B[1]))) - n_ - 1, int(math.ceil(max(A[1], B[1]))) + n_ + 1):
        for x in range(int(math.floor(min(A[0], B[0]))) - n_ - 1, int(math.ceil(max(A[0], B[0]))) + n_ + 2):
            px, py = x + 0.5, y + 0.5
            t = ((px - A[0]) * vx + (py - A[1]) * vy) / n
            if t < -0.5 or t > n + 0.5:
                continue
            sd = (px - A[0]) * (vy / n) - (py - A[1]) * (vx / n)
            if abs(sd) <= hw:
                cells[(x, y)] = profile[max(0, min(n_ - 1, int(math.floor(-sd + n_ / 2.0))))]


def leg_cells(part, H, K, A):
    """{(x, y): colour} of one leg - thigh H->K, shin K->A, the knee plate on the knee's front, the boot at A - and the
    bands' own squares (their outline ring)."""
    cells = {}
    band(cells, H, K, part["thigh"])
    band(cells, K, A, part["shin"])
    vx, vy = A[0] - K[0], A[1] - K[1]
    n = math.hypot(vx, vy) or 1e-9
    ux, uy = vx / n, vy / n
    fx, fy = (uy, -ux) if uy > 0 else (-uy, ux)      # across the shin toward its front (image right for a shin down)
    if fx < 0:
        fx, fy = -fx, -fy
    for k, c in enumerate(part["plate"]):          # two squares down the knee's front
        x = int(math.floor(K[0] + fx * 0.8 + ux * (k - 0.3)))
        y = int(math.floor(K[1] + fy * 0.8 + uy * (k - 0.3)))
        cells[(x, y)] = c
    banded = set(cells)
    off, cols = part["boot"]
    for x, y, c in zip(np.floor(A[0] + off[:, 0]).astype(int), np.floor(A[1] + off[:, 1]).astype(int), cols):
        cells[(int(x), int(y))] = c
    return cells, banded


def draw_legs(can, geo, P):
    """Both legs on can: the far one first, the near one and its ring over it."""
    for key in ("far", "near"):
        H, K, A = geo[key]
        cells, banded = leg_cells(P[key], H, K, A)
        ring = set()
        for (x, y) in banded:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in cells:
                    ring.add(q)
        for (x, y) in ring:
            if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
                can[y, x] = (*INK, 255)
        for (x, y), c in cells.items():
            if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
                can[y, x] = c


def geometry(j, P):
    """{"near" | "far": (hip, knee, ankle)} in idle squares from League's joints j: each thigh along League's
    hip -> knee, each shin along League's knee -> foot, clamped to SHIN_BACK..SHIN_FWD from straight down."""
    geo = {}
    for key, L in LEGS.items():
        s = L["side"]
        h, k, f = (np.array(j[f"{s}_{n}"][:2], float) for n in ("hip", "knee", "foot"))
        t = (k - h) / (np.linalg.norm(k - h) or 1)
        ang = max(SHIN_BACK, min(SHIN_FWD, math.degrees(math.atan2(f[0] - k[0], f[1] - k[1]))))
        H = np.array(L["hip"], float)
        K = H + t * P[key]["thigh_len"]
        A = K + P[key]["shin_len"] * np.array((math.sin(math.radians(ang)), math.cos(math.radians(ang))))
        geo[key] = (H, K, A)
    return geo


def body(idle):
    b = idle.copy()
    yy, xx = np.mgrid[0:idle.shape[0], 0:idle.shape[1]]
    b[(yy >= CUT_ROW) & (xx >= CAPE_X)] = 0
    return b


def frame(idle, P, j, joints, pad=(12, 12, 10, 4), lunge=0.5, air=True, body_img=None, ref=None):
    """One frame on drawn legs: the body (the idle without its legs, or body_img) moved forward / back with League's
    pelvis (lunge x its travel from `ref`'s pelvis - the tag's first frame, default the design pose - in game px x PPU),
    the legs from j, the whole set on the ground by its lowest boot, or lifted as far as League's lower foot is off the
    floor (air). -> (canvas, the body's (0, 0) on it)."""
    left, right, top, bottom = pad
    Hh, Ww = idle.shape[0] + top + bottom, idle.shape[1] + left + right
    d = joints["design"]
    r = ref or d
    dx = (j["pelvis"][0] - r["pelvis"][0]) * PPU * lunge
    geo = geometry(j, P)
    low = max(geo[k][2][1] + P[k]["drop"] for k in geo)
    lift = 0.0
    if air:
        lf = min(-j["l_foot"][1], -j["r_foot"][1]) - min(-d["l_foot"][1], -d["r_foot"][1])
        lift = max(0.0, lf) * PPU
    dy = GROUND - lift - low
    ox, oy = int(round(left + dx)), int(round(top + dy))
    can = np.zeros((Hh, Ww, 4), np.uint8)
    geo = {k: tuple(v + np.array((ox, oy)) for v in g) for k, g in geo.items()}
    draw_legs(can, geo, P)
    b = body_img if body_img is not None else body(idle)
    lay = np.zeros_like(can)
    y0, x0 = max(0, oy), max(0, ox)
    sub = b[y0 - oy:Hh - oy, x0 - ox:Ww - ox]
    lay[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]] = sub
    m = lay[..., 3] > 0
    can[m] = lay[m]
    return can, (ox, oy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", required=True)
    ap.add_argument("--check", required=True)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args()
    os.makedirs(a.check, exist_ok=True)
    idle = load("idle.png")
    P = parts(idle)
    joints = json.load(open(a.joints, encoding="utf-8"))
    z = 8
    rows = joints["tags"][a.tag]
    cans = [frame(idle, P, joints["design"], joints, air=False)[0]]
    cans += [frame(idle, P, fr["j"], joints, air=False, ref=rows[0]["j"])[0] for fr in rows]
    ref = np.zeros_like(cans[0])
    ref[10:10 + idle.shape[0], 12:12 + idle.shape[1]] = idle
    tiles = []
    for c in [ref] + cans:
        im = Image.new("RGBA", (c.shape[1] * z, c.shape[0] * z), (200, 200, 200, 255))
        im.alpha_composite(Image.fromarray(np.repeat(np.repeat(c, z, 0), z, 1)))
        tiles.append(im)
    for g, part in (("a", tiles[:5]), ("b", tiles[5:])):
        W = sum(t.width + 8 for t in part)
        sh = Image.new("RGB", (W, part[0].height), (255, 255, 255))
        x = 0
        for t in part:
            sh.paste(t.convert("RGB"), (x, 0))
            x += t.width + 8
        sh.save(os.path.join(a.check, f"legs_{a.tag}_{g}.png"))
    frs = []
    for c in cans[1:]:
        g = Image.fromarray(c)
        bg = Image.new("RGBA", g.size, (96, 112, 96, 255))
        bg.alpha_composite(g)
        frs.append(bg.convert("RGB").resize((g.width * 4, g.height * 4), Image.NEAREST))
    frs[0].save(os.path.join(a.check, f"legs_{a.tag}.gif"), save_all=True, append_images=frs[1:],
                duration=int(rows[0]["ms"]), loop=0)


if __name__ == "__main__":
    main()
