#!/usr/bin/env python3
"""Zed's actions from Codex's whole-frame redraw (assets/source/zed/hd/casts: tools/art/pack_zed_actions.py's pack,
delivered 2026-10-28, Documents/Codex/2026-10-28/new-chat-7/outputs/zed_actions_done.zip - its own strict checks not
passed, the drawings complete) read onto the design's squares - tools/art/casts_tristana_hd.py's reading
(casts_rengar_hd's keying, cells and palette sampling, each sheet at the zoom its head gives), pointed at his design.

hd/casts holds Codex's 22 chosen sheets (its raw/ - the first tries and the revisions - left out). Codex drew finished
pictures on a near-white ground, not on the templates' 8-px grid, each sheet at its own size; so each sheet's zoom is
read off his HEAD (the helmet, its gold trim, the red eyes and the red hood round it): the zoom at which the design's
head, at its own size, fits the frame's head best (ZOOM; --measure). His blades and the shuriken's lit faces are near
the ground's white: casts_rengar_hd.figure keys a walled-in white away only when the outline rings it.

Each frame is then placed where the old frame stood: its box's middle on the old box's middle and its bottom on the
old box's bottom, from the pivot (old frames: the soles 11.5 pixels under the frame's centre), on the design's grid
(the design's pivot: his feet's middle, OLD_CENTRE right of it). The old frames that are another frame's picture
(pack_zed_actions.SAME) take that frame's drawing on their OWN old box - several are the same picture moved (E 5,
R 2 and 4, the death's 7 and 8).

    python tools/art/casts_zed_hd.py --review DIR      # every tag placed, at 2x, the design first
    python tools/art/casts_zed_hd.py --measure         # the ZOOM search again, frame by frame (slow: minutes)
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
import casts_draven_hd as CD  # noqa: E402
import casts_rengar_hd as CS  # noqa: E402
import pack_zed_actions as PK  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "zed", "hd")
SRC = os.path.join(HD, "casts")
TAGS = PK.TAGS
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles
PPU = D0.shape[0] / 40          # 65 rows over his 1x 40 (design_zed_hd)
HEAD = (5, 22, 18, 34)          # the design's head: rows 5-21 (the helmet's top to the hood under the visor), the red
#                                 hood and the helmet's gold trim out both sides
# px of Codex's drawing a design square, a sheet (2026-10-28): the mean of two reads - the figure's AREA over the
# design's (1662 squares: the square root of the ratio, the same within a sheet to 0.1-0.3 whatever the pose; its reds
# and golds alone agree) and, where the head fits (--measure, error <= 60), the HEAD's zoom. The head alone wandered
# (its fits 8.2-10.8, noisy with the sampling's phase: the run's 9.6 read his body 5 % too small beside the design);
# where his head is turned, bowed or lying (Q's rearing, E's spin, the kneeling and the fall) the area alone
ZOOM = {"run_1": 8.8, "run_2": 9.3, "run_3": 9.4, "run_4": 8.7, "attack_1": 10.4, "attack_2": 10.4, "attack_3": 9.4,
        "skill_1": 9.4, "skill_2": 8.4, "skill2_1": 10.9, "skill2_2": 10.1, "skill2_3": 8.5, "skill_e_1": 9.9,
        "skill_e_2": 9.6, "skill_e_3": 8.7, "ult_1": 10.3, "ult_2": 10.0, "ult_3": 8.6, "hit_1": 8.6, "dead_1": 10.0,
        "dead_2": 8.9, "dead_3": 8.8}
ZOOMS = np.arange(5.6, 11.01, 0.2)                      # the zooms the head is searched at (8-px templates)
OLD_CENTRE = 1.0                # the old idle: its frame's centre 1 pixel right of its feet's middle (14.5 / 15.5)
PIVOT = int(round(CD.shoes_mid(D0) + OLD_CENTRE * PPU))

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
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true", help="the ZOOM search, frame by frame (slow: minutes)")
    a = ap.parse_args()
    if a.measure:
        measure()
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
