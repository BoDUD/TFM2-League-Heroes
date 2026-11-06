#!/usr/bin/env python3
"""Nautilus's actions from Codex's whole-frame redraw (assets/source/nautilus/hd/casts: tools/art/pack_nautilus_actions.py's
pack, delivered 2026-11-06, Documents/Codex/2026-11-05/new-chat/outputs/nautilus-actions, raw/ - the user, 2026-11-06:
「Codex全都交付了 你做到完美后喊我review」) read onto the design's squares - tools/art/casts_khazix_hd.py's reading, pointed at
his design (hd/design.png, 73 x 92, PPU 1.80: 92 rows over his 1x 51).

hd/casts holds Codex's 31 sheets, each its raw generation byte for byte (raw/: not Codex's palette-snapped copies), drawn
on a near-white ground; dead_7's raw came on a grey checkerboard (a fake transparency), keyed off here (CHECKER).
Each frame's zoom is the one its fit over its template's pale figure gives (--fits DIR, DIR the pack's templates,
C:/t/nautilus_actions/templates). Each frame is placed with its bottom on the old body's bottom and its column where
its squares overlap the old body's best (--fits' way at the design's squares: the anchor's chain runs as long as Codex
drew it - skill_4 runs off the sheet - so the box's middle, casts_khazix_hd's, would slide him along it); standing
frames' soles on the soles' row. He stands on the ground (HOVER 0); the design's pivot column (PIVOT) is where the
design lies best over the old idle_base (--pivot).

    python tools/art/casts_nautilus_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_nautilus_hd.py --fits DIR        # each frame's zoom from its fit over its template
    python tools/art/casts_nautilus_hd.py --heights         # each frame's zoom from its height against the old frame's
    python tools/art/casts_nautilus_hd.py --heads           # each placed frame's helmet against the design's
    python tools/art/casts_nautilus_hd.py --pivot           # the design's column on the old idle_base's pivot
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
import pack_nautilus_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "nautilus", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 51          # rows over his 1x 51 (design_nautilus_hd: the top of his anchor to his soles)
HOVER = 0                       # (he stands on the ground: his old idle_base's soles on its soles' line)
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1 + int(round(HOVER * PPU))   # the soles' line, under him
HEAD = (24, 59, 30, 65)        # the design's helmet: rows 24-58 (its dome to its chin), cols 30-64
# px of Codex's drawing a design square: the template's own (pack_nautilus_actions.SQ, SQ_OF) - Codex traced every
# frame over its template's pale figure at the template's squares: the fit over it (--fits) gives the template's square
# within 1 % in 37 of the 38 frames (overlap 0.79-0.98); attack_3's 8.99 (0.68) is the anchor drawn rounder than the
# old frame's at the chain's end - its body lies square on the pale figure at 8
def _sheet_zoom():
    with open(os.path.join(SRC, "sheets.json"), encoding="utf-8") as f:
        return {s_["name"]: PK.SQ_OF.get(s_["tag"], PK.SQ) for s_ in json.load(f)["sheets"]}


ZOOM = _sheet_zoom()
FRAME_ZOOM = {}
ZOOMS = np.arange(4.5, 9.01, 0.1)                       # the zooms the head is searched at (6-px templates)
PIVOT = 47                      # the design's column on the old idle_base's pivot (--pivot: overlap 0.76)

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


CHECKER = {"dead_7"}             # raw sheets drawn on a grey checkerboard (254 / 230): keyed to white from the edges


def unchecker(a):
    """The light greys (each channel >= 222, spread <= 8) reached from the sheet's edges made the white ground."""
    rgb = a[..., :3].astype(int)
    lite = (rgb.min(-1) >= 222) & (rgb.max(-1) - rgb.min(-1) <= 8)
    lbl, _ = ndimage.label(lite)
    bg = np.isin(lbl, list(set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}))
    out = a.copy()
    out[bg, :3] = 255
    return out


def frame_masks(s):
    """(sheet picture, [(frame, mask)]) of a sheet."""
    a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
    if s["name"] in CHECKER:
        a = unchecker(a)
    return a, CS.cells(s, CS.figure(a))


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
    """His size: the orange of his helmet, its largest 4-connected piece - the shoulders and boots are the same orange
    but walled off by the outline; the helmet is as big in every pose."""
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = op & (r >= 100) & (r - g >= 40) & (b <= 70) & (g >= 30)
    lbl, n = ndimage.label(m)
    if n < 2:
        return m
    return lbl == int(np.argmax(ndimage.sum(m, lbl, range(1, n + 1)))) + 1


def heads():
    """{"<tag>_<frame>": helmet}: each placed frame's helmet against the design's - the square root of its
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
    figure best at one s, and the drawing's px a square is SQ / s. Longer claws, spread wings or a raised branch move
    the drawing's box and area, hardly this."""
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


def old_squares(tag, k):
    """The old frame's body scaled to the design's squares (nearest), and its pivot column / soles row in it."""
    if tag == "idle_base":
        fr = PK.idle_sheet()
        pvx, pvy = fr.shape[1] / 2, fr.shape[0] / 2 + PK.OLD_SOLES
    else:
        fr, _, (pvx, pvy) = OLD[tag][k - 1]
    m = old_body(fr)
    h, w = m.shape
    big = np.asarray(Image.fromarray(m.astype(np.uint8) * 255).resize((round(w * PPU), round(h * PPU)), Image.NEAREST)) > 127
    return big, pvx * PPU, pvy * PPU


def best_column(pic, y, tag, k):
    """(x, overlap): the column the picture overlaps the old body best at, its top on row y (the old body's pivot on
    PIVOT, its soles on GROUND); x tried over the old body's width either way."""
    om, px, py = old_squares(tag, k)
    ox, oy = int(round(PIVOT - px)), int(round(GROUND - py))
    m = pic[..., 3] > 0
    best = (-1.0, 0)
    for x in range(ox - m.shape[1], ox + om.shape[1] + 1):
        x0, x1 = max(x, ox), min(x + m.shape[1], ox + om.shape[1])
        y0, y1 = max(y, oy), min(y + m.shape[0], oy + om.shape[0])
        inter = 0 if x1 <= x0 or y1 <= y0 else int((m[y0 - y:y1 - y, x0 - x:x1 - x] & om[y0 - oy:y1 - oy, x0 - ox:x1 - ox]).sum())
        iou = inter / (m.sum() + om.sum() - inter)
        if iou > best[0]:
            best = (iou, x)
    return best[1], best[0]


OVERLAP_MIN = 0.35              # under this the box's middle on the old box's middle (casts_khazix_hd's)
DIAG = {}


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)}: its bottom on the old box's bottom
    (nothing under the soles' row), its column where it overlaps the old body best (best_column; the box's middle on
    the old box's middle where that overlap is poor)."""
    out = {}
    for n, (sq, mid, bottom, zoom) in read_all().items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        y = min(int(round(GROUND + bottom - pic.shape[0])), GROUND - pic.shape[0])
        tag, k = n.rsplit("_", 1)
        x_box = int(round(PIVOT + mid - pic.shape[1] / 2))
        x, ov = best_column(pic, y, tag, int(k))
        if ov < OVERLAP_MIN:
            x = x_box
        DIAG[n] = (round(ov, 2), x - x_box)
        out[n] = (pic, x, y)
    for n in CHAIN_CUT:
        out[n] = chain_cut(n, *out[n])
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
# frames whose chain Codex ran off the sheet's right edge (cut through a link, and twice the old chain's length): cut
# where the old frame's chain ends, at the narrowest column (a link's joint) within 4 squares of it; the rig's outline
# pass closes the end
CHAIN_CUT = ["skill_5", "skill_pull_1", "skill_pull_2"]


def chain_cut(name, pic, x, y):
    tag, k = name.rsplit("_", 1)
    L, T, R, B = old_box(tag, int(k))
    end = int(round(PIVOT + R * PPU)) - x                      # the old chain's end, in the picture's columns
    op = pic[..., 3] > 0
    cols = range(max(1, end - 4), min(op.shape[1] - 1, end + 5))
    cut = min(cols, key=lambda c: (int(op[:, c].sum()), abs(c - end)))
    out = pic[:, :cut].copy()
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[:ys.max() + 1], x, y


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


def pivot():
    """The design's column on the old idle_base's pivot: the old idle_base 1's body at the design's squares, its soles
    on the design's, slid along until it overlaps the design best."""
    om, px, py = old_squares("idle_base", 1)
    dm = D0[..., 3] > 0
    oy = int(round(GROUND - py))
    best = (-1.0, 0)
    for ox in range(-om.shape[1], dm.shape[1] + 1):
        x0, x1 = max(0, ox), min(dm.shape[1], ox + om.shape[1])
        y0, y1 = max(0, oy), min(dm.shape[0], oy + om.shape[0])
        inter = 0 if x1 <= x0 or y1 <= y0 else int((dm[y0:y1, x0:x1] & om[y0 - oy:y1 - oy, x0 - ox:x1 - ox]).sum())
        iou = inter / (dm.sum() + om.sum() - inter)
        if iou > best[0]:
            best = (iou, ox)
    print("PIVOT", int(round(best[1] + px)), "overlap", round(best[0], 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pivot", action="store_true", help="the design's column on the old idle_base's pivot")
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true", help="the ZOOM search, frame by frame (slow: minutes)")
    ap.add_argument("--area", action="store_true", help="each sheet's zoom from its figure's area")
    ap.add_argument("--heads", action="store_true", help="each frame's head against the design's at ZOOM")
    ap.add_argument("--heights", action="store_true", help="each frame's zoom from its height against the old frame's")
    ap.add_argument("--fits", help="each frame's zoom from its fit over its template: the pack's templates folder")
    a = ap.parse_args()
    if a.pivot:
        pivot()
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
