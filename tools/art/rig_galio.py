#!/usr/bin/env python3
"""league_galio's sheets from Codex's step-2 strips (assets/source/galio/codex_strips) and the design (hd/front.png).

    python tools/art/rig_galio.py [--review DIR]

Codex drew the 52 action frames on the pack's 7-px grid (tools/art/pack_galio_strips.py: 219 x 146 squares, the
standing point column PIV_X, the soles' row SOLE) and read them back into the design's colours itself (the 1x copies,
one pixel a square). Here, for every frame:
  * the colours: Codex used the design before Zeri's flat look (45 colours, commit b5ba65c5); each of them goes to the
    flat colour the design itself turned it into (LUT: the commonest flat colour at its squares in the two designs),
    then design_galio_hd.flat's lone-square rounds (the eyes kept);
  * the outline: closed first where Codex left it open (strips.complete_outline: a light square touching the ground -
    the wings' upper edges, round the crown; the user: 「有像素缺失的部分吧」), then made 2 squares thick where it is one (the design's 2, the one look's ~1 game
    pixel), closed pinholes of PINHOLE squares or less (the seams round the pasted head showed the ground);
  * the fists: attack 3 / 4 came back with curled spirals again (FISTS): the curl's lines filled with the stone round
    them, knuckle creases cut in (Codex's silhouette kept, no ground showing round a smaller fist);
  * idle = the design breathing (the upper body BREATH rows up over the legs and the tail), hit = the design moved 2 and
    1 squares back.
Then the run's legs are drawn (run_legs: Codex's never alternated) and every frame is brought down twice: for the 1x
sheet (down: 2 x 2 blocks, the face kept) and for the game (dense: 1.5 squares a game pixel, pixel_down.pixelate),
written to assets/source/ppu/galio_<tag>.png + .json (ppu_hd.py's drawn strips; python tools/art/ppu_hd.py --hero galio
then adds the hd_ / lo_ tags). Drawn at PPU 2.0 (76 squares crown to soles = 38 game rows, 52 with the wings); shown at
100 % and 1.5 squares a game pixel - the user, 2026-10-13: 「加里奥在局内看起来太小了」「而且在局内还是太高清了加里奥」
(he was PPU 2.0 at 85 %), picked from sheets of 85-110 % and of 2.0 / 1.5 / 1.2 / 1 squares a game pixel (1 tried:
「1太糊了 用1.5」).
"""
import argparse
import io
import math
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import design_galio_hd as DG  # noqa: E402
import pixel_down as PD  # noqa: E402
import rigkit as K  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "galio")
CODEX = os.path.join(SRC, "codex_strips")
DESIGN = os.path.join(SRC, "hd", "front.png")
OLD_DESIGN = "b5ba65c5"                  # the 45-colour design Codex drew from (before the flat look)
STEM = os.path.join(ROOT, "league", "champions", "league_galio")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
PPU = 2.0
GAME_PPU = 1.65                         # the dense frames' squares a 1x pixel (ppu_hd.py PPU): at SIZE 1.10, 1.5 a game pixel
COLS, ROWS = 219, 146
PIV_X, SOLE = 92, 140                   # pack_galio_strips.py
DESIGN_AT = (42, 37)                    # the cropped design's top-left on that canvas (pack_galio_strips.py's print)
FEET = 11                               # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
# shown at 110 % (hd.rs SIZES; the user: 「在局内还是偏小啊」 - 38 game px crown to soles under 52 with the wings, Darius
# 42): the DLL scales about the frame's centre, so the dense frames are drawn RAISE rows higher, the soles on the ground
SIZE = 1.10
RAISE = round((FEET + 0.5) * GAME_PPU * (1 - 1 / SIZE))
OUTLINE = DG.SHADES["O"]
PINHOLE = 6
SPECK = 8
HEAD_R = 6                              # 1x squares round the eyes where the face is kept (down)
FIX = (60, 62)                          # every 1x frame (2 x 60 + 1) x (2 x 62 + 1), the pivot square in the middle: one
                                        # size, so every dense frame has the same parity and centre (2026-10-14 review)
BREATH = [0, 1, 2, 2, 1, 0]
WAIST = 66                              # the design's row under the belly: the upper body above it breathes
LEGS = (34, 68)                         # the design's columns of the legs below the waist (the arms hang outside them)
TAIL_ROW = 86                           # the design's tail: below this row left of TAIL_COL (it does not breathe)
TAIL_COL = 30
TAGS = ["run", "attack", "attack2", "skill", "skill2", "w_charge", "w_burst", "ult", "ult_loop", "ult_land", "dead"]
# the spiral fists Codex drew again: (tag, index) -> [(box rows r0..r1, cols c0..c1 round the spiral on the canvas, the
# side its knuckles face: "right" for the punch, "down" for a hanging fist)]. Each keeps Codex's silhouette (a smaller
# drawn-in fist left the ground showing round it, the user: 「这里空出来一大块干嘛」): the curl's lines inside it are filled
# with the stone round them, then three knuckle creases are cut in from the knuckle side and one highlight added.
FISTS = {
    ("attack", 3): [((77, 99, 156, 177), "right"), ((89, 110, 58, 83), "down")],
    ("attack", 4): [((85, 105, 150, 168), "right"), ((97, 120, 62, 88), "down")],
}


def ms(ticks):
    return ticks * 1000.0 / 60.0


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def design():
    d = load(DESIGN)
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def old_design():
    raw = subprocess.run(["git", "show", f"{OLD_DESIGN}:assets/source/galio/hd/front.png"], cwd=ROOT,
                         capture_output=True, check=True).stdout
    d = np.asarray(Image.open(io.BytesIO(raw)).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def lut():
    """Old design colour -> the flat colour the design turned it into most often."""
    old, new = old_design(), design()
    assert old.shape == new.shape
    op = (old[..., 3] > 0) & (new[..., 3] > 0)
    table = {}
    for c in np.unique(old[op][:, :3], axis=0):
        m = op & (old[..., :3] == c).all(-1)
        cols, n = np.unique(new[m][:, :3], axis=0, return_counts=True)
        table[tuple(int(v) for v in c)] = tuple(int(v) for v in cols[n.argmax()])
    return table, np.unique(new[new[..., 3] > 0][:, :3], axis=0)


def recolour(a, table, pal):
    out = a.copy()
    op = a[..., 3] > 0
    for y, x in zip(*np.nonzero(op)):
        c = tuple(int(v) for v in a[y, x, :3])
        if c in table:
            out[y, x, :3] = table[c]
        else:
            out[y, x, :3] = pal[((pal.astype(int) - np.array(c)) ** 2).sum(1).argmin()]
    return out


def outline2(a):
    """Where the outer outline is one square thick (the square inside it is lit), one more outline square outside."""
    op = a[..., 3] > 0
    dark = op & (a[..., :3].astype(int).sum(-1) < 70)
    out = a.copy()
    H, W = op.shape
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        for y, x in zip(*np.nonzero(~op)):
            ey, ex, iy, ix = y + dy, x + dx, y + 2 * dy, x + 2 * dx
            if y > SOLE:                   # nothing under the ground row (the soles stay where Codex put them)
                continue
            if 0 <= iy < H and 0 <= ix < W and dark[ey, ex] and op[iy, ix] and not dark[iy, ix]:
                out[y, x] = (*OUTLINE, 255)
    return out


def specks(a, most=SPECK):
    """Loose pieces of outline only, at most `most` squares (the leftover tick beside the pasted crown, a row the
    breathing left under a thigh), cleared."""
    op = a[..., 3] > 0
    lab, k = ndimage.label(op, structure=np.ones((3, 3)))
    dark = a[..., :3].astype(int).sum(-1) < 70
    for i in range(1, k + 1):
        m = lab == i
        if m.sum() <= most and dark[m].all():
            a[m] = 0
    return a


def close_all(a):
    """Every light square still touching the ground 4-wise (the one-square lines complete_outline leaves open) gets an
    outline square there, nothing under the ground row."""
    op = a[..., 3] > 0
    light = op & (a[..., :3].astype(int).sum(-1) >= 70)
    H, W = op.shape
    out = a.copy()
    for y, x in zip(*np.nonzero(light)):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and not op[yy, xx] and yy <= SOLE:
                out[yy, xx] = (*OUTLINE, 255)
    return out


def pinholes(a, most=PINHOLE):
    lab, k = ndimage.label(a[..., 3] == 0)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    for i in range(1, k + 1):
        if i not in border and (lab == i).sum() <= most:
            a[lab == i] = (*OUTLINE, 255)
    return a


def fix_fists(a, specs):
    for (r0, r1, c0, c1), side in specs:
        a = defurl(a, (r0, r1, c0, c1), side)
    return a


def defurl(a, box, side):
    r0, r1, c0, c1 = box
    op = a[..., 3] > 0
    dark = op & (a[..., :3].astype(int).sum(-1) < 70)
    inbox = np.zeros(op.shape, bool)
    inbox[r0:r1, c0:c1] = True
    edge = op & ~ndimage.binary_erosion(op, structure=np.ones((3, 3)))
    edge2 = op & ~ndimage.binary_erosion(op, structure=np.ones((3, 3)), iterations=2)
    curl = inbox & dark & ~edge2
    out = a.copy()
    for _ in range(6):                     # the curl filled from the stone round it, outside in
        todo = [(y, x) for y, x in zip(*np.nonzero(curl))]
        if not todo:
            break
        nxt = curl.copy()
        for y, x in todo:
            nb = [tuple(out[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dy or dx) and op[y + dy, x + dx] and not curl[y + dy, x + dx]
                  and int(out[y + dy, x + dx, :3].astype(int).sum()) >= 70]
            if nb:
                vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True)
                out[y, x, :3] = vals[cnt.argmax()]
                nxt[y, x] = False
        curl = nxt
    # the knuckles: three creases 3 squares long cut in from the knuckle side, evenly over the fist's extent
    m = inbox & op
    ys, xs = np.nonzero(m)
    crease = np.array(DG.SHADES["D"], np.uint8)
    if side == "right":
        lo, hi = ys.min() + 3, ys.max() - 3
        for t in (0.25, 0.5, 0.75):
            y = int(round(lo + (hi - lo) * t))
            xe = xs[ys == y].max()                 # the outline square on the knuckle side
            for k in range(1, 4):
                if out[y, xe - k, :3].astype(int).sum() >= 70:
                    out[y, xe - k, :3] = crease
    else:
        lo, hi = xs.min() + 3, xs.max() - 3
        for t in (0.25, 0.5, 0.75):
            x = int(round(lo + (hi - lo) * t))
            ye = ys[xs == x].max()
            for k in range(1, 4):
                if out[ye - k, x, :3].astype(int).sum() >= 70:
                    out[ye - k, x, :3] = crease
    return out


HEAD_BOX = (26, 45, 36, 61)             # the design's crown and face (rows, columns of the cropped design)
EYE = (39, 52)                          # the middle between its two blue eyes


def crown_gaps(a, before, d):
    """The gaps between the crown's spikes stay clear (the outline closing filled them black - a dark block behind the
    head): inside the head's box, placed by the eyes, a square clear in the design's head and clear in Codex's frame
    before the closing is cleared again."""
    op = a[..., 3] > 0
    eye = op & (a[..., 2].astype(int) > a[..., 0].astype(int) + 80) & (a[..., 1].astype(int) > a[..., 0].astype(int) + 60)
    if not eye.any():
        return a
    ys, xs = np.nonzero(eye)
    dy, dx = int(round(ys.mean())) - EYE[0], int(round(xs.mean())) - EYE[1]
    r0, r1, c0, c1 = HEAD_BOX
    for r in range(r0, r1):
        for c in range(c0, c1):
            y, x = r + dy, c + dx
            if 0 <= y < a.shape[0] and 0 <= x < a.shape[1] and not d[r, c, 3] and not before[y, x, 3]:
                a[y, x] = 0
    H, W = a.shape[:2]
    head = np.zeros((H, W), bool)
    box = np.zeros((H, W), bool)
    for r in range(r0, r1):
        for c in range(c0, c1):
            y, x = r + dy, c + dx
            if 0 <= y < H and 0 <= x < W:
                box[y, x] = True
                head[y, x] = bool(d[r, c, 3])
    # a kept gap with something light behind it on three sides (a wing round the crown) is a hole in that part: it
    # takes the colour found above it (or beside it); open to the sky it stays clear
    fill = {}
    for y, x in zip(*np.nonzero(box & (a[..., 3] == 0))):
        hits = {}
        for v, u in ((-1, 0), (0, -1), (0, 1), (1, 0)):
            yy, xx = y + v, x + u
            while 0 <= yy < H and 0 <= xx < W:
                if a[yy, xx, 3] and not head[yy, xx]:
                    if int(a[yy, xx, :3].astype(int).sum()) >= 70:
                        hits[(v, u)] = tuple(a[yy, xx, :3])
                    break
                if not a[yy, xx, 3] and not box[yy, xx]:
                    break
                yy, xx = yy + v, xx + u
        if len(hits) >= 3:
            fill[(y, x)] = hits.get((-1, 0)) or next(iter(hits.values()))
    for (y, x), col in fill.items():
        a[y, x, :3] = col
        a[y, x, 3] = 255
    # what stands next to a kept gap (a wing's edge) gets a one-square outline; the head's squares are the design's
    op = a[..., 3] > 0
    light = op & ~head & (a[..., :3].astype(int).sum(-1) >= 70)
    for y, x in zip(*np.nonzero(light)):
        for v, u in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + v, x + u
            if 0 <= yy < H and 0 <= xx < W and not op[yy, xx] and yy <= SOLE:
                a[yy, xx] = (*OUTLINE, 255)
    return a


def frame(tag, i, table, pal):
    a = load(os.path.join(CODEX, f"galio_{tag}_{i}_1x.png"))
    a[a[..., 3] == 0] = 0
    a = recolour(a, table, pal)
    a = DG.flat_rounds(a)
    if (tag, i) in FISTS:
        a = fix_fists(a, FISTS[(tag, i)])
    before = specks(a)
    a, _, _ = G.complete_outline(before, color=OUTLINE, feet=SOLE)
    a = pinholes(outline2(close_all(a)))
    return crown_gaps(a, before, design())


def on_canvas(d, dx=0, dy=0):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    x0, y0 = DESIGN_AT
    can[y0 + dy:y0 + dy + d.shape[0], x0 + dx:x0 + dx + d.shape[1]] = d
    return can


def upper_mask(d):
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:H, 0:W]
    legs = (yy >= WAIST) & (xx >= LEGS[0]) & (xx < LEGS[1])
    tail = (yy >= TAIL_ROW) & (xx < TAIL_COL)
    return op & ~legs & ~tail


def breathe(can, mask, k):
    """The masked squares moved k rows up; the squares they uncover take the colour of the square under them."""
    if k == 0:
        return can.copy()
    out = can.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    rest = out.copy()
    out[ys - k, xs] = can[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            below = y + 1
            while below < can.shape[0] and out[below, x, 3] == 0 and mask[below, x]:
                below += 1
            if below < can.shape[0] and rest[below, x, 3] > 0:
                out[y, x] = rest[below, x]
            elif below < can.shape[0] and out[below, x, 3] > 0:
                out[y, x] = out[below, x]
    return out


def down(can):
    """The PPU canvas -> the 1x frame, centred on the pivot's square (FEET 1x rows above the soles). Each 1x square is a
    2 x 2 block: clear under 2 opaque; the outline on the silhouette's edge where any of it is dark, inside where 3 or
    more is (the stone's 2-square lines stay, a line a block cuts in half goes); otherwise its commonest light colour;
    the blue eyes always kept and round them (HEAD_R squares) one light square is enough, so the face and the crown
    read (a plain commonest-colour vote left a black head: the user picked 1 square a game pixel, 「用1吧」)."""
    k = int(PPU)
    px, py = PIV_X + 0.5 - k / 2, SOLE + 1 - FEET * PPU - k / 2          # a block centred on the pivot
    H, W = can.shape[:2]
    nx0, ny0 = int(np.ceil(px / k)), int(np.ceil(py / k))
    Wn, Hn = nx0 + int(np.ceil((W - px) / k)), ny0 + int(np.ceil((H - py) / k))
    big = np.zeros((Hn * k, Wn * k, 4), np.uint8)
    ox, oy = nx0 * k - int(round(px)), ny0 * k - int(round(py))
    sub = can[max(0, -oy):, max(0, -ox):]
    h, w = min(sub.shape[0], big.shape[0] - max(0, oy)), min(sub.shape[1], big.shape[1] - max(0, ox))
    big[max(0, oy):max(0, oy) + h, max(0, ox):max(0, ox) + w] = sub[:h, :w]
    blk = big.reshape(Hn, k, Wn, k, 4).transpose(0, 2, 1, 3, 4).reshape(Hn, Wn, k * k, 4)
    op = blk[..., 3] > 0
    rgb = blk[..., :3].astype(int)
    dark = op & (rgb.sum(-1) < 70)
    light = op & ~dark
    eye = op & (rgb[..., 2] > rgb[..., 0] + 40) & (rgb[..., 2] > 150)
    keep = op.sum(-1) * 2 >= k * k
    edge = keep & ~ndimage.binary_erosion(keep, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    near = ndimage.binary_dilation(eye.any(-1), structure=np.ones((3, 3)), iterations=HEAD_R)
    one = np.zeros((Hn, Wn, 4), np.uint8)
    for j, i in zip(*np.nonzero(keep)):
        if eye[j, i].any() and not edge[j, i]:
            px_ = blk[j, i][eye[j, i]][:, :3]
        elif (edge[j, i] and dark[j, i].any()) or light[j, i].sum() < (1 if near[j, i] else 2):
            one[j, i] = (*OUTLINE, 255)
            continue
        else:
            px_ = blk[j, i][light[j, i]][:, :3]
        cols, n = np.unique(px_, axis=0, return_counts=True)
        one[j, i] = (*cols[n.argmax()], 255)
    ys, xs = np.nonzero(one[..., 3])
    hw, hh = FIX
    assert max(nx0 - xs.min(), xs.max() - nx0) <= hw and max(ny0 - ys.min(), ys.max() - ny0) <= hh, "FIX too small"
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    out[ys - ny0 + hh, xs - nx0 + hw] = one[ys, xs]
    out, _, _ = G.complete_outline(out, color=OUTLINE, feet=hh + FEET)
    return out


# ------------------------------------------------------------------------------------------------ the run's legs
# Codex's first run kept the light leg forward and the dark one back in all 8 frames (the user: 「走路没有交叉步」); legs
# built here read as deformed (「腿部变形？」「还是变形啊」「不还是变形？」「看不到这里变形吗」), so Codex redrew the legs
# (tools/art/pack_galio_run.py, RUN_PROMPT.md -> assets/source/galio/codex_run/) and they are traced frame by frame
# (the user: 「Codex的腿你不会拿来用？然后一帧一帧描了修复？」). Its near leg - one leg drawn in eight phases - is the leg:
# each frame's near leg is Codex's near leg of that frame, the far leg Codex's near leg four frames on (its own far legs
# never crossed the near ones, their hips 7 px apart, and ran into them in frames 1, 2, 8), moved RUN_FAR_DX squares
# behind, in the design's darker greys. Traced: the silhouette kept (a one-square gap closed, holes filled, a lone
# square taken off), repainted flat (a lit rim toward the light, a shadow rim away, mid inside), Codex's claw marks, the
# design's own knee guard (the idle's far-guard browns on the far leg), a clean 2-square outline; the near leg in front.
# The tail's shaft carried on to the hips (Codex left the root out): tail_root. At game density run_dense_true and
# run_dense_clean put right what the averaging made of the legs (blends, notches, a closed pocket). Every version went
# through an independent pixel review before the user saw it (the user: 「你学尼拉做完后内部review 都没问题了再喊我review」).
# The cut the pack made: Codex's upper body kept above game row RUN_CUT, the fists and the tail below it.
RUN_CUT = -2                     # rows from RUN_CUT down are the legs ...
RUN_KEEP = (9, 0, -15, -1)       # ... but the front fist (right of 9, down to row 0) and the back one (left of -15, to -1)
RUN_TAILX = -13                  # and the tail left of this column
RUN_LEGS = os.path.join(SRC, "codex_run")
# round 1's guide (pack_galio_run.py at 606162b8): the hips, the toe / hock per phase, thigh / shin squares
RUN_GUIDE_HIPS = {"near": (-4.5, -3.0), "far": (2.5, -3.5)}
_PLANT, _PUSH, _LIFT, _TUCK = (-6, -9), (-3, -10), (-2, -8), (-5, -7)
RUN_GUIDE = [(11, 0, _PLANT), (6, 0, _PLANT), (1, 0, _PLANT), (-4, 0, _PLANT), (-9, 1, _PUSH), (-9, 7, _LIFT),
             (1, 6, _TUCK), (9, 3, _PLANT)]
RUN_BONE = 11.0
# the frames where Codex drew its legs into each other: its far leg traced by hand (canvas polygon), the rest the near
RUN_FAR_AREA = {0: [(92, 113), (101, 113), (101, 122), (96, 126), (91, 127), (89, 122), (92, 119)],
                1: [(90, 113), (100, 113), (100, 121), (94, 126), (89, 128), (86, 123), (90, 118)],
                7: [(91, 113), (104, 113), (104, 122), (98, 126), (97, 133), (90, 133), (89, 121), (92, 118)]}
RUN_FAR_DX_AT = {3: 6}           # frame 4 (0-based 3): its knee showed only as a point behind the near knee
RUN_FAR_DX = 3                   # the far leg (Codex's near leg four frames on) this many squares to the right: the hips
                                 # almost together, side-on, so the feet pass each other
RUN_NEAR_DX = {6: -3}            # frame 7 (0-based 6): its lifted near foot passed right over the planted far one
RUN_SCRAP = 20                   # a far-leg piece under this many squares left in sight is not shown
RUN_NEAR = ((236, 251, 241), (190, 208, 202), (149, 169, 168))      # lit, mid, shadow
RUN_FAR = ((124, 143, 145), (103, 120, 123), (60, 73, 78))
RUN_CLAW = {"near": (44, 35, 30), "far": (60, 73, 78)}
RUN_LIGHT = (-0.6, -0.8)         # light from the upper left
RUN_GUARD = (80, 88, 37, 47)     # the design's near knee guard: rows, columns (its gold only)
RUN_GUARD_FAR = {(253, 198, 43): (220, 138, 19), (252, 214, 63): (220, 138, 19), (253, 220, 68): (220, 138, 19),
                 (249, 220, 77): (220, 138, 19), (253, 240, 87): (220, 138, 19), (253, 244, 102): (220, 138, 19),
                 (220, 138, 19): (177, 99, 20), (177, 99, 20): (104, 48, 8)}   # the idle's far guard: brown, a little gold
_CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def to_can(x, y):
    """Game pixels from the pivot -> canvas coordinates (the pivot square's corner: down()'s 1x grid)."""
    return PIV_X - 0.5 + PPU * x, SOLE - FEET * PPU + PPU * y


def tail_root(can, tail_from):
    """The tail's shaft carried on to the hips: its own column at RUN_TAILX (in tail_from, Codex's upper body) - the
    last run of stone in it with at most 2 outline squares over and under it (the run of the whole column took the back
    fist's 4-row outline along and stacked it into a black block over the band) - repeated square by square, its top
    rising evenly to sit right under the body's outline where the legs begin, its underside where it is: a root widening
    into the hips (Codex's tail curves up into the body; the whole band raised left black pockets under it). Where the
    body comes within 3 squares of its stone, the band joins it: 2 outline squares under the body's stone (its own
    outline counted), stone down to the band - no stacked outlines, no slit of background between them. Drawn behind
    everything, each of its rows stopping at the first leg square it meets (run on, it peeked out between the legs as
    grey dots)."""
    out = can.copy()
    edge = int(math.floor(to_can(RUN_TAILX, 0)[0])) - 1
    col = tail_from[:, edge]
    top, bot = int(to_can(0, RUN_CUT - 5)[1]), int(to_can(0, RUN_CUT + 4)[1])
    lit = col[:, 3].astype(bool) & (col[:, :3].astype(int).sum(-1) >= 70)
    ink = col[:, 3].astype(bool) & ~lit
    light = [y for y in range(top, bot) if lit[y]]
    if not light:
        return out
    l0 = l1 = light[-1]
    while lit[l0 - 1]:
        l0 -= 1
    r0, r1 = l0, l1
    while r0 > l0 - 2 and ink[r0 - 1]:
        r0 -= 1
    while r1 < l1 + 2 and ink[r1 + 1]:
        r1 += 1
    c1 = int(math.floor(to_can(0.0, 0)[0]))
    body = tail_from[..., 3] > 0
    legs = (out[..., 3] > 0) & ~body
    dark = out[..., 3].astype(bool) & (out[..., :3].astype(int).sum(-1) < 70)

    def under(x):
        """The body's lowest square over the band's stone at column x, how many outline squares end it there, and
        whether stone (not background) lies over those."""
        b = next((y for y in range(l0 - 1, top, -1) if body[y, x]), None)
        n = 0
        while b is not None and b - n > top and dark[b - n, x]:
            n += 1
        return b, n, b is not None and bool(out[b - n, x, 3])

    cut = int(to_can(0, RUN_CUT)[1])
    xe = next((x for x in range(edge + 1, c1) if legs[r0 - 6:r1 + 1, x].any()), c1)
    b, n, _ = under(xe - 1)
    rise = 0 if b is None else max(0, l0 - max(cut, b + 1 + max(0, 2 - n)))
    # the band's top stone row per column: the even rise, never dropping again toward the hips, and where the body is
    # near 1 to 3 outline squares between them (2 under its stone) - a top edge stepping with the body's every notch
    # read as jagged
    plan, prev = {}, None
    for x in range(edge + 1, c1):
        t = l0 - int(round(rise * min(1.0, (x - edge) / max(1, xe - 1 - edge))))
        T = t if prev is None else min(t, prev)
        b, n, stone = under(x)
        joined = b is not None and b >= cut - 1 and t - b - 1 <= 3     # (not up into a gap Codex left in the body)
        if joined:
            lo = b + 1 + (max(0, 2 - n) if stone else 0)
            T = min(max(T, lo), max(lo, b + 4 - n))
        plan[x] = (T, joined, b)
        prev = T
    stopped = set()
    for x, (T, joined, b) in plan.items():
        if joined:
            for yy in range(b + 1, T):
                if not out[yy, x, 3] and not legs[yy, x]:
                    out[yy, x] = (*OUTLINE, 255)
            rows = []
        else:
            rows = [(y - (l0 - T), col[y], ("top", y)) for y in range(r0, l0)]     # its own top outline, raised
        rows += [(yy, col[l0], ("root", yy)) for yy in range(T, l0)]              # the stone under it, widening
        rows += [(y, col[y], ("band", y)) for y in range(l0, r1 + 1)]             # the band, its underside as they are
        for yy, c, key in rows:
            if key in stopped:
                continue
            if legs[yy, x]:
                stopped.add(key)
                continue
            if not out[yy, x, 3]:
                out[yy, x] = c
        if x < xe and lit[l0]:
            thin_ink(out, x, min(T, l0), cut, legs)
    for x in range(edge - 6, edge + 1):                    # and over Codex's own shaft just left of it (frame 3)
        ys = [y for y in range(top, bot) if out[y, x, 3] and out[y, x, :3].astype(int).sum() >= 70]
        if ys:
            t = ys[-1]
            while t - 1 in ys:
                t -= 1
            if not _gold(out[t:t + 1, x:x + 1])[0, 0]:
                thin_ink(out, x, t, cut, legs)
    return out


def thin_ink(out, x, t, cut, legs):
    """Over the tail's stone at column x (its top row t) at most 2 outline squares under the body's stone: 3 or 4
    (Codex's leftover thigh outline stacked on the band's, frame 3) and the lowest of them become the tail's stone. A
    deeper black is Codex's own shadow between the thighs and stays; so does an outline with background over it."""
    light = lambda y: out[y, x, 3] and out[y, x, :3].astype(int).sum() >= 70
    if legs[t, x] or not light(t):
        return
    t0 = t
    while t > t0 - 2 and light(t - 1):
        t -= 1                                             # the top of the stone the band joined
    run = 0
    while out[t - 1 - run, x, 3] and not light(t - 1 - run):
        run += 1
    if 3 <= run <= 4 and light(t - 1 - run):
        for yy in range(max(t - (run - 2), cut - 3), t):
            out[yy, x] = out[t, x]


def upper_only(can):
    """The run canvas without its legs (the fists and the tail kept): what the pack gave Codex."""
    H, W = can.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    x0, y0 = to_can(0, 0)
    rx, ry = np.floor((xx + 0.5 - x0) / PPU), np.floor((yy + 0.5 - y0) / PPU)
    fx, fy, bx, by = RUN_KEEP
    keep = (rx >= fx) & (ry <= fy) | (rx <= bx) & (ry <= by) | (rx < RUN_TAILX)
    out = can.copy()
    out[(ry >= RUN_CUT) & ~keep] = 0
    return out


RUN_THIGH = (-5.0, -4.0)         # Codex's old far thigh left above the cut (game rows -5 to the cut, columns RUN_TAILX
                                 # to -4): its dark greys and their outline read as a black block over the tail


def strip_old_thigh(base):
    """The pack's upper body less what is left of Codex's old far thigh between the tail and the hips (its far greys
    and the outline not next to other stone): the back fist and the belly stay."""
    out = base.copy()
    H, W = base.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    x0, y0 = to_can(0, 0)
    rx, ry = (xx + 0.5 - x0) / PPU, (yy + 0.5 - y0) / PPU
    zone = (ry >= RUN_THIGH[0]) & (ry < RUN_CUT) & (rx >= RUN_TAILX) & (rx <= RUN_THIGH[1])
    rgb = base[..., :3].astype(int)
    key = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
    op = base[..., 3] > 0
    far = op & np.isin(key, [r * 65536 + g * 256 + b for r, g, b in RUN_FAR])
    stone = op & ~_dark(base) & ~far
    gone = zone & (far | (op & _dark(base) & ~ndimage.binary_dilation(stone, structure=np.ones((3, 3)), iterations=2)))
    out[gone] = 0
    return out


def run_guide(name, k):
    """Round 1's skeleton of one leg at phase k: hip, knee, hock, toe (canvas)."""
    hx, hy = to_can(*RUN_GUIDE_HIPS[name])
    toe_dx, lift, (hdx, hdy) = RUN_GUIDE[k]
    toe = (hx + toe_dx, SOLE + 0.5 - lift + (hy - to_can(*RUN_GUIDE_HIPS["near"])[1]))
    knee, hock = K.elbow((hx, hy), (toe[0] + hdx, toe[1] + hdy), RUN_BONE, RUN_BONE, bend=-1)
    if knee[0] < min(hx, hock[0]):
        knee, hock = K.elbow((hx, hy), hock, RUN_BONE, RUN_BONE, bend=1)
    return [(hx, hy), knee, hock, toe]


def _dark(a):
    return a[..., :3].astype(int).sum(-1) < 70


def _gold(a):
    return (a[..., 3] > 0) & (a[..., 0].astype(int) > a[..., 2].astype(int) + 60)


def _inside(poly, shape):
    """The squares whose centres fall inside a polygon (canvas coordinates)."""
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5, yy + 0.5
    inside = np.zeros(shape, bool)
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        cross = (y1 > py) != (y2 > py)
        inside ^= cross & (px < x1 + (py - y1) * (x2 - x1) / ((y2 - y1) if y2 != y1 else 1e-9))
    return inside


def run_split(d, light, k):
    """Codex's near-leg squares in its frame k: two pieces apart -> the lighter piece (it drew the near leg light, the
    far one darker); one piece (the legs drawn into each other) -> all but its far leg traced by hand (RUN_FAR_AREA)."""
    if k in RUN_FAR_AREA:
        return light & ~_inside(RUN_FAR_AREA[k], light.shape)
    rgb = d[..., :3].astype(int)
    key = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
    is_light = light & np.isin(key, [r * 65536 + g * 256 + b for r, g, b in RUN_NEAR + ((244, 250, 246),)])
    is_dark = light & np.isin(key, [r * 65536 + g * 256 + b for r, g, b in RUN_FAR])
    lab, n = ndimage.label(light, structure=np.ones((3, 3)))
    sizes = ndimage.sum(light, lab, range(1, n + 1)) if n else []
    big = [i + 1 for i, z in enumerate(sizes) if z >= 30]
    share = [is_light[lab == i].sum() / max(1, (is_light | is_dark)[lab == i].sum()) for i in big]
    return lab == big[int(np.argmax(share))]


def _smooth(m):
    """A leg's silhouette: a one-square gap closed, its holes filled, a lone square sticking out taken off."""
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, structure=_CROSS))
    for _ in range(2):
        m &= sum(np.roll(m, s, a) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1))) >= 2
    return m


def _shade(sil, pts, pal):
    """Flat faces on a leg silhouette: a lit rim on each row's left (light from the upper left), a shadow rim on its
    right, mid inside - the same way in every frame."""
    out = np.zeros((*sil.shape, 4), np.uint8)
    dist = ndimage.distance_transform_edt(sil)
    ys, xs = np.nonzero(sil)
    centre = np.zeros(sil.shape[0])
    for y in np.unique(ys):
        centre[y] = xs[ys == y].mean()
    lit = (xs < centre[ys]) & (dist[ys, xs] <= 2.0)
    dark = (xs > centre[ys]) & (dist[ys, xs] <= 2.0)
    out[ys, xs, :3] = np.where(lit[:, None], pal[0], np.where(dark[:, None], pal[2], pal[1]))
    out[ys, xs, 3] = 255
    return out


def run_prepare(frames):
    """Codex's near leg in each of its 8 run frames: (the frame the pack gave it, silhouette, claw marks, knee-guard
    centre, the skeleton it was drawn to)."""
    out = []
    for k, (can, _) in enumerate(frames):
        base = upper_only(can)
        d = load(os.path.join(RUN_LEGS, f"galio_run_{k + 1}_1x.png"))
        d[d[..., 3] == 0] = 0
        added = (d[..., 3] > 0) & (base[..., 3] == 0)
        light = added & ~_dark(d)
        near = run_split(d, light, k)
        sil = _smooth(light & near)
        pts = run_guide("near", k)
        foot = np.zeros_like(sil)
        sy, _ = np.nonzero(sil)
        if len(sy):
            foot[sy.max() - 8:] = True
        bottom = np.zeros_like(sil)
        ys_, _ = np.nonzero(sil)
        if len(ys_):
            bottom[ys_.max() - 1:] = True
        claws = added & foot & sil & ~bottom & ((d[..., :3] == RUN_CLAW["near"]).all(-1) | _dark(d))
        inner = claws & ndimage.binary_erosion(sil, structure=_CROSS)
        if inner.sum() >= 2:
            claws = inner
        gold = light & near & _gold(d)
        centre = tuple(int(round(v)) for v in ndimage.center_of_mass(gold)) if gold.any() else None
        out.append((base, sil, claws, centre, pts))
    return out


def run_leg_layer(leg, pal, guard, claw, dx=0):
    _, sil, claws, centre, pts = leg
    if dx:
        sil, claws = np.roll(sil, dx, axis=1), np.roll(claws, dx, axis=1)
        pts = [(x + dx, y) for x, y in pts]
        centre = (centre[0], centre[1] + dx) if centre else None
    layer = _shade(sil, pts, pal)
    layer[claws] = (*claw, 255)
    if centre:
        gx, gy = centre[1] - guard.shape[1] // 2, centre[0] - guard.shape[0] // 2
        K.put(layer, guard, gx, gy)
        # a one-square gap left between the leg's edge and the guard beside it (frame 5: the guard's top tip stood
        # alone in the outline) filled with the leg's colour beside it
        m = layer[..., 3] > 0
        gap = np.zeros_like(m)
        gap[gy:gy + guard.shape[0], gx:gx + guard.shape[1]] = True
        gap &= ~m & np.roll(m, 1, 1) & np.roll(m, -1, 1)
        layer[gap] = np.roll(layer, 1, 1)[gap]
    layer[:int(to_can(0, RUN_CUT)[1]) + 1] = 0
    return layer, layer[..., 3] > 0


def run_frame(k, prep, info=None):
    """Run frame k: Codex's upper body, its near leg of frame k in front, its near leg of frame k + 4 behind as the
    far leg."""
    r0, r1, c0, c1 = RUN_GUARD
    guard = design()[r0:r1, c0:c1].copy()
    g = _gold(guard)
    filled = ndimage.binary_fill_holes(g)
    for y, x in zip(*np.nonzero(filled & ~g)):          # a hole in the guard takes its gold neighbour's colour
        nb = [guard[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= y + dy < g.shape[0] and 0 <= x + dx < g.shape[1] and g[y + dy, x + dx]]
        if nb:
            guard[y, x] = nb[0]
    guard[~filled] = 0
    for _ in range(2):                                     # a square of it hanging on by one side (the design's gold
        g = guard[..., 3] > 0                              # tip under its brown edge: a gold dot on the shin) taken off
        guard[g & (sum(np.pad(g, 1)[1 + dy:1 + dy + g.shape[0], 1 + dx:1 + dx + g.shape[1]]
                       for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))) <= 1)] = 0
    guard_far = guard.copy()
    for c, dc in RUN_GUARD_FAR.items():
        guard_far[(guard[..., :3] == c).all(-1) & (guard[..., 3] > 0), :3] = dc
    base = prep[k][0]
    near, ns = run_leg_layer(prep[k], RUN_NEAR, guard, RUN_CLAW["near"], RUN_NEAR_DX.get(k, 0))
    far, fs = run_leg_layer(prep[(k + 4) % 8], RUN_FAR, guard_far, RUN_CLAW["far"], RUN_FAR_DX_AT.get(k, RUN_FAR_DX))
    near_ring = ndimage.binary_dilation(ns, structure=_CROSS, iterations=2)
    seen = ndimage.binary_opening(fs & ~ns, structure=np.ones((3, 3)))
    # beyond the near leg's outline, a far strip under 3 squares (far grey showing through beside the near knee guard)
    # is taken away - but never the foot it stands on (its claws are narrow)
    beyond = seen & ~near_ring
    lab_b, nb = ndimage.label(beyond, structure=np.ones((3, 3)))
    if nb > 1:
        sizes_b = ndimage.sum(beyond, lab_b, range(1, nb + 1))
        main = 1 + int(np.argmax(sizes_b))
        seen &= ~(beyond & (lab_b != main) & (lab_b > 0))
    lab, n = ndimage.label(seen)
    if n:
        sizes = ndimage.sum(seen, lab, range(1, n + 1))
        seen = np.isin(lab, [i + 1 for i, z in enumerate(sizes) if z >= max(RUN_SCRAP, 0.4 * sizes.max())])
    # the far foot's sole as traced, its bottom 3 rows (the opening took a heel 2 squares thin off: the foot stood on
    # its toe alone over a black heel)
    fy = np.nonzero(fs.any(1))[0]
    if len(fy) and seen.any():
        sole = np.zeros_like(fs)
        sole[fy.max() - 2:] = True
        seen = ndimage.binary_propagation(seen, structure=np.ones((3, 3)), mask=seen | (fs & sole & ~ns))
    out = np.zeros_like(base)
    out[ndimage.binary_dilation(seen, structure=_CROSS, iterations=2) & ~seen] = (*OUTLINE, 255)
    out[seen] = far[seen]
    out[near_ring & ~ns] = (*OUTLINE, 255)
    out[ns] = near[ns]
    upper = base
    top = upper[..., 3] > 0
    out[top] = upper[top]
    out = tail_root(out, base)
    out[SOLE + 1:] = 0
    # the clean-up below the head only (the crown's gaps stay open: a whole-frame pass filled them black)
    legs = int(to_can(0, -20)[1])
    clean = close_all(out.copy())
    tail_x = int(math.floor(to_can(0.0, 0)[0]))
    filled = pinholes(clean.copy())
    hips = int(to_can(0, RUN_THIGH[0])[1])
    clean[hips:, tail_x:] = filled[hips:, tail_x:]         # small holes filled only below the hips and right of the
                                                           # tail band (Codex's own gaps in the body stay open)
    zone_top = int(to_can(0, RUN_THIGH[0])[1])
    loose = specks(clean.copy())
    clean[zone_top:] = loose[zone_top:]                    # loose outline taken only from the old thigh's zone down
    out[legs:] = clean[legs:]
    if info is not None:
        info.update(near=ns, seen=seen, far=fs)
    return out


def run_dense_true(can, f, grid, ours):
    """A dense run frame from the waist down: a square mostly over what run_frame drew (`ours`: the legs, their outline,
    the tail's root - not Codex's tail tip and fists) whose colour lies nowhere under it on the canvas - a mean snapped
    to a third colour (the knee guard's brown and the shin's white to a grey row under the guard, an outline square and
    a grey one to a dark-grey dot on the near leg's edge) - takes the canvas colour covering most of it; then single odd
    squares merged as pixelate does (pixel_down.despeckle)."""
    xs, ys = grid
    out = f.copy()
    top = int(round(f.shape[0] / 2 - RAISE + (RUN_CUT - 0.5) * GAME_PPU)) - 2
    light = (can[..., 3] > 0) & (can[..., :3].astype(int).sum(-1) >= 70)
    Hc, Wc = light.shape
    fixed = np.zeros(f.shape[:2], bool)
    for Y in range(max(0, top), f.shape[0]):
        y0, y1 = ys[Y], ys[Y + 1]
        for X in range(f.shape[1]):
            p = f[Y, X]
            if not p[3] or int(p[0]) + int(p[1]) + int(p[2]) < 70:
                continue
            x0, x1 = xs[X], xs[X + 1]
            area, mine, whole = {}, 0.0, 0.0
            for j in range(max(0, int(np.floor(y0))), min(Hc, int(np.ceil(y1)))):
                hy = min(y1, j + 1) - max(y0, j)
                for i in range(max(0, int(np.floor(x0))), min(Wc, int(np.ceil(x1)))):
                    a = hy * (min(x1, i + 1) - max(x0, i))
                    if a <= 1e-6:
                        continue
                    whole += a
                    mine += a if ours[j, i] else 0.0
                    if light[j, i]:
                        c = tuple(int(v) for v in can[j, i, :3])
                        area[c] = area.get(c, 0.0) + a
            if mine * 2 >= whole and area and tuple(int(v) for v in p[:3]) not in area:
                out[Y, X, :3] = max(area, key=area.get)
                fixed[Y, X] = True
    spk = PD.despeckle(out[top:])
    near = ndimage.binary_dilation(fixed, structure=np.ones((3, 3)))[top:]   # merged only round what was put right
    out[top:][near] = spk[near]
    return out


def run_dense_clean(f):
    """A dense run frame's last pass from the waist down: a clear square between two opaque ones (left-right or up-down) gets
    the outline, and in the waist's outline rows a gap up to 3 squares wide; an outline square with no stone within 2
    squares (a lone black speck) is cleared."""
    out = f.copy()
    top = int(round(f.shape[0] / 2 - RAISE + (RUN_CUT - 0.5) * GAME_PPU)) - 2   # from the waist row down (Codex's
                                                                                 # upper body as it is)
    op = out[..., 3] > 0
    p = np.pad(op, 1)
    gap = ~op & ((p[1:-1, :-2] & p[1:-1, 2:]) | (p[:-2, 1:-1] & p[2:, 1:-1]))
    waist = int(round(f.shape[0] / 2 - RAISE + (RUN_CUT - 0.5) * GAME_PPU))
    for y in range(waist - 2, waist + 3):                  # in the waist's outline rows gaps up to 3 squares wide
        xs = np.nonzero(op[y])[0]
        for a, b in zip(xs, xs[1:]):
            if 1 < b - a <= 4:
                gap[y, a + 1:b] = True
    gap[:top] = False
    out[gap] = (*OUTLINE, 255)
    op = out[..., 3] > 0
    light = op & (out[..., :3].astype(int).sum(-1) >= 70)
    lone = op & ~light & ~ndimage.binary_dilation(light, structure=np.ones((3, 3)), iterations=2)
    lone[:top] = False
    out[lone] = 0
    # round the tail's root (the tip, the belly and the band's start): black with no stone beside it that meets the
    # background is background - a little pocket there closed up at this density into a 4-5 row black corner
    op = out[..., 3] > 0
    light = op & (out[..., :3].astype(int).sum(-1) >= 70)
    thick = op & ~light & ~ndimage.binary_dilation(light, structure=np.ones((3, 3)))
    zone = np.zeros_like(thick)
    W = f.shape[1]
    zone[waist - 1:waist + 7, int(W / 2 + (RUN_TAILX - 4) * GAME_PPU):int(W / 2 - 0.5 * GAME_PPU)] = True
    thick &= zone
    lab, n = ndimage.label(thick, structure=np.ones((3, 3)))
    if n:
        p = np.pad(~op, 1)
        open_ = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
        block = thick[:-1, :-1] & thick[1:, :-1] & thick[:-1, 1:] & thick[1:, 1:]   # a mass, not a 1-row strip
        mass = np.zeros_like(thick)
        mass[:-1, :-1] |= block
        meet = np.intersect1d(np.unique(lab[thick & open_]), np.unique(lab[mass]))
        out[np.isin(lab, meet[meet > 0])] = 0
    return out


def dense(can, one, grid=False):
    """The game's frame: the canvas at GAME_PPU squares a 1x pixel (pixel_down.pixelate; GAME_PPU / SIZE = the 1.5 the
    user picked), RAISE rows up, on a frame of round(GAME_PPU x the 1x frame's size) - grown alike at both ends where
    the drawing needs more - the pivot square's corner at its centre. grid: also the frame's (column, row) edges on the
    canvas, (xs, ys) - frame column i spans canvas x from xs[i] to xs[i + 1]."""
    x0, y0 = to_can(0, 0)
    px, py = x0 + PPU / 2, y0 + PPU / 2                    # the pivot square's centre on the canvas
    lo, (lx, ly) = PD.pixelate(can, GAME_PPU / PPU, (px, py), PD.edge_colour(can))
    W, H = round(one.shape[1] * GAME_PPU), round(one.shape[0] * GAME_PPU)
    ys, xs = np.nonzero(lo[..., 3])
    ys = ys - RAISE
    while W / 2 < max(lx - xs.min(), xs.max() + 1 - lx):
        W += 2
    while H / 2 < max(ly - ys.min(), ys.max() + 1 - ly):
        H += 2
    f = np.zeros((H, W, 4), np.uint8)
    ox, oy = int(np.floor(W / 2 - lx + 0.5)), int(np.floor(H / 2 - ly + 0.5))
    f[ys + oy, xs + ox] = lo[ys + RAISE, xs]
    if grid:
        c = PPU / GAME_PPU                                 # pixelate's squares: lo column j from px + (j - lx) c
        return f, (px + (np.arange(W + 1) - ox - lx) * c, py + (np.arange(H + 1) - oy + RAISE - ly) * c)
    return f


def actions():
    table, pal = lut()
    cells = json.load(open(os.path.join(CODEX, "cells.json"), encoding="utf-8"))
    by_tag = {}
    for f in cells["frames"]:
        by_tag.setdefault(f["tag"], []).append(f)
    d = design()
    idle = on_canvas(d)
    mask = np.zeros(idle.shape[:2], bool)
    x0, y0 = DESIGN_AT
    mask[y0:y0 + d.shape[0], x0:x0 + d.shape[1]] = upper_mask(d)
    out = {"idle": [(pinholes(close_all(specks(breathe(idle, mask, k))), 2), ms(10)) for k in BREATH]}
    for tag in TAGS:
        out[tag] = [(frame(tag, f["index"] + 1, table, pal), f["ms"]) for f in sorted(by_tag[tag], key=lambda f: f["index"])]
    out["hit"] = [(on_canvas(d, dx=-2), 80.0), (on_canvas(d, dx=-1), 120.0)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's dense frames at 4x on magenta here")
    a = ap.parse_args()
    acts = actions()
    sheet = {}
    for tag, frames in acts.items():
        ones, hds = [], []
        prep = run_prepare(frames) if tag == "run" else None
        for k, (can, t) in enumerate(frames):
            if tag == "run":
                can = run_frame(k, prep)
                frames[k] = (can, t)
            one = down(can)
            if tag == "run":
                hd, grid = dense(can, one, grid=True)
                ours = (can[..., 3] > 0) & ~(prep[k][0][..., 3] > 0)
                hd = run_dense_clean(run_dense_true(can, hd, grid, ours))
            else:
                hd = dense(can, one)
            ones.append((one, round(t, 3)))
            hds.append(hd)
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"galio_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"galio_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 4
            tiles = [Image.fromarray(c[0]) for c in frames]
            w, h = tiles[0].size
            big = Image.new("RGBA", (len(tiles) * w * Z, h * Z), (255, 0, 255, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((w * Z, h * Z), Image.NEAREST), (k * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"galio_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_galio#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
