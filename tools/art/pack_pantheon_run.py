#!/usr/bin/env python3
"""Pantheon's run redo pack for Codex (assets/source/pantheon/RUN_REDO.md): only the legs of the 8 run frames redrawn on
League's run, the upper bodies of Codex's step-2 run kept.

    python tools/lol/pose_joints.py assets/source/pantheon/poses.json --tag run --json %TEMP%/pn_work/run_joints.json
    python tools/art/pack_pantheon_run.py [--out %TEMP%/pn_work/pantheon_run_pack]

Codex's step-2 run (assets/source/pantheon/codex_strips, 2026-10-16) has a good upper body (the lean, the cape, the
spear held level, the shield) but the same leg in front in all eight frames: the right foot planted ahead, the left
kicked behind (a gallop, never a crossing step - the run rule, run-crossing-root-causes). The legs are re-posed by
Codex, not by me: re-posing them losslessly is impossible (no rotations allowed) and my own leg drawings were rejected
before (LeBlanc), so this pack gives each frame's leg skeleton from League's own run (pose_joints: hip, knee, foot,
toe of both legs per frame, game px from the pivot): the near leg (League's L, toward the camera) red, the far leg (R)
blue, scaled LEG times to the design's shorter legs (design belt row 34 -> soles 65: 30 squares against League's ~35)
and put on our grid (1.5 squares a game px, the pivot at column PIV_X, the ground under row SOLE). x comes from the
frame's own belt centre plus League's hip-relative x; y from the ground (the planted foot on the red line), so the
hip marks give the run's bob too.
Writes <out>/ (and <out>.zip): RUN_REDO.md, design/ (the design 10 px a square + 1x), now/ (Codex's run frames as they
are), guide/ (each frame with its legs faded and the skeleton drawn over), refs/ (League's run contact sheet).
"""
import argparse
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "pantheon")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "pn_work")
STRIPS = os.path.join(SRC, "codex_strips")
PX = 10
CW = 1536
SOLE = 140                      # the soles' row (ground under it)
PIV_X = 66                      # the standing point's column
DENS = 1.5                      # squares a game pixel
LEG = 0.86                      # League's legs to the design's
BELT = [(207, 3, 54), (159, 5, 39), (120, 1, 35), (73, 1, 24), (200, 24, 27)]
NEAR, FAR = (230, 30, 30, 255), (30, 90, 240, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def belt(a):
    """(row, centre column) of the rope belt: the row with the most belt red between columns 40 and 110."""
    rgb = a[..., :3].astype(int)
    m = np.zeros(a.shape[:2], bool)
    for c in BELT:
        m |= np.abs(rgb - c).sum(-1) < 20
    m &= a[..., 3] > 0
    m[:, :40] = False
    m[:, 110:] = False
    row = int(m.sum(1).argmax())
    xs = np.nonzero(m[row])[0]
    return row, float(xs.mean())


def joints(path):
    t = json.load(open(path, encoding="utf-8"))
    frames = t["frames"] if isinstance(t, dict) and "frames" in t else t
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "pantheon_run_pack"))
    ap.add_argument("--joints", default=os.path.join(TMP, "run_joints.json"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    for sub in ("design", "now", "guide", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, PX, 0), PX, 1)).save(os.path.join(out, "design", "pantheon_design.png"))
    Image.fromarray(des).save(os.path.join(out, "design", "pantheon_design_1x.png"))
    js = joints(a.joints)
    table = []
    for k in range(8):
        name = f"pantheon_run_{k + 1}"
        f1 = np.asarray(Image.open(lp(os.path.join(STRIPS, name + "_1x.png"))).convert("RGBA"))
        # the repo keeps Codex's 1x copies only: the 1536 frame is every square PX x PX (Codex's own big frame was that)
        big = Image.fromarray(np.repeat(np.repeat(f1, PX, 0), PX, 1))
        canvas = Image.new("RGBA", (CW, CW), (0, 0, 0, 0))
        canvas.paste(big, (0, 0))
        canvas.save(os.path.join(out, "now", name + ".png"))
        row, cx = belt(f1)
        j = js[k]["joints"] if isinstance(js[k], dict) and "joints" in js[k] else js[k]
        hip = ((j["L_Hip"][0] + j["R_Hip"][0]) / 2.0)
        pts = {}
        for side in ("L", "R"):
            for part in ("Hip", "KneeLower", "Foot", "Toe"):
                x, y = j[f"{side}_{part}"][0], j[f"{side}_{part}"][1]
                # x: from the frame's belt centre; y: from the ground (League's soles at +11), legs scaled to ours
                X = cx + (x - hip) * DENS * LEG
                Y = (SOLE + 1) - (11 - y) * DENS * LEG
                pts[(side, part)] = (X, Y)
        # the guide: Codex's frame, everything below the belt faded, the skeleton over it
        g = Image.new("RGBA", (CW, CW), (255, 255, 255, 255))
        g.alpha_composite(canvas)
        fade = Image.new("RGBA", (CW, CW), (0, 0, 0, 0))
        ImageDraw.Draw(fade).rectangle([0, (row + 3) * PX, CW, CW], fill=(255, 255, 255, 190))
        g.alpha_composite(fade)
        dr = ImageDraw.Draw(g)
        for side, col in (("R", FAR), ("L", NEAR)):
            chain = [pts[(side, p)] for p in ("Hip", "KneeLower", "Foot", "Toe")]
            xy = [(x * PX, y * PX) for x, y in chain]
            dr.line(xy, fill=col, width=7)
            for x, y in xy:
                dr.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
        dr.line([(0, (SOLE + 1) * PX), (CW, (SOLE + 1) * PX)], fill=(255, 0, 0, 255), width=3)
        dr.text((20, 20), f"run {k + 1}: red = NEAR leg (bright), blue = FAR leg (one shade darker); red line = ground",
                fill=(0, 0, 0, 255))
        g.convert("RGB").save(os.path.join(out, "guide", name + ".png"))
        table.append({"frame": k + 1, "belt_row": row, "near_foot_x": round(pts[("L", "Foot")][0], 1),
                      "far_foot_x": round(pts[("R", "Foot")][0], 1), "near_foot_y": round(pts[("L", "Foot")][1], 1),
                      "far_foot_y": round(pts[("R", "Foot")][1], 1)})
    p = os.path.join(TMP, "look", "Pantheon_Run_base.png")
    if os.path.exists(p):
        shutil.copyfile(p, os.path.join(out, "refs", "league_pantheon_run.png"))
    with open(os.path.join(out, "legs.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(table, fh, indent=1)
    shutil.copyfile(lp(os.path.join(SRC, "RUN_REDO.md")), os.path.join(out, "RUN_REDO.md"))
    zp = shutil.make_archive(out, "zip", out)
    for t in table:
        print(t)
    print(zp)


if __name__ == "__main__":
    main()
