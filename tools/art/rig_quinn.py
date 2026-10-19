#!/usr/bin/env python3
"""league_quinn's action frames posed from the approved designs' own squares (the 2026-10-19 frame-audit way: no
Codex strips, lossless poses compared with League's clips - tools/lol/anim_graph.py Quinn, pose_ref.py).

    python tools/art/rig_quinn.py --parts DIR       # the idle design with its parts tinted + pose tries (12x)
    python tools/art/rig_quinn.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_quinn.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_quinn.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_quinn_grid.py: the PPU 1.3 picks redrawn by Codex at PPU 2.0 - 「像素有点太低了 太多模糊
的了 调一下PPU」, the user's pick A-1, 2026-10-19 - with the face redrawn on the grid; 38 game px, one palette): idle.png
(3/4 front, the crossbow arm held out to the right, 65 x 75: every standing action's base and the one face of every
frame) and ride.png (her riding Valor, 100 x 72: R's ride). Every pose is lossless: parts cut square by square from a
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
PPU = 2.0
SRC = os.path.join(R.ROOT, "assets", "source", "quinn", "hd")
with open(os.path.join(R.ROOT, "assets", "source", "quinn", "poses_side.json"), encoding="utf-8") as _f:
    F_PITCH = json.load(_f)["camera"]["pitch"]           # the side camera's pitch (hd/side/quinn_joints.json)


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
SHOULDER = (32.5, 25.5)       # (x, y) the crossbow arm turns about
SHOULDER_ROW = 25             # the crossbow arm's root row (it moves with the lean's shift there)
HEAD_LOW = 22                 # the head's lowest row (the chin): the head leans as one block
CAPE_ROW, CAPE_COL = 46, 9    # the cape's hem: rows from CAPE_ROW down, columns to CAPE_COL (under the near hand)
LEG_TOP = 46                  # the legs: rows LEG_TOP to the soles, split at LEG_X
LEG_X = 22
# The crossbow arm is her far arm, reaching out from behind her chest: its fist (the cuff, the glove and the crossbow,
# the arm's squares from FIST_X on) hangs at WRIST, the cuff's left edge on the sleeve's middle row. Held anywhere but out
# at the shoulder, the arm is drawn again from the shoulder - an upper arm and a forearm, bands across the sleeve's own
# squares (SLEEVE, light top to dark bottom: the idle's column 35, rows 24-27), behind the body as a far arm is - and
# the fist put on at its end (the user, 2026-10-19, on the run's crossbow moved whole down to her hip, the hand with no
# arm to the shoulder: 「手拿武器有点奇怪」). In a dying fall the crossbow (BOW_X on: the glove and the bow) drops as
# League's does.
FIST_X, BOW_X = 39, 44
WRIST = (39.0, 25.5)
SLEEVE = (0x53099A, 0x22205F, 0x1C133D, 0x1C133D)
CRACK, CRACK_W = 36, 2.3      # an enclosed gap at most this many squares and this far from its edge is a crack (a wider
                              # one - between the cape's hem and a back leg - stays open, as the idle's gap there; filled
                              # with the cape's shade it read as the cape grown a hand longer)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=stand_col(d))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    op = d[..., 3] > 0
    arm = op & (yy >= 14) & (yy <= 31) & (xx >= 33)
    D.part("arm", arm)
    legs = op & (yy >= LEG_TOP) & (xx >= 10)
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
IDLE_HEAD = (0, 22, 13, 34)    # rows / cols of the idle's head: the visor crest to the chin, the hood
RIDE_HEAD = (0, 19, 46, 67)
RIDE_CLEAR = 18                # the ride head's rows cleared (below them its chin and collar meet the arm)


def skin(d):
    """Her skin (design_quinn_grid.face's test: the visor's pale golds are far greener than blue)."""
    c = d[..., :3].astype(int)
    return ((d[..., 3] > 0) & (c[..., 0] > 200) & (c[..., 2] > 90) & (c[..., 1] - c[..., 2] < 60)
            & (c[..., 0] - c[..., 2] > 40))


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
        self.other = {"ride": self.placed(ride_design(D))}
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
        # the cape's hem (her back, behind the legs: drawn first, the legs over it - at the idle's own layering it hid
        # every heel kicked up behind) and the rest of the body (the skirt over the thighs' tops)
        yy, xx = np.mgrid[0:D.H, 0:D.W]
        hem = (yy >= CAPE_ROW) & (xx <= CAPE_COL) & (b[..., 3] > 0)
        cape = np.zeros_like(b)
        cape[hem] = b[hem]
        b[hem] = 0
        self.BODY = pad(b)
        self.CAPE = pad(cape)
        self.CAPE_LOW = int(np.nonzero((cape[..., 3] > 0).any(1))[0].max())
        arm = D.layer("arm")
        self.FIST, self.BOW = (pad(np.where((xx >= x0)[..., None], arm, 0).astype(np.uint8)) for x0 in (FIST_X, BOW_X))
        bys = np.nonzero((self.BOW[..., 3] > 0).any(1))[0]
        self.BOW_LOW = int(bys.max()) - P            # the crossbow's lowest row (design rows)
        self.SLEEVE = [QL.rgb(c) for c in SLEEVE]
        self.PITCH = F_PITCH
        self._cache = {}

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

    def pose(self, crouch=0, whole=(0, 0), arm=(0, 0), arm_rot=0, legs=None, fill=True, no_arm=False):
        """crouch: rows the body (with the arm) sets down onto the legs; whole: the whole figure; arm: the crossbow arm
        moved, arm_rot quarter turns counter-clockwise about SHOULDER (1: pointing up); legs: ((near dx, dy),
        (far dx, dy)) for the idle's own legs."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        L = self.L
        ux, uy = wx, wy + crouch
        (nx, ny), (fx, fy) = legs or ((0, 0), (0, 0))
        leg_layers = [(L["far_leg"], dict(dx=wx + fx, dy=wy + fy)), (L["near_leg"], dict(dx=wx + nx, dy=wy + ny))]
        layers = [*leg_layers, (L["body"], dict(dx=ux, dy=uy))]
        if not no_arm:
            layers.append((L["arm"], dict(dx=ux + arm[0], dy=uy + arm[1], rot=arm_rot, about=SHOULDER)))
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def leant(self, per):
        """The body (without legs and crossbow arm) leant forward on an even line, no square resampled (league_zeri's
        run): every row above the hips one square further right every `per` rows, the head (rows to HEAD_LOW) one block
        by its lowest row's amount. -> (padded layer, the shift at the shoulder - the arm moves by it)."""
        key = ("lean", per)
        if key not in self._cache:
            src = self.BODY
            out = np.zeros_like(src)
            for y in range(src.shape[0]):
                dy = y - P
                ref = max(dy, HEAD_LOW)
                sh = int((QL.CUT_ROW - ref) // per) if ref < QL.CUT_ROW else 0
                if sh:
                    out[y, sh:] = src[y, :-sh]
                else:
                    out[y] = src[y]
            self._cache[key] = (out, int((QL.CUT_ROW - SHOULDER_ROW) // per))
        return self._cache[key]

    def drawn(self, j, ref=None, arm=(0, 0), arm_rot=0, air=False, lunge=0.5, shift=(0, 0), swing=1.0, lean=0,
              hips=None, flight=None, cape=(0, 0), spread=None, roles=False, ground=False, hold=None, drop=False):
        """A frame on legs drawn on League's joints j (quinn_legs, the side camera's): the body moved forward / back
        lunge x League's pelvis travel from ref's (default the design pose), set on the ground by its lowest boot, or
        lifted as far as League's lower foot leaves the floor (air); the crossbow arm moved / turned losslessly; shift:
        the whole frame; swing: League's leg angles widened (quinn_legs.geometry); lean: the body leant forward one
        square every `lean` rows (0: upright); hips: the hips' places instead of the idle's (quinn_legs.geometry);
        flight: (the tag's lowest foot height in game px, share kept) - lifted as League's lower foot is above its
        lowest in the tag (a run's both-feet-off-the-ground frames); cape: the cape's hem moved whole (flying back as
        she runs); spread: the legs placed by League's feet seen from the hips, the direction widened
        (quinn_legs.geometry_ik) instead of by League's thigh and shin angles; ground: League's joints without the
        camera's pitch, her feet put on the floor where League's are and a knee League has down kneeling
        (quinn_legs.geometry_ground); hold: dict(elbow, wrist[, rot]) - the arm drawn from the shoulder to the elbow
        and the wrist (squares from the shoulder), the fist on it turned rot quarter turns counter-clockwise; drop: no
        crossbow arm (the bow fell; her far arm hangs behind her)."""
        d = self.JS["design"]
        floor = None
        if ground:
            j, d = (QL.flat(x, self.PITCH, self.JS["unit"]) for x in (j, d))
            ref = ref and QL.flat(ref, self.PITCH, self.JS["unit"])
            geo, floor = QL.geometry_ground(j, d, self.P, spread=spread or 1.0, hips=hips, roles=roles)
        else:
            geo = (QL.geometry_ik(j, self.P, spread=spread, hips=hips, roles=roles) if spread else
                   QL.geometry(j, self.P, swing=swing, hips=hips))
        low = floor if floor is not None else max(geo[k][2][1] + self.P[k]["drop"] for k in geo)
        r = ref or d
        lift = 0.0
        if air:
            lift = max(0.0, min(-j["l_foot"][1], -j["r_foot"][1]) - min(-d["l_foot"][1], -d["r_foot"][1])) * QL.PPU
        if flight:
            low_tag, keep = flight
            lift = max(0.0, self.toe_height(j) - low_tag) * QL.PPU * keep
        dx = int(round((j["pelvis"][0] - r["pelvis"][0]) * QL.PPU * lunge)) + shift[0]
        dy = int(round(QL.GROUND - lift - low)) + shift[1]
        rig = self.rig
        # the hem rests on the floor when she goes down on her knees (set down whole it hung through the floor)
        can = R.compose(rig, [(self.CAPE, dict(dx=dx + cape[0], dy=min(dy + cape[1], QL.GROUND - 1 - self.CAPE_LOW)))])
        QL.draw_legs(can, {k: (*(v + np.array((rig.ox + dx, rig.oy + dy)) for v in g[:3]), *g[3:])
                           for k, g in geo.items()}, self.P)
        body, ash = self.leant(lean) if lean else (self.BODY, 0)
        layers = [(body, dict(dx=dx, dy=dy))]
        if hold:
            S = np.array(SHOULDER) + (rig.ox + dx + ash, rig.oy + dy)
            W = S + hold["wrist"]
            self.draw_arm(can, S, S + hold["elbow"], W)
            layers.append((self.FIST, dict(dx=int(round(W[0] - rig.ox - WRIST[0])),
                                           dy=int(round(W[1] - rig.oy - WRIST[1])), rot=hold.get("rot", 0),
                                           about=WRIST)))
        elif not drop:
            layers.append((self.L["arm"], dict(dx=dx + ash + arm[0], dy=dy + arm[1], rot=arm_rot, about=SHOULDER)))
        up = R.compose(rig, layers)
        m = up[..., 3] > 0
        can[m] = up[m]
        return self.close_cracks(can)

    def close_cracks(self, can):
        """The ground seen through a thin crack the drawn legs leave against the cape, the skirt or each other (a slit
        between two boots that touch, a pocket under the hip) closed with the outline's dark - the idle has no enclosed
        gap at all (gap-check); a wider room between the limbs or the cape stays open."""
        op = can[..., 3] > 0
        lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
        out = can.copy()
        for k in range(1, n + 1):
            h = lbl == k
            if h.sum() <= CRACK and ndimage.distance_transform_edt(h).max() <= CRACK_W:
                out[h] = (*QL.INK, 255)
        return out

    def toe_height(self, j):
        """League's lower toe over its floor (game px, without the camera's pitch): a foot is down while its toe is,
        whatever its ankle does as it rolls from heel to toe (by the ankles seen through the pitch, six of the run's
        eight frames left the floor; League's has both feet up in two)."""
        f = QL.flat(j, self.PITCH, self.JS["unit"])
        return -max(f["l_toe"][1], f["r_toe"][1])

    def draw_arm(self, can, S, E, W):
        """Her far arm from the shoulder S to the elbow E and the wrist W (canvas squares): bands across the sleeve's
        squares in an outline ring (quinn_legs.band), drawn into can before the body - the body covers it."""
        cells = {}
        QL.band(cells, S, E, self.SLEEVE)
        QL.band(cells, E, W, self.SLEEVE)
        ring = {(x + ex, y + ey) for x, y in cells for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)
        for x, y in ring:
            can[y, x] = (*QL.INK, 255)
        for (x, y), c in cells.items():
            can[y, x] = c

    def bow(self, can, dx, dy, rot=0, about=(53.0, 23.0)):
        """The dropped crossbow (no hand) added behind the figure on can: moved (dx, dy) from where her hand held it,
        turned rot quarter turns counter-clockwise about `about` (design squares)."""
        b = R.compose(self.rig, [(self.BOW, dict(dx=dx, dy=dy, rot=rot, about=about))])
        m = (b[..., 3] > 0) & (can[..., 3] == 0)
        out = can.copy()
        out[m] = b[m]
        return out

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
    return Form(design(), rig_pad=(60, 80, 80, 30))


def tries(F):
    p = F.pose
    return [p(), p(arm_rot=1, arm=(5, -3)), p(crouch=2), p(whole=(-3, 0), arm=(0, -2)), F.whole("ride"),
            R.lie(F.rig, p(), 3, dx=3, sink=0), R.lie(F.rig, p(), 1, dx=-3, sink=0)]


# ------------------------------------------------------------------------------------------------- the actions
# the crossbow raised to the sky beside the head, never over the face: the arm drawn from the shoulder out to the elbow
# and up, the fist turned a quarter up at the wrist (the whole arm turned about the shoulder laid the bow's near prong
# across her eyes at PPU 2.0, and left a slit of ground between the sleeve and the cheek)
UP = dict(hold=dict(elbow=(5, -2), wrist=(11, -8), rot=1))
# the run as League's (the user, 2026-10-19, beside League's frames: 「明显动作不一样吧 你起码做到一样啊」 - League strides
# wide, leans forward): League's leg angles x RUN_SWING (her chibi legs are under a third of her height), the body leant
# one square every RUN_LEAN rows (the head about six squares ahead of the hips, league_zeri's approved run), the whole
# frame RUN_DX back so the hips stay over the standing point
RUN_SWING, RUN_LEAN, RUN_DX = 1.6, 3, -3
ACT_SPREAD = 1.2              # the standing moves' feet seen from the hips, widened a little (her legs are half League's)
RUN_SPREAD = 1.3              # League's feet seen from the hips, the direction widened (her legs are half League's)
# the crossbow arm bent as League's runs with it: the elbow down at her side behind her, the forearm forward at her
# stomach, the bow held out before her (squares from the shoulder; Form.drawn hold)
RUN_HOLD = dict(elbow=(-1.5, 7.0), wrist=(4.0, 6.0))
LOW_HOLD = dict(elbow=(-1.5, 7.5), wrist=(4.0, 14.0))   # let down to her hip (R's channel, League's 0.5 s)
# the death's crossbow: flung up behind her (moved, then a quarter turn up), then lying on the floor behind her
BOW_FLUNG = (-61, 12)
BOW_DX = -64
STAND_CAPE = (0, -3)          # the cape's hem in the standing moves (Form.drawn cape)
RUN_FLIGHT = 0.6              # share of League's lift kept in the run's both-feet-off-the-ground frames
RUN_CAPE = [(-3, -3), (-5, -8), (-8, -8), (-3, -5), (-3, -3), (-5, -8), (-8, -8), (-3, -5)]   # the hem flying back,
# up clear of the heel kicked up behind (lower, the two closed a pocket of ground between them)
# the hips close together as League's side-on run has them (league_zeri: the far hip 2 squares right of the near): at
# the idle's 3/4 places, 12 squares apart, the near leg swinging forward crossed the far one swinging back and the
# stride closed up instead of opening
RUN_HIPS = {"near": (19.5, 43.0), "far": (23.0, 43.5)}

# ms per frame; the kit's ticks (tools/kit/build_quinn.py) come from these
MS = {"idle": [150] * 8, "run": [117] * 8, "attack": [80, 70, 90, 110, 90],
      "skill": [90, 80, 100, 90, 110], "skill2": [60, 60], "e_flip": [50, 50, 50, 60, 90],
      "ult": [80, 100, 120, 200], "ult_ride": [100] * 4, "ult_land": [70, 70, 70, 70, 100, 100],
      "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500],
      "r_idle": [160] * 4, "r_run": [90] * 4, "r_hit": [100, 100]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    # every tag's legs from the side-on camera (assets/source/quinn/poses_side.json): the 3/4 camera foreshortened
    # League's steps forward and back, and her legs stand side by side in the drawing; standing moves map League's front
    # and back feet onto her image-right and image-left legs (roles), her own stance
    T = {t: [r["j"] for r in rows] for t, rows in F.JS["tags"].items()}
    # (the cape's hem held 3 rows up through the standing moves: down at the idle's row a back foot up on its toes
    # touched its tip and closed a pocket of ground between them)
    dr = lambda j, **o: F.drawn(j, **{"spread": ACT_SPREAD, "roles": True, "ground": True, "cape": STAND_CAPE, **o})
    out = {}
    # idle (League's Quinn_idle1: the crossbow held out, she breathes): the approved design, the body set down a game
    # pixel (two rows)
    out["idle"] = [p(), p(), p(), p(crouch=2), p(crouch=2), p(crouch=2), p(crouch=2), p()]
    # run (Quinn_run, 8 frames of its 0.93 s stride, seen nearly side-on): the legs on League's legs (widened for her
    # chibi legs), the body leant forward, the crossbow down at her hip, both feet off the ground where League's are,
    # the cape's hem flying back behind the legs
    S = [r["j"] for r in F.JS["tags"]["run"]]
    low = min(F.toe_height(j) for j in S)
    out["run"] = [F.drawn(j, ref=S[0], spread=RUN_SPREAD, lean=RUN_LEAN, shift=(RUN_DX, 0), hips=RUN_HIPS,
                          hold=RUN_HOLD, flight=(low, RUN_FLIGHT), cape=c) for j, c in zip(S, RUN_CAPE)]
    # auto attack (Quinn_attack1: into League's wide crouched stance, the shot kicking the crossbow up, settling)
    kick = [(0, 0), (0, 0), (0, -3), (0, -2), (0, 0)]
    out["attack"] = [dr(j, arm=k, lunge=0.7) for j, k in zip(T["attack"], kick)]
    # Q Blinding Assault (quinn_spell1: up on her toes with the crossbow raised to the sky as Valor leaves, then the
    # lunge after him, leant forward)
    out["skill"] = [dr(T["skill"][0], lunge=0.7, air=True, **UP)] + [dr(j, lunge=0.7, lean=k) for j, k in
                                                         zip(T["skill"][1:], (4, 3, 3, 4))]
    # E Vault (Quinn_spell3_dash: flying at the target leant far forward, the legs trailing, the cape flying back)
    out["skill2"] = [dr(j, air=True, lunge=0.5, lean=1.5, cape=(-3, -3)) for j in T["skill2"]]
    # Quinn_spell3_flip: she kicks off and somersaults back (the kick-off frame turned whole a quarter at a time,
    # counter-clockwise), lands (League's landing frame), stands
    kick_off = dr(T["e_flip"][0])
    tumble = lambda k, dx, up: shift(R.lie(rig, kick_off, k, dx=dx, sink=0), 0, -up)
    out["e_flip"] = [tumble(1, 0, 12), tumble(2, -2, 21), tumble(3, -3, 14), dr(T["e_flip"][4], shift=(-3, 0)), p()]
    # R Behind Enemy Lines (Quinn_Spell4_Channel: aimed, the crossbow let down to her hip, standing tall aiming again,
    # down on one knee with the crossbow raised as Valor comes down; she is on his back from ult_ride on)
    out["ult"] = [dr(T["ult"][0]), dr(T["ult"][1], hold=LOW_HOLD), dr(T["ult"][2], air=True), dr(T["ult"][3], **UP)]
    # the ride (quinnvalor_run_glide): gliding, the whole group rising and falling
    out["ult_ride"] = [F.whole("ride", dy=-d) for d in (6, 8, 9, 8)]
    # Skystrike (QuinnRFinale: the two loop up through the air and she drops onto them): the group whole quarter turns
    # counter-clockwise (nose up, over, down), she lands (the somersault's landing, the channel's crouch), stands
    loop = lambda k, dx, up: shift(R.lie(rig, F.whole("ride"), k, dx=dx, sink=0), 0, -up)
    out["ult_land"] = [loop(1, 2, 9), loop(2, 0, 18), loop(3, -2, 9), dr(T["e_flip"][4]), dr(T["ult"][1]), p()]
    # hit (League's idle leaning toward its death): flashed, knocked back
    out["hit"] = [R.flash(dr(T["hit"][0], shift=(-3, 0))), dr(T["hit"][1], shift=(-2, 0))]

    # the death (quinn_death, League's 0 / 0.4 / 0.8 / 1.2 / 2.3 / 2.6 / 2.8 / 3.15 s): hit as she aims, she doubles
    # over as the crossbow flies from her hand behind her, her knees give, she drops onto one knee, slumps, falls face
    # down, head forward (a standing frame without the bow a quarter turn clockwise), bounces once, lies; the crossbow
    # lies on the floor behind her from the third frame on
    D = T["dead"]
    on_floor = lambda can: F.bow(can, BOW_DX, (QL.GROUND - 1) - F.BOW_LOW)

    def lying(sink):                     # her own straight legs side by side (drawn apart they lay one up, one down)
        return R.lie(rig, p(crouch=5, no_arm=True), 3, dx=12, sink=sink)
    out["dead"] = [dr(D[0]), F.bow(dr(D[1], drop=True, lean=2), *BOW_FLUNG, rot=1),
                   on_floor(dr(D[2], drop=True, lean=2)), on_floor(dr(D[3], drop=True, lean=2)),
                   on_floor(dr(D[4], drop=True, lean=2)), on_floor(lying(0)), on_floor(lying(-3)), on_floor(lying(0))]
    # the add-on's ride form (addons/league_quinn): standing / moving / hit as the group gliding
    out["r_idle"] = [F.whole("ride", dy=-d) for d in (6, 8, 8, 6)]
    out["r_run"] = [F.whole("ride", dy=-d, dx=x) for d, x in ((6, 0), (9, 2), (8, 0), (5, -2))]
    out["r_hit"] = [F.whole("ride", dx=-3, dy=-6, flash=True), F.whole("ride", dx=-2, dy=-6)]
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
