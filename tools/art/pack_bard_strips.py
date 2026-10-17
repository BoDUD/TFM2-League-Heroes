#!/usr/bin/env python3
"""Bard's step-2 pack for Codex (assets/source/bard/MODEL_STRIPS.md): every action frame as a FINE draft, 3/4 front,
posed after League's animation.

    python tools/art/pack_bard_strips.py [--out dist/bard_packs/bard_strips_pack]

All actions from the 3/4 front (the user, 2026-10-13: 「其实不用侧面啊 四分之三就行了吧」 - Braum's and Galio's way).
The lesson of steps 0-1: Codex draws clean pixel art at its own fine square size (~5-8 px) and muddies it when it cuts
it to a coarse grid itself, so it draws only fine drafts and tools/art/design_bard_hd.py's cut brings them to the
design (PPU 1.5, assets/source/bard/hd/front.png, 54 x 58 squares). Every frame sits on one 1536 x 1024 canvas at one
scale: a design square is PX canvas px (the design 58 squares = 638 px tall), the soles on SOLE_Y, the point between
the feet on PIV_X.
The skeletons: tools/lol/native_pose.py on assets/source/bard/poses.json (--alpha) -> %TEMP%/ba_work/pose_n: League's
clips through one camera (yaw 30, mirrored: he faces right), 8 render px a game px; the design pose is 36 game px tall
(native_pose's print), the soles 11 game px under a cell's pivot. Each frame's cell is scaled to the design's size and
placed with its pivot on the standing point: the pose, the place and the size.
Writes <out>/ (and <out>.zip): MODEL_STRIPS.md, design/ (Codex's own fine front draft, the same on the canvas at the
pack's size, the game design at 8x), now/ (skeletons), guide/ (the same with the lines and the design's outline),
refs/ (League's clips as contact sheets - Riot's model: local only), cells.json (every frame: tag, index, ms).
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
SRC = os.path.join(ROOT, "assets", "source", "bard")
DESIGN = os.path.join(SRC, "hd", "front.png")
DRAFT = os.path.join(SRC, "codex_model", "raw", "front-01.png")
DOC = os.path.join(SRC, "MODEL_STRIPS.md")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ba_work")
POSE = os.path.join(TMP, "pose_n")
CLIPS = os.path.join(TMP, "clips30")
PX = 11                      # canvas px a design square (the fine draft: ~2.5 of its own squares to one of these)
SOLE_Y = 980                 # the soles' bottom edge on the canvas (room above for the raised instrument)
PIV_X = 640                  # the point between the feet
RS = 8                       # render px a game px in native_pose's renders
DESIGN_GP = 36               # the design pose's height in game px (native_pose's print)
SOLE_BELOW_PIVOT = 11        # native_pose: the soles 11 game px under a cell's pivot (pivot row 88, soles row 99)
DRAFT_SOLE, DRAFT_MID, DRAFT_PX = 1391, 605, 20.74   # the fine front draft: soles, feet middle, px a design square


def design():
    d = np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ys, xs = np.nonzero(d[..., 3])
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def feet_mid(d):
    """The middle between the two peg feet: the bottom 6 rows' opaque columns, split at the widest gap."""
    op = d[..., 3] > 0
    xs = np.nonzero(op[-6:].any(0))[0]
    return (xs.min() + xs.max()) / 2.0


def draft_on_canvas():
    """Codex's own fine front draft scaled to the pack's size, its soles on SOLE_Y and its feet's middle on PIV_X."""
    im = Image.open(DRAFT).convert("RGBA")
    k = PX / DRAFT_PX
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    can = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    can.alpha_composite(im, (round(PIV_X - DRAFT_MID * k), round(SOLE_Y - DRAFT_SOLE * k)))
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
    im = Image.open(os.path.join(POSE, f"bard_pose_{tag}.png")).convert("RGBA")
    cw = 128 * RS
    cols = im.width // cw
    cx, cy = i % cols, i // cols
    c = im.crop((cx * cw, cy * cw, (cx + 1) * cw, (cy + 1) * cw))
    k = PX * design().shape[0] / DESIGN_GP / RS
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
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "bard_packs", "bard_strips_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    d = design()
    shutil.copyfile(DRAFT, os.path.join(out, "design", "bard_front_draft.png"))
    dc = draft_on_canvas()
    dc.save(os.path.join(out, "design", "bard_front_on_canvas.png"))
    lines(dc.copy()).save(os.path.join(out, "design", "bard_front_on_canvas_guide.png"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "bard_in_game_8x.png"))
    edge = outline_of(dc)
    for n in ("Bard_Run01", "Bard_Attack01", "Bard_Spell1", "Bard_Spell3", "Bard_Spell2", "Bard_Spell4", "Bard_Death"):
        p = os.path.join(CLIPS, n + ".png")
        if os.path.isfile(p):
            shutil.copyfile(p, os.path.join(out, "refs", f"league_{n[5:].lower()}.png"))
    cells = json.load(open(os.path.join(POSE, "bard_cells.json"), encoding="utf-8"))
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
            name = f"bard_{tag}_{i + 1}.png"
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
