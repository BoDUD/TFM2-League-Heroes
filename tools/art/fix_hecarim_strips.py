#!/usr/bin/env python3
"""Hecarim's action strips from Codex's whole-figure drawings (2026-10-09, assets/source/hecarim/codex_strips).

    python tools/art/fix_hecarim_strips.py [--check] [--review DIR] [--no-write] [--report]

Codex drew every action from League's own poses (MODEL_STRIPS.md) with the image generator, the whole centaur at once,
and delivered the generator's originals: soft-edged pictures at a different size and pixel pitch per strip (4-10 px a
drawn square), the figures not kept inside their cells (hooves and blades cross the cell lines) and none on the
design's 18 colours. Here, per frame:
1. the frame: the strip's pieces (alpha >= 128, 8-connected) each given to the cell its centre lies in;
2. its size: the frame's area should be the design's area times League's area for that frame over League's idle area
   (a pose keeps the body as big as the idle); the strip's frames share the median of those scales unless Codex drew a
   frame more than OWN apart from the others, which keeps its own (Codex's generator drifts in size inside a strip);
3. its squares: every picture pixel snapped to the design's palette (CIELAB), each game square the commonest colour of
   its pixels (see-through where most are), the grid anchored on the frame's lowest pixel row;
4. its place: the lowest square on League's lowest row for that frame (on the soles when League stands), the centre of
   mass on League's;
5. the design's helm and horn pasted where Codex drew its helm (the two teal eyes and the horn matched), Codex's own
   helm under it cleared - round 1 only: round 2 (one 1024 picture a frame on the game grid, codex_strips_v2) drew
   the helm like the design's in every pose and keeps it;
6. finished: pinholes filled, the outline closed, crumbs and stray outline squares gone (rigkit.finish).
Writes assets/source/native/hecarim_<tag>.png (8x, 128x112 cells, the hooves on cell row 101) and hecarim_cells.json;
the idle is the design (import_native.py's idle_breathe animates it). Then tools/art/import_native.py.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402
import design_rengar as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hecarim", "codex_strips")
SRC2 = os.path.join(ROOT, "assets", "source", "hecarim", "codex_strips_v2", "frames")   # round 2: one image a frame
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "hecarim_native.png")
PIVOT = (64, 88)                  # the standing point on the 128 canvas (the hooves on row 99)
SOLES = 99
CELL = (128, 112)
CELL_PIVOT = (64, 90)             # the standing point in a written cell (the hooves on cell row 101)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_hit", "ult", "hit", "dead"]
CODEX_TAGS = TAGS[1:]
OWN = 0.12                        # a frame whose own scale is this far from the strip's median keeps its own
FILL = 0.28                       # a game square is drawn when this share of its pixels is (thin legs and shafts stay)
MS = {"idle": [200] * 6}
HEAD_BOX = (55, 69, 66, 77)       # the design's horn and helm: rows 55-69, columns 66-77 (eyes on row 65, teeth 67)
EYES = (72.5, 65)                 # the middle of the design's two eye squares (row 65, columns 71 and 74)
EYE_REACH = (9, 10, 6)            # Codex's eyes are looked for this far from League's head (across, above, below)
GLOW = ("k", "m")                 # the bright teals of the eyes
CLEAR = (3, 3, 1)                 # Codex's helm and horn cleared this far round the pasted head (up, left, right)
CLEAR_V2 = (0, 1, 1)              # round 2's helms are drawn like the design's: only the piece's own box (a raised
                                  # glaive or hand right over the helm stays)
SPARE = {}                        # (tag, frame): [(row0, row1, col0, col1)] kept from the clearing (a raised hand)
KEEP_COLOURS = ("n", "o", "l")    # the blade and the copper: Codex's glaive stays where it crosses the head's box
# frames whose head stays Codex's own: the death's thrown-back, falling and lying heads
KEEP_HEAD = {("dead", k) for k in range(2, 9)}
HEAD_AT = {}                      # (tag, frame): (dx, dy) of the design's head where the search misses
# frames drawn from another frame of round 2: the hit's first picture came out with a smeared torso (grey patches,
# see-through holes in the read), so the hit shows the clean second picture twice (the base game's hit is one frame)
# - the death's last two pictures lay the body down as a long mound of plates (it read as a heap of stones) and lifted
#   the dropped glaive off the ground onto it: the death ends on its sixth picture (collapsed, the helm up, the glaive
#   where it fell)
SAME_AS = {("hit", 1): ("hit", 2), ("dead", 7): ("dead", 6), ("dead", 8): ("dead", 6)}
STEADY = {"run", "skill2"}         # loops whose rider must not wander across (see steady)
JOIN = 3                          # a loose piece this near the figure is joined back (a blade whose 1-square neck the
                                  # read lost: Q 2-3); the death's dropped glaive stays apart
# the run: the DESIGN itself, the oppi way - one body picture in every frame and the legs stepping under it. Round 2's
# per-frame gallop (League's) changed shape frame to frame (the user: 「人马移动有点不自然啊 参考下oppi怎么移动的」「而且
# 移动时模型有点变形」); sliding only the shins in a trot did not read (「四个脚移动时看起来不太自然」「我是指移动的时候
# 四个脚都要有明显错开并且自然的感觉」); Codex's own side-on redraw and its legs grafted under the design were another
# horse (「模型变形了啊」「武器断了啊」「这腿对吗 残疾了？」). So nothing is redrawn: the design's four legs (LEGS: rows
# 90-99, the tail's and the tabard's columns stay with the body) step in a four-beat gait (each a quarter cycle after the
# last: the two hind legs, then the two fore legs), each leg moved whole in three blocks - the thigh band (rows 90-91)
# under the hip, the cannon (92-94) half the hoof's way, the hoof (95-99): RUN_GROUND frames on the ground, the hoof
# sliding evenly from RUN_REACH columns ahead to as far behind, then the rest in the air on an even arc (up and down
# alike: 3, 5, 3 rows of RUN_LIFT) coming forward, folded up to RUN_FOLD columns (a fore hoof back, a hind one
# forward). The legs are tidied alone and shown only under the belly line; the design's body goes over
# them untouched (bobbing a row on RUN_BOB, the tail - columns up to RUN_TAIL - waving a row on RUN_WAVE).
RUN_FRAMES = 8
RUN_MS = 85
RUN_TOP, RUN_CANNON, RUN_HOOF = 90, 92, 95
RUN_LEGS = {"hind_in": (54, 63, "h"), "fore_in": (63, 73, "f"), "hind_out": (43, 54, "h"), "fore_out": (77, 88, "f")}
# a gallop's footfalls: the two hind hooves, then the two fore hooves, a quarter cycle (2 frames) apart; the two middle
# legs stand side by side, so they step less (RUN_REACH_IN: they are the far ones too) and never pile into one hoof
RUN_OFFSET = {"hind_out": 0, "hind_in": 2, "fore_in": 4, "fore_out": 6}
RUN_GROUND = 5                    # frames a hoof is on the ground (of RUN_FRAMES)
RUN_REACH, RUN_REACH_IN, RUN_LIFT, RUN_FOLD = 3, 2, 5, 2
RUN_BOB = [0, 0, 1, 0, 0, 0, 1, 0]
RUN_TAIL = 40
RUN_WAVE = [0, 0, -1, -1, 0, 0, 1, 1]


def lp(p):
    return K.lp(p)


def layout(n):
    return K.layout(n)


def league():
    with open(lp(os.path.join(SRC, "league_cells.json")), encoding="utf-8") as f:
        return json.load(f)


def league_frames(tag):
    """League's game-size frames of a tag (the pack's now strip) on 128 canvases, pivot on PIVOT."""
    cells = league()
    cw, ch = cells["cell"]
    frs = cells["tags"][tag]
    cols, _ = layout(len(frs))
    pose = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "hc_work", "pose2", f"hecarim_native_{tag}.png")
    a = np.asarray(Image.open(pose).convert("RGBA"))[K.Z // 2::K.Z, K.Z // 2::K.Z]
    out = []
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * cw, (i // cols) * ch
        cell = a[Y:Y + ch, X:X + cw].copy()
        bg = np.abs(cell[..., :3].astype(int) - 225).sum(-1) <= 12
        cell[..., 3] = np.where(bg, 0, 255)
        c = np.zeros((128, 128, 4), np.uint8)
        K.put(c, cell, PIVOT[0] - fr["pivot"][0], PIVOT[1] - fr["pivot"][1])
        out.append(c)
    return out, [fr["ms"] for fr in frs]


def codex_frames(tag):
    """Codex's frames of a tag: [(RGBA crop of the picture, its mask)], the pieces given to cells by their centres."""
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"hecarim_{tag}_generator.png"))).convert("RGBA"))
    n = len(league()["tags"][tag])
    cols, rows = layout(n)
    cw, ch = raw.shape[1] / cols, raw.shape[0] / rows
    op = raw[..., 3] >= 128
    lab, k = label8(op)
    sizes = np.bincount(lab.ravel())
    owner = np.full(k + 1, -1)
    for p in range(1, k + 1):
        if sizes[p] < 30:                       # specks of the generator's haze
            continue
        ys, xs = np.nonzero(lab == p)
        cy, cx = ys.mean(), xs.mean()
        cell = int(cy // ch) * cols + int(cx // cw)
        owner[p] = cell if cell < n else -1
    out = []
    for i in range(n):
        m = np.isin(lab, np.nonzero(owner == i)[0])
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        out.append((raw[y0:y1, x0:x1], m[y0:y1, x0:x1]))
    return out


def label8(m):
    """8-connected labels of a mask (scipy-free)."""
    H, W = m.shape
    lab = np.zeros((H, W), np.int32)
    k = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        k += 1
        st = [(y, x)]
        lab[y, x] = k
        while st:
            cy, cx = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = k
                        st.append((ny, nx))
    return lab, k


INK = 14                          # picture pixels this dark (luminance) are the outline; darker armour is not


class Pal:
    """The design's palette; the outline colour only for near-black pixels (Hecarim's dark armour snapped to the
    outline would be dropped as stray outline by the finish, leaving the hooves floating)."""

    def __init__(self, design):
        self.rgb = np.array(design.palette, np.uint8)
        self.lab = R.lab(self.rgb.reshape(1, -1, 3).astype(float))[0]
        self.ink = int(np.argmin(self.rgb.astype(int).sum(1)))

    def snap(self, pic, mask):
        d = ((R.lab(pic[..., :3].astype(float))[..., None, :] - self.lab[None, None]) ** 2).sum(-1)
        lum = 0.299 * pic[..., 0] + 0.587 * pic[..., 1] + 0.114 * pic[..., 2]
        d[..., self.ink] = np.where(lum <= INK, -1, np.inf)
        idx = d.argmin(-1)
        idx[~mask] = -1
        return idx


def vote(idx, pitch):
    """Game squares of a snapped picture at `pitch` picture pixels a square, the grid anchored on its lowest row and
    left column; each square the commonest palette index of its pixels, -1 (clear) where most are clear."""
    H, W = idx.shape
    h, w = int(np.ceil(H / pitch)), int(np.ceil(W / pitch))
    oy = H - h * pitch
    out = np.full((h, w), -1, int)
    for y in range(h):
        y0, y1 = int(round(oy + y * pitch)), int(round(oy + (y + 1) * pitch))
        for x in range(w):
            x0, x1 = int(round(x * pitch)), int(round((x + 1) * pitch))
            blk = idx[max(y0, 0):y1, x0:x1].ravel()
            if blk.size == 0 or (blk >= 0).sum() < FILL * blk.size:
                continue
            v, c = np.unique(blk[blk >= 0], return_counts=True)
            out[y, x] = v[c.argmax()]
    return out


def bridge(c):
    """One-square gaps across a thin limb or shaft closed: a clear square between two drawn squares (left and right,
    or above and below, or on a diagonal) takes the darker of them."""
    op = c[..., 3] > 0
    lum = 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]
    out = c.copy()
    H, W = op.shape
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if op[y, x]:
                continue
            for (ay, ax), (by, bx) in (((0, -1), (0, 1)), ((-1, 0), (1, 0)), ((-1, -1), (1, 1)), ((-1, 1), (1, -1))):
                if op[y + ay, x + ax] and op[y + by, x + bx]:
                    p, q = (y + ay, x + ax), (y + by, x + bx)
                    out[y, x] = c[p] if lum[p] <= lum[q] else c[q]
                    break
    return out


def finish_v2(c, outline):
    """rigkit.finish without its stray-outline pass: round 2's thin black lines (the glaive's 1-square shaft) are
    drawing, and dropping them as stray outline cut the blade off (Q 2-3). Pinholes filled, the outline closed (never
    under the soles), crumbs under 3 squares gone."""
    import strips
    a = K.fill_pinholes(c.copy(), 3, outline)
    low = int(np.nonzero(a[..., 3].any(1))[0].max())
    a, _, _ = strips.complete_outline(a, color=tuple(outline), feet=max(SOLES, low))
    for comp in K.pieces(a)[1:]:
        if len(comp) < 3:
            for y, x in comp:
                a[y, x] = 0
    a = thin_ring(a, outline)
    return K.fill_pinholes(a, 2, outline)


def thin_ring(a, outline):
    """The outer square of a 2-square outline goes: an outline square touching the clear outside on exactly one side
    (a 1-square line - the shaft - touches it on two and stays), with no colour among its 8 neighbours, lying on
    another outline square that has colour beside it. The design's outline is one square (oppi's way)."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    ink = op & (a[..., :3] == np.array(outline, np.uint8)).all(-1)
    col = op & ~ink
    pc = np.pad(col, 1)
    near_col = np.zeros((H, W), bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                near_col |= pc[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
    po, pk = np.pad(op, 1), np.pad(ink & near_col, 1)
    gone = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(ink & ~near_col)):
        clear = [(dy, dx) for dy, dx in K.N4 if not po[1 + y + dy, 1 + x + dx]]
        if len(clear) != 1:
            continue
        dy, dx = clear[0]
        if pk[1 + y - dy, 1 + x - dx]:                 # the square behind it, away from the outside
            gone[y, x] = True
    out = a.copy()
    out[gone] = 0
    return out


def join(c, reach=JOIN):
    """Loose pieces (6+ squares) within `reach` of the largest one joined to it by a line of the colour where the
    line meets the figure."""
    comps = K.pieces(c)
    if len(comps) < 2:
        return c
    main = np.zeros(c.shape[:2], bool)
    for y, x in comps[0]:
        main[y, x] = True
    my, mx = np.nonzero(main)
    out = c.copy()
    for comp in comps[1:]:
        if len(comp) < 6:
            continue
        best = None
        for y, x in comp:
            d = np.maximum(np.abs(my - y), np.abs(mx - x))
            j = int(d.argmin())
            if best is None or d[j] < best[0]:
                best = (int(d[j]), (y, x), (int(my[j]), int(mx[j])))
        if best[0] > reach:
            continue
        (y0, x0), (y1, x1) = best[1], best[2]
        col = c[y1, x1].copy()
        n = max(abs(y1 - y0), abs(x1 - x0))
        for t in range(1, n):
            out[int(round(y0 + (y1 - y0) * t / n)), int(round(x0 + (x1 - x0) * t / n))] = col
    return out


def v2_frame(tag, k, pal, sk):
    """Round 2's drawing of a frame (one 1024 image on the 128x128 grid at 8x, drawn over the skeleton `sk`), read on
    its own squares (regrid at the canvas pitch), snapped to the palette and set where the skeleton stands (its lowest
    row on the skeleton's, its centre of mass on the skeleton's); None when the picture is not there."""
    from regrid import regrid
    path = os.path.join(SRC2, f"{tag}_{k}.png")
    if not os.path.exists(lp(path)):
        return None
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).copy()
    if (a[..., 3] == 255).all():                     # a magenta background instead of alpha
        key = np.abs(a[..., :3].astype(int) - (255, 0, 255)).sum(-1) < 90
        a[key, 3] = 0
    pitch = a.shape[1] / 128
    g, _, _ = regrid(a, size=pitch)
    m = g[..., 3] >= 128
    idx = pal.snap(g, m)
    ys, xs = np.nonzero(idx >= 0)
    idx = idx[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sy, sx = np.nonzero(sk[..., 3] > 0)
    gy, gx = np.nonzero(idx >= 0)
    oy = sy.max() - (idx.shape[0] - 1)
    ox = int(round(sx.mean() - gx.mean()))
    c = np.zeros((128, 128, 4), np.uint8)
    for y, x in zip(gy, gx):
        Y, X = oy + y, ox + x
        if 0 <= Y < 128 and 0 <= X < 128:
            c[Y, X, :3] = pal.rgb[idx[y, x]]
            c[Y, X, 3] = 255
    return c


def run_rig(design):
    """The run from the design's own body and legs (see RUN_LEGS)."""
    import math
    a = design.a
    rnd = lambda v: int(math.floor(v + 0.5))

    def pose(j, reach):
        """(hoof across, share of the lift) in the leg's own frame j."""
        if j < RUN_GROUND:
            return reach - 2 * reach * j / (RUN_GROUND - 1), 0.0
        q = (j - RUN_GROUND + 0.5) / (RUN_FRAMES - RUN_GROUND)
        return -reach + 2 * reach * q, math.sin(math.pi * q)
    body = a.copy()
    for x0, x1, _ in RUN_LEGS.values():
        body[RUN_TOP:, x0:x1] = 0
    frames = []
    for k in range(RUN_FRAMES):
        c = np.zeros_like(a)
        for name, (x0, x1, kind) in RUN_LEGS.items():          # the far legs first
            d, up = pose((k + RUN_OFFSET[name]) % RUN_FRAMES, RUN_REACH_IN if name.endswith("in") else RUN_REACH)
            lift = rnd(RUN_LIFT * up)
            fold = rnd(RUN_FOLD * up) * (-1 if kind == "f" else 1)
            for r0, r1, dx in ((RUN_TOP, RUN_CANNON, 0), (RUN_CANNON, RUN_HOOF, rnd(d / 2)), (RUN_HOOF, 128, rnd(d) + fold)):
                seg = np.zeros_like(a)
                seg[r0:r1, x0:x1] = a[r0:r1, x0:x1]
                seg = K.shifted(seg, dx, -lift)
                m = seg[..., 3] > 0
                c[m] = seg[m]
        c = finish_v2(c, design.outline)
        c[:RUN_TOP + RUN_BOB[k]] = 0
        b = K.shifted(body, 0, RUN_BOB[k])
        if RUN_WAVE[k]:
            tail = b.copy()
            tail[:, RUN_TAIL + 1:] = 0
            b[:, :RUN_TAIL + 1] = 0
            tail = K.shifted(tail, 0, RUN_WAVE[k])
            m = tail[..., 3] > 0
            b[m] = tail[m]
        m = b[..., 3] > 0
        c[m] = b[m]
        frames.append(c)
    return frames

def build(design, pal, tag, report):
    if tag == "run":
        return run_rig(design), [RUN_MS] * RUN_FRAMES
    lol, ms = league_frames(tag)
    lol_idle = league_frames("idle")[0][0]
    base = (design.a[..., 3] > 0).sum() / (lol_idle[..., 3] > 0).sum()
    cod = codex_frames(tag)
    scales = []
    for (pic, m), L in zip(cod, lol):
        want = base * (L[..., 3] > 0).sum()
        scales.append(np.sqrt(want / m.sum()))
    med = float(np.median(scales))
    out = []
    for i, ((pic, m), L) in enumerate(zip(cod, lol)):
        s = scales[i] if abs(scales[i] / med - 1) > OWN else med
        g = vote(pal.snap(pic, m), 1 / s)
        ys, xs = np.nonzero(g >= 0)
        g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        lop = L[..., 3] > 0
        ly, lx = np.nonzero(lop)
        bottom = ly.max()
        gy, gx = np.nonzero(g >= 0)
        cx = int(round(lx.mean() - gx.mean()))
        cy = bottom - (g.shape[0] - 1)
        c = np.zeros((128, 128, 4), np.uint8)
        for y, x in zip(gy, gx):
            Y, X = cy + y, cx + x
            if 0 <= Y < 128 and 0 <= X < 128:
                c[Y, X, :3] = pal.rgb[g[y, x]]
                c[Y, X, 3] = 255
        c = K.finish(bridge(c), design.outline, SOLES)
        src = SAME_AS.get((tag, i + 1), (tag, i + 1))
        v2 = v2_frame(src[0], src[1], pal, c)
        if v2 is not None and tag != "dead":
            v2 = join(v2)
        frame_key[1] = v2 is not None
        if v2 is not None:
            c = finish_v2(bridge(v2), design.outline)
        at = None
        # round 2's helms are drawn like the design's (small, the horn, the eye squares) and move with each pose; a
        # pasted design head sat on the raised hands in attack 2-3 - they keep their own unless HEAD_AT names one
        if (tag, i + 1) not in KEEP_HEAD and (v2 is None or (tag, i + 1) in HEAD_AT):
            at = HEAD_AT.get((tag, i + 1)) or head_place(design, c, lol_head(tag, i))
            frame_key[0] = (tag, i + 1)
            c = with_head(design, c, at)
        report.append((tag, i + 1, round(s, 4), round(med, 4), g.shape, int(bottom), at))
        out.append(c)
    if tag in STEADY:
        out = steady(design, tag, out)
    return out, ms


def rider_eyes(design, f):
    """(x, y) of the rider's eyes: the topmost bright teal squares in the upper 14 rows of the figure, right of its
    middle (the tail's flames are at the left, the blade is not teal)."""
    m = np.zeros(f.shape[:2], bool)
    for k in GLOW:
        m |= (f[..., :3] == np.array(design.letters()[k], np.uint8)).all(-1) & (f[..., 3] > 0)
    ys, xs = np.nonzero(f[..., 3] > 0)
    top, mid = ys.min(), (xs.min() + xs.max()) / 2
    ty, tx = np.nonzero(m)
    keep = (ty <= top + 14) & (tx >= mid)
    if not keep.any():
        return None
    ty, tx = ty[keep], tx[keep]
    sel = ty <= ty.min() + 1
    return float(tx[sel].mean()), float(ty[sel].min())


def steady(design, tag, frames):
    """A loop's frames moved whole across so the rider's eyes follow League's head across (its offset from the
    strip's mean): Codex placed each frame by its own centre of mass, and the tail and the glaive swing that - the
    rider wandered 9 columns in the run (League's head 3.4)."""
    cells = league()
    li = cells["tags"]["idle"][0]
    lx = [fr["head"][0] - fr["pivot"][0] - (li["head"][0] - li["pivot"][0]) for fr in cells["tags"][tag]]
    ex = [rider_eyes(design, f) for f in frames]
    pairs = [(e[0], l) for e, l in zip(ex, lx) if e is not None]
    c = float(np.mean([e - l for e, l in pairs]))
    out = []
    for f, e, l in zip(frames, ex, lx):
        dx = 0 if e is None else int(round(c + l - e[0]))
        out.append(K.shifted(f, dx, 0))
    return out


def head_mask(design):
    """The design's horn and helm (HEAD_BOX, the opaque squares of the piece joined to the eyes)."""
    r0, r1, c0, c1 = HEAD_BOX
    m = np.zeros((128, 128), bool)
    m[r0:r1 + 1, c0:c1 + 1] = design.a[r0:r1 + 1, c0:c1 + 1, 3] > 0
    return m


def lol_head(tag, i):
    """League's head joint in frame i on the 128 canvas, minus League's idle head: where the head goes from the
    design's place."""
    cells = league()
    def at(fr):
        return fr["head"][0] - fr["pivot"][0], fr["head"][1] - fr["pivot"][1]
    hx, hy = at(cells["tags"][tag][i])
    ix, iy = at(cells["tags"]["idle"][0])
    return int(round(hx - ix)), int(round(hy - iy))


def head_place(design, c, guess):
    """(dx, dy) of the design's head piece: its eyes (EYES) on Codex's eyes - the topmost bright teal squares within
    EYE_REACH of League's head (the chest grin, the skull plates and the tail are lower or off to the side); League's
    head when Codex drew none there."""
    teal = np.zeros((128, 128), bool)
    for k in GLOW:
        teal |= (c[..., :3] == np.array(design.letters()[k], np.uint8)).all(-1) & (c[..., 3] > 0)
    ex, ey = EYES[0] + guess[0], EYES[1] + guess[1]
    ys, xs = np.nonzero(teal)
    near = (np.abs(xs - ex) <= EYE_REACH[0]) & (ys >= ey - EYE_REACH[1]) & (ys <= ey + EYE_REACH[2])
    if not near.any():
        return guess
    ys, xs = ys[near], xs[near]
    top = ys.min()
    sel = ys <= top + 1
    cy, cx = ys[sel].mean(), xs[sel].mean()
    return int(round(cx - EYES[0])), int(round(cy - EYES[1]))


frame_key = [None, False]          # (tag, frame), drawn in round 2


def with_head(design, c, at):
    """c with Codex's helm cleared round the design's head piece placed at offset `at` and the piece pasted;
    the glaive's blade and copper squares Codex drew in that box stay unless the head covers them."""
    dx, dy = at
    hm = head_mask(design)
    piece = np.zeros_like(design.a)
    piece[hm] = design.a[hm]
    piece = K.shifted(piece, dx, dy)
    put = piece[..., 3] > 0
    r0, r1, c0, c1 = HEAD_BOX
    box = np.zeros((128, 128), bool)
    u, l, r = CLEAR_V2 if frame_key[1] else CLEAR
    box[max(0, r0 + dy - u):r1 + dy + 1, max(0, c0 + dx - l):c1 + dx + 1 + r] = True
    for (y0, y1, x0, x1) in SPARE.get(frame_key[0], []):
        box[y0:y1 + 1, x0:x1 + 1] = False
    keep = np.zeros((128, 128), bool)
    for k in KEEP_COLOURS:
        keep |= (c[..., :3] == np.array(design.letters()[k], np.uint8)).all(-1)
    out = c.copy()
    out[box & ~keep & ~put] = 0
    out[put] = piece[put]
    # whatever Codex had above the cleared box (a crest it drew taller) and is now cut off from the body goes
    comps = K.pieces(out)
    for comp in comps[1:]:
        if len(comp) < 12 and not any(keep[y, x] for y, x in comp):
            for y, x in comp:
                out[y, x] = 0
    return K.finish(out, design.outline, SOLES, keep=put)


def grid_png(f, path, z=6):
    """A frame at z with a line every 5 squares (labelled every 10) for reading coordinates."""
    from PIL import ImageDraw
    ys, xs = np.nonzero(f[..., 3] > 0)
    y0, y1, x0, x1 = max(ys.min() - 3, 0), min(ys.max() + 4, 128), max(xs.min() - 3, 0), min(xs.max() + 4, 128)
    img = Image.new("RGBA", ((x1 - x0) * z + 30, (y1 - y0) * z + 20), (120, 128, 116, 255))
    img.alpha_composite(Image.fromarray(np.ascontiguousarray(f[y0:y1, x0:x1])).resize(((x1 - x0) * z, (y1 - y0) * z),
                                                                                          Image.NEAREST), (30, 20))
    d = ImageDraw.Draw(img)
    for y in range(y0, y1):
        if y % 5 == 0:
            d.line([(30, 20 + (y - y0) * z), (img.width, 20 + (y - y0) * z)], fill=(255, 60, 60, 90 if y % 10 else 200))
            if y % 10 == 0:
                d.text((2, 20 + (y - y0) * z - 6), str(y), fill=(255, 255, 255, 255))
    for x in range(x0, x1):
        if x % 5 == 0:
            d.line([(30 + (x - x0) * z, 20), (30 + (x - x0) * z, img.height)], fill=(60, 60, 255, 90 if x % 10 else 200))
            if x % 10 == 0:
                d.text((30 + (x - x0) * z + 2, 2), str(x), fill=(255, 255, 255, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--tags", default=",".join(CODEX_TAGS))
    ap.add_argument("--out", default=NATIVE, help="where the strips go (default: assets/source/native)")
    ap.add_argument("--nohead", action="store_true", help="debug: Codex's own heads everywhere")
    ap.add_argument("--grid", help="debug: every frame at 6x with a coordinate grid into this folder")
    a = ap.parse_args()
    if a.nohead:
        KEEP_HEAD.update((t, k) for t in CODEX_TAGS for k in range(1, 9))
    design = K.Design(DESIGN)
    pal = Pal(design)
    built = {"idle": [design.a.copy() for _ in MS["idle"]]}
    ms = {"idle": MS["idle"]}
    report = []
    for tag in a.tags.split(","):
        built[tag], ms[tag] = build(design, pal, tag, report)
    if a.report:
        for r in report:
            print(r)
    for tag in built:
        rows = K.audit(built[tag], design.a, design.outline, SOLES)
        print(f"{tag:10s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        os.makedirs(lp(a.out), exist_ok=True)
        bad = K.write_strips("hecarim", built, ms, a.out, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.grid:
        os.makedirs(a.grid, exist_ok=True)
        for t in built:
            if t == "idle":
                continue
            for k, f in enumerate(built[t], 1):
                grid_png(f, os.path.join(a.grid, f"{t}_{k}.png"))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        rows = []
        for t in built:
            rows.append((t, built[t]))
            if t != "idle":
                rows.append((t + " LoL", league_frames(t)[0]))
        K.review_sheet(rows, os.path.join(a.review, "hecarim_fix_review.png"), z=3, soles=SOLES)
        K.review_gif([(t, built[t]) for t in built], ms, os.path.join(a.review, "hecarim_fix_review.gif"), z=4)
    return built


if __name__ == "__main__":
    main()
