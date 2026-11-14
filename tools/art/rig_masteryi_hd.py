#!/usr/bin/env python3
"""league_masteryi redone at PPU 2.23 (the user, 2026-11-02: 「接下来可以重做 戴安娜 易大师 瑞兹」, 「戴安娜1.81 剑圣2.23 瑞兹1.66」): the design is
Codex's masteryi-A read on its own ~9.8-px squares (tools/art/design_masteryi_hd.py: 94 x 125), every action Codex's
whole-frame redraw of his old frame read onto it at the median of the zooms his height (his sword left out), his head and his area give
(tools/art/casts_masteryi_hd.py), rig_viego_hd.py's way.

The old frames that repeat another (pack_masteryi_actions.SAME) take that drawing; idle_base is the design held still (the
idle is hero_reels' reel of action snippets). Nothing is baked. The idle and the ban/pick card are cut from the actions
by tools/art/hero_reels.py.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
Alpha Strike and Highlander get frames made from their own pictures - the sword's blade turned about his grip (INB),
everything else of the picture checked unchanged.

    python tools/art/rig_masteryi_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_masteryi_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero masteryi && python tools/art/ppu_hd.py --hero masteryi
    python tools/art/ppu_one.py --hero masteryi && python tools/art/rig_masteryi_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero masteryi       # then: the idle / ban-pick reels
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_masteryi_hd as CA  # noqa: E402
import inbetween as IB  # noqa: E402
import pack_masteryi_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "masteryi"
PPU = CA.PPU
DESIGN_ROWS = 125
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")


def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(R.lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(R.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.d0 = D.d.copy()
    D.px = CA.PIVOT
    return D


def sealed(can, outline):
    """Every edge of the figure outlined (rig_syndra_hd's; not imported: casts_syndra_hd would point casts_rengar_hd's
    reading at Syndra): a near-black square on the edge made the outline, any other square on the edge given the
    outline on its open side."""
    out = can.copy()
    four = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], bool)
    op = out[..., 3] > 0
    line = op & (out[..., :3] == outline).all(-1)
    edge = op & ~line & ndimage.binary_dilation(~op, structure=four)
    dark = edge & (out[..., :3].max(-1) < 40)
    out[dark, :3] = outline
    ring = ndimage.binary_dilation(edge & ~dark, structure=four) & ~op
    out[ring] = (*outline, 255)
    return out


class MasterYiRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


# The in-betweens (2026-11-14: Alpha Strike was sword up, the low slash, sword up again - 200 ms, the kit's 12-tick
# animation, its hit at the teleport -; Highlander up, the power stance, the crouch - 340 ms, the cast at 100): the
# sword's blade (BLADE, a box in each picture's own squares, above the crossguard) turned about his grip (GRIP;
# inbetween.spin, the blade's root going in under the hand) - on its way down from the guard to the low slash, settling
# lower, rising back to the guard. INB: tag -> ([(picture, degrees the blade turns clockwise on screen)], ms): Alpha
# Strike's slash now from 50 ms (60 before), Highlander's stance still from 100, the crouch from 210.
VPAD = 30
BLADE = {"skill_3": [(0, 0, 22, 43)], "ult_1": [(0, 0, 25, 48)], "ult_2": [(0, 34, 64, 47)], "ult_3": [(0, 38, 61, 56)]}
GRIP = {"skill_3": (21, 46), "ult_1": (25, 51), "ult_2": (68, 41), "ult_3": (65, 44)}
INB = {"skill": ([("skill_1", 0), ("skill_2", 0), ("skill_3", -40), ("skill_3", 0)], IB.spans((200, 4))),
       "ult": ([("ult_1", 0), ("ult_1", -40), ("ult_2", 0), ("ult_2", -12), ("ult_3", 0), ("ult_3", 25)],
               IB.spans((100, 2), (110, 2), (130, 2)))}


def blade_turned(rig, casts, name, deg):
    """A cast on the grid, its sword's blade turned `deg` (inbetween.vary: the rest checked unchanged)."""
    d, x, y = casts[name]
    if deg:
        d = IB.vary(d, {"blade": BLADE[name]}, tuple(int(v) for v in rig.D.outline),
                    spins=[("blade", GRIP[name], deg, "under")], pad=VPAD, name=f"{name} blade {deg}")
        x, y = x - VPAD, y - VPAD
    return RG.on_grid(rig, d, x, y)


def frames(rig, casts):
    sheet = R.sheet_of(HERO)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        ms = [m for _, m in sheet[tag]]
        if tag == "idle_base":
            fr = [RG.on_grid(rig, rig.D.d0, 0, 0) for _ in ms]             # (held still: the design)
        elif tag in INB:
            seq, ms = INB[tag]
            fr = [blade_turned(rig, casts, n, deg) for n, deg in seq]
        else:
            fr = []
            for k in range(1, len(ms) + 1):
                if PK.SAME.get(tag, {}).get(k) == PK.DESIGN:
                    fr.append(RG.on_grid(rig, rig.D.d0, 0, 0))     # (his idle pose: the design itself)
                else:
                    fr.append(RG.on_grid(rig, *casts[f"{tag}_{k}"]))
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        out[tag] = list(zip(fr, ms))
    out["idle"] = list(out["idle_base"])
    return {t: out[t] for t in sheet if t in out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--one-ground", action="store_true", help="after ppu_one.py: trim the 1x frames along the ground")
    a = ap.parse_args()
    if a.one_ground:
        RG.HERO = HERO                                  # (rig_rengar_hd's trim along the ground, on his sheet)
        RG.one_ground()
        return
    D = design()
    cs = CA.placed()
    rig = MasterYiRig(D, pad=pad_for(D, cs))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
