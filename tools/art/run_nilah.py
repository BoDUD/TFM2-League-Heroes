#!/usr/bin/env python3
"""Nilah's run, drawn from her side design: the upper body upright, the legs in a straight crossing stride
(assets/source/nilah/frames/run_1..8.png; the rest of frames/ untouched).

    python tools/art/run_nilah.py [--review DIR]

Codex's run (step 2) bent the knees and never swapped the legs; ADC runs are straight legs in a scissor stride (memory
run-legs-caitlyn-way; league_nidalee's approved run, tools/art/run_nidalee.py, the same method):
  * the body (above HIP, the ponytail's hair, the skirt panel and the top's hem) stays as the design has it - upright,
    the head and the blade not moved;
  * the legs below HIP are split into the back (far) one and the front (near) one: the components of the trousers /
    armour / skin left after taking out the outline, the hair and the skirt's colours (the back thigh is the part of the
    big hip component left of column SPLIT); each outline square goes with the nearest leg within 2 squares;
  * each leg is one straight slanted piece: its rows shifted in proportion to their depth below HIP so the ankle (row
    ANKLE) lands at STRIDE[k][0] columns from the hip (HIP_X), the slipper (rows from ANKLE) pasted unsheared at the
    ankle's shift; a lifted leg rises by STRIDE[k][1] rows (what goes above HIP is hidden behind the body); the back leg
    runs the same phases four frames on; the back leg is drawn first, the front one over it, the body over both;
  * cracks the slant opens take the outline (gap-check), specks are dropped, the outline is closed, the frame grounded.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import import_nilah_strips as I  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

HIP = 63                  # cropped design row: the legs start here (the hips above stay with the body)
SPLIT = 30                # the column between the two thighs in the big hip component
ANKLE = 96                # the row where the ankles' skin starts: the slippers below are pasted unsheared
HIP_X = 30                # the hips' column: the stride's ankle positions are measured from it
HAIR = [(60, 50, 102), (37, 27, 62)]
SKIRT = [(128, 52, 239), (252, 173, 6), (254, 217, 47), (250, 161, 3), (84, 184, 213)]
OUTLINE = (10, 1, 20)
# the front leg's ankle (columns from HIP_X, rows lifted) per frame; the back leg takes the phase four frames on. Frame 1:
# the front foot planted ahead, the back one kicked up behind; frames 3 and 7: the feet pass under the hips.
STRIDE = [(11, 0), (7, 0), (2, 0), (-4, 0), (-10, 2), (-7, 8), (0, 10), (6, 4)]
RUN_MS = 100
CRACK = 10
SPECK = 12


def masks(d):
    op = d[..., 3] > 0
    rgb = d[..., :3].astype(int)
    isc = lambda cs: np.any([(rgb == np.array(c)).all(-1) for c in cs], axis=0)
    hair, skirt, outline = isc(HAIR), isc(SKIRT), isc([OUTLINE])
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    reg = op & (yy >= HIP) & ~hair & ~skirt & ~outline
    lab, n = ndimage.label(reg)
    big = np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))) + 1
    back, front = np.zeros_like(op), np.zeros_like(op)
    for j in range(1, n + 1):
        comp = lab == j
        ys, xs = np.nonzero(comp)
        if j == big:
            back |= comp & (xx < SPLIT) & (yy <= 75)
            front |= comp & ~((xx < SPLIT) & (yy <= 75))
        elif xs.mean() < SPLIT:
            back |= comp
        elif ys.max() > 82 or xs.min() < 41:      # the front leg's armour, ankle and slipper (the skirt's bits are higher right)
            front |= comp
    # outline squares below HIP go with the nearest leg within 2 squares
    db = ndimage.distance_transform_edt(~back)
    df = ndimage.distance_transform_edt(~front)
    ol = op & outline & (yy >= HIP)
    back |= ol & (db <= 2) & (db <= df)
    front |= ol & (df <= 2) & (df < db)
    # squares of the hair's / skirt's colours inside a leg (the trousers' darkest shade, the soles) go with that leg:
    # below HIP, a body square with at least 5 of its 8 neighbours in one leg (twice, for 2-square specks)
    kern = np.ones((3, 3))
    for _ in range(2):
        rest_ = op & ~back & ~front & (yy >= HIP)
        nb = ndimage.convolve(back.astype(int), kern, mode="constant")
        nf = ndimage.convolve(front.astype(int), kern, mode="constant")
        back |= rest_ & (nb >= 5) & (nb >= nf)
        front |= rest_ & (nf >= 5) & (nf > nb)
    return back, front, op & ~back & ~front


def run_frame(k, d):
    H, W = d.shape[:2]
    back, front, body = masks(d)
    pad = 30
    out = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)
    body_sil = ndimage.binary_fill_holes(body)

    def leg(mask, rest_x, phase):
        ax, lift = phase
        dx = ax - rest_x
        kk = dx / float(ANKLE - HIP)
        shift = lambda y: int(round((min(y, ANKLE) - HIP) * kk))
        ys, xs = np.nonzero(mask)
        tx = xs + np.array([shift(y) for y in ys], int)
        ty = ys - lift
        keep = (ty >= HIP) | ~body_sil[np.clip(ty, 0, H - 1), np.clip(tx, 0, W - 1)] & (ty >= HIP - 3)
        ys, xs, tx, ty = ys[keep], xs[keep], tx[keep], ty[keep]
        out[ty + pad, tx + pad] = d[ys, xs]

    def rest(mask):
        ys, xs = np.nonzero(mask & (np.mgrid[0:H, 0:W][0] >= ANKLE - 2) & (np.mgrid[0:H, 0:W][0] <= ANKLE + 1))
        return xs.mean() - HIP_X

    leg(back, rest(back), STRIDE[(k + 4) % 8])
    leg(front, rest(front), STRIDE[k])
    ys, xs = np.nonzero(body)
    out[ys + pad, xs + pad] = d[ys, xs]
    # cracks the slant opened: small enclosed gaps take the outline
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    own = np.zeros_like(opq)
    own[pad:pad + H, pad:pad + W] = ndimage.binary_fill_holes(d[..., 3] > 0) & ~(d[..., 3] > 0)
    for j in range(1, n + 1):
        hole = lab == j
        if hole.sum() <= CRACK and not (hole & own).any():
            out[hole] = (*OUTLINE, 255)
    lab, n = ndimage.label(out[..., 3] > 0)
    if n > 1:
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz < SPECK:
                out[lab == j] = 0
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    x0, y0 = I.AT
    ys, xs = np.nonzero(out[..., 3] > 0)
    ty, tx = ys + y0 - pad, xs + x0 - pad
    ok = (ty >= 0) & (ty <= I.SOLE) & (tx >= 0) & (tx < I.COLS)
    can[ty[ok], tx[ok]] = out[ys[ok], xs[ok]]
    can = G.complete_outline(can, color=OUTLINE)[0]
    return I.ground(can)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the 8 frames side by side at 4x on magenta here")
    a = ap.parse_args()
    d = I.design()
    frames = [run_frame(k, d) for k in range(8)]
    table_path = os.path.join(I.OUT, "frames.json")
    table = json.load(open(table_path, encoding="utf-8"))
    table["run"] = []
    for k, f in enumerate(frames):
        name = f"run_{k + 1}.png"
        Image.fromarray(f).save(os.path.join(I.OUT, name))
        table["run"].append([name, RUN_MS])
    with open(table_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z = 4
        crop = [f[I.SOLE - 110:I.SOLE + 2, I.PIV - 45:I.PIV + 45] for f in frames]
        big = Image.new("RGBA", (len(crop) * 90 * Z, 112 * Z), (255, 0, 255, 255))
        for k, c in enumerate(crop):
            big.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((90 * Z, 112 * Z), Image.NEAREST),
                                (k * 90 * Z, 0))
        big.convert("RGB").save(os.path.join(a.review, "nilah_run.png"))
    print("run: 8 frames written")


if __name__ == "__main__":
    main()
