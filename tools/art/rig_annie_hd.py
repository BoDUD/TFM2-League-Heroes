#!/usr/bin/env python3
"""league_annie redone at PPU 2.2 (the user, 2026-10-24: 「继续重做下一个英雄 安妮」): the design is Codex's take A read back
on its own squares (tools/art/design_annie_hd.py, 44 x 75, the face set by hand), every action Codex's whole-frame
redraw mended onto it (tools/art/casts_annie_hd.py: the design's head, her size, the ground). The standing idle_base is
the design itself; the idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py.

    python tools/art/rig_annie_hd.py --review DIR       # every tag at 3x + GIFs
    python tools/art/rig_annie_hd.py                    # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero annie && python tools/art/ppu_hd.py --hero annie
    python tools/art/hero_reels.py --hero annie         # then: the idle / ban-pick reels from idle_base
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_annie_hd as CA  # noqa: E402
import design_annie_hd as DA  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "annie"
PPU = DA.PPU
DESIGN_ROWS = 75
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
OUTLINE = CA.OUTLINE


def lp(path):
    return R.lp(path)


def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    mids, _ = CA.shoes(d)
    D.px = int(round((mids[0] + mids[-1]) / 2.0))     # between her shoes
    D.d0 = D.d.copy()
    return D


def drop_specks(can, most=4):
    """Bits of up to `most` squares cut off from the figure: gone."""
    out = can.copy()
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] <= most:
                out[lbl == k] = 0
    return out


class AnnieRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def on_grid(rig, d, x, y):
    """A picture whose top-left square sits at (x, y) on the design's grid, on the rig's canvas; what rests on the
    ground (lying) edged by the outline there."""
    ys, xs = np.nonzero(d[..., 3] > 0)
    can = rig.canvas()
    Y, X = ys + y + rig.oy, xs + x + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    if not ok.all():
        sys.exit(f"{int((~ok).sum())} squares off the canvas")
    can[Y, X] = d[ys, xs]
    cut = (can[rig.GY:rig.GY + 1, :, 3] > 0)[0] & (can[rig.GY - 1, :, 3] > 0)
    can[rig.GY:] = 0
    can[rig.GY - 1, cut] = (*OUTLINE, 255)
    return can


def frames(rig):
    sheet = R.sheet_of(HERO)
    casts = CA.placed()
    if CA.PIVOT_COL != rig.D.px or CA.GROUND != rig.D.ground:
        # (casts_annie_hd places on the design's own pivot and ground: the same numbers)
        shift = rig.D.px - CA.PIVOT_COL
        casts = {n: (d, x + int(round(shift)), y + rig.D.ground - CA.GROUND) for n, (d, x, y) in casts.items()}
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag == "idle_base":
            fr = [on_grid(rig, rig.D.d0, 0, 0) for _ in range(n)]
        else:
            fr = [on_grid(rig, *casts[f"{tag}_{k + 1}"]) for k in range(n)]
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = list(out["idle_base"])
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = AnnieRig(D, pad=(110, 110, 110, 30))
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
