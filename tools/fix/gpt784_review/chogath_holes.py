"""league_chogath's pinholes (the user, 2026-11-19: 「科加斯这里脚部失去像素了」): GPT's drawing leaves single clear squares
inside his outline - about 10 a frame, in the notches between back spikes, between the legs, at the claws - where the
ground shows through. Every clear square with >= 6 of its 8 neighbours drawn is filled: on the silhouette (a clear
4-neighbour) with its body neighbours' commonest colour (the darkest neighbour when all are outline: his outline stays
the one square tools/art/thin_outline.py keeps), inside with their commonest colour; twice, each
dense rect once (a third pass would start closing the 1-square slits between spikes: run it once). lo_ again (ppu_hd.add_lo's replica, tools/fix/xinzhao_galio_1119/sheetkit.py), the strips rewritten.
The 1x frames stay (the game's own, not played with league.dll's frames).

    python tools/fix/gpt784_review/chogath_holes.py [--check]
"""
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
sys.path.insert(0, HERE)
from sheetkit import Kit  # noqa: E402
import chogath_size as CS  # noqa: E402

N8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b]


def holes(c):
    a = c[..., 3] > 0
    nb = ndimage.convolve(a.astype(int), np.ones((3, 3), int), mode="constant") - a
    return (~a) & (nb >= 6)


def fill(c):
    out = c.copy()
    for _ in range(2):
        hs = holes(out)
        if not hs.any():
            break
        a = out[..., 3] > 0
        h, w = a.shape
        new = out.copy()
        for y, x in zip(*np.nonzero(hs)):
            nb = [out[y + dy, x + dx] for dy, dx in N8 if 0 <= y + dy < h and 0 <= x + dx < w and a[y + dy, x + dx]]
            edge = any(not (0 <= y + dy < h and 0 <= x + dx < w) or not a[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
            body = [p for p in nb if int(p[0]) + int(p[1]) + int(p[2]) > 60]
            if edge and not body:
                new[y, x] = min(nb, key=lambda p: int(p[0]) + int(p[1]) + int(p[2]))
            elif edge:
                # a notch in the silhouette: the body's own colour (his 1-square outline stays 1 square,
                # tools/art/thin_outline.py KEEP)
                vals, cnt = np.unique(np.array([tuple(int(v) for v in p) for p in body]), axis=0, return_counts=True)
                new[y, x] = vals[cnt.argmax()]
            else:
                vals, cnt = np.unique(np.array([tuple(int(v) for v in p) for p in nb]), axis=0, return_counts=True)
                new[y, x] = vals[cnt.argmax()]
        out = new
    return out


def main():
    k = Kit(ROOT, "league", "chogath")
    plain = CS.plain_tags(k)
    rects = {}
    for t in k.anims:
        if t.startswith("hd_"):
            for i in range(len(k.anims[t]["frames"])):
                rects.setdefault(k.rect(t, i), (t, i))
    if "--check" in sys.argv:
        # two passes on purpose (a third would start closing the 1-square slits between spikes), so a rerun would fill
        # more: the check is that the derived frames follow the dense ones (chogath_size.py --check does that)
        bad = CS.check(k)
        print("chogath holes: OK" if not bad else f"chogath holes: {bad} lo_ frames / strip cells not from the dense frames")
        sys.exit(1 if bad else 0)
    n = 0
    for r, (t, i) in rects.items():
        c = k.cell(t, i)
        f = fill(c)
        n += int((f != c).any(-1).sum())
        k.put(t, i, f)
    for t in plain:
        for i in range(len(k.anims[t]["frames"])):
            k.put("lo_" + t, i, k.lo_of(k.cell(t, i).shape[:2], k.cell("hd_" + t, i)))
    k.save()
    for t in plain:
        CS.write_strip(k, t)
    print(f"chogath holes: {n} squares filled in {len(rects)} dense frames")


if __name__ == "__main__":
    main()
