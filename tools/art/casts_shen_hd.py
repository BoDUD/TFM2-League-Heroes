#!/usr/bin/env python3
"""Shen's actions from Codex's whole-frame redraw (assets/source/shen/hd/casts: tools/art/pack_shen_actions.py's pack,
delivered 2026-11-09, Documents/Codex/2026-11-09/new-chat/outputs/shen_actions_done.zip: shen-actions) read onto the
design's squares - tools/art/casts_viego_hd.py's reading (casts_rengar_hd's cells and palette sampling), pointed at his
design (the user, 2026-11-10: 「慎也需要重做」「1.8」「codex交付了 有问题的地方你帮忙修复 做到完美后喊我review」).

hd/casts holds Codex's 23 sheets, each the raw generation its export came from byte for byte (raw/<sheet>.png or its
--repair / --head / --matched redraw, as generation-records.json selects; the delivery's root PNGs are Codex's
normalized copies, scaled by its own head marks and snapped to the palette, and are not read; a later delivery drawn by
a script once the image tool's quota ran out is not read either), drawn on a transparent ground: figure() keeps alpha
128 and up. Each frame's zoom is the one its fit over its template's pale figure gives (--fits DIR, DIR the pack's
templates, pack_shen_actions.py --out: Codex drew every frame on the old frame shown pale at SQ px a square; the drawing
scaled until it overlaps the pale figure best); where it overlaps under 0.65 (another pose), the median of that, the
zoom its HEIGHT gives (--heights: the drawing's box over the old frame's body), the one his size part gives against the
design's (_skin) and the one its area gives (calibrated on the run). The old frame's body leaves out what the old sheet
baked in, (none: his old sheet draws no effects): only what lies within two pixels of the dark outline counts
(OLD_BODY). Each frame is then placed where the old body stood: its box's middle on the old box's middle and its bottom
on the old box's bottom, from the pivot, on the design's grid. He stands on the ground (HOVER 0); the design's pivot
column (PIVOT) is where the design lies best over the old idle_base.

    python tools/art/casts_shen_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_shen_hd.py --fits DIR        # each frame's zoom from its fit over its template
    python tools/art/casts_shen_hd.py --heights         # each frame's zoom from its height against the old frame's
    python tools/art/casts_shen_hd.py --heads           # each placed frame's head against the design's
"""
import argparse
import json
import math
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
import pack_shen_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "shen", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 42          # rows over his 1x 42 (design_shen_hd: the top of the sword hilt on his back to his soles)
HOVER = 0                       # (he stands on the ground: his old idle_base's soles on its soles' line)
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1 + int(round(HOVER * PPU))   # the soles' line, under him
HEAD = (7, 29, 24, 46)          # the design's head: rows 7-28 (the top of his hood to his chin), cols 24-45
# px of Codex's drawing a design square: each frame's from its fit over its template's pale figure (fits(): the
# drawing scaled until it overlaps the old frame Codex drew it on best); where it overlaps under 0.65 (another pose)
# the median of that fit, the zoom its height gives against the old body's (heights()), the one its size part gives
# against the design's (_skin) and the one its area gives against the old body's (calibrated on the run) - the
# height and the area alone moved with a raised staff, a stretched mouth or flowing hair (the user, on Sett:
# 「瑟提感觉模型会一大一小？」); a sheet's ZOOM is its frames' mean. 2026-11-10, under 0.65: dead_6
# then (the user, 2026-11-10: 「有问题的地方你帮忙修复」, 「千万别出现模型一大一小的问题」, 「还有模型不要变大变小 这个问题一定要
# 注意」): twelve frames Codex drew with the head off the design's on a body of the right size - E's four and the
# death's dead_4-8 10-30 % over, the swing's fifth and the R channel's second (it pulsed as the channel looped) 10 %
# over, the swing's sixth 8 % under - by the hilt gem, his boots and gloves against the run's at the fit's zoom and the
# heads counted square by square: HEAD_RESCALE rescales the head alone (rescale_head()), the body read at the fit's zoom
# x its factor. The fit's zooms: FIT_ZOOM
FIT_ZOOM = {'run_1': 10.0, 'run_2': 9.8, 'run_3': 10.1, 'run_4': 10.0, 'run_5': 10.0, 'run_6': 10.1, 'run_7': 10.0, 'run_8': 10.0, 'attack_1': 8.0, 'attack_2': 8.08, 'attack_3': 8.0, 'attack_4': 8.0, 'attack_5': 8.0, 'attack_6': 8.16, 'skill_2': 9.9, 'skill2_1': 9.71, 'skill2_2': 10.0, 'skill2_3': 10.0, 'skill2_4': 10.0, 'ult_2': 10.0, 'ult_loop_2': 9.62, 'hit_1': 10.1, 'dead_1': 10.1, 'dead_2': 10.0, 'dead_3': 9.71, 'dead_4': 9.43, 'dead_5': 9.01, 'dead_6': 9.4, 'dead_7': 9.62, 'dead_8': 10.1}
ZOOM = {'run_1': 9.9, 'run_2': 10.05, 'run_3': 10.05, 'run_4': 10.0, 'attack_1': 8.04, 'attack_2': 8.0, 'attack_3': 8.0, 'attack_4': 8.16, 'skill_1': 9.9, 'skill2_1': 9.71, 'skill2_2': 10.0, 'skill2_3': 10.0, 'skill2_4': 10.8, 'ult_1': 10.0, 'ult_loop_1': 9.62, 'hit_1': 10.1, 'dead_1': 10.1, 'dead_2': 10.0, 'dead_3': 9.8, 'dead_4': 9.46, 'dead_5': 10.15, 'dead_6': 9.62, 'dead_7': 10.1}
FRAME_ZOOM = {'run_1': 10.0, 'run_2': 9.8, 'run_3': 10.1, 'run_4': 10.0, 'run_5': 10.0, 'run_6': 10.1, 'run_7': 10.0, 'run_8': 10.0, 'attack_1': 8.0, 'attack_2': 8.08, 'attack_3': 8.0, 'attack_4': 8.0, 'attack_5': 8.0, 'attack_6': 8.16, 'skill_2': 9.9, 'skill2_1': 9.71, 'skill2_2': 10.0, 'skill2_3': 10.0, 'skill2_4': 10.8, 'ult_2': 10.0, 'ult_loop_2': 9.62, 'hit_1': 10.1, 'dead_1': 10.1, 'dead_2': 10.0, 'dead_3': 9.71, 'dead_4': 9.9, 'dead_5': 9.46, 'dead_6': 10.15, 'dead_7': 9.62, 'dead_8': 10.1}
# the frames whose head alone is rescaled (shrunk; attack_6's grown): (cx, cy, rx, ry, degrees, px, py) of the
# ellipse round the head and of the pivot (where his neck holds it) in the sheet's raw px, then the body's factor over
# the fit's zoom (FRAME_ZOOM is fit x it) and the head's: the head ends the size the zoom fit x that factor reads it
# at - the design's (by eye on crops round the eyes at one scale); the body's factor from the hilt gem, his boots and
# gloves against the run's
HEAD_RESCALE = {
    "skill2_1": (876, 472, 142, 134, 0, 840, 590, 1.0, 1.25),
    "skill2_2": (918, 428, 112, 124, 0, 862, 512, 1.0, 1.18),
    "skill2_3": (862, 541, 118, 126, 0, 770, 590, 1.0, 1.12),
    "skill2_4": (933, 444, 130, 144, 0, 830, 520, 1.08, 1.24),
    "dead_4": (1167, 367, 119, 142, 0, 1130, 480, 1.05, 1.28),
    "dead_5": (850, 502, 119, 152, 0, 790, 600, 1.05, 1.3),
    "dead_6": (872, 595, 119, 139, 0, 800, 660, 1.08, 1.28),
    "dead_7": (784, 580, 129, 139, 0, 720, 680, 1.0, 1.25),
    "dead_8": (1292, 789, 129, 119, 0, 1190, 810, 1.0, 1.1),
    "attack_5": (1120, 375, 100, 110, 0, 1115, 465, 1.0, 1.1),
    "attack_6": (776, 420, 92, 105, 0, 778, 500, 1.0, 0.92),
    "ult_loop_2": (735, 245, 125, 130, 0, 745, 370, 1.0, 1.1),
}
ZOOMS = np.arange(0.75 * PK.SQ, 1.25 * PK.SQ + 0.01, 0.1)   # the zooms measure() searches, round the pack's SQ
PIVOT = 29                      # the design's column on the old idle_base's pivot (overlap peak 0.87)

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


# ------------------------------------------------------------------------------------------- the head-only rescale
KEPT_MIN = 400      # raw px: a hilt or gem piece at least this big stays where it is
KEEP_EDGE = 5       # raw px: the dark outline round the kept hilt and gem stays with them
FOREIGN = 0.5       # a light-grey piece more than this share outside the ellipse is no part of the head (blade, trim)
MARGIN = 160        # raw px round the ellipse the light-grey pieces are followed out to
RAYS = 16           # directions a pixel the head leaves looks along, out of the head's place
BODY_VOTE = 0.6     # the share of them that must meet the figure for it to take the body's colours (else the ground)
ERODE = 4           # raw px: those colours come from this far inside the body (not its dark outline)
SPECK = 150         # raw px: a loose piece of the figure this small by the head's place afterwards is dropped


def disk(r):
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return xx * xx + yy * yy <= r * r


def ellipse(shape, cx, cy, rx, ry, deg):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    u = (xx - cx) * c + (yy - cy) * s
    v = -(xx - cx) * s + (yy - cy) * c
    return (u / rx) ** 2 + (v / ry) ** 2 <= 1


def kept(a, m):
    """The hilt and the gem: pieces (8-connected) of leather browns or the gem's light blues at least KEPT_MIN px (not
    the eye slit's brown shading), with the dark outline round them."""
    rgb = a[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    brown = (r > g) & (g > b) & (r - b >= 25) & (r <= 140) & (rgb.max(-1) >= 40)
    blue = (b >= 150) & (g >= 100) & (b > r + 40) & (g > r + 10)
    k = (brown | blue) & m
    lbl, n = ndimage.label(k, structure=np.ones((3, 3)))
    sz = ndimage.sum(k, lbl, range(1, n + 1))
    k = np.isin(lbl, [i + 1 for i in range(n) if sz[i] >= KEPT_MIN])
    return k | (m & (rgb.max(-1) < 70) & ndimage.binary_dilation(k, structure=disk(1), iterations=KEEP_EDGE))


def head_region(a, m, inside, kp):
    """The head: the figure inside the ellipse, less the kept hilt and gem and less the light-grey pieces (4-connected)
    lying mostly outside it - the blade over his back, the armour's trims - which stay where they are; his horns and
    mask lie inside and go with the head."""
    rgb = a[..., :3].astype(int)
    ys, xs = np.nonzero(inside)
    w = (slice(max(0, ys.min() - MARGIN), ys.max() + 1 + MARGIN),
         slice(max(0, xs.min() - MARGIN), xs.max() + 1 + MARGIN))
    c = rgb[w]
    light = m[w] & (c.min(-1) >= 110) & (c.max(-1) - c.min(-1) <= 60)
    lbl, n = ndimage.label(light)
    tot = ndimage.sum(light, lbl, range(1, n + 1))
    ins = ndimage.sum(light & inside[w], lbl, range(1, n + 1))
    foreign = np.zeros_like(m)
    foreign[w] = np.isin(lbl, [i + 1 for i in range(n) if ins[i] > 0 and tot[i] - ins[i] > FOREIGN * tot[i]])
    return m & inside & ~kp & ~foreign


def enclosed(head, m):
    """For each pixel of `head`: the share of RAYS rays from it that, once out of the head's place, meet the figure
    (the body behind the head) rather than the ground."""
    ys, xs = np.nonzero(head)
    votes = np.zeros(len(ys))
    H, W = head.shape
    for k in range(RAYS):
        dy, dx = math.sin(2 * math.pi * k / RAYS), math.cos(2 * math.pi * k / RAYS)
        done = np.zeros(len(ys), bool)
        hit = np.zeros(len(ys), bool)
        for t in range(1, int(np.hypot(H, W)) + 1):
            yy, xx = np.rint(ys + t * dy).astype(int), np.rint(xs + t * dx).astype(int)
            done |= (yy < 0) | (yy >= H) | (xx < 0) | (xx >= W)
            live = np.nonzero(~done)[0]
            if not len(live):
                break
            yl, xl = yy[live], xx[live]
            leave = ~head[yl, xl]
            hit[live[leave]] = m[yl[leave], xl[leave]]
            done[live[leave]] = True
        votes += hit
    out = np.zeros(head.shape)
    out[ys, xs] = votes / RAYS
    return out


def rescale_head(a, m, e, s):
    """(picture, mask) of a raw frame with its head - head_region() inside ellipse e = (cx, cy, rx, ry, deg, px, py) -
    scaled by s about the pivot (px, py). Where the head no longer reaches: the body's colours (from ERODE px inside it,
    nearest first) where the body lies round that place on most sides (enclosed()), the ground elsewhere; loose specks
    by it dropped."""
    cx, cy, rx, ry, deg, px, py = e
    head = head_region(a, m, ellipse(m.shape, cx, cy, rx, ry, deg), kept(a, m))
    ys, xs = np.nonzero(head)
    pad = ERODE + 8
    win = (slice(max(0, ys.min() - pad), ys.max() + 1 + pad), slice(max(0, xs.min() - pad), xs.max() + 1 + pad))
    hw = head[win]
    body = m[win] & ~hw
    fill = hw & (enclosed(hw, m[win]) >= BODY_VOTE)
    src = ndimage.binary_erosion(body, structure=disk(ERODE))
    iy, ix = ndimage.distance_transform_edt(~(src if src.any() else body), return_distances=False, return_indices=True)
    a2, m2 = a.copy(), m.copy()
    sub, mw = a2[win], m2[win]
    sub[fill] = a[win][iy[fill], ix[fill]]
    mw[hw & ~fill] = False
    ty, tx = np.mgrid[int(math.floor(py + s * (ys.min() - py))):int(math.ceil(py + s * (ys.max() - py))) + 1,
                      int(math.floor(px + s * (xs.min() - px))):int(math.ceil(px + s * (xs.max() - px))) + 1]
    sy, sx = np.rint(py + (ty - py) / s).astype(int), np.rint(px + (tx - px) / s).astype(int)
    ok = (sy >= 0) & (sy < m.shape[0]) & (sx >= 0) & (sx < m.shape[1]) & (ty >= 0) & (ty < m.shape[0]) & \
        (tx >= 0) & (tx < m.shape[1])
    ok[ok] = head[sy[ok], sx[ok]]
    a2[ty[ok], tx[ok]] = a[sy[ok], sx[ok]]
    m2[ty[ok], tx[ok]] = True
    lbl, n = ndimage.label(m2, structure=np.ones((3, 3)))
    sz = ndimage.sum(m2, lbl, range(1, n + 1))
    near = np.unique(lbl[ndimage.binary_dilation(head, structure=disk(1), iterations=pad)])
    m2 &= ~np.isin(lbl, [i for i in near if i > 0 and sz[i - 1] < SPECK])
    return a2, m2


def read_all():
    """{"<tag>_<frame>": (squares, the old box's middle and bottom from the pivot in design squares, the zoom)}; the
    HEAD_RESCALE frames with their heads rescaled first."""
    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        for k, m in ms:
            L, T, R, B = old_box(s["tag"], k)
            n = f"{s['tag']}_{k}"
            z = FRAME_ZOOM.get(n, ZOOM[s["name"]])
            b, mb = (a, m) if n not in HEAD_RESCALE else rescale_head(a, m, HEAD_RESCALE[n][:7],
                                                                     HEAD_RESCALE[n][7] / HEAD_RESCALE[n][8])
            out[n] = (at_zoom(b, mb, z), (L + R) / 2 * PPU, B * PPU, z)
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
    """His size: the tan of his bare arms, its largest piece (joined across one-square gaps) - the
    orange of his eyes is redder, the boots' brown darker."""
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = op & (r >= 160) & (g >= 90) & (g <= 175) & (b >= 60) & (b <= 120) & (r - b >= 80)
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
    for n, (back, front) in LEG_SWAP.items():
        pic, x, y = out[n]
        out[n] = (swap_legs(pic, back, front), x, y)
    return out


# run frame 5 with the two legs' shades exchanged: Codex drew it like frame 1 - the darker (far) leg kicked back,
# the lighter (near) one planted - where the pack asks for the near leg kicked back (pack_shen_actions RUN_LEGS: the
# near leg carries him in frames 1-4, the far leg in 5-8) - so frames 1 and 5 showed the same leg stepping (the user, on
# Blitzcrank: 「走路没有换腿」); frames 2 / 6, 3 / 7 and 4 / 8 already take turns. Each entry: (row, col, squares) of the
# back piece's first square and of the front piece's in the placed picture (the squares as read: a reading that moves
# them fails here instead of shading the wrong piece); a piece is the 4-connected run of LEG_COLOURS squares round it in
# the lowest LEG_ROWS rows of the figure
LEG_SWAP = {"run_5": ((50, 16, 68), (60, 28, 64))}
LEG_ROWS = 22
LEG_COLOURS = lambda r, g, b: (np.maximum(np.maximum(r, g), b) >= 45) & (((b > g) & (r >= 40)) | ((r > b) & (r - b >= 20) & (r <= 130)))   # his purple trousers and brown boots: not the outline


def swap_legs(pic, back, front):
    """The picture with its two legs' shades exchanged: each of the two pieces' squares takes the colour at the
    same brightness rank among the other piece's squares - each keeps its own light and shade, the back one now the
    lighter (near) leg, the front the darker (far) one."""
    rgb, op = pic[..., :3].astype(int), pic[..., 3] > 0
    m = op & LEG_COLOURS(rgb[..., 0], rgb[..., 1], rgb[..., 2])
    m[:np.nonzero(op.any(1))[0].max() + 1 - LEG_ROWS] = False
    lbl, _ = ndimage.label(m)
    ms = []
    for r, c, size in (back, front):
        piece = lbl == lbl[r, c]
        assert lbl[r, c] and piece.sum() == size, ("swap_legs", r, c, int(piece.sum()), size)
        ms.append(piece)
    lum = rgb @ np.array([299, 587, 114])
    out = pic.copy()
    for a, b in ((ms[0], ms[1]), (ms[1], ms[0])):
        src = pic[b][np.argsort(lum[b], kind="stable")]                     # the other piece's squares, dark to light
        rank = np.argsort(np.argsort(lum[a], kind="stable"), kind="stable")  # each square's rank in its own piece
        out[a] = src[np.round(rank * (len(src) - 1) / max(1, len(rank) - 1)).astype(int)]
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
