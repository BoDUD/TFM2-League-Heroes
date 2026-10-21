#!/usr/bin/env python3
"""Shyvana's effects drawn by Gemini (the user, 2026-10-21: the FX pack's 26 pictures came back as JPGs in Downloads,
「龙女的技能特效在这里面」, made in the pack's order; 30 files, four of them byte-for-byte copies) brought to the
delivery import_shyvana_fx.py reads: assets/source/shyvana/codex_fx/shyvana_fx/pixel_1x/shyvana_fx_<name>.png (one row of
equal game-size frames, alpha 0/255) + manifest.json - process_gnar_fx.py's way (its keying, cutting and voting).

    python tools/art/process_shyvana_fx.py [--src C:/t/sv_work/gemini] [--review DIR]

The JPGs (kept locally in --src as g00.jpg .. g25.jpg in the order they were made, the copies dropped; not committed)
have no alpha and backgrounds of every kind (black, white, a painted chequerboard, grey panels, divider lines); every
cell is keyed by flooding in from its own border (process_gnar_fx.key_cell). All frames of an effect cropped by one box
(their union), brought down by votes to the pack's game size in the effect's own K colours, made symmetric from the
fuller half - left to right, top to bottom for the three projectiles the game turns with their flight (e_ball, de_ball,
r_breath), not at all for the two slashes that point forward and are baked into her frames (q_slash, d_q_slash).
Gemini's layout: w_blast two rows of six (the second a variant: dropped), de_blast two rows of three, r_breath two of
two, r_land three rows of three (all nine kept - the pack asked six), e_slow six frames (the pack asked four: kept).
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
import process_gnar_fx as G  # noqa: E402  key_cell, centred
import process_powder_fx as PP  # noqa: E402  symmetric

OUT = os.path.join(ROOT, "assets", "source", "shyvana", "codex_fx", "shyvana_fx")
FLYING = {"e_ball", "de_ball", "r_breath"}       # turned with their flight: drawn flying right, symmetric top to bottom
FORWARD = {"q_slash", "d_q_slash"}               # point forward, baked into her frames: no symmetry
# file -> (effect, frames, game size (w, h) from PROMPTS_FX.md)
SOURCES = {
    "g00.jpg": ("a_hit", 3, (12, 12)), "g01.jpg": ("q_slash", 4, (30, 22)), "g02.jpg": ("d_q_slash", 4, (48, 34)),
    "g03.jpg": ("q_hit", 3, (14, 14)), "g04.jpg": ("q2_wave", 5, (60, 24)), "g05.jpg": ("d_q2_wave", 5, (90, 34)),
    "g06.jpg": ("q2_hit", 3, (12, 12)), "g07.jpg": ("q3_hit", 4, (16, 16)), "g08.jpg": ("w_aegis", 6, (44, 50)),
    "g09.jpg": ("w_blast", 6, (72, 46)), "g10.jpg": ("w_hit", 3, (12, 12)), "g11.jpg": ("w_heal", 5, (26, 30)),
    "g12.jpg": ("e_ball", 4, (16, 10)), "g13.jpg": ("e_hit", 3, (12, 12)), "g14.jpg": ("e_blast", 5, (34, 30)),
    "g15.jpg": ("de_ball", 4, (26, 16)), "g16.jpg": ("de_hit", 3, (14, 14)), "g17.jpg": ("de_blast", 6, (64, 44)),
    "g18.jpg": ("de_singe", 3, (10, 12)), "g19.jpg": ("e_slow", 6, (16, 8)), "g20.jpg": ("r_breath", 4, (44, 20)),
    "g21.jpg": ("r_hit", 4, (14, 18)), "g22.jpg": ("r_land", 9, (86, 36)), "g23.jpg": ("tf_dragon", 6, (64, 64)),
    "g24.jpg": ("tf_human", 5, (48, 48)), "g25.jpg": ("fury_full", 4, (30, 44)),
}
# (rows, columns) of the picture's grid where it is not one row of `frames` cells; the cells read row by row
LAYOUT = {"w_blast": (2, 6), "de_blast": (2, 3), "r_breath": (2, 2), "r_land": (3, 3)}
KEY = {"tf_human": 70}                           # colour distance to a border colour that floods (default KEY_D);
KEY_D = 40                                       # tf_human's flash sits in a dark glow fading to the black ground
THIN = {"q2_wave": 0.35, "d_q2_wave": 0.35, "r_land": 0.35, "w_blast": 0.4, "e_slow": 0.35, "w_heal": 0.35,
        "w_aegis": 0.25}                         # the shield's bubble is a line a third of a square wide
K = 24
OVERLAP = 0.03                                   # each cell's border band ignored (Gemini's dividers sit on the cuts)


def lp(path):
    return G.lp(path)


def key(sub, dist):
    """process_gnar_fx's key flooding only from the border's grey colours (black, white, a chequerboard, a panel: where
    a drawing reaches the border its colours are no ground - the shield's pale bubble went with them), and on a dark
    ground every pixel of the ground's colour wherever it is: the black a ring, a bubble or the gaps between smoke
    puffs close in (fire is outlined in dark red, never in the ground's black)."""
    cols = G.border_colours(sub)
    grey = cols[cols.max(1) - cols.min(1) < 60]
    cols = grey if len(grey) else cols
    fg = G.key_cell(sub, dist, cols)
    dark = cols[cols.mean(1) < 60]
    if len(dark):
        f = sub.astype(float)
        near = (((f[:, :, None, :] - dark[None, None]) ** 2).sum(-1) <= dist ** 2).any(-1)
        fg &= ~near
        fg = ndimage.binary_opening(fg, np.ones((3, 3), bool))
    return fg


def down(p, box, k, pal_px, need):
    """process_powder_fx.down (blocks voted to the effect's colours, drawn where `need` of them is drawn; sparks too
    small for that come back as one square each), the sparks only blobs at most two squares across: a whole ring is one
    blob whose middle is empty, and powder's way put a square in every ring's middle."""
    y0, y1, x0, x1 = box
    crop = p[y0:y1, x0:x1]
    H, W = crop.shape[:2]
    Wn, Hn = max(1, round(W * k)), max(1, round(H * k))
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
    ok = counts.sum(1) >= need * np.maximum(tot, 1)
    out.reshape(-1, 4)[ok, :3] = pal_px[counts.argmax(1)[ok]]
    out.reshape(-1, 4)[ok, 3] = 255
    lbl, _ = ndimage.label(op)
    sq_y, sq_x = H / Hn, W / Wn
    for i, o in enumerate(ndimage.find_objects(lbl), 1):
        if o[0].stop - o[0].start > 2 * sq_y or o[1].stop - o[1].start > 2 * sq_x:
            continue
        m = lbl[o] == i
        ys, xs = np.nonzero(m)
        ty = min(Hn - 1, int((ys.mean() + o[0].start) * Hn / H))
        tx = min(Wn - 1, int((xs.mean() + o[1].start) * Wn / W))
        sub = crop[o][m][:, :3].astype(int)
        bright = (sub.max(1) - sub.min(1)).max() > 60
        if out[ty, tx, 3] == 0 and bright and m.sum() >= 0.08 * sq_y * sq_x:
            col = sub[sub.sum(1).argmax()]
            out[ty, tx, :3] = pal_px[((pal_px - col) ** 2).sum(1).argmin()]
            out[ty, tx, 3] = 255
    return out


def boxes(name, n, H, W):
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
        fg = key(sub, KEY.get(name, KEY_D))
        a4 = np.zeros(sub.shape[:2] + (4,), np.uint8)
        a4[..., :3] = sub
        a4[..., 3] = np.where(fg, 255, 0)
        out.append(a4)
    return out[:n]                               # w_blast: the first row's six


def effect(name, n, size, img):
    ps = cells_of(img, name, n)
    if name not in FORWARD:
        ps = [G.centred(p, 0 if name in FLYING else 1) for p in ps]
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
    frames = [down(p, (y0, y1, x0, x1), k, pal_px, THIN.get(name, 0.5)) for p in ps]
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
        elif name not in FORWARD:
            c = PP.symmetric(c)
        cells.append(c)
    while len(cells) > 1 and not cells[-1][..., 3].any():
        cells.pop()                              # a last frame too faint to survive the key
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="C:/t/sv_work/gemini")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    entries, sheets = [], []
    for fn, (name, n, size) in SOURCES.items():
        cells = effect(name, n, size, Image.open(lp(os.path.join(a.src, fn))))
        h, w = cells[0].shape[:2]
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(lp(os.path.join(OUT, "pixel_1x", f"shyvana_fx_{name}.png")))
        entries.append({"name": name, "file": f"shyvana_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                        "symmetry": "top-bottom" if name in FLYING else "none (points right)" if name in FORWARD
                        else "left-right", "source": f"gemini {fn}"})
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": entries, "made_by": "Gemini (the user's images), processed by tools/art/process_shyvana_fx.py"},
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
        path = os.path.join(a.review, "shyvana_fx_processed.png")
        sheet.convert("RGB").save(path)
        print(path, sheet.size)


if __name__ == "__main__":
    main()
