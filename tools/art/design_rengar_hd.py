#!/usr/bin/env python3
"""Rengar's dense design: Codex's picture (tools/art/pack_rengar_ppu.py's pack, traced from his sprite now - the hunched
stalking crouch) read back on its own squares, design_leesin_hd's way.

    python tools/art/design_rengar_hd.py [--review DIR]

Codex delivered (2026-10-27, Documents/Codex/2026-10-27/new-chat-6) raw/rengar-selected-original.png (archived as
hd/raw/rengar-A.png): asked for 11-px squares with true alpha, it came 1254 x 1254 on ~15 x 14.6-px squares with soft
alpha. Its own export (rengar-A.png / rengar-A-grid.png) squeezed the figure into 62 x 62 by nearest - the face lost,
the body stretched tall - so it is NOT used. The raw is read on its own squares (design_fiora_hd.grid, alpha under 128
dropped), cut to colours by k-means, the outline closed where the read lost it, and kept as drawn: its rows from the
horn's tip to the soles over his 1x sprite's 40 make the PPU (~1.5, as asked).
-> hd/design.png. With --review DIR: <dir>/rengar_ppu_size.png (the design beside this pack's PPU 1.5 heroes and Rengar
now, as the game draws them, hd.rs SIZES applied) and <dir>/rengar_ppu_closeup.png (Codex's picture | the read).
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
import strips as G  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
AH.HD = os.path.join(ROOT, "assets", "source", "rengar", "hd")
AH.RAW, AH.PITCH = "rengar-A.png", (12.0, 17.0)  # its own square (~15.1 x 14.6 px)
OLD = 40                        # his 1x idle, the horn's tip to his soles
PEERS = ["rengar", "leesin", "udyr", "xinzhao", "khazix"]


def design():
    q, pal, _ = AH.native()
    # where the read lost Codex's outline: closed again in the outline colour (strips.complete_outline)
    out = AH.outline_of(pal)
    q = G.complete_outline(q, color=out)[0]
    # and the dark squares on the rim (the outline averaged with what it rings) the outline colour
    op = q[..., 3] > 0
    rim = op & ~ndimage.binary_erosion(op, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    q[rim & (q[..., :3].astype(int).sum(-1) < 170), :3] = out
    ys, xs = np.nonzero(q[..., 3])
    q = q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return tail_root(q, out), q.shape[0] / OLD


# Codex's tail curls up right of his far hand and ends behind it - in game it read as growing out of the hand (「怎么
# 尾巴在手上？」). Its root drawn on from there: down-left behind the blade and the hand, seen under the hand as a short
# piece that goes in behind his far thigh. TAIL_PATH: the root's middle line (row, column) on the read; drawn only
# where the picture is empty (behind everything), its upper side lit like the rest of the tail.
TAIL_PATH = ((43.5, 63.0), (49.5, 55.5))
TAIL = ((0x7d, 0x86, 0xb1), (0x67, 0x71, 0x9d), (0x52, 0x5b, 0x85))      # lit / mid / shade: the tail's own blues


def tail_root(q, out):
    return root(q, TAIL_PATH, out)


def root(q, path, out):
    """The tail's root along path ((row, column), (row, column)) on q: 2.7 squares thick in the tail's blues (its side
    towards the top-right lit) inside an outline, drawn only where q is empty (so it passes behind what is there)."""
    q = q.copy()
    (y0, x0), (y1, x1) = path
    d = np.array([y1 - y0, x1 - x0])
    n = np.array([-d[1], d[0]]) / np.hypot(*d)            # the side towards the top-right: lit
    for y in range(max(0, int(min(y0, y1)) - 3), min(q.shape[0], int(max(y0, y1)) + 4)):
        for x in range(max(0, int(min(x0, x1)) - 3), min(q.shape[1], int(max(x0, x1)) + 4)):
            if q[y, x, 3]:
                continue
            p = np.array([y + 0.5 - y0, x + 0.5 - x0])
            t = np.clip(p @ d / (d @ d), 0, 1)
            off = p - t * d
            r = np.hypot(*off)
            if r <= 1.35:
                side = off @ n
                c = TAIL[0] if side > 0.45 else TAIL[1] if side > -0.45 else TAIL[2]
                q[y, x] = (*c, 255)
            elif r <= 2.4:
                q[y, x] = (*out, 255)
    return q


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
        cells.append((("now" if h == "rengar" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "rengar_ppu_size.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("Codex's picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "rengar_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
