#!/usr/bin/env python3
"""league_bard's dense front design (PPU 1.5) from Codex's step-1 delivery: assets/source/bard/hd/front.png.

    python tools/art/design_bard_hd.py [--check]

The user picked picture A at 85 % ("A 模型太大了 缩小一点", 2026-10-13). Codex's own 51-row front (codex_model/
bard-front.png) came down from its fine draft by a crude cut and read muddy (a grey blob of an arm, a speckled tabard,
black-framed gold blocks for bells, legs hardly there); the user: 「你处理处理不就能用了」「你帮忙修复吧 修复到完美了再喊我
review」. Its raw draft (codex_model/raw/front-01.png) is clean pixel art on ~8-px squares (140 x 130 read back), so the
design is that draft brought to 51 rows mane-top to soles my way, then the parts that do not survive the cut drawn in:
  1. regrid.py reads the draft on its own grid (raw_rg: 140 x 130 squares).
  2. 30 colours: the outline (near-black) + 29 k-means colours in Lab of the rest.
  3. Majority vote down to 51 rows (2.51 draft squares per design square, the soles on the bottom): a square is clear
     where half or more of it is, outline where a third or more of the drawn part is near-black, else the colour that
     covers most of it.
  4. Codex's own 10 x 10 bronze mask (three gold holes) and its antenna replace the cut-down mask (too small to show
     eyes); Codex's gold ring + teal swirl replace the bell-mouth, with a one-square outline.
  5. The horn and its three bells redrawn: the draft's horn centreline and widths rasterised per square (ivory light /
     mid / shade across the arc, two leather bands), behind the arm (a hand-read left edge of the arm per row), the
     bells as small gold sprites; one-square outline round the horn; 1-2 square cracks between horn and arm closed.
  6. The outer outline grown by one square (4-neighbours): ~1.3 game px, as on the restyled PPU heroes.
  7. Near-duplicate colours merged (the ring's golds to the body's), dents and lone specks closed.
  8. Two majority passes (pixel_down._majority: a square unlike its 8 neighbours takes their commonest colour when 4
     or more share it) for the Zeri look's calm (adjacent differing squares 0.47 -> 0.38; Zeri 0.37), the mask, the
     antenna, the ring, the charm between the legs and every gold / teal / purple square kept (thin parts the passes
     would eat); then the two notches they open closed.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts")
sys.path.insert(0, SKILL)
import strips  # noqa: E402
sys.path.insert(0, HERE)
from pixel_down import _majority as pd_majority  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "bard")
RAW = os.path.join(SRC, "codex_model", "raw", "front-01.png")
CODEX_FRONT = os.path.join(SRC, "codex_model", "bard-front.png")
OUT = os.path.join(SRC, "hd", "front.png")
WORK = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ba_work", "design")

K = (13, 12, 17)
LEG = {
    'K': K, 'M': (253, 253, 219), 'R': (248, 250, 228), 'b': (208, 217, 187), 'P': (172, 170, 143),
    'a': (142, 161, 144), 'E': (109, 134, 118), 'B': (80, 102, 93), 'V': (48, 72, 67), 'A': (69, 57, 65),
    'L': (248, 53, 46), 'N': (214, 26, 42), 'Z': (183, 17, 37), 'U': (141, 31, 41), 'S': (101, 22, 30),
    'G': (71, 17, 24), 'W': (254, 113, 52), 'H': (124, 52, 32), 'I': (100, 61, 30), 'C': (66, 37, 19),
    'Q': (146, 88, 32), 'c': (127, 91, 57), 'F': (229, 172, 124), 'O': (250, 210, 50), 'T': (202, 140, 16),
    'Y': (255, 211, 69), 'y': (255, 244, 160), 'g': (220, 155, 39), 'X': (34, 197, 157), 't': (38, 193, 164),
    'q': (24, 133, 127), 'D': (103, 53, 195), 'J': (60, 38, 72), '%': (65, 80, 120), 'd': (45, 54, 83),
    'm': (142, 93, 56), 'l': (179, 124, 72),
}
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)

# ------------------------------------------------------------------------------------------------ 1-3: the cut
CROWN, SOLE, TARGET = 12, 139, 51      # the draft's mane top and soles rows (raw_rg), the design's rows between


def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def kmeans(px, n, seed=0, it=30):
    rng = np.random.default_rng(seed)
    L = lab(px.astype(float))
    cen = L[rng.choice(len(L), n, replace=False)]
    for _ in range(it):
        idx = ((L[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (idx == j).any():
                cen[j] = L[idx == j].mean(0)
    idx = ((L[:, None] - cen[None]) ** 2).sum(-1).argmin(1)
    return np.array([px[idx == j].mean(0) if (idx == j).any() else px[0] for j in range(n)]).round().astype(np.uint8)


def cut(a, n_col=30, dark_frac=0.34, seed=0):
    op = a[..., 3] > 0
    px = a[op][:, :3]
    dark = px.astype(int).sum(1) < 90
    pal = np.vstack([np.array([[14, 12, 18]], np.uint8), kmeans(px[~dark], n_col - 1, seed)])
    L = lab(pal.astype(float))
    idx = np.full(op.shape, -1)
    d = ((lab(a[..., :3].astype(float))[..., None, :] - L[None, None]) ** 2).sum(-1)
    idx[op] = d[op].argmin(-1)
    idx[op & (a[..., :3].astype(int).sum(-1) < 90)] = 0
    s = (SOLE - CROWN + 1) / TARGET
    H, W = op.shape
    nrows, ncols = int(np.ceil((SOLE + 1) / s)), int(np.ceil(W / s))
    top = SOLE + 1 - nrows * s
    out = np.full((nrows, ncols), -1)
    for r in range(nrows):
        y0, y1 = top + r * s, top + (r + 1) * s
        for c in range(ncols):
            x0, x1 = c * s, (c + 1) * s
            w, tot = {}, 0.0
            for yy in range(int(np.floor(y0)), int(np.ceil(y1))):
                if not 0 <= yy < H:
                    continue
                wy = min(y1, yy + 1) - max(y0, yy)
                for xx in range(int(np.floor(x0)), int(np.ceil(x1))):
                    if not 0 <= xx < W:
                        continue
                    wx = min(x1, xx + 1) - max(x0, xx)
                    w[idx[yy, xx]] = w.get(idx[yy, xx], 0) + wx * wy
                    tot += wx * wy
            clear = w.get(-1, 0)
            if tot == 0 or clear >= 0.5 * tot:
                continue
            if w.get(0, 0) >= dark_frac * (tot - clear):
                out[r, c] = 0
                continue
            out[r, c] = max((v, k) for k, v in w.items() if k > 0)[1]
    img = np.zeros((nrows, ncols, 4), np.uint8)
    m = out >= 0
    img[m, :3] = pal[out[m]]
    img[m, 3] = 255
    bb = Image.fromarray(img).getbbox()
    return img[bb[1]:bb[3], bb[0]:bb[2]]


# ------------------------------------------------------------------------------------------------ 4: mask, antenna, ring
MASK = ["..KKKKKK..", ".KmmmmmmK.", "KmmllllmmK", "KmYYmmYYmK", "KmYymmyYmK", "KmmmmmmmmK", "KmmmYYmmmK",
        "KmmmyYmmmK", ".KmmmmmmK.", "..KKKKKK.."]
ANT = [".KKK.", "KgygK", "KYYgK", ".KmK.", ".KmK.", ".KmK."]
OLD_MASK = {(229, 172, 124), (124, 52, 32), (146, 88, 32), (250, 210, 50), (100, 61, 30), (127, 91, 57),
            (66, 37, 19), (202, 140, 16)}


def put(a, rows, r0, c0, corner=None, clear=False):
    for i, row in enumerate(rows):
        for j, ch in enumerate(row):
            if ch == '.':
                if corner:
                    corner(a, r0 + i, c0 + j)
                elif clear:
                    a[r0 + i, c0 + j] = 0
                continue
            a[r0 + i, c0 + j, :3] = LEG[ch]
            a[r0 + i, c0 + j, 3] = 255


def head_and_ring(a, codex):
    def mane(a, r, c):
        if tuple(int(x) for x in a[r, c, :3]) in OLD_MASK:
            a[r, c, :3] = LEG['M']
            a[r, c, 3] = 255
    a[0:5, 33:40] = 0                        # the cut-down bead and stick
    put(a, MASK, 7, 32, corner=mane)
    put(a, ANT, 1, 34)
    ring = codex[6:17, 12:23]                # Codex's gold ring + teal swirl (its front, read on its grid)
    gt = {LEG[k] for k in 'YgqtY'} | {LEG['y']}
    m = np.array([[tuple(int(x) for x in ring[i, j, :3]) in gt and ring[i, j, 3] > 0 for j in range(11)]
                  for i in range(11)])
    br, bc = 3, 14
    sub = a[br:br + 11, bc:bc + 11]
    sub[m] = ring[m]
    ring_edge = ndimage.binary_dilation(np.pad(m, 1), structure=CROSS) & ~np.pad(m, 1)
    for i, j in zip(*np.where(ring_edge)):
        r, c = br + i - 1, bc + j - 1
        if 0 <= r < a.shape[0] and 0 <= c < a.shape[1]:
            a[r, c, :3] = K
            a[r, c, 3] = 255
    a, _, _ = strips.complete_outline(a, color=K)
    return a


# ------------------------------------------------------------------------------------------------ 5: horn and bells
S_, OFF = 2.5098, 0.56                   # draft squares per design square; design row = (draft y + OFF) / S_
PTS = np.array([(29, 12.5), (21, 15.5), (13, 21.5), (8, 30), (6.5, 40), (8.5, 50), (12.5, 59), (17.5, 67.5)], float)
WID = np.array([8.5, 9.5, 10, 10, 9.5, 8, 5.5, 2.0])
BANDS = [(0.13, 0.27), (0.42, 0.53)]
# the arm / hand / bracer's left edge per design row (read off the cut's letter map): horn and bells left of it
ARM_EDGE = {2: 13, 3: 12, 4: 11, 5: 11, 6: 10, 7: 9, 8: 9, 9: 9, 10: 10, 11: 8, 12: 8, 13: 7, 14: 9, 15: 8, 16: 7,
            17: 7, 18: 8, 19: 9, 20: 11, 21: 12, 22: 13, 23: 15, 24: 15, 25: 15, 26: 16, 27: 16, 28: 14, 29: 14,
            30: 12, 31: 12, 32: 12, 33: 10}
BELL_S = [".KK.", "KyOK", "KOTK", "KTTK", ".KK."]
BELL_B = [".KKK.", "KyOOK", "KOOTK", "KOOTK", "KTTTK", ".KKK."]


def horn_sample(px, py):
    seg = np.linalg.norm(np.diff(PTS, axis=0), axis=1)
    tt = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()
    best = (1e9, 0, 0, 0)
    for i in range(len(PTS) - 1):
        a, b = PTS[i], PTS[i + 1]
        ab = b - a
        u = np.clip(((px - a[0]) * ab[0] + (py - a[1]) * ab[1]) / (ab @ ab), 0, 1)
        q = a + u * ab
        d = np.hypot(px - q[0], py - q[1])
        if d < best[0]:
            nrm = np.array([-ab[1], ab[0]]) / np.linalg.norm(ab)
            side = np.sign((px - q[0]) * nrm[0] + (py - q[1]) * nrm[1])
            best = (d, tt[i] + u * (tt[i + 1] - tt[i]), side, WID[i] + u * (WID[i + 1] - WID[i]))
    d, t, side, w = best
    return d <= w / 2, t, side * d / max(w / 2, 1e-6)


def horn(a):
    H, W = a.shape[:2]
    a[(a[..., :3] == (14, 12, 18)).all(-1)] = (*K, 255)
    for r, e in ARM_EDGE.items():
        a[r, :e] = 0
    for r, e in ARM_EDGE.items():
        for c in range(e):
            hits, ts, offs = 0, [], []
            for sy in range(5):
                for sx in range(5):
                    ins, t, off = horn_sample((c + (sx + 0.5) / 5) * S_, (r + (sy + 0.5) / 5) * S_ - OFF)
                    if ins:
                        hits += 1
                        ts.append(t)
                        offs.append(off)
            if hits >= 10:
                t, off = float(np.median(ts)), float(np.median(offs))
                if any(lo <= t <= hi for lo, hi in BANDS):
                    col = LEG['H'] if off > -0.2 else LEG['C']
                else:
                    col = LEG['M'] if off > 0.35 else (LEG['b'] if off > -0.45 else LEG['P'])
                a[r, c, :3] = col
                a[r, c, 3] = 255
    for br, bc, spr in [(17, 4, BELL_S), (21, 7, BELL_B), (27, 4, BELL_S)]:
        put(a, spr, br, bc, clear=True)       # round the bells' corners off
    hornmask = np.zeros((H, W), bool)
    for r, e in ARM_EDGE.items():
        for c in range(e):
            hornmask[r, c] = a[r, c, 3] > 0 and tuple(int(x) for x in a[r, c, :3]) != K
    ring = ndimage.binary_dilation(hornmask, structure=CROSS) & (a[..., 3] == 0)
    a[ring, :3] = K
    a[ring, 3] = 255
    return a


def close_cracks(a, rows, cols, w=2):
    op = a[..., 3] > 0
    H, W = op.shape
    add = []
    for r in range(*rows):
        for c in range(*cols):
            if op[r, c]:
                continue
            for dr, dc in ((0, 1), (1, 0)):
                ok = False
                for k1 in range(1, w + 1):
                    r1, c1 = r - dr * k1, c - dc * k1
                    if 0 <= r1 < H and 0 <= c1 < W and op[r1, c1]:
                        for k2 in range(1, w + 2 - k1):
                            r2, c2 = r + dr * k2, c + dc * k2
                            if 0 <= r2 < H and 0 <= c2 < W and op[r2, c2]:
                                ok = True
                                break
                        break
                if ok:
                    add.append((r, c))
                    break
    for r, c in add:
        a[r, c, :3] = K
        a[r, c, 3] = 255
    return a


# ------------------------------------------------------------------------------------------------ 6-7: outline, tidy
def grow(a):
    op = np.pad(a[..., 3] > 0, 1)
    b = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    ring = ndimage.binary_dilation(op, structure=CROSS) & ~op
    b[ring, :3] = K
    b[ring, 3] = 255
    return b


def tidy(a):
    for src, dst in (('R', 'M'), ('Y', 'O'), ('g', 'T')):
        m = (a[..., :3] == LEG[src]).all(-1) & (a[..., 3] > 0)
        a[m, :3] = LEG[dst]
    # a teal speck by the ring, notches in the silhouette and lone cells in the outline
    for r, c in [(14, 25), (2, 13), (3, 25), (4, 33), (5, 40), (25, 14), (51, 28), (53, 35), (4, 12), (13, 25),
                 (14, 24), (17, 8), (35, 19)]:
        a[r, c, :3] = K
        a[r, c, 3] = 255
    return a


def calm(a):
    keep = np.zeros(a.shape[:2], bool)
    keep[0:18, 33:44] = True                 # antenna + mask
    keep[2:16, 14:28] = True                 # the bell-mouth ring
    keep[48:57, 28:36] = True                # the charm between the legs
    for k in 'DOTyXtq':
        keep |= (a[..., :3] == LEG[k]).all(-1)
    op = a[..., 3] > 0
    for _ in range(2):
        a = pd_majority(a, op, keep)
    for r, c in [(26, 14), (54, 35)]:
        a[r, c, :3] = K
        a[r, c, 3] = 255
    return a


def build():
    os.makedirs(WORK, exist_ok=True)
    rg = os.path.join(WORK, "raw_rg.png")
    subprocess.run([sys.executable, os.path.join(SKILL, "regrid.py"), RAW, rg], check=True, capture_output=True)
    a = cut(np.array(Image.open(rg).convert("RGBA")))
    codex = np.array(Image.open(CODEX_FRONT).convert("RGBA"))[6::12, 8::12][:128, :85]
    bb = Image.fromarray(codex).getbbox()
    codex = codex[bb[1]:bb[3], bb[0]:bb[2]]
    a = head_and_ring(a, codex)
    a = horn(a)
    a = close_cracks(a, (3, 28), (4, 17))
    a = grow(a)
    return calm(tidy(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="compare with this picture instead of writing")
    a_ = ap.parse_args()
    a = build()
    if a_.check:
        ref = np.array(Image.open(a_.check).convert("RGBA"))
        same = ref.shape == a.shape and (ref == a).all()
        print("identical" if same else f"DIFFERENT {ref.shape} {a.shape} {(ref != a).any(-1).sum() if ref.shape == a.shape else ''}")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    Image.fromarray(a).save(OUT)
    op = a[..., 3] > 0
    print(OUT, a.shape[1], "x", a.shape[0], "colours", len(set(map(tuple, a[op][:, :3]))))


if __name__ == "__main__":
    main()
