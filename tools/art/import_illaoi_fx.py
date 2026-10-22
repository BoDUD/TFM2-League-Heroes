#!/usr/bin/env python3
"""Import Illaoi's effects (assets/source/illaoi/PROMPTS_FX.md, 15 pictures) as the game sheets league_illaoi_fx and
league_illaoi_big.

    python tools/art/import_illaoi_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/illaoi/codex_fx/illaoi_fx: pixel_1x/illaoi_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the projectile drawn flying
right and symmetric top to bottom, every other one symmetric left to right - checked again here, then made an odd
number of squares across the symmetric way). The user had Gemini draw all 15 (JPGs, 2026-10-23), brought to that
delivery by tools/art/process_illaoi_fx.py. Each frame is placed as the kit plays it (import_hwei_fx.py's way): spots
are game px from the pivot (x forward, y down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), a ground
point's too. Anchors: "core" (the cell's middle), "bottom" (the lowest drawn row of all its frames), "mid" (the middle
of all its frames' drawn rows). The buffs (her heal, the Elder God's eye, the spirit, the Vessel's brand, the slow, R's
glyph ring) and the projectile loop; the rest play once, timed to the kit (tools/kit/build_illaoi.py).
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

SRC = os.path.join(ROOT, "assets", "source", "illaoi", "codex_fx", "illaoi_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"p_spawn", "p_slam", "w_slam", "r_slam", "r_aura"}
FLYING = {"e_grab"}             # turned with its flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
CHEST = (0, -12)                # the spirit shattering before the chest
SOLES = (0, 11)                 # on the ground under a unit or a point
GROUND = (0, 12)                # a picture's lowest row on the ground line
OVER = (0, -30)                 # the Elder God's eye: its lowest row just over a 40 px unit's head
LINE = (0, 0)                   # a projectile's point
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the idol strike
    "a_hit": ("a_hit", "core", seq(range(3), [50, 60, 80]), [HIT]),
    # the tentacles: the ground cracking where one grows, its slam on the ground and on a unit, her heal (a buff)
    "p_spawn": ("p_spawn", "mid", seq(range(5), [60, 80, 100, 140, 220]), [SOLES]),
    "p_slam": ("p_slam", "bottom", seq(range(6), [40, 60, 70, 90, 110, 130]), [GROUND]),
    "p_hit": ("p_hit", "core", seq(range(3), [40, 60, 90]), [HIT]),
    "p_heal": ("p_heal", "bottom", loop(6, 100), [GROUND]),
    # Harsh Lesson: the landing, the eye over the lesson's head (a buff)
    "w_slam": ("w_slam", "bottom", seq(range(7), [40, 50, 60, 80, 100, 120, 140]), [GROUND]),
    "w_mark": ("w_mark", "bottom", loop(4, 125), [OVER]),
    # Test of Spirit: the ghostly tentacle, the spirit, the Vessel's brand, the shattering, the mist (buffs but the two)
    "e_grab": ("e_grab", "core", loop(4, 50), [LINE]),
    "e_spirit": ("e_spirit", "bottom", loop(6, 100), [GROUND]),
    "e_vessel": ("e_vessel", "mid", loop(8, 100), [SOLES]),
    "e_break": ("e_break", "core", seq(range(6), [40, 50, 60, 80, 100, 120]), [CHEST]),
    "e_slow": ("e_slow", "bottom", loop(4, 100), [GROUND]),
    # Leap of Faith: the crater, the glyph ring under her (a buff), the hit
    "r_slam": ("r_slam", "bottom", seq(range(8), [40, 60, 70, 90, 110, 140, 180, 220]), [GROUND]),
    "r_aura": ("r_aura", "mid", loop(6, 110), [SOLES]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 50, 60, 80]), [HIT]),
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
    return [odd(c, name) for c in out]


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    ax = 0 if name in FLYING else 1
    n = c.shape[ax]
    if n % 2:
        return c
    return np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)


def rows_drawn(cs):
    ys = np.concatenate([np.nonzero(c[..., 3].any(1))[0] for c in cs])
    return ys.min(), ys.max()


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    x = (w - 1) / 2
    if kind == "core":
        return [x, (h - 1) / 2]
    if kind == "bottom":
        return [x, float(rows_drawn(cs)[1])]
    if kind == "mid":
        y0, y1 = rows_drawn(cs)
        return [x, (y0 + y1) / 2]
    if kind == "mid0":
        y0, y1 = rows_drawn(cs[:1])
        return [x, (y0 + y1) / 2]
    return [x, h - 1 - kind[1]]


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man.get("effects", []):
        name = e["name"].replace("illaoi_fx_", "")
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
    tables = {"league_illaoi_fx": {}, "league_illaoi_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_illaoi_big" if tag in BIG else "league_illaoi_fx"][tag] = out
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
