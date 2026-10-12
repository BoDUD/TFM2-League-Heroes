#!/usr/bin/env python3
"""Braum's action frames from Codex's step-2 delivery (assets/source/braum/codex_strips, 6-px grid, read back by Codex
square for square into the design's 48 colours), tidied the user's way (「你觉得有问题你修吧」):

    python tools/art/import_braum_strips.py [--review DIR]

  * R drawn small: every ult frame scaled ULT_SCALE about the standing point (whole squares repeated, nearest), the
    soles kept on the ground line - Codex drew the action about a fifth smaller (ult 1 standing 96 rows against the
    design's 121);
  * one face (memory one-face-all-frames): in every upright frame the design's head (HEAD box minus the fur and the
    shoulder) is pasted where it matches the drawn head best (exact palette squares within a few squares of the drawn
    head's place, scale 1), and the drawn head's leftovers round it (head colours in the cranium's rows outside the
    pasted head) are cleared; tilted or lying heads (dead 1-6) stay Codex's;
  * the soles on the design's ground row (Codex's frames stand one row higher);
  * idle = the design itself; hit = the design 2 squares back with a white flash, then 1 back.
Writes assets/source/braum/frames/braum_<tag>_<n>.png (the dense frames on the pack's 256 x 170 canvas with PAD rows
added on top, standing point PIV_X / SOLE) and frames.json (tag -> [(file, ms)]). tools/art/rig_braum.py turns
them into the game sheets (outline, breathing, sizes).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view as swv
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "braum")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
DESIGN = os.path.join(SRC, "hd", "front.png")
PAD = 40                           # rows added above the pack's canvas: R's shield, scaled up, rises past its top
COLS, ROWS = 256, 170 + PAD
PIV_X, SOLE = 110, 163 + PAD       # the pack's standing point (pack_braum_strips.py), moved down by PAD
DESIGN_AT = (68, 43 + PAD)         # the design's top-left on that canvas
ULT_SCALE = 1.2
HEAD = (0, 20, 37, 56)             # the design's head box (rows, columns): crown to chin, ear to the moustache's tip
FUR = {(241, 229, 197), (200, 188, 161), (167, 156, 132), (93, 83, 67)}
KEEP_HEAD = {("dead", i) for i in range(1, 7)}
SEARCH = 6                         # squares round the drawn head's place the pasted head may move
OUTLINE = (6, 5, 5)
SPECK = 8                          # loose pieces this small round a pasted head are leftovers


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def head_patch(d):
    y0, y1, x0, x1 = HEAD
    p = d[y0:y1, x0:x1].copy()
    m = p[..., 3] > 0
    for y, x in zip(*np.nonzero(m)):
        if tuple(int(v) for v in p[y, x, :3]) in FUR or (y >= 12 and x + x0 >= 51):
            m[y, x] = False
    return p, m


def head_colours(p, m):
    return {tuple(int(v) for v in c) for c in p[m][:, :3]}


def match(a, p, m, around=None):
    """Best place (y, x) of the patch: the most squares within 45 of the patch's colour."""
    rgb = a[..., :3].astype(np.int16)
    op = a[..., 3] > 0
    h, w = m.shape
    win = swv(rgb, (h, w, 3))[..., 0, :, :, :]
    wop = swv(op, (h, w))
    d = np.abs(win - p[..., :3].astype(np.int16)).sum(-1)
    score = ((d < 45) & wop & m).sum((2, 3)).astype(float)
    if around is not None:
        yy, xx = np.mgrid[0:score.shape[0], 0:score.shape[1]]
        score[(abs(yy - around[0]) > SEARCH) | (abs(xx - around[1]) > SEARCH)] = -1
    y, x = np.unravel_index(np.argmax(score), score.shape)
    return int(y), int(x), score[y, x] / m.sum()


def scale_about(a, k, px, py):
    """`a` scaled k about (px, py) (the standing point: column centre, the soles' bottom edge), nearest."""
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    sy = np.floor((yy + 0.5 - (py + 1)) / k + (py + 1)).astype(int)
    sx = np.floor((xx + 0.5 - (px + 0.5)) / k + (px + 0.5)).astype(int)
    ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
    out = np.zeros_like(a)
    out[ok] = a[sy[ok], sx[ok]]
    return out


def paste_head(a, p, m, cols, at):
    """The design's head at `at` (top-left), its leftovers cleared: head colours in the cranium's rows (the patch's
    rows 0-10) within 3 squares outside the pasted head become clear."""
    y, x = at
    h, w = m.shape
    out = a.copy()
    region = out[y:y + h, x:x + w]
    region[m] = p[m]
    # leftovers of the drawn head beside / above the pasted cranium
    for yy in range(max(0, y - 3), y + 11):
        for xx in range(max(0, x - 3), min(COLS, x + w + 3)):
            iy, ix = yy - y, xx - x
            inside = 0 <= iy < h and 0 <= ix < w and m[iy, ix]
            if inside or out[yy, xx, 3] == 0:
                continue
            c = tuple(int(v) for v in out[yy, xx, :3])
            if c in cols or c == OUTLINE:
                # clear only what sits outside the design's own head silhouette on that row
                out[yy, xx] = 0
    # the drawn moustache's tips sticking out beside the pasted one (its rows, right of the face)
    brown = {c for c in cols if c[0] < 120 and c[1] < 90 and c[2] < 70}
    for yy in range(y + 6, min(ROWS, y + 15)):
        for xx in range(x + w - 6, min(COLS, x + w + 4)):
            iy, ix = yy - y, xx - x
            if 0 <= ix < w and m[iy, ix]:
                continue
            c = tuple(int(v) for v in out[yy, xx, :3])
            if out[yy, xx, 3] and c in brown:
                out[yy, xx] = 0
    # specks: opaque pieces of at most SPECK squares near the head, joined to nothing
    lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        for k, sz in enumerate(sizes, 1):
            if sz <= SPECK:
                ys, xs = np.nonzero(lab == k)
                if (abs(ys.mean() - (y + h / 2)) < h and abs(xs.mean() - (x + w / 2)) < w):
                    out[lab == k] = 0
    out, _, _ = G.complete_outline(out, color=OUTLINE)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a 6x before / after sheet per tag here")
    a = ap.parse_args()
    d = load(DESIGN)
    p, m = head_patch(d)
    cols = head_colours(p, m)
    manifest = json.load(open(os.path.join(CODEX, "cells.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    frames = {}
    # the design's head place on the canvas: the reference the drawn heads are found round
    hy0, hx0 = DESIGN_AT[1] + HEAD[0], DESIGN_AT[0] + HEAD[2]
    report = []
    for f in manifest["frames"]:
        tag, i = f["tag"], f["index"] + 1
        src = load(os.path.join(CODEX, f["file"].replace(".png", "_1x.png")))
        src = np.concatenate([np.zeros((PAD + 1, COLS, 4), np.uint8), src[:-1]])   # PAD rows on top; soles on SOLE
                                                                                   # (Codex: one row higher)
        if tag == "ult":
            src = scale_about(src, ULT_SCALE, PIV_X, SOLE)
        before = src.copy()
        if (tag, i) not in KEEP_HEAD:
            y, x, s = match(src, p, m)
            src = paste_head(src, p, m, cols, (y, x))
            report.append(f"{tag} {i}: head at ({y},{x}) match {s:.2f}")
        else:
            report.append(f"{tag} {i}: Codex's head kept")
        name = f"braum_{tag}_{i}.png"
        Image.fromarray(src).save(os.path.join(OUT, name))
        frames.setdefault(tag, []).append((name, f["ms"]))
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 4
            pair = np.concatenate([before, np.zeros((ROWS, 4, 4), np.uint8), src], axis=1)
            bg = Image.new("RGBA", (pair.shape[1] * Z, pair.shape[0] * Z), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(pair).resize((pair.shape[1] * Z, pair.shape[0] * Z), Image.NEAREST))
            bg.convert("RGB").save(os.path.join(a.review, name))
    # idle = the design; hit = moved back with a flash
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[DESIGN_AT[1]:DESIGN_AT[1] + d.shape[0], DESIGN_AT[0]:DESIGN_AT[0] + d.shape[1]] = d
    Image.fromarray(can).save(os.path.join(OUT, "braum_idle_1.png"))
    frames["idle"] = [("braum_idle_1.png", 500)]
    flash = can.copy()
    op = flash[..., 3] > 0
    flash[op, :3] = (flash[op, :3] * 0.65 + 255 * 0.35).astype(np.uint8)
    Image.fromarray(np.roll(flash, -2, axis=1)).save(os.path.join(OUT, "braum_hit_1.png"))
    Image.fromarray(np.roll(can, -1, axis=1)).save(os.path.join(OUT, "braum_hit_2.png"))
    frames["hit"] = [("braum_hit_1.png", 100), ("braum_hit_2.png", 100)]
    with open(os.path.join(OUT, "frames.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(frames, fh, indent=1)
    print("\n".join(report))


if __name__ == "__main__":
    main()
