"""Lissandra's 40-row design drawn square by square after Codex's v2 attempt-02 (the user: 「我照第 2 张逐格重画 40 行」,
2026-10-05; Codex's image tool could not draw 40 rows and every shrink of its 72-100-row drafts broke into noise).

    python work/lz/design_lz.py            -> Temp/lz_work/design/lissandra_40_1x.png + review sheet (workspace root)

Every square is placed here: the grid G (40 rows x 24 columns, one character per colour of lz_pal.PAL, '.' empty)
is painted by the shape passes below (gown, hem crystals, braid, arms, crown, face, crystals) and then the
per-square fixes in FIX; the outline (K) closes the silhouette last.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lz_pal import RGB  # noqa: E402

TMPW = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "lz_work")
OUT = os.path.join(TMPW, "design")
WS = os.path.abspath(os.path.join(HERE, "..", ".."))
REF = os.path.join(TMPW, "codex2", "lissandra-model-v2", "raw", "attempt-02.png")
H, W = 40, 28


class Grid:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]

    def px(self, y, x, c):
        if 0 <= y < H and 0 <= x < W:
            self.g[y][x] = c

    def run(self, y, x0, s):
        for i, c in enumerate(s):
            if c != " ":
                self.px(y, x0 + i, c)

    def poly(self, pts, c):
        im = Image.new("L", (W, H), 0)
        ImageDraw.Draw(im).polygon(pts, fill=1, outline=1)
        m = np.asarray(im)
        for y, x in zip(*np.nonzero(m)):
            self.g[y][x] = c

    def get(self, y, x):
        return self.g[y][x] if 0 <= y < H and 0 <= x < W else "."

    def outline(self):
        """K on every empty square touching the figure (4-neighbours)."""
        add = []
        for y in range(H):
            for x in range(W):
                if self.g[y][x] == "." and any(self.get(y + dy, x + dx) not in ".K"
                                               for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    add.append((y, x))
        for y, x in add:
            self.g[y][x] = "K"

    def rgba(self):
        a = np.zeros((H, W, 4), np.uint8)
        for y in range(H):
            for x in range(W):
                c = self.g[y][x]
                if c != ".":
                    a[y, x, :3] = RGB[c]
                    a[y, x, 3] = 255
        return a


GOWN = "1234"


def build():
    G = Grid()
    # ---- braid (rows 10-31, behind her): 3 wide, plaits of 3 rows leaning left and right in turn, a dark band at 28
    LOBE = (("rrq", "prq", "ppq"), ("qrr", "qrp", "qpp"))
    for y in range(10, 32):
        x0 = 8 if y < 30 else 9
        x1 = 10 if y < 30 else 9
        tile = LOBE[((y - 10) // 3) % 2][(y - 10) % 3]
        for x in range(x0, x1 + 1):
            G.px(y, x, tile[x - 8] if x1 > x0 else "q")
    G.run(28, 8, "m4m")
    # ---- gown (rows 22-38): narrow at the waist, flaring to the hem; dark back side, lit ridge, lit front edge
    G.poly([(15, 22), (19, 22), (20, 26), (22, 30), (24, 33), (26, 38), (2, 38), (6, 33), (10, 30), (13, 26)], "2")
    for y in range(22, 39):
        xs = [x for x in range(W) if G.get(y, x) == "2"]
        lx, rx = min(xs), max(xs)
        for x in range(lx, min(rx, lx + max(1, (rx - lx) // 4)) + 1):
            G.px(y, x, "1")
        G.px(y, rx, "3")
        G.px(y, 17, "4")
        G.px(y, 18, "3")
    for y, x in ((26, 15), (27, 15), (28, 14), (29, 14), (30, 13), (31, 13), (26, 20), (27, 20), (28, 21), (29, 21), (30, 22)):
        G.px(y, x, "3")
    # ---- hem crystals (rows 31-38): five triangular shards rising out of the dark gown, outlined, lit on the right;
    # the gown shows between them
    for p, t, hw in ((5, 34, 2), (24, 34, 2), (10, 32, 2), (21, 32, 2), (16, 30, 3)):
        for y in range(t, 39):
            half = round((y - t) * hw / (38 - t))
            for x in range(p - half, p + half + 1):
                c = "a" if x < p else ("c" if x == p + half and half else "b")
                if y == t:
                    c = "c"
                G.px(y, x, c)
            for x in (p - half - 1, p + half + 1):
                if G.get(y, x) in "1234":
                    G.px(y, x, "K")
        if G.get(t - 1, p) in "1234":
            G.px(t - 1, p, "K")
    # ---- bodice (rows 15-22): fitted, the V neckline, the ridges
    G.poly([(14, 15), (21, 15), (20, 19), (19, 22), (15, 22), (14, 19)], "2")
    for y in range(15, 23):
        xs = [x for x in range(W) if G.get(y, x) == "2"]
        G.px(y, min(xs), "1")
    G.run(15, 16, "uwuu")
    G.run(16, 16, " uut")
    G.run(17, 17, "ut")
    G.run(18, 17, "t")
    for y, x in ((18, 15), (19, 16), (20, 17), (19, 18), (18, 19)):
        G.px(y, x, "4")
    for y, x in ((20, 15), (21, 16), (22, 17), (21, 18), (20, 19)):
        G.px(y, x, "5")
    # ---- far arm (her right, image left): upper arm in the dark sleeve, glowing forearm, clawed hand
    for y in range(16, 20):
        G.run(y, 12, "32")
    for y in range(20, 26):
        G.run(y, 12, "gh")
    G.run(25, 11, "ghj")
    G.run(26, 11, "hjh")
    G.run(27, 11, "j.j")
    G.run(28, 11, "w.w")
    # ---- near arm (her left, image right)
    for y in range(16, 20):
        G.run(y, 21, "32")
    for y in range(20, 26):
        G.run(y, 22, "gh")
    G.run(25, 22, "ghj")
    G.run(26, 22, "hjw")
    G.run(27, 22, "h.j")
    G.run(28, 22, "w.w")
    # ---- hood-locks (rows 8-16): dark ridged hair framing the face on both sides
    for y in range(8, 15):
        G.run(y, 12, "mn4n")
    G.run(15, 13, "n4")
    for y in range(8, 13):
        G.px(y, 21, "n")
    # ---- face (rows 8-13): the mask, pale skin, one lips square, the chin; the neck
    G.run(8, 16, "11111")
    G.run(9, 16, "24442")
    G.run(10, 16, "sttut")
    G.run(11, 16, "sttts")
    G.run(12, 16, "stLts")
    G.run(13, 17, "sss")
    G.run(14, 17, "ss")
    # ---- crown (rows 1-7): a flat diamond with two blades, lit edges, the cyan crescent
    G.poly([(14, 1), (15, 1), (26, 5), (26, 6), (21, 7), (6, 7), (1, 6), (1, 5)], "2")
    G.run(2, 12, "333")
    G.run(3, 10, "33333")
    G.run(4, 7, "3333333")
    G.run(5, 3, "5544444")
    G.run(6, 2, "55555")
    G.run(7, 6, "111111111111111")
    G.run(5, 20, "44455")
    G.run(6, 21, "44555")
    for y, x, c in ((1, 15, "z"), (2, 15, "y"), (2, 16, "z"), (3, 16, "y"), (3, 17, "z"), (4, 17, "y"), (4, 18, "z"),
                    (5, 18, "y"), (5, 19, "h"), (6, 18, "y"), (6, 17, "x"), (7, 17, "x"), (7, 16, "x")):
        G.px(y, x, c)
    # ---- shoulder crystals (rows 12-17)
    for y, x, c in ((12, 11, "z"), (13, 10, "y"), (13, 11, "w"), (13, 12, "y"), (14, 10, "x"), (14, 11, "z"), (14, 12, "y"),
                    (14, 13, "x"), (15, 11, "x"), (15, 12, "y"),
                    (12, 23, "z"), (13, 22, "y"), (13, 23, "w"), (13, 24, "y"), (14, 21, "x"), (14, 22, "y"), (14, 23, "z"),
                    (14, 24, "x"), (15, 22, "x"), (15, 23, "y")):
        G.px(y, x, c)
    for y, x, c in FIX:
        G.px(y, x, c)
    G.outline()
    return G


FIX = []   # per-square fixes after review: (row, col, colour)


def sheet(a):
    z = 12
    ref = Image.open(REF).convert("RGBA")
    ref = ref.crop(ref.getbbox())
    rh = H * z
    ref = ref.resize((int(ref.width * rh / ref.height), rh), Image.LANCZOS)
    big = Image.fromarray(a).resize((W * z, H * z), Image.NEAREST)
    grid = big.copy()
    d = ImageDraw.Draw(grid)
    for y in range(H + 1):
        d.line([(0, y * z), (W * z, y * z)], fill=(255, 0, 0, 90))
    for x in range(W + 1):
        d.line([(x * z, 0), (x * z, H * z)], fill=(255, 0, 0, 90))
    one = Image.fromarray(a)
    s = Image.new("RGBA", (ref.width + W * z * 2 + 200, rh + 20), (225, 225, 225, 255))
    s.alpha_composite(ref, (10, 10))
    s.alpha_composite(big, (ref.width + 20, 10))
    s.alpha_composite(grid, (ref.width + W * z + 30, 10))
    for k, zz in enumerate((1, 3)):
        im = one.resize((W * zz, H * zz), Image.NEAREST)
        bg = Image.new("RGBA", (W * zz + 8, H * zz + 8), (96, 104, 72, 255) if k == 0 else (24, 22, 30, 255))
        bg.alpha_composite(im, (4, 4))
        s.alpha_composite(bg, (ref.width + W * z * 2 + 40, 10 + k * 160))
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    G = build()
    a = G.rgba()
    Image.fromarray(a).save(os.path.join(OUT, "lissandra_40_1x.png"))
    sheet(a).convert("RGB").save(os.path.join(OUT, "review.png"))
    for y, row in enumerate(G.g):
        print(f"{y:2d} {''.join(row)}")


if __name__ == "__main__":
    main()
