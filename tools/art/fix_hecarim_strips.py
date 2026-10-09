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


def build(design, pal, tag, report):
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
        v2 = v2_frame(tag, i + 1, pal, c)
        frame_key[1] = v2 is not None
        if v2 is not None:
            c = K.finish(bridge(v2), design.outline, SOLES)
        at = None
        # round 2's helms are drawn like the design's (small, the horn, the eye squares) and move with each pose; a
        # pasted design head sat on the raised hands in attack 2-3 - they keep their own unless HEAD_AT names one
        if (tag, i + 1) not in KEEP_HEAD and (v2 is None or (tag, i + 1) in HEAD_AT):
            at = HEAD_AT.get((tag, i + 1)) or head_place(design, c, lol_head(tag, i))
            frame_key[0] = (tag, i + 1)
            c = with_head(design, c, at)
        report.append((tag, i + 1, round(s, 4), round(med, 4), g.shape, int(bottom), at))
        out.append(c)
    return out, ms


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
