#!/usr/bin/env python3
"""Import Galio's effects (assets/source/galio/PROMPTS_FX.md, 17 pictures) as the game sheets league_galio_fx and
league_galio_big.

    python tools/art/import_galio.py [--review out.png]

Codex's delivery reached us as one overview picture only (assets/source/galio/codex_fx/galio_fx_overview.jpg, pasted by
the user: every effect labelled, drawn on a dark ground, lossy JPEG, mostly one to three frames each), no game-size
copies - Braum's and Kassadin's case, so tools/art/import_kassadin.py's way and its functions: the ground keyed out
(squares far from its colour), each drawn frame cut from its box, one scale per effect, every game pixel the commonest
colour under it snapped to the prompt's ramps (wind, blue magic, gold, dust, plus the rocks' browns) with the bright
cores kept, the red side's symmetry (q_wind top to bottom, everything else left to right about its own best axis,
checked square for square). The person-shaped silhouette Codex drew inside w_ps is cleared first (the prompt wanted the
middle empty). Where fewer frames were drawn than the effect needs, the rest are made from them (SEQ): grown in from the
first drawn frame (scaled about the anchor), cycled, faded out (the darker squares thinned first, then all but the
brightest), and the tornado's spin as its colours rolled up inside its own outline.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_galio.P, 60 ticks a second).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import import_kassadin as K  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "galio", "codex_fx")
MOD = os.path.join(ROOT, "league")
OVERVIEW = "galio_fx_overview.jpg"

# the prompt's ramps (pack_galio_fx.py) and the rocks Codex drew
WIND = ["#FFFFFF", "#E8FBFF", "#BDEFFF", "#7FD6F2", "#3FA9D6", "#2A7FA8", "#1F5E7A"]   # + two deep teals: the streaks
MAGIC = ["#D6ECFF", "#8CC4FF", "#4A8EF0", "#2457C9", "#142F80"]
GOLD = ["#FFF8D6", "#FFE27A", "#F5BE3C", "#C98A1E", "#8A5A12"]
DUST = ["#F2EEE4", "#D6CDBB", "#B3A68E", "#8A7D66"]
ROCK = ["#6E5A44", "#4A3A2C", "#2E241C"]
DARKS = {(0x14, 0x2F, 0x80), (0x2E, 0x24, 0x1C), (0x4A, 0x3A, 0x2C)}
KEY = 40                                  # a square this far from the ground's colour (max channel) is drawn
SILHOUETTE = (90, 255, 1722, 1836)        # the figure Codex drew inside w_ps (rows, columns): cleared
# thin lines thickened by n sheet px before the shrink (their colour from the nearest drawn px): the windblasts' crescents
# broke into specks at 30 game px
THICKEN = {"q_wind": 3}

# effect -> (sheet, (y0, y1) band, [(x0, x1) per drawn frame])
BOXES = {
    "a_hit": (1, (44, 176), [(30, 120), (130, 245), (255, 360), (370, 480)]),
    "a_dust": (1, (178, 270), [(30, 120), (130, 245), (255, 360), (370, 480)]),
    "p_hit": (1, (40, 285), [(505, 750), (752, 990)]),
    "p_ring": (1, (88, 256), [(1020, 1540)]),
    "w_ps": (1, (40, 292), [(1580, 1975)]),
    "q_wind": (1, (340, 585), [(25, 475)]),
    "q_burst": (1, (325, 590), [(520, 975)]),
    "q_tornado": (1, (338, 590), [(1108, 1395)]),
    "q_hit": (1, (350, 576), [(1512, 1735), (1745, 1970)]),
    "e_dash": (1, (690, 850), [(25, 715)]),
    "e_hit": (1, (636, 885), [(780, 1000), (1001, 1196), (1198, 1400)]),
    "w_charge": (1, (934, 1178), [(55, 455)]),
    "w_burst": (1, (954, 1186), [(700, 1302)]),
    "r_cast": (1, (944, 1176), [(1370, 1560), (1582, 1772), (1792, 1980)]),
    "r_land": (1, (1236, 1492), [(22, 635)]),
    "r_hit": (1, (1238, 1475), [(740, 990)]),
    "w_taunt": (1, (1284, 1393), [(1118, 1258)]),
    "r_shield": (1, (1256, 1458), [(1366, 1570), (1586, 1774), (1796, 1977)]),
}
# the biggest frame's size in game px: ("w" | "h", n) - the prompt's sizes, a little over for the small hits
SIZE = {"a_hit": ("w", 16), "a_dust": ("w", 14), "p_hit": ("w", 20), "p_ring": ("w", 34), "w_ps": ("w", 40), "q_wind": ("w", 30),
        "q_burst": ("w", 30), "q_tornado": ("h", 36), "q_hit": ("w", 16), "e_dash": ("w", 30), "e_hit": ("h", 24),
        "w_charge": ("w", 44), "w_burst": ("w", 52), "r_cast": ("h", 50), "r_land": ("w", 46), "r_hit": ("h", 24),
        "w_taunt": ("w", 14), "r_shield": ("w", 22)}
SYM = {"q_wind": "tb"}                    # every other one "lr"

HIT = (0, -12)                            # a hit on the upper body of a 36-44 px unit
OVER = (0, -34)                           # over a unit's head
SOLES = (0, 11)                           # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight

# the frames each effect plays, made from the drawn cells: ("cell", i) | ("grow", i, k) | ("fade", i, level) |
# ("roll", i, rows) - with their ms
G_, F_, C_, R_ = "grow", "fade", "cell", "roll"
SEQ = {
    "a_hit": [((C_, 0), 40), ((C_, 1), 50), ((C_, 2), 60), ((C_, 3), 70)],      # + a_dust's frames 2-3 under 3-4
    "p_hit": [((F_, 0, 2), 40), ((C_, 0), 50), ((C_, 1), 70), ((F_, 1, 1), 80), ((F_, 1, 2), 90)],
    "p_ring": [((G_, 0, 0.35), 40), ((G_, 0, 0.65), 50), ((C_, 0), 60), ((F_, 0, 1), 70), ((F_, 0, 2), 80)],
    "w_ps": [((F_, 0, 1), 60), ((C_, 0), 80), ((C_, 0), 100), ((F_, 0, 1), 80), ((F_, 0, 2), 80)],
    "q_burst": [((G_, 0, 0.45), 40), ((G_, 0, 0.75), 50), ((C_, 0), 60), ((F_, 0, 1), 70), ((F_, 0, 2), 80)],
    # the tornado's 2 s (q_t 120 ticks): rising, spinning (its colours rolled up its own shape), breaking up
    "q_tornado": [((G_, 0, 0.6), 150), ((C_, 0), 270), ((R_, 0, 2), 270), ((R_, 0, 4), 270), ((C_, 0), 270),
                  ((R_, 0, 2), 270), ((R_, 0, 4), 270), ((F_, 0, 1), 230)],
    "q_hit": [((F_, 0, 2), 40), ((C_, 0), 50), ((C_, 1), 60), ((F_, 1, 1), 70)],
    "e_dash": [((G_, 0, 0.5), 40), ((G_, 0, 0.8), 60), ((C_, 0), 70), ((F_, 0, 1), 80)],
    "e_hit": [((C_, 0), 40), ((C_, 1), 50), ((C_, 2), 60), ((F_, 2, 1), 80), ((F_, 2, 2), 90)],
    # the brace's 50 ticks (833 ms)
    "w_charge": [((G_, 0, 0.9), 100), ((C_, 0), 245), ((F_, 0, 0), 245), ((C_, 0), 245)],
    "w_burst": [((G_, 0, 0.35), 40), ((G_, 0, 0.65), 50), ((C_, 0), 60), ((F_, 0, 1), 80), ((F_, 0, 2), 90)],
    # the channel's 120 ticks (2 s)
    "r_cast": [((C_, 0), 333), ((C_, 1), 333), ((C_, 2), 333), ((C_, 0), 333), ((C_, 1), 333), ((C_, 2), 335)],
    "r_land": [((G_, 0, 0.35), 40), ((G_, 0, 0.65), 50), ((C_, 0), 60), ((F_, 0, 1), 70), ((F_, 0, 2), 80),
               ((F_, 0, 3), 90)],
    "r_hit": [((F_, 0, 2), 40), ((C_, 0), 50), ((F_, 0, 1), 60), ((F_, 0, 2), 70)],
    "w_taunt": [((C_, 0), 150), ((F_, 0, 0), 150)],
    "r_shield": [((C_, 0), 150), ((C_, 1), 150), ((C_, 2), 150)],
}
# effect -> (anchor kind, spots); q_wind flies the lob's q_fly 24 ticks (400 ms)
WHERE = {"a_hit": ("core", [HIT]), "p_hit": ("core", [HIT]), "p_ring": ("core", [SOLES]),
         "w_ps": (("feet", 0), [SOLES]), "q_burst": (("feet", 4), [SOLES]), "q_tornado": (("feet", 0), [SOLES]),
         "q_hit": ("core", [HIT]), "e_dash": (("feet", 2), [SOLES]), "e_hit": ("core", [HIT]),
         "w_charge": (("feet", 0), [SOLES]), "w_burst": (("feet", 5), [SOLES]), "r_cast": (("feet", 3), [SOLES]),
         "r_land": (("feet", 6), [SOLES]), "r_hit": ("core", [HIT]), "w_taunt": ("core", [OVER]),
         "r_shield": (("feet", 0), [SOLES])}
BIG = {"p_ring", "q_burst", "q_tornado", "w_charge", "w_burst", "r_land"}


def load_overview():
    a = np.asarray(Image.open(os.path.join(SRC, OVERVIEW)).convert("RGB")).astype(np.int16)
    bg = np.median(a.reshape(-1, 3), axis=0)
    alpha = np.where(np.abs(a - bg).max(2) > KEY, 255, 0).astype(np.int16)
    y0, y1, x0, x1 = SILHOUETTE
    alpha[y0:y1, x0:x1] = 0
    sheet = np.dstack([a, alpha])
    from scipy import ndimage
    for name, it in THICKEN.items():
        _, (y0, y1), boxes = BOXES[name]
        for x0, x1 in boxes:
            reg = sheet[y0:y1, x0:x1]
            m = reg[..., 3] > 0
            grown = ndimage.binary_dilation(m, iterations=it) & ~m
            iy, ix = ndimage.distance_transform_edt(~m, return_distances=False, return_indices=True)
            reg[grown, :3] = reg[iy[grown], ix[grown], :3]
            reg[grown, 3] = 255
    return sheet


def use_galio(sheet):
    """import_kassadin's functions read their module's tables: point them at Galio's."""
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in WIND + MAGIC + GOLD + DUST + ROCK]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS
    K.BOXES, K.SIZE, K.SYM, K.AXIS = BOXES, SIZE, SYM, {}
    K.load = lambda n: sheet


def anchor_of(cell, kind):
    return K.anchor(cell, kind)


def grow(cell, k, kind):
    """The cell scaled by k about its anchor (nearest), on the same canvas, symmetric again."""
    h, w = cell.shape[:2]
    ax, ay = anchor_of(cell, kind)
    nh, nw = max(1, round(h * k)), max(1, round(w * k))
    small = np.asarray(Image.fromarray(cell).resize((nw, nh), Image.NEAREST))
    out = np.zeros_like(cell)
    x0 = int(round(ax - (nw - 1) / 2))
    y0 = int(round(ay - ay * k))
    ys, xs = slice(max(0, y0), min(h, y0 + nh)), slice(max(0, x0), min(w, x0 + nw))
    out[ys, xs] = small[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    if (cell == cell[:, ::-1]).all():
        out = np.where(out[..., 3:] > 0, out, out[:, ::-1])
        out = np.where((out == out[:, ::-1]).all(-1, keepdims=True), out, 0)
    return out


def fade(cell, level):
    """level 0: one step dimmer (every colour to the next darker of its ramp); 1: the darker squares thinned on a
    checker; 2: only the brightest third left, thinned; 3: only the brightest, sparse."""
    out = cell.copy()
    op = out[..., 3] > 0
    lum = out[..., :3].astype(float) @ np.array([0.3, 0.59, 0.11])
    yy, xx = np.mgrid[0:out.shape[0], 0:out.shape[1]]
    if level == 0:
        ramps = [WIND, MAGIC, GOLD, DUST, ROCK]
        cols = [[tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in r] for r in ramps]
        for y, x in zip(*np.nonzero(op)):
            c = tuple(int(v) for v in out[y, x, :3])
            for r in cols:
                if c in r and r.index(c) + 1 < len(r):
                    out[y, x, :3] = r[r.index(c) + 1]
                    break
        return out
    lit = lum[op]
    if not len(lit):
        return out
    cut = {1: np.percentile(lit, 40), 2: np.percentile(lit, 66), 3: np.percentile(lit, 85)}[level]
    checker = ((yy + xx) % 2 == 0) if level == 1 else ((yy % 2 == 0) & (xx % 2 == 0)) if level == 2 else \
        ((yy % 3 == 0) & (xx % 3 == 0))
    drop = op & ((lum < cut) | ((level >= 2) & ~checker))
    if level == 1:
        drop = op & (lum < cut) & checker
    out[drop] = 0
    # keep the left-right symmetry: a square stays only where its mirror stays
    if (cell == cell[:, ::-1]).all():
        keep = out[..., 3] > 0
        out[~(keep & keep[:, ::-1])] = 0
    return out


def roll(cell, rows):
    """The colours moved `rows` up inside the cell's own shape (the spin of a funnel), the outline shape unchanged."""
    out = cell.copy()
    op = cell[..., 3] > 0
    for x in range(cell.shape[1]):
        ys = np.nonzero(op[:, x])[0]
        if len(ys) < 2:
            continue
        colours = cell[ys, x].copy()
        out[ys, x] = np.roll(colours, -rows, axis=0)
    return out


def make(name, cells, kind):
    frames = []
    for spec, ms in SEQ[name]:
        op, i = spec[0], spec[1]
        c = cells[i]
        if op == C_:
            f = c
        elif op == G_:
            f = grow(c, spec[2], kind)
        elif op == F_:
            f = fade(c, spec[2])
        else:
            f = roll(c, spec[2])
        frames.append((f, ms))
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size frames at 6x here")
    a = ap.parse_args()
    sheet = load_overview()
    use_galio(sheet)
    cells = K.build_cells({1: sheet})
    tables = {"league_galio_fx": {}, "league_galio_big": {}}
    played = {}
    # a_hit: Codex drew the dust ring as a row of its own under the stars: frames 3-4 take its frames 2-3, same middle
    stars, dust = cells["a_hit"], cells["a_dust"]
    H = max(c.shape[0] for c in stars + dust)
    W = max(c.shape[1] for c in stars + dust)
    H += 1 - H % 2
    W += 1 - W % 2

    def mid(c):
        out = np.zeros((H, W, 4), np.uint8)
        y, x = (H - c.shape[0]) // 2, (W - c.shape[1]) // 2
        out[y:y + c.shape[0], x:x + c.shape[1]] = c
        return out
    merged = [mid(c) for c in stars]
    for k, d in ((2, 1), (3, 2)):
        under = mid(dust[d])
        m = (merged[k][..., 3] == 0) & (under[..., 3] > 0)
        merged[k][m] = under[m]
    cells["a_hit"] = merged
    for name in BOXES:
        if name == "a_dust":
            continue
        cs = cells[name]
        if name == "q_wind":
            anc = K.anchor(cs[0], "core")
            out = [(np.zeros((3, 3, 4), np.uint8), ms) if k == EMPTY else (J.place(cs[k], anc, [(0, 0)]), ms)
                   for k, ms in flight(len(cs), 80, 450)]
            tables["league_galio_fx"][name] = out
            played[name] = [cs[k] for k, _ in flight(len(cs), 80, 450) if k != EMPTY][:1]
            continue
        kind, spots = WHERE[name]
        anc = K.anchor(cs[0], kind)
        frames = make(name, cs, kind)
        out = [(J.place(f, anc, spots), ms) for f, ms in frames]
        for f, _ in frames:
            if not (f == f[:, ::-1]).all():
                sys.exit(f"galio_fx_{name}: a made frame is not symmetric left to right")
        tables["league_galio_big" if name in BIG else "league_galio_fx"][name] = out
        played[name] = [f for f, _ in frames]
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name, fs in played.items():
            fs = [f for f in fs if f is not None and f.shape[0] > 3]
            W = sum(f.shape[1] + 2 for f in fs)
            H = max(f.shape[0] for f in fs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for f in fs:
                img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - f.shape[0]) * Z))
                x += f.shape[1] + 2
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
