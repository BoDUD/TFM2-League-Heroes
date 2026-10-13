#!/usr/bin/env python3
"""Galio's step-2 pack for Codex (assets/source/galio/MODEL_STRIPS.md): every action frame drawn on the dense design's
own grid, posed after League's animation.

    python tools/art/pack_galio_strips.py [--out dist/galio_packs/galio_strips_pack]

The design (tools/art/design_galio_hd.py -> assets/source/galio/hd/front.png: picture A read back, the fists drawn oppi's
way, 85 x 128 canvas, 104 squares wing tips to soles, 45 colours; PPU 2.0) is the idle. Every action is drawn from the
3/4 FRONT (the user, on the side view: 「侧面还是跟怪啊」 -> 「不要侧身，所有动作用正面」, Braum's / Kassadin's way) and posed
after League's animation (Braum's lesson: 「参考英雄联盟里的动作帧吧」).
The skeletons: tools/lol/native_pose.py on assets/source/galio/poses.json (--alpha) -> %TEMP%/gl_work/pose_n: League's
clips through one camera (yaw 30, mirrored: he faces right), one scale for every frame, 8 render px a game px; the
design pose is 50 game px tall with the wings (native_pose's print), the design 104 squares, so a design square is
50 / 104 game px. Each frame's cell is scaled to PX px a square and placed with its pivot on the canvas's standing point
(column PIV_X, the soles' row SOLE): the pose, the place and the size.
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (the design at PX px a square, 1x, palette), now/ (skeletons),
guide/ (the same with the lines), refs/ (picture A, League's clips as contact sheets - Riot's model: local only),
cells.json (every frame: tag, index, ms, standing point).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "galio")
DESIGN = os.path.join(SRC, "hd", "front.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gl_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips30")   # contact sheets at the pack's 3/4 camera (yaw 30, mirrored)
PICTURE = os.path.join(SRC, "codex_picture", "galio-model-A.png")
PX = 7                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 219, 146           # 1533 x 1022 inside the 1536 x 1024 canvas
SOLE = 140                      # the soles' row (the ground under it): room above for the leaps
PIV_X = 92                      # the standing point's column (the middle between his feet)
RS = 8                          # render px a game px in native_pose's renders
DESIGN_GP = 50                  # the design pose's height in game px with the wings (native_pose's print)
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot (design pose: pivot 88, soles 99)


def design():
    d = np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def feet_mid(d):
    """The middle column between his two clawed feet: the bottom 4 rows right of the tail (columns >= 26)."""
    op = d[..., 3] > 0
    ys, xs = np.nonzero(op[-4:, 26:])
    xs = xs + 26
    return (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(tag, i, cell, cols):
    """Frame i of a tag's pose render on the pack canvas (1536 x 1024 RGBA)."""
    im = Image.open(os.path.join(POSE, f"galio_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    rows = design().shape[0]
    k = PX * rows / DESIGN_GP / RS                     # render px -> canvas px
    c = c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS)
    return c, k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "galio_packs", "galio_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):          # its contents (the folder itself may be some shell's working directory)
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = design()
    h, w = d.shape[:2]
    Image.fromarray(up(d, PX)).save(os.path.join(out, "design", "galio_design.png"))
    Image.fromarray(d).save(os.path.join(out, "design", "galio_design_1x.png"))
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    cols = cols[np.argsort(cols.sum(axis=1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "galio_palette.png"))
    # the design on the pack canvas: its feet's middle on PIV_X, its soles on SOLE
    x0 = int(round(PIV_X + 0.5 - feet_mid(d) - 0.5))
    y0 = SOLE - (h - 1)
    can = np.zeros((1024 // PX + 1, COLS, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    big = Image.fromarray(up(can, PX)).crop((0, 0, 1536, 1024))
    big.save(os.path.join(out, "design", "galio_design_on_canvas.png"))
    lines(big.copy(), y0).save(os.path.join(out, "design", "galio_design_guide.png"))
    shutil.copyfile(PICTURE, os.path.join(out, "refs", "galio_picture_A.png"))
    for n in ("Galio_run", "Galio_attack01", "Galio_passive_attack", "Galio_spell1", "Galio_spell3_windup", "Galio_spell3",
              "Galio_spell2_idle", "Galio_spell2_idle_cast", "Galio_Spell4_IN", "Galio_Spell4_OUT", "Galio_Death"):
        p = os.path.join(CLIPS, n + ".png")
        if os.path.isfile(p):
            shutil.copyfile(p, os.path.join(out, "refs", f"league_{n[6:].lower()}.png"))

    spec = json.load(open(SPEC, encoding="utf-8"))
    cells = json.load(open(os.path.join(POSE, "galio_cells.json"), encoding="utf-8"))
    cell = cells["cell"]
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "standing_point": [PIV_X, SOLE],
                "design_squares": [w, h], "design_at": [x0, y0], "frames": []}
    for tag, frames in cells["tags"].items():
        n_cols = 3 if len(frames) <= 6 else 4
        for i, f in enumerate(frames):
            sk, k = skeleton(tag, i, cell, n_cols)
            can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
            px, py = f["pivot"]
            # the cell's pivot (game px) -> the canvas: x on PIV_X's centre, the soles on SOLE's bottom edge
            ox = round((PIV_X + 0.5) * PX - (px + 0.5) * RS * k)
            oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
            can_im.alpha_composite(sk, (ox, oy)) if ox >= 0 and oy >= 0 else can_im.paste(sk, (ox, oy), sk)
            name = f"galio_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            lines(can_im.copy(), y0).save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": f["ms"]})
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"design {w}x{h} squares at ({x0},{y0}), {len(cols)} colours; {len(manifest['frames'])} frames -> {zp}")


def lines(img, top):
    """The grid's lines: every 10th square light grey, the design's top row (blue), the soles' row (red), the standing
    point (blue cross)."""
    dr = ImageDraw.Draw(img)
    for c in range(0, COLS + 1, 10):
        dr.line([(c * PX, 0), (c * PX, 1024)], fill=(200, 200, 200, 90))
    for r in range(0, ROWS + 1, 10):
        dr.line([(0, r * PX), (1536, r * PX)], fill=(200, 200, 200, 90))
    dr.line([(0, top * PX), (1536, top * PX)], fill=(40, 90, 255, 255), width=2)
    dr.line([(0, (SOLE + 1) * PX), (1536, (SOLE + 1) * PX)], fill=(255, 40, 40, 255), width=2)
    cx, cy = (PIV_X + 0.5) * PX, (SOLE + 1) * PX
    dr.line([(cx - 18, cy), (cx + 18, cy)], fill=(40, 90, 255, 255), width=3)
    dr.line([(cx, cy - 18), (cx, cy + 18)], fill=(40, 90, 255, 255), width=3)
    return img


if __name__ == "__main__":
    main()
