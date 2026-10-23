#!/usr/bin/env python3
"""Import Aurora's effects (assets/source/aurora/PROMPTS_FX.md, 20 pictures) as the game sheets league_aurora_fx and
league_aurora_big.

    python tools/art/import_aurora_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/aurora/codex_fx/aurora_fx, Codex 2026-10-23/new-chat-2:
pixel_1x/aurora_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json (a list: cell_1x,
frames, symmetry); alpha 0 / 255; the four projectiles drawn flying right and symmetric top to bottom, every other one
symmetric left to right - checked again here, then made an odd number of squares across the symmetric way).
Each frame is placed as the kit plays it (import_ivern_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's
middle), "bottom" (the lowest drawn row of all its frames), "mid" (the middle of all its frames' drawn rows). The buffs
(the curse, the spirit mark, the haste, the slow) and the projectiles loop; the rest play once, timed to the kit
(tools/kit/build_aurora.py): the realm opens on its first two frames and its last six loop over r_t (210 ticks = 3.5 s).
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

SRC = os.path.join(ROOT, "assets", "source", "aurora", "codex_fx", "aurora_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"r_shock", "r_zone"}
FLYING = {"a_bolt", "q_out", "q_back", "e_wave"}   # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
OVER = (0, -27)                 # over a 34 px unit's head
CHEST = (0, -7)                 # her chest: 18 px over her soles (the pivot 11 over them; her eyes 27 over them)
SOLES = (0, 11)                 # on the ground under a unit or a point
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
R_T_MS = 210 * 1000 // 60       # the realm's life (build_aurora.py r_t)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def realm():
    """The realm: frames 0-1 open it, 2-7 loop until r_t is over."""
    out = [(0, 90), (1, 90)]
    k = 2
    while sum(ms for _, ms in out) + 110 <= R_T_MS:
        out.append((k, 110))
        k = 2 + (k - 1) % 6
    out.append((k, R_T_MS - sum(ms for _, ms in out)))
    return out


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the attack's spirit bolt and its spark
    "a_bolt": ("a_bolt", "core", loop(4, 50), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    # Twofold Hex: the hex out (and the combo's homing hex), the curse back, the hits, the curse on the unit
    "q_out": ("q_out", "core", loop(4, 50), [LINE]),
    "q_back": ("q_back", "core", loop(4, 50), [LINE]),
    "q_hit": ("q_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "q_back_hit": ("q_back_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT]),
    "q_curse": ("q_curse", "core", loop(4, 100), [HIT]),
    # Spirit Abjuration: the count over the head, the spirit torn out, its heal round her; Across the Veil
    "p_mark": ("p_mark", "core", loop(4, 120), [OVER]),
    "p_spirit": ("p_spirit", "bottom", seq(range(6), [50, 70, 80, 90, 100, 120]), [(0, 0)]),
    "p_heal": ("p_heal", "bottom", seq(range(6), [60, 70, 80, 90, 100, 120]), [GROUND]),
    "w_veil": ("w_veil", "mid", seq(range(5), [40, 60, 80, 100, 120]), [CHEST]),
    "w_haste": ("w_haste", "bottom", loop(4, 90), [GROUND]),
    # The Weirding: the window at her chest, the wave, the hit, the slow
    "e_burst": ("e_burst", "core", seq(range(5), [40, 50, 60, 80, 100]), [CHEST]),
    "e_wave": ("e_wave", "core", loop(4, 50), [LINE]),
    "e_hit": ("e_hit", "core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Between Worlds: the landing shockwave, the realm, a hit, the step to its champion
    "r_shock": ("r_shock", "mid", seq(range(6), [50, 60, 70, 90, 110, 130]), [SOLES]),
    "r_zone": ("r_zone", "mid", realm(), [SOLES]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "r_blink": ("r_blink", "bottom", seq(range(5), [40, 60, 80, 70, 90]), [GROUND]),
}


def hexrgb(c):
    return [int(c[i:i + 2], 16) for i in (1, 3, 5)] + [255]


# a_hit's first frame came back a flat blob on the cell's bottom rows (pixel_1x): redrawn as the prompt's flash, a white
# core with an icy blue rim in the cell's middle (12 x 12, symmetric about columns 5 | 6)
A_HIT0 = {(3, 5): "#4A86F0", (4, 4): "#8CC8FF", (4, 5): "#D8F0FF", (5, 3): "#4A86F0", (5, 4): "#D8F0FF",
          (5, 5): "#FFFFFF", (6, 3): "#4A86F0", (6, 4): "#D8F0FF", (6, 5): "#FFFFFF", (7, 4): "#8CC8FF",
          (7, 5): "#D8F0FF", (8, 5): "#4A86F0"}


def fix(name, out):
    if name == "a_hit":
        c = np.zeros_like(out[0])
        for (y, x), col in A_HIT0.items():
            c[y, x] = c[y, 11 - x] = hexrgb(col)
        out[0] = c
    return out


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = fix(name, [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])])
    for k, c in enumerate(out):
        mirror = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd_(c, name) for c in out]


def odd_(c, name):
    """import_hwei_fx.odd with this hero's projectiles."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man:
        name = e["file"][:-4].replace("aurora_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join("pixel_1x", e["file"]))
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
    tables = {"league_aurora_fx": {}, "league_aurora_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_aurora_big" if tag in BIG else "league_aurora_fx"][tag] = out
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
