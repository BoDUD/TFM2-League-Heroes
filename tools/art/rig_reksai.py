#!/usr/bin/env python3
"""league_reksai's action frames posed from the approved designs' own squares (no Codex strips: the user, 2026-10-17,
「动作帧你就参考塔姆那样做吧 不用交给codex 做完美了喊我review」 - tools/art/rig_tahmkench.py / rig_rell.py's way).

    python tools/art/rig_reksai.py --review DIR      # every tag on the canvas, 6x sheets + a 3x GIF per tag
    python tools/art/rig_reksai.py                   # the frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero reksai && python tools/art/ppu_hd.py --hero reksai

The designs (tools/art/design_reksai.py: Codex's step-1 takes read back square for square, nothing cut):
  A = the surface idle (hd/design_A.png, 70 x 57 squares, crest top to claw tips 36 game px -> PPU 57 / 36 = 1.58);
  B = burrowed (hd/design_B.png, 52 x 33, the crest, the upper back and the helmet's top out of a dirt heap, A's scale).
Both are posed at their own density (the frames ARE at PPU, nothing is resampled) and only losslessly (memory
no-deformation-lossless-poses): whole-part moves, row shifts of the legs (the leg's rows slide from its top's offset to
its claws' offset, every row whole), layering (the body over the legs' tops, the dirt over B's body), clipping at the
ground (sinking into it - she is a burrower). New squares: only the open mouth (tools/art/rig_tahmkench.py's way): the
lower jaw dropped `d` rows under the upper fangs, the gap the mouth's own dark magenta between the lips, the cheek's row
above the mouth line repeated beside them.
Parts of A (square ranges, design_A's own columns / rows): four legs below the body (hf far hind 12-20, hn near hind 22-28,
fn the planted middle leg with the blade plate's claws 29-46, ff the front claws under the head 52-69); the lower jaw
(rows MOUTH-JAW_BOT, columns >= JAW_X); the rest is the body. B: the dirt (warm browns and the dark squares touching them,
rows >= 20) and the body (the rest).
Actions (League's clips for the beats: RekSai_idle01, run, attack1, spell1, spell1_burrowed, Spell3, Spell2_unburrow,
Spell4_cast / Spell4_hit, death, idle01_burrowed, run_burrowed):
  idle 8      breathing: the body sinks 0-2 rows over the standing legs, the mouth opens a row at the deepest
  run 8       on all fours: the diagonal pairs (fn + hf, ff + hn) swing half a cycle apart, lifted while they come
              forward, the body bobbing a row
  attack 5    the bite-swipe: drawn back, the lunge with the mouth open, the snap (frame 3), back
  skill 5     Queen's Wrath: crouch, a hop with the mouth open and the front claws reaching, the slam (frame 3), back
  skill_q2 5  Prey Seeker: she dips into the ground, the shot leaves with the mouth open (frame 3), up again
  bite 5      Furious Bite: a hop back with the mouth wide, the lunge and the snap (frame 3), back
  skill2 6    Burrow: crouch, into the ground head first, then B (the mound) bobbing while she tunnels
  skill2_up 5 Unburrow: out of the ground into the air (the knock-up), down, crouch, stand
  ult 6       Void Rush: crouch, into the ground, B held while she is untargetable
  ult_hit 5   the lunge: out of the ground, the leap with the mouth wide, the strike, the landing
  hit 2       moved back with a white flash
  dead 6      League's death digs her into the ground: a flinch, a crouch, down head first, the dirt heap left
  b_idle 8    (the add-on's burrowed body) B: the back sinks 0-2 rows into the heap
  b_run 8     B moving: the back bobs into the heap, the crest leaning a column
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
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile: long paths
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "reksai")
STEM = os.path.join(ROOT, "league", "champions", "league_reksai")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
GAME_ROWS = 36                    # the user's pick: crest top to claw tips
FEET = 11                         # 1x rows from the pivot down to the ground row
ORDER = ["idle", "run", "attack", "skill", "skill_q2", "bite", "skill2", "skill2_up", "ult", "ult_hit", "hit", "dead",
         "b_idle", "b_run", "b_hit", "t_dig", "t_dig_l", "t_up", "t_up_l"]


def load(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


A0 = load(os.path.join(SRC, "hd", "design_A.png"))
AH, AW = A0.shape[:2]                                 # 57 x 70
PPU = round(AH / GAME_ROWS, 2)                        # 1.58
A_OP = A0[..., 3] > 0
B0 = load(os.path.join(SRC, "hd", "design_B.png"))
BH, BW = B0.shape[:2]                                 # 33 x 52
B_OP = B0[..., 3] > 0
OUTLINE = tuple(int(v) for v in A0[A_OP][np.argmin(A0[A_OP][:, :3].astype(int).sum(1)), :3])


def box(a_op, r0, r1, c0, c1):
    m = np.zeros(a_op.shape, bool)
    m[r0:r1 + 1, c0:c1 + 1] = True
    return m & a_op


# ------------------------------------------------------------------------------------------------- A's parts
# (rows from, columns from-to): each leg's own squares below the body; its rows slide (see leg())
LEG_SPEC = {"hf": (43, 12, 20), "hn": (45, 22, 28), "fn": (46, 29, 46), "ff": (46, 52, 69)}
LEGS = {k: box(A_OP, r, AH - 1, c0, c1) for k, (r, c0, c1) in LEG_SPEC.items()}
LEG_ORDER = ["hf", "hn", "ff", "fn"]                  # drawn first to last (the near middle leg in front)
ALL_LEGS = np.logical_or.reduce(list(LEGS.values()))
BODY = A_OP & ~ALL_LEGS
FEET_MID = 37                                         # the planted leg's middle: the pivot column
# the mouth: the lower jaw (rows MOUTH..JAW_BOT, columns >= JAW_X: the chin plate, both tusks, the cheek's lower rows)
# drops `d` rows to open it, the upper fangs stay; the gap between the lips (columns LIP0-LIP1, the outline on both
# edges) is the mouth's own dark magenta, beside them (the cheek) the row above the mouth line repeated
JAW_X, MOUTH, JAW_BOT = 53, 37, 45
LIP0, LIP1 = 59, 65
MOUTH_IN = (97, 6, 74)                                # design_A's own darkest magenta (the mouth's inside)
assert any(tuple(int(v) for v in c) == MOUTH_IN for c in A0[A_OP][:, :3]), "the mouth colour is not design_A's"

# ------------------------------------------------------------------------------------------------- B's parts
_rgb = B0[..., :3].astype(int)
_warm = B_OP & (_rgb[..., 0] > _rgb[..., 1]) & (_rgb[..., 1] > _rgb[..., 2]) & (_rgb[..., 0] - _rgb[..., 2] > 30) \
    & (np.arange(BH)[:, None] >= 20)
_dark = B_OP & (_rgb.sum(-1) < 90)
DIRT = _warm | (ndimage.binary_dilation(_warm, structure=np.ones((3, 3))) & _dark)
DIRT |= box(B_OP, 30, BH - 1, 0, BW - 1)             # the heap's bottom rows whole
B_BODY = B_OP & ~DIRT
A_CREST_X = int(np.nonzero(A_OP[0])[0].min())         # the crest's top square, A
B_CREST_X = int(np.nonzero(B_OP[0])[0].min())         # and B (B is placed so the two coincide)

# ------------------------------------------------------------------------------------------------- the canvas
CW, CH = 170, 100
GY = 90                                               # the ground line: the first row under the claws
PX = 85                                               # the pivot column
AX0, AY0 = PX - FEET_MID, GY - AH
BX0, BY0 = AX0 + A_CREST_X - B_CREST_X, GY - BH


def blank():
    return np.zeros((CH, CW, 4), np.uint8)


def put(dst, src, m, dx, dy):
    ys, xs = np.nonzero(m)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    dst[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]


def leg(dst, name, top_dx, foot_dx, lift, y0):
    """A leg from its own squares: each row slid from top_dx (its first row, under the body) to foot_dx (its last
    row), whole rows; the leg `lift` rows up (its top goes up under the body)."""
    m = LEGS[name]
    ys, xs = np.nonzero(m)
    r0, r1 = ys.min(), ys.max()
    t = (ys - r0) / max(1, r1 - r0)
    k = np.round(top_dx + (foot_dx - top_dx) * t).astype(int)
    ty, tx = y0 + ys - lift, AX0 + xs + k
    ok = (ty >= 0) & (ty < CH) & (tx >= 0) & (tx < CW)
    dst[ty[ok], tx[ok]] = A0[ys[ok], xs[ok]]


def open_mouth(src, d):
    """design_A's body with the lower jaw dropped d rows (the same size: the jaw drops over the front claws)."""
    if d <= 0:
        return src
    out = src.copy()
    jaw = np.zeros((AH, AW), bool)
    jaw[MOUTH:JAW_BOT + 1, JAW_X:] = True
    jaw &= src[..., 3] > 0
    jy, jx = np.nonzero(jaw)
    out[jy, jx] = 0
    out[jy + d, jx] = src[jy, jx]
    for x in range(JAW_X, AW):
        above, top = src[MOUTH - 1, x], src[MOUTH, x]
        if not (above[3] and top[3]):
            continue
        for i in range(d):
            if LIP0 < x < LIP1:
                out[MOUTH + i, x] = (*MOUTH_IN, 255)
            elif x in (LIP0, LIP1):
                out[MOUTH + i, x] = (*OUTLINE, 255)
            else:
                out[MOUTH + i, x] = above
    return out


HEAP_UNDER = 3                                        # sunk this deep (or deeper), the dirt heap is round her
DEEP = 20                                             # this deep, what sticks out beside the heap (the tail) is under too


def pose_a(dx=0, sink=0, lift=0, mouth=0, legs=None, under=0, hide=()):
    """A on the canvas: the body (with the head) dx forward, `sink` rows down over the legs, everything `lift` rows up;
    legs: {leg: (top dx, foot dx, lift)} (missing: (dx, 0, 0) - the top follows the body, the claws stay); `under`
    rows of A sunk into the ground (the whole figure moved down and cut at the ground line); hide: legs left out (the
    attack draws the far front claw on an arm of its own - swipe())."""
    can = blank()
    legs = legs or {}
    y_legs = AY0 + under - lift
    for name in LEG_ORDER:
        if name in hide:
            continue
        tdx, fdx, ll = legs.get(name, (dx, 0, 0))
        leg(can, name, tdx, fdx, ll, y_legs)
    src = open_mouth(np.where(BODY[..., None], A0, 0).astype(np.uint8), mouth)
    put(can, src, src[..., 3] > 0, AX0 + dx, AY0 + sink + under - lift)
    if under >= DEEP:                                 # deep down only what is inside the heap is still out
        cols = np.nonzero(DIRT.any(0))[0]
        can[:, :BX0 + dx + cols.min()] = 0
        can[:, BX0 + dx + cols.max() + 1:] = 0
    if under >= HEAP_UNDER:                           # digging in / out: B's heap round her (over her); in its
        heap = blank()                                # columns she shows only above its top
        put(heap, B0, DIRT, BX0 + dx, BY0)
        op = heap[..., 3] > 0
        cols = np.nonzero(op.any(0))[0]
        tops = {x: np.nonzero(op[:, x])[0].min() for x in cols}
        for x in range(CW):                           # beside the heap its slope goes on (2 rows a column) into the ground
            if x in tops:
                can[tops[x]:, x] = 0
            else:
                edge = cols.min() if x < cols.min() else cols.max()
                can[min(GY, tops[edge] + 2 * abs(x - edge)):, x] = 0
        m = heap[..., 3] > 0
        can[m] = heap[m]
    can[GY:] = 0
    return can


def pose_b(dx=0, sink=0, lean=0):
    """B on the canvas: its body `sink` rows down into the heap (the dirt drawn over it), the crest's top `lean` columns
    forward (the body's rows above the heap slid, 0 at the heap's top row), all dx forward."""
    can = blank()
    ys, xs = np.nonzero(B_BODY)
    t = np.clip((20 - ys) / 20.0, 0, 1)
    k = np.round(lean * t).astype(int)
    ty, tx = BY0 + ys + sink, BX0 + dx + xs + k
    ok = (ty >= 0) & (ty < GY) & (tx >= 0) & (tx < CW)
    can[ty[ok], tx[ok]] = B0[ys[ok], xs[ok]]
    put(can, B0, DIRT, BX0 + dx, BY0)
    can[GY:] = 0
    return can


def pose_heap(dx=0):
    """B's dirt heap alone (she has gone under): what her death leaves."""
    can = blank()
    put(can, B0, DIRT, BX0 + dx, BY0)
    can[GY:] = 0
    return can


def shift(a, dx, dy):
    out = np.zeros_like(a)
    ys, xs = np.nonzero(a[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < a.shape[0]) & (tx >= 0) & (tx < a.shape[1]) & (ty < GY)
    out[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
    return out


def flash(a, k=0.55):
    out = a.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- the claw swipe
# League's RekSai_attack1 / attack2: she rears and brings a front claw down on the target - her design's front "hands"
# are only claws under the head, so the far front claw (LEGS["ff"], carried whole: mirrored or turned a quarter) is set
# on an arm drawn from her own limb colours (league_caitlyn's / league_aphelios's thin-limb way) from the shoulder
ARM_COLS = ((30, 10, 30), (67, 32, 55), (105, 51, 79))   # design_A's dark limb under the head: shade, mid, light
SHOULDER = (34, 47)                                      # design square (row, column) where the far front limb starts


def limb(can, p0, p1, width, behind):
    """An arm from canvas square p0 to p1 ((x, y)): ARM_COLS lit on its upper side, outlined; behind: only where the
    canvas is empty (behind the body)."""
    (x0, y0), (x1, y1) = p0, p1
    ys, xs = np.mgrid[0:CH, 0:CW]
    dx, dy = x1 - x0, y1 - y0
    L2 = max(1e-6, dx * dx + dy * dy)
    t = np.clip(((xs + 0.5 - x0) * dx + (ys + 0.5 - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.hypot(xs + 0.5 - px, ys + 0.5 - py)
    side = (xs + 0.5 - x0) * dy - (ys + 0.5 - y0) * dx          # > 0: below / behind the bone
    inside = d <= width / 2.0
    ring = ndimage.binary_dilation(inside, structure=np.ones((3, 3))) & ~inside
    out = can.copy()
    free = can[..., 3] == 0 if behind else np.ones((CH, CW), bool)
    for m, c in ((inside & (side > 0) & (d > width * 0.2), ARM_COLS[0]), (inside & (np.abs(side) <= 0) | (inside & (d <= width * 0.2)), ARM_COLS[1]),
                 (inside & (side < 0) & (d > width * 0.2), ARM_COLS[2])):
        m = m & free
        out[m] = (*c, 255)
    m = ring & free & (out[..., 3] == 0)
    out[m] = (*OUTLINE, 255)
    return out


def claw_piece(how):
    """LEGS["ff"]'s squares cut to their box: "up" mirrored top to bottom (the claws up), "fwd" a quarter turn
    counter-clockwise (the root left, the claws forward), "down" as drawn."""
    ys, xs = np.nonzero(LEGS["ff"])
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = A0[ys, xs]
    return {"up": sub[::-1], "fwd": np.rot90(sub, 1), "down": sub}[how].copy()


def swipe(dx, sink, hand, how, behind, mouth=0, width=4):
    """A frame of the swipe: the body (dx, sink) without the far front claw, the arm from SHOULDER to `hand` (design
    square (row, column) of the posed body) and the claw there (its root on the hand), behind the body or in front."""
    can = pose_a(dx=dx, sink=sink, mouth=mouth, hide=("ff",))
    bx, by = AX0 + dx, AY0 + sink
    s = (bx + SHOULDER[1] + 0.5, by + SHOULDER[0] + 0.5)
    h = (bx + hand[1] + 0.5, by + hand[0] + 0.5)
    can = limb(can, s, h, width, behind)
    pc = claw_piece(how)
    ph, pw = pc.shape[:2]
    hx, hy = int(round(h[0])), int(round(h[1]))
    x0, y0 = {"up": (hx - pw // 2, hy - ph + 1), "fwd": (hx, hy - ph // 2), "down": (hx - pw // 2, hy)}[how]
    m = pc[..., 3] > 0
    if behind:
        sub = np.zeros_like(can)
        put(sub, pc, m, x0, y0)
        m2 = (sub[..., 3] > 0) & (can[..., 3] == 0)
        can[m2] = sub[m2]
    else:
        put(can, pc, m, x0, y0)
    can[GY:] = 0
    return can


# ------------------------------------------------------------------------------------------------- the run
RUN_MS = 90
RUN_SWING = 4                                         # squares each way (6 tried in the 2026-10-19 frame audit: the
                                                      # front leg slanted into a thin line - a sheared leg)
RUN_LIFT = 2


def run_frame(i):
    """Phase i of 8: pair 1 (fn, hf) and pair 2 (ff, hn) half a cycle apart; a foot comes forward lifted, goes back
    planted; the body a row down while both pairs are planted (the push)."""
    legs = {}
    for names, ph in ((("fn", "hf"), i), (("ff", "hn"), i + 4)):
        a = 2 * np.pi * (ph % 8) / 8
        fdx = int(round(-RUN_SWING * np.cos(a)))
        lift = int(round(max(0.0, np.sin(a)) * RUN_LIFT))
        for nm in names:
            far = nm in ("hf", "hn")
            legs[nm] = (0, int(round(fdx * (0.7 if far else 1))), lift)
    sink = [0, 1, 1, 0, 0, 1, 1, 0][i]
    return pose_a(sink=sink, legs=legs)


# ------------------------------------------------------------------------------------------------- actions
IDLE_MS = 150


def frames():
    out = {}
    breath = [0, 0, 1, 1, 2, 2, 1, 1]
    out["idle"] = [(pose_a(sink=b, mouth=1 if b == 2 else 0), IDLE_MS) for b in breath]
    out["run"] = [(run_frame(i), RUN_MS) for i in range(8)]
    # the bite-swipe: the kit's hit on tick 11 = 183 ms -> frame 3 (from 180 ms)
    # the claw swipe (League's RekSai_attack1 / attack2; the user, 2026-10-19: 「雷克塞普攻是不是用手的？」 - the strip
    # was a lunge with the jaw open, E's bite): the far front claw raised over her head behind the crest, higher, brought
    # down in front of her face onto the target (frame 3, the hit), planted, back
    out["attack"] = [(swipe(-2, 1, (16, 60), "up", True, width=6), 90), (swipe(-3, 0, (8, 58), "up", True, width=6), 80),
                     (swipe(4, 1, (44, 77), "down", True, mouth=1, width=6), 100),
                     (swipe(4, 2, (47, 75), "down", True, width=6), 70), (pose_a(dx=2), 50), (pose_a(), 43)]
    # Queen's Wrath (League's spell1 leaps; a hop here, nothing pitched): crouch, the hop with the mouth open and the front
    # claws reaching, the slam forward (q_hit tick 10 = 167 ms -> frame 3), back
    out["skill"] = [(pose_a(dx=-1, sink=2), 100),
                    (pose_a(dx=2, lift=4, mouth=2, legs={"ff": (2, 5, 0), "fn": (2, 2, 0)}), 67),
                    (pose_a(dx=4, sink=1, legs={"ff": (4, 6, 0), "fn": (4, 2, 0)}), 100),
                    (pose_a(dx=2, legs={"ff": (2, 2, 0)}), 80), (pose_a(), 53)]
    # Prey Seeker: q2_at tick 8 = 133 ms -> frame 3
    out["skill_q2"] = [(pose_a(under=3), 67), (pose_a(under=8), 66), (pose_a(dx=1, under=8, mouth=2), 100),
                       (pose_a(under=4), 67), (pose_a(sink=1), 67)]
    # Furious Bite (League's Spell3 rears up and dives at the target): a hop back with the mouth wide, the lunge, the snap
    # (e_hit tick 12 = 200 ms -> frame 3), back
    out["bite"] = [(pose_a(dx=-2, lift=3, mouth=3), 100), (pose_a(dx=3, lift=1, mouth=3, legs={"ff": (3, 3, 0)}), 100),
                   (pose_a(dx=5, sink=1, legs={"ff": (5, 4, 0)}), 100), (pose_a(dx=3, legs={"ff": (3, 2, 0)}), 100),
                   (pose_a(), 67)]
    # Burrow: into the ground by the dash's start (w_go tick 7 = 117 ms), then the mound while she tunnels
    out["skill2"] = [(pose_a(sink=2), 67), (pose_a(dx=1, under=12), 50), (pose_a(dx=2, under=26), 50),
                     (pose_b(dx=2, sink=1), 100), (pose_b(dx=2, lean=1), 100), (pose_b(dx=2, sink=1), 100)]
    # Unburrow (played on arrival): out of the ground into the air, down
    out["skill2_up"] = [(pose_a(under=14), 50), (pose_a(lift=6, mouth=2), 67), (pose_a(lift=3, mouth=1), 83),
                        (pose_a(sink=2), 67), (pose_a(), 66)]
    # Void Rush: under for r_hide (54 ticks = 900 ms)
    out["ult"] = [(pose_a(sink=2), 100), (pose_a(dx=1, under=12), 67), (pose_a(dx=2, under=26), 67),
                  (pose_b(dx=2, sink=1), 222), (pose_b(dx=2, sink=2, lean=1), 222), (pose_b(dx=2, sink=1), 222)]
    out["ult_hit"] = [(pose_a(dx=-2, under=12), 67), (pose_a(dx=1, lift=8, mouth=3, legs={"ff": (1, 3, 2)}), 83),
                      (pose_a(dx=4, lift=4, mouth=3, legs={"ff": (4, 6, 2)}), 100),
                      (pose_a(dx=4, sink=2, legs={"ff": (4, 4, 0)}), 100), (pose_a(dx=1), 150)]
    out["hit"] = [(shift(pose_a(), -2, 0), 90), (shift(pose_a(), -1, 0), 120)]
    # death: League's RekSai_death digs her into the ground - a flinch, a crouch, down head first, the heap left
    heap = pose_heap()
    # (8 frames since the 2026-10-19 frame audit: two more steps of the dig)
    out["dead"] = [(shift(pose_a(), -2, 0), 120), (pose_a(dx=-1, sink=2, mouth=1), 110), (pose_a(under=7), 80),
                   (pose_a(under=14), 90), (pose_a(under=22), 80), (pose_a(under=30), 100), (heap, 300),
                   (heap.copy(), 400)]
    out["b_idle"] = [(pose_b(sink=s), IDLE_MS) for s in breath]
    out["b_run"] = [(pose_b(sink=s, lean=ln), RUN_MS) for s, ln in
                    zip([0, 1, 2, 1, 0, 1, 2, 1], [0, 1, 1, 0, 0, 1, 1, 0])]
    # hit while burrowed (the add-on plays it for `hit` under the ground: the hit showed her out of it)
    out["b_hit"] = [(shift(pose_b(), -2, 0), 90), (shift(pose_b(), -1, 0), 120)]
    # the add-on's tunnels (addons/league_reksai plays these as one-off pictures where she goes in and comes out, while
    # it keeps her banished - her own frames, drawn dense by league.dll like her; League's Spell3_burrowed): into the
    # ground (Burrow's first three frames), out of it (Unburrow), each also mirrored about the pivot for a tunnel run
    # leftward (the client never mirrors a picture)
    out["t_dig"] = out["skill2"][:3]
    out["t_up"] = list(out["skill2_up"])
    done = {t: [(tidy(a), ms) for a, ms in out[t]] for t in ORDER if t in out}
    for t in ("t_dig", "t_up"):
        done[t + "_l"] = [(mirrored(a), ms) for a, ms in done[t]]
    for t in ("hit", "b_hit"):
        done[t][0] = (flash(done[t][0][0]), done[t][0][1])
    return {t: done[t] for t in ORDER}


def mirrored(a):
    """The frame turned left to right about the pivot column (its squares carried whole)."""
    out = np.zeros_like(a)
    xs = np.arange(CW)
    src = 2 * PX - xs
    ok = (src >= 0) & (src < CW)
    out[:, xs[ok]] = a[:, src[ok]]
    return out


# ------------------------------------------------------------------------------------------------- finishing
HOLE_FILL = 6
SPECK = 4


def tidy(a):
    out = G.complete_outline(a, color=OUTLINE, feet=GY - 1)[0]
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


CORNER = (PX + 0.5, GY)


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


def strip_of(frames_):
    H = max(h.shape[0] for h in frames_)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames_) - 1, 4), np.uint8)
    x = 0
    for h in frames_:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


# ------------------------------------------------------------------------------------------------- review
def review(acts, out_dir, z=6, zg=3):
    os.makedirs(out_dir, exist_ok=True)
    allc = np.concatenate([np.stack([f for f, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, GY + 3, xs.min() - 2, xs.max() + 3
    for tag, fr in acts.items():
        tiles = []
        for f, _ in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB"))
        sheet = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 6), (y1 - y0) * z), (60, 60, 60))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST), (i * ((x1 - x0) * z + 6), 0))
        sheet.save(os.path.join(out_dir, f"reksai_{tag}.png"))
        small = [t.resize(((x1 - x0) * zg, (y1 - y0) * zg), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"reksai_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


def check():
    """The standing frame must be design_A square for square; B's standing frame design_B."""
    for name, f, want in (("A", tidy(pose_a()), A0), ("B", tidy(pose_b()), B0)):
        ys, xs = np.nonzero(f[..., 3] > 0)
        got = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        same = got.shape == want.shape and np.array_equal(got, want)
        diff = None if got.shape != want.shape else int((np.any(got != want, -1)).sum())
        print(f"standing {name} == design_{name}:", same, "shape", got.shape, want.shape, "squares differing", diff)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="every tag's frames at 6x and a 3x GIF here (nothing written to the repo)")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
        return
    acts = frames()
    if a.review:
        review(acts, a.review)
        return
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag, frs in acts.items():
        ones, hds = [], []
        for can, t in frs:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"reksai_{tag}.png"))
        with open(os.path.join(ORIG, f"reksai_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_reksai#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
