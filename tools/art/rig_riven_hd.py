#!/usr/bin/env python3
"""league_riven redone at PPU 1.5 from Codex's design picture (assets/source/riven/PICTURE_PROMPT_PPU.md, read back by
tools/art/design_riven_hd.py: 68 x 61, the user: 「用 PPU 1.5」), every action posed after League's own clip frame by
frame the way league_darius was (tools/art/rig_darius_hd.py; its lossless Design from rig_xinzhao_hd).

    python tools/art/design_riven_hd.py                                            # hd/design.png
    python tools/lol/league_joints.py assets/source/riven/poses.json --out <dir>   # League joints (once)
    python tools/art/rig_riven_hd.py --parts DIR                                   # the parts tinted + the rest-frame check
    python tools/art/rig_riven_hd.py --joints <dir>/riven_joints.json --review DIR   # every tag at 3x + GIFs
    python tools/art/rig_riven_hd.py --joints <dir>/riven_joints.json             # orig strips + the 1x sheet

Parts (design squares, 61 rows from the blade's tip to the soles): her sword hand (the far hand round the grip and its
forearm) turned about her shoulder after League's right shoulder-to-hand, the broken sword turned about her fist after
League's weapon, both only losslessly (as drawn, mirrored or quarter-turned: the one of the 8 nearest League's turn);
both legs as drawn; the upper body (head, the green top and shoulder plate, the open near hand, the belt and shorts)
moved with League's pelvis, at most a column off the hips. In the picture the sword's middle is hidden behind her head:
the sword is drawn from the picture with that stretch of blade made again along its own line out of the blade's
cross-section (SWORD_FILL) - hidden in the idle, it shows when she swings. The R-form tags (`*_r`) hold the same sword
with the green energy blade grown out of its broken edge (ENERGY: drawn square by square along the blade's line in the
colours of Codex's reforged blade, assets/source/riven/hd/codex_r_blade.png - Codex drew that one at another angle, so
it could not be turned onto the picture's sword). The effects stay baked as before (assets/source/native/
riven_bake.json, Rig.bake). The death ends lying: the figure a quarter turn.
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

HERO = "riven"
PPU = 1.5
DESIGN_ROWS = 61
ROWS = DESIGN_ROWS / PPU                     # game rows of the design picture, the blade's tip to the soles
BODY_ROWS = 56 / PPU                         # her hair's top (row 5) to the soles: what League's `height` measures
SPEC_HEIGHT = 45                             # assets/source/riven/poses.json "height"
SQUARE = XZ.SQUARE

# the blade's line (square edges): its middle and its direction (fitted to the blade's grey squares), across = AX
# turned a quarter clockwise on screen (down-right); the blade reaches BLADE_ALONG along it, BLADE_HW either side
BLADE_C, AX = np.array((53.79, 11.26)), np.array((0.891, -0.455))
ACROSS = np.array((-AX[1], AX[0]))
BLADE_ALONG, BLADE_HW = (-21.5, 14.0), 8.0
# the stretch hidden behind her head, from the guard to where the blade shows, made again from the cross-section at
# PROFILE_AT along the line
SWORD_FILL, PROFILE_AT = (-37.5, -20.5), -3.0   # (-16 ran a rune along the stretch as a stripe)
GRIP = (11.5, 23.5)                          # her fist round the grip
SHOULDER = (18.5, 28.0)                      # her far shoulder, behind the body
TIP = tuple(BLADE_C + AX * BLADE_ALONG[1])
HILT = [(0.0, 24.0), (4.0, 21.5), (13.0, 18.0), (19.0, 18.0), (19.0, 23.5), (14.0, 25.5), (4.0, 31.5), (0.0, 31.5)]
ARM = [(7.5, 19.0), (15.0, 19.0), (15.0, 23.0), (16.5, 24.0), (16.5, 32.0), (10.0, 32.0), (8.0, 27.0)]
# the energy blade: from ENERGY_FROM along the line ENERGY_LEN squares on, ENERGY_HW across at its root narrowing to
# the point; Codex's reforged blade's colours, edge to core
ENERGY_FROM, ENERGY_LEN, ENERGY_HW = 8.0, 30.0, 6.5
ENERGY = [(3, 80, 30), (89, 223, 65), (173, 249, 69), (240, 250, 225)]
FRONT = dict(name="fl", side="near", rigid=True, hip=(33.0, 46.5), knee=(36.0, 52.0), sole=(42.0, 60.0),
             area=[(29.5, 46.0), (38.0, 46.0), (43.0, 54.0), (48.5, 55.0), (48.5, 61.0), (35.5, 61.0), (33.0, 52.0),
                   (29.5, 49.0)])
BACK = dict(name="bl", side="far", rigid=True, hip=(21.0, 46.5), knee=(18.0, 52.0), sole=(16.0, 60.0),
            area=[(13.0, 46.0), (24.5, 46.0), (24.5, 49.0), (21.0, 54.0), (22.5, 57.0), (22.5, 61.0), (12.0, 61.0),
                  (12.0, 55.0), (15.0, 50.0)])
IDLE_SINK = [0, 0, 1, 1, 1, 1, 0, 0]
R_TAGS = {"attack_r": "attack", "skill_r": "skill", "q2_r": "q2", "q3_r": "q3", "skill2_r": "skill2"}
R_FORM = {"r_slash"}                         # the wind slash: reforged throughout
ULT_REFORGED = 2                             # the reforge (ult): reforged from this frame on

# ------------------------------------------------------------------------------------------------- the swords
# The user on the first rig (the picture's own blade, R-sized, turned 8 ways): 「锐雯的剑有这么大？开大才有这么打吧 还有
# 打的时候一套姿势吗？…还有武器挥打遮挡脸部？」. The picture's blade is cut away; her sword is one of Codex's angle drawings
# (tools/art/swords_riven_hd.py: 8 angles of the broken sword, 31 squares, and of the reforged one, 44 - each also
# mirrored left-right, up-down and both, 32 directions) - the one nearest the way League's weapon points, its grip
# under her fist. SWORD_REST: the way it points in the idle (League's riven_idle1: over her back, up and right);
# FACE: her face (x, y, r design squares), never under her fist; HEAD: her head with its hair, never under a sword in
# front of her (one that would cross it turns at most HEAD_TURN degrees, else goes behind her: on her back as League's).
SWORD_REST = 22.0
# the idle alone holds it up by her shoulder: at League's angle the short blade hid wholly behind her head and back
IDLE_HOLD = 54.0
FACE = (27.0, 21.0, 5.5)
HEAD, HEAD_TURN = (24.5, 16.5, 10.0), 30
GUARD_AT = 4.5                               # squares from the fist to the guard: the blade starts there
SWORD_HW = 4.5


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


def on_line(a, s):
    return BLADE_C + AX * a + ACROSS * s


def blade_poly(a0, a1, hw):
    return [tuple(on_line(a0, -hw)), tuple(on_line(a1, -hw)), tuple(on_line(a1, hw)), tuple(on_line(a0, hw))]


def steel(rgb):
    """The blade's squares: neutral greys up to its silver edge (spread under 20; her cream hair is warm, ~36), the
    green runes, the outline - not her hair, skin or clothes."""
    r, g, b = (rgb[..., k].astype(int) for k in range(3))
    grey = (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)) < 20
    rune = (g > r + 40) & (g > b + 40)
    line = (r + g + b) < 70
    return grey | rune | line


def squares_of(D, sq):
    """Design-square mask -> picture-pixel mask."""
    S = SQUARE
    px = np.zeros(D.pic.shape[:2], bool)
    px[:D.H * S, :D.W * S] = np.repeat(np.repeat(sq, S, 0), S, 1)
    return px


def paint(src, D, cells):
    """{(x, y): rgb} design squares painted into a picture-sized source."""
    S = SQUARE
    for (x, y), c in cells.items():
        if 0 <= x < D.W and 0 <= y < D.H:
            X, Y = int(round(D.d2p(x, y)[0])), int(round(D.d2p(x, y)[1]))
            src[Y:Y + S, X:X + S, :3] = c
            src[Y:Y + S, X:X + S, 3] = 255


def fill_cells(D):
    """The hidden stretch of blade: every square whose middle lies in SWORD_FILL along the line and within BLADE_HW
    across it, coloured as the blade's own cross-section at PROFILE_AT at the same distance across."""
    prof = {}
    for s in np.arange(-BLADE_HW, BLADE_HW + 0.01, 0.5):
        x, y = on_line(PROFILE_AT, s)
        xi, yi = int(np.floor(x)), int(np.floor(y))
        if 0 <= xi < D.W and 0 <= yi < D.H and D.d0[yi, xi, 3] > 0 and steel(D.d0[yi, xi][None, :3])[0]:
            prof[round(s * 2) / 2] = tuple(int(v) for v in D.d0[yi, xi, :3])
    keys = np.array(sorted(prof))
    cells = {}
    for y in range(D.H):
        for x in range(D.W):
            v = np.array((x + 0.5, y + 0.5)) - BLADE_C
            a, s = float(v @ AX), float(v @ ACROSS)
            if SWORD_FILL[0] <= a <= SWORD_FILL[1] and keys[0] - 0.5 <= s <= keys[-1] + 0.5:
                cells[(x, y)] = prof[float(keys[np.argmin(abs(keys - s))])]
    return cells


def energy_cells(D):
    """The green energy blade out of the broken edge, square by square: tapering from ENERGY_HW to a point, its edge
    the darkest green, a near-white core along the line."""
    cells = {}
    for y in range(-30, D.H):
        for x in range(-10, D.W + 40):
            v = np.array((x + 0.5, y + 0.5)) - BLADE_C
            a, s = float(v @ AX), float(v @ ACROSS)
            t = (a - (BLADE_ALONG[1] - ENERGY_FROM)) / ENERGY_LEN
            if not 0 <= t <= 1:
                continue
            hw = ENERGY_HW * (1 - t) ** 0.8 + 0.6
            if abs(s) > hw:
                continue
            k = abs(s) / hw
            cells[(x, y)] = ENERGY[3] if k < 0.25 else ENERGY[2] if k < 0.5 else ENERGY[1] if k < 0.8 else ENERGY[0]
    return cells


def design():
    want = picture()
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != want.shape or (D.d != want).any() or D.gx0 != 0 or D.gy0 != 0:
        sys.exit("hd/picture.png does not read back as hd/design.png")
    op = D.d[..., 3] > 0
    D.pal = np.unique(D.d[op][:, :3], axis=0).astype(np.uint8)
    legs = {}
    for lg in (FRONT, BACK):
        th, sh = R.leg_masks(D, lg["area"], lg["hip"], lg["knee"], over_knee=0.5, under_knee=1.0, extend=-100)
        legs[lg["name"] + "_thigh"], legs[lg["name"] + "_shin"] = th, sh
    arm = poly_mask(D, [ARM])
    # (1.5 squares wider than the blade: its outline along the top edge stayed in her body as a thin line)
    blade = poly_mask(D, [blade_poly(BLADE_ALONG[0], BLADE_ALONG[1] + 2, BLADE_HW + 1.5)]) & steel(D.pic[..., :3])
    sword = (poly_mask(D, [HILT]) | blade) & ~arm
    D.cut_props({"arm": arm, "sword": sword, **legs}, close=1, bare=set(legs))
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
    # the picture's blade is only cut away: every frame draws one of Codex's swords where it was (with_sword)
    D.swords = load_swords()
    D.polys["arm"], D.polys["sword"] = ARM, sword_poly(D.swords, "normal")
    D.AXES = {"arm": (GRIP[0] - SHOULDER[0], GRIP[1] - SHOULDER[1]),
              "sword": (np.cos(np.radians(SWORD_REST)), -np.sin(np.radians(SWORD_REST)))}
    D.SHAFTS = {}
    lossless = D.snap
    arm_ways = sorted({float(e) for e in D.ops("arm").values()})

    def snap(name, angle):
        if name == "sword":
            return angle                                     # the drawings take any way
        if name == "arm":
            # her far arm turned forward put her fist on her mouth (League's hand in front of its chest): the
            # way that puts the fist nearest where League's would be and off her face
            want = R.turn_pt(GRIP, SHOULDER, angle)
            for e in sorted(arm_ways, key=lambda e_: float(np.hypot(*(R.turn_pt(GRIP, SHOULDER, e_) - want)))):
                if np.hypot(*(R.turn_pt(GRIP, SHOULDER, e) - FACE[:2])) > FACE[2] + 1:
                    return e
        return lossless(name, angle)
    D.snap = snap
    D.part("upper", D.rest(), take=False)
    D.taken = taken
    return D


def energy(rig, can, layers):
    """The green energy blade (energy_cells, in design squares, past the picture's edges too) laid on a frame where the
    frame is clear, moved and turned as its `sword` layer was (the same lossless op, the same place)."""
    D = rig.D
    opts = next(o for n, o in layers if n == "sword")
    ang, about = opts.get("angle", 0), np.array(opts.get("about", GRIP), float)
    (flip, rot), _ = D.op_for("sword", ang) if ang else ((False, 0), 0.0)
    cells = energy_cells(D)
    pts = np.array([(x + 0.5, y + 0.5) for x, y in cells]) - about
    v = XZ.lossless(pts, flip, rot) + about + (rig.ox + opts.get("dx", 0), rig.oy + opts.get("dy", 0))
    out = can.copy()
    for (xy, c), (X, Y) in zip(cells.items(), np.floor(v).astype(int)):
        if 0 <= Y < out.shape[0] and 0 <= X < out.shape[1] and out[Y, X, 3] == 0:
            out[Y, X, :3] = c
            out[Y, X, 3] = 255
    return out


def load_swords():
    """{kind: [dict(img, angle, grip)]}: every drawing of swords.json as drawn and mirrored three ways."""
    sd = os.path.join(R.ROOT, "assets", "source", HERO, "hd", "swords")
    with open(lp(os.path.join(sd, "swords.json")), encoding="utf-8") as f:
        info = json.load(f)
    out = {"normal": [], "reforged": []}
    for name, i in info.items():
        img = np.asarray(Image.open(lp(os.path.join(sd, name + ".png"))).convert("RGBA"))
        h, w = img.shape[:2]
        gx, gy = i["grip"]
        a = i["angle"]
        tx, ty = i["tip"]
        px_, py_ = i["pommel"]
        for fx, fy in ((False, False), (True, False), (False, True), (True, True)):
            im = img[::-1 if fy else 1, ::-1 if fx else 1]
            ang = (180 - a if fx else a)
            ang = -ang if fy else ang
            f = lambda x, y: (w - x if fx else x, h - y if fy else y)   # noqa: E731
            out[name.split("_")[0]].append(dict(img=np.ascontiguousarray(im), angle=R.wrap(ang), grip=f(gx, gy),
                                                tip=f(tx, ty), pommel=f(px_, py_), name=name, flip=(fx, fy)))
    return out


def reach(swords, kind):
    """(behind, ahead): squares from the fist to the pommel's end and to the tip, the longest of the drawings."""
    back = max(float(np.hypot(*(np.subtract(s["pommel"], s["grip"])))) for s in swords[kind])
    ahead = max(float(np.hypot(*(np.subtract(s["tip"], s["grip"])))) for s in swords[kind])
    return back, ahead


def sword_poly(swords, kind):
    back, ahead = reach(swords, kind)
    u = np.array((np.cos(np.radians(SWORD_REST)), -np.sin(np.radians(SWORD_REST))))
    n = np.array((-u[1], u[0]))
    g = np.array(GRIP)
    return [tuple(g - u * back - n * SWORD_HW), tuple(g + u * ahead - n * SWORD_HW),
            tuple(g + u * ahead + n * SWORD_HW), tuple(g - u * back + n * SWORD_HW)]


def stamp(rig, swords, kind, heading, fist):
    """A canvas with the drawing of `kind` nearest `heading` (degrees on screen), its grip on `fist` (canvas)."""
    s = min(swords[kind], key=lambda s_: (abs(R.wrap(s_["angle"] - heading)), s_["flip"]))
    out = rig.canvas()
    x0, y0 = int(round(fist[0] - s["grip"][0])), int(round(fist[1] - s["grip"][1]))
    im = s["img"]
    h, w = im.shape[:2]
    ys, xs = np.nonzero(im[..., 3] > 0)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < out.shape[0]) & (X >= 0) & (X < out.shape[1])
    out[Y[ok], X[ok]] = im[ys[ok], xs[ok]]
    return out


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]
    return dst


def with_sword(rig, swords, layers, kind):
    """The frame of these layers with its "sword" layer (the picture's cut-out blade as the Driver turned it) drawn
    as Codex's sword: heading SWORD_REST + the layer's turn, the grip on the fist the layer was moved to."""
    i = next(k for k, (n, _) in enumerate(layers) if isinstance(n, str) and n == "sword")
    o = layers[i][1]
    heading = SWORD_REST + o.get("angle", 0)
    fist = (rig.ox + GRIP[0] + o.get("dx", 0), rig.oy + GRIP[1] + o.get("dy", 0))
    can = R.compose(rig, layers[:i]) if i else rig.canvas()
    over(can, stamp(rig, swords, kind, heading, fist))
    if i + 1 < len(layers):
        over(can, R.compose(rig, layers[i + 1:]))
    return can


def spied_frame(drv, j, o=None):
    """drv.frame(j, o) and the layers it composed."""
    seen = []
    orig = R.compose

    def spy(rig_, layers):
        seen.append(layers)
        return orig(rig_, layers)
    R.compose = spy
    try:
        can = drv.frame(j, o)
    finally:
        R.compose = orig
    return can, seen[-1]


def check_design(D):
    outside = int(((D.d != D.d0).any(-1) & ~D.taken).sum())
    rig = R.Rig(D)
    z0 = dict(angle=0, about=(0, 0))
    lay = [("arm", z0)] + \
        [(n, z0) for n in sorted(D.props) if n.endswith(("_thigh", "_shin"))] + [("upper", dict())]
    can = R.compose(rig, lay)
    got = can[rig.oy:rig.oy + D.H, rig.ox:rig.ox + D.W]
    D.diff_at = np.argwhere((got != D.d0).any(-1))
    return outside, int((got != D.d0).any(-1).sum())


def make_rig(D):
    return R.Rig(D, pad=(90, 90, 90, 30))          # the long sword turned about her fist reaches far


def driver(rig, joints, kind="normal"):
    D = rig.D
    ahead = reach(D.swords, kind)[1]
    tip = (GRIP[0] + ahead * np.cos(np.radians(SWORD_REST)), GRIP[1] - ahead * np.sin(np.radians(SWORD_REST)))
    drv = R.Driver(rig, joints, SPEC_HEIGHT, BODY_ROWS, legs=[FRONT, BACK],
                   arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, relative=True, league_hand="r",
                            with_weapon=True, over_weapon=True),
                   weapons=[dict(name="sword", grip=GRIP, tip=tip, league=("weapon", "weapon_tip"), relative=True,
                                 floor=2, rest_back=True, face=HEAD, face_turn=HEAD_TURN,
                                 face_from=(GRIP[0] + GUARD_AT * np.cos(np.radians(SWORD_REST)),
                                            GRIP[1] - GUARD_AT * np.sin(np.radians(SWORD_REST))))],
                   src=D.leg_src, leg_max=0, max_lean=1)
    drv.kind = kind
    return drv


def sword_frame(drv, j, o=None, r_form=False):
    """drv.frame with Codex's sword, and the layers (the "sword" layer as the Driver placed it)."""
    D = drv.rig.D
    keep = D.polys["sword"]
    D.polys["sword"] = sword_poly(D.swords, drv.kind)
    try:
        _, layers = spied_frame(drv, j, o)
    finally:
        D.polys["sword"] = keep
    return with_sword(drv.rig, D.swords, layers, drv.kind), layers


def leg_piece(D, lg):
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


def idle_frame(rig, legs, sink, rest=0.0, front=False):
    lay = [("arm", dict(dy=sink, angle=0, about=SHOULDER))]
    lay += [(legs[lg["name"]], dict()) for lg in (BACK, FRONT)]
    lay += [("upper", dict(dy=sink))]
    sword = ("sword", dict(dy=sink, angle=rest, about=GRIP))
    lay = lay[:-1] + [lay[-1], sword, lay[0]] if front else [sword] + lay
    return with_sword(rig, rig.D.swords, lay, "normal")


# ------------------------------------------------------------------------------------------------- the legs
# Her legs step and lunge in League's run and dashes; the design's legs as drawn cannot (no skirt to hide a lifted
# leg's cut top) and Codex's drawn legs change width frame to frame (memory codex-legs-deform), so in LEG_TAGS the legs
# are drawn on League's bones the way league_fiora's are (rig_fiora_hd): thigh and shin bands of constant width in the
# design's own colours across the leg (one row of the design's shorts / shin, left to right), the design's boot
# stamped whole at the ankle - never turned, slid or resized; the thighs go under her shorts (the body drawn over).
LEG_TAGS = ["run", "attack", "skill", "q2", "q3", "skill2", "r_slash"]
THIGH, SHIN_LEN = 6.0, 5.0
SHIN_BACK, SHIN_FWD = -70.0, 50.0
LEGS = {
    "near": dict(leg="fl", hip=(33.0, 44.5), knee=(35.5, 50.0), ankle=(37.5, 54.0), thigh_row=(47, 31, 36),
                 shin_row=(51, 35, 39), boot_row=54),
    "far": dict(leg="bl", hip=(23.0, 44.5), knee=(20.5, 50.0), ankle=(18.0, 54.5), thigh_row=(47, 22, 27),
                shin_row=(51, 18, 22), boot_row=54),
}


def leg_parts(D):
    """{"near" | "far": dict(thigh profile, shin profile, boot (offsets, colours), drop)} from the design's squares."""
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
        ys, xs = np.nonzero(leg & (yy >= L["boot_row"]))
        boot = (np.stack([xs + 0.5 - L["ankle"][0], ys + 0.5 - L["ankle"][1]], 1), d[ys, xs])
        out[key] = dict(thigh=thigh, shin=shin, boot=boot, drop=float(boot[0][:, 1].max()) + 0.5)
    return out


def band(cells, A, B, profile):
    """The squares within half the profile's width of the segment A -> B into `cells`, each the profile's colour at its
    place across the band (rig_fiora_hd.band)."""
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
                cells[(x, y)] = profile[max(0, min(n_ - 1, int(np.floor(sd + n_ / 2.0))))]


def leg_layer(rig, part, H, K, A):
    cells = {}
    band(cells, H, K, part["thigh"])
    band(cells, K, A, part["shin"])
    off, cols = part["boot"]
    for x, y, c in zip(np.floor(A[0] + off[:, 0]).astype(int), np.floor(A[1] + off[:, 1]).astype(int), cols):
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


def drawn_frame(rig, drv, joints, parts, j, r_form=False):
    """The frame on drawn legs (rig_fiora_hd.drawn_frame): the rig's body without its legs, the legs on League's
    thigh and shin directions from the hips the rig puts them at, the lower boot on the ground (or as high as League
    leaps); the R form's energy blade on its sword."""
    import math
    can, layers = sword_frame(drv, j)
    rest = [(n, o) for n, o in layers if not (isinstance(n, str) and n.endswith(("_thigh", "_shin")))]
    offs = {n: (o.get("dx", 0), o.get("dy", 0)) for n, o in layers if isinstance(n, str) and n.endswith("_thigh")}
    bare = with_sword(rig, rig.D.swords, rest, drv.kind)
    geo = {}
    for lg in (FRONT, BACK):
        key = lg["side"]
        L = LEGS[key]
        sd = drv.side[key]
        dx, dy = offs.get(lg["name"] + "_thigh", (0, 0))
        H = np.array((rig.ox + L["hip"][0] + dx, rig.oy + L["hip"][1] + dy))
        h, k, f = (np.array(j[f"{sd}_{n}"][:2], float) for n in ("hip", "knee", "foot"))
        t = (k - h) / (np.linalg.norm(k - h) or 1)
        s_ang = max(SHIN_BACK, min(SHIN_FWD, math.degrees(math.atan2(f[0] - k[0], f[1] - k[1]))))
        K = H + t * THIGH
        A = K + SHIN_LEN * np.array((math.sin(math.radians(s_ang)), math.cos(math.radians(s_ang))))
        geo[key] = (H, K, A)
    d = joints["design"]
    lift = max(0.0, min(-j["l_foot"][1], -j["r_foot"][1]) - min(-d["l_foot"][1], -d["r_foot"][1])) * drv.s
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


def frames(rig, joints):
    drvs = {False: driver(rig, joints), True: driver(rig, joints, "reforged")}
    D = rig.D
    legs = {lg["name"]: leg_piece(D, lg) for lg in (FRONT, BACK)}
    parts = leg_parts(D)
    sheet = R.sheet_of(HERO)
    bake = json.load(open(lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8"))
    baked = {e["into"] for e in bake["items"] if "from" in e}
    out = {}
    for tag in sheet:
        if tag in baked:
            continue
        base = R_TAGS.get(tag, tag)
        if base not in joints["tags"]:
            sys.exit(f"{tag}: no League frames")
        rows = R.fit_rows(joints["tags"][base], len(sheet[tag]))
        ms = [m for _, m in sheet[tag]]
        drv = drvs[tag in R_TAGS or tag in R_FORM]
        if tag == "idle":
            fr = [idle_frame(rig, legs, IDLE_SINK[i % len(IDLE_SINK)], IDLE_HOLD) for i in range(len(ms))]
        elif base in LEG_TAGS:
            fr = [drawn_frame(rig, drv, joints, parts, r["j"]) for r in rows]
        elif tag == "ult":
            fr = [sword_frame(drvs[i >= ULT_REFORGED], r["j"])[0] for i, r in enumerate(rows)]
        else:
            fr = [sword_frame(drv, r["j"])[0] for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            # the sword pointing straight down in front of her first: laid a quarter turn it lies along the ground
            # beside her, not up in the air (behind her it vanished under the body)
            _, lay = spied_frame(drv, rows[3]["j"], dict(keep=True, arm=-90, weapon=-90 - SWORD_REST))
            sw = next(x for x in lay if isinstance(x[0], str) and x[0] == "sword")
            lay = [x for x in lay if x is not sw] + [sw]
            lie = R.lie(rig, with_sword(rig, D.swords, lay, "normal"), k=1, dx=-2)
            fr = fr[:4] + [lie.copy() for _ in fr[4:]]
        out[tag] = list(zip(fr, ms))
    acts = rig.bake(out)
    for t in sheet:
        if t not in acts or len(acts[t]) != len(sheet[t]) or \
                [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: frames or timing differ from the sheet")
    return {t: acts[t] for t in sheet}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", help="tools/lol/league_joints.py's riven_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        tint = {"arm": (0, 128, 255), "sword": (0, 255, 128), "fl_thigh": (255, 0, 255), "fl_shin": (255, 128, 0),
                "bl_thigh": (255, 255, 0), "bl_shin": (255, 0, 0)}
        img = D.d0.astype(float).copy()
        for n, c in tint.items():
            sq, _ = XZ.square_mask(D, D.prop_masks[n])
            img[sq, :3] = img[sq, :3] * 0.45 + np.array(c) * 0.55
        Image.fromarray(np.repeat(np.repeat(img.astype(np.uint8), 12, 0), 12, 1)).save(
            os.path.join(a.parts, f"{HERO}_parts.png"))
        rig = make_rig(D)
        legs = {lg["name"]: leg_piece(D, lg) for lg in (FRONT, BACK)}
        import design_fiora_hd as FD
        cells = []
        for rest, front in ((0, False), (18, False), (36, False), (54, False), (0, True), (-40, True)):
            can = rig.finish(idle_frame(rig, legs, 0, rest, front))
            ys, xs = np.nonzero(can[..., 3] > 0)
            im = Image.fromarray(can[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3])
            cells.append((f"{SWORD_REST + rest:g} deg" + (" front" if front else ""), FD.shown(im, 1, 6)))
        FD.strip(cells).convert("RGB").save(os.path.join(a.parts, f"{HERO}_idle_swords.png"))
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
