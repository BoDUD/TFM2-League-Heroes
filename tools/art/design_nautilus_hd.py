#!/usr/bin/env python3
"""Nautilus's dense design: Codex's picture drawn from tools/art/pack_nautilus_ppu.py's pack (the orange diving helmet
with its dark visor and two red eyes, the grey anchor held in his fist with its hooks over his head, the grey iron
armour with its teal seams, the massive iron fists, the bronze-orange boots) read back on its own squares,
design_khazix_hd's way.

    python tools/art/design_nautilus_hd.py [--pitch P] [--review DIR]

Codex delivered (2026-11-05, Documents/Codex/2026-11-05/new-chat/outputs/ppu_all_6_done.zip, the six of this PR
together) nautilus-ppu/raw/generation-02.png (Codex itself turned down generation-01: the anchor's grip was empty) - its
raw generation: 1254 x 1254 with soft alpha, not cut to 6-px squares, kept as hd/raw/nautilus-A.png (Codex's own
nautilus-A.png is that resampled to 6 px on a 64-colour palette: not read). Its squares drift (no one grid fits the
whole picture; they run ~9-10 px) and its outline is about two of them thick - so it is read at three pitches (PITCHES:
10.58 px ~ PPU 2.2, 8.75 px ~ PPU 2.65, 12.85 px ~ PPU 1.8) for the user to choose from, the face on the same snapped
lines (FACES empty: batch 4 found each square's mean dulls small eyes into what rings them). Syndra's reader: the grid
fitted (design_fiora_hd.fit, PITCH), each line snapped to the strongest colour edge near it, each square the palette
colour most of its middle has, the outline closed where the read lost it. Its rows from the top of his anchor to his
soles over his 1x sprite's 51 make the PPU (the user, 2026-11-05: 「下面重做凯隐 维克托 永恩 泰坦」).
-> hd/design.png (the default read) or hd/design_<raw>_p<pitch>.png. With --review DIR: <dir>/nautilus_ppu_size*.png
(the design beside Diana, Ryze, Master Yi and his sprite now, as the game draws them) and
<dir>/nautilus_ppu_closeup*.png (the picture | the read).
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
AH.HD = os.path.join(ROOT, "assets", "source", "nautilus", "hd")
AH.RAW, AH.PITCH = "nautilus-A.png", (10.52, 10.64)    # the default read (10.58 px, PPU ~2.2) until the user picks
# per picture: the squares read at (px range) and how far a line may snap to a colour edge (under half a square)
PITCHES = {"nautilus-A.png": {"10.58": ((10.52, 10.64), 5), "8.75": ((8.69, 8.81), 4), "12.85": ((12.79, 12.91), 6)}}
DEFAULT = ("nautilus-A.png", "10.58")
# per picture: the face (x0, y0, x1, y1 px of the picture) read by the uniform grid at every pitch - none here: each
# square's mean dulls small eyes into what rings them (batch 4: Kha'Zix's maw, Blitzcrank's and Lillia's eyes); the
# snapped lines keep them (Kennen's and Lissandra's way)
FACES = {}
# per picture: thin lines the squares cut into dashes, the line's colour as (r, g, b) bounds, laid on the grid along
# their skeletons (thin_lines()) - none here
THIN = {}
THIN_WIDTH, THIN_LENGTH = 10, 100
AH.COLOURS = 64                 # (as Talon's)
OLD = 51                        # his 1x idle_base, the top of his anchor to his soles
PEERS = ["nautilus", "diana", "ryze", "masteryi"]


SNAP = 5                        # px a grid line may move to the strongest colour edge near it
FACE = None                     # px box of the picture read by the uniform grid (None: the snapped lines)
CORE = 0.2                      # each square's colour is read from its middle (this much of it off each side)
FACE_DARK = 0.5                 # in the face, a square this much near-black is a dark line's (native())
FACE_GLOW = 0.15                # in the face, a square this much glowing red is the eyes (native()): the mean with the
                                # dark visor round them dulls small glowing eyes to dark dots (Aatrox's fix, the user:
                                # 「剑魔的头看起来只看后面」)


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
    glow = op & (rgb_[..., 0] >= 200) & (rgb_[..., 1] <= 90) & (rgb_[..., 2] <= 80)   # his red eyes
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
        cells.append((("now" if h == PEERS[0] else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"nautilus_ppu_size{tail}.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, f"nautilus_ppu_closeup{tail}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
