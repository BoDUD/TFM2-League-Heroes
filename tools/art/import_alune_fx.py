#!/usr/bin/env python3
"""Import Alune's effects (assets/source/alune/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft pack's sheets
tft_alune_fx and tft_alune_big and its icons.

    python tools/art/import_alune_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/alune/codex_fx/alune_fx: pixel_1x/alune_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; everything but the flying ring
symmetric left to right - checked again here; alune_icon_<slot>.png 64 x 64). Each frame is cut by the manifest's frame
size and placed as the kit plays it (import_powder_fx.py's way): spots are game px from the pivot (x forward, y down);
a unit's soles are 11 under it, a point's ground too. Times from the kit (build_alune.P, 60 ticks a second).
The ground rows were measured on the cells (2026-10-26): the shard's tip in its last falling frame (q_drop row 53), the
splash's ground ring (q_hit 17), the shadow's ellipse middle (r_warn 11.5), the full moon's shockwave middle (r_moon 67:
the moon sinks below it as it crashes), the blessing's ground ring (e_glow 37). The moon is cut in two (the kit's views):
r_fall = its four descending frames, played over the champion's spot from the launch and spread over the moon's
r_open flight; r_moon = the crash, the shockwave and the fading, played where it lands (the damage's tick). The phases
p_moon1-3 are p_moon's three cells, each its own still picture over her head.
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
from build_alune import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "alune", "codex_fx", "alune_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FLYING = {"a_ring"}                       # turned with its flight: symmetric top to bottom instead
BIG = {"q_drop", "r_warn", "r_fall", "r_moon"}
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
BODY = (0, -8)                  # the middle of a unit
OVER_HEAD = (0, -34)            # just over a 32-46 px unit's head
HER_MOON = (0, -41)             # over her own head (45 game px tall riding her crescent)
seq = J.seq
flight = J.flight
MS = 1000 / 60
RING_MS = P["atk_range"] / P["a_speed"] * MS * 2           # the homing ring (twice its straight flight)
FALL_MS = P["q_fall"] * MS                                 # a moonshard's fall
MOON_MS = P["r_open"] * MS                                 # the moon's flight


def loop(n, ms):
    return seq(range(n), [ms] * n)


def spread(frames, total):
    """frames over `total` ms, evenly (the last takes the rounding)."""
    n = len(frames)
    each = [round(total / n)] * (n - 1)
    return seq(frames, each + [total - sum(each)])


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_ring": ("a_ring", "core", flight(4, 60, RING_MS, lead=1), [(0, 0)]),
    "a_hit": ("a_hit", "core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_drop": ("q_drop", ("ground", 53), spread(range(6), FALL_MS), [SOLES]),
    "q_hit": ("q_hit", ("ground", 17), seq(range(5), [40, 60, 80, 90, 100]), [SOLES]),
    "q_shred": ("q_shred", ("ground", 3.5), loop(6, 110), [OVER_HEAD]),
    "e_glow": ("e_glow", ("ground", 37), loop(6, 100), [SOLES]),
    "p_moon1": ("p_moon", "core", seq([0], [500]), [HER_MOON]),
    "p_moon2": ("p_moon", "core", seq([1], [500]), [HER_MOON]),
    "p_moon3": ("p_moon", "core", seq([2], [500]), [HER_MOON]),
    "r_warn": ("r_warn", ("ground", 11.5), spread(range(6), MOON_MS), [SOLES]),
    "r_fall": ("r_moon", ("ground", 67), spread(range(4), MOON_MS), [SOLES]),
    "r_moon": ("r_moon", ("ground", 67), seq(range(4, 10), [60, 80, 90, 100, 110, 120]), [SOLES]),
    "r_hit": ("r_hit", "core", seq(range(4), [40, 60, 70, 80]), [HIT]),
}
ICONS = {"icon_skill": "tft_alune_skill", "icon_skill2": "tft_alune_skill2", "icon_ult": "tft_alune_ult"}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name in FLYING:
            if not (c == c[::-1]).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric top to bottom")
        elif not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    man = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig"))
    meta = {}
    for e in man["items"]:                     # (its "effects" / "icons" are counts)
        if not e["file"].startswith("alune_fx_"):
            continue
        name = e["file"].replace("alune_fx_", "").replace(".png", "")
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", f"alune_fx_{name}.png"))
    need = {src for src, *_ in FX.values()}
    if need - set(meta):
        sys.exit(f"missing {sorted(need - set(meta))} (delivered {sorted(meta)})")
    allc = {n: cells(n, meta[n]) for n in sorted(need)}
    tables = {"tft_alune_fx": {}, "tft_alune_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_alune_big" if tag in BIG else "tft_alune_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"alune_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"alune_{src}.png is {im.size}, not 64 x 64")
        im.save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")
    if a.review:
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
            rows.append(img)
        sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
        y = 0
        for r in rows:
            sheet.alpha_composite(r, (0, y))
            y += r.height + 8
        sheet.convert("RGB").save(a.review)
        print(a.review)


if __name__ == "__main__":
    main()
