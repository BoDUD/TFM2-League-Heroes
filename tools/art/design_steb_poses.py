#!/usr/bin/env python3
"""Steb's Codex poses (assets/source/steb/codex_poses: POSE_PROMPTS.md, 12 key poses of his own TFT clips on his
design, 2026-10-29) as game pictures: on the design's colours, the design's head where Codex drew him standing, specks
dropped and gaps closed (design_sevika_poses.py's way).

    python tools/art/design_steb_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_steb_poses.py                  # writes assets/source/steb/hd/pose_<name>.png (+ .json)

Codex delivered 1254 px canvases on exact 9 px squares from the canvas corner (every 9x9 cell one colour, alpha 0/255,
checked 2026-10-29), so every pose is read square for square, one pixel a square, on the pose pack's own grid. Every
square then takes the nearest of the design's colours. The design's head (HEAD_BOX of hd/idle.png: the part joined to
his face above his collar, no baton, no shoulder) goes where it matches Codex's head best, over it; Codex's hair and
face squares left round it are cleared. The falls keep Codex's own head (tilted with his body): the design's upright
head would not lie down with him.
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
from design_steb_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import pixel_down as PD  # noqa: E402
import pack_steb_poses as PK  # noqa: E402
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "steb", "codex_poses", "steb-poses")
OUT = os.path.join(ROOT, "assets", "source", "steb", "hd")
NAMES = list(PK.POSES)                    # the run is design_steb_run.py's (its own pack)
SQ = 9                                    # Codex's squares on the delivered canvases
RAW = {}                                  # read from raw/ on squares of this many raw px
# poses Codex drew a size off: brought to the design's by pixel_down about the soles' middle (from --probe)
SCALE = {}
KEEP_HEAD = ("d_down",)                  # Codex's own head, lying with him
HEAD_BOX = (35, 0, 63, 27)                # x0, y0, x1, y1 on hd/idle.png: the head, the chin on row 26
FACE_AT = (52, 20)                        # a square of his face (hd/idle.png): the head is the part joined to it
NECK_CUT = (21, 45)                       # rows from 21 left of column 45 are the shoulder and the baton, not the head
NOT_HEAD = ("#2B3873", "#3B2B2A", "#DA952D", "#F2AE37", "#6075A4", "#745635", "#FAE059", "#F7C545",   # the baton
            "#2E2A4A", "#BE7722", "#A46222", "#FBEC73", "#2F419B", "#2F1117", "#1D51D5", "#247EEF",   # gold, uniform
            "#C3A74A", "#7A6794")
HAIR_FACE = ("#2C6E7B", "#7ADDDA", "#64A78D", "#8FCFB0", "#DBF0DA", "#468472")   # his quiff, skin, ears
NEAR = 3                                  # Codex's hair / face squares this close to the pasted head are cleared
SPECK = 6                                 # parts apart from the figure smaller than this are dropped
MATCH = 45                                # a head square agrees within this RGB distance
SMALL = 12                                # an enclosed hole of this many squares or fewer is a pinhole


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA")).copy()


def head(d):
    """(the design's head squares in HEAD_BOX, its mask): the part joined to his face, no baton, collar or shoulder."""
    x0, y0, x1, y1 = HEAD_BOX
    box = d[y0:y1, x0:x1].copy()
    ex = {rgb(c) for c in NOT_HEAD}
    ok = (box[..., 3] > 0) & ~np.array([[tuple(p[:3]) in ex for p in r] for r in box])
    ok[NECK_CUT[0] - y0:, :NECK_CUT[1] - x0] = False
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"steb-pose-{name}.png"))).convert("RGBA"))
    one = a[SQ // 2::SQ, SQ // 2::SQ].copy()
    if name in SCALE:
        k = SCALE[name]
        ys, xs = np.nonzero(one[..., 3] > 0)
        cx, base = feet_x(one), ys.max() + 1
        g, _ = PD.pixelate(one, k, (cx, base), PD.edge_colour(one))
        # back on the pack's grid: the soles' middle and the ground where they were
        gy, gx = np.nonzero(g[..., 3] > 0)
        g = g[gy.min():gy.max() + 1, gx.min():gx.max() + 1]
        left = round(cx - feet_x(g))
        return g, (left, int(base) - g.shape[0])
    if name not in RAW:
        return one, (0, 0)
    r = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"steb-pose-{name}.png"))).convert("RGBA")).copy()
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
    fig = fill_thin(close_gaps(drop_specks(fig), d), d)
    ys, xs = np.nonzero(fig[..., 3] > 0)
    oy, ox = int(ys.min()), int(xs.min())
    return (fig[oy:ys.max() + 1, ox:xs.max() + 1], (int(x - ox), int(y - oy)), (int(grid[0] + ox), int(grid[1] + oy)),
            score)


def fill_thin(fig, d):
    """Clear holes the figure closes that are at most two squares thick or under SMALL squares (a sliver between an
    arm and the body, a pinhole: they read as missing squares, the user's 「我怎么看到像素缺失？」) take the outline
    colour; a real opening (the arms' loop over the head) stays clear."""
    op = fig[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    ink = tuple(PD.edge_colour(d))[:3] + (255,)
    out = fig.copy()
    for j in range(1, n + 1):
        c = lab == j
        if c.sum() <= SMALL or not ndimage.binary_erosion(c).any():
            out[c] = ink
    return out


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
            path = os.path.join(a.sheet, f"steb_poses_{j}.png")
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
