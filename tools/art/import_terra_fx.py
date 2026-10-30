#!/usr/bin/env python3
"""Import Terra's effects (assets/source/terra/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft pack's sheets
tft_terra_fx and tft_terra_big and its icons.

    python tools/art/import_terra_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/terra/codex_fx/terra_fx: pixel_1x/terra_fx_<name>.png, one row of
equal frames at game size, cell_1x and frames in manifest.json's assets; raw/ its drafts; 64 px icons). Every frame is
cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_terra_fx.py's way): spots are game
px from the pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked left-right symmetric
(none flies: the client never mirrors a picture).
Anchors: the hits and the bite on the body (the cell's middle, HIT); the slow lies on the ground round the feet (the
cell's middle on the soles); the taunt mark floats over the taunted one's head (OVER); the pictures round her - the
roar, the rock shield, the quake's armour, the ground waking under her - stand on her soles (the cell's bottom) under
the middle of her body (BODY: 5 game px behind her standing point), and the earthquake ring's ellipse is centred on the
ground there (its own centre row QUAKE_ROW: the heaved wall stands above it at the back).
Icons: Codex's 64 px icons were its 1254 px tiles voted down 2 x 2 into mud; brought to 64 x 64 again from the raw tiles
with LANCZOS (tft_sohm's way).
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
import pack_terra_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "terra", "codex_fx", "terra_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
OVER = (0, -30)                 # over a unit's head
BODY = (-5, 11)                 # under the middle of her body (champion_view's centre x), on her soles
QUAKE_ROW = 31                  # r_quake: the row of its cell the ellipse is centred on (the wall rises above it)
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
SIDE_CUT = {}


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Rock Claw's hit
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    # Rending Bite: the stone jaws on the target, the cracked ground under the slowed (q_slow_t 90 ticks)
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_slow": ("core", loop(6, 100), [SOLES]),
    # Dragon's Roar: the sound waves round her, the mark over the taunted, her floating rock slabs (an aura)
    "e": ("foot", seq(range(6), [40, 50, 60, 70, 80, 90]), [BODY]),
    "e_taunt": ("core", loop(6, 100), [OVER]),
    "e_shield": ("foot", loop(6, 120), [BODY]),
    # Earthquake: the ground waking under her, each stomp's ring (on the ground where she stomped), the spikes under the
    # hit, her stone armour after (an aura)
    "r": ("foot", seq(range(4), [60, 70, 80, 90]), [BODY]),
    "r_quake": (QUAKE_ROW, seq(range(7), [50, 60, 70, 80, 90, 100, 110]), [BODY]),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_res": ("foot", loop(6, 120), [BODY]),
}
ICONS = {"icon_skill": "tft_terra_skill", "icon_skill2": "tft_terra_skill2", "icon_ult": "tft_terra_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("terra_fx_"):-4]: e for e in json.load(f)["assets"] if e["file"].startswith("terra_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"terra_fx_{name}.png"))).convert("RGBA")).copy()
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
            side = part[:, :EDGE_STRIP].any() or part[:, -EDGE_STRIP:].any()
            thin = np.ptp(np.nonzero(part.any(0))[0]) < EDGE_STRIP   # a sliver of the next cell standing at the side
            if side and (part.sum() < EDGE_SPECK or thin):
                c[part] = 0
    for (fx, k), cols in SIDE_CUT.items():
        if fx != name:
            continue
        c = out[k]
        lb, n = ndimage.label(c[..., 3] > 0, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            xs = np.nonzero((lb == j).any(0))[0]
            if xs.max() < cols or xs.min() >= c.shape[1] - cols:
                c[lb == j] = 0
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
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, kind]


def icon(name):
    """Codex's raw 1254 px icon tile -> 64 x 64 (LANCZOS): its own 64 px cut voted 2 x 2 blocks into mud."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"terra_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_terra_fx": {}, "tft_terra_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_terra_big" if tag in BIG else "tft_terra_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        icon(src).save(lp(os.path.join(MOD, "icons", dst + ".png")))
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
