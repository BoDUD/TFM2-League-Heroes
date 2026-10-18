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
straight shaft of its own brown), and his near arm (gold-trimmed purple sleeve, brown forearm guard, the gloved fist on
the shaft). Both are only ever moved losslessly (the user, on the first actions: 「还有武器变形？」 - RotSprite turns of the
spear redrew its blade, hook and rings differently in every frame): as drawn, mirrored or quarter-turned (8 ways,
Design.snap picks the one nearest League's angle, ppu_rig.Driver puts the fist and the spear where that one puts them),
the spear also slid along its own line through the fist as League's hand moves along League's spear (League holds it by
the butt to thrust). The spear is drawn BEHIND the body unless League's comes forward. The legs never turn in the
actions: as drawn, moved with the figure. The upper body (head, ribbons, coat, the open far hand) moves with League's
pelvis and leans with its chest, never turned.

The run (the user: 「跑步腿不对吧？这样跑步的？」「你参考原版赵兴怎么跑步的？」 - the first run moved the wide stance's legs a
column or two) is League's Runbase frame for frame, the way his approved 1x run was made (rig_xinzhao.run): the hips
together under the middle of the waist, the front flap cut short (FLAP_END), the body as drawn leaning RUN_LEAN columns
forward and bobbing a row; each leg drawn on League's thigh and shin angles in the design's own trouser shades (the near
leg lit, the far leg shaded) and greave steels, a knee cap in its knee-guard golds, and at the ankle the design's own
boot stamped whole (never turned or slid: 「脚严重变形啊」); the near leg over the flap.
The idle: the upper body, the arm and the spear sinking whole rows over the standing legs (breathing, the sheet's 8
frames). skill2 and ult end with the W slash and the R tell drawn into the frames as before
(assets/source/native/xinzhao_bake.json, Rig.bake). The death ends lying: the figure without the spear a quarter turn,
the spear flat on the ground under him (its columns slid level: no lossless turn lays it flat).
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
# the shaft's stretches the picture never shows, drawn as straight lines of its brown wherever the spear moves them
# into view: under the fist (no outline round it: at rest the fist covers it whole) and behind the body (outlined)
SHAFT_FIST = (on_spear(29.0), on_spear(40.5))
SHAFT = (on_spear(40.0), on_spear(72.0))
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
SHAFT_FIST = (E(SHAFT_FIST[0]), E(SHAFT_FIST[1]))
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
    despeckle) would change design squares, so a part is the design's own squares; turned, it is mirrored and / or
    quarter-turned about the point (every square kept, none redrawn) - the one of the 8 ways nearest the angle asked
    (snap), its axis (AXES) measuring the angle."""

    AXES = {}
    SHAFTS = {}

    def ops(self, name):
        """{(flip, rot): the angle (degrees, counter-clockwise) the part's axis turns by under that move}."""
        ax = np.array(self.AXES[name], float)
        out = {}
        for flip in (False, True):
            for rot in range(4):
                v = lossless(ax[None], flip, rot)[0]
                out[(flip, rot)] = round(R.wrap(R.heading(v) - R.heading(ax)), 3)
        return out

    def op_for(self, name, angle):
        best = None
        for (flip, rot), eff in self.ops(name).items():
            key = (round(abs(R.wrap(eff - angle)), 3), flip, rot)
            if best is None or key < best[0]:
                best = (key, (flip, rot), eff)
        return best[1], best[2]

    def snap(self, name, angle):
        """The angle the part can really take nearest `angle` (0 for a part that never turns)."""
        if name not in self.AXES:
            return 0
        return self.op_for(name, angle)[1]

    def turn(self, name, angle, about, src=None):
        self._turning = name
        return super().turn(name, angle, about, src)

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
        name = getattr(self, "_turning", None)
        if angle and name not in self.AXES:
            sys.exit(f"{name}: turned {angle} degrees but only {sorted(self.AXES)} turn")
        (flip, rot), _ = self.op_for(name, angle) if angle else ((False, 0), 0.0)
        out = np.zeros_like(part)
        ys, xs = np.nonzero(part[..., 3] > 0)
        v = np.stack([xs - P + 0.5 - about[0], ys - P + 0.5 - about[1]], 1)
        v = lossless(v, flip, rot)
        tx = np.floor(about[0] + v[:, 0] + P).astype(int)
        ty = np.floor(about[1] + v[:, 1] + P).astype(int)
        ok = (tx >= 0) & (tx < Wd) & (ty >= 0) & (ty < Hd)
        out[ty[ok], tx[ok]] = part[ys[ok], xs[ok]]
        for (x0, y0), (x1, y1), w, colour, rim in self.SHAFTS.get(name, ()):
            ends = lossless(np.array([[x0 - about[0], y0 - about[1]], [x1 - about[0], y1 - about[1]]]), flip, rot)
            (X0, Y0), (X1, Y1) = ends + np.array(about) + P
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


def lossless(v, flip, rot):
    """Offsets (n, 2) mirrored left-right (flip), then turned `rot` quarter turns counter-clockwise on screen (y down)."""
    x, y = np.array(v[:, 0], float), np.array(v[:, 1], float)
    if flip:
        x = -x
    for _ in range(rot % 4):
        x, y = y, -x
    return np.stack([x, y], 1)


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
    brown = shaft_colour(D)
    D.SHAFTS = {"spear": [(SHAFT_FIST[0], SHAFT_FIST[1], 1.8, brown, 0.0), (SHAFT[0], SHAFT[1], 1.8, brown, 1.0)]}
    D.AXES = {"spear": (E(SPEAR_B)[0] - E(SPEAR_A)[0], E(SPEAR_B)[1] - E(SPEAR_A)[1]),
              "arm": (GRIP[0] - SHOULDER[0], GRIP[1] - SHOULDER[1])}
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
                    arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, over_weapon=True, relative=True, dead=ARM_DEAD,
                             with_weapon=True),
                    weapons=[dict(name="spear", grip=GRIP, tip=BUTT, league=("weapon_a", "weapon_b"), relative=True,
                                  floor=2, rest_back=True, slide=dict(blade=E(SPEAR_A), lo=0.2, hi=SLIDE_HI), face=(*FACE, 7.0))],
                    src=rig.D.leg_src, leg_max=0)                 # the legs as drawn: never turned


# the run (see the module's doc): hips RUN_HIP_DX either side of the pivot on the waist's row, thighs RUN_THIGH long
# and RUN_HW half wide, a thigh swinging forward never folds its shin flatter than RUN_TRAIL degrees back
RUN_LEAN = 3
RUN_HIP_DX = 3.5
RUN_HIP_ROW = 47.5
RUN_THIGH = 10.5
RUN_HW = 2.8
RUN_TRAIL = -50.0
FLAP_END = 53                                  # design row: the front flap cut here in the run (it hangs to 59)
TROUSER = ((208, 151, 247), (169, 111, 208))    # the design's trouser shades: lit, shade
# the shins drawn on League's shin angle in the design's greave steels (RUN_SHIN long, RUN_SHW half wide), never
# flatter than RUN_KICK back nor more than RUN_REACH forward; at the knee a small cap in the design's knee-guard golds;
# at the ankle the design's own boot (its cuff, sole and the outline under it: the leg's rows from BOOT_ROW down) stamped
# whole - never turned, mirrored or slid (the user: 「脚严重变形啊」 - the second run turned and slid the whole shin and
# boot); the near boot mirrored once so its toe points forward as the far one's does (the stance turned it out)
RUN_SHIN = 6.0
RUN_SHW = 2.0
RUN_KICK = -70.0
RUN_REACH = 35.0
GREAVE = ((252, 252, 252), (212, 217, 231), (137, 139, 164), (73, 74, 95))   # the design's greave: white, light, steel, shade
KNEE_CAP = ((253, 209, 9), (246, 159, 1), (134, 61, 3))           # the design's knee guard: light, gold, shade
BOOT_ROW = 60
BOOTS = {"near": dict(leg="nl", ankle=(39.5, 60.0), mirror=True), "far": dict(leg="fl", ankle=(79.0, 60.0), mirror=False)}
SLIDE_HI = 0.6                                 # the fist at most this share of the spear back from the blade
FACE = (66.0, 25.0)                            # between the eyes (square edges): the spear in front keeps 7 clear
ARM_DEAD = 30                                  # League's arm turned less than this from its idle: the arm as drawn


def run_boots(D):
    """{"near" | "far": (offsets from the ankle (n, 2), colours (n, 4))}: the leg's squares from BOOT_ROW down, the
    near one mirrored about its ankle."""
    yy = np.arange(D.H)[:, None] * np.ones((1, D.W), int)
    out = {}
    for key, bt in BOOTS.items():
        leg = np.zeros((D.H, D.W), bool)
        for part in ("_thigh", "_shin"):
            leg |= square_mask(D, D.prop_masks[bt["leg"] + part])[0]
        ys, xs = np.nonzero(leg & (yy >= BOOT_ROW))
        off = np.stack([xs + 0.5 - bt["ankle"][0], ys + 0.5 - bt["ankle"][1]], 1)
        if bt["mirror"]:
            off[:, 0] = -off[:, 0]
        out[key] = (off, D.d0[ys, xs])
    return out


def band(cells, A, B, hw, colour_of):
    """Squares within hw of the segment A -> B into `cells` ({(x, y): rgba}), coloured by colour_of(side)."""
    import math
    vx, vy = B[0] - A[0], B[1] - A[1]
    n = math.hypot(vx, vy) or 1e-9
    for y in range(int(min(A[1], B[1])) - 4, int(max(A[1], B[1])) + 4):
        for x in range(int(min(A[0], B[0])) - 4, int(max(A[0], B[0])) + 5):
            px, py = x + 0.5, y + 0.5
            t = max(0.0, min(n, ((px - A[0]) * vx + (py - A[1]) * vy) / n))
            qx, qy = A[0] + vx / n * t, A[1] + vy / n * t
            if math.hypot(px - qx, py - qy) <= hw:
                cells[(x, y)] = colour_of((px - qx) * (vy / n) - (py - qy) * (vx / n))


def leg_cells(H, K, A, far):
    """{(x, y): rgba} the leg drawn on its bones - the thigh hip H -> knee K in the trouser shades (the near one lit with
    its back edge shaded, the far one shaded with its front edge lit), the shin K -> ankle A in the greave steels, the
    knee cap - and its outline ring (a list of squares)."""
    lit, shade = (np.array((*c, 255), np.uint8) for c in TROUSER)
    g_white, g_light, g_steel, g_dark = (np.array((*c, 255), np.uint8) for c in GREAVE)
    cap = [np.array((*c, 255), np.uint8) for c in KNEE_CAP]
    cells = {}
    band(cells, H, K, RUN_HW, (lambda sd: lit if sd > 1.6 else shade) if far else (lambda sd: shade if sd < -0.8 else lit))
    band(cells, K, A, RUN_SHW, (lambda sd: g_light if sd > 0.9 else g_steel if sd > -0.3 else g_dark) if far else
         (lambda sd: g_white if sd > 0.9 else g_light if sd > -0.3 else g_steel))
    # the knee guard: a gold band across the knee, 4 wide and 2 tall, lit on top
    kx, ky = int(np.floor(K[0])) - 2, int(np.floor(K[1])) - 1
    for dx_ in range(4):
        cells[(kx + dx_, ky)] = cap[0] if dx_ < 3 else cap[1]
        cells[(kx + dx_, ky + 1)] = cap[1] if dx_ < 3 else cap[2]
    ring = []
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in cells:
                ring.append((x + dx, y + dy))
    return cells, ring


def run_frame(rig, j):
    """{"near" | "far": (hip, knee, ankle)} on the canvas after League's joints j (the figure not yet set down)."""
    import math
    side = {"near": "r", "far": "l"}
    legs = {}
    for key in ("far", "near"):
        sd = side[key]
        t_ang = math.degrees(math.atan2(j[f"{sd}_knee"][0] - j[f"{sd}_hip"][0], j[f"{sd}_knee"][1] - j[f"{sd}_hip"][1]))
        s_ang = math.degrees(math.atan2(j[f"{sd}_foot"][0] - j[f"{sd}_knee"][0], j[f"{sd}_foot"][1] - j[f"{sd}_knee"][1]))
        if t_ang > 5 and s_ang < RUN_TRAIL:
            s_ang = RUN_TRAIL
        s_ang = max(RUN_KICK, min(RUN_REACH, s_ang))
        H = np.array([rig.CX + (-RUN_HIP_DX if key == "near" else RUN_HIP_DX), rig.oy + RUN_HIP_ROW])
        K = np.round((H + RUN_THIGH * np.array([math.sin(math.radians(t_ang)), math.cos(math.radians(t_ang))])) * 2) / 2
        A = np.round((K + RUN_SHIN * np.array([math.sin(math.radians(s_ang)), math.cos(math.radians(s_ang))])) * 2) / 2
        legs[key] = (H, K, A)
    return legs


def run_compose(rig, legs, boots, dy):
    """The run's frame: the spear behind, the far leg, the body (its flap cut), the near leg over the flap."""
    D = rig.D
    spear = R.compose(rig, [("spear", dict(angle=0, about=GRIP, dx=RUN_LEAN, dy=dy))])
    top = R.compose(rig, [("upper", dict(dx=RUN_LEAN, dy=dy)),
                          ("arm", dict(angle=0, about=SHOULDER, dx=RUN_LEAN, dy=dy))])
    top[rig.oy + FLAP_END + dy:] = 0
    out = rig.canvas()
    m = spear[..., 3] > 0
    out[m] = spear[m]
    outline = np.array((*D.outline, 255), np.uint8)
    for key in ("far", "near"):
        H, K, A = (np.asarray(v) + (0, dy) for v in legs[key])
        leg = rig.canvas()
        cells, ring = leg_cells(H, K, A, far=(key == "far"))
        for (x, y) in ring:
            if 0 <= y < leg.shape[0] and 0 <= x < leg.shape[1]:
                leg[y, x] = outline
        for (x, y), c in cells.items():
            if 0 <= y < leg.shape[0] and 0 <= x < leg.shape[1]:
                leg[y, x] = c
        off, cols = boots[key]
        tx = np.floor(A[0] + off[:, 0]).astype(int)
        ty = np.floor(A[1] + off[:, 1]).astype(int)
        ok = (tx >= 0) & (tx < leg.shape[1]) & (ty >= 0) & (ty < leg.shape[0])
        leg[ty[ok], tx[ok]] = cols[ok]
        if key == "near":
            m = top[..., 3] > 0
            out[m] = top[m]
            hem = int(rig.oy + RUN_HIP_ROW + dy)       # above the hips the coat stays over the near leg
            lm = leg[..., 3] > 0
            lm[:hem] &= ~m[:hem]
            out[lm] = leg[lm]
        else:
            m = leg[..., 3] > 0
            out[m] = leg[m]
    out[rig.GY:] = 0
    return out


def run_frames(rig, rows):
    """The run's frames: League's Runbase on the design (run_frame), the lowest boot's sole on the ground, both feet off
    it in League's flight frames a row higher, the body bobbing a row with League's pelvis."""
    boots = run_boots(rig.D)
    drop = {k: float(v[0][:, 1].max()) + 0.5 for k, v in boots.items()}     # ankle -> the boot's lowest row's bottom
    pel = sorted(r["j"]["pelvis"][1] for r in rows)
    mid = pel[len(pel) // 2]
    out = []
    for r in rows:
        j = r["j"]
        legs = run_frame(rig, j)
        low = max(legs[k][2][1] + drop[k] for k in legs)
        air = all(-j[f"{s_}_foot"][1] * PPU > 14 for s_ in "rl")
        bob = int(round(max(-1, min(1, (mid - j["pelvis"][1]) * PPU * 0.15))))
        dy = int(round(rig.GY - low)) - (1 if air else 0) - bob
        out.append(run_compose(rig, legs, boots, dy))
    return out


def leg_piece(D, lg):
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


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
    head forward as League's falls (rig_jax_hd); the spear flat on the ground under him - no lossless turn lays its 24
    degrees flat (turned with him it stood straight up and lifted the lying body off the ground), so its columns slide
    level, every square kept."""
    keep = drv.weapons
    drv.weapons = []
    try:
        body = R.lie(rig, drv.frame(j), k=-1, dx=2)
    finally:
        drv.weapons = keep
    sp = R.compose(rig, [("spear", dict(angle=0, about=GRIP))])
    ys, xs = np.nonzero(sp[..., 3] > 0)
    k = (SPEAR_B[1] - SPEAR_A[1]) / (SPEAR_B[0] - SPEAR_A[0])
    ys = ys - np.round(k * (xs - xs.min())).astype(int)
    flat = rig.canvas()
    ys0 = ys - ys.max() + rig.GY - 1                 # its lowest square on the ground's row
    xs0 = xs - int(round((xs.min() + xs.max()) / 2)) + rig.CX
    ok = (ys0 >= 0) & (ys0 < flat.shape[0]) & (xs0 >= 0) & (xs0 < flat.shape[1])
    flat[ys0[ok], xs0[ok]] = sp[ys[ok] + np.round(k * (xs[ok] - xs.min())).astype(int), xs[ok]]
    m = body[..., 3] > 0
    flat[m] = body[m]
    return flat


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
            fr = run_frames(rig, rows)
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
