#!/usr/bin/env python3
"""league_fiora redone at PPU 1.5 from Codex's design picture (assets/source/fiora/PICTURE_PROMPT_PPU.md, read back by
tools/art/design_fiora_hd.py: 87 x 60, her whole head kept, the user: 「用这个吧」), every action posed after League's own
clip frame by frame the way league_camille was (tools/art/rig_camille_hd.py; its lossless Design from rig_xinzhao_hd).

    python tools/art/design_fiora_hd.py --blade-row 24                              # hd/design.png
    python tools/lol/league_joints.py assets/source/fiora/poses.json --out <dir>    # League joints (once)
    python tools/art/rig_fiora_hd.py --parts DIR                                    # the parts tinted + the rest-frame check
    python tools/art/rig_fiora_hd.py --joints <dir>/fiora_joints.json --review DIR  # every tag at 3x + GIFs
    python tools/art/rig_fiora_hd.py --joints <dir>/fiora_joints.json               # orig strips + the 1x sheet

Parts (design squares, 60 rows hair to soles): her sword arm (the gold bracer and the glove, out from the shoulder plate
to the hilt) turned about its shoulder after League's right shoulder-to-hand, and the rapier (the gold guard with its gem
and the 31-square blade) turned about her glove after League's weapon, both only losslessly (as drawn, mirrored or
quarter-turned: the one of the 8 nearest League's turn); both legs (thigh, gold knee, shin and boot) as drawn in the
idle, hit, ult and death, drawn on League's bones in the steps and lunges (LEG_TAGS: see the legs' section); the upper
body (head, shoulder plates, the white top, the hip armour, the cape and the hand on it) moved with League's pelvis, at
most a column off the hips (Driver max_lean). skill_fx1 is skill with the Q dash under it (assets/source/native/
fiora_bake.json, Rig.bake); its two dash frames are the figure a quarter turn (DASH). The death ends lying: the
figure a quarter turn.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "fiora"
PPU = 1.5
ROWS = 40                                    # game rows hair to soles (the 1x idle's)
SPEC_HEIGHT = 40                             # assets/source/fiora/poses.json "height"
SQUARE = XZ.SQUARE


def E(p):
    """Square centres -> square edges (the cut, the turns and the Driver)."""
    return (p[0] + 0.5, p[1] + 0.5)


# her sword arm: the bracer from under the shoulder plate to the glove before the hilt (polygons in square edges)
SHOULDER, GRIP = E((35.0, 22.5)), E((46.5, 23.0))
TIP = (87.0, GRIP[1])                        # level with the glove: the blade lies flat in the picture
ARM = [(36.0, 21.0), (40.0, 21.0), (40.0, 20.0), (48.0, 20.0), (48.0, 26.0), (36.0, 26.0)]
RAPIER = [(48.0, 16.0), (56.0, 16.0), (56.0, 21.5), (88.0, 21.5), (88.0, 24.5), (56.0, 24.5), (56.0, 28.0),
          (48.0, 28.0)]
# the legs below the hip armour: League's right leg is the front one (image right), its left the back one
FRONT = dict(name="fl", side="near", rigid=True, hip=E((30.0, 36.0)), knee=E((32.0, 43.5)), sole=E((33.0, 59.0)),
             area=[(26.0, 36.0), (36.0, 36.0), (36.0, 47.0), (35.0, 56.0), (41.0, 56.0), (41.0, 60.0), (27.0, 60.0),
                   (27.0, 46.0), (27.0, 39.0), (26.0, 39.0)])
BACK = dict(name="bl", side="far", rigid=True, hip=E((21.5, 36.0)), knee=E((20.0, 43.5)), sole=E((14.5, 59.0)),
            area=[(17.5, 36.0), (26.0, 36.0), (26.0, 39.0), (27.0, 39.0), (27.0, 46.0), (22.0, 52.0), (21.0, 60.0),
                  (11.0, 60.0), (11.0, 55.0), (13.0, 51.0), (13.0, 46.0), (17.5, 44.0)])
IDLE_SINK = [0, 0, 1, 1, 1, 1, 0, 0]
# the blade: from the guard's mouth (EXIT, square edges, on the line between its two rows) BLADE_LEN squares on
BLADE_X0, EXIT, BLADE_LEN = 56, (56.0, 23.0), 31
ARM_FLAT = 60
SWORD_STEP = 90                              # level or upright (Codex's 45-degree guard lost the gem and the cup: not used)
BLADE_HI, BLADE_LO = (250, 250, 252), (168, 176, 198)     # design_fiora_hd.BLADE: the white edge, the blue-grey face


class Design(XZ.Design):
    """XZ.Design (parts turned only losslessly) with the rapier straight in one of SWORD_STEP's directions: the guard
    turned losslessly to it (as drawn, mirrored or quarter-turned) and the blade - one straight two-colour line
    (design_fiora_hd draws it so) - drawn again square by square along it, two squares across, the white edge up (left
    when it stands upright). The user, 2026-10-18: 「剑别歪啊 歪的地方全部修复」 - at League's own angle the blade came out
    in uneven steps and bent off a guard that can only take quarter turns; so guard and blade always point the same way,
    level or upright."""

    def snap(self, name, angle):
        if name == "rapier":
            return float(round(R.wrap(angle) / SWORD_STEP) * SWORD_STEP)
        if name == "arm":
            # the arm takes the nearest quarter turn, held out straight while League's is within ARM_FLAT of it: her
            # thrusts hold the arm 20-45 degrees down and often half toward the camera (2-5 game px seen), which a
            # straight-down arm put at her hips with the guard under it
            a = R.wrap(angle)
            if abs(a) <= ARM_FLAT:
                return 0.0
            return super().snap(name, a)
        return super().snap(name, angle)

    def turned(self, poly_pts, angle, about, src=None, shaft=None, mask=None):
        if getattr(self, "_turning", None) != "rapier":
            return super().turned(poly_pts, angle, about, src, shaft, mask)
        guard = mask.copy()
        x0 = int(round(self.d2p(BLADE_X0, 0)[0]))
        y0, y1 = (int(round(self.d2p(0, y)[1])) for y in (EXIT[1] - 1, EXIT[1] + 1))
        guard[y0:y1, x0:] = False                     # the blade's two rows past the guard: drawn again below
        (flip, rot), eff = self.op_for("rapier", angle) if angle else ((False, 0), 0.0)
        out = super().turned(poly_pts, eff, about, src, shaft, guard)
        P = self.TURN_PAD
        s0 = XZ.lossless(np.array([[EXIT[0] - about[0], EXIT[1] - about[1]]]), flip, rot)[0] + np.array(about)
        u = R.turn_pt(TIP, GRIP, angle) - np.array(GRIP)
        u = u / np.hypot(*u)
        flat = abs(u[0]) >= abs(u[1])
        for t in np.arange(0.0, BLADE_LEN, 0.2):
            px, py = s0 + u * t
            if flat:
                cells = [((int(np.floor(px + 1e-6)), int(np.floor(py - 1 + 1e-6))), BLADE_HI),
                         ((int(np.floor(px + 1e-6)), int(np.floor(py + 1e-6))), BLADE_LO)]
            else:
                cells = [((int(np.floor(px - 1 + 1e-6)), int(np.floor(py + 1e-6))), BLADE_HI),
                         ((int(np.floor(px + 1e-6)), int(np.floor(py + 1e-6))), BLADE_LO)]
            for (x, y), c in cells:
                if 0 <= y + P < out.shape[0] and 0 <= x + P < out.shape[1] and out[y + P, x + P, 3] == 0:
                    out[y + P, x + P, :3] = c
                    out[y + P, x + P, 3] = 255
        return out


def cape(rgb):
    """The cape's crimson, not the teal legs."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (r > 90) & (g < 50) & (r > b + 30)


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
    D = Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != want.shape or (D.d != want).any() or D.gx0 != 0 or D.gy0 != 0:
        sys.exit("hd/picture.png does not read back as hd/design.png")
    op = D.d[..., 3] > 0
    D.pal = np.unique(D.d[op][:, :3], axis=0).astype(np.uint8)
    legs = {}
    for lg in (FRONT, BACK):
        th, sh = R.leg_masks(D, lg["area"], lg["hip"], lg["knee"], keep_out=cape, over_knee=0.5, under_knee=1.0,
                             extend=-100)
        legs[lg["name"] + "_thigh"], legs[lg["name"] + "_shin"] = th, sh
    arm = poly_mask(D, [ARM])
    rapier = poly_mask(D, [RAPIER]) & ~arm
    D.cut_props({"arm": arm, "rapier": rapier, **legs}, close=1, bare=set(legs))
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
    D.polys["arm"], D.polys["rapier"] = ARM, RAPIER
    D.AXES = {"arm": (GRIP[0] - SHOULDER[0], GRIP[1] - SHOULDER[1]),
              "rapier": (TIP[0] - GRIP[0], TIP[1] - GRIP[1])}
    D.SHAFTS = {}
    D.part("upper", D.rest(), take=False)
    D.taken = taken
    return D


def check_design(D):
    outside = int(((D.d != D.d0).any(-1) & ~D.taken).sum())
    rig = R.Rig(D)
    z0 = dict(angle=0, about=(0, 0))
    lay = [(n, z0) for n in sorted(D.props) if n.endswith(("_thigh", "_shin"))] + \
        [("upper", dict()), ("arm", z0), ("rapier", z0)]
    can = R.compose(rig, lay)
    got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
    D.diff_at = np.argwhere((got != D.d0).any(-1))
    return outside, int((got != D.d0).any(-1).sum())


class Rig(R.Rig):
    def finish(self, can):
        """R.Rig.finish, but the blade stays without an outline as drawn (design_fiora_hd): outline squares the tidy
        put on that touch nothing but the blade go again."""
        out = super().finish(can)
        blade = np.zeros(can.shape[:2], bool)
        for c in (BLADE_HI, BLADE_LO):
            blade |= (can[..., 3] > 0) & (can[..., :3] == c).all(-1)
        body = (can[..., 3] > 0) & ~blade
        added = (out[..., 3] > 0) & (can[..., 3] == 0)
        near_body = ndimage.binary_dilation(body, structure=np.ones((3, 3)))
        out[added & ~near_body] = 0
        return out


def make_rig(D):
    return Rig(D, pad=(80, 80, 80, 30))            # the rapier turned about her glove reaches far


def driver(rig, joints):
    return R.Driver(rig, joints, SPEC_HEIGHT, ROWS, legs=[FRONT, BACK],
                    # absolute: League's idle holds the sword arm 39 degrees down, the picture straight out - turned
                    # by the change from it, the raised arm of the attack came out pointing back through her
                    arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, relative=False, league_hand="r",
                             with_weapon=True, over_weapon=True),
                    weapons=[dict(name="rapier", grip=GRIP, tip=TIP, league=("weapon_b", "weapon_a"), relative=False,
                                  floor=2, always_front=True, back_when_back=True)],
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
    lay += [("upper", dict(dy=sink)), ("arm", dict(dy=sink, angle=0, about=SHOULDER)),
            ("rapier", dict(dy=sink, angle=0, about=GRIP))]
    return R.compose(rig, lay)


# ------------------------------------------------------------------------------------------------- the legs
# League's actions step, lunge and crouch on legs the rigid design legs cannot pose losslessly (league_kaisa's walk:
# every slid, cut or row-swung leg read as 「变形」), and Codex's drawn legs changed width frame to frame (the user:
# 「腿部变形了吧？」, memory codex-legs-deform). So the legs are drawn on League's bones the way league_xinzhao's
# approved run is (rig_xinzhao_hd.leg_cells): each thigh and shin a band of constant width whose squares take the
# design's own colours across the leg (one row of the design's thigh / shin, left to right), the design's gold knee
# guard stamped whole at the knee and the design's own boot stamped whole at the ankle - never turned, slid or
# resized. Thigh THIGH, shin SHIN_LEN squares (the design's), the shin never further than SHIN_BACK / SHIN_FWD degrees
# from upright (flatter put the upright boot beside the leg).
LEG_TAGS = ["run", "attack", "attack_e", "skill", "skill2"]
THIGH = 8.0
SHIN_LEN = 11.0
SHIN_BACK, SHIN_FWD = -70.0, 50.0
# per leg: the band's top on the hip row (its axis), the design's knee and ankle points, the profile rows (row, first
# column, end column), the knee guard's box (its gold squares stamped) and the boot's first row (the leg's squares
# from it down are the boot)
LEGS = {
    "near": dict(leg="fl", hip=(31.5, 36.0), knee=(32.5, 44.0), ankle=(30.5, 55.0), thigh_row=(38, 28, 35),
                 shin_row=(48, 28, 33), knee_box=(29, 41, 35, 46), boot_row=55),
    "far": dict(leg="bl", hip=(22.0, 36.0), knee=(20.5, 44.0), ankle=(15.0, 54.0), thigh_row=(38, 19, 25),
                shin_row=(48, 15, 20), knee_box=(16, 41, 23, 46), boot_row=54),
}
# Q's dash (League flies low, the body almost flat): the design a quarter turn clockwise, sword arm and rapier raised
# first so they point ahead (lossless, the way league_kaisa's R flight was accepted), DASH_LIFT rows off the ground
DASH = {"skill": [1, 2]}
DASH_LIFT, DASH_DX = 4, 4


def leg_parts(D):
    """{"near" | "far": dict(thigh profile, shin profile, knee (offsets, colours), boot (offsets, colours), drop)} from
    the design's own squares (drop: the ankle to the boot's sole)."""
    out = {}
    d = D.d0
    yy = np.arange(D.H)[:, None] * np.ones((1, D.W), int)
    for key, L in LEGS.items():
        leg = np.zeros((D.H, D.W), bool)
        for part in ("_thigh", "_shin"):
            leg |= XZ.square_mask(D, D.prop_masks[L["leg"] + part])[0]
        y, a, b = L["thigh_row"]
        thigh = d[y, a:b].copy()
        y, a, b = L["shin_row"]
        shin = d[y, a:b].copy()
        x0, y0, x1, y1 = L["knee_box"]
        box = d[y0:y1, x0:x1]
        gold = (box[..., 3] > 0) & (box[..., 0].astype(int) > 120) & (box[..., 2].astype(int) < 140)
        ys, xs = np.nonzero(gold)
        knee = (np.stack([xs + x0 + 0.5 - L["knee"][0], ys + y0 + 0.5 - L["knee"][1]], 1), box[ys, xs])
        ys, xs = np.nonzero(leg & (yy >= L["boot_row"]))
        boot = (np.stack([xs + 0.5 - L["ankle"][0], ys + 0.5 - L["ankle"][1]], 1), d[ys, xs])
        out[key] = dict(thigh=thigh, shin=shin, knee=knee, boot=boot, drop=float(boot[0][:, 1].max()) + 0.5)
    return out


def band(cells, A, B, profile):
    """The squares within half the profile's width of the segment A -> B into `cells` ({(x, y): rgba}), each the
    profile's colour at its place across the band (left to right looking down the leg)."""
    import math
    n_ = len(profile)
    hw = n_ / 2.0 - 0.01
    vx, vy = B[0] - A[0], B[1] - A[1]
    n = math.hypot(vx, vy) or 1e-9
    for y in range(int(min(A[1], B[1])) - n_, int(max(A[1], B[1])) + n_):
        for x in range(int(min(A[0], B[0])) - n_, int(max(A[0], B[0])) + n_ + 1):
            px, py = x + 0.5, y + 0.5
            t = ((px - A[0]) * vx + (py - A[1]) * vy) / n
            if t < -0.5 or t > n + 0.5:
                continue
            sd = (px - A[0]) * (vy / n) - (py - A[1]) * (vx / n)
            if abs(sd) <= hw:
                i = int(np.floor(sd + n_ / 2.0))
                cells[(x, y)] = profile[max(0, min(n_ - 1, i))]


def leg_layer(rig, part, H, K, A):
    """One leg on the canvas: thigh H -> K and shin K -> A as bands, the knee guard and the boot stamped, an outline
    ring round it."""
    cells = {}
    band(cells, H, K, part["thigh"])
    band(cells, K, A, part["shin"])
    for (off, cols), at in ((part["knee"], K), (part["boot"], A)):
        tx = np.floor(at[0] + off[:, 0]).astype(int)
        ty = np.floor(at[1] + off[:, 1]).astype(int)
        for x, y, c in zip(tx, ty, cols):
            cells[(int(x), int(y))] = c
    out = rig.canvas()
    line = np.array((*rig.D.outline, 255), np.uint8)
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and 0 <= q[1] < out.shape[0] and 0 <= q[0] < out.shape[1]:
                out[q[1], q[0]] = line
    for (x, y), c in cells.items():
        if 0 <= y < out.shape[0] and 0 <= x < out.shape[1]:
            out[y, x] = c
    return out


def spied(drv, j):
    """drv.frame(j)'s layers: (the frame without the legs, {leg name: (dx, dy)})."""
    seen = []
    orig = R.compose

    def spy(rig_, layers):
        seen.append(layers)
        return orig(rig_, layers)
    R.compose = spy
    try:
        drv.frame(j)
    finally:
        R.compose = orig
    layers = seen[-1]
    rest = [(n, o) for n, o in layers if not (isinstance(n, str) and n.endswith(("_thigh", "_shin")))]
    offs = {n: (o.get("dx", 0), o.get("dy", 0)) for n, o in layers if isinstance(n, str) and n.endswith("_thigh")}
    return R.compose(drv.rig, rest), offs


def drawn_frame(rig, drv, joints, parts, j):
    """The frame on drawn legs: the rig's body without its legs, the legs on League's thigh and shin directions from
    the hips the rig puts them at, the figure set so the lower boot stands on the ground (lifted as far as League's
    lower foot is above its design pose's: a leap)."""
    import math
    bare, offs = spied(drv, j)
    geo = {}
    for lg in (FRONT, BACK):
        key = lg["side"]
        L = LEGS[key]
        sd = drv.side[key]
        dx, dy = offs.get(lg["name"] + "_thigh", (0, 0))
        H = np.array((rig.ox + L["hip"][0] + dx, rig.oy + L["hip"][1] + dy))
        h, k, f = (np.array(j[f"{sd}_{n}"][:2], float) for n in ("hip", "knee", "foot"))
        t = (k - h) / (np.linalg.norm(k - h) or 1)
        s_ang = math.degrees(math.atan2(f[0] - k[0], f[1] - k[1]))       # from straight down, + forward
        s_ang = max(SHIN_BACK, min(SHIN_FWD, s_ang))
        K = H + t * THIGH
        A = K + SHIN_LEN * np.array((math.sin(math.radians(s_ang)), math.cos(math.radians(s_ang))))
        geo[key] = (H, K, A)
    d = joints["design"]
    feet = min(-j["l_foot"][1], -j["r_foot"][1])
    feet0 = min(-d["l_foot"][1], -d["r_foot"][1])
    lift = max(0.0, feet - feet0) * drv.s
    low = max(geo[k][2][1] + parts[k]["drop"] for k in geo)
    dy = int(round(rig.GY - lift - low))
    out = rig.canvas()
    for key in ("far", "near"):
        H, K, A = (v + (0, dy) for v in geo[key])
        lay = leg_layer(rig, parts[key], H, K, A)
        m = lay[..., 3] > 0
        out[m] = lay[m]
    body = np.roll(bare, dy, axis=0)
    if dy > 0:
        body[:dy] = 0
    elif dy < 0:
        body[dy:] = 0
    m = body[..., 3] > 0
    out[m] = body[m]
    out[rig.GY:] = 0
    return out


def dash_frame(rig, drv, j):
    """Q's dash: the figure, sword arm and rapier raised, a quarter turn clockwise (head ahead), off the ground."""
    up = drv.frame(j, dict(keep=True, arm=90, weapon=90))
    return R.lie(rig, up, k=-1, dx=DASH_DX, sink=-DASH_LIFT)


def frames(rig, joints):
    drv = driver(rig, joints)
    D = rig.D
    legs = {lg["name"]: leg_piece(D, lg) for lg in (FRONT, BACK)}
    parts = leg_parts(D)
    sheet = R.sheet_of(HERO)
    bake = json.load(open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8"))
    baked = {e["into"] for e in bake["items"] if "from" in e}
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in sheet or tag in baked:
            continue
        ms = [m for _, m in sheet[tag]]
        rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, legs, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        elif tag in LEG_TAGS:
            fr = [dash_frame(rig, drv, r["j"]) if i in DASH.get(tag, ()) else drawn_frame(rig, drv, joints, parts, r["j"])
                  for i, r in enumerate(rows)]
        else:
            fr = [drv.frame(r["j"]) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            # arm and rapier held down before she is laid a quarter turn: they lie along the ground, not up in the air
            lie = R.lie(rig, drv.frame(rows[3]["j"], dict(keep=True, arm=-90, weapon=-90)), k=1, dx=-2)
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
    ap.add_argument("--joints", help="tools/lol/league_joints.py's fiora_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint = {"arm": (0, 128, 255), "rapier": (0, 255, 128), "fl_thigh": (255, 0, 255), "fl_shin": (255, 128, 0),
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
