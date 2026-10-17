#!/usr/bin/env python3
"""Tahm Kench's step-2 pack for Codex (assets/source/tahmkench/MODEL_STRIPS.md): every action frame drawn on the dense
design's own grid, posed after League's animations (pack_elise_strips.py's way, one form).

    python tools/art/pack_tahmkench_strips.py [--out dist/tahmkench_packs/tahmkench_strips_pack]

The design (tools/art/design_tahmkench_hd.py -> assets/source/tahmkench/hd/A.png, 151 x 125 squares, 40 colours; the
user's pick 2026-10-16: A) is the idle. The skeletons: tools/lol/native_pose.py on assets/source/tahmkench/poses.json
--alpha -> %TEMP%/tk_work/pose_n: League's clips through one camera (yaw 45, not mirrored: his front faces right), one
scale for every frame, 8 render px a game px; the design pose is 42 game px from the hat to the soles = the design's
125 rows. Each frame's cell is scaled to PX px a square and placed with its pivot on the canvas's standing point
(column PIV_X, the soles' row SOLE): the pose, the place and the size.
PX is 6: 1536 x 1020 at 6 px is 256 x 170 squares - room for the tongue to the right, the tail to the left and the
dive's leap above.
Abyssal Dive (skill2, w_land) is posed from the design itself (DESIGN_POSES: shifted and quarter-turned, cut at the
ground): League's dive turns to the camera and leaps out of any canvas.
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (the design at PX px a square, 1x, the palette, on the
canvas), now/ (skeletons), guide/ (the same with the lines), refs/ (the step-0 pictures A and B - B is the open
mouth - and League's clips as contact sheets: Riot's model, local only), cells.json (every frame: tag, index, ms).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "tahmkench")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "tk_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips")
PX = 6                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 256, 170           # 1536 x 1020 inside the 1536 x 1024 canvas
SOLE = 160                      # the soles' row (the ground under it)
PIV_X = 100                     # the standing point's column
GP = 42                         # the design pose's height in game px (poses.json "height")
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
HERO = "tahmkench"
# Abyssal Dive's frames posed from the design itself, not League's clips (his League dive turns to the camera and leaps
# straight up out of any canvas): (quarter turns counter-clockwise, columns right, rows up of the turned design's
# bottom over the soles' row); everything under the soles' row is cut (he is under the ground there)
DESIGN_POSES = {
    ("skill2", 0): (0, 0, 0),       # crouching to dive (the text says how)
    ("skill2", 1): (0, 6, 10),      # a hop up and forward
    ("skill2", 2): (-1, 14, -70),   # turned head-first down to the right, the front half under the ground
    ("skill2", 3): (-1, 18, -118),  # only the tail and the feet still out
    ("w_land", 0): (1, 4, -55),     # bursting up out of the ground mouth first, the lower half still under it
    ("w_land", 1): (0, 2, 16),      # out, in the air
    ("w_land", 2): (0, 0, 0),       # landing (the text: squashed wide)
    ("w_land", 3): (0, 0, 0),       # back to the standing pose
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def design():
    return np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA")).copy()


def feet_mid(d):
    """The middle column between the feet: the bottom 6 rows (the tail ends higher)."""
    ys, xs = np.nonzero(d[-6:, :, 3] > 0)
    return (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(tag, i, cell, cols):
    """Frame i of a tag's pose render, scaled to the pack's squares."""
    im = Image.open(os.path.join(POSE, f"{HERO}_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    k = PX * design().shape[0] / GP / RS                 # render px -> canvas px
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


def design_pose(d, x0, y0, turn, dx, dy):
    """The design turned by `turn` quarter turns, its feet's middle moved dx columns, its bottom dy rows over the soles'
    row, cut under the soles' row; at PX px a square on the canvas."""
    t = np.rot90(d, turn).copy()
    h, w = t.shape[:2]
    can = np.zeros((ROWS + 400, COLS + 400, 4), np.uint8)
    top = SOLE - (h - 1) - dy + 200
    left = (x0 if turn == 0 else PIV_X - w // 2) + dx + 200
    can[top:top + h, left:left + w] = t
    can = can[200:200 + ROWS, 200:200 + COLS].copy()
    can[SOLE + 1:] = 0
    big = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    big.paste(Image.fromarray(up(can, PX)), (0, 0))
    return big


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "tahmkench_packs", "tahmkench_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):          # its contents (the folder itself may be some shell's working directory)
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    d = design()
    h, w = d.shape[:2]
    Image.fromarray(up(d, PX)).save(os.path.join(out, "design", f"{HERO}_design.png"))
    Image.fromarray(d).save(os.path.join(out, "design", f"{HERO}_design_1x.png"))
    x0 = int(round(PIV_X - feet_mid(d)))
    y0 = SOLE - (h - 1)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    big = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    big.paste(Image.fromarray(up(can, PX)), (0, 0))
    big.save(os.path.join(out, "design", f"{HERO}_design_on_canvas.png"))
    lines(big.copy(), y0).save(os.path.join(out, "design", f"{HERO}_design_guide.png"))
    for pic in ("tahmkench-A.png", "tahmkench-B.png"):
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", pic)), os.path.join(out, "refs", pic))
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "design_squares": [w, h],
                "design_at": [x0, y0], "standing_point": [PIV_X, SOLE], "frames": []}

    cells = json.load(open(os.path.join(POSE, f"{HERO}_cells.json"), encoding="utf-8"))
    cell = cells["cell"]
    for tag, frames in cells["tags"].items():
        n_cols = 3 if len(frames) <= 6 else 4
        for i, fr in enumerate(frames):
            if (tag, i) in DESIGN_POSES:
                can_im = design_pose(d, x0, y0, *DESIGN_POSES[(tag, i)])
            else:
                sk, k = skeleton(tag, i, cell, n_cols)
                can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
                px, py = fr["pivot"]
                # the cell's pivot (game px) -> the canvas: x on PIV_X's centre, the soles on SOLE's bottom edge
                ox = round((PIV_X + 0.5) * PX - (px + 0.5) * RS * k)
                oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
                can_im.paste(sk, (ox, oy), sk)
            name = f"{HERO}_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            lines(can_im.copy(), y0).save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": fr["ms"]})
    cols = np.array(sorted({tuple(c) for c in d[d[..., 3] > 0][:, :3]}, key=lambda c: int(c[0]) + int(c[1]) + int(c[2])),
                    np.uint8)
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", f"{HERO}_palette.png"))
    for n in sorted(os.listdir(CLIPS)) if os.path.isdir(CLIPS) else []:
        shutil.copyfile(os.path.join(CLIPS, n), os.path.join(out, "refs", "league_" + n.lower()))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{len(cols)} colours; {len(manifest['frames'])} frames -> {zp}")
    print({k: manifest[k] for k in ("design_squares", "design_at", "standing_point")})


if __name__ == "__main__":
    main()
