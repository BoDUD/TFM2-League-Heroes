#!/usr/bin/env python3
"""Import Scar's effects (assets/source/scar/PROMPTS_FX.md: 11 pictures and 3 skill icons) as the tft pack's sheets
tft_scar_fx and tft_scar_big and its icons.

    python tools/art/import_scar_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/scar/codex_fx/scar_fx: pixel_1x/scar_fx_<name>.png, one row of
equal frames at game size; raw/ its 1254-1774 px drafts, manifest.json where each frame was cut from them). Each frame
is placed as the kit plays it (import_violet_fx.py's way): spots are game px from the pivot (x forward, y down); a
unit's soles are 11 under it. Times from the kit (build_scar.P, 60 ticks a second).
Codex brought its drafts down with an 18% cover threshold and forced every picture symmetric, and four came out lost
(8x, 2026-10-28): p_heal's rising motes and the star over its head gone (a faint ring left), q_bomb a dark square
whose middle frames vanish on the arena, q_stun's circling stars flattened into bands, r_guard's arcs a few faint
squares. Its drafts are good, so REDO reads those four from raw/ again: each frame's whole cut box (one size for all of
an effect's frames, so the pieces keep their places) in blocks of BLOCK px, a block drawn where COVER of it is drawn,
in the median colour of its brighter half (a mote of two draft squares survives), every colour then the nearest of
the pack's ramps (pack_scar_fx). p_heal and r_guard are made symmetric by laying each frame over its mirror (they ride
on him and the client never mirrors them); q_stun circles over a head and q_bomb spins, neither has a side, so they
stay as drawn (the check below skips them). q_bomb is turned a quarter left: its picture is turned with its flight
(drawn flying to the image right), so the fuse trails behind it whichever way it is thrown.
Ground effects stand on their widest row of the frames' lower half (measured here); the hits sit on the body. The icons
are cut from Codex's raws (LANCZOS to 64, Violet's way).
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
import pack_scar_fx as PK  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scar", "codex_fx", "scar_fx")
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
# re-read from the drafts: effect -> (px a game square, symmetric by mirror, quarter turns left)
REDO = {"p_heal": (13.0, True, 0), "r_guard": (12.2, True, 0), "q_stun": (21.0, False, 0), "q_bomb": (31.0, False, 1)}
COVER = 0.12
NOT_SYMMETRIC = {"q_stun", "q_bomb"}
RAMPS = [PK.GOLD, PK.FIRE, PK.IMPACT, PK.PAINT, PK.DUST, PK.STEEL]


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or "ground", frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "p_hit": ("p_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "p_heal": ("p_heal", "ground", seq(range(5), [70, 90, 110, 130, 150]), [SOLES]),
    "q_bomb": ("q_bomb", "core", loop(4, 80), [(0, 0)]),
    "q_hit": ("q_hit", "core", seq(range(6), [50, 60, 70, 80, 100, 120]), [HIT]),
    "q_stun": ("q_stun", "core", loop(6, 100), [HEAD]),
    "e_hit": ("e_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "r_bomb": ("r_bomb", "ground", seq(range(6), [50, 70, 90, 110, 130, 150]), [SOLES]),
    "r_land": ("r_land", "ground", seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("r_hit", "ground", seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "r_guard": ("r_guard", "ground", loop(6, 120), [SOLES]),
}
ICONS = {"icon_skill": "tft_scar_skill", "icon_skill2": "tft_scar_skill2", "icon_ult": "tft_scar_ult"}
SIZES = {name: tuple(int(v) for v in size.replace(" ", "").split("×")) for name, _, _, size, *_ in PK.FX}


def ramp_colours():
    cols = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for r in RAMPS for c in r.split(", ")], np.uint8)
    return cols, srgb2lab(cols.astype(float) / 255.0)


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("scar_fx_"):-4]: e for e in json.load(f)["effects"]}


def redo(name):
    """The frames read again from Codex's draft (REDO): every frame's whole cut box in blocks."""
    block, sym, turns = REDO[name]
    e = manifest()[name]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", e["source"]))).convert("RGBA"))
    cols, lab = ramp_colours()
    out = []
    for f in e["frame_details"]:
        x0, y0, x1, y1 = f["source_box"]
        box = raw[y0:y1, x0:x1]
        W, H = int(round((x1 - x0) / block)), int(round((y1 - y0) / block))
        c = np.zeros((H, W, 4), np.uint8)
        for j in range(H):
            for i in range(W):
                b = box[int(j * block):int((j + 1) * block), int(i * block):int((i + 1) * block)].reshape(-1, 4)
                op = b[b[:, 3] >= 128]
                if len(op) < COVER * len(b):
                    continue
                lum = op[:, :3].astype(int) @ np.array([299, 587, 114])
                bright = op[lum >= np.median(lum)]
                rgb = np.median(bright[:, :3], axis=0)
                k = np.argmin(((srgb2lab(rgb[None].astype(float) / 255.0) - lab) ** 2).sum(-1))
                c[j, i, :3], c[j, i, 3] = cols[k], 255
        if sym:   # laid over its mirror, then its left half copied over the right (a square both have: the left's)
            c = np.where(c[..., 3:] > 0, c, c[:, ::-1])
            half = W // 2
            c[:, W - half:] = c[:, :half][:, ::-1]
        out.append(np.rot90(c, turns).copy())
    # one cell for all: the frames' union box
    union = np.zeros(out[0].shape[:2], bool)
    for c in out:
        union |= c[..., 3] > 0
    ys, xs = np.nonzero(union)
    x0, x1 = xs.min(), xs.max() + 1
    if sym:   # keep the box symmetric about the middle
        r = max(out[0].shape[1] / 2 - x0, x1 - out[0].shape[1] / 2)
        x0, x1 = int(np.floor(out[0].shape[1] / 2 - r)), int(np.ceil(out[0].shape[1] / 2 + r))
    return [c[ys.min():ys.max() + 1, x0:x1].copy() for c in out]


def cells(name):
    """The frames of an effect, symmetry checked."""
    if name in REDO:
        out = redo(name)
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"scar_fx_{name}.png"))).convert("RGBA")).copy()
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
        a[a[..., 3] == 0] = 0
        w, h = SIZES[name]
        if a.shape[0] != h or a.shape[1] % w:
            sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
        out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for c in out:   # bits of a neighbour at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            if part.sum() < EDGE_SPECK and (part[:, 0].any() or part[:, -1].any()):
                c[part] = 0
    for k, c in enumerate(out):
        if name not in NOT_SYMMETRIC and not (c == c[:, ::-1]).all():
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
    allc = {n: cells(n) for n in sorted({src for src, *_ in FX.values()})}
    tables = {"tft_scar_fx": {}, "tft_scar_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_scar_big" if tag in BIG else "tft_scar_fx"][tag] = out
        print(f"{tag:8s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, "raw", f"scar_{src}-generated.png"))).convert("RGBA").resize(
            (64, 64), Image.LANCZOS)
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
