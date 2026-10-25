#!/usr/bin/env python3
"""Gwen's dense design: Codex's v2 picture read back on its own squares, design_annie_hd's way.

    python tools/art/design_gwen_hd.py [--ppu 2.2] [--review DIR] [--out PNG]

The user, 2026-10-25, after the pack traced from her sprite (tools/art/pack_gwen_ppu.py): gave Codex their own Gemini
picture (「参照这个 来做」) and picked its take 「用这个」 - a new look: navy-and-white layered dress, white frilled
headband, turquoise drill curls with pink tips, League's big round blue eyes, real closed dressmaker scissors over her
shoulder (one big and one small round finger loop, gold frame). hd/raw/gwen-v2.png is drawn on ~10.6-px squares
(93 x 116 with the ahoge) with a soft alpha rim (dropped at 128); read on its own squares (design_fiora_hd.grid), cut
to colours by k-means, then design_ahri_hd.read's Lab-mean step takes her crown (CROWN rows under the ahoge's tip) to
her soles to her height now (38 game rows) times PPU.
Brought to size by whole lines dropped (design()), the face's lines kept.
-> hd/design.png (PPU 2.84: as drawn). With --review DIR: <dir>/gwen_ppu_size.png (the design at each --ppus beside this pack's PPU 2.2
heroes and Gwen now, as the game draws them) and <dir>/gwen_ppu_closeup.png (Codex's picture and the design at 6x).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_ahri_hd as AH  # noqa: E402
import design_fiora_hd as FD  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
AH.HD = os.path.join(ROOT, "assets", "source", "gwen", "hd")
AH.RAW, AH.PITCH = "gwen-v2.png", (10.3, 11.2)  # its own square (10.67 x 10.56)
OLD = 38                        # her 1x idle, crown to soles (the ahoge and the blade apart; 2026-10-09 「格温好像也偏大」)
CROWN = 8                       # squares of Codex's read from the ahoge's tip down to her crown (the headband's top)
PPU = 2.84                      # the user's pick, 2026-10-25: 「用 2.84，按原图密度」 - her read as drawn (108 / 38 rows)
FACE_ROWS, FACE_COLS = range(34, 51), range(43, 68)   # her eyes (rows 37-45), mouth (48-49) on the read's squares
PEERS = ["gwen", "annie", "ahri", "lux"]


def design(ppu, how="cut"):
    """how "cut": the read on its own squares brought to her size by whole rows and columns dropped (design_rell_cut.
    even_cut: one per equal window, never two neighbours, never the face's lines FACE_ROWS / FACE_COLS) - the Lab
    mean (how "mean", design_ahri_hd.read) muddied her face and broke the outline at 1.29 squares a square."""
    q, _, _ = AH.native()
    ys, xs = np.nonzero(q[..., 3])
    q = q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    step = (q.shape[0] - CROWN) / (OLD * ppu)
    if step < 1.01:
        return q, step                                  # (as drawn: PPU 2.84)
    if how == "mean":
        return AH.read(step)[0], step
    import design_rell_cut as RC
    rows = round(q.shape[0] / step)
    cols = round(q.shape[1] / step)
    return RC.even_cut(q, rows, cols, (list(FACE_ROWS), list(FACE_COLS))), step


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppu", type=float, default=PPU)
    ap.add_argument("--review")
    ap.add_argument("--ppus", type=float, nargs="*", default=[2.2, 2.84])
    ap.add_argument("--out", help="write the design here instead of hd/design.png")
    a = ap.parse_args()
    d, step = design(a.ppu)
    Image.fromarray(d).save(AH.lp(a.out or os.path.join(AH.HD, "design.png")))
    print(f"step {step:.2f} -> design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    cells, close = [], []
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    for p in a.ppus:
        dt, _ = design(p)
        cells.append((f"new {p}: {(dt.shape[0]) / p:.1f}px", FD.shown(Image.fromarray(dt), p, 3)))
        z = 600 / dt.shape[0]
        if not close:
            close.append(("Codex's picture", raw.resize((round(raw.width * 600 / raw.height), 600), Image.LANCZOS)))
        big = Image.fromarray(dt).resize((round(dt.shape[1] * z), 600), Image.NEAREST)
        close.append((f"design {dt.shape[1]}x{dt.shape[0]} (PPU {p})", FD.shown(big, 1, 1)))
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == "gwen" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "gwen_ppu_size.png"))
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "gwen_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
