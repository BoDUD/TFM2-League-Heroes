#!/usr/bin/env python3
"""Import Azir's effects (assets/source/azir/PROMPTS_FX.md, 17 pictures) as the game sheets league_azir_fx and
league_azir_big.

    python tools/art/import_azir_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/azir/codex_fx/azir_fx, Codex 2026-10-23/new-chat-4:
pixel_1x/azir_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json ("assets": a list
of name, cell_1x, frames, symmetry); alpha 0 / 255; the two projectiles drawn flying right and symmetric top to bottom,
every other one symmetric left to right - checked again here, then made an odd number of squares across the symmetric
way). Each frame is placed as the kit plays it (import_aurora_fx.py's way): spots are game px from the pivot (x
forward, y down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core"
(the cell's middle), "bottom" (the lowest drawn row of all its frames), "mid" (the middle of all its frames' drawn rows).
The slow and the projectiles loop; E's shield loops over the shield's e_t (1.5 s: the CasterViewEffect plays its tag once);
the Sun Disc's ring loops one stamp (the add-on stamps it again every s_step); the rest play once, timed to the kit
(tools/kit/build_azir.py) and the add-on (the disc's rise as long as its disc_rise sheet tag, 560 ms).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from import_hwei_fx import anchor, lp, odd  # noqa: E402
from build_azir import P as KIT  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "azir", "codex_fx", "azir_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"r_rise", "d_rise", "d_beam"}
FLYING = {"a_bolt", "q_wave"}   # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SPEAR = (0, -6)                 # the sand spear's tip on a unit's chest (17 px over its soles)
BODY = (0, -8)                  # his body's middle (19 px over his soles): the shield shell round him
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
E_T_MS = KIT["e_t"] * 1000 // 60
STAMP_MS = KIT["s_step"] * 1000 // 60
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def shield():
    """E's shell: its four frames round and round for the shield's e_t."""
    out, k = [], 0
    while sum(ms for _, ms in out) + 75 <= E_T_MS:
        out.append((k % 4, 75))
        k += 1
    return out


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # his own sand bolt and its hit
    "a_bolt": ("a_bolt", "core", loop(4, 50), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    # Arise!: the mound a soldier rises from, the sand spear his stab drives into its target
    "s_spawn": ("s_spawn", "bottom", seq(range(5), [60, 70, 80, 90, 100]), [GROUND]),
    "s_stab": ("s_stab", "bottom", seq(range(4), [40, 50, 60, 80]), [SPEAR]),
    # Conquering Sands: the sand rush, the soldiers' landing, a hit, the quicksand slow
    "q_wave": ("q_wave", "core", loop(4, 50), [LINE]),
    "q_land": ("q_land", "bottom", seq(range(5), [50, 60, 80, 90, 110]), [GROUND]),
    "q_hit": ("q_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Shifting Sands: the shell round him, the geyser where he lands, a hit
    "e_shield": ("e_shield", "core", shield(), [BODY]),
    "e_land": ("e_land", "bottom", seq(range(5), [50, 60, 80, 90, 110]), [GROUND]),
    "e_hit": ("e_hit", "core", seq(range(4), [40, 60, 80, 100]), [HIT]),
    # Emperor's Divide: the sand bursting up round him as the guards come out, the dust at their feet hop by hop, a slam
    "r_rise": ("r_rise", "bottom", seq(range(6), [60, 70, 80, 90, 110, 130]), [GROUND]),
    "r_dust": ("r_dust", "bottom", seq(range(4), [40, 50, 60, 70]), [GROUND]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    # the Sun Disc (the add-on): its rise from the ruin (as long as the disc's own rise), the solar ray on its target
    # (its ring of light at the target's feet), the ring at its foot (one stamp, stamped again every s_step)
    "d_rise": ("d_rise", "bottom", seq(range(6), [70, 80, 90, 100, 110, 110]), [GROUND]),
    "d_beam": ("d_beam", "bottom", seq(range(5), [40, 50, 70, 80, 100]), [GROUND]),
    "d_glow": ("d_glow", "bottom", seq(range(6), [110] * 5 + [STAMP_MS - 550]), [GROUND]),
}


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(os.path.join(src, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
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
    return {e["name"]: e for e in man["assets"]}


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
    tables = {"league_azir_fx": {}, "league_azir_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_azir_big" if tag in BIG else "league_azir_fx"][tag] = out
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
