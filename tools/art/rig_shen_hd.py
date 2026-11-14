#!/usr/bin/env python3
"""league_shen redone at PPU 1.81 (the user, 2026-11-09: 「慎也需要重做」, 「1.8」): the design is Codex's shen-A read on ~13.1-px
squares (tools/art/design_shen_hd.py: 61 x 76), every action Codex's whole-frame redraw of his old frame read onto it at
its fit over the old frame Codex drew it on, E's and the death's kneeling frames scaled to the design's head
(tools/art/casts_shen_hd.py), rig_viego_hd.py's way.

The old frames that repeat another (pack_shen_actions.SAME) take that drawing; idle_base is the design held still (the
idle is hero_reels' reel of action snippets). The idle and the ban/pick card are cut from the actions by
tools/art/hero_reels.py.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
Q (his idle pose, the palm) and R's seal (his idle pose, the clasped hands) get frames made from those two pictures -
the near arm turned about its shoulder (INB), everything else of the picture checked unchanged.

    python tools/art/rig_shen_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_shen_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero shen && python tools/art/ppu_hd.py --hero shen
    python tools/art/ppu_one.py --hero shen && python tools/art/rig_shen_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero shen       # then: the idle / ban-pick reels
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_shen_hd as CA  # noqa: E402
import inbetween as IB  # noqa: E402
import pack_shen_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "shen"
PPU = CA.PPU
DESIGN_ROWS = 76
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


class ShenRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


# The in-betweens (2026-11-14: Q was his idle pose for 60 ms and the palm for 240, R's 300-ms seal his idle pose and the
# clasped hands, 150 ms each): the near arm below its shoulder guard (PARTS, boxes in each picture's own squares)
# turned about the corner where it leaves him on the side it turns away from (SHOULDER; inbetween.spin) - the palm
# coming down after the push, the arm rising toward the seal. INB: tag -> ([(picture: "design" or a cast, degrees the
# arm turns clockwise on screen)], ms); the palm still shows from 60 ms (the spirit goes at tick 7), the seal from 150.
VPAD = 30
PARTS = {"design": {"arm": [(38, 36, 61, 42), (41, 43, 43, 45), (44, 43, 46, 47), (47, 43, 61, 55)]},
         "skill_2": {"arm": [(44, 14, 68, 38)]}}
SHOULDER = {"design": (38, 41), "skill_2": (45, 28)}
INB = {"skill": ([("design", 0), ("skill_2", 0), ("skill_2", 12), ("skill_2", 28)], IB.spans((60, 1), (240, 3))),
       "ult": ([("design", 0), ("design", -30), ("ult_2", 0)], IB.spans((150, 2), (150, 1)))}


def arm_turned(rig, casts, name, deg):
    """The design or a cast on the grid, its near arm turned `deg` (inbetween.vary: the rest checked unchanged)."""
    d, x, y = (rig.D.d0, 0, 0) if name == "design" else casts[name]
    if deg:
        d = IB.vary(d, PARTS[name], tuple(int(v) for v in rig.D.outline), spins=[("arm", SHOULDER[name], deg, "under")],
                    pad=VPAD, name=f"{name} arm {deg}")
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
            fr = [arm_turned(rig, casts, n, deg) for n, deg in seq]
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
    rig = ShenRig(D, pad=pad_for(D, cs))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
