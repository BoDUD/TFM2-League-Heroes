#!/usr/bin/env python3
"""league_lucian redone at PPU 2.02 (the user, 2026-10-26: 「下一个英雄重做卢锡安 模型要和英雄联盟像一点」): the design is
Codex's picture after League's Lucian in his old sprite's pose, read on its raw's own squares
(tools/art/design_lucian_hd.py: 111 x 93, 「通过，用 2.02 原样」), every action Codex's whole-frame redraw of his old frame
in its old pose read onto it (tools/art/casts_lucian_hd.py: his head the design's size, the run on one head column).
The frames that were his idle pose pixel for pixel (attack 1 and 6, passive 1 and 7, skill 1 and 7, skill2 8,
skill2_back 8, hit 2, dead 1) and the standing idle_base (its old 8 breathing frames) are the design itself; the idle
and the ban/pick card are cut from the actions by tools/art/hero_reels.py. Nothing is baked: his shots, Piercing
Light's beam and The Culling's bullets are effects of their own (the old frames' painted muzzle flashes are gone).

    python tools/art/rig_lucian_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_lucian_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero lucian && python tools/art/ppu_hd.py --hero lucian
    python tools/art/hero_reels.py --hero lucian       # then: the idle / ban-pick reels from idle_base
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
import casts_lucian_hd as CS  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "lucian"
PPU = CS.PPU
DESIGN_ROWS = 93
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
PAD = (48, 50, 20, 30)          # the canvas round the design (left, right, top, bottom): the dash's coat tails reach 38
                                # columns behind him, the levelled pistols and the falls 39 ahead
SAME_DESIGN = {"attack": [1, 6], "passive": [1, 7], "skill": [1, 7], "skill2": [8], "skill2_back": [8], "hit": [2],
               "dead": [1]}     # his old idle pose pixel for pixel (tools/art/pack_lucian_actions.py): the design


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
    D.px = int(round(CD.shoes_mid(d)))              # between his shoes
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


class LucianRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def make_rig(D):
    return LucianRig(D, pad=PAD)


def on_grid(rig, d, x, y):
    """A picture whose top-left square sits at (x, y) on the design's grid, on the rig's canvas."""
    ys, xs = np.nonzero(d[..., 3] > 0)
    can = rig.canvas()
    Y, X = ys + y + rig.oy, xs + x + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    if not ok.all():
        sys.exit(f"{int((~ok).sum())} squares off the canvas")
    if Y.max() >= rig.GY:
        sys.exit("a frame reaches under his soles' row")
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
    # his walk while The Culling fires (tools/art/casts_lucian_runshoot.py; an add-on plays it for `run` while
    # league_lucian_r_ch is on): the run's timing
    import casts_lucian_runshoot as RS
    walk = RS.placed()
    runs = [m for _, m in sheet["run"]]
    out["r_run"] = [(on_grid(rig, *walk[f"r_run_{k + 1}"]), runs[k % len(runs)]) for k in range(len(walk))]
    return {**{t: out[t] for t in sheet if t in out}, "r_run": out["r_run"]}


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
