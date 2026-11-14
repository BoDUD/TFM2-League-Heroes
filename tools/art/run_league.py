#!/usr/bin/env python3
"""League's run as the motion of our own art: a hero's run cycle rebuilt from its design, posed frame by frame on
League's run clip (the user, 2026-11-15, on the oppi mod's hand-drawn runs: 「怎么样做到走路时也和oppi模组也这样自然的动的
你想想办法」「用aseprite手绘的是吗 我们不能做到像手绘那样流畅？」「你要承认动画的差距 然后追赶上去 想个办法」).

    python tools/art/run_league.py motion --hero jinx [--lol D:\\WeGameApps\\lol]   # League's clip -> hd/<hero>_run_motion.json
    python tools/art/run_league.py parts --hero vi --review DIR                    # the part map over the design
    python tools/art/run_league.py build --hero jinx --review DIR [--legs]         # the frames at 4x + a GIF, nothing written
    python tools/art/run_league.py build --hero jinx                               # the run tags into the sheet (+ strips)
    python tools/art/jinx_excited_run.py                                           # (league_jinx: run_x is made from run)
    python -I tools/art/thin_outline.py --hero jinx                                # then the outline pass, as after any redraw

The motion (`motion`): the clip `Run` plays at base move speed (tools/lol/anim_graph.py), sampled SAMPLES times over
one stride cycle on the chibi model (the hero's poses.json proportions), seen from the side: every joint of the
hero's table as (forward, up, across) game px, up from League's floor. Numbers only (no render): committed beside
the design, so `build` runs without the client.

The build (`build`): N frames of one cycle, every frame the hero's design cut into parts and posed - no square
drawn anew but the thighs (the design's own rows laid along the bone) and RotSprite's turns (`turned`: Scale2x three
times, turned, each square the commonest colour of its block - only the part's own colours - the outline tidied):
- timing: the cycle is as long as it takes the unit (move_speed / 1000 game px a tick, 60 ticks a second) to cover
  CYCLE_HEIGHTS of its own height, the frames even (oppi's runs: 6-9 frames of 75-100 ms; ours were 105-143 ms);
- the legs: League's sole path relative to its hip (forward x the stride, which makes the planted foot go back as
  fast as the ground goes by - it slid by up to 1.9 body heights a cycle -, up as League; both x our leg length /
  League's), the knee by two-bone IK, the shin and boot the design's own turned with the shin (lifted where a turned
  heel or toe would go under the ground);
- the body: League's pelvis bob and sway by whole squares; the upper body leant from the hips by whole rows, the lean
  swinging with League's spine;
- the upper body from League's joints, part by part (the user, 2026-11-15, on the first draft that only bobbed:
  「有问题的地方你都说了还是僵硬」): the head bobbing less than the hips and nodding with League's head on its neck;
  arms, gauntlets, a staff turned about their shoulder / hand with League's arm / staff (a gun a frame behind the body
  and tilting with League's, the arms holding it turned to keep hold); braids bent through League's hair chain (its
  middle and tip), a hat's tip turned with League's hat chain, hair and a robe's hem trailing the body by a beat, a
  prop on the back one beat late, a familiar (Pix) floating on his own.
The dense frames are all one size, centred on the pivot as the hero's other frames (hd_idle_base), the outline grown
to the hero's KEEP (thin_outline.json) as its other frames have it; the 1x frames come from them the way
tools/art/ppu_one.py makes them, the lo_ frames the way tools/art/ppu_hd.py does. The sheet keeps every other tag's
frames where they are (the run's old squares are cleared, the new frames put in the free room).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

G = R.G
SAMPLES = 48
N_FRAMES = 8
CYCLE_HEIGHTS = 0.85    # body heights of ground a cycle covers (oppi's measured 0.9-1.2; ours were 1.05-1.9)
TICKS = 60              # game ticks a second
DARK = 26               # luminance under which a square is outline (inbetween.DARK)

# hero -> League's clip and the joints the build reads. cycle: one stride cycle in clip seconds (Lulu_Run.anm holds
# four in its 2 s); tick: the graph's mTickDuration over the clip's own frame time (Lulu's 0.05 s a frame at 30 fps:
# her cycle plays 1.5 times as long in League).
HEROES = {
    "jinx": dict(clip="Jinx_minigun_run", cycle=0.9333, tick=1.0,
                 joints=dict(pelvis="Pelvis", chest="Spine3", neck="Neck", head="Head",
                             l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                             r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                             l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                             r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                             gun="Minigun", gun_front="Minigun_Handle_Front", gun_back="Minigun_Handle_Back",
                             rocket="Rocket_Launcher", rocket_front="Rocket_Launcher_Front",
                             l_hair1="L_Hair1", l_hair3="L_Hair3", l_hair6="L_Hair6",
                             r_hair1="R_Hair1", r_hair3="R_Hair3", r_hair6="R_Hair6")),
    "vi": dict(clip="Vi_Run1", cycle=0.8387, tick=1.0,
               joints=dict(pelvis="Root", spine="Spine1", chest="Spine3", neck="Neck", head="Head",
                           l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                           r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                           l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_GloveHand",
                           l_forearm="L_GloveForarm",
                           r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_GloveHand",
                           r_forearm="R_GloveForarm",
                           hair1="Hair1", hair2="Hair2", l_flap="L_JacketFlap", r_flap="R_JacketFlap")),
    "lulu": dict(clip="Lulu_Run", cycle=0.5, tick=1.5,
                 joints=dict(pelvis="Hip", spine="Spine", chest="Chest", head="Head",
                             l_hip="L_thigh", l_knee="L_knee", l_foot="L_foot", l_toe="L_toe",
                             r_hip="R_thigh", r_knee="R_knee", r_foot="R_foot", r_toe="R_toe",
                             l_shoulder="L_upArm", l_elbow="L_foreArm", l_hand="L_hand",
                             r_shoulder="R_upArm", r_elbow="R_foreArm", r_hand="R_hand",
                             staff="Weapon", hat="hat", hat2="hat2", hat4="hat4", hat6="hat6",
                             l_hair="L_HairB_d", r_hair="R_HairA_d", f_skirt="f_skirt", b_skirt="b_skirt")),
}


def lp(path):
    return R.lp(path)


def motion_path(hero):
    return os.path.join(ROOT, "assets", "source", hero, "hd", f"{hero}_run_motion.json")


# ================================================================================================== League's motion
def extract(hero, lol):
    """League's run clip sampled over one cycle, side view, chibi proportions -> the motion table (see the module)."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
    import native_pose as N
    cfg = HEROES[hero]
    with open(lp(os.path.join(ROOT, "assets", "source", hero, "poses.json")), encoding="utf-8") as f:
        spec = json.load(f)
    chibi = dict(spec["chibi"])
    keep = chibi.pop("keep", None)
    ch = N.Champ(lol, spec["champ"], keep, spec.get("weapon", r"^weapon$"), spec.get("hide", ()),
                 spec.get("hair_part", False), spec.get("crown"), spec.get("parts", ()),
                 spec.get("hide_submeshes", False), spec.get("submesh_textures"), spec.get("glue"), spec.get("legs"))
    rot = N.camera({"yaw": 90, "pitch": 0})              # the model's +Z (its front) to +x: facing right
    by = {j["name"].lower(): i for i, j in enumerate(ch.joints)}
    pv, glob, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())   # game px per world unit
    floor = cv[ch.legv, 1].min()

    def point(g, name):
        p = rot @ g[by[name.lower()]][:3, 3]
        return [round(float(p[0] * unit), 3), round(float((p[1] - floor) * unit), 3), round(float(p[2] * unit), 3)]

    design = {k: point(glob, n) for k, n in cfg["joints"].items()}
    rows, low = [], []
    for k in range(SAMPLES):
        t = cfg["cycle"] * k / SAMPLES
        pv, glob, _ = ch.posed(f"{cfg['clip']}@{t * 1000:.3f}", chibi)
        rows.append({n: point(glob, j) for n, j in cfg["joints"].items()})
        low.append(round(float(((pv @ rot.T)[ch.legv, 1].min() - floor) * unit), 3))
    return {"champ": spec["champ"], "clip": cfg["clip"], "cycle_s": cfg["cycle"] * cfg["tick"], "unit": unit,
            "height": spec["height"], "chibi": spec["chibi"], "design": design, "low": low, "frames": rows}


def write_motion(hero, m):
    with open(lp(motion_path(hero)), "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n" + ",\n".join(f' "{k}": ' + json.dumps(v, separators=(",", ":"))
                                   for k, v in m.items() if k != "frames"))
        f.write(',\n "frames": [\n' + ",\n".join("  " + json.dumps(r, separators=(",", ":"))
                                               for r in m["frames"]) + "\n ]\n}\n")


class Motion:
    """The motion table, read at any phase (0..1 over the cycle, linear between samples, wrapping)."""

    def __init__(self, hero):
        with open(lp(motion_path(hero)), encoding="utf-8") as f:
            m = json.load(f)
        self.m = m
        self.n = len(m["frames"])
        self.cycle_s = m["cycle_s"]
        self.names = list(m["frames"][0])
        self.arr = {k: np.array([r[k] for r in m["frames"]], float) for k in self.names}   # (n, 3)
        self.low = np.array(m["low"], float)

    def at(self, name, ph):
        a = self.arr[name]
        x = (ph % 1.0) * self.n
        i = int(math.floor(x)) % self.n
        t = x - math.floor(x)
        return a[i] * (1 - t) + a[(i + 1) % self.n] * t

    def mean(self, name):
        return self.arr[name].mean(0)

    def sole(self, side):
        """(n, 2): the foot joint's forward and height over League's floor, the height less its lowest (the sole on
        the floor when planted)."""
        f = self.arr[f"{side}_foot"]
        return np.c_[f[:, 0], f[:, 1] - f[:, 1].min()]

    def stance(self, side, tol=0.5):
        """Samples where the foot is planted: within tol px of its lowest."""
        f = self.arr[f"{side}_foot"][:, 1]
        return f <= f.min() + tol

    def stance_speed(self, side):
        """How fast the planted foot goes back under the hip (px a second of League's cycle): the slope of its x
        relative to the hip over the planted samples."""
        st = self.stance(side)
        x = self.arr[f"{side}_foot"][:, 0] - self.arr[f"{side}_hip"][:, 0]
        dt = self.cycle_s / self.n
        sp = [(x[i] - x[(i + 1) % self.n]) / dt for i in range(self.n) if st[i] and st[(i + 1) % self.n]]
        return float(np.median(sp)) if sp else 0.0

    def contact(self, side):
        """The phase the foot lands (the first planted sample after a lifted one)."""
        st = self.stance(side)
        for i in range(self.n):
            if st[i] and not st[i - 1]:
                return i / self.n
        return 0.0


# ================================================================================================== geometry
def ik(hip, target, l1, l2, bend=1.0):
    """The knee of a two-bone leg from `hip` to `target` (design squares, y down), bending forward (+x) for bend > 0.
    A target out of reach: the leg straight toward it. -> (knee, the reached end)."""
    h, t = np.asarray(hip, float), np.asarray(target, float)
    v = t - h
    d = float(np.hypot(*v))
    if d < 1e-6:
        v, d = np.array([0.0, 1.0]), 1e-6
    u = v / d
    if d >= l1 + l2 - 1e-6:
        return h + u * l1, h + u * (l1 + l2)
    d = max(d, abs(l1 - l2) + 1e-6)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    hgt = math.sqrt(max(0.0, l1 * l1 - a * a))
    n = np.array([u[1], -u[0]])                       # the side of the line: (down -> +x) ... see bend
    if n[0] * bend < 0:
        n = -n
    return h + u * a + n * hgt, t


def angle_down(v):
    """Degrees of a vector (x, y down) from straight down, + toward +x (forward)."""
    return math.degrees(math.atan2(v[0], v[1]))


def _scale2x(a):
    H, W = a.shape
    p = np.pad(a, 1)
    A, B, C, D = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]
    out = np.empty((H * 2, W * 2), a.dtype)
    out[0::2, 0::2] = np.where((C == A) & (C != D) & (A != B), A, a)
    out[0::2, 1::2] = np.where((A == B) & (A != C) & (B != D), B, a)
    out[1::2, 0::2] = np.where((D == C) & (D != B) & (C != A), C, a)
    out[1::2, 1::2] = np.where((B == D) & (B != A) & (D != C), D, a)
    return out


def turned(img, at, src, dst, degrees, outline, tidy=True):
    """A part's picture `img` (its top-left at design square `at`) turned `degrees` counter-clockwise on screen about
    its point `src` and put with that point on `dst` (design squares, any fraction), RotSprite's way (inbetween.spin:
    Scale2x three times, turned, each square the commonest colour of its 8 x 8 block) - only its own colours, the
    outline tidied. -> (picture, its top-left square)."""
    H, W = img.shape[:2]
    m = img[..., 3] > 0
    packed = np.zeros((H, W), np.uint32)
    c = img.astype(np.uint32)
    packed[m] = (c[m][:, 0] << 16) | (c[m][:, 1] << 8) | c[m][:, 2] | np.uint32(0xFF000000)
    if not degrees and abs(dst[0] - src[0] - round(dst[0] - src[0])) < 1e-9 and \
            abs(dst[1] - src[1] - round(dst[1] - src[1])) < 1e-9:
        return img.copy(), (at[0] + int(round(dst[0] - src[0])), at[1] + int(round(dst[1] - src[1])))
    big = _scale2x(_scale2x(_scale2x(packed)))
    K = 8
    th = math.radians(degrees)
    co, si = math.cos(th), math.sin(th)
    # the turned picture's box (design squares): the corners of img turned
    corners = np.array([[at[0], at[1]], [at[0] + W, at[1]], [at[0], at[1] + H], [at[0] + W, at[1] + H]], float) - src
    tx = corners[:, 0] * co + corners[:, 1] * si + dst[0]
    ty = -corners[:, 0] * si + corners[:, 1] * co + dst[1]
    x0, y0 = int(math.floor(tx.min())) - 1, int(math.floor(ty.min())) - 1
    x1, y1 = int(math.ceil(tx.max())) + 1, int(math.ceil(ty.max())) + 1
    Wo, Ho = x1 - x0, y1 - y0
    Y, X = np.mgrid[0:Ho * K, 0:Wo * K]
    px = x0 + (X + 0.5) / K - dst[0]
    py = y0 + (Y + 0.5) / K - dst[1]
    sx = (px * co - py * si) + src[0]                  # back through the turn
    sy = (px * si + py * co) + src[1]
    fx = np.floor((sx - at[0]) * K).astype(int)
    fy = np.floor((sy - at[1]) * K).astype(int)
    ok = (fx >= 0) & (fx < W * K) & (fy >= 0) & (fy < H * K)
    rot = np.zeros((Ho * K, Wo * K), np.uint32)
    rot[ok] = big[fy[ok], fx[ok]]
    blocks = rot.reshape(Ho, K, Wo, K).transpose(0, 2, 1, 3).reshape(Ho, Wo, K * K)
    filled = (blocks != 0).sum(-1)
    out = np.zeros((Ho, Wo, 4), np.uint8)
    for y, x in zip(*np.nonzero(filled * 2 > K * K)):
        v = blocks[y, x]
        vals, cnt = np.unique(v[v != 0], return_counts=True)
        col = int(vals[cnt.argmax()])
        out[y, x] = ((col >> 16) & 255, (col >> 8) & 255, col & 255, 255)
    if tidy:
        out = G.complete_outline(out, color=tuple(outline), dark=DARK)[0]
        out = G.clean_outline(out, tuple(outline), dark=DARK)[0]
        lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
            for j in range(1, n + 1):
                if sz[j - 1] < max(4, 0.05 * sz.max()):
                    out[lab == j] = 0
    return out, (x0, y0)


def sheared(img, at, k, pivot_row, profile=1.5):
    """A hanging part (a braid, a tail) swung by whole rows: each row below `pivot_row` (design rows) shifted
    k x ((r - pivot) / (last - pivot)) ** profile columns, nothing above it. -> (picture, top-left)."""
    H, W = img.shape[:2]
    x0, y0 = at
    p = pivot_row - y0
    s = [0 if r <= p else int(round(k * ((r - p) / max(1, H - 1 - p)) ** profile)) for r in range(H)]
    lo, hi = min(s), max(s)
    out = np.zeros((H, W + hi - lo, 4), np.uint8)
    for r in range(H):
        out[r, s[r] - lo:s[r] - lo + W] = img[r]
    return out, (x0 + lo, y0)


def lifted(img, at, k, x_free, x_root, profile=1.5):
    """A part streaming sideways (hair behind the head, a cape) waved by whole columns: each column lifted
    k x (distance from x_root / reach) ** profile rows toward its free end x_free, nothing at the root.
    -> (picture, top-left)."""
    H, W = img.shape[:2]
    x0, y0 = at
    reach = max(1, abs(x_free - x_root))
    s = []
    for c in range(W):
        x = x0 + c
        t = (x - x_root) / (x_free - x_root) if x_free != x_root else 0.0
        t = min(1.0, max(0.0, t))
        s.append(-int(round(k * t ** profile)))
    lo, hi = min(s), max(s)
    out = np.zeros((H + hi - lo, W, 4), np.uint8)
    for c in range(W):
        out[s[c] - lo:s[c] - lo + H, c] = img[:, c]
    return out, (x0, y0 + lo)


def bent(img, at, root_row, k_mid, k_tip, tip_row=None):
    """A hanging part (a braid) bent by whole rows through three points: nothing at `root_row`, k_mid columns
    half way down, k_tip at its last row (a smooth curve through them) - League's hair chain's middle and tip.
    -> (picture, top-left)."""
    H, W = img.shape[:2]
    x0, y0 = at
    last = (tip_row if tip_row is not None else y0 + H - 1)
    span = max(1.0, last - root_row)
    s = []
    for r in range(H):
        t = min(1.0, max(0.0, (y0 + r - root_row) / span))
        # the quadratic through (0, 0), (0.5, k_mid), (1, k_tip)
        a = 2 * k_tip - 4 * k_mid
        b = 4 * k_mid - k_tip
        s.append(int(round(a * t * t + b * t)))
    lo, hi = min(s), max(s)
    out = np.zeros((H, W + hi - lo, 4), np.uint8)
    for r in range(H):
        out[r, s[r] - lo:s[r] - lo + W] = img[r]
    return out, (x0 + lo, y0)


def angle_up(v):
    """Degrees of a vector (x, y down) from straight up, + leaning toward +x."""
    return math.degrees(math.atan2(v[0], -v[1]))


def rot_pt(p, about, degrees):
    """A point turned `degrees` counter-clockwise on screen about `about` (y down)."""
    th = math.radians(degrees)
    dx, dy = p[0] - about[0], p[1] - about[1]
    return np.array([about[0] + dx * math.cos(th) + dy * math.sin(th),
                     about[1] - dx * math.sin(th) + dy * math.cos(th)])


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def leant(img, at, k, hip_row):
    """The upper body leant forward from the hips: each row above `hip_row` (design rows) moved round(k x its
    height over the hips) columns forward (jinx_excited_run's lean, gentler). -> (picture, top-left)."""
    if not k:
        return img, at
    H, W = img.shape[:2]
    x0, y0 = at
    s = [int(round(k * max(0.0, hip_row - (y0 + r)))) for r in range(H)]
    lo, hi = min(s), max(s)
    out = np.zeros((H, W + hi - lo, 4), np.uint8)
    for r in range(H):
        out[r, s[r] - lo:s[r] - lo + W] = img[r]
    return out, (x0 + lo, y0)


class Canvas:
    """A frame being composed in design squares, PAD squares round the design."""

    def __init__(self, shape, pad):
        self.pad = pad
        self.a = np.zeros((shape[0] + 2 * pad, shape[1] + 2 * pad, 4), np.uint8)
        self.z = np.full(self.a.shape[:2], -1e9)

    def stamp(self, img, at, z):
        """img's squares at design square `at`, over what is lower (z) and under what is higher."""
        ys, xs = np.nonzero(img[..., 3] > 0)
        Y, X = ys + int(at[1]) + self.pad, xs + int(at[0]) + self.pad
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
        up = self.z[Y, X] <= z
        Y, X, ys, xs = Y[up], X[up], ys[up], xs[up]
        self.a[Y, X] = img[ys, xs]
        self.z[Y, X] = z


def piece(d, m):
    ys, xs = np.nonzero(m)
    sub = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
    return sub, (int(xs.min()), int(ys.min()))


# ================================================================================================== the cycle
def move_speed(hero):
    with open(lp(os.path.join(ROOT, "league", "champion", f"league_{hero}.data_champion")), encoding="utf-8-sig") as f:
        return float(json.load(f)["stat"]["move_speed"])


class Gait:
    """Our run from League's: per frame the hip height, the body's sway, each leg's hip / knee / sole, and League's
    other joints at that phase (for what follows through).

    rig: the hero's numbers (design squares, y down): ground (the soles' bottom edge), hips {near, far} (x, y),
    thigh {near, far}, shin {near, far} (knee to the sole's contact point), sides {near: "l"|"r", far: ...} (which
    of League's legs drives ours), stride (forward scale of the sole path over the vertical), bob (share of League's
    pelvis bob kept), reach (the stance leg straight at most this share of its length), sway (share of League's
    pelvis sway kept)."""

    def __init__(self, hero, rig, ppu, n=N_FRAMES, cycle_s=None):
        self.m = Motion(hero)
        self.rig, self.ppu, self.n = rig, ppu, n
        v_px = move_speed(hero) / 1000.0 * TICKS                       # game px a second
        self.v = v_px * ppu                                            # squares a second
        height = rig["height"] / ppu                                   # game px tall
        self.cycle_s = cycle_s or round(CYCLE_HEIGHTS * height / v_px, 3)
        ms = int(round(self.cycle_s * 1000 / n))
        self.ms = [ms] * n
        self.cycle_s = ms * n / 1000.0
        m = self.m
        # League's leg (hip height over its floor, standing in the design pose) -> ours
        dsg = m.m["design"]
        lg_hip = np.mean([dsg[f"{s}_hip"][1] for s in "lr"])
        our_hip = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        self.s = our_hip / lg_hip                                      # squares per League px, up and down
        # forward: as far as the ground goes by while a foot is planted
        lg_v = np.mean([m.stance_speed(s) for s in "lr"])              # League px a second, at League's timing
        want = self.v * self.cycle_s                                   # squares of ground a cycle
        got = self.s * lg_v * m.cycle_s                                # League's planted sweep at our scale
        self.stride = rig.get("stride") or want / max(1e-6, got)
        self.stride = min(self.stride, rig.get("stride_max", 9.0))
        near_side = rig["sides"]["near"]
        self.ph0 = m.contact(near_side) + rig.get("phase", 0.0)       # frame 0: the near foot lands
        pel = m.arr["pelvis"][:, 1]
        self.pel_mean = pel.mean()
        self.sway_mean = m.arr["pelvis"][:, 0].mean()
        # the hip height: League's bob (x bob) about a middle chosen so every planted foot reaches the ground
        self.h_mid = self._fit_height()

    def phase(self, i):
        return (self.ph0 + i / self.n) % 1.0

    def _sole(self, key, ph, hip):
        """Our sole target for leg `key` at phase ph, its hip at `hip` (design squares)."""
        m, rig, side = self.m, self.rig, self.rig["sides"][key]
        f = m.at(f"{side}_foot", ph)
        h = m.at(f"{side}_hip", ph)
        lowest = m.arr[f"{side}_foot"][:, 1].min()
        dx = (f[0] - h[0]) * self.s * self.stride
        up = (f[1] - lowest) * self.s * rig.get("lift", 1.0)          # the sole's height over the ground
        return np.array([hip[0] + dx, rig["ground"] - up])

    def _bob(self, ph):
        return (self.m.at("pelvis", ph)[1] - self.pel_mean) * self.s * self.rig.get("bob", 1.0)

    def _fit_height(self):
        """The hip's middle height: the planted foot reaches the ground through the middle of its stance (REACH_Q of
        the planted samples; at landing and push-off it may hang a square over it, the heel or the toe down)."""
        rig = self.rig
        hs = []
        for k in range(self.m.n):
            ph = k / self.m.n
            for key in ("near", "far"):
                side = rig["sides"][key]
                if not self.m.stance(side)[k]:
                    continue
                hx = rig["hips"][key][0]
                sole = self._sole(key, ph, (hx, 0.0))
                reach = rig.get("reach", 0.97) * (rig["thigh"][key] + rig["shin"][key])
                dx = sole[0] - hx
                need = math.sqrt(max(0.0, reach * reach - dx * dx))     # hip at most this high over the sole
                hs.append(need - self._bob(ph))
        stand = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        return min(float(np.percentile(hs, rig.get("reach_q", 30))), stand + rig.get("rise", 0.0))

    def pose_dy_f(self, i, lag):
        """The body's sink (squares, down +) `lag` of a cycle before frame i (what trails it is where it was)."""
        rig = self.rig
        ph = (self.phase(i) - lag) % 1.0
        stand = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        return float(stand - (self.h_mid + self._bob(ph)))

    def pose(self, i):
        """-> {"ph", "dy": the body's rows (down +), "dx", "legs": {key: (hip, knee, sole)}}."""
        rig = self.rig
        ph = self.phase(i)
        h = self.h_mid + self._bob(ph)
        stand = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        dy = stand - h                                                 # the body sinks this many squares
        dx = (self.m.at("pelvis", ph)[0] - self.sway_mean) * self.s * rig.get("sway", 1.0)
        legs = {}
        for key in ("near", "far"):
            hx, hy = rig["hips"][key]
            hip = np.array([hx + dx, hy + dy])
            sole = self._sole(key, ph, hip)
            sole[1] = min(sole[1], rig["ground"])
            knee, end = ik(hip, sole, rig["thigh"][key], rig["shin"][key])
            legs[key] = (hip, knee, end)
        return {"ph": ph, "dy": dy, "dx": dx, "legs": legs}


# ================================================================================================== the heroes
class JinxRun:
    """league_jinx from her design's parts (tools/art/rig_jinx_hd.py masks): the stocking thighs laid along the bone
    as her rig lays them, the boots turned with the shin, the braids and Fishbones following through."""
    hero = "jinx"
    ppu = 2.2

    def __init__(self):
        import rig_jinx_hd as JX
        self.JX = JX
        self.d = np.asarray(Image.open(lp(os.path.join(ROOT, "assets", "source", "jinx", "hd", "design.png")))
                            .convert("RGBA")).copy()
        d = self.d
        self.M = JX.masks(d)
        self.pieces = {n: piece(d, m) for n, m in self.M.items()}
        self.legs = JX.Legs(d, self.M)
        self.outline = JX.O
        self.pivot = (JX.PIVOT_COL, JX.GROUND)          # the pivot column, the soles' bottom edge
        # the sole's contact point of each boot (its middle on the ground) and the knee it hangs from
        self.contact = {"near": (28.0, JX.GROUND), "far": (58.0, JX.GROUND)}
        hip_y = JX.RUN_HIP_Y
        self.rig = dict(ground=JX.GROUND, height=JX.GROUND - 0.0,
                        hips={"near": (JX.RUN_HIP_X["near"], hip_y), "far": (JX.RUN_HIP_X["far"], hip_y)},
                        thigh={"near": JX.RUN_LT["near"], "far": JX.RUN_LT["far"]},
                        shin={k: float(np.hypot(*np.subtract(self.contact[k], JX.KNEE[k]))) for k in ("near", "far")},
                        sides={"near": "l", "far": "r"}, bob=0.75, reach=0.98, sway=0.5,
                        # the lean: columns a row over the hips, and the share of League's spine swing kept;
                        # the head bobs (1 - head_counter) of the hips and tilts head_tilt of League's nod; the gun
                        # stays gun_lag of where the body was a frame ago and tilts gun_tilt of League's minigun;
                        # the braids (middle, tip) stream back by braid_base and swing braid_gain x League's chain
                        lean=0.07, lean_gain=0.8, head_counter=0.45, head_tilt=0.3, gun_lag=1.0, gun_tilt=0.4,
                        braid_base={"n": (-3, -8), "f": (-5, -14)}, braid_gain=2.8, fish_lag=1.0)

    # joints of the design (squares, edges): the shoulders, the near elbow, the hands on the gun, the neck
    S_FAR, H_FAR = (48.5, 29.5), (64.0, 43.0)
    S_NEAR, E_NEAR, H_NEAR = (38.0, 30.0), (31.5, 38.5), (45.0, 44.0)
    NECK = (47.0, 27.0)
    GUN_PIVOT = (54.0, 45.0)

    def signals(self, g, pose, i):
        """The upper body's moves at this frame, all from League's joints (squares / degrees):
        lean (columns a row over the hips: League's spine angle about its mean), the head's counter-bob and tilt
        (League's head on its neck), the gun a frame behind the body and tilting with League's minigun, the braids
        bent through League's hair chains (their middle and tip under the head, about their mean)."""
        m, ph, s = g.m, pose["ph"], g.s
        rig = self.rig
        sp = lambda q: angle_up(m.at("chest", q) - m.at("pelvis", q))
        spm = float(np.mean([angle_up(r) for r in m.arr["chest"] - m.arr["pelvis"]]))
        lean = rig["lean"] + math.tan(math.radians(rig["lean_gain"] * (sp(ph) - spm)))
        hn = lambda q: angle_up(m.at("head", q) - m.at("neck", q))
        hnm = float(np.mean([angle_up(r) for r in m.arr["head"] - m.arr["neck"]]))
        tilt = -rig["head_tilt"] * wrap180(hn(ph) - hnm)        # (+ League: the face down, forward -> clockwise)
        head_dy = -rig["head_counter"] * pose["dy"]
        late = g.pose_dy_f(i, 1.0 / g.n) - pose["dy"]           # where the body was a frame ago
        ga = lambda q: angle_up(m.at("gun_front", q) - m.at("gun_back", q))
        gam = float(np.mean([angle_up(r) for r in m.arr["gun_front"] - m.arr["gun_back"]]))
        gun_tilt = -rig["gun_tilt"] * wrap180(ga(ph) - gam)
        braids = {}
        for key, side in (("n", "r"), ("f", "l")):
            def off(j):
                v = m.at(f"{side}_{j}", ph) - m.at("head", ph)
                v0 = m.mean(f"{side}_{j}") - m.mean("head")
                return (v[1] - v0[1]) * s
            base_mid, base_tip = rig["braid_base"][key]
            braids[key] = (base_mid - rig["braid_gain"] * 0.5 * off("hair3"), base_tip - rig["braid_gain"] * off("hair6"))
        return dict(lean=lean, tilt=tilt, head_dy=head_dy, gun_dy=rig["gun_lag"] * late, gun_tilt=gun_tilt,
                    braids=braids, late=late)

    def frame(self, g, pose, i, only=None):
        JX = self.JX
        d = self.d
        can = Canvas(d.shape, 50)
        Z = JX.Z
        m = g.m
        ph = pose["ph"]
        bdx, bdy = int(round(pose["dx"])), int(round(pose["dy"]))
        sg = self.signals(g, pose, i)
        hip_row = self.rig["hips"]["near"][1]
        o = self.outline
        hdy = int(round(sg["head_dy"]))
        gdy = int(round(sg["gun_dy"]))
        # the gun's move (about its pivot, then down): the hands on it go with it, the arms turn to keep hold
        def gun_move(p):
            q = rot_pt(p, self.GUN_PIVOT, sg["gun_tilt"])
            return q + np.array([0.0, gdy])
        a_far = angle_down(gun_move(self.H_FAR) - np.array(self.S_FAR)) - angle_down(
            np.array(self.H_FAR) - np.array(self.S_FAR))
        a_near = angle_down(gun_move(self.E_NEAR) - np.array(self.S_NEAR)) - angle_down(
            np.array(self.E_NEAR) - np.array(self.S_NEAR))
        kn = sg["braids"]["n"]
        kf = sg["braids"]["f"]
        items = []
        for name in JX.PARTS:
            if name in ("leg_r", "leg_f") or (only is not None and name not in only):
                continue
            img, at = self.pieces[name]
            x, y = at
            dx, dy = 0, 0
            if name == "braid_n":
                img, (x, y) = bent(img, at, at[1] + 5, kn[0], kn[1])
                dy = hdy
            elif name == "braid_f":
                img, (x, y) = bent(img, at, at[1] + 3, kf[0], kf[1])
                dy = hdy
            elif name == "curl":
                x, y = x + JX.CURL_ON[0] + int(round(kf[1])), y + JX.CURL_ON[1]
                dy = hdy
            elif name == "head":
                if abs(sg["tilt"]) >= 0.5:
                    img, (x, y) = turned(img, at, self.NECK, self.NECK, sg["tilt"], o)
                dy = hdy
            elif name in ("gun", "arm_lo"):
                if abs(sg["gun_tilt"]) >= 0.5:
                    img, (x, y) = turned(img, at, self.GUN_PIVOT, self.GUN_PIVOT, sg["gun_tilt"], o)
                dy = gdy
            elif name == "arm_f" and abs(a_far) >= 0.5:
                img, (x, y) = turned(img, at, self.S_FAR, self.S_FAR, a_far, o)
            elif name == "arm_n" and abs(a_near) >= 0.5:
                img, (x, y) = turned(img, at, self.S_NEAR, self.S_NEAR, a_near, o)
            elif name == "fish":
                dy = int(round(sg["late"] * self.rig["fish_lag"]))
            img, (x, y) = leant(img, (x, y), sg["lean"], hip_row)
            items.append((Z[name], img, (x + bdx + dx, y + bdy + dy)))
        for z, img, at in sorted(items, key=lambda t: t[0]):
            can.stamp(img, at, z)
        # the legs
        for key, zname in (("far", "leg_f"), ("near", "leg_r")):
            hip, knee, out, oat = self.leg(g, key, pose["legs"][key])
            cells = JX.fold(self.legs.thigh(key, tuple(hip), tuple(knee)))
            timg, tx, ty = JX.cells_img(cells)
            can.stamp(timg, (tx, ty), Z[zname])
            can.stamp(out, oat, Z[zname] + 0.1)
        return can

    def leg(self, g, key, leg):
        """One leg's knee and its boot turned with the shin; where the turned boot would go under the ground (a heel
        or a toe), the sole's target is raised as much and the knee found again. -> (hip, knee, boot, its top-left)."""
        JX = self.JX
        hip, knee, sole = leg
        bimg, bat = self.legs.boot[key]
        k0 = np.array(JX.KNEE[key])
        c0 = np.array(self.contact[key])
        rest = angle_down(c0 - k0)
        target = np.array(sole, float)
        for _ in range(4):
            out, oat = turned(bimg, bat, tuple(k0), tuple(knee), angle_down(target - knee) - rest, self.outline)
            ys = np.nonzero((out[..., 3] > 0).any(1))[0]
            under = (oat[1] + ys.max() + 1) - math.ceil(self.rig["ground"])
            if under <= 0:
                break
            target = target - np.array([0.0, under])
            knee, target = ik(hip, target, self.rig["thigh"][key], self.rig["shin"][key])
        return hip, knee, out, oat


def poly_mask(shape, pts):
    """Squares whose centre lies inside the polygon pts [(x, y), ...] (square edges)."""
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    return np.asarray(img, bool)


def colour_mask(d, cols, tol=0):
    rgb = d[..., :3].astype(int)
    m = np.zeros(d.shape[:2], bool)
    for c in cols:
        m |= (np.abs(rgb - np.array(c)).sum(-1) <= tol)
    return m & (d[..., 3] > 0)


class LegArt:
    """A leg drawn from the design: the thigh's rows (cross-sections of a thigh the design shows whole) laid along
    hip -> knee (league_jinx's Legs.thigh), the shin and boot the design's own, turned with the shin about the knee.
    rows: (mask, row0, row1) the thigh's squares; shin: (mask) the shin + boot squares; knee, contact: the shin's top
    and its sole's middle on the ground (design squares, edges)."""

    def __init__(self, d, thigh_mask, rows, shin_mask, knee, contact, outline, rigid=False):
        self.outline = outline
        self.rigid = rigid              # a foot that only moves (Lulu's boots under her robe): never turned
        self.slices = []
        dark = (IB_lum(d[..., :3]) < DARK)
        for y in range(rows[0], rows[1] + 1):
            xs = np.nonzero(thigh_mask[y] & ~dark[y])[0]
            if len(xs):
                self.slices.append(d[y, xs.min():xs.max() + 1].copy())
        self.shin = piece(d, shin_mask)
        self.knee = np.array(knee, float)
        self.contact = np.array(contact, float)
        self.rest = angle_down(self.contact - self.knee)

    def thigh(self, H, K):
        """{(x, y): rgba} the thigh along H -> K (design squares, edges), its rows along it, the outline round it."""
        H, K = np.asarray(H, float), np.asarray(K, float)
        v = K - H
        L = max(1e-6, float(np.hypot(*v)))
        u = v / L
        n = np.array((u[1], -u[0]))
        cells = {}
        for y in range(int(math.floor(min(H[1], K[1]))) - 8, int(math.ceil(max(H[1], K[1]))) + 8):
            for x in range(int(math.floor(min(H[0], K[0]))) - 8, int(math.ceil(max(H[0], K[0]))) + 8):
                q = np.array((x + 0.5, y + 0.5)) - H
                t, s_ = float(q @ u), float(q @ n)
                if t < -1.5 or t > L + 1.0:
                    continue
                row = self.slices[int(round(min(1.0, max(0.0, t / L)) * (len(self.slices) - 1)))]
                xi = int(math.floor(len(row) / 2 + s_))
                if 0 <= xi < len(row) and row[xi][3]:
                    cells[(x, y)] = row[xi]
        out = dict(cells)
        for (x, y) in list(cells):
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + ddx, y + ddy) not in cells:
                    out.setdefault((x + ddx, y + ddy), np.array((*self.outline, 255), np.uint8))
        xs = [x for x, _ in out]
        ys = [y for _, y in out]
        x0, y0 = min(xs), min(ys)
        img = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
        for (x, y), c in out.items():
            img[y - y0, x - x0, :3] = np.asarray(c)[:3]
            img[y - y0, x - x0, 3] = 255
        return img, (x0, y0)

    def shin_at(self, knee, sole):
        img, at = self.shin
        if self.rigid:                  # the boot's sole on the target, upright, by whole squares
            dx, dy = (int(round(v)) for v in np.asarray(sole) - self.contact)
            return img.copy(), (at[0] + dx, at[1] + dy)
        return turned(img, at, tuple(self.knee), tuple(knee), angle_down(np.asarray(sole) - knee) - self.rest,
                      self.outline)


def IB_lum(rgb):
    rgb = rgb.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


class PartRun:
    """A hero cut into parts by polygons (and colours) on the design: the body moved by whole squares (bob, sway,
    lean), parts with moves of their own (an arm's swing, a beat late), what hangs waved, the legs LegArt. A square a
    moved part bares inside the figure is filled from round it (ppu_rig.fill_under); the outline closed again."""
    hero = None
    ppu = None
    outline = None
    PARTS = []          # [(name, polygon | box (x0, y0, x1, y1), colours to leave out or None)] in claiming order
    Z = {}
    REST = "body"

    def __init__(self):
        self.d = np.asarray(Image.open(lp(os.path.join(ROOT, "assets", "source", self.hero, "hd", "design.png")))
                            .convert("RGBA")).copy()
        d = self.d
        op = d[..., 3] > 0
        taken = np.zeros(op.shape, bool)
        self.M = {}
        for name, shape, leave in self.PARTS:
            if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape):
                x0, y0, x1, y1 = shape
                m = np.zeros(op.shape, bool)
                m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
            else:
                m = poly_mask(op.shape, shape)
            m &= op & ~taken
            if isinstance(leave, dict):
                m &= colour_mask(d, leave["keep"])
            elif leave:
                m &= ~colour_mask(d, leave)
            self.M[name] = m
            taken |= m
        self.M[self.REST] = op & ~taken
        self.pieces = {n: piece(d, m) for n, m in self.M.items() if m.any()}
        self.holes0 = ndimage.binary_fill_holes(op) & ~op

    def parts_png(self, path, z=8):
        tints = [(255, 0, 0), (0, 160, 255), (0, 200, 0), (255, 200, 0), (200, 0, 255), (255, 120, 0), (0, 255, 200),
                 (120, 60, 0), (255, 0, 160)]
        img = np.zeros(self.d.shape[:2] + (3,), np.uint8) + 230
        for k, (name, m) in enumerate(self.M.items()):
            img[m] = (self.d[m, :3] * 0.45 + np.array(tints[k % len(tints)]) * 0.55).astype(np.uint8)
        Image.fromarray(img).resize((img.shape[1] * z, img.shape[0] * z), Image.NEAREST).save(path)
        print(path, {n: int(m.sum()) for n, m in self.M.items()})

    def frame(self, g, pose, i, only=None):
        """The parts put down in their order, each: waved (`wave`: ("lift", k, x_free, x_root) by columns,
        ("shear", k, pivot_row) or ("bent", root_row, k_mid, k_tip) by rows), turned about a joint (`rot`: (joint,
        degrees counter-clockwise), RotSprite's way), moved (`dx`, `dy`), leant with the upper body and moved with
        it; then the legs."""
        d = self.d
        can = Canvas(d.shape, 50)
        bdx, bdy = int(round(pose["dx"])), int(round(pose["dy"]))
        spec = self.pose_parts(g, pose, i)
        lean = spec.pop("_lean", None)
        if lean is None:
            lean = self.lean(g, pose["ph"])
        hip_row = np.mean([self.rig["hips"][k][1] for k in ("near", "far")])
        items = []
        for name, (img, at) in self.pieces.items():
            if name.startswith("leg_") or (only is not None and name not in only):
                continue
            t = spec.get(name, {})
            x, y = at
            w = t.get("wave")
            if w and w[0] == "lift" and w[1]:
                img, (x, y) = lifted(img, (x, y), w[1], w[2], w[3])
            elif w and w[0] == "shear" and w[1]:
                img, (x, y) = sheared(img, (x, y), w[1], w[2])
            elif w and w[0] == "bent":
                img, (x, y) = bent(img, (x, y), w[1], w[2], w[3])
            r = t.get("rot")
            if r and abs(r[1]) >= 0.5:
                img, (x, y) = turned(img, (x, y), r[0], r[0], r[1], self.outline)
            if not t.get("still"):
                img, (x, y) = leant(img, (x, y), lean, hip_row)
                x, y = x + bdx, y + bdy
            items.append((self.Z[name], img, (x + int(round(t.get("dx", 0))), y + int(round(t.get("dy", 0))))))
        for z, img, at in sorted(items, key=lambda q: q[0]):
            can.stamp(img, at, z)
        for key in ("far", "near"):
            hip, knee, sole = pose["legs"][key]
            art = self.legs[key]
            knee, shin, sat = self.leg(art, key, hip, knee, sole)
            z = self.Z[f"leg_{key}"]
            if self.rig.get("thighs", True):
                timg, tat = art.thigh(hip, knee)
                can.stamp(timg, tat, z)
            can.stamp(shin, sat, z + 0.1)
        return can

    def pose_parts(self, g, pose, i):
        """{part: {"dx", "dy", "rot", "wave", "still"}} and "_lean" (the hero's own)."""
        return {}

    # ---- League's joints as moves (shared by the heroes)
    @staticmethod
    def spine_lean(g, ph, base, gain):
        """Columns a row over the hips: `base` plus `gain` of League's spine swing (pelvis -> chest) about its mean."""
        m = g.m
        mean = float(np.mean([angle_up(r) for r in m.arr["chest"] - m.arr["pelvis"]]))
        return base + math.tan(math.radians(gain * wrap180(angle_up(m.at("chest", ph) - m.at("pelvis", ph)) - mean)))

    @staticmethod
    def swing(g, ph, a, b, gain):
        """Degrees counter-clockwise on screen: `gain` of League's a -> b (an arm, a staff) turn about its mean."""
        m = g.m
        mean = float(np.mean([angle_up(r) for r in m.arr[b] - m.arr[a]]))
        return -gain * wrap180(angle_up(m.at(b, ph) - m.at(a, ph)) - mean)

    @staticmethod
    def rel(g, ph, name, to, k):
        """A joint's offset from another (League px x the scale -> squares, axis k: 0 forward, 1 up) about its mean."""
        m = g.m
        v = m.at(name, ph) - m.at(to, ph)
        v0 = m.mean(name) - m.mean(to)
        return (v[k] - v0[k]) * g.s

    def lean(self, g, ph):
        return self.spine_lean(g, ph, self.rig.get("lean", 0.0), self.rig.get("lean_gain", 0.0))

    def leg(self, art, key, hip, knee, sole):
        """The knee and the shin turned; a turned boot that would go under the ground lifts its sole's target as
        much and the knee is found again (JinxRun.leg)."""
        target = np.array(sole, float)
        for _ in range(4):
            out, oat = art.shin_at(knee, target)
            ys = np.nonzero((out[..., 3] > 0).any(1))[0]
            under = (oat[1] + ys.max() + 1) - math.ceil(self.rig["ground"])
            if under <= 0:
                break
            target = target - np.array([0.0, under])
            knee, target = ik(hip, target, self.rig["thigh"][key], self.rig["shin"][key])
        return knee, out, oat

    def finish(self, can):
        """Holes the moves bared inside the figure (not the design's own gaps) filled from round them; the outline
        closed (ppu_rig.tidy)."""
        a = can.a
        p = can.pad
        op = a[..., 3] > 0
        own = np.zeros(op.shape, bool)
        own[p:p + self.d.shape[0], p:p + self.d.shape[1]] = self.holes0
        holes = ndimage.binary_fill_holes(op) & ~op & ~ndimage.binary_dilation(own, iterations=1)
        lab, n = ndimage.label(holes)
        for j in range(1, n + 1):
            h = lab == j
            if h.sum() <= self.FILL_MAX:
                a = R.fill_under(a, h)
        return R.tidy(a, self.outline)

    FILL_MAX = 60


VI_HAIR = [(232, 54, 124), (249, 100, 164), (205, 40, 105), (170, 27, 83), (141, 19, 67), (116, 16, 56),
           (176, 60, 102), (91, 17, 47)]


class ViRun(PartRun):
    """league_vi: the design cut into her two gauntlets (the near one low at her hip, the far one raised), the head
    (her hair streaming back), the body and the legs; the gauntlets pump with League's hands, the hair waves."""
    hero = "vi"
    ppu = 73 / 40
    outline = (26, 12, 16)
    PARTS = [
        ("fist_near", [(0, 25), (11, 20), (21, 20), (23, 28), (23, 52), (20, 58), (0, 58)], VI_HAIR),
        ("fist_far", [(36, 13), (53, 13), (53, 43), (37, 43), (33, 38), (33, 24), (35, 21)], None),
        ("leg_far", [(29, 45), (46, 45), (47, 55), (53, 61), (53, 74), (31, 74), (31, 56)], None),
        ("leg_near", [(0, 56), (17, 56), (17, 74), (0, 74)], None),
        ("head", [(0, 0), (40, 0), (40, 13), (36, 22), (33, 26), (24, 29), (14, 29), (0, 29)], None),
    ]
    Z = {"leg_far": 1, "body": 2, "head": 3, "fist_far": 4, "leg_near": 5, "fist_near": 6}

    def __init__(self):
        super().__init__()
        d = self.d
        o = self.outline
        far, near = self.M["leg_far"], self.M["leg_near"]
        self.legs = {
            "far": LegArt(d, far, (46, 55), far & (np.arange(d.shape[0])[:, None] >= 55), (39.0, 55.5), (43.0, 73.0), o),
            "near": LegArt(d, far, (46, 55), near & (np.arange(d.shape[0])[:, None] >= 57), (9.0, 58.0), (6.0, 73.0), o),
        }
        ground = 73.0
        hips = {"far": (34.0, 47.0), "near": (22.0, 47.0)}
        total = (ground - hips["far"][1]) * 1.04
        shin = {k: float(np.hypot(*(self.legs[k].contact - self.legs[k].knee))) for k in ("far", "near")}
        self.rig = dict(ground=ground, height=ground, hips=hips, shin=shin,
                        thigh={k: total - shin[k] for k in ("far", "near")},
                        sides={"near": "l", "far": "r"}, bob=0.7, reach=0.98, sway=0.5, lean=0.06, lean_gain=0.7,
                        head_counter=0.45)

    NECK = (28.0, 26.0)
    SHOULDER = {"fist_near": (16.0, 25.0), "fist_far": (35.0, 24.0)}

    def pose_parts(self, g, pose, i):
        """The gauntlets turned about the shoulders with League's arms (and moved with its gloves), the head bobbing
        less than the hips and nodding with League's head, her hair's free end trailing the body by a beat."""
        ph, rig = pose["ph"], self.rig
        out = {"_lean": self.spine_lean(g, ph, rig["lean"], rig["lean_gain"])}
        for part, side, gain, move in (("fist_near", "l", 1.0, 0.35), ("fist_far", "r", 0.7, 0.3)):
            out[part] = {"rot": (self.SHOULDER[part], self.swing(g, ph, f"{side}_shoulder", f"{side}_hand", gain)),
                         "dx": move * self.rel(g, ph, f"{side}_hand", "chest", 0),
                         "dy": -move * self.rel(g, ph, f"{side}_hand", "chest", 1)}
        head_dy = -rig["head_counter"] * pose["dy"]
        trail = pose["dy"] - g.pose_dy_f(i, 1.5 / g.n)          # how far the body went down since 1.5 frames ago
        tilt = 0.8 * self.swing(g, ph, "neck", "head", 1.0)
        out["head"] = {"dy": head_dy, "rot": (self.NECK, tilt), "wave": ("lift", int(round(1.5 * trail)), 3, 21)}
        return out


LULU_HAIR = [(70, 24, 102), (85, 35, 121), (41, 12, 61), (117, 58, 160), (56, 19, 82), (24, 10, 22), (35, 16, 30)]


class LuluRun(PartRun):
    """league_lulu: League's skipping run (Lulu_Run: two hops a cycle) on her design - her boots peeping out under
    the robe in turn, the body hopping, the hat's curled tip and her long hair flapping with League's own hat and
    hair joints, the staff (and her hands) a beat late, Pix floating on his own beside her."""
    hero = "lulu"
    ppu = 70 / 39
    outline = (24, 10, 22)
    PARTS = [
        ("pix", (3, 0, 17, 16), None),
        ("hand_free", [(54, 45), (66, 45), (66, 54), (54, 54)], None),
        ("staff", [(48, 0), (69, 0), (69, 20), (64, 40), (61, 46), (65, 47), (66, 54), (58, 55), (56, 63), (47, 63),
                   (43, 57), (43, 49), (51, 46), (56, 30), (60, 16), (48, 13)], None),
        ("leg_near", (38, 65, 52, 70), None),
        ("leg_far", (20, 65, 36, 70), None),
        ("hair", [(4, 44), (34, 44), (34, 70), (4, 70)], {"keep": LULU_HAIR}),
        ("hat_tip", [(0, 24), (16, 22), (26, 30), (30, 38), (30, 47), (16, 47), (0, 46)], None),
        ("head", [(8, 9), (50, 9), (57, 20), (57, 48), (26, 49), (10, 47), (8, 20)], None),
    ]
    Z = {"hair": 1, "leg_far": 1.2, "leg_near": 1.4, "body": 2, "head": 3, "hat_tip": 3.1, "staff": 4,
         "hand_free": 4.1, "pix": 5}
    NECK = (44.0, 46.0)
    HAT_ROOT = (27.0, 32.0)
    STAFF_HAND = (47.0, 53.0)
    HAND_ROOT = (55.0, 50.0)

    def __init__(self):
        super().__init__()
        d = self.d
        o = self.outline
        rows = np.arange(d.shape[0])[:, None]
        legs = {}
        for key in ("near", "far"):
            m = self.M[f"leg_{key}"]
            ys, xs = np.nonzero(m)
            cx = (xs.min() + xs.max() + 1) / 2
            legs[key] = LegArt(d, m, (int(ys.min()) + 1, int(ys.min()) + 2), m, (cx, float(ys.min()) + 1.0),
                               (cx, 70.0), o, rigid=True)
        self.legs = legs
        ground = 70.0
        hips = {"near": (legs["near"].knee[0], 61.0), "far": (legs["far"].knee[0], 61.0)}
        total = (ground - 61.0) * 1.04
        shin = {k: float(np.hypot(*(legs[k].contact - legs[k].knee))) for k in ("far", "near")}
        self.rig = dict(ground=ground, height=ground, hips=hips, shin=shin,
                        thigh={k: total - shin[k] for k in ("far", "near")},
                        sides={"near": "r", "far": "l"}, bob=0.5, reach=0.98, sway=0.4, lean=0.03, hop_lean=0.014,
                        head_counter=0.35,
                        lift=0.35, thighs=False, phase=0.06)        # (frames on landing, rising, top, falling)

    def pose_parts(self, g, pose, i):
        """The hat's curled tip turned and flapping with League's hat chain, her hair with League's hair, the head a
        little behind the hop, the staff swinging about her hand with League's staff (and a beat late), the free hand
        with League's, Pix on his own."""
        ph, rig = pose["ph"], self.rig
        late = g.pose_dy_f(i, 1.0 / g.n) - pose["dy"]           # where the body was a frame ago
        head_dy = -rig["head_counter"] * pose["dy"]
        # League's Lulu hops upright (her spine swings under a degree): she pitches forward as she comes down and
        # straightens as she takes off, hop_lean columns a row for every square the body went down since a frame ago
        out = {"_lean": rig["lean"] + rig["hop_lean"] * (-late)}
        out["head"] = {"dy": head_dy, "rot": (self.NECK, 0.6 * self.swing(g, ph, "chest", "head", 1.0))}
        out["hat_tip"] = {"dy": head_dy, "rot": (self.HAT_ROOT, self.swing(g, ph, "hat2", "hat6", 0.45)),
                          "wave": ("lift", int(round(0.25 * self.rel(g, ph, "hat6", "head", 1))), 0, 27)}
        out["hair"] = {"dy": 0.5 * head_dy, "wave": ("lift", int(round(0.3 * self.rel(g, ph, "l_hair", "head", 1))), 4, 32)}
        out["staff"] = {"dy": 0.6 * late, "rot": (self.STAFF_HAND, self.swing(g, ph, "l_hand", "staff", 0.3))}
        out["hand_free"] = {"dx": 0.15 * self.rel(g, ph, "r_hand", "chest", 0),
                            "dy": -0.25 * self.rel(g, ph, "r_hand", "chest", 1)}
        # the robe's hem trails the hop (its lower rows a beat behind the body)
        trail = pose["dy"] - g.pose_dy_f(i, 1.5 / g.n)
        out["body"] = {"wave": ("shear", int(round(-0.8 * trail)), 55)}
        # Pix flies on his own: not moved with her, a slow bob and a sway of his own
        out["pix"] = {"still": True, "dx": round(2.0 * math.sin(2 * math.pi * (ph + 0.1))),
                      "dy": round(2.5 * math.sin(2 * math.pi * (ph + 0.3)))}
        return out


RUNS = {"jinx": JinxRun, "vi": ViRun, "lulu": LuluRun}


# ================================================================================================== the sheet
TAGS = ("run", "hd_run", "lo_run")


def rect_of(f):
    return tuple(int(round(f["data"][k])) for k in ("x", "y", "w", "h"))


def read_sheet(hero):
    import ppu_hd
    stem = ppu_hd.stem_of(hero)
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        an = json.load(f)
    px = np.array(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    return stem, an, px


def frame_px(px, f):
    x, y, w, h = rect_of(f)
    return px[y:y + h, x:x + w].copy()


def idle_frame(hero):
    """The hero's dense standing frame as the game draws it (hd_idle_base[0]: the design held still)."""
    _, an, px = read_sheet(hero)
    return frame_px(px, an["anims"]["hd_idle_base"]["frames"][0])


def pivot_of(hero, d):
    """The pivot (every frame's centre) in design squares (edges): where the hero's own dense idle_base frame (the
    design held still) has it - the run's frames stand exactly where the rest of the hero's do."""
    _, an, px = read_sheet(hero)
    b = frame_px(px, an["anims"]["hd_idle_base"]["frames"][0])
    m = d[..., 3] > 0
    best = None
    for oy in range(0, b.shape[0] - d.shape[0] + 1):
        for ox in range(0, b.shape[1] - d.shape[1] + 1):
            sub = b[oy:oy + d.shape[0], ox:ox + d.shape[1]]
            same = int((sub[m] == d[m]).all(-1).sum())
            if best is None or same > best[0]:
                best = (same, ox, oy)
    same, ox, oy = best
    if same < 0.97 * m.sum():
        sys.exit(f"{hero}: hd_idle_base[0] does not hold the design ({same} of {int(m.sum())} squares)")
    return b.shape[1] / 2 - ox, b.shape[0] / 2 - oy


def dense_frames(frames, pad, pivot, ppu):
    """The composed canvases (design squares + pad) cut to one size about the pivot: every frame centred on it, as
    wide and tall as the widest reach of any of them (so no frame's centre falls half a square off another's).
    -> ([dense frames], (w1, h1) the 1x size)."""
    px, py = pivot[0] + pad, pivot[1] + pad
    allop = np.stack([f[..., 3] > 0 for f in frames]).any(0)
    ys, xs = np.nonzero(allop)
    hw = max(px - xs.min(), xs.max() + 1 - px)
    hh = max(py - ys.min(), ys.max() + 1 - py)
    hw1 = int(math.ceil(hw / ppu - 0.5))
    hh1 = max(int(math.ceil(hh / ppu - 0.5)), int(math.ceil(R.FEET)) + 1)
    w1, h1 = 2 * hw1 + 1, 2 * hh1 + 1
    W, H = round(w1 * ppu), round(h1 * ppu)
    while abs((px - W / 2) - round(px - W / 2)) > 1e-6 or W / 2 < hw:
        W += 1
    while abs((py - H / 2) - round(py - H / 2)) > 1e-6 or H / 2 < hh:
        H += 1
    x0, y0 = int(round(px - W / 2)), int(round(py - H / 2))
    out = []
    for f in frames:
        b = np.zeros((H, W, 4), np.uint8)
        sx0, sy0 = max(0, x0), max(0, y0)
        sub = f[sy0:min(f.shape[0], y0 + H), sx0:min(f.shape[1], x0 + W)]
        b[sy0 - y0:sy0 - y0 + sub.shape[0], sx0 - x0:sx0 - x0 + sub.shape[1]] = sub
        out.append(b)
    return out, (w1, h1)


def one_frames(hero, dense, size, ppu):
    """The 1x frames from the dense ones as tools/art/ppu_one.py brings them down (pixel_down.pixelate, centred),
    on a rect of the 1x size grown alike at both ends where the drawing needs it."""
    import ppu_one
    w1, h1 = size
    out = []
    for b in dense:
        ws = [w1 + 2 * k for k in range(0, 6)]
        hs = [h1 + 2 * k for k in range(0, 6)]
        f, off = ppu_one.one_frame(b, w1, h1, 1.0 / ppu, ws, hs)
        if off:
            sys.exit(f"{hero}: a 1x run frame loses {off} squares off its rect")
        out.append(f)
    W = max(f.shape[1] for f in out)
    H = max(f.shape[0] for f in out)
    same = []
    for f in out:                                       # one size for all, grown alike at both ends
        g_ = np.zeros((H, W, 4), np.uint8)
        oy, ox = (H - f.shape[0]) // 2, (W - f.shape[1]) // 2
        g_[oy:oy + f.shape[0], ox:ox + f.shape[1]] = f
        same.append(g_)
    return same


def lo_frames(hero, ones, dense, ms):
    """lo_run the way tools/art/ppu_hd.py makes every lo_ tag (add_lo) from the hd_ one."""
    import ppu_hd
    mini = {"run": list(zip(ones, ms)), "hd_run": list(zip(dense, ms))}
    ppu_hd.add_lo(hero, mini)
    return [f for f, _ in mini["lo_run"]]


def strip(frames):
    Hm = max(h.shape[0] for h in frames)
    out = np.zeros((Hm, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        out[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return out


def write_strips(hero, dense, ppu, orig=None):
    """assets/source/ppu/<hero>_run.png (+ .json sizes): the strip tools/art/ppu_hd.py reads for hd_run (so its run
    writes these frames again); `orig`: the frames before the outline pass, into ppu/orig/ for tools/art/ppu_restyle.py
    (a restyle run then starts from these, not the old run)."""
    for folder, fr in ((os.path.join(ROOT, "assets", "source", "ppu"), dense),
                       (os.path.join(ROOT, "assets", "source", "ppu", "orig"), orig)):
        if fr is None:
            continue
        Image.fromarray(strip(fr), "RGBA").save(lp(os.path.join(folder, f"{hero}_run.png")), optimize=True)
        with open(lp(os.path.join(folder, f"{hero}_run.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in fr], "ppu": ppu}, f)


def place(px, anims, drop, new):
    """The sheet with the tags in `drop` taken off (their squares cleared where no other tag uses them) and `new`
    ({tag: [(frame, ms)]}) put in the free room - top-left first, 1 clear square between frames, no wider than the
    sheet; every other tag's frames stay exactly where they are. -> (sheet, anims)."""
    keep = {rect_of(f) for t, a in anims.items() if t not in drop for f in a["frames"]}
    gone = {rect_of(f) for t in drop if t in anims for f in anims[t]["frames"]} - keep
    px = px.copy()
    for x, y, w, h in gone:
        px[y:y + h, x:x + w] = 0
    Ws = px.shape[1]
    total_h = px.shape[0] + sum(f.shape[0] + 1 for fr in new.values() for f, _ in fr)
    occ = np.zeros((total_h, Ws), bool)
    for x, y, w, h in keep:
        occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
    out_px = np.zeros((total_h, Ws, 4), np.uint8)
    out_px[:px.shape[0]] = px
    anims = {t: a for t, a in anims.items()}
    for tag, fr in new.items():
        rows = []
        for f, ms in fr:
            h, w = f.shape[:2]
            ii = np.pad(np.cumsum(np.cumsum(occ.astype(np.int32), 0), 1), ((1, 0), (1, 0)))
            s_ = ii[h:, w:] - ii[:-h, w:] - ii[h:, :-w] + ii[:-h, :-w]       # occupied squares in each h x w box
            free = np.argwhere(s_ == 0)
            if not len(free):
                sys.exit(f"{tag}: no room for a {w}x{h} frame")
            y, x = free[0]
            out_px[y:y + h, x:x + w] = f
            occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
            rows.append({"duration": round(ms / 1000.0, 6), "data": {"x": float(x), "y": float(y), "w": float(w),
                                                                     "h": float(h)}})
        anims[tag] = {"frames": rows}
    used = [rect_of(f) for a in anims.values() for f in a["frames"]]
    H = max(y + h for x, y, w, h in used)
    W = max(x + w for x, y, w, h in used)
    return out_px[:H, :W], anims


def write_sheet(hero, new, drop=TAGS):
    """The run tags into the hero's sheet (place); the fanim keeps every other tag as it was, in its order."""
    stem, an, px = read_sheet(hero)
    order = list(an["anims"])
    sheet, anims = place(px, an["anims"], drop, new)
    for t in drop:                                      # (dropped tags not made again leave the table)
        if t not in new:
            anims.pop(t, None)
    an["anims"] = {t: anims[t] for t in order if t in anims}
    for t in anims:
        if t not in an["anims"]:
            an["anims"][t] = anims[t]
    Image.fromarray(sheet, "RGBA").save(lp(stem + "#sheet.png"), optimize=True)
    with open(lp(stem + "#anim.fanim"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(an, ensure_ascii=False, separators=(",", ":")))
    return sheet.shape[1], sheet.shape[0]


# ================================================================================================== frames
LOOSE = 20              # squares: a piece apart from the figure smaller than this is a crumb a turn left (Pix is ~115)


def finish(rig, can):
    """The composed squares: stray outline squares (a turned corner) gone, the outline closed round what moved, crumbs
    a turn or a wave cut loose dropped."""
    if hasattr(rig, "finish"):
        a = rig.finish(can)
    else:
        a = R.tidy(rig.JX.drop_stray_outline(can.a), rig.outline)
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(a[..., 3] > 0, lab, range(1, n + 1))
        for j in range(1, n + 1):
            if sz[j - 1] < LOOSE:
                a[lab == j] = 0
    return a


def build(hero, n=N_FRAMES, cycle_s=None, only=None):
    run = RUNS[hero]()
    g = Gait(hero, run.rig, run.ppu, n, cycle_s)
    frames = []
    for i in range(n):
        pose = g.pose(i)
        can = run.frame(g, pose, i, only)
        frames.append(finish(run, can))
    return run, g, frames


def review(hero, out_dir, n=N_FRAMES, cycle_s=None, legs=False):
    run, g, frames = build(hero, n, cycle_s)
    rows = [frames]
    if legs:                                            # the legs alone under the frames (to read their poses)
        rows.append(build(hero, n, cycle_s, only=())[2])
    os.makedirs(out_dir, exist_ok=True)
    pad = 50
    allop = np.stack([f[..., 3] > 0 for f in frames]).any(0)
    ys, xs = np.nonzero(allop)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    gy = int(run.rig["ground"]) + pad
    z = 4
    grid = []
    for fr in rows:
        tiles = []
        for f in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            dr = ImageDraw.Draw(bg)
            dr.line([(0, gy - y0), (x1 - x0, gy - y0)], fill=(70, 86, 70, 255))
            tiles.append(bg.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
        grid.append(tiles)
    tw, th = grid[0][0].width, grid[0][0].height
    sheet = Image.new("RGB", (n * (tw + 6), len(grid) * (th + 6)), (40, 40, 40))
    for r, tiles in enumerate(grid):
        for i, t in enumerate(tiles):
            sheet.paste(t, (i * (tw + 6), r * (th + 6)))
    sheet.save(os.path.join(out_dir, f"{hero}_run_new.png"))
    tiles = grid[0]
    gif = [t.convert("RGB").quantize(255) for t in tiles]
    gif[0].save(os.path.join(out_dir, f"{hero}_run_new.gif"), save_all=True, append_images=gif[1:],
                duration=g.ms, loop=0)
    print(f"{hero}: {n} frames of {g.ms[0]} ms ({g.cycle_s:.3f} s), stride x{g.stride:.2f}, scale {g.s:.3f} sq/px, "
          f"hip middle {g.h_mid:.1f}")
    for i in range(n):
        p = g.pose(i)
        print(f"  {i}: ph {p['ph']:.3f} dy {p['dy']:+.1f} dx {p['dx']:+.1f} " + " ".join(
            f"{k}: sole ({v[2][0]:.1f},{v[2][1]:.1f}) knee ({v[1][0]:.1f},{v[1][1]:.1f})" for k, v in p["legs"].items()))


def pinholes(a, most=3):
    """Labels of the enclosed clear holes of at most `most` squares."""
    op = a[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    return [lab == j for j in range(1, n + 1) if (lab == j).sum() <= most]


def filled(a, most=3):
    """Pinholes filled with the commonest colour round them (ppu_rig.tidy's way) - for a hero whose design has none:
    the downscale to the UI's density (ppu_hd.add_lo) leaves one where two edges come within a square."""
    out = a.copy()
    for h in pinholes(a, most):
        ring = ndimage.binary_dilation(h, structure=np.ones((3, 3))) & (out[..., 3] > 0)
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[h, :3] = cols[cnt.argmax()]
        out[h, 3] = 255
    return out


def outlined(hero, frames, kind):
    """The hero's outline round the frames as its other frames have it: grown to KEEP squares (thin_outline.json,
    the restyle's edge did it for the rest - the design's own outline is a square thinner); thin_outline.py then
    finds nothing to change (or only what it changes everywhere)."""
    import thin_outline as T
    with open(lp(T.STATE), encoding="utf-8") as f:
        st = json.load(f)[f"league_{hero}"]
    oc, keep, colour = st["outline"], st[kind]["keep"], st["grow"]
    out = []
    for a in frames:
        b = T.grow_ring(a, oc, keep, colour)[0]
        # a notch's mouth or an opening (the inside of a curl) the new ring closed down to a pinhole inside the
        # figure: outline, as the ring round it - the drawing's own pinholes (league_jinx's design has some) stay
        ah = ndimage.binary_fill_holes(a[..., 3] > 0) & ~(a[..., 3] > 0)
        al, an_ = ndimage.label(ah)
        before = np.zeros(ah.shape, bool)
        for j in range(1, an_ + 1):
            if (al == j).sum() <= 6:
                before |= al == j
        op = b[..., 3] > 0
        lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
        for j in range(1, n + 1):
            h = lab == j
            if h.sum() <= 6 and not (h & before).any():
                b[h, :3] = colour
                b[h, 3] = 255
        out.append(b)
    return out


def export(hero, n=N_FRAMES, cycle_s=None, dry=False):
    """The run tags made and written (unless dry) -> {"run", "hd_run", "lo_run": frames, "ms", "gait", "pivot"}."""
    run, g, frames = build(hero, n, cycle_s)
    pad = (frames[0].shape[0] - run.d.shape[0]) // 2
    pivot = pivot_of(hero, run.d)
    drawn, size = dense_frames(frames, pad, pivot, run.ppu)
    dense = outlined(hero, drawn, "hd")
    ones = one_frames(hero, dense, size, run.ppu)
    lo = outlined(hero, lo_frames(hero, ones, dense, g.ms), "lo")
    if not pinholes(idle_frame(hero)):                  # (a hero whose standing frame has no pinholes: none here)
        lo = [filled(a) for a in lo]
        ones = [filled(a) for a in ones]
    out = {"run": ones, "hd_run": dense, "lo_run": lo, "ms": g.ms, "gait": g, "pivot": pivot}
    if dry:
        return out
    write_strips(hero, dense, run.ppu, orig=drawn)
    w, h = write_sheet(hero, {t: list(zip(out[t], g.ms)) for t in TAGS})
    print(f"league_{hero}#sheet.png {w}x{h}: run / hd_run / lo_run {n} frames of {g.ms[0]} ms "
          f"(1x {ones[0].shape[1]}x{ones[0].shape[0]}, hd {dense[0].shape[1]}x{dense[0].shape[0]}, "
          f"lo {lo[0].shape[1]}x{lo[0].shape[0]})")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["motion", "build", "parts"])
    ap.add_argument("--hero", action="append", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--review")
    ap.add_argument("--frames", type=int, default=N_FRAMES)
    ap.add_argument("--cycle", type=float)
    ap.add_argument("--legs", action="store_true", help="--review: the legs alone in a second row")
    ap.add_argument("--dry", action="store_true", help="make the frames, write nothing")
    a = ap.parse_args()
    for hero in a.hero:
        if a.what == "motion":
            m = extract(hero, a.lol)
            write_motion(hero, m)
            print(f"{hero}: {m['clip']} {SAMPLES} samples over {m['cycle_s']:.3f} s -> {motion_path(hero)}")
        elif a.what == "parts":
            RUNS[hero]().parts_png(os.path.join(a.review or ".", f"{hero}_run_parts.png"))
        elif a.review:
            review(hero, a.review, a.frames, a.cycle, a.legs)
        else:
            export(hero, a.frames, a.cycle, a.dry)


if __name__ == "__main__":
    main()
