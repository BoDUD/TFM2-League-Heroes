#!/usr/bin/env python3
"""league_jhin redone at PPU 1.80 (the user, 2026-11-05: 「接下来重做螳螂 机器人 莉莉娅 烬」, 「卡兹克2.24 布里茨1.8 莉莉娅2.62 烬1.8」): the design
is Codex's jhin-A read on ~15.3-px squares (tools/art/design_jhin_hd.py: 55 x 74), every action Codex's whole-frame
redraw of his old frame read onto it at the zoom its fit over the old frame Codex drew it on gives
(tools/art/casts_jhin_hd.py), rig_viego_hd.py's way.

The old frames that repeat another (pack_jhin_actions.SAME) take that drawing; idle_base is the design held still (the
idle is hero_reels' reel of action snippets). Attack's, attack4's, skill's, skill2's and ult_shot's native body cells
drawn and the muzzle flashes and Q's throw flash baked back on (rig_akali_hd's frames()); the attack's shot moved up to
Codex's muzzle (FX_SHIFT). The idle and the ban/pick card are cut from the actions by tools/art/hero_reels.py.

    python tools/art/rig_jhin_hd.py --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_jhin_hd.py                  # orig strips + the 1x sheet
    python tools/art/ppu_restyle.py --hero jhin && python tools/art/ppu_hd.py --hero jhin
    python tools/art/ppu_one.py --hero jhin && python tools/art/rig_jhin_hd.py --one-ground   # the 1x frames
    python tools/art/hero_reels.py --hero jhin       # then: the idle / ban-pick reels
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
import casts_jhin_hd as CA  # noqa: E402
import pack_jhin_actions as PK  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_rengar_hd as RG  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "jhin"
PPU = CA.PPU
DESIGN_ROWS = 74
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
FX_PAD = 60                     # squares round the canvas for the baked effects (frames())
# jhin_bake.json items moved (dx, dy old px) onto Codex's muzzle: in the attack's aim (frame 3) he holds Whisper 8 px
# higher than the old cell did, so its flash and the shot fly from his muzzle; the gun's tip under every other effect
# (the attack's cast spark, the fourth shot, Q's throw, W's and R's shots) is Codex's within a pixel
FX_SHIFT = {"a_muzzle": (0, -8)}


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


class JhinRig(R.Rig):
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
    rig = JhinRig(D, pad=(left + FX_PAD, right + FX_PAD, top + FX_PAD, bottom + FX_PAD))
    acts = frames(rig, cs)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
