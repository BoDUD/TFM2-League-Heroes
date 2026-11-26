"""The rebuilt Xin Zhao sheet against the pipeline: every lo_ frame = ppu_hd.add_lo of its hd_ frame, every 1x frame =
pixel_down.pixelate(hd_, 1/1.5) on its frame, every hd_ frame of a tag with a strip = that strip's cell (main and orig/,
orig ult / skill2 cells compared without the overlay-free check). usage: python verify.py <sheet base> <strip dir>"""
import json, os, sys
sys.path.insert(0, "tools/art")
import numpy as np
from PIL import Image
import ppu_hd as P
import pixel_down as D
base, strips = sys.argv[1:3]
img = np.asarray(Image.open(base + "#sheet.png").convert("RGBA"))
a = json.loads(open(base + "#anim.fanim", "rb").read().decode("utf-8-sig"))["anims"]
def cell(t, k):
    d = a[t]["frames"][k]["data"]; x, y, w, h = (int(round(d[q])) for q in ("x", "y", "w", "h")); return img[y:y+h, x:x+w]
def lo_of(one_shape, b):
    outline = D.edge_colour(b) if (b[..., 3] > 0).any() else (0, 0, 0)
    lo, (px, py) = D.pixelate(b, P.UI_PPU / P.PPU["xinzhao"], (b.shape[1] / 2, b.shape[0] / 2), outline)
    W, H = P.lo_size(one_shape[1], one_shape[0])
    ys, xs = np.nonzero(lo[..., 3] > 0)
    while W / 2 < max(px - xs.min(), xs.max() + 1 - px): W += 2
    while H / 2 < max(py - ys.min(), ys.max() + 1 - py): H += 2
    f = np.zeros((H, W, 4), np.uint8); ox, oy = int(np.floor(W / 2 - px + 0.5)), int(np.floor(H / 2 - py + 0.5))
    ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W); f[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return f
def one_of(one_shape, b):
    H, W = one_shape[:2]
    lo, (px, py) = D.pixelate(b, 1 / 1.5, (b.shape[1] / 2, b.shape[0] / 2), D.edge_colour(b))
    f = np.zeros((H, W, 4), np.uint8); ox, oy = int(np.floor(W / 2 - px + 0.5)), int(np.floor(H / 2 - py + 0.5))
    ys, xs = np.nonzero(lo[..., 3] > 0); ok = (ys + oy >= 0) & (ys + oy < H) & (xs + ox >= 0) & (xs + ox < W); f[ys[ok] + oy, xs[ok] + ox] = lo[ys[ok], xs[ok]]
    return f
bad_lo = [f"{t}[{k}]" for t in a if t.startswith("lo_") for k in range(len(a[t]["frames"])) if not np.array_equal(lo_of(cell(t[3:], k).shape, cell("hd_" + t[3:], k)), cell(t, k))]
plain = [t for t in a if not t.startswith(("hd_", "lo_"))]
bad_1x = [f"{t}[{k}]" for t in plain for k in range(len(a[t]["frames"])) if not np.array_equal(one_of(cell(t, k).shape, cell("hd_" + t, k)), cell(t, k))]
bad_strip = []
for sub in ("", "orig"):
    for t in plain:
        p = os.path.join(strips, sub, f"xinzhao_{t}.png")
        if not os.path.isfile(p) or not os.path.isfile(p[:-4] + ".json"): continue
        st = np.asarray(Image.open(p).convert("RGBA")); sizes = json.load(open(p[:-4] + ".json"))["sizes"]; x0 = 0
        for i, (w, h) in enumerate(sizes):
            if not np.array_equal(st[:h, x0:x0 + w], cell("hd_" + t, i)): bad_strip.append(f"{sub or 'main'}/{t}[{i}]")
            x0 += w + 1
print(f"lo_ frames not add_lo of their hd_: {len(bad_lo)} {bad_lo[:6]}")
print(f"1x frames not pixelate of their hd_: {len(bad_1x)} {bad_1x[:6]}")
print(f"strip cells unlike the hd_ frame: {len(bad_strip)} {bad_strip[:8]}")
