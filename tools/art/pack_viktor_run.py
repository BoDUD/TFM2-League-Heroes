#!/usr/bin/env python3
"""Viktor's run redo pack for Codex: a skin swap on a skeleton (pack_renekton_run.py's way: League's walk as the
motion, our design as the skin).

    python tools/art/pack_viktor_run.py [--out dist/viktor_packs]

Why: Codex's step-2 run moved the design's two legs as rigid pieces (named the wrong way round, layers swapped), and
every rebuild from those pieces failed: sliding them 6 columns read as a crab (「走路和螃蟹一样？」), league_gwen's kick
cycle and two rigid crossings never showed a crossing step (「走路没有明显的交叉步感觉」「不行啊 还是看不出」) - his far leg
is small and hides behind the cape and the near leg's big foot. So Codex redraws only the legs, from League's own walk
(tools/lol/native_pose.py, the step-2 reference). The pack (zipped as viktor_run_swap_pack.zip; League's frames go into
the pack only, never into git):
  RUN_SWAP.md                  the prompt (also written to assets/source/viktor/RUN_SWAP.md)
  1_skeleton_run.png           League's walk sampled at game size, 8 frames in 4 x 2 cells of 96 x 88 squares at 8x
  2_league_run_pose.png        the same frames rendered (the legs' motion, mirrored), same cells
  3_viktor_design.png          the approved design at 8x - the skin
  4_viktor_idle_cell.png       the design in run frame 1's cell (size and place: feet on row 74)
  5_viktor_upper_body.png      what stays the design's own in every frame (head, mask, crown, claw arm, shawl, body to
                               the gold belt, both arms, the staff, the cape), the two legs cut away
  viktor_run_cells.json        each frame's standing point and duration
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
POSE = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "vk_work", "pose_n")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "viktor_native.png")
RIG = os.path.join(ROOT, "assets", "source", "viktor", "codex_strips", "rig")
DOC = os.path.join(ROOT, "assets", "source", "viktor", "RUN_SWAP.md")
PIVOT, Z = (64, 88), 8


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def upper_body(d):
    """The design without its two legs (Codex's rig/near_leg and rig/far_leg masks): everything else stays."""
    out = d.copy()
    for n in ("near_leg", "far_leg"):
        m = np.asarray(Image.open(lp(os.path.join(RIG, n + "_1x.png"))).convert("RGBA"))[..., 3] > 0
        out[m] = 0
    return out


def in_cell(a, cell, pivot):
    """A design-canvas picture in one cell (the design's pivot on the cell's pivot) on green."""
    cw, ch = cell
    c = np.zeros((ch, cw, 4), np.uint8)
    c[...] = (0, 255, 0, 255)
    ys, xs = np.nonzero(a[..., 3] > 0)
    c[ys - PIVOT[1] + pivot[1], xs - PIVOT[0] + pivot[0]] = a[ys, xs]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "viktor_packs"))
    a = ap.parse_args()
    pack = os.path.join(a.out, "viktor_run_swap_pack")
    if os.path.exists(pack):
        shutil.rmtree(pack)
    os.makedirs(pack)
    shutil.copyfile(os.path.join(POSE, "viktor_native_run.png"), os.path.join(pack, "1_skeleton_run.png"))
    shutil.copyfile(os.path.join(POSE, "viktor_pose_run.png"), os.path.join(pack, "2_league_run_pose.png"))
    with open(os.path.join(POSE, "viktor_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    with open(os.path.join(pack, "viktor_run_cells.json"), "w", encoding="utf-8") as f:
        json.dump({"cell": cells["cell"], "run": cells["tags"]["run"]}, f, indent=1)
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    pv = cells["tags"]["run"][0]["pivot"]
    up(d).save(os.path.join(pack, "3_viktor_design.png"))
    up(in_cell(d, cells["cell"], pv)).save(os.path.join(pack, "4_viktor_idle_cell.png"))
    up(in_cell(upper_body(d), cells["cell"], pv)).save(os.path.join(pack, "5_viktor_upper_body.png"))
    shutil.copyfile(DOC, os.path.join(pack, "RUN_SWAP.md"))
    zp = shutil.make_archive(pack, "zip", pack)
    print("written", zp, "pivot", pv)


if __name__ == "__main__":
    main()
