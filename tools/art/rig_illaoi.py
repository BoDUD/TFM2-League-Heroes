#!/usr/bin/env python3
"""league_illaoi's action frames and her tentacle's sheets: her approved 3/4 design and Codex's key poses after League's
clips (the user, 2026-10-23: 「动作帧让 Codex 照骨架画姿势」, then 「你做到完美版本后再喊我review」).

    python tools/art/rig_illaoi.py --review DIR      # every tag at 3x + a GIF per tag, the tentacle's too (nothing written)
    python tools/art/rig_illaoi.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet;
                                                     # the tentacle's dense sheets -> league/effects/league_illaoi_tentacle
                                                     # and league_illaoi_lash

The pictures (tools/art/design_illaoi_model.py, design_illaoi_poses.py):
  hd/idle.png             her, 3/4 front facing right, 52 x 68 at PPU 1.5 (42 game px bun to soles): the idle, the hit;
  hd/pose_<name>.png      Codex's key poses read back at the design's size with the design's head put in
                          (assets/source/illaoi/POSE_PROMPTS.md; the long-legged ones' and the runs' legs drawn again in
                          LEGS_PROMPTS.md): a_raise a_slam w_jump w_land e_thrust e_yank r_crouch r_leap r_slam run1-4
                          d_stagger d_slump;
  hd/tentacle.png         the tentacle from the front, 33 x 66 at PPU 1.5 (44 game px);
  hd/tentacle_<name>.png  its poses on their own grids: tn_rise tn_grow tn_sway tn_rear tn_slam tn_recoil tn_sink.
Placing a pose (league_ivern's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares, its soles on the ground row (its lowest square) or `lift` rows over it. The idle is the design alone
(no breathing: hero_reels cuts her idle snippets from these actions).
The tentacle is an effect picture (tools/kit/build_illaoi.py: views tentacle and lash; league_heimerdinger's turrets):
each a dense sheet holding idle (1x) and hd_idle (PPU 1.5, league_main hd.rs EFFECTS). `tentacle` is one life on the
spot it grew (rising, swaying, sinking back) as long as the kit's t_life; `lash` is a tentacle rearing and slamming down
on the unit it strikes, standing LASH_BACK game px behind it. Their pictures are drawn as stored on both sides (the
client never mirrors an effect), so they are the front view.
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402
import pack_illaoi_poses as PK  # noqa: E402
from build_illaoi import P as KIT  # noqa: E402

HERO = "illaoi"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "illaoi", "hd")
MOD = os.path.join(ROOT, "league")
STAND = 29                     # the idle's standing column: under her middle, between her boots
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
T_PPU = 1.5                    # the tentacle's sheets (the user's pick: 44 game px at PPU 1.5)
LASH_BACK = 4                  # game px the striking tentacle's root stands behind (over) the unit's soles
FEET = R.FEET


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


# squares put right after the readback: (x0, y0, x1, y1) boxes on hd/pose_<name>.png whose tattoo teal goes back to the
# skin round it - Codex drew e_yank's spiral tattoo on her FAR arm (the design has it on the near, bracer arm)
PIXFIX = {"e_yank": [(5, 24, 15, 32)]}


def untattoo(d, box):
    """The tattoo's squares in box (greener than red, not the outline) take the commonest skin colour among their
    neighbours."""
    x0, y0, x1, y1 = box
    f = d[..., :3].astype(int)
    teal = (f[..., 1] > f[..., 0] + 8) & (f[..., :3].sum(-1) > 90) & (d[..., 3] > 0)   # greener than red: not skin
    skin = (f[..., 0] > 80) & (f[..., 0] > f[..., 1]) & (f[..., 1] > f[..., 2]) & (d[..., 3] > 0)
    out = d.copy()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not teal[y, x]:
                continue
            near = [tuple(d[j, i, :3]) for j in range(y - 2, y + 3) for i in range(x - 2, x + 3)
                    if 0 <= j < d.shape[0] and 0 <= i < d.shape[1] and skin[j, i]]
            if near:
                out[y, x, :3] = max(set(near), key=near.count)
    return out


def load_pose(name, prefix="pose_"):
    d = load(f"{prefix}{name}.png")
    for box in PIXFIX.get(name, []) if prefix == "pose_" else []:
        d = untattoo(d, box)
    with open(lp(os.path.join(SRC, f"{prefix}{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(meta.get("ground", ys.max() + 1))


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(70, 70, 50, 12))      # room for the idol swung out, held up, flying off
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name)
        return d, (rig.ox + HEAD[0] - hx + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False):
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


def ms_of(tick):
    return round(tick * 1000 / 60)


# ms per frame; the kit's ticks (tools/kit/build_illaoi.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the idol landing on the slam frame (a_hit 14 = 233 ms; the slam from 200 ms);
# Harsh Lesson 500 ms = w_dur 30, the leap from the cast (w_dash 12 = 200 ms, in the air to 300 ms), landing pressed;
# Test of Spirit 500 ms = e_dur 30, the ghost tentacle off the idol thrust out (e_rel 12 = 200 ms; the thrust to 250 ms),
# then the yank; Leap of Faith 667 ms = r_dur 40, the crouch, the leap, the idol smashed down (r_at 26 = 433 ms; the
# slam from 430 ms)
MS = {"idle": [1000], "run": [140] * 4, "attack": [200, 150, 100, 50], "skill": [120, 180, 200],
      "skill2": [250, 250], "ult": [150, 280, 237], "hit": [100, 100], "dead": [140, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run1: contact, passing, contact on the other leg, passing; the idol carried low at her side). The
    # head over the ground row 61 / 62 / 61 / 62 (the readbacks stand it at 59 / 60 / 61 / 61: Codex's legs differ by a
    # row or two), so the head bobs a row, the passing frames higher
    out["run"] = [f("run1", lift=2), f("run2", lift=2), f("run3"), f("run4", lift=1)]
    # attack (League's attack2: the idol swung up behind her, then smashed down before her, back)
    out["attack"] = [f("a_raise", dx=-1), f("a_slam", dx=2), f("a_slam", dx=2), f("idle")]
    # Harsh Lesson (Spell2: the crouch, the leap with the idol up - the data's dash - and the landing pressing it down)
    out["skill"] = [f("r_crouch"), f("w_jump"), f("w_land", dx=2)]     # w_jump's ground row holds its hop
    # Test of Spirit (Spell3: the idol thrust out - the ghost tentacle flies - then yanked back to her chest)
    out["skill2"] = [f("e_thrust", dx=1), f("e_yank", dx=-1)]
    # Leap of Faith (Spell4: the crouch, the high leap with the idol raised, kneeling as it is smashed down)
    out["ult"] = [f("r_crouch"), f("r_leap"), f("r_slam", dx=2)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: knocked back, the idol flying off; slumped down sitting by it)
    out["dead"] = [f("d_stagger", dx=-1, flash=True), f("d_stagger", dx=-2), f("d_slump", dx=-2), f("d_slump", dx=-2)]
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


# ------------------------------------------------------------------------------------------------------- tentacle
# its two sheets: [(pose, sink rows (under the ground, clipped), ms)]. `tentacle` lasts the kit's t_life (6 s): rising
# out of its cracks, swaying, sinking back; `lash` strikes: rearing, slamming down, springing back, sinking
LIFE = KIT["t_life"] * 1000 // 60
SWAY = 600
TENT_MS = {
    "tentacle": ([("tn_rise", 0, 100), ("tn_grow", 0, 120)]
                 + [(p, 0, SWAY) for _ in range(4) for p in ("idle", "tn_sway")]
                 + [("idle", 0, LIFE - 100 - 120 - 8 * SWAY - 300), ("tn_sink", 0, 300)]),
    "lash": [("tn_rear", 0, 150), ("tn_slam", 0, 150), ("tn_recoil", 0, 150), ("tn_sink", 0, 150)],
}


class Tentacle:
    """Its frames as dense canvases: the design (or a pose) centred on the pivot, its root on the canvas' ground row,
    `back` game px over the unit's soles under the pivot (a ground spot's soles are FEET under it, like a unit's)."""

    def __init__(self, back):
        self.d = load("tentacle.png")
        self.W, self.H = 80, 140
        self.px = self.W / 2.0
        self.soles = self.H - 12
        self.py = self.soles - FEET * T_PPU
        self.ground = self.soles - int(round(back * T_PPU))

    def frame(self, name, sink):
        can = np.zeros((self.H, self.W, 4), np.uint8)
        d = self.d if name == "idle" else load(f"tentacle_{name}.png")
        x0 = int(round(self.px - d.shape[1] / 2))
        y0 = self.ground - d.shape[0] + sink
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + y0, xs + x0
        ok = (ty >= 0) & (ty < self.ground) & (tx >= 0) & (tx < self.W)
        if not ok.all() and not sink:
            sys.exit(f"tentacle {name}: {int((~ok).sum())} squares off its canvas")
        can[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]
        return can


def tentacle_tags():
    out = {}
    for sheet, seq in TENT_MS.items():
        T = Tentacle(0 if sheet == "tentacle" else LASH_BACK)
        ones, hds = [], []
        for name, sink, ms in seq:
            can = T.frame(name, sink)
            ys, xs = np.nonzero(can[..., 3] > 0)
            hw = int(np.ceil(max(T.px - xs.min(), xs.max() + 1 - T.px) / T_PPU - 0.5))
            hh = int(np.ceil(max(T.py - ys.min(), ys.max() + 1 - T.py) / T_PPU - 0.5))
            hh = max(hh, int(np.ceil(FEET)) + 1)
            ones.append((R.one_of(can, T.px, T.py, hw, hh, T_PPU), ms))
            W, H = round((2 * hw + 1) * T_PPU), round((2 * hh + 1) * T_PPU)
            hds.append((R.crop_dense(can, T.px, T.py, W, H), ms))
        out[f"league_illaoi_{sheet}"] = {"idle": ones, "hd_idle": hds}
    return out


def review_tentacle(out_dir):
    """The tentacle's two sheets at 3x as GIFs (its hd frames), on the arena colour."""
    os.makedirs(out_dir, exist_ok=True)
    for sheet, tt in tentacle_tags().items():
        fr = tt["hd_idle"]
        H = max(c.shape[0] for c, _ in fr)
        W = max(c.shape[1] for c, _ in fr)
        ims = []
        for c, ms in fr:
            bg = Image.new("RGBA", (W, H), (104, 112, 72, 255))
            bg.alpha_composite(Image.fromarray(c), ((W - c.shape[1]) // 2, (H - c.shape[0]) // 2))
            ims.append(bg.convert("RGB").resize((W * 3, H * 3), Image.NEAREST))
        ims[0].save(os.path.join(out_dir, f"{sheet}.gif"), save_all=True, append_images=ims[1:],
                    duration=[int(ms) for _, ms in fr], loop=0)
        print(sheet, len(fr), "frames", sum(ms for _, ms in fr), "ms")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        review_tentacle(os.path.join(a.review, "tentacle"))
        return
    C.rig.export(acts)
    for sheet, tt in tentacle_tags().items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tt, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(v)}" for t, v in tt.items()))


if __name__ == "__main__":
    main()
