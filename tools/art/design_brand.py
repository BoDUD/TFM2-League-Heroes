#!/usr/bin/env python3
"""Brand's design (assets/source/native/brand_native.png): Codex's generated draft read back on its own grid and
shrunk by whole rows and columns, every kept square the draft's own (tools/art/design_pyke.py's way).

    python tools/art/design_brand.py [--raw A] [--body 37] [--sheet out.png] [--check]

How it came about (2026-10-06): the user picked Codex's picture A (codex_picture/brand-model-A.png: League's idle, a
slight crouch, both fire hands open, flames on the head). Codex's step 1 (codex_model/) sampled its own drafts to 37
rows by grid centres and they broke into specks (Kai'Sa / Ryze / Xerath / Pyke: never read a draft at fewer rows than
it was drawn). Steps:
  1. codex_model/raw/brand_<A|B>_raw.png read back on its own grid (the skill's regrid.py, alpha >= 128): A 74 x 57
     (the bald crown on row 9, the eyes on row 19, the soles on row 73), B 66 x 51 (crown 10, eyes 18, soles 64);
  2. every square one of K colours of the read-back's own (design_varus.kmeans: CIELAB, farthest-point start, seed 1);
  3. rows in four parts, each shrunk by design_riven.pick (in groups, the row most like a neighbour goes, the offset
     that loses least): the flames over the crown, the skull (the crown to the eye rows), the eye rows (FACE_ROWS)
     whole, the rest of the body; the flames and the skull keep the body's share. Then the columns: left of
     FACE_COLS (the back fire hand) and right of it (the front hand) shrunk alike, FACE_COLS whole;
  4. strips.complete_outline where a deleted line held the outline (the face never touched);
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  6. clean (the user picked A at 37 rows, 「A 37」): k-means colours used by RARE squares or fewer take the nearest of
     the others (single off-shade specks), and a lone near-black square inside the figure outside the face (all four
     neighbours lit material) takes its darkest neighbour's colour (oppi: one black ring, outside);
  7. CHIN: the lava crack right under the chin (rows 74-75) read as a bloody open mouth (「嘴上这是什么 怎么看的这么怪」):
     its seven squares take the neck's purple-greys and the shadow under the chin.
--sheet writes the options (A and B at 37 / 40 / 44 rows crown to soles) beside Codex's own cuts and the pack's
heroes; --check compares with the committed brand_native.png.
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

SRC = os.path.join(ROOT, "assets", "source", "brand", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "native", "brand_native.png")
K = 28
# per read-back: the bald crown's row, the soles' row, the eye rows kept whole, the face's columns kept whole
RAWS = {
    "A": {"crown": 9, "soles": 73, "face_rows": range(16, 22), "face_cols": range(28, 43)},
    "B": {"crown": 10, "soles": 64, "face_rows": range(15, 21), "face_cols": range(24, 39)},
}
SOLE_ROW, MID_COL = 99, 64
RARE = 3
CHIN = {(74, 70): (0x35, 0x21, 0x34), (74, 71): (0x35, 0x21, 0x34), (74, 72): (0x21, 0x12, 0x1E),
        (75, 68): (0x21, 0x12, 0x1E), (75, 69): (0x45, 0x36, 0x46), (75, 70): (0x45, 0x36, 0x46),
        (75, 71): (0x35, 0x21, 0x34)}                                  # canvas (row, col) of the A 37 design


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"brand_{name}_raw.png"))).convert("RGBA")))
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


def build(name="A", body=37):
    cfg = RAWS[name]
    raw = read_back(name)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    face, crown, soles = cfg["face_rows"], cfg["crown"], cfg["soles"]
    flames, skull, low = list(range(0, crown)), list(range(crown, face.start)), list(range(face.stop, H))
    scale = (body - len(face)) / (soles + 1 - crown - len(face))
    parts = [(flames, round(len(flames) * scale)), (skull, round(len(skull) * scale))]
    parts.append((low, body - len(face) - parts[1][1]))
    rows = []
    for lines, n in parts[:2]:
        rows += [lines[i] for i in shrink([idx[r] for r in lines], n)]
    rows += list(face)
    rows += [low[i] for i in shrink([idx[r] for r in low], parts[2][1])]
    sub = idx[rows]
    fc = cfg["face_cols"]
    left, right = list(range(0, fc.start)), list(range(fc.stop, W))
    n_side = round((len(left) + len(right)) * scale)
    n_left = round(n_side * len(left) / (len(left) + len(right)))
    cols = ([left[i] for i in shrink([sub[:, c] for c in left], n_left)] + list(fc)
            + [right[i] for i in shrink([sub[:, c] for c in right], n_side - n_left)])
    small = idx[np.ix_(rows, cols)]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [i for i, r in enumerate(rows) if r in face]
    fcc = [i for i, c in enumerate(cols) if c in fc]
    keep[fr[0]:fr[-1] + 1, fcc[0]:fcc[-1] + 1] = True
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
    face_box = np.zeros((128, 128), bool)
    face_box[y0 + 1 + fr[0]:y0 + 2 + fr[-1], x0 + 1 + fcc[0]:x0 + 2 + fcc[-1]] = True
    return out, rows, cols, added, face_box


def clean(can, face_box):
    """Step 6: rare off-shades to their nearest colour, lone inner near-black squares to their darkest neighbour."""
    out = can.copy()
    op = out[..., 3] > 0
    cols, counts = np.unique(out[op][:, :3], axis=0, return_counts=True)
    common = cols[counts > RARE].astype(int)
    for c in cols[counts <= RARE]:
        near = common[np.argmin(((common - c.astype(int)) ** 2).sum(1))]
        out[op & (out[..., :3] == c).all(-1), :3] = near
    lum = (out[..., :3] * [0.299, 0.587, 0.114]).sum(-1)
    dark = op & (lum < 25)
    H, W = op.shape
    fixed = []
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            nb = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
            if dark[y, x] and not face_box[y, x] and all(op[q] and not dark[q] for q in nb):
                q = min(nb, key=lambda q: lum[q])
                out[y, x, :3] = out[q][:3]
                fixed.append((y, x))
    return out, fixed


def info(can):
    ys, xs = np.nonzero(can[..., 3] > 0)
    return (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols "
            f"{xs.min()}-{xs.max()}), {len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours")


def crop(can):
    ys, xs = np.nonzero(can[..., 3] > 0)
    return Image.fromarray(can[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def sheet(path, options, z=6):
    """The options at z on one soles line, Codex's own cuts and the pack's heroes beside them."""
    pad = 30
    shots = [(label, crop(can)) for label, can in options]
    for v in ("A", "B"):
        codex = Image.open(lp(os.path.join(SRC, f"brand_design_{v}_1x.png"))).convert("RGBA")
        shots.append((f"Codex {v}", codex.crop(codex.getchannel("A").getbbox())))
    for h in ("xerath", "pyke", "tryndamere"):
        sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{h}"))
        f = sp.frames[sp.tag_frames("idle")[0]]
        shots.append((h, f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox())))
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
    ap.add_argument("--raw", default="A")
    ap.add_argument("--body", type=int, default=37)
    ap.add_argument("--sheet")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.sheet:
        opts = []
        for name in ("A", "B"):
            for body in (37, 40, 44):
                b = build(name, body)
                can = clean(b[0], b[4])[0]
                print(name, body, info(can))
                opts.append((f"{name} {body}", can))
        sheet(a.sheet, opts)
        print("wrote", a.sheet)
        return
    can, rows, cols, added, face_box = build(a.raw, a.body)
    can, fixed = clean(can, face_box)
    if a.raw == "A" and a.body == 37:
        for (y, x), rgb in CHIN.items():
            assert can[y, x, 3], (y, x)
            can[y, x, :3] = rgb
    text = f"{info(can)}, outline +{added}, inner ink {fixed}; rows kept {rows}; columns kept {cols}"
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", text)
        return
    Image.fromarray(can).save(lp(OUT))
    print(OUT, text)


if __name__ == "__main__":
    main()
