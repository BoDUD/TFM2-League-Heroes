#!/usr/bin/env python3
"""Infernal Chains' flight as one chain paid out from Aatrox's hand: assets/source/aatrox/aatrox_fx_w_chain_grow.png
(8x) and its cell in aatrox_fx_anchors.json, from the effects pack's own chain (aatrox_fx_w_chain.png frame 1: the
burning claw head and the 8-square link it repeats).

    python tools/art/chain_aatrox.py

The first chain picture was the claw and three links (about 25 x 10 px) flying 5000 units a tick: the whole reach in
0.2 s, and the user saw nothing (「W 甩出去的锁链看不到」). League's chain flies 1800 units a second (2200 a tick here,
build_aatrox.py w_speed) and stays tied to his hand. Frame k (k ticks after the chain leaves) is the head with links
back to his hand; past the reach the last frame holds.

The hand, not the projectile's start: the chain (a LinearProjectile, y_offset -3000) starts 8 px over his pivot, on
his chest, while W's throw (skill2 4-5) holds the red claw out at (13..18, -12). The links used to run back to the
start, so for 8 ticks the burning head crossed his belly and arm and the chain then came out of his torso (the effects
audit, 2026-10-04). Now the links end TAIL px along the flight from the start - at his hand whatever the cast's
direction, since the picture turns with the flight -, shown from its first moving tick (SHOW 0; a chain that hits
within a few ticks must still be seen). The chain runs at the projectile's height, 4-8 px under the claw (the
picture turns upside down on a leftward cast, so it cannot carry a height of its own; lifting it needs a higher
y_offset, which also moves the chain's path and the ring - gameplay).
build_aatrox.py draws the chain under the units (z -1, league_thresh's chain): the links' end TAIL px along the
flight lies inside his silhouette whatever the angle (his arm on a level throw, his head thrown up, his legs thrown
down), so the chain comes out from behind him - drawn over him, a steep throw put the burning head on his face or his
groin and ran the links out of his head (a quarter of the logged casts fly 60 degrees or more off level).
The links are the pack's iron only: its fire ember dots (1-2 squares over and under each link, most of them loose)
drew two dotted lines along the chain at game size.
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
IRON = ("1A1624", "39334A", "625B74", "9A93A8", "D9D4DE")   # import_aatrox.RAMPS["IRON"]: the links keep only these
# px along the flight from the start to the links' end: under the claw arm while it is out (skill2 4-5: x 2-18, rows
# -14..-10) and on the near fist once it is back (skill2 6 and the idle: x 8-11), so the chain never hangs loose in the
# air in front of him (at 15, the claw's middle, it floated 4 px off his fist after tick 25)
TAIL = 11
# px flown before the chain shows: none (fix round 1 of phase 1b). The chain does not penetrate - it goes with its
# picture on the first enemy it touches - and every tick it waits hides it on more casts: at 25 px (tick 26) 71% of
# the logged chains (12 SDK games) were never seen, at 8 px (tick 18) 26%; HEAD's chain, shown from its first moving
# tick, 16%. Drawn under him (z -1) the head and the links over his body are hidden by his sprite, so the chain comes
# out from behind him (his arm on a level throw, his head or legs thrown steeply) from the throw on; w_throw's claw
# flash ends as the head clears his arm (import_aatrox.py), so one fire spot shows at a time
SHOW = 0


def hexes(a):
    return np.array([["%02X%02X%02X" % tuple(int(v) for v in p[:3]) for p in row] for row in a])


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
    unit = first[r0:r1, LINK[0]:LINK[1]].copy()
    unit[(unit[..., 3] > 0) & ~np.isin(hexes(unit), IRON)] = 0      # the ember dots off
    ax_in_head = c["anchor"][0] - HEAD[0]                 # the projectile's spot inside the head
    hw, uw, h = head.shape[1], unit.shape[1], head.shape[0]
    longest = REACH - TAIL - ax_in_head                   # links behind the head at the full reach
    W = longest + hw + 2
    n = math.ceil(REACH / SPEED)
    frames = []
    for k in range(1, n + 1):
        d = min(REACH, k * SPEED)                         # px flown: the projectile's spot from the start
        f = np.zeros((h, W, 4), np.uint8)
        if d >= SHOW:
            length = max(0, int(round(d)) - TAIL - ax_in_head)
            x_head = W - hw
            # links leftward from the head, whole units first, the last one cut at the hand
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
    shown = next(k for k in range(1, n + 1) if k * SPEED >= SHOW)
    print("aatrox_fx_w_chain_grow.png", n, "frames", W, "x", h, "anchor", anchors["w_chain_grow"]["anchor"],
          f"- shown from frame {shown} ({shown * SPEED:.1f} px flown), the links from {TAIL} px along the flight")


if __name__ == "__main__":
    main()
