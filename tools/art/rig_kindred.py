#!/usr/bin/env python3
"""Kindred's game sheets from her dense frames (tools/art/import_kindred_strips.py -> assets/source/kindred/frames) and
the designs (tools/art/design_kindred_hd.py -> assets/source/kindred/hd) - league_nilah's way (tools/art/rig_nilah.py).

    python tools/art/rig_kindred.py [--review DIR]

Density: the user kept Codex's picture B read back square for square and picked 34 game rows from the mask's ear tips
to the hooves (2026-10-14, 「模型还得缩小」: 154 squares -> 34 rows, ORIG_PPU 4.53), with Zeri's density at the end
(「泽丽密度（最后统一重做）」): tools/art/ppu_restyle.py RESTYLE["kindred"] brings these frames to it.
Two figures in one sprite (the user's pick: the Wolf drawn into Lamb's frames):
  idle   the front design (Lamb 3/4 front, the Wolf behind her hips; hd/front_lamb.png + front_wolf.png): Lamb's upper
         body breathes (everything above WAIST up BREATH rows, the squares it uncovers taking the colour under them),
         the Wolf floats on its own (FLOAT, half a beat later);
  hit    the side design (hd/side.png) moved HIT_DX back, a white flash on the first frame, the Wolf with it;
  the rest  Lamb's action frames as imported, the Wolf's profile (hd/side_wolf.png) behind her, floating FLOAT rows by
         frame: in the run trailing at her heels (WOLF_RUN; at her hips, as in the idle, her long tail hid it in every
         action - 2026-10-14 trials); in the other actions under her tail against her back (WOLF_ROW / WOLF_TUCK: a fixed
         place left it adrift where she stands back, ult_4, dead_1), at least WOLF_SHOW of it showing (skill_5 had it
         blink out behind the tail) and raised with her in Q's leap; in the death it shrinks away where it shows while
         it fades (DEAD_FADE).
Writes assets/source/ppu/orig/kindred_<tag>.png / .json (the dense frames, each round(ORIG_PPU x its 1x frame) round
the pivot) and league/champions/league_kindred#sheet.png / #anim.fanim (the 1x tags: each 1x pixel the commonest colour
of its squares; the fallback without league.dll).
"""
import argparse
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
import import_kindred_strips as I  # noqa: E402

PPU = 154 / 34                    # dense squares a game pixel: the mask's ear tips to the hooves, 154 squares = 34 rows
FEET = 11                         # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
STEM = os.path.join(ROOT, "league", "champions", "league_kindred")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
HD = os.path.join(I.SRC, "hd")
FRONT_SOLE, FRONT_MID = 165, 162  # the front / side designs' hooves row and standing column
WAIST = 112                       # the front design's row under the fur skirt's top: Lamb's upper body above it breathes
BREATH = [0, 1, 1, 1, 0, 0]
FLOAT = [0, 1, 2, 2, 1, 0]        # the Wolf's float (rows up), by frame, looping
BREATH_MS = 170
HIT_DX = 4
HIT = [(HIT_DX, True, 90), (HIT_DX // 2, False, 120)]
WOLF_RUN = (-38, -78)             # the run: the Wolf's nose (rows, cols) from the hooves' row / the standing column -
                                  # trailing at her heels while she runs
WOLF_ROW = -32                    # the other actions: the nose this many rows over the hooves' row, its column at her
WOLF_TUCK = 6                     # silhouette's back edge at that height, tucked this many squares in (smoothed over
WOLF_STEP = 30                    # the frames of the action, at most WOLF_STEP squares a frame): with her, never adrift
WOLF_SHOW = 0.55                  # ... and at least this share of it showing past her tail (farther out where it would not)
DEAD_FADE = [1.0, 0.75, 0.45, 0.0, 0.0, 0.0]   # the death: the Wolf stays where it was in the first frame and fades by
DEAD_SINK = [0, 4, 8, 0, 0, 0]                  # shrinking (pixel_down.pixelate) and sinking, gone from the fourth
TIMING = {"run": [125] * 8, "attack": [80, 80, 90, 90, 100], "skill": [60, 60, 60, 60, 80, 100],
          "skill2": [80, 80, 90, 90, 100], "w_cast": [80, 80, 100, 100], "ult": [80, 80, 80, 100, 100, 100],
          "dead": [100, 100, 100, 120, 150, 400]}
ORDER = ["idle", "run", "attack", "skill", "skill2", "w_cast", "ult", "hit", "dead"]


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def over(dst, src, x0, y0):
    """src drawn over dst with its top-left at (x0, y0) (clipped)."""
    H, W = dst.shape[:2]
    h, w = src.shape[:2]
    ys, xs = np.nonzero(src[..., 3] > 0)
    r, c = ys + y0, xs + x0
    ok = (r >= 0) & (r < H) & (c >= 0) & (c < W)
    dst[r[ok], c[ok]] = src[ys[ok], xs[ok]]


def under(dst, src, x0, y0):
    """src drawn under dst (only where dst is clear)."""
    H, W = dst.shape[:2]
    ys, xs = np.nonzero(src[..., 3] > 0)
    r, c = ys + y0, xs + x0
    ok = (r >= 0) & (r < H) & (c >= 0) & (c < W)
    r, c, ys, xs = r[ok], c[ok], ys[ok], xs[ok]
    free = dst[r, c, 3] == 0
    dst[r[free], c[free]] = src[ys[free], xs[free]]


def wolf_side(k=1.0):
    """The Wolf's profile (hd/side_wolf.png), brought to k of its size for the death's fade; (picture, nose row)."""
    w = rgba(os.path.join(HD, "side_wolf.png"))
    if k != 1.0:
        import pixel_down as PD
        pal = np.unique(w[w[..., 3] > 0][:, :3], axis=0).astype(float)
        w, _ = PD.pixelate(w, k, (w.shape[1], w.shape[0] // 2), PD.edge_colour(w), pal=pal)
        ys, xs = np.nonzero(w[..., 3] > 0)
        w = w[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    nose_row = int(np.nonzero(w[:, -1, 3])[0].mean())
    return w, nose_row


def with_wolf(lamb, nose_col, nose_row, k=1.0):
    """Lamb's frame (on the import canvas) with the Wolf's profile behind her, its nose at (nose_row, nose_col)."""
    if k <= 0:
        return lamb.copy()
    w, nr = wolf_side(k)
    out = lamb.copy()
    under(out, w, nose_col - w.shape[1] + 1, nose_row - nr)
    return out


def contact(lamb, row):
    """Her silhouette's back edge at the Wolf's height: the median leftmost drawn column of the rows round `row`."""
    op = lamb[..., 3] > 0
    lefts = [np.nonzero(op[r])[0].min() for r in range(row - 8, row + 9) if op[r].any()]
    return int(np.median(lefts)) if lefts else I.PIV + WOLF_RUN[1]


def shown(lamb, wolf, nose_col, top):
    """The share of the Wolf's squares (its mask, nose at nose_col, top row at top) that Lamb leaves clear."""
    ys, xs = np.nonzero(wolf)
    r, c = ys + top, xs + nose_col - wolf.shape[1] + 1
    ok = (r >= 0) & (r < lamb.shape[0]) & (c >= 0) & (c < lamb.shape[1])
    return float((lamb[r[ok], c[ok], 3] == 0).sum()) / len(ys)


def nose_cols(lambs, rows):
    """Per frame: the back edge tucked WOLF_TUCK in - farther out while less than WOLF_SHOW of the Wolf shows past her
    tail (skill_5: 16 %, it blinked out) - averaged with the frames beside it, at most WOLF_STEP a frame; the averaging
    and the step only ever move it out, never back behind her."""
    w, nr = wolf_side()
    wm = w[..., 3] > 0
    raw = []
    for a, row in zip(lambs, rows):
        c = contact(a, row) + WOLF_TUCK
        while c > w.shape[1] // 2 and shown(a, wm, c, row - nr) < WOLF_SHOW:
            c -= 1
        raw.append(c)
    n = len(raw)
    sm = [min(r, round(np.mean(raw[max(0, i - 1):i + 2]))) for i, r in enumerate(raw)]
    for i in range(1, n):
        sm[i] = min(sm[i], sm[i - 1] + WOLF_STEP)
    for i in range(n - 2, -1, -1):
        sm[i] = min(sm[i], sm[i + 1] + WOLF_STEP)
    return [int(s) for s in sm]


def front_frames():
    """The idle: the front design on the import canvas (hooves on SOLE, standing column on PIV)."""
    lamb = rgba(os.path.join(HD, "front_lamb.png"))
    wolf = rgba(os.path.join(HD, "front_wolf.png"))
    ox, oy = I.PIV - FRONT_MID, I.SOLE - FRONT_SOLE
    upper = np.zeros(lamb.shape[:2], bool)
    upper[:WAIST] = lamb[:WAIST, :, 3] > 0
    frames = []
    for k, b in enumerate(BREATH):
        can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
        body = breathe(lamb, upper, b)
        over(can, body, ox, oy)
        under(can, wolf, ox, oy - FLOAT[(k + 1) % len(FLOAT)])
        frames.append((can, BREATH_MS))
    return frames


def breathe(a, mask, k):
    """The masked squares moved k rows up; the squares they uncover take the colour of the square under them."""
    if k == 0:
        return a.copy()
    out = a.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    rest = out.copy()
    out[ys - k, xs] = a[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            below = y + 1
            while below < a.shape[0] and out[below, x, 3] == 0 and mask[below, x]:
                below += 1
            if below < a.shape[0] and rest[below, x, 3] > 0:
                out[y, x] = rest[below, x]
            elif below < a.shape[0] and out[below, x, 3] > 0:
                out[y, x] = out[below, x]
    return out


def hit_frames():
    side = rgba(os.path.join(HD, "side.png"))
    can = np.zeros((I.ROWS, I.COLS, 4), np.uint8)
    over(can, side, I.PIV - FRONT_MID, I.SOLE - FRONT_SOLE)
    row = I.SOLE + WOLF_ROW
    can = with_wolf(can, nose_cols([can], [row])[0], row)
    out = []
    for dx, flash, ms in HIT:
        a = np.roll(can, -dx, axis=1)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, ms))
    return out


def lift(lamb, name):
    """Rows the airborne frames (import_kindred_strips.AIR: Q's leap) have her hooves over the ground: the Wolf rises
    with her (on the ground row it hung a gap below her tail, skill_3 / skill_4)."""
    if name not in I.AIR:
        return 0
    pal = I.palette()
    hoof = np.zeros(lamb.shape[:2], bool)
    for i in I.HOOF:
        hoof |= (lamb[..., 3] > 0) & np.all(lamb[..., :3] == pal[i][:3], axis=-1)
    return I.SOLE - int(np.nonzero(hoof.any(1))[0].max()) if hoof.any() else 0


def action_frames(tag):
    lambs = [rgba(os.path.join(I.OUT, f"kindred_{tag}_{k}.png")) for k in range(1, len(TIMING[tag]) + 1)]
    out = []
    if tag == "run":
        for k, (a, ms) in enumerate(zip(lambs, TIMING[tag])):
            row = I.SOLE + WOLF_RUN[0] - FLOAT[k % len(FLOAT)]
            out.append((with_wolf(a, I.PIV + WOLF_RUN[1], row), ms))
        return out
    row = I.SOLE + WOLF_ROW
    rows = [row + DEAD_SINK[k] if tag == "dead" else row - FLOAT[k % len(FLOAT)] - lift(a, f"{tag}_{k + 1}")
            for k, a in enumerate(lambs)]
    # the death keeps one place, where it shows in each frame it fades in (the lying frames' far tail would pull it
    # off her; at the first frame's own place her kneeling body hid it from the second on)
    fade = sum(1 for f in DEAD_FADE if f > 0)
    cols = [min(nose_cols(lambs[:fade], rows[:fade]))] if tag == "dead" else nose_cols(lambs, rows)
    for k, (a, ms) in enumerate(zip(lambs, TIMING[tag])):
        if tag == "dead":
            out.append((with_wolf(a, cols[0], rows[k], DEAD_FADE[k]), ms))
        else:
            out.append((with_wolf(a, cols[k], rows[k]), ms))
    return out


def one_of(can, px, py, hw, hh, need=0.5):
    """The 1x frame (2 hw + 1 by 2 hh + 1, centred on (px, py)): every pixel the commonest colour of the dense squares
    under it, clear when fewer than `need` of them are drawn."""
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


def down(can):
    """The dense canvas -> (the 1x frame centred on the pivot, the dense frame round(PPU x its size)). The pivot: the
    standing column's centre, FEET 1x rows above the hooves' bottom edge."""
    px, py = I.PIV + 0.5, I.SOLE + 1 - FEET * PPU
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


def actions():
    out = {"idle": front_frames(), "hit": hit_frames()}
    for tag in TIMING:
        out[tag] = action_frames(tag)
    return {t: out[t] for t in ORDER}


def pinholes(hero="kindred", most=3):
    """After tools/art/ppu_restyle.py: enclosed holes of at most `most` pixels in the restyled strips
    (assets/source/ppu/kindred_<tag>.png - the hd_ frames ppu_hd.py reads) take the commonest colour round them.
    Codex's fur and the Wolf's mane carry such pinholes, the design too; at 2.86 a game pixel they read as specks of
    ground (memory gap-check)."""
    from scipy import ndimage
    src = os.path.join(ROOT, "assets", "source", "ppu")
    import ppu_hd as P
    n_all, hds = 0, {}
    for tag in ORDER:
        path = os.path.join(src, f"{hero}_{tag}.png")
        meta = json.load(open(os.path.join(src, f"{hero}_{tag}.json"), encoding="utf-8"))
        strip = np.asarray(Image.open(path).convert("RGBA")).copy()
        x, hds[tag] = 0, []
        for W, H in meta["sizes"]:
            a = strip[:H, x:x + W]
            op = a[..., 3] > 0
            holes = ndimage.binary_fill_holes(op) & ~op
            lbl, n = ndimage.label(holes)
            for k in range(1, n + 1):
                m = lbl == k
                if m.sum() > most:
                    continue
                ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
                cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
                a[m, :3] = cols[cnt.argmax()]
                a[m, 3] = 255
                n_all += int(m.sum())
            hds[tag].append(a)
            x += W + 1
        Image.fromarray(strip).save(path)
    print(f"{hero}: {n_all} pinhole pixels filled")
    # the 1x tags (the fallback without league.dll) are brought down from the frames before the restyle, whose grown
    # outline closes thin gaps: their pinholes over squares the restyled frame draws take that frame's commonest colour
    # there (gaps the hd frame shows stay open)
    k1, n1 = P.PPU[hero], 0
    sheet = P.read_sheet(STEM)
    for tag in ORDER:
        for (a, _), b in zip(sheet[tag], hds[tag]):
            op = a[..., 3] > 0
            holes = ndimage.binary_fill_holes(op) & ~op
            lbl, n = ndimage.label(holes)
            for k in range(1, n + 1):
                m = lbl == k
                if m.sum() > most:
                    continue
                for y, x in zip(*np.nonzero(m)):
                    hx = int(round((x - a.shape[1] / 2) * k1 + b.shape[1] / 2))
                    hy = int(round((y - a.shape[0] / 2) * k1 + b.shape[0] / 2))
                    blk = b[max(0, hy):hy + int(round(k1)), max(0, hx):hx + int(round(k1))].reshape(-1, 4)
                    if not len(blk) or (blk[:, 3] > 0).mean() < 0.5:
                        continue
                    cols, cnt = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
                    a[y, x, :3] = cols[cnt.argmax()]
                    a[y, x, 3] = 255
                    n1 += 1
    G.write_sheet(STEM, sheet)
    print(f"{hero}: {n1} 1x pinhole pixels filled from the restyled frames")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's dense frames at 2x here")
    ap.add_argument("--pinholes", action="store_true",
                    help="only fill the pinholes of the restyled strips (after ppu_restyle.py, before ppu_hd.py)")
    a = ap.parse_args()
    if a.pinholes:
        pinholes()
        return
    acts = actions()
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag, frames in acts.items():
        ones, hds = [], []
        for can, t in frames:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"kindred_{tag}.png"))
        with open(os.path.join(ORIG, f"kindred_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": round(PPU, 4)}, f)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            Z = 2
            tiles = [Image.fromarray(c[0]) for c in frames]
            w, h = tiles[0].size
            big = Image.new("RGBA", (len(tiles) * w * Z, h * Z), (96, 112, 96, 255))
            for k, t in enumerate(tiles):
                big.alpha_composite(t.resize((w * Z, h * Z), Image.NEAREST), (k * w * Z, 0))
            big.convert("RGB").save(os.path.join(a.review, f"kindred_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_kindred#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
