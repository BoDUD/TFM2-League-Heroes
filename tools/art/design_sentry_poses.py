#!/usr/bin/env python3
"""The Sentry's Codex poses (assets/source/sentry/codex_poses: POSE_PROMPTS.md, 15 poses laid out from the design's
three parts, 2026-11-02) at the design's stone size, on the design's palette, gaps closed, placed where the layout put
them.

    python tools/art/design_sentry_poses.py --sheet DIR     # all poses beside the design (4x), the core column marked
    python tools/art/design_sentry_poses.py                 # writes assets/source/sentry/hd/pose_<name>.png (+ .json)

Codex was asked the design at 12 px a square and drew every pose at a size of its own (its HANDOFF: the grid not kept;
the stone areas say 11.6 - 14.4 px a design square). The shards are rigid and only the core grows, so BODY[name] (raw px
for one design square) is the one that gives the pose's stone (everything but the core) the design's stone area
(STONE squares), unless set by eye. Each raw drawing is read on squares of BODY px (raw_read: the commonest palette
colour round each square's centre; the palette = the design's own colours + the core's glow rings and its dimmed / dead
greys, pack_sentry_poses.glow), the one-square cracks and small holes closed (design_silco_poses.close_gaps), loose
specks dropped.
Placing: Codex's own placement drifted (a_rise's bottom drawn under the ground line where the layout lifts it 3 rows),
so each pose goes where its layout (pack_sentry_poses.compose) put the design's parts: its core's middle on the layout
core's middle column (the dead ones without a core: the middle of their box on the layout's), its lowest row `lift`
rows above the design's ground. The json keeps `x` (the pose's left column in design squares) and `lift`.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pack_sentry_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_sentry_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sentry", "codex_poses", "sentry-poses")
OUT = os.path.join(ROOT, "assets", "source", "sentry", "hd")
SPECK = 6
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {}                     # name -> raw px a design square, set by eye (else from the stone area)
GLOW = [(40, 150, 255), (90, 200, 255), (235, 250, 255)]                  # pack_sentry_poses.glow's rings, hot middle
DIM = [(28, 40, 58), (46, 60, 82), (70, 86, 110), (100, 118, 140)]       # a dimmed / dead core
NAMES = [n for n in PK.POSES if not n.startswith("run")]   # the glide is the design's own (rig_sentry.py)


def design():
    return np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))


def is_core(px):
    r, g, b = (px[..., k].astype(int) for k in range(3))
    return ((b > 150) & (b - r > 70)) | ((r > 190) & (g > 220) & (b > 220))


STONE = None


def stone_squares():
    global STONE
    if STONE is None:
        d = design()
        STONE = int(((d[..., 3] > 0) & ~is_core(d)).sum())
    return STONE


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"sentry-pose-{name}.png"))).convert("RGBA")).copy()


def body_of(name, a):
    if name in BODY:
        return BODY[name]
    op = a[..., 3] >= 128
    return float(np.sqrt((op & ~is_core(a)).sum() / stone_squares()))


def raw_read(name):
    """Codex's raw drawing at the design's stone size, on the palette -> (figure, body)."""
    d = design()
    pal = np.unique(np.vstack([d[d[..., 3] > 0][:, :3], np.array(GLOW + DIM)]), axis=0)
    a = raw(name)
    body = body_of(name, a)
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    x0, y1 = xs.min(), ys.max() + 1
    nw, nh = int(np.ceil((xs.max() + 1 - x0) / body)), int(np.ceil((y1 - ys.min()) / body))
    cx = x0 + (np.arange(nw) + 0.5) * body
    cy = y1 - (nh - np.arange(nh) - 0.5) * body
    r = WIN // 2
    out = np.zeros((nh, nw, 4), np.uint8)
    lab_p = PD._lab(pal.astype(float))
    for j, y in enumerate(cy):
        for i, x in enumerate(cx):
            yi, xi = int(y), int(x)
            win = a[max(0, yi - r):yi + r + 1, max(0, xi - r):xi + r + 1].reshape(-1, 4)
            on = win[win[:, 3] >= 128]
            if len(on) * 2 < len(win):
                continue
            lab_w = PD._lab(on[:, :3].astype(float))
            idx = np.argmin(((lab_w[:, None, :] - lab_p[None]) ** 2).sum(-1), axis=1)
            out[j, i, :3] = pal[np.bincount(idx).argmax()]
            out[j, i, 3] = 255
    return out, body


def rim_glints(g):
    out = g.copy()
    r, gg, b = (g[..., k].astype(int) for k in range(3))
    white = (g[..., 3] > 0) & (r > 190) & (gg > 220) & (b > 220)
    azure = (g[..., 3] > 0) & is_core(g) & ~white
    h, w = white.shape
    for y, x in zip(*np.nonzero(white)):
        nb = [(y + dy, x + dx) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)) if 0 <= y + dy < h and 0 <= x + dx < w]
        if sum(azure[p] for p in nb) >= 2:
            continue
        cols = [tuple(g[p][:3]) for p in nb if g[p][3] > 0 and not white[p] and not azure[p]]
        if cols:
            out[y, x, :3] = max(set(cols), key=cols.count)
    return out


def target(name):
    """Where the layout put the pose: (the column its core's middle - or its box's middle - goes to, lift rows)."""
    d = design()
    moves = PK.POSES[name][0]
    img, M = PK.compose(d, PK.part_masks(d), moves)
    lay = img[..., 3] > 0
    core = lay & is_core(img)
    cols = np.nonzero(core)[1] if core.sum() >= 4 and not moves.get("dark") else np.nonzero(lay)[1]
    mid = (cols.min() + cols.max() + 1) / 2 if moves.get("dark") else cols.mean() + 0.5
    return mid - M, moves.get("lift", 0)


def read(name):
    d = design()
    g, body = raw_read(name)
    g = close_gaps(g, d)
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            g[lb == j] = 0
    # glow squares away from the core (run4's white line down the gap, where the design has none): the gap is empty
    core = (g[..., 3] > 0) & is_core(g)
    lb, n = ndimage.label(core, structure=np.ones((3, 3), bool))
    if n > 1:
        keep = np.argmax(ndimage.sum(core, lb, range(1, n + 1))) + 1
        g[core & (lb != keep)] = 0
    # near-white glints on a shard's rim (q_beam1's left shard by the core, touching it at a corner only): the core's
    # white sits inside it, so a white square with fewer than two azure neighbours takes its commonest neighbour's
    # colour
    g = rim_glints(g)
    ys, xs = np.nonzero(g[..., 3] > 0)
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    mid, lift = target(name)
    dark = PK.POSES[name][0].get("dark")
    core = (g[..., 3] > 0) & is_core(g)
    cols = np.nonzero(core)[1] if core.sum() >= 4 and not dark else np.nonzero(g[..., 3] > 0)[1]
    own = (cols.min() + cols.max() + 1) / 2 if dark else cols.mean() + 0.5
    x = int(round(mid - own))
    st = int(((g[..., 3] > 0) & ~is_core(g)).sum())
    print(f"{name:8s} body {body:5.2f} px: {g.shape[1]}x{g.shape[0]}, stone {st} (design {stone_squares()}), x {x}, "
          f"lift {lift}")
    return g, {"x": x, "lift": lift}


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {n: read(n) for n in names}
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 5
        d = design()
        tiles = [("design", d, {"x": 0, "lift": 0})] + [(n, *figs[n]) for n in NAMES if n in figs]
        left = min(0, *(m["x"] for _, _, m in tiles))
        right = max(t.shape[1] + m["x"] for _, t, m in tiles)
        top = max(t.shape[0] + m["lift"] for _, t, m in tiles)
        cw, ch = right - left + 2, top + 2
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
        for j, row in enumerate(rows):
            sheet = Image.new("RGBA", (len(row) * cw * z, ch * z + 20), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            for k, (n, t, m) in enumerate(row):
                ox = k * cw * z
                gy = 20 + ch * z - z
                sheet.alpha_composite(big(t, z), (ox + (m["x"] - left + 1) * z, gy - (t.shape[0] + m["lift"]) * z))
                core_x = ox + (14.5 - left + 1) * z
                dr.line([(core_x, 20), (core_x, gy)], fill=(255, 0, 0, 255))
                dr.line([(ox, gy), (ox + cw * z, gy)], fill=(40, 40, 40, 255))
                dr.text((ox + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
            path = os.path.join(a.sheet, f"sentry_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, meta) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump(meta, fh)


if __name__ == "__main__":
    main()
