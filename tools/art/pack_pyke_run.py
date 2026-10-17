#!/usr/bin/env python3
"""Pyke's run redo pack for Codex: a skin swap on a skeleton (league_alistar's run, 2026-10-05: oppi's run as the motion,
our design as the skin).

    python tools/art/pack_pyke_run.py [--out dist/pyke_packs]

Why: Codex's step-2 run (codex_strips/) turned the design's legs 45 degrees by nearest-neighbour (jagged, no crossing),
and the design's own legs moved whole (tools/art/rig_pyke.py tries) only slid: Pyke stands in a deep, wide crouch, his
legs are short under baggy trousers. oppi's Rengar (LoL Reborn, Steam Workshop 3774304166, champions/cf_rengar.aseprite)
runs hunched in the same crouch, legs crossing, a weapon carried - 36 rows to Pyke's 40, so it is laid 1:1 in our cells.
The pack (zipped as pyke_run_swap_pack.zip; oppi's frames go into the pack only, never into git):
  RUN_SWAP.md                    the prompt (also written to assets/source/pyke/RUN_SWAP.md)
  1_skeleton_run.png             oppi's Rengar run, 8 frames, 4 x 2 cells of 128 x 96 squares at 8x on #00FF00,
                                 the feet on square row 81 of each cell, the standing point on column 64
  2_pyke_design.png              the approved design at 8x (the skin)
  3_pyke_idle_cell.png           the design in one cell of the same layout (size and place)
  4_pyke_upper_body.png          what stays the design's own in every frame (head, harpoon arm, spikes, coat, belt,
                                 claw arm), cut at the belt
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

OPPI = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/cf_rengar.aseprite"
DESIGN = os.path.join(ROOT, "assets", "source", "native", "pyke_native.png")
DOC = os.path.join(ROOT, "assets", "source", "pyke", "RUN_SWAP.md")
CELL, FEET, MID, Z = (128, 96), 81, 64, 8
BELT = 83                                  # design rows above this stay the design's own


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "pyke_packs"))
    a = ap.parse_args()
    pack = os.path.join(a.out, "pyke_run_swap_pack")
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
    up(des).save(os.path.join(pack, "2_pyke_design.png"))
    cell = np.zeros((ch, cw, 4), np.uint8)
    cell[...] = (0, 255, 0, 255)
    m = des[..., 3] > 0
    dy = FEET - 99
    ys, xs = np.nonzero(m)
    cell[ys + dy, xs] = des[ys, xs]
    up(cell).save(os.path.join(pack, "3_pyke_idle_cell.png"))
    upper = des.copy()
    upper[BELT:] = 0
    up(upper).save(os.path.join(pack, "4_pyke_upper_body.png"))
    shutil.copyfile(DOC, os.path.join(pack, "RUN_SWAP.md"))
    zp = shutil.make_archive(pack, "zip", pack)
    print("written", zp, len(frs), "frames")


if __name__ == "__main__":
    main()
