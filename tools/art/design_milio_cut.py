"""Milio's picture B (the user's pick 2026-10-15) cut to the game size the user picked: the boy 32 game rows hair top
to soles at about 2.2 squares a game pixel = ROWS squares, the fire spirit with him.

    python tools/art/design_milio_cut.py

Reads assets/source/milio/codex_picture/milio-model-B.png (Codex's step-0 take, squares ~10-12 px, alpha max 254 haze):
hard alpha (>= 128), a k-means palette of 32 (pixel_down.palette_of on Codex's raw is all dark: snap to k-means
first), pixel_down.pixelate so the boy is ROWS squares tall, the outline of the edge. The spirit is the picture's
second piece (left of the boy, never touching him). Writes assets/source/milio/hd/cut_front.png (both),
cut_boy.png and cut_spirit.png (the same canvas, one each) - the step-1 pack's guide for Codex's on-grid redraw (a cut
from a bigger picture reads muddy: memory muddy-design-grid-redraw), not the final design.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "milio")
GAME_ROWS = 32
DENS = 2.2
ROWS = round(GAME_ROWS * DENS)   # 70 squares hair top to soles


def kpal(a, n=32):
    px = a[a[..., 3] > 0][:, :3].astype(float)
    rng = np.random.default_rng(0)
    sub = px[rng.choice(len(px), min(60000, len(px)), replace=False)]
    c, _ = kmeans2(sub, n, seed=1, minit="++")
    return c


def main():
    a = np.array(Image.open(os.path.join(SRC, "codex_picture", "milio-model-B.png")).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    lab, n = ndimage.label(a[..., 3] > 0)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    order = np.argsort(-sizes) + 1
    boy, spirit = lab == order[0], lab == order[1]
    ys = np.nonzero(boy.any(1))[0]
    y0, y1 = ys.min(), ys.max()
    k = ROWS / (y1 - y0 + 1)
    xs = np.nonzero(boy[y1 - 40:y1 + 1].any(0))[0]
    pivot = (int(round((xs.min() + xs.max()) / 2)), int(y1 + 1))   # between the sandals, under the soles
    pal = kpal(a)
    outline = PD.edge_colour(a)
    out = {}
    for name, m in (("cut_front", boy | spirit), ("cut_boy", boy), ("cut_spirit", spirit)):
        b = a.copy()
        b[~m] = 0
        f, piv = PD.pixelate(b, k, pivot, outline, pal)
        out[name] = (f, piv)
    full = out["cut_front"][0]
    yy, xx = np.nonzero(full[..., 3])
    box = (xx.min(), yy.min(), xx.max() + 1, yy.max() + 1)
    os.makedirs(os.path.join(SRC, "hd"), exist_ok=True)
    for name, (f, piv) in out.items():
        Image.fromarray(f).crop(box).save(os.path.join(SRC, "hd", name + ".png"))
    by = np.nonzero(out["cut_boy"][0][..., 3].any(1))[0]
    piv = out["cut_front"][1]
    print("canvas", box[2] - box[0], "x", box[3] - box[1], "boy rows", by.min() - box[1], "->", by.max() - box[1],
          "(", by.max() - by.min() + 1, ") standing col", piv[0] - box[0], "colours",
          len(np.unique(full[full[..., 3] > 0][:, :3], axis=0)))


if __name__ == "__main__":
    main()
