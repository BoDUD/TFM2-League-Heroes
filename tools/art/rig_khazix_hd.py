#!/usr/bin/env python3
"""league_khazix redone at PPU 2.24 (the user, 2026-11-05: 「接下来重做螳螂 机器人 莉莉娅 烬」, 「卡兹克2.24 布里茨1.8 莉莉娅2.62 烬1.8」): the
design is Codex's khazix-A read on ~13.8-px squares (tools/art/design_khazix_hd.py: 81 x 83), every action Codex's
whole-frame redraw of his old frame read onto it at the zoom its fit over the old frame Codex drew it on gives
(tools/art/casts_khazix_hd.py), rig_viego_hd.py's way.

The old frames that repeat another (pack_khazix_actions.SAME) take that drawing; idle_base is the design held still (the
idle is hero_reels' reel of action snippets). The idle and the ban/pick card are cut from the actions by
tools/art/hero_reels.py.

    python tools/art/rig_khazix_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_khazix_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero khazix && python tools/art/ppu_hd.py --hero khazix
    python tools/art/ppu_one.py --hero khazix && python tools/art/rig_khazix_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero khazix       # then: the idle / ban-pick reels
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_khazix_hd as CA  # noqa: E402
import inbetween as IB  # noqa: E402
import pack_khazix_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "khazix"
PPU = CA.PPU
DESIGN_ROWS = 83
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


class KhazixRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


# R's in-betweens (2026-11-14, the user: 「有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): R had three
# drawings for its 300 ms (r_anim 18 ticks; the stealth and the rest at tick 0, no tick on a frame) - spread with the
# claws out, hunched, standing (attack_6). Two frames from his own drawings, nothing drawn: his wings turned about their
# root behind his back (inbetween.spin, "under": the root stays hidden) - on the hunched drawing still low, coming up
# from the spread one's level wings (-30 deg), and on the standing one past upright before they settle (+15 deg). The
# wings by their own yellow-greens inside the box, with their outline two squares deep where it touches only wing,
# outline or air (the antennae's cyan and the carapace stay). The drawings keep their milliseconds: hunched at 100,
# standing at 200. INB tags do not take their frames from the sheet.
INB = {"ult": [(1, 50), (2, 50, "wings_low"), (2, 50), (3, 50, "wings_up"), (3, 100)]}
INB_PARTS = {"wings_low": dict(box=(32, 14, 66, 50), about=(61, 45), deg=-30),
             "wings_up": dict(box=(36, 18, 68, 52), about=(62, 46), deg=15)}
INB_PAD = 12


def wing_colour(a):
    rgb = a[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (a[..., 3] > 0) & (r > 90) & (g > 90) & (b < g - 40) & (abs(r - g) < 70)


def inb_frame(rig, can, part):
    """The drawing's canvas with INB_PARTS[part] (its wings) turned; the same canvas size."""
    p = INB_PARTS[part]
    x0, y0, x1, y1 = p["box"]
    box = np.zeros(can.shape[:2], bool)
    box[y0:y1 + 1, x0:x1 + 1] = True
    dark = (can[..., 3] > 0) & (can[..., :3].astype(int).max(-1) < 40)
    m = wing_colour(can) & box
    for _ in range(2):
        for y, x in zip(*np.nonzero(ndimage.binary_dilation(m, structure=np.ones((3, 3))) & dark & box & ~m)):
            nb = can[max(0, y - 1):y + 2, max(0, x - 1):x + 2]
            nd = (nb[..., 3] > 0) & (nb[..., :3].astype(int).max(-1) < 40)
            if ((nb[..., 3] == 0) | wing_colour(nb) | nd).all():
                m[y, x] = True
    parts = {part: [(int(x), int(y), int(x), int(y)) for y, x in zip(*np.nonzero(m))]}
    out = IB.vary(can, parts, tuple(int(v) for v in rig.D.outline), spins=[(part, p["about"], p["deg"], "under")],
                  pad=INB_PAD, name=part)
    q = INB_PAD
    if out[:q, :, 3].any() or out[-q:, :, 3].any() or out[:, :q, 3].any() or out[:, -q:, 3].any():
        sys.exit(f"{part}: the wings leave the canvas")
    return out[q:-q, q:-q]


def frames(rig, casts):
    sheet = R.sheet_of(HERO)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        if tag in INB:
            drawn = {}
            for k, *_ in INB[tag]:
                if k not in drawn:
                    drawn[k] = RG.on_grid(rig, *casts[f"{tag}_{k}"])
            out[tag] = [(inb_frame(rig, drawn[k], part[0]) if part else drawn[k], ms) for k, ms, *part in INB[tag]]
            continue
        ms = [m for _, m in sheet[tag]]
        if tag == "idle_base":
            fr = [RG.on_grid(rig, rig.D.d0, 0, 0) for _ in ms]             # (held still: the design)
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
    rig = KhazixRig(D, pad=pad_for(D, cs))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
