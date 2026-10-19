#!/usr/bin/env python3
"""Import Rammus's effects (assets/source/rammus/PROMPTS_FX.md, 13 pictures) as the game sheets league_rammus_fx and
league_rammus_big.

    python tools/art/import_rammus_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/rammus/codex_fx/rammus_fx: pixel_1x/rammus_fx_<name>.png, one row
of equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; every picture symmetric left
to right - checked again here). Each frame is cut by the manifest's frame size and placed as the kit plays it
(import_poppy_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a
point's ground too. Times: q_dust loops 4 x 100 ms (the add-on stamps it every 24 ticks while he rolls), r_shock plays
on each of the 3 aftershocks, the buffs loop.
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

SRC = os.path.join(ROOT, "assets", "source", "rammus", "codex_fx", "rammus_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_burst", "w_cast", "r_land", "r_shock"}
FLYING = set()                  # no projectile pictures: Powerball is his own body
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head (the mark 36-44 px over its soles)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    # Powerball: the dust under the rolling ball, the impact's sand ring round him, the hit, the slow at their feet
    "q_dust": (("feet", 0), loop(4, 100), [SOLES]),
    "q_burst": (("feet", 9), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "q_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_slow": (("feet", 0), loop(4, 100), [SOLES]),
    # Defensive Ball Curl: the flare as he curls up, the spiked shell while it lasts (a buff)
    "w_cast": (("feet", 1), seq(range(4), [60, 80, 100, 120]), [SOLES]),
    "w_on": (("feet", 1), loop(4, 150), [SOLES]),
    # Frenzying Taunt: the flare on the target, the anger mark over its head (a buff)
    "e_hit": (("feet", 0), seq(range(4), [60, 70, 80, 90]), [SOLES]),
    "e_taunt": ("core", loop(4, 100), [OVERHEAD]),
    # Soaring Slam: the landing (a point), the aftershocks (a point), the hit, the cracked ground at their feet (a buff)
    "r_land": (("feet", 14), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "r_shock": (("feet", 12), seq(range(4), [60, 70, 80, 90]), [SOLES]),
    "r_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "r_slow": (("feet", 0), loop(2, 150), [SOLES]),
}

STRAY = {}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for (nm, k), (r0, r1) in STRAY.items():
        if nm == name:
            out[k][r0:r1] = 0
    for k, c in enumerate(out):
        mirror = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    # Codex's manifest (2026-10-19): "entries", each with id, file, frames and cell_1x; the 1x sheets in pixel_1x/
    meta = {e["id"]: dict(e, pixel_1x=os.path.join("pixel_1x", e["file"])) for e in man["entries"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_rammus_fx": {}, "league_rammus_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_rammus_big" if name in BIG else "league_rammus_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
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
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        Ht = sum(r.height + 10 for _, r in rows)
        sheet = Image.new("RGB", (W, Ht), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
