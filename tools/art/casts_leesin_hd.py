#!/usr/bin/env python3
"""Lee Sin's actions from Codex's whole-frame redraw (assets/source/leesin/hd/casts: tools/art/pack_leesin_actions.py's
pack, delivered 2026-10-26; the raw generations stay in Codex's outputs folder new-chat-7/outputs/leesin-actions/raw),
read onto the design's squares.

Codex drew them as finished pictures, not on the templates' 7-px grid: a white background (not transparent),
anti-aliased edges, colours off the design's palette, and each figure zoomed 1.1-1.6x past its template by its own
measure. Codex's own export for Draven scaled each figure so its visible box was as tall as its old frame's: tried here first,
it left heads 0.82-1.22 of the design's (Codex drew Lee Sin's poses looser than the templates). So the zoom is read off
his HEAD: the design's head (skull, blindfold, face; HEAD) laid on each frame with its gem on the frame's gem at scales
0.70-1.40, the best colour match giving the head's size; one zoom a SHEET (both cells are one generation - the two
frames' head zooms agree within a few per cent, the box zooms by up to 18 %), the mean of its frames whose match is
good (GOOD); where none is (E's last frame, the falls: the head tilted or upside down) the blindfold gem's blue area
instead (zoom = sqrt(area / the design's 3 squares) x the median head / gem ratio, 0.949). ZOOM holds the result
(--measure works it out again).

Each frame then: the white keyed off from the sheet's edges and the white it walls in, every piece of the drawing given
to the cell its centre of mass falls in, sampled at its sheet's zoom (each square the colour most of its pixels snap to
in the design's palette, nearest in Lab), and placed where the old frame stood: its box's bottom on the old box's
bottom, its box's middle on the old box's middle, both from the pivot (soles 11.5 old pixels under the frame's centre,
on the design's soles' row). The run is placed by his head (STEADY): the old run held the skull in one column and within 6
squares of one height while the legs cycled; the redo's frames drawn on straighter legs stood the head up to 14 squares
higher and swayed it 6 columns - so each run frame's skull goes on its old frame's column, and down to its old frame's
height as far as its lowest foot can go (to the soles' row: the airborne frames whose front foot reaches down land on it).

    python tools/art/casts_leesin_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_leesin_hd.py --measure         # the ZOOM table again (slow: a few minutes)
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
HD = os.path.join(ROOT, "assets", "source", "leesin", "hd")
SRC = os.path.join(HD, "casts")
TAGS = ["run", "attack", "skill", "q2", "skill2", "ult", "hit", "dead"]
OLD_SOLES = 11.5                # old frames: the soles this many pixels under the frame's centre (its pivot)
# px of Codex's drawing a design square, a sheet: the first delivery's as measured 2026-10-26 (the frames the user
# passed: 「其他动作通过」), the run's four sheets and E's last frame from the redo (RUN_REDO_PROMPT.md) by --measure
ZOOM = {"run_1": 9.35, "run_2": 9.27, "run_3": 8.91, "run_4": 9.24, "attack_1": 7.68, "attack_2": 8.84,
        "attack_3": 7.89, "skill_1": 8.98, "skill_2": 7.96, "skill_3": 8.18, "skill_4": 9.61, "q2_1": 9.75,
        "q2_2": 11.04, "q2_3": 10.32, "q2_4": 9.38, "q2_5": 8.69, "skill2_1": 8.84, "skill2_2": 8.08, "skill2_3": 9.51,
        "skill2_4": 5.64, "ult_1": 7.9, "ult_2": 8.7, "ult_3": 8.11, "ult_4": 8.56, "hit_1": 8.0, "dead_1": 7.21,
        "dead_2": 10.94, "dead_3": 7.27, "dead_4": 7.5}
STEADY = {"run"}                # placed by the skull: the old frame's column, its height as far as the feet allow
HEAD = (11, 31, 25, 47)         # the design's head for the match: rows 11-30 (under the braid), columns 25-46
GOOD = 100                      # a head match this good (mean colour distance) counts
WHITE = 238                     # the background: every channel this light, grey (spread <= 12), reached from the edge


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


D0 = design()
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles
PPU = 2.1                       # design squares a game pixel: 86 rows / 2.1 = his 1x 41 (design_leesin_hd)
PAL = np.unique(D0[D0[..., 3] > 0][:, :3], axis=0)
PAL_LAB = color.rgb2lab(PAL[None].astype(float) / 255.0)[0]


def sheets():
    with open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)["sheets"]


def old_frames():
    """{tag: [RGBA]} of the old 1x sheet (assets/source/leesin/hd/old: main's league_leesin before the redo)."""
    px = np.asarray(Image.open(lp(os.path.join(HD, "old", "sheet.png"))).convert("RGBA"))
    with open(lp(os.path.join(HD, "old", "anim.fanim")), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        out[tag] = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            out[tag].append(px[y:y + h, x:x + w].copy())
    return out


OLD = old_frames()


def figure(a):
    """The drawing's mask: everything but the white reached from the sheet's edges, and the white it walls in (inside
    the braid's loop, between an arm and the body) - neutral like the background and 100 px up; the bandages' whites
    are warm (#FAF6EE, #FAF2E2: blue under red) and small."""
    rgb = a[..., :3].astype(int)
    white = (rgb.min(-1) >= WHITE) & (rgb.max(-1) - rgb.min(-1) <= 12)
    lbl, n = ndimage.label(white)
    bg = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    idx = range(1, n + 1)
    size = ndimage.sum(white, lbl, idx)
    r, b = (ndimage.mean(rgb[..., c], lbl, idx) for c in (0, 2))
    lo = ndimage.mean(rgb.min(-1), lbl, idx)
    bg |= {i + 1 for i in range(n) if size[i] >= 100 and abs(r[i] - b[i]) <= 2.5 and lo[i] >= 247}
    return ~np.isin(lbl, list(bg))


def cells(s, fig):
    """[(frame, mask)]: every piece of the drawing (40 px up) given to the cell its centre of mass falls in."""
    cw = 1536 // s["cells"]
    lbl, n = ndimage.label(fig, structure=np.ones((3, 3)))
    idx = range(1, n + 1)
    sz, com = ndimage.sum(fig, lbl, idx), ndimage.center_of_mass(fig, lbl, idx)
    return [(k, np.isin(lbl, [i + 1 for i in range(n) if sz[i] >= 40 and c * cw <= com[i][1] < (c + 1) * cw]))
            for c, k in enumerate(s["frames"])]


def snap(rgb):
    """Each pixel's nearest design colour (Lab) -> palette indices."""
    lab = color.rgb2lab(rgb.reshape(-1, 1, 3).astype(float) / 255.0)[:, 0]
    d = ((lab[:, None, :] - PAL_LAB[None]) ** 2).sum(-1)
    return d.argmin(1).reshape(rgb.shape[:2])


def sample(a, m, rows, cols):
    """The box a[m] on a rows x cols grid: each square the palette colour most of its drawn pixels snap to, drawn where
    half its pixels are."""
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub, sm = a[y0:y1, x0:x1, :3], m[y0:y1, x0:x1]
    idx = snap(sub)
    out = np.zeros((rows, cols, 4), np.uint8)
    hy, hx = (y1 - y0) / rows, (x1 - x0) / cols
    for j in range(rows):
        ya, yb = int(round(j * hy)), max(int(round(j * hy)) + 1, int(round((j + 1) * hy)))
        for i in range(cols):
            xa, xb = int(round(i * hx)), max(int(round(i * hx)) + 1, int(round((i + 1) * hx)))
            mm = sm[ya:yb, xa:xb]
            if mm.sum() * 2 < mm.size:
                continue
            v = np.bincount(idx[ya:yb, xa:xb][mm], minlength=len(PAL))
            out[j, i, :3] = PAL[v.argmax()]
            out[j, i, 3] = 255
    return out


def old_box(fr):
    """The old frame's visible box from its pivot, in 1x pixels: (left, top, right, bottom); y up negative."""
    ys, xs = np.nonzero(fr[..., 3] > 0)
    h, w = fr.shape[:2]
    return xs.min() - w / 2, ys.min() - h / 2 - OLD_SOLES, xs.max() + 1 - w / 2, ys.max() + 1 - h / 2 - OLD_SOLES


def zoom_of(s, n, gh):
    """The sheet's zoom (ZOOM); while measuring (ZOOM empty) the old box's height at PPU."""
    if s["name"] in ZOOM:
        return ZOOM[s["name"]]
    T, B = old_box(OLD[s["tag"]][int(n.rsplit("_", 1)[1]) - 1])[1::2]
    return gh / round((B - T) * PPU)


def blue(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (b > 150) & (b - r > 70) & (g > 80)


def gem(a, m=None):
    """The blindfold's gem: (centre row, centre column, blue area) of the biggest blue piece."""
    bl = blue(a) & (a[..., 3] > 0 if m is None else m)
    lbl, n = ndimage.label(bl, structure=np.ones((3, 3)))
    if not n:
        return None
    sz = ndimage.sum(bl, lbl, range(1, n + 1))
    ys, xs = np.nonzero(lbl == int(np.argmax(sz)) + 1)
    return ys.mean(), xs.mean(), len(ys)


def head_fit(pic):
    """(scale, mean colour distance): the design's head scaled about its gem, the gem on the frame's (+-1 square)."""
    gy0, gx0, _ = gem(D0)
    r0, r1, c0, c1 = HEAD
    g = gem(pic)

    def dist(sc, dy, dx):
        tot, n = 0.0, 0
        for y in range(int(np.floor(g[0] + dy + (r0 - gy0) * sc)) - 1, int(np.ceil(g[0] + dy + (r1 - gy0) * sc)) + 1):
            for x in range(int(np.floor(g[1] + dx + (c0 - gx0) * sc)) - 1, int(np.ceil(g[1] + dx + (c1 - gx0) * sc)) + 1):
                sy, sx = int(round(gy0 + (y - g[0] - dy) / sc)), int(round(gx0 + (x - g[1] - dx) / sc))
                if not (r0 <= sy < r1 and c0 <= sx < c1) or D0[sy, sx, 3] == 0:
                    continue
                n += 1
                ok = 0 <= y < pic.shape[0] and 0 <= x < pic.shape[1] and pic[y, x, 3]
                tot += np.sqrt(((pic[y, x, :3].astype(float) - D0[sy, sx, :3]) ** 2).sum()) if ok else 300.0
        return tot / max(n, 1)
    best = min((dist(sc, dy, dx), sc) for sc in np.arange(0.70, 1.401, 0.05) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    best = min([best] + [(dist(sc, dy, dx), sc) for sc in np.arange(best[1] - 0.04, best[1] + 0.041, 0.02)
                         for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
    return best[1], best[0]


def measure():
    """The ZOOM table: frames read at their old boxes' zoom, each head fitted (head_fit); a sheet's zoom the mean of its
    good fits' box zoom x head scale, without one its gems' blue area against the design's x the median ratio."""
    ZOOM.clear()
    raw = read_all()
    fits, gems = {}, {}
    d_area = gem(D0)[2]
    for s in sheets():
        a = np.asarray(Image.open(lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        for k, m in cells(s, figure(a)):
            n = f"{s['tag']}_{k}"
            sq = raw[n][0]
            ys, xs = np.nonzero(sq[..., 3] > 0)
            sc, err = head_fit(sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
            fits[n] = (raw[n][3] * sc, err)
            gems[n] = np.sqrt(gem(a, m)[2] / d_area)
    ratio = float(np.median([fits[n][0] / gems[n] for n in fits if fits[n][1] <= GOOD]))
    out = {}
    for s in sheets():
        ns = [f"{s['tag']}_{k}" for k in s["frames"]]
        good = [fits[n][0] for n in ns if fits[n][1] <= GOOD]
        out[s["name"]] = round(float(np.mean(good)) if good else float(np.mean([gems[n] for n in ns])) * ratio, 2)
    return out, ratio


def read_all():
    """{"<tag>_<frame>": (squares, the old box's middle and bottom from the pivot in design squares, the zoom)}."""
    out = {}
    for s in sheets():
        a = np.asarray(Image.open(lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        fig = figure(a)
        for k, m in cells(s, fig):
            n = f"{s['tag']}_{k}"
            ys, xs = np.nonzero(m)
            gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
            L, T, R, B = old_box(OLD[s["tag"]][k - 1])
            zoom = zoom_of(s, n, gh)
            sq = sample(a, m, round(gh / zoom), round(gw / zoom))
            mid = (L + R) / 2 * PPU
            out[n] = (sq, mid, B * PPU, zoom)
    return out


def skull(p):
    """(top row, middle column) of the shaved skull: the highest skin squares (hue 15-40, saturation .2-.6, value .6 up),
    the middle of the skin on its top three rows."""
    import colorsys
    sk = np.zeros(p.shape[:2], bool)
    for y, x in zip(*np.nonzero(p[..., 3])):
        h, s_, v = colorsys.rgb_to_hsv(*(p[y, x, :3] / 255.0))
        sk[y, x] = 15 <= h * 360 <= 40 and 0.2 <= s_ <= 0.6 and v >= 0.6
    top = int(np.nonzero(sk.any(1))[0].min())
    xs = np.nonzero(sk[top:top + 3].any(0))[0]
    return top, (xs.min() + xs.max() + 1) / 2.0


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}: the box's middle on the old box's
    middle and its bottom on the old box's bottom, from the design's pivot (its shoes' middle on its soles' row)."""
    import casts_draven_hd as CD
    px = CD.shoes_mid(D0)
    out = {}
    for n, (sq, mid, bottom, zoom) in read_all().items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        # (the old falls lay a pixel under the soles' line: nothing may hang under it - the health bar is there)
        x, y = int(round(px + mid - pic.shape[1] / 2)), min(int(round(GROUND + bottom - pic.shape[0])), GROUND - pic.shape[0])
        if n.rsplit("_", 1)[0] in STEADY:
            old = OLD[n.rsplit("_", 1)[0]][int(n.rsplit("_", 1)[1]) - 1]
            ot, ox = skull(old)
            want_x = px + (ox - old.shape[1] / 2) * PPU                 # the old skull's column on the design's grid
            want_top = GROUND - (old.shape[0] / 2 + OLD_SOLES - ot) * PPU
            nt, nx = skull(pic)
            x = int(round(want_x - nx))
            y = min(GROUND - pic.shape[0], max(y, int(round(want_top - nt))))
        out[n] = (pic, x, y)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        table, ratio = measure()
        print(f"head / gem {ratio:.3f}")
        print("ZOOM =", json.dumps(table))
        return
    fr = placed()
    print("frames", len(fr))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    for t in TAGS:
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        x0 = min(min(fr[n][1] for n in names), 0) - 2
        x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), D0.shape[1]) + 2
        y0 = min(min(fr[n][2] for n in names), 0) - 2
        y1 = max(GROUND, max(fr[n][2] + fr[n][0].shape[0] for n in names)) + 2
        Z, W, Hh = 2, x1 - x0, y1 - y0
        tiles = [("design", (D0, 0, 0))] + [(n, fr[n]) for n in names]
        can = Image.new("RGB", (len(tiles) * (W * Z + 4), Hh * Z), (40, 40, 40))
        for i, (n, (pic, x, y)) in enumerate(tiles):
            tile = Image.new("RGBA", (W, Hh), (150, 165, 150, 255))
            tile.alpha_composite(Image.fromarray(pic), (x - x0, y - y0))
            can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
        can.save(os.path.join(a.review, f"placed_{t}.png"))
    print("written", a.review)


if __name__ == "__main__":
    main()
