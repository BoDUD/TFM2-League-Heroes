#!/usr/bin/env python3
"""Import Sylas's effects (assets/source/sylas/PROMPTS_FX.md, 23 pictures) as the game sheets league_sylas_fx and
league_sylas_big.

    python tools/art/import_sylas_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/sylas/codex_fx/sylas_fx: pixel_1x/sylas_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's effects (cell_1x); alpha 0 / 255; the four projectiles
symmetric top to bottom and drawn going right, everything else left to right - checked again here). Each frame is cut
by the manifest's frame size and placed as the kit plays it (import_zoe_fx.py's way): spots are game px from the pivot
(x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit (build_sylas.P, 60 ticks a
second): Chain Lash's crossing glows q_wait ticks before it bursts, as the kit's delayed zone does. r2_arrow, r2_slam,
r2_song and r2_blink are the add-on's stolen ults (addons/league_sylas).
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
from build_sylas import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sylas", "codex_fx", "sylas_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"q_chain", "e_chain", "r_hook", "r2_arrow"}   # turned with their flight: drawn going right
BIG = {"p_spin", "q_cross", "r2_boom", "r2_slam", "r2_song"}
HIT = (0, -14)                  # a hit on the upper body of a 36-38 px unit
CHEST = (0, -16)                # his chest (the stolen power coming home)
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -31)             # over his head (38 px)
seq = J.seq
flight = J.flight
MS = 1000 / 60
Q_MS = P["q_len"] / P["q_speed"] * MS                    # the lash's line
E_MS = P["e_len"] / P["e_speed"] * MS                    # Abduct's chain
R_MS = P["r_range"] / P["r_speed"] * MS * 2              # the steal's homing chain (twice its straight flight)
A_MS = P["r2_alen"] / P["r2_aspeed"] * MS                # the add-on's stolen arrow
WAIT_MS = P["q_wait"] * MS                               # the crossing's glow before the burst


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "q_chain": ("core", flight(3, 60, Q_MS, lead=1), [(0, 0)]),
    "e_chain": ("core", flight(3, 60, E_MS, lead=1), [(0, 0)]),
    "r_hook": ("core", flight(3, 60, R_MS, lead=1), [(0, 0)]),
    "r2_arrow": ("core", flight(3, 50, A_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "p_spin": (("feet", 0), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "p_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    "w_hit": ("core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    "w_heal": (("feet", 3), seq(range(5), [60, 80, 90, 100, 90]), [SOLES]),
    "q_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    # the crossing lies on the ground and glows (frames 1-6 over the wait), then bursts (7-10)
    "q_cross": (("feet", 10), seq(range(10), [WAIT_MS / 6] * 6 + [60, 80, 90, 100]), [SOLES]),
    "q_hit2": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "e_hit": (("feet", 0), seq(range(4), [60, 80, 100, 120]), [SOLES]),
    "r_steal": (("feet", 0), seq(range(6), [60, 80, 90, 100, 90, 80]), [SOLES]),
    "r_got": ("core", seq(range(5), [60, 80, 90, 100, 90]), [CHEST]),
    "r2_boom": (("feet", 8), seq(range(7), [60, 60, 80, 90, 100, 100, 110]), [SOLES]),
    "r2_hit": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "p_1": (("feet", 0), loop(4, 110), [SOLES]),
    "q_slow": ("core", loop(4, 120), [SOLES]),
    "r_have": ("core", loop(4, 120), [OVERHEAD]),
    "r2_slam": (("feet", 8), seq(range(6), [50, 70, 80, 90, 90, 100]), [SOLES]),
    "r2_song": (("feet", 4), seq(range(6), [80, 100, 120, 140, 140, 120]), [SOLES]),
    "r2_blink": (("feet", 0), seq(range(4), [60, 80, 90, 100]), [SOLES]),
}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in TB else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in TB else 'left to right'}")
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
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man["effects"]:
        name = e.get("name") or e["file"][len("sylas_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", e["file"]))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_sylas_fx": {}, "league_sylas_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_sylas_big" if name in BIG else "league_sylas_fx"][name] = out
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
