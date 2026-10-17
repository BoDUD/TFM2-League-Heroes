#!/usr/bin/env python3
"""The huntress's run: Codex's legs (the run redo, assets/source/elise/RUN_PROMPT.md) under the design's upper body
-> assets/source/elise/frames/run_1..8.png (+ faces.json). Run after import_elise_strips.py (it writes Codex's step-2 run,
which this replaces).

    python tools/art/import_elise_run.py <delivery>/elise-run [--review DIR]

The delivery (Codex, 2026-10-15, outputs/elise_run_review.zip): 8 frames drawn by image_gen along the pack's leg lines
(tools/art/pack_elise_run.py), each a whole picture - Codex's own handoff: the upper body redrawn (not pixel-identical),
soft edges, not on a strict 7-px grid, some soles below the ground. So, its RUN_PROMPT's last step:
  * each raw frame is read on the pack's 7-px grid (the phase that matches the pack's upper body best), every square the
    commonest colour of its pixels snapped to the design's 40 colours, clear where most of it is clear;
  * the legs only: the squares under LEG_TOP (a few rows over the hips) that are not the pack's upper body (dilated a
    square: Codex's own edge of the gown goes) and not in the back legs' claw corner (run_elise's masks);
  * the pack's upper body (the design's, sunk SINK rows) goes back over the legs, square for square;
  * the frame is grounded (its lowest square on the soles' row), the outline closed, small cracks between the legs and
    the body filled; the face point moves with it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import import_elise_strips as I  # noqa: E402
import pack_elise_run as PR  # noqa: E402
import run_elise as RE  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

PX = PR.PX
LEG_TOP = RE.HIP - 4              # design row: the legs taken from here down (the thighs' tops under the gown)
CRACK = 30
SPECK = 12


def palette():
    d = I.design("human")
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)


PAL = palette()


def read_grid(raw, ox, oy):
    """The raw picture read on a 7-px grid starting at (ox, oy) -> (ROWS, COLS, 4) on the pack's squares."""
    H, W = I.ROWS, I.COLS
    out = np.zeros((H, W, 4), np.uint8)
    a = raw.astype(int)
    for r in range(H):
        y0 = oy + r * PX
        if y0 < 0 or y0 + PX > a.shape[0]:
            continue
        for c in range(W):
            x0 = ox + c * PX
            if x0 < 0 or x0 + PX > a.shape[1]:
                continue
            blk = a[y0:y0 + PX, x0:x0 + PX].reshape(-1, 4)
            op = blk[:, 3] >= 128
            if op.sum() * 2 < len(blk):
                continue
            cols = blk[op][:, :3]
            idx = np.argmin(((cols[:, None, :] - PAL[None, :, :]) ** 2).sum(-1), axis=1)
            k = np.bincount(idx).argmax()
            out[r, c, :3], out[r, c, 3] = PAL[k], 255
    return out


def best_phase(raw, body):
    """The 7-px grid phase (and whole-square shift) whose read-back's opaque squares match the pack's upper body most."""
    best = None
    for oy in range(PX):
        for ox in range(PX):
            g = read_grid(raw, ox, oy)
            op = g[..., 3] > 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    sh = np.roll(np.roll(op, dy, 0), dx, 1)
                    score = (sh & body).sum() - (sh & ~body)[: I.FORMS["human"]["at"][1] + RE.HIP].sum()
                    if best is None or score > best[0]:
                        best = (score, ox, oy, dx, dy)
    return best


def run_frame(raw, k):
    up = PR.upper(k)
    body = up[..., 3] > 0
    _, ox, oy, dx, dy = best_phase(raw, body)
    g = np.roll(np.roll(read_grid(raw, ox, oy), dy, 0), dx, 1)
    x0, y0 = I.FORMS["human"]["at"]
    yy, xx = np.mgrid[0:I.ROWS, 0:I.COLS]
    legs = (g[..., 3] > 0) & (yy >= y0 + LEG_TOP + PR.SINK[k])
    # Codex's own edge of the gown (beside the pack's) goes above the hips; below them every leg square stays, so the
    # legs meet the body with no gap (a dilation all the way down left a clear row under the thighs)
    grown = ndimage.binary_dilation(body, structure=np.ones((3, 3)))
    grown[y0 + RE.HIP + PR.SINK[k]:] = body[y0 + RE.HIP + PR.SINK[k]:]
    legs &= ~grown
    legs &= ~((yy < y0 + RE.CLAW_ROW + PR.SINK[k]) & (xx < x0 + RE.NEAR_TOP_COL))
    # the legs' own pieces only (a stray of Codex's gown or claws left after the cut goes)
    lbl, n = ndimage.label(legs, structure=np.ones((3, 3)))
    if n:
        sizes = ndimage.sum(legs, lbl, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz < SPECK:
                legs[lbl == j] = False
    out = np.zeros_like(up)
    out[legs] = g[legs]
    out[body] = up[body]
    dark = tuple(int(v) for v in PAL[np.argmin(PAL.sum(1))])
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    for j in range(1, n + 1):
        hole = lab == j
        if hole.sum() <= CRACK:
            out[hole] = (*dark, 255)
    out = G.complete_outline(out, color=dark)[0]
    ys = np.nonzero((out[..., 3] > 0).any(1))[0]
    shift = I.SOLE - int(ys.max())
    return np.roll(out, shift, axis=0), (ox, oy, dx, dy, shift, int(legs.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("delivery")
    ap.add_argument("--review", help="write the 8 frames side by side at 3x here")
    a = ap.parse_args()
    table_path = I.lp(os.path.join(I.OUT, "frames.json"))
    faces_path = I.lp(os.path.join(I.OUT, "faces.json"))
    table = json.load(open(table_path, encoding="utf-8"))
    faces = json.load(open(faces_path, encoding="utf-8"))
    x0, y0 = I.FORMS["human"]["at"]
    r0, _, c0, _ = I.FORMS["human"]["face"]
    table["run"], frames = [], []
    for k in range(8):
        raw = np.asarray(Image.open(os.path.join(a.delivery, "raw", f"elise_run_{k + 1}.png")).convert("RGBA"))
        f, info = run_frame(raw, k)
        frames.append(f)
        name = f"run_{k + 1}.png"
        Image.fromarray(f).save(I.lp(os.path.join(I.OUT, name)))
        table["run"].append([name, RE.RUN_MS])
        faces[f"run_{k + 1}"] = [x0 + c0, y0 + r0 + PR.SINK[k] + info[4]]
        print(f"run {k + 1}: grid phase {info[0]},{info[1]} shift {info[2]},{info[3]} grounded {info[4]:+d}, legs {info[5]}")
    with open(table_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    with open(faces_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(faces, fh, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z = 3
        crop = [f[:, 40:180] for f in frames]
        big = Image.new("RGBA", (len(crop) * 140 * Z, I.ROWS * Z), (96, 112, 96, 255))
        for k, c in enumerate(crop):
            big.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((140 * Z, I.ROWS * Z), Image.NEAREST),
                                (k * 140 * Z, 0))
        big.convert("RGB").save(os.path.join(a.review, "elise_run_codex_legs.png"))


if __name__ == "__main__":
    main()
