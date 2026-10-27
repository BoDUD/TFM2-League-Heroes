#!/usr/bin/env python3
"""league_lucian's R bullets leave from his guns: at the guns' height, their first frames drawn ahead of the projectile.

    python tools/fix/lucian_r_muzzle.py [--check]

The user (2026-10-27, on the walking R): 「子弹也没从枪口出来」. A projectile leaves from the caster's pivot, only its
height can be set: `league_lucian_r_bullet` flew at y_offset -3000 (his belt; the attack's bullets fly at -21000), while
his guns point forward about 19 game px up and 27-30 ahead (hd_run 0, hd_ult 2-3, measured on the PPU 1.5 sheet). Now:
* every r_bullet at Y_OFFSET (the guns' height);
* its picture (league_lucian_fx `r_bullet`, drawn centred on the projectile and turned with its flight) has its first
  visible frames pushed ahead by SHIFT game px - transparent columns added behind them, twice the shift - so the dot
  appears at the muzzle while the projectile is still 12 px out (12000 a tick) and the streak sets off from there; from
  the third frame on the picture rides the projectile again, so it never overshoots the target.
The damage (the hidden `r_line`) and the timing do not change. Idempotent (the frames are rebuilt from their widths when
first padded); --check exits 1 when a file differs.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

DATA = os.path.join(ROOT, "league", "champion", "league_lucian.data_champion")
FX = os.path.join(ROOT, "league", "effects", "league_lucian_fx")
NAME = "league_lucian_r_bullet"
Y_OFFSET = -18000
ORIG_W = {1: 7, 2: 31}          # the unpadded widths of r_bullet's frames 1 and 2
SHIFT = {1: 16, 2: 4}           # game px ahead of the projectile: the muzzle ~28 px out, the projectile 12 px a tick


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def fix_data(raw):
    d = json.loads(raw.lstrip("﻿"))
    n = 0

    def walk(o):
        nonlocal n
        if isinstance(o, dict):
            if o.get("type") == "TargetProjectile" and o.get("name") == NAME:
                o["y_offset"] = Y_OFFSET
                n += 1
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d["ult"])
    if not n:
        sys.exit(f"no {NAME} in his ult")
    nl = "\r\n" if "\r\n" in raw else "\n"
    bom = "﻿" if raw.startswith("﻿") else ""
    return bom + json.dumps(d, ensure_ascii=False, indent=2).replace("\n", nl) + nl


def read_tags(stem):
    a = json.loads(open(lp(stem + "#anim.fanim"), "rb").read().decode("utf-8").lstrip("﻿"))["anims"]
    sh = np.asarray(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    tags = {}
    for tag, v in a.items():
        out = []
        for f in v["frames"]:
            d = f["data"]
            x, y, w, h = (int(round(d[k])) for k in "xywh")
            out.append((sh[y:y + h, x:x + w].copy(), f["duration"] * 1000))     # ms, kept exact (1/60 s frames)
        tags[tag] = out
    return tags


def fix_fx(tags):
    """r_bullet's frames 1 and 2 padded behind (on the left: the picture is drawn flying right); False if done."""
    frames = tags["r_bullet"]
    if all(frames[k][0].shape[1] != w for k, w in ORIG_W.items()):
        return False
    for k, w in ORIG_W.items():
        arr, ms = frames[k]
        if arr.shape[1] != w:
            sys.exit(f"r_bullet frame {k} is {arr.shape[1]} wide, neither {w} nor padded")
        pad = np.zeros((arr.shape[0], 2 * SHIFT[k], 4), np.uint8)
        frames[k] = (np.concatenate([pad, arr], axis=1), ms)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    raw = open(lp(DATA), "rb").read().decode("utf-8")
    data = fix_data(raw)
    tags = read_tags(FX)
    padded = fix_fx(tags)
    todo = (data != raw) or padded
    if a.check:
        print("already done" if not todo else "Lucian's R muzzle fix not applied")
        sys.exit(1 if todo else 0)
    if data != raw:
        open(lp(DATA), "w", encoding="utf-8", newline="").write(data)
    if padded:
        w, h = G.write_sheet(FX, tags)
        print(f"{FX}#sheet.png {w}x{h}: r_bullet frames 1-2 ahead by {SHIFT}")
    print("done" if todo else "already done")


if __name__ == "__main__":
    main()
