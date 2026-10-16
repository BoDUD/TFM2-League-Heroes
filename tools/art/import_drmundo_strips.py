#!/usr/bin/env python3
"""Dr. Mundo's step-2 frames: Codex's delivery (assets/source/drmundo/codex_strips: 43 frames, one dense square a pixel
on the pack's 219 x 146 canvas, 37 design colours) finished here -> assets/source/drmundo/frames/<tag>_<n>.png +
frames.json.

    python tools/art/import_drmundo_strips.py [--review DIR]

Codex's HANDOFF (2026-10-16): heads redrawn per frame, the saw and the build drifting, sizes jumping, the death not on
the ground. The user: 「完成下一步 有问题的地方你帮忙修复 然后你自己review 完美了再喊我review」. So, the Kalista way
(tools/art/import_kalista_strips.py):
  1. size: the frames Codex drew bigger than the design (SCALE, read off the design's silhouette behind each frame)
     brought back by taking whole rows and columns out (design_akali.dp_keep: never two neighbours, the soles' row
     kept) round the feet;
  2. place: every standing frame moved so the middle of his two feet (their purple in the bottom rows) is where the
     design's is - Codex put most frames 10-20 columns to the right, so the actions jumped sideways; the design stands
     with its torso (not its feet) over the pivot (DESIGN_AT);
  3. heads: Codex's own kept. Its heads are the design's size with the same black spikes, pink eye and teeth (Temp
     md_work/heads_cmp.png); pasting the design head over them (by colour or by the hair) landed on shoulders and chests
     in a third of the frames and left two heads - the Kalista paste is not used;
  4. run (all 8 frames, rebuilt): Codex's run held the saw up in frames 1-4 and down in 5-8 and barely stepped. The
     design itself (pixel-identical to the idle) with its two legs cut below LEG_CUT and swung from the hip, every row
     moved whole (nothing at the cut, the whole step at the foot: no break in the outline; Shen's scissor run, memory
     run-stride-crossing): the near leg forward in frames 1-4 and back in 5-8, the far leg the other way, the swinging
     foot lifted, the body bobbing down over them (never up: no slit at the cut);
  5. death: the lying frames (3-6) moved down so his body rests on the ground row;
  6. tidy: specks off, the outline closed (strips.complete_outline, nothing under the soles), pinholes filled.
The idle (the design breathing) and hit come in the rig step (rig_drmundo.py).
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
from design_akali import dp_keep  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "drmundo")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
COLS, ROWS, SOLE, PIV_X = 219, 146, 138, 100
# design A on the canvas: its torso's middle (design column 70) on the pivot - the pivot between his feet left his body
# 8 game px to the right of it, so every picture on him (the shock, the rings, the dose) sat off his body, and
# a picture's offset cannot follow him to the red side (pictures are never mirrored)
DESIGN_AT = (30, 49)
SPECK = 6


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def rgba(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


A = rgba(os.path.join(SRC, "hd", "A.png"))
OUTLINE = (3, 2, 3)


def classes(a):
    """0 clear, 1 hair / outline (dark, not purple), 2 purple skin, 3 anything else."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    op = a[..., 3] > 0
    purple = op & (b > r) & (b > g + 30) & (r > 50)
    dark = op & ~purple & (r + g + b < 220)
    out = np.full(a.shape[:2], 3, np.int8)
    out[~op] = 0
    out[dark] = 1
    out[purple] = 2
    return out


def is_purple(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return b > r and b > g + 30 and r > 50


# ---------------------------------------------------------------------------------------------- size and place
# read off the design's silhouette behind each frame (Temp/md_work/rev/side_<tag>.png, 2026-10-16)
SCALE = {"attack_3": 1.30, "attack_4": 1.20, "attack_e_2": 1.10, "attack_e_3": 1.10, "attack_e_5": 1.10,
         "skill2_end_1": 1.10, "ult_1": 1.05, "ult_3": 1.10, "ult_4": 1.15, "ult_5": 1.15,
         "dead_3": 1.20, "dead_4": 1.20, "dead_5": 1.20, "dead_6": 1.20}
DESIGN_FRAMES = {"attack_5", "skill_5", "skill2_end_4", "ult_6"}     # Codex copied the design itself
LYING = {"dead_3", "dead_4", "dead_5", "dead_6"}


def feet_mid(a):
    """The middle column of his feet: purple squares in the 8 rows above the ground."""
    band = a[SOLE - 7:SOLE + 1]
    cls = classes(band)
    xs = np.nonzero((cls == 2).any(0))[0]
    if not len(xs):
        xs = np.nonzero(band[..., 3].any(0))[0]
    return (xs.min() + xs.max()) / 2.0


def A_on_canvas():
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[DESIGN_AT[1]:DESIGN_AT[1] + A.shape[0], DESIGN_AT[0]:DESIGN_AT[0] + A.shape[1]] = A
    return can


FEET_X = feet_mid(A_on_canvas())


def shrink(a, s, cx):
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    f = a[y0:y1 + 1, x0:x1 + 1]
    h, w = f.shape[:2]
    key = ((f[..., 0].astype(np.int64) << 24) | (f[..., 1].astype(np.int64) << 16) |
           (f[..., 2].astype(np.int64) << 8) | f[..., 3])
    lum = 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]
    wt = np.where(f[..., 3] > 0, 1.0 + lum / 255.0, 0.2)
    rows, _ = dp_keep([key[r] for r in range(h)], [wt[r] for r in range(h)], round(h / s), hard=(h - 1,))
    f, key, wt = f[rows], key[rows], wt[rows]
    cols, _ = dp_keep([key[:, c] for c in range(w)], [wt[:, c] for c in range(w)], round(w / s))
    f = f[:, cols]
    out = np.zeros_like(a)
    nh, nw = f.shape[:2]
    ny1 = SOLE - round((SOLE - y1) / s)
    nx0 = int(round(cx + (x0 - cx) / s))
    out[ny1 - nh + 1:ny1 + 1, nx0:nx0 + nw] = f
    return out


def shift(a, dx, dy=0):
    out = np.zeros_like(a)
    ys, xs = np.nonzero(a[..., 3] > 0)
    yy, xx = ys + dy, xs + dx
    ok = (yy >= 0) & (yy < ROWS) & (xx >= 0) & (xx < COLS)
    out[yy[ok], xx[ok]] = a[ys[ok], xs[ok]]
    return out


def to_ground(a):
    ys = np.nonzero(a[..., 3].any(1))[0]
    return shift(a, 0, SOLE - ys.max())


# ---------------------------------------------------------------------------------------------- the run
LEG_CUT = 66                              # design rows from here down: the legs move, the rest is the body
LEG_COLS = (44, 102)                      # the legs' columns below LEG_CUT (the saw left of them stays on the body)
LEG_SPLIT = 67                            # near leg left of it, far leg right of it
FOOT_ROW = 82                             # from here down the foot moves the whole way
NEAR_DX = [7, 4, 0, -4, -7, -4, 0, 4]    # the near leg forward (right) in frames 1-4, back in 5-8
NEAR_UP = [0, 0, 0, 0, 0, 2, 3, 2]       # lifted while it swings forward
FAR_DX = [-7, -4, 0, 4, 7, 4, 0, -4]
FAR_UP = [0, 2, 3, 2, 0, 0, 0, 0]
BOB = [2, 1, 0, 1, 2, 1, 0, 1]           # the body sinks on each footfall, highest as the legs pass
RUN_MS = 133                              # League's Run: 1.07 s a cycle


def run_parts():
    body, near, far = A.copy(), np.zeros_like(A), np.zeros_like(A)
    for y in range(LEG_CUT, A.shape[0]):
        for x in range(*LEG_COLS):
            if not A[y, x, 3]:
                continue
            (near if x < LEG_SPLIT else far)[y, x] = A[y, x]
            body[y, x] = 0
    return body, near, far


def run_frames():
    body, near, far = run_parts()
    out = []
    for i in range(8):
        can = np.zeros((ROWS, COLS, 4), np.uint8)
        for part, dx, up in ((far, FAR_DX[i], FAR_UP[i]), (near, NEAR_DX[i], NEAR_UP[i])):
            # the leg swings from the hip: each row moved whole, nothing at the cut, the whole dx at the foot (a row
            # shift keeps every pixel; a leg moved as one block broke its outline at the cut)
            ys, xs = np.nonzero(part[..., 3] > 0)
            rowdx = np.round(dx * (ys - LEG_CUT + 1) / (FOOT_ROW - LEG_CUT + 1)).astype(int)
            lift = np.round(up * (ys - LEG_CUT + 1) / (FOOT_ROW - LEG_CUT + 1)).astype(int)
            can[ys + DESIGN_AT[1] - lift, xs + DESIGN_AT[0] + rowdx] = part[ys, xs]
        ys, xs = np.nonzero(body[..., 3] > 0)
        can[ys + DESIGN_AT[1] + BOB[i], xs + DESIGN_AT[0]] = body[ys, xs]
        can[SOLE + 1:] = 0
        out.append(can)
    return out


# ---------------------------------------------------------------------------------------------- tidy
def tidy(a):
    out = a.copy()
    op = out[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        keep = 1 + int(np.argmax(sizes))
        for i, s in enumerate(sizes, 1):
            if s < SPECK and i != keep:
                out[lab == i] = 0
    out, _, _ = G.complete_outline(out, color=OUTLINE, feet=SOLE)
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) > 2:
            continue
        for y, x in zip(ys, xs):
            nb = [tuple(int(v) for v in out[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= yy < ROWS and 0 <= xx < COLS and out[yy, xx, 3]]
            if nb:
                out[y, x] = Counter(nb).most_common(1)[0][0]
    out[SOLE + 1:] = 0
    return out


# ---------------------------------------------------------------------------------------------- main
def finish(name, f, log):
    if name in DESIGN_FRAMES:
        return A_on_canvas()
    if name in SCALE:
        f = shrink(f, SCALE[name], feet_mid(f))
    if name in LYING:
        f = to_ground(f)
        return f
    dx = int(round(FEET_X - feet_mid(f)))
    log[name] = dx
    return shift(f, dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write contact sheets here")
    a = ap.parse_args()
    cells = json.load(open(lp(os.path.join(CODEX, "cells.json")), encoding="utf-8"))
    tags = {}
    for fr in cells["frames"]:
        tags.setdefault(fr["tag"], []).append(fr)
    frames, log = {}, {}
    for tag, lst in tags.items():
        if tag == "run":
            continue
        for fr in lst:
            name = f"{tag}_{fr['index'] + 1}"
            frames[name] = finish(name, rgba(os.path.join(CODEX, f"drmundo_{name}_1x.png")), log)
    for i, f in enumerate(run_frames()):
        frames[f"run_{i + 1}"] = f
    os.makedirs(lp(OUT), exist_ok=True)
    table = {}
    for tag, lst in tags.items():
        table[tag] = []
        for fr in lst:
            name = f"{tag}_{fr['index'] + 1}"
            out = tidy(frames[name])
            Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
            table[tag].append({"file": f"{name}.png", "ms": RUN_MS if tag == "run" else fr["ms"]})
    with open(lp(os.path.join(OUT, "frames.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"canvas": [COLS, ROWS], "soles_row": SOLE, "standing_point": [PIV_X, SOLE], "tags": table}, f, indent=1)
    for k, v in sorted(log.items()):
        print(f"{k:14s} moved {v:+d} columns")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        ghost = A_on_canvas()
        gm = ghost[..., 3] > 0
        for tag, lst in table.items():
            ims = [rgba(os.path.join(OUT, e["file"])) for e in lst]
            S = Image.new("RGBA", (COLS * len(ims), ROWS), (60, 66, 60, 255))
            for i, im in enumerate(ims):
                g = np.zeros_like(ghost)
                g[gm] = (255, 255, 255, 36)
                S.alpha_composite(Image.fromarray(g), (i * COLS, 0))
                S.alpha_composite(Image.fromarray(im), (i * COLS, 0))
            S.resize((S.width * 3, S.height * 3), Image.NEAREST).save(os.path.join(a.review, f"drmundo_{tag}.png"))
    print("frames:", ", ".join(f"{t} {len(l)}" for t, l in table.items()))


if __name__ == "__main__":
    main()
