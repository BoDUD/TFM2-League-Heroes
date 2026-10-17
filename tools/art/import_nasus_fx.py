#!/usr/bin/env python3
"""Import Nasus's effects (assets/source/nasus/PROMPTS_FX.md, 11 pictures) as the game sheets league_nasus_fx and
league_nasus_big.

    python tools/art/import_nasus_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/nasus/codex_fx: pixel_1x/nasus_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255, symmetric left to right -
checked again here - and no dark outline round the light). Each frame is cut by the manifest's frame size and placed as
the kit plays it (import_swain_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are
11 under it, a point's ground too. Times from the kit (build_nasus.P, 60 ticks a second).
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
from build_nasus import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nasus", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"e_fire", "r_cast", "r_on"}
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -34)             # just over a unit's head (the cracked shield)
EMPTY = J.EMPTY
seq = J.seq
MS = 1000 / 60
FIRE_MS = P["e_t"] * MS                                     # Spirit Fire burns e_t ticks (5 s)
FIRE_LOOPS = 8                                               # the burning frames 3-6 played this often
fire_k = (FIRE_MS - 80 - 100 - 150 - 200) / (4 * FIRE_LOOPS)
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # a soul drawn into him as Q's kill adds stacks (on him, following)
    "q_soul": (("feet", 0), seq(range(6), [60, 70, 80, 90, 100, 120]), [SOLES]),
    # the fire where the lob lands: it starts, burns its 5 s (frames 3-6 looped), dies
    "e_fire": (("feet", 14), seq([0, 1] + [2, 3, 4, 5] * FIRE_LOOPS + [6, 7],
                                 [80, 100] + [fire_k] * (4 * FIRE_LOOPS) + [150, 200]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    # the armour shred's cracked shield over each unit standing in the fire (a buff's loop)
    "e_shred": ("core", seq(range(4), [120, 120, 120, 120]), [OVERHEAD]),
    "w_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # the withering glyph over the slowed champion (a buff's loop)
    "w_slow": (("feet", 0), seq(range(4), [130, 130, 130, 130]), [SOLES]),
    # the burst as he grows (its widest frame 4 when the big body comes: ult frame 4 at 200 ms)
    "r_cast": (("feet", 6), seq(range(7), [60, 60, 80, 100, 110, 120, 130]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the sandstorm round him while r_on lasts (a buff's loop, under him)
    "r_on": (("feet", 10), seq(range(6), [100] * 6), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
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
    return [(w - 1) / 2, h - 1 - kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = {e["name"]: e for e in json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))["effects"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_nasus_fx": {}, "league_nasus_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_nasus_big" if name in BIG else "league_nasus_fx"][name] = out
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
