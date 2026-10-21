#!/usr/bin/env python3
"""Ornn's Codex poses (assets/source/ornn/codex_poses: POSE_PROMPTS.md, fourteen of League's whole-body poses and four
run frames on skeletons) read back at the design's scale, in its colours, with the design's own face.

    python tools/art/design_ornn_poses.py --sheet DIR        # all poses beside the design (5x) and at game size
    python tools/art/design_ornn_poses.py                    # writes assets/source/ornn/hd/pose_<name>.png

Codex drew about the 16 px asked (2026-10-21; its HANDOFF: no exact grid, half-transparent edges), so one scale for
all: the median over the upright poses of the eye-to-sole height (Codex px) over the design's 41.5 squares. (Each pose
at its own eye-to-sole scale was tried: impact and stagger, rearing up and leaning back, shrank to 58 rows and summon
grew to 84 - the eye height is no measure for them; on one grid they stand 66-76 rows like the idle.) The eyes are
the pair of glowing yellow blobs at about one height (20 px: stagger's head leans back) 55-110 px apart (the molten arm's yellow lies in long cracks, lower).
Each pose is sampled on that grid from the figure's top-left (design_chogath_poses.sample), every colour snapped to the
design's own (Lab), the outline closed. One face in all frames (memory one-face-all-frames): the design's face (the mane,
the eyes, the nose, the beard and its rings - not the horns, which Codex drew turned with each pose) laid with its near
eye on Codex's near eye. Not in `TURNED` (charge, headbutt, lie): there the head is turned down or lies on its side,
and the upright face would not fit - Codex's own face stays.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_poses import sample  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_ornn_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ornn", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "ornn", "hd")
NAMES = ["raise", "smash", "q_raise", "q_slam", "breath", "charge", "impact", "summon", "call", "butt_wind",
         "headbutt", "stagger", "kneel", "lie", "run1", "run2", "run3", "run4"]
DESIGN_NEAR_EYE = (44.5, 24.0)  # (x, y) of the near eye's middle in hd/idle.png (the far one at (50, 24))
DESIGN_EYE_TO_SOLE = 41.5       # squares from the eyes' middle to the soles' bottom edge in the design
UPRIGHT = ["breath", "impact", "summon", "stagger", "run1", "run2", "run3", "run4"]
TURNED = ["charge", "headbutt", "lie"]
# the design's face (mane, eyes, nose, beard and its rings) as a polygon in design squares (x, y) on hd/idle.png
FACE_POLY = [(37, 18), (56, 18), (60, 22), (60, 33), (57, 38), (52, 41), (44, 41), (38, 37), (35, 29), (35, 21)]


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"ornn-pose-{name}.png"))).convert("RGBA"))


def eyes_px(a):
    """Codex's eyes: (x, y) of the near (left) and the far one - the highest pair of yellow blobs at one height."""
    rgb = a[..., :3].astype(int)
    m = (a[..., 3] >= 128) & (rgb[..., 0] > 230) & (rgb[..., 1] > 190) & (rgb[..., 2] < 140)
    lb, k = ndimage.label(m)
    blobs = []
    for i in range(1, k + 1):
        b = lb == i
        if 60 <= b.sum() <= 700:
            ys, xs = np.nonzero(b)
            blobs.append((xs.mean(), ys.mean()))
    pairs = [(p, q) for p in blobs for q in blobs if 55 <= q[0] - p[0] <= 110 and abs(q[1] - p[1]) <= 20]
    if not pairs:
        return None
    # the pair nearest the body's middle column (a raised molten fist has yellow pairs too, off to the side)
    mid = float(np.median(np.nonzero(a[..., 3] >= 128)[1]))
    return min(pairs, key=lambda pq: abs((pq[0][0] + pq[1][0]) / 2 - mid))


def scale_of(name):
    a = raw(name)
    (ex, ey), _ = eyes_px(a)
    ys = np.nonzero(a[..., 3] >= 128)[0]
    return (ys.max() + 1 - ey) / DESIGN_EYE_TO_SOLE


def common_scale():
    return float(np.median([scale_of(n) for n in UPRIGHT]))


def face_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(FACE_POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def with_face(fig, idle, dy, dx):
    m = face_mask(idle)
    ys, xs = np.nonzero(m)
    pad = 20
    out = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    out[ys + dy + pad, xs + dx + pad] = idle[ys, xs]
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def finish(fig):
    """The outline closed; single enclosed holes the readback left take the outline."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1:
            pad[h] = (*ink, 255)
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def read(name, idle, sc):
    a = raw(name)
    fig = snap(sample(a, sc), idle)
    eyes = eyes_px(a)
    if name in TURNED or eyes is None:
        return finish(fig), eyes is not None
    ys, xs = np.nonzero(a[..., 3] >= 128)
    (ex, ey), _ = eyes
    dy = int(round((ey - ys.min()) / sc - 0.5 - DESIGN_NEAR_EYE[1]))
    dx = int(round((ex - xs.min()) / sc - 0.5 - DESIGN_NEAR_EYE[0]))
    return finish(with_face(fig, idle, dy, dx)), True


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    sc = common_scale()
    print(f"scale {sc:.2f} Codex px a square (upright poses: " +
          ", ".join(f"{n} {scale_of(n):.2f}" for n in UPRIGHT) + ")")
    figs = {}
    for n in NAMES:
        fig, eyed = read(n, idle, sc)
        figs[n] = fig
        print(f"{n:10s} {fig.shape[1]:3d} x {fig.shape[0]:3d}" + ("" if eyed else "  (no eyes found)") +
              ("  (Codex's own face)" if n in TURNED else ""))
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z, gap = 5, 12
        cells = [("idle", idle)] + list(figs.items())
        cols = 5
        W = max(f.shape[1] for _, f in cells) * z + gap
        H = max(f.shape[0] for _, f in cells) * z + gap + 16
        rows = (len(cells) + cols - 1) // cols
        can = Image.new("RGBA", (cols * W, rows * H), (200, 205, 195, 255))
        dr = ImageDraw.Draw(can)
        for i, (n, f) in enumerate(cells):
            x, y = (i % cols) * W, (i // cols) * H
            dr.text((x + 4, y + 2), n, fill=(20, 20, 20, 255))
            im = big(f, z)
            can.alpha_composite(im, (x, y + H - gap - im.height))
        can.convert("RGB").save(lp(os.path.join(a.sheet, "ornn_poses_readback.png")))
        print(os.path.join(a.sheet, "ornn_poses_readback.png"))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, f in figs.items():
        Image.fromarray(f).save(lp(os.path.join(OUT, f"pose_{n}.png")))


if __name__ == "__main__":
    main()
