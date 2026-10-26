#!/usr/bin/env python3
"""Vayne's actions from Codex's whole-frame redraw (assets/source/vayne/hd/casts: tools/art/pack_vayne_actions.py's
pack, delivered 2026-10-26; the raw generations stay in Codex's outputs folder new-chat-9/outputs/vayne-actions/raw),
read onto the design's squares - tools/art/casts_leesin_hd.py's way.

Codex drew them as finished pictures, not on the templates' 7-px grid: a near-white background (not transparent),
anti-aliased edges, colours off the design's palette, each figure at its own zoom. The zoom is read off her HEAD: the
design's head (HEAD: crown to chin, hair and face) slid over each frame brought to design squares at zooms 5-14 px a
square (masked squared difference by FFT, then 0.05 steps about the best) - no anchor colour, the glasses' red is the
cape's. One zoom a SHEET: the mean of its frames' good fits (GOOD, and within 15 % of the frame's box zoom x the median
head / box ratio); a sheet without one (the rolls, the falls, the flinch: the head turned) the median of its tag's
good fits, else of all - Codex drew the set at about one scale. ZOOM holds the result (--measure works it out again).

Each frame then: the white keyed off from the sheet's edges and the white it walls in, every piece of the drawing given
to the cell its centre of mass falls in, sampled at its sheet's zoom (each square the colour most of its pixels snap to
in the design's palette, nearest in Lab), and placed where the old frame stood: its box's bottom on the old box's
bottom, its box's middle on the old box's middle, both from the pivot (soles 11.5 old pixels under the frame's centre,
on the design's soles' row). The run (STEADY) is shifted sideways so every frame's head stands in one column - the old
run held its glasses within a pixel of one column, Codex's swayed 10 squares - and its second half is its first again
(REUSE): Codex's 7th frame came in the wrong phase (front foot planted, the back one lifted - the old 7th is the 3rd's
twin), and with both legs one colour a half cycle's twin is the same picture. Death's 2nd frame is its 1st (Codex drew
her already flat on the ground, the old one still stands: a drop and a rise).

    python tools/art/casts_vayne_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_vayne_hd.py --measure         # the ZOOM table again (slow: a few minutes)
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
HD = os.path.join(ROOT, "assets", "source", "vayne", "hd")
SRC = os.path.join(HD, "casts")
TAGS = ["run", "attack", "attack_q", "skill", "skill_back", "skill2", "ult", "hit", "dead"]
OLD_SOLES = 11.5                # old frames: the soles this many pixels under the frame's centre (its pivot)
# px of Codex's drawing a design square, a sheet: the first delivery's as measured 2026-10-26 (the frames the user
# passed: 「其他动作通过」), the run's four sheets and E's last frame from the redo (RUN_REDO_PROMPT.md) by --measure
ZOOM = {"run_1": 7.53, "run_2": 6.85, "run_3": 7.42, "run_4": 7.9, "attack_1": 8.2, "attack_2": 8.0, "attack_3": 7.8,
        "attack_4": 8.0, "attack_q_1": 7.5, "attack_q_2": 7.85, "attack_q_3": 7.3, "attack_q_4": 7.4,
        "attack_q_5": 7.85, "skill_1": 7.85, "skill_2": 7.85, "skill_3": 7.85, "skill_back_1": 7.85,
        "skill_back_2": 7.85, "skill_back_3": 7.85, "skill_back_4": 7.85, "skill_back_5": 7.85, "skill2_1": 8.1,
        "skill2_2": 8.25, "skill2_3": 8.55, "skill2_4": 8.4, "skill2_5": 7.25, "ult_1": 7.55, "ult_2": 8.3,
        "ult_3": 7.95, "ult_4": 8.2, "ult_5": 8.0, "hit_1": 7.85, "dead_1": 7.85, "dead_2": 7.85, "dead_3": 7.85,
        "dead_4": 7.85, "dead_5": 7.85, "dead_6": 7.85}
STEADY = {"run"}                # one head column (head_place): the old run held its glasses within 1 px of one column
REUSE = {"run_5": "run_1", "run_6": "run_2", "run_7": "run_3", "run_8": "run_4",  # the run's second half = its first
         "dead_2": "dead_1"}    # (Codex drew death's 2nd frame flat on the ground; the old one still stands)
GOOD = 100                      # a head match this good (rms colour distance a square) counts
WHITE = 238                     # the background: every channel this light, grey (spread <= 12), reached from the edge


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


D0 = design()
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles
PPU = 2.55                      # design squares a game pixel: 102 rows / 2.55 = her 1x 40 (design_vayne_hd)
PAL = np.unique(D0[D0[..., 3] > 0][:, :3], axis=0)
PAL_LAB = color.rgb2lab(PAL[None].astype(float) / 255.0)[0]


def sheets():
    with open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)["sheets"]


def old_frames():
    """{tag: [RGBA]} of the old 1x sheet (assets/source/vayne/hd/old: main's league_vayne before the redo)."""
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
    the ponytail's sweep, between an arm and the body) - neutral like the background and 100 px up."""
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


HEAD = (8, 30, 44, 74)          # the design's head for the match: rows 8-29 (crown to chin), columns 44-73
ZOOMS = np.arange(5.0, 14.01, 0.25)


def head_fit(a, m):
    """(zoom, mean colour distance, (row, col) of the head's top-left in the cell's squares at that zoom): the drawing
    a[m] brought to design squares at each zoom (px a square, box-averaged), the design's head slid over it (masked
    squared difference by FFT) - the best place and zoom. No anchor: the glasses' red is the cape's."""
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb = np.where(m[y0:y1, x0:x1, None], a[y0:y1, x0:x1, :3], 255).astype(np.uint8)
    r0, r1, c0, c1 = HEAD
    T = D0[r0:r1, c0:c1].astype(float)
    M = (T[..., 3] > 0).astype(float)
    T = T[..., :3]
    n = M.sum()
    best = (1e18, None, None)
    for z in list(ZOOMS) + [None]:
        if z is None:                   # then finer about the best
            for z2 in np.arange(best[1] - 0.2, best[1] + 0.201, 0.05):
                best = min(best, fit_at(rgb, z2, T, M, n), key=lambda b: b[0])
            break
        best = min(best, fit_at(rgb, z, T, M, n), key=lambda b: b[0])
    return best[1], best[0], best[2]


def fit_at(rgb, z, T, M, n):
    """(rms distance, zoom, place) of the head's best place in rgb brought to design squares at zoom z."""
    from scipy.signal import fftconvolve
    h, w = max(1, round(rgb.shape[0] / z)), max(1, round(rgb.shape[1] / z))
    if h < T.shape[0] or w < T.shape[1]:
        return (1e18, z, None)
    I = np.asarray(Image.fromarray(rgb).resize((w, h), Image.BOX)).astype(float)
    ssd = fftconvolve((I ** 2).sum(-1), M[::-1, ::-1], mode="valid") + (M[..., None] * T ** 2).sum()
    for c in range(3):
        ssd -= 2 * fftconvolve(I[..., c], (M * T[..., c])[::-1, ::-1], mode="valid")
    j, i = np.unravel_index(int(np.argmin(ssd)), ssd.shape)
    return (np.sqrt(max(ssd[j, i], 0) / n), z, (j, i))


def measure():
    """The ZOOM table: every frame's head fitted (head_fit). A fit counts when it is good (GOOD) and within 15 % of
    its frame's box zoom x the median head / box ratio (a head matched on the cape or the crossbow lands far off). A
    sheet's zoom the mean of its good fits; a sheet without one (the rolls, the falls, the flinch: the head turned)
    the median of its tag's good fits, else of all good fits - Codex drew the set at about one scale, its boxes swing
    with the poses (a crouch's box is half a stand's)."""
    fits, boxes = {}, {}
    for s in sheets():
        a = np.asarray(Image.open(lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        for k, m in cells(s, figure(a)):
            n = f"{s['tag']}_{k}"
            z, err, _ = head_fit(a, m)
            ys = np.nonzero(m.any(1))[0]
            T, B = old_box(OLD[s["tag"]][k - 1])[1::2]
            fits[n], boxes[n] = (z, err), (ys.max() + 1 - ys.min()) / ((B - T) * PPU)
    ratio = float(np.median([fits[n][0] / boxes[n] for n in fits if fits[n][1] <= GOOD]))
    good = {n: z for n, (z, e) in fits.items() if e <= GOOD and abs(z / (boxes[n] * ratio) - 1) <= 0.15}
    for n in fits:
        print(n, "head zoom", round(fits[n][0], 2), "err", round(fits[n][1], 1), "box zoom", round(boxes[n], 2),
              "GOOD" if n in good else "")
    out = {}
    for s in sheets():
        g = [good[f"{s['tag']}_{k}"] for k in s["frames"] if f"{s['tag']}_{k}" in good]
        tag = [z for n, z in good.items() if n.rsplit("_", 1)[0] == s["tag"]]
        out[s["name"]] = round(float(np.mean(g)) if g else float(np.median(tag or list(good.values()))), 2)
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


def head_place(pic):
    """(row, column) of the design's head (HEAD's top-left) where it fits the read squares best (masked squared
    difference by FFT; the squares already at the design's head size)."""
    from scipy.signal import fftconvolve
    r0, r1, c0, c1 = HEAD
    T = D0[r0:r1, c0:c1].astype(float)
    M = (T[..., 3] > 0).astype(float)
    J = np.where(pic[..., 3:] > 0, pic[..., :3].astype(float), 400.0)
    ssd = fftconvolve((J ** 2).sum(-1), M[::-1, ::-1], mode="valid") + (M[..., None] * T[..., :3] ** 2).sum()
    for c in range(3):
        ssd -= 2 * fftconvolve(J[..., c], (M * T[..., c])[::-1, ::-1], mode="valid")
    return np.unravel_index(int(np.argmin(ssd)), ssd.shape)


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}: the box's middle on the old box's
    middle and its bottom on the old box's bottom, from the design's pivot (its shoes' middle on its soles' row). The
    run (STEADY) then shifted sideways so every frame's head stands in one column (their mean), and its second half
    the first again (REUSE)."""
    import casts_draven_hd as CD
    px = CD.shoes_mid(D0)
    out = {}
    for n, (sq, mid, bottom, zoom) in read_all().items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        # (the old falls lay a pixel under the soles' line: nothing may hang under it - the health bar is there)
        x, y = int(round(px + mid - pic.shape[1] / 2)), min(int(round(GROUND + bottom - pic.shape[0])), GROUND - pic.shape[0])
        out[n] = (pic, x, y)
    for n, src in REUSE.items():
        out[n] = out[src]
    for tag in STEADY:
        names = [n for n in out if n.rsplit("_", 1)[0] == tag and n not in REUSE]
        col = {n: head_place(out[n][0])[1] + out[n][1] for n in names}
        mean = int(round(np.mean(list(col.values()))))
        for n in names:
            pic, x, y = out[n]
            out[n] = (pic, x + mean - col[n], y)
        for n, src in REUSE.items():
            if n.rsplit("_", 1)[0] == tag:
                out[n] = out[src]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        table, ratio = measure()
        print(f"head / box {ratio:.3f}")
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
