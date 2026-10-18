#!/usr/bin/env python3
"""league_darius redone at PPU 1.45 from Codex's design picture (assets/source/darius/PICTURE_PROMPT_PPU.md, read back by
tools/art/design_darius_hd.py: 56 x 61, the user: 「用 PPU 1.45，和现在一样高」), every action posed after League's own clip
frame by frame the way league_fiora was (tools/art/rig_fiora_hd.py; its lossless Design from rig_xinzhao_hd).

    python tools/art/design_darius_hd.py                                            # hd/design.png
    python tools/lol/league_joints.py assets/source/darius/poses.json --out <dir>   # League joints (once)
    python tools/art/rig_darius_hd.py --parts DIR                                   # the parts tinted + the rest-frame check
    python tools/art/rig_darius_hd.py --joints <dir>/darius_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_darius_hd.py --joints <dir>/darius_joints.json             # orig strips + the 1x sheet

Parts (design squares, 61 rows from the axe's ring to the soles): his axe hand (the gauntlet round the shaft and the
vambrace under the big shoulder plate) turned about his shoulder after League's right shoulder-to-hand, the axe (ring,
shaft and both crescent blades) turned about his fist after League's weapon, both only losslessly (as drawn, mirrored or
quarter-turned: the one of the 8 nearest League's turn); both legs (greave and boot) as drawn; the upper body (head,
shoulder plates, armour, tabard, cape and the far fist) moved with League's pelvis, at most a column off the hips.
The death ends lying: the figure a quarter turn.
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

HERO = "darius"
PPU = 1.45
DESIGN_ROWS = 61
ROWS = DESIGN_ROWS / PPU                     # game rows of the design picture, the axe's ring to the soles
BODY_ROWS = 58 / PPU                         # his hair's top (row 3) to the soles: what League's `height` measures
SPEC_HEIGHT = 34                             # assets/source/darius/poses.json "height"
SQUARE = XZ.SQUARE

# polygons in square edges (x, y); points in square edges
SHOULDER, GRIP = (22.0, 26.0), (14.0, 31.5)
TIP = (14.0, 50.0)                           # the axe head's middle, straight under the fist: the axe hangs down
ARM = [(8.0, 26.0), (18.0, 26.0), (18.0, 30.0), (21.0, 30.0), (21.0, 37.0), (8.0, 37.0)]
AXE = [(9.0, 0.0), (19.0, 0.0), (19.0, 11.0), (16.5, 11.0), (16.5, 37.0), (17.0, 37.0), (17.0, 41.0), (19.5, 41.0),
       (19.5, 38.0), (26.0, 38.0), (26.0, 56.0), (24.0, 56.0), (24.0, 61.0), (0.0, 61.0), (0.0, 38.0), (11.5, 38.0),
       (11.5, 11.0), (9.0, 11.0)]
FRONT = dict(name="fl", side="near", rigid=True, hip=(29.0, 47.0), knee=(29.0, 53.0), sole=(28.0, 61.0),
             area=[(25.0, 46.0), (34.0, 46.0), (34.0, 61.0), (24.0, 61.0), (24.0, 56.0), (25.0, 56.0)])
BACK = dict(name="bl", side="far", rigid=True, hip=(47.0, 52.0), knee=(47.0, 56.0), sole=(48.0, 61.0),
            area=[(41.0, 51.0), (56.0, 51.0), (56.0, 61.0), (41.0, 61.0)])
IDLE_SINK = [0, 0, 1, 1, 1, 1, 0, 0]


def crimson(rgb):
    """The tabard's and the cape's crimson, not the steel legs."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (r > 90) & (g < 60) & (r > b + 30)


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
    for lg in (FRONT, BACK):
        th, sh = R.leg_masks(D, lg["area"], lg["hip"], lg["knee"], keep_out=crimson, over_knee=0.5, under_knee=1.0,
                             extend=-100)
        legs[lg["name"] + "_thigh"], legs[lg["name"] + "_shin"] = th, sh
    arm = poly_mask(D, [ARM])
    axe = poly_mask(D, [AXE]) & ~arm
    D.cut_props({"arm": arm, "axe": axe, **legs}, close=1, bare=set(legs))
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
    D.polys["arm"], D.polys["axe"] = ARM, AXE
    D.AXES = {"arm": (GRIP[0] - SHOULDER[0], GRIP[1] - SHOULDER[1]),
              "axe": (TIP[0] - GRIP[0], TIP[1] - GRIP[1])}
    D.SHAFTS = {}
    D.part("upper", D.rest(), take=False)
    D.taken = taken
    return D


def check_design(D):
    outside = int(((D.d != D.d0).any(-1) & ~D.taken).sum())
    rig = R.Rig(D)
    z0 = dict(angle=0, about=(0, 0))
    lay = [(n, z0) for n in sorted(D.props) if n.endswith(("_thigh", "_shin"))] + \
        [("upper", dict()), ("axe", z0), ("arm", z0)]
    can = R.compose(rig, lay)
    got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
    D.diff_at = np.argwhere((got != D.d0).any(-1))
    return outside, int((got != D.d0).any(-1).sum())


def make_rig(D):
    return R.Rig(D, pad=(80, 80, 80, 30))          # the axe turned about his fist reaches far


def driver(rig, joints):
    # the picture is drawn after League's idle: arm and axe turned by League's change from it
    return R.Driver(rig, joints, SPEC_HEIGHT, BODY_ROWS, legs=[FRONT, BACK],
                    arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, relative=True, league_hand="r",
                             with_weapon=True, over_weapon=True),
                    weapons=[dict(name="axe", grip=GRIP, tip=TIP, league=("weapon_b", "weapon_a"), relative=True,
                                  floor=2)],
                    src=rig.D.leg_src, leg_max=0, max_lean=1)


def leg_piece(D, lg):
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


def idle_frame(rig, legs, sink):
    lay = [(legs[lg["name"]], dict()) for lg in (BACK, FRONT)]
    lay += [("upper", dict(dy=sink)), ("axe", dict(dy=sink, angle=0, about=GRIP)),
            ("arm", dict(dy=sink, angle=0, about=SHOULDER))]
    return R.compose(rig, lay)


# the run: both legs as drawn (greave and boot, never cut or turned), each moved whole after League's run - its foot's
# way forward or back against the pelvis RUN_X of it (at most RUN_MAX columns: further, the thigh's top came out from
# under the armoured skirt), lifted as high as League's foot is over the lower one RUN_LIFT of it (at most RUN_UP rows;
# the rows that rise go under the skirt, which is drawn over the legs); the body bobs with League's pelvis
RUN_X, RUN_MAX, RUN_LIFT, RUN_UP = 0.35, 5, 0.5, 4


def run_steps(drv, joints, rows):
    """[(near (dx, lift), far (dx, lift), bob)] per frame of League's run."""
    d = joints["design"]
    s = drv.s
    pel = sorted(r["j"]["pelvis"][1] for r in rows)
    mid = pel[len(pel) // 2]
    out = []
    for r in rows:
        j = r["j"]
        low = max(j["r_foot"][1], j["l_foot"][1])            # y down: the lower foot
        step = {}
        for key, f in (("near", drv.side["near"]), ("far", drv.side["far"])):
            fx = (j[f + "_foot"][0] - j["pelvis"][0]) - (d[f + "_foot"][0] - d["pelvis"][0])
            dx = int(round(max(-RUN_MAX, min(RUN_MAX, fx * s * RUN_X))))
            lift = int(round(max(0, min(RUN_UP, (low - j[f + "_foot"][1]) * s * RUN_LIFT))))
            step[key] = (dx, lift)
        bob = int(round(max(-1, min(1, (j["pelvis"][1] - mid) * s * 0.3))))
        out.append((step["near"], step["far"], bob))
    return out


def walk(legs, step):
    """Driver `walk` for one run step: the far leg, then the near one, each moved whole."""
    near_step, far_step, _ = step

    def layers(hx, dy):
        return [(legs[lg["name"]], dict(dx=hx + dx, dy=dy - lift))
                for lg, (dx, lift) in ((BACK, far_step), (FRONT, near_step))]
    return layers


def frames(rig, joints):
    drv = driver(rig, joints)
    D = rig.D
    legs = {lg["name"]: leg_piece(D, lg) for lg in (FRONT, BACK)}
    sheet = R.sheet_of(HERO)
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in sheet:
            continue
        ms = [m for _, m in sheet[tag]]
        rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, legs, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        elif tag == "run":
            fr = [drv.frame(r["j"], {"walk": walk(legs, st), "dy": st[2]})
                  for r, st in zip(rows, run_steps(drv, joints, rows))]
        else:
            fr = [drv.frame(r["j"]) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            lie = R.lie(rig, drv.frame(rows[3]["j"], dict(keep=True)), k=-1, dx=2)
            fr = fr[:4] + [lie.copy() for _ in fr[4:]]
        out[tag] = list(zip(fr, ms))
    for t in sheet:
        if t not in out or len(out[t]) != len(sheet[t]):
            sys.exit(f"{t}: no League frames or a different count")
    return {t: out[t] for t in sheet}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's darius_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint = {"arm": (0, 128, 255), "axe": (0, 255, 128), "fl_thigh": (255, 0, 255), "fl_shin": (255, 128, 0),
                "bl_thigh": (255, 255, 0), "bl_shin": (255, 0, 0)}
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
