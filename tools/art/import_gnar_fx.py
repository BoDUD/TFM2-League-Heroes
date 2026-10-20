#!/usr/bin/env python3
"""Import Gnar's effects (assets/source/gnar/PROMPTS_FX.md, 24 pictures) as the game sheets league_gnar_fx and
league_gnar_big.

    python tools/art/import_gnar_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/gnar/codex_fx/gnar_fx: pixel_1x/gnar_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the three projectiles drawn flying
right and symmetric top to bottom, every other one symmetric left to right - checked again here). The user had Gemini
draw them (24 JPGs, 2026-10-20), brought to that delivery by tools/art/process_gnar_fx.py. Each frame is placed as the
kit plays it (import_chogath_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11
under it (league.dll hd.rs FEET 11.5). Times follow tools/kit/build_gnar.py: the boulder lies for pick_t ticks, Wallop's
stars spin through the stun (w2_stun); the buffs and the projectiles loop; the rest play once. The boomerang's way back
(q_back) shows Boomerang Throw's frames.
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
from build_gnar import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gnar", "codex_fx", "gnar_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"c_slam", "w_quake", "r_wave", "tf_mega", "tf_mini"}
FLYING = {"a_boom", "q_boom", "q_rock"}   # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head
LINE = (0, 0)                   # a projectile's point
MINI = (0, -4)                  # Mini Gnar's middle (32 px on soles 11.5 under the pivot)
STUNNED = (0, -10)              # Wallop's blow at the body's middle, the stars over the head (a 30-px cell)
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def ticks_ms(t):
    return t * 1000 / 60


# tag -> (picture, anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the attack: Mini's boomerang (a projectile), its hit, Hyper's third hit and speed; Mega's punch
    "a_boom": ("a_boom", "core", loop(4, 50), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "a_hyper": ("a_hyper", "core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "hyper": ("hyper", ("feet", 0), loop(4, 90), [SOLES]),
    "m_hit": ("m_hit", "core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Rage Gene: full (a buff), the transform and the turn back
    "full": ("full", ("feet", 0), loop(4, 100), [SOLES]),
    "tf_mega": ("tf_mega", ("feet", 0), seq(range(7), [50, 60, 70, 80, 80, 90, 100]), [SOLES]),
    "tf_mini": ("tf_mini", ("feet", 0), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    # Boomerang Throw: out and back, the hit, the catch, the slow (a buff)
    "q_boom": ("q_boom", "core", loop(4, 50), [LINE]),
    "q_back": ("q_boom", "core", loop(4, 50), [LINE]),
    "q_hit": ("q_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "q_catch": ("q_catch", "core", seq(range(2), [60, 90]), [MINI]),
    "q_slow": ("q_slow", "core", loop(4, 100), [OVERHEAD]),
    # Boulder Toss: the boulder, the smash on the point, the boulder lying there (pick_t), the pick-up, the slow
    "q_rock": ("q_rock", "core", loop(4, 60), [LINE]),
    "q2_hit": ("q2_hit", ("feet", 8), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "q_rest": ("q_rest", ("feet", 0), seq([k % 4 for k in range(12)], [250] * 12), [SOLES]),
    "q_pick": ("q_pick", ("feet", 0), seq(range(3), [60, 70, 80]), [SOLES]),
    "q2_slow": ("q2_slow", ("feet", 0), loop(4, 100), [SOLES]),
    # Hop's bounce; Crunch's landing round the point and its hit; Wallop's smash round him and its stun
    "e_hit": ("e_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "c_slam": ("c_slam", ("feet", 9), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "c_hit": ("c_hit", "core", seq(range(3), [40, 50, 60]), [HIT]),
    "w_quake": ("w_quake", ("feet", 8), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "w_hit": ("w_hit", "core", seq([0, 1] + [2, 3, 4] * 3, [50, 60] + [round((ticks_ms(P["w2_stun"]) - 110) / 9)] * 9),
              [STUNNED]),
    # GNAR!: the shockwave round him, the thrown
    "r_wave": ("r_wave", ("feet", 12), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 50, 70, 90]), [HIT]),
}
# the pictures that must last as long as something in the kit: tag -> ticks
LASTS = {"q_rest": P["pick_t"], "w_hit": P["w2_stun"]}


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
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def manifest(src):
    man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man.get("effects", []):
        name = e["name"].replace("gnar_fx_", "")
        meta[name] = dict(e, pixel_1x=os.path.join("pixel_1x", e["file"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="the delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    for tag, t in LASTS.items():
        ms = sum(m for _, m in FX[tag][2])
        if abs(ms - ticks_ms(t)) > 12:
            sys.exit(f"{tag} plays {ms} ms, the kit holds it {t} ticks ({ticks_ms(t):.0f} ms)")
    meta = manifest(a.src)
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n], a.src) for n in pics}
    tables = {"league_gnar_fx": {}, "league_gnar_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_gnar_big" if tag in BIG else "league_gnar_fx"][tag] = out
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
