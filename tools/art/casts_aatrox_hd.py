#!/usr/bin/env python3
"""Aatrox's actions from Codex's whole-frame redraw (assets/source/aatrox/hd/casts: tools/art/pack_aatrox_actions.py's pack,
delivered 2026-11-03, Documents/Codex/2026-11-03/new-chat-3/outputs/b2_actions_full.zip: aatrox-actions) read onto the
design's squares - tools/art/casts_viego_hd.py's reading (casts_rengar_hd's keying, cells and palette sampling), pointed
at his design (the user, 2026-11-03: 「继续加四个 魔腾 凯南 剑魔 丽桑卓」「另外四个英雄codex全部交付了 你做到完美后喊我review」).

hd/casts holds Codex's 73 sheets (each its chosen raw generation byte for byte, redos included), drawn on a
near-white ground: casts_rengar_hd.figure keys it off. Each frame's zoom is the median of the zoom its HEIGHT gives
(--heights: the drawing's box over the old frame's body), the one his head gives against the design's (--heads) and
the one its area gives (calibrated on the run); the old frame's body leaves out what the old sheet baked in, the fire, sparks, chains and eruptions of his Q, W and empowered strikes:
only what lies within two pixels of the dark outline counts (OLD_BODY). Each frame is then placed where the old body
stood: its box's middle on the old box's middle and its bottom on the old box's bottom, from the pivot, on the design's
grid. He stands on the ground (HOVER 0); the design's pivot column (PIVOT) is where the design lies best over the
old idle_base.

    python tools/art/casts_aatrox_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_aatrox_hd.py --heights         # each frame's zoom from its height against the old frame's
    python tools/art/casts_aatrox_hd.py --heads           # each placed frame's head against the design's
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
sys.path.insert(0, HERE)
import casts_rengar_hd as CS  # noqa: E402
import pack_aatrox_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "aatrox", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 40          # rows over his 1x 40 (design_aatrox_hd: his highest point to his soles)
HOVER = 0                       # (he stands on the ground: his old idle_base's soles on its soles' line)
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1 + int(round(HOVER * PPU))   # the soles' line, under him
HEAD = (7, 31, 0, 97)         # the design's head: rows 7-30 (the tips of his horns to his chin), its sides
# px of Codex's drawing a design square: each frame's the median of three - the zoom its height gives against the
# old body's (heights()), the one its head gives against the design's (heads()) and the one its area gives against the
# old body's (calibrated on the run) - so one raised blade, a lying body or a stray lock does not size a frame alone
# (the user, on Sett: 「瑟提感觉模型会一大一小？」); a sheet's ZOOM is its frames' mean
ZOOM = {'run_1': 6.96, 'run_2': 6.94, 'run_3': 7.04, 'run_4': 6.92, 'attack_1': 6.92, 'attack_2': 6.76, 'attack_3': 6.92, 'attack_p_1': 6.97, 'attack_p_2': 6.9, 'attack_p_3': 7.0, 'attack_p_4': 6.96, 'skill_1': 6.03, 'skill_2': 6.1, 'skill_3': 6.11, 'skill_4': 6.23, 'skill_5': 6.21, 'skill_6': 5.92, 'q2_1': 6.17, 'q2_2': 6.47, 'q2_3': 7.54, 'q2_4': 6.34, 'q2_5': 7.31, 'q3_1': 5.11, 'q3_2': 5.21, 'q3_3': 5.46, 'q3_4': 6.44, 'q3_5': 6.41, 'skill2_1': 6.95, 'skill2_2': 6.97, 'ult_1': 6.92, 'ult_2': 6.82, 'ult_3': 7.37, 'ult_4': 7.09, 'ult_5': 7.57, 'ult_6': 7.31, 'ult_7': 7.84, 'ult_8': 8.45, 'hit_1': 7.01, 'dead_1': 5.93, 'dead_2': 6.19, 'dead_3': 5.91, 'dead_4': 5.91, 'attack_r_1': 7.01, 'attack_r_2': 7.29, 'attack_r_3': 7.16, 'attack_r_4': 7.26, 'attack_r_5': 7.51, 'attack_p_r_1': 7.53, 'attack_p_r_2': 7.02, 'attack_p_r_3': 6.91, 'attack_p_r_4': 8.16, 'attack_p_r_5': 7.6, 'skill_r_1': 6.1, 'skill_r_2': 6.07, 'skill_r_3': 6.83, 'skill_r_4': 6.24, 'skill_r_5': 6.09, 'skill_r_6': 6.21, 'q2_r_1': 5.93, 'q2_r_2': 6.33, 'q2_r_3': 7.23, 'q2_r_4': 6.57, 'q2_r_5': 6.86, 'q2_r_6': 6.86, 'q3_r_1': 5.04, 'q3_r_2': 5.26, 'q3_r_3': 5.28, 'q3_r_4': 8.06, 'q3_r_5': 6.42, 'skill2_r_1': 7.83, 'skill2_r_2': 7.19, 'skill2_r_3': 7.45, 'skill2_r_4': 7.42}
FRAME_ZOOM = {'run_1': 7.02, 'run_2': 6.91, 'run_3': 6.95, 'run_4': 6.93, 'run_5': 6.97, 'run_6': 7.11, 'run_7': 6.84, 'run_8': 7.01, 'attack_2': 6.92, 'attack_3': 6.77, 'attack_4': 6.76, 'attack_5': 6.92, 'attack_p_1': 6.97, 'attack_p_2': 6.9, 'attack_p_3': 7.0, 'attack_p_4': 7.0, 'attack_p_5': 6.96, 'skill_1': 5.94, 'skill_2': 6.11, 'skill_3': 6.16, 'skill_4': 6.04, 'skill_5': 6.11, 'skill_6': 6.23, 'skill_7': 6.21, 'skill_8': 5.92, 'q2_1': 6.21, 'q2_2': 6.12, 'q2_3': 6.57, 'q2_4': 6.37, 'q2_5': 7.54, 'q2_6': 6.34, 'q2_7': 7.31, 'q3_1': 5.16, 'q3_2': 5.05, 'q3_3': 5.3, 'q3_4': 5.13, 'q3_5': 5.46, 'q3_6': 6.44, 'q3_7': 6.41, 'skill2_2': 6.95, 'skill2_3': 6.95, 'skill2_4': 6.97, 'ult_1': 6.92, 'ult_2': 6.82, 'ult_3': 7.37, 'ult_4': 7.09, 'ult_5': 7.57, 'ult_6': 7.31, 'ult_7': 7.84, 'ult_8': 8.45, 'hit_1': 6.98, 'hit_2': 7.03, 'dead_2': 5.99, 'dead_3': 5.86, 'dead_4': 6.19, 'dead_5': 5.91, 'dead_6': 5.91, 'attack_r_1': 7.01, 'attack_r_2': 7.29, 'attack_r_3': 7.16, 'attack_r_4': 7.26, 'attack_r_5': 7.51, 'attack_p_r_1': 7.53, 'attack_p_r_2': 7.02, 'attack_p_r_3': 6.91, 'attack_p_r_4': 8.16, 'attack_p_r_5': 7.6, 'skill_r_1': 6.1, 'skill_r_2': 6.03, 'skill_r_3': 6.11, 'skill_r_4': 6.83, 'skill_r_5': 6.24, 'skill_r_6': 6.09, 'skill_r_7': 6.21, 'q2_r_1': 5.93, 'q2_r_2': 6.19, 'q2_r_3': 6.46, 'q2_r_4': 7.23, 'q2_r_5': 6.57, 'q2_r_6': 6.86, 'q2_r_7': 6.86, 'q3_r_1': 5.01, 'q3_r_2': 5.07, 'q3_r_3': 5.36, 'q3_r_4': 5.16, 'q3_r_5': 5.28, 'q3_r_6': 8.06, 'q3_r_7': 6.42, 'skill2_r_2': 7.83, 'skill2_r_3': 7.19, 'skill2_r_4': 7.45, 'skill2_r_5': 7.42}
ZOOMS = np.arange(4.5, 9.01, 0.1)                       # the zooms the head is searched at (6-px templates)
PIVOT = 63                      # the design's column on the old idle_base's pivot (overlap peak 0.81)

# casts_rengar_hd's reading on his design
CS.D0, CS.HEAD = D0, HEAD
CS.PAL = np.unique(D0[D0[..., 3] > 0][:, :3], axis=0)
CS.PAL_LAB = color.rgb2lab(CS.PAL[None].astype(float) / 255.0)[0]


def head_mask():
    """The head in HEAD's box: its largest opaque piece, holes filled."""
    r0, r1, c0, c1 = HEAD
    op = D0[r0:r1, c0:c1, 3] > 0
    lbl, n = ndimage.label(op)
    m = lbl == int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1)))) + 1
    return ndimage.binary_fill_holes(m)


CS.HEAD_MASK = head_mask()


def sheets():
    with open(CS.lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)["sheets"]


OLD = PK.old_frames(CS.lp(os.path.join(HD, "old", "sheet.png")), CS.lp(os.path.join(HD, "old", "anim.fanim")))


# the colours of his body: every colour of the old run and idle_base (no effects in them)
BODY_PAL = np.unique(np.concatenate([f[f[..., 3] > 0][:, :3] for f in [r[0] for r in OLD["run"]] + [PK.idle_sheet()]]),
                     axis=0).astype(int)
OFF = None


def old_body(fr):
    """An old frame's body: its pixels in the body's colours (within 40) and within two pixels of the dark outline (the
    baked effects have none), the largest 8-connected piece and any of 30 pixels up."""
    op = fr[..., 3] > 0
    d = np.abs(fr[..., :3].astype(int)[:, :, None, :] - BODY_PAL[None, None]).sum(-1).min(-1)
    m = op & (d <= 40) & ndimage.binary_dilation(op & (fr[..., :3].max(-1) < 90), structure=np.ones((3, 3)), iterations=2)
    lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
    sz = ndimage.sum(m, lbl, range(1, n + 1))
    return np.isin(lbl, [int(np.argmax(sz)) + 1] + [i + 1 for i in range(n) if sz[i] >= 30])


def old_box(tag, k, off=False):
    """The old frame's body box from its pivot, in 1x pixels: (left, top, right, bottom); y up negative (off: OFF's
    colours left out)."""
    fr, _, (pvx, pvy) = OLD[tag][k - 1]
    m = old_body(fr)
    if off and OFF is not None:
        m &= ~OFF(fr[..., :3].astype(int))
    ys, xs = np.nonzero(m)
    return xs.min() - pvx, ys.min() - pvy, xs.max() + 1 - pvx, ys.max() + 1 - pvy


def frame_masks(s):
    """(sheet picture, [(frame, mask)]) of a sheet."""
    a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
    return a, CS.cells(s, CS.figure(a))


EYE_COVER = 0.15                # a square this much of an eye's glow is an eye square (design_aatrox_hd's FACE_GLOW)


def eyes(a, m, sq):
    """His glowing eyes (and the glow of his mouth) kept: each is a slanted stroke a square or two big, and off the
    grid the majority read dulled it into the black visor round it or lost it - his head read as the back of a helmet
    (the user: 「剑魔的头看起来只看后面」). Every small glowing red piece in the drawing (r 200+, g and b 110 at most;
    1/5 to 6 squares big, at most 3 squares across) walled in by the dark visor (half the ring round it near-black)
    marks the squares it covers by EYE_COVER, and at least the one under its middle, the design colour nearest its
    mean - the sword's and the wings' red edges are long strips on crimson or violet, the chest core bigger."""
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rows, cols = sq.shape[:2]
    hy, hx = (y1 - y0) / rows, (x1 - x0) / cols
    rgb = a[..., :3].astype(int)
    glow = m & (rgb[..., 0] >= 200) & (rgb[..., 1] <= 110) & (rgb[..., 2] <= 110)
    dark = m & (rgb.max(-1) < 80)
    lbl, n = ndimage.label(glow, structure=np.ones((3, 3)))
    for i, sl in enumerate(ndimage.find_objects(lbl)):
        piece = lbl[sl] == i + 1
        size = int(piece.sum())
        if not hy * hx * 0.2 <= size <= hy * hx * 6:
            continue
        if max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start) > 3 * max(hy, hx):
            continue
        big = tuple(slice(max(0, q.start - 4), q.stop + 4) for q in sl)
        own = np.zeros(lbl[big].shape, bool)
        own[sl[0].start - big[0].start:sl[0].stop - big[0].start, sl[1].start - big[1].start:sl[1].stop - big[1].start] = piece
        ring = ndimage.binary_dilation(own, iterations=3) & ~own & m[big]
        if not ring.any() or dark[big][ring].mean() < 0.5:
            continue
        py, px = np.nonzero(own)
        py, px = py + big[0].start, px + big[1].start
        lab = color.rgb2lab(a[py, px, :3][None].astype(float) / 255.0)[0].mean(0)
        col = CS.PAL[((CS.PAL_LAB - lab) ** 2).sum(-1).argmin()]
        rr = ((py - y0) / hy).astype(int).clip(0, rows - 1)
        cc = ((px - x0) / hx).astype(int).clip(0, cols - 1)
        cells = {}
        for r, c in zip(rr, cc):
            cells[(r, c)] = cells.get((r, c), 0) + 1
        hit = [rc for rc, k in cells.items() if k >= EYE_COVER * hy * hx] or [(int(rr.mean()), int(cc.mean()))]
        for r, c in hit:
            sq[r, c] = (*col, 255)
    return sq


def at_zoom(a, m, zoom):
    """The drawing a[m] read at `zoom` px a square, cropped (his eyes kept: eyes())."""
    ys, xs = np.nonzero(m)
    gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
    sq = eyes(a, m, CS.sample(a, m, round(gh / zoom), round(gw / zoom)))
    yy, xx = np.nonzero(sq[..., 3] > 0)
    return sq[yy.min():yy.max() + 1, xx.min():xx.max() + 1]


def read_all():
    """{"<tag>_<frame>": (squares, the old box's middle and bottom from the pivot in design squares, the zoom)}."""
    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        for k, m in ms:
            L, T, R, B = old_box(s["tag"], k)
            z = FRAME_ZOOM.get(f"{s['tag']}_{k}", ZOOM[s["name"]])
            out[f"{s['tag']}_{k}"] = (at_zoom(a, m, z), (L + R) / 2 * PPU, B * PPU, z)
    for tag, m in PK.SAME.items():
        for k, src in m.items():
            if src == PK.DESIGN:
                continue
            L, T, R, B = old_box(tag, k)
            sq, _, _, z = out[f"{src[0]}_{src[1]}"]
            out[f"{tag}_{k}"] = (sq, (L + R) / 2 * PPU, B * PPU, z)
    return out


def area():
    """Each sheet's zoom from its figure's area: the square root of its frames' mean opaque area over the design's."""
    des = float((D0[..., 3] > 0).sum())
    out = {}
    for s in sheets():
        _, ms = frame_masks(s)
        out[s["name"]] = round(float(np.sqrt(np.mean([m.sum() for _, m in ms]) / des)), 2)
        print(s["name"], out[s["name"]], flush=True)
    return out


def _largest(m):
    lbl, n = ndimage.label(m)
    return float(ndimage.sum(m, lbl, range(1, n + 1)).max()) if n else 0.0


def _skin(a):
    """His head's size: the glowing orange core in his chest, its largest piece (joined across one-square
    gaps) - his steel is everywhere; the core sits under his head at its size."""
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = op & (r >= 210) & (g >= 60) & (g <= 180) & (b <= 90)
    lbl, n = ndimage.label(ndimage.binary_closing(m, structure=np.ones((3, 3))), structure=np.ones((3, 3)))
    if n < 2:
        return m
    return m & (lbl == int(np.argmax(ndimage.sum(m, lbl, range(1, n + 1)))) + 1)


def heads():
    """{"<tag>_<frame>": skin}: each placed frame's face skin against the design's - the square root of its
    area over the design's (1.0: the design's size; ZOOM is right when it is near 1)."""
    ds = float(_skin(D0).sum())
    out = {}
    for n, (pic, _, _) in placed().items():
        out[n] = round((_skin(pic).sum() / ds) ** 0.5, 2)
        print(n, out[n], flush=True)
    return out


def heights():
    """{"<tag>_<frame>": zoom}: each drawn frame's zoom from its HEIGHT - its drawing's box height over the old frame's
    body's box height in design squares, so the same figure is as tall as before frame by frame; a sheet's ZOOM is its
    frames' mean."""
    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        for k, m in ms:
            L, T, R, B = old_box(s["tag"], k, off=True)
            if OFF is not None:
                m = m & ~OFF(a[..., :3].astype(int))
            ys = np.nonzero(m.any(1))[0]
            out[f"{s['tag']}_{k}"] = round(float((ys.max() + 1 - ys.min()) / ((B - T) * PPU)), 2)
            print(s["name"], k, out[f"{s['tag']}_{k}"], flush=True)
    return out


def measure():
    """Each frame's (zoom, error): read at each of ZOOMS, the design's head at its own size matched over it
    (casts_rengar_hd.match; the falls also tried turned a quarter), the zoom it fits best."""
    tpl = [CS.head_tpl(1.0, t) for t in (0, 1)]
    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        for k, m in ms:
            best = None
            for z in ZOOMS:
                pic = at_zoom(a, m, z)
                for rgb, hm in tpl[:2 if s["tag"] == "dead" else 1]:
                    e, y, x = CS.match(pic, rgb, hm, 2)
                    e, y, x = CS.match(pic, rgb, hm, 1, (y, x))
                    if best is None or e < best[1]:
                        best = (round(float(z), 2), round(float(e), 1))
            out[f"{s['name']} {k}"] = best
            print(s["name"], k, best, flush=True)
    return out


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}: the box's middle on the old box's
    middle and its bottom on the old box's bottom, from the design's pivot; nothing under the soles' row."""
    out = {}
    for n, (sq, mid, bottom, zoom) in read_all().items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        x = int(round(PIVOT + mid - pic.shape[1] / 2))
        y = min(int(round(GROUND + bottom - pic.shape[0])), GROUND - pic.shape[0])
        out[n] = (pic, x, y)
    for n in THROWN:
        out[n] = thrown(n, *out[n])
    for n, (pic, x, y) in out.items():
        out[n] = (body_only(pic), x, y)
    return out


def body_only(pic, keep_ahead=False):
    """The picture with its loose pieces (8-connected, under 80 squares: stray specks) taken off (keep_ahead: the ones
    right of the body's middle kept)."""
    lbl, n = ndimage.label(pic[..., 3] > 0, structure=np.ones((3, 3)))
    if n < 2:
        return pic
    idx = range(1, n + 1)
    sz = ndimage.sum(np.ones(lbl.shape), lbl, idx)
    cx = [c[1] for c in ndimage.center_of_mass(np.ones(lbl.shape), lbl, idx)]
    xs = np.nonzero(lbl == int(np.argmax(sz)) + 1)[1]
    mid = (xs.min() + xs.max()) / 2
    out = pic.copy()
    out[np.isin(lbl, [i + 1 for i in range(n) if sz[i] < 80 and not (keep_ahead and cx[i] > mid)])] = 0
    return out


THROWN = []                     # (no loose piece to move)


def pieces(a):
    """(the largest 8-connected piece's mask, the others' of 40 squares up) of a picture."""
    lbl, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    sz = ndimage.sum(np.ones(lbl.shape), lbl, range(1, n + 1))
    big = int(np.argmax(sz)) + 1
    return lbl == big, np.isin(lbl, [i + 1 for i in range(n) if i + 1 != big and sz[i] >= 40])


def thrown(name, pic, x, y):
    """The frame with its loose sword moved, as a whole, to where the old frame's loose sword is (its middle on the
    old one's, on the design's grid); the body stays."""
    tag, k = name.rsplit("_", 1)
    fr, _, (pvx, pvy) = OLD[tag][int(k) - 1]
    _, old_sword = pieces(fr)
    oy, ox = (np.array(np.nonzero(old_sword)).mean(1) - (pvy, pvx)) * PPU + (GROUND, PIVOT)
    body, sword = pieces(pic)
    ys, xs = np.nonzero(sword)
    dy, dx = int(round(oy - (y + ys.mean()))), int(round(ox - (x + xs.mean())))
    by, bx = np.nonzero(body)
    Y = np.concatenate([by + y, ys + y + dy])
    X = np.concatenate([bx + x, xs + x + dx])
    out = np.zeros((Y.max() + 1 - Y.min(), X.max() + 1 - X.min(), 4), np.uint8)
    out[by + y - Y.min(), bx + x - X.min()] = pic[by, bx]
    out[ys + y + dy - Y.min(), xs + x + dx - X.min()] = pic[ys, xs]
    return out, int(X.min()), int(Y.min())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true", help="the ZOOM search, frame by frame (slow: minutes)")
    ap.add_argument("--area", action="store_true", help="each sheet's zoom from its figure's area")
    ap.add_argument("--heads", action="store_true", help="each frame's head against the design's at ZOOM")
    ap.add_argument("--heights", action="store_true", help="each frame's zoom from its height against the old frame's")
    a = ap.parse_args()
    if a.measure:
        measure()
        return
    if a.area:
        area()
        return
    if a.heads:
        heads()
        return
    if a.heights:
        heights()
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
