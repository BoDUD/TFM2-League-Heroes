#!/usr/bin/env python3
"""league_orianna's action frames posed from the approved design's own squares (no Codex strips: the user, 2026-10-16,
「动作帧的话你可以参考塔姆那样做 这样就不需要codex了」 - tools/art/rig_tahmkench.py's way).

    python tools/art/rig_orianna.py --review DIR        # every tag on the canvas, 8x sheets + a 3x GIF per tag
    python tools/art/rig_orianna.py                     # the frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero orianna && python tools/art/ppu_hd.py --hero orianna

The design: assets/source/orianna/hd/design.png = model2_ppu22, Codex's step-1 take 2 read back on its own grid
(model2, 54 x 99 squares, PPU 2.6) with 15 rows and 8 columns deleted evenly (design_orianna_cut.even_cut: the eyes,
the throat's gear emblem and the clear columns between the hand and the skirt kept) - 46 x 84 squares bun top to soles,
38 game rows at PPU 2.2. The first rig ran on model2_cut (31 x 57 at PPU 1.5, half the lines gone): the user,
「腿变形啊哥 还有为什么这么模糊」 - its 4-square legs broke at every shifted row - then 2.6 looked 「又太清晰了」 and they
picked 「PPU 2.2（84 行）」. Parts are cut by fixed square ranges and posed only losslessly (memory
no-deformation-lossless-poses): whole-part moves, the near arm turned about its shoulder by quarter turns and mirrors,
whole-row shifts (the legs' thighs and shins), layering (the body sinking over the legs). The legs are jointed like a
doll's: the knee's and the ankle's gold balls and the boot are carried whole, only the thigh and the shin between them
slant. Nothing is redrawn; tidy() closes the outline round moved edges and fills pinholes. The ball is not in her
frames (its own picture, the kit's views).
Actions (League's clips, tools/lol/pose_ref.py --hide-joints 'Ball|Spinnig', for the beats):
  idle 8    breathing: the whole body (the skirt and the arms too) dipping 0-3 rows over the standing legs
  run 8     League's run (Orianna_run's feet per frame from their hips, pose_joints): the legs (the near leg's own
            squares mirrored, toe forward, for both, the far one behind) swinging straight from the design's hips like a
            pendulum, the swinging foot just clear of the ground with its knee a little ahead; the body (the arm with
            it) bobbing over them
  attack 5  the flick (Orianna_attack1): the near arm back and up, swung forward over the chest (the bolt leaves on
            frame 3), held, back
  skill 4   Command (orianna_spell1): the near arm back, then pointing ahead over the chest, held, back
  skill_w 4 Dissonance (Orianna_spell2's hop): up with the near arm raised behind her, down
  skill_e 4 Protect (Orianna_spell3's rise on the toes): up a little, the arm raised, then pointing ahead
  ult 5     Shockwave (Orianna_spell4's crouch): the arm raised behind, the body sinking over the legs, the arm out
            behind, then thrust ahead at the blast (frame 5, 480 ms: the kit's r_delay 30)
  hit 2     moved back with a white flash
  dead 6    a flinch back, the near knee going out as the body sinks into the skirt, the head dropping forward over the
            neck, the eyes shut
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "orianna")
STEM = os.path.join(ROOT, "league", "champions", "league_orianna")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 2.2                         # 84 squares bun top to soles = 38 game rows
FEET = 11                         # 1x rows from the pivot down to the ground row
N = 160                           # the canvas, squares
SOLE, PIV_X = 126, 80             # the soles' row and the pivot column on the canvas
CORNER = (PIV_X + 0.5, SOLE + 1)
ORDER = ["idle", "run", "attack", "skill", "skill_w", "skill_e", "ult", "hit", "dead"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


DESIGN = load(os.path.join(SRC, "hd", "design.png"))
DH, DW = DESIGN.shape[:2]                         # 84 x 46
OP = DESIGN[..., 3] > 0
FEET_MID = 31                                     # the design's column between the feet
X0, Y0 = PIV_X - FEET_MID, SOLE - (DH - 1)        # where the design's (0, 0) goes standing


def palette():
    cols = {tuple(int(v) for v in c) for c in DESIGN[OP][:, :3]}
    return np.array(sorted(cols, key=sum), np.uint8)


PAL = palette()
OUTLINE = tuple(int(v) for v in PAL[0])
TEAL = tuple(int(v) for v in DESIGN[19, 27, :3])  # the eyes' colour (row 19, columns 27-28 and 31)

# ------------------------------------------------------------------------------------------------- parts (design)
ARM_TOP = 32                                      # the near arm from this row (the shoulder's gold ball, rows 28-31,
                                                  # stays on the body)
SHOULDER = (17.5, 32.0)                           # its pivot: the top of the upper arm


def arm_lim(y):
    """The near arm's last column on design row y (the torso / skirt start right of it; the hand ends at 11 with a
    column clear before the skirt)."""
    return (19 if y <= 33 else 18 if y <= 36 else 17 if y <= 37 else 16 if y <= 38 else 15 if y <= 39
            else 14 if y <= 44 else 12 if y <= 45 else 11)


def mask(pred):
    m = np.zeros((DH, DW), bool)
    for y in range(DH):
        for x in range(DW):
            m[y, x] = OP[y, x] and pred(y, x)
    return m


NEAR_ARM = mask(lambda y, x: ARM_TOP <= y <= 55 and x <= arm_lim(y))
LEG_TOP = 55                                      # the legs below the skirt (its centre spike ends on row 55)
NEAR_LEG = mask(lambda y, x: y >= LEG_TOP and 17 <= x <= 27)
FAR_LEG = mask(lambda y, x: (y >= LEG_TOP + 1 and x >= 29) or (y == LEG_TOP and x >= 30))
HEAD_BOTTOM = 23                                  # the bun to the chin

def greyish(y, x):
    """A square of the limbs' metal (grey, silver, white): the skirt is gold, orange and brown, its outline dark."""
    r, g, b = (int(v) for v in DESIGN[y, x, :3])
    return OP[y, x] and r + g + b >= 110 and max(r, g, b) - min(r, g, b) < 60


# the thighs showing between the skirt's spikes (design rows 47-54, grey squares over the legs' columns): they move with
# the run's legs - left on the body they stood still while the legs stepped (「腿部看着很奇怪」: a dark lump under the skirt)
THIGHS = mask(lambda y, x: 47 <= y < LEG_TOP and 17 <= x <= 37 and greyish(y, x))
RUN_TOP = 47                                      # a run leg from this row: its thigh goes on up under the skirt


def run_leg():
    """The near leg from RUN_TOP, mirrored: rows RUN_TOP..56 are its row 56 (the first whole row of the thigh, under
    the skirt's spikes) repeated - the thigh goes on up as one tube under the skirt (its own squares there were cut by
    the spikes and showed their stumps when it moved) - then the design's leg; cut to its box."""
    a = np.zeros((DH - RUN_TOP, DW, 4), np.uint8)
    for y in range(RUN_TOP, DH):
        src = max(y, 56)
        row = np.where((NEAR_LEG[src])[:, None], DESIGN[src], 0)
        a[y - RUN_TOP] = row
    xs = np.nonzero(a[..., 3].max(0) > 0)[0]
    a = a[:, xs.min():xs.max() + 1][:, ::-1].copy()
    hip = a.shape[1] - 1 - (22 - xs.min())       # the leg's top middle column (design column 22)
    return a, hip


LEG, LEG_HIP_X = run_leg()


# ------------------------------------------------------------------------------------------------- composing
def blank():
    return np.zeros((N, N, 4), np.uint8)


def put(dst, src, m, dx, dy, under=False):
    """src's pixels under mask m (src coordinates) onto dst moved by (dx, dy); under: only where dst is clear."""
    ys, xs = np.nonzero(m)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    dst[ty, tx] = src[ys, xs]


# the near arm's turns about the shoulder: (dx, dy) -> matrix rows; every one of them maps squares onto squares
TURNS = {
    "rest": ((1, 0), (0, 1)),       # down and back (the design)
    "point": ((0, 1), (-1, 0)),     # ahead and a little down, over the chest (a quarter turn)
    "up": ((1, 0), (0, -1)),        # raised up and back, behind the hair (mirrored top to bottom)
    "back": ((0, -1), (-1, 0)),     # out behind and up (a quarter turn the other way, mirrored)
}
# (a mirrored "down in front of the skirt" was dropped on the first rig: its hand sank into the skirt)
# where the turned arm's shoulder end goes (columns forward, rows down): an arm turned forward over the chest from the
# shoulder itself merges with the torso; moved this far it reaches out past the body at chest height, its root on the
# chest, clear of the neck
TURN_AT = {"point": (8, -4)}


def arm(dst, turn, dx=0, dy=0, under=False):
    """The near arm turned about the shoulder (canvas: the shoulder moved by dx, dy with the body)."""
    (a, b), (c, d) = TURNS[turn]
    ax, ay = TURN_AT.get(turn, (0, 0))
    dx, dy = dx + ax, dy + ay
    ys, xs = np.nonzero(NEAR_ARM)
    sx, sy = SHOULDER
    rx, ry = xs + 0.5 - sx, ys + 0.5 - sy
    tx = np.floor(sx + a * rx + b * ry).astype(int) + X0 + dx
    ty = np.floor(sy + c * rx + d * ry).astype(int) + Y0 + dy
    ok = (ty >= 0) & (ty < N) & (tx >= 0) & (tx < N)
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    dst[ty, tx] = DESIGN[ys, xs]


# LEG's rows (design rows 47-83): the thigh (47-57, under the skirt down to row 55), the knee's gold ball (58-62)
# carried whole, the shin with its plate (63-72), the ankle's gold ball and the boot (73-83) carried whole: a doll's
# jointed leg - a whole-leg shear bent the boot and the balls; a 3-row thigh put the knee beside the hip (「腿变形」)
THIGH, KNEE, SHIN = range(0, 11), range(11, 16), range(16, 26)


def leg(dst, hip_x, top_y, foot_dx, knee_dx=0, lift=0):
    """A run leg from LEG: its top middle at canvas (hip_x, top_y - lift); the thigh's rows shifted toward the knee
    (half the foot's offset, knee_dx more), the knee's ball at the knee, the shin's rows on to the foot's offset, the
    ankle's ball and the boot moved whole by it."""
    knee = foot_dx / 2 + knee_dx
    for r in range(LEG.shape[0]):
        if r in THIGH:
            off = knee * (r + 1) / (len(THIGH) + 1)
        elif r in KNEE:
            off = knee
        elif r in SHIN:
            off = knee + (foot_dx - knee) * (r - SHIN.start + 1) / (len(SHIN) + 1)
        else:
            off = foot_dx
        k = int(round(off))
        row = LEG[r]
        ty = top_y - lift + r
        if ty < 0 or ty >= N:
            continue
        for x in np.nonzero(row[:, 3] > 0)[0]:
            tx = hip_x - LEG_HIP_X + x + k
            if 0 <= tx < N and dst[ty, tx, 3] == 0:
                dst[ty, tx] = row[x]


def pose(turn="rest", bob=0, dx=0, lift=0, sink=0, splay=0, bow=(0, 0)):
    """The design standing: the body (all but the near arm and the legs) dx columns forward and bob + sink rows down
    over the legs (they stay: a dip or a crouch covers their tops, nothing is stretched), everything lifted `lift` rows
    (a hop), the near arm in `turn` (behind the body when raised); splay: the near leg moved that many columns out (a
    collapse: the knee going out under the skirt; the far leg splays in the design), only below the sunk hem; bow: the
    head moved (dx, dy) over the neck (a slump)."""
    can = blank()
    under = turn in ("up", "back")
    legs = NEAR_LEG | FAR_LEG
    body = OP & ~NEAR_ARM & ~legs
    head = body & (np.arange(DH)[:, None] < HEAD_BOTTOM)
    if bow != (0, 0):
        body = body & ~head
    ady = bob + sink - lift
    if under:
        arm(can, turn, dx, ady)
    if splay:
        under_hem = np.arange(DH)[:, None] >= LEG_TOP + sink
        put(can, DESIGN, NEAR_LEG & under_hem, X0 + dx - splay, Y0 - lift)
        put(can, DESIGN, FAR_LEG & under_hem, X0 + dx, Y0 - lift)
    else:
        put(can, DESIGN, legs, X0 + dx, Y0 - lift)
    put(can, DESIGN, body, X0 + dx, Y0 + ady)
    if bow != (0, 0):
        put(can, DESIGN, head, X0 + dx + bow[0], Y0 + ady + bow[1])
    if not under:
        arm(can, turn, dx, ady)
    can[SOLE + 1:] = 0
    return can


def shift(a, dx, dy):
    out = np.zeros_like(a)
    ys, xs = np.nonzero(a[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < N) & (tx >= 0) & (tx < N) & (ty <= SOLE)
    out[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
    return out


def flash(a, k=0.55):
    out = a.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


def shut_eyes(a):
    out = a.copy()
    m = np.all(out[..., :3] == np.array(TEAL, np.uint8), axis=-1) & (out[..., 3] > 0)
    out[m, :3] = OUTLINE
    return out


# ------------------------------------------------------------------------------------------------- the run
# League's run (Orianna_run, a 1.35 s cycle, 8 frames 169 ms apart; tools/lol/pose_joints.py at 38 game rows, yaw 45):
# per frame the left (near) and right (far) foot's x, its lift off the ground and the knee's x, game px from the body's
# middle (the planted foot's ankle sits 1.8 px up: taken off the lifts)
LEAGUE_RUN = [(-7.5, 4.3, -3.3, 8.0, 0.0, 5.7), (-7.2, 4.5, -1.5, 3.6, 0.1, 6.5), (-1.0, 2.4, 3.6, -0.4, 0.0, 5.2),
              (5.3, 0.0, 3.5, -4.1, 0.3, 1.2), (6.1, 0.2, 3.3, -6.2, 5.6, -0.3), (2.5, 0.0, 3.7, -5.7, 4.8, 1.1),
              (-0.9, 0.0, 2.6, -0.5, 3.0, 5.5), (-4.3, 0.2, -0.4, 5.7, 0.0, 5.6)]
LEAGUE_HIPS = (-1.6, 1.2)         # League's left / right thigh x (the feet are taken from their own hip)
RUN_K = 1.0                       # design squares a League px for the feet's swing (PPU 2.2 x 0.45)
RUN_LIFT = 0.4                    # the lifts: League's foot comes up behind on a folded shin - a turn no lossless move
                                  # makes; lifting the whole leg that high read as a short, floating, dislocated leg
                                  # (「腿部看着很奇怪 感觉还是变形的」), so the legs swing straight like a pendulum and the
                                  # swinging foot only clears the ground
RUN_BEND = 1.5                    # the swinging leg's knee this many columns ahead of its line
RUN_HIPS = (22, 32)               # the legs' tops (design columns): the design's own (nearer, the two thighs ran into one
                                  # dark block under the skirt)
RUN_BOB = [0, 1, 2, 1, 0, 1, 2, 1]   # the pelvis is highest at the widest split (League: frames 0 and 4)
RUN_MS = 169


def run_frame(i):
    """Frame i: each foot where League's is from its own hip (scaled), the swinging one lifted a little with the knee
    bent ahead; the far leg first, the near leg over it, the body (the arm with it) over their tops."""
    can = blank()
    bob = RUN_BOB[i]
    nfx, nl, nkx, ffx, fl, fkx = LEAGUE_RUN[i]
    top = Y0 + RUN_TOP

    def params(fx, hip, lift):
        return int(round((fx - hip) * RUN_K)), (RUN_BEND if lift > 0.5 else 0.0), int(round(lift * RUN_LIFT))

    fd, fk, flift = params(ffx, LEAGUE_HIPS[1], fl)
    leg(can, X0 + RUN_HIPS[1], top, fd, fk, flift)
    near = blank()
    nd, nk, nlift = params(nfx, LEAGUE_HIPS[0], nl)
    leg(near, X0 + RUN_HIPS[0], top, nd, nk, nlift)
    m = near[..., 3] > 0
    can[m] = near[m]
    body = OP & ~NEAR_ARM & ~NEAR_LEG & ~FAR_LEG & ~THIGHS
    put(can, DESIGN, body, X0, Y0 + bob)
    arm(can, "rest", 0, bob)
    can[SOLE + 1:] = 0
    return can


# ------------------------------------------------------------------------------------------------- actions
IDLE_MS = 150
# the breath: the whole body (skirt and arms too) dips over the standing legs, nothing stretched (the first version
# lifted the rows above the waist and repeated the waist's row into the gap: 「上下摆动模型变形」)
BREATH = [0, 1, 2, 3, 3, 3, 2, 1]


def frames():
    out = {}
    out["idle"] = [(pose(bob=b), IDLE_MS) for b in BREATH]
    out["run"] = [(run_frame(i), RUN_MS) for i in range(8)]
    out["attack"] = [(pose("back", dx=-2), 90), (pose("up", dx=-2), 90), (pose("point", dx=2), 100),
                     (pose("point", dx=2), 100), (pose(), 87)]
    out["skill"] = [(pose("back", dx=-2), 60), (pose("point", dx=2), 80), (pose("point", dx=2), 100), (pose(), 93)]
    out["skill_w"] = [(pose("up", lift=3), 60), (pose("up", lift=6), 80), (pose("up", lift=3), 80), (pose(bob=2), 80)]
    out["skill_e"] = [(pose("up", lift=2), 70), (pose("point", lift=2, dx=2), 90), (pose("point", dx=2), 80),
                      (pose(), 60)]
    out["ult"] = [(pose("up"), 100), (pose("up", sink=4), 120), (pose("up", sink=8), 130), (pose("back", sink=8), 130),
                  (pose("point", sink=8, dx=2), 120)]
    out["hit"] = [(shift(pose(), -4, 0), 90), (shift(pose(), -2, 0), 120)]
    # the collapse: thrown back, the near knee going out as she sinks into her skirt, the head dropping, the eyes shut
    d5 = shut_eyes(pose(sink=21, dx=-2, splay=6, bow=(2, 3)))
    out["dead"] = [(shift(pose("back"), -3, 0), 120), (pose("back", sink=4, dx=-3, splay=2), 120),
                   (pose("rest", sink=10, dx=-2, splay=3), 140), (pose(sink=16, dx=-2, splay=4, bow=(1, 2)), 160),
                   (d5, 200), (d5.copy(), 400)]
    done = {t: [(tidy(a), ms) for a, ms in out[t]] for t in ORDER}
    # the hit's flash after the finish (flashed, the outline is light and the finish ringed it again, closing gaps)
    done["hit"][0] = (flash(done["hit"][0][0]), done["hit"][0][1])
    return done


# ------------------------------------------------------------------------------------------------- finishing
HOLE_FILL = 8
SPECK = 5


def tidy(a):
    out = G.complete_outline(a, color=OUTLINE, feet=SOLE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > HOLE_FILL:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < SPECK:
                out[lbl == k] = 0
    return out


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
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot). The pivot: the pivot
    column, FEET 1x rows above the ground line."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh))[0]
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


# ------------------------------------------------------------------------------------------------- review
def review(acts, out_dir, z=8, zg=3):
    os.makedirs(out_dir, exist_ok=True)
    allc = np.concatenate([np.stack([f for f, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, SOLE + 3, xs.min() - 2, xs.max() + 3
    for tag, fr in acts.items():
        tiles = []
        for f, _ in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB"))
        sheet = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 6), (y1 - y0) * z), (60, 60, 60))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST), (i * ((x1 - x0) * z + 6), 0))
        sheet.save(os.path.join(out_dir, f"orianna_{tag}.png"))
        small = [t.resize(((x1 - x0) * zg, (y1 - y0) * zg), Image.NEAREST) for t in tiles]
        q = [t.quantize(255, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"orianna_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="every tag's frames at 8x and a 3x GIF here (nothing written to the repo)")
    a = ap.parse_args()
    acts = frames()
    if a.review:
        review(acts, a.review)
        return
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
        with open(lp(os.path.join(ORIG, f"orianna_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_orianna#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
