#!/usr/bin/env python3
"""Import Locke's effects (assets/source/locke/PROMPTS_FX.md, 20 pictures) as the game sheets league_locke_fx and
league_locke_big.

    python tools/art/import_locke_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/locke/codex_fx/locke_fx, Codex 2026-10-26/new-chat:
pixel_1x/locke_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json (a list: cell_1x,
frames, symmetry); alpha 0 / 255; the nail and the case flying right and symmetric top to bottom, every other one
symmetric left to right - checked again here, then made an odd number of squares across the symmetric way).
import_trundle_fx.py's way. Each frame is placed as the kit plays it (tools/kit/build_locke.py's views): spots are game px
from the pivot (x forward, y down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too.
Anchors: "core" (the cell's middle), "bottom" (the lowest drawn row of all its frames), (0, k) (the row k over the
cell's last). The projectiles loop while they fly; the marks over heads, the slows, the soul fire round him loop while
their buffs last; the rest play once. r_land came 80 squares wide (asked 60: the seal circle drawn bigger) and is read
as delivered.
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
from import_hwei_fx import anchor, lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "locke", "codex_fx", "locke_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"r_land"}
FLYING = {"q_nail", "r_case"}   # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
MIDDLE = (0, -7)                # the middle of a 36 px unit (the mark round it, the nails driven in)
OVER = (0, -27)                 # over a unit's head
OVER_HIM = (0, -34)             # over Locke's hair (44 game px)
GROUND = (0, 12)                # a picture's lowest row on the ground line
FEETRING = (0, 11)              # the middle of a ring drawn round a unit's feet
DASH = (0, -11)                 # the slash at his waist where the pursuit starts
LINE = (0, 0)                   # a projectile's point

seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the projectiles: the soul nail (homing, ~8 ticks a throw), the case lobbed (r_travel 18 ticks)
    "q_nail": ("q_nail", "core", loop(4, 60), [LINE]),
    "r_case": ("r_case", "core", loop(4, 75), [LINE]),
    # the attack's Silver Stake
    "a_hit": ("a_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    # Ritual Nails: a nail striking, the mark over the head while it lasts, the nails driven in by his attack, the slow
    "q_hit": ("q_hit", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "q_mark": ("q_mark", "bottom", loop(4, 150), [OVER]),
    "q_pop": ("q_pop", "core", seq(range(4), [50, 60, 80, 100]), [MIDDLE]),
    "slow": ("slow", "core", loop(4, 110), [FEETRING]),
    # Ashen Pursuit: the ash where he left, the ash he comes back out of, the shockwave round him, the pursuit's slash,
    # the reset sigil over his head after a takedown
    "e_out": ("e_out", "bottom", seq(range(5), [60, 70, 80, 90, 110]), [GROUND]),
    "e_in": ("e_in", "bottom", seq(range(5), [50, 60, 70, 80, 100]), [GROUND]),
    "e_hit": ("e_hit", "core", seq(range(4), [50, 60, 80, 100]), [FEETRING]),
    "e_dash": ("e_dash", "core", seq(range(4), [40, 60, 80, 100]), [DASH]),
    "p_reset": ("p_reset", "bottom", seq(range(4), [60, 70, 80, 110]), [OVER_HIM]),
    # Soul Ignition: the flames rising round him, the soul fire while it burns, drawn back in at the end
    "w_ign": ("w_ign", "bottom", seq(range(6), [50, 60, 70, 80, 90, 110]), [GROUND]),
    "w_aura": ("w_aura", "bottom", loop(6, 120), [GROUND]),
    "w_end": ("w_end", "bottom", seq(range(5), [60, 70, 80, 90, 110]), [GROUND]),
    # Purgatory: the case slamming down in its seal circle (the circle's middle on the landing point), the blast's hit,
    # the mark round a champion while it lasts, each check of it, a soul sealed back to him
    "r_land": ("r_land", (0, 7), seq(range(8), [60, 70, 80, 100, 120, 140, 160, 200]), [FEETRING]),
    "r_hit": ("r_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT]),
    "r_mark": ("r_mark", "core", loop(6, 130), [MIDDLE]),
    "r_tick": ("r_tick", "core", seq(range(3), [40, 60, 80]), [HIT]),
    "r_seal": ("r_seal", "bottom", seq(range(6), [60, 70, 80, 90, 100, 120]), [GROUND]),
}


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    ax = 0 if name in FLYING else 1
    n = c.shape[ax]
    if n % 2:
        return c
    return np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        m = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == m).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd(c, name) for c in out]


def manifest(src):
    """{name: its manifest entry, pixel_1x = its picture}."""
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    if isinstance(man, dict):                 # a delivery shaped {"schema_version", ..., "effects": [...]}
        man = man.get("effects") or man.get("items")
    meta = {}
    for e in man:
        f = os.path.basename(e["file"])
        meta[f[:-4].replace("locke_fx_", "")] = dict(e, pixel_1x=os.path.join(src, "pixel_1x", f))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="the delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest(a.src)
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n], a.src) for n in pics}
    tables = {"league_locke_fx": {}, "league_locke_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_locke_big" if tag in BIG else "league_locke_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name in sorted(allc):
            cs = allc[name]
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
        sheet = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
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
