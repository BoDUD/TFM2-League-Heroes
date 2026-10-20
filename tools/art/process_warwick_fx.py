#!/usr/bin/env python3
"""Warwick's effects drawn by Gemini (the user, 2026-10-20: the FX pack's ten pictures as ten JPGs in Downloads, made in
the pack's order) brought to the delivery import_warwick_fx.py reads:
assets/source/warwick/codex_fx/warwick_fx/pixel_1x/warwick_fx_<name>.png (one row of equal game-size frames, alpha
0/255) + manifest.json - process_graves_fx.py's way.

    python tools/art/process_warwick_fx.py [--src C:/t/ww_work/gemini] [--review DIR]

The JPGs (kept locally in --src as g00.jpg .. g09.jpg in the order they were made; not committed) have no alpha. Gemini
laid some out as one row of panels and some as a grid (SOURCES: columns x rows, the frames read row by row); their
backgrounds: black (with grey or white bars between the panels), a flat grey (e_fear), a dark grey with black boxes
where the champion stands (r_bind: both are ground), a painted black / grey chequerboard (r_hit: both greys are ground). Per picture: the
background keyed, the picture cut into its panels (a margin off each cut: the bars), all frames of an effect cropped by
one box (their union), brought down by votes to the pack's game size (STRETCH: the flat ground ones scaled apart to the
asked width and height) and made symmetric left to right from the fuller half (the game never mirrors an effect).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import process_powder_fx as PP  # noqa: E402  key, symmetric, down

OUT = os.path.join(ROOT, "assets", "source", "warwick", "codex_fx", "warwick_fx")
# file -> (effect, columns, rows, background, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "g00.jpg": ("a_hit", 3, 1, "black", (18, 20)),
    "g01.jpg": ("q_hit", 5, 1, "black", (22, 22)),
    "g02.jpg": ("q_heal", 5, 1, "black", (44, 50)),
    "g03.jpg": ("e_guard", 2, 2, "black", (64, 54)),
    "g04.jpg": ("e_howl", 2, 3, "black", (88, 32)),
    "g05.jpg": ("e_roar", 3, 2, "black", (44, 26)),
    "g06.jpg": ("e_fear", 6, 1, "grey", (16, 14)),
    "g07.jpg": ("r_bind", 8, 1, "greybox", (28, 36)),
    "g08.jpg": ("r_hit", 4, 1, "checker", (24, 24)),
    "g09.jpg": ("w_hunt", 2, 2, "black", (52, 22)),
}
STRETCH = {"e_howl", "w_hunt", "e_guard"}       # flat on the ground / round him: width and height scaled apart
FILL = {"q_hit", "e_fear"}                      # solid shapes whose dark inside is body, not ground
THIN = {"a_hit": 0.22, "r_hit": 0.35, "e_roar": 0.4, "e_howl": 0.35, "r_bind": 0.35, "q_heal": 0.35, "e_guard": 0.35}
K = 24


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(rgb, kind):
    """-> the foreground mask of a picture with no alpha."""
    f = rgb.astype(int)
    sat = f.max(-1) - f.min(-1)
    lum = f.mean(-1)
    if kind == "greybox":                       # dark grey ground and black boxes: every grey and black is ground
        return ~((sat < 22) & (lum < 120))
    if kind == "checker":                       # a painted black / grey chequerboard: both of its greys are ground
        return ~((sat < 26) & (lum < 125))
    return PP.key(rgb, kind)


def panels(img, cols, rows, kind, fill):
    rgb = np.asarray(img.convert("RGB"))
    fg = key(rgb, kind)
    H, W = fg.shape
    out = []
    for r in range(rows):
        for c in range(cols):
            y0, y1 = round(r * H / rows), round((r + 1) * H / rows)
            x0, x1 = round(c * W / cols), round((c + 1) * W / cols)
            a = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
            a[..., :3] = rgb[y0:y1, x0:x1]
            m = fg[y0:y1, x0:x1].copy()
            mx, my = max(4, (x1 - x0) // 60), max(4, (y1 - y0) // 60)
            m[:, :mx] = False                   # a panel bar on the cut
            m[:, -mx:] = False
            m[:my] = False
            m[-my:] = False
            m = ndimage.binary_opening(m, iterations=1)
            if fill:
                m = ndimage.binary_fill_holes(m)
            a[..., 3] = np.where(m, 255, 0)
            out.append(a)
    return out


def down(p, box, kx, ky, pal_px, need):
    """process_powder_fx.down, its sparks rule kept to sparks: a component of the picture too small to fill half a
    square comes back as one square at its middle - only when it IS small (at most two squares' worth of pixels: the
    rule put a dot in the empty middle of every ring and ellipse)."""
    y0, y1, x0, x1 = box
    crop = p[y0:y1, x0:x1]
    H, W = crop.shape[:2]
    Wn, Hn = max(1, round(W * kx)), max(1, round(H * ky))
    op = crop[..., 3] > 0
    idx = np.full(op.shape, -1)
    if op.any():
        px = crop[op][:, :3].astype(int)
        idx[op] = ((px[:, None, :] - pal_px[None]) ** 2).sum(-1).argmin(1)
    cy = np.minimum((np.arange(H) * Hn) // H, Hn - 1)
    cx = np.minimum((np.arange(W) * Wn) // W, Wn - 1)
    out = np.zeros((Hn, Wn, 4), np.uint8)
    cell = cy[:, None] * Wn + cx[None, :]
    tot = np.bincount(cell.ravel(), minlength=Hn * Wn)
    counts = np.zeros((Hn * Wn, len(pal_px)), int)
    np.add.at(counts, (cell[op], idx[op]), 1)
    drawn = counts.sum(1)
    best = counts.argmax(1)
    ok = drawn >= need * np.maximum(tot, 1)
    out.reshape(-1, 4)[ok, :3] = pal_px[best[ok]]
    out.reshape(-1, 4)[ok, 3] = 255
    sq = (H / Hn) * (W / Wn)
    lbl, n = ndimage.label(op)
    for i, o in enumerate(ndimage.find_objects(lbl), 1):
        m = lbl[o] == i
        if m.sum() > 2 * sq:
            continue
        ys, xs = np.nonzero(m)
        ty = min(Hn - 1, int((ys.mean() + o[0].start) * Hn / H))
        tx = min(Wn - 1, int((xs.mean() + o[1].start) * Wn / W))
        sub = crop[o][m][:, :3].astype(int)
        bright = (sub.max(1) - sub.min(1)).max() > 60
        if out[ty, tx, 3] == 0 and bright and m.sum() >= 0.08 * sq:
            col = sub[sub.sum(1).argmax()]
            out[ty, tx, :3] = pal_px[((pal_px - col) ** 2).sum(1).argmin()]
            out[ty, tx, 3] = 255
    return out


def effect(name, cols, rows, kind, size, img):
    ps = panels(img, cols, rows, kind, fill=name in FILL)
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
    frames = [down(p, (y0, y1, x0, x1), kx, ky, pal_px, THIN.get(name, 0.5)) for p in ps]
    cells = []
    for c in frames:
        c = c.copy()
        c[..., 3] = np.where(c[..., 3] >= 128, 255, 0)
        c[c[..., 3] == 0] = 0
        cells.append(PP.symmetric(c))
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/ww_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, cols, rows, kind, size) in SOURCES.items():
        n = cols * rows
        cells = effect(name, cols, rows, kind, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"warwick_fx_{name}.png")))
        entries.append({"name": name, "file": f"warwick_fx_{name}.png", "frames": n, "cell_1x": [w, h],
                        "symmetry": "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {n} frames of {w}x{h}")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_warwick_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        Z = 6
        rows_ = []
        for name, s, w in sheets:
            n = s.shape[1] // w
            im = Image.new("RGBA", ((s.shape[1] + 2 * n) * Z, s.shape[0] * Z), (40, 40, 52, 255))
            for k in range(n):
                cell = s[:, k * w:(k + 1) * w]
                bg = Image.new("RGBA", (w * Z, s.shape[0] * Z), (70, 74, 60, 255))
                bg.alpha_composite(Image.fromarray(cell).resize((w * Z, s.shape[0] * Z), Image.NEAREST))
                im.alpha_composite(bg, (k * (w + 2) * Z, 0))
            rows_.append((name, im))
        W = max(r.width for _, r in rows_) + 110
        sheet = Image.new("RGBA", (W, sum(r.height + 12 for _, r in rows_)), (20, 20, 26, 255))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows_:
            sheet.alpha_composite(r, (110, y))
            d.text((4, y + 4), name, fill=(255, 255, 255, 255))
            y += r.height + 12
        path = os.path.join(a.review, "warwick_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
