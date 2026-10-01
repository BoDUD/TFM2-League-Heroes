#!/usr/bin/env python3
"""Nocturne's action strips (assets/source/native/nocturne_<tag>.png) from Codex's step-2 delivery.

    python tools/art/fix_nocturne_strips.py [--check]

Codex (assets/source/nocturne/codex_strips/, its HANDOFF.md) built the nine actions as a part rig of the approved
40-row design (assets/source/nocturne/MODEL_STRIPS.md: the pieces cut, turned and moved, the head only moved) and kept
the idle strip as sent: exact 1x strips, only the design's 20 colours, the head identical in every frame. The one fault
found frame by frame: when an arm moves off the body, a dangling piece of its old outline stays behind - near-black
squares joined to the body only at a corner (a 3-square stroke right of the chest in 20 frames, 1-2 squares by a fist
in 5). They go. A corner-joined square at the tail's tip (on the feet row, 11 under the pivot) stays: the tip ending
on a diagonal is ordinary pixel art, and it keeps him on the ground.
Writes the strips at 8x and copies nocturne_cells.json (the pack's table, the standing points Codex drew to).
--check compares with the committed files instead of writing them.
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "nocturne", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
TAGS = ["idle", "run", "attack", "attack_p", "skill", "skill2", "ult", "ult_hit", "hit", "dead"]
OUTLINE = (0x08, 0x06, 0x11)
FEET = 11
Z = 8


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def components(op):
    """Label the 4-neighbour components of the opaque pixels."""
    lab = np.zeros(op.shape, int)
    n = 0
    H, W = op.shape
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        n += 1
        stack = [(y, x)]
        lab[y, x] = n
        while stack:
            cy, cx = stack.pop()
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    stack.append((ny, nx))
    return lab, n


def tidy(frame, pivot):
    """Remove the outline pieces left beside the body; returns (frame, squares removed)."""
    op = frame[..., 3] > 0
    lab, n = components(op)
    if n < 2:
        return frame, 0
    main = int(np.argmax(np.bincount(lab.ravel())[1:])) + 1
    out, gone = frame.copy(), 0
    for k in range(1, n + 1):
        if k == main:
            continue
        ys, xs = np.nonzero(lab == k)
        outline = all(tuple(int(v) for v in frame[y, x, :3]) == OUTLINE for y, x in zip(ys, xs))
        assert outline and len(ys) <= 3, (len(ys), pivot)            # only small outline pieces are expected
        if ys.max() == pivot[1] + FEET:                               # the tail's tip on the feet row stays
            continue
        out[ys, xs] = 0
        gone += len(ys)
    return out, gone


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(lp(os.path.join(SRC, "nocturne_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    same = True
    for tag in TAGS:
        one = np.asarray(Image.open(lp(os.path.join(SRC, "strips_1x", f"nocturne_{tag}_1x.png"))).convert("RGBA")).copy()
        one[one[..., 3] < 128] = 0
        one[one[..., 3] > 0, 3] = 255
        cols = one.shape[1] // cw
        removed = []
        for i, fr in enumerate(cells["tags"][tag]):
            y0, x0 = (i // cols) * ch, (i % cols) * cw
            frame, gone = tidy(one[y0:y0 + ch, x0:x0 + cw], fr["pivot"])
            one[y0:y0 + ch, x0:x0 + cw] = frame
            removed.append(gone)
        big = np.repeat(np.repeat(one, Z, 0), Z, 1)
        path = os.path.join(OUT, f"nocturne_{tag}.png")
        if a.check:
            ok = np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), big)
            same &= ok
            print(f"{tag:8s} {'identical' if ok else 'DIFFERENT'}")
        else:
            Image.fromarray(big).save(lp(path))
            print(f"{tag:8s} {len(removed)} frames, outline squares removed per frame {removed}")
    if a.check:
        print("all identical" if same else "DIFFERENT")
    else:
        shutil.copyfile(lp(os.path.join(SRC, "nocturne_cells.json")), lp(os.path.join(OUT, "nocturne_cells.json")))


if __name__ == "__main__":
    main()
