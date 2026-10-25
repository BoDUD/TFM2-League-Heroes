#!/usr/bin/env python3
"""Ambessa's step-1 pack for Codex (assets/source/ambessa/MODEL_PROMPTS.md): the step-0 design at game size and CHIBI,
squares drawn BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_ambessa_model.py [--out DIR] [--height 48] [--ppu 1.75] [--share 0.32]

Step 0 (hd/A 216x196, hd/SA 147x176) drew her nearly life-proportioned: hair top to chin 44 of 196 rows (22%; the
pack's top laners draw the head about a third), so at game size her face is a few squares and her dark plate one smear.
The step-1 targets make her chibi first (`chibi`): the head (HEAD_* box, hair top to chin) blown up so it is `share` of
the whole height, its chin back where the body's is, its centre over the neck; then cut to the count (height x PPU
rows: 48 game px at PPU 1.75 -> 84). Codex redraws from the step-0 picture (the look) at the target's size and
proportions. A her idle 3/4 front, SA her side, both facing right, both the same height (Codex drew SA about a
tenth smaller: 838 px raw against A's 876); two takes each. 13 px squares
(84 x 13 = 1092 tall in Codex's 1254 canvas, about 81 squares wide with the blades); the soles' bottom edge on a whole
number of squares from the canvas top (1209 = 93 x 13), so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_{A,SA}.png (step 0, the look to keep), 2_target_{A,SA}.png
(chibi, cut to the count: size, place, pose, the head's share - details broken), 3_layout_{A,SA}.png (with the grid,
the top / eye / ground lines), 4_head.png (her head read back, 8x), style/5..7.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_model as RM  # noqa: E402
from design_ambessa_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ambessa")
# name -> (head box in hd/<name>.png: hair top row, chin row, first col, end col; the eye row)
HEAD = {"A": ((0, 44, 74, 132), 26), "SA": ((0, 47, 40, 99), 26)}
SHOULDER = 28   # rows above the chin the body keeps (the fur mantle rises beside the head)
PX, SOLE = 13, 1209
GREY = (225, 225, 225)
STYLE = {"5_style_illaoi.png": ("illaoi", "hd_idle"), "6_style_darius.png": ("darius", "hd_idle"),
         "7_style_ksante.png": ("ksante", "hd_idle")}


def chibi(d, box, share):
    """`d` (hd RGBA) with its head scaled so it is `share` of the whole height, the chin where it was, the head centred
    over the neck; the body untouched. -> (chibi RGBA, the head's scale, rows the head's top moved up)."""
    r0, r1, c0, c1 = box
    body_rows = d.shape[0] - r1
    f = share / (1 - share) * body_rows / (r1 - r0)
    head = Image.fromarray(np.ascontiguousarray(d[r0:r1, c0:c1]))
    head = head.resize((round(head.width * f), round(head.height * f)), Image.NEAREST)
    body = Image.fromarray(np.ascontiguousarray(d[max(0, r1 - SHOULDER):]))
    top = head.height                                   # the chin's row in the chibi
    neck = (c0 + c1) / 2
    left = min(0, round(neck - head.width / 2))
    W = max(d.shape[1], round(neck + head.width / 2)) - left
    can = Image.new("RGBA", (W, top + body_rows), (0, 0, 0, 0))
    can.alpha_composite(body, (-left, top - min(SHOULDER, r1)))
    can.alpha_composite(head, (round(neck - head.width / 2) - left, 0))
    a = np.asarray(can)
    return RM.crop(a.copy()), f


def target(name, rows, share):
    """The chibi of hd/<name> cut to `rows` rows, its eye row in the cut."""
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
    box, eye = HEAD[name]
    c, f = chibi(d, box, share)
    k = rows / c.shape[0]
    RM.PX, RM.SOLE_Y, RM.ROWS = PX, SOLE, rows
    g = RM.target(c, k)
    eye_row = round(eye * f * k)
    return g, k, eye_row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.environ.get("TMP", "/tmp"), "ambessa_model_pack"))
    ap.add_argument("--height", type=int, default=48, help="game px, hair top to soles")
    ap.add_argument("--ppu", type=float, default=1.75)
    ap.add_argument("--share", type=float, default=0.32, help="the head's share of the height")
    a = ap.parse_args()
    out, rows = a.out, round(a.height * a.ppu)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    report = []
    for name in ("A", "SA"):
        g, k, eye_row = target(name, rows, a.share)
        can, x0, y0 = RM.place(g)
        can.save(os.path.join(out, f"2_target_{name}.png"))
        top, eye = SOLE - g.shape[0] * PX, SOLE - (g.shape[0] - eye_row) * PX
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   blue her eyes y {eye}   red ground y {SOLE}   "
                 f"one square = {PX} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "ambessa-picture", "raw", f"ambessa-{name}.png")),
                        os.path.join(out, f"1_picture_{name}.png"))
        report.append(f"{name} {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {PX}, top y {top}, eyes y {eye}, "
                      f"ground y {SOLE}")
    (r0, r1, c0, c1), _ = HEAD["A"]
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    if os.path.isfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md"))):
        shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("\n".join(report), "\n->", zp)


if __name__ == "__main__":
    main()
