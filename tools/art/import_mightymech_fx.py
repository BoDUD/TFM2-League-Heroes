#!/usr/bin/env python3
"""Import the Mighty Mech's effects (assets/source/mightymech/PROMPTS_FX.md: 15 pictures and 3 skill icons) as the tft
pack's sheets tft_mightymech_fx and tft_mightymech_big and its icons.

    python tools/art/import_mightymech_fx.py [--review out.png]

The source is tools/art/process_mightymech_fx.py's read of the user's Gemini sheet (assets/source/mightymech/gemini_fx:
pixel_1x/mightymech_fx_<name>.png, one row of equal frames at game size, alpha 0 / 255; cells.json their frames and
cell; icons/mightymech_icon_<name>.png 64 x 64). Every frame is placed as the kit plays it: spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked symmetric left to right, the slash
wave r_slash top to bottom, pointing right.
Anchors: the hits on the struck body (HIT); the gravity mark over a taunted head (OVER); the slow, the knock-up, the
landing, the transform's blades, the blazing pillar and the Ultimate form's embers with their cells' bottom on the soles
(SOLES); the gravity field and the shockwave centred on the ground under it (GROUND); the escort's shield round a
champion's body (BODY); the slash wave from just ahead of the line's start (TAIL: its back end on the line's point).
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
import pack_mightymech_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "mightymech", "gemini_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
OVER = (0, -21)                 # just over a 30 px unit's head (its soles 11 under the pivot)
SOLES = (0, 11)                 # on the ground under a unit (or under its own pivot)
GROUND = (0, 11)                # a ground ellipse's middle on the soles
BODY = (0, -4)                  # a 30 px champion's middle
TAIL = (0, 0)                   # the slash wave's back end on the line's point
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" = the cell's middle, "foot" = its bottom middle, "tail" = its left end's middle; frames
# with ms; spots)
FX = {
    # Piston Slash: the cut, every third swing's piston chop, the crackle at the feet
    "a_hit": ("core", seq(range(3), [40, 50, 70]), [HIT]),
    "a_crush": ("foot", seq(range(4), [40, 60, 70, 90]), [(0, 2)]),
    "a_slow": ("foot", loop(6, 100), [SOLES]),
    # Gravity Matrix: the field under it, the mark over the taunted, the shockwave, its hits
    "q_stance": ("core", loop(4, 150), [GROUND]),
    "q_taunt": ("core", seq(range(4), [80, 100, 100, 120]), [OVER]),
    "q_wave": ("core", seq(range(3), [70, 90, 120]), [GROUND]),
    "q_hit": ("core", seq(range(3), [40, 60, 90]), [HIT]),
    # Mecha Leap: the landing, the knocked up
    "e_slam": ("foot", seq(range(4), [60, 80, 100, 140]), [(0, 15)]),
    "e_up": ("foot", seq(range(4), [60, 70, 80, 100]), [SOLES]),
    # Ultimate Form: Super Blade: the blades flaring behind it, the blazing pillar, the wave, its hits, the embers
    "r_transform": ("foot", seq(range(3), [90, 110, 140]), [SOLES]),
    "r_sword": ("foot", seq(range(3), [100, 120, 160]), [SOLES]),
    "r_slash": ("tail", seq(range(3), [50, 60, 80]), [TAIL]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "r_form": ("foot", loop(3, 160), [(0, 13)]),
    # Voyager Escort: the shield round whoever it guards
    "p_shield": ("core", loop(6, 110), [BODY]),
}
ICONS = {"skill": "tft_mightymech_skill", "skill2": "tft_mightymech_skill2", "ult": "tft_mightymech_ult"}


def cells(name, meta):
    """The frames of an effect, symmetry checked."""
    e = meta[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"mightymech_fx_{name}.png"))).convert("RGBA")).copy()
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
    if kind == "tail":
        return [0, (h - 1) / 2]
    return [(w - 1) / 2, h - 1]


def icon(name):
    return Image.open(lp(os.path.join(SRC, "icons", f"mightymech_icon_{name}.png"))).convert("RGBA")


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
        import process_mightymech_fx as PR
        PR.PB.review(allc, a.review)
        return
    tables = {"tft_mightymech_fx": {}, "tft_mightymech_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_mightymech_big" if tag in BIG else "tft_mightymech_fx"][tag] = out
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
