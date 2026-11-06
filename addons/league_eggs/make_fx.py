#!/usr/bin/env python3
"""The Queen of the Freljord's ice crown (league_eggs): a plain 1x sheet the game draws itself as a buff's view.

    python -X utf8 addons/league_eggs/make_fx.py [--out STEM] [--review out.png]

The user, 2026-11-05: 「弗雷尔卓德之战 ... 最先击杀/助攻对方的获得「冰雪女王」称号，头顶出现永久的冰冠特效」. Drawn here on the
game grid (1x pixels): a 9-px crown of three ice spikes (the middle one tallest) on a band with two white gems, a deep blue
outline so it reads on any hair; a glint runs over the three tips (4 frames, 1.1 s, looping).

A buff's view is drawn by the game a texel a game px, centred on the unit's pivot (tools/art/import_yuumi_fx.py, the
ride picture's lesson of 2026-11-05: never registered in league.dll's hd.rs), and never mirrored (champion-data.md
section 6), so the crown stays centred over the pivot whichever way she faces. Each queen has her own tag with the
crown's band `SINK` px into her crown - the top of her head over the pivot in game px, measured here on the frames the
battlefield draws (`head_top`: her first hd_idle frame at 1 / PPU when league.dll's hd.rs lists her, else her 1x idle,
times her hd.rs SIZES; the highest opaque row within 6 game px either side of the frame's middle, the rule of
tools/art/yuumi_ride_lifts.py): ashe 24, sejuani 25, lissandra 31 on the 2026-11-05 sheets (league_yuumi's lifts.rs, from
the 1x frames and an older Lissandra sheet, says 23 / 24 / 30) - and the frame padded so the pivot is its middle.
Checked on the queens' frames (x4 renders, 2026-11-05): the band sits 3 px into the hood / hair / dome in the idle,
run and attack poses; it floats while Ashe aims in her idle (0.57 s holds, her head 5 px lower) and while Sejuani rides
(run: her head 4 px lower) - a buff's picture cannot follow the body's frames.

Writes STEM#sheet.png and STEM#anim.fanim (default addons/league_eggs/effects/league_eggs_crown_1x). The add-on hangs
league_eggs_crown_<queen> on the winner; the picture shows once a champion's data names it in `view_buffs`
(README.md: the entries for the main pack's league_ashe / league_sejuani / league_lissandra, with the sheet in
league/effects/: generate it there with --out league/effects/league_eggs_crown_1x).
"""
import argparse
import json
import os
import re

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "effects", "league_eggs_crown_1x")
QUEENS = ("ashe", "sejuani", "lissandra")
SINK = 3                        # the band sits this many px into her hair
HEAD = 2                        # rows over the spikes for the glint
BAND = 6                        # game px either side of the frame's middle the head is looked for in
HD_RS = os.path.join(ROOT, "addons", "league_main", "src", "hd.rs")


def hd_tables():
    """league.dll's hd.rs: ({champion: PPU} of HEROES, {champion: size} of SIZES)."""
    text = open(HD_RS, encoding="utf-8").read()
    at = text.index("pub const HEROES")
    ppu = {n: float(k) for n, k in re.findall(r'\("([a-z0-9_]+)", ([0-9.]+), include_str!', text[at:text.index("];", at)])}
    at = text.index("pub const SIZES")
    size = {n: float(k) for n, k in re.findall(r'\("([a-z0-9_]+)", ([0-9.]+)\)', text[at:text.index("];", at)])}
    return ppu, size


def head_top(queen, tables=None):
    """Game px from her pivot up to the top of her head in the first idle frame the battlefield draws (frames centred on
    the pivot): hd_idle at 1 / PPU for a hero with dense frames, the 1x idle otherwise; times her size."""
    ppu, size = tables or hd_tables()
    hero = "league_" + queen
    stem = os.path.join(ROOT, "league", "champions", hero)
    with open(stem + "#anim.fanim", "rb") as f:
        anims = json.loads(f.read().decode("utf-8").lstrip("﻿"))["anims"]
    dense = hero in ppu and "hd_idle" in anims
    scale = ppu[hero] if dense else 1.0
    d = anims["hd_idle" if dense else "idle"]["frames"][0]["data"]
    x, y, w, h = (int(round(d[k])) for k in ("x", "y", "w", "h"))
    alpha = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA").crop((x, y, x + w, y + h)))[..., 3] > 0
    mid = (w - 1) / 2
    band = alpha[:, max(0, int(round(mid - BAND * scale))):int(round(mid + BAND * scale)) + 1]
    rows = np.nonzero(band.any(1))[0]
    return int(round(((h - 1) / 2 - rows.min()) / scale * size.get(hero, 1.0)))


def crowns():
    """{queen: the top of her head over her pivot, game px}."""
    tables = hd_tables()
    out = {q: head_top(q, tables) for q in QUEENS}
    for q, c in out.items():
        assert 15 <= c <= 45, f"{q}'s head top {c} px over her pivot: look at her sheet"
    return out

PAL = {
    "o": (28, 60, 120),         # outline, deep blue
    "d": (60, 124, 200),        # dark ice
    "m": (120, 200, 240),       # ice
    "l": (200, 244, 255),       # light ice
    "w": (255, 255, 255),       # white: tips, gems
}
CROWN = [
    "....o....",
    ".o.owo.o.",
    "owooloowo",
    "olooloolo",
    "olmlmlmlo",
    "odmwmwmdo",
    ".ooooooo.",
]
TIPS = [(1, 1), (1, 4), (1, 7)]   # (row, col) of the left, middle and right spike tips in CROWN


def crown():
    h, w = len(CROWN), len(CROWN[0])
    a = np.zeros((h + HEAD, w, 4), np.uint8)
    for y, r in enumerate(CROWN):
        for x, ch in enumerate(r):
            if ch in PAL:
                a[y + HEAD, x, :3] = PAL[ch]
                a[y + HEAD, x, 3] = 255
    return a


def glint(a, tip):
    """A small four-point glint on a spike's tip."""
    b = a.copy()
    y, x = tip[0] + HEAD, tip[1]
    for dy, dx in ((0, 0), (-1, 0), (-2, 0), (0, -1), (0, 1)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < b.shape[0] and 0 <= xx < b.shape[1]:
            if dy == 0 and dx != 0 and b[yy, xx, 3]:
                continue                  # keep the outline beside the tip
            b[yy, xx, :3] = PAL["w"]
            b[yy, xx, 3] = 255
    return b


def frames():
    c = crown()
    return [(c, 650), (glint(c, TIPS[0]), 140), (glint(c, TIPS[1]), 160), (glint(c, TIPS[2]), 140)]


def placed(a, crown_px):
    """The crown with its bottom row `crown_px - SINK` px over the pivot, in an odd frame centred on the pivot."""
    h, w = a.shape[:2]
    bottom = crown_px - SINK               # px over the pivot of the crown's lowest row
    top = bottom + h - 1                   # px over the pivot of its highest row
    out = np.zeros((2 * top + 1, w, 4), np.uint8)
    out[0:h] = a                           # row 0 is `top` px over the pivot; the pivot is row `top`
    return out


def write_sheet(stem, tags):
    """tags: {tag: [(frame, ms), ...]} -> stem#sheet.png + stem#anim.fanim (frames side by side, 1 px apart; a frame
    the same as one already placed points at it)."""
    rects, seen, x = [], {}, 0
    for frs in tags.values():
        for arr, _ in frs:
            key = (arr.shape, arr.tobytes())
            if key in seen:
                rects.append(seen[key])
                continue
            h, w = arr.shape[:2]
            rects.append((x, 0, w, h))
            seen[key] = rects[-1]
            x += w + 1
    W = max(r[0] + r[2] for r in rects)
    H = max(r[3] for r in rects)
    sheet = np.zeros((H, W, 4), np.uint8)
    anims, i = {}, 0
    for tag, frs in tags.items():
        out = []
        for arr, ms in frs:
            rx, ry, rw, rh = rects[i]
            sheet[ry:ry + rh, rx:rx + rw] = arr
            out.append({"duration": round(ms / 1000.0, 6), "data": {"x": float(rx), "y": float(ry), "w": float(rw),
                                                                   "h": float(rh)}})
            i += 1
        anims[tag] = {"frames": out}
    os.makedirs(os.path.dirname(os.path.abspath(stem)), exist_ok=True)
    Image.fromarray(sheet, "RGBA").save(stem + "#sheet.png", optimize=True)
    with open(stem + "#anim.fanim", "w", encoding="utf-8", newline="\n") as f:
        json.dump({"anims": anims}, f, separators=(",", ":"))
    return W, H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--review", help="write each queen's frames at 8x over a stand-in head here")
    a = ap.parse_args()
    fr = frames()
    # the crown itself is symmetric; the glint runs left to right over it (a buff's view is never mirrored)
    assert (fr[0][0] == fr[0][0][:, ::-1]).all(), "the crown is not symmetric"
    tops = crowns()
    tags = {q: [(placed(f, c), ms) for f, ms in fr] for q, c in tops.items()}
    w, h = write_sheet(a.out, tags)
    print(f"{a.out}#sheet.png {w}x{h}: " + ", ".join(f"{q} (head {tops[q]} px) {len(v)}f {v[0][0].shape[1]}x{v[0][0].shape[0]}"
                                                    for q, v in tags.items()))
    if a.review:
        Z, pad = 8, 4
        cols = [v for v in tags.values()]
        fh = max(v[0][0].shape[0] for v in cols)
        img = Image.new("RGBA", ((9 + pad) * Z * len(fr) * len(cols), fh * Z), (70, 80, 70, 255))
        x = 0
        for q, v in tags.items():
            for f, _ in v:
                hh = f.shape[0]
                # a stand-in head: a brown disc whose top is at the queen's crown height
                head = np.zeros_like(f)
                top = hh // 2 - tops[q]
                for yy in range(max(top, 0), min(top + 9, hh)):
                    for xx in range(1, 8):
                        if (xx - 4) ** 2 + (yy - top - 4.5) ** 2 <= 16:
                            head[yy, xx] = (120, 80, 50, 255)
                fr_img = Image.fromarray(head)
                fr_img.alpha_composite(Image.fromarray(f))
                img.alpha_composite(fr_img.resize((f.shape[1] * Z, hh * Z), Image.NEAREST), (x, (fh - hh) * Z))
                x += (9 + pad) * Z
        img.convert("RGB").save(a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()
