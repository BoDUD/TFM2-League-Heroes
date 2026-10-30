#!/usr/bin/env python3
"""Briar's dense design: Codex's picture drawn from tools/art/pack_briar_ppu.py's pack (the dark iron pillory with its
gold studs, spikes and red gem locked round her neck and both wrists, the white hair touched with pink, the pale blue
eyes, the black outfit splashed with red, the bare legs with black shin wraps) read back on its own squares,
design_sona_hd's way.

    python tools/art/design_briar_hd.py [--raw briar-A.png|briar-pass2.png] [--pitch P] [--review DIR]

Codex delivered (2026-10-30, Documents/Codex/2026-10-30/new-chat-7/outputs/briar_ppu_done.zip) briar-A.png (its first
pass, filling the canvas: 1157 px pillory top to soles) and raw/briar-pass2.png (its layout retry, 964 px): 1254 x 1254
each with soft alpha, not cut to 7-px squares. As Sona's picture, their outlines and pillory are coarse squares (~12 /
~10 px) but the eyes, lashes, fingers and studs are drawn on half and third squares - so each is read at several
pitches (PITCHES) for the user to choose from: A on ~8.5-px squares, PPU 2.94 (the user, 2026-10-30: 「用2.13就行」,
then 「算了用2.94吧」); pass2 on its own ~10-px squares (2.13) kept with its eyes and mouth on the uniform grid
(FACES: the snapped lines lean on the lashes and left the eyes one blue square each). Syndra's reader: the grid fitted (design_fiora_hd.fit, PITCH), each line
snapped to the strongest colour edge near it, each square the palette colour most of its middle has, the outline closed
where the read lost it. Its rows from the top of the pillory to her soles over her 1x sprite's 46 make the PPU.
-> hd/design.png (the default read) or hd/design_<raw>_p<pitch>.png. With --review DIR: <dir>/briar_ppu_size*.png (the
design beside this pack's PPU 2.2 heroes and Briar now, as the game draws them) and <dir>/briar_ppu_closeup*.png (the
picture | the read).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_ahri_hd as AH  # noqa: E402
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402
import strips as G  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
AH.HD = os.path.join(ROOT, "assets", "source", "briar", "hd")
AH.RAW, AH.PITCH = "briar-A.png", (8.2, 8.8)    # about two thirds of its outline squares (~8.5 px)
# per picture: the squares read at (px range) and how far a line may snap to a colour edge (under half a square)
PITCHES = {"briar-A.png": {"12": ((11.2, 13.0), 5), "8.5": ((8.2, 8.8), 3), "6": ((5.7, 6.3), 2)},
           "briar-pass2.png": {"10": ((9.5, 10.2), 4), "6.5": ((6.3, 6.8), 2)}}
DEFAULT = ("briar-A.png", "8.5")
FACES = {("briar-pass2.png", "10"): (34, 49, 40, 60)}     # rows / columns of the read (the eyes and the mouth) read by the uniform grid
AH.COLOURS = 64                 # (as Kayle's: room for the iron greys, the golds, the reds and the pinks)
OLD = 46                        # her 1x idle_base, the top of the pillory to her soles
PEERS = ["briar", "jinx", "ahri", "annie"]


SNAP = 5                        # px a grid line may move to the strongest colour edge near it
FACE = None                     # rows / columns of the read read by the uniform grid (None: the snapped lines)
CORE = 0.2                      # each square's colour is read from its middle (this much of it off each side)


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
    q = FD.crop(q)
    if FACE is None:
        return q, pal
    # the face: the snapped lines lean on the hair's and the helmet's edges there and moved the eyes a square apart
    # (the right one shrank to a dot); on the uniform grid laid over the figure's box (its rows / the read's rows)
    # Codex's eye, lash and mouth squares fall on one square each
    ys_, xs_ = np.nonzero(op)
    by, bx = ys_.min(), xs_.min()
    ky, kx = (ys_.max() + 1 - by) / q.shape[0], (xs_.max() + 1 - bx) / q.shape[1]
    r0, r1, c0, c1 = FACE
    for j in range(r0, r1):
        for i in range(c0, c1):
            y0, y1 = by + j * ky, by + (j + 1) * ky
            x0, x1 = bx + i * kx, bx + (i + 1) * kx
            win = idx[int(y0 + (y1 - y0) * 0.3):int(y1 - (y1 - y0) * 0.3) + 1,
                      int(x0 + (x1 - x0) * 0.3):int(x1 - (x1 - x0) * 0.3) + 1].ravel()
            if (win >= 0).sum() * 2 <= win.size:
                q[j, i] = 0
                continue
            q[j, i, :3] = pal[np.bincount(win[win >= 0], minlength=len(pal)).argmax()]
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
    FACE = FACES.get((a.raw, p))
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
        cells.append((("now" if h == "briar" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"briar_ppu_size{tail}.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, f"briar_ppu_closeup{tail}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
