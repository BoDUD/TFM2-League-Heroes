#!/usr/bin/env python3
"""Heimerdinger's effects drawn by Gemini (the user, 2026-10-21: 「特效和动作全部完成了 请你收尾」, the FX pack's 27
pictures as JPGs in Downloads; 28 files, one a byte-for-byte copy) brought to the delivery import_heimerdinger_fx.py
reads: assets/source/heimerdinger/codex_fx/heimerdinger_fx/pixel_1x/heimerdinger_fx_<name>.png (one row of equal
game-size frames, alpha 0/255) + manifest.json - process_shyvana_fx.py's way (its keying, cutting and voting).

    python tools/art/process_heimerdinger_fx.py [--src C:/t/hd_work/gemini_fx] [--review DIR]

The JPGs (kept locally in --src under Gemini's names; not committed) have no alpha and backgrounds of every kind (black,
white bands, a painted chequerboard); every cell is keyed by flooding in from its own border. All frames of an effect
cropped by one box (their union), brought down by votes to the pack's game size in the effect's own K colours, made
symmetric from the fuller half: left to right; top to bottom for the five projectiles the game turns with their flight;
both ways for the two grenades (turned along their arcs) and the two muzzle flashes seen head on; not at all for the
crane's launch flash, which points forward and is baked into his frames.
Gemini's layout: e_blast two rows of three, e_hit six bolts (three frames of a mirrored pair each), x_dust eight
frames at uneven places (cut by its own gaps; the pack asked six: all kept).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import process_chogath_fx as PC  # noqa: E402  symmetric_tb
import process_gnar_fx as G  # noqa: E402  centred
import process_powder_fx as PP  # noqa: E402  symmetric
import process_shyvana_fx as PS  # noqa: E402  key, down

OUT = os.path.join(ROOT, "assets", "source", "heimerdinger", "codex_fx", "heimerdinger_fx")
FLYING = {"a_bolt", "w_rocket", "t_shot", "t_beam_line", "x_shot"}   # turned with their flight: symmetric top to bottom
ROUNDS = {"e_grenade", "re_grenade", "t_muzzle", "x_muzzle"}          # symmetric both ways
FORWARD = {"w_flash"}                                                 # points forward, baked into his frames
G_ = "Gemini_Generated_Image_"
# file -> (effect, frames, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    G_ + "ik2tz7ik2tz7ik2t.jpg": ("a_bolt", 4, (10, 6)),
    G_ + "ik2tz7ik2tz7ik2t (1).jpg": ("a_hit", 3, (12, 12)),
    G_ + "ik2tz7ik2tz7ik2t (2).jpg": ("w_rocket", 3, (12, 6)),
    G_ + "ik2tz7ik2tz7ik2t (3).jpg": ("w_flash", 3, (10, 10)),
    G_ + "ik2tz7ik2tz7ik2t (4).jpg": ("w_hit", 4, (14, 14)),
    G_ + "ik2tz7ik2tz7ik2t (5).jpg": ("t_dust", 5, (30, 12)),
    G_ + "ik2tz7ik2tz7ik2t (6).jpg": ("t_muzzle", 3, (10, 10)),
    G_ + "ik2tz7ik2tz7ik2t (7).jpg": ("t_shot", 2, (8, 5)),
    G_ + "ik2tz7ik2tz7ik2t (8).jpg": ("t_hit", 3, (10, 10)),
    G_ + "ik2tz7ik2tz7ik2t (9).jpg": ("t_beam", 4, (26, 14)),
    G_ + "e1vq8ee1vq8ee1vq.jpg": ("t_beam_line", 3, (24, 6)),
    G_ + "e1vq8ee1vq8ee1vq (1).jpg": ("t_gone", 4, (24, 18)),
    G_ + "e1vq8ee1vq8ee1vq (2).jpg": ("e_grenade", 4, (9, 9)),
    G_ + "e1vq8ee1vq8ee1vq (3).jpg": ("e_blast", 6, (54, 36)),
    G_ + "e1vq8ee1vq8ee1vq (4).jpg": ("e_hit", 3, (14, 18)),
    G_ + "e1vq8ee1vq8ee1vq (5).jpg": ("e_slow", 4, (22, 8)),
    G_ + "e1vq8ee1vq8ee1vq (6).jpg": ("r_up", 6, (40, 36)),        # (7) is the same file
    G_ + "e1vq8ee1vq8ee1vq (8).jpg": ("re_grenade", 4, (11, 11)),
    G_ + "e1vq8ee1vq8ee1vq (9).jpg": ("re_blast", 7, (58, 42)),
    G_ + "e1vq8ee1vq8ee1vq (10).jpg": ("x_dust", 8, (40, 30)),
    G_ + "gf2f3zgf2f3zgf2f.jpg": ("x_muzzle", 3, (14, 14)),
    G_ + "gf2f3zgf2f3zgf2f (1).jpg": ("x_shot", 3, (12, 8)),
    G_ + "gf2f3zgf2f3zgf2f (2).jpg": ("x_hit", 4, (16, 16)),
    G_ + "gf2f3zgf2f3zgf2f (3).jpg": ("x_beam", 4, (32, 16)),
    G_ + "gf2f3zgf2f3zgf2f (4).jpg": ("x_gone", 5, (30, 26)),
    G_ + "gf2f3zgf2f3zgf2f (5).jpg": ("haste", 3, (20, 8)),
    G_ + "gf2f3zgf2f3zgf2f (6).jpg": ("dead_burst", 5, (34, 26)),
}
LAYOUT = {"e_blast": (2, 3)}                    # (rows, columns) where it is not one row of `frames` cells
XCUTS = {"x_dust": [(60, 800), (820, 1820), (1880, 2900), (2920, 4225), (4228, 4600), (4610, 5070), (5090, 5400),
                    (5450, 5856)]}              # one row cut at these x ranges (Gemini placed the frames unevenly)
KEY = {}
KEY_D = 40
THIN = {"t_dust": 0.35, "x_dust": 0.35, "e_slow": 0.35, "haste": 0.3, "e_blast": 0.35, "re_blast": 0.35,
        "t_beam": 0.4, "x_beam": 0.4, "t_beam_line": 0.45, "e_hit": 0.4}
K = 24
OVERLAP = 0.03


def lp(path):
    return G.lp(path)


def boxes(name, n, H, W):
    if name in XCUTS:
        return [(0, H, x0, x1) for x0, x1 in XCUTS[name]]
    rows, cols = LAYOUT.get(name, (1, n))
    out = []
    for r in range(rows):
        y0, y1 = round(r * H / rows), round((r + 1) * H / rows)
        for c in range(cols):
            x0, x1 = round(c * W / cols), round((c + 1) * W / cols)
            my, mx = int(OVERLAP * (y1 - y0)), int(OVERLAP * (x1 - x0))
            out.append((y0 + my, y1 - my, x0 + mx, x1 - mx))
    return out


def cells_of(img, name, n):
    rgb = np.asarray(img.convert("RGB"))
    H, W = rgb.shape[:2]
    out = []
    for y0, y1, x0, x1 in boxes(name, n, H, W):
        sub = rgb[y0:y1, x0:x1]
        fg = PS.key(sub, KEY.get(name, KEY_D))
        a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
        a4[..., :3] = sub
        a4[..., 3] = np.where(fg, 255, 0)
        out.append(a4)
    return out[:n]


def effect(name, n, size, img):
    ps = cells_of(img, name, n)
    if name not in FORWARD:
        # centred on the axis the symmetry needs (both ways for the round ones)
        ps = [G.centred(p, 0 if name in FLYING else 1) for p in ps]
        if name in ROUNDS:
            ps = [G.centred(p, 0) for p in ps]
    ys, xs = [], []
    for p in ps:
        yy, xx = np.nonzero(p[..., 3])
        if len(yy):
            ys += [yy.min(), yy.max()]
            xs += [xx.min(), xx.max()]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    cw, ch = size
    k = min(cw / (x1 - x0), ch / (y1 - y0))
    allpx = np.concatenate([p[y0:y1, x0:x1][p[y0:y1, x0:x1, 3] > 0][:, :4] for p in ps])
    rng = np.random.default_rng(0)
    sample = allpx[rng.choice(len(allpx), min(len(allpx), 60000), replace=False)]
    _, pal = V.kmeans(sample.reshape(1, -1, 4), K)
    pal_px = np.asarray(pal, int)[:, :3]
    frames = [PS.down(p, (y0, y1, x0, x1), k, pal_px, THIN.get(name, 0.5)) for p in ps]
    W, H = size
    cells = []
    for f in frames:
        c = np.zeros((H, W, 4), np.uint8)
        fh, fw = min(f.shape[0], H), min(f.shape[1], W)
        ox, oy = (W - fw) // 2, (H - fh) // 2
        c[oy:oy + fh, ox:ox + fw] = f[:fh, :fw]
        c[..., 3] = np.where(c[..., 3] >= 128, 255, 0)
        c[c[..., 3] == 0] = 0
        if name in FLYING:
            c = PC.symmetric_tb(c)
        elif name in ROUNDS:
            c = PC.symmetric_tb(PP.symmetric(c))
        elif name not in FORWARD:
            c = PP.symmetric(c)
        cells.append(c)
    while len(cells) > 1 and not cells[-1][..., 3].any():
        cells.pop()                              # a last frame too faint to survive the key
    return cells


def symmetry(name):
    return ("top-bottom" if name in FLYING else "both" if name in ROUNDS else "none (points right)" if name in FORWARD
            else "left-right")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/hd_work/gemini_fx")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, size) in SOURCES.items():
        cells = effect(name, n, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"heimerdinger_fx_{name}.png")))
        entries.append({"name": name, "file": f"heimerdinger_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": symmetry(name), "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries,
                   "made_by": "Gemini (the user's images), processed by tools/art/process_heimerdinger_fx.py"},
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
        path = os.path.join(a.review, "heimerdinger_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
