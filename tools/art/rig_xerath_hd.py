#!/usr/bin/env python3
"""league_xerath re-adjusted at PPU (the user, 2026-10-21: 「帮我使用PPU优化泽拉斯模型 大招动作帧之类的和英雄联盟都不一样」
「不是重做 是重新调整」「好好做吧 别身体变形各种奇怪的问题」): the design of tools/art/design_xerath_hd.py (35 x 62 squares:
the slimmer take, shortened - 「泽拉斯在游戏里身体太长了吧？」 -> take C) posed after League's own clips, every part only moved
losslessly - whole squares and quarter turns about its joint, never redrawn, never sheared.

    python tools/art/rig_xerath_hd.py --parts DIR        # the parts tinted, to check the cut
    python tools/art/rig_xerath_hd.py --review DIR       # every tag at 3x + GIFs (ppu_rig.Rig.review)
    python tools/art/rig_xerath_hd.py                    # orig strips + the 1x sheet (then ppu_restyle, ppu_hd)
    python tools/art/review_xerath_actions.py --out DIR  # every tag beside League's frames, one GIF

Parts (design squares): the two floating claws (the cyan-to-navy squares under the pauldrons and the outline round
them), the two pauldrons, the hood, the two legs (each an upper plate and a lower spike) and the body; for the ult and
the death the body comes apart too (SPLIT: the purple plates of the chest and the hips off the energy core - the cyan
body, the chains and the gem). He floats: his spike tips hang HOVER squares over the ground line.

A lean (LEAN) moves the hood, the body and the legs by whole columns, at most one column between neighbours (hood /
chest / hip plate / spike): a step of two read as a broken neck or knee, and the user asked for little tilt on the 1x
(「倾斜不要太大」).

What League plays (tools/lol/pose_ref.py --champ Xerath; review_xerath_actions.LOL has the moment of each frame):
  idle      Idle1: a slow bob, the claws a beat behind the body;
  run       run: leant into the glide, the legs swaying in turn, the claws swept back;
  attack    Attack1: leans back with the far claw raised over his shoulder, then leans in and flings it forward level
            (a_flash at 183 ms sits on its tips);
  skill     Q = channel_windup (both claws thrown up, a V, leaning back) + channel (hunched forward, both claws held
  / _quick  ahead at face height, the far one over the near one: q_charge glows between them) + Spell1 (a lunge, both
            claws thrust forward: q_fire at 900 / 367 ms);
  skill2    E -> W = Spell3 (leans back with the far claw raised, then leans in and flings it: e_cast at 183 ms) and
            Spell2 (both claws up, then drawn in to the chest);
  ult       R = Spell5Start: he curls up (bows, the claws to his chest, the shins folded forward), stretches out with
            the claws up, and his armour starts to fly off;
  ult_loop  Spell5Loop: every plate of his armour - hood, pauldrons, chest and hip plates, the legs - floats in a wide
            ring round the energy core, the claws out at his sides, each piece circling a square on its own beat;
  ult_shot  a shot inside the ring: the far claw thrust ahead under the rising bolt (r_cast_shot at 0 ms);
  hit       a recoil, the claws flung out;
  dead      Death: he rises arching back with the claws up, bursts apart in the air, and the plates lie scattered on
            the ground - the energy core gone.
The tags, frame counts and ms are the sheet's (the kit's timing); the tags the bake lays a picture into are posed on
their frames before the split (assets/source/native/xerath_cells.json), Rig.bake lays the effects in and makes the
_fx copies.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "xerath"
DESIGN = os.path.join(R.ROOT, "assets", "source", HERO, "hd", "design.png")
PPU = 1.55                                   # squares a game pixel: 62 design rows = 40 game px crown to spike tips
                                             # (the 1x was 44: 「游戏里别太大就行」; 73 rows at 1.75 read as stretched)
HOVER = 2                                    # squares between the spike tips and the ground line
DARK = 30.0                                  # luma under which a square is outline

# cuts and joints (design squares; a joint is a square edge point)
L_SHOULDER, R_SHOULDER = (6.0, 27.0), (31.0, 27.0)
CLAW_ROWS = 26                               # the claws hang from this row down
CLAW_COLS = (11, 26)                         # the near claw in columns up to 11, the far one from 26
HOOD_ROWS, HOOD_COLS = 12, (7, 28)           # the hood: every square above row 12, rows 12-14 in columns 7..27
NECK_ROW = 15
PADS = {"lpad": (12, 31, 0, 12), "rpad": (12, 31, 26, 35)}
LEG_TOP, LEG_KNEE, LEG_SPLIT = 41, 51, 19    # the legs from row 41; the plate / spike break; left / right columns
GEM = (22, 29, 17, 23)                       # rows, columns of the gem's setting (stays on the core)
CHEST_TOP, CHEST_HIP = 22, 34               # the chest plates in these rows (above, the thin bits by the collar stay on
                                             # the core: flown, they broke into specks), the hip plates below


def lp(path):
    return R.lp(path)


def classes(d):
    op = d[..., 3] > 0
    r, g, b = (d[..., i].astype(int) for i in range(3))
    lum = r * 0.299 + g * 0.587 + b * 0.114
    dark = op & (lum < DARK)
    blue = op & (r < 60) & ((b >= 80) | ((g >= 40) & (b >= 40)))
    grey = op & ~dark & (abs(r - g) < 30) & (abs(g - b) < 30)
    orange = op & (r > 150) & (b < 100)
    purple = op & ~dark & ~blue & ~grey & ~orange
    return op, dark, blue, purple


class Design:
    """The design as ppu_rig.Rig wants it (W, H, px, ground, ppu, outline, hero) and its parts."""

    def __init__(self):
        d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA")).copy()
        self.d = self.d0 = d
        self.hero = HERO
        self.H, self.W = d.shape[:2]
        op, dark, blue, purple = classes(d)
        lum = (d[..., :3].astype(float) * [0.299, 0.587, 0.114]).sum(2)
        self.outline = tuple(int(v) for v in d[dark][np.argmin(lum[dark])][:3])
        tips = [max(np.nonzero(op[:, c0:c1].any(1))[0]) for c0, c1 in ((0, LEG_SPLIT), (LEG_SPLIT, self.W))]
        self.ground = max(tips) + 1 + HOVER
        self.ppu = PPU
        self.px = float(np.mean([np.nonzero(op[t, c0:c1])[0].mean() + c0 + 0.5
                                 for t, (c0, c1) in zip(tips, ((0, LEG_SPLIT), (LEG_SPLIT, self.W)))]))
        self.parts = {}
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        taken = np.zeros_like(op)

        def grab(name, core, area, into=None):
            """core squares and the outline squares touching them inside area."""
            near = np.zeros_like(op)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    near |= np.roll(np.roll(core, dy, 0), dx, 1)
            m = (core | (near & dark)) & area & ~taken
            (self.parts if into is None else into)[name] = m
            taken[:] |= m

        for name, side in (("lclaw", xx <= CLAW_COLS[0]), ("rclaw", xx >= CLAW_COLS[1])):
            area = side & (yy >= CLAW_ROWS) & (yy < LEG_TOP + 3)
            grab(name, blue & area, area)
        area = (yy < HOOD_ROWS) | ((yy < NECK_ROW) & (xx >= HOOD_COLS[0]) & (xx < HOOD_COLS[1]))
        grab("head", op & area, area)
        for name, (r0, r1, c0, c1) in PADS.items():
            area = (yy >= r0) & (yy < r1) & (xx >= c0) & (xx < c1)
            grab(name, op & area, area)
            # a pauldron square that touches no other square of its pauldron side by side hangs off the claw under
            # it (the shortened design's dark purple at the far pauldron's foot): it goes with that claw - left on
            # the pauldron it floated alone when the claw was flung
            pad = self.parts[name]
            sides = sum(np.roll(pad, s, a) for s in (1, -1) for a in (0, 1))
            claw = self.parts["lclaw" if name == "lpad" else "rclaw"]
            near = sum(np.roll(claw, s, a) for s in (1, -1) for a in (0, 1)) > 0
            hang = pad & (sides == 0) & near
            self.parts[name] = pad & ~hang
            self.parts["lclaw" if name == "lpad" else "rclaw"] = claw | hang
        for side, cols in (("l", xx < LEG_SPLIT), ("r", xx >= LEG_SPLIT)):
            area = cols & (yy >= LEG_TOP) & (yy < LEG_KNEE)
            grab(side + "plate", op & area, area)
            area = cols & (yy >= LEG_KNEE)
            grab(side + "spike", op & area, area)
        body = op & ~taken
        self.parts["body"] = body
        # the body's own plates, off the core only in the ult and the death (frame(split=True))
        r0, r1, c0, c1 = GEM
        gem = (yy >= r0) & (yy < r1) & (xx >= c0) & (xx < c1)
        self.split = {}
        chest = (yy >= CHEST_TOP) & (yy < CHEST_HIP)
        for name, area in (("lchest", (xx < LEG_SPLIT) & chest), ("rchest", (xx >= LEG_SPLIT) & chest),
                           ("lhip", (xx < LEG_SPLIT) & (yy >= CHEST_HIP)), ("rhip", (xx >= LEG_SPLIT) & (yy >= CHEST_HIP))):
            grab(name, body & purple & ~gem & area, body & area, into=self.split)
        self.split["core"] = body & ~np.any([m for m in self.split.values()], axis=0)
        # joints: the claws turn about their shoulders, the spikes about their knees (the top row's middle)
        self.joint = {"lclaw": L_SHOULDER, "rclaw": R_SHOULDER}
        for side in "lr":
            m = self.parts[side + "spike"]
            top = np.nonzero(m.any(1))[0].min()
            cols = np.nonzero(m[top])[0]
            self.joint[side + "spike"] = ((cols.min() + cols.max() + 1) / 2, float(top))

    def mask(self, name):
        return self.parts[name] if name in self.parts else self.split[name]

    def layer(self, name):
        out = np.zeros_like(self.d)
        m = self.mask(name)
        out[m] = self.d[m]
        return out


ORDER = ["rclaw", "rpad", "rplate", "rspike", "lplate", "lspike", "body", "head", "lpad", "lclaw"]
SPLIT_ORDER = ["rclaw", "rpad", "rplate", "rspike", "rhip", "rchest", "lplate", "lspike", "core", "lhip", "lchest",
               "head", "lpad", "lclaw"]
GROUP = {"head": "head", "lplate": "plates", "rplate": "plates", "lspike": "spikes", "rspike": "spikes"}
# lean n (+ forward): columns of (the hood, the body with its pauldrons and claws, the hip plates, the spikes)
LEAN = {2: (2, 1, 0, -1), 1: (1, 0, 0, -1), 0: (0, 0, 0, 0), -1: (-1, 0, 0, 1), -2: (-2, -1, 0, 1)}


def frame(rig, pose):
    """pose: {"all": (dx, dy), "lean": n, "split": bool, "back": [parts drawn first], "front": [claws drawn over their
    pauldron], "hide": [...], "flash": [...], part: (dx, dy[, quarter turns ccw about its joint])} -> a canvas. Parts not
    named move with the body; with split the body is the core and its plates."""
    D = rig.D
    can = rig.canvas()
    bx, by = pose.get("all", (0, 0))
    lh, lb, lpl, lsp = LEAN[pose.get("lean", 0)]
    lean = {"head": lh, "plates": lpl, "spikes": lsp}
    order = list(SPLIT_ORDER if pose.get("split") else ORDER)
    for name in pose.get("front", ()):
        order.remove(name)
        order.insert(order.index(name[0] + "pad") + 1, name)
    back = pose.get("back", [])
    for name in back + [n for n in order if n not in back]:
        if name in pose.get("hide", ()):
            continue
        p = pose.get(name, (0, 0))
        dx, dy, rot = (tuple(p) + (0,))[:3]
        dx += bx + lean.get(GROUP.get(name), lb)
        dy += by
        big = rig.canvas()
        lay = D.layer(name)
        if name in pose.get("flash", ()):
            lay = R.flash(lay, 0.6)
        big[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W] = lay
        about = None
        if rot:
            jx, jy = D.joint[name]
            about = (jx + rig.ox, jy + rig.oy)
        R.put(can, big, dx=dx, dy=dy, rot=rot, about=about)
    return can


# ------------------------------------------------------------------------------------------------------- the poses
# claw poses (dx, dy, quarter turns about the shoulder): FWD the far claw level ahead (a throw: its wrist stays under
# the pauldron - pushed further out it floated off the body); UP a claw raised over his shoulder, upside down, drawn in
# front of its pauldron with the wrist over the pauldron's middle (pose "front"): tucked behind the pauldron's top, the
# ground showed between the wrist and the hood and the user saw a broken arm (「怎么有手臂断开？」); UP_L the near one so
# on his other side (a V); HOLD_R the far one pointing ahead at face height (Q's charge on its tips), HOLD_L the near
# one lifted; IN_R / IN_L drawn to the chest
FWD = (1, -2, 1)
UP = (2, -1, 2)
UP_L = (-2, -1, 2)
UP_BACK = (1, -1, 2)                         # UP when leant back two (the hood a column further back)
HOLD_R = (2, -8, 1)
HOLD_L = (2, -5)                             # the near one lifted at his side, unturned: turned across the chest it
                                             # hung off the chest's middle (an arm cut off again) or, from its
                                             # pauldron, ran together with the cyan chest and hid the gem
IN_R, IN_L = (-3, -3), (3, -3)


IDLE_BOB = [0, 0, -1, -1, -2, -2, -1, -1]
IDLE_CLAW = [-1, -1, 0, -1, 0, -1, -2, -1]   # the claws a beat behind the bob, never lower than drawn under their
                                             # pauldrons: one row down opened the ground under the wrist (a cut arm)


def idle(k):
    return {"all": (0, IDLE_BOB[k % 8]), "lclaw": (0, IDLE_CLAW[k % 8]), "rclaw": (0, IDLE_CLAW[k % 8])}


RUN_BOB = [0, -1, -1, 0, 0, -1, -1, 0]
RUN_SWAY = [0, 0, -1, -1, 0, 0, -1, -1]       # a leg (plate and spike together) trailing a column, the two in turn


def run(k):
    sl, sr = RUN_SWAY[k % 8], RUN_SWAY[(k + 2) % 8]
    return {"all": (0, RUN_BOB[k % 8] - 1), "lean": 1, "lplate": (sl, 0), "lspike": (sl, 0), "rplate": (sr, 0),
            "rspike": (sr, 0), "lclaw": (-1, -1 + RUN_SWAY[(k + 4) % 8]), "rclaw": (-1, -1 + RUN_SWAY[k % 8])}


def attack(k):
    return [
        {"lean": -1, "rclaw": (2, -3), "lclaw": (-1, -1)},                                 # the far claw rises
        {"lean": -1, "rclaw": UP, "lclaw": (-1, -2), "front": ["rclaw"]},
        {"lean": -2, "all": (0, -1), "rclaw": (UP_BACK[0], UP_BACK[1] - 1, 2), "lclaw": (-1, -2),
         "front": ["rclaw"]},                                                              # drawn back
        {"lean": 2, "all": (1, 0), "rclaw": FWD, "lclaw": (-2, -2)},                       # flung: a_flash
        {"lean": 2, "all": (1, 0), "rclaw": FWD, "lclaw": (-1, -1)},
        {"lean": 0, "rclaw": (1, -1), "lclaw": (0, -1)},
    ][k]


def q_pose(phase, k=0):
    """Q: 'up' the V (both claws thrown up, leaning back); 'hold' hunched forward, the claws ahead at face height;
    'fire' the lunge, both thrust forward; 'back' recovering."""
    if phase == "up":
        return {"lean": -1, "all": (0, -1 - min(k, 1)), "rclaw": UP, "lclaw": UP_L, "front": ["rclaw", "lclaw"]}
    if phase == "hold":
        b = [0, -1, 0][k % 3]
        return {"lean": 2, "all": (0, b), "rclaw": HOLD_R, "lclaw": HOLD_L}
    if phase == "fire":
        return {"lean": 2, "all": (2, 0), "rclaw": FWD, "lclaw": (2, -3)}
    return {"lean": 1, "rclaw": (1, -1), "lclaw": (0, -1)}


SKILL = [("up", 0), ("up", 1), ("hold", 0), ("hold", 1), ("hold", 2), ("fire", 0), ("back", 0)]
QUICK = [("up", 1), ("hold", 0), ("hold", 1), ("fire", 0), ("back", 0)]


def skill2(k):
    return [
        {"lean": -1, "rclaw": (2, -3), "lclaw": (-1, -1)},                                 # E: leans back, claw up
        {"lean": -2, "all": (0, -1), "rclaw": UP_BACK, "lclaw": (-1, -2), "front": ["rclaw"]},
        {"lean": 2, "all": (1, 0), "rclaw": FWD, "lclaw": (-2, -2)},                       # flung: e_cast
        {"lean": 2, "all": (1, 0), "rclaw": FWD, "lclaw": (-1, -1)},
        {"lean": -1, "all": (0, -1), "rclaw": UP, "lclaw": UP_L, "front": ["rclaw", "lclaw"]},   # W: both up
        {"lean": 0, "rclaw": IN_R, "lclaw": IN_L},                                         # drawn in
    ][k]


# The armour's ring round the core (Spell5Loop), squares from where each piece stands; ORBIT: each piece circles a
# square, one step a frame, on its own beat (PHASE) so the ring never moves as one
RING = {"core": (0, -3), "head": (0, -8), "lpad": (-14, -12), "rpad": (11, -17), "lchest": (-9, -2),
        "rchest": (9, -1), "lhip": (-1, 9), "rhip": (2, 8), "lplate": (-12, 8), "rplate": (14, 7),
        "lspike": (-19, 8, 3), "rspike": (19, 9, 1), "lclaw": (-11, -5), "rclaw": (12, -6)}
# (on the 62-row design the far spike a row higher - turned, the wider spike's tip dipped under the ground line - and
# the far pauldron three columns in and three up: standing a column further out, it sat in r_cast_shot's bolt)
ORBIT = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
PHASE = {"core": 0, "head": 3, "lpad": 1, "rpad": 4, "lchest": 2, "rchest": 5, "lhip": 4, "rhip": 1, "lplate": 5,
         "rplate": 2, "lspike": 0, "rspike": 3, "lclaw": 2, "rclaw": 5}


def ring(t, s=1.0, core_bob=True):
    """The ring at beat t, scaled by s (0 = standing: the start of the burst)."""
    out = {"split": True}
    for name, v in RING.items():
        dx, dy = round(v[0] * s), round(v[1] * s)
        if t is not None and name != "core":
            ox, oy = ORBIT[(t + PHASE[name]) % 6]
            dx, dy = dx + ox, dy + oy
        if name == "core" and t is not None and core_bob:
            dy += [0, 0, -1, -1, 0, 0][t % 6]
        rot = v[2] if len(v) > 2 and s >= 0.5 else 0
        out[name] = (dx, dy, rot)
    return out


# the curl (Spell5Start): a C - the hood bowed forward and down, the spikes a column forward (knees drawn up), the
# claws to the chest; one column between neighbours as a lean (shins folded a quarter turn read as a plank)
CURL = {"head": (1, 1), "lspike": (1, 0), "rspike": (1, 0)}


def ult(k):
    return [
        {"lean": 1, "all": (0, 1), "rclaw": IN_R, "lclaw": IN_L},                          # curls up
        {"all": (0, 1), **CURL, "rclaw": IN_R, "lclaw": (IN_L[0] + 1, IN_L[1] - 1)},
        {"all": (0, 2), **CURL, "rclaw": IN_R, "lclaw": (IN_L[0] + 1, IN_L[1] - 1)},
        {"lean": -1, "all": (0, -2), "rclaw": UP, "lclaw": UP_L, "front": ["rclaw", "lclaw"]},   # stretches out
        ring(None, 0.45),                                                                  # the armour flies off
    ][k]


def ult_shot(k):
    b = ring(0)
    if k < 2:
        b["rclaw"] = (8 + k, 6, 1)                                                         # the bolt rises off it
    return b


def hit(k):
    return [{"lean": -1, "lclaw": (-2, -2), "rclaw": (2, -1)}, {"lean": -1, "lclaw": (-1, -1), "rclaw": (1, -1)}][k]


# the death's scatter on the ground (League's Death from 2.5 s): (piece, quarter turns, column of its middle from the
# pivot, rows up from the ground) - the armour lies where it fell, the long pieces on their side, the spikes further
# back (higher, drawn first); the energy - the core and the claws - is gone (it flashed out in the burst), the chest
# plates under the heap
SCATTER = [("lspike", 1, -27, 5), ("rspike", 3, 31, 5), ("lpad", 1, -12, 7), ("rpad", 1, 15, 7),
           ("lplate", 1, -21, 0), ("lhip", 0, -11, 0), ("head", 0, 2, 0), ("rhip", 0, 15, 0), ("rplate", 1, 24, 0)]
FALL = 0.6                                   # frame 5: each piece that share of the way from the burst to where it lies


def dead(rig, k):
    if k == 0:
        return frame(rig, {"lean": -1, "lclaw": (-2, -1), "rclaw": (2, -1)})
    if k in (1, 2, 3):
        rise = [0, -4, -8, -11][k]
        up_l = (-UP_BACK[0], UP_BACK[1], 2)
        claws = [None, ((-3, -4), (3, -4)), (up_l, UP_BACK), ((up_l[0], up_l[1] - 1, 2), (UP_BACK[0], UP_BACK[1] - 1, 2))][k]
        return frame(rig, {"lean": -2, "all": (-1, rise), "lclaw": claws[0], "rclaw": claws[1],
                           "front": ["rclaw", "lclaw"] if k > 1 else []})
    if k == 4:
        p = burst_air()
        p["flash"] = ["core", "lclaw", "rclaw"]
        return frame(rig, p)
    return falling(rig) if k == 5 else scatter(rig)


def burst_air():
    p = ring(None, 1.3)
    for name in p:
        if name != "split":
            v = p[name]
            p[name] = (v[0], v[1] - 9) + tuple(v[2:])
    return p


def box_mid(can):
    ys, xs = np.nonzero(can[..., 3] > 0)
    return (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2


def falling(rig):
    """Each piece of the scatter as it was in the burst, FALL of the way to where it lies (the core and the claws
    gone)."""
    air = burst_air()
    can = rig.canvas()
    for name, _, _, _ in SCATTER:
        a = frame(rig, {**air, "hide": [n for n in SPLIT_ORDER if n != name]})
        g = scatter(rig, only=name)
        (ax, ay), (gx, gy) = box_mid(a), box_mid(g)
        R.put(can, a, dx=int(round((gx - ax) * FALL)), dy=int(round((gy - ay) * FALL)))
    return can


def scatter(rig, only=None):
    D = rig.D
    can = rig.canvas()
    for name, k, mid, up in SCATTER:
        if only is not None and name != only:
            continue
        m = D.mask(name)
        ys, xs = np.nonzero(m)
        sub = D.layer(name)[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        t = np.rot90(sub, k)
        h, w = t.shape[:2]
        top, left = rig.GY - h - up, int(round(rig.CX + mid - w / 2))
        seat = t[..., 3] > 0
        reg = can[top:top + h, left:left + w]
        reg[seat] = t[seat]
    return can


def frames(rig):
    sheet = R.sheet_of(HERO)
    native = os.path.join(R.ROOT, "assets", "source", "native")
    with open(lp(os.path.join(native, f"{HERO}_bake.json")), encoding="utf-8") as f:
        bake = json.load(f)
    with open(lp(os.path.join(native, f"{HERO}_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)["tags"]
    baked = {e["into"] for e in bake["items"] if "from" in e}
    laid_in = {e["into"] for e in bake["items"] if "from" not in e}
    out = {}
    for tag in sheet:
        if tag in baked:
            continue
        # a tag the bake lays a picture into has the sheet's frames split at the picture's times: posed on its own
        ms = [r["ms"] for r in cells[tag]] if tag in laid_in else [m for _, m in sheet[tag]]
        n = len(ms)
        if tag == "dead":
            fr = [dead(rig, k) for k in range(n)]
        else:
            poses = {"idle": idle, "run": run, "attack": attack, "skill2": skill2, "ult": ult, "ult_shot": ult_shot,
                     "hit": hit, "ult_loop": lambda k: ring(k),
                     "skill": lambda k: q_pose(*SKILL[k]), "skill_quick": lambda k: q_pose(*QUICK[k])}
            if tag not in poses:
                sys.exit(f"{tag}: no pose")
            fr = [frame(rig, poses[tag](k)) for k in range(n)]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        for c in fr:
            c[rig.GY:] = 0
        out[tag] = list(zip(fr, ms))
    acts = rig.bake(out)
    for t in sheet:
        if len(acts[t]) != len(sheet[t]) or [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: {[round(m) for _, m in acts[t]]} against the sheet's {[m for _, m in sheet[t]]}")
    return {t: acts[t] for t in sheet}


def design():
    return Design()


def make_rig(D):
    rig = R.Rig(D, pad=(60, 60, 40, 10))         # the death's scatter and the ult's ring reach far
    rig.idle_canvas = frame(rig, idle(0))
    return rig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = Design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint = {"lclaw": (0, 128, 255), "rclaw": (0, 255, 255), "head": (255, 0, 0), "lpad": (255, 160, 0),
                "rpad": (255, 255, 0), "lplate": (0, 255, 0), "rplate": (0, 160, 0), "lspike": (255, 0, 255),
                "rspike": (160, 0, 160), "lchest": (255, 80, 80), "rchest": (255, 200, 120), "lhip": (80, 255, 80),
                "rhip": (80, 160, 255)}
        img = D.d.astype(float).copy()
        for n, c in tint.items():
            m = D.mask(n)
            img[m, :3] = img[m, :3] * 0.45 + np.array(c) * 0.55
        Image.fromarray(np.repeat(np.repeat(img.astype(np.uint8), 12, 0), 12, 1)).save(
            os.path.join(a.parts, f"{HERO}_parts.png"))
        rig = make_rig(D)
        diffs = []
        for split in (False, True):
            can = frame(rig, {"split": split})
            got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
            diffs.append(int((got != D.d).any(-1).sum()))
        print(f"PPU {D.ppu:.4f}, pivot column {D.px}, ground row {D.ground}, joints {D.joint}; the parts put back "
              f"differ in {diffs[0]} squares (split {diffs[1]})")
        return
    rig = make_rig(D)
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
