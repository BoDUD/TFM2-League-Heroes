#!/usr/bin/env python3
"""Pyke's design (assets/source/native/pyke_native.png): Codex's generated draft read back on its own grid and shrunk
by whole rows and columns, every kept square the draft's own (tools/art/design_xerath.py's way).

    python tools/art/design_pyke.py [--body 40] [--raw A-second] [--sheet out.png] [--check]

How it came about (2026-10-06): the user picked Codex's picture A (codex_picture/pyke-model-A.png: League's idle,
crouched, the harpoon raised). Codex's step 1 (codex_model/) sampled its own drafts to 40 rows by grid centres and
they broke into specks (the lesson of Kai'Sa / Ryze / Xerath: never read a draft at fewer rows than it was drawn).
Steps:
  1. codex_model/raw/<raw>.png read back on its own grid (the skill's regrid.py, alpha >= 128): A-second is 72 x 86
     (the harpoon's blade over his head included), the bald head's top on row 18, the soles on row 71;
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. rows in three parts, each shrunk by design_riven.pick (in groups, the row most like a neighbour goes, the
     offset that loses least): the harpoon over his head (rows 0 to the head's top) to HARPOON_ROWS, the face
     (FACE_ROWS: the head's top, the glowing eyes, the mask's top) whole, the rest of the body to the target; then the
     columns: the part left of FACE_COLS (the harpoon's hook and the raised arm) and the part right of it shrunk alike
     to WIDTH, FACE_COLS whole;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  6. EYES: the read-back's eyes are dark teal (the draft's #00FFFF glow sat on square edges); the three eye squares
     get the picture's glow (the near eye cyan with a white-cyan glint, the far eye cyan).
The user picked 40 rows (「40 行」, 62 x 53) from the options sheet (40 with the blade cut to 6 rows, 40, 44, 48).
--sheet writes the options beside the pack's heroes instead; --check compares with the committed pyke_native.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
import tfm2_ase  # noqa: E402
from regrid import regrid  # noqa: E402

RAWS = os.path.join(ROOT, "assets", "source", "pyke", "codex_model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "native", "pyke_native.png")
K = 28
# on the A-second read-back (72 x 86)
HEAD_TOP, SOLES = 18, 71
FACE_ROWS = range(18, 31)          # the bald head's top, the glowing eyes (rows 26-27), the mask's top
FACE_COLS = range(50, 64)
SOLE_ROW, MID_COL = 99, 64
EYES = {(69, 72): (32, 216, 224), (69, 73): (200, 255, 255), (69, 77): (32, 216, 224)}   # canvas (row, col)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(RAWS, name + ".png"))).convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def shrink(lines, n_out):
    """design_riven.pick at the offset that loses least; all lines when nothing is to go."""
    if n_out >= len(lines):
        return list(range(len(lines)))
    best = None
    for off in range(3):
        k, lost = R.pick(lines, n_out, off)
        if k is not None and (best is None or lost < best[1]):
            best = (k, lost)
    return best[0]


def build(raw_name="A-second", body=40, harpoon=None, width=None):
    raw = read_back(raw_name)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    # rows: harpoon part over the head, the face whole, the body below the face
    top = list(range(0, HEAD_TOP))
    low = list(range(FACE_ROWS.stop, H))
    n_low = body - len(FACE_ROWS)
    n_top = harpoon if harpoon is not None else round(len(top) * n_low / len(low))
    rows = ([top[i] for i in shrink([idx[r] for r in top], n_top)] + list(FACE_ROWS)
            + [low[i] for i in shrink([idx[r] for r in low], n_low)])
    sub = idx[rows]
    left = list(range(0, FACE_COLS.start))
    right = list(range(FACE_COLS.stop, W))
    scale = n_low / len(low)
    target_w = width if width is not None else round(len(FACE_COLS) + (len(left) + len(right)) * scale)
    n_side = target_w - len(FACE_COLS)
    n_left = round(n_side * len(left) / (len(left) + len(right)))
    cols = ([left[i] for i in shrink([sub[:, c] for c in left], n_left)] + list(FACE_COLS)
            + [right[i] for i in shrink([sub[:, c] for c in right], n_side - n_left)])
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [i for i, r in enumerate(rows) if r in FACE_ROWS]
    fc = [i for i, c in enumerate(cols) if c in FACE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero(fig[-3:, :, 3].max(0) > 0)[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    head_top = SOLE_ROW + 1 - body
    return out, rows, cols, added, head_top


def info(can):
    ys, xs = np.nonzero(can[..., 3] > 0)
    return (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols "
            f"{xs.min()}-{xs.max()}), {len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours")


def crop(can):
    ys, xs = np.nonzero(can[..., 3] > 0)
    return Image.fromarray(can[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def sheet(path, options):
    """The options at 6x on one soles line, Codex's own A cut and the pack's heroes beside them."""
    z, pad = 6, 30
    shots = [(label, crop(can)) for label, can in options]
    codex = Image.open(lp(os.path.join(ROOT, "assets", "source", "pyke", "codex_model", "pyke_design_A_1x.png")))
    shots.append(("Codex's own A (40)", codex.crop(codex.getchannel("A").getbbox())))
    for h in ("jhin", "kayn", "xinzhao", "tryndamere"):
        sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{h}"))
        f = sp.frames[sp.tag_frames("idle")[0]]
        shots.append((f"{h}", f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox())))
    tall = max(s.height for _, s in shots) * z
    w = sum(s.width * z + pad for _, s in shots) + pad
    img = Image.new("RGBA", (w, tall + 2 * pad + 20), (236, 236, 230, 255))
    d = ImageDraw.Draw(img)
    x = pad
    for label, s in shots:
        big = s.resize((s.width * z, s.height * z), Image.NEAREST)
        img.alpha_composite(big, (x, pad + tall - big.height))
        d.text((x, pad + tall + 6), f"{label} {s.width}x{s.height}", fill=(0, 0, 0, 255))
        x += big.width + pad
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", type=int, default=40)
    ap.add_argument("--raw", default="A-second")
    ap.add_argument("--sheet")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.sheet:
        opts = []
        for body, harp in ((40, 6), (40, None), (44, 7), (48, 8)):
            can = build(a.raw, body, harp)[0]
            label = f"{body} rows" + (f", blade +{harp}" if harp else "")
            print(label, info(can))
            opts.append((label, can))
        sheet(a.sheet, opts)
        print("wrote", a.sheet)
        return
    can, rows, cols, added, _ = build(a.raw, a.body)
    for (y, x), rgb in EYES.items():
        assert can[y, x, 3] and tuple(can[y, x, :3]) != (5, 3, 3), (y, x)
        can[y, x, :3] = rgb
    text = f"{info(can)}, outline +{added}; rows kept {rows}; columns kept {cols}"
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", text)
        return
    Image.fromarray(can).save(lp(OUT))
    print(OUT, text)


if __name__ == "__main__":
    main()
