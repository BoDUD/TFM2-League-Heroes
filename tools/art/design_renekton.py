#!/usr/bin/env python3
"""Renekton's design (assets/source/native/renekton_native.png): Codex's generated draft read back on its own grid,
narrowed by whole columns in the blade-and-tail zone only (tools/art/design_twitch.py's way).

    python tools/art/design_renekton.py [--raw B] [--width 60] [--sheet out.png] [--check]

The user picked Codex's picture A (codex_picture/renekton-model-A.png, 2026-10-07: League's idle, the blade trailing)
and then gave the blade picture B's shape (「鳄鱼的斧头应该是这形状的」). Codex's step 1 (codex_model/) cut its drafts
to 38 / 40 rows and 53 / 56 columns itself, deleting columns through the body and the face (specks). Steps here:
  1. codex_model/raw/renekton_<A|B>_weapon_corrected.png read back on its own grid (the skill's regrid.py, alpha >=
     128): A 72 x 39, B 76 x 41 (the helmet's top on row 0, the soles on the last row) - the height is kept;
  2. every square one of K colours of the read-back's own (design_varus.kmeans);
  3. columns: only those left of BACK[name] (the blade and the tail; the body, the head and the claws start there)
     go, design_riven.pick choosing the ones that lose least, until the figure is --width wide;
  4. strips.complete_outline where a deleted column held the outline;
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the feet (the lowest three rows) on column 64;
  6. clean: colours used by RARE squares or fewer take the nearest of the others, a lone near-black square inside the
     figure takes its darkest neighbour's colour.
--sheet writes the options beside Codex's own cuts and the pack's heroes; --check compares with the committed file.
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
import design_varus as dv  # noqa: E402
import strips  # noqa: E402
import tfm2_ase  # noqa: E402
from design_twitch import shrink  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renekton", "codex_model")
OUT = os.path.join(ROOT, "assets", "source", "native", "renekton_native.png")
K = 28
BACK = {"A": 30, "B": 28}         # the first column of the body (the back pauldron); left of it only blade and tail
OPTIONS = (("A", 0), ("A", 60), ("B", 0), ("B", 64), ("B", 58))
SOLE_ROW, MID_COL = 99, 64
RARE = 3


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"renekton_{name}_weapon_corrected.png")))
                                  .convert("RGBA")))
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def build(name="B", width=0):
    """width 0: as read back."""
    raw = read_back(name)
    idx, pal = dv.kmeans(raw, K)
    H, W = idx.shape
    zone = list(range(0, BACK[name]))
    n_zone = len(zone) - max(0, W - width) if width else len(zone)
    cols = [zone[i] for i in shrink([idx[:, c] for c in zone], n_zone)] + list(range(BACK[name], W))
    small = idx[:, cols]
    fig = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    fig[m, :3] = pal[small[m]]
    fig[m, 3] = 255
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, added, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0])
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero(fig[-3:, :, 3].max(0) > 0)[0]
    mid_x = (feet.min() + feet.max()) / 2
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - mid_x))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out, cols, added


def clean(can):
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
            if dark[y, x] and all(op[q] and not dark[q] for q in nb):
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
        codex = Image.open(lp(os.path.join(SRC, f"renekton_design_{v}_1x.png"))).convert("RGBA")
        shots.append((f"Codex {v}", codex.crop(codex.getchannel("A").getbbox())))
    for h in ("tryndamere", "darius"):
        sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", "champions", f"league_{h}"))
        f = sp.frames[sp.tag_frames("idle")[0]]
        shots.append((h, f.crop(f.getchannel("A").point(lambda v: 255 if v > 127 else 0).getbbox())))
    rows = [shots[:len(options)], shots[len(options):]]
    tall = max(s.height for _, s in shots) * z
    w = max(sum(s.width * z + pad for _, s in r) for r in rows) + pad
    img = Image.new("RGBA", (w, 2 * (tall + pad + 20) + pad), (236, 236, 230, 255))
    d = ImageDraw.Draw(img)
    for k, r in enumerate(rows):
        top = pad + k * (tall + pad + 20)
        x = pad
        for label, s in r:
            big = s.resize((s.width * z, s.height * z), Image.NEAREST)
            img.alpha_composite(big, (x, top + tall - big.height))
            d.text((x, top + tall + 4), f"{label} {s.width}x{s.height}", fill=(0, 0, 0, 255))
            x += big.width + pad
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="B")
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--sheet")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.sheet:
        opts = []
        for name, width in OPTIONS:
            can = clean(build(name, width)[0])[0]
            print(name, width, info(can))
            opts.append((f"{name} {width or 'full'}", can))
        sheet(a.sheet, opts)
        print("wrote", a.sheet)
        return
    can, cols, added = build(a.raw, a.width)
    can, fixed = clean(can)
    text = f"{info(can)}, outline +{added}, inner ink {fixed}; columns kept {cols}"
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", text)
        return
    Image.fromarray(can).save(lp(OUT))
    print(OUT, text)


if __name__ == "__main__":
    main()
