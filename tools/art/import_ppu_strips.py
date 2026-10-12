#!/usr/bin/env python3
"""A Codex delivery of dense (PPU) action strips -> assets/source/ppu/<hero>_<tag>.png, the drawn strips ppu_hd.py uses.

The user, 2026-10-12: 「接下来使用PPU修复吸血鬼和卡尔玛和艾希 做到所有动作帧一致 待机一致」. tools/art/pack_ppu_strips.py
made the pack (every 1x frame scaled by PPU as a skeleton in a cell, cells.json); Codex drew the design over every cell
at the pack's square size. This reads every image back square for square (each block's most common colour, clear
included), maps the colours to the design's, and puts each cell into its frame by the pivot: the frame is
round(PPU x the 1x frame) and its centre is the pivot, as in the game. A cell that starts above the frame
(frame_top < 0: room for the design's head) grows the frame by as much at the top and the bottom, so the pivot stays
its centre; the grown sizes go to <hero>_<tag>.json next to the strip. The idle is the design itself, still in every
frame (「待机一致」; an importer's breathing deforms the body: memory rig-deformation-checks), standing where the 1x idle
stands (its soles on the 1x soles, across where it overlaps the scaled 1x idle most).

    python tools/art/import_ppu_strips.py --hero vladimir --delivery <outputs>/vladimir-ppu-strips
    python tools/art/import_ppu_strips.py --hero yasuo --delivery <...> --scale 2     # pack PPU 1.5 -> game PPU 3

Then: python tools/art/ppu_hd.py --hero <hero> (the hd_ tags into the sheet) and the hero in
addons/league_main/src/hd.rs.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ppu")
PACKS = os.path.join(ROOT, "dist", "ppu_packs")


def squares(path, px):
    """The image read back one pixel per drawn px x px square: each block's most common colour (clear counts)."""
    a = np.asarray(Image.open(path).convert("RGBA"))
    H, W = a.shape[0] // px, a.shape[1] // px
    b = a[:H * px, :W * px].reshape(H, px, W, px, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, px * px, 4).copy()
    b[b[..., 3] < 128] = 0
    b[..., 3] = np.where(b[..., 3] > 0, 255, 0)
    out = np.zeros((H, W, 4), np.uint8)
    mixed = 0
    keys = b.astype(np.uint32)
    keys = (keys[..., 0] << 24) | (keys[..., 1] << 16) | (keys[..., 2] << 8) | keys[..., 3]
    for y in range(H):
        for x in range(W):
            v, n = np.unique(keys[y, x], return_counts=True)
            if len(v) > 1:
                mixed += 1
            k = int(v[n.argmax()])
            out[y, x] = ((k >> 24) & 255, (k >> 16) & 255, (k >> 8) & 255, k & 255)
    return out, mixed


def to_palette(a, pal):
    """Every opaque pixel to its nearest design colour. -> (image, pixels changed)."""
    op = a[..., 3] > 0
    rgb = a[op][:, :3].astype(int)
    d = ((rgb[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
    near = pal[d.argmin(axis=1)]
    out = a.copy()
    out[op, :3] = near
    return out, int((near != rgb).any(axis=1).sum())


def place_idle(design, idle1, k):
    """The design in a frame of round(k x the 1x idle): soles on the 1x soles, across at the most overlap."""
    H, W = round(idle1.shape[0] * k), round(idle1.shape[1] * k)
    sk = P.scale_any(idle1, k)[..., 3] > 0
    sole = np.nonzero(sk.any(axis=1))[0].max()
    dh, dw = design.shape[:2]
    y0 = sole - dh + 1
    if y0 < 0 or dw > W:
        sys.exit(f"the design ({dw}x{dh}) does not fit the idle frame {W}x{H} (soles at row {sole})")
    dm = design[..., 3] > 0
    best = max(range(0, W - dw + 1), key=lambda x0: int((sk[y0:y0 + dh, x0:x0 + dw] & dm).sum()))
    out = np.zeros((H, W, 4), np.uint8)
    out[y0:y0 + dh, best:best + dw] = design
    return out, (best, y0)


def write_strip(hero, tag, frames, want):
    """frames left to right, 1 px apart, top-aligned; <hero>_<tag>.json lists the sizes when any is not `want`."""
    h = max(f.shape[0] for f in frames)
    w = sum(f.shape[1] for f in frames) + len(frames) - 1
    s = np.zeros((h, w, 4), np.uint8)
    x = 0
    for f in frames:
        s[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    Image.fromarray(s).save(os.path.join(SRC, f"{hero}_{tag}.png"))
    side = os.path.join(SRC, f"{hero}_{tag}.json")
    sizes = [[int(f.shape[1]), int(f.shape[0])] for f in frames]
    if sizes != [list(v) for v in want]:
        with open(side, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"sizes": sizes}, fh)
    elif os.path.isfile(side):
        os.remove(side)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--delivery", required=True, help="Codex's folder: cells.json and the <hero>_<tag>_<n>.png images")
    ap.add_argument("--design", help="the design, 1 px per square (default: the pack's design/<hero>_design_1x.png)")
    ap.add_argument("--scale", type=int, default=1, help="game pixels per drawn square (yasuo: 2)")
    ap.add_argument("--same", action="append", default=[], metavar="TAG:I=J",
                    help="frame I of TAG is frame J's drawing, its lowest row on frame I's skeleton's lowest row (a "
                         "drawing that does not match its neighbours; vladimir dead:5=4 dead:6=4 dead:7=4 - Codex drew "
                         "the last three lying frames apart, a different crumpled body from frames 3-4)")
    a = ap.parse_args()
    hero, s = a.hero, a.scale
    with open(os.path.join(a.delivery, "cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    px, k = cells["px_per_square"], cells["ppu"] * s
    if hero not in P.PPU or abs(P.PPU[hero] - k) > 1e-3:
        sys.exit(f"{hero}: PPU in tools/art/ppu_hd.py must be {k:g} (the pack's {cells['ppu']:g} x --scale {s})")
    dpath = a.design or os.path.join(PACKS, hero, "design", f"{hero}_design_1x.png")
    design = np.asarray(Image.open(dpath).convert("RGBA")).copy()
    design[..., 3] = np.where(design[..., 3] > 0, 255, 0)
    pal = np.unique(design[design[..., 3] > 0][:, :3], axis=0).astype(int)
    sheet = P.read_sheet(os.path.join(ROOT, "league", "champions", f"league_{hero}"))
    got = {}
    for im in cells["images"]:
        p = os.path.join(a.delivery, im["file"])
        if not os.path.isfile(p):
            sys.exit(f"missing {p}")
        sq, mixed = squares(p, px)
        sq, recoloured = to_palette(sq, pal)
        if tuple(sq.shape[1::-1]) != tuple(im["squares"]):
            sys.exit(f"{im['file']}: {sq.shape[1]}x{sq.shape[0]} squares, the pack's {im['squares']}")
        inside = np.zeros(sq.shape[:2], bool)
        for m in im["cells"]:
            x, y, w, h = m["rect"]
            inside[y:y + h, x:x + w] = True
        lost = int((sq[..., 3] > 0)[~inside].sum())
        print(f"{im['file']}: {mixed} mixed squares, {recoloured} recoloured, {lost} drawn outside the cells (dropped)")
        for m in im["cells"]:
            x, y, w, h = m["rect"]
            cell = up(sq[y:y + h, x:x + w], s)
            fw, fh = m["frame_size"]
            one = sheet[m["tag"]][m["frame"]][0]
            FW, FH = round(one.shape[1] * k), round(one.shape[0] * k)
            g = max(0, -m["frame_top"] * s)
            FH += 2 * g
            # the cell's origin so that its pivot (fw/2, fh/2 - top in squares) is the frame's centre
            ox = round(FW / 2 - fw * s / 2)
            oy = round(FH / 2 - (fh / 2 - m["frame_top"]) * s)
            fr = np.zeros((FH, FW, 4), np.uint8)
            cy0, cx0 = max(0, -oy), max(0, -ox)
            cy1, cx1 = min(cell.shape[0], FH - oy), min(cell.shape[1], FW - ox)
            cut = int((cell[..., 3] > 0).sum()) - int((cell[cy0:cy1, cx0:cx1, 3] > 0).sum())
            if cut:
                print(f"  {m['tag']}[{m['frame']}]: {cut} pixels past the frame (dropped)")
            fr[oy + cy0:oy + cy1, ox + cx0:ox + cx1] = cell[cy0:cy1, cx0:cx1]
            specks = drop_specks(fr)
            if specks:
                print(f"  {m['tag']}[{m['frame']}]: specks of {specks} pixels apart from the figure (dropped)")
            got.setdefault(m["tag"], {})[m["frame"]] = fr
    for spec in a.same:
        tag, ij = spec.split(":")
        i, j = (int(v) for v in ij.split("="))
        got[tag][i] = same_as(got[tag][j], got[tag][i].shape[:2], sheet[tag][i][0], k)
        print(f"{tag}[{i}]: frame {j}'s drawing, on its own skeleton's lowest row")
    design_s = up(design, s)
    idle = sheet["idle"]
    fr, at = place_idle(design_s, idle[0][0], k)
    got["idle"] = {i: fr for i in range(len(idle))}
    print(f"idle: the design ({design_s.shape[1]}x{design_s.shape[0]}) at {at} in every one of {len(idle)} frames")
    os.makedirs(SRC, exist_ok=True)
    for tag, frames in sheet.items():
        if tag.startswith(P.PREFIX):
            continue
        have = got.get(tag, {})
        if sorted(have) != list(range(len(frames))):
            sys.exit(f"{tag}: frames {sorted(have)} delivered, {len(frames)} in the sheet")
        want = [(round(f.shape[1] * k), round(f.shape[0] * k)) for f, _ in frames]
        write_strip(hero, tag, [have[i] for i in range(len(frames))], want)
        print(f"assets/source/ppu/{hero}_{tag}.png: {len(frames)} frames")


def same_as(src, shape, one, k):
    """`src` (a frame) in a frame of `shape`, centred across, its lowest opaque row on the lowest row of the 1x
    frame `one` scaled by k (the frame grown alike at both ends: the 1x frame centred in it)."""
    H, W = shape
    sk = P.scale_any(one, k)
    want = np.nonzero(sk[..., 3].any(axis=1))[0].max() + (H - sk.shape[0]) // 2
    have = np.nonzero(src[..., 3].any(axis=1))[0]
    dy, dx = want - have.max(), (W - src.shape[1]) // 2
    out = np.zeros((H, W, 4), np.uint8)
    ys, xs = np.nonzero(src[..., 3] > 0)
    ok = (ys + dy >= 0) & (ys + dy < H) & (xs + dx >= 0) & (xs + dx < W)
    if not ok.all():
        sys.exit(f"the drawing does not fit the frame {W}x{H}")
    out[ys + dy, xs + dx] = src[ys, xs]
    return out


def drop_specks(fr, below=4):
    """Clear the parts of fewer than `below` pixels (8-connected) - a dot left floating by the image model
    (「别留多余的像素」). -> their sizes."""
    from scipy import ndimage
    op = fr[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    small = [v + 1 for v, z in enumerate(sizes) if z < below]
    fr[np.isin(lab, small)] = 0
    return [int(sizes[v - 1]) for v in small]


def up(a, s):
    return a if s == 1 else np.repeat(np.repeat(a, s, axis=0), s, axis=1)


if __name__ == "__main__":
    main()
