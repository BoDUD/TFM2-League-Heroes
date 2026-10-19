#!/usr/bin/env python3
"""Import Quinn's effects (assets/source/quinn/PROMPTS_FX.md, 16 pictures) as the game sheets league_quinn_fx and
league_quinn_big.

    python tools/art/import_quinn_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/quinn/codex_fx/quinn_fx: pixel_1x/quinn_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255; the projectiles
symmetric top to bottom, Valor circling a loop with no per-frame symmetry, everything else left to right - checked
again here). Each frame is cut by the manifest's frame size and placed as the kit plays it (import_zoe_fx.py's way):
spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from
the kit (build_quinn.P, 60 ticks a second). r_mount_fx is the add-on's (addons/league_quinn's copy plays it on the
mount).
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
from build_quinn import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn", "codex_fx", "quinn_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"a_bolt", "q_bird"}                      # turned with their flight: drawn going right
LOOP_ONLY = {"valor"}                          # a loop that looks the same from either side: no per-frame mirror
BIG = {"p_dive", "q_burst", "r_call", "r_land", "valor", "r_mount_fx"}
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head
HEAD = (0, -25)                 # a 36-px unit's crown
OVER_HER = (0, -28)             # just over Quinn's visor (her crown 26.5 over the pivot)
BODY = (0, -8)                  # the middle of her body
seq = J.seq
flight = J.flight
MS = 1000 / 60
BOLT_MS = P["atk_range"] / P["a_speed"] * MS * 2                     # the homing bolts (twice their straight flight)
Q_MS = P["q_range"] / P["q_speed"] * MS                              # Valor's line out (and home)


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_bolt": ("core", flight(2, 60, BOLT_MS, lead=1), [(0, 0)]),
    "q_bird": ("core", flight(4, 70, Q_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "p_hit": ("core", seq(range(4), [40, 60, 70, 90]), [HIT]),
    "p_dive": (("feet", 3), seq(range(6), [70, 70, 80, 90, 90, 100]), [HEAD]),        # P dive_t: 30 ticks
    "q_burst": (("feet", 0), seq(range(6), [50, 60, 80, 90, 80, 70]), [SOLES]),
    "q_hit": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "q_blind": ("core", loop(4, 120), [OVERHEAD]),
    "e_hit": ("core", seq(range(4), [50, 60, 80, 100]), [HIT]),
    "e_slow": (("feet", 0), loop(4, 120), [SOLES]),
    "w_haste": (("feet", 0), loop(4, 80), [SOLES]),
    "r_call": (("feet", 0), seq(range(6), [70, 80, 90, 90, 90, 80]), [SOLES]),        # the ult's 30-tick call
    "r_land": (("feet", 7), seq(range(6), [50, 60, 80, 90, 90, 90]), [SOLES]),
    "r_hit": ("core", seq(range(3), [40, 60, 80]), [HIT]),
    "valor": (("feet", 0), loop(8, 125), [OVER_HER]),
    "r_mount_fx": ("core", seq(range(5), [50, 60, 70, 80, 90]), [BODY]),
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
        if name not in LOOP_ONLY:
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
    for e in man.get("effects") or man["entries"]:
        name = (e.get("name") or e["id"]).removeprefix("quinn_fx_").removesuffix(".png")
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", e.get("file") or f"quinn_fx_{name}.png"))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_quinn_fx": {}, "league_quinn_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_quinn_big" if name in BIG else "league_quinn_fx"][name] = out
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
