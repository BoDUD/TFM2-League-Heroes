#!/usr/bin/env python3
"""Pantheon's step-2 pack for Codex (assets/source/pantheon/MODEL_STRIPS.md): every action frame drawn on the design's
own grid, posed after League's animations (pack_pantheon_strips.py's way).

    python tools/lol/native_pose.py assets/source/pantheon/poses.json --out %TEMP%/pn_work/pose --alpha
    python tools/art/pack_pantheon_strips.py [--out %TEMP%/pn_work/pantheon_strips_pack]

The design (tools/art/design_pantheon_cut.py -> assets/source/pantheon/hd/design.png = model1_cut.png, 66 x 66 squares,
39 colours; the user's picks 2026-10-16: 「选A 40尺寸 PPU1.5」 then 「造型用第1稿删行列的版本」 - League's idle, the spear
held low in the near hand, the shield on the far arm) is the idle at the final density (1.5 squares a game pixel: no
rescale after), every action keeps its 3/4 front view facing right. The skeletons: native_pose on poses.json (yaw 45,
not mirrored), one scale for every frame, 8 render px a game px; the design pose is GP game px from the crest top
(row CROWN) to the soles. Each frame's cell is scaled to PX px a square and placed with its pivot on the canvas's
standing point (column PIV_X, the soles' row SOLE). PX 10: 1530 x 1530 is 153 x 153 squares - 74 rows above his crest
for the leaps, the vault and the raised spear, the thrusts reaching right.
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (the design at PX px a square, 1x, the palette, on the canvas),
now/ (skeletons), guide/ (the same with the lines), refs/ (the picture, League's clips as contact sheets - Riot's
model: local only), cells.json (every frame: tag, index, ms).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "pantheon")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "pn_work")
POSE = os.path.join(TMP, "pose")
CLIPS = os.path.join(TMP, "look")
PX = 10                         # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 153, 153           # 1530 x 1530 inside the 1536 x 1536 canvas
CW, CH = 1536, 1536             # the canvas
SOLE = 140                      # the soles' row (the ground under it)
PIV_X = 66                      # the standing point's column (the cape flies left, the thrusts reach right)
CROWN = 0                       # the crest top: the design's first row
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
GP = 44                         # poses.json "height": the design pose, crest top to soles, in game px
CLIP_SHEETS = ["Pantheon_Run_base", "Pantheon_attack1", "Pantheon_spell1_nomove", "Pantheon_spell3_loop_nomove_0", "Pantheon_spell4"]
LOOK = os.path.join(TMP, "look2")
LOOK_SHEETS = ["Pantheon_attack2", "Pantheon_spell1_hit", "Pantheon_spell1_longhit", "Pantheon_spell2", "Pantheon_spell2_hit",
               "Pantheon_spell3_hit", "Pantheon_spell4_leap", "Pantheon_spell4_hit", "Pantheon_Death"]


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
    im = Image.open(os.path.join(POSE, f"pantheon_pose_{tag}.png")).convert("RGBA")
    cw, ch = cell[0] * RS, cell[1] * RS       # cells are not square (pack_kalista_strips cut rows by the width)
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * ch, (cx + 1) * cw, (cy + 1) * ch))
    k = PX * (rows_design - CROWN) / GP / RS           # render px -> canvas px
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


def lines(img, top):
    """The grid's lines: every 10th square light grey, the design's top row (blue), the soles' row (red), the standing
    point (blue cross)."""
    dr = ImageDraw.Draw(img)
    for c in range(0, COLS + 1, 10):
        dr.line([(c * PX, 0), (c * PX, CH)], fill=(200, 200, 200, 90))
    for r in range(0, ROWS + 1, 10):
        dr.line([(0, r * PX), (CW, r * PX)], fill=(200, 200, 200, 90))
    dr.line([(0, top * PX), (CW, top * PX)], fill=(40, 90, 255, 255), width=2)
    dr.line([(0, (SOLE + 1) * PX), (CW, (SOLE + 1) * PX)], fill=(255, 40, 40, 255), width=2)
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
    big = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    big.paste(Image.fromarray(up(can, PX)), (0, 0))
    return big, x0, y0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "pantheon_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    des = design("design.png")
    h, w = des.shape[:2]
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE],
                "design_squares": [w, h], "crown_row": CROWN, "frames": []}
    Image.fromarray(up(des, PX)).save(os.path.join(out, "design", "pantheon_design.png"))
    Image.fromarray(des).save(os.path.join(out, "design", "pantheon_design_1x.png"))
    big, x0, y0 = on_canvas(des)
    big.save(os.path.join(out, "design", "pantheon_design_on_canvas.png"))
    lines(big.copy(), y0).save(os.path.join(out, "design", "pantheon_design_guide.png"))
    manifest["design_at"] = [x0, y0]
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "pantheon-picture", "pantheon-A.png")), os.path.join(out, "refs", "pantheon-A.png"))
    # the picked take of step 1, the look at this size
    shutil.copyfile(lp(os.path.join(SRC, "codex_model", "pantheon-model-1.png")), os.path.join(out, "refs", "pantheon-model-1.png"))

    cells = json.load(open(os.path.join(POSE, "pantheon_cells.json"), encoding="utf-8"))
    cell = cells["cell"]
    for tag, frames in cells["tags"].items():
        n_cols = 3 if len(frames) <= 6 and len(frames) != 4 else 4
        for i, fr in enumerate(frames):
            sk, k = skeleton(tag, i, cell, n_cols, h)
            can_im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
            px, py = fr["pivot"]
            ox = round((PIV_X + 0.5) * PX - (px + 0.5) * RS * k)
            oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
            can_im.paste(sk, (ox, oy), sk)
            name = f"pantheon_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            g = Image.new("RGBA", (CW, CH), (255, 255, 255, 255))
            g.alpha_composite(can_im)
            lines(g, y0).convert("RGB").save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": fr["ms"]})
    cols = np.unique(des[des[..., 3] > 0][:, :3], axis=0)
    cols = cols[np.argsort(cols.astype(int).sum(1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "pantheon_palette.png"))
    for folder, names in ((CLIPS, CLIP_SHEETS), (LOOK, LOOK_SHEETS)):
        for n in names:
            p = os.path.join(folder, n + ".png")
            if os.path.exists(p):
                shutil.copyfile(p, os.path.join(out, "refs", "league_" + n.lower() + ".png"))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(lp(DOC), os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{len(cols)} colours; {len(manifest['frames'])} frames; design {w}x{h} at {x0},{y0} -> {zp}")


if __name__ == "__main__":
    main()
