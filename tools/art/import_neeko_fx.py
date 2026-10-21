#!/usr/bin/env python3
"""Import Neeko's effects (assets/source/neeko/PROMPTS_FX.md, 16 pictures) as the game sheets league_neeko_fx and
league_neeko_big.

    python tools/art/import_neeko_fx.py [--review out.png]

The source is the step-3 delivery (assets/source/neeko/codex_fx/neeko_fx: pixel_1x/neeko_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's effects (cell_1x); alpha 0 / 255; preview/ its 8x copies,
raw/ the generated pictures). The bolt, the seed and the barbs are projectiles (the game turns them to their flight:
flying left they turn upside down, so they must be symmetric top to bottom); every other picture is symmetric left to
right (the client never mirrors it on the red side) - both checked again here. Each frame is cut by the manifest's frame
size and placed as the kit plays it (import_naafiri_fx.py's way): spots are game px from the pivot (x forward, y down); a
unit's soles are 11 under it, a point's ground too. Her own pictures are centred on her standing point (the middle of her
body: symmetric for the red side). Which sheet an effect goes to is read from the kit's own views (build_neeko.build with
the add-on's p_poof), so the two never disagree. Times from the kit (build_neeko.P, 60 ticks a second).
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
import build_neeko as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "neeko", "codex_fx", "neeko_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)
P = K.P


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bolt", "q_seed", "e_barbs"}     # projectiles: turned to their flight by the game
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
FLIGHT = (0, 0)                 # a projectile's own point
HER = (0, 11)                   # her soles under her standing point (the middle of her body)
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    "a_bolt": ("core", loop(4, 60), [FLIGHT]),
    "q_seed": ("core", loop(4, 60), [FLIGHT]),
    "e_barbs": ("core", loop(4, 60), [FLIGHT]),
    "a_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "w_hit": ("core", seq(range(4), [50, 60, 70, 90]), [HIT]),
    # the seed's bursts on its spot: the ground ellipse's middle 9 (the bloom 8) squares over the cell's bottom row
    "q_burst": (("feet", 9), seq(range(5), [60, 80, 90, 100, 110]), [SOLES]),
    "q_bloom": (("feet", 8), seq(range(4), [60, 80, 90, 110]), [SOLES]),
    "q_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "e_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    # Pop Blossom: the bud round her over the whole charge (her soles 3 squares over the cell's bottom), the spring's ring
    # 4 squares over it, the landing's ellipse 15 squares over it - all on her soles
    "r_charge": (("feet", 3), seq(range(6), [120, 120, 120, 130, 130, round(P["r_charge"] * MS) - 620]), [HER]),
    "r_jump": (("feet", 4), seq(range(4), [60, 70, 80, 90]), [HER]),
    "r_land": (("feet", 15), seq(range(6), [60, 80, 100, 110, 110, 120]), [HER]),
    "r_hit": ("core", seq(range(4), [50, 60, 80, 90]), [HIT]),
    # the add-on's disguise on and off: the smoke over her, her soles 3 squares over the cell's bottom
    "p_poof": (("feet", 3), seq(range(5), [60, 70, 80, 80, 90]), [HER]),
    # buffs, looped while they hold: the vines' roots on the rooted unit's soles, the haste motes' ellipse round hers
    "e_bound": (("feet", 0), loop(4, 120), [SOLES]),
    "w_haste": (("feet", 4), loop(4, 100), [HER]),
}


def sheets_of_kit():
    """{effect: "league_neeko_fx" or "league_neeko_big"} as the kit's views name them (the add-on copy: p_poof too)."""
    kit = K.build(dict(P, native=1))
    out = {}
    for group in ("view_projectiles", "view_effects", "view_buffs"):
        for v in kit[group]:
            out[v["tag"]] = v["anim"].rsplit("/", 1)[1]
    return out


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in TB else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
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
    meta = {}
    for e in man["effects"]:
        name = os.path.basename(e["file"])[len("neeko_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", os.path.basename(e["file"])))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the importer's {sorted(FX)}")
    sheet_of = sheets_of_kit()
    if set(sheet_of) != set(FX):
        sys.exit(f"the kit's views {sorted(sheet_of)} against the importer's {sorted(FX)}")
    for name, (_, frames, _) in FX.items():
        if any(k >= meta[name]["frames"] for k, _ in frames if k != J.EMPTY):
            sys.exit(f"{name}: a frame past the delivered {meta[name]['frames']}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_neeko_fx": {}, "league_neeko_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables[sheet_of[name]][name] = out
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
