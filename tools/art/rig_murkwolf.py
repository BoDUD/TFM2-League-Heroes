#!/usr/bin/env python3
"""tft_murkwolf's action frames: Murk Wolf's approved design and Codex's key poses after its own TFT clips (the user,
2026-11-01: sprites by Codex from written prompts).

    python tools/art/rig_murkwolf.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_murkwolf.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                      # (tft/champions/tft_murkwolf), then ppu_restyle.py / ppu_hd.py --hero murkwolf

The pictures (tools/art/design_murkwolf_model.py, design_murkwolf_poses.py):
  hd/idle.png         the two-headed wolf crouched, 3/4 facing right, 83 x 60 at PPU 1.67 (36 game px, the tail tip to
                      its claws): the idle, the hit and the run;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's faces where they match
                      (assets/source/murkwolf/POSE_PROMPTS.md, design_murkwolf_poses.py): a_back a_bite q_crouch q_leap
                      q_rend e_gather e_howl r_growl r_bark d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: its planted hind foot carried to the root column) on the
design's (design_murkwolf_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground.
The run is the design's own idle trotting (rig_raptor's walk on the idle: every Codex run frame here was a body of its
own - its tail, body length and head spacing changed frame to frame, codex-walk-drafts-differ): the body, the mane, the
two heads and the tail exactly the idle's; its three visible legs cut out (LEGS: the hind leg at the left, the near
front leg under the chest, the far front leg under the far head) and each swung about its top row by a shear (the foot
moves STRIDE columns, the hip stays), lifted LIFT rows while it swings forward; the near front leg half a cycle against
the other two (a trot), the body rising a row as the legs pass. One full cycle in RUN_MS x 8 (TFT's gallop is 0.8 s).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_murkwolf_poses import DESIGN_PIVOT  # noqa: E402

HERO = "murkwolf"
PPU = 1.67
SRC = os.path.join(ROOT, "assets", "source", "murkwolf", "hd")
POSES = ("a_back", "a_bite", "q_crouch", "q_leap", "q_rend", "e_gather", "e_howl", "r_growl", "r_bark", "d_fall",
         "d_down")
SHIFT = {}
# the legs in hd/idle.png (rows, columns; ends exclusive) and their phase (a turn = one cycle): the hind leg below the
# thigh, the near front leg below the chest (its upper part above row 46 stays with the body), the far front leg below
# the far head's ruff
LEGS = {"hind": ((40, 60, 0, 27), 0.0), "near": ((46, 60, 27, 50), 0.5), "far": ((49, 60, 60, 79), 0.0)}
STRIDE = 5                      # columns the foot swings to each side of where it stands
LIFT = 3                        # rows a foot is lifted at the top of its swing
FOOT = 5                        # a leg's lowest rows (the paw and claws) moved whole, not sheared
CRACK = 3                       # bare squares a step opens, this many columns wide at most: a crack
SPECK = 6                       # loose parts smaller than this are dropped


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def leg_step(k, phase):
    """(foot columns forward, rows lifted) of a leg at frame k of 8: the foot swings forward (lifted) in one half of
    the cycle and pushes back (planted) in the other."""
    t = 2 * math.pi * (k / 8 + phase)
    return round(STRIDE * math.sin(t)), max(0, round(LIFT * math.cos(t)))


def trot_frame(d, k):
    """The idle with its legs at frame k: each leg's squares sheared about its top row (row y moves dx * (y - top) /
    (knee - top)) and lifted, its paw (the lowest FOOT rows) moved whole, the body over all of them; the cracks a step
    opens closed with the outline."""
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    pad = STRIDE + 1
    out = np.zeros((H, W + 2 * pad, 4), np.uint8)
    body = d.copy()
    masks = {}
    for name, ((r0, r1, c0, c1), _) in LEGS.items():
        m = np.zeros((H, W), bool)
        m[r0:r1, c0:c1] = True
        masks[name] = m & op
        body[masks[name]] = 0
    order = ("far", "hind", "near")                       # the far front leg behind, the near front leg in front
    for name in order:
        (r0, r1, c0, c1), phase = LEGS[name]
        dx, lift = leg_step(k, phase)
        m = masks[name]
        ys, xs = np.nonzero(m)
        knee = ys.max() - FOOT                          # the foot below it moves whole
        f = np.clip((ys - r0) / max(1, knee - r0), 0, 1)
        nx = xs + np.round(dx * f).astype(int) + pad
        ny = ys - np.round(lift * f).astype(int)
        out[ny, nx] = d[ys, xs]
    b = body[..., 3] > 0
    out[:, pad:pad + W][b] = body[b]
    # one-square cracks a shear opens inside the figure take the outline (the idle's own holes stay)
    opw = np.zeros(out.shape[:2], bool)
    opw[:, pad:pad + W] = op
    own = ndimage.binary_fill_holes(opw) & ~opw
    outline = PD.edge_colour(d)
    wop = out[..., 3] > 0
    crack = ndimage.binary_fill_holes(wop) & ~wop & ~own
    for y in np.nonzero(crack.any(1))[0]:
        xs = np.nonzero(crack[y])[0]
        for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
            if len(run) <= CRACK:
                out[y, run] = (*outline[:3], 255)
    lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3), bool))   # loose specks
    sizes = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            out[lab == j] = 0
    return out, pad


def rise_of(k):
    """The body a row up as the legs pass (frames 0 and 4: the swinging feet under the body)."""
    return 1 if k % 4 == 0 else 0


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.pivot = DESIGN_PIVOT
        lefts, rights, tops = [-STRIDE - 2], [d.shape[1] + STRIDE + 2], [-2]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot on the design's, its lowest row on the
        ground."""
        x = self.pivot - meta(name)["pivot"][0]
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def place(self, p, x, y, name):
        rig = self.rig
        can = rig.canvas()
        left, top = rig.ox + x, rig.oy + y
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return can

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        can = self.place(p, x + dx, y, name)
        return R.flash(can) if flash else can

    def trot(self, k):
        fig, pad = trot_frame(self.d, k)
        return self.place(fig, -pad, -rise_of(k), f"run{k + 1}")


# ms per frame; the kit's ticks (tools/kit/build_murkwolf.py) match these (a frame's start in ticks = ms x 0.06):
# attack 367 ms = atk_dur 22, the bite on atk_st 10 (167 ms: a_bite showing); Rending Claws' leap 233 ms = q_jump 14 and
# its rend 267 ms = q_dur 30 less q_jump; Slayer's Howl 500 ms = e_dur 30, the howl on e_st 20 (333 ms); Pack Attack 500
# ms = r_dur 30, the pups pounce on r_st 12 (200 ms: r_bark showing). The run: one full cycle in 0.8 s (TFT's gallop).
RUN_MS = 100
MS = {"idle": [1000], "run": [RUN_MS] * 8, "attack": [167, 200], "leap": [100, 133], "rend": [267],
      "howl": [150, 350], "ult": [200, 300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [C.trot(k) for k in range(8)]
    out["attack"] = [f("a_back"), f("a_bite")]                               # Twin Bite
    out["leap"] = [f("q_crouch"), f("q_leap")]                               # Rending Claws: the spring
    out["rend"] = [f("q_rend")]                                              # Rending Claws: the rend
    out["howl"] = [f("e_gather"), f("e_howl")]                               # Slayer's Howl
    out["ult"] = [f("r_growl"), f("r_bark")]                                 # Pack Attack
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down")]
    return out


def frames(C, tags=None):
    out = {}
    for tag, cans in actions(C).items():
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
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
