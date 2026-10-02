#!/usr/bin/env python3
"""Ryze's action strips read again from Codex's own drawings (the user: "Codex生成的质量很差 你看看奇怪的地方能不能修复吧").

    python tools/art/fix_ryze_strips.py [--check] [--review OUT.png]

Codex drew the eight strips with its image tool from the approved 40-row design (assets/source/ryze/MODEL_STRIPS.md)
and turned them into game pixels itself (assets/source/ryze/codex_strips/, as delivered, with its HANDOFF: "review
draft"). Its drawings are clean pixel art (codex_strips/raw/ryze_<tag>_raw.png, one frame per cell of an even grid);
the conversion was not: it sampled every strip on one estimated pitch (the image tool drew each strip on its own
grid: 5-8 px squares), so a strip drawn finer came out a fifth too big and coarse ones lost rows (the run's frames 1,
2 and 6 cut in two at row 72); it then wiped a box round its drawn head before pasting the design's, which took the
arm raised beside the head with it (W's raised arm a thin stick, R's last frame two floating hands), and left the drawn
crown a row or two over the pasted one and pieces of the drawn scroll top beside the pasted scroll top; the death's
last frames got the pasted upright head on a body lying on the ground. So every frame is read again from the drawing:
1. the drawing read on its own grid (the skill's regrid.py at the strip's square size, TRUE: the period of its colour
   changes), alpha 0/255, every square snapped to the nearest of the design's colours in Lab (the two eye colours
   left out: they stay the pasted eyes' own);
2. cut to the idle's scale by whole-line deletion (design_akali.dp_keep, never two neighbouring lines, the eye rows
   and columns kept): the strip's reference frame (REF: back in the idle stance, or the run's median) has the idle's
   height from the crown to the soles;
3. the head: the drawn eyes found (bright squares ringed by skin, not the scroll's highlights), the design's head (the
   pack's mask: the bald head, the face, the beard's top) pasted where its eyes meet them; before that the drawn head
   goes - from its eyes through skin, rune lines and whites, no further than one square round the pasted head and
   the rows over its crown between the eyes, then the outline squares round that - so an arm raised beside the head
   stays; holes left inside the figure take a drawn neighbour's colour, thin remains of the drawn head round the
   pasted one (no 3x3 block of drawn squares: its crown arc, a side column; arms and the scroll are thicker) and
   crumbs of at most 3 squares go; where the drawn head was wider, what stood behind it (the scroll, mostly) closes
   up to the pasted head, its outline moved against it, as on the design. Not pasted (NO_PASTE): the death's frames
   6-8 (lying on the ground): the drawn head stays; frame 3 bows the head (EYES_AT: its eyes placed by hand);
4. pinholes (clear pieces of at most 2 squares shut in by the figure) take the commonest colour round them;
5. placed in the pack's cell: the soles on the feet line (11 rows under the standing point), the pasted near eye on
   the column where Codex's pasted one stood (the head's place over the standing point Codex kept in every frame);
   frames without a pasted head by the middle of Codex's figure.
CODEX: the last frame of the attack, Q, the combo and the landing stay Codex's (the idle itself at the standing
point: the action ends in the approved stance). FRAMES: R's last frame (both arms straight up) holds frame 7 (both
arms raised wide): its near arm rises right behind the head and is mostly covered by the pasted one.
Writes assets/source/native/ryze_<tag>.png (8x) for every tag, ryze_idle.png (the pack's, as delivered) and
ryze_cells.json (the pack's standing points); then run tools/art/import_native.py --hero ryze. --check compares with
the files instead of writing them; --review writes Codex's frame and the new one side by side.
"""
import argparse
import json
import os
import shutil
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
from design_kaisa import keep_lines, lab  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ryze", "codex_strips")
RAW = os.path.join(SRC, "raw")
OUT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(OUT, "ryze_native.png")
Z = 8
FEET = 11
TAGS = ["run", "attack", "skill", "skill2", "ult", "ult_land", "hit", "dead"]
# the raw sheets: columns x rows of even cells, read left to right, top to bottom
GRID = {"run": (4, 2), "attack": (3, 2), "skill": (3, 2), "skill2": (4, 3), "ult": (4, 2), "ult_land": (4, 1),
        "hit": (2, 1), "dead": (4, 2)}
TRUE = {"run": 8.0, "attack": 5.1, "skill": 7.0, "skill2": 5.0, "ult": 5.0, "ult_land": 8.0, "hit": 8.0, "dead": 5.0}
REF = {"run": None, "attack": 6, "skill": 6, "skill2": 12, "ult": 1, "ult_land": 4, "hit": 2, "dead": 2}
NO_PASTE = {("dead", 6), ("dead", 7), ("dead", 8)}
# eyes found by hand ((top, left, bottom, right) near, far, on the cut frame): the death's frame 3 bows the head,
# one eye a 3-square slant and the far one hidden; the design's head goes there like in frames 2 and 4
EYES_AT = {("dead", 3): ((11, 20, 13, 21), (12, 26, 12, 26))}
CODEX = {("attack", 6), ("skill", 6), ("skill2", 12), ("ult_land", 4)}
FRAMES = {("ult", 8): 7}
# the design's head (strips_pack_ry.head_rows) and its eyes' centres
HEAD = [(y, x) for y in range(61, 71) for x in range(56, 70)] + [(y, x) for y in range(71, 75) for x in range(57, 69)]
NEAR_EYE, FAR_EYE = (67.5, 61.5), (67.5, 67.0)
SIDE = 5                   # the drawn head reaches this many columns past the pasted one's sides (crown to beard)
GAP = 6                    # at most this wide a gap it leaves between the scroll and the pasted head is closed
EYE_ONLY = [(0xFB, 0xFB, 0xFD), (0xB3, 0x68, 0xFD)]
SKIN = {(0x6B, 0x44, 0xCC), (0xB5, 0x9C, 0xFC), (0x92, 0x70, 0xF2), (0xA8, 0x8C, 0xFB), (0xC8, 0xB5, 0xFD),
        (0x51, 0x1A, 0xC4), (0x23, 0x14, 0x8D)}
RUNES = {(0x14, 0x17, 0x43), (0x18, 0x23, 0x5D)}
OUTLINE = {(0x0F, 0x02, 0x13), (0x10, 0x04, 0x1C)}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def at1x(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def colour(a, y, x):
    return tuple(int(v) for v in a[y, x, :3])


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def grow(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def pieces(mask):
    """8-connected pieces of a mask: (label array, sizes)."""
    lab_ = np.zeros(mask.shape, int)
    sizes = [0]
    for y, x in zip(*np.nonzero(mask)):
        if lab_[y, x]:
            continue
        n = len(sizes)
        q = deque([(y, x)])
        lab_[y, x] = n
        size = 0
        while q:
            cy, cx = q.popleft()
            size += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab_[ny, nx]:
                        lab_[ny, nx] = n
                        q.append((ny, nx))
        sizes.append(size)
    return lab_, sizes


def background(empty):
    """Empty squares joined to the border (4-connected)."""
    H, W = empty.shape
    bg = np.zeros_like(empty)
    q = deque((y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and empty[y, x])
    for y, x in q:
        bg[y, x] = True
    while q:
        y, x = q.popleft()
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < H and 0 <= xx < W and empty[yy, xx] and not bg[yy, xx]:
                bg[yy, xx] = True
                q.append((yy, xx))
    return bg


def raw_frames(tag):
    a = np.asarray(Image.open(lp(os.path.join(RAW, f"ryze_{tag}_raw.png"))).convert("RGBA"))
    cols, rows = GRID[tag]
    H, W = a.shape[:2]
    return [a[r * H // rows:(r + 1) * H // rows, c * W // cols:(c + 1) * W // cols]
            for r in range(rows) for c in range(cols)]


def palette(design):
    cols = np.unique(design[design[..., 3] > 0][:, :3], axis=0)
    return np.array([c for c in cols if tuple(int(v) for v in c) not in EYE_ONLY])


def read(f, size, pal):
    """Step 1."""
    g, _, _ = regrid(f, size)
    g = g.copy()
    op = g[..., 3] >= 128
    g[~op] = 0
    g[op, 3] = 255
    L, P = lab(g[op][:, :3]), lab(pal)
    g[op, :3] = pal[((L[:, None, :] - P[None, :, :]) ** 2).sum(2).argmin(1)]
    return crop(g)


def eyes(a):
    """The drawn eyes: bright blocks ringed by skin (the scroll's highlights are ringed by paper and case), a pair
    3-10 columns apart on about one row. ((top, left, bottom, right) near, far) or None."""
    op = a[..., 3] > 0
    white = op & (a[..., :3].astype(int).min(2) > 225)
    lab_, sizes = pieces(white)
    H, W = op.shape
    cand = []
    for n in range(1, len(sizes)):
        ys, xs = np.nonzero(lab_ == n)
        ring = [colour(a, y, x) in SKIN or colour(a, y, x) in RUNES
                for y in range(max(0, ys.min() - 2), min(H, ys.max() + 3))
                for x in range(max(0, xs.min() - 2), min(W, xs.max() + 3)) if lab_[y, x] != n and op[y, x]]
        score = float(np.mean(ring)) if ring else 0.0
        if score >= 0.4:
            cand.append((score, sizes[n], int(ys.min()), int(xs.min()), int(ys.max()), int(xs.max())))
    best = None
    for p in cand:
        for q in cand:
            if q is p or not (3 <= q[3] - p[3] <= 10) or abs((q[2] + q[4]) - (p[2] + p[4])) > 4:
                continue
            s = p[0] + q[0] + 0.1 * (p[1] + q[1])
            if best is None or s > best[0]:
                best = (s, p, q)
    return None if best is None else (best[1][2:], best[2][2:])


def crown_soles(a):
    e = eyes(a)
    if e is None:
        return None
    near, far = e
    op = a[..., 3] > 0
    cols = list(range(near[1], far[3] + 1))
    r = near[0]
    while r - 1 >= 0 and op[r - 1, cols].any():
        r -= 1
    return r, int(np.nonzero(op.any(1))[0].max())


def cut(a, factor):
    """Step 2."""
    if factor >= 0.995:
        return a
    H, W = a.shape[:2]
    cols = sorted({colour(a, y, x) for y, x in zip(*np.nonzero(a[..., 3] > 0))})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, W), -1, int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        idx[y, x] = lut[colour(a, y, x)]
    w = np.ones((H, W), int)
    hard_r, hard_c = set(), set()
    e = eyes(a)
    if e:
        near, far = e
        hard_r = set(range(near[0] - 1, max(near[2], far[2]) + 2))
        hard_c = set(range(near[1] - 1, far[3] + 2))
    rows, _ = keep_lines(list(idx), list(w), max(1, round(H * factor)), hard_r)
    kc, _ = keep_lines(list(idx[rows].T), list(w[rows].T), max(1, round(W * factor)), hard_c)
    return a[np.ix_(rows, kc)]


def head_like(px):
    c = tuple(int(v) for v in px[:3])
    return c in SKIN or c in RUNES or c in OUTLINE or min(c) > 225


def paste_head(a, head, at=None):
    """Step 3: (frame, near eye's centre column in it) or (frame, None) when the eyes are not found."""
    e = at or eyes(a)
    if e is None:
        return a, None
    near, far = e
    dy = int(round(((near[0] + near[2]) / 2 - NEAR_EYE[0] + (far[0] + far[2]) / 2 - FAR_EYE[0]) / 2))
    dx = int(round(((near[1] + near[3]) / 2 - NEAR_EYE[1] + (far[1] + far[3]) / 2 - FAR_EYE[1]) / 2))
    hy = np.array([p[0] for p in head]) + dy
    hx = np.array([p[1] for p in head]) + dx
    P = max(4, -int(hy.min()) + 4, -int(hx.min()) + 4)
    b = np.pad(a, ((P, P), (P, P), (0, 0)))
    hy, hx, dy, dx = hy + P, hx + P, dy + P, dx + P
    H, W = b.shape[:2]
    op = b[..., 3] > 0
    hm = np.zeros((H, W), bool)
    hm[hy, hx] = True
    win = grow(hm)
    win[max(0, hy.min() - 4):hy.min(), 60 + dx:69 + dx] = True
    win[61 + dy:71 + dy, max(0, 56 + dx - SIDE):70 + dx + SIDE] = True
    ok = np.zeros((H, W), bool)
    dark = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(op)):
        c = colour(b, y, x)
        ok[y, x] = c in SKIN or c in RUNES or min(c) > 225
        dark[y, x] = c in OUTLINE or c in RUNES
    inner = np.zeros((H, W), bool)
    seeds = [(y + P, x + P) for t in (near, far) for y in range(t[0], t[2] + 1) for x in range(t[1], t[3] + 1)]
    q = deque(seeds)
    for y, x in seeds:
        inner[y, x] = True
    while q:
        y, x = q.popleft()
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < H and 0 <= xx < W and win[yy, xx] and ok[yy, xx] and not inner[yy, xx]:
                inner[yy, xx] = True
                q.append((yy, xx))
    gone = inner | (grow(inner) & win & dark)
    out = b.copy()
    out[gone] = 0
    for (_, _, rgba), yy, xx in zip(head, hy, hx):
        out[yy, xx] = rgba
    for _ in range(4):                                   # holes inside the figure: what lies behind the head (the
        empty = out[..., 3] == 0                         # scroll, the collar), never skin (it would grow the drawn
        holes = empty & ~background(empty) & gone        # head back), else the outline
        if not holes.any():
            break
        for y, x in zip(*np.nonzero(holes)):
            nb = [out[yy, xx] for yy, xx in ((y, x - 1), (y, x + 1), (y + 1, x), (y - 1, x))
                  if out[yy, xx, 3] > 0 and not hm[yy, xx] and not head_like(out[yy, xx])]
            out[y, x] = nb[0] if nb else (*sorted(OUTLINE)[0], 255)
    zone = np.zeros((H, W), bool)                        # thin remains of the drawn head
    top, bot = int(hy.min()), int(hy.max())
    zone[max(0, top - 4):bot - 3, max(0, hx.min() - 2):hx.max() + 3] = True
    zone &= ~hm
    for _ in range(2):
        drawn = (out[..., 3] > 0) & ~hm
        core = np.ones((H, W), bool)
        for yy in (-1, 0, 1):
            for xx in (-1, 0, 1):
                core &= np.roll(np.roll(drawn, yy, 0), xx, 1)
        thin = zone & drawn & ~grow(core)
        if not thin.any():
            break
        out[thin] = 0
    # the drawn head was wider: what stood behind its side (the scroll, mostly) closes up to the pasted head, as on the
    # design (the scroll's interior colour carried over, its outline moved against the head); only between two
    # drawn squares, a gap of at most GAP
    filled = {}
    for y in range(top, bot + 1):
        row = np.nonzero(hm[y])[0]
        if not len(row):
            continue
        hl = int(row.min())
        x = hl - 1
        while x >= 0 and out[y, x, 3] == 0:
            x -= 1
        w = hl - 1 - x
        if not (1 <= w <= GAP) or x < 1 or head_like(out[y, x]) and tuple(int(v) for v in out[y, x, :3]) not in OUTLINE:
            continue
        filled[y] = (x, hl, out[y, x:hl].copy())
        edge = tuple(int(v) for v in out[y, x, :3])
        if edge in OUTLINE and out[y, x - 1, 3] > 0 and not head_like(out[y, x - 1]):
            inner, line = out[y, x - 1].copy(), out[y, x].copy()
            out[y, x:hl - 1] = inner
        else:
            inner, line = out[y, x].copy(), np.array([*sorted(OUTLINE)[0], 255], np.uint8)
            out[y, x + 1:hl - 1] = inner
        out[y, hl - 1] = line
    for y, (x, hl, before) in filled.items():           # a lone row would be a stick across the gap
        if y - 1 not in filled and y + 1 not in filled:
            out[y, x:hl] = before
    lab_, sizes = pieces(out[..., 3] > 0)              # crumbs
    main = int(np.argmax(sizes[1:])) + 1
    near_head = grow(hm, 3)
    for n in range(1, len(sizes)):
        m = lab_ == n
        if n != main and sizes[n] <= 3 and (m & near_head).any():
            out[m] = 0
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 61.5 + dx - xs.min()


def plug(f):
    """Pinholes: clear pieces of at most 2 squares shut in by the figure take the commonest colour round them."""
    empty = f[..., 3] == 0
    lab_, sizes = pieces(empty & ~background(empty))
    out = f.copy()
    for n in range(1, len(sizes)):
        if sizes[n] > 2:
            continue
        ys, xs = np.nonzero(lab_ == n)
        nb = [colour(f, yy, xx) for y, x in zip(ys, xs) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
              if f[yy, xx, 3] > 0]
        c = max(set(nb), key=nb.count)
        out[ys, xs] = (*c, 255)
    return out, sum(s for s in sizes[1:] if s <= 2)


def build():
    design = at1x(DESIGN)
    pal = palette(design)
    head = [(y, x, design[y, x].copy()) for y, x in HEAD if design[y, x, 3] > 0]
    idle_cs = crown_soles(crop(design))
    cells = json.load(open(lp(os.path.join(SRC, "ryze_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    out, report = {}, []
    for tag in TAGS:
        codex = at1x(os.path.join(SRC, f"ryze_{tag}.png"))
        frs = cells["tags"][tag]
        cols, rows = layout(len(frs))
        reads = [read(f, TRUE[tag], pal) for f in raw_frames(tag)]
        assert len(reads) == len(frs), tag
        refs = range(len(reads)) if REF[tag] is None else [REF[tag] - 1]
        hs = [cs[1] - cs[0] + 1 for cs in (crown_soles(reads[k]) for k in refs) if cs]
        factor = (idle_cs[1] - idle_cs[0] + 1) / float(np.median(hs))
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        frames = []
        for k, fr in enumerate(frs):
            X, Y = (k % cols) * cw, (k // cols) * ch
            cf = codex[Y:Y + ch, X:X + cw]
            if (tag, k + 1) in CODEX:
                frames.append(cf.copy())
                report.append((tag, k + 1, "Codex's (the idle)"))
                continue
            f = cut(reads[k], factor)
            eye = None
            if (tag, k + 1) not in NO_PASTE:
                f, eye = paste_head(f, head, EYES_AT.get((tag, k + 1)))
            f, holes = plug(np.pad(f, ((1, 1), (1, 1), (0, 0))))
            f = crop(f)
            cop = cf[..., 3] > 0
            ys, xs = np.nonzero(cop)
            if eye is not None:
                hits = np.nonzero((cf[..., :3] == EYE_ONLY[0]).all(-1) & cop)
                near = hits[1][hits[1] <= hits[1].min() + 1]           # Codex's near eye: the left 2x2 white
                x0 = int(round(near.mean() - eye))
            else:
                x0 = int(round((xs.min() + xs.max()) / 2 - (f.shape[1] - 1) / 2))
            y0 = fr["pivot"][1] + FEET - (f.shape[0] - 1)
            assert 0 <= x0 and x0 + f.shape[1] <= cw and 0 <= y0, (tag, k + 1, x0, y0, f.shape)
            cell = np.zeros((ch, cw, 4), np.uint8)
            cell[y0:y0 + f.shape[0], x0:x0 + f.shape[1]] = f
            frames.append(cell)
            report.append((tag, k + 1, f"{f.shape[1]}x{f.shape[0]}, " + ("head pasted" if eye is not None else
                                                                          "drawn head") +
                           (f", {holes} pinhole squares shut" if holes else "")))
        for (t, k), src in FRAMES.items():
            if t == tag:                                 # the same place over its own standing point
                (sx, sy), (px, py) = frs[src - 1]["pivot"], frs[k - 1]["pivot"]
                frames[k - 1] = np.roll(np.roll(frames[src - 1], py - sy, 0), px - sx, 1)
                report.append((tag, k, f"frame {src}"))
        for k, cell in enumerate(frames):
            X, Y = (k % cols) * cw, (k // cols) * ch
            sheet[Y:Y + ch, X:X + cw] = cell
        out[tag] = sheet
        report.append((tag, 0, f"x{factor:.2f}"))
    return out, cells, report


def review(out, cells, path):
    """Codex's frame and the new one side by side at 4x, the feet line in red."""
    cw, ch = cells["cell"]
    K, x0, x1, y0, y1 = 4, 8, 96, 22, 84
    tiles = []
    for tag in TAGS:
        old = at1x(os.path.join(SRC, f"ryze_{tag}.png"))
        frs = cells["tags"][tag]
        cols, _ = layout(len(frs))
        for k, fr in enumerate(frs):
            X, Y = (k % cols) * cw, (k // cols) * ch
            pair = []
            for a in (old, out[tag]):
                c = np.ascontiguousarray(a[Y + y0:Y + y1, X + x0:X + x1])
                img = Image.new("RGBA", (c.shape[1] * K, c.shape[0] * K), (104, 112, 72, 255))
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * K, c.shape[0] * K), Image.NEAREST))
                fy = (fr["pivot"][1] + FEET + 1 - y0) * K
                ImageDraw.Draw(img).line([(0, fy), (img.width, fy)], fill=(220, 40, 40, 255))
                pair.append(img)
            t = Image.new("RGBA", (pair[0].width * 2 + 4, pair[0].height + 16), (24, 24, 24, 255))
            t.alpha_composite(pair[0], (0, 16))
            t.alpha_composite(pair[1], (pair[0].width + 4, 16))
            ImageDraw.Draw(t).text((3, 2), f"{tag} {k + 1}: Codex | new", fill=(255, 255, 255, 255))
            tiles.append(t)
    c2 = 3
    W, H = tiles[0].size
    sheet = Image.new("RGB", (c2 * (W + 6), -(-len(tiles) // c2) * (H + 6)), (10, 10, 10))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % c2) * (W + 6), (i // c2) * (H + 6)))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    ap.add_argument("--review", help="write Codex's frames and the new ones side by side to this PNG")
    a = ap.parse_args()
    out, cells, report = build()
    for tag, k, what in report:
        print(f"{tag:9s} {'scale' if k == 0 else f'{k:5d}'}: {what}")
    if a.review:
        review(out, cells, a.review)
        print("review", a.review)
    same = True
    for tag, new in out.items():
        big = np.repeat(np.repeat(new, Z, 0), Z, 1)
        path = os.path.join(OUT, f"ryze_{tag}.png")
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA")) if os.path.exists(lp(path)) else None
            ok = old is not None and old.shape == big.shape and (old == big).all()
            same &= ok
            print(("identical " if ok else "DIFFERENT ") + path)
        else:
            Image.fromarray(big).save(lp(path))
    if a.check:
        sys.exit(0 if same else 1)
    shutil.copyfile(lp(os.path.join(SRC, "ryze_idle.png")), lp(os.path.join(OUT, "ryze_idle.png")))
    with open(lp(os.path.join(OUT, "ryze_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    print("written", ", ".join(f"ryze_{t}.png" for t in ["idle"] + TAGS), "and ryze_cells.json")


if __name__ == "__main__":
    main()
