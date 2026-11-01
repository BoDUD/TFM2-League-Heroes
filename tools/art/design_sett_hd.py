#!/usr/bin/env python3
"""Sett's dense design: Codex's picture drawn from tools/art/pack_sett_ppu.py's pack (the spiky red hair and beast
ears, the tanned face with its gold eyes, the violet fur mantle, the gold collar and beast-head clasps, the bare
muscled chest, the open wine-red coat with its gold trim, the white trousers, the gold gauntlets) read back on its own
squares, design_senna_hd's way.

    python tools/art/design_sett_hd.py [--raw sett-A.png|sett-v1.png] [--pitch P] [--review DIR]

Codex delivered (2026-11-01, Documents/Codex/2026-11-01/new-chat-6/outputs/sett_ppu_done.zip) sett-A.png (its second
generation: 1164 px hair top to soles) and raw/sett-generation-01.png as sett-v1.png (its first, 961 px): 1254 x 1254
each with soft alpha, not cut to 6-px squares. A's outline is ~15.5-px squares (its face and gold drawn on finer
ones), v1's ~9.8 - so each is read at several pitches (PITCHES) for the user to choose from, the face on the uniform
grid at every pitch (FACES). Syndra's reader: the grid fitted (design_fiora_hd.fit, PITCH), each line snapped to the
strongest colour edge near it, each square the palette colour most of its middle has, the outline closed where the
read lost it. Its rows from the top of his hair to his soles over his 1x sprite's 42 make the PPU.
-> hd/design.png (the default read) or hd/design_<raw>_p<pitch>.png. With --review DIR: <dir>/sett_ppu_size*.png (the
design beside Thresh, Talon, Jinx and Sett now, as the game draws them) and <dir>/sett_ppu_closeup*.png (the picture |
the read).
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
AH.HD = os.path.join(ROOT, "assets", "source", "sett", "hd")
AH.RAW, AH.PITCH = "sett-A.png", (10.15, 10.55)    # its own outline squares (~10.35 px)
# per picture: the squares read at (px range) and how far a line may snap to a colour edge (under half a square)
PITCHES = {"sett-A.png": {"15.5": ((15.3, 15.7), 6), "10.35": ((10.15, 10.55), 4), "7.75": ((7.6, 7.9), 3)},
           "sett-v1.png": {"14.7": ((14.5, 14.9), 6), "9.8": ((9.6, 10.0), 4), "7.35": ((7.2, 7.5), 3)}}
DEFAULT = ("sett-A.png", "10.35")
# per picture: the face (x0, y0, x1, y1 px of the picture) read by the uniform grid at every pitch - the snapped lines
# lean on the strong edges round the face there and lose the eyes and the mouth
FACES = {"sett-A.png": (560, 320, 770, 490), "sett-v1.png": (560, 380, 730, 520)}
AH.COLOURS = 64                 # (as Talon's)
OLD = 42                        # his 1x idle_base, the top of his hair to his soles
PEERS = ["sett", "thresh", "talon", "jinx"]


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
        cells.append((("now" if h == "sett" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"sett_ppu_size{tail}.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, f"sett_ppu_closeup{tail}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
