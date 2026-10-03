#!/usr/bin/env python3
"""Zilean's action strips: Codex's step-2 delivery (assets/source/zilean/codex_strips/, 2026-10-03) with the few frames
that broke fixed from the design's own pixels, written to assets/source/native/ for import_native.py.

    python tools/art/fix_zilean_strips.py

Codex drew the seven strips with its image model, pasted the design's head into every frame and swapped its own clock
for the design's (codex_strips/HANDOFF.md). Reviewed frame by frame at 8x:
- the bow of the four spells (attack, Q, W and E, frame 3 each: League bows deep and tips the clock over his head)
  came back as a lower body broken into dark scraps under the pasted head and clock: frame 3 is frame 2 again (the
  same fix Kennen's attack frame 2 took), the bow kept only as League's short 70 ms;
- the death's frames 1 and 2 left a hand and a whole sleeve floating off the body: only the body (the largest
  8-connected piece) is kept;
- ground showed through the chest under the beard (the pasted head and Codex's robe did not meet: attack 4 had 72
  enclosed clear squares, the design 25 - the gaps beside the beard and inside the gears): clear squares the figure
  closes in take the design's pixel at the same place relative to the pasted head, only where the design has body;
- the death's frames 4-8 were the whole design turned 55, 75 and 85 degrees by nearest neighbour, which broke the face
  and the outline into specks: frame 4 is the design turned 45 degrees with RotSprite (tools/art/rig_nocturne.py) and
  frames 5-8 the design turned a quarter (np.rot90) - fallen backwards onto the clock, the face up, as League's death
  and Kennen's (rig_kennen.dead_frames) - centred where Codex laid him, the lowest row on the feet line.
Everything else is Codex's frame as delivered; idle is the pack's (the design in all six).
"""
import json
import os
import shutil
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rig_nocturne import rotsprite  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zilean", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(OUT, "zilean_native.png")
CELLS = os.path.join(OUT, "zilean_cells.json")
TAGS = ["run", "attack", "skill", "w", "skill2", "hit", "dead"]
Z = 8
FEET = 11
BOW = {"attack": 2, "skill": 2, "w": 2, "skill2": 2}          # tag: 0-based frame that repeats the one before it
LOOSE = {("dead", 0), ("dead", 1)}                            # frames that keep only their largest piece
TURN = {3: 45, 4: 90, 5: 90, 6: 90, 7: 90}                    # death frame (0-based): degrees, counter-clockwise
CHEST = set(TAGS)                                             # tags whose chest holes take the design's pixels
HEAD = os.path.join(ROOT, "assets", "source", "zilean", "zilean_head_1x.png")   # the head pasted into every frame


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) or os.name != "nt" else pre + p


def read1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def write8x(a, path):
    Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1)).save(lp(path))


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def crop(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def largest_piece(f):
    """The frame with only its largest 8-connected piece."""
    op = f[..., 3] > 0
    seen = np.zeros_like(op)
    best = None
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        q, comp = deque([(y, x)]), []
        seen[y, x] = True
        while q:
            cy, cx = q.popleft()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
        if best is None or len(comp) > len(best):
            best = comp
    out = np.zeros_like(f)
    for y, x in best:
        out[y, x] = f[y, x]
    return out


def enclosed(op):
    """Clear squares the figure closes in (4-connected, not reachable from the frame's edge)."""
    H, W = op.shape
    out = np.zeros_like(op)
    q = deque((y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and not op[y, x])
    for s in q:
        out[s] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v, u = y + dy, x + dx
            if 0 <= v < H and 0 <= u < W and not op[v, u] and not out[v, u]:
                out[v, u] = True
                q.append((v, u))
    return ~op & ~out


def closed(op):
    """The silhouette with its 1-square gaps shut (a 3x3 dilation, then erosion)."""
    p = np.pad(op, 1)
    dil = np.zeros_like(p)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            dil |= np.roll(np.roll(p, dy, 0), dx, 1)
    ero = np.ones_like(dil)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ero &= np.roll(np.roll(dil, dy, 0), dx, 1)
    return ero[1:-1, 1:-1] | op


def find_head(f, head):
    """Where the design's pasted head sits in the frame: (dy, dx) from the design canvas, or None."""
    hy, hx = np.nonzero(head[..., 3] > 0)
    hc = head[hy, hx, :3].astype(int)
    H, W = f.shape[:2]
    for oy in range(-hy.min(), H - hy.max()):
        for ox in range(-hx.min(), W - hx.max()):
            g = f[hy + oy, hx + ox]
            if (g[:, 3] > 0).all() and (g[:, :3].astype(int) == hc).all():
                return oy, ox
    return None


def fill_chest(f, design, head, pivot):
    """Ground showing through the body where the pasted head and Codex's robe did not meet: the clear squares the
    (gap-shut) figure closes in take the design's pixel at the same place relative to the head - only where the design
    has body there (its own gaps, beside the beard and inside the gears, stay clear)."""
    at = find_head(f, head)
    if at is None:
        return f, 0
    oy, ox = at
    op = f[..., 3] > 0
    holes = enclosed(closed(op)) | enclosed(op)
    holes &= ~op
    out = f.copy()
    n = 0
    for y, x in zip(*np.nonzero(holes)):
        dy, dx = y - oy, x - ox
        if 0 <= dy < design.shape[0] and 0 <= dx < design.shape[1] and design[dy, dx, 3] > 0:
            out[y, x] = design[dy, dx]
            n += 1
    return out, n


def turned(fig, deg):
    """The figure turned counter-clockwise: a quarter exactly, other angles by RotSprite about its lowest middle."""
    if deg == 90:
        return np.rot90(fig, 1).copy()
    return crop(rotsprite(fig, (fig.shape[1] // 2, fig.shape[0] - 1), deg)[0])


def main():
    cells = json.load(open(lp(CELLS), encoding="utf-8"))
    cw, ch = cells["cell"]
    design_canvas = read1x(DESIGN)
    design = crop(design_canvas)
    head = np.asarray(Image.open(lp(HEAD)).convert("RGBA"))
    for tag in TAGS:
        sheet = read1x(os.path.join(SRC, f"zilean_{tag}.png"))
        frs = cells["tags"][tag]
        cols, _ = layout(len(frs))
        box = lambda k: ((k // cols) * ch, (k // cols + 1) * ch, (k % cols) * cw, (k % cols + 1) * cw)
        fixed = []
        if tag in BOW:
            k = BOW[tag]
            y0, y1, x0, x1 = box(k)
            p0, p1, q0, q1 = box(k - 1)
            # the frame before, where it stood about its own standing point (the cells' pivots differ by the lunge)
            dx = frs[k]["pivot"][0] - frs[k - 1]["pivot"][0]
            dy = frs[k]["pivot"][1] - frs[k - 1]["pivot"][1]
            prev = np.roll(np.roll(sheet[p0:p1, q0:q1], dy, 0), dx, 1)
            sheet[y0:y1, x0:x1] = prev
            fixed.append(f"frame {k + 1} = frame {k} (moved {dx:+d},{dy:+d} with the pivot)")
        for k in range(len(frs)):
            y0, y1, x0, x1 = box(k)
            if (tag, k) in LOOSE:
                before = int((sheet[y0:y1, x0:x1, 3] > 0).sum())
                sheet[y0:y1, x0:x1] = largest_piece(sheet[y0:y1, x0:x1])
                fixed.append(f"frame {k + 1} loose pieces {before - int((sheet[y0:y1, x0:x1, 3] > 0).sum())} px")
            if tag == "dead" and k in TURN:
                old = sheet[y0:y1, x0:x1]
                oys, oxs = np.nonzero(old[..., 3] > 0)
                mid = (oxs.min() + oxs.max() + 1) // 2           # where Codex laid him
                t = turned(design, TURN[k])
                f = np.zeros((ch, cw, 4), np.uint8)
                px, py = frs[k]["pivot"]
                top = py + FEET + 1 - t.shape[0]
                left = mid - t.shape[1] // 2
                left = max(1, min(cw - 1 - t.shape[1], left))
                m = t[..., 3] > 0
                f[top:top + t.shape[0], left:left + t.shape[1]][m] = t[m]
                sheet[y0:y1, x0:x1] = f
                fixed.append(f"frame {k + 1} the design turned {TURN[k]}")
        if tag in CHEST:
            n = 0
            for k in range(len(frs)):
                if tag == "dead" and k in TURN:
                    continue
                y0, y1, x0, x1 = box(k)
                f, added = fill_chest(sheet[y0:y1, x0:x1], design_canvas, head, frs[k]["pivot"])
                sheet[y0:y1, x0:x1] = f
                n += added
            fixed.append(f"chest holes filled from the design: {n} px")
        write8x(sheet, os.path.join(OUT, f"zilean_{tag}.png"))
        print(f"{tag:7s} " + ("; ".join(fixed) if fixed else "as delivered"))


if __name__ == "__main__":
    main()
