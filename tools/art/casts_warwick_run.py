#!/usr/bin/env python3
"""league_warwick's run from Codex's whole-frame redraw (assets/source/warwick/hd/run: tools/art/pack_warwick_run.py's
pack, delivered 2026-11-01, Documents/Codex/2026-11-01/new-chat-6/outputs/warwick-run) read onto the design's squares
(hd/idle.png, PPU 1.5) - casts_rengar_hd's keying, cells and palette sampling - and written over the run strip
tools/art/rig_warwick.py exports (assets/source/ppu/orig/warwick_run.png): the user, 2026-11-01, 「狼人的走路姿势现在有点
奇怪 让codex可以重做一下」 - the rig's run (the design's own legs lifted a few rows) read as a shuffle in place.

Each frame is read at the zoom that gives it the rig's frame's area (the same body, tail and gauntlet: Codex's straighter
legs in frames 1-2 made the height read him a size small) and placed in that frame's canvas: its box's bottom on the
old box's bottom, its box's middle on the old box's middle - so the strip keeps its sizes (warwick_run.json) and the 1x
sheet its rects.

    python tools/art/casts_warwick_run.py --review DIR    # the old run over the new one, 3x
    python tools/art/casts_warwick_run.py                 # write the strip (rig_warwick.py's export calls this too)
    python tools/art/ppu_restyle.py --hero warwick && python tools/art/ppu_hd.py --hero warwick
    python tools/art/ppu_one.py --hero warwick && python tools/art/hero_reels.py --hero warwick
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_rengar_hd as CS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "warwick", "hd")
SRC = os.path.join(HD, "run")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig", "warwick_run")
RIG = os.path.join(SRC, "rig_run")    # the rig's own run strip (rig_warwick.py's export saves it here before this runs)
GROW = 10                    # squares added above and below each frame's canvas (its centre, the pivot, stays): the
                             # redrawn run's raised spike stands up to 8 squares over the rig's canvas
D0 = np.asarray(Image.open(CS.lp(os.path.join(HD, "idle.png"))).convert("RGBA"))

# casts_rengar_hd's reading on his design
CS.D0 = D0
CS.PAL = np.unique(D0[D0[..., 3] > 0][:, :3], axis=0)
CS.PAL_LAB = color.rgb2lab(CS.PAL[None].astype(float) / 255.0)[0]


def sheets():
    with open(CS.lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)["sheets"]


def old_strip():
    """([RGBA frame], sizes) of the rig's run strip."""
    with open(CS.lp(RIG + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    a = np.asarray(Image.open(CS.lp(RIG + ".png")).convert("RGBA"))
    out, x = [], 0
    for w, h in meta["sizes"]:
        out.append(a[:h, x:x + w].copy())
        x += w
    return out, meta


def box(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def read():
    """[(new frame in the old frame's canvas, zoom)] for the 8 run frames."""
    olds, _ = old_strip()
    out = [None] * len(olds)
    for s in sheets():
        a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        for k, m in CS.cells(s, CS.figure(a)):
            old = np.pad(olds[k - 1], ((GROW, GROW), (0, 0), (0, 0)))
            L, T, R, B = box(old)
            ys, xs = np.nonzero(m)
            gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
            zoom = float(np.sqrt(m.sum() / (old[..., 3] > 0).sum()))
            sq = CS.sample(a, m, round(gh / zoom), round(gw / zoom))
            yy, xx = np.nonzero(sq[..., 3] > 0)
            sq = sq[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
            can = np.zeros_like(old)
            h, w = sq.shape[:2]
            x0 = int(round((L + R) / 2 - w / 2))
            y0 = B - h
            cx0, cy0 = max(0, x0), max(0, y0)
            cx1, cy1 = min(can.shape[1], x0 + w), min(can.shape[0], y0 + h)
            if (cx0, cy0, cx1, cy1) != (x0, y0, x0 + w, y0 + h):
                print(f"run {k}: {w}x{h} at {x0},{y0} clipped to the {can.shape[1]}x{can.shape[0]} canvas")
            can[cy0:cy1, cx0:cx1] = sq[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            out[k - 1] = (can, round(float(zoom), 2))
    return out


def write():
    """The strip and its sizes over the rig's export, each frame GROW squares taller above and below."""
    _, meta = old_strip()
    frs = read()
    sizes = [[w, h + 2 * GROW] for w, h in meta["sizes"]]
    strip = np.zeros((max(h for _, h in sizes), sum(w for w, _ in sizes), 4), np.uint8)
    x = 0
    for (can, z), (w, h) in zip(frs, sizes):
        strip[:h, x:x + w] = can
        x += w
    Image.fromarray(strip).save(CS.lp(ORIG + ".png"))
    with open(CS.lp(ORIG + ".json"), "w", encoding="utf-8") as f:
        json.dump(dict(meta, sizes=sizes), f)
    print("run strip written:", [z for _, z in frs], "px a square")


def review(out):
    olds, _ = old_strip()
    frs = read()
    Z = 3
    W, H = max(o.shape[1] for o in olds), max(o.shape[0] for o in olds)
    can = Image.new("RGB", (len(olds) * (W * Z + 6), 2 * (H * Z + 6)), (40, 40, 40))
    for i, (o, (n, _)) in enumerate(zip(olds, frs)):
        for row, pic in enumerate((o, n)):
            t = Image.new("RGBA", (W, H), (96, 112, 96, 255))
            t.alpha_composite(Image.fromarray(pic))
            can.paste(t.convert("RGB").resize((W * Z, H * Z), Image.NEAREST), (i * (W * Z + 6), row * (H * Z + 6)))
    os.makedirs(out, exist_ok=True)
    can.save(os.path.join(out, "warwick_run_old_new.png"))
    print("written", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    if a.review:
        review(a.review)
    else:
        write()


if __name__ == "__main__":
    main()
