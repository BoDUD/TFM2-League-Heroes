#!/usr/bin/env python3
"""The two fix deliveries of tools/art/pack_fix_1018.py read back into assets/source/<hero>/hd/act/:

- akshan: idle_0..4 and skill1_0..4 with the gun in the front hand (Codex's raw generations; its exports were not put on
  one grid). Each sheet read on its own square size = the figure's height in the raw / the old frame's height in squares
  (70: the other actions' density), so the new frames match the walk and attack square for square.
- wukong: spin_0..7 (R Cyclone) from the 4 x 2 delivery.

    python tools/art/import_fix_1018.py akshan|wukong

Colours snapped to the hero's other action frames (their union palette); key fringe, crumbs and eye specks as in
import_swap_1018.py.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402

DELIV = {"akshan": "C:/Users/OWNER/Documents/Codex/2026-10-18/new-chat-15/outputs/akshan-gunhand",
         "wukong": "C:/Users/OWNER/Documents/Codex/2026-10-18/new-chat-16/outputs/wukong-spin"}
JOBS = {"akshan": [("raw/akshan-idle-generated.png", "idle", 5, 70), ("raw/akshan-skill1-generated.png", "skill1", 5, 70)],
        "wukong": [(None, "spin", 8, None)]}
EYE = {"wukong": (70, 215, 90)}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def keyed(a):
    return (a[..., 1] > 170) & (a[..., 1] - np.maximum(a[..., 0], a[..., 2]) > 90)


def figures(a, n):
    key = keyed(a)
    lbl, k = ndimage.label(ndimage.binary_closing(~key, iterations=3))
    sz = ndimage.sum(~key, lbl, range(1, k + 1))
    boxes = []
    for j in [j + 1 for j, s in enumerate(sz) if s > 5000]:
        ys, xs = np.nonzero(lbl == j)
        boxes.append((ys.min(), ys.max(), xs.min(), xs.max()))
    rowh = a.shape[0] // 2
    boxes.sort(key=lambda b: (b[0] // rowh, b[2]))
    if len(boxes) != n:
        raise SystemExit(f"{len(boxes)} figures, not {n}")
    return [np.dstack([a[y0:y1 + 1, x0:x1 + 1], np.where(~key[y0:y1 + 1, x0:x1 + 1], 255, 0)]).astype(np.uint8)
            for y0, y1, x0, x1 in boxes]


def palette(act):
    cols = [np.asarray(Image.open(lp(os.path.join(act, f))).convert("RGBA")) for f in os.listdir(lp(act))]
    px = np.concatenate([c[c[..., 3] > 0][:, :3] for c in cols])
    return np.unique(px, axis=0).astype(int)


def clean(d, pal, eye):
    d = d.astype(np.int64)
    op = d[..., 3] >= 128
    op &= ~((d[..., 1] - np.maximum(d[..., 0], d[..., 2])) > 60) if eye is None else op
    holes = ndimage.binary_fill_holes(op) & ~op
    hl, hn = ndimage.label(holes)
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    eyes = np.isin(hl, [j + 1 for j, z in enumerate(hs) if z <= 2])
    px = d[op][:, :3]
    d[op, :3] = pal[np.argmin(((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1), 1)]
    if eyes.any():
        if eye is not None:
            d[eyes, :3] = eye
        else:
            d[eyes, :3] = pal[np.argmin(pal.sum(1))]
        op |= eyes
    lbl, k = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lbl, range(1, k + 1))
    for j, z in enumerate(sizes):
        if z <= 3:
            op[lbl == j + 1] = False
    d[..., 3] = np.where(op, 255, 0)
    d[~op] = 0
    ys, xs = np.nonzero(op)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero", choices=list(DELIV))
    a = ap.parse_args()
    act = os.path.join(ROOT, "assets", "source", a.hero, "hd", "act")
    pal = palette(act)
    for src, tag, n, rows in JOBS[a.hero]:
        if src is None:                                  # the spin: Codex's 4 x 2 export on 5 px squares
            from import_swap_1018 import cells
            fr = [f for f, _ in cells(os.path.join(DELIV[a.hero], f"{a.hero}-{tag}.png"), n, EYE.get(a.hero))]
        else:
            img = np.asarray(Image.open(os.path.join(DELIV[a.hero], src)).convert("RGB")).astype(int)
            figs = figures(img, n)
            size = (figs[0].shape[0]) / rows
            fr = [clean(RG.regrid(f, size)[0], pal, EYE.get(a.hero)) for f in figs]
            print(f"{tag}: {size:.2f} px a square")
        for i, f in enumerate(fr):
            Image.fromarray(f).save(lp(os.path.join(act, f"{tag}_{i}.png")))
        print(tag, [f.shape[:2] for f in fr])


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
