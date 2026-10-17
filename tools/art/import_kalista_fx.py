#!/usr/bin/env python3
"""Import Kalista's effects (assets/source/kalista/PROMPTS_FX.md, 15 pictures) as the game sheets league_kalista_fx and
league_kalista_big.

    python tools/art/import_kalista_fx.py [--review out.png]

The source is the 15 pictures of Codex's step-3 run as the user forwarded them (JPEG screenshots, each 2000 px wide,
assets/source/kalista/codex_fx/kalista_fx_<name>.jpg; the user: 「这是特效 你帮我处理一下然后导入吧」): no pixel_1x, every
picture at its own scale, on black, grey, dark grey or a checkerboard. Each picture is a row of equal cells (CELLS:
columns, rows, the cells used); the background keyed out (KEY), then read import_elise_fx.py's way through
import_kassadin.py: one scale per effect (the biggest frame's content to SIZE), every game pixel the commonest colour
under it snapped to the prompt's ramps with the bright cores kept, the red side's symmetry - the flying spears top to
bottom, everything else left to right about its own best axis (the fuller half mirrored) - checked square for square.
Codex drew Pierce's spear 8 times in 2 columns (the left column's last two without the head's glow): the right column
is used. Rend's slow ring came twice (two rows): the upper row is used. The rings round a figure are sized to our
heroes (34-42 px tall), not the prompt's 22-px figure.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_kalista.P, 60 ticks a second).
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
import import_kassadin as K  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
from build_kalista import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kalista", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


# the prompt's ramps (pack_kalista_fx.py)
GREEN = ["#FFFFFF", "#D9FFF1", "#7CF5C8", "#22D9A0", "#0E9C78", "#075443"]
SPEAR = ["#E8F4F8", "#8A8FA0", "#4C4F60", "#26262F", "#121217"]
BLUE = ["#FFFFFF", "#CFE9FF", "#7EB8FF", "#3C7BE0", "#1D3E8A"]
EARTH = ["#F2E6CF", "#D6C3A0", "#B39B76", "#8A7255", "#5E4C39"]
DARKS = {(0x07, 0x54, 0x43), (0x12, 0x12, 0x17), (0x1D, 0x3E, 0x8A), (0x5E, 0x4C, 0x39)}
RAMPS = {"g": GREEN, "s": GREEN + SPEAR, "b": BLUE + GREEN, "d": BLUE + EARTH}

# effect -> (columns, rows, [(column, row) used], (y0, y1) rows of the picture or None, ramps)
CELLS = {
    "a_spear": (2, 1, [(0, 0), (1, 0)], None, "s"),
    "q_spear": (2, 4, [(1, 0), (1, 1), (1, 2), (1, 3)], None, "s"),
    "a_hit": (4, 1, [(k, 0) for k in range(4)], None, "g"),
    "q_hit": (5, 1, [(k, 0) for k in range(5)], None, "g"),
    "w_hit": (4, 1, [(k, 0) for k in range(4)], None, "g"),
    "sp_mark": (2, 1, [(0, 0), (1, 0)], None, "s"),
    "e_rip": (5, 1, [(k, 0) for k in range(5)], None, "s"),
    "e_cast": (5, 1, [(k, 0) for k in range(5)], (372, 744), "g"),
    "e_reset": (4, 1, [(k, 0) for k in range(4)], None, "g"),
    "r_take": (6, 1, [(k, 0) for k in range(6)], None, "b"),
    "r_fly": (4, 1, [(k, 0) for k in range(4)], None, "b"),
    "r_land": (6, 1, [(k, 0) for k in range(6)], None, "d"),
    "r_up": (5, 1, [(k, 0) for k in range(5)], None, "b"),
    "e_slow": (4, 1, [(k, 0) for k in range(4)], (455, 662), "g"),
    "r_safe": (4, 1, [(k, 0) for k in range(4)], None, "b"),
}
# the background: "dark" (black or near-black cells), ("grey", level), "checker"; the pictures without a spear keep
# only coloured or near-white pixels (their cell lines and grey bands are neutral)
KEY = {"a_spear": "checker", "e_rip": ("grey", 131), "e_reset": ("grey", 53), "e_slow": "dark"}
SPEARS = {"a_spear", "q_spear", "sp_mark", "e_rip"}
# the biggest frame's size in game px: ("w" | "h", n)
# (the small ones ~30% over the prompt's sizes - the user, 10-16: 「有的特效也做大点吧稍微 看起来不太明显」)
SIZE = {"a_spear": ("w", 20), "q_spear": ("w", 30), "a_hit": ("w", 14), "q_hit": ("w", 22), "w_hit": ("w", 18),
        "sp_mark": ("h", 17), "e_rip": ("w", 20), "e_cast": ("w", 38), "e_reset": ("w", 16), "r_take": ("h", 42),
        "r_fly": ("h", 44), "r_land": ("w", 40), "r_up": ("h", 36), "e_slow": ("w", 20), "r_safe": ("h", 44)}
SYM = {"a_spear": "tb", "q_spear": "tb"}     # every other one "lr"
BIG = {"e_cast", "r_take", "r_fly", "r_land", "r_safe"}

HIT = (0, -14)                  # a hit on the upper body of a 34-42 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
MID = (0, -9)                   # a unit's middle (the rings round a figure)
HEAD = (0, -38)                 # over her head
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
# effect -> (anchor kind, frames with ms, spots)
FX = {
    # the spear: atk_range 52500 at spear_speed 8000 a tick, ~7 ticks (homing: twice)
    "a_spear": ("core", flight(2, 60, 2 * P["atk_range"] / P["spear_speed"] * MS), [(0, 0)]),
    # Pierce: q_len 115000 at q_speed 9000, ~13 ticks in a straight line
    "q_spear": ("core", flight(4, 60, P["q_len"] / P["q_speed"] * MS), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "w_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    # the spear stuck in him, played every sp_pic ticks: its two frames fill them
    "sp_mark": ("core", seq(range(2), [P["sp_pic"] * MS / 2] * 2), [HIT]),
    "e_rip": ("burst", seq(range(5), [50, 60, 70, 80, 90]), [HIT]),
    "e_cast": ("core", seq(range(5), [50, 60, 70, 80, 90]), [MID]),
    "e_reset": ("core", seq(range(4), [50, 60, 80, 100]), [HEAD]),
    # the Oathsworn drawn in over r_hold ticks (500 ms)
    "r_take": (("feet", 0), seq(range(6), [60, 70, 80, 100, 100, 90]), [SOLES]),
    # hurled: the aura flickering through the flight (r_fly 40 ticks at most), the last frame held
    "r_fly": ("core", seq([0, 1, 2, 3, 0, 1, 2, 3], [80] * 7 + [1000]), [MID]),
    "r_land": ("ring", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES]),
    "r_up": (("feet", 0), seq(range(5), [60, 70, 100, 130, 160]), [SOLES]),
    # buffs (looped while they last): the slow e_slow_t, the shroud r_hold + r_fly
    "e_slow": ("core", seq(range(4), [100] * 4), [SOLES]),
    "r_safe": (("feet", 0), seq(range(4), [120] * 4), [SOLES]),
}


def key(rgb, kind, spear):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    if kind == "checker":
        a = (mx - mn > 16) | (mn > 150)        # the tiles are neutral greys (lighter under the spear), the shaft bluish
    elif isinstance(kind, tuple):
        a = np.abs(rgb - kind[1]).max(-1) > 30
    else:
        a = mx > (30 if spear else 40)
    if not spear:
        a &= (mx - mn > 20) | (mn > 190)
    return np.where(a, 255, 0).astype(np.int16)


def strip(name):
    """The used cells of the picture side by side, keyed, as one RGBA sheet; the frames' boxes in it."""
    cols, rows, used, band, _ = CELLS[name]
    im = np.asarray(Image.open(lp(os.path.join(SRC, f"kalista_fx_{name}.jpg"))).convert("RGB")).astype(np.int16)
    if band:
        im = im[band[0]:band[1]]
    H, W = im.shape[:2]
    cw, ch = W // cols, H // rows
    pieces = [im[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw] for c, r in used]
    rgb = np.concatenate(pieces, 1)
    a = key(rgb, KEY.get(name, "dark"), name in SPEARS)
    sheet = np.concatenate([rgb, a[..., None]], -1)
    return sheet, (1, ch - 1), [(k * cw + 2, (k + 1) * cw - 2) for k in range(len(used))]


KASSADIN_SHRINK = K.shrink


def thin_shrink(a, s):
    """import_kassadin's shrink, but a game pixel a fifth covered is drawn (not 45%): the flying spears' trail, shaft
    and blade are thinner than a game pixel in the screenshots."""
    H, W = a.shape[:2]
    h, w = max(1, int(round(H * s))), max(1, int(round(W * s)))
    idx = K.snap(np.clip(a[..., :3], 0, 255))
    alpha = a[..., 3] > 100
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        ya, yb = int(j / s), max(int(j / s) + 1, int((j + 1) / s))
        for i in range(w):
            xa, xb = int(i / s), max(int(i / s) + 1, int((i + 1) / s))
            m = alpha[ya:yb, xa:xb]
            if m.size == 0 or m.mean() < 0.2:
                continue
            ids, cnt = np.unique(idx[ya:yb, xa:xb][m], return_counts=True)
            best = ids[cnt.argmax()]
            lit = [(K.PAL_LUM[k], k) for k, c in zip(ids, cnt) if K.PAL_LUM[k] >= K.BRIGHT and c >= 0.25 * cnt.sum()]
            if lit:
                best = max(lit)[1]
            out[j, i, :3], out[j, i, 3] = K.PAL[best], 255
    return out


def use_ramps(names):
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in names]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS


def build_cells():
    cells = {}
    for name in CELLS:
        sheet, band, boxes = strip(name)
        use_ramps(RAMPS[CELLS[name][4]])
        K.BOXES = {name: (name, band, boxes)}
        K.SIZE, K.SYM, K.AXIS = SIZE, SYM, {}
        K.shrink = thin_shrink if name in SHAFTS else KASSADIN_SHRINK
        frames, s, _ = K.frames_of(name, {name: sheet})
        sym = SYM.get(name, "lr")
        cs = K.common_cell(frames, sym, None, s, band)
        if sym == "lr":
            cs, _ = K.trim_rows(cs)
        else:
            any_col = np.zeros(cs[0].shape[1], bool)
            for c in cs:
                any_col |= c[..., 3].any(0)
            xs = np.nonzero(any_col)[0]
            cs = [c[:, xs.min():xs.max() + 1] for c in cs]
            any_row = np.zeros(cs[0].shape[0], bool)
            for c in cs:
                any_row |= c[..., 3].any(1)
            ys = np.nonzero(any_row)[0]
            top = min(ys.min(), cs[0].shape[0] - 1 - ys.max())
            cs = [c[top:c.shape[0] - top] for c in cs]
        if name in SHAFTS:
            cs = [shaft(c, sheet, box, s) for c, box in zip(cs, boxes)]
        K.check(name, cs, sym)
        cells[name] = cs
    return cells


SHAFTS = {"a_spear", "q_spear"}
SPEAR_RGB = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in SPEAR[1:4]])


def shaft(cell, sheet, box, s):
    """The flying spears' black shaft is thinner than a game pixel in the screenshots (and inside Pierce's glow): the
    middle row gets it back - every column whose source column has the neutral grey shaft near the picture's middle
    row, in the nearest of the spear ramp's greys."""
    a = sheet[:, box[0]:box[1]]
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    x0, x1, ymid = xs.min(), xs.max(), (ys.min() + ys.max()) / 2
    rgb = a[..., :3]
    neutral = op & (rgb.max(-1) - rgb.min(-1) < 30) & (rgb.max(-1) < 140)
    half = max(2, int(0.6 / s))
    band = neutral[int(ymid) - half:int(ymid) + half + 1]
    cols = np.nonzero(cell[..., 3].any(0))[0]
    c0, c1 = cols.min(), cols.max()
    out = cell.copy()
    H = cell.shape[0]
    rows = [H // 2] if H % 2 else [H // 2 - 1, H // 2]
    for j in range(c0, c1 + 1):
        sa = int(x0 + (j - c0) / (c1 - c0 + 1) * (x1 - x0 + 1))
        sb = int(x0 + (j - c0 + 1) / (c1 - c0 + 1) * (x1 - x0 + 1))
        m = band[:, sa:max(sb, sa + 1)]
        if m.sum() < 0.15 * m.size:
            continue
        px = a[int(ymid) - half:int(ymid) + half + 1, sa:max(sb, sa + 1), :3][m]
        col = SPEAR_RGB[np.abs(SPEAR_RGB[None] - np.median(px, 0)[None, None]).sum(-1).argmin()]
        for r in rows:
            out[r, j, :3], out[r, j, 3] = col, 255
    return out


def burst_anchor(cells):
    """Rend's rip: the middle of frame 3's burst (the spear gone above it)."""
    c = cells[2]
    ys, xs = np.nonzero(c[..., 3] > 0)
    return [(c.shape[1] - 1) / 2, float(np.median(ys))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    cells = build_cells()
    tables = {"league_kalista_fx": {}, "league_kalista_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        if kind == "ring":
            anc = K.ring_anchor(cs)
        elif kind == "burst":
            anc = burst_anchor(cs)
        else:
            anc = K.anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_kalista_big" if name in BIG else "league_kalista_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, cs in cells.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        Ht = sum(r.height + 10 for _, r in rows)
        sheet = Image.new("RGB", (W, Ht), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(a.review)
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
