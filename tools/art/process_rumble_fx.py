#!/usr/bin/env python3
"""Rumble's effects drawn by Gemini (the user, 2026-10-25: 「兰博的技能特效在这里面 注意R画的太小了 特效和英雄联盟不一样 你能改就
帮我改改」 - the FX pack's 17 pictures came back as 17 JPGs in Downloads, made in the pack's order) brought to the delivery
import_rumble_fx.py reads: assets/source/rumble/gemini_fx/rumble_fx/pixel_1x/rumble_fx_<name>.png (one row of equal
game-size frames, alpha 0/255) + manifest.json - process_nunu_fx.py's way (process_shyvana_fx's keying, voting and
symmetry with these tables).

    python tools/art/process_rumble_fx.py [--src C:/t/ru_work/gemini] [--review DIR]

The JPGs (kept locally in --src as rumble_fx_<name>.jpg, not committed, process_nunu_fx.py's way): Gemini_Generated_Image_
tjfueg* = the pack's 1-10 in order (the plain one first, then (1) .. (9)), gbgilc* = 11-17. Backgrounds of every kind (black, a navy panel, grey, white, a painted
chequerboard, per-frame grey panels): every cell keyed by flooding in from its own border. Layouts other than one row of
equal cells: q_flame two rows of two; e_harpoon, dz_on, r_launch and burn cut where the drawings' columns leave gaps
(CUTS); haste a grid of four rows, each row's left half (a puff on each side, mirrored) one frame.
Sizes (game px) are the pack's except where League's own look asks otherwise (the user's 「特效和英雄联盟不一样」, compared with
Riot's ability videos 2026-10-25): Flamespitter's cone is League's 64 degrees, much wider than the pack's 40 x 18 (STRETCH:
Gemini's flame stretched up and down before the vote); The Equalizer's launch drawn bigger (「R画的太小了」). The landing
(r_fall) and the Scrap Shield are redrawn on these frames by tools/art/fix_rumble_fx.py (League's look: the rocket stuck
in the cracked, red-hot ground; a tight cyan shell of shards).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import process_shyvana_fx as S  # noqa: E402  effect(), down() with this module's tables put in
import process_hwei_fx as HW  # noqa: E402  key() from grey border colours

RAW = "C:/t/ru_work/gemini"           # the user's JPGs renamed rumble_fx_<name>.jpg (--src)
OUT = os.path.join(ROOT, "assets", "source", "rumble", "gemini_fx", "rumble_fx")
FLYING = {"e_harpoon"}           # turned with its flight: drawn flying right, symmetric top to bottom
FORWARD = {"q_flame"}            # drawn into his own skill frames: points right, no symmetry
# effect -> (frames, game size (w, h)): the pack's (tools/art/pack_rumble_fx.py FX), League's where it differs
SOURCES = {
    "a_hit": (3, (12, 12)), "oh_hit": (4, (14, 14)), "q_flame": (4, (42, 24)), "q_hit": (3, (12, 12)),
    "e_harpoon": (4, (16, 8)), "e_hit": (3, (14, 14)), "e2_hit": (4, (18, 18)), "e_zap": (4, (20, 30)),
    "w_shield": (4, (56, 42)), "haste": (4, (40, 10)), "dz_on": (5, (40, 40)), "dz_steam": (4, (36, 16)),
    "oh_on": (6, (56, 50)), "oh_smoke": (4, (36, 22)), "r_launch": (5, (44, 76)), "r_fall": (11, (34, 50)),
    "burn": (4, (20, 9)),
}
LAYOUT = {"q_flame": (2, 2)}
# the picture's frame cuts (x) where its frames are not evenly spaced, midway in the drawings' column gaps
CUTS = {"e_harpoon": [0, 1531, 2935, 4416, 5856], "dz_on": [0, 888, 1855, 2780, 3767, 4640],
        "r_launch": [0, 706, 1399, 2186, 2860, 3584], "burn": [0, 682, 1375, 2070, 2752]}
# haste: rows (y0, y1) of the 4 x 4 grid; each row's left half (x 0 - 1387: a puff on each side, mirrored) is a frame
HASTE_ROWS = [(155, 361), (510, 763), (820, 1142), (1336, 1536)]
HASTE_X = (0, 1387)
STRETCH = {"q_flame": 1.7}        # rows grown before the vote: League's cone is 64 degrees, Gemini's jet about 25
KEY = {}
# keyed by brightness instead of the border flood: drawings that reach their cell's edge on a plain ground (the steam and
# the launch's smoke columns stand on the bottom edge, so the flood took them for the ground; the black smoke of oh_smoke
# on white sits between black divider lines, which the grey key took for a dark ground and removed everywhere)
KEYMODE = {"dz_steam": "dark", "r_launch": "dark", "oh_smoke": "white"}
THIN = {"a_hit": 0.3, "oh_hit": 0.35, "q_flame": 0.4, "q_hit": 0.35, "e_harpoon": 0.3, "e_hit": 0.3, "e2_hit": 0.3,
        "e_zap": 0.3, "w_shield": 0.25, "haste": 0.4, "dz_on": 0.35, "dz_steam": 0.35, "oh_on": 0.4, "oh_smoke": 0.4,
        "r_launch": 0.35, "r_fall": 0.35, "burn": 0.4}


def lp(path):
    return S.lp(path)


def setup():
    """process_shyvana_fx's functions read their module's tables: put Rumble's in (and process_hwei_fx's grey key, and
    this module's cells)."""
    S.FLYING, S.FORWARD, S.LAYOUT, S.KEY, S.THIN = FLYING, FORWARD, LAYOUT, KEY, THIN
    S.key = HW.key
    S.cells_of = cells_of


def keyed(sub, name):
    mode = KEYMODE.get(name)
    f = sub.astype(int)
    if mode == "dark":                           # anything clearly lighter than the black ground
        fg = f.max(-1) > 45
    elif mode == "white":                        # anything clearly off the white ground, the black divider columns out
        fg = (f.min(-1) < 200) | (f.max(-1) - f.min(-1) > 40)
        dark = f.max(-1) < 70
        fg[:, dark.mean(0) > 0.6] = False
        fg[dark.mean(1) > 0.6, :] = False
    else:
        fg = S.key(sub, KEY.get(name, S.KEY_D))
    fg = ndimage.binary_opening(fg, np.ones((2, 2), bool))
    a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
    a4[..., :3] = sub
    a4[..., 3] = np.where(fg, 255, 0)
    return a4


def cells_of(img, name, n):
    rgb = np.asarray(img.convert("RGB"))
    H, W = rgb.shape[:2]
    if name == "haste":
        boxes = [(y0, y1, HASTE_X[0], HASTE_X[1]) for y0, y1 in HASTE_ROWS]
    elif name in CUTS:
        xs = CUTS[name]
        boxes = [(0, H, xs[k], xs[k + 1]) for k in range(len(xs) - 1)]
    else:
        boxes = S.boxes(name, n, H, W)
    out = [keyed(rgb[y0:y1, x0:x1], name) for y0, y1, x0, x1 in boxes]
    if name in STRETCH:
        f = STRETCH[name]
        out = [np.asarray(Image.fromarray(c).resize((c.shape[1], round(c.shape[0] * f)), Image.NEAREST)) for c in out]
    h0 = max(c.shape[0] for c in out)
    w0 = max(c.shape[1] for c in out)
    out = [np.pad(c, ((0, h0 - c.shape[0]), ((w0 - c.shape[1]) // 2, w0 - c.shape[1] - (w0 - c.shape[1]) // 2), (0, 0)))
           for c in out]
    return out[:n]


def process(name, src=RAW):
    n, size = SOURCES[name]
    img = Image.open(lp(os.path.join(src, f"rumble_fx_{name}.jpg")))
    return S.effect(name, n, size, img)


def review_sheet(sheets, path, Z=4):
    from PIL import ImageDraw
    rows = []
    for name, s, w in sheets:
        n = s.shape[1] // w
        im = Image.new("RGBA", ((s.shape[1] + 2 * n) * Z, s.shape[0] * Z), (40, 40, 52, 255))
        for k in range(n):
            cell = s[:, k * w:(k + 1) * w]
            bg = Image.new("RGBA", (w * Z, s.shape[0] * Z), (70, 74, 60, 255))
            bg.alpha_composite(Image.fromarray(cell).resize((w * Z, s.shape[0] * Z), Image.NEAREST))
            im.alpha_composite(bg, (k * (w + 2) * Z, 0))
        rows.append((name, im))
    W = max(r.width for _, r in rows) + 110
    sheet = Image.new("RGBA", (W, sum(r.height + 12 for _, r in rows)), (20, 20, 26, 255))
    d = ImageDraw.Draw(sheet)
    y = 0
    for name, r in rows:
        sheet.alpha_composite(r, (110, y))
        d.text((4, y + 4), name, fill=(255, 255, 255, 255))
        y += r.height + 12
    sheet.convert("RGB").save(path)
    return sheet.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=RAW)
    ap.add_argument("--review")
    ap.add_argument("--only", help="comma separated effect names")
    a = ap.parse_args()
    setup()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    names = a.only.split(",") if a.only else list(SOURCES)
    man_path = os.path.join(OUT, "manifest.json")
    old = {}
    if os.path.isfile(lp(man_path)):
        old = {e["name"]: e for e in json.load(open(lp(man_path), encoding="utf-8"))["effects"]}
    sheets = []
    for name in names:
        cells = process(name, a.src)
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"rumble_fx_{name}.png")))
        old[name] = {"name": name, "file": f"rumble_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                     "symmetry": "top-bottom" if name in FLYING else "none (points right)" if name in FORWARD
                     else "left-right", "source": f"gemini rumble_fx_{name}.jpg"}
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}", flush=True)
    entries = [old[k] for k in SOURCES if k in old]
    with open(lp(man_path), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_rumble_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        path = os.path.join(a.review, "rumble_fx_processed.png")
        print(path, review_sheet(sheets, path))


if __name__ == "__main__":
    main()
