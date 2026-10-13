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
Then every frame is brought down for the 1x sheet (each 1x pixel the commonest colour of its PPU x PPU squares, frames
centred on the pivot: FEET 1x rows above the soles) and its dense frame written to assets/source/ppu/galio_<tag>.png +
.json (ppu_hd.py's drawn strips). Then python tools/art/ppu_hd.py --hero galio adds the hd_ / lo_ tags.
PPU 2.0 (the user's pick: 76 squares crown to soles = 38 game rows, 52 with the wings).
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "galio")
CODEX = os.path.join(SRC, "codex_strips")
DESIGN = os.path.join(SRC, "hd", "front.png")
OLD_DESIGN = "b5ba65c5"                  # the 45-colour design Codex drew from (before the flat look)
STEM = os.path.join(ROOT, "league", "champions", "league_galio")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
PPU = 2.0
COLS, ROWS = 219, 146
PIV_X, SOLE = 92, 140                   # pack_galio_strips.py
DESIGN_AT = (42, 37)                    # the cropped design's top-left on that canvas (pack_galio_strips.py's print)
FEET = 11                               # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
OUTLINE = DG.SHADES["O"]
PINHOLE = 6
SPECK = 8
BREATH = [0, 1, 2, 2, 1, 0]
WAIST = 66                              # the design's row under the belly: the upper body above it breathes
LEGS = (34, 68)                         # the design's columns of the legs below the waist (the arms hang outside them)
TAIL_ROW = 86                           # the design's tail: below this row left of TAIL_COL (it does not breathe)
TAIL_COL = 30
# shown at 85 % (hd.rs SIZES; the user: 「这做的也太大了吧 缩小点模型」, picked from a true-scale sheet): the DLL scales about
# the frame's centre, so the dense frames are drawn SHIFT rows lower and the soles stay on the ground (rig_braum's way)
SIZE = 0.85
SHIFT = round((FEET + 0.5) * PPU * (1 / SIZE - 1))
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
    """The dense canvas -> (the 1x frame centred on the pivot, the dense frame of round(PPU x its size))."""
    px, py = PIV_X + 0.5, SOLE + 1 - FEET * PPU
    ys, xs = np.nonzero(can[..., 3])
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() * 2 < len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    W, H = round(w1 * PPU), round(h1 * PPU)
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    pad = max(0, -hx0, -hy0, hx0 + W - can.shape[1], hy0 + H - can.shape[0])
    big = np.pad(can, ((pad, pad), (pad, pad), (0, 0)))
    hd = big[hy0 + pad:hy0 + pad + H, hx0 + pad:hx0 + pad + W].copy()
    return one, hd


def lower(hd):
    """The dense frame moved SHIFT rows down (grown SHIFT rows at both ends first when its soles have no room)."""
    if not SHIFT:
        return hd
    rows = np.nonzero(hd[..., 3].any(1))[0]
    if hd.shape[0] - 1 - rows.max() < SHIFT:
        hd = np.pad(hd, ((SHIFT, SHIFT), (0, 0), (0, 0)))
    out = np.zeros_like(hd)
    out[SHIFT:] = hd[:-SHIFT]
    return out


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
        for can, t in frames:
            one, hd = down(can)
            hd = lower(hd)
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
