#!/usr/bin/env python3
"""Alistar's run on the design's own body and legs -> assets/source/native/alistar_run.png (8x, the run cells of
alistar_cells.json).

    python tools/art/run_alistar.py [--review OUT.png]

The user, on the run built from Codex's draft: 「牛头走路没有交叉步」「单脚走路的」「走路和待机的体型不一样？？走路还会变大？？」 -
Codex's run showed one leg under a body a size bigger than the idle's. As Sett's approved run (tools/art/run_sett.py)
the upper body is the design itself: everything but the two legs (the hump, the head, both hanging arms with their
shackles and chains, the loincloth), one block in every frame, sinking a row over its belly on the contacts (BOB).
The legs are the design's own two legs (LEGS: the purple fur from under the loincloth to the hooves, without the
chain beside the far one or the loincloth between them), each turned WHOLE about its hip by RotSprite - never cut at
the knee, never more than ~27 degrees (rig lessons from Aatrox) - and set back on the ground: the planted one's hoof on
the soles' row, the swinging one lifted. The hips come in 2 squares each (8 apart instead of 12) so the hooves pass
each other: the near hoof leads, then trails (near minus far hoof x changes sign twice a cycle). The near leg is drawn
over the far one, the body (loincloth, hands) over both; then the outline is closed.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402
from kayn_kit import rotsprite  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "alistar_native.png")
CELLS = os.path.join(NATIVE, "alistar_cells.json")
OUT = os.path.join(NATIVE, "alistar_run.png")
PIVOT = (64, 88)                  # the design canvas's standing point; its soles on row 99
SOLE = 99
OUTLINE = (0x12, 0x03, 0x19)
CHAIN = {(0x44, 0x3A, 0x3F), (0xA8, 0x82, 0x6E)}                                 # the far shackle's chain
CLOTH = {(0x87, 0x3E, 0x28), (0xC8, 0x67, 0x2F), (0xF5, 0xB7, 0x43), (0xFB, 0xD5, 0x9B), (0x42, 0x17, 0x14)}
# the legs on the design canvas: (rows, columns) boxes; the hooves (rows 95-99) whole, above them the fur only
LEGS = {"far": dict(top=86, x0=44, x1=60, hip=(54.0, 87.0), chain_x=49),
        "near": dict(top=86, x0=60, x1=74, hip=(66.0, 87.0), chain_x=None)}
HOOF_ROW = 95
IN = {"far": 5, "near": -4}       # the hips come in (squares)
LEN = 12.0                        # hip to sole
# one hoof over the cycle (phase 0 = its contact, ahead): (hoof x from the hip, lift of the hoof)
STEP = [(7, 0), (3.5, 0), (0, 0), (-3.5, 0), (-7, 1), (-4.5, 3), (0, 3), (4.5, 1)]
PHASE = {"near": 0, "far": 4}
BOB = [1, 0, 0, 0, 1, 0, 0, 0]    # the body a row lower on each contact
BOB_ROW = 84                      # rows above it sink (the belly; the loincloth and the hands' lower rows stay)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def col(p):
    return tuple(int(v) for v in p[:3])


def split(des):
    """The two legs' masks and the upper body (the design without them)."""
    op = des[..., 3] > 0
    masks = {}
    for name, L in LEGS.items():
        m = np.zeros(op.shape, bool)
        for y in range(L["top"], SOLE + 1):
            for x in range(L["x0"], L["x1"]):
                if not op[y, x]:
                    continue
                c = col(des[y, x])
                if y >= HOOF_ROW:
                    m[y, x] = True
                    continue
                if c in CLOTH or (L["chain_x"] is not None and x < L["chain_x"] and c in CHAIN | {OUTLINE}):
                    continue
                if c in CHAIN:
                    continue
                m[y, x] = True
        masks[name] = m
    # a pixel claimed by both (the shared column) goes to the near leg
    masks["far"] &= ~masks["near"]
    upper = des.copy()
    for m in masks.values():
        upper[m] = 0
    return masks, upper


def leg_sprite(des, m, hip):
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    s[m[y0:y1, x0:x1]] = des[y0:y1, x0:x1][m[y0:y1, x0:x1]]
    return s, (hip[0] - x0, hip[1] - y0)


def stamp(can, s, at):
    m = s[..., 3] > 0
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        Y, X = y + at[1], x + at[0]
        if 0 <= Y < can.shape[0] and 0 <= X < can.shape[1]:
            can[Y, X] = s[y, x]


def frame(des, masks, upper, k):
    can = np.zeros_like(des)
    feet = {}
    for name in ("far", "near"):
        L = LEGS[name]
        dx, lift = STEP[(k + PHASE[name]) % 8]
        hip = (L["hip"][0] + IN[name], L["hip"][1])
        s, j = leg_sprite(des, masks[name], L["hip"])
        deg = math.degrees(math.atan2(dx, LEN))          # + counter-clockwise: the hoof forward (right)
        r, rj = rotsprite(s, j, deg)
        op = r[..., 3] > 0
        ys, xs = np.nonzero(op)
        low = ys.max() - rj[1]                           # the hoof's lowest row under the hip
        y_hip = SOLE - lift - low                        # back on the ground (or lifted)
        at = (int(round(hip[0] - rj[0])), int(round(y_hip - rj[1])))
        stamp(can, r, at)
        feet[name] = float(np.median(xs[ys >= ys.max() - 1])) + at[0]
    # the body over the legs, sinking a row over its belly on the contacts
    body = upper.copy()
    if BOB[k]:
        moved = np.zeros_like(body)
        moved[1:BOB_ROW + 1] = body[0:BOB_ROW]
        moved[BOB_ROW + 1:] = body[BOB_ROW + 1:]
        keep = moved[BOB_ROW + 1:, :, 3] == 0
        moved[BOB_ROW + 1:][keep] = body[BOB_ROW + 1:][keep]
        body = moved
    m = body[..., 3] > 0
    can[m] = body[m]
    pad = np.pad(can, ((2, 2), (2, 2), (0, 0)))
    pad, _, _ = G.complete_outline(pad, color=OUTLINE, feet=SOLE + 2)
    can = pad[2:-2, 2:-2]
    can[SOLE + 1:] = 0
    return can, feet


def build():
    des = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[4::8, 4::8].copy()
    masks, upper = split(des)
    cells = json.load(open(lp(CELLS), encoding="utf-8"))
    frs = cells["tags"]["run"]
    cols, rows = layout(len(frs))
    strip = np.zeros((rows * 96, cols * 128, 4), np.uint8)
    report = []
    for k, fr in enumerate(frs):
        can, feet = frame(des, masks, upper, k)
        px, py = fr["pivot"]
        X, Y = (k % cols) * 128 + px - PIVOT[0], (k // cols) * 96 + py - PIVOT[1]
        ys, xs = np.nonzero(can[..., 3] > 0)
        for y, x in zip(ys, xs):
            yy, xx = Y + y, X + x
            if (k // cols) * 96 <= yy < (k // cols + 1) * 96 and (k % cols) * 128 <= xx < (k % cols + 1) * 128:
                strip[yy, xx] = can[y, x]
        report.append(round(feet["near"] - feet["far"], 1))
    return strip, report, des


def review(path, strip, des):
    cells = json.load(open(lp(CELLS), encoding="utf-8"))
    frs = cells["tags"]["run"]
    cols, _ = layout(len(frs))
    z = 6
    tiles = []
    ys, xs = np.nonzero(des[..., 3] > 0)
    tiles.append(des[PIVOT[1] - 40:PIVOT[1] + 13, PIVOT[0] - 28:PIVOT[0] + 30])
    for k, fr in enumerate(frs):
        px, py = fr["pivot"]
        f = strip[(k // cols) * 96:(k // cols + 1) * 96, (k % cols) * 128:(k % cols + 1) * 128]
        tiles.append(f[py - 40:py + 13, px - 28:px + 30])
    h, w = tiles[0].shape[:2]
    img = Image.new("RGB", (len(tiles) * (w * z + 6), h * z + 24), (92, 98, 86))
    d = ImageDraw.Draw(img)
    for i, t in enumerate(tiles):
        im = Image.fromarray(np.ascontiguousarray(t)).resize((w * z, h * z), Image.NEAREST)
        img.paste(im, (i * (w * z + 6), 24), im)
        d.text((i * (w * z + 6) + 4, 4), "idle" if i == 0 else f"run {i}", fill=(255, 255, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    strip, report, des = build()
    Image.fromarray(strip).resize((strip.shape[1] * 8, strip.shape[0] * 8), Image.NEAREST).save(lp(OUT))
    print("near - far hoof x per frame:", report)
    if a.review:
        review(a.review, strip, des)


if __name__ == "__main__":
    main()
