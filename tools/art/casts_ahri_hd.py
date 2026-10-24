#!/usr/bin/env python3
"""Ahri's actions from Codex's whole-frame redraw (assets/source/ahri/hd/casts: tools/art/pack_ahri_actions.py's pack,
delivered 2026-10-24 after the user's 「你让codex帮忙把 整理整理 给我动作包吧」), read onto the design's squares:

1. the near-white ground keyed off (the white flooded in from the sheet's edge: the tails' white stays inside their
   outline), each cell's figure the pieces of it big enough;
2. brought to the design's size: Codex drew each action at its own scale and off any fixed grid, so each tag takes
   the scale that sets her ear tips as far over her near eye as the design's (EAR_EYE squares; SCALE, measured);
   every design square the Lab mean of the Codex pixels it covers, snapped to the design's colours, the outline where
   it covers OUTLINE_SHARE of outline; speckle cleaned (design_jinx_hd.clean);
3. placed on the design's grid (cell x -> PIVOT column, Codex's ground -> GROUND).

    python tools/art/casts_ahri_hd.py --review DIR      # every tag read, at 3x
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_jinx_hd as JD  # noqa: E402
import ppu_rig as R  # noqa: E402

HERO = "ahri"
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
SRC = os.path.join(HD, "casts")
CELL = (768, 1024)
CELL_X = 384                    # Codex's standing point in a cell (the template's)
WHITE = 228                     # a ground pixel: every channel at least this, joined to the sheet's edge
MIN_PIECE = 300                 # Codex pixels: smaller bits off the figure dropped
EAR_EYE = 28                    # design squares from her ear tips to her near eye
# Codex pixels a design square per tag. Codex drew her body 8-25 % longer than the design for its head (eye to soles
# 65-75 squares against the design's 60 when read at the head's size), so the body sets the scale - her near eye as
# high over the ground as the design's in the tag's most upright frame on the ground - and the design's head goes on
# (head()): her ear-to-eye height over EAR_EYE (the median over the frames whose two eyes read as a level pair,
# C:/t/ar_imp/eyes.py) times that frame's eye-to-soles squares over EYE_SOLES (2026-10-24)
EYE_SOLES = 60
HEAD_SCALE = {"run": 6.58, "attack": 6.52, "skill": 7.08, "skill2": 6.74, "ult": 5.76, "hit": 5.92, "dead": 5.66}
BODY = {"run": 66, "attack": 75, "skill": 67, "skill2": 75, "ult": 65, "hit": 73, "dead": 69}
SCALE = {t: HEAD_SCALE[t] * BODY[t] / EYE_SOLES for t in HEAD_SCALE}
# Codex's own head kept: lying, and where it tilts or bows as she falls so far that the design's upright head leaves
# its ears showing round it (2026-10-24, the user: 「这里出现两个三个耳朵了？」), and Spirit Rush's frame 4 (her head
# lower in the flight: the match lands off it)
NO_HEAD = {"dead_3", "dead_4", "dead_5", "dead_6", "dead_7", "dead_8", "ult_4"}
HEAD_NUDGE = {}                         # squares: a matched head moved by hand
HAIR_RGB = [0x1A1738, 0x282655, 0x494693, 0x311528]
FACE_WEIGHT = 4
HEAD_DROP = 16
NEAR_EYE = (58.5, 28.5)                 # the design's near eye
TAIL_PIECE, NOTCH_R, NOTCH_MOST, HOLE_MOST = 120, 2, 40, 60
FEET_ROWS, FEET_WIDE, FEET_GAP, LIFT = 3, 3, 2, 3
TASSEL_RGB = [0x9D4EF5, 0x7127CC, 0x5C1FA2, 0x5B257E]
BLOCK = {"dead": 63.6}                  # the design's tassel column
TILTS = {"dead": tuple(range(-30, 31, 6)), "hit": (-12, -6, 0, 6, 12)}   # degrees counter-clockwise tried
EAR_RGB = [0xFBC1AF, 0xEB897F, 0xF3A592, 0xAB6960, 0xD29888]
EAR_MOST, EAR_PINK = 90, 3
FACE_LAB = 14                           # Lab distance: a head square on Codex's head of its own colour family
SKIN = ("D29888", "F3A592", "FBC1AF", "FDE3D0", "EB897F", "AB6960")   # a hand's squares
ARM_MOST = 6                            # squares of sleeve under the head before they count as an arm before the face
OUTLINE = (10, 2, 16)
OUTLINE_RGB = (OUTLINE[0] << 16) | (OUTLINE[1] << 8) | OUTLINE[2]
OUTLINE_SHARE = 0.40
PIVOT_COL, GROUND = 58, 88


def lp(p):
    return R.lp(p)


def keyed(rgb):
    """The sheet with its near-white ground transparent."""
    light = rgb.min(-1) >= WHITE
    lbl, _ = ndimage.label(light)
    edge = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(np.isin(lbl, list(edge)), 0, 255)
    return out


def figure(cell):
    op = cell[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if not n:
        return None
    sz = ndimage.sum(op, lbl, range(1, n + 1))
    keep = np.isin(lbl, [k + 1 for k in range(n) if sz[k] >= MIN_PIECE])
    out = cell.copy()
    out[~keep] = 0
    return out if keep.any() else None


def palette():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0)


def resample(fig, step, pal):
    """Codex's figure -> design squares (step Codex pixels a square): per square the Lab mean of what it covers but
    the outline, snapped to pal; the outline where its share is OUTLINE_SHARE."""
    import design_lux_hd as DL
    op = fig[..., 3] > 0
    plab = color.rgb2lab(pal[None].astype(float) / 255.0)[0]
    lab = color.rgb2lab(fig[..., :3] / 255.0)
    near = np.argmin(((lab[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
    oi = int(np.argmin(np.abs(pal.astype(int) - np.array(OUTLINE)).sum(1)))
    out_px = (op & (near == oi)).astype(float)
    DL.STEP = step
    wy, wx = DL.cover(fig.shape[0]), DL.cover(fig.shape[1])
    opf = op.astype(float)
    inner = opf * (1 - out_px)
    cov, oc, wi = wy @ opf @ wx.T, wy @ out_px @ wx.T, wy @ inner @ wx.T
    area = wy.sum(1)[:, None] * wx.sum(1)[None, :]
    mean = np.stack([wy @ (lab[..., c] * inner) @ wx.T for c in range(3)], -1) / np.maximum(wi, 1e-9)[..., None]
    k = np.argmin(((mean[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
    keep = cov >= 0.5 * area
    d = np.zeros(cov.shape + (4,), np.uint8)
    d[keep, :3] = pal[k[keep]]
    d[keep & ((oc >= OUTLINE_SHARE * cov) | (wi < 0.2 * area)), :3] = pal[oi]
    d[keep, 3] = 255
    return JD.clean(d)


def head_at(d, img, eye, r):
    """Where the design's head piece (img, its near eye at `eye` in it) goes on the read frame d: the design's head
    shrunk to Codex's head size (r: Codex drew the head r times the design's for her body) matched over the frame's top
    part (its ear tips at most HEAD_DROP rows under the figure's top) - the most of its squares on a square of the same
    colour family (Lab within FACE_LAB) less those on nothing, her face (every head colour but the hair's and the
    outline's) counting FACE_WEIGHT times - and the full head's near eye put on the match's. -> (the full head's top-left
    in d's squares, the shrunk head's mask and its top-left there: Codex's head, the score per head square) or None."""
    h, w = img.shape[:2]
    sm = np.asarray(Image.fromarray(img).resize((max(1, round(w * r)), max(1, round(h * r))), Image.NEAREST))
    hy, hx = np.nonzero(sm[..., 3] > 0)
    if not len(hy):
        return None
    hl = color.rgb2lab(sm[hy, hx, :3][None].astype(float) / 255.0)[0]
    hrgb = (sm[hy, hx, 0].astype(np.int32) << 16) | (sm[hy, hx, 1].astype(np.int32) << 8) | sm[hy, hx, 2]
    wt = np.where(np.isin(hrgb, HAIR_RGB + [OUTLINE_RGB]), 1.0, FACE_WEIGHT)
    op = d[..., 3] > 0
    dl = color.rgb2lab(d[..., :3].astype(float) / 255.0)
    top = np.nonzero(op.any(1))[0].min()
    best, at = -1e9, None
    for sy in range(top - hy.min() - 4, top - hy.min() + HEAD_DROP + 1):
        for sx in range(-hx.min(), d.shape[1] - hx.max()):
            ty, tx = hy + sy, hx + sx
            ins = (ty >= 0) & (ty < d.shape[0])
            on = np.zeros(len(hy), bool)
            on[ins] = op[ty[ins], tx[ins]]
            dist = np.full(len(hy), 1e9)
            dist[on] = np.sqrt(((dl[ty[on], tx[on]] - hl[on]) ** 2).sum(-1))
            sc = (wt * (dist < FACE_LAB)).sum() - (wt * ~on).sum()
            if sc > best:
                best, at = sc, (sx, sy)
    ex, ey = at[0] + eye[0] * r, at[1] + eye[1] * r
    return (int(round(ex - eye[0])), int(round(ey - eye[1]))), (sm[..., 3] > 0, at), best / max(1.0, wt.sum())


def head(d, x, y, head_piece, keep_cols, r, tilts=(0,), nudge=(0, 0)):
    """The design's head (ear tips to the chin) on the read frame d (top-left x, y on the design's grid) where it covers
    Codex's (head_at): Codex's head goes under it, her sleeves and hands in front of the face stay on top (the squares
    under the head of a colour the head lacks - keep_cols - and the skin and outline touching them), and what of Codex's
    head shows past the design's above her eyes (a tilted head's ears) cleared - its hair, skin and outline squares, never the tails
    nor the outline edging them. Tags in TILTS also try the head turned about her near eye (Codex tilts it as she
    falls) and take the best match. -> (frame, x, y) grown to hold the head, her near eye there on the design's grid."""
    import rig_ahri_hd as RA
    best = None
    for deg in tilts:
        img, (hx0, hy0) = head_piece
        if deg:
            img, hx0, hy0 = RA.turned_soft(img, hx0, hy0, deg, NEAR_EYE)
        found = head_at(d, img, (NEAR_EYE[0] - hx0, NEAR_EYE[1] - hy0), r)
        if found is not None and (best is None or found[2] > best[0][2]):
            best = (found, img, hx0, hy0)
    if best is None:
        return d, x, y, None
    (at, (cm, (cx, cy)), _), img, hx0, hy0 = best
    gx, gy = x + at[0] + nudge[0], y + at[1] + nudge[1]   # the head's top-left on the design's grid
    X0, Y0 = min(x, gx), min(y, gy)
    X1, Y1 = max(x + d.shape[1], gx + img.shape[1]), max(y + d.shape[0], gy + img.shape[0])
    can = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8)
    can[y - Y0:y - Y0 + d.shape[0], x - X0:x - X0 + d.shape[1]] = d
    oy, ox = gy - Y0, gx - X0
    hm = img[..., 3] > 0
    m = np.zeros(can.shape[:2], bool)
    m[oy:oy + img.shape[0], ox:ox + img.shape[1]] = hm
    rgb = (can[..., 0].astype(np.int32) << 16) | (can[..., 1].astype(np.int32) << 8) | can[..., 2]
    op = can[..., 3] > 0
    arm = m & op & np.isin(rgb, keep_cols[0])
    if arm.sum() >= ARM_MOST:
        near = ndimage.binary_dilation(arm, iterations=2)
        arm |= m & op & near & np.isin(rgb, keep_cols[1])
        arm |= m & op & ndimage.binary_dilation(arm) & (rgb == OUTLINE_RGB)
    else:
        arm[:] = False
    codex = np.zeros(can.shape[:2], bool)
    codex[cy + y - Y0:cy + y - Y0 + cm.shape[0], cx + x - X0:cx + x - X0 + cm.shape[1]] = cm
    tail = op & np.isin(rgb, keep_cols[3])
    above = np.arange(can.shape[0])[:, None] <= oy + NEAR_EYE[1] - hy0               # her ears' rows: never the neck
    past = (ndimage.binary_dilation(codex, iterations=2) & above & ~m & op & ~arm & np.isin(rgb, keep_cols[2])
            & ~((rgb == OUTLINE_RGB) & ndimage.binary_dilation(tail, structure=np.ones((3, 3)))))
    can[past] = 0
    # a whole ear of Codex's left over the design's head (a tilted or bigger head): a piece of her head's colours above
    # her eyes and off the design's head, up to EAR_MOST squares, holding EAR_PINK squares of an ear's inside
    rgb = (can[..., 0].astype(np.int32) << 16) | (can[..., 1].astype(np.int32) << 8) | can[..., 2]
    op = can[..., 3] > 0
    loose = above & ~m & op & ~arm & np.isin(rgb, keep_cols[2]) & ~np.isin(rgb, HAIR_RGB[:1] + [0x282655, 0x494693])
    loose |= above & ~m & op & ~arm & np.isin(rgb, HAIR_RGB + [OUTLINE_RGB])
    loose &= ~((rgb == OUTLINE_RGB) & ndimage.binary_dilation(tail, structure=np.ones((3, 3))))
    lbl, k = ndimage.label(loose, structure=np.ones((3, 3)))
    for j in range(1, k + 1):
        piece_ = lbl == j
        if piece_.sum() <= EAR_MOST and (piece_ & np.isin(rgb, EAR_RGB)).sum() >= EAR_PINK:
            can[piece_] = 0
    keep = can.copy()
    sub = can[oy:oy + img.shape[0], ox:ox + img.shape[1]]
    sub[hm] = img[hm]
    can[arm] = keep[arm]
    return can, X0, Y0, (gx + NEAR_EYE[0] - hx0, gy + NEAR_EYE[1] - hy0)


def join_tails(can, tail_rgb):
    """The tails kept joined to her hair: every open notch of background (up to NOTCH_MOST squares, inside the figure's
    closing by a NOTCH_R disk) between the tails' fan (its tail-coloured pieces of TAIL_PIECE squares or more) and her
    hair filled with the nearest tail square's colour, its new edge outlined - Codex leaves thin slits of ground between
    a tail's tip and her hair, which read as tails cut off her body; and the enclosed holes against them filled."""
    op = can[..., 3] > 0
    rgb = (can[..., 0].astype(np.int32) << 16) | (can[..., 1].astype(np.int32) << 8) | can[..., 2]
    lbl, n = ndimage.label(op & np.isin(rgb, tail_rgb), structure=np.ones((3, 3)))
    if not n:
        return can
    sz = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    tail = np.isin(lbl, [k + 1 for k in range(n) if sz[k] >= TAIL_PIECE])
    hair = op & np.isin(rgb, HAIR_RGB)
    yy, xx = np.mgrid[-NOTCH_R:NOTCH_R + 1, -NOTCH_R:NOTCH_R + 1]
    pad = np.pad(op, NOTCH_R + 1)
    shut = ndimage.binary_closing(pad, yy ** 2 + xx ** 2 <= NOTCH_R ** 2 + 0.5)[NOTCH_R + 1:-NOTCH_R - 1,
                                                                                NOTCH_R + 1:-NOTCH_R - 1]
    gap = shut & ~op
    nt, nh = ndimage.binary_dilation(tail, iterations=2), ndimage.binary_dilation(hair, iterations=2)
    glbl, gn = ndimage.label(gap)
    fill = np.zeros_like(gap)
    for k in range(1, gn + 1):
        m = glbl == k
        if m.sum() <= NOTCH_MOST and (m & nt).any() and (m & nh).any():
            fill |= m
    out = can.copy()
    if fill.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~tail, return_indices=True)
        out[fill] = can[iy[fill], ix[fill]]
        now = out[..., 3] > 0
        edge = fill & ndimage.binary_dilation(~now, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
        out[edge, :3] = OUTLINE
    # enclosed holes against the hair or the tails (behind the new head, between locks and tails): the nearest
    # square's colour but the outline's
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    hlbl, hn = ndimage.label(holes)
    solid = op & (rgb != OUTLINE_RGB)
    if hn and solid.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
        for k in range(1, hn + 1):
            m = hlbl == k
            if m.sum() <= HOLE_MOST and (m & (nt | nh)).any():
                out[m] = out[iy[m], ix[m]]
    return out


def frames():
    """{"<tag>_<frame>": (design-square picture, x, y of its top-left on the design's grid)} for every frame Codex
    drew, placed by Codex's own cell (its standing point and the sheet's ground)."""
    pal = palette()
    import rig_ahri_hd as RA
    ps = RA.Poser(RA.design().d0)
    head_piece = ps.pieces["head_fly"]
    img = head_piece[0]
    hc = set(((img[..., 0].astype(np.int32) << 16) | (img[..., 1].astype(np.int32) << 8) | img[..., 2])[img[..., 3] > 0])
    allc = {(int(c[0]) << 16) | (int(c[1]) << 8) | int(c[2]) for c in pal}
    sleeve = sorted(allc - hc - set(RA.TAIL_RGB))                 # robe, cuffs, sash: never on her head
    skin = sorted(c for c in hc if c in {int(h, 16) for h in SKIN})
    face = sorted(c for c in hc if c not in set(RA.TAIL_RGB))        # hair, ears, skin, eyes, outline
    keep_cols = (sleeve, skin, face, sorted(set(RA.TAIL_RGB) - {OUTLINE_RGB}))
    sheets = json.load(open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8"))["sheets"]
    out = {}
    for sh in sheets:
        tag = sh["tag"]
        rgb = np.asarray(Image.open(lp(os.path.join(SRC, sh["name"] + ".png"))).convert("RGB"))
        k = keyed(rgb)
        cells = [figure(k[:, i * CELL[0]:(i + 1) * CELL[0]]) for i in range(len(sh["frames"]))]
        soles = [int(np.nonzero(c[..., 3].any(1))[0].max()) + 1 for c in cells if c is not None]
        ground = max(soles) if soles else CELL[1] - 150
        step = SCALE[tag]
        for fno, c in zip(sh["frames"], cells):
            if c is None:
                continue
            d = resample(c, step, pal)
            # the cell's (CELL_X, ground) lands on the design's (PIVOT_COL, GROUND)
            x, y = int(round(PIVOT_COL - CELL_X / step)), int(round(GROUND - ground / step))
            name = f"{tag}_{fno}"
            eye = None
            if name not in NO_HEAD:
                d, x, y, eye = head(d, x, y, head_piece, keep_cols, EYE_SOLES / BODY[tag], TILTS.get(tag, (0,)),
                                   HEAD_NUDGE.get(name, (0, 0)))
            d = join_tails(d, keep_cols[3])
            out[name] = (d, x, y, eye)
    return out


def feet(d, tail_rgb):
    """Her boots on the ground: the middles of the groups (FEET_WIDE squares or wider, FEET_GAP apart) of boot squares
    (neither tail, hair nor outline) in the FEET_ROWS rows over the lowest boot square. -> ([x, ...] in d's columns,
    the row under the lowest)."""
    rgb = (d[..., 0].astype(np.int32) << 16) | (d[..., 1].astype(np.int32) << 8) | d[..., 2]
    body = (d[..., 3] > 0) & ~np.isin(rgb, list(tail_rgb) + HAIR_RGB + [OUTLINE_RGB])
    ys = np.nonzero(body.any(1))[0]
    low = ys.max() + 1
    xs = np.nonzero(body[low - FEET_ROWS:low].any(0))[0]
    groups = [g for g in np.split(xs, np.where(np.diff(xs) > FEET_GAP)[0] + 1) if g.max() - g.min() + 1 >= FEET_WIDE]
    return [(g.min() + g.max() + 1) / 2.0 for g in groups], low


def tassel(d, x):
    """The middle column of her violet tassel (it hangs from her waist) on the design's grid."""
    rgb = (d[..., 0].astype(np.int32) << 16) | (d[..., 1].astype(np.int32) << 8) | d[..., 2]
    xs = np.nonzero((d[..., 3] > 0) & np.isin(rgb, TASSEL_RGB))[1]
    return x + xs.mean() + 0.5


def placed():
    """{name: (picture, x, y)}: frames() shifted along the ground. The run keeps her head steady (her near eye in one
    column, the boots' mean on the standing point); every other tag starts with her boots where the design has them
    and keeps the rear boot planted while both stand on the ground (Codex drew each sheet off the standing point:
    eyes 10-40 squares to the right, drifting from sheet to sheet); the frames between run straight from shift to
    shift. The death (BLOCK) moves whole: Codex's frames kept where they stand to one another, her tassel in the first
    where the design has it (no boot of hers stands on the ground till she lies)."""
    import rig_ahri_hd as RA
    tail_rgb = sorted(set(RA.TAIL_RGB) - {OUTLINE_RGB})
    raw = cached_frames()
    D = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    dm, _ = feet(D, tail_rgb)
    design_mid = (dm[0] + dm[-1]) / 2.0
    tags = {}
    for n in sorted(raw, key=lambda n: int(n.rsplit("_", 1)[1])):
        tags.setdefault(n.rsplit("_", 1)[0], []).append(n)
    out = {}
    for tag, names in tags.items():
        ft = {}
        for n in names:
            d, x, y, eye = raw[n]
            mids, low = feet(d, tail_rgb)
            ft[n] = ([x + m for m in mids], y + low)
        known = {}
        if tag in BLOCK:
            d, x, y, eye = raw[names[0]]
            known[0] = BLOCK[tag] - tassel(d, x)
        elif tag == "run":
            lead = np.mean([raw[n][3][0] - np.mean(ft[n][0]) for n in names if ft[n][0]])
            for i, n in enumerate(names):
                known[i] = PIVOT_COL + lead - raw[n][3][0]
        else:
            rear = None
            for i, n in enumerate(names):
                mids, low = ft[n]
                if len(mids) < 2 or low < GROUND - LIFT:
                    continue
                if rear is None:
                    known[i] = design_mid - (mids[0] + mids[-1]) / 2.0
                    rear = mids[0] + known[i]
                else:
                    known[i] = rear - mids[0]
            if not known:
                known[0] = 0.0
        for i, n in enumerate(names):
            if i in known:
                v = known[i]
            else:
                lo = [k for k in known if k < i]
                hi = [k for k in known if k > i]
                if lo and hi:
                    a, b = max(lo), min(hi)
                    v = known[a] + (known[b] - known[a]) * (i - a) / (b - a)
                else:
                    v = known[max(lo)] if lo else known[min(hi)]
            d, x, y, _ = raw[n]
            out[n] = (d, x + int(round(v)), y)
    return out


def cached_frames():
    """frames(), kept in the temp folder against this file's, the design's and the sources' bytes (it reads for ~2 minutes)."""
    import hashlib
    import pickle
    import tempfile
    h = hashlib.sha1(open(__file__, "rb").read() + open(lp(os.path.join(HD, "design.png")), "rb").read())
    for f in sorted(os.listdir(lp(SRC))):
        if f.endswith(".png") or f.endswith(".json"):
            h.update(open(lp(os.path.join(SRC, f)), "rb").read())
    path = os.path.join(tempfile.gettempdir(), f"casts_ahri_{h.hexdigest()[:16]}.pkl")
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    fr = frames()
    pickle.dump(fr, open(path, "wb"))
    return fr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr = placed()
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        tags = sorted({n.rsplit("_", 1)[0] for n in fr}, key=list(SCALE).index)
        import pickle
        pickle.dump(fr, open(os.path.join(a.review, "frames.pkl"), "wb"))
        for t in tags:
            names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
            Z, W, H = 3, 200, 140
            can = Image.new("RGB", (len(names) * (W * Z + 4), H * Z), (40, 40, 40))
            for i, n in enumerate(names):
                d, x, y = fr[n]
                tile = Image.new("RGBA", (W, H), (96, 112, 96, 255))
                tile.alpha_composite(Image.fromarray(d), (x + 60, y + 40))
                can.paste(tile.convert("RGB").resize((W * Z, H * Z), Image.NEAREST), (i * (W * Z + 4), 0))
            can.save(os.path.join(a.review, f"read_{t}.png"))
        print("written", a.review)


if __name__ == "__main__":
    main()
