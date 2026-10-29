#!/usr/bin/env python3
"""Renni's Codex poses (assets/source/renni/codex_poses: POSE_PROMPTS.md, 19 key poses of her own TFT clips on her
design, 2026-10-29) as game pictures: on the design's colours, the design's head where Codex drew her standing, specks
dropped and gaps closed.

    python tools/art/design_renni_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_renni_poses.py                  # writes assets/source/renni/hd/pose_<name>.png (+ .json)

Codex delivered 1254 px canvases on exact 12 px squares from the canvas corner (every 12 x 12 block one colour, its
manifest's grid_px), so most poses are read square for square, one pixel a square, on the pose pack's own grid. Three it
shrank to fit the canvas (manifest fit_scale 0.94 to 0.97: the saw raised over her head), resampling their colours to
mush: those are read from its raw drafts instead (RAW: the square that makes Codex's head the design's head's size -
the head template matched best there), placed across by their feet on the shrunk picture's feet.
Every square then takes the nearest of the design's 36 colours. The design's head (HEAD_BOX of hd/idle.png, its
squares only: no collar, no feathers) goes where it matches Codex's head best, over it; Codex's hair and face squares
left round it are cleared. The falls keep Codex's own head (tilted with her body, the face readable at 10x,
2026-10-29): the design's upright head would not lie down with her.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
from design_renni_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import pack_renni_poses as PK  # noqa: E402
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renni", "codex_poses", "renni-poses")
OUT = os.path.join(ROOT, "assets", "source", "renni", "hd")
NAMES = list(PK.POSES)
SQ = 12                                   # Codex's squares on the delivered canvases
RAW = {"r_heave": 11.2, "r_hold": 11.2}   # read from raw/ on squares of this many raw px
KEEP_HEAD = ("d_fall", "d_down")          # Codex's own head, tilted with her
HEAD_BOX = (22, 0, 50, 32)                # x0, y0, x1, y1 on hd/idle.png: the head, its collar and what is round them
FACE_AT = (40, 15)                        # a square of her face (hd/idle.png): the head is the part joined to it
# the collar comes with the head (rows 28-31): it covers Codex's own chin when its face ran longer than the design's
NOT_HEAD = ("#186840", "#1B484C", "#122008", "#1A8D2C",   # the feathers
            "#433771", "#21243A", "#8C5215", "#C07C24", "#E9A638")   # the gloves, the straps and buckles
HAIR_FACE = ("#900F1A", "#C11F1E", "#FA4A24", "#FBF0DD", "#FCC8A7", "#F3A48A", "#B35B4C")   # only on a head
NEAR = 3                                  # Codex's hair / face squares this close to the pasted head are cleared
SPECK = 6                                 # parts apart from the figure smaller than this are dropped
MATCH = 45                                # a head square agrees within this RGB distance


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA")).copy()


def head(d):
    """(the design's head squares in HEAD_BOX, its mask): the part joined to her face, no feathers, collar or glove."""
    x0, y0, x1, y1 = HEAD_BOX
    box = d[y0:y1, x0:x1].copy()
    ex = {rgb(c) for c in NOT_HEAD}
    ok = (box[..., 3] > 0) & ~np.array([[tuple(p[:3]) in ex for p in r] for r in box])
    lab, _ = ndimage.label(ok)
    m = lab == lab[FACE_AT[1] - y0, FACE_AT[0] - x0]
    box[~m] = 0
    return box, m


def snap(a, pal):
    """Every square the nearest design colour, alpha 0 / 255."""
    out = np.zeros_like(a)
    op = a[..., 3] >= 128
    px = a[op][:, :3].astype(int)
    k = ((px[:, None, :] - pal[None].astype(int)) ** 2).sum(-1).argmin(1)
    out[op, :3] = pal[k]
    out[op, 3] = 255
    return out


def feet_x(a):
    """The middle column of the lowest 3 rows."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    low = ys >= ys.max() - 2
    return xs[low].mean()


def read_grid(name):
    """(the pose one pixel a square, its top-left square on the pack's grid)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"renni-pose-{name}.png"))).convert("RGBA"))
    one = a[SQ // 2::SQ, SQ // 2::SQ].copy()
    if name not in RAW:
        return one, (0, 0)
    r = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"renni-pose-{name}.png"))).convert("RGBA")).copy()
    fig, _, _ = RG.regrid(r, RAW[name])
    op = fig[..., 3] >= 128
    ys, xs = np.nonzero(op)
    fig = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # across: its feet on the shrunk picture's feet; down: its soles on the shrunk picture's (the ground)
    oys = np.nonzero((one[..., 3] >= 128).any(1))[0]
    left = round(feet_x(one) - feet_x(fig))
    top = int(oys.max()) + 1 - fig.shape[0]
    return fig, (left, top)


def match(fig, h, m):
    """Where the design's head (h, mask m) agrees best with fig: (score, x, y)."""
    P = fig.astype(int)
    H = h.astype(int)
    hh, hw = m.shape
    best = (-9.0, 0, 0)
    for y in range(-6, P.shape[0] - hh + 1):
        for x in range(-6, P.shape[1] - hw + 1):
            y0, x0 = max(0, y), max(0, x)
            win = P[y0:y + hh, x0:x + hw]
            sub_m = m[y0 - y:y0 - y + win.shape[0], x0 - x:x0 - x + win.shape[1]]
            sub_h = H[y0 - y:y0 - y + win.shape[0], x0 - x:x0 - x + win.shape[1]]
            op = win[..., 3] > 0
            agree = sub_m & op & (np.sqrt(((win[..., :3] - sub_h[..., :3]) ** 2).sum(-1)) < MATCH)
            s = (agree.sum() - 0.5 * (sub_m & ~op).sum() - 0.5 * (m.sum() - sub_m.sum())) / m.sum()
            if s > best[0]:
                best = (s, x, y)
    return best


def lay_head(fig, h, m, x, y):
    """The design's head over fig at (x, y) (fig grown if it runs off), Codex's hair and face squares within NEAR of
    it cleared. Returns (fig, the head's top-left in fig)."""
    hh, hw = m.shape
    pl, pt = max(0, -x), max(0, -y)
    pr, pb = max(0, x + hw - fig.shape[1]), max(0, y + hh - fig.shape[0])
    fig = np.pad(fig, ((pt, pb), (pl, pr), (0, 0)))
    x, y = x + pl, y + pt
    mask = np.zeros(fig.shape[:2], bool)
    mask[y:y + hh, x:x + hw] = m
    near = ndimage.binary_dilation(mask, iterations=NEAR) & ~mask
    hf = {rgb(c) for c in HAIR_FACE}
    old = near & np.array([[tuple(p[:3]) in hf and p[3] > 0 for p in r] for r in fig])
    fig[old] = 0
    fig[mask] = h[m]
    return fig, (x, y)


def drop_specks(fig):
    op = fig[..., 3] > 0
    lab, n = ndimage.label(op)
    if n > 1:
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        for j in range(1, n + 1):
            if sizes[j - 1] < SPECK:
                fig[lab == j] = 0
    return fig


def read(name, d, h, m, pal):
    fig, grid = read_grid(name)
    fig = snap(fig, pal)
    score, x, y = match(fig, h, m)
    if name not in KEEP_HEAD:
        fig, (x, y) = lay_head(fig, h, m, x, y)
        grid = (grid[0] - max(0, -x), grid[1] - max(0, -y))
    fig = close_gaps(drop_specks(fig), d)
    ys, xs = np.nonzero(fig[..., 3] > 0)
    oy, ox = int(ys.min()), int(xs.min())
    return (fig[oy:ys.max() + 1, ox:xs.max() + 1], (int(x - ox), int(y - oy)), (int(grid[0] + ox), int(grid[1] + oy)),
            score)


def big(a, z):
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
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    h, m = head(d)
    figs = {}
    for n in names:
        fig, at, grid, score = read(n, d, h, m, pal)
        figs[n] = (fig, at, grid)
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, head match {score:.2f} at {at}, on the grid at {grid}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", d)] + [(n, figs[n][0]) for n in names]
        rows = [tiles[i:i + 5] for i in range(0, len(tiles), 5)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"renni_poses_{j}.png")
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
