#!/usr/bin/env python3
"""Codex's image-generation art for Vi (big drawn squares, soft edges) read onto the game's grid, block by block.

Used by tools/art/design_vi.py (the design) and for her action frames drawn at the same scale. Not a resize of a
read-back: each game pixel reads the ORIGINAL picture over the block it covers (px_per_row x px_per_col source
pixels), the source pixels snapped to the read-back's palette:
  - it is opaque when `solid` of the block is (alpha 129 and up);
  - the eyes' and crystals' blues win a block they hold `feature` of, the whites (eye, dial) at three times that -
    small bright marks survive; else the outline darks win a block they hold `dark` of - inner lines stay; else the
    commonest colour;
  - a lone square whose four neighbours all share one other colour takes it (specks), the features excepted.
Before this, the approved master read back on its own grid (59 rows) and shrunk melted the details into specks; the
user: 「codex做了一版挺大的 需要你慢慢调到合适的尺寸」.
"""
import numpy as np
from PIL import Image

FEATURE = {"005DE7", "007CFC", "0067F8", "006CFB", "01C6FD", "FBF2E6", "F4E9DA"}
WHITE = {"FBF2E6", "F4E9DA"}
DARK = {"200C05", "2C1E3F", "1F1E2F"}


def hexs(c):
    return "%02X%02X%02X" % tuple(int(v) for v in c[:3])


def palette(path):
    """The read-back's colours: (names, rgb array)."""
    r = np.asarray(Image.open(path).convert("RGBA"))
    cols = sorted({hexs(p) for p in r.reshape(-1, 4) if p[3]})
    return cols, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in cols], float)


def read_blocks(src, left, bottom, px_col, px_row, W, H, cols, pal, solid=0.45, feature=0.12, dark=0.4):
    """An H x W picture whose square (r, c) reads src[bottom - (H - r) * px_row : ..., left + c * px_col : ...].
    Returns (picture, feature mask)."""
    out = np.zeros((H, W, 4), np.uint8)
    feat = np.zeros((H, W), bool)
    for r in range(H):
        ya, yb = int(round(bottom - (H - r) * px_row)), int(round(bottom - (H - r - 1) * px_row))
        for c in range(W):
            xa, xb = int(round(left + c * px_col)), int(round(left + (c + 1) * px_col))
            blk = src[max(0, ya):max(0, yb), max(0, xa):max(0, xb)].reshape(-1, 4)
            if not len(blk):
                continue
            op = blk[blk[:, 3] > 128]
            if len(op) < solid * len(blk) or not len(op):
                continue
            k = np.argmin(((op[:, None, :3].astype(float) - pal[None]) ** 2).sum(-1), 1)
            counts = {}
            for i in k:
                counts[cols[i]] = counts.get(cols[i], 0) + 1
            n = len(k)
            best = None
            fe = {h: v for h, v in counts.items() if h in FEATURE and v >= feature * n * (3 if h in WHITE else 1)}
            if fe:
                best = max(fe, key=fe.get)
                feat[r, c] = True
            if best is None:
                dk = {h: v for h, v in counts.items() if h in DARK}
                if dk and sum(dk.values()) >= dark * n:
                    best = max(dk, key=dk.get)
            if best is None:
                best = max(counts, key=counts.get)
            out[r, c, :3] = [int(best[i:i + 2], 16) for i in (0, 2, 4)]
            out[r, c, 3] = 255
    return out, feat


def despeckle(a, feat):
    """A lone square whose four neighbours all share one other (opaque) colour takes it; features stay."""
    H, W = a.shape[:2]
    o = a.copy()
    for r in range(H):
        for c in range(W):
            if not a[r, c, 3] or feat[r, c]:
                continue
            nb = [tuple(a[r + dy, c + dx]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if 0 <= r + dy < H and 0 <= c + dx < W]
            if len(nb) == 4 and len(set(nb)) == 1 and nb[0] != tuple(a[r, c]) and nb[0][3]:
                o[r, c] = nb[0]
    return o
