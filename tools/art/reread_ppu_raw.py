#!/usr/bin/env python3
"""A Codex strips delivery re-read from its raw drafts by its own manifest.json (each frame's source crop, art box and
read scale, and where it went in the cell), without the head Codex pasted over every frame afterwards.

league_garen (PPU 3, 2026-10-12): Codex's own script pasted the design's head into every frame and left its old head's
outline round it, see-through holes in faces and, in the leaping strike, a second face on the chest; its raw drafts are
clean. Every square is the commonest design colour in the middle of its block (each raw pixel to its nearest design
colour first); parts apart from the figure under a fifth of its size (bits of the next frame in the crop) go.

    python tools/art/reread_ppu_raw.py <delivery folder> <out folder> dist/ppu_packs/garen/design/garen_design_1x.png         --raw garen_spin_2.png=garen_spin_2_rejected_back.png --raw garen_spin_3.png=garen_spin_3_rejected_back.png
--raw IMAGE=RAW reads IMAGE's frames from another raw draft (each frame from the same crop, its art box from the
draft's own pixels, RAW_K raw pixels a square - the size of his other spin frames - its soles on the cell's feet row and
their middle on the cell's standing point, as near as the cell lets it): his E spin, where Codex drew him turning his back and set those drafts aside
because the pack said 「不画背影」 - kept, his E stayed facing right and did not turn (「盖伦放E的时候模型不会旋转了？」).
    python tools/art/import_ppu_strips.py --hero garen --delivery <out folder>
"""
import argparse, json, os, shutil
import numpy as np
from scipy import ndimage
from PIL import Image
ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("design")
ap.add_argument("--raw", action="append", default=[], metavar="IMAGE=RAW")
a = ap.parse_args()
src, out, design = a.src, a.out, a.design
swap = dict(r.split("=") for r in a.raw)
RAW_K = 6.9
os.makedirs(out, exist_ok=True)
shutil.copyfile(os.path.join(src, "cells.json"), os.path.join(out, "cells.json"))
d = np.asarray(Image.open(design).convert("RGBA"))
pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)
man = json.load(open(os.path.join(src, "manifest.json")))
cells = {(im["file"], c["frame"]): c for im in json.load(open(os.path.join(src, "cells.json")))["images"] for c in im["cells"]}
PX = 6
for img in man:
    W, H = img["squares"]
    sq = np.zeros((H, W, 4), np.uint8)
    raw = np.asarray(Image.open(os.path.join(src, "raw", swap.get(img["file"], img["file"]))).convert("RGBA")).astype(int)
    for fr in img["frames"]:
        cx, cy, cw, ch = fr["rect"]
        bx0, by0, bx1, by1 = fr["bbox"]
        sx0, sy0 = fr["source_crop"][:2]
        ax0, ay0, ax1, ay1 = fr["source_art_bbox"]
        k = fr["grid_read_scale"]
        if img["file"] in swap:
            k = RAW_K
            cx1, cy1 = fr["source_crop"][2:]
            crop = raw[sy0:min(cy1, raw.shape[0]), sx0:cx1, 3] >= 128
            ys, xs = np.nonzero(crop)
            ax0, ay0, ax1, ay1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
            w, h = int(round((ax1 - ax0) / k)), int(round((ay1 - ay0) / k))
            low = ys >= ys.max() - int(4 * k)
            feet = ((xs[low].min() + xs[low].max()) / 2 - ax0) / k
            c = cells[(img["file"], fr["frame"])]
            by1 = c["feet_row"] - cy + 1
            by0 = by1 - h
            # inside the cell (its frame is PPU x the 1x frame): as near the standing point as it fits
            bx0 = min(max(0, int(round(c["pivot"][0] - cx - feet))), cw - w)
            bx1 = bx0 + w
        for j in range(by1 - by0):
            for i in range(bx1 - bx0):
                x0 = sx0 + ax0 + i * k
                y0 = sy0 + ay0 + j * k
                blk = raw[int(round(y0 + k * 0.2)):int(round(y0 + k * 0.8)), int(round(x0 + k * 0.2)):int(round(x0 + k * 0.8))]
                blk = blk.reshape(-1, 4)
                if not len(blk) or (blk[:, 3] >= 128).sum() * 2 < len(blk):
                    continue
                px = blk[blk[:, 3] >= 128][:, :3]
                idx = ((px[:, None, :] - pal[None]) ** 2).sum(-1).argmin(1)
                c = pal[np.bincount(idx).argmax()]
                Y, X = cy + by0 + j, cx + bx0 + i
                if 0 <= Y < H and 0 <= X < W:
                    sq[Y, X, :3] = c
                    sq[Y, X, 3] = 255
        # parts apart from the figure (bits of the next cell in Codex's crop): only the figure stays
        cell = sq[cy:cy + ch, cx:cx + cw]
        op = cell[..., 3] > 0
        lab, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(op, lab, range(1, n + 1))
            big = sz.max()
            for v, z in enumerate(sz, 1):
                if z < big * 0.2:
                    cell[lab == v] = 0
                    print(f"  {img['file']} frame {fr['frame']}: dropped a part of {int(z)} squares")
    Image.fromarray(np.repeat(np.repeat(sq, PX, 0), PX, 1)).save(os.path.join(out, img["file"]))
    print(img["file"], sq.shape)
