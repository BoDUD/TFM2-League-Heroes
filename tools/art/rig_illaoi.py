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
import inbetween as IB  # noqa: E402
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

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - parts of the pose (PARTS) moved by whole squares, "under" the rest of her or
        "over" it; spins [(part, point, degrees, how)] - a part turned clockwise by any angle about a point, then moved
        if `moves` names it too. The head and everything of the pose in none of its parts are checked unchanged."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        if moves or spins:
            hx, hy = load_pose(name)[1]
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + HEAD_H, hx:hx + HEAD_W] = self.head()
            d = IB.vary(d, without(d, parts_of(name, d), head), self.outline, moves, (), None, head, VPAD, name, (),
                        spins)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.d, HEAD, (HEAD_W, HEAD_H),
                                        [load_pose(n)[:2] for n in POSES])
        return self._head


# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): polygons / boxes in each pose picture's own
# squares. The idol she swings one-handed turns with the arm about her shoulder (inbetween.spin: the join hidden under
# the collar); the idol held out in both hands slides along her arms in under her (drawn in); the idol knocked out of
# her hands in the death tumbles on by itself (its own piece of the picture: IDOL_AT, a square of it). Her head (the bun,
# the hair, the face: pack_illaoi_poses.HEAD) and the rest of her are in no part: they never change.
HEAD_W, HEAD_H = PK.HEAD[3] - PK.HEAD[2], PK.HEAD[1] - PK.HEAD[0]
POSES = ["a_raise", "a_slam", "w_jump", "w_land", "e_thrust", "e_yank", "r_crouch", "r_leap", "r_slam", "run1", "run2",
         "run3", "run4", "d_stagger", "d_slump"]
VPAD = 34                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "a_raise": {"idol": [[(0, 0), (26, 0), (26, 22), (24, 26), (30, 33), (34, 37), (34, 41), (30, 42), (26, 40),
                          (18, 33), (0, 33)]]},
    "r_leap": {"idol": [[(0, 0), (28, 0), (28, 24), (30, 34), (33, 39), (33, 45), (27, 46), (14, 42), (0, 36)]]},
    "e_thrust": {"idol": [[(46, 0), (86, 0), (86, 40), (57, 40), (57, 33), (46, 33)]]},
}
IDOL_AT = {"d_stagger": (14, 14)}  # a square of the flying idol: the piece of the picture it is
# the point the swung idol turns about (square corners): the corner where her arm leaves the collar on the side it
# turns away from (so its root swings in under her and no gap opens); the flying idol about its middle
PIVOT = {("a_raise", "ccw"): (34, 36), ("a_raise", "cw"): (30, 42), ("r_leap", "ccw"): (33, 38),
         ("r_leap", "cw"): (28, 45), ("d_stagger", "ccw"): (14, 16)}


def parts_of(name, d):
    """PARTS of a pose, with the flying idol (IDOL_AT) as the piece of the picture it is."""
    out = dict(PARTS.get(name, {}))
    if name in IDOL_AT:
        from scipy import ndimage
        lab, _ = ndimage.label(d[..., 3] > 0, structure=np.ones((3, 3)))
        x, y = IDOL_AT[name]
        out["idol"] = [runs(lab == lab[y, x])]
    return out


def runs(m):
    """A mask as row runs (x0, y, x1, y) - boxes for inbetween.part_mask."""
    out = []
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        if not len(xs):
            continue
        cut = np.nonzero(np.diff(xs) > 1)[0]
        out += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
    return out


def without(d, parts, head):
    """Each part's mask less the head's squares (her raised arm lies against her hair, and a polygon's edge may take a
    square more than its vertices say), as row runs for inbetween.vary."""
    out = {}
    for k, items in parts.items():
        flat = []
        for it in items:
            flat += it if isinstance(it, list) and it and isinstance(it[0], tuple) and len(it[0]) == 4 else [it]
        out[k] = runs(IB.part_mask(d.shape, flat) & ~head)
    return out


def ms_of(tick):
    return round(tick * 1000 / 60)


# ms per frame; the kit's ticks (tools/kit/build_illaoi.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the idol landing on the slam frame (a_hit 14 = 233 ms; the slam from 200 ms);
# Harsh Lesson 500 ms = w_dur 30, the leap from the cast (w_dash 12 = 200 ms, in the air to 300 ms), landing pressed;
# Test of Spirit 500 ms = e_dur 30, the ghost tentacle off the idol thrust out (e_rel 12 = 200 ms; the thrust to 250 ms),
# then the yank; Leap of Faith 667 ms = r_dur 40, the crouch, the leap, the idol smashed down (r_at 26 = 433 ms; the
# slam from 430 ms)
#
# The in-betweens (2026-11-14: the attack played 3 poses, E 2, the leap and the ult 3 each, the death 2 and a flash):
# each span above is shared out over more frames (inbetween.spans: whole ms, none under 50), so every action is as
# long as it was and its strike still begins on its millisecond - the slam at 200 (the idol landing at 233) and the
# idle at 450, the leap at 120 and the landing at 300, the yank at 250, the leap at 150 and the slam at 430, the slump
# at 340. A frame that is only its neighbour moved whole is no new pose: one stays only where the move is the motion
# (the slam's lunge, the hop's arc, the fall). The run and the hit are as they were.
MS = {"idle": [1000], "run": [140] * 4, "attack": IB.spans((200, 3), (250, 2), (50, 1)),
      "skill": IB.spans((120, 1), (180, 2), (200, 2)),
      "skill2": IB.spans((250, 3), (250, 3)), "ult": IB.spans((150, 1), (280, 3), (237, 2)), "hit": [100, 100],
      "dead": IB.spans((340, 3, (4, 5, 8)), (900, 2, (8, 92)))}


def actions(C):
    f = C.frame

    def spin(name, degrees, how="under"):
        """The pose's idol turned clockwise by `degrees` (negative: counter-clockwise) about its point (PIVOT)."""
        return [("idol", PIVOT[(name, "cw" if degrees > 0 else "ccw")], degrees, how)]

    def drawn(dx):
        """The idol held out in both hands slid dx squares along her arms (in under her)."""
        return [("idol", (dx, 0), "under")]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run1: contact, passing, contact on the other leg, passing; the idol carried low at her side). The
    # head over the ground row 61 / 62 / 61 / 62 (the readbacks stand it at 59 / 60 / 61 / 61: Codex's legs differ by a
    # row or two), so the head bobs a row, the passing frames higher
    out["run"] = [f("run1", lift=2), f("run2", lift=2), f("run3"), f("run4", lift=1)]
    # attack (League's attack2: the idol swung up behind her, then smashed down before her, back): the idol coming up
    # from her side, swung up behind her, coming over her head; smashed down a step ahead, at rest; the idle
    out["attack"] = [f("a_raise", dx=-1, spins=spin("a_raise", -20)), f("a_raise", dx=-1),
                     f("a_raise", dx=-1, spins=spin("a_raise", 40)), f("a_slam", dx=4), f("a_slam", dx=2), f("idle")]
    # Harsh Lesson (Spell2: the crouch, the leap with the idol up - the data's dash - and the landing pressing it down):
    # the crouch; springing up, at the top; dropping onto the target, landed
    out["skill"] = [f("r_crouch"), f("w_jump", lift=-5), f("w_jump"),     # w_jump's ground row holds its hop
                    f("w_land", dx=2, lift=5), f("w_land", dx=2)]
    # Test of Spirit (Spell3: the idol thrust out - the ghost tentacle flies - then yanked back to her chest): the idol
    # at her chest (the yank's pose), half out, thrust out; pulled back in two steps, at her chest
    out["skill2"] = [f("e_yank", dx=-1), f("e_thrust", dx=1, moves=drawn(-6)), f("e_thrust", dx=1),
                     f("e_thrust", dx=1, moves=drawn(-6)), f("e_thrust", dx=1, moves=drawn(-12)), f("e_yank", dx=-1)]
    # Leap of Faith (Spell4: the crouch, the high leap with the idol raised, kneeling as it is smashed down): the crouch;
    # rising with the idol coming up from her side, at the top with it raised behind her, coming over her head; smashed
    # down a step ahead, kneeling
    out["ult"] = [f("r_crouch"), f("r_leap", lift=-4, spins=spin("r_leap", -25)), f("r_leap"),
                  f("r_leap", spins=spin("r_leap", 35)), f("r_slam", dx=4), f("r_slam", dx=2)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: knocked back, the idol flying off; slumped down sitting by it): struck; knocked back with
    # the idol tumbling on away from her; dropping, slumped
    out["dead"] = [f("d_stagger", dx=-1, flash=True),
                   f("d_stagger", dx=-3, lift=1, spins=spin("d_stagger", -30, "over"), moves=[("idol", (-4, 5), "over")]),
                   f("d_stagger", dx=-4, lift=2, spins=spin("d_stagger", -70, "over"),
                     moves=[("idol", (-7, 12), "over")]),
                   f("d_slump", dx=-2, lift=3), f("d_slump", dx=-2)]
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
# the add-on's tentacle lives a minute (League's) and is drawn in three parts it chains on its spot (the user,
# 2026-10-23: 「俄洛伊触手乱长 和英雄联盟逻辑不一样」): rising, one sway it plays again for as long as it stands, sinking
TENT_PARTS = {
    "tentacle": {"rise": [("tn_rise", 0, 100), ("tn_grow", 0, 120)],
                 "sway": [("idle", 0, SWAY), ("tn_sway", 0, SWAY)],
                 "sink": [("tn_sink", 0, 300)]},
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

        def drawn(seq):
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
            return ones, hds

        ones, hds = drawn(seq)
        tags = {"idle": ones, "hd_idle": hds}
        for part, pseq in TENT_PARTS.get(sheet, {}).items():
            ones, hds = drawn(pseq)
            tags[part], tags[f"hd_{part}"] = ones, hds
        out[f"league_illaoi_{sheet}"] = tags
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
    ap.add_argument("--tentacles", action="store_true",
                    help="only the tentacle's effect sheets (her own sheet, reeled by hero_reels.py, is left alone)")
    a = ap.parse_args()
    if a.tentacles:
        for sheet, tt in tentacle_tags().items():
            w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tt, share=True)
            print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(v)}" for t, v in tt.items()))
        return
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
