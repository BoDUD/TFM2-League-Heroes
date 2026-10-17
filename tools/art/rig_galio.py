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
    1 squares back; the design with both fists a size smaller and the tail held up off the ground (design());
  * run = the idle walking, league_nautilus / league_braum's way (walk_frame): Codex's run never alternated its legs, and
    every sprint after it - legs built here, Codex's redrawn legs traced - read as deformed or 「完全脱节」 (the user:
    「你向前那样冲刺模型永远会变形」).
Every frame is then brought down twice: for the 1x
sheet (down: 2 x 2 blocks, the face kept) and for the game (dense: 1.5 squares a game pixel, pixel_down.pixelate),
written to assets/source/ppu/galio_<tag>.png + .json (ppu_hd.py's drawn strips; python tools/art/ppu_hd.py --hero galio
then adds the hd_ / lo_ tags). Drawn at PPU 2.0 (76 squares crown to soles = 38 game rows, 52 with the wings); shown at
100 % and 1.5 squares a game pixel - the user, 2026-10-13: 「加里奥在局内看起来太小了」「而且在局内还是太高清了加里奥」
(he was PPU 2.0 at 85 %), picked from sheets of 85-110 % and of 2.0 / 1.5 / 1.2 / 1 squares a game pixel (1 tried:
「1太糊了 用1.5」).
"""
import argparse
import io
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
TAGS = ["attack", "attack2", "skill", "skill2", "w_charge", "w_burst", "ult", "ult_loop", "ult_land", "dead"]
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


# The design as the user had it changed for the walk (2026-10-14: 「尾巴怎么长在地上了？」「拳头缩小点不就好了吗 然后尾巴不能
# 放地上啊」): both fists a size smaller - each loses its two cheapest interior rows and columns (least loss: the squares
# most like their neighbours), the wrist row joined to the forearm as drawn, the outline and the knuckles kept - and the
# tail held up TAIL_UP rows, under the smaller near fist (it lay along the ground at the near ankle). hd/front.png stays the
# approved file; this is applied as it is read.
FIST_BOXES = (((79, 89, 16, 32), (18, 30)),       # the near fist: design rows, columns (incl.) with its outline; its stone
              ((79, 91, 68, 84), (70, 82)))       # the far fist (to its knuckle tips' outline)
FIST_CUT = 2
TAIL_BOXES = ((85, 90, 0, 13), (90, 90, 14, 35), (91, 98, 0, 28), (91, 95, 29, 34))   # the tail (rows, columns incl.):
                                 # its tip, its shaft's top outline (shared with the old fist), its shaft - not the
                                 # near shin's outline at column 35
TAIL_UP = 6


def smaller_fist(d, block, stone, n=FIST_CUT):
    """A fist less its n cheapest interior rows (under the wrist row, above the knuckles) and columns, still centred and
    joined at the wrist; the forearm's bottom row outside it takes the outline."""
    r0, r1, c0, c1 = block
    b0, b1 = stone
    box = d[r0:r1 + 1, c0:c1 + 1].copy()
    k = box[..., 0].astype(int) * 65536 + box[..., 1].astype(int) * 256 + box[..., 2]
    cost = lambda a, b, c: int((a != b).sum() + (c != b).sum())
    cols = sorted((cost(k[:, j - 1], k[:, j], k[:, j + 1]), j) for j in range(b0 - c0 + 1, b1 - c0))
    rows = sorted((cost(k[i - 1], k[i], k[i + 1]), i) for i in range(1, box.shape[0] - 4))

    def pick(c):
        out = []
        for _, j in c:
            if all(abs(j - o) > 1 for o in out):
                out.append(j)
            if len(out) == n:
                return out
        return out

    gone_c, gone_r = pick(cols), pick(rows)
    small = box[np.ix_([i for i in range(box.shape[0]) if i not in gone_r],
                       [j for j in range(box.shape[1]) if j not in gone_c])]
    d[r0 + 1:r1 + 1, c0:c1 + 1] = 0
    x = c0 + n // 2
    d[r0:r0 + small.shape[0], x:x + small.shape[1]] = small
    for c in range(max(0, c0 - 2), min(d.shape[1], c1 + 3)):
        if not x <= c < x + small.shape[1] and d[r0, c, 3]:
            d[r0, c] = (*OUTLINE, 255)
    return d


def tail_up(d, up=TAIL_UP):
    """The tail's squares moved up `up` rows, behind what is there -> (design, the squares the tail now shows on)."""
    m = np.zeros(d.shape[:2], bool)
    for r0, r1, c0, c1 in TAIL_BOXES:
        m[r0:r1 + 1, c0:c1 + 1] = True
    m &= d[..., 3] > 0
    tail = d.copy()
    d[m] = 0
    shown = np.zeros_like(m)
    for y, x in zip(*np.nonzero(m)):
        if not d[y - up, x, 3]:
            d[y - up, x] = tail[y, x]
            shown[y - up, x] = True
    return d, shown


def approved_design():
    """hd/front.png as approved, cropped: what Codex's frames are recoloured and mended against (lut, crown_gaps)."""
    d = load(DESIGN)
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def design_parts():
    """-> (the design the idle, the walk and the hit are made of, the tail's squares in it)."""
    d = approved_design()
    for block, stone in FIST_BOXES:
        d = smaller_fist(d, block, stone)
    return tail_up(d)


def design():
    return design_parts()[0]


def old_design():
    raw = subprocess.run(["git", "show", f"{OLD_DESIGN}:assets/source/galio/hd/front.png"], cwd=ROOT,
                         capture_output=True, check=True).stdout
    d = np.asarray(Image.open(io.BytesIO(raw)).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def lut():
    """Old design colour -> the flat colour the design turned it into most often."""
    old, new = old_design(), approved_design()
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
    return crown_gaps(a, before, approved_design())


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
    tail = design_parts()[1]                        # the tail held up under the near fist: it does not breathe
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


def to_can(x, y):
    """Game pixels from the pivot -> canvas coordinates (the pivot square's corner: down()'s 1x grid)."""
    return PIV_X - 0.5 + PPU * x, SOLE - FEET * PPU + PPU * y


def dense(can, one):
    """The game's frame: the canvas at GAME_PPU squares a 1x pixel (pixel_down.pixelate; GAME_PPU / SIZE = the 1.5 the
    user picked), RAISE rows up, on a frame of round(GAME_PPU x the 1x frame's size) - grown alike at both ends where
    the drawing needs more - the pivot square's corner at its centre."""
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
    return f


# ------------------------------------------------------------------------------------------------ the walk
# The run is league_nautilus's / league_braum's approved walk (the user: 「你不要向前冲刺交叉腿 你按照泰坦布隆那种走路方式这种
# 腿就不会变形」「你向前那样冲刺模型永远会变形」, after the traced sprint's legs read as 「完全脱节」): the idle as it is -
# body, wings, fists, tail - and the design's own two legs under the belly (row WALK_BAND), the near leg (WALK_NEAR) and
# the far one (WALK_FAR); in each frame a leg is lifted by losing its top rows (the thigh turned toward us, the knee
# guard hanging from the belly) and moved forward, the legs take turns, the whole figure rises a little; no part turned,
# sheared or stretched (rig_braum.walk_frame, fix_nautilus_strips2.walk_frame).
WALK_BAND = 66                           # the design's row under the belly: the legs start below it
WALK_NEAR = ((67, 96, 36, 51), (96, 104, 29, 51))   # the near leg: design rows, columns (ends exclusive) - its foot wider
WALK_FAR = ((67, 96, 51, 65), (96, 104, 51, 72))    # the far leg, left of the front fist down to its foot
# per frame: the near leg's (columns forward, rows lifted), the far leg's, the figure's rise (canvas squares:
# league_nautilus's 1x steps x PPU)
WALK = [((0, 0), (0, 4), 2), ((0, 0), (2, 6), 4), ((0, 0), (2, 2), 2), ((0, 0), (2, 0), 0),
        ((0, 4), (0, 0), 2), ((2, 6), (0, 0), 4), ((2, 2), (0, 0), 2), ((2, 0), (0, 0), 0)]
WALK_MS = 115
CRACK = 3                                # bare squares a step opens, this many columns wide at most: a crack


def walk_frame(idle, near_step, far_step, rise):
    """The idle canvas with the legs stepping: each leg's squares moved (dx, -lift) after losing their top `lift` rows;
    the far leg first, the near one over it, the body over both; the whole frame `rise` rows up."""
    x0, y0 = DESIGN_AT
    H, W = idle.shape[:2]
    op = idle[..., 3] > 0

    def part(boxes):
        m = np.zeros((H, W), bool)
        for r0, r1, c0, c1 in boxes:
            m[y0 + r0:y0 + r1, x0 + c0:x0 + c1] = True
        return m & op

    near, far = part(WALK_NEAR), part(WALK_FAR)
    band = y0 + WALK_BAND
    body = idle.copy()
    body[near | far] = 0
    out = np.zeros_like(idle)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        leg = np.where(m[..., None], idle, 0).astype(np.uint8)
        leg[:band + 1 + lift] = 0
        ys, xs = np.nonzero(leg[..., 3] > 0)
        ok = (ys - lift >= 0) & (xs + dx < W)
        out[ys[ok] - lift, xs[ok] + dx] = leg[ys[ok], xs[ok]]
    m = body[..., 3] > 0
    out[m] = body[m]
    # the cracks a step opens take the outline, in every row a run of at most CRACK columns however tall: squares the
    # idle covered that the moved legs left bare (the slit behind a leg stepped forward) and new enclosed gaps (the
    # ground between the legs closed in by a step) - not the ground under a lifted foot (the rows its foot left), and not
    # what the idle itself shows through (the window between the tail's tip and the fist, the one under the hips)
    ground = np.zeros_like(op)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        if lift:
            ys, xs = np.nonzero(m)
            ground[ys.max() - lift + 1:ys.max() + 1, xs.min():xs.max() + dx + 1] = True
    own = ndimage.binary_fill_holes(op) & ~op
    for _ in range(3):                                     # a filled slit can close off another gap: again
        wop = out[..., 3] > 0
        crack = (op & ~wop & ~ground) | (ndimage.binary_fill_holes(wop) & ~wop & ~own)
        fill = np.zeros_like(crack)
        for a in (crack, crack.T):                         # thin across the rows or down the columns
            f = fill if a is crack else fill.T
            for y in np.nonzero(a.any(1))[0]:
                xs = np.nonzero(a[y])[0]
                for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
                    if len(run) <= CRACK:
                        f[y, run] = True
        if not fill.any():
            break
        out[fill] = (*OUTLINE, 255)
    return np.roll(out, -rise, axis=0)


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
    out = {"idle": [(pinholes(close_all(specks(breathe(idle, mask, k))), 2), ms(10)) for k in BREATH],
           "run": [(pinholes(close_all(specks(walk_frame(idle, n_, f_, r_))), 2), WALK_MS) for n_, f_, r_ in WALK]}
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
        for k, (can, t) in enumerate(frames):
            one = down(can)
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
