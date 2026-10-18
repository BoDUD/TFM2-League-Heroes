#!/usr/bin/env python3
"""league_drmundo's frames: the finished strips (tools/art/import_drmundo_strips.py -> assets/source/drmundo/frames) and
the design -> the dense strips at PPU 1.5 and the 1x sheet.

    python tools/art/rig_drmundo.py [--review DIR]

The Kalista way (rig_kalista.py). The user, 2026-10-16: 「选 A，42 行，PPU 1.5」:
  * the frames are on the design's grid (90 squares hair to soles = 42 game rows: NATIVE squares a game pixel) and
    brought here to PPU squares a game pixel (pixel_down.pixelate on a grid through the pivot, the design's colours),
    so ppu_restyle.py changes no density;
  * heads: every frame's own (Codex's heads are the design's; import_drmundo_strips.py);
  * idle: the design breathing (above the waist up BREATH squares, the saw in his hand carried whole);
    hit: the design moved HIT_DX back, a white flash on the first frame;
  * tidy: the outline closed, 1-square slits and small holes filled, loose specks off.
Writes assets/source/ppu/orig/drmundo_<tag>.png / .json (each round(PPU x its 1x frame) round the pivot) and
league/champions/league_drmundo#sheet.png / #anim.fanim (the 1x tags). Then tools/art/ppu_restyle.py --hero drmundo and
tools/art/ppu_hd.py --hero drmundo.
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
import import_drmundo_strips as I  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "drmundo")
FRAMES = os.path.join(SRC, "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_drmundo")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
NATIVE = 90 / 42                  # design squares a game pixel
PPU = 1.5                         # the user's pick (2026-10-16)
SIZE = 1.0
K = PPU * SIZE / NATIVE
FEET = 11                         # 1x rows from the pivot down to the ground row
PIVOT = (I.PIV_X + 0.5, I.SOLE + 1)
ORDER = ["idle", "run", "attack", "attack_e", "skill", "skill2", "skill2_end", "ult", "hit", "dead"]
IDLE_MS = 150
BREATH = [0, 1, 1, 2, 2, 1, 1, 0]
HIT_DX = 3                        # PPU squares
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
HOLE_FILL = 8
SPECK = 10
# the saw and the near forearm holding it (design rows 44 down, columns 0-46): carried whole when he breathes
SAW = (44, 0, 47)


def lp(path):
    return I.lp(path)


def palette():
    d = I.A
    cols = {tuple(int(v) for v in c) for c in d[d[..., 3] > 0][:, :3]}
    return np.array(sorted(cols, key=sum), np.uint8)


PAL = palette()
PALF = PAL.astype(float)
OUTLINE = tuple(int(v) for v in PAL[0])
WHITE = max((tuple(int(v) for v in c) for c in PAL), key=sum)


def grid(a, nx0, ny0):
    H, W = a.shape[:2]
    c = 1.0 / K
    cx = np.floor((np.arange(W) + 0.5 - PIVOT[0]) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - PIVOT[1]) / c).astype(int) + ny0
    return cx, cy


def design_canvas():
    return I.A_on_canvas()


def to_ppu(a):
    out, (nx0, ny0) = PD.pixelate(a, K, PIVOT, OUTLINE, PALF)
    return tidy(out), (nx0, ny0)


def cracks(a):
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


def saw_mask_ppu(p, corner):
    """The design's saw and the hand on it at PPU on the idle frame."""
    can = design_canvas()
    ax, ay = I.DESIGN_AT
    m = np.zeros(can.shape[:2], bool)
    r0, c0, c1 = SAW
    m[ay + r0:, ax + c0:ax + c1] = can[ay + r0:, ax + c0:ax + c1, 3] > 0
    cx, cy = grid(can, *corner)
    out = np.zeros(p.shape[:2], bool)
    ys, xs = np.nonzero(m)
    j, i = cy[ys], cx[xs]
    ok = (j >= 0) & (j < p.shape[0]) & (i >= 0) & (i < p.shape[1])
    out[j[ok], i[ok]] = True
    return out & (p[..., 3] > 0)


def breathe(a, waist, k, carried):
    if k == 0:
        return a.copy()
    out = a.copy()
    mask = np.zeros(a.shape[:2], bool)
    mask[:waist] = a[:waist, :, 3] > 0
    mask |= carried
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    out[ys - k, xs] = a[ys, xs]
    hole = (out[..., 3] == 0) & mask & ~carried
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            if y + 1 < a.shape[0] and out[y + 1, x, 3] > 0:
                out[y, x] = out[y + 1, x]
    return out


def idle_frames():
    a0, corner = to_ppu(design_canvas())
    ys = np.nonzero(a0[..., 3] > 0)[0]
    waist = int(ys.min() + (ys.max() - ys.min()) * 0.55)
    carried = saw_mask_ppu(a0, corner)
    return [(tidy(breathe(a0, waist, b, carried)), corner, IDLE_MS) for b in BREATH]


def hit_frames():
    a0, corner = to_ppu(design_canvas())
    out = []
    for dx, flash, ms in HIT:
        a = np.roll(a0, -dx, axis=1)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, corner, ms))
    return out


# 2026-10-19 frame audit: his run moved 9 % of his squares a frame against the pack's 40 % (the strips' short front-on
# stride, his body bobbing about a game pixel) and his death had 6 frames against the pack's 8. Without redrawing the
# strips' legs: the whole figure hops RUN_HOP more design squares off the ground between the strides' ends (run_1 the
# feet closest, run_5 widest), and the death gets the lying frame twice more, DEAD_DROP squares above the ground before
# it lands and DEAD_BOUNCE after.
RUN_HOP = [0, 1, 2, 1, 0, 1, 2, 1]
DEAD_LIE = 2                      # dead_3.png: the first frame lying
DEAD_DROP, DEAD_BOUNCE = 5, 2
DEAD_MS = [100, 100, 60, 90, 60, 110, 150, 400]


# R Maximum Dosage (League's drmundo_spell4: he jabs a syringe into himself, then roars): the strips had no syringe. One
# is drawn in his far fist on the crouching frames, in the design's own colours (the saw's pale glass, the boils'
# magenta for the dose, dark steel for the needle), from the fist's grip toward the tip: held up ready on ult_1, its
# needle in his side on ult_4. Nothing of him moves.
SYRINGE = {0: ((112, 151), (99, 161)), 3: ((116, 146), (113, 130))}     # ult frame -> (grip, needle tip), (row, col)
GLASS, DOSE, STEEL, PLUNGER = (183, 220, 218), (241, 3, 103), (99, 108, 125), (132, 146, 157)


def syringe(a, grip, tip):
    """The syringe on native frame a: the plunger behind the grip, the barrel (glass round a magenta dose) from the grip
    to 70 % of the way, the needle on to the tip; outlined."""
    out = a.copy()
    (gy, gx), (ty, tx) = grip, tip
    H, W = a.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    vy, vx = ty - gy, tx - gx
    L = np.hypot(vy, vx)
    uy, ux = vy / L, vx / L
    along = (ys + 0.5 - gy) * uy + (xs + 0.5 - gx) * ux
    across = np.abs((ys + 0.5 - gy) * ux - (xs + 0.5 - gx) * uy)
    plunger = (along >= -4) & (along < 0) & (across <= 1.6)
    barrel = (along >= 0) & (along <= 0.7 * L) & (across <= 2.2)
    dose = barrel & (across <= 1.0) & (along >= 1.5)
    needle = (along > 0.7 * L) & (along <= L) & (across <= 0.7)
    body = plunger | barrel | needle
    ring = ndimage.binary_dilation(body, structure=np.ones((3, 3))) & ~body
    out[ring] = (*OUTLINE, 255)
    out[plunger] = (*PLUNGER, 255)
    out[barrel] = (*GLASS, 255)
    out[dose] = (*DOSE, 255)
    out[needle] = (*STEEL, 255)
    return out


def lifted(a, k):
    """a moved k rows up (nothing wraps round)."""
    if k == 0:
        return a
    out = np.zeros_like(a)
    out[:-k] = a[k:]
    return out


def actions():
    table = json.load(open(lp(os.path.join(FRAMES, "frames.json")), encoding="utf-8"))["tags"]
    out = {"idle": idle_frames(), "hit": hit_frames()}
    for tag, frames in table.items():
        out[tag] = []
        src = [(np.asarray(Image.open(lp(os.path.join(FRAMES, e["file"]))).convert("RGBA")).copy(), e["ms"])
               for e in frames]
        if tag == "run":
            src = [(lifted(a, RUN_HOP[i]), ms) for i, (a, ms) in enumerate(src)]
        if tag == "ult":
            src = [(syringe(a, *SYRINGE[i]) if i in SYRINGE else a, ms) for i, (a, ms) in enumerate(src)]
        if tag == "dead":
            lie = src[DEAD_LIE][0]
            src = src[:DEAD_LIE] + [(lifted(lie, DEAD_DROP), 0), (lie, 0), (lifted(lie, DEAD_BOUNCE), 0)] + src[DEAD_LIE + 1:]
            src = [(a, ms) for (a, _), ms in zip(src, DEAD_MS)]
        for a, ms in src:
            p, corner = to_ppu(a)
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
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"drmundo_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"drmundo_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
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
            big.convert("RGB").save(os.path.join(a.review, f"drmundo_{tag}.png"))
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_drmundo#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
