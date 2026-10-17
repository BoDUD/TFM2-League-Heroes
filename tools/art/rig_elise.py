#!/usr/bin/env python3
"""league_elise's frames: the imported strips (tools/art/import_elise_strips.py -> assets/source/elise/frames) and the
designs -> the dense strips at PPU 1.8 and the 1x sheet.

    python tools/art/rig_elise.py [--review DIR]

league_jayce's way (tools/art/rig_jayce.py), the user's density (2026-10-15: PPU 1.5, then 1.8 for a readable face):
  * the frames are on the design's grid (100 squares crown to toes = 38 game rows: NATIVE squares a game pixel) and
    brought to PPU 1.8 here (pixel_down.pixelate on a grid through the pivot, the design's 40 colours), so
    ppu_restyle.py changes no density (it only grows the outer outline a square);
  * idle / c_idle: the human / spider design breathing (everything above the waist up BREATH squares at PPU);
    hit / c_hit: the design moved HIT_DX back, a white flash on the first frame;
  * tidy: the outline closed, 1-square slits and holes up to HOLE_FILL filled, loose specks off.
Both forms in one sheet: the huntress's tags and the spider's c_* (league_nidalee's way: the data plays the spider's
casts by CasterAnimation, the add-on swaps idle / run / hit / dead to c_idle ...).
Writes assets/source/ppu/orig/elise_<tag>.png / .json (the frames at PPU, each round(PPU x its 1x frame) round the
pivot) and league/champions/league_elise#sheet.png / #anim.fanim (the 1x tags, the fallback without league.dll).
Then tools/art/ppu_restyle.py --hero elise and tools/art/ppu_hd.py --hero elise.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import import_elise_strips as I  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "elise")
FRAMES = os.path.join(SRC, "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_elise")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
NATIVE = 100 / 38                 # design squares a game pixel (crown to toes 100 squares = 38 game rows)
PPU = 1.8                         # the user's pick: 1.5 first, then 「脸部这么糊？用PPU调整一下啊」「用1.8」
K = PPU / NATIVE
FEET = 11                         # 1x rows from the pivot down to the ground row (the pack's 128-canvas heroes)
ORDER = ["idle", "run", "attack", "skill", "skill2", "transform", "hit", "dead",
         "c_idle", "c_run", "c_attack", "c_skill", "c_skill2", "c_land", "c_transform", "c_hit", "c_dead"]
IDLE_MS = 150
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
HIT_DX = 4                        # PPU squares
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
HOLE_FILL = 12
SPECK = 16                        # detached bits under this many PPU squares go (dead 3: a 12-square leg tip)


def lp(path):
    return I.lp(path)


def palette():
    cols = set()
    for form in I.FORMS:
        d = I.design(form)
        cols |= {tuple(int(v) for v in c) for c in d[d[..., 3] > 0][:, :3]}
    return np.array(sorted(cols, key=sum), np.uint8)


PAL = palette()
PALF = PAL.astype(float)
OUTLINE = tuple(int(v) for v in PAL[0])


def form_of(tag):
    return "spider" if tag.startswith("c_") else "human"


def pivot(form):
    return (I.FORMS[form]["piv"] + 0.5, I.SOLE + 1)


# one face for every frame (the user: 「脸部这么糊？用PPU调整一下啊」): the design's face brought down to PPU once, the
# eyes and brows kept (a square EYE_RED or more eye red turns eye red, DARK_LINE or more near-black turns the outline,
# over the face's EYES box of design rows / columns), then pasted on every human frame where the design's face went
# (import_elise_strips.py's faces.json, the dense face box's top-left) after its own downscale
EYE_RED, DARK_LINE = 0.2, 0.35
EYES = (38, 56, 45, 62)           # design rows / columns: the brows, the eyes, the mouth
FACE_BOX = (36, 44)               # import_elise_strips FORMS["human"]["face"]: the face box's top-left (row, column)


def grid(a, piv, nx0, ny0):
    """Each dense column's / row's PPU square for a frame pixelated round piv."""
    H, W = a.shape[:2]
    c = 1.0 / K
    cx = np.floor((np.arange(W) + 0.5 - piv[0]) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - piv[1]) / c).astype(int) + ny0
    return cx, cy


def face_patch():
    """The design's head (import_elise_strips HEAD box) at PPU with the eyes kept -> (patch RGBA, its top-left square
    and the face box's top-left dense point on the design canvas)."""
    can = design_canvas("human")
    piv = pivot("human")
    out, (nx0, ny0) = PD.pixelate(can, K, piv, OUTLINE, PALF)
    cx, cy = grid(can, piv, nx0, ny0)
    ax, ay = I.FORMS["human"]["at"]
    rgb = can[..., :3].astype(int)
    op = can[..., 3] > 0
    red = op & (rgb[..., 0] > 170) & (rgb[..., 1] < 70) & (rgb[..., 2] < 90)
    dark = op & (rgb.sum(-1) < 70)
    e0, e1, f0, f1 = EYES
    cells = {}
    for y in range(ay + e0, ay + e1):
        for x in range(ax + f0, ax + f1):
            cells.setdefault((cy[y], cx[x]), []).append((y, x))
    for (j, i), pts in cells.items():
        n = len(pts)
        if sum(red[y, x] for y, x in pts) >= EYE_RED * n:
            cols, cnt = np.unique(np.array([can[y, x, :3] for y, x in pts if red[y, x]]), axis=0, return_counts=True)
            out[j, i, :3], out[j, i, 3] = cols[cnt.argmax()], 255
        elif sum(dark[y, x] for y, x in pts) >= DARK_LINE * n:
            out[j, i, :3], out[j, i, 3] = OUTLINE, 255
    # the head's squares at PPU: those whose dense centre lies in the design's head ellipse (import_elise_strips)
    ys, xs, clear = I.head_mask("human")
    cells = {}
    for y, x, c in zip(ys, xs, clear):
        k = (cy[ay + y], cx[ax + x])
        cells.setdefault(k, []).append(c)
    j0 = min(j for j, _ in cells); i0 = min(i for _, i in cells)
    j1 = max(j for j, _ in cells) + 1; i1 = max(i for _, i in cells) + 1
    patch = np.zeros((j1 - j0, i1 - i0, 4), np.uint8)
    clr = np.zeros(patch.shape[:2], bool)
    for (j, i), cs in cells.items():
        patch[j - j0, i - i0] = out[j, i]
        clr[j - j0, i - i0] = out[j, i, 3] == 0 and sum(cs) * 2 >= len(cs)
    return (patch, clr), (j0, i0), (ax + FACE_BOX[1], ay + FACE_BOX[0]), (nx0, ny0)


FACE = None


def paste_face(p, face_at, corner):
    """The PPU face pasted on a PPU frame whose dense face box sits at face_at (x, y)."""
    global FACE
    if FACE is None:
        FACE = face_patch()
    (patch, clr), (j0, i0), (dfx, dfy), (dnx, dny) = FACE
    # the design's square of the face's top-left -> this frame's: the dense shift times K, the grids meeting at the pivots
    dj = int(round((face_at[1] - dfy) * K)) + (corner[1] - dny)
    di = int(round((face_at[0] - dfx) * K)) + (corner[0] - dnx)
    out = p.copy()
    for m, put in ((patch[..., 3] > 0, True), (clr, False)):
        ys, xs = np.nonzero(m)
        ty, tx = ys + j0 + dj, xs + i0 + di
        ok = (ty >= 0) & (ty < out.shape[0]) & (tx >= 0) & (tx < out.shape[1])
        out[ty[ok], tx[ok]] = patch[ys[ok], xs[ok]] if put else 0
    return out


def to_ppu(a, form, face_at=None):
    """A dense canvas -> (the frame at PPU, the pivot there (x, ground row)); a human frame with its face box's dense
    top-left gets the one face."""
    out, (nx0, ny0) = PD.pixelate(a, K, pivot(form), OUTLINE, PALF)
    if face_at is not None:
        out = paste_face(out, face_at, (nx0, ny0))
    return tidy(out), (nx0, ny0)


def cracks(a):
    """1-square slits of ground into the body, filled with the outline (twice: 2-square slits)."""
    out = a.copy()
    for _ in range(2):
        op = out[..., 3] > 0
        lr = np.zeros_like(op)
        lr[:, 1:-1] = op[:, :-2] & op[:, 2:]
        ud = np.zeros_like(op)
        ud[1:-1] = op[:-2] & op[2:]
        m = (lr | ud) & ~op
        if not m.any():
            break
        out[m, :3] = OUTLINE
        out[m, 3] = 255
    return out


def tidy(a):
    out = G.complete_outline(cracks(a), color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > HOLE_FILL:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < SPECK:
                out[lbl == k] = 0
    return out


def design_canvas(form):
    d = I.design(form)
    x0, y0 = I.FORMS[form]["at"]
    c = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    c[y0:y0 + d.shape[0], x0:x0 + d.shape[1]] = d
    return c


def breathe(a, waist, k):
    if k == 0:
        return a.copy()
    out = a.copy()
    mask = np.zeros(a.shape[:2], bool)
    mask[:waist] = a[:waist, :, 3] > 0
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    out[ys - k, xs] = a[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            if y + 1 < a.shape[0] and out[y + 1, x, 3] > 0:
                out[y, x] = out[y + 1, x]
    return out


def design_face(form):
    ax, ay = I.FORMS[form]["at"]
    return (ax + FACE_BOX[1], ay + FACE_BOX[0]) if form == "human" else None


def idle_frames(form):
    a0, corner = to_ppu(design_canvas(form), form, design_face(form))
    ys = np.nonzero(a0[..., 3] > 0)[0]
    waist = int(ys.min() + (ys.max() - ys.min()) * 0.55)
    return [(tidy(breathe(a0, waist, b)), corner, IDLE_MS) for b in BREATH]


def hit_frames(form):
    a0, corner = to_ppu(design_canvas(form), form, design_face(form))
    out = []
    for dx, flash, ms in HIT:
        a = np.roll(a0, -dx, axis=1)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, corner, ms))
    return out


def actions():
    table = json.load(open(lp(os.path.join(FRAMES, "frames.json")), encoding="utf-8"))
    faces = json.load(open(lp(os.path.join(FRAMES, "faces.json")), encoding="utf-8"))
    out = {"idle": idle_frames("human"), "c_idle": idle_frames("spider"), "hit": hit_frames("human"),
           "c_hit": hit_frames("spider")}
    for tag, frames in table.items():
        form = form_of(tag)
        out[tag] = []
        for name, ms in frames:
            a = np.asarray(Image.open(lp(os.path.join(FRAMES, name))).convert("RGBA")).copy()
            p, corner = to_ppu(a, form, faces.get(name[:-4]))
            out[tag].append((p, corner, ms))
    return {t: out[t] for t in ORDER}


def one_of(can, px, py, hw, hh, need=0.5):
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can, corner):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot). The pivot: the corner's
    column, FEET 1x rows above the ground row."""
    px, py = float(corner[0]), corner[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh))[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's PPU frames at 3x here")
    a = ap.parse_args()
    acts = actions()
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, corner, t in frames:
            one, hd = down(can, corner)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"elise_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"elise_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 3
            w = max(h.shape[1] for h in hds)
            hgt = max(h.shape[0] for h in hds)
            big = Image.new("RGBA", (len(hds) * (w + 4) * Z, hgt * Z), (96, 112, 96, 255))
            for j, h in enumerate(hds):
                big.alpha_composite(Image.fromarray(h).resize((h.shape[1] * Z, h.shape[0] * Z), Image.NEAREST),
                                    (j * (w + 4) * Z, (hgt - h.shape[0]) * Z))
            big.convert("RGB").save(os.path.join(a.review, f"elise_{tag}.png"))
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_elise#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
