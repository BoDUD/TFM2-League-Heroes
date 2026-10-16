#!/usr/bin/env python3
"""Import Tahm Kench's effects (assets/source/tahmkench/PROMPTS_FX.md, 19 pictures) as the game sheets
league_tahmkench_fx and league_tahmkench_big, replacing the stand-ins of tools/art/fx_tahmkench.py.

    python tools/art/import_tahmkench_fx.py [--review out.png]

The source: the 19 sheets Codex drew for the pack, pasted by the user into the chat as JPGs 2000 px wide
(assets/source/tahmkench/codex_fx/pasted/<effect>.jpg; the user: 「特效生成完毕了 你帮我处理一下 然后导入吧」). Each is a
row of equal cells (the pack's layout, scaled to 2000 px): a game square = 2000 / cells / the cell's squares (CELL),
the background black (two of the taste marks on a grey gradient: keyed by colour instead). Every square: opaque when a
third of its pixels are drawn, its colour the drawn pixels' mean pulled half way to their brightest quarter (white
cores survive), snapped to the effect's ramps (the prompt's). Placed on the unit's pivot (art-spec "Effect anchors":
x forward, y down, the soles 11 under it): the cell's middle column (the tongue: its tip) and the whole strip's drawn
rows (their middle, or their bottom on the ground for what rises from it), whole squares only, then made
symmetric for the red side (left to right, the tongue top to bottom; the fuller half mirrored).
Codex drew the W marker from straight above (a circle, asked for the ground ellipse): squashed to 0.38 of its height;
the water column twice as tall as asked (92 squares) and the shield 63 tall: 0.5 and 0.8; the stun stars twice.
Times as the kit and the stand-ins had them.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from fx_tahmkench import Canvas  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "tahmkench", "codex_fx", "pasted")
MOD = os.path.join(ROOT, "league")


def ramp(s):
    return [tuple(int(c.strip().lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for c in s.split(",")]


WATER = ramp("#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52")
PINK = ramp("#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C")
GOLD = ramp("#FFFFFF, #FFF2A8, #FFD23F, #E39A1E, #9E5A12")
GREEN = ramp("#F2FFE0, #B6F57A, #5ED45A, #2A9A44")
SHIELD = ramp("#FFFFFF, #E2E8FF, #A9B6F2, #7B7FD6, #4E4AA0")
RED = ramp("#FFE0DA, #FF6A5A, #D62A2A, #8E1414")
CREAM = ramp("#FFF8E6, #F2E2B8, #CDB688")
TONGUE = ramp("#FFE1F0, #FF8FBF, #F0508E, #C42A66, #7E1440")      # Codex's tongue is pinker than the drool

# effect -> (cells in the picture, squares a cell is wide, ramps, anchor, (spot x, spot y), symmetry, ms per frame,
#            big sheet, y squash)
# anchor: "c" the cell's centre on the spot, "b" the cell's bottom row on the spot's row, "tip" the rightmost drawn
# column on x = spot x and the cell's middle row on y, "box" the drawn box's centre on the spot
FX = {
    "q_tongue": (2, 30, TONGUE + WATER, "tip", (1, 0), "tb", [80], False, 1.0),
    "a_hit": (3, 20, PINK + WATER, "mid", (0, -6), "lr", [70], False, 1.0),
    "q_hit": (4, 22, WATER + PINK, "mid", (0, -6), "lr", [70], False, 1.0),
    "q_stun": (4, 26, GOLD + WATER, "mid", (0, -27), "lr", [300], False, 1.0),
    "q_heal": (4, 44, GREEN, "bot", (0, 11), "lr", [120], False, 1.0),
    "e_shield": (4, 72, SHIELD, "mid", (0, -10), "lr", [80, 600, 900, 100], False, 0.75),
    "w_down": (4, 48, WATER, "bot", (0, 13), "lr", [100], True, 1.0),
    "w_warn": (6, 32, RED + WATER, "mid", (0, 10), "lr", [170], True, 0.38),
    "w_up": (4, 48, WATER, "bot", (0, 13), "lr", [90], True, 0.5),
    "w_hit": (3, 20, WATER, "bot", (0, 11), "lr", [90], False, 1.0),
    "r_gulp": (4, 32, CREAM + PINK + WATER, "mid", (0, -16), "lr", [90], False, 1.0),
    "r_in": (3, 24, WATER, "bot", (0, 11), "lr", [100], False, 1.0),
    "r_spit": (3, 22, PINK + WATER, "mid", (0, -6), "lr", [90], False, 1.0),
    "t_pip1": (2, 21, WATER + PINK, "box", (-6, -31), None, [400], False, 1.0),
    "t_pip2": (2, 21, WATER + PINK, "box", (0, -31), "lr", [400], False, 1.0),
    "t_pip3": (2, 21, WATER + PINK, "box", (6, -31), None, [400], False, 1.0),
    "q_slow": (4, 24, PINK, "mid", (0, 11), "lr", [300], False, 1.0),
    "r_full": (3, 44, WATER, "bot", (0, 11), "lr", [200], False, 1.0),
    "r_bubble": (2, 24, WATER, "bot", (0, 11), "lr", [300], False, 1.0),
}
ROWS = {"q_stun": (0, 310)}       # Codex drew the stars twice (two rows of four): the top row only
PIP_W = 5                         # the taste marks are drawn 5 squares wide whatever the picture's scale


def drawn(a, name):
    """Pixels that belong to the effect: off the black background; the grey-ground taste marks by their colour."""
    rgb = a.astype(int)
    mx, mn = rgb.max(-1), rgb.min(-1)
    if name.startswith("t_pip"):
        return (mx - mn > 45) | ((mx > 215) & (mn > 190) & (np.roll(mx - mn, 6, 0) > 45))
    return mx > 34


def squares(cell, k, name, pal, squash):
    """The cell read on a grid of 1 / k pixels a square -> RGBA squares."""
    H, W = cell.shape[:2]
    gw, gh = max(1, round(W * k)), max(1, round(H * k * squash))
    m = drawn(cell, name)
    out = np.zeros((gh, gw, 4), np.uint8)
    xs = np.linspace(0, W, gw + 1).astype(int)
    ys = np.linspace(0, H, gh + 1).astype(int)
    palf = np.asarray(pal, float)
    for j in range(gh):
        for i in range(gw):
            blk = cell[ys[j]:ys[j + 1], xs[i]:xs[i + 1]].reshape(-1, 3).astype(float)
            mb = m[ys[j]:ys[j + 1], xs[i]:xs[i + 1]].reshape(-1)
            if not len(mb) or mb.mean() < 0.34:
                continue
            px = blk[mb]
            lum = px @ np.array([0.3, 0.59, 0.11])
            top = px[lum >= np.quantile(lum, 0.75)].mean(0)
            c = (px.mean(0) + top) / 2
            out[j, i, :3] = pal[int(((palf - c) ** 2).sum(1).argmin())]
            out[j, i, 3] = 255
    return out


def place(sq, anchor, spot, sym, strip_box):
    """sq on a frame centred on the pivot. Columns: the cell's middle column on spot x (the tongue: its tip); rows by
    the whole strip's drawn rows (strip_box = top, bottom), so the frames keep their places against each other."""
    c = Canvas(80)
    H, W = sq.shape[:2]
    ys, xs = np.nonzero(sq[..., 3] > 0)
    if not len(ys):
        return c.done()
    top, bot = strip_box
    ax = W // 2
    ay = (top + bot) // 2
    if anchor == "tip":
        ax = int(xs.max())
    elif anchor == "bot":
        ay = bot
    elif anchor == "box":
        ax, ay = (int(xs.min()) + int(xs.max())) // 2, (int(ys.min()) + int(ys.max())) // 2
    for y, x in zip(ys, xs):
        c.dot(spot[0] + int(x) - ax, spot[1] + int(y) - ay, tuple(int(v) for v in sq[y, x, :3]))
    if sym == "lr":
        if spot[0] != 0:
            raise ValueError("left-right symmetry only about the pivot")
        c.mirror_x()
    elif sym == "tb":
        c.mirror_y()
    return c.done()


def build():
    sheets = {"league_tahmkench_fx": {}, "league_tahmkench_big": {}}
    cells_of = {}
    for name, (n, cw, pal, anchor, spot, sym, ms, big, squash) in FX.items():
        a = np.asarray(Image.open(os.path.join(SRC, name + ".jpg")).convert("RGB"))
        W = a.shape[1]
        k = cw / (W / n)
        if name in ROWS:
            a = a[ROWS[name][0]:ROWS[name][1]]
        sqs = []
        for i in range(n):
            cell = a[:, round(i * W / n):round((i + 1) * W / n)]
            if name.startswith("t_pip"):           # the mark alone, PIP_W squares wide
                m = drawn(cell, name)
                ys, xs = np.nonzero(m)
                cell = cell[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
                k = PIP_W / (xs.max() - xs.min() + 1)
            sqs.append(squares(cell, k, name, pal, squash))
        rows = [np.nonzero(q[..., 3].any(1))[0] for q in sqs]
        strip_box = (min(r.min() for r in rows if len(r)), max(r.max() for r in rows if len(r)))
        frames = [(place(q, anchor, spot, sym, strip_box), ms[i] if len(ms) > 1 else ms[0]) for i, q in enumerate(sqs)]
        sheets["league_tahmkench_big" if big else "league_tahmkench_fx"][name] = frames
        cells_of[name] = [f for f, _ in frames]
    return sheets, cells_of


def review(cells_of, path, z=6):
    from PIL import ImageDraw
    rows = []
    for name, fs in cells_of.items():
        W = sum(f.shape[1] + 3 for f in fs)
        H = max(f.shape[0] for f in fs)
        img = Image.new("RGBA", (W * z, H * z), (92, 98, 86, 255))
        x = 0
        for f in fs:
            img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST),
                                (x * z, (H - f.shape[0]) // 2 * z))
            x += f.shape[1] + 3
        rows.append((name, img))
    W = max(r.width for _, r in rows) + 110
    out = Image.new("RGB", (W, sum(r.height + 8 for _, r in rows)), (30, 32, 30))
    d = ImageDraw.Draw(out)
    y = 0
    for name, r in rows:
        d.text((4, y + 4), name, fill=(255, 255, 255))
        out.paste(r, (110, y), r)
        y += r.height + 8
    out.save(path)
    print(path, out.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    sheets, cells_of = build()
    for sheet, tags in sheets.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {v[0][0].shape[1]}x{v[0][0].shape[0]}" for t, v in tags.items()))
    if a.review:
        review(cells_of, a.review)


if __name__ == "__main__":
    main()
