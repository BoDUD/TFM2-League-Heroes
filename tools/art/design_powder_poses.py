#!/usr/bin/env python3
"""Powder's pose pack read back (assets/source/powder/codex_poses, 2026-10-19, Codex new-chat-6; the pack:
tools/art/pack_powder_poses.py): the clean head, the seven action poses and the eight run frames, on the design's grid
and palette.

    python tools/art/design_powder_poses.py [--review DIR]   # writes assets/source/powder/hd/head.png, poses/*.png

The head (powder-head.png, 1387 x 1134 = 33 x 27 squares of 42 px): read back at 42 px; only the squares the fist hid
(pack_powder_poses.HAND_SQ) are taken from it, every other square stays the idle's own (Codex redrew the rest a little).
The poses and the run (1509 x 1042): each figure is a connected piece on the green (the green varies: keyed by hue;
the green fringe at the outline turned into the outline). Codex drew its heads smaller and its bodies longer than the
design (the run's head 34% of the height, the idle's 40%) and the two sheets at different sizes (heads ~168 px on the
poses, ~141 on the run), so each figure is brought down by votes (pixel_down.pixelate) until its chin-to-sole is the
idle's 32 rows (chin row 20, soles row 52), and the clean head (21 rows, hd/head.png rows 0-20, no braids) goes on its
chin: 53 rows standing, the one face in every frame (one-face-all-frames). Colours snapped to the designs' palette plus
the far tights' blue-violet Codex used (FAR_TIGHTS).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
import pixel_down as PD  # noqa: E402
from pack_powder_poses import HAND_SQ, HEAD_ROWS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "powder", "codex_poses", "powder-poses")
HD = os.path.join(ROOT, "assets", "source", "powder", "hd")
OUT = os.path.join(HD, "poses")
HEAD_PX = 42.0
SQ = 1509 / 1358 * 7          # 7.78 px a square on the pose and run sheets
POSES = ["wind", "throw", "crouch", "toss", "slam", "hop", "hit"]   # the guide's cells, left to right, top to bottom
CELL = (1358 // 4, 938 // 2)  # a guide cell with its gap, in guide pixels (4 x 2 cells)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


FAR_TIGHTS = [(74, 53, 184), (46, 35, 128)]
CHIN_ROW, BODY_ROWS = 20, 32           # the idle: the chin's outline row, chin to the soles' row
HEAD_CHIN = (15.5, 20.0)               # the chin's point in hd/head.png


def palette():
    cols = set(FAR_TIGHTS)
    for n in ("idle.png", "side.png"):
        a = load(os.path.join(HD, n))
        for c in a[a[..., 3] > 0][:, :3]:
            cols.add(tuple(int(v) for v in c))
    return np.array(sorted(cols), int)


def snap(a, pal):
    out = a.copy()
    op = a[..., 3] > 0
    px = a[op][:, :3].astype(int)
    # nearest in a lightness-weighted RGB (keeps the near-black outline from turning into dark blue hair)
    w = np.array([0.30, 0.59, 0.11]) * 3
    d = (((px[:, None, :] - pal[None]) ** 2) * w).sum(-1)
    out[op, :3] = pal[d.argmin(1)]
    out[..., 3] = np.where(op, 255, 0)
    return out


def head():
    """The idle's head with the chin squares Codex drew where the fist was."""
    idle = load(os.path.join(HD, "idle.png"))
    h, sq, _ = RG.regrid(load(os.path.join(SRC, "powder-head.png")), HEAD_PX)
    h = h[:HEAD_ROWS, :idle.shape[1]]
    out = idle[:HEAD_ROWS].copy()
    for r, c0, c1 in HAND_SQ:
        out[r, c0:c1 + 1] = h[r, c0:c1 + 1]
    return out


def figures(name):
    """The figures of a sheet in reading order: (cell index, RGBA crop keyed from the green)."""
    s = load(os.path.join(SRC, name))
    rgb = s[..., :3].astype(int)
    green = (rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2]) > 60) & (rgb[..., 1] > 140)
    fg = ndimage.binary_opening(~green, np.ones((3, 3), bool))
    lbl, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lbl, range(1, n + 1))
    out = []
    k = s.shape[1] / 1358
    for i, o in enumerate(ndimage.find_objects(lbl)):
        if sizes[i] < 5000:
            continue
        cy, cx = (o[0].start + o[0].stop) / 2, (o[1].start + o[1].stop) / 2
        cell = int(cy // (CELL[1] * k)) * 4 + int(cx // (CELL[0] * k))
        a = np.zeros((o[0].stop - o[0].start, o[1].stop - o[1].start, 4), np.uint8)
        a[..., :3] = s[o][..., :3]
        a[..., 3] = np.where(lbl[o] == i + 1, 255, 0)
        out.append((cell, a))
    return sorted(out, key=lambda t: t[0])


NATIVE = {"powder-poses.png": 7.0, "powder-run.png": 6.0}   # Codex's own squares (both heads ~24 rows at these)


def face(a):
    """(chin y, face middle x) of a figure: the skin piece touching the most blue hair (the face; hands and knees
    touch none)."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] > 0
    skin = op & (rgb[..., 0] > 215) & (rgb[..., 1] > 150) & (rgb[..., 2] > 120) & (rgb[..., 0] - rgb[..., 2] > 25)
    hair = op & (rgb[..., 2] > 150) & (rgb[..., 0] < 90)
    lbl, n = ndimage.label(skin)
    best = None
    for i, o in enumerate(ndimage.find_objects(lbl)):
        m = lbl == i + 1
        touch = int((ndimage.binary_dilation(m, np.ones((3, 3), bool), iterations=2) & hair).sum())
        if best is None or touch > best[0]:
            best = (touch, o)
    o = best[1]
    return o[0].stop, (o[1].start + o[1].stop) / 2


def despill(a):
    """The green Codex left round the outline -> the outline's near-black."""
    out = a.copy()
    rgb = a[..., :3].astype(int)
    spill = (a[..., 3] > 0) & (rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2]) > 20)
    out[spill, :3] = (8, 1, 16)
    return out


def mode_down(d, k, pivot):
    """d (one pixel a square) brought to k times the squares a side (k < 1), each new square the commonest colour of
    the squares whose centres fall in it (clear where most of them are clear): no averaged colours."""
    H, W = d.shape[:2]
    c = 1.0 / k
    px, py = pivot
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    Wn, Hn = nx0 + int(np.ceil((W - px) / c)), ny0 + int(np.ceil((H - py) / c))
    cx = np.floor((np.arange(W) + 0.5 - px) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - py) / c).astype(int) + ny0
    out = np.zeros((Hn, Wn, 4), np.uint8)
    buckets = {}
    for y in range(H):
        for x in range(W):
            buckets.setdefault((cy[y], cx[x]), []).append(tuple(int(v) for v in d[y, x]))
    for (y, x), px_ in buckets.items():
        op = [p for p in px_ if p[3] > 0]
        if len(op) * 2 < len(px_):
            continue
        cols = {}
        for p in op:
            cols[p] = cols.get(p, 0) + 1
        out[y, x] = max(cols, key=lambda q: (cols[q], -sum(q[:3])))   # ties: the darker (outlines hold)
    return out, (nx0, ny0)


STANDING = ["wind", "throw", "toss", "hit"]     # the poses whose chin-to-sole sets the poses sheet's scale


FAR_TO = {(74, 53, 184): (184, 55, 134), (46, 35, 128): (114, 21, 80)}   # the far leg: the tights' own darker pinks


def native(a, pal, size):
    d, _, _ = RG.regrid(despill(a), size)
    d = d.copy()
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = snap(d, pal)
    for src, dst in FAR_TO.items():
        d[(d[..., :3] == src).all(-1), :3] = dst
    return d


def scale_of(d):
    chin, _ = face(d)
    sole = np.nonzero((d[..., 3] > 0).any(1))[0][-1] + 1
    return BODY_ROWS / max(1, sole - chin)


def drop_head(d, chin):
    """Codex's own head taken off: the blue hair, the face, the gold clips and braid ties touching them, and the outline
    round them - above the chin only (the neck, the arms and the collar touch the face but stay)."""
    rgb = d[..., :3].astype(int)
    op = d[..., 3] > 0
    hair = op & (rgb[..., 2] > 150) & (rgb[..., 0] < 90)
    lbl, n = ndimage.label(hair, np.ones((3, 3), bool))
    if n == 0:
        return d
    sizes = ndimage.sum(hair, lbl, range(1, n + 1))
    keep = lbl == (int(np.argmax(sizes)) + 1)           # the head's hair mass (the bombs' blue are small pieces)
    skin = op & (rgb[..., 0] > 215) & (rgb[..., 1] > 150) & (rgb[..., 2] > 120) & (rgb[..., 0] - rgb[..., 2] > 25)
    gold = op & (rgb[..., 0] > 200) & (rgb[..., 1] > 150) & (rgb[..., 2] < 90)
    near = ndimage.binary_dilation(keep, np.ones((3, 3), bool), iterations=2)
    sl, _ = ndimage.label(skin)
    face_ids = set(np.unique(sl[near & skin])) - {0}
    head = keep | (np.isin(sl, list(face_ids))) | (gold & near)
    dark = op & (rgb.sum(-1) < 90)
    head |= ndimage.binary_dilation(head, np.ones((3, 3), bool)) & dark
    head[chin + 1:] = False
    out = d.copy()
    out[head] = 0
    return out


def read(d, k, hd):
    """A figure (read on Codex's grid) brought down by k, its own head swapped for the clean head on its chin."""
    chin, mid = face(d)
    d = drop_head(d, chin)
    d, (px, py) = mode_down(d, k, (mid, chin))
    core = hd[:CHIN_ROW + 1].copy()
    core[:, :, 3] = np.where(core[..., 3] > 0, 255, 0)
    dx, dy = int(round(px - HEAD_CHIN[0])), int(round(py - HEAD_CHIN[1]))
    pad = 30
    can = np.zeros((d.shape[0] + 2 * pad, d.shape[1] + 2 * pad, 4), np.uint8)
    can[pad:pad + d.shape[0], pad:pad + d.shape[1]] = d
    hy, hx = np.nonzero(core[..., 3])
    can[hy + dy + pad, hx + dx + pad] = core[hy, hx]
    lbl, n = ndimage.label(can[..., 3] > 0, np.ones((3, 3), bool))
    if n > 1:                                               # crumbs the head swap left floating (Codex's braid bits)
        sizes = ndimage.sum(can[..., 3] > 0, lbl, range(1, n + 1))
        for i, sz in enumerate(sizes, 1):
            if sz <= 14:
                can[lbl == i] = 0
    ys, xs = np.nonzero(can[..., 3])
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    pal = palette()
    hd = head()
    Image.fromarray(hd).save(lp(os.path.join(HD, "head.png")))
    got = {}
    poses = {POSES[c]: native(f, pal, NATIVE["powder-poses.png"]) for c, f in figures("powder-poses.png")}
    runs = {f"run{c + 1}": native(f, pal, NATIVE["powder-run.png"]) for c, f in figures("powder-run.png")}
    # one scale a sheet (crouched poses have a short chin-to-sole): the standing poses' mean, the run frames' mean
    kp = float(np.mean([scale_of(poses[n]) for n in STANDING]))
    kr = float(np.mean([scale_of(d) for d in runs.values()]))
    print(f"scale: poses {kp:.3f}, run {kr:.3f}")
    for n, d in poses.items():
        got[n] = read(d, kp, hd)
    for n, d in runs.items():
        got[n] = read(d, kr, hd)
    for name, d in got.items():
        Image.fromarray(d).save(lp(os.path.join(OUT, f"{name}.png")))
        print(name, d.shape[1], "x", d.shape[0])
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        z = 8
        items = [("head", hd)] + list(got.items())
        for row, names in enumerate((["head"] + POSES, [f"run{k}" for k in range(1, 9)])):
            cells = [dict(items)[n] for n in names if n in dict(items)]
            H = max(c.shape[0] for c in cells) * z
            W = sum(c.shape[1] * z + 16 for c in cells)
            sh = Image.new("RGBA", (W, H), (200, 205, 195, 255))
            x = 0
            for c in cells:
                sh.alpha_composite(Image.fromarray(np.repeat(np.repeat(c, z, 0), z, 1)), (x, H - c.shape[0] * z))
                x += c.shape[1] * z + 16
            sh.convert("RGB").save(os.path.join(a.review, f"readback_{row}.png"))


if __name__ == "__main__":
    main()
