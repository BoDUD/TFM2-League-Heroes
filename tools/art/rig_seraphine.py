#!/usr/bin/env python3
"""Seraphine's action strips posed from the approved design's own parts (the casting body = the idle's).

    python tools/art/rig_seraphine.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 round (assets/source/seraphine/codex_strips/) pasted the design's head, legs and stage over generated
frames: the back hair came out as flat-topped slabs cut straight across, the gloves as white blobs (a sword-like raised
arm in the attack, an extra arm in the hit), R's crouch lost the upper body under the pasted head and the lying death
frames stacked two faces. The user: 「codex交付了 有问题的地方你灵活运用工具修复」. This rig (rig_gwen's way) poses her from
the design instead:
- the body, the head, the legs and the stage: the design's own squares, every frame;
- the far arm (image right, the gloved hand raised at her ear in the design): the forearm and the glove lifted off
  (FAR_OFF) and drawn again per pose with rigkit.bone_arm from the shoulder under the white puffed sleeve, in the
  design's materials (skin lit / mid / shade, the white glove's two steps at the hand), one outline ring, under the
  body (the far arm);
- the near arm (image left, hanging at the hip with its glove): as drawn (turned outward for W's song it read as a
  white stick across the hair; near_turned() kept for a later pose);
- the back hair (the long pink mass on the image left): stretched backward row by row from where it leaves the body
  (its roots stay, its tips stream further, up to HAIR_MAX squares at the bottom rows) - the glide's wave and the casts'
  swing; never cut, never moved off the body;
- the glide (League's run): the whole figure with its stage 1 row up in frames 2-3 and 6-7, the hair streaming 2-4;
- the death (league_sivir's, the user's accepted one): struck back, knocked, the figure (without the stage) turned 20
  and 45 degrees about her feet, then lying on her back on the deck, her boots at the stage's right end, her head and hair past its left
  edge; the stage stays level under her.
Every frame is finished alike (rigkit.finish). Writes assets/source/native/seraphine_<tag>.png (8x, 112x88 cells) and
seraphine_cells.json; then tools/art/import_native.py.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "seraphine_native.png")
HERO = "seraphine"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the stage's bottom on row 99)
CELL, CELL_PIVOT = (112, 88), (56, 64)
SOLES = 99
MS = {"idle": [200] * 6, "run": [133] * 8, "attack": [60, 60, 60, 80, 80, 80],
      "skill": [60, 60, 70, 80, 80, 80], "skill2": [60, 60, 80, 80, 60, 80, 80, 80],
      "ult": [80, 100, 120, 120], "hit": [100, 100], "dead": [100, 110, 120, 130, 150, 200, 300, 400]}
TAGS = list(MS)
KEYS = "0abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# the design's colours used here (rigkit.Design.letters with KEYS: 0 outline, Q glove white, O glove shade, K glove
# shadow, N skin lit, L skin mid, J skin shade, p / n hair, m hair shade)
OUTLINE = hx("#0D0222")
SKIN = (hx("#FDDAB8"), hx("#FCCF8A"), hx("#F2B89A"))
GLOVE = (hx("#FDFCFE"), hx("#EEE5E5"), hx("#CFCBE4"))
HAIR_FILL = hx("#D31865")
STAGE_TOP = 90                         # the stage's rows (to the bottom)
STAGE_RIGHT = 78                       # lying on the deck, her boots end here (the stage reaches column 79)
# the far arm as drawn: the forearm and the glove at her ear, lifted off when the arm moves (rows: (first, last))
FAR_OFF = {63: (76, 77), 64: (76, 77), 65: (76, 77), 66: (76, 77), 67: (77, 77), 68: (77, 78), 69: (77, 78),
           70: (77, 78), 71: (76, 78), 72: (76, 78), 73: (77, 78)}
FAR_SHOULDER = (76.5, 70.5)            # where the far arm leaves the white puffed sleeve
FAR_UPPER, FAR_FORE = 4.0, 6.0         # bone lengths (the forearm with the glove's last two squares)
# the near arm's forearm and glove (under the sleeve's gold band), the joint at the elbow
NEAR_ARM = {73: (59, 60), 74: (59, 60), 75: (59, 60), 76: (58, 60), 77: (57, 60), 78: (57, 59), 79: (56, 59),
            80: (56, 59), 81: (56, 57)}
NEAR_ELBOW = (60.0, 73.0)
# the back hair: the pink mass left of the body, rows HAIR_ROWS, columns left of HAIR_EDGE (the sleeve and the arm
# start there); streamed by stretching each row's run leftward from its right end
HAIR_ROWS, HAIR_EDGE, HAIR_MAX = (62, 84), 57, 4

# far-arm poses: the hand relative to the shoulder (x right, y down) and which way the elbow bends (+1 down/out)
POSES = {"fwd": ((9.0, -1.0), 1), "fwd_up": ((7.0, -6.5), 1), "up": ((3.0, -9.0), 1), "fwd_low": ((8.5, 3.0), 1),
         "down": ((2.0, 9.0), -1), "wide": ((8.0, -4.5), 1), "chest": ((4.0, 2.0), -1)}


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a.copy()
        self.full = a
        self.stage = np.zeros_like(a)
        self.stage[STAGE_TOP:] = a[STAGE_TOP:]
        fig = a.copy()
        fig[STAGE_TOP:] = 0
        self.fig = fig                                   # everything but the stage
        far = K.mask_rows(FAR_OFF)
        self.no_far = fig.copy()
        self.no_far[far] = 0
        # the old arm's own outline ring goes with it (left behind it cut the redrawn arm with a black line at the
        # elbow, 「手臂这里一条黑线怎么回事」): dark squares next to the lifted arm that touch no other coloured square
        lum = 0.299 * fig[..., 0] + 0.587 * fig[..., 1] + 0.114 * fig[..., 2]
        dark = (fig[..., 3] > 0) & (lum < 40)
        op = self.no_far[..., 3] > 0
        for y, x in zip(*np.nonzero(dark & ~far)):
            nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if not any(far[q] for q in nb):
                continue
            if not any(op[q] and not dark[q] for q in nb):
                self.no_far[y, x] = 0
        near = K.mask_rows(NEAR_ARM)
        self.near_part = K.Part.from_canvas(fig, near, NEAR_ELBOW)
        self.near_mask = near & (fig[..., 3] > 0)
        hair = np.zeros(a.shape[:2], bool)
        pink = {tuple(c) for c in D.palette if c[0] > 150 and c[1] < 90}
        dark = {tuple(c) for c in D.palette if c[0] > 70 and c[1] < 20 and c[2] < 80}
        for y in range(HAIR_ROWS[0], HAIR_ROWS[1] + 1):
            for x in range(0, HAIR_EDGE):
                c = tuple(int(v) for v in a[y, x, :3])
                if a[y, x, 3] and (c in pink or c in dark or c == OUTLINE):
                    hair[y, x] = True
        self.hair = hair


def stream(a, hair, amount):
    """The back hair stretched leftward: each row's hair run keeps its right end (the roots at the body) and reaches
    round(amount x depth) squares further left, depth growing from 0 at the top row to 1 at the bottom."""
    if amount == 0:
        return a
    out = a.copy()
    r0, r1 = HAIR_ROWS
    for y in range(r0, r1 + 1):
        xs = np.nonzero(hair[y])[0]
        if not len(xs):
            continue
        l, r = int(xs.min()), int(xs.max())
        d = int(round(amount * (y - r0) / (r1 - r0)))
        if d <= 0:
            continue
        src = a[y, l:r + 1].copy()
        out[y, l:r + 1][hair[y, l:r + 1]] = 0
        n0, n1 = l - d, r
        for x in range(n0, n1 + 1):
            sx = r - int(round((r - x) * (r - l) / max(1, r - n0)))
            if 0 <= x < 128 and src[sx - l, 3] and hair[y, sx]:
                out[y, x] = src[sx - l]
    return out


def far_arm(dst, pose):
    """The far arm drawn under the figure from the shoulder to the hand of `pose`."""
    (dx, dy), bend = POSES[pose]
    sh = FAR_SHOULDER
    hand = (sh[0] + dx, sh[1] + dy)
    elb, hand = K.elbow(sh, hand, FAR_UPPER, FAR_FORE, bend)
    layer = np.zeros_like(dst)
    mats = {"upper": [(0, 1, SKIN)], "fore": [(0, 0.62, SKIN), (0.62, 1, GLOVE)]}
    K.bone_arm(layer, sh, elb, hand, mats, width=(2.3, 2.3), outline=OUTLINE)
    return K.put(dst, layer, 0, 0, under=True)


def near_turned(P, base, deg):
    """The near forearm and glove turned deg (counter-clockwise on screen) about the elbow; what it covered refilled
    with the hair behind it."""
    out = base.copy()
    out[P.near_mask] = 0
    for y, x in zip(*np.nonzero(P.near_mask)):
        if x < 59:
            out[y, x] = (*HAIR_FILL, 255)
    part = K.turn(P.near_part, deg)
    return K.place(out, part, NEAR_ELBOW)


def figure(P, pose=None, hair=0, near=0, dx=0, dy=0):
    """One frame without the stage: the far arm in `pose` (None = as drawn), the hair streamed, the near arm turned."""
    body = P.fig if pose is None else P.no_far
    if near:
        body = near_turned(P, body, near)
    body = stream(body, P.hair, hair)
    if pose is not None:
        body = far_arm(body.copy(), pose)
    return K.shifted(body, dx, dy)


def frame(P, stage_dy=0, **kw):
    f = figure(P, **kw)
    out = K.shifted(P.stage, 0, stage_dy)
    out = K.put(out, f, 0, 0)
    return K.finish(out, P.D.outline, SOLES)


def lying(P, deg, dx):
    """The figure (no stage) turned deg about her feet on the deck, on the stage."""
    feet = (66.0, 89.5)
    part = K.Part.from_canvas(P.fig, P.fig[..., 3] > 0, feet)
    t = K.turn(part, deg)
    body = K.place(np.zeros_like(P.fig), t, (feet[0] + dx, feet[1]))
    xs = np.nonzero(body[..., 3].any(0))[0]
    right = max(0, int(xs.max()) - STAGE_RIGHT) if deg >= 90 else 0   # lying: her boots at the stage's right end
    body = K.shifted(body, -right, 0)
    sx = np.nonzero(P.stage[..., 3].any(0))[0]
    over = body[:, sx.min():sx.max() + 1, 3].any(1)     # her rows above the stage's columns rest on the deck
    low = int(np.nonzero(over)[0].max()) if over.any() else int(np.nonzero(body[..., 3].any(1))[0].max())
    out = K.put(P.stage.copy(), body, 0, (STAGE_TOP - 1) - low)
    return K.finish(out, P.D.outline, SOLES)


def build(P):
    F = {}
    F["idle"] = [frame(P, hair=h) for h in (0, 0, 1, 1, 0, 0)]
    F["run"] = [frame(P, hair=h, dy=up, stage_dy=up) for h, up in
                ((2, 0), (3, -1), (4, -1), (3, 0), (2, 0), (3, -1), (4, -1), (3, 0))]
    F["attack"] = [frame(P), frame(P, pose="chest", hair=1), frame(P, pose="up", hair=2, dx=-1),
                   frame(P, pose="fwd", hair=3, dx=1), frame(P, pose="fwd_low", hair=2), frame(P, hair=1)]
    F["skill"] = [frame(P), frame(P, pose="up", hair=1, dx=-1), frame(P, pose="up", hair=2, dx=-1),
                  frame(P, pose="fwd_up", hair=4, dx=1), frame(P, pose="fwd", hair=2), frame(P, hair=1)]
    F["skill2"] = [frame(P), frame(P, pose="chest", hair=1), frame(P, pose="fwd_low", hair=3, dx=1),
                   frame(P, pose="fwd", hair=2), frame(P, pose="down", hair=1),
                   frame(P, pose="wide", hair=4), frame(P, pose="fwd", hair=2), frame(P, hair=1)]
    F["ult"] = [frame(P, pose="chest", hair=1, dy=1), frame(P, pose="down", hair=1, dy=1),
                frame(P, pose="fwd_up", hair=4, dx=1), frame(P, pose="fwd", hair=2)]
    F["hit"] = [frame(P, hair=3, dx=-2), frame(P, hair=1, dx=-1)]
    F["dead"] = [frame(P, hair=3, dx=-1), frame(P, hair=4, dx=-2), lying(P, 20, -2), lying(P, 45, -2),
                 lying(P, 90, -2), lying(P, 90, -2), lying(P, 90, -2), lying(P, 90, -2)]
    return F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="folder for the review sheet and GIF")
    ap.add_argument("--tags")
    a = ap.parse_args()
    P = Parts()
    F = build(P)
    if a.tags:
        F = {t: F[t] for t in a.tags.split(",")}
    idle = F.get("idle", [P.full])[0]
    for tag, frs in F.items():
        print(tag, K.audit(frs, idle, P.D.outline, SOLES))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        rows = [(t, frs) for t, frs in F.items()]
        K.review_sheet(rows, os.path.join(a.review, "seraphine_rig.png"), z=4, soles=SOLES)
        K.review_gif(rows, MS, os.path.join(a.review, "seraphine_rig.gif"), z=4)
    bad = K.write_strips(HERO, F, {t: MS[t] for t in F}, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differs:", bad or "nothing")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
