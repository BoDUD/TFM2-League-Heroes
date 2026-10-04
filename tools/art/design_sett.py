#!/usr/bin/env python3
"""Sett's design: Codex's raw draft B read onto the game grid block by block (league_vi's way, tools/art/shrink_vi.py).

    python tools/art/design_sett.py [--rows 42] [--out assets/source/native/sett_native.png] [--check]
    python tools/art/design_sett.py --candidates <folder>      # 42 / 40 / 38 rows side by side, for the user

Codex's step 1 did not draw at game size: its raw draft B (assets/source/sett/codex_model/sett_design_B_raw.png,
1254 px) reads back on its own ~8 px grid as 50 x 81 squares, and its own 42-row designs, shrunk and resampled with
the head and the body apart, broke into specks. The user: 「直接用这个然后你慢慢调整就行了」 (the raw draft B). So
each game pixel reads the ORIGINAL draft over the block it covers, the source pixels snapped to the draft's own
colours (PALETTE, 25):
  - it is opaque when 45% of the block is (alpha 129 and up);
  - the outline's near-black wins a block it holds 40% of (inner lines stay); else the commonest colour;
  - a lone square whose four neighbours all share one other colour takes it (specks);
  - an outline-black square inside the figure with three or four neighbours of one material takes that material's
    darkest shade (the abs and the folds read back as black specks);
  - the outline is closed (strips.complete_outline);
  - on the 128 x 128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sett", "codex_model")
DRAFT = os.path.join(SRC, "sett_design_B_raw.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "sett_native.png")
ROWS = 42
# The draft's own colours: its squares read back on their own grid (scripts/regrid.py) clustered (k-means, 28) and
# merged by material; the step 1 palette (codex_model/palette.txt) is not what the draft was drawn in (its skin
# snapped to gold). The eyes' amber is too close to the gold to read apart: the face is drawn after the read.
PALETTE = {
    "outline": ["050302"],
    "coat": ["1F0917", "340F1E", "451A2A"],
    "hair": ["55011B", "810426", "AA0C35", "C7153E", "D51B45"],
    "mantle": ["290B42", "3C1268", "531E8E"],
    "gold": ["361F05", "693B08", "925B11", "BD7702", "DF9704", "F7C414"],
    "skin": ["B06B44", "DC9263", "F9BC89"],
    "trousers": ["9FA8C3", "B2B9D2", "C4C9DB", "DCDFE8"],
}
FEATURE = set()                  # no colour needs a smaller share to win a block (the eyes are drawn afterwards)
DARK = {"050302"}                # the outline
EYE = "C8700A"                   # the eyes' amber, a shade nothing else has (import_native can find the face by it)
WHITE = "DCDFE8"                 # the near eye's highlight (the trousers' lightest)
BROW = "55011B"                  # the hair's darkest crimson: brows and lashes
SHADE = "B06B44"                 # the skin's shadow
# The face at 42 rows (the read keeps the face's skin but not its features): (x, y) on the 42-row figure -> colour.
# Brows and lashes on row 6; one row of eyes on row 7: the near eye a white highlight beside an amber iris, the far eye
# an amber iris, one skin column between; skin under them, a shadow for the mouth. The first version had a second
# row of amber under both eyes (three squares) - the user: 「这两坨黄的有点怪吧」, and of three faces took this one
# (「用option2」) over no amber and a single amber square under each pupil. Later, eyes copied from the draft's (a 3 x 2
# near eye: highlight, amber, pupil over shadow, glow, amber; dark lids) were tried; the user: 「就用option2吧」.
FACE = {
    (11, 6): BROW, (12, 6): BROW, (13, 6): "F9BC89", (14, 6): BROW,
    (11, 7): WHITE, (12, 7): EYE, (13, 7): "F9BC89", (14, 7): EYE, (15, 7): "DC9263",
    (11, 8): "DC9263", (12, 8): "F9BC89", (13, 8): "F9BC89", (14, 8): "F9BC89", (15, 8): "DC9263",
    (11, 9): "DC9263", (12, 9): "F9BC89", (13, 9): "F9BC89", (14, 9): "F9BC89",
    (13, 10): SHADE,
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def palette():
    cols = [h for hs in PALETTE.values() for h in hs]
    return cols, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in cols], float)


def read_blocks(src, left, bottom, px, W, H, cols, pal, solid=0.45, feature=0.12, dark=0.4):
    """An H x W picture whose square (r, c) reads src over the px x px block at (left + c px, bottom - (H - r) px)."""
    snapped = np.full(src.shape[:2], -1, int)
    op = src[..., 3] > 128
    ys, xs = np.nonzero(op)
    rgb = src[ys, xs, :3].astype(float)
    snapped[ys, xs] = np.argmin(((rgb[:, None] - pal[None]) ** 2).sum(-1), 1)
    out = np.zeros((H, W, 4), np.uint8)
    feat = np.zeros((H, W), bool)
    for r in range(H):
        ya, yb = int(round(bottom - (H - r) * px)), int(round(bottom - (H - r - 1) * px))
        for c in range(W):
            xa, xb = int(round(left + c * px)), int(round(left + (c + 1) * px))
            blk = snapped[max(0, ya):max(0, yb), max(0, xa):max(0, xb)].ravel()
            if not len(blk):
                continue
            k = blk[blk >= 0]
            if len(k) < solid * len(blk) or not len(k):
                continue
            counts = np.bincount(k, minlength=len(cols))
            n = len(k)
            best = None
            fe = [i for i, h in enumerate(cols) if h in FEATURE and counts[i] >= feature * n]
            if fe:
                best = max(fe, key=lambda i: counts[i])
                feat[r, c] = True
            if best is None:
                dk = [i for i, h in enumerate(cols) if h in DARK]
                if dk and counts[dk].sum() >= dark * n:
                    best = max(dk, key=lambda i: counts[i])
            if best is None:
                best = int(np.argmax(counts))
            out[r, c, :3] = pal[best]
            out[r, c, 3] = 255
    return out, feat


def despeckle(a, feat):
    """A lone square whose four neighbours all share one other (opaque) colour takes it; the eyes stay."""
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


def soften(a):
    """An outline-black square inside the figure with three or four 4-neighbours of one material (skin, trousers,
    coat, mantle, hair, gold) takes that material's darkest shade: the draft's thin inner lines (the abs, the folds)
    read back as black specks. Squares on the silhouette's edge stay."""
    cols, _ = palette()
    mat = {h: m for m, hs in PALETTE.items() for h in hs}
    darkest = {m: hs[0] for m, hs in PALETTE.items()}
    H, W = a.shape[:2]
    o = a.copy()
    name = lambda p: "%02X%02X%02X" % tuple(int(v) for v in p[:3])
    for r in range(1, H - 1):
        for c in range(1, W - 1):
            if not a[r, c, 3] or name(a[r, c]) not in DARK:
                continue
            nb = [a[r + dy, c + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            if any(not p[3] for p in nb):
                continue
            ms = [mat.get(name(p)) for p in nb]
            for m in set(ms) - {None, "outline"}:
                if ms.count(m) >= 3:
                    h = darkest[m] if m != "skin" else PALETTE["skin"][0]
                    o[r, c] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return o


def figure(rows=ROWS):
    """The figure, rows tall, cropped to its columns."""
    src = np.asarray(Image.open(lp(DRAFT)).convert("RGBA"))
    cols, pal = palette()
    ys, xs = np.nonzero(src[..., 3] > 128)
    bottom, x0, x1 = ys.max() + 1, xs.min(), xs.max() + 1
    px = (bottom - ys.min()) / rows                  # the draft's squares are square (regrid: ~8 x 8 px)
    W = int(np.ceil((x1 - x0) / px)) + 2
    left = (x0 + x1) / 2 - W * px / 2
    fig, feat = read_blocks(src, left, bottom, px, W, rows, cols, pal)
    fig = despeckle(fig, feat)
    fig = soften(fig)
    fig, _, _ = G.complete_outline(fig, feet=rows - 1)
    xs = np.nonzero(fig[..., 3].any(0))[0]
    fig = fig[:, xs.min():xs.max() + 1].copy()
    if rows == ROWS:
        for (x, y), h in FACE.items():
            fig[y, x] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return fig


def feet_left(fig):
    """The canvas column of the figure's first column: the middle of the feet (its lowest row) on column 64."""
    feet = np.nonzero(fig[-1, :, 3] > 0)[0]
    return int(round(64 - (feet.min() + feet.max() + 1) / 2))


def build(rows=ROWS):
    fig = figure(rows)
    canvas = np.zeros((128, 128, 4), np.uint8)
    cx = feet_left(fig)
    canvas[100 - rows:100, cx:cx + fig.shape[1]] = fig
    return canvas, fig


def candidates(out):
    """42 / 40 / 38 rows next to league_darius (42) and league_aatrox (40), at 1x and 6x on the arena colour."""
    import tfm2_ase
    os.makedirs(out, exist_ok=True)
    figs = [(f"{r} rows", build(r)[1]) for r in (42, 40, 38)]
    for name in ("darius", "aatrox"):
        f = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{name}")).frames[0]
        a = np.asarray(f)
        ys, xs = np.nonzero(a[..., 3] > 127)
        figs.append((name, a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]))
    for z in (1, 6):
        pad = 4 * z
        H = max(f.shape[0] for _, f in figs) * z
        W = sum(f.shape[1] * z + pad for _, f in figs) + pad
        img = Image.new("RGBA", (W, H + 2 * pad), tfm2_ase.ARENA_BG)
        x = pad
        for _, f in figs:
            im = Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST)
            img.alpha_composite(im, (x, pad + H - im.height))
            x += im.width + pad
        img.convert("RGB").save(os.path.join(out, f"sett_rows_{z}x.png"))
    for r in (42, 40, 38):
        Image.fromarray(np.repeat(np.repeat(build(r)[0], 8, 0), 8, 1)).save(os.path.join(out, f"sett_native_{r}.png"))
    print("wrote", ", ".join(sorted(os.listdir(out))))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=ROWS)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing it")
    ap.add_argument("--candidates", help="write 42 / 40 / 38-row candidates and comparison sheets into this folder")
    a = ap.parse_args()
    if a.candidates:
        candidates(a.candidates)
        return
    canvas, fig = build(a.rows)
    big = Image.fromarray(np.repeat(np.repeat(canvas, 8, 0), 8, 1))
    if a.check:
        old = np.asarray(Image.open(lp(a.out)).convert("RGBA"))
        same = old.shape == np.asarray(big).shape and (old == np.asarray(big)).all()
        print("identical" if same else "DIFFERENT", a.out)
        sys.exit(0 if same else 1)
    big.save(lp(a.out))
    op = fig[..., 3] > 0
    n = len(np.unique(fig[op][:, :3], axis=0))
    print(f"{a.out}: {fig.shape[1]}x{fig.shape[0]}, {n} colours, {int(op.sum())} px")


if __name__ == "__main__":
    main()
