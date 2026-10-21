#!/usr/bin/env python3
"""Import Naafiri's effects (assets/source/naafiri/PROMPTS_FX.md, 21 pictures) as the game sheets league_naafiri_fx and
league_naafiri_big.

    python tools/art/import_naafiri_fx.py [--review out.png]

The source is the step-3 delivery (assets/source/naafiri/codex_fx/naafiri_fx: pixel_1x/naafiri_fx_<name>.png, one row of
equal frames each at game size, frame sizes in manifest.json's effects (cell_1x); alpha 0 / 255). The daggers and the
pack's streak are projectiles (the game turns them to their flight: flying left they turn upside down, so they must be
symmetric top to bottom); every other picture is symmetric left to right (the client never mirrors it on the red side) -
both checked again here. Each frame is cut by the manifest's frame size and placed as the kit plays it (import_mel_fx.py's
way, import_zoe_fx's): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it, a point's
ground too. Her own pictures are centred on her standing point (the middle of her body: symmetric for the red side). Which
sheet an effect goes to is read from the kit's own views (build_naafiri.build), so the two never disagree. Times from the
kit (build_naafiri.P, 60 ticks a second).
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
import build_naafiri as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "naafiri", "codex_fx", "naafiri_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)
P = K.P


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


TB = {"q_dagger", "q2_dagger", "q_leap"}     # projectiles: turned to their flight by the game
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
LOW = (0, -9)                   # a bite lower on it (the pack reaches its flank)
SOLES = (0, 11)                 # on the ground under a unit or a point
OVERHEAD = (0, -29)             # over a 36-px unit's head
FLIGHT = (0, 0)                 # a projectile's own point
HER = (0, 11)                   # her soles under her standing point (the middle of her body)
HER_MID = (0, -4)               # the middle of her low body (15 px over her soles)
HER_TOP = (0, -8)               # a little under her top (her blades reach 30 px over her soles)
seq = J.seq
MS = 1000 / 60


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("feet", rows above the cell's bottom row), frames with ms, spots)
FX = {
    "q_dagger": ("core", loop(4, 60), [FLIGHT]),
    "q2_dagger": ("core", loop(4, 60), [FLIGHT]),
    "q_leap": ("core", loop(3, 60), [FLIGHT]),
    "a_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "pk_bite": ("core", seq(range(3), [50, 60, 70]), [LOW]),
    "pk_bite4": ("core", seq(range(3), [50, 60, 80]), [LOW]),
    "pk_leap": ("core", seq(range(4), [50, 60, 60, 80]), [LOW]),
    # the pack mauling the champion Q hit: played every pk_period ticks while the ride lasts, the hounds' paws on its
    # soles (a picture shorter than the bite's interval: 4 frames of 150 ms in 750)
    "pk_ride": (("feet", 0), seq(range(4), [150, 150, 150, 150]), [SOLES]),
    "q_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "q_bleed": ("core", seq(range(3), [70, 80, 90]), [HIT]),
    "q2_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_heal": ("core", seq(range(4), [70, 80, 90, 110]), [HER_MID]),
    # Eviscerate's two shreds round her: the ellipse's middle 4 squares over the cell's bottom row, on her soles
    "e_slash": (("feet", 4), seq(range(4), [50, 60, 70, 90]), [HER]),
    "e_slash2": (("feet", 4), seq(range(4), [50, 60, 70, 90]), [HER]),
    "e_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    # the roar over r_roar ticks: the cell's bottom on her soles
    "r_roar": (("feet", 0), seq(range(5), [60, 70, 80, 90, round(P["r_roar"] * MS) - 300]), [HER]),
    "r_hit": ("core", seq(range(4), [50, 60, 80, 90]), [HIT]),
    "r_reset": (("feet", 0), seq(range(4), [80, 120, 120, 140]), [HER_TOP]),
    # buffs, looped while they hold: the aura's ellipse middle on her soles, the shred mark over the champion's head, the
    # shield's open bottom on her soles
    "pack_aura": (("feet", 9), loop(4, 120), [HER]),
    "r_shred": ("core", loop(4, 120), [OVERHEAD]),
    "r_shield": (("feet", 0), loop(4, 110), [HER]),
}


def sheets_of_kit():
    """{effect: "league_naafiri_fx" or "league_naafiri_big"} as the kit's views name them."""
    kit = K.build(dict(P))
    out = {}
    for group in ("view_projectiles", "view_effects", "view_buffs"):
        for v in kit[group]:
            out[v["tag"]] = v["anim"].rsplit("/", 1)[1]
    return out


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
        name = os.path.basename(e["file"])[len("naafiri_fx_"):-len(".png")]
        meta[name] = dict(e, pixel_1x=os.path.join(SRC, "pixel_1x", os.path.basename(e["file"])))
    if set(meta) != set(FX):
        sys.exit(f"delivered {sorted(meta)} against the importer's {sorted(FX)}")
    sheet_of = sheets_of_kit()
    if set(sheet_of) != set(FX):
        sys.exit(f"the kit's views {sorted(sheet_of)} against the importer's {sorted(FX)}")
    for name, (_, frames, _) in FX.items():
        if any(k >= meta[name]["frames"] for k, _ in frames if k != J.EMPTY):
            sys.exit(f"{name}: a frame past the delivered {meta[name]['frames']}")
    allc = {n: cells(n, meta[n]) for n in FX}
    tables = {"league_naafiri_fx": {}, "league_naafiri_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = allc[name]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables[sheet_of[name]][name] = out
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
