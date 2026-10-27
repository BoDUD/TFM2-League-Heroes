#!/usr/bin/env python3
"""league_syndra redone at PPU 1.86 (the user, 2026-10-27: 「接下来可以重做辛德拉」, 「就用原样 1.86，继续做辛德拉的动作包」):
the design is Codex's picture traced from her sprite read on its own squares (tools/art/design_syndra_hd.py: 54 x 78),
every frame built from it the way her old sheet was built from its idle frame.

Her old sheet (assets/source/syndra/hd/old, main's before the redo) is a rig of idle 1: every frame is that drawing
moved whole (OLD: dy, dx in 1x pixels, read frame by frame - the hover's bob, R's lift, the hit's step back, the death's
sink) with only the far forearm and hand drawn again (four poses: A the hover's top, B raised to the shoulder, C pushed
out at the waist, D over the shoulder; the run's F and G) or the legs (the run's lower leg trailing, the death's legs
folding as she sinks). So here:

- the far arm is Codex's (tools/art/casts_syndra_hd.py reads its nine pose pictures onto the design's squares): the
  design's own far arm (ARM) taken off and the pose's squares in the arm's window (WINDOW) put where the rest of the
  design leaves room, the pose lined up on her body by its torso (align) - the face, the hair and the body stay the
  design's square for square, so nothing flickers;
- the legs are the design's: the run's long lower leg trails back from the knee (TRAIL, rigkit.swing_leg), the death
  sinks her body over her boots (sunk: the boots stay where they hovered, the skirt drawn over them). Codex's leg poses
  (E-I) redrew the skirt as well and would not join the design without a seam.

The idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py. Nothing is baked: the dark
spheres are effects of their own.

    python tools/art/rig_syndra_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_syndra_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero syndra && python tools/art/ppu_hd.py --hero syndra
    python tools/art/ppu_one.py --hero syndra && python tools/art/rig_syndra_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero syndra       # then: the idle / ban-pick reels
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_syndra_hd as CY  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402
import rigkit as K  # noqa: E402

HERO = "syndra"
PPU = CY.PPU
DESIGN_ROWS = 78
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
# Her old frames against idle 1 (each frame's centre on the pivot): (dy, dx) in 1x pixels (up / left negative), the far
# arm's pose (None: the design's) and the leg: ("trail", k) the run's lower leg TRAIL[k], ("sink", 0) the death's
# boots kept while she sinks. Read off the old sheet (the shift that matches her head exactly, the rest of the
# difference only in the arm's or the legs' box).
OLD = {
    "idle_base": [(0, 0, None, None), (-1, 0, None, None), (-1, 0, None, None), (-2, 0, "A", None),
                  (-2, 0, "A", None), (-1, 0, "A", None), (-1, 0, None, None), (0, 0, None, None)],
    "run": [(0, 0, None, None), (-1, 0, None, ("trail", 1)), (-1, 0, "F", ("trail", 2)), (0, 0, "G", ("trail", 3)),
            (0, 0, None, None), (-1, 0, None, ("trail", 1)), (-1, 0, "F", ("trail", 2)), (0, 0, "G", ("trail", 3))],
    "attack": [(0, 0, None, None), (0, -1, "B", None), (0, 1, "C", None), (0, 1, "C", None), (0, 0, None, None)],
    "skill": [(0, 0, "D", None), (-1, 0, "B", None), (0, 1, "C", None), (0, 0, None, None)],
    "skill2": [(0, 1, "C", None), (-1, -1, "B", None), (0, 2, "C", None), (0, 1, "A", None), (0, 0, None, None)],
    "skill2_e": [(0, -1, "A", None), (0, -1, "B", None), (0, 2, "C", None), (0, 0, None, None)],
    "ult": [(-1, 0, "D", None), (-2, 0, "B", None), (-2, 1, "C", None), (-1, 1, "C", None), (0, 0, None, None)],
    "hit": [(0, -2, None, None), (0, -1, None, None)],
    "dead": [(0, -1, None, None), (1, -2, None, ("sink", 0)), (2, -2, None, ("sink", 0)), (3, -2, None, ("sink", 0)),
             (4, -2, None, ("sink", 0)), (4, -2, None, ("sink", 0)), (4, -2, None, ("sink", 0)),
             (4, -2, None, ("sink", 0))],
}
# The design's far arm (image right): rows 37-50 from column 40 out (its root at rows 40-43 from column 38, where the
# hair's outline is), the hand's fingers down to row 53 from column 42
ARM = ((37, 40, 40), (40, 44, 38), (44, 51, 40), (51, 54, 42))
WINDOW = (18, 54, 40)           # a pose's far arm: rows 18-53 from column 40 out (the hair's edge under it with it)
TORSO = (30, 60, 0, 40)         # the window a pose is lined up on her body by (rows, columns: hair, bodice, skirt)
# The run's trailing lower leg: the long (far) boot from its knee down, its toe swung back (columns, - = back)
LEG = (62, 26, 40)              # (knee row, first column, column past)
ANKLE = 70
TRAIL = [0, -2, -4, -3]
# The death: her boots (rows 63 down from column 21: the long skirt panel left of it sinks with her) stay where they hovered, the body sinks over them
BOOTS = (63, 21, 40)


def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(R.lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(R.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.d0 = D.d.copy()
    # the pivot: her old frames' centre column is half a pixel left of her lower toe's middle
    ys, xs = np.nonzero(d[..., 3] > 0)
    toe = xs[ys == ys.max()]
    D.px = int(round((toe.min() + toe.max() + 1) / 2 - 0.5 * PPU))
    return D


def box(shape, rows_cols):
    m = np.zeros(shape[:2], bool)
    for r0, r1, c0 in rows_cols:
        m[r0:r1, c0:] = True
    return m


def align(pic, off):
    """The pose's (dy, dx) onto the design refined from its head's (casts_syndra_hd) to its torso's: the shift within
    3 squares where most of TORSO's squares agree (opaque on both and the same colour)."""
    r0, r1, c0, c1 = TORSO
    d = CY.D0[r0:r1, c0:c1]
    best = None
    for dy in range(off[0] - 3, off[0] + 4):
        for dx in range(off[1] - 3, off[1] + 4):
            p = place(pic, dy, dx, CY.D0.shape)[r0:r1, c0:c1]
            both = (d[..., 3] > 0) & (p[..., 3] > 0)
            same = both & (d[..., :3] == p[..., :3]).all(-1)
            alone = (d[..., 3] > 0) ^ (p[..., 3] > 0)
            score = int(same.sum()) - int(alone.sum())
            if best is None or score > best[0]:
                best = (score, dy, dx)
    return best[1], best[2]


def place(pic, dy, dx, shape):
    """pic's squares at (dy, dx) on a canvas of the design's shape (what falls off it dropped)."""
    out = np.zeros(shape[:2] + (4,), np.uint8)
    ys, xs = np.nonzero(pic[..., 3] > 0)
    Y, X = ys + dy, xs + dx
    ok = (Y >= 0) & (Y < shape[0]) & (X >= 0) & (X < shape[1])
    out[Y[ok], X[ok]] = pic[ys[ok], xs[ok]]
    return out


def arms():
    """{pose: the far arm's squares on the design's grid (a canvas as wide as needed to the right)}."""
    got = CY.read()
    d = CY.D0
    H, W = d.shape[:2]
    shape = (H, W + 20)
    body = np.zeros(shape, bool)
    body[:, :W] = (d[..., 3] > 0) & ~box(d.shape, ARM)
    r0, r1, c0 = WINDOW
    outline = np.array(outline_of(d))
    out = {}
    for lab in "ABCDFG":
        pic, off = got[lab][0], got[lab][1]
        dy, dx = align(pic, off)
        p = place(pic, dy, dx, shape)
        win = np.zeros(shape, bool)
        win[r0:r1, c0:] = True
        free = win & (p[..., 3] > 0) & ~body
        rgb = p[..., :3].astype(int)
        line = (rgb == outline).all(-1)
        hair = (rgb.min(-1) >= 140) & (np.ptp(rgb, -1) <= 60)    # the pose's own hair edge: the design's stays
        fill = free & ~line & ~hair
        lbl, n = ndimage.label(fill, structure=np.ones((3, 3)))
        if n:
            sz = ndimage.sum(fill, lbl, range(1, n + 1))
            fill = np.isin(lbl, [k + 1 for k in range(n) if sz[k] >= 6])
        # the arm's outline: only the pose's outline round the arm (not a second line along the design's hair)
        keep = fill | (free & line & ndimage.binary_dilation(fill, structure=np.ones((3, 3))))
        a = np.zeros_like(p)
        a[keep] = p[keep]
        out[lab] = a
        print(f"arm {lab}: head offset {off}, torso {dy, dx}, {int(keep.sum())} squares")
    return out


def outline_of(d):
    """The design's outline colour: its commonest colour on the figure's edge."""
    op = d[..., 3] > 0
    edge = op & ~ndimage.binary_erosion(op)
    cols, cnt = np.unique(d[edge][:, :3], axis=0, return_counts=True)
    return [int(v) for v in cols[cnt.argmax()]]


def with_arm(D, arm):
    """The design with its far arm taken off and `arm` put on (a canvas 20 squares wider on the right)."""
    d = D.d0
    H, W = d.shape[:2]
    out = np.zeros((H, W + 20, 4), np.uint8)
    out[:, :W] = d
    if arm is None:
        return out
    out[:, :W][box(d.shape, ARM)] = 0
    m = arm[..., 3] > 0
    out[m] = arm[m]
    return out


def trailed(a, k):
    """The long lower leg swung back TRAIL[k] squares at the toe, turned about the knee."""
    if not TRAIL[k]:
        return a
    kr, c0, c1 = LEG
    op = a[..., 3] > 0
    R_, C_ = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    leg = op & (R_ >= kr) & (C_ >= c0) & (C_ < c1)
    rest = a.copy()
    rest[leg] = 0
    return K.put(rest, K.swing_leg(a, leg, kr, ANKLE, TRAIL[k]), 0, 0, under=True)


def sunk(a, rows):
    """The body `rows` squares lower, the boots (BOOTS) left where they were, under it; nothing under her toe."""
    if rows == 0:
        return a
    h = a.shape[0]
    r0, c0, c1 = BOOTS
    op = a[..., 3] > 0
    R_, C_ = np.mgrid[0:h, 0:a.shape[1]]
    boots = op & (R_ >= r0) & (C_ >= c0) & (C_ < c1)
    body = a.copy()
    body[boots] = 0
    out = np.zeros_like(a)
    out[rows:] = body[:h - rows]
    feet = np.zeros_like(a)
    feet[boots] = a[boots]
    return K.put(out, feet, 0, 0, under=True)


def frame(D, arm_pics, dy, dx, pose, leg):
    a = with_arm(D, None if pose is None else arm_pics[pose])
    if leg and leg[0] == "trail":
        a = trailed(a, leg[1])
    up, side = round(dy * PPU), round(dx * PPU)
    if leg and leg[0] == "sink":
        a = sunk(a, up)
        up = 0
    return a, side, up


def sealed(can, outline):
    """Every edge of the figure outlined, as the design's is: a near-black square on the edge (Codex's arm drew its top
    edge in the sleeve's darkest shade) made the outline, any other square on the edge (the pose's arm where its line
    was open, the sunk leg's cut over a short boot) given the outline on its open side."""
    out = can.copy()
    four = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], bool)
    op = out[..., 3] > 0
    line = op & (out[..., :3] == outline).all(-1)
    edge = op & ~line & ndimage.binary_dilation(~op, structure=four)
    dark = edge & (out[..., :3].max(-1) < 40)
    out[dark, :3] = outline
    rest = edge & ~dark
    ring = ndimage.binary_dilation(rest, structure=four) & ~op
    out[ring] = (*outline, 255)
    return out


class SyndraRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def frames(rig, arm_pics):
    sheet = R.sheet_of(HERO)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        if tag not in OLD:
            sys.exit(f"{tag}: not in OLD")
        if len(OLD[tag]) != len(sheet[tag]):
            sys.exit(f"{tag}: {len(OLD[tag])} frames for the sheet's {len(sheet[tag])}")
        fr = [RG.on_grid(rig, *frame(rig.D, arm_pics, *spec)) for spec in OLD[tag]]
        if tag == "hit":
            fr[0] = R.flash(rig.finish(fr[0]))          # (the struck frame flashes, as every rig's)
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = list(out["idle_base"])
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--one-ground", action="store_true", help="after ppu_one.py: trim the 1x frames along the ground")
    a = ap.parse_args()
    if a.one_ground:
        RG.HERO = HERO                                  # (rig_rengar_hd's trim along the ground, on her sheet)
        RG.one_ground()
        return
    D = design()
    arm_pics = arms()
    rig = SyndraRig(D, pad=(12, 30, 10, 6))
    acts = frames(rig, arm_pics)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
