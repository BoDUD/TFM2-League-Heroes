#!/usr/bin/env python3
"""Annie's actions from Codex's whole-frame redraw (assets/source/annie/hd/casts: tools/art/pack_annie_actions.py's
pack, delivered 2026-10-24; the user: 「codex交付了 做到完美后喊我review」), read onto the design's squares - Ahri's way
(tools/art/casts_ahri_hd.py) without the tails:

1. the near-white ground keyed off (flooded in from the sheet's edge), each cell's figure the pieces of it big enough;
2. brought to the design's size: Codex drew each sheet at its own scale, so each sheet takes the scale its head says
   (her near eye under her cat-ear tips, measured on the green of her eyes and the light pink of the headband) times
   BODY_K (Codex's bodies run a little longer than its heads: the factor that gives the upright frames the design's eye
   to soles); every design square the Lab mean of the Codex pixels it covers, snapped to the design's colours, the
   outline where it covers OUTLINE_SHARE of outline; speckle cleaned (design_jinx_hd.clean);
3. the design's head (rows above HEAD_CUT, the face set by hand) put on where Codex's is: its near eye on Codex's near
   eye, then the best of the nearby places (the most head squares on a square of the same colour family, the face
   counting FACE_WEIGHT times); Codex's sleeves, bracelet, hand and Tibbers lying over the face stay on top, and what of
   Codex's head shows past the design's above her eyes is cleared. Lying frames (NO_HEAD) keep Codex's own head;
4. placed on the design's grid: the soles (the lowest squares that are neither Tibbers nor outline) of each sheet's
   lowest frame on the ground; along the ground the run keeps her near eye in one column, the other tags start with
   her shoes where the design has them and keep the rear shoe planted, the death moves whole (Codex's own cells).

    python tools/art/casts_annie_hd.py --review DIR      # every tag read, at 3x
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
import casts_ahri_hd as CA  # noqa: E402
import design_jinx_hd as JD  # noqa: E402
import ppu_rig as R  # noqa: E402

HERO = "annie"
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
SRC = os.path.join(HD, "casts")
CELL = (768, 1024)
CELL_X = 384                    # Codex's standing point in a cell (the template's)
MIN_PIECE = 300                 # Codex pixels: smaller bits off the figure dropped
HOLE_RIM = 0.8                  # an enclosed light piece this much ringed by outline is ground (gaps: 0.86-0.98; eye
                                # whites 0.58-0.60, collar and headband 0-0.5)
H = lambda s: [int(h, 16) for h in s.split()]  # noqa: E731
HAIR = H("87033D C50F5B 560223 FB2B88 3A0314")
PINK = H("FB8ADC CC80B4 B14D8C EB54AC AB226C DCC9D7 C1A5C5 F5F1F2")
SKIN = H("FCC58E F39A6E F8B279 E88661 C38868 BF553F 903C3A 774A35")
EYES = H("62A608 3D7A05 1D370A")
DRESS = H("4E1580 6C20A9 AC34F0 410E5D A52CA6 811976 082B60 0E45A0")
TIB = H("7F3010 A74716 541A0E")
BRACELET = H("B40C2D")
OUTLINE = (0x10, 0x02, 0x13)
OUTLINE_RGB = 0x100213
HEAD_COLS = HAIR + PINK + SKIN + EYES + H("BA1E36") + [OUTLINE_RGB]
OVER_COLS = DRESS + TIB + BRACELET              # never on her head: what of them lies over it is an arm / the bear
OUTLINE_SHARE = 0.40
HEAD_CUT = 32                   # the design's head: its rows above this (the chin's row is 31)
FACE_WEIGHT = 4
FACE_LAB = 14
SEARCH = 3                      # squares round the eye match the head is tried at
ARM_MOST = 6
STRAND_R = 6                    # squares round the design's head where Codex's thin strands of hair are cleared
TIB_MIN = 120                   # squares: Tibbers whole is 250+; a brown bit smaller is the next cell's
LOOSE = 80                      # squares: a piece off her body this small, neither the bear nor a hand, goes
SPECK = 20                      # squares: a piece this small off the figure is a speck
PAST_R = 4                      # squares round the design's head where Codex's own head is cleared
TIB_TAN = 2                     # tan squares this near Tibbers' browns are his patches
BODY_K = None                   # measured in frames() when None
# frames standing up straight on both feet (Codex's own drawings): they set their sheets' scale
UPRIGHT = {"attack_1", "attack_5", "skill_1", "skill_6", "skill2_1", "skill2_2", "skill2_7", "ult_5", "ult_6", "ult_7"}
NO_HEAD = {"dead_4", "dead_5", "dead_6"}
# a sheet with no head to measure: scaled so she lies as long as in the given frame (sheet: (that frame, one of this
# sheet's frames)); her bear would not do, Codex drew it smaller there
LIE_SCALE = {"dead_3": ("dead_4", "dead_5")}
STILL_TIB = {"dead": 5}         # her bear lying still apart from her: the later frames take this frame's picture of it
TILTS = {"dead": tuple(range(-36, 37, 6)), "hit": (-12, -6, 0, 6, 12)}
HEAD_NUDGE = {}
PIVOT_COL, GROUND = None, None  # set from the design (pivot between its shoes, the row under its soles)


def lp(p):
    return R.lp(p)


def rgb24(a):
    return (a[..., 0].astype(np.int32) << 16) | (a[..., 1].astype(np.int32) << 8) | a[..., 2]


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


def palette():
    d = design()
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0)


def tibbers(d):
    """Tibbers' squares: his browns and the tan patches next to them."""
    rgb = rgb24(d)
    op = d[..., 3] > 0
    br = op & np.isin(rgb, TIB)
    near = ndimage.binary_dilation(br, iterations=TIB_TAN)
    return br | (near & op & np.isin(rgb, H("E88661 F8B279 F39A6E")))


def soles_row(d):
    """The row under her lowest square that is neither Tibbers nor outline (+1: the outline under the shoe)."""
    op = (d[..., 3] > 0) & ~tibbers(d) & (rgb24(d) != OUTLINE_RGB)
    ys = np.nonzero(op.any(1))[0]
    return ys.max() + 2


def shoes(d):
    """Her shoes: the middles of the groups of shoe squares (her dark shoe colours) in the 3 rows over the soles."""
    rgb = rgb24(d)
    sh = (d[..., 3] > 0) & np.isin(rgb, H("332137 878483 A9AF95")) & ~tibbers(d)
    low = soles_row(d) - 1
    xs = np.nonzero(sh[max(0, low - 4):low].any(0))[0]
    if not len(xs):
        return [], low
    groups = [g for g in np.split(xs, np.where(np.diff(xs) > 2)[0] + 1) if g.max() - g.min() + 1 >= 2]
    return [(g.min() + g.max() + 1) / 2.0 for g in groups], low


def eye_measure(rgb, op):
    """(near eye (y, x), ear-tip row) on a picture: the larger green blobs (the leftmost the near eye), the topmost
    light pink (the headband). None where no eye is found."""
    hsv = color.rgb2hsv(rgb / 255.0)
    green = op & (hsv[..., 0] > 0.17) & (hsv[..., 0] < 0.36) & (hsv[..., 1] > 0.4) & (hsv[..., 2] > 0.25)
    pink = op & (hsv[..., 0] > 0.85) & (hsv[..., 1] > 0.15) & (hsv[..., 1] < 0.55) & (hsv[..., 2] > 0.8)
    lbl, n = ndimage.label(green, structure=np.ones((3, 3)))
    if not n:
        return None
    sz = ndimage.sum(green, lbl, range(1, n + 1))
    big = [k + 1 for k in np.argsort(-sz)[:2] if sz[k] >= 0.1 * sz.max()]
    cents = [ndimage.center_of_mass(lbl == k) for k in big]
    near = min(cents, key=lambda c: c[1])
    pys = np.nonzero(pink.any(1))[0]
    if not len(pys):
        return None
    return near, pys.min()


def keyed(rgb):
    """CA.keyed, and the enclosed near-white gaps too (between her legs, the bear and her arm): a light piece whose
    rim is at least HOLE_RIM dark outline - her eye whites, collar and headband lie among her colours."""
    out = CA.keyed(rgb)
    light = (rgb.min(-1) >= CA.WHITE) & (out[..., 3] > 0)
    dark = rgb.astype(int).sum(-1) < 150
    lbl, n = ndimage.label(light)
    for k in range(1, n + 1):
        m = lbl == k
        ring = ndimage.binary_dilation(m, iterations=3) & ~ndimage.binary_dilation(m, iterations=1)
        if dark[ring].mean() >= HOLE_RIM:
            out[m, 3] = 0
    return out


def codex_soles(c):
    """The lowest row of a Codex figure but its bear's (his browns, closed and filled, and a margin round them)."""
    op = c[..., 3] > 0
    hsv = color.rgb2hsv(c[..., :3] / 255.0)
    br = op & (hsv[..., 0] > 0.03) & (hsv[..., 0] < 0.09) & (hsv[..., 1] > 0.5) & (hsv[..., 2] > 0.25) & (hsv[..., 2] < 0.75)
    bear = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(br, iterations=4)), iterations=6)
    ys = np.nonzero((op & ~bear).any(1))[0]
    return ys.max() + 1


def keyed_cells(sh):
    rgb = np.asarray(Image.open(lp(os.path.join(SRC, sh["name"] + ".png"))).convert("RGB"))
    k = keyed(rgb)
    return [CA.figure(k[:, i * CELL[0]:(i + 1) * CELL[0]]) for i in range(len(sh["frames"]))]


def design_measure():
    d = design()
    big = np.repeat(np.repeat(d, 8, 0), 8, 1)
    (ey, ex), top = eye_measure(big[..., :3].astype(float), big[..., 3] > 0)
    soles = soles_row(d) * 8
    return (ey - top) / 8, (soles - ey) / 8, (ey / 8, ex / 8)


def head_piece():
    d = design()
    img = d.copy()
    img[HEAD_CUT:] = 0
    return img


def place_head(d, x, y, img, eye_d, eye_c, tilts, nudge):
    """The design's head (img; its near eye at eye_d, design squares) on the read frame d (top-left x, y on the grid)
    whose near eye Codex drew at eye_c (d's squares): tried at SEARCH squares round the eye match and at each tilt,
    the best colour agreement kept. -> (frame, x, y)."""
    import rig_ahri_hd as RA
    op = d[..., 3] > 0
    dl = color.rgb2lab(d[..., :3].astype(float) / 255.0)
    best = None
    for deg in tilts:
        im, ox0, oy0 = (img, 0, 0) if not deg else RA.turned_soft(img, 0, 0, deg, (eye_d[1], eye_d[0]))
        hy, hx = np.nonzero(im[..., 3] > 0)
        hl = color.rgb2lab(im[hy, hx, :3][None].astype(float) / 255.0)[0]
        wt = np.where(np.isin(rgb24(im)[hy, hx], HAIR + [OUTLINE_RGB]), 1.0, FACE_WEIGHT)
        ey, ex = eye_d[0] - oy0, eye_d[1] - ox0
        for dy in range(-SEARCH, SEARCH + 1):
            for dx in range(-SEARCH, SEARCH + 1):
                sy, sx = int(round(eye_c[0] - ey)) + dy, int(round(eye_c[1] - ex)) + dx
                ty, tx = hy + sy, hx + sx
                ins = (ty >= 0) & (ty < d.shape[0]) & (tx >= 0) & (tx < d.shape[1])
                on = np.zeros(len(hy), bool)
                on[ins] = op[ty[ins], tx[ins]]
                dist = np.full(len(hy), 1e9)
                dist[on] = np.sqrt(((dl[ty[on], tx[on]] - hl[on]) ** 2).sum(-1))
                sc = (wt * (dist < FACE_LAB)).sum() - (wt * ~on).sum()
                if best is None or sc > best[0]:
                    best = (sc, im, sx, sy)
    _, im, sx, sy = best
    sx, sy = sx + nudge[0], sy + nudge[1]
    X0, Y0 = min(0, sx), min(0, sy)
    X1, Y1 = max(d.shape[1], sx + im.shape[1]), max(d.shape[0], sy + im.shape[0])
    can = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8)
    can[-Y0:-Y0 + d.shape[0], -X0:-X0 + d.shape[1]] = d
    oy, ox = sy - Y0, sx - X0
    hm = np.zeros(can.shape[:2], bool)
    hm[oy:oy + im.shape[0], ox:ox + im.shape[1]] = im[..., 3] > 0
    rgb = rgb24(can)
    op = can[..., 3] > 0
    # what lies over her face: Codex's sleeve, bracelet and Tibbers squares under the head, with the skin and the
    # outline touching them (a hand)
    over = hm & op & np.isin(rgb, OVER_COLS)
    lbl, n = ndimage.label(over, structure=np.ones((3, 3)))
    if n:
        sz = ndimage.sum(over, lbl, range(1, n + 1))
        over = np.isin(lbl, [k + 1 for k in range(n) if sz[k] >= ARM_MOST])
    if over.any():
        near = ndimage.binary_dilation(over, iterations=3)
        skin = hm & op & np.isin(rgb, SKIN) & near
        over |= skin
        over |= hm & op & ndimage.binary_dilation(over) & (rgb == OUTLINE_RGB)
    # a hand raised over her head (Q's swing): Codex's skin reaching past the design's head above her eyes stays on
    # top, with its outline
    eye_row = oy + eye_d[0]
    above = np.arange(can.shape[0])[:, None] <= eye_row
    skin = op & np.isin(rgb, SKIN)
    lbl, n = ndimage.label(skin, structure=np.ones((3, 3)))
    for k in range(1, n + 1):
        m = lbl == k
        if (m & ~hm & above).sum() >= ARM_MOST and (m & hm).any():
            over |= m
    over |= hm & op & ndimage.binary_dilation(over) & (rgb == OUTLINE_RGB)
    # Codex's head past the design's, above the near eye and close round it (never the bear thrown over her): its
    # hair, headband and outline squares off the design's head
    close = ndimage.binary_dilation(hm, iterations=PAST_R)
    guard = ~ndimage.binary_dilation(over | tibbers(can), iterations=1)
    past = above & close & ~hm & op & np.isin(rgb, HAIR + PINK + EYES + [OUTLINE_RGB]) & guard
    # ... and down to her chin its hair only (a lock Codex swung out behind her head), with the outline that rimmed it
    chin = np.arange(can.shape[0])[:, None] < oy + HEAD_CUT
    lock = ~above & chin & close & ~hm & op & np.isin(rgb, HAIR) & guard
    rim = (ndimage.binary_dilation(lock, structure=np.ones((3, 3), bool)) & ~hm & op & (rgb == OUTLINE_RGB) & guard
           & ~ndimage.binary_dilation(op & ~lock & ~np.isin(rgb, HAIR + [OUTLINE_RGB]) & ~hm,
                                      structure=np.ones((3, 3), bool)))
    past |= lock | rim
    keep = can.copy()
    can[past] = 0
    sub = can[oy:oy + im.shape[0], ox:ox + im.shape[1]]
    m = im[..., 3] > 0
    sub[m] = im[m]
    can[over] = keep[over]
    return reattach(can, hm), x + X0, y + Y0


def reattach(can, hm):
    """After the head: Codex's 1-square strands of hair left by it (off the design's head, within STRAND_R) cleared;
    a hand left floating over the head (Codex drew it reaching up from behind a head the design's is lower than) moved
    straight down till it touches her; specks of up to SPECK squares and loose bits of up to LOOSE (neither Tibbers
    nor a hand) dropped."""
    op = can[..., 3] > 0
    rgb = rgb24(can)
    thin = op & ~ndimage.binary_opening(op, structure=np.ones((2, 2), bool))
    near = ndimage.binary_dilation(hm, iterations=STRAND_R) & ~hm
    can[thin & near & np.isin(rgb, HAIR + [OUTLINE_RGB])] = 0
    op = can[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        main = int(np.argmax(sz)) + 1
        for k in range(1, n + 1):
            m = lbl == k
            if k == main:
                continue
            if sz[k - 1] <= SPECK:
                can[m] = 0
                continue
            if (m & tibbers(can)).sum() > 0.3 * sz[k - 1]:
                if sz[k - 1] < TIB_MIN:
                    can[m] = 0                              # (a bit of the next cell's bear)
                continue                                    # (Tibbers in the air: as drawn)
            if (m & np.isin(rgb, SKIN)).sum() < 0.4 * sz[k - 1]:
                if sz[k - 1] <= LOOSE:
                    can[m] = 0                              # (a lock's end the head clearing cut off)
                continue
            body = lbl == main
            ys, xs = np.nonzero(m)
            px = can[ys, xs].copy()
            for dy in range(1, 9):
                if ys.max() + dy >= can.shape[0]:
                    break
                moved = np.zeros_like(m)
                moved[ys + dy, xs] = True
                if (ndimage.binary_dilation(moved, structure=np.ones((3, 3), bool)) & body).any():
                    can[m] = 0
                    ok = ~body[ys + dy, xs]
                    can[ys[ok] + dy, xs[ok]] = px[ok]
                    break
    return can



def bear_piece(d):
    """The piece of the frame (apart from her) that is mostly Tibbers."""
    op = d[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    t = tibbers(d)
    best = max(range(1, n + 1), key=lambda k: (t & (lbl == k)).sum() / max(1, (lbl == k).sum()))
    return lbl == best


def body_width(d):
    """Her length lying: the columns her squares (not the bear's) span."""
    xs = np.nonzero(((d[..., 3] > 0) & ~tibbers(d)).any(0))[0]
    return xs.max() - xs.min() + 1


def frames():
    """{"<tag>_<frame>": (design-square picture, x, y of its top-left on the design's grid)}."""
    global PIVOT_COL, GROUND
    pal = palette()
    d0 = design()
    mids, _ = shoes(d0)
    PIVOT_COL, GROUND = (mids[0] + mids[-1]) / 2.0, soles_row(d0)
    top_d, body_d, eye_d = design_measure()
    img = head_piece()
    sheets = json.load(open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8"))["sheets"]
    cells, meas = {}, {}
    for sh in sheets:
        cs = keyed_cells(sh)
        for fno, c in zip(sh["frames"], cs):
            if c is None:
                continue
            name = f"{sh['tag']}_{fno}"
            cells[name] = (sh, c)
            m = eye_measure(c[..., :3].astype(float), c[..., 3] > 0)
            meas[name] = m and (m[0][0] - m[1], codex_soles(c) - m[0][0])
    # a sheet with frames standing up straight (UPRIGHT): her eye as high over her soles as the design's; any other
    # its head's scale (eye under the ear tips) times the median of body over head on those sheets
    scale, ratio = {}, []
    for sh in sheets:
        ns = [f"{sh['tag']}_{f}" for f in sh["frames"]]
        up = [n for n in ns if n in UPRIGHT and meas.get(n)]
        heads = [meas[n][0] / top_d for n in ns if meas.get(n) and n not in NO_HEAD]
        if up:
            scale[sh["name"]] = float(np.mean([meas[n][1] / body_d for n in up]))
            if heads:
                ratio.append(scale[sh["name"]] / float(np.mean(heads)))
    k = BODY_K if BODY_K is not None else float(np.median(ratio))
    for sh in sheets:
        ns = [f"{sh['tag']}_{f}" for f in sh["frames"]]
        heads = [meas[n][0] / top_d for n in ns if meas.get(n) and n not in NO_HEAD]
        if sh["name"] not in scale and heads:
            scale[sh["name"]] = float(np.mean(heads)) * k
    for sh in sheets:                                   # never taller than she stands (the death apart)
        ns = [f"{sh['tag']}_{f}" for f in sh["frames"] if meas.get(f"{sh['tag']}_{f}")]
        if sh["tag"] != "dead" and ns and sh["name"] in scale:
            scale[sh["name"]] = max(scale[sh["name"]], max(meas[n][1] for n in ns) / body_d)
    for sh in sheets:
        if sh["name"] not in scale:                     # (no head to measure: the tag's other sheets')
            same = [scale[s["name"]] for s in sheets if s["tag"] == sh["tag"] and s["name"] in scale]
            scale[sh["name"]] = float(np.mean(same))
    for name, (ref, mine) in LIE_SCALE.items():         # lying: as long as in the frame before
        pr, sr = cells[ref]
        pm, sm = cells[mine]
        wr = body_width(CA.resample(sr, scale[pr["name"]], pal))
        wm = body_width(CA.resample(sm, scale[name], pal))
        scale[name] *= wm / wr
    out = {}
    for name, (sh, c) in cells.items():
        step = scale[sh["name"]]
        d = CA.resample(c, step, pal)
        x, y = int(round(PIVOT_COL - CELL_X / step)), 0
        tag = sh["tag"]
        if name not in NO_HEAD and meas.get(name):
            m = eye_measure(c[..., :3].astype(float), c[..., 3] > 0)
            (ey, ex), _ = m
            ys, xs = np.nonzero(c[..., 3] > 0)
            # the resampled frame is cropped by JD.clean? no: resample keeps the cell's grid
            eye_c = (ey / step - 0.5, ex / step - 0.5)
            d, x, y = place_head(d, x, y, img, (eye_d[0] - 0.5, eye_d[1] - 0.5), eye_c, TILTS.get(tag, (0,)),
                                 HEAD_NUDGE.get(name, (0, 0)))
        out[name] = (d, x, y, step)
    print("BODY_K", round(k, 3), "scales", {n: round(v, 2) for n, v in scale.items()})
    return out


def placed(raw=None):
    """{name: (picture, x, y)}: each sheet's lowest soles on the ground (a sheet with no frame on its feet - the
    death's first - takes Codex's ground of the others), then shifted along it (see the module's notes)."""
    raw = raw or frames()
    d0 = design()
    dm, _ = shoes(d0)
    design_mid = (dm[0] + dm[-1]) / 2.0
    sheets = json.load(open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8"))["sheets"]
    # Codex's ground per sheet: the lowest soles of its frames, in Codex pixels
    cg = {}
    for sh in sheets:
        lows = []
        for f in sh["frames"]:
            n = f"{sh['tag']}_{f}"
            if n in raw:
                d, x, y, step = raw[n]
                lows.append(soles_row(d) * step)
        cg[sh["name"]] = max(lows)
    common = float(np.median(list(cg.values())))
    ys = {}
    for sh in sheets:
        g = common if sh["tag"] == "dead" and sh["name"] == "dead_1" else cg[sh["name"]]
        for f in sh["frames"]:
            n = f"{sh['tag']}_{f}"
            if n in raw:
                d, x, y, step = raw[n]
                ys[n] = int(round(GROUND - g / step)) + y
    tags = {}
    for n in sorted(raw, key=lambda n: int(n.rsplit("_", 1)[1])):
        tags.setdefault(n.rsplit("_", 1)[0], []).append(n)
    out = {}
    for tag, names in tags.items():
        known = {}
        if tag == "dead":
            d, x, y, step = raw[names[0]]
            m = np.isin(rgb24(d), DRESS) & (d[..., 3] > 0)
            dd = np.isin(rgb24(d0), DRESS) & (d0[..., 3] > 0)
            for i in range(len(names)):
                known[i] = np.nonzero(dd)[1].mean() - (x + np.nonzero(m)[1].mean())
        elif tag == "run":
            eyes = {}
            for n in names:
                d, x, y, step = raw[n]
                op = d[..., 3] > 0
                g = op & np.isin(rgb24(d), EYES)
                lbl, k = ndimage.label(g, structure=np.ones((3, 3)))
                cs = [ndimage.center_of_mass(lbl == j) for j in range(1, k + 1)]
                eyes[n] = x + min(c[1] for c in cs)
            mids = [np.mean([x + v for v in shoes(raw[n][0])[0]]) - eyes[n] for n in names
                    if shoes(raw[n][0])[0] for x in [raw[n][1]]]
            lead = -float(np.mean(mids))
            for i, n in enumerate(names):
                known[i] = PIVOT_COL + lead - eyes[n]
        else:
            rear = None
            for i, n in enumerate(names):
                d, x, y, step = raw[n]
                mids, low = shoes(d)
                if len(mids) < 2 or ys[n] - y + low < GROUND - 4:
                    continue
                mids = [x + v for v in mids]
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
            out[n] = (d, x + int(round(v)), ys[n])
    for tag, k0 in STILL_TIB.items():                   # her bear lying still: the same picture, where it lies
        ref, rx, ry = out[f"{tag}_{k0}"]
        bear = bear_piece(ref)
        by, bx = np.nonzero(bear)
        for nm in tags[tag]:
            if int(nm.rsplit("_", 1)[1]) <= k0:
                continue
            d, x, y = out[nm]
            d = d.copy()
            mine = bear_piece(d)
            my, mx = np.nonzero(mine)
            d[mine] = 0
            dy, dx = my.max() - by.max(), mx.min() - bx.min()
            ty, tx = by + dy, bx + dx
            ok = (ty >= 0) & (ty < d.shape[0]) & (tx >= 0) & (tx < d.shape[1])
            d[ty[ok], tx[ok]] = ref[by[ok], bx[ok]]
            out[nm] = (d, x, y)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr = placed()
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        import pickle
        pickle.dump(fr, open(os.path.join(a.review, "frames.pkl"), "wb"))
        order = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
        d0 = design()
        for t in order:
            names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
            Z, W, Hh = 3, 120, 110
            can = Image.new("RGB", ((len(names) + 1) * (W * Z + 4), Hh * Z), (40, 40, 40))
            for i, (n, (d, x, y)) in enumerate([("design", (d0, 0, 0))] + [(n, fr[n]) for n in names]):
                tile = Image.new("RGBA", (W, Hh), (96, 112, 96, 255))
                for gx in range(W):
                    tile.putpixel((gx, int(GROUND) + 25), (60, 70, 60, 255))
                tile.alpha_composite(Image.fromarray(d), (x + 40, y + 25))
                can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
            can.save(os.path.join(a.review, f"read_{t}.png"))
        print("written", a.review)


if __name__ == "__main__":
    main()
