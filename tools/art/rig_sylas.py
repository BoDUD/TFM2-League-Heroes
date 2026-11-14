#!/usr/bin/env python3
"""league_sylas's action frames: the approved 3/4 design (idle) and Codex's skeleton poses (every action), timed after
League's own clips (the user, 2026-10-20: 3/4 only, 「Codex 照骨架画关键姿势」).

    python tools/art/rig_sylas.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_sylas.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_sylas.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/review_sylas_actions.py --out DIR   # League left / ours right, one GIF

The design (tools/art/design_sylas_model.py: Codex's step-1 take A-1 read back to 65 x 46 = 38 game px at PPU 1.2;
Codex's own face): League's idle seen 3/4 from the front-right - feet planted apart, the manacled fists hanging at his
sides, the gold chains down to the ground and trailing out on both sides.
The idle breathes on the design itself (the upper body, chains included, sets down a row onto the legs and comes back:
League's Sylas_Idle). Every action is Codex's poses (tools/art/design_sylas_poses.py: sixteen of League's frames drawn
on skeletons at the design's segment lengths, read back at the design's scale with the design's own head on each) - the
wind-up, the lash, the whirl, the leap, the stab, the slam, the dash, the throw, the pull, the stagger, the kneel, the
fall and four run frames - each placed with the middle of its trousers on the design's and its lowest row on the ground
(or `lift` rows over it in the air), moved by whole squares only: then `whole` keeps the body (all but the chains) over
his standing point as the idle's is (its middle 2 squares behind it), a few squares forward in the lunges and the pull
(a kneeling or lunging pose's trousers reach far back, so its middle alone would put the body ahead).
The in-betweens (2026-11-14): CHAIN waves a trailing chain by its columns (the run, E's dash and pull, the stolen ult's
leap); HELD moves the chains on in the second frame of a pose shown twice running (by rows, a bow, columns or a slide
along the floor, their ends kept: the attack, Q, W, E's and R's throw, the stolen ult's slam, the death).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inbetween as IB  # noqa: E402
import ppu_rig as R  # noqa: E402
from rig_warwick import close_cracks  # noqa: E402
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "sylas"
PPU = 1.2
SRC = os.path.join(R.ROOT, "assets", "source", "sylas", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


STAND = 37                     # the column between his feet: the standing point
WAIST = 27                     # the last row of the upper body (the belt's top): the idle's breath sets it down


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("upper", D.box(0, WAIST, 0, D.W - 1))
    D.part("lower", D.rest())
    return D


def trousers(d):
    """The dark teal trousers' squares (and the scarf's, above): green and blue over red, dark."""
    rgb = d[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (d[..., 3] > 0) & (g > r + 8) & (b > r + 8) & (r < 100) & (g < 140)


def trousers_mid(d):
    """The middle column of a figure's trousers (the lower 60% of the figure: the scarf left out)."""
    m = trousers(d)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    m[:ys.min() + int(0.4 * (ys.max() - ys.min()))] = False
    xs = np.nonzero(m)[1]
    return (xs.min() + xs.max() + 1) / 2


# The run in eight frames (2026-11-14, the user: 「有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): each of
# Codex's four run poses held for two frames of 75 ms (the legs and the body's height still change every 150 ms: the
# same bob) while the chain trailing from his far fist swings - a wave travelling down it to its tip: its whole columns
# left of CHAIN (where it hangs from the fist: the columns from there on stay) lifted AMP t sin(step x 45 deg - pi t)
# rows, t from 0 there to 1 at its tip (the picture's left edge), the step going on frame by frame, so all eight
# frames differ (rig_aurelionsol's travelling(), his tail's). Everything but the chain is checked unchanged.
# The same wave gives the one-drawing actions their frames: Abduct's pull (the chain trailing low behind him) and the
# leaps of the stolen ult (the chain flung up behind him). CHAIN: pose -> (that column, the rows the chain's squares
# lie in there - the pull's trailing foot is above them).
CHAIN = {"run1": (14, 0, 99), "run2": (14, 0, 99), "run3": (14, 0, 99), "run4": (14, 0, 99),
         "pull": (18, 28, 99), "leap": (14, 0, 20), "dash": (22, 0, 26)}
AMP = 4
VPAD = 8


def travelling(shape, x0, x1, amp, phase, beats=0.5):
    """The moves of a wave travelling down a trailing chain: its whole columns lifted amp t sin(phase - 2 pi beats t)
    rows, t from 0 at column x1 (where it hangs from him) to 1 at its tip (column x0). -> (dx, dy) arrays."""
    H, W = shape[:2]
    dy = np.zeros((H, W), int)
    for x in range(W):
        t = min(max((x1 - x) / (x1 - x0), 0.0), 1.0)
        dy[:, x] = -int(round(amp * t * np.sin(phase - 2 * np.pi * beats * t)))
    return np.zeros((H, W), int), dy


def chain_waved(d, name, step, outline):
    """A pose picture (on a canvas VPAD bigger on every side) with its trailing chain - every square left of
    CHAIN[name] in its rows, the chain alone there - at `step` of the travelling wave, behind the rest of him."""
    x1, y0, y1 = CHAIN[name]
    m = np.zeros(d.shape[:2], bool)
    m[y0:y1 + 1, :x1 + 1] = d[y0:y1 + 1, :x1 + 1, 3] > 0
    dx, dy = travelling(d.shape, 0, x1, AMP, step * np.pi / 4)
    out = IB.repose(d, [(m, (dx, dy), "under")], outline, pad=VPAD)
    if not IB.kept(d, out, VPAD, but=m):
        sys.exit(f"{name} chain step {step}: the wave changed him outside the chain")
    return out


# The held pairs (2026-11-14, the user: 「有的动画感觉只有一帧 不如oppi的地方都要补」「能改就想办法改 全都要改」): where
# an action shows one of Codex's poses twice running (the same picture, or the same moved a square), the second frame
# has his chains moving on. Those chains hang from the manacles or lie on the floor, where CHAIN's column wave would
# tear them off the manacle or lift them off the floor, so HELD moves each by whole squares with its ends kept:
#   "rows" (a, b, amp): its rows shifted amp t^2 columns, t 0 at row a (next to the manacle: the squares there stay)
#          to 1 at row b (the free end) - a hanging chain swinging on;
#   "bow"  (a, b, amp): its rows shifted amp sin(pi t) between rows a and b - a chain hanging from the manacle down to
#          the floor, both ends where they were;
#   "cols" (a, b, amp): its columns lifted amp t^2 rows, t 0 at column a to 1 at column b - a chain flung out level;
#   "slide" (amp,): all of it moved amp columns along the floor, toward the manacle, in under the end that stays there.
# A chain is its golds inside the box and only the outline squares that edge nothing else (Pantheon's cape's way: a leg,
# a manacle or an arm in the box keeps its own outline); everything else is checked unchanged. Behind the rest of him.
HELD = {
    # the wind-up's second frame (a square further back): both hanging chains lag, swinging forward
    "wind": [((38, 23, 51, 42), "rows", (23, 41, 2)), ((0, 11, 13, 33), "rows", (11, 32, 2))],
    # the lash held: the chain flung ahead sags at its hook, the one trailing behind swings further back
    "lash": [((50, 5, 61, 22), "cols", (50, 61, -2)), ((0, 17, 12, 31), "rows", (17, 30, -2))],
    # the stab held: both chains swing on forward
    "stab": [((48, 19, 61, 28), "rows", (20, 27, 3)), ((36, 23, 53, 33), "rows", (23, 32, 2))],
    # the throw held (R's steal, E's Abduct): the thrown chain swings on forward, the near one back
    "throw": [((43, 17, 65, 34), "rows", (17, 33, 3)), ((0, 15, 14, 36), "rows", (15, 36, -3))],
    # the slam held (Q, the stolen ult): the chains on the floor drawn back toward him
    "slam": [((47, 29, 57, 39), "slide", (-2,)), ((25, 32, 46, 41), "slide", (-2,))],
    # the death: staggering back, the chains hanging to the floor bow; on his knees and face down, they are dragged in
    "stagger": [((8, 33, 17, 44), "bow", (34, 44, 2)), ((37, 33, 46, 45), "bow", (34, 45, 2))],
    "kneel": [((0, 29, 24, 37), "slide", (2,)), ((50, 29, 58, 37), "slide", (-2,))],
    "lie": [((20, 15, 38, 22), "slide", (2,))],
}


def gold(d):
    """The chains' golds, their darkest brown included (not the belt's, nor the skin's)."""
    c = d[..., :3].astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return (d[..., 3] > 0) & (r >= 55) & (b <= 20) & (r >= g + 15) & (g >= 35)


def chain_in(d, box, grow=3):
    """The golds in the box (x0, y0, x1, y1) and the outline squares there that touch them and edge nothing else (grown
    `grow` deep while that holds)."""
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    inbox = IB.cut(d.shape, boxes=[box])
    dark = (d[..., 3] > 0) & (IB.lum(d[..., :3]) < IB.DARK)
    other = ndimage.binary_dilation((d[..., 3] > 0) & ~gold(d) & ~dark, structure=cross)
    m = gold(d) & inbox
    for _ in range(grow):
        add = dark & inbox & ~m & ~other & ndimage.binary_dilation(m, structure=cross)
        if not add.any():
            break
        m |= add
    return m


def held_moved(d, name, outline):
    """A pose picture (on a canvas VPAD bigger on every side) with its chains moved on as HELD[name] says."""
    H, W = d.shape[:2]
    moves, taken = [], np.zeros((H, W), bool)
    for box, how, args in HELD[name]:
        m = chain_in(d, box)
        dx, dy = np.zeros((H, W), int), np.zeros((H, W), int)
        if how in ("rows", "bow"):
            a, b, amp = args
            for y in range(H):
                t = min(max((y - a) / (b - a), 0.0), 1.0)
                dx[y] = int(round(amp * (t * t if how == "rows" else np.sin(np.pi * t))))
        elif how == "cols":
            a, b, amp = args
            for x in range(W):
                t = min(max((x - a) / (b - a), 0.0), 1.0)
                dy[:, x] = -int(round(amp * t * t))
        else:
            dx[:] = args[0]
        moves.append((m, (dx, dy), "under"))
        taken |= m
    out = IB.repose(d, moves, outline, pad=VPAD)
    if not IB.kept(d, out, VPAD, but=taken):
        sys.exit(f"{name} held: the chains' move changed him outside them")
    if IB.audit(out) != IB.audit(IB.padded(d, VPAD)):
        sys.exit(f"{name} held: {IB.audit(out)} (the pose itself: {IB.audit(IB.padded(d, VPAD))})")
    return out


class Form:
    def __init__(self, D, rig_pad=(70, 70, 70, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), crouch=0):
        wx, wy = whole
        can = R.compose(self.rig, [(self.L["lower"], dict(dx=wx, dy=wy)), (self.L["upper"], dict(dx=wx, dy=wy + crouch))])
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def posed(self, name, whole=(0, 0), lift=0, wave=None, held=False):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands: the middle of its trousers on the
        design's, its lowest row on the ground - `lift` rows above it (in the air); `wave`: the trailing chain waved at
        that step of its travelling wave (chain_waved); `held`: the chains moved on (held_moved, the second frame of a
        pose shown twice) - both placed where the pose itself stands."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        top = P + self.D.ground - (ys.max() + 1) - lift
        left = P + int(round(trousers_mid(self.D.d) - trousers_mid(d)))
        if wave is not None:
            d = chain_waved(d, name, wave, tuple(int(v) for v in self.D.outline))
            top, left = top - VPAD, left - VPAD
        elif held:
            d = held_moved(d, name, tuple(int(v) for v in self.D.outline))
            top, left = top - VPAD, left - VPAD
        x0, x1 = max(0, left), min(lay.shape[1], left + d.shape[1])
        y0, y1 = max(0, top), min(lay.shape[0], top + d.shape[0])
        lay[y0:y1, x0:x1] = d[y0 - top:y1 - top, x0 - left:x1 - left]
        can = R.compose(self.rig, [(lay, dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can


def form():
    F = Form(design())
    F.rig.idle_canvas = F.pose()
    return F


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_sylas.py) come from these (a frame's start in ticks = ms x 0.06)
# the run 150 ms a pose (2026-10-22, 「塞拉斯局内也是跑的时候跳动频率太高 和之前奎桑提一个问题」: 110 made a 0.44 s cycle);
# since 2026-11-14 each pose two frames of 75 ms, the trailing chain swinging between them (CHAIN) - the bob unchanged
MS = {"idle": [150] * 8, "run": [75] * 8,
      "attack": [80, 80, 70, 90, 110],            # the lash from 160 ms: a_rel 10
      "attack_p": [100, 100, 150, 150],           # the whirl from 100 ms: p_rel 7
      "skill_w": [100, 120, 140, 140],            # the stab from 100 ms: w_rel 7
      "skill": [110, 130, 130, 130],              # the slam from 110 ms: q_rel 7
      "skill2": [90, 90, 130, 130, 127],          # the dash (7 ticks), the throw from 180 ms (the chain at tick 13)
      "skill2_pull": [150, 150],
      "ult": [100, 150, 120, 130],                # the throw from 100 ms: r_rel 7
      "ult_cast": [150, 120, 150, 100, 80],       # the slam from 270 ms: r2_rel 17
      "ult_dash": [80, 80, 80, 80],
      "hit": [100, 100],
      "dead": [120, 140, 160, 200, 160, 600]}


def frames_all(F):
    p, q = F.pose, F.posed
    out = {}
    # idle (League's Sylas_Idle: a slow breath, the chains swaying a little): the upper body sets down a row and back
    out["idle"] = [p(crouch=c) for c in (0, 0, 0, 1, 1, 1, 1, 0)]
    # run (League's Sylas_Run: an upright run, the arms pumping, the chains trailing): Codex's four run frames, the body
    # one square higher on the passing frames (run2 / run4 drawn so); each held two frames, the trailing chain swinging
    # (CHAIN: a wave travelling down it, a step a frame)
    out["run"] = [q(f"run{k // 2 + 1}", wave=k) for k in range(8)]
    # auto attack (League's Sylas_Attack_01: leaning back with the near arm swung behind him, then lunging forward
    # with the far arm and its chain flung ahead): wind-up, the lash (the hit), held, back; the second frame of the
    # wind-up and of the lash with the chains moving on (HELD)
    out["attack"] = [q("wind"), q("wind", whole=(-1, 0), held=True), q("lash", whole=(-3, 0)),
                     q("lash", whole=(-3, 0), held=True), p()]
    # Petricite Burst (League's Sylas_Attack_Passive: wound up, then the chains whirled round him in a wide crouch)
    out["attack_p"] = [q("wind"), q("spin"), q("spin", whole=(1, 0)), p()]
    # W Kingslayer (League's Sylas_Spell2: a leap with the manacles raised, then the stab forward on landing)
    # (the stab's second frame: the chains swinging on, HELD)
    out["skill_w"] = [q("leap", lift=4), q("stab", whole=(-5, 0)), q("stab", whole=(-5, 0), held=True), p(whole=(1, 0))]
    # Q Chain Lash (League's Sylas_Spell1_Cast: up with the manacles raised, then down on one knee slamming them into
    # the ground in front)
    # (the slam's second frame: the chains on the floor drawn back toward him, HELD)
    out["skill"] = [q("leap", lift=3), q("slam", whole=(-8, 0)), q("slam", whole=(-8, 0), held=True), p()]
    # E Abscond (League's Sylas_Spell3_Dash: rushing forward low, the chains streaming) then Abduct (Sylas_Spell4_Cast-
    # like: planted, the far arm thrust forward with the chain); the dash's second frame (one drawing a square on until
    # 2026-11-14) has both streaming chains whipping behind him (CHAIN: the wave's step 6, the tips 4 rows up); the
    # throw's second frame the chains swinging on (HELD, as R's)
    out["skill2"] = [q("dash", whole=(5, 0)), q("dash", whole=(6, 0), wave=6), q("throw"), q("throw", held=True), p()]
    # Abduct's pull (League's Sylas_Spell3_Bhit_Cast: flying forward level after his chain)
    # (the trailing chain's tip swung down, then up: CHAIN)
    out["skill2_pull"] = [q("pull", whole=(-6, 0), lift=3, wave=2), q("pull", whole=(-6, 0), lift=2, wave=6)]
    # R Hijack, the steal (League's Sylas_Spell4_Cast: wound back, the far arm thrust forward, back; the thrust's
    # second frame with the chains swinging on: HELD)
    out["ult"] = [q("wind"), q("throw"), q("throw", held=True), p()]
    # R, the stolen ult (League shows the robbed champion's own: here up with the manacles raised and down slamming)
    # (at the top of the leap the chain flung up behind him swings on: CHAIN; the slam's second frame as Q's: HELD)
    out["ult_cast"] = [q("leap", lift=5), q("leap", lift=7, wave=6), q("slam", whole=(-8, 0)),
                       q("slam", whole=(-8, 0), held=True), p()]
    # the add-on's melee stolen ult: the leap onto the champion (the chain flung up behind him swinging: CHAIN)
    out["ult_dash"] = [q("leap", lift=k, wave=s) for k, s in ((5, 0), (7, 2), (7, 4), (4, 6))]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Sylas_Death: struck back, down on his knees, then face down; each pose's second frame with
    # the chains moving on: HELD)
    out["dead"] = [q("stagger"), q("stagger", whole=(-1, 0), held=True), q("kneel", whole=(-6, 0)),
                   q("kneel", whole=(-6, 0), held=True), q("lie", whole=(-7, 0), lift=1),
                   q("lie", whole=(-7, 0), held=True)]
    return out


def frames(F):
    a = frames_all(F)
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = [(c, m) for c, m in zip(cans, ms)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    F = form()
    acts = frames(F)
    if a.audit:
        import rig_wukong as RW
        RW.HERO = HERO
        RW.audit(F, acts, a.audit)
    elif a.review:
        F.rig.review(acts, a.review)
    else:
        F.rig.export(acts)


if __name__ == "__main__":
    main()
