#!/usr/bin/env python3
"""Lissandra's actions from Codex's whole-frame redraw (assets/source/lissandra/hd/casts: tools/art/pack_lissandra_actions.py's pack,
delivered 2026-11-03, Documents/Codex/2026-11-03/new-chat-3/outputs/b2_actions_full.zip: lissandra-actions) read onto the
design's squares - tools/art/casts_viego_hd.py's reading (casts_rengar_hd's keying, cells and palette sampling), pointed
at her design (the user, 2026-11-03: 「继续加四个 魔腾 凯南 剑魔 丽桑卓」「另外四个英雄codex全部交付了 你做到完美后喊我review」).

hd/casts holds Codex's 25 sheets (each its chosen raw generation byte for byte, redos included), drawn on a
near-white ground: casts_rengar_hd.figure keys it off. Each frame's zoom (FRAME_ZOOM, --fit) reads her STAND rows tall,
the top of her crown to her hem as the design, and of the zooms that do, the one nearest to what her CROWN gives (see
FRAME_ZOOM), so her body and her crown are the design's size in every frame; HEAD_FROM gives two frames another's head.
The old frame's body (its box places the new frame) leaves out what the old sheet baked in, the ice shards and frost by
her hands: only what lies within two pixels of the dark outline counts (OLD_BODY). Each frame is then placed where the
old body stood: its box's middle on the old box's middle and its bottom on the old box's bottom, from the pivot, on the
design's grid. She stands on the ground (HOVER 0); the design's pivot column (PIVOT) is where the design lies best over
the old idle_base.

    python tools/art/casts_lissandra_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_lissandra_hd.py --fit             # FRAME_ZOOM again, with each placed frame's height and crown
    python tools/art/casts_lissandra_hd.py --heights         # each frame's zoom from its height against the old frame's
    python tools/art/casts_lissandra_hd.py --heads           # each placed frame's head against the design's
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
import pack_lissandra_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "lissandra", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 42          # rows over her 1x 42 (design_lissandra_hd: the top of her crown to her soles)
HOVER = 0                       # (she stands on the ground: her old idle_base's soles on its soles' line)
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1 + int(round(HOVER * PPU))   # the soles' line, under him
HEAD = (3, 27, 0, 47)         # the design's head: rows 3-26 (the top of her crown to her chin), its sides
# px of Codex's drawing a design square (FRAME_ZOOM, fit()): each frame read STAND rows tall - the top of her crown to
# her hem, the design's 76 rows and every old frame's 42 px - and of the zooms that do (round(the box's height / zoom) =
# STAND), the nearest to the one her CROWN gives (crown_px: the widest run in the top 18 % of the drawing over the
# design's 47 squares; CROWN_SKIP, death 3-6: her raised hands reach the crown's rows - the height alone), so the crown
# reads 46-48 squares where the height leaves it a choice. History: the median of height, head and area (the other
# heroes' way) made her pulse - the old glide sinks in frames 3-4 and the old death in 5-6, Codex drew her full height
# there, and the height matched to the OLD frame shrank her a size (the user: 「丽桑卓有模型一大一小的问题」); then the crown
# alone (2026-11-03 to 11-16), but Codex drew the glide's 7-8 shorter under a wider crown (668 px tall against 687-691,
# the crown 432 px against 424-428): matched by the crown they read 73 rows against 75-77, the body and the gown a size
# smaller, and other frames 74-78 (the user, 2026-11-16: 「丽桑卓还有模型一大一小的问题 不光是失去了像素」). A sheet's ZOOM
# is the crown rule's mean (a fallback: every drawn frame has its FRAME_ZOOM)
STAND = 76                      # design rows from the top of her crown to her hem: the design's, her 1x 42 x PPU
CROWN_SKIP = ('dead_3', 'dead_4', 'dead_5', 'dead_6')
ZOOM = {'run_1': 9.1, 'run_2': 9.02, 'run_3': 9.19, 'attack_1': 9.0, 'attack_2': 8.99, 'attack_3': 9.04, 'skill_1': 9.22, 'skill_2': 9.06, 'skill_3': 9.02, 'skill2_1': 9.04, 'skill2_2': 9.0, 'skill2_3': 8.98, 'skill2_e_1': 9.06, 'skill2_e_2': 8.99, 'skill2_e_3': 9.04, 'ult_1': 8.99, 'ult_2': 8.9, 'ult_3': 8.96, 'ult_self_1': 8.98, 'ult_self_2': 8.91, 'hit_1': 9.0, 'dead_1': 9.03, 'dead_2': 9.09, 'dead_3': 9.04, 'dead_4': 9.21}
FRAME_ZOOM = {'run_1': 9.09, 'run_2': 9.09, 'run_3': 9.03, 'run_6': 9.04, 'run_7': 8.84, 'run_8': 8.84, 'attack_2': 9.02, 'attack_3': 8.98, 'attack_4': 8.99, 'attack_5': 8.98, 'attack_6': 9.03, 'skill_1': 9.14, 'skill_2': 9.14, 'skill_3': 9.06, 'skill_4': 9.06, 'skill_5': 9.02, 'skill_6': 9.02, 'skill2_1': 9.01, 'skill2_2': 9.01, 'skill2_3': 9.08, 'skill2_4': 9.08, 'skill2_5': 8.98, 'skill2_e_1': 9.18, 'skill2_e_2': 9.18, 'skill2_e_3': 9.0, 'skill2_e_5': 8.98, 'skill2_e_6': 9.01, 'ult_1': 9.0, 'ult_2': 8.98, 'ult_3': 8.94, 'ult_4': 8.94, 'ult_5': 8.96, 'ult_self_1': 8.96, 'ult_self_2': 8.97, 'ult_self_4': 8.91, 'hit_1': 8.93, 'dead_1': 9.04, 'dead_2': 9.14, 'dead_3': 9.08, 'dead_4': 9.09, 'dead_5': 9.04, 'dead_6': 9.04, 'dead_7': 9.05}
ZOOMS = np.arange(4.5, 9.01, 0.1)                       # the zooms the head is searched at (6-px templates)
PIVOT = 25                      # the design's column on the old idle_base's pivot (overlap peak 0.84)
# frames that hold another's drawing: Codex's death froze her in ice pillars at frame 6 and drew 7-8 in her plain gown
# again (the old death ends frozen, the pillars taller each frame): 7-8 hold frame 6, so the death ends frozen
HELD = {"dead_7": "dead_6", "dead_8": "dead_6"}
# frames whose head is another frame's (head_from: the crown and, under its brim, the visor and the face, laid where
# the design's crown fits each): Codex drew the glide's 7-8 with a black blot round the face (its "eyes in the
# crown's shadow") and a crown two squares wider at her height; tools/art/thin_outline.py ate into the blot, open to
# the ground beside the face, and left holes and specks there (the user, 2026-11-16: 「丽桑卓头那里失去像素了」
# 「丽桑卓也有莫名其妙阴影的部分」). Glide 6 is drawn the same way under the brim (the face as low), clean: frames 6-8 share it
HEAD_FROM = {"run_7": "run_6", "run_8": "run_6"}
CROWN_ROWS = 14                 # design rows 0-13: the crown down to the brim's bottom outline (head_from takes all of it)
# head_from's boxes under the brim (design rows and columns, from the fitted crown): the visor, the face and its dark
# right side; the hair on her left and the hand by her chin stay the frame's own
HEAD_BOXES = ((14, 22, 21, 38), (22, 26, 21, 33))

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


def frame_masks(s):
    """(sheet picture, [(frame, mask)]) of a sheet."""
    a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
    return a, CS.cells(s, CS.figure(a))


def at_zoom(a, m, zoom):
    """The drawing a[m] read at `zoom` px a square, cropped."""
    ys, xs = np.nonzero(m)
    gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
    sq = CS.sample(a, m, round(gh / zoom), round(gw / zoom))
    yy, xx = np.nonzero(sq[..., 3] > 0)
    return sq[yy.min():yy.max() + 1, xx.min():xx.max() + 1]


def crown_px(m):
    """Her crown's width in the mask's own units: the widest run in the top 18 % of its rows."""
    ys = np.nonzero(m.any(1))[0]
    best = 0
    for row in m[ys.min():ys.min() + int(0.18 * (ys.max() + 1 - ys.min()))]:
        lbl, n = ndimage.label(row)
        if n:
            best = max(best, int(ndimage.sum(row, lbl, range(1, n + 1)).max()))
    return best


CROWN_W = crown_px(D0[..., 3] > 0)      # the design's crown: 47 squares


def fit(verbose=False):
    """{"<tag>_<frame>": zoom}: FRAME_ZOOM's rule - each drawn frame read STAND rows tall (round(its box's height /
    zoom) = STAND), and of those zooms the nearest to the one its crown gives (crown_px over CROWN_W); CROWN_SKIP by
    the height alone. verbose: each frame's zoom with the rows and the crown squares it reads, against the old table."""
    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        for k, m in ms:
            n = f"{s['tag']}_{k}"
            ys = np.nonzero(m.any(1))[0]
            gh = ys.max() + 1 - ys.min()
            lo, hi = gh / (STAND + 0.4), gh / (STAND - 0.4)
            z = gh / STAND if n in CROWN_SKIP else min(max(crown_px(m) / CROWN_W, lo), hi)
            out[n] = round(float(z), 2)
            if round(gh / out[n]) != STAND:
                sys.exit(f"{n}: {out[n]} reads {round(gh / out[n])} rows")
            if verbose:
                sq = body_only(at_zoom(a, m, out[n]))
                rows = np.nonzero(sq[..., 3].any(1))[0]
                print(f"{n}: {out[n]} ({FRAME_ZOOM.get(n)} before) - {rows.max() + 1 - rows.min()} rows, crown "
                      f"{crown_px(sq[..., 3] > 0)}", flush=True)
    return out


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
    for n, src in HELD.items():
        out[n] = out[src]
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
    """Her head's size: the pale blue of her face, its largest piece (joined across one-square gaps) - her
    hair and ice are more cyan, her gown darker."""
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = op & (b >= 200) & (r >= 120) & (g >= 140) & (b - r >= 30) & (b - r <= 110) & (g - r <= 60)
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
    for n, src in HEAD_FROM.items():
        out[n] = head_from(*out[n], out[src][0])
    for n, (pic, x, y) in out.items():
        out[n] = (body_only(pic), x, y)
    return out


def crown_fit(pic, search=6):
    """(dy, dx): where the design's row 0 and column 0 lie in the picture when its crown (design rows 0 to
    CROWN_ROWS - 1) is laid best over the picture's - the most overlap of the two silhouettes (intersection over union)
    and, half as much, of squares alike in colour (RGB distance under 40)."""
    d = D0[:CROWN_ROWS]
    dop = d[..., 3] > 0
    H, W = pic.shape[:2]
    top = int(np.nonzero(pic[..., 3].any(1))[0].min())
    best = None
    for dy in range(top - search, top + search + 1):
        for dx in range(-search - 10, W - d.shape[1] + search + 11):
            can = np.zeros(d.shape, np.uint8)
            y0, y1, x0, x1 = max(0, dy), min(H, dy + CROWN_ROWS), max(0, dx), min(W, dx + d.shape[1])
            if y1 <= y0 or x1 <= x0:
                continue
            can[y0 - dy:y1 - dy, x0 - dx:x1 - dx] = pic[y0:y1, x0:x1]
            op = can[..., 3] > 0
            alike = op & dop & (np.abs(can[..., :3].astype(int) - d[..., :3].astype(int)).sum(-1) < 40)
            sc = (op & dop).sum() / (op | dop).sum() + 0.5 * alike.sum() / dop.sum()
            if best is None or sc > best[0]:
                best = (sc, dy, dx)
    return best[1], best[2]


def head_from(pic, x, y, src, pad=4):
    """(picture, x, y): the frame with src's head - src's rows down to the crown's last row (CROWN_ROWS - 1 in the
    design) over the whole width, and HEAD_BOXES under the brim - laid where the design's crown fits the frame
    (crown_fit on both); the frame's own rows above and in the crown's go first (a taller crown tip, a wider brim)."""
    sy, sx = crown_fit(src)
    fy, fx = crown_fit(pic)
    oy, ox = fy - sy + pad, fx - sx + pad
    out = np.zeros((pic.shape[0] + 2 * pad, pic.shape[1] + 2 * pad, 4), np.uint8)
    out[pad:pad + pic.shape[0], pad:pad + pic.shape[1]] = pic
    last = sy + CROWN_ROWS                          # src rows above this are the crown
    out[:max(0, last + oy)] = 0
    ys, xs = np.nonzero(src[:last, :, 3] > 0)
    out[ys + oy, xs + ox] = src[ys, xs]
    for r0, r1, c0, c1 in HEAD_BOXES:
        for r in range(r0 + sy, r1 + sy):
            for c in range(c0 + sx, c1 + sx):
                if 0 <= r < src.shape[0] and 0 <= c < src.shape[1]:
                    out[r + oy, c + ox] = src[r, c]
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1], x - pad + int(xs.min()), y - pad + int(ys.min())


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
    ap.add_argument("--fit", action="store_true", help="FRAME_ZOOM by its rule (fit), each frame's rows and crown")
    a = ap.parse_args()
    if a.fit:
        print("FRAME_ZOOM =", fit(verbose=True))
        fr = placed()
        for n in sorted(fr, key=lambda n: (TAGS.index(n.rsplit("_", 1)[0]), int(n.rsplit("_", 1)[1]))):
            m = fr[n][0][..., 3] > 0
            rows = np.nonzero(m.any(1))[0]
            print(f"placed {n}: {rows.max() + 1 - rows.min()} rows, crown {crown_px(m)}")
        return
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
