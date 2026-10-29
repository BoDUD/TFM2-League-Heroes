#!/usr/bin/env python3
"""league_rumble's action frames: Rumble's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-25: 「动作帧用 Codex 骨架姿势包」 - the skeletons set after League's own frames: 「用英雄联盟本地客户端的动作帧重做兰博的
姿势包」 - then 「codex的动作帧也交付了 你做到完美后喊我review」).

    python tools/art/rig_rumble.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_rumble.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_rumble_model.py, design_rumble_poses.py):
  hd/idle.png         Rumble in his mech, 3/4 front facing right, 92 x 62 at PPU 1.75 (36 game px mohawk to the red
                      feet): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/rumble/POSE_PROMPTS.md): a_wind a_smash q_aim q_spray e_aim e_recoil r_crouch
                      r_launch run1-4 d_drop d_down.
Placing a pose (rig_yorick's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as the pose pack's skeleton moves the head in that frame (HEAD_DX, rounded) and dx squares more by hand; its
lowest square on the ground row (the red feet; the ball smashed down or the toppled hull where those are lowest), or
`lift` rows over it. The idle is the design alone (no breathing: hero_reels cuts the idle snippets from these actions).
Flamespitter's fire is drawn into the skill frames by the bake (assets/source/native/rumble_bake.json: league_rumble_fx
q_flame from q_spray's first moment on, its nozzle on the cannon's muzzle: tools/art/import_rumble_fx.py).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
import pack_rumble_poses as PK  # noqa: E402
from design_rumble_poses import POLY  # noqa: E402

HERO = "rumble"
PPU = 1.75
SRC = os.path.join(ROOT, "assets", "source", "rumble", "hd")
STAND = 46                     # the idle's standing column: under the hull's bottom middle, between the red feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far the head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}
# Overheat (红温, the user 2026-10-25: 「红温特效补一个吧」): League turns the mech's metal glowing red while the yordle stays
# himself (his model under rumble_overheat_base.tex, rendered from the local client). The oh_ tags are his frames with
# every square of the mech - brass, steel, the ball, the cannon, the pods, the joints - put on this crimson ramp by its
# brightness (the outline kept); the pilot's head (POLY, where the pose's head box went) and his blue fur in the bowl under
# it keep their colours. league_rumble's view hook (the add-on) swaps them in while he is Overheated; his attacks
# play oh_attack from the data too.
HOT = [(45, (42, 8, 8, 255)), (75, (88, 16, 14, 255)), (110, (140, 24, 18, 255)), (150, (196, 38, 26, 255)),
       (195, (238, 70, 40, 255)), (256, (255, 140, 90, 255))]


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
        self.rig = R.Rig(D, pad=(40, 130, 40, 12))      # room for the ball swung up, the cannon raised, the fire poured
        self.outline = D.outline
        # pinholes the read-back left where two outlines meet (gap-check): enclosed holes of at most 3 squares anywhere
        # in the frame that the standing frame does not have take the outline (the gaps between the ball, the arm and
        # the legs are bigger and stay)
        self.rig.fill_rows, self.rig.CRACK = (-40, D.H), 3
        self.rig.idle_canvas = self.frame("idle")

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas, the head box's top-left in the picture)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX[name]
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift), (hx, hy)

    def frame(self, name, dx=0, lift=0, flash=False, hot=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top), (hx, hy) = self.placed(name, dx, lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        if hot:
            can = self.red_hot(can, (left + hx - HEAD[0], top + hy - HEAD[1]))
        return R.flash(can) if flash else can

    def red_hot(self, can, at):
        """The mech glowing red (HOT), the pilot as he is: `at` is where the design's (0, 0) lies for the head (POLY)."""
        from PIL import ImageDraw
        img = Image.new("L", (can.shape[1], can.shape[0]), 0)
        ImageDraw.Draw(img).polygon([(x + at[0], y + at[1]) for x, y in POLY], fill=255)
        head = np.asarray(img) > 0
        # the pilot under his head: his blue fur and arms in the bowl, a band the head box's width, 16 rows down
        pilot = np.zeros_like(head)
        x0, y0 = at[0] + HEAD[0], at[1] + HEAD[1] + (PK.HEAD[1] - PK.HEAD[0])
        pilot[max(0, y0 - 4):max(0, y0 + 16), max(0, x0 - 4):max(0, x0 + (PK.HEAD[3] - PK.HEAD[2]) + 4)] = True
        rgb = can[..., :3].astype(int)
        op = can[..., 3] > 0
        ink = (rgb == np.array(self.outline[:3])).all(-1)
        blue = (rgb[..., 2] - rgb[..., 0] > 40) & (rgb[..., 2] >= rgb[..., 1])
        metal = op & ~ink & ~head & ~(pilot & blue)
        lum = rgb @ np.array([299, 587, 114]) // 1000
        out = can.copy()
        lo = 0
        for hi, col in HOT:
            m = metal & (lum >= lo) & (lum < hi)
            out[m] = col
            lo = hi
        return out


# ms per frame; the kit's ticks (tools/kit/build_rumble.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the ball landing on the smash frame (a_hit 11 = 183 ms); Flamespitter 1500 ms = q_t 90,
# the cannon levelled, the fire from q_first 8 (133 ms) to the end; Electro-Harpoon 400 ms = e_dur 24, fired on e_rel 8
# (133 ms); The Equalizer 600 ms = r_dur 36, the rockets off on r_rel 14 (233 ms)
MS = {"idle": [1000], "run": [150] * 4, "attack": [183, 184, 100], "skill": [133, 1367], "skill2": [133, 267],
      "ult": [233, 367], "hit": [100, 100], "dead": [140, 260, 300, 600]}
MS.update({f"oh_{t}": MS[t] for t in ("idle", "run", "attack", "hit", "dead")})
# Flamespitter on the move: the run's four steps twice, standing the same length (the fire loops within them)
MS.update({"q_run": [150] * 8, "q_stand": [1200]})

# ------------------------------------------------------------------ Flamespitter on the move (q_run, q_stand)
# League's Rumble walks while he flames (the user, 2026-10-29: 「兰博不会边走边放火吗」 -> 「就这么做」, the frames approved as
# drafted): league_rumble's add-on lets him walk through Q and its view hook plays q_run / q_stand while it lasts (the main
# pack keeps him standing: without the add-on no run frame carries the fire). Each q_run step is q_spray's body - the hull,
# the levelled cannon, the ball hanging - moved whole so its brass bowl sits where the run step's bowl sits (the run bobs
# up to 10 rows), over that step's legs (the parts under its bowl, not the ball, specks dropped); the fire is the bake's
# q_flame moved with the body, so it always pours from the muzzle. Nothing is drawn anew.
SQ = np.ones((3, 3), bool)
LEG_MIN = 40                    # a piece of the legs layer smaller than this is a speck of an arm or the ball: dropped


def bowl(can):
    """The brass bowl (the biggest brass part): (its bottom row, its centre column, its right column)."""
    r, g, b = (can[..., i].astype(int) for i in range(3))
    brass = (can[..., 3] > 0) & (r > 150) & (g > 100) & (b < 100) & (r - b > 90)
    lab, k = ndimage.label(brass)
    big = lab == (np.argmax(ndimage.sum(brass, lab, range(1, k + 1))) + 1)
    ys, xs = np.nonzero(big)
    return int(ys.max()), int(round(xs.mean())), int(xs.max())


def legs_of(can, outline):
    """(the leg parts, the leg parts with their outline): the outline-separated parts whose middle lies under the bowl's
    bottom (2 rows up) and left of its right edge (6 on, the cannon beyond), not the spiked ball (a big part, mostly grey)."""
    low, _, right = bowl(can)
    op = can[..., 3] > 0
    ink = op & (can[..., :3] == np.array(outline[:3])).all(-1)
    lab, n = ndimage.label(op & ~ink)
    sel = np.zeros_like(op)
    for k in range(1, n + 1):
        m = lab == k
        ys, xs = np.nonzero(m)
        rgb = can[m][:, :3].astype(int)
        grey = ((abs(rgb[:, 0] - rgb[:, 1]) < 25) & (abs(rgb[:, 1] - rgb[:, 2]) < 30)).mean()
        if len(ys) > 60 and grey > 0.7:
            continue
        if ys.mean() > low - 2 and xs.mean() <= right + 6:
            sel |= m
    full = sel | (ink & ndimage.binary_dilation(sel, structure=SQ))
    lab, n = ndimage.label(full, structure=SQ)
    for k in range(1, n + 1):
        if (lab == k).sum() < LEG_MIN:
            full[lab == k] = False
    return sel & full, full


def shifted(a, dy, dx):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = a[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
    return out


def q_run(C):
    """[(canvas, (dy, dx) the spray body moved)] for run1-4."""
    spray = C.frame("q_spray")
    sb, sc, _ = bowl(spray)
    own, _ = legs_of(spray, C.outline)
    body = spray.copy()
    body[own] = 0
    op = body[..., 3] > 0
    ink = op & (body[..., :3] == np.array(C.outline[:3])).all(-1)
    body[ink & ~ndimage.binary_dilation(op & ~ink, structure=SQ)] = 0      # the spray legs' outline left on its own
    out = []
    for name in ("run1", "run2", "run3", "run4"):
        run = C.frame(name)
        rb, rc, _ = bowl(run)
        _, legs = legs_of(run, C.outline)
        dy, dx = rb - sb, rc - sc
        top = shifted(body, dy, dx)
        can = np.zeros_like(run)
        can[legs] = run[legs]
        can[top[..., 3] > 0] = top[top[..., 3] > 0]
        out.append((C.rig.finish(can), (dy, dx)))
    return out


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's run: a long stomping stride on each leg, the passing frames a square higher)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack2: the ball raised over his head, smashed down before him, back)
    out["attack"] = [f("a_wind"), f("a_smash"), f("idle")]
    # Flamespitter (Spell1: the cannon levelled, then held spraying while the fire pours: the bake)
    out["skill"] = [f("q_aim"), f("q_spray")]
    # Electro-Harpoon (Spell3: aimed, the kick of the shot)
    out["skill2"] = [f("e_aim"), f("e_recoil")]
    # The Equalizer (Spell4: crouched with the pods to the sky, the kick of the rockets going off)
    out["ult"] = [f("r_crouch"), f("r_launch")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: knocked back, toppled onto his back with the legs in the air)
    out["dead"] = [f("d_drop", flash=True), f("d_drop"), f("d_down"), f("d_down")]
    # Overheated (红温): the same frames with the mech glowing red, for the tags he plays while it lasts (no casts then)
    out["oh_idle"] = [f("idle", hot=True)]
    out["oh_run"] = [f("run1", hot=True), f("run2", hot=True), f("run3", hot=True), f("run4", hot=True)]
    out["oh_attack"] = [f("a_wind", hot=True), f("a_smash", hot=True), f("idle", hot=True)]
    out["oh_hit"] = [f("idle", dx=-2, flash=True, hot=True), f("idle", dx=-1, hot=True)]
    out["oh_dead"] = [f("d_drop", flash=True, hot=True), f("d_drop", hot=True), f("d_down", hot=True),
                      f("d_down", hot=True)]
    # Flamespitter on the move (the add-on): the spray held still, and the spray body on the run's legs; each step's
    # body offset kept for the fire (baked)
    out["q_stand"] = [f("q_spray")]
    steps = q_run(C)
    C.q_moved = {id(can): moved for can, moved in steps}
    out["q_run"] = [can for can, _ in steps] * 2
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


def baked(C, acts):
    """The bake's effects laid into their tags (Flamespitter's fire), when the effect sheet is there."""
    path = os.path.join(ROOT, "assets", "source", "native", f"{HERO}_bake.json")
    sheet = os.path.join(ROOT, "league", "effects", "league_rumble_fx#sheet.png")
    if not (os.path.isfile(lp(path)) and os.path.isfile(lp(sheet))):
        return acts
    with open(lp(path), encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["items"] = [e for e in cfg["items"] if e["into"] in acts]        # (--tags: only the tags asked for)
    if not cfg["items"]:
        return acts
    out = C.rig.bake(acts, cfg=cfg)
    # q_run: the fire laid for q_spray's muzzle, moved with the step's body (bake keeps each frame's body array)
    moved = getattr(C, "q_moved", {})
    for lay, _ in out.get("q_run", []):
        dy, dx = moved[id(lay["body"])]
        for key in ("over", "under"):
            if lay[key] is not None:
                lay[key] = shifted(lay[key], dy, dx)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = baked(C, frames(C, a.tags.split(",") if a.tags else None))
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
