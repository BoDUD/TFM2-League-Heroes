#!/usr/bin/env python3
"""Powder's effects drawn by Gemini (the user, 2026-10-19: the FX pack's 14 pictures and 3 icons came back as 17 JPGs in
Downloads, 「完事了 你处理一下 然后导入吧」) brought to the delivery import_powder_fx.py reads:
assets/source/powder/codex_fx/powder_fx/pixel_1x/powder_fx_<name>.png (one row of equal game-size frames, alpha 0/255,
symmetric left to right but the three tumbling projectiles) + manifest.json, and pixel_1x/powder_icon_<slot>.png (64 x 64).

    python tools/art/process_powder_fx.py [--src C:/t/pw_work/gemini_fx] [--review DIR]

The JPGs (kept locally in --src as 00.jpg .. 16.jpg in the order they were made; not committed) have no alpha and
backgrounds of every kind: black, white with black panel bars, grey, a painted chequerboard. Per picture (SOURCES):
the background is keyed - white and grey flood-filled in from the border (a white core inside a glow stays), black
only near pure black (the near-black outlines of the solid things stay), a chequerboard by its low saturation - the
frames are the picture cut into equal panels, all frames of an effect cropped by one box (their union: a flash
keeps its place under the blast), brought down by votes to the pack's game size (pixel_down.pixelate, the frame's own
colours) and, unless the effect tumbles, made symmetric left to right from the fuller half (the client never mirrors
an effect picture). The icons: the whole square brought down to 64 x 64 and snapped to its own 32 colours.
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
import pixel_down as PD  # noqa: E402
import design_varus as V  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "powder", "codex_fx", "powder_fx")
TUMBLE = {"a_pop", "q_monkey", "r_bag"}
# file -> (effect, frames, background, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "00.jpg": ("a_pop", 4, "black", (10, 10)),
    "01.jpg": ("a_hit", 3, "black", (12, 12)),
    "02.jpg": ("q_monkey", 4, "grey", (16, 16)),
    "03.jpg": ("q_blast", 6, "grey", (40, 34)),
    "04.jpg": ("q_hit", 4, "grey", (16, 16)),
    "05.jpg": ("q_wound", 4, "grey", (14, 10)),
    "06.jpg": ("e_smoke", 6, "boxed", (40, 26)),
    "07.jpg": ("e_blind", 4, "dark", (16, 10)),
    "08.jpg": ("r_cast", 3, "white", (14, 14)),
    "09.jpg": ("r_bag", 4, "white", (16, 16)),
    "10.jpg": ("r_warn", 4, "black", (44, 16)),
    "11.jpg": ("r_fuse", 4, "black", (16, 18)),
    "12.jpg": ("r_blast", 6, "grey", (52, 42)),
    "13.jpg": ("r_hit", 3, "black", (14, 14)),
}
ICONS = {"14.jpg": "icon_skill", "15.jpg": "icon_skill2", "16.jpg": "icon_ult"}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def key(rgb, kind):
    """-> foreground mask of a picture with no alpha."""
    f = rgb.astype(int)
    mx, mn = f.max(-1), f.min(-1)
    lum = f.mean(-1)
    sat = mx - mn
    if kind == "black":
        bg = (mx < 22) | ((lum < 48) & (sat < 14))          # pure black and the dark grey panel bars
    elif kind == "boxed":                                    # black with dark violet frames round each panel
        bg = (mx < 22) | ((lum < 75) & (sat < 45))
    elif kind == "dark":
        bg = (lum < 70) & (sat < 20)                         # a black / dark grey chequerboard
    elif kind == "grey":
        bg = (sat < 18) & (lum > 40) & (lum < 175)           # grey or a painted grey chequerboard
    else:                                                    # white with black panel bars and boxes
        H, W = f.shape[:2]
        white = (lum > 225) & (sat < 25)
        lbl, n = ndimage.label(white)
        edge = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
        sizes = ndimage.sum(white, lbl, range(1, n + 1))
        big = {i + 1 for i, sz in enumerate(sizes) if sz > 0.015 * H * W}
        bg = np.isin(lbl, list(edge | big))                  # a small white core inside a glow stays
        dark = lum < 60
        lbl, n = ndimage.label(dark)
        for i, o in enumerate(ndimage.find_objects(lbl), 1):
            h, w = o[0].stop - o[0].start, o[1].stop - o[1].start
            if (h > 0.5 * H and w < 0.04 * W) or (w > 0.5 * W and h < 0.04 * H) or (h > 0.5 * H and w > 0.5 * W and
                                                                                      (lbl[o] == i).mean() < 0.2):
                bg |= lbl == i                               # the panel bars and box frames
    if kind == "grey":                                       # grey: flood too, so grey inside a thing stays
        lbl, _ = ndimage.label(bg)
        edge = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
        bg = np.isin(lbl, list(edge)) | (bg & (ndimage.binary_opening(bg, np.ones((5, 5), bool))))
    fg = ~bg
    fg = ndimage.binary_opening(fg, np.ones((3, 3), bool))   # JPEG fringe specks
    return fg


def panels(img, n, kind):
    rgb = np.asarray(img.convert("RGB"))
    fg = key(rgb, kind)
    H, W = fg.shape
    out = []
    for k in range(n):
        x0, x1 = round(k * W / n), round((k + 1) * W / n)
        a = np.zeros((H, x1 - x0, 4), np.uint8)
        a[..., :3] = rgb[:, x0:x1]
        m = fg[:, x0:x1].copy()
        m[:, :3] = False                                     # a panel bar on the cut
        m[:, -3:] = False
        a[..., 3] = np.where(m, 255, 0)
        out.append(a)
    return out


def symmetric(c):
    """The fuller half mirrored onto the other (exactly symmetric left to right)."""
    w = c.shape[1]
    h = w // 2
    left, right = c[:, :h], c[:, w - h:]
    if (left[..., 3] > 0).sum() >= (right[..., 3] > 0).sum():
        out = c.copy()
        out[:, w - h:] = left[:, ::-1]
    else:
        out = c.copy()
        out[:, :h] = right[:, ::-1]
    return out


THIN = {"r_warn": 0.2, "e_blind": 0.35, "r_hit": 0.35}   # thin lines and wisps: a square is drawn from this coverage
STRETCH = {"r_warn"}                                     # a flat ground ring: width and height scaled apart
K = 24                                                   # colours an effect is snapped to


def down(p, box, kx, ky, pal_px, need):
    """One panel brought to game squares: blocks of 1/kx x 1/ky source pixels over the box, each the commonest of the
    effect's K colours among its drawn pixels, drawn where `need` of it is drawn; the sparks too small to fill half a
    square come back as one square each (their brightest colour) where nothing else is drawn."""
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
    lbl, n = ndimage.label(op)
    for i, o in enumerate(ndimage.find_objects(lbl), 1):
        m = lbl[o] == i
        ys, xs = np.nonzero(m)
        ty = min(Hn - 1, int((ys.mean() + o[0].start) * Hn / H))
        tx = min(Wn - 1, int((xs.mean() + o[1].start) * Wn / W))
        sub = crop[o][m][:, :3].astype(int)
        bright = (sub.max(1) - sub.min(1)).max() > 60    # a coloured spark (dark blue motes too), not a grey JPEG speck
        if out[ty, tx, 3] == 0 and bright and m.sum() >= 0.08 * (H / Hn) * (W / Wn):
            col = sub[sub.sum(1).argmax()]
            out[ty, tx, :3] = pal_px[((pal_px - col) ** 2).sum(1).argmin()]
            out[ty, tx, 3] = 255
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
    frames = [down(p, (y0, y1, x0, x1), kx, ky, pal_px, THIN.get(name, 0.5)) for p in ps]
    W = max(f.shape[1] for f in frames)
    H = max(f.shape[0] for f in frames)
    W += (W % 2 == 0) and 0
    cells = []
    for f in frames:
        c = np.zeros((H, W, 4), np.uint8)
        oy, ox = (H - f.shape[0]) // 2, (W - f.shape[1]) // 2
        c[oy:oy + f.shape[0], ox:ox + f.shape[1]] = f
        c[..., 3] = np.where(c[..., 3] >= 128, 255, 0)
        c[c[..., 3] == 0] = 0
        cells.append(c if name in TUMBLE else symmetric(c))
    return cells


def icon(img):
    a = np.asarray(img.convert("RGB").resize((64, 64), Image.BOX)).copy()
    rgba = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    idx, pal = V.kmeans(rgba, 32)
    return np.dstack([pal[idx].astype(np.uint8), np.full(a.shape[:2], 255, np.uint8)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/pw_work/gemini_fx")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, kind, size) in SOURCES.items():
        cells = effect(name, n, kind, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"powder_fx_{name}.png")))
        entries.append({"name": name, "file": f"powder_fx_{name}.png", "frames": n, "cell_1x": [w, h],
                        "symmetry": "tumbling" if name in TUMBLE else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip))
        print(f"{name}: {n} frames of {w}x{h}")
    for fn, slot in ICONS.items():
        ic = icon(Image.open(lp(os.path.join(a.src, fn))))
        Image.fromarray(ic).save(lp(os.path.join(OUT, "pixel_1x", f"powder_{slot}.png")))
        sheets.append((slot, ic))
        print(f"{slot}: 64x64")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_powder_fx.py"},
                  f, ensure_ascii=False, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        Z = 6
        rows = []
        for name, s in sheets:
            z = 3 if name.startswith("icon") else Z
            im = Image.new("RGBA", (s.shape[1] * z, s.shape[0] * z), (40, 40, 52, 255))
            im.alpha_composite(Image.fromarray(s).resize((s.shape[1] * z, s.shape[0] * z), Image.NEAREST))
            rows.append(im)
        W = max(r.width for r in rows)
        sheet = Image.new("RGBA", (W, sum(r.height + 10 for r in rows)), (20, 20, 26, 255))
        y = 0
        for r in rows:
            sheet.alpha_composite(r, (0, y))
            y += r.height + 10
        path = os.path.join(a.review, "powder_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path)


if __name__ == "__main__":
    main()
