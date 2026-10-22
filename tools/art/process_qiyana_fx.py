#!/usr/bin/env python3
"""Qiyana's effects drawn by Gemini (the user, 2026-10-22: 「奇亚娜的特效在这里面 差两张 你可以帮忙做一下」 - 20 of the FX pack's
22 pictures came back as JPGs in Downloads, made in the pack's order, two batches) brought to the delivery
import_qiyana_fx.py reads: assets/source/qiyana/codex_fx/qiyana_fx/pixel_1x/qiyana_fx_<name>.png (one row of equal
game-size frames, alpha 0/255) + manifest.json - process_shyvana_fx.py's way (its keying, cutting, voting and symmetry,
called with Qiyana's tables). The two missing ones, the last of the pack (q_slow, River Q's cold puddle under the
slowed enemy, and q_haste, Grass Q's wind at her feet), are drawn here square by square on the pack's own ramps
(draw_q_slow, draw_q_haste), symmetric left to right like the rest.

    python tools/art/process_qiyana_fx.py [--src C:/t/qy_work/gemini] [--review DIR]

The JPGs (kept locally in --src as g00.jpg .. g19.jpg in the order they were made; not committed) have no alpha and
backgrounds of black, a painted chequerboard (w_on's top), grey (q_r) or white (r_swing); every cell is keyed by
flooding in from its own border. Gemini's layout: el_g and el_w two rows of two, el_r three rows of two (six frames,
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
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
}
ROWS = {"el_r": [340, 760, 1150, 1536]}
WHITE = {"r_swing"}            # a pure white ground: also inside the ring, where the flood from the border cannot reach
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
}
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
    """process_shyvana_fx's cells; on a white ground every pure white pixel keyed wherever it is."""
    cells = _cells_of(img, name, n)
    if name in WHITE:
        for c in cells:
            f = c[..., :3].astype(int)
            c[(f.max(-1) - f.min(-1) < 16) & (f.mean(-1) > 228), 3] = 0
    return cells


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


def hexes(s):
    return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in s.split(", ")]


RIVER = hexes("#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A")
GRASS = hexes("#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C")


def put(c, x, y, col):
    """A square and its mirror across the cell's middle column."""
    h, w = c.shape[:2]
    for xx in (x, w - 1 - x):
        if 0 <= xx < w and 0 <= y < h:
            c[y, xx, :3] = col
            c[y, xx, 3] = 255


def ellipse_rim(w, h, cx, cy):
    """The squares of a flat ellipse's rim (w x h squares, middle (cx, cy)), with whether each is on its front half."""
    pts = set()
    for t in np.linspace(0, 2 * np.pi, 240, endpoint=False):
        x = int(round(cx + (w - 1) / 2 * np.cos(t)))
        y = int(round(cy + (h - 1) / 2 * np.sin(t)))
        pts.add((x, y))
    return [(x, y, y >= cy) for x, y in sorted(pts)]


def draw_q_slow():
    """River Q's slow under the enemy, 18 x 8, four frames looping: a flat puddle 18 x 3 on the bottom rows (its rim lit,
    its middle deep blue, two white glints), a few white frost wisps rising from it in turn (two each frame, mirrored)."""
    W, H = 18, 8
    frames = []
    for f in range(4):
        c = np.zeros((H, W, 4), np.uint8)
        cx, cy = (W - 1) / 2, H - 1.8
        for y in range(H):
            for x in range(W // 2):
                dx, dy = (x - cx) / 8.2, (y - cy) / 1.25
                d = dx * dx + dy * dy
                if d <= 1.0:
                    col = RIVER[4] if d < 0.35 else RIVER[3] if d < 0.75 else RIVER[2]
                    if y == H - 1 and d > 0.5:
                        col = RIVER[4]
                    put(c, x, y, col)
        put(c, 5 + (f % 2), H - 2, RIVER[1])                       # glints moving on the water
        put(c, 2 + (f % 2), H - 2, RIVER[0] if f % 2 else RIVER[1])
        # frost wisps: each rises three rows over two frames, then starts again
        for k, (x0, ph) in enumerate(((4, 0), (7, 2))):
            t = (f + ph) % 4
            if t < 3:
                y = H - 5 - t
                put(c, x0 + (t == 2), y, RIVER[0] if t < 2 else RIVER[1])
                if t == 0:
                    put(c, x0, y + 1, RIVER[1])
        frames.append(c)
    return frames


def draw_q_haste():
    """Grass Q's haste at her feet, 30 x 10, four frames looping: the rim of a thin green wind ellipse 26 x 6 on the
    bottom rows (the front half lit, the back half dark), three small grass blades whirling along it in mirror pairs,
    a step round each frame."""
    W, H = 30, 10
    rim = ellipse_rim(26, 6, (W - 1) / 2, H - 3.5)
    frames = []
    for f in range(4):
        c = np.zeros((H, W, 4), np.uint8)
        for x, y, front in rim:
            if x <= (W - 1) / 2 and (x + y + f) % 3:                    # a broken, flickering line: wind, not a ring
                put(c, x, y, GRASS[2] if front else GRASS[3])
        for k in range(3):
            t = (f / 4 + k / 3) * 2 * np.pi
            x = int(round((W - 1) / 2 - 12.5 * abs(np.cos(t))))
            y = int(round(H - 3.5 + 2.5 * np.sin(t)))
            front = np.sin(t) > 0
            # a blade: two squares slanting, its tip lit
            put(c, x, y, GRASS[1] if front else GRASS[2])
            put(c, x + 1, y - 1, GRASS[0] if front else GRASS[1])
            if front:
                put(c, x + 2, y - 2, GRASS[1])
        frames.append(c)
    return frames


DRAWN = {"q_slow": draw_q_slow, "q_haste": draw_q_haste}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/qy_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    setup()
    os.makedirs(S.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    work = [(fn, name, n, size) for fn, (name, n, size) in SOURCES.items()] + [(None, name, 4, None) for name in DRAWN]
    for fn, name, n, size in work:
        if fn is None:
            cells = DRAWN[name]()
            src = "drawn by tools/art/process_qiyana_fx.py (Gemini left it out)"
        else:
            img = Image.open(S.lp(os.path.join(a.src, fn)))
            cells = w_on(img) if name == "w_on" else S.effect(name, n, size, img)
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
        json.dump({"effects": entries, "made_by": "Gemini (the user's images; q_slow and q_haste drawn here), processed "
                   "by tools/art/process_qiyana_fx.py"}, f, ensure_ascii=False, indent=1)
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
