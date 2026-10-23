#!/usr/bin/env python3
"""Import Singed's effects (assets/source/singed/PROMPTS_FX.md, 14 pictures) as the game sheets league_singed_fx and
league_singed_big.

    python tools/art/import_singed_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/singed/codex_fx/singed_fx, Codex 2026-10-23/new-chat-6:
pixel_1x/singed_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json "effects"
(cell_1x, frames, symmetry, playback); alpha 0 / 255; the vial drawn flying right and symmetric top to bottom, every other
one symmetric left to right - checked again here, then made an odd number of squares across the symmetric way).
Each frame is placed as the kit plays it (import_zac_fx.py's way): spots are game px from the pivot (x forward, y down);
a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground point's too. Anchors: "core" (the cell's middle),
"bottom" (the lowest drawn row of all its frames). The two pictures round his body (the potion's rush and its steam) left
his place clear with his soles 3 squares over the cell's bottom: their middle goes that far over his soles.
The lasting pictures are a few frames stretched to their zone's life (tools/kit/build_singed.py; the manifest's
playback): a poison cloud q_t 180 ticks (3 s: rising, its middle three frames looped, thinning), the glue w_t 180 ticks
(the splash, four lying frames looped, drying), the root e_root 60 ticks (its last frame held); the buffs (the glue's
slow, the grievous wounds, the potion's steam for its 25 s, the slipstream's wisps) and the vial loop; the rest play once.
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

SRC = os.path.join(ROOT, "assets", "source", "singed", "codex_fx", "singed_fx")
MOD = os.path.join(ROOT, "league")

BIG = {"q_cloud", "q_cloud_r", "w_glue"}
FLYING = {"w_vial"}             # turned with its flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
LINE = (0, 0)                   # a projectile's point
OVER = (0, -30)                 # over a 36 px unit's head (its top at -25)


def round_him(cell_h):
    """A picture round his body: his soles 3 squares over the cell's bottom, so the cell's middle is (cell_h / 2 - 3) over
    his soles - the spot of the "core" anchor."""
    return (0, 11 - (cell_h // 2 - 3))


seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def lasting(opening, looped, closing, total):
    """An opening (frames with ms), the looped frames at their ms repeated while the total lasts, a closing: a picture
    stretched to a zone's life (total ms)."""
    head = sum(ms for _, ms in opening) + sum(ms for _, ms in closing)
    per = sum(ms for _, ms in looped)
    n = max(1, round((total - head) / per))
    return opening + looped * n + closing


T = lambda ticks: ticks * 1000 / 60     # noqa: E731

# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the plate's blow
    "a_hit": ("a_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    # Poison Trail: a cloud rising, rolling (frames 1-3 looped), thinning - 3 s where he walked; Insanity Potion's thicker one
    "q_cloud": ("q_cloud", "bottom", lasting(seq([0], [150]), seq([1, 2, 3], [150, 150, 150]), seq([4, 5], [250, 250]),
                                             T(180)), [GROUND]),
    "q_cloud_r": ("q_cloud_r", "bottom", lasting(seq([0], [150]), seq([1, 2, 3], [150, 150, 150]),
                                                 seq([4, 5], [250, 250]), T(180)), [GROUND]),
    # Fling: the grab, the body landing (on the thrown one's feet), the root when it lands in the glue (held e_root)
    "e_hit": ("e_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    "e_land": ("e_land", "bottom", seq(range(4), [60, 80, 100, 120]), [GROUND]),
    "e_root": ("e_root", "bottom", seq(range(4), [60, 80, 100, T(60) - 240]), [GROUND]),
    # Mega Adhesive: the vial flying, the glue (the splash, four lying frames looped, drying - 3 s), the slow at the feet
    "w_vial": ("w_vial", "core", loop(4, 60), [LINE]),
    "w_glue": ("w_glue", "bottom", lasting(seq([0, 1], [100, 150]), seq([2, 3, 4, 5], [180, 180, 180, 180]),
                                           seq([6, 7], [300, 300]), T(180)), [GROUND]),
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Insanity Potion: the rush round him, the steam behind him while it lasts, the grievous wounds over a head
    "r_drink": ("r_drink", "core", seq(range(5), [70, 90, 110, 130, 150]), [round_him(50)]),
    "r_aura": ("r_aura", "core", loop(4, 150), [round_him(50)]),
    "gw": ("gw", "core", loop(4, 120), [OVER]),
    # Noxious Slipstream: the burst of speed at his feet, the wisps while it lasts
    "p_fast": ("p_fast", "bottom", seq(range(3), [60, 80, 100]), [GROUND]),
    "haste": ("haste", "bottom", loop(4, 90), [GROUND]),
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
    """import_hwei_fx.odd with this hero's projectile."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    if isinstance(man, dict):                     # this delivery: {"schema_version", ..., "effects": [...]}
        man = man.get("effects") or man.get("items")
    meta = {}
    for e in man:
        f = os.path.basename(e["file"])
        name = f[:-4].replace("singed_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join("pixel_1x", f))
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
    tables = {"league_singed_fx": {}, "league_singed_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_singed_big" if tag in BIG else "league_singed_fx"][tag] = out
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
