#!/usr/bin/env python3
"""Illaoi's effects drawn by Gemini (the user, 2026-10-23: 「俄洛伊的特效在这里面 你可以导入后使用」 - the FX pack's 15
pictures came back as JPGs in Downloads, made in the pack's order) brought to the delivery import_illaoi_fx.py reads:
assets/source/illaoi/codex_fx/illaoi_fx/pixel_1x/illaoi_fx_<name>.png (one row of equal game-size frames, alpha 0/255)
+ manifest.json - process_hwei_fx.py's way (process_shyvana_fx's keying, cutting, voting and symmetry with these tables;
the ground keyed from the GREY border colours only, process_hwei_fx.key).

    python tools/art/process_illaoi_fx.py [--src C:/t/il_work/gemini] [--review DIR]

Which JPGs are hers: the 15 downloaded 00:55-00:57 (Gemini_Generated_Image_2iykwo* x10, then cxcpqh* x5), copied to
--src as g00.jpg .. g14.jpg in the order they were made (not committed); they follow the pack's order one for one.
Gemini's layout: p_slam one column of six, w_slam two rows of four (seven drawn: kept), e_grab two of two, e_vessel two
rows of four (eight: kept, two turns of its loop); the rest one row of the pack's count but e_break (six of the six).
Grounds: black, white with grey dividers (p_spawn), white (r_slam), white over black (r_aura). Symmetric from the
fuller half: left to right, top to bottom for the projectile the game turns with its flight (e_grab).
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

OUT = os.path.join(ROOT, "assets", "source", "illaoi", "codex_fx", "illaoi_fx")
FLYING = {"e_grab"}
FORWARD = set()
# (rows, columns) of the picture's grid where it is not one row of `frames` cells; the cells read row by row
LAYOUT = {"p_slam": (6, 1), "w_slam": (2, 4), "e_grab": (2, 2), "e_vessel": (2, 4)}
# file -> (effect, frames, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "g00.jpg": ("a_hit", 3, (12, 12)), "g01.jpg": ("p_spawn", 5, (32, 14)), "g02.jpg": ("p_slam", 6, (40, 20)),
    "g03.jpg": ("p_hit", 3, (14, 14)), "g04.jpg": ("p_heal", 6, (36, 46)), "g05.jpg": ("w_slam", 7, (44, 22)),
    "g06.jpg": ("w_mark", 4, (12, 12)), "g07.jpg": ("e_grab", 4, (28, 12)), "g08.jpg": ("e_spirit", 6, (26, 44)),
    "g09.jpg": ("e_vessel", 8, (22, 10)), "g10.jpg": ("e_break", 6, (32, 36)), "g11.jpg": ("e_slow", 4, (16, 8)),
    "g12.jpg": ("r_slam", 8, (64, 30)), "g13.jpg": ("r_aura", 6, (40, 14)), "g14.jpg": ("r_hit", 4, (16, 16)),
}
# cells cut on the gaps between the drawings where they are not equal: w_slam's first row is four (the flash narrow, the
# burst wide), its second three, split at y 970 (y0, y1, x0, x1 on the JPG)
CUT_BOXES = {"w_slam": [(0, 970, 0, 394), (0, 970, 394, 1001), (0, 970, 1001, 1916), (0, 970, 1916, 2902),
                        (970, 1472, 0, 1030), (970, 1472, 1030, 1960), (970, 1472, 1960, 2902)]}
BOTTOM = {"w_slam"}              # every frame's lowest drawn row on the cell's bottom (its two rows sat differently)
WHITE_GROUND = {"p_spawn"}       # white ground and grey dividers: only the white is ground (its dark disc is drawn)
DARK_DROP = {"r_aura": 70}       # its ring's dark teal fill dropped (it read as a hole under her): max channel below
KEY = {}
THIN = {"a_hit": 0.3, "p_hit": 0.35, "p_heal": 0.35, "p_slam": 0.4, "w_slam": 0.4, "w_mark": 0.35, "e_spirit": 0.3,
        "e_break": 0.35, "r_slam": 0.4, "r_aura": 0.35, "r_hit": 0.35, "e_vessel": 0.4}


def setup():
    """process_shyvana_fx's functions read their module's tables: put Illaoi's in (and process_hwei_fx's grey key, and
    this module's cells)."""
    S.FLYING, S.FORWARD, S.LAYOUT, S.KEY, S.THIN = FLYING, FORWARD, LAYOUT, KEY, THIN
    S.key = HW.key
    S.cells_of = cells_of


def boxes(name, n, H, W):
    return CUT_BOXES.get(name) or S.boxes(name, n, H, W)


def cells_of(img, name, n):
    rgb = np.asarray(img.convert("RGB"))
    H, W = rgb.shape[:2]
    out = []
    for y0, y1, x0, x1 in boxes(name, n, H, W):
        sub = rgb[y0:y1, x0:x1]
        f = sub.astype(int)
        if name in WHITE_GROUND:
            fg = ~((f.min(-1) > 200) | ((f.max(-1) - f.min(-1) < 12) & (f.mean(-1) < 140) & (f.mean(-1) > 90)))
            fg = ndimage.binary_opening(fg, np.ones((3, 3), bool))
            fg[:, :8] = fg[:, -8:] = False
        else:
            fg = S.key(sub, KEY.get(name, S.KEY_D))
        if name in DARK_DROP:
            fg &= f.max(-1) >= DARK_DROP[name]
        a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
        a4[..., :3] = sub
        a4[..., 3] = np.where(fg, 255, 0)
        out.append(a4)
    return out[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/il_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    setup()
    os.makedirs(S.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, size) in SOURCES.items():
        cells = S.effect(name, n, size, Image.open(S.lp(os.path.join(a.src, fn))))
        if name in BOTTOM:
            cells = [np.roll(c, c.shape[0] - 1 - int(np.nonzero(c[..., 3].any(1))[0].max()), axis=0) for c in cells]
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(S.lp(os.path.join(OUT, "pixel_1x", f"illaoi_fx_{name}.png")))
        entries.append({"name": name, "file": f"illaoi_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(S.lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_illaoi_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 5
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
        path = os.path.join(a.review, "illaoi_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
