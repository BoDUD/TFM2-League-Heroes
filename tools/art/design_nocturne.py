#!/usr/bin/env python3
"""Nocturne's design (assets/source/native/nocturne_native.png): Codex's game-size design B, cut to 40 rows.

    python tools/art/design_nocturne.py [--check] [--review OUT.png]

How it came about (2026-10-02): the user picked Codex's picture A (assets/source/nocturne/PICTURE_PROMPT.md: League's
hunched idle, a smoke tail instead of legs). Asked for a 44-row game-size sprite (MODEL_PROMPTS.md), Codex drew both
versions front-on and symmetric and too big - A 37x50, B 37x46 (codex_model/HANDOFF.md: its geometry pass was blocked
by HTTP 403 when the user's GPT plan ran out). The user took B (two 2x2 white eyes) and asked for 40-41 rows ("最后要
削到40-41格"), then picked 40 of a 41 and a 40 cut shown beside the pack's heroes. Steps:
  1. codex_model/nocturne_design_B_1x.png as drawn (alpha 0/255, 20 colours, one 8-connected piece);
  2. whole rows and columns deleted, never two neighbours and never through the face (the 2x2 eyes on rows 67-68,
     columns 63-64 and 67-68 stay with the two navy columns between them): ROWS - two of the crest's stem, one at the
     pauldrons' top under the spikes, one through the tabard and the blades' straight part, two of the tail; COLS -
     each blade's outer edge column and one inside each pauldron (the rows and columns that differ least from a
     neighbour, measured on the design);
  3. put back with the tail's tip (the lowest row's middle) on row 99, column 64 - the standing point (64, 88) is 11
     rows above it, as for the other heroes' soles;
  4. shown at 8x on the 128x128 canvas.
--check compares the result with the committed nocturne_native.png instead of writing it.
"""
import argparse
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DRAFT = os.path.join(ROOT, "assets", "source", "nocturne", "codex_model", "nocturne_design_B_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "nocturne_native.png")
ROWS = [56, 59, 62, 86, 93, 95]          # on Codex's 128x128 canvas (the figure is rows 54-99, columns 44-80)
COLS = [45, 54, 71, 79]
SOLE_ROW, MID_COL = 99, 64
EYE = (255, 255, 255)                    # the eyes' white, used nowhere else (import_native steadies the loops on it)


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def build():
    a = np.asarray(Image.open(lp(DRAFT)).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    a[a[..., 3] == 0] = 0
    for r in ROWS:
        assert r - 1 not in ROWS and not 66 <= r <= 69, r
    for c in COLS:
        assert c - 1 not in COLS and not 62 <= c <= 69, c
    cut = a[[r for r in range(128) if r not in ROWS]][:, [c for c in range(128) if c not in COLS]]
    ys, xs = np.nonzero(cut[..., 3])
    fig = cut[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    low = np.nonzero(fig[-1, :, 3])[0]
    mid = int(round((low.min() + low.max()) / 2))
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], MID_COL - mid
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    assert fig.shape[:2] == (40, 33), fig.shape
    eye = np.all(out[..., :3] == np.array(EYE, np.uint8), -1) & (out[..., 3] > 0)
    assert eye.sum() == 8, eye.sum()         # two 2x2 eyes
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="also write a 12x view with the cut rows/columns marked on Codex's B")
    a = ap.parse_args()
    out = build()
    big = np.repeat(np.repeat(out, 8, 0), 8, 1)
    if a.check:
        cur = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(cur, big) else "DIFFERENT")
        return
    Image.fromarray(big).save(lp(OUT))
    ys, xs = np.nonzero(out[..., 3])
    eye = np.argwhere(np.all(out[..., :3] == np.array(EYE, np.uint8), -1) & (out[..., 3] > 0))
    print(OUT, f"{xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}", f"rows {ys.min()}-{ys.max()}",
          len({tuple(c) for c in out[out[..., 3] > 0][:, :3].tolist()}), "colours",
          "eyes rows", sorted({int(y) for y, _ in eye}), "cols", sorted({int(x) for _, x in eye}))
    if a.review:
        src = np.asarray(Image.open(lp(DRAFT)).convert("RGBA")).copy()
        z = 12
        v = np.repeat(np.repeat(src, z, 0), z, 1).copy()
        for r in ROWS:
            v[r * z:(r + 1) * z, :, :3] = (v[r * z:(r + 1) * z, :, :3] * 0.4 + np.array([255, 60, 60]) * 0.6).astype(np.uint8)
            v[r * z:(r + 1) * z, :, 3] = 255
        for c in COLS:
            v[:, c * z:(c + 1) * z, :3] = (v[:, c * z:(c + 1) * z, :3] * 0.4 + np.array([60, 60, 255]) * 0.6).astype(np.uint8)
            v[:, c * z:(c + 1) * z, 3] = 255
        Image.fromarray(v[50 * z:102 * z, 40 * z:84 * z]).save(a.review)


if __name__ == "__main__":
    main()
