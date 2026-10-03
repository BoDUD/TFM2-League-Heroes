#!/usr/bin/env python3
"""Infernal Chains' flight as one chain paid out from Aatrox's hand: assets/source/aatrox/aatrox_fx_w_chain_grow.png
(8x) and its cell in aatrox_fx_anchors.json, from the effects pack's own chain (aatrox_fx_w_chain.png frame 1: the
burning claw head and the 8-square link it repeats).

    python tools/art/chain_aatrox.py

The first chain picture was the claw and three links (about 25 x 10 px) flying 5000 units a tick: the whole reach in
0.2 s, and the user saw nothing (「W 甩出去的锁链看不到」). League's chain flies 1800 units a second (2200 a tick here,
build_aatrox.py w_speed) and stays tied to his hand. Frame k is the head with k x SPEED px of links behind it, so the
tail stays on the hand while the projectile (the head) flies; past the reach the last frame holds.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aatrox")
Z = 8
SPEED = 2.2                 # px a tick (build_aatrox.py w_speed 2200)
REACH = 66                  # px (w_reach 66000)
LINK = (6, 14)              # the link unit's columns in the chain picture (8 squares, rows 3-11)
HEAD = (18, 28)             # the claw head's columns (rows 1-13)
ROWS = (1, 14)


def main():
    path = G.lp(os.path.join(SRC, "aatrox_fx_anchors.json"))
    with open(path, encoding="utf-8") as f:
        anchors = json.load(f)
    c = anchors["w_chain"]
    cw, ch = c["cell"]
    big = np.asarray(Image.open(G.lp(os.path.join(SRC, "aatrox_fx_w_chain.png"))).convert("RGBA"))
    first = big[Z // 2::Z, Z // 2::Z][:, :cw]
    r0, r1 = ROWS
    head = first[r0:r1, HEAD[0]:HEAD[1]]
    unit = first[r0:r1, LINK[0]:LINK[1]]
    ax_in_head = c["anchor"][0] - HEAD[0]                 # the projectile's spot inside the head
    hw, uw, h = head.shape[1], unit.shape[1], head.shape[0]
    W = REACH + hw + 2
    n = math.ceil(REACH / SPEED)
    frames = []
    for k in range(1, n + 1):
        length = min(REACH, int(round(k * SPEED)))
        f = np.zeros((h, W, 4), np.uint8)
        x_head = W - hw
        # links leftward from the head, whole units first, the last one cut at the tail
        x = x_head
        while x > x_head - length:
            x0 = x - uw
            src0 = max(0, (x_head - length) - x0)
            seg = unit[:, src0:]
            dst0 = x0 + src0
            m = seg[..., 3] > 0
            f[:, dst0:dst0 + seg.shape[1]][m] = seg[m]
            x = x0
        m = head[..., 3] > 0
        f[:, x_head:x_head + hw][m] = head[m]
        frames.append(f)
    strip = np.concatenate(frames, axis=1)
    Image.fromarray(np.repeat(np.repeat(strip, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, "aatrox_fx_w_chain_grow.png")))
    anchors["w_chain_grow"] = {"cell": [W, h], "anchor": [W - hw + ax_in_head, c["anchor"][1] - r0], "frames": n}
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(anchors, f, indent=1)
    print("aatrox_fx_w_chain_grow.png", n, "frames", W, "x", h, "anchor", anchors["w_chain_grow"]["anchor"])


if __name__ == "__main__":
    main()
