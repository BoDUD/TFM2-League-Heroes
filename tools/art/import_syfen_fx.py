#!/usr/bin/env python3
"""Import Sy'fen's effects (assets/source/syfen/PROMPTS_FX.md: 12 pictures and 3 skill icons) as the tft pack's sheets
tft_syfen_fx and tft_syfen_big and its icons.

    python tools/art/import_syfen_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/syfen/codex_fx/syfen_fx: pixel_1x/syfen_fx_<name>.png, one row of
equal frames at game size, cell_1x and frames in manifest.json's assets; raw/ its drafts; 64 px icons). Every frame is
cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_daeja_fx.py's way): spots are game
px from the pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked left-right symmetric
(none flies: the client never mirrors a picture).
Anchors: the hits, the bites and the shrink on the body (the cell's middle, HIT); the slow and the shrink's sigil lie on
the ground round the feet (the cell's middle on the soles); the pictures round him - the wing sweep, the roar, the fury
- stand on his soles (the cell's bottom), and so does the charge's kick-off dust on the ground where it starts.
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
import pack_syfen_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "syfen", "codex_fx", "syfen_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it (the wing sweep's and
                                # the roar's last frames carried slivers of their neighbours, 2026-10-30)
# (effect, frame index) -> columns from each side cleared of parts lying within them: the wing sweep's last frame has a
# 5 x 22 bar at each side, a neighbour's cut, not its fading smoke
SIDE_CUT = {("e_sweep", 5): 6}


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "foot", frames with ms, spots)
FX = {
    # the attack's claw marks
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    # Bite: the jaws snapping shut on the target
    "q_bite": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # Wing Sweep: the two crescents round him (on his soles), the cut on each enemy, the slow round the feet (90 ticks)
    "e_sweep": ("foot", seq(range(6), [40, 50, 50, 60, 70, 80]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    "e_slow": ("core", loop(6, 90), [SOLES]),
    # Rampage: the roar's sound waves round him, the kick-off dust where the charge starts, the rammed, the great bite
    "r": ("foot", seq(range(6), [40, 50, 60, 60, 70, 80]), [SOLES]),
    "r_dash": ("foot", seq(range(4), [50, 60, 70, 80]), [SOLES]),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_bite": ("core", seq(range(6), [40, 50, 60, 70, 80, 100]), [HIT]),
    # Whispers: the shrink closing on the enemy, its sigil under the shrunk (p_t), his fury (an aura)
    "p": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "p_shrink": ("core", loop(6, 100), [SOLES]),
    "p_rage": ("foot", loop(6, 100), [SOLES]),
}
ICONS = {"icon_skill": "tft_syfen_skill", "icon_skill2": "tft_syfen_skill2", "icon_ult": "tft_syfen_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("syfen_fx_"):-4]: e for e in json.load(f)["assets"] if e["file"].startswith("syfen_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"syfen_fx_{name}.png"))).convert("RGBA")).copy()
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
    return [(w - 1) / 2, h - 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_syfen_fx": {}, "tft_syfen_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_syfen_big" if tag in BIG else "tft_syfen_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"syfen_{src}.png"))).convert("RGBA")
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
