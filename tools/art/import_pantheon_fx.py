#!/usr/bin/env python3
"""Import Pantheon's effects (assets/source/pantheon/PROMPTS_FX.md, 19 pictures) as the game sheets league_pantheon_fx
and league_pantheon_big.

    python tools/art/import_pantheon_fx.py [--review out.png]

The source is the 19 pictures of Codex's step-3 run as the user forwarded them (JPEG screenshots, each 2000 px wide,
assets/source/pantheon/codex_fx/pantheon_fx_<name>.jpg; the user, 2026-10-16: 「处理一下特效 然后帮我导入」): every
picture at its own scale on black, some with thin white lines between the cells. Each picture is a row of equal cells
(CELLS: columns, rows, the cells used, the band of rows used); the background keyed out, then read import_kalista_fx.py's
way through import_kassadin.py: one scale per effect (the biggest frame's content to SIZE), every game pixel the commonest
colour under it snapped to the prompt's ramps with the bright cores kept, the red side's symmetry - the flying spear and
the thrust top to bottom, everything else left to right about its own best axis (the fuller half mirrored).
Codex drew the comet spear 8 times in 2 columns (the right column flying left): the left column is used. The landing
ring (r_mark) came as round rings seen from above: squashed to a third of its height first (a ground ellipse like the
other rings). The thin spear shafts (q_spear, q_thrust, r_spear) are read with a game pixel drawn from a fifth covered.
The small hits are ~30 % over the prompt's sizes (Kalista's lesson: 「有的特效也做大点吧稍微」).
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_pantheon.P, 60 ticks a second).
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
from build_pantheon import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "pantheon", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


# the prompt's ramps (pack_pantheon_fx.py)
GOLD = ["#FFFFFF", "#FFF6C8", "#FFE066", "#FFB627", "#F07A12", "#A4440B"]
COSMIC = ["#FFFFFF", "#C9D2FF", "#7C83F0", "#4A3FB5", "#2B1F72", "#160F3D"]
FIRE = ["#FFFFFF", "#FFE9A8", "#FFB13B", "#F2581A", "#B0280F", "#5A1408"]
EARTH = ["#E8DCC4", "#C2AC88", "#96805F", "#6B5843", "#463A2E"]
DARKS = {(0xA4, 0x44, 0x0B), (0x16, 0x0F, 0x3D), (0x5A, 0x14, 0x08), (0x46, 0x3A, 0x2E)}
RAMPS = {"g": GOLD, "gc": GOLD + COSMIC, "gf": GOLD + FIRE, "ge": GOLD + EARTH, "f": FIRE, "fce": FIRE + COSMIC + EARTH}

# effect -> (columns, rows, [(column, row) used], (y0, y1) rows of the picture or None, ramps)
CELLS = {
    "q_spear": (2, 4, [(0, 0), (0, 1), (0, 2), (0, 3)], None, "gc"),
    "q_thrust": (4, 1, [(k, 0) for k in range(4)], (420, 700), "g"),
    "q_hit": (5, 1, [(k, 0) for k in range(5)], None, "g"),
    "q_low": (5, 1, [(k, 0) for k in range(5)], None, "gc"),
    "a_hit": (4, 1, [(k, 0) for k in range(4)], None, "g"),
    "p_ready": (5, 1, [(k, 0) for k in range(5)], None, "gf"),
    "w_hit": (5, 1, [(k, 0) for k in range(5)], None, "g"),
    "e_shield": (6, 1, [(k, 0) for k in range(6)], None, "gc"),
    "e_stab": (3, 1, [(k, 0) for k in range(3)], None, "g"),
    "e_bash": (5, 1, [(k, 0) for k in range(5)], None, "ge"),
    "e_hit": (4, 1, [(k, 0) for k in range(4)], None, "g"),
    "r_cast": (6, 1, [(k, 0) for k in range(6)], None, "gc"),
    "r_mark": (6, 1, [(k, 0) for k in range(6)], None, "g"),
    "r_spear": (5, 1, [(k, 0) for k in range(5)], None, "gf"),
    "r_sp_hit": (4, 1, [(k, 0) for k in range(4)], None, "f"),
    "r_land": (5, 1, [(k, 0) for k in range(5)], None, "fce"),
    "r_hit": (4, 1, [(k, 0) for k in range(4)], None, "f"),
    "r_slow": (4, 1, [(k, 0) for k in range(4)], (420, 700), "f"),
    "e_def": (4, 1, [(k, 0) for k in range(4)], None, "g"),
}
SQUASH = {"r_mark": 1 / 3}       # round rings seen from above -> ground ellipses
EDGE = 14                        # pixels off each cell's sides (the white lines between q_hit's and w_hit's cells, ~13 px)
# pictures whose frames are not equal cells: (x0, x1) of each frame used in the 2000-px picture. r_land: Codex drew
# frames 2-3 (the fireball rising) off-centre and overlapping their neighbours - mirrored they became two fires - so
# the flash, the blast (4), the smoke (5, 6) and the cracks (7) are used
XBOXES = {"r_land": [(100, 185), (745, 1115), (1115, 1425), (1425, 1740), (1740, 1975)]}
# the biggest frame's size in game px: ("w" | "h", n)
SIZE = {"q_spear": ("w", 30), "q_thrust": ("w", 48), "q_hit": ("w", 22), "q_low": ("w", 28), "a_hit": ("w", 14),
        "p_ready": ("h", 52), "w_hit": ("w", 26), "e_shield": ("w", 46), "e_stab": ("w", 10), "e_bash": ("w", 50),
        "e_hit": ("w", 20), "r_cast": ("h", 60), "r_mark": ("w", 2 * P["r_r"] // 1000), "r_spear": ("h", 72),
        "r_sp_hit": ("w", 18), "r_land": ("w", 72), "r_hit": ("w", 22), "r_slow": ("w", 18), "e_def": ("h", 50)}
SYM = {"q_spear": "tb", "q_thrust": "tb"}     # every other one "lr"
BIG = {"q_thrust", "e_shield", "e_bash", "r_cast", "r_mark", "r_spear", "r_land"}
THIN = {"q_spear", "q_thrust", "r_spear"}

HIT = (0, -14)                  # a hit on the upper body of a 34-46 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
# effect -> (anchor kind, frames with ms, spots)
FX = {
    # the comet spear: q_line 100000 at q_speed 4500 a tick, ~22 ticks
    "q_spear": ("core", flight(4, 60, P["q_line"] / P["q_speed"] * MS), [(0, 0)]),
    # the thrust's line lives q_thrust_t ticks (its picture turns with it: kept on the line's own row)
    "q_thrust": ("core", seq(range(4), [40, 50, 50, P["q_thrust_t"] * MS - 140]), [(0, 0)]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_low": ("core", seq(range(5), [40, 50, 70, 80, 90]), [HIT]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_ready": (("feet", 0), seq(range(5), [60, 70, 100, 100, 120]), [SOLES]),
    "w_hit": ("core", seq(range(5), [40, 50, 70, 80, 90]), [HIT]),
    # the shield's light for the whole channel (e_t ticks): the six frames looped
    "e_shield": (("feet", 4), seq([k % 6 for k in range(6)], [P["e_t"] * MS / 6] * 6), [SOLES]),
    "e_stab": ("core", seq(range(3), [30, 40, 50]), [HIT]),
    "e_bash": ("ring", seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the crouch: r_ch ticks
    "r_cast": (("feet", 0), seq(range(6), [P["r_ch"] * MS * f for f in (0.14, 0.16, 0.17, 0.18, 0.17, 0.18)]), [SOLES]),
    # the landing ring for the fall (r_fall ticks), on the ground of the landing point
    "r_mark": ("core", seq(range(6), [P["r_fall"] * MS / 6] * 6), [SOLES]),
    # the spear: falling over the first r_sp ticks (frames 1-2), in the ground on frame 3 when it strikes
    "r_spear": (("feet", 0), seq(range(5), [P["r_sp"] * MS / 2] * 2 + [110, 120, 140]), [SOLES]),
    "r_sp_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "r_land": ("ground", seq(range(5), [60, 120, 120, 130, 140]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # buffs (looped while they last)
    "r_slow": ("core", seq(range(4), [100] * 4), [SOLES]),
    "e_def": (("feet", 0), seq(range(4), [120] * 4), [SOLES]),
}


def key(rgb):
    """Black (or near-black JPEG noise) out; the white cell lines go with the cell edges (EDGE)."""
    mx, mn = rgb.max(-1), rgb.min(-1)
    a = (mx > 40) & ((mx - mn > 20) | (mn > 170))
    return np.where(a, 255, 0).astype(np.int16)


def strip(name):
    """The used cells of the picture side by side, keyed, as one RGBA sheet; the frames' boxes in it."""
    cols, rows, used, band, _ = CELLS[name]
    img = Image.open(lp(os.path.join(SRC, f"pantheon_fx_{name}.jpg"))).convert("RGB")
    if name in SQUASH:
        img = img.resize((img.width, max(1, round(img.height * SQUASH[name]))), Image.LANCZOS)
    im = np.asarray(img).astype(np.int16)
    if band:
        f = SQUASH.get(name, 1)
        im = im[int(band[0] * f):int(band[1] * f)]
    H, W = im.shape[:2]
    cw, ch = W // cols, H // rows
    pieces = []
    if name in XBOXES:
        cw = max(x1 - x0 for x0, x1 in XBOXES[name])
        for x0, x1 in XBOXES[name]:
            p = np.zeros((H, cw, 3), np.int16)
            p[:, (cw - (x1 - x0)) // 2:(cw - (x1 - x0)) // 2 + (x1 - x0)] = im[:, x0:x1]
            p[:3] = 0
            p[-3:] = 0
            pieces.append(p)
        used = []
    for c, r in used:
        p = im[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].copy()
        p[:, :EDGE] = 0
        p[:, -EDGE:] = 0
        p[:3] = 0
        p[-3:] = 0
        pieces.append(p)
    rgb = np.concatenate(pieces, 1)
    a = key(rgb)
    sheet = np.concatenate([rgb, a[..., None]], -1)
    n = len(pieces)
    return sheet, (1, ch - 1), [(k * cw + 2, (k + 1) * cw - 2) for k in range(n)]


KASSADIN_SHRINK = K.shrink


def thin_shrink(a, s):
    """import_kassadin's shrink, but a game pixel a fifth covered is drawn (not 45%): the spears' shafts and the
    thrust's streak are thinner than a game pixel in the screenshots."""
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
        K.shrink = thin_shrink if name in THIN else KASSADIN_SHRINK
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
        K.check(name, cs, sym)
        cells[name] = cs
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    cells = build_cells()
    tables = {"league_pantheon_fx": {}, "league_pantheon_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        if kind == "ring":
            anc = K.ring_anchor(cs)
        elif kind == "ground":      # the cracks' row (the last frame's lowest drawn rows) on the ground
            ys = np.nonzero(cs[-1][..., 3].any(1))[0]
            anc = [(cs[0].shape[1] - 1) / 2, int(np.median(ys))]
        else:
            anc = K.anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_pantheon_big" if name in BIG else "league_pantheon_fx"][name] = out
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
