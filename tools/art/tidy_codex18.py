#!/usr/bin/env python3
"""Tidy Codex's step-2 redraw of the 18 heroes (model_strips_18: every strip drawn from the approved design) into
the native strips.

    python tools/art/tidy_codex18.py <hero> <Codex's delivery folder>

Codex delivers <hero>_<tag>.png for every tag of assets/source/native/<hero>_cells.json, on the same cells, every
game pixel an 8x8 block, the design's palette and its head pasted into every frame. One thing is fixed here on the
game pixels before the strips are written to assets/source/native/: the doubled outline. A study of the LoL Reborn
pack (oppi) against ours found our designs use black as the shadow tone, so the ring just inside the 1-px outline
is black as well (inner-ring black 0.58 against oppi's 0.30 and the base game's 0.20), and hair, cloth and thin
props melt into the outline at game size. Per frame:
  - a near-black pixel on the silhouette's edge with at most one opaque 4-neighbour (an outline spur) goes;
    coloured pixels are never removed (chains, braids and wand tips are 1 px wide);
  - a near-black pixel just inside the edge takes the darkest of its lighter 8-neighbours (at least two of them):
    the material's own dark shade instead of a second ring of black;
  - a lone pixel inside an area (its colour on none of its four neighbours, three or four of which share one
    colour) takes that colour: the specks of noise (Fiddlesticks's red and grey dots in his dark wood). Lines stay:
    a pixel of a chain, a crack or an edge has at least two neighbours of its own colour or of different ones.
The face round the eyes (EYE_COLOURS) is left alone. Then run import_native.py --hero <hero>.
Fiddlesticks and Kayle (merged before the 18) are cleaned the same way in place: their own
assets/source/native folder is the delivery.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
DARK = 40                       # luma under this is "black" (outline, black shadow)
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
# the colours of each hero's eyes in Codex's delivery (Thresh's green glints are also on his hood flame and lantern:
# only the pixels round the eyes are kept, see protected())
EYE_COLOURS = {"thresh": [(13, 200, 78), (4, 71, 29)],
               # merged before the 18 (PRs #27 and #26), cleaned the same way in place: run with their own
               # assets/source/native folder as the delivery
               "fiddlesticks": [(200, 224, 96)], "kayle": [(226, 138, 8)],
               "leona": [(186, 88, 30)], "janna": [(3, 51, 207)],
               "ekko": [(213, 125, 34)], "darius": [(255, 247, 238)],
               "leesin": [(212, 34, 50)]}
# heroes whose delivered faces were drawn anew in every frame (Codex: "not a pixel copy of the head"): the design's
# face - eyes, brows, cheeks and the fringe right round them - goes back into every frame where the head is found.
# head: the design's head box on its 128x128 canvas (<hero>_native.png), matched in every frame by colour; patch: the
# face pasted there; iris: the eyes' colour and the eye-only shade it becomes in every frame (import_native.py's EYES
# steadies the head on it; the design's iris is also on the hair)
FACES = {"leona": {"head": (42, 58, 66, 74), "patch": (53, 68, 61, 73), "iris": ((184, 86, 28), (186, 88, 30))},
         # Darius's eye white is already an eye-only shade in the design (#FFF7EE)
         "darius": {"head": (52, 55, 65, 66), "patch": (55, 60, 64, 65), "iris": ((255, 247, 238), (255, 247, 238))},
         # Lee Sin's eyes are under the blindfold: the skull top, the band across the face (its own red #D42232 in the
         # design) and the face under it go back; matched on that face alone (his braid knot changes every frame)
         "leesin": {"head": (57, 62, 69, 72), "patch": (57, 63, 69, 72), "iris": ((212, 34, 50), (212, 34, 50))}}
FACE_OK = 120                   # mean colour distance over the head box above which a frame's head is not found
# deliveries whose frames Codex centred in their cells (its manifest's atlas pivot) instead of standing them on our
# pivots: every frame whose face is found goes sideways so that its eyes stand on League's head joint of that frame
# (the cells table's "head"), as in the design; a frame without a face keeps Codex's place round the atlas pivot,
# moved to ours. Up and down stay Codex's: the soles are on the feet line already.
PLACE_BY_HEAD = {"darius", "leesin"}


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    if a.shape[0] % Z or a.shape[1] % Z:
        sys.exit(f"{path}: {a.shape[1]}x{a.shape[0]} is not a multiple of {Z}")
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    if not set(np.unique(out[..., 3])) <= {0, 255}:
        sys.exit(f"{path}: semi-transparent pixels")
    return out


def lum(rgb):
    rgb = rgb.astype(float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def protected(a, colours):
    """The face: from 2 rows over the eyes to 4 rows under them, 3 columns either side (sockets, lashes, brows and
    the mouth - Kayle's mouth is one lone red pixel)."""
    op = a[..., 3] > 0
    m = np.zeros(op.shape, bool)
    for c in colours:
        m |= op & np.all(a[..., :3] == np.array(c, np.uint8), -1)
    grown = m.copy()
    for dy in range(-2, 5):
        for dx in range(-3, 4):
            grown |= shifted(m, dy, dx)
    return grown


def one_outline(a, colours=()):
    """One frame at game size: outline spurs off, the second ring of black turned into the material's dark shade."""
    a = a.copy()
    keep = protected(a, colours)
    for _ in range(2):
        op = a[..., 3] > 0
        cnt = sum(shifted(op, dy, dx).astype(int) for dy, dx in N4)
        a[op & (lum(a[..., :3]) < DARK) & (cnt <= 1) & ~keep] = 0
    op = a[..., 3] > 0
    L = lum(a[..., :3])
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    ring2 = np.zeros_like(op)
    for dy, dx in N4:
        ring2 |= shifted(edge, dy, dx)
    ring2 &= op & ~edge & (L < DARK) & ~keep
    H, W = op.shape
    out = a.copy()
    for y, x in zip(*np.nonzero(ring2)):
        cols = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N8
                if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and L[y + dy, x + dx] >= DARK]
        if len(cols) >= 2:
            out[y, x] = min(cols, key=lambda c: (lum(np.array(c[:3])), -cols.count(c)))
    return despeckle(out, keep)


def despeckle(a, keep):
    """Lone pixels inside an area take the colour of the area (3 or 4 of the 4 neighbours share it)."""
    op = a[..., 3] > 0
    H, W = op.shape
    out = a.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or keep[y, x]:
                continue
            nb = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N4]
            me = tuple(int(v) for v in a[y, x])
            if me in nb or any(n[3] == 0 for n in nb):
                continue
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 3:
                out[y, x] = best
    return out


def find_head(frame, head, guess, reach=(16, 14)):
    """(mean colour distance, x, y) of the best place for the design's head box in the frame near guess (x, y)."""
    m = head[..., 3] > 0
    hh, hw = head.shape[:2]
    H, W = frame.shape[:2]
    best = (1e9, 0, 0)
    for y in range(max(0, guess[1] - reach[1]), min(H - hh, guess[1] + reach[1]) + 1):
        for x in range(max(0, guess[0] - reach[0]), min(W - hw, guess[0] + reach[0]) + 1):
            win = frame[y:y + hh, x:x + hw]
            d = np.sqrt(((win[..., :3].astype(float) - head[..., :3]) ** 2).sum(-1))
            d[win[..., 3] == 0] = 255
            s = float(d[m].mean())
            if s < best[0]:
                best = (s, x, y)
    return best


def paste_face(frame, design, face, guess):
    """The design's face patch pasted where the head is found, the iris in its eye-only shade; (score, x, y) or
    None when the head is not found (turned away, lying)."""
    x0, y0, x1, y1 = face["head"]
    px0, py0, px1, py1 = face["patch"]
    head = design[y0:y1 + 1, x0:x1 + 1]
    s, x, y = find_head(frame, head, guess)
    if s > FACE_OK:
        return None
    patch = design[py0:py1 + 1, px0:px1 + 1].copy()
    iris, shade = face["iris"]
    patch[np.all(patch[..., :3] == np.array(iris, np.uint8), -1) & (patch[..., 3] > 0), :3] = shade
    ox, oy = x + px0 - x0, y + py0 - y0
    win = frame[oy:oy + patch.shape[0], ox:ox + patch.shape[1]]
    m = patch[..., 3] > 0
    win[m] = patch[m]
    return s, x, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero")
    ap.add_argument("delivery")
    a = ap.parse_args()
    h = a.hero
    with open(G.lp(os.path.join(SRC, f"{h}_cells.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cw, ch = spec["cell"]
    colours = EYE_COLOURS.get(h, [])
    face = FACES.get(h)
    if face:
        design = blocks(os.path.join(SRC, f"{h}_native.png"))
        idle = blocks(os.path.join(a.delivery, f"{h}_idle.png"))[:ch, :cw]
        x0, y0, x1, y1 = face["head"]
        s, hx, hy = find_head(idle, design[y0:y1 + 1, x0:x1 + 1], (cw // 2, ch // 2), (cw // 2, ch // 2))
        p0 = spec["tags"]["idle"][0]["pivot"]
        off = (hx - p0[0], hy - p0[1])          # the head box's corner from the standing point in the design
        print(f"{h}: design head in idle frame 1 at {hx},{hy} (distance {s:.1f})")
    place = h in PLACE_BY_HEAD
    if place:
        shade = np.array(face["iris"][1], np.uint8)
        eye_k = eye_x(idle, shade) - spec["tags"]["idle"][0]["head"][0]   # the eyes from League's head joint
    for tag, frames in spec["tags"].items():
        new = blocks(os.path.join(a.delivery, f"{h}_{tag}.png"))
        old = blocks(os.path.join(SRC, f"{h}_{tag}.png"))
        if new.shape != old.shape:
            sys.exit(f"{h}_{tag}.png: {new.shape[1]}x{new.shape[0]} game pixels, the cells need "
                     f"{old.shape[1]}x{old.shape[0]}")
        atlas = atlas_pivots(a.delivery, h, tag) if place else None
        out = new.copy()
        cols = new.shape[1] // cw
        found, moved = [], []
        for k, fr in enumerate(frames):
            y, x = (k // cols) * ch, (k % cols) * cw
            cell = out[y:y + ch, x:x + cw]
            if face:
                ap = atlas[k] if atlas else fr["pivot"]
                r = paste_face(cell, design, face, (ap[0] + off[0], ap[1] + off[1]))
                found.append("-" if r is None else f"{r[0]:.0f}")
                if place and tag != "idle":
                    ex = eye_x(cell, shade) if r is not None else None
                    dx = (round(fr["head"][0] + eye_k - ex) if ex is not None
                          else fr["pivot"][0] - (ap[0] if atlas else fr["pivot"][0]))
                    cell[:], dx = slide(cell, dx), dx
                    moved.append(f"{dx:+d}")
            out[y:y + ch, x:x + cw] = one_outline(cell, colours)
        n = int((out != new).any(-1).sum())
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, f"{h}_{tag}.png")))
        print(f"{h}_{tag}.png: {n} pixels changed" + (f"; face pasted (head distance per frame, - = not found): "
                                                     f"{' '.join(found)}" if face else "")
              + (f"; moved sideways {' '.join(moved)}" if moved else ""))


def eye_x(frame, shade):
    """The middle column of the eye-only shade in a frame, or None."""
    m = (frame[..., 3] > 0) & np.all(frame[..., :3] == shade, -1)
    xs = np.nonzero(m)[1]
    return float(xs.mean()) if len(xs) else None


def atlas_pivots(delivery, h, tag):
    """The per-frame pivots Codex's manifest gives for its centred frames, or None."""
    p = os.path.join(delivery, f"{h}_{tag}_manifest.json")
    if not os.path.exists(p):
        return None
    m = json.load(open(p, encoding="utf-8-sig"))
    return [f["pivot"] for f in m.get("atlas", {}).get("frames", [])] or None


def slide(cell, dx):
    """The cell's content moved dx columns (no further than keeps it inside the cell)."""
    xs = np.nonzero(cell[..., 3].any(0))[0]
    if not len(xs):
        return cell.copy()
    dx = max(-int(xs[0]), min(int(dx), cell.shape[1] - 1 - int(xs[-1])))
    out = np.zeros_like(cell)
    if dx >= 0:
        out[:, dx:] = cell[:, :cell.shape[1] - dx]
    else:
        out[:, :dx] = cell[:, -dx:]
    return out


if __name__ == "__main__":
    main()
