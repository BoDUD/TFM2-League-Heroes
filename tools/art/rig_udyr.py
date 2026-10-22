#!/usr/bin/env python3
"""league_udyr's action frames, posed by hand on the four approved 3/4 designs after League's own clips, frame by frame
(the user, 2026-10-22: 「每个用到的姿态一套」「只做四分之三侧面」「动作帧做到完美后再喊我review」).

    python tools/art/rig_udyr.py --parts DIR       # each design with its parts tinted (12x)
    python tools/art/rig_udyr.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_udyr.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_udyr.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/review_udyr_actions.py --out DIR   # League left / ours right, one GIF

The designs (tools/art/design_udyr_model.py, the user's picks A-1 / Q-1 / E-1 / R-1, one palette, PPU 1.5):
  hd/idle.png    his plain guard (League's spell2_idle, the Boar's stance - W is folded into the passive): idle, run,
                 attack, hit, dead.
  hd/q_idle.png  the Bear (Q Wilding Claw): q_idle, q_run, q_attack, q_hit, q_dead and skill (the Q cast).
  hd/e_idle.png  the Ram (E Blazing Stampede): e_idle, e_run (also the charge), e_attack, e_stun (the stunning blow),
                 e_hit, e_dead and skill2 (the E cast).
  hd/r_idle.png  the Phoenix (R Wingborne Storm): r_idle, r_run, r_attack, r_hit, r_dead and ult (the R cast).
The kit plays the stance's attack itself (CasterAnimation); the add-on league_udyr swaps idle / run / hit / dead (and
attack) to the stance's own tags while its flag holds (league_gnar's m_* way).
Every stance stands on one canvas: its standing point is the middle of the belt's stone plaque (the body's own middle),
so a stance swap keeps the body where it was.
Lossless (memory rig-deformation-checks): parts cut square by square from the design and moved by whole squares, the
arms also turned by quarter turns about a joint; the head is never cut from the body, sheared or turned; the legs are
the design's own (league_braum's walk: one lifted per frame by losing its top rows and stepped forward, the body
floating a little - memory run-legs-caitlyn-way for big heroes).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "udyr"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "udyr", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def poly(pts, shape):
    """Squares whose centres lie inside the polygon (design square edges)."""
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    return np.asarray(img, bool)


def dark_of(d):
    rgb = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (rgb.sum(-1) < 90)


def hair_of(d):
    """His dark brown dreadlocks and beard (and the outline): brown-black, red over blue."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (r < 110) & (g < 80) & (b < 70) & (r >= b)


# ------------------------------------------------------------------------------------------------- lossless moves
def turned(layer, k, about):
    """A padded layer turned k quarter turns counter-clockwise on screen about `about` (design square edges): every
    square kept, none stretched (rig_warwick.turned)."""
    if not k % 4:
        return layer
    out = np.zeros_like(layer)
    ys, xs = np.nonzero(layer[..., 3] > 0)
    ax, ay = about[0] + P, about[1] + P
    ox, oy = xs + 0.5 - ax, ys + 0.5 - ay
    for _ in range(k % 4):
        ox, oy = oy, -ox
    tx = np.floor(ax + ox).astype(int)
    ty = np.floor(ay + oy).astype(int)
    ok = (tx >= 0) & (tx < out.shape[1]) & (ty >= 0) & (ty < out.shape[0])
    out[ty[ok], tx[ok]] = layer[ys[ok], xs[ok]]
    return out


def lifted(layer, lift):
    """A leg layer lifted `lift` rows by losing its top rows (the thigh turned toward us): league_braum's walk."""
    if not lift:
        return layer
    out = layer.copy()
    ys = np.nonzero(layer[..., 3].any(1))[0]
    out[:ys.min() + lift] = 0
    return np.roll(out, -lift, axis=0)


def close_cracks(can, outline, keep=None, most=14, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across (a crack
    between a moved part and the one beside it) take the outline (gap-check); `keep`: the standing frame's own holes,
    left open."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        if keep is not None and (h & keep).any():
            continue
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


def shifted(m, d):
    dy, dx = d
    return np.roll(np.roll(m, dy, 0), dx, 1)


def best_shift(op, ref, r=10):
    """The whole-square move of `ref` that overlaps `op` most (a frame's whole-figure move against its idle)."""
    best, bd = -1, (0, 0)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            k = int((shifted(ref, (dy, dx)) & op).sum())
            if k > best:
                best, bd = k, (dy, dx)
    return bd


# ------------------------------------------------------------------------------------------------- one stance
class Stance:
    """A design cut into its parts and posed: pose() -> canvas on the shared rig."""

    def __init__(self, prefix, D, joints, band, legs, order):
        self.prefix, self.D = prefix, D
        self.J = joints               # name -> (x, y) design square edges: shoulders, elbows
        self.band = band              # the design's last row of the body: the legs start under it
        self.legs = legs              # (near leg columns (x0, x1), far leg columns): the legs that step
        self.order = order            # back-to-front draw order of the upper parts ("body" among them)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.rig = None
        self.holes = None
        self.orphans = None

    def pose(self, whole=(0, 0), upper=(0, 0), arms=None, legs=None, layers=None, lift=0, kneel=None):
        """whole: the figure (dx, dy); upper: the body and arms over the legs (dx, dy); arms: {part: (dx, dy, k, about)}
        each arm moved (dx, dy) on the body after k quarter turns about `about` (a joint name or a point); legs:
        {"near" | "far": (dx, dy, lift)} a leg moved after losing `lift` top rows (league_braum's walk); layers:
        another back-to-front order of the upper parts; lift: rows the whole figure is off the ground (a hop); kneel:
        the legs' last row kept (the knee guards' bottom) - the shins folded away under him and the figure set down
        onto its knees (League's death kneels)."""
        arms, legs = arms or {}, legs or {}
        wx, wy = whole[0], whole[1] - lift
        if kneel is not None:
            wy += self.D.ground - 1 - kneel
        ux, uy = wx + upper[0], wy + upper[1]
        out = []
        for side in ("far", "near"):
            name = side + "_leg"
            if name not in self.L:
                continue
            dx, dy, lf = legs.get(side, (0, 0, 0))
            leg = lifted(self.L[name], lf)
            if kneel is not None:
                leg = leg.copy()
                leg[P + kneel + 1:] = 0
            out.append((leg, dict(dx=wx + dx, dy=wy + dy)))
        for name in (layers or self.order):
            img = self.L[name]
            dx, dy = ux, uy
            if name in arms:
                ax, ay, k, about = arms[name]
                if k:
                    img = turned(img, k, self.J[about] if isinstance(about, str) else about)
                dx, dy = ux + ax, uy + ay
            out.append((img, dict(dx=dx, dy=dy)))
        can = R.compose(self.rig, out)
        can[self.rig.GY:] = 0
        can = close_cracks(can, self.D.outline, keep=shifted(self.holes, (wy, wx)) if self.holes is not None else None)
        return self.patch(can, (wy, wx))

    def patch(self, can, d):
        """Enclosed gaps a part's move opened that the standing frame (moved as the whole figure is) does not have:
        the body behind the part, filled from the squares round it (ppu_rig.fill_under)."""
        op = can[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op
        if self.holes is not None:
            holes &= ~ndimage.binary_dilation(shifted(self.holes, d), iterations=2)
        if holes.any():
            can = R.fill_under(can, holes)
        return self.unorphan(can, d)

    def unorphan(self, can, d):
        """Outline squares a move left with no colour beside them (a part's edge left behind on the body) that the
        standing frame does not have, where they touch the ground round the figure: taken off (finish() closes the
        outline again)."""
        op = can[..., 3] > 0
        dk = op & (np.abs(can[..., :3].astype(int) - np.array(self.D.outline)).sum(-1) < 30)
        orphan = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
        if self.orphans is not None:
            orphan &= ~shifted(self.orphans, d)
        clear = ndimage.convolve((~op).astype(int), np.ones((3, 3), int), mode="constant", cval=1)
        orphan &= clear >= 5                       # sticking out into the ground: a line left behind, not an edge
        out = can.copy()
        out[orphan] = 0
        return out

    def walk(self, step, arm_swing=None, ms=None):
        """league_braum's walk: WALK's legs, the figure rising, the arms swinging a square against the legs."""
        out = []
        for i, (n, f, r, sw) in enumerate(WALK):
            arms = {}
            for name, (ax, k, about) in (arm_swing or {}).items():
                arms[name] = (ax * sw, 0, k, about)
            out.append(self.pose(whole=(0, -r), legs={"near": (n[0] * step, 0, n[1]), "far": (f[0] * step, 0, f[1])},
                                 arms=arms))
        return out


# the walk (league_braum / league_warwick at PPU 1.5): per frame the near leg's (forward, lifted), the far leg's, the
# figure's rise, the arms' swing (+1: the near arm forward)
WALK = [((0, 0), (0, 2), 1, 1), ((0, 0), (1, 5), 2, 1), ((0, 0), (1, 2), 1, 0), ((0, 0), (1, 0), 0, 0),
        ((0, 2), (0, 0), 1, -1), ((1, 5), (0, 0), 2, -1), ((1, 2), (0, 0), 1, 0), ((1, 0), (0, 0), 0, 0)]


# ------------------------------------------------------------------------------------------------- the plain guard
def plain():
    """hd/idle.png (50 x 60): both bandaged fists raised beside the face, each arm folded at an elbow under the fist.
    Parts: the far forearm (the fist right of the hair and the orange bracer under it down to the elbow, (43, 25)), the
    far upper arm (the skin left of the bracer, from the shoulder down to the elbow), the near forearm (the fist left of
    the hair and the forearm down to the elbow at (5, 16)), the near upper arm (the big tattooed block out to the left),
    the legs under the trousers' top (row 35) split round the two orange ropes (columns 20-31 stay with the body); the
    rest is the body (head, torso, belt, ropes)."""
    d = load("idle.png")
    D = CutDesign(d, px=26)
    hair = hair_of(d) & poly([(0, 0), (37.5, 0), (37.5, 30), (0, 30)], d.shape) & ~poly(
        [(0, 0), (16.5, 0), (16.5, 30), (0, 30)], d.shape)
    op = d[..., 3] > 0
    far = poly([(35.5, 1.5), (47.5, 1.5), (49.5, 11), (49.5, 27.5), (36.5, 27.5), (36.5, 12.5), (35.5, 10.5)],
               d.shape) & op & ~hair
    far_fore = far & (poly([(35.5, 1.5), (47.5, 1.5), (49.5, 11), (49.5, 24.5), (46.5, 25.5), (43.5, 25.5),
                            (40.5, 13.5), (40.5, 11.5), (35.5, 11.5)], d.shape))
    near = poly([(8.5, 1.5), (18.5, 1.5), (18.5, 14.5), (12.5, 15.5), (12.5, 26.5), (0, 26.5), (0, 12.5)], d.shape)
    near &= op & ~hair
    near_fore = near & poly([(8.5, 1.5), (18.5, 1.5), (18.5, 14.5), (11.5, 15.5), (3.5, 15.5), (3.5, 8.5)], d.shape)
    D.part("far_fist", far_fore & poly([(0, 0), (50, 0), (50, 10.5), (0, 10.5)], d.shape))
    D.part("far_fore", far_fore & ~poly([(0, 0), (50, 0), (50, 10.5), (0, 10.5)], d.shape))
    D.part("far_upper", far & ~far_fore)
    D.part("near_fore", near_fore)
    D.part("near_upper", near & ~near_fore)
    D.part("near_leg", D.box(36, 60, 0, 19))
    D.part("far_leg", D.box(36, 60, 32, 49))
    D.part("body", D.rest())
    S = Stance("", D, {"far_elbow": (43.0, 25.0), "far_shoulder": (38.0, 15.0), "near_elbow": (5.0, 16.0),
                       "near_shoulder": (12.0, 18.0)},
               band=35, legs=((0, 19), (32, 49)),
               order=["far_upper", "far_fore", "far_fist", "body", "near_upper", "near_fore"])
    return S


def bear():
    """hd/q_idle.png (65 x 61): hunched like a bear, the hide over his back, the bear's head over the far fist. Parts:
    the far paw (the bear's head and the bandaged paw with its claws, right of the hide's edge), the near paw (the
    bandaged hand and its claws hanging under the hide on the left), the legs under the belt; the rest is the body."""
    d = load("q_idle.png")
    D = CutDesign(d, px=30)
    op = d[..., 3] > 0
    far = poly([(48.5, 8.5), (53.5, 8.5), (65, 22), (65, 51), (49.5, 51), (49.5, 31.5), (47.5, 17.5)], d.shape) & op
    far &= ~(hair_of(d) & poly([(0, 0), (49.5, 0), (49.5, 30), (0, 30)], d.shape))
    near = poly([(0, 30.5), (13.5, 30.5), (14.5, 37.5), (12.5, 45.5), (0, 45.5)], d.shape) & op
    D.part("far_paw", far)
    D.part("near_paw", near)
    D.part("near_leg", D.box(41, 61, 0, 24))
    D.part("far_leg", D.box(42, 61, 33, 64) & ~far)
    D.part("body", D.rest())
    return Stance("q_", D, {"far_shoulder": (50.0, 20.0), "near_shoulder": (12.0, 30.0)}, band=40,
                  legs=((0, 24), (33, 64)), order=["body", "far_paw", "near_paw"])


def ram():
    """hd/e_idle.png (64 x 69): head down under the two great horns, ready to charge. Parts: the near fist (the bandaged
    fist under the near horn), the far arm (the orange bracer and the bandaged fist on the right), the legs under the
    belt; the rest is the body (the head, the horns, the shoulders)."""
    d = load("e_idle.png")
    D = CutDesign(d, px=38)
    op = d[..., 3] > 0
    near = poly([(18.5, 29.5), (30.5, 29.5), (31.5, 41.5), (18.5, 41.5)], d.shape) & op
    far = poly([(47.5, 32.5), (58.5, 32.5), (64, 37), (64, 52), (52.5, 52), (47.5, 45.5)], d.shape) & op
    D.part("near_fist", near)
    D.part("far_arm", far)
    D.part("near_leg", D.box(44, 69, 0, 30))
    D.part("far_leg", D.box(45, 69, 43, 63) & ~far)
    D.part("body", D.rest())
    return Stance("e_", D, {"far_elbow": (50.0, 38.0), "near_elbow": (22.0, 33.0)}, band=43,
                  legs=((0, 30), (43, 63)), order=["far_arm", "body", "near_fist"])


def phoenix():
    """hd/r_idle.png (89 x 73): both arms spread like wings, rows of feather blades along them, the hair swept up.
    Parts: the near arm (the open hand, the bracer, the forearm and the feather blades on it, left of the shoulder at
    (28, 30)), the far arm (the hand, the bracer, the forearm and its blades right of the face), the legs under the
    belt; the rest is the body (the head and hair, the back's blades, the torso)."""
    d = load("r_idle.png")
    D = CutDesign(d, px=52)
    op = d[..., 3] > 0
    hair = hair_of(d)
    near = poly([(0, 20), (9.5, 18.5), (15.5, 11.5), (26.5, 11.5), (28.5, 26.5), (28.5, 39.5), (17.5, 41.5),
                 (0, 41.5)], d.shape) & op
    far = poly([(69.5, 19.5), (71.5, 10.5), (89.5, 12.5), (89.5, 27.5), (79.5, 28.5), (74.5, 32.5), (69.5, 32.5)],
               d.shape) & op & ~(hair & poly([(0, 0), (74.5, 0), (74.5, 40), (0, 40)], d.shape))
    D.part("near_arm", near)
    D.part("far_arm", far)
    D.part("near_leg", D.box(49, 73, 0, 46))
    D.part("far_leg", D.box(49, 73, 59, 88))
    D.part("body", D.rest())
    return Stance("r_", D, {"near_shoulder": (28.0, 31.0), "far_shoulder": (70.0, 29.0)}, band=48,
                  legs=((0, 46), (59, 88)), order=["far_arm", "body", "near_arm"])


STANCES = {"": plain, "q_": bear, "e_": ram, "r_": phoenix}
TINT = {"far_fore": (255, 220, 0), "far_upper": (255, 160, 60), "near_fore": (0, 255, 120),
        "near_upper": (0, 160, 255), "far_paw": (255, 220, 0), "near_paw": (0, 255, 120), "near_fist": (0, 255, 120),
        "far_arm": (255, 220, 0), "near_arm": (0, 255, 120), "near_leg": (255, 0, 255), "far_leg": (255, 120, 0),
        "head": (60, 200, 255), "hide": (60, 200, 255), "horns": (60, 200, 255), "wings": (60, 200, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        if name not in D.parts:
            continue
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def stances():
    """Every stance on one shared canvas: each design's standing point (the plaque's middle) and ground on the same
    canvas square."""
    S = {k: f() for k, f in STANCES.items()}
    left = max(s.D.px for s in S.values()) + 70
    right = max(s.D.W - s.D.px for s in S.values()) + 70
    top = max(s.D.ground for s in S.values()) + 70
    for s in S.values():
        s.rig = R.Rig(s.D, pad=(left - s.D.px, right - (s.D.W - s.D.px), top - s.D.ground, 24))
        s.rig.fill_rows = None
        idle = R.compose(s.rig, [(s.L[k], {}) for k in ([n for n in ("far_leg", "near_leg") if n in s.L] + s.order)])
        op = idle[..., 3] > 0
        s.holes = ndimage.binary_fill_holes(op) & ~op
        dk = op & (np.abs(idle[..., :3].astype(int) - np.array(s.D.outline)).sum(-1) < 30)
        s.orphans = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
        s.rig.idle_canvas = idle
    return S


# ------------------------------------------------------------------------------------------------- the actions
# Codex's poses (tools/art/design_udyr_poses.py -> hd/pose_<name>.png + .json, the user's pick 2026-10-22: 「Codex 照骨架画
# 姿势」 after the part-moved rig looked deformed): each placed so its head box (the design's head, pasted) stands where the
# stance design's head stands - the body under it as Codex drew it - dx squares forward in a lunge, its lowest square on
# the ground (or `lift` rows over it). The deaths are the plain poses in every stance (the spirit leaves him as he falls),
# placed on the plain design's head; each stance's own flash comes first.
POSE_STANCE = {"a_punch": "", "run1": "", "run2": "", "run3": "", "run4": "", "d_hit": "", "d_kneel": "",
               "q_wind": "q_", "q_swipe": "q_", "q_roar": "q_", "q_run1": "q_", "q_run2": "q_", "q_run3": "q_",
               "q_run4": "q_", "e_hook": "e_", "e_leap": "e_", "e_slam": "e_", "e_stomp": "e_", "e_run1": "e_",
               "e_run2": "e_", "e_run3": "e_", "e_run4": "e_", "r_thrust": "r_", "r_crouch": "r_", "r_flap": "r_",
               "r_run1": "r_", "r_run2": "r_", "r_run3": "r_", "r_run4": "r_"}
HEAD_AT = {"": (16, 0), "q_": (32, 9), "e_": (37, 17), "r_": (54, 21)}   # each design's head box top-left (column, row)


def load_pose(name):
    import json
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    return d, tuple(meta["head_at"])


# the poses whose head Codex drew tipped (design_udyr_poses.TILTED: its head kept, no head box to align): placed by
# their feet instead - the middle of the lowest FEET_ROWS rows' extent on the design's
FEET_ROWS = 6
TIPPED = {"d_hit", "d_kneel", "e_hook", "e_leap", "r_thrust", "r_flap"}


def feet_mid(d):
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    xs = np.nonzero((d[ys.max() - FEET_ROWS + 1:ys.max() + 1, :, 3] > 0).any(0))[0]
    return (xs.min() + xs.max() + 1) / 2


def place(S, name, dx=0, lift=0, flash=False):
    """Pose `name` on stance S's canvas: its head box on the design's head box (a tipped head: its feet's middle on the
    design's), moved dx squares, its lowest square on the ground row (lift rows over it)."""
    st = S[POSE_STANCE[name]]
    rig = st.rig
    d, (hx, hy) = load_pose(name)
    cx, cy = HEAD_AT[POSE_STANCE[name]]
    can = rig.canvas()
    if name in TIPPED:
        left = rig.ox + int(round(feet_mid(st.D.d) - feet_mid(d))) + dx
    else:
        left = rig.ox + cx - hx + dx
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    top = rig.GY - (ys.max() + 1) - lift
    y0, x0 = max(0, top), max(0, left)
    y1, x1 = min(rig.CH, top + d.shape[0]), min(rig.CW, left + d.shape[1])
    can[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
    can[rig.GY:] = 0
    return R.flash(can) if flash else can


def design_frame(S, x, dx=0, lift=0, flash=False):
    can = S[x].pose(whole=(dx, 0), lift=lift)
    return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_udyr.py) come from these (a frame's start in ticks = ms x 0.06):
# attacks 30 ticks with the blow on frame 2 (a_hit 9 ticks = 150 ms falls in it), the Q cast 12 ticks, the E cast 10, the
# stunning blow 24 (its slam frame from 135 ms: e_hit 8), the R cast 24 (the storm's first pulse at 10 = 167 ms, frame 3)
MS = {"idle": [400, 400], "run": [150] * 4, "attack": [70, 150, 140, 140], "hit": [100, 100],
      "dead": [100, 180, 260, 700],
      "q_idle": [400, 400], "q_run": [140] * 4, "q_attack": [70, 150, 140, 140], "skill": [70, 80, 50],
      "q_hit": [100, 100], "q_dead": [100, 180, 260, 700],
      "e_idle": [400, 400], "e_run": [110] * 4, "e_attack": [70, 150, 140, 140], "e_stun": [60, 75, 130, 85, 50],
      "skill2": [90, 77], "e_hit": [100, 100], "e_dead": [100, 180, 260, 700],
      "r_idle": [400, 400], "r_run": [150] * 4, "r_attack": [70, 150, 140, 140], "ult": [80, 80, 90, 80, 70],
      "r_hit": [100, 100], "r_dead": [100, 180, 260, 700]}


def frames_all(S):
    out = {}
    for x, stance_name in (("", "plain"), ("q_", "bear"), ("e_", "ram"), ("r_", "phoenix")):
        out[x + "idle"] = [design_frame(S, x), design_frame(S, x)]
        out[x + "hit"] = [design_frame(S, x, dx=-2, flash=True), design_frame(S, x, dx=-1)]
        out[x + "dead"] = [design_frame(S, x, dx=-1, flash=True), place(S, "d_hit", dx=-2), place(S, "d_kneel", dx=-2),
                           place(S, "d_kneel", dx=-2)]
    # runs (League's Spell2_run / Spell1_Run / Spell3_Run / Spell4_run): the four key poses, each stance's own
    out["run"] = [place(S, n) for n in ("run1", "run2", "run3", "run4")]
    out["q_run"] = [place(S, n) for n in ("q_run1", "q_run2", "q_run3", "q_run4")]
    out["e_run"] = [place(S, n, dx=1) for n in ("e_run1", "e_run2", "e_run3", "e_run4")]
    out["r_run"] = [place(S, n) for n in ("r_run1", "r_run2", "r_run3", "r_run4")]
    # the attacks: the guard, the blow (a lunge forward), held, back to the guard
    out["attack"] = [design_frame(S, ""), place(S, "a_punch", dx=2), place(S, "a_punch", dx=2), design_frame(S, "")]
    out["q_attack"] = [place(S, "q_wind", dx=-1), place(S, "q_swipe", dx=2), place(S, "q_swipe", dx=2),
                       design_frame(S, "q_")]
    out["e_attack"] = [design_frame(S, "e_"), place(S, "e_hook", dx=2), place(S, "e_hook", dx=2), design_frame(S, "e_")]
    out["r_attack"] = [design_frame(S, "r_"), place(S, "r_thrust", dx=2), place(S, "r_thrust", dx=2),
                       design_frame(S, "r_")]
    # the casts: the bear's roar (League's Spell1_activate), the ram's stamp (Spell3), the stunning leap and slam
    # (Spell3_enhanced_attack), the phoenix taking wing (Spell4)
    out["skill"] = [place(S, "q_roar"), place(S, "q_roar"), design_frame(S, "q_")]
    out["skill2"] = [place(S, "e_stomp"), design_frame(S, "e_")]
    out["e_stun"] = [place(S, "e_leap", lift=4), place(S, "e_leap", dx=1, lift=8), place(S, "e_slam", dx=3),
                     place(S, "e_slam", dx=3), design_frame(S, "e_", dx=1)]
    out["ult"] = [place(S, "r_crouch"), place(S, "r_flap", lift=4), place(S, "r_flap", lift=8), place(S, "r_flap", lift=4),
                  design_frame(S, "r_")]
    return out


def frames(S):
    a = frames_all(S)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = [(c, m) for c, m in zip(cans, ms)]
    return out


STANCE_OF = {"skill": "q_", "skill2": "e_", "e_stun": "e_", "ult": "r_"}


def stance_of(tag):
    if tag in STANCE_OF:
        return STANCE_OF[tag]
    for x in ("q_", "e_", "r_"):
        if tag.startswith(x):
            return x
    return ""


def audit(S, acts, out_dir, only=None):
    """Every frame after the rig's finish(), against its own stance's idle: its pieces (8-connected), new enclosed
    holes, colours in no design (a hit's flash aside), outline squares with no colour beside them; each tag at 6x."""
    os.makedirs(lp(out_dir), exist_ok=True)
    bad = 0
    ref = {}
    for x, st in S.items():
        idle = st.rig.finish(acts[x + "idle"][0][0])
        iop = idle[..., 3] > 0
        idark = iop & (np.abs(idle[..., :3].astype(int) - np.array(st.D.outline)).sum(-1) < 30)
        ref[x] = dict(op=iop, allowed={tuple(c) for c in st.D.d[st.D.d[..., 3] > 0][:, :3].tolist()} | {tuple(st.D.outline)},
                      holes=ndimage.binary_fill_holes(iop) & ~iop,
                      orphan=int((idark & ~ndimage.binary_dilation(iop & ~idark, structure=R.CROSS)).sum()))
    for tag, fr in acts.items():
        if only and tag not in only:
            continue
        x = stance_of(tag)
        st, rf = S[x], ref[x]
        tiles = []
        for i, (c, _) in enumerate(fr):
            f = st.rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(shifted(rf["holes"], best_shift(op, rf["op"])), iterations=3)
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - rf["allowed"]
            dk = op & (np.abs(f[..., :3].astype(int) - np.array(st.D.outline)).sum(-1) < 30)
            orphan = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
            flag = len(sz) > 1 or new.sum() or (odd and "hit" not in tag and not (tag.endswith("dead") and i == 0))                 or orphan.sum() > rf["orphan"] + 4
            bad += bool(flag)
            print(f"{tag:10s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}/{rf['orphan']}{'  <--' if flag else ''}")
            show = f.copy()
            if n > 1:
                big = 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
                show[(lbl > 0) & (lbl != big)] = (255, 0, 0, 255)
            show[new] = (255, 0, 255, 255)
            tiles.append(show)
        allc = np.stack(tiles)
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        z = 6
        sheet_ = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 8), (y1 - y0) * z + 16), (40, 40, 40))
        dr = ImageDraw.Draw(sheet_)
        for i, t in enumerate(tiles):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
            sheet_.paste(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST),
                         (i * ((x1 - x0) * z + 8), 16))
            dr.text((i * ((x1 - x0) * z + 8) + 2, 2), str(i + 1), fill=(255, 255, 0))
        sheet_.save(lp(os.path.join(out_dir, f"{HERO}_{tag}_6x.png")))
    print("frames flagged:", bad)


def zoom(S, acts, spec, out_dir):
    """TAG:i (1-based) at 12x with its squares' grid and canvas coordinates relative to the standing point."""
    tag, i = spec.split(":")
    st = S[stance_of(tag)]
    f = st.rig.finish(acts[tag][int(i) - 1][0])
    ys, xs = np.nonzero(f[..., 3] > 0)
    R.zoom_crop(f, os.path.join(out_dir, f"z_{tag}_{i}.png"), (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3),
                z=12, origin=(st.rig.CX, st.rig.GY))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    ap.add_argument("--tags", help="only these tags (comma separated) for --audit")
    ap.add_argument("--zoom", help="TAG:i[,TAG:i] at 12x into --audit's folder")
    a = ap.parse_args()
    S = stances()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        for k, s in S.items():
            tinted(s.D).save(os.path.join(a.parts, f"{HERO}_{k or 'plain_'}parts.png"))
            print(k or "plain", {n: int(v.sum()) for n, v in s.D.parts.items()}, "stand", s.D.px, "ground", s.D.ground)
        return
    acts = frames(S)
    rig = S[""].rig
    if a.review:
        # the bear's claw streaks and the ram's charge with its fire trail (assets/source/native/udyr_bake.json, the
        # pictures in league_udyr_fx: import_udyr_fx.py first) drawn into his frames: they turn with him
        rig.review(rig.bake(acts), a.review)
        return
    if a.zoom:
        os.makedirs(a.audit or ".", exist_ok=True)
        for spec in a.zoom.split(","):
            zoom(S, acts, spec, a.audit or ".")
    elif a.audit:
        audit(S, acts, a.audit, a.tags.split(",") if a.tags else None)
    else:
        rig.export(rig.bake(acts))


if __name__ == "__main__":
    main()
