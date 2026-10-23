#!/usr/bin/env python3
"""Jinx's dense (PPU 2.2) design: the user's own pixel picture read back on its grid, Fishbones added on her back.

    python tools/art/design_jinx_hd.py [--review DIR]                    # hd/design.png (+ the size check)
    python tools/art/design_jinx_hd.py --fishbones RENDER.png            # hd/fishbones.png again from a League render
    python tools/art/design_jinx_hd.py --held RENDER.png                 # hd/fishbones_held.png (shouldered) again

The user, 2026-10-23, with a 2000-px picture of their own (hd/raw/jinx_user.jpg: a grey JPEG, Jinx in profile facing
right, Pow-Pow at her hip, no Fishbones): 「你用PPU处理一下这能用吗」, then 「不换角度了 PPU可以调高点」 (the side view kept,
the denser grid) and 「设计图和 PPU 2.2 通过，开始做动作」.

- The grey ground (223 +- 16 on every channel) goes where it touches the border or fills a pocket of more than 2000 px.
- The picture's squares: its edges sit on an 11.11-px grid (2000 / 180) and its drawing on every second one, 22.23 px
  (design_fiora_hd.grid: one fitted pitch and phase, the median of each square's middle half): 82 rows from her hair's
  top to her soles, 37.3 px at PPU 2.2 - her 1x sprite's 37. The colours cut to 48 by k-means in Lab (design_varus).
- Fishbones (「得画鱼骨头吧？」): hd/fishbones.png, drawn on these squares from League's launcher alone (pose_ref.py
  --only-joints Rocket_Launcher, Jinx_minigun_idle1@0, yaw 80, pitch 15, head 2 legs 0.8 hair 0.5, --fit-all, 82 squares
  for the 549 render px from her hair's top to her soles): each square's material by hue (the indigo hide in four shades
  by value, the brass strap in three, the red war paint, the near-black neck band and mouth, the orange eye), a third of
  a square enough for the eye, the paint and the band, the teeth and the hull's holes set by hand (FEATURES), one
  outline square round it. It hangs BEHIND everything at FISHBONES_AT, filling only empty squares: the shark's head up
  beside the back of her head, the braids over its hull (the first paste over the braid and the hair: 「穿模了吧」).
- POCKETS: the grey ground left in gaps too small for the key (under the near arm, round the zapper) cleared.
- Speckle: palette entries nearer than MERGE merged (the commoner kept), then a square with no same-coloured neighbour
  takes its commonest near-tone (< NEAR) neighbour's colour - the JPEG's and k-means' noise; the eyes' glints, the
  buttons and the teeth have no near-tone neighbour and stay.
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
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "jinx", "hd")
RAW = os.path.join(HD, "raw", "jinx_user.jpg")
GREY, KEY, POCKET = 223, 16, 2000
PITCH = (22.1, 22.4)
COLOURS = 48
FISHBONES_AT = (-6, 3)          # the launcher's top-left square on the read-back picture's squares
LEFT = 8                        # columns added on the left for its tail
MERGE, NEAR = 30, 60
# the picture's grey ground left in gaps too small for the key (light grey squares): under the near arm, round the zapper
POCKETS = [(36, 37), (36, 38), (37, 38), (29, 52), (30, 51), (30, 52), (30, 59), (31, 60), (31, 61), (33, 60)]
PEERS = ["jinx", "caitlyn", "varus", "riven"]

# Fishbones from a League render: squares per render px and the hand-set features (square of the layer, 1-based
# inside its outline ring)
FB_K = 82 / 549.0
INDIGO = [(0x2D, 0x2A, 0x5E), (0x45, 0x43, 0x8E), (0x5E, 0x5F, 0xB8), (0x84, 0x87, 0xDE)]
BRASS = [(0x4A, 0x30, 0x20), (0x80, 0x56, 0x2C), (0xC9, 0x94, 0x36)]
RED, DARK, EYE = (0x8E, 0x22, 0x33), (0x20, 0x1C, 0x27), (0xF2, 0xA3, 0x3A)
TOOTH, FB_OUT = (0xD8, 0xDA, 0xF2), (0x1A, 0x14, 0x20)
FEATURES = {"teeth": [(28, 10), (27, 12), (26, 13), (28, 11)], "holes": [(9, 25), (12, 23), (10, 28)]}


def lp(path):
    return FD.lp(path)


def keyed():
    a = np.asarray(Image.open(lp(RAW)).convert("RGB")).astype(int)
    g = np.abs(a - GREY).max(axis=2) < KEY
    lab, n = ndimage.label(g)
    sizes = ndimage.sum(g, lab, range(1, n + 1))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, [i for i, s in enumerate(sizes, 1) if i in border or s > POCKET])
    out = np.zeros(a.shape[:2] + (4,), np.uint8)
    out[..., :3] = a
    out[..., 3] = np.where(bg, 0, 255)
    return out


def read():
    FD.PITCH = PITCH
    d, size = FD.grid(keyed())
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out, size


def fishbones_from(render):
    """League's launcher (a pose_ref.py render on a 225-grey ground) on the design's squares."""
    im = Image.open(render).convert("RGB")
    fb = np.asarray(im).astype(float)
    m = np.abs(fb - 225).max(axis=2) > 10
    hsv = np.asarray(im.convert("HSV")).astype(float)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    pal = INDIGO + BRASS + [RED, None, DARK, EYE]                     # 8: unused (pale glints take the light indigo)
    lab = np.full(m.shape, -1)
    ind = m & (s > 0.2) & (h > 180) & (h < 310) & (v >= 0.25)
    lab[ind] = np.digitize(v[ind], [0.42, 0.6, 0.8])
    br = m & (s > 0.35) & (h >= 15) & (h <= 55)
    lab[br] = 4 + np.digitize(v[br], [0.45, 0.72])
    lab[m & (s > 0.4) & ((h > 330) | (h < 15))] = 7
    lab[m & (s < 0.3) & (v > 0.6)] = 3
    dk = m & (lab < 0)
    lab[dk] = np.where(v[dk] < 0.45, 9, 1)
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max(), xs.max()
    lab[br & (v > 0.8) & (s > 0.6) & (np.arange(m.shape[0])[:, None] < y0 + 0.3 * (y1 - y0))] = 10
    step = 1 / FB_K
    nh, nw = int(np.ceil((y1 - y0 + 1) * FB_K)), int(np.ceil((x1 - x0 + 1) * FB_K))
    out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
    for j in range(nh):
        for i in range(nw):
            a, b = int(round(y0 + j * step)), int(round(x0 + i * step))
            w = lab[a:int(round(y0 + (j + 1) * step)), b:int(round(x0 + (i + 1) * step))].ravel()
            if (w >= 0).mean() <= 0.5:
                continue
            w = w[w >= 0]
            cnt = np.bincount(w, minlength=len(pal))
            for keep, part in ((10, 5), (8, 4), (7, 3), (9, 3)):         # small features win with a part of a square
                if cnt[keep] * part >= len(w):
                    c = keep
                    break
            else:
                c = cnt.argmax()
            out[j + 1, i + 1, :3] = pal[c]
            out[j + 1, i + 1, 3] = 255
    op = out[..., 3] > 0
    ring = ndimage.binary_dilation(op, structure=FD_CROSS) & ~op
    out[ring, :3] = FB_OUT
    out[ring, 3] = 255
    for x, y in FEATURES["teeth"]:
        out[y, x, :3] = TOOTH
    for x, y in FEATURES["holes"]:
        out[y, x, :3] = DARK
    return out


TUBE = [(0x1E, 0x2C, 0x30), (0x2E, 0x44, 0x48), (0x45, 0x63, 0x64)]


def fishbones_held(render):
    """Fishbones shouldered (League's Jinx_Rlauncher_attack1@0, the launcher alone, the same camera and scale): drawn
    the same way plus its dark teal tube in three shades and the open mouth's teeth (white by value) - the picture the
    rocket attack and the ult hold."""
    im = Image.open(render).convert("RGB")
    fb = np.asarray(im).astype(float)
    m = np.abs(fb - 225).max(axis=2) > 10
    hsv = np.asarray(im.convert("HSV")).astype(float)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    pal = INDIGO + BRASS + [RED, TOOTH, DARK, EYE] + TUBE
    lab = np.full(m.shape, -1)
    ind = m & (s > 0.2) & (h > 200) & (h < 310) & (v >= 0.25)
    lab[ind] = np.digitize(v[ind], [0.42, 0.6, 0.8])
    tube = m & (s > 0.1) & (h >= 110) & (h <= 205) & (lab < 0)
    lab[tube] = 11 + np.digitize(v[tube], [0.17, 0.27])
    br = m & (s > 0.35) & (h >= 15) & (h <= 55)
    lab[br] = 4 + np.digitize(v[br], [0.45, 0.72])
    lab[m & (s > 0.4) & ((h > 330) | (h < 15))] = 7
    lab[m & (s < 0.3) & (v > 0.62)] = 8
    dk = m & (lab < 0)
    lab[dk] = np.where(v[dk] < 0.45, 9, 1)
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max(), xs.max()
    lab[br & (v > 0.8) & (s > 0.6) & (np.arange(m.shape[1])[None, :] > x0 + 0.75 * (x1 - x0))] = 10
    step = 1 / FB_K
    nh, nw = int(np.ceil((y1 - y0 + 1) * FB_K)), int(np.ceil((x1 - x0 + 1) * FB_K))
    out = np.zeros((nh + 2, nw + 2, 4), np.uint8)
    for j in range(nh):
        for i in range(nw):
            a, b = int(round(y0 + j * step)), int(round(x0 + i * step))
            w = lab[a:int(round(y0 + (j + 1) * step)), b:int(round(x0 + (i + 1) * step))].ravel()
            if (w >= 0).mean() <= 0.5:
                continue
            w = w[w >= 0]
            cnt = np.bincount(w, minlength=len(pal))
            for keep, part in ((10, 5), (8, 3), (7, 3), (9, 3)):
                if cnt[keep] * part >= len(w):
                    c = keep
                    break
            else:
                c = cnt.argmax()
            out[j + 1, i + 1, :3] = pal[c]
            out[j + 1, i + 1, 3] = 255
    op = out[..., 3] > 0
    ring = ndimage.binary_dilation(op, structure=FD_CROSS) & ~op
    out[ring, :3] = FB_OUT
    out[ring, 3] = 255
    return out


FD_CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def with_fishbones(d, fb):
    """The launcher behind the figure: on empty squares only, the canvas widened LEFT columns, cropped to the figure."""
    H, W = d.shape[:2]
    out = np.zeros((H, W + LEFT, 4), np.uint8)
    out[:, LEFT:] = d
    x0, y0 = FISHBONES_AT[0] + LEFT, FISHBONES_AT[1]
    ys, xs = np.nonzero(fb[..., 3] > 0)
    Y, X = ys + y0, xs + x0
    ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W + LEFT)
    Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
    free = out[Y, X, 3] == 0
    out[Y[free], X[free]] = fb[ys[free], xs[free]]
    cols = np.nonzero(out[..., 3].any(0))[0]
    return out[:, cols.min():cols.max() + 1].copy()


def clean(d):
    a = d[..., 3] > 0
    rgb = d[..., :3].astype(int)
    H, W = a.shape
    cols, cnt = np.unique(rgb[a], axis=0, return_counts=True)
    keep, remap = [], {}
    for c in cols[np.argsort(-cnt, kind="stable")]:
        for k in keep:
            if np.abs(k - c).sum() < MERGE:
                remap[tuple(c)] = tuple(k)
                break
        else:
            keep.append(c)
            remap[tuple(c)] = tuple(c)
    for y, x in zip(*np.nonzero(a)):
        rgb[y, x] = remap[tuple(rgb[y, x])]
    for _ in range(2):
        new = rgb.copy()
        for y, x in zip(*np.nonzero(a)):
            nb = [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx)
                  and 0 <= y + dy < H and 0 <= x + dx < W and a[y + dy, x + dx]]
            if not nb or any((rgb[p] == rgb[y, x]).all() for p in nb):
                continue
            near = [tuple(rgb[p]) for p in nb if np.abs(rgb[p] - rgb[y, x]).sum() < NEAR]
            if near:
                new[y, x] = max(sorted(set(near)), key=near.count)
        rgb = new
    out = np.zeros_like(d)
    out[..., :3] = rgb
    out[..., 3] = a * 255
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fishbones", help="a pose_ref.py render of the launcher alone: hd/fishbones.png again from it")
    ap.add_argument("--held", help="a pose_ref.py render of the launcher shouldered: hd/fishbones_held.png again")
    ap.add_argument("--review")
    a = ap.parse_args()
    if a.held:
        Image.fromarray(fishbones_held(a.held)).save(lp(os.path.join(HD, "fishbones_held.png")))
        return
    if a.fishbones:
        Image.fromarray(fishbones_from(a.fishbones)).save(lp(os.path.join(HD, "fishbones.png")))
    d, size = read()
    fb = np.asarray(Image.open(lp(os.path.join(HD, "fishbones.png"))).convert("RGBA"))
    d = clean(with_fishbones(d, fb))
    for x, y in POCKETS:
        d[y, x] = 0
    Image.fromarray(d).save(lp(os.path.join(HD, "design.png")))
    print(f"square {size[0]:.2f} x {size[1]:.2f}, design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    im = Image.fromarray(d)
    cells = [(f"new 2.2: {d.shape[0] / 2.2:.1f}px", FD.shown(im, 2.2, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == "jinx" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "jinx_ppu_size.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
