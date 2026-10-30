#!/usr/bin/env python3
"""Idas's Codex poses (assets/source/idas/codex_poses: POSE_PROMPTS.md, 11 key poses of her own TFT clips on her design,
2026-10-30) read back on 7 px squares, on the design's palette, gaps closed.

    python tools/art/design_idas_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_idas_poses.py                  # writes assets/source/idas/hd/pose_<name>.png (+ .json)

Codex did not keep the asked grid (its HANDOFF and validation.json: soft alpha, each pose on its own 5-8 px squares,
regrid.square_size per pose 2026-10-30) nor the ground line, but drew every figure at about the design's size on the
canvas, about 1.22x its reference (SQ). So each pose is read back on its own squares (regrid), brought to SQ px squares (pixel_down.pixelate through the pivot), its colours
snapped to the design's own (nearest in Lab), the one-square cracks and small holes closed (design_silco_poses.close_gaps)
and loose specks dropped. Each pose's json keeps where PIVOT fell in it: x = the pack's root column on the canvas
(pack_idas_poses: the design centred on whole squares, her root on its column 63.1 -> canvas x 624; Codex placed the
bodies over their references, roughly), y = the pose's own lowest square (it stands where it was drawn, not on the pack's line).
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
import pack_idas_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
from design_idas_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "idas", "codex_poses", "idas-poses")
OUT = os.path.join(ROOT, "assets", "source", "idas", "hd")
# the pack's root column on the canvas (pack_idas_poses prints "pelvis column 63.1": canvas x 182 + 63.1 x 7), in squares
PIVOT_X = 624 / (7.0 * 1.22)
# the squares a pose is read on: Codex drew every figure about 1.22x its reference (the figures' heights against the
# pack's refs, 1.08-1.39, mean 1.22, measured 2026-10-30), and the refs are at the design's scale (7 px a square)
SQ = 7.0 * 1.22
SPECK = 6                     # parts apart from the figure smaller than this are dropped
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


# the inside of her open mouth (MOUTH_POSES): Codex's crimson, a colour the design (mouth shut) does not have - its
# three shades measured on the three raws (squares red with almost no green, 2026-10-30); kept only on a red patch of
# MOUTH_MIN squares or more in those poses, so the reddish dark browns Codex scattered over her body (a_wind had 27
# squares of them) stay the design's browns
MOUTH = np.array([(69, 1, 13), (101, 4, 18), (140, 5, 24)])
MOUTH_POSES = ("q_breath", "e_roar", "r_burst")
MOUTH_MIN = 8


def mouth(a):
    """The squares of a frame that are the open mouth's crimson: red patches of MOUTH_MIN squares or more."""
    c = a[..., :3].astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    red = (a[..., 3] > 0) & (r > 60) & (g < 35) & (b > 8) & (b < 90) & (r > b + 40)
    lb, n = ndimage.label(red, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(red, lb, range(1, n + 1))
    return np.isin(lb, [j + 1 for j in range(n) if sizes[j] >= MOUTH_MIN])


def snap(a, d, open_mouth=False):
    """Every opaque square to the nearest of the design's colours (in Lab); with open_mouth, the mouth's crimson to
    MOUTH."""
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    m = mouth(a) if open_mouth else np.zeros(a.shape[:2], bool)
    out = np.zeros_like(a)
    for sel, p in ((a[..., 3] > 0) & ~m, pal), (m, MOUTH):
        if not sel.any():
            continue
        lab_p = PD._lab(p.astype(float))
        lab_a = PD._lab(a[sel][:, :3].astype(float))
        idx = np.argmin(((lab_a[:, None, :] - lab_p[None, :, :]) ** 2).sum(-1), axis=1)
        out[sel, :3] = p[idx]
        out[sel, 3] = 255
    return out


def read(name):
    """The pose on the design's palette -> (figure, PIVOT's square in it)."""
    d = design()
    raw = np.asarray(Image.open(lp(os.path.join(SRC, f"idas-pose-{name}.png"))).convert("RGBA")).copy()
    a, sq, (bx, _by) = RG.regrid(raw)   # on Codex's own squares of this pose (5-8 px)
    a = a.copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    # ... then brought to SQ px squares through the pivot (the pack's root column, the pose's lowest square)
    # (the squares on the design's colours first: pixelate's own palette, the 64 commonest, was all golds - the cyan
    # crest and the grey claws went gold)
    a = snap(a, d, name in MOUTH_POSES)
    pal = np.concatenate([np.unique(d[d[..., 3] > 0][:, :3], axis=0), MOUTH]).astype(float)
    a, (pvx, pvy) = PD.pixelate(a, sq / SQ, ((PIVOT_X * SQ - bx[0]) / sq, a.shape[0]), PD.edge_colour(d), pal=pal)
    a = a.copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    g = close_gaps(snap(a, d, name in MOUTH_POSES), d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (int(pvx - xs.min()), int(ys.max() - ys.min()))


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
    figs = {n: read(n) for n in names}
    for n, (fig, piv) in figs.items():
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}")
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
            path = os.path.join(a.sheet, f"idas_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]]}, fh)


if __name__ == "__main__":
    main()
