#!/usr/bin/env python3
"""Azir's line of sand to each of his soldiers (the user, 2026-10-30: 「沙皇和召唤的士兵之间没连接线 LOL是有的」).

    python tools/art/fx_azir_tether.py [--review out.png]

League draws a beam of swirling sand (Azir_Base_W_SoldierIndicator: Azir_base_Z_Beam_Core / _Outer, gold sand
streaks scrolling along it) from Azir to every soldier within the tether radius (Arise!'s 660, the command range since
V7.19). Here the add-on (addons/league_azir) spawns one projectile a soldier every tick, its picture one straight piece
as long as the gap between them: the game turns a projectile's picture to its direction, so each piece is drawn
pointing right (toward the soldier) and a tag per length, `tether_<px>` for px in TETHER_MIN..=TETHER_MAX step 2
(src/lib.rs), one frame each.

The piece: a 1 px core of gold sand with a pale grain every FLOW_P px, and a deep gold grain above and below it a step
apart (a twisted strand of sand). The grains repeat every FLOW_P px from the piece's start, and the add-on moves the
start a px toward the soldier every FLOW_T ticks, so the sand flows from him to the soldier as League's does. Above and
below the same colour: a picture pointing left is this one turned half round. No outline (VFX spec); the colours are
the ones in league_azir_fx (Codex's sand). Of three colourings tried over grass, sand and grey ground (a pale core with
gold or deep gold grains, this gold core), the pale core all but vanished on sand; the gold one reads on all three.

Written to addons/league_azir/effects/league_azir_tether (the add-on's own sheet: no change to the main pack;
addons/league_addons/assemble.py carries it into the bundle). addons/league_azir/make_override.py adds the views.
"""
import argparse
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

LIB = os.path.join(ROOT, "addons", "league_azir", "src", "lib.rs")
OUT = os.path.join(ROOT, "addons", "league_azir", "effects", "league_azir_tether")
SHEET = "league_azir_tether"


def hexes(*hs):
    return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in hs]


# league_azir_fx's sand: the pale grain, the gold core, the deep gold of the strands
GRAIN, CORE, STRAND = hexes("#FFF2C8", "#F8BC2C", "#C47A12")


def consts():
    """TETHER_MIN, TETHER_MAX and FLOW_P from the add-on's src/lib.rs (its constants are the only copy)."""
    src = open(LIB, encoding="utf-8").read()
    out = {}
    for k in ("TETHER_MIN", "TETHER_MAX", "FLOW_P"):
        m = re.search(r"pub const " + k + r": usize = (\d+);", src)
        if not m:
            sys.exit(f"{k} not in {os.path.relpath(LIB, ROOT)}")
        out[k] = int(m.group(1))
    if out["TETHER_MIN"] % 2 or out["TETHER_MAX"] % 2 or out["TETHER_MIN"] >= out["TETHER_MAX"]:
        sys.exit(f"tether lengths {out['TETHER_MIN']}..{out['TETHER_MAX']} are not even and rising")
    return out


def lengths(c):
    return list(range(c["TETHER_MIN"], c["TETHER_MAX"] + 1, 2))


def piece(n, p):
    """One piece n px long pointing right, its pivot in its middle: rows -1, 0, +1; the grains repeat every p px."""
    a = np.zeros((3, n, 4), np.uint8)
    for x in range(n):
        a[1, x, :3] = GRAIN if x % p == 0 else CORE
        a[1, x, 3] = 255
        if x % p == 1:
            a[0, x, :3] = STRAND
            a[0, x, 3] = 255
        if x % p == 2:
            a[2, x, :3] = STRAND
            a[2, x, 3] = 255
    return G.centre_frame(a, -(n // 2), -1)


def frames(c=None):
    """{tag: [(frame centred on its pivot, ms)]}: one frame a length (the add-on draws a new piece every tick)."""
    c = c or consts()
    return {f"tether_{n}": [(piece(n, c["FLOW_P"]), 100)] for n in lengths(c)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="a few pieces at 12x")
    a = ap.parse_args()
    c = consts()
    tags = frames(c)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    w, h = G.write_sheet(OUT, tags, share=True)
    print(f"addons/league_azir/effects/{SHEET}#sheet.png {w}x{h}: {len(tags)} tags "
          f"tether_{c['TETHER_MIN']} .. tether_{c['TETHER_MAX']}, grains every {c['FLOW_P']} px")
    if a.review:
        Z = 12
        show = [tags[f"tether_{n}"][0][0] for n in (c["TETHER_MIN"], 20, 40)]
        ims = [Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST) for f in show]
        can = Image.new("RGBA", (max(i.width for i in ims) + 12, sum(i.height + 12 for i in ims)), (70, 78, 60, 255))
        y = 6
        for i in ims:
            can.alpha_composite(i, (6, y))
            y += i.height + 12
        can.save(a.review)


if __name__ == "__main__":
    main()
