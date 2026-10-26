#!/usr/bin/env python3
"""league_vayne redone at PPU 2.55, shown at 2.2 (the user, 2026-10-26: 「下一个英雄重做薇恩」): the design is the user's
own picture read on its own squares (tools/art/design_vayne_hd.py: 85 x 102, 「通过，用 2.2」), every action Codex's
whole-frame redraw of her old frame in its old pose read onto it (tools/art/casts_vayne_hd.py: her head the design's
size, the run on one head column). The frames that were her idle pose pixel for pixel (attack 5-6, attack_q 6, skill 7,
skill_back 7, skill2 7, ult 6, hit 2) and the standing idle_base (its old 8 breathing frames) are the design itself;
the idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py. Nothing is baked: her bolts, the
tumble's smoke, Condemn's bolt and Final Hour's aura are effects of their own.

    python tools/art/rig_vayne_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_vayne_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero vayne && python tools/art/ppu_hd.py --hero vayne
    python tools/art/hero_reels.py --hero vayne       # then: the idle / ban-pick reels from idle_base
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_draven_hd as CD  # noqa: E402
import casts_vayne_hd as CS  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "vayne"
PPU = CS.PPU
DESIGN_ROWS = 102
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
PAD = (50, 70, 40, 30)          # the canvas round the design (left, right, top, bottom): the rolls reach 36 columns
                                # behind her, the levelled crossbows and the falls 59 ahead, E's raised crossbow 23 rows
                                # over her top
SAME_DESIGN = {"attack": [5, 6], "attack_q": [6], "skill": [7], "skill_back": [7], "skill2": [7], "ult": [6],
               "hit": [2]}      # her old idle pose pixel for pixel (tools/art/pack_vayne_actions.py): the design


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
    D.px = int(round(CD.shoes_mid(d)))              # between her shoes
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


class VayneRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def make_rig(D):
    return VayneRig(D, pad=PAD)


def on_grid(rig, d, x, y):
    """A picture whose top-left square sits at (x, y) on the design's grid, on the rig's canvas."""
    ys, xs = np.nonzero(d[..., 3] > 0)
    can = rig.canvas()
    Y, X = ys + y + rig.oy, xs + x + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    if not ok.all():
        sys.exit(f"{int((~ok).sum())} squares off the canvas")
    if Y.max() >= rig.GY:
        sys.exit("a frame reaches under her soles' row")
    can[Y, X] = d[ys, xs]
    return can


def frames(rig):
    sheet = R.sheet_of(HERO)
    casts = CS.placed()
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag == "idle_base":
            fr = [on_grid(rig, rig.D.d0, 0, 0) for _ in range(n)]
        else:
            fr = [on_grid(rig, rig.D.d0, 0, 0) if k + 1 in SAME_DESIGN.get(tag, []) else
                  on_grid(rig, *casts[f"{tag}_{k + 1}"]) for k in range(n)]
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = list(out["idle_base"])
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = make_rig(D)
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
