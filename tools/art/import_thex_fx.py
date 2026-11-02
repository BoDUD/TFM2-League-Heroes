#!/usr/bin/env python3
"""Import T-Hex's effects (assets/source/thex/PROMPTS_FX.md: 12 pictures and 3 skill icons) as the tft pack's sheets
tft_thex_fx and tft_thex_big and its icons.

    python tools/art/import_thex_fx.py [--review out.png]

The source is tools/art/process_thex_fx.py's read of the user's Gemini sheet (assets/source/thex/gemini_fx:
pixel_1x/thex_fx_<name>.png, one row of equal frames at game size, alpha 0 / 255; cells.json their frames and cell;
icons/thex_icon_<name>.png 64 x 64). Every frame is placed as the kit plays it: spots are game px from the pivot (x
forward, y down); a unit's soles are 11 under it. Every picture is checked symmetric left to right, the flying bullet
a_bullet and the laser r_beam top to bottom, pointing right.
Anchors: the hits on the struck body (HIT); the bullet and the laser on their own point (FLY); the launch on its back
(BACK: the picture's bottom on it); the falling missile, the dash dust, the static at the feet, the shield and the
mech's burst with their cells' bottom on the soles of whoever carries them or where they land (SOLES).
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
import pack_thex_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "thex", "gemini_fx")
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
BACK = (0, -6)                  # T-Hex's back, where the pods open (the picture is symmetric: never off to one side)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" = the cell's middle, "foot" = its bottom middle; frames with ms; spots)
FX = {
    # Gatling Barrage: the bullet in flight, its hit, every fourth attack's hextech round
    "a_bullet": ("core", loop(2, 60), [FLY]),
    "a_hit": ("core", seq(range(3), [40, 50, 70]), [HIT]),
    "a_crit": ("core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    # Homing Missiles: the launch off its back, a missile falling and bursting (the ult's missiles too)
    "q_launch": ("foot", seq(range(3), [60, 80, 110]), [BACK]),
    "q_fall": ("foot", seq(range(7), [50, 50, 50, 40, 60, 90, 120]), [SOLES]),
    # Rex Charge: the dust where it sets off, the bite, the static at the feet
    "e_dash": ("foot", seq(range(4), [50, 60, 80, 110]), [SOLES]),
    "e_hit": ("core", seq(range(3), [50, 60, 90]), [HIT]),
    "e_slow": ("foot", loop(2, 120), [SOLES]),
    # Hex Armory: the laser, its burn, the hex shield
    "r_beam": ("core", loop(2, 60), [FLY]),
    "r_hit": ("core", seq(range(3), [40, 60, 90]), [HIT]),
    "r_shield": ("foot", loop(2, 200), [(0, 15)]),
    # Pilot Eject: the mech bursting where it fell
    "p_blast": ("foot", seq(range(5), [50, 70, 90, 140, 200]), [SOLES]),
}
ICONS = {"skill": "tft_thex_skill", "skill2": "tft_thex_skill2", "ult": "tft_thex_ult"}


def cells(name, meta):
    """The frames of an effect, symmetry checked."""
    e = meta[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"thex_fx_{name}.png"))).convert("RGBA")).copy()
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
    return Image.open(lp(os.path.join(SRC, "icons", f"thex_icon_{name}.png"))).convert("RGBA")


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
        import process_thex_fx as PR
        PR.PB.review(allc, a.review)
        return
    tables = {"tft_thex_fx": {}, "tft_thex_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_thex_big" if tag in BIG else "tft_thex_fx"][tag] = out
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
