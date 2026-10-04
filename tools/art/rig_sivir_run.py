#!/usr/bin/env python3
"""Sivir's run (tools/art/rig_sivir.py builds it into the strips), v2 2026-10-04: 「走路姿势不像希维尔 上下晃动时模型变形」 - the turned straight legs (RotSprite) changed
shape every frame and the far one was longer (the body jumped 2-5 rows). Now League's run: the design's head and
torso upright, the near arm pumping bent at the elbow (a fist), the blade held behind; the legs DRAWN along a two-bone
run cycle in the design's own leg materials (skin at the thigh top, the purple stocking, the gold knee guard stamped
as drawn at the knee, the boot as drawn at the ankle), both legs the same lengths, the body on the planted foot
(a bob of a row at most)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig_sivir as R  # noqa: E402

OUT = R.OUT
C = {
    "t": (0xF4, 0xB8, 0x88), "p": (0xD5, 0x8A, 0x5C), "m": (0x9A, 0x54, 0x34),       # skin lit / mid / dark
    "j": (0x4E, 0x3F, 0x5E), "e": (0x2E, 0x24, 0x38),                                # stocking / sleeve lit, dark
    "u": (0xFF, 0xE2, 0x7A), "q": (0xE8, 0xA8, 0x30), "n": (0xA8, 0x69, 0x1E),       # gold light / mid / dark
    "k": (0x7A, 0x4A, 0x28), "f": (0x5C, 0x34, 0x10), "c": (0x3E, 0x24, 0x16),       # glove brown
}


def rgba(ch):
    return np.array(C[ch] + (255,), np.uint8)


THIGH, SHIN = 7.5, 7.0          # hip -> knee, knee -> ankle (squares): the idle's leg is ~14 hip -> ankle
SKIN_LEN = 2.3                  # the bare thigh under the belt
W_THIGH, W_SHIN = 2.1, 1.6      # half widths
ANKLE_TO_SOLE = 4               # the boot as drawn: its ankle 4 rows over the soles' row
# one leg's cycle (8 frames; degrees from straight down, + = forward): contact, loading, mid-stance, push, toe-off,
# kick (shin up behind), passing (knee ahead, shin back), reaching
CYCLE = [(26, 10), (14, 0), (2, -6), (-12, -16), (-24, -34), (-16, -88), (24, -72), (36, -8)]
STANCE = (0, 1, 2, 3)            # the phases whose foot is on the ground
HIPS = {"near": 68.5, "far": 63.5}
HIP_ROW = 84.5                   # the design's thigh tops (under the belt): the body moves with the hips from here
# the near arm (shoulder under the pauldron): the upper arm swings against the near leg, the forearm bent forward
SHOULDER = (75.5, 77.5)
UPPER, FORE = 4.5, 3.5
ARM_SWING = [-25, -15, 0, 15, 28, 18, 0, -15]     # upper arm, degrees from straight down (+ forward)
ELBOW = 85                                          # the forearm's bend ahead of the upper arm
LEAN = -0.06                                        # the upper body leans forward over the hips (the head ~2 ahead)


def seg(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(vx, vy) or 1e-9
    t = max(0.0, min(n, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / n))
    qx, qy = a[0] + vx / n * t, a[1] + vy / n * t
    side = (p[0] - qx) * (vy / n) - (p[1] - qy) * (vx / n)      # + = right of a->b going down
    return math.hypot(p[0] - qx, p[1] - qy), t, side


def pt(a, deg, n):
    t = math.radians(deg)
    return (a[0] + math.sin(t) * n, a[1] + math.cos(t) * n)


def parts(d):
    """The knee guard and the boot as the design draws them (near leg), with their joints."""
    knee = {}
    for y in range(88, 93):
        for x in range(73, 80):
            c = tuple(int(v) for v in d[y, x, :3])
            if d[y, x, 3] and c not in (C["j"], C["e"]) and c != OUT:
                knee[(x - 76, y - 90)] = d[y, x].copy()
    boot = {}
    for y in range(94, 100):
        for x in range(78, 88):
            c = tuple(int(v) for v in d[y, x, :3])
            if d[y, x, 3] and c not in (C["j"], C["e"]) and (y >= 95 or x >= 80):
                boot[(x - 80, y - 95)] = d[y, x].copy()          # the ankle (80, 95)
    return knee, boot


def leg_cells(hip, thigh_deg, shin_deg, knee_sprite, boot_sprite, mirror_boot=False):
    K = pt(hip, thigh_deg, THIGH)
    A = pt(K, shin_deg, SHIN)
    return leg_at(hip, K, A, knee_sprite, boot_sprite, mirror_boot)


def ik(hip, ankle, l1=None, l2=None):
    """The knee of a two-bone leg from the hip to the ankle, bent forward (+x); the ankle pulled in if out of reach."""
    l1 = THIGH if l1 is None else l1
    l2 = SHIN if l2 is None else l2
    dx, dy = ankle[0] - hip[0], ankle[1] - hip[1]
    d = math.hypot(dx, dy)
    if d >= l1 + l2 - 1e-6:
        k = (l1 + l2 - 1e-6) / d
        ankle = (hip[0] + dx * k, hip[1] + dy * k)
        dx, dy, d = dx * k, dy * k, l1 + l2 - 1e-6
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    mx, my = hip[0] + dx * a / d, hip[1] + dy * a / d
    nx, ny = -dy / d, dx / d
    if nx < 0:                       # the knee to the front
        nx, ny = -nx, -ny
    return (mx + nx * h, my + ny * h), ankle


def leg_at(hip, K, A, knee_sprite, boot_sprite, mirror_boot=False):
    cells = {}
    xs = [hip[0], K[0], A[0]]
    ys = [hip[1], K[1], A[1]]
    for y in range(int(min(ys)) - 3, int(max(ys)) + 4):
        for x in range(int(min(xs)) - 3, int(max(xs)) + 4):
            p = (x + 0.5, y + 0.5)
            d1, t1, s1 = seg(p, hip, K)
            d2, t2, s2 = seg(p, K, A)
            if d1 <= W_THIGH and (d1 <= d2 or t1 < THIGH * 0.6):
                if t1 < SKIN_LEN:
                    ch = "t" if s1 > 0.8 else ("m" if s1 < -1.0 else "p")
                else:
                    ch = "j" if s1 >= -0.3 else "e"
            elif d2 <= W_SHIN:
                ch = "j" if s2 >= -0.3 else "e"
            else:
                continue
            cells[(x, y)] = rgba(ch)
    kx, ky = int(math.floor(K[0])), int(math.floor(K[1]))
    for (dx, dy), c in knee_sprite.items():
        cells[(kx + dx, ky + dy)] = c
    ax, ay = int(math.floor(A[0])), int(math.floor(A[1]))
    for (dx, dy), c in boot_sprite.items():
        cells[(ax - dx if mirror_boot else ax + dx, ay + dy)] = c
    return cells, A


def ring(cells, floor=99):
    """One outline square round the cells; nothing under the soles' row (the boot's own sole line is the outline)."""
    out = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and q[1] <= floor:
                out[q] = np.array(OUT + (255,), np.uint8)
    out.update({k: v for k, v in cells.items() if k[1] <= floor})
    return out


def arm_cells(shoulder, up_deg, elbow=None):
    elbow = ELBOW if elbow is None else elbow
    E = pt(shoulder, up_deg, UPPER)
    F = pt(E, up_deg + elbow, FORE)
    H = pt(F, up_deg + elbow, 1.2)
    cells = {}
    for y in range(int(min(shoulder[1], E[1], H[1])) - 3, int(max(shoulder[1], E[1], H[1])) + 4):
        for x in range(int(min(shoulder[0], E[0], H[0])) - 3, int(max(shoulder[0], E[0], H[0])) + 4):
            p = (x + 0.5, y + 0.5)
            dh = math.hypot(p[0] - H[0], p[1] - H[1])
            d1, _, s1 = seg(p, shoulder, E)
            d2, _, s2 = seg(p, E, F)
            if dh <= 1.5:
                ch = "k" if p[1] < H[1] else ("f" if dh < 1.0 else "c")
            elif d2 <= 1.3:
                ch = "u" if s2 > 0.6 else ("n" if s2 < -0.6 else "q")
            elif d1 <= 1.2:
                ch = "j" if s1 >= -0.2 else "e"
            else:
                continue
            cells[(x, y)] = rgba(ch)
    return cells


def run_frame_v2(P, i):
    d = P.d
    knee, boot = parts(d)
    near_ph, far_ph = i % 8, (i + 4) % 8
    planted = near_ph if near_ph in STANCE else far_ph
    t, s = CYCLE[planted]
    extent = THIGH * math.cos(math.radians(t)) + SHIN * math.cos(math.radians(s))
    hip_y = 99 - ANKLE_TO_SOLE - extent + 0.5
    dy = int(round(hip_y - HIP_ROW))
    hip_y = HIP_ROW + dy
    can = np.zeros((128, 128, 4), np.uint8)
    # the blade held back at the waist (League's run trails it behind her), under the legs: a foot kicked up behind
    # shows over it
    ud = [-6, -5, -4, -3, -2, -3, -4, -5][i]
    cuff = (59.0, 76.0)
    lean_c = R.lean_shift(int(cuff[1]), LEAN)
    behind = R.transform(*P.unit, R.CUFF, ud, (cuff[0] + lean_c, cuff[1] + dy))
    for k, v in R.sleeve((R.SHOULDER_FAR[0] + R.lean_shift(int(R.SHOULDER_FAR[1]), LEAN), R.SHOULDER_FAR[1] + dy),
                         (cuff[0] + lean_c, cuff[1] + dy)).items():
        behind.setdefault(k, v)
    R.put(can, behind)
    legs = {}
    for side, ph in (("far", far_ph), ("near", near_ph)):
        cells, A = leg_cells((HIPS[side], hip_y), CYCLE[ph][0], CYCLE[ph][1], knee, boot)
        legs[side] = ring(cells)
    R.put(can, legs["far"])
    R.put(can, legs["near"])
    # the upper body (the design without legs and arms), the blade behind in the far hand
    up = {}

    body = P.body_nolegs
    for yy, xx in zip(*np.nonzero(body[..., 3])):
        up.setdefault((xx, yy), body[yy, xx])
    R.put(can, {(x + R.lean_shift(y, LEAN), y + dy): c for (x, y), c in up.items()})
    arm = ring(arm_cells((SHOULDER[0] + R.lean_shift(int(SHOULDER[1]), LEAN), SHOULDER[1] + dy), ARM_SWING[i]))
    R.put(can, arm)
    can = R.drop_small(can, 4)
    r0 = R.rot_pt(R.RING, R.CUFF, ud)
    r_ = (r0[0] - R.CUFF[0] + cuff[0] + lean_c, r0[1] - R.CUFF[1] + cuff[1] + dy)
    keep = [(int(round(r_[0] - 0.5)), int(round(r_[1] - 0.5)))]
    return R.settle(can, keep, 0, dy, 86 + dy)


# ---------------------------------------------------------------------------------------------------------------
# v3 (2026-10-04, 「太僵硬了吧？和僵尸一样」): v2 held the upper body dead still (no bob), the arm at one bend and the
# blade nearly fixed. Now the upper body - one rigid block, never sheared or stretched - rises and falls with League's
# run (its head joint per frame, sivir_cells.json of the strips pack: 35.6 38.4 38.4 34.4 33.6 37.3 38.5 35.7 = low on
# the contacts, high in the flight), 0.6 of it; each foot is placed (ahead on the contact, drawn back under the body,
# off the toe, kicked up behind, swung through, reaching) and the leg solved to it (knee forward), so the planted foot
# stays on the ground and the knee bends as the body sinks; the near arm swings 70 degrees with the elbow more bent
# ahead than behind; the blade swings against it.

BOB = [1, 3, 3, 0, 0, 2, 3, 1]                  # rows the body sits lower (League's head joint x 0.6)
HIP_BASE = 81.5                                  # the hips' row at the top of the bob (the legs nearly straight;
#                                                  HIP_ROW - 3, so the body moves whole rows)
# one foot over its cycle (phase 0 = contact): (ankle x from its hip, lift of the sole over the ground)
FOOT = [(6.0, 0), (3.0, 0), (0.0, 0), (-3.5, 0), (-7.0, 1), (-6.5, 5), (-1.0, 5), (5.0, 2)]
CONTACT = 1                                      # the frame of the near foot's contact (League: the low frames 2-3)
V3_HIPS = {"near": 68.5, "far": 63.5}
ARM3 = [(-30, 45), (-25, 50), (-5, 70), (20, 95), (35, 105), (25, 95), (0, 70), (-20, 50)]   # (upper arm, elbow)
BLADE3 = [5, 6, 4, 0, -4, -6, -4, 0]             # the unit's swing (degrees) against the near arm


def run_frame(P, i):
    d = P.d
    knee, boot = parts(d)
    hip_y = HIP_BASE + BOB[i]
    up_dy = int(round(hip_y - HIP_ROW))
    can = np.zeros((128, 128, 4), np.uint8)
    # the blade behind the waist, under the legs
    ud = BLADE3[i]
    cuff = (59.0, 76.0)
    lean_c = R.lean_shift(int(cuff[1]), LEAN)
    behind = R.transform(*P.unit, R.CUFF, ud, (cuff[0] + lean_c, cuff[1] + up_dy))
    for k, v in R.sleeve((R.SHOULDER_FAR[0] + R.lean_shift(int(R.SHOULDER_FAR[1]), LEAN), R.SHOULDER_FAR[1] + up_dy),
                         (cuff[0] + lean_c, cuff[1] + up_dy)).items():
        behind.setdefault(k, v)
    R.put(can, behind)
    for side in ("far", "near"):
        ph = (i - CONTACT + (4 if side == "far" else 0)) % 8
        fx, lift = FOOT[ph]
        hip = (V3_HIPS[side], hip_y)
        ankle = (hip[0] + fx, 99 - ANKLE_TO_SOLE + 0.5 - lift)
        K, A = ik(hip, ankle)
        R.put(can, ring(leg_at(hip, K, A, knee, boot)[0]))
    up = {}
    body = P.body_nolegs
    for yy, xx in zip(*np.nonzero(body[..., 3])):
        up.setdefault((xx, yy), body[yy, xx])
    R.put(can, {(x + R.lean_shift(y, LEAN), y + up_dy): c for (x, y), c in up.items()})
    ua, el = ARM3[i]
    R.put(can, ring(arm_cells((SHOULDER[0] + R.lean_shift(int(SHOULDER[1]), LEAN), SHOULDER[1] + up_dy), ua, el)))
    can = R.drop_small(can, 4)
    r0 = R.rot_pt(R.RING, R.CUFF, ud)
    r_ = (r0[0] - R.CUFF[0] + cuff[0] + lean_c, r0[1] - R.CUFF[1] + cuff[1] + up_dy)
    keep = [(int(round(r_[0] - 0.5)), int(round(r_[1] - 0.5)))]
    return R.settle(can, keep, 0, up_dy, 86 + up_dy)


if __name__ == "__main__":
    P = R.Parts()
    fr = [("idle", P.d)] + [(f"run {k + 1}", run_frame(P, k)) for k in range(8)]
    print(R.show(fr, "run.png", z=5))
