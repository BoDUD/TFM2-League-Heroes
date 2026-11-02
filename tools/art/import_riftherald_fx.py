#!/usr/bin/env python3
"""Import the Rift Herald's effects (assets/source/riftherald/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft
pack's sheets tft_riftherald_fx and tft_riftherald_big and its icons.

    python tools/art/import_riftherald_fx.py [--review out.png]

The source is tools/art/process_riftherald_fx.py's read of the user's Gemini sheet (assets/source/riftherald/gemini_fx:
pixel_1x/riftherald_fx_<name>.png, one row of equal frames at game size, alpha 0 / 255; cells.json their frames and
cell; icons/riftherald_icon_<name>.png 64 x 64). Every frame is placed as the kit plays it: spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked symmetric left to right (it has no
flying one).
Anchors: the hits on the struck body (HIT); the stun ring over the stunned head (HEAD); the spin's ground ring with its
middle on its soles, the slow, the charge's crash and the slam with their cells' bottom on the soles (SOLES); the roar's
rings and the warp armour with their bottom just under its own soles (ITS: the 44-px beast).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_riftherald_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "riftherald", "gemini_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
FLY = (0, 0)                    # a projectile's own point
SOLES = (0, 11)                 # on the ground under a unit (or under its own pivot)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


HEAD = (0, -34)                 # over the head of a 32-46 px unit
ITS = (0, 13)                   # under the beast's own soles (its rings and plates stand round its 44-px body)

# effect -> (anchor: "core" = the cell's middle, "foot" = its bottom middle; frames with ms; spots)
FX = {
    # Rending Pincer: the gash on the struck
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Spin Sweep: the ground ring round it (one spin, 40 ticks), the slash on the swept, the void at their feet
    "q_spin": ("core", seq(range(6), [60, 70, 80, 100, 120, 140]), [SOLES]),
    "q_hit": ("core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    "q_slow": ("foot", loop(6, 120), [SOLES]),
    # Void Charge: the ram, the crash where it stops, the stunned eyes
    "e_hit": ("core", seq(range(5), [40, 60, 80, 100, 120]), [HIT]),
    "e_crash": ("foot", seq(range(6), [50, 70, 90, 120, 150, 200]), [SOLES]),
    "e_stun": ("core", loop(6, 110), [HEAD]),
    # Warp Armor: the roar round it, the slam on the ground, the floating plates
    "r_roar": ("foot", seq(range(6), [70, 80, 100, 120, 140, 160]), [ITS]),
    "r_slam": ("foot", seq(range(7), [50, 70, 90, 120, 150, 180, 220]), [(0, 15)]),
    "r_armor": ("foot", loop(6, 130), [ITS]),
}
ICONS = {"skill": "tft_riftherald_skill", "skill2": "tft_riftherald_skill2", "ult": "tft_riftherald_ult"}


def cells(name, meta):
    """The frames of an effect, symmetry checked."""
    e = meta[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"riftherald_fx_{name}.png"))).convert("RGBA")).copy()
    w, h = e["cell"]
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    if a.shape[0] != h or a.shape[1] != w * e["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {e['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(e["frames"])]
    for k, c in enumerate(out):
        flip = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == flip).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric " + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1]


def icon(name):
    return Image.open(lp(os.path.join(SRC, "icons", f"riftherald_icon_{name}.png"))).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here (nothing else written)")
    a = ap.parse_args()
    with open(lp(os.path.join(SRC, "cells.json")), encoding="utf-8") as f:
        meta = json.load(f)
    if set(meta) != set(FX):
        sys.exit(f"processed {sorted(set(meta) ^ set(FX))} differ from the list")
    allc = {n: cells(n, meta) for n in FX}
    for n, (_, frames, _) in FX.items():
        if max(k for k, _ in frames) >= len(allc[n]):
            sys.exit(f"{n}: plays frame {max(k for k, _ in frames) + 1} of {len(allc[n])}")
    if a.review:
        import process_riftherald_fx as PR
        PR.B.review(allc, a.review)
        return
    tables = {"tft_riftherald_fx": {}, "tft_riftherald_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_riftherald_big" if tag in BIG else "tft_riftherald_fx"][tag] = out
        print(f"{tag:8s} {cs[0].shape[1]}x{cs[0].shape[0]}, {kind}, {len(out)} frames")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        icon(src).save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")


if __name__ == "__main__":
    main()
