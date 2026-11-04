#!/usr/bin/env python3
"""Kha'Zix's dense design: Codex's picture drawn from tools/art/pack_khazix_ppu.py's pack (the blue-violet insect crouched
forward in his final form, the pale green wings, the teal antennae, the scythe claws with their pale pink blades, the
copper clawed feet) read back on its own squares, design_ryze_hd's way.

    python tools/art/design_khazix_hd.py [--pitch P] [--review DIR]

Codex delivered (2026-11-05, Documents/Codex/2026-11-04/new-chat/outputs/khazix_blitzcrank_lillia_jhin_ppu_review.zip,
the four of this PR together) khazix-ppu/khazix-A.png, byte for byte its raw generation: 1254 x 1254 with soft alpha,
not cut to 6-px squares, kept as hd/raw/khazix-A.png. Its squares drift (no one grid fits the whole picture); its
outline runs ~20 px thick, two of its squares - so it is read at several pitches (PITCHES) for the user to choose from,
the face on the same snapped lines (FACES empty: each square's mean dulled his red maw to dark red and spread his pale
eye); his thin antennae laid on the grid along their skeletons (THIN: the squares cut them into dashes). Syndra's
reader: the grid fitted (design_fiora_hd.fit, PITCH), each line snapped to the strongest colour edge near it, each
square the palette colour most of its middle has, the outline closed where the read lost it. Its rows from the tips of
his antennae to his soles over his 1x sprite's 37 make the PPU (the user, 2026-11-05: 「接下来重做螳螂 机器人 莉莉娅 烬」).
-> hd/design.png (the default read) or hd/design_<raw>_p<pitch>.png. With --review DIR: <dir>/khazix_ppu_size*.png (the
design beside Diana, Ryze, Master Yi and his sprite now, as the game draws them) and <dir>/khazix_ppu_closeup*.png (the
picture | the read).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_ahri_hd as AH  # noqa: E402
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402
import strips as G  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
AH.HD = os.path.join(ROOT, "assets", "source", "khazix", "hd")
AH.RAW, AH.PITCH = "khazix-A.png", (13.6, 14.0)    # the default read (13.8 px) until the user picks
# per picture: the squares read at (px range) and how far a line may snap to a colour edge (under half a square)
PITCHES = {"khazix-A.png": {"13.8": ((13.6, 14.0), 6), "11.3": ((11.1, 11.5), 5), "17": ((16.8, 17.2), 8)}}
DEFAULT = ("khazix-A.png", "13.8")
# per picture: the face (x0, y0, x1, y1 px of the picture) read by the uniform grid at every pitch - none here: tried on
# (740, 580, 900, 730), each square's mean dulled his red maw to dark red and spread his pale eye; the snapped lines
# keep them (Kennen's and Lissandra's way)
FACES = {}
# per picture: thin lines the squares cut into dashes, the line's colour as (r, g, b) bounds - each component of that
# colour at most THIN_WIDTH px wide on average and at least THIN_LENGTH px long is laid on the grid along its skeleton
# (thin_lines()): his antennae, ~8 px of teal inside their dark outline, under one of Codex's ~10-px squares - on
# squares of 11-17 px most of each square's middle is the outline and they read as dashes
THIN = {"khazix-A.png": ((0, 110), (150, 255), (160, 255))}
THIN_WIDTH, THIN_LENGTH = 10, 100
AH.COLOURS = 64                 # (as Talon's)
OLD = 37                        # his 1x idle_base, the tips of his antennae to his soles
PEERS = ["khazix", "diana", "ryze", "masteryi"]


SNAP = 5                        # px a grid line may move to the strongest colour edge near it
FACE = None                     # px box of the picture read by the uniform grid (None: the snapped lines)
CORE = 0.2                      # each square's colour is read from its middle (this much of it off each side)
FACE_DARK = 0.5                 # in the face, a square this much near-black is a dark line's (native())
FACE_GLOW = 0.15                # in the face, a square this much glowing pale yellow is the eye (native()): the mean
                                # with the dark red maw and the violet head round it dulls small glowing eyes to dark
                                # dots (Aatrox's fix, the user: 「剑魔的头看起来只看后面」)


def lines(e, pitch, phase, n):
    """The square boundaries along one axis: the fitted grid (pitch, phase), each line moved to the strongest colour
    edge within SNAP px of it - Codex's squares drift up to half a square off one grid across the picture."""
    out = []
    for x in np.arange(phase, n, pitch):
        c = int(round(x))
        lo, hi = max(0, c - SNAP), min(n, c + SNAP + 1)
        w = e[lo:hi]
        best = lo + int(np.argmax(w - 0.01 * np.abs(np.arange(lo, hi) - c))) if w.size and w.max() > 0 else c
        if out and best - out[-1] < pitch * 0.6:
            best = c                    # (two lines on one edge: this one stays where the grid puts it)
        if not out or best - out[-1] >= pitch * 0.4:
            out.append(best)
    return out


def thin_lines(q, a, op, idx, pal, xs, ys):
    """THIN's lines laid on the grid in place: each thin component of the line colour skeletonised, the square under
    every skeleton pixel the palette colour most of the component has - an unbroken line one square wide."""
    (r0, r1), (g0, g1), (b0, b1) = THIN[AH.RAW]
    rgb = a[..., :3].astype(int)
    m = op & (rgb[..., 0] >= r0) & (rgb[..., 0] <= r1) & (rgb[..., 1] >= g0) & (rgb[..., 1] <= g1) & \
        (rgb[..., 2] >= b0) & (rgb[..., 2] <= b1)
    lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
    for k, sl in enumerate(ndimage.find_objects(lbl), 1):
        c = lbl[sl] == k
        sk = skeletonize(c)
        if sk.sum() < THIN_LENGTH or c.sum() > THIN_WIDTH * sk.sum():
            continue
        col = pal[np.bincount(idx[sl][c], minlength=len(pal)).argmax()]
        sy, sx = np.nonzero(sk)
        j = np.searchsorted(ys, sy + sl[0].start, side="right") - 1
        i = np.searchsorted(xs, sx + sl[1].start, side="right") - 1
        ok = (j >= 0) & (j < q.shape[0]) & (i >= 0) & (i < q.shape[1])
        q[j[ok], i[ok], :3] = col
        q[j[ok], i[ok], 3] = 255


def native():
    """The picture on its own squares: the palette (48 colours) from a first read on the fitted grid
    (design_ahri_hd.native), every raw pixel snapped to it (Lab), then each square - between the snapped lines - the
    palette colour most of its middle pixels have (one of the drawing's colours, never a blend of two squares)."""
    first, pal, _ = AH.native()
    a = np.asarray(Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    op = a[..., 3] > 0
    lab = V.srgb2lab(a[op][:, :3].astype(float))
    plab = V.srgb2lab(pal.astype(float))
    idx = np.full(a.shape[:2], -1)
    idx[op] = np.concatenate([((lab[i:i + 200000, None] - plab[None]) ** 2).sum(-1).argmin(1)
                              for i in range(0, len(lab), 200000)])
    FD.PITCH = AH.PITCH
    (px, phx), (py, phy) = FD.fit(a, op, 1), FD.fit(a, op, 0)
    xs = lines(FD.RG.profile(a, op, 1), px, phx, a.shape[1])
    ys = lines(FD.RG.profile(a, op, 0), py, phy, a.shape[0])
    q = np.zeros((len(ys) - 1, len(xs) - 1, 4), np.uint8)
    for j in range(len(ys) - 1):
        y0, y1 = ys[j], ys[j + 1]
        dy = int((y1 - y0) * CORE)
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            dx = int((x1 - x0) * CORE)
            win = idx[y0 + dy:y1 - dy, x0 + dx:x1 - dx].ravel()
            if (win >= 0).sum() * 2 <= win.size:
                continue
            q[j, i, :3] = pal[np.bincount(win[win >= 0], minlength=len(pal)).argmax()]
            q[j, i, 3] = 255
    if AH.RAW in THIN:
        thin_lines(q, a, op, idx, pal, xs, ys)
    q = FD.crop(q)
    if FACE is None:
        return q, pal
    # the face: the snapped lines lean on the strong edges round it and lose the eyes and the mouth; on the uniform
    # grid laid over the figure's box (its rows / the read's rows) each square the palette colour nearest the mean of
    # all its pixels (Lab) - Codex's ~8-10 px strokes (the eyes, the lashes, the mouth, the grin's teeth) run across
    # squares, under half of each, and a majority loses them - or, past FACE_DARK of it near-black, the dark colour
    # nearest that mean (the line itself)
    ys_, xs_ = np.nonzero(op)
    by, bx = ys_.min(), xs_.min()
    ky, kx = (ys_.max() + 1 - by) / q.shape[0], (xs_.max() + 1 - bx) / q.shape[1]
    fx0, fy0, fx1, fy1 = FACE
    labs = np.zeros(a.shape[:2] + (3,))
    labs[op] = lab
    black = op & (a[..., :3].max(-1) < 70)
    rgb_ = a[..., :3].astype(int)
    glow = op & (rgb_[..., 0] >= 220) & (rgb_[..., 1] >= 200) & (rgb_[..., 2] >= 140)   # his pale glowing eye
    dark = np.flatnonzero(pal.max(-1) < 70)             # the palette's near-black (outline) colours
    r0, r1 = int((fy0 - by) / ky), int(np.ceil((fy1 - by) / ky))
    c0, c1 = int((fx0 - bx) / kx), int(np.ceil((fx1 - bx) / kx))
    for j in range(r0, r1):
        for i in range(c0, c1):
            y0, y1 = int(by + j * ky), int(np.ceil(by + (j + 1) * ky))
            x0, x1 = int(bx + i * kx), int(np.ceil(bx + (i + 1) * kx))
            w = op[y0:y1, x0:x1]
            if w.sum() * 2 <= w.size:
                q[j, i] = 0
                continue
            g = glow[y0:y1, x0:x1] & w
            if g.sum() >= FACE_GLOW * w.sum():         # an eye: its own glowing colour, not the mean with the black round it
                m = labs[y0:y1, x0:x1][g].mean(0)
                q[j, i, :3] = pal[((plab - m) ** 2).sum(-1).argmin()]
                q[j, i, 3] = 255
                continue
            m = labs[y0:y1, x0:x1][w].mean(0)
            near = dark if black[y0:y1, x0:x1].sum() >= FACE_DARK * w.sum() else np.arange(len(pal))
            q[j, i, :3] = pal[near[((plab[near] - m) ** 2).sum(-1).argmin()]]
            q[j, i, 3] = 255
    return q, pal


def read():
    """Codex's picture on its own squares, cut to colours, its outline closed, cropped - as Codex drew it."""
    q, pal = native()
    # where the read lost Codex's outline: closed again in the outline colour (strips.complete_outline)
    out = AH.outline_of(pal)
    q = G.complete_outline(q, color=out)[0]
    # and the dark squares on the rim (the outline averaged with what it rings) the outline colour
    op = q[..., 3] > 0
    rim = op & ~ndimage.binary_erosion(op, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    q[rim & (q[..., :3].astype(int).sum(-1) < 170), :3] = out
    ys, xs = np.nonzero(q[..., 3])
    return q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def design():
    q = read()
    return q, q.shape[0] / OLD


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT[0], choices=sorted(PITCHES))
    ap.add_argument("--pitch", help="one of the picture's PITCHES (default: its first)")
    ap.add_argument("--review")
    a = ap.parse_args()
    global SNAP, FACE
    p = a.pitch or (DEFAULT[1] if a.raw == DEFAULT[0] else next(iter(PITCHES[a.raw])))
    FACE = FACES.get(a.raw)
    AH.RAW = a.raw
    AH.PITCH, SNAP = PITCHES[a.raw][p]
    d, ppu = design()
    stem = "design" if (a.raw, p) == DEFAULT else f"design_{a.raw[:-4]}_p{p}"
    tail = "" if stem == "design" else stem[len("design"):]
    Image.fromarray(d).save(AH.lp(os.path.join(AH.HD, stem + ".png")))
    print(f"design {d.shape[1]}x{d.shape[0]} = PPU {ppu:.3f} at {OLD} rows, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    from preview_dense import SIZES
    os.makedirs(a.review, exist_ok=True)
    cells = [(f"new: {d.shape[0] / ppu:.1f}px (PPU {ppu:.2f})", FD.shown(Image.fromarray(d), ppu, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        k = SIZES.get(h, 1.0)
        cells.append((("now" if h == "khazix" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"khazix_ppu_size{tail}.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, f"khazix_ppu_closeup{tail}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
