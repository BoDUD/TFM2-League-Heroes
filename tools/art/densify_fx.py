#!/usr/bin/env python3
"""Dense (PPU) twins of a hero's 1x effect sheets, read back from Codex's raw drawings.

    python tools/art/densify_fx.py --hero akshan [--ppu 2] [--zoom r_boom=1.44@0,7] [--skip SHEET ...]
                                   [--out DIR] [--report out.json] [--review out.png]

The user, 2026-11-09: 「目前完成的所有英雄被反映特效贴图做的非常粗糙 ... 能不能利用PPU来做精致一点？」, then 「继续完成别的英雄的
技能特效的修复」. Every effect was cut at 1x - a game pixel a square - out of Codex drawings 500-2000 px a frame
(assets/source/<hero>/codex_fx/**/raw), so an 18 x 18 hit kept little of them. This tool keeps each sheet's 1x frames
as they are (the fallback the game shows with league.dll's hook off) and adds, beside every tag, its `hd_` twin PPU
times the size, redrawn from the raw:

1. The hero's Codex deliveries, read whatever way each was written (deliveries): every 1x strip (pixel_1x/, or a
   preview at the top of the delivery, k x k blocks a game pixel, brought back to 1x) with its raw (named in the
   manifest, or raw/<strip or picture>[-original|-repair|-generated|_generated].png), its frame count from the
   manifest entry naming it, and the raw's frame cuts (raw_rects): the manifest's own (a rectangle a frame, cut
   positions, a contact sheet's grid with its row cuts, crops - a dozen ways of writing them; trusted), else guessed
   ways - equal cuts across, the gaps between the drawings, a contact sheet's drawings, its equal grids - which a fit
   may squeeze only a little (2026-11-09: Scuttle Crab's and Sevika's 2 x 2 sheets read as strips and squeezed onto
   the frames came out as streaks). Older effect drawings with no 1x strip (assets/source/<hero>/*fx*.png that are
   real drawings, not pixel previews: Lux, Garen, Ashe, Xerath ...) come in cut at their gaps, for step 3 only.
2. Each 1x frame is matched to the Codex cell it was cut from: the cell as delivered, its middle column or row doubled
   (the importers' `odd`), or doubled in size (import_gragas.py TWICE) - the frame's drawn squares equal to the cell's.
   A picture's frames are fitted onto their cells together (one scale - two, across and down, when Codex squeezed it
   into its cell - and offset), then each frame on its own (Codex registered some frame by frame): the raw's drawn
   pixels (alpha >= FG), area-averaged over each square, cover the squares the cell draws (coverage >= COVER, the rule
   Codex cut the 1x cells by) - scored by F-score with a square's slip forgiven.
3. A frame no cell matched (resized, recoloured or mended by its importer: Aurelion Sol's stacks, Bard's doors) is
   fitted straight onto the game frame from the picture its tag is named after (the likeliest raw frames first).
4. With the fit each frame is redrawn PPU times finer as its own 1x frame, refined (refine): the raw's drawn pixels
   draw the fine pixels, but only within a fine pixel of the 1x frame's squares and at least FILL of their area (the
   raw's glows and specks Codex left out stay out; its sparks keep their weight), each fine pixel coloured by a vote of
   its raw pixels over the 1x colours of its square and the eight round it, its own square's first - the 1x frame's
   look, finer (the user: 「别给我整的更差了 我要的是质量更好的」). Symmetric frames stay symmetric.
5. A tag is redrawn from its raws only when all its drawn frames passed the gate (specks aside: an animation half
   redrawn is no better) and its pictures are fine enough at 1x - at most K_MAX raw pixels a game pixel: a smaller
   effect Codex redesigned as it cut it to 1x, and its raw redrawn finer looks like another drawing (Sevika's hits,
   2026-11-09). Every other tag is its 1x frames Scale2x'd (scale2x: the same design, rounder at its edges, no colour
   made up); tools/art/pack_fx_redraw.py packs those for Codex to redraw.

`--zoom tag=z` redraws a tag bigger about the spot it is played at (its ground centre or core), both its 1x frames and
its dense ones - its 1x frames zoomed, refined at 1x, then PPU times finer (zoom_frames) - when all its frames passed: the user, 2026-11-09, on the ults (「有些大招范围起码要按照英雄联盟的范围来适当缩小还原吧」
「如果按照codex的范围 实在太小了」, then 「只改画面，判定不动」): an area's picture as wide as the area the kit hits -
its radius plus a champion's 15000-unit body each side, 1000 units a game pixel.

Writes <out>/<sheet>#sheet.png + #anim.fanim (default: league/effects) with every tag, its hd_ twin and an `idle` /
`hd_idle` pair (hd_engine's anim-table densify needs them: hd_idle exactly PPU times as wide).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

FG = 0.5          # a raw pixel is drawn from this alpha
COVER = 0.25      # a square is drawn when this much of it is covered by drawn raw pixels (Codex's 1x rule)
MIN_FIT = 0.7     # a frame fitted worse than this (F-score, a square's slip forgiven) is not redrawn from its raw
GUESS_ASPECT = 1.35    # a guessed way's frames may be squeezed this much at most (across against down)
TRUSTED_ASPECT = 2.2   # the manifest's own way's (Codex squeezed Aurora's realm 1.8 times into its cells)
# The gate a frame passes to be redrawn from its raw (the user, 2026-11-09, on Scuttle Crab's and Sevika's streaks:
# 「杜绝这种情况啊」「英雄联盟的也是 别给我整的更差了 我要的是质量更好的」): the raw at its fit, read back at 1x by Codex's own
# rule, draws the 1x frame's squares (F-score with a square's slip forgiven) in about its colours (a gross mismatch only:
# refine() takes every colour from the 1x frame), and the finished dense frame read back at 1x is the 1x frame (the
# round trip). Plain IoU and the colour mix are measured (the report) but no gate: good frames span the same range.
GATE_F = 0.7
GATE_IOU = 0.0
GATE_GAP = 0.35    # the raw's own colours this far from the 1x frame's: not its drawing (Xerath's bolt for his smoke)
GATE_TV = 1.0
GATE_RT = 0.3
GATE_OUT = 1.0
SPECK = 12        # a frame of fewer squares is a speck: its squares do not keep its tag at 1x
PRIOR = 0.3       # a fine pixel keeps its 1x square's colour unless another has this share of the votes more (refine)
FILL = 0.8        # a dense frame draws at least this share of its 1x frame's area (refine)
SOLID = 0.45      # a fine pixel is drawn when the game pixel round it is this covered (refine: solid parts stay solid)
K_MAX = 18.0      # a tag is redrawn from its raw only where a game pixel is at most this many raw pixels across
FAINT = 0.25      # a fine pixel takes another colour than its 1x square's only from votes over this share of its area
MAX_X2_TEXELS = 2_000_000   # a sheet only Scale2x'd is written only up to this many 1x frame texels
for _k in ("GATE_F", "GATE_IOU", "GATE_GAP", "GATE_RT", "GATE_OUT", "GATE_TV", "GUESS_ASPECT", "TRUSTED_ASPECT",
           "PRIOR", "FILL", "SOLID", "K_MAX", "FAINT"):
    if os.environ.get("DENSIFY_" + _k):
        globals()[_k] = float(os.environ["DENSIFY_" + _k])


# ------------------------------------------------------------------ Codex deliveries
RAW_SUFFIXES = ("", "-original", "-repair", "-generated", "-raw")


def entries_of(obj):
    """every dict inside a manifest's JSON (Codex wrote each delivery's own way: lists under effects / assets / items /
    entries / sheets, or dicts keyed by name)"""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from entries_of(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from entries_of(v)


def entry_for(manifests, file, name):
    """the manifest entry of a pixel_1x strip: the dict naming its file (as `file`, `pixel_1x`, `pixel_1x_file` ...), else
    its picture name (`name`, `tag`, `id`), with a frame count"""
    def frames_of(e):
        f = e.get("frames", e.get("frame_count", e.get("count")))
        return len(f) if isinstance(f, list) else (int(f) if isinstance(f, (int, float)) else None)
    by_file, by_name = None, None
    for m in manifests:
        for e in entries_of(m):
            if frames_of(e) is None:
                continue
            strings = [v for v in e.values() if isinstance(v, str)]
            if by_file is None and any(s == file or s.endswith("/" + file) for s in strings):
                by_file = e
            if by_name is None and any(e.get(k) == name for k in ("name", "tag", "id")):
                by_name = e
    e = by_file or by_name
    return (e, frames_of(e)) if e else (None, None)


def rect(v, W, H):
    """a rectangle as (x0, y0, x1, y1) from [x0, y0, x1, y1], [x, y, w, h] or {x, y, width, height}"""
    if isinstance(v, dict):
        x, y = v.get("x", 0), v.get("y", 0)
        return (x, y, x + v.get("width", v.get("w", 0)), y + v.get("height", v.get("h", 0)))
    x0, y0, a, b = v[:4]
    if a > x0 and b > y0 and a <= W + 1 and b <= H + 1:
        return (x0, y0, a, b)
    return (x0, y0, x0 + a, y0 + b)


def _numbers(v, k=None):
    return isinstance(v, list) and len(v) > 0 and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                                                       for x in v) and (k is None or len(v) == k)


def rects_of(v, W, H):
    """A list of rectangles in the raw (W x H), all read the same way - [x0, y0, x1, y1] or [x, y, w, h] (fractions of
    the raw when no value is over 1), {x, y, width, height}, or {"slot": [...], "crop_in_slot": [...]} (Gangplank's) -
    -> [(x0, y0, x1, y1)] or None. A list each rectangle of which reads both ways is taken the way its rectangles come
    out alike in size (Codex's cells are)."""
    if not v:
        return None
    if all(isinstance(x, dict) for x in v):
        out = []
        for x in v:
            if _numbers(x.get("slot"), 4):
                sx0, sy0, sx1, sy1 = x["slot"]
                c = x.get("crop_in_slot")
                out.append((sx0 + c[0], sy0 + c[1], sx0 + c[2], sy0 + c[3]) if _numbers(c, 4) else (sx0, sy0, sx1, sy1))
            elif all(isinstance(x.get(k), (int, float)) for k in ("x", "y")) and \
                    isinstance(x.get("width", x.get("w")), (int, float)):
                out.append((x["x"], x["y"], x["x"] + x.get("width", x.get("w")), x["y"] + x.get("height", x.get("h"))))
            else:
                return None
        return out
    if not all(_numbers(x, 4) for x in v):
        return None
    vals = [c for x in v for c in x]
    if max(vals) <= 1.0 and max(vals) > 0:
        v = [[x[0] * W, x[1] * H, x[2] * W, x[3] * H] for x in v]
    slack_w, slack_h = W * 1.05 + 1, H * 1.05 + 1
    xyxy = [(x[0], x[1], x[2], x[3]) for x in v]
    xywh = [(x[0], x[1], x[0] + x[2], x[1] + x[3]) for x in v]

    def fits(rs):
        return all(r[2] > r[0] and r[3] > r[1] and r[2] <= slack_w and r[3] <= slack_h for r in rs)

    a, b = fits(xyxy), fits(xywh)
    if a and b:
        def spread(rs):
            ws = np.array([r[2] - r[0] for r in rs], float)
            hs = np.array([r[3] - r[1] for r in rs], float)
            return float(ws.std() / max(1.0, ws.mean()) + hs.std() / max(1.0, hs.mean()))
        return xyxy if spread(xyxy) <= spread(xywh) else xywh
    return xyxy if a else xywh if b else None


def cuts_of(v, size):
    """a list of cut positions (fractions of `size` when none is over 1) -> [floats], increasing, or None"""
    if not _numbers(v) or len(v) < 2:
        return None
    if max(v) <= 1.0:
        v = [x * size for x in v]
    return [float(x) for x in v] if all(b > a for a, b in zip(v[:-1], v[1:])) else None


def grid_rects(n, xs_rows, ys):
    """the first n cells, row by row, of a grid cut at ys (rows) and xs_rows (the column cuts, one list a row)"""
    out = []
    for r in range(len(ys) - 1):
        xs = xs_rows[min(r, len(xs_rows) - 1)]
        for c in range(len(xs) - 1):
            out.append((xs[c], ys[r], xs[c + 1], ys[r + 1]))
    return out[:n] if len(out) >= n else None


RECT_KEYS = ("raw_frame_rects", "source_rectangles", "source_frame_viewports", "source_rects", "source_frame_rects",
             "source_crop_boxes", "source_frame_crop_boxes", "sample_rects", "frame_rectangles_estimate")
FRAME_RECT_KEYS = ("raw_rect", "source_rect", "source_raw_rect", "sourceRect", "rect_raw", "source_rect_raw",
                   "raw_cell_rect", "rect")
XCUT_KEYS = ("source_frame_boundaries", "source_frame_cuts", "source_frame_cuts_x", "source_frame_boundaries_x",
             "raw_cell_boundaries_x", "source_x_boundaries", "source_x_cuts", "raw_column_boundaries")
YCUT_KEYS = ("source_y_cuts", "raw_row_boundaries")
GRID_KEYS = ("source_layout", "source_grid", "raw_grid", "raw_layout", "sourceGridActual", "sourceGrid", "layout_grid",
             "raw_frame_layout", "layout_columns_rows", "working_grid", "raw_working_grid", "generation_grid",
             "generation_layout")
BAND_KEYS = ("source_crop", "source_row_band", "source_viewport", "common_source_viewport", "source_common_crop",
             "source_crop_common", "raw_frame_crop_union", "crop", "readback_crop", "raw_crop_per_cell")
YBAND_KEYS = ("source_vertical_crop", "source_crop_y", "raw_y_crop", "raw_shared_vertical_crop", "source_vertical_band")


def manifest_ways(e, n, W, H):
    """The ways the manifest entry itself cuts its raw into the n frames (Codex wrote it a dozen ways: rectangles a frame,
    cut positions, a contact sheet's grid with its row cuts, crops a cell or across the raw) -> [[n rectangles]]"""
    ways = []
    for k in RECT_KEYS:
        v = e.get(k)
        if isinstance(v, list) and len(v) >= n:
            r = rects_of(v[:n], W, H)
            if r:
                ways.append(r)
    for lst in (e.get("raw_frames"), e.get("frames")):
        if isinstance(lst, list) and len(lst) == n and all(isinstance(x, dict) for x in lst):
            for k in FRAME_RECT_KEYS:
                if all(k in x for x in lst):
                    r = rects_of([x[k] for x in lst], W, H)
                    if r:
                        ways.append(r)
                    break
    # cut positions: across (one list, or one a row) and down
    xs_rows = ys = None
    for k in XCUT_KEYS:
        v = e.get(k)
        if isinstance(v, list) and v and all(isinstance(x, list) for x in v):
            rows = [cuts_of(x, W) for x in v]
            if all(rows):
                xs_rows = rows
                break
        elif cuts_of(v, W):
            xs_rows = [cuts_of(v, W)]
            break
    for k in YCUT_KEYS:
        if cuts_of(e.get(k), H):
            ys = cuts_of(e.get(k), H)
            break
    # a grid: [columns, rows], {"columns", "rows", "row_cuts", "col_cuts"}, or columns / rows in the entry
    grid = None
    for k in GRID_KEYS:
        g = e.get(k)
        if isinstance(g, dict):
            c, r = g.get("columns", g.get("cols")), g.get("rows")
            if isinstance(c, int) and isinstance(r, int):
                grid = (c, r)
                if cuts_of(g.get("row_cuts"), H):
                    ys = ys or cuts_of(g.get("row_cuts"), H)
                for ck in ("col_cuts", "column_cuts"):
                    if cuts_of(g.get(ck), W):
                        xs_rows = xs_rows or [cuts_of(g.get(ck), W)]
                break
        if _numbers(g, 2) and all(isinstance(x, int) for x in g):
            grid = (g[0], g[1])
            break
    if grid is None:
        for ck, rk in (("columns", "rows"), ("source_columns", "source_rows")):
            if isinstance(e.get(ck), int) and isinstance(e.get(rk), int):
                grid = (e[ck], e[rk])
                break
    # a band the frames are cut from (across the raw), or a crop the same in every cell (as wide as a cell at most)
    band = None
    for k in BAND_KEYS:
        if _numbers(e.get(k), 4):
            band = rects_of([e[k]], W, H)
            band = band[0] if band else None
            break
    yband = None
    for k in YBAND_KEYS:
        if _numbers(e.get(k), 2):
            yband = [tuple(e[k])]
            break
    vc = e.get("source_vertical_crops")
    if isinstance(vc, list) and vc and all(_numbers(x, 2) for x in vc):
        yband = [tuple(x) for x in vc]
    cells, ys2 = None, None
    if grid and grid[0] * grid[1] >= n:
        c, r = grid
        ys2 = ys if ys and len(ys) == r + 1 else [H * i / r for i in range(r + 1)]
        xs2 = xs_rows if xs_rows and all(len(x) == c + 1 for x in xs_rows) else [[W * i / c for i in range(c + 1)]]
        cells = grid_rects(n, xs2, ys2)
    elif xs_rows:
        ys2 = ys if ys and len(ys) == len(xs_rows) + 1 else [0.0, float(H)] if len(xs_rows) == 1 else None
        if ys2:
            cells = grid_rects(n, xs_rows, ys2)
    if cells:
        cut = []
        for i, (x0, y0, x1, y1) in enumerate(cells):
            row = max(k for k, yy in enumerate(ys2[:-1]) if yy <= y0 + 1e-6)
            if band and band[2] - band[0] <= (x1 - x0) + 2 and band[3] - band[1] <= (y1 - y0) + 2:
                # a crop in each cell's own coordinates
                x0, y0, x1, y1 = x0 + band[0], y0 + band[1], x0 + band[2], y0 + band[3]
            elif band:
                x0, y0, x1, y1 = max(x0, band[0]), max(y0, band[1]), min(x1, band[2]), min(y1, band[3])
            if yband:
                yb = yband[min(row, len(yband) - 1)]
                y0, y1 = max(y0, yb[0]), min(y1, yb[1])
            cut.append((x0, y0, x1, y1))
        if all(r[2] > r[0] and r[3] > r[1] for r in cut):
            ways.append(cut)
    per_cell = e.get("source_crop_per_cell")
    if isinstance(per_cell, list) and len(per_cell) == n and all(_numbers(x, 4) for x in per_cell) and cells:
        ways.append([(c[0] + p[0], c[1] + p[1], c[0] + p[2], c[1] + p[3]) for c, p in zip(cells, per_cell)])
    return ways


def covers(rects, alpha, need):
    """the rectangles hold `need` of the raw's drawn pixels, and half of them draw something (a way read in the wrong
    coordinates - Sona's 16x preview cells - holds little of the raw)"""
    on = alpha >= FG
    total = on.sum()
    if not total:
        return False
    H, W = on.shape
    u = np.zeros_like(on)
    drawn = 0
    for x0, y0, x1, y1 in rects:
        x0, y0 = max(0, int(round(x0))), max(0, int(round(y0)))
        x1, y1 = min(W, int(round(x1))), min(H, int(round(y1)))
        if x1 <= x0 or y1 <= y0:
            continue
        u[y0:y1, x0:x1] = True
        drawn += int(on[y0:y1, x0:x1].any())
    return (on & u).sum() >= need * total and drawn * 2 >= len(rects)


def raw_rects(e, n, W, H, alpha):
    """[(the n frames' rectangles in the raw (W x H), trusted)]: the manifest's own ways (trusted: a fit may squeeze
    them as Codex did, Aurora's realm 1.8 times flatter); else guessed ways - equal cuts across (Codex's own: a frame a
    cell), the gaps between the drawings, a contact sheet's drawings by its clear rows and columns, and its equal grids -
    which a fit may squeeze only a little (Scuttle Crab's 2 x 2 sheets cut across as strips and squeezed 3 times onto the
    frames came out as streaks, 2026-11-09)"""
    e = e or {}
    out = []
    for w in ([] if os.environ.get("DENSIFY_NO_MANIFEST") else manifest_ways(e, n, W, H)):
        w = [tuple(float(c) for c in r) for r in w]
        if w not in [o[0] for o in out] and covers(w, alpha, 0.7):
            out.append((w, True))
    if out:
        return out
    ways = []
    y0, y1 = 0, H
    for k in YBAND_KEYS:
        if _numbers(e.get(k), 2):
            y0, y1 = e[k]
    ways.append([(k * W / n, y0, (k + 1) * W / n, y1) for k in range(n)])
    # the drawings side by side with clear gaps between them
    cols = np.nonzero(alpha[int(y0):int(y1)].max(0) >= FG)[0]
    if len(cols):
        runs, s = [], cols[0]
        for a, b in zip(cols[:-1], cols[1:]):
            if b - a > max(4, W // 200):
                runs.append((s, a + 1))
                s = b
        runs.append((s, cols[-1] + 1))
        while len(runs) > n:      # loose sparks: join the two nearest runs
            k = min(range(len(runs) - 1), key=lambda i: runs[i + 1][0] - runs[i][1])
            runs[k:k + 2] = [(runs[k][0], runs[k + 1][1])]
        if len(runs) == n:
            mids = [0] + [(runs[i][1] + runs[i + 1][0]) / 2 for i in range(n - 1)] + [W]
            ways.append([(mids[i], y0, mids[i + 1], y1) for i in range(n)])
    # a contact sheet with no layout written: its drawings by the clear rows and columns, row by row
    segs = segments(alpha)
    if len(segs) == n:
        ways.append([tuple(map(float, s)) for s in segs])
    # its equal grids (each cell no more than 2.5 times as tall as wide or the other way)
    for r in range(2, n + 1):
        c = -(-n // r)
        if c < 2 or c * r - n >= c:
            continue
        if 0.4 <= (W / c) / (H / r) <= 2.5:
            ways.append(grid_rects(n, [[W * i / c for i in range(c + 1)]], [H * i / r for i in range(r + 1)]))
    for w in ways:
        w = [tuple(float(c) for c in r) for r in w]
        if w not in [o[0] for o in out] and covers(w, alpha, 0.6):
            out.append((w, False))
    return out


def block_size(a):
    """k when a picture is made of uniform k x k blocks from its top-left corner (a pixel-art preview), else 1"""
    for k in (16, 12, 10, 8, 6, 5, 4, 3, 2):
        if a.shape[0] < 2 * k or a.shape[1] < 2 * k or a.shape[0] % k or a.shape[1] % k:
            continue
        c = a.reshape(a.shape[0] // k, k, a.shape[1] // k, k, -1).astype(int)
        if (np.abs(c - c[:, :1, :, :1]).max(axis=(1, 3, 4)) <= 8).mean() > 0.97:
            return k
    return 1


def pixelated(a):
    """True when a picture is made of uniform k x k blocks (k >= 2): a pixel-art preview, no more detail than its 1x"""
    for k in (16, 12, 10, 8, 6, 5, 4, 3, 2):
        if a.shape[0] < 2 * k or a.shape[1] < 2 * k:
            continue
        for oy in range(k):
            for ox in range(k):
                b = a[oy:, ox:]
                H, W = (b.shape[0] // k) * k, (b.shape[1] // k) * k
                c = b[:H, :W].reshape(H // k, k, W // k, k, -1).astype(int)
                if (np.abs(c - c[:, :1, :, :1]).max(axis=(1, 3, 4)) <= 8).mean() > 0.97:
                    return True
            break
    return False


def segments(alpha):
    """every drawing of a strip or a contact sheet, by the clear rows and columns between them: [(x0, y0, x1, y1)]"""
    def runs(mask, gap):
        idx = np.nonzero(mask)[0]
        if not len(idx):
            return []
        out, s = [], idx[0]
        for a, b in zip(idx[:-1], idx[1:]):
            if b - a > gap:
                out.append((s, a + 1))
                s = b
        out.append((s, idx[-1] + 1))
        return out
    on = alpha >= FG
    H, W = on.shape
    rects = []
    for y0, y1 in runs(on.any(1), max(4, H // 100)):
        for x0, x1 in runs(on[y0:y1].any(0), max(4, W // 100)):
            ys = np.nonzero(on[y0:y1, x0:x1].any(1))[0]
            rects.append((x0, y0 + ys[0], x1, y0 + ys[-1] + 1))
    # a speck alone is not a drawing
    big = max(((r[2] - r[0]) * (r[3] - r[1]) for r in rects), default=0)
    return [r for r in rects if (r[2] - r[0]) * (r[3] - r[1]) >= big * 0.02]


def drawings(hero, used):
    """{picture: {"cells": [], "ways": [[frames]]}}: a hero's older effect drawings (no Codex pixel_1x beside them:
    assets/source/<hero>/**/*fx*.png that are real drawings, not pixel previews), each cut into its drawings - only the
    direct fit by tag name reads them"""
    out = {}
    base = os.path.join(ROOT, "assets", "source", hero)
    for p in sorted(glob.glob(os.path.join(base, "**", "*fx*.png"), recursive=True)):
        rel = os.path.relpath(p, base).replace("\\", "/")
        if p in used or "/pixel_1x/" in "/" + rel or rel.startswith("hd/") or "/hd/" in rel or os.path.getsize(p) < 20000:
            continue
        a8 = np.asarray(Image.open(G.lp(p)).convert("RGBA"))
        if pixelated(a8):
            continue
        r = a8.astype(np.float64) / 255.0
        segs = segments(r[..., 3])
        if not segs or len(segs) > 40:
            continue
        stem = os.path.basename(p)[:-4]
        name = stem.split("_fx_")[-1] if "_fx_" in stem else stem
        if name in out:
            continue
        out[name] = {"cells": [], "ways": [([r[y0:y1, x0:x1] for x0, y0, x1, y1 in segs], False)],
                     "file": os.path.relpath(p, ROOT)}
    return out


def deliveries(hero):
    """{picture: {"cells": [1x cell RGBA], "raw": [raw frame RGBA float], "file": str}}: every pixel_1x strip of the
    hero's Codex effect deliveries (assets/source/<hero>/codex_fx/**) with its raw beside it (raw/<file>, or with
    -original / -repair / -generated, or named by the picture), its frame count from the manifest there"""
    pics = {}
    base = os.path.join(ROOT, "assets", "source", hero)
    # every delivery folder: one with a pixel_1x/ folder, or a manifest beside a raw/ folder (Kha'Zix's: the strips
    # themselves 16x previews at the top, raws named <picture>_generated.png)
    dirs = {os.path.dirname(os.path.dirname(p))
            for p in glob.glob(os.path.join(base, "codex_fx", "**", "pixel_1x", "*.png"), recursive=True)}
    dirs |= {os.path.dirname(os.path.dirname(p))
             for p in glob.glob(os.path.join(base, "codex_fx", "**", "raw", "*.png"), recursive=True)}
    found = []
    for d in sorted(dirs):
        manifests = []
        for mf in glob.glob(os.path.join(d, "*.json")):
            try:
                manifests.append(json.load(open(G.lp(mf), encoding="utf-8-sig")))
            except (ValueError, OSError):
                pass
        strips = sorted(glob.glob(os.path.join(d, "pixel_1x", "*.png"))) + sorted(glob.glob(os.path.join(d, "*.png")))
        for px in strips:
            found.append((d, px, manifests))
    for d, px, manifests in found:
        file = os.path.basename(px)
        stem = file[:-4]
        name = stem.split("_fx_")[-1] if "_fx_" in stem else stem
        if name in pics:
            continue          # its pixel_1x strip came first
        e, n = entry_for(manifests, file, name)
        if not n:
            continue
        named = [e.get(k) for k in ("raw", "raw_file", "raw_path") if e and isinstance(e.get(k), str)]
        raw = next((p for p in [os.path.join(d, x) for x in named]
                    + [os.path.join(d, "raw", b + s + ".png") for s in RAW_SUFFIXES + ("_generated", "_original")
                       for b in (stem, name)] if os.path.isfile(p)), None)
        if raw is None:
            continue
        a = np.asarray(Image.open(G.lp(px)).convert("RGBA")).copy()
        # a preview (each game pixel a k x k block): back to 1x, a block's middle pixel
        k = block_size(a) if "pixel_1x" not in px.replace("\\", "/") else 1
        if k > 1:
            a = a[k // 2::k, k // 2::k].copy()
        if a.shape[1] % n:
            continue
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
        a[a[..., 3] == 0] = 0
        cw = a.shape[1] // n
        cells = [a[:, k * cw:(k + 1) * cw].copy() for k in range(n)]
        r = np.asarray(Image.open(G.lp(raw)).convert("RGBA")).astype(np.float64) / 255.0
        H, W = r.shape[:2]
        ways = []
        for rects, trusted in raw_rects(e, n, W, H, r[..., 3]):
            raws = [r[max(0, int(round(y0))):min(H, int(round(y1))), max(0, int(round(x0))):min(W, int(round(x1)))]
                    for x0, y0, x1, y1 in rects]
            if all(x.size for x in raws):
                ways.append((raws, trusted))
        if not ways:
            continue
        key = name if name not in pics else stem
        pics[key] = {"cells": cells, "ways": ways, "file": os.path.relpath(raw, ROOT), "path": raw}
    # the older drawings without a pixel_1x strip (fitted only straight onto the frames of their tag)
    for name, d in drawings(hero, {p["path"] for p in pics.values()}).items():
        if name not in pics:
            pics[name] = d
    return pics


def variants(cell):
    """(label, array): the cell, its middle column / row doubled, it doubled in size"""
    out = [("as is", cell)]
    h, w = cell.shape[:2]
    if w % 2 == 0:
        out.append(("odd col", np.insert(cell, w // 2, cell[:, w // 2], axis=1)))
    if h % 2 == 0:
        out.append(("odd row", np.insert(cell, h // 2, cell[h // 2], axis=0)))
    big = np.repeat(np.repeat(cell, 2, 0), 2, 1)
    out.append(("x2", big))
    if big.shape[1] % 2 == 0:
        out.append(("x2 odd col", np.insert(big, big.shape[1] // 2, big[:, big.shape[1] // 2], axis=1)))
    return out


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return (ys.min(), xs.min(), ys.max() + 1, xs.max() + 1) if len(xs) else None


def match(frame, pics):
    """The Codex cell this 1x frame shows -> (picture, k, label, (y, x) of the variant's top-left in the frame) or None"""
    fm = frame[..., 3] > 0
    fb = bbox(fm)
    if fb is None:
        return None
    fh, fw = fb[2] - fb[0], fb[3] - fb[1]
    best = None
    for name, p in pics.items():
        for k, c in enumerate(p["cells"]):
            for label, v in variants(c):
                vm = v[..., 3] > 0
                vb = bbox(vm)
                if vb is None or (vb[2] - vb[0], vb[3] - vb[1]) != (fh, fw):
                    continue
                a = frame[fb[0]:fb[2], fb[1]:fb[3]]
                b = v[vb[0]:vb[2], vb[1]:vb[3]]
                am, bm = a[..., 3] > 0, b[..., 3] > 0
                iou = (am & bm).sum() / max(1, (am | bm).sum())
                same = ((a[..., :3] == b[..., :3]).all(-1) & am & bm).sum() / max(1, am.sum())
                score = iou + same
                if iou >= 0.97 and same >= 0.9 and (best is None or score > best[0]):
                    best = (score, name, k, label, (fb[0] - vb[0], fb[1] - vb[1]))
    return None if best is None else best[1:]


# ------------------------------------------------------------------ fitting the raw
class Raw:
    """A raw frame's drawn pixels as summed-area tables: coverage and mean colour of any rectangle."""

    def __init__(self, r):
        fg = (r[..., 3] >= FG).astype(np.float64)
        self.h, self.w = fg.shape
        self.sat = self._sat(fg)
        self.sat_c = [self._sat(fg * r[..., c]) for c in range(3)]
        ys, xs = np.nonzero(fg)
        self.box = (ys.min(), xs.min(), ys.max() + 1, xs.max() + 1) if len(xs) else None
        self.rgb = np.round(r[..., :3] * 255).astype(np.uint8)
        self.fg = fg > 0

    @staticmethod
    def _sat(a):
        s = np.zeros((a.shape[0] + 1, a.shape[1] + 1))
        s[1:, 1:] = a.cumsum(0).cumsum(1)
        return s

    @staticmethod
    def _at(s, y, x):
        """the SAT at fractional (y, x), bilinear (clamped to the picture)"""
        H, W = s.shape[0] - 1, s.shape[1] - 1
        y = np.clip(y, 0, H)
        x = np.clip(x, 0, W)
        y0 = np.minimum(np.floor(y).astype(int), H - 1)
        x0 = np.minimum(np.floor(x).astype(int), W - 1)
        fy, fx = y - y0, x - x0
        return (s[y0, x0] * (1 - fy) * (1 - fx) + s[y0 + 1, x0] * fy * (1 - fx) + s[y0, x0 + 1] * (1 - fy) * fx
                + s[y0 + 1, x0 + 1] * fy * fx)

    def _rect(self, s, y0, x0, y1, x1):
        return self._at(s, y1, x1) - self._at(s, y0, x1) - self._at(s, y1, x0) + self._at(s, y0, x0)

    def counts(self, pal, h, w, scale, ty, tx, grid=1.0):
        """(h, w, len(pal)): in each square, how many drawn raw pixels have each palette colour as their nearest (the
        votes Codex coloured its 1x squares by)"""
        near = np.full(self.fg.shape, -1, np.int16)
        if self.box is not None:
            y0, x0, y1, x1 = self.box
            c = self.rgb[y0:y1, x0:x1].astype(np.int32)
            d = ((c[..., None, :] - pal[None, None].astype(np.int32)) ** 2).sum(-1)
            near[y0:y1, x0:x1] = np.where(self.fg[y0:y1, x0:x1], d.argmin(-1), -1)
        sx, sy = scale if isinstance(scale, tuple) else (scale, scale)
        X0 = (np.arange(w) * grid - tx) / sx
        Y0 = (np.arange(h) * grid - ty) / sy
        X0, Y0 = np.meshgrid(X0, Y0)
        X1, Y1 = X0 + grid / sx, Y0 + grid / sy
        return np.stack([np.maximum(0.0, self._rect(self._sat((near == k).astype(np.float64)), Y0, X0, Y1, X1))
                         for k in range(len(pal))], -1)

    def render(self, h, w, scale, ty, tx, grid=1.0, colour=True, window=None):
        """Coverage (h x w) and mean colour (h x w x 3) of the squares of a grid `grid` game px across, the raw placed by
        game = scale * raw + (tx, ty) (in game px of the frame); scale a number or (across, down). `window`: each
        square's coverage read over a square that wide round its middle instead (refine's game-pixel body)."""
        sx, sy = scale if isinstance(scale, tuple) else (scale, scale)
        win = grid if window is None else window
        off = (grid - win) / 2
        X0 = (np.arange(w) * grid + off - tx) / sx
        X1 = X0 + win / sx
        Y0 = (np.arange(h) * grid + off - ty) / sy
        Y1 = Y0 + win / sy
        X0, Y0 = np.meshgrid(X0, Y0)
        X1, Y1 = np.meshgrid(X1, Y1)
        area = (win / sx) * (win / sy)
        cov = self._rect(self.sat, Y0, X0, Y1, X1)
        if not colour:
            return cov / area, None
        col = np.stack([self._rect(sc, Y0, X0, Y1, X1) for sc in self.sat_c], -1)
        col = col / np.maximum(cov, 1e-9)[..., None]
        return cov / area, col


def fit_picture(raws, cells, max_aspect=1.35):
    """One scale and offset for every frame of a Codex picture (its raw cut in equal or listed cells, each cut onto its
    cell the same way), then each frame's offset nudged on its own (Codex registered some pictures frame by frame):
    Codex sometimes squeezed a picture into its cell (Aurora's realm 1.8 times flatter than drawn): then the scale is
    two, across and down, searched round the cells' own proportion.
    The two scales differ by max_aspect at most (a guessed way's less than the manifest's own); cells this much further
    from the raws' proportion than that are not these raws' frames (0 back).
    -> (mean F-score, [(F-score, ((across, down), ty, tx)) per frame]) in the cells' coordinates."""
    targets = [c[..., 3] > 0 for c in cells]
    tbs = [bbox(t) for t in targets]
    ok = [i for i, (r, tb) in enumerate(zip(raws, tbs)) if r.box is not None and tb is not None]
    if not ok:
        return 0.0, [(0.0, None)] * len(cells)
    ratios = [np.sqrt((tbs[i][2] - tbs[i][0]) / (raws[i].box[2] - raws[i].box[0])
                      * (tbs[i][3] - tbs[i][1]) / (raws[i].box[3] - raws[i].box[1])) for i in ok]
    s0 = float(np.median(ratios))
    # down / across, the cells' proportion against the raws'
    a0 = float(np.median([((tbs[i][2] - tbs[i][0]) / (raws[i].box[2] - raws[i].box[0]))
                          / ((tbs[i][3] - tbs[i][1]) / (raws[i].box[3] - raws[i].box[1])) for i in ok]))
    lim = float(np.log(max_aspect))
    if abs(np.log(a0)) > lim + 0.25:
        return 0.0, [(0.0, None)] * len(cells)
    aspects = [1.0] if abs(np.log(a0)) < 0.12 else sorted({float(np.clip(x, 1 / max_aspect, max_aspect))
                                                           for x in a0 * np.array([0.9, 0.95, 1.0, 1.05, 1.1])})
    # the cells' and the raws' common middles, so a scale step keeps the pictures where they are
    cy0 = float(np.median([(tbs[i][0] + tbs[i][2]) / 2 for i in ok]))
    cx0 = float(np.median([(tbs[i][1] + tbs[i][3]) / 2 for i in ok]))
    my = float(np.median([(raws[i].box[0] + raws[i].box[2]) / 2 for i in ok]))
    mx = float(np.median([(raws[i].box[1] + raws[i].box[3]) / 2 for i in ok]))

    def sc(s, a):
        return (s / np.sqrt(a), s * np.sqrt(a))

    grown = [grow(t) for t in targets]

    def iou_of(i, s, ty, tx, strict=0.25):
        """F-score of the drawn squares against the cell's, a square's slip forgiven (thin rings and streaks), plus
        `strict` x the plain IoU (between equal F-scores the closer fit wins)"""
        h, w = targets[i].shape
        cov, _ = raws[i].render(h, w, s, ty, tx, colour=False)
        m = cov >= COVER
        if not m.any():
            return 0.0
        p = (m & grown[i]).sum() / m.sum()
        r = (targets[i] & grow(m)).sum() / max(1, targets[i].sum())
        f = 2 * p * r / max(1e-9, p + r)
        return f + strict * (m & targets[i]).sum() / max(1, (m | targets[i]).sum())

    def place(s, a, dy, dx):
        sx, sy = sc(s, a)
        return (sx, sy), cy0 - sy * my + dy, cx0 - sx * mx + dx

    def mean(s, a, dy, dx):
        k, ty, tx = place(s, a, dy, dx)
        return float(np.mean([iou_of(i, k, ty, tx) for i in ok]))

    best = (-1.0, s0, 1.0, 0.0, 0.0)
    for a in aspects:
        for s in s0 * np.arange(0.82, 1.181, 0.03):
            for dy in np.arange(-2.0, 2.01, 0.5):
                for dx in np.arange(-2.0, 2.01, 0.5):
                    v = mean(s, a, dy, dx)
                    if v > best[0]:
                        best = (v, s, a, dy, dx)
    _, s1, a1, dy1, dx1 = best
    for a in ([a1] if len(aspects) == 1 else sorted({float(np.clip(x, 1 / max_aspect, max_aspect))
                                                      for x in a1 * np.array([0.975, 1.0, 1.025])})):
        for s in s1 * np.arange(0.97, 1.0301, 0.0075):
            for dy in np.arange(dy1 - 0.5, dy1 + 0.51, 0.125):
                for dx in np.arange(dx1 - 0.5, dx1 + 0.51, 0.125):
                    v = mean(s, a, dy, dx)
                    if v > best[0]:
                        best = (v, s, a, dy, dx)
    _, s, a, dy, dx = best
    _, ty, tx = place(s, a, dy, dx)
    per = []
    for i in range(len(cells)):
        if i not in ok:
            per.append((0.0, None))
            continue
        # this frame alone: Codex grew, shrank or moved some frames of a picture at 1x (a lock ring growing in)
        b = (iou_of(i, sc(s, a), ty, tx), s, ty, tx)
        ri = raws[i]
        rcy, rcx = (ri.box[0] + ri.box[2]) / 2, (ri.box[1] + ri.box[3]) / 2
        tb = tbs[i]
        for si in s * np.arange(0.7, 1.31, 0.05):
            kx, ky = sc(si, a)
            cy = (tb[0] + tb[2]) / 2 - ky * rcy
            cx = (tb[1] + tb[3]) / 2 - kx * rcx
            for ey in np.arange(-2.0, 2.01, 0.5):
                for ex in np.arange(-2.0, 2.01, 0.5):
                    v = iou_of(i, (kx, ky), cy + ey, cx + ex)
                    if v > b[0] + 0.005:
                        b = (v, si, cy + ey, cx + ex)
        _, s2, ty2, tx2 = b
        k2x, k2y = sc(s2, a)
        for si in s2 * np.arange(0.975, 1.0251, 0.0125):
            kx, ky = sc(si, a)
            for ey in np.arange(-0.5, 0.51, 0.125):
                for ex in np.arange(-0.5, 0.51, 0.125):
                    yy, xx = ty2 + ey - (ky - k2y) * rcy, tx2 + ex - (kx - k2x) * rcx
                    v = iou_of(i, (kx, ky), yy, xx)
                    if v > b[0] + 0.005:
                        b = (v, si, yy, xx)
        per.append((iou_of(i, sc(b[1], a), b[2], b[3], strict=0.0), (sc(b[1], a), b[2], b[3])))
    return float(np.mean([per[i][0] for i in ok])), per


def fit_one(raw, target, max_aspect=1.35):
    """One raw frame fitted straight onto a game frame's squares (no Codex cell to go by: the importer resized,
    recoloured or mended it - Aurelion Sol's stacks, Bard's doors): (F-score, ((across, down), ty, tx)) or (0, None)."""
    tb = bbox(target)
    if raw.box is None or tb is None:
        return 0.0, None
    h, w = target.shape
    ry0, rx0, ry1, rx1 = raw.box
    sy0, sx0 = (tb[2] - tb[0]) / (ry1 - ry0), (tb[3] - tb[1]) / (rx1 - rx0)
    a0 = sy0 / sx0
    if abs(np.log(a0)) > np.log(max_aspect) + 0.25:
        return 0.0, None
    aspects = [1.0] if abs(np.log(a0)) < 0.12 else sorted({float(np.clip(a0 * f, 1 / max_aspect, max_aspect))
                                                           for f in (0.95, 1.0, 1.05)})
    s0 = float(np.sqrt(sy0 * sx0))
    cy, cx = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
    rcy, rcx = (ry0 + ry1) / 2, (rx0 + rx1) / 2
    grown = grow(target)

    def score(s, a, dy, dx, strict=0.25):
        kx, ky = s / np.sqrt(a), s * np.sqrt(a)
        cov, _ = raw.render(h, w, (kx, ky), cy - ky * rcy + dy, cx - kx * rcx + dx, colour=False)
        m = cov >= COVER
        if not m.any():
            return 0.0
        p = (m & grown).sum() / m.sum()
        r = (target & grow(m)).sum() / max(1, target.sum())
        f = 2 * p * r / max(1e-9, p + r)
        return f + strict * (m & target).sum() / max(1, (m | target).sum())

    best = (-1.0, s0, aspects[0], 0.0, 0.0)
    for a in aspects:
        for s in s0 * np.arange(0.85, 1.151, 0.05):
            for dy in np.arange(-2.0, 2.01, 1.0):
                for dx in np.arange(-2.0, 2.01, 1.0):
                    v = score(s, a, dy, dx)
                    if v > best[0]:
                        best = (v, s, a, dy, dx)
    _, s1, a1, dy1, dx1 = best
    for s in s1 * np.arange(0.95, 1.051, 0.0125):
        for dy in np.arange(dy1 - 1.0, dy1 + 1.01, 0.25):
            for dx in np.arange(dx1 - 1.0, dx1 + 1.01, 0.25):
                v = score(s, a1, dy, dx)
                if v > best[0]:
                    best = (v, s, a1, dy, dx)
    _, s, a, dy, dx = best
    kx, ky = s / np.sqrt(a), s * np.sqrt(a)
    return score(s, a, dy, dx, strict=0.0), ((kx, ky), cy - ky * rcy + dy, cx - kx * rcx + dx)


MAX_GAP = 0.22    # a straight fit whose colours are further from the frame's than this (0-1 a channel) is not its frame


def pieces(mask, big=0.2):
    """how many separate large drawings a frame holds (its squares joined across a gap of up to two): one picture
    placed at several spots (Nidalee's two flame columns) is no one raw frame - a straight fit would smear one over all"""
    g = grow(grow(mask))
    seen = np.zeros_like(g)
    sizes = []
    for y, x in zip(*np.nonzero(g)):
        if seen[y, x]:
            continue
        stack, n = [(y, x)], 0
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            n += int(mask[cy, cx])
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < g.shape[0] and 0 <= nx < g.shape[1] and g[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        sizes.append(n)
    total = max(1, sum(sizes))
    return sum(1 for s in sizes if s >= big * total)


def colour_gap(raw, arr, f):
    """How far the raw's colours at the fit are from the 1x frame's, over the squares both draw: the mean of each
    channel's difference, 0 (the same) to 1"""
    s, ty, tx = f
    h, w = arr.shape[:2]
    cov, col = raw.render(h, w, s, ty, tx)
    both = (cov >= COVER) & (arr[..., 3] > 0)
    if both.sum() < 3:
        return 1.0
    return float(np.abs(col[both] * 255.0 - arr[both][:, :3].astype(np.float64)).mean() / 255.0)


def by_name(tag, pics):
    """the Codex pictures a tag may show, by name: the same name, else the longest picture name the tag starts with
    (e_hole_3 -> e_hole), else one that starts with the tag"""
    if tag in pics:
        return [tag]
    pre = sorted((n for n in pics if tag.startswith(n + "_") or tag.startswith(n)), key=len, reverse=True)
    if pre:
        return pre[:1]
    return [n for n in pics if n.startswith(tag)][:2]


def grow(m):
    """a mask grown by one square every way"""
    g = m.copy()
    g[1:] |= m[:-1]
    g[:-1] |= m[1:]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    g[1:, 1:] |= m[:-1, :-1]
    g[:-1, :-1] |= m[1:, 1:]
    g[1:, :-1] |= m[:-1, 1:]
    g[:-1, 1:] |= m[1:, :-1]
    return g


def refine(arr, raw, s, ty, tx, P, pal, keep=True):
    """The frame arr (h x w game px) P times finer, from its raw at the fit, and still arr's own look (the user,
    2026-11-09: 「别给我整的更差了 我要的是质量更好的」): drawn where the raw draws (COVER of a fine pixel) but only within one
    fine pixel of arr's squares - the glows, rings and specks Codex left out of its 1x frame stay out (Akshan's camo
    outline, Gragas's W ring); with keep every square of arr keeps at least its best-covered fine pixel; and each fine
    pixel coloured by a vote of its raw pixels over the colours arr draws in its square and the eight round it, each raw
    pixel's vote going to the nearest of those - no colour lands where arr has none near (Akshan's white hit gone blue).
    -> RGBA uint8 (h * P x w * P), binary alpha."""
    h, w = arr.shape[:2]
    H, W = h * P, w * P
    t = arr[..., 3] > 0
    cov, _ = raw.render(H, W, s, ty, tx, grid=1.0 / P, colour=False)
    up = np.repeat(np.repeat(t, P, 0), P, 1)
    on = (cov >= COVER) & grow(up)
    if P > 1:
        # arr's inner squares (drawn, their four neighbours drawn) all drawn: only its edges are refined. The raw is
        # often faint or dithered inside where Codex's 1x filled it (Kindred's W ring, Garen's spin: holes and stipple)
        pad = np.pad(t, 1)
        inner = t & pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
        on |= np.repeat(np.repeat(inner, P, 0), P, 1)
        # solid where the raw is solid at the game pixel's own scale: a fine pixel whose game-pixel-wide square round it
        # is SOLID covered is drawn (inside arr's squares) - arr's solid parts stay solid, finer only at their edges
        # (Sevika's blood wings and flames came out as specks and wisps at the fine pixel's scale alone)
        body, _ = raw.render(H, W, s, ty, tx, grid=1.0 / P, colour=False, window=1.0)
        on |= (body >= SOLID) & up
    if keep and P > 1:
        # as heavy as arr: FILL of its squares' area at least, the best-covered fine pixels inside its squares added
        # where the raw's sparks and wisps fall short of COVER on the finer grid (Sevika's hits and flames came out thin)
        short = int(FILL * t.sum() * P * P) - int(on.sum())
        inside = up & ~on & (cov > 1e-3)
        if short > 0 and inside.any():
            vals = np.sort(cov[inside])[::-1]
            on |= inside & (cov >= vals[min(short, len(vals)) - 1])
    if keep and P > 1 and t.any():
        c4 = cov.reshape(h, P, w, P).transpose(0, 2, 1, 3).reshape(h, w, P * P)
        o4 = on.reshape(h, P, w, P).transpose(0, 2, 1, 3).reshape(h, w, P * P)
        ys, xs = np.nonzero(t & ~o4.any(-1))
        if len(ys):
            k = c4[ys, xs].argmax(-1)
            on[ys * P + k // P, xs * P + k % P] = True
    K = len(pal)
    pidx = np.full((h, w), -1)
    if t.any():
        c = arr[t][:, :3].astype(np.int32)
        pidx[t] = ((c[:, None] - pal[None].astype(np.int32)) ** 2).sum(-1).argmin(1)
    cand = np.zeros((h, w, K), bool)
    pad = np.pad(pidx, 1, constant_values=-1)
    for dy in range(3):
        for dx in range(3):
            sh = pad[dy:dy + h, dx:dx + w]
            yy, xx = np.nonzero(sh >= 0)
            cand[yy, xx, sh[yy, xx]] = True
    cand = np.repeat(np.repeat(cand, P, 0), P, 1)
    cnt = raw.counts(pal, H, W, s, ty, tx, grid=1.0 / P)
    parent = np.repeat(np.repeat(pidx, P, 0), P, 1)
    sx, sy = s if isinstance(s, tuple) else (s, s)
    area = (1.0 / P) ** 2 / (sx * sy)            # raw pixels a fine pixel
    D = ((pal[:, None].astype(np.float64) - pal[None].astype(np.float64)) ** 2).sum(-1)
    col = np.zeros((H, W), int)
    for y0 in range(0, H, 16):
        cd = cand[y0:y0 + 16]
        near = (D[None, None] + np.where(cd[:, :, None, :], 0.0, np.inf)).argmin(-1)
        score = np.zeros(cd.shape)
        for k in range(K):
            score += cnt[y0:y0 + 16, :, k:k + 1] * (near[..., k:k + 1] == np.arange(K))
        # its own square's colour first: another wins only where the raw clearly draws it (Akshan's R bullet went orange)
        # and draws it solidly - a faint or dithered raw (a few votes) leaves the 1x colour (Kindred's W ring went to
        # colour noise)
        par = parent[y0:y0 + 16]
        yy, xx = np.nonzero(par >= 0)
        score[yy, xx, par[yy, xx]] += PRIOR * score[yy, xx].sum(-1) + FAINT * area
        col[y0:y0 + 16] = score.argmax(-1)
    # a fine pixel no raw pixel votes for (kept for its square): its square's colour
    col = np.where((cnt.sum(-1) <= 0) & (parent >= 0), parent, col)
    out = np.zeros((H, W, 4), np.uint8)
    out[on, :3] = pal[col[on]]
    out[on, 3] = 255
    return out


def zoom_frames(arr, raw, s, ty, tx, P, pal, z):
    """(1x frame, dense frame) of a 1x frame redrawn z = (zoom, (dx, dy)) times bigger about the pivot + (dx, dy): the
    1x frame's squares zoomed (nearest) give the shape and colours the raw then refines - at 1x (the fallback), and P
    times finer from that. The frame keeps its middle on the pivot (grown alike at both ends)."""
    h, w = arr.shape[:2]
    zf, (dx, dy) = z
    qx, qy = w / 2 + dx, h / 2 + dy
    sx, sy = s if isinstance(s, tuple) else (s, s)
    s2, ty2, tx2 = (sx * zf, sy * zf), qy + zf * (ty - qy), qx + zf * (tx - qx)
    ys, xs = np.nonzero(arr[..., 3] > 0)
    ex = max(w / 2 - (qx + zf * (xs.min() - qx)), qx + zf * (xs.max() + 1 - qx) - w / 2) - w / 2
    ey = max(h / 2 - (qy + zf * (ys.min() - qy)), qy + zf * (ys.max() + 1 - qy) - h / 2) - h / 2
    gx, gy = max(0, int(np.ceil(ex))) + 1, max(0, int(np.ceil(ey))) + 1
    H1, W1 = h + 2 * gy, w + 2 * gx
    Y, X = np.mgrid[0:H1, 0:W1]
    py = np.floor(qy + (Y + 0.5 - gy - qy) / zf).astype(int)
    px = np.floor(qx + (X + 0.5 - gx - qx) / zf).astype(int)
    ok = (py >= 0) & (py < h) & (px >= 0) & (px < w)
    nn = np.zeros((H1, W1, 4), np.uint8)
    nn[ok] = arr[py[ok], px[ok]]
    one = refine(nn, raw, s2, ty2 + gy, tx2 + gx, 1, pal, keep=False)
    return one, refine(one, raw, s2, ty2 + gy, tx2 + gx, P, pal)


def fidelity(raw, arr, s, ty, tx):
    """(F-score with a square's slip forgiven, plain IoU, colour gap) of the raw at the fit read back onto the 1x frame by
    Codex's rule (a square drawn when COVER of it is drawn raw), against the 1x frame"""
    h, w = arr.shape[:2]
    cov, col = raw.render(h, w, s, ty, tx)
    m = cov >= COVER
    t = arr[..., 3] > 0
    if not m.any() or not t.any():
        return 0.0, 0.0, 1.0
    p = (m & grow(t)).sum() / m.sum()
    r = (t & grow(m)).sum() / t.sum()
    f = float(2 * p * r / max(1e-9, p + r))
    iou = float((m & t).sum() / (m | t).sum())
    both = m & t
    gap = float(np.abs(col[both] * 255.0 - arr[both][:, :3]).mean() / 255.0) if both.sum() >= 3 else 1.0
    return f, iou, gap


def readback(arr, dense, ppu):
    """The finished dense frame (coloured, mirrored) read back onto the 1x frame's grid: (round trip - the mean, over the
    squares either draws, of the premultiplied colour difference blurred a square (a square's slip is no error), 0-1 -
    and the share of the dense frame's drawn pixels outside the 1x frame)"""
    P = int(round(ppu))
    h, w = arr.shape[:2]
    H, W = dense.shape[:2]
    oy, ox = (H - h * P) // 2, (W - w * P) // 2
    if oy < 0 or ox < 0 or P != ppu:
        return 1.0, 1.0
    sub = dense[oy:oy + h * P, ox:ox + w * P]
    outside = 1.0 - (sub[..., 3] > 0).sum() / max(1, (dense[..., 3] > 0).sum())
    blk = sub.reshape(h, P, w, P, 4).astype(np.float64)
    on = blk[..., 3] > 0
    cov = on.mean(axis=(1, 3))
    col = (blk[..., :3] * on[..., None]).sum(axis=(1, 3)) / np.maximum(on.sum(axis=(1, 3)), 1)[..., None]
    ma = (arr[..., 3] > 0).astype(np.float64)
    u = (ma > 0) | (cov >= COVER)
    if u.sum() < 3:
        return 1.0, float(outside)

    def blur(x):
        y = x.copy()
        y[1:] += x[:-1]
        y[:-1] += x[1:]
        y[:, 1:] += x[:, :-1]
        y[:, :-1] += x[:, 1:]
        return y / 5.0
    pa = arr[..., :3].astype(np.float64) * ma[..., None]
    pd = col * cov[..., None]
    return float(np.abs(blur(pa) - blur(pd))[u].mean() / 255.0), float(outside)


def symmetric(frame, axis):
    """True when the 1x frame is its own mirror (axis 1: left to right, 0: top to bottom)"""
    return bool(frame[..., 3].any()) and (frame == np.flip(frame, axis)).all()


def balance(arr, dense, pal):
    """How far the dense frame's colours are from the 1x frame's in share (each a palette colour): half the summed
    differences of the shares, 0 (the same mix) to 1"""
    def share(a):
        m = a[..., 3] > 0
        if not m.any():
            return np.zeros(len(pal))
        c = a[m][:, :3].astype(np.int32)
        k = ((c[:, None] - pal[None].astype(np.int32)) ** 2).sum(-1).argmin(1)
        return np.bincount(k, minlength=len(pal)) / len(k)
    return float(0.5 * np.abs(share(arr) - share(dense)).sum())


def mirror_half(a, axis):
    """the first half (and an odd size's middle row) kept and mirrored onto the second"""
    n = a.shape[axis]
    half = np.take(a, range(n // 2), axis=axis)
    mid = np.take(a, range(n // 2, n - n // 2), axis=axis)
    return np.concatenate([half, mid, np.flip(half, axis)], axis=axis)


def symmetrize(a, axis):
    """a frame made its own mirror: drawn where either side draws (a line a hair off the middle is kept, not lost), the
    first half's colours"""
    b = np.flip(a, axis)
    out = a.copy()
    take = (a[..., 3] == 0) & (b[..., 3] > 0)
    out[take] = b[take]
    return mirror_half(out, axis)


# ------------------------------------------------------------------ sheets
def load_sheet(stem):
    fan = json.load(open(G.lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    img = np.asarray(Image.open(G.lp(stem + "#sheet.png")).convert("RGBA"))
    tags = {}
    for t, a in fan.items():
        tags[t] = []
        for f in a["frames"]:
            x, y, w, h = (int(f["data"][k]) for k in "xywh")
            tags[t].append((img[y:y + h, x:x + w].copy(), round(f["duration"] * 1000, 3)))
    return tags


def centre_pad(a, h, w):
    """a padded (or cut) round its middle to h x w"""
    out = np.zeros((h, w, 4), np.uint8)
    ah, aw = a.shape[:2]
    oy, ox = (h - ah) // 2, (w - aw) // 2
    sy0, sx0 = max(0, -oy), max(0, -ox)
    dy0, dx0 = max(0, oy), max(0, ox)
    ch, cw = min(ah - sy0, h - dy0), min(aw - sx0, w - dx0)
    out[dy0:dy0 + ch, dx0:dx0 + cw] = a[sy0:sy0 + ch, sx0:sx0 + cw]
    return out


X2_LIST = os.environ.get("DENSIFY_X2_LIST") or os.path.join(HERE, "fx_x2_tags.txt")


def x2_tags(path=X2_LIST):
    """{(sheet, tag): how} the review kept off their raws (tools/art/fx_x2_tags.txt, a line each: `sheet:tag  # why` -
    Scale2x'd whatever their fits - or `sheet:tag = square  # why` - its 1x squares, PPU times, not even Scale2x)"""
    out = {}
    if os.path.isfile(path):
        for line in open(path, encoding="utf-8"):
            line = line.split("#")[0].strip()
            if ":" in line:
                key, _, how = line.partition("=")
                sheet, tag = key.split(":", 1)
                out[(sheet.strip(), tag.strip())] = how.strip() or "x2"
    return out


def densify(hero, sheets, ppu, zooms, log):
    pics = deliveries(hero)
    log(f"{hero}: {len(pics)} Codex pictures with raws: {', '.join(sorted(pics))}")
    sheet_tags = {stem: load_sheet(stem) for stem in sheets}
    # 1. every distinct 1x frame -> the Codex cell it shows
    matches = {}
    for stem, tags in sheet_tags.items():
        for tag, frames in tags.items():
            if tag.startswith(("hd_", "lo_")) or tag == "idle":
                continue
            for arr, _ in frames:
                key = (arr.shape, arr.tobytes())
                if key not in matches:
                    matches[key] = match(arr, pics) if arr[..., 3].any() else None
                    if matches[key] is None and arr[..., 3].any():
                        log(f"  {tag}: a {arr.shape[1]}x{arr.shape[0]} frame matches no Codex cell - scaled up square "
                            f"for square")
    # 2. one fit a Codex picture (as each variant is used), every frame of it
    fits, raws, trust = {}, {}, {}
    for (name, label) in sorted({(m[0], m[2]) for m in matches.values() if m}):
        cells = [dict(variants(c))[label] for c in pics[name]["cells"]]
        # each way of cutting the raw into frames (equal cells, or the gaps between the drawings) fitted: the better kept
        best = None
        for w, (way, trusted) in enumerate(pics[name]["ways"]):
            rs = [Raw(r) for r in way]
            mean, per = fit_picture(rs, cells, TRUSTED_ASPECT if trusted else GUESS_ASPECT)
            if best is None or mean > best[0] + 1e-6:
                best = (mean, per, rs, w, trusted)
        mean, per, rs, w, trusted = best
        for k, r in enumerate(rs):
            raws[(name, label, k)] = r
            trust[(name, label, k)] = trusted
        bad = [k for k, (score, _) in enumerate(per) if score < MIN_FIT]
        log(f"  {name} ({label}): fit {mean:.2f} over {len(cells)} frames, way {w + 1} of "
            f"{len(pics[name]['ways'])}{' (the manifest' + chr(39) + 's)' if trusted else ' (guessed)'} ("
            + " ".join(f"{score:.2f}" for score, _ in per) + ")"
            + (f" - frame(s) {', '.join(str(k + 1) for k in bad)} too unlike their 1x cells: scaled up square for square"
               if bad else ""))
        for k, (score, f) in enumerate(per):
            fits[(name, label, k)] = f if score >= MIN_FIT else None
    # 2b. frames no cell matched (or matched badly): their tag's picture by name, each raw frame of it fitted straight on
    # the game frame - the best one kept (cheap scores first, the full fit for the three likeliest). Its colours must be
    # the frame's (Xerath's R smoke took a bolt's raw frame by its outline alone, 2026-11-09), and a tag's frames take the
    # picture's frames in their order where they can (a step back costs a little).
    direct = {}
    for stem, tags in sheet_tags.items():
        for tag, frames in tags.items():
            if tag.startswith(("hd_", "lo_")) or tag == "idle":
                continue
            names = by_name(tag, pics)
            if not names:
                continue
            prev = None                       # the raw frame the tag's last fitted frame took
            for arr, _ in frames:
                key = (arr.shape, arr.tobytes())
                m = matches.get(key)
                if key in direct:
                    prev = direct[key][0]
                    continue
                if not arr[..., 3].any() or (m and fits.get((m[0], m[2], m[1]))):
                    continue
                target = arr[..., 3] > 0
                if pieces(target) > 1:
                    log(f"  {tag}: a {arr.shape[1]}x{arr.shape[0]} frame of {pieces(target)} drawings apart - no straight "
                        f"fit: scaled up square for square")
                    continue
                cands = []
                for name in names:
                    for w, (way, trusted) in enumerate(pics[name]["ways"]):
                        for k in range(len(way)):
                            rk = (name, "direct", w, k)
                            if rk not in raws:
                                raws[rk] = Raw(way[k])
                                trust[rk] = trusted
                            r = raws[rk]
                            if r.box is None:
                                continue
                            tb = bbox(target)
                            s = np.sqrt((tb[2] - tb[0]) / (r.box[2] - r.box[0]) * (tb[3] - tb[1]) / (r.box[3] - r.box[1]))
                            cy, cx = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
                            cov, _ = r.render(*target.shape, s, cy - s * (r.box[0] + r.box[2]) / 2,
                                              cx - s * (r.box[1] + r.box[3]) / 2, colour=False)
                            mm = cov >= COVER
                            cands.append(((mm & target).sum() / max(1, (mm | target).sum()), rk))
                best = (-1.0, None, None, 0.0, 0.0)
                for _, rk in sorted(cands, reverse=True)[:3]:
                    score, f = fit_one(raws[rk], target, TRUSTED_ASPECT if trust[rk] else GUESS_ASPECT)
                    if f is None or score < MIN_FIT:
                        continue
                    gap = colour_gap(raws[rk], arr, f)
                    if gap > MAX_GAP:
                        continue
                    back = prev is not None and rk[:3] == prev[:3] and rk[3] < prev[3]
                    value = score - gap - (0.05 if back else 0.0)
                    if value > best[0]:
                        best = (value, f, rk, score, gap)
                if best[1] is not None:
                    direct[key] = (best[2], best[1])
                    prev = best[2]
                    log(f"  {tag}: a {arr.shape[1]}x{arr.shape[0]} frame fitted straight on {best[2][0]}[{best[2][3]}] "
                        f"({best[3]:.2f}, colours {best[4]:.2f} apart)")
                elif cands:
                    log(f"  {tag}: a {arr.shape[1]}x{arr.shape[0]} frame - no raw frame of {', '.join(names)} with its "
                        f"outline and its colours: scaled up square for square")
    # 3. the frames. Each fitted frame passes the gate at 1x or is not redrawn from its raw; a tag is redrawn from its
    # raws only when every drawn frame of it is (specks of under SPECK squares aside: an animation half redrawn is no
    # better) and its pictures are fine enough at 1x (K_MAX raw pixels a game pixel at most: coarser ones Codex redesigned
    # when it cut them to 1x); every other tag is its 1x frames Scale2x'd. A redrawn frame is the 1x frame refined
    # (refine), kept symmetric where its 1x frame is, read back at 1x once more, and zoomed only after all that.
    result, stats = {}, {"raw": 0, "x2": 0, "gated": 0}
    kept_off = x2_tags()
    for stem, tags in sheet_tags.items():
        out1, outd = {}, {}
        sheet_stats = {"raw": 0, "x2": 0, "gated": 0, "drawn": 0, "tags_raw": [], "tags_x2": [], "gate": [],
                       "frames": {}, "measures": {}, "zoom_left": []}
        for tag, frames in tags.items():
            if tag.startswith(("hd_", "lo_")) or tag == "idle":
                continue
            fitted, why = [], {}
            for arr, _ in frames:
                key = (arr.shape, arr.tobytes())
                m = matches.get(key)
                f = fits.get((m[0], m[2], m[1])) if m else None
                d = direct.get(key) if f is None else None
                if d is not None:
                    rk, (sc, ty, tx) = d
                    fitted.append((raws[rk], sc, ty, tx, rk[0]))
                elif f is not None:
                    name, k, label, (oy, ox) = m
                    fitted.append((raws[(name, label, k)], f[0], f[1] + oy, f[2] + ox, name))   # the cell's fit moved on
                else:
                    fitted.append(None)
            measures = [None] * len(frames)
            for i, ((arr, _), ft) in enumerate(zip(frames, fitted)):
                if ft is not None:
                    fq, iou, gap = fidelity(ft[0], arr, *ft[1:4])
                    measures[i] = {"f": round(fq, 3), "iou": round(iou, 3), "gap": round(gap, 3),
                                   "squares": int((arr[..., 3] > 0).sum()), "aspect": round(float(
                                       np.log(ft[1][0] / ft[1][1]) if isinstance(ft[1], tuple) else 0.0), 3),
                                   "raw_px": round(raw_px(ft), 1)}
                    if fq < GATE_F or iou < GATE_IOU or gap > GATE_GAP:
                        why[i] = f"raw read back at 1x: F {fq:.2f}, IoU {iou:.2f}, colours {gap:.2f} apart"
                        fitted[i] = None
            # each picture's palette: its Codex cells' colours, else (an older drawing) the tag's own 1x frames'
            colours = {}
            for pic in {ft[4] for ft in fitted if ft}:
                ones = [c for c in pics[pic]["cells"] if c[..., 3].any()] or [a for a, _ in frames if a[..., 3].any()]
                colours[pic] = np.unique(np.concatenate([c[c[..., 3] > 0][:, :3] for c in ones]), axis=0)

            def finish(arr, g):
                for axis in (1, 0):
                    if symmetric(arr, axis):
                        g = symmetrize(g, axis)
                return g
            dense = []
            for i, ((arr, _), ft) in enumerate(zip(frames, fitted)):
                if ft is None:
                    dense.append(None)
                    continue
                h, w = arr.shape[:2]
                g = finish(arr, refine(arr, ft[0], ft[1], ft[2], ft[3], int(ppu), colours[ft[4]]))
                rt, outside = readback(arr, g, ppu)
                tv = balance(arr, g, colours[ft[4]])
                measures[i].update(rt=round(rt, 3), out=round(outside, 3), tv=round(tv, 3))
                if rt > GATE_RT or outside > GATE_OUT or tv > GATE_TV:
                    why[i] = (f"dense frame read back at 1x: {rt:.2f} off, {outside:.0%} of it outside the frame, "
                              f"colour mix {tv:.2f} apart")
                    fitted[i] = None
                    g = None
                dense.append(g)
            # from the raws all or nothing a tag (specks aside), and only where its pictures are fine enough
            big = [i for i, (arr, _) in enumerate(frames) if (arr[..., 3] > 0).sum() >= SPECK]
            short = [i for i in big if fitted[i] is None]
            coarse = sorted({ft[4] for ft in fitted if ft and raw_px(ft) > K_MAX})
            listed = kept_off.get((os.path.basename(stem), tag))
            use_raw = any(ft is not None for ft in fitted) and not short and not coarse and not listed
            if any(ft is not None for ft in fitted) and not use_raw:
                if listed:
                    log(f"  {tag}: {'squares' if listed == 'square' else 'Scale2x'} - kept off its raw by the review "
                        f"(tools/art/fx_x2_tags.txt)")
                elif short:
                    log(f"  {tag}: Scale2x - frame(s) {', '.join(str(i + 1) for i in short)} not redrawn from a raw"
                        + "".join(f"; {i + 1}: {why[i]}" for i in short if i in why))
                else:
                    log(f"  {tag}: Scale2x - {', '.join(coarse)} too coarse at 1x "
                        f"({max(raw_px(ft) for ft in fitted if ft):.0f} raw px a game px)")
                for i in range(len(frames)):
                    if fitted[i] is not None:
                        why.setdefault(i, "Scale2x with its tag")
                        fitted[i], dense[i] = None, None
            z = zooms.get(tag, (1.0, (0.0, 0.0)))
            per = []
            if use_raw and z[0] != 1.0:
                for (arr, ms), ft in zip(frames, fitted):
                    if ft is None:
                        per.append((arr, finer(arr, ppu), ms, None))
                        continue
                    f1, fd = zoom_frames(arr, ft[0], ft[1], ft[2], ft[3], int(ppu), colours[ft[4]], z)
                    per.append((finish(arr, f1), finish(arr, fd), ms, ft[4]))
                log(f"  {tag}: zoomed x{z[0]:g}")
            else:
                up = (lambda a: square(a, ppu)) if listed == "square" else (lambda a: finer(a, ppu))
                for (arr, ms), ft, g in zip(frames, fitted, dense):
                    per.append((arr, g, ms, ft[4]) if ft is not None else (arr, up(arr), ms, None))
                if z[0] != 1.0:
                    sheet_stats["zoom_left"].append(tag)
                    log(f"  {tag}: not zoomed (x{z[0]:g} asked) - no raw redraws it: left to Codex's redraw")
            n_raw = sum(1 for p_ in per if p_[3])
            n_x2 = sum(1 for p_ in per if not p_[3] and p_[0][..., 3].any())
            stats["raw"] += n_raw
            stats["x2"] += n_x2
            stats["gated"] += len(why)
            sheet_stats["raw"] += n_raw
            sheet_stats["x2"] += n_x2
            sheet_stats["gated"] += len(why)
            sheet_stats["drawn"] += n_raw + n_x2
            sheet_stats["gate"] += [[tag, i + 1, w_] for i, w_ in sorted(why.items())]
            sheet_stats["measures"][tag] = measures
            sheet_stats["frames"][tag] = "".join("R" if p_[3] else "X" if p_[0][..., 3].any() else "."
                                                 for p_ in per)
            if n_raw:
                sheet_stats["tags_raw"].append(tag)
            elif n_x2:
                sheet_stats["tags_x2"].append(tag)
            out1[tag] = [(p_[0], p_[2]) for p_ in per]
            outd["hd_" + tag] = [(p_[1], p_[2]) for p_ in per]
        result[stem] = (out1, outd, sheet_stats)
    log(f"{hero}: {stats['raw']} frames redrawn from the raws, {stats['x2']} Scale2x'd ({stats['gated']} of them fitted "
        f"to a raw but not redrawn from it)")
    return result


def scale2x_plain(a):
    """EPX / Scale2x as published: each pixel four, a corner taking its two neighbours' colour where they agree and the
    other two do not (kept to tell the frames it made before 2026-11-09 23:30 from the guarded ones, scale2x)"""
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)))
    P = p[1:-1, 1:-1]
    A, D = p[:-2, 1:-1], p[2:, 1:-1]       # up, down
    C, B = p[1:-1, :-2], p[1:-1, 2:]       # left, right

    def eq(x, y):
        return (x == y).all(-1)
    out = np.zeros((h * 2, w * 2, a.shape[2]), a.dtype)
    out[0::2, 0::2] = np.where((eq(C, A) & ~eq(C, D) & ~eq(A, B))[..., None], A, P)
    out[0::2, 1::2] = np.where((eq(A, B) & ~eq(A, C) & ~eq(B, D))[..., None], B, P)
    out[1::2, 0::2] = np.where((eq(D, C) & ~eq(D, B) & ~eq(C, A))[..., None], C, P)
    out[1::2, 1::2] = np.where((eq(B, D) & ~eq(B, A) & ~eq(D, C))[..., None], D, P)
    return out


def scale2x_thick(a):
    """scale2x's first guard alone (2026-11-09 23:21-23:40; kept to tell the frames it made from the final ones)"""
    return _scale2x(a, own=False)


def scale2x(a):
    """Scale2x (EPX) for the solid parts only: each pixel four, a corner taking its two neighbours' colour where they
    agree and the other two do not - and only where that colour is two pixels thick there both ways (the diagonal
    between the two neighbours and the pixel beyond each are that colour too) and the pixel itself goes on in its own
    colour on its other two sides. So the edges between solid areas come out rounder (diagonal steps halved) while 1-px
    lines, rings, dots, crosses, glyphs, dither and thin fringes stay exactly as drawn: the plain Scale2x thickened
    Aatrox's telegraph rings, fused Akali's dotted marks and Darius's sparks, rounded Dr. Mundo's + crosses and Ryze's
    runes, mottled Shaco's chequered clone, and let Irelia's white eat her red fringe (the review, 2026-11-09). Nothing
    added, no colour made up: the 1x frame's own design. For the tags no raw redraws faithfully (Sevika's small hits
    redrawn from their raws looked like other drawings - Codex had redesigned them at 1x, 20-40 raw pixels a pixel)."""
    return _scale2x(a, own=True)


def _scale2x(a, own):
    h, w = a.shape[:2]
    p = np.pad(a, ((2, 2), (2, 2), (0, 0)))

    def at(dy, dx):
        return p[2 + dy:2 + dy + h, 2 + dx:2 + dx + w]

    def eq(x, y):
        return (x == y).all(-1)
    P = at(0, 0)
    A, D, C, B = at(-1, 0), at(1, 0), at(0, -1), at(0, 1)          # up, down, left, right
    yes = np.ones(P.shape[:2], bool)
    out = np.zeros((h * 2, w * 2, a.shape[2]), a.dtype)
    out[0::2, 0::2] = np.where((eq(C, A) & ~eq(C, D) & ~eq(A, B) & eq(at(-1, -1), A) & eq(at(-2, 0), A)
                                & eq(at(0, -2), C) & (eq(B, P) & eq(D, P) if own else yes))[..., None], A, P)
    out[0::2, 1::2] = np.where((eq(A, B) & ~eq(A, C) & ~eq(B, D) & eq(at(-1, 1), A) & eq(at(-2, 0), A)
                                & eq(at(0, 2), B) & (eq(C, P) & eq(D, P) if own else yes))[..., None], B, P)
    out[1::2, 0::2] = np.where((eq(D, C) & ~eq(D, B) & ~eq(C, A) & eq(at(1, -1), C) & eq(at(2, 0), D)
                                & eq(at(0, -2), C) & (eq(A, P) & eq(B, P) if own else yes))[..., None], C, P)
    out[1::2, 1::2] = np.where((eq(B, D) & ~eq(B, A) & ~eq(D, C) & eq(at(1, 1), D) & eq(at(2, 0), D)
                                & eq(at(0, 2), B) & (eq(A, P) & eq(C, P) if own else yes))[..., None], D, P)
    return out


def finer(arr, ppu):
    """a 1x frame no raw redraws, PPU times finer: Scale2x at PPU 2, else its squares"""
    return scale2x(arr) if ppu == 2 else square(arr, ppu)


def raw_px(ft):
    """raw pixels a game pixel at a fit"""
    sx, sy = ft[1] if isinstance(ft[1], tuple) else (ft[1], ft[1])
    return float(1.0 / np.sqrt(sx * sy))


def square(arr, ppu):
    h, w = arr.shape[:2]
    if float(ppu).is_integer():
        return np.repeat(np.repeat(arr, int(ppu), 0), int(ppu), 1)
    return np.asarray(Image.fromarray(arr).resize((int(round(w * ppu)), int(round(h * ppu))), Image.NEAREST))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", required=True)
    ap.add_argument("--pack", default="league", help="league (league/effects) or tft (tft/effects)")
    ap.add_argument("--ppu", type=float, default=2.0)
    ap.add_argument("--sheets", nargs="*", help="sheet names (default: every <pack>/effects/<pack>_<hero>_* sheet)")
    ap.add_argument("--skip", nargs="*", default=[],
                    help="sheets left alone (dense already by their own tools: the pack DLL's hd.rs EFFECTS)")
    ap.add_argument("--zoom", nargs="*", default=[],
                    help="tag=z[@dx,dy]: redraw that tag z times bigger (1x and dense) about the pivot + (dx, dy) game px")
    ap.add_argument("--out", help="where the sheets go (default: <pack>/effects)")
    ap.add_argument("--review", help="write a 1x | dense review of every tag here")
    ap.add_argument("--report", help="write {sheet: {raw, square, drawn, tags_raw, tags_square, written}} here (JSON)")
    a = ap.parse_args()
    fx_dir = os.path.join(ROOT, a.pack, "effects")
    a.out = a.out or fx_dir
    sheets = a.sheets or sorted(f[:-len("#anim.fanim")] for f in os.listdir(fx_dir)
                                if f.startswith(f"{a.pack}_{a.hero}_") and f.endswith("#anim.fanim"))
    # a `_1x` sheet is drawn by an add-on's own code at its size (Yuumi's ride, Zoe's spells, the eggs' crown): never dense
    stems = [os.path.join(fx_dir, s) for s in sheets if s not in a.skip and not s.endswith("_1x")
             and os.path.isfile(os.path.join(fx_dir, s + "#anim.fanim"))]
    zooms = {}
    for spec in a.zoom:
        t, v = spec.split("=")
        zf, _, at = v.partition("@")
        dx, dy = (float(c) for c in at.split(",")) if at else (0.0, 0.0)
        zooms[t] = (float(zf), (dx, dy))
    res = densify(a.hero, stems, a.ppu, zooms, print)
    report = {}
    for stem, (t1, td, st) in res.items():
        # a huge sheet only Scale2x'd is left at 1x: its twins would cost far more texels than the rounder edges are worth
        # (Illaoi's souls, every champion's spirit: 3.3 M texels, 13 M more dense - over a 256 MiB image cache's share)
        texels = sum(f[0].shape[0] * f[0].shape[1] for fr in t1.values() for f in fr)
        written = st["raw"] > 0 or (st["x2"] > 0 and a.ppu == 2 and texels <= MAX_X2_TEXELS)
        report[os.path.basename(stem)] = dict(st, written=written)
        if not written:
            print(f"{os.path.basename(stem)}: nothing redrawn from a raw and {texels} texels to Scale2x - left as it is")
            continue
        tags = {}
        first = next(iter(t1))
        idle1 = t1[first][0][0]
        idled = td["hd_" + first][0][0]
        tags["idle"] = [(idle1, 100)]
        tags["hd_idle"] = [(centre_pad(idled, idled.shape[0], int(round(idle1.shape[1] * a.ppu))), 100)]
        for t in t1:
            tags[t] = t1[t]
        for t in td:
            tags[t] = td[t]
        out = os.path.join(a.out, os.path.basename(stem))
        W, H = G.write_sheet(G.lp(out), tags, share=True)
        print(f"{out}#sheet.png {W}x{H}: {len(t1)} tags + hd_ twins ({st['raw']} frames from raws, {st['x2']} "
              f"Scale2x'd{': ' + ', '.join(st['tags_x2']) if st['tags_x2'] else ''})")
    # Codex's redraws of this hero's Scale2x tags (tools/art/import_fx_redraw.py, kept in assets/source/<hero>/
    # codex_fx_redraw): over what was just written, so a rerun keeps them
    if os.path.normcase(os.path.abspath(a.out)) == os.path.normcase(os.path.abspath(fx_dir)) and a.ppu == 2:
        import import_fx_redraw
        import_fx_redraw.apply(a.hero, log=print)
    if a.report:
        with open(G.lp(a.report), "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
    if a.review:
        review({k: v for k, v in res.items() if v[2]["raw"] or v[2]["x2"]}, a.review, a.ppu)


def review(res, path, ppu, M=4):
    from PIL import ImageDraw
    rows = []
    for stem, (t1, td, _) in res.items():
        for t in t1:
            pairs = list(zip(t1[t], td["hd_" + t]))
            k = max(range(len(pairs)), key=lambda i: (pairs[i][0][0][..., 3] > 0).sum())
            (f1, _), (fd, _) = pairs[k]
            a = Image.fromarray(f1).resize((f1.shape[1] * M, f1.shape[0] * M), Image.NEAREST)
            b = Image.fromarray(fd).resize((int(fd.shape[1] * M / ppu), int(fd.shape[0] * M / ppu)), Image.NEAREST)
            rows.append((os.path.basename(stem).replace("league_", "") + " " + t, a, b))
    W = 220 + max(r[1].width + r[2].width for r in rows) + 40
    H = sum(max(r[1].height, r[2].height) + 14 for r in rows)
    can = Image.new("RGB", (W, H), (34, 40, 48))
    d = ImageDraw.Draw(can)
    y = 0
    for label, a, b in rows:
        d.text((6, y + 4), label, fill=(255, 220, 120))
        for x, im in ((220, a), (240 + a.width, b)):
            bg = Image.new("RGBA", im.size, (66, 88, 66, 255))
            bg.alpha_composite(im.convert("RGBA"))
            can.paste(bg.convert("RGB"), (x, y))
        y += max(a.height, b.height) + 14
    can.save(G.lp(path))
    print("review", path, can.size)


if __name__ == "__main__":
    main()
