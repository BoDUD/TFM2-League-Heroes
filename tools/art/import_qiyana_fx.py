#!/usr/bin/env python3
"""Import Qiyana's effects (assets/source/qiyana/PROMPTS_FX.md, 22 pictures) as the game sheets league_qiyana_fx and
league_qiyana_big.

    python tools/art/import_qiyana_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/qiyana/codex_fx/qiyana_fx: pixel_1x/qiyana_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the shockwave drawn flying right
and symmetric top to bottom, the six forward pictures pointing right, every other one symmetric left to right - checked
again here, then made an odd number of squares across the symmetric way). The user had Gemini draw them (JPGs,
2026-10-22; the last two, q_slow and q_haste, later the same day), brought to that delivery by
tools/art/process_qiyana_fx.py.
Each frame is placed as the kit plays it (import_ksante_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it (league.dll hd.rs FEET 11.5), hers too. A ground ring's anchor is the middle of
its ellipse as drawn (rows above the cell's bottom). The buffs (the three elements round her waist, the slow, the
haste) and the shockwave loop; the rest play once. The forward pictures (Q's four sweeps, R's swing and burst) are drawn
into her frames by tools/fix/bake_caster_fx.py once the frames are in; they sit in the sheets for it, anchored at their
own middle.
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

SRC = os.path.join(ROOT, "assets", "source", "qiyana", "codex_fx", "qiyana_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_swing", "q_w", "q_r", "q_g", "r_swing", "r_burst", "r_wave"}   # build_qiyana.py's views on the big sheet
FLYING = {"r_wave"}                                  # turned with its flight: drawn going right, symmetric top to bottom
FORWARD = {"q_swing", "q_w", "q_r", "q_g", "r_swing", "r_burst"}   # pointing forward, baked into her frames later
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
WAIST = (0, -1)                 # round her waist: 12 px over her soles (hd/idle rows 40-42 of 60, at PPU 1.5)
WAVE = (0, 0)                   # the shockwave's middle row 11 px over the ground line (it is 22 tall): it runs on the ground
CORE = (0, 0)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# tag -> (picture, anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the attack, the passive, Terrashape's enchant: the hits, the crown on a first hit, the swirl as she lands
    "a_hit": ("a_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "w_hit": ("w_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "p_hit": ("p_hit", "core", seq(range(4), [60, 70, 80, 80]), [HIT]),
    "w_on": ("w_on", ("feet", 1), seq(range(7), [60, 60, 60, 70, 70, 80, 90]), [SOLES]),
    # Q: the hits by element, the slow (a buff on the enemy) and the haste (a buff on her)
    "q_hit": ("q_hit", "core", seq(range(4), [40, 50, 60, 60]), [HIT]),
    "q_w_hit": ("q_w_hit", ("feet", 2), seq(range(4), [50, 120, 160, 120]), [SOLES]),
    "q_r_hit": ("q_r_hit", "core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "q_g_hit": ("q_g_hit", "core", seq(range(3), [40, 60, 70]), [HIT]),
    "q_slow": ("q_slow", ("feet", 1), loop(4, 130), [SOLES]),
    "q_haste": ("q_haste", ("feet", 3), loop(4, 90), [SOLES]),
    # E: the dash's hit
    "e_hit": ("e_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    # R: the shockwave (the projectile) and its burst on the ones it strikes
    "r_wave": ("r_wave", "core", loop(4, 60), [WAVE]),
    "r_hit": ("r_hit", "core", seq(range(4), [50, 60, 80, 100]), [HIT]),
    # the three elements round her waist while her ring holds one (buffs)
    "el_g": ("el_g", "core", loop(4, 110), [WAIST]),
    "el_w": ("el_w", "core", loop(4, 110), [WAIST]),
    "el_r": ("el_r", "core", loop(6, 100), [WAIST]),
    # the forward pictures, baked into her frames (bake_caster_fx.py) at their own middle
    "q_swing": ("q_swing", "core", seq(range(4), [40, 50, 60, 70]), [CORE]),
    "q_w": ("q_w", "core", seq(range(4), [40, 50, 60, 70]), [CORE]),
    "q_r": ("q_r", "core", seq(range(5), [40, 50, 60, 70, 80]), [CORE]),
    "q_g": ("q_g", "core", seq(range(4), [40, 50, 60, 70]), [CORE]),
    "r_swing": ("r_swing", "core", seq(range(3), [50, 60, 70]), [CORE]),
    "r_burst": ("r_burst", "core", seq(range(4), [40, 50, 60, 70]), [CORE]),
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
        if name not in FORWARD:
            mirror = c[::-1] if name in FLYING else c[:, ::-1]
            if not (c == mirror).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return [odd(c, name) for c in out]


def odd(c, name):
    """A symmetric picture an even number of squares across gets its middle column (top to bottom for a projectile: its
    middle row) twice: the game mirrors and turns about the pivot's square, so only an odd width lies even about it."""
    if name in FORWARD:
        return c
    ax = 0 if name in FLYING else 1
    n = c.shape[ax]
    if n % 2:
        return c
    return np.insert(c, n // 2, np.take(c, n // 2, axis=ax), axis=ax)


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    return {e["name"]: dict(e, pixel_1x=os.path.join("pixel_1x", e["file"])) for e in man.get("effects", [])}


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
    tables = {"league_qiyana_fx": {}, "league_qiyana_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_qiyana_big" if tag in BIG else "league_qiyana_fx"][tag] = out
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
