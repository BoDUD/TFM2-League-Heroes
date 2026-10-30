#!/usr/bin/env python3
"""tft_daeja's action frames: Daeja's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-30: sprites by Codex from written prompts).

    python tools/art/rig_daeja.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_daeja.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_daeja), then ppu_restyle.py / ppu_hd.py --hero daeja

The pictures (tools/art/design_daeja_model.py, design_daeja_poses.py):
  hd/idle.png         Daeja standing upright, 3/4 facing right, 58 x 69 at PPU 1.72 (40 game px, the wing tips to his
                      feet): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size and density with the design's face
                      (assets/source/daeja/POSE_PROMPTS.md, design_daeja_poses.py): a_wind a_punch q_raise q_sweep e_beat
                      e_hop r_up r_fly1 r_fly2 r_blast r_land d_fall d_down.
Placing a pose: the pack drew every reference with his root on one canvas column and his lowest point on the ground
line, and Codex placed each pose over its reference; so a pose's pivot (its json: that column) goes on the design's
root column (DESIGN_PIVOT) and its lowest row on the design's ground line. The run is the idle's own legs stepping
(walk); the poses in the air were drawn standing on the line (the pack's rule) and are lifted here: the hop back (e_hop) and the ult's take-off, flight and blasts (r_up, r_fly1,
r_fly2, r_blast) - the flight flaps LEVEL -> UP between the blasts, bobbing a row.
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

HERO = "daeja"
PPU = 1.72
SRC = os.path.join(ROOT, "assets", "source", "daeja", "hd")
DESIGN_PIVOT = 32             # the design's root column (pack_daeja_poses' pelvis column 31.9)
POSES = ("a_wind", "a_punch", "q_raise", "q_sweep", "e_beat", "e_hop", "r_up", "r_fly1", "r_fly2", "r_blast", "r_land",
         "d_fall", "d_down")
E_LIFT = 8                    # the hop back's height (design rows; 4.7 game px)
HOVER = 22                    # the flight's height (design rows; 12.8 game px over the ground)
LIFT_MAX = HOVER + 2
# the flight's frames stand by the design's face pasted on them (design_daeja_poses: its json's face): their root columns,
# read back through Codex's fit of each raw drawing, wander a few squares from frame to frame
FACE_ALIGN = ("r_fly1", "r_fly2", "r_blast")
FACE_X = ("r_up", "r_land")   # the take-off and the landing: the face's column on the design's (out of and back into the idle), soles down

# ------------------------------------------------------------------------------------------------ the walk
# Codex's eight run frames kept the same leg ahead in all of them (the far leg trailing, the near one planted: no swap -
# 「走路感觉换腿不明显啊」, Sevika's and Violet's complaint), so the run is the pack's walk for big heroes on the idle
# (rig_galio.walk_frame = rig_braum's; the user's rule for heavy heroes: 「按照泰坦布隆那种走路方式这种腿就不会变形」): the idle
# as it is - wings, body, fists, tail - and the design's own two legs, cut out by their colours (LEG_COLOURS: the dark
# violets the legs alone use below the chest, each leg one patch of them with the outline round it), not by boxes (a box
# took the tail's blue tip with the far leg and broke the tail when the leg lifted). In each frame a leg is lifted by
# losing its top rows (the thigh turned toward us, its top staying under the chest plate) and set a little forward or
# back; the legs take turns; the body sits a row lower when both feet are down. No part turned, sheared or stretched.
WALK_TOP = 47                            # the design's first row of the legs (the chest plate's lower edge above it)
LEG_COLOURS = {(128, 87, 173), (81, 45, 110), (58, 34, 70), (34, 21, 44)}
# per frame: the near leg's (columns forward, rows lifted), the far leg's, the body's drop (rows): near ahead and down,
# the far leg lifting and passing it, far ahead and down, the near one lifting and passing
WALK = [((2, 0), (-2, 0), 1), ((1, 0), (-1, 3), 0), ((0, 0), (0, 5), 0), ((-1, 0), (1, 3), 0),
        ((-2, 0), (2, 0), 1), ((-1, 3), (1, 0), 0), ((0, 5), (0, 0), 0), ((1, 3), (-1, 0), 0)]
WALK_MS = 115
CRACK = 3                                # bare squares a step opens, this many across at most: a crack


def leg_masks(d):
    """The far and the near leg in the design: (far, near) boolean masks. Each leg is a patch of LEG_COLOURS under
    WALK_TOP reaching the feet; each outline square goes with the coloured square nearest to it (on a tie the body,
    then the near leg). The few loose squares of those colours inside a leg's box are that leg's."""
    c = d[..., :3].astype(int)
    op = d[..., 3] > 0
    H, W = op.shape
    rows = np.arange(H)[:, None] >= WALK_TOP
    paint = np.zeros((H, W), bool)
    for col in LEG_COLOURS:
        paint |= (c == col).all(-1)
    paint &= op & rows
    lab, n = ndimage.label(paint)
    parts = [lab == j for j in range(1, n + 1)]
    big = sorted((m for m in parts if m.sum() >= 30), key=lambda m: np.nonzero(m)[1].mean())
    if len(big) != 2:
        sys.exit(f"walk: {len(big)} leg patches, expected 2")
    far, near = big[0].copy(), big[1].copy()
    for m in parts:                                # a few squares of the same colours inside a leg's box: that leg's
        if m.sum() >= 30:                          # (a toe's shading, a lone square), elsewhere (a fist, the tail): not
            continue
        ys, xs = np.nonzero(m)
        for leg in (far, near):
            ly, lx = np.nonzero(leg)
            if ly.min() <= ys.min() and ys.max() <= ly.max() and lx.min() <= xs.min() and xs.max() <= lx.max():
                leg |= m
                break
    ink = op & (c.sum(-1) < 90)
    # every outline square goes with the coloured square nearest to it: the body's (the tail, the fists, the hips),
    # the near leg's or the far leg's - on a tie the body first (the tail is in front of the far leg), then the near leg
    # (drawn over the far one)
    colour = op & ~ink
    dist = [ndimage.distance_transform_edt(~m) for m in (colour & ~far & ~near, near, far)]
    pick = np.argmin(np.stack(dist), axis=0)       # argmin keeps the first of equals
    label = np.zeros((H, W), int)
    label[far] = 1
    label[near] = 2
    sel = ink & rows
    label[sel & (pick == 1)] = 2
    label[sel & (pick == 2)] = 1
    return label == 1, label == 2


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - LIFT_MAX)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its root column (its json's pivot) on the design's, its
        lowest row on the ground; the flight (FACE_ALIGN) by its face on the design's, so the body hangs still in the
        air while the wings beat."""
        m = meta(name)
        if name in FACE_ALIGN:
            return -m["face"][0], -m["face"][1]
        if name in FACE_X:
            return -m["face"][0], self.d.shape[0] - p.shape[0]
        return DESIGN_PIVOT - m["pivot"][0], self.d.shape[0] - p.shape[0]

    def walk(self, near_step, far_step, drop):
        """The idle with the legs stepping: each leg's squares moved (dx, -lift) after losing its top `lift` rows, the
        far leg first, the near one over it, the body over both and `drop` rows lower."""
        idle = self.frame("idle")
        x0, y0 = self.rig.ox, self.rig.oy
        H, W = idle.shape[:2]
        op = idle[..., 3] > 0
        far_d, near_d = leg_masks(self.d)
        far = np.zeros((H, W), bool)
        near = np.zeros((H, W), bool)
        dh, dw = far_d.shape
        far[y0:y0 + dh, x0:x0 + dw] = far_d
        near[y0:y0 + dh, x0:x0 + dw] = near_d
        body = idle.copy()
        body[near | far] = 0
        out = np.zeros_like(idle)
        for m, (dx, lift) in ((far, far_step), (near, near_step)):
            leg = np.where(m[..., None], idle, 0).astype(np.uint8)
            top = np.nonzero(m.any(1))[0].min()
            leg[:top + lift] = 0
            ys, xs = np.nonzero(leg[..., 3] > 0)
            out[ys - lift, xs + dx] = leg[ys, xs]
        if drop:
            body = np.roll(body, drop, axis=0)
        m = body[..., 3] > 0
        out[m] = body[m]
        # what a step leaves bare: the squares the figure covered in the idle that nothing covers now. A thin run of
        # them (at most CRACK squares) with the figure on both ends - across the row or down the column - is a crack
        # (the slit beside a leg set forward or back) and takes the outline; a run open on one side (where a lifted
        # foot's toes were) is ground. A pinhole the step closes off (one or two squares) takes the outline too.
        wop = out[..., 3] > 0
        bare = op & ~wop
        fill = np.zeros_like(bare)
        for a_, w_, f in ((bare, wop, fill), (bare.T, wop.T, fill.T)):
            for y in np.nonzero(a_.any(1))[0]:
                xs = np.nonzero(a_[y])[0]
                for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
                    lo, hi = run[0] - 1, run[-1] + 1
                    if len(run) <= CRACK and lo >= 0 and hi < w_.shape[1] and w_[y, lo] and w_[y, hi]:
                        f[y, run] = True
        own = ndimage.binary_fill_holes(op) & ~op
        lab, n = ndimage.label(ndimage.binary_fill_holes(wop) & ~wop & ~own)
        for j in range(1, n + 1):
            if (lab == j).sum() <= 2:
                fill |= lab == j
        out[fill & ~wop] = (*self.outline, 255)
        return out

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_daeja.py) match these (a frame's start in ticks = ms x 0.06): attack
# 400 ms = atk_dur 24, the bolt leaves on a_rel 8 (133 ms: the punch); Windblast 500 ms = q_dur 30, the wave on q_rel 14
# (233 ms: the sweep); Wingbeat Retreat 400 ms = e_dur 24, the gust and the hop on e_rel 6 (100 ms: the hop); Sky Gale
# 1900 ms = its 114 ticks: the take-off over r_rise 24 (400 ms), three blasts 24 ticks apart (400 ms each: the blast
# 200 ms on ticks 24 / 48 / 72, then wings level and up), the landing r_land 18 (300 ms)
BLAST = [200, 100, 100]
MS = {"idle": [1000], "run": [WALK_MS] * 8, "attack": [133, 267], "skill": [233, 267], "skill2": [100, 300],
      "ult": [133, 133, 134] + BLAST * 3 + [300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [C.walk(n_, f_, r_) for n_, f_, r_ in WALK]
    # attack (the fist drawn back, then thrust out: the wind bolt)
    out["attack"] = [f("a_wind"), f("a_punch")]
    # Windblast (the wings raised back, then swept forward)
    out["skill"] = [f("q_raise"), f("q_sweep")]
    # Wingbeat Retreat (one beat of the wings, the hop back off the ground)
    out["skill2"] = [f("e_beat"), f("e_hop", lift=E_LIFT)]
    # Sky Gale (the take-off rising, three blasts in the air each followed by a flap, down on his feet)
    up = [f("r_up", lift=HOVER * k // 3) for k in (1, 2, 3)]
    air = []
    for _ in range(3):
        air += [f("r_blast", lift=HOVER), f("r_fly1", lift=HOVER + 1), f("r_fly2", lift=HOVER)]
    out["ult"] = up + air + [f("r_land")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (knocked back, down on his knees)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down")]
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
