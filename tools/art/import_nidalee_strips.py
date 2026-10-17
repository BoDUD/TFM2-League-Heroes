#!/usr/bin/env python3
"""Nidalee's step-2 delivery (Codex, assets/source/nidalee/codex_strips: 68 frames, one dense square a pixel on the
pack's 307 x 204 canvas) made into her action frames: assets/source/nidalee/frames/<tag>_<n>.png + frames.json.

    python tools/art/import_nidalee_strips.py [--review DIR]

Codex's own handoff says the frames are on the grid and in the palette but the heads are its own, the sizes drift and
the soles miss the ground; reading them back (2026-10-13) also showed the cougar about 1.2x the design in most tags and
floating 20-30 rows in its run, and the huntress's run keeping the same leg in front in all 8 frames (Braum's hop).
The user picked 「我在导入时修」:
  1. size: every frame's head is found by matching the design's face (skimage match_template on the colours) on the frame
     shrunk by 1/s for s in SCALES; each tag takes the median s of its frames that matched (one size through a tag, no
     wobble) and the frame is brought to the design's size by 1/s, nearest neighbour, round the standing point (the
     frames go down to about 2.2 squares a game pixel later, the user's pick 「按泽丽标准」, so this costs nothing that
     step keeps);
  2. ground: the lowest opaque row on the soles' row SOLE (AIR frames - the pounce's leap - keep their height above it);
  3. one face: in every upright frame the design's head (HEAD box, its opaque squares) is pasted where the face matched
     at s = 1 (the cougar's biting frames keep Codex's open jaw: NO_HEAD);
  4. the huntress's run: the approved walk (league_braum's / league_nautilus's, rig_braum.walk_frame) on her design: the
     legs under LEG_BAND cut at LEG_SPLIT (the javelin's columns stay with the body), lifted and moved forward in turn;
     Codex's run frames are not used.
The idles (the designs) and hit come later with the breathing (rig step).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.feature import match_template

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "nidalee")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
COLS, ROWS, SOLE = 307, 204, 196
FORMS = {
    # design, where it sits on the canvas, standing point column; the face matched (rows, cols in the design) and the
    # head pasted (rows, cols)
    "human": {"design": "human.png", "at": (98, 29), "piv": 140, "face": (30, 56, 34, 61), "head": (22, 57, 26, 64)},
    "cougar": {"design": "cougar.png", "at": (24, 84), "piv": 160, "face": (10, 56, 186, 229), "head": (2, 58, 184, 230)},
}
SCALES = np.round(np.arange(0.80, 1.36, 0.02), 2)
MATCH_MIN = 0.55                 # a face found below this score does not count (lying, turned, covered)
AIR = {("c_pounce", 2), ("c_pounce", 3), ("c_pounce", 4)}
NO_HEAD = {"c_skill"}            # the bite opens the jaw: Codex's head kept
# the huntress's walk on her design (rig_braum.walk_frame's way, its hd steps x 3.83 / 2.88)
LEG_BAND = 117                   # the design's row under the loincloth's hips: the legs start below it
LEG_SPLIT = 45                   # the column between the legs (near leg left of it)
LEG_END = 80                     # the far leg ends left of the javelin (columns 81-88 stay with the body)
WALK = [((0, 0), (0, 8), 4), ((0, 0), (4, 12), 8), ((0, 0), (4, 4), 4), ((0, 0), (4, 0), 0),
        ((0, 8), (0, 0), 4), ((4, 12), (0, 0), 8), ((4, 4), (0, 0), 4), ((4, 0), (0, 0), 0)]
WALK_MS = 115
OUTLINE = (20, 12, 16)           # the design's near-black (closest palette colour is used)
CRACK = 80


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def design(form):
    return rgba(os.path.join(SRC, "hd", FORMS[form]["design"]))


def canvas(form):
    """The design on the pack's canvas (where Codex was told it stands)."""
    d = design(form)
    x0, y0 = FORMS[form]["at"]
    c = np.zeros((ROWS, COLS, 4), np.uint8)
    c[y0:y0 + d.shape[0], x0:x0 + d.shape[1]] = d
    return c


def as_float(a):
    """Colours for matching: transparent squares a fixed mid grey."""
    f = a[..., :3].astype(float) / 255.0
    f[a[..., 3] == 0] = 0.4
    return f


def find_face(frame, form):
    """(score, s, x, y): the design's face found in the frame shrunk by 1/s; (x, y) the face box's top-left in the
    frame's own squares."""
    r0, r1, c0, c1 = FORMS[form]["face"]
    t = as_float(design(form)[r0:r1, c0:c1])
    best = (-1.0, 1.0, 0, 0)
    for s in SCALES:
        w, h = max(1, round(COLS / s)), max(1, round(ROWS / s))
        f = as_float(np.asarray(Image.fromarray(frame).resize((w, h), Image.NEAREST)))
        if f.shape[0] < t.shape[0] or f.shape[1] < t.shape[1]:
            continue
        sc = np.mean([match_template(f[..., k], t[..., k]) for k in range(3)], axis=0)
        y, x = np.unravel_index(np.argmax(sc), sc.shape)
        if sc[y, x] > best[0]:
            best = (float(sc[y, x]), float(s), int(round(x * s)), int(round(y * s)))
    return best


def rescale(frame, s, piv):
    """The frame brought to the design's size: shrunk (or grown) by 1/s round (piv, the soles' bottom edge)."""
    if abs(s - 1.0) < 1e-6:
        return frame.copy()
    H, W = frame.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    sx = np.round((xx + 0.5 - (piv + 0.5)) * s + (piv + 0.5) - 0.5).astype(int)
    sy = np.round((yy + 0.5 - (SOLE + 1)) * s + (SOLE + 1) - 0.5).astype(int)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    out = np.zeros_like(frame)
    out[ok] = frame[sy[ok], sx[ok]]
    return out


def ground(frame):
    ys = np.nonzero((frame[..., 3] > 0).any(1))[0]
    return np.roll(frame, SOLE - int(ys.max()), axis=0) if len(ys) else frame


def paste_head(frame, form, x, y):
    """The design's head (HEAD box, opaque squares) pasted with its face box at (x, y) of the frame."""
    f = FORMS[form]
    r0, r1, c0, c1 = f["head"]
    fr0, _, fc0, _ = f["face"]
    d = design(form)[r0:r1, c0:c1]
    ox, oy = x - (fc0 - c0), y - (fr0 - r0)
    out = frame.copy()
    ys, xs = np.nonzero(d[..., 3] > 0)
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty < ROWS) & (tx >= 0) & (tx < COLS)
    out[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]
    return out


def walk_frame(idle, near_step, far_step, rise):
    """league_braum's walk on the huntress's design canvas: each leg's squares under LEG_BAND moved (dx, -lift) after
    losing their top `lift` rows; the far leg first, the near one over it, the body over both; the frame `rise` rows up."""
    x0, y0 = FORMS["human"]["at"]
    band = y0 + LEG_BAND
    H, W = idle.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    op = idle[..., 3] > 0
    near = op & (yy > band) & (xx < x0 + LEG_SPLIT)
    far = op & (yy > band) & (xx >= x0 + LEG_SPLIT) & (xx <= x0 + LEG_END)
    body = idle.copy()
    body[near | far] = 0
    out = np.zeros_like(idle)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        leg = np.where(m[..., None], idle, 0).astype(np.uint8)
        leg[:band + 1 + lift] = 0
        ys, xs = np.nonzero(leg[..., 3] > 0)
        ok = (ys - lift >= 0) & (xs + dx < W)
        out[ys[ok] - lift, xs[ok] + dx] = leg[ys[ok], xs[ok]]
    m = body[..., 3] > 0
    out[m] = body[m]
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    own = ndimage.binary_fill_holes(idle[..., 3] > 0) & ~(idle[..., 3] > 0)
    dark = darkest(idle)
    for j in range(1, n + 1):
        hole = lab == j
        xs = np.nonzero(hole.any(0))[0]
        if hole.sum() <= CRACK and (xs.max() - xs.min() < 3 or not (hole & own).any()):
            out[hole] = (*dark, 255)
    return np.roll(out, -rise, axis=0)


def darkest(a):
    c = a[a[..., 3] > 0][:, :3].astype(int)
    return tuple(int(v) for v in c[np.argmin(c.sum(1))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a before / after sheet per tag here")
    a = ap.parse_args()
    cells = json.load(open(os.path.join(CODEX, "cells.json"), encoding="utf-8"))
    by_tag = {}
    for f in cells["frames"]:
        by_tag.setdefault(f["tag"], []).append(f)
    os.makedirs(OUT, exist_ok=True)
    table, report = {}, []
    for tag, frames in by_tag.items():
        form = frames[0]["form"]
        piv = FORMS[form]["piv"]
        if tag == "run":            # the approved walk on the design (Codex's run is not used)
            idle = canvas("human")
            outs = [walk_frame(idle, n_, f_, r_) for n_, f_, r_ in WALK]
            table[tag] = []
            for i, o in enumerate(outs):
                name = f"{tag}_{i + 1}.png"
                Image.fromarray(o).save(os.path.join(OUT, name))
                table[tag].append([name, WALK_MS])
            report.append(f"{tag:12s} walk on the design, {len(outs)} frames")
            continue
        raw = [rgba(os.path.join(CODEX, f["file"].replace(".png", "_1x.png"))) for f in frames]
        found = [find_face(r, form) for r in raw]
        good = [m[1] for m in found if m[0] >= MATCH_MIN]
        s = float(np.median(good)) if good else 1.0
        table[tag] = []
        for i, (r, f, m) in enumerate(zip(raw, frames, found)):
            o = rescale(r, s, piv)
            if (tag, i + 1) not in AIR:
                o = ground(o)
            pasted = False
            if tag not in NO_HEAD and m[0] >= MATCH_MIN:
                sc, s1, x, y = find_face(o, form)
                if sc >= MATCH_MIN and abs(s1 - 1.0) <= 0.04:
                    o = paste_head(o, form, x, y)
                    pasted = True
            name = f"{tag}_{i + 1}.png"
            Image.fromarray(o).save(os.path.join(OUT, name))
            table[tag].append([name, f["ms"]])
            report.append(f"{tag:12s} {i + 1}: face {m[0]:.2f} at s {m[1]:.2f} -> tag s {s:.2f}{' head' if pasted else ''}")
    with open(os.path.join(OUT, "frames.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    print("\n".join(report))


if __name__ == "__main__":
    main()
