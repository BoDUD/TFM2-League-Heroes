#!/usr/bin/env python3
"""Gangplank's walk feet (the user, 2026-10-18: 「船长走路脚还是有点变形的」): Codex redrew the boots in every frame of
tools/art/import_gangplank_legs.py's read-back at a different size and left key-green specks under the soles. The design's
own two boots (whole, lossless - memory xinzhao-ppu-session: the design's boots stamped whole on drawn legs) are put where
Codex drew each foot: its bottom row and middle column kept (a lifted foot stays lifted), the rear foot (left) the design's
rear boot, the front one its front boot; the trousers above stay Codex's.

    python tools/art/stamp_gangplank_boots.py      # rewrites assets/source/gangplank/hd/run_<k>.png in place

Run after import_gangplank_legs.py (it reads the frames that script writes).
"""
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "gangplank", "hd")
OUTLINE = (9, 1, 8)     # the design's outline colour (ppu_restyle reads the same)


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def brown(a):
    a = a.astype(int)
    return (a[..., 3] > 0) & (a[..., 0] > 60) & (a[..., 0] < 160) & (a[..., 1] > 30) & (a[..., 1] < 110) \
        & (a[..., 2] < 80) & (a[..., 0] > a[..., 2] + 25)


def greenish(a):
    a = a.astype(int)
    return (a[..., 3] > 0) & (a[..., 1] > a[..., 0] + 60) & (a[..., 1] > a[..., 2] + 60)


def trouser(a):
    a = a.astype(int)
    return (a[..., 3] > 0) & (a[..., 1] > a[..., 0] + 15) & (a[..., 2] > a[..., 0] + 5) & ~greenish(a)


def feet(a, rows=12):
    """[(x0, x1, y_bottom)] of the brown boot pieces in the bottom `rows`, left to right."""
    b = brown(a)
    b[:a.shape[0] - rows] = False
    lbl, n = ndimage.label(b, structure=np.ones((3, 3)))
    out = []
    for j in range(1, n + 1):
        ys, xs = np.nonzero(lbl == j)
        if len(ys) >= 8:
            out.append((xs.min(), xs.max(), ys.max()))
    merged = []                     # a boot's brown can come in two pieces (the cuff's shade and the boot): one foot
    for x0, x1, yb in sorted(out):
        if merged and x0 <= merged[-1][1] + 1:
            px0, px1, pyb = merged[-1]
            merged[-1] = (px0, max(px1, x1), max(pyb, yb))
        else:
            merged.append((x0, x1, yb))
    return merged


def purple(a):
    a = a.astype(int)
    return (a[..., 3] > 0) & (a[..., 2] > a[..., 1] + 20) & (a[..., 0] > a[..., 1])


def boot_sprites(d):
    """The design's rear and front boots: the non-trouser, non-coat squares 8-connected to each brown piece (the gold
    cuff, the brown, the outline round them) in the bottom rows."""
    out = []
    H = d.shape[0]
    for x0, x1, yb in feet(d):
        y0 = H - 10
        bx0, bx1 = max(0, x0 - 3), x1 + 4
        box = d[y0:yb + 2, bx0:bx1].copy()
        cand = (box[..., 3] > 0) & ~trouser(box) & ~purple(box)
        lbl, n = ndimage.label(cand, structure=np.ones((3, 3)))
        seed = brown(box) & cand
        keep = np.isin(lbl, np.unique(lbl[seed & (lbl > 0)]))
        box[~keep] = 0
        out.append((box, (x0 + x1) / 2 - bx0, yb - y0))
    return out


def bridge(big, ox, w, oy, sp, reach=8):
    """Air between the shin and a stamped boot's cuff: each column of the boot filled up to the leg above it (at most
    `reach` rows) with that column's nearest trouser colour (its outline squares kept as they are); the gap's outer
    columns closed with the outline."""
    m = sp[..., 3] > 0
    filled = []
    for c in range(w):
        rows = np.nonzero(m[:, c])[0]
        if not len(rows):
            continue
        top = oy + rows.min()
        x = ox + c
        y = top - 1
        while y >= 0 and big[y, x, 3] == 0 and top - y <= reach:
            y -= 1
        if y < 0 or top - y <= 1 or top - y > reach:
            continue
        col = None
        for yy in range(y, max(-1, y - 4), -1):
            if trouser(big[yy:yy + 1, x:x + 1])[0, 0]:
                col = big[yy, x].copy()
                break
        if col is None:
            continue
        big[y + 1:top, x] = col
        filled.append((x, y + 1, top))
    if filled:
        for x, y0, y1 in (filled[0], filled[-1]):
            big[y0:y1, x] = (*OUTLINE, 255)


def main():
    """Each foot where Codex drew it (so it stays on its trouser leg), matched to the guide's near / far leg by its
    column; the swinging foot's lower leg (shin and boot, the column band from KNEE rows over the bottom) lifted whole by
    the guide's lift (Codex kept it down - 「船长走路还有点怪 脚部」); then the design's boots stamped (far first, near over
    it, so the passing frames show two boots, never one block)."""
    import json
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA")).copy()
    rear, front = boot_sprites(d)
    g = json.load(open(lp(os.path.join(HD, "legs_guides.json")), encoding="utf-8"))
    offs = json.load(open(lp(os.path.join(HD, "run_offsets.json")), encoding="utf-8"))
    KNEE = 13
    for k in range(8):
        path = os.path.join(HD, f"run_{k}.png")
        f = np.asarray(Image.open(lp(path)).convert("RGBA")).copy()
        f[greenish(f)] = 0
        pad = 8
        big = np.zeros((f.shape[0] + 2 * pad, f.shape[1] + 2 * pad, 4), np.uint8)
        big[pad:pad + f.shape[0], pad:pad + f.shape[1]] = f
        H = f.shape[0] + pad                                       # the row under the soles
        ft = feet(big[:H])
        if len(ft) == 1:
            x0, x1, yb = ft[0]
            m = (x0 + x1) // 2
            ft = [(x0, m, yb), (m + 1, x1, yb)]
        ft = sorted(ft)[:1] + sorted(ft)[-1:]
        gx = {side: g["guides"][k][side][2][0] - offs[k][0] + pad for side in ("near", "far")}
        lift = {"near": g["guides"][k]["near"][2], "far": g["guides"][k]["far"][2]}
        lifts = {s_: round(g["SOLE"] - 2.5 - lift[s_][1]) for s_ in lift}          # squares
        # which detected foot is which leg: the pairing with the smaller column error
        a_, b_ = ft
        c1 = abs((a_[0] + a_[1]) / 2 - gx["far"]) + abs((b_[0] + b_[1]) / 2 - gx["near"])
        c2 = abs((a_[0] + a_[1]) / 2 - gx["near"]) + abs((b_[0] + b_[1]) / 2 - gx["far"])
        legs = {"far": a_, "near": b_} if c1 <= c2 else {"far": b_, "near": a_}
        for side in ("far", "near"):
            x0, x1, yb = legs[side]
            up = lifts[side]
            if up <= 0:
                continue
            band = big[H - KNEE:H, max(0, x0 - 2):x1 + 3].copy()
            keep = band[..., 3] > 0
            big[H - KNEE:H, max(0, x0 - 2):x1 + 3][keep] = 0
            dst = big[H - KNEE - up:H - up, max(0, x0 - 2):x1 + 3]
            dst[keep] = band[keep]
            legs[side] = (x0, x1, yb - up)
        low = big[H - KNEE - 4:]
        low[(low[..., 3] > 0) & brown(low)] = 0                    # Codex's boot brown (cuffs follow the stamp)
        for side, (sp, sx, sy) in (("far", rear), ("near", front)):
            x0, x1, yb = legs[side]
            h, w = sp.shape[:2]
            px, py = int(round((x0 + x1) / 2 - sx)), yb - sy
            reg = big[py:py + h, px:px + w]
            m = sp[..., 3] > 0
            reg[m] = sp[m]
            bridge(big, px, w, py, sp)
        op = big[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op
        hl, hn = ndimage.label(holes)
        for j in range(1, hn + 1):
            if (hl == j).sum() <= 4:
                big[hl == j] = (*OUTLINE, 255)
        lbl, n = ndimage.label(big[..., 3] > 0, structure=np.ones((3, 3)))
        if n > 1:
            sizes = ndimage.sum(big[..., 3] > 0, lbl, range(1, n + 1))
            big[lbl != (np.argmax(sizes) + 1)] = 0
        ys, xs = np.nonzero(big[..., 3])
        Image.fromarray(big[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(lp(path))
        print(f"run_{k}: near lift {lifts['near']} far lift {lifts['far']} feet {legs}")


if __name__ == "__main__":
    main()
