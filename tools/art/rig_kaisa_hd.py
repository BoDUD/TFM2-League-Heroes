#!/usr/bin/env python3
"""league_kaisa redone at PPU 1.45 from Codex's chibi picture (assets/source/kaisa/PICTURE_PROMPT_PPU.md, read back by
tools/art/design_kaisa_hd.py: 42 x 61, the user's 「用 PPU 1.45（和现在一样高）」), every action posed after League's own
clip frame by frame the way league_xinzhao was (tools/art/rig_xinzhao_hd.py, whose lossless Design and helpers this uses).

    python tools/art/design_kaisa_hd.py                                         # hd/design.png
    python tools/lol/league_joints.py assets/source/kaisa/poses_hd.json --out <dir>  # League joints (once)
    python tools/art/rig_kaisa_hd.py --parts DIR                                # the parts tinted + the rest-frame check
    python tools/art/rig_kaisa_hd.py --joints <dir>/kaisa_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_kaisa_hd.py --joints <dir>/kaisa_joints.json          # orig strips + the 1x sheet

Parts (design squares, 61 rows pod tips to soles): her near arm (the gold-edged pauldron, the violet forearm and the
clawed hand with its magenta palm) and her far arm, each turned about its shoulder only losslessly (as drawn, mirrored
or quarter-turned: the one of the 8 nearest League's shoulder-to-hand turn - rig_xinzhao_hd.Design.snap; the near one
as ppu_rig.Driver's arm, the far one as an `attach`); both legs as drawn, never turned in the actions; the upper body
(head, hair, the Icathian Rain pods, the suit) moved with League's pelvis and leaning with its chest, never turned.
The run is League's kaisa_run (poses_hd.json, yaw 45 like the 3/4 design) on the design's own two legs swung about the
hips by whole rows (the boots moved whole; every row as drawn: 「腿部别变形」), the feet passing each other front to back
twice a cycle (「交叉步」): the near foot lands ahead with the legs crossed and the far heel kicked up behind it. The idle: the upper body and the
arms sinking whole rows over the standing legs (breathing, the sheet's 8 frames). The shot, Q cast, W charge / muzzle
and R trail stay drawn into the frames as before (assets/source/native/kaisa_bake.json, Rig.bake); R keeps the old
split: ult = League's first three R frames, ult_dash = the fourth; she crouches (the upper body sunk over the legs),
flies head first (the design a quarter turn) and lands crouched (R_POSE). The death ends lying: the figure a quarter
turn.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "kaisa"
PPU = 1.45
ROWS = 42                                    # game rows pod tips to soles (the 1x idle's)
SPEC_HEIGHT = 44                             # assets/source/kaisa/poses_hd.json "height" (poses.json at yaw 45: the 3/4 design)
SQUARE = XZ.SQUARE                           # px a square in hd/picture.png


def E(p):
    """Square centres (as the class map counts them) -> square edges (the cut, the turns and the Driver)."""
    return (p[0] + 0.5, p[1] + 0.5)


SHOULDER_N, HAND_N = E((15.5, 28.0)), E((11.0, 40.0))     # her near (image-left) arm
SHOULDER_F, HAND_F = E((32.0, 31.0)), E((37.5, 40.5))     # her far arm
NEAR_ARM = [E(p) for p in [(12.6, 26.5), (17.5, 26.5), (17.5, 30.5), (16.5, 35.5), (14.5, 37.5), (13.6, 45.5),
                           (7.5, 45.5), (7.5, 37.5), (10.5, 34.6), (12.6, 34.6)]]
FAR_ARM = [E(p) for p in [(31.5, 30.5), (33.6, 30.5), (35.6, 34.5), (41.5, 37.5), (41.5, 45.5), (33.5, 45.5),
                          (33.5, 38.5), (32.4, 36.5), (31.5, 33.5)]]
NEAR = dict(name="nl", side="near", rigid=True, hip=E((20.0, 46.0)), knee=E((18.5, 51.5)), sole=E((19.0, 60.0)),
            area=[E(p) for p in [(15.5, 45.6), (23.5, 45.6), (23.5, 50.5), (25.5, 56.5), (25.5, 60.5), (13.5, 60.5),
                                 (13.5, 55.5), (15.5, 50.5)]])
FAR = dict(name="fl", side="far", rigid=True, hip=E((30.0, 46.0)), knee=E((32.0, 51.5)), sole=E((33.0, 60.0)),
           area=[E(p) for p in [(26.6, 45.6), (33.5, 45.6), (35.5, 50.5), (36.5, 54.5), (39.5, 57.5), (39.5, 60.5),
                                (26.6, 60.5), (28.5, 54.5), (26.6, 50.5)]])
IDLE_SINK = [0, 0, 1, 1, 2, 2, 1, 1]         # rows the upper body and arms sink over the legs, the sheet's 8 idle frames

# the run (the user: 「走路好好做 腿部别变形」; 「走路腿变形啊 看不出吗」 at legs lifted by losing their top rows in view;
# 「没有明显换腿啊」「看起来像平移」 at whole legs only slid; 「没有前后换腿交叉步的感觉」 at feet that never passed each other):
# each leg swings about its hip by whole design rows - the thigh and knee rows (LEG_TOP..LEG_BOOT-1) each moved on a
# straight line from the hip's columns to the foot's, the boot rows moved whole (never slid row by row:
# league_xinzhao's 「脚严重变形啊」) - every row as drawn. Her boots stand 14.5 columns apart, so the near foot crosses in
# front of the far one only with the hips brought in as far as her bare hip plates cover (near -1..+3, far -3..+1)
# and the legs slanted up to 7 columns: after League's kaisa_run (poses_hd.json, yaw 45) the near foot passes the far
# one in frames 1-3 (landing ahead in frame 2) and falls behind it in 5-7, so the order of the feet changes twice a
# cycle. The far leg, then behind the near one, kicks its heel up (lifted whole, its top rows up under its plate and
# hidden by the near thigh); a leg in view is never lifted (it would show shorter). League's two flights a cycle: the
# whole figure off the ground in frames 0-1 and 4-5; the arms swing in a column while the near leg is back (out opens
# a slit at the shoulder).
# Per frame: near (hip columns, foot columns, rows lifted), far (...), rows the figure rises, near arm, far arm
LEG_TOP, LEG_BOOT = 46, 55
RUN = [((1, 3, 0), (-1, -3, 0), 1, 0, 0), ((3, 8, 0), (-3, -8, 2), 2, 0, 0),
       ((3, 10, 0), (-3, -10, 4), 0, 0, 0), ((3, 8, 0), (-3, -8, 3), 0, 0, 0),
       ((1, 3, 0), (-1, -3, 0), 1, 1, -1), ((-1, -2, 0), (1, 2, 0), 2, 1, -1),
       ((-1, -4, 0), (1, 4, 0), 0, 1, -1), ((-1, -2, 0), (1, 2, 0), 0, 1, -1)]

# R (League's kaisa_spell4_in / spell4 / spell4_out): she crouches, flies at her mark head first and lands crouched.
# A crouch: League's frame (its arms) with the upper body and the arms sunk whole rows over the standing legs; the
# flight: the design a quarter turn clockwise (head forward, chest down, legs and arms trailing - lossless), FLY_LIFT
# rows off the ground. Per (tag, League frame): (rows sunk, the arms as drawn) or "fly". A crouch sinks at most the
# idle's 2 rows: deeper, her hip plates swallow the thighs and the legs read as stumps (「走路腿变形啊」); landing keeps
# the arms as drawn (League's swing back behind a body bent double, which the upright figure cannot show: a tangle with
# her hair).
R_POSE = {("ult", 0): (2, False), ("ult", 1): (2, False), ("ult", 2): "fly", ("ult_dash", 0): "fly",
          ("ult_land", 0): (2, True), ("ult_land", 1): (2, True), ("ult_land", 2): (1, False)}
FLY_LIFT = 2


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


def hair(rgb):
    """Her plum hair falling behind the near arm (never part of the arm); not the bright magenta lights."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (g < 20) & (r > 40) & (b > 40) & (r < 130) & (b < 130) & (np.abs(r - b) < 35)


def poly_mask(D, polys):
    H, W = D.pic.shape[:2]
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for poly in polys:
        dr.polygon([D.d2p(x, y) for x, y in poly], fill=1)
    return np.asarray(img, bool) & (D.pic[..., 3] > 0)


def design():
    want = picture()
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != want.shape or (D.d != want).any() or D.gx0 != 0 or D.gy0 != 0:
        sys.exit("hd/picture.png does not read back as hd/design.png")
    op = D.d[..., 3] > 0
    D.pal = np.unique(D.d[op][:, :3], axis=0).astype(np.uint8)
    legs = {}
    for lg in (NEAR, FAR):
        th, sh = R.leg_masks(D, lg["area"], lg["hip"], lg["knee"], over_knee=0.5, under_knee=1.0, extend=-100)
        legs[lg["name"] + "_thigh"], legs[lg["name"] + "_shin"] = th, sh
    hair_px = hair(D.pic[..., :3].astype(int))
    narm = poly_mask(D, [NEAR_ARM]) & ~hair_px
    farm = poly_mask(D, [FAR_ARM])
    D.cut_props({"narm": narm, "farm": farm, **legs}, close=1, bare=set(legs))
    taken = np.zeros((D.H, D.W), bool)
    bare = np.zeros((D.H, D.W), bool)
    for name in list(D.props):
        sq, px = XZ.square_mask(D, D.prop_masks[name])
        D.prop_masks[name] = px
        taken |= sq
        if name in legs:
            bare |= sq
    D.d = np.where(taken[..., None], D.d, D.d0)
    D.d[bare] = 0
    for k in D.parts:
        D.parts[k] &= D.d[..., 3] > 0
    D.polys["narm"], D.polys["farm"] = NEAR_ARM, FAR_ARM
    D.AXES = {"narm": (HAND_N[0] - SHOULDER_N[0], HAND_N[1] - SHOULDER_N[1]),
              "farm": (HAND_F[0] - SHOULDER_F[0], HAND_F[1] - SHOULDER_F[1])}
    D.SHAFTS = {}
    D.part("upper", D.rest(), take=False)
    D.taken = taken
    return D


def check_design(D):
    """(squares changed outside the parts, squares where the parts at angle 0 and the body differ from the design)."""
    outside = int(((D.d != D.d0).any(-1) & ~D.taken).sum())
    rig = R.Rig(D)
    z0 = dict(angle=0, about=(0, 0))
    lay = [(n, z0) for n in sorted(D.props) if n.endswith(("_thigh", "_shin"))] + \
        [("farm", z0), ("upper", dict()), ("narm", z0)]
    can = R.compose(rig, lay)
    got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
    D.diff_at = np.argwhere((got != D.d0).any(-1))
    return outside, int((got != D.d0).any(-1).sum())


def make_rig(D):
    return R.Rig(D, pad=(60, 60, 60, 30))


def driver(rig, joints):
    return R.Driver(rig, joints, SPEC_HEIGHT, ROWS, legs=[NEAR, FAR],
                    arm=dict(name="narm", shoulder=SHOULDER_N, hand=HAND_N, relative=True, league_hand="r"),
                    attach=[dict(name="farm", anchor=SHOULDER_F, league="l_shoulder", turn=("l_shoulder", "l_hand"),
                                 max_turn=180, max_move=1)],
                    src=rig.D.leg_src, leg_max=0, max_lean=1)


def leg_piece(D, lg):
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


def idle_frame(rig, legs, sink):
    """The design standing, the upper body and both arms `sink` rows lower over the legs."""
    lay = [("farm", dict(dy=sink, angle=0, about=SHOULDER_F))]
    for lg in (FAR, NEAR):
        lay.append((legs[lg["name"]], dict()))
    lay += [("upper", dict(dy=sink)), ("narm", dict(dy=sink, angle=0, about=SHOULDER_N))]
    return R.compose(rig, lay)


# ------------------------------------------------------------------------------------------------- the run
def swung(a, hip, foot, lift=0):
    """A leg (leg_piece) swung by whole rows: its thigh and knee rows moved from `hip` to `foot` columns along a
    straight line, its boot rows moved `foot` columns as one piece; lifted `lift` rows whole (its top rows up under the
    hip plate)."""
    top = np.nonzero(a[..., 3].any(1))[0].min()
    boot = top + LEG_BOOT - LEG_TOP
    out = np.zeros_like(a)
    for r in range(top, boot):
        out[r] = np.roll(a[r], hip + int(round((foot - hip) * (r - top) / (boot - top))), axis=0)
    out[boot:] = np.roll(a[boot:], foot, axis=1)
    if lift:
        out = np.roll(out, -lift, axis=0)
        out[:top] = 0
    return out


def run_frames(rig, rows):
    D = rig.D
    legs = {"near": leg_piece(D, NEAR), "far": leg_piece(D, FAR)}
    out = []
    for i in range(len(rows)):
        near, far, rise, na, fa = RUN[i % len(RUN)]
        out.append(R.compose(rig, [("farm", dict(angle=0, about=SHOULDER_F, dx=fa, dy=-rise)),
                                   (swung(legs["far"], *far), dict(dy=-rise)),
                                   (swung(legs["near"], *near), dict(dy=-rise)),
                                   ("upper", dict(dy=-rise)),
                                   ("narm", dict(angle=0, about=SHOULDER_N, dx=na, dy=-rise))]))
    return out


# ------------------------------------------------------------------------------------------------- R
def sunk(drv, legs, j, sink, keep=False):
    """League's frame j (its arms, or the arms as drawn: keep) with the upper body and the arms `sink` rows down over
    the standing legs."""
    def walk(hx, dy):
        return [(legs[lg["name"]], dict(dx=hx)) for lg in (FAR, NEAR)]
    return drv.frame(j, {"walk": walk, "dy": sink, "keep": keep})


def flying(rig, legs):
    """The design a quarter turn clockwise, head forward, FLY_LIFT rows off the ground (R's dash)."""
    can = idle_frame(rig, legs, 0)
    ys, xs = np.nonzero(can[..., 3] > 0)
    t = np.rot90(can[ys.min():ys.max() + 1, xs.min():xs.max() + 1], -1).copy()
    h, w = t.shape[:2]
    out = rig.canvas()
    top, left = rig.GY - h - FLY_LIFT, int(round(rig.CX - w / 2))
    out[top:top + h, left:left + w] = t
    return out


# ------------------------------------------------------------------------------------------------- the actions
def frames(rig, joints):
    drv = driver(rig, joints)
    D = rig.D
    legs = {lg["name"]: leg_piece(D, lg) for lg in (NEAR, FAR)}
    sheet = R.sheet_of(HERO)
    tags = dict(joints["tags"])
    # R as the old import split it: ult = League's first three R frames, ult_dash = the fourth (100 ms before the bake)
    tags["ult_dash"] = [dict(tags["ult"][3], ms=100)]
    tags["ult"] = tags["ult"][:3]
    bake = json.load(open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8"))
    baked = {e["into"] for e in bake["items"]}
    out = {}
    for tag, rows in tags.items():
        if tag not in sheet:
            continue
        if tag in baked:
            ms = [r["ms"] for r in rows]
        else:
            ms = [m for _, m in sheet[tag]]
            rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, legs, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        elif tag == "run":
            fr = run_frames(rig, rows)
        else:
            fr = []
            for i, r in enumerate(rows):
                pose = R_POSE.get((tag, i))
                fr.append(flying(rig, legs) if pose == "fly" else sunk(drv, legs, r["j"], *pose) if pose
                          else drv.frame(r["j"]))
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            lie = R.lie(rig, drv.frame(rows[3]["j"]), k=1, dx=-2)
            fr = fr[:4] + [lie.copy() for _ in fr[4:]]
        out[tag] = list(zip(fr, ms))
    acts = {t: out[t] for t in sheet if t in out}
    for t in sheet:
        if t not in acts:
            sys.exit(f"{t}: no League frames")
    acts = rig.bake(acts)
    for t in sheet:
        if len(acts[t]) != len(sheet[t]) or [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: {[round(m) for _, m in acts[t]]} against the sheet's {[m for _, m in sheet[t]]}")
    return acts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's kaisa_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint = {"narm": (0, 128, 255), "farm": (0, 255, 128), "nl_thigh": (255, 0, 255), "nl_shin": (255, 128, 0),
                "fl_thigh": (255, 255, 0), "fl_shin": (255, 0, 0)}
        img = D.d0.astype(float).copy()
        for n, c in tint.items():
            sq, _ = XZ.square_mask(D, D.prop_masks[n])
            img[sq, :3] = img[sq, :3] * 0.45 + np.array(c) * 0.55
        Image.fromarray(np.repeat(np.repeat(img.astype(np.uint8), 12, 0), 12, 1)).save(
            os.path.join(a.parts, f"{HERO}_parts.png"))
        print("pivot column", D.px, "| squares changed outside the parts / rest frame differs in:", check_design(D))
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
