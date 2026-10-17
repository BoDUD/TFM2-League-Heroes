#!/usr/bin/env python3
"""Import Nidalee's effects (assets/source/nidalee/PROMPTS_FX.md, 24 pictures) as the game sheets league_nidalee_fx and
league_nidalee_big.

    python tools/art/import_nidalee.py [--review out.png]

Codex delivered every effect as its own image (assets/source/nidalee/codex_fx/raw/nidalee_fx_<name>.png: one row of
frames, soft alpha) plus its own game-size read-back (pixel_1x/), which came out too coarse - the leaves,
rings and claw arcs of the drafts turned into flat blobs (e_as, brush, hunt). So the drafts are read again
tools/art/import_kassadin.py's way (as import_braum.py does): each frame cut from its cell, one scale per effect, every
game pixel the commonest colour under it snapped to the prompt's ramps with the bright cores kept, the red side's
symmetry - the javelins top to bottom, everything else left to right about its own best axis - checked square for
square. Here only the cells, the sizes, the ramps and the timings are Nidalee's.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_nidalee.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "nidalee", "codex_fx", "raw")
MOD = os.path.join(ROOT, "league")

# the prompt's ramps (pack_nidalee_fx.py)
GOLD = ["#FFFFFF", "#FFF4C2", "#FFD966", "#F2A93B", "#C9701E", "#7A3E12"]
GREEN = ["#E8FFD6", "#A8F07A", "#5CC84A", "#2E8B3A", "#145A2A"]
EARTH = ["#F2E6CF", "#D6C3A0", "#B39B76", "#8A7255", "#5E4C39"]
WOOD = ["#E9C79A", "#C58C4E", "#9A5E2C", "#6B3A1A", "#3A1E0E"]
STONE = ["#E4E6EE", "#B9BCC9", "#8C8FA0"]
DARKS = {(0x7A, 0x3E, 0x12), (0x14, 0x5A, 0x2A), (0x5E, 0x4C, 0x39), (0x3A, 0x1E, 0x0E)}

# effect -> frames in its row (each draft one row of equal cells)
FRAMES = {"a_spear": 2, "q_spear": 4, "a_hit": 4, "q_hit": 5, "hunted": 4, "hunt": 4, "e_heal": 6, "e_as": 4,
          "w_lob": 2, "w_trap": 8, "w_snap": 5, "c_hit": 4, "cq_arm": 4, "cq_hit": 5, "cw_dust": 4, "cw_land": 5,
          "cw_hit": 4, "ce_swipe": 5, "ce_hit": 3, "tf_cougar": 6, "tf_human": 6, "r_roar": 5, "r_hit": 5, "brush": 4}
# the biggest frame's size in game px: ("w" | "h", n) - a little over the prompt's sizes for the small ones
SIZE = {"a_spear": ("w", 18), "q_spear": ("w", 26), "a_hit": ("w", 12), "q_hit": ("w", 22), "hunted": ("w", 11),
        "hunt": ("w", 20), "e_heal": ("h", 30), "e_as": ("w", 18), "w_lob": ("w", 9), "w_trap": ("w", 20),
        "w_snap": ("w", 18), "c_hit": ("w", 14), "cq_arm": ("w", 26), "cq_hit": ("w", 22), "cw_dust": ("w", 32),
        "cw_land": ("w", 34), "cw_hit": ("w", 15), "ce_swipe": ("w", 46), "ce_hit": ("w", 13), "tf_cougar": ("h", 46),
        "tf_human": ("w", 52), "r_roar": ("w", 42), "r_hit": ("w", 24), "brush": ("w", 15)}
SYM = {"a_spear": "tb", "q_spear": "tb"}           # every other one "lr"

HIT = (0, -14)                  # a hit on the upper body of a 42 px unit
OVER = (0, -38)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
# effect -> (anchor kind, frames with ms, spots)
FX = {
    # the attack's javelin: a_speed 5000 a tick over her 50000 reach, ~10 ticks
    "a_spear": ("core", flight(2, 60, 360), [(0, 0)]),
    # Javelin Toss: q_speed 3000 a tick over 95000, ~32 ticks
    "q_spear": ("core", flight(4, 60, 600), [(0, 0)]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "hunted": ("core", seq(range(4), [110] * 4), [OVER]),
    "hunt": ("core", seq(range(4), [100] * 4), [SOLES]),
    "e_heal": (("feet", 0), seq(range(6), [60, 70, 80, 90, 90, 90]), [SOLES]),
    "e_as": ("core", seq(range(4), [110] * 4), [SOLES]),
    # the snare's lob: w_fly 16 ticks
    "w_lob": ("core", flight(2, 80, 300, lead=0), [(0, 0)]),
    # the snare on the ground for w_life 240 ticks (4 s): frame 4 held
    "w_trap": ("core", seq(range(8), [80, 80, 100, 3200, 150, 150, 120, 120]), [SOLES]),
    "w_snap": (("feet", 2), seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "c_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "cq_arm": (("feet", 0), seq(range(4), [60, 70, 80, 90]), [SOLES]),
    "cq_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "cw_dust": ("core", seq(range(4), [40, 60, 70, 80]), [SOLES]),
    "cw_land": ("core", seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "cw_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "ce_swipe": (("feet", 1), seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "ce_hit": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    # the turns: tf_dur 16 ticks (270 ms) under the burst, its tail after
    "tf_cougar": (("feet", 0), seq(range(6), [50, 50, 80, 80, 80, 90]), [SOLES]),
    "tf_human": (("feet", 0), seq(range(6), [50, 50, 80, 80, 80, 90]), [SOLES]),
    "r_roar": (("feet", 1), seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "brush": ("core", seq(range(4), [120] * 4), [SOLES]),
}
BIG = {"cw_land", "ce_swipe", "tf_cougar", "tf_human", "r_roar"}


def frame_runs(alpha, n):
    """The n frames' column ranges in a draft: Codex's cells are not all the same width (equal cells cut slivers of the
    next frame in), and one frame can be two pieces apart (a pair of wisps), so a gap is no frame boundary either: each
    boundary of the equal cells moves to the emptiest column within a sixth of a cell of it."""
    cols = (alpha > 40).sum(0)
    W = len(cols)
    cw = W / n
    bounds = [0]
    for k in range(1, n):
        c = int(round(k * cw))
        r = max(2, int(cw / 6))
        lo, hi = max(1, c - r), min(W - 1, c + r)
        seg = cols[lo:hi + 1]
        best = np.nonzero(seg == seg.min())[0]
        bounds.append(lo + int(best[np.argmin(np.abs(best + lo - c))]))
    bounds.append(W)
    return [(bounds[k], bounds[k + 1]) for k in range(n)]


def boxes():
    """effect -> (sheet id, (y0, y1) band, [(x0, x1) per frame]): the draft's full height, its frames' boundaries on the emptiest columns."""
    out, sheets = {}, {}
    for i, name in enumerate(FRAMES, 1):
        path = os.path.join(SRC, f"nidalee_fx_{name}.png")
        a = np.asarray(Image.open(path).convert("RGBA"))
        sheets[i] = f"nidalee_fx_{name}.png"
        out[name] = (i, (0, a.shape[0]), frame_runs(a[..., 3], FRAMES[name]))
    return out, sheets


def shaft(c):
    """The attack's javelin: its wooden shaft is thinner than half a game pixel in the draft and the vote cleared it
    between the tail light and the blade - the middle row filled there in the wood ramp's middle colour (the cell is
    an odd number of rows tall, so it stays top-bottom symmetric)."""
    c = c.copy()
    mid = c.shape[0] // 2
    xs = np.nonzero(c[:, :, 3].any(0))[0]
    filled = np.nonzero(c[mid, :, 3])[0]
    if len(filled):
        gap = [x for x in range(xs.min(), xs.max() + 1) if c[mid, x, 3] == 0]
        wood = tuple(int(WOOD[2][i:i + 2], 16) for i in (1, 3, 5))
        for x in gap:
            c[mid, x] = (*wood, 255)
    return c


def use_nidalee():
    """import_kassadin's functions read their module's tables: point them at Nidalee's."""
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in GOLD + GREEN + EARTH + WOOD + STONE]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS
    b, sheets = boxes()
    K.BOXES, K.SIZE, K.SYM, K.AXIS = b, SIZE, SYM, {}
    K.SRC, K.SHEETS = SRC, sheets
    return sheets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    sheets_ids = use_nidalee()
    sheets = {n: K.load(n) for n in sheets_ids}
    cells = K.build_cells(sheets)
    cells["a_spear"] = [shaft(c) for c in cells["a_spear"]]
    tables = {"league_nidalee_fx": {}, "league_nidalee_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        anc = K.anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_nidalee_big" if name in BIG else "league_nidalee_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
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
