#!/usr/bin/env python3
"""Volibear's arm poses from Codex (assets/source/volibear/codex_poses, POSE_PROMPTS.md part A) read back onto the
design's grid -> assets/source/volibear/hd/pose_<name>.png (+ _8x) and pose_<name>.json (where the design's (0, 0) is).

    python tools/art/design_volibear_poses.py

Codex drew the same bear with only the arms in a new pose on the pack's 15 px grid (soles y 1140), but the canvas
drifted (the soles 1133-1156) and the upper body was drawn again (its HANDOFF: no square identical to the design). The
legs keep the design's own size (the stance 34 squares at 14.7-15.0 px in every take), so each take is sampled at 15 px
from its own stance: the design's column 9 at the stance's left edge, the soles' row at its lowest opaque row. Each
square is the median of its middle 7 x 7, snapped to the design's palette. Then the design's own squares go back where
they must not change (memory one-face-all-frames): the head (rows <= HEAD_ROW inside HEAD_COLS) and the lower legs
(rig_volibear's near_leg / far_leg); Codex's squares there are cleared first (one square round them too, so no second
rim stays). What is left of Codex's drawing is the torso and the arms in the new pose.
Takes (the user's step-1 grid, PPU 1.2): up2 = both arms raised (TAKES), up1 = the near arm raised, rake = the near arm
swung forward and down across the belly, maul = both arms thrust forward.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_volibear as V  # noqa: E402

lp = V.lp
SRC = os.path.join(ROOT, "assets", "source", "volibear", "codex_poses", "volibear-pose", "raw")
OUT = os.path.join(ROOT, "assets", "source", "volibear", "hd")
TAKES = {"up2": "volibear-pose-up2-2", "up1": "volibear-pose-up1-2", "rake": "volibear-pose-rake-2",
         "maul": "volibear-pose-maul-2"}
PX = 15.0
STANCE_COL = 9            # the design's left stance edge (the near foot's outline)
HEAD_ROW = 12             # the head: design rows 0-12 ...
HEAD_COLS = (13, 38)      # ... inside these columns (the shoulder fur beside it is Codex's)


def sample(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, name + ".png"))).convert("RGBA"))
    o = a[..., 3] >= 128
    yy = np.nonzero(o.any(1))[0]
    b = yy.max()
    x = np.nonzero(o[b - 60:b + 1].any(0))[0]
    gx, gy = x.min() - STANCE_COL * PX, b + 1 - 54 * PX
    ys, xs = np.nonzero(o)
    c0, c1 = int(np.floor((xs.min() - gx) / PX)), int(np.ceil((xs.max() - gx) / PX))
    c0, c1 = min(c0, -1), max(c1, 51)              # room for the whole design box
    r0 = min(int(np.floor((ys.min() - gy) / PX)), -1)
    out = np.zeros((54 - r0, c1 - c0 + 1, 4), np.uint8)
    for r in range(r0, 54):
        for c in range(c0, c1 + 1):
            cy, cx = int(gy + (r + 0.5) * PX), int(gx + (c + 0.5) * PX)
            win = a[max(0, cy - 3):cy + 4, max(0, cx - 3):cx + 4].reshape(-1, 4)
            if (win[:, 3] >= 128).sum() * 2 > len(win):
                out[r - r0, c - c0, :3] = np.median(win[win[:, 3] >= 128][:, :3], 0)
                out[r - r0, c - c0, 3] = 255
    return out, (-c0, -r0)


def snap(a, pal):
    out = a.copy()
    m = out[..., 3] > 0
    px = out[m][:, :3].astype(int)
    d = ((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    out[m, :3] = pal[d.argmin(1)]
    return out


def main():
    D = V.front()
    d = D.d
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    head = (D.parts["body"] | D.parts["near_arm"] | D.parts["far_arm"]) & (yy <= HEAD_ROW) & \
        (xx >= HEAD_COLS[0]) & (xx <= HEAD_COLS[1])
    head &= D.parts["body"]
    legs = D.parts["near_leg"] | D.parts["far_leg"]
    # the head's own outline where it meets the shoulders stays Codex's (pasted, it drew a black line across the chest)
    dk = V.dark(d)
    rest = ~head & (d[..., 3] > 0)
    inner = dk & head & ndimage.binary_dilation(rest & ~dk, structure=V.R.CROSS)
    head &= ~inner
    for key, name in TAKES.items():
        s, (ox, oy) = sample(name)
        s = snap(s, pal)
        H, W = s.shape[:2]
        # the legs: Codex's squares round the design's legs cleared first (its legs were drawn a square wider here and
        # there), then the design's legs and head laid over
        lg = np.zeros((H, W), bool)
        lg[oy:oy + D.H, ox:ox + D.W] = legs
        box = np.zeros((H, W), bool)
        box[oy + V.LEG_TOP:, ox + 7:ox + 45] = True
        s[ndimage.binary_dilation(lg, structure=np.ones((3, 3))) & box] = 0
        src = np.zeros((H, W, 4), np.uint8)
        src[oy:oy + D.H, ox:ox + D.W][head | legs] = d[head | legs]
        m = src[..., 3] > 0
        s[m] = src[m]
        # crumbs the clearing left (under 6 squares, apart from the figure)
        op = s[..., 3] > 0
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(op, lbl, range(1, n + 1))
            for j in range(1, n + 1):
                if sz[j - 1] < 6:
                    s[lbl == j] = 0
        Image.fromarray(s).save(lp(os.path.join(OUT, f"pose_{key}.png")))
        Image.fromarray(np.repeat(np.repeat(s, 8, 0), 8, 1)).save(lp(os.path.join(OUT, f"pose_{key}_8x.png")))
        with open(lp(os.path.join(OUT, f"pose_{key}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"take": name, "origin": [ox, oy], "size": [W, H]}, f)
        print(key, name, W, "x", H, "design origin", (ox, oy))


if __name__ == "__main__":
    main()
