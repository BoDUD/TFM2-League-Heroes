"""Polish Olaf's 42-row letter grid (Temp/ol_work/rg/g42.txt -> g42p.txt + previews).

    python work/ol/polish_ol.py

1. the helmet: every steel square of the dome (and stray outline squares inside it) re-shaded as one clean dome,
   lit from the upper left, a lit brim row, one engraved swirl;
2. EDITS: hand edits (row, first column, letters; '.' clears, ' ' keeps).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ol", "tools", "art"))
import design_olaf as D  # noqa: E402

T = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ol_work", "rg")
STEEL = set("dgGhwW")
HAIR = set("rRoO")
DOME = (5, 11, 14, 28)          # rows, columns of the helmet dome (inclusive rows 5..11, cols 14..27)
BRIM = 11
RAMP = "WwhhGGGggd"
SWIRL = [(8, 18, "g"), (8, 19, "g"), (9, 18, "g"), (9, 19, "h")]
EDITS = [
    # the left horn: a dark-steel band lit on its upper side, tapering to the tip
    (2, 13, "h"), (3, 13, "Gh"), (4, 14, "h"), (5, 13, "gGh"),
    # the right horn
    (1, 31, "G"), (2, 31, "hG"), (3, 31, "hg"), (4, 30, "hGg"), (5, 29, "hGgd"),
    # the helmet dome, lit from the upper left, an engraved swirl (gg/gh), the brim
    (6, 14, "gGh00oR0Ghh000hGGg"),
    (7, 14, "0gGhh0GhhGGg0GhGgg0"),
    (8, 14, "00hGhggGGGGgggGgd0"),
    (9, 16, "0GGgGGGggggddd0"),
    (10, 17, "0Gggggggdd00"),
    (11, 17, "0wwhhhhGGGg0"),
    # under the brim: the cheek guards and the nose guard; the eyes; the face round the nose guard
    (12, 18, "gGGg00G0g0"),
    (13, 19, "gGKWeGEg"),
    (14, 19, "gGKSGKg"),
    # the mouth: the read-back's own (the user: 「用之前的嘴」)
    (15, 19, "hGh0000wh"),
    (16, 19, "0hGBm0RhG"),
    (17, 19, "o0hbtpSh0"),
]


def load():
    return [list(r.rstrip("\n")) for r in open(os.path.join(T, "g42.txt"))]


def dome(g):
    y0, y1, x0, x1 = DOME
    H, W = len(g), len(g[0])

    def inside(y, x):
        return 0 <= y < H and 0 <= x < W and g[y][x] != "."
    for y in range(y0, y1 + 1):
        for x in range(x0, x1):
            c = g[y][x]
            interior0 = c == "0" and all(inside(y + dy, x + dx) and g[y + dy][x + dx] not in HAIR | {"0"}
                                         for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)) if True)
            if c in STEEL or interior0:
                if y == BRIM:
                    g[y][x] = "h" if x < 22 else "G"
                    continue
                t = 0.6 * (y - y0) / (BRIM - y0) + 0.4 * (x - x0) / (x1 - x0)
                g[y][x] = RAMP[min(len(RAMP) - 1, int(t * len(RAMP)))]
    for y, x, c in SWIRL:
        g[y][x] = c


def edits(g):
    for y, x0, text in EDITS:
        for i, c in enumerate(text):
            if c != " ":
                g[y][x0 + i] = c


def to_rgba(g):
    a = np.zeros((len(g), len(g[0]), 4), np.uint8)
    for y, r in enumerate(g):
        for x, c in enumerate(r):
            if c != ".":
                a[y, x, :3] = D.hx(D.PAL[c])
                a[y, x, 3] = 255
    return a


def show(a, path, z=20):
    H, W = a.shape[:2]
    c = Image.new("RGBA", (W * z + 30, H * z + 30), (225, 225, 225, 255))
    c.alpha_composite(Image.fromarray(a).resize((W * z, H * z), Image.NEAREST), (30, 30))
    d = ImageDraw.Draw(c)
    for y in range(H):
        d.text((2, 30 + y * z + 4), str(y), fill=(0, 0, 0, 255))
    for x in range(W):
        d.text((30 + x * z + 3, 2 if x % 2 == 0 else 14), str(x), fill=(0, 0, 0, 255))
    c.save(path)


def main():
    g = load()
    before = to_rgba(g)
    edits(g)
    after = to_rgba(g)
    open(os.path.join(T, "g42p.txt"), "w").write("\n".join("".join(r) for r in g) + "\n")
    show(after, os.path.join(T, "g42p.png"))
    side = np.zeros((before.shape[0], before.shape[1] * 2 + 4, 4), np.uint8)
    side[:, :before.shape[1]] = before
    side[:, before.shape[1] + 4:] = after
    Image.fromarray(side).resize((side.shape[1] * 8, side.shape[0] * 8), Image.NEAREST).save(os.path.join(T, "ba8.png"))


if __name__ == "__main__":
    main()
