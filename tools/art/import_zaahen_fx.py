#!/usr/bin/env python3
"""Import Zaahen's effects (assets/source/zaahen/PROMPTS_FX.md, 16 pictures) as the game sheets league_zaahen_fx and
league_zaahen_big.

    python tools/art/clean_zaahen_fx.py       # the Gemini pictures -> assets/source/zaahen/gemini_fx/clean
    python tools/art/import_zaahen_fx.py [--src DIR] [--review out.png]

The source is the cleaned delivery (tools/art/clean_zaahen_fx.py: pixel_1x/zaahen_fx_<name>.png, one row of equal
frames each at game size, manifest.json a list of cell_1x / frames / symmetry; alpha 0 / 255; symmetric left to right,
the W projectile top to bottom - checked again here, then made an odd number of squares across the symmetric way).
import_skarner_fx.py's way. Each frame is placed as the kit plays it: spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames). The full-Determination aura and R's guard loop while their
buffs last; the projectile loops while it flies; the rest play once. rv_glow is not a view of the kit: rig_zaahen.py
lays his rising frames over it for the add-on's revive picture rv_rise (in league_zaahen_big from there). Frames come
from the manifest (the cleaner drops empty ones), the times from TIMES.
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
from import_hwei_fx import anchor, lp, odd  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zaahen", "gemini_fx", "clean")
MOD = os.path.join(ROOT, "league")

BIG = {"e_spin", "r_rise", "r_slam", "rv_glow"}
FLYING = {"w_glaive"}            # turned with its flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
FEETRING = (0, 11)              # the middle of a ring drawn round a unit's feet (or a ground point)
BODY = (0, -13)                 # the middle of Zaahen's body (48 game px tall, soles 11 under the pivot)
LINE = (0, 0)                   # a projectile's point

seq = J.seq

# tag -> (picture, anchor, frame times (ms; a single number = a loop at that step), spots)
FX = {
    "w_glaive": ("w_glaive", "core", 60, [LINE]),
    "a_hit": ("a_hit", "core", [40, 60, 80], [HIT]),
    "q_hit": ("q_hit", "core", [40, 60, 90], [HIT]),
    "q_hit2": ("q_hit2", "core", [40, 60, 90], [HIT]),
    "q_uphit": ("q_uphit", "bottom", [40, 60, 80, 100, 120], [GROUND]),
    "w_hit": ("w_hit", "core", [50, 60, 80, 100], [HIT]),
    "e_spin": ("e_spin", "bottom", [40, 50, 60, 70, 90, 110], [GROUND]),
    "e_hit": ("e_hit", "core", [40, 60, 80], [HIT]),
    "r_rise": ("r_rise", "bottom", [60, 80, 100, 120, 120, 140], [GROUND]),
    "r_slam": ("r_slam", "core", [40, 50, 60, 70, 90, 110, 130, 150], [FEETRING]),
    "r_hit": ("r_hit", "core", [40, 60, 80, 100], [HIT]),
    "p_full": ("p_full", "bottom", [50, 60, 70, 80, 100, 120], [GROUND]),
    "p_aura": ("p_aura", "bottom", 110, [GROUND]),
    "p_shield": ("p_shield", "core", [60, 80, 100, 120], [BODY]),
    "rv_glow": ("rv_glow", "bottom", [80, 80, 80, 120, 120, 120, 120, 120], [GROUND]),
}


def odd_(c, name):
    """import_hwei_fx.odd with this hero's projectiles."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, "pixel_1x", meta["file"])))).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        ok = (c == c[::-1]).all() if name in FLYING else (c == c[:, ::-1]).all()
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd_(c, name) for c in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(a.src, "manifest.json")), encoding="utf-8"))
    meta = {e["file"][:-4].replace("zaahen_fx_", ""): e for e in man}
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n], a.src) for n in pics}
    tables = {"league_zaahen_fx": {}, "league_zaahen_big": {}}
    for tag, (pic, kind, times, spots) in FX.items():
        cs = allc[pic]
        n = len(cs)
        ms = [times] * n if isinstance(times, int) else (times + [times[-1]] * n)[:n]
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), m) for k, m in enumerate(ms)]
        tables["league_zaahen_big" if tag in BIG else "league_zaahen_fx"][tag] = out
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
