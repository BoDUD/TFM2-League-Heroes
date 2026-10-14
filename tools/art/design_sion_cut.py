#!/usr/bin/env python3
"""league_sion's step-0 read-back and the 44-row guide cut (assets/source/sion/design/).

    python tools/art/design_sion_cut.py

The user picked picture A (the axe hanging by the near leg) at 44 rows crown to soles (2026-10-14). Codex's own 44-row
cut (codex_picture/sion-model-A_1x.png) reads muddy; its raw draft (codex_picture/raw/sion-A-draft-02.png, ~12-px
squares) is clean. Writes:
  A_draft_rg.png  the raw draft read back on its own grid (regrid.py): 108 x 81, crown row 9, soles row 80 (72 rows)
  A44_cut.png     that read-back brought to 44 rows crown to soles by a majority vote (Bard's cut: 24 colours, a square
                  clear where half of it is, outline where a third of the drawn part is near-black, else the colour
                  covering most of it), the outline closed - ONLY the step-1 pack's size / place guide; the design
                  itself is Codex's on-grid redraw (art-spec "A muddy design").
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid  # noqa: E402
import strips  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sion")
RAW = os.path.join(SRC, "codex_picture", "raw", "sion-A-draft-02.png")
OUT = os.path.join(SRC, "design")
CROWN, SOLE, TARGET = 9, 80, 44
def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def kmeans(px, n, seed=0, it=25):
    rng = np.random.default_rng(seed); L = lab(px.astype(float))
    cen = L[rng.choice(len(L), n, replace=False)]
    for _ in range(it):
        idx = ((L[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (idx == j).any(): cen[j] = L[idx == j].mean(0)
    idx = ((L[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
    return np.array([px[idx == j].mean(0) if (idx == j).any() else px[0] for j in range(n)]).round().astype(np.uint8)

def cut(a, crown, sole, target, n_col=24):

    op = a[..., 3] > 0; H, W = op.shape
    dk = a[..., :3].astype(int).sum(-1) < 90
    pal = np.vstack([[[14, 12, 18]], kmeans(a[op & ~dk][:, :3], n_col - 1)]).astype(np.uint8)
    d = ((lab(a[..., :3].astype(float))[..., None, :] - lab(pal.astype(float))[None, None]) ** 2).sum(-1)
    idx = np.where(op, d.argmin(-1), -1); idx[op & dk] = 0
    s = (sole - crown + 1) / target
    nrows, ncols = int(np.ceil((sole + 1) / s)), int(np.ceil(W / s)); top = sole + 1 - nrows * s
    res = np.zeros((nrows, ncols, 4), np.uint8)
    for r in range(nrows):
        for c in range(ncols):
            y0, y1, x0, x1 = top + r * s, top + (r + 1) * s, c * s, (c + 1) * s
            w = {}; tot = 0
            for yy in range(int(np.floor(y0)), int(np.ceil(y1))):
                if not 0 <= yy < H: continue
                wy = min(y1, yy + 1) - max(y0, yy)
                for xx in range(int(np.floor(x0)), int(np.ceil(x1))):
                    if not 0 <= xx < W: continue
                    wx = min(x1, xx + 1) - max(x0, xx); k = idx[yy, xx]
                    w[k] = w.get(k, 0) + wx * wy; tot += wx * wy
            if tot == 0 or w.get(-1, 0) >= tot / 2: continue
            drawn = tot - w.get(-1, 0)
            if w.get(0, 0) >= drawn / 3: k = 0
            else: k = max((v, kk) for kk, v in w.items() if kk > 0)[1]
            res[r, c, :3] = pal[k]; res[r, c, 3] = 255
    im = Image.fromarray(res)
    bb = im.getbbox(); im = im.crop(bb)
    im = Image.fromarray(strips.complete_outline(np.array(im))[0])
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    rg = regrid.regrid(np.array(Image.open(RAW).convert("RGBA")))[0]
    Image.fromarray(rg).save(os.path.join(OUT, "A_draft_rg.png"))
    im = cut(rg, CROWN, SOLE, TARGET)
    im.save(os.path.join(OUT, "A44_cut.png"))
    print("A_draft_rg", rg.shape[1::-1], "A44_cut", im.size)


if __name__ == "__main__":
    main()
