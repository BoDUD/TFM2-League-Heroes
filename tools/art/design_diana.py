#!/usr/bin/env python3
"""Diana's design (assets/source/native/diana_native.png) from Codex's game-size draft A, step by step.

    python tools/art/design_diana.py [--version A] [--height 40] [--out FILE] [--check]

The draft (assets/source/diana/codex_model/diana_design_A.png, Codex's answer to assets/source/diana/MODEL_PROMPTS.md;
the user picked A over B, 2026-09-30) is pixel art at about 11.5 source pixels a square, 52 squares from the crown to
the soles (the blade's tip 4 more) - bigger than the 39 asked, as Codex's drafts have come every time.
  1. regrid (the skill's scripts/regrid.py): square borders at the peaks of colour change, each square the median of
     its middle 3x3 -> 33x56;
  2. palette, 26 colours: the eye squares (the purple irises and white catch-lights inside the two eye boxes) keep
     three colours of their own, used nowhere else; the rest by k-means in Lab with the a*/b* axes counted twice (so
     the hair's warm greys never join a green or blue cluster - with plain Lab they turned olive), k-means++ from six
     seeds, the least error kept, each cluster shown by its commonest real colour;
  3. size, 40 rows from the crown to the soles (the user's size for Riven and Vayne, who were too big at 46-48):
     whole rows and columns deleted (tools/art/design_riven.py's keep_axis: in each group the line most like its
     neighbour goes), never through the face (the moon disc, lashes, eyes, cheeks, chin), the width in proportion;
  4. one outline (design_riven.one_outline, the face kept) and the ring completed where a deleted line held it;
  5. the blade 2 squares back, clear of the hair (tools/art/tidy_diana.py's move_blade; the user, after the strips:
     "皎月的武器和头发重叠了", and of the variants picked "待机 A2" - this is the idle's frame);
  6. League's short tassets and the legs under them in place of the long coat (diana_run_legs.idle_lower, in the idle
     cell; the user: "戴安娜的腿部被包裹的感觉还是好奇怪", then "按样稿换成短裙甲");
  7. on the 128x128 canvas, soles on row 99, the middle of the feet on column 64, shown at 8x.
--check compares the result with the committed file instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
from regrid import regrid  # noqa: E402
from tidy_diana import BLADE_BACK, move_blade  # noqa: E402
from diana_run_legs import idle_lower  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "diana", "codex_model", "diana_design_{}.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "diana_native.png")
IDLE_AT = (24, 37)          # where the design (= the idle frame) stands in the idle's 96x96 cell: its top-left
K, HUE_W, SEEDS = 26, 2.0, 6
# per draft, on its regrid: the crown row (the hair's top), the face kept square for square, the eye boxes
DRAFTS = {
    "A": dict(crown=4, rows=range(11, 18), cols=range(19, 27), eyes=[(13, 16, 20, 22), (13, 16, 24, 26)]),
    "B": dict(crown=8, rows=range(16, 25), cols=range(24, 33), eyes=[(20, 23, 25, 28), (20, 23, 30, 32)]),
}


def eye_mask(a, boxes):
    """Purple or near-white squares inside the eye boxes (the lashes stay with the dark body colours)."""
    rgb = a[..., :3].astype(int)
    purple = (rgb[..., 2] > rgb[..., 1] + 40) & (rgb[..., 0] > rgb[..., 1] + 10) & (rgb.max(-1) > 60)
    white = rgb.min(-1) > 200
    m = np.zeros(a.shape[:2], bool)
    for y0, y1, x0, x1 in boxes:
        m[y0:y1, x0:x1] = True
    return m & (purple | white) & (a[..., 3] > 0)


def palette_hue(img, k, seed):
    """design_riven.palette with Lab's a*/b* weighted by HUE_W; also returns the weighted error."""
    op = img[..., 3] > 0
    uniq, inv, cnt = np.unique(img[op][:, :3], axis=0, return_inverse=True, return_counts=True)
    lab = R.to_lab(uniq) * np.array([1.0, HUE_W, HUE_W])
    w = np.sqrt(cnt)
    rng = np.random.default_rng(seed)
    cent = [lab[np.argmax(cnt)]]
    for _ in range(k - 1):
        d = np.min([((lab - c) ** 2).sum(1) for c in cent], axis=0) * w
        cent.append(lab[rng.choice(len(lab), p=d / d.sum())])
    cent = np.array(cent)
    for _ in range(40):
        lbl = np.argmin(((lab[:, None] - cent[None]) ** 2).sum(-1), axis=1)
        for j in range(k):
            m = lbl == j
            if m.any():
                cent[j] = (lab[m] * w[m, None]).sum(0) / w[m].sum()
    lbl = np.argmin(((lab[:, None] - cent[None]) ** 2).sum(-1), axis=1)
    pal = np.zeros((k, 3), int)
    for j in range(k):
        m = np.nonzero(lbl == j)[0]
        pal[j] = uniq[m[np.argmax(cnt[m])]] if len(m) else 0
    idx = np.full(img.shape[:2], -1, int)
    idx[op] = lbl[inv.ravel()]
    return pal, idx, float((((lab - cent[lbl]) ** 2).sum(1) * w).sum())


def quantise(a, eyes):
    body = a.copy()
    body[eyes] = 0
    pal, idx, _ = min((palette_hue(body, K - 3, s) for s in range(SEEDS)), key=lambda r: r[2])
    out = np.zeros_like(a)
    m = idx >= 0
    out[m, :3] = pal[idx[m]]
    out[m, 3] = 255
    ev = a[eyes][:, :3].astype(int)
    lum = R.lum(ev)
    wh = ev.min(1) > 200
    mid = np.median(lum[~wh])
    white = tuple(int(v) for v in np.median(ev[wh], 0))
    dark = tuple(int(v) for v in np.median(ev[~wh & (lum <= mid)], 0))
    light = tuple(int(v) for v in np.median(ev[~wh & (lum > mid)], 0))
    for (y, x), is_w, l in zip(zip(*np.nonzero(eyes)), wh, lum):
        out[y, x, :3] = white if is_w else light if l > mid else dark
        out[y, x, 3] = 255
    return out


def shrink(a, crown, rows, cols, height):
    H, W = a.shape[:2]
    colours = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(colours)}
    idx = np.full((H, W), -1, int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]
    th = round(H * height / (H - crown))
    keep_r = R.keep_axis([idx[y] for y in range(H)], th, rows)
    sub = idx[keep_r]
    keep_c = R.keep_axis([sub[:, x] for x in range(W)], round(W * th / H), cols)
    small = idx[np.ix_(keep_r, keep_c)]
    pal = np.array(colours, np.uint8)
    out = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    out[m, :3] = pal[small[m]]
    out[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [keep_r.index(r) for r in rows]
    fc = [keep_c.index(c) for c in cols]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    fig = R.outline_rgba(R.one_outline(out, keep), feet=out.shape[0] - 1, keep=keep)
    ys, xs = np.nonzero(fig[..., 3] > 0)
    return fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def canvas(fig):
    c = np.zeros((128, 128, 4), np.uint8)
    h, w = fig.shape[:2]
    xs = np.nonzero((fig[-4:, :, 3] > 0).any(0))[0]
    x0 = int(round(64 - (xs.min() + xs.max() + 1) / 2))
    c[100 - h:100, x0:x0 + w] = fig
    return np.repeat(np.repeat(c, 8, 0), 8, 1)


def design(version="A", height=40):
    d = DRAFTS[version]
    a = np.asarray(Image.open(R.lp(DRAFT.format(version))).convert("RGBA"))
    one, _, _ = regrid(a)
    q = quantise(one, eye_mask(one, d["eyes"]))
    fig = shrink(q, d["crown"], d["rows"], d["cols"], height)
    moved = move_blade(np.pad(fig, ((0, 0), (BLADE_BACK, 0), (0, 0))))
    ys, xs = np.nonzero(moved[..., 3] > 0)
    moved = moved[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cell = np.zeros((96, 96, 4), np.uint8)                       # the idle's frame: the tassets as in the strips
    cell[IDLE_AT[1]:IDLE_AT[1] + moved.shape[0], IDLE_AT[0]:IDLE_AT[0] + moved.shape[1]] = moved
    cell = idle_lower(cell)
    ys, xs = np.nonzero(cell[..., 3] > 0)
    return cell[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="A", choices=sorted(DRAFTS))
    ap.add_argument("--height", type=int, default=40)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true")
    o = ap.parse_args()
    fig = design(o.version, o.height)
    img = canvas(fig)
    n = len({tuple(int(v) for v in p[:3]) for p in fig[fig[..., 3] > 0]})
    print(f"{o.version}: {fig.shape[1]}x{fig.shape[0]} squares, {n} colours")
    if o.check:
        now = np.asarray(Image.open(R.lp(o.out)).convert("RGBA"))
        print("same as", o.out, bool((now == img).all()))
        return
    Image.fromarray(img).save(R.lp(o.out))
    print("written", o.out)


if __name__ == "__main__":
    main()
