#!/usr/bin/env python3
"""league_graves's action frames, posed from the approved designs' own squares and Codex's poses on skeletons.

    python tools/art/rig_graves.py --parts DIR       # the side design with its parts tinted (12x)
    python tools/art/rig_graves.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_graves.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_graves.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_graves_model.py, the user's picks 2026-10-20: A-1 and side-2, 38 game px hair to soles at
PPU 1.5 = 57 rows; one palette, one head): idle.png (3/4 front, 67 x 57) and side.png (side-on facing right with the
idle's head, 74 x 57: every action's base). Lossless: parts cut square by square from a design, moved by whole
squares only; the shotgun is never turned off the level by the rig (a tipped gun comes from Codex's poses, drawn
straight: pack_graves_poses.py / design_graves_poses.py).
Parts of the side design: the legs under the belt (LEG_BAND: the back leg to LEG_SPLIT, the front leg past it); the rest
is the body (head, scarf, pauldron, torso, arms and the shotgun with both hands on it - the gun's golds and steel are
mixed square by square with the hands, the sleeves and the trousers' top, so it never moves apart from the body).
The walk is league_nautilus's / league_braum's approved walk (the heavy heroes' rule, memory run-legs-caitlyn-way: Galio's
final ruling): the design's own legs cut under the belt, one lifted per frame by losing its top rows and set a little
forward, the body floating a row; no part turned, sheared or redrawn.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad, sheet  # noqa: E402

HERO = "graves"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "graves", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the side's parts
STAND = 33                     # the column between his boots: the standing point
LEG_BAND = 41                  # the belt's lowest row: the legs start below it
LEG_SPLIT = 33                 # the column between the legs (back leg to it, front leg past it)
MUZZLE = (73, 30)              # the muzzle's middle (design square): the flash is laid here
IDLE_STAND = 33                # the idle design's standing column (between its boots)
IDLE_LEG_ROW = 41              # the idle design's legs from this row stay while the body breathes


def design():
    d = load("side.png")
    D = CutDesign(d, px=STAND)
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    D.part("back_leg", D.box(LEG_BAND + 1, D.H - 1, 0, LEG_SPLIT))
    D.part("front_leg", D.box(LEG_BAND + 1, D.H - 1, LEG_SPLIT + 1, D.W - 1))
    D.part("body", D.rest())
    return D


TINT = {"back_leg": (60, 120, 255), "front_leg": (255, 60, 60)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def lifted(layer, lift):
    """A leg layer lifted `lift` rows by losing its top rows (the thigh turned toward us): league_braum's walk."""
    if not lift:
        return layer
    out = layer.copy()
    ys = np.nonzero(layer[..., 3].any(1))[0]
    out[:ys.min() + lift] = 0
    return np.roll(out, -lift, axis=0)


class Form:
    """The designs' layers; pose() / front() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.idle = self.placed(load("idle.png"), IDLE_STAND)

    def placed(self, d, stand):
        """Another design in a padded layer of the side design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        lay[top:top + d.shape[0], x0:x1] = d[:, x0 - left:x1 - left]
        return lay

    def pose(self, whole=(0, 0), crouch=0, back=(0, 0, 0), front=(0, 0, 0)):
        """whole: the whole figure (dx, dy); crouch: rows the upper body (with the gun: the gun is never moved apart
        from the body - its golds and steel are mixed with the hands and the trousers) sets down onto the legs;
        back / front: a leg's (dx, dy, lift)."""
        wx, wy = whole
        ux, uy = wx, wy + crouch
        L = self.L
        layers = []
        for name, (dx, dy, lift) in (("back_leg", back), ("front_leg", front)):
            layers.append((lifted(L[name], lift), dict(dx=wx + dx, dy=wy + dy)))
        layers.append((L["body"], dict(dx=ux, dy=uy)))
        can = R.compose(self.rig, layers)
        return close_cracks(can, self.D.outline)

    def front(self, crouch=0, whole=(0, 0), flash=False):
        """The 3/4 idle design, its body (above IDLE_LEG_ROW) set down `crouch` rows onto its own legs."""
        lay = self.idle
        legs, top = lay.copy(), lay.copy()
        yy = np.mgrid[0:lay.shape[0], 0:lay.shape[1]][0]
        legs[yy < P + IDLE_LEG_ROW] = 0
        top[yy >= P + IDLE_LEG_ROW] = 0
        wx, wy = whole
        can = R.compose(self.rig, [(legs, dict(dx=wx, dy=wy)), (top, dict(dx=wx, dy=wy + crouch))])
        return R.flash(can) if flash else can


def close_cracks(can, outline, most=12):
    """Enclosed gaps of at most `most` squares a move opened (between a leg and the belt): the outline (gap-check)."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        if h.sum() <= most:
            out[h] = (*outline, 255)
    return out


def form():
    F = Form(design(), rig_pad=(40, 40, 40, 20))
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_graves.py) come from these
MS = {"idle": [160] * 8, "run": [115] * 8, "attack": [70, 60, 80, 80, 90, 70], "hit": [100, 100]}
# the walk: per frame the back leg's (dx, dy, lift), the front leg's, the body's rise (league_nautilus's 1x steps, at
# PPU 1.5 a step of 2 squares, a lift of 3)
WALK = [((0, 0, 2), (0, 0, 0), 1), ((2, 0, 3), (0, 0, 0), 1), ((2, 0, 1), (0, 0, 0), 0), ((2, 0, 0), (0, 0, 0), 0),
        ((0, 0, 0), (0, 0, 2), 1), ((0, 0, 0), (2, 0, 3), 1), ((0, 0, 0), (2, 0, 1), 0), ((0, 0, 0), (2, 0, 0), 0)]


def frames_all(F):
    p = F.pose
    out = {}
    # idle (League's graves_idle1: a slow breath, the gun still at the hip): the 3/4 design's body sets down a row
    out["idle"] = [F.front(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    out["run"] = [p(whole=(0, -r), back=b, front=f) for b, f, r in WALK]
    # auto attack (League's graves_attack1: the shot at ~0 ms, the gun kicked up by ~190 ms and pumped, level again by
    # ~1100 ms): aimed, the shot (the gun and his body kicked back a square), the pump (Codex's tilt pose when it
    # arrives; until then the gun pulled back), back to aim
    out["attack"] = [p(), p(whole=(-2, 0)), p(whole=(-2, 0)), p(whole=(-1, 0)), p(whole=(-1, 0)), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if not (a.audit or a.review or a.parts):
        F = form()
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            import rig_wukong as RW
            RW.HERO = HERO
            RW.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)


if __name__ == "__main__":
    main()
