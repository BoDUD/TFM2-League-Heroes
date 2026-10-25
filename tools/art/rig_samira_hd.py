#!/usr/bin/env python3
"""league_samira redone at PPU 2.84 (the user, 2026-10-25: 「下一个英雄重做萨米拉」): the design is Codex's v3 picture (League's
look, the head made smaller - 「这头怎么这么大」) read on its own squares and cut to 77 x 105 (tools/art/design_samira_hd.py,
the greatsword straightened by tools/art/sword_samira_hd.py), every action Codex's whole-frame redraw read onto it
(tools/art/casts_samira_hd.py). The standing idle_base is Codex's own stance frame (IDLE); the idle and the ban/pick card are cut from
the actions by tools/art/hero_reels.py. Her muzzle flashes, sword arcs and the dash's dust stay baked as before
(assets/source/native/samira_bake.json, Rig.bake), moved to the new muzzles and hands (her guns at shoulder height now,
R's two flashes each to its own gun).

    python tools/art/rig_samira_hd.py --review DIR     # every tag at 3x + GIFs, the effects on
    python tools/art/rig_samira_hd.py                  # orig strips (+ the effects' .over) + the 1x sheet
    python tools/art/ppu_restyle.py --hero samira && python tools/art/ppu_hd.py --hero samira
    python tools/art/hero_reels.py --hero samira       # then: the idle / ban-pick reels from idle_base
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_samira_hd as CS  # noqa: E402
import design_samira_hd as DS  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "samira"
PPU = DS.PPU
DESIGN_ROWS = 105
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
# the standing frame: Codex's own redraw of her stance (Flair's last frame, hands on hips, the sword on her back) -
# the design's head is a size bigger than every action's (crown to chin 33 rows against 28-31), so idling between
# actions her head grew and shrank (「现在头还会变一大一小」)
IDLE = "skill_m_8"
PAD = (110, 170, 70, 30)        # the canvas round the design: R's guns out to both sides, the Q's thrust ahead


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
    D.px = int(round(CS.shoes_mid(d)))              # between her shoes
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


class SamiraRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def make_rig(D):
    return SamiraRig(D, pad=PAD)


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
            fr = [on_grid(rig, *casts[IDLE]) for _ in range(n)]
        else:
            fr = [on_grid(rig, *casts[f"{tag}_{k + 1}"]) for k in range(n)]
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = list(out["idle_base"])
    acts = rig.bake(out)
    for t in out:
        if [round(m) for _, m in acts[t]] != [round(m) for _, m in out[t]]:
            sys.exit(f"{t}: the bake changed the frames' timing")
    return {t: acts[t] for t in sheet if t in acts}


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
