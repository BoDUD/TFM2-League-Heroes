#!/usr/bin/env python3
"""K'Sante's effects drawn by Gemini (the user, 2026-10-22: 「奎桑提的特效包在这里面」 - the FX pack's 19 pictures came
back as JPGs in Downloads, made in the pack's order, two batches, no copies) brought to the delivery
import_ksante_fx.py reads: assets/source/ksante/codex_fx/ksante_fx/pixel_1x/ksante_fx_<name>.png (one row of equal
game-size frames, alpha 0/255) + manifest.json - process_shyvana_fx.py's way (its keying, cutting, voting and symmetry,
called with K'Sante's tables).

    python tools/art/process_ksante_fx.py [--src C:/t/ks_work/gemini] [--review DIR]

The JPGs (kept locally in --src as g00.jpg .. g18.jpg in the order they were made; not committed) have no alpha and
backgrounds of black, a painted chequerboard (p_hit, w_trail) or white divider lines (r_hit); every cell is keyed by
flooding in from its own border. Gemini's layout: p_mark, q_slow, q3_wave and ao_aura two rows of two, r_slam two rows
of three, the rest one row; q_crack's five cells are drawn as one panorama run across the dividers (cut on the cell
lines, its first frame's flash moved to the strike point at the left), q3_burst's sand wall meets two cell lines.
Symmetric from the fuller half: left to right, top to bottom for the projectile the game turns with its flight
(q3_wave), not at all for the five forward pictures baked into his frames (a_swipe, q_crack, q3_burst, w_trail,
ao_swipe).
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
import process_shyvana_fx as S  # noqa: E402  effect(), key(), down() with this module's tables put in
V = S.V                         # design_varus (kmeans)

OUT = os.path.join(ROOT, "assets", "source", "ksante", "codex_fx", "ksante_fx")
FLYING = {"q3_wave"}
FORWARD = {"a_swipe", "q_crack", "q3_burst", "w_trail", "ao_swipe"}
# file -> (effect, frames, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "g00.jpg": ("a_hit", 3, (12, 12)), "g01.jpg": ("p_hit", 4, (16, 16)), "g02.jpg": ("p_mark", 4, (36, 8)),
    "g03.jpg": ("a_swipe", 4, (40, 32)), "g04.jpg": ("q_crack", 5, (44, 16)), "g05.jpg": ("q_hit", 3, (14, 14)),
    "g06.jpg": ("q_slow", 4, (20, 6)), "g07.jpg": ("q3_burst", 5, (36, 22)), "g08.jpg": ("q3_wave", 4, (40, 16)),
    "g09.jpg": ("q3_hit", 4, (18, 18)), "g10.jpg": ("w_brace", 6, (52, 54)), "g11.jpg": ("w_trail", 4, (32, 18)),
    "g12.jpg": ("w_land", 5, (56, 24)), "g13.jpg": ("w_hit", 4, (18, 20)), "g14.jpg": ("r_hit", 4, (22, 22)),
    "g15.jpg": ("r_slam", 6, (64, 44)), "g16.jpg": ("ao_on", 6, (60, 58)), "g17.jpg": ("ao_aura", 4, (58, 14)),
    "g18.jpg": ("ao_swipe", 4, (70, 30)),
}
# (rows, columns) of the picture's grid where it is not one row of `frames` cells; the cells read row by row
LAYOUT = {"p_mark": (2, 2), "q_slow": (2, 2), "q3_wave": (2, 2), "r_slam": (2, 3), "ao_aura": (2, 2)}
KEY = {"ao_on": 70}                     # its flash sits in a dark glow fading to the black ground (Shyvana's tf_human)
THIN = {"w_brace": 0.25, "q_slow": 0.35, "p_mark": 0.35, "ao_aura": 0.35, "q3_hit": 0.35, "ao_on": 0.35,
        "w_land": 0.35, "r_slam": 0.35, "q_crack": 0.4, "a_swipe": 0.4, "ao_swipe": 0.4}
CHEQUER = {"p_hit", "w_trail"}           # a painted chequerboard behind them: its two greys keyed wherever they are
CREEP = {"r_slam"}                       # the lower row's cells start with a sliver of the drawing above them
_cells_of = S.cells_of


def setup():
    """process_shyvana_fx's functions read their module's tables: put K'Sante's in (and its cells_of, which knows the
    effect's name)."""
    S.FLYING, S.FORWARD, S.LAYOUT, S.KEY, S.THIN = FLYING, FORWARD, LAYOUT, KEY, THIN
    S.cells_of = cells_of


def cells_of(img, name, n):
    """process_shyvana_fx's cells, then: a chequerboard's greys keyed wherever they are (flooding from the border stops
    at the drawing, the squares between its puffs stay); for a grid's lower rows, the pieces touching the cell's top
    edge dropped (the row above reaches over the cut)."""
    cells = _cells_of(img, name, n)
    if name in CHEQUER:
        for c in cells:
            f = c[..., :3].astype(int)
            grey = (f.max(-1) - f.min(-1) < 18) & (f.mean(-1) > 70) & (f.mean(-1) < 215)
            c[grey, 3] = 0
    if name in CREEP:
        cols = LAYOUT[name][1]
        for c in cells[cols:]:
            lbl, k = ndimage.label(c[..., 3] > 0)
            band = int(0.08 * c.shape[0])
            for i in range(1, k + 1):
                m = lbl == i
                if m[:band].any() and not m[band:].any() or m[0].any():
                    c[m, 3] = 0
    return cells


def peel_dark(c, level=75):
    """ao_on: the flash's dark glow, fading to the black ground, keys only partly: dark squares on the drawing's outside
    are peeled off layer by layer until a lit one is reached (a dark ring round a flash reads as dirt)."""
    c = c.copy()
    while True:
        op = c[..., 3] > 0
        dark = op & (c[..., :3].astype(int).mean(-1) < level)
        edge = dark & ndimage.binary_dilation(~op)
        if not edge.any():
            return c
        c[edge] = 0


def fill_dark_in(c, level=70):
    """w_land's third frame: two dark rock chips sit inside the sand mound like a pair of eyes (the mound read as a face).
    Dark squares with most of their neighbours drawn take their neighbours' commonest colour."""
    c = c.copy()
    f = c[..., :3].astype(int)
    op = c[..., 3] > 0
    H, W = op.shape
    for y, x in zip(*np.nonzero(op & (f.mean(-1) < level))):
        nb = [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and 0 <= y + dy < H and 0 <= x + dx < W]
        lit = [tuple(f[p]) for p in nb if op[p] and f[p].mean() >= level]
        if len(lit) >= 5:
            c[y, x, :3] = max(set(lit), key=lit.count)
    return c


def panorama(img, size, frames):
    """q_crack: Gemini drew the five cells as one long panorama run across the dividers - the strike's flash, the crack
    with its dust, the teal splashes, the dust, the crack fading - so each cell's own cut held a sliver. The whole
    picture is read as one ground crack at the game's size (keyed as one cell, voted to its own colours), and the frames
    are a window running along it from the strike: each frame the stretch it has reached, the stretch before it trailing
    behind, the crack's start fading - the wave travelling forward along the ground."""
    rgb = np.asarray(img.convert("RGB"))
    a4 = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    a4[..., :3] = rgb
    a4[..., 3] = np.where(S.key(rgb, S.KEY_D), 255, 0)
    yy, xx = np.nonzero(a4[..., 3])
    y0, y1, x0, x1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
    W, H = size
    k = min(W / (x1 - x0), H / (y1 - y0))
    px = a4[y0:y1, x0:x1][a4[y0:y1, x0:x1, 3] > 0]
    rng = np.random.default_rng(0)
    sample = px[rng.choice(len(px), min(len(px), 60000), replace=False)]
    _, pal = V.kmeans(sample.reshape(1, -1, 4), S.K)
    whole = S.down(a4, (y0, y1, x0, x1), k, np.asarray(pal, int)[:, :3], THIN.get("q_crack", 0.5))
    whole[..., 3] = np.where(whole[..., 3] >= 128, 255, 0)
    hh, ww = whole.shape[:2]
    out = []
    seg = ww / frames
    for f in range(frames):
        c = np.zeros((H, W, 4), np.uint8)
        lo, hi = max(0, int(round((f - 0.6) * seg))), min(ww, int(round((f + 1) * seg)))
        c[H - hh:, lo:hi] = whole[:, lo:hi]
        out.append(c)
    return out


def ragged(c, seed, side, slope=0.45):
    """q3_burst: Gemini's sand wall and wave met the cell lines in straight vertical edges. Each row loses its outermost
    squares on that side (`left` / `right`) - on the left more the higher it is (the sand piles up toward the wave), on
    the right the crest rounded off over its top rows - and a random 0-2 more, so the edge is as ragged as the sand's
    own; a straight cut read as a ruled line."""
    a = c[..., 3] > 0
    if not a.any():
        return c
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(a)
    top, bottom = ys.min(), ys.max()
    c = c.copy()
    for y in range(c.shape[0]):
        row = np.nonzero(a[y])[0]
        if not len(row):
            continue
        if side == "left":
            n = int(round((bottom - y) * slope)) + int(rng.integers(0, 3))
            c[y, row[:n]] = 0
        else:
            n = max(0, 3 - (y - top)) + int(rng.integers(0, 3))
            if n:
                c[y, row[-n:]] = 0
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/ks_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    setup()
    os.makedirs(S.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, size) in SOURCES.items():
        img = Image.open(S.lp(os.path.join(a.src, fn)))
        if name == "q_crack":
            cells = panorama(img, size, n)
        else:
            cells = S.effect(name, n, size, img)
        if name == "q3_burst":
            cells = ([cells[0]] + [ragged(ragged(c, k, "left"), k + 10, "right") for k, c in enumerate(cells[1:4])] +
                     [ragged(c, 20, "left", slope=0.2) for c in cells[4:]])
        if name == "ao_on":
            cells = [peel_dark(cells[0])] + cells[1:]
        if name == "w_land":
            cells = cells[:2] + [fill_dark_in(cells[2])] + cells[3:]
        if name in CREEP:                    # the row above's last specks: lone squares on the lower row's top rows
            for c in cells[LAYOUT[name][1]:]:
                op = c[..., 3] > 0
                alone = op & (ndimage.convolve(op.astype(int), np.ones((3, 3), int), mode="constant") == 1)
                alone[4:] = False
                c[alone] = 0
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(S.lp(os.path.join(OUT, "pixel_1x", f"ksante_fx_{name}.png")))
        entries.append({"name": name, "file": f"ksante_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "none (points right)" if name in FORWARD
                        else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(S.lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_ksante_fx.py"},
                  f, ensure_ascii=False, indent=1)
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
        path = os.path.join(a.review, "ksante_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
