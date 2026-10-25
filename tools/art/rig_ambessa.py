#!/usr/bin/env python3
"""league_ambessa's action frames: Ambessa's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-25: the pose pack built with League's own frames, then 「安倍萨的动作帧交付了 你做到完美后喊我review」).

    python tools/art/rig_ambessa.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_ambessa.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_ambessa_model.py, design_ambessa_poses.py):
  hd/idle.png         Ambessa, 3/4 front facing right, 117 x 96 at PPU 2.0 (48 game px hair to soles, the blades out
                      to her sides): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/ambessa/POSE_PROMPTS.md): a1_wind a1_slash a2_wind a2_slash q_wind q_sweep q2_leap
                      q2_slam w_guard w_slam e_lash1 e_lash2 step r_grab r_slam run1-4 d_kneel d_slump.
Placing a pose (rig_yorick's way): its head box (the design's head, pasted) stands where the design's head stands,
moved as far as League's head moves in that frame (the pose pack's skeleton: HEAD_DX, rounded) and dx squares more by
hand; its soles on the ground row (its lowest square: the boots, or a blade's tip laid on the ground), or `lift` rows
over it (Sundering Slam's leap). The idle is the design alone (no breathing: hero_reels cuts the idle snippets from
these actions).
Two effects with a front and a back are drawn into her own frames (the client never mirrors an effect picture: the
skill's tfm2-hero-mod rule; tools/art/pack_ambessa_fx.py FORWARD): Cunning Sweep's half circle (q_sweep, over her, in
front) on the sweep, Drakehound's Step's speed streaks (st_dash, under her, behind) on the step - the Gemini half of the
effects read back by tools/art/read_ambessa_gemini.py, each game px PPU x PPU squares, laid in BAKE's frames.
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
import pack_ambessa_poses as PK  # noqa: E402
import design_ambessa_poses as DP  # noqa: E402

HERO = "ambessa"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "ambessa", "hd")
FXSRC = os.path.join(ROOT, "assets", "source", "ambessa", "gemini_fx", "pixel_1x")
STAND = 63                     # the idle's standing column: under her sash, between her boots
HEAD = (DP.HEAD[2], DP.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far League's head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, spec) in PK.POSES.items()}
LIFT = {"q2_leap": 10}                     # rows the lowest square stands over the ground (the pose pack's lift)


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


def fx_cells(name):
    """The baked effect's frames at game size (read_ambessa_gemini's strip and manifest)."""
    man = json.load(open(lp(os.path.join(os.path.dirname(FXSRC), "manifest.json")), encoding="utf-8"))
    e = next(x for x in man if x["file"] == f"ambessa_fx_{name}.png")
    a = np.asarray(Image.open(lp(os.path.join(FXSRC, e["file"]))).convert("RGBA"))
    w, h = e["cell_1x"]
    return [a[:h, k * w:(k + 1) * w].copy() for k in range(e["frames"])]


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(90, 90, 70, 12))      # room for the blades flung out on their chains, raised, lying
        self.outline = D.outline

    def placed(self, name, dx=0, lift=None):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX[name]
        lift = LIFT.get(name, 0) if lift is None else lift
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=None, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can

    def fx_layer(self, cell, at):
        """An effect frame (game px) on a canvas-sized layer: each game px PPU x PPU squares (nearest), its top-left
        `at` game px from the standing point (x forward, y down from the ground)."""
        rig = self.rig
        h, w = cell.shape[:2]
        H, W = int(round(h * PPU)), int(round(w * PPU))
        yy = np.minimum((np.arange(H) / PPU).astype(int), h - 1)
        xx = np.minimum((np.arange(W) / PPU).astype(int), w - 1)
        big = cell[yy][:, xx]
        lay = rig.canvas()
        x0, y0 = int(round(rig.CX + at[0] * PPU)), int(round(rig.GY + at[1] * PPU))
        ys, xs = np.nonzero(big[..., 3] > 0)
        ok = (ys + y0 >= 0) & (ys + y0 < rig.CH) & (xs + x0 >= 0) & (xs + x0 < rig.CW)
        lay[ys[ok] + y0, xs[ok] + x0] = big[ys[ok], xs[ok]]
        return lay


# ms per frame; the kit's ticks (tools/kit/build_ambessa.py) match these (a frame's start in ticks = ms x 0.06):
# attack 433 ms = atk_dur 26, the first blade landing on the first slash (a_hit 10 = 167 ms), the second blade after it
# (League's alternating twin blades in one swing); Q 400 ms = q_dur 24: wound up, the sweep from 150 ms (q_hit 10 =
# 167 ms; Drakehound's Step st_gap 8 after it); Q2 400 ms = q2_dur 24: the leap, slammed down at 183 ms (q2_hit 12 =
# 200 ms); E 400 ms = e_dur 24: the chains flung out, swung round at 167 ms (e_hit 10); W 600 ms = w_dur 36: braced until
# the slam at w_brace 24 (400 ms); R 800 ms = r_dur 48: the lunge, the victim hoisted from the blink (r_go 8 = 133 ms),
# slammed down at 617 ms (r_go - 1 + r_slam 30 = 37 ticks); the step 167 ms = st_dur 10
MS = {"idle": [1000], "run": [150] * 4, "attack": [117, 116, 84, 116], "skill": [150, 250], "slam": [183, 217],
      "skill2": [167, 233], "w": [400, 200], "ult": [133, 484, 183], "step": [167], "hit": [100, 100],
      "dead": [140, 260, 300, 600]}
# effects drawn into her frames: tag -> (picture, the pose frame it starts on, ms of each effect frame, top-left game px
# from the standing point, "over" | "under")
BAKE = {"skill": ("q_sweep", 1, [40, 50, 70, 90], (9, -46), "over"),
        "step": ("st_dash", 0, [40, 40, 40, 47], (-42, -19), "under")}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's RunBase: the far foot landing, passing, the near foot landing, passing; the blades trailing)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack1 then Attack2: the near blade swung up and cut down, the far blade raised and swept across)
    out["attack"] = [f("a1_wind"), f("a1_slash"), f("a2_wind"), f("a2_slash")]
    # Cunning Sweep (Spell1A: crouched, the chains swung out, then flung wide as she rises into the sweep)
    out["skill"] = [f("q_wind"), f("q_sweep")]
    # Sundering Slam (Spell1B: the leap with the blades high, the slam)
    out["slam"] = [f("q2_leap"), f("q2_slam")]
    # Lacerate (Spell3: the chains flung out to both sides, whirled round)
    out["skill2"] = [f("e_lash1"), f("e_lash2")]
    # Repudiation (Spell2: braced behind the raised blade, the slam into the ground)
    out["w"] = [f("w_guard"), f("w_slam")]
    # Public Execution (Spell4: the lunge, the victim hoisted, slammed down)
    out["ult"] = [f("step"), f("r_grab"), f("r_slam")]
    # Drakehound's Step (PassiveDash: the lunge forward, the chains trailing)
    out["step"] = [f("step")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: struck down onto her knees, slumped forward)
    out["dead"] = [f("d_kneel", flash=True), f("d_kneel"), f("d_slump"), f("d_slump")]
    return out


def bake(C, tag, fr):
    """The tag's frames with its BAKE effect laid in: the pose frame `start` cut into the effect's frames (ms each),
    the rest of that pose frame after them; -> [(canvas or {"body", "over", "under"}, ms)]."""
    if tag not in BAKE:
        return fr
    pic, start, ms, at, key = BAKE[tag]
    cells = fx_cells(pic)
    if len(cells) < len(ms):
        sys.exit(f"{tag}: {pic} has {len(cells)} frames for {len(ms)}")
    body, total = fr[start]
    if sum(ms) > total:
        sys.exit(f"{tag}: {pic} runs {sum(ms)} ms on a {total} ms frame")
    cut = []
    for cell, m in zip(cells, ms):
        cut.append(({"body": body, key: C.fx_layer(cell, at), ("under" if key == "over" else "over"): None}, m))
    if total - sum(ms) > 0:
        cut.append((body, total - sum(ms)))
    return fr[:start] + cut + fr[start + 1:]


def frames(C, tags=None):
    out = {}
    for tag, cans in actions(C).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = bake(C, tag, list(zip(cans, ms)))
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
