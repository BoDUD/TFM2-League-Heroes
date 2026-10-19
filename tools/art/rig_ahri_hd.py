#!/usr/bin/env python3
"""league_ahri redone dense from Codex's picture A (tools/art/design_ahri_hd.py: 54 x 69, drawn at 85 %: PPU 69 / 34;
the user, 2026-10-20: 「A 正式稿原样」, 「太大了 得缩小一点」, 「85%」), every action posed after League's own clip frame
by frame the way league_leblanc was (tools/art/rig_leblanc_hd.py).

    python tools/art/design_ahri_hd.py                                           # hd/design.png
    python tools/lol/league_joints.py assets/source/ahri/poses.json --out <dir>  # League joints (once)
    python tools/art/rig_ahri_hd.py --joints <dir>/ahri_joints.json --review DIR # every tag at 3x + GIFs
    python tools/art/rig_ahri_hd.py --joints <dir>/ahri_joints.json              # orig strips + the 1x sheet

The figure - head, body, arms and the nine tails in their bunch at her back - moves as one with League's pelvis
(LUNGE of its way forward, its rise kept, never down into the ground), losslessly: whole squares only. The tags, frame
counts and ms are the sheet's (the kit's timing). The idle breathes: the figure above the boots' tops a row down on
frames 2-5 (the shins a row shorter). The death lays the figure down a quarter turn after League's fall.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "ahri"
ROWS = 34                                    # game rows ear tips to soles (her 40 now at 85 %)
DESIGN_ROWS = 69
PPU = DESIGN_ROWS / ROWS
SPEC_HEIGHT = 32                             # assets/source/ahri/poses.json "height"
SQUARE = XZ.SQUARE
STAND_COL = 38.5                             # the column between her soles
BREATHE_ROW = 64                             # rows above it go down a row on the breathing frames (the boots' tops)
IDLE_SINK = [0, 0, 1, 1, 1, 1, 0, 0]
LUNGE = 0.6


def lp(path):
    return R.lp(path)


def picture():
    hd = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
    d = np.asarray(Image.open(lp(os.path.join(hd, "design.png"))).convert("RGBA"))
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(hd, "picture.png")))
    return d


def design():
    want = picture()
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE, foot_x=STAND_COL * SQUARE)
    if D.d.shape != want.shape or (D.d != want).any() or D.gx0 != 0 or D.gy0 != 0:
        sys.exit("hd/picture.png does not read back as hd/design.png")
    op = D.d[..., 3] > 0
    D.pal = np.unique(D.d[op][:, :3], axis=0).astype(np.uint8)
    D.part("upper", D.rest(), take=False)
    return D


def make_rig(D):
    return R.Rig(D, pad=(60, 60, 60, 30))


def body_at(rig, dx=0, dy=0):
    can = R.compose(rig, [("upper", dict(dx=dx, dy=dy))])
    can[rig.GY:] = 0
    return can


def pose(rig, joints, j):
    d = joints["design"]
    s = rig.D.ppu * ROWS / SPEC_HEIGHT
    dx = int(round((j["pelvis"][0] - d["pelvis"][0]) * s * LUNGE))
    dy = int(round(min(0.0, (j["pelvis"][1] - d["pelvis"][1]) * s)))
    return body_at(rig, dx, dy)


def idle_frame(rig, sink):
    can = body_at(rig)
    if sink:
        y = rig.oy + BREATHE_ROW
        top = can[:y].copy()
        can[sink:y + sink] = top
        can[:sink] = 0
    return can


def frames(rig, joints):
    sheet = R.sheet_of(HERO)
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in sheet:
            continue
        ms = [m for _, m in sheet[tag]]
        rows = R.fit_rows(rows, len(ms))
        if tag == "idle":
            fr = [idle_frame(rig, IDLE_SINK[i % len(IDLE_SINK)]) for i in range(len(ms))]
        else:
            fr = [pose(rig, joints, r["j"]) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            lie = R.lie(rig, body_at(rig), k=1)
            fr = fr[:4] + [lie.copy() for _ in fr[4:]]
        out[tag] = list(zip(fr, ms))
    for t in sheet:
        if t not in out:
            sys.exit(f"{t}: no League frames")
    return {t: out[t] for t in sheet}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", required=True, help="tools/lol/league_joints.py's ahri_joints.json")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = make_rig(D)
    acts = frames(rig, joints)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
