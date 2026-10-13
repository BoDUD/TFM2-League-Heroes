#!/usr/bin/env python3
"""Nilah's run: the design's upper body over League's own running legs drawn in the design's colours
(assets/source/nilah/frames/run_1..8.png; the rest of frames/ untouched).

    python tools/art/run_nilah.py [--renders DIR] [--review DIR]

The user, 2026-10-13, on the first run (the design's legs sheared straight, league_nidalee's way): 「走路时候腿部有变形吧？」 -
the puffy harem trousers sheared into slanted steps, the thighs stayed under the hips while the shins slid, the shins
thinned to a line and the legs ran into one blob. Redone league_zeri's dense way (tools/art/ppu_zeri.py
run_from_renders, approved: 「不要腿部有任何变形」): the legs are League's own legs in its run, every frame - rendered
nearly from the side with the hair, the whip-blade, the orb and both arms left out (assets/source/nilah/run/
run_legs.json; tools/lol/native_pose.py --alpha --parts paints the near and the far leg apart, tools/lol/pose_joints.py
--json gives the hips, knees, feet and toes) at the design's leg length (legs 0.55 and height 101 put League's hips 44
squares over the soles, as the design's are), so a knee bends, a trouser leg balloons and a slipper points as the 3D leg
does - and drawn in the design's colours square by square: every 8x8 block of the render is one square, voting by
material (MATERIAL: the plum trousers, their red pattern, the bronze-teal armour, the skin, the slippers, by hue and
brightness, the region - thigh, shin, foot - from the joints), a speckle with four neighbours of one other colour
taking theirs, a square thicker all round (the design's legs are fuller than League's), one outline ring; the far leg
(League's left) a shade darker. League's run leaps (the hips 45 squares up in four frames): the hips keep only RISE of
League's height over their standing height (pinned on the design's hips the leaps turned into wide lunges), a foot that
would go under the ground lifts the frame - a light, bounding run. The upper body is the side design's above its legs (run_nilah.masks), never moved against the
hips. Without the renders (they show Riot's model and stay local) nothing is written.
"""
import argparse
import colorsys
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

RENDERS = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "nl_work", "run_legs")
HIP = 63                  # cropped design row: the design's legs start here (removed; the hips above stay)
SPLIT = 30                # the column between the design's two thighs in its big hip component
HIP_D = (61, 30)          # cropped design row and column of the hips' middle (League's hips put there)
HAIR = [(60, 50, 102), (37, 27, 62)]
SKIRT = [(128, 52, 239), (252, 173, 6), (254, 217, 47), (250, 161, 3), (84, 184, 213)]
OUTLINE = (10, 1, 20)
# the design's own leg colours, lit and dark
PLUM = ((94, 42, 108), (67, 26, 80))
RED = ((186, 44, 43), (147, 32, 37))
TEAL = ((101, 215, 233), (64, 144, 179))
SKIN = ((214, 120, 63), (165, 83, 43))
SLIP = ((66, 52, 69), (37, 27, 62))
PAD = (60, 68, 21, 40)    # cropped design rows / columns of the hips' pad (narrowing from its third row)
PIN = 3                   # enclosed gaps in the legs up to this many squares are pinholes (filled)
HIP_ZONE = 10            # rows under the hips where a line between two filled squares is no edge
UPPER_END = 91           # cropped design row: the skirt panel's end; the body has nothing below it
SPECK = 8                 # leg pieces smaller than this (stray render blocks under the feet) are dropped
RISE = 0.25               # how much of League's height above the ground the hips keep (its run leaps 45 squares up)
HIP_LEAGUE = 44.4         # League's hips over the soles standing (pose_joints, legs 0.55, height 101)
FAR_SHADE = 0.78          # the far leg: every colour but the outline this much darker
Z = 8                     # render pixels a square
RUN_MS = 100


def masks(d):
    """The design's back leg, front leg and the rest (body, hair, skirt panel) below / above HIP."""
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
        elif ys.max() > 82 or xs.min() < 41:      # the front leg's armour, ankle and slipper (the skirt's bits are higher right)
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


def material(q, region):
    """One render pixel's design colour: by hue, saturation and brightness, and where on the leg it is (the bronze-teal
    armour only on the knee and the shin: League's trousers have a blue-grey sheen that read as armour on the thigh)."""
    h, s, v = colorsys.rgb_to_hsv(*(np.asarray(q[:3], float) / 255.0))
    hue = h * 360
    orange = 15 <= hue <= 50 and s > 0.45 and v > 0.3
    if region == "foot":
        if orange:
            return SKIN[0] if v > 0.55 else SKIN[1]
        return SLIP[0] if v > 0.17 else SLIP[1]
    if orange:                                   # the ankle's skin; on the thigh the pattern's gold is its red
        return (SKIN[0] if v > 0.55 else SKIN[1]) if region == "shin" else RED[0]
    if (hue < 15 or hue > 335) and s > 0.35 and v > 0.18:
        return RED[0] if v > 0.4 else RED[1]
    if region in ("knee", "shin") and 185 <= hue <= 228 and s > 0.15 and v > 0.18:
        return TEAL[0] if v > 0.4 else TEAL[1]
    return PLUM[0] if v > 0.17 else PLUM[1]


def seg_dist(p, a, b):
    a, b, p = np.asarray(a, float), np.asarray(b, float), np.asarray(p, float)
    t = np.clip(np.dot(p - a, b - a) / max(np.dot(b - a, b - a), 1e-9), 0, 1)
    return np.linalg.norm(p - (a + t * (b - a)))


def leg_squares(pose, parts, which, jt, pivot):
    """One leg of one frame as squares (dict (x, y) in cell squares -> colour), voted by material."""
    pp = parts.astype(int)
    opq = pose[..., 3] > 128
    if which == "far":
        m = opq & (pp[..., 0] < 60) & (pp[..., 1] > 100) & (pp[..., 2] > 100)
        side = "L"
    else:
        m = opq & (pp[..., 0] > 100) & (pp[..., 1] < 60) & (pp[..., 2] > 100)
        side = "R"
    px, py = pivot
    J = {k: (px + jt[side + "_" + k][0], py + jt[side + "_" + k][1]) for k in ("Hip", "KneeLower", "Foot", "Toe")}
    out = {}
    H, W = m.shape
    for by in range(H // Z):
        for bx in range(W // Z):
            blk = m[by * Z:(by + 1) * Z, bx * Z:(bx + 1) * Z]
            if blk.sum() < Z * Z // 2:
                continue
            c = (bx + 0.5, by + 0.5)
            dists = {"thigh": seg_dist(c, J["Hip"], J["KneeLower"]), "shin": seg_dist(c, J["KneeLower"], J["Foot"]),
                     "foot": seg_dist(c, J["Foot"], J["Toe"])}
            region = min(dists, key=dists.get)
            if region == "thigh":                    # the last quarter of the thigh is the knee (its armour plate)
                a, b = np.asarray(J["Hip"], float), np.asarray(J["KneeLower"], float)
                t = np.dot(np.asarray(c) - a, b - a) / max(np.dot(b - a, b - a), 1e-9)
                if t > 0.75:
                    region = "knee"
            votes = {}
            for q in pose[by * Z:(by + 1) * Z, bx * Z:(bx + 1) * Z][blk][::3]:
                col = material(q, region)
                votes[col] = votes.get(col, 0) + 1
            out[(bx, by)] = max(votes, key=votes.get)
    return out, J


def draw_leg(sq, shape, hip_y=None):
    """The squares on a canvas of `shape`, pieces under SPECK squares apart from the leg dropped, speckles merged, a
    square thicker all round, one outline ring."""
    g = np.zeros((*shape, 4), np.uint8)
    for (x, y), c in sq.items():
        if 0 <= x < shape[1] and 0 <= y < shape[0]:
            g[y, x] = (*c, 255)
    lab, n = ndimage.label(g[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz < SPECK:
                g[lab == j] = 0
    for _ in range(2):
        op = g[..., 3] > 0
        for y, x in zip(*np.nonzero(op)):
            nb = [tuple(g[y + a, x + b, :3]) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))
                  if 0 <= y + a < shape[0] and 0 <= x + b < shape[1] and g[y + a, x + b, 3]]
            if len(nb) == 4 and len(set(nb)) == 1 and nb[0] != tuple(g[y, x, :3]):
                g[y, x, :3] = nb[0]
    for _ in range(2):                    # flat areas: a square takes the colour most of its 3x3 has (at least 5)
        op = g[..., 3] > 0
        src = g.copy()
        for y, x in zip(*np.nonzero(op)):
            win = src[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2]
            cols = [tuple(c[:3]) for c in win.reshape(-1, 4) if c[3]]
            best = max(set(cols), key=cols.count)
            if cols.count(best) >= 5:
                g[y, x, :3] = best
    op = g[..., 3] > 0
    grow = ndimage.binary_dilation(op) & ~op
    for y, x in zip(*np.nonzero(grow)):
        nb = [(y + a, x + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))
              if 0 <= y + a < shape[0] and 0 <= x + b < shape[1] and op[y + a, x + b]]
        g[y, x] = g[nb[0]]
    op = g[..., 3] > 0
    ring = ndimage.binary_dilation(op) & ~op
    if hip_y is not None:                 # the thigh runs on into the hips: no outline across its top (it showed as a
        ring[:int(hip_y) + 3] = False     # black cut under the top's hem); open edges are closed on the whole frame
    g[ring] = (*OUTLINE, 255)
    return g


def shade(g, k):
    out = g.copy()
    col = (g[..., 3] > 0) & ~(g[..., :3] == np.array(OUTLINE)).all(-1)
    out[col, :3] = (g[col, :3].astype(float) * k).astype(np.uint8)
    return out


def run_frames(renders):
    cells = json.load(open(os.path.join(renders, "nilah_cells.json"), encoding="utf-8"))
    cw, ch = cells["cell"]
    pose = np.asarray(Image.open(os.path.join(renders, "nilah_pose_run.png")).convert("RGBA"))
    parts = np.asarray(Image.open(os.path.join(renders, "nilah_parts_run.png")).convert("RGBA"))
    joints = json.load(open(os.path.join(renders, "joints_run.json"), encoding="utf-8"))
    d = I.design()
    back, front, body = masks(d)
    body[UPPER_END:] = False              # nothing of the body below the skirt panel (the slippers' dark is the hair's)
    upper = np.where(body[..., None], d, 0).astype(np.uint8)
    x0, y0 = I.AT
    hx_c, hy_c = x0 + HIP_D[1], y0 + HIP_D[0]          # the design's hips on the canvas
    frames = []
    for k in range(8):
        cx0, cy0 = (k % 4) * cw * Z, (k // 4) * ch * Z
        cp = pose[cy0:cy0 + ch * Z, cx0:cx0 + cw * Z]
        pp = parts[cy0:cy0 + ch * Z, cx0:cx0 + cw * Z]
        pivot = cells["tags"]["run"][k]["pivot"]
        jt = joints[k]["joints"]
        legs = {}
        hips = []
        for which in ("far", "near"):
            sq, J = leg_squares(cp, pp, which, jt, pivot)
            legs[which] = draw_leg(sq, (ch, cw), J["Hip"][1])
            hips.append(J["Hip"])
        hx = (hips[0][0] + hips[1][0]) / 2
        hy = (hips[0][1] + hips[1][1]) / 2
        up = (pivot[1] + 11) - hy - HIP_LEAGUE          # League's hips over (+) or under (-) their standing height
        hip_row = hy_c - RISE * up
        dx, dy = int(round(hx_c - hx)), int(round(hip_row - hy))
        legs_only = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
        for which, g in (("far", shade(legs["far"], FAR_SHADE)), ("near", legs["near"])):
            ys, xs = np.nonzero(g[..., 3] > 0)
            ty, tx = ys + dy, xs + dx
            ok = (ty >= 0) & (ty < I.ROWS) & (tx >= 0) & (tx < I.COLS)
            legs_only[ty[ok], tx[ok]] = g[ys[ok], xs[ok]]
        # a foot under the ground lifts the whole frame (legs and body) until it stands on it
        low = int(np.nonzero(legs_only[..., 3].any(1))[0].max())
        lift = min(0, I.SOLE - low)
        can = np.roll(legs_only, lift, axis=0)
        lift += int(round(hip_row - hy_c))               # the body rides on the hips
        # the hips' pad behind the legs: the trousers' dark under the body's waistband, so no gap opens between it and
        # the thighs' tops (the gap took the outline: a black cut across the hips)
        for r in range(PAD[0], PAD[1]):
            inset = max(0, r - PAD[0] - 2)
            for c in range(PAD[2] + inset, PAD[3] - inset):
                Y, X = r + y0 + lift, c + x0
                if 0 <= Y < I.ROWS and 0 <= X < I.COLS and can[Y, X, 3] == 0:
                    can[Y, X] = (*PLUM[1], 255)
        ys, xs = np.nonzero(upper[..., 3] > 0)
        ty, tx = ys + y0 + lift, xs + x0
        ok = (ty >= 0) & (ty < I.ROWS) & (tx >= 0) & (tx < I.COLS)
        can[ty[ok], tx[ok]] = upper[ys[ok], xs[ok]]
        # round the hips an outline square between two filled ones above and below (a thigh's top edge under the pad)
        # takes the colour under it: no line across the hips
        hr = y0 + HIP_D[0] + lift
        for _ in range(2):
            for Y in range(max(hr - 4, 1), min(hr + HIP_ZONE, I.ROWS - 1)):
                for X in range(I.COLS):
                    if can[Y, X, 3] and (can[Y, X, :3] == OUTLINE).all():
                        a_, b_ = can[Y - 1, X], can[Y + 1, X]
                        if a_[3] and b_[3] and not (a_[:3] == OUTLINE).all() and not (b_[:3] == OUTLINE).all():
                            can[Y, X] = b_
        # pinholes in the legs (at most PIN squares enclosed, under the hips) take the colour most of their neighbours have
        opq = can[..., 3] > 0
        lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
        for j in range(1, n + 1):
            hole = lab == j
            ys_, xs_ = np.nonzero(hole)
            if hole.sum() <= PIN and ys_.min() > hr:
                ring_ = ndimage.binary_dilation(hole) & ~hole & opq
                cols_ = [tuple(c) for c in can[ring_][:, :3]]
                can[hole] = (*max(set(cols_), key=cols_.count), 255)
        can = G.complete_outline(can, color=OUTLINE)[0]
        can[I.SOLE + 1:] = 0
        frames.append(can)
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--renders", default=RENDERS)
    ap.add_argument("--review", help="write the 8 frames side by side at 4x on magenta here")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.renders, "nilah_pose_run.png")):
        sys.exit("no League renders: tools/lol/native_pose.py assets/source/nilah/run/run_legs.json --alpha --parts "
                 "and tools/lol/pose_joints.py ... --tag run --json joints_run.json into " + a.renders)
    frames = run_frames(a.renders)
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
