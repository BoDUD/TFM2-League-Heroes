#!/usr/bin/env python3
"""league_cassiopeia's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧就参照塔姆
那种方法做吧 做好后自己review 真正没问题了完美了喊我review」).

    python tools/art/rig_cassiopeia.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_cassiopeia.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_cassiopeia.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_cassiopeia.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design: Codex's step-1 take A-2 read back on its own 15 px grid and brought to 57 rows crest tip to ground by whole
rows / columns (tools/art/design_cassiopeia_cut.py; the user: 「44 ppu1.3 A」 -> PPU 1.3, 44 game rows), 64 x 57
squares; the two fangs put back by hand (FANGS: the read-back lost them). She has no legs: the upper body (the hood, the
face, the torso, the belt and its two gold hook-fins) sits on the snake's body - a neck rising from the coil (columns
NECK_X on, above NECK_BASE) and the flat tail lying out behind her to the image left.
Every pose is lossless (memory no-deformation-lossless-poses): parts cut square by square from the design and only
moved by whole squares; what changes length is made of the design's own lines repeated or dropped whole:
  * the neck rises (lift) by repeating its row NECK_SPLIT and sinks (sink) by dropping rows above it - the snake's body
    stretching up or settling into its coil;
  * the neck bends forward (bend) by moving its rows whole, more at the top (a snake leaning in, League's casts);
  * the flat tail's columns are lifted whole (the tip's sway, the run's wave);
  * an arm reaches (reach) by repeating its wrist column (FAR_WRIST / NEAR_WRIST): the claw goes out on a longer
    forearm and never leaves it (Gangplank's lesson: no hand moved off its forearm).
Parts: the near arm (image left: the upper arm's band, the blue-gem bracelet, the gold claw), the far arm (image right:
the forearm and the gold claw in front of her), the upper body, the lower body (neck + tail).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "cassiopeia"
PPU = 1.3
SRC = os.path.join(R.ROOT, "assets", "source", "cassiopeia", "hd")
P = 40                                          # padding round a design-sized layer


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign:
    """What ppu_rig.Rig needs of a design: the squares, the standing point, the outline colour."""
    TURN_PAD = P

    def __init__(self, d, px):
        self.hero, self.ppu = HERO, PPU
        self.d = d
        self.d0 = d.copy()
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = px
        self.outline = PD.edge_colour(d)
        self.parts, self.order, self.props = {}, [], set()

    def box(self, y0, y1, x0, x1):
        m = np.zeros((self.H, self.W), bool)
        m[max(0, y0):y1 + 1, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

    def part(self, name, m):
        for k in self.parts:
            self.parts[k] &= ~m
        self.parts[name] = m.copy()
        if name not in self.order:
            self.order.append(name)

    def rest(self):
        m = self.d[..., 3] > 0
        for v in self.parts.values():
            m &= ~v
        return m

    def layer(self, name, m=None):
        m = (self.parts[name] if name != "rest" else self.rest()) if m is None else m
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


def pad(a):
    out = np.zeros((a.shape[0] + 2 * P, a.shape[1] + 2 * P, 4), np.uint8)
    out[P:P + a.shape[0], P:P + a.shape[1]] = a
    return out


def classes(d, cols):
    m = np.zeros(d.shape[:2], bool)
    for c in cols:
        m |= np.all(d[..., :3] == c, axis=-1)
    return m & (d[..., 3] > 0)


# ------------------------------------------------------------------------------------------------- the design's parts
WHITE = (252, 251, 252)
FANGS = {(22, 51): WHITE, (22, 53): WHITE}      # the mouth row: outline, fang, tongue, fang
STAND = 49                                      # the neck's middle column: where she stands
NECK_X = 41                                     # the neck's columns (the coil rising under her) start here
NECK_TOP = 37                                   # the belt's lowest row: the neck starts under it
NECK_SPLIT = 42                                 # the neck's row repeated to lift her, the rows above it dropped to sink
NECK_BASE = 47                                  # under this the coil lies on the ground (a bend moves nothing there)
TAIL_X = 40                                     # the flat tail's columns (lifted whole for the sway and the wave)
FAR_WRIST = 55                                  # the far forearm's column repeated when the far claw reaches out
NEAR_WRIST = 40                                 # (the near arm runs diagonally from the shoulder: no clean wrist column,
                                                #  so it never reaches - repeating column 40 laid a black band)


def design():
    d = load("modelA2_cut.png")
    for (y, x), rgb in FANGS.items():
        d[y, x] = (*rgb, 255)
    D = CutDesign(d, px=STAND)
    D.part("near_arm", D.box(25, 36, 29, 40))
    D.part("far_arm", D.box(26, 36, 55, 63))
    rgb = d[..., :3].astype(int)
    gold = (rgb[..., 0] > 120) & (rgb[..., 0] > rgb[..., 1]) & (rgb[..., 1] > rgb[..., 2] + 20) & (d[..., 3] > 0)
    dark = classes(d, [tuple(PD.edge_colour(d))])
    box = D.box(38, 43, 36, 43) | D.box(38, 43, 52, 58)
    fins = box & (gold | (dark & ndimage.binary_dilation(gold & box, structure=np.ones((3, 3)))))
    D.part("upper", D.box(0, NECK_TOP, 0, D.W - 1) & ~D.parts["near_arm"] & ~D.parts["far_arm"] | fins)
    D.part("lower", D.rest())
    return D


TINT = {"near_arm": (60, 120, 255), "far_arm": (0, 220, 120), "upper": (255, 220, 0), "lower": (255, 0, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# ------------------------------------------------------------------------------------------------- lossless operations
def neck(layer, lift=0, bend=0):
    """The lower body's neck (columns NECK_X on, rows above NECK_BASE) lifted `lift` rows by repeating row NECK_SPLIT
    (negative: sunk, the rows above it dropped), then bent `bend` columns forward at the top (each row moved whole,
    nothing at NECK_BASE)."""
    out = layer.copy()
    x0 = P + NECK_X
    split = P + NECK_SPLIT
    if lift > 0:
        src = layer[:, x0:].copy()
        out[:split, x0:] = 0
        out[:split - lift, x0:] = src[lift:split]
        for k in range(lift):
            out[split - lift + k, x0:] = src[split]
    elif lift < 0:
        k = -lift
        src = layer[:, x0:].copy()
        out[:split, x0:] = 0
        out[k:split, x0:] = src[:split - k]
    if bend:
        cur = out.copy()
        top = P + NECK_TOP - max(0, lift)
        base = P + NECK_BASE
        for y in range(0, base):
            t = 1.0 if y <= top else (base - y) / (base - top)
            s = int(round(bend * t))
            if not s:
                continue
            row = cur[y, x0:].copy()
            out[y, x0:] = 0
            if s > 0:
                out[y, x0 + s:] = row[:-s]
            else:
                out[y, x0:s] = row[-s:]
    return out


def tail_lift(layer, lifts):
    """Columns of the flat tail (left of TAIL_X) lifted whole by lifts[x] rows (>= 0: nothing goes under the ground)."""
    out = layer.copy()
    for x in range(TAIL_X):
        k = int(lifts[x])
        if k <= 0:
            continue
        c = P + x
        col = layer[:, c].copy()
        out[:, c] = 0
        out[:-k, c] = col[k:]
    return out


def tip(k):
    """The tail's tip lifted k rows, falling off to nothing at column 30."""
    return [max(0.0, k * (30 - x) / 30) for x in range(TAIL_X)]


def wave(phase, amp=2, length=32):
    """The run's travelling wave along the flat tail: up to `amp` rows, none where the tail meets the coil."""
    out = []
    for x in range(TAIL_X):
        w = 1.0 if x < 22 else max(0.0, (TAIL_X - 2 - x) / (TAIL_X - 24))
        out.append(round(amp * (1 - math.cos(2 * math.pi * x / length + phase)) / 2 * w))
    return out


def reach(layer, k, wrist, side):
    """An arm reaching out k squares (side +1: to the image right, -1: left) on a forearm lengthened by repeating its
    wrist column; negative k pulls the claw in (wrist columns dropped)."""
    if not k:
        return layer
    out = np.zeros_like(layer)
    w = P + wrist
    col = layer[:, w].copy()          # the repeated column: the forearm and one outline square above and below it
    lit = np.nonzero((col[:, 3] > 0) & (col[:, :3].astype(int).sum(-1) >= 70))[0]
    if len(lit):
        keep = np.zeros(len(col), bool)
        keep[max(0, lit.min() - 1):lit.max() + 2] = True
        col[~keep] = 0
    if side > 0:
        out[:, :w] = layer[:, :w]
        if k > 0:
            out[:, w + k:] = layer[:, w:-k]
            for i in range(k):
                out[:, w + i] = col
        else:
            out[:, w:k] = layer[:, w - k:]
    else:
        out[:, w + 1:] = layer[:, w + 1:]
        if k > 0:
            out[:, :w + 1 - k] = layer[:, k:w + 1]
            for i in range(k):
                out[:, w - i] = col
        else:
            out[:, -k:w + 1] = layer[:, :w + 1 + k]
    return out


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.ref_holes = None

    def pose(self, whole=(0, 0), lift=0, bend=0, tail=None, far=0, near_at=(0, 0), fill=True):
        """whole: the whole figure moved; lift: rows the neck rises (negative: sinks); bend: columns the neck's top
        leans forward (the upper body goes with it); tail: per-column lifts of the flat tail; far: squares the far claw
        reaches out (negative: drawn in); near_at: the near arm moved whole against the shoulder (at most a square;
        never out to the left: a slit of air opened between it and the torso)."""
        if near_at[0] < 0 or max(abs(near_at[0]), abs(near_at[1])) > 1:
            raise ValueError("the near arm moves at most a square, never out from the body (a see-through slit opens)")
        wx, wy = whole
        L = self.L
        low = neck(L["lower"], lift, bend)
        if tail is not None:
            low = tail_lift(low, tail)
        ux, uy = wx + bend, wy - lift
        layers = [(low, dict(dx=wx, dy=wy)),
                  (reach(L["far_arm"], far, FAR_WRIST, +1), dict(dx=ux, dy=uy)),
                  (L["upper"], dict(dx=ux, dy=uy)),
                  (L["near_arm"], dict(dx=ux + near_at[0], dy=uy + near_at[1]))]
        can = R.compose(self.rig, layers)
        return self.close_holes(can) if fill else can

    def lying(self, sink=9, dx=4, dy=4, tail=None):
        """Dead, fallen forward: the neck sunk `sink` rows into the coil and the upper body (with the far arm; the near
        arm lies under her) turned a quarter clockwise about the top of the neck, face down on the ground in front."""
        L = self.L
        low = neck(L["lower"], -sink, 0)
        if tail is not None:
            low = tail_lift(low, tail)
        up = np.zeros_like(L["upper"])
        for k in ("far_arm", "upper"):
            m = L[k][..., 3] > 0
            up[m] = L[k][m]
        can = R.compose(self.rig, [(low, dict())])
        top = R.compose(self.rig, [(up, dict(dy=sink))])
        about = (self.rig.ox + STAND + 0.5, self.rig.oy + NECK_TOP + sink)
        R.put(can, top, rot=3, about=about, dx=dx, dy=dy)
        can[self.rig.GY:] = 0
        return can

    MOST = 10

    def close_holes(self, can):
        """Small enclosed holes the idle does not have filled from the squares round them (rig_jarvaniv's way)."""
        if self.ref_holes is None:
            idle = self.pose(fill=False)
            op = idle[..., 3] > 0
            self.ref_holes = ndimage.binary_dilation(ndimage.binary_fill_holes(op) & ~op, iterations=2)
        op = can[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op & ~self.ref_holes
        lbl, n = ndimage.label(holes)
        fill = np.zeros_like(holes)
        for k in range(1, n + 1):
            m = lbl == k
            if m.sum() <= self.MOST:
                fill |= m
        if not fill.any():
            return can
        out = R.fill_under(can, fill)
        left = fill & (out[..., 3] == 0)
        if left.any():
            src = (out[..., 3] > 0) & (out[..., :3].astype(int).sum(-1) >= 70)
            _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
            out[left] = out[iy[left], ix[left]]
        return out


def form():
    return Form(design(), rig_pad=(30, 40, 30, 20))


def sheet(cans, path, z=4):
    allc = np.stack(cans)
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    tiles = []
    for c in cans:
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(c[y0:y1, x0:x1]))
        tiles.append(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
    out = Image.new("RGB", (sum(t.width + 6 for t in tiles), tiles[0].height), (40, 40, 40))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + 6
    out.save(lp(path))


def tries(F):
    p = F.pose
    return [p(), p(lift=3), p(lift=-4), p(bend=3), p(far=3), p(near_at=(0, -1)), p(tail=tip(2)), p(tail=wave(0))]


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_cassiopeia.py) come from these
MS = {"idle": [150] * 8, "run": [90] * 8, "attack": [70, 70, 90, 90, 80], "skill": [70, 70, 90, 90, 80],
      "skill2": [70, 80, 90, 100, 110], "ult": [120, 130, 150, 150], "hit": [100, 100],
      "dead": [100, 110, 120, 150, 200, 500]}


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}
    # idle: the neck settles a row into the coil and rises again, the tail's tip lifting a little after it
    out["idle"] = [p(lift=-c, tail=tip(k)) for c, k in zip([0, 0, 1, 1, 1, 1, 0, 0], [0, 1, 2, 2, 1, 0, 0, 0])]
    # E Twin Fang (League's cassiopeia_attack1 / spell3: a flick of the front claw): drawn back (the neck leaning back a
    # column, the claw pulled in), the flick - the neck leaning in, the far claw thrust out (frame 3: the fang leaves),
    # held, back
    out["attack"] = [p(bend=-1, far=-1), p(bend=1, far=1), p(bend=2, far=3), p(bend=2, far=3), p(bend=1, far=1)]
    # Q Noxious Blast (League's cassiopeia_spell1: she rears up tall and flings a hand down at the spot): rising tall,
    # the claw drawn in and the near arm raised, the fling down and forward (frame 3), held, settling
    out["skill"] = [p(lift=3, far=-1, near_at=(0, -1)), p(lift=4, bend=-1, far=-1, near_at=(0, -1)),
                    p(lift=1, bend=3, far=3), p(lift=1, bend=3, far=3), p(lift=0, bend=1, far=1)]
    # W Miasma (League's cassiopeia_spell2: both arms swept wide, the clouds flung): rising with the claws drawn in,
    # both flung wide and up (frame 3: the near arm out a square, the far claw out), held, settling
    out["skill2"] = [p(lift=1, far=-1, near_at=(1, 0)), p(lift=3, far=1, near_at=(0, -1)),
                     p(lift=4, far=3, near_at=(0, -1)), p(lift=3, far=3, near_at=(0, -1)), p(lift=1, far=1)]
    # R Petrifying Gaze (League's cassiopeia_spell4: rearing up and back, then lunging low at them with the gaze):
    # reared up and back with both claws drawn in, the lunge low and far forward (frame 3: the gaze leaves), held
    out["ult"] = [p(lift=4, bend=-2, far=-1, near_at=(1, 0)), p(lift=2, bend=1, far=1),
                  p(lift=-2, bend=4, far=3, near_at=(0, 0)), p(lift=-2, bend=4, far=3, near_at=(0, 0))]
    out["hit"] = [R.flash(p(whole=(-2, 0), bend=-1)), p(whole=(-1, 0))]
    # the death (League's cassiopeia_death: she sinks and falls forward): flinch back, settling down the neck row by
    # row while tipping forward, fallen face down in front of her coil (the tail's tip dropping), still

    def ground(can):
        out_ = can.copy()
        out_[rig.GY:] = 0
        return out_
    fallen = F.lying()
    out["dead"] = [p(bend=-1, whole=(-1, 0), tail=tip(1)), p(lift=-3, bend=1, tail=tip(1)),
                   ground(p(lift=-6, bend=3)), ground(p(lift=-8, bend=4, far=-1)), fallen, fallen.copy()]
    return out


def walk(F):
    """The run (League's cassiopeia_run: she leans in and the tail swims behind her): a wave travelling back along the
    flat tail over 8 frames, the neck leaning in a column and bobbing a row with each half wave."""
    out = []
    for i in range(8):
        ph = -2 * math.pi * i / 8
        out.append(F.pose(bend=1, lift=(0, 0, 1, 1, 0, 0, 1, 1)[i], tail=wave(ph)))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": walk(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def audit(F, acts, out_dir):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), new enclosed holes, colours in no design,
    outline squares with no colour beside them (rig_jarvaniv.audit); each tag at 6x."""
    from PIL import ImageDraw
    os.makedirs(lp(out_dir), exist_ok=True)
    rig = F.rig
    allowed = {tuple(c) for c in F.D.d[F.D.d[..., 3] > 0][:, :3].tolist()} | {tuple(F.D.outline)}
    idle = rig.finish(acts["idle"][0][0])
    iop = idle[..., 3] > 0
    idark = iop & (np.abs(idle[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
    base_orphan = int((idark & ~ndimage.binary_dilation(iop & ~idark, structure=R.CROSS)).sum())
    idle_holes = ndimage.binary_fill_holes(iop) & ~iop
    bad = 0
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            f = rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(idle_holes, iterations=3)
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - allowed
            dk = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
            flag = len(sz) != 1 or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
            bad += bool(flag)
            print(f"{tag:10s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}{'  <--' if flag else ''}")
            show = f.copy()
            if n > 1:
                big = 1 + int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1))))
                show[(lbl > 0) & (lbl != big)] = (255, 0, 0, 255)
            show[new] = (255, 0, 255, 255)
            show[orphan] = (255, 128, 0, 255)
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
            audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    tinted(D).save(os.path.join(a.parts, f"{HERO}_parts.png"))
    print({k: int(v.sum()) for k, v in D.parts.items()})
    F = form()
    idle = F.pose()
    ref = F.rig.canvas()
    ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
    print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
    t = [F.rig.finish(c) for c in tries(F)]
    sheet(t[:4], os.path.join(a.parts, f"{HERO}_tries1.png"), z=5)
    sheet(t[4:], os.path.join(a.parts, f"{HERO}_tries2.png"), z=5)


if __name__ == "__main__":
    main()
