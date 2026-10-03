#!/usr/bin/env python3
"""Where League's joints are at game size: a tag's frames as tools/lol/native_pose.py renders them, joint by joint.

    python tools/lol/pose_joints.py assets/source/caitlyn/poses.json --tag run
        [--joints L_Hip,L_KneeLower,L_Foot,L_Toe,R_Hip,R_KneeLower,R_Foot,R_Toe] [--names] [--json OUT]

The same model, chibi proportions, camera and scale as native_pose.py with that spec. Each joint is printed as
(x, y, z) in game px: x from the pivot (right +), y down from the pivot with the frame's lowest leg point on the soles'
row (11, as the render's "flat" placement puts it; a frame whose whole body is off the ground is lifted as the render
lifts it), z toward the camera. --names lists the skeleton's joints. Used to draw legs on League's poses
(the first Caitlyn design's run legs, 2026-10-01; its script was retired with that design).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import native_pose as N  # noqa: E402

LEGS = "L_Hip,L_KneeLower,L_Foot,L_Toe,R_Hip,R_KneeLower,R_Foot,R_Toe"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--tag", default="run")
    ap.add_argument("--joints", default=LEGS)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol", help="League install folder")
    ap.add_argument("--names", action="store_true", help="list the skeleton's joints and stop")
    ap.add_argument("--json", help="also write the table here")
    a = ap.parse_args()
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    cam, chibi = spec["camera"], dict(spec["chibi"])
    keep = chibi.pop("keep", None)
    N.set_cell(*spec.get("cell", N.CELL))
    ch = N.Champ(a.lol, spec["champ"], keep, spec.get("weapon", r"^weapon$"), spec.get("hide", ()),
                 spec.get("hair_part", False), spec.get("crown"), spec.get("parts", ()),
                 spec.get("hide_submeshes", False), spec.get("submesh_textures"), spec.get("glue"), spec.get("legs"))
    if a.names:
        print(" ".join(j["name"] for j in ch.joints))
        return
    rot = N.camera(cam)
    sign = -1.0 if cam.get("mirror") else 1.0
    pv, _, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())     # game px per world unit
    by = {j["name"].lower(): i for i, j in enumerate(ch.joints)}
    names = a.joints.split(",")
    t = spec["tags"][a.tag]
    table = []
    for f in t["frames"]:
        opt = f[2] if len(f) > 2 else {}
        pv, glob, lift = ch.posed(f[0], chibi, opt.get("turn", 0.0), opt.get("head_like", t.get("head_like")),
                                  t.get("rise", 1.0), t.get("travel", 1.0))
        lowest = (pv @ rot.T)[ch.legv, 1].min()
        air = int(round(max(0.0, pv[:, 1].min()) * unit * np.cos(np.radians(cam["pitch"]))))
        row = {}
        for n in names:
            c = rot @ (glob[by[n.lower()]][:3, 3] + np.array([0.0, lift, 0.0]))
            row[n] = [round(sign * c[0] * unit, 2), round(11 - air - (c[1] - lowest) * unit, 2), round(c[2] * unit, 1)]
        table.append({"frame": f[0], "air": air, "joints": row})
        print(f[0], " ".join(f"{n}:({v[0]:+.1f},{v[1]:+.1f},z{v[2]:+.0f})" for n, v in row.items()))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(table, f, indent=1)


if __name__ == "__main__":
    main()
