#!/usr/bin/env python3
"""Alistar's run from Codex's skin swap -> assets/source/native/alistar_run.png (8x, the run cells of alistar_cells.json).

    python tools/art/run_alistar.py

History: every run built on the design's frozen upper body read as unnatural - one leg, no crossing, Codex's squeezed
stick legs, then a measured stride on full-width legs that the user still called 「不自然」. oppi's Alistar run (LoL
Reborn) showed what was missing: the fists pump opposite the legs, the recovering leg bends and kicks the hoof up
behind, the body bobs and leans. So the run was redrawn by skin swap (the user's skeleton + skin method): oppi's 9
frames as the motion skeleton, our design as the skin, 3 x 3 cells of 56 squares on #00FF00
(assets/source/alistar/codex_run_swap/: Codex's picture, its HANDOFF, the prompt and our design image; oppi's own
frames are not redistributed here).

Import: key the green out, read each cell back on the pack's grid (1254 px / 168 squares), snap every square to the
design's own colours (CIELAB nearest), keep the largest piece and what touches it, set each frame where Codex drew it
in its cell (the pack put the design's standing point at cell column 27, its soles on row 50 -> here the run cell's
standing point (60, 70), soles on row 81), close the outline and shut enclosed holes. 9 frames x 111 ms = League's
1 s cycle.
"""
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
import strips as G  # noqa: E402
sys.path.insert(0, HERE)
from native_refs import layout  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "alistar_native.png")
CELLS = os.path.join(NATIVE, "alistar_cells.json")
OUT = os.path.join(NATIVE, "alistar_run.png")
SWAP = os.path.join(ROOT, "assets", "source", "alistar", "codex_run_swap", "alistar_run_swap.png")
PIVOT = (64, 88)                  # the design canvas's standing point; its soles on row 99
SOLE = 99
OUTLINE = (0x12, 0x03, 0x19)
CHAIN = {(0x44, 0x3A, 0x3F), (0xA8, 0x82, 0x6E)}                                 # the far shackle's chain
CLOTH = {(0x87, 0x3E, 0x28), (0xC8, 0x67, 0x2F), (0xF5, 0xB7, 0x43), (0xFB, 0xD5, 0x9B), (0x42, 0x17, 0x14)}
# the legs on the design canvas: (rows, columns) boxes; the hooves (rows 95-99) whole, above them the fur only
LEGS = {"far": dict(top=86, x0=44, x1=60, hip=(54.0, 87.0), chain_x=49),
        "near": dict(top=86, x0=60, x1=74, hip=(66.0, 87.0), chain_x=None)}
HOOF_ROW = 95
CELL = (128, 96)
CELL_PIVOT = (60, 70)             # the soles on row 81
PACK_CELL = 56                    # squares per swap-pack cell
PACK_PIVOT = (27, 50)             # the design's standing point in a pack cell (soles row 50)
FRAMES = 9
MS = 111


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def col(p):
    return tuple(int(v) for v in p[:3])


def split(des):
    """The two legs' masks and the upper body (the design without them) - used by the earlier run packs."""
    op = des[..., 3] > 0
    masks = {}
    for name, L in LEGS.items():
        m = np.zeros(op.shape, bool)
        for y in range(L["top"], SOLE + 1):
            for x in range(L["x0"], L["x1"]):
                if not op[y, x]:
                    continue
                c = col(des[y, x])
                if y >= HOOF_ROW:
                    m[y, x] = True
                    continue
                if c in CLOTH or (L["chain_x"] is not None and x < L["chain_x"] and c in CHAIN | {OUTLINE}):
                    continue
                if c in CHAIN:
                    continue
                m[y, x] = True
        masks[name] = m
    masks["far"] &= ~masks["near"]
    upper = des.copy()
    for m in masks.values():
        upper[m] = 0
    return masks, upper


def lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def pieces(op):
    labs = np.zeros(op.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if labs[y, x]:
            continue
        n += 1
        st = [(y, x)]
        labs[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not labs[ny, nx]:
                        labs[ny, nx] = n
                        st.append((ny, nx))
    return labs, n


def holes(op):
    H, W = op.shape
    out = np.zeros_like(op)
    q = deque((y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and not op[y, x])
    for p in q:
        out[p] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                q.append((ny, nx))
    return list(zip(*np.nonzero(~op & ~out)))


def read_cell(im, k, pal, pal_lab):
    """Cell k of the swap picture on its grid, snapped to the design's colours; with its place in the pack cell."""
    H, W = im.shape[:2]
    s = W / (3 * PACK_CELL)
    y0, x0 = round((k // 3) * H / 3), round((k % 3) * W / 3)
    c = im[y0:round((k // 3 + 1) * H / 3), x0:round((k % 3 + 1) * W / 3)]
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    green = (g > r * 1.25 + 20) & (g > b * 1.25 + 20)
    a = np.zeros(c.shape[:2] + (4,), np.uint8)
    a[..., :3] = c
    a[..., 3] = (~green) * 255
    grid, _, (bx, by) = RG.regrid(a, s)
    op = grid[..., 3] > 127
    d = ((lab(grid[..., :3])[..., None, :] - pal_lab[None, None]) ** 2).sum(-1)
    out = np.zeros_like(grid)
    out[..., :3] = pal[d.argmin(-1)]
    out[..., 3] = op * 255
    labs, n = pieces(op)
    if n > 1:                                                         # keep the body; drop specks of the backdrop
        sizes = [(labs == i).sum() for i in range(1, n + 1)]
        big = 1 + int(np.argmax(sizes))
        for i in range(1, n + 1):
            if i != big and sizes[i - 1] < 6:
                out[labs == i] = 0
    return out, bx[0] / s, by[-1] / s                                # left column / bottom edge in pack squares


def build():
    des = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[4::8, 4::8]
    pal = np.array(sorted({col(p) for p in des[des[..., 3] > 0]}))
    pal_lab = lab(pal)
    im = np.asarray(Image.open(lp(SWAP)).convert("RGB")).astype(int)
    cols, rows = layout(FRAMES)
    strip = np.zeros((rows * CELL[1], cols * CELL[0], 4), np.uint8)
    report = []
    for k in range(FRAMES):
        g, left, bottom = read_cell(im, k, pal, pal_lab)
        X = int(round(left)) - PACK_PIVOT[0] + CELL_PIVOT[0]
        Y = int(round(bottom)) - g.shape[0] - (PACK_PIVOT[1] + 1) + CELL_PIVOT[1] + 12
        can = np.zeros((CELL[1], CELL[0], 4), np.uint8)
        m = g[..., 3] > 0
        can[Y:Y + g.shape[0], X:X + g.shape[1]][m] = g[m]
        pad = np.pad(can, ((2, 2), (2, 2), (0, 0)))
        pad, _, _ = G.complete_outline(pad, color=OUTLINE, feet=CELL_PIVOT[1] + 13)
        can = pad[2:-2, 2:-2].copy()
        can[CELL_PIVOT[1] + 12:] = 0
        for y, x in holes(can[..., 3] > 0):
            can[y, x] = (*OUTLINE, 255)
        strip[(k // cols) * CELL[1]:(k // cols + 1) * CELL[1], (k % cols) * CELL[0]:(k % cols + 1) * CELL[0]] = can
        ys, xs = np.nonzero(can[..., 3])
        report.append((k + 1, int(ys.max() - ys.min() + 1), int(ys.max()), int(xs.min()), int(xs.max())))
    return strip, report


def main():
    strip, report = build()
    Image.fromarray(strip).resize((strip.shape[1] * 8, strip.shape[0] * 8), Image.NEAREST).save(lp(OUT))
    cells = json.load(open(lp(CELLS), encoding="utf-8"))
    cells["tags"]["run"] = [{"pivot": list(CELL_PIVOT), "ms": MS} for _ in range(FRAMES)]
    with open(lp(CELLS), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(cells, ensure_ascii=False, indent=1) + "\n")
    for r in report:
        print("frame %d: %d rows, soles row %d, columns %d-%d" % r)


if __name__ == "__main__":
    main()
