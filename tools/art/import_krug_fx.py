#!/usr/bin/env python3
"""Import the Ancient Krug's effects (assets/source/krug/PROMPTS_FX.md: 15 pictures and 3 skill icons) as the tft pack's
sheets tft_krug_fx and tft_krug_big and its icons.

    python tools/art/import_krug_fx.py [--review out.png]

The source is the user's Gemini run cleaned by tools/art/clean_krug_fx.py (assets/source/krug/gemini_fx/clean:
pixel_1x/krug_fx_<name>.png, one row of equal frames each at game size, the cell sizes in its manifest.json; alpha 0 /
255; every frame symmetric left to right - checked again here; krug_icon_<slot>.png 64 x 64). Each frame is cut and
placed as the kit plays it (import_kobuko_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's
soles are 11 under it. Times from the kit (build_krug.P, 60 ticks a second) and tft.dll (krug.rs).
The ground rows were measured on the cells (2026-10-28, each frame's drawn rows and mean row): the stone shell round
him (q_shield / e_shell rows 0-43: the ring's middle on his middle, so row 41 on his soles - he is 38 tall); the shell
stomp's ring (e_cast 11); the anger mark over a 36-tall unit's head (e_taunt rows 0-13: row 47 on the soles); the
leap's dust ring (r_jump 26); the landing mark (r_mark 7, its middle); the crash's ground ring (r_slam 25); the falling
rocks landing round him (r_rocks 56); the knock-up dust jets from the feet (r_hit 23); the shattered heap (p_burst
44); the reforming ring (p_up 35); the Mini Krug's ground ring (p_mini 6).
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
import pack_krug_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "krug", "gemini_fx", "clean")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_shield": ("q_shield", ("ground", 41), seq(range(5), [60, 70, 80, 90, 120]), [SOLES]),
    "q_hit": ("q_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "e_cast": ("e_cast", ("ground", 11), seq(range(5), [60, 70, 80, 90, 110]), [SOLES]),
    "e_shell": ("e_shell", ("ground", 41), loop(6, 140), [SOLES]),
    "e_taunt": ("e_taunt", ("ground", 47), loop(6, 100), [SOLES]),
    "r_jump": ("r_jump", ("ground", 26), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "r_mark": ("r_mark", ("ground", 7), seq(range(5), [60, 60, 70, 80, 90]), [SOLES]),
    "r_slam": ("r_slam", ("ground", 25), seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("r_hit", ("ground", 23), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "r_rocks": ("r_rocks", ("ground", 56), seq(range(8), [70, 70, 70, 70, 80, 90, 110, 130]), [SOLES]),
    "r_rock_hit": ("r_rock_hit", "core", seq(range(4), [60, 60, 70, 90]), [HIT]),
    "p_burst": ("p_burst", ("ground", 44), seq(range(5), [70, 80, 80, 80, 90]), [SOLES]),
    "p_up": ("p_up", ("ground", 35), seq(range(6), [60, 70, 70, 70, 70, 80]), [SOLES]),
    "p_mini": ("p_mini", ("ground", 6), loop(5, 130), [SOLES]),
}
ICONS = {"icon_skill": "tft_krug_skill", "icon_skill2": "tft_krug_skill2", "icon_ult": "tft_krug_ult"}
MAN = {e["file"]: e for e in json.load(open(os.path.join(SRC, "manifest.json"), encoding="utf-8"))}


def cells(name):
    """The frames of the cleaned game-size sheet, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"krug_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = MAN[f"krug_fx_{name}.png"]["cell_1x"]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for k, c in enumerate(out):
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    allc = {n: cells(n) for n in sorted({src for src, *_ in FX.values()})}
    tables = {"tft_krug_fx": {}, "tft_krug_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        if len(frames) != len(cs):
            sys.exit(f"{tag}: {len(frames)} timings for {len(cs)} frames")
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_krug_big" if tag in BIG else "tft_krug_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"krug_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"krug_{src}.png is {im.size}, not 64 x 64")
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
