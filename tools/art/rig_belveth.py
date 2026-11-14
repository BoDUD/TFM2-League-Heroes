#!/usr/bin/env python3
"""league_belveth's action frames: Bel'Veth's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-24: 「动作帧和特效都交付了 做到完美了喊我review」).

    python tools/art/rig_belveth.py --parts DIR       # the design with its parts tinted (12x)
    python tools/art/rig_belveth.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_belveth.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_belveth_model.py, design_belveth_poses.py):
  hd/idle.png         Bel'Veth, 3/4 front facing right, 86 x 82 at PPU 1.75 (40 game px head top to claws): the idle,
                      the hit, the glide;
  hd/pose_<name>.png  Codex's key poses read back with the design's head, the bodies brought to the design's size
                      (assets/source/belveth/POSE_PROMPTS.md): a_wind a_slash q_dash w_coil w_slam e_spin1 e_spin2
                      r_curl r_rise d_reel d_down.
Placing a pose: across, its head box on the design's head box (one face that never jumps; she hovers on her claws, so
there is no planted foot to keep), moved dx squares (League's lunges); up and down, its lowest square on the ground
row, or `lift` rows over it (she flies in the dash, the storm and the rise) - the storm's two poses, played in turn every
75 ms, with their heads on one row instead (the highest either reaches standing; e_spin1's head sat 13 rows lower over
its claws than e_spin2's: the face jumped), so e_spin1 flies higher.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The move is her glide (League's RunClosed: she floats on, the claws trailing): the design whole, bobbing up and down a
row, the claws swinging a square back and forth under the hem and the tail's tip waving - no part turned or stretched.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import inbetween as IB  # noqa: E402
from rig_wukong import CutDesign as _Cut, pad  # noqa: E402

HERO = "belveth"
PPU = 1.75
SRC = os.path.join(R.ROOT, "assets", "source", "belveth", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 58                     # the column under her body's middle: the standing point
HEAD_X, HEAD_Y = 46, 11        # the head box's top-left square on hd/idle.png (pack_belveth_poses.HEAD)
HEAD_W, HEAD_H = 21, 20        # the head box: the crest to the chin
CLAWS = (72, 43)               # the claws: rows from 72 down, columns from 43 right (under the hem)
TAIL = (66, 33)                # the tail: rows from 66 down, columns left of 33 (the near cloak's edge is right of it)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    D.part("claws", op & (yy >= CLAWS[0]) & (xx >= CLAWS[1]))
    D.part("tail", op & (yy >= TAIL[0]) & (xx < TAIL[1]))
    D.part("body", D.rest())
    return D


TINT = {"claws": (255, 220, 0), "tail": (0, 255, 120)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def close_cracks(can, outline, most=12, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across - the
    outline (gap-check; rig_warwick.close_cracks). The design's own gaps between the claws stay open."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


def head_at(name):
    """The head box's top-left square in hd/pose_<name>.png (design_belveth_poses' json)."""
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


class Form:
    """The design's layers and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(70, 70, 60, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), claws=(0, 0), tail=(0, 0)):
        """The design with its parts moved by whole squares: whole (dx, dy); the claws' and the tail's (dx, dy)."""
        wx, wy = whole
        L = self.L
        layers = [(L["tail"], dict(dx=wx + tail[0], dy=wy + tail[1])),
                  (L["claws"], dict(dx=wx + claws[0], dy=wy + claws[1])),
                  (L["body"], dict(dx=wx, dy=wy))]
        can = R.compose(self.rig, layers)
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def ground_head(self, name):
        """The canvas row of a pose's head box top when it stands on its lowest square, AT's lift over the ground."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        return self.rig.GY - (ys.max() + 1) - AT[name][1] + head_at(name)[1]

    def posed(self, name, dx=0, lift=0, rise=0, moves=(), sway=(), lit=None):
        """A Codex pose (hd/pose_<name>.png) with its head box on the design's, moved dx squares; its lowest square on
        the ground, `lift` rows above it in the air; `rise` rows more on top of either placement (the true form's glide).
        The in-betweens (tools/art/inbetween.py), the pose placed as it is whole: moves [(part, (dx, dy), how)] - parts
        of the pose (PARTS) moved by whole squares, "under" the rest of her; sway [(part, x0, x1, k, attach)] - a part's
        columns lifted 0..k rows along its length; lit - a part whose rim is lit for the frame (LIT)."""
        rig = self.rig
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        hx, hy = head_at(name)
        left = rig.ox + HEAD_X - hx + dx
        top = rig.GY - (ys.max() + 1) - lift
        if name in HEAD_UP:   # the group's heads on one row: the highest any of them stands with its claws grounded
            top = min(self.ground_head(g) for g in HEAD_UP) - hy
        top -= rise
        if moves or sway or lit:
            d = self.varied(name, d, moves, sway, lit)
            left, top = left - VPAD, top - VPAD
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can

    def varied(self, name, d, moves, sway, lit):
        """The pose picture with parts of it moved (see posed), on a canvas VPAD squares bigger on every side; the head
        and every square in no part checked as the pose has them (one approved head, a body that never changes)."""
        hx, hy = head_at(name)
        head = np.zeros(d.shape[:2], bool)
        head[hy:hy + HEAD_H, hx:hx + HEAD_W] = self.head()
        return IB.vary(d, PARTS[name], self.D.outline, moves, sway, (lit, LIT) if lit else None, head, VPAD, name)

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.D.d, (HEAD_X, HEAD_Y), (HEAD_W, HEAD_H),
                                        [(load(f"pose_{n}.png"), head_at(n)) for n in AT])
        return self._head


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_belveth.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 367 ms = atk_dur 22: the wing raised, the slash landing at a_hit 9 (150 ms), back to the idle;
# Q (skill, q_dur 18 = 300 ms): the dash from q_go 3 (50 ms) for q_t 7 ticks (10 in the true form), then the idle;
# W (skill2, w_dur 30 = 500 ms): the tail raised, slammed at w_rel 12 (200 ms);
# R (ult, r_dur 40 = 667 ms): curled round the coral, risen in the true form at r_hit 20 (333 ms);
# the maelstrom (skill_e, played e_t 90 ticks = 1500 ms by a CasterAnimation, which loops the tag: league_garen's
# whirl): the two storm poses in turn.
#
# The in-betweens (the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」 - her attack played
# 3 different pictures, Q, W and R 2 each, the death 3): every span above is shared out over more frames
# (inbetween.spans: whole ms, none under 50), so each action is as long as it was and its strike still begins on its
# millisecond - the slash at 133, the dash pose from 0 (she is level before q_go) and the idle at 250, the slam at
# 200, the rise at 333, the fall at 400.
MS = {"idle": [1000], "run": [110] * 6,
      "attack": IB.spans((133, 2), (117, 2, (3, 4)), (117, 2)),
      "skill": IB.spans((250, 4, (3, 4, 4, 4)), (50, 1)),
      "skill2": IB.spans((200, 3), (300, 4, (3, 4, 5, 6))),
      "skill_e": [75] * 4,
      "ult": IB.spans((333, 4), (334, 4, (4, 4, 6, 6))),
      "hit": [100, 100],
      "dead": IB.spans((400, 4, (4, 4, 5, 7)), (1000, 4, (8, 8, 9, 75)))}
# the true form (TRUE below): the same timings as the folded form's tags - the kit plays one tag in both forms, and
# the add-on's test every_swapped_tag_is_in_her_sheet_with_the_same_timing holds the twins to it
MS.update({"r_idle": [1000], "r_run": MS["run"], "r_attack": MS["attack"], "r_skill": MS["skill"],
           "r_skill2": MS["skill2"], "r_hit": MS["hit"]})
# the glide: per frame the figure's rise, the claws' (dx, dy), the tail's (dx, dy)
GLIDE = [(0, (0, 0), (0, 0)), (1, (-1, 0), (0, -1)), (2, (-1, 0), (0, -1)),
         (2, (0, 0), (0, 0)), (1, (1, 0), (0, 1)), (0, (1, 0), (0, 0))]
# each pose moved dx squares from the design's head column (League's lunges), `lift` rows off the ground
AT = {"a_wind": (0, 0), "a_slash": (0, 0), "q_dash": (4, 6), "w_coil": (0, 0), "w_slam": (0, 0), "e_spin1": (0, 4),
      "e_spin2": (0, 4), "r_curl": (0, 0), "r_rise": (0, 5), "d_reel": (-2, 0), "d_down": (-3, 0)}


# poses played in turn fast (the storm): placed by the head's height, so the face does not jump between them
HEAD_UP = {"e_spin1", "e_spin2"}

# The parts of the key poses that move on their own in the in-between frames: polygons in each pose picture's own
# squares (tools/art/inbetween.py cut). A wing or the raised tail grows out from behind her, so it is slid toward her
# "under" the rest of the picture - seen shorter, still whole, nothing turned or stretched; a tail lying out behind
# her waves by its columns (inbetween.sway). The head, the collar and the body are in no part: they never change.
VPAD = 30                      # squares a moved part may leave its pose picture's box by
# the slashing wing's magenta rim lit as it lands: each shade the design's next lighter one (the claws' pinks)
LIT = {(248, 6, 250): (251, 128, 251), (209, 0, 206): (250, 86, 250), (170, 3, 168): (209, 0, 206)}
PARTS = {
    "a_wind": {"wing": [[(0, 0), (40, 0), (41, 29), (47, 36), (47, 44), (50, 46), (50, 60), (49, 62), (49, 68),
                         (0, 68)]]},
    "a_slash": {"wing": [[(0, 5), (57, 5), (57, 38), (48, 38), (48, 48), (0, 48)]],
                "edge": [R.band((60, 58), (112, 86), 6)]},
    "q_dash": {"tail": [[(0, 26), (46, 26), (46, 42), (40, 44), (40, 50), (0, 50)]]},
    "w_coil": {"tail": [[(0, 0), (36, 0), (36, 14), (24, 14), (24, 50), (28, 53), (22, 58), (22, 60), (24, 64),
                         (26, 68), (20, 68), (8, 60), (0, 50)]]},
    "w_slam": {"lwing": [[(0, 0), (50, 0), (50, 62), (46, 64), (46, 78), (0, 78)]],
               "rwing": [[(87, 0), (113, 0), (113, 70), (92, 70), (92, 73), (86, 73), (86, 67), (87, 66)]]},
    "r_curl": {"tail": [[(0, 56), (36, 56), (36, 74), (0, 74)]]},
    "r_rise": {"lwing": [[(0, 0), (44, 0), (44, 58), (46, 60), (46, 72), (0, 72)]],
               "rwing": [[(80, 0), (103, 0), (103, 68), (80, 68)]],
               "tail": [[(0, 64), (38, 72), (38, 95), (0, 95)]]},
    "d_reel": {"tail": [[(0, 70), (15, 71), (30, 75), (45, 77), (52, 72), (56, 86), (0, 86)]]},
    "d_down": {"tail": [[(0, 42), (34, 42), (34, 57), (0, 57)]]},
    "e_spin1": {"lwing": [[(0, 0), (31, 0), (31, 30), (33, 34), (33, 60), (30, 62), (30, 82), (0, 82)]],
                "rwing": [[(63, 0), (83, 0), (83, 82), (66, 82), (66, 60), (63, 56)]]},
    "e_spin2": {"lwing": [[(0, 28), (38, 28), (38, 72), (25, 72), (25, 80), (12, 84), (12, 96), (0, 96)]],
                "rwing": [[(80, 28), (107, 28), (107, 96), (80, 96)]]},
}

# The true form (the user, 2026-11-14: 「阿尔卑斯的变为真身是不是要做个变形啊 和联盟一样」 - 「卑尔维斯」, 「先变大再张翼」): while
# Endless Banquet's `league_belveth_r_on` is on her the add-on league_belveth plays `r_<tag>` for these tags (Swain's
# and Kayn's way: the playing animation's name swapped in the display world; `r_` as league_volibear's storm twins -
# hero_reels keeps `tf_` / `t_` tags out of the idles as transformations). League's true form is her body with the
# wings spread; Codex's poses already hold her so, at the design's size with the design's head: TRUE, the storm's
# swept-out pose (both wings spread out and down, the tail curled under her, off the ground - the storm itself then
# starts from her stance), is how she stands, glides and reels in true form; she strikes from the rise (both wings
# up, the ult's last frame) down through the slash. No new picture drawn. The idle is the stance alone, as the folded
# form's is the design alone (hero_reels cuts the little moves: tools/art/hero_reels.json `r_idle`).
TRUE = "e_spin2"
# the glide in true form: rows risen per frame (the folded glide's own bob, a row more - nothing of her touches the ground)
R_GLIDE = [0, 1, 2, 3, 2, 1]


def WINGS(k):
    """The stance's two spread wings beating: their tips k rows up (negative: down), nothing at the shoulders."""
    return [("lwing", 0, 38, k, "right"), ("rwing", 80, 105, k, "left")]


def actions(F):
    p, q = F.pose, F.posed

    def at(name, ddx=0, dlift=0, **how):
        dx, lift = AT[name]
        return q(name, dx + ddx, lift + dlift, **how)

    def under(**parts):
        return [(part, off, "under") for part, off in parts.items()]

    def tail(name, k, x1):
        """The pose's tail waved: its tip k rows up, nothing where it joins her at column x1."""
        return [("tail", 0, x1, k, "right")]
    out = {}
    out["idle"] = [p()]
    # the glide (League's RunClosed)
    out["run"] = [p(whole=(0, -r), claws=c, tail=t) for r, c, t in GLIDE]
    # auto attack (League's Attack_Slow1a: the near wing raised, then slashed down across her front): leaning back as
    # the wing comes up from behind her, raised; the slash landing a step ahead with its rim lit, the far wing folding
    # in behind her as she settles and draws back; the idle
    slash = [at("a_slash", 3, lit="edge"), at("a_slash", 1, moves=under(wing=(3, 2)))]
    out["attack"] = [at("a_wind", -2, moves=under(wing=(10, 20))), at("a_wind", -3), *slash,
                     at("a_slash", -1, moves=under(wing=(8, 6))), p()]
    # Q Void Surge (Q_spell1: level, rushing forward): low and back as she springs, level, stretched out ahead with the
    # tail whipping up, sinking as she brakes; then the idle
    dash = [at("q_dash", -6, -4, sway=tail("q_dash", -3, 44)), at("q_dash"),
            at("q_dash", 3, 1, sway=tail("q_dash", 4, 44)), at("q_dash", 1, -3, sway=tail("q_dash", 1, 44))]
    out["skill"] = [*dash, p()]
    # W Above and Below (Spell2_0: the tail raised, slammed): the tail swinging up over her from behind in two steps as
    # she rises off the ground, coiled; slammed a step ahead with the wings still opening, the wings spread, then
    # sinking in two steps
    slam = [at("w_slam", 3, moves=under(lwing=(5, 6), rwing=(-3, 5))), at("w_slam", 1),
            at("w_slam", moves=under(lwing=(3, 4), rwing=(-2, 3))), at("w_slam", moves=under(lwing=(7, 9), rwing=(-4, 7)))]
    out["skill2"] = [at("w_coil", moves=under(tail=(3, 12))), at("w_coil", -1, 1, moves=under(tail=(2, 6))),
                     at("w_coil", -2, 2), *slam]
    # E Royal Maelstrom (Spell3_attack_slow: the wings up, swept out, in turn)
    out["skill_e"] = [at("e_spin1") if k % 2 == 0 else at("e_spin2") for k in range(len(MS["skill_e"]))]
    # R Endless Banquet (Spell4: curled round the coral, risen): sinking into the curl with the tail waving, curled,
    # drawn back; then bursting up - the wings half open, flung up a little too high, risen, settling
    out["ult"] = [at("r_curl", 0, 5, sway=tail("r_curl", 3, 36)), at("r_curl", 0, 2, sway=tail("r_curl", 1, 36)),
                  at("r_curl"), at("r_curl", -2, 0, sway=tail("r_curl", 3, 36)),
                  at("r_rise", 0, -4, moves=under(lwing=(8, 10), rwing=(-5, 9))), at("r_rise", 0, 3),
                  at("r_rise"), at("r_rise", 0, -1, moves=under(lwing=(3, 4), rwing=(-2, 3)))]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's Death: flung up and back, fallen to the ground): struck, reeling back and up off the ground with
    # the tail flung up; curling up as she drops (the ult's curl, in the air), down, the tail falling after her, still
    out["dead"] = [R.flash(at("d_reel", 2)), at("d_reel", 0, 1), at("d_reel", -2, 3, sway=tail("d_reel", 3, 50)),
                   at("d_reel", -3, 4, sway=tail("d_reel", 1, 50)),
                   at("r_curl", -5, 5, sway=tail("r_curl", 4, 36)), at("d_down", 0, 3, sway=tail("d_down", 4, 32)),
                   at("d_down", 0, 0, sway=tail("d_down", 2, 32)), at("d_down")]
    # the true form: hovering with the wings spread
    out["r_idle"] = [at(TRUE)]
    out["r_run"] = [q(TRUE, AT[TRUE][0], AT[TRUE][1], rise=r) for r in R_GLIDE]
    # she strikes from the rise - the wings coming up, raised - down through the slash, the wings spreading out again
    out["r_attack"] = [at("r_rise", -2, -1, moves=under(lwing=(8, 10), rwing=(-5, 9))), at("r_rise", -3), *slash,
                       at(TRUE, 1, sway=WINGS(4)), at(TRUE)]
    out["r_skill"] = [*dash, at(TRUE)]
    # W: the coil's wings are folded round her - in true form that frame would read as her turning back (the user on
    # Kayn, 2026-10-19: 「变身的时候中途有一段突然变回去」), so she winds up with both wings raised (the storm's first pose),
    # coming up from behind her in two steps
    out["r_skill2"] = [at("e_spin1", moves=under(lwing=(6, 14), rwing=(-4, 12))),
                       at("e_spin1", -1, 0, moves=under(lwing=(3, 7), rwing=(-2, 6))), at("e_spin1", -2), *slam]
    out["r_hit"] = [R.flash(at(TRUE, -2)), at(TRUE, -1)]
    return out


def frames(F, tags=None):
    out = {}
    for tag, cans in actions(F).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(lp(a.parts), exist_ok=True)
        tinted(D).save(lp(os.path.join(a.parts, "belveth_parts.png")))
        return
    F = Form(D)
    F.rig.idle_canvas = F.pose()
    acts = frames(F, a.tags.split(",") if a.tags else None)
    if a.review:
        F.rig.review(acts, a.review)
        return
    F.rig.export(acts)


if __name__ == "__main__":
    main()
