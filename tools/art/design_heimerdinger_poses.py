#!/usr/bin/env python3
"""Heimerdinger's 15 body poses from Codex (pack A, assets/source/heimerdinger/codex_poses, 2026-10-21) read back at the
design's own square size, his design head pasted back (one face in every frame) and placed where League's frame puts
him (pack_heimerdinger_poses.place).

    python tools/art/design_heimerdinger_poses.py [--review DIR]   # writes assets/source/heimerdinger/hd/pose_<name>.png

Codex drew every pose at its own square size (12 to 14.3 px; asked 12: its HANDOFF admits the drift), so each is read at
its own: the two goggle lenses (the two biggest cyan blobs) are 9.9 design squares apart on hd/idle.png, which gives the
picture's px a square; regrid reads it there (alpha >= 128). The design's head (hd/idle.png rows above HEAD_ROWS, the
tools left out) goes back on by the lenses' middle; Codex's own head under it is cleared first (its squares inside the
design head's outline grown by two, above the moustache's last row). Lying down (death3) the design head is laid a
quarter turn (lossless) like him; death2, tipping over, keeps Codex's own head (a 45-degree head has no lossless form).
The colours are brought to the design's palette where one is near (Lab distance), Codex's own elsewhere (the crane and
the engine in the deaths). Each pose's place: its pasted lenses where the design's lenses sit moved by League's neck
(place()'s neck minus REST's), so the run's hops and the attack's lunge are League's.
Writes hd/pose_<name>.png at the design's squares on a canvas the design's size plus PAD all round (the design's (0, 0)
at (PAD, PAD)), and pose_<name>.json (the lens middle, the scale read).
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
import design_varus as dv  # noqa: E402
import pack_heimerdinger_poses as PK  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heimerdinger", "codex_poses", "raw")
HD = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd")
LENSES = ((26.0, 25.0), (35.9, 25.2))      # the design's two lens middles (hd/idle.png squares)
LENS_GAP = LENSES[1][0] - LENSES[0][0]
PAD = 40
OWN_HEAD = {"death2"}                      # tipping over at 45 degrees: Codex's head kept
LAID = {"death3": 1}                       # lying: the design head turned this many quarter turns counter-clockwise
# Codex's leftovers erased (x0, y0, x1, y1 on the written canvas, ends exclusive): death1's own monocle above the pasted
# head's; death2's rocket in his near hand (its HANDOFF: 「近侧手里的道具被误画成火箭」 - the flying one stays)
ERASE = {"death1": [(83, 44, 94, 51)], "death2": [(3, 27, 27, 56)]}
JOINTS = "C:/t/hd_work/joints/heimerdinger_joints.json"


def lp(path):
    return PK.lp(path)


def lenses(rgb, op):
    """The two lens blobs' middles (x, y) in the picture, left one first, or None."""
    cy = (rgb[..., 2] > 170) & (rgb[..., 1] > 150) & (rgb[..., 0] < 140) & op
    lbl, n = ndimage.label(cy)
    if n < 2:
        return None
    sizes = ndimage.sum(cy, lbl, range(1, n + 1))
    best = np.argsort(sizes)[::-1][:2] + 1
    pts = [tuple(np.array(ndimage.center_of_mass(cy, lbl, int(i)))[::-1]) for i in best]
    return sorted(pts)


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA")).copy()


def head_layer(d):
    P = PK.pieces(d)
    return P["head"]


def read(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"heimerdinger-pose-{name}.png"))).convert("RGBA")).copy()
    op = a[..., 3] >= 128
    L = lenses(a[..., :3].astype(int), op)
    gap = np.hypot(L[1][0] - L[0][0], L[1][1] - L[0][1])
    size = gap / LENS_GAP
    g, bx, by = regrid_at(a, size)
    mid = ((L[0][0] + L[1][0]) / 2, (L[0][1] + L[1][1]) / 2)
    return g, (to_sq(bx, mid[0]), to_sq(by, mid[1])), size, L


def to_sq(bounds, v):
    """A picture coordinate in squares of the read (bounds: the squares' edges)."""
    i = int(np.clip(np.searchsorted(bounds, v, side="right") - 1, 0, len(bounds) - 2))
    return i + (v - bounds[i]) / max(1, bounds[i + 1] - bounds[i])


def regrid_at(a, size):
    """regrid's read at `size` px a square, not cropped: (squares, column edges, row edges)."""
    import regrid as RG
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    ex, ey = RG.profile(a, op, 1), RG.profile(a, op, 0)
    bx = RG.boundaries(ex, xs.min(), xs.max(), size)
    by = RG.boundaries(ey, ys.min(), ys.max(), size)
    H, W = len(by) - 1, len(bx) - 1
    out = np.zeros((H, W, 4), np.uint8)
    for j in range(H):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(W):
            cx = (bx[i] + bx[i + 1]) // 2
            win = a[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            if (win[:, 3] >= 128).sum() * 2 > len(win):
                px = win[win[:, 3] >= 128][:, :3]
                out[j, i, :3] = np.median(px, axis=0).astype(np.uint8)
                out[j, i, 3] = 255
    return out, np.asarray(bx, float), np.asarray(by, float)


def palette_snap(img, pal, max_d=18.0):
    """Every drawn square to the nearest design colour when it is within max_d (Lab), else kept."""
    op = img[..., 3] > 0
    px = img[op][:, :3]
    lab = np.array([dv.srgb2lab(c) for c in px], float).reshape(-1, 3)
    plab = np.array([dv.srgb2lab(c) for c in pal], float).reshape(-1, 3)
    d2 = ((lab[:, None, :] - plab[None]) ** 2).sum(-1)
    k = d2.argmin(1)
    near = np.sqrt(d2[np.arange(len(k)), k]) <= max_d
    out = img.copy()
    sub = out[op]
    sub[near, :3] = pal[k[near]]
    out[op] = sub
    return out


def build(name, d, head, pal, J):
    g, mid_sq, size, L = read(name)
    tag, ms, bounce, _ = PK.BODY[name]
    neck, _, _, _ = PK.place(PK.row(J, tag, ms)["j"], J["design"], bounce)
    dn = (neck[0] - PK.REST["neck"][0], neck[1] - PK.REST["neck"][1])
    dmid = ((LENSES[0][0] + LENSES[1][0]) / 2, (LENSES[0][1] + LENSES[1][1]) / 2)
    H, W = d.shape[0] + 2 * PAD, d.shape[1] + 2 * PAD
    can = np.zeros((H, W, 4), np.uint8)
    # Codex's picture placed so its lens middle lands on the design's lens middle moved by League's neck
    tx, ty = PAD + dmid[0] + dn[0] - mid_sq[0], PAD + dmid[1] + dn[1] - mid_sq[1]
    tx, ty = int(round(tx)), int(round(ty))
    ys, xs = np.nonzero(g[..., 3] > 0)
    ok = (ys + ty >= 0) & (ys + ty < H) & (xs + tx >= 0) & (xs + tx < W)
    can[ys[ok] + ty, xs[ok] + tx] = g[ys[ok], xs[ok]]
    can = palette_snap(can, pal)
    if name not in OWN_HEAD:
        k = LAID.get(name, 0)
        hl = np.rot90(head, k).copy() if k else head
        hl_mask = hl[..., 3] > 0
        hh, hw = hl.shape[:2]
        # the design's lens middle in the (turned) head layer: np.rot90 once takes (x, y) to (y, W - 1 - x)
        cx, cy = dmid
        for _ in range(k):
            cx, cy = cy, head.shape[1] - 1 - cx
        at = (int(round(PAD + dmid[0] + dn[0] - cx)), int(round(PAD + dmid[1] + dn[1] - cy)))
        big = np.zeros((H, W), bool)
        hy, hx = np.nonzero(hl_mask)
        okh = (hy + at[1] >= 0) & (hy + at[1] < H) & (hx + at[0] >= 0) & (hx + at[0] < W)
        big[hy[okh] + at[1], hx[okh] + at[0]] = True
        grow = ndimage.binary_dilation(big, iterations=2)
        if not k:
            grow[at[1] + hh - 1:] = False    # nothing cleared below the moustache's last row
        can[grow] = 0
        can[hy[okh] + at[1], hx[okh] + at[0]] = hl[hy[okh], hx[okh]]
    for x0, y0, x1, y1 in ERASE.get(name, ()):
        can[y0:y1, x0:x1] = 0
    return can, {"scale_px": round(size, 2), "lenses_px": [list(map(float, p)) for p in L], "neck_shift": dn}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    d = design()
    head = head_layer(d)
    op = d[..., 3] > 0
    pal = np.unique(d[op][:, :3], axis=0)
    J = json.load(open(JOINTS, encoding="utf-8"))
    PK.merge_tools(J, JOINTS)
    out = {}
    for name in PK.BODY:
        can, meta = build(name, d, head, pal, J)
        Image.fromarray(can).save(lp(os.path.join(HD, f"pose_{name}.png")))
        with open(lp(os.path.join(HD, f"pose_{name}.json")), "w", encoding="utf-8") as f:
            json.dump(meta, f)
        out[name] = can
        print(name, meta["scale_px"])
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z = 4
        tiles = []
        for name, can in out.items():
            ys, xs = np.nonzero(can[..., 3] > 0)
            sub = can[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
            bg = Image.new("RGBA", (sub.shape[1] * Z, sub.shape[0] * Z), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(sub).resize((sub.shape[1] * Z, sub.shape[0] * Z), Image.NEAREST))
            tiles.append(bg)
        W = sum(t.width + 8 for t in tiles[:8])
        H = max(t.height for t in tiles) * 2 + 8
        sheet = Image.new("RGB", (max(W, sum(t.width + 8 for t in tiles[8:])), H), (40, 40, 40))
        x = 0
        for i, t in enumerate(tiles):
            if i == 8:
                x = 0
            sheet.paste(t.convert("RGB"), (x, 0 if i < 8 else H // 2 + 4))
            x += t.width + 8
        sheet.save(os.path.join(a.review, "poses_read.png"))
        print(os.path.join(a.review, "poses_read.png"))


if __name__ == "__main__":
    main()
