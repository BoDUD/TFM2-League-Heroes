#!/usr/bin/env python3
"""Nunu & Willump's effects drawn by Gemini (the user, 2026-10-23: 「努努的特效在这里面 你可以优先处理」 - the FX pack's 20
pictures came back as 7 JPGs in Downloads) brought to the delivery import_nunu_fx.py reads:
assets/source/nunu/codex_fx/nunu_fx/pixel_1x/nunu_fx_<name>.png (one row of equal game-size frames, alpha 0/255) +
manifest.json - process_illaoi_fx.py's way (process_shyvana_fx's keying, voting and symmetry with these tables).

    python tools/art/process_nunu_fx.py [--src C:/t/nu_work/gemini] [--review DIR]

Which JPGs are theirs (copied to --src, not committed): g00.jpg = Gemini_Generated_Image_tvh6dt* (11:53), an ATLAS of 14
effects on a navy ground, each labelled with its file name (a_hit p_hit q_hit w_dust w_hit e_ball e_hit e_slow e_mark
e_root_hit e_root r_hit r_slow r_shield); g01..g06 = Gemini_Generated_Image_ijwlwx* (12:01-12:02, the plain one first,
then (1) .. (5)) = p_on, p_buff, w_burst, w_big, r_storm, r_burst, one row each.
The atlas is cut by ATLAS: each frame's box found by the drawings' blobs (a 25-px dilation; the labels' blobs left out),
every box of an effect the same size, centred on its blob across and set on the effects' common bottom (ground pictures)
or centred up and down. Gemini drew fewer frames than asked for w_dust (4 of 6), w_hit and r_hit (3 of 4), e_slow (1 of
4, a still ring) and e_root (4 in two pairs, split at their middles): kept as drawn.
w_burst (g03) came on a painted snowy ground and a sand band that cannot be keyed off its own snow: it is made from
w_big's frames (g04) brought to w_burst's smaller size instead (W_BURST_FROM), until a clean picture comes back.
Ground rings drawn rounder than asked (p_on, p_buff, e_slow, r_storm, r_burst with its tall spikes) are squashed up and down to the pack's
proportions before the vote (SQUASH: the union of the frames brought to the pack's width : height).
Symmetric from the fuller half: left to right, top to bottom for the projectile the game turns with its flight (e_ball).
q_hit: Gemini drew Willump's head side-on, and the mirror made a blob of it: the bite's jaws are drawn here (bite())
and only Gemini's last frame, the burst of snow and ice chips, is kept.
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
import process_shyvana_fx as S  # noqa: E402  effect(), down() with this module's tables put in
import process_hwei_fx as HW  # noqa: E402  key() from grey border colours

OUT = os.path.join(ROOT, "assets", "source", "nunu", "codex_fx", "nunu_fx")
FLYING = {"e_ball"}
FORWARD = set()
SIZE = {"a_hit": (12, 12), "p_hit": (10, 10), "q_hit": (16, 16), "p_on": (40, 12), "p_buff": (20, 8),
        "w_dust": (28, 12), "w_hit": (18, 18), "w_burst": (40, 26), "w_big": (56, 34), "e_ball": (12, 8),
        "e_hit": (10, 10), "e_slow": (16, 8), "e_mark": (10, 10), "e_root_hit": (22, 30), "e_root": (20, 14),
        "r_storm": (110, 44), "r_burst": (110, 50), "r_hit": (16, 20), "r_slow": (18, 36), "r_shield": (44, 50)}
# the atlas g00.jpg: effect -> the frames' blob boxes (y0, y1, x0, x1), read by a 25-px dilation of the drawings
ATLAS = {
    "a_hit": [(83, 320, 29, 296), (83, 326, 332, 609), (83, 320, 664, 931)],
    "p_hit": [(208, 314, 1002, 1240), (161, 315, 1270, 1478), (173, 313, 1514, 1712)],
    "q_hit": [(427, 650, 44, 297), (427, 657, 323, 608), (427, 657, 621, 894), (420, 657, 920, 1164)],
    "w_dust": [(789, 929, 39, 275), (764, 929, 286, 569), (776, 929, 585, 908), (789, 929, 927, 1164)],
    "w_hit": [(789, 919, 1245, 1379), (772, 929, 1419, 1572), (764, 932, 1595, 1754)],
    "e_ball": [(1062, 1148, 38, 281), (1062, 1148, 318, 561), (1200, 1287, 38, 282), (1200, 1287, 318, 562)],
    "e_hit": [(1206, 1283, 641, 731), (1173, 1287, 760, 897), (1179, 1287, 920, 1049)],
    "e_slow": [(1127, 1299, 1100, 1399)],
    "e_mark": [(1047, 1173, 1463, 1588), (1045, 1173, 1624, 1750), (1178, 1306, 1463, 1589), (1178, 1307, 1624, 1750)],
    "e_root_hit": [(1449, 1661, 14, 287), (1408, 1661, 308, 571), (1428, 1661, 586, 786), (1424, 1661, 800, 997)],
    "e_root": [(1492, 1661, 1030, 1213), (1492, 1661, 1213, 1397), (1492, 1661, 1400, 1583), (1492, 1661, 1583, 1766)],
    "r_hit": [(1779, 2022, 21, 287), (1762, 2022, 319, 577), (1788, 2022, 606, 896)],
    "r_slow": [(1762, 2022, 925, 1190), (1762, 2022, 1216, 1481), (1762, 2022, 1507, 1771)],
    "r_shield": [(2133, 2369, 8, 294), (2133, 2368, 306, 592), (2133, 2368, 603, 890), (2133, 2368, 902, 1188),
                 (2133, 2368, 1200, 1486)],
}
GROUNDED = {"w_dust", "e_slow", "e_root_hit", "e_root", "r_hit", "r_shield"}   # set on the effect's common bottom
PAD = 8
# the strips: file -> (effect, frames)
STRIPS = {"g01.jpg": ("p_on", 4), "g02.jpg": ("p_buff", 4), "g04.jpg": ("w_big", 7), "g05.jpg": ("r_storm", 6),
          "g06.jpg": ("r_burst", 7)}
# a strip's frames are not evenly spaced: the cuts (x) between them, midway in the gaps of the drawings' columns
# (r_burst's frames 5 and 6 touch: cut at the thinnest column, x 4560)
STRIP_CUTS = {"w_big": [0, 866, 1741, 2578, 3426, 4196, 5037, 5856], "r_storm": [0, 976, 1953, 2927, 3900, 4880, 5856],
              "r_burst": [0, 1108, 2039, 2890, 3719, 4560, 5150, 5856]}
W_BURST_FROM = "g04.jpg"
SQUASH = {"p_on", "p_buff", "e_slow", "r_storm", "r_burst"}
CROP_TOP = {"r_burst": 0.3}       # the share of each cell's rows dropped from the top (its first flash's light column)
LAYOUT = {}
KEY = {}
THIN = {"a_hit": 0.3, "p_hit": 0.3, "q_hit": 0.35, "w_dust": 0.4, "w_hit": 0.3, "w_burst": 0.35, "w_big": 0.35,
        "e_hit": 0.3, "e_mark": 0.3, "e_root_hit": 0.35, "e_root": 0.4, "p_on": 0.3, "p_buff": 0.3, "r_storm": 0.35,
        "r_burst": 0.35, "r_hit": 0.35, "r_slow": 0.3, "r_shield": 0.25, "e_slow": 0.35}


def setup():
    """process_shyvana_fx's functions read their module's tables: put Nunu's in (and process_hwei_fx's grey key, and
    this module's cells)."""
    S.FLYING, S.FORWARD, S.LAYOUT, S.KEY, S.THIN = FLYING, FORWARD, LAYOUT, KEY, THIN
    S.key = HW.key
    S.cells_of = cells_of


def atlas_boxes(name, H, W):
    """The effect's frames in the atlas as boxes of one size: centred on each blob across, on the common bottom
    (GROUNDED) or centred up and down."""
    bs = ATLAS[name]
    h = max(b[1] - b[0] for b in bs) + 2 * PAD
    w = max(b[3] - b[2] for b in bs) + 2 * PAD
    bottom = max(b[1] for b in bs) + PAD
    out = []
    for y0, y1, x0, x1 in bs:
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        top = bottom - h if name in GROUNDED and len({b[1] for b in bs}) == 1 else cy - h // 2
        if name in GROUNDED and len({b[1] for b in bs}) > 1:   # two rows of frames (none grounded so far)
            top = y1 + PAD - h
        out.append((max(0, top), min(H, top + h), max(0, cx - w // 2), min(W, cx - w // 2 + w)))
    return out


def squash(cells, name):
    """The frames' union brought to the pack's width : height by shrinking the rows (rounder rings than asked)."""
    ys, xs = [], []
    for c in cells:
        yy, xx = np.nonzero(c[..., 3])
        if len(yy):
            ys += [yy.min(), yy.max()]
            xs += [xx.min(), xx.max()]
    bh, bw = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
    cw, ch = SIZE[name]
    f = (ch / cw) / (bh / bw)
    if f >= 1:
        return cells
    return [np.asarray(Image.fromarray(c).resize((c.shape[1], max(1, round(c.shape[0] * f))), Image.NEAREST))
            for c in cells]


def cells_of(img, name, n):
    rgb = np.asarray(img.convert("RGB"))
    H, W = rgb.shape[:2]
    if name in ATLAS:
        boxes = atlas_boxes(name, H, W)
    elif name in STRIP_CUTS:
        xs = STRIP_CUTS[name]
        boxes = [(0, H, xs[k], xs[k + 1]) for k in range(len(xs) - 1)]
    else:
        boxes = S.boxes(name, n, H, W)
    out = []
    for y0, y1, x0, x1 in boxes:
        sub = rgb[y0:y1, x0:x1]
        fg = S.key(sub, KEY.get(name, S.KEY_D))
        fg = ndimage.binary_opening(fg, np.ones((2, 2), bool))
        a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
        a4[..., :3] = sub
        a4[..., 3] = np.where(fg, 255, 0)
        out.append(a4)
    if name in CROP_TOP:
        out = [c[round(c.shape[0] * CROP_TOP[name]):] for c in out]
    h0 = max(c.shape[0] for c in out)
    w0 = max(c.shape[1] for c in out)
    out = [np.pad(c, ((0, h0 - c.shape[0]), (0, w0 - c.shape[1]), (0, 0))) for c in out]
    if name in SQUASH:
        out = squash(out, name)
    return out[:n]


def bite(burst):
    """Consume's bite drawn on the 16 x 16 cell (Gemini drew a yeti's head side-on, which the mirror turned into a blob):
    an upper row of white fangs pointing down and a lower one pointing up, open, then snapped shut with a flash, then
    Gemini's own last frame (the burst of snow and ice chips) and a fainter copy of it."""
    W = H = 16
    white, shade, ice = (255, 255, 255, 255), (200, 228, 248, 255), (150, 200, 240, 255)

    def jaws(gap):
        c = np.zeros((H, W, 4), np.uint8)
        top, bot = H // 2 - 1 - gap // 2, H // 2 + gap // 2      # the rows the fangs' points reach
        for x in (1, 5, 9, 13):                                    # four fangs a row, a gap between: 3 wide at the gum,
            for d, (a0, a1, col) in enumerate(((0, 3, white), (0, 3, white), (1, 2, white), (1, 2, shade))):
                c[top - 3 + d, x + a0:x + a1] = col                # 1 at the point, 4 long
                c[bot + 3 - d, x + a0:x + a1] = col
        c[top - 4, 1:16] = ice                                     # the gums' line above / below the fangs
        c[bot + 4, 1:16] = ice
        return c
    shut = jaws(0)
    flash = shut.copy()
    flash[6:10, 5:11] = white
    fade = burst.copy()
    fade[(fade[..., 3] > 0) & (np.arange(W)[None, :] % 2 == np.arange(H)[:, None] % 2)] = 0
    import process_powder_fx as PP
    return [PP.symmetric(jaws(6)), PP.symmetric(flash), burst, PP.symmetric(fade)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/nu_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    setup()
    os.makedirs(S.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    jobs = [(name, len(bs), "g00.jpg") for name, bs in ATLAS.items()]
    jobs += [(name, n, fn) for fn, (name, n) in STRIPS.items()]
    jobs.append(("w_burst", 7, W_BURST_FROM))
    entries, sheets = [], []
    for name, n, fn in jobs:
        img = Image.open(S.lp(os.path.join(a.src, fn)))
        if fn == W_BURST_FROM and name == "w_burst":
            S.cells_of = lambda im, _name, k: cells_of(im, "w_big", k)
        cells = S.effect(name, n, SIZE[name], img)
        S.cells_of = cells_of
        if name == "q_hit":
            cells = bite(cells[-1])
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(S.lp(os.path.join(OUT, "pixel_1x", f"nunu_fx_{name}.png")))
        entries.append({"name": name, "file": f"nunu_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(S.lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_nunu_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 4
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
        path = os.path.join(a.review, "nunu_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
