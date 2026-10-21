#!/usr/bin/env python3
"""league_orianna's action frames for the chibi design (Q版, 2026-10-22), posed by me from the approved designs after
League's own clips, frame by frame (the user: 「60帧吧 不交给codex了 你自己慢慢处理 合理利用工具 做到完美了喊我review」).

    python tools/art/rig_orianna.py --parts DIR       # the side design cut into its parts, tinted, at 12x
    python tools/art/rig_orianna.py --review DIR      # every tag next to League's clip at 6x + one GIF
    python tools/art/rig_orianna.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero orianna && python tools/art/ppu_hd.py --hero orianna

The designs (tools/art/design_orianna_chibi.py, the user's pick A: head 0.66 / body 0.80 of Codex's Q1 drafts):
  chibi/design-front.png   3/4 front, 58 x 86: the idle, and THE head of every frame (one face: memory one-face-all-frames)
  chibi/design-side.png    side-on facing right, 48 x 87: every action's body, arms and legs
Both stand on a 128 canvas with the soles on row 117; here they are put on one bigger canvas at the same place.
How a frame is made (rigkit's and ppu_rig's rules):
  * the front head is one block, moved by whole squares, never turned or sheared;
  * the torso (neck, bodice, bust, shoulder balls) and the skirt are the side design's own squares, moved whole; a lean
    is an even shear of whole rows above the hips (league_zeri's run) - the head rides on the top row's shift;
  * the doll's limbs are rigid pieces of the side design - thigh, shin, boot; upper arm, forearm with the hand - each
    turned about its joint (RotSprite: rigkit.turn, quarter turns exact) to the pose's angle and set at the joint the
    pieces above it put down; the brown ball joints are stamped over the seams; boots stay flat (league_caitlyn's run);
  * the angles come from League's skeleton (tools/lol/native_pose.py "dump_joints" on assets/source/orianna/poses.json,
    the same renders the pose references were made from) as changes from League's side-on idle, and are then set frame
    by frame in POSES where a doll's straight limbs or the big head need it; planted feet are put on the ground by IK
    with our own bone lengths.
The ball is not in her frames (its own picture in the effects).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import rigkit as RK  # noqa: E402
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "orianna")
SIDE = os.path.join(SRC, "chibi", "design-side.png")
FRONT = os.path.join(SRC, "chibi", "design-front.png")
STEM = os.path.join(ROOT, "league", "champions", "league_orianna")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "or_q")
JOINTS = os.path.join(TMP, "pose_n", "orianna_joints.json")     # native_pose.py's dump (Riot's data: local only)
OUTLINE = (9, 3, 15)
CW, CH = 180, 160                  # the canvas, squares
OX, OY = 26, 30                    # where a design's (0, 0) goes on it
SOLE = 117 + OY                    # the soles' row
PIV_X = 64 + OX                    # the standing point's column (the middle between the feet)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def on_canvas(a):
    can = np.zeros((CH, CW, 4), np.uint8)
    can[OY:OY + a.shape[0], OX:OX + a.shape[1]] = a
    return can


# ------------------------------------------------------------------------------------------------ the parts
def box(shape, x0, y0, x1, y1):
    """Squares in columns x0..x1 and rows y0..y1 (inclusive), design coordinates."""
    m = np.zeros(shape[:2], bool)
    m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    return m


def rows_cols(shape, spans):
    """{row: (first col, last col)} -> mask (design coordinates)."""
    m = np.zeros(shape[:2], bool)
    for y, (x0, x1) in spans.items():
        m[y, x0:x1 + 1] = True
    return m


CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def is_outline(a):
    return (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - OUTLINE).sum(-1) < 12)


def is_brown(a):
    """The ball joints' browns (and the hair's darkest): red over blue, dull."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (r > b + 15) & (r < 160) & ~is_outline(a)


def is_gold(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (r > b + 60) & (r >= 160)


class Piece:
    """A sprite cut from a design with its joint (continuous design coordinates, square centres at +0.5)."""

    def __init__(self, a, mask, joint, ring=True):
        # its own coloured squares, and the outline squares edge-next to them (a moved piece keeps its own edge, and
        # never another part's: an arm's outline left in the torso drew loose black arcs once the arm moved)
        core = mask & (a[..., 3] > 0) & ~is_outline(a)
        m = core | (ndimage.binary_dilation(core, structure=CROSS) & is_outline(a) & (mask | ring))
        ys, xs = np.nonzero(m)
        self.y0, self.x0 = ys.min(), xs.min()
        s = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
        sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        mm = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        s[mm] = sub[mm]
        self.s = s
        self.mask = m
        self.j = (joint[0] - self.x0, joint[1] - self.y0)

    def part(self):
        return RK.Part(self.s, self.j)


# the side design's joints (continuous design coordinates: a square's centre is +0.5) and pieces, read square by square
# off design-side.png (the near limbs are image-left: the arm hanging back, the leg behind; League's side idle the same)
NECK = (62.5, 69.0)                # the neck's ball under the chin
N_SHOULDER = (57.0, 70.5)          # the near shoulder's ball (rows 69-71, cols 55-58)
N_ELBOW = (50.5, 79.0)             # the near elbow's ball (rows 78-79, cols 48-52)
N_WRIST = (43.5, 87.5)             # the near wrist's ball (rows 86-88, cols 42-44)
F_SHOULDER = (65.5, 72.0)          # the far shoulder, behind the bust
F_ELBOW = (71.5, 76.5)             # the far elbow's ball, at the bust's edge
N_HIP, N_KNEE, N_ANKLE = (57.5, 90.5), (56.5, 101.0), (52.0, 110.9)
F_HIP, F_KNEE, F_ANKLE = (64.5, 90.5), (71.5, 101.5), (74.0, 111.0)
HEAD_AT = (-3, -1)                 # the front head on the side body: moved 3 columns back and a row up (chin on the neck)

KEY_ROWS = {61: (45, 47), 62: (44, 48), 63: (43, 51), 64: (43, 53), 65: (43, 53), 66: (44, 53), 67: (45, 53),
            68: (44, 53), 69: (43, 55), 70: (42, 54), 71: (42, 55), 72: (42, 51), 73: (43, 51), 74: (45, 50)}
N_UPPER_ROWS = {72: (52, 56), 73: (52, 56), 74: (51, 56), 75: (50, 55), 76: (50, 55), 77: (52, 54)}
N_ELBOW_ROWS = {78: (48, 52), 79: (49, 51)}
N_LOWER_ROWS = {80: (48, 50), 81: (47, 50), 82: (46, 50), 83: (46, 50), 84: (45, 49), 85: (45, 47), 86: (41, 47),
                87: (41, 44), 88: (40, 44), 89: (39, 46), 90: (38, 46), 91: (38, 46), 92: (37, 46), 93: (37, 46),
                94: (37, 46), 95: (38, 45), 96: (38, 43), 97: (38, 42)}
F_LOWER_ROWS = {76: (71, 71), 77: (72, 74), 78: (72, 78), 79: (72, 80), 80: (75, 81), 81: (75, 82), 82: (75, 83),
                83: (77, 83), 84: (77, 83), 85: (80, 83), 86: (80, 82), 87: (81, 81)}
N_HAND_ROWS = {86: (41, 44), 87: (41, 44), 88: (40, 44), 89: (39, 46), 90: (38, 46), 91: (38, 46), 92: (37, 46),
               93: (37, 46), 94: (37, 46), 95: (38, 45), 96: (38, 43), 97: (38, 42)}
HAND_TIP = (40.5, 97.5)            # the claws' tips (the hand points from the wrist to here)
N_THIGH_ROWS = {94: (55, 58), 95: (54, 59), 96: (55, 59), 97: (55, 58), 98: (57, 58)}
N_KNEE_ROWS = {99: (55, 56), 100: (55, 57), 101: (55, 57), 102: (56, 56)}
N_SHIN_ROWS = {101: (52, 53), 102: (50, 54), 103: (50, 55), 104: (49, 56), 105: (49, 56), 106: (49, 56),
               107: (50, 55), 108: (50, 54)}
N_ANKLE_ROWS = {109: (50, 52), 110: (50, 53), 111: (50, 53)}
N_BOOT_ROWS = {112: (48, 49), 113: (48, 53), 114: (48, 54), 115: (48, 55), 116: (49, 56)}
SKIRT_TOP, SKIRT_BOTTOM = 83, 94   # the skirt's rows (its blades hang to 99 at cols 65-72)


def ramp_darker(a, steps=1):
    """Every metal colour `steps` shades darker on the design's own metal ramp (the far limbs), browns one shade
    darker on theirs; the outline stays."""
    metal = [(248, 246, 233), (198, 202, 203), (178, 184, 189), (152, 160, 168), (129, 137, 149), (97, 107, 121),
             (67, 77, 91), (42, 45, 59)]
    brown = [(148, 96, 69), (138, 85, 45), (115, 72, 40), (92, 56, 33), (66, 38, 22), (51, 29, 16), (34, 21, 18)]
    out = a.copy()
    for ramp in (metal, brown):
        for i, c in enumerate(ramp):
            m = (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - c).sum(-1) == 0)
            out[m, :3] = ramp[min(len(ramp) - 1, i + steps)]
    return out


class Kit:
    """The doll's pieces, cut once from the designs."""

    def __init__(self):
        self.side = load(SIDE)
        self.front = load(FRONT)
        S, F = self.side, self.front
        H, W = S.shape[:2]
        yy, xx = np.mgrid[:H, :W]
        op = S[..., 3] > 0
        # the front head: everything down to its chin row 68 but the key behind it (rows 63 on, columns left of 56)
        fop = F[..., 3] > 0
        self.head_mask = fop & (yy <= 68) & ~((yy >= 63) & (xx < 56))
        hm = np.zeros_like(F)
        hm[self.head_mask] = F[self.head_mask]
        self.head = np.roll(np.roll(hm, HEAD_AT[1], 0), HEAD_AT[0], 1)
        # the side design's own parts
        key = rows_cols(S.shape, KEY_ROWS)
        n_upper = rows_cols(S.shape, N_UPPER_ROWS)
        n_elbow = rows_cols(S.shape, N_ELBOW_ROWS)
        n_lower = rows_cols(S.shape, N_LOWER_ROWS)
        f_lower = rows_cols(S.shape, F_LOWER_ROWS)
        n_thigh = rows_cols(S.shape, N_THIGH_ROWS)
        n_knee = rows_cols(S.shape, N_KNEE_ROWS)
        n_shin = rows_cols(S.shape, N_SHIN_ROWS)
        n_ankle = rows_cols(S.shape, N_ANKLE_ROWS)
        n_boot = rows_cols(S.shape, N_BOOT_ROWS)
        side_head = op & (yy <= 67) & ~key
        skirt = op & (((yy >= SKIRT_TOP) & (yy <= SKIRT_BOTTOM) & (xx >= 47) & (xx <= 79))
                      | ((yy > SKIRT_BOTTOM) & (yy <= 99) & (xx >= 65) & (xx <= 72)
                         & (is_gold(S) | is_brown(S) | (xx == 71))))
        skirt &= ~(n_lower | n_thigh)
        legs_any = op & (yy > SKIRT_BOTTOM) & ~skirt
        torso = op & (yy >= 67) & (yy < SKIRT_TOP) & ~(key | n_upper | n_elbow | n_lower | f_lower | side_head)
        self.masks = dict(side_head=side_head, key=key, torso=torso, skirt=skirt, n_upper=n_upper, n_elbow=n_elbow,
                          n_lower=n_lower, f_lower=f_lower, n_thigh=n_thigh, n_knee=n_knee, n_shin=n_shin,
                          n_ankle=n_ankle, n_boot=n_boot,
                          legs_rest=legs_any & ~(n_thigh | n_knee | n_shin | n_ankle | n_boot))
        self.key = Piece(S, key, (52.0, 70.5))
        self.torso = Piece(S, torso, NECK, ring=False)
        self.skirt = Piece(S, skirt, (61.0, 90.5), ring=False)
        self.n_upper = Piece(S, n_upper, N_SHOULDER)
        self.n_elbow = Piece(S, n_elbow, N_ELBOW)
        self.n_lower = Piece(S, n_lower, N_ELBOW)
        self.f_lower = Piece(S, f_lower, F_ELBOW)
        self.n_knee = Piece(S, n_knee, N_KNEE)
        self.n_ankle = Piece(S, n_ankle, N_ANKLE)
        self.n_boot = Piece(S, n_boot, N_ANKLE)
        self.n_shin = Piece(S, n_shin, N_KNEE)
        # the thigh runs on under the skirt to the hip: its top visible row repeated up to it (hidden when it hangs)
        th = n_thigh.copy()
        ext = S.copy()
        for y in range(int(N_HIP[1]) - 1, 94):
            ext[y, 54:60] = S[95, 54:60]
            th[y, 54:60] = True
        self.n_thigh = Piece(ext, th, N_HIP)
        # the hand with its wrist ball, in its eight lossless orientations (and a shade darker for the far arm)
        hand = rows_cols(S.shape, N_HAND_ROWS)
        self.hand = Piece(S, hand, N_WRIST)
        self.hands = hand_variants(self.hand.s, self.hand.j, HAND_TIP)
        self.hands_dark = hand_variants(ramp_darker(self.hand.s), self.hand.j, HAND_TIP)
        # the far limbs: the near ones a shade darker (one leg, one arm for both sides, as a doll's are)
        self.dark = {}
        for name in ("n_upper", "n_lower", "n_thigh", "n_shin", "n_boot", "n_knee", "n_ankle", "n_elbow"):
            p = getattr(self, name)
            q = Piece.__new__(Piece)
            q.s, q.j, q.x0, q.y0, q.mask = ramp_darker(p.s), p.j, p.x0, p.y0, p.mask
            self.dark[name] = q


def heading(a, b):
    """Screen angle of a -> b, degrees counter-clockwise from +x (y grows down)."""
    return math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))


def wrap(d):
    return (d + 180.0) % 360.0 - 180.0


def along(p, deg, length):
    t = math.radians(deg)
    return (p[0] + math.cos(t) * length, p[1] - math.sin(t) * length)


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def ik(hip, ankle, l1, l2, bend=1):
    """The knee for an ankle within reach (pulled in when not), bones l1 / l2; bend +1 puts the knee forward (+x)."""
    d = dist(hip, ankle)
    d = max(abs(l1 - l2) + 1e-3, min(l1 + l2 - 1e-3, d))
    h0 = heading(hip, ankle)
    a = math.degrees(math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
    # the knee on the forward side: for a leg hanging down (heading ~ -90) forward is +x, a clockwise turn of the hip ray
    k = along(hip, h0 + a * bend, l1)
    if (k[0] - hip[0]) * bend < (along(hip, h0 - a * bend, l1)[0] - hip[0]) * bend:
        k = along(hip, h0 - a * bend, l1)
    return k


def stamp(can, sprite, joint, at, under=False):
    """sprite (RGBA) with its joint (sprite coords, continuous) put with the joint on the canvas point `at`."""
    ox = int(round(at[0] - joint[0]))
    oy = int(round(at[1] - joint[1]))
    h, w = sprite.shape[:2]
    y0, x0 = max(0, oy), max(0, ox)
    y1, x1 = min(can.shape[0], oy + h), min(can.shape[1], ox + w)
    if y1 <= y0 or x1 <= x0:
        return
    src = sprite[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    dst = can[y0:y1, x0:x1]
    m = src[..., 3] > 0
    if under:
        m &= dst[..., 3] == 0
    dst[m] = src[m]


def turned(piece, deg):
    """(sprite, joint) of a piece turned deg counter-clockwise on screen about its joint (RotSprite, quarter turns
    exact; a turn under a degree is none)."""
    if abs(deg) < 1.0:
        return piece.s, piece.j
    p = RK.turn(piece.part(), deg)
    return p.s, p.j


def sheared(a, k, row0):
    """Rows above row0 moved k columns per row they are above it (whole rows, rounded): the upper body's lean."""
    out = np.zeros_like(a)
    for y in range(a.shape[0]):
        dx = int(round(k * (row0 - y))) if y < row0 else 0
        if dx == 0:
            out[y] = a[y]
        elif dx > 0:
            out[y, dx:] = a[y, :-dx]
        else:
            out[y, :dx] = a[y, -dx:]
    return out


class Pose(dict):
    """A frame's pose. Keys (all optional; the side design's own stance when absent):
    dx, dy           the hips moved (squares, canvas)
    lean             columns the neck row moves ahead of the hips (an even shear of the upper body's rows)
    head             (dx, dy) the head moved further than the neck
    key              (dx, dy) or "flip" / turns of the wind-up key
    n_up, n_lo       the near arm's upper arm / forearm headings (screen degrees), or None for the design's
    f_up, f_lo       the far arm's; f_piece "own" (the design's foreshortened far forearm) or "long" (the near one)
    n_leg, f_leg     None (the design's), ("ang", thigh, shin) headings, or ("ik", ankle_x, ankle_y) in design
                     coordinates moved with the hips' dx only (the ground does not move)
    n_boot, f_boot   quarter turns of the boot (0 flat)
    lift             the whole figure lifted (squares) - a jump
    order            "arm_front" puts the near arm over the head
    """


# the limbs drawn as metal bands in the design's own shades (lit side first: league_garen's PPU run, league_jarvaniv's
# legs - straight greave segments in the design's greys with an outline ring, the design's own joints and boots pasted)
M = {"B": (248, 246, 233), "A": (198, 202, 203), "x": (178, 184, 189), "v": (152, 160, 168), "s": (129, 137, 149),
     "m": (97, 107, 121), "j": (67, 77, 91), "e": (42, 45, 59)}
DARKER = {"B": "A", "A": "x", "x": "v", "v": "s", "s": "m", "m": "j", "j": "e", "e": "e"}
PROFILES = {"thigh": "xBxvs", "shin": "ABxvsm", "upper": "BAxvm", "fore": "Bxsm"}
WIDTHS = {"thigh": (5.0, 5.0), "shin": (6.0, 5.0), "upper": (5.0, 4.0), "fore": (4.0, 4.0)}
LIGHT = (-0.6, -0.8)               # towards the light (upper left)
SHIN_PIECE = True                  # the shins are the design's own (a band read as another leg: no calf plate)


def band(layer, p0, p1, kind, far=False, ext0=0.0, ext1=0.0):
    """A limb's band from p0 to p1 (canvas, continuous) into layer: every square whose middle lies within the band
    (its width going from WIDTHS[kind][0] to [1]) coloured by where it lies across it, the lit side first; its own
    outline ring round it where the layer is clear."""
    w0, w1 = WIDTHS[kind]
    prof = PROFILES[kind]
    if far:
        prof = "".join(DARKER[DARKER[c]] for c in prof)
    vx, vy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(vx, vy) or 1e-6
    ux, uy = vx / L, vy / L
    nx, ny = -uy, ux
    lit = 1.0 if nx * LIGHT[0] + ny * LIGHT[1] >= 0 else -1.0
    r = max(w0, w1) / 2 + 2
    x0, x1 = int(math.floor(min(p0[0], p1[0]) - r - ext0 - ext1)), int(math.ceil(max(p0[0], p1[0]) + r + ext0 + ext1))
    y0, y1 = int(math.floor(min(p0[1], p1[1]) - r - ext0 - ext1)), int(math.ceil(max(p0[1], p1[1]) + r + ext0 + ext1))
    fill = np.zeros(layer.shape[:2], bool)
    col = np.zeros(layer.shape[:2] + (3,), np.uint8)
    for y in range(max(0, y0), min(layer.shape[0], y1 + 1)):
        for x in range(max(0, x0), min(layer.shape[1], x1 + 1)):
            cx, cy = x + 0.5 - p0[0], y + 0.5 - p0[1]
            t = cx * ux + cy * uy
            if t < -ext0 or t > L + ext1:
                continue
            tt = min(1.0, max(0.0, t / L))
            hw = (w0 + (w1 - w0) * tt) / 2.0
            d = cx * nx + cy * ny
            if abs(d) > hw:
                continue
            u = d * lit / hw                      # +1 lit edge .. -1 dark edge
            i = int((1.0 - u) / 2.0 * len(prof))
            fill[y, x] = True
            col[y, x] = M[prof[min(len(prof) - 1, max(0, i))]]
    ring = ndimage.binary_dilation(fill, structure=CROSS) & ~fill & (layer[..., 3] == 0)
    layer[ring, :3] = OUTLINE
    layer[ring, 3] = 255
    layer[fill, :3] = col[fill]
    layer[fill, 3] = 255


def hand_variants(sprite, joint, tip):
    """The hand in its eight lossless orientations (quarter turns, and mirrored): [(heading of wrist -> fingertips,
    sprite, joint)]."""
    out = []
    h0 = heading(joint, tip)
    for mirror in (False, True):
        s, j, h = sprite, joint, h0
        if mirror:
            s = s[:, ::-1].copy()
            j = (s.shape[1] - j[0], j[1])
            h = 180.0 - h
        for k in range(4):
            part = RK.Part(s, j)
            q = RK.turn(part, 90 * k)
            out.append((wrap(h + 90 * k), q.s, q.j))
    return out


def best_hand(variants, want):
    return min(variants, key=lambda v: abs(wrap(v[0] - want)))


def compose(kit, p):
    """One frame (canvas RGBA) of pose p (see Pose)."""
    dx, dy = p.get("dx", 0), p.get("dy", 0) - p.get("lift", 0)
    k = p.get("lean", 0.0)                 # columns the upper body moves ahead per row above the hips
    hip_row = N_HIP[1]

    def body_pt(pt):
        """A point on the upper body (design coords) -> canvas, with the lean and the hips' move."""
        sx = math.floor(k * (hip_row - pt[1])) if pt[1] < hip_row else 0.0
        return (pt[0] + sx + dx + OX, pt[1] + dy + OY)

    def leg_pt(pt):
        return (pt[0] + dx + OX, pt[1] + dy + OY)

    def empty():
        return np.zeros((CH, CW, 4), np.uint8)

    layers = []                            # (z, canvas-sized RGBA)

    def piece_layer(z, sprite, joint, at):
        lay = empty()
        stamp(lay, sprite, joint, at)
        layers.append((z, lay))
        return lay

    up_len, lo_len = dist(N_SHOULDER, N_ELBOW), dist(N_ELBOW, N_WRIST)
    # ---- an arm: the upper band, the forearm band, the hand at the wrist, the elbow ball
    def arm(z, shoulder, up, lo, far, hand_ang=None):
        lay = empty()
        elbow = along(shoulder, up, up_len)
        wrist = along(elbow, lo, lo_len)
        band(lay, shoulder, elbow, "upper", far, ext0=1.0, ext1=0.5)
        band(lay, elbow, wrist, "fore", far, ext0=0.5, ext1=0.0)
        hv = kit.hands_dark if far else kit.hands
        h, s, j = best_hand(hv, lo if hand_ang is None else hand_ang)
        stamp(lay, s, j, wrist)
        eb = kit.dark["n_elbow"] if far else kit.n_elbow
        stamp(lay, eb.s, eb.j, elbow)
        layers.append((z, lay))
        return elbow, wrist

    # the far arm: behind everything of the body
    if p.get("f_up") is None and p.get("f_lo") is None:
        piece_layer(11, kit.f_lower.s, kit.f_lower.j, body_pt(F_ELBOW))
    else:
        arm(10, body_pt(F_SHOULDER), p.get("f_up", -100.0), p.get("f_lo", -60.0), True, p.get("f_hand"))
    # ---- the legs: bands from the hips (under the skirt), the design's knee and ankle balls and boots pasted
    l1, l2 = dist(N_HIP, N_KNEE), dist(N_KNEE, N_ANKLE)
    for side in ("f", "n"):
        near = side == "n"
        hip0, knee0, ank0 = (N_HIP, N_KNEE, N_ANKLE) if near else (F_HIP, F_KNEE, F_ANKLE)
        hip0 = p.get(side + "_hip", hip0)
        hip = leg_pt(hip0)
        spec = p.get(side + "_leg")
        if spec is None:
            th, sh = heading(hip0, knee0), heading(knee0, ank0)
        elif spec[0] == "ang":
            th, sh = spec[1], spec[2]
        else:          # ("ik", x, y[, bend]): the ankle on that design point (the ground does not move with the hips)
            ank = (spec[1] + OX, spec[2] + OY)
            kn = ik(hip, ank, l1, l2, bend=spec[3] if len(spec) > 3 else 1)
            th, sh = heading(hip, kn), heading(kn, ank)
        knee = along(hip, th, l1)
        ank = along(knee, sh, l2)
        thigh, shinl = empty(), empty()
        band(thigh, hip, knee, "thigh", not near, ext0=2.0, ext1=1.0)
        pieces = {n: getattr(kit, n) for n in ("n_boot", "n_knee", "n_ankle", "n_shin")} if near else kit.dark
        if SHIN_PIECE:     # the design's own shin (its calf plate) turned about the knee
            sp = pieces["n_shin"]
            s, j = turned(sp, sh - DESIGN_ANG["n_sh"])
            stamp(shinl, s, j, knee)
        else:
            band(shinl, knee, ank, "shin", not near, ext0=1.0, ext1=0.5)
        boot = pieces["n_boot"]
        bt = p.get(side + "_boot", 0)
        s, j = turned(boot, bt) if bt else (boot.s, boot.j)
        stamp(shinl, s, j, ank)
        stamp(shinl, pieces["n_ankle"].s, pieces["n_ankle"].j, ank)
        stamp(shinl, pieces["n_knee"].s, pieces["n_knee"].j, knee)
        if near:
            layers.append((21, thigh))      # under the skirt
            layers.append((40, shinl))
        else:
            layers.append((20, thigh))
            layers.append((20.5, shinl))
    # ---- the key, the skirt, the torso (sheared), the head
    kd = p.get("key", (0, 0))
    kat = body_pt((52.0, 70.5))
    if not p.get("lie"):    # lying on her back the key is under her (it poked into the ground)
        piece_layer(24, kit.key.s, kit.key.j, (kat[0] + kd[0], kat[1] + kd[1]))
    piece_layer(26, kit.skirt.s, kit.skirt.j, leg_pt((61.0, 90.5)))
    tor = empty()
    tor[OY + kit.torso.y0:OY + kit.torso.y0 + kit.torso.s.shape[0],
        OX + kit.torso.x0:OX + kit.torso.x0 + kit.torso.s.shape[1]] = kit.torso.s
    tor = sheared(tor, k, int(round(hip_row + OY)))
    tor = np.roll(np.roll(tor, int(round(dy)), 0), int(round(dx)), 1)
    layers.append((28, tor))
    hd = p.get("head", (0, 0))
    nk = body_pt(NECK)
    head = empty()
    head[OY:OY + kit.head.shape[0], OX:OX + kit.head.shape[1]] = kit.head
    hx = int(round(nk[0] - (NECK[0] + OX))) + hd[0]
    hy = int(round(nk[1] - (NECK[1] + OY))) + hd[1]
    head = np.roll(np.roll(head, hy, 0), hx, 1)
    layers.append((60, head))
    head_sq = head[..., 3] > 0
    # ---- the near arm (over the body; under the head unless "arm_front")
    ns = body_pt(N_SHOULDER)
    if p.get("n_up") is None and p.get("n_lo") is None:
        piece_layer(50, kit.n_upper.s, kit.n_upper.j, ns)
        e = along(ns, DESIGN_ANG["n_up"], up_len)
        piece_layer(51, kit.n_lower.s, kit.n_lower.j, e)
        piece_layer(52, kit.n_elbow.s, kit.n_elbow.j, e)
    else:
        za = 70 if p.get("order") == "arm_front" else 50
        arm(za, ns, p.get("n_up", DESIGN_ANG["n_up"]), p.get("n_lo", DESIGN_ANG["n_lo"]), False, p.get("n_hand"))
    can = empty()
    for z, lay in sorted(layers, key=lambda t: t[0]):
        m = lay[..., 3] > 0
        can[m] = lay[m]
    # a gap the moved head opens against the neck, the shoulders or the key (memory gap-check): the outline's dark
    can = neck_gaps(can, head_sq)
    if p.get("turn"):       # the whole figure turned (a fall): RotSprite about the standing point
        part = RK.turn(RK.Part(can, (PIV_X + 0.5, SOLE + 1.0)), p["turn"])
        can = empty()
        stamp(can, part.s, part.j, (PIV_X + 0.5 + p.get("turn_dx", 0), SOLE + 1.0 + p.get("turn_dy", 0)))
    if p.get("lie"):        # lying: a quarter turn (lossless), its lowest row on the ground, centred turn_dx from the point
        can = lie(can, p["lie"], p.get("sink", 0), p.get("turn_dx", 0))
    return finish(can)


def neck_gaps(can, head_sq, most=16, crack=24):
    """Enclosed gaps filled with the outline colour: those of at most `most` squares touching the head (the moved head
    against the neck, the shoulders or the key), and thin cracks - at most two squares across, `crack` squares in all -
    between a limb and the body (memory gap-check); a wider gap (the room a bent arm leaves) stays."""
    op = can[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    near_head = ndimage.binary_dilation(head_sq, structure=np.ones((3, 3), bool))
    out = can.copy()
    for i in range(1, n + 1):
        m = lbl == i
        thin = m.sum() <= crack and ndimage.distance_transform_edt(m).max() <= 1.0
        if thin:
            out[m, :3] = OUTLINE
            out[m, 3] = 255
        elif m.sum() <= most and (m & near_head).any():
            out[m, :3] = M["e"]                 # the neck's own darkest metal (black read as a hole)
            out[m, 3] = 255
    return out


def lie(can, k, sink, dx):
    r = np.rot90(can, k).copy()
    ys, xs = np.nonzero(r[..., 3] > 0)
    fig = r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = np.zeros((CH, CW, 4), np.uint8)
    y0 = SOLE + 1 + sink - fig.shape[0]
    x0 = int(round(PIV_X + dx - fig.shape[1] / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def finish(can):
    """The outline closed round moved edges (never under the soles), pinholes of up to 2 squares filled from their
    neighbours, specks under 4 squares apart from the figure gone."""
    out = G.complete_outline(can, color=OUTLINE, feet=SOLE)[0]
    op = out[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for i in range(1, n + 1):
        m = lbl == i
        if m.sum() > 2:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & op & ~is_outline(out)
        if not ring.any():
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool)) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for i in range(1, n + 1):
            if sz[i - 1] < 12:
                out[lbl == i] = 0
    return out


# ------------------------------------------------------------------------------------------------ League's skeleton
S_GP = 86 / 39                    # design squares per game px of League's render (the design pose 39 px tall)
SEGS = {"tor": ("Hip", "Chest"), "nek": ("Chest", "Head"), "nTh": ("L_Thigh", "L_Knee"), "nSh": ("L_Knee", "L_Foot"),
        "fTh": ("R_Thigh", "R_Knee"), "fSh": ("R_Knee", "R_Foot"), "nUp": ("L_UpArm", "L_ForeArm"),
        "nLo": ("L_ForeArm", "L_hand"), "fUp": ("R_UpArm", "R_ForeArm"), "fLo": ("R_ForeArm", "R_hand")}


def league():
    """{tag: [frame dict: deltas of every segment's heading from League's side-on idle, the hips' move and each
    foot's move in design squares]} (League's L side is the near one: its arm and leg nearer the camera)."""
    J = json.load(open(lp(JOINTS), encoding="utf-8"))
    ref = J["ref"][0]

    def rel(fr, name):
        x, y, _ = fr["joints"][name]
        px, py = fr["pivot"]
        return ((x - px) * S_GP, (y - (py + 11.5)) * S_GP)

    out = {}
    for tag, frs in J.items():
        if tag == "ref":
            continue
        rows = []
        for fr in frs:
            j, rj = fr["joints"], ref["joints"]
            d = {k: wrap(heading(j[a], j[b]) - heading(rj[a], rj[b])) for k, (a, b) in SEGS.items()}
            d.update({k + "_abs": heading(j[a], j[b]) for k, (a, b) in SEGS.items()})
            h, h0 = rel(fr, "Hip"), rel(ref, "Hip")
            d["hip"] = (h[0] - h0[0], h[1] - h0[1])
            for side, name in (("n", "L_Foot"), ("f", "R_Foot")):
                f, f0 = rel(fr, name), rel(ref, name)
                d[side + "_foot"] = (f[0] - f0[0], f[1] - f0[1])
            d["ms"] = fr["ms"]
            rows.append(d)
        out[tag] = rows
    return out


DESIGN_ANG = {"n_up": heading(N_SHOULDER, N_ELBOW), "n_lo": heading(N_ELBOW, N_WRIST),
              "f_up": heading(F_SHOULDER, F_ELBOW), "f_lo": heading(F_ELBOW, (78.0, 83.0)),
              "n_th": heading(N_HIP, N_KNEE), "n_sh": heading(N_KNEE, N_ANKLE),
              "f_th": heading(F_HIP, F_KNEE), "f_sh": heading(F_KNEE, F_ANKLE)}
LEG_K = 0.83                      # our legs (thigh + shin) against League's chibi legs: the hips' height moves


def auto(d, planted=2.5):
    """A first pose from League's frame d: every limb turned by League's change, the hips moved as League's (their
    height by our shorter legs), the upper body leaning and the head moving with League's spine and neck; a foot
    within `planted` squares of its idle height stays on the ground (IK with our bones)."""
    hx, hy = d["hip"]
    p = Pose(dx=round(hx * 0.6), dy=round(hy * LEG_K))
    p["lean"] = max(-7.0, min(7.0, 21.5 * math.sin(math.radians(-d["tor"]))))
    hd = 14.0 * math.sin(math.radians(-d["nek"]))
    p["head"] = (int(round(max(-5, min(5, hd)))), int(round(min(4, abs(hd) * 0.3))))
    p["n_up"] = DESIGN_ANG["n_up"] + d["nUp"]
    p["n_lo"] = DESIGN_ANG["n_lo"] + d["nLo"]
    p["f_up"] = DESIGN_ANG["f_up"] + d["fUp"]
    p["f_lo"] = DESIGN_ANG["f_lo"] + d["fLo"]
    for side, (hip0, knee0, ank0) in (("n", (N_HIP, N_KNEE, N_ANKLE)), ("f", (F_HIP, F_KNEE, F_ANKLE))):
        fx, fy = d[side + "_foot"]
        if abs(fy) <= planted:
            p[side + "_leg"] = ("ik", ank0[0] + fx * 0.6, ank0[1])
        else:
            p[side + "_leg"] = ("ang", DESIGN_ANG[side + "_th"] + d[side + "Th"],
                                DESIGN_ANG[side + "_sh"] + d[side + "Sh"])
    return p


# ------------------------------------------------------------------------------------------------ review
PACK_NOW = os.path.join(TMP, "orianna_strips_pack", "now")   # League's frame per action frame on the 8-px design grid


def lol_tile(tag, i, z, box):
    """League's frame i of tag on our grid (the strips pack's skeleton: 8 px a square, soles on row 117, standing
    point column 96), cropped like our canvas `box` (x0, y0, x1, y1 from the standing point / the row under the soles)."""
    im = Image.open(lp(os.path.join(PACK_NOW, f"orianna_{tag}_{i + 1}.png"))).convert("RGBA")
    x0, y0, x1, y1 = box
    c = im.crop(((96 + x0) * 8, (118 + y0) * 8, (96 + x1) * 8, (118 + y1) * 8))
    bg = Image.new("RGBA", c.size, (232, 232, 232, 255))
    bg.alpha_composite(c)
    return bg.resize(((x1 - x0) * z, (y1 - y0) * z), Image.LANCZOS).convert("RGB")


def our_tile(can, z, box, bg=(92, 98, 86)):
    x0, y0, x1, y1 = box
    c = can[SOLE + 1 + y0:SOLE + 1 + y1, PIV_X + x0:PIV_X + x1]
    out = np.zeros(c.shape, np.uint8)
    out[...] = (*bg, 255)
    m = c[..., 3] > 0
    out[m] = c[m]
    return Image.fromarray(out).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST).convert("RGB")


def compare_sheet(tag, frames, path, z=3, box=(-56, -104, 56, 6)):
    """Two rows: League's frames on top, ours under them, one column per frame."""
    tops = [lol_tile(tag, i, z, box) for i in range(len(frames))]
    bots = [our_tile(f, z, box) for f in frames]
    w, h = tops[0].size
    sheet = Image.new("RGB", (len(frames) * (w + 4), 2 * h + 4), (40, 40, 40))
    for i, (t, b) in enumerate(zip(tops, bots)):
        sheet.paste(t, (i * (w + 4), 0))
        sheet.paste(b, (i * (w + 4), h + 4))
    sheet.save(lp(path))


def tint(a, masks, colours):
    out = a.copy()
    for name, c in colours.items():
        m = masks[name] & (a[..., 3] > 0) & ~is_outline(a)
        out[m, :3] = (out[m, :3] * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    return out


def zoom(a, z, x0, y0, x1, y1, grid=5):
    """a[y0:y1, x0:x1] at z x on magenta with a grid and labels every `grid` squares."""
    c = a[y0:y1, x0:x1]
    bg = np.zeros(c.shape, np.uint8)
    bg[...] = (255, 0, 255, 255)
    m = c[..., 3] > 0
    bg[m] = c[m]
    im = Image.fromarray(bg).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST).convert("RGB")
    out = Image.new("RGB", (im.width + 34, im.height + 22), (255, 255, 255))
    out.paste(im, (34, 22))
    d = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    for x in range(c.shape[1] + 1):
        if (x0 + x) % grid == 0:
            d.line([(34 + x * z, 22), (34 + x * z, out.height)], fill=(0, 0, 0))
            d.text((35 + x * z, 4), str(x0 + x), fill=(0, 0, 0), font=font)
    for y in range(c.shape[0] + 1):
        if (y0 + y) % grid == 0:
            d.line([(34, 22 + y * z), (out.width, 22 + y * z)], fill=(0, 0, 0))
            d.text((2, 23 + y * z), str(y0 + y), fill=(0, 0, 0), font=font)
    return out


# ------------------------------------------------------------------------------------------------ the actions
GROUND = 110.9                     # the ankle's row with the boot on the ground (design rows)
# the run (league_caitlyn's way): one leg's ankle in eight phases (squares ahead of its hip, the ankle's row), the far
# leg four phases on; the hips close together under the skirt as League's side-on run has them
RUN_PHASES = [(13.0, GROUND), (6.5, GROUND), (0.0, GROUND), (-7.0, GROUND), (-12.5, GROUND - 3.5),
              (-11.0, GROUND - 11.0), (0.0, GROUND - 11.0), (9.5, GROUND - 5.5)]
RUN_DY = [4, 5, 5, 3, 4, 5, 5, 3]
RUN_HIPS = {"n": (59.0, 90.5), "f": (61.0, 90.5)}
RUN_LEAN, RUN_HEAD = 0.5, (2, 2)
RUN_DX = -4                        # the whole run back: the leaning head nearer where it stands in the idle


def run_poses():
    out = []
    for i in range(8):
        dy = RUN_DY[i]
        sw = math.cos(2 * math.pi * i / 8)
        p = Pose(dx=RUN_DX, dy=dy, lean=RUN_LEAN, head=RUN_HEAD, f_piece="long")
        for side, ph in (("n", i), ("f", (i + 4) % 8)):
            hx, hy = RUN_HIPS[side]
            ax, ay = RUN_PHASES[ph]
            p[side + "_hip"] = (hx, hy)
            p[side + "_leg"] = ("ik", hx + ax, ay)
        # the near arm swings behind the body only (in front it covered the bust), the far one ahead of it
        p["n_up"] = -135 - 18 * sw
        p["n_lo"] = p["n_up"] + 20
        p["f_up"] = -95 + 25 * sw
        p["f_lo"] = p["f_up"] + 35
        out.append((p, 169))
    return out


def stand(**kw):
    """The side design's stance (both ankles on their design spots by IK, the arms at rest), with changes."""
    p = Pose(n_leg=("ik", N_ANKLE[0], GROUND), f_leg=("ik", F_ANKLE[0], GROUND), n_up=-127.0, n_lo=-130.0,
             f_up=-70.0, f_lo=-20.0)
    p.update(kw)
    return p


def planted(dx=0, **kw):
    """Feet kept on their design spots while the hips move (a crouch, a lean): IK with our bones."""
    return stand(n_leg=("ik", N_ANKLE[0] + dx, GROUND), f_leg=("ik", F_ANKLE[0] + dx, GROUND), **kw)


def frames_of(rows, ms):
    return [(p, m) for p, m in zip(rows, ms if isinstance(ms, list) else [ms] * len(rows))]


def attack_poses():
    """League's attack1: the far (front) hand drawn up before her chest, a bow, the flick forward (the bolt leaves on
    frame 4), the head and the upper body thrown back after it, back to the stance. The near arm hangs behind her
    (in front of the body it covered the bust)."""
    rows = [
        stand(),
        planted(dy=1, lean=-0.05, head=(-1, 0), n_up=-135, n_lo=-135, f_up=-60, f_lo=30),
        planted(dy=2, lean=1 / 4, head=(3, 3), n_up=-130, n_lo=-128, f_up=-40, f_lo=60),
        planted(lean=0.0, n_up=-140, n_lo=-145, f_up=-5, f_lo=0, f_hand=0),
        planted(lean=-1 / 6, head=(-2, -1), n_up=-138, n_lo=-140, f_up=25, f_lo=40),
        planted(lean=-1 / 6, head=(-3, -1), n_up=-135, n_lo=-136, f_up=30, f_lo=55),
        planted(lean=-0.1, head=(-1, 0), n_up=-130, n_lo=-132, f_up=-20, f_lo=10),
        stand(f_up=-50, f_lo=-10),
    ]
    # frame 4 (the flick) starts at the kit's a_st 10 ticks (167 ms); 28 ticks in all (tools/kit/build_orianna.P)
    return frames_of(rows, [56, 56, 55, 58, 60, 60, 60, 62])


def skill_poses():
    """Q (League's spell1): a dip, the far arm cocked high behind the head, a hop with the arms flung apart - the far
    hand pointing ahead (the Ball sent, frame 4), the near arm back - the legs hanging with the toes down, a landing
    crouch."""
    rows = [
        stand(),
        planted(dy=3, lean=1 / 8, head=(1, 1), n_up=-135, n_lo=-125, f_up=-70, f_lo=-40),
        planted(dy=-1, lean=-0.1, head=(-1, -1), n_up=-140, n_lo=-150, f_up=100, f_lo=150),
        stand(lift=6, lean=-0.08, n_leg=("ang", -96, -104), f_leg=("ang", -84, -96), n_boot=-30, f_boot=-30,
              n_up=-150, n_lo=-165, f_up=25, f_lo=35),
        stand(lift=8, lean=-0.08, n_leg=("ang", -45, -115), f_leg=("ang", -92, -100), n_boot=-30, f_boot=-30,
              n_up=-155, n_lo=-170, f_up=30, f_lo=45),
        stand(lift=5, n_leg=("ang", -75, -100), f_leg=("ang", -90, -96), f_boot=-20, n_up=-145, n_lo=-150, f_up=0,
              f_lo=-10),
        planted(dy=3, lean=1 / 8, n_up=-140, n_lo=-135, f_up=-50, f_lo=-30),
        stand(),
    ]
    # frame 4 (the point) starts at the kit's q_st 6 ticks (100 ms); q_dur 20 ticks in all
    return frames_of(rows, [28, 34, 38, 46, 46, 46, 50, 48])


def skill_w_poses():
    """W (League's spell2): a deep crouch, the jump with straight legs and the toes down, spread like a star at the
    top, then the legs tucked and the far hand drawn to her chest (the pulse, frame 5), a landing crouch. Nothing goes
    over her head: her head hid raised arms but for a stick of them."""
    rows = [
        stand(),
        planted(dy=6, lean=1 / 6, head=(2, 2), n_up=-150, n_lo=-160, f_up=-45, f_lo=-60),
        stand(lift=3, lean=-0.1, n_leg=("ang", -95, -100), f_leg=("ang", -85, -95), n_boot=-30, f_boot=-30,
              n_up=-160, n_lo=-175, f_up=30, f_lo=30),
        stand(lift=13, head=(0, -1), n_leg=("ang", -94, -98), f_leg=("ang", -84, -90), n_boot=-45, f_boot=-45,
              n_up=-158, n_lo=-168, f_up=-20, f_lo=-32),
        stand(lift=12, n_leg=("ang", -20, -110), f_leg=("ang", -30, -115), n_up=-140, n_lo=-125, f_up=-75, f_lo=35),
        stand(lift=8, n_leg=("ang", -40, -118), f_leg=("ang", -45, -120), n_up=-142, n_lo=-128, f_up=-72, f_lo=30),
        planted(dy=5, lean=1 / 8, n_up=-150, n_lo=-160, f_up=-40, f_lo=-20),
        stand(),
    ]
    return frames_of(rows, 38)


def skill_e_poses():
    """E (League's spell3): a crouch, a rise onto the near toe (the boot pointing down), the far leg drawn up to the
    knee (a pirouette), the far hand pointing ahead at the ally (frame 4, the kit's e_st), down again."""
    pir = dict(n_leg=("ang", -90, -90), n_boot=-90, f_leg=("ang", -10, -140))
    rows = [
        stand(),
        planted(dy=5, lean=1 / 8, n_up=-140, n_lo=-150, f_up=-70, f_lo=-50),
        stand(lift=4, head=(0, -1), n_leg=("ang", -90, -92), n_boot=-90, f_leg=("ang", -30, -130), n_up=-170,
              n_lo=-150, f_up=-15, f_lo=35),
        stand(lift=8, n_up=-150, n_lo=-150, f_up=10, f_lo=15, f_hand=0, **pir),
        stand(lift=9, n_up=-150, n_lo=-150, f_up=15, f_lo=25, **pir),
        stand(lift=9, n_up=-148, n_lo=-148, f_up=25, f_lo=35, **pir),
        stand(lift=6, n_leg=("ang", -90, -92), n_boot=-90, f_leg=("ang", -50, -110), n_up=-140, n_lo=-140, f_up=-30,
              f_lo=-10),
        planted(dy=1),
    ]
    # frame 4 (the point) starts at the kit's e_st 6 ticks (100 ms); e_dur 18 ticks in all
    return frames_of(rows, [25, 35, 40, 50, 40, 40, 34, 40])


def ult_poses():
    """R (League's spell4): the arms flung up in a V (the hands past her head), up on the toes, a drop into a bow with
    the far hand to the ground ahead and the near arm thrown back, held, then up again with the arms in the V (the
    shockwave, frame 9)."""
    rows = [
        stand(),
        planted(lean=-0.1, head=(-1, 0), n_up=150, n_lo=130, f_up=40, f_lo=60),
        planted(dy=-1, lean=-1 / 6, head=(-2, -1), n_up=140, n_lo=135, f_up=50, f_lo=55),
        planted(dy=5, lean=1 / 6, head=(2, 2), n_up=-150, n_lo=-150, f_up=-40, f_lo=-60),
        planted(dy=9, lean=1 / 3, head=(4, 5), n_up=-150, n_lo=-160, f_up=-60, f_lo=-85),
        planted(dy=10, lean=1 / 3, head=(4, 6), n_up=-152, n_lo=-162, f_up=-62, f_lo=-88),
        planted(dy=10, lean=1 / 3, head=(4, 5), n_up=-152, n_lo=-162, f_up=-62, f_lo=-88),
        planted(dy=9, lean=1 / 3, head=(4, 5), n_up=-150, n_lo=-158, f_up=-58, f_lo=-80),
        planted(dy=-2, lean=-1 / 8, head=(-1, -2), n_up=145, n_lo=140, f_up=45, f_lo=50),
        stand(n_up=-140, n_lo=-140, f_up=-50, f_lo=-20),
    ]
    # frame 9 (the shockwave) starts at the kit's r_delay 30 ticks (500 ms), when the blow lands; r_anim 36 ticks in all
    return frames_of(rows, [60, 60, 60, 60, 65, 65, 65, 65, 50, 50])


def dead_poses():
    """Death (League's): hit, the head thrown back, then dropping, the body going slack like a puppet whose strings
    were cut, falling back, lying on her back."""
    limp = dict(n_up=-100, n_lo=-95, f_up=-85, f_lo=-90)
    rows = [
        planted(dx=-1, lean=-0.1, head=(-1, 0), n_up=-150, n_lo=-170, f_up=20, f_lo=40),
        planted(dx=-2, lean=-1 / 6, head=(-3, -2), n_up=160, n_lo=170, f_up=60, f_lo=80),
        planted(dx=-2, lean=-1 / 5, head=(-4, -1), n_up=150, n_lo=150, f_up=70, f_lo=100),
        planted(dx=-2, dy=2, lean=1 / 8, head=(2, 3), n_up=-160, n_lo=-160, f_up=-30, f_lo=-30),
        planted(dx=-2, dy=4, lean=1 / 5, head=(3, 5), **limp),
        planted(dx=-2, dy=5, lean=1 / 4, head=(4, 6), **limp),
        planted(dx=-3, dy=6, lean=1 / 4, head=(4, 6), **limp),
        planted(dx=-3, dy=6, lean=1 / 5, head=(3, 6), **limp),
        # falling back: lying already (a quarter turn, lossless) five rows over the ground, then down on it (league_mel's
        # fall; a RotSprite turn of the whole figure broke her face)
        stand(n_leg=("ang", -82, -100), f_leg=("ang", -78, -96), lie=1, sink=-5, turn_dx=-6, n_up=-100, n_lo=-80,
              f_up=-80, f_lo=-70),
        stand(n_leg=("ang", -92, -95), f_leg=("ang", -88, -92), lie=1, turn_dx=-8, n_up=-92, n_lo=-92, f_up=-88,
              f_lo=-88),
    ]
    return frames_of(rows, 100)


# ------------------------------------------------------------------------------------------------ the idle and the hit
FRONT_LOW_ROW, FRONT_LOW_COL = 83, 47     # the front design's skirt (rows 83 on, columns 47 on) never moves
FRONT_LEG_ROW = 99                        # nor anything from row 99 down (the legs: the near boot reaches column 44)
IDLE_SINK = [0, 0, 1, 1, 1, 1, 0, 0]


def front_parts(kit):
    F = kit.front
    yy, xx = np.mgrid[:F.shape[0], :F.shape[1]]
    op = F[..., 3] > 0
    low = op & ((yy >= FRONT_LEG_ROW) | ((yy >= FRONT_LOW_ROW) & (xx >= FRONT_LOW_COL)))
    return np.where(low[..., None], F, 0).astype(np.uint8), np.where((op & ~low)[..., None], F, 0).astype(np.uint8)


def idle_frames(kit):
    """The front design breathing above the waist (memory rig-deformation-checks, league_mel): the head, the bust, the
    shoulders, both arms and the key settle a row onto the waist; the skirt and the legs never move."""
    low, up = front_parts(kit)
    out = []
    for s in IDLE_SINK:
        can = on_canvas(low)
        u = on_canvas(np.roll(up, s, 0))
        m = u[..., 3] > 0
        can[m] = u[m]
        out.append((finish(can), 150))
    return out


def flash(a, k=0.55):
    out = a.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


def hit_frames(kit):
    """The front design knocked back two squares with a white flash, then one square back."""
    f = on_canvas(kit.front)
    return [(flash(np.roll(f, -2, 1)), 90), (np.roll(f, -1, 1), 120)]


ORDER = ["idle", "run", "attack", "skill", "skill_w", "skill_e", "ult", "hit", "dead"]


def actions(kit):
    acts = {"idle": idle_frames(kit)}
    for tag in ORDER[1:]:
        if tag == "hit":
            acts[tag] = hit_frames(kit)
            continue
        acts[tag] = [(compose(kit, p), ms) for p, ms in globals()[tag + "_poses"]()]
    return acts


# ------------------------------------------------------------------------------------------------ export
PPU = 2.25                          # 86 squares bun top to soles = 38.2 game rows, the old 84 at 2.2
FEET = 11.5                         # 1x rows from the pivot down to the soles' bottom edge


def one_of(can, px, py, hw, hh, need=0.5):
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot)."""
    px, py = PIV_X + 0.5, SOLE + 1 - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    # the 1x frame the way the UI frames are made (pixel_down.pixelate: each square the mean of its pixels snapped to
    # the frame's own colours, lines kept) on a grid with the pivot in its middle square - a vote of the commonest
    # colour per square took the outline's black for most of her
    lo, (nx0, ny0) = PD.pixelate(can, 1.0 / PPU, (px - PPU / 2, py - PPU / 2), OUTLINE)
    one = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    for j in range(2 * hh + 1):
        y = ny0 - hh + j
        if 0 <= y < lo.shape[0]:
            for i in range(2 * hw + 1):
                x = nx0 - hw + i
                if 0 <= x < lo.shape[1]:
                    one[j, i] = lo[y, x]
    one = G.complete_outline(one, color=OUTLINE)[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def export(acts):
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    for tag, frs in acts.items():
        ones, hds = [], []
        for can, t in frs:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"orianna_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"orianna_{tag}.json")), "w", encoding="utf-8", newline=chr(10)) as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_orianna#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


# ------------------------------------------------------------------------------------------------ review
def review(acts, out_dir, z=3):
    """Every tag next to League's clip (League left, ours right; idle and hit ours only), played twice with its name
    over it, in one GIF (memory one-gif-review); and one PNG sheet per tag at 6x."""
    os.makedirs(out_dir, exist_ok=True)
    box = (-58, -112, 58, 6)
    font = ImageFont.load_default()
    frames, durs = [], []
    for tag, frs in acts.items():
        lol = tag not in ("idle", "hit")
        for rep in range(2):
            for i, (can, ms) in enumerate(frs):
                ours = our_tile(can, z, box)
                w, h = ours.size
                im = Image.new("RGB", (2 * w + 8, h + 26), (34, 34, 34))
                if lol:
                    im.paste(lol_tile(tag, i, z, box), (0, 26))
                im.paste(ours, (w + 8, 26))
                d = ImageDraw.Draw(im)
                d.text((8, 6), f"{tag}  {i + 1}/{len(frs)}" + ("" if lol else "  (no League clip)"),
                       fill=(255, 240, 160), font=font)
                frames.append(im.quantize(255, dither=Image.Dither.NONE))
                durs.append(int(ms))
        tiles = [our_tile(can, 6, box) for can, _ in frs]
        sheet = Image.new("RGB", (len(tiles) * (tiles[0].width + 6), tiles[0].height), (34, 34, 34))
        for i, t in enumerate(tiles):
            sheet.paste(t, (i * (t.width + 6), 0))
        sheet.save(os.path.join(out_dir, f"orianna_{tag}.png"))
    frames[0].save(os.path.join(out_dir, "orianna_actions_vs_lol.gif"), save_all=True, append_images=frames[1:],
                   duration=durs, loop=0)
    print("review ->", out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the comparison GIF and the 6x sheets here (nothing written to the repo)")
    ap.add_argument("--parts", help="the side design's parts tinted, at 12x, here")
    a = ap.parse_args()
    kit = Kit()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        cols = dict(side_head=(255, 0, 0), key=(255, 200, 0), torso=(0, 200, 255), skirt=(0, 255, 0),
                    n_upper=(255, 0, 255), n_elbow=(128, 0, 255), n_lower=(255, 128, 0), f_lower=(0, 0, 255),
                    n_thigh=(255, 64, 64), n_knee=(128, 64, 0), n_shin=(64, 255, 64), n_ankle=(0, 128, 128),
                    n_boot=(255, 255, 0), legs_rest=(80, 80, 80))
        zoom(tint(kit.side, kit.masks, cols), 12, 34, 28, 88, 120).save(os.path.join(a.parts, "orianna_parts.png"))
        return
    acts = actions(kit)
    if a.review:
        review(acts, a.review)
        return
    export(acts)


if __name__ == "__main__":
    main()
