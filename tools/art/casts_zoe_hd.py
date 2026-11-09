#!/usr/bin/env python3
"""Zoe's actions from Codex's whole-frame redraw (assets/source/zoe/hd/casts: tools/art/pack_zoe_actions.py's pack,
delivered 2026-11-09, Documents/Codex/2026-11-09/new-chat/outputs/zoe_actions_done.zip: zoe-actions) read onto the
design's squares - tools/art/casts_viego_hd.py's reading (casts_rengar_hd's cells and palette sampling), pointed at her
design (the user, 2026-11-09: 「最后重做提莫 菲兹 泽丽吧」「再补一个吧 米利欧」「继续完成5个英雄的动作包 codex交付了」).

hd/casts holds Codex's 53 sheets, each its raw generation byte for byte (raw/<sheet>-repair.png where Codex redrew the
sheet, else <sheet>-original.png; the delivery's root PNGs are Codex's normalized copies, scaled to the template's
figure and snapped to the palette, and are not read), drawn on a transparent ground: figure() keeps alpha 128 and up.
Each frame's zoom is the one its fit over its template's pale figure gives (--fits DIR, DIR the pack's templates,
pack_zoe_actions.py --out: Codex drew every frame on the old frame shown pale at SQ px a square; the drawing scaled
until it overlaps the pale figure best); where it overlaps under 0.65 (another pose), the median of that, the zoom its
HEIGHT gives (--heights: the drawing's box over the old frame's body), the one her size part gives against the design's
(_skin) and the one its area gives (calibrated on the run). The old frame's body leaves out what the old sheet baked in,
(none: her old sheet draws no effects into these tags; its hit 1 is a white flash): only what lies within two pixels of
the dark outline counts (OLD_BODY). Each frame is then placed where the old body stood: its box's middle on the old
box's middle and its bottom on the old box's bottom, from the pivot, on the design's grid. She stands on the ground
(HOVER 0); the design's pivot column (PIVOT) is where the design lies best over the old idle_base.

    python tools/art/casts_zoe_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_zoe_hd.py --fits DIR        # each frame's zoom from its fit over its template
    python tools/art/casts_zoe_hd.py --heights         # each frame's zoom from its height against the old frame's
    python tools/art/casts_zoe_hd.py --heads           # each placed frame's head against the design's
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_rengar_hd as CS  # noqa: E402
import pack_zoe_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "zoe", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 36          # rows over her 1x 36 (design_zoe_v2: the top of her hair to her soles)
HOVER = 0                       # (she stands on the ground: her old idle_base's soles on its soles' line)
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1 + int(round(HOVER * PPU))   # the soles' line, under him
HEAD = (0, 42, 22, 73)          # the design's head: rows 0-41 (the top of her hair to her chin), cols 22-72
# px of Codex's drawing a design square: each frame's from its fit over its template's pale figure (fits(): the
# drawing scaled until it overlaps the old frame Codex drew it on best); where it overlaps under 0.65 (another pose)
# the median of that fit, the zoom its height gives against the old body's (heights()), the one its size part gives
# against the design's (_skin) and the one its area gives against the old body's (calibrated on the run) - the
# height and the area alone moved with a raised staff, a stretched mouth or flowing hair (the user, on Sett:
# 「瑟提感觉模型会一大一小？」); a sheet's ZOOM is its frames' mean. 2026-11-09, under 0.65: skill2_5, skill2_6, dead_7, dead_8, dead_9, dead_10
# then each tag's zooms scaled together until the median of its frames' her pink hair (all its squares) is as big as the
# design's (the user, 2026-11-09: 「千万别出现模型一大一小的问题」): the fit follows the old frame's outline, and
# Codex drew the new figure off that size; one factor a tag keeps the fit's frame-to-frame sizes (no pumping):
# run x1.146, attack x1.109, attack_p x1.157, skill x1.124, skill2 x1.078, ult x1.100, skill_w x1.121, ult_exit x1.141, ult_back x1.117, hit x1.132, dead x1.123. The fit's zooms: FIT_ZOOM
FIT_ZOOM = {'run_1': 7.77, 'run_2': 7.48, 'run_3': 7.55, 'run_4': 7.84, 'run_5': 7.69, 'run_6': 7.48, 'run_7': 7.69, 'run_8': 7.92, 'attack_1': 7.55, 'attack_2': 8.51, 'attack_3': 8.16, 'attack_4': 7.55, 'attack_5': 8.16, 'attack_6': 7.69, 'attack_7': 8.16, 'attack_8': 8.25, 'attack_p_1': 8.42, 'attack_p_2': 8.16, 'attack_p_3': 8.33, 'attack_p_4': 8.33, 'attack_p_5': 8.08, 'attack_p_6': 7.55, 'attack_p_7': 7.34, 'attack_p_8': 7.34, 'skill_1': 7.77, 'skill_2': 7.92, 'skill_3': 8.33, 'skill_4': 8.33, 'skill_5': 8.16, 'skill2_1': 8.08, 'skill2_2': 8.08, 'skill2_3': 8.08, 'skill2_4': 7.69, 'skill2_5': 8.98, 'skill2_6': 8.89, 'skill2_7': 8.42, 'skill2_8': 8.16, 'skill2_9': 7.62, 'ult_1': 7.0, 'ult_2': 7.07, 'ult_3': 6.86, 'ult_4': 6.93, 'ult_5': 6.67, 'ult_6': 6.6, 'ult_7': 6.93, 'ult_8': 7.14, 'skill_w_1': 7.27, 'skill_w_2': 7.77, 'skill_w_3': 7.14, 'skill_w_4': 7.77, 'skill_w_5': 8.33, 'skill_w_6': 8.33, 'skill_w_7': 8.08, 'ult_exit_1': 6.0, 'ult_exit_2': 6.0, 'ult_back_1': 7.29, 'ult_back_3': 7.29, 'hit_1': 7.69, 'hit_2': 7.77, 'dead_1': 7.08, 'dead_2': 8.0, 'dead_3': 7.48, 'dead_5': 7.84, 'dead_6': 7.69, 'dead_7': 7.46, 'dead_8': 7.81, 'dead_9': 6.97, 'dead_10': 7.2}
ZOOM = {'run_1': 8.91, 'run_2': 8.57, 'run_3': 8.82, 'run_4': 8.7, 'run_5': 8.82, 'run_6': 9.08, 'attack_1': 8.37, 'attack_2': 9.44, 'attack_3': 9.05, 'attack_4': 8.71, 'attack_5': 8.79, 'attack_6': 9.15, 'attack_p_1': 9.74, 'attack_p_2': 9.44, 'attack_p_3': 9.63, 'attack_p_4': 9.63, 'attack_p_5': 9.35, 'attack_p_6': 8.73, 'attack_p_7': 8.49, 'skill_1': 8.82, 'skill_2': 9.36, 'skill_3': 9.27, 'skill2_1': 8.71, 'skill2_2': 8.71, 'skill2_3': 8.29, 'skill2_4': 9.68, 'skill2_5': 9.58, 'skill2_6': 9.08, 'skill2_7': 8.8, 'skill2_8': 8.22, 'ult_1': 7.73, 'ult_2': 7.58, 'ult_3': 7.29, 'ult_4': 7.73, 'skill_w_1': 8.15, 'skill_w_2': 8.71, 'skill_w_3': 8.0, 'skill_w_4': 8.71, 'skill_w_5': 9.34, 'skill_w_6': 9.34, 'skill_w_7': 9.05, 'ult_exit_1': 6.85, 'ult_back_1': 8.14, 'hit_1': 8.76, 'dead_1': 7.95, 'dead_2': 8.98, 'dead_3': 8.4, 'dead_4': 8.8, 'dead_5': 8.63, 'dead_6': 8.38, 'dead_7': 8.77, 'dead_8': 7.83, 'dead_9': 8.08}
FRAME_ZOOM = {'run_1': 8.91, 'run_2': 8.57, 'run_3': 8.65, 'run_4': 8.99, 'run_5': 8.82, 'run_6': 8.57, 'run_7': 8.82, 'run_8': 9.08, 'attack_1': 8.37, 'attack_2': 9.44, 'attack_3': 9.05, 'attack_4': 8.37, 'attack_5': 9.05, 'attack_6': 8.53, 'attack_7': 9.05, 'attack_8': 9.15, 'attack_p_1': 9.74, 'attack_p_2': 9.44, 'attack_p_3': 9.63, 'attack_p_4': 9.63, 'attack_p_5': 9.35, 'attack_p_6': 8.73, 'attack_p_7': 8.49, 'attack_p_8': 8.49, 'skill_1': 8.73, 'skill_2': 8.9, 'skill_3': 9.36, 'skill_4': 9.36, 'skill_5': 9.17, 'skill2_1': 8.71, 'skill2_2': 8.71, 'skill2_3': 8.71, 'skill2_4': 8.29, 'skill2_5': 9.68, 'skill2_6': 9.58, 'skill2_7': 9.08, 'skill2_8': 8.8, 'skill2_9': 8.22, 'ult_1': 7.7, 'ult_2': 7.77, 'ult_3': 7.54, 'ult_4': 7.62, 'ult_5': 7.33, 'ult_6': 7.26, 'ult_7': 7.62, 'ult_8': 7.85, 'skill_w_1': 8.15, 'skill_w_2': 8.71, 'skill_w_3': 8.0, 'skill_w_4': 8.71, 'skill_w_5': 9.34, 'skill_w_6': 9.34, 'skill_w_7': 9.05, 'ult_exit_1': 6.85, 'ult_exit_2': 6.85, 'ult_back_1': 8.14, 'ult_back_3': 8.14, 'hit_1': 8.71, 'hit_2': 8.8, 'dead_1': 7.95, 'dead_2': 8.98, 'dead_3': 8.4, 'dead_5': 8.8, 'dead_6': 8.63, 'dead_7': 8.38, 'dead_8': 8.77, 'dead_9': 7.83, 'dead_10': 8.08}
ZOOMS = np.arange(0.75 * PK.SQ, 1.25 * PK.SQ + 0.01, 0.1)   # the zooms measure() searches, round the pack's SQ
PIVOT = 56                      # the design's column on the old idle_base's pivot (overlap peak 0.70)

# casts_rengar_hd's reading on her design
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


# the colours of her body: every colour of the old run and idle_base (no effects in them)
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


def figure(a):
    """The drawing's mask: Codex's raw generations come on a transparent ground, the figure opaque inside a faint halo:
    alpha 128 and up (casts_rengar_hd.figure keys a white ground)."""
    return a[..., 3] >= 128


def frame_masks(s):
    """(sheet picture, [(frame, mask)]) of a sheet."""
    a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
    return a, CS.cells(s, figure(a))


def at_zoom(a, m, zoom):
    """The drawing a[m] read at `zoom` px a square, cropped."""
    ys, xs = np.nonzero(m)
    gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
    sq = CS.sample(a, m, round(gh / zoom), round(gw / zoom))
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
    """Her size: the teal of her skirt and scarf, its largest piece (joined across one-square gaps) - her
    long hair flows with every move, her skin runs on into her arms and legs."""
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = op & (g >= 150) & (b >= 140) & (r <= 120) & (g - r >= 60)
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


def fits(templates):
    """{"<tag>_<frame>": (zoom, overlap)}: each drawn frame's zoom from its fit over its template's pale figure - Codex
    drew every frame on its template (templates/<sheet>.png of PK's pack), the old frame shown pale at SQ px a square:
    the drawing's mask, scaled by s and slid anywhere (FFT correlation, at a third of the size), overlaps the pale
    figure best at one s, and the drawing's px a square is SQ / s. A raised blowgun, a swung trident or flowing hair
    move the drawing's box and area, hardly this."""
    def small(m):
        hh, ww = m.shape[0] // 3 * 3, m.shape[1] // 3 * 3
        return m[:hh, :ww].reshape(hh // 3, 3, ww // 3, 3).mean((1, 3)) >= 0.5

    def crop(m):
        ys, xs = np.nonzero(m)
        return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        t = np.asarray(Image.open(CS.lp(os.path.join(templates, s["name"] + ".png"))).convert("RGB")).astype(int)
        pale = (t.min(-1) >= 165) & (t.min(-1) < 250)      # the faded figure: its colours * 0.35 + 255 * 0.65
        cw = 1536 // s["cells"]
        sq = PK.SQ_OF.get(s["tag"], PK.SQ)
        for c, (k, m) in enumerate(ms):
            T = pale.copy()
            T[:, :c * cw] = False
            T[:, (c + 1) * cw:] = False
            T, M = crop(small(T)).astype(float), crop(small(m))
            best = (0.0, 1.0)
            for sc in np.arange(0.78, 1.30, 0.01):
                cs = np.asarray(Image.fromarray(M.astype(np.uint8) * 255).resize(
                    (max(1, round(M.shape[1] * sc)), max(1, round(M.shape[0] * sc))), Image.NEAREST)) > 127
                inter = fftconvolve(T, cs[::-1, ::-1].astype(float), mode="full").max()
                iou = inter / (T.sum() + cs.sum() - inter)
                if iou > best[0]:
                    best = (iou, sc)
            out[f"{s['tag']}_{k}"] = (round(float(sq / best[1]), 2), round(float(best[0]), 2))
            print(s["name"], k, *out[f"{s['tag']}_{k}"], flush=True)
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
    ap.add_argument("--fits", help="each frame's zoom from its fit over its template: the pack's templates folder")
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
    if a.fits:
        fits(a.fits)
        return
    fr = placed()
    print("frames", len(fr))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    for t in TAGS:
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        if not names:
            continue                                    # (every frame of the tag is the design)
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
