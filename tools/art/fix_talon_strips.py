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


def drop_specks(f, keep_min=8):
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


# the design's head (hood, crest, shadow band, lower face, chin) in design-grid cells: rows 0-9 from column 17, the
# chin row 10 columns 20-28, the mouth row 11 columns 23-27
HEAD_CELLS = [(r, c) for r in range(10) for c in range(17, 32)] + [(10, c) for c in range(20, 29)] +              [(11, c) for c in range(23, 28)]
CLASS = {**{l: 1 for l in "abcde"}, **{l: 2 for l in "fgh"}, **{l: 3 for l in "xyz"}, **{l: 4 for l in "uvw"},
         **{l: 5 for l in "pqrs"}, "k": 0, "m": 6, "n": 6, "o": 7}
LET_OF = {tuple(int(D.PAL[l][i:i + 2], 16) for i in (1, 3, 5)): l for l in D.PAL}
KEEP_HEAD = {("skill2", 1), ("skill2", 2), ("skill2_stab", 2), ("skill2_stab", 3), ("skill2_stab", 4),
             ("skill2_stab", 5), ("skill_e", 2), ("skill_e", 3), ("skill_e", 4), ("ult", 1), ("ult", 5), ("ult", 7),
             ("dead", 3), ("dead", 5), ("dead", 6), ("dead", 7), ("dead", 8)}   # tilted / turned heads: Codex's own


HEAD_SURE = 0.45     # below this Codex's head is turned / tilted: kept
FORCE_HEAD = {("skill", 1)}   # a garbled upright head under the bar: pasted anyway


def head_piece():
    rows = D.grid()
    cells = [(r, c, rows[r][c]) for r, c in HEAD_CELLS if rows[r][c] != "."]
    return cells


def classes(f):
    """Per pixel: the material class of the snapped frame (-1 empty)."""
    out = np.full(f.shape[:2], -1, int)
    op = f[..., 3] > 0
    for y, x in zip(*np.nonzero(op)):
        out[y, x] = CLASS[LET_OF.get(tuple(int(v) for v in f[y, x, :3]), "k")]
    return out


def find_head(f, piece):
    """Where the design head fits Codex's head best: (dy, dx, share of matching classes) over the piece's cells."""
    cl = classes(f)
    H, W = cl.shape
    ys = np.nonzero((cl >= 0).any(1))[0]
    best = (0, 0, -1.0)
    pr = np.array([[r, c, CLASS[l]] for r, c, l in piece])
    for dy in range(ys[0] - 4, ys[0] + 14):
        for dx in range(-10, W - 20):
            yy, xx = pr[:, 0] + dy, pr[:, 1] + dx
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            if ok.sum() < len(pr) * 0.9:
                continue
            got = cl[yy[ok], xx[ok]]
            want = pr[ok, 2]
            # the hood (1) and the face (2) weigh most; an empty cell where the piece has paint costs
            w = np.where(want == 1, 2.0, np.where(want == 2, 3.0, 1.0))
            sc = (w * (got == want)).sum() / w.sum() - 0.5 * (w * (got < 0)).sum() / w.sum()
            if sc > best[2]:
                best = (dy, dx, sc)
    return best


def paste_head(f, piece, dy, dx):
    out = f.copy()
    H, W = f.shape[:2]
    rs = [r for r, _, _ in piece]
    cs = [c for _, c, _ in piece]
    mask = {(r + dy, c + dx) for r, c, _ in piece}
    # Codex's own head pixels round it (hood blue, skin, the crest's steel) above the shoulders go
    for y in range(min(rs) + dy - 1, min(rs) + dy + 9):
        for x in range(min(cs) + dx - 2, max(cs) + dx + 3):
            if 0 <= y < H and 0 <= x < W and (y, x) not in mask and out[y, x, 3]:
                cl = CLASS[LET_OF.get(tuple(int(v) for v in out[y, x, :3]), "k")]
                if cl in (1, 2, 3, 0):
                    out[y, x] = 0
    for r, c, l in piece:
        y, x = r + dy, c + dx
        if 0 <= y < H and 0 <= x < W:
            out[y, x, :3] = [int(D.PAL[l][i:i + 2], 16) for i in (1, 3, 5)]
            out[y, x, 3] = 255
    return out


# the design's pelvis: the belt (row 18), the trousers and the teal sash with its gold edge (rows 19-24), columns 16-21
WAIST_CELLS = [(18, c) for c in range(16, 21)] + [(r, c) for r in range(19, 25) for c in range(16, 22)]
SASH = [(r, c) for r in range(19, 25) for c in (19, 20)]          # the teal sash: the anchor (teal is used by it alone)


def waist_piece():
    rows = D.grid()
    return [(r, c, rows[r][c]) for r, c in WAIST_CELLS if rows[r][c] not in ".k"]


def find_waist(f):
    """The design sash's offset onto Codex's teal (the sash), or None when the frame shows too little teal."""
    cl = classes(f)
    ys, xs = np.nonzero(cl == 6)
    if len(ys) < 4:
        return None
    best = None
    for dy in range(ys.min() - 24, ys.max() - 18):
        for dx in range(xs.min() - 21, xs.max() - 18):
            hit = sum(1 for r, c in SASH if 0 <= r + dy < cl.shape[0] and 0 <= c + dx < cl.shape[1]
                      and cl[r + dy, c + dx] == 6)
            if best is None or hit > best[0]:
                best = (hit, dy, dx)
    return best if best[0] >= 4 else None


def paste_waist(f, piece, dy, dx):
    out = f.copy()
    H, W = f.shape[:2]
    for r, c, l in piece:
        y, x = r + dy, c + dx
        if 0 <= y < H and 0 <= x < W and out[y, x, 3]:
            out[y, x, :3] = [int(D.PAL[l][i:i + 2], 16) for i in (1, 3, 5)]
    return out


def skin_off(f, head_mask):
    """Skin is the face's alone (the design): skin pixels outside the pasted head take the commonest other
    material's darkest shade round them (Codex painted belts and gloves in skin browns)."""
    out = f.copy()
    H, W = f.shape[:2]
    lets = {}
    for y, x in zip(*np.nonzero(f[..., 3] > 0)):
        lets[(y, x)] = LET_OF.get(tuple(int(v) for v in f[y, x, :3]), "k")
    DARK = {1: "b", 3: "x", 4: "v", 5: "q", 6: "m", 7: "o", 0: "k"}
    for (y, x), l in lets.items():
        if l in "fgh" and (y, x) not in head_mask:
            cnt = {}
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    m = lets.get((y + a, x + b))
                    if m and m not in "fghk":
                        cnt[CLASS[m]] = cnt.get(CLASS[m], 0) + 1
            c_ = max(cnt, key=cnt.get) if cnt else 0
            out[y, x, :3] = [int(D.PAL[DARK[c_]][i:i + 2], 16) for i in (1, 3, 5)]
    return out


def deblob(f):
    """Black masses inside the figure (2x2 outline-coloured squares with every neighbour opaque) take the darkest shade
    of the material round them - Codex filled whole pelvis areas with outline black."""
    out = f.copy()
    H, W = f.shape[:2]
    op = f[..., 3] > 0
    lets = np.full((H, W), ".", object)
    for y, x in zip(*np.nonzero(op)):
        lets[y, x] = LET_OF.get(tuple(int(v) for v in f[y, x, :3]), "k")
    k = lets == "k"
    inner = np.zeros_like(op)
    inner[1:-1, 1:-1] = op[:-2, 1:-1] & op[2:, 1:-1] & op[1:-1, :-2] & op[1:-1, 2:] & op[:-2, :-2] & op[:-2, 2:] & op[2:, :-2] & op[2:, 2:]
    blob = np.zeros_like(op)
    for y in range(H - 1):
        for x in range(W - 1):
            if k[y:y + 2, x:x + 2].all() and inner[y:y + 2, x:x + 2].all():
                blob[y:y + 2, x:x + 2] = True
    DARK = {1: "a", 3: "x", 4: "u", 5: "p", 2: "f", 6: "m", 7: "o"}
    for y, x in zip(*np.nonzero(blob)):
        cnt = {}
        for a in range(-2, 3):
            for b in range(-2, 3):
                yy, xx = y + a, x + b
                if 0 <= yy < H and 0 <= xx < W and lets[yy, xx] not in ".k":
                    c_ = CLASS[lets[yy, xx]]
                    cnt[c_] = cnt.get(c_, 0) + 1
        if cnt:
            c_ = max(cnt, key=cnt.get)
            out[y, x, :3] = [int(D.PAL[DARK[c_]][i:i + 2], 16) for i in (1, 3, 5)]
    return out


def despeckle(f):
    """A pixel whose colour none of its 8 neighbours has, with 5+ neighbours of one colour of its own material,
    takes that colour (Codex's checkered steel / cloth); outline and empty neighbours never vote."""
    out = f.copy()
    H, W = f.shape[:2]
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not f[y, x, 3]:
                continue
            me = LET_OF.get(tuple(int(v) for v in f[y, x, :3]), "k")
            if me == "k":
                continue
            nb = [LET_OF.get(tuple(int(v) for v in f[y + a, x + b, :3]), "k") if f[y + a, x + b, 3] else "."
                  for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
            if me in nb:
                continue
            same = [l for l in nb if l not in ".k" and CLASS[l] == CLASS[me]]
            if same:
                top = max(set(same), key=same.count)
                if same.count(top) >= 5:
                    out[y, x, :3] = [int(D.PAL[top][i:i + 2], 16) for i in (1, 3, 5)]
    return out


WAIST = 19                   # design-grid row: rows 0-WAIST (head, torso, belt, the cape's top) breathe
BREATH = [0, 0, 1, 1, 1, 0]   # rows the upper body sinks per idle frame (200 ms each)


def breathe(fr, ch, cw, sink):
    """The idle's breath, lossless: the legs and the cape's lower part stay; the upper body (design rows <= WAIST)
    moves down `sink` rows and is drawn over them."""
    top = D.SOLE_ROW + 1 - len(D.grid())
    low = design_at(fr, ch, cw, rows=range(top + WAIST + 1, 128))
    up_ = design_at(fr, ch, cw, dy=sink, rows=range(0, top + WAIST + 1))
    m = up_[..., 3] > 0
    low[m] = up_[m]
    return low


def flinch(fr, ch, cw, back):
    """The hit frames: the design moved back `back` columns (lossless)."""
    f = design_at(fr, ch, cw)
    return np.roll(f, -back, axis=1)


# the run rig: the design's own lower legs (the user's rule: actions stand on the idle's own legs), moved whole -
# the shin block by half the boot's step, the boot by the full step, lifted on the swing; the rest of the design
# (knees, trousers, the cape and its spear blade) bobs. Design-grid cells:
NEAR_LEG = [(r, c) for r in range(31, 42) for c in range(9, 20) if not (r <= 32 and c < 13)]
FAR_LEG = [(r, c) for r in range(31, 41) for c in range(20, 32) if not (r <= 32 and c < 24)]   # rows 31-32 cols 21-23: the red flap
SHIN_LAST = 36            # rows <= this move with the shin block, below with the boot block
# per frame (8 x 121 ms): (dx, lift) of one leg's boot; the other leg runs half a cycle later
STEP = [(4, 0), (2, 0), (0, 0), (-2, 0), (-4, 1), (-2, 3), (1, 3), (3, 1)]
RUN_BOB = [0, 1, 1, 0, 0, 1, 1, 0]
# "legs": the cross-step below (the user, 10-10: 「走路有点奇怪啊 没有明显的腿部换位」 - Codex's cross-step redraw for it
# was rejected: 「有问题的地方你帮忙修复 codex实在太烂了」); "rig": the design's lower legs stepping in place (the first run);
# "codex": Codex's first legs under the design's upper body
RUN_MODE = "legs"

# "legs": the cross-step from the design's own leg (the user on Codex's cross-step: 「有问题的地方你帮忙修复 codex实在太烂了」
# 「而且模型又变形了」「请你好好修 不要有模型变形 还有姿势奇怪」 - its legs were 1-2 px threads under the coat's left half,
# its skirt specks, and its body was not shrunk with the idle's columns). Nothing is drawn: both legs are the design's
# far leg (thigh plate, knee, shin, boot - the near one a copy of it, legs alike as league_zed's run), each row of it
# moved whole - the thigh's rows lean from the hip to the knee, the shin's on to the ankle, at most a column a row -
# the boot moved whole, the leg lifted whole for a step (its thigh then hides under the coat: a bent knee); the near
# leg over the far one, both under the body. The body is the design's: rows 0-21 as the idle, the cape on the left,
# the coat to its hem (row 25, the teal sash's end and the back flap a row lower) with the near steel plate cut at the
# hem. The run is drawn at the idle's 95% already: the idle's cut (RUN_CUT_ROWS / RUN_CUT_COLS, the rows and columns
# import_native's SHRINK takes out of the idle) is taken out of the design first and the import's shrink skips the run
# (import_native SHRINK_SKIP), so the body is the shrunk idle's pixel for pixel and the legs the idle's legs.
RUN_CUT_ROWS, RUN_CUT_COLS = (35, 37), (1, 8)
RUN_PIVOT_COL = 14             # the design column on the pivot (the idle's, kept by the shrink)
RUN_KEEP_LOW = 21              # rows 0-21 of the design kept whole (as the idle)
RUN_CAPE_COL = 11              # below that, the cape on the left (columns <= this)
RUN_HEM = 25                   # the coat's hem row; the sash's end and the back flap one row lower
STEEL = "uvwxyz"
# the far leg's cells by design row (its own outline included): thigh plate 24-27, knee 28-30, shin 31-37, boot 38-40
RUN_LEG = {24: range(24, 28), 25: range(23, 29), 26: range(23, 30), 27: range(23, 31), 28: range(25, 31),
           29: range(25, 32), 30: range(24, 31), 31: range(24, 30), 32: range(24, 28), 33: range(23, 28),
           34: range(23, 27), 35: range(23, 27), 36: range(22, 26), 37: range(22, 27), 38: range(21, 28),
           39: range(21, 30), 40: range(21, 30)}
LEG_HIP, LEG_KNEE, LEG_ANKLE, LEG_BOOT = 24, 30, 37, 38      # design rows; the hip's middle is column 26
RUN_HIPS = {"near": 6, "far": 7}             # the hips from the pivot: under the coat's middle (columns +2..+9)
RUN_FAR_BACK = -1                            # the far foot's path a column behind its hip's: both feet share one path
# one leg's cycle, from the frame its foot lands: (knee lean, ankle lean, lift) - leans in columns from the design's
# own leg (its shin already slants back 3), at most a column a row; lift in rows off the ground. League's Talon_run at
# ~0.6: the foot lands ahead and slides back 3 a frame under him (planted 4 frames), pushes off behind, comes up under
# him (lifted 5-6, clear of the planted leg's knee) and through past the planted leg, then reaches ahead; the far leg
# half a cycle later. The feet
# change order twice a cycle (10-11 apart at each landing, front and back swapped) and one is always on the ground.
# Earlier cycles: the back leg leaned 8 columns (a long stick); both feet within 9 (the passing legs one dark lump);
# the heel kicked back to the cape (a leg touching the cape walls in a hole between them, the coat's hem and the leg -
# work/tl/rev/run_tune_tl.py tries cycles and counts those holes: none here).
RUN_CYCLE = [(3, 6, 0), (2, 3, 0), (0, 0, 0), (-1, -3, 0), (-2, -5, 1), (0, -1, 5), (2, 1, 6), (4, 4, 2)]
RUN_DIP = [0, 1, 2, 1, 0, 1, 2, 1]           # the body sunk: lowest at each mid-stance (2, 6)


def run_legs(fr, ch, cw, k, only=None):
    g = D.grid()
    rows = [i for i in range(len(g)) if i not in RUN_CUT_ROWS]
    cols = [j for j in range(len(g[0])) if j not in RUN_CUT_COLS]
    nrow = {r: i for i, r in enumerate(rows)}
    ncol = {c: j for j, c in enumerate(cols)}
    px, py = fr["pivot"]
    ground = py + FEET
    piv = ncol[RUN_PIVOT_COL]
    dip = RUN_DIP[k % 8]
    out = np.zeros((ch, cw, 4), np.uint8)
    rgb = lambda l: [int(D.PAL[l][i:i + 2], 16) for i in (1, 3, 5)]

    def put(y, x, l):
        if 0 <= y < ch and 0 <= x < cw:
            out[y, x, :3] = rgb(l)
            out[y, x, 3] = 255

    leg_rows = [r for r in sorted(RUN_LEG) if r not in RUN_CUT_ROWS]
    i_knee = leg_rows.index(LEG_KNEE)
    i_ank = max(i for i, r in enumerate(leg_rows) if r < LEG_BOOT)

    def leg(side, phase):
        sk, sa, lift = RUN_CYCLE[phase % 8]
        if side == "far":
            sa += RUN_FAR_BACK
            sk += RUN_FAR_BACK // 2
        base = RUN_HIPS[side] - (ncol[26] - piv)
        sole = len(leg_rows) - 1
        for i, r in enumerate(leg_rows):
            if i <= i_knee:
                sh = sk * i / i_knee
            elif i <= i_ank:
                sh = sk + (sa - sk) * (i - i_knee) / (i_ank - i_knee)
            else:
                sh = sa
            y = ground - lift - (sole - i)
            for c in RUN_LEG[r]:
                l = g[r][c] if c < len(g[r]) else "."
                if l != ".":
                    put(y, px + ncol[c] - piv + base + int(np.floor(sh + 0.5)), l)

    if only in (None, "far"):
        leg("far", k + 4)
    if only in (None, "near"):
        leg("near", k)
    if only is not None:
        return out                               # one leg alone (work/tl/rev/run_tune_tl.py measures overlaps)
    near = set(NEAR_LEG)
    for r in rows:
        for c in cols:
            l = g[r][c]
            if l == ".":
                continue
            cape = r > RUN_KEEP_LOW and c <= RUN_CAPE_COL and (r, c) not in near
            skirt = RUN_KEEP_LOW < r <= RUN_HEM and 12 <= c <= 24 and (c <= 15 or l not in STEEL)
            skirt |= r == RUN_HEM + 1 and 19 <= c <= 23 and l not in STEEL
            if r <= RUN_KEEP_LOW or cape or skirt:
                put(ground - (len(rows) - 1 - nrow[r]) + dip, px + ncol[c] - piv, l)
    return out


def run_rig(fr, ch, cw, k):
    rows = D.grid()
    top = D.SOLE_ROW + 1 - len(rows)
    oy, ox = fr["pivot"][1] + FEET - D.SOLE_ROW + top, fr["pivot"][0] - D.MID_COL + D.canvas(rows)[..., 3].any(0).nonzero()[0][0]
    rgb = lambda l: [int(D.PAL[l][i:i + 2], 16) for i in (1, 3, 5)]
    out = np.zeros((ch, cw, 4), np.uint8)
    legs = set(NEAR_LEG) | set(FAR_LEG)

    def put(r, c, l, dy=0, dx=0):
        y, x = oy + r + dy, ox + c + dx
        if 0 <= y < ch and 0 <= x < cw:
            out[y, x, :3] = rgb(l)
            out[y, x, 3] = 255

    def leg(cells, phase):
        dx, lift = STEP[phase % len(STEP)]
        for r, c in cells:
            l = rows[r][c] if c < len(rows[r]) else "."
            if l == ".":
                continue
            if r <= SHIN_LAST:
                put(r, c, l, -((lift + 1) // 2), int(round(dx / 2)))
            else:
                put(r, c, l, -lift, dx)

    bob = RUN_BOB[k % len(RUN_BOB)]
    leg(FAR_LEG, k + 4)                          # the far leg behind
    for r, row in enumerate(rows):
        for c, l in enumerate(row):
            if l != "." and (r, c) not in legs:
                put(r, c, l, bob)
    leg(NEAR_LEG, k)                             # the near leg in front
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


def finish(f, fr, run=False, force=False):
    f = drop_specks(f, 10 ** 6 if run else 8)
    f[fr["pivot"][1] + FEET + 1:] = 0
    f, _, _ = G.complete_outline(f, color=OUTLINE, feet=fr["pivot"][1] + FEET)
    f = close_all(f, fr["pivot"][1] + FEET)
    for _ in range(4):                                  # filling a pocket can close a new hole: until stable
        g = fill_holes(f, run=run, pocket_max=200 if force else (0 if run else 40), force=force)
        if (g == f).all():
            break
        f = g
    return f


# frames whose open pockets are holes in the body all the same (reviewed at 10x): every pocket filled, whatever its
# ring - the hips of attack 3 / skill2_stab 2, the slit between skill 3's hanging cape blade and its leg, the knee of
# skill2 5, run 4's boot against the cape's spear tip. run 8's gap between the legs is a leg gap: kept.
FILL_POCKETS = {("attack", 3), ("skill", 3), ("skill2", 5), ("skill2_stab", 2), ("run", 4)}


def fill_holes(f, run=False, pocket_max=40, force=False):
    """Holes read as holes (the user: 「这里留个大窟窿」): every transparent region the figure encloses, and every
    region a 1-px opening leaves nearly enclosed (a 3x3 closing) when one material holds >= 60% of its ring, is
    filled - pinholes (<= 2 px) and the run's leg gaps with the outline (a crease), the rest with the dark shade of the
    material round it (a fold in the cape or the clothes)."""
    from scipy import ndimage
    out = f.copy()
    op = f[..., 3] > 0
    H, W = op.shape

    def enclosed(mask):
        lab, n = ndimage.label(~mask)
        border = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
        return [lab == k for k in range(1, n + 1) if k not in border]

    regions = [(m, True) for m in enclosed(op)]
    closed = ndimage.binary_closing(op, structure=np.ones((3, 3))) | op
    hole_px = np.zeros_like(op)
    for m, _ in regions:
        hole_px |= m
    for m in enclosed(closed):
        m = m & ~op & ~hole_px
        if 0 < m.sum() <= pocket_max:
            regions.append((m, False))
    DARK = {1: "b", 3: "v", 4: "u", 5: "q", 2: "f", 6: "m", 7: "o"}
    for m, is_hole in regions:
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op & ~m
        cnt = {}
        for y, x in zip(*np.nonzero(ring)):
            l = LET_OF.get(tuple(int(v) for v in out[y, x, :3]), "k")
            if l != "k":
                cnt[CLASS[l]] = cnt.get(CLASS[l], 0) + 1
        tot = sum(cnt.values())
        top = max(cnt, key=cnt.get) if cnt else None
        share = cnt[top] / tot if tot else 0
        if not is_hole and share < 0.6 and not force:
            continue                                   # an open gap between two different parts: kept
        if run and m.sum() > 2:
            continue                                   # the run's gaps between the legs, the cape and the coat: kept
        if m.sum() <= 2 or run or top is None:
            l = "k"
        else:
            l = DARK.get(top, "k")
        out[m, :3] = [int(D.PAL[l][i:i + 2], 16) for i in (1, 3, 5)]
        out[m, 3] = 255
    return out


def close_all(f, sole):
    """Every clear pixel 4-next to a light figure pixel (thin blades included: the design outlines its blades too)
    becomes the outline; under the soles the light pixel itself darkens instead."""
    out = f.copy()
    op = f[..., 3] > 0
    lum = f[..., :3].astype(float) @ [0.299, 0.587, 0.114]
    light = op & (lum >= 45)
    H, W = op.shape
    for y, x in zip(*np.nonzero(light)):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and not op[yy, xx]:
                if yy > sole:
                    out[y, x, :3] = OUTLINE
                else:
                    out[yy, xx, :3] = OUTLINE
                    out[yy, xx, 3] = 255
    return out


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
    global PIECE, PELVIS
    PIECE = head_piece()
    PELVIS = waist_piece()
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
            note = ""
            if tag == "hit":
                f = flinch(fr, ch, cw, 2 if k == 1 else 1)
                note = "design flinch"
            elif (tag, k) == ("skill2_stab", 1):
                f = design_at(fr, ch, cw)
                note = "design (wind-up)"
            elif tag == "run":
                if RUN_MODE == "legs":
                    f = run_legs(fr, ch, cw, k - 1)
                    note = "design legs, cross-step"
                elif RUN_MODE == "rig":
                    f = run_rig(fr, ch, cw, k - 1)
                else:
                    f = run_frame(despeckle(f), fr, ch, cw)
            else:
                f = deblob(despeckle(f))
                if (tag, k) not in KEEP_HEAD:
                    dy, dx, sc = find_head(f, PIECE)
                    wz = find_waist(f)
                    # the pelvis only on upright frames (the head fits) with a clear sash
                    if wz and wz[0] >= 10 and (sc >= HEAD_SURE or (tag, k) in FORCE_HEAD):
                        f = paste_waist(f, PELVIS, wz[1], wz[2])
                        note += f"waist {wz[1]},{wz[2]} ({wz[0]}/12) "
                    if sc >= HEAD_SURE or (tag, k) in FORCE_HEAD:
                        f = paste_head(f, PIECE, dy, dx)
                        f = skin_off(f, {(r + dy, c + dx) for r, c, _ in PIECE})
                        note += f"head at {dy},{dx} ({sc:.2f})"
                    else:
                        note += f"own head (best {sc:.2f})"
            f = finish(f, fr, run=tag == "run", force=(tag, k) in FILL_POCKETS)
            out.append(f)
            print(f"{tag}_{k:02d}: grid {s} px, {int((f[..., 3] > 0).sum())} px {note}")
        built[tag] = out
        strip(out, cw, ch).save(lp(os.path.join(OUT, f"talon_{tag}.png")))
    idle = [breathe(fr, ch, cw, BREATH[k % len(BREATH)]) for k, fr in enumerate(cells["tags"]["idle"])]
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
