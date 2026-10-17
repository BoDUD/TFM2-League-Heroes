#!/usr/bin/env python3
"""Import Jarvan IV's effects (assets/source/jarvaniv/PROMPTS_FX.md, 15 pictures) as the game sheets
league_jarvaniv_fx and league_jarvaniv_big.

    python tools/art/import_jarvaniv_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/jarvaniv/codex_fx: pixel_1x/jarvaniv_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's entries (cell_1x); alpha 0 / 255, symmetric left to
right - checked again here). Each frame is cut by the manifest's frame size and placed as the kit plays it
(import_nasus_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a
point's ground too. Times from the kit (build_jarvaniv.P, 60 ticks a second).
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
from build_jarvaniv import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jarvaniv", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = {"q_land", "e_flag", "w_cast", "r_ring"}
HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -34)             # just over a unit's head (the cracked shield)
EMPTY = J.EMPTY
seq = J.seq
MS = 1000 / 60


def looped(start, loop, end, start_ms, end_ms, total_ms, loop_ms=110):
    """start frames, the loop frames repeated to fill total_ms, end frames."""
    left = total_ms - sum(start_ms) - sum(end_ms)
    n = max(1, round(left / (loop_ms * len(loop))))
    k = left / (n * len(loop))
    return seq(start + loop * n + end, start_ms + [k] * (n * len(loop)) + end_ms)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_hit": ("core", seq(range(5), [40, 60, 70, 80, 90]), [HIT]),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the armour shred's red cracked shield over each unit Q struck (a buff's loop)
    "q_shred": ("core", seq(range(4), [120, 120, 120, 120]), [OVERHEAD]),
    # E -> Q: the shock where he lands at the standard (on the ground, under the units)
    "q_land": (("feet", 6), seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    # the standard where the lob lands: it drops in, stands its f_t ticks (frames 3-6 looped), vanishes
    "e_flag": (("feet", 2), looped([0, 1], [2, 3, 4, 5], [6, 7], [70, 90], [150, 200], P["f_t"] * MS, 140), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 60, 70, 80]), [HIT]),
    # the rally aura at an ally's feet (a buff's loop)
    "f_as": (("feet", 3), seq(range(4), [130, 130, 130, 130]), [SOLES]),
    "w_cast": (("feet", 4), seq(range(6), [50, 60, 70, 80, 90, 110]), [SOLES]),
    # the shield shell round him while w_on lasts (a buff's loop)
    "w_on": (("feet", 2), seq(range(4), [120, 120, 120, 120]), [SOLES]),
    "w_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "w_slow": (("feet", 2), seq(range(4), [130, 130, 130, 130]), [SOLES]),
    # Cataclysm's rock ring round the landing point: rises, stands r_t ticks (frames 4-7 looped), crumbles
    "r_ring": (("feet", 12), looped([0, 1, 2], [3, 4, 5, 6], [7], [60, 80, 100], [250], P["r_t"] * MS, 130), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "r_zap": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
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
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
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
    meta = {e["name"]: e for e in man.get("effects", man.get("images", []))}
    rb = os.path.join(SRC, "readback.json")            # a re-read from the drafts, if one is made
    if os.path.exists(lp(rb)):
        for name, r in json.load(open(lp(rb), encoding="utf-8")).items():
            meta[name] = {**meta[name], "frames": r["frames"], "cell_1x": r["cell_1x"]}
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(FX)}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_jarvaniv_fx": {}, "league_jarvaniv_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_jarvaniv_big" if name in BIG else "league_jarvaniv_fx"][name] = out
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
