#!/usr/bin/env python3
"""Nilah's step-2 delivery (Codex, assets/source/nilah/codex_strips: 50 frames, one dense square a pixel on the pack's
219 x 146 canvas) made into her action frames: assets/source/nilah/frames/<tag>_<n>.png + frames.json.

    python tools/art/import_nilah_strips.py [--review DIR]

Codex's own handoff (2026-10-13) says the frames are on the grid and in the 29 colours but the heads are its own
redraws, the folded blade drifts when level, the sizes drift and the run has bent legs. import_nidalee_strips.py's way:
  1. size: every frame's head is found by matching the design's face (skimage match_template on the colours) on the frame
     shrunk by 1/s for s in SCALES; Codex's sizes drift inside a tag (s 0.98-1.30 for the same tag), so each frame whose
     face matched well (FRAME_MIN) is brought to the design's size by its own 1/s, the others by the median s of all
     frames (about 1.13: the dying frames' tilted heads are not found), nearest neighbour, round the standing point;
  2. ground: the lowest opaque row on the soles' row SOLE (AIR frames keep their height above it);
  3. one face (then specks of at most 6 squares dropped): in every frame where the face is found again at s = 1 the design's head (the front's head squares,
     design_nilah_hd.HEAD moved by the side take's shift) is pasted on the face (memory one-face-all-frames).
The idle (the front design) and hit come later with the rig step.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from skimage.feature import match_template

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_nilah_hd as dn  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nilah")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
COLS, ROWS, SOLE, PIV = 219, 146, 140, 80
AT = (49, 35)                     # the cropped side design's top-left on the pack canvas (pack_nilah_strips.py)
CROP = (10, 11)                   # hd/side.png's crop (rows, columns) for the pack
FACE = (11, 25, 30, 46)           # the face matched: rows, columns in the cropped design (eyes, nose, mouth, cheeks)
SCALES = np.round(np.arange(0.80, 1.31, 0.02), 2)
MATCH_MIN = 0.55                  # a face found below this score does not count (lying, turned, covered)
FRAME_MIN = 0.75                  # a frame takes its own size from its face only above this score
AIR = {("w_cast", 2), ("skill2", 2), ("ult", 2), ("ult", 3), ("ult", 4), ("ult", 5), ("ult", 6)}


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def design():
    d = rgba(os.path.join(SRC, "hd", "side.png"))
    ys, xs = np.nonzero(d[..., 3] > 0)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def head_mask():
    """The front's head squares where design_nilah_hd pasted them on side take A, in the cropped design."""
    r0, r1, c0, c1, low, lc = dn.HEAD
    sp = dn.SIDE_HEAD["A"]
    d = design()
    m = np.zeros(d.shape[:2], bool)
    for r in range(r0, r1):
        for c in range(c0, c1):
            if r < low or c >= lc:
                y, x = r + sp["dy"] - CROP[0], c + sp["dx"] - CROP[1]
                if 0 <= y < m.shape[0] and 0 <= x < m.shape[1]:
                    m[y, x] = d[y, x, 3] > 0
    return m


def as_float(a):
    """Colours for matching: transparent squares a fixed mid grey."""
    f = a[..., :3].astype(float) / 255.0
    f[a[..., 3] == 0] = 0.4
    return f


def face_at_1(frame, d):
    """(score, x, y): the design's face found in the frame as it is."""
    r0, r1, c0, c1 = FACE
    t = as_float(d[r0:r1, c0:c1])
    sc = np.mean([match_template(as_float(frame)[..., k], t[..., k]) for k in range(3)], axis=0)
    y, x = np.unravel_index(np.argmax(sc), sc.shape)
    return float(sc[y, x]), int(x), int(y)


def find_face(frame, d):
    """(score, s, x, y): the design's face found in the frame shrunk by 1/s; (x, y) the face box's top-left in the
    frame's own squares."""
    r0, r1, c0, c1 = FACE
    t = as_float(d[r0:r1, c0:c1])
    best = (-1.0, 1.0, 0, 0)
    for s in SCALES:
        w, h = max(1, round(COLS / s)), max(1, round(ROWS / s))
        f = as_float(np.asarray(Image.fromarray(frame).resize((w, h), Image.NEAREST)))
        sc = np.mean([match_template(f[..., k], t[..., k]) for k in range(3)], axis=0)
        y, x = np.unravel_index(np.argmax(sc), sc.shape)
        if sc[y, x] > best[0]:
            best = (float(sc[y, x]), float(s), int(round(x * s)), int(round(y * s)))
    return best


def rescale(frame, s):
    """The frame brought to the design's size: shrunk (or grown) by 1/s round (PIV, the soles' bottom edge)."""
    if abs(s - 1.0) < 1e-6:
        return frame.copy()
    H, W = frame.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    sx = np.round((xx + 0.5 - (PIV + 0.5)) * s + (PIV + 0.5) - 0.5).astype(int)
    sy = np.round((yy + 0.5 - (SOLE + 1)) * s + (SOLE + 1) - 0.5).astype(int)
    ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
    out = np.zeros_like(frame)
    out[ok] = frame[sy[ok], sx[ok]]
    return out


def ground(frame):
    ys = np.nonzero((frame[..., 3] > 0).any(1))[0]
    return np.roll(frame, SOLE - int(ys.max()), axis=0) if len(ys) else frame


def paste_head(frame, d, mask, x, y):
    """The design's head squares pasted with its face box at (x, y) of the frame."""
    ox, oy = x - FACE[2], y - FACE[0]
    out = frame.copy()
    ys, xs = np.nonzero(mask)
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty < ROWS) & (tx >= 0) & (tx < COLS)
    out[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]
    return out


def despeckle(frame, most=6):
    """Pieces of at most `most` squares apart from everything (what is left of Codex's bigger head round the pasted
    one) dropped."""
    from scipy import ndimage
    lab, n = ndimage.label(frame[..., 3] > 0, structure=np.ones((3, 3)))
    out = frame.copy()
    if n > 1:
        sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz <= most:
                out[lab == j] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a before / after sheet per tag here")
    a = ap.parse_args()
    cells = json.load(open(os.path.join(CODEX, "cells.json"), encoding="utf-8"))
    by_tag = {}
    for f in cells["frames"]:
        by_tag.setdefault(f["tag"], []).append(f)
    d, mask = design(), head_mask()
    os.makedirs(OUT, exist_ok=True)
    table, report = {}, []
    raw_all = {tag: [rgba(os.path.join(CODEX, f["file"].replace(".png", "_1x.png"))) for f in frames]
               for tag, frames in by_tag.items()}
    found_all = {tag: [find_face(r, d) for r in raws] for tag, raws in raw_all.items()}
    s_all = float(np.median([m[1] for ms in found_all.values() for m in ms if m[0] >= FRAME_MIN]))
    for tag, frames in by_tag.items():
        raw, found = raw_all[tag], found_all[tag]
        table[tag] = []
        outs = []
        for i, (r, f, m) in enumerate(zip(raw, frames, found)):
            s = m[1] if m[0] >= FRAME_MIN else s_all
            o = rescale(r, s)
            if (tag, i + 1) not in AIR:
                o = ground(o)
            sc, x, y = face_at_1(o, d)
            pasted = sc >= MATCH_MIN and m[0] >= FRAME_MIN
            if pasted:
                o = paste_head(o, d, mask, x, y)
            o = despeckle(o)
            name = f"{tag}_{i + 1}.png"
            Image.fromarray(o).save(os.path.join(OUT, name))
            outs.append((r, o))
            table[tag].append([name, f["ms"]])
            report.append(f"{tag:9s} {i + 1}: face {m[0]:.2f} at s {m[1]:.2f} -> s {s:.2f}; again {sc:.2f}"
                          f"{' HEAD' if pasted else ' (no head)'}")
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            z = 4
            sheet = Image.new("RGBA", (len(outs) * 110 * z, 2 * 120 * z), (255, 0, 255, 255))
            for i, (r, o) in enumerate(outs):
                for j, im in enumerate((r, o)):
                    crop = Image.fromarray(im).crop((PIV - 55, SOLE - 115, PIV + 55, SOLE + 5))
                    sheet.alpha_composite(crop.resize((110 * z, 120 * z), Image.NEAREST), (i * 110 * z, j * 120 * z))
            sheet.convert("RGB").save(os.path.join(a.review, f"import_{tag}.png"))
    with open(os.path.join(OUT, "frames.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    print("\n".join(report))


if __name__ == "__main__":
    main()
