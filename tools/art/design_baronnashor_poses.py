#!/usr/bin/env python3
"""Baron Nashor's Codex poses (assets/source/baronnashor/codex_poses: POSE_PROMPTS.md, 19 poses - its body on its own TFT
clips, its legs on T-Hex's - on its design, 2026-11-03), on the spider legs since 2026-11-08 (codex_legs2), at the
design's body size, on the design's palette, gaps closed, the design's face on each.

    python tools/art/design_baronnashor_poses.py --sheet DIR      # all poses beside the design (4x), pivots marked
    python tools/art/design_baronnashor_poses.py                  # writes assets/source/baronnashor/hd/pose_<name>.png (+ .json)

Codex was asked the design at 9 px a square and drew each pose on its own squares at its own size (run7 and run8 a good
deal bigger, run6 smaller). BODY[name] raw px is the design's square: the square root of the pose's blue head pixels
(its biggest sky-blue piece) over the design's, averaged with the same for the whole figure's area (the head alone
shrinks when it turns; the area alone grows when it rears or spreads its claws), or BODY_DEFAULT where the head is out
(under the ground). The run is the redrawn one (assets/source/baronnashor/codex_run, RUN_PROMPTS.md: the first run's
legs never swapped - T-Hex's run at this camera keeps one foot ahead): one body for all eight, their median height at
RUN_ROWS (the idle's size, so starting to run does not jump; Codex kept one upper body, so the head never changes size).

The spider legs (2026-11-07 the user: 「大龙的腿应该是这样的」, TFT's Baron on six thin legs; L6 picked, the idle is L6:
design_baronnashor_model.py): Codex put L6's legs on every pose and run frame but e_dig (assets/source/baronnashor/
codex_legs2, LEGS2_PROMPT.md: its composites keep the old drawings' pixels outside its edit masks, checked pixel for
pixel). The body is the old drawing, so everything about it is measured on the old drawing (OLD_SRC, OLD_RUN_SRC): its
scale (against A-1, the idle before the legs, whose body L6 keeps), the phase its squares are read on (cells laid from
its leftmost pixel and its soles, as before: the body reads square for square as it did, the cells only run on as far
as the new legs reach) and its pivot (between the old two feet: the body stands where it stood). Where the mask cut the
old thighs away and left the old body's colour against the ground (seal_cuts), that square takes the outline.

Each drawing (the top-level PNGs) is read on squares of BODY px (raw_read: the commonest design colour round each
square's centre), the one-square cracks and small holes closed (design_silco_poses.close_gaps), loose specks dropped,
and the design's own face (the blue head and its yellow eyes, FACE_ROWS x FACE_COLS of hd/idle.png; the mouth left out,
it opens and shuts with the pose) pasted where it matches best (the user's rule: one face in every frame), only where
at least FACE_MIN of its squares already match and its blue lands on the pose's own head.
Each pose's json keeps its pivot (the point between its feet, on the ground): the old drawing's, between its two feet
(feet_mid: the two biggest pieces in its lowest rows, the design's own DESIGN_PIVOT likewise on A-1), so the body rears
or lunges over the same point; the run frames take the design's pivot carried by where the face landed (the head runs
steady, the legs step under it); PIVOT[name] where neither tells (under the ground, lying). The ground is the figure's
lowest row.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pack_baronnashor_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_baronnashor_hd import lp  # noqa: E402
from design_baronnashor_model import L6_LEFT  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
from design_sohm_poses import lab  # noqa: E402

BN = os.path.join(ROOT, "assets", "source", "baronnashor")
SRC = os.path.join(BN, "codex_legs2", "baronnashor-legs2")              # the poses and the run on the spider legs
MASKS = os.path.join(SRC, "edit-masks")                                 # white: the squares Codex redrew
OLD_SRC = os.path.join(BN, "codex_poses", "baronnashor-poses")          # the drawings before the legs changed
OLD_RUN_SRC = os.path.join(BN, "codex_run", "baronnashor-run")
OUT = os.path.join(BN, "hd")
SPECK = 6
# the face (the user's rule: the idle's face in every frame): the blue head and its yellow eyes - rows / columns of
# hd/idle.png (the mouth left out: it opens and shuts with the pose); A-1's columns 24-47, L6_LEFT on in L6
FACE_ROWS, FACE_COLS = (18, 35), (24 + L6_LEFT, 47 + L6_LEFT)
FACE_MIN = 0.4
NO_FACE = {"d_down", "e_dig"}  # lying with its eyes gone dark (Codex's own); under the ground
NO_LEGS = {"e_dig"}            # under the ground: its old drawing as it was
DARK_EYE = set()
BODY_DEFAULT = 11.0
RUNS = tuple(f"run{i}" for i in range(1, 9))
# a run frame taller than RUN_TOP rows loses the extra rows from its shins (evenly spaced rows of the band LEG_BAND rows
# above its soles), so the head bobs at most RUN_TOP - 94 rows (the redrawn run5 put its planted foot 4 rows under the
# others': its head hopped up at one crossing of the two)
RUN_TOP = 96
RUN_ROWS = 95                 # a run frame's height: the idle's 94 rows and one for the stride
LEG_BAND = (30, 6)
WIN = 5                       # raw pixels round each design square's centre that vote
BODY = {}                     # filled by body_of() from the old raws (head + area), printed with every read
# where neither tells: lying, its head foreshortened and dark (head alone 6.1) and its whole length on show (area alone
# 9.4) - the other poses' measure is ~0.93 of their area's, and Codex's squares there (8 px) are 0.84 of d_fall's (9.5)
BODY_FIX = {"d_down": 8.9}
DARK = 90                     # a colour this dark (r + g + b) is outline


def blue(px):
    """The sky blue of its head (and the two small heads)."""
    r, b = px[..., 0].astype(int), px[..., 2].astype(int)
    return (b > 150) & (r < 120) & (b - r > 90)


def visor_px(a):
    """The biggest blue piece: its head."""
    m = blue(a) & (a[..., 3] >= 128)
    lb, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    return int(ndimage.sum(m, lb, range(1, n + 1)).max()) if n else 0


def png(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def old_raw(name):
    """Codex's drawing before the spider legs (the redrawn run: pack_baronnashor_run.py, the legs taking turns)."""
    if name in RUNS:
        return png(os.path.join(OLD_RUN_SRC, f"baronnashor-run-{name}.png"))
    return png(os.path.join(OLD_SRC, f"baronnashor-pose-{name}.png"))


def raw(name):
    """The drawing read: on the spider legs (codex_legs2), e_dig as it was."""
    if name in NO_LEGS:
        return old_raw(name)
    return png(os.path.join(SRC, f"baronnashor-legs2-{name}.png"))


def mask(name):
    """Codex's edit mask (True: redrawn), none for e_dig."""
    if name in NO_LEGS:
        return None
    return np.asarray(Image.open(lp(os.path.join(MASKS, f"baronnashor-legs2-{name}.png"))).convert("L")) > 127


def body_one(name):
    """Measured on the old drawing against A-1 (the idle it was drawn on; L6 keeps A-1's body, but its legs would
    count in the area)."""
    d = design("A-1.png")
    a = old_raw(name)
    op = a[..., 3] >= 128
    area = np.sqrt(op.sum() / (d[..., 3] > 0).sum())
    v = visor_px(a)
    if v < 500:   # no head to measure (under the ground)
        return BODY_DEFAULT
    return round((np.sqrt(v / visor_px(d)) + area) / 2, 2)


def body_of(name):
    """The raw px a design square takes in this pose: the head's scale and the area's, averaged; the run's by height, one
    for all eight (the redrawn run, assets/source/baronnashor/codex_run: Codex kept one upper body, its tops on the same
    row; only the feet differ - so the median height at RUN_ROWS, the idle's size, the head the same in every frame)."""
    if name not in BODY:
        if name in BODY_FIX:
            BODY[name] = BODY_FIX[name]
        elif name in RUNS:   # one body for all eight: their median height (crest tips to soles) at RUN_ROWS
            hs = []
            for n in RUNS:
                ys = np.nonzero((old_raw(n)[..., 3] >= 128).any(1))[0]
                hs.append(ys.max() + 1 - ys.min())
            BODY.update({n: round(float(np.median(hs)) / RUN_ROWS, 2) for n in RUNS})
        else:
            BODY[name] = body_one(name)
    return BODY[name]


FOOT_ROWS = 8                 # the lowest rows the feet are read in
FOOT_GAP = 4                  # columns between the claws of one foot
# name -> pivot column in the read pose where its feet do not tell (filled once the poses are read)
PIVOT = {}


def feet_mid(g):
    """Between its feet: the middle of the two widest runs of columns in its lowest FOOT_ROWS rows (its two clawed
    feet; claws FOOT_GAP columns apart count as one foot)."""
    cols = (g[-FOOT_ROWS:, :, 3] > 0).any(0)
    runs, x = [], 0
    while x < len(cols):
        if cols[x]:
            x0 = x
            while x < len(cols) and (cols[x] or cols[x:x + FOOT_GAP + 1].any()):
                x += 1
            runs.append((x0, x))
        x += 1
    if len(runs) < 2:
        return None
    two = sorted(runs, key=lambda r: r[1] - r[0])[-2:]
    return int(round(np.mean([(r[0] + r[1] - 1) / 2 for r in two])))


def dark_eye(g, d):
    """The eye gone out: the red rim and the white inside its box take the design's darkest two navy greys."""
    r, gr, b = (g[..., k].astype(int) for k in range(3))
    red = (r > 170) & (gr < 90) & (b < 90) & (g[..., 3] > 0)
    if not red.any():
        return g
    ys, xs = np.nonzero(red)
    out = g.copy()
    op = d[..., 3] > 0
    cols = np.unique(d[op][:, :3], axis=0)
    navy = cols[(cols[:, 2] > cols[:, 0]) & (cols.sum(1) < 260)]
    navy = navy[np.argsort(navy.sum(1))]
    box = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    sub = out[box]
    sr, sg, sb = (sub[..., k].astype(int) for k in range(3))
    sub[(sr > 170) & (sg < 90) & (sb < 90)] = list(navy[0]) + [255]
    sub[(sr > 200) & (sg > 200) & (sb > 200)] = list(navy[min(1, len(navy) - 1)]) + [255]
    return out


def put_face(g, d):
    """The design's face pasted where most of its squares already match (in Lab, within a few steps) AND its blue
    lands on the pose's own blue head (at least half its blue squares) -> (pose, offset, match share)."""
    (r0, r1), (c0, c1) = FACE_ROWS, FACE_COLS
    patch = d[r0:r1, c0:c1]
    pm = patch[..., 3] > 0
    ph, pw = patch.shape[:2]
    vis = blue(patch) & pm
    lab_g, lab_p = lab(g), lab(patch)
    best = (-1, 0, 0)
    for y in range(0, g.shape[0] - ph + 1):
        for x in range(0, g.shape[1] - pw + 1):
            win = g[y:y + ph, x:x + pw]
            if (blue(win) & vis).sum() * 2 < vis.sum():
                continue
            both = pm & (win[..., 3] > 0)
            dist = ((lab_g[y:y + ph, x:x + pw] - lab_p) ** 2).sum(-1)
            score = int((both & (dist < 400)).sum())
            if score > best[0]:
                best = (score, x, y)
    score, x, y = best
    if score < FACE_MIN * pm.sum():   # the head turned: Codex's own face stays
        return g, None, max(score, 0) / pm.sum()
    out = g.copy()
    win = out[y:y + ph, x:x + pw]
    put = pm & (win[..., 3] > 0)
    win[put] = patch[put]
    return out, (x - c0, y - r0), score / pm.sum()


NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


DESIGN_PIVOT = feet_mid(design("A-1.png")) + L6_LEFT   # between A-1's two feet: the body stands where it stood


def raw_read(name, old=False):
    """Codex's drawing at the design's body, on the design's palette -> (figure, its own square size, where its
    top-left square is on the old drawing's cells (column from the old leftmost, row up from the old soles), the
    cells inside Codex's edit mask).
    Every design square takes the commonest design colour among the raw pixels round its centre (WIN x WIN, each
    snapped to the design's palette in Lab). The cells are the old drawing's (laid from its leftmost pixel and up from
    its soles), on both sides as far as this drawing goes."""
    d = design()
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    a = old_raw(name) if old else raw(name)
    m = None if old else mask(name)
    o = old_raw(name)[..., 3] >= 128
    oys, oxs = np.nonzero(o)
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    sq = RG.square_size(RG.profile(a, op, 1), xs.min(), xs.max())
    body = body_of(name)
    x0, y1 = oxs.min(), oys.max() + 1
    k0, k1 = int(np.floor((xs.min() - x0) / body)), int(np.ceil((xs.max() + 1 - x0) / body))
    j0, j1 = int(np.floor((y1 - ys.max() - 1) / body)), int(np.ceil((y1 - ys.min()) / body))
    cx = x0 + (np.arange(k0, k1) + 0.5) * body
    cy = y1 - (np.arange(j1 - 1, j0 - 1, -1) + 0.5) * body
    r = WIN // 2
    out = np.zeros((len(cy), len(cx), 4), np.uint8)
    cut = np.zeros((len(cy), len(cx)), bool)
    lab_p = PD._lab(pal.astype(float))
    for j, y in enumerate(cy):
        for i, x in enumerate(cx):
            yi, xi = int(y), int(x)
            box = (slice(max(0, yi - r), yi + r + 1), slice(max(0, xi - r), xi + r + 1))
            if m is not None:
                cut[j, i] = m[box].mean() >= 0.5
            win = a[box].reshape(-1, 4)
            on = win[win[:, 3] >= 128]
            if len(on) * 2 < len(win):
                continue
            lab_w = PD._lab(on[:, :3].astype(float))
            idx = np.argmin(((lab_w[:, None, :] - lab_p[None]) ** 2).sum(-1), axis=1)
            out[j, i, :3] = pal[np.bincount(idx).argmax()]
            out[j, i, 3] = 255
    return out, sq, (k0, j1 - 1), cut


OLD = {}


def old_read(name):
    """The old drawing read (close_gaps'd) on its own cells -> (figure, where its top-left square is)."""
    if name not in OLD:
        g, _, at, _ = raw_read(name, old=True)
        OLD[name] = close_gaps(g, design()), at
    return OLD[name]


SLIT = 2                      # a clear run this short between two opaque squares, where the old body was, is closed


def slits(gone, op):
    """The squares of `gone` in a clear run of at most SLIT squares (across or up and down) with opaque squares at
    both ends: the slits the cut leaves between the old body and a new leg."""
    out = np.zeros_like(gone)
    for t, (gn, o, res) in enumerate(((gone, op, out), (gone.T, op.T, out.T))):
        for r in range(o.shape[0]):
            row, x = o[r], 0
            while x < len(row):
                if row[x]:
                    x += 1
                    continue
                x0 = x
                while x < len(row) and not row[x]:
                    x += 1
                if 0 < x0 and x < len(row) and x - x0 <= SLIT and gn[r, x0:x].any():
                    res[r, x0:x] = True
    return out & ~op


def seal_cuts(name, g, at, cut, d):
    """Where Codex's mask took the old body away and left the ground (a square the old drawing had, clear now): the
    slits it leaves (slits) are closed and the old body's light squares beside it take the design's outline colour, the
    cut edge outlined like the rest of the figure."""
    if cut is None:
        return g, 0
    og, oat = old_read(name)
    was = np.zeros(g.shape[:2], bool)
    ys, xs = np.nonzero(og[..., 3] > 0)
    ty, tx = ys + at[1] - oat[1], xs + oat[0] - at[0]
    ok = (ty >= 0) & (ty < g.shape[0]) & (tx >= 0) & (tx < g.shape[1])
    was[ty[ok], tx[ok]] = True
    ink = tuple(PD.edge_colour(d))[:3] + (255,)
    out = g.copy()
    op = out[..., 3] > 0
    shut = slits(was & ~op, op)
    out[shut] = ink
    op = out[..., 3] > 0
    gone = was & ~op
    light = op & (out[..., :3].astype(int).sum(-1) > DARK)
    seal = light & ~cut & ndimage.binary_dilation(gone, structure=ndimage.generate_binary_structure(2, 1))
    out[seal] = ink
    return out, int(seal.sum() + shut.sum())


def drop_specks(g):
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    out = g.copy()
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            out[lb == j] = 0
    return out


def old_feet(name):
    """Between the old drawing's two feet, as a column of its cells (column 0: its leftmost)."""
    g = drop_specks(old_read(name)[0])
    ys, xs = np.nonzero(g[..., 3] > 0)
    f = feet_mid(g[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return None if f is None else f + xs.min()


def shorter_shins(g, k):
    """k rows dropped from the band LEG_BAND rows above the soles (evenly spaced): the body comes down k rows onto
    the same feet."""
    h = g.shape[0]
    top, bot = h - LEG_BAND[0], h - LEG_BAND[1]
    drop = set(np.round(np.linspace(top, bot - 1, k + 2)[1:-1]).astype(int))
    return g[[r for r in range(h) if r not in drop]]


def pivot_of(name, g, face, left):
    """The run: the design's pivot carried by the face (the head runs steady, the legs step under it); the rest:
    PIVOT[name], else between the old drawing's two feet (`left`: the cut figure's first column on the old drawing's
    cells), else between its own feet, else the figure's middle."""
    h, w = g.shape[:2]
    if name in RUNS and face is not None:
        return int(round(DESIGN_PIVOT + face[0])), h
    if name in PIVOT:
        return PIVOT[name], h
    f = old_feet(name)
    if f is not None:
        return int(f - left), h
    f = feet_mid(g)
    return (w // 2 if f is None else f), h


def read(name):
    d = design()
    g, sq, at, cut = raw_read(name)
    g = close_gaps(g, d)
    g, sealed = seal_cuts(name, g, at, cut, d)
    if name in DARK_EYE:
        g = dark_eye(g, d)
    if name in NO_FACE:
        off, share = None, 0.0
    else:
        g, off, share = put_face(g, d)
    g = drop_specks(g)
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (int(off[0] - xs.min()), int(off[1] - ys.min()))
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if name in RUNS and g.shape[0] > RUN_TOP:
        g = shorter_shins(g, g.shape[0] - RUN_TOP)
    piv = pivot_of(name, g, face, at[0] + xs.min())
    print(f"{name:9s} squares {sq:.1f} px -> body {body_of(name)}: {g.shape[1]}x{g.shape[0]}, face "
          f"{face}, {share:.0%} matched, {sealed} cut squares sealed, pivot {piv}")
    return g, piv, face


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    figs = {n: read(n) for n in names}
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 5] for i in range(0, len(tiles), 5)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                px = DESIGN_PIVOT if n == "design" else figs[n][1][0]
                dr.line([(x + px * z, 24 + (Hm - t.shape[0]) * z), (x + px * z, 24 + Hm * z)], fill=(255, 0, 0, 255))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"baronnashor_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, piv, face) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "face": None if face is None else [face[0], face[1]]}, fh)


if __name__ == "__main__":
    main()
