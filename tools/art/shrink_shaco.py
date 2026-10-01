#!/usr/bin/env python3
"""Shaco three rows shorter (the user, 2026-10-01: "萨科能略微的变小一点吗尺寸 现在放游戏里有点大"): 46 -> 43 rows.

    python tools/art/shrink_shaco.py [--check] [--out DIR]

The 46-row strips (Codex's, with the legs pass and the re-stepped run) are kept one pixel a square in
assets/source/shaco/native46/shaco_<tag>_1x.png (the first run copies them there from assets/source/native); every run
starts from those and writes assets/source/native/shaco_<tag>.png (8x), so running it again changes nothing and --check
can tell. Rows only, like tools/art/shorten_legs.py: no pixel is redrawn. In every upright frame three rows between the
top of the pantaloons and the shoes go - the ones most like a neighbour, never two neighbours - and everything above
them comes down: the head, the hat and the face as drawn, three rows lower; the feet and the ground line stay. A row
across the 2x2 checks would leave a one-row band of checks, so rows with three or more dark checks cost extra: in the
design (and most frames) the rows that go are the pantaloons' top under the jacket's flap (two dark checks there), the
knee band's second gold row and a plain row of the boots. The death's last two frames lie on the ground (frame 6 turned
a quarter turn): there the legs reach out to the left, and three columns of them go instead (shorten_legs.shorten_cols).
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
from shorten_legs import line_cost, read8, shorten_cols  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
KEEP = os.path.join(ROOT, "assets", "source", "shaco", "native46")
ROWS = 3
CHECK = np.array([0x2F, 0x2E, 0x40], np.uint8)          # the pantaloons' dark check, used nowhere else
GOLD = np.array([0xF3, 0xBF, 0x27], np.uint8)           # the knee and ankle bands' gold
SPIKES = [np.array([0xD1, 0xCB, 0xDE], np.uint8), np.array([0xAA, 0xA3, 0xBE], np.uint8)]   # the boots' silver
# spikes - the pantaloons' light checks are the same two colours, so they count only under the knee band
SPLIT = 100                                              # the extra cost of a row through a band of checks, or of the
                                                         # only row of a gold band, or of the spikes' row
LYING = {"dead7": [20, 52, ROWS], "dead8": [20, 52, ROWS]}   # cell columns of the legs reaching out, columns to go


def checks(f):
    return ((f[..., :3] == CHECK).all(-1) & (f[..., 3] > 0)).sum(1)


def colour_rows(f, c):
    return (f[..., :3] == c).all(-1) & (f[..., 3] > 0)


def pick_rows(f, lo, hi, n):
    """n rows of f in lo..hi to delete: the least cost, never two neighbours. A row through a band of 2x2 checks, the
    only row of a gold band (one of the knee band's two rows may go) or a row of the boots' spikes costs SPLIT more:
    those would lose a check row, a band or the spikes; the pantaloons' top under the flap, the knee band's second
    gold row and the plain rows of the boots are what goes."""
    dark = checks(f)
    gold = colour_rows(f, GOLD)
    spike = colour_rows(f, SPIKES[0]) | colour_rows(f, SPIKES[1])
    rows = list(range(lo, hi + 1))
    knee = next((r for r in rows if gold[r].sum() >= 3), hi + 1)

    def extra(r):
        e = SPLIT if dark[r] >= 3 else 0
        g = gold[r]
        if g.sum() >= 3 and not ((g & gold[r - 1]).sum() >= 2 or (g & gold[r + 1]).sum() >= 2):
            e += SPLIT
        if r > knee and spike[r].sum() >= 2:
            e += SPLIT
        return e
    cost = {r: min(line_cost(f, r, r - 1), line_cost(f, r, r + 1)) + extra(r) for r in rows}
    best = None

    def rec(start, left, chosen, total):
        nonlocal best
        if left == 0:
            if best is None or total < best[0]:
                best = (total, list(chosen))
            return
        for i in range(start, len(rows)):
            r = rows[i]
            if chosen and r - chosen[-1] < 2:
                continue
            if best is not None and total + cost[r] >= best[0]:
                continue
            chosen.append(r)
            rec(i + 1, left - 1, chosen, total + cost[r])
            chosen.pop()

    rec(0, n, [], 0)
    return best[1], best[0]


def shrink_frame(f, py):
    """Three rows out of the legs of an upright frame; (frame, rows gone, cost)."""
    dark = checks(f)
    op = (f[..., 3] > 0).any(1)
    lowest = int(np.nonzero(op)[0].max())
    top = max(int(np.nonzero(dark >= 1)[0].min()), py - 7)   # the pantaloons' first row, never over the belt
    gone, cost = pick_rows(f, top, lowest - 3, ROWS)
    keep = [y for y in range(f.shape[0]) if y not in gone]
    out = np.zeros_like(f)
    out[len(gone):] = f[keep]
    return out, gone, cost


def originals(table):
    out = {}
    for tag in table["tags"]:
        p = os.path.join(KEEP, f"shaco_{tag}_1x.png")
        if not os.path.exists(G.lp(p)):
            os.makedirs(G.lp(KEEP), exist_ok=True)
            Image.fromarray(read8(os.path.join(SRC, f"shaco_{tag}.png"))).save(G.lp(p))
            print("kept the 46-row strip as", os.path.relpath(p, ROOT))
        out[tag] = np.asarray(Image.open(G.lp(p)).convert("RGBA"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only say whether the strips are what a run writes")
    ap.add_argument("--out", help="write the strips (1x) here instead of assets/source/native (a draft)")
    o = ap.parse_args()
    table = json.load(open(G.lp(os.path.join(SRC, "shaco_cells.json")), encoding="utf-8"))
    CW, CH = table["cell"]
    src = originals(table)
    bad = 0
    for tag, rows in table["tags"].items():
        a = src[tag]
        out = np.zeros_like(a)
        cols, _ = layout(len(rows))
        notes = []
        for k in range(len(rows)):
            sl = (slice(k // cols * CH, (k // cols + 1) * CH), slice(k % cols * CW, (k % cols + 1) * CW))
            f = a[sl]
            key = f"{tag}{k + 1}"
            if key in LYING:
                out[sl], gone, cost = shorten_cols(f, *LYING[key])
                notes.append(f"{k + 1} cols {gone}")
            else:
                py = rows[k]["pivot"][1]
                out[sl], gone, cost = shrink_frame(f, py)
                notes.append(f"{k + 1} rows {[g - py for g in gone]} ({cost})")
        if o.out:
            os.makedirs(o.out, exist_ok=True)
            Image.fromarray(out).save(os.path.join(o.out, f"shaco_{tag}_1x.png"))
        else:
            dst = os.path.join(SRC, f"shaco_{tag}.png")
            big = np.repeat(np.repeat(out, Z, 0), Z, 1)
            if o.check:
                cur = np.asarray(Image.open(G.lp(dst)).convert("RGBA"))
                same = cur.shape == big.shape and np.array_equal(cur, big)
                bad += not same
                print(f"{tag:8s} {'same' if same else 'DIFFERENT'}")
                continue
            Image.fromarray(big).save(G.lp(dst))
        print(f"{tag:8s} " + "; ".join(notes))
    if o.check and bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
