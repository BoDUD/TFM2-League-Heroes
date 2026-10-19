#!/usr/bin/env python3
"""Import Powder's effects (assets/source/powder/PROMPTS_FX.md: 14 pictures and 3 skill icons) as the tft pack's sheets
tft_powder_fx and tft_powder_big and its icons.

    python tools/art/import_powder_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/powder/codex_fx/powder_fx: pixel_1x/powder_fx_<name>.png, one row
of equal frames each at game size, frame sizes in manifest.json (cell_1x); alpha 0 / 255; everything but the three
tumbling projectiles symmetric left to right - checked again here; pixel_1x/powder_icon_<slot>.png 64 x 64). Each
frame is cut by the manifest's frame size and placed as the kit plays it (import_zoe_fx.py's way): spots are game px
from the pivot (x forward, y down); a unit's soles are 11 under it, a point's ground too. Times from the kit
(build_powder.P, 60 ticks a second).
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
from build_powder import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "powder", "codex_fx", "powder_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TUMBLE = {"a_pop", "q_monkey", "r_bag"}       # turned with their flight, tumbling: no symmetry asked
BIG = {"q_blast", "e_smoke", "r_warn", "r_blast"}
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
BODY = (0, -8)                  # the middle of a unit
EYES = (0, -22)                 # a unit's eye level
seq = J.seq
flight = J.flight
MS = 1000 / 60
POP_MS = P["atk_range"] / P["a_speed"] * MS * 2           # the homing firecracker (twice its straight flight)
MONKEY_MS = P["q_travel"] * MS                            # the lobbed monkey
BAG_MS = P["r_travel"] * MS                               # the lobbed bag
FUSE_MS = P["r_show"] * MS                                # the fizzing bag re-stamped every r_show ticks
WARN_MS = BAG_MS                                          # the landing ring the whole flight


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom), frames with ms, spots)
FX = {
    "a_pop": ("core", flight(4, 60, POP_MS, lead=1), [(0, 0)]),
    "q_monkey": ("core", flight(4, 70, MONKEY_MS, lead=1), [(0, 0)]),
    "r_bag": ("core", flight(4, 70, BAG_MS, lead=1), [(0, 0)]),
    "a_hit": ("core", seq(range(3), [50, 60, 70]), [HIT]),
    "q_blast": (("feet", 0), seq(range(6), [40, 60, 80, 90, 100, 110]), [SOLES]),
    "q_hit": ("core", seq(range(4), [40, 60, 80, 90]), [HIT]),
    "q_wound": ("core", loop(4, 110), [BODY]),
    "e_smoke": (("feet", 0), seq(range(6), [40, 60, 80, 100, 110, 120]), [SOLES]),
    "e_blind": ("core", seq(range(4), [70, 80, 80, 90]), [EYES]),
    "r_cast": ("core", seq(range(3), [50, 70, 90]), [(4, -20)]),
    "r_warn": (("feet", 0), loop(4, WARN_MS / 4), [SOLES]),
    "r_fuse": (("feet", 0), loop(4, FUSE_MS / 4), [SOLES]),
    "r_blast": (("feet", 0), seq(range(6), [40, 70, 90, 110, 120, 130]), [SOLES]),
    "r_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
}
ICONS = {"icon_skill": "tft_powder_skill", "icon_skill2": "tft_powder_skill2", "icon_ult": "tft_powder_ult"}


def cells(name, meta):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        if name not in TUMBLE and not (c == c[:, ::-1]).all():
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
    meta = {}
    for e in man.get("effects") or man.get("entries") or []:
        name = (e.get("name") or e.get("id") or e["file"]).replace("powder_fx_", "").replace(".png", "")
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", e["file"]))
    if set(FX) - set(meta):
        sys.exit(f"missing {sorted(set(FX) - set(meta))} (delivered {sorted(meta)})")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"tft_powder_fx": {}, "tft_powder_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_powder_big" if name in BIG else "tft_powder_fx"][name] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        p = os.path.join(SRC, "pixel_1x", f"powder_{src}.png")
        im = Image.open(lp(p)).convert("RGBA")
        if im.size != (64, 64):
            im = im.resize((64, 64), Image.NEAREST)
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
