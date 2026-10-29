#!/usr/bin/env python3
"""Kayle's actions from Codex's whole-frame redraw (assets/source/kayle/hd/casts: tools/art/pack_kayle_actions.py's
pack, delivered 2026-10-29, Documents/Codex/2026-10-29/new-chat-8/outputs/kayle_actions_done.zip - its own strict
checks not passed, the drawings complete) read onto the design's squares - tools/art/casts_zed_hd.py's reading
(casts_rengar_hd's keying, cells and palette sampling, each sheet at the zoom its figure and head give), pointed at
her design.

hd/casts holds Codex's 31 chosen sheets (its raw/ - the rejected tries - left out). Codex drew finished pictures on a
near-white ground, not on the templates' grid, each sheet at its own size; so each sheet's zoom is read: the mean of
the figure's AREA over the design's (--area) and, where the head fits (--measure), the HEAD's zoom (the white hair, the
amber eyes, the gold gorget under them). Her hair, the wings' light edges and the blade are near the ground's white:
casts_rengar_hd.figure keys a walled-in white away only when the outline rings it.

Each frame is then placed where the old frame stood: its box's middle on the old box's middle and its bottom on the
old box's bottom, from the pivot (old frames: the soles 11.5 pixels under the frame's centre), on the design's grid;
R's sword flung up alone in frame 6 then moved to where the old frame has it (THROWN).
She hovers: her old idle_base's lowest pixel (the sword's tip) is HOVER old pixels over its soles' line, so the design's
ground is that far under its lowest row; its pivot column (PIVOT) is where the design lies best over the old idle_base
(their overlap's peak, 0.70; Taric's lesson: not a shoes' middle, the sword's tip stands lowest).

    python tools/art/casts_kayle_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_kayle_hd.py --area            # each sheet's zoom from its figure's area
    python tools/art/casts_kayle_hd.py --measure         # the head's zoom, frame by frame (slow: minutes)
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
import pack_kayle_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "kayle", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 49          # 112 rows over her 1x 49 (design_kayle_hd: wing tips to sword tip)
HOVER = 2                       # old pixels between her old idle_base's lowest (the sword's tip) and its soles' line
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1 + int(round(HOVER * PPU))   # the soles' line, under her
HEAD = (27, 51, 15, 38)         # the design's head: rows 27-50 (the top of the hair to the chin), the hair's sides
# px of Codex's drawing a design square, a sheet: the figure's area over the design's (--area) read too small - the
# design spreads its wings and holds the long sword out, the actions fold them, so every frame came out big, its head
# 10-20 % over the design's - times the head's own size against the design's (heads()): the geometric mean of her hair's
# and her face's (each its largest piece) square roots of their areas; the hair's alone where the face turns to us
# (the kneeling death, the struck frame). The head fit (--measure) wandered (its template takes in the wings)
ZOOM = {"run_1": 9.46, "run_2": 8.77, "run_3": 8.43, "run_4": 9.39, "run_5": 9.7, "run_6": 9.13, "run_7": 8.8,
        "run_8": 8.79, "attack_1": 7.66, "attack_2": 8.58, "attack_3": 9.36, "attack_4": 9.53,
        "attack_melee_1": 8.86, "attack_melee_2": 8.85, "attack_melee_3": 9.48, "skill_1": 9.24, "skill_2": 10.1,
        "skill_3": 8.49, "skill2_1": 8.9, "skill2_2": 8.39, "skill2_3": 8.1, "ult_1": 7.38, "ult_2": 7.65,
        "ult_3": 7.12, "ult_4": 8.35, "hit_1": 8.3, "dead_1": 8.19, "dead_2": 8.5, "dead_3": 8.12, "dead_4": 7.2,
        "dead_5": 8.53}
ZOOMS = np.arange(3.0, 9.01, 0.2)                       # the zooms the head is searched at (7- and 4-px templates)
PIVOT = 30                      # the design's column on the old idle_base's pivot (overlap peak 0.70)

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


def old_box(tag, k):
    """The old frame's visible box from its pivot, in 1x pixels: (left, top, right, bottom); y up negative."""
    fr, _, (pvx, pvy) = OLD[tag][k - 1]
    ys, xs = np.nonzero(fr[..., 3] > 0)
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


def read_all():
    """{"<tag>_<frame>": (squares, the old box's middle and bottom from the pivot in design squares, the zoom)}."""
    out = {}
    for s in sheets():
        a, ms = frame_masks(s)
        for k, m in ms:
            L, T, R, B = old_box(s["tag"], k)
            out[f"{s['tag']}_{k}"] = (at_zoom(a, m, ZOOM[s["name"]]), (L + R) / 2 * PPU, B * PPU, ZOOM[s["name"]])
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


def _hair(a):
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    return op & (rgb.min(-1) >= 180) & (rgb.max(-1) - rgb.min(-1) <= 22) & (rgb[..., 2] >= rgb[..., 0])


def _face(a):
    rgb, op = a[..., :3].astype(int), a[..., 3] > 0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return op & (r >= 235) & (g >= 180) & (g <= 235) & (b >= 140) & (b <= 215)


def heads():
    """{"<tag>_<frame>": (hair, face)}: each placed frame's head against the design's - the square root of its hair's
    and its face's largest piece over the design's (1.0: the design's size; ZOOM is right when they are near 1)."""
    dh, df = _largest(_hair(D0)), _largest(_face(D0))
    out = {}
    for n, (pic, _, _) in placed().items():
        out[n] = (round((_largest(_hair(pic)) / dh) ** 0.5, 2), round((_largest(_face(pic)) / df) ** 0.5, 2))
        print(n, out[n], flush=True)
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
    return out


THROWN = ["ult_6"]              # R's frame 6: the sword flung up alone - Codex drew it 30 squares over her head


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
