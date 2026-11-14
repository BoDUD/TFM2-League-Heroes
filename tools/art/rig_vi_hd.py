#!/usr/bin/env python3
"""league_vi redone at PPU 1.82 (the user, 2026-11-03: 「下面重做蔚 崔斯特 艾克」「再加一个吧 萨科」, 「蔚1.82 卡牌2.7 艾克1.94 萨科2.12」): the design is Codex's
vi-A read on ~16-px squares (tools/art/design_vi_hd.py: 52 x 73), every action Codex's whole-frame
redraw of her old frame read onto it at the median of the zooms her height, her hair and her area give
(tools/art/casts_vi_hd.py), rig_viego_hd.py's way.

The old frames that repeat another (pack_vi_actions.SAME) take that drawing; idle_base is the design held still (the
idle is hero_reels' reel of action snippets). Skill_dash's native body cells drawn and Q's dash picture baked back on; skill_fx1 / ult_fx1 the copies vi_bake.json makes (rig_akali_hd's frames()). The idle and the ban/pick card are cut from the actions by
tools/art/hero_reels.py.
The in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」,
「能改就想办法改 全都要改」): Q's charge and R's dash get a frame after each drawing with her hair waved by whole columns (INB),
everything else of the picture checked unchanged.

    python tools/art/rig_vi_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_vi_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero vi && python tools/art/ppu_hd.py --hero vi
    python tools/art/ppu_one.py --hero vi && python tools/art/rig_vi_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero vi       # then: the idle / ban-pick reels
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_vi_hd as CA  # noqa: E402
import inbetween as IB  # noqa: E402
import pack_vi_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "vi"
PPU = CA.PPU
DESIGN_ROWS = 73
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
FX_PAD = 60                     # squares round the canvas for the baked effects (frames())


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


class ViRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


# The in-betweens (2026-11-14: R's cast is the kit's 8 ticks, 133 ms in two frames - a third would be under 50 ms -, so
# the eye stays on the dash after it, six running drawings at 125 ms; Q's charge was four drawings at 125 ms): after
# each drawing the same drawing with her hair (by its own colours inside WAVE's box - her armour's pink stripes lie
# outside it -, with the outline squares that edge only hair or air) waved by whole columns, nothing at the column where
# it leaves her head and k rows at its free end (positive: lifted): Q's hair flares up 4 as she charges, the dash's
# swings 4 lower (one frame 4 higher: lowered, its tip would come apart) - hair under her raised arm only moves away
# from it. INB: tag -> ([(cast, waved)], ms). Q keeps its drawings at 0 / 125 / 250 / 375 and puts its in-betweens on
# vi_bake.json's own boundaries (its charge effect changes every 100 ms), so skill_fx1 gets no piece under 50 ms that it
# did not have; the dash keeps its 125 ms a drawing.
VPAD = 30
HAIR = [(232, 54, 124), (249, 100, 164), (205, 40, 105), (170, 27, 83), (141, 19, 67), (116, 16, 56), (176, 60, 102),
        (91, 17, 47)]
WAVE = {"skill_1": ((4, 0, 26, 25), 8, 26, 4), "skill_2": ((0, 0, 23, 26), 4, 23, 4),
        "skill_3": ((0, 0, 19, 33), 0, 19, 4), "skill_4": ((0, 0, 20, 26), 0, 20, 4),
        "ult_dash_1": ((0, 0, 49, 41), 0, 49, -4), "ult_dash_2": ((0, 0, 35, 36), 0, 35, -4),
        "ult_dash_3": ((0, 0, 40, 34), 0, 40, -4), "ult_dash_4": ((0, 0, 36, 34), 0, 36, -4),
        "ult_dash_5": ((0, 0, 39, 34), 0, 39, 4), "ult_dash_6": ((0, 0, 41, 36), 0, 41, -4)}
INB = {"skill": ([(f"skill_{k}", w) for k in range(1, 5) for w in (False, True)],
                 IB.spans((125, 2, [2, 3]), (125, 2, [3, 2]), (125, 2, [2, 3]), (125, 2, [3, 2]))),
       "ult_dash": ([(f"ult_dash_{k}", w) for k in range(1, 7) for w in (False, True)], IB.spans(*[(125, 2)] * 6))}


def hair_in(d, box):
    """Her hair's squares inside the box (x0, y0, x1, y1): its colours, and the near-black squares edging them where
    nothing but hair, outline and air is next to them (the hair's outline, two or three squares thick in places; a line
    between the hair and something else stays with that)."""
    x0, y0, x1, y1 = box
    rgb, op = d[..., :3].astype(int), d[..., 3] > 0
    inb = np.zeros(op.shape, bool)
    inb[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    hair = op & inb & np.any([(rgb == c).all(-1) for c in HAIR], axis=0)
    dark = op & inb & (IB.lum(d[..., :3]) < IB.DARK)
    other = op & ~hair & ~dark
    near = lambda m: np.pad(m, 1)[2:, 1:-1] | np.pad(m, 1)[:-2, 1:-1] | np.pad(m, 1)[1:-1, 2:] | np.pad(m, 1)[1:-1, :-2]
    inc = hair.copy()
    for _ in range(3):
        add = dark & near(inc) & ~near(other) & ~inc
        if not add.any():
            break
        inc |= add
    return inc


def runs(m):
    """A mask as row runs (x0, y, x1, y), boxes for inbetween.vary."""
    out = []
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        if not len(xs):
            continue
        cut = np.nonzero(np.diff(xs) > 1)[0]
        out += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
    return out


def hair_waved(rig, casts, name, waved):
    """A cast on the grid, its hair waved (WAVE) when `waved` (inbetween.vary: the rest checked unchanged)."""
    d, x, y = casts[name]
    if waved:
        box, x0, x1, k = WAVE[name]
        d = IB.vary(d, {"hair": runs(hair_in(d, box))}, tuple(int(v) for v in rig.D.outline),
                    sway=[("hair", x0, x1, k, "right")], pad=VPAD, name=f"{name} hair {k}")
        x, y = x - VPAD, y - VPAD
    return RG.on_grid(rig, d, x, y)


def body_timing(tag, sheet):
    """The frames' durations before the bake: a baked tag's native cells', else the sheet's (rig_akali_hd's)."""
    if tag in PK.BAKED:
        with open(R.lp(os.path.join(PK.NATIVE, f"{HERO}_cells.json")), encoding="utf-8") as f:
            return [c["ms"] for c in json.load(f)["tags"][tag]]
    return [m for _, m in sheet[tag]]


def frames(rig, casts):
    """Every tag's frames on the grid; the BAKED tags from their native body cells, then <hero>_bake.json lays the
    effects on again (rig.bake) and makes its copies (the *_fx1 tags), as the 1x sheet was made."""
    sheet = R.sheet_of(HERO)
    with open(R.lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8") as f:
        src = {e["into"]: e["from"] for e in json.load(f)["items"] if "from" in e}
    copies = set(src)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp") or tag in copies:
            continue
        ms = body_timing(tag, sheet) if tag != "idle_base" else [m for _, m in sheet[tag]]
        if tag == "idle_base":
            fr = [RG.on_grid(rig, rig.D.d0, 0, 0) for _ in ms]             # (held still: the design)
        elif tag in INB:
            seq, ms = INB[tag]
            fr = [hair_waved(rig, casts, n, w) for n, w in seq]
        else:
            fr = []
            for k in range(1, len(ms) + 1):
                if PK.SAME.get(tag, {}).get(k) == PK.DESIGN:
                    fr.append(RG.on_grid(rig, rig.D.d0, 0, 0))     # (the idle pose: the design itself)
                else:
                    fr.append(RG.on_grid(rig, *casts[f"{tag}_{k}"]))
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        if len(fr) != len(ms):
            sys.exit(f"{tag}: {len(fr)} frames for {len(ms)}")
        out[tag] = list(zip(fr, ms))
    acts = rig.bake(out)
    acts["idle"] = list(acts["idle_base"])
    for t in sheet:
        if t in ("idle", "bp") or t in INB or src.get(t) in INB:      # (the in-betweens' tags: their own frames)
            continue
        if t not in acts or [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: frames or timing differ from the sheet")
    return {t: acts[t] for t in sheet if t in acts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--one-ground", action="store_true", help="after ppu_one.py: trim the 1x frames along the ground")
    a = ap.parse_args()
    if a.one_ground:
        RG.HERO = HERO                                  # (rig_rengar_hd's trim along the ground, on her sheet)
        RG.one_ground()
        return
    D = design()
    cs = CA.placed()
    left, right, top, bottom = pad_for(D, cs)
    # the baked effects reach past the body (Twisted Fate's card fan, Vi's dash dust and trail): FX_PAD more round the
    # canvas so rig.bake lays them on whole (export crops each frame to what it holds)
    rig = ViRig(D, pad=(left + FX_PAD, right + FX_PAD, top + FX_PAD, bottom))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
