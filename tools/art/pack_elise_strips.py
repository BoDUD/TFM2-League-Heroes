#!/usr/bin/env python3
"""Elise's step-2 pack for Codex (assets/source/elise/MODEL_STRIPS.md): every action frame of both forms drawn on the
dense designs' own grid, posed after League's animations (pack_nidalee_strips.py's way).

    python tools/art/pack_elise_strips.py [--out dist/elise_packs/elise_strips_pack]

The designs (tools/art/design_elise_hd.py -> assets/source/elise/hd/human.png 83 x 124 squares and spider.png
114 x 72, one 40-colour palette; the user's picks 2026-10-15: human B, spider A) are the idles. Both forms keep the
designs' view in every action: the human 3/4 front (one face in every frame), the spider 3/4 facing right.
The skeletons: tools/lol/native_pose.py on assets/source/elise/poses_human.json / poses_spider.json (--alpha) ->
%TEMP%/el_work/pose_n: League's clips through one camera per form (yaw 45, not mirrored: her front faces right), one
scale for every frame, 8 render px a game px; the human design pose is 38 game px from the crown to the toes = 100
design rows (the crown on design row 24, the spider legs and hair horns above it), the spider's whole render matched
to the whole design. Each frame's cell is scaled to PX px a square and placed with its pivot on the canvas's standing
point (column piv_x, the toes' row SOLE): the pose, the place and the size.
PX is 7: the human design is 124 squares tall with the raised back legs; 1533 x 1022 at 7 px is 219 x 146 squares.
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (each design at PX px a square, 1x, the palette, on the
canvas), now/ (skeletons), guide/ (the same with the lines), refs/ (the pictures, League's clips as contact sheets -
Riot's model: local only), cells.json (every frame: form, tag, index, ms, standing point).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "elise")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "el_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips")
PX = 7                          # pixels a square in the pack (one square = one dense pixel)
COLS, ROWS = 219, 146           # 1533 x 1022 inside the 1536 x 1024 canvas
SOLE = 138                      # the toes' row (the ground under it)
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
# form -> design file, native_pose hero name, crown row in the design (the head's top, the spider legs / hair horns above it
# not counted, as native_pose measures), the design pose's height in game px (poses_*.json "height"; None: scale the
# design pose's whole render to the whole design), the standing
# point's column on the canvas, how to find the design's feet middle (columns of the bottom rows to look in)
FORMS = {
    "human": {"design": "human.png", "hero": "elise", "crown": 24, "gp": 38, "piv_x": 105, "feet": (0, 83),
              "picture": "elise-human-B.png"},
    "spider": {"design": "spider.png", "hero": "elise_spider", "crown": 0, "gp": None, "piv_x": 110, "feet": (0, 114),
               "picture": "elise-spider-A.png"},
}


def design(form):
    return np.asarray(Image.open(os.path.join(SRC, "hd", FORMS[form]["design"])).convert("RGBA")).copy()


def feet_mid(d, form):
    """The middle column between the feet (toes / claw tips): the bottom 6 rows, inside the form's column range."""
    lo, hi = FORMS[form]["feet"]
    op = d[..., 3] > 0
    ys, xs = np.nonzero(op[-6:, lo:hi])
    return lo + (xs.min() + xs.max()) / 2.0


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(form, tag, i, cell, cols):
    """Frame i of a tag's pose render, scaled to the pack's squares."""
    f = FORMS[form]
    im = Image.open(os.path.join(POSE, f"{f['hero']}_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    rows = design(form).shape[0] - f["crown"]
    if f["gp"]:
        k = PX * rows / f["gp"] / RS                   # render px -> canvas px
    else:
        # the spider: no crown to measure, so the design pose's whole render is matched to the whole design
        des = np.asarray(Image.open(os.path.join(POSE, f"{f['hero']}_pose_design.png")).convert("RGBA")).astype(int)
        ys = np.nonzero((np.abs(des - des[0, 0]).sum(2) > 30).any(1))[0]      # on the render's grey ground
        k = PX * rows / (ys.max() - ys.min() + 1)
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


def lines(img, top, piv_x):
    """The grid's lines: every 10th square light grey, the design's top row (blue), the soles' row (red), the standing
    point (blue cross)."""
    dr = ImageDraw.Draw(img)
    for c in range(0, COLS + 1, 10):
        dr.line([(c * PX, 0), (c * PX, 1024)], fill=(200, 200, 200, 90))
    for r in range(0, ROWS + 1, 10):
        dr.line([(0, r * PX), (1536, r * PX)], fill=(200, 200, 200, 90))
    dr.line([(0, top * PX), (1536, top * PX)], fill=(40, 90, 255, 255), width=2)
    dr.line([(0, (SOLE + 1) * PX), (1536, (SOLE + 1) * PX)], fill=(255, 40, 40, 255), width=2)
    cx, cy = (piv_x + 0.5) * PX, (SOLE + 1) * PX
    dr.line([(cx - 18, cy), (cx + 18, cy)], fill=(40, 90, 255, 255), width=3)
    dr.line([(cx, cy - 18), (cx, cy + 18)], fill=(40, 90, 255, 255), width=3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "elise_packs", "elise_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):          # its contents (the folder itself may be some shell's working directory)
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "forms": {}, "frames": []}
    pal_cols = set()
    for form, f in FORMS.items():
        d = design(form)
        h, w = d.shape[:2]
        pal_cols |= {tuple(c) for c in d[d[..., 3] > 0][:, :3]}
        Image.fromarray(up(d, PX)).save(os.path.join(out, "design", f"elise_{form}_design.png"))
        Image.fromarray(d).save(os.path.join(out, "design", f"elise_{form}_design_1x.png"))
        # the design on the pack canvas: its feet's middle on piv_x, its soles on SOLE
        x0 = int(round(f["piv_x"] - feet_mid(d, form)))
        y0 = SOLE - (h - 1)
        can = np.zeros((ROWS, COLS, 4), np.uint8)
        can[y0:y0 + h, x0:x0 + w] = d
        big = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
        big.paste(Image.fromarray(up(can, PX)), (0, 0))
        big.save(os.path.join(out, "design", f"elise_{form}_design_on_canvas.png"))
        lines(big.copy(), y0, f["piv_x"]).save(os.path.join(out, "design", f"elise_{form}_design_guide.png"))
        shutil.copyfile(os.path.join(SRC, "codex_picture", f["picture"]), os.path.join(out, "refs", f["picture"]))
        manifest["forms"][form] = {"design_squares": [w, h], "design_at": [x0, y0], "standing_point": [f["piv_x"], SOLE]}

        cells = json.load(open(os.path.join(POSE, f"{f['hero']}_cells.json"), encoding="utf-8"))
        cell = cells["cell"]
        for tag, frames in cells["tags"].items():
            n_cols = 3 if len(frames) <= 6 else 4
            for i, fr in enumerate(frames):
                sk, k = skeleton(form, tag, i, cell, n_cols)
                can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
                px, py = fr["pivot"]
                # the cell's pivot (game px) -> the canvas: x on piv_x's centre, the soles on SOLE's bottom edge
                ox = round((f["piv_x"] + 0.5) * PX - (px + 0.5) * RS * k)
                oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
                can_im.paste(sk, (ox, oy), sk)
                name = f"elise_{tag}_{i + 1}.png"
                can_im.save(os.path.join(out, "now", name))
                lines(can_im.copy(), y0, f["piv_x"]).save(os.path.join(out, "guide", name))
                manifest["frames"].append({"file": name, "form": form, "tag": tag, "index": i, "ms": fr["ms"]})
    cols = np.array(sorted(pal_cols, key=lambda c: int(c[0]) + int(c[1]) + int(c[2])), np.uint8)
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "elise_palette.png"))
    for n in sorted(os.listdir(CLIPS)) if os.path.isdir(CLIPS) else []:
        shutil.copyfile(os.path.join(CLIPS, n), os.path.join(out, "refs", "league_" + n.lower()))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{len(cols)} colours; {len(manifest['frames'])} frames -> {zp}")
    for form, m in manifest["forms"].items():
        print(form, m)


if __name__ == "__main__":
    main()
