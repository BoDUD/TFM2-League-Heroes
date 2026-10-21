#!/usr/bin/env python3
"""Heimerdinger's props from Codex (pack B, assets/source/heimerdinger/codex_props, 2026-10-21): the backpack crane in its
17 positions and R's gear in 3, read back at the design's square size and placed where the guides had them.

    python tools/art/design_heimerdinger_props.py [--review DIR]   # writes assets/source/heimerdinger/hd/prop_<name>.png

Codex drew each at its own scale (its HANDOFF: joints, thickness and place drift; the joint housings 77 to 144 px across),
so every crane is read with its widest part - a joint housing - at JOINT squares (the guide's 7): the 98th percentile
of the drawn arm's half-width (its distance transform) gives the picture's px a square; regrid reads it there. Its root
(the arm's square farthest from the red claw) goes on League's crane root for that frame (Rocket_Base, the same joint
the guide started from); the crane is laid behind him, the root hidden in the mane. R's gear is read with its red ring
as wide as the guide's (RING squares) and the ring's middle on the guide's; the drum alone (gear_drum) is read at the
burst's scale and set where the burst has its drum. One palette for the cranes and one for the gear (K colours,
design_varus.kmeans). Writes hd/prop_<name>.png on a canvas with the design's (0, 0) at (PAD, TOP).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_heimerdinger_poses as DP  # noqa: E402  regrid_at, to_sq, PAD
import design_varus as dv  # noqa: E402
import pack_heimerdinger_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heimerdinger", "codex_props", "raw")
HD = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd")
JOINT = 7.0                  # a joint housing's squares across (the guide's widest)
RING = 56.0                  # R's ring: squares across (the guide's ellipse)
RING_MID = (25.0, 10.0)      # its middle (design squares)
K = 16
PAD = DP.PAD
TOP = 100                    # the props' canvas: the design's (0, 0) at (PAD, TOP) - the crane reaches 70 squares above
JOINTS = DP.JOINTS


def lp(p):
    return PK.lp(p)


def masks(a):
    op = a[..., 3] >= 128
    r, g, b = (a[..., i].astype(int) for i in range(3))
    olive = op & (g > r * 0.9) & (g > b * 1.2) & (g > 60) & (r > 50)
    red = op & (r > 150) & (g < 80) & (b < 80)
    return op, olive, red


def joint_px(a):
    op, olive, _ = masks(a)
    r, g, b = (a[..., i].astype(int) for i in range(3))
    dark = op & (r < 70) & (g < 70) & (b < 70)
    dt = ndimage.distance_transform_edt(ndimage.binary_closing(olive | dark, iterations=2))
    return 2 * float(np.percentile(dt[olive], 98))


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"heimerdinger-prop-{name}.png"))).convert("RGBA")).copy()
    g, bx, by = DP.regrid_at(a, size)
    return a, g, bx, by


def place(can, g, at):
    ys, xs = np.nonzero(g[..., 3] > 0)
    H, W = can.shape[:2]
    ok = (ys + at[1] >= 0) & (ys + at[1] < H) & (xs + at[0] >= 0) & (xs + at[0] < W)
    can[ys[ok] + at[1], xs[ok] + at[0]] = g[ys[ok], xs[ok]]


def crane(name, J, W, H):
    tag, ms, held, _ = PK.PROPS[name]
    a0 = np.asarray(Image.open(lp(os.path.join(SRC, f"heimerdinger-prop-{name}.png"))).convert("RGBA"))
    size = joint_px(a0) / JOINT
    a, g, bx, by = read(name, size)
    _, olive, red = masks(g)
    ry, rx = np.nonzero(red)
    oy, ox = np.nonzero(olive)
    claw = (rx.mean(), ry.mean())
    k = np.argmax((ox - claw[0]) ** 2 + (oy - claw[1]) ** 2)
    root = (ox[k], oy[k])
    base = PK.xy(PK.row(J, tag, ms)["j"], "crane0")
    at = (int(round(PAD + base[0] - root[0])), int(round(TOP + base[1] - root[1])))
    can = np.zeros((H, W, 4), np.uint8)
    place(can, g, at)
    return can, {"scale_px": round(size, 2), "root": [int(root[0]), int(root[1])], "at": at}


def ring_of(g):
    _, _, red = masks(g)
    ys, xs = np.nonzero(red)
    big = ys > np.percentile(ys, 40) if len(ys) else ys    # the ring is the low, wide red; the balls are high
    return xs[big].min(), xs[big].max(), ys[big].mean()


def gear(name, W, H, burst_size=None):
    a0 = np.asarray(Image.open(lp(os.path.join(SRC, f"heimerdinger-prop-{name}.png"))).convert("RGBA"))
    if name == "gear_drum":
        size = burst_size
    else:
        _, _, red = masks(a0)
        ys, xs = np.nonzero(red)
        low = ys > np.percentile(ys, 40)
        size = (xs[low].max() - xs[low].min() + 1) / RING
    a, g, bx, by = read(name, size)
    can = np.zeros((H, W, 4), np.uint8)
    if name == "gear_drum":
        ys, xs = np.nonzero(g[..., 3] > 0)
        mid = ((xs.min() + xs.max()) / 2, ys.max())
        at = (int(round(PAD + RING_MID[0] - mid[0])), int(round(TOP + RING_MID[1] - 6 - mid[1])))
    else:
        x0, x1, ym = ring_of(g)
        at = (int(round(PAD + RING_MID[0] - (x0 + x1) / 2)), int(round(TOP + RING_MID[1] - ym)))
    place(can, g, at)
    return can, {"scale_px": round(size, 2), "at": at}, size


def palette(layers):
    allpx = np.concatenate([l[l[..., 3] > 0] for l in layers])
    rng = np.random.default_rng(0)
    sample = allpx[rng.choice(len(allpx), min(len(allpx), 60000), replace=False)]
    _, pal = dv.kmeans(sample.reshape(1, -1, 4), K)
    return np.asarray(pal, int)[:, :3]


def snap(l, pal):
    out = l.copy()
    op = out[..., 3] > 0
    px = out[op][:, :3].astype(int)
    out[op, :3] = pal[((px[:, None] - pal[None]) ** 2).sum(-1).argmin(1)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    d = DP.design()
    H, W = d.shape[0] + TOP + PAD, d.shape[1] + 2 * PAD
    J = json.load(open(JOINTS, encoding="utf-8"))
    PK.merge_tools(J, JOINTS)
    cranes, metas = {}, {}
    for name in PK.PROPS:
        cranes[name], metas[name] = crane(name, J, W, H)
    pal = palette(list(cranes.values()))
    for name, l in cranes.items():
        cranes[name] = snap(l, pal)
    gears = {}
    gears["gear_burst"], metas["gear_burst"], bs = gear("gear_burst", W, H)
    gears["gear_settle"], metas["gear_settle"], _ = gear("gear_settle", W, H)
    gears["gear_drum"], metas["gear_drum"], _ = gear("gear_drum", W, H, bs)
    gpal = palette(list(gears.values()))
    for name, l in gears.items():
        gears[name] = snap(l, gpal)
    for name, l in list(cranes.items()) + list(gears.items()):
        Image.fromarray(l).save(lp(os.path.join(HD, f"prop_{name}.png")))
        print(name, metas[name])
    with open(lp(os.path.join(HD, "props.json")), "w", encoding="utf-8") as f:
        json.dump({"origin": [PAD, TOP], "props": {k: {kk: (float(vv) if isinstance(vv, np.floating) else vv)
                                                          for kk, vv in v.items()} for k, v in metas.items()}}, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z = 3
        tiles = []
        for name, l in list(cranes.items()) + list(gears.items()):
            bg = Image.new("RGBA", (W, H), (96, 112, 96, 255))
            ghost = d.copy()
            ghost[..., :3] = (ghost[..., :3] * 0.3 + 140).astype(np.uint8)
            if name.startswith("crane"):
                bg.alpha_composite(Image.fromarray(l))
                bg.alpha_composite(Image.fromarray(ghost), (PAD, TOP))
            else:
                bg.alpha_composite(Image.fromarray(ghost), (PAD, TOP))
                bg.alpha_composite(Image.fromarray(l))
            tiles.append(bg.resize((W * Z, H * Z), Image.NEAREST))
        per = 5
        sheet = Image.new("RGB", (per * (W * Z + 6), ((len(tiles) + per - 1) // per) * (H * Z + 6)), (30, 30, 30))
        for i, t in enumerate(tiles):
            sheet.paste(t.convert("RGB"), ((i % per) * (W * Z + 6), (i // per) * (H * Z + 6)))
        sheet.save(os.path.join(a.review, "props_read.png"))
        print(os.path.join(a.review, "props_read.png"), sheet.size)


if __name__ == "__main__":
    main()
