#!/usr/bin/env python3
"""league_neeko's action frames: her approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-21: 「Codex 画关键姿势」, then 「动作包也交付了 你收尾吧」).

    python tools/art/rig_neeko.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_neeko.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (PPU 2.5, one palette; tools/art/design_neeko_model.py and design_neeko_poses.py):
  hd/idle.png         her, 3/4 front facing right, 49 x 100 (40 game px): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head pasted on
                      (assets/source/neeko/POSE_PROMPTS.md): stance thrust kick pounce tuck throw_air coil fling hunch
                      soar land run1-4 twirl sit.
Placing a pose: its head box goes where the pose's skeleton planned it (tools/art/pack_neeko_poses.py builds the same
skeletons: the head box over the neck, the neck along the spine from the pelvis) - so a lunge carries her head forward,
a crouch takes it down, and the head never jumps from what the skeleton had (league_shyvana's lesson: feet anchoring
made the torso jump); the lowest square stands on the ground, or `lift` squares over it in the air. Blooming Burst's
somersault is the tuck turned by quarter turns about its middle (lossless), clockwise as she flips forward.
The idle breathes: the rows above her hips (and her hair) set down a row, the legs and the tail stay.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
a key pose with a part of it moved (PARTS, boxes in the pose's own squares): her long tail waved from where it leaves
her (its columns lifted or lowered, more toward the tip), never past the leg or the arm drawn over it; the design's head
the pose carries and everything else of the pose checked unchanged.
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
import inbetween as IB  # noqa: E402
import pixel_down as PD  # noqa: E402
import pack_neeko_poses as PK  # noqa: E402

HERO = "neeko"
PPU = 2.5
SRC = os.path.join(ROOT, "assets", "source", "neeko", "hd")
STAND = 29                     # the idle's standing column: between her feet, under the middle of her body
HEAD = (PK.HEAD[2], PK.HEAD[0])   # the head box's top-left square in hd/idle.png (columns 4.., rows 0..)
HEAD_WH = (PK.HW, PK.HH)          # its size (45 x 41: the quills to the chin, the hair at both sides)
VPAD = 30                         # an in-between's picture is this much bigger on every side (inbetween.vary)
BREATH_ROW = 62                # rows above this breathe (her hair reaches down to row 41 at both sides) ...
HIP_ROW = 70                   # ... and right of the tail (column 18) down to her hips
TAIL_COL = 18


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def head_at(name):
    import json
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


def planned_head(name):
    """The head box's top-left (design squares, x right, y down; the idle's at HEAD) where the pose's skeleton puts it."""
    sk = PK.build(PK.POSES[name][3])
    hx, hy = sk["head"]
    return hx - PK.HW / 2.0, hy - PK.HH / 2.0


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        self.poses = {n[5:-4]: load(n) for n in sorted(os.listdir(lp(SRC))) if n.startswith("pose_") and n.endswith(".png")}
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(100, 100, 100, 12))   # room for the lunge, the long tail and the leap
        self.outline = D.outline

    def stamp(self, can, a, x0, y0):
        ys, xs = np.nonzero(a[..., 3] > 0)
        ty, tx = ys + y0, xs + x0
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        can[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
        return can

    def place(self, name, dx=0, lift=0, breath=0, turn=0):
        """(picture, its top-left canvas square) for the design ('idle') or a pose; `turn` quarter turns clockwise
        about the picture's middle (the tuck's somersault)."""
        ox, GY = self.rig.ox, self.rig.GY
        if name == "idle":
            a = breathe(self.d, breath) if breath else self.d
            x0 = ox + dx
            ys = np.nonzero(a[..., 3] > 0)[0]
            return a, x0, GY - 1 - ys.max() - lift
        a = self.poses[name]
        hx, _ = head_at(name)
        px, _ = planned_head(name)
        x0 = int(round(ox + px - hx)) + dx
        ys = np.nonzero(a[..., 3] > 0)[0]
        y0 = GY - 1 - ys.max() - lift
        if turn:
            cy, cx = y0 + a.shape[0] / 2.0, x0 + a.shape[1] / 2.0
            a = np.rot90(a, -turn).copy()
            x0, y0 = int(round(cx - a.shape[1] / 2.0)), int(round(cy - a.shape[0] / 2.0))
        return a, x0, y0

    def head(self, name, a):
        """The design's head as pose `name` carries it: the head box's squares the pose holds unchanged."""
        (x0, y0), (w, h) = HEAD, HEAD_WH
        hx, hy = head_at(name)
        box = self.d[y0:y0 + h, x0:x0 + w]
        sub = a[hy:hy + h, hx:hx + w]
        m = np.zeros(a.shape[:2], bool)
        h, w = sub.shape[:2]
        m[hy:hy + h, hx:hx + w] = (box[:h, :w, 3] > 0) & (sub == box[:h, :w]).all(-1)
        return m

    def frame(self, name, dx=0, lift=0, breath=0, turn=0, flash=False, moves=(), sway=(), spins=()):
        """The pose placed as place() puts it; moves / sway / spins (inbetween.vary, by PARTS' names): an in-between
        made from it, placed where the pose stands (every square in no part checked unchanged)."""
        can = self.rig.canvas()
        a, x0, y0 = self.place(name, dx, lift, breath, turn)
        if moves or sway or spins:
            a = IB.vary(a, PARTS[name], self.outline, moves, sway, None, self.head(name, a), VPAD, name, spins=spins)
            x0, y0 = x0 - VPAD, y0 - VPAD
        self.stamp(can, a, x0, y0)
        return hit_white(can) if flash else can


def breathe(a, k):
    """Her body above the hips set down k rows: everything above BREATH_ROW, and right of the tail down to HIP_ROW; the
    legs and the tail (left of TAIL_COL under BREATH_ROW) stay."""
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    moving = (yy < BREATH_ROW) | ((yy < HIP_ROW) & (xx >= TAIL_COL))
    top = np.where(moving[..., None], a, 0).astype(np.uint8)
    out = np.where(moving[..., None], 0, a).astype(np.uint8)
    sh = np.zeros_like(top)
    sh[k:] = top[:H - k]
    m = sh[..., 3] > 0
    out[m] = sh[m]
    return out


def hit_white(can, k=0.45):
    """ppu_rig.flash keeping the outline dark (rig_shyvana.hit_white)."""
    import strips
    out = can.copy()
    m = (out[..., 3] > 0) & (strips.lum(out[..., :3]) >= 70)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- the in-betweens
# the tail of each pose that is waved (boxes (x0, y0, x1, y1), inclusive, in the pose's own squares): only the free
# length of it, cut square across where nothing else lies next to it - the leg or the arm drawn over its root stays
# where it is, and so does the root
PARTS = {
    "stance": {"tail": [(0, 55, 35, 99)]},           # left of the near boot, the tip out behind her
    "thrust": {"tail": [(0, 56, 44, 99)]},           # left of the near leg
    "pounce": {"tail": [(0, 0, 44, 66)]},            # raised behind her, left of the quills
    "land": {"tail": [(0, 0, 46, 74)]},              # raised over her back
    "fling": {"tail": [(63, 56, 116, 82)]},          # thrown out to the right under the far arm
    "hunch": {"tail": [(0, 0, 46, 40)]},             # the curl over her back
    "soar": {"tail": [(0, 40, 21, 80)]},             # hanging under her, its tip curled up
    "twirl": {"tail": [(58, 60, 85, 90)]},           # swung out to the right
    "sit": {"tail": [(0, 68, 20, 101)]},             # the loop behind her on the ground
    # the run's curl and the tail under it down to the back foot (left of where the tail runs on to her hip)
    "run1": {"tail": [(0, 30, 22, 68)]}, "run2": {"tail": [(0, 30, 22, 75)]}, "run3": {"tail": [(0, 28, 22, 68)]},
    "run4": {"tail": [(0, 41, 22, 77)]},
}
RUN_SWAY = (2, 5, 5, 2, -2, -5, -5, -2)  # the run's curl tip, rows up, a frame (once a cycle; new legs every two)


def tail(x0, x1, k, attach="right"):
    """The tail's columns x0..x1 lifted 0..k rows (negative: lowered), none where it stays attached (inbetween.wave)."""
    return [("tail", x0, x1, k, attach)]


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_neeko.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27, the bolt from the thrust at 100 ms -> a_rel 10 (tick 9 = 150 ms, inside it); attack_w
# the same length, the bolt from the pounce at 140 ms; skill 500 ms = q_dur 30, the seed from the throw at 220 ms ->
# q_rel 14; skill2 500 ms = e_dur 30, the barbs from the fling at 170 ms -> e_rel 11; ult 750 ms = r_charge 45 (the
# charge); ult_b 500 ms = r_dur 30 (the leap: the dash and the landing burst come at the kit's own time)
# The in-betweens (2026-11-14: the attack was the stance, the thrust and its copy moved a square, the stance; E's fling
# and the death's sitting pose were held twice): the spans shared out over more frames (inbetween.spans: whole ms, none
# under 50), so every action is as long as it was and the thrust still starts at 100, the pounce at 140, the fling at
# 170, the sit at 300.
MS = {"idle": [150] * 8, "run": [60] * 8, "attack": IB.spans((100, 2), (230, 2, (110, 120)), (120, 2)),
      "attack_w": IB.spans((140, 1), (210, 2, (110, 100)), (100, 2)),
      "skill": [60, 40, 40, 40, 40, 110, 90, 80], "skill2": IB.spans((170, 2, (90, 80)), (220, 2), (110, 2)),
      "ult": [90, 160, 170, 160, 170], "ult_b": [60, 60, 60, 160, 160], "hit": [100, 100],
      "dead": IB.spans((120, 1), (180, 2), (300, 2), (600, 1))}
LIFT = {name: (spec[3]["lift"] or 0) for name, spec in PK.POSES.items()}


def actions(C):
    f = C.frame
    breaths = (0, 0, 1, 1, 1, 1, 0, 0)
    out = {}
    # idle (League's idle1: she stands, hands together before her chest, breathing)
    out["idle"] = [f("idle", breath=b) for b in breaths]
    # run (League's Run: the four phases of the bounding run, the tail curled behind and swaying up and down: each
    # drawing held two frames as before - 120 ms - the curl moving every 60)
    out["run"] = [f(f"run{i // 2 + 1}", lift=LIFT[f"run{i // 2 + 1}"], sway=tail(0, 22, k))
                  for i, k in enumerate(RUN_SWAY)]
    # attack (League's Attack1: the low stance, springing forward with the near arm thrust out - the bolt - held,
    # back down)
    # (the tail's tip lifting as she gathers, trailing low as she comes down out of the thrust and settling)
    out["attack"] = [f("stance"), f("stance", sway=tail(0, 35, 6)), f("thrust", lift=LIFT["thrust"]),
                     f("thrust", dx=1, lift=LIFT["thrust"] - 2, sway=tail(0, 44, -6)),
                     f("stance", sway=tail(0, 35, -4)), f("stance")]
    # the third attack (League's Passive_attack: the high kick, the low pounce - the empowered bolt - held with the
    # raised tail swinging down, back with it still coming down)
    out["attack_w"] = [f("kick"), f("pounce"), f("pounce", dx=1, sway=tail(0, 44, -6)),
                       f("stance", sway=tail(0, 35, 6)), f("stance")]
    # Q Blooming Burst (League's Spell1: down in the stance, the somersault - the tuck turned a quarter at a time,
    # rising - the throw in the air (the seed), landing, back)
    t = LIFT["tuck"]
    out["skill"] = [f("stance"), f("tuck", lift=t - 2), f("tuck", lift=t + 4, turn=1), f("tuck", lift=t + 6, turn=2),
                    f("tuck", lift=t + 3, turn=3), f("throw_air", lift=LIFT["throw_air"]), f("land"), f("stance")]
    # E Tangle-Barbs (League's Spell3: the spin in the air with the tail round her, the fling - the barbs - held,
    # back down)
    # (the tail thrown out with the barbs whipping on, back down with the tail settling)
    out["skill2"] = [f("coil", lift=LIFT["coil"]), f("coil", lift=LIFT["coil"] + 2), f("fling"),
                     f("fling", sway=tail(63, 116, 6, "left")), f("stance", sway=tail(0, 35, -4)), f("stance")]
    # R Pop Blossom, the charge (League's channel_wndup: down into the hunch, gathering - rocking a square back and
    # forth in it, the feet on the ground)
    # (the curl over her back pumping up and down with the rocking)
    out["ult"] = [f("stance"), f("hunch"), f("hunch", dx=-1, sway=tail(0, 46, 5)), f("hunch", sway=tail(0, 46, -3)),
                  f("hunch", dx=-1, sway=tail(0, 46, 3))]
    # R Pop Blossom, the leap (League's Spell4: up out of the crouch, high, coming down, the landing held)
    s = LIFT["soar"]
    # (the hanging tail trailing down as she rises and flipping up as she comes down; the raised tail coming down
    # after the landing)
    out["ult_b"] = [f("soar", lift=s - 2), f("soar", lift=s + 20, sway=tail(0, 21, -5)),
                    f("soar", lift=s + 10, sway=tail(0, 21, 5)), f("land"), f("land", sway=tail(0, 46, -6))]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: the twirl with the tail swinging round, sinking down to sit, the tail's loop settling on
    # the ground)
    out["dead"] = [f("twirl", dx=-1, flash=True), f("twirl", dx=-2, sway=tail(58, 85, 6, "left")),
                   f("twirl", dx=-2, sway=tail(58, 85, -5, "left")), f("sit", sway=tail(0, 20, 5)),
                   f("sit", sway=tail(0, 20, 2)), f("sit")]
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
