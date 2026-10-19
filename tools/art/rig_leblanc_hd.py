#!/usr/bin/env python3
"""league_leblanc redone at PPU 2.0 from Codex's take A (tools/art/design_leblanc_hd.py: 51 x 86, the staff straight;
the user, 2026-10-19: 「其实这个就挺好的 你只要把法杖做好 利用PPU就行了」), every action posed after League's own clip
frame by frame the way league_fiora was (tools/art/rig_fiora_hd.py; its lossless Design from rig_xinzhao_hd).

    python tools/art/design_leblanc_hd.py                                            # hd/design.png
    python tools/lol/league_joints.py assets/source/leblanc/poses.json --out <dir>   # League joints (once)
    python tools/art/rig_leblanc_hd.py --parts DIR                                   # the parts tinted + the rest check
    python tools/art/rig_leblanc_hd.py --joints <dir>/leblanc_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_leblanc_hd.py --joints <dir>/leblanc_joints.json            # orig strips + the 1x sheet

Parts (design squares, 86 rows crown to soles): her staff arm (the sleeve from the shoulder to the glove on the shaft)
turned about its shoulder by the change of League's right shoulder-to-hand from its idle, and the staff (the red
crystal, the bat-wing guards and the straight gold shaft) turned about her glove to League's weapon, both only
losslessly (as drawn, mirrored or quarter-turned); the staff only upright or level (STAFF_STEP: 「另外法杖别做歪啊」).
The rest - head, gown, the near arm and the legs under the gown - moves with League's pelvis, at most a column off the
hips (Driver max_lean). The tags, frame counts and ms are the sheet's (the kit's timing); skill is posed on its 5 frames
before Rig.bake lays Q's cast flash in (assets/source/native/leblanc_bake.json), the _fx copies are made by the bake.
The death ends lying: the figure a quarter turn, staff and arm held down first.
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
import design_leblanc_hd as DL  # noqa: E402

HERO = "leblanc"
PPU = 2.0
ROWS = 43                                    # game rows crown to soles (the 1x idle's)
SPEC_HEIGHT = 38                             # assets/source/leblanc/poses.json "height"
SQUARE = XZ.SQUARE
STAND_COL = 21.5                             # the column between her soles (the staff left out of the standing point)


def E(p):
    """Square centres -> square edges (the cut, the turns and the Driver)."""
    return (p[0] + 0.5, p[1] + 0.5)


# her staff arm: the sleeve from the shoulder under the collar up to the glove round the shaft (polygons in square edges)
SHOULDER, GRIP = E((31.0, 49.5)), E((40.5, 46.0))
TIP = E((41.0, 0.0))                         # the crystal's point: the staff stands straight up in the picture
ARM = [(30.0, 46.0), (34.0, 43.0), (37.0, 42.0), (43.0, 42.0), (43.0, 50.0), (39.0, 50.0), (37.0, 52.0), (34.0, 54.0),
       (30.0, 54.0)]
# (the wings' lowest tips and the neck's foot on rows 27-28 are the staff's too: left on the body they floated by her
# head when the staff turned)
STAFF = [(30.0, 0.0), (51.0, 0.0), (51.0, 30.0), (43.0, 30.0), (43.0, 87.0), (39.0, 87.0), (39.0, 30.0), (36.0, 30.0),
         (36.0, 27.0), (30.0, 27.0)]
IDLE_SINK = [0, 0, 1, 1, 1, 1, 0, 0]
RUN_SINK = 2                                 # rows a run frame may go down to set a sole on the ground
CAPE_X_RUN = 9                               # tools/art/pack_leblanc_legs.CAPE_X: the cape at her back stays
STAFF_STEP = 90                              # upright or level, never at a slant


class Design(XZ.Design):
    """XZ.Design with the staff turned only by whole quarter turns: drawn straight, it stays straight."""

    def snap(self, name, angle):
        if name == "staff":
            return float(round(R.wrap(angle) / STAFF_STEP) * STAFF_STEP)
        return super().snap(name, angle)


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
    D = Design(HERO, PPU, ROWS, regrid=SQUARE, foot_x=STAND_COL * SQUARE)
    if D.d.shape != want.shape or (D.d != want).any() or D.gx0 != 0 or D.gy0 != 0:
        sys.exit("hd/picture.png does not read back as hd/design.png")
    op = D.d[..., 3] > 0
    D.pal = np.unique(D.d[op][:, :3], axis=0).astype(np.uint8)
    arm = poly_mask(D, [ARM])
    staff = poly_mask(D, [STAFF]) & ~arm
    D.cut_props({"arm": arm, "staff": staff}, close=1)
    taken = np.zeros((D.H, D.W), bool)
    for name in list(D.props):
        sq, px = XZ.square_mask(D, D.prop_masks[name])
        D.prop_masks[name] = px
        taken |= sq
    D.d = np.where(taken[..., None], D.d, D.d0)
    for k in D.parts:
        D.parts[k] &= D.d[..., 3] > 0
    D.polys["arm"], D.polys["staff"] = ARM, STAFF
    D.AXES = {"arm": (GRIP[0] - SHOULDER[0], GRIP[1] - SHOULDER[1]),
              "staff": (TIP[0] - GRIP[0], TIP[1] - GRIP[1])}
    D.SHAFTS = {}
    D.part("upper", D.rest(), take=False)
    D.taken = taken
    # the shaft's stretch the glove hides (design_leblanc_hd draws it there too, under the glove's squares): drawn again
    # into the staff's own picture, so a staff turned level or lying is whole (「这里法杖断了？」「其他地方也有断开的情况」)
    src = D.pic.copy()
    m = np.zeros(src.shape[:2], bool)
    for y in range(DL.HAND[0] - 1, DL.HAND[-1] + 1):    # the arm takes row 42 too
        for x, c in ((DL.AXIS - 1, DL.OUTLINE), (DL.AXIS, DL.HI if (y - DL.Y0) % 6 == 0 else DL.SHAFT),
                     (DL.AXIS + 1, DL.OUTLINE)):
            (px0, py0), (px1, py1) = D.d2p(x, y), D.d2p(x + 1, y + 1)
            sl = (slice(int(round(py0)), int(round(py1))), slice(int(round(px0)), int(round(px1))))
            src[sl] = (*c, 255)
            m[sl] = True
    D.prop_masks["staff"] = D.prop_masks["staff"] | m
    D.staff_src = src
    return D


def check_design(D):
    outside = int(((D.d != D.d0).any(-1) & ~D.taken).sum())
    rig = R.Rig(D)
    z0 = dict(angle=0, about=(0, 0))
    can = R.compose(rig, [("upper", dict()), ("staff", z0), ("arm", z0)])
    got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
    D.diff_at = np.argwhere((got != D.d0).any(-1))
    return outside, int((got != D.d0).any(-1).sum())


def make_rig(D):
    return R.Rig(D, pad=(90, 90, 90, 30))         # the staff turned level about her glove reaches far


# The staff is taller than she is and held near its middle, so the generic Driver (the arm turned after League's, the
# staff about the moved grip) put it through her face and body (the first review: attack frames 2-3). Her own posing:
#  - the body moved with League's pelvis (LUNGE of its way forward, its rise kept, never down into the ground: the gown);
#  - the staff turned to League's weapon (weapon_a -> weapon_b) snapped to a quarter turn (STAFF_STEP), upright in front
#    as drawn, level or down BEHIND her (the hand and glove over it): League's lower end swings behind her body;
#  - the staff arm as drawn (turned a quarter up, the glove came to her mouth and the shaft over her cheek: ARM_UP None);
#  - idle holds the staff upright as drawn; the run holds it level ahead as League's does.
LUNGE = 0.6
ARM_UP = None
KEEP = set()


def pose(rig, joints, j, staff_free=True, arm_free=True):
    D = rig.D
    d = joints["design"]
    s = D.ppu * ROWS / SPEC_HEIGHT
    dx = int(round((j["pelvis"][0] - d["pelvis"][0]) * s * LUNGE))
    dy = int(round(min(0.0, (j["pelvis"][1] - d["pelvis"][1]) * s)))
    arm = 0.0
    if arm_free and ARM_UP is not None:
        rel = R.wrap(R.heading(np.subtract(j["r_hand"][:2], j["r_shoulder"][:2]))
                     - R.heading(np.subtract(d["r_hand"][:2], d["r_shoulder"][:2])))
        if rel >= ARM_UP:
            arm = 90.0
    grip = R.turn_pt(GRIP, SHOULDER, arm) if arm else np.array(GRIP)
    staff = 0.0
    if staff_free:
        want = R.heading(np.subtract(j["weapon_b"][:2], j["weapon_a"][:2]))
        staff = D.snap("staff", R.wrap(want - R.heading(np.subtract(TIP, GRIP))))
        if abs(staff) > 135:
            staff = 0.0                          # upside down (the crystal on the ground) reads wrong: held upright
    gx, gy = int(round(grip[0] - GRIP[0])), int(round(grip[1] - GRIP[1]))
    st = ("staff", dict(dx=dx + gx, dy=dy + gy, angle=staff, about=GRIP, src=D.staff_src))
    lay = [("upper", dict(dx=dx, dy=dy)), ("arm", dict(dx=dx, dy=dy, angle=arm, about=SHOULDER))]
    lay = [st] + lay if staff else [lay[0], st, lay[1]]
    can = R.compose(rig, lay)
    can[rig.GY:] = 0
    return can


# The run on Codex's legs (tools/art/import_leblanc_legs.py: hd/run_lower_<k>.png, the legs and the gown below the belt
# drawn along skeletons of her own leg lengths; the user: 「走路腿部不动的？」): the design's upper body and staff arm, the
# lower half of frame k, the staff to League's run (level, behind her); each frame set RUN_SINK rows lower at most, so
# its lowest sole meets the ground (round 2's soles came back on rows 82-85: two frames sink two rows - a run's own
# dip - and float a row, half a game pixel)
def run_lowers():
    hd = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
    with open(lp(os.path.join(hd, "run_lower.json")), encoding="utf-8") as f:
        meta = json.load(f)
    out = []
    for k in range(len(meta["frames"])):
        low = np.asarray(Image.open(lp(os.path.join(hd, f"run_lower_{k}.png"))).convert("RGBA"))
        sole = meta["hip_row"] + 1 + int(np.nonzero(low[..., 3].any(1))[0].max())
        out.append((low, meta["hip_row"], meta["pad"], int(min(RUN_SINK, max(0, ROWS * 2 - 1 - sole)))))
    return out


def over(base, top):
    m = top[..., 3] > 0
    base[m] = top[m]
    return base


def run_frame(rig, joints, j, lower):
    D = rig.D
    low, hip, pad, dy = lower
    d = joints["design"]
    want = R.heading(np.subtract(j["weapon_b"][:2], j["weapon_a"][:2]))
    staff = D.snap("staff", R.wrap(want - R.heading(np.subtract(TIP, GRIP))))
    if abs(staff) > 135:
        staff = 0.0
    st = R.compose(rig, [("staff", dict(dy=dy, angle=staff, about=GRIP, src=D.staff_src))])
    body = R.compose(rig, [("upper", dict(dy=dy))])
    y0 = rig.oy + hip + 1 + dy
    yy, xx = np.mgrid[0:body.shape[0], 0:body.shape[1]]
    body[(yy >= y0) & (xx >= rig.ox + CAPE_X_RUN)] = 0          # the design's gown and legs: Codex's instead
    lowc = rig.canvas()
    x0 = rig.ox - pad
    h = min(low.shape[0], lowc.shape[0] - y0)
    lowc[y0:y0 + h, x0:x0 + low.shape[1]] = low[:h]
    arm = R.compose(rig, [("arm", dict(dy=dy, angle=0, about=SHOULDER))])
    can = rig.canvas()
    for lay in ([st, body, lowc, arm] if staff else [body, lowc, st, arm]):
        over(can, lay)
    can[rig.GY:] = 0
    return can


def idle_frame(rig, sink):
    return R.compose(rig, [("upper", dict(dy=sink)), ("staff", dict(dy=sink, angle=0, about=GRIP, src=rig.D.staff_src)),
                           ("arm", dict(dy=sink, angle=0, about=SHOULDER))])


def frames(rig, joints):
    sheet = R.sheet_of(HERO)
    bake = json.load(open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8"))
    baked = {e["into"] for e in bake["items"] if "from" in e}
    laid_in = {e["into"] for e in bake["items"] if "from" not in e}
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in sheet or tag in baked:
            continue
        # a tag the bake lays a picture into has the sheet's frames split at the picture's times: posed on its own
        ms = [r["ms"] for r in rows] if tag in laid_in else [m for _, m in sheet[tag]]
        rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        elif tag == "run":
            lows = run_lowers()
            fr = [run_frame(rig, joints, r["j"], lows[i % len(lows)]) for i, r in enumerate(rows)]
        else:
            fr = [pose(rig, joints, r["j"], staff_free=tag not in KEEP and tag != "dead",
                       arm_free=tag not in KEEP) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            # League's death: she falls back and the staff stays standing where she held it - her figure without it
            # laid a quarter turn, the staff upright on its foot as in the idle
            body = R.compose(rig, [("upper", dict()), ("arm", dict(angle=0, about=SHOULDER))])
            stand = R.compose(rig, [("staff", dict(angle=0, about=GRIP, src=rig.D.staff_src))])
            lie = R.lie(rig, body, k=1)
            gap = np.nonzero(stand[..., 3].any(0))[0].min() - 2 - np.nonzero(lie[..., 3].any(0))[0].max()
            lie = R.lie(rig, body, k=1, dx=int(min(0, gap)))     # lying left of the standing staff
            m = stand[..., 3] > 0
            lie[m] = stand[m]
            fr = fr[:4] + [lie.copy() for _ in fr[4:]]
        out[tag] = list(zip(fr, ms))
    acts = {t: out[t] for t in sheet if t in out}
    for t in sheet:
        if t not in acts and t not in baked:
            sys.exit(f"{t}: no League frames")
    acts = rig.bake(acts)
    for t in sheet:
        if len(acts[t]) != len(sheet[t]) or [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: {[round(m) for _, m in acts[t]]} against the sheet's {[m for _, m in sheet[t]]}")
    return {t: acts[t] for t in sheet}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's leblanc_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint = {"arm": (0, 128, 255), "staff": (0, 255, 128)}
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
