#!/usr/bin/env python3
"""league_heimerdinger's action frames, posed on the approved 3/4 design after League's own clips (the user's way since
2026-10-20: the actions rigged by me from the design, no Codex pose packs).

    python tools/art/rig_heimerdinger.py --parts DIR     # the cut, tinted, at 14x
    python tools/art/rig_heimerdinger.py --review DIR    # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_heimerdinger.py                 # orig strips + the 1x sheet

The design (tools/art/design_heimerdinger_model.py, Codex's A-2 cut to 54 rows, 50 x 54 squares at PPU 1.5, 3/4 front
facing right): the orange multitool in his right hand (image-left, the near arm), the grey-green wrench in his left
(image-right, the far arm), two short boots. Every pose is lossless: the arms are the design's own squares (each from
its glove to its tool, below the coat's cuff), moved by whole squares, at most REACH from the cuff (his head is two
thirds of him: a hand turned or raised past the shoulder lies over the goggles); the boots step by
whole squares; the body (the mane, the goggles, the moustache, the coat) is never cut - it moves as one block and leans
by whole rows above the belt. League's clips (Heimerdinger_Base_Attack1 / Spell1 / Spell3, Spell4_IN / LOOP, Run1, Death)
are followed in the body; his Q and E lift a crane arm out of his backpack that holds the turret / the grenade: that
arm is not in the design and goes to the effects (step 3), the body pose stays (he braces, the tool hand works it).
Timings match the kit (build_heimerdinger.P): attack 27 ticks with the bolt on tick 10, Q and E 30 with the turret's
bolt / the grenade on 12, R 40 with the upgrade on 14.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_zyra import stamp  # noqa: E402

HERO = "heimerdinger"
PPU = 1.5
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
INK = None                                   # read from the design: its darkest colour

# the arms below the orange cuffs (they are the coat's): the tool or wrench and the purple glove holding it (x0, y0, x1, y1)
TOOL_BOX = [(7, 34, 16, 45), (13, 45, 16, 47)]   # the near arm, the multitool
WRENCH_BOX = [(38, 33, 50, 46), (34, 41, 38, 45)]   # the far arm, the wrench (the moustache's tip at 34-37 stays)
REACH = 1                                    # squares a hand may move from its cuff and stay held (weapon-arm-drawn)
NBOOT_BOX = (14, 49, 25, 54)
FBOOT_BOX = (25, 49, 37, 54)
TOOL_SHOULDER = (17.0, 38.0)                 # square edges: what the arms turn about
WRENCH_SHOULDER = (35.0, 39.0)
BELT = 44                                    # rows above lean as one block over the hips
TOP = 34                                     # rows above (the head) never cut by a lean


def lp(path):
    return R.lp(path)


class Design:
    def __init__(self):
        d = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA")).copy()
        self.d0 = d
        self.H, self.W = d.shape[:2]
        self.hero, self.ppu = HERO, PPU
        op = d[..., 3] > 0
        lum = d[..., :3].astype(int).sum(-1)
        self.outline = tuple(int(v) for v in d[op][np.argmin(lum[op])][:3])
        ys, xs = np.nonzero(op)
        self.ground = ys.max() + 1
        low = d[ys.max() - 2:ys.max() + 1, :, 3].any(0)
        fx = np.nonzero(low)[0]
        self.px = int(round((fx.min() + fx.max() + 1) / 2))

        def box(*bs):
            m = np.zeros(op.shape, bool)
            for x0, y0, x1, y1 in bs:
                m[y0:y1, x0:x1] = True
            return m & op
        self.parts = {"tool": box(*TOOL_BOX), "wrench": box(*WRENCH_BOX), "nboot": box(NBOOT_BOX),
                      "fboot": box(FBOOT_BOX)}
        body = op.copy()
        for m in self.parts.values():
            body &= ~m
        self.parts["body"] = body
        self.layers = {k: np.where(m[..., None], d, 0).astype(np.uint8) for k, m in self.parts.items()}


class Pose:
    """One frame. tool / wrench: (quarter turns ccw, dx, dy) of each arm; boots: {nboot / fboot: (dx, dy)}; dx, dy the
    whole figure; sink rows the body (with the arms) sets down onto the boots; lean columns at the head (whole rows,
    the head one block); flash."""

    def __init__(self, tool=(0, 0, 0), wrench=(0, 0, 0), boots=None, dx=0, dy=0, sink=0, lean=0, flash=False):
        self.tool, self.wrench = tool, wrench
        self.boots = {"nboot": (0, 0), "fboot": (0, 0), **(boots or {})}
        self.dx, self.dy, self.sink, self.lean, self.flash = dx, dy, sink, lean, flash


def lean_rows(layer, lean):
    if not lean:
        return layer
    out = np.zeros_like(layer)
    for y in range(layer.shape[0]):
        s = lean if y < TOP else (0 if y >= BELT else int(round(lean * (BELT - y) / (BELT - TOP))))
        if s > 0:
            out[y, s:] = layer[y, :-s]
        elif s < 0:
            out[y, :s] = layer[y, -s:]
        else:
            out[y] = layer[y]
    return out


def compose(rig, D, p):
    can = rig.canvas()
    ox, oy = rig.ox + p.dx, rig.oy + p.dy
    up = (ox, oy + p.sink)

    def arm(name, shoulder, op_):
        k, dx, dy = op_
        assert max(abs(dx), abs(dy)) <= REACH and not k, f"{name} {op_}: a hand moved off its cuff"
        sh_lean = p.lean if shoulder[1] < TOP else int(round(p.lean * (BELT - shoulder[1]) / (BELT - TOP)))
        stamp(can, D.layers[name], (up[0] + dx + sh_lean, up[1] + dy), (False, k), shoulder)

    # back to front: the far arm (the wrench), the far boot, the body, the near boot, the near arm (the multitool);
    # an arm raised over the head is drawn in front (it would vanish in the mane)
    front_wrench = p.wrench[0] != 0
    if not front_wrench:
        arm("wrench", WRENCH_SHOULDER, p.wrench)
    for b in ("fboot",):
        bx, by = p.boots[b]
        stamp(can, D.layers[b], (ox + bx, oy + by))
    stamp(can, lean_rows(D.layers["body"], p.lean), up)
    bx, by = p.boots["nboot"]
    stamp(can, D.layers["nboot"], (ox + bx, oy + by))
    if front_wrench:
        arm("wrench", WRENCH_SHOULDER, p.wrench)
    arm("tool", TOOL_SHOULDER, p.tool)
    can[rig.GY:] = 0
    return R.flash(can) if p.flash else can


# per tag: [(pose, ms)] after League's clips (frame times in ms)
def acts():
    P_ = Pose
    run_b = [({"nboot": (2, 0), "fboot": (-2, 0)}, 0), ({"nboot": (1, -1), "fboot": (-1, 0)}, 1),
             ({"nboot": (-1, 0), "fboot": (1, -1)}, 0), ({"nboot": (-2, 0), "fboot": (2, 0)}, 0),
             ({"nboot": (-1, 0), "fboot": (1, -1)}, 1), ({"nboot": (1, -1), "fboot": (-1, 0)}, 0)]
    return {
        "idle": [(P_(sink=s), 150) for s in (0, 0, 1, 1, 1, 1, 0, 0)],
        # Run1: little quick steps, the body bobbing a row, leaning into the run, the arms held
        "run": [(P_(boots=b, dy=-up_, lean=1, tool=(0, 0, -up_), wrench=(0, 0, up_ - 1 if up_ else 0)), 100)
                for b, up_ in run_b],
        # Attack1: he draws the wrench back, then jabs it forward at the target (the bolt leaves it on tick 10)
        "attack": [(P_(), 83), (P_(wrench=(0, -1, -1), lean=-1), 84),
                   (P_(wrench=(0, 1, 0), lean=1, dx=1), 117), (P_(wrench=(0, 1, 0), lean=1), 83), (P_(), 83)],
        # Spell1 (Q): he crouches and reaches the multitool down in front (the crane arm from his pack sets the turret
        # down: step 3), the turret's bolt on tick 12. His head is two thirds of him: a hand turned or raised past the
        # shoulder lies over the goggles or across the boots, so the hands only move by whole squares, low.
        "skill": [(P_(), 67), (P_(sink=1, lean=1, tool=(0, 1, 1), wrench=(0, 0, 1)), 67),
                  (P_(sink=2, lean=2, tool=(0, 1, 1), wrench=(0, 1, 1)), 133),
                  (P_(sink=2, lean=2, tool=(0, 1, 1), wrench=(0, 1, 1)), 100),
                  (P_(sink=1, lean=1, tool=(0, 1, 1), wrench=(0, 0, 1)), 67), (P_(), 66)],
        # Spell3 (E): the wrench hand drawn back and up, then flung forward (the grenade on tick 12)
        "skill2": [(P_(), 67), (P_(wrench=(0, -1, -1), lean=-1), 67), (P_(wrench=(0, -1, -1), lean=-2, dx=-1), 66),
                   (P_(wrench=(0, 1, -1), lean=2, dx=1), 133), (P_(wrench=(0, 1, 0), lean=1), 100), (P_(), 67)],
        # Spell4_IN / LOOP (R): a crouch with the hands in, then a hop with both tools spread out (the upgrade bursts
        # out round him on tick 14: step 3)
        "ult": [(P_(), 67), (P_(sink=2, tool=(0, 1, 1), wrench=(0, -1, 1)), 100),
                (P_(dy=-1, tool=(0, -1, -1), wrench=(0, 1, -1), lean=-1), 66),
                (P_(dy=-2, tool=(0, -1, -1), wrench=(0, 1, -1), lean=-1), 100),
                (P_(dy=-1, tool=(0, -1, -1), wrench=(0, 1, -1), lean=-1), 167),
                (P_(sink=1, tool=(0, 0, 1), wrench=(0, 0, 1)), 100), (P_(), 67)],
        "hit": [(P_(dx=-2, lean=-1, flash=True), 100), (P_(dx=-1), 100)],
        "dead": None,
    }


def frames(rig):
    D = rig.D
    out = {}
    for tag, seq in acts().items():
        if seq is None:
            continue
        out[tag] = [(compose(rig, D, p), ms) for p, ms in seq]
    # Death: he staggers back, sits down hard and falls on his back, head to the image-left
    back = compose(rig, D, Pose(lean=-2, dx=-1, tool=(0, -1, -1), wrench=(0, 1, -1)))
    sit = compose(rig, D, Pose(sink=2, lean=-2, dx=-2, tool=(0, -1, 0), wrench=(0, 1, 0)))
    flat = compose(rig, D, Pose())
    lie = R.lie(rig, flat, k=1, dx=-6, sink=3)
    bounce = R.lie(rig, flat, k=1, dx=-6, sink=1)
    out["dead"] = [(back, 117), (sit, 117), (bounce, 100), (lie, 150), (lie.copy(), 300), (lie.copy(), 500)]
    return out


TINT = {"tool": (0, 128, 255), "wrench": (255, 255, 0), "nboot": (255, 0, 255), "fboot": (0, 255, 128)}


def parts_png(D, path, z=14):
    img = D.d0.astype(float).copy()
    for n, c in TINT.items():
        m = D.parts[n]
        img[m, :3] = img[m, :3] * 0.45 + np.array(c) * 0.55
    big = Image.fromarray(np.repeat(np.repeat(img.astype(np.uint8), z, 0), z, 1))
    bg = Image.new("RGBA", big.size, (210, 210, 210, 255))
    bg.alpha_composite(big)
    bg.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = Design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        parts_png(D, os.path.join(a.parts, f"{HERO}_parts.png"))
        return
    rig = R.Rig(D, pad=(40, 40, 30, 20))
    acts_ = frames(rig)
    if a.review:
        rig.review(acts_, a.review)
        return
    rig.export(acts_)


if __name__ == "__main__":
    main()
