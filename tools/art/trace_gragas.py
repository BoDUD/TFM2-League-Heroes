#!/usr/bin/env python3
"""Gragas's 1x front design traced from Codex's raw draft at 2:1 (the user, 2026-10-12: 「我照原稿逐格描」, front only:
「不需要侧面吧」): every game square is one 2x2 block of the draft's own squares.

    python tools/art/trace_gragas.py --auto            # the first pass -> assets/source/gragas/design/front_auto.txt
    python tools/art/trace_gragas.py --write           # design/front.txt (the hand-finished table) -> native png
    python tools/art/trace_gragas.py --sheet OUT.png   # the table beside the draft, 8x, with row/column numbers

The draft: codex_model/raw/gragas-front-A-raw.png read back on its own grid (the skill's regrid.py) = 71 x 86 squares
(the top of his head on row 2, the soles on row 85). Its colours: K = 24 (design_varus.kmeans), one letter each
(design/palette.json; '.' = clear). The first pass, for each 2x2 block at the offset that splits the fewest blocks:
  * clear when at most one of its four squares is drawn;
  * on the silhouette (a clear block beside it) any outline square makes it outline (the draft's 1-square outline stays
    one square);
  * inside, two or more outline squares make it outline (the draft's inner contour lines: arm against belly, fingers);
  * else the commonest of its other colours, a tie going to the colour more common in the 4x4 squares round it.
Then the table is finished by hand (design/front.txt; the face, the beard's braids and rings, the X scar, the keg's lid),
and design_gragas-style placement puts it on the 128 canvas: the soles on row 99, the feet's middle on column 64.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as dv  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "gragas", "codex_model", "raw", "gragas-front-A-raw.png")
DESIGN = os.path.join(ROOT, "assets", "source", "gragas", "design")
NATIVE = os.path.join(ROOT, "assets", "source", "native", "gragas_native.png")
K = 24
LETTERS = "abcdefghijklmnopqrstuvwx"
SOLE_ROW, MID_COL, FEET_ROWS = 99, 64, 3


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back():
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def palette():
    """The draft's K colours, sorted dark to light, and the draft as indices."""
    idx, pal = dv.kmeans(read_back(), K)
    order = np.argsort((pal * [0.299, 0.587, 0.114]).sum(1))
    remap = {int(o): i for i, o in enumerate(order)}
    idx = np.vectorize(lambda v: -1 if v < 0 else remap[int(v)])(idx)
    return idx, pal[order]


def reduce2(idx, oy, ox, ink=0):
    H, W = idx.shape
    pad = np.full((H + 4, W + 4), -1)
    pad[oy + 2:oy + 2 + H, ox + 2:ox + 2 + W] = idx       # the draft shifted by the offset, two clear squares round
    R, C = (H + oy + 1) // 2 + 1, (W + ox + 1) // 2 + 1
    blocks = [[pad[2 + 2 * r:4 + 2 * r, 2 + 2 * c:4 + 2 * c].ravel() for c in range(C)] for r in range(R)]
    drawn = np.array([[(b >= 0).sum() >= 2 for b in row] for row in blocks])
    out = np.full((R, C), -1)
    split = 0
    for r in range(R):
        for c in range(C):
            if not drawn[r, c]:
                continue
            b = blocks[r][c]
            cells = b[b >= 0]
            n_ink = (cells == ink).sum()
            edge = any(not (0 <= r + dy < R and 0 <= c + dx < C and drawn[r + dy, c + dx])
                       for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if (edge and n_ink >= 1) or n_ink >= 2:
                out[r, c] = ink
                continue
            rest = cells[cells != ink]
            vals, cnt = np.unique(rest, return_counts=True)
            top = vals[cnt == cnt.max()]
            if len(top) > 1:
                split += 1
                ctx = pad[2 * r + 1:2 * r + 5, 2 * c + 1:2 * c + 5].ravel()
                top = sorted(top, key=lambda v: -(ctx == v).sum())
            out[r, c] = top[0]
    ys, xs = np.nonzero(out >= 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1], split


def to_text(t):
    return "\n".join("".join("." if v < 0 else LETTERS[v] for v in row) for row in t) + "\n"


def from_text(s):
    rows = [r for r in s.splitlines() if r.strip()]
    w = max(len(r) for r in rows)
    return np.array([[-1 if ch == "." else LETTERS.index(ch) for ch in r.ljust(w, ".")] for r in rows])


def rgba(t, pal):
    out = np.zeros(t.shape + (4,), np.uint8)
    m = t >= 0
    out[m, :3] = pal[t[m]]
    out[m, 3] = 255
    return out


def on_canvas(fig):
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def sheet(path, t, pal):
    raw = read_back()
    z = 8
    a = Image.fromarray(raw).resize((raw.shape[1] * z // 2, raw.shape[0] * z // 2), Image.NEAREST)
    b = Image.fromarray(rgba(t, pal)).resize((t.shape[1] * z, t.shape[0] * z), Image.NEAREST)
    W = a.width + b.width + 3 * 40
    H = max(a.height, b.height) + 60
    img = Image.new("RGBA", (W, H), (205, 205, 205, 255))
    img.alpha_composite(a, (20, 40))
    x0 = a.width + 60
    img.alpha_composite(b, (x0, 40))
    d = ImageDraw.Draw(img)
    for r in range(0, t.shape[0], 5):
        d.text((x0 - 22, 40 + r * z), str(r), fill=(200, 0, 0, 255))
    for c in range(0, t.shape[1], 5):
        d.text((x0 + c * z + 1, 26), str(c), fill=(0, 0, 200, 255))
    d.text((20, 10), "Codex raw front-A (71x86), shown at half", fill=(0, 0, 0, 255))
    d.text((x0, 10), f"traced 2:1: {t.shape[1]}x{t.shape[0]}", fill=(0, 0, 0, 255))
    img.convert("RGB").save(path)
    print("wrote", path, img.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--sheet")
    ap.add_argument("--table", default=os.path.join(DESIGN, "front.txt"))
    a = ap.parse_args()
    os.makedirs(lp(DESIGN), exist_ok=True)
    pal_path = os.path.join(DESIGN, "palette.json")
    if a.auto:
        idx, pal = palette()
        best = None
        for oy in (0, 1):
            for ox in (0, 1):
                t, split = reduce2(idx, oy, ox)
                print(f"offset ({oy},{ox}): {t.shape[1]}x{t.shape[0]}, {split} tied blocks")
                if best is None or split < best[1]:
                    best = (t, split, (oy, ox))
        t = best[0]
        print("picked offset", best[2])
        with open(lp(os.path.join(DESIGN, "front_auto.txt")), "w", newline="\n") as f:
            f.write(to_text(t))
        json.dump({LETTERS[i]: "#%02x%02x%02x" % tuple(int(v) for v in pal[i]) for i in range(K)},
                  open(lp(pal_path), "w"), indent=1)
        if not os.path.exists(lp(a.table)):
            with open(lp(a.table), "w", newline="\n") as f:
                f.write(to_text(t))
    pal = np.array([[int(v[i:i + 2], 16) for i in (1, 3, 5)] for v in json.load(open(lp(pal_path))).values()], np.uint8)
    t = from_text(open(lp(a.table)).read())
    if a.sheet:
        sheet(a.sheet, t, pal)
    if a.write:
        Image.fromarray(on_canvas(rgba(t, pal))).save(lp(NATIVE))
        print("wrote", NATIVE, t.shape)


if __name__ == "__main__":
    main()
