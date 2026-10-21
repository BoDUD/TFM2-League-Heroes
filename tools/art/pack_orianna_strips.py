#!/usr/bin/env python3
"""Orianna's chibi step-2 pack for Codex (assets/source/orianna/STRIPS_PROMPTS.md): every action frame drawn on the side
design's own grid, posed after League's animation (Galio's way: tools/art/pack_galio_strips.py).

    python tools/art/pack_orianna_strips.py [--render] [--out %TEMP%/or_q/orianna_strips_pack]

The user (2026-10-22) picked design A (tools/art/design_orianna_chibi.py: head 0.66 / body 0.80 of Codex's Q1 drafts):
assets/source/orianna/chibi/design-front.png (the idle, 3/4 front, 58 x 86 squares) and design-side.png (side-on facing
right, 48 x 87) on 128 canvases, soles on row 117. Then 「侧面也按这个比例改，然后做动作帧的包」 - Codex draws the actions
side-on after League's skeleton (the choice made for her: 「动作帧也让 Codex 照英雄联盟的骨架画，你检查修好再给我看」).
The skeletons: tools/lol/native_pose.py on assets/source/orianna/poses.json (--alpha, into %TEMP%/or_q/pose_n): League's
clips at chibi proportions (head 2.6, legs 0.75 - the design's head is about 43% of her height), camera yaw 70, every
action frame turned side-on (its "turn": 40 degrees from the 3/4 idle pose, like the run; her E spins in League), the
ball's joints hidden. The design pose is 39 game px tall and the design 86 squares, so a game px is 86 / 39 squares;
each frame's cell is scaled to PX px a square and set with its pivot on the canvas's standing point (column PIV_X, soles
on row SOLE). The idle (the front design breathing) and the hit (the side design knocked back, a white flash) are made
here, not by Codex.
Writes <out>/ (and <out>.zip): STRIPS_PROMPTS.md, design/ (both designs at PX px a square and 1x, the side design on the
canvas, its palette), now/ (the skeletons: League's 3D frame on the canvas), guide/ (the same with the lines), cells.json.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "orianna")
FRONT = os.path.join(SRC, "chibi", "design-front.png")
SIDE = os.path.join(SRC, "chibi", "design-side.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "STRIPS_PROMPTS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "or_q")
POSE = os.path.join(TMP, "pose_n")
PX = 8                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 192, 128           # the 1536 x 1024 canvas
SOLE = 117                      # the soles' row (the ground under it): room above for the hops
PIV_X = {"dead": 120}           # the standing point's column (the middle between her feet), per tag; 96 otherwise
RS = 8                          # render px a game px in native_pose's renders
DESIGN_GP = 39                  # the design pose's height in game px (native_pose's print)
DESIGN_SQ = 86                  # the front design's height in squares
SOLE_BELOW_PIVOT = 11.5         # native_pose: the soles 11.5 game px under a cell's pivot


def crop(path):
    d = np.asarray(Image.open(path).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def feet_mid(d):
    op = d[..., 3] > 0
    _, xs = np.nonzero(op[-3:])
    return (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(tag, i, cell):
    """Frame i of a tag's pose render, scaled to the pack's squares."""
    im = Image.open(os.path.join(POSE, f"orianna_pose_{tag}.png")).convert("RGBA")
    cw, ch = cell[0] * RS, cell[1] * RS
    c = im.crop(((i % 4) * cw, (i // 4) * ch, (i % 4 + 1) * cw, (i // 4 + 1) * ch))
    k = PX * DESIGN_SQ / DESIGN_GP / RS                 # render px -> canvas px
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


def lines(img, top, piv):
    """Every 10th square light grey, the design's bun top (blue), the soles' row (red), the standing point (blue cross)."""
    dr = ImageDraw.Draw(img)
    for c in range(0, COLS + 1, 10):
        dr.line([(c * PX, 0), (c * PX, 1024)], fill=(200, 200, 200, 110))
    for r in range(0, ROWS + 1, 10):
        dr.line([(0, r * PX), (1536, r * PX)], fill=(200, 200, 200, 110))
    dr.line([(0, top * PX), (1536, top * PX)], fill=(40, 90, 255, 255), width=2)
    dr.line([(0, (SOLE + 1) * PX), (1536, (SOLE + 1) * PX)], fill=(255, 40, 40, 255), width=2)
    cx, cy = (piv + 0.5) * PX, (SOLE + 1) * PX
    dr.line([(cx - 18, cy), (cx + 18, cy)], fill=(40, 90, 255, 255), width=3)
    dr.line([(cx, cy - 18), (cx, cy + 18)], fill=(40, 90, 255, 255), width=3)
    return img


def on_canvas(d, piv):
    h, w = d.shape[:2]
    x0 = int(round(piv - feet_mid(d)))
    y0 = SOLE - (h - 1)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    return Image.fromarray(up(can, PX)), x0, y0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true", help="run native_pose.py on the spec first")
    ap.add_argument("--out", default=os.path.join(TMP, "orianna_strips_pack"))
    a = ap.parse_args()
    if a.render:
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lol", "native_pose.py"), SPEC, "--out", POSE,
                        "--alpha"], check=True, cwd=ROOT)
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide"):
        os.makedirs(os.path.join(out, sub))
    side, front = crop(SIDE), crop(FRONT)
    for name, d in (("side", side), ("front", front)):
        Image.fromarray(up(d, PX)).save(os.path.join(out, "design", f"orianna_{name}.png"))
        Image.fromarray(d).save(os.path.join(out, "design", f"orianna_{name}_1x.png"))
    cols = np.unique(side[side[..., 3] > 0][:, :3], axis=0)
    cols = cols[np.argsort(cols.sum(axis=1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "orianna_palette.png"))
    big, x0, y0 = on_canvas(side, 96)
    big.save(os.path.join(out, "design", "orianna_side_on_canvas.png"))
    lines(big.copy(), y0, 96).save(os.path.join(out, "design", "orianna_side_guide.png"))

    cells = json.load(open(os.path.join(POSE, "orianna_cells.json"), encoding="utf-8"))
    cell = cells["cell"]
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "sole_row": SOLE, "design_squares": [side.shape[1], side.shape[0]],
                "frames": []}
    for tag, frames in cells["tags"].items():
        piv = PIV_X.get(tag, 96)
        ims = []
        for i, f in enumerate(frames):
            sk, k = skeleton(tag, i, cell)
            can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
            px, py = f["pivot"]
            ox = round((piv + 0.5) * PX - (px + 0.5) * RS * k)
            oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
            can_im.paste(sk, (ox, oy), sk)
            ims.append(can_im)
        # the turned side-on frames reach lower than the 3/4 design pose (the near toe, the camera's pitch): the tag is
        # lifted so that its standing frame (the first; the run's lowest step) has its soles on SOLE
        low = [int(np.nonzero(np.asarray(im)[..., 3] > 60)[0].max()) for im in ims]
        lift = max(0, (max(low) if tag == "run" else low[0]) - ((SOLE + 1) * PX - 1))
        for i, f in enumerate(frames):
            can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
            can_im.paste(ims[i], (0, -lift), ims[i])
            name = f"orianna_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            g = Image.new("RGBA", can_im.size, (245, 245, 245, 255))
            g.alpha_composite(can_im)
            lines(g, y0, piv).convert("RGB").save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": f["ms"], "standing_point": [piv, SOLE]})
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "STRIPS_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"side design {side.shape[1]}x{side.shape[0]} at ({x0},{y0}), {len(cols)} colours; "
          f"{len(manifest['frames'])} frames -> {zp}")


if __name__ == "__main__":
    main()
