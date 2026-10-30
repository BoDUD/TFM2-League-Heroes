#!/usr/bin/env python3
"""Import Idas's effects (assets/source/idas/PROMPTS_FX.md: 12 pictures and 3 skill icons) as the tft pack's sheets
tft_idas_fx and tft_idas_big and its icons.

    python tools/art/import_idas_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/idas/codex_fx/idas-fx: pixel_1x/idas_fx_<name>.png, one row of
equal frames at game size, cell_1x and frames in manifest.json's assets; raw/ its drafts; 64 px icons). Every frame is
cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_nomsy_fx.py's way): spots are
game px from the pivot (x forward, y down); a unit's soles are 11 under it. The symmetry is checked again: left to
right for every picture that stays where it plays; top to bottom for the breath, which flies along its picture-only
line and is turned with the cast (FLYING).
Anchors: a hit on the body ("core": the cell's middle); the pictures that stand on the ground - the shields round a
unit, the shell and its burst round her, the heal, the slow at the feet - on the cell's bottom row ("foot") or, for
the slow's ring lying on the ground, the cell's middle on the soles. The breath is drawn on its picture-only line's
middle (import_nomsy_fx's way): the kit's line is q_len long so that the breath's left end is at her open jaws (BREATH:
rig_idas's q_breath frame has the jaws' front 26 px ahead of the pivot and the mouth 35 over the ground, 24 over the
pivot: the breath's 56 px from 26 to 82 ahead, its middle 54 px = q_len / 2).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_idas_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "idas", "codex_fx", "idas-fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
HER = (1, 11)                   # round her: her body's middle is a px ahead of her pivot, her feet 11 under it
BODY = (0, -14)                 # on a unit's shoulders and over its head (the molten armour)
BREATH = (0, -24)               # the breath line's middle, at her open mouth's height
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "foot", frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    # Golden Breath: the breath on its line (looping while the line lasts), the molten armour on what it melts
    "q_breath": ("core", loop(6, 80), [BREATH]),
    "q_shred": ("core", loop(6, 90), [BODY]),
    # Dragon's Roar: the shockwave round her, the slow at the struck feet, the allies' light shields
    "e_roar": ("foot", seq(range(6), [50, 60, 70, 80, 90, 100]), [HER]),
    "e_slow": ("core", loop(6, 90), [SOLES]),
    "e_shield": ("foot", loop(6, 90), [SOLES]),
    # Guardian's Vow (tft.dll's): the flash on her and the ally, the shield while it holds
    "p_burst": ("foot", seq(range(5), [50, 60, 70, 80, 100]), [SOLES]),
    "p_shield": ("foot", loop(6, 90), [SOLES]),
    # Golden Scales: the shell round her while the wings close, its burst, her heal, the allies' shields
    "r_wrap": ("foot", loop(6, 90), [HER]),
    "r_burst": ("foot", seq(range(7), [50, 60, 70, 80, 90, 100, 120]), [HER]),
    "r_heal": ("foot", seq(range(6), [60, 70, 80, 90, 100, 110]), [HER]),
    "r_shield": ("foot", loop(6, 90), [SOLES]),
}
ICONS = {"icon_skill": "tft_idas_skill", "icon_skill2": "tft_idas_skill2", "icon_ult": "tft_idas_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("idas_fx_"):-4]: e for e in json.load(f)["assets"] if e["file"].startswith("idas_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"idas_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = m[name]["cell_1x"]
    if a.shape[0] != h or a.shape[1] != w * m[name]["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {m[name]['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(m[name]["frames"])]
    for c in out:   # bits of a neighbour at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            if part.sum() < EDGE_SPECK and (part[:, 0].any() or part[:, -1].any()):
                c[part] = 0
    for k, c in enumerate(out):
        flip = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == flip).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric " + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_idas_fx": {}, "tft_idas_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_idas_big" if tag in BIG else "tft_idas_fx"][tag] = out
        print(f"{tag:10s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"idas_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"{src}: {im.size}, not 64 x 64")
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
