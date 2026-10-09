#!/usr/bin/env python3
"""Talon's action strips from Codex's per-frame drawings (step 2: assets/source/talon/MODEL_STRIPS.md, one generator
image per frame) -> assets/source/native/talon_<tag>.png + talon_cells.json for tools/art/import_native.py.

    python tools/art/fix_talon_strips.py [--src DIR] [--review DIR]

Per frame (SRC/<tag>_<kk>.png, the 120 x 112 cell at 8x):
  1. read back on its own grid: the block size / offset that make the 8x8 blocks most uniform (Codex was asked for
     8 px squares from the corner; a drawing on another grid is read on that one), one game pixel = the block's
     commonest colour, opaque when most of the block is;
  2. every pixel snapped to the design's 22 colours (CIELAB), near-blacks to the outline colour;
  3. specks of 1-2 pixels not touching the figure dropped, nothing under the soles' row (pivot + FEET);
  4. the run: the design's upper body (canvas rows <= HIP) pasted over Codex's at the frame's standing point, moved
     by the frame's bob (Codex's own head top against the design's), only the legs and the hem below stay Codex's -
     a loop's body must be the approved design, pixel for pixel (the Hecarim lesson);
  5. strips.complete_outline closes the outline.
The idle is the design itself at every idle frame's point (import_native breathes it). --review writes a sheet of
every frame at 6x beside League's frame.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import layout  # noqa: E402
import design_talon as D  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "talon", "codex_strips", "frames")
CELLS = os.path.join(ROOT, "assets", "source", "talon", "talon_cells.json")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z, FEET = 8, 11
HIP = 87                 # the design canvas's last upper-body row (the run keeps rows <= HIP from the design)
TAGS = ["run", "attack", "skill", "skill2", "skill2_stab", "skill_e", "ult", "hit", "dead"]
lp = D.lp


def lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


PAL_RGB = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in D.PAL.values()], float)
PAL_LAB = lab(PAL_RGB)
OUTLINE = tuple(int(v) for v in PAL_RGB[list(D.PAL).index("k")])


def read_grid(a, cw, ch):
    """The drawing read back on its grid: (ch, cw, 4) uint8. Tries block sizes 7-9 px and every offset."""
    H, W = a.shape[:2]
    best = None
    for s in (8, 7.5, 8.5, 7, 9):
        for oy in range(int(s)):
            for ox in range(int(s)):
                ys = (oy + (np.arange(int((H - oy) / s)) + 0.5) * s).astype(int)
                xs = (ox + (np.arange(int((W - ox) / s)) + 0.5) * s).astype(int)
                if len(ys) < 10 or len(xs) < 10:
                    continue
                c = a[ys][:, xs]
                # uniformity: the centre pixel against its 4 neighbours one pixel away
                nb = [a[np.clip(ys + dy, 0, H - 1)][:, np.clip(xs + dx, 0, W - 1)] for dy, dx in ((-2, 0), (2, 0), (0, -2), (0, 2))]
                err = np.mean([np.abs(c.astype(int) - n.astype(int)).sum(-1).mean() for n in nb])
                if best is None or err < best[0]:
                    best = (err, s, oy, ox)
            if s == 8 and best and best[0] < 2:
                break
    _, s, oy, ox = best
    out = np.zeros((ch, cw, 4), np.uint8)
    for r in range(min(ch, int((H - oy) / s))):
        for c in range(min(cw, int((W - ox) / s))):
            blk = a[int(oy + r * s):int(oy + (r + 1) * s), int(ox + c * s):int(ox + (c + 1) * s)]
            op = blk[..., 3] >= 128
            if op.mean() < 0.5:
                continue
            px = blk[op][:, :3]
            vals, cnt = np.unique(px, axis=0, return_counts=True)
            out[r, c, :3] = vals[cnt.argmax()]
            out[r, c, 3] = 255
    return out, s


def snap(f):
    out = f.copy()
    op = f[..., 3] > 0
    rgb = f[..., :3][op].astype(float)
    d = ((lab(rgb)[:, None, :] - PAL_LAB[None]) ** 2).sum(-1)
    lum = rgb @ [0.299, 0.587, 0.114]
    k = list(D.PAL).index("k")
    d[lum < 38, :] = np.inf
    d[lum < 38, k] = 0
    out[..., :3][op] = PAL_RGB[d.argmin(1)].astype(np.uint8)
    return out


def drop_specks(f, keep_min=3):
    op = f[..., 3] > 0
    H, W = op.shape
    seen = np.zeros_like(op)
    comps = []
    for y in range(H):
        for x in range(W):
            if op[y, x] and not seen[y, x]:
                st, cells = [(y, x)], []
                seen[y, x] = True
                while st:
                    a, b = st.pop()
                    cells.append((a, b))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = a + dy, b + dx
                            if 0 <= yy < H and 0 <= xx < W and op[yy, xx] and not seen[yy, xx]:
                                seen[yy, xx] = True
                                st.append((yy, xx))
                comps.append(cells)
    comps.sort(key=len, reverse=True)
    out = f.copy()
    for cells in comps[1:]:
        if len(cells) < keep_min:
            for a, b in cells:
                out[a, b] = 0
    return out


def design_at(fr, ch, cw, dy=0, rows=None):
    """The design (128 canvas) placed with its soles on this frame's soles row, its feet middle on the pivot."""
    des = D.canvas(D.grid())
    out = np.zeros((ch, cw, 4), np.uint8)
    oy, ox = fr["pivot"][1] + FEET - D.SOLE_ROW + dy, fr["pivot"][0] - D.MID_COL
    for y in range(128):
        if rows is not None and y not in rows:
            continue
        for x in range(128):
            if des[y, x, 3] and 0 <= y + oy < ch and 0 <= x + ox < cw:
                out[y + oy, x + ox] = des[y, x]
    return out


def run_frame(f, fr, ch, cw):
    """The design's upper body over Codex's legs; the bob from Codex's head top (clipped to 1 row)."""
    up_ = design_at(fr, ch, cw, rows=range(0, HIP + 1))
    top_design = np.nonzero(up_[..., 3].any(1))[0][0]
    ys = np.nonzero(f[..., 3].any(1))[0]
    bob = int(np.clip(ys[0] - top_design, -1, 1)) if len(ys) else 0
    up_ = design_at(fr, ch, cw, dy=bob, rows=range(0, HIP + 1))
    hip_row = fr["pivot"][1] + FEET - D.SOLE_ROW + HIP + bob
    out = f.copy()
    out[:hip_row + 1] = 0
    m = up_[..., 3] > 0
    out[m] = up_[m]
    return out


def finish(f, fr):
    f = drop_specks(f)
    f[fr["pivot"][1] + FEET + 1:] = 0
    f, _, _ = G.complete_outline(f, color=OUTLINE, feet=fr["pivot"][1] + FEET)
    return f


def strip(frames, cw, ch):
    cols, rows = layout(len(frames))
    a = np.zeros((rows * ch, cols * cw, 4), np.uint8)
    for k, f in enumerate(frames):
        a[k // cols * ch:(k // cols + 1) * ch, k % cols * cw:(k % cols + 1) * cw] = f
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review")
    a = ap.parse_args()
    cells = json.load(open(lp(CELLS), encoding="utf-8"))
    cw, ch = cells["cell"]
    built = {}
    for tag in TAGS:
        frs = cells["tags"][tag]
        out = []
        for k, fr in enumerate(frs, 1):
            path = os.path.join(a.src, f"{tag}_{k:02d}.png")
            if not os.path.exists(lp(path)):
                sys.exit(f"missing {path}")
            raw = np.asarray(Image.open(lp(path)).convert("RGBA"))
            f, s = read_grid(raw, cw, ch)
            f = snap(f)
            if tag == "run":
                f = run_frame(f, fr, ch, cw)
            f = finish(f, fr)
            out.append(f)
            print(f"{tag}_{k:02d}: grid {s} px, {int((f[..., 3] > 0).sum())} px")
        built[tag] = out
        strip(out, cw, ch).save(lp(os.path.join(OUT, f"talon_{tag}.png")))
    idle = [design_at(fr, ch, cw) for fr in cells["tags"]["idle"]]
    strip(idle, cw, ch).save(lp(os.path.join(OUT, "talon_idle.png")))
    with open(lp(os.path.join(OUT, "talon_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for tag, frames in built.items():
            W = len(frames) * (cw * 6 + 12)
            sheet = Image.new("RGBA", (W, ch * 6), (225, 225, 225, 255))
            for i, f in enumerate(frames):
                sheet.alpha_composite(Image.fromarray(np.repeat(np.repeat(f, 6, 0), 6, 1)), (i * (cw * 6 + 12), 0))
            sheet.save(os.path.join(a.review, f"talon_{tag}_review.png"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
