#!/usr/bin/env python3
"""Self-check of the frames tools/art/rig_<hero>_hd.py poses (the user, 2026-10-16: 「你做完了自己内部review 完美了再喊我
review 蕾欧娜我都看到手断了」), before anything is shown:

    python tools/art/ppu_rig_audit.py [--hero nami ...] [--sheet DIR] [--joints DIR]

Per frame (the body after ppu_rig.tidy, effects left out): the pieces it falls into (8-connected: a one-square line
of a thin post or staff holds together at its corners) and their sizes; the holes (clear squares closed in by the figure)
next to the idle's own; and with --sheet, every frame at 6x with each piece but the biggest tinted red and every new
hole magenta, one PNG per tag, for looking at. --joints: the folder of tools/lol/league_joints.py's <hero>_joints.json
for the rigs posed after League's clips.
"""
import argparse
import importlib
import inspect
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HEROES = ["morgana", "nami", "janna"]
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def body_of(c, rig):
    return rig.finish(c["body"] if isinstance(c, dict) else c)


def pieces(a):
    op = a[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if not n:
        return lbl, []
    sz = ndimage.sum(op, lbl, range(1, n + 1)).astype(int)
    return lbl, sorted(((int(s), k + 1) for k, s in enumerate(sz)), reverse=True)


def holes(a):
    op = a[..., 3] > 0
    h = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(h, structure=CROSS)
    return h, n, int(h.sum())


def audit(hero, sheet_dir=None, joints_dir=None):
    mod = importlib.import_module(f"rig_{hero}_hd")
    D = mod.design()
    rig = mod.make_rig(D) if hasattr(mod, "make_rig") else R.Rig(D)
    fn = mod.actions if hasattr(mod, "actions") else mod.frames
    args = [rig]
    if "joints" in inspect.signature(fn).parameters:
        with open(os.path.join(joints_dir, f"{hero}_joints.json"), encoding="utf-8") as f:
            args.append(json.load(f))
    acts = fn(*args)
    _, _, idle_holes = holes(body_of(acts["idle"][0][0], rig))
    report = []
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            a = body_of(c, rig)
            lbl, ps = pieces(a)
            hm, hn, ha = holes(a)
            extra = [s for s, _ in ps[1:]]
            flag = []
            if extra:
                flag.append(f"pieces {extra}")
            if ha > idle_holes + 2:
                flag.append(f"holes {ha} (idle {idle_holes})")
            if flag:
                report.append(f"{hero} {tag}[{i}]: " + "; ".join(flag))
            if sheet_dir:
                t = a.copy()
                for _, k in ps[1:]:
                    t[lbl == k] = (255, 0, 0, 255)
                t[hm] = (255, 0, 255, 255)
                tiles.append(t)
        if sheet_dir and tiles:
            allc = np.max([t[..., 3] for t in tiles], 0)
            ys, xs = np.nonzero(allc)
            y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
            z = 6
            w, h = (x1 - x0) * z, (y1 - y0) * z
            img = Image.new("RGB", (len(tiles) * (w + 8), h), (60, 60, 60))
            for j, t in enumerate(tiles):
                bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
                bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
                img.paste(bg.convert("RGB").resize((w, h), Image.NEAREST), (j * (w + 8), 0))
            os.makedirs(sheet_dir, exist_ok=True)
            img.save(os.path.join(sheet_dir, f"{hero}_{tag}.png"))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", action="append")
    ap.add_argument("--sheet")
    ap.add_argument("--joints")
    a = ap.parse_args()
    total = 0
    for hero in a.hero or HEROES:
        rep = audit(hero, a.sheet, a.joints)
        total += len(rep)
        print(f"== {hero}: {len(rep)} frames flagged")
        for line in rep:
            print("  " + line)
    print("flagged frames:", total)


if __name__ == "__main__":
    main()
