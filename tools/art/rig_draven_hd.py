#!/usr/bin/env python3
"""league_draven redone at PPU 2.2 (the user, 2026-10-26: 「下一个英雄重做德莱文」): the design is the user's own picture
(「就用这个就行」, drawn at PPU 2.2 on 11-px squares, read back exactly by tools/art/design_draven_hd.py: 114 x 76), every
action Codex's whole-frame redraw of his old frame in its old pose (「你照着旧动作做啊 又没什么新动作」) read onto it
(tools/art/casts_draven_hd.py). The standing idle_base is the design itself - the actions' heads came back the design's
size (crown to chin within a square of it in every frame, Samira's lesson checked); the idle and the ban/pick card are
cut from the actions by tools/art/hero_reels.py. Nothing is baked: his axes, the catch circle and the cash-in are
effects of their own (league/effects/league_draven_fx, _big).

    python tools/art/rig_draven_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_draven_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero draven && python tools/art/ppu_hd.py --hero draven
    python tools/art/hero_reels.py --hero draven       # then: the idle / ban-pick reels from idle_base
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_draven_hd as CS  # noqa: E402
import design_draven_hd as DS  # noqa: E402
import inbetween as IB  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "draven"
PPU = DS.PPU
DESIGN_ROWS = 76
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
PAD = (40, 60, 70, 30)          # the canvas round the design: the ult's raised axe 49 rows over his crown, the death's
                                # axe and the attack's reach 28 columns past the design's right edge


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
    D.px = int(round(CS.shoes_mid(d)))              # between his shoes
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


class DravenRig(R.Rig):
    def finish(self, can):
        return drop_specks(super().finish(can))


def make_rig(D):
    return DravenRig(D, pad=PAD)


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


# The death's in-betweens (2026-11-14, the user: 「有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): every frame
# one of Codex's four casts or a cast with one part moved (inbetween.vary), nothing drawn - the red cloth strips at his
# waist lifted at their free ends (a column wave, nothing where they leave him), the raised right arm and its axe turned
# down about the shoulder toward the next cast's (spin: the root goes under the fur collar), the raised left arm and its
# axe turned down to the left as he falls (the axe on the ground in the last cast). Boxes / polygons in the canvas's
# squares (on_grid's), the fur collar's cream and teal at the shoulder left out. The death keeps its length and its
# boundaries: the stagger at 100, the fall at 200, on the ground at 320 (1070 ms in all). INB tags do not take their
# frames from the sheet.
INB = {"dead": [("dead_1", 50), ("dead_1", 50, "cloth"), ("dead_2", 50), ("dead_2", 50, "arm_r"),
                ("dead_3", 60), ("dead_3", 60, "arm_l"), ("dead_4", 750)]}
INB_PARTS = {
    "cloth": dict(cast="dead_1", poly=[(70, 92), (92, 92), (92, 114), (70, 114)], sway=(70, 91, 4)),
    "arm_r": dict(cast="dead_2", poly=[(116, 86), (113, 70), (112, 60), (106, 58), (106, 30), (143, 30), (143, 58),
                                       (131, 60), (130, 75), (128, 86)], fur=(70, None, 0, 119), spin=((115, 82), 45)),
    "arm_l": dict(cast="dead_3", poly=[(79, 86), (70, 88), (64, 80), (60, 70), (52, 70), (34, 72), (34, 30), (72, 30),
                                       (72, 58), (75, 63), (77, 66), (77, 80)], fur=(74, None, 70, None),
                  spin=((76, 82), -25)),
}
INB_PAD = 12


def fur_collar(a):
    """The fur collar's cream and teal squares."""
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (((rgb.min(-1) > 170) & (rgb.max(-1) - rgb.min(-1) < 60)) |
                              ((rgb[..., 2] > rgb[..., 0] + 20) & (rgb[..., 1] > rgb[..., 0])))


def inb_frame(rig, can, part):
    """The cast's canvas with INB_PARTS[part] moved; the same canvas size."""
    p = INB_PARTS[part]
    m = IB.part_mask(can.shape, [p["poly"]]) & (can[..., 3] > 0)
    if "fur" in p:                                   # the collar inside the part's rows / columns stays
        y0, y1, x0, x1 = p["fur"]
        box = np.zeros_like(m)
        box[y0:y1, x0:x1] = True
        m &= ~(fur_collar(can) & box)
    parts = {part: [(int(x), int(y), int(x), int(y)) for y, x in zip(*np.nonzero(m))]}
    outline = rig.D.outline
    if "sway" in p:
        x0, x1, k = p["sway"]
        out = IB.vary(can, parts, outline, sway=[(part, x0, x1, k, "right")], pad=INB_PAD, name=part)
    else:
        about, deg = p["spin"]
        out = IB.vary(can, parts, outline, spins=[(part, about, deg, "under")], pad=INB_PAD, name=part)
    q = INB_PAD
    if out[:q, :, 3].any() or out[-q:, :, 3].any() or out[:, :q, 3].any() or out[:, -q:, 3].any():
        sys.exit(f"{part}: the moved part leaves the canvas")
    out = out[q:-q, q:-q]
    if IB.audit(out):
        sys.exit(f"{part}: {IB.audit(out)}")
    return out


def frames(rig):
    sheet = R.sheet_of(HERO)
    casts, _ = CS.placed()
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        if tag in INB:
            out[tag] = []
            for name, ms, *part in INB[tag]:
                can = on_grid(rig, *casts[name])
                out[tag].append((inb_frame(rig, can, part[0]) if part else can, ms))
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
    rig = make_rig(D)
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
