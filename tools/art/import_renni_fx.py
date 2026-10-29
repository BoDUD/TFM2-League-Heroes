#!/usr/bin/env python3
"""Import Renni's effects (assets/source/renni/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft pack's sheets
tft_renni_fx and tft_renni_big and its icons.

    python tools/art/import_renni_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/renni/codex_fx/renni_fx: pixel_1x/renni_fx_<name>.png, one row
of equal frames at game size, cell_1x and frames in manifest.json; raw/ its 1254 px drafts). All ten read back whole
at 8x (2026-10-29: the motes, rings, arcs and stars all there, every frame left-right symmetric), so every frame is cut
from pixel_1x as delivered. Each frame is placed as the kit plays it (import_scar_fx.py's way): spots are game px from
the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit (build_renni.P, 60 ticks a second).
Anchors: a hit on the body ("core": the cell's middle); a ground effect on its widest row of the lower half ("ground");
the pictures drawn round her - the shimmer shot and rush, the guard - stand on the cell's bottom row ("foot": Codex
drew them round a body whose soles are that row). The slam's crack plays on the target she slams down (the kit's
ViewEffect: a picture placed ahead of her would stay on her right facing left, lint_mod). The icons are cut from Codex's raws (LANCZOS to 64, Violet's way).
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
import pack_renni_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renni", "codex_fx", "renni_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
HEAD = (0, -34)                 # over a unit's head
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core", "ground" or "foot", frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    "q_hit": ("q_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "q_slow": ("q_slow", "ground", loop(6, 100), [SOLES]),
    "p": ("p", "foot", seq(range(6), [60, 80, 100, 110, 120, 130]), [SOLES]),
    "p_rush": ("p_rush", "foot", loop(6, 100), [SOLES]),
    "e": ("e", "foot", seq(range(5), [50, 70, 80, 90, 100]), [SOLES]),
    "e_guard": ("e_guard", "foot", loop(6, 110), [SOLES]),
    "r_up": ("r_up", "core", loop(6, 100), [HEAD]),
    "r_hit": ("r_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "r_slam": ("r_slam", "ground", seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
}
ICONS = {"icon_skill": "tft_renni_skill", "icon_skill2": "tft_renni_skill2", "icon_ult": "tft_renni_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["name"]: e for e in json.load(f) if e.get("kind") == "fx"}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"renni_fx_{name}.png"))).convert("RGBA")).copy()
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
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def ground_row(cs):
    """The widest row of the frames' lower half (all frames together)."""
    op = np.zeros(cs[0].shape[:2], int)
    for c in cs:
        op += c[..., 3] > 0
    h = op.shape[0]
    widths = [(op[y] > 0).sum() for y in range(h)]
    return int(max(range(h // 2, h), key=lambda y: (widths[y], y)))


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, ground_row(cs)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    allc = {n: cells(n, m) for n in sorted({src for src, *_ in FX.values()})}
    tables = {"tft_renni_fx": {}, "tft_renni_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_renni_big" if tag in BIG else "tft_renni_fx"][tag] = out
        print(f"{tag:8s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, "raw", f"renni_{src}.png"))).convert("RGBA").resize((64, 64), Image.LANCZOS)
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
