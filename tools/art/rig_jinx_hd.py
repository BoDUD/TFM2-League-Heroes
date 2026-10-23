#!/usr/bin/env python3
"""league_jinx redone at PPU 2.2 from the user's own side-view picture (tools/art/design_jinx_hd.py; the user,
2026-10-23: 「设计图和 PPU 2.2 通过，开始做动作」, then 「动作帧你自己做吧 不通过codex了 做到完美了喊我review」), every
action posed here from the design's own squares, after oppi's Jinx (LoL Reborn champions/jinx.aseprite: the same side
view, Fishbones on her back) and League's clips.

    python tools/art/rig_jinx_hd.py --parts DIR         # the parts tinted and the key poses
    python tools/art/rig_jinx_hd.py --review DIR        # every tag at 3x + GIFs
    python tools/art/rig_jinx_hd.py                     # orig strips + the 1x sheet
    python tools/art/hero_reels.py --hero jinx          # then: the idle / ban-pick reels from idle_base

No square is redrawn: the parts are cut square by square (SPANS, Fishbones by its own layer's footprint) and placed only by
whole squares, quarter turns, mirrors and whole-row shifts, the run's and the death's thighs the design's own stocking
rows laid along the bone (Legs); standing, the parts rebuild the design exactly (Poser.check).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "jinx"
PPU = 2.2
DESIGN_ROWS = 82
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
PAD = 40
PIVOT_COL = 45                  # between the soles (rear boot 22-33, front boot 51-66)

# ------------------------------------------------------------------------------------------------ the parts
# part -> {row: (first column, last column)} of the design's squares (outline squares included); a square belongs to the
# first part in ORDER that names it; Fishbones is its own layer's footprint (hd/fishbones.png at FISH_AT), the gun what is
# left of GUN_BOX that is not the torso's black, skin and gold, the torso the rest
FISH_AT = (0, 3)
SPANS = {
    # the near braid: every square up to this column, from under the back of her head down to its curled tip
    "braid_n": {25: (0, 31), 26: (0, 32), 27: (0, 32), 28: (0, 31), 29: (0, 29), 30: (0, 29), 31: (0, 29), 32: (0, 28),
                33: (0, 27), 34: (0, 26), 35: (0, 24), 36: (0, 24), 37: (0, 23), 38: (0, 22), 39: (0, 21), 40: (0, 21),
                41: (0, 21), 42: (0, 20), 43: (0, 19), 44: (0, 18), 45: (0, 17), 46: (0, 16), 47: (0, 16), 48: (0, 17),
                49: (0, 17), 50: (0, 17), 51: (0, 16), 52: (0, 16), 53: (0, 15), 54: (0, 14), 55: (0, 14), 56: (0, 15),
                57: (0, 15), 58: (0, 16), 59: (0, 17), 60: (0, 17), 61: (0, 18), 62: (0, 21), 63: (0, 21), 64: (0, 21),
                65: (0, 22), 66: (0, 22), 67: (0, 22), 68: (0, 22), 69: (0, 22), 70: (0, 22), 71: (0, 21), 72: (0, 20),
                73: (0, 19), 74: (0, 18), 75: (0, 17)},
    # the far braid: down behind her hip, then its tip curling out between her legs
    "braid_f": {39: (26, 28), 40: (25, 28), 41: (24, 29), 42: (25, 30), 43: (25, 31), 44: (25, 31), 45: (24, 30),
                46: (23, 31), 47: (23, 31), 48: (23, 30), 49: (23, 30), 50: (23, 30), 51: (24, 29), 52: (24, 28),
                53: (24, 29), 54: (24, 29), 55: (23, 30), 56: (23, 30), 57: (23, 30), 58: (23, 30), 59: (23, 29),
                60: (23, 30), 61: (24, 30), 62: (25, 31), 63: (25, 30), 64: (25, 29),
                66: (37, 44), 67: (36, 45), 68: (34, 47), 69: (33, 47), 70: (35, 47), 71: (40, 47), 72: (40, 47),
                73: (41, 47), 74: (42, 47), 75: (38, 47), 76: (38, 46), 77: (38, 45), 78: (39, 44)},
    # the rear leg (the striped stocking from under her shorts to the knee, the boot) and the front one (the knee under
    # the gun, the boot)
    "leg_r": {53: (40, 44), 54: (40, 44), 55: (39, 44), 56: (35, 44), 57: (34, 44), 58: (34, 43), 59: (33, 43),
              60: (34, 42), 61: (33, 42), 62: (32, 41), 63: (31, 41), 64: (30, 40), 65: (26, 41), 66: (26, 38),
              67: (25, 35), 68: (25, 33), 69: (25, 32), 70: (25, 34), 71: (24, 35), 72: (23, 34), 73: (23, 34),
              74: (22, 34), 75: (22, 31), 76: (22, 32), 77: (22, 33), 78: (22, 33), 79: (23, 33), 80: (23, 33),
              81: (23, 33)},
    "leg_f": {64: (51, 55), 65: (52, 58), 66: (51, 59), 67: (50, 60), 68: (50, 61), 69: (50, 61), 70: (49, 61),
              71: (50, 61), 72: (51, 61), 73: (51, 60), 74: (51, 64), 75: (51, 65), 76: (51, 66), 77: (51, 66),
              78: (51, 66), 79: (51, 66), 80: (51, 66), 81: (52, 66)},
    # the zapper hanging at her near hip
    "zap": {47: (32, 35), 48: (31, 35), 49: (32, 35), 50: (31, 37), 51: (30, 37), 52: (29, 36), 53: (30, 36),
            54: (30, 35), 55: (31, 35), 56: (31, 35), 57: (31, 34), 58: (31, 34), 59: (30, 34), 60: (30, 34),
            61: (30, 34), 62: (30, 32)},
    # the far arm: the shoulder by her chin, the black bands, the pink gauntlet, the hand on the gun's front handle
    "arm_f": {28: (47, 50), 29: (47, 51), 30: (47, 52), 31: (48, 53), 32: (48, 54), 33: (49, 54), 34: (49, 55),
              35: (49, 57), 36: (48, 58), 37: (48, 59), 38: (51, 61), 39: (52, 63), 40: (53, 66), 41: (54, 68),
              42: (56, 67), 43: (62, 68), 44: (64, 67), 45: (64, 66)},
    # the near (tattooed) arm: the shoulder, the upper arm down to the elbow, the forearm across her waist, the gloved
    # hand on the gun's rear grip
    "arm_n": {27: (35, 40), 28: (34, 40), 29: (33, 39), 30: (33, 40), 31: (33, 41), 32: (33, 41), 33: (32, 41),
              34: (31, 41), 35: (31, 39), 36: (30, 38), 37: (30, 38), 38: (29, 39), 39: (29, 48), 40: (29, 45),
              41: (30, 45), 42: (31, 46), 43: (33, 49), 44: (34, 49), 45: (38, 48), 46: (44, 49), 47: (46, 49)},
    # the head: the hair, the face and the dark locks hanging behind her near shoulder and in front of it
    "head": {**{r: (25, 87) for r in range(25)},
             25: (32, 53), 26: (33, 52), 27: [(32, 34), (39, 51)], 28: [(31, 33), (41, 46)], 29: [(28, 33), (42, 44)],
             30: [(28, 32), (42, 45)], 31: [(28, 32), (43, 45)], 32: (29, 32), 33: (28, 31), 34: (27, 30),
             35: (28, 30), 36: (28, 29), 37: (28, 29), 38: (27, 28)},
}
ORDER = ["leg_r", "leg_f", "braid_n", "braid_f", "zap", "arm_f", "arm_n", "head"]
GUN_BOX = (42, 38, 87, 66)      # columns, rows (inclusive) the gun lies in
TORSO_COLOURS = {"322330", "4E363A", "765C69", "765A49", "FAD3C5", "DC9F9B", "CA858E", "B6A492", "AC5875", "EBEBE7",
                 "AEADB7", "AC7895", "4A3020", "744B28", "936B3A", "C28D44", "E7BF76"}
TORSO_BOX = (30, 26, 52, 57)
FISH_COLOURS = {"8487DE", "5E5FB8", "45438E", "2D2A5E", "D8DAF2", "8E2233", "F2A33A", "1A1420",
                "4A3020", "744B28", "936B3A", "C28D44", "E7BF76"}
PARTS = ["fish", "curl", "braid_f", "braid_n", "leg_f", "leg_r", "torso", "zap", "head", "arm_f", "gun", "arm_n", "arm_lo"]
CURL_ROW = 65                   # braid_f from this row down: its tip curling out between her legs (curl)
CURL_ON = (-12, -2)             # the curl moved onto the braid's end (the hidden stretch behind the near knee left out)
ELBOW_ROW = 39                  # arm_n from this row down (the forearm across her waist and the gloved hand): arm_lo
O = (13, 1, 23)                 # the outline (0D0117)


def lp(path):
    return R.lp(path)


def hexes(d):
    return np.array([["%02X%02X%02X" % tuple(d[y, x, :3]) for x in range(d.shape[1])] for y in range(d.shape[0])])


def masks(d):
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    hx = hexes(d)
    lab = np.full((H, W), "", object)
    fb = np.asarray(Image.open(lp(os.path.join(HD, "fishbones.png"))).convert("RGBA"))
    ys, xs = np.nonzero(fb[..., 3] > 0)
    foot = np.zeros((H, W), bool)
    foot[ys + FISH_AT[1], xs + FISH_AT[0]] = True
    lab[foot & op & np.isin(hx, list(FISH_COLOURS))] = "fish"
    for name in ORDER:
        for r, spans in SPANS[name].items():
            for x0, x1 in (spans if isinstance(spans, list) else [spans]):
                for x in range(x0, x1 + 1):
                    if 0 <= r < H and 0 <= x < W and op[r, x] and lab[r, x] == "":
                        lab[r, x] = name
    yy, xx = np.mgrid[0:H, 0:W]
    x0, y0, x1, y1 = GUN_BOX
    tx0, ty0, tx1, ty1 = TORSO_BOX
    torso_like = np.isin(hx, list(TORSO_COLOURS)) & (xx >= tx0) & (xx <= tx1) & (yy >= ty0) & (yy <= ty1)
    gun = op & (lab == "") & (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1) & ~torso_like
    lab[gun] = "gun"
    lab[op & (lab == "")] = "torso"
    lab[(lab == "arm_n") & (yy >= ELBOW_ROW)] = "arm_lo"
    lab[(lab == "braid_f") & (yy >= CURL_ROW)] = "curl"
    return {name: lab == name for name in PARTS}


def piece(d, m):
    """The squares of mask m cut out on their bounding box, and the box's top-left (x, y)."""
    ys, xs = np.nonzero(m)
    sub = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
    return sub, (int(xs.min()), int(ys.min()))


# ------------------------------------------------------------------------------------------------ drawing
class Frame:
    """A frame being composed in design squares (PAD squares round the design)."""

    def __init__(self, d):
        self.d = d
        self.a = np.zeros((d.shape[0] + 2 * PAD, d.shape[1] + 2 * PAD, 4), np.uint8)

    def stamp(self, img, x0, y0, under=False):
        ys, xs = np.nonzero(img[..., 3] > 0)
        Y, X = ys + y0 + PAD, xs + x0 + PAD
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
        if under:
            free = self.a[Y, X, 3] == 0
            Y, X, ys, xs = Y[free], X[free], ys[free], xs[free]
        self.a[Y, X] = img[ys, xs]


def transformed(img, x0, y0, t):
    """A part's picture (top-left x0, y0 in design squares) moved by its transform t: "shear" (whole rows shifted, k
    columns at the bottom row growing from 0 at row `pivot` - a braid swinging), "flip" (mirrored about column
    t["about"][0]), "rot" (quarter turns counter-clockwise about t["about"]), then (dx, dy). Returns (picture, x, y)."""
    out, x, y = img, x0, y0
    k = t.get("shear", 0)
    if k:
        h, w = out.shape[:2]
        p = t.get("pivot", 0)
        prof = t.get("profile")
        s = [0 if r <= p else int(round(k * (prof((r - p) / max(1, h - 1 - p)) if prof else (r - p) / max(1, h - 1 - p))))
             for r in range(h)]
        lo, hi = min(s), max(s)
        sh = np.zeros((h, w + hi - lo, 4), np.uint8)
        for r in range(h):
            sh[r, s[r] - lo:s[r] - lo + w] = out[r]
        out, x = sh, x + lo
    if t.get("flip") or t.get("rot"):
        ax, ay = t.get("about", (x + out.shape[1] / 2, y + out.shape[0] / 2))
        ys, xs = np.nonzero(out[..., 3] > 0)
        fx, fy = xs + x + 0.5, ys + y + 0.5
        if t.get("flip"):
            fx = 2 * ax - fx
        for _ in range(t.get("rot", 0) % 4):
            fx, fy = ax + (fy - ay), ay - (fx - ax)
        tx, ty = np.floor(fx).astype(int), np.floor(fy).astype(int)
        nx, ny = tx.min(), ty.min()
        new = np.zeros((ty.max() - ny + 1, tx.max() - nx + 1, 4), np.uint8)
        new[ty - ny, tx - nx] = out[ys, xs]
        out, x, y = new, nx, ny
    return out, x + t.get("dx", 0), y + t.get("dy", 0)


# ------------------------------------------------------------------------------------------------ the legs
# The run's and the death's legs are the idle's own (the user: 「走路时和待机时 左腿不一样了？」 on legs drawn in the
# design's colours): the near thigh is the design's striped stocking (its rows THIGH_ROWS, each row's squares less the
# outline square at each end) laid along hip -> knee - each square near the bone takes the stocking row at that length
# and its square at that side (league_varus's legs), so its stripes and colours are the idle's; the boot is the design's
# whole boot (cuff, buckle, laces, sole), never turned standing (「脚变形」 on turned feet), hanging from the knee. The far
# thigh (hidden by the gun as drawn) takes the far knee's own skin rows the same way where it shows; the far boot is the
# design's knee and boot. One outline ring round each thigh; the boot over it.
GROUND = 81.5                   # the soles' bottom edge
THIGH_ROWS = {"near": (56, 67), "far": (65, 66)}
KNEE = {"near": (31.5, 67.0), "far": (55.0, 64.5)}       # where the boot's top meets the thigh (design squares)
HIP = {"near": (38.5, 55.5), "far": (46.0, 55.5)}
PINKS = {"430F47", "690E5A", "93146E", "652D77", "CC2588", "F62893", "EE4AB2", "F68EDB", "7E274D", "A9439D", "DC6ACA",
         "8E58AB", "E0A6E3", "AE114A", "210F3D"}


class Legs:
    def __init__(self, d, M):
        hx = hexes(d)
        yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
        r0, r1 = THIGH_ROWS["near"]
        stock = M["leg_r"] & np.isin(hx, list(PINKS)) & (yy >= r0) & (yy <= r1)
        self.slices = {"near": [], "far": []}
        thigh = np.zeros_like(stock)
        for y in range(r0, r1 + 1):
            xs = np.nonzero(stock[y])[0]
            self.slices["near"].append(d[y, xs.min():xs.max() + 1].copy())
            thigh[y, xs.min() - 1:xs.max() + 2] = True
        thigh |= M["leg_r"] & (yy < r0)                    # the skin above the stocking, under her shorts
        thigh &= M["leg_r"]
        f0, f1 = THIGH_ROWS["far"]
        skin = M["leg_f"] & ~np.isin(hx, ["0D0117"])
        for y in range(f0, f1 + 1):
            xs = np.nonzero(skin[y])[0]
            self.slices["far"].append(d[y, xs.min():xs.max() + 1].copy())
        rest = M["leg_r"] & ~thigh                         # the boot: the largest piece left (not the stocking's
        lbl, n = ndimage.label(rest, structure=np.ones((3, 3)))     # stray edge squares)
        big = 1 + int(np.argmax(ndimage.sum(rest, lbl, range(1, n + 1))))
        self.boot = {"near": piece(d, lbl == big), "far": piece(d, M["leg_f"])}
        self.boot_h = {k: GROUND - KNEE[k][1] for k in KNEE}
        self.lt = {k: float(np.hypot(*np.subtract(KNEE[k], HIP[k]))) for k in KNEE}

    def thigh(self, key, H, K):
        """{(x, y): rgba} the thigh along hip H -> knee K (square edges), the stocking's (skin's) rows along it."""
        H, K = np.asarray(H, float), np.asarray(K, float)
        v = K - H
        L = max(1e-6, float(np.hypot(*v)))
        u = v / L
        n = np.array((u[1], -u[0]))                     # down -> +x: a row's left stays on the left
        sl = self.slices[key]
        cells = {}
        for y in range(int(math.floor(min(H[1], K[1]))) - 6, int(math.ceil(max(H[1], K[1]))) + 6):
            for x in range(int(math.floor(min(H[0], K[0]))) - 6, int(math.ceil(max(H[0], K[0]))) + 6):
                p = np.array((x + 0.5, y + 0.5)) - H
                t, s_ = float(p @ u), float(p @ n)
                if t < -1.0 or t > L + 0.5:
                    continue
                row = sl[int(round(min(1.0, max(0.0, t / L)) * (len(sl) - 1)))]
                xi = int(math.floor(len(row) / 2 + s_))
                if 0 <= xi < len(row) and row[xi][3]:
                    cells[(x, y)] = row[xi]
        return cells

    def items(self, key, hip, knee, turn=0):
        """Items (z, name, picture, x, y) of one leg: its thigh hip -> knee and its whole boot at the knee (turned
        `turn` quarter turns counter-clockwise about the knee: lying)."""
        z = Z["leg_r"] if key == "near" else Z["leg_f"]
        img, x0, y0 = cells_img(fold(self.thigh(key, hip, knee)))
        bimg, (bx, by) = self.boot[key]
        kx, ky = KNEE[key]
        if turn:
            bimg, bx, by = transformed(bimg, bx, by, dict(rot=turn, about=(kx, ky)))
        return [(z, "thigh_" + key, img, x0, y0),
                (z + 0.1, "boot_" + key, bimg, int(round(bx + knee[0] - kx)), int(round(by + knee[1] - ky)))]


def fold(cells, outline=O):
    """A thigh's squares with the outline ring closed round them (the slices carry no edge squares of their own)."""
    out = dict(cells)
    for (x, y) in list(cells):
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ddx, y + ddy)
            if q not in cells:
                out.setdefault(q, np.array((*outline, 255), np.uint8))
    return out


def cells_img(cells):
    """{(x, y): rgb} -> (picture, x0, y0)."""
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    x0, y0 = min(xs), min(ys)
    img = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
    for (x, y), c in cells.items():
        img[y - y0, x - x0, :3] = np.asarray(c)[:3]
        img[y - y0, x - x0, 3] = 255
    return img, x0, y0


# ------------------------------------------------------------------------------------------------ the zapper
# Neither arm is ever re-posed: moving one bares body the picture never drew (her waist under the near forearm, her chest
# under the far arm) and every way of drawing it was a deformation (the user: 「手有点变形啊」, 「你再查查吧哥们 各种变形」 on
# a mirrored hand, a sheared upper arm and a painted-in waist). W puts the zapper - the design's own, turned a quarter
# clockwise (its brass ring, the muzzle, forward) - into the near hand where it holds the gun's rear grip, over the
# glove's fingers.
GRIP = (45.0, 44.0)             # the near gloved fist's middle
ZAP_IN_HAND = (1, -2)           # the turned zapper's top-left from the fist's middle: its grip end in the fingers


# ------------------------------------------------------------------------------------------------ composing
UNITS = {"upper": ["fish", "curl", "braid_f", "braid_n", "torso", "zap", "head", "arm_f", "gun", "arm_n", "arm_lo",
                   "held", "zap_held"]}
Z = {name: i for i, name in enumerate(PARTS)}
Z["held"] = Z["braid_f"] + 0.5          # Fishbones shouldered: in front of the far braid, behind everything else


def compose(d, pieces, pose, legs=None):
    """pose: {"dx", "dy": the whole figure; "upper": the upper body over the drawn legs (dx, dy); a part's name: its
    transform (dx, dy, shear, flip, rot, about); "held": where Fishbones shouldered goes (its picture's top-left);
    "legs": {"near" / "far": (hip, knee)} the run's thighs (Legs.items); "zap_hand": the zapper in the near hand;
    "curl_on": the far braid's curl on its end; "prone": the death on her back (prone_items); "hide": parts left out}."""
    f = Frame(d)
    gdx, gdy = pose.get("dx", 0), pose.get("dy", 0)
    pose = dict(pose)
    items = []
    hide = set(pose.get("hide", ()))
    if pose.get("held") is not None:
        hide.add("fish")
        items.append((Z["held"], "held", pieces["_held"], *pose["held"]))
    if pose.get("zap_hand"):
        hide.add("zap")
        zimg, (zx, zy) = pieces["zap"]
        zt, _, _ = transformed(zimg, zx, zy, dict(rot=3, about=(zx + zimg.shape[1] / 2, zy + zimg.shape[0] / 2)))
        items.append((Z["arm_lo"] + 0.05, "zap_held", zt, int(GRIP[0] + ZAP_IN_HAND[0]), int(GRIP[1] + ZAP_IN_HAND[1])))
    lg = pose.get("legs")
    if lg:
        hide |= {"leg_r", "leg_f"}
        for key in ("far", "near"):
            items += legs.items(key, *lg[key])
    for name in PARTS:
        if name in hide:
            continue
        img, (x0, y0) = pieces[name]
        items.append((Z[name], name, img, x0, y0))
    if pose.get("prone"):
        items = prone_items(pieces, pose["prone"], legs, pose)
    # the far braid's curl goes where the braid's last row went (its swing), and onto the braid's end with "curl_on"
    bf = pose.get("braid_f", {})
    last = 0
    if bf.get("shear"):
        prof = bf.get("profile")
        last = int(round(bf["shear"] * (prof(1.0) if prof else 1.0)))
    if pose.get("curl_on"):
        pose["curl"] = dict(dx=CURL_ON[0] + last, dy=CURL_ON[1])
    elif last:
        pose["curl"] = dict(dx=last)
    for _, name, img, x0, y0 in sorted(items, key=lambda t: t[0]):
        out, x, y = transformed(img, x0, y0, dict(pose.get("held_t" if name == "held" else name, {})))
        for unit, members in UNITS.items():
            if name in members and unit in pose:
                out, x, y = transformed(out, x, y, pose[unit])
        f.stamp(out, x + gdx, y + gdy)
    return f.a


# ------------------------------------------------------------------------------------------------ the death
# League's death and her old sheet's: knocked over backwards onto her back. Her head, body and arms turn a quarter
# counter-clockwise about her hips (lossless: no square redrawn), the braids first gathered in behind her back (their
# rows shifted toward it, BRAID_GATHER) and lying under her (her back on the ground, what of them would be below it not
# drawn) so she is not propped on a heap of hair; her near leg is drawn the run's way from the turned hip (the far one
# lies behind it, out of sight) - thrown up as she lands, then lying along the ground - with the design's whole boot
# turned (DEAD_TURN); Pow-Pow, dropped, lies across her thighs in front of them (the hips' join under it: 「死亡后腿断了？」),
# Fishbones on the ground behind her head.
PRONE_PIVOT = (40.0, 56.0)
BRAID_GATHER = (18, 6)          # the near / far braid's tips moved toward her back (columns, before the turn)
# the near knee from the turned hip (dx, dy in squares): "up" - the leg thrown straight up as she lands, "flat" - lying
DEAD_LEGS = {"up": (0, -13), "flat": (13, 0)}
DEAD_TURN = {"up": 2, "flat": 1}         # the boots: upside down (soles to the sky), or lying toes-up


def loose_gun(d, M, img, at):
    """Pow-Pow out of her hands (dropped as she dies): the gun's own squares (its largest piece: the specks its hands'
    edges left are not kept), and under where the hands held it - the far hand on the front handle, the near glove at the
    rear grip, never drawn - its casing closed: each such square inside the gun's closed outline takes the colour of the
    gun square under it (36 squares)."""
    x0, y0 = at
    op = img[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    main = lbl == 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
    out = img.copy()
    out[~main] = 0
    H, W = img.shape[:2]
    hand = (M["arm_f"] | M["arm_lo"])[y0:y0 + H, x0:x0 + W]
    fill = (ndimage.binary_closing(main, structure=np.ones((7, 7), bool)) | main) & ~main & hand
    for y, x in sorted(zip(*np.nonzero(fill)), key=lambda t: -t[0]):
        yy = y + 1
        while yy < H and not out[yy, x, 3]:
            yy += 1
        if yy < H:
            out[y, x] = out[yy, x]
    return out


def prone_items(pieces, pr, legs, pose):
    """Items of the body on its back: pr = {"lift": rows off the ground, "dx": columns on, "legs": "up" | "flat",
    "gun": (dx, dy) of the dropped gun, "fish": (dx, dy) of Fishbones lying behind her}."""
    group = []
    gather = {"braid_n": dict(shear=BRAID_GATHER[0], pivot=5, profile=lambda t: t ** 1.2),
              "braid_f": dict(shear=BRAID_GATHER[1], pivot=3, profile=lambda t: t ** 1.2)}
    for name in ("curl", "braid_f", "braid_n", "torso", "zap", "head", "arm_n", "arm_lo"):
        img, (x0, y0) = pieces[name]
        if name == "curl":
            t = dict(dx=CURL_ON[0] + BRAID_GATHER[1], dy=CURL_ON[1])
        else:
            t = gather.get(name, {})
        img, x0, y0 = transformed(img, x0, y0, t)
        group.append((Z[name], name, img, x0, y0))
    px, py = PRONE_PIVOT
    turned = [(z, n) + transformed(img, x, y, dict(rot=1, about=(px, py))) for z, n, img, x, y in group]
    bottom = max(y + img.shape[0] for _, n, img, x, y in turned if n not in ("braid_n", "braid_f", "curl"))
    sy = int(round(GROUND - bottom)) - pr.get("lift", 0)
    sx = pr.get("dx", 0)
    items = [(z, n, img, x + sx, y + sy) for z, n, img, x, y in turned]
    hx, hy = px + sx, py + sy                           # the turned hip
    mode = pr.get("legs", "flat")
    kdx, kdy = DEAD_LEGS[mode]                         # the far leg lies behind the near one, out of sight
    items += legs.items("near", (hx, hy), (hx + kdx, hy + kdy), turn=DEAD_TURN[mode])
    left = min(x for _, _, img, x, y in items)
    right = max(x + img.shape[1] for _, _, img, x, y in items)
    if pr.get("fish") is not None:
        fimg = pieces["_held"]
        fdx, fdy = pr["fish"]
        items.append((Z["fish"], "held", fimg, left - fimg.shape[1] + 18 + fdx, int(round(GROUND - fimg.shape[0])) + fdy))
    gimg = pieces["_gun_loose"]
    gdx, gdy = pr.get("gun", (0, 0))
    # across her thighs, in front of them: her hips' join to the legs is under it
    items.append((Z["arm_lo"] + 1, "gun", gimg, int(round(hx - 8)) + gdx, int(round(GROUND - gimg.shape[0])) + gdy))
    return items


# ------------------------------------------------------------------------------------------------ poses
STAND = {}


def braids(k, kf=None):
    """The braids swinging: their tips k columns (right +) from where they hang, the roots still (they lag a beat behind
    the body: back when she lunges forward, forward when she is knocked back)."""
    return {"braid_n": dict(shear=k, pivot=5, profile=lambda t: t ** 1.5),
            "braid_f": dict(shear=kf if kf is not None else k, pivot=3, profile=lambda t: t ** 1.5)}


def P(dx=0, held=None, **kw):
    """A pose: the whole figure moved dx columns, legs and all (the upper body slid over planted legs changed how much of
    the stocking her shorts cover: 「放技能的时候左腿有点变形」), Fishbones shouldered at `held`, the braids' swing and any
    part's transform in kw."""
    out = dict(kw)
    if dx:
        out["dx"] = dx
    if held is not None:
        out["held"] = held
    return out


# Fishbones shouldered: its grip (hd/fishbones_held.png square (52, 22)) in the far hand on the gun's front handle
GRIP_HELD = (52, 22)
FAR_HAND = (64, 43)
HELD_AT = (FAR_HAND[0] - GRIP_HELD[0], FAR_HAND[1] - GRIP_HELD[1] + 3)   # 3 rows low: the mouth ~8 px over the pivot


def held(dx=0, dy=0):
    return (HELD_AT[0] + dx, HELD_AT[1] + dy)


# The run (8 frames of 117 ms), set by hand after League's Jinx_minigun_run seen from the side (hd/jinx_run_joints.json:
# tools/lol/league_joints.py on hd/poses_side.json, its run's frames; the chibi sprint swings the thighs -28 to +67
# degrees): the thighs on RUN_LEGS's angles from hips RUN_HIP_X apart, the boots the design's own hanging from the knees,
# the hips as high as the planted leg holds them (the body bobbing with the steps), the upper body RUN_LEAN columns
# ahead of the hips, the braids streaming back.
RUN_HIP_X = {"near": 40.0, "far": 44.0}
RUN_HIP_Y = 55.0                # the hips' row with the planted thigh at 30 degrees: the upper body as drawn
RUN_LEAN = 2
BRAID_RUN = [(-5, -15), (-6, -16), (-5, -15), (-4, -14), (-5, -15), (-6, -16), (-5, -15), (-4, -14)]


# per frame: each leg's thigh angle (degrees from straight down, + = the knee forward) and how many rows it is lifted
# (the whole leg, its top sliding up under her shorts) - the planted leg (lift 0) stands its boot on the ground and holds
# the hips; one leg reaches forward and lands while the other pushes off behind, then they pass, half a cycle apart
RUN_LEGS = [((30, 0), (-32, 2)), ((15, 0), (-20, 5)), ((0, 0), (5, 6)), ((-18, 0), (25, 3)),
            ((-32, 2), (30, 0)), ((-20, 5), (15, 0)), ((5, 6), (0, 0)), ((25, 3), (-18, 0))]


RUN_LT = {"near": 13.5, "far": 11.0}   # thigh lengths: standing straight, both hold the hips at the same height (the far
                                        # boot is the taller by its knee)


def run_poses():
    lt = RUN_LT
    bh = {k: GROUND - KNEE[k][1] for k in KNEE}
    out = []
    for i, (nl, fl) in enumerate(RUN_LEGS):
        spec = {"near": nl, "far": fl}
        ang = {k: math.radians(spec[k][0]) for k in spec}
        plant = [k for k in spec if spec[k][1] == 0]
        hy = max(GROUND - bh[k] - lt[k] * math.cos(ang[k]) for k in plant)
        legs = {}
        for key in ("far", "near"):
            hip = np.array((RUN_HIP_X[key], hy - spec[key][1]))
            knee = hip + lt[key] * np.array((math.sin(ang[key]), math.cos(ang[key])))
            legs[key] = (tuple(hip), tuple(knee))
        kn, kf = BRAID_RUN[i]
        out.append(dict(upper=dict(dx=RUN_LEAN, dy=int(round(hy - RUN_HIP_Y))), curl_on=True, legs=legs,
                        **braids(kn, kf)))
    return out


POSES = {
    # the minigun: kicked back a column on each burst (the kit's shot on the 3rd frame), the braids swinging with it
    "attack": [STAND, P(), P(-1, **braids(1)), P(**braids(1, 0)), P(-1, **braids(2, 1)), P(**braids(1, 0))],
    # Fishbones swung onto her far shoulder (its grip in the hand that held the gun's front handle), the rocket on the
    # 4th frame (183 ms): the launcher kicks up and back, she rocks back a column
    "rocket": [P(held=held(-4, -5), **braids(-1)), P(held=held(-1, -1)), P(held=held()),
               P(-1, held=held(-3, -2), **braids(2, 1)), P(held=held(-1, -1), **braids(1)), P(held=held())],
    # knocked back two columns, the braids flung forward; then halfway back
    "hit": [P(-2, **braids(3, 2)), P(-1, **braids(1))],
    # Super Mega Death Rocket (League's spell4): Fishbones heaved up off her back, swung onto her shoulder to aim, the
    # rocket on the 5th frame (283 ms) blowing her back off her feet, the landing, Fishbones back on her back as she
    # rights herself
    "ult": [P(fish=dict(dx=2, dy=-4), **braids(-1)),
            P(fish=dict(dx=6, dy=-14), **braids(-2)),
            P(held=held(-2, -8), **braids(-2)),
            P(held=held(), **braids(-1)),
            P(-6, held=held(-3, -2), dy=-4, **braids(4, 3)),
            P(-8, held=held(-1, -1), **braids(2)),
            P(-3, **braids(1))],
    # struck: knocked back, she reels, topples over backwards (legs thrown up as she lands), bounces and lies flat
    "dead": [P(-2, **braids(3, 2)),
             P(-4, **braids(5, 3)),
             dict(prone=dict(lift=10, dx=-14, legs="up", gun=(-6, -10), fish=(4, -12))),
             dict(prone=dict(lift=2, dx=-18, legs="up", gun=(-2, 0), fish=(0, 0))),
             dict(prone=dict(lift=0, dx=-18, legs="flat", fish=(0, 0))),
             dict(prone=dict(lift=1, dx=-18, legs="flat", fish=(0, 0))),
             dict(prone=dict(lift=0, dx=-18, legs="flat", fish=(0, 0))),
             dict(prone=dict(lift=0, dx=-18, legs="flat", fish=(0, 0)))],
}


def Z_(dx=0, **kw):
    """W's pose: the zapper in the near hand."""
    out = P(dx, **kw)
    out["zap_hand"] = True
    return out


# W (Zap!): the zapper out of its holster into the hand on the gun's grip, levelled, its charge glowing from the muzzle
# (jinx_bake.json w_charge), the shot on the 6th of the 8 frames (383 ms) jolting her back a column, holstered again.
# The sheet's frames are these split where the charge's frames change.
BASE = {
    "skill": ([60, 60, 60, 70, 80, 90, 90, 90],
              [STAND, Z_(), Z_(1), Z_(1), Z_(1), Z_(-1, **braids(1)), Z_(), STAND]),
    # E (Flame Chompers!): she rocks back and lunges into the throw (the chompers leave on the 4th frame, 200 ms), the
    # braids swinging behind her, and settles
    "skill2": ([60, 60, 60, 60, 70, 80, 90],
               [STAND, P(-2, **braids(2, 1)), P(**braids(0)), P(3, **braids(-3, -2)), P(4, **braids(-4, -3)),
                P(2, **braids(-2, -1)), P(1, **braids(-1))]),
}


# jinx_bake.json's pictures were drawn round the old 1x sprite's zapper (its muzzle 13 px ahead of the pivot, 8 up): each
# effect moved (dx, dy) 1x px onto this one's (the zapper in the hand on the gun's grip, its muzzle (62, 45) squares)
FX_AT = {"w_charge": (-5.3, 2.9)}


def expand(base_ms, poses, ms):
    """The base poses on the sheet's frames (a sheet frame takes the base frame its start falls in)."""
    cum = np.cumsum([0] + list(base_ms))
    out, t = [], 0
    for m in ms:
        out.append(poses[int(np.searchsorted(cum, t, side="right") - 1)])
        t += m
    return out


# ------------------------------------------------------------------------------------------------ the rig
def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.px = PIVOT_COL
    D.d0 = D.d.copy()
    return D


def drop_stray_outline(can):
    """Outline squares with no coloured square within two (a turned or swung part's corner, the picture's own stray at
    the near braid's tip) taken out, until none is left (league_shen's bare_outline_gone)."""
    out = can.copy()
    while True:
        op = out[..., 3] > 0
        isout = op & (np.abs(out[..., :3].astype(int) - np.array(O)).sum(-1) < 30)
        near = ndimage.binary_dilation(op & ~isout, structure=np.ones((5, 5), bool))
        stray = isout & ~near
        if not stray.any():
            return out
        out[stray] = 0


class JinxRig(R.Rig):
    def finish(self, can):
        return drop_stray_outline(super().finish(can))


def on_rig(rig, a):
    """A composed frame (design squares + PAD) on the rig's canvas (the design's (0, 0) at ox, oy)."""
    can = rig.canvas()
    ys, xs = np.nonzero(a[..., 3] > 0)
    Y, X = ys - PAD + rig.oy, xs - PAD + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    can[Y[ok], X[ok]] = a[ys[ok], xs[ok]]
    can[rig.GY:] = 0
    return can


class Poser:
    def __init__(self, d):
        self.d = d
        self.M = masks(d)
        self.pieces = {n: piece(d, m) for n, m in self.M.items()}
        self.pieces["_held"] = np.asarray(Image.open(lp(os.path.join(HD, "fishbones_held.png"))).convert("RGBA"))
        self.legs = Legs(d, self.M)
        self.pieces["_gun_loose"] = loose_gun(d, self.M, *self.pieces["gun"])

    def check(self):
        """Standing, the parts rebuild the design square for square; the parts cover it once."""
        d = self.d
        op = d[..., 3] > 0
        n = sum(m.astype(int) for m in self.M.values())
        if (n[op] != 1).any() or (n[~op] != 0).any():
            sys.exit(f"parts: {int((n[op] != 1).sum())} squares not in exactly one part")
        a = self.frame(STAND)
        got = a[PAD:PAD + d.shape[0], PAD:PAD + d.shape[1]]
        if (got != d).any() or int((a[..., 3] > 0).sum()) != int(op.sum()):
            sys.exit("the standing pose does not rebuild the design")

    def frame(self, pose):
        return compose(self.d, self.pieces, pose, self.legs)


def frames(rig):
    d = rig.D.d0
    ps = Poser(d)
    ps.check()
    sheet = R.sheet_of(HERO)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        ms = [m for _, m in sheet[tag]]
        n = len(ms)
        if tag in BASE:
            poses = expand(*BASE[tag], ms)
        elif tag in POSES:
            poses = POSES[tag]
        elif tag == "run":
            poses = run_poses()
        else:
            poses = [STAND] * n
        if len(poses) != n:
            sys.exit(f"{tag}: {len(poses)} poses for {n} frames")
        fr = [on_rig(rig, ps.frame(p)) for p in poses]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        out[tag] = list(zip(fr, ms))
    out["idle"] = [(fr_, m) for fr_, m in out["idle_base"]]
    with open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8") as f:
        bake = json.load(f)
    for e in bake["items"]:                             # the old sprite's muzzles -> this one's (FX_AT)
        ddx, ddy = FX_AT.get(e["tag"], (0, 0))
        e["dx"], e["dy"] = e.get("dx", 0) + ddx, e.get("dy", 0) + ddy
    acts = rig.bake(out, cfg=bake)
    return {t: acts[t] for t in sheet if t in acts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = JinxRig(D, pad=(110, 130, 110, 30))
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        ps = Poser(D.d0)
        ps.check()
        tint = {"fish": (90, 90, 230), "braid_n": (0, 220, 255), "braid_f": (0, 90, 200), "head": (255, 230, 0),
                "torso": (60, 200, 60), "arm_n": (255, 140, 0), "arm_f": (255, 60, 160), "gun": (170, 0, 255),
                "zap": (0, 255, 160), "leg_r": (255, 0, 0), "leg_f": (140, 70, 20), "curl": (0, 60, 140),
                "arm_lo": (200, 100, 0)}
        d = D.d0
        img = np.zeros(d.shape[:2] + (3,), np.uint8) + 200
        for name, m in ps.M.items():
            img[m] = (d[m, :3] * 0.45 + np.array(tint[name]) * 0.55).astype(np.uint8)
        Image.fromarray(img).resize((d.shape[1] * 8, d.shape[0] * 8), Image.NEAREST).save(
            os.path.join(a.parts, "jinx_parts.png"))
        return
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
