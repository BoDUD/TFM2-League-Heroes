#!/usr/bin/env python3
"""Steb's run (assets/source/steb/RUN_PROMPTS.md, Codex's codex_run/steb-run, 2026-10-29) as game pictures: ONE upper body
for all eight frames on each frame's own legs (design_sevika_run.py's way, the run the user accepted for Sevika).

    python tools/art/design_steb_run.py --sheet DIR     # the eight frames, 6x, the legs' parts tinted
    python tools/art/design_steb_run.py                 # writes assets/source/steb/hd/pose_run<k>.png (+ .json)

Codex drew the whole 1.30 s cycle as asked (pack_steb_run.py): the far leg (his left, darker: trousers #2E2A4A, boots
#17282F) ahead in run1-3 and run8, the near leg in run5-6, the legs passing / crossing in run4 and run7, on exact 9 px
squares from the canvas corner. But above the hips every frame is its own drawing (Codex's validation says so): the
torso's size and lean change and the batons jump about from frame to frame - what Smeech's and Sevika's walks taught
(memory codex-walk-drafts-differ): keep one upper body. So:
  * the upper body is run3's (UPPER: its hands and batons are clear of its legs): everything of run3 but its legs, with
    the design's head laid over once (design_steb_poses' match);
  * each frame keeps its own legs: below its trouser line (the first row under the coat with TROUSER_MIN trouser
    squares) the leg colours joined to the soles; where that frame's own hand or baton hangs over a thigh (HAND boxes)
    only the trouser squares there are kept;
  * the legs go under the upper body's hips (the middle of the top LEG_TOP rows of the legs), the soles on the ground;
    the upper body sits on the legs' top at the frame's trouser line, lowered to HIP_FLOOR (a leg is never stretched):
    the legs' tops stay under the coat (cut flat they left holes the user saw: 「我怎么看到像素缺失？」), and a hole
    left between the hem and the thighs takes the trousers' dark shade (fill_hips).
Then specks dropped, holes and one-square cracks closed (design_silco_poses.close_gaps), the outline completed
(strips.complete_outline). The rig (tools/art/rig_steb.py) plays them pack_steb_run.MS apart.
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
import design_steb_poses as DP  # noqa: E402
from design_steb_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "steb", "codex_run", "steb-run")
OUT = os.path.join(ROOT, "assets", "source", "steb", "hd")
FRAMES = list(range(1, 9))
UPPER = 3
SQ = 9
TROUSER = ("#564A68", "#2E2A4A")
LEG = TROUSER + ("#17282F", "#364A42", "#BE7722", "#F2AE37", "#F7C545", "#DA952D", "#A46222", "#FAE059", "#FBEC73",
                 "#C3A74A", "#0F0414", "#6F3523", "#904729", "#4F231C", "#3B2B2A")   # trousers, boots, gold rings, straps
TROUSER_MIN = 6
LEG_TOP = 4
# a frame's own hand / baton end hanging beside a thigh (x0, y0, x1, y1 inclusive, on its 1254 / 9 squares): only its
# trouser squares stay with the legs (read on 7x grids, 2026-10-29)
HAND = {4: [(50, 80, 70, 91)], 5: [(48, 80, 66, 96)], 6: [(52, 86, 64, 96)], 7: [(48, 82, 63, 93)],
        8: [(54, 80, 72, 92)]}
# the upper body's bottom row on the canvas per frame: each frame's own trouser line (81-88), raised frames lowered to
# 85 so the bob is 85-88 (3 rows; run2's long stride sits lowest)
HIP_FLOOR = 85
TOP_KEEP = 8                     # leg rows kept above the hips' line (the coat covers them; cut flat they left holes)
HIPS_ZONE = (-10, 20)            # rows round the hips' line where a clear hole the figure closes is filled
HIPS_FILL = "#2E2A4A"            # with the trousers' dark shade: the shadow under the coat (Irelia's rule)


def fill_hips(can, hip):
    """Clear holes the figure closes between the coat's hem and the thighs (any size: another frame's legs under this
    upper body leave them) take the trousers' dark shade; holes elsewhere are left to close_gaps."""
    op = can[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    out = can.copy()
    for j in range(1, n + 1):
        ys, _ = np.nonzero(lab == j)
        if hip + HIPS_ZONE[0] <= ys.min() and ys.max() <= hip + HIPS_ZONE[1]:
            out[lab == j] = DP.rgb(HIPS_FILL) + (255,)
    return out


def rgbs(hexes):
    return {DP.rgb(h) for h in hexes}


def colour_mask(a, hexes):
    s = rgbs(hexes)
    return np.array([[p[3] > 0 and tuple(p[:3]) in s for p in r] for r in a])


def read(k, pal):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"steb-run-run{k}.png"))).convert("RGBA"))
    return DP.snap(a[SQ // 2::SQ, SQ // 2::SQ].copy(), pal)


def legs_of(one, k):
    """(the legs' mask, the trouser line): the leg colours under the coat joined to the soles, minus the frame's own
    hands and baton ends over the thighs (their trouser squares kept)."""
    tr = colour_mask(one, TROUSER)
    rows = np.nonzero(tr[70:].sum(1) >= TROUSER_MIN)[0] + 70
    cut = int(rows.min())
    leg = colour_mask(one, LEG)
    leg[:cut] = False
    for x0, y0, x1, y1 in HAND.get(k, ()):
        box = np.zeros_like(leg)
        box[y0:y1 + 1, x0:x1 + 1] = True
        leg &= ~box | tr
    lab, _ = ndimage.label(leg, structure=np.ones((3, 3)))
    low = int(np.nonzero(one[..., 3] > 0)[0].max()) - 5   # the soles' rows
    keep = set(lab[low:][lab[low:] > 0].ravel())
    return np.isin(lab, list(keep)), cut


def hips(mask):
    """The middle column of the legs' top LEG_TOP rows."""
    ys, xs = np.nonzero(mask)
    top = ys.min()
    return float(xs[ys < top + LEG_TOP].mean()), int(top)


def build():
    d = DP.design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    h, m = DP.head(d)
    frames = {k: read(k, pal) for k in FRAMES}
    legs = {k: legs_of(frames[k], k) for k in FRAMES}
    # the upper body: run3 without its legs, the design's head on it
    up = frames[UPPER].copy()
    up_legs, up_cut = legs[UPPER]
    up[up_legs] = 0
    score, hx, hy = DP.match(up, h, m)
    up, (hx, hy) = DP.lay_head(up, h, m, hx, hy)
    pad_y = up.shape[0] - frames[UPPER].shape[0]   # lay_head grows the picture only off its top / left
    pad_x = up.shape[1] - frames[UPPER].shape[1]
    up_hip_x, _ = hips(up_legs)
    up_hip_x += pad_x
    out = {}
    for k in FRAMES:
        f = frames[k]
        mask, cut = legs[k]
        hip_x, top = hips(mask)
        hip_y = max(cut, HIP_FLOOR)
        can = np.zeros((f.shape[0] + 40, f.shape[1] + 40, 4), np.uint8)
        ox = 20 + round(up_hip_x - pad_x - hip_x)   # the legs under the upper body's hips
        legs_px = np.zeros_like(f)
        legs_px[mask] = f[mask]
        legs_px[:hip_y - TOP_KEEP] = 0               # only what would rise far over the coat's hem is dropped
        ys, xs = np.nonzero(legs_px[..., 3] > 0)
        can[ys + 20, xs + ox] = legs_px[ys, xs]
        # the upper body: its trouser line on this frame's hips
        uy = 20 + hip_y - (up_cut + pad_y)
        ys, xs = np.nonzero(up[..., 3] > 0)
        can[ys + uy, xs + 20 - pad_x] = up[ys, xs]
        can = fill_hips(can, 20 + hip_y)
        can = DP.drop_specks(can)
        can = DP.fill_thin(close_gaps(can, d), d)
        can, _, _ = G.complete_outline(can)
        ys, xs = np.nonzero(can[..., 3] > 0)
        oy, ox_ = int(ys.min()), int(xs.min())
        fig = can[oy:ys.max() + 1, ox_:xs.max() + 1]
        out[k] = (fig, {"head_at": [int(hx + 20 - ox_), int(hy + uy - oy)], "grid_at": [ox_ - 20, oy - 20],
                        "hip_y": hip_y, "legs_cut": cut, "head_match": round(float(score), 2)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    out = build()
    for k, (fig, info) in out.items():
        print(f"run{k} {fig.shape[1]} x {fig.shape[0]} {info}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 6
        H = max(f.shape[0] for f, _ in out.values())
        W = sum(f.shape[1] * z + 12 for f, _ in out.values())
        sheet = Image.new("RGBA", (W, H * z + 24), (90, 96, 90, 255))
        dr = ImageDraw.Draw(sheet)
        x = 0
        for k, (fig, info) in out.items():
            sheet.alpha_composite(DP.big(fig, z), (x, 24 + (H - fig.shape[0]) * z))
            dr.text((x + 4, 4), f"run{k} hip {info['hip_y']}", fill=(255, 255, 0, 255))
            x += fig.shape[1] * z + 12
        sheet.convert("RGB").save(lp(os.path.join(a.sheet, "steb_run.png")))
        return
    for k, (fig, info) in out.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_run{k}.png")))
        with open(lp(os.path.join(OUT, f"pose_run{k}.json")), "w", encoding="utf-8") as fh:
            json.dump(info, fh)


if __name__ == "__main__":
    main()
