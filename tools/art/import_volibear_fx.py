#!/usr/bin/env python3
"""Import Volibear's effects (assets/source/volibear/PROMPTS_FX.md, 18 pictures) as the game sheets league_volibear_fx and
league_volibear_big.

    python tools/art/import_volibear_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/volibear/codex_fx: pixel_1x/volibear_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the flying picture (p_bolt) drawn
pointing right and symmetric top to bottom, every other one symmetric left to right - checked again here). Each frame is
cut by the manifest's frame size and placed as the kit plays it (import_poppy_fx.py's way): spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Loops (buffs: w_mark, q_ms, q_stun,
e_slow, e_sh, r_form, r_tower) run as long as their buff; the rest play once.
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

SRC = os.path.join(ROOT, "assets", "source", "volibear", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_ms", "e_cloud", "e_bolt", "e_sh", "w_heal", "r_land", "r_form", "r_tower"}
FLYING = {"p_bolt"}             # turned with its flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -28)             # over a 36-px unit's head
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # The Relentless Storm: the bolt in flight, its strike on a unit
    "p_bolt": ("core", loop(4, 50), [(0, 0)]),
    "p_hit": (("feet", 7), seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the attack's claws; Frenzied Maul: the bite, the mark (a buff), the second bite's heal on him
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "w_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "w_mark": ("core", loop(4, 120), [OVERHEAD]),
    "w_heal": (("feet", 2), seq(range(4), [60, 80, 90, 100]), [SOLES]),
    # Thundering Smash: the charge's sparks (a buff), the smash, the stun (a buff)
    "q_ms": (("feet", 3), loop(4, 90), [SOLES]),
    "q_hit": (("feet", 3), seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "q_stun": ("core", loop(4, 100), [OVERHEAD]),
    # Sky Splitter: the warning on the point, the bolt, its hit, the slow (a buff), his shield (a buff)
    "e_cloud": (("feet", 10), seq(range(4), [300, 300, 300, 400]), [SOLES]),
    "e_bolt": (("feet", 4), seq(range(5), [50, 60, 80, 90, 100]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_slow": (("feet", 3), loop(4, 100), [SOLES]),
    "e_sh": (("feet", 2), loop(4, 120), [SOLES]),
    # Stormbringer: the landing, the hit, the storm form (a buff), the silenced tower (the add-on's buff)
    "r_land": (("feet", 9), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "r_form": (("feet", 2), loop(4, 120), [SOLES]),
    "r_tower": (("feet", 2), loop(4, 100), [SOLES]),
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
    # Codex's manifest (2026-10-18): "assets", each with name, file, pixel_1x, frames and cell_1x ("effects" in older ones)
    meta = {e["name"]: dict(e, pixel_1x=e.get("pixel_1x") or os.path.join("pixel_1x", e["file"])) for e in man.get("effects") or man["assets"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_volibear_fx": {}, "league_volibear_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_volibear_big" if name in BIG else "league_volibear_fx"][name] = out
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
