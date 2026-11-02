#!/usr/bin/env python3
"""Brock's effects and icons from the one Gemini sheet the user made (2026-11-02, 「这是gemini生成的特效和技能图标 你处理后导入
使用吧」): each frame cut from the sheet, keyed off its grey ground, brought down to the game size the pack's prompt gave
(assets/source/brock/PROMPTS_FX.md), its colours cut to its own palette, made symmetric, and written as a strip of
equal cells for import_brock_fx.py.

    python tools/art/process_brock_fx.py [--src C:/t/br_work/gemini/brock_fx.jpg] [--review out.png]

The sheet (2440 x 1728, JPEG, every effect on one flat grey #8E8E8E with its name written over its row; the original is
the user's Downloads/Gemini_Generated_Image_4twe584twe584twe.jpg, kept out of git like the other heroes' Gemini art).
CELLS below are each frame's box on it, read by eye from its keyed components (C:/t/br_work/gemini/boxes.png).
What the sheet got wrong, fixed here (fix-delivered-art-myself):
  e_root   six OPAQUE square tiles of tangled roots on dark earth: the dark earth keyed off, the tile brought to the
           ankle band and cut to a low arch, so it binds the legs and leaves the body clear;
  e_vine   every frame stands on an opaque block of soil: of it only the glowing cracks near its top are kept; the
           frames reordered so the crack opens first (sheet order 3, 2, 4, 1, 5);
  e_shield five SOLID mossy shells that would hide him: hollowed to a 4-px rim (the prompt's ring of plates);
  r_hit / r_rock  the two rows ran together: the six spike eruptions are r_hit (five kept, smallest first); the falling
           rock is put together from the sheet's boulder falling three steps, then the eruption's flare on the ground
           and the two rubble piles;
  r_slam   two frames only: the sheet's quake crown and rings (a_quake's) scaled up before, under and after them;
  q_hit    its first frame (a flash beside a whole boulder) mirrored into an eye-like slit: left out, four frames;
  a_quake  the first frame is two arcs side by side - one frame;
  q_rock   six boulders, two of them under a mistaken a_up label: the four of its own row;
  and every picture made symmetric (left to right, q_rock top to bottom) by union with its mirror: the client never
  mirrors an effect.
Writes assets/source/brock/gemini_fx/pixel_1x/brock_fx_<name>.png (one row of equal cells at game size, alpha 0 / 255),
gemini_fx/cells.json (each strip's frames and cell) and gemini_fx/icons/brock_icon_<name>.png (64 x 64, LANCZOS).
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
import design_varus as V  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "brock", "gemini_fx")
SRC = "C:/t/br_work/gemini/brock_fx.jpg"
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


# the names written over the rows (white text): only their white / grey pixels are cleared, colour under them stays
LABELS = [(25, 15, 265, 75), (1250, 15, 1490, 75), (1695, 15, 1965, 75), (25, 240, 320, 298), (1250, 240, 1495, 298),
          (25, 445, 262, 500), (25, 636, 292, 692), (1250, 516, 1515, 572), (25, 750, 290, 808), (1252, 744, 1545, 785),
          (25, 1040, 296, 1100), (25, 1236, 258, 1294), (1250, 1030, 1515, 1087), (25, 1470, 283, 1528),
          (1250, 1288, 1640, 1338), (1655, 1288, 2035, 1338), (2058, 1288, 2440, 1338)]
SOIL = 938          # e_vine: the top of the soil blocks
SOIL_KEEP = 40      # e_vine: the soil's glowing cracks kept only this far under its top (its surface)

# frame boxes (x0, y0, x1, y1) on the sheet
CELLS = {
    "a_hit": [(40, 78, 182, 220), (205, 72, 370, 224), (390, 72, 562, 222), (575, 98, 800, 222)],
    "a_quake": [(30, 298, 320, 418), (330, 284, 632, 422), (640, 286, 920, 430), (932, 298, 1196, 418)],
    "a_up": [(33, 518, 238, 596), (253, 478, 470, 596), (485, 486, 690, 594), (703, 510, 917, 594)],
    "q_slow": [(25, 645, 255, 742), (270, 655, 486, 740), (532, 646, 721, 740), (750, 638, 980, 740),
               (1000, 640, 1229, 740)],
    "q_rock": [(1706, 76, 1842, 212), (1888, 73, 2034, 210), (2060, 82, 2202, 216), (2243, 70, 2390, 206)],
    "q_hit": [(1487, 300, 1725, 498), (1738, 297, 1965, 501), (1988, 300, 2197, 497),
              (2210, 296, 2440, 501)],
    "e_root": [(1258, 581, 1452, 726), (1466, 581, 1668, 726), (1789, 581, 1984, 726), (1997, 581, 2194, 726),
               (2208, 581, 2405, 726), (1677, 581, 1778, 726)],
    "e_vine": [(495, 798, 722, 1030), (260, 798, 487, 1030), (730, 798, 957, 1030), (20, 798, 252, 1030),
               (963, 798, 1194, 1030)],
    "e_shield": [(1253, 742, 1510, 1015), (1514, 768, 1740, 1016), (1760, 779, 1953, 1016), (1960, 778, 2144, 1016),
                 (2161, 753, 2392, 1019)],
    "r_jump": [(40, 1106, 332, 1226), (364, 1084, 690, 1226), (712, 1134, 950, 1226), (985, 1096, 1192, 1226)],
    "r_hit": [(203, 1338, 356, 1458), (368, 1298, 538, 1458), (30, 1520, 180, 1696), (200, 1520, 356, 1696),
              (372, 1518, 542, 1696)],
    "r_slam": [(1253, 1077, 1806, 1266), (1834, 1066, 2430, 1268)],
}
ROCK_BALL = (753, 1385, 850, 1482)      # r_rock: the falling boulder (the third column of the mixed rows)
ROCK_FLARE = (200, 1520, 356, 1696)     # the impact: an eruption's flare
ROCK_PILES = [(710, 1574, 887, 1696), (550, 1616, 707, 1696)]
ICONS = {"skill": (1278, 1340, 1630, 1694), "skill2": (1676, 1340, 2031, 1694), "ult": (2077, 1340, 2432, 1694)}

# name -> (cell w, h at game size, where the frames sit in the cell: "c" centre / "b" bottom, symmetry, colours)
SPEC = {
    "a_hit": (18, 16, "c", "LR", 14), "a_quake": (40, 14, "c", "LR", 14), "a_up": (22, 10, "b", "LR", 12),
    "q_rock": (20, 14, "c", "TB", 12), "q_hit": (30, 22, "c", "LR", 16), "q_slow": (24, 8, "b", "LR", 10),
    "e_vine": (30, 30, "b", "LR", 16), "e_root": (24, 16, "b", "LR", 12), "e_shield": (72, 54, "b", "LR", 16),
    "r_jump": (60, 16, "b", "LR", 12), "r_slam": (110, 44, "b", "LR", 18), "r_hit": (22, 26, "b", "LR", 14),
    "r_rock": (22, 52, "b", "LR", 14),
}


def key(rgb):
    """The sheet's grey ground off: alpha 0 where the colour is that flat grey."""
    a = rgb.astype(int)
    mx, mn = a.max(2), a.min(2)
    bg = (mx - mn < 16) & (mx > 118) & (mx < 170)
    fg = ndimage.binary_opening(~bg, iterations=1)
    fg = ndimage.binary_fill_holes(fg) & ~bg | fg
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(fg, 255, 0)
    return out


def clear_labels(rgba):
    for x0, y0, x1, y1 in LABELS:
        sub = rgba[y0:y1, x0:x1]
        a = sub[..., :3].astype(int)
        grey = (a.max(2) - a.min(2) < 28) & (a.max(2) > 150)
        sub[grey, 3] = 0


def crop(sheet, box):
    x0, y0, x1, y1 = box
    return sheet[y0:y1, x0:x1].copy()


def tight(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    if not len(ys):
        return a[:1, :1] * 0
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def shrink(a, k, cover=0.5):
    """Area average by k (< 1): a square's colour the alpha-weighted mean, opaque where cover >= `cover`."""
    h, w = a.shape[:2]
    H, W = max(1, round(h * k)), max(1, round(w * k))
    out = np.zeros((H, W, 4), np.uint8)
    f = a.astype(float)
    for j in range(H):
        ya, yb = int(j * h / H), max(int(j * h / H) + 1, int((j + 1) * h / H))
        for i in range(W):
            xa, xb = int(i * w / W), max(int(i * w / W) + 1, int((i + 1) * w / W))
            win = f[ya:yb, xa:xb].reshape(-1, 4)
            al = win[:, 3] / 255
            if al.mean() >= cover:
                out[j, i, :3] = ((win[:, :3] * al[:, None]).sum(0) / al.sum()).round()
                out[j, i, 3] = 255
    return out


def put(cell, a, where, dy=0):
    """`a` into the cell, centred across; centred down ("c") or on the bottom ("b"), clipped."""
    H, W = cell.shape[:2]
    h, w = a.shape[:2]
    x = (W - w) // 2
    y = (H - h) // 2 if where == "c" else H - h
    y += dy
    for j in range(h):
        for i in range(w):
            if a[j, i, 3] and 0 <= y + j < H and 0 <= x + i < W:
                cell[y + j, x + i] = a[j, i]


def union_mirror(c, sym):
    f = c[:, ::-1] if sym == "LR" else c[::-1]
    out = c.copy()
    m = (out[..., 3] == 0) & (f[..., 3] > 0)
    out[m] = f[m]
    # the shared column/row: make it exactly symmetric (where one side differs, the original half wins)
    if sym == "LR":
        w = out.shape[1]
        out[:, w - w // 2:] = out[:, :w // 2][:, ::-1]
    else:
        h = out.shape[0]
        out[h - h // 2:] = out[:h // 2][::-1]
    return out


def frames_of(sheet, name):
    W, H, where, sym, ncol = SPEC[name]
    parts = []
    for k, box in enumerate(CELLS.get(name, [])):
        a = crop(sheet, box)
        if name == "e_vine":   # under the soil line only the glowing cracks
            s = SOIL - box[1]
            low = a[s:]
            rgb = low[..., :3].astype(int)
            glow = (rgb[..., 0] > 200) & (rgb[..., 1] > 130)
            glow[SOIL_KEEP:] = False
            low[~glow, 3] = 0
        if name == "e_root":   # the dark earth between the roots off
            rgb = a[..., :3].astype(int)
            a[rgb.max(2) < 78, 3] = 0
        parts.append(tight(a))
    return parts


def scaled(parts, W, H, fit="max"):
    """All the frames by one factor: the widest to W or the tallest to H, whichever is smaller."""
    mw = max(p.shape[1] for p in parts)
    mh = max(p.shape[0] for p in parts)
    k = min(W / mw, H / mh)
    return [shrink(p, k) for p in parts]


def build(sheet):
    out = {}
    for name in SPEC:
        W, H, where, sym, ncol = SPEC[name]
        if name == "r_rock":
            cells = rock_frames(sheet, W, H)
        elif name == "r_slam":
            cells = slam_frames(sheet, W, H)
        else:
            parts = frames_of(sheet, name)
            if name == "e_root":
                cells = [root_cell(p, W, H) for p in parts]
            else:
                cells = []
                for p in scaled(parts, W, H):
                    c = np.zeros((H, W, 4), np.uint8)
                    put(c, p, where)
                    cells.append(c)
        if name == "e_shield":
            cells = [hollow(c, 4) for c in cells]
        cells = palette(cells, ncol)
        cells = [union_mirror(c, sym) for c in cells]
        out[name] = cells
    return out


def root_cell(tile, W, H):
    """A root tile squeezed to the ankle band and cut to a low arch (the body clear above the shins)."""
    a = np.asarray(Image.fromarray(tile).resize((W, H - 2), Image.BOX)).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    c = np.zeros((H, W, 4), np.uint8)
    c[2:] = a
    yy, xx = np.mgrid[0:H, 0:W]
    cx = (W - 1) / 2
    arch = ((xx - cx) / (W / 2)) ** 2 + ((H - 1 - yy) / (H - 1)) ** 2 <= 1.0
    inner = ((xx - cx) / (W / 2 - 6)) ** 2 + ((H - 1 - yy) / (H - 7)) ** 2 <= 1.0   # the shins themselves
    c[~arch | inner & (yy < H - 5)] = 0
    return c


def hollow(c, rim):
    m = c[..., 3] > 0
    inner = ndimage.binary_erosion(m, iterations=rim)
    out = c.copy()
    out[inner] = 0
    return out


def palette(cells, n):
    strip = np.concatenate(cells, axis=1)
    if not (strip[..., 3] > 0).any():
        return cells
    idx, pal = V.kmeans(strip, n)
    q = np.zeros_like(strip)
    op = strip[..., 3] > 0
    q[op, :3] = pal[idx[op]]
    q[op, 3] = 255
    w = cells[0].shape[1]
    return [q[:, k * w:(k + 1) * w] for k in range(len(cells))]


def rock_frames(sheet, W, H):
    """The falling rock: the boulder at three heights, landing, the flare on the ground, two rubble piles. (The sheet's
    streaks above it came down to 1-px lines that read as a beetle's feelers: left out.)"""
    ball = crop(sheet, ROCK_BALL)
    lab, n = ndimage.label(ball[..., 3] > 0)
    big = 1 + int(np.argmax(ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))))
    ball[lab != big, 3] = 0                                  # the boulder alone (the pebbles round it off)
    ball = tight(ball)
    fall = shrink(ball, 10 / ball.shape[1])                  # the boulder 10 px across
    m = fall[..., 3] > 0                                     # its outline's stray corner squares off
    nb = ndimage.convolve(m.astype(int), np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]), mode="constant")
    fall[m & (nb < 2)] = 0
    flare = shrink(tight(crop(sheet, ROCK_FLARE)), 18 / tight(crop(sheet, ROCK_FLARE)).shape[1])
    piles = [tight(crop(sheet, box)) for box in ROCK_PILES]
    piles = [shrink(p, 20 / p.shape[1]) for p in piles]
    cells = []
    for drop in (0, 14, 28, H - fall.shape[0]):
        c = np.zeros((H, W, 4), np.uint8)
        put(c, fall, "b", -(H - fall.shape[0] - drop))
        cells.append(c)
    for p in [flare] + piles:
        c = np.zeros((H, W, 4), np.uint8)
        put(c, p, "b")
        cells.append(c)
    return cells


def slam_frames(sheet, W, H):
    """The two slab frames, the quake crown before them and its rings under and after them (all scaled up)."""
    q = [tight(key_crop(sheet, b)) for b in CELLS["a_quake"]]
    s = [tight(key_crop(sheet, b)) for b in CELLS["r_slam"]]
    ring = lambda i, w: shrink(q[i], w / q[i].shape[1])
    slab = lambda i: shrink(s[i], W / s[i].shape[1])
    plan = [[(ring(0, 60), 0)], [(ring(1, 80), 0), (slab(0), 0)], [(ring(2, 104), 0), (slab(1), 0)],
            [(ring(3, 108), 0)], [(ring(3, 90), 0)]]
    cells = []
    for layers in plan:
        c = np.zeros((H, W, 4), np.uint8)
        for a, dy in layers:
            put(c, a, "b", dy)
        cells.append(c)
    return cells


SHEET = None


def key_crop(sheet, box):
    return crop(sheet, box)


def icon(rgb, box):
    x0, y0, x1, y1 = box
    return Image.fromarray(rgb[y0:y1, x0:x1]).resize((64, 64), Image.LANCZOS)


def review(out, path):
    Z = 6
    rows = []
    for name, cs in out.items():
        W = sum(c.shape[1] + 2 for c in cs)
        H = max(c.shape[0] for c in cs)
        img = Image.new("RGBA", (W * Z, H * Z), (104, 112, 72, 255))
        x = 0
        for c in cs:
            img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST), (x * Z, 0))
            x += c.shape[1] + 2
        rows.append(img)
    sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height + 8
    sheet.convert("RGB").save(path)
    print(path, sheet.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="also write every strip at 6x here")
    a = ap.parse_args()
    rgb = np.asarray(Image.open(lp(a.src)).convert("RGB"))
    if rgb.shape[:2] != (1728, 2440):
        sys.exit(f"{a.src}: {rgb.shape[1]}x{rgb.shape[0]}, not the 2440 x 1728 sheet")
    sheet = key(rgb)
    clear_labels(sheet)
    out = build(sheet)
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    os.makedirs(lp(os.path.join(OUT, "icons")), exist_ok=True)
    meta = {}
    for name, cs in out.items():
        Image.fromarray(np.concatenate(cs, axis=1)).save(lp(os.path.join(OUT, "pixel_1x", f"brock_fx_{name}.png")))
        meta[name] = {"frames": len(cs), "cell": [cs[0].shape[1], cs[0].shape[0]], "symmetry": SPEC[name][3]}
        print(f"{name:9s} {len(cs)} x {cs[0].shape[1]}x{cs[0].shape[0]}")
    with open(lp(os.path.join(OUT, "cells.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    for n, box in ICONS.items():
        icon(rgb, box).save(lp(os.path.join(OUT, "icons", f"brock_icon_{n}.png")))
    if a.review:
        review(out, a.review)


if __name__ == "__main__":
    main()
