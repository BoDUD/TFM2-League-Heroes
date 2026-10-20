#!/usr/bin/env python3
"""Graves's effects drawn by Gemini (the user, 2026-10-20: 「男枪的特效在这里」 - the FX pack's 16 pictures as 16 JPGs in
Downloads, made in the pack's order) brought to the delivery import_graves_fx.py reads:
assets/source/graves/codex_fx/graves_fx/pixel_1x/graves_fx_<name>.png (one row of equal game-size frames, alpha 0/255)
+ manifest.json - process_chogath_fx.py's way (itself process_powder_fx.py's).

    python tools/art/process_graves_fx.py [--src C:/t/gv_work/gemini_fx] [--review DIR]

The JPGs (kept locally in --src as 00.jpg .. 15.jpg in the order they were made; not committed) have no alpha. Their
backgrounds (SOURCES): black; black with dark grey bars between the panels (a_hit, r_blast); white (r_flash); a black
to grey gradient under the bomb (q_blast: keyed against each row's own background, the bomb's dark body kept by its
outline - holes filled); black under dark smoke (w_smoke, w_slow: only the near-pure black keyed, the smoke's darkest
grey-green stays). Per picture: the background keyed, the picture cut into equal panels, the shotgun's barrel Gemini
drew at the muzzle blasts' left edge taken off (BARREL: its dark steel and the gold ring next to it - our own gun is
under them in his frames), all frames of an effect cropped by one box (their union), brought down by votes to the
pack's game size (STRETCH: the flat ground ones scaled apart to the asked width and height) and made symmetric from
the fuller half - left to right; top to bottom for the projectiles (the game turns them); both ways for the tumbling
canister; not at all for the muzzle blasts, which point right and go into his own frames (the game mirrors those).
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
import process_chogath_fx as PC  # noqa: E402  symmetric_tb
import process_powder_fx as PP  # noqa: E402  key, symmetric, down

OUT = os.path.join(ROOT, "assets", "source", "graves", "codex_fx", "graves_fx")
FLYING = {"a_shot", "q_shell", "r_shell"}       # turned with their flight: symmetric top to bottom
BOTH = {"w_can"}                                # symmetric both ways
BAKED = {"a_flash", "q_flash", "r_flash"}       # pointing right, drawn into his frames: no symmetry
# file -> (effect, frames, background, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "00.jpg": ("a_flash", 3, "black", (16, 12)),
    "01.jpg": ("a_shot", 2, "black", (8, 4)),
    "02.jpg": ("a_hit", 3, "black", (12, 12)),
    "03.jpg": ("q_flash", 4, "black", (20, 14)),
    "04.jpg": ("q_shell", 2, "black", (12, 6)),
    "05.jpg": ("q_hit", 3, "black", (14, 14)),
    "06.jpg": ("q_blast", 9, "rows", (48, 40)),
    "07.jpg": ("w_can", 2, "black", (6, 6)),
    "08.jpg": ("w_smoke", 8, "deep", (52, 34)),
    "09.jpg": ("w_slow", 2, "deep", (16, 6)),
    "10.jpg": ("e_dust", 4, "black", (26, 10)),
    "11.jpg": ("e_grit", 2, "black", (32, 10)),
    "12.jpg": ("r_flash", 4, "white", (28, 18)),
    "13.jpg": ("r_shell", 2, "black", (18, 8)),
    "14.jpg": ("r_hit", 4, "black", (20, 20)),
    "15.jpg": ("r_blast", 5, "black", (50, 38)),
}
STRETCH = {"e_grit", "w_slow", "e_dust"}        # flat on the ground: width and height scaled apart
BARREL = {"a_flash", "q_flash", "r_flash"}      # Gemini drew the gun's barrel at the blast's left edge
RINGS = {"e_grit", "r_hit"}                     # rings: their middle is ground, not a dark body to fill
THIN = {"e_grit": 0.35, "a_shot": 0.4, "w_slow": 0.4}
K = 24


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(rgb, kind):
    """-> the foreground mask of a picture with no alpha."""
    f = rgb.astype(int)
    if kind == "deep":                          # black under dark smoke: only the near-pure black is ground
        fg = f.max(-1) >= 16
    elif kind == "rows":                        # a black-to-grey gradient: each row against its own ground (its margins)
        H, W = f.shape[:2]
        m = max(8, W // 80)
        ground = np.median(np.concatenate([f[:, :m], f[:, -m:]], axis=1), axis=1)
        fg = np.abs(f - ground[:, None, :]).max(-1) > 14
        fg = ndimage.binary_opening(fg, iterations=1)
    else:
        fg = PP.key(rgb, kind)                  # process_powder_fx.key: the foreground mask itself
    return fg


def panels(img, n, kind, fill=True):
    rgb = np.asarray(img.convert("RGB"))
    fg = key(rgb, kind)
    H, W = fg.shape
    out = []
    for k in range(n):
        x0, x1 = round(k * W / n), round((k + 1) * W / n)
        a = np.zeros((H, x1 - x0, 4), np.uint8)
        a[..., :3] = rgb[:, x0:x1]
        m = fg[:, x0:x1].copy()
        m[:, :3] = False                        # a panel bar on the cut
        m[:, -3:] = False
        if fill:
            m = ndimage.binary_fill_holes(m)    # a dark body inside its outline (the bomb, the canister)
        a[..., 3] = np.where(m, 255, 0)
        out.append(a)
    return out


def no_barrel(p):
    """A muzzle blast's panel without the gun Gemini drew at its left edge: the barrel's dark steel - very dark, little
    colour, in the band of rows round the panel's middle, reaching the panel's left edge (its piece touches the left
    sixth: grey smoke puffs further right stay) - and the gold ring touching it."""
    a = p.copy()
    f = a[..., :3].astype(int)
    op = a[..., 3] > 0
    H, W = op.shape
    lum, sat = f.mean(-1), f.max(-1) - f.min(-1)
    dark = op & (lum < 70) & (sat < 40)
    dark[:int(H * 0.3)] = False
    dark[int(H * 0.7):] = False
    lbl, n = ndimage.label(dark)
    steel = np.zeros_like(op)
    for i in range(1, n + 1):
        piece = lbl == i
        xs = np.nonzero(piece.any(0))[0]
        if xs.min() <= W // 6:
            steel |= piece
    if not steel.any():
        return a
    ys, xs = np.nonzero(steel)
    y0, y1, x1 = ys.min(), ys.max(), xs.max()
    gold = op & (f[..., 0] > 140) & (f[..., 2] < 110) & (sat > 70)
    band = np.zeros_like(op)
    band[max(0, y0 - 4):y1 + 5, :x1 + max(6, W // 16)] = True
    lbl, n = ndimage.label(gold & band)
    ring = np.zeros_like(op)
    for i in range(1, n + 1):
        piece = lbl == i
        if ndimage.binary_dilation(piece, iterations=3)[steel].any():   # touching the steel: the muzzle's ring
            ring |= piece
    gone = steel | ring
    a[gone] = 0
    return a


def effect(name, n, kind, size, img):
    ps = panels(img, n, kind, fill=name not in RINGS)
    if name in BARREL:
        ps = [no_barrel(p) for p in ps]
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
    cells = []
    for c in frames:
        c = c.copy()
        c[..., 3] = np.where(c[..., 3] >= 128, 255, 0)
        c[c[..., 3] == 0] = 0
        if name in BAKED:
            pass
        elif name in FLYING:
            c = PC.symmetric_tb(c)
        elif name in BOTH:
            c = PC.symmetric_tb(PP.symmetric(c))
        else:
            c = PP.symmetric(c)
        cells.append(c)
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/gv_work/gemini_fx")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, kind, size) in SOURCES.items():
        cells = effect(name, n, kind, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"graves_fx_{name}.png")))
        sym = ("none (points right)" if name in BAKED else "top-bottom" if name in FLYING else
               "both" if name in BOTH else "left-right")
        entries.append({"name": name, "file": f"graves_fx_{name}.png", "frames": n, "cell_1x": [w, h],
                        "symmetry": sym, "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {n} frames of {w}x{h}")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_graves_fx.py"},
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
        path = os.path.join(a.review, "graves_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
