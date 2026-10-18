#!/usr/bin/env python3
"""Akshan's gun-arm pose (Codex, assets/source/akshan/codex_poses: akshan-pose-aim-<n>.png - the near arm held straight
out forward, the relic pistol level) read back onto the design's grid as a stamp for tools/art/rig_akshan.py.

    python tools/art/design_akshan_poses.py [--take N]   # -> assets/source/akshan/hd/pose_aim.png + pose_aim_edit.png

The pack (tools/art/pack_akshan_poses.py) drew the design at PX = 15 px a square with its (0, 0) at (X0, Y0) on the
1254 canvas; Codex keeps that grid to a few pixels (searched on the lower body, which must not have changed). Each square
is read as the commonest colour of its middle 7 x 7 pixels (alpha >= 128, at least half of them), snapped to the design's
own palette. The stamp is the design's grid with RIGHT columns beside it (the gun held out reaches past his right side).
The edit mask: the squares that changed against the design (a colour step over 40 or an alpha change) or held the old
gun arm, inside EDIT - the arm's reach, never the head or the face (Codex drifts a few squares elsewhere: those keep the
design's squares). Inside the mask the rig puts the stamp's square, clear ones too (the old arm's place); outside, the
design as posed. Gangplank's way (tools/art/design_gangplank_poses.py).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rig_akshan as A  # noqa: E402

lp = A.lp
SRC = os.path.join(ROOT, "assets", "source", "akshan")
X0, Y0, PX = 90, 165, 15
RIGHT = 34
# (row0, row1, col0, col1) boxes in design squares, inclusive: where the pose may differ from the design - the old gun
# arm left of the hair (and its hooks over the hair's top-left), the arm across the chest under the beard and the gun
# held out (its hooks spread up and down past his right side, rows 18-52); never the head (rows 12-32, columns 12-43)
EDIT = [(0, 11, 0, 18), (12, 32, 0, 11), (33, 47, 0, 45 + RIGHT), (18, 52, 44, 45 + RIGHT)]


def sample(a, H, W, dx=0, dy=0):
    out = np.zeros((H, W + RIGHT, 4), np.int64)
    for r in range(H):
        for c in range(W + RIGHT):
            x = X0 + c * PX + 4 + dx
            y = Y0 + r * PX + 4 + dy
            if x < 0 or y < 0 or x + 7 > a.shape[1] or y + 7 > a.shape[0]:
                continue
            win = a[y:y + 7, x:x + 7].reshape(-1, 4)
            win = win[win[:, 3] >= 128]
            if len(win) < 25:
                continue
            cols, cnt = np.unique(win[:, :3], axis=0, return_counts=True)
            out[r, c, :3] = cols[cnt.argmax()]
            out[r, c, 3] = 255
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", type=int, default=1)
    a_ = ap.parse_args()
    des = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")).astype(np.int64)
    H, W = des.shape[:2]
    pal = np.unique(des[des[..., 3] > 0][:, :3], axis=0)
    D = A.design()
    old = D.parts["gun"]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_poses", f"akshan-pose-aim-{a_.take}.png"))).convert("RGBA"))
    a = a.astype(np.int64)
    best = None
    for dx in range(-8, 9, 2):
        for dy in range(-8, 9, 2):
            s = sample(a, H, W, dx, dy)
            body, ref = s[48:H, :W], des[48:H]
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
    big[:, :W] = des
    diff = (np.abs(s[..., :3] - big[..., :3]).sum(-1) > 40) | ((s[..., 3] > 0) != (big[..., 3] > 0))
    oldb = np.zeros(diff.shape, bool)
    oldb[:, :W] = old
    box = np.zeros(diff.shape, bool)
    for r0, r1, c0, c1 in EDIT:
        box[max(0, r0):r1 + 1, max(0, c0):c1 + 1] = True
    edit = (diff | oldb) & box
    outside = diff & ~box
    print(f"take {a_.take}: offset ({dx},{dy}) lower-body error {err:.1f}; edit {int(edit.sum())} squares, "
          f"changes left outside the arm's reach {int(outside.sum())}")
    # pieces left apart from the figure once the stamp is on (the old gun's outline beside the hair, columns 12-13 rows
    # 12-20, which Codex copied too): squares of any small 8-connected piece other than the figure are cleared
    from scipy import ndimage
    comp = big.copy()
    comp[edit] = s[edit]
    op = comp[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    main_ = 1 + int(np.argmax(sizes))
    stray = (lbl > 0) & (lbl != main_) & np.isin(lbl, [k + 1 for k, z in enumerate(sizes) if z <= 10])
    s[stray] = 0
    edit |= stray
    print(f"stray pieces cleared: {int(stray.sum())} squares")
    stamp = s.astype(np.uint8)
    Image.fromarray(stamp).save(lp(os.path.join(SRC, "hd", "pose_aim.png")))
    Image.fromarray((edit * 255).astype(np.uint8)).save(lp(os.path.join(SRC, "hd", "pose_aim_edit.png")))


if __name__ == "__main__":
    main()
