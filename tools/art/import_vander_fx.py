#!/usr/bin/env python3
"""Import Vander's effects (assets/source/vander/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's sheets
tft_vander_fx and tft_vander_big and its icons.

    python tools/art/import_vander_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/vander/codex_fx/vander_fx: pixel_1x/vander_fx_<name>.png, one row
of equal frames each at game size, the frame sizes the pack asked for (pack_vander_fx.FX); alpha 0 / 255; every frame
symmetric left to right - checked again here; vander_icon_<slot>.png 64 x 64). Each frame is cut and placed as the kit
plays it (import_loris_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under
it. Times from the kit (build_vander.P, 60 ticks a second).
The ground rows were measured on the cells (2026-10-27): the guard's stomp ring (q_guard_in 40) and its held arcs'
ring (q_guard 37), the last stand's ember ring (r_hold 35), the Watcher's thin ring (p_watch 7.5), the kick-off dust
(e_dash 10), the uppercut's burst over its small ring (e_hit 27), the slam's shockwave (r_slam 20, its middle row), the
knock-up's dust jet (r_hit 17); the charged fist over his head (q_ready 47.5: the cell's bottom on his soles, the fist
40-46 over them, he is 40 tall), the stun's stars and the taunt's anger mark over a 36-tall unit's head (e_stun 43.5,
q_taunt 42.5). The icons are cut from Codex's 1254 px raws (LANCZOS to 64: its own 64 px
cuts voted 2 px squares and lost the gauntlet's shapes). Codex left a puff of dust floating at the top of q_guard_in's last frame (rows 0-12, over his head, from
its multi-row master): CLEAR takes it out.
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
import pack_vander_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vander", "codex_fx", "vander_fx")
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
CLEAR = {"q_guard_in": {4: (0, 13)}}   # picture -> frame -> rows (from, to) emptied


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_guard_in": ("q_guard_in", ("ground", 40), seq(range(5), [60, 70, 80, 90, 120]), [SOLES]),
    "q_guard": ("q_guard", ("ground", 37), loop(6, 120), [SOLES]),
    "q_ready": ("q_ready", ("ground", 47.5), loop(6, 110), [SOLES]),
    "q_hit": ("q_hit", "core", seq(range(6), [50, 60, 70, 80, 90, 100]), [HIT]),
    "q_taunt": ("q_taunt", ("ground", 42.5), loop(6, 100), [SOLES]),
    "e_dash": ("e_dash", ("ground", 10), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "e_hit": ("e_hit", ("ground", 27), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "e_stun": ("e_stun", ("ground", 43.5), loop(6, 100), [SOLES]),
    "r_slam": ("r_slam", ("ground", 20), seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("r_hit", ("ground", 17), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "r_hold": ("r_hold", ("ground", 35), loop(6, 120), [SOLES]),
    "p_watch": ("p_watch", ("ground", 7.5), loop(6, 160), [SOLES]),
}
ICONS = {"icon_skill": "tft_vander_skill", "icon_skill2": "tft_vander_skill2", "icon_ult": "tft_vander_ult"}
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
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"vander_fx_{name}.png"))).convert("RGBA")).copy()
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
    tables = {"tft_vander_fx": {}, "tft_vander_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_vander_big" if tag in BIG else "tft_vander_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        # from Codex's 1254 px raw (its own 64 px cut voted 2 px squares and lost the gauntlet's shapes)
        im = Image.open(lp(os.path.join(SRC, "raw", f"vander_{src}.png"))).convert("RGBA").resize((64, 64), Image.LANCZOS)
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
