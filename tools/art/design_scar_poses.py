#!/usr/bin/env python3
"""Scar's Codex poses (assets/source/scar/codex_poses: POSE_PROMPTS.md, 22 key poses of his own TFT clips on his
design, 2026-10-28) as game pictures: cropped, the design's head where Codex did not put it, gaps closed.

    python tools/art/design_scar_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_scar_poses.py                  # writes assets/source/scar/hd/pose_<name>.png (+ .json)

Codex delivered every pose twice: 1254 px canvases on exact 12 px squares and pixel_1x/ (105 x 105, one pixel a
square, on the pose pack's own grid from the canvas corner), all in the design's 36 colours, and it pasted the design's
head (approved-head-1x.png = the pack's 1_head.png, 27 x 29) square for square into the 20 poses that stand. So each
pose is read from pixel_1x as it is; its json keeps where the figure's top-left square is on that grid (grid_at: Codex
drew each pose where its reference put it, so rig_scar places them by it) and where the head box went (manifest.json).
The two falls kept a head Codex drew itself, about 16 squares and the sockets smeared (8x, 2026-10-28): d_fall gets
the design's head upright, centred where Codex's was; d_down (on his back, the head at the image left) the design's
head turned a quarter left so the mask looks up and the neck meets the body, its right edge on the shoulder. Codex's
own head squares round a pasted head that it does not cover are cleared where they are head-only colours; loose specks
dropped, small holes closed (design_silco_poses.close_gaps).

The walk is read from Codex's raw drafts instead (raw/scar-pose-run<k>-generated.png): to hold the head on one column
with the soles fixed Codex resampled the body's rows in pixel_1x, so the waist sat 36 to 40 rows under the head and 3 to
7 squares across from frame to frame (the user, 2026-10-28: 「走路的时候身体和头不协调 导致身体看起来变形」). Each
raw frame is read whole at one scale (the drafts were drawn 7.5 to 10.5 px a square, so the scale is the frame's own):
its jaw (the bottom of its skull, the largest bone-coloured blob in the top part) to its soles = WALK_JAW rows plus the
TFT walk's bob (WALK_NECK: his model's neck over the soles, pack_scar_poses' skeletons, less their mean); every square
the commonest design colour in its block's middle; the design's head on it, its skull's middle on the raw skull's middle
and its jaw on the raw jaw.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_scar_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import pack_scar_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scar", "codex_poses", "scar-poses")
OUT = os.path.join(ROOT, "assets", "source", "scar", "hd")
NAMES = list(PK.POSES)
# the falls: where the design's head goes (its box's middle, on pixel_1x's grid) and how it is turned
HEAD_CENTRE = {"d_fall": (25, 41), "d_down": (9, 80)}
TURN = {"d_down": 1}             # quarter turns left (np.rot90): the top of the head to the image left, the mask up
SPECK = 6                        # parts apart from the figure smaller than this are dropped
WALK = [f"run{k}" for k in range(1, 9)]
WALK_JAW = 53                    # rows from the jaw to the soles: pixel_1x's walk on average (its head at 21-23 + 22, soles 97)
# his TFT walk (pack_scar_poses' skeletons, 12 px squares): the neck's height over the soles
WALK_NECK = {"run1": 57.4, "run2": 55.6, "run3": 58.3, "run4": 57.3, "run5": 57.7, "run6": 55.5, "run7": 58.6,
             "run8": 57.6}
SKULL = (10, 9, 23, 22)          # the design head's skull (bone squares) in approved-head-1x.png: x0, y0, x1, y1


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def head():
    return np.asarray(Image.open(lp(os.path.join(SRC, "approved-head-1x.png"))).convert("RGBA")).copy()


def head_colours(d, h):
    """The colours only the head uses: not shared with the body, the spear or the outline."""
    x0, y0, x1, y1 = PK.HEAD_BOX
    rest = d.copy()
    rest[y0:y1, x0:x1][h[..., 3] > 0] = 0
    return {tuple(c) for c in h[h[..., 3] > 0][:, :3]} - {tuple(c) for c in rest[rest[..., 3] > 0][:, :3]}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {p["file"][len("scar-pose-"):-4]: p for p in json.load(f)["poses"]}


def walk_frame(name, d):
    """A walk frame read from its raw draft at one scale -> (squares, where the design head's top-left goes)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"scar-pose-{name}-generated.png"))).convert("RGBA")).astype(int)
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)
    bone = [i for i, c in enumerate(pal) if c.min() > 150 and c.max() - c.min() < 70]
    op = a[..., 3] >= 128
    lab = np.full(op.shape, -1)
    lab[op] = np.argmin(((a[op][:, None, :3] - pal[None]) ** 2).sum(-1), 1)
    ys, xs = np.nonzero(op)
    m = np.isin(lab, bone)
    m[int(ys.min() + 0.45 * (ys.max() - ys.min())):] = False      # the skull, not the bandaged arm
    lb, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    sky, skx = np.nonzero(lb == np.argmax(ndimage.sum(m, lb, range(1, n + 1))) + 1)
    jaw, mid, sole = sky.max(), (skx.min() + skx.max()) / 2, ys.max()
    rows = WALK_JAW + WALK_NECK[name] - np.mean(list(WALK_NECK.values()))
    b = (sole + 1 - jaw) / rows                                   # raw px a square
    H = int(np.ceil((sole + 1 - ys.min()) / b)) + 1
    left = int(np.ceil((mid - xs.min()) / b)) + 1                 # the skull's middle square
    W = left + int(np.ceil((xs.max() - mid) / b)) + 1
    out = np.zeros((H, W, 4), np.uint8)
    for r in range(H):
        y1 = sole + 1 - (H - 1 - r) * b
        y0 = int(round(y1 - b * 0.8))
        y1 = int(round(y1 - b * 0.2))
        for c in range(W):
            x0 = mid + (c - left - 0.5) * b
            win = lab[max(0, y0):max(0, y1), max(0, int(round(x0 + b * 0.2))):max(0, int(round(x0 + b * 0.8)))].ravel()
            if len(win) and (win >= 0).sum() * 2 > len(win):
                out[r, c, :3] = pal[np.bincount(win[win >= 0]).argmax()]
                out[r, c, 3] = 255
    jaw_row = H - 1 - int(round((sole + 1 - jaw) / b))
    return out, (int(round(left - (SKULL[0] + SKULL[2]) / 2)), jaw_row - SKULL[3])


def read(name, d, h, only):
    """The pose -> (figure, the head box's top-left in it, the figure's top-left square on the pack's grid)."""
    if name in WALK:
        a, head_box = walk_frame(name, d)
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"scar-pose-{name}.png"))).convert("RGBA")).copy()
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    pad = 20
    big = np.pad(a, ((pad, pad), (pad, pad), (0, 0)))
    if name in WALK:                                              # the design head where the raw head was
        hy, hx = np.nonzero(h[..., 3] > 0)
        py, px = hy + head_box[1] + pad, hx + head_box[0] + pad
        pasted = np.zeros(big.shape[:2], bool)
        pasted[py, px] = True
        for y in range(py.min() - 4, py.max() + 5):
            for x in range(px.min() - 4, px.max() + 5):
                if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                    big[y, x] = 0
        big[py, px] = h[hy, hx]
        head_at = (head_box[0] + pad, head_box[1] + pad)
    elif name in HEAD_CENTRE:
        hd = np.rot90(h, TURN.get(name, 0)).copy()
        cx, cy = HEAD_CENTRE[name]
        hx0 = int(round(cx - (hd.shape[1] - 1) / 2)) + pad
        hy0 = int(round(cy - (hd.shape[0] - 1) / 2)) + pad
        hy, hx = np.nonzero(hd[..., 3] > 0)
        py, px = hy + hy0, hx + hx0
        pasted = np.zeros(big.shape[:2], bool)
        pasted[py, px] = True
        for y in range(py.min() - 3, py.max() + 4):
            for x in range(px.min() - 3, px.max() + 4):
                if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                    big[y, x] = 0
        big[py, px] = hd[hy, hx]
        head_at = (hx0, hy0)
    else:
        o = manifest()[name]["head"]["origin"]
        head_at = (o[0] + pad, o[1] + pad)
    big = close_gaps(big, d)
    op = big[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            big[lb == j] = 0
    ys, xs = np.nonzero(big[..., 3] > 0)
    oy, ox = ys.min(), xs.min()
    return (big[oy:ys.max() + 1, ox:xs.max() + 1], (int(head_at[0] - ox), int(head_at[1] - oy)),
            (int(ox - pad), int(oy - pad)))


def big4(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    d, h = design(), head()
    only = head_colours(d, h)
    figs = {}
    for n in names:
        fig, at, grid = read(n, d, h, only)
        figs[n] = (fig, at, grid)
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, head box at {at}, on the grid at {grid}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", d)] + [(n, figs[n][0]) for n in names]
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"scar_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, grid) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [at[0], at[1]], "grid_at": [grid[0], grid[1]]}, fh)


if __name__ == "__main__":
    main()
