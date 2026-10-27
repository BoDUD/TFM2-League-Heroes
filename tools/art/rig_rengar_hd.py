#!/usr/bin/env python3
"""league_rengar redone at PPU 1.475 (the user, 2026-10-27: 「可以参考另外一个账号 利用PPU1.5重做一下狮子狗模型」): the
design is Codex's picture traced from his sprite (the hunched stalking crouch) read on its own squares
(tools/art/design_rengar_hd.py: 76 x 59, 「设计图通过」), every action Codex's whole-frame redraw of his old frame in its
old pose read onto it (tools/art/casts_rengar_hd.py: his head the design's size), tools/art/rig_leesin_hd.py's way.

What Codex did not draw (tools/art/pack_rengar_actions.py): the old frames that were his idle pose itself (SAME_DESIGN)
are the design; a frame that repeated another (SAME) repeats its drawing; idle_base breathes and R crouches as the old
sheet did - the design's upper body sunk over its feet (BREATH, ULT: the old sheet's sinks in 1x pixels, x PPU). The
idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py. Nothing is baked: the bola, the roar,
the slashes and the leap dust are effects of their own.

    python tools/art/rig_rengar_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_rengar_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero rengar && python tools/art/ppu_hd.py --hero rengar
    python tools/art/hero_reels.py --hero rengar       # then: the idle / ban-pick reels from idle_base
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
import casts_rengar_hd as CS  # noqa: E402
import design_rengar_hd as DH  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "rengar"
PPU = CS.PPU
DESIGN_ROWS = 59
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
# (pack_rengar_actions) + dead 2: Codex drew the old frame 2 (still up, the claw flung out) already lying - his
# frame 3 (the same stagger) stands in for it, the fall from frame 4 as the old sheet's
SAME = {"dead": {2: 3, 7: 6, 8: 6}}
SAME_DESIGN = {"attack": [6], "leap": [8], "skill": [8], "skill2": [6], "skill_w": [2, 7]}
# the old sheet's sinks in 1x pixels: idle_base its breath, ult its crouch (= idle_base's sunk frames)
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]
ULT = [1, 2, 2, 1]
# the run: Codex drew frames 3-4 on straighter legs, the head 5-6 squares over frames 5-8 (one hop a cycle; the old run
# bobbed a pixel) - whole rows cut out of the legs (RUN_LEGS: squares over the soles), evenly, the feet where they stand
RUN_CUT = {1: 1, 2: 1, 3: 3, 4: 4}
RUN_LEGS = (17, 5)
FEET = (52, 18, 63)
# the tail's root (design_rengar_hd.root) on Codex's frames that drew the tail as the design had it - curled up right of
# the far hand and gone behind the blade there, so it read as growing out of the hand (「怎么尾巴在手上？」): from behind
# the blade, under the hand, into his far thigh. (row, column) pairs on the cast pictures (casts_rengar_hd.placed);
# the frames whose tail already comes out from behind his body (attack 2-5, the leap's flight, Q 2-7, W 3-5, the
# fall) are left as drawn
TAIL_ROOTS = {
    "run_1": ((40, 64), (47, 51)), "run_2": ((40, 62), (48, 49)), "run_3": ((44, 70), (48, 55)),
    "run_4": ((42, 69), (49, 48)), "run_5": ((40, 69), (45, 53)), "run_6": ((41, 69), (45, 51)),
    "run_7": ((41, 68), (46, 47)), "run_8": ((41, 68), (46, 49)), "attack_1": ((50, 71), (54, 57)),
    "leap_1": ((45, 71), (49, 60)), "leap_7": ((47, 81), (49, 68)), "skill_1": ((48, 71), (51, 64)),
    "skill2_1": ((41, 64), (45, 54)), "skill2_2": ((41, 71), (44, 59)), "skill2_3": ((48, 68), (52, 58)),
    "skill2_4": ((45, 75), (49, 64)), "skill2_5": ((50, 64), (53, 56)), "skill_w_1": ((51, 70), (54, 61)),
    "skill_w_6": ((44, 62), (47, 54)), "hit_1": ((43, 68), (47, 60)), "hit_2": ((42, 71), (47, 57)),
}             # the design's feet: rows 52 down between columns 18 and 62 (the claw and the blade out)


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
    D.px = int(round(CD.shoes_mid(d)))              # between his feet
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


class RengarRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


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


def sunk(d, rows):
    """The design's body `rows` squares lower with the feet where they stand (drawn over it), nothing under the soles."""
    if rows == 0:
        return d.copy()
    h = d.shape[0]
    out = np.zeros_like(d)
    out[rows:] = d[:h - rows]
    r0, c0, c1 = FEET
    feet = np.zeros(d.shape[:2], bool)
    feet[r0:, c0:c1] = d[r0:, c0:c1, 3] > 0
    out[feet] = d[feet]
    return out


def cut_legs(rig, can, n):
    """n whole rows cut out of the band RUN_LEGS over the soles (evenly spread), what is over them lowered n rows."""
    if not n:
        return can
    hi, lo = rig.GY - RUN_LEGS[0], rig.GY - RUN_LEGS[1]
    cut = set(int(round(v)) for v in np.linspace(hi, lo - 1, n + 2)[1:-1])
    keep = [r for r in range(rig.GY) if r not in cut]
    out = rig.canvas()
    out[rig.GY - len(keep):rig.GY] = can[keep]
    out[rig.GY:] = can[rig.GY:]
    return out


def frames(rig, casts):
    casts = {n: ((DH.root(p, TAIL_ROOTS[n], rig.D.outline), x, y) if n in TAIL_ROOTS else (p, x, y))
             for n, (p, x, y) in casts.items()}
    sheet = R.sheet_of(HERO)
    d0 = rig.D.d0
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag == "idle_base":
            fr = [on_grid(rig, sunk(d0, round(s * PPU)), 0, 0) for s in BREATH]
        elif tag == "ult":
            fr = [on_grid(rig, sunk(d0, round(s * PPU)), 0, 0) for s in ULT]
        else:
            fr = []
            for k in range(1, n + 1):
                if k in SAME_DESIGN.get(tag, []):
                    fr.append(on_grid(rig, d0, 0, 0))
                else:
                    fr.append(on_grid(rig, *casts[f"{tag}_{SAME.get(tag, {}).get(k, k)}"]))
            if tag == "run":
                fr = [cut_legs(rig, f, RUN_CUT.get(k + 1, 0)) for k, f in enumerate(fr)]
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        if len(fr) != n:
            sys.exit(f"{tag}: {len(fr)} frames for the sheet's {n}")
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = list(out["idle_base"])
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    casts = CS.placed()
    rig = RengarRig(D, pad=pad_for(D, casts))
    acts = frames(rig, casts)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
