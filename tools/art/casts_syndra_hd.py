#!/usr/bin/env python3
"""Syndra's nine poses (tools/art/pack_syndra_actions.py's pack, delivered 2026-10-27, Documents/Codex/2026-10-27/
new-chat-7/outputs/syndra_actions_done.zip: hd/casts/pose_1..5.png, white ground, her silver hair kept) read onto the
design's squares and lined up with it - tools/art/casts_rengar_hd.py's reading (its keying, cells, palette sampling and
head search, pointed at her design here).

Codex redrew her whole in each pose and its head, hair and size drift a little from picture to picture (its HANDOFF
says so), so a pose is not used whole: rig_syndra_hd takes only the part that changes (the far arm, the death's
crumple) and puts it on the design. For that each pose is read at the zoom its head gives (the design's horns, helmet
and face searched over it, casts_rengar_hd.head_fit) and the head's place is kept: the pose's offset onto the design.

    python tools/art/casts_syndra_hd.py --review DIR      # every pose read, its head outline on it, and on the design
    python tools/art/casts_syndra_hd.py --measure         # the ZOOM table again
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_rengar_hd as CS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "syndra", "hd")
SRC = os.path.join(HD, "casts")
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
PPU = D0.shape[0] / 42
# her head for the match: the horns, the helmet and the face (rows 0-32, columns 12-43), the hair round it left out
HEAD = (0, 33, 12, 44)
# px of Codex's drawing a design square, a pose: --measure 2026-10-27 (the box's zoom x the head's scale)
ZOOM = {"A": 9.87, "B": 9.87, "C": 9.42, "D": 9.44, "E": 9.7, "F": 10.12, "G": 9.72, "H": 9.25, "I": 8.35}


def head_mask():
    r0, r1, c0, c1 = HEAD
    h = D0[r0:r1, c0:c1].astype(int)
    op = h[..., 3] > 0
    light = (h[..., :3].min(-1) >= 180) & (np.ptp(h[..., :3], -1) <= 40)      # the silver hair: not the head
    m = op & ~light
    lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
    return lbl == int(np.argmax(ndimage.sum(m, lbl, range(1, n + 1)))) + 1


# casts_rengar_hd's reading on her design
CS.D0, CS.HEAD = D0, HEAD
CS.PAL = np.unique(D0[D0[..., 3] > 0][:, :3], axis=0)
CS.PAL_LAB = color.rgb2lab(CS.PAL[None].astype(float) / 255.0)[0]
CS.HEAD_MASK = head_mask()


def poses():
    """[(label, sheet name, cell count)] in sheet order (hd/casts/sheets.json)."""
    with open(CS.lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        sheets = json.load(f)["sheets"]
    return [(p["pose"], s["name"], s["cells"]) for s in sheets for p in s["poses"]]


def cells_of(name, ncells):
    a = np.asarray(Image.open(CS.lp(os.path.join(SRC, name + ".png"))).convert("RGBA"))
    fig = CS.figure(a)
    return a, CS.cells(dict(cells=ncells, frames=list(range(ncells))), fig)


def head_place(pic):
    """(scale, error, row, column) of the design's head (scale 0.84-1.16) on pic: the top-left of HEAD's box."""
    best = None
    for sc in np.arange(0.84, 1.161, 0.04):
        rgb, m = CS.head_tpl(sc, 0)
        e, y, x = CS.match(pic, rgb, m, 2)
        e, y, x = CS.match(pic, rgb, m, 1, (y, x))
        if best is None or e < best[0]:
            best = (e, sc, y - m.shape[0], x - m.shape[1])
    return best[1], best[0], best[2], best[3]


def read(zoom_of=None):
    """{label: (picture at design squares, (dy, dx) to put it on the design: its head on the design's head,
    zoom, head error)}."""
    out = {}
    by_sheet = {}
    for lab, name, n in poses():
        by_sheet.setdefault((name, n), []).append(lab)
    for (name, n), labs in by_sheet.items():
        a, cs = cells_of(name, n)
        for (k, m), lab in zip(cs, labs):
            ys, xs = np.nonzero(m)
            gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
            zoom = (zoom_of or ZOOM).get(lab) or gh / (D0.shape[0] - 1)
            sq = CS.sample(a, m, round(gh / zoom), round(gw / zoom))
            yy, xx = np.nonzero(sq[..., 3] > 0)
            sq = sq[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
            sc, err, hy, hx = head_place(sq)
            out[lab] = (sq, (HEAD[0] - hy, HEAD[2] - hx), zoom, sc, err)
    return out


def measure():
    """ZOOM: each pose's first read at its box's zoom, the head's scale folded in (zoom x scale), read again."""
    first = read({})
    return {lab: round(float(z * sc), 2) for lab, (_, _, z, sc, _) in first.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        print("ZOOM =", json.dumps(measure()))
        return
    got = read()
    for lab, (p, off, z, sc, err) in got.items():
        print(lab, p.shape[:2], "offset", off, "zoom", round(z, 2), "head x%.2f err %.0f" % (sc, err))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    Z = 6
    tiles = []
    for lab, (p, (dy, dx), z, sc, err) in got.items():
        H = max(D0.shape[0], p.shape[0] + max(0, dy)) + 4
        W = max(D0.shape[1], p.shape[1] + max(0, dx)) + 30
        can = Image.new("RGBA", (W, H + 4), (150, 165, 150, 255))
        ox, oy = max(0, -dx) + 2, max(0, -dy) + 2
        can.alpha_composite(Image.fromarray(p), (ox + dx, oy + dy) if dx >= 0 and dy >= 0 else (ox + dx, oy + dy))
        im = can.convert("RGB").resize((can.width * Z, can.height * Z), Image.NEAREST)
        dr = ImageDraw.Draw(im)
        r0, r1, c0, c1 = HEAD
        dr.rectangle([(ox + c0) * Z, (oy + r0) * Z, (ox + c1) * Z, (oy + r1) * Z], outline=(255, 0, 255), width=2)
        dr.text((4, 4), f"{lab}: x{sc:.2f} err {err:.0f}", fill=(0, 0, 0))
        tiles.append(im)
    W = sum(t.width + 6 for t in tiles)
    H = max(t.height for t in tiles)
    can = Image.new("RGB", (W, H), (40, 40, 40))
    x = 0
    for t in tiles:
        can.paste(t, (x, 0))
        x += t.width + 6
    can.save(os.path.join(a.review, "syndra_poses_read.png"))
    print("written", a.review)


if __name__ == "__main__":
    main()
