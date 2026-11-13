#!/usr/bin/env python3
"""In-between frames for the heroes posed from whole key pictures (rig_belveth, rig_azir, rig_trundle ...): more
different pictures in an action without a new drawing from anyone (the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的
地方都要补 参考联盟的动画」, 「动画你觉得少的地方就想办法补」, 「不合格的特效和动画你可以手搓」).

A key pose is one finished picture, so nothing here turns, scales or blends it (art-spec: no arbitrary turns, no
stretched limbs, the head never touched). What it offers instead, all on whole squares:

  moved(can, dx, dy)          the whole figure moved (anticipation, lunge, overshoot, settle);
  cut(shape, polys, boxes)    a part's mask from polygons in the pose picture's own squares;
  repose(d, moves, outline)   a pose picture with parts moved: "under" - behind the rest of the figure, so a wing or a
                              tail that grows out from behind the body is seen shorter or longer as it slides (the
                              squares it leaves are air, the ones the body covers are hidden); "over" - in front, the
                              squares it leaves inside the figure filled from the squares round them
                              (ppu_rig.fill_under); "gone" - taken off. The outline is closed again round what the move
                              bared, and only there: an edge the key pose draws open stays as drawn, so a key frame and
                              the frames made from it do not flicker;
  sway(d, mask, x0, x1, k)    a part's whole columns lifted 0..k rows along its length (a tail's wave: ppu_rig.sway);
  smear(a, mask, dx, dy, n)   a smear behind a part that moves fast: the air it swept over in its last n squares
                              filled flat in one of the part's own colours and joined to it;
  recolour(a, mask, table)    a part's colours changed for a frame (a blade's rim lit as it lands);
  audit(a)                    what a frame may not have: loose specks, pinholes;
  kept(d, out, ...)           that the head, and everything of a pose that is in no part, came through untouched;
  shared_head(...)            the head every key pose carries (the design's, pasted).

split(ms, n) / spans(...) share a span of an action out over n frames (whole ms, none under 50), so an action keeps
its length and the frame its strike begins on keeps its millisecond (the kits' ticks come from them).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

CROSS = R.CROSS
MIN_MS = 50                     # no frame shorter than this (three ticks)
DARK = 26                       # luminance under which a square is outline already (the designs' near-black edges)


# ------------------------------------------------------------------------------------------------- timing
def split(ms, n, weights=None):
    """`ms` shared over n frames in the proportions `weights` (default even): whole ms, the last takes the rest, none
    under MIN_MS."""
    w = list(weights) if weights else [1] * n
    if len(w) != n:
        raise SystemExit(f"split: {len(w)} weights for {n} frames")
    out = [int(round(ms * k / sum(w))) for k in w[:-1]]
    out.append(int(round(ms)) - sum(out))
    if min(out) < MIN_MS:
        raise SystemExit(f"split: {ms} ms over {n} frames gives {out} (a frame under {MIN_MS} ms)")
    return out


def spans(*parts):
    """[(ms of a span, n frames[, weights])...] -> the frames' ms in order (each span shared out by split): the
    spans' ends stay on their milliseconds whatever the frames inside them."""
    out = []
    for ms, n, *w in parts:
        out += split(ms, n, *w)
    return out


# ------------------------------------------------------------------------------------------------- masks
def cut(shape, polys=(), boxes=()):
    """A mask (H, W) of the squares whose centre is inside any polygon [(x, y), ...] (square edges, as
    ppu_rig.Design.poly) or box (x0, y0, x1, y1) (squares, inclusive), in the picture's own squares."""
    H, W = shape[:2]
    img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(img)
    for pts in polys:
        dr.polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    m = np.asarray(img, bool).copy()
    for x0, y0, x1, y1 in boxes:
        m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    return m


def lum(rgb):
    rgb = rgb.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


# ------------------------------------------------------------------------------------------------- moving
def moved(can, dx=0, dy=0):
    """The whole picture moved (dx, dy) squares on its canvas (what would leave the canvas is an error)."""
    if not dx and not dy:
        return can.copy()
    out = np.zeros_like(can)
    ys, xs = np.nonzero(can[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    if len(ys) and (ty.min() < 0 or ty.max() >= can.shape[0] or tx.min() < 0 or tx.max() >= can.shape[1]):
        raise SystemExit("moved: the figure leaves its canvas (pad the rig)")
    out[ty, tx] = can[ys, xs]
    return out


def padded(d, pad):
    out = np.zeros((d.shape[0] + 2 * pad, d.shape[1] + 2 * pad) + d.shape[2:], d.dtype)
    out[pad:pad + d.shape[0], pad:pad + d.shape[1]] = d
    return out


def repose(d, moves, outline, pad=0, seam=True, crack=10, slit=40, fill_iters=12):
    """The pose picture d with parts moved by whole squares: moves = [(mask, (dx, dy), how)], how "under" (behind the
    rest of the figure; of two under parts the first named is in front), "over" (in front: laid on last, the squares
    it left inside the figure filled from round them) or "gone" (taken off: a far limb gone behind the body).
    -> the picture on a canvas `pad` squares bigger on every side (so a part may leave the picture's own box).

    The outline afterwards: a clear square next to a drawn one that is not near-black gets the outline colour where
    the move bared that edge (the two squares were both drawn in d, or a part now ends against air where it ran on
    under the body); seam: a part behind the figure gets the figure's outline drawn on it where the figure's edge
    square is not near-black itself (the line a body throws on the wing behind it). Enclosed cracks the move opened
    (at most `crack` squares, or `slit` squares one square across) are filled with the outline colour; the gaps the
    pose itself has stay open."""
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    taken = np.zeros((H, W), bool)
    for mask, _, _ in moves:
        taken |= mask & op
    Ho, Wo = H + 2 * pad, W + 2 * pad
    out = np.zeros((Ho, Wo, 4), np.uint8)
    sy = np.full((Ho, Wo), -1, int)                      # each drawn square's own square in d
    sx = np.full((Ho, Wo), -1, int)
    depth = np.full((Ho, Wo), -1, int)                   # -1 air, 0 a part in front, 1 the rest, 2.. the parts behind

    def lay(mask, dx, dy, under, n):
        ys, xs = np.nonzero(mask & op)
        ty, tx = ys + pad + dy, xs + pad + dx
        ok = (ty >= 0) & (ty < Ho) & (tx >= 0) & (tx < Wo)
        if not ok.all():
            raise SystemExit(f"repose: {int((~ok).sum())} squares of a part leave the picture (pad more)")
        if under:
            free = out[ty, tx, 3] == 0
            ty, tx, ys, xs = ty[free], tx[free], ys[free], xs[free]
        out[ty, tx] = d[ys, xs]
        sy[ty, tx], sx[ty, tx], depth[ty, tx] = ys, xs, n

    lay(op & ~taken, 0, 0, False, 1)
    n = 2
    for mask, (dx, dy), how in moves:
        if how == "under":
            lay(mask, dx, dy, True, n)
            n += 1
    holes = np.zeros((Ho, Wo), bool)
    for mask, (dx, dy), how in moves:
        if how == "over":
            holes |= padded(mask & op, pad)
    if holes.any():
        solid = out[..., 3] > 0
        inside = ndimage.binary_fill_holes(solid | holes)
        todo = holes & inside & ~solid
        out = R.fill_under(out, todo, iters=fill_iters)
        depth[todo & (out[..., 3] > 0)] = 1
    for mask, (dx, dy), how in moves:
        if how == "over":
            lay(mask, dx, dy, False, 0)
    # the outline round what the move bared
    drawn = out[..., 3] > 0
    light = drawn & (lum(out[..., :3]) >= DARK)
    opd = np.pad(op, 1)
    ring = np.zeros((Ho, Wo), bool)
    line = np.zeros((Ho, Wo), bool)
    pdrawn, pdepth = np.pad(drawn, 1), np.pad(depth, 1, constant_values=-1)
    for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = pdrawn[1 + dy_:1 + dy_ + Ho, 1 + dx_:1 + dx_ + Wo]      # whether the square at (y + dy_, x + dx_) is drawn
        nb_depth = pdepth[1 + dy_:1 + dy_ + Ho, 1 + dx_:1 + dx_ + Wo]
        ys, xs = np.nonzero(light & ~nb)
        if len(ys):
            # was the neighbour in that direction drawn in d (an inner edge then, bared now)?
            qy, qx = sy[ys, xs], sx[ys, xs]
            known = qy >= 0
            was = np.zeros(len(ys), bool)
            was[known] = opd[qy[known] + 1 + dy_, qx[known] + 1 + dx_]
            ty, tx = ys[was] + dy_, xs[was] + dx_
            ok = (ty >= 0) & (ty < Ho) & (tx >= 0) & (tx < Wo)
            ring[ty[ok], tx[ok]] = True
        if seam:
            # a square of a part behind, next to a light square of something in front of it
            behind = light & nb & (nb_depth > depth)
            ys, xs = np.nonzero(behind)
            ty, tx = ys + dy_, xs + dx_
            ok = (ty >= 0) & (ty < Ho) & (tx >= 0) & (tx < Wo)
            line[ty[ok], tx[ok]] = True
    ring &= ~drawn
    out[ring, :3] = outline
    out[ring, 3] = 255
    if seam:
        line &= drawn & (depth >= 2)
        out[line, :3] = outline
    # cracks the move opened
    keep = padded(ndimage.binary_dilation(ndimage.binary_fill_holes(op) & ~op, iterations=1), pad)
    drawn = out[..., 3] > 0
    lab, k = ndimage.label(ndimage.binary_fill_holes(drawn) & ~drawn)
    for j in range(1, k + 1):
        h = lab == j
        if (h & keep).any():
            continue
        size = int(h.sum())
        if size <= crack or (size <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h, :3] = outline
            out[h, 3] = 255
    return out


def sway(d, mask, x0, x1, k, attach="right", under=True):
    """The part's whole columns between x0 and x1 lifted up to k rows (negative: lowered): nothing at the attached end,
    k at the free one - a tail's or a ribbon's wave (ppu_rig.sway on one part of a pose picture). A column that moved
    leaves air where it was; where it comes to lie on the rest of the figure it goes behind it (under: a tail's tip
    lifted against the wing over it), or over it. Columns step a square at a time, which keeps a drawn outline
    closed."""
    op = d[..., 3] > 0
    m = mask & op
    part = np.zeros_like(d)
    part[m] = d[m]
    out = d.copy()
    out[m] = 0
    sw = R.sway(part, x0, x1, k, attach)
    mm = sw[..., 3] > 0
    if under:
        mm &= out[..., 3] == 0
    out[mm] = sw[mm]
    return out


def smear(a, mask, dx, dy, n=3, colour=None):
    """A smear behind the part `mask` of picture a as it moves along (dx, dy) (only the direction counts): the air the
    part swept over in the last n squares of the move - its silhouette laid 1..n squares back along it, each step a
    square narrower at both ends across the move, so the smear thins out toward where it came from - filled flat with
    `colour` (default: the part's lightest colour that fills 3 % of it or more), and the part's own outline squares
    along that side taken into it (no dark line between the part and its smear: the part reads as drawn out by its
    speed, the way a smear frame is drawn). Run it before the outline is closed: ppu_rig.Rig.finish rings the smear
    like the rest of the figure."""
    op = a[..., 3] > 0
    m = mask & op
    if not m.any() or (not dx and not dy):
        return a.copy()
    L = float(np.hypot(dx, dy))
    ux, uy = -dx / L, -dy / L                              # back along the move
    if colour is None:
        px = a[m][:, :3]
        cols, cnt = np.unique(px, axis=0, return_counts=True)
        big = cols[cnt >= 0.03 * len(px)]
        colour = tuple(int(v) for v in big[lum(big).argmax()])
    out = a.copy()
    H, W = op.shape
    across = np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]]) if abs(uy) >= abs(ux) else np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
    band = np.zeros((H, W), bool)
    cur = m
    for k in range(1, n + 1):
        if k > 1:
            cur = ndimage.binary_erosion(cur, structure=across, border_value=0)
        # every square on the way from step k - 1 to step k (a diagonal step leaves no checkered gap)
        for sx_, sy_ in {(int(round(ux * k)), int(round(uy * k))), (int(round(ux * (k - 1))), int(round(uy * k))),
                         (int(round(ux * k)), int(round(uy * (k - 1))))}:
            ys, xs = np.nonzero(cur)
            ty, tx = ys + sy_, xs + sx_
            ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
            band[ty[ok], tx[ok]] = True
    band &= ~op
    # a band a square thin is a doubled outline, not a smear: only what is two squares deep or more somewhere stays
    lab, cnt = ndimage.label(band)
    for j in range(1, cnt + 1):
        piece = lab == j
        if ndimage.distance_transform_edt(piece).max() < 2:
            band[piece] = False
    if not band.any():
        return out
    edge = m & (lum(a[..., :3]) < DARK) & ndimage.binary_dilation(band, structure=np.ones((3, 3)))
    out[band | edge, :3] = colour
    out[band, 3] = 255
    return out


def recolour(a, mask, table):
    """The squares of the part `mask` that are in a colour of `table` {rgb: rgb} repainted - a blade's rim lit for the
    frame it lands on, in colours the design already has."""
    out = a.copy()
    m = mask & (a[..., 3] > 0)
    rgb = a[..., :3].astype(int)
    for src, dst in table.items():
        hit = m & (rgb == np.array(src)).all(-1)
        out[hit, :3] = dst
    return out


# ------------------------------------------------------------------------------------------------- checks
def audit(a, speck=4, hole=3):
    """What a finished frame may not have -> a list of faults: loose pieces (a speck under `speck` squares, or the
    figure in more than one piece), enclosed pinholes of at most `hole` squares."""
    op = a[..., 3] > 0
    faults = []
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = [int(s) for s in ndimage.sum(op, lab, range(1, n + 1))]
        small = [s for s in sz if s < speck]
        if small:
            faults.append(f"{len(small)} loose specks {small}")
        if sum(1 for s in sz if s >= speck) > 1:
            faults.append(f"in {sum(1 for s in sz if s >= speck)} pieces {sorted(sz)}")
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    if n:
        sz = [int(s) for s in ndimage.sum(np.ones_like(op), lab, range(1, n + 1))]
        pin = [s for s in sz if s <= hole]
        if pin:
            faults.append(f"{len(pin)} pinholes {pin}")
    return faults


def kept(d, out, pad=0, only=None, but=None):
    """Whether every drawn square of the pose picture d (`only`: a mask of the squares that count, all by default;
    `but`: a mask of squares left out - the parts that moved) is the same square in `out`, the picture made from it on
    a canvas `pad` bigger on every side. The head of a key pose, and everything of it that is in no part, must come
    through every in-between untouched: one approved head, a body that never changes size."""
    m = d[..., 3] > 0
    if only is not None:
        m = m & only
    if but is not None:
        m = m & ~but
    ys, xs = np.nonzero(m)
    return bool((out[ys + pad, xs + pad] == d[ys, xs]).all())


def shared_head(design, at, size, poses):
    """The head every key pose carries: the squares of the design's head box (top-left `at` (x, y), `size` (w, h))
    that each pose picture holds unchanged in its own head box. poses: [(picture, its head box's top-left)].
    -> a mask (h, w) of the box (the collar and the horns round the head differ from pose to pose and are not in it)."""
    (x, y), (w, h) = at, size
    box = design[y:y + h, x:x + w]
    m = box[..., 3] > 0
    for d, (px, py) in poses:
        sub = d[py:py + h, px:px + w]
        if sub.shape != box.shape:
            raise SystemExit("shared_head: a pose's head box leaves its picture")
        m &= (sub == box).all(-1)
    return m
