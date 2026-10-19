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
CUT_ROW = 46                        # the idle's rows from here down (right of CAPE_X) are her legs; above: the body
CAPE_X = 10
INK = (0x09, 0x00, 0x13)
PPU = 2.0                           # the PPU 2.0 redraw (assets/source/quinn/hd2, tools/art/design_quinn_grid.py)
# each leg measured on hd/idle.png (square edges): the hip under the skirt (row 43, hidden), the knee, the ankle; its thigh and shin rows
# (inner colours, left to right: the near thigh's gold trim and the shins' gold stripe in front), the knee plate squares
# on its front, its boot (rows / cols, the outline included)
LEGS = {
    "near": dict(hip=(15.5, 43.0), knee=(14.5, 56.5), ankle=(13.5, 66.0), thigh_row=(46, 13, 19), shin_row=(60, 13, 15),
                 plate=[0xfde46c, 0xfac747], boot=((66, 73), (10, 19)), side="r"),
    "far": dict(hip=(27.5, 43.5), knee=(29.5, 56.5), ankle=(32.0, 66.0), thigh_row=(55, 27, 31), shin_row=(60, 30, 32),
                plate=[0xfded8b, 0xf4ac28], boot=((65, 74), (30, 41)), side="l"),
}
# both legs the same length, the idle's own split of it: from the hip under the skirt (rows 30-45 cover it; the body
# is drawn over the thighs' tops) to the knee plate at row 56-58 and a shorter shin to the ankle at 66, the brown boot
# shaft with its gold stripe in front (row 60). Standing straight the ankles land where the idle's are; a leg swung
# forward or back shows the thigh the skirt hid - her stride opens as League's instead of shuffling under her. (On the
# PPU 1.3 design at thigh 7 / shin 6.5 the knees rode 2-3 rows above the idle's and the shins ran long: the user,
# 2026-10-19, 「奎因腿部还是有轻微的变形」; this split keeps the design's own.)
THIGH_LEN, SHIN_LEN = 13.5, 9.0
KNEE_R = 1.8                        # the knee rounded: squares this close to the knee joint take the thigh's middle colour
BOOT_TURN = 55.0                    # a shin pointing further than this back / forward from straight down carries its boot a
                                    # quarter turn round (toe down / up), the boot's shaft along the shin
SHIN_BACK, SHIN_FWD = -130.0, 60.0  # degrees from straight down the shin may point: back far enough for the run's
# heel kicked up behind (League's run reaches -110 to -135; at -75 the kick was cut off and the run shuffled)
GROUND = 75                         # the idle's soles' bottom edge


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
                        thigh_len=THIGH_LEN, shin_len=SHIN_LEN, plate=[rgb(h) for h in L["plate"]])
    return out


def band(cells, A, B, profile):
    """The squares within half the profile's width of the segment A -> B, each the profile's colour at its place across
    the band, left to right on screen for a bone pointing down - the source row's back edge at the back, its front
    edge (the gold stripe) in front (rig_riven_hd.band laid them right to left: the stripe ran down her calves)."""
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
                cells[(x, y)] = profile[max(0, min(n_ - 1, int(math.floor(sd + n_ / 2.0))))]


def boot_offsets(part, rot=0):
    """The boot's square offsets from the ankle, turned rot quarter turns clockwise on screen (1: the toe pointing down,
    the sole to the back - a kneeling leg's foot on its toes)."""
    off, cols = part["boot"]
    off = off.copy()
    for _ in range(rot % 4):                       # clockwise on screen (y down): (x, y) -> (-y, x)
        off = np.stack([-off[:, 1], off[:, 0]], 1)
    return off, cols


def boot_turn(K, A):
    """The boot's quarter turns clockwise for a shin K -> A: 1 pointing back past BOOT_TURN from straight down (the heel
    kicked up behind: toe down, sole back), 3 pointing forward past it (toe up), else 0 (upright) - stamped upright on
    a shin lying flat the boot hung off its end like a hook."""
    a = math.degrees(math.atan2(A[0] - K[0], A[1] - K[1]))
    return 1 if a < -BOOT_TURN else 3 if a > BOOT_TURN else 0


def leg_cells(part, H, K, A, boot_rot=None):
    """{(x, y): colour} of one leg - thigh H->K, shin K->A, the knee rounded and its plate on the knee's front, the boot
    at A (turned boot_rot quarter turns clockwise; None: by the shin, boot_turn) - and the bands' own squares (their
    outline ring)."""
    cells = {}
    mid = part["thigh"][len(part["thigh"]) // 2]
    for y in range(int(math.floor(K[1] - KNEE_R)) - 1, int(math.ceil(K[1] + KNEE_R)) + 1):
        for x in range(int(math.floor(K[0] - KNEE_R)) - 1, int(math.ceil(K[0] + KNEE_R)) + 1):
            if math.hypot(x + 0.5 - K[0], y + 0.5 - K[1]) <= KNEE_R:
                cells[(x, y)] = mid
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
    off, cols = boot_offsets(part, boot_turn(K, A) if boot_rot is None else boot_rot)
    for x, y, c in zip(np.floor(A[0] + off[:, 0]).astype(int), np.floor(A[1] + off[:, 1]).astype(int), cols):
        cells[(int(x), int(y))] = c
    return cells, banded


def draw_legs(can, geo, P):
    """Both legs on can: the far one first, the near one and its ring over it. geo values: (hip, knee, ankle[, boot
    quarter turns clockwise - None or left out: by the shin])."""
    for key in ("far", "near"):
        H, K, A = geo[key][:3]
        cells, banded = leg_cells(P[key], H, K, A, geo[key][3] if len(geo[key]) > 3 else None)
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


def reach(hip, foot_dir, frac, L1, L2):
    """Two-bone IK: the ankle frac x (L1 + L2) from hip along foot_dir (degrees from straight down, + forward), the
    knee on the forward side of the hip-ankle line (a leg bends back at the knee). -> (knee, ankle)."""
    d = max(abs(L1 - L2) + 0.01, min(L1 + L2 - 0.01, frac * (L1 + L2)))
    a = math.radians(foot_dir)
    u = np.array((math.sin(a), math.cos(a)))
    ankle = hip + u * d
    c = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
    t = math.acos(max(-1.0, min(1.0, c)))
    side = np.array((u[1], -u[0]))                  # u turned a quarter counter-clockwise on screen: forward for a leg
    if side[0] < 0:                                  # pointing down (the knee goes the way she faces)
        side = -side
    knee = hip + u * (L1 * math.cos(t)) + side * (L1 * math.sin(t))
    return knee, ankle


def flat(j, pitch, unit):
    """League's joints seen without the camera's pitch: y the true height (down, game px, one zero for every frame of
    the camera), x as seen. Through the spec's pitch a foot further from the camera showed higher than it stood - a
    kneeling leg's knee on the floor looked lifted and its toes in the air."""
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    return {k: [v[0], cp * v[1] - sp * v[2] * unit, v[2]] for k, v in j.items()}


def leg_sides(j, roles):
    """Which of League's legs ("l" / "r") each of hers draws: by name, or (roles) League's front foot on her image-right
    leg and its back foot on her image-left one."""
    if not roles:
        return {key: L["side"] for key, L in LEGS.items()}
    front = "r" if j["r_foot"][0] >= j["l_foot"][0] else "l"
    return {"far": front, "near": "l" if front == "r" else "r"}


def reach_to(hip, ankle, L1, L2):
    """Two-bone IK to a given ankle (pulled in along the line when out of reach), the knee forward. -> (knee, ankle)."""
    v = np.asarray(ankle, float) - hip
    d = min(float(np.hypot(*v)), L1 + L2 - 0.01)
    return reach(hip, math.degrees(math.atan2(v[0], v[1])), d / (L1 + L2), L1, L2)


PLANT_TOL = 1.5     # League's ankle within this (game px) of its standing ankle's height: the foot is on the floor
KNEE_LOW = 3.0      # a knee's band and outline reach this far under the knee joint (squares)
BACK_FOOT = 3.0     # a planted foot this far behind its hip is the back foot (it may rise on its toes)
KNEEL_TOL = 1.0     # a knee down at its ankle's height or within this (game px) over it kneels (League's R channel:
                    # knee 4.9, ankle 4.8 - solved as a planted leg its knee went through the floor)


def lowest_row(part, H, K, A, rot=0):
    """The lowest square row a leg drawn so covers, its outline ring included."""
    cells, banded = leg_cells(part, H, K, A, rot)
    return max([y for _, y in cells] + [y + 1 for x, y in banded if (x, y + 1) not in cells])


def geometry_ground(j, jd, P, spread=1.0, hips=None, roles=False):
    """Her legs where League's stand on the floor. j, jd: League's joints of the frame and of the design pose, both
    flat(). The legs as geometry_ik places them, then: a leg whose knee is down at League's standing ankle height or
    lower, and under its own ankle, kneels - the thigh the way League's points, the knee on the floor, the shin back to
    the ankle, the boot turned toe down onto the floor - and sets the floor; every other foot League has on the floor
    (within PLANT_TOL px of its standing ankle) is solved down onto that floor, or onto the lowest planted boot's (the
    ankle kept where geometry_ik put it across, the knee forward; all of them on one floor, as low as each can reach);
    a lifted foot that would reach under the floor is lifted a row over it.
    -> ({"near" | "far": (hip, knee, ankle, boot quarter turns clockwise or None: by the shin)}, the floor's row - the boots' bottom edge -
    in the idle's squares; None when no foot is down: the figure then stands on its lowest boot or League's lift)."""
    geo = {k: (*v, None) for k, v in geometry_ik(j, P, spread=spread, hips=hips, roles=roles).items()}
    sides = leg_sides(j, roles)
    stand = max(jd["l_foot"][1], jd["r_foot"][1])
    kneel, planted, lifted = [], [], []
    for key, s in sides.items():
        knee_y, foot_y = j[f"{s}_knee"][1], j[f"{s}_foot"][1]
        if knee_y >= stand - PLANT_TOL and knee_y > foot_y - KNEEL_TOL:
            kneel.append(key)
        elif foot_y >= stand - PLANT_TOL:
            planted.append(key)
        else:
            lifted.append(key)
    floor = None
    for key in kneel:
        s = sides[key]
        part = P[key]
        H = geo[key][0]
        h, k, f = (np.array(j[f"{s}_{n}"][:2], float) for n in ("hip", "knee", "foot"))
        u = (k - h) / (np.linalg.norm(k - h) or 1.0)
        K = H + u * part["thigh_len"]
        off, _ = boot_offsets(part, 1)
        rise = KNEE_LOW - (off[:, 1].max() + 0.5)          # the ankle this far under the knee (negative: over it)
        rise = max(-part["shin_len"] + 0.5, min(part["shin_len"] - 0.5, rise))
        back = -1.0 if f[0] <= k[0] else 1.0
        A = K + np.array((back * math.sqrt(part["shin_len"] ** 2 - rise ** 2), rise))
        geo[key] = (H, K, A, 1)
        low = lowest_row(part, H, K, A, 1) + 1
        floor = low if floor is None else max(floor, low)
    if planted:
        if floor is None:
            floor = max(geo[k][2][1] + P[k]["drop"] for k in planted)
        for key in planted:                                 # as low as every planted leg reaches
            H, A = geo[key][0], geo[key][2]
            dmax = P[key]["thigh_len"] + P[key]["shin_len"] - 0.05
            dx = A[0] - H[0]
            if abs(dx) < dmax:
                floor = min(floor, H[1] + math.sqrt(dmax ** 2 - dx ** 2) + P[key]["drop"])
        floor = math.floor(floor)                           # a square edge: every planted boot ends on one row
        for key in planted:
            H, A = geo[key][0], geo[key][2]
            L1, L2 = P[key]["thigh_len"], P[key]["shin_len"]
            K, A2 = reach_to(H, (A[0], floor - P[key]["drop"]), L1, L2)
            rot = 0
            if boot_turn(K, A2) == 1 and A2[0] < H[0] - BACK_FOOT:   # the back foot with its shin lying back: up on her
                off, _ = boot_offsets(P[key], 1)       # toes, the boot turned toe down onto the floor (upright under a flat
                                                       # shin it stood like a Z; a front foot stays flat)
                K, A2 = reach_to(H, (A[0], floor - (off[:, 1].max() + 0.5)), L1, L2)
                rot = 1
            geo[key] = (H, K, A2, rot)
    if floor is not None:
        for key in lifted:
            H, K, A, _ = geo[key]
            if A[1] + P[key]["drop"] > floor - 1:
                K, A = reach_to(H, (A[0], floor - 1 - P[key]["drop"]), P[key]["thigh_len"], P[key]["shin_len"])
                geo[key] = (H, K, A, None)
    return geo, floor


def geometry_ik(j, P, spread=1.0, hips=None, roles=False):
    """{"near" | "far": (hip, knee, ankle)}: each ankle where League's foot is seen from its hip - the direction times
    `spread`, at the share of the leg's full length League's hip-to-foot is (how bent it is) - and the knee solved at the
    idle's lengths. League's chibi legs at her height are twice hers (hip to foot about 20 squares against 9): its
    feet from the hips lie only -40..+17 degrees off straight down and its stride is wide by length alone; hers widens
    by the direction (spread). roles: League's front foot (the one further forward) drawn on her image-right leg and its
    back foot on her image-left one, as her idle stands (League steps forward with its near leg: by name the near leg
    went forward across the far one and the two crossed into one)."""
    geo = {}
    sides = leg_sides(j, roles)
    for key, L in LEGS.items():
        s = sides[key]
        h, k, f = (np.array(j[f"{s}_{n}"][:2], float) for n in ("hip", "knee", "foot"))
        full = np.linalg.norm(k - h) + np.linalg.norm(f - k)
        frac = np.linalg.norm(f - h) / (full or 1)
        fdir = math.degrees(math.atan2(f[0] - h[0], f[1] - h[1])) * spread
        H = np.array((hips or {}).get(key, L["hip"]), float)
        K, A = reach(H, fdir, frac, P[key]["thigh_len"], P[key]["shin_len"])
        geo[key] = (H, K, A)
    return geo


def geometry(j, P, swing=1.0, hips=None):
    """{"near" | "far": (hip, knee, ankle)} in idle squares from League's joints j: each thigh along League's
    hip -> knee, each shin along League's knee -> foot, clamped to SHIN_BACK..SHIN_FWD from straight down. swing: the
    thigh's angle from straight down times this, the shin keeping its bend at the knee x swing too (her legs are a
    chibi's, under a third of her height against League's half: at League's angles her stride shows half as wide).
    hips: {"near" | "far": (x, y)} instead of the idle's."""
    geo = {}
    for key, L in LEGS.items():
        s = L["side"]
        h, k, f = (np.array(j[f"{s}_{n}"][:2], float) for n in ("hip", "knee", "foot"))
        a_t = math.degrees(math.atan2(k[0] - h[0], k[1] - h[1]))
        a_s = math.degrees(math.atan2(f[0] - k[0], f[1] - k[1]))
        a_t2 = a_t * swing
        a_s2 = a_t2 + (a_s - a_t) * swing
        t = np.array((math.sin(math.radians(a_t2)), math.cos(math.radians(a_t2))))
        ang = max(SHIN_BACK, min(SHIN_FWD, a_s2))
        H = np.array((hips or {}).get(key, L["hip"]), float)
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
