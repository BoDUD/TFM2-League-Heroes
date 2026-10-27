#!/usr/bin/env python3
"""league_gwen redone at PPU 2.84 (the user, 2026-10-25: 「接下来可以优化格温 格温感觉只要利用PPU调高像素 还有眼睛那里改一下
就可以了」): the design is Codex's v2 picture read as drawn (tools/art/design_gwen_hd.py, 93 x 116), every action Codex's
whole-frame redraw mended onto it (tools/art/casts_gwen_hd.py: her scissors full size and always in her right hand, each
frame placed on the design's grid). The run is the design's own skip (run_frames): Codex drew one pose eight times, the
same foot always kicked back (the user: 「跑步有点不对啊」「没有格温跳动的感觉 左右腿也不明显的交换」). The standing
idle_base is the design itself; the idle and the ban/pick card are cut
from the actions by tools/art/hero_reels.py. Her snips and the dash's mist stay baked as before
(assets/source/native/gwen_bake.json, Rig.bake), the snips moved with the blade's tip: the old frames' tips were 42 / 39
/ 40 game px in front of her (attack frame 4, Snip Snip!'s frames 3 and 7, its frame 12), the new ones 56 / 44 / 46.5.

    python tools/art/rig_gwen_hd.py --review DIR       # every tag at 3x + GIFs, the effects on
    python tools/art/rig_gwen_hd.py                    # orig strips (+ the effects' .over) + the 1x sheet
    python tools/art/ppu_restyle.py --hero gwen && python tools/art/ppu_hd.py --hero gwen
    python tools/art/hero_reels.py --hero gwen         # then: the idle / ban-pick reels from idle_base
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_gwen_hd as CG  # noqa: E402
import gwen_twin_tails as TT  # noqa: E402
import design_gwen_hd as DG  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "gwen"
PPU = DG.PPU
DESIGN_ROWS = 116
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
OUTLINE = CG.SC.OUTLINE
# the canvas round the design: the thrust and its snip reach 190 squares in front of her pivot, the swing-down 110
# behind, the raised pair 67 over her ahoge
PAD = (80, 170, 80, 30)


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
    mids, _, _ = CG.shoes(d)
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


class GwenRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def make_rig(D):
    return GwenRig(D, pad=PAD)


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


# the run: her legs under the skirt (design rows from LEG_CUT, these columns) cut out whole and moved - translation only;
# each half cycle one leg pushes off and kicks up (the near one mostly up: kicked back it would cover the far one), the
# other lands and reaches on, the whole figure hops and the body sinks over the legs when she lands; the legs swap
# every half cycle. Per frame: (hop up, body sink, kicking leg (dx, dy), planted leg (dx, dy)), design squares.
LEG_CUT = 103
LEGS = {"far": (32, 46), "near": (54, 73)}
SKIP = {"near": [(0, 3, (-2, 0), (1, 0)), (-4, 0, (-3, -5), (1, 0)), (-8, 0, (-4, -8), (2, -1)), (-4, 1, (-3, -4), (2, 0))],
        "far": [(0, 3, (-4, 0), (3, 0)), (-4, 0, (-6, -5), (3, 0)), (-8, 0, (-7, -8), (5, -1)), (-4, 1, (-5, -4), (4, 0))]}


def run_frames(rig):
    d = rig.D.d0
    legs = {}
    for name, (x0, x1) in LEGS.items():
        m = np.zeros(d.shape[:2], bool)
        m[LEG_CUT:, x0:x1] = True
        legs[name] = m & (d[..., 3] > 0)
    body = d.copy()
    body[legs["far"] | legs["near"]] = 0
    out = []
    for kick, plant in (("near", "far"), ("far", "near")):
        for hop, sink, kd, pd in SKIP[kick]:
            can = rig.canvas()
            for name, (dx, dy) in ((kick, kd), (plant, pd)):
                ys, xs = np.nonzero(legs[name])
                can[ys + dy + hop + rig.oy, xs + dx + rig.ox] = d[ys, xs]
            ys, xs = np.nonzero(body[..., 3] > 0)
            can[ys + sink + hop + rig.oy, xs + rig.ox] = body[ys, xs]      # the body over the legs
            out.append(can)
    return out


def frames(rig):
    sheet = R.sheet_of(HERO)
    casts = TT.cut_casts(CG.placed())             # without the back tail (gwen_twin_tails.py)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag == "idle_base":
            fr = [on_grid(rig, rig.D.d0, 0, 0) for _ in range(n)]
        elif tag == "run":
            fr = run_frames(rig)
            if len(fr) != n:
                sys.exit(f"run: {len(fr)} frames, the sheet has {n}")
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
