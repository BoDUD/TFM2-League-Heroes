#!/usr/bin/env python3
"""Shorter legs for a hero whose drawn legs read too long (the user, 2026-10-01: "盲僧的腿太长 导致步频过慢 比较违和",
"安妮的腿也可以缩短一点 安妮的定位是小女孩").

    python tools/art/shorten_legs.py --hero leesin [--hero annie] [--check] [--out DIR]

The strips as Codex drew them are kept at one pixel a square in assets/source/<hero>/legs_long/<hero>_<tag>_1x.png
(the first run copies them there from assets/source/native); every run starts from those and writes
assets/source/native/<hero>_<tag>.png (8x), so running it again changes nothing and --check can tell.
In every upright frame whole rows between the hip and the ankles go: the hip is the first row (from the top) where
the legs' own colours (Lee Sin's navy trousers) fill LEGS[hero]["min"] squares, or with "feet" the frame's lowest
row (Annie: no colour of hers is the legs' alone); each band (rows from the hip; a negative end counts from the
frame's lowest row) loses its count of rows, the ones most like a neighbour (the fewest squares differ), never two
neighbours. Whatever is above a deleted row comes down a row, the
feet and the ground line stay: the figure is that many rows shorter, the head lower, the stride as long on shorter
legs. Frames whose legs do not hang under the hip take the overrides in LEGS[hero]["frames"] ("<tag><n>"): "skip"
(lying in the death), or "cols": [x0, x1, n] - n columns of a leg reaching out sideways between cell columns x0 and x1
go and the foot's side comes in, "shift": n - the whole frame n rows down (in the air, where rows would squash the
body: the head keeps its path), or "rows" to replace the bands for that frame.
Rows and columns only: no pixel is redrawn, the outline and the shading stay as drawn.
The tables that count from the pivot (<hero>_retouch.json, the idle's BOB seam in import_native.py, the effects'
anchors in import_<hero>.py) are kept in step by hand; the report says which rows went in every frame.
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
import strips as G  # noqa: E402
from native_refs import Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")


def hexes(*h):
    return [tuple(int(x[i:i + 2], 16) for i in (0, 2, 4)) for x in h]


LEGS = {
    # the baggy navy trousers from the hip, the red and white shin wraps, the feet: three rows between the
    # waistband and the ankles (17 rows from the hip to the soles in idle -> 14)
    "leesin": {"colours": hexes("2C3059", "20223F", "131528"), "min": 3,
               "bands": [(2, -3, 3)],
               # in the air with the legs not under him (Q2's somersault and flying kick, R's flip, thrown back in
               # the death) rows would squash him: the frame comes down as far instead, so the head keeps its path;
               # lying on the ground in the death: as drawn
               "frames": {**{f"q2{k}": {"shift": 3} for k in (2, 3, 4, 5)}, "ult3": {"shift": 3}, "dead3": {"shift": 3},
                          **{f"dead{k}": {"skip": True} for k in (4, 5, 6, 7)}}},
    # the leggings under the dress: two rows. Her leggings' shades are her outline's and the dress's too, and the
    # dress's purples her leggings' stripes, so no colour finds the hem: the band is the idle's legs counted up
    # from the feet ("feet": rows 7 to 2 over the frame's lowest row; 8 rows from the hem to the soles -> 6)
    "annie": {"feet": True, "bands": [(-7, -2, 2)],
              # thrown up and falling in the death: down as far; lying: as drawn
              "frames": {"dead2": {"shift": 2}, "dead3": {"shift": 2}, "dead4": {"skip": True},
                         "dead5": {"skip": True}, "dead6": {"skip": True}}},
}


def read8(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    H, W = a.shape[:2]
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    out[out[..., 3] < 128] = 0
    out[out[..., 3] >= 128, 3] = 255
    return out


def line_cost(f, j, k):
    """Squares that differ between rows j and k of f (columns: pass f transposed)."""
    if k < 0 or k >= f.shape[0]:
        return 10 ** 6
    return int((f[j] != f[k]).any(-1).sum())


def pick(f, lo, hi, n, taken):
    """n lines of f in lo..hi (inclusive) to delete: the least cost, never two neighbours, none next to `taken`."""
    lines = [r for r in range(lo, hi + 1) if not ({r - 1, r, r + 1} & taken)]
    cost = {r: min(line_cost(f, r, r - 1), line_cost(f, r, r + 1)) for r in lines}
    best = None

    def rec(start, left, chosen, total):
        nonlocal best
        if left == 0:
            if best is None or total < best[0]:
                best = (total, list(chosen))
            return
        for i in range(start, len(lines)):
            r = lines[i]
            if chosen and r - chosen[-1] < 2:
                continue
            if best is not None and total + cost[r] >= best[0]:
                continue
            chosen.append(r)
            rec(i + 1, left - 1, chosen, total + cost[r])
            chosen.pop()

    while n > 0:
        rec(0, n, [], 0)
        if best is not None:
            return best[1], best[0]
        n -= 1                     # a band too short for all of them (a crouch, a leg drawn up): as many as fit
    return [], 0


def hip_row(f, spec):
    op = f[..., 3] > 0
    col = np.zeros(op.shape, bool)
    for c in spec["colours"]:
        col |= np.all(f[..., :3] == np.array(c, np.uint8), -1) & op
    rows = np.nonzero(col.sum(1) >= spec["min"])[0]
    if not len(rows):
        raise ValueError("no hip row: none of the legs' colours")
    return int(rows[0])


def shorten_rows(f, spec, bands):
    lowest = int(np.nonzero((f[..., 3] > 0).any(1))[0].max())
    hip = lowest if spec.get("feet") else hip_row(f, spec)
    gone, cost = [], 0
    for a, b, n in bands:
        rows, c = pick(f, hip + a, lowest + b if b < 0 else hip + b, n, set(gone))
        gone += rows
        cost += c
    keep = [y for y in range(f.shape[0]) if y not in gone]
    out = np.zeros_like(f)
    out[len(gone):] = f[keep]
    return out, sorted(gone), hip, cost


def shorten_cols(f, x0, x1, n):
    """n columns out of x0..x1; the far side of the band from the body comes in."""
    cols, cost = pick(np.transpose(f, (1, 0, 2)), x0, x1, n, set())
    keep = [x for x in range(f.shape[1]) if x not in cols]
    xs = np.nonzero(f[..., 3] > 0)[1]
    out = np.zeros_like(f)
    if xs.mean() > (x0 + x1) / 2:          # the body right of the band: a leg reaching left, its foot moves right
        out[:, n:] = f[:, keep]
    else:
        out[:, :len(keep)] = f[:, keep]
    return out, cols, cost


def originals(hero, table):
    """The strips as drawn, one pixel a square: assets/source/<hero>/legs_long, filled from the native strips once."""
    keep = os.path.join(ROOT, "assets", "source", hero, "legs_long")
    out = {}
    for tag in table["tags"]:
        p = os.path.join(keep, f"{hero}_{tag}_1x.png")
        if not os.path.exists(G.lp(p)):
            os.makedirs(G.lp(keep), exist_ok=True)
            Image.fromarray(read8(os.path.join(SRC, f"{hero}_{tag}.png"))).save(G.lp(p))
            print("kept the drawn strip as", os.path.relpath(p, ROOT))
        out[tag] = np.asarray(Image.open(G.lp(p)).convert("RGBA"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append", required=True, choices=sorted(LEGS))
    ap.add_argument("--check", action="store_true", help="only say whether the strips are what a run writes")
    ap.add_argument("--out", help="write the strips (1x) here instead of assets/source/native (a draft)")
    o = ap.parse_args()
    bad = 0
    for hero in o.hero:
        spec = LEGS[hero]
        table = json.load(open(G.lp(os.path.join(SRC, f"{hero}_cells.json")), encoding="utf-8"))
        CW, CH = table["cell"]
        src = originals(hero, table)
        for tag, rows in table["tags"].items():
            a = src[tag]
            out = np.zeros_like(a)
            cols, _ = layout(len(rows))
            notes = []
            for k in range(len(rows)):
                sl = (slice(k // cols * CH, (k // cols + 1) * CH), slice(k % cols * CW, (k % cols + 1) * CW))
                f = a[sl]
                ov = spec["frames"].get(f"{tag}{k + 1}", {})
                if ov.get("skip"):
                    out[sl] = f
                    notes.append(f"{k + 1} kept")
                elif "shift" in ov:
                    # down as far as the others shrank, never under the ground line (11 rows under the pivot)
                    lowest = int(np.nonzero((f[..., 3] > 0).any(1))[0].max())
                    n = max(0, min(ov["shift"], rows[k]["pivot"][1] + 11 - lowest))
                    g = np.zeros_like(f)
                    g[n:] = f[:f.shape[0] - n]
                    out[sl] = g
                    notes.append(f"{k + 1} down {n}")
                elif "cols" in ov:
                    out[sl], gone, cost = shorten_cols(f, *ov["cols"])
                    notes.append(f"{k + 1} cols {gone}")
                else:
                    out[sl], gone, hip, cost = shorten_rows(f, spec, ov.get("rows", spec["bands"]))
                    notes.append(f"{k + 1} hip {hip} rows {gone}")
            print(f"{hero} {tag}: " + "; ".join(notes))
            if o.check:
                now = read8(os.path.join(SRC, f"{hero}_{tag}.png"))
                same = now.shape == out.shape and (now == out).all()
                bad += not same
                print(f"  {hero}_{tag}.png {'as a run writes it' if same else 'DIFFERENT'}")
            elif o.out:
                os.makedirs(o.out, exist_ok=True)
                Image.fromarray(out).save(os.path.join(o.out, f"{hero}_{tag}_1x.png"))
            else:
                Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, f"{hero}_{tag}.png")))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
