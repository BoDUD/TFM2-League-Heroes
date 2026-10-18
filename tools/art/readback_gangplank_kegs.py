#!/usr/bin/env python3
"""Read Codex's bigger kegs (the redraw for 「桶最大点吧 也太小了」) back from the raw drafts into pixel_1x/.

    python tools/art/readback_gangplank_kegs.py [--review out.png]

Codex's own 1x read-back of the redraw snapped the drafts to a pale wood ramp: the barrel came out beige and the skull a
white blob, though the drafts are warm orange wood with a clear skull. Here every frame is cut from its draft
(manifest `source_regions`), the black backdrop keyed off from the edges, and sampled on the delivered cell grid
(`cell_1x`): the figure's height fills ROWS[name] cells from the cell's bottom row (e_throw: its width fills COLS),
every cell takes the commonest colour of its draft pixels after snapping them to the drafts' own palette (k-means), and is
figure when at least 40% of it is. Then the left half is mirrored (top half for the flying keg), the outline closed
(strips.complete_outline), and the lit keg takes the plain keg's barrel square for square (only the fuse's sparks and
the glow outside the barrel are its own). Writes assets/source/gangplank/codex_fx/pixel_1x/gangplank_fx_<name>.png.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gangplank", "codex_fx")
PRE = chr(92) * 2 + "?" + chr(92)
ROWS = {"e_keg": 21, "e_keg_lit": 24}          # the figure's height in cells (the cell is 22 / 25: one row spare)
COLS = {"e_throw": 13}                          # the flying keg's length in cells (the cell is 16)
K = 18                                          # the drafts' palette size


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def frames(meta):
    raw = np.asarray(Image.open(lp(os.path.join(SRC, meta["raw_file"]))).convert("RGBA")).copy()
    out = []
    for r in meta["source_regions"]:
        x0, y0, x1, y1 = r["source_slot"]
        a = raw[y0:y1, x0:x1].copy()
        dark = a[..., :3].max(-1) < 14
        lbl, _ = ndimage.label(dark)
        edge = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
        a[np.isin(lbl, list(edge)), 3] = 0
        out.append(a)
    return out


def palette(arrs):
    px = np.concatenate([a[a[..., 3] > 0][:, :3] for a in arrs]).astype(float)
    rng = np.random.default_rng(1)
    px = px[rng.choice(len(px), min(len(px), 60000), replace=False)]
    c = px[np.linspace(0, len(px) - 1, K).astype(int)]
    for _ in range(25):
        lab = ((px[:, None] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(K):
            if (lab == j).any():
                c[j] = px[lab == j].mean(0)
    return c


def sample(a, cell, pal, rows=None, cols=None):
    """a's figure on a cell grid: the figure's height (or width) spans rows (cols) cells; bottom-centred (centred)."""
    W, H = cell
    ys, xs = np.nonzero(a[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    p = (y1 - y0) / rows if rows else (x1 - x0) / cols
    lab = ((a[..., :3].astype(float)[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    out = np.zeros((H, W, 4), np.uint8)
    cx = (x0 + x1) / 2
    for j in range(H):
        for i in range(W):
            if rows:
                ya, yb = y1 - (H - j) * p, y1 - (H - j - 1) * p
            else:
                cy = (y0 + y1) / 2
                ya, yb = cy + (j - H / 2) * p, cy + (j + 1 - H / 2) * p
            xa, xb = cx + (i - W / 2) * p, cx + (i + 1 - W / 2) * p
            ya, yb, xa, xb = (int(round(v)) for v in (ya, yb, xa, xb))
            if yb <= 0 or xb <= 0 or ya >= a.shape[0] or xa >= a.shape[1]:
                continue
            blk = a[max(ya, 0):yb, max(xa, 0):xb]
            m = blk[..., 3] > 0
            if m.mean() < 0.4:
                continue
            ids = lab[max(ya, 0):yb, max(xa, 0):xb][m]
            out[j, i, :3] = pal[np.bincount(ids, minlength=K).argmax()].round().astype(np.uint8)
            out[j, i, 3] = 255
    return out


def mirror(c, top_bottom=False):
    if top_bottom:
        h = c.shape[0]
        c[h - h // 2:] = c[:h // 2][::-1]
    else:
        w = c.shape[1]
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
    return c


# the skull and crossbones, 6 x 7 squares on the front plank (W bone, d the eyes); "." = the plank's wood
SKULL = [".WWWW.",
         "WWWWWW",
         "WdWWdW",
         ".WWWW.",
         "W.WW.W",
         ".W..W.",
         "W....W"]
SPARKS = [["..YY..",       # frame 1: a white-hot core, orange round it
           ".OWWO.",
           "..OO.."],
          [".O..O.",       # frame 2: the flicker
           "..YY..",
           ".OWWO."]]
FIRE = {"W": (255, 246, 196), "Y": (255, 204, 64), "O": (255, 122, 32)}


def near(pal, rgb):
    return tuple(int(v) for v in pal[((pal - np.array(rgb, float)) ** 2).sum(1).argmin()].round())


def touch_up(c, pal):
    """The keg at 20 x 22: the front plank repainted with a crisp skull, the fuse a straight 2-square rope."""
    c = c.copy()
    H, W = c.shape[:2]
    lum = c[..., :3].astype(int).sum(-1)
    white = (c[..., 3] > 0) & (c[..., :3].min(-1) > 215)
    ys, xs = np.nonzero(white)
    cy = int(round(ys.mean()))
    wood = near(pal, (200, 110, 45))
    bone = near(pal, (240, 236, 228))
    eye = tuple(int(v) for v in pal[np.argmin(pal.sum(1))].round())
    rope = near(pal, (214, 170, 110))
    x0 = W // 2 - 3
    y0 = cy - 3
    for j, row in enumerate(SKULL):
        for i, ch in enumerate(row):
            c[y0 + j, x0 + i, :3] = {"W": bone, "d": eye, ".": wood}[ch]
            c[y0 + j, x0 + i, 3] = 255
    # the fuse: everything over the barrel's rim cleared, a 2-square rope up from the rim with an outline
    top = np.nonzero((c[..., 3] > 0).any(1))[0][0]
    rim = next(y for y in range(H) if (c[y, :, 3] > 0).sum() >= 6)
    c[top:rim] = 0
    for y in range(rim - 2, rim):
        c[y, W // 2 - 1:W // 2 + 1] = rope + (255,)
        c[y, W // 2 - 2] = eye + (255,)
        c[y, W // 2 + 1] = eye + (255,)
    c[rim - 3, W // 2 - 1:W // 2 + 1] = eye + (255,)
    c[rim, W // 2 - 1:W // 2 + 1] = rope + (255,)
    return c


def sparks(body, cell, k):
    """The lit keg: the plain keg's barrel at the cell's bottom and frame k's sparks over the fuse."""
    W, H = cell
    out = np.zeros((H, W, 4), np.uint8)
    out[H - body.shape[0]:] = body
    fuse = np.nonzero((out[..., 3] > 0).any(1))[0][0]
    pat = SPARKS[k % len(SPARKS)]
    x0 = W // 2 - 3
    for j, row in enumerate(pat):
        for i, ch in enumerate(row):
            if ch != ".":
                out[fuse - len(pat) + j, x0 + i] = FIRE[ch] + (255,)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    man = {e["name"][13:]: e for e in json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))["assets"]}
    fr = {n: frames(man[n]) for n in ("e_keg", "e_keg_lit", "e_throw")}
    pal = palette([f for v in fr.values() for f in v])
    dark = tuple(int(v) for v in pal[np.argmin(pal.sum(1))].round())
    res = {}
    for n, fs in fr.items():
        cell = man[n]["cell_1x"]
        out = []
        for f in fs:
            c = sample(f, cell, pal, rows=ROWS.get(n), cols=COLS.get(n))
            c = mirror(c, top_bottom=(n == "e_throw"))
            if n != "e_keg_lit":            # the lit keg's sparks and glow get no outline (its barrel is e_keg's)
                c = G.complete_outline(c, color=dark)[0]
                c = mirror(c, top_bottom=(n == "e_throw"))
            out.append(c)
        res[n] = out
    # hand touch-up at 20 x 22: the 35 px cells blur the skull into a white blob and mirror the bent fuse into a spike
    for k, c in enumerate(res["e_keg"]):
        res["e_keg"][k] = touch_up(c, pal)
    # the lit keg's barrel = the plain keg's, square for square (bottom-aligned), the fuse's sparks drawn over it
    body = res["e_keg"][0]
    res["e_keg_lit"] = [sparks(body, man["e_keg_lit"]["cell_1x"], k) for k in range(len(res["e_keg_lit"]))]
    for k, c in enumerate(res["e_keg"]):
        res["e_keg"][k] = body.copy()
    for n, cs in res.items():
        Image.fromarray(np.concatenate(cs, axis=1)).save(lp(os.path.join(SRC, "pixel_1x", f"gangplank_fx_{n}.png")))
        big = np.concatenate(cs, axis=1)
        Image.fromarray(big).resize((big.shape[1] * 8, big.shape[0] * 8), Image.NEAREST).save(
            lp(os.path.join(SRC, f"gangplank_fx_{n}.png")))
        print(n, [c.shape[:2] for c in cs], "colours", len({tuple(p) for c in cs for p in c[c[..., 3] > 0][:, :3]}))
    if a.review:
        tiles = []
        for n, cs in res.items():
            for c in cs:
                bg = Image.new("RGBA", (c.shape[1], c.shape[0]), (90, 100, 90, 255))
                bg.alpha_composite(Image.fromarray(c))
                tiles.append(bg.resize((c.shape[1] * 10, c.shape[0] * 10), Image.NEAREST))
        W = sum(t.width + 10 for t in tiles)
        H = max(t.height for t in tiles)
        s = Image.new("RGB", (W, H), (30, 30, 30))
        x = 0
        for t in tiles:
            s.paste(t.convert("RGB"), (x, H - t.height))
            x += t.width + 10
        s.save(lp(a.review))


if __name__ == "__main__":
    main()
