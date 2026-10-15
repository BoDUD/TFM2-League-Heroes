#!/usr/bin/env python3
"""league_kalista's frames: the finished strips (tools/art/import_kalista_strips.py -> assets/source/kalista/frames) and
the design -> the dense strips at PPU 1.4 (85 %) and the 1x sheet.

    python tools/art/rig_kalista.py [--review DIR]

league_elise's way (tools/art/rig_elise.py). The user, 2026-10-16: 「模型太大 第二像素太高 需要降低」, then from the size x
PPU sheet 「大小 85%，PPU 1.4」. The 85 % is baked into the frames (league_smolder's way: no SIZES row in hd.rs), so the
1x sheet - the fallback without league.dll - is the same size:
  * the frames are on the design's grid (82 squares helm to soles = 40 game rows: NATIVE squares a game pixel) and
    brought here to PPU x SIZE squares a game pixel of the 100 % figure (pixel_down.pixelate on a grid through the
    pivot, the design's colours), so ppu_restyle.py changes no density;
  * one head: the design's whole head (import_kalista_strips HEAD) brought down once, the eyes kept (a square EYE or
    more of the glowing eye white turns white, DARK_LINE or more near-black turns the outline), pasted on every frame
    where the dense head matched at score <= HEAD_EXACT (Codex's frames and the run: the design head is there
    exactly); the turned lying frames keep their own;
  * idle: the design breathing (above the waist up BREATH squares, the spear in her hand carried whole);
    hit: the design moved HIT_DX back, a white flash on the first frame;
  * tidy: the outline closed, 1-square slits and small holes filled, loose specks off.
Writes assets/source/ppu/orig/kalista_<tag>.png / .json (each round(PPU x its 1x frame) round the pivot) and
league/champions/league_kalista#sheet.png / #anim.fanim (the 1x tags). Then tools/art/ppu_restyle.py --hero kalista and
tools/art/ppu_hd.py --hero kalista.
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
import import_kalista_strips as I  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kalista")
FRAMES = os.path.join(SRC, "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_kalista")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
NATIVE = 82 / 40                  # design squares a game pixel at 100 %
PPU = 1.4                         # the user's pick (2026-10-16)
SIZE = 0.85                       # baked in
K = PPU * SIZE / NATIVE
FEET = 11                         # 1x rows from the pivot down to the ground row
PIVOT = (I.PIV_X + 0.5, I.SOLE + 1)
ORDER = ["idle", "run", "attack", "hop_b", "hop_f", "skill", "skill2", "ult", "ult2", "hit", "dead"]
IDLE_MS = 150
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]
HIT_DX = 3                        # PPU squares
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
HOLE_FILL = 8
SPECK = 10
EYE, DARK_LINE = 0.2, 0.35
EYES = (26, 38, 86, 100)          # design rows / columns: the eyes and the brow line
HEAD_EXACT = 20                   # mean colour distance of a frame's head to the design's: pasted there


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


def head_patch():
    """The design's head at PPU (eyes kept) -> (patch, clear mask, its top-left square, the dense head origin, corner)."""
    can = design_canvas()
    out, (nx0, ny0) = PD.pixelate(can, K, PIVOT, OUTLINE, PALF)
    cx, cy = grid(can, nx0, ny0)
    ax, ay = I.DESIGN_AT
    rgb = can[..., :3].astype(int)
    op = can[..., 3] > 0
    white = op & (rgb.sum(-1) > 700)
    dark = op & (rgb.sum(-1) < 70)
    e0, e1, f0, f1 = EYES
    cells = {}
    for y in range(ay + e0, ay + e1):
        for x in range(ax + f0, ax + f1):
            cells.setdefault((cy[y], cx[x]), []).append((y, x))
    for (j, i), pts in cells.items():
        n = len(pts)
        if sum(white[y, x] for y, x in pts) >= EYE * n:
            out[j, i, :3], out[j, i, 3] = WHITE, 255
        elif sum(dark[y, x] for y, x in pts) >= DARK_LINE * n:
            out[j, i, :3], out[j, i, 3] = OUTLINE, 255
    cells = {}
    ys, xs = np.nonzero(I.HM)
    for y, x in zip(ys, xs):
        cells.setdefault((cy[ay + I.HR0 + y], cx[ax + I.HC0 + x]), []).append(1)
    j0 = min(j for j, _ in cells)
    i0 = min(i for _, i in cells)
    j1 = max(j for j, _ in cells) + 1
    i1 = max(i for _, i in cells) + 1
    patch = np.zeros((j1 - j0, i1 - i0, 4), np.uint8)
    for (j, i) in cells:
        patch[j - j0, i - i0] = out[j, i]
    return patch, (j0, i0), (ax + I.HC0, ay + I.HR0), (nx0, ny0)


HEADP = head_patch()


def paste_head(p, head_at, corner):
    patch, (j0, i0), (dhx, dhy), (dnx, dny) = HEADP
    dj = int(round((head_at[1] - dhy) * K)) + (corner[1] - dny)
    di = int(round((head_at[0] - dhx) * K)) + (corner[0] - dnx)
    out = p.copy()
    ys, xs = np.nonzero(patch[..., 3] > 0)
    ty, tx = ys + j0 + dj, xs + i0 + di
    ok = (ty >= 0) & (ty < out.shape[0]) & (tx >= 0) & (tx < out.shape[1])
    out[ty[ok], tx[ok]] = patch[ys[ok], xs[ok]]
    return out


def to_ppu(a, head=True):
    out, (nx0, ny0) = PD.pixelate(a, K, PIVOT, OUTLINE, PALF)
    if head:
        s, ox, oy = I.find_head(a, rng=60)
        if s <= HEAD_EXACT:
            out = paste_head(out, (ox, oy), (nx0, ny0))
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


def spear_mask_ppu(p, corner):
    """The design's spear (import_kalista_strips' death split, design A's line) at PPU on the idle frame."""
    can = design_canvas()
    ax, ay = I.DESIGN_AT
    m = np.zeros(can.shape[:2], bool)
    for y in range(can.shape[0]):
        for x in range(can.shape[1]):
            if not can[y, x, 3]:
                continue
            dx, dy = x - ax, y - ay
            r = I.dist_line(dx + 0.5, dy + 0.5, (0.5, 83.5), (80.5, 50.5))
            if (dx <= 60 and r <= 3.4) or (66 <= dx <= 81 and r <= 2.6 and not I.is_skin(can[y, x])):
                m[y, x] = True
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
    carried = spear_mask_ppu(a0, corner)
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


def actions():
    table = json.load(open(lp(os.path.join(FRAMES, "frames.json")), encoding="utf-8"))["tags"]
    out = {"idle": idle_frames(), "hit": hit_frames()}
    for tag, frames in table.items():
        out[tag] = []
        for e in frames:
            a = np.asarray(Image.open(lp(os.path.join(FRAMES, e["file"]))).convert("RGBA")).copy()
            lying = tag == "dead" and e["file"] in ("dead_4.png", "dead_5.png", "dead_6.png")
            p, corner = to_ppu(a, head=not lying)
            out[tag].append((p, corner, e["ms"]))
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
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"kalista_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"kalista_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
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
            big.convert("RGB").save(os.path.join(a.review, f"kalista_{tag}.png"))
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_kalista#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
