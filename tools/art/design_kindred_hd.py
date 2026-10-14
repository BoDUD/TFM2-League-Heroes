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


# the side takes (assets/source/kindred/codex_model, step 1): Codex drew ~6-px squares; per take the mask's ear tips
# (outline top), the hooves' lowest row and the hooves' middle in its pixels -> the front's EAR_ROW, SOLE_ROW, MID_COL
EAR_ROW, SOLE_ROW, MID_COL = 12, 165, 162
SIDES = {"A": (93, 1006, 838), "B": (96, 998, 810)}
SIDE_W = 250                  # B's bow reaches column 233
# the front's mask head (one face in every frame, memory one-face-all-frames): the mask's own squares - the piece of
# non-fur, non-outline squares holding the near eye - and the outline round it, inside this box (rows, cols)
HEAD_BOX = (10, 58, 150, 183)
EYE = (38, 162)


def mask_piece(a, eye, box):
    """(rows, cols) boolean of the mask: the 4-connected non-fur, non-outline piece holding `eye`, inside `box`, plus
    the outline squares within 2 of it."""
    r0, r1, c0, c1 = box
    op = a[..., 3] > 0
    rgb = a[..., :3].astype(float)
    lab = dv.srgb2lab(rgb)
    dark = rgb.sum(-1) < 90
    fur = (lab[..., 0] > 60) & (lab[..., 1] > -15) & (lab[..., 2] < 5)
    inner = op & ~dark & ~fur
    inner[:r0] = inner[r1:] = False
    inner[:, :c0] = inner[:, c1:] = False
    lbl, _ = ndimage.label(inner)
    piece = lbl == lbl[eye]
    ring = ndimage.binary_dilation(piece, iterations=2) & dark & op
    return piece | ring


side_left = [None]


# the mask's outline on the front design (row, col), drawn round it by eye at 10x (fhead review 2026-10-14): ear tips,
# the right cheek, the snout tip, the left cheek; every non-fur square inside is the mask
MASK_POLY = [(11, 151), (11, 183), (47, 184), (59, 177), (59, 167), (35, 154), (22, 151)]


def poly_mask(shape, poly):
    from PIL import ImageDraw
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([(c, r) for r, c in poly], fill=1, outline=1)
    return np.array(im) > 0


def paste_head(front, sd):
    """The front's mask (mask_piece) laid on the side take where it matches best (the side's own mask squares as the
    target, +-12 squares round the same spot), the side's own mask squares it does not cover turned to the outline."""
    rgbf = front[..., :3].astype(float)
    labf = dv.srgb2lab(rgbf)
    furf = (labf[..., 0] > 60) & (labf[..., 1] > -15) & (labf[..., 2] < 5)
    fm = poly_mask(front.shape, MASK_POLY) & (front[..., 3] > 0) & ~furf
    darkf = rgbf.sum(-1) < 90
    fm &= ~darkf | ndimage.binary_dilation(fm & ~darkf, structure=np.ones((3, 3)), iterations=2)  # only its own ring
    rgb = sd[..., :3].astype(float)
    lab = dv.srgb2lab(rgb)
    cand = (sd[..., 3] > 0) & (rgb.sum(-1) >= 90) & ~((lab[..., 0] > 60) & (lab[..., 1] > -15) & (lab[..., 2] < 5))
    ys, xs = np.nonzero(fm)
    best = None
    for dy in range(-14, 15):
        for dx in range(-14, 15):
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < sd.shape[0]) & (xx >= 0) & (xx < sd.shape[1])
            d = np.abs(front[ys[ok], xs[ok], :3].astype(int) - sd[yy[ok], xx[ok], :3].astype(int)).sum(-1)
            score = (d < 60).sum()
            if best is None or score > best[0]:
                best = (score, dy, dx)
    _, dy, dx = best
    out = sd.copy()
    cover = np.zeros_like(cand)
    cover[ys + dy, xs + dx] = True
    out[ys + dy, xs + dx] = front[ys, xs]
    # what is left of the side's own mask round the pasted one (A: its far ear behind, specks off the snout): non-fur
    # squares outside the pasted mask, above the cheek, from the mask's left edge rightwards, touching the background
    r0, c0 = min(r for r, _ in MASK_POLY) + dy, min(c for _, c in MASK_POLY) + dx
    r1, c1 = 47 + dy, max(c for _, c in MASK_POLY) + dx + 6
    zone = np.zeros_like(cand)
    zone[max(r0 - 8, 0):r1, c0:c1] = True
    left = zone & ~cover & (out[..., 3] > 0) & ~((lab[..., 0] > 60) & (lab[..., 1] > -15) & (lab[..., 2] < 5))
    left &= ~((lab[..., 1] < -20) & (lab[..., 0] > 70))           # the bow's pale teal tip
    lbl, n = ndimage.label(left, structure=np.ones((3, 3)))
    bgd = ndimage.binary_dilation(out[..., 3] == 0, structure=np.ones((3, 3)))
    gone = 0
    for k in range(1, n + 1):
        piece = lbl == k
        if (piece & bgd).any() and piece.sum() < 60:
            out[piece] = 0
            gone += int(piece.sum())
    print("side's own mask squares cleared:", gone)
    # loose outline specks (1-4 squares of outline with nothing but background and outline round them)
    op = out[..., 3] > 0
    dk = op & (out[..., :3].astype(int).sum(-1) < 90)
    lbl, n = ndimage.label(dk, structure=np.ones((3, 3)))
    lit = ndimage.binary_dilation(op & ~dk, structure=np.ones((3, 3)))
    for k in range(1, n + 1):
        piece = lbl == k
        if piece.sum() <= 4 and not (piece & lit).any():
            out[piece] = 0
    print("head pasted at", (dy, dx))
    return out


def side(take, pal):
    """Codex's side take on the front's grid: every pixel snapped to the palette, each square the palette colour most
    of its pixels have (an area vote, no mixed colours), scaled so the ear tips and the hooves land on the front's rows."""
    a = np.array(Image.open(os.path.join(SRC, "codex_model", f"kindred-side-lamb-{take}.png")).convert("RGBA"))
    op = a[..., 3] >= ALPHA
    ear, sole, mid = SIDES[take]
    s = (sole + 1 - ear) / (SOLE_ROW + 1 - EAR_ROW)
    idx = np.full(op.shape, -1)
    lab = dv.srgb2lab(a[op][:, :3].astype(float))
    pl = dv.srgb2lab(pal.astype(float))
    idx[op] = ((lab[:, None] - pl[None]) ** 2).sum(-1).argmin(1)
    H, W = 166, SIDE_W
    g = np.zeros((H, W, 4), np.uint8)
    for r in range(H):
        y0 = sole + 1 - (SOLE_ROW + 1 - r) * s
        for c in range(W):
            x0 = mid + (c - MID_COL - 0.5) * s
            ya, yb, xa, xb = int(round(y0)), int(round(y0 + s)), int(round(x0)), int(round(x0 + s))
            if yb <= 0 or xb <= 0 or ya >= a.shape[0] or xa >= a.shape[1]:
                continue
            cell = idx[max(ya, 0):yb, max(xa, 0):xb].ravel()
            if (cell >= 0).sum() * 2 < cell.size:
                continue
            v = np.bincount(cell[cell >= 0], minlength=len(pal))
            g[r, c, :3] = pal[v.argmax()]
            g[r, c, 3] = 255
    print(f"side {take}: {s:.2f} px a square")
    return g


def wolf_side(pal, front_wolf):
    """Codex's wolf profile at the front wolf's size: the same area (its own drawing came out 881 x 506 px, ~2x the
    asked size), by pixel_down.pixelate of the palette-snapped picture (the same tool that made the front wolf)."""
    a = np.array(Image.open(os.path.join(SRC, "codex_model", "kindred-side-wolf.png")).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= ALPHA, 255, 0)
    op = a[..., 3] > 0
    lab = dv.srgb2lab(a[op][:, :3].astype(float))
    pl = dv.srgb2lab(pal.astype(float))
    a[op, :3] = pal[((lab[:, None] - pl[None]) ** 2).sum(-1).argmin(1)]
    ys, xs = np.nonzero(op)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    area = (front_wolf[..., 3] > 0).sum()
    k = np.sqrt(area / (a[..., 3] > 0).sum())
    small, _ = pd.pixelate(a, k, (a.shape[1], a.shape[0] // 2), pd.edge_colour(a), pal=pal.astype(float))
    print("wolf side", a.shape[:2], "->", small.shape[:2], "k %.3f" % k)
    return small


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
    return whole, lam, wol, pal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    whole, lam, wol, pal = build()
    sides = {t: paste_head(lam, side(t, pal)) for t in SIDES}
    wside = wolf_side(pal, wol)
    os.makedirs(OUT, exist_ok=True)
    for name, im in (("front", whole), ("front_lamb", lam), ("front_wolf", wol), ("side_A_raw", sides["A"]),
                     ("side_B_raw", sides["B"]), ("side_wolf", wside)):
        Image.fromarray(im).save(os.path.join(OUT, name + ".png"))
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        z = 5
        h, w = whole.shape[:2]
        bg = Image.new("RGBA", (w * 3 * z + 40, h * z), (255, 0, 255, 255))
        for i, im in enumerate((lam, sides["A"], sides["B"])):
            bg.alpha_composite(Image.fromarray(im).resize((w * z, h * z), Image.NEAREST), (i * (w * z + 20), 0))
        bg.convert("RGB").save(os.path.join(a.preview, "kindred_design.png"))


if __name__ == "__main__":
    main()
