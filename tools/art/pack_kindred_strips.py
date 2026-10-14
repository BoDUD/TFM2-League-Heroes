#!/usr/bin/env python3
"""Kindred's step-2 pack for Codex (assets/source/kindred/MODEL_STRIPS.md): every action frame of Lamb drawn on the dense
side design's own grid, posed after League's animations, and the Wolf's own short strips.

    python tools/art/pack_kindred_strips.py [--out dist/kindred_packs/kindred_strips_pack]

The designs (tools/art/design_kindred_hd.py, one 40-colour palette; the user picked side A, 2026-10-14):
assets/source/kindred/hd/front.png (the idle and the ban/pick card, Lamb with the Wolf behind her hips) and side.png
(Lamb in full profile facing right with the front's 3/4 mask head, memory one-face-all-frames); side_wolf.png (the Wolf
in profile). Every Lamb action is side-on facing right (memory side-view-design); the bow is one rigid piece (moved,
or held level when drawn). The Wolf is a layer of its own, put into her frames by Claude: Codex draws only its
floating loop and its lunge.
The skeletons: tools/lol/native_pose.py on assets/source/kindred/poses.json -> %TEMP%/kn_work/pose_n: League's clips
through one side camera (yaw 70), one scale for every frame, 8 render px a game px; the design pose is GP game px from
the crown to the soles, so a design square is that over the side design's ear-to-hoof rows. Each frame's cell is scaled
to PX px a square and placed with its pivot on the canvas's standing point (column PIV_X, the soles' row SOLE).
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (the side design and the wolf at PX px a square, 1x, the
palette, on the canvas; the front for the look), now/ (skeletons), guide/ (the same with the lines), refs/ (League's
clips as contact sheets - Riot's model: local only), cells.json (every frame: tag, index, ms).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "kindred")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "kn_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips")
PX = 5                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 307, 204           # 1535 x 1020 inside the 1536 x 1024 canvas
SOLE = 196                      # the hooves' row (the ground under it)
PIV_X = 165                     # the standing point's column (her fur tail reaches ~150 squares behind her)
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
GP = 34                         # poses.json "height": the design pose, crown to soles, in game px
EAR_ROW = 12                    # the mask's ear tips in hd/side.png (uncropped); the bow tip is row 0
CLIP_SHEETS = ["Lamb_run", "Lamb_Attack1", "Lamb_Spell1Forward", "Lamb_Spell2", "Lamb_Spell3", "Lamb_Spell4",
               "Lamb_Death", "Wolf_W_Attack1", "Wolf_Run_01", "Wolf_Idle_base_movement"]
# the Wolf's own strips: its profile design on a canvas of the same grid, its nose tip at WOLF_NOSE (col, row)
WOLF_NOSE = (150, 120)
WOLF_TAGS = {"wolf_float": 4, "wolf_bite": 5}


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def design(name):
    return crop(np.asarray(Image.open(os.path.join(SRC, "hd", name)).convert("RGBA")))


def feet_mid(d):
    """The middle column between the feet: the bottom 4 rows."""
    ys, xs = np.nonzero(d[-4:, :, 3] > 0)
    return (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(tag, i, cell, cols, rows_design):
    """Frame i of a tag's pose render, scaled to the pack's squares."""
    im = Image.open(os.path.join(POSE, f"kindred_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    k = PX * rows_design / GP / RS                     # render px -> canvas px
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


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


def on_canvas(d):
    h, w = d.shape[:2]
    x0 = int(round(PIV_X - feet_mid(d)))
    y0 = SOLE - (h - 1)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    big = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    big.paste(Image.fromarray(up(can, PX)), (0, 0))
    return big, x0, y0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "kindred_packs", "kindred_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):          # its contents (the folder itself may be some shell's working directory)
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    raw_side = np.asarray(Image.open(os.path.join(SRC, "hd", "side.png")).convert("RGBA"))
    top = int(np.nonzero(raw_side[..., 3].any(1))[0].min())
    side, front, wolf = design("side.png"), design("front.png"), design("side_wolf.png")
    h, w = side.shape[:2]
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE],
                "design_squares": [w, h], "frames": []}
    for name, d in (("side", side), ("front", front), ("wolf", wolf)):
        Image.fromarray(up(d, PX)).save(os.path.join(out, "design", f"kindred_{name}_design.png"))
        Image.fromarray(d).save(os.path.join(out, "design", f"kindred_{name}_design_1x.png"))
    big, x0, y0 = on_canvas(side)
    y_ear = y0 + EAR_ROW - top
    big.save(os.path.join(out, "design", "kindred_side_design_on_canvas.png"))
    lines(big.copy(), y_ear).save(os.path.join(out, "design", "kindred_side_design_guide.png"))
    manifest["design_at"] = [x0, y0]
    shutil.copyfile(os.path.join(SRC, "codex_picture", "kindred-model-B.png"), os.path.join(out, "refs", "kindred-model-B.png"))
    # the Wolf on its own canvas: nose tip (its rightmost column, the middle of that column's squares) at WOLF_NOSE
    wcan = np.zeros((ROWS, COLS, 4), np.uint8)
    wh, ww = wolf.shape[:2]
    ny = int(np.nonzero(wolf[:, -1, 3])[0].mean())
    wx0, wy0 = WOLF_NOSE[0] - ww + 1, WOLF_NOSE[1] - ny
    wcan[wy0:wy0 + wh, wx0:wx0 + ww] = wolf
    wbig = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    wbig.paste(Image.fromarray(up(wcan, PX)), (0, 0))
    wbig.save(os.path.join(out, "design", "kindred_wolf_design_on_canvas.png"))
    manifest["wolf_at"] = [wx0, wy0]
    for tag, n in WOLF_TAGS.items():
        for i in range(n):
            manifest["frames"].append({"file": f"kindred_{tag}_{i + 1}.png", "tag": tag, "index": i, "ms": 100})

    cells = json.load(open(os.path.join(POSE, "kindred_cells.json"), encoding="utf-8"))
    cell = cells["cell"]
    rows_design = (int(np.nonzero(raw_side[..., 3].any(1))[0].max()) + 1) - EAR_ROW   # ear tips -> hooves
    for tag, frames in cells["tags"].items():
        n_cols = 3 if len(frames) <= 6 and len(frames) != 4 else 4
        for i, fr in enumerate(frames):
            sk, k = skeleton(tag, i, cell, n_cols, rows_design)
            can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
            px, py = fr["pivot"]
            ox = round((PIV_X + 0.5) * PX - (px + 0.5) * RS * k)
            oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
            can_im.paste(sk, (ox, oy), sk)
            name = f"kindred_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            lines(can_im.copy(), y_ear).save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": fr["ms"]})
    both = np.concatenate([side[side[..., 3] > 0][:, :3], wolf[wolf[..., 3] > 0][:, :3]])
    cols = np.unique(both, axis=0)
    cols = cols[np.argsort(cols.astype(int).sum(1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "kindred_palette.png"))
    for n in CLIP_SHEETS:
        p = os.path.join(CLIPS, n + ".png")
        if os.path.exists(p):
            shutil.copyfile(p, os.path.join(out, "refs", "league_" + n.lower() + ".png"))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{len(cols)} colours; {len(manifest['frames'])} frames; design {w}x{h} at {x0},{y0} -> {zp}")


if __name__ == "__main__":
    main()
