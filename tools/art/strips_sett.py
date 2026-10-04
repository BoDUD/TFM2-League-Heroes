#!/usr/bin/env python3
"""Sett's action strips from Codex's step-2 drafts (assets/source/sett/MODEL_STRIPS.md), read like the design.

    python tools/art/strips_sett.py [--raw <Codex's delivery folder>] [--review <png>]

Codex's own strips (sett_strips_pack_done.zip) were put together from cut-up pieces of the design and broke into
specks (the run's legs a heap of gold bits, the punching arms long sticks, the death a lump); its raw generations
(raw/sett_<tag>_raw.png) draw every pose cleanly, at their own size (50-54 squares tall, bigger than the design's 42).
So each raw frame is read the way the design was read from Codex's draft B (tools/art/design_sett.py, Vi's
strips_vi.py): every game pixel reads the block of the draft it covers, snapped to the design's colours (the eyes'
amber left out); specks merged; the outline closed; no black inside the body (design_sett.clean). Then:
  - the scale: Codex drew every strip at its own size, so each strip's block is its standing frame's height over
    the design's 42 rows (REF);
  - the design's head (the ear tips to the chin, pack_sett_strips.head_mask) is pasted where the frame's own head
    matches it best (hair and skin squares), the frame's own hair, eyes and (on the face's side) skin within 2 squares
    of it cleared first (Vi's paste_head; Sett has no hair falling behind his head), the outline of Codex's own ears
    left round nothing dropped and small pockets filled; the fallen death frames keep their own head (OWN_HEAD), as
    Vi's did;
  - the place: across the cell the pasted head goes where League's head joint is in sett_cells.json (native_pose.py
    on poses.json; the design's head stands 7.9 squares left of the idle's joint and 13.3 above it); down the cell
    the soles go on the feet line (row 67), a run or slam frame drawn off Codex's ground line keeps its lift
    (FLIGHT, cut to stay inside the cell), the flight hangs 5 rows over the line (HOVER), and the slam's first frame
    drops onto the second's spot (HEAD_FROM);
  - the run's far leg, which Codex shaded violet, takes the trousers' shades (LEG_VIOLET).
--raw copies Codex's raw generations into assets/source/sett/codex_strips/ snapped to the design's colours (an
indexed PNG reads back exactly the same). Writes assets/source/native/sett_<tag>.png (8x, 96 x 80 cells,
native_refs.layout) and sett_cells.json (League's pivots and the strips' ms); the idle is the design six times.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_sett as D  # noqa: E402
import pack_sett_strips as K  # noqa: E402
import strips as G  # noqa: E402
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sett", "codex_strips")
CELLS = os.path.join(SRC, "sett_cells.json")
OUT = os.path.join(ROOT, "assets", "source", "native")
TAGS = ["run", "attack", "attack2", "skill", "skill2", "ult", "ult_dash", "ult_slam", "hit", "dead"]
FEET = 67                        # the cell's lowest row for the soles
HEAD_AT = (-7.9, -13.3)          # the design head's top-left from League's head joint (idle: (40, 26) / (47.9, 39.3))
DESIGN_PIVOT = (64, 88)
# per strip: (frame, rows) - that frame stands rows tall in the design's squares (its standing frame: 42), or a block
# size in the draft's pixels where no frame stands (the flight: between the throw's 7.6 and the slam's 7.8)
REF = {"run": ("max", 42), "attack": (4, 42), "attack2": (4, 42), "skill": (6, 42), "skill2": (6, 42),
       "ult": (2, 41), "ult_dash": 7.7, "ult_slam": (3, 42), "hit": (1, 42), "dead": (0, 42)}
FLIGHT = {"run", "ult_slam"}     # strips whose frames may be drawn above Codex's ground line
HANG = {"ult_dash"}              # placed by League's head height, not on the ground
OWN_HEAD = {("dead", k) for k in range(2, 8)}
HOVER = {"ult_dash": 5}          # the flight's lowest row this many rows over the feet line (League's dash skims it)
TOP = 2                          # an airborne frame's lift is cut so its top stays this many rows inside the cell
# (tag, frame): the frame's head this many squares from that of another frame of the strip instead of League's: the
# slam's first frame drops onto the spot of the second (League's power bomb starts it 20 squares back, mid-leap)
HEAD_FROM = {("ult_slam", 0): (1, -5)}
# strips whose legs Codex shaded with the mantle's violet (the far leg in the run): violet squares in the lowest
# LEG_ROWS rows of the frame take the trousers' shades
LEG_VIOLET = {"run": 16}
TROUSERS = {"290B42": "9FA8C3", "3C1268": "9FA8C3", "531E8E": "B2B9D2"}
# The run's legs, redrawn (「移动的时候腿有点细？有点变形？」: Codex's legs were 3-4 squares thin, the back one came
# and went behind the coat and the shoes changed size; the far leg barely took turns with the near one). As Sivir's
# run (rig_sivir_run.py, the version the user liked): Codex's upper body stays (the pumping fists, the lean, the coat
# streaming back); under the belt its legs go and two legs are drawn along a run cycle - each foot placed (ahead on
# the contact, drawn back under the body, off the toe, kicked up behind, swung through, reaching), the knee solved
# forward, both legs the design's length and width (thigh 6 squares, shin 4) in the trousers' shades with the gold
# side stripe, the far leg a shade darker and behind the coat, the near one over everything, the design's own shoe
# (its far one, curled to the right) at each ankle. One foot is always on the ground.
RUN_THIGH, RUN_SHIN = 8.0, 7.2            # hip -> knee, knee -> ankle: a little longer than the drop from the
#                                           belt to the shoe top (~13 rows), so the planted leg bends at the knee
RUN_W = (2.7, 1.9)                        # half widths of the thigh and the shin
RUN_FOOT = [(6.6, 0), (3.3, 0), (0.0, 0), (-3.9, 0), (-7.7, 1), (-7.2, 5.5), (-1.1, 5.5), (5.5, 2.2)]
RUN_HIP_GAP = 1.5                          # the near hip this far left of the trousers' middle, the far one right
RUN_SHADES = {"near": ("DCDFE8", "C4C9DB", "9FA8C3", "DF9704"), "far": ("C4C9DB", "B2B9D2", "9FA8C3", "BD7702")}
SHOE = (66, 95, 75, 100)                  # the design's far shoe on the canvas (x0, y0, x1, y1)
SHOE_ANKLE = (68.5, 95)
COAT = {"1F0917", "340F1E", "451A2A"}
RUN_COAT = 12                              # the coat's tails end above the knees: only legs this near the ground
HEAD_SURE = 0.5
HAIR = {"55011B", "810426", "AA0C35", "C7153E", "D51B45"}
SKIN = {"B06B44", "DC9263", "F9BC89"}
EYES = {"DCDFE8", "C8700A"}
OUTLINE = (0x05, 0x03, 0x02)


def hexs(p):
    return "%02X%02X%02X" % tuple(int(v) for v in p[:3])


def palette():
    """The design's colours but the eyes' amber (it comes back with the pasted head)."""
    cols = [h for hs in D.PALETTE.values() for h in hs if h != D.EYE]
    return cols, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in cols], float)


def snap(img):
    """The draft with every pixel on the palette and its alpha 0 or 255: what read_blocks sees of it."""
    cols, pal = palette()
    a = np.asarray(img.convert("RGBA"))
    out = np.zeros_like(a)
    op = a[..., 3] > 128
    ys, xs = np.nonzero(op)
    idx = np.argmin(((a[ys, xs, :3].astype(float)[:, None] - pal[None]) ** 2).sum(-1), 1)
    out[ys, xs, :3] = pal[idx].astype(np.uint8)
    out[ys, xs, 3] = 255
    return out


def to_indexed(a):
    cols, pal = palette()
    im = Image.new("P", (a.shape[1], a.shape[0]), 0)
    flat = [0, 0, 0] + [int(v) for c in pal for v in c]
    im.putpalette(flat + [0] * (768 - len(flat)))
    idx = np.zeros(a.shape[:2], np.uint8)
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    idx[ys, xs] = np.argmin(((a[ys, xs, :3].astype(float)[:, None] - pal[None]) ** 2).sum(-1), 1) + 1
    im.putdata(idx.ravel().tolist())
    im.info["transparency"] = 0
    return im


def components(mask, k=4):
    """8-connected pieces of a mask read in k x k blocks: (y0, y1, x0, x1, blocks) in full-size pixels."""
    H, W = mask.shape
    h, w = H // k, W // k
    m = mask[:h * k, :w * k].reshape(h, k, w, k).any((1, 3))
    lab = np.zeros((h, w), int)
    out = []
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        lab[y, x] = len(out) + 1
        st, ys, xs = [(y, x)], [], []
        while st:
            cy, cx = st.pop()
            ys.append(cy)
            xs.append(cx)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = len(out) + 1
                        st.append((ny, nx))
        out.append((min(ys) * k, (max(ys) + 1) * k, min(xs) * k, (max(xs) + 1) * k, len(ys)))
    return out


def raw_frames(a, n):
    """The n biggest figures of a draft in reading order (rows of native_refs.layout), each alone on a clear copy,
    and the row each stands in."""
    cols, rows = layout(n)
    comps = sorted(components(a[..., 3] > 0), key=lambda c: -c[4])[:n]
    band = a.shape[0] / rows
    comps.sort(key=lambda c: (int((c[0] + c[1]) / 2 // band), c[2]))
    out = []
    for y0, y1, x0, x1, _ in comps:
        f = np.zeros_like(a)
        f[y0:y1, x0:x1] = a[y0:y1, x0:x1]
        out.append((f, int((y0 + y1) / 2 // band)))
    return out


def extent(f):
    ys, xs = np.nonzero(f[..., 3] > 0)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


def block_size(tag, frames):
    ref = REF[tag]
    if not isinstance(ref, tuple):
        return float(ref)
    k, rows = ref
    hs = [extent(f)[1] - extent(f)[0] for f, _ in frames]
    return (max(hs) if k == "max" else hs[k]) / rows


def read(f, px, bottom):
    """The frame read on blocks of px draft pixels, its lowest row on `bottom`."""
    cols, pal = palette()
    y0, y1, x0, x1 = extent(f)
    H = int(np.ceil((bottom - y0) / px)) + 1
    W = int(np.ceil((x1 - x0) / px)) + 4
    left = (x0 + x1) / 2 - W * px / 2
    fig, feat = D.read_blocks(f, left, bottom, px, W, H, cols, pal)
    fig = D.despeckle(fig, feat)
    rows = np.nonzero(fig[..., 3].any(1))[0]
    fig = fig[rows.min():rows.max() + 1]
    fig, _, _ = G.complete_outline(fig, feet=fig.shape[0] - 1)
    fig = D.clean(fig)
    xs = np.nonzero(fig[..., 3].any(0))[0]
    return fig[:, xs.min():xs.max() + 1].copy()


def trousers(fig, rows):
    """The mantle's violet in the lowest `rows` rows becomes the trousers' shades (TROUSERS)."""
    out = fig.copy()
    for y in range(max(0, fig.shape[0] - rows), fig.shape[0]):
        for x in range(fig.shape[1]):
            h = hexs(fig[y, x]) if fig[y, x, 3] else None
            if h in TROUSERS:
                c = TROUSERS[h]
                out[y, x] = (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)
    return out


def seg(p, a, b):
    """(distance from p to segment a-b, position along it, side: + to the right of a->b going down)."""
    vx, vy = b[0] - a[0], b[1] - a[1]
    n = float(np.hypot(vx, vy)) or 1e-9
    s = max(0.0, min(n, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / n))
    qx, qy = a[0] + vx / n * s, a[1] + vy / n * s
    return float(np.hypot(p[0] - qx, p[1] - qy)), s, (p[0] - qx) * (vy / n) - (p[1] - qy) * (vx / n)


def ik(hip, ankle, l1=RUN_THIGH, l2=RUN_SHIN):
    """The knee of a two-bone leg from hip to ankle, bent forward (+x); the ankle drawn in if out of reach."""
    dx, dy = ankle[0] - hip[0], ankle[1] - hip[1]
    d = float(np.hypot(dx, dy))
    if d >= l1 + l2 - 1e-6:
        k = (l1 + l2 - 1e-6) / d
        ankle = (hip[0] + dx * k, hip[1] + dy * k)
        dx, dy, d = dx * k, dy * k, l1 + l2 - 1e-6
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = float(np.sqrt(max(0.0, l1 * l1 - a * a)))
    nx, ny = -dy / d, dx / d
    if nx < 0:
        nx, ny = -nx, -ny
    return (hip[0] + dx * a / d + nx * h, hip[1] + dy * a / d + ny * h), ankle


def rgba(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255), np.uint8)


def shoe():
    """The design's far shoe (curled to the right) as {(dx, dy) from its ankle: colour}, its outline left to leg()."""
    a = K.design_1x()
    x0, y0, x1, y1 = SHOE
    out = {}
    for y in range(y0, y1):
        for x in range(x0, x1):
            if a[y, x, 3] and hexs(a[y, x]) not in TROUSERS_ALL and hexs(a[y, x]) != "050302":
                out[(x - int(SHOE_ANKLE[0]), y - SHOE_ANKLE[1])] = a[y, x].copy()
    return out


TROUSERS_ALL = {"9FA8C3", "B2B9D2", "C4C9DB", "DCDFE8"}


def leg(hip, knee, ankle, shades, foot):
    """{(x, y): colour} of one leg: the thigh and the shin in the trousers' shades (lit on the front, dark behind,
    the gold stripe down the middle), the shoe at the ankle, one outline ring (nothing under the ankle's shoe line)."""
    lit, mid, dark, gold = shades
    cells = {}
    xs, ys = [hip[0], knee[0], ankle[0]], [hip[1], knee[1], ankle[1]]
    for y in range(int(min(ys)) - 3, int(max(ys)) + 3):
        for x in range(int(min(xs)) - 4, int(max(xs)) + 5):
            p = (x + 0.5, y + 0.5)
            d1, s1, side1 = seg(p, hip, knee)
            d2, s2, side2 = seg(p, knee, ankle)
            if d1 <= RUN_W[0] and (d1 <= d2 or s1 < RUN_THIGH * 0.6):
                side = side1
            elif d2 <= RUN_W[1] and p[1] < ankle[1] + 0.5:
                side = side2
            else:
                continue
            cells[(x, y)] = rgba(gold if abs(side - 0.4) < 0.5 else lit if side > 0.9 else dark if side < -0.9 else mid)
    ax, ay = int(round(ankle[0] - 0.5)), int(round(ankle[1]))
    for (dx, dy), c in foot.items():
        cells[(ax + dx, ay + dy)] = c
    ring = {}
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                ring[q] = rgba("050302")
    ring.update(cells)
    return ring


def run_legs(c, k):
    """Run frame k with Codex's legs under the belt replaced by two drawn legs (see RUN_THIGH)."""
    c = c.copy()
    H, W = c.shape[:2]
    top = mid = None
    for y in range(44, 60):
        xs = [x for x in range(36, 57) if c[y, x, 3] and hexs(c[y, x]) in TROUSERS_ALL]
        if len(xs) >= 3:
            top, mid = y, (min(xs) + max(xs) + 1) / 2
            break
    # Codex's legs go: under the belt, round the trousers' middle, all but the coat (and the coat's gold beside it)
    x0, x1 = int(mid) - 20, int(mid) + 12
    for y in range(top, H):
        for x in range(W) if y > FEET - RUN_COAT else range(max(0, x0), min(W, x1)):
            if not c[y, x, 3]:
                continue
            h = hexs(c[y, x])
            coat = h in COAT or (h not in TROUSERS_ALL and h != "050302" and any(
                c[y + dy, x + dx, 3] and hexs(c[y + dy, x + dx]) in COAT
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= y + dy < H and 0 <= x + dx < W))
            if not coat or y > FEET - RUN_COAT:
                c[y, x] = 0
    # what Codex shaded its back leg with reads as the coat's plum too: under the belt only the coat's mass stays (a
    # square with at least 3 of its 8 neighbours drawn in it), the leg's thin strips go
    for _ in range(2):
        keep = c.copy()
        for y in range(top + 1, H):
            for x in range(1, W - 1):
                if c[y, x, 3] and hexs(c[y, x]) != "050302":
                    n = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and c[y + dy, x + dx, 3]
                            and hexs(c[y + dy, x + dx]) != "050302")
                    if n < 3:
                        keep[y, x] = 0
        c = keep
    c = orphans(c)
    foot = shoe()
    hip_y = top + 0.5
    ankle_y = FEET - 4 + 0.0                 # the shoe's top row: 4 rows over the soles' row
    legs = {}
    for side, ph, dx in (("near", k % 8, -RUN_HIP_GAP), ("far", (k + 4) % 8, RUN_HIP_GAP)):
        fx, lift = RUN_FOOT[ph]
        hip = (mid + dx, hip_y)
        knee, ankle = ik(hip, (hip[0] + fx, ankle_y - lift))
        legs[side] = leg(hip, knee, ankle, RUN_SHADES[side], foot)
    for (x, y), col in legs["far"].items():
        if 0 <= y <= FEET and 0 <= x < W and not c[y, x, 3]:
            c[y, x] = col
    for (x, y), col in legs["near"].items():
        if top <= y <= FEET and 0 <= x < W:
            c[y, x] = col
    c = pieces(c)
    c, _, _ = G.complete_outline(c, feet=FEET)
    return c


def head_sprite():
    a = K.design_1x()
    m = K.head_mask(a)
    ys, xs = np.nonzero(m)
    y0, x0 = ys.min(), xs.min()
    h = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1, 4), np.uint8)
    h[ys - y0, xs - x0] = a[ys, xs]
    return h


def classes(img):
    out = np.zeros(img.shape[:2], np.int8)
    for y, x in zip(*np.nonzero(img[..., 3])):
        h = hexs(img[y, x])
        out[y, x] = 1 if h in HAIR else 2 if h in SKIN else 3
    return out


def grow(m, n):
    for _ in range(n):
        g = m.copy()
        g[1:] |= m[:-1]
        g[:-1] |= m[1:]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    return m


def find_head(fig, head):
    """(share, x, y): where the design head's hair and skin squares agree most with the frame's."""
    pad = 6
    big = np.zeros((fig.shape[0] + 2 * pad, fig.shape[1] + 2 * pad, 4), np.uint8)
    big[pad:-pad, pad:-pad] = fig
    hm = head[..., 3] > 0
    hc = classes(head)
    key = hm & (hc < 3)
    cc = classes(big)
    hh, hw = head.shape[:2]
    best = (0.0, 0, 0)
    for y in range(0, big.shape[0] - hh + 1):
        for x in range(0, big.shape[1] - hw + 1):
            s = ((cc[y:y + hh, x:x + hw] == hc) & key).sum() / key.sum()
            if s > best[0]:
                best = (s, x - pad, y - pad)
    return best


def paste_head(fig, head, x, y):
    """The design head at (x, y) on the frame (which grows to hold it): the frame's own hair and eyes within 2 squares
    of it go first, and its skin on the face's side (behind the head it is an arm raised beside it); the design has no
    hair falling behind the head, so Codex's bigger mane goes too, and so do the crumbs of its ears beside the head.
    Then the outline left round nothing goes, small pockets are filled and the outline is closed."""
    hh, hw = head.shape[:2]
    top, left = max(0, -y), max(0, -x)
    H = max(fig.shape[0] + top, y + top + hh)
    W = max(fig.shape[1] + left, x + left + hw)
    out = np.zeros((H, W, 4), np.uint8)
    out[top:top + fig.shape[0], left:left + fig.shape[1]] = fig
    x, y = x + left, y + top
    m = head[..., 3] > 0
    placed = np.zeros((H, W), bool)
    placed[y:y + hh, x:x + hw] = m
    near = grow(placed, 2)
    near[y + hh - 1:] = False
    face_side = x + hw // 2
    for yy, xx in zip(*np.nonzero(near & (out[..., 3] > 0))):
        h = hexs(out[yy, xx])
        if h in HAIR or h in EYES or (h in SKIN and xx >= face_side):
            out[yy, xx] = 0
    out = crumbs(out, placed, near)
    out[y:y + hh, x:x + hw][m] = head[m]
    out = orphans(out)
    out = fill_holes(out)
    out, _, _ = G.complete_outline(out, feet=H - 1)
    return pieces(out), (x, y), (left, top)


def crumbs(a, placed, near, limit=10):
    """Pieces of fewer than `limit` squares beside the head once the head is left out (8-connected): what is left of
    Codex's own ears and their dark outline. A fist raised by the head is part of its arm and stays."""
    a = a.copy()
    m = (a[..., 3] > 0) & ~placed
    H, W = m.shape
    seen = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(m & near)):
        if seen[y, x]:
            continue
        st, pts = [(y, x)], []
        seen[y, x] = True
        while st and len(pts) <= limit:
            cy, cx = st.pop()
            pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        st.append((ny, nx))
        if len(pts) < limit and not st:
            for cy, cx in pts:
                a[cy, cx] = 0
    return a


def orphans(a):
    """Outline squares with nothing drawn beside them (8 ways) go: the outline of Codex's own ears and hair, left
    standing once their colour is cleared."""
    a = a.copy()
    H, W = a.shape[:2]
    for _ in range(3):
        op = a[..., 3] > 0
        drawn = op & ~np.all(a[..., :3] == OUTLINE, -1)
        near = np.zeros((H, W), bool)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                s = np.zeros((H, W), bool)
                s[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = \
                    drawn[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
                near |= s
        gone = op & ~drawn & ~near
        if not gone.any():
            break
        a[gone] = 0
    return a


def fill_holes(a, limit=6):
    """Clear pockets of up to `limit` squares walled in by the figure take the commonest colour round them that is not
    the outline (a cleared strand of hair between the pasted head and the mantle)."""
    from collections import Counter
    a = a.copy()
    op = a[..., 3] > 0
    H, W = op.shape
    outside = np.zeros((H, W), bool)
    st = [(y, x) for y in range(H) for x in (0, W - 1) if not op[y, x]] + \
         [(y, x) for x in range(W) for y in (0, H - 1) if not op[y, x]]
    for y, x in st:
        outside[y, x] = True
    while st:
        y, x = st.pop()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                st.append((ny, nx))
    hole = ~op & ~outside
    seen = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(hole)):
        if seen[y, x]:
            continue
        pts, st = [], [(y, x)]
        seen[y, x] = True
        while st:
            cy, cx = st.pop()
            pts.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if hole[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    st.append((ny, nx))
        if len(pts) > limit:
            continue
        ps = set(pts)
        nb = Counter(tuple(int(v) for v in a[qy, qx]) for cy, cx in pts
                     for qy, qx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1))
                     if (qy, qx) not in ps and a[qy, qx, 3] and tuple(int(v) for v in a[qy, qx, :3]) != OUTLINE)
        if nb:
            col = np.array(nb.most_common(1)[0][0], np.uint8)
            for cy, cx in pts:
                a[cy, cx] = col
    return a


def pieces(c, limit=8):
    """Pieces of fewer than `limit` squares apart from the body go."""
    m = c[..., 3] > 0
    seen = np.zeros(m.shape, bool)
    found = []
    for y, x in zip(*np.nonzero(m)):
        if seen[y, x]:
            continue
        st, pts = [(y, x)], []
        seen[y, x] = True
        while st:
            cy, cx = st.pop()
            pts.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    st.append((ny, nx))
        found.append(pts)
    found.sort(key=len, reverse=True)
    out = c.copy()
    for p in found[1:]:
        if len(p) < limit:
            for y, x in p:
                out[y, x] = 0
    return out


def own_head_at(fig, head):
    """Where a fallen frame's own head is, for placing it: its hair's middle as the head box's middle."""
    ys, xs = np.nonzero(classes(fig) == 1)
    return int(round(xs.mean() - head.shape[1] / 2)), int(round(ys.mean() - head.shape[0] / 2))


def build(cells, src=SRC):
    head = head_sprite()
    CW, CH = cells["cell"]
    sheets, report = {}, {}
    idle = K.design_1x()
    sheets["idle"] = []
    for f in cells["tags"]["idle"]:
        c = np.zeros((CH, CW, 4), np.uint8)
        ox, oy = f["pivot"][0] - DESIGN_PIVOT[0], f["pivot"][1] - DESIGN_PIVOT[1]
        ys, xs = np.nonzero(idle[..., 3])
        c[ys + oy, xs + ox] = idle[ys, xs]
        sheets["idle"].append(c)
    for tag in TAGS:
        table = cells["tags"][tag]
        a = np.asarray(Image.open(os.path.join(src, f"sett_{tag}_raw.png")).convert("RGBA"))
        frames = raw_frames(a, len(table))
        px = block_size(tag, frames)
        ground = {}
        for f, row in frames:
            ground[row] = max(ground.get(row, 0), extent(f)[1])
        out, rep = [], []
        for k, ((f, row), ref) in enumerate(zip(frames, table)):
            bottom = extent(f)[1]
            lift = int(round((ground[row] - bottom) / px)) if tag in FLIGHT else 0
            fig = read(f, px, bottom)
            if tag in LEG_VIOLET:
                fig = trousers(fig, LEG_VIOLET[tag])
            if (tag, k) in OWN_HEAD:
                hx, hy = own_head_at(fig, head)
                share = None
            else:
                share, x, y = find_head(fig, head)
                fig, (hx, hy), _ = paste_head(fig, head, x, y)
            lx, ly = ref["head"]
            if (tag, k) in HEAD_FROM:
                other, dx = HEAD_FROM[(tag, k)]
                lx = table[other]["head"][0] + dx
            ox = int(round(lx + HEAD_AT[0])) - hx
            if tag in HANG:
                oy = FEET - HOVER[tag] - (fig.shape[0] - 1)
            else:
                lift = min(lift, FEET - (fig.shape[0] - 1) - TOP)
                oy = FEET - lift - (fig.shape[0] - 1)
            c = np.zeros((CH, CW, 4), np.uint8)
            ys, xs = np.nonzero(fig[..., 3])
            ok = (ys + oy >= 0) & (ys + oy < CH) & (xs + ox >= 0) & (xs + ox < CW)
            c[ys[ok] + oy, xs[ok] + ox] = fig[ys[ok], xs[ok]]
            if tag == "run":
                c = run_legs(c, k)
            out.append(c)
            rep.append((None if share is None else round(share, 2), fig.shape[1], fig.shape[0], lift,
                        int((fig[..., 3] > 0).sum()), int((~ok).sum())))
        sheets[tag] = out
        report[tag] = (round(px, 2), rep)
    return sheets, report


def strip(frames):
    CH, CW = frames[0].shape[:2]
    cols, rows = layout(len(frames))
    out = np.zeros((rows * CH, cols * CW, 4), np.uint8)
    for k, c in enumerate(frames):
        r, cc = divmod(k, cols)
        out[r * CH:(r + 1) * CH, cc * CW:(cc + 1) * CW] = c
    return np.repeat(np.repeat(out, 8, 0), 8, 1)


def review(sheets, cells, path, z=4):
    """Every frame at z x round its pivot: the feet line red, the pivot column blue."""
    rows = []
    for tag, frames in sheets.items():
        tiles = []
        for k, c in enumerate(frames):
            px, py = cells["tags"][tag][k]["pivot"]
            sub = c[py - 50:py + 13, max(0, px - 30):px + 31]
            im = Image.fromarray(sub).resize((sub.shape[1] * z, sub.shape[0] * z), Image.NEAREST)
            bg = Image.new("RGBA", (im.width, im.height + 16), (96, 104, 88, 255))
            d = ImageDraw.Draw(bg)
            gy = 16 + (FEET - (py - 50) + 1) * z
            d.line((0, gy, im.width, gy), fill=(220, 60, 60, 255))
            d.line((30 * z, 16, 30 * z, bg.height), fill=(70, 110, 230, 255))
            bg.alpha_composite(im, (0, 16))
            d.text((3, 2), f"{tag} {k + 1}", fill=(255, 255, 255, 255))
            tiles.append(bg)
        rows.append(tiles)
    W = max(sum(t.width + 6 for t in r) for r in rows)
    H = sum(max(t.height for t in r) + 6 for r in rows)
    out = Image.new("RGB", (W, H), (40, 40, 40))
    y = 0
    for r in rows:
        x = 0
        for t in r:
            out.paste(t.convert("RGB"), (x, y))
            x += t.width + 6
        y += max(t.height for t in r) + 6
    out.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder (raw/sett_<tag>_raw.png, sett_cells.json, HANDOFF.md)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--review")
    a = ap.parse_args()
    if a.raw:
        os.makedirs(SRC, exist_ok=True)
        for tag in TAGS:
            img = Image.open(os.path.join(a.raw, "raw", f"sett_{tag}_raw.png"))
            to_indexed(snap(img)).save(os.path.join(SRC, f"sett_{tag}_raw.png"), optimize=True)
        for name in ("sett_cells.json", "HANDOFF.md", "generation_prompts.json"):
            shutil.copy(os.path.join(a.raw, name), os.path.join(SRC, name))
    with open(CELLS, encoding="utf-8") as f:
        cells = json.load(f)
    sheets, report = build(cells)
    for tag, frames in sheets.items():
        Image.fromarray(strip(frames)).save(os.path.join(a.out, f"sett_{tag}.png"))
    text = '{"cell": [%d, %d], "scale": 8, "tags": {\n' % tuple(cells["cell"]) + ",\n".join(
        f'  "{tag}": [' + ", ".join(f'{{"pivot": [{f["pivot"][0]}, {f["pivot"][1]}], "ms": {f["ms"]}}}'
                                    for f in cells["tags"][tag]) + "]" for tag in sheets) + "\n}}\n"
    with open(os.path.join(a.out, "sett_cells.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    for tag, (px, rep) in report.items():
        print(f"{tag:9s} block {px:5.2f}: " + "  ".join(
            f"{k + 1}: head {s} {w}x{h} lift {l} {n}px" + (f" CUT {cut}" if cut else "")
            for k, (s, w, h, l, n, cut) in enumerate(rep)))
    if a.review:
        review(sheets, cells, a.review)


if __name__ == "__main__":
    main()
