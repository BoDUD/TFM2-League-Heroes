#!/usr/bin/env python3
"""Import Elise's effects (assets/source/elise/PROMPTS_FX.md, 22 pictures) as the game sheets league_elise_fx and
league_elise_big.

    python tools/art/import_elise_fx.py [--review out.png]

The source is one overview picture of all 22 effects with transparent background, cut by the user from Codex's step-3
run (assets/source/elise/codex_fx/elise_fx_overview.png; the user: 「蜘蛛特效你自己裁剪处理吧」). Every effect's frames are
boxes in it (BOXES: band of rows, columns per frame - read off the picture's opaque pieces; frames glued together were
split on their emptiest column), read import_nidalee.py / import_kassadin.py's way: each frame cut from its box (the
labels under the rows dropped as pieces outside the band), one scale per effect, every game pixel the commonest
colour under it snapped to the prompt's ramps with the bright cores kept, the red side's symmetry - the flying ones
top to bottom, everything else left to right about its own best axis (the fuller half mirrored) - checked square for
square. Codex drew the spiderlings' bites as crescent slashes and the volatile spiderling from the front (its handoff
missed the prompt there); the top-to-bottom mirror turns the crawling spiderling into a spider seen from above, and the
left-to-right mirror makes Skittering Frenzy's swirls two-sided.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_elise.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "elise", "codex_fx")
MOD = os.path.join(ROOT, "league")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


# the prompt's ramps (pack_elise_fx.py)
CRIMSON = ["#FFFFFF", "#FFD1DA", "#FF5C7A", "#E0143C", "#9E0A2A", "#4F0618"]
VIOLET = ["#F3E6FF", "#C9A6F2", "#8E5BD0", "#5B2E94", "#2E1452"]
SILK = ["#ECEAF2", "#C9C6D6", "#9D99B0", "#6E6A82"]
CHITIN = ["#4A3550", "#2A1E30", "#120C16"]
EARTH = ["#F2E6CF", "#D6C3A0", "#B39B76", "#8A7255", "#5E4C39"]
DARKS = {(0x4F, 0x06, 0x18), (0x2E, 0x14, 0x52), (0x6E, 0x6A, 0x82), (0x12, 0x0C, 0x16), (0x5E, 0x4C, 0x39)}

# effect -> (sheet, (y0, y1) band, [(x0, x1) per frame]) in the overview's pixels; a band ends above the label under
# its row (the labels' glyphs go as pieces whose middle is outside the band)
BOXES = {
    "a_spit": (1, (20, 82), [(17, 123), (140, 241)]),
    "q_bolt": (1, (18, 82), [(298, 433), (433, 558), (558, 671), (671, 808)]),
    "a_hit": (1, (20, 80), [(863, 896), (900, 942), (943, 991), (993, 1050), (1053, 1111)]),
    "q_hit": (1, (102, 182), [(15, 90), (90, 156), (156, 223), (223, 290), (290, 368)]),
    "c_hit": (1, (110, 182), [(403, 511), (514, 619), (623, 725)]),
    "cq_hit": (1, (104, 182), [(732, 804), (804, 884), (884, 958), (958, 1029), (1029, 1111)]),
    "sl_bite1": (1, (200, 291), [(13, 73), (73, 129), (129, 184), (184, 241)]),
    "sl_bite2": (1, (200, 291), [(261, 353), (353, 421), (421, 494)]),
    "sl_bite3": (1, (206, 291), [(522, 584), (584, 643), (643, 705), (705, 760)]),
    "e_web": (1, (222, 284), [(782, 887), (887, 955), (955, 1029), (1029, 1117)]),
    "e_hit": (1, (308, 399), [(9, 96), (96, 190), (190, 279)]),
    "w_spider": (1, (342, 392), [(295, 360), (360, 427), (427, 495), (495, 566)]),
    "w_boom": (1, (308, 404), [(579, "split"), ("split", 788), (788, 907)]),
    "w_hit": (1, (324, 393), [(915, 966), (966, 1015), (1015, 1064), (1064, 1113)]),
    "ce_up": (1, (423, 521), [(15, 62), (62, 112), (112, 162)]),
    "ce_land": (1, (411, 518), [(165, 280), (280, 426)]),
    "ce_hit": (1, (426, 516), [(439, 480), (480, "split"), ("split", 590)]),
    "cw_frenzy": (1, (427, 516), [(596, 727), (727, "split"), ("split", 929)]),
    "cw_on": (1, (444, 506), [(935, 1110)]),
    "tf_spider": (1, (540, 710), [(13, 143), (143, 263), (263, 389)]),
    "tf_human": (1, (543, 704), [(396, 523), (523, 641), (641, 773)]),
    "r_cast": (1, (532, 716), [(801, 902), (902, 1008), (1008, 1108)]),
}
SHEETS = {1: "elise_fx_overview.png"}
# the biggest frame's size in game px: ("w" | "h", n) (a little over the prompt's sizes for the small ones)
SIZE = {"a_spit": ("w", 13), "q_bolt": ("w", 21), "a_hit": ("w", 12), "q_hit": ("w", 18), "c_hit": ("w", 18),
        "cq_hit": ("w", 20), "sl_bite1": ("h", 16), "sl_bite2": ("h", 17), "sl_bite3": ("h", 17), "e_web": ("w", 17),
        "e_hit": ("w", 22), "w_spider": ("w", 11), "w_boom": ("w", 26), "w_hit": ("w", 11), "ce_up": ("h", 38),
        "ce_land": ("w", 30), "ce_hit": ("w", 13), "cw_frenzy": ("w", 50), "cw_on": ("w", 42), "tf_spider": ("h", 44),
        "tf_human": ("h", 46), "r_cast": ("h", 40)}
SYM = {"a_spit": "tb", "q_bolt": "tb", "e_web": "tb", "w_spider": "tb"}     # every other one "lr"

HIT = (0, -14)                  # a hit on the upper body of a 38-48 px unit
SOLES = (0, 11)                 # on the ground under a unit or a point
EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
# effect -> (anchor kind, frames with ms, spots)
FX = {
    # the spit: a_speed 4500 a tick over her 50000 reach, ~11 ticks
    "a_spit": ("core", flight(2, 60, 380), [(0, 0)]),
    # Neurotoxin: q_speed 4500 over 55000, ~13 ticks (homing: twice)
    "q_bolt": ("core", flight(4, 60, 450), [(0, 0)]),
    "a_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "c_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "cq_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "sl_bite1": ("core", seq(range(4), [50, 60, 60, 80]), [HIT]),
    "sl_bite2": ("core", seq(range(3), [50, 70, 80]), [HIT]),
    "sl_bite3": ("core", seq(range(4), [50, 60, 60, 80]), [HIT]),
    # the cocoon: e_speed 4500 over 85000, ~19 ticks
    "e_web": ("core", flight(4, 70, 700), [(0, 0)]),
    # wrapped: the middle frame held for the stun (e_stun 100 ticks)
    "e_hit": ("core", seq(range(3), [90, 1450, 140]), [HIT]),
    # the spiderling crawls: w_speed 2500 over 75000, ~30 ticks
    "w_spider": ("core", flight(4, 90, 1000, lead=0), [(0, 0)]),
    "w_boom": (("feet", 2), seq(range(3), [60, 90, 120]), [SOLES]),
    "w_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Rappel: the thread while she rises (ce_rise 13 ticks), then the banish hides her
    "ce_up": (("feet", 0), seq(range(3), [70, 80, 120]), [SOLES]),
    "ce_land": (("feet", 2), seq(range(2), [90, 160]), [SOLES]),
    "ce_hit": ("core", seq(range(3), [50, 60, 80]), [HIT]),
    "cw_frenzy": (("feet", 0), seq([0, 1], [90, 190]), [SOLES]),     # its third frame was cut to one swirl
    "cw_on": ("core", seq(range(1), [200]), [SOLES]),
    # the turns: tf_dur 16 ticks (270 ms) under the burst, its tail after
    "tf_spider": (("feet", 0), seq(range(3), [70, 110, 140]), [SOLES]),
    "tf_human": (("feet", 0), seq(range(3), [70, 110, 140]), [SOLES]),
    "r_cast": (("feet", 0), seq(range(3), [80, 100, 120]), [SOLES]),
}
BIG = {"w_boom", "ce_up", "ce_land", "tf_spider", "tf_human", "r_cast"}


def split_runs(alpha, boxes):
    """'split' ends: the emptiest column between the neighbouring frames' fixed ends."""
    cols = (alpha > 40).sum(0)
    out = []
    for k, (x0, x1) in enumerate(boxes):
        if x1 == "split":
            a, b = x0, boxes[k + 1][1]
            lo, hi = a + (b - a) // 3, b - (b - a) // 3
            seg = cols[lo:hi]
            x1 = lo + int(np.argmin(seg))
        if x0 == "split":
            x0 = out[-1][1]
        out.append((x0, x1))
    return out


def use_elise():
    """import_kassadin's functions read their module's tables: point them at Elise's."""
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in CRIMSON + VIOLET + SILK + CHITIN + EARTH]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = DARKS
    sheet = np.asarray(Image.open(lp(os.path.join(SRC, SHEETS[1]))).convert("RGBA"))
    boxes = {n: (s, band, split_runs(sheet[band[0]:band[1], :, 3], bx)) for n, (s, band, bx) in BOXES.items()}
    K.BOXES, K.SIZE, K.SYM, K.AXIS = boxes, SIZE, SYM, {}
    K.SRC, K.SHEETS = SRC, SHEETS
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    use_elise()
    sheets = {1: np.asarray(Image.open(lp(os.path.join(SRC, SHEETS[1]))).convert("RGBA")).astype(np.int16)}
    cells = K.build_cells(sheets)
    tables = {"league_elise_fx": {}, "league_elise_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        anc = K.anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_elise_big" if name in BIG else "league_elise_fx"][name] = out
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
