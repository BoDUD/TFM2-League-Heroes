#!/usr/bin/env python3
"""Import Violet's effects (assets/source/violet/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft pack's sheets
tft_violet_fx and tft_violet_big and its icons.

    python tools/art/import_violet_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/violet/codex_fx/violet_fx: pixel_1x/violet_fx_<name>.png, one row
of equal frames each at game size, the frame sizes the pack asked for (pack_violet_fx.FX); alpha 0 / 255; every frame
symmetric left to right - checked again here; violet_icon_<slot>.png 64 x 64). Each frame is cut and placed as the kit
plays it (import_vander_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under
it. Times from the kit (build_violet.P, 60 ticks a second).
The ground rows were measured on the cells (2026-10-28: the widest row of the frames' lower half): the uppercut's
shock ring (q_up 30), the kick-off dust (e_dash 6), the slam's shockwave (r_slam 15, its middle row), the knock-up's
dust jet (r_hit 17, its base), the fury's pink ring (r_fury 35), the second wind's green rings (p_burst 33, p_wind 32);
the punches' hits (a_hit, q_jab, e_hit) on the body. Codex's cells were cut from wider masters, so bits of a ring ran
into a neighbour's edge (r_slam most, 12-38 squares a frame): EDGE_SPECK drops the parts touching a cell's side that
are smaller than it. The icons are cut from Codex's 1254 px raws (LANCZOS to 64: its own 64 px cuts voted 2 px squares
and the gauntlets went to mud, Vander's way).
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
import pack_violet_fx as PK
from scipy import ndimage  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "violet", "codex_fx", "violet_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
LIFT = {}                       # rows above the first moved up by the second
CLEAR = {}                      # picture -> frame -> rows (from, to) emptied
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_jab": ("q_jab", "core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_up": ("q_up", ("ground", 30), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "e_dash": ("e_dash", ("ground", 6), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "e_hit": ("e_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "r_slam": ("r_slam", ("ground", 15), seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("r_hit", ("ground", 17), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "r_fury": ("r_fury", ("ground", 35), loop(6, 110), [SOLES]),
    "p_burst": ("p_burst", ("ground", 33), seq(range(5), [60, 80, 100, 120, 140]), [SOLES]),
    "p_wind": ("p_wind", ("ground", 32), loop(6, 130), [SOLES]),
}
ICONS = {"icon_skill": "tft_violet_skill", "icon_skill2": "tft_violet_skill2", "icon_ult": "tft_violet_ult"}
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"violet_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = SIZES[name]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for c in out:   # bits of a neighbour's ring at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            if part.sum() < EDGE_SPECK and (part[:, 0].any() or part[:, -1].any()):
                c[part] = 0
    for k, c in enumerate(out):
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    for k, (r0, r1) in CLEAR.get(name, {}).items():
        out[k][r0:r1] = 0
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
    tables = {"tft_violet_fx": {}, "tft_violet_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_violet_big" if tag in BIG else "tft_violet_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        # from Codex's 1254 px raw (its own 64 px cut voted 2 px squares and the gauntlets went to mud)
        im = Image.open(lp(os.path.join(SRC, "raw", f"violet_{src}.png"))).convert("RGBA").resize((64, 64), Image.LANCZOS)
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
