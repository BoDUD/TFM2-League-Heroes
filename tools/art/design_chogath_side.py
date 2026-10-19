#!/usr/bin/env python3
"""Cho'Gath's side view (assets/source/chogath/codex_side, 2026-10-19, Codex new-chat-7: SIDE_PROMPTS.md) read back on
its own grid, in the idle's colours, with the idle's head.

    python tools/art/design_chogath_side.py --options DIR     # both takes side by side (the user's pick)
    python tools/art/design_chogath_side.py                   # writes assets/source/chogath/hd/side.png

Codex's squares (the colour spread inside the squares levels off): side-1 ~16 px (44 rows, as asked), side-2 ~15 px
(51 rows). Each is read back with regrid at its own size, side-2 cut to 46 rows by whole lines (design_chogath_model's
keep_axis, its head kept); every colour then snaps to the nearest of the idle's own (hd/idle.png, Lab). One face in
all frames: the idle's head (pack_chogath_side.HEAD) is pasted with its eyes on the side's eyes, after the side's own
head is cleared inside the pasted head's outline.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_chogath_model as M  # noqa: E402
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_hd import lp  # noqa: E402
from pack_chogath_side import HEAD  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "chogath", "codex_side", "chogath-side")
OUT = os.path.join(ROOT, "assets", "source", "chogath", "hd")
ROWS = 46
PICK = "side-1"
# name -> (Codex's square px, head rows, head columns on its own read-back)
TAKES = {"side-1": (16.0, None, None), "side-2": (15.0, range(22, 46), range(52, 79))}


def cyan(a):
    a = a.astype(int)
    return (a[..., 2] > 180) & (a[..., 1] > 170) & (a[..., 0] < 140) & (a[..., 3] > 0)


def read(name):
    size, fr, fc = TAKES[name]
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"chogath-{name}.png"))).convert("RGBA")), size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    if raw.shape[0] > ROWS:
        idx, pal = M.recolour(raw)
        rows = [0] + [r + 1 for r in M.keep_axis([idx[y] for y in range(1, raw.shape[0])], ROWS - 1,
                                                 range(fr.start - 1, fr.stop - 1))]
        sub = idx[rows]
        cols = M.keep_axis([sub[:, x] for x in range(raw.shape[1])], round(raw.shape[1] * ROWS / raw.shape[0]), fc)
        raw = raw[np.ix_(rows, cols)]
    return raw


def snap(fig, ref):
    """Every colour of fig to the nearest colour of ref (Lab)."""
    pal = np.unique(ref[ref[..., 3] > 0][:, :3], axis=0)
    lab_p = V.srgb2lab(pal)
    out = fig.copy()
    m = fig[..., 3] > 0
    px = fig[m][:, :3].astype(float)
    lab_x = V.srgb2lab(px)
    d = ((lab_x[:, None, :] - lab_p[None, :, :]) ** 2).sum(2)
    out[m, :3] = pal[d.argmin(1)]
    return out


def with_head(fig, idle):
    """The idle's head pasted with its eyes' centre on the side's eyes' centre; the side's own squares under the head's
    outline are replaced, the rest stays."""
    r0, r1, c0, c1 = HEAD
    head = idle[r0:r1, c0:c1]
    hy, hx = np.argwhere(cyan(head)).mean(0)
    sy, sx = np.argwhere(cyan(fig)).mean(0)
    oy, ox = int(round(sy - hy)), int(round(sx - hx))
    pad = 30
    can = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    m = head[..., 3] > 0
    reg = can[pad + oy:pad + oy + head.shape[0], pad + ox:pad + ox + head.shape[1]]
    # the side's own eyes / teeth left outside the pasted head: none may stay (one face)
    reg[m] = head[m]
    out = can
    ys, xs = np.nonzero(out[..., 3] > 0)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    left = cyan(out).sum() - cyan(head).sum()
    return out, (oy, ox), left


def finish(fig):
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def build(name, idle):
    fig = snap(read(name), idle)
    fig, off, left = with_head(fig, idle)
    print(name, "head at", off, "stray eye squares", left)
    return finish(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = [("idle", idle)]
        for n in TAKES:
            raw = snap(read(n), idle)
            cells += [(f"{n} read", raw), (f"{n} + idle head", build(n, idle))]
        M.sheet(cells, os.path.join(a.options, "chogath_side_options.png"))
        return
    fig = build(PICK, idle)
    Image.fromarray(fig).save(lp(os.path.join(OUT, "side.png")))
    Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, "side_4x.png")))
    print("side", PICK, fig.shape[1], "x", fig.shape[0])


if __name__ == "__main__":
    main()
