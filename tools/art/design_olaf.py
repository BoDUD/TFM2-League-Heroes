#!/usr/bin/env python3
"""Olaf's game-size design (step 1) from Codex's generator draft (assets/source/olaf/codex_model/raw).

    python tools/art/design_olaf.py [--out PNG] [--rows 42]    # the route from the raw draft -> the native design

How it came about (2026-10-09): the user picked Codex's picture A (League's idle: a wide crouched stance, an axe in
each hand). Codex's first step-1 round placed 40 x 33 figures square by square with a script (blocky, rejected); the
second round's generator attempt 2 (raw/olaf_design_raw.png) reads back on its own grid as 48 x 45 at the pack's
quality. The user picked 42 rows of it (the height of league_darius) and asked 「头上的角要完整」, so:
  1. the draft read back on its own grid (the skill's regrid.py) - 48 x 45;
  2. every square to the nearest of a palette (CIELAB): the read-back's own colours (median cut over the figure
     outside the face) plus the face's eye, mouth and tooth colours, which only the face box may use;
  3. whole rows and columns deleted: the head (rows 0-19: both horns, the helmet, the face) and the soles keep every
     row; 4 rows come out of the torso and arms (rows 20-34) and 2 out of the legs (35-42), spread out, each the row
     most like a kept neighbour (all 6 from the body anywhere took the greaves and boots: legs too short); columns
     the same way outside both horns, the face and the axes' blades;
  4. strips.complete_outline;
  5. on the 128 x 128 canvas at 8x: the soles on row 99, the middle of the feet on column 64.
The user then asked 「再精修一下吧 有点模糊啊」: the curated ramps (PAL; the median cut had merged the skin's shadows into
the hair's dark orange and kept 9 near-blacks), the lone near-duplicate squares merged (despeckle), and by hand on the
letter grid (work/ol/polish_ol.py): both horns lit on their upper edge, the helmet as one clean dome with a swirl and a
lit brim, both eyes (e, E) round the nose guard; the mouth back as the route drew it (「用之前的嘴」, with the tongue
colour p). Approved 「用右边」 (2026-10-09): FINAL, 42 x 39, 21 colours.

    python tools/art/design_olaf.py --final     # FINAL (the approved letter grid) -> OUT
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

RAW = os.path.join(ROOT, "assets", "source", "olaf", "codex_model", "raw", "olaf_design_raw.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "olaf_native.png")
FINAL = os.path.join(ROOT, "assets", "source", "olaf", "design", "olaf_design_42.txt")
SOLE_ROW, MID_COL = 99, 64
OUTLINE = (0x2A, 0x12, 0x08)
# the palette: 3-4 shades a material (a median cut of the read-back merged the skin's shadows into the hair's dark
# orange and kept 9 near-blacks: blurry); the face-only colours are used inside FACE alone
PAL = {
    "0": "#2A1208",   # outline (the only near-black)
    "r": "#A83410",   # hair / beard darkest
    "R": "#E94101",   # hair dark
    "o": "#FC8302",   # hair mid
    "O": "#FFB43C",   # hair light
    "k": "#A4542E",   # skin dark
    "K": "#D47C48",   # skin mid
    "S": "#FCB870",   # skin light
    "b": "#4A2A1E",   # leather / boots dark
    "B": "#74442C",   # leather mid
    "n": "#A06A44",   # leather light
    "d": "#2E3448",   # steel darkest (horns)
    "g": "#4E5E7E",   # steel dark
    "G": "#8494B2",   # steel mid
    "h": "#BCC4D8",   # steel light / fur shadow
    "w": "#ECEAF0",   # fur / steel highlight
    "W": "#FFFFFF",   # glint
    "e": "#0455A6",   # eye
    "E": "#022460",   # eye dark
    "m": "#B30729",   # mouth
    "t": "#F4E6E8",   # teeth
    "p": "#CA4A60",   # tongue
}
FACE_ONLY = ("e", "E", "m", "t", "p")
DARK_L = 18                                # CIELAB lightness under which a square is the outline (9 near-blacks were)
SPECK_DE = 14                              # a lone square this close to its neighbours' colour takes theirs
# on the 48 x 45 read-back
FACE = (12, 20, 21, 32)                    # rows, columns: eyes (row 13), nose guard, mouth and teeth (rows 16-17)
HEAD_ROWS = set(range(0, 20))              # horns, hair top, helmet, face: never deleted
SOLE_ROWS = set(range(44, 48))
HARD_COLS = set(range(12, 19)) | set(range(21, 36))   # the left horn, the face, the right horn
DROP_PARTS = [(20, 34, 4), (35, 42, 2)]    # (first row, last row, deletions): the torso and arms, the legs


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def lab(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def palette(a):
    """The curated ramps (PAL); the face-only colours are the last FACE_ONLY letters."""
    common = np.array([hx(v) for k, v in PAL.items() if k not in FACE_ONLY])
    own = np.array([hx(PAL[k]) for k in FACE_ONLY])
    return common, own


def snap(a, common, own):
    """Every square to the nearest PAL colour (CIELAB); the eye and mouth colours only inside the face box."""
    out = a.copy()
    y0, y1, x0, x1 = FACE
    L = lab(a[..., :3])
    allc = np.vstack([common, own])
    near_c = common[((L[..., None, :] - lab(common)[None, None]) ** 2).sum(-1).argmin(-1)]
    near_a = allc[((L[..., None, :] - lab(allc)[None, None]) ** 2).sum(-1).argmin(-1)]
    out[..., :3] = near_c
    out[y0:y1, x0:x1, :3] = near_a[y0:y1, x0:x1]
    out[L[..., 0] < DARK_L, :3] = OUTLINE     # every near-black is the one outline colour
    out[..., 3] = np.where(a[..., 3] > 0, 255, 0)
    return out


def despeckle(a):
    """A square whose colour none of its 8 neighbours has, and whose neighbours' commonest colour is within SPECK_DE
    (CIELAB) of it, takes that colour: near-duplicate tones read as blur. Contrasting single squares (a glint, a stud,
    an eye) stay - they are the detail."""
    out = a.copy()
    H, W = a.shape[:2]
    k = key(a)
    L = lab(a[..., :3])
    y0, y1, x0, x1 = FACE
    for y in range(H):
        for x in range(W):
            if not a[y, x, 3] or (y0 <= y < y1 and x0 <= x < x1):
                continue
            nb = [(yy, xx) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                  if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W and a[yy, xx, 3]]
            if not nb or any(k[yy, xx] == k[y, x] for yy, xx in nb):
                continue
            vals, cnt = np.unique([k[yy, xx] for yy, xx in nb], return_counts=True)
            top = vals[cnt.argmax()]
            yy, xx = next(p for p in nb if k[p] == top)
            if ((L[y, x] - L[yy, xx]) ** 2).sum() < SPECK_DE ** 2:
                out[y, x, :3] = a[yy, xx, :3]
    return out


def key(a):
    k = a[..., 0].astype(np.int64) << 16 | a[..., 1].astype(np.int64) << 8 | a[..., 2]
    return np.where(a[..., 3] > 0, k, -1)


def drop(lines, allowed, q):
    """q deletions among `allowed`: each time the line most like a kept neighbour, one next to an earlier
    deletion costing more (spread out)."""
    alive = list(range(len(lines)))
    gone = set()
    for _ in range(q):
        best = None
        for i, x in enumerate(alive):
            if x not in allowed or i == 0 or i == len(alive) - 1:
                continue
            c = min((lines[x] != lines[alive[i - 1]]).sum(), (lines[x] != lines[alive[i + 1]]).sum())
            c += 6 * ((x - 1 in gone) + (x + 1 in gone))
            if best is None or c < best[0]:
                best = (c, x)
        gone.add(best[1])
        alive.remove(best[1])
    return sorted(gone)


def cut(a, rows):
    H, W = a.shape[:2]
    k = key(a)
    assert sum(q for _, _, q in DROP_PARTS) == H - rows, "DROP_PARTS must delete exactly the extra rows"
    dr = []
    for lo, hi, q in DROP_PARTS:
        dr += drop([k[y] for y in range(H)], set(range(lo, hi + 1)) - HEAD_ROWS - SOLE_ROWS, q)
    dr = sorted(dr)
    kr = [y for y in range(H) if y not in dr]
    sub = k[kr]
    cols = round(W * rows / H)
    dc = drop([sub[:, x] for x in range(W)], set(range(W)) - HARD_COLS, W - cols)
    kc = [x for x in range(W) if x not in dc]
    return a[kr][:, kc], dr, dc


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def close_outline(a):
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    p, _, _ = strips.complete_outline(p, color=OUTLINE, feet=a.shape[0], keep=None)
    return crop(p)


def on_canvas(fig):
    fig = crop(fig)
    feet = np.nonzero((fig[-3:, :, 3] > 0).any(0))[0]
    out = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], int(round(MID_COL - (feet.min() + feet.max()) / 2))
    out[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return out


def build(rows=42):
    raw, _, _ = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))
    raw = raw.copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    common, own = palette(raw)
    fig = snap(raw, common, own)
    fig, dr, dc = cut(fig, rows)
    fig = despeckle(fig)
    fig = close_outline(fig)
    n = len(np.unique(key(fig))) - 1
    print(f"read back {raw.shape[0]} x {raw.shape[1]}; rows dropped {dr}; columns dropped {dc}; "
          f"{fig.shape[0]} x {fig.shape[1]}, {n} colours")
    return on_canvas(fig)


def final():
    """FINAL (letters, '.' clear) on the 128 x 128 canvas."""
    rows = [r.rstrip(chr(13) + chr(10)) for r in open(lp(FINAL), encoding="utf-8") if not r.startswith("#")]
    a = np.zeros((len(rows), max(len(r) for r in rows), 4), np.uint8)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c not in " .":
                a[y, x, :3] = hx(PAL[c])
                a[y, x, 3] = 255
    return on_canvas(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--rows", type=int, default=42)
    ap.add_argument("--final", action="store_true", help="write the approved letter grid FINAL to --out")
    a = ap.parse_args()
    can = final() if a.final else build(a.rows)
    os.makedirs(os.path.dirname(lp(a.out)), exist_ok=True)
    Image.fromarray(can).resize((1024, 1024), Image.NEAREST).save(lp(a.out))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
