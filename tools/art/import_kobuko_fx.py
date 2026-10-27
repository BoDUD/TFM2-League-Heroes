#!/usr/bin/env python3
"""Import Kobuko's effects (assets/source/kobuko/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's sheets
tft_kobuko_fx and tft_kobuko_big and its icons.

    python tools/art/import_kobuko_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/kobuko/codex_fx/kobuko_fx: pixel_1x/kobuko_fx_<name>.png, one row
of equal frames each at game size, the frame sizes the pack asked for (pack_kobuko_fx.FX); alpha 0 / 255; every frame
symmetric left to right - checked again here; kobuko_icon_<slot>.png 64 x 64). Each frame is cut and placed as the kit
plays it (import_loris_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under
it. Times from the kit (build_kobuko.P, 60 ticks a second).
The ground rows were measured on the cells (2026-10-27, the densest and the mean rows of each frame): the golden dome
round him (q_shield rows 0-41: its middle on his middle, the cell's row 41 on his soles - he is 40 tall); the charged
claw's spiral over his head (q_on rows 7-15, so row 66 on his soles: the spiral (its glow 12 squares across) clear over
his raised face and topknot (55 and 61 sat on his brow in the preview), the motes at his sides); the rage's flames and
ring (p_rage 42, p_burst 44); the pounce's landing ring (e_land 10); the leap's dust (r_jump 25); the landing mark
(r_mark 6, its middle); the crash's shockwave (r_slam 24, its middle row); the knock-up dust jets (e_hit 18, r_hit 22);
the stun's stars over a 36-tall unit's head (q_stun 43.5, the cell's bottom on the soles).
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
import pack_kobuko_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kobuko", "codex_fx", "kobuko_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
LIFT = {}                       # rows above the first moved up by the second (none: Codex drew the marks in place)


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_shield": ("q_shield", ("ground", 41), seq(range(6), [50, 60, 70, 80, 90, 120]), [SOLES]),
    "q_on": ("q_on", ("ground", 66), loop(6, 120), [SOLES]),
    "q_hit": ("q_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "q_stun": ("q_stun", ("ground", 43.5), loop(6, 100), [SOLES]),
    "e_land": ("e_land", ("ground", 10), seq(range(6), [60, 60, 70, 80, 100, 130]), [SOLES]),
    "e_hit": ("e_hit", ("ground", 18), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "r_jump": ("r_jump", ("ground", 25), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "r_mark": ("r_mark", ("ground", 6), seq(range(6), [100] * 6), [SOLES]),
    "r_slam": ("r_slam", ("ground", 24), seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("r_hit", ("ground", 22), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "p_burst": ("p_burst", ("ground", 44), seq(range(6), [60, 70, 70, 80, 100, 130]), [SOLES]),
    "p_rage": ("p_rage", ("ground", 42), loop(6, 120), [SOLES]),
}
ICONS = {"icon_skill": "tft_kobuko_skill", "icon_skill2": "tft_kobuko_skill2", "icon_ult": "tft_kobuko_ult"}
SIZES = {name: tuple(int(v) for v in size.replace(" ", "").split("×")) for name, _, _, size, *_ in PK.FX}


def lifted(c, split, up):
    """The rows above `split` moved `up` rows higher (the cell grows on top by `up`)."""
    out = np.zeros((c.shape[0] + up, c.shape[1], 4), np.uint8)
    out[up + split:] = c[split:]
    out[:split] = c[:split]
    return out


def cells(name):
    """The frames of Codex's game-size sheet, symmetry checked (and LIFT applied: the ground row then counts from the
    grown cell's top)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"kobuko_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = SIZES[name]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for k, c in enumerate(out):
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    if name in LIFT:
        out = [lifted(c, *LIFT[name]) for c in out]
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
    tables = {"tft_kobuko_fx": {}, "tft_kobuko_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_kobuko_big" if tag in BIG else "tft_kobuko_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"kobuko_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"kobuko_{src}.png is {im.size}, not 64 x 64")
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
