#!/usr/bin/env python3
"""Import Nomsy's effects (assets/source/nomsy/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's sheets
tft_nomsy_fx and tft_nomsy_big and its icons.

    python tools/art/import_nomsy_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/nomsy/codex_fx/nomsy-fx: pixel_1x/nomsy_fx_<name>.png, one row of
equal frames at game size, cell_1x and frames in manifest.json's assets; raw/ its drafts; 64 px icons). Every frame is
cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_sevika_fx.py's way): spots are
game px from the pivot (x forward, y down); a unit's soles are 11 under it. The symmetry is checked again: left to
right for every picture that stays where it plays; top to bottom for the four that fly and are turned with their
flight (FLYING: the bolt, the big fireball, the small bouncing ones, the breath on its picture-only line).
Anchors: a hit on the body ("core": the cell's middle); the pictures that stand on the ground - the explosion, the
falling fireball (its last frames touch down on the cell's bottom row), the impact, the pictures round her - on the
cell's bottom row ("foot"). The breath is drawn on its picture-only line's middle at pivot height (import_chogath_fx):
the kit's line is e_len long so that the flame's left end is at her open mouth (BREATH: rig_nomsy's e_breath frame
has the mouth's front 28 px ahead of the pivot, 14 over the ground: the flame's 48 px from 26 to 74 ahead, its middle
50 px = e_len / 2, raised 3 px).
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
import pack_nomsy_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nomsy", "codex_fx", "nomsy-fx")
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
BODY = (0, -10)                 # on a unit's body (a burn)
FLY = (0, 0)                    # a projectile's own point
BREATH = (0, -3)                # the breath line's middle, at her open mouth's height
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
# Codex's soot wisp over e_burn's flames reads as a little grey figure (a ring head, arms) over the burnt unit's head:
# grey squares (soot, low saturation) in the top SOOT share of its cells are dropped; the scorch at the feet is kept
SOOT = {"e_burn": 0.5}


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "foot", frames with ms, spots)
FX = {
    "a_bolt": ("core", loop(4, 60), [FLY]),
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    # Fireballs!: the big one flying, its explosion on the struck units' ground, the small ones bouncing on (tft.dll)
    "q_ball": ("core", loop(6, 70), [FLY]),
    "q_hit": ("foot", seq(range(7), [50, 60, 70, 80, 90, 100, 120]), [SOLES]),
    "q_bounce": ("core", loop(4, 60), [FLY]),
    "q_bounce_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Dragon Breath: the flame on its line (looping while the line lasts), the burn on what it scorches
    "e_flame": ("core", loop(6, 80), [BREATH]),
    "e_burn": ("core", loop(6, 90), [BODY]),
    # Dragon Ascension: a fireball falling the kit's r_fall_t 18 ticks (300 ms: touching down at 250-300 ms on frame 6,
    # bursting on 7 as r_hit comes), the impact, the glow under her while she flies, the ascended aura
    "r_fall": ("foot", seq(range(7), [50, 50, 50, 50, 50, 50, 100]), [SOLES]),
    "r_hit": ("foot", seq(range(6), [40, 50, 60, 70, 80, 100]), [SOLES]),
    "r_fly": ("core", loop(6, 100), [SOLES]),
    "r_up": ("foot", loop(6, 100), [HER]),
    # Dragon Body (tft.dll's heal: its 40-tick buff)
    "p_heal": ("foot", seq(range(6), [60, 80, 90, 100, 110, 120]), [HER]),
}
ICONS = {"icon_skill": "tft_nomsy_skill", "icon_skill2": "tft_nomsy_skill2", "icon_ult": "tft_nomsy_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("nomsy_fx_"):-4]: e for e in json.load(f)["assets"] if e["file"].startswith("nomsy_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"nomsy_fx_{name}.png"))).convert("RGBA")).copy()
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
    if name in SOOT:
        for c in out:
            rgb = c[..., :3].astype(int)
            grey = (c[..., 3] > 0) & (rgb.max(-1) - rgb.min(-1) < 40)
            grey[int(h * SOOT[name]):] = False
            c[grey] = 0
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
    tables = {"tft_nomsy_fx": {}, "tft_nomsy_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_nomsy_big" if tag in BIG else "tft_nomsy_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"nomsy_{src}.png"))).convert("RGBA")
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
