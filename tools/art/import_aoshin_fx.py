#!/usr/bin/env python3
"""Import Ao Shin's effects (assets/source/aoshin/PROMPTS_FX.md: 11 pictures and 3 skill icons) as the tft pack's sheets
tft_aoshin_fx and tft_aoshin_big and its icons.

    python tools/art/import_aoshin_fx.py [--review out.png]

The source is Codex's step-3 delivery made ready by tools/art/clean_aoshin_fx.py (assets/source/aoshin/codex_fx/clean:
pixel_1x/aoshin_fx_<name>.png, one row of equal frames each at game size, the pack's cell sizes (pack_aoshin_fx.FX);
alpha 0 / 255; the symmetry the pack asked for - checked again here: left to right but for the round ball (both ways),
the breath's bolt (top to bottom) and the two bolts from the sky (none); aoshin_icon_<slot>.png 64 x 64). Each frame is
cut and placed as the kit plays it (import_violet_fx.py's way): spots are game px from the pivot (x forward, y down); a
unit's soles are 11 under it. Times from the kit (build_aoshin.P, 60 ticks a second) and tft.dll (aoshin.rs).
The ground rows were measured on the cells (2026-10-28, each frame's drawn rows): the take-off whirl's base (e_cast 24),
the storm shield round his 38 px (e_shield rows 0-43: row 41 on his soles), the crackle up round him after the storm
(p_storm's ground ring 43), the bolts' strike on the ground (p_bolt 85, r_bolt 86), the storm cloud over his head
(r_cloud rows 0-21: row 63 on his soles, so it hangs 42-63 over them); the silence's crown (q_sil rows 1-13) over the
head; the hits on the body. A projectile leaves his pivot (build_aoshin a_y / q_y lift it to his snout's height), so
the ball and the breath's bolt are drawn ahead along their flight, to start at his snout (the lunge / breath frames).
"""
import argparse
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
import pack_aoshin_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aoshin", "codex_fx", "clean")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
OVER_HEAD = (0, -32)            # just over a 32-46 px unit's head
BALL_AHEAD = (8, 0)             # the ball drawn 8 px ahead along its flight: it leaves his pivot, his snout 16 ahead
BEAM_AHEAD = (22, 0)            # the breath's 40 px bolt drawn 22 ahead (its tail at his snout, 21 ahead in the frame)
seq = J.seq
SYM = {"a_ball": "both", "q_beam": "top-bottom", "p_bolt": None, "r_bolt": None}


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_ball": ("a_ball", "core", loop(4, 60), [BALL_AHEAD]),
    "a_hit": ("a_hit", "core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "q_beam": ("q_beam", "core", loop(3, 50), [BEAM_AHEAD]),
    "q_hit": ("q_hit", "core", seq(range(4), [50, 60, 70, 90]), [HIT]),
    "q_sil": ("q_sil", ("ground", 13), loop(6, 90), [OVER_HEAD]),
    "e_cast": ("e_cast", ("ground", 24), seq(range(5), [50, 60, 70, 80, 100]), [SOLES]),
    "e_shield": ("e_shield", ("ground", 41), loop(6, 110), [SOLES]),
    "p_bolt": ("p_bolt", ("ground", 85), seq(range(5), [50, 70, 80, 100, 120]), [SOLES]),
    "p_storm": ("p_storm", ("ground", 43), loop(6, 100), [SOLES]),
    "r_cloud": ("r_cloud", ("ground", 63), loop(6, 120), [SOLES]),
    "r_bolt": ("r_bolt", ("ground", 86), seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES]),
}
ICONS = {"icon_skill": "tft_aoshin_skill", "icon_skill2": "tft_aoshin_skill2", "icon_ult": "tft_aoshin_ult"}
SIZES = {name: tuple(int(v) for v in size.replace(" ", "").split("×")) for name, _, _, size, *_ in PK.FX}


def cells(name):
    """The frames of the game-size sheet, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"aoshin_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = SIZES[name]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    sym = SYM.get(name, "left-right")
    for k, c in enumerate(out):
        if sym in ("left-right", "both") and not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if sym in ("top-bottom", "both") and not (c == c[::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric top to bottom")
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
    tables = {"tft_aoshin_fx": {}, "tft_aoshin_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        if len(frames) != len(cs):
            sys.exit(f"{tag}: {len(frames)} timings for {len(cs)} frames")
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_aoshin_big" if tag in BIG else "tft_aoshin_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"aoshin_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"aoshin_{src}.png is {im.size}, not 64 x 64")
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
