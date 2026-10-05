#!/usr/bin/env python3
"""Alistar's action strips from Codex's generated drafts (assets/source/alistar/codex_strips/raw/<tag>.png) with the
design's head pasted by its own shape -> assets/source/native/alistar_<tag>.png (8x, the cells of alistar_cells.json).

    python tools/art/fix_alistar_strips.py [--tag skill ...] [--review DIR]

Codex's own import (codex_strips/prepare_strips.py, delivered as a review draft) read the drafts well but, before
pasting the head, cleared a 27 x 22 rectangle round the eyes: every frame showed the head in a box of background
(the grey frame round the head in its contact sheet). Here:
  1. each draft is read on the logical canvas (its cells x 128 x 96 squares) by majority (Codex's majority_read: every
     square the design colour most of its pixels are nearest to, green background and thin coverage left out);
  2. loose bits (< 12 squares, or small pieces touching the cell top) go; the whole figure moves so its soles sit on
     row 81 and the middle of its lowest 4 rows on the pivot's column (Codex's alignment);
  3. HEAD: the design's head by shape - both horns with their outlines, the mane between them, the face, the snout,
     the nose ring and the beard (head_mask) - pasted where Codex drew the eyes: the design's eye centre (row 78,
     column 73.0 on its canvas) on the mean of the frame's eye-red squares (cells' League head joint when there are
     none); the death's lying frames (6-8) take it turned a quarter counter-clockwise;
  4. Codex's own head left round the paste - horn ivory (the dark shade only where it does not touch iron: the
     shackles' rim shares it) and eye red outside the pasted shape, within 12 squares of it - goes: to the
     neighbouring body colour inside the figure, to nothing on its edge;
  5. strips.complete_outline closes the edge;
  6. CUTS: butt = skill2 frames 5-6 (the headbutt played on landing) and slam = skill frames 3-6 (Pulverize after the
     headbutt) become strips of their own, their cells added to alistar_cells.json.
The idle is the pack's own (the design in all six cells).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "alistar", "codex_strips", "raw")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "alistar_native.png")
CELLS = os.path.join(NATIVE, "alistar_cells.json")
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
# (tag, 0-based frame): boxes (row0, row1, col0, col1) in the cell where Codex's own frontal head - its big horns
# sweeping down to the shoulders in pale gold, brown and iron, the mane's tuft - is left beside the pasted head:
# every square there of those colours (and their inner outline) becomes the nearest violet of the body
CLEAR = {("ult", 3): [(20, 39, 48, 70), (26, 39, 76, 90)],
         ("ult", 4): [(19, 40, 34, 57), (28, 39, 60, 74)]}
VIOLET = {(0x3B, 0x18, 0x88), (0x55, 0x26, 0xC3), (0x73, 0x3D, 0xF5), (0x9A, 0x63, 0xF3), (0xBB, 0x88, 0xFB),
          (0x15, 0x0B, 0x4B)}
CUTS = {"butt": ("skill2", [4, 5]), "slam": ("skill", [2, 3, 4, 5])}     # 0-based frames
CW, CH, Z = 128, 96, 8
SOLE = 81
EYE_RED = (0xFB, 0x12, 0x0D)
OUTLINE = (0x12, 0x03, 0x19)
DESIGN_EYE = (78.0, 73.0)          # the design's eye centre (row, column) on its 128 x 128 canvas
LYING = {("dead", 5), ("dead", 6), ("dead", 7)}   # 0-based frames lying on his back
NOT_HEAD = {(0x42, 0x17, 0x14), (0x87, 0x3E, 0x28), (0xC8, 0x67, 0x2F), (0xF5, 0xB7, 0x43), (0xFB, 0xD5, 0x9B)}  # loincloth
IRON = (0x44, 0x3A, 0x3F)
HORN = {(0xE1, 0xB5, 0x90), (0xFA, 0xF1, 0xD6)}   # light horn ivory, used nowhere else
HORN_DARK = (0xA8, 0x82, 0x6E)     # the horns' shade, also the shackles' bronze rim (kept when it touches iron)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def design1x():
    return np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()


def head_mask(des):
    """The design's head: rows 62-84, columns 63-85, minus the loincloth, the shackle under the chin (iron from row 84)
    and the chest / loincloth corner left of column 68 below row 79."""
    m = np.zeros(des.shape[:2], bool)
    for y in range(62, 85):
        for x in range(63, 86):
            p = des[y, x]
            if not p[3]:
                continue
            c = tuple(int(v) for v in p[:3])
            if c in NOT_HEAD or (c == IRON and y >= 84) or (y > 79 and x < 68) or (y < 67 and x < 68):
                continue
            m[y, x] = True
    return m


def majority_read(path, cols, rows, palette):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    h, w = a.shape[:2]
    H, W = rows * CH, cols * CW
    small = np.zeros((H, W, 4), np.uint8)
    pal = palette.astype(np.int32)
    ys = [round(y * h / H) for y in range(H + 1)]
    xs = [round(x * w / W) for x in range(W + 1)]
    for y in range(H):
        y0, y1 = ys[y], max(ys[y] + 1, ys[y + 1])
        for x in range(W):
            x0, x1 = xs[x], max(xs[x] + 1, xs[x + 1])
            block = a[y0:y1, x0:x1].reshape(-1, 4)
            green = (block[:, 1] > 190) & (block[:, 0] < 90) & (block[:, 2] < 100)
            solid = (block[:, 3] >= 128) & ~green
            if solid.sum() <= len(block) / 2:
                continue
            rgb = block[solid, :3].astype(np.int32)
            k = np.bincount(((rgb[:, None, :] - pal[None]) ** 2).sum(2).argmin(1), minlength=len(pal)).argmax()
            small[y, x, :3] = palette[k]
            small[y, x, 3] = 255
    return small


def clean_fragments(a):
    mask = a[..., 3] > 0
    seen = np.zeros(mask.shape, bool)
    h, w = mask.shape
    for y, x in np.argwhere(mask):
        if seen[y, x]:
            continue
        stack, comp = [(y, x)], []
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if len(comp) < 12 or (min(p[0] for p in comp) <= 2 and len(comp) < 150):
            for cy, cx in comp:
                a[cy, cx] = 0
    return a


def shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    sx, sy, ex, ey = max(0, -dx), max(0, -dy), min(w, w - dx), min(h, h - dy)
    if ex > sx and ey > sy:
        out[sy + dy:ey + dy, sx + dx:ex + dx] = a[sy:ey, sx:ex]
    return out


def paste_head(f, des, mask, ey, ex, lying):
    """Paste the masked head with the design's eye centre on (ey, ex) (lying: turned a quarter counter-clockwise)."""
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    hd = des[y0:y1, x0:x1].copy()
    hm = mask[y0:y1, x0:x1]
    hd[~hm] = 0
    ry, rx = DESIGN_EYE[0] - y0, DESIGN_EYE[1] - x0
    if lying:
        hd = np.rot90(hd)                     # counter-clockwise: the crown points left
        hm = np.rot90(hm)
        ry, rx = (x1 - x0 - 1) - rx, ry
    ty, tx = int(round(ey - ry)), int(round(ex - rx))
    placed = np.zeros(f.shape[:2], bool)
    for y, x in zip(*np.nonzero(hm)):
        Y, X = ty + y, tx + x
        if 0 <= Y < f.shape[0] and 0 <= X < f.shape[1]:
            f[Y, X] = hd[y, x]
            placed[Y, X] = True
    return placed


def clear_old_head(f, placed, reach=12):
    """Codex's own horn ivory and eye red outside the pasted head, within `reach` squares of it."""
    near = placed.copy()
    for _ in range(reach):
        g = near.copy()
        g[1:] |= near[:-1]
        g[:-1] |= near[1:]
        g[:, 1:] |= near[:, :-1]
        g[:, :-1] |= near[:, 1:]
        near = g
    def rim(y, x):
        return any(tuple(int(v) for v in f[y + dy, x + dx, :3]) == IRON for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if 0 <= y + dy < f.shape[0] and 0 <= x + dx < f.shape[1])

    todo = [(y, x) for y, x in zip(*np.nonzero(near & ~placed & (f[..., 3] > 0)))
            if tuple(int(v) for v in f[y, x, :3]) in HORN | {EYE_RED}
            or (tuple(int(v) for v in f[y, x, :3]) == HORN_DARK and not rim(y, x))]
    gone = set(todo)
    for y, x in todo:
        nb = [f[y + dy, x + dx] for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))
              if 0 <= y + dy < f.shape[0] and 0 <= x + dx < f.shape[1]]
        if any(p[3] == 0 for p in nb):
            f[y, x] = 0
            continue
        body = [p for p, (dy, dx) in zip(nb, ((0, -1), (0, 1), (-1, 0), (1, 0)))
                if (y + dy, x + dx) not in gone
                and tuple(int(v) for v in p[:3]) not in HORN | {EYE_RED, OUTLINE, HORN_DARK}]
        f[y, x] = body[0] if body else np.array(OUTLINE + (255,), np.uint8)
    return len(todo)


def clear_boxes(f, placed, boxes):
    """Every non-violet square in the boxes (not the pasted head, not the silhouette's edge) -> the nearest violet."""
    from collections import deque
    todo = set()
    for r0, r1, c0, c1 in boxes:
        for y in range(r0, r1):
            for x in range(c0, c1):
                if placed[y, x] or not f[y, x, 3] or tuple(int(v) for v in f[y, x, :3]) in VIOLET:
                    continue
                edge = any(not f[y + dy, x + dx, 3] for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)))
                if not edge:
                    todo.add((y, x))
    src = f.copy()
    for y, x in todo:
        q, seen = deque([(y, x)]), {(y, x)}
        while q:
            cy, cx = q.popleft()
            if (cy, cx) not in todo and tuple(int(v) for v in src[cy, cx, :3]) in VIOLET and src[cy, cx, 3]:
                f[y, x] = src[cy, cx]
                break
            for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                n = (cy + dy, cx + dx)
                if n not in seen and 0 <= n[0] < f.shape[0] and 0 <= n[1] < f.shape[1]:
                    seen.add(n)
                    q.append(n)
    return len(todo)


def build(tag, des, mask, palette, cells):
    frs = cells["tags"][tag]
    cols, rows = layout(len(frs))
    a = majority_read(os.path.join(SRC, f"{tag}.png"), cols, rows, palette)
    out = np.zeros_like(a)
    log = []
    for i, meta in enumerate(frs):
        X, Y = (i % cols) * CW, (i // cols) * CH
        f = clean_fragments(a[Y:Y + CH, X:X + CW].copy())
        yy, xx = np.nonzero(f[..., 3] > 0)
        sole = int(yy.max())
        anchor = float(np.median(xx[yy >= sole - 3]))
        f = shift(f, int(round(meta["pivot"][0] - anchor)), SOLE - sole)
        red = np.argwhere((f[..., :3] == EYE_RED).all(-1) & (f[..., 3] > 0))
        lying = (tag, i) in LYING
        if len(red):
            ey, ex = red.mean(0)
        else:
            ex, ey = meta["head"]
        placed = paste_head(f, des, mask, ey, ex, lying)
        n = clear_old_head(f, placed)
        n += clear_boxes(f, placed, CLEAR.get((tag, i), []))
        can = np.pad(f, ((2, 2), (2, 2), (0, 0)))
        can, _, _ = strips.complete_outline(can, color=OUTLINE, feet=SOLE + 2)
        f = can[2:-2, 2:-2]
        f[SOLE + 1:] = 0
        out[Y:Y + CH, X:X + CW] = f
        log.append(f"{i + 1}:eyes{len(red)} cleared{n}")
    print(tag, " ".join(log))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", nargs="*", default=TAGS)
    a = ap.parse_args()
    des = design1x()
    mask = head_mask(des)
    op = des[..., 3] > 0
    palette = np.unique(des[op][:, :3], axis=0)
    cells = json.load(open(lp(CELLS), encoding="utf-8"))
    built = {}
    for tag in a.tag:
        s = build(tag, des, mask, palette, cells)
        built[tag] = s
        Image.fromarray(s).resize((s.shape[1] * Z, s.shape[0] * Z), Image.NEAREST).save(
            lp(os.path.join(NATIVE, f"alistar_{tag}.png")))
    for cut, (src, ks) in CUTS.items():
        if src not in built:
            continue
        cols, _ = layout(len(cells["tags"][src]))
        c2, r2 = layout(len(ks))
        s = np.zeros((r2 * CH, c2 * CW, 4), np.uint8)
        for j, k in enumerate(ks):
            fr = built[src][(k // cols) * CH:(k // cols + 1) * CH, (k % cols) * CW:(k % cols + 1) * CW]
            s[(j // c2) * CH:(j // c2 + 1) * CH, (j % c2) * CW:(j % c2 + 1) * CW] = fr
        cells["tags"][cut] = [dict(cells["tags"][src][k]) for k in ks]
        Image.fromarray(s).resize((s.shape[1] * Z, s.shape[0] * Z), Image.NEAREST).save(
            lp(os.path.join(NATIVE, f"alistar_{cut}.png")))
    with open(lp(CELLS), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)


if __name__ == "__main__":
    main()
