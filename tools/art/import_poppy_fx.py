#!/usr/bin/env python3
"""Import Poppy's effects (assets/source/poppy/PROMPTS_FX.md, 19 pictures) as the game sheets league_poppy_fx and
league_poppy_big.

    python tools/art/import_poppy_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/poppy/codex_fx: pixel_1x/poppy_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; the two flying pictures (p_buckler,
r_wave) drawn pointing right and symmetric top to bottom, every other one symmetric left to right - checked again here).
Each frame is cut by the manifest's frame size and placed as the kit plays it (import_cassiopeia_fx.py's way): spots are
game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit
(build_poppy.P, 60 ticks a second): the lying buckler and the cracked ground stamp one picture every 15 ticks, so their
frames fill 15 ticks; the charge glow loops through r_ch; w_block and e_wall are 20-tick buffs.
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
from build_poppy import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "poppy", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_slam", "q_crack", "q_burst", "w_cast", "w_on", "r_charge", "r_wave", "r_tap"}
FLYING = {"p_buckler", "r_wave"}     # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -28)             # over a 36-px unit's head
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    # Iron Ambassador: the buckler in flight, lying (a stamp every 15 ticks), picked up, her shield (a buff)
    "p_buckler": ("core", loop(4, 50), [(0, 0)]),
    "p_lie": (("feet", 3), loop(2, 15 * MS / 2), [SOLES]),
    "p_pick": (("feet", 2), seq(range(4), [60, 70, 80, 90]), [SOLES]),
    "p_shown": (("feet", 2), loop(4, 120), [SOLES]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Hammer Shock: the slam, the cracked ground (a stamp every 15 ticks), the rupture, the hit
    "q_slam": (("feet", 6), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "q_crack": (("feet", 7), loop(4, 15 * MS / 4), [SOLES]),
    "q_burst": (("feet", 6), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "q_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    # Steadfast Presence: the dome rising, the aura (a buff), a dash blocked (the add-on's 20-tick buff)
    "w_cast": (("feet", 3), seq(range(4), [60, 80, 100, 120]), [SOLES]),
    "w_on": (("feet", 12), loop(4, 120), [SOLES]),
    "w_block": (("feet", 2), seq(range(4), [60, 80, 90, 100]), [SOLES]),
    # Heroic Charge: the impact, the wall slam (the add-on's 20-tick buff), the stun stars (a buff)
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_wall": (("feet", 2), seq(range(5), [50, 60, 70, 70, 80]), [SOLES]),
    "e_stun": ("core", loop(4, 100), [OVERHEAD]),
    # Keeper's Verdict: the charge (through r_ch), the shockwave in flight, the tap's quake, the hit
    "r_charge": (("feet", 3), loop(4, P["r_ch"] * MS / 4), [SOLES]),
    "r_wave": ("core", loop(4, 50), [(0, 0)]),
    "r_tap": (("feet", 8), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
}


# a stray 4-square bar Codex left floating 20 rows above the quake's dust in r_tap's last frame (rows 0-3 are otherwise
# empty there): (effect, frame index) -> rows cleared
STRAY = {("r_tap", 4): (0, 4)}


def cells(name, meta):
    a = np.asarray(Image.open(lp(os.path.join(SRC, meta["pixel_1x"]))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for (nm, k), (r0, r1) in STRAY.items():
        if nm == name:
            out[k][r0:r1] = 0
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    # Codex's manifest (2026-10-18): "assets", each with name, file, pixel_1x, frames and cell_1x ("effects" in older ones)
    meta = {e["name"]: dict(e, pixel_1x=e.get("pixel_1x") or os.path.join("pixel_1x", e["file"])) for e in man.get("effects") or man["assets"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_poppy_fx": {}, "league_poppy_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_poppy_big" if name in BIG else "league_poppy_fx"][name] = out
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
