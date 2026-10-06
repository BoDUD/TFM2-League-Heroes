#!/usr/bin/env python3
"""Brand's run redo pack for Codex: a skin swap on a skeleton (pack_pyke_run.py's way: oppi's run as the motion, our
design as the skin).

    python tools/art/pack_brand_run.py [--out dist/brand_packs]

Why: Codex's step-2 run pressed both legs into one column; my rigs from the design's own legs (tools/art/rig_brand.py,
2026-10-06) turned them (「裤子膝盖那里严重模型变形」), slid them sideways without crossing (「螃蟹步」, 「不是交叉
步」) or stood one wide crouched thigh upright (a brown block). Brand stands in a wide crouch: his legs cannot be
re-posed from their pixels. oppi's Brand (LoL Reborn, Steam Workshop 3774304166, champions/cf_brand.aseprite) runs
with crossing legs and the same trousers - 40 rows to our 43, laid 1:1 in our cells. The user picked this pack
(「换腿包给 Codex」). The pack (zipped as brand_run_swap_pack.zip; oppi's frames go into the pack only, never into git):
  RUN_SWAP.md                    the prompt (also written to assets/source/brand/RUN_SWAP.md)
  1_skeleton_run.png             oppi's Brand run, its frames in 4 x 2 cells of 128 x 96 squares at 8x on #00FF00,
                                 the feet on square row 81 of each cell, the standing point on column 64
  2_brand_design.png             the approved design at 8x (the skin)
  3_brand_idle_cell.png          the design in one cell of the same layout (size and place)
  4_brand_upper_body.png         what stays the design's own in every frame (head, flames, torso, both arms with
                                 the fire hands), cut at the belt
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase  # noqa: E402

OPPI = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/cf_brand.aseprite"
DESIGN = os.path.join(ROOT, "assets", "source", "native", "brand_native.png")
DOC = os.path.join(ROOT, "assets", "source", "brand", "RUN_SWAP.md")
CELL, FEET, MID, Z = (128, 96), 81, 64, 8
BELT = 85                                  # design rows above this stay the design's own


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "brand_packs"))
    a = ap.parse_args()
    pack = os.path.join(a.out, "brand_run_swap_pack")
    if os.path.exists(pack):
        shutil.rmtree(pack)
    os.makedirs(pack)
    sp = tfm2_ase.load_sprite(OPPI)
    frs = [np.asarray(sp.frames[i].convert("RGBA")) for i in sp.tag_frames("run")]
    cw, ch = CELL
    sheet = np.zeros((2 * ch, 4 * cw, 4), np.uint8)
    sheet[...] = (0, 255, 0, 255)
    for i, f in enumerate(frs):
        f = f.copy()
        f[f[..., 3] < 128] = 0
        ys, xs = np.nonzero(f[..., 3])
        idle = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
        iy, ix = np.nonzero(idle[..., 3] > 127)
        mid = (ix.min() + ix.max()) / 2          # one standing point for every frame: the idle's middle
        X, Y = (i % 4) * cw, (i // 4) * ch
        fy, fx = np.nonzero(f[..., 3])
        sheet[Y + FEET - int(iy.max()) + fy, X + int(round(MID - mid)) + fx] = f[fy, fx]
    up(sheet).save(os.path.join(pack, "1_skeleton_run.png"))
    des = np.asarray(Image.open(DESIGN).convert("RGBA"))
    up(des).save(os.path.join(pack, "2_brand_design.png"))
    cell = np.zeros((ch, cw, 4), np.uint8)
    cell[...] = (0, 255, 0, 255)
    m = des[..., 3] > 0
    dy = FEET - 99
    ys, xs = np.nonzero(m)
    cell[ys + dy, xs] = des[ys, xs]
    up(cell).save(os.path.join(pack, "3_brand_idle_cell.png"))
    upper = des.copy()
    sys.path.insert(0, HERE)
    import rig_brand
    P = rig_brand.Parts()
    legs = np.zeros(des.shape[:2], bool)
    legs[BELT:] = True
    legs &= ~(P.back_m | P.front_m)        # the fire hands hang below the belt: they stay
    upper[legs] = 0
    up(upper).save(os.path.join(pack, "4_brand_upper_body.png"))
    shutil.copyfile(DOC, os.path.join(pack, "RUN_SWAP.md"))
    zp = shutil.make_archive(pack, "zip", pack)
    print("written", zp, len(frs), "frames")


if __name__ == "__main__":
    main()
