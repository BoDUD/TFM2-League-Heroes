#!/usr/bin/env python3
"""Sion's step-2 pack for Codex (assets/source/sion/MODEL_STRIPS.md): every action frame drawn on the PPU design's own
grid, posed after League's animation.

    python tools/art/pack_sion_strips.py [--out dist/sion_packs/sion_strips_pack]

The design (tools/art/design_sion.py --hd -> assets/source/sion/hd/front.png: Codex's front draft read back square for
square, 101 x 75 squares, 28 colours; PPU 1.52 = 67 squares crown to soles for 44 game px) is the idle. Every action is
drawn from the 3/4 FRONT (the user dropped the side view: 「不要侧面，全用 3/4 正面」) and posed after League's animation.
The run is NOT in the pack: big heroes walk league_nautilus / league_braum's way on the idle (rig_galio.walk_frame; the
user: 「你向前那样冲刺模型永远会变形」); R's charge pose (ult) is drawn for its upper body only, its legs walk the same way.
The skeletons: tools/lol/native_pose.py on assets/source/sion/poses.json (--alpha) -> %TEMP%/sn_work/pose_n (yaw 30,
mirrored: he faces right), 8 render px a game px; the design pose is DESIGN_GP game px tall with the stake (native_pose's
print), the design its height in squares. Each frame's cell is scaled to PX px a square and placed with its pivot on the
canvas's standing point (column PIV_X, the soles' row SOLE): the pose, the place and the size.
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
SRC = os.path.join(ROOT, "assets", "source", "sion")
DESIGN = os.path.join(SRC, "hd", "front.png")
SPEC = os.path.join(SRC, "poses.json")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "sn_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips30")   # contact sheets at the pack's 3/4 camera (yaw 30, mirrored)
PICTURE = os.path.join(SRC, "codex_model", "raw", "sion-front-2-generated.png")
PX = 7                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 219, 146           # 1533 x 1022 inside the 1536 x 1024 canvas
SOLE = 140                      # the soles' row (the ground under it): room above for the axe raised overhead
PIV_X = 100                     # the standing point's column (the middle between his feet)
RS = 8                          # render px a game px in native_pose's renders
DESIGN_GP = 47                  # the design pose's height in game px with the stake (native_pose's print)
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot


def design():
    d = np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def feet_mid(d):
    """The middle column between his two boots: the bottom 4 rows right of the axe blade (columns >= 30)."""
    op = d[..., 3] > 0
    ys, xs = np.nonzero(op[-4:, 30:])
    xs = xs + 30
    return (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(tag, i, cell, cols):
    """Frame i of a tag's pose render on the pack canvas (1536 x 1024 RGBA)."""
    im = Image.open(os.path.join(POSE, f"sion_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    rows = design().shape[0]
    k = PX * rows / DESIGN_GP / RS                     # render px -> canvas px
    c = c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS)
    return c, k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "sion_packs", "sion_strips_pack"))
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
    Image.fromarray(up(d, PX)).save(os.path.join(out, "design", "sion_design.png"))
    Image.fromarray(d).save(os.path.join(out, "design", "sion_design_1x.png"))
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    cols = cols[np.argsort(cols.sum(axis=1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "sion_palette.png"))
    # the design on the pack canvas: its feet's middle on PIV_X, its soles on SOLE
    x0 = int(round(PIV_X + 0.5 - feet_mid(d) - 0.5))
    y0 = SOLE - (h - 1)
    can = np.zeros((1024 // PX + 1, COLS, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    big = Image.fromarray(up(can, PX)).crop((0, 0, 1536, 1024))
    big.save(os.path.join(out, "design", "sion_design_on_canvas.png"))
    lines(big.copy(), y0).save(os.path.join(out, "design", "sion_design_guide.png"))
    shutil.copyfile(PICTURE, os.path.join(out, "refs", "sion_picture_A.png"))
    for n in ("Sion_Attack1", "Sion_Spell1_CHRG", "Sion_Spell1_Hit2", "Sion_Spell3", "Sion_Spell2_B", "Sion_Spell4_RunIN",
              "Sion_Spell4_Hit", "Sion_Death"):
        p = os.path.join(CLIPS, n + ".png")
        if os.path.isfile(p):
            shutil.copyfile(p, os.path.join(out, "refs", f"league_{n[5:].lower()}.png"))

    spec = json.load(open(SPEC, encoding="utf-8"))
    cells = json.load(open(os.path.join(POSE, "sion_cells.json"), encoding="utf-8"))
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
            name = f"sion_{tag}_{i + 1}.png"
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
