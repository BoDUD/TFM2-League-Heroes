#!/usr/bin/env python3
"""tft_maddie's action frames: Maddie's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-27: sprites by Codex from written prompts, then 「Codex交付了 你做到完美后喊我review」).

    python tools/art/rig_maddie.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_maddie.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_maddie), then ppu_restyle.py / ppu_hd.py --hero maddie

The pictures (tools/art/design_maddie_model.py, design_maddie_poses.py):
  hd/idle.png         Maddie with the rifle on her shoulder, 3/4 facing right, 44 x 57 at PPU 1.5 (38 game px, the
                      beret to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head put in (assets/source/maddie/POSE_PROMPTS.md): a_aim
                      a_fire a_kick a_back q_crouch q_fire e_point r_aim r_fire run1-4 d_fall d_down.
Placing a pose: every pose stands on her HIPS - the middle column of her lavender trousers (TROUSERS: the design's two
lighter lavenders, in every pose; the feet's middle jumped 4-9 squares between her wide and narrow stances) goes on
the idle's (STAND), the lowest square on the ground row.
The muzzle flashes (Codex's a_flash / r_flash, tools/art/import_maddie_fx.py's source) are drawn into the frame a shot
leaves - pointing right, they cannot be effects (the client never mirrors an effect picture: SKILL.md "Both sides") -
as the frame's "over" layer (ppu_restyle lays it on after the outline): its left edge one square ahead of the muzzle
(the figure's rightmost square), its middle row on the muzzle's, at PPU (each game px 1.5 squares, nearest).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "maddie"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "maddie", "hd")
FLASH = os.path.join(ROOT, "assets", "source", "maddie", "codex_fx", "pixel_1x")
TROUSERS = ((160, 155, 191), (114, 104, 147))
FLASHES = {"a_flash": (14, 10), "r_flash": (30, 20)}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def hips_x(d):
    """The middle column of her trousers' squares."""
    m = np.zeros(d.shape[:2], bool)
    for c in TROUSERS:
        m |= (d[..., 3] > 0) & np.all(d[..., :3] == c, axis=-1)
    _, xs = np.nonzero(m)
    return float(xs.mean())


def flash_frames(name):
    """A muzzle flash's frames at PPU (nearest), pointing right."""
    w, h = FLASHES[name]
    a = np.asarray(Image.open(lp(os.path.join(FLASH, f"maddie_fx_{name}.png"))).convert("RGBA"))
    out = []
    for k in range(a.shape[1] // w):
        c = Image.fromarray(a[:, k * w:(k + 1) * w].copy())
        out.append(np.asarray(c.resize((round(w * PPU), round(h * PPU)), Image.NEAREST)).copy())
    return out


def muzzle(can):
    """The muzzle on a canvas: (the rightmost opaque column, the middle row of its squares in the two rightmost)."""
    op = can[..., 3] > 0
    xs = np.nonzero(op.any(0))[0]
    x1 = xs.max()
    ys = np.nonzero(op[:, x1 - 1:x1 + 1].any(1))[0]
    return int(x1), float(ys.mean())


STAND = None                                # the idle's hips_x, set by Canvas


class Canvas:
    def __init__(self):
        global STAND
        self.d = load("idle.png")
        d = self.d
        STAND = hips_x(d)
        self.flashes = {n: flash_frames(n) for n in FLASHES}

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], int(round(STAND)), d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(40, 90, 24, 8))        # room for the rifle aimed ahead, kicked up, the flashes
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas): its hips on the idle's."""
        rig = self.rig
        d = self.d if name == "idle" else load(f"pose_{name}.png")
        ground = d.shape[0]
        return d, (rig.ox + int(round(STAND - hips_x(d))) + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False, muzzle_flash=None):
        """A pose on the canvas; flash = the hit's whitening; muzzle_flash = (flash name, its frame) as the over layer."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        can = R.flash(can) if flash else can
        if not muzzle_flash:
            return can
        fname, k = muzzle_flash
        f = self.flashes[fname][k]
        mx, my = muzzle(can)
        over = rig.canvas()
        fy, fx = np.nonzero(f[..., 3] > 0)
        oy = fy + int(round(my - (f.shape[0] - 1) / 2))
        ox = fx + mx + 1
        ok = (oy >= 0) & (oy < rig.CH) & (ox >= 0) & (ox < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: the {fname} flash runs off the canvas (pad the rig)")
        over[oy, ox] = f[fy, fx]
        return {"body": can, "over": over}


# ms per frame; the kit's ticks (tools/kit/build_maddie.py) match these (a frame's start in ticks = ms x 0.06):
# attack 400 ms = atk_dur 24, the bullet leaves on a_rel 7 (100 ms: the shot's frame, the flash); Fan the Hammer
# 1100 ms = q_dur 66: the crouch 150 ms, then six shots q_gap 8 ticks (133 ms) apart from q_rel 10 (150 ms), each a
# flash frame (67 ms) and a plain one, then back up; Wanted 500 ms = e_dur 30, the mark on e_rel 7 (100 ms: the arm
# thrust out); the snipe 1500 ms = r_dur 90: the crouch, the long aim, the shot on r_rel 66 (1100 ms: the blast), the
# kick, back up
MS = {"idle": [1000], "run": [150] * 4, "attack": [100, 100, 100, 100],
      "skill": [150] + [67, 66] * 6 + [150], "skill2": [100, 400], "ult": [150, 950, 100, 200, 100],
      "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # the run (her run clip: a low jog, the rifle across her hips)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (her TFT shot: aim from the hip, the shot and its flash, the kick throwing the muzzle up, level again)
    out["attack"] = [f("a_aim"), f("a_fire", muzzle_flash=("a_flash", 0)), f("a_kick"), f("a_back")]
    # Fan the Hammer (her spell: down into a half crouch, the stock at her shoulder, six shots - a flash on each, the
    # second and later shots' flashes alternating the flash's first two frames - then up)
    shots = []
    for k in range(6):
        shots += [f("q_fire", dx=-1, muzzle_flash=("a_flash", k % 2)), f("q_fire")]
    out["skill"] = [f("q_crouch")] + shots + [f("a_back")]
    # Wanted (the rifle stays on her shoulder, the other arm thrust out at the target)
    out["skill2"] = [f("idle"), f("e_point")]
    # the snipe (crouched, the long steady aim, the blast, the big kick, level again)
    out["ult"] = [f("q_crouch"), f("r_aim"), f("r_aim", dx=-1, muzzle_flash=("r_flash", 0)), f("r_fire"),
                  f("a_back")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (her death: thrown back off her feet, the rifle flying, down on her back)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down"), f("d_down")]
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
