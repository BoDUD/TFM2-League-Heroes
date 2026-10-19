#!/usr/bin/env python3
"""league_quinn's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way: no
Codex strips, lossless poses compared with League's clips - tools/lol/anim_graph.py Quinn, pose_ref.py).

    python tools/art/rig_quinn.py --parts DIR       # the idle design with its parts tinted + pose tries (12x)
    python tools/art/rig_quinn.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_quinn.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_quinn.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_quinn_model.py, the user's picks 2026-10-19; 38 game px at PPU 1.3, one palette):
idle.png (Q-1, 3/4 front, the crossbow arm held out to the right, 45 x 49: every standing action's base and the one face
of every frame), side.png (S-2, side-on, 47 x 49), valor.png (Valor gliding, 34 x 27: the circling buff picture, not a
frame) and ride.png (her riding Valor, 67 x 46: R's ride). Every pose is lossless: parts cut square by square from a
design and only moved by whole squares, quarter turns about half-integer pivots and mirrors.
Parts of the idle design: the crossbow arm (the sleeve from the shoulder and the crossbow; it turns about SHOULDER),
the near leg (image left) and the far leg (image right) from LEG_TOP down; the rest is the body (the head, the hood,
the pauldron, the cape, the torso).
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
import quinn_legs as QL  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet  # noqa: E402

HERO = "quinn"
PPU = 1.3
SRC = os.path.join(R.ROOT, "assets", "source", "quinn", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def stand_col(d, rows=3):
    """The middle of the lowest `rows` rows' squares: where the design stands."""
    op = d[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys.max() - rows + 1:ys.max() + 1].any(0))[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


def dark(d):
    return (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 70)


# ------------------------------------------------------------------------------------------------- the idle's parts
SHOULDER = (20.5, 17.5)       # (x, y) the crossbow arm turns about
LEG_TOP = 33                  # the legs: rows LEG_TOP to the soles, split at LEG_X
LEG_X = 16


def design():
    d = load("idle.png")
    D = CutDesign(d, px=stand_col(d))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    op = d[..., 3] > 0
    arm = op & (((yy >= 10) & (yy <= 21) & (xx >= 22)) | ((yy >= 15) & (yy <= 20) & (xx >= 20)))
    D.part("arm", arm)
    legs = op & (yy >= LEG_TOP) & (xx >= 7)
    D.part("near_leg", legs & (xx < LEG_X))
    D.part("far_leg", legs & (xx >= LEG_X))
    D.part("body", D.rest())
    return D


TINT = {"arm": (60, 120, 255), "near_leg": (255, 220, 0), "far_leg": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# the ride's own head (rows 0..RIDE_CHIN, cols RIDE_HEAD_X) gives way to the idle's (one face in every frame)
IDLE_HEAD = (0, 15, 8, 21)     # rows / cols of the idle's head: the visor crest to the chin, the hood
RIDE_HEAD = (0, 14, 33, 45)
RIDE_CLEAR = 12                # the ride head's rows cleared (below them its chin and collar meet the arm)


def skin(d):
    c = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (c[..., 0] > 200) & (c[..., 1] > 160) & (c[..., 2] > 130) & (c[..., 0] - c[..., 2] > 25)


def ride_design(D):
    """ride.png with the idle's head on it: the ride's head squares cleared, the idle's head (its face's skin box laid
    on the ride face's: the right edges and the chins level) put over them."""
    r = load("ride.png")
    y0, y1, x0, x1 = IDLE_HEAD
    head = D.d[y0:y1 + 1, x0:x1 + 1].copy()
    head[D.parts["arm"][y0:y1 + 1, x0:x1 + 1]] = 0
    ry0, ry1, rx0, rx1 = RIDE_HEAD
    hs, rs = skin(head), skin(r[ry0:ry1 + 1, rx0:rx1 + 1])
    hy, hx = np.nonzero(hs)
    ry, rx = np.nonzero(rs)
    dy = (ry.max() + ry0) - (hy.max() + y0)
    dx = (rx.max() + rx0) - (hx.max() + x0)
    out = r.copy()
    out[ry0:RIDE_CLEAR + 1, rx0:rx1 + 1] = 0
    ty, tx = y0 + dy, x0 + dx
    if ty < 0:                                   # the idle's head is taller: the whole ride goes down to make room
        out = np.concatenate([np.zeros((-ty, out.shape[1], 4), np.uint8), out])
        ty = 0
    m = head[..., 3] > 0
    sub = out[ty:ty + head.shape[0], tx:tx + head.shape[1]]
    sub[m] = head[m]
    return out


class Form:
    """The idle design's layers and the other designs; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.other = {n: self.placed(d) for n, d in (("side", load("side.png")), ("ride", ride_design(D)))}
        # League's skeleton frame by frame (tools/lol/league_joints.py assets/source/quinn/poses.json -> hd/
        # quinn_joints.json) and the legs drawn on it (tools/art/quinn_legs.py, league_riven's way): the body without its
        # legs and without the crossbow arm (a layer of its own, turned losslessly)
        with open(lp(os.path.join(SRC, "quinn_joints.json")), encoding="utf-8") as f:
            self.J = json.load(f)
        # the run from a camera nearly side-on (assets/source/quinn/poses_side.json, yaw 75: the run is a side-on move;
        # at the 3/4 camera League's stride projected to thighs of +-30 degrees, league_riven's run reaches +-50)
        with open(lp(os.path.join(SRC, "side", "quinn_joints.json")), encoding="utf-8") as f:
            self.JS = json.load(f)
        self.P = QL.parts(D.d)
        b = QL.body(D.d)
        b[D.parts["arm"]] = 0
        self.BODY = pad(b)
        # Codex's leg poses (tools/art/design_quinn_legs.py): the legs of each, on the idle's grid, and how far the
        # upper body goes down onto them
        with open(lp(os.path.join(SRC, "legs.json")), encoding="utf-8") as f:
            self.LEG_META = json.load(f)
        self.LEGS = {}
        for k, m in self.LEG_META.items():
            img = load(f"legs_{k}_only.png")
            lay = np.zeros((D.H + 2 * P, D.W + 2 * P, 4), np.uint8)
            x0 = P - m["padx"]
            sub = img[:lay.shape[0] - P, max(0, -x0):]
            lay[P:P + sub.shape[0], max(0, x0):max(0, x0) + sub.shape[1]] = sub[:, :lay.shape[1] - max(0, x0)]
            self.LEGS[k] = lay

    def placed(self, d):
        """Another design in a padded layer of the idle design's size, standing on the same point and ground."""
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(d)
        y0, x0 = max(0, top), max(0, left)
        sub = d[y0 - top:, x0 - left:]
        sub = sub[:lay.shape[0] - y0, :lay.shape[1] - x0]
        lay[y0:y0 + sub.shape[0], x0:x0 + sub.shape[1]] = sub
        return lay

    def pose(self, crouch=0, whole=(0, 0), arm=(0, 0), arm_rot=0, legs=None, leg=None, fill=True):
        """crouch: rows the body (with the arm) sets down onto the legs; whole: the whole figure; arm: the crossbow arm
        moved, arm_rot quarter turns counter-clockwise about SHOULDER (1: pointing up); legs: ((near dx, dy),
        (far dx, dy)) for the idle's own legs; leg: one of Codex's leg poses instead (kneel, lunge, wide, back, tuck,
        step) - the body then goes down that pose's drop, plus crouch."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        L = self.L
        if leg:
            ux, uy = wx, wy + crouch + self.LEG_META[leg]["drop"]
            leg_layers = [(self.LEGS[leg], dict(dx=wx, dy=wy))]
        else:
            ux, uy = wx, wy + crouch
            (nx, ny), (fx, fy) = legs or ((0, 0), (0, 0))
            leg_layers = [(L["far_leg"], dict(dx=wx + fx, dy=wy + fy)), (L["near_leg"], dict(dx=wx + nx, dy=wy + ny))]
        layers = [*leg_layers,
                  (L["body"], dict(dx=ux, dy=uy)),
                  (L["arm"], dict(dx=ux + arm[0], dy=uy + arm[1], rot=arm_rot, about=SHOULDER))]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def drawn(self, j, ref=None, arm=(0, 0), arm_rot=0, air=False, lunge=0.5, shift=(0, 0)):
        """A frame on legs drawn on League's joints j (quinn_legs): the body moved forward / back lunge x League's
        pelvis travel from ref's (default the design pose), set on the ground by its lowest boot, or lifted as far as
        League's lower foot leaves the floor (air); the crossbow arm moved / turned losslessly; shift: the whole frame."""
        geo = QL.geometry(j, self.P)
        low = max(geo[k][2][1] + self.P[k]["drop"] for k in geo)
        d = self.J["design"]
        r = ref or d
        lift = 0.0
        if air:
            lift = max(0.0, min(-j["l_foot"][1], -j["r_foot"][1]) - min(-d["l_foot"][1], -d["r_foot"][1])) * QL.PPU
        dx = int(round((j["pelvis"][0] - r["pelvis"][0]) * QL.PPU * lunge)) + shift[0]
        dy = int(round(QL.GROUND - lift - low)) + shift[1]
        rig = self.rig
        can = rig.canvas()
        QL.draw_legs(can, {k: tuple(v + np.array((rig.ox + dx, rig.oy + dy)) for v in g) for k, g in geo.items()},
                     self.P)
        up = R.compose(rig, [(self.BODY, dict(dx=dx, dy=dy)),
                             (self.L["arm"], dict(dx=dx + arm[0], dy=dy + arm[1], rot=arm_rot, about=SHOULDER))])
        m = up[..., 3] > 0
        can[m] = up[m]
        return can

    def whole(self, name, dx=0, dy=0, flash=False):
        can = R.compose(self.rig, [(self.other[name], dict(dx=dx, dy=dy))])
        return R.flash(can) if flash else can

    ref_holes = None
    close_holes = _Form.close_holes
    MOST = _Form.MOST


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


def form():
    return Form(design(), rig_pad=(40, 50, 50, 20))


def tries(F):
    p = F.pose
    return [p(), p(arm_rot=1, arm=(1, -2)), p(crouch=2), p(whole=(-2, 0), arm=(0, -1)), F.whole("side"),
            F.whole("ride"), R.lie(F.rig, p(), 3, dx=2, sink=0), R.lie(F.rig, p(), 1, dx=-2, sink=0)]


# ------------------------------------------------------------------------------------------------- the actions
UP = dict(arm_rot=1, arm=(3, -2))     # the crossbow arm turned up to the sky, beside the head (never over the face)

# ms per frame; the kit's ticks (tools/kit/build_quinn.py) come from these
MS = {"idle": [150] * 8, "run": [117] * 8, "attack": [80, 70, 90, 110, 90],
      "skill": [90, 80, 100, 90, 110], "skill2": [60, 60], "e_flip": [50, 50, 50, 60, 90],
      "ult": [80, 100, 120, 200], "ult_ride": [100] * 4, "ult_land": [70, 70, 70, 70, 100, 100],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500],
      "r_idle": [160] * 4, "r_run": [90] * 4, "r_hit": [100, 100]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    T = {t: [r["j"] for r in rows] for t, rows in F.J["tags"].items()}
    dr = F.drawn
    out = {}
    # idle (League's Quinn_idle1: the crossbow held out, she breathes): the approved design, the body set down a row
    out["idle"] = [p(), p(), p(), p(crouch=1), p(crouch=1), p(crouch=1), p(crouch=1), p()]
    # run (Quinn_run, 8 frames of its 0.93 s stride, seen nearly side-on): the legs drawn on League's legs, the body
    # bobbing with them
    S = [r["j"] for r in F.JS["tags"]["run"]]
    out["run"] = [dr(j, ref=S[0]) for j in S]
    # auto attack (Quinn_attack1: her stance from League's frames, the shot kicking the crossbow up)
    # (the first and last frames are League's blends from and into its idle, whose back foot is lifted - our idle's own
    # legs stand there, so the attack starts and ends on the idle)
    kick = [(0, 0), (0, -2), (0, -1)]
    out["attack"] = [p()] + [dr(j, arm=k, lunge=0.7) for j, k in zip(T["attack"][1:4], kick)] + [p()]
    # Q Blinding Assault (quinn_spell1: the crossbow raised to the sky as Valor leaves, then the lunge after him)
    out["skill"] = [dr(T["skill"][0], lunge=0.7, **UP)] + [dr(j, lunge=0.7) for j in T["skill"][1:]]
    # E Vault (Quinn_spell3_dash: off the ground at the target, the legs trailing)
    out["skill2"] = [dr(j, air=True, lunge=0.5) for j in T["skill2"]]
    # Quinn_spell3_flip: she kicks off and somersaults back (the kick-off frame turned whole a quarter at a time,
    # counter-clockwise), lands (League's landing frame)
    kick_off = dr(T["e_flip"][0])
    tumble = lambda k, dx, up: shift(R.lie(rig, kick_off, k, dx=dx, sink=0), 0, -up)
    out["e_flip"] = [tumble(1, 0, 6), tumble(2, -1, 10), tumble(3, -2, 7), dr(T["e_flip"][4], shift=(-2, 0)), p()]
    # R Behind Enemy Lines (Quinn_Spell4_Channel: she sinks, springs up with the crossbow raised to call Valor down,
    # mounts him)
    out["ult"] = [dr(T["ult"][0]), dr(T["ult"][1]), dr(T["ult"][2], air=True, **UP), F.whole("ride", dy=-4)]
    # the ride (quinnvalor_run_glide): gliding, the whole group rising and falling
    out["ult_ride"] = [F.whole("ride", dy=-d) for d in (4, 5, 6, 5)]
    # Skystrike (QuinnRFinale: the two loop up through the air and she drops onto them): the group whole quarter turns
    # counter-clockwise (nose up, over, down), she lands (the somersault's landing, the channel's crouch), stands
    loop = lambda k, dx, up: shift(R.lie(rig, F.whole("ride"), k, dx=dx, sink=0), 0, -up)
    out["ult_land"] = [loop(1, 1, 6), loop(2, 0, 12), loop(3, -1, 6), dr(T["e_flip"][4]), dr(T["ult"][1]), p()]
    # hit (League's idle leaning toward its death): flashed, knocked back
    out["hit"] = [R.flash(dr(T["hit"][0], shift=(-2, 0))), dr(T["hit"][1], shift=(-1, 0))]

    # the death (quinn_death: she staggers back, her knees give and she pitches forward onto her face): League's first
    # three frames on drawn legs, then lying face down, head forward (the frame a quarter turn clockwise, her own
    # straight legs, the crossbow arm let down first so it lies along her), a bounce, lying
    DOWN = dict(arm_rot=3, arm=(-1, 2))

    def lying(sink, dx):
        return R.lie(rig, p(crouch=3, **DOWN), 3, dx=dx, sink=sink)
    out["dead"] = [dr(T["dead"][0]), dr(T["dead"][1], lunge=0.5), dr(T["dead"][2], lunge=0.5, arm=(0, 2)),
                   lying(0, 6), lying(2, 8), lying(0, 8), lying(2, 8), lying(2, 8)]
    # the add-on's ride form (addons/league_quinn): standing / moving / hit as the group gliding
    out["r_idle"] = [F.whole("ride", dy=-d) for d in (4, 5, 5, 4)]
    out["r_run"] = [F.whole("ride", dy=-d, dx=x) for d, x in ((4, 0), (6, 1), (5, 0), (3, -1))]
    out["r_hit"] = [F.whole("ride", dx=-2, dy=-4, flash=True), F.whole("ride", dx=-1, dy=-4)]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# League's Quinn_run: the design's own legs step whole under the body (each planted and sliding back, then lifted and
# carried forward, the far one half a cycle later), the body set down a row on each contact (league_wukong's walk).
from rig_wukong import _steps  # noqa: E402

WALK_STEP = dict(_steps(2, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    for (ndx, nup), (fdx, fup), bob, up_ in zip(st["near"], st["far"], st["bob"], st["rise"]):
        out.append(F.pose(whole=(0, bob - up_), legs=((ndx, -nup), (fdx, -fup))))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": a["run"], **{k: v for k, v in a.items() if k not in ("idle", "run")}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if not (a.audit or a.review or a.parts):
        F = form()
        F.rig.export(frames(F))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            import rig_wukong as RW
            RW.HERO = HERO
            RW.audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()}, "stand", D.px, "ground", D.ground)
    F = form()
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()
