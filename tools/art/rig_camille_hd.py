#!/usr/bin/env python3
"""league_camille redone at PPU 1.5 from Codex's design picture (assets/source/camille/PICTURE_PROMPT_PPU.md, read back by
tools/art/design_camille_hd.py: 32 x 69, the user: 「确认」), every action posed after League's own clip frame by frame the
way league_kaisa was (tools/art/rig_kaisa_hd.py; its lossless Design from rig_xinzhao_hd).

    python tools/art/design_camille_hd.py                                          # hd/design.png
    python tools/lol/league_joints.py assets/source/camille/poses_hd.json --out <dir>  # League joints (once)
    python tools/art/rig_camille_hd.py --parts DIR                                 # the parts tinted + the rest-frame check
    python tools/art/rig_camille_hd.py --joints <dir>/camille_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_camille_hd.py --joints <dir>/camille_joints.json          # orig strips + the 1x sheet

Parts (design squares, 69 rows hair to blade tips): her near arm (the gold-edged shoulder, the arm bent out to the
elbow and back, the gold cuff and the glove on her hip) and her far arm (the upper arm down to the elbow, the forearm
up to the gold cuff and the raised glove), each turned about its shoulder only losslessly (as drawn, mirrored or
quarter-turned: the one of the 8 nearest League's shoulder-to-hand turn), the near one as ppu_rig.Driver's arm, the far
one as an `attach` (moved at most a square with League's shoulder); both legs (thigh, gold knee and blade) as drawn;
the upper body (head, collar, breastplate, hips with the hextech core) moved with League's pelvis, at most a column off
the hips (Driver max_lean: the hip armour sits on the thighs). The idle: the upper body and the arms sinking whole rows
over the standing legs. The death ends lying: the figure a quarter turn.
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
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "camille"
PPU = 1.5
ROWS = 46                                    # game rows hair to blade tips (the 1x idle's)
SPEC_HEIGHT = 46                             # assets/source/camille/poses_hd.json "height" (poses.json at yaw 45)
SQUARE = XZ.SQUARE


def E(p):
    """Square centres -> square edges (the cut, the turns and the Driver)."""
    return (p[0] + 0.5, p[1] + 0.5)


SHOULDER_N, HAND_N = E((6.0, 23.5)), E((9.0, 32.0))      # her near (image-left) arm: the hand on her hip
SHOULDER_F, HAND_F = E((20.5, 26.0)), E((29.0, 19.5))    # her far arm: raised, thumb and forefinger in a ring
NEAR_ARM = [E(p) for p in [(1.0, 22.5), (8.6, 22.5), (9.6, 24.5), (6.5, 25.5), (5.5, 27.5), (8.5, 29.4), (10.6, 29.4),
                           (10.6, 33.6), (6.5, 34.5), (2.5, 31.5), (-0.5, 28.0), (-0.5, 24.5)]]
FAR_ARM = [E(p) for p in [(19.6, 25.6), (21.5, 25.6), (24.5, 22.5), (26.5, 21.5), (27.5, 16.5), (31.5, 16.5),
                          (31.5, 23.5), (29.5, 25.5), (26.5, 26.5), (24.5, 30.5), (23.5, 31.6), (20.5, 31.6),
                          (19.6, 29.5)]]
NEAR = dict(name="nl", side="near", rigid=True, hip=E((11.0, 42.0)), knee=E((11.5, 50.0)), sole=E((10.5, 68.0)),
            area=[E(p) for p in [(6.5, 41.6), (14.5, 41.6), (14.5, 50.5), (13.5, 53.5), (12.5, 68.5), (5.5, 68.5),
                                 (5.5, 45.0)]])
FAR = dict(name="fl", side="far", rigid=True, hip=E((20.0, 41.0)), knee=E((20.0, 50.0)), sole=E((19.0, 68.0)),
           area=[E(p) for p in [(16.5, 40.6), (24.5, 40.6), (24.5, 49.5), (22.5, 51.5), (21.5, 68.5), (16.5, 68.5),
                                (16.5, 52.5)]])
IDLE_SINK = [0, 0, 1, 1, 2, 2, 1, 1]


def lp(path):
    return R.lp(path)


def picture():
    hd = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
    d = np.asarray(Image.open(lp(os.path.join(hd, "design.png"))).convert("RGBA"))
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(hd, "picture.png")))
    return d


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
    narm = poly_mask(D, [NEAR_ARM])
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
    lay = [("farm", dict(dy=sink, angle=0, about=SHOULDER_F))]
    for lg in (FAR, NEAR):
        lay.append((legs[lg["name"]], dict()))
    lay += [("upper", dict(dy=sink)), ("narm", dict(dy=sink, angle=0, about=SHOULDER_N))]
    return R.compose(rig, lay)


def frames(rig, joints):
    drv = driver(rig, joints)
    D = rig.D
    legs = {lg["name"]: leg_piece(D, lg) for lg in (NEAR, FAR)}
    sheet = R.sheet_of(HERO)
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in sheet:
            continue
        ms = [m for _, m in sheet[tag]]
        rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, legs, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        else:
            fr = [drv.frame(r["j"]) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            lie = R.lie(rig, drv.frame(rows[3]["j"]), k=1, dx=-2)
            fr = fr[:4] + [lie.copy() for _ in fr[4:]]
        out[tag] = list(zip(fr, ms))
    acts = {t: out[t] for t in sheet if t in out}
    for t in sheet:
        if t not in acts or len(acts[t]) != len(sheet[t]):
            sys.exit(f"{t}: no League frames or a different count")
    return acts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's camille_joints.json")
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
