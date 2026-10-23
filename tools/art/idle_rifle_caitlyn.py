#!/usr/bin/env python3
"""league_caitlyn's idle with the action frames' straight rifle (the user, 2026-10-23: 「凯特琳怎么感觉待机时候枪是歪的？」
「把凯特琳待机的枪换成动作帧那把直枪」): her idle is the approved design (hd/design.png, Codex's picture read back), whose
rifle steps unevenly and bends up at the muzzle. tools/art/actions_caitlyn_hd.straighten() - the same step every
redrawn action frame went through - takes Codex's rifle out and puts tools/art/rifle_caitlyn.py's in: the way nearest
Codex's angle, its grip on Codex's grip point, her hands over it, the old rifle's squares inside her outline filled
from their neighbours. The result goes back on the design's own canvas at the same place (her soles and standing
point do not move; tools/art/rig_caitlyn_hd.py DESIGN_ROWS), 65 rows; the 3 empty columns the shorter reach leaves on
the right are cut (the design is read back trimmed).

    python tools/art/idle_rifle_caitlyn.py [--review DIR]

Reads hd/design_codex_rifle.png (the design as approved, kept once) and writes hd/design.png; then
tools/art/rig_caitlyn_hd.py and tools/art/hero_reels.py --hero caitlyn. --review writes the two at 8x side by side.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import actions_caitlyn_hd as AC  # noqa: E402

HD = AC.HD
SRC = os.path.join(HD, "design_codex_rifle.png")
OUT = os.path.join(HD, "design.png")
# Codex's rifle in the design, read off it by hand (squares, x right, y down): the butt of the stock low on her left
# and the muzzle up by her hat. straighten()'s own line fit took only the receiver-to-muzzle stretch (the stock bends
# away), which moved the grip up the barrel and the new rifle out of the canvas.
STOCK = (6.5, 48.5)
MUZZLE = (53.5, 11.5)


def lp(path):
    return AC.lp(path)


def straight_idle():
    if not os.path.exists(lp(SRC)):
        shutil.copyfile(lp(OUT), lp(SRC))
    d = np.asarray(Image.open(lp(SRC)).convert("RGBA"))
    fit = AC.find_rifle
    AC.find_rifle = lambda m, **k: (np.array(STOCK) + AC.PAD, np.array(MUZZLE) + AC.PAD)
    try:
        out, (dx, dy), info = AC.straighten(d)
    finally:
        AC.find_rifle = fit
    # back on the design's canvas: the old corner moved by (dx, dy) inside `out`
    can = np.zeros_like(d)
    h, w = out.shape[:2]
    for y in range(h):
        for x in range(w):
            Y, X = y - dy, x - dx
            if out[y, x, 3] and 0 <= Y < can.shape[0] and 0 <= X < can.shape[1]:
                can[Y, X] = out[y, x]
    lost = int((out[..., 3] > 0).sum() - (can[..., 3] > 0).sum())
    # the design is read back trimmed to its squares (rig_caitlyn_hd.design()): the straight muzzle stops 3 columns
    # short of Codex's, so the empty columns on the right go (the left edge, rows and her standing point stay)
    xs = np.nonzero((can[..., 3] > 0).any(0))[0]
    if xs.min() != 0:
        sys.exit("the left edge moved")
    can = can[:, :xs.max() + 1]
    return d, can, info, lost


def review(d, can, path, Z=8):
    h, w = d.shape[:2]
    img = Image.new("RGBA", ((2 * w + 4) * Z, h * Z), (200, 200, 200, 255))      # (the new one is no wider)
    for k, a in enumerate((d, can)):
        img.alpha_composite(Image.fromarray(a).resize((w * Z, h * Z), Image.NEAREST), (k * (w + 4) * Z, 0))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the design before / after at 8x here")
    a = ap.parse_args()
    d, can, info, lost = straight_idle()
    print(f"rifle: Codex's at {info['angle']} degrees -> the straight one at {info['way']}, grip {info['grip']}; "
          f"{lost} squares off the {d.shape[1]} x {d.shape[0]} canvas")
    if lost:
        sys.exit("the straight rifle does not fit the design's canvas")
    Image.fromarray(can).save(lp(OUT))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        review(d, can, os.path.join(a.review, "caitlyn_idle_rifle_8x.png"))


if __name__ == "__main__":
    main()
