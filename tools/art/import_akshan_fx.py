#!/usr/bin/env python3
"""Import Akshan's effects (assets/source/akshan/PROMPTS_FX.md, 14 pictures) as the game sheets league_akshan_fx and
league_akshan_big.

    python tools/art/import_akshan_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/akshan/codex_fx: pixel_1x/akshan_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; symmetric left to right - checked again
here - except the three flying pictures, drawn pointing right). Each frame is cut by the manifest's frame size and placed
as the kit plays it (import_wukong_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are
11 under it. Times from the kit (build_akshan.P, 60 ticks a second): the hook's rope stays up through the swing.
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
from build_akshan import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "akshan", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"e_hook", "w_camo", "r_lock"}
FLYING = {"a_shot", "q_rang", "r_bullet"}      # drawn pointing right; the game turns them (no symmetry asked)
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


SWING = (P["e_hook"] + P["e_n"] * P["e_every"]) * MS     # the hook's rope up through the swing
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the shots (projectiles: the picture's middle on the projectile)
    "a_shot": ("core", loop(3, 60), [(0, 0)]),
    "q_rang": ("core", loop(4, 50), [(0, 0)]),
    "r_bullet": ("core", loop(3, 60), [(0, 0)]),
    # the hits on a unit
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # on him: the catch at his chest, the hook's rope (its bottom over his head), the camouflage, the lock sigil
    "q_catch": (("feet", 0), seq(range(3), [50, 60, 70]), [SOLES]),
    # the rope's foot drawn 46 rows over the cell's bottom (the raised gun's tip) floated 8 px over his hair, and a centred
    # picture cannot follow the gun to his side (never mirrored on the red side): set 8 rows lower, the rope starts on
    # his head, the same on both sides
    "e_hook": (("feet", -8), seq(range(5), [50, 60, 60, 80, max(100, SWING - 250)]), [SOLES]),
    "w_camo": (("feet", 4), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "r_lock": (("feet", 0), seq(range(5), [50, 60, 80, 90, 100]), [SOLES]),
    # buffs (looped): the shield, the speed streaks, the add-on's Scoundrel mark over an enemy
    "p_sh": (("feet", 2), loop(4, 120), [SOLES]),
    "w_ms": (("feet", 3), loop(4, 80), [SOLES]),
    "w_mark": (("feet", 0), loop(4, 130), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name not in FLYING and not (c == c[:, ::-1]).all():
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
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    # Codex's manifest (2026-10-18): "assets", each with name, file (the 8x sheet's name, the same in pixel_1x/), frames
    # and cell_1x
    # Codex's manifest (2026-10-18): "effects", each with name, pixel_1x, frames and cell_1x
    meta = {e["name"]: e for e in man["effects"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_akshan_fx": {}, "league_akshan_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_akshan_big" if name in BIG else "league_akshan_fx"][name] = out
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
