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
  5b. the death's last frame repeats the one before (Codex's own import copied it; its raw read back only one eye
     there and the head slid under the feet line, 「死亡的时候头部少了像素？」); a lying head is placed by both eyes or
     where it lay the frame before, and a pasted head never reaches under the soles' row;
  5c. despeckle: lone squares unlike all their neighbours and stray black specks inside the figure take the colour
     round them (「还有清理没用的色素 杂点太多 不干净」);
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
# (tag, 0-based frame): boxes where Codex's own horns stick out past the body (its head thrown back in the death):
# every square there that is not the pasted head goes; the loose bits left are dropped and the outline closed again
REMOVE = {("dead", 0): [(36, 56, 80, 96)],
          ("dead", 1): [(32, 44, 26, 41)],
          ("dead", 2): [(30, 44, 26, 42)],
          ("dead", 3): [(37, 46, 21, 34), (49, 58, 21, 38)],
          ("dead", 4): [(63, 77, 30, 46)],
          ("skill2", 2): [(58, 66, 92, 97)],
          ("skill2", 3): [(56, 66, 85, 92)]}
# (tag, 0-based frame): boxes where Codex's old horns in iron grey stand in front of the face (W's charge holds both
# arms back, so nothing iron belongs there): the iron, rim, brown, gold and outline squares there (not the pasted
# head) go
REMOVE_JUNK = {("skill2", 0): [(55, 72, 84, 97)],
               ("skill2", 1): [(50, 71, 79, 91)],
               ("skill2", 2): [(56, 69, 88, 98)],
               ("skill2", 5): [(51, 61, 82, 90)]}
VIOLET = {(0x3B, 0x18, 0x88), (0x55, 0x26, 0xC3), (0x73, 0x3D, 0xF5), (0x9A, 0x63, 0xF3), (0xBB, 0x88, 0xFB),
          (0x15, 0x0B, 0x4B)}
CUTS = {"butt": ("skill2", [4, 5]), "slam": ("skill", [2, 3, 4, 5])}     # 0-based frames
CW, CH, Z = 128, 96, 8
SOLE = 81
EYE_RED = (0xFB, 0x12, 0x0D)
OUTLINE = (0x12, 0x03, 0x19)
DESIGN_EYE = (78.0, 73.0)          # the design's eye centre (row, column) on its 128 x 128 canvas
LYING = {("dead", 5), ("dead", 6), ("dead", 7)}   # 0-based frames lying on his back
SAME_AS = {("dead", 7): 6}        # Codex's last death frame repeats the one before (its own import copied it too)
NOT_HEAD = {(0x42, 0x17, 0x14), (0x87, 0x3E, 0x28), (0xC8, 0x67, 0x2F), (0xF5, 0xB7, 0x43), (0xFB, 0xD5, 0x9B)}  # loincloth
IRON = (0x44, 0x3A, 0x3F)
HORN = {(0xE1, 0xB5, 0x90), (0xFA, 0xF1, 0xD6)}   # light horn ivory, used nowhere else
SILVER = {(0x8E, 0x96, 0xA2), (0xD8, 0xDC, 0xE4)}   # the nose ring's two greys: anywhere else they are read-back noise
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


def clean_fragments(a, small=12):
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
        if len(comp) < small or (min(p[0] for p in comp) <= 2 and len(comp) < 150):
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
    ty = min(ty, SOLE + 1 - hm.shape[0])            # never under the soles' row (the feet line cuts it off)
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

    ys = np.nonzero(placed.any(1))[0]
    top_half = (ys.min() + ys.max()) / 2 + 3      # the horns' height: the loincloth's browns are far below it

    def brown_horn(y, x):
        return y <= top_half and tuple(int(v) for v in f[y, x, :3]) in NOT_HEAD and not rim(y, x)

    todo = [(y, x) for y, x in zip(*np.nonzero(near & ~placed & (f[..., 3] > 0)))
            if tuple(int(v) for v in f[y, x, :3]) in HORN | {EYE_RED}
            or (tuple(int(v) for v in f[y, x, :3]) == HORN_DARK and not rim(y, x)) or brown_horn(y, x)]
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


def small_junk(f, placed, reach=6, size=12):
    """Codex's old horn shading in the shackles' iron and rim, the loincloth's browns or gold: such squares near the
    pasted head (not part of it) that make a piece of fewer than `size` squares go - a real shackle is one big iron
    piece. Inside the figure they take the neighbouring violet, on its edge they go clear."""
    H, W = f.shape[:2]
    junk_cols = {IRON, HORN_DARK} | NOT_HEAD
    near = placed.copy()
    for _ in range(reach):
        g = near.copy()
        g[1:] |= near[:-1]
        g[:-1] |= near[1:]
        g[:, 1:] |= near[:, :-1]
        g[:, :-1] |= near[:, 1:]
        near = g
    junk = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero((f[..., 3] > 0) & ~placed)):
        junk[y, x] = tuple(int(v) for v in f[y, x, :3]) in junk_cols
    seen = np.zeros_like(junk)
    todo = []
    for y, x in zip(*np.nonzero(junk & near)):
        if seen[y, x]:
            continue
        comp, st = [], [(y, x)]
        seen[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and junk[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        st.append((ny, nx))
        if len(comp) < size:
            todo += comp
    for y, x in todo:
        nb = [f[y + dy, x + dx] for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))
              if 0 <= y + dy < H and 0 <= x + dx < W]
        vio = [p_ for p_ in nb if p_[3] and tuple(int(v) for v in p_[:3]) in VIOLET]
        if any(p_[3] == 0 for p_ in nb) or not vio:
            f[y, x] = 0
        else:
            f[y, x] = vio[0]
    return len(todo)


def despeckle(f, placed, rounds=3):
    """「还有清理没用的色素 杂点太多 不干净」: inside the figure (all 4 neighbours opaque), not on the pasted head, a square
    unlike all 8 neighbours where 5 or more of them share one colour takes that colour (or unlike its 4 neighbours when
    3 of them share one: a speck touching its own colour only at a corner); an outline square there with at
    most one outline 4-neighbour (a stray black speck, not a line) takes its neighbours' most common other colour. The
    eyes' red and the ring's greys are never touched."""
    from collections import Counter
    H, W = f.shape[:2]
    keep = {EYE_RED} | SILVER
    n = 0
    for _ in range(rounds):
        changes = []
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if not f[y, x, 3] or placed[y, x]:
                    continue
                c = tuple(int(v) for v in f[y, x, :3])
                if c in keep:
                    continue
                n4 = [f[y + dy, x + dx] for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))]
                if any(p_[3] == 0 for p_ in n4):
                    continue
                n8 = [tuple(int(v) for v in f[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                      if (dy or dx) and f[y + dy, x + dx, 3]]
                if c == OUTLINE:
                    ol4 = sum(1 for p_ in n4 if tuple(int(v) for v in p_[:3]) == OUTLINE)
                    if ol4 <= 1:
                        others = [q for q in n8 if q != OUTLINE]
                        if others:
                            changes.append((y, x, Counter(others).most_common(1)[0][0]))
                    continue
                c4 = [tuple(int(v) for v in p_[:3]) for p_ in n4]
                if c not in n8:
                    top, k = Counter(n8).most_common(1)[0]
                    if k >= 5 and top != OUTLINE:
                        changes.append((y, x, top))
                        continue
                if c not in c4:                      # touching its own colour only at a corner
                    top, k = Counter(c4).most_common(1)[0]
                    if k >= 3 and top != OUTLINE:
                        changes.append((y, x, top))
        for y, x, c in changes:
            f[y, x, :3] = c
        n += len(changes)
        if not changes:
            break
    return n


def strays(f, placed, reach=12):
    """Codex's old horn outlines left round the pasted head once their fill was cleared: dangling outline strokes near
    the head (an outline or dark-brown square, not part of the head, with at most one opaque 4-neighbour) are pruned,
    end by end, until none is left."""
    H, W = f.shape[:2]
    near = placed.copy()
    for _ in range(reach):
        g = near.copy()
        g[1:] |= near[:-1]
        g[:-1] |= near[1:]
        g[:, 1:] |= near[:, :-1]
        g[:, :-1] |= near[:, 1:]
        near = g
    dark = {OUTLINE, (0x42, 0x17, 0x14)}
    gone = 0
    while True:
        drop = []
        for y, x in zip(*np.nonzero(near & ~placed & (f[..., 3] > 0))):
            if tuple(int(v) for v in f[y, x, :3]) not in dark:
                continue
            nb = sum(1 for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))
                     if 0 <= y + dy < H and 0 <= x + dx < W and f[y + dy, x + dx, 3])
            if nb <= 1:
                drop.append((y, x))
        if not drop:
            return gone
        for y, x in drop:
            f[y, x] = 0
        gone += len(drop)


def desilver(f, placed):
    """The nose ring's greys outside the pasted head (Codex's shading read back as ring silver, grey like the arena:
    「好几个地方都少了像素」) take their neighbours' most common other colour."""
    from collections import Counter
    H, W = f.shape[:2]
    todo = [(y, x) for y, x in zip(*np.nonzero(f[..., 3] > 0))
            if not placed[y, x] and tuple(int(v) for v in f[y, x, :3]) in SILVER]
    for _ in range(3):
        left = []
        for y, x in todo:
            cols = [tuple(int(v) for v in f[y + dy, x + dx, :3]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if (dy or dx) and 0 <= y + dy < H and 0 <= x + dx < W and f[y + dy, x + dx, 3]]
            cols = [c for c in cols if c not in SILVER and c != OUTLINE]
            if not cols:
                left.append((y, x))
                continue
            f[y, x, :3] = Counter(cols).most_common(1)[0][0]
        todo = left
    return 0


def seal(f, placed, rounds=3):
    """Close the gaps the head swap leaves: a clear square touching the pasted head and the body (4-neighbours) takes
    the body colour next to it; then every clear square the outside cannot reach in a hole of at most 12 squares, and
    every pinhole (4 opaque neighbours), takes its neighbours' most common colour. Returns the squares filled."""
    from collections import Counter, deque
    H, W = f.shape[:2]
    filled = 0
    N4 = ((0, -1), (0, 1), (-1, 0), (1, 0))
    for _ in range(rounds):
        add = {}
        for y, x in zip(*np.nonzero(f[..., 3] == 0)):
            nb = [(y + dy, x + dx) for dy, dx in N4 if 0 <= y + dy < H and 0 <= x + dx < W and f[y + dy, x + dx, 3]]
            if len(nb) < 2:
                continue
            head = [q for q in nb if placed[q]]
            body = [q for q in nb if not placed[q]]
            if head and body:
                cols = [tuple(int(v) for v in f[q][:3]) for q in body]
                inner = [c for c in cols if c != OUTLINE]
                add[(y, x)] = Counter(inner or cols).most_common(1)[0][0]
        for (y, x), c in add.items():
            f[y, x, :3] = c
            f[y, x, 3] = 255
        filled += len(add)
        if not add:
            break
    # holes and pinholes
    op = f[..., 3] > 0
    outside = np.zeros_like(op)
    q = deque([(y, x) for y in range(H) for x in (0, W - 1) if not op[y, x]] +
              [(y, x) for x in range(W) for y in (0, H - 1) if not op[y, x]])
    for p_ in q:
        outside[p_] = True
    while q:
        y, x = q.popleft()
        for dy, dx in N4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                q.append((ny, nx))
    seen = np.zeros_like(op)
    todo = []
    for y, x in zip(*np.nonzero(~op & ~outside)):
        if seen[y, x]:
            continue
        comp, st = [], [(y, x)]
        seen[y, x] = True
        while st:
            cy, cx = st.pop()
            comp.append((cy, cx))
            for dy, dx in N4:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not outside[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    st.append((ny, nx))
        if len(comp) <= 12:
            todo += comp
    for y, x in zip(*np.nonzero(~op & outside)):
        if all(0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] for dy, dx in N4):
            todo.append((y, x))
    for _ in range(4):
        left = []
        for y, x in todo:
            cols = [tuple(int(v) for v in f[y + dy, x + dx, :3]) for dy, dx in N4
                    if 0 <= y + dy < H and 0 <= x + dx < W and f[y + dy, x + dx, 3]]
            if not cols:
                left.append((y, x))
                continue
            inner = [c for c in cols if c != OUTLINE]
            f[y, x, :3] = Counter(inner or cols).most_common(1)[0][0]
            f[y, x, 3] = 255
            filled += 1
        todo = left
    return filled


def build(tag, des, mask, palette, cells):
    frs = cells["tags"][tag]
    cols, rows = layout(len(frs))
    a = majority_read(os.path.join(SRC, f"{tag}.png"), cols, rows, palette)
    out = np.zeros_like(a)
    log = []
    last_eyes = None
    log_clean = []
    for i, meta in enumerate(frs):
        if (tag, i) in SAME_AS:          # a held last frame: the frame before it again
            k = SAME_AS[(tag, i)]
            X, Y = (i % cols) * CW, (i // cols) * CH
            out[Y:Y + CH, X:X + CW] = out[(k // cols) * CH:(k // cols + 1) * CH, (k % cols) * CW:(k % cols + 1) * CW]
            log.append(f"{i + 1}:=frame{k + 1}")
            continue
        X, Y = (i % cols) * CW, (i // cols) * CH
        f = clean_fragments(a[Y:Y + CH, X:X + CW].copy())
        yy, xx = np.nonzero(f[..., 3] > 0)
        sole = int(yy.max())
        anchor = float(np.median(xx[yy >= sole - 3]))
        f = shift(f, int(round(meta["pivot"][0] - anchor)), SOLE - sole)
        red = np.argwhere((f[..., :3] == EYE_RED).all(-1) & (f[..., 3] > 0))
        lying = (tag, i) in LYING
        two_eyes = len(red) and np.ptp(red[:, 0 if lying else 1]) >= 3
        if len(red) and (two_eyes or not lying):
            ey, ex = red.mean(0)
        elif lying and last_eyes is not None:     # one eye read back: the lying head stays where it lay
            ey, ex = last_eyes
        else:
            ex, ey = meta["head"]
        if lying:
            last_eyes = (ey, ex)
        placed = paste_head(f, des, mask, ey, ex, lying)
        n = clear_old_head(f, placed)
        n += clear_boxes(f, placed, CLEAR.get((tag, i), []))
        for r0, r1, c0, c1 in REMOVE.get((tag, i), []):
            box = np.zeros(f.shape[:2], bool)
            box[r0:r1, c0:c1] = True
            gone = box & ~placed & (f[..., 3] > 0)
            f[gone] = 0
            n += int(gone.sum())
        junk_cols = {IRON, HORN_DARK, OUTLINE} | NOT_HEAD
        for r0, r1, c0, c1 in REMOVE_JUNK.get((tag, i), []):
            for y in range(r0, r1):
                for x in range(c0, c1):
                    if f[y, x, 3] and not placed[y, x] and tuple(int(v) for v in f[y, x, :3]) in junk_cols:
                        f[y, x] = 0
                        n += 1
        if (tag, i) in REMOVE or (tag, i) in REMOVE_JUNK:
            f = clean_fragments(f, small=30)
        n += seal(f, placed)
        n += desilver(f, placed)
        n += small_junk(f, placed)
        n += strays(f, placed)
        cleaned = despeckle(f, placed)
        log_clean.append(cleaned)
        can = np.pad(f, ((2, 2), (2, 2), (0, 0)))
        can, _, _ = strips.complete_outline(can, color=OUTLINE, feet=SOLE + 2)
        f = can[2:-2, 2:-2]
        f[SOLE + 1:] = 0
        seal(f, np.zeros(f.shape[:2], bool), rounds=0)     # the closing outline can shut a notch into a pinhole
        f = clean_fragments(f, small=10)                   # specks the clearing cut off
        out[Y:Y + CH, X:X + CW] = f
        log.append(f"{i + 1}:eyes{len(red)} cleared{n}")
    print(tag, " ".join(log), "| specks cleaned", log_clean)
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
