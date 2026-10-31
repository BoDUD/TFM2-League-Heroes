#!/usr/bin/env python3
"""Miss Fortune's dense design: Codex's picture drawn from tools/art/pack_missfortune_ppu.py's pack (the wide navy
tricorn with its gold trim, the long red hair, the blue eyes, the white bell sleeves, the navy top, the gold belt, the
two gold-mounted pistols, the navy boots) read back on its own squares, design_talon_hd's way.

    python tools/art/design_missfortune_hd.py [--raw missfortune-A.png] [--pitch P] [--review DIR]

Codex delivered (2026-10-31, Documents/Codex/2026-10-31/new-chat-7/outputs/missfortune_ppu_done.zip) missfortune-A.png
(1034 px hat top to soles; its raw/ the same picture): 1254 x 1254 with soft alpha, not cut to 6-px squares. Its
outline is ~9.75-px squares (a ~14.75 coarse one under them), the eyes, lips and gold fittings drawn on finer ones -
so it is read at several pitches (PITCHES) for the user to choose from, the face on the uniform grid at every pitch
(FACES). Syndra's reader: the grid fitted (design_fiora_hd.fit, PITCH), each line snapped to the strongest colour edge
near it, each square the palette colour most of its middle has, the outline closed where the read lost it. Its rows
from the top of the hat to her soles over her 1x sprite's 38 make the PPU.
-> hd/design.png (the default read) or hd/design_<raw>_p<pitch>.png. With --review DIR: <dir>/missfortune_ppu_size*.png
(the design beside Talon, Briar, Jinx and Miss Fortune now, as the game draws them) and
<dir>/missfortune_ppu_closeup*.png (the picture | the read).
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
AH.HD = os.path.join(ROOT, "assets", "source", "missfortune", "hd")
AH.RAW, AH.PITCH = "missfortune-A.png", (9.5, 10.0)    # its own outline squares (~9.75 px)
# per picture: the squares read at (px range) and how far a line may snap to a colour edge (under half a square)
PITCHES = {"missfortune-A.png": {"14.75": ((14.4, 15.1), 6), "9.75": ((9.5, 10.0), 4), "6.5": ((6.3, 6.7), 2)}}
DEFAULT = ("missfortune-A.png", "9.75")
# per picture: the face (x0, y0, x1, y1 px of the picture) read by the uniform grid at every pitch - the snapped lines
# lean on the strong edges round the face there and lose the eyes and the mouth
FACES = {"missfortune-A.png": (520, 430, 660, 630)}
AH.COLOURS = 64                 # (as Talon's)
OLD = 38                        # her 1x idle_base, the top of the hat to her soles
PEERS = ["missfortune", "talon", "briar", "jinx"]


SNAP = 5                        # px a grid line may move to the strongest colour edge near it
FACE = None                     # px box of the picture read by the uniform grid (None: the snapped lines)
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
    # the face: the snapped lines lean on the strong edges round it and lose the eyes and the mouth; on the uniform grid laid over the figure's box (its rows / the read's rows) Codex's eye, lash
    # and mouth squares fall on one square each
    ys_, xs_ = np.nonzero(op)
    by, bx = ys_.min(), xs_.min()
    ky, kx = (ys_.max() + 1 - by) / q.shape[0], (xs_.max() + 1 - bx) / q.shape[1]
    fx0, fy0, fx1, fy1 = FACE
    r0, r1 = int((fy0 - by) / ky), int(np.ceil((fy1 - by) / ky))
    c0, c1 = int((fx0 - bx) / kx), int(np.ceil((fx1 - bx) / kx))
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
        cells.append((("now" if h == "missfortune" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"missfortune_ppu_size{tail}.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, f"missfortune_ppu_closeup{tail}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
