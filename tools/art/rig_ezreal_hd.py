#!/usr/bin/env python3
"""league_ezreal redone at PPU 2.19 (the user, 2026-11-08: 「接下来重做奥拉夫 EZ 人马 鳄鱼」, then 「伊泽瑞尔2.19 其他都1.8」): the design is
Codex's ezreal-A read on ~10.2-px squares (tools/art/design_ezreal_hd.py: 41 x 79), every action Codex's whole-frame
redraw of his old frame read onto it at the zoom its fit over the old frame Codex drew it on gives
(tools/art/casts_ezreal_hd.py), rig_yone_hd.py's way.

idle_base is the design held still (the idle is hero_reels' reel of action snippets). R's body is baked: its native cells read onto the design, then R's charge (league_ezreal_big r_charge) laid
on again by assets/source/native/ezreal_bake.json from 50 ms, as the 1x sheet was made. The idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py.

    python tools/art/rig_ezreal_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_ezreal_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero ezreal && python tools/art/ppu_hd.py --hero ezreal
    python tools/art/ppu_one.py --hero ezreal && python tools/art/rig_ezreal_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero ezreal       # then: the idle / ban-pick reels
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
import casts_ezreal_hd as CA  # noqa: E402
import pack_ezreal_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "ezreal"
PPU = CA.PPU
DESIGN_ROWS = 79
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
FX_PAD = 60                     # squares round the canvas for the baked effects (frames())
FX_SHIFT = {}                   # (ezreal_bake.json's effects are laid on where the 1x sheet had them)


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


class EzrealRig(R.Rig):
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
        cfg = json.load(f)
    copies = {e["into"] for e in cfg["items"] if "from" in e}
    for e in cfg["items"]:
        if e["tag"] in FX_SHIFT:
            e["dx"], e["dy"] = FX_SHIFT[e["tag"]]
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp") or tag in copies:
            continue
        ms = body_timing(tag, sheet) if tag != "idle_base" else [m for _, m in sheet[tag]]
        if tag == "idle_base":
            fr = [RG.on_grid(rig, rig.D.d0, 0, 0) for _ in ms]             # (held still: the design)
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
    acts = rig.bake(out, cfg=cfg)
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
        RG.HERO = HERO                                  # (rig_rengar_hd's trim along the ground, on his sheet)
        RG.one_ground()
        return
    D = design()
    cs = CA.placed()
    left, right, top, bottom = pad_for(D, cs)
    # the baked effects reach past the body: FX_PAD more round the canvas so rig.bake lays them on whole, under
    # the soles too (export crops each frame to what it holds)
    rig = EzrealRig(D, pad=(left + FX_PAD, right + FX_PAD, top + FX_PAD, bottom + FX_PAD))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
