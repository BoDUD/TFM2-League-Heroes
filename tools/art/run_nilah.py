#!/usr/bin/env python3
"""Nilah's run, posed the way the pack's accepted runs are (art-spec "Strips posed from the design's own parts":
league_shen's tools/art/fix_shen_strips.py stride_frame / run_upper) - assets/source/nilah/frames/run_1..8.png; the rest
of frames/ untouched.

    python tools/art/run_nilah.py [--review DIR]

The user's verdicts, 2026-10-13: the design's legs sheared - 「走路时候腿部有变形吧？」; League's legs in their texture's
colours - 「还是变形啊 自己不看吗」「而且腿这么粗？」; the design's legs slid whole - 「还是不对 不修改到完美不要联络我」;
the design's and Codex's leg drawings mixed - 「这里还有变形看不到吗」 (seams at the hips, lengths and knee guards
changing frame to frame). The art-spec's rules for a run: legs are never squashed, slid or sheared - a bent knee draws
the leg on its joints in the design's own colours, the same shape in every frame, the design's boots whole; the run is
its own pose - the upper body leans in, the head moved whole. Six internal reviews (2026-10-14) settled the rest. So:
  * the legs: tools/art/nilah_stride.py - League's Run (8 frames, assets/source/nilah/run/run_legs.json -> run_joints.json)
    gives the thigh and shin angles and the leap, the design's bone lengths take them; each bone one drawing read off
    the design (see its docstring: profiles, bands, the feet along a trailing shin, the hips 0.7 apart, the balloon's
    sag). The far leg is drawn first, the seat (RUMP: the design's own back-thigh top) over it, the ponytail, the near
    leg, then the body;
  * the skirt panel and its teal border stay with the body (TRIM); the teal strap down the near leg is the leg's own;
  * the upper body leans into the run: every row of the torso from the hips (HIP) up to the neck (NECK) moved forward
    LEAN columns a row, and the parts that must not shear moved whole with the row they hang from - the head (above
    NECK), the ponytail (from its root), the folded whip-blade with the hand and the red-wrapped forearm holding it
    (one rigid unit, the blade upright), the front arm with its open hand (from the shoulder); everything moves with the
    leap's rows;
  * the seams: where the far leg runs beside the near one a single outline (merge_legs); a foot in the air kept a square
    of ground off the ponytail (nilah_stride.away_from); every exposed edge of the drawn legs and the seat lined; new
    one-square cracks closed (the body's own, the design's, kept); orphan outline taken out only where the design did
    not draw it;
  * every frame is audited (rigkit.audit: pieces, holes, orphan outline, nothing under the soles); 175 ms a frame,
    League's pace (Run.anm 1.4 s).
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
import nilah_stride as NS  # noqa: E402
import rigkit as K  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

JOINTS = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "nl_work", "run_legs", "joints_run.json")
RUN_JOINTS = os.path.join(ROOT, "assets", "source", "nilah", "run", "run_joints.json")   # the committed copy
HIP = 63                  # cropped design row: the legs start here; the torso leans from here up
NECK = 27                 # cropped design row: the chin; the head above it moves as one block
LEAN = 0.15               # columns forward a row up the torso (5 at the neck: about 8 degrees)
SPLIT = 30                # the column between the design's two thighs in its big hip component
HAIR = [(60, 50, 102), (37, 27, 62)]
SKIRT = [(128, 52, 239), (252, 173, 6), (254, 217, 47), (250, 161, 3), (84, 184, 213)]
OUTLINE = (10, 1, 20)
RED = [(186, 44, 43), (147, 32, 37), (107, 29, 54)]
TEAL = [(101, 215, 233), (64, 144, 179), (47, 103, 139), (84, 184, 213)]
TRIM = dict(rows=(61, 91), x0=37, strap=(71, 46))   # the skirt panel's teal border (and the teal at the waist) stays
                                    # with the body; the teal strap down the near leg's front (rows from 71, columns
                                    # left of 46) is the leg's own (nilah_stride draws it on the near leg): kept with the
                                    # body it hung in the air like a chain when the leg swung back
RUMP = dict(centre=(27.5, 62.5), radii=(7.5, 5.0))   # the seat behind the hips: the design's own back-thigh top in
                                    # this ellipse stays with the body (the far thigh swung forward left a red point)
# rigid parts of the upper body (cropped design rows / columns) and the row whose lean moves each
BLADE = dict(box=(0, 47, 0, 21), row=30)            # the folded whip-blade, the hand round its grip, its lower point
FOREARM = dict(box=(30, 45, 19, 30), row=30)        # the red-wrapped forearm holding it (red squares and their outline)
FRONT_ARM = dict(box=(28, 52, 43, 56), row=40)      # the front arm with its open hand
TAIL = dict(box=(25, 92, 0, 27), row=28, tips=60)   # the ponytail (hair squares and their outline)
UPPER_END = 91            # cropped design row: the skirt panel's end; the body has nothing below it
RUN_MS = 175               # League's Run: 1.4 s a cycle, its 8 frames 175 ms apart (art-spec: League's pace)
PIN = 3                   # enclosed gaps up to this many squares under the hips (between drawn legs) filled
CLOSE = 12                # enclosed gaps up to this many squares above the hips (where moved parts left them) closed


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


def trim_mask(d):
    """The skirt panel's teal trim over the near leg (and its outline): part of the body, not the leg."""
    op = d[..., 3] > 0
    rgb = d[..., :3].astype(int)
    isc = lambda cs: np.any([(rgb == np.array(c)).all(-1) for c in cs], axis=0)
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    box = (yy >= TRIM["rows"][0]) & (yy < TRIM["rows"][1]) & (xx >= TRIM["x0"])
    box &= (yy < TRIM["strap"][0]) | (xx >= TRIM["strap"][1])
    t = op & isc(TEAL) & box
    return t | (op & isc([OUTLINE]) & box & ndimage.binary_dilation(t, np.ones((3, 3), bool)))


def rump_mask(back):
    """The seat behind the hips: the design's back leg's squares in the RUMP ellipse under the hips' row."""
    yy, xx = np.mgrid[0:back.shape[0], 0:back.shape[1]]
    (cx, cy), (rx, ry) = RUMP["centre"], RUMP["radii"]
    return back & (yy >= HIP) & (((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1.0)


def shift_of(y):
    """The lean's columns at design row y: 0 at and under the hips, LEAN a row up to the neck, the neck's above it."""
    return int(round((HIP - max(min(y, HIP), NECK)) * LEAN))


def upper_parts(d, body):
    """The upper body in parts: {name: (mask, row its lean moves it by)} with "torso" the rest (leant row by row)."""
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    rgb = d[..., :3].astype(int)
    isc = lambda cs: np.any([(rgb == np.array(c)).all(-1) for c in cs], axis=0)
    hair, red, outline = isc(HAIR), isc(RED), isc([OUTLINE])
    inbox = lambda b: (yy >= b[0]) & (yy < b[1]) & (xx >= b[2]) & (xx < b[3])
    taken = np.zeros_like(body)
    parts = {}
    head = I.head_mask() & body
    parts["head"] = (head, NECK)
    taken |= head
    tail = body & ~taken & inbox(TAIL["box"]) & hair
    tail |= body & ~taken & inbox(TAIL["box"]) & outline & ndimage.binary_dilation(tail, np.ones((3, 3), bool))
    tips = body & ~taken & inbox(TAIL["box"]) & outline & (yy >= TAIL["tips"])
    for _ in range(3):                          # the outline squares the strands' tips hang on (one left behind was a speck)
        tail |= tips & ndimage.binary_dilation(tail, np.ones((3, 3), bool))
    parts["tail"] = (tail, TAIL["row"])
    taken |= tail
    blade = body & ~taken & inbox(BLADE["box"]) & ~hair
    fore = body & ~taken & inbox(FOREARM["box"]) & red
    fore |= body & ~taken & inbox(FOREARM["box"]) & outline & ndimage.binary_dilation(fore, np.ones((3, 3), bool))
    parts["blade"] = (blade | fore, BLADE["row"])
    taken |= blade | fore
    farm = body & ~taken & inbox(FRONT_ARM["box"])
    parts["front_arm"] = (farm, FRONT_ARM["row"])
    taken |= farm
    parts["torso"] = (body & ~taken, None)
    return parts


def lean_layer(d, mask, row, x0, y0, bob):
    """A part on the canvas, leant: moved whole by its row's shift, or (row None) every row by its own."""
    out = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    ys, xs = np.nonzero(mask)
    sh = np.full(len(ys), shift_of(row)) if row is not None else np.array([shift_of(y) for y in ys])
    ty, tx = ys + y0 + bob, xs + x0 + sh
    ok = (ty >= 0) & (ty < I.ROWS) & (tx >= 0) & (tx < I.COLS)
    out[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]
    return out


def put(can, g):
    m = g[..., 3] > 0
    can[m] = g[m]


def close_gaps(can, rows):
    """Small enclosed gaps (up to CLOSE squares) in `rows` - where a part moved off the torso - take the colour most of
    their filled, not outline, neighbours have (the outline between outlines)."""
    opq = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    for j in range(1, n + 1):
        hole = lab == j
        ys_, _ = np.nonzero(hole)
        if hole.sum() <= CLOSE and ys_.min() >= rows[0] and ys_.max() < rows[1]:
            ring_ = ndimage.binary_dilation(hole) & ~hole & opq
            cols_ = [tuple(c) for c in can[ring_][:, :3] if tuple(c) != OUTLINE]
            can[hole] = (*(max(set(cols_), key=cols_.count) if cols_ else OUTLINE), 255)
    return can


def merge_legs(can, far, near):
    """Where the far leg runs beside the near one, one outline between them, not three or four (the far leg's own
    outline, one or two squares of ground, the near leg's outline): the ground between them and the far leg's outline
    square beside the near leg's outline (or between its fill and the filled ground) take the far leg's nearest fill."""
    O = np.array(OUTLINE, np.uint8)
    farop = far[..., 3] > 0
    ffill = farop & ~(far[..., :3] == O).all(-1)
    if not ffill.any():
        return can
    _, (iy, ix) = ndimage.distance_transform_edt(~ffill, return_indices=True)
    fillcol = far[iy, ix]
    H, W = can.shape[:2]

    def at(m, dy, dx):                          # at(m, dy, dx)[y, x] = m[y + dy, x + dx] (False off the canvas)
        out = np.zeros_like(m)
        out[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)] = m[max(0, dy):H - max(0, -dy),
                                                                         max(0, dx):W - max(0, -dx)]
        return out

    nink = (near[..., 3] > 0) & (near[..., :3] == O).all(-1) & (can == near).all(-1)
    filled = np.zeros((H, W), bool)
    for _ in range(2):                          # ground one or two squares wide between the legs
        farside = (farop & (can == far).all(-1)) | filled
        clear = can[..., 3] == 0
        gap = np.zeros((H, W), bool)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            behind = at(farside, -dy, -dx)
            gap |= clear & behind & (at(nink, dy, dx) | (at(clear, dy, dx) & at(nink, 2 * dy, 2 * dx)))
        can[gap] = fillcol[gap]
        filled |= gap
    shows_far = farop & (can == far).all(-1)
    fink = shows_far & (far[..., :3] == O).all(-1)
    own = (shows_far & ffill) | filled
    nb_ink = at(nink, 0, 1) | at(nink, 0, -1) | at(nink, 1, 0) | at(nink, -1, 0)
    nb_own = at(own, 0, 1) | at(own, 0, -1) | at(own, 1, 0) | at(own, -1, 0)
    beside = fink & nb_ink & nb_own                                  # beside the near leg's outline
    between = fink & ((at(own, 0, 1) & at(own, 0, -1)) | (at(own, 1, 0) & at(own, -1, 0)))   # or inside its own fill
    can[beside | between] = fillcol[beside | between]
    return can


def run_frame(k, d, parts, joints):
    x0, y0 = I.AT
    tail_m, tail_row = parts["tail"]
    far, near, bob, _ = NS.stride(joints, k, d, (I.ROWS, I.COLS), origin=(x0, y0),
                                  avoid=lambda b: lean_layer(d, tail_m, tail_row, x0, y0, b)[..., 3] > 0)
    layer = {name: lean_layer(d, m, row, x0, y0, bob) for name, (m, row) in parts.items()}
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    for g in (far, layer["rump"], layer["tail"], near, layer["torso"], layer["front_arm"], layer["blade"],
              layer["head"]):
        put(can, g)
    can = merge_legs(can, far, near)
    mine = np.zeros(can.shape[:2], bool)        # squares the design's own parts gave (their outline is never cut)
    for name in ("rump", "tail", "torso", "front_arm", "blade", "head"):
        mine |= layer[name][..., 3] > 0
    # where the leant torso and the parts moved whole part company, close the small gaps (the design's own gaps kept)
    can = close_gaps(can, (y0, y0 + HIP + bob))
    can = G.complete_outline(can, color=OUTLINE)[0]
    drawn = np.zeros(can.shape[:2], bool)       # the seat's cut edge and the drawn legs' edges where moved or merged
    for g in (layer["rump"], far, near):        # squares left them open (complete_outline leaves dark fills unlined)
        drawn |= (g[..., 3] > 0) & (can == g).all(-1)
    drawn |= (can[..., 3] > 0) & ~(can[..., :3] == OUTLINE).all(-1) & ~mine & (np.arange(I.ROWS)[:, None] >= y0 + HIP + bob)
    drawn &= ~(can[..., :3] == OUTLINE).all(-1)
    can[NS.ring4(drawn) & (can[..., 3] == 0)] = (*OUTLINE, 255)
    can = close_gaps(can, (y0, y0 + HIP + bob))
    while True:                                 # new outline squares with no colour beside them (rigkit.orphan_outline)
        gone = K.orphan_outline(can, OUTLINE) & ~mine
        if not gone.any():
            break
        can[gone] = 0
    can[I.SOLE + 1:] = 0
    can = pinholes(can, y0 + HIP + bob)
    upper = np.zeros_like(can)                  # the body alone: its cracks are the design's own and stay (not the
    for name in ("tail", "torso", "front_arm", "blade", "head"):    # seat's: it stays put while the leant tail moves)
        put(upper, layer[name])
    own = cracks(upper)
    for _ in range(4):                          # one-square cracks the legs (and the seat) make against the body
        new = cracks(can) & ~own
        if not new.any():
            break
        can[new] = (*OUTLINE, 255)
    return can


def cracks(a):
    """Clear squares with opaque squares on both sides (left and right, or above and below)."""
    op = a[..., 3] > 0
    p = np.pad(op, 1)
    return ~op & ((p[1:-1, :-2] & p[1:-1, 2:]) | (p[:-2, 1:-1] & p[2:, 1:-1]))


def pinholes(can, top):
    """Enclosed gaps of up to PIN squares from row `top` down (between the drawn legs) take the commonest colour round
    them (the outline's only if nothing else is there)."""
    opq = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    for j in range(1, n + 1):
        hole = lab == j
        ys_, _ = np.nonzero(hole)
        if hole.sum() <= PIN and ys_.min() >= top:
            ring_ = ndimage.binary_dilation(hole) & ~hole & opq
            cols_ = [tuple(c) for c in can[ring_][:, :3] if tuple(c) != OUTLINE]
            can[hole] = (*(max(set(cols_), key=cols_.count) if cols_ else OUTLINE), 255)
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the 8 frames side by side at 4x on magenta here")
    a = ap.parse_args()
    src = JOINTS if os.path.exists(JOINTS) else RUN_JOINTS
    joints = json.load(open(src, encoding="utf-8"))
    if src == JOINTS:                           # keep the joints the run is drawn on (numbers only, no Riot art)
        os.makedirs(os.path.dirname(RUN_JOINTS), exist_ok=True)
        with open(RUN_JOINTS, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(joints, fh, indent=1)
    d = I.design()
    back, front, body = masks(d)
    tm = trim_mask(d)
    body |= tm
    body[UPPER_END:] = False                    # nothing of the body below the skirt panel (the slippers' dark is the hair's)
    parts = upper_parts(d, body)
    parts["rump"] = (rump_mask(back), None)
    frames = [run_frame(k, d, parts, joints) for k in range(8)]
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
        crop = [f[I.SOLE - 118:I.SOLE + 2, I.PIV - 60:I.PIV + 50] for f in frames]
        big = Image.new("RGBA", (len(crop) * 110 * S, 120 * S), (255, 0, 255, 255))
        for k, c in enumerate(crop):
            big.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((110 * S, 120 * S), Image.NEAREST),
                                (k * 110 * S, 0))
        big.convert("RGB").save(os.path.join(a.review, "nilah_run.png"))
    print("run: 8 frames written")


if __name__ == "__main__":
    main()
