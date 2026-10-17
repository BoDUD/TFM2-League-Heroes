#!/usr/bin/env python3
"""Import Anivia's effects (assets/source/anivia/PROMPTS_FX.md, 15 pictures) as the game sheets league_anivia_fx and
league_anivia_big.

    python tools/art/import_anivia_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/anivia/codex_fx: pixel_1x/anivia_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255, the red side's symmetry exact
- checked again here: the three projectiles top to bottom, the rest left to right - and no dark outline round the
light). Each frame is cut by the manifest's frame size and placed as the kit plays it (import_swain_fx.py's way): spots
are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit
(build_anivia.P, 60 ticks a second).
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
from build_anivia import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "anivia", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bolt", "q_ball", "e_shard"}            # turned with their flight: drawn going right, symmetric top to bottom
BIG = {"q_blast", "w_wall", "r_storm", "r_formed"}
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
BOLT_MS = P["atk_range"] / P["a_speed"] * MS * 2                    # the homing bolt (twice its straight flight)
Q_MS = (P["q_range"] + 20000) / P["q_speed"] * MS                   # the orb to its spot at most
E_MS = P["e_range"] / P["e_speed"] * MS * 1.5                       # the homing shard
STUN_MS = P["q_stun"] * MS                                          # the freeze holds the stun
stun_k = (STUN_MS - 80 - 100 - 100 - 120) / 4
WALL_MS = P["w_t"] * MS                                             # the wall stands w_t ticks
WALL_LOOPS = 8
wall_k = (WALL_MS - 100 - 120 - 150 - 200) / (4 * WALL_LOOPS)
GROW_MS = 3 * P["r_grow"] * MS                                       # the storm grows over three stages
FORMED_MS = (P["r_t"] - 3 * P["r_grow"]) * MS                        # then stands formed
FORMED_LOOPS = 6
formed_k = (FORMED_MS - 120 - 150 - 200 - 250) / (4 * FORMED_LOOPS)
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_bolt": ("core", flight(4, 60, BOLT_MS, lead=1), [(0, 0)]),
    "q_ball": ("core", flight(4, 80, Q_MS, lead=1), [(0, 0)]),
    "e_shard": ("core", flight(3, 60, E_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the blast where the orb stops (the ground ellipse's middle 10 rows above the cell's bottom)
    "q_blast": (("feet", 10), seq(range(6), [40, 60, 70, 90, 100, 120]), [SOLES]),
    # the ice crust round a stunned unit's legs, held for the stun, then shattering
    "q_stun": (("feet", 0), seq([0, 1, 2, 3, 2, 3, 4, 5], [80, 100] + [stun_k] * 4 + [100, 120]), [SOLES]),
    # the wall: its middle (the cell's row 38) on the cast point's ground; rises, stands w_t ticks (3-6 looped), breaks
    "w_wall": (("feet", None), seq([0, 1] + [2, 3, 4, 5] * WALL_LOOPS + [6, 7],
                                   [100, 120] + [wall_k] * (4 * WALL_LOOPS) + [150, 200]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "e_iced": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # the blizzard called round her as she raises her wings (the storm falls on tick 10)
    "r_cast": (("feet", 0), seq(range(6), [60, 70, 80, 90, 100, 120]), [SOLES]),
    # the storm growing on the ground (three stages, two frames each) ...
    "r_storm": (("feet", 14), seq(range(6), [GROW_MS / 6] * 6), [SOLES]),
    # ... then formed for the rest of its time (3-6 looped)
    "r_formed": (("feet", 14), seq([0, 1] + [2, 3, 4, 5] * FORMED_LOOPS + [6, 7],
                                   [120, 150] + [formed_k] * (4 * FORMED_LOOPS) + [200, 250]), [SOLES]),
    # the Iced mark over a champion (a buff's loop)
    "iced": (("feet", 0), seq(range(4), [130, 130, 130, 130]), [SOLES]),
    # Rebirth (the add-on's egg): the flash that covers her turning into the egg, the egg breaking open
    "p_egg_in": (("feet", 0), seq(range(4), [50, 60, 70, 90]), [SOLES]),
    "p_hatch": (("feet", 0), seq(range(4), [60, 70, 80, 100]), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", os.path.basename(meta.get("pixel_1x", meta["file"])))))
                   .convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        ok = (c == c[::-1]).all() if name in TB else (c == c[:, ::-1]).all()
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind[1] is None:                                 # the wall: its middle on the cell's middle row
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {e["name"]: e for e in man.get("effects", man.get("images", []))}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_anivia_fx": {}, "league_anivia_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_anivia_big" if name in BIG else "league_anivia_fx"][name] = out
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
