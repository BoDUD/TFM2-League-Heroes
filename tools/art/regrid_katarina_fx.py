#!/usr/bin/env python3
"""Katarina's effects read back from the pictures of Codex's step-3 delivery the user pasted into the chat
(assets/source/katarina/codex_fx/pasted; the delivery itself never reached this machine - the user: 「特效你自己处理啊
我发了那么多图给你了」). Writes what tools/art/import_katarina_fx.py reads: codex_fx/pixel_1x/katarina_fx_<name>.png (the
frames side by side, game squares), codex_fx/manifest.json (each frame's pixel_1x_rect) and
codex_fx/pixel_1x/katarina_bake_<key>.png (on the 256 x 170 guide grid).

    python tools/art/regrid_katarina_fx.py [--review DIR]

Two kinds of pictures:
  STRIPS   the 13 sheets pasted one by one (pixel art, transparent): each is Codex's whole sheet scaled, so a game square
           is the image width / (frames x the cell's squares from PROMPTS_FX.md);
  SHEET    the contact sheet of the files (overview_files.webp: every file in a panel, small, on dark grey) for the five
           effects and three bakes pasted only there: a panel's frames sit in equal cells, so a square is the spacing of
           the frames' middles / the cell's squares; the bakes fill their panel's picture area (the guide, 256 x 170).
Every square takes the commonest ramp colour of its pixels (PROMPTS_FX.md's ramps for that effect) when enough of it is
drawn (COVER); the effects the game shows unmirrored on the red side are then made symmetric as PROMPTS_FX.md asked
(left-right, half-turn or top-bottom about the axis the drawing fits best; where only one side has a square, both get it,
where both have one, the brighter).
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
SRC = os.path.join(ROOT, "assets", "source", "katarina")
CODEX = os.path.join(SRC, "codex_fx")
PASTED = os.path.join(CODEX, "pasted")
OUT1X = os.path.join(CODEX, "pixel_1x")

CRIMSON = ["FFFFFF", "FFE3E6", "FF7A84", "E8283C", "A8122A", "5C0A18"]
STEEL = ["FFFFFF", "EEF2F8", "C2CCDA", "8A97AA", "56627A", "2E3442"]      # + the dark hilt
SMOKE = ["FFD6DC", "E8455A", "A8203A", "6C1428", "3A0C18"]
GOLD = ["FFFFFF", "FFF4C8", "FFD86A", "F5A93A", "C8741E"]

# name -> (file, frames, cell squares (w, h), ramps, symmetry)
STRIPS = {
    "q_hit": ("q_hit.webp", 4, (14, 14), CRIMSON + STEEL, "lr"),
    "a_hit": ("a_hit.webp", 4, (14, 14), CRIMSON, "lr"),
    "r_dagger": ("r_dagger.webp", 2, (12, 6), STEEL + CRIMSON, "ud"),
    "q_arc": ("q_arc.webp", 5, (10, 32), STEEL + CRIMSON, "lr"),
    "p_hit": ("p_hit.webp", 3, (14, 10), CRIMSON, "lr"),
    "e_hit": ("e_hit.webp", 4, (16, 16), CRIMSON + SMOKE, "lr"),
    "r_hit": ("r_hit.webp", 3, (10, 10), CRIMSON, "lr"),
    "e_out": ("e_out.webp", 5, (22, 32), SMOKE + CRIMSON, "lr"),
    "e_in": ("e_in.webp", 4, (24, 26), SMOKE + CRIMSON, "lr"),
    "w_toss": ("w_toss.png", 6, (10, 42), STEEL + CRIMSON, "lr"),
    "d_fall": ("d_fall.webp", 4, (16, 24), STEEL + GOLD + CRIMSON, "lr"),
    "d_stuck": ("d_stuck.webp", 4, (12, 16), STEEL + GOLD, "lr"),
    "p_reset": ("p_reset.webp", 5, (28, 36), CRIMSON, "lr"),
}
WIDE = {"r_dagger": 14, "p_hit": 12, "r_hit": 8}   # squares across the widest frame (PROMPTS_FX.md)
PAD = 8                           # room round a frame for the symmetry's shift
BRIGHT = 0.5                      # how far a square's colour goes from its average towards its brightest quarter
# name -> (file, panel (x0, y0, x1, y1) in the picture, frames, cell squares, ramps, symmetry)
SHEET = {
    "q_blade": ("overview_labelled.webp", (20, 15, 530, 128), 4, (13, 13), STEEL + CRIMSON, "pt"),
    "spin": ("overview_files.webp", (8, 392, 1122, 470), 5, (64, 30), CRIMSON + STEEL, "lr"),
    "r_lotus": ("overview_files.webp", (9, 496, 1122, 611), 6, (54, 34), CRIMSON + STEEL, "lr"),
    "w_ms": ("overview_files.webp", (7, 638, 311, 745), 4, (22, 10), CRIMSON, "lr"),
    "r_gw": ("overview_files.webp", (320, 638, 574, 744), 4, (12, 12), CRIMSON, "lr"),
}
# the contact sheet's pictures are soft (glow, half-transparent edges): only their solid middles count, and the glow's
# darkest wine shades go (they filled the rings' empty middles)
SOFT_SOLID = 200
SOFT_DROP = ("5C0A18", "3A0C18", "6C1428")
BY_RUNS = {"q_blade"}
MID_GAP = {"spin": (12, 5), "r_lotus": (12, 6)}    # (squares wide, the ring's front rows kept)
LABEL = 0                         # rows of a panel its label may take (the panels above start under their labels)
# key -> (width in guide squares, the tip's place from the cyan cross): the thrust from her hand to 6 past the dagger's
# point; the throw arc from over her shoulder to 8 past the empty hand; the slash arc from low behind her up to the point
BAKE_FIT = {"a_slash_3": (40, (6, 0)), "q_throw_3": (46, (8, 0)), "e_slash_2": (44, (0, 0))}
# key -> panel of the picture area (the guide's 256 x 170 squares)
BAKE_PANEL = {"a_slash_3": (581, 634, 754, 744), "q_throw_3": (760, 634, 942, 744), "e_slash_2": (951, 634, 1117, 744)}
COVER = 0.3                       # a square is drawn when this share of its pixels is


def lp(p):
    return p


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def snap_table(ramps):
    pal = np.array(sorted({rgb(h) for h in ramps}), float)
    return pal


def snap(px, pal):
    """Nearest ramp colour (weighted RGB) for every pixel row of px (N x 3)."""
    w = np.array([2.0, 4.0, 3.0])
    d = (((px[:, None, :] - pal[None, :, :]) ** 2) * w).sum(-1)
    return d.argmin(1)


def regrid(a, s, ramps, ox=0.0, oy=0.0, cover=COVER, solid=128, drop=()):
    """The picture a (RGBA) on squares of s pixels from (ox, oy): each square drawn when cover of its pixels is, in the
    average colour of its drawn pixels pushed towards its brightest ones (the white cores stay) and snapped to the
    ramps."""
    pal = snap_table(ramps)
    H, W = a.shape[:2]
    nx, ny = int(round((W - ox) / s)), int(round((H - oy) / s))
    out = np.zeros((ny, nx, 4), np.uint8)
    op = a[..., 3] > solid
    lu = a[..., :3].astype(float) @ np.array([0.3, 0.59, 0.11])
    for j in range(ny):
        y0, y1 = int(round(oy + j * s)), int(round(oy + (j + 1) * s))
        for i in range(nx):
            x0, x1 = int(round(ox + i * s)), int(round(ox + (i + 1) * s))
            blk = op[y0:y1, x0:x1]
            if blk.size == 0 or blk.mean() < cover:
                continue
            px = a[y0:y1, x0:x1][blk][:, :3].astype(float)
            l = lu[y0:y1, x0:x1][blk]
            top = px[l >= np.percentile(l, 75)].mean(0)
            c = BRIGHT * top + (1 - BRIGHT) * px.mean(0)
            k = snap(c[None], pal)[0]
            if "%02X%02X%02X" % tuple(int(v) for v in pal[k]) in drop:
                continue
            out[j, i, :3] = pal[k]
            out[j, i, 3] = 255
    return out


def lum(c):
    return c[..., 0] * 0.3 + c[..., 1] * 0.59 + c[..., 2] * 0.11


def symmetric(frames, kind):
    """The frames made symmetric about one shared axis (the one the drawings fit best)."""
    if kind is None:
        return frames
    frames = [np.pad(f, ((PAD, PAD), (PAD, PAD), (0, 0))) for f in frames]
    H, W = frames[0].shape[:2]
    flip = {"lr": lambda f: f[:, ::-1], "ud": lambda f: f[::-1], "pt": lambda f: f[::-1, ::-1]}[kind]

    def shifted(f, dx, dy):
        g = np.zeros_like(f)
        ys, xs = slice(max(0, dy), H + min(0, dy)), slice(max(0, dx), W + min(0, dx))
        ys0, xs0 = slice(max(0, -dy), H + min(0, -dy)), slice(max(0, -dx), W + min(0, -dx))
        g[ys, xs] = f[ys0, xs0]
        return g

    best = None
    for dx in (range(-6, 7) if kind in ("lr", "pt") else [0]):
        for dy in (range(-6, 7) if kind in ("ud", "pt") else [0]):
            sc = 0
            for f in frames:
                m = flip(shifted(f, dx, dy))[..., 3] > 0
                o = shifted(f, dx, dy)[..., 3] > 0
                sc += (m & o).sum()
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
    _, dx, dy = best
    out = []
    for f in frames:
        g = shifted(f, dx, dy)
        m = flip(g)
        take = (m[..., 3] > 0) & ((g[..., 3] == 0) | (lum(m.astype(float)) > lum(g.astype(float))))
        g = g.copy()
        g[take] = m[take]
        out.append(g)
    return trim(out)


def trim(frames):
    """Rows and columns no frame draws on, off every frame alike."""
    op = np.zeros(frames[0].shape[:2], bool)
    for f in frames:
        op |= f[..., 3] > 0
    ys, xs = np.nonzero(op.any(1))[0], np.nonzero(op.any(0))[0]
    return [f[ys.min():ys.max() + 1, xs.min():xs.max() + 1] for f in frames]


def cells_of(grid, n, cw):
    return [grid[:, k * cw:(k + 1) * cw].copy() for k in range(n)]


def trim_rows(frames):
    """Rows no frame draws on, off the top and bottom of every frame alike (the cells keep their bottom: feet anchors use
    the lowest drawn row, so only empty rows go)."""
    rows = np.zeros(frames[0].shape[0], bool)
    for f in frames:
        rows |= (f[..., 3] > 0).any(1)
    ys = np.nonzero(rows)[0]
    return [f[ys.min():ys.max() + 1] for f in frames]


def strip(name):
    fn, n, (cw, ch), ramps, sym = STRIPS[name]
    a = np.asarray(Image.open(os.path.join(PASTED, fn)).convert("RGBA")).astype(np.uint8)
    s = a.shape[1] / (n * cw)
    if name in WIDE:
        # the widest frame's drawing = PROMPTS_FX.md's width; cells from the frames' spacing
        cell = a.shape[1] / n
        widest = max(np.ptp(np.nonzero((a[:, int(k * cell):int((k + 1) * cell), 3] > 128).any(0))[0]) + 1
                     for k in range(n))
        s = widest / WIDE[name]
        cw = int(round(cell / s))
        grid = regrid(a, s, ramps)
        fr = [grid[:, int(round(k * cell / s)):int(round(k * cell / s)) + cw].copy() for k in range(n)]
        return symmetric(trim_rows(fr), sym), s
    grid = regrid(a, s, ramps)
    fr = cells_of(grid, n, cw)
    return symmetric(trim_rows(fr), sym), s


def opaque_cols(a):
    return (a[..., 3] > 128).any(0)


def runs(mask, gap):
    """Runs of True in mask, joined over gaps shorter than gap."""
    xs = np.nonzero(mask)[0]
    out = []
    for x in xs:
        if out and x - out[-1][1] <= gap:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def from_sheet(name):
    fn, (x0, y0, x1, y1), n, (cw, ch), ramps, sym = SHEET[name]
    a = np.asarray(Image.open(os.path.join(PASTED, fn)).convert("RGBA")).astype(np.uint8)[y0:y1, x0:x1].copy()
    lab = np.zeros(a.shape[:2], bool)
    lab[:LABEL] = True                                     # the panel's white label and its grey text, top left
    a[lab & ((a[..., :3].min(-1) > 200) | ((a[..., :3].max(-1) - a[..., :3].min(-1)) < 30))] = 0
    if name in BY_RUNS:
        # frames found by their drawings (the labelled sheet: the row's cells don't fill the picture)
        r = sorted(sorted(runs(opaque_cols(a), 6), key=lambda t: t[1] - t[0], reverse=True)[:n])
        if len(r) != n:
            sys.exit(f"{name}: {len(r)} frames found, not {n}")
        mids = [(u + v) / 2.0 for u, v in r]
        s = float(np.mean(np.diff(mids))) / cw
        starts = [m - cw * s / 2.0 for m in mids]
    else:
        # the frames' cells from the big frames (the last ones: the ring at its fullest): their middles' spacing is a
        # cell, the last one is the last frame
        r = runs(opaque_cols(a), 2)
        wmax = max(v - u for u, v in r)
        mids = [(u + v) / 2.0 for u, v in r if v - u >= 0.6 * wmax]
        d = float(np.median(np.diff(mids)))
        s = d / cw
        starts = [mids[-1] - (n - 1 - k) * d - cw * s / 2.0 for k in range(n)]
        # each drawing (a run of columns) belongs to the frame whose middle is nearest: a neighbour's edge reaching
        # into a cell stays out of it
        owner = np.full(a.shape[1], -1)
        for u, v in r:
            owner[u:v + 1] = int(np.argmin([abs((u + v) / 2.0 - (st + cw * s / 2.0)) for st in starts]))
    solid, drop = (128, ()) if name in BY_RUNS else (SOFT_SOLID, SOFT_DROP)
    frames = []
    for k, ox in enumerate(starts):
        lo, hi = int(max(0, ox)), int(min(a.shape[1], ox + cw * s))
        part = np.zeros((a.shape[0], int(round(cw * s)) + 2, 4), np.uint8)
        src = a[:, lo:hi].copy()
        if name not in BY_RUNS:
            src[:, owner[lo:hi] != k] = 0
        part[:, lo - int(ox):lo - int(ox) + hi - lo] = src
        frames.append(regrid(part, s, ramps, solid=solid, drop=drop)[:, :cw])
    frames = symmetric(trim_rows(frames), sym)
    if name in MID_GAP:
        # her body's place: an upright gap in the middle over the ring's front (PROMPTS_FX.md)
        w, front = MID_GAP[name]
        for f in frames:
            c = f.shape[1] // 2
            f[:f.shape[0] - front, c - w // 2:c + w - w // 2] = 0
    return frames, s


def bake(key):
    """The bake picture fitted onto the guide as PROMPTS_FX.md placed it: the thumbnail's drawing scaled to BAKE_FIT's
    width (guide squares) and its tip (its rightmost drawn column's middle) put that far from the guide's cyan cross
    (the thumbnails do not show where on the guide Codex drew: read as the whole guide, the thrust crossed her body)."""
    x0, y0, x1, y1 = BAKE_PANEL[key]
    a = np.asarray(Image.open(os.path.join(PASTED, "overview_files.webp")).convert("RGBA")).astype(np.uint8)
    a = a[y0:y1, x0:x1].copy()
    a[a[..., 3] < 60] = 0
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    width, (dx, dy) = BAKE_FIT[key]
    f = width / a.shape[1]
    hgt = max(1, int(round(a.shape[0] * f)))
    big = np.asarray(Image.fromarray(a).resize((width * 4, hgt * 4), Image.LANCZOS))
    ramps = CRIMSON + SMOKE + STEEL if key == "q_throw_3" else CRIMSON + SMOKE
    g = regrid(big, 4.0, ramps, solid=SOFT_SOLID, drop=SOFT_DROP)
    with open(os.path.join(SRC, "fx_bake_cells.json"), encoding="utf-8") as fh:
        cell = json.load(fh)[key]
    W, H = cell["canvas"]
    cx, cy = cell["cyan"]
    gy, gx = np.nonzero(g[..., 3] > 0)
    tx = gx.max()
    ty = int(round(gy[gx >= tx - 1].mean()))
    out = np.zeros((H, W, 4), np.uint8)
    ox, oy = cx + dx - tx, cy + dy - ty
    for y, x in zip(gy, gx):
        X, Y = x + ox, y + oy
        if 0 <= X < W and 0 <= Y < H:
            out[Y, X] = g[y, x]
    return out


def write(name, frames):
    H = max(f.shape[0] for f in frames)
    W = sum(f.shape[1] for f in frames)
    sheet = np.zeros((H, W, 4), np.uint8)
    rects, x = [], 0
    for f in frames:
        sheet[H - f.shape[0]:, x:x + f.shape[1]] = f
        rects.append([x, 0, f.shape[1], H])
        x += f.shape[1]
    Image.fromarray(sheet).save(os.path.join(OUT1X, f"katarina_fx_{name}.png"))
    return {"file": f"katarina_fx_{name}.png", "frames": [{"pixel_1x_rect": r} for r in rects]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(OUT1X, exist_ok=True)
    man_path = os.path.join(CODEX, "manifest.json")
    man = json.load(open(man_path, encoding="utf-8")) if os.path.exists(man_path) else {"assets": []}
    items = {it["file"]: it for it in man["assets"]}
    done = {}
    for name in STRIPS:
        if a.only and name not in a.only:
            continue
        fr, s = strip(name)
        items[f"katarina_fx_{name}.png"] = write(name, fr)
        done[name] = fr
        print(f"{name:9s} {s:5.2f} px a square, frames {[f.shape[1::-1] for f in fr]}")
    for name in SHEET:
        if a.only and name not in a.only:
            continue
        fr, s = from_sheet(name)
        items[f"katarina_fx_{name}.png"] = write(name, fr)
        done[name] = fr
        print(f"{name:9s} {s:5.2f} px a square, frames {[f.shape[1::-1] for f in fr]}")
    for key in BAKE_PANEL:
        if a.only and key not in a.only:
            continue
        b = bake(key)
        Image.fromarray(b).save(os.path.join(OUT1X, f"katarina_bake_{key}.png"))
        done[key] = [b]
        print(f"{key:9s} {b.shape[1::-1]}, {int((b[..., 3] > 0).sum())} squares")
    man["assets"] = list(items.values())
    json.dump(man, open(man_path, "w", encoding="utf-8"), indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        rows = []
        for name, fr in done.items():
            z = 8
            W = sum(f.shape[1] * z + 6 for f in fr)
            H = max(f.shape[0] for f in fr) * z
            im = Image.new("RGB", (W, H + 4), (52, 60, 46))
            x = 0
            for f in fr:
                t = Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST)
                im.paste(t, (x, H - t.height), t)
                x += t.width + 6
            rows.append((name, im))
        Wt = max(r.width for _, r in rows) + 90
        sheet = Image.new("RGB", (Wt, sum(r.height + 6 for _, r in rows)), (20, 20, 20))
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r, (90, y))
            d.text((4, y + 4), name, fill=(255, 255, 0))
            y += r.height + 6
        sheet.save(os.path.join(a.review, "regrid.png"))
        print(os.path.join(a.review, "regrid.png"), sheet.size)


if __name__ == "__main__":
    main()
