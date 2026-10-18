#!/usr/bin/env python3
"""league_xinzhao redone at PPU 1.5 from Codex's chibi picture (assets/source/xinzhao/PICTURE_PROMPT_PPU.md, read back
and cut to 63 rows by tools/art/design_xinzhao_hd.py), every action posed after League's own clip frame by frame the way
league_jax was (tools/art/rig_jax_hd.py on ppu_rig.Driver; the user: 「动作帧不让 Codex 画，按英雄联盟原版动画的骨骼一帧
一帧摆，特效沿用现在的」).

    python tools/art/design_xinzhao_hd.py                                          # hd/design.png (+ picture.png below)
    python tools/lol/league_joints.py assets/source/xinzhao/poses.json --out <dir>  # League's joints (once)
    python tools/art/rig_xinzhao_hd.py --parts DIR                                 # the parts tinted (12x)
    python tools/art/rig_xinzhao_hd.py --joints <dir>/xinzhao_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_xinzhao_hd.py --joints <dir>/xinzhao_joints.json          # orig strips + the 1x sheet

The design's picture (hd/picture.png) is hd/design.png at 12 px a square, read back square for square (Design regrid 12:
the design exactly, its own 40 colours as the palette).

Parts (design squares, 63 rows topknot to soles): the spear - its purple blade with the silver crescent hook, the
streamer and the gold collar (low behind him at the left), the shaft's two visible stretches and the iron butt over his
front shoulder: ONE rigid prop on one straight line (SPEAR_A -> SPEAR_B; the stretch hidden behind his body drawn as a
straight shaft of its own brown, ppu_rig.Design.shaft), turned whole about his fist with League's weapon (the blade end
weapon_a to the butt weapon_b) and drawn BEHIND the body unless League's spear comes forward; his near arm (gold-trimmed
purple sleeve, brown forearm guard, the gloved fist on the shaft) turned about the shoulder with League's shoulder-to-
hand, the fist over the shaft; both legs as a stub of trousers and a shin (gold knee, steel greave, boot) turned at the
knee with League's thigh (rigid, rig_jax_hd's way); the upper body (head, ribbons, coat, the open far hand) moved with
League's pelvis and leaning with its chest, never turned. The run: the design's own two legs moved whole (rig_jax_hd's
WALK, league_braum's approved walk). The idle: the upper body, the arm and the spear sinking whole rows over the standing
legs (breathing, the sheet's 8 frames). skill2 and ult end with the W slash and the R tell drawn into the frames as
before (assets/source/native/xinzhao_bake.json, Rig.bake). The death ends lying: the figure a quarter turn.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "xinzhao"
PPU = 1.5
ROWS = 42                                    # game rows topknot to soles (the 1x idle's)
SPEC_HEIGHT = 42                             # assets/source/xinzhao/poses.json "height"
SQUARE = 12                                  # px a square in hd/picture.png
PIVOT_COL = 60                               # the coat's front panel, between his feet

# the spear's centre line (design squares): the blade's tip and the butt spike's tip
SPEAR_A = (1.5, 48.0)
SPEAR_B = (100.0, 3.7)


def on_spear(x):
    k = (SPEAR_B[1] - SPEAR_A[1]) / (SPEAR_B[0] - SPEAR_A[0])
    return (x, SPEAR_A[1] + k * (x - SPEAR_A[0]))


GRIP = on_spear(36.0)                        # his gloved fist round the shaft
BUTT = SPEAR_B
SHOULDER = (48.0, 26.5)                      # where the sleeve meets the tall gold shoulder guard (that stays on the body)
CHEST = (60.0, 34.0)
# the near arm: the gold-trimmed sleeve, the forearm guard and the fist (the shaft's silver ring under the forearm stays
# the spear's)
ARM = [(31.6, 30.6), (34.5, 28.0), (38.5, 26.6), (41.5, 24.0), (44.6, 22.0), (48.4, 22.0), (48.4, 31.5),
       (45.0, 31.6), (41.6, 33.6), (39.6, 35.6), (31.4, 35.6), (31.4, 34.6)]
# the spear's own squares: the blade group left of the fist, the shaft stretch by the forearm, the stretch over his
# front shoulder up to the butt (none of the head's silver ornament at columns 69-72)
SPEAR_LOW = [(-1.0, 51.0), (-1.0, 44.0), (19.0, 24.4), (31.6, 24.4), (31.6, 36.4), (39.6, 36.4), (39.6, 50.5)]
SPEAR_MID = R.band(on_spear(31.0), on_spear(42.0), 1.3)
SPEAR_HIGH = R.band(on_spear(72.6), on_spear(102.0), 4.4)
SHAFT = (on_spear(29.0), on_spear(72.0))     # under the fist and hidden behind his body: a straight line
# the legs below the coat: lavender trousers, gold knee, steel greave, brown boot
NEAR = dict(name="nl", side="near", rigid=True, hip=(48.0, 47.0), knee=(43.5, 53.5), sole=(39.0, 62.0),
            area=[(41.4, 45.6), (54.6, 45.6), (54.6, 50.0), (50.0, 54.0), (47.0, 57.0), (44.0, 63.0), (33.0, 63.0),
                  (37.0, 55.0), (40.0, 50.0)])
FAR = dict(name="fl", side="far", rigid=True, hip=(71.0, 47.0), knee=(75.5, 53.5), sole=(80.0, 62.0),
           area=[(64.5, 45.6), (78.0, 45.6), (79.0, 50.0), (83.0, 55.0), (87.0, 63.0), (73.0, 63.0), (72.0, 56.0),
                 (68.0, 54.0), (64.5, 51.0)])
IDLE_SINK = [0, 0, 1, 1, 2, 2, 1, 1]         # rows the upper body sinks over the legs, the sheet's 8 idle frames


# every point above is measured on square centres (square (c, r) at (c, r), as the design's class map and
# Design.poly count them); the cut, the turns and the Driver work on square edges (square (c, r) spans c..c+1)
def E(p):
    return (p[0] + 0.5, p[1] + 0.5)


GRIP, BUTT, SHOULDER, CHEST = E(GRIP), E(BUTT), E(SHOULDER), E(CHEST)
ARM, SPEAR_LOW, SPEAR_MID, SPEAR_HIGH = ([E(p) for p in poly] for poly in (ARM, SPEAR_LOW, SPEAR_MID, SPEAR_HIGH))
SHAFT = (E(SHAFT[0]), E(SHAFT[1]))
for _lg in (NEAR, FAR):
    _lg.update(hip=E(_lg["hip"]), knee=E(_lg["knee"]), sole=E(_lg["sole"]), area=[E(p) for p in _lg["area"]])


def lp(path):
    return R.lp(path)


def picture():
    """hd/design.png at SQUARE px a square (+ 2 clear squares round it) -> hd/picture.png."""
    hd = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
    d = np.asarray(Image.open(lp(os.path.join(hd, "design.png"))).convert("RGBA"))
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(hd, "picture.png")))
    return d


def coat(rgb):
    """The coat's purples (deep blue-violet, little green) - not the lavender trousers."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (g < 70) & (b > 100) & (b > r)


def poly_mask(D, polys):
    H, W = D.pic.shape[:2]
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for poly in polys:
        dr.polygon([D.d2p(x, y) for x, y in poly], fill=1)
    return np.asarray(img, bool) & (D.pic[..., 3] > 0)


def shaft_colour(D):
    """The shaft's brown: the commonest colour of the stretch over his shoulder between the gold rings."""
    cols = []
    for x in range(78, 86):
        _, y = on_spear(x)
        for yy in (int(np.floor(y)) - 1, int(np.floor(y)), int(np.floor(y)) + 1):
            c = tuple(int(v) for v in D.d0[yy, x, :3])
            if D.d0[yy, x, 3] and sum(c) > 70 and c[0] > c[2] + 40 and c[1] < 90:
                cols.append(c)
    return max(set(cols), key=cols.count)


class Design(R.Design):
    """ppu_rig.Design with the parts kept square for square: pixel_down.pixelate (its outline unification and
    despeckle) would change design squares, so a part is the picture's pixels in its mask turned (nearest) at 12 px a
    square and each square the commonest colour of its pixels where half or more are drawn - at angle 0 the design's own
    squares exactly."""

    def turned(self, poly_pts, angle, about, src=None, shaft=None, mask=None):
        P, S = self.TURN_PAD, SQUARE
        pic = self.pic if src is None else src
        if mask is None:
            img = Image.new("L", (pic.shape[1], pic.shape[0]), 0)
            ImageDraw.Draw(img).polygon([self.d2p(x, y) for x, y in poly_pts], fill=1)
            mask = np.asarray(img, bool)
        sq, _ = square_mask(self, mask)
        part = np.zeros((self.H + 2 * P, self.W + 2 * P, 4), np.uint8)
        part[P:P + self.H, P:P + self.W][sq] = pic[S // 2::S, S // 2::S][:self.H, :self.W][sq]
        Hd, Wd = part.shape[:2]
        if angle:
            # RotSprite: Scale2x three times (8x, its diagonals kept whole), turned nearest about the point, each
            # square the commonest colour of its 8 x 8 where half or more is drawn
            big = scale2x(scale2x(scale2x(part)))
            cx, cy = (about[0] + P) * 8, (about[1] + P) * 8
            big = np.asarray(Image.fromarray(big).rotate(angle, resample=Image.NEAREST, center=(cx, cy))).copy()
            out = vote(big, 8)
        else:
            out = part
        if shaft is not None and angle:              # at rest the fist and the body hide the line (as drawn)
            (x0, y0), (x1, y1), w, colour, _, rim = shaft
            th = np.radians(angle)
            ax_, ay_ = about

            def rot(x, y):
                return (ax_ + (x - ax_) * np.cos(th) + (y - ay_) * np.sin(th) + P,
                        ay_ - (x - ax_) * np.sin(th) + (y - ay_) * np.cos(th) + P)
            (X0, Y0), (X1, Y1) = rot(x0, y0), rot(x1, y1)
            yy, xx = np.mgrid[0:Hd, 0:Wd]
            cx_, cy_ = xx + 0.5, yy + 0.5
            dx_, dy_ = X1 - X0, Y1 - Y0
            L2 = max(1e-9, dx_ * dx_ + dy_ * dy_)
            t = np.clip(((cx_ - X0) * dx_ + (cy_ - Y0) * dy_) / L2, 0, 1)
            dist = np.hypot(cx_ - (X0 + t * dx_), cy_ - (Y0 + t * dy_))
            line = (dist <= w / 2) & (out[..., 3] == 0)
            out[line, :3] = colour
            out[line, 3] = 255
            if rim:
                edge = (dist <= w / 2 + rim) & (out[..., 3] == 0)
                out[edge, :3] = self.outline
                out[edge, 3] = 255
        return out


def vote(a, S):
    """Each S x S block of `a`: the commonest colour of its drawn pixels where half or more are drawn, else clear."""
    Hd, Wd = a.shape[0] // S, a.shape[1] // S
    b = a[:Hd * S, :Wd * S].reshape(Hd, S, Wd, S, 4).transpose(0, 2, 1, 3, 4).reshape(Hd * Wd, S * S, 4)
    op = b[..., 3] > 0
    cnt = op.sum(1)
    out = np.zeros((Hd * Wd, 4), np.uint8)
    keep = np.nonzero(cnt * 2 >= S * S)[0]
    if len(keep):
        code = (b[keep, :, 0].astype(np.int64) << 16) | (b[keep, :, 1].astype(np.int64) << 8) | b[keep, :, 2]
        code = np.where(op[keep], code, -1)
        for i, k in enumerate(keep):
            vals, n = np.unique(code[i][code[i] >= 0], return_counts=True)
            c = int(vals[n.argmax()])
            out[k] = (c >> 16, (c >> 8) & 255, c & 255, 255)
    return out.reshape(Hd, Wd, 4)


def scale2x(a):
    """EPX / Scale2x on an RGBA array (colours compared exactly, clear as a colour of its own)."""
    code = np.where(a[..., 3] > 0, (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2], -1)
    pc = np.pad(code, 1, mode="edge")
    A, B, C, Dn = pc[:-2, 1:-1], pc[1:-1, 2:], pc[1:-1, :-2], pc[2:, 1:-1]       # up, right, left, down
    pa = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    up, right, left, down = pa[:-2, 1:-1], pa[1:-1, 2:], pa[1:-1, :-2], pa[2:, 1:-1]
    H, W = code.shape
    out = np.repeat(np.repeat(a, 2, 0), 2, 1)
    for (oy, ox), cond, src in (((0, 0), (C == A) & (C != Dn) & (A != B), up),
                                ((0, 1), (A == B) & (A != C) & (B != Dn), right),
                                ((1, 0), (Dn == C) & (Dn != B) & (C != A), left),
                                ((1, 1), (B == Dn) & (B != A) & (Dn != C), down)):
        q = out[oy::2, ox::2]
        q[cond] = src[cond]
    return out


def square_mask(D, m):
    """A picture-pixel mask -> the design squares it holds half or more of (and back to pixels on those squares)."""
    S = SQUARE
    sq = m[:D.H * S, :D.W * S].reshape(D.H, S, D.W, S).mean((1, 3)) >= 0.5
    px = np.zeros_like(m)
    px[:D.H * S, :D.W * S] = np.repeat(np.repeat(sq, S, 0), S, 1)
    return sq, px


def design():
    want = picture()
    D = Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != want.shape or (D.d != want).any() or D.gx0 != 0 or D.gy0 != 0:
        sys.exit("hd/picture.png does not read back as hd/design.png")
    op = D.d[..., 3] > 0
    D.pal = np.unique(D.d[op][:, :3], axis=0).astype(np.uint8)     # the design's own colours, nothing else
    D.px = PIVOT_COL
    legs = {}
    for lg in (NEAR, FAR):
        th, sh = R.leg_masks(D, lg["area"], lg["hip"], lg["knee"], keep_out=coat, over_knee=0.5, under_knee=1.0,
                              extend=-100)              # the thighs never turn: no rows carried up under the coat
        legs[lg["name"] + "_thigh"], legs[lg["name"] + "_shin"] = th, sh
    arm = poly_mask(D, [ARM])
    spear = poly_mask(D, [SPEAR_LOW, SPEAR_MID, SPEAR_HIGH]) & ~arm
    D.cut_props({"arm": arm, "spear": spear, **legs}, close=1, bare=set(legs))
    # every prop on whole squares; the body the cut re-made (pixel_down.pixelate) kept only on the props' squares
    taken = np.zeros((D.H, D.W), bool)
    bare = np.zeros((D.H, D.W), bool)
    for name in list(D.props):
        sq, px = square_mask(D, D.prop_masks[name])
        D.prop_masks[name] = px
        taken |= sq
        if name in legs:
            bare |= sq
    D.d = np.where(taken[..., None], D.d, D.d0)
    D.d[bare] = 0                                   # nothing of the body under the legs' own squares
    for k in D.parts:
        D.parts[k] &= D.d[..., 3] > 0
    D.polys["arm"] = ARM
    D.polys["spear"] = R.band(E(SPEAR_A), E(SPEAR_B), 3.0)                  # the floor check's outline of the whole spear
    D.shaft("spear", SHAFT[0], SHAFT[1], 1.8, colour=shaft_colour(D), keep=[ARM], rim=1.0)
    D.part("upper", D.rest(), take=False)
    D.taken = taken
    return D


def check_design(D):
    """(squares changed outside the parts, squares where the parts at angle 0 and the body together differ from the
    design) - both must be 0."""
    outside = int(((D.d != D.d0).any(-1) & ~D.taken).sum())
    rig = R.Rig(D)
    z0 = dict(angle=0, about=(0, 0))
    lay = [("spear", z0)] + [(n, z0) for n in sorted(D.props) if n.endswith(("_thigh", "_shin"))] +         [("upper", dict()), ("arm", z0)]
    can = R.compose(rig, lay)
    got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
    D.diff_at = np.argwhere((got != D.d0).any(-1))
    return outside, int((got != D.d0).any(-1).sum())


def make_rig(D):
    return R.Rig(D, pad=(80, 80, 80, 30))          # the long spear turned about his fist reaches far


def driver(rig, joints):
    return R.Driver(rig, joints, SPEC_HEIGHT, ROWS, legs=[NEAR, FAR],
                    arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, over_weapon=True, relative=True),
                    weapons=[dict(name="spear", grip=GRIP, tip=BUTT, league=("weapon_a", "weapon_b"), relative=True,
                                  floor=2, rest_back=True, slide=dict(blade=E(SPEAR_A), lo=0.2, hi=0.8))],
                    src=rig.D.leg_src, leg_max=25)


# the run's legs: rig_jax_hd's WALK (league_braum's approved walk): per frame the near leg's (columns forward, rows
# lifted), the far leg's, the figure's rise
WALK = [((0, 0), (0, 3), 2), ((0, 0), (2, 5), 3), ((0, 0), (2, 2), 2), ((0, 0), (2, 0), 0),
        ((0, 3), (0, 0), 2), ((2, 5), (0, 0), 3), ((2, 2), (0, 0), 2), ((2, 0), (0, 0), 0)]
RUN_LEAN = 2


def leg_piece(D, lg):
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


def walk(legs, step):
    near_step, far_step, _ = step

    def layers(hx, dy):
        out = []
        for lg, (dx, lift) in ((FAR, far_step), (NEAR, near_step)):
            a = legs[lg["name"]]
            if lift:
                a = a.copy()
                a[:np.nonzero(a[..., 3].any(1))[0].min() + lift] = 0
            out.append((a, dict(dx=hx + dx, dy=dy - lift)))
        return out
    return layers


def idle_frame(rig, legs, sink):
    """The design standing, the upper body with the arm and the spear `sink` rows lower over the legs."""
    D = rig.D
    lay = [("spear", dict(dy=sink, angle=0, about=GRIP))]
    for lg in (FAR, NEAR):
        lay.append((legs[lg["name"]], dict()))
    lay += [("upper", dict(dy=sink)), ("arm", dict(dy=sink, angle=0, about=SHOULDER))]
    return R.compose(rig, lay)


def lying(rig, drv, j):
    """The death's end: the figure as it falls (League's frame 4) without the spear a quarter turn onto the ground, his
    head forward as League's falls (rig_jax_hd); the spear turned flat on the ground under him - turned with him, its
    108 squares stood straight up and lifted the lying body off the ground."""
    keep = drv.weapons
    drv.weapons = []
    try:
        body = R.lie(rig, drv.frame(j), k=-1, dx=2)
    finally:
        drv.weapons = keep
    a = -R.heading((SPEAR_B[0] - SPEAR_A[0], SPEAR_B[1] - SPEAR_A[1]))
    a = round(a / 2) * 2
    L = float(np.hypot(SPEAR_B[0] - SPEAR_A[0], SPEAR_B[1] - SPEAR_A[1]))
    mid = L / 2 - float(np.hypot(GRIP[0] - E(SPEAR_A)[0], GRIP[1] - E(SPEAR_A)[1]))   # grip -> the spear's middle
    dx = int(round(rig.CX - (rig.ox + GRIP[0] + mid)))
    dy = int(round(rig.GY - 2 - (rig.oy + GRIP[1])))
    spear = R.compose(rig, [("spear", dict(angle=a, about=GRIP, dx=dx, dy=dy))])
    spear[rig.GY:] = 0
    m = body[..., 3] > 0
    spear[m] = body[m]
    return spear


def frames(rig, joints):
    drv = driver(rig, joints)
    D = rig.D
    legs = {lg["name"]: leg_piece(D, lg) for lg in (NEAR, FAR)}
    sheet = R.sheet_of(HERO)
    bake = json.load(open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8"))
    baked = {e["into"] for e in bake["items"]}
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in sheet:
            continue
        if tag in baked:
            ms = [r["ms"] for r in rows]             # the strip before the bake split it (poses.json's timing)
        else:
            ms = [m for _, m in sheet[tag]]
            rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, legs, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        elif tag == "run":
            fr = []
            for i, r in enumerate(rows):
                j = r["j"]
                pel = (j["pelvis"][0] - joints["design"]["pelvis"][0]) * drv.s * drv.lunge
                lean = ((j["chest"][0] - j["pelvis"][0]) -
                        (joints["design"]["chest"][0] - joints["design"]["pelvis"][0])) * drv.s * drv.lean
                st = WALK[(i - 1) % len(WALK)]
                fr.append(drv.frame(j, {"walk": walk(legs, st), "dy": -st[2], "dx": -pel,
                                        "lean": RUN_LEAN - int(round(max(-5, min(5, lean))))}))
        else:
            fr = [drv.frame(r["j"]) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            fr = fr[:4] + [lying(rig, drv, rows[3]["j"])] * (len(fr) - 4)
            fr = fr[:4] + [f.copy() for f in fr[4:]]
        out[tag] = list(zip(fr, ms))
    acts = {t: out[t] for t in sheet if t in out}
    for t in sheet:
        if t not in acts:
            sys.exit(f"{t}: no League frames")
    acts = rig.bake(acts)
    for t in sheet:
        if len(acts[t]) != len(sheet[t]) or [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: {[m for _, m in acts[t]]} against the sheet's {[m for _, m in sheet[t]]}")
    return acts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's xinzhao_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D.ruler(os.path.join(a.parts, f"{HERO}_parts.png"), z=12)
        print("squares changed outside the parts / design rebuilt from the parts differs in:", check_design(D))
        print([tuple(int(v) for v in p[::-1]) for p in D.diff_at][:40])
        return
    if not a.joints:
        sys.exit("--joints is needed")
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = make_rig(D)
    acts = frames(rig, joints)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
