"""league_galio's idle_loop (the wings moving through the idle's holds, hero_reels.json "hold"): GPT's redraw (#784,
2026-11-19) drew the 8 loop frames whole, and in frames 1 and 7 the whole figure stands a row higher than the idle's
frame 0 - played every 0.15 s through a hold, the body bobbed (the user, 2026-10-22: 「上下摆动全不要了」). Each loop
frame is moved, as a whole, by the offset that lays its stone body best on frame 0's (the light grey stone pixels, the
wings' gold left out; searched +-3 columns, +-4 rows): frames 1 and 7 one row down, the others stay. No pixel is
redrawn. hd_ written, 1x / lo_ derived (tools/fix/xinzhao_galio_1119/sheetkit.py), the strips rewritten.

    python tools/fix/gpt784_review/galio_loop.py [--check]
"""
import os
import sys

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
from sheetkit import Kit  # noqa: E402


def stone(c):
    r, g, b = (c[..., k].astype(int) for k in range(3))
    warm = (r > 90) & (r >= g) & (g > b + 15)
    return (c[..., 3] > 0) & ~warm & (r + g + b > 240)


def shift(c, dx, dy):
    out = np.zeros_like(c)
    h, w = c.shape[:2]
    ys, xs = np.nonzero(c[..., 3] > 0)
    ok = (ys + dy >= 0) & (ys + dy < h) & (xs + dx >= 0) & (xs + dx < w)
    if not ok.all():
        raise SystemExit("a moved loop frame would lose pixels at its edge")
    out[ys + dy, xs + dx] = c[ys, xs]
    return out


def best_offset(ref, c):
    R, M = stone(ref), stone(c)
    best = None
    for dy in range(-4, 5):
        for dx in range(-3, 4):
            d = (np.roll(np.roll(M, dy, 0), dx, 1) ^ R).sum()
            if best is None or d < best[0] or (d == best[0] and abs(dx) + abs(dy) < abs(best[1]) + abs(best[2])):
                best = (d, dx, dy)
    return best[1], best[2]


def main():
    k = Kit(ROOT, "league", "galio")
    base = k.cell("hd_idle_base", 0)
    n = len(k.anims["hd_idle_loop"]["frames"])
    moves = [best_offset(base, k.cell("hd_idle_loop", i)) for i in range(n)]
    if "--check" in sys.argv:
        bad = [i for i, m in enumerate(moves) if m != (0, 0)]
        print("galio loop: OK" if not bad else f"galio loop: frames {bad} off the idle's body")
        sys.exit(1 if bad else 0)
    done = set()                        # frames 1 and 7 are one rect: move each rect once
    for i, (dx, dy) in enumerate(moves):
        r = k.rect("hd_idle_loop", i)
        if (dx, dy) == (0, 0) or r in done:
            continue
        done.add(r)
        k.put("hd_idle_loop", i, shift(k.cell("hd_idle_loop", i), dx, dy))
        print(f"idle_loop[{i}] moved {dx}, {dy}")
    for i in range(n):
        if moves[i] != (0, 0):
            k.derive("idle_loop", i)
    k.save()
    k.strip("idle_loop")


if __name__ == "__main__":
    main()
