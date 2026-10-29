#!/usr/bin/env python3
"""Import Smeech's effects (assets/source/smeech/PROMPTS_FX.md: 8 pictures and 3 skill icons) as the tft pack's sheet
tft_smeech_fx and its icons.

    python tools/art/import_smeech_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/smeech/codex_fx/smeech_fx: raw/smeech_fx_<name>.png its 1920-2200
px drafts, manifest.json where each frame was cut from them (sample_rects) and at what game size (cell_1x)). Codex's own
pixel_1x came down with an 18% cover threshold and forced symmetry, and read at 8x (2026-10-29) the thin claw lines broke
into scattered squares (a_hit's X a gold blur, e_shred's split shield a green gem), as Scar's did. Its drafts are clean,
so every effect is read from raw/ again (import_scar_fx.redo's way): each frame's cut box in blocks of its own size
(the box over cell_1x, across and down apart: q_land and r_frenzy were cut wider than tall; only the frame's own strip
between its source_x_boundaries - the boxes reach into the neighbours), a block drawn where COVER
of it is drawn, in the median colour of its brighter half (a two-square claw line survives), every colour then the
nearest of the pack's ramps (pack_smeech_fx); each frame laid over its mirror and its left half copied over the right
(they sit on units and the client never mirrors them). Each frame is placed as the kit plays it (import_violet_fx.py's
way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. The ground ones stand on
their widest row of the frames' lower half. The icons are Codex's own 64 x 64 (32 squares at 2 px).
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
import pack_smeech_fx as PK  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "smeech", "codex_fx", "smeech_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
HEAD = (0, -34)                 # over a unit's head
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
COVER = 0.12
RAMPS = [PK.CLAW, PK.CHEM, PK.CRIT, PK.SCRAP, PK.GRIME]


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "ground", frames with ms, spots); his own (q_land, r_frenzy) on his soles
FX = {
    "a_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "p_hit": ("core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "q_land": ("ground", seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "q_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "e_hit": ("core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "e_shred": ("core", loop(6, 100), [HEAD]),
    "r_hit": ("core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "r_frenzy": ("ground", loop(6, 90), [SOLES]),
}
ICONS = {"icon_skill": "tft_smeech_skill", "icon_skill2": "tft_smeech_skill2", "icon_ult": "tft_smeech_ult"}


def ramp_colours():
    cols = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for r in RAMPS for c in r.split(", ")], np.uint8)
    return cols, srgb2lab(cols.astype(float) / 255.0)


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("smeech_fx_"):-4]: e for e in json.load(f)["entries"] if "sample_rects" in e}


def redo(name):
    """The frames read again from Codex's draft: every frame's cut box in blocks of its own size, made symmetric."""
    e = manifest()[name]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", e["file"]))).convert("RGBA"))
    cols, lab = ramp_colours()
    W, H = e["cell_1x"]
    bounds = e["source_x_boundaries"]
    out = []
    for k, (x0, y0, x1, y1) in enumerate(e["sample_rects"]):
        own = raw.copy()            # only this frame's own strip of the draft (the cut boxes reach into the neighbours)
        own[:, :int(bounds[k])] = 0
        own[:, int(bounds[k + 1]):] = 0
        bx, by = (x1 - x0) / W, (y1 - y0) / H
        c = np.zeros((H, W, 4), np.uint8)
        for j in range(H):
            for i in range(W):
                b = own[int(round(y0 + j * by)):int(round(y0 + (j + 1) * by)),
                        int(round(x0 + i * bx)):int(round(x0 + (i + 1) * bx))].reshape(-1, 4)
                if not len(b):
                    continue
                op = b[b[:, 3] >= 128]
                if len(op) < COVER * len(b):
                    continue
                lum = op[:, :3].astype(int) @ np.array([299, 587, 114])
                bright = op[lum >= np.median(lum)]
                rgb = np.median(bright[:, :3], axis=0)
                k = np.argmin(((srgb2lab(rgb[None].astype(float) / 255.0) - lab) ** 2).sum(-1))
                c[j, i, :3], c[j, i, 3] = cols[k], 255
        c = np.where(c[..., 3:] > 0, c, c[:, ::-1])     # over its mirror, then the left half copied over the right
        half = W // 2
        c[:, W - half:] = c[:, :half][:, ::-1]
        out.append(c)
    return out


def cells(name):
    """The frames of an effect, symmetry checked."""
    out = redo(name)
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
    return [(w - 1) / 2, ground_row(cs)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    allc = {n: cells(n) for n in FX}
    table = {}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        table[tag] = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms)
                      for k, ms in frames]
        print(f"{tag:9s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    w, h = G.write_sheet(lp(os.path.join(MOD, "effects", "tft_smeech_fx")), table, share=True)
    print(f"tft/effects/tft_smeech_fx#sheet.png {w}x{h}: " + ", ".join(
        f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in table.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"smeech_{src}.png"))).convert("RGBA")
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
