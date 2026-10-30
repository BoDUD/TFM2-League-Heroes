#!/usr/bin/env python3
"""Import Shi Oh Yu's effects (assets/source/shiohyu/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's
sheets tft_shiohyu_fx and tft_shiohyu_big and its icons.

    python tools/art/import_shiohyu_fx.py [--review out.png]

The source is the user's Gemini run cleaned by tools/art/clean_shiohyu_fx.py (assets/source/shiohyu/gemini_fx/clean:
pixel_1x/shiohyu_fx_<name>.png, one row of equal frames at game size, cell_1x and frames in manifest.json;
shiohyu_icon_<slot>.png 64 x 64). Every frame is cut as cleaned (alpha 0 / 255) and placed as the kit plays it
(import_daeja_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. The
symmetry is checked again: left to right for every picture that stays where it plays; top to bottom for the jade wave
(FLYING: a line the game turns with the cast).
Anchors (rows measured on the cleaned cells, 2026-10-30): the hits on the body (the cell's middle, HIT); the ground
pictures by the row that lies on the soles - the slam's ellipse (e_slam row 13), the rock burst (e_hit 12, its lowest
row), the snare (e_slow 4), the spikes of the wave's hit (r3_hit 16), and the rings round his feet of the stance flash
(r 47), the stance aura (r_jade 44), the stone skin flash (p 46) and the skin aura (p_skin 44). The wave is drawn on its
line's middle (the kit's r3_wave line is r3_len 92000 long and the picture 92 wide: its left end at him).
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
import pack_shiohyu_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shiohyu", "gemini_fx", "clean")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
FLY = (0, 0)                    # a projectile's own point (the wave line's middle)
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or ("ground", the cell's row on the soles), frames with ms, spots)
FX = {
    # the claw swipes; the fists of Jade Fist Barrage (four, 8 ticks apart: 133 ms)
    "a_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "q_hit": ("core", seq(range(3), [40, 40, 50]), [HIT]),
    # Earthshaker: the slam on the ground under him, the rock burst at each enemy's feet, the snare (90 ticks)
    "e_slam": (("ground", 13), seq(range(6), [50, 60, 80, 90, 100, 120]), [SOLES]),
    "e_hit": (("ground", 12), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "e_slow": (("ground", 4), loop(6, 120), [SOLES]),
    # Jade Form: the flash as it comes on, the aura while it holds, the three blows' hits, the wave on its line (it
    # hits r3_delay 18 ticks = 300 ms after it shows) and its spikes under every enemy in it
    "r": (("ground", 47), seq(range(5), [70, 80, 90, 90, 100]), [SOLES]),
    "r_jade": (("ground", 44), loop(6, 110), [SOLES]),
    "r1_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r2_hit": ("core", seq(range(3), [60, 70, 80]), [HIT]),
    "r3_wave": ("core", seq(range(6), [40, 40, 50, 50, 60, 60]), [FLY]),
    "r3_hit": (("ground", 16), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    # Jade Skin: the flash as his skin turns, the aura while it holds (180 ticks)
    "p": (("ground", 46), seq(range(5), [70, 80, 90, 90, 100]), [SOLES]),
    "p_skin": (("ground", 44), loop(6, 120), [SOLES]),
}
ICONS = {"icon_skill": "tft_shiohyu_skill", "icon_skill2": "tft_shiohyu_skill2", "icon_ult": "tft_shiohyu_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("shiohyu_fx_"):-4]: e for e in json.load(f) if e["file"].startswith("shiohyu_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"shiohyu_fx_{name}.png"))).convert("RGBA")).copy()
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
    return [(w - 1) / 2, kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_shiohyu_fx": {}, "tft_shiohyu_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_shiohyu_big" if tag in BIG else "tft_shiohyu_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"shiohyu_{src}.png"))).convert("RGBA")
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
