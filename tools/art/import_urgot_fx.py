#!/usr/bin/env python3
"""Import Urgot's effects (assets/source/urgot/PROMPTS_FX.md, 22 pictures) as the game sheets league_urgot_fx and
league_urgot_big.

    python tools/art/import_urgot_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/urgot/codex_fx: pixel_1x/urgot_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json; alpha 0 / 255, the red side's symmetry already exact - checked
again here - and no dark outline round the light). Each frame is cut by the manifest's frame size and placed as the
kit plays it (league_kalista / league_aphelios's way): spots are game px from the pivot (x forward, y down); a unit's
soles are 11 under it. Times from the kit (build_urgot.P, 60 ticks a second).
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
from build_urgot import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "urgot", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SYM = {"a_shot": "tb", "w_shot": "tb", "p_fan": "tb", "r_drill": "tb", "q_charge": "both"}   # every other one "lr"
BIG = {"p_fan", "q_blast", "r_ex", "r_fear"}
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
HEAD = (0, -36)                 # over a unit's head
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
SHOT_MS = max(P["atk_range"], 60000) / P["shot_speed"] * MS * 2     # a homing shot's flight, chasing: twice the straight
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the shots and the drill fly (their pictures turn with the flight)
    "a_shot": ("core", flight(3, 60, SHOT_MS), [(0, 0)]),
    "w_shot": ("core", flight(2, 50, SHOT_MS), [(0, 0)]),
    "r_drill": ("core", flight(4, 60, P["r_range"] / P["r_speed"] * MS), [(0, 0)]),
    # the leg's cone lives as long as its line (12 ticks): its centre is the line's middle
    "p_fan": ("core", seq(range(4), [40, 50, 50, 12 * MS - 140]), [(0, 0)]),
    # the canister on its lob (q_travel ticks)
    "q_charge": ("core", flight(4, 60, P["q_travel"] * MS, lead=0), [(0, 0)]),
    # the landing ring while it flies (q_travel ticks), on the ground of the landing point
    "q_mark": ("core", seq([k % 4 for k in range(4)], [P["q_travel"] * MS / 4] * 4), [SOLES]),
    # on the landing spot: the canister's fuse over q_apply ticks (frames 1-3), the acid blast as the zone hits
    "q_blast": (("feet", 6), seq(range(7), [P["q_apply"] * MS / 3] * 3 + [50, 90, 110, 130]), [SOLES]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "w_hit": ("core", seq(range(3), [30, 40, 50]), [HIT]),
    "p_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "e_hit": ("core", seq(range(4), [40, 50, 70, 90]), [HIT]),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_ex": ("core", seq(range(6), [40, 60, 80, 90, 100, 120]), [HIT]),
    # the shield closing round him as he charges
    "e_shield": (("feet", 0), seq(range(6), [60, 70, 80, 100, 120, 140]), [SOLES]),
    # the slam under the champion he hurls
    "e_fling": (("feet", 5), seq(range(5), [50, 70, 90, 100, 110]), [SOLES]),
    # the reel over r_reel ticks
    "r_reel": (("feet", 0), seq(range(4), [P["r_reel"] * MS / 4] * 4), [SOLES]),
    # the fear's shockwave round him
    "r_fear": (("feet", 8), seq(range(6), [60, 80, 90, 100, 110, 120]), [SOLES]),
    # buffs (looped while they last)
    "w_on": ("core", seq(range(4), [100] * 4), [SOLES]),
    "q_slow": ("core", seq(range(4), [100] * 4), [SOLES]),
    "r_leash": (("feet", 0), seq(range(4), [120] * 4), [SOLES]),
    "r_flee": ("core", seq(range(4), [120] * 4), [HEAD]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["frame_width"], meta["frame_height"]
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    sym = SYM.get(name, "lr")
    for k, c in enumerate(out):
        ok = {"lr": (c == c[:, ::-1]).all(), "tb": (c == c[::-1]).all(),
              "both": (c == c[:, ::-1]).all() and (c == c[::-1]).all()}[sym]
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {sym}")
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
    meta = {e["tag"]: e for e in json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))["effects"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_urgot_fx": {}, "league_urgot_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_urgot_big" if name in BIG else "league_urgot_fx"][name] = out
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
