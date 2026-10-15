#!/usr/bin/env python3
"""The huntress's run, drawn from her design: the upper body as it stands, the legs in a crossing stride
(assets/source/elise/frames run_1..8.png + faces.json; the rest of frames/ untouched). Run after import_elise_strips.py.

    python tools/art/run_elise.py [--review DIR]

Codex's run (step 2) kept the same leg in front in all 8 frames, the planted toe sliding forward then snapping back -
the user: 「人形态走路对吗？交叉步都没 腿不换步的？」. Rebuilt the way league_nidalee's approved run was
(tools/art/run_nidalee.py, 「身体站直 + 两腿交叉跑」 / 「OK」), memory run-crossing-root-causes:
  * the upper body is the design's (rows above HIP), as in the idle (upright, the same head);
  * the design stands in a wide A: the hips 14 squares apart, the ankles 36. Each leg (below HIP: the near one in
    NEAR_COLS, the far one from LEG_SPLIT - the back legs' claws beside the near thigh left out) is one straight piece:
    its rows shifted in proportion to their depth below HIP so its ankle (row ANKLE) lands INWARD + PHASES[k][0]
    columns from where it stands - under its hip, then a scissor stride; a lifted leg rises `lift` rows (league_braum's
    walk), what of it rises above the hips outside the body's silhouette is dropped; the boot (rows from ANKLE) moves
    whole at the ankle's shift; the far leg runs the same phases four frames on (the legs take turns in front and cross
    under the body at frames 1 and 5); the near leg is drawn over the far one, the body over both;
  * the stride: each ankle STRIDE squares before / behind its hip (feet at most about 11 game pixels apart, crossing by
    2 squares), the lifted foot 8-11 rows up while it swings through; the planted sole on the ground row.
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
import import_elise_strips as I  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

HIP = 84                  # design row under the leotard's V: the legs start below it
ANKLE = 110               # design row where the boots' feet start (moved whole)
LEG_SPLIT = 49            # the near leg left of this column, the far one from it
NEAR_TOP_COL = 32         # above row CLAW_ROW the near leg starts at this column (the back legs' claws are left of it)
CLAW_ROW = 97
INWARD = (11, -11)        # near / far ankle: columns to bring it under its hip (31 -> 42, 67 -> 56)
# per frame: (ankle shift in columns, lift in rows) of the near leg; the far leg takes the phase four frames on
PHASES = [(0, 0), (-3, 0), (-6, 0), (-8, 8), (-3, 11), (3, 7), (6, 2), (8, 0)]
# the body sinks these dense rows over the legs (lowest when the feet are furthest apart, highest as they pass): a
# frozen upper body reads stiff (memory run-crossing-root-causes, oppi's runs bob 3 rows); the legs stay as they are
SINK = [0, 2, 3, 2, 0, 2, 3, 2]
RUN_MS = 115
CRACK = 40
SPECK = 20


def masks(d):
    H, W = d.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    op = d[..., 3] > 0
    legs = op & (yy >= HIP)
    near = legs & (xx < LEG_SPLIT) & ((yy >= CLAW_ROW) | (xx >= NEAR_TOP_COL))
    far = legs & (xx >= LEG_SPLIT)
    return near, far, op & ~near & ~far


def run_frame(k):
    d = I.design("human")
    H, W = d.shape[:2]
    near, far, body = masks(d)
    pad = 40
    out = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)

    def put(mask, dx_of_row, dy=0):
        ys, xs = np.nonzero(mask)
        tx = xs + np.array([dx_of_row(y) for y in ys], int) + pad
        ty = ys + dy + pad
        ok = (tx >= 0) & (tx < out.shape[1]) & (ty >= 0) & (ty < out.shape[0])
        out[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]

    body_sil = ndimage.binary_fill_holes(body)

    def leg(mask, phase, inward):
        dxa, lift = phase
        dxa += inward
        k_ = dxa / float(ANKLE - HIP)
        shift = lambda y: int(round((min(y, ANKLE) - HIP) * k_)) if y >= HIP else 0
        ys, xs = np.nonzero(mask)
        tx = xs + np.array([shift(y) for y in ys], int)
        ty = ys - lift
        keep = (ty >= HIP) | body_sil[np.clip(ty, 0, H - 1), np.clip(tx, 0, W - 1)]
        m2 = np.zeros_like(mask)
        m2[ys[keep], xs[keep]] = True
        put(m2, shift, dy=-lift)

    leg(far, PHASES[(k + 4) % 8], INWARD[1])
    leg(near, PHASES[k], INWARD[0])
    put(body, lambda y: 0, dy=SINK[k])
    # cracks the moves opened between the legs and the body: small enclosed gaps take the outline
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    dark = I.darkest(d) if hasattr(I, "darkest") else tuple(int(v) for v in d[d[..., 3] > 0][:, :3][
        np.argmin(d[d[..., 3] > 0][:, :3].astype(int).sum(1))])
    for j in range(1, n + 1):
        hole = lab == j
        if hole.sum() <= CRACK:
            out[hole] = (*dark, 255)
    lab, n = ndimage.label(out[..., 3] > 0)
    if n > 1:
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz < SPECK:
                out[lab == j] = 0
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    x0, y0 = I.FORMS["human"]["at"]
    ox, oy = x0 - pad, y0 - pad
    ys, xs = np.nonzero(out[..., 3] > 0)
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty <= I.SOLE) & (tx >= 0) & (tx < I.COLS)
    can[ty[ok], tx[ok]] = out[ys[ok], xs[ok]]
    can = despur(can, y0 + HIP)
    can = G.complete_outline(can, color=dark)[0]
    return I.ground(can)


def despur(a, top, passes=3):
    """The shear's jags on the legs' outline (rows from `top`): a square with clear above and below and clear on one
    side - a one-square spur sticking out of the leg's edge - goes; then the outline is closed again."""
    out = a.copy()
    for _ in range(passes):
        op = out[..., 3] > 0
        up = np.zeros_like(op); up[1:] = op[:-1]
        dn = np.zeros_like(op); dn[:-1] = op[1:]
        lf = np.zeros_like(op); lf[:, 1:] = op[:, :-1]
        rt = np.zeros_like(op); rt[:, :-1] = op[:, 1:]
        spur = op & ~up & ~dn & (lf ^ rt)
        spur[:top] = False
        if not spur.any():
            break
        out[spur] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the 8 frames side by side at 3x here")
    a = ap.parse_args()
    frames = [run_frame(k) for k in range(8)]
    table_path = I.lp(os.path.join(I.OUT, "frames.json"))
    faces_path = I.lp(os.path.join(I.OUT, "faces.json"))
    table = json.load(open(table_path, encoding="utf-8"))
    faces = json.load(open(faces_path, encoding="utf-8"))
    x0, y0 = I.FORMS["human"]["at"]
    r0, _, c0, _ = I.FORMS["human"]["face"]
    table["run"] = []
    for k, f in enumerate(frames):
        name = f"run_{k + 1}.png"
        Image.fromarray(f).save(I.lp(os.path.join(I.OUT, name)))
        table["run"].append([name, RUN_MS])
        # the face where the design's is (the body is the design's, grounded: the soles were on the ground already)
        ys = np.nonzero((f[..., 3] > 0).any(1))[0]
        faces[f"run_{k + 1}"] = [x0 + c0, y0 + r0 + SINK[k] + (I.SOLE - (y0 + I.design("human").shape[0] - 1))]
    with open(table_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    with open(faces_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(faces, fh, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z = 3
        crop = [f[:, 40:180] for f in frames]
        big = Image.new("RGBA", (len(crop) * 140 * Z, I.ROWS * Z), (96, 112, 96, 255))
        for k, c in enumerate(crop):
            big.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((140 * Z, I.ROWS * Z), Image.NEAREST),
                                (k * 140 * Z, 0))
        big.convert("RGB").save(os.path.join(a.review, "elise_run_new.png"))
    print("run: 8 frames written")


if __name__ == "__main__":
    main()
