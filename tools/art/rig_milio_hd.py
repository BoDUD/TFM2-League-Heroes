#!/usr/bin/env python3
"""league_milio redone at PPU 2.21 (the user, 2026-11-09: 「最后重做提莫 菲兹 泽丽吧」「佐伊的模型我也不满意」「再补一个吧 米利欧」, 「泽丽2.1 佐伊2.64 米利欧2.21 其他都1.8」): the design is Codex's
milio-A read on ~11.8-px squares (tools/art/design_milio_v2.py: 51 x 73), every action Codex's whole-frame
redraw of his old frame read onto it at its fit over the old frame Codex drew it on, each tag scaled until his curls are the design's size
(tools/art/casts_milio_hd.py), rig_viego_hd.py's way.

The old frames that repeat another (pack_milio_actions.SAME) take that drawing; idle_base is the design held still (the
idle is hero_reels' reel of action snippets). His fire spirit is a layer of its own (hd/design_spirit.png, read from
Codex's design picture apart from the boy): it floats over his backpack's teal cap (SPIRIT_UP over it, its middle
SPIRIT_DX off the cap's - as in the picture), going FOLLOW of the way to that place each frame (a beat behind him, the
run's loop closed), bobbing (BOB), behind him; as he dies it sinks with the pack and shrinks (FADE). The idle and the ban/pick card are cut from the actions by
tools/art/hero_reels.py.

    python tools/art/rig_milio_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_milio_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero milio && python tools/art/ppu_hd.py --hero milio
    python tools/art/ppu_one.py --hero milio && python tools/art/rig_milio_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero milio       # then: the idle / ban-pick reels
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_milio_hd as CA  # noqa: E402
import pack_milio_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "milio"
PPU = CA.PPU
DESIGN_ROWS = 73
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


class MilioRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


# ---------------------------------------------------------------------------------------------- the fire spirit
SPIRIT = np.asarray(Image.open(R.lp(os.path.join(HD, "design_spirit.png"))).convert("RGBA"))
CAP = np.array([(1, 162, 137), (1, 130, 119), (3, 64, 62), (3, 35, 33)])    # the backpack's cap: its own teals
SPIRIT_UP = 3.4                 # squares from the spirit's bottom up off the cap's top (Codex's design picture)
SPIRIT_DX = -0.9                # its middle this far right of the cap's middle (the picture)
FOLLOW = 0.6                    # each frame it goes this share of the way to its place by the cap: a beat behind him
BOB = [0, -1, -2, -1]           # its float, squares up, frame by frame
FADE = {"dead": [1, 1, 1, 0.85, 0.7, 0.55]}    # its size as he dies (it sinks with the pack and dims away)
SPIRIT_PAD = 30                 # squares more over the canvas for it


def cap_at(pic, x, y):
    """(top row, middle column) on the design's grid of the backpack's cap in a picture placed at (x, y): the highest
    piece of the cap's teals (6 squares or more), its middle from its top 4 rows; None when none shows."""
    rgb = pic[..., :3].astype(int)
    m = (pic[..., 3] > 0) & (np.abs(rgb[:, :, None, :] - CAP[None, None]).sum(-1) == 0).any(-1)
    lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
    best = None
    for i in range(n):
        ys, xs = np.nonzero(lbl == i + 1)
        if len(ys) < 6 or (best is not None and ys.min() >= best[0]):
            continue
        sel = ys < ys.min() + 4
        best = (ys.min(), (xs[sel].min() + xs[sel].max() + 1) / 2)
    return None if best is None else (best[0] + y, best[1] + x)


def spirit_place(cap):
    """The spirit's top-left (design grid) for a cap at (top, middle)."""
    return np.array([cap[0] - SPIRIT_UP - SPIRIT.shape[0], cap[1] + SPIRIT_DX - SPIRIT.shape[1] / 2])


IDLE_PLACE = None


def spirit_track(pics, loop):
    """Per frame the spirit's top-left: FOLLOW of the way from where it was to its place by the cap (frames with no
    cap showing keep the last place); from its idle place, or round the loop twice (the run)."""
    targets, last = [], None
    for pic, x, y in pics:
        cap = cap_at(pic, x, y)
        last = spirit_place(cap) if cap is not None else last
        targets.append(last)
    first = next(t for t in targets if t is not None)
    targets = [first if t is None else t for t in targets]
    pos = targets[-1].copy() if loop else IDLE_PLACE.copy()
    for _ in range(2 if loop else 1):
        out = []
        for t in targets:
            pos = pos + FOLLOW * (t - pos)
            out.append(pos.copy())
    return out


def with_spirit(rig, can, place, k, fade=1.0):
    """The spirit put behind him (on clear squares only) at `place` + its bob for frame k, at `fade` of its size."""
    sp = SPIRIT
    if fade < 1:
        sp = np.asarray(Image.fromarray(SPIRIT).resize((max(1, round(SPIRIT.shape[1] * fade)),
                                                         max(1, round(SPIRIT.shape[0] * fade))), Image.NEAREST))
    y = int(round(place[0] + (SPIRIT.shape[0] - sp.shape[0]))) + BOB[k % len(BOB)] + rig.oy
    x = int(round(place[1] + (SPIRIT.shape[1] - sp.shape[1]) / 2)) + rig.ox
    out = can.copy()
    ys, xs = np.nonzero(sp[..., 3] > 0)
    Y, X = ys + y, xs + x
    ok = (Y >= 0) & (Y < out.shape[0]) & (X >= 0) & (X < out.shape[1])
    if not ok.all():
        sys.exit("the spirit off the canvas")
    clear = out[Y, X, 3] == 0
    out[Y[clear], X[clear]] = sp[ys[clear], xs[clear]]
    return out


def frames(rig, casts):
    global IDLE_PLACE
    sheet = R.sheet_of(HERO)
    IDLE_PLACE = spirit_place(cap_at(rig.D.d0, 0, 0))
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        ms = [m for _, m in sheet[tag]]
        if tag == "idle_base":
            pics = [(rig.D.d0, 0, 0) for _ in ms]             # (held still: the design)
        else:
            pics = []
            for k in range(1, len(ms) + 1):
                if PK.SAME.get(tag, {}).get(k) == PK.DESIGN:
                    pics.append((rig.D.d0, 0, 0))     # (his idle pose: the design itself)
                else:
                    pics.append(casts[f"{tag}_{k}"])
        places = [IDLE_PLACE] * len(pics) if tag == "idle_base" else spirit_track(pics, loop=tag == "run")
        fade = FADE.get(tag, [1] * len(pics))
        fr = [with_spirit(rig, RG.on_grid(rig, *p), places[k], k, fade[k]) for k, p in enumerate(pics)]
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
    left, right, top, bottom = pad_for(D, cs)
    # the spirit floats over the backpack, above his hair: SPIRIT_PAD more over the canvas
    rig = MilioRig(D, pad=(left, right, top + SPIRIT_PAD, bottom))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
