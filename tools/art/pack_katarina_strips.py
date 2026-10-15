#!/usr/bin/env python3
"""Katarina's step-2 pack for Codex (assets/source/katarina/MODEL_STRIPS.md): every action frame drawn on the side
design's own grid, posed after League's animations (pack_milio_strips.py's way).

    python tools/lol/native_pose.py assets/source/katarina/poses.json --out %TEMP%/kt_packs/pose --alpha
    python tools/art/pack_katarina_strips.py [--out %TEMP%/kt_packs/katarina_strips_pack]

The designs (tools/art/design_katarina_hd.py, one 40-colour palette; the user picked K1 and side-1, 2026-10-15):
assets/source/katarina/hd/front.png (the idle and the ban/pick card), side.png (three quarters to the side facing
right with the front's head, memory one-face-all-frames). Every action is side-on facing right (memory
side-view-design); the idle and the hit are made from the designs by Claude.
The skeletons: tools/lol/native_pose.py on assets/source/katarina/poses.json -> %TEMP%/kt_packs/pose: League's clips
through one camera (yaw 60), one scale for every frame, 8 render px a game px; the design pose is GP game px from the
crown to the soles, the side design's rows over it make one square. Each frame's cell is scaled to PX px a square and
placed with its pivot on the canvas's standing point (column PIV_X, the soles' row SOLE).
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (the side design and the front at PX px a square, 1x, the
palette, on the canvas), now/ (skeletons), guide/ (the same with the lines), refs/ (League's clips as contact sheets -
Riot's model: local only), cells.json (every frame: tag, index, ms).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "katarina")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "kt_packs")
POSE = os.path.join(TMP, "pose")
CLIPS = os.path.join(TMP, "clips")
PX = 8                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 192, 128           # 1536 x 1024
SOLE = 118                      # the boots' row (the ground under it)
PIV_X = 90                      # the standing point's column
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
GP = 38                         # poses.json "height": the design pose, crown to soles, in game px
CLIP_SHEETS = ["katarina_run", "katarina_attack1", "katarina_spell1", "katarina_spell2_Throw", "katarina_spell3",
               "katarina_spell2", "katarina_spell4", "katarina_death"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def design(name):
    return crop(np.asarray(Image.open(lp(os.path.join(SRC, "hd", name))).convert("RGBA")))


def feet_mid(d):
    """The middle column between the feet: the bottom 4 rows."""
    ys, xs = np.nonzero(d[-4:, :, 3] > 0)
    return (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(tag, i, cell, cols, rows_design):
    """Frame i of a tag's pose render, scaled to the pack's squares."""
    im = Image.open(os.path.join(POSE, f"katarina_pose_{tag}.png")).convert("RGBA")
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
    ap.add_argument("--out", default=os.path.join(TMP, "katarina_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    side, front = design("side.png"), design("front.png")
    h, w = side.shape[:2]
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE],
                "design_squares": [w, h], "frames": []}
    for name, d in (("side", side), ("front", front)):
        Image.fromarray(up(d, PX)).save(os.path.join(out, "design", f"katarina_{name}_design.png"))
        Image.fromarray(d).save(os.path.join(out, "design", f"katarina_{name}_design_1x.png"))
    head = crop(np.asarray(Image.open(lp(os.path.join(SRC, "hd", "head.png"))).convert("RGBA")))
    Image.fromarray(up(head, PX * 2)).save(os.path.join(out, "design", "katarina_head_x2.png"))
    big, x0, y0 = on_canvas(side)
    big.save(os.path.join(out, "design", "katarina_side_design_on_canvas.png"))
    lines(big.copy(), y0).save(os.path.join(out, "design", "katarina_side_design_guide.png"))
    manifest["design_at"] = [x0, y0]
    shutil.copyfile(lp(os.path.join(SRC, "codex_side", "katarina-side-1.png")),
                    os.path.join(out, "refs", "katarina-side-1.png"))

    cells = json.load(open(os.path.join(POSE, "katarina_cells.json"), encoding="utf-8"))
    cell = cells["cell"]
    for tag, frames in cells["tags"].items():
        n_cols = 3 if len(frames) <= 6 and len(frames) != 4 else 4
        for i, fr in enumerate(frames):
            sk, k = skeleton(tag, i, cell, n_cols, h)
            can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
            px, py = fr["pivot"]
            ox = round((PIV_X + 0.5) * PX - (px + 0.5) * RS * k)
            oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
            can_im.paste(sk, (ox, oy), sk)
            name = f"katarina_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            g = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
            g.alpha_composite(can_im)
            lines(g, y0).convert("RGB").save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": fr["ms"]})
    cols = np.unique(np.concatenate([side[side[..., 3] > 0][:, :3], front[front[..., 3] > 0][:, :3]]), axis=0)
    cols = cols[np.argsort(cols.astype(int).sum(1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "katarina_palette.png"))
    for n in CLIP_SHEETS:
        p = os.path.join(CLIPS, n + ".png")
        if os.path.exists(p):
            shutil.copyfile(p, os.path.join(out, "refs", "league_" + n.lower() + ".png"))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(lp(DOC), os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{len(cols)} colours; {len(manifest['frames'])} frames; design {w}x{h} at {x0},{y0} -> {zp}")


if __name__ == "__main__":
    main()
