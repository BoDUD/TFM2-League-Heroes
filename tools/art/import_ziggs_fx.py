#!/usr/bin/env python3
"""Import Ziggs's effects (assets/source/ziggs/PROMPTS_FX.md, 20 pictures) as the game sheets league_ziggs_fx and
league_ziggs_big.

    python tools/art/import_ziggs_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/ziggs/codex_fx: pixel_1x/ziggs_fx_<name>.png, one row of equal
frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255; the projectiles symmetric top
to bottom, everything else left to right - checked again here). Each frame is cut by the manifest's frame size and
placed as the kit plays it (import_jarvaniv_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's
soles are 11 under it, a point's ground too. Times from the kit (build_ziggs.P, 60 ticks a second).
The bouncing bomb (q_bomb) is not bound itself: every stamp height of build_ziggs.air_heights gets its own tag
q_air<h> - one frame (a stamp shows until the next, q_step ticks later), the bomb's lowest row h px over the ground.
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
from build_ziggs import P, air_heights  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ziggs", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bomb", "p_bomb", "e_throw", "r_bomb"}      # turned with their flight: drawn going right, symmetric top to bottom
BIG = {"q_blast", "e_land", "e_field", "w_blast", "r_cast", "r_bomb", "r_warn", "r_boom"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
BOMB_MS = P["atk_range"] / P["a_speed"] * MS * 2                     # the homing bomb (twice its straight flight)
E_MS = P["e_travel"] * MS                                            # the mines' lob
R_MS = P["r_travel"] * MS                                            # the mega bomb's lob
STAMP_MS = P["q_step"] * MS                                          # a bouncing-bomb stamp until the next
SHOW_MS = P["e_show"] * MS                                           # the minefield re-stamped every e_show ticks
# R's big bomb over his head: from the cast to the heave (r_rel), then gone
R_HOLD = P["r_rel"] * MS - 60
# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_bomb": ("core", flight(3, 60, BOMB_MS, lead=1), [(0, 0)]),
    "p_bomb": ("core", flight(3, 60, BOMB_MS, lead=1), [(0, 0)]),
    "e_throw": ("core", flight(2, 80, E_MS, lead=1), [(0, 0)]),
    "r_bomb": ("core", flight(3, 70, R_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_hit": ("core", seq(range(5), [40, 60, 70, 80, 90]), [HIT]),
    "q_bounce": (("feet", 0), seq(range(3), [50, 70, 90]), [SOLES]),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_blast": (("feet", 4), seq(range(6), [40, 60, 70, 90, 100, 120]), [SOLES]),
    "e_land": (("feet", 11), seq(range(4), [50, 70, 90, 110]), [SOLES]),
    "e_field": (("feet", 11), seq(range(3), [SHOW_MS / 3] * 3), [SOLES]),
    "e_hit": (("feet", 0), seq(range(4), [40, 60, 70, 80]), [SOLES]),
    "e_slow": (("feet", 2), seq(range(4), [130, 130, 130, 130]), [SOLES]),
    "w_blast": (("feet", 4), seq(range(6), [50, 50, 70, 90, 110, 130]), [SOLES]),
    "w_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "r_cast": (("feet", 0), seq(range(4), [60, R_HOLD / 2, R_HOLD / 2, 80]), [SOLES]),
    "r_warn": (("feet", 15), seq(range(8), [R_MS / 8] * 8), [SOLES]),
    "r_boom": (("feet", 6), seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
}
DELIVERED = set(FX) | {"q_bomb"}


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
        sym = (c == c[::-1]).all() if name in TB else (c == c[:, ::-1]).all()
        if not sym:
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
    meta = {e.get("name") or os.path.basename(e["file"])[len("ziggs_fx_"):-4]: e for e in man.get("effects", man.get("images", []))}
    rb = os.path.join(SRC, "readback.json")            # a re-read from the drafts, if one is made
    if os.path.exists(lp(rb)):
        for name, r in json.load(open(lp(rb), encoding="utf-8")).items():
            meta[name] = {**meta[name], "frames": r["frames"], "cell_1x": r["cell_1x"]}
    if set(meta) != DELIVERED:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(DELIVERED)}")
    allc = {n: cells(n, meta[n]) for n in sorted(DELIVERED)}
    tables = {"league_ziggs_fx": {}, "league_ziggs_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_ziggs_big" if name in BIG else "league_ziggs_fx"][name] = out
    # the bouncing bomb's stamps: its lowest row h px over the ground, one frame each (the spark flickers by height)
    bomb = allc["q_bomb"]
    for h in sorted({min(h, 18) // 2 * 2 for _, _, _, h in air_heights(P)}):
        c = bomb[(h // 2) % len(bomb)]
        tables["league_ziggs_fx"][f"q_air{h}"] = [(J.place(c, anchor(c, ("feet", 0)), [(0, SOLES[1] - h)]), STAMP_MS)]
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
