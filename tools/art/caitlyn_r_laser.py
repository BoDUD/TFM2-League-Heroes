#!/usr/bin/env python3
"""Caitlyn's laser sight for Ace in the Hole (the user, 2026-10-02: "女警大招释放时候没有线 补一个特效吧 不然中没中 打谁的都
不知道" - League draws a red line from her rifle to the target while she channels).

    python tools/art/caitlyn_r_laser.py      # writes assets/source/caitlyn/caitlyn_fx_r_laser.png + its anchors entry

The line is a train of links (league_fiddlesticks W's chain): during the channel the kit sends a TargetProjectile at the
target every 2 ticks at 12000 a tick (24 px apart) and each link grows 12, 24, 36 px a tick after it leaves the
rifle, so the newest link always reaches back to the muzzle and the older ones overlap: one unbroken line that ends
on him (a homing projectile is removed on its target). Each link is drawn pointing right with its head on the anchor
and the tail behind, 2 px thick in the crosshair's reds (FF6A6A over D13845); tools/art/import_caitlyn.py keeps it
hidden until its head is out of the rifle (also the spawn tick, when a TargetProjectile's view points straight up,
champion-data "A beam from a raised weapon").
"""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "caitlyn")
Z = 8
LENGTHS = (12, 24, 36)
CORE, EDGE = (0xFF, 0x6A, 0x6A, 255), (0xD1, 0x38, 0x45, 255)
W, H = 37, 3                     # the head is column 35 (its right edge the anchor, 36.0); rows 1 (core), 2 (edge)


def lp(p):
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\") else p


def main():
    cells = []
    for n in LENGTHS:
        a = np.zeros((H, W, 4), np.uint8)
        a[1, W - 1 - n:W - 1] = CORE
        a[2, W - 1 - n:W - 1] = EDGE
        cells.append(a)
    strip = np.concatenate(cells, axis=1)
    big = np.repeat(np.repeat(strip, Z, axis=0), Z, axis=1)
    Image.fromarray(big, "RGBA").save(lp(os.path.join(SRC, "caitlyn_fx_r_laser.png")))
    path = lp(os.path.join(SRC, "caitlyn_fx_anchors.json"))
    with open(path, encoding="utf-8") as f:
        anchors = json.load(f)
    anchors["r_laser"] = {"cell": [W, H], "anchor": [float(W - 1), 2.0], "frames": len(LENGTHS), "ticks": [1, 1, 1]}
    with open(path, "w", encoding="utf-8") as f:            # the file's own layout: one strip a line
        f.write("{\n" + ",\n".join(f"  {json.dumps(k)}: {json.dumps(v)}" for k, v in anchors.items()) + "\n}\n")
    print("wrote caitlyn_fx_r_laser.png and its anchors")


if __name__ == "__main__":
    main()
