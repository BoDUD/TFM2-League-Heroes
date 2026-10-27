#!/usr/bin/env python3
"""Vander's Codex poses (assets/source/vander/codex_poses: POSE_PROMPTS.md, 15 key poses of his own TFT clips on
his design, 2026-10-27) on the design's palette, at the design's scale, with the design's own head pasted in (one face
in all frames), gaps closed.

    python tools/art/design_vander_poses.py --measure        # each pose's scale and head match
    python tools/art/design_vander_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_vander_poses.py                  # writes assets/source/vander/hd/pose_<name>.png (+ .json)

Loris's way (design_loris_poses.py): Codex delivered on the asked grid (12 px squares from the canvas corner, the
soles on y 1176) and mapped to the design's colours itself (its HANDOFF), at sizes that drift. Each pose is read one
pixel a square, every colour taken to the nearest of the design's in Lab, brought to the scale below, and the
design's head box (POLY: the hair, the face and the beard, not the jacket's collar under it) pasted where most of its
squares' colours match; Codex's own head squares round it that the paste did not lay cleared where they are head-only
colours, loose specks dropped and the small holes and cracks closed (design_silco_poses.close_gaps).
Each pose's json keeps where the head box went (its top-left square), the scale and where the figure's top-left square
was on Codex's 12 px grid (grid_at): Codex drew every pose where its reference put it, so rig_vander places them by it.
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
from design_vander_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import pack_vander_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vander", "codex_poses", "vander-poses")
# the run redrawn (RUN_PROMPTS.md, after the review's 「跑步姿势不像啊」): 8 frames of his TFT run on 9 px squares
RUN_SRC = os.path.join(ROOT, "assets", "source", "vander", "codex_run", "vander-run")
RUN_SQ = 9
RUN_NAMES = [f"run{k}" for k in range(1, 9)]
SKIN = [(249, 193, 144), (250, 173, 122), (204, 105, 80), (158, 107, 93)]      # the design face's skin
FACE_SIDE = 8                    # columns beside the pasted head where a run frame's own face is looked for
HAIR = [(64, 32, 34), (87, 76, 78), (39, 18, 28), (131, 131, 136), (148, 148, 182)]   # the design's hair (rows 0-6)
HAIR_BACK = 14                   # columns behind the pasted head where a run frame's own hair is looked for
FACE_LOW = 6                     # the head's lowest rows, where the jacket's collar and shoulder meet the beard
OUT = os.path.join(ROOT, "assets", "source", "vander", "hd")
SQ = 12
# the hair, the face and the beard in hd/idle.png (x, y) - not the jacket's collar under the beard
POLY = [(47.0, 0.0), (55.0, 0.0), (61.0, 2.0), (62.5, 5.0), (62.0, 7.0), (62.0, 11.0), (61.0, 13.0), (60.5, 16.0),
        (59.5, 19.0), (57.0, 21.5), (51.0, 21.5), (47.0, 20.0), (45.0, 19.0), (42.0, 18.0), (41.0, 14.0), (41.0, 6.0),
        (42.0, 3.0), (44.0, 1.0)]
SCALES = [1.0]
# a head-match scale search (0.80-1.05) put most bodies at 1.0 (Codex's heads as big as the design's), q_guard at 0.90
# (drawn 14 % over its reference)
STAND = {}
SCALE = {"q_guard": 0.90}
# the run drawn as tall as his model running (~125 rows to the design's 80: 「怎么体型现在这么大啊 跑步的时候」): 0.75,
# ~90 rows, the pasted head the design's own size
RUN_SCALE = 0.75
SCALE.update({n: RUN_SCALE for n in RUN_NAMES})
DEFAULT = 1.0
TURN = {}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
NAMES = [n for n in PK.POSES if not n.startswith("run")] + RUN_NAMES


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def palette(d):
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    return cols, srgb2lab(cols.astype(float) / 255.0)


def pose(name, d):
    """The pose one pixel a square, every colour the nearest of the design's, cropped -> (figure, its top-left square
    on Codex's grid)."""
    if name in RUN_NAMES:
        a = np.asarray(Image.open(lp(os.path.join(RUN_SRC, f"vander-run-{name}.png"))).convert("RGBA"))
        g = a[RUN_SQ // 2::RUN_SQ, RUN_SQ // 2::RUN_SQ].copy()
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, f"vander-pose-{name}.png"))).convert("RGBA"))
        g = a[SQ // 2::SQ, SQ // 2::SQ].copy()
    op = g[..., 3] > 0
    cols, lab = palette(d)
    src = g[op][:, :3]
    uniq, inv = np.unique(src, axis=0, return_inverse=True)
    ul = srgb2lab(uniq.astype(float) / 255.0)
    near = np.argmin(((ul[:, None, :] - lab[None, :, :]) ** 2).sum(-1), axis=1)
    g[op, :3] = cols[near[inv.ravel()]]
    g[..., 3] = np.where(op, 255, 0)
    ys, xs = np.nonzero(op)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (int(xs.min()), int(ys.min()))


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def scaled(fig, k):
    h, w = fig.shape[:2]
    im = Image.fromarray(fig).resize((max(1, round(w * k)), max(1, round(h * k))), Image.NEAREST)
    return np.asarray(im).copy()


def match(fig, d, hm):
    """The offset (dx, dy) of the design's head in `fig` with the most squares of the same colour -> (dx, dy, share)."""
    ys, xs = np.nonzero(hm)
    want = d[ys, xs]
    best = (0, 0, -1.0)
    H, W = fig.shape[:2]
    for dy in range(-ys.min(), H - ys.max()):
        for dx in range(-xs.min(), W - xs.max()):
            got = fig[ys + dy, xs + dx]
            share = float(np.all(got == want, axis=1).mean())
            if share > best[2]:
                best = (dx, dy, share)
    return best


def head_colours(d, hm):
    """The colours only the head uses: not shared with the body, the gauntlet or the outline."""
    head = {tuple(c) for c in d[hm][:, :3]}
    rest = {tuple(c) for c in d[~hm & (d[..., 3] > 0)][:, :3]}
    return head - rest


def fit(name, d, hm, scale=None):
    """The pose at the scale its head matches best -> (figure, scale, dx, dy, share, its top-left on Codex's grid: a
    scaled pose grown about its bottom middle)."""
    raw, (gx, gy) = pose(name, d)
    best = None
    for k in ([scale] if scale else SCALES):
        fig = scaled(raw, k)
        dx, dy, share = match(fig, d, hm)
        if best is None or share > best[4]:
            at = (gx + (raw.shape[1] - fig.shape[1]) / 2, gy + raw.shape[0] - fig.shape[0])
            best = (fig, float(k), dx, dy, share, at)
    return best


def read(name, scale=None):
    """The pose with the design's head -> (figure, the head box's top-left square in it, scale, the match share, the
    figure's top-left square on Codex's grid)."""
    d = design()
    hm = head_mask(d)
    if scale is None:
        scale = STAND[name] / pose(name, d)[0].shape[0] if name in STAND else SCALE.get(name, DEFAULT)
    fig, k, dx, dy, share, (gx, gy) = fit(name, d, hm, scale)
    pad = 6
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    ys, xs = np.nonzero(hm)
    head = np.zeros_like(d)
    head[hm] = d[hm]
    y0_, x0_ = ys.min(), xs.min()
    head = head[y0_:ys.max() + 1, x0_:xs.max() + 1]
    if name in TURN:   # the head box turned about its middle, where the upright one matched
        cy, cx = dy + y0_ + (head.shape[0] - 1) / 2, dx + x0_ + (head.shape[1] - 1) / 2
        head = np.flipud(np.rot90(head, -1)) if TURN[name] == "up" else np.rot90(head, TURN[name])
        dy, dx = int(round(cy - (head.shape[0] - 1) / 2)) - 0, int(round(cx - (head.shape[1] - 1) / 2))
        y0_, x0_ = 0, 0
    hy, hx = np.nonzero(head[..., 3] > 0)
    ys, xs = hy + y0_, hx + x0_
    py, px = ys + dy + pad, xs + dx + pad
    pasted = np.zeros(big.shape[:2], bool)
    pasted[py, px] = True
    only = head_colours(d, hm)
    y0, y1, x0, x1 = py.min() - 3, py.max() + 4, px.min() - 3, px.max() + 4
    for y in range(max(0, y0), min(big.shape[0], y1)):
        for x in range(max(0, x0), min(big.shape[1], x1)):
            if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                big[y, x] = 0
    if name in RUN_NAMES:
        drop_old_face(big, pasted, d)
    big[py, px] = head[hy, hx]
    big = close_gaps(big, d)
    op = big[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            big[lb == j] = 0
    ys2, xs2 = np.nonzero(big[..., 3] > 0)
    oy, ox = ys2.min(), xs2.min()
    at = (int(xs.min() + dx + pad - ox), int(ys.min() + dy + pad - oy))
    grid = (round(float(gx + ox - pad), 1), round(float(gy + oy - pad), 1))
    return big[oy:ys2.max() + 1, ox:xs2.max() + 1], at, k, share, grid


def drop_old_face(big, pasted, d):
    """A run frame's own face where the pasted head does not cover it (Codex drew the run's heads off the paste's
    place: a second nose and cheek showed beside the design's, and its own hair round the pasted one - the user:
    「头发不干净吧？」): its skin squares round the pasted head go, everything in front of the face and over the head,
    the hair's colours behind it, then the outline squares left hanging there (no opaque square but outline beside
    them), in place."""
    ys, xs = np.nonzero(pasted)
    y0, y1, x0, x1 = ys.min() - 3, ys.max() - 1, xs.min() - FACE_SIDE, xs.max() + FACE_SIDE + 1
    win = np.zeros(pasted.shape, bool)
    win[max(0, y0):y1, max(0, x0):x1] = True
    loose_win = np.zeros(pasted.shape, bool)
    loose_win[:ys.max() + 1, max(0, xs.min() - HAIR_BACK):x1] = True
    rgb = big[..., :3]
    skin = np.zeros(pasted.shape, bool)
    for c in SKIN:
        skin |= np.all(rgb == c, axis=-1)
    big[win & ~pasted & skin & (big[..., 3] > 0)] = 0
    # in front of the face, over the jacket's shoulder (the head's rows but its lowest FACE_LOW): nothing but the head
    for y in range(max(0, y0), ys.max() + 1 - FACE_LOW):
        row = xs[ys == y]
        edge = row.max() if row.size else xs.max()
        big[y, edge + 1:x1] = 0
    # its own hair: over the pasted head nothing; behind it (image left, the same rows) the hair's colours
    big[:ys.min()] = 0
    hair = np.zeros(pasted.shape, bool)
    for c in HAIR:
        hair |= np.all(rgb == c, axis=-1)
    for y in range(ys.min(), ys.max() + 1 - FACE_LOW):
        row = xs[ys == y]
        edge = row.min() if row.size else xs.min()
        lo = max(0, edge - HAIR_BACK)
        cut = hair[y, lo:edge] & ~pasted[y, lo:edge]
        big[y, lo:edge][cut] = 0
    # beside the beard (the head's lowest FACE_LOW rows, where the jacket meets it): the hair's (and beard's) colours
    for y in range(ys.max() + 1 - FACE_LOW, ys.max() + 1):
        row = xs[ys == y]
        edge = row.max() if row.size else xs.max()
        cut = hair[y, edge + 1:x1] & ~pasted[y, edge + 1:x1]
        big[y, edge + 1:x1][cut] = 0
    ink = tuple(PD.edge_colour(d))
    for _ in range(4):
        op = big[..., 3] > 0
        line = op & np.all(rgb == ink, axis=-1)
        solid = np.pad(op & ~line, 1)
        near = solid[:-2, 1:-1] | solid[2:, 1:-1] | solid[1:-1, :-2] | solid[1:-1, 2:]
        loose = loose_win & ~pasted & line & ~near
        if not loose.any():
            break
        big[loose] = 0


def big4(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {}
    for n in names:
        fig, at, k, share, grid = read(n)
        figs[n] = (fig, at, k, share, grid)
        print(f"{n:9s} scale {k:.2f}, head {share:5.1%} of its squares as drawn -> {fig.shape[1]} x {fig.shape[0]}, "
              f"head box at {at}")
    if a.measure:
        return
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
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
            path = os.path.join(a.sheet, f"vander_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, k, share, grid) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])], "scale": round(k, 2), "share": round(share, 3),
                       "grid_at": [grid[0], grid[1]]}, fh)


if __name__ == "__main__":
    main()
