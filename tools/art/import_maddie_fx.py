#!/usr/bin/env python3
"""Import Maddie's effects (assets/source/maddie/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's sheets
tft_maddie_fx and tft_maddie_big and its icons.

    python tools/art/import_maddie_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/maddie/codex_fx: pixel_1x/maddie_fx_<name>.png, one row of equal
frames each at game size, the frame sizes the pack asked for (pack_maddie_fx.FX); alpha 0 / 255; the flying ones and
the muzzle flashes symmetric top to bottom, the rest left to right - checked again here; maddie_icon_<slot>.png
64 x 64). Each frame is cut and placed as the kit plays it (import_silco_fx.py's way): spots are game px from the pivot
(x forward, y down); a unit's soles are 11 under it. Times from the kit (build_maddie.P, 60 ticks a second).
The muzzle flashes a_flash and r_flash go into no sheet: rig_maddie.py draws them into her firing frames (flash()).
The ground rows were measured on the cells (2026-10-27): the Wanted ring's middle (e_wanted 43.5; e_mark is drawn for
the same unit, its badge settling 36-40 squares over the ground), the bounty's rising ring (p_bounty 44), the bounty
glow's ring (p_bounty_loop 5.5); the scope's reticle closes on its row 27.5, put on the chest (r_sight 47: 20 squares
over the soles).
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
import pack_maddie_fx as PK  # noqa: E402
from build_maddie import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "maddie", "codex_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = set(PK.FLYING) | set(PK.ASYM)          # turned with their flight / baked into her frames: top to bottom
BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
flight = J.flight
MS = 1000 / 60
OVERSHOOT = 20_000                                             # maddie.rs: a bullet flies on past its target
BULLET_MS = P["atk_range"] / P["a_speed"] * MS * 2             # the homing bullet (twice its straight flight)
FAN_MS = (P["q_range"] + OVERSHOOT) / P["q_speed"] * MS        # tft.dll's bullets fly the line out
ROUND_MS = (P["r_range"] + OVERSHOOT) / P["r_speed"] * MS
AIM_MS = (P["r_rel"] - 1) * MS                                 # the scope closes while she aims


def loop(n, ms):
    return seq(range(n), [ms] * n)


def spread(frames, total):
    """frames over `total` ms, evenly (the last takes the rounding)."""
    frames = list(frames)
    n = len(frames)
    each = [round(total / n)] * (n - 1)
    return seq(frames, each + [total - sum(each)])


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_bullet": ("a_bullet", "core", flight(4, 60, BULLET_MS, lead=1), [(0, 0)]),
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_bullet": ("q_bullet", "core", flight(4, 50, FAN_MS, lead=1), [(0, 0)]),
    "q_hit": ("q_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "e_mark": ("e_mark", ("ground", 43.5), seq(range(6), [60, 60, 70, 90, 110, 140]), [SOLES]),
    "e_wanted": ("e_wanted", ("ground", 43.5), loop(6, 120), [SOLES]),
    "p_bounty": ("p_bounty", ("ground", 44), seq(range(6), [70, 80, 90, 100, 110, 130]), [SOLES]),
    "p_bounty_loop": ("p_bounty_loop", ("ground", 5.5), loop(6, 140), [SOLES]),
    "r_sight": ("r_sight", ("ground", 47), spread(range(8), AIM_MS), [SOLES]),
    "r_round": ("r_round", "core", flight(4, 50, ROUND_MS, lead=1), [(0, 0)]),
    "r_hit": ("r_hit", "core", seq(range(7), [50, 60, 70, 80, 90, 100, 110]), [HIT]),
}
ICONS = {"icon_skill": "tft_maddie_skill", "icon_skill2": "tft_maddie_skill2", "icon_ult": "tft_maddie_ult"}
SIZES = {name: tuple(int(v) for v in size.replace(" ", "").split("×")) for name, _, _, size, *_ in PK.FX}


def cells(name):
    """The frames of Codex's game-size sheet, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"maddie_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = SIZES[name]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for k, c in enumerate(out):
        if name in TB:
            if not (c == c[::-1]).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric top to bottom")
        elif not (c == c[:, ::-1]).all():
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
    tables = {"tft_maddie_fx": {}, "tft_maddie_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_maddie_big" if tag in BIG else "tft_maddie_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"maddie_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"maddie_{src}.png is {im.size}, not 64 x 64")
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
