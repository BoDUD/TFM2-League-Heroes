"""Lucian's dense design: the user's picture (「就用这个啊」, 2026-10-26: hd/raw/lucian-user.webp - Codex's first take
re-pixelated coarser, ~10.4 x 10.85-px squares, soft alpha edge) read back on its own squares, design_samira_hd's way.
Codex's own deliveries (hd/raw/lucian-A.png on ~8-px squares = PPU 3.5, lucian-B*.png with no steady grid) are kept for
reference only.

    python tools/art/design_lucian_hd.py [--review DIR]

The picture is read on its own squares (design_fiora_hd.grid, the halo under alpha 128 dropped), cut to colours by
k-means, the outline closed where the read lost it, and kept as drawn: its rows from the top to the soles over her 1x
sprite's 40 make the PPU (~2.55). -> hd/design.png. With --review DIR: <dir>/lucian_ppu_size.png (the design beside
this pack's PPU 2.2 heroes and Lucian now, as the game draws them, hd.rs SIZES applied) and <dir>/lucian_ppu_closeup.png
(the picture | the read).
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
AH.HD = os.path.join(ROOT, "assets", "source", "lucian", "hd")
AH.RAW, AH.PITCH = "lucian-generation-02.png", (9.0, 11.0)  # Codex's raw (its export resampled it to 9 px)
OLD = 46                        # his 1x idle, the raised muzzle to his soles
PEERS = ["lucian", "draven", "jinx", "vayne"]


def design():
    q, pal, _ = AH.native()
    # Codex's outline runs thinner than a square in places (the cheek, the wraps): the read lost it there - closed
    # again in the outline colour (strips.complete_outline, as the rig's finish does on every frame)
    out = AH.outline_of(pal)
    q = G.complete_outline(q, color=out)[0]
    # and where the thin outline came back averaged with the skin (a dark brown on the cheek): the dark squares on the
    # rim the outline colour
    op = q[..., 3] > 0
    rim = op & ~ndimage.binary_erosion(op, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    q[rim & (q[..., :3].astype(int).sum(-1) < 170), :3] = out
    ys, xs = np.nonzero(q[..., 3])
    q = q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
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
        cells.append((("now" if h == "lucian" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "lucian_ppu_size.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "lucian_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
