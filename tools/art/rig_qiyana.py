#!/usr/bin/env python3
"""league_qiyana's action frames: her approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-22: 「Codex 照骨架画姿势」, then 「请好好做吧 做到完美了喊我review」).

    python tools/art/rig_qiyana.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_qiyana.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (PPU 1.5, one palette; tools/art/design_qiyana_model.py and design_qiyana_poses.py):
  hd/idle.png         her, 3/4 front facing right, 52 x 60 (40 game px): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head pasted on
                      (assets/source/qiyana/POSE_PROMPTS.md, the legs drawn again short in LEGS_PROMPTS.md): a_wind
                      a_strike q_wind q_sweep q_end e_dash e_hit r_leap r_slam run1-4 d_fall d_lie.
Placing a pose (league_udyr's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares (a lunge carries her forward), its soles on the ground row - the pose's json "ground" (the row its
soles rest on: the ring may dip lower, a slam's blade striking in front of her) or its lowest square - or `lift` rows
over it in the air. The idle is the design alone (no breathing: hero_reels cuts her idle snippets from these actions).
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
a key pose with a part of it moved (PARTS, in the pose's own squares, less the design's head the pose carries):
her streaming hair waved, the ring turned about the hand that holds it; everything else of the pose checked unchanged.
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

HERO = "qiyana"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "qiyana", "hd")
STAND = 34                     # the idle's standing column: under her belt's middle, between her feet
HEAD = (20, 0)                 # the design's head box top-left (column, row) in hd/idle.png (design_qiyana_poses.HEAD)
HEAD_WH = (28, 27)             # its size (columns 20-47, rows 0-26: crest to chin)
VPAD = 30                      # an in-between's picture is this much bigger on every side (inbetween.vary)


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


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(70, 70, 60, 12))      # room for the ring swung behind and before her, the leap
        self.outline = D.outline

    def head(self, d, hx, hy):
        """The design's head as the pose at (hx, hy) carries it: the head box's squares the pose holds unchanged."""
        (x0, y0), (w, h) = HEAD, HEAD_WH
        box = self.d[y0:y0 + h, x0:x0 + w]
        sub = d[hy:hy + h, hx:hx + w]
        m = np.zeros(d.shape[:2], bool)
        h, w = sub.shape[:2]
        m[hy:hy + h, hx:hx + w] = (box[:h, :w, 3] > 0) & (sub == box[:h, :w]).all(-1)
        return m

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), sway=(), spins=()):
        """The pose placed by its head box and its ground; moves / sway / spins (inbetween.vary, by PARTS' names): an
        in-between made from it, placed where the pose stands (every square in no part checked unchanged)."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name)
        left = rig.ox + HEAD[0] - hx + dx
        top = rig.GY - ground - lift
        if moves or sway or spins:
            head = self.head(d, hx, hy)
            d = IB.vary(d, without(d, PARTS[name], head), self.outline, moves, sway, None, head, VPAD, name,
                        spins=spins)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


HAIR = ((162, 148, 185), (244, 249, 252), (203, 205, 227), (130, 126, 146))     # her hair's colours (the design's)


def hair_in(d, box):
    """Her hair's squares inside the box (x0, y0, x1, y1): the hair's colours, and the near-black squares that edge
    them where nothing but hair and air is next to them (the hair's own outline; a line between the hair and an arm
    lying over it stays with the arm)."""
    x0, y0, x1, y1 = box
    rgb, op = d[..., :3].astype(int), d[..., 3] > 0
    inb = np.zeros(op.shape, bool)
    inb[y0:y1 + 1, x0:x1 + 1] = True
    hair = op & inb & np.any([(rgb == c).all(-1) for c in HAIR], axis=0)
    dark = op & inb & (IB.lum(d[..., :3]) < IB.DARK)
    other = op & ~hair & ~dark
    near = lambda m: np.pad(m, 1)[2:, 1:-1] | np.pad(m, 1)[:-2, 1:-1] | np.pad(m, 1)[1:-1, 2:] | np.pad(m, 1)[1:-1, :-2]
    return hair | (dark & near(hair) & ~near(other))


def without(d, parts, head):
    """Each part's mask (polygons, boxes; ("hair", box): hair_in) less the head's squares, as row runs (x0, y, x1, y)
    for inbetween.vary (rig_taliyah's)."""
    out = {}
    for k, items in parts.items():
        m = IB.part_mask(d.shape, [it for it in items if it[0] != "hair"])
        for it in items:
            if it[0] == "hair":
                m |= hair_in(d, it[1])
        m &= ~head
        runs = []
        for y in range(m.shape[0]):
            xs = np.nonzero(m[y])[0]
            if not len(xs):
                continue
            cut = np.nonzero(np.diff(xs) > 1)[0]
            runs += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
        out[k] = runs
    return out


# the in-betweens' parts, in each pose's own squares (boxes (x0, y0, x1, y1) inclusive; ("hair", box): her hair in the
# box, hair_in), the design's head always taken out. A hair part has an arm lying over its edge: it moves only in under
# that arm (lowered when the arm is below it, lifted or swung toward her when the arm is above it), never away from it
# (the hair under the arm is not drawn).
PARTS = {
    # E's dash: the hair streaming back from her head, above the far arm and the ring (they lie over its lower edge)
    "e_dash": {"hair": [("hair", (36, 4, 62, 24))]},
    # E's landing: the hair hanging under the far arm
    "e_hit": {"hair_lo": [("hair", (4, 27, 24, 42))]},
    # the attack's strike: the hair streaming back above the far arm
    "a_strike": {"hair": [("hair", (2, 9, 21, 25))]},
    # the ult's slam: the hair hanging under the raised far arm
    "r_slam": {"hair": [("hair", (5, 19, 24, 40))]},
    # the death's stagger: the ring hanging from her near hand (all of it left of the fist, column 37 on); d_lie: the
    # ring lying on the ground, its end ornament in her hand (columns 44 on stay: the hand)
    "d_fall": {"ring": [(0, 33, 36, 63)]},
    "d_lie": {"ring": [(0, 38, 38, 51), (39, 45, 43, 51)]},
}
GRIP = {"d_fall": (37, 42), "d_lie": (46, 47)}      # where the hand holds the ring (the turns' point)


def rows_wave(shape, y0, y1, k):
    """The moves of hanging hair swinging: its whole rows shifted sideways, nothing on row y0 and k columns (negative:
    to the left) on row y1, the rows past it going with it - inbetween.wave on its side (rig_naafiri's). -> (dx, dy)."""
    H, W = shape[:2]
    dx = np.zeros((H, W), int)
    for y in range(H):
        t = min(max((y - y0) / (y1 - y0), 0.0), 1.0)
        dx[y, :] = int(round(k * t))
    return dx, np.zeros((H, W), int)


# ms per frame; the kit's ticks (tools/kit/build_qiyana.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 420 ms = atk_dur 25, the blow on the strike frame (a_hit 10 = 167 ms; the strike from 140 ms); skill 400 ms =
# q_dur 24, the sweep from 150 ms (q_at 10 = 167 ms); skill2 333 ms = e_dur 20, the dash then the slash (the hit comes at
# the kit's landing); ult 667 ms = r_dur 40, the slam from 250 ms (r_at 16 = 267 ms, the shockwave)
# The in-betweens (2026-11-14: E was the dash, the dash moved two squares, the slash; the death the stagger and the sitting
# pose held twice each): the spans shared out over more frames (inbetween.spans: whole ms, none under 50), so every
# action is as long as it was and the slash still starts at 200, the fall at 340.
MS = {"idle": [1000], "run": [130] * 4, "attack": [140, 110, 90, 80], "skill": [150, 110, 140],
      "skill_w": [150, 110, 140], "skill_r": [150, 110, 140], "skill_g": [150, 110, 140],
      "skill2": IB.spans((200, 3), (133, 2)), "ult": [120, 130, 200, 217], "hit": [100, 100],
      "dead": IB.spans((140, 1), (200, 2), (300, 2), (600, 1))}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run: contact, passing, contact on the other leg, passing; the ring slung across her back)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]     # each on its support foot: the passing frames stand taller
    # attack (League's Attack1: the ring swung back on one leg, springing forward to strike, landing with the hair
    # coming down, back)
    hair = lambda x0, x1, k: [("hair", x0, x1, k, "right")]
    out["attack"] = [f("a_wind", dx=-1), f("a_strike", dx=2, lift=3),
                     f("a_strike", dx=2, lift=1, sway=hair(2, 21, -4)), f("idle")]
    # Q Edge of Ixtal (League's Spell1: the ring dragged low behind her, swept round to the front, the follow-through)
    out["skill"] = [f("q_wind", dx=-1), f("q_sweep", dx=2), f("q_end", dx=2)]
    # the same cast once per element on her ring, each with its own sweep drawn in (qiyana_bake.json): river, rock, grass
    for x in ("skill_w", "skill_r", "skill_g"):
        out[x] = [c.copy() for c in out["skill"]]
    # E Audacity (League's Spell3 -> Spell3_Hit: the low dash with the ring trailing, the hair streaming down; the ring
    # swung round to the front in the air - the attack's strike -; the landing slash with the hair still up, settled)
    out["skill2"] = [f("e_dash", dx=1, lift=2), f("e_dash", dx=3, lift=2, sway=hair(36, 62, -4)),
                     f("a_strike", dx=3, lift=1), f("e_hit", dx=2, sway=[("hair_lo", 6, 22, 3, "right")]),
                     f("e_hit", dx=2)]
    # R Supreme Display of Talent (League's Spell4: up with the ring raised behind her, the slam forward, held while
    # the hanging hair swings in after it)
    slam = load_pose("r_slam")[0]
    out["ult"] = [f("r_leap", lift=4), f("r_leap", lift=10), f("r_slam", dx=2),
                  f("r_slam", dx=2, moves=[("hair", rows_wave(slam.shape, 20, 38, 3), "under")])]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: the stagger with the ring slipping from her hand, swinging out; down to sit, the ring
    # dropping to the ground)
    ring = lambda pose, deg: [("ring", GRIP[pose], deg, "under")]
    out["dead"] = [f("d_fall", dx=-1, flash=True), f("d_fall", dx=-2, spins=ring("d_fall", 10)),
                   f("d_fall", dx=-2, spins=ring("d_fall", 20)), f("d_lie", dx=-2, spins=ring("d_lie", 9)),
                   f("d_lie", dx=-2, spins=ring("d_lie", 5)), f("d_lie", dx=-2)]
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
    ap.add_argument("--no-bake", action="store_true", help="leave the forward effects out (assets/source/native/qiyana_bake.json)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if not a.no_bake and os.path.isfile(lp(os.path.join(ROOT, "assets", "source", "native", "qiyana_bake.json"))):
        acts = C.rig.bake(acts)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
