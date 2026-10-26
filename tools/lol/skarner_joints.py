#!/usr/bin/env python3
"""League's Skarner skeleton at the references' camera: where each joint is in a frame, seen 3/4 facing right.

    python tools/lol/skarner_joints.py Idlebase@0 [Spell4_Hit1@100 ...] [--sticks OUT.png] [--lol D:\\WeGameApps\\lol]

The camera of tools/art/pack_skarner_picture.py's renders (pose_ref.py --yaw 35 --mirror, pitch 12): every joint of
Skarner_Rework_Base.skl posed by the clip at that time and projected to (x, y, depth) in model units, x toward the
image right (the way he faces), y DOWN, depth larger = nearer the camera. A frame is <clip>@<ms> (the .anm name without
extension, case-insensitive) or <clipA>@<ms>><clipB>@<ms>:<weight of B>, as pose_ref.py reads it.
CHAINS names the parts tools/art/pack_skarner_poses.py draws: the three tails (C = the middle one, L / R = his left /
right; seen mirrored, his right tail is the near one), the two claws (his right = near), six legs, the head and the body.
--sticks draws the frames' skeletons side by side (to check them against pose_ref's renders).
"""
import argparse
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pose_ref as P  # noqa: E402
from riot import Wad  # noqa: E402

YAW, PITCH = 35.0, 12.0
CHAINS = {
    "body": ["Hip", "Root_DT", "Torso_A", "Head"],
    "tail_c": ["Hip", "C_Tail_A", "C_Tail_B", "C_Tail_C", "C_Tail_D", "C_Tail_E", "C_Tail_F"],
    "tail_l": ["Hip", "L_Tail_A", "L_Tail_B", "L_Tail_C", "L_Tail_D", "L_Tail_E", "L_Tail_F"],
    "tail_r": ["Hip", "R_Tail_A", "R_Tail_B", "R_Tail_C", "R_Tail_D", "R_Tail_E", "R_Tail_F"],
    "claw_l": ["Torso_A", "L_Claw_A", "L_Claw_B", "L_Claw_C", "L_Claw", "L_Pincer"],
    "claw_r": ["Torso_A", "R_Claw_A", "R_Claw_B", "R_Claw_C", "R_Claw", "R_Pincer"],
    "leg_lf": ["L_LegFront_A", "L_LegFront_B", "L_LegFront_C", "L_LegFront_D"],
    "leg_lm": ["L_LegMid_A", "L_LegMid_B", "L_LegMid_C", "L_LegMid_D", "L_LegMid_E", "L_LegMid_F"],
    "leg_lb": ["L_LegBack_A", "L_LegBack_B", "L_LegBack_C", "L_LegBack_D", "L_LegBack_E", "L_LegBack_F"],
    "leg_rf": ["R_LegFront_A", "R_LegFront_B", "R_LegFront_C", "R_LegFront_D"],
    "leg_rm": ["R_LegMid_A", "R_LegMid_B", "R_LegMid_C", "R_LegMid_D", "R_LegMid_E", "R_LegMid_F"],
    "leg_rb": ["R_LegBack_A", "R_LegBack_B", "R_LegBack_C", "R_LegBack_D", "R_LegBack_E", "R_LegBack_F"],
}
STICK = {"body": (0, 170, 60), "tail_c": (0, 200, 220), "tail_l": (0, 120, 200), "tail_r": (120, 230, 255),
         "claw_l": (150, 60, 200), "claw_r": (255, 140, 0), "leg_l": (40, 90, 230), "leg_r": (230, 30, 30)}


class Skarner:
    def __init__(self, lol=r"D:\WeGameApps\lol"):
        w = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", "Skarner.wad.client"))
        self.w = w
        self.joints, _ = P.read_skl(w.read_path("assets/characters/skarner/skins/base/skarner_rework_base.skl"))
        self.index = {j["name"]: i for i, j in enumerate(self.joints)}
        refs = re.findall(rb"[A-Za-z0-9_/\.\-]+\.anm", w.read_path("data/characters/skarner/animations/skin0.bin"))
        self.anims = {os.path.splitext(os.path.basename(m.decode("latin1")))[0].lower(): m.decode("latin1") for m in refs}
        self.loaded = {}
        cy, sy = np.cos(np.radians(-YAW)), np.sin(np.radians(-YAW))   # --mirror: the other side, flipped
        cp, sp = np.cos(np.radians(PITCH)), np.sin(np.radians(PITCH))
        self.rot = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])

    def clip(self, name):
        key = name.lower()
        if key not in self.loaded:
            self.loaded[key] = P.read_anim(self.w.read_path(self.anims[key].lower()))
        return self.loaded[key]

    def frame(self, spec):
        """{joint name: (x right, y down, depth)} in model units."""
        a, ta, b, tb, wgt = P.parse_frame(spec)
        local = P.local_pose(self.joints, self.clip(a), ta)
        if b:
            local = P.blend_pose(local, P.local_pose(self.joints, self.clip(b), tb), wgt)
        glob = P.globals_(self.joints, [P.trs(*p) for p in local])
        out = {}
        for name, i in self.index.items():
            v = self.rot @ glob[i][:3, 3]
            out[name] = (-v[0], -v[1], -v[2])   # flipped left-right (mirror), y down; depth toward the camera
        return out


def sticks(frames, path, size=360):
    cells = []
    for f in frames:
        pts = [p for c in CHAINS.values() for p in (f[j] for j in c)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        k = size * 0.8 / max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
        ox, oy = size / 2 - k * (max(xs) + min(xs)) / 2, size / 2 - k * (max(ys) + min(ys)) / 2
        im = Image.new("RGB", (size, size), (225, 225, 225))
        d = ImageDraw.Draw(im)
        for name, chain in CHAINS.items():
            col = STICK.get(name, STICK.get(name[:5], (0, 0, 0)))
            q = [(ox + k * f[j][0], oy + k * f[j][1]) for j in chain]
            d.line(q, fill=col, width=3)
            for x, y in q:
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=col)
        cells.append(im)
    sheet = Image.new("RGB", (size * len(cells), size), (255, 255, 255))
    for i, c in enumerate(cells):
        sheet.paste(c, (i * size, 0))
    sheet.save(path)
    print(path, sheet.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames", nargs="+")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--sticks")
    a = ap.parse_args()
    sk = Skarner(a.lol)
    frames = [sk.frame(s) for s in a.frames]
    if a.sticks:
        sticks(frames, a.sticks)
    else:
        for s, f in zip(a.frames, frames):
            print(s)
            for name, chain in CHAINS.items():
                print(f"  {name:7s}", " ".join(f"({f[j][0]:.0f},{f[j][1]:.0f})" for j in chain))


if __name__ == "__main__":
    main()
