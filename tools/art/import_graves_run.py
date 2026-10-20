#!/usr/bin/env python3
"""league_graves's run from Codex's leg redraw (tools/art/pack_graves_run.py -> outputs/graves-run, 2026-10-20).

    python tools/art/import_graves_run.py --prepare <delivery>     (once: the raws -> assets/source/graves/codex_run/)
    python tools/art/import_graves_run.py [--check DIR]            # hd/run_<n>.png (+ 8x sheets beside the design)

Codex redrew the whole figure in every frame (its HANDOFF: the upper body is not the pack's square for square), so only
its LEGS are taken (league_jayce's / league_milio's run): each raw lies on the pack's 1254 canvas on the 16-px grid within
a few pixels (OFFSET: the shift at which its upper body matches the pack's best, 95-100% of the squares), so
  * the raw is read at the middle of every 16-px square at that shift (alpha >= 128), every colour snapped to the side
    design's own (Lab: design_chogath_side.snap);
  * its legs - every square from the cut row (the design's row 42 at the frame's bob) down - go under the side design's
    upper body at the frame's bob (pack_graves_run.upper: head, scarf, pauldron, arms and shotgun square for square);
  * each frame is set on the ground by its lowest square (one foot is down in every frame of the 8 phases);
  * the outline closed round the legs (strips.complete_outline), the small enclosed gaps at the belt (the seam) taken
    by the outline (gap-check).
Writes assets/source/graves/hd/run_<n>.png (the design's size, padded) which rig_graves.py plays as the run.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pack_graves_run as PR  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_side import snap  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves")
CODEX = os.path.join(SRC, "codex_run")
OUT = os.path.join(SRC, "hd")
PAD = 6                         # rows / columns round the design's box in run_<n>.png (the legs reach out of it)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def prepare(delivery):
    """The delivery's raw drafts (raw/graves_run_<n>.png) -> codex_run/, with its HANDOFF."""
    os.makedirs(lp(CODEX), exist_ok=True)
    for k in range(1, 9):
        shutil.copyfile(os.path.join(delivery, "raw", f"graves_run_{k}.png"), lp(os.path.join(CODEX, f"graves_run_{k}.png")))
    for name in ("HANDOFF.md", "generation-prompts.txt"):
        p = os.path.join(delivery, name)
        if os.path.isfile(p):
            shutil.copyfile(p, lp(os.path.join(CODEX, name)))


def offset(raw, now):
    """The pixel shift at which the raw's squares match the pack's upper body (now) best."""
    ys = np.arange(8, PR.CANVAS, 16)
    Y, X = np.meshgrid(ys, ys, indexing="ij")
    m = now[Y, X, 3] > 0
    best = None
    for oy in range(-8, 9):
        for ox in range(-8, 9):
            Yr, Xr = np.clip(Y + oy, 0, PR.CANVAS - 1), np.clip(X + ox, 0, PR.CANVAS - 1)
            d = np.abs(raw[Yr, Xr, :3].astype(int) - now[Y, X, :3].astype(int)).sum(-1)
            score = (d[m] < 60).mean()
            if best is None or score > best[0]:
                best = (score, ox, oy)
    return best


def squares(raw, ox, oy):
    """The raw read at the middle of every 16-px square, shifted (ox, oy): a canvas-grid RGBA array."""
    ys = np.arange(8, PR.CANVAS, 16)
    Y, X = np.meshgrid(ys, ys, indexing="ij")
    Yr, Xr = np.clip(Y + oy, 0, PR.CANVAS - 1), np.clip(X + ox, 0, PR.CANVAS - 1)
    g = raw[Yr, Xr].copy()
    op = g[..., 3] >= 128
    g[..., 3] = np.where(op, 255, 0)
    g[~op] = 0
    return g


def frame(k, side, up):
    """Run frame k (1-8) in the side design's squares, padded PAD: the design's upper body over Codex's legs."""
    raw = np.asarray(Image.open(lp(os.path.join(CODEX, f"graves_run_{k}.png"))).convert("RGBA"))
    now = np.asarray(Image.open(os.path.join(PR_OUT, "now", f"graves_run_{k}.png")).convert("RGBA"))
    score, ox, oy = offset(raw, now)
    g = squares(raw, ox, oy)
    bob = PR.BOB[k - 1]
    cut = PR.DY + bob + PR.CUT                     # the canvas-grid row of the design's row 42 at this frame's bob
    legs = np.zeros_like(g)
    legs[cut:] = g[cut:]
    legs = snap(legs, side)
    # into the design's squares (its (0, 0) on canvas square (DX, DY + bob)), padded
    H, W = side.shape[0] + 2 * PAD, side.shape[1] + 2 * PAD
    out = np.zeros((H, W, 4), np.uint8)
    y0, x0 = PR.DY + bob - PAD, PR.DX - PAD
    sub = legs[max(0, y0):y0 + H, max(0, x0):x0 + W]
    out[max(0, -y0):max(0, -y0) + sub.shape[0], max(0, -x0):max(0, -x0) + sub.shape[1]] = sub
    body = np.zeros_like(out)
    body[PAD:PAD + up.shape[0], PAD:PAD + up.shape[1]] = up
    m = body[..., 3] > 0
    out[m] = body[m]
    # one foot down in every phase: the lowest square on the design's ground row (PAD + its rows)
    ys = np.nonzero(out[..., 3].any(1))[0]
    out = np.roll(out, PAD + side.shape[0] - 1 - ys.max(), axis=0)
    ink = PD.edge_colour(side)
    out, _, _ = strips.complete_outline(out, color=ink, feet=PAD + side.shape[0])
    op = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lab == j
        if h.sum() <= 6:
            out[h] = (*ink, 255)
    return out, (score, ox, oy)


PR_OUT = "C:/t/gv_work/graves_run_pack"


def main():
    global PR_OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", metavar="DELIVERY")
    ap.add_argument("--pack", default=PR_OUT, help="the run pack's folder (its now/ upper bodies)")
    ap.add_argument("--check")
    a = ap.parse_args()
    PR_OUT = a.pack
    if a.prepare:
        prepare(a.prepare)
        return
    side = np.asarray(Image.open(lp(os.path.join(OUT, "side.png"))).convert("RGBA"))
    up = PR.upper()
    frames = []
    for k in range(1, 9):
        f, (score, ox, oy) = frame(k, side, up)
        Image.fromarray(f).save(lp(os.path.join(OUT, f"run_{k}.png")))
        frames.append(f)
        print(f"run_{k}: upper body matched {score:.2f} at ({ox}, {oy}) px")
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        z = 8
        ref = np.zeros_like(frames[0])
        ref[PAD:PAD + side.shape[0], PAD:PAD + side.shape[1]] = side
        tiles = [ref] + frames
        for g, part in (("a", tiles[:5]), ("b", tiles[5:])):
            ims = []
            for t in part:
                im = Image.new("RGBA", (t.shape[1] * z, t.shape[0] * z), (200, 205, 195, 255))
                im.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, z, 0), z, 1)))
                ims.append(im)
            W = sum(i.width + 10 for i in ims)
            sh = Image.new("RGB", (W, ims[0].height), (255, 255, 255))
            x = 0
            for i in ims:
                sh.paste(i.convert("RGB"), (x, 0))
                x += i.width + 10
            sh.save(os.path.join(a.check, f"run_legs_{g}.png"))
        print("check", a.check)


if __name__ == "__main__":
    main()
