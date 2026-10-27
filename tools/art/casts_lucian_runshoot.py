#!/usr/bin/env python3
"""Lucian's walk while The Culling fires (`r_run`) from Codex's redraw (assets/source/lucian/hd/runshoot: the
tools/art/pack_lucian_runshoot.py pack, delivered 2026-10-27), read onto the design's squares the way
tools/art/casts_lucian_hd.py reads his other actions: the white keyed off, the zoom read off his head (the design's head
slid over the frame at zooms 5-14 px a square), each square the design colour most of its pixels snap to, the box's
middle and bottom on the pose guide's (the pasted run + ult frame the pack faded into the cell: soles 11.5 game px
under the pivot), then every frame shifted sideways so its head stands in one column like his run.
    python tools/art/casts_lucian_runshoot.py --measure    # the zoom of each sheet from the heads
    python tools/art/casts_lucian_runshoot.py --review DIR # the 8 frames placed, at 3x, the design first
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_lucian_hd as CS  # noqa: E402

SRC = os.path.join(CS.HD, "runshoot")
TAG = "r_run"
# px of Codex's drawing a design square, a sheet (--measure, 2026-10-27)
ZOOM = {"r_run_1": 6.95, "r_run_2": 7.4, "r_run_3": 7.17, "r_run_4": 7.02}


def sheets():
    with open(CS.lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)["sheets"]


def guides():
    """The pack's pose guides at the old 1x scale (what each cell held, faded): kept in SRC as guide_<k>.png the first
    time (pack_lucian_runshoot pastes them from the sheet's current hd_run / hd_ult, which a later export changes)."""
    paths = [os.path.join(SRC, f"guide_{k}.png") for k in range(1, 9)]
    if not all(os.path.isfile(p) for p in paths):
        import pack_lucian_runshoot as PK
        pasted, _, _ = PK.guides(4, 3)
        for p, (f, _) in zip(paths, pasted):
            Image.fromarray(PK.as_old(f)).save(CS.lp(p))
    return [np.asarray(Image.open(CS.lp(p)).convert("RGBA")) for p in paths]


GUIDE = guides()


def heads():
    """{frame name: (zoom, error)} - every frame's head fitted (casts_lucian_hd.head_fit)."""
    out = {}
    for s in sheets():
        a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        for k, m in CS.cells(s, CS.figure(a)):
            z, err, _ = CS.head_fit(a, m)
            out[f"{TAG}_{k}"] = (z, err)
    return out


def zoom_of(s, fits):
    g = [fits[f"{TAG}_{k}"][0] for k in s["frames"] if fits[f"{TAG}_{k}"][1] <= CS.GOOD]
    allg = [z for z, e in fits.values() if e <= CS.GOOD]
    return round(float(np.mean(g)) if g else float(np.median(allg)), 2)


def read_all():
    if ZOOM:
        zooms = ZOOM
    else:
        fits = heads()
        zooms = {s["name"]: zoom_of(s, fits) for s in sheets()}
    out = {}
    for s in sheets():
        a = np.asarray(Image.open(CS.lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        for k, m in CS.cells(s, CS.figure(a)):
            ys, xs = np.nonzero(m)
            gh, gw = ys.max() + 1 - ys.min(), xs.max() + 1 - xs.min()
            z = zooms[s["name"]]
            sq = CS.sample(a, m, round(gh / z), round(gw / z))
            L, T, R, B = CS.old_box(GUIDE[k - 1])
            out[f"{TAG}_{k}"] = (sq, (L + R) / 2 * CS.PPU, B * CS.PPU, z)
    return out


def placed():
    """{"r_run_<k>": (picture, x, y of its top-left on the design's grid)}: casts_lucian_hd.placed()'s rule, the soles on
    the ground, every head in one column (their mean)."""
    import casts_draven_hd as CD
    px = CD.shoes_mid(CS.D0)
    out = {}
    for n, (sq, mid, bottom, zoom) in read_all().items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        x, y = int(round(px + mid - pic.shape[1] / 2)), min(int(round(CS.GROUND + bottom - pic.shape[0])),
                                                            CS.GROUND - pic.shape[0])
        out[n] = (pic, x, y)
    col = {n: CS.head_place(out[n][0])[1] + out[n][1] for n in out}
    mean = int(round(np.mean(list(col.values()))))
    return {n: (pic, x + mean - col[n], y) for n, (pic, x, y) in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        fits = heads()
        for n, (z, e) in sorted(fits.items(), key=lambda t: int(t[0].rsplit("_", 1)[1])):
            print(n, "head zoom", round(z, 2), "err", round(e, 1), "GOOD" if e <= CS.GOOD else "")
        print("ZOOM =", json.dumps({s["name"]: zoom_of(s, fits) for s in sheets()}))
        return
    fr = placed()
    print("frames", len(fr))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        names = sorted(fr, key=lambda n: int(n.rsplit("_", 1)[1]))
        x0 = min(min(fr[n][1] for n in names), 0) - 2
        x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), CS.D0.shape[1]) + 2
        y0 = min(min(fr[n][2] for n in names), 0) - 2
        y1 = CS.GROUND + 2
        Z, W, H = 3, x1 - x0, y1 - y0
        tiles = [("design", (CS.D0, 0, 0))] + [(n, fr[n]) for n in names]
        can = Image.new("RGB", (len(tiles) * (W * Z + 4), H * Z), (40, 40, 40))
        for i, (n, (pic, x, y)) in enumerate(tiles):
            tile = Image.new("RGBA", (W, H), (150, 165, 150, 255))
            tile.alpha_composite(Image.fromarray(pic), (x - x0, y - y0))
            can.paste(tile.convert("RGB").resize((W * Z, H * Z), Image.NEAREST), (i * (W * Z + 4), 0))
        can.save(os.path.join(a.review, "placed_r_run.png"))
        print("written", a.review)


if __name__ == "__main__":
    main()
