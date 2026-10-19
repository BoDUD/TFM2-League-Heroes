#!/usr/bin/env python3
"""Cho'Gath's effects drawn by Gemini (the user, 2026-10-19: the FX pack's 15 pictures came back as 15 JPGs in Downloads,
made in the pack's order) brought to the delivery import_chogath_fx.py reads:
assets/source/chogath/codex_fx/chogath_fx/pixel_1x/chogath_fx_<name>.png (one row of equal game-size frames, alpha 0/255)
+ manifest.json - process_powder_fx.py's way.

    python tools/art/process_chogath_fx.py [--src C:/t/cg_work/gemini_fx] [--review DIR]

The JPGs (kept locally in --src as 00.jpg .. 14.jpg in the order they were made; not committed) have no alpha and
backgrounds of every kind (SOURCES): black, black with grey boxes round the frames (e_pic), white (e_arm, e_hit,
q_slow), grey panels (q_spikes), a painted grey chequerboard (q_hit), black and grey panels side by side (r_grow).
Per picture: the background keyed (process_powder_fx.key), the picture cut into equal panels, all frames of an
effect cropped by one box (their union), brought down by votes to the pack's game size and made symmetric from the
fuller half - left to right, or top to bottom for the two pictures the game turns with their line (e_pic, w_wave).
Gemini drew three of them squarer than the pack asked (STRETCH: the spikes' volley in a box instead of along a
50-px line, Rupture's cracks round instead of a flat 50-px ground ellipse, Feral Scream's arcs tall and narrow
instead of a 55-px cone): their width and height are scaled apart to the asked size, so they cover what the kit hits.
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
import process_powder_fx as PP  # noqa: E402  key, panels, down, symmetric

OUT = os.path.join(ROOT, "assets", "source", "chogath", "codex_fx", "chogath_fx")
FLYING = {"e_pic", "w_wave"}                    # turned with their line: symmetric top to bottom
# file -> (effect, frames, background, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "00.jpg": ("a_hit", 3, "black", (16, 16)),
    "01.jpg": ("p_heal", 4, "black", (40, 36)),
    "02.jpg": ("e_arm", 4, "white", (48, 30)),
    "03.jpg": ("e_pic", 4, "boxed", (52, 18)),
    "04.jpg": ("e_hit", 3, "white", (14, 14)),
    "05.jpg": ("e_slow", 2, "black", (18, 8)),
    "06.jpg": ("q_crack", 6, "black", (54, 20)),
    "07.jpg": ("q_spikes", 6, "grey", (56, 46)),
    "08.jpg": ("q_hit", 3, "dark", (16, 16)),
    "09.jpg": ("q_slow", 2, "white", (24, 8)),
    "10.jpg": ("w_wave", 5, "black", (56, 32)),
    "11.jpg": ("w_hit", 3, "black", (16, 16)),
    "12.jpg": ("w_sil", 4, "black", (16, 13)),
    "13.jpg": ("r_hit", 5, "black", (32, 34)),
    "14.jpg": ("r_grow", 5, "mixed", (64, 48)),
}
STRETCH = {"e_pic", "q_crack", "w_wave"}
THIN = {"e_pic": 0.35, "q_crack": 0.3, "w_wave": 0.3, "r_grow": 0.3}   # thin lines: drawn from this coverage
K = 24                                                                # colours an effect is snapped to


def purple_haze(c):
    return c[2] >= c[0] and c[2] > c[1] and max(c) < 120


# squares dropped after the votes: Gemini's soft glows came down as dark muddy blobs (p_heal's void puff and its
# remnants, q_hit's haze), r_grow's light ring had a near-black outline (light has none)
DROP = {"p_heal": lambda c: max(c) < 100, "q_hit": purple_haze, "r_grow": lambda c: max(c) < 75}
# a thin bright line on a dark ground (q_slow's glowing cracks, ~10 % of a square): the square takes the line's colour
BRIGHT = {"q_slow": 0.1}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def panels(img, n, kind):
    if kind != "mixed":
        return PP.panels(img, n, kind)
    # black panels and grey panels side by side: keyed both ways
    a, b = PP.panels(img, n, "black"), PP.panels(img, n, "grey")
    out = []
    for p, q in zip(a, b):
        c = p.copy()
        c[..., 3] = np.where((p[..., 3] > 0) & (q[..., 3] > 0), 255, 0)
        out.append(c)
    return out


def symmetric_tb(c):
    """The fuller half mirrored onto the other (exactly symmetric top to bottom)."""
    h = c.shape[0]
    k = h // 2
    top, bottom = c[:k], c[h - k:]
    out = c.copy()
    if (top[..., 3] > 0).sum() >= (bottom[..., 3] > 0).sum():
        out[h - k:] = top[::-1]
    else:
        out[:k] = bottom[::-1]
    return out


def bright(p, box, out, pal_px, frac):
    """out (one panel's squares) with every drawn square holding at least frac of bright saturated pixels (a lit
    crack) in the commonest of their palette colours."""
    y0, y1, x0, x1 = box
    crop = p[y0:y1, x0:x1]
    H, W = crop.shape[:2]
    Hn, Wn = out.shape[:2]
    f = crop[..., :3].astype(int)
    lit = (crop[..., 3] > 0) & (f.max(-1) > 150) & (f.max(-1) - f.min(-1) > 60)
    out = out.copy()
    cy = np.minimum((np.arange(H) * Hn) // H, Hn - 1)
    cx = np.minimum((np.arange(W) * Wn) // W, Wn - 1)
    for j in range(Hn):
        for i in range(Wn):
            m = lit[cy == j][:, cx == i]
            if out[j, i, 3] and m.size and m.mean() >= frac:
                px = f[cy == j][:, cx == i][m]
                idx = ((px[:, None, :] - pal_px[None]) ** 2).sum(-1).argmin(1)
                out[j, i, :3] = pal_px[np.bincount(idx).argmax()]
    return out


def effect(name, n, kind, size, img):
    ps = panels(img, n, kind)
    ys, xs = [], []
    for p in ps:
        yy, xx = np.nonzero(p[..., 3])
        if len(yy):
            ys += [yy.min(), yy.max()]
            xs += [xx.min(), xx.max()]
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    cw, ch = size
    k = min(cw / (x1 - x0), ch / (y1 - y0))
    kx, ky = (cw / (x1 - x0), ch / (y1 - y0)) if name in STRETCH else (k, k)
    allpx = np.concatenate([p[y0:y1, x0:x1][p[y0:y1, x0:x1, 3] > 0][:, :4] for p in ps])
    rng = np.random.default_rng(0)
    sample = allpx[rng.choice(len(allpx), min(len(allpx), 60000), replace=False)]
    idx, pal = V.kmeans(sample.reshape(1, -1, 4), K)
    pal_px = np.asarray(pal, int)[:, :3]
    frames = [PP.down(p, (y0, y1, x0, x1), kx, ky, pal_px, THIN.get(name, 0.5)) for p in ps]
    if name in BRIGHT:
        frames = [bright(p, (y0, y1, x0, x1), f, pal_px, BRIGHT[name]) for p, f in zip(ps, frames)]
    cells = []
    for c in frames:
        c = c.copy()
        if name in DROP:
            gone = np.array([[DROP[name](tuple(int(v) for v in c[y, x, :3])) for x in range(c.shape[1])]
                             for y in range(c.shape[0])])
            c[gone] = 0
        c[..., 3] = np.where(c[..., 3] >= 128, 255, 0)
        c[c[..., 3] == 0] = 0
        cells.append(symmetric_tb(c) if name in FLYING else PP.symmetric(c))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/cg_work/gemini_fx")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, kind, size) in SOURCES.items():
        cells = effect(name, n, kind, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"chogath_fx_{name}.png")))
        entries.append({"name": name, "file": f"chogath_fx_{name}.png", "frames": n, "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {n} frames of {w}x{h}")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_chogath_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 6
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
        path = os.path.join(a.review, "chogath_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
