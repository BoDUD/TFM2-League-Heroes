#!/usr/bin/env python3
"""The huntress's run, drawn from her design: leaning forward, the legs in a crossing stride (assets/source/nidalee/frames
run_1..8.png; the rest of frames/ untouched).

    python tools/art/run_nidalee.py [--review DIR]

The user, 2026-10-13: 「奈德丽走路有点问题 跑动姿势不像LOL的」 (the run was league_braum's walk on her standing design),
then, handed the redraw pack (RUN_FIX.md): 「你自己画跑步 8 帧」. A lean like League's (sheared upper body) was shown and
turned down: 「站直了啊」「怎么身体歪的」 - the upper body stands straight, only the legs run (picked 「身体站直 + 两腿交叉跑」).
Built the way league_zeri's approved run was (memory run-legs-caitlyn-way: straight legs, a scissor stride, the upper body
leaning on a shear above the hips with the head moved as one block, boots pasted unsheared):
  * the upper body (design rows above HIP) leans forward on an even LEAN shear (row y moves (HIP - y) x LEAN columns
    right); the head above NECK moves as one block with the neck row's shift (never sheared); the javelin (SPEAR mask)
    moves as one block with the far hand's row, so it stays straight and upright in her hand;
  * each leg (below HIP: the near one left of LEG_SPLIT, the far one up to LEG_END) is one straight slanted piece: its rows
    shifted in proportion to their depth below HIP so the ankle (row ANKLE) lands PHASES[k][0] columns from where it
    stands; a lifted leg loses its top `lift` rows and rises by them (league_braum's walk); the boot (rows from ANKLE)
    is pasted unsheared at the ankle's shift; the far leg runs the same phases four frames on (the legs take turns in
    front and cross under the body at frames 1 and 5); the near leg is drawn over the far one, the body over both;
  * the whole frame rises BOB[k] rows; cracks the slant opens take the outline (gap-check).
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
import import_nidalee_strips as I  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

HIP = 102                 # design row under the loincloth's belt: the legs start below it
NECK = 57                 # design row under the chin: the head above it moves as one block
ANKLE = 154               # design row where the boots start (pasted unsheared)
LEG_SPLIT = 41            # near leg left of this column; the loincloth's fringe between stays with the body
LEG_START_FAR = 54
LEG_END = 82              # the far leg (and its boot toe) up to here; the javelin's shaft right of it
LEAN = 0.0                # the upper body stands straight like the idle (the user: 「站直了啊」「怎么身体歪的」; a 0.5 lean was tried)
# per frame: (ankle shift in columns, lift in rows) of the near leg; the far leg takes the phase four frames on
PHASES = [(0, 0), (-8, 0), (-16, 0), (-24, 4), (-10, 12), (4, 10), (12, 2), (14, 0)]
FAR_DX = 10               # the far leg's phases sit FAR_DX further forward: the feet converge but never swap sides
                          # (league_zeri / league_irelia: 「腿和腰之间有点变形」 when the legs crossed over)
BOB = [0] * 8              # the planted sole stays on the ground (the frame is grounded instead)
RUN_MS = 100
CRACK = 40
SPECK = 20


def spear_mask(d):
    """The javelin's squares in the design: the blade and feathers above the hand, the shaft below it, the gold butt
    over the far boot's toe."""
    H, W = d.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    op = d[..., 3] > 0
    m = (yy < 53) & (xx >= 79)
    m |= (yy >= 73) & (yy < 154) & (xx >= 82) & (xx <= 88)
    m |= (yy >= 154) & (yy <= 160) & (xx >= 83) & (xx <= 88)
    m |= (yy >= 161) & (yy <= 163) & (xx >= 85) & (xx <= 88)
    return m & op


def run_frame(k):
    d = I.design("human")
    H, W = d.shape[:2]
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:H, 0:W]
    spear = spear_mask(d)
    near = op & (yy >= HIP) & (xx < LEG_SPLIT) & ~spear
    far = op & (yy >= HIP) & (xx >= LEG_START_FAR) & ((xx <= LEG_END) | (yy >= ANKLE)) & ~spear
    body = op & ~spear & ~near & ~far
    pad = 40
    out = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)

    def put(mask, dx_of_row, dy=0, cut_top=0):
        ys, xs = np.nonzero(mask)
        keep = ys >= cut_top
        ys, xs = ys[keep], xs[keep]
        tx = xs + np.array([dx_of_row(y) for y in ys], int) + pad
        ty = ys + dy + pad
        ok = (tx >= 0) & (tx < out.shape[1]) & (ty >= 0) & (ty < out.shape[0])
        out[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]

    body_sil = ndimage.binary_fill_holes(body | spear)

    def leg(mask, phase, extra=0):
        """A lifted leg rises whole (no rows cut: a cut left a flat edge at the thigh's top); what of it rises above the
        hips outside the body's silhouette is dropped, the rest is hidden behind the body drawn over it."""
        dxa, lift = phase
        dxa += extra
        k_ = dxa / float(ANKLE - HIP)
        shin = lambda y: int(round((min(y, ANKLE) - HIP) * k_)) if y >= HIP else 0
        ys, xs = np.nonzero(mask)
        tx = xs + np.array([shin(y) for y in ys], int)
        ty = ys - lift
        keep = (ty >= HIP) | body_sil[np.clip(ty, 0, H - 1), np.clip(tx, 0, W - 1)]
        m2 = np.zeros_like(mask)
        m2[ys[keep], xs[keep]] = True
        put(m2, shin, dy=-lift)

    p_far = PHASES[(k + 4) % 8]
    leg(far, p_far, FAR_DX)
    leg(near, PHASES[k])
    lean = lambda y: int(round((HIP - max(y, NECK)) * LEAN)) if y < HIP else 0
    put(body, lean)
    hand = int(round((HIP - 62) * LEAN))
    put(spear, lambda y: hand)
    # cracks the slant opened between the legs and the body: small enclosed gaps take the outline
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    dark = I.darkest(d)
    for j in range(1, n + 1):
        hole = lab == j
        if hole.sum() <= CRACK:
            out[hole] = (*dark, 255)
    # specks the cuts left (a few squares of the javelin's butt or the boots' toes apart from everything): dropped
    lab, n = ndimage.label(out[..., 3] > 0)
    if n > 1:
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz < SPECK:
                out[lab == j] = 0
    # onto the pack canvas at the design's place, risen BOB rows
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    x0, y0 = I.FORMS["human"]["at"]
    ox, oy = x0 - pad, y0 - pad - BOB[k]
    ys, xs = np.nonzero(out[..., 3] > 0)
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty <= I.SOLE) & (tx >= 0) & (tx < I.COLS)
    can[ty[ok], tx[ok]] = out[ys[ok], xs[ok]]
    # the edges the moves opened (a lifted thigh's top beside the hip) take the design's outline; the planted sole on the
    # ground row
    can = G.complete_outline(can, color=dark)[0]
    return I.ground(can)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the 8 frames side by side at 3x here")
    a = ap.parse_args()
    frames = [run_frame(k) for k in range(8)]
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
        Z = 3
        crop = [f[:, 60:260] for f in frames]
        big = Image.new("RGBA", (len(crop) * 200 * Z, I.ROWS * Z), (96, 112, 96, 255))
        for k, c in enumerate(crop):
            big.alpha_composite(Image.fromarray(np.ascontiguousarray(c)).resize((200 * Z, I.ROWS * Z), Image.NEAREST),
                                (k * 200 * Z, 0))
        big.convert("RGB").save(os.path.join(a.review, "nidalee_run_new.png"))
    print("run: 8 frames written")


if __name__ == "__main__":
    main()
