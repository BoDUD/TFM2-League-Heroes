#!/usr/bin/env python3
"""league_sivir redone at PPU 2.25 (the user, 2026-10-28: 「下一个英雄重做希维尔吧」, 「通过，用 2.25」): the design is
Codex's picture read as drawn (tools/art/design_sivir_hd.py: 98 x 81), every action Codex's whole-frame redraw of her
old frame read onto it at the zoom her head gives (tools/art/casts_sivir_hd.py), tools/art/rig_akali_hd.py's way.

What Codex did not draw (tools/art/pack_sivir_actions.py): a frame that is another frame of the old sheet (SAME) takes
that frame's drawing; idle_base is the design (her old idle_base is one still frame, six times). The effects are baked
as before (assets/source/native/sivir_bake.json, Rig.bake): Q's wait body frames (their native cells' timing) get the
Q throw's picture and are sliced to its frames; attack_fx1 / skill_catch_fx1 are the attack and the catch with the W
cast's and the catch's pictures. The idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py.

    python tools/art/rig_sivir_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_sivir_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero sivir && python tools/art/ppu_hd.py --hero sivir
    python tools/art/ppu_one.py --hero sivir && python tools/art/rig_sivir_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero sivir       # then: the idle / ban-pick reels
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
import casts_sivir_hd as CA  # noqa: E402
import pack_sivir_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "sivir"
PPU = CA.PPU
DESIGN_ROWS = 81
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


class SivirRig(R.Rig):
    def finish(self, can):
        outline = tuple(int(v) for v in self.D.outline)
        return RG.trim_nubs(sealed(RG.drop_specks(super().finish(can)), outline), outline)


def pad_for(D, casts):
    """(left, right, top, bottom) squares round the design that every cast fits in, 4 to spare."""
    left = max([0] + [-x for _, x, _ in casts.values()]) + 4
    right = max([0] + [x + p.shape[1] - D.d.shape[1] for p, x, _ in casts.values()]) + 4
    top = max([0] + [-y for _, _, y in casts.values()]) + 4
    return left, right, top, 6


def body_timing(tag, sheet):
    """The frames' durations before the bake: a baked tag's native cells', else the sheet's."""
    if tag in PK.BAKED:
        with open(R.lp(os.path.join(PK.NATIVE, "sivir_cells.json")), encoding="utf-8") as f:
            return [c["ms"] for c in json.load(f)["tags"][tag]]
    return [m for _, m in sheet[tag]]


def frames(rig, casts):
    sheet = R.sheet_of(HERO)
    with open(R.lp(os.path.join(R.ROOT, "assets", "source", "native", f"{HERO}_bake.json")), encoding="utf-8") as f:
        copies = {e["into"] for e in json.load(f)["items"] if "from" in e}
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp") or tag in copies:
            continue
        ms = body_timing(tag, sheet)
        if tag == "idle_base":
            fr = [RG.on_grid(rig, rig.D.d0, 0, 0) for _ in ms]             # (one still frame: the design)
        else:
            fr = []
            for k in range(1, len(ms) + 1):
                t, j = PK.SAME.get(tag, {}).get(k, (tag, k))
                fr.append(RG.on_grid(rig, *casts[f"{t}_{j}"]))
            if tag == "hit":
                fr[0] = R.flash(rig.finish(fr[0]))      # (the struck frame flashes, as every rig's)
        if len(fr) != len(ms):
            sys.exit(f"{tag}: {len(fr)} frames for {len(ms)}")
        out[tag] = list(zip(fr, ms))
    acts = rig.bake(out)
    acts["idle"] = list(acts["idle_base"])
    for t in sheet:
        if t in ("idle", "bp"):
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
    rig = SivirRig(D, pad=pad_for(D, cs))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
