#!/usr/bin/env python3
"""league_zaahen's action frames: Zaahen's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-26: sprites by Codex from written prompts, then 「亚恒的动作帧也交付了 你做到完美后喊我review」).

    python tools/art/rig_zaahen.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_zaahen.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/rig_zaahen.py --rise           # the add-on's revive picture -> league/effects/league_zaahen_rise

The pictures (tools/art/design_zaahen_model.py, design_zaahen_poses.py):
  hd/idle.png         Zaahen, 3/4 front facing right, 88 x 84 at PPU 1.75 (48 game px horn tips to soles): the idle, the
                      hit;
  hd/wings.png        step 0's B on the same squares: the wings spread, the glaive raised - the end of the revive;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/zaahen/POSE_PROMPTS.md): a_wind a_sweep q_cut1 q_cut2 q_crouch q_up w_thrust w_pull
                      e_dash e_spin r_crouch r_rise r_stab run1-4 d_fall d_down rv_kneel.
Placing a pose (rig_locke's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as the skeleton's head moves in that pose (the pose pack: HEAD_DX, rounded) and dx squares more by hand; its
soles on the ground row (its feet's lowest square: FEET where the glaive or a wing hangs lower), or `lift` rows over
it. The idle is the design alone (hero_reels cuts the idle snippets from these actions). The spin (the add-on's Aureate
Rush, and the main pack's W that ends in it) turns him round: the spin pose, then the same pose mirrored about his
standing column (his back to the front for a moment, the glaive sweeping round the other side), then the level cut.
The revive (the add-on's: he is banished while he rises, so his rising is an effect picture, not his own frames - and
an effect picture is never mirrored on the red side) is drawn twice, facing right (rise_r) and left (rise_l), in front
of the cleaned light column rv_glow (tools/art/clean_zaahen_fx.py), as a dense effect sheet like league_leblanc_clone
(league_main hd.rs EFFECTS at PPU 1.75 / SIZE: drawn at his 85 %, write_rise): collapsed (d_down), kneeling with the
glaive planted (rv_kneel), standing with the wings spread (hd/wings.png); the add-on plays the side facing the nearest
enemy champion.
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
import inbetween as IB  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402
import pack_zaahen_poses as PK  # noqa: E402

HERO = "zaahen"
PPU = 1.75
# on the battlefield he is drawn at 85 % (the user, 2026-11-11: 「亚恒模型在局内偏大了」; league_main hd.rs SIZES), his dense
# frames 4 squares lower so his soles stay on the ground (ppu_restyle.py RESTYLE zaahen drop_sq: 11.5 x 1.75 x
# (1 / 0.85 - 1) = 3.6). His revive picture goes with him (write_rise): its sheet's PPU in hd.rs EFFECTS is PPU / SIZE.
SIZE = 0.85
LIFT_SQ = 4
SRC = os.path.join(ROOT, "assets", "source", "zaahen", "hd")
FXSRC = os.path.join(ROOT, "assets", "source", "zaahen", "gemini_fx", "clean", "pixel_1x")
RISE = os.path.join(ROOT, "league", "effects", "league_zaahen_rise")
STAND = 54                     # the idle's standing column: under his belt, between his feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far the skeleton's head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}
LIFT = {"q_up": 2, "e_dash": 3, "r_rise": 14, "run2": 1, "run4": 1}   # rows off the ground (the skeletons'; the ult's
                                                                       # rise sets its own: up, higher, the dive)
# pose -> its soles' row where the glaive's blade or a wing hangs lower than the feet (else its lowest row), read at 6x
FEET = {"a_sweep": 75, "q_crouch": 62, "q_up": 126, "q_cut2": 111, "r_crouch": 91, "run2": 78, "run4": 81, "d_fall": 118}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name):
    if name == "wings":
        d = load("wings.png")
        return d, wings_head(d), d.shape[0]
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(FEET.get(name, ys.max() + 1))


def wings_head(d):
    """Where B's head box stands in hd/wings.png: B was drawn from A on the same squares, so the design's head box is
    found there square for square (design_shyvana_poses.match_head at one pixel a square)."""
    from design_shyvana_poses import match_head
    r0, r1, c0, c1 = PK.HEAD
    head = load("idle.png")[r0:r1, c0:c1]
    s, x, y, cost, ang = match_head(d, head, scales=[1.0], half=1)
    return (x, y)


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(72, 72, 96, 16))      # room for the glaive raised high, swung out and flung away
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX.get(name, 0)
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=None, flash=False, flip=False, moves=(), sway=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - a part of the pose (PARTS) moved by whole squares (the glaive he lost, flying
        on); sway [(part, x0, x1, k, attach)] - a spread wing's columns lifted 0..k rows toward its tip (the beat). The
        head and everything of the pose in none of its parts are checked unchanged."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, LIFT.get(name, 0) if lift is None else lift)
        if moves or sway:
            hx, hy = load_pose(name)[1]
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + HEAD_H, hx:hx + HEAD_W] = self.head()
            d = IB.vary(d, parts_of(name, d, head), self.outline, moves, sway, None, head, VPAD, name)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        if flip:                                        # mirrored about his standing column
            tx = 2 * rig.CX - tx
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.d, HEAD, (HEAD_W, HEAD_H), [load_pose(n)[:2] for n in HEADED])
        return self._head


# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): the two wings he spreads as he rises (their
# columns lifted toward the tips: a beat), polygons in the pose picture's own squares less the head's squares; the
# glaive knocked out of his hands in the death (GLAIVE_AT: a square of it - the piece of the picture it is). The glaive
# he holds is in both hands across his body and its shaft is a line a square or two thick: it is not turned. His head
# (the horns, circlet, hair and face: pack_zaahen_poses.HEAD) and the rest of him are in no part: they never change.
HEAD_W, HEAD_H = PK.HEAD[3] - PK.HEAD[2], PK.HEAD[1] - PK.HEAD[0]
VPAD = 40                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "r_rise": {"lwing": [[(0, 0), (40, 0), (41, 30), (42, 46), (41, 56), (30, 67), (0, 67)]],
               "rwing": [[(67, 0), (96, 0), (96, 61), (76, 63), (68, 56), (66, 42)]]},
}
GLAIVE_AT = {"d_fall": (100, 54)}    # a square of the flying glaive's shaft
HEADED = ("r_rise", "d_fall")      # the poses with in-betweens: the head they share with the design is checked
# a wing's beat: its columns (tip, root) and which end is attached
WING = {("r_rise", "lwing"): (0, 42, "right"), ("r_rise", "rwing"): (66, 95, "left")}


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


def parts_of(name, d, head):
    """PARTS of a pose as masks less the head's squares, with the flying glaive (GLAIVE_AT) as the piece of the
    picture it is - as row runs for inbetween.vary."""
    out = {k: runs(IB.part_mask(d.shape, v) & ~head) for k, v in PARTS.get(name, {}).items()}
    if name in GLAIVE_AT:
        from scipy import ndimage
        lab, _ = ndimage.label(d[..., 3] > 0, structure=np.ones((3, 3)))
        x, y = GLAIVE_AT[name]
        if not lab[y, x]:
            sys.exit(f"{name}: GLAIVE_AT is not on the glaive")
        out["glaive"] = runs(lab == lab[y, x])
    return out


# ms per frame; the kit's ticks (tools/kit/build_zaahen.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the sweep on a_hit 12 (200 ms); The Darkin Glaive 567 ms = q_dur 34, the cuts on q_h1 12
# (200 ms) and q_h2 22 (367 ms); its recast 500 ms = q3_dur 30, the uppercut on q3_hit 14 (233 ms); Dreaded Return
# 500 ms = w_dur 30 (the add-on's copy), the glaive let fly on w_rel 7 (117 ms); the main pack's W with the spin folded
# in 933 ms = w_e_dur 56, the spin striking on w_e 34 (567 ms); the add-on's rush 167 ms = its DASH_T 10, its spin
# 433 ms = e_dur 26, striking on e_hit 14 (233 ms); Grim Deliverance 1000 ms = r_dur 60, the dive on r_jump 26
# (433 ms), the slam on r_slam 40 (667 ms)
#
# The in-betweens (2026-11-14: the attack played 3 poses, the ult 3 - one drawing risen three times -, the death 2 and a
# flash): the attack's wind-up shares its 200 ms with the level cut borrowed from Q, the ult's rising frames beat the
# wings, the death's glaive flies on; every action is as long as it was and its strikes begin on their milliseconds (the
# sweep at 200, the dive at 433, the stab pose at 600, the fall at 400). The other actions are as they were.
MS = {"idle": [1000], "run": [125] * 4, "attack": IB.spans((200, 2), (200, 1), (100, 1)), "skill": [200, 167, 133, 67],
      "skill_up": [233, 200, 67], "skill2": [117, 233, 150], "skill2e": [117, 233, 150, 117, 116, 100, 100],
      "dash": [167], "skill3": [133, 117, 117, 66], "ult": [200, 117, 116, 167, 400], "hit": [100, 100],
      "dead": IB.spans((400, 3, (35, 30, 35)), (900, 2, (8, 92)))}


def spin(f):
    """The spin: the glaive swung out behind him, the same pose mirrored (his back turned, the blade round the other
    side), the level cut forward."""
    return [f("e_spin"), f("e_spin", flip=True), f("q_cut1")]


def actions(C):
    f = C.frame

    def beat(name, k):
        """The pose's wings beaten: their tips k rows up (negative: down), nothing at the shoulders."""
        return [(w, WING[(name, w)][0], WING[(name, w)][1], k, WING[(name, w)][2]) for w in ("lwing", "rwing")]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Runfast: contact, passing, contact on the other leg, passing; the glaive trailing, the wings back)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack_02: the glaive raised high behind him, swept low across to the front, back): raised; coming round
    # level (Q's level cut, borrowed); swept low; back
    out["attack"] = [f("a_wind"), f("q_cut1"), f("a_sweep"), f("idle")]
    # The Darkin Glaive (Spell1_AA1: the glaive drawn back, cut level across, cut up to the upper right, back)
    out["skill"] = [f("a_wind"), f("q_cut1"), f("q_cut2"), f("idle")]
    # its recast (Spell1_AA2: crouched with the blade low, the uppercut springing up, back)
    out["skill_up"] = [f("q_crouch"), f("q_up"), f("idle")]
    # Dreaded Return (Spell2 / Spell2_hit: gathered, the long thrust, the pull back)
    out["skill2"] = [f("q_crouch"), f("w_thrust"), f("w_pull")]
    # the main pack's W: the same, then Aureate Rush's spin folded in where the pulled ones stand
    out["skill2e"] = out["skill2"] + spin(f) + [f("idle")]
    # the add-on's Aureate Rush: the rush (Spell3_Dash), then the spin on landing
    out["dash"] = [f("e_dash")]
    out["skill3"] = spin(f) + [f("idle")]
    # Grim Deliverance (Spell4_Intro / Dash / Finish: crouched, wings spread; rising; up; the dive; the landing stab)
    # (the rise beats the wings: down as he lifts off, up at the top, as drawn as he dives)
    out["ult"] = [f("r_crouch"), f("r_rise", lift=10, sway=beat("r_rise", -5)),
                  f("r_rise", lift=24, sway=beat("r_rise", 5)), f("r_rise", lift=12), f("r_stab")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: knocked back, the glaive flying; down on his knees, the glaive on the ground): struck; reeling with
    # the glaive flying on away from him in two steps; dropping, down
    out["dead"] = [f("d_fall", flash=True), f("d_fall", dx=-2, moves=[("glaive", (6, -5), "over")]),
                   f("d_fall", dx=-3, lift=1, moves=[("glaive", (11, -7), "over")]), f("d_down", lift=3), f("d_down")]
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


# the revive: (pose, ms) over the add-on's rv_rise 240 ticks (4000 ms), the light column behind (rv_glow's frames:
# three rising once, then its five-frame loop at GLOW_MS)
RISE_SEQ = [("d_down", 800), ("rv_kneel", 1100), ("rv_kneel", 900), ("wings", 1200)]
GLOW_MS = 100


def rise_canvases(C):
    """The revive's dense canvases facing right, each GLOW_MS long: his pose at that time over rv_glow (brought to PPU,
    nearest, its lowest row on the ground line under his feet)."""
    rig = C.rig
    glow = np.asarray(Image.open(lp(os.path.join(FXSRC, "zaahen_fx_rv_glow.png"))).convert("RGBA"))
    with open(lp(os.path.join(FXSRC, "..", "manifest.json")), encoding="utf-8") as f:
        man = {e["file"]: e for e in json.load(f)}
    cw, ch = man["zaahen_fx_rv_glow.png"]["cell_1x"]
    cells = [glow[:, k * cw:(k + 1) * cw] for k in range(glow.shape[1] // cw)]
    order = list(range(3)) + [3 + (k % (len(cells) - 3)) for k in range(400)]
    out = []
    poses = []
    for name, ms in RISE_SEQ:
        poses += [name] * (ms // GLOW_MS)
    for k, name in enumerate(poses):
        can = rig.canvas()
        g = cells[order[k]]
        big = np.asarray(Image.fromarray(g).resize((round(cw * PPU), round(ch * PPU)), Image.NEAREST))
        ys, xs = np.nonzero(big[..., 3] > 0)
        top = rig.GY + 1 - (ys.max() + 1)
        left = rig.CX - big.shape[1] // 2
        can[ys + top, xs + left] = big[ys, xs]
        body = C.frame(name)
        m = body[..., 3] > 0
        can[m] = body[m]
        out.append((can, GLOW_MS))
    return out


def write_rise(C):
    """league/effects/league_zaahen_rise: tags rise_r / rise_l (1x) and their hd_ twins, every frame centred on the
    pivot like a hero's frame (ppu_rig.Rig.export's one_of / crop_dense), rise_l the mirror of rise_r; idle / hd_idle
    = rise_r (league.dll tells a dense effect sheet by its idle, rig_azir's way; shared frames, no room taken).
    He is drawn at SIZE on the battlefield and an effect sheet has no SIZES row (the effect draw shrinks it to 1 / its
    PPU), so the dense frames are canvases PPU / SIZE times the 1x frames (hd.rs EFFECTS at PPU / SIZE; the DLL takes a
    dense table only when hd_idle is that many times as wide) holding the picture at PPU, LIFT_SQ squares lower like his
    own dense frames: drawn at SIZE / PPU, the risen Zaahen is as big as he is and stands where his soles do. The 1x
    frames (the game without league.dll, where he is 100 %) as before."""
    rig = C.rig
    px = float(rig.CX)
    py = rig.GY - R.FEET * PPU
    shown = PPU / SIZE
    cans = rise_canvases(C)
    allc = np.stack([c for c, _ in cans])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    W, H = round((2 * hw + 1) * shown), round((2 * hh + 1) * shown)
    # the picture lowered LIFT_SQ squares inside the canvas still fits (it reaches (hh + 0.5) x PPU from the pivot)
    assert (hh + 0.5) * PPU + LIFT_SQ <= H / 2 and (hw + 0.5) * PPU <= W / 2, (hw, hh, W, H)
    tags = {"rise_r": [], "hd_rise_r": [], "rise_l": [], "hd_rise_l": []}
    for can, ms in cans:
        one = G.complete_outline(R.one_of(can, px, py, hw, hh, PPU), color=C.outline)[0]
        hd = R.crop_dense(can, px, py - LIFT_SQ, W, H)
        tags["rise_r"].append((one, float(ms)))
        tags["hd_rise_r"].append((hd, float(ms)))
        tags["rise_l"].append((one[:, ::-1].copy(), float(ms)))
        tags["hd_rise_l"].append((hd[:, ::-1].copy(), float(ms)))
    tags = {"idle": tags["rise_r"], "hd_idle": tags["hd_rise_r"], **tags}
    w, h = G.write_sheet(lp(RISE), tags, share=True)
    print(f"league/effects/league_zaahen_rise#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(v)}" for t, v in tags.items()))
    return cans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    ap.add_argument("--rise", action="store_true", help="write the revive's effect sheet")
    a = ap.parse_args()
    C = Canvas()
    if a.rise:
        cans = write_rise(C)
        if a.review:
            C.rig.review({"rise": cans}, a.review)
        return
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
