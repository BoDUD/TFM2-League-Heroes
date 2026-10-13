#!/usr/bin/env python3
"""Nilah's run: the side design's upper body on two legs drawn from the design's own parts in eight phases
(assets/source/nilah/frames/run_1..8.png; the rest of frames/ untouched).

    python tools/art/run_nilah.py [--review DIR]

The user, 2026-10-13: the design's legs sheared straight (league_nidalee's way) - 「走路时候腿部有变形吧？」 (the puffy
trousers sheared into slanted steps); League's own running legs recoloured (league_zeri's dense way) - 「还是变形啊 自己不看
吗」「而且腿这么粗？」 (another pair of legs: longer, thicker, mottled, the design's bands, plates and slippers gone). So the
legs are the design's, posed the way league_irelia's and league_garen's dense runs were (approved): the upper body
stays as the design has it; each leg is a hip, a knee and an ankle - the ankle placed by the phase (PHASES: ahead of
the hips, planted under them, pushed back, kicked up behind, swung forward high; the far leg four phases on), the
knee solved at the design's thigh and lower-leg lengths (rigkit.elbow, bent forward) - and drawn square by square in the
design's own colours and widths, a little slimmer than the design's balloons: the red-patterned thigh, the plum
balloon with its red stripes, the bronze-teal shin band (the near leg's long plate down its front edge, the far leg's
plate on its knee), the ankle's skin, three shades across lit from the upper left, one outline ring; the design's own
slipper pasted flat on the ankle; the far leg a shade darker on the design's own ramps, drawn first. A foot landing
brings the body STEP rows down. Pinholes are filled, open edges closed, the frame grounded.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import import_nilah_strips as I  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

HIP = 63                  # cropped design row: the design's legs start here (removed; the hips above stay)
SPLIT = 30                # the column between the design's two thighs in its big hip component
HAIR = [(60, 50, 102), (37, 27, 62)]
SKIRT = [(128, 52, 239), (252, 173, 6), (254, 217, 47), (250, 161, 3), (84, 184, 213)]
OUTLINE = (10, 1, 20)
# the design's own leg colours: (lit, mid, dark)
RED = ((186, 44, 43), (147, 32, 37), (107, 29, 54))
PLUM = ((94, 42, 108), (94, 42, 108), (67, 26, 80))
TEAL = ((101, 215, 233), (64, 144, 179), (47, 103, 139))
SKIN = ((214, 120, 63), (214, 120, 63), (165, 83, 43))
# the far leg one shade darker on the design's ramps
DARKER = {(186, 44, 43): (147, 32, 37), (147, 32, 37): (107, 29, 54), (94, 42, 108): (67, 26, 80),
          (67, 26, 80): (52, 11, 106), (101, 215, 233): (64, 144, 179), (64, 144, 179): (47, 103, 139),
          (214, 120, 63): (165, 83, 43), (165, 83, 43): (130, 66, 41), (66, 52, 69): (37, 27, 62)}
# The legs are the design's own two legs, moved whole (never turned, sheared or redrawn): SHAPES "front" is the design's
# front leg (planted ahead, its lower leg upright), "back" its back leg (pushed off behind, its lower leg slanting
# back). Each leg takes the shape its phase needs - ahead or under the hips the front one, behind or swinging the back
# one - moved (columns, rows) from where the design has it; the far leg is the same cycle four frames on, a shade
# darker. Their tops (cut at HIP) stay under the top's hem; the hips' pad fills what a lift opens.
CYCLE = [("front", (0, 0)),     # 1 landing ahead (the design's front leg as it stands)
         ("front", (-3, 0)),    # 2 the body over it
         ("front", (-6, 0)),    # 3 planted under the hips
         ("back", (3, 0)),      # 4 pushing back
         ("back", (0, 0)),      # 5 pushed off behind (the design's back leg as it stands)
         ("back", (4, -4)),     # 6 lifting, swinging forward
         ("back", (8, -6)),     # 7 passing under the hips, the foot up behind
         ("front", (2, -3))]    # 8 reaching forward, about to land
STEP = [0] * 8             # the body never comes down over the legs (rigid pieces: it would sink into them)
PAD = (60, 68, 21, 40)    # cropped design rows / columns of the hips' pad (narrowing from its third row)
HIP_ZONE = 10             # rows under the hips where a line between two filled squares is no edge
SLIT = 30                 # enclosed gaps up to this many squares under the hips are slits a move opened (filled)
PIN = 3                   # enclosed gaps in the legs up to this many squares are pinholes (filled)
UPPER_END = 91            # cropped design row: the skirt panel's end; the body has nothing below it
LIGHT = (-0.6, -0.8)      # the light from the upper left
LEGS = {}
RUN_MS = 100


def masks(d):
    """The design's back leg, front leg and the rest (body, hair, skirt panel)."""
    op = d[..., 3] > 0
    rgb = d[..., :3].astype(int)
    isc = lambda cs: np.any([(rgb == np.array(c)).all(-1) for c in cs], axis=0)
    hair, skirt, outline = isc(HAIR), isc(SKIRT), isc([OUTLINE])
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    reg = op & (yy >= HIP) & ~hair & ~skirt & ~outline
    lab, n = ndimage.label(reg)
    big = np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))) + 1
    back, front = np.zeros_like(op), np.zeros_like(op)
    for j in range(1, n + 1):
        comp = lab == j
        ys, xs = np.nonzero(comp)
        if j == big:
            back |= comp & (xx < SPLIT) & (yy <= 75)
            front |= comp & ~((xx < SPLIT) & (yy <= 75))
        elif xs.mean() < SPLIT:
            back |= comp
        elif ys.max() > 82 or xs.min() < 41:
            front |= comp
    db = ndimage.distance_transform_edt(~back)
    df = ndimage.distance_transform_edt(~front)
    ol = op & outline & (yy >= HIP)
    back |= ol & (db <= 2) & (db <= df)
    front |= ol & (df <= 2) & (df < db)
    kern = np.ones((3, 3))
    for _ in range(2):
        rest_ = op & ~back & ~front & (yy >= HIP)
        nb = ndimage.convolve(back.astype(int), kern, mode="constant")
        nf = ndimage.convolve(front.astype(int), kern, mode="constant")
        back |= rest_ & (nb >= 5) & (nb >= nf)
        front |= rest_ & (nf >= 5) & (nf > nb)
    return back, front, op & ~back & ~front


def leg_layers(d):
    """The design's two legs as RGBA layers (full tone) and their far-tone copies."""
    back, front, _ = masks(d)
    shapes = {"front": np.where(front[..., None], d, 0).astype(np.uint8),
              "back": np.where(back[..., None], d, 0).astype(np.uint8)}
    far = {}
    for k, g in shapes.items():
        f = g.copy()
        for y, x in zip(*np.nonzero(f[..., 3])):
            c = tuple(int(v) for v in f[y, x, :3])
            if c in DARKER:
                f[y, x, :3] = DARKER[c]
        far[k] = f
    return {"near": shapes, "far": far}


def fill_gaps(can, hr):
    """Under the hips (row hr): pinholes take the colour round them, slits a moved leg opened the trousers' dark (one
    square wide: the outline)."""
    opq = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    for j in range(1, n + 1):
        hole = lab == j
        ys_, xs_ = np.nonzero(hole)
        if ys_.min() <= hr:
            continue
        if hole.sum() <= PIN:                    # a pinhole: the colour round it
            ring_ = ndimage.binary_dilation(hole) & ~hole & opq
            cols_ = [tuple(c) for c in can[ring_][:, :3]]
            can[hole] = (*max(set(cols_), key=cols_.count), 255)
        elif hole.sum() <= SLIT:                 # a slit a moved leg opened (by the skirt panel, between the legs):
            can[hole] = (*(OUTLINE if xs_.max() - xs_.min() < 2 else PLUM[2]), 255)   # the trousers behind it
    return can


def run_frame(k, d, upper):
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    x0, y0 = I.AT
    step = STEP[k]
    for which, phase in (("far", (k + 4) % 8), ("near", k)):
        shape, (mx, my) = CYCLE[phase]
        g = LEGS[which][shape]
        ys, xs = np.nonzero(g[..., 3] > 0)
        ty, tx = ys + my + y0 + step, xs + mx + x0
        ok = (ty >= 0) & (ty < I.ROWS) & (tx >= 0) & (tx < I.COLS)
        can[ty[ok], tx[ok]] = g[ys[ok], xs[ok]]
    # the hips' pad behind the legs (no gap opens between the waistband and the thighs)
    for r in range(PAD[0], PAD[1]):
        inset = max(0, r - PAD[0] - 2)
        for c in range(PAD[2] + inset, PAD[3] - inset):
            Y, X = r + y0 + step, c + x0
            if 0 <= Y < I.ROWS and 0 <= X < I.COLS and can[Y, X, 3] == 0:
                can[Y, X] = (*PLUM[2], 255)
    ys, xs = np.nonzero(upper[..., 3] > 0)
    ty, tx = ys + y0 + step, xs + x0
    ok = (ty >= 0) & (ty < I.ROWS) & (tx >= 0) & (tx < I.COLS)
    can[ty[ok], tx[ok]] = upper[ys[ok], xs[ok]]
    # round the hips an outline square between two filled ones above and below takes the colour under it
    hr = y0 + HIP + step - 2
    for _ in range(2):
        for Y in range(max(hr - 4, 1), min(hr + HIP_ZONE, I.ROWS - 1)):
            for X in range(I.COLS):
                if can[Y, X, 3] and (can[Y, X, :3] == OUTLINE).all():
                    a_, b_ = can[Y - 1, X], can[Y + 1, X]
                    if a_[3] and b_[3] and not (a_[:3] == OUTLINE).all() and not (b_[:3] == OUTLINE).all():
                        can[Y, X] = b_
    can = fill_gaps(can, hr)
    can = G.complete_outline(can, color=OUTLINE)[0]
    can = fill_gaps(can, hr)                     # again: closing the outline seals slits that were open to the outside
    can[I.SOLE + 1:] = 0
    return I.ground(can)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the 8 frames side by side at 4x on magenta here")
    a = ap.parse_args()
    d = I.design()
    back, front, body = masks(d)
    body[UPPER_END:] = False              # nothing of the body below the skirt panel (the slippers' dark is the hair's)
    upper = np.where(body[..., None], d, 0).astype(np.uint8)
    LEGS.update(leg_layers(d))
    frames = [run_frame(k, d, upper) for k in range(8)]
    table_path = os.path.join(I.OUT, "frames.json")
    table = json.load(open(table_path, encoding="utf-8"))
    table["run"] = []
    for k, f in enumerate(frames):
        name = f"run_{k + 1}.png"
        Image.fromarray(f).save(os.path.join(I.OUT, name))
        table["run"].append([name, RUN_MS])
    with open(table_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        S = 4
        crop = [f[I.SOLE - 112:I.SOLE + 2, I.PIV - 50:I.PIV + 50] for f in frames]
        big = Image.new("RGBA", (len(crop) * 100 * S, 114 * S), (255, 0, 255, 255))
        for k, c in enumerate(crop):
            big.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((100 * S, 114 * S), Image.NEAREST),
                                (k * 100 * S, 0))
        big.convert("RGB").save(os.path.join(a.review, "nilah_run.png"))
    print("run: 8 frames written")


if __name__ == "__main__":
    main()
