#!/usr/bin/env python3
"""Rengar's actions from Codex's whole-frame redraw (assets/source/rengar/hd/casts: tools/art/pack_rengar_actions.py's
pack, delivered 2026-10-27, Documents/Codex/2026-10-27/new-chat-6/outputs/rengar_actions_done.zip), read onto the
design's squares, tools/art/casts_leesin_hd.py's way.

hd/casts holds Codex's RAW generations (its raw/<name>.png: the chosen take of each sheet; its first attempts and
pre-fix takes left out), not its top-level exports (those are the same pictures snapped to the palette - read from the
raws, as every redo since Akshan). Codex drew finished pictures, not on the templates' 8-px grid: a near-white
background (#FDFDFF), anti-aliased edges, and its own squares 7-14 px from sheet to sheet. So the zoom is read off his
HEAD, as Lee Sin's: the design's head (the mane, the face and the beard; HEAD) matched on each frame at scales
0.70-1.40 - with no gem to pin it (Lee Sin's), the head is SEARCHED over the frame (every place, a coarse step and then
round the best), and the falls try it turned a quarter (he lies on his back, the head to the left). One zoom a SHEET
(both cells are one generation), the mean of its frames whose match is good (GOOD); a sheet with none takes its box
zoom. ZOOM holds the result (--measure works it out again).

Each frame then: the white keyed off from the sheet's edges and the white it walls in, every piece of the drawing given
to the cell its centre of mass falls in, sampled at its sheet's zoom (each square the colour most of its pixels snap to
in the design's palette, nearest in Lab), and placed where the old frame stood: its box's bottom on the old box's
bottom, its box's middle on the old box's middle, both from the pivot (soles 11.5 old pixels under the frame's centre,
on the design's soles' row).

    python tools/art/casts_rengar_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_rengar_hd.py --measure         # the ZOOM table again (slow: a few minutes)
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
HD = os.path.join(ROOT, "assets", "source", "rengar", "hd")
SRC = os.path.join(HD, "casts")
TAGS = ["run", "attack", "leap", "skill", "skill2", "skill_w", "hit", "dead"]
OLD_SOLES = 11.5                # old frames: the soles this many pixels under the frame's centre (its pivot)
# px of Codex's drawing a design square, a sheet: --measure 2026-10-27 (GOOD 130); skill_3, dead_2, dead_3 (the head
# tilted or lying: no good match) the median of the rest
ZOOM = {"run_1": 8.61, "run_2": 8.57, "run_3": 8.46, "run_4": 8.91, "attack_1": 7.39, "attack_2": 7.38,
        "attack_3": 8.12, "leap_1": 7.63, "leap_2": 7.38, "leap_3": 7.81, "leap_4": 7.83, "skill_1": 7.43,
        "skill_2": 8.06, "skill_3": 7.8, "skill_4": 8.04, "skill2_1": 8.45, "skill2_2": 7.83, "skill2_3": 7.58,
        "skill_w_1": 7.79, "skill_w_2": 7.1, "skill_w_3": 8.31, "hit_1": 8.41, "dead_1": 7.74, "dead_2": 7.8,
        "dead_3": 7.8}
HEAD = (1, 35, 32, 61)          # the design's head for the match: rows 1-34 (mane top to beard), columns 32-60
TURNED = {"dead"}               # tags whose frames may lie: the head also tried turned a quarter
GOOD = 130                      # a head match this good (mean colour distance) counts
WHITE = 238                     # the background: every channel this light, grey (spread <= 12), reached from the edge
OUTLINE = 80                    # the outline: every channel under this
RINGED = 0.5                    # a walled-in white is background when this share of what rings it is outline


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


D0 = design()
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles
PPU = D0.shape[0] / 40          # design squares a game pixel: 59 rows over his 1x 40 (design_rengar_hd)
PAL = np.unique(D0[D0[..., 3] > 0][:, :3], axis=0)
PAL_LAB = color.rgb2lab(PAL[None].astype(float) / 255.0)[0]


def sheets():
    with open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)["sheets"]


def old_frames():
    """{tag: [RGBA]} of the old 1x sheet (assets/source/rengar/hd/old: main's league_rengar before the redo)."""
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
    """The drawing's mask: everything but the white reached from the sheet's edges, and the white it walls in (between
    an arm and the body, inside the tail's curl): 100 px up and ringed by the outline. The mane is drawn in the
    background's own white (#FEFEFE against #FDFDFF) between its braids - ringed by its blue-grey shades, not the
    outline, so it stays (keyed by colour alone, as Lee Sin's, it went and left the mane grey: 「怎么还变黑了？」)."""
    rgb = a[..., :3].astype(int)
    white = (rgb.min(-1) >= WHITE) & (rgb.max(-1) - rgb.min(-1) <= 12)
    lbl, n = ndimage.label(white)
    bg = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    dark = rgb.max(-1) < OUTLINE
    for i, sl in enumerate(ndimage.find_objects(lbl)):
        if i + 1 in bg or sl is None:
            continue
        sl = tuple(slice(max(0, s.start - 3), s.stop + 3) for s in sl)
        m = lbl[sl] == i + 1
        if m.sum() < 100:
            continue
        ring = ndimage.binary_dilation(m, iterations=3) & ~m & ~white[sl]
        if ring.any() and dark[sl][ring].mean() >= RINGED:
            bg.add(i + 1)
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


def box_zoom(s, k, gh):
    """The zoom that makes the drawing's box as tall as the old frame's box at PPU."""
    T, B = old_box(OLD[s["tag"]][k - 1])[1::2]
    return gh / round((B - T) * PPU)


def zoom_of(s, k, gh):
    return ZOOM.get(s["name"]) or box_zoom(s, k, gh)


def head_mask():
    """The head alone in HEAD's box: the mane's and the face's whites and blue-greys and the horn (columns 52-62, rows
    0-14), closed over the braids' lines and the face's features - the pauldron and the arm round it left out (they
    move with every pose)."""
    r0, r1, c0, c1 = HEAD
    h = D0[r0:r1, c0:c1].astype(int)
    op = h[..., 3] > 0
    mx, mn = h[..., :3].max(-1), h[..., :3].min(-1)
    m = op & (mx >= 110) & (mx - mn <= 70)
    m[max(0, 0 - r0):15 - r0, 52 - c0:63 - c0] |= op[max(0, 0 - r0):15 - r0, 52 - c0:63 - c0]
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=2)) & op
    lbl, n = ndimage.label(m)
    m = lbl == int(np.argmax(ndimage.sum(m, lbl, range(1, n + 1)))) + 1
    return ndimage.binary_fill_holes(m)


HEAD_MASK = head_mask()


def head_tpl(sc, turn):
    """The design's head (HEAD_MASK) scaled by sc (nearest), turned `turn` quarters counter-clockwise: (rgb float,
    mask)."""
    r0, r1, c0, c1 = HEAD
    h = D0[r0:r1, c0:c1].copy()
    h[~HEAD_MASK, 3] = 0
    h = np.rot90(h, turn)
    im = Image.fromarray(np.ascontiguousarray(h)).resize((max(1, round(h.shape[1] * sc)), max(1, round(h.shape[0] * sc))),
                                                        Image.NEAREST)
    t = np.asarray(im)
    return t[..., :3].astype(float), t[..., 3] > 0


def match(pic, rgb, m, step, around=None):
    """(mean colour distance, y, x) of the template's best place on pic (outside the frame or on its holes 300 a
    square), every `step` places, or round `around` (+-2)."""
    H, W = pic.shape[:2]
    th, tw = m.shape
    pad = np.zeros((H + 2 * th, W + 2 * tw, 4), np.float64)
    pad[th:th + H, tw:tw + W] = pic
    n = m.sum()
    best = None
    if around is None:
        ys, xs = range(0, H + th, step), range(0, W + tw, step)
    else:
        ys = range(max(0, around[0] - 2), min(H + th, around[0] + 3))
        xs = range(max(0, around[1] - 2), min(W + tw, around[1] + 3))
    for y in ys:
        for x in xs:
            win = pad[y:y + th, x:x + tw]
            op = win[..., 3] > 0
            dd = np.sqrt(((win[..., :3] - rgb) ** 2).sum(-1))
            tot = np.where(op, dd, 300.0)[m].sum()
            if best is None or tot / n < best[0]:
                best = (tot / n, y, x)
    return best


def head_fit(pic, turned=False):
    """(scale, mean colour distance, turn): the design's head searched over the frame at scales 0.70-1.40."""
    best = None
    for turn in ((0, 1) if turned else (0,)):
        for sc in np.arange(0.70, 1.401, 0.05):
            rgb, m = head_tpl(sc, turn)
            e, y, x = match(pic, rgb, m, 2)
            e, y, x = match(pic, rgb, m, 1, (y, x))
            if best is None or e < best[0]:
                best = (e, sc, turn, y, x)
    e, sc, turn, y, x = best
    for s2 in np.arange(sc - 0.04, sc + 0.041, 0.02):
        rgb, m = head_tpl(s2, turn)
        e2, y2, x2 = match(pic, rgb, m, 1, (y, x))
        if e2 < e:
            e, sc = e2, s2
    return sc, e, turn


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
            zoom = zoom_of(s, k, gh)
            sq = sample(a, m, round(gh / zoom), round(gw / zoom))
            out[n] = (sq, (L + R) / 2 * PPU, B * PPU, zoom)
    return out


def measure():
    """The ZOOM table: frames read at their old boxes' zoom, each head fitted (head_fit); a sheet's zoom the mean of its
    good fits' box zoom x head scale (none good: left out, the box zoom)."""
    ZOOM.clear()
    raw = read_all()
    out, fits = {}, {}
    for s in sheets():
        good = []
        for k in s["frames"]:
            n = f"{s['tag']}_{k}"
            sq = raw[n][0]
            ys, xs = np.nonzero(sq[..., 3] > 0)
            sc, err, turn = head_fit(sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1], s["tag"] in TURNED)
            fits[n] = (round(float(sc), 2), round(float(err), 1), turn, round(float(raw[n][3]), 2))
            print(n, fits[n], flush=True)
            if err <= GOOD:
                good.append(raw[n][3] * sc)
        if good:
            out[s["name"]] = round(float(np.mean(good)), 2)
    return out, fits


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}: the box's middle on the old box's
    middle and its bottom on the old box's bottom, from the design's pivot (its feet's middle on its soles' row)."""
    import casts_draven_hd as CD
    px = CD.shoes_mid(D0)
    out = {}
    for n, (sq, mid, bottom, zoom) in read_all().items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        # (nothing may hang under the soles' line: the health bar is there)
        x, y = int(round(px + mid - pic.shape[1] / 2)), min(int(round(GROUND + bottom - pic.shape[0])), GROUND - pic.shape[0])
        out[n] = (pic, x, y)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        table, fits = measure()
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
