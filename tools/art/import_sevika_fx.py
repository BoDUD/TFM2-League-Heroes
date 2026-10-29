#!/usr/bin/env python3
"""Import Sevika's effects (assets/source/sevika/PROMPTS_FX.md: 17 pictures and 3 skill icons) as the tft pack's sheets
tft_sevika_fx and tft_sevika_big and its icons.

    python tools/art/import_sevika_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/sevika/codex_fx/sevika_fx: pixel_1x/sevika_fx_<name>.png, one row
of equal frames at game size, cell_1x and frames in manifest.json's assets; raw/ its drafts; 64 px icons). Every frame
is cut from pixel_1x as delivered (alpha 0 / 255, read whole at 6x, 2026-10-29) and placed as the kit plays it
(import_renni_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. The
symmetry is checked again: left to right for every picture that stays where it plays; top to bottom for the three
that fly and are turned with their flight (FLYING: the flame on its picture-only line, the rockets, the fist).
Anchors: a hit on the body ("core": the cell's middle); the pictures drawn round her - the shield, the shimmer, the
jackpot fountain - stand on the cell's bottom row ("foot"). A line's picture is drawn on the line's middle at pivot
height (import_chogath_fx.py): the kit's picture-only flame line is q_len long so that its middle is the flame's
middle, the flame's left end at her claws (FLAME: 11 over the pivot, where the levelled arm is in her q_flame frames).
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
import pack_sevika_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sevika", "codex_fx", "sevika_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = {"q_flame", "p_rocket", "e_fist"}
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
HEAD = (0, -34)                 # over a unit's head
HER_HEAD = (0, -38)             # over her own head (39 game px, the soles 11 under the pivot)
BODY = (0, -10)                 # on a unit's body (a burn, a bleed)
FLY = (0, 0)                    # a projectile's own point
FLAME = (0, -11)                # the flame line's middle, at her levelled claws' height
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "foot", frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    "a2_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # High Roller: the slot machine over her head at every cast; Jinx's mods
    "p": ("core", seq(range(8), [60, 70, 80, 90, 100, 110, 120, 150]), [HER_HEAD]),
    "p_rocket": ("core", loop(4, 60), [FLY]),
    "p_rocket_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "p_shield": ("foot", seq(range(6), [50, 70, 80, 90, 100, 110]), [SOLES]),
    "p_jackpot": ("foot", seq(range(8), [60, 80, 100, 110, 120, 130, 140, 160]), [SOLES]),
    "p_shimmer": ("foot", loop(6, 100), [SOLES]),
    "p_triple": ("core", loop(6, 100), [HER_HEAD]),
    # Flamethrower: the flame on its line (looping while the line lasts), the burn on what it licks
    "q_flame": ("core", loop(6, 80), [FLAME]),
    "q_burn": ("core", loop(6, 90), [BODY]),
    # Extendo-Punch: the fist flying, its hit, the stun of the two knocked together
    "e_fist": ("core", loop(4, 50), [FLY]),
    "e_hit": ("core", seq(range(6), [40, 50, 60, 70, 80, 90]), [HIT]),
    "e_stun": ("core", loop(6, 100), [HEAD]),
    # Chomp: each bite, the bleed, the execution
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_bleed": ("core", loop(6, 110), [BODY]),
    "r_kill": ("core", seq(range(8), [50, 60, 70, 80, 90, 100, 120, 140]), [HIT]),
}
ICONS = {"icon_skill": "tft_sevika_skill", "icon_skill2": "tft_sevika_skill2", "icon_ult": "tft_sevika_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["id"][3:]: e for e in json.load(f)["assets"] if e["id"].startswith("fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"sevika_fx_{name}.png"))).convert("RGBA")).copy()
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
    tables = {"tft_sevika_fx": {}, "tft_sevika_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_sevika_big" if tag in BIG else "tft_sevika_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"sevika_{src}.png"))).convert("RGBA")
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
