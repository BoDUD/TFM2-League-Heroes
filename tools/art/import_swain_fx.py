#!/usr/bin/env python3
"""Import Swain's effects (assets/source/swain/PROMPTS_FX.md, 15 pictures) as the game sheets league_swain_fx and
league_swain_big.

    python tools/art/import_swain_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/swain/codex_fx: pixel_1x/swain_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255, the red side's symmetry
already exact - checked again here against the entry's `symmetry` - and no dark outline round the light). Each frame is
cut by the manifest's frame size and placed as the kit plays it (import_urgot_fx.py's way): spots are game px from the
pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit (build_swain.P, 60
ticks a second). The wings' aura is not here: it is a tag of his own sheet (rig_swain.py r_wings).
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
from build_swain import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "swain", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SYM = {"top_bottom": "tb", "left_right": "lr"}
BIG = {"w_eye", "r_cast", "r_flare"}
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
# the raven bolt chases (twice its straight flight); it shows once past the demon hand (2 ticks at 5 px a tick)
BOLT_MS = max(P["atk_range"], 60000) / P["bolt_speed"] * MS * 2
Q_MS = P["q_len"] / P["q_speed"] * MS                       # Death's Hand's bolts: 62 px at 9 a tick, ~115 ms
E_OUT_MS = P["e_len"] / P["e_out"] * MS                     # the hand out: 70 px at 4 a tick
E_BACK_MS = (P["e_len"] + 20000) / P["e_back"] * MS         # and back: at most 90 px at 5 a tick
ROOT_MS = P["e_root"] * MS                                   # the root (1.5 s): the claws rise, then hold
EYE_MS = P["w_delay"] * MS                                   # the eye's fuse (1.5 s) to the burst
q_k = (Q_MS - MS) / 4
root_k = (ROOT_MS - 50 - 60 - 80) / 9
stare = (EYE_MS - 80 - 100 - 120) / 8
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # the flying pictures turn with their flight (drawn going right, symmetric top to bottom)
    "a_bolt": ("core", flight(4, 60, BOLT_MS, lead=2), [(0, 0)]),
    # Death's Hand's fan opens over its flight (played once, the widest frame held)
    "q_bolts": ("core", [(EMPTY, MS)] + seq(range(5), [q_k] * 4 + [1000]), [(0, 0)]),
    "e_out": ("core", flight(4, 60, E_OUT_MS, lead=1), [(0, 0)]),
    "e_back": ("core", flight(4, 60, E_BACK_MS * 1.5, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "w_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_pull": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    "r_fl_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    # the claws rise round the rooted unit's legs and hold for the root
    "e_hit": (("feet", 3), seq([0, 1, 2] + [3, 4, 5] * 3, [50, 60, 80] + [root_k] * 9), [SOLES]),
    # the eye on the ground where the target stood: opens, stares, narrows, bursts as the zone hits (w_delay)
    "w_eye": (("feet", 10), seq([0, 1] + [2, 3, 4, 5] * 2 + [6, 7], [80, 100] + [stare] * 8 + [120, 200]), [SOLES]),
    # the ravens bring a fragment to him
    "p_frag": (("feet", 0), seq(range(6), [60, 70, 80, 90, 100, 120]), [SOLES]),
    # the demon bursts out round him (its widest frame as the wings come, r_wings_at = 11 ticks in)
    "r_cast": (("feet", 4), seq(range(6), [60, 60, 90, 100, 110, 120]), [SOLES]),
    # soul wisps drawn out of a drained unit, from its chest up
    "r_drain": (("feet", 8), seq(range(4), [80, 90, 100, 110]), [HIT]),
    # Demonflare's nova spreading on the ground round him
    "r_flare": (("feet", 18), seq(range(6), [40, 60, 70, 80, 90, 120]), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", meta["file"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    sym = SYM[meta["symmetry"]]
    for k, c in enumerate(out):
        ok = (c == c[:, ::-1]).all() if sym == "lr" else (c == c[::-1]).all()
        if not ok:
            sys.exit(f"{name} frame {k + 1} is not symmetric {sym}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
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
    meta = {e["name"]: e for e in json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))["effects"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_swain_fx": {}, "league_swain_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_swain_big" if name in BIG else "league_swain_fx"][name] = out
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
