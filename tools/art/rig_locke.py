#!/usr/bin/env python3
"""league_locke's action frames: Locke's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-26: actions and effects by Codex, then 「codex都交付了 动作帧和技能特效 你做到完美了喊我review」).

    python tools/art/rig_locke.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_locke.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_locke_model.py, design_locke_poses.py):
  hd/idle.png         Locke, 3/4 front facing right, 54 x 88 at PPU 2.0 (44 game px hair to soles): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/locke/POSE_PROMPTS.md): a_wind a_stab q_raise q_throw w_hunch w_spread e_blink
                      e_dash r_swing r_throw run1-4 d_fall d_down.
Placing a pose (rig_trundle's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as League's head moves in that frame (the pose pack's skeleton: HEAD_DX, rounded) and dx squares more by hand;
its soles on the ground row (its lowest square), or `lift` rows over it. The idle is the design alone (no breathing:
hero_reels cuts the idle snippets from these actions).
His W look (Soul Ignition: step 0's B colours - blue-violet skin, a white suit, glowing lenses, a blue crystal case) is
every frame recoloured square for square (W_LOOK: the design's colours, material by material, after the A-2 / B-2 pair
of step 0), in `w_<tag>` tags the add-on (addons/league_locke/src/view.rs) plays while `league_locke_w_on` lasts; the
ignition itself (`w`) turns from the plain hunch to the W look as his arms spread.
"""
import argparse
import json
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
import pack_locke_poses as PK  # noqa: E402

HERO = "locke"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "locke", "hd")
STAND = 33                     # the idle's standing column: under his belt buckle, between his feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far League's head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}
LIFT = {"w_spread": 6, "e_dash": 10}       # rows off the ground: rising in the ignition, flying in the dash
# the design's colours -> his W look (material by material, each ramp keeping its light-to-dark order; matched on step
# 0's A-2 / B-2 pair, the same pose in both looks)
W_LOOK = {
    "0c020b": "0c020b",
    # the case: charcoal -> a deep blue crystal; its bands and studs -> bright cyan edges
    "252329": "141aa8", "4a253f": "2b5ce8", "5a1c5c": "38cbfc", "833880": "8fe8ff", "505459": "c4ebf4",
    # the coat: dark teal -> pale lilac, mid -> near white, cuffs and silver ribbons -> white, bluish -> pale cyan
    "243539": "b8b2e8", "2d5057": "e6e4fa", "618186": "ccc8f0", "9bb7b5": "f6f7fc", "7989a5": "c4ebf4",
    # the shirt: royal blue -> glowing bright blue
    "12176a": "1a3cf0", "092da4": "2f8cff", "53568e": "8a86d8",
    # skin: warm -> blue-violet, light to dark
    "fbc692": "5a46ee", "ec9b65": "4632d6", "dd8451": "3a26bc", "c38e68": "3a26bc", "bf613a": "2a1a98", "964126": "1d1270",
    # hair: gold -> deep indigo, the light golds -> bright blue strands, the highlight -> cyan
    "99702b": "0c0a4a", "714825": "0c0a4a", "ccac49": "13149e", "f9ec83": "1f3df8", "fbf39d": "2f6cfc", "fcf5c9": "36b6fc",
    # lenses: magenta -> glowing white
    "b60480": "ffffff", "8d056d": "e8f4ff",
    "e4f1f2": "ffffff",
    # belt and pouches: purple-brown -> lilac / indigo
    "714452": "8a86d8", "482a1a": "1d1972", "18153a": "0c0a4a",
}
W_TAGS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dash")   # the add-on's view.rs FORM_TAGS


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(meta.get("ground", ys.max() + 1))


def w_look(can):
    """A frame in his W colours (W_LOOK); a colour not in the table (none in the design's palette) stays."""
    lut = {tuple(int(k[i:i + 2], 16) for i in (0, 2, 4)): tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
           for k, v in W_LOOK.items()}
    out = can.copy()
    op = can[..., 3] > 0
    cols = np.unique(can[op][:, :3], axis=0)
    for c in cols:
        t = lut.get(tuple(int(v) for v in c))
        if t is not None:
            m = op & np.all(can[..., :3] == c, axis=-1)
            out[m, :3] = t
    return out


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(60, 60, 40, 14))      # room for the case swung up and out, the ribbons behind, the dash
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX[name]
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=None, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, LIFT.get(name, 0) if lift is None else lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_locke.py) match these (a frame's start in ticks = ms x 0.06):
# attack 400 ms = atk_dur 24, the stab on atk_st 8 (133 ms); Ritual Nails 500 ms = q_dur 30, the first nail thrown on
# q_at 8 (133 ms), the others q_gap 6 apart; Ashen Pursuit's landing 267 ms = e_dur 16; the pursuit's dash 233 ms; the
# Soul Ignition (tag `w`) 333 ms = w_dur 20; Purgatory 500 ms = r_dur 30, the case let go on r_rel 14 (233 ms)
MS = {"idle": [1000], "run": [125] * 4, "attack": [133, 167, 100], "skill": [133, 267, 100], "skill2": [267],
      "dash": [233], "w": [133, 200], "ult": [233, 267], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run_Fast: contact, passing, contact on the other leg, passing; the case on his back)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack_02_L / Attack_01_R: the nail drawn back by his shoulder, stabbed forward in a lunge, back)
    out["attack"] = [f("a_wind"), f("a_stab"), f("idle")]
    # Ritual Nails (Spell1: the nails raised over his head, flung forward, back)
    out["skill"] = [f("q_raise"), f("q_throw"), f("idle")]
    # Ashen Pursuit (Spell3_Blink: landing low out of the ash next to the champion)
    out["skill2"] = [f("e_blink")]
    # the pursuit (Spell3_Dash: the next attack after E, flying flat through the target)
    out["dash"] = [f("e_dash")]
    # Soul Ignition (Spell2, the passive's W after E lands by a champion: hunched gripping the nail, rising arms spread
    # in his W look)
    out["w"] = [f("w_hunch"), w_look(f("w_spread"))]
    # Purgatory (Spell4: the case swung off his back on its strap, flung high)
    out["ult"] = [f("r_swing"), f("r_throw")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: knocked back, the nail flying; sitting slumped against the case)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down"), f("d_down")]
    # his W look: the same frames recoloured (the hit's flash recoloured after the flash: the same white)
    for tag in W_TAGS:
        out["w_" + tag] = [w_look(c) for c in out[tag]]
    return out


def frames(C, tags=None):
    out = {}
    for tag, cans in actions(C).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag[2:] if tag.startswith("w_") else tag]
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
