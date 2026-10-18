#!/usr/bin/env python3
"""Gangplank's gun-hand poses (Codex, 2026-10-18, assets/source/gangplank/codex_poses: gangplank-pose-Q.png - the arm
out, the cannon aimed - and gangplank-pose-R.png - the arm up, the cannon to the sky) read back onto the design's grid
as stamps for tools/art/rig_gangplank.py.

    python tools/art/design_gangplank_poses.py      # -> assets/source/gangplank/hd/pose_{Q,R}.png + pose_{Q,R}_edit.png

The pack (tools/art/pack_gangplank_poses.py) drew the design at PX = 17 px a square with its (0, 0) at (X0, Y0) on the
1254 canvas; Codex kept that grid (Q exactly, R 2 px off: the offset is searched on the lower body, which must not have
changed). Each square is read as the commonest colour of its middle 7 x 7 pixels (alpha >= 128, at least half of them),
snapped to the design's own palette. The stamp is the design's grid with TOP rows above and LEFT / RIGHT columns beside
it (R's cannon rises above the hat). The edit mask: the squares that changed against the design (a colour step over 40
or an alpha change) or held the old arm and cannon, inside EDIT[pose] - the arm's reach, never the head or the face
(Codex drifted a few squares elsewhere: those keep the design's squares). Inside the mask the rig puts the stamp's square,
clear ones too (the old arm's place); outside, the design as posed.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_gangplank_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gangplank")
X0, Y0, PX = 142, 160, 17
TOP, LEFT, RIGHT = 12, 8, 8
# (row0, row1, col0, col1) boxes in design squares, inclusive: where a pose may differ from the design
EDIT = {"Q": [(8, 16, 0, 19), (17, 34, 0, 58)],
        "R": [(-12, 16, 0, 19), (17, 34, 0, 22)]}


def sample(a, H, W, dx=0, dy=0):
    out = np.zeros((H + TOP, W + LEFT + RIGHT, 4), np.int64)
    for r in range(-TOP, H):
        for c in range(-LEFT, W + RIGHT):
            x = X0 + c * PX + 5 + dx
            y = Y0 + r * PX + 5 + dy
            if x < 0 or y < 0 or x + 7 > a.shape[1] or y + 7 > a.shape[0]:
                continue
            win = a[y:y + 7, x:x + 7].reshape(-1, 4)
            win = win[win[:, 3] >= 128]
            if len(win) < 25:
                continue
            cols, cnt = np.unique(win[:, :3], axis=0, return_counts=True)
            out[r + TOP, c + LEFT, :3] = cols[cnt.argmax()]
            out[r + TOP, c + LEFT, 3] = 255
    return out


def main():
    des = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")).astype(np.int64)
    H, W = des.shape[:2]
    pal = np.unique(des[des[..., 3] > 0][:, :3], axis=0)
    import rig_gangplank as G
    D = G.design()
    old = D.parts["gun"] | D.parts["near_arm"]
    for name in ("Q", "R"):
        a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_poses", f"gangplank-pose-{name}.png"))).convert("RGBA"))
        a = a.astype(np.int64)
        best = None
        for dx in range(-8, 9, 2):
            for dy in range(-8, 9, 2):
                s = sample(a, H, W, dx, dy)
                body, ref = s[TOP + 36:TOP + H, LEFT:LEFT + W], des[36:H]
                both = (body[..., 3] > 0) & (ref[..., 3] > 0)
                err = np.abs(body[..., :3] - ref[..., :3]).sum(-1)[both].mean() \
                    + 300 * ((body[..., 3] > 0) != (ref[..., 3] > 0)).mean()
                if best is None or err < best[0]:
                    best = (err, dx, dy, s)
        err, dx, dy, s = best
        op = s[..., 3] > 0
        px = s[op][:, :3]
        s[op, :3] = pal[np.argmin(((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1), 1)]
        big = np.zeros_like(s)
        big[TOP:TOP + H, LEFT:LEFT + W] = des
        diff = (np.abs(s[..., :3] - big[..., :3]).sum(-1) > 40) | ((s[..., 3] > 0) != (big[..., 3] > 0))
        olds = np.zeros(diff.shape, bool)
        olds[TOP:TOP + H, LEFT:LEFT + W] = old
        box = np.zeros(diff.shape, bool)
        for r0, r1, c0, c1 in EDIT[name]:
            box[r0 + TOP:r1 + TOP + 1, c0 + LEFT:c1 + LEFT + 1] = True
        edit = box & (diff | olds)
        Image.fromarray(s.astype(np.uint8)).save(lp(os.path.join(SRC, "hd", f"pose_{name}.png")))
        Image.fromarray((edit * 255).astype(np.uint8)).save(lp(os.path.join(SRC, "hd", f"pose_{name}_edit.png")))
        print(name, "offset", dx, dy, "lower-body mismatch", round(float(err), 1), "edit squares", int(edit.sum()),
              "of", int(diff.sum()), "changed")


if __name__ == "__main__":
    main()
