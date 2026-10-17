#!/usr/bin/env python3
"""Renekton's run redo pack for Codex: a skin swap on a skeleton (pack_brand_run.py's way: League's run as the motion,
our design as the skin).

    python tools/art/pack_renekton_run.py [--out dist/renekton_packs]

Why: Codex's step-2 run (its parts rig) moved only the lower legs, up to 24 columns sideways to cross them, while the
thighs stayed in the body piece: in the crossing frames both shins piled up in the middle and thigh scraps floated
(the user: 「还有走路时候腿部模型严重变形」). Renekton stands in a wide crouch: his legs cannot be re-posed from their
pixels (league_brand's lesson). The user picked a leg pack for Codex (「给 Codex 发换腿包」). No other pack has a
Renekton, so the skeleton is League's own run at game size (tools/lol/native_pose.py, the step-2 reference). The pack
(zipped as renekton_run_swap_pack.zip; League's frames go into the pack only, never into git):
  RUN_SWAP.md                    the prompt (also written to assets/source/renekton/RUN_SWAP.md)
  1_skeleton_run.png             League's run sampled at game size, 8 frames in 4 x 2 cells of 128 x 96 squares at 8x
  2_league_run_pose.png          the same frames rendered (the legs' motion, mirrored), same cells
  3_renekton_design.png          the approved (narrowed) design at 8x - the skin
  4_renekton_idle_cell.png       the design in one cell of the layout (size and place: feet on row 81, pivot column 64)
  5_renekton_upper_body.png      what stays the design's own in every frame (head, body, kilt, both arms with the
                                 blade and the claws), the legs and the tail cut away
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
POSE = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rk_work", "pose_n")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "renekton_native.png")
PARTS = os.path.join(ROOT, "assets", "source", "renekton", "codex_strips_narrow", "rig", "source_parts")
DOC = os.path.join(ROOT, "assets", "source", "renekton", "RUN_SWAP.md")
CELL, FEET, PIVOT, Z = (128, 96), 81, (64, 88), 8
WAIST = 87                     # design rows above this stay the design's own (with the kilt, the blade and the claws)
KILT = {(238, 207, 161), (203, 163, 116), (177, 84, 47), (132, 58, 21), (92, 55, 30), (39, 32, 22)}


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def upper_body(d):
    """The design without legs and tail: rows above WAIST, the blade arm and the claw arm whole, the kilt's cloth and
    its outline between the legs; loose crumbs dropped."""
    part = {n: np.asarray(Image.open(lp(os.path.join(PARTS, n + ".png"))).convert("RGBA"))[..., 3] > 0
            for n in ("near", "far")}
    yy, xx = np.indices(d.shape[:2])
    op = d[..., 3] > 0
    kilt = np.zeros(op.shape, bool)
    for c in KILT:
        kilt |= (d[..., :3] == c).all(-1)
    keep = op & ((yy < WAIST) | part["near"] | part["far"] | (kilt & (xx >= 48) & (xx <= 68)))
    dark = op & ((d[..., :3] * [0.299, 0.587, 0.114]).sum(-1) < 25)
    nb = np.zeros_like(keep)
    nb[1:] |= keep[:-1]
    nb[:-1] |= keep[1:]
    nb[:, 1:] |= keep[:, :-1]
    nb[:, :-1] |= keep[:, 1:]
    keep |= dark & nb & (xx >= 47) & (xx <= 69) & (yy >= WAIST)
    out = d.copy()
    out[~keep] = 0
    # drop islands under 6 squares (crumbs of the cut)
    seen = np.zeros(op.shape, bool)
    for y0, x0 in zip(*np.nonzero(out[..., 3] > 0)):
        if seen[y0, x0]:
            continue
        stack, comp = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < 128 and 0 <= nx < 128 and out[ny, nx, 3] > 0 and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if len(comp) < 6:
            for y, x in comp:
                out[y, x] = 0
    return out


def in_cell(a):
    """A design-canvas picture placed in one cell (feet on row FEET, pivot on column PIVOT[0]) on green."""
    cw, ch = CELL
    cell = np.zeros((ch, cw, 4), np.uint8)
    cell[...] = (0, 255, 0, 255)
    ys, xs = np.nonzero(a[..., 3] > 0)
    cell[ys - (PIVOT[1] + 11 - FEET), xs] = a[ys, xs]
    return cell


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "renekton_packs"))
    a = ap.parse_args()
    pack = os.path.join(a.out, "renekton_run_swap_pack")
    if os.path.exists(pack):
        shutil.rmtree(pack)
    os.makedirs(pack)
    shutil.copyfile(os.path.join(POSE, "renekton_native_run.png"), os.path.join(pack, "1_skeleton_run.png"))
    shutil.copyfile(os.path.join(POSE, "renekton_pose_run.png"), os.path.join(pack, "2_league_run_pose.png"))
    with open(os.path.join(POSE, "renekton_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    with open(os.path.join(pack, "renekton_run_cells.json"), "w", encoding="utf-8") as f:
        json.dump({"cell": cells["cell"], "run": cells["tags"]["run"]}, f, indent=1)
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    up(d).save(os.path.join(pack, "3_renekton_design.png"))
    up(in_cell(d)).save(os.path.join(pack, "4_renekton_idle_cell.png"))
    up(in_cell(upper_body(d))).save(os.path.join(pack, "5_renekton_upper_body.png"))
    shutil.copyfile(DOC, os.path.join(pack, "RUN_SWAP.md"))
    zp = shutil.make_archive(pack, "zip", pack)
    print("written", zp)


if __name__ == "__main__":
    main()
