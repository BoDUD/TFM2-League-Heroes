#!/usr/bin/env python3
"""Qiyana's effects drawn by Gemini (the user, 2026-10-22: 「奇亚娜的特效在这里面 差两张 你可以帮忙做一下」 - 20 of the FX pack's
22 pictures came back as JPGs in Downloads, made in the pack's order, two batches) brought to the delivery
import_qiyana_fx.py reads: assets/source/qiyana/codex_fx/qiyana_fx/pixel_1x/qiyana_fx_<name>.png (one row of equal
game-size frames, alpha 0/255) + manifest.json - process_shyvana_fx.py's way (its keying, cutting, voting and symmetry,
called with Qiyana's tables). The two it left out, the last of the pack (q_slow, River Q's cold puddle under the
slowed enemy, and q_haste, Grass Q's wind at her feet), the user had Gemini draw later (「刚才漏的最后两张特效也补了」,
g20.jpg and g21.jpg).

    python tools/art/process_qiyana_fx.py [--src C:/t/qy_work/gemini] [--review DIR]

The JPGs (kept locally in --src as g00.jpg .. g21.jpg in the order they were made; not committed) have no alpha and
backgrounds of black, a painted chequerboard (w_on's top, q_slow's dark one, q_haste's light one), grey (q_r) or
white (r_swing); every cell is keyed by flooding in from its own border, and where a chequerboard shows through a
closed shape (the haste ring's middle, the gaps between the frost wisps) its grey squares go wherever they are (GREY). Gemini's layout: el_g and el_w two rows of two, el_r three rows of two (six frames,
kept), the rest one row - not always of equal cells: w_on came as seven (the ground ring wide, six ribbons: all kept),
q_hit as four (flash, sparks, two fades), r_burst's big third frame wider than the others; those are cut on the gaps
between their drawings (CUTS, x on the JPG). Symmetric from the fuller half: left to right, top to bottom for the
shockwave the game turns with its flight (r_wave), not at all for the six forward pictures baked into her frames
(q_swing, q_w, q_r, q_g, r_swing, r_burst).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402  kmeans
import process_gnar_fx as G  # noqa: E402  centred
import process_powder_fx as PP  # noqa: E402  symmetric
import process_shyvana_fx as S  # noqa: E402  effect(), key(), down() with this module's tables put in

OUT = os.path.join(ROOT, "assets", "source", "qiyana", "codex_fx", "qiyana_fx")
FLYING = {"r_wave"}
FORWARD = {"q_swing", "q_w", "q_r", "q_g", "r_swing", "r_burst"}
# (rows, columns) of the picture's grid where it is not one row of `frames` cells; the cells read row by row
LAYOUT = {"el_g": (2, 2), "el_w": (2, 2), "el_r": (3, 2)}
# the cells' x edges on the JPG where they are not equal (cut on the gaps between the drawings); ROWS the y edges
# where a grid's rows are not (el_r's three rows sit low, under an empty band)
CUTS = {
    "w_on_ring": [0, 960], "w_on_rib": [960, 1480, 1950, 2440, 2910, 3400, 3904],
    "q_hit": [0, 1195, 2390, 3000, 3584],
    "r_burst": [0, 1150, 2500, 4400, 5856],
    "el_r": [0, 1376, 2752],
    "q_slow": [0, 783, 1555, 2325, 3104], "q_haste": [0, 895, 1792, 2689, 3584],     # cut on Gemini's grid lines
}
ROWS = {"el_r": [340, 760, 1150, 1536], "q_slow": [381, 1031], "q_haste": [324, 860]}
WHITE = {"r_swing"}            # a pure white ground: also inside the ring, where the flood from the border cannot reach
# a chequerboard seen through a closed shape: its squares (saturation under s, brightness lo..hi) keyed wherever they are
# - the frost is white and pale blue (bright), the grass ring saturated green
GREY = {"q_slow": (26, 0, 150), "q_haste": (30, 100, 256)}
# w_on: Gemini drew the enchant's two ribbons as one helix up the middle of the cell (it would cover her); the ground
# ring is read on its own, the helix as a ribbon 11 wide, and the frames put one ribbon at each side of her (the
# middle EMPTY, as the pack asked) on a cell 40 wide
W_ON = (40, 34)
RING, RIB = (30, 8), (11, 32)
# file -> (effect, frames, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "g00.jpg": ("a_hit", 3, (12, 12)), "g01.jpg": ("w_hit", 3, (10, 10)), "g02.jpg": ("p_hit", 4, (14, 14)),
    "g03.jpg": ("w_on", 7, W_ON), "g04.jpg": ("q_swing", 4, (40, 26)), "g05.jpg": ("q_w", 4, (44, 26)),
    "g06.jpg": ("q_r", 5, (44, 28)), "g07.jpg": ("q_g", 4, (44, 26)), "g08.jpg": ("q_hit", 4, (12, 12)),
    "g09.jpg": ("q_w_hit", 4, (18, 16)), "g10.jpg": ("q_r_hit", 4, (16, 16)), "g11.jpg": ("q_g_hit", 3, (14, 14)),
    "g12.jpg": ("e_hit", 3, (14, 14)), "g13.jpg": ("r_swing", 4, (36, 36)), "g14.jpg": ("r_burst", 4, (40, 20)),
    "g15.jpg": ("r_wave", 4, (32, 22)), "g16.jpg": ("r_hit", 4, (20, 20)), "g17.jpg": ("el_g", 4, (34, 12)),
    "g18.jpg": ("el_w", 4, (34, 12)), "g19.jpg": ("el_r", 6, (34, 12)),
    # Gemini's own proportions kept (the pack asked 18 x 8 and 30 x 10): the puddle 16 across with the frost rising high
    # over it, the haste ring 28 across
    "g20.jpg": ("q_slow", 4, (18, 16)), "g21.jpg": ("q_haste", 4, (28, 10)),
}
# the two later ones are line art and sparkles a square or less across: process_shyvana_fx's vote over all colours lost
# the ring's line and made the frost one grey cloud. They are brought down by kinds of pixel instead (classed): each
# square drawn where `need` of it is that kind, in the median (or the commonest) of its own pixels snapped to the kind's
# own few colours, the kinds in turn (frost over water); the frost only from its bright pixels (Gemini's dark gaps
# between the sparkles go), its specks under a square brought back as one square each
CLASSES = {
    "q_slow": [("water", 0.45, 4, "mode"), ("frost", 0.3, 3, "mode")],
    "q_haste": [("grass", 0.3, 3, "median")],     # (only its colours: the ring is haste()'s)
}
BLADE_GAP, BLADE_NEED = 1.2, 0.15
FROST = 190                    # the frost's brightness (the puddle's light rim is under it)
SPARKS = {"frost"}
KEY = {}
THIN = {"w_on_ring": 0.3, "w_on_rib": 0.3, "el_g": 0.35, "el_w": 0.3, "el_r": 0.3, "r_swing": 0.35, "q_w_hit": 0.4, "q_hit": 0.35,
        "w_hit": 0.4, "p_hit": 0.4, "r_wave": 0.4, "q_g": 0.4, "q_g_hit": 0.4, "r_burst": 0.4}
_boxes = S.boxes
_cells_of = S.cells_of


def setup():
    """process_shyvana_fx's functions read their module's tables: put Qiyana's in (and boxes that know the cuts)."""
    S.FLYING, S.FORWARD, S.LAYOUT, S.KEY, S.THIN = FLYING, FORWARD, LAYOUT, KEY, THIN
    S.boxes = boxes
    S.cells_of = cells_of


def boxes(name, n, H, W):
    if name not in CUTS:
        return _boxes(name, n, H, W)
    xs = CUTS[name]
    ys = ROWS.get(name, [0, H])
    out = []
    for y0, y1 in zip(ys, ys[1:]):
        my = int(S.OVERLAP * (y1 - y0))
        for x0, x1 in zip(xs, xs[1:]):
            mx = int(S.OVERLAP * (x1 - x0))
            out.append((y0 + my, y1 - my, x0 + mx, x1 - mx))
    return out


def cells_of(img, name, n):
    """process_shyvana_fx's cells; on a white ground every pure white pixel keyed wherever it is, on a chequerboard (GREY)
    its squares, then the specks they leave."""
    cells = _cells_of(img, name, n)
    for c in cells:
        f = c[..., :3].astype(int)
        sat, lum = f.max(-1) - f.min(-1), f.mean(-1)
        if name in WHITE:
            c[(sat < 16) & (lum > 228), 3] = 0
        if name in GREY:
            most, lo, hi = GREY[name]
            c[(sat < most) & (lum >= lo) & (lum < hi), 3] = 0
            c[~ndimage.binary_opening(c[..., 3] > 0, np.ones((3, 3), bool)), 3] = 0
    return cells


def kinds(name, px):
    """{kind: mask} of the pixels px (... x 3)."""
    f = px.astype(int)
    sat, lum = f.max(-1) - f.min(-1), f.mean(-1)
    if name == "q_slow":
        frost = (lum > FROST) & (sat < 120)
        return {"water": (sat >= 50) & (lum <= FROST), "frost": frost}
    return {"grass": sat >= 30}


def classed_ramps(name, ps, box):
    """{kind: its few colours} (k-means over every frame's pixels of that kind)."""
    y0, y1, x0, x1 = box
    allpx = np.concatenate([p[y0:y1, x0:x1][p[y0:y1, x0:x1, 3] > 0][:, :3] for p in ps])
    ramps = {}
    rng = np.random.default_rng(0)
    for kind, m in kinds(name, allpx).items():
        sub = allpx[m][rng.choice(int(m.sum()), min(int(m.sum()), 40000), replace=False)]
        ncol = next(c for kk, _, c, _ in CLASSES[name] if kk == kind)
        _, pal = V.kmeans(np.concatenate([sub, np.full((len(sub), 1), 255)], 1).astype(np.uint8)[None], ncol)
        ramps[kind] = np.asarray(pal, int)[:, :3]
    return ramps


def classed(name, n, size, img):
    """The frames brought down kind by kind (CLASSES) onto size (w, h), standing on its bottom row, symmetric."""
    ps = [G.centred(p, 1) for p in S.cells_of(img, name, n)]
    (y0, y1, x0, x1), Wn, Hn = frames_box(ps, size)
    W, H = size
    ramps = classed_ramps(name, ps, (y0, y1, x0, x1))
    out = []
    for p in ps:
        crop = p[y0:y1, x0:x1]
        h, w = crop.shape[:2]
        cy = np.minimum((np.arange(h) * Hn) // h, Hn - 1)
        cx = np.minimum((np.arange(w) * Wn) // w, Wn - 1)
        cell = cy[:, None] * Wn + cx[None, :]
        tot = np.bincount(cell.ravel(), minlength=Hn * Wn)
        f = np.zeros((Hn * Wn, 4), np.uint8)
        masks = kinds(name, crop[..., :3])
        for kind, need, _, how in CLASSES[name]:
            m = masks[kind] & (crop[..., 3] > 0)
            ramp = ramps[kind]
            for i in np.nonzero(np.bincount(cell[m], minlength=Hn * Wn) >= need * tot)[0]:
                px = crop[m & (cell == i)][:, :3].astype(int)
                if how == "mode":
                    j = np.bincount(((px[:, None] - ramp[None]) ** 2).sum(-1).argmin(1), minlength=len(ramp)).argmax()
                else:
                    j = ((ramp - np.median(px, 0)) ** 2).sum(1).argmin()
                f[i, :3], f[i, 3] = ramp[j], 255
            if kind in SPARKS:                 # specks too small for `need`: one square each, where nothing is drawn
                lbl, _ = ndimage.label(m)
                sq = h / Hn * w / Wn
                for j, o in enumerate(ndimage.find_objects(lbl), 1):
                    mm = lbl[o] == j
                    if mm.sum() < 0.08 * sq or o[0].stop - o[0].start > 1.5 * h / Hn or o[1].stop - o[1].start > 1.5 * w / Wn:
                        continue
                    yy, xx = np.nonzero(mm)
                    i = cell[o[0].start + int(yy.mean()), o[1].start + int(xx.mean())]
                    if not f[i, 3]:
                        px = crop[o][mm][:, :3].astype(int)
                        f[i, :3], f[i, 3] = ramp[((ramp - px[px.sum(1).argmax()]) ** 2).sum(1).argmin()], 255
        c = np.zeros((H, W, 4), np.uint8)
        c[H - Hn:, (W - Wn) // 2:(W - Wn) // 2 + Wn] = f.reshape(Hn, Wn, 4)
        out.append(PP.symmetric(c))
    return out


def frames_box(ps, size):
    """The frames' union box on the JPG and the game squares it comes to (k: squares a pixel)."""
    ys, xs = [], []
    for p in ps:
        yy, xx = np.nonzero(p[..., 3])
        ys += [yy.min(), yy.max()]
        xs += [xx.min(), xx.max()]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    W, H = size
    k = min(W / (x1 - x0), H / (y1 - y0))
    return (y0, y1, x0, x1), min(W, round((x1 - x0) * k)), min(H, round((y1 - y0) * k))


def haste(img, size):
    """Grass Q's haste: Gemini's ring is a line about a square thick, every vote broke it. The ellipse is fitted on the
    JPG (the most green pixels within half a square of it) and drawn as a clean line a square thick - its back half mid
    green, its front half lit; the grass blades are the green pixels more than BLADE_GAP squares off it, each square
    drawn where BLADE_NEED of it is blade, in its pixels' median snapped to the ring's three greens."""
    ps = [G.centred(p, 1) for p in S.cells_of(img, "q_haste", 4)]
    (y0, y1, x0, x1), Wn, Hn = frames_box(ps, size)
    W, H = size
    dark, mid, light = sorted((tuple(c) for c in classed_ramps("q_haste", ps, (y0, y1, x0, x1))["grass"]), key=sum)
    ramp = np.asarray([dark, mid, light])
    sx, sy = (x1 - x0) / Wn, (y1 - y0) / Hn                  # JPG px a square
    masks = [kinds("q_haste", p[y0:y1, x0:x1, :3])["grass"] & (p[y0:y1, x0:x1, 3] > 0) for p in ps]
    hh, ww = masks[0].shape
    t = np.linspace(0, 2 * np.pi, 2000, endpoint=False)

    def dist(cy, ax, by):                                    # squares from the ellipse, on the JPG's pixels
        off = np.ones((hh, ww), bool)
        off[np.clip(((cy + by * np.sin(t)) * sy).astype(int), 0, hh - 1),
            np.clip(((Wn / 2 + ax * np.cos(t)) * sx).astype(int), 0, ww - 1)] = False
        return ndimage.distance_transform_edt(off) / sx

    ring = np.any(masks, 0)[::4, ::4]                       # (the fit on every fourth pixel: the same fit, quicker)

    def fit(cy, ax, by):
        return int((ring & (dist(cy, ax, by)[::4, ::4] < 0.5)).sum())

    best = max((fit(cy, ax, by), cy, ax, by) for cy in np.arange(3.5, 7.01, 0.5)
               for ax in np.arange(12.0, Wn / 2 + 0.01, 0.5) for by in np.arange(2.0, 4.01, 0.5))
    _, cy, ax, by = best
    best = max((fit(cy + a, ax + b, by + c), cy + a, ax + b, by + c) for a in (-0.25, 0, 0.25)
               for b in (-0.25, 0, 0.25) for c in (-0.25, 0, 0.25))
    _, cy, ax, by = best
    d = dist(cy, ax, by)
    print(f"q_haste ring: middle row {cy:.2f}, half axes {ax:.2f} x {by:.2f} squares")
    yy, xx = np.mgrid[0:hh, 0:ww]
    cell = np.minimum((yy / sy).astype(int), Hn - 1) * Wn + np.minimum((xx / sx).astype(int), Wn - 1)
    # the line: one square a column on the arcs, one a row on the sides
    line = np.zeros((Hn, Wn), bool)
    cx = Wn / 2
    for x in range(Wn):
        u = (x + 0.5 - cx) / ax
        if abs(u) <= 1:
            for sg in (-1, 1):
                line[min(Hn - 1, int(cy + sg * by * np.sqrt(1 - u * u))), x] = True
    for y in range(Hn):
        v = (y + 0.5 - cy) / by
        if abs(v) <= 1:
            for sg in (-1, 1):
                line[y, min(Wn - 1, max(0, int(cx + sg * ax * np.sqrt(1 - v * v))))] = True
    out = []
    for p, m in zip(ps, masks):
        f = np.zeros((Hn, Wn, 4), np.uint8)
        for y, x in zip(*np.nonzero(line)):
            f[y, x, :3], f[y, x, 3] = (mid if y + 0.5 < cy else light), 255
        bl = m & (d > BLADE_GAP)
        crop = p[y0:y1, x0:x1, :3].astype(int)
        for i in np.nonzero(np.bincount(cell[bl], minlength=Hn * Wn) >= BLADE_NEED * sx * sy)[0]:
            med = np.median(crop[bl & (cell == i)], 0)
            f.reshape(-1, 4)[i, :3], f.reshape(-1, 4)[i, 3] = ramp[((ramp - med) ** 2).sum(1).argmin()], 255
        c = np.zeros((H, W, 4), np.uint8)
        c[H - Hn:, (W - Wn) // 2:(W - Wn) // 2 + Wn] = f
        out.append(PP.symmetric(c))
    return out


def w_on(img):
    """The enchant: the ground ring (frame 1), then the helix as two ribbons rising at her sides (frames 2-7)."""
    ring = S.effect("w_on_ring", 1, RING, img)[0]
    S.FORWARD = FORWARD | {"w_on_rib"}           # one ribbon: no symmetry of its own, kept where it was drawn
    ribs = S.effect("w_on_rib", 6, RIB, img)
    S.FORWARD = FORWARD
    W, H = W_ON
    out = []
    c = np.zeros((H, W, 4), np.uint8)
    c[H - RING[1]:, (W - RING[0]) // 2:(W - RING[0]) // 2 + RING[0]] = ring
    out.append(c)
    for r in ribs:
        c = np.zeros((H, W, 4), np.uint8)
        c[H - RIB[1]:, 0:RIB[0]] = r
        c[H - RIB[1]:, W - RIB[0]:] = r[:, ::-1]
        out.append(c)
    return out


def edge_slivers(cells, most_w=3, most=40):
    """A neighbouring cell's drawing reaching over the cut leaves a thin strip on a cell's left or right edge (q_w's first
    frame: two squares of the next frame's wave down its right side): pieces touching that edge, at most most_w squares
    wide and most squares in all, go."""
    out = []
    for c in cells:
        c = c.copy()
        lbl, n = ndimage.label(c[..., 3] > 0, structure=np.ones((3, 3)))
        for j, o in enumerate(ndimage.find_objects(lbl), 1):
            w = o[1].stop - o[1].start
            touches = o[1].start == 0 or o[1].stop == c.shape[1]
            if touches and w <= most_w and (lbl[o] == j).sum() <= most:
                c[lbl == j] = 0
        out.append(c)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/qy_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    setup()
    os.makedirs(S.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, size) in SOURCES.items():
        img = Image.open(S.lp(os.path.join(a.src, fn)))
        cells = (w_on(img) if name == "w_on" else haste(img, size) if name == "q_haste"
                 else classed(name, n, size, img) if name in CLASSES
                 else S.effect(name, n, size, img))
        if name in FORWARD:
            cells = edge_slivers(cells)
        src = f"gemini {fn}"
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(S.lp(os.path.join(OUT, "pixel_1x", f"qiyana_fx_{name}.png")))
        entries.append({"name": name, "file": f"qiyana_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "none (points right)" if name in FORWARD
                        else "left-right", "source": src})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(S.lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by "
                   "tools/art/process_qiyana_fx.py"}, f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 5
        rows = []
        for name, s, w in sheets:
            n = s.shape[1] // w
            im = Image.new("RGBA", ((s.shape[1] + 2 * n) * Z, s.shape[0] * Z), (40, 40, 52, 255))
            for k in range(n):
                cell = s[:, k * w:(k + 1) * w]
                bg = Image.new("RGBA", (w * Z, s.shape[0] * Z), (70, 74, 60, 255))
                bg.alpha_composite(Image.fromarray(cell).resize((w * Z, s.shape[0] * Z), Image.NEAREST))
                im.alpha_composite(bg, (k * (w + 2) * Z, 0))
            rows.append((name, im))
        W = max(r.width for _, r in rows) + 110
        sheet = Image.new("RGBA", (W, sum(r.height + 12 for _, r in rows)), (20, 20, 26, 255))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.alpha_composite(r, (110, y))
            d.text((4, y + 4), name, fill=(255, 255, 255, 255))
            y += r.height + 12
        path = os.path.join(a.review, "qiyana_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
