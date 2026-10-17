#!/usr/bin/env python3
"""Jayce's step-2 pack for Codex (assets/source/jayce/MODEL_STRIPS.md): every action frame of both forms drawn on the
side designs' own grid, posed after League's animations.

    python tools/art/pack_jayce_strips.py [--out dist/jayce_packs/jayce_strips_pack]

The designs (tools/art/design_jayce_hd.py, one 40-colour palette, ~2.6 squares a game pixel = Codex's own density; the
user's picks 2026-10-15: hammer A2 / cannon B2 fronts, side-2 of each, 3/4 to the right): assets/source/jayce/hd/
hammer_side.png and cannon_side.png (the bases of every action, memory side-view-design), hammer_front.png /
cannon_front.png (the idles and the ban/pick card), head.png (the one face, memory one-face-all-frames). Every frame is
brought to PPU 1.5 only at the end (ppu_restyle), Milio's way.
The skeletons: tools/lol/native_pose.py on assets/source/jayce/poses_hammer.json / poses_cannon.json ->
%TEMP%/jy_work/pose_n: League's clips through one camera (yaw 60), one scale for every frame, RS render px a game px;
the design pose is GP game px from the crown to the soles, the side design's crown-to-soles rows over it make one
square. Each frame's cell is scaled to PX px a square and placed with its pivot on the canvas's standing point (column
PIV_X, the soles' row SOLE). Tags (TFM2 names; the kit's build_jayce.py plays them): hammer run attack skill (To the
Skies) skill2 (Thundering Blow) w_cast (Lightning Field) tf_c (hammer -> cannon) dead; cannon c_run c_attack c_skill
(Shock Blast) c_skill2 (Hyper Charge) ult (Acceleration Gate + the gated Shock Blast) tf_h (cannon -> hammer). The
idles, hit and the cannon's idle are made from the designs (Claude).
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (both side designs and fronts at PX px a square, 1x, the
palette, the side designs on the canvas), now/ (skeletons), guide/ (the same with the lines), refs/ (League's clips as
contact sheets - Riot's model: local only), cells.json (every frame: form, tag, index, ms).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "jayce")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "jy_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips")
PX = 5                          # pixels a square in the pack (one square = one design pixel)
COLS, ROWS = 307, 204           # 1535 x 1020 inside the 1536 x 1024 canvas
SOLE = 196                      # the boots' row (the ground under it)
PIV_X = 120                     # the standing point's column
RS = 8                          # render px a game px in native_pose's renders
SOLE_BELOW_PIVOT = 11           # native_pose: the soles 11 game px under a cell's pivot
GP = 38                         # poses_*.json "height": the design pose, crown to soles, in game px
CLIP_SHEETS = ["jayce_melee_run1", "jayce_melee_attack1", "jayce_melee_spell1", "jayce_melee_spell3",
               "jayce_ranged_run1", "jayce_ranged_attack1", "jayce_ranged_spell1", "Jayce_ranged_spell3",
               "jayce_ranged_spell2_attack1", "Jayce_death"]


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def skeleton(form, tag, i, cell, cols, rows_design):
    """Frame i of a tag's pose render, scaled to the pack's squares."""
    im = Image.open(os.path.join(POSE, f"jayce_{form}_pose_{tag}.png")).convert("RGBA")
    cw = cell[0] * RS
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    a = np.asarray(c).copy()
    grey = np.abs(a[..., :3].astype(int) - a[0, 0, :3].astype(int)).sum(-1) < 30
    a[grey] = 0
    c = Image.fromarray(a)
    k = PX * rows_design / GP / RS                     # render px -> canvas px
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


def lines(img, top):
    """The grid's lines: every 10th square light grey, the design's crown row (blue), the soles' row (red), the standing
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


def on_canvas(d, mid):
    h, w = d.shape[:2]
    x0 = int(round(PIV_X - mid))
    y0 = SOLE - (h - 1)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[y0:y0 + h, x0:x0 + w] = d
    big = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    big.paste(Image.fromarray(up(can, PX)), (0, 0))
    return big, x0, y0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "jayce_packs", "jayce_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            q = os.path.join(out, e)
            shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    info = json.load(open(os.path.join(SRC, "hd", "design.json"), encoding="utf-8"))
    manifest = {"px_per_square": PX, "grid": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE],
                "forms": {}, "frames": []}
    allcols = []
    for form in ("hammer", "cannon"):
        side = np.asarray(Image.open(os.path.join(SRC, "hd", f"{form}_side.png")).convert("RGBA"))
        front = np.asarray(Image.open(os.path.join(SRC, "hd", f"{form}_front.png")).convert("RGBA"))
        di = info["designs"][f"{form}_side"]
        rows_design = di["soles"] - di["crown"] + 1
        for name, d in (("side", side), ("front", front)):
            Image.fromarray(up(d, PX)).save(os.path.join(out, "design", f"jayce_{form}_{name}_design.png"))
            Image.fromarray(d).save(os.path.join(out, "design", f"jayce_{form}_{name}_design_1x.png"))
            allcols.append(d[d[..., 3] > 0][:, :3])
        big, x0, y0 = on_canvas(side, di["standing_col"])
        big.save(os.path.join(out, "design", f"jayce_{form}_side_on_canvas.png"))
        crown = y0 + di["crown"]
        g = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
        g.alpha_composite(big)
        lines(g, crown).convert("RGB").save(os.path.join(out, "design", f"jayce_{form}_side_guide.png"))
        manifest["forms"][form] = {"design_squares": [int(side.shape[1]), int(side.shape[0])], "design_at": [x0, y0],
                                   "crown_row": int(crown), "crown_to_soles": int(rows_design)}
        cells = json.load(open(os.path.join(POSE, f"jayce_{form}_cells.json"), encoding="utf-8"))
        cell = cells["cell"]
        for tag, frames in cells["tags"].items():
            n_cols = 3 if len(frames) <= 6 and len(frames) != 4 else 4
            for i, fr in enumerate(frames):
                sk, k = skeleton(form, tag, i, cell, n_cols, rows_design)
                can_im = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
                px, py = fr["pivot"]
                ox = round((PIV_X + 0.5) * PX - (px + 0.5) * RS * k)
                oy = round((SOLE + 1) * PX - (py + SOLE_BELOW_PIVOT) * RS * k)
                can_im.paste(sk, (ox, oy), sk)
                name = f"jayce_{tag}_{i + 1}.png"
                can_im.save(os.path.join(out, "now", name))
                gi = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
                gi.alpha_composite(can_im)
                lines(gi, crown).convert("RGB").save(os.path.join(out, "guide", name))
                manifest["frames"].append({"file": name, "form": form, "tag": tag, "index": i, "ms": fr["ms"]})
    shutil.copyfile(os.path.join(SRC, "hd", "head.png"), os.path.join(out, "design", "jayce_head_1x.png"))
    head = np.asarray(Image.open(os.path.join(SRC, "hd", "head.png")).convert("RGBA"))
    Image.fromarray(up(head, PX)).save(os.path.join(out, "design", "jayce_head.png"))
    cols = np.unique(np.concatenate(allcols), axis=0)
    cols = cols[np.argsort(cols.astype(int).sum(1))]
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols, 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "jayce_palette.png"))
    for n in CLIP_SHEETS:
        p = os.path.join(CLIPS, n + ".png")
        if os.path.exists(p):
            shutil.copyfile(p, os.path.join(out, "refs", "league_" + n.lower() + ".png"))
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{len(cols)} colours; {len(manifest['frames'])} frames -> {zp}")


if __name__ == "__main__":
    main()
