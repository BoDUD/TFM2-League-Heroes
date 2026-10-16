#!/usr/bin/env python3
"""Import Dr. Mundo's effects (assets/source/drmundo/PROMPTS_FX.md, 20 pictures) as the game sheets league_drmundo_fx and
league_drmundo_big.

    python tools/art/import_drmundo_fx.py [--review out.png]

The source is the 20 pictures of Codex's step-3 run as the user forwarded them (JPEG screenshots, each 2000 px wide,
assets/source/drmundo/codex_fx/drmundo_fx_<name>.jpg; the user: 「这是特效 你完善一下然后倒入」), import_kalista_fx.py's
way: each picture a row of equal cells (CELLS), the background keyed out (KEY: black; Heart Zapper's shock drawn over a
grey figure and grey cell lines - neutral greys go; the healing pluses' white cell lines cut), one scale per effect (the
biggest frame's content to SIZE), every game pixel the commonest colour under it snapped to the prompt's ramps with the
bright cores kept (import_kassadin.shrink), then the red side's symmetry:
  * left to right about its own best axis (the fuller half mirrored) for everything on a unit, on him or on the ground;
  * none for the spinning saw (q_saw) and the tumbling corpse (e_fling): turned with their flight, either way up is right;
  * none for the tank on the ground (p_tank): a ground ViewEffect each 2-s link of the chain plays (a zone's own
    picture turns with it, the tank would stand on its head on the red side), never turned or mirrored.
The rings and flashes round him are sized to his 54 x 43 game px (the prompt's clear areas were for a 28-wide body).
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_drmundo.P, 60 ticks a second).
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
from build_drmundo import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "drmundo", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


# the prompt's ramps (pack_drmundo_fx.py)
CHEM = ["#F4FFE0", "#C8FF7A", "#8EE83C", "#4CB82A", "#237A2C", "#0F4220"]
ZAP = ["#FFFFFF", "#E0FDFF", "#8CEBFF", "#38C2F5", "#1C78C8", "#0F3A78"]
HOT = ["#FFFFFF", "#FFF4CF", "#FFD27A", "#FF9A3C", "#D85A20"]
STEEL = ["#F2FAFA", "#C4D8D8", "#8FA6AA", "#5C6E74", "#2E3A40"]
DUST = ["#F2E6CF", "#D6C3A0", "#B39B76", "#8A7255", "#5E4C39"]
PINK = ["#FFE0F2", "#FF7CC8", "#F0309A", "#A8166A"]
BODY = ["#B8A8C8", "#7A6890", "#4C3E60", "#2A2038"]
SAW = ["#E07A2A", "#A04A1C", "#6A3016", "#2FA8C0", "#1A6878"]          # the saw's rusty back and teal band (the design's)
DARKS = {(0x0F, 0x42, 0x20), (0x0F, 0x3A, 0x78), (0xD8, 0x5A, 0x20), (0x2E, 0x3A, 0x40), (0x5E, 0x4C, 0x39),
         (0xA8, 0x16, 0x6A), (0x2A, 0x20, 0x38)}
RAMPS = {"c": CHEM, "z": ZAP, "h": HOT, "hc": HOT + CHEM, "sc": STEEL + CHEM, "saw": STEEL + CHEM + SAW,
         "dc": DUST + CHEM, "dh": DUST + HOT, "cp": CHEM + PINK, "body": BODY + DUST + ["#FFFFFF"]}

# effect -> (columns, [columns used], (y0, y1) rows of the picture or None, ramps)
CELLS = {
    "q_saw": (4, range(4), None, "saw"),
    "q_hit": (5, range(5), None, "hc"),
    "q_heal": (4, range(4), None, "c"),
    "q_slow": (4, range(4), (430, 700), "c"),
    "a_hit": (4, range(4), None, "h"),
    "e_hit": (5, range(5), None, "hc"),
    "e_fling": (4, range(4), None, "body"),
    "e_fling_hit": (4, range(4), None, "dh"),
    "w_on": (4, range(4), None, "z"),
    "w_start": (4, range(4), None, "z"),
    "w_zap": (3, range(3), None, "z"),
    "w_burst": (5, range(5), None, "z"),
    "w_end_hit": (4, range(4), None, "z"),
    "r_cast": (6, range(6), None, "cp"),
    "r_on": (4, range(4), None, "cp"),
    "p_shake": (5, range(5), None, "sc"),
    "p_tank": (2, range(2), None, "sc"),
    "p_land": (4, range(4), None, "dc"),
    "p_pick": (4, range(4), None, "c"),
    "p_break": (4, range(4), None, "sc"),
}
# keep neutral greys (steel, glass, shards) only in these; the others keep coloured or near-white pixels
METAL = {"q_saw", "p_tank", "p_shake", "p_break"}
CUT_LINES = {"q_heal": 8}            # px cleared round the cell borders (Codex's white cell lines)
# the biggest frame's size in game px: ("w" | "h", n)
SIZE = {"q_saw": ("w", 20), "q_hit": ("w", 20), "q_heal": ("w", 40), "q_slow": ("w", 20), "a_hit": ("w", 14),
        "e_hit": ("w", 24), "e_fling": ("w", 16), "e_fling_hit": ("w", 18), "w_on": ("w", 56), "w_start": ("w", 40),
        "w_zap": ("h", 20), "w_burst": ("w", 60), "w_end_hit": ("w", 22), "r_cast": ("w", 52), "r_on": ("w", 40),
        "p_shake": ("w", 44), "p_tank": ("w", 12), "p_land": ("w", 20), "p_pick": ("h", 26), "p_break": ("w", 20)}
FREE = {"q_saw", "e_fling", "p_tank"}  # no symmetry: the saw and the corpse spin, the tank lies on the ground
HALF = set()                          # half-turn symmetry (none now)
BIG = {"w_on", "w_start", "w_burst", "r_cast"}

HIT = (0, -14)                  # a hit on the upper body of a 34-42 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
MS = 1000 / 60
W_PER_MS = P["w_per"] * MS
# effect -> (anchor kind, frames with ms, spots)
FX = {
    # the saw: (q_range + 10000) at q_speed a tick, in a straight line
    "q_saw": ("core", flight(4, 50, (P["q_range"] + 10000) / P["q_speed"] * MS), [(0, 0)]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_heal": (("feet", 0), seq(range(4), [70, 80, 90, 100]), [SOLES]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "e_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # the corpse: e_fling_l at e_fling_v a tick
    "e_fling": ("core", flight(4, 60, P["e_fling_l"] / P["e_fling_v"] * MS), [(0, 0)]),
    "e_fling_hit": ("core", seq(range(4), [50, 60, 70, 80]), [HIT]),
    "w_start": (("feet", 0), seq(range(4), [40, 50, 60, 80]), [SOLES]),
    # one zap a pulse (w_per ticks): its 3 frames inside it
    "w_zap": (("feet", 0), seq(range(3), [W_PER_MS / 3] * 3), [SOLES]),
    "w_burst": (("feet", 0), seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "w_end_hit": ("core", seq(range(4), [40, 50, 60, 80]), [HIT]),
    "r_cast": (("feet", 0), seq(range(6), [60, 70, 80, 90, 100, 110]), [SOLES]),
    "p_shake": (("feet", 0), seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "p_land": ("ring", seq(range(4), [50, 60, 80, 100]), [SOLES]),
    "p_pick": (("feet", 0), seq(range(4), [60, 70, 80, 100]), [SOLES]),
    "p_break": ("ring", seq(range(4), [50, 60, 80, 100]), [SOLES]),
    # the tank on the ground, played by each link of the chain (p_link ticks): its two frames in turn
    "p_tank": (("feet", 1), seq([0, 1] * 4, [P["p_link"] * MS / 8] * 8), [SOLES]),
    # buffs (looped while they last)
    "q_slow": ("core", seq(range(4), [100] * 4), [SOLES]),
    "w_on": (("feet", 0), seq(range(4), [80] * 4), [SOLES]),
    "r_on": (("feet", 0), seq(range(4), [150] * 4), [SOLES]),
}


def key(rgb, metal):
    mx, mn = rgb.max(-1), rgb.min(-1)
    a = mx > 40
    if not metal:
        a &= (mx - mn > 20) | (mn > 190)
    return np.where(a, 255, 0).astype(np.int16)


def strip(name):
    """The used cells of the picture side by side, keyed, as one RGBA sheet; the frames' boxes in it."""
    cols, used, band, _ = CELLS[name]
    im = np.asarray(Image.open(lp(os.path.join(SRC, f"drmundo_fx_{name}.jpg"))).convert("RGB")).astype(np.int16)
    if band:
        im = im[band[0]:band[1]]
    H, W = im.shape[:2]
    cw = W // cols
    pieces = [im[:, c * cw:(c + 1) * cw].copy() for c in used]
    cut = CUT_LINES.get(name, 0)
    for p in pieces:
        if cut:
            p[:, :cut] = 0
            p[:, -cut:] = 0
    rgb = np.concatenate(pieces, 1)
    a = key(rgb, name in METAL)
    sheet = np.concatenate([rgb, a[..., None]], -1)
    return sheet, (1, H - 1), [(k * cw + 2, (k + 1) * cw - 2) for k in range(len(pieces))]


def use_ramps(names):
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in names]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS


def free_frames(name, sheet, band, boxes):
    """The spinning pictures and the tank: scaled like the others, no mirroring, every frame on one centred cell."""
    crops = [K.crop(sheet, band, xr) for xr in boxes]
    dim, target = SIZE[name]
    ext = []
    for a, _ in crops:
        ys, xs = np.nonzero(a[..., 3] > 40)
        ext.append((xs.max() - xs.min() + 1) if dim == "w" else (ys.max() - ys.min() + 1))
    s = target / max(ext)
    out = []
    for a, _ in crops:
        if name in HALF:
            a = a.copy()
            r, g, b = (a[..., i].astype(int) for i in range(3))
            ring = (g > r + 30) & (g < 140) & (b < 90)          # the dark green ground ring under the tank
            ys = np.nonzero((a[..., 3] > 40).any(1))[0]
            a[ring & (np.arange(a.shape[0])[:, None] > (ys.min() + ys.max()) / 2)] = 0
        g_ = K.shrink(a, s)
        ys, xs = np.nonzero(g_[..., 3] > 0)
        g_ = g_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        out.append(K.despeckle(g_))
    H = max(f.shape[0] for f in out)
    W = max(f.shape[1] for f in out)
    H += (H + 1) % 2
    W += (W + 1) % 2
    cells = []
    for f in out:
        c = np.zeros((H, W, 4), np.uint8)
        y, x = (H - f.shape[0]) // 2, (W - f.shape[1]) // 2
        c[y:y + f.shape[0], x:x + f.shape[1]] = f
        cells.append(half_turn(c) if name in HALF else c)
    return cells


def half_turn(c):
    """The cell (odd sizes) made the same turned 180 degrees about its middle: its left half and that half turned onto
    the right; the middle column's upper half turned onto its lower half."""
    h, w = c.shape[:2]
    m = w // 2
    out = np.zeros_like(c)
    out[:, :m] = c[:, :m]
    out[:, m + 1:] = c[::-1, :m][:, ::-1]
    for y in range(h):
        out[y, m] = c[y, m] if y <= h // 2 else c[h - 1 - y, m]
    return out


def build_cells():
    cells = {}
    for name in CELLS:
        sheet, band, boxes = strip(name)
        use_ramps(RAMPS[CELLS[name][3]])
        if name in FREE | HALF:
            cs = free_frames(name, sheet, band, boxes)
            if name in HALF:
                for k, c in enumerate(cs):
                    if not (c == c[::-1, ::-1]).all():
                        sys.exit(f"drmundo_fx_{name} cell {k + 1} is not the same turned half round")
            cells[name] = cs
            continue
        K.BOXES = {name: (name, band, boxes)}
        K.SIZE, K.SYM, K.AXIS = SIZE, {}, {}
        frames, s, _ = K.frames_of(name, {name: sheet})
        cs = K.common_cell(frames, "lr", None, s, band)
        cs, _ = K.trim_rows(cs)
        K.check(name, cs, "lr")
        cells[name] = cs
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    cells = build_cells()
    tables = {"league_drmundo_fx": {}, "league_drmundo_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        anc = K.ring_anchor(cs) if kind == "ring" and len(cs) >= 4 else K.anchor(cs[0], "core" if kind == "ring" else kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_drmundo_big" if name in BIG else "league_drmundo_fx"][name] = out
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
