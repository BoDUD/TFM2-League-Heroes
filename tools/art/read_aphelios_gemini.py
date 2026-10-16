#!/usr/bin/env python3
"""Read the user's Gemini pictures of Aphelios's last effects (tools/art/pack_aphelios_fx_gemini.py: swap, r_cast, r_moon,
r_boom, r_hit, mw, g_slow, q_s_haste, cre; the user, 2026-10-16: Gemini instead of waiting for Codex's quota) into
game-size strips like Codex's read-backs, so tools/art/import_aphelios_fx.py takes them as it takes the rest.

    python tools/art/read_aphelios_gemini.py [--review DIR] [name ...]

Source: assets/source/aphelios/gemini_fx/aphelios_fx_<name>.(png|jpg|jpeg|webp), the frames in GRID (columns, rows;
the template's one row unless listed), on black. Each cell: the cell lines (EDGE px of its sides) and the black keyed
out, then import_kassadin.py's read: one scale for the effect (the source cell onto the pack's cell, cw x ch game px,
or SIZE: its biggest frame's content to n game px), every game pixel the commonest colour under it snapped to the
prompt's ramp (a bright colour wins from a fifth: the white cores stay), lone dark specks dropped, the red side's
symmetry - r_moon top to bottom, the rest left to right about the frame's own best axis (the fuller half mirrored).
Each frame keeps its place in its cell (scaled), so a figure's feet stay on the cell's bottom row.
Writes assets/source/aphelios/codex_fx/pixel_1x/aphelios_fx_<name>.png: the frames side by side in cw x ch cells.
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
sys.path.insert(0, HERE)
import import_kassadin as K  # noqa: E402
import pack_aphelios_fx as PK  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
from pack_aphelios_fx_gemini import REST, cells  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aphelios", "gemini_fx")
OUT = os.path.join(ROOT, "assets", "source", "aphelios", "codex_fx", "pixel_1x")
EDGE = 4                         # px off each cell's sides (the template's lines, if Gemini kept them)
GRID = {}                        # name -> (columns, rows) when Gemini laid the frames out otherwise
SIZE = {}                        # name -> ("w" | "h", n): the biggest frame's content to n game px (else the cell's scale)
SYM = {"r_moon": "tb"}           # every other one "lr"
LAYOUT = cells()


def ramp(name):
    return [h for h in REST[name][3].split(", ")]


def use_ramp(names):
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in names]
    K.PAL = np.array(cols, np.uint8)
    K.PAL_LAB = srgb2lab(K.PAL.astype(float))
    K.PAL_LUM = K.PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
    K.DARKS = {cols[-1], cols[-2]}


def key(rgb):
    """Black (or near-black JPEG noise) out; grey cell lines out unless bright."""
    mx, mn = rgb.max(-1), rgb.min(-1)
    a = (mx > 40) & ((mx - mn > 18) | (mn > 170))
    return np.where(a, 255, 0).astype(np.int16)


def source(name):
    for ext in ("png", "jpg", "jpeg", "webp"):
        hits = glob.glob(os.path.join(SRC, f"aphelios_fx_{name}.{ext}"))
        if hits:
            return hits[0]
    return None


def read(name):
    n, cw, ch = LAYOUT[name]
    cols, rows = GRID.get(name, (n, 1))
    rgb = np.asarray(Image.open(source(name)).convert("RGB")).astype(np.int16)
    H, W = rgb.shape[:2]
    sw, sh = W / cols, H / rows
    crops = []
    for k in range(n):
        c, r = k % cols, k // cols
        x0, x1 = int(round(c * sw)) + EDGE, int(round((c + 1) * sw)) - EDGE
        y0, y1 = int(round(r * sh)) + EDGE, int(round((r + 1) * sh)) - EDGE
        p = rgb[y0:y1, x0:x1]
        crops.append(np.concatenate([p, key(p)[..., None]], -1))
    # one scale: the source cell onto the game cell (or SIZE)
    s_cell = min(cw / sw, ch / sh)
    if name in SIZE:
        dim, target = SIZE[name]
        ext = []
        for a in crops:
            ys, xs = np.nonzero(a[..., 3] > 0)
            if len(xs):
                ext.append((xs.max() - xs.min() + 1) if dim == "w" else (ys.max() - ys.min() + 1))
        s = target / max(ext)
    else:
        s = s_cell
    use_ramp(ramp(name))
    sym = SYM.get(name, "lr")
    out = []
    for a in crops:
        ys, xs = np.nonzero(a[..., 3] > 0)
        cell = np.zeros((ch, cw, 4), np.uint8)
        if not len(xs):
            out.append(cell)
            continue
        sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        g = K.shrink(sub, s)
        m = g[..., 3] > 0
        if not m.any():
            out.append(cell)
            continue
        if sym == "lr":
            gx = np.nonzero(m.any(0))[0]
            g = K.mirror_lr(g, K.best_axis(m, int(gx.min()), int(gx.max())))
        else:
            gy = np.nonzero(m.any(1))[0]
            g = K.mirror_tb(g, K.best_axis(np.ascontiguousarray(m.T), int(gy.min()), int(gy.max())))
        g = K.despeckle(g)
        gm = g[..., 3] > 0
        gy, gx = np.nonzero(gm)
        g = g[gy.min():gy.max() + 1, gx.min():gx.max() + 1]
        h, w = g.shape[:2]
        # its place in the cell: across, the cell's middle (lr) or its own place scaled (tb); down, its middle scaled
        # (tb), its own bottom scaled (lr: a figure's feet stay on the bottom row)
        if sym == "lr":
            x = (cw - w) // 2
            y = int(round((ys.max() + 1 + EDGE) * s_cell)) - h if REST[name][1] else \
                int(round((ys.min() + ys.max() + 1 + 2 * EDGE) / 2 * s_cell - h / 2))
        else:
            x = int(round((xs.min() + EDGE) * s_cell))
            y = (ch - h) // 2
        x, y = min(max(0, x), max(0, cw - w)), min(max(0, y), max(0, ch - h))
        cell[y:y + min(h, ch), x:x + min(w, cw)] = g[:ch - y, :cw - x]
        if sym == "lr" and cw % 2 == 0 and w % 2 == 1:
            pass                            # an odd picture in an even cell: half a square right of the middle
        out.append(cell)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--review", help="write the read strips at 8x here")
    a = ap.parse_args()
    names = a.names or [n for n in REST if source(n)]
    if not names:
        sys.exit(f"no pictures in {SRC}")
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        if not source(name):
            print(name, "not there yet")
            continue
        cs = read(name)
        strip = np.concatenate(cs, 1)
        Image.fromarray(strip).save(os.path.join(OUT, f"aphelios_fx_{name}.png"))
        print(name, f"{len(cs)} frames of {cs[0].shape[1]}x{cs[0].shape[0]}",
              "drawn", [int((c[..., 3] > 0).sum()) for c in cs])
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            big = Image.fromarray(strip).resize((strip.shape[1] * 8, strip.shape[0] * 8), Image.NEAREST)
            bg = Image.new("RGBA", big.size, (20, 22, 30, 255))
            bg.alpha_composite(big)
            bg.convert("RGB").save(os.path.join(a.review, f"gemini_{name}.png"))


if __name__ == "__main__":
    main()
