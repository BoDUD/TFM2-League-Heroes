#!/usr/bin/env python3
"""Kha'Zix's action strips: Codex's step-2 delivery (assets/source/khazix/codex_strips/) with the death redone.

    python tools/art/fix_khazix_strips.py [--check]

Codex re-posed the design's own parts (its HANDOFF: arms and claws cut out and turned whole by 45-degree steps, the
torso and legs square for square the design's, the head pasted in every frame) - the casting body is the idle's, as
the user's rule asks - and those strips go in as delivered. Its death did not: frames 3-4 tipped the body but kept the
head upright and left a leg hanging under it, and frames 5-8 stood the 90-degree figure on one leg instead of lying it
down (the user: 「完成下一步 有问题的地方你要灵活运用已有的工具来收尾」). DEAD rebuilds them as league_sivir's accepted
death (rig_samira.py's): frames 1-2 Codex's (struck, knocked back), then the WHOLE design turned 45 degrees back
(rigkit.turn, RotSprite, about the back foot), then a quarter turn counter-clockwise - on his back, the head to the
image left, the bent insect legs up at the right - first a row above the ground (the bounce), then on it.
Reads codex_strips/khazix_<tag>.png (8x) and khazix_cells.json, writes assets/source/native/khazix_<tag>.png (8x) and
khazix_cells.json for tools/art/import_native.py. --check only prints what would change.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "khazix", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(OUT, "khazix_native.png")
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99)
SOLES = 99
BACK_FOOT = (50.0, 99.0)         # the turn's joint: the back foot's heel on the ground
# the death, per frame: Codex's frame, ("tilt", degrees counter-clockwise, dx), ("lying", rows above the ground, dx);
# dx = where the box's centre lies from the standing point (he falls back: to the image left)
DEAD = ["codex", "codex", ("tilt", 45, -6), ("lying", 1, -8), ("lying", 0, -8), ("lying", 0, -8), ("lying", 0, -8),
        ("lying", 0, -8)]


def at1x(path):
    a = np.asarray(Image.open(path).convert("RGBA"))
    a = a[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def outline_colour(a):
    op = a[..., 3] > 0
    cols, n = np.unique(a[op][:, :3], axis=0, return_counts=True)
    return min(cols, key=lambda c: int(c.sum())).tolist()


def on_ground(a, rise, dx):
    """On the ground line (rise rows above it), its box centred dx columns from the standing point."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    return K.shifted(a, PIVOT[0] + dx - (xs.min() + xs.max() + 1) // 2, SOLES - rise - ys.max())


def dead_frame(design, what):
    kind, amount, dx = what
    ys, xs = np.nonzero(design[..., 3] > 0)
    part = K.Part(design[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(),
                  (BACK_FOOT[0] - xs.min(), BACK_FOOT[1] - ys.min()))
    turned = K.turn(part, amount if kind == "tilt" else 90)
    out = np.zeros_like(design)
    K.place(out, turned, BACK_FOOT)
    return on_ground(out, 0 if kind == "tilt" else amount, dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(SRC, "khazix_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    design = at1x(DESIGN) if Image.open(DESIGN).size[0] != 128 else np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ink = outline_colour(design)
    for tag in TAGS:
        sheet = at1x(os.path.join(SRC, f"khazix_{tag}.png"))
        if tag == "dead":
            cols = sheet.shape[1] // cw
            for i, what in enumerate(DEAD):
                if what == "codex":
                    continue
                fig = K.finish(dead_frame(design, what), ink, SOLES)
                X, Y = (i % cols) * cw, (i // cols) * ch
                px, py = cells["tags"][tag][i]["pivot"]
                cell = np.zeros((ch, cw, 4), np.uint8)
                K.put(cell, fig, px - PIVOT[0], py - PIVOT[1])
                sheet[Y:Y + ch, X:X + cw] = cell
            print(f"dead: frames {[i + 1 for i, w in enumerate(DEAD) if w != 'codex']} rebuilt from the design")
        if a.check:
            continue
        big = Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1))
        big.save(os.path.join(OUT, f"khazix_{tag}.png"))
    if not a.check:
        shutil.copyfile(os.path.join(SRC, "khazix_cells.json"), os.path.join(OUT, "khazix_cells.json"))
        print("wrote", ", ".join(f"khazix_{t}.png" for t in TAGS), "and khazix_cells.json to assets/source/native")


if __name__ == "__main__":
    main()
