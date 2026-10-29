#!/usr/bin/env python3
"""Sevika's run, the second Codex round (assets/source/sevika/RUN_PROMPTS.md, delivered as sevika_run_review_v2.zip,
2026-10-29) as game pictures: ONE upper body for all eight frames on each frame's own legs, the far leg a step darker.

    python tools/art/design_sevika_run.py --sheet DIR     # the eight frames, the near / far split tinted, 6x
    python tools/art/design_sevika_run.py                 # writes assets/source/sevika/hd/pose_run<k>.png (+ .json)

The user on the first run: 「走路感觉换腿不明显啊」 (only half her TFT cycle; both legs one tone). Codex redrew the whole
cycle (pack_sevika_run.py): its legs take turns as asked - the far leg ahead in run1-3 and run8, the near one in run5-6,
the legs passing in run4 and crossing in run7 - on exact 12 px squares (pixel_1x, alpha 0/255), the boots one size (13-15
squares) in every frame. But each frame is its own drawing above the hips: the torso's size and lean, the mechanical
arm and the slot machine change from frame to frame (Codex's own validation says so) - what Smeech's walk taught
(memory codex-walk-drafts-differ): keep one upper body. So:
  * the upper body is run5's (UPPER): everything above its trouser line (CUT), its mechanical arm (ARM: right of the
    column, down to the row) and its flesh hand, with the design's head laid over once (design_sevika_poses: the head
    matched there at scale 1.0);
  * each frame keeps its own legs: below its CUT, minus its own mechanical arm (ARM) and flesh hand (HAND), placed so
    its hips (the middle of its trouser line) sit under the upper body's - the planted leg on the ground gives the bob;
  * the legs split near / far: below the crotch each leg is its own run of squares in a row (the gap between them); where
    they touch, at the hips and in the passing frames, along SPLIT (a line of (row, column) points); the far side is
    FAR_SIDE. The far leg takes DARKER (the design's own darker colour of each of its leg colours; the boot unchanged),
    the near leg is left as Codex drew it.
Then specks dropped, holes and one-square cracks closed (design_silco_poses.close_gaps), the outline completed
(strips.complete_outline). The rig (tools/art/rig_sevika.py) plays them RUN_MS apart (pack_sevika_run.MS).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_sevika_poses as DP  # noqa: E402
from design_sevika_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sevika", "codex_run", "sevika-run-review-v2", "pixel_1x")
OUT = os.path.join(ROOT, "assets", "source", "sevika", "hd")
FRAMES = list(range(1, 9))
UPPER = 5
# per frame (pixel_1x squares, 2026-10-29, read on 9x grids): the first trouser row under the belt and the pouch
CUT = {1: 56, 2: 57, 3: 63, 4: 60, 5: 59, 6: 62, 7: 60, 8: 62}
# the mechanical arm: right of this column and above this row (its claws end there; the front boot below is a leg)
ARM = {1: (67, 82), 2: (70, 82), 3: (62, 87), 4: (64, 85), 5: (63, 83), 6: (65, 85), 7: (62, 82), 8: (66, 78)}
# the flesh hand where it hangs beside the legs (x0, y0, x1, y1, inclusive), dropped from the legs
HAND = {1: (20, 46, 37, 61), 2: (33, 55, 46, 69), 3: (25, 59, 38, 70), 4: (30, 56, 44, 67), 5: (25, 47, 38, 60),
        6: (29, 55, 41, 65), 7: (22, 52, 35, 64), 8: (28, 54, 41, 69)}
# which leg is the far one (her left, a step darker): the front one where the far leg leads, the back one where the
# near one does, and in the passing / crossing frames the one Codex drew behind
FAR_SIDE = {1: "right", 2: "right", 3: "right", 4: "left", 5: "left", 6: "left", 7: "left", 8: "right"}
# where the legs touch: (row, column) points of the line between them (interpolated by row; below the last point the
# last column; rows with a gap between two runs split there instead)
SPLIT = {1: [(56, 53), (64, 52)], 2: [(57, 54), (66, 53)], 3: [(63, 52), (70, 49)], 4: [(60, 51), (80, 52), (98, 53)],
         5: [(59, 52), (68, 51)], 6: [(62, 51), (70, 51)], 7: [(60, 51), (80, 50), (98, 51)], 8: [(62, 53), (70, 52)]}
# the hips' height over the soles (squares): Codex's leg lengths alone gave 40 39 34 38 38 36 36 33 - a 7-row bob with a
# 7-row hop from run8 back to run1 (its wide split sits low); her TFT run bobs 5 (38.9 34.8 38.7 39.8 39.5 37.3 37.9
# 38.9 at the pack's scale). Lowered over the thighs' tops where the legs came out long (the belt covers them; a leg is
# never stretched): a 3-row bob, 3 at the seam
HIP_H = {1: 36, 2: 35, 3: 34, 4: 36, 5: 36, 6: 35, 7: 35, 8: 33}
# colours the palette snap took from the arm and the face for Codex's leg shades -> the leg's own
FOREIGN = {"#AA3B36": "#CE6F51", "#35062A": "#3D2629", "#343D42": "#292C48", "#877832": "#7E5530", "#6C6B69": "#454E77",
           "#174F5C": "#292C48"}
LEG_SPECK = 40                   # parts of a frame's legs smaller than this (its own hand's leftovers: run2's finger
#                                  was 12-39 squares) are dropped; a leg is hundreds
# the far leg's colours: each of the design's leg colours to its own darker one (the boot, its toe cap and the outline
# unchanged)
DARKER = {"#604345": "#3D2629", "#7E5530": "#473124", "#637FAE": "#454E77", "#454E77": "#292C48", "#FBAA81": "#CE6F51",
          "#473124": "#3D2629"}


def frame(k, pal):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"sevika-run-run{k}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return DP.snap(a, pal)


def in_box(shape, box):
    m = np.zeros(shape, bool)
    x0, y0, x1, y1 = box
    m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    return m


def arm_mask(shape, k):
    x0, y1 = ARM[k]
    m = np.zeros(shape, bool)
    m[:y1 + 1, x0:] = True
    return m


def legs(a, k):
    """Frame k's legs: below its CUT, without its own mechanical arm and flesh hand (and what is left of them), its
    shades in the legs' own colours."""
    keep = np.zeros(a.shape[:2], bool)
    keep[CUT[k]:] = True
    keep &= ~arm_mask(a.shape[:2], k) & ~in_box(a.shape[:2], HAND[k])
    out = a.copy()
    out[~keep] = 0
    op = out[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        if (lb == j).sum() < LEG_SPECK:
            out[lb == j] = 0
    for src, dst in FOREIGN.items():
        sel = (out[..., :3] == np.array(DP.rgb(src))).all(-1) & (out[..., 3] > 0)
        out[sel, :3] = DP.rgb(dst)
    return out


def upper(a, k):
    """Frame k's upper body: above its CUT, its mechanical arm and its flesh hand."""
    keep = np.zeros(a.shape[:2], bool)
    keep[:CUT[k]] = True
    keep |= arm_mask(a.shape[:2], k) | in_box(a.shape[:2], HAND[k])
    out = a.copy()
    out[~keep] = 0
    return out


def hips(lg, k):
    """The middle of the trouser line: the opaque run of CUT's row (and the next) nearest the split."""
    sx = SPLIT[k][0][1]
    for y in (CUT[k], CUT[k] + 1, CUT[k] + 2):
        xs = np.nonzero(lg[y, :, 3] > 0)[0]
        if len(xs):
            return (float(xs.min() + xs.max()) / 2, y)
    return (float(sx), CUT[k])


def split_col(k, y, row):
    """The column between the two legs in row y: the widest gap between opaque runs near the split line, else the
    line."""
    pts = SPLIT[k]
    if y <= pts[0][0]:
        line = pts[0][1]
    elif y >= pts[-1][0]:
        line = pts[-1][1]
    else:
        for (y0, x0), (y1, x1) in zip(pts, pts[1:]):
            if y0 <= y <= y1:
                line = x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0)
                break
    xs = np.nonzero(row)[0]
    if len(xs) < 2:
        return line
    gaps = [(b - a, (a + b) / 2) for a, b in zip(xs, xs[1:]) if b - a > 1]
    near = [g for g in gaps if abs(g[1] - line) <= 12]
    if near and k not in (4, 7):      # the passing frames: their legs overlap, the line decides
        return max(near)[1]
    return line


def far_mask(lg, k):
    """The far leg's squares in a legs picture."""
    m = np.zeros(lg.shape[:2], bool)
    op = lg[..., 3] > 0
    for y in range(CUT[k], lg.shape[0]):
        if not op[y].any():
            continue
        c = split_col(k, y, op[y])
        xs = np.arange(lg.shape[1])
        m[y] = op[y] & ((xs > c) if FAR_SIDE[k] == "right" else (xs < c))
    return m


def darken(lg, m):
    out = lg.copy()
    for src, dst in DARKER.items():
        s, t = np.array(DP.rgb(src)), np.array(DP.rgb(dst))
        sel = m & (out[..., :3] == s).all(-1) & (out[..., 3] > 0)
        out[sel, :3] = t
    return out


def build(pal, d):
    h, hm = DP.head(d)
    a5 = frame(UPPER, pal)
    up = upper(a5, UPPER)
    score, mx, my = DP.match(up, h, hm)
    up, (hx, hy) = DP.lay_head(up, h, hm, mx, my)
    # lay_head grows the picture at the left / top when the head runs off: (gx, gy) squares, so the upper body's
    # squares in run5's own coordinates are the grown ones less (gx, gy)
    gx, gy = hx - mx, hy - my
    lg5 = legs(a5, UPPER)
    hip5 = hips(lg5, UPPER)
    print(f"upper body run{UPPER}: head match {score:.2f} at ({mx}, {my}), hips {hip5}, grown {gx, gy}")
    out = {}
    for k in FRAMES:
        a = frame(k, pal)
        lg = legs(a, k)
        fm = far_mask(lg, k)
        lg = darken(lg, fm)
        hip = hips(lg, k)
        sole = int(np.nonzero((lg[..., 3] > 0).any(1))[0].max())
        natural = sole - CUT[k]
        if HIP_H[k] > natural:
            sys.exit(f"run{k}: HIP_H {HIP_H[k]} over its legs' own {natural} (a gap at the waist)")
        dx, dy = round(hip[0] - hip5[0]), (sole - HIP_H[k]) - CUT[UPPER]
        W, H = a.shape[1] + 40, a.shape[0] + 40
        can = np.zeros((H, W, 4), np.uint8)
        ox, oy = 20, 20
        ys, xs = np.nonzero(lg[..., 3] > 0)
        can[ys + oy, xs + ox] = lg[ys, xs]
        uy, ux = np.nonzero(up[..., 3] > 0)
        ty, tx = uy - gy + dy + oy, ux - gx + dx + ox
        can[ty, tx] = up[uy, ux]
        fig = close_gaps(DP.drop_specks(can), d)
        fig, _, _ = G.complete_outline(fig)
        ys, xs = np.nonzero(fig[..., 3] > 0)
        y0, x0 = int(ys.min()), int(xs.min())
        fig = fig[y0:ys.max() + 1, x0:xs.max() + 1]
        head_at = (int(mx + dx + ox - x0), int(my + dy + oy - y0))
        grid_at = (int(x0 - ox), int(y0 - oy))
        out[k] = (fig, head_at, grid_at, fm, lg)
        print(f"run{k}: hips {hip}, own height {natural} -> {HIP_H[k]}: upper body moved ({dx}, {dy}); "
              f"{fig.shape[1]} x {fig.shape[0]}, far leg {int(fm.sum())} squares")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    d = DP.design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    res = build(pal, d)
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 6
        tiles = []
        for k in FRAMES:
            fig, _, _, fm, lg = res[k]
            t = Image.fromarray(np.repeat(np.repeat(fig, z, 0), z, 1))
            bg = Image.new("RGBA", t.size, (70, 76, 70, 255))
            bg.alpha_composite(t)
            tint = np.zeros(lg.shape[:2] + (4,), np.uint8)
            tint[fm] = (255, 60, 60, 110)
            near = (lg[..., 3] > 0) & ~fm
            tint[near] = (60, 120, 255, 70)
            tt = Image.fromarray(np.repeat(np.repeat(tint, z, 0), z, 1))
            tiles.append((bg, tt))
        Hm = max(b.height for b, _ in tiles)
        sheet = Image.new("RGBA", (sum(b.width + 12 for b, _ in tiles), Hm + 24), (40, 44, 40, 255))
        x = 0
        for k, (b, _) in zip(FRAMES, tiles):
            sheet.alpha_composite(b, (x, 24 + Hm - b.height))
            ImageDraw.Draw(sheet).text((x + 4, 4), f"run{k}", fill=(255, 255, 0, 255))
            x += b.width + 12
        sheet.convert("RGB").save(lp(os.path.join(a.sheet, "sevika_run_v2.png")))
        # the split, tinted on each frame's own legs
        lsheet = Image.new("RGBA", (sum(t.width + 12 for _, t in tiles), max(t.height for _, t in tiles) + 24),
                           (40, 44, 40, 255))
        x = 0
        for k, (_, t) in zip(FRAMES, tiles):
            lg = res[k][4]
            base = Image.fromarray(np.repeat(np.repeat(lg, z, 0), z, 1))
            cell = Image.new("RGBA", base.size, (70, 76, 70, 255))
            cell.alpha_composite(base)
            cell.alpha_composite(t)
            lsheet.alpha_composite(cell, (x, 24))
            ImageDraw.Draw(lsheet).text((x + 4, 4), f"run{k} far={FAR_SIDE[k]}", fill=(255, 255, 0, 255))
            x += t.width + 12
        lsheet.convert("RGB").save(lp(os.path.join(a.sheet, "sevika_run_v2_split.png")))
        print(a.sheet)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for k, (fig, head_at, grid_at, _fm, _lg) in res.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_run{k}.png")))
        with open(lp(os.path.join(OUT, f"pose_run{k}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [head_at[0], head_at[1]], "grid_at": [grid_at[0], grid_at[1]]}, fh)
    print("written", OUT)


if __name__ == "__main__":
    main()
