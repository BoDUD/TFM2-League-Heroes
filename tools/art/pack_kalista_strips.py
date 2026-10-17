#!/usr/bin/env python3
"""Kalista's step-2 pack for Codex (assets/source/kalista/MODEL_STRIPS.md): every action frame drawn on the design's own
grid, posed after League's animations (pack_elise_strips.py's way, one form).

    python tools/lol/native_pose.py assets/source/kalista/poses.json --out %TEMP%/kl_work/pose --alpha
    python tools/art/pack_kalista_strips.py [--out %TEMP%/kl_work/kalista_strips_pack]

The design (tools/art/design_kalista_hd.py -> assets/source/kalista/hd/A.png, 122 x 98 squares, 40 colours; the
user's pick 2026-10-15: A, League's idle: a low lunge, the spear held low behind her) is the idle; every action
keeps its 3/4 front view facing right (one face in every frame). The skeletons: native_pose on poses.json (yaw 45,
not mirrored: her front faces right), one scale for every frame, 8 render px a game px; the design pose is GP game px
from the crown (the helm's top, row CROWN of the design; the crest and the horn tips above it) to the soles. Each
frame's cell is scaled to PX px a square and placed with its pivot on the canvas's standing point (column PIV_X, the
soles' row SOLE): the pose, the place and the size. PX 7: 1533 x 1022 is 219 x 146 squares, room above her for the
raised arm of R's call and the spear raised for Q.
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
SRC = os.path.join(ROOT, "assets", "source", "kalista")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "kl_work")
POSE = os.path.join(TMP, "pose")
CLIPS = os.path.join(TMP, "look2")
PX = 7                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 219, 146           # 1533 x 1022 inside the 1536 x 1024 canvas
SOLE = 138                      # the soles' row (the ground under it)
PIV_X = 130                     # the standing point's column (the spear reaches back to the left)
CROWN = 20                      # the helm's top in the design (the crest and the horn tips above it)
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
GP = 38                         # poses.json "height": the design pose, crown to soles, in game px
CLIP_SHEETS = ["Kalista_Attack1", "Kalista_Attack1_Dash_180", "Kalista_Spell3", "Kalista_Spell4_Call", "Kalista_Death"]
LOOK = os.path.join(TMP, "look")      # the first contact sheets
LOOK_SHEETS = ["Kalista_Idle1", "Kalista_Run1", "Kalista_Spell1", "Kalista_Spell4_Throw", "Kalista_Attack1_Dash_0"]


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
    im = Image.open(os.path.join(POSE, f"kalista_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    k = PX * (rows_design - CROWN) / GP / RS           # render px -> canvas px
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
    ap.add_argument("--out", default=os.path.join(TMP, "kalista_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    des = design("A.png")
    h, w = des.shape[:2]
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE],
                "design_squares": [w, h], "crown_row": CROWN, "frames": []}
    Image.fromarray(up(des, PX)).save(os.path.join(out, "design", "kalista_design.png"))
    Image.fromarray(des).save(os.path.join(out, "design", "kalista_design_1x.png"))
    big, x0, y0 = on_canvas(des)
    big.save(os.path.join(out, "design", "kalista_design_on_canvas.png"))
    lines(big.copy(), y0).save(os.path.join(out, "design", "kalista_design_guide.png"))
    manifest["design_at"] = [x0, y0]
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "raw", "kalista-A-original.png")),
                    os.path.join(out, "refs", "kalista-A.png"))

    cells = json.load(open(os.path.join(POSE, "kalista_cells.json"), encoding="utf-8"))
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
            name = f"kalista_{tag}_{i + 1}.png"
            can_im.save(os.path.join(out, "now", name))
            g = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
            g.alpha_composite(can_im)
            lines(g, y0).convert("RGB").save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": fr["ms"]})
    cols = np.unique(des[des[..., 3] > 0][:, :3], axis=0)
    cols = cols[np.argsort(cols.astype(int).sum(1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "kalista_palette.png"))
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
