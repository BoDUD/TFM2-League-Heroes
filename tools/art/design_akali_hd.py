#!/usr/bin/env python3
"""Akali's dense design: Codex's picture (tools/art/pack_akali_ppu.py's pack: her wide stance, the ponytail swept up
behind her, League's arm tattoos; the near hand's hooked kama out to the left, the far hand's blade down to the right -
the fourth take, the user: 「就用这张，不用照旧精灵的手」) read back on its own squares, design_syndra_hd's way.

    python tools/art/design_akali_hd.py [--review DIR]

Codex delivered (2026-10-27, Documents/Codex/2026-10-27/https-github-com-bodud-tfm2-patch-2) four takes; the user's is
raw/attempt-04-pixel.png (= its akali-pixel-v3.png, archived as raw/akali-A.png): asked for 11-px squares on
1024 x 1024 with true alpha, it came 1254 x 1254 on ~16-px squares with soft alpha (its HANDOFF says so). Read on its
own squares (design_syndra_hd's snapped lines and palette mode), the outline closed where the read lost it, and kept
as drawn: its rows from the ponytail's top to the soles over her 1x sprite's 40 make the PPU. -> hd/design.png.
With --review DIR: <dir>/akali_ppu_size.png (the design beside this pack's PPU 1.5 heroes and Akali now, as the game
draws them, hd.rs SIZES applied) and <dir>/akali_ppu_closeup.png (Codex's picture | the read).
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
AH.HD = os.path.join(ROOT, "assets", "source", "akali", "hd")
AH.RAW, AH.PITCH = "akali-A.png", (15.0, 16.6)  # its own square (16.0 px; wider lets the columns lock on 17.1)
OLD = 40                        # her 1x idle, the ponytail's top to her soles
PEERS = ["akali", "leesin", "riven", "qiyana"]


GRID = (16.02, 6.0, 4.0)        # her squares: pitch and the first column's / row's line, px
FACE = None                     # rows / columns of the read (the eyes): read by the uniform grid, if the lines miss
CORE = 0.2                      # each square's colour is read from its middle (this much of it off each side)


def native():
    """The picture on its own squares: the palette (48 colours) from a first read on the fitted grid
    (design_ahri_hd.native), every raw pixel snapped to it (Lab), then each square of GRID the palette colour most of
    its middle pixels have (one of the drawing's colours, never a blend of two squares)."""
    first, pal, _ = AH.native()
    a = np.asarray(Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    op = a[..., 3] > 0
    lab = V.srgb2lab(a[op][:, :3].astype(float))
    plab = V.srgb2lab(pal.astype(float))
    idx = np.full(a.shape[:2], -1)
    idx[op] = np.concatenate([((lab[i:i + 200000, None] - plab[None]) ** 2).sum(-1).argmin(1)
                              for i in range(0, len(lab), 200000)])
    # her squares are one even grid (16.02 px both ways; the snapped lines of Syndra's read dropped 2-3 crowded
    # columns and moved the eye): the grid whose squares' middles hold the fewest colours (GRID, searched 15.6-16.5 px)
    pitch, phx, phy = GRID
    xs = [int(round(x)) for x in np.arange(phx, a.shape[1] + 1, pitch)]
    ys = [int(round(y)) for y in np.arange(phy, a.shape[0] + 1, pitch)]
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
    # the face: the snapped lines lean on the hair's and the helmet's edges there and moved the eyes a square apart
    # (the right one shrank to a dot); on the uniform grid laid over the figure's box (its rows / the read's rows)
    # Codex's eye, lash and mouth squares fall on one square each
    if FACE is None:
        return q, pal
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
    ap.add_argument("--review")
    a = ap.parse_args()
    d, ppu = design()
    Image.fromarray(d).save(AH.lp(os.path.join(AH.HD, "design.png")))
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
        cells.append((("now" if h == "akali" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "akali_ppu_size.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("Codex's picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "akali_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
