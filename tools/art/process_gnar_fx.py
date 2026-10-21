#!/usr/bin/env python3
"""Gnar's effects drawn by Gemini (the user, 2026-10-20: the FX pack's 24 pictures came back as 24 JPGs in Downloads,
「纳尔的所有特效都在这里面」, made in the pack's order) brought to the delivery import_gnar_fx.py reads:
assets/source/gnar/codex_fx/gnar_fx/pixel_1x/gnar_fx_<name>.png (one row of equal game-size frames, alpha 0/255) +
manifest.json - process_chogath_fx.py's way.

    python tools/art/process_gnar_fx.py [--src C:/t/gn_work/gemini_fx_in] [--review DIR]

The JPGs (kept locally in --src as 01.jpg .. 24.jpg in the order they were made; not committed) have no alpha and
backgrounds of every kind: black, black with light lines between the frames, a painted dark or grey chequerboard,
grey panels, a white-to-grey wash, white and black halves in one frame (w_quake), a sand floor under the boulder
(q_rest). So every panel is keyed by flooding in from its own border: the border's colours (up to three, k-means) and
everything connected to the border within KEY of one of them is background; what an outline closes off (a grey rock,
a white core in a glow) stays, and a thin light line the whole height of the picture (a frame divider) goes. Then as
process_powder_fx: all frames of an effect cropped by one box (their union: a flash keeps its place), brought down by
votes to the pack's game size in the effect's own K colours, made symmetric from the fuller half - left to right, or
top to bottom for the three projectiles the game turns with their flight.
Gemini's layout quirks (SOURCES / LAYOUT / CUTS): two rows of frames (q_rock's second row is a spare: dropped; r_wave
and tf_mini read row by row, tf_mini's sixth cell empty), frames of uneven widths cut where measured (q_slow, q2_hit,
tf_mega - which came as 7 frames, 4 over 3), q_slow drawn over the heads of the units it rides (the heads
cut off: its lower quarter), hyper drawn as a 5 x 8 sheet of one-sided streaks on brown ground bars (its first row's
first four cells, each on the right of the feet and mirrored to the left).
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
import design_varus as V  # noqa: E402
import process_powder_fx as PP  # noqa: E402  down, symmetric
import process_chogath_fx as PC  # noqa: E402  symmetric_tb

OUT = os.path.join(ROOT, "assets", "source", "gnar", "codex_fx", "gnar_fx")
FLYING = {"a_boom", "q_boom", "q_rock"}          # turned with their flight: drawn flying right, symmetric top to bottom
# file -> (effect, frames, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "01.jpg": ("a_boom", 4, (10, 10)), "02.jpg": ("a_hit", 3, (12, 12)), "03.jpg": ("a_hyper", 4, (18, 18)),
    "04.jpg": ("hyper", 4, (24, 8)), "05.jpg": ("full", 4, (34, 36)), "06.jpg": ("q_boom", 4, (16, 16)),
    "07.jpg": ("q_hit", 3, (16, 16)), "08.jpg": ("q_catch", 3, (16, 16)), "09.jpg": ("q_slow", 4, (16, 8)),
    "10.jpg": ("e_hit", 3, (16, 14)), "11.jpg": ("m_hit", 4, (20, 18)), "12.jpg": ("q_rock", 4, (18, 16)),
    "13.jpg": ("q2_hit", 5, (34, 24)), "14.jpg": ("q_rest", 4, (16, 12)), "15.jpg": ("q_pick", 3, (21, 16)),
    "16.jpg": ("q2_slow", 4, (18, 6)), "17.jpg": ("c_slam", 5, (48, 26)), "18.jpg": ("c_hit", 3, (16, 14)),
    "19.jpg": ("w_quake", 5, (60, 26)), "20.jpg": ("w_hit", 5, (20, 30)), "21.jpg": ("r_wave", 6, (70, 40)),
    "22.jpg": ("r_hit", 4, (18, 18)), "23.jpg": ("tf_mega", 7, (72, 56)), "24.jpg": ("tf_mini", 5, (60, 46)),
}
# (rows, columns) of the picture's grid where it is not one row of `frames` cells; the cells read row by row
LAYOUT = {"q_rock": (2, 4), "r_wave": (2, 3), "tf_mini": (2, 3), "hyper": (5, 8)}
# frames Gemini drew at uneven widths (measured on the keyed pictures, gaps of 24+ empty columns): (row band, x0, x1)
# with the number of row bands; tf_mega came as 7 frames, 4 over 3
CUTS = {
    "q_slow": (1, [(0, 0, 960), (0, 960, 2880), (0, 2880, 4480), (0, 4480, 5856)]),
    "q2_hit": (1, [(0, 0, 760), (0, 760, 1720), (0, 1720, 3570), (0, 3570, 5050), (0, 5050, 5856)]),
    "tf_mega": (2, [(0, 0, 650), (0, 650, 1536), (0, 1536, 2297), (0, 2297, 3168),
                    (1, 0, 1080), (1, 1080, 2110), (1, 2110, 3168)]),
}
KEEP_ROWS = {"q_slow": (0.0, 0.74)}            # the part of each cell kept (fractions of its height)
KEY = {"q_rest": 46, "w_quake": 46, "c_hit": 34}   # colour distance to a border colour that floods (default KEY_D)
KEY_D = 40
THIN = {"q_slow": 0.3, "q2_slow": 0.35, "w_quake": 0.35, "r_wave": 0.35, "c_slam": 0.4}
K = 24
OVERLAP = 0.03                                  # each cell's border band ignored (Gemini's dividers sit on the cuts)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def border_colours(rgb, k=3):
    """The commonest colours round a cell's border (up to k)."""
    b = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(float)
    cols = [b.mean(0)]
    for _ in range(12):                          # tiny k-means
        if len(cols) < k:
            far = ((b[:, None, :] - np.asarray(cols)[None]) ** 2).sum(-1).min(1)
            cols.append(b[far.argmax()])
        lab = ((b[:, None, :] - np.asarray(cols)[None]) ** 2).sum(-1).argmin(1)
        cols = [b[lab == i].mean(0) if (lab == i).any() else cols[i] for i in range(len(cols))]
    lab = ((b[:, None, :] - np.asarray(cols)[None]) ** 2).sum(-1).argmin(1)
    keep = [c for i, c in enumerate(cols) if (lab == i).mean() > 0.04]
    return np.asarray(keep)


def key_cell(rgb, dist, cols=None):
    """-> foreground mask: the background flooded in from the border (colours near the border's own, or `cols`)."""
    f = rgb.astype(float)
    cols = border_colours(rgb) if cols is None else cols
    d2 = ((f[:, :, None, :] - cols[None, None]) ** 2).sum(-1)
    near = d2.min(-1) <= dist ** 2
    lbl, n = ndimage.label(near)
    edge = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    bg = np.isin(lbl, list(edge))
    sat = f.max(-1) - f.min(-1)
    lum = f.mean(-1)
    # the dark ground a ring or an ellipse closes in (the black inside the boomerang's ring, GNAR!'s shockwave): big
    # regions of a dark border colour not reaching the border; a grey rock is lighter than its grey panel, a white
    # core in a flash is not dark, so both stay
    dark_cols = [i for i, c in enumerate(cols) if c.mean() < 110]
    if dark_cols:
        near_dark = d2[..., dark_cols].min(-1) <= dist ** 2
        sizes = ndimage.sum(near, lbl, range(1, n + 1))
        darkfrac = ndimage.mean(near_dark, lbl, range(1, n + 1))
        big = [i + 1 for i in range(n) if i + 1 not in edge and sizes[i] > 0.002 * near.size and darkfrac[i] > 0.8]
        bg |= np.isin(lbl, big)
    # a chequerboard's other tone: low saturation and dark, in big blocks touching the background
    dull = (sat < 16) & (lum < 90)
    grow = ndimage.binary_dilation(bg, iterations=2)
    lbl2, _ = ndimage.label(dull & ~bg)
    touch = set(np.unique(lbl2[grow & (lbl2 > 0)])) - {0}
    bg |= np.isin(lbl2, list(touch)) & ndimage.binary_opening(dull, np.ones((5, 5), bool))
    # thin light lines the full height of the cell (frame dividers)
    light = (lum > 150) & (sat < 30)
    cols_line = light.mean(0) > 0.9
    bg[:, cols_line] = True
    fg = ~bg
    fg = ndimage.binary_opening(fg, np.ones((3, 3), bool))      # JPEG fringe specks
    return fg


def bar_bands(rgb):
    """hyper's sheet: the row bands above each brown ground bar (the bars are not evenly spaced from the top)."""
    f = rgb.astype(int)
    bar = (np.abs(f[..., 0] - 92) < 30) & (np.abs(f[..., 1] - 68) < 26) & (np.abs(f[..., 2] - 44) < 24)
    rows = bar.mean(1) > 0.5
    bands, top, y = [], 0, 0
    while y < len(rows):
        if rows[y]:
            y1 = y
            while y1 < len(rows) and rows[y1]:
                y1 += 1
            bands.append((top, y))
            top, y = y1, y1
        else:
            y += 1
    return bands


def boxes(name, n, H, W, rgb):
    """The cells' (y0, y1, x0, x1): CUTS where Gemini drew uneven frames, else the grid (minus a thin band on the cuts,
    where Gemini's divider lines sit); hyper's rows end at its ground bars."""
    if name in CUTS:
        rows, cuts = CUTS[name]
        return [(round(r * H / rows), round((r + 1) * H / rows), x0, x1) for r, x0, x1 in cuts]
    rows, cols = LAYOUT.get(name, (1, n))
    bands = bar_bands(rgb) if name == "hyper" else None
    out = []
    for r in range(rows):
        y0, y1 = round(r * H / rows), round((r + 1) * H / rows)
        if bands is not None:
            if r >= len(bands):
                continue
            y0, y1 = bands[r]
        for c in range(cols):
            x0, x1 = round(c * W / cols), round((c + 1) * W / cols)
            my, mx = int(OVERLAP * (y1 - y0)), int(OVERLAP * (x1 - x0))
            out.append((y0 + my, y1 - my, x0 + mx, x1 - mx))
    return out


def cells_of(img, name, n):
    rgb = np.asarray(img.convert("RGB"))
    H, W = rgb.shape[:2]
    out = []
    for y0, y1, x0, x1 in boxes(name, n, H, W, rgb):
        sub = rgb[y0:y1, x0:x1]
        if name in KEEP_ROWS:
            a, b = KEEP_ROWS[name]
            h = sub.shape[0]
            sub = sub[int(a * h):int(b * h)]
        fg = key_cell(sub, KEY.get(name, KEY_D))
        if name == "hyper":                  # the brown ground bar under each cell
            f = sub.astype(int)
            bar = (np.abs(f[..., 0] - 92) < 30) & (np.abs(f[..., 1] - 68) < 26) & (np.abs(f[..., 2] - 44) < 24)
            rows_bar = bar.mean(1) > 0.5
            if rows_bar.any():
                fg[np.argmax(rows_bar):] = False
        a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
        a4[..., :3] = sub
        a4[..., 3] = np.where(fg, 255, 0)
        out.append(a4)
    if name == "q_rock":
        out = out[:4]                            # the second row is a spare
    elif name == "hyper":
        out = out[:4]                            # the first row's first four
    return out[:n]


def centred(p, axis):
    """A cell moved so its drawing's box is centred across (axis 1) or up and down (axis 0): Gemini drew some frames
    off the middle, and the mirror then made two flashes of one (q2_hit, tf_mega)."""
    yy, xx = np.nonzero(p[..., 3])
    if not len(yy):
        return p
    v = xx if axis == 1 else yy
    d = int(round(p.shape[axis] / 2 - (v.min() + v.max() + 1) / 2))
    return np.roll(p, d, axis=axis) if d else p


def effect(name, n, size, img):
    ps = cells_of(img, name, n)
    h0 = max(p.shape[0] for p in ps)              # uneven cuts: each cell padded to the biggest, centred across
    w0 = max(p.shape[1] for p in ps)
    pad = []
    for p in ps:
        q = np.zeros((h0, w0, 4), np.uint8)
        ox = (w0 - p.shape[1]) // 2
        q[:p.shape[0], ox:ox + p.shape[1]] = p
        pad.append(q)
    ps = pad
    if name != "hyper":
        ps = [centred(p, 0 if name in FLYING else 1) for p in ps]
    ys, xs = [], []
    for p in ps:
        yy, xx = np.nonzero(p[..., 3])
        if len(yy):
            ys += [yy.min(), yy.max()]
            xs += [xx.min(), xx.max()]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    cw, ch = size
    if name == "hyper":                          # one side: on the right of the feet, mirrored to the left
        cw = cw // 2 - 2
    k = min(cw / (x1 - x0), ch / (y1 - y0))
    allpx = np.concatenate([p[y0:y1, x0:x1][p[y0:y1, x0:x1, 3] > 0][:, :4] for p in ps])
    rng = np.random.default_rng(0)
    sample = allpx[rng.choice(len(allpx), min(len(allpx), 60000), replace=False)]
    _, pal = V.kmeans(sample.reshape(1, -1, 4), K)
    pal_px = np.asarray(pal, int)[:, :3]
    frames = [PP.down(p, (y0, y1, x0, x1), k, k, pal_px, THIN.get(name, 0.5)) for p in ps]
    W, H = size
    cells = []
    for f in frames:
        c = np.zeros((H, W, 4), np.uint8)
        fh, fw = min(f.shape[0], H), min(f.shape[1], W)
        if name == "hyper":
            ox = W - fw                          # the right half, its streaks running out from the feet
            oy = H - fh
        else:
            ox, oy = (W - fw) // 2, (H - fh) // 2
        c[oy:oy + fh, ox:ox + fw] = f[:fh, :fw]
        c[..., 3] = np.where(c[..., 3] >= 128, 255, 0)
        c[c[..., 3] == 0] = 0
        cells.append(PC.symmetric_tb(c) if name in FLYING else PP.symmetric(c))
    while len(cells) > 1 and not cells[-1][..., 3].any():
        cells.pop()                              # a last frame too faint to survive the key (q_catch's sparkles)
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/gn_work/gemini_fx_in")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, size) in SOURCES.items():
        cells = effect(name, n, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"gnar_fx_{name}.png")))
        entries.append({"name": name, "file": f"gnar_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_gnar_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 6
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
        path = os.path.join(a.review, "gnar_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
