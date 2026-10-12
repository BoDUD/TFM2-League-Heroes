#!/usr/bin/env python3
"""Import Braum's effects (assets/source/braum/PROMPTS_FX.md, 18 pictures) as the game sheets league_braum_fx and
league_braum_big.

    python tools/art/import_braum.py [--review out.png]

Codex's delivery reached us as two overview sheets only (assets/source/braum/codex_fx/braum_fx_sheet1.webp and
sheet2.webp, pasted by the user: every effect a row of its frames, each row at its own scale, soft alpha, lossy WebP),
no game-size copies - Kassadin's case, so tools/art/import_kassadin.py's way and its functions (cut each frame from its
box, one scale per effect, every game pixel the commonest colour under it snapped to the prompt's ramps with the bright
cores kept, the red side's symmetry: q_ice and r_wave top to bottom, everything else left to right about its own best
axis, checked square for square). Here only the boxes, the sizes, the ramps and the timings are Braum's.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_braum.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "braum", "codex_fx")
MOD = os.path.join(ROOT, "league")
SHEETS = {1: "braum_fx_sheet1.webp", 2: "braum_fx_sheet2.webp"}

# the prompt's ramps (pack_braum_fx.py)
ICE = ["#FFFFFF", "#DFF8FF", "#9EE6FF", "#4FC3F7", "#1E88E5", "#0D47A1"]
FROST = ["#EEF7FF", "#CFE6F5", "#A5C8E1", "#7FA6C6"]
GOLD = ["#FFF6C8", "#FFE07A", "#F2B83C", "#B98322"]
DARKS = {(0x0D, 0x47, 0xA1)}

# effect -> (sheet, (y0, y1) band, [(x0, x1) per frame])
BOXES = {
    "a_hit": (2, (15, 172), [(78, 182), (238, 342), (377, 577), (610, 768)]),
    "p_mark": (2, (187, 272), [(101, 197), (277, 380), (459, 564), (648, 744)]),
    "p_stun": (2, (298, 371), [(95, 226), (276, 407), (449, 574), (616, 749)]),
    "p_proc": (2, (392, 561), [(48, 133), (182, 319), (352, 474), (492, 659), (685, 808)]),
    "p_extra": (2, (576, 628), [(128, 181), (265, 322), (406, 442)]),
    "q_ice": (2, (653, 718), [(15, 224), (252, 398), (412, 580), (603, 803)]),
    "q_hit": (2, (740, 876), [(50, 160), (184, 307), (327, 480), (495, 656), (675, 793)]),
    "q_slow": (2, (886, 957), [(38, 177), (192, 334), (354, 495), (521, 664), (677, 806)]),
    "e_raise": (2, (976, 1114), [(15, 162), (168, 348), (355, 516), (524, 680), (688, 830)]),
    "e_on": (1, (6, 188), [(40, 205), (230, 405), (425, 615), (635, 805)]),
    "e_ally": (1, (197, 279), [(65, 175), (265, 372), (458, 579), (674, 781)]),
    "w_dash": (1, (299, 391), [(50, 176), (233, 383), (418, 614), (644, 810)]),
    "w_land": (1, (411, 518), [(21, 172), (181, 325), (334, 499), (507, 668), (675, 825)]),
    "w_guard": (1, (526, 620), [(62, 203), (253, 395), (448, 596), (644, 786)]),
    "r_slam": (1, (634, 763), [(10, 132), (140, 270), (272, 421), (430, 576), (586, 703), (717, 825)]),
    "r_wave": (1, (778, 902), [(15, 216), (227, 410), (428, 614), (636, 831)]),
    "r_crack": (1, (923, 983), [(10, 91), (101, 197), (206, 311), (318, 423), (430, 529), (537, 635), (644, 732),
                                (748, 833)]),
    "r_hit": (1, (991, 1112), [(66, 191), (246, 398), (436, 580), (637, 756)]),
}
# the biggest frame's size in game px: ("w" | "h", n) - a little over the prompt's sizes for the small ones (Kassadin:
# at those the drafts' thin rays broke up)
SIZE = {"a_hit": ("w", 18), "p_mark": ("w", 14), "p_stun": ("w", 22), "p_proc": ("h", 30), "p_extra": ("w", 10),
        "q_ice": ("w", 18), "q_hit": ("w", 20), "q_slow": ("w", 18), "e_raise": ("w", 40), "e_on": ("h", 44),
        "e_ally": ("w", 14), "w_dash": ("w", 30), "w_land": ("w", 28), "w_guard": ("w", 18), "r_slam": ("w", 50),
        "r_wave": ("w", 26), "r_crack": ("w", 26), "r_hit": ("w", 20)}
SYM = {"q_ice": "tb", "r_wave": "tb"}              # every other one "lr"

HIT = (0, -14)                  # a hit on the upper body of a 42 px unit
OVER = (0, -36)                 # over a unit's head
CHEST = (0, -14)
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
# effect -> (anchor kind, frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "p_mark": ("core", seq(range(4), [100] * 4), [OVER]),
    "p_stun": ("core", seq(range(4), [100] * 4), [OVER]),
    "p_proc": (("feet", 2), seq(range(5), [40, 70, 90, 80, 90]), [SOLES]),
    "p_extra": ("core", seq(range(3), [40, 60, 70]), [HIT]),
    # the ice: Q flies q_range 70000 at q_speed 3600 a tick, ~20 ticks (330 ms)
    "q_ice": ("core", flight(4, 60, 450), [(0, 0)]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_slow": ("core", seq(range(5), [100] * 5), [SOLES]),
    "e_raise": ("core", seq(range(5), [50, 60, 60, 70, 80]), [SOLES]),
    "e_on": (("feet", 0), seq(range(4), [110] * 4), [SOLES]),
    "e_ally": ("core", seq(range(4), [110] * 4), [OVER]),
    "w_dash": ("core", seq(range(4), [40, 60, 70, 80]), [SOLES]),
    "w_land": ("core", seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "w_guard": ("core", seq(range(4), [120] * 4), [CHEST]),
    "r_slam": ("core", seq(range(6), [40, 50, 60, 70, 80, 90]), [SOLES]),
    # the wave: r_len 80000 at r_speed 9000 a tick, ~9 ticks (150 ms)
    "r_wave": ("core", flight(4, 50, 250), [(0, 0)]),
    # one stamp of the fissure, held over its fields' r_zone 240 ticks (4 s)
    "r_crack": ("core", seq(range(8), [60, 60, 60, 3200, 200, 150, 150, 120]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
}
BIG = {"e_on", "r_wave", "r_slam", "r_crack"}


def use_braum():
    """import_kassadin's functions read their module's tables: point them at Braum's."""
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in ICE + FROST + GOLD]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS
    K.BOXES, K.SIZE, K.SYM, K.AXIS = BOXES, SIZE, SYM, {}
    K.SRC, K.SHEETS = SRC, SHEETS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    use_braum()
    sheets = {n: K.load(n) for n in SHEETS}
    cells = K.build_cells(sheets)
    tables = {"league_braum_fx": {}, "league_braum_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        anc = K.anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_braum_big" if name in BIG else "league_braum_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
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
        from PIL import ImageDraw
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
