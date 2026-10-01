#!/usr/bin/env python3
"""Camille's design (assets/source/native/camille_native.png) from Codex's 65-row drawing, by deleting whole rows.

    python tools/art/design_camille.py [--check]

Source: assets/source/camille/camille_source_65.png - an image Codex generated on 2026-10-02 while asked for a 46-row
design (its own delivery was hand-placed blocks), read back on its 10-px grid with regrid.py: 65 x 28 squares. The
user wanted 46 rows ("不行还是得用46 帮我换吧 50太大了") and "可以牺牲点腿部元素 来做上半身 比如手和脸做好点", and picked
C1 of three cuts: the head (rows 0-11, the hair, the bun and the face down to the chin) is kept exactly as drawn; the
body loses rows by regions - torso (12-26) weight 0.5, hips (27-42) 1.0, leg blades (43-) 1.3 - and columns by
(46 / 65) ** 0.8, about 10% a step: in every region the lines that go are the cheapest (squares differing from the
more similar neighbour), never two neighbours in one step, a line whose deletion would split the figure costing
extra. Near-identical shades are merged first (RGB distance 22, by frequency). The result, 46 x 21 and 49 colours,
stands on the 128 x 128 canvas with the middle of its blade tips at column 64 and its lowest row at 99 (the pivot
(64, 88), 11 rows above), and its far eye takes the near eye's cyan #029FD9 so that colour is the eyes' alone (the
far eye and the hip core shared #0AE3FB). Writes the 8x design; --check compares with the committed file instead.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "camille", "camille_source_65.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "camille_native.png")
CHIN = 11                                    # the last head row
REGIONS = [(12, 26), (27, 42), (43, 99)]     # torso, hips, leg blades (rows of the source)
WEIGHTS = [0.5, 1.0, 1.3]
ROWS, WIDTH, TOL = 46, 0.8, 22
SPLIT_COST = 1000
EYE = (0x02, 0x9F, 0xD9)
FAR_EYE = [(63, 67)]                         # (row, column) on the canvas: the far eye, #0AE3FB in the cut
CANVAS, FEET, MID = 128, 99, 64
Z = 8


def clean(a, tol):
    """Merge near-identical shades: colours by frequency, each joins the first kept colour within tol."""
    op = a[..., 3] > 0
    cols, inv, cnt = np.unique(a[op][:, :3].astype(np.int32), axis=0, return_inverse=True, return_counts=True)
    keep, mapping = [], np.zeros(len(cols), np.int32)
    for k in np.argsort(-cnt):
        c = cols[k]
        best = next((j for j, kc in enumerate(keep) if np.sqrt(((kc - c) ** 2).sum()) <= tol), -1)
        if best < 0:
            keep.append(c)
            best = len(keep) - 1
        mapping[k] = best
    out = a.copy()
    out[op, :3] = np.array(keep, np.uint8)[mapping[inv.ravel()]]
    out[op, 3] = 255
    out[~op] = 0
    return out


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def pieces(op):
    """Number of 8-connected pieces of a mask."""
    H, W = op.shape
    lab = np.zeros((H, W), np.int32)
    n = 0
    for y in range(H):
        for x in range(W):
            if op[y, x] and not lab[y, x]:
                n += 1
                stack = [(y, x)]
                lab[y, x] = n
                while stack:
                    cy, cx = stack.pop()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n
                                stack.append((ny, nx))
    return n


def line_cost(a, axis):
    b = a if axis == 0 else a.transpose(1, 0, 2)
    n = b.shape[0]
    key = np.where(b[..., 3:4] > 0, b[..., :3].astype(np.int32), -1)
    diff = (key[1:] != key[:-1]).any(-1).sum(1)
    cost = np.full(n, 1e6)
    for i in range(n):
        cost[i] = min(diff[i - 1] if i > 0 else 1e6, diff[i] if i < n - 1 else 1e6)
    return cost


def pick(cost, k, allowed):
    """k lines among `allowed` with the least total cost, never two neighbours."""
    n, INF = len(cost), float("inf")
    c = np.array([cost[i] if i in allowed else INF for i in range(n)])
    dp = np.full((n + 1, k + 1), INF)
    take = np.zeros((n + 1, k + 1), bool)
    dp[0][0] = 0.0
    for i in range(1, n + 1):
        for j in range(k + 1):
            best, tk = dp[i - 1][j], False
            if j > 0 and c[i - 1] < INF:
                prev = dp[i - 2][j - 1] if i >= 2 else (0.0 if j == 1 else INF)
                if prev + c[i - 1] < best:
                    best, tk = prev + c[i - 1], True
            dp[i][j], take[i][j] = best, tk
    if dp[n][k] == INF:
        return []
    out, i, j = [], n, k
    while j > 0 and i > 0:
        if take[i][j]:
            out.append(i - 1)
            i -= 2
            j -= 1
        else:
            i -= 1
    return sorted(out)


def delete_lines(a, axis, k, allowed_sets, protect=()):
    cost = line_cost(a, axis)
    op = a[..., 3] > 0
    base = pieces(op)
    for i in set().union(*[s for s, _ in allowed_sets]) - set(protect):
        if pieces(np.delete(op, i, axis=axis)) > base:
            cost[i] += SPLIT_COST
    gone = []
    for s, q in allowed_sets:
        if q > 0:
            gone += pick(cost, q, (s - set(protect)) - {x for g in gone for x in (g - 1, g, g + 1)})
    keep = [i for i in range(a.shape[axis]) if i not in set(gone)]
    return np.take(a, keep, axis=axis), keep


def shrink_block(a, rows_target, cols_target, groups, weights, step=0.9):
    """Shrink to rows_target x cols_target in ~10% steps, each row group giving up rows by its weight."""
    wts = list(weights)
    while a.shape[0] > rows_target or a.shape[1] > cols_target:
        nr = max(rows_target, int(round(a.shape[0] * step)))
        nc = max(cols_target, int(round(a.shape[1] * step)))
        k_r, k_c = a.shape[0] - nr, a.shape[1] - nc
        if k_r:
            sizes = [(hi - lo + 1) * w for (lo, hi), w in zip(groups, wts)]
            quotas = [int(round(k_r * s / sum(sizes))) for s in sizes]
            while sum(quotas) > k_r:
                quotas[int(np.argmax(quotas))] -= 1
            while sum(quotas) < k_r:
                quotas[int(np.argmax(sizes))] += 1
            sets = [(set(range(lo, hi + 1)), q) for (lo, hi), q in zip(groups, quotas)]
            a, keep = delete_lines(a, 0, k_r, sets, {0, a.shape[0] - 1})
            new = []
            for lo, hi in groups:
                inside = [j for j, i in enumerate(keep) if lo <= i <= hi]
                new.append((inside[0], inside[-1]) if inside else (0, -1))
            wts = [w for g, w in zip(new, wts) if g[1] >= g[0]]
            groups = [g for g in new if g[1] >= g[0]]
        if k_c:
            a, _ = delete_lines(a, 1, k_c, [(set(range(a.shape[1])), k_c)], {0, a.shape[1] - 1})
        if not k_r and not k_c:
            break
    return a


def mid_cols(row):
    xs = np.nonzero(row[..., 3] > 0)[0]
    return (xs.min() + xs.max()) / 2


def stack(head, body):
    """The head over the body, the chin's middle column over the collar's."""
    left = int(round(mid_cols(body[0]) - mid_cols(head[-1])))
    x0 = min(0, left)
    W = max(body.shape[1], left + head.shape[1]) - x0
    out = np.zeros((head.shape[0] + body.shape[0], W, 4), np.uint8)
    out[head.shape[0]:, -x0:-x0 + body.shape[1]] = body
    m = head[..., 3] > 0
    out[:head.shape[0], left - x0:left - x0 + head.shape[1]][m] = head[m]
    return crop(out)


def design():
    src = crop(clean(np.asarray(Image.open(G.lp(SRC)).convert("RGBA")), TOL))
    head, body0 = src[:CHIN + 1], src[CHIN + 1:]
    groups = [(max(0, lo - CHIN - 1), min(body0.shape[0] - 1, hi - CHIN - 1)) for lo, hi in REGIONS]
    cols = int(round(body0.shape[1] * (ROWS / src.shape[0]) ** WIDTH))
    cut = stack(head, shrink_block(body0.copy(), ROWS - head.shape[0], cols, groups, WEIGHTS))
    op = cut[..., 3] > 0
    low = int(np.nonzero(op.any(1))[0].max())
    tips = np.nonzero(op[low - 2:low + 1].any(0))[0]
    x0 = MID - int(round((tips.min() + tips.max()) / 2))
    out = np.zeros((CANVAS, CANVAS, 4), np.uint8)
    out[FEET - low:FEET + 1, x0:x0 + cut.shape[1]] = cut[:low + 1]
    for y, x in FAR_EYE:
        out[y, x, :3] = EYE
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = np.repeat(np.repeat(design(), Z, 0), Z, 1)
    if a.check:
        old = np.asarray(Image.open(G.lp(OUT)).convert("RGBA"))
        diff = int((old != out).any(-1).sum()) // (Z * Z)
        print("matches the committed design" if not diff else f"{diff} squares differ from the committed design")
        return
    Image.fromarray(out).save(G.lp(OUT))
    op = out[4::8, 4::8, 3] > 0
    print(OUT, f"{int(op.any(1).sum())} rows x {int(op.any(0).sum())} cols,",
          len(np.unique(out[4::8, 4::8][op][:, :3], axis=0)), "colours")


if __name__ == "__main__":
    main()
