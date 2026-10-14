#!/usr/bin/env python3
"""league_kindred's dense design from Codex's step 0 picture B (Lamb on both hooves, Wolf low behind her hips).

    python tools/art/design_kindred_hd.py [--preview DIR]

The user's picks (2026-10-14): picture B; the Wolf about 55 %; Lamb 34 game rows ear tips to hooves (「模型还得缩小」,
85 % of the first 40), Zeri's density at the end (ppu_restyle); until then the picture read back 1:1 (no
resampling of Lamb). So:
  1. picture B with a hard alpha (Codex's alpha never reached 255: a soft haze round both figures; >= ALPHA is figure);
  2. read back on its own grid (regrid.py's boundary search at SQ px: Codex drew ~5.5-px squares, not the 8 asked for;
     Lamb ear tips -> hooves ~154 squares);
  3. one palette: K Lab k-means colours of the read-back (design_varus.kmeans), every square snapped to it;
  4. Lamb / Wolf split: a square is Lamb's when most of its middle is in Codex's B-lamb layer (that layer is redrawn by
     Codex's editor - 76 % of its pixels within 20 of the picture - so only its shape is used, never its colours);
     loose non-Lamb specks away from the wolf go to Lamb (tidy_split);
  5. the Wolf brought to WOLF_SCALE by pixel_down.pixelate (shrink_wolf), its nose tip where it was;
  6. both on the read-back's canvas, Lamb over Wolf.
Writes assets/source/kindred/hd/front.png (whole), front_lamb.png and front_wolf.png (layers, same canvas).
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
import design_varus as dv  # noqa: E402
import pixel_down as pd  # noqa: E402
from regrid import boundaries, profile  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kindred")
OUT = os.path.join(SRC, "hd")
SQ = 5.5
K = 40
ALPHA = 160
WOLF_SCALE = 0.55               # the user: 70 % first, then 「狼再小一些」 (2026-10-14)
NEAR = 8                      # a loose mane tuft lies within this many squares of the wolf's head + mane


def load(name):
    a = np.array(Image.open(os.path.join(SRC, "codex_picture", name)).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= ALPHA, 255, 0)
    return a


def readback(a, lamb):
    """(H, W, 4) squares of picture a on its own grid, and the (H, W) Lamb vote from the layer mask."""
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    bx = boundaries(profile(a, op, 1), xs.min(), xs.max(), SQ)
    by = boundaries(profile(a, op, 0), ys.min(), ys.max(), SQ)
    H, W = len(by) - 1, len(bx) - 1
    out = np.zeros((H, W, 4), np.uint8)
    who = np.zeros((H, W), bool)
    for j in range(H):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(W):
            cx = (bx[i] + bx[i + 1]) // 2
            win = a[cy - 1:cy + 2, cx - 1:cx + 2].reshape(-1, 4)
            if (win[:, 3] > 0).sum() * 2 > len(win):
                out[j, i, :3] = np.median(win[win[:, 3] > 0][:, :3], axis=0).astype(np.uint8)
                out[j, i, 3] = 255
                who[j, i] = lamb[cy - 1:cy + 2, cx - 1:cx + 2].sum() * 2 > 9
    return out, who


def snap(one, pal):
    op = one[..., 3] > 0
    lab = dv.srgb2lab(one[op][:, :3].astype(float))
    pl = dv.srgb2lab(pal.astype(float))
    out = one.copy()
    out[op, :3] = pal[((lab[:, None] - pl[None]) ** 2).sum(-1).argmin(1)]
    return out


def tidy_split(op, who):
    """Wolf = its big piece (head + mane) and the loose tufts within NEAR squares of it, left of its nose; every
    other non-Lamb piece (specks along Lamb's edge the layer mask missed) goes to Lamb."""
    lab, n = ndimage.label(op & ~who, structure=np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    big = int(np.argmax(sizes)) + 1
    by_, bx_ = np.nonzero(lab == big)
    nose = bx_.max()
    out = who.copy()
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        inside = (ys.min() >= by_.min() - NEAR and ys.max() <= by_.max() + NEAR and xs.min() >= bx_.min() - NEAR
                  and xs.max() < nose - 4)
        if k != big and not inside:
            out[ys, xs] = True
    return out


def shrink_wolf(wolf, pal):
    """The wolf brought to WOLF_SCALE by pixel_down.pixelate (each new square the mean of its old ones snapped to the
    design palette, outline where dark). Cutting whole rows / columns round a kept 1:1 face crushed the mane and
    broke its outline (tried 2026-10-14); a crisp pass lost the eyes. The grid runs through the nose tip, which stays
    where it was (so the parts Lamb hid stay hidden). -> (small wolf RGBA, its top-left (row, col) on the canvas)."""
    ys, xs = np.nonzero(wolf[..., 3])
    y0, x0 = ys.min(), xs.min()
    w = wolf[y0:ys.max() + 1, x0:xs.max() + 1]
    nx = w.shape[1]
    ny = int(np.nonzero(w[:, nx - 1, 3])[0].mean())
    small, (px, py) = pd.pixelate(w, WOLF_SCALE, (nx, ny), pd.edge_colour(w), pal=pal.astype(float))
    print("wolf", w.shape[:2], "->", small.shape[:2])
    return small, (y0 + ny - py, x0 + nx - px)


def build():
    pic = load("kindred-model-B.png")
    lamb = load("kindred-model-B-lamb.png")[..., 3] > 0
    one, who = readback(pic, lamb)
    _, pal = dv.kmeans(one, K)
    one = snap(one, pal)
    op = one[..., 3] > 0
    who = tidy_split(op, who)
    lm, wm = op & who, op & ~who
    lam = np.where(lm[..., None], one, 0).astype(np.uint8)
    small, (sy, sx) = shrink_wolf(np.where(wm[..., None], one, 0).astype(np.uint8), pal)
    wol = np.zeros_like(one)
    h, w = small.shape[:2]
    wol[sy:sy + h, sx:sx + w] = small
    whole = wol.copy()
    whole[lm] = lam[lm]                            # Lamb over Wolf
    print("grid", one.shape[:2], "lamb squares", int(lm.sum()), "wolf squares", int((wol[..., 3] > 0).sum()),
          "colours", len(pal))
    return whole, lam, wol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    whole, lam, wol = build()
    os.makedirs(OUT, exist_ok=True)
    for name, im in (("front", whole), ("front_lamb", lam), ("front_wolf", wol)):
        Image.fromarray(im).save(os.path.join(OUT, name + ".png"))
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        z = 5
        h, w = whole.shape[:2]
        bg = Image.new("RGBA", (w * 3 * z + 40, h * z), (255, 0, 255, 255))
        for i, im in enumerate((whole, lam, wol)):
            bg.alpha_composite(Image.fromarray(im).resize((w * z, h * z), Image.NEAREST), (i * (w * z + 20), 0))
        bg.convert("RGB").save(os.path.join(a.preview, "kindred_design.png"))


if __name__ == "__main__":
    main()
