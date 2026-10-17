#!/usr/bin/env python3
"""Jarvan IV's face from Codex's redesign take 2 (assets/source/jarvaniv/codex_redesign/jarvaniv-redesign-2.png) for the
approved design (the user, 2026-10-18: 「脸部太糊」, then 「接着只换脸,先给我看前后对比」).

    python tools/art/face_jarvaniv.py        # -> assets/source/jarvaniv/hd/face.png

Take 2 is drawn on 15 px squares (regrid: 34 x 71, the design's own density; its helmet two rows higher than the
design's). Only the face's squares come over - skin, the eye whites, the pupils and the dark brown brows / jaw line,
in the face's box (FACE_BOX design rows / columns) - each snapped to the design's own colours; every other square of the
design stays. Writes a design-sized RGBA with only those squares (rig_jarvaniv.design() lays it on).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
import rig_jarvaniv as J  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jarvaniv")
TAKE = os.path.join(SRC, "codex_redesign", "jarvaniv-redesign-2.png")
DY = 2                          # take 2's row = design row - DY (the helmets line up, columns the same)
FACE_BOX = (23, 31, 12, 20)     # design rows y0..y1, columns x0..x1


def kind(p, ol):
    if p[3] == 0:
        return None
    r, g, b = (int(v) for v in p[:3])
    if abs(r - ol[0]) + abs(g - ol[1]) + abs(b - ol[2]) < 30:
        return "outline"
    if r > 200 and g > 200 and b > 200:
        return "white"
    if r > 170 and 120 < g < 215 and 90 < b < 170 and r - b > 40:
        return "skin"
    if r < 100 and g < 70 and b < 60 and r >= b:
        return "brown"
    if b > r + 10 and b > g + 10:
        return "navy"
    return None


def face(D):
    a = np.asarray(Image.open(J.lp(TAKE)).convert("RGBA")).copy()
    t2, _, _ = RG.regrid(a, None)
    t2 = t2.copy()
    t2[..., 3] = np.where(t2[..., 3] >= 128, 255, 0)
    op = t2[..., 3] > 0
    t2 = t2[np.ix_(op.any(1), op.any(0))]
    d = D.d
    ol = np.array(D.outline)
    pal = np.array(sorted({tuple(int(v) for v in p[:3]) for p in d[d[..., 3] > 0]}), np.uint8)
    out = np.zeros_like(d)
    y0, y1, x0, x1 = FACE_BOX
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            src = t2[y - DY, x]
            k = kind(src, ol)
            here = kind(d[y, x], ol)
            face_here = here in ("skin", "white") or (here in ("navy", "brown") and y >= 25)
            if k in ("skin", "white", "brown") or (k == "navy" and face_here):
                out[y, x, :3] = pal[np.argmin(np.abs(pal.astype(int) - src[:3].astype(int)).sum(1))]
                out[y, x, 3] = 255
    return out


def main():
    J.FACE = None                    # the design as drawn, without a face laid on
    D = J.design()
    f = face(D)
    Image.fromarray(f).save(J.lp(os.path.join(SRC, "hd", "face.png")))
    changed = (f[..., 3] > 0) & (f != D.d).any(-1)
    print("face squares", int((f[..., 3] > 0).sum()), "changed", int(changed.sum()))


if __name__ == "__main__":
    main()
