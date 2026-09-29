#!/usr/bin/env python3
"""Tidy Codex's round-2 strips of Lucian (assets/source/lucian/MODEL_PROMPTS.md) into the native strips.

    python tools/art/tidy_lucian.py <Codex's delivery folder>

Codex delivered lucian_native.png (the approved design B with the head traced from League, U3) and ten strips on
the reference cells (96x96 game pixels, every pixel an 8x8 block, 25-26 colours, the design's head copied into
every upright frame, nothing under the feet line but the dive and the fall). One thing read wrong and is fixed
here, on the game pixels, before the strips are written to assets/source/native/:
  - the move: Codex drew League's slim run silhouette under the stocky design, so while he ran the body was about
    two thirds of every other strip's (339 opaque pixels a frame against 460-566; legs one or two pixels wide,
    the torso six) and the head read too big for it. From WIDEN_FROM rows above the pivot down, every row is
    stretched across about the body's middle column, the stretch growing over RAMP rows to WIDEN and easing off
    again over the hips toward WIDEN_TO (the gun arm and the head above, and the legs below, stay as drawn: the
    dark trousers, stretched too, ran into one mass), and a fresh 1-pixel outline is drawn round the result
    (outline pixels inside the body, the seams between legs and coat, stay).
  - Piercing Light: the pack asked for the pistols at belt height in frames 4-5 (a LineRangeProjectile's picture
    sits at the pivot's height), so he fired from the waist; the user: League fires it from the pistols held out at
    shoulder height. Frames 4 and 5 become frame 3 (Codex's League pose: both pistols forward, the front muzzle
    20 px ahead of the pivot and 11-13 px above it), placed on their own pivots; frame 4 keeps its muzzle flash,
    moved from the lowered pistol to that muzzle. The beam's picture now rides a projectile raised to the muzzle
    (the kit's q_ray).
The rest is used as delivered. Then run import_native.py --hero lucian (EYES steadies idle and run on the green
irises, the one colour nothing else uses).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z, CELL = 8, 96
TAGS = ["idle", "run", "attack", "passive", "skill", "skill2", "skill2_back", "ult", "hit", "dead"]
OUTLINE = (20, 14, 18)
WIDEN = {"run": 1.3}           # tag: the stretch across, reached RAMP rows under WIDEN_FROM
WIDEN_FROM = -6                # rows from the pivot: the chest, under the arm that holds the pistols forward
WIDEN_TO = 3                   # ... down to the hips; the legs under it stay as drawn (stretched they ran together)
RAMP = 3
Q_AIM = 3                      # the Q frame with the pistols forward at shoulder height (1-based)
Q_FIRE = {4: True, 5: False}   # frames redrawn from it: True keeps the frame's own muzzle flash
FLASH_FROM = 6                 # in Codex's frame 4 everything from 6 px ahead of the pivot is the flash
MUZZLE = (21, -12)             # where the flash starts: just ahead of frame 3's front muzzle, from the pivot


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    return b[:, 0, :, 0].copy()


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def dilate(m):
    out = m.copy()
    out[1:] |= m[:-1]
    out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def widen(cell, pivot, factor):
    """The cell with its rows from WIDEN_FROM down stretched across about the body's middle column."""
    px, py = pivot
    y0 = py + WIDEN_FROM
    a = cell.copy()
    body = a[y0:]
    xs = np.nonzero((body[..., 3] > 0).any(0))[0]
    mid = (xs.min() + xs.max()) / 2
    new = np.zeros_like(body)
    for r in range(body.shape[0]):
        y = WIDEN_FROM + r
        f = 1 + (factor - 1) * max(0.0, min(1.0, (r + 1) / RAMP, (WIDEN_TO - y) / RAMP))
        for x in range(body.shape[1]):
            sx = int(round(mid + (x - mid) / f))
            if 0 <= sx < body.shape[1]:
                new[r, x] = body[r, sx]
    ink = (new[..., :3] == OUTLINE).all(-1) & (new[..., 3] > 0)
    solid = (new[..., 3] > 0) & ~ink
    seam = np.zeros_like(solid)
    seam[:, 1:-1] |= solid[:, :-2] & solid[:, 2:]
    seam[1:-1] |= solid[:-2] & solid[2:]
    keep = solid | (ink & seam)
    out = np.zeros_like(new)
    out[keep] = new[keep]
    ring = dilate(keep) & ~keep
    ring[0] = False                           # the row that meets the untouched part above keeps its pixels
    out[ring, :3] = OUTLINE
    out[ring, 3] = 255
    top = a[:y0]
    joined = np.concatenate([top, out], 0)
    # the untouched row above keeps an outline only where the widened body leaves it open below
    return joined


def cell_of(a, frames, k):
    cols = layout(len(frames))
    cx, cy = (k % cols) * CELL, (k // cols) * CELL
    return a[cy:cy + CELL, cx:cx + CELL]


def q_aim(a, frames):
    """Frames Q_FIRE redrawn as frame Q_AIM on their own pivots, frame 4's flash moved to the raised muzzle."""
    src = cell_of(a, frames, Q_AIM - 1).copy()
    sx, sy = frames[Q_AIM - 1]["pivot"]
    for f, flash in Q_FIRE.items():
        cell = cell_of(a, frames, f - 1)
        px, py = frames[f - 1]["pivot"]
        old = cell.copy()
        cell[:] = 0
        dx, dy = px - sx, py - sy
        ys, xs = np.nonzero(src[..., 3] > 0)
        ty, tx = ys + dy, xs + dx
        ok = (ty >= 0) & (ty < CELL) & (tx >= 0) & (tx < CELL)
        if not ok.all():
            sys.exit(f"skill frame {f}: frame {Q_AIM} does not fit round its pivot")
        cell[ty, tx] = src[ys, xs]
        if flash:
            ys, xs = np.nonzero(old[..., 3] > 0)
            keep = xs >= px + FLASH_FROM
            fy, fx = ys[keep], xs[keep]
            ox, oy = px + MUZZLE[0] - fx.min(), py + MUZZLE[1] - int(round((fy.min() + fy.max()) / 2))
            cell[fy + oy, fx + ox] = old[fy, fx]
            print(f"lucian_skill.png: frame {f} = frame {Q_AIM} + its flash ({len(fx)} pixels) at the muzzle")
        else:
            print(f"lucian_skill.png: frame {f} = frame {Q_AIM}")
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery", help="Codex's delivery folder (lucian_<tag>.png, lucian_native.png)")
    args = ap.parse_args()
    with open(G.lp(os.path.join(SRC, "lucian_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)["tags"]
    for name in ["native"] + TAGS:
        src = os.path.join(args.delivery, f"lucian_{name}.png")
        a = blocks(src)
        if name in WIDEN:
            frames = cells[name]
            cols = layout(len(frames))
            for k, fr in enumerate(frames):
                cx, cy = (k % cols) * CELL, (k // cols) * CELL
                a[cy:cy + CELL, cx:cx + CELL] = widen(a[cy:cy + CELL, cx:cx + CELL], fr["pivot"], WIDEN[name])
            before = (blocks(src)[..., 3] > 0).sum() / len(frames)
            print(f"lucian_{name}.png: rows from {WIDEN_FROM} widened x{WIDEN[name]}: "
                  f"{before:.0f} -> {(a[..., 3] > 0).sum() / len(frames):.0f} opaque pixels a frame")
        if name == "skill":
            a = q_aim(a, cells[name])
        Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"lucian_{name}.png")))
    print("wrote", len(TAGS) + 1, "images to assets/source/native/")


if __name__ == "__main__":
    main()
