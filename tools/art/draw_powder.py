#!/usr/bin/env python3
"""Powder's action figures drawn square by square along skeletons (the user, 2026-10-19: 「你直接画不就好了吗」 - no Codex
pose pack): the approved idle's head on every frame, the body, arms and legs drawn at the design's own lengths, widths
and colours, the same drawing in every frame.

    python tools/art/draw_powder.py --try DIR      # the standing figure and a few poses at 8x

Why drawn: the approved side draft (S-2) at 53 rows is 24 squares wide with a two-square near arm that does not part
from the body, and the idle (A-2) holds a hand at her chin - neither can be posed from its own squares without the
deformations the user rejects. What is kept square for square: the idle's head (rows 0-18 and both braids; the fist
that hid her chin is gone, the chin drawn back in: CHIN). What is drawn: the neck, the teal tunic with its collar, belt
and buckle, the pouch of blue bombs (POUCH, a fixed picture), the arms (pink sleeve, skin, the dark brown wrap, the
hand) and the legs (the brown shorts' edge, the pink tights, the boot shaft along the shin and the flat boot foot BOOT,
a fixed picture) - each limb a band of fixed width round its bone with its own 1-square outline, the far limbs a shade
darker. Lengths and rows are the idle's (pack_powder_poses.py measured them): head top row 0, chin row 20, shoulder
row 24, hip joint row 38, knee 44.5, ankle 50.5, soles row 52.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "powder", "hd")


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


# the design's own colours (hd/idle.png, hd/side.png)
C = {k: hexc(v) for k, v in {
    "#": "080110",                                     # outline
    "S": "fdd6b9", "s": "fda78e", "r": "f76252",       # skin, its shade, the cheek red
    "T": "13a7bc", "t": "015f9a",                      # the teal tunic
    "P": "eb589f", "p": "b83786", "q": "721550",       # pink sleeves / tights
    "B": "b96635", "b": "83412b", "d": "532722",       # browns: boots, wraps, belt, shorts, pouch
    "G": "b0b1b5", "g": "55546a",                      # the silver buckle, the boot sole
    "Y": "fcba1d", "y": "fee456",                      # gold
    "c": "00c3fc", "h": "0193fd", "n": "0052c8", "W": "f5fafc",   # the blue bombs (the hair's blues), a highlight
}.items()}
DARKER = {"S": "s", "s": "r", "P": "p", "p": "q", "B": "b", "b": "d", "d": "d", "T": "t", "t": "t", "g": "g",
          "G": "g", "#": "#", "c": "h", "h": "n", "n": "n", "W": "c", "Y": "B", "y": "Y", "r": "r", "q": "q"}

# the lengths (squares) and the head's anchor
THIGH, SHIN = 7.5, 6.0
UPPER, FORE = 5.0, 4.0
TORSO, NECK = 13.0, 4.0                 # hip joint (row 37) to shoulder (row 24), shoulder to chin (row 20)
SOLE_ROW, HIP_ROW = 52, 37             # the idle: belt row 31, the tunic's hem 37, shorts 37-40, tights 40-44
CHIN_AT = (15.5, 20.0)                  # the chin's point (x, y) in the idle's squares: it sits on the skeleton's chin
# the chin drawn back where the fist was (idle rows 19-20)
CHIN = {19: (12, "#sSSSs#"), 20: (13, "#####")}
# a boot foot, its ankle at (2, 0) of the picture (the shaft comes down onto it); the toe points right
BOOT = ["dbbbBBb..",
        "dbbbbBBBb",
        "ddbbbbbBb",
        ".gggggggg"]
BOOT_ANKLE = (3, 0)
# the pouch of blue bombs on the belt behind her, its strap point at (5, 2) of the picture
POUCH = ["..cWc..",
         ".chhcc.",
         "dbbBbbd",
         "dbBBbbd",
         "dbbYbbd",
         ".dbbbd."]
POUCH_AT = (5, 2)


def ray(p, deg, length):
    """From p along deg (0 = straight down, 90 = forward / image right, 180 = up, 270 = back)."""
    a = math.radians(deg)
    return (p[0] + length * math.sin(a), p[1] + length * math.cos(a))


def skeleton(hip, lean=0.0, near_arm=(10, 10), far_arm=(-10, -10), near_leg=(0, 0), far_leg=(0, 0)):
    """Joints from the hip: lean = degrees the torso tips forward; arms (upper, forearm) and legs (thigh, shin) in ray()
    degrees."""
    shoulder = ray(hip, 180 - lean, TORSO)
    chin = ray(shoulder, 180 - lean * 0.5, NECK)
    j = {"hip": hip, "shoulder": shoulder, "chin": chin}
    for side, (ua, fa) in (("near", near_arm), ("far", far_arm)):
        elbow = ray(shoulder, ua, UPPER)
        j[side + "_arm"] = (shoulder, elbow, ray(elbow, fa, FORE), fa)
    for side, (ta, sa) in (("near", near_leg), ("far", far_leg)):
        knee = ray(hip, ta, THIGH)
        j[side + "_leg"] = (hip, knee, ray(knee, sa, SHIN))
    return j


# ------------------------------------------------------------------------------------------------- drawing
class Layer:
    """One part on a canvas: a mask and its colour letters; finish() rings it with the outline."""

    def __init__(self, shape):
        self.m = np.zeros(shape, bool)
        self.c = np.full(shape, " ", "<U1")

    def paint(self, mask, letter):
        self.m |= mask
        self.c[mask] = letter

    def picture(self, at, rows, darker=False):
        x0, y0 = at
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                y, x = y0 + dy, x0 + dx
                if ch != "." and 0 <= y < self.m.shape[0] and 0 <= x < self.m.shape[1]:
                    self.m[y, x] = True
                    self.c[y, x] = DARKER[ch] if darker else ch

    def rgba(self, outline=True):
        H, W = self.m.shape
        out = np.zeros((H, W, 4), np.uint8)
        if outline:
            ring = ndimage.binary_dilation(self.m, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)) & ~self.m
            out[ring] = C["#"]
        for k, v in C.items():
            out[self.m & (self.c == k)] = v
        return out


def grid(shape):
    ys, xs = np.mgrid[0:shape[0], 0:shape[1]]
    return xs + 0.5, ys + 0.5


def band(shape, p0, p1, r0, r1=None):
    """Squares whose centres lie within r (r0 at p0 to r1 at p1) of the segment; -> mask, t along it, side (+ = the
    segment's right-hand side looking from p0 to p1)."""
    r1 = r0 if r1 is None else r1
    px, py = grid(shape)
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    l2 = max(dx * dx + dy * dy, 1e-6)
    t = ((px - x0) * dx + (py - y0) * dy) / l2
    tc = np.clip(t, 0, 1)
    d = np.hypot(px - (x0 + tc * dx), py - (y0 + tc * dy))
    side = (px - x0) * dy - (py - y0) * dx
    return d <= r0 + (r1 - r0) * tc, t, side, d, r0 + (r1 - r0) * tc


def shade_letters(darker, *letters):
    return [DARKER[k] if darker else k for k in letters]


def draw_arm(shape, arm, darker=False):
    """The pink short sleeve, the skin of the upper arm, the dark brown wrap on the forearm, the hand."""
    shoulder, elbow, wrist, fa = arm
    L = Layer(shape)
    P_, p_, S_, s_, B_, b_, d_ = shade_letters(darker, "P", "p", "S", "s", "B", "b", "d")
    m, t, side, d, r = band(shape, shoulder, elbow, 1.4)
    L.paint(m, S_)
    L.paint(m & (side < 0) & (d > r - 0.9), s_)
    sleeve = m & (t < 0.38)
    L.paint(sleeve, P_)
    L.paint(sleeve & (side < 0) & (d > r - 0.9), p_)
    m2, t2, side2, d2, r2 = band(shape, elbow, wrist, 1.45)
    L.paint(m2 & ~sleeve, b_)
    L.paint(m2 & ~sleeve & (side2 < 0) & (d2 > r2 - 0.8), d_)
    L.paint(m2 & ~sleeve & (side2 > 0) & (d2 > r2 - 0.8) & (t2 < 0.8), B_)
    hand = ray(wrist, fa, 1.2)
    mh, _, sideh, dh, rh = band(shape, wrist, hand, 1.5)
    L.paint(mh & ~m2, S_)
    L.paint(mh & ~m2 & (sideh < 0) & (dh > rh - 0.8), s_)
    return L


def draw_leg(shape, leg, darker=False):
    """The shorts' edge and the pink tights on the thigh, the boot shaft along the shin, the flat boot foot."""
    hip, knee, ankle = leg
    L = Layer(shape)
    P_, p_, B_, b_, d_ = shade_letters(darker, "P", "p", "B", "b", "d")
    m, t, side, d, r = band(shape, hip, knee, 2.0, 1.75)
    L.paint(m, P_)
    L.paint(m & (side < 0) & (d > r - 0.9), p_)
    L.paint(m & (t < 0.38), b_)                     # the brown shorts under the tunic (rows 37-40)
    m2, t2, side2, d2, r2 = band(shape, knee, ankle, 2.1, 2.3)
    shaft = m2 & (t2 > 0.05)
    L.paint(shaft, b_)
    L.paint(shaft & (side2 > 0) & (d2 > r2 - 0.9), B_)
    L.paint(shaft & (side2 < 0) & (d2 > r2 - 0.9), d_)
    ax, ay = int(math.floor(ankle[0])) - BOOT_ANKLE[0], int(math.floor(ankle[1])) - BOOT_ANKLE[1]
    L.picture((ax, ay), BOOT, darker)
    return L


def draw_torso(shape, j):
    """The neck, the teal tunic from the collar to the hem (its back edge darker), the pink collar, the belt with its
    silver buckle at the front."""
    hip, shoulder, chin = j["hip"], j["shoulder"], j["chin"]
    L = Layer(shape)
    m, _, sn, dn, rn = band(shape, chin, shoulder, 1.0)
    L.paint(m, "S")
    L.paint(m & (sn < 0), "s")
    up = ((shoulder[0] - hip[0]) / TORSO, (shoulder[1] - hip[1]) / TORSO)
    top = (shoulder[0] + up[0] * 0.5, shoulder[1] + up[1] * 0.5)
    hem = (hip[0] + up[0] * 0.3, hip[1] + up[1] * 0.3)
    mt, tt, side, d, r = band(shape, top, hem, 3.0, 4.3)
    L.paint(mt, "T")
    L.paint(mt & (side > 0) & (d > r - 1.1), "t")          # the back edge (left of the spine looking down)
    L.paint(mt & (tt < 0.12) & (side < 0) & (d < 1.6), "P")   # the pink shirt at the collar's front
    span = math.hypot(hem[0] - top[0], hem[1] - top[1])
    belt = mt & (tt > 6.3 / span) & (tt < 7.9 / span)          # rows 31-32 of the idle
    L.paint(belt, "b")
    L.paint(belt & (side > 0) & (d > r - 1.1), "d")
    L.paint(belt & (side < 0) & (d > r - 1.6), "G")         # the buckle at the front
    strap = (top[0] - up[0] * 7.0 - 2.5, top[1] - up[1] * 7.0)   # on the belt, at her back
    L.picture((int(round(strap[0])) - POUCH_AT[0], int(round(strap[1])) - POUCH_AT[1]), POUCH)
    return L


class Head:
    """The idle's head, braids and drawn-back chin, as colour letters relative to CHIN_AT."""

    def __init__(self):
        a = np.asarray(Image.open(lp(os.path.join(SRC, "idle.png"))).convert("RGBA"))
        keep = np.zeros(a.shape[:2], bool)
        keep[:19, :25] = True
        keep[19:29, :8] = True                  # the braids behind her on the left
        keep[19:25, 20:24] = True               # and on the right
        keep &= a[..., 3] > 0
        pix = np.where(keep[..., None], a, 0)
        for row, (c0, s) in CHIN.items():
            for k, ch in enumerate(s):
                pix[row, c0 + k] = C[ch]
        self.a = pix

    def put(self, can, chin):
        dx = int(round(chin[0] - CHIN_AT[0]))
        dy = int(round(chin[1] - CHIN_AT[1]))
        H, W = self.a.shape[:2]
        for y in range(H):
            for x in range(W):
                if self.a[y, x, 3]:
                    Y, X = y + dy, x + dx
                    if 0 <= Y < can.shape[0] and 0 <= X < can.shape[1]:
                        can[Y, X] = self.a[y, x]
        return can


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]
    return dst


HEAD = None


def figure(shape, hip, **pose):
    """One frame: far arm, far leg, near leg, torso (and pouch), near arm, head - each over the last (a near thigh
    raised forward goes over the tunic)."""
    global HEAD
    HEAD = HEAD or Head()
    j = skeleton(hip, **pose)
    can = np.zeros(shape + (4,), np.uint8)
    over(can, draw_arm(shape, j["far_arm"], darker=True).rgba())
    over(can, draw_leg(shape, j["far_leg"], darker=True).rgba())
    near_leg = draw_leg(shape, j["near_leg"]).rgba()
    thigh_up = pose.get("near_leg", (0, 0))[0] > 35      # a thigh raised forward is in front of the tunic's skirt
    if not thigh_up:
        over(can, near_leg)
    over(can, draw_torso(shape, j).rgba())
    if thigh_up:
        over(can, near_leg)
    over(can, draw_arm(shape, j["near_arm"]).rgba())
    HEAD.put(can, j["chin"])
    return can


# a standing figure and the poses (pack_powder_poses.POSES, the same skeletons)
POSES = {
    "stand": dict(near_arm=(8, 5), far_arm=(-8, -5), near_leg=(4, 0), far_leg=(-4, 0)),
    "wind": dict(lean=-12, near_arm=(272, 235), far_arm=(60, 80), near_leg=(-15, -10), far_leg=(25, 5)),
    "throw": dict(lean=22, near_arm=(105, 95), far_arm=(-40, -20), near_leg=(-35, -35), far_leg=(45, 0)),
    "crouch": dict(lean=28, near_arm=(35, 70), far_arm=(45, 80), near_leg=(75, -15), far_leg=(70, -20)),
}


def grounded_hip(shape, ground, x, **pose):
    """The hip that puts the lowest ankle of the pose on the ground (the boot's sole two rows under the ankle)."""
    j = skeleton((x, 0.0), **pose)
    low = max(j["near_leg"][2][1], j["far_leg"][2][1])
    return (x, ground - 2 - low)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--try", dest="tries", required=True)
    a = ap.parse_args()
    os.makedirs(a.tries, exist_ok=True)
    shape = (66, 56)
    cells = []
    for name, pose in POSES.items():
        hip = grounded_hip(shape, 62, 26.5, **pose)
        cells.append(figure(shape, hip, **pose))
    z = 8
    W = len(cells) * (shape[1] * z + 16)
    sheet = Image.new("RGBA", (W, shape[0] * z), (200, 205, 195, 255))
    for k, c in enumerate(cells):
        sheet.alpha_composite(Image.fromarray(np.repeat(np.repeat(c, z, 0), z, 1)), (k * (shape[1] * z + 16), 0))
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "idle.png"))).convert("RGBA"))
    path = os.path.join(a.tries, "powder_draw_try.png")
    sheet.convert("RGB").save(path)
    print(path)


if __name__ == "__main__":
    main()
