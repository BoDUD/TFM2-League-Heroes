#!/usr/bin/env python3
"""Samira's dense design: Codex's picture (tools/art/pack_samira_ppu.py's pack, traced from her sprite now - the user's
own ChatGPT picture cut to game size) read back on its own squares, design_gwen_hd's way.

    python tools/art/design_samira_hd.py [--ppu 2.2] [--review DIR] [--out PNG]

Codex delivered (2026-10-25) hd/raw/samira-refined.png drawn on ~10-px squares - 138 of them from the sword's hilt to
her soles, PPU 3.7 at her 37 game rows - and its own export samira-A.png, that resampled to 72 x 81 squares at 11 px
(PPU 2.2: muddy). The raw is read on its own squares (design_fiora_hd.grid), cut to colours by k-means, then brought to
her height (OLD game rows from the hilt's top to the soles) times PPU by whole lines dropped (design_rell_cut.even_cut,
never the face's lines). -> hd/design.png. With --review DIR: <dir>/samira_ppu_size.png (each --ppus beside this pack's
PPU 2.2 heroes and Samira now, as the game draws them) and <dir>/samira_ppu_closeup.png.
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
AH.HD = os.path.join(ROOT, "assets", "source", "samira", "hd")
AH.RAW, AH.PITCH = "samira-lol-refined.png", (7.5, 8.6)  # its own square (~8 px)
OLD = 37                        # her 1x idle, the sword's hilt to her soles
CROWN = 0                       # (measured from the top of the read: the hilt)
PPU = 2.2
FACE_ROWS, FACE_COLS = range(0), range(0)             # set once the read is looked at
PEERS = ["samira", "annie", "ahri", "lux"]


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
    ap.add_argument("--ppus", type=float, nargs="*", default=[2.2, 2.84, 3.7])
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
        cells.append((("now" if h == "samira" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "samira_ppu_size.png"))
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "samira_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
