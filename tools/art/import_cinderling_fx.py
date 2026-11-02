#!/usr/bin/env python3
"""Import the Cinderling's (绯红树怪) effects (assets/source/cinderling/PROMPTS_FX.md: 14 pictures and 3 skill icons) as
the tft pack's sheets tft_cinderling_fx and tft_cinderling_big and its icons.

    python tools/art/import_cinderling_fx.py [--review out.png]

The source is the user's Gemini sheet cleaned by tools/art/clean_cinderling_fx.py (assets/source/cinderling/gemini_fx/
clean: pixel_1x/cinderling_fx_<name>.png, one row of equal frames each at game size, the cell sizes in its
manifest.json; alpha 0 / 255; every frame symmetric - left to right, the three flying leaves top to bottom - checked
again here, the earth's three left as drawn; cinderling_icon_<slot>.png 64 x 64). Each frame is cut and placed as the kit plays it (import_cinderling_fx.py's
way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Anchors: "core" (the
cell's middle) or ("row", r): the cell's row r on the spot. The flying leaves on their own point; the hits on the upper
body; the burn's flames (cell row 25) on the soles; the wound mark over the head; the dig, the burst out and the mud
on the ground (their lowest rows); the ult's fire behind it standing (its lowest row on the soles); the burning-leaf
arc round its lower body (behind it); Scarlet Buff's ember crown (its top row) just above its leaf tips (30 game px tall). Times
from the kit (build_cinderling.P, 60 ticks a second).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_cinderling_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "cinderling", "gemini_fx", "clean")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
EARTH = {"e_dig", "e_pop", "e_slow"}   # heaps of dirt: no front or back, kept as Gemini drew them (not mirrored)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
FLY = (0, 0)                    # a projectile's own point
SOLES = (0, 11)                 # on the ground under a unit
OVER = (0, -34)                 # over a unit's head
CROWN = (0, -22)                # just above its leaf tips (30 tall, soles 11 under the pivot)
LOW = (0, 5)                    # round its lower body, behind it (the arc would hide it in front)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("row", r), frames with ms, spots)
FX = {
    "a_leaf": ("a_leaf", "core", loop(4, 60), [FLY]),
    "a_hit": ("a_hit", "core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_full": ("p_full", ("row", 0), loop(6, 100), [CROWN]),
    "p_burn": ("p_burn", ("row", 25), loop(6, 100), [SOLES]),
    "q_leaf": ("q_leaf", "core", loop(4, 50), [FLY]),
    "q_hit": ("q_hit", "core", seq(range(5), [40, 50, 60, 70, 90]), [HIT]),
    "q_wound": ("q_wound", "core", loop(6, 120), [OVER]),
    "e_dig": ("e_dig", ("row", 17), seq(range(5), [60, 60, 70, 80, 100]), [SOLES]),
    "e_pop": ("e_pop", ("row", 25), seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES]),
    "e_slow": ("e_slow", ("row", 7), loop(6, 110), [SOLES]),
    "r_cast": ("r_cast", ("row", 47), seq(range(6), [50, 60, 70, 80, 90, 110]), [SOLES]),
    "r_blaze": ("r_blaze", "core", loop(6, 90), [LOW]),
    "r_leaf": ("r_leaf", "core", loop(4, 60), [FLY]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 60, 70, 80]), [HIT]),
}
ICONS = {"icon_skill": "tft_cinderling_skill", "icon_skill2": "tft_cinderling_skill2", "icon_ult": "tft_cinderling_ult"}
MAN = {e["file"]: e for e in json.load(open(os.path.join(SRC, "manifest.json"), encoding="utf-8"))}


def cells(name):
    """The frames of the cleaned game-size sheet, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"cinderling_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = MAN[f"cinderling_fx_{name}.png"]["cell_1x"]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for k, c in enumerate(out):
        if name in FLYING and not (c == c[::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric top to bottom")
        if name not in FLYING | EARTH and not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, kind[1]]   # ("row", r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    allc = {n: cells(n) for n in sorted({src for src, *_ in FX.values()})}
    tables = {"tft_cinderling_fx": {}, "tft_cinderling_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        if len(frames) != len(cs):
            sys.exit(f"{tag}: {len(frames)} timings for {len(cs)} frames")
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_cinderling_big" if tag in BIG else "tft_cinderling_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"cinderling_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"cinderling_{src}.png is {im.size}, not 64 x 64")
        im.save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")
    if a.review:
        Z = 6
        rows = []
        for name, cs in allc.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append(img)
        sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
        y = 0
        for r in rows:
            sheet.alpha_composite(r, (0, y))
            y += r.height + 8
        sheet.convert("RGB").save(a.review)
        print(a.review)


if __name__ == "__main__":
    main()
