#!/usr/bin/env python3
"""Import Loris's effects (assets/source/loris/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's sheets
tft_loris_fx and tft_loris_big and its icons.

    python tools/art/import_loris_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/loris/codex_fx/loris_fx: pixel_1x/loris_fx_<name>.png, one row of
equal frames each at game size, the frame sizes the pack asked for (pack_loris_fx.FX); alpha 0 / 255; every frame
symmetric left to right - checked again here; loris_icon_<slot>.png 64 x 64). Each frame is cut and placed as the kit
plays it (import_maddie_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under
it. Times from the kit (build_loris.P, 60 ticks a second).
The ground rows were measured on the cells (2026-10-27): the barriers round him (q_shield rows 3-49, p_shield 1-48,
p_burst 1-50) centred on his middle, 21 over his soles (he is 42 tall); the iron stance's ring (r_wall 46); the kick-off
dust (q_dash 11); the guard landing's ring (e_land 43); the slam's shockwave (r_slam 24, its middle row); the knock-up's
dust jet (r_hit 18); the stun's ring of stars over a 36-tall unit's head (q_stun 43.5, the cell's bottom on the soles).
Codex drew the guard's badge and the taunt's anger mark over the unit's face (rows 7-16 of their 44-row cells, the
rings at 32-37): LIFT moves the rows above the split up so they sit over the head. Its slam (r_slam) came out a thin
flat line and dust puffs, too slight for the ult: slam_ring() lays under each frame the shockwave the pack asked for -
a bronze ellipse ring with a cyan inner edge spreading over the first five frames (14 to 80 squares wide, a third as
tall, its middle on the ground row), cracks running out from his feet that glow cyan and fade - Codex's dust and grit
kept on top, every frame still symmetric left to right.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_loris_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "loris", "codex_fx", "loris_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
seq = J.seq
LIFT = {"e_guard": (20, 12), "r_taunt": (20, 12)}     # rows above the first moved up by the second


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (source picture, anchor: "core" or ("ground", the cell's ground row), frames with ms, spots)
FX = {
    "a_hit": ("a_hit", "core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "q_shield": ("q_shield", ("ground", 47), seq(range(6), [50, 60, 70, 80, 90, 120]), [SOLES]),
    "q_dash": ("q_dash", ("ground", 11), seq(range(5), [60, 70, 80, 90, 100]), [SOLES]),
    "q_hit": ("q_hit", "core", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "q_stun": ("q_stun", ("ground", 43.5), loop(6, 100), [SOLES]),
    "e_land": ("e_land", ("ground", 43), seq(range(6), [60, 60, 70, 80, 100, 130]), [SOLES]),
    "e_guard": ("e_guard", ("ground", 48), loop(6, 120), [SOLES]),
    "r_slam": ("r_slam", ("ground", 24), seq(range(8), [50, 60, 70, 80, 90, 110, 130, 150]), [SOLES]),
    "r_hit": ("r_hit", ("ground", 18), seq(range(4), [50, 70, 80, 90]), [SOLES]),
    "r_taunt": ("r_taunt", ("ground", 46), loop(6, 100), [SOLES]),
    "r_wall": ("r_wall", ("ground", 46), loop(6, 120), [SOLES]),
    "p_shield": ("p_shield", ("ground", 45.5), loop(6, 140), [SOLES]),
    "p_burst": ("p_burst", ("ground", 46.5), seq(range(6), [60, 70, 70, 80, 100, 130]), [SOLES]),
}
ICONS = {"icon_skill": "tft_loris_skill", "icon_skill2": "tft_loris_skill2", "icon_ult": "tft_loris_ult"}
SIZES = {name: tuple(int(v) for v in size.replace(" ", "").split("×")) for name, _, _, size, *_ in PK.FX}


BRONZE = [(255, 240, 200), (242, 200, 120), (208, 140, 60), (142, 84, 32), (74, 40, 16)]
CYAN = [(242, 255, 255), (168, 246, 255), (62, 216, 240), (26, 140, 192)]
# frame -> (ring width or None, ring colour, inner edge colour, segmented); cracks: frame -> (length share, colour)
RING = {0: (14, BRONZE[0], None, False), 1: (34, BRONZE[1], CYAN[2], False), 2: (54, BRONZE[1], CYAN[1], False),
        3: (70, BRONZE[2], CYAN[2], False), 4: (80, BRONZE[3], CYAN[3], True)}
CRACKS = {2: (0.5, BRONZE[4]), 3: (0.8, BRONZE[4]), 4: (1.0, BRONZE[4]), 5: (1.0, CYAN[2]), 6: (1.0, CYAN[3]),
          7: (0.9, BRONZE[3])}
CRACK_DIRS = [(1.0, 0.0), (0.85, 0.32), (0.55, -0.28), (0.3, 0.36)]      # right half (mirrored), ground plane x, y


def slam_ring(c, k, gy):
    """Frame k of the slam with the shockwave ring and the cracks laid under Codex's drawing (its middle on row gy)."""
    from PIL import ImageDraw
    h, w = c.shape[:2]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = (w - 1) / 2
    if k in CRACKS:
        share, col = CRACKS[k]
        for dx, dy in CRACK_DIRS:
            L = 36 * share
            pts = [(cx + dx * L * f, gy + dy * L * f / 3 + (1 if f > 0.5 else 0)) for f in (0.15, 0.5, 1.0)]
            d.line([(round(x), round(y)) for x, y in pts], fill=col + (255,), width=1)
    if k in RING:
        rw, col, inner, seg = RING[k]
        rh = max(4, round(rw / 3))
        box = [round(cx - rw / 2), round(gy - rh / 2), round(cx + rw / 2), round(gy + rh / 2)]
        if k == 0:
            d.ellipse(box, fill=col + (255,))
        else:
            d.ellipse(box, outline=col + (255,), width=2 if rw < 70 else 1)
            if inner:
                d.ellipse([box[0] + 2, box[1] + 1, box[2] - 2, box[3] - 1], outline=inner + (255,), width=1)
        if seg:   # the last ring breaking into bright segments
            a = np.asarray(im).copy()
            ys, xs = np.nonzero(a[..., 3] > 0)
            gap = ((xs // 5) % 2 == 1) & (np.abs(xs - cx) > 6)
            a[ys[gap], xs[gap]] = 0
            im = Image.fromarray(a)
    a = np.asarray(im).copy()
    a[:, w - (w // 2):] = a[:, :w // 2][:, ::-1] if w % 2 == 0 else a[:, :w // 2 + 1][:, ::-1][:, 1:]
    out = a.copy()
    top = c[..., 3] > 0
    out[top] = c[top]
    return out


def lifted(c, split, up):
    """The rows above `split` moved `up` rows higher (the cell grows on top by `up`)."""
    out = np.zeros((c.shape[0] + up, c.shape[1], 4), np.uint8)
    out[up + split:] = c[split:]
    out[:split] = c[:split]
    return out


def cells(name):
    """The frames of Codex's game-size sheet, symmetry checked (and LIFT applied: the ground row then counts from the
    grown cell's top)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"loris_fx_{name}.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = SIZES[name]
    if a.shape[0] != h or a.shape[1] % w:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(a.shape[1] // w)]
    for k, c in enumerate(out):
        if not (c == c[:, ::-1]).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric left to right")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    if name in LIFT:
        out = [lifted(c, *LIFT[name]) for c in out]
    if name == "r_slam":
        out = [np.pad(c, ((0, 16), (0, 0), (0, 0))) for c in out]     # room under the ground row for the ring
        out = [slam_ring(c, k, FX["r_slam"][1][1]) for k, c in enumerate(out)]
        for k, c in enumerate(out):
            if not (c == c[:, ::-1]).all():
                sys.exit(f"r_slam frame {k + 1}: the ring broke the symmetry")
    return out


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, kind[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    allc = {n: cells(n) for n in sorted({src for src, *_ in FX.values()})}
    tables = {"tft_loris_fx": {}, "tft_loris_big": {}}
    for tag, (src, kind, frames, spots) in FX.items():
        cs = allc[src]
        anc = anchor(cs[0], kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_loris_big" if tag in BIG else "tft_loris_fx"][tag] = out
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        im = Image.open(lp(os.path.join(SRC, f"loris_{src}.png"))).convert("RGBA")
        if im.size != (64, 64):
            sys.exit(f"loris_{src}.png is {im.size}, not 64 x 64")
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
