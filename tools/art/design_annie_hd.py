#!/usr/bin/env python3
"""Annie's dense design: Codex's step-0 picture read back on its own squares, design_ahri_hd's way.

    python tools/art/design_annie_hd.py [--take A] [--ppu 2.2] [--review DIR] [--out PNG]

Asked (assets/source/annie/PICTURE_PROMPT_PPU.md) for 75 squares of 11 px from her cat-ear tips to her soles in two
takes, Codex drew (hd/raw/) A (League's idle: Tibbers hanging from her near hand) on ~11.5-px squares, 106 rows, and
B (Tibbers hugged in front) on ~11.0 x 10.8-px squares, 111 rows; both with a soft alpha rim (dropped at 128). Each is
read on its own squares (design_fiora_hd.grid), cut to colours by k-means, then design_ahri_hd.read's Lab-mean step
takes it to her old height (34 px) times PPU.
-> hd/design.png (take A at 2.2 with FACE). With --review DIR: <dir>/annie_ppu_size.png (both takes at each --ppus beside this pack's PPU 2.2
heroes and Annie now, as the game draws them) and <dir>/annie_ppu_closeup.png (the designs at 6x).
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
AH.HD = os.path.join(ROOT, "assets", "source", "annie", "hd")
TAKES = {"A": ("annie-A.png", (11.3, 11.8)), "B": ("annie-B.png", (10.6, 11.4))}
OLD = 34                        # her 1x idle, cat-ear tips to soles
PPU = 2.2
PEERS = ["annie", "ahri", "lux", "jinx"]
# take A at PPU 2.2 (the user's pick, 2026-10-24: 「用 A，PPU 2.2，修脸后给我看」), the face set by hand after Codex's
# picture: the near eye's lash one dark row over a white-left / green iris (lime light, dark rim below), the far eye a
# green iris with a lime light, the nose a shade square, the mouth a crimson line, the cheek's tan speck skin
H = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # noqa: E731
OUT, WHITE, IRIS, LIME, RIM, SKIN = (H(c) for c in ("100213", "F5F1F2", "3D7A05", "62A608", "1D370A", "FCC58E"))
FACE = {(21, 23): OUT, (26, 23): OUT, (22, 24): WHITE, (21, 25): WHITE, (22, 25): WHITE, (23, 25): IRIS,
        (24, 25): LIME, (25, 25): IRIS, (21, 26): H("F39A6E"), (23, 26): RIM, (24, 26): RIM, (25, 26): SKIN,
        (31, 22): IRIS, (31, 23): LIME, (32, 23): RIM, (30, 25): H("F39A6E"),
        (27, 28): SKIN, (28, 28): H("BA1E36"), (29, 28): H("BA1E36"), (30, 28): SKIN}


def design(take, ppu):
    AH.RAW, AH.PITCH = TAKES[take]
    q, _, _ = AH.native()
    ys = np.nonzero(q[..., 3])[0]
    step = (ys.max() - ys.min() + 1) / (OLD * ppu)
    return AH.read(step)[0], step


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", default="A", choices=sorted(TAKES))
    ap.add_argument("--ppu", type=float, default=PPU)
    ap.add_argument("--review")
    ap.add_argument("--ppus", type=float, nargs="*", default=[2.2, 2.5])
    ap.add_argument("--out", help="write the design here instead of hd/design.png")
    ap.add_argument("--raw-face", action="store_true", help="leave the face as read (no FACE)")
    a = ap.parse_args()
    d, step = design(a.take, a.ppu)
    if (a.take, a.ppu) == ("A", PPU) and not a.raw_face:
        for (x, y), c in FACE.items():
            d[y, x, :3] = c
    Image.fromarray(d).save(AH.lp(a.out or os.path.join(AH.HD, "design.png")))
    print(f"take {a.take}, step {step:.2f} -> design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    cells, close = [], []
    for take in sorted(TAKES):
        for p in a.ppus:
            dt, _ = design(take, p)
            cells.append((f"{take} {p}: {dt.shape[0] / p:.1f}px", FD.shown(Image.fromarray(dt), p, 3)))
            if p == a.ppus[0]:
                close.append((f"{take} design {dt.shape[1]}x{dt.shape[0]} (PPU {p})", FD.shown(Image.fromarray(dt), 1, 6)))
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == "annie" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "annie_ppu_size.png"))
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "annie_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
