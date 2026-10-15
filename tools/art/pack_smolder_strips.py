#!/usr/bin/env python3
"""Smolder's step-2 pack for Codex (assets/source/smolder/MODEL_STRIPS.md): every action frame as a FINE draft, 3/4
front, posed after League's animation.

    python tools/art/pack_smolder_strips.py [--out dist/smolder_packs/smolder_strips_pack]

All actions from the 3/4 front (the user, 2026-10-14: 「只画正面，不要侧面」 - Bard's way). Codex draws clean pixel
art at its own fine square size and never hit a coarse grid in steps 0-1, so it draws fine drafts like its step-1
take 3 (assets/source/smolder/codex_model/raw/smolder-front-attempt-03.png, the design's source) and
tools/art/design_smolder.py's way (area votes, the face kept) brings them to the design (PPU 1.5,
assets/source/smolder/hd/front.png, horn tips -> soles 41 squares). Every frame sits on one 1536 x 1024 canvas at one
scale: a design square is PX canvas px, the soles on SOLE_Y, the middle of the standing feet on PIV_X.
The skeletons: tools/lol/native_pose.py on assets/source/smolder/poses.json (--alpha) -> %TEMP%/sm_work/pose_n:
League's clips through one camera (yaw 30, NOT mirrored: Smolder's model faces image right as it is), 8 render px a
game px; the design pose (run_collar@167, standing on four legs) is 28 game px from the crown to the soles, the soles
11 game px under a cell's pivot. Each frame's cell is scaled so 28 game px = the design's 41 rows and placed with its
pivot on the standing point: the pose, the place and the size.
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (the fine front draft, the same on the canvas at the pack's
size, the game design at 8x), now/ (skeletons), guide/ (the same with the lines and the design's outline), refs/
(League's clips as contact sheets - Riot's model: local only), cells.json (every frame: tag, index, ms).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "smolder")
DESIGN = os.path.join(SRC, "hd", "front.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "smolder-front-attempt-03.png")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "sm_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips30")
PX = 12                      # canvas px a design square (the fine draft: ~1.8 of its own squares to one of these)
SOLE_Y = 990                 # the soles' bottom edge on the canvas (room above for the flight and the wings)
PIV_X = 760                  # the middle of the standing feet
RS = 8                       # render px a game px in native_pose's renders
DESIGN_ROWS = 41             # the design: horn tips -> soles, squares
DESIGN_GP = 28               # the design pose's height in game px (native_pose's print)
SOLE_BELOW_PIVOT = 13        # the skeletons' soles 13 game px under a cell's pivot (pivot row 87, feet line row 100)
DRAFT_HORN, DRAFT_SOLE = 88, 1012   # the fine front draft: horn tips, soles (raw px) -> 41 design squares


def design():
    d = np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def feet_mid(a, rows=6):
    """The middle of the feet: the bottom rows' opaque columns, first to last."""
    op = a[..., 3] > 128
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys[-1] - rows + 1:ys[-1] + 1].any(0))[0]
    return (xs.min() + xs.max()) / 2.0


def draft_on_canvas():
    """Codex's own fine front draft scaled to the pack's size, its soles on SOLE_Y and its feet's middle on PIV_X."""
    im = Image.open(DRAFT).convert("RGBA")
    a = np.asarray(im).copy()
    a[a[..., 3] < 128] = 0                       # Codex's haze
    a[a[..., 3] >= 128, 3] = 255
    im = Image.fromarray(a)
    mid = feet_mid(a, 40)
    k = PX * DESIGN_ROWS / (DRAFT_SOLE - DRAFT_HORN)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    can = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    can.alpha_composite(im, (round(PIV_X - mid * k), round(SOLE_Y - DRAFT_SOLE * k)))
    return can


def outline_of(can):
    """The design's silhouette edge on the canvas (where the standing figure ends)."""
    op = np.asarray(can)[..., 3] > 128
    lab, n = ndimage.label(op)
    if n > 1:                                    # the figure only (the resize leaves specks of alpha round it)
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        op = lab == (1 + int(np.argmax(sizes)))
    op = ndimage.binary_fill_holes(op)
    return op & ~ndimage.binary_erosion(op, iterations=2)


def skeleton(tag, i):
    """Frame i of a tag's pose render, scaled to the pack (1536 x 1024 RGBA), and the scale."""
    im = Image.open(os.path.join(POSE, f"smolder_pose_{tag}.png")).convert("RGBA")
    cw = 128 * RS
    cols = im.width // cw
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    k = PX * DESIGN_ROWS / DESIGN_GP / RS
    return c.resize((round(c.width * k), round(c.height * k)), Image.LANCZOS), k


def lines(img, edge=None):
    """Guide lines: every 50 px light grey, the soles (red), the standing point (blue cross), the standing design's
    outline (magenta) when given."""
    dr = ImageDraw.Draw(img)
    for x in range(0, 1537, 50):
        dr.line([(x, 0), (x, 1024)], fill=(200, 200, 200, 80))
    for y in range(0, 1025, 50):
        dr.line([(0, y), (1536, y)], fill=(200, 200, 200, 80))
    if edge is not None:
        ov = np.zeros((1024, 1536, 4), np.uint8)
        ov[edge] = (255, 0, 200, 150)
        img.alpha_composite(Image.fromarray(ov))
    dr.line([(0, SOLE_Y), (1536, SOLE_Y)], fill=(255, 40, 40, 255), width=2)
    dr.line([(PIV_X - 18, SOLE_Y), (PIV_X + 18, SOLE_Y)], fill=(40, 90, 255, 255), width=3)
    dr.line([(PIV_X, SOLE_Y - 18), (PIV_X, SOLE_Y + 18)], fill=(40, 90, 255, 255), width=3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "smolder_packs", "smolder_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    d = design()
    shutil.copyfile(DRAFT, os.path.join(out, "design", "smolder_front_draft.png"))
    dc = draft_on_canvas()
    dc.save(os.path.join(out, "design", "smolder_front_on_canvas.png"))
    lines(dc.copy()).save(os.path.join(out, "design", "smolder_front_on_canvas_guide.png"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "smolder_in_game_8x.png"))
    edge = outline_of(dc)
    for n, tag in (("run_collar", "run"), ("attack_H_1", "attack"), ("Spell1_F_to_Idle", "skill_q"),
                   ("Spell2_A", "skill2_w"), ("Spell3_0", "skill2_e_takeoff"), ("Spell3_Idle", "skill2_e_flying"),
                   ("Spell4_A", "ult"), ("Death2", "dead")):
        p = os.path.join(CLIPS, n + ".png")
        if os.path.isfile(p):
            shutil.copyfile(p, os.path.join(out, "refs", f"league_{tag}.png"))
    cells = json.load(open(os.path.join(POSE, "smolder_cells.json"), encoding="utf-8"))
    manifest = {"canvas": [1536, 1024], "px_per_design_square": PX, "soles_y": SOLE_Y, "standing_x": PIV_X,
                "design_squares": [int(d.shape[1]), int(d.shape[0])], "frames": []}
    for tag, frames in cells["tags"].items():
        for i, f in enumerate(frames):
            sk, k = skeleton(tag, i)
            can = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
            px, py = f["pivot"]
            ox = round(PIV_X - (px + 0.5) * RS * k)
            oy = round(SOLE_Y - (py + SOLE_BELOW_PIVOT) * RS * k)
            can.paste(sk, (ox, oy), sk)
            name = f"smolder_{tag}_{i + 1}.png"
            can.save(os.path.join(out, "now", name))
            lines(can.copy(), edge).save(os.path.join(out, "guide", name))
            manifest["frames"].append({"file": name, "tag": tag, "index": i, "ms": f["ms"]})
    with open(os.path.join(out, "cells.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    shutil.copyfile(DOC, os.path.join(out, "MODEL_STRIPS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"design {d.shape[1]}x{d.shape[0]} squares, {len(manifest['frames'])} frames -> {zp}")


if __name__ == "__main__":
    main()
