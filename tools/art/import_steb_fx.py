#!/usr/bin/env python3
"""Import Steb's effects (assets/source/steb/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's sheets
tft_steb_fx and tft_steb_big and its icons.

    python tools/art/import_steb_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/steb/codex_fx/steb_fx: pixel_1x/steb_fx_<name>.png, one row of
equal frames at game size, cell_1x and frames in manifest.json's list; raw/ its drafts; 64 px icons). Every frame is
cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_sevika_fx.py's way): spots are
game px from the pivot (x forward, y down); a unit's soles are 11 under it. Every picture stays where it plays, so
every frame is checked symmetric left to right (none flies). Anchors: a hit on the body or a mark over a head
("core": the cell's middle); the pictures drawn round a unit - his dose, the bounty, the rush, the shared heal, the
pulses, the guard, the barrier - stand on the cell's bottom row ("foot"); the pack's circle lies on the ground with its
middle under his feet ("core" on SOLES).
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
import pack_steb_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "steb", "codex_fx", "steb_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set()
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
HEAD = (0, -34)                 # over a unit's head
MARK = (0, -37)                 # the Wanted mark hanging a little higher, clear of the stun
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "foot", frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    # Field Medicine: the dose round him, the strike, the stun over the struck one
    "q_heal": ("foot", seq(range(6), [60, 80, 90, 100, 110, 120]), [SOLES]),
    "q_hit": ("core", seq(range(6), [40, 50, 60, 70, 80, 90]), [HIT]),
    "q_stun": ("core", loop(6, 100), [HEAD]),
    # Wanted: the mark slamming down, the mark hanging on, the bounty on him, the rush on his side
    "e_mark": ("core", seq(range(6), [50, 50, 60, 80, 100, 120]), [MARK]),
    "e_wanted": ("core", loop(6, 110), [MARK]),
    "e_kill": ("foot", seq(range(8), [50, 70, 80, 90, 100, 110, 120, 140]), [SOLES]),
    "e_rush": ("foot", loop(6, 90), [SOLES]),
    # Field Medicine's passive: the share on an ally
    "p_heal": ("foot", seq(range(6), [60, 80, 90, 100, 110, 130]), [SOLES]),
    # Medic's Pack: the circle on the ground, a pulse, his guard, an ally's barrier
    "r_pack": ("core", seq(range(8), [50, 60, 80, 120, 120, 120, 140, 160]), [SOLES]),
    "r_heal": ("foot", seq(range(5), [60, 80, 90, 100, 120]), [SOLES]),
    "r_guard": ("foot", loop(6, 100), [SOLES]),
    "r_shield": ("foot", loop(6, 110), [SOLES]),
}
ICONS = {"icon_skill": "tft_steb_skill", "icon_skill2": "tft_steb_skill2", "icon_ult": "tft_steb_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("steb_fx_"):-len(".png")]: e for e in json.load(f) if e["file"].startswith("steb_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"steb_fx_{name}.png"))).convert("RGBA")).copy()
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
    tables = {"tft_steb_fx": {}, "tft_steb_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_steb_big" if tag in BIG else "tft_steb_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"steb_{src}.png"))).convert("RGBA")
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
