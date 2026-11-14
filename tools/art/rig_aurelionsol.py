#!/usr/bin/env python3
"""league_aurelionsol's action frames: Aurelion Sol's approved 3/4 designs and Codex's key poses after League's clips
(the user, 2026-10-24: 「codex都交付了 做到完美后喊我review」).

    python tools/art/rig_aurelionsol.py --parts DIR       # the designs with their parts tinted (12x)
    python tools/art/rig_aurelionsol.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_aurelionsol.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_aurelionsol_model.py, design_aurelionsol_poses.py):
  hd/idle.png         Aurelion Sol hovering, 3/4 front facing right, 56 x 77 at PPU 1.75 (44 game px crest to tail tip):
                      the idle and the hit;
  hd/run.png          his flight (step 1's B), 85 x 51 on the idle's scale: the move (League's Astral Flight - he flies
                      everywhere), the idle's head pasted on it (one face in all frames);
  hd/pose_<name>.png  Codex's key poses read back with the design's head, the bodies brought to the design's size
                      (assets/source/aurelionsol/POSE_PROMPTS.md): a_wind a_throw q_wind q_breath e_reach e_hold r_call
                      r_pull d_rear d_down.
He floats: every frame stands FLOAT rows above the ground line (Vel'Koz's way), except the dead one lying on it.
Placing a pose: across, its head box on the design's head box (one face that never jumps), moved dx squares (League's
lunges); up and down, its lowest square FLOAT rows over the ground, or `lift` rows more.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The move is his flight: the flying design whole, bobbing up and down a row or two, a wave travelling down the nebula
tail (its columns lifted, nothing where it leaves him) - no part turned or stretched.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
each key pose's tail swayed (a hanging tail's rows shifted sideways, a trailing tail's columns lifted - the tip 3-4
squares, nothing where it leaves him), a raised arm turned about its shoulder (inbetween.spin), never the head.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import inbetween as IB  # noqa: E402
from rig_wukong import CutDesign as _Cut, pad  # noqa: E402

HERO = "aurelionsol"
PPU = 1.75
SRC = os.path.join(R.ROOT, "assets", "source", "aurelionsol", "hd")
FLOAT = 4                      # rows between his lowest square and the ground line (he hovers)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU
        self.ground += FLOAT


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 22                     # the column under his body's middle (the tail's root): the standing point
HEAD_X, HEAD_Y = 3, 0          # the head box's top-left square on hd/idle.png (pack_aurelionsol_poses.HEAD)
HEAD_W, HEAD_H = 35, 32        # the head box: the mane's top to the chin's gold point
RUN_HEAD = (45, 0)             # where the idle's head (design_aurelionsol_poses.POLY) lies best on hd/run.png


def head_squares():
    """The idle's head squares (design_aurelionsol_poses.POLY) -> (rows, cols, colours)."""
    import design_aurelionsol_poses as DP
    d = load("idle.png")
    ys, xs = np.nonzero(DP.head_mask(d))
    return ys, xs, d[ys, xs]


def run_design():
    """hd/run.png with the idle's head pasted on its own (one face in all frames)."""
    r = load("run.png")
    ys, xs, c = head_squares()
    r[ys + RUN_HEAD[1], xs + RUN_HEAD[0]] = c
    return r


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("body", D.rest())
    return D


def close_cracks(can, outline, most=12, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across - the
    outline (gap-check; rig_belveth.close_cracks)."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


def picture(name):
    """A pose's picture: hd/pose_<name>.png, or the design itself for "idle"."""
    return load("idle.png" if name == "idle" else f"pose_{name}.png")


def without(d, parts, head):
    """Each part's mask (PARTS: polygons, boxes) less the head's squares - a raised claw lies next to his face, and a
    polygon's edge may take a square more than its vertices say - as row runs (x0, y, x1, y) for inbetween.vary."""
    out = {}
    for k, items in parts.items():
        m = IB.part_mask(d.shape, items) & ~head
        runs = []
        for y in range(m.shape[0]):
            xs = np.nonzero(m[y])[0]
            if not len(xs):
                continue
            cut = np.nonzero(np.diff(xs) > 1)[0]
            runs += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
        out[k] = runs
    return out


def rows_wave(shape, y0, y1, k):
    """The moves of a hanging (or rising) tail's sway: its whole rows shifted sideways, nothing on row y0 where it
    leaves him and k columns (negative: to the left) on row y1 at its tip, the rows past the tip going with it -
    inbetween.wave on its side. Neighbouring rows step a square at most, which keeps the drawn outline closed.
    -> (dx, dy) arrays."""
    H, W = shape[:2]
    dx = np.zeros((H, W), int)
    for y in range(H):
        t = min(max((y - y0) / (y1 - y0), 0.0), 1.0)
        dx[y, :] = int(round(k * t))
    return dx, np.zeros((H, W), int)


def travelling(shape, x0, x1, amp, phase, beats=0.5):
    """The moves of a wave travelling down a trailing tail: its whole columns lifted amp t sin(phase - 2 pi beats t)
    rows, t from 0 where it leaves him (column x1) to 1 at its tip (column x0), the columns past the tip going with it;
    the phase stepped on from frame to frame carries the wave toward the tip. Neighbouring columns step a square at
    most. -> (dx, dy) arrays."""
    H, W = shape[:2]
    dy = np.zeros((H, W), int)
    for x in range(W):
        t = min(max((x1 - x) / (x1 - x0), 0.0), 1.0)
        dy[:, x] = -int(round(amp * t * np.sin(phase - 2 * np.pi * beats * t)))
    return np.zeros((H, W), int), dy


def head_at(name):
    """The head box's top-left square in hd/pose_<name>.png (design_aurelionsol_poses' json); the design's own for
    "idle"."""
    if name == "idle":
        return [HEAD_X, HEAD_Y]
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


class Form:
    """The designs and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(72, 40, 40, 12)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.run = run_design()

    def pose(self, whole=(0, 0)):
        """The idle design moved by whole squares (dx, dy)."""
        can = R.compose(self.rig, [(self.L["body"], dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can

    def place(self, d, left, top):
        rig = self.rig
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can

    def flying(self, rise=0, phase=0.0):
        """The flight: hd/run.png (the idle's head on it) with its head box over the idle's, its lowest square FLOAT +
        rise rows over the ground; a wave travelling down the tail (travelling: RUN_TAIL's columns, the tip RUN_AMP
        rows up and down, `phase` its step), "under" the rest of him - the head and the body checked unchanged."""
        rig = self.rig
        r = self.run
        ys = np.nonzero((r[..., 3] > 0).any(1))[0]
        left = rig.ox + HEAD_X - RUN_HEAD[0]
        top = rig.GY - FLOAT - rise - (ys.max() + 1)
        hy, hx, _ = head_squares()
        head = np.zeros(r.shape[:2], bool)
        head[hy + RUN_HEAD[1], hx + RUN_HEAD[0]] = True
        x0, x1 = RUN_TAIL[0], RUN_TAIL[2]
        wave = travelling(r.shape, x0, x1, RUN_AMP, phase)
        r = IB.vary(r, without(r, {"tail": [RUN_TAIL]}, head), self.D.outline, [("tail", wave, "under")], (), None,
                    head, VPAD, "run")
        return close_cracks(self.place(r, left - VPAD, top - VPAD), self.D.outline)

    def posed(self, name, dx=0, lift=None, tail=0, spins=()):
        """A Codex pose (hd/pose_<name>.png; "idle": the design) with its head box on the design's, moved dx squares;
        its lowest square `lift` rows over the ground (FLOAT unless given). The in-betweens (tools/art/inbetween.py
        vary), the pose placed as it is whole: tail k - its tail waved (WAVE: the tip k squares sideways for a hanging
        tail, up for a trailing one); spins [(part, degrees)] - a raised arm turned clockwise about its shoulder
        (PIVOT). Both go "under" the rest of him; the head and every square in no part are checked unchanged."""
        rig = self.rig
        d = picture(name)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        hx, hy = head_at(name)
        left = rig.ox + HEAD_X - hx + dx
        top = rig.GY - (ys.max() + 1) - (FLOAT if lift is None else lift)
        if tail or spins:
            d = self.varied(name, d, tail, spins)
            left, top = left - VPAD, top - VPAD
        return self.place(d, left, top)

    def varied(self, name, d, tail, spins):
        """The pose picture with its tail waved and arms turned (see posed), on a canvas VPAD squares bigger on every
        side."""
        head = self.head(name, d)
        moves, sway = [], []
        if tail:
            part, kind, *w = WAVE[name]
            if kind == "rows":
                moves.append((part, rows_wave(d.shape, w[0], w[1], tail), "under"))
            else:
                sway.append((part, w[0], w[1], tail, w[2]))
        turned = [(part, PIVOT[(name, part)], deg, "under") for part, deg in spins]
        return IB.vary(d, without(d, PARTS[name], head), self.D.outline, moves, sway, None, head, VPAD, name, (),
                       turned)

    def head(self, name, d):
        """The head's squares in a pose picture: the design's (design_aurelionsol_poses.POLY on hd/idle.png) that the
        pose holds unchanged in its head box (Q's breath: only above the open jaw)."""
        import design_aurelionsol_poses as DP
        des = self.D.d
        ys, xs = np.nonzero(DP.head_mask(des))
        hx, hy = head_at(name)
        ty, tx = ys - HEAD_Y + hy, xs - HEAD_X + hx
        ok = (ty >= 0) & (ty < d.shape[0]) & (tx >= 0) & (tx < d.shape[1])
        ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
        same = (d[ty, tx] == des[ys, xs]).all(-1)
        m = np.zeros(d.shape[:2], bool)
        m[ty[same], tx[same]] = True
        return m


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_aurelionsol.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27: the claw raised, the star let go at a_rel 10 (167 ms), back to the idle;
# Q (skill, held by a CasterAnimation for q_t 90 ticks = 1500 ms): the breath in, then the breath (the jaw open), the
# body rising and settling a row while the beam pulses from q_rel 8 (133 ms);
# E (skill2, e_dur 30 = 500 ms): the claw reaching out, the claws cupped as the orb flies at e_rel 12 (200 ms);
# R (ult, r_dur 36 = 600 ms): the claw raised high, yanked down at r_rel 14 (233 ms) as the star starts to fall.
#
# The in-betweens (2026-11-14: the attack played 3 poses, Q 2 - its breath one drawing a row up and down -, E, R and
# the death 2 each): each span above is shared out over more frames (inbetween.spans: whole ms, none under 50), so
# every action is as long as it was and its strike still begins on its millisecond - the star let go at 167, the beam
# at 133, the orb at 200, the yank at 233, the slump at 400. A frame that is only its neighbour moved whole is no new
# pose: the tail sways or an arm turns in each in-between.
MS = {"idle": [1000], "run": [120] * 6,
      "attack": IB.spans((167, 3), (150, 2), (133, 2)),
      "skill": IB.spans((133, 2), (1368, 9)),
      "skill2": IB.spans((200, 3), (300, 3)),
      "ult": IB.spans((233, 3), (367, 3, (3, 4, 4))),
      "hit": [100, 100],
      "dead": IB.spans((150, 1), (250, 2), (1000, 3, (8, 10, 82)))}
# the flight: per frame the figure's rise (rows up); the tail's wave steps a sixth of its beat a frame
FLIGHT = [0, 1, 2, 2, 1, 0]
RUN_TAIL = (0, 14, 25, 46)     # hd/run.png: the tail (columns 0-25, rows 14-46: short of the far claws)
RUN_AMP = 4                    # rows its tip rises and falls
# each pose moved dx squares from the design's head column (League's lunges), `lift` rows off the ground (None: FLOAT)
AT = {"a_wind": (0, None), "a_throw": (2, None), "q_wind": (0, None), "q_breath": (1, None), "e_reach": (1, None),
      "e_hold": (0, None), "r_call": (0, None), "r_pull": (2, None), "d_rear": (-2, 2), "d_down": (-4, 0),
      "idle": (0, None)}

# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py): boxes / polygons
# in each picture's own squares, less the head. The nebula tail sways - a hanging tail's rows shifted sideways, a
# trailing tail's columns lifted (WAVE) -, a raised arm turns about its shoulder (PIVOT: the corner where it leaves
# him on the side it turns away from, so its root swings in under him). The head, the chest and the rest of him are in
# no part: they never change.
VPAD = 30                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "idle": {"tail": [(10, 56, 40, 77)]},
    "a_wind": {"arm": [(34, 18, 48, 44)], "tail": [(4, 58, 40, 88)]},
    "a_throw": {"tail": [(0, 44, 38, 63)]},
    "q_wind": {"tail": [(0, 57, 40, 79)]},
    "q_breath": {"tail": [(0, 49, 34, 68)]},
    "e_reach": {"arm": [(57, 14, 81, 42)], "tip": [(0, 28, 12, 56)]},
    "e_hold": {"tail": [(0, 57, 40, 76)]},
    "r_call": {"arm": [[(41, 0), (60, 0), (60, 40), (49, 47), (41, 47)]], "tail": [(20, 66, 56, 88)]},
    "r_pull": {"tail": [[(0, 0), (19, 0), (19, 30), (16, 30), (16, 49), (0, 49)]]},
    "d_rear": {"tail": [(22, 66, 58, 92)]},
    "d_down": {"tail": [(0, 38, 48, 58)]},
}
# each pose's tail and how it waves: (part, "rows", y0, y1) - hanging (or rising), nothing on row y0, the tip's row y1
# moved k columns; (part, "cols", x0, x1, attached end) - trailing, its columns lifted 0..k rows (inbetween.wave)
WAVE = {"idle": ("tail", "rows", 56, 76), "a_wind": ("tail", "rows", 58, 87), "q_wind": ("tail", "rows", 57, 78),
        "q_breath": ("tail", "rows", 49, 67), "e_hold": ("tail", "rows", 57, 75), "r_call": ("tail", "rows", 66, 87),
        "d_rear": ("tail", "rows", 66, 91), "r_pull": ("tail", "rows", 48, 0), "e_reach": ("tip", "rows", 56, 28),
        "a_throw": ("tail", "cols", 0, 38, "right"), "d_down": ("tail", "cols", 0, 48, "right")}
PIVOT = {("a_wind", "arm"): (34, 37), ("e_reach", "arm"): (56, 34), ("r_call", "arm"): (42, 40)}


def actions(F):
    p, q = F.pose, F.posed

    def at(name, ddx=0, dlift=0, **how):
        dx, lift = AT[name]
        return q(name, dx + ddx, (FLOAT if lift is None else lift) + dlift, **how)
    out = {}
    out["idle"] = [p()]
    # the flight (League's run: he swims through the air, the wave running down his tail)
    out["run"] = [F.flying(r, 2 * np.pi * k / len(FLIGHT)) for k, r in enumerate(FLIGHT)]
    # auto attack (League's Attack1: reared up, the far claw drawn back, then flung forward): the claw coming up as the
    # tail swings, raised; flung forward, the trailing tail whipping up after him; settling back, the tail swinging
    # under him; the idle
    out["attack"] = [at("a_wind", tail=3, spins=[("arm", 40)]), at("a_wind", tail=-2), at("a_wind"),
                     at("a_throw"), at("a_throw", tail=4), at("idle", tail=-3), p()]
    # Q Breath of Light (Spell1: the breath in, then the jaw open on the target; the body rises and settles a row while
    # the tail sways from side to side)
    sway = [0, 3, 0, -3]
    out["skill"] = [at("q_wind", tail=3), at("q_wind")] + [at("q_breath", dlift=k % 2, tail=sway[k % 4])
                                                           for k in range(len(MS["skill"]) - 2)]
    # E Singularity (Spell3: the claw reaching out, the claws cupped round the black hole): the claw coming up, the
    # tail's tip whipping; reached out; cupped as the orb flies, the tail swaying after it
    out["skill2"] = [at("e_reach", tail=3, spins=[("arm", 30)]), at("e_reach", tail=-2), at("e_reach"),
                     at("e_hold"), at("e_hold", tail=3), at("e_hold", tail=-2)]
    # R Falling Star (Spell4_Calamity: the claw raised to the sky, yanked down): the claw going up as the tail swings,
    # raised; yanked down, the tail flung over him swaying on
    out["ult"] = [at("r_call", tail=3, spins=[("arm", 45)]), at("r_call", tail=-2), at("r_call"),
                  at("r_pull"), at("r_pull", tail=3), at("r_pull", tail=-2)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's Death: rearing back, sunk to the ground): struck; rearing back with the tail swinging, sinking;
    # down, the tail falling after him, still
    out["dead"] = [R.flash(at("d_rear")), at("d_rear", tail=3), at("d_rear", -1, -1, tail=-3),
                   at("d_down", tail=4), at("d_down", tail=2), at("d_down")]
    return out


def frames(F, tags=None):
    out = {}
    for tag, cans in actions(F).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    D = design()
    F = Form(D)
    F.rig.idle_canvas = F.pose()
    acts = frames(F, a.tags.split(",") if a.tags else None)
    if a.review:
        F.rig.review(acts, a.review)
        return
    F.rig.export(acts)


if __name__ == "__main__":
    main()
