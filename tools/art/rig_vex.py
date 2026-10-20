#!/usr/bin/env python3
"""league_vex's action frames posed from the designs' own squares (the user, 2026-10-20: 「动作帧不用依赖codex参考其他英雄
怎么做的 做完美了喊我review 对照英雄联盟的动作帧来做」 - league_zoe's way: no Codex strips, lossless poses compared with
League's clips).

    python tools/art/rig_vex.py --parts DIR       # the side design with its parts tinted + pose tries
    python tools/art/rig_vex.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_vex.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_vex.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (tools/art/design_vex_model.py; the user's picks 2026-10-20: the Shadow risen, 34 game px from her ear tips
to her soles at PPU 1.5; the drafts mine): idle.png (A-2, 3/4 front, 51 x 63) and side.png (SA-2, side-on facing right
with the same 3/4 face - both eyes - 49 x 63: every action's base). Every pose is lossless: parts cut square by square
from a design and only moved by whole squares, quarter turns about half-integer pivots and mirrors.
Her Shadow is a layer of its own (split by colour: its indigo darks, violet rim and pale spiral eyes; the black outline
squares touching her colours are hers): it stands behind her and follows her a square or two late, and leaves her in
Looming Darkness (the effect flies it to the target, step 3). Where she covered it the Shadow layer is filled with its
own dark, so nothing see-through opens when she moves off it.
Parts of the side design: the near sleeve (hanging down her back from the shoulder to the magenta cross-laced cuff at
the ground; it turns about SHOULDER), the two shoes (rows FOOT_TOP on, split at FOOT_X), the Shadow; the rest is her
body (the hood with its ears, the head, the hair, the torso with the pendant, the trousers).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, Form as _Form, P, pad, sheet, spans  # noqa: E402

HERO = "vex"
# the user, 2026-10-20, on the first review: 「感觉背后的宠物不需要啊」 - no Shadow behind her in any frame; it shows only in
# her spells' effects (step 3). The Shadow layer and the frames' Shadow moves stay in the code, switched off here.
WITH_SHADOW = False
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "vex", "hd")
# the Shadow's colours (design_vex_model's palette): indigo darks, the violet rim, the spiral eyes
SHADOW = {(19, 11, 49), (21, 12, 53), (115, 3, 251), (40, 13, 95), (207, 247, 252), (67, 1, 154), (63, 2, 135)}
SH_DARK = (19, 11, 49)
INK = (8, 2, 16)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


def split(d):
    """(her squares, the Shadow's squares): by colour; a black square is hers when it touches her colours, else it goes
    to the nearer of the two."""
    op = d[..., 3] > 0
    rgb = d[..., :3].astype(int)
    sh = np.zeros(op.shape, bool)
    for c in SHADOW:
        sh |= (rgb == c).all(-1)
    sh &= op
    blk = op & (rgb == INK).all(-1)
    her = op & ~sh & ~blk
    near = ndimage.binary_dilation(her, structure=np.ones((3, 3)))
    dv, ds = ndimage.distance_transform_edt(~her), ndimage.distance_transform_edt(~sh)
    mine = blk & (near | (dv <= ds))
    her, sh = her | mine, sh | (blk & ~mine)
    # her colours in small pieces off her body (a grey square the cut left in the Shadow's eye) are the Shadow's
    lbl, n = ndimage.label(her, structure=np.ones((3, 3)))
    if n > 1:
        big = 1 + int(np.argmax(ndimage.sum(her, lbl, range(1, n + 1))))
        stray = her & (lbl != big)
        her, sh = her & ~stray, sh | stray
    return her, sh


def shadow_layer(d, sh, her):
    """The Shadow's squares in a design-sized layer, the squares she covers inside its outline filled with its dark: in
    each row from its first square to its last (her squares only) - so it stays whole when she moves off it."""
    out = np.zeros_like(d)
    out[sh] = d[sh]
    for y in range(d.shape[0]):
        xs = np.nonzero(sh[y])[0]
        if len(xs):
            hide = her[y].copy()
            hide[:xs.min()] = False
            hide[xs.max() + 1:] = False
            out[y, hide] = (*SH_DARK, 255)
    return out


def stand_col(d, rows=3, shoes=None):
    """Where the design stands: the middle of her shoes' squares in the lowest `rows` rows (`shoes`: their columns; the
    side's sleeve cuff and the Shadow's wisp lie on the ground beside them)."""
    her, _ = split(d)
    ys = np.nonzero(her.any(1))[0]
    low = her[ys.max() - rows + 1:ys.max() + 1].any(0)
    if shoes is not None:
        low[:shoes[0]] = False
        low[shoes[1] + 1:] = False
    xs = np.nonzero(low)[0]
    return int(round((xs.min() + xs.max() + 1) / 2))


# ------------------------------------------------------------------------------------------------- the side's parts
# (side.png read at 20x) the near sleeve hangs down her back from the shoulder (row 42, columns 30-35) to the cuff with
# its magenta cross-laces just over the ground (rows 54-60); behind it columns 22-29 are her cloak's back and hem (they
# stay with the body); the torso starts at column 36
SLEEVE = [(range(42, 58), (30, 35)), (range(58, 62), (29, 34))]
SHOULDER = (32.5, 42.5)               # (x, y) the sleeve turns about
FORWARD_DROP = 4                      # turned forward the 6-square-wide sleeve spans rows 39-45 about SHOULDER, over her
                                      # chin (rows 36-41): it is held this many rows lower, across her chest
FOOT_TOP = 59                         # the shoes: rows FOOT_TOP to the soles, columns FOOT_COLS, near <= FOOT_X
FOOT_COLS = (35, 47)
FOOT_X = 40
HEAD_LOW = 41                         # the head's lowest row (the chin): a lean moves it as one block
ISLAND = 80                           # loose pieces up to this many squares are dropped once the sleeve moves: the back of
                                      # her cloak (69 squares, columns 20-29 under row 54) hangs on the sleeve and floats
                                      # off when it swings


# one face in every frame (the user, 2026-10-20: 「脸还会一大一小 为什么？」 - the idle's face was drawn bigger than the
# side's; then 「这个脸不是最好的吗 为什么不用啊」 pointing at the side's own face): the side's head - her squares from its
# ear tips down to its chin, rows to SIDE_CHIN - goes on the idle's body (the idle's own head, its rows to IDLE_CHIN,
# taken off) moved IDLE_HEAD_SHIFT so the chin sits on the idle's neck; the side frames keep the side's head as it is
SIDE_CHIN, IDLE_CHIN = 40, 42
IDLE_HEAD_SHIFT = (-5, 2)             # (dx, dy): the side's eyes (columns 37 / 44, row 34) over the idle's (32 / 38, 37)


def side_head_on(d):
    """idle.png's own squares (her, the Shadow left out) with its head swapped for the side's."""
    import strips
    import pixel_down as PD
    her, _ = split(d)
    out = d.copy()
    out[~her] = 0
    out[:IDLE_CHIN + 1] = 0
    side = load("side.png")
    sher, _ = split(side)
    dx, dy = IDLE_HEAD_SHIFT
    ys, xs = np.nonzero(sher[:SIDE_CHIN + 1])
    for y, x in zip(ys, xs):
        Y, X = y + dy, x + dx
        if 0 <= Y < out.shape[0] and 0 <= X < out.shape[1]:
            out[Y, X] = side[y, x]
    # the idle hood's lower edge beside her neck was outline only: with the hood gone it hung on as a thin line -
    # outline squares in the neck rows with no colour beside them go
    ink = PD.edge_colour(d)
    for _ in range(1):
        op = out[..., 3] > 0
        col = op & (np.abs(out[..., :3].astype(int) - ink).sum(-1) > 30)
        near = ndimage.binary_dilation(col, structure=R.CROSS)
        orphan = op & ~col & ~near
        orphan[:IDLE_CHIN + 1] = False
        orphan[IDLE_CHIN + 4:] = False
        out[orphan] = 0
    out = drop_islands(out, 10)
    keep = np.zeros(out.shape[:2], bool)
    keep[33 + dy:40 + dy, 33 + dx:46 + dx] = True              # the side's face (rows 33-39, columns 33-45)
    pad_ = np.pad(out, ((1, 1), (1, 1), (0, 0)))
    pad_, _, _ = strips.complete_outline(pad_, color=PD.edge_colour(d), feet=out.shape[0], keep=np.pad(keep, 1))
    return pad_[1:-1, 1:-1]


def design():
    d = load("side.png")
    her, sh = split(d)
    D = CutDesign(d, px=stand_col(d, shoes=FOOT_COLS))
    D.part("shadow", sh)
    D.part("sleeve", D.rows(spans(SLEEVE)) & her)
    feet = D.box(FOOT_TOP, D.H - 1, *FOOT_COLS) & her & ~D.parts["sleeve"]
    xx = np.mgrid[0:D.H, 0:D.W][1]
    D.part("far_foot", feet & (xx > FOOT_X))
    D.part("near_foot", feet & (xx <= FOOT_X))
    D.part("body", D.rest())
    D.shadow_full = shadow_layer(d, sh, her)
    return D


TINT = {"shadow": (255, 200, 0), "sleeve": (60, 120, 255), "far_foot": (255, 60, 60), "near_foot": (0, 220, 255)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# the idle's head (the user, 2026-10-20: 「待机时头有点大」): the 3/4 design's hood is 32 squares wide against the side's 28
# for the same height, so it is cut down by whole rows and columns, least loss first (design_vex_model.keep_axis): the
# band from her ear tips (row 16) to her chin (row HEAD_BAND[1]), HEAD_DROP rows from the hood and its ears (the face's
# rows kept) and HEAD_DROP_COLS columns either side of the face (its columns kept); the band sits back on her shoulders
# with the face's first column where it was, and the outline is closed round the joint
HEAD_BAND = (16, 41)
HEAD_FACE = (range(35, 42), range(29, 43))     # rows / columns of her face in idle.png (eyes 36-38, mouth 40)
HEAD_DROP, HEAD_DROP_COLS = 5, 7          # 6 rows / 9 columns cut into the ears


def small_head(d):
    """idle.png's own squares with the head band cut down (her squares only; the Shadow's left out)."""
    import design_vex_model as DM
    import strips
    import pixel_down as PD
    her, _ = split(d)
    src = d.copy()
    src[~her] = 0
    r0, r1 = HEAD_BAND
    fr, fc = HEAD_FACE
    band = src[r0:r1 + 1]
    rows = DM.keep_axis([band[y] for y in range(band.shape[0])], band.shape[0] - HEAD_DROP,
                        range(fr.start - r0, min(fr.stop, r1 + 1) - r0))
    sub = band[rows]
    cols = DM.keep_axis([sub[:, x] for x in range(sub.shape[1])], sub.shape[1] - HEAD_DROP_COLS, fc)
    head = sub[:, cols]
    out = src.copy()
    out[:r1 + 1] = 0
    left = fc.start - cols.index(fc.start)
    top = r1 + 1 - head.shape[0]
    m = head[..., 3] > 0
    view = out[top:r1 + 1, left:left + head.shape[1]]
    view[m] = head[m]
    keep = np.zeros(out.shape[:2], bool)
    keep[fr.start:fr.stop, fc.start:fc.stop] = True
    pad_ = np.pad(out, ((1, 1), (1, 1), (0, 0)))
    pad_, _, _ = strips.complete_outline(pad_, color=PD.edge_colour(d), feet=out.shape[0], keep=np.pad(keep, 1))
    return pad_[1:-1, 1:-1]


class Form:
    """The designs' layers; pose() / front() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.L["shadow"] = pad(D.shadow_full)
        idle = load("idle.png")
        her, sh = split(idle)
        self.idle_her = self.placed(side_head_on(idle), None, idle)
        self.idle_shadow = self.placed(shadow_layer(idle, sh, her), None, idle)

    def placed(self, d, mask=None, ref=None):
        """Another design (its `mask` squares) in a padded layer of the side design's size, standing on the same point
        and ground (`ref`: the design whose standing point to use)."""
        ref = d if ref is None else ref
        src = d.copy()
        if mask is not None:
            src[~mask] = 0
        lay = np.zeros((self.D.H + 2 * P, self.D.W + 2 * P, 4), np.uint8)
        ys = np.nonzero((ref[..., 3] > 0).any(1))[0]
        top = P + self.D.ground - (ys.max() + 1)
        left = P + self.D.px - stand_col(ref, shoes=IDLE_SHOES)
        x0, x1 = max(0, left), min(lay.shape[1], left + src.shape[1])
        lay[top:top + src.shape[0], x0:x1] = src[:, x0 - left:x1 - left]
        return lay

    def pose(self, crouch=0, whole=(0, 0), sleeve=(0, 0), rot=0, feet=None, lean=0, shadow=(0, 0), no_shadow=False,
             fill=True):
        """crouch: rows her body (with the sleeve) sets down onto the shoes; whole: the whole figure; sleeve: the sleeve
        moved, rot its quarter turns counter-clockwise about SHOULDER (1: pointing forward, 2: up, 3: back); feet:
        ((near dx, dy), (far dx, dy)); lean: the body bent forward over the shoes one square every `lean` rows (negative:
        back) - leant(); shadow: the Shadow's move from where it stands (it follows her `whole`); no_shadow: it is away."""
        if crouch < 0:
            raise ValueError("the body never lifts off the shoes")
        wx, wy = whole
        ux, uy = wx, wy + crouch
        (nx, ny), (fx, fy) = feet or ((0, 0), (0, 0))
        L = self.L
        feet_l = [(L["far_foot"], dict(dx=wx + fx, dy=wy + fy)), (L["near_foot"], dict(dx=wx + nx, dy=wy + ny))]
        moved = sleeve != (0, 0) or rot % 4
        drop = FORWARD_DROP if rot % 4 == 1 else 0
        sl = (L["sleeve"], dict(dx=ux + sleeve[0], dy=uy + sleeve[1] + drop, rot=rot, about=SHOULDER))
        upper = [(L["body"], dict(dx=ux, dy=uy))]
        # turned forward or up the sleeve is in front of her; hanging or swung back it is behind her body
        upper = upper + [sl] if rot % 4 in (1, 2) else [sl] + upper
        if lean:
            up = leant(R.compose(self.rig, upper), self.rig.oy + uy, lean)
            can = R.compose(self.rig, feet_l)
            m = up[..., 3] > 0
            can[m] = up[m]
        else:
            can = R.compose(self.rig, feet_l + upper)
        if moved:
            can = drop_islands(can)
        if fill:
            can = self.close_holes(can)
        if WITH_SHADOW and not no_shadow:
            sx, sy = shadow
            back = R.compose(self.rig, [(L["shadow"], dict(dx=wx + sx, dy=wy + sy))])
            m = can[..., 3] > 0
            back[m] = can[m]
            can = back
        return can

    def front(self, crouch=0, whole=(0, 0), shadow=(0, 0), flash=False):
        """The 3/4 idle design, her body (above IDLE_LEG_ROW) set down `crouch` rows onto her own legs, the Shadow
        moved `shadow`."""
        legs, top = self.idle_her.copy(), self.idle_her.copy()
        cut_row = P + IDLE_LEG_ROW
        legs[:cut_row] = 0
        top[cut_row:] = 0
        wx, wy = whole
        sx, sy = shadow
        back = [(self.idle_shadow, dict(dx=wx + sx, dy=wy + sy))] if WITH_SHADOW else []
        can = R.compose(self.rig, back + [(legs, dict(dx=wx, dy=wy)), (top, dict(dx=wx, dy=wy + crouch))])
        return R.flash(can) if flash else can

    ref_holes = None
    MOST = _Form.MOST

    def close_holes(self, can):
        """Small enclosed holes the side lacks, filled (league_wukong); her reference is the plain pose without the
        Shadow."""
        if self.ref_holes is None:
            idle = self.pose(fill=False, no_shadow=True)
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


IDLE_SHOES = (27, 40)                 # the idle design's shoes' columns (the sleeves' cuffs lie beside them)
IDLE_LEG_ROW = 58                     # the idle design's shoes: rows from here down stay while the body breathes


IDLE_CROUCH = (0, 0, 0, 1, 1, 1, 1, 0)   # the idle's body set down a row (its breath)
FEET_1X = 3                           # the 1x idle's shoes: its lowest rows that stay while the body breathes


def still_breath(ones):
    """The 1x idle (the cards, the encyclopedia and the face icons draw it): a body set down one fine row is set down
    2/3 of a 1x pixel, and brought down to 1x that way its face smeared (the user, 2026-10-20: 「薇古丝发现个问题 脸变形？」).
    So every 1x idle frame is the standing frame's own pixels, its body above the shoes set down one whole pixel on the
    frames the fine one breathes, each centred on the pivot in its own frame size."""
    base = ones[0][0]
    out = []
    for (one, ms), c in zip(ones, IDLE_CROUCH):
        a = base.copy()
        if c:
            ys = np.nonzero(a[..., 3].any(1))[0]
            cut = ys.max() + 1 - FEET_1X                 # the shoes' first row
            body = a[:cut].copy()
            a[:cut] = 0
            m = body[..., 3] > 0
            low = a[1:cut + 1]
            low[m] = body[m]                             # the body one pixel lower, over the shoes' top row
        H, W = one.shape[:2]
        h, w = a.shape[:2]
        dy, dx = (h - H) // 2, (w - W) // 2
        if dy >= 0 and dx >= 0:
            if a[:dy].any() or a[h - dy:].any() or a[:, :dx].any() or a[:, w - dx:].any():
                sys.exit("still_breath: the standing 1x idle does not fit a breathing frame")
            fit = a[dy:dy + H, dx:dx + W]
        else:
            fit = np.zeros_like(one)
            fit[-dy:-dy + h, -dx:-dx + w] = a
        out.append((fit, ms))
    return out


EYE = (248, 3, 175)                   # her eyes' magenta (the side's face: one fine square each)
SKIN = (221, 230, 228)


def one_with_eyes(can, px, py, hw, hh, ppu, need=0.5):
    """ppu_rig.one_of, her eyes kept: brought down to 1x by the commonest colour, the one-square magenta eyes were
    outvoted by her skin and lids and the 1x frames lost them (the user, 2026-10-20: 「下面的眼睛怎么变色了」). Every 1x
    square over an eye square (EYE beside her skin) takes the eye's colour."""
    one = _ONE_OF(can, px, py, hw, hh, ppu, need)
    rgb = can[..., :3].astype(int)
    op = can[..., 3] > 0
    skin = op & (rgb == SKIN).all(-1)
    eye = op & (rgb == EYE).all(-1) & ndimage.binary_dilation(skin, structure=R.CROSS)
    for y, x in zip(*np.nonzero(eye)):
        j = int(np.floor((y + 0.5 - py) / ppu + 0.5)) + hh
        i = int(np.floor((x + 0.5 - px) / ppu + 0.5)) + hw
        if 0 <= j < one.shape[0] and 0 <= i < one.shape[1]:
            one[j, i] = (*EYE, 255)
    return one


_ONE_OF = R.one_of


def export(F, acts):
    """Rig.export with the 1x idle's breath set down whole pixels (still_breath) and her eyes kept (one_with_eyes)."""
    R.one_of = one_with_eyes
    write = R.G.write_sheet

    def write_sheet(stem, sheet, *a, **kw):
        if "idle" in sheet:
            sheet = dict(sheet, idle=still_breath(sheet["idle"]))
        return write(stem, sheet, *a, **kw)
    R.G.write_sheet = write_sheet
    try:
        F.rig.export(acts)
    finally:
        R.G.write_sheet = write
        R.one_of = _ONE_OF


def leant(can, oy, per):
    """Her body bent over her shoes on an even line, no square resampled (league_zoe's): every row above FOOT_TOP one
    square further forward every `per` rows (negative: back), the head - rows to HEAD_LOW - one block by its lowest
    row's amount, so the face is never sheared."""
    out = np.zeros_like(can)
    sgn, per = (1 if per > 0 else -1), abs(per)
    for y in range(can.shape[0]):
        ref = max(y - oy, HEAD_LOW)
        sh = sgn * ((FOOT_TOP - ref) // per) if ref < FOOT_TOP else 0
        if sh > 0:
            out[y, sh:] = can[y, :-sh]
        elif sh < 0:
            out[y, :sh] = can[y, -sh:]
        else:
            out[y] = can[y]
    return out


def drop_islands(can, most=ISLAND):
    op = can[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n < 2:
        return can
    out = can.copy()
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    for k, sz in enumerate(sizes, 1):
        if sz <= most:
            out[lbl == k] = 0
    return out


def shift(can, dx, dy):
    out = np.zeros_like(can)
    H, W = can.shape[:2]
    ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
    yd, xd = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = can[yd, xd]
    return out


def form():
    F = Form(design(), rig_pad=(50, 60, 50, 20))
    F.rig.fill_rows = (FOOT_TOP - 4, F.D.H - 1)
    F.rig.idle_canvas = F.pose()
    return F


def tries(F):
    p = F.pose
    return [p(), p(rot=1), p(rot=2), p(rot=3), p(crouch=2, rot=1, lean=4), p(no_shadow=True), F.front(),
            F.front(crouch=1, shadow=(0, -1))]


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_vex.py) come from these
MS = {"idle": [150] * 8, "run": [100] * 8,
      "attack": [80, 70, 80, 100, 120], "skill": [80, 70, 90, 90, 90, 80], "skill_w": [60, 70, 90, 100, 130],
      "skill2": [80, 80, 80, 90, 90, 80], "ult": [80, 70, 80, 100, 120], "ult_dash": [100, 150, 150],
      "ult_hit": [100, 150, 150], "hit": [100, 100], "dead": [100, 110, 120, 150, 60, 60, 100, 500]}
LIE_SINK = 4                          # lying on her back: the hood's ears' rows hidden by the ground


def frames_all(F):
    p = F.pose
    rig = F.rig
    out = {}

    def tumble(k, dx, up, **kw):
        """The side pose (without the Shadow) turned k quarter turns counter-clockwise (3: forward), up rows in the air."""
        return shift(R.lie(rig, p(no_shadow=True, **kw), k, dx=dx, sink=0), 0, -up)
    # idle (League's Vex Idle: she slouches on the spot, the Shadow drifting behind her): the 3/4 design's body sets
    # down a row onto its shoes, the Shadow rises and sinks a row half a cycle later
    out["idle"] = [F.front(crouch=c, shadow=(0, s)) for c, s in zip(IDLE_CROUCH, (0, -1, -1, -1, 0, 0, 0, 0))]
    # auto attack (League's Attack_1: the near sleeve drawn back and flung forward, the bolt leaving the cuff, then it
    # drops back): the sleeve back, flung forward (frame 2: the bolt), held as she settles, hanging again
    out["attack"] = [p(sleeve=(-2, 0), shadow=(-1, 0)), p(whole=(1, 0), rot=1, shadow=(1, 0)),
                     p(crouch=1, whole=(1, 0), rot=1, shadow=(2, 0)), p(whole=(1, 0), shadow=(1, 0)), p()]
    # Q Mistral Bolt (League's Spell1: a low crouch with the sleeve back, then a lunge pushing the gust forward, the
    # Shadow surging after her): crouched with the sleeve back, rising, the lunge with the sleeve thrust forward (frame 3:
    # the bolt), held, settling back
    lunge = ((1, 0), (-2, 0))         # the near shoe forward, the far one back: League's wide lunge
    out["skill"] = [p(crouch=2, sleeve=(-2, 0), feet=((1, 0), (-1, 0)), shadow=(-1, 0)),
                    p(crouch=2, whole=(1, 0), sleeve=(-2, -1), feet=lunge, shadow=(0, 0)),
                    p(crouch=1, whole=(3, 0), rot=1, lean=8, feet=lunge, shadow=(4, -1)),
                    p(crouch=1, whole=(3, 0), rot=1, lean=8, feet=lunge, shadow=(5, -1)),
                    p(crouch=1, whole=(2, 0), shadow=(3, 0)), p(whole=(1, 0), shadow=(1, 0))]
    # W Personal Space (League's Spell2: the sleeves swept up, then slammed out as the shock wave bursts round her and the
    # Shadow wraps her): crouched, a hop with the sleeve swung back, landing crouched with the sleeve out (frame 3: the
    # wave), the Shadow closing round her, standing
    out["skill_w"] = [p(crouch=2, shadow=(0, -1)), p(whole=(0, -4), sleeve=(-2, -1), shadow=(-1, -3)),
                      p(crouch=2, rot=1, feet=((1, 0), (-1, 0)), shadow=(4, -2)), p(crouch=1, rot=1, shadow=(2, -1)), p()]
    # E Looming Darkness (League's Spell3: a hop and a kick that sends the Shadow off to the spot): crouched with the
    # sleeve back, up with the sleeve flung forward (frame 2: the Shadow leaves her - the effect flies it), coming down
    # alone, landing, standing, the Shadow back behind her
    out["skill2"] = [p(crouch=2, sleeve=(-2, 0)), p(whole=(1, -5), rot=1, no_shadow=True), p(whole=(2, -3), rot=1, no_shadow=True),
                     p(crouch=2, whole=(2, 0), no_shadow=True), p(whole=(1, 0), no_shadow=True), p(shadow=(-2, 0))]
    # R Shadow Surge's throw (League's Spell4_Cast: crouched, wound up, the missile flung forward with the whole arm):
    # crouched with the sleeve back, up and wound back, the throw (frame 3: the missile), held, standing
    out["ult"] = [p(crouch=2, sleeve=(-2, 0), shadow=(0, -1)), p(whole=(-1, -3), sleeve=(-3, -1), shadow=(-2, -4)),
                  p(whole=(2, -2), rot=1, shadow=(3, -2)), p(crouch=1, whole=(2, 0), rot=1, feet=((1, 0), (-1, 0)),
                                                              shadow=(3, -1)), p(whole=(1, 0), shadow=(1, 0))]
    # the surge (League's Spell4_Dash: she flies at the mark stretched out forward; the surge effect is the Shadow):
    # crouched to spring, then flying low over the ground leant far forward, the sleeve thrust ahead (turned whole she
    # flew with her face on its side)
    out["ult_dash"] = [p(crouch=2, rot=1, no_shadow=True), p(whole=(4, -6), rot=1, lean=4, no_shadow=True),
                       p(whole=(6, -5), rot=1, lean=4, no_shadow=True)]
    # the blow on landing (League's Spell4_Attack: she comes down swinging the sleeve through the mark): up with the
    # sleeve back, the swing (frame 2: the blow), standing with the Shadow back
    out["ult_hit"] = [p(whole=(0, -4), sleeve=(-2, -1), no_shadow=True), p(crouch=2, rot=1, shadow=(2, 0)), p(crouch=1)]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]

    # the death (League's Death: she reels, tips over backwards and lands on her back, then lies still; the Shadow
    # sinks away): reeling, crouched, tipping back (a quarter turn, in the air), on her back, a bounce, lying
    def lying(up=0, dx=-8):
        can = R.lie(rig, p(no_shadow=True), 1, dx=dx, sink=LIE_SINK)
        can[rig.GY:] = 0
        return shift(can, 0, -up)
    out["dead"] = [p(whole=(-1, 0), shadow=(-1, 1)), p(crouch=2, whole=(-2, 0), shadow=(-2, 3)),
                   shift(R.lie(rig, p(no_shadow=True), 1, dx=-6, sink=0), 0, -4), lying(), lying(2), lying(), lying(),
                   lying()]
    return out


def run(F):
    """League's Run: a slouched shuffle, the sleeves trailing. Her shoes step whole under the body (stride 2), the body
    bobbing a row on each contact, the Shadow gliding a square behind."""
    from rig_wukong import _steps
    st = dict(_steps(2, (1, 1, 1)))
    out = []
    for i, ((ndx, nup), (fdx, fup), bob) in enumerate(zip(st["near"], st["far"], st["bob"])):
        out.append(F.pose(whole=(0, bob), feet=((ndx, -nup), (fdx, -fup)), shadow=(-1 - (i // 2) % 2, -(i % 4 == 2))))
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": run(F), **{k: v for k, v in a.items() if k != "idle"}}
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
        export(F, frames(F))
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
