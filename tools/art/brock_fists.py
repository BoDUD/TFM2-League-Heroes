#!/usr/bin/env python3
"""tft_brock's fists off the ground, in every frame that stands in his design (the user, 2026-11-17, on his round-7 run:
「岩宝也是太僵硬」 - his design rests both stone fists on the ground (the near one's soles row is the ground, the far
one's three rows over it), so his body could not sink with his steps: sunk two rows, the fists went under the ground).

    python -I tools/art/brock_fists.py --init      # keep the base: the frames as they are before (once)
    python -I tools/art/brock_fists.py             # lay them: the sheet's idle_base / hit frames (hd_, 1x, lo_), their
                                                   # strips, and the run's sources (then run_body_anim.py --hero brock)
    python -I tools/art/brock_fists.py --check     # exit 1 when a frame is not as this tool makes it (CI)
    python -I tools/art/brock_fists.py --review DIR   # base / new at 8x, nothing written

The model change: each fist RISES `rows` (4) squares up his arm - his forearms that much shorter, every square of the
fist his own, only moved:
- the fist is the arm's part under its own outline: the cheapest path across the arm (data `fists` -> [first col, last
  col, first row, last row] of the design, hd/idle.png) through outline squares - an outline square costs nothing, a
  colour square one - and everything of the arm under it;
- laid back `rows` higher, in front of the arm (it covers the arm's lowest rows); the colour squares the path crossed
  (its top edge where no outline ran) made outline, as a stone's edge is; what it leaves is ground, a colour square of
  the leg beside it bared to the ground gets the outline;
- the frame's own pixels move (a flashed hit frame's white fist moves white); the frame is then thinned as
  tools/art/thin_outline.py leaves his frames.
Where (each frame is found against the design by its silhouette): the dense frames (hd_) of the tags that stand in his
design - idle_base (the idle and ban/pick reels' rest frame: hero_reels.py's rects), hit - and the run's drawn frames
(the rig's walk, the design's own body and fists over its stepping legs); their 1x frames (the rig's own drawing,
ppu_rig.one_of of the dense one: each 1x square of the fist where most of its dense squares are, `one_rows` up); their
lo_ frames (ppu_hd.add_lo grew the dense frames: every lo_ square grown from a changed dense square takes its new
value).
The run (`run`): the fists also swing as the steps go - `swing` -> fist: rows up a frame on top of `rows` (the near fist
with the far leg's step, the far fist with the near leg's: a knuckle walk); the run's sources
(assets/source/brock/hd/brock_run_drawn.png, brock_run_one.png, brock_run_lo.png) are written, run_body_anim.py lays the
run from them. Every other tag keeps his drawing (his attacks, skills and fall swing or plant the fists as the action
draws them)."""
import argparse
import heapq
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import thin_outline as T  # noqa: E402

HERO, SHORT = "tft_brock", "brock"
SRC = os.path.join(ROOT, "assets", "source", "brock", "hd")
DATA = os.path.join(SRC, "brock_fists.json")
UI_PPU = 1.5                                         # tools/art/ppu_hd.py UI_PPU
N4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def lp(path):
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    return path


def load_png(path):
    return np.array(Image.open(lp(path)).convert("RGBA"))


def dilate(m, it=1, st=None):
    """binary dilation (numpy only: CI has no scipy)"""
    st = N4 if st is None else st
    out = m.copy()
    for _ in range(it):
        cur = out.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if not st[dy + 1, dx + 1] or (dy == 0 and dx == 0):
                    continue
                sh = np.zeros_like(cur)
                ys = slice(max(0, dy), cur.shape[0] + min(0, dy))
                yd = slice(max(0, -dy), cur.shape[0] + min(0, -dy))
                xs = slice(max(0, dx), cur.shape[1] + min(0, dx))
                xd = slice(max(0, -dx), cur.shape[1] + min(0, -dx))
                sh[yd, xd] = cur[ys, xs]
                out |= sh
    return out


# ------------------------------------------------------------------------------------------------- the design's fists
def ink_of(a, oc):
    """the squares of an outline colour (oc: one colour, or a list of them)"""
    ocs = [oc] if isinstance(oc[0], (int, np.integer)) else oc
    m = np.zeros(a.shape[:2], bool)
    for c in ocs:
        m |= (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2])
    return m & (a[..., 3] > 0)


def flashed(c, k=0.45):
    """a colour as tools/art/ppu_rig.py's flash whitens it (the hit's first frame)"""
    return tuple(int(v * (1 - k) + 255 * k) for v in c)


def cut_path(D, oc, c0, c1, r0, r1):
    """the cheapest 8-connected path from column c0 to c1 within rows r0..r1 (outline or clear 0, colour 1)."""
    op = D[..., 3] > 0
    ink = ink_of(D, oc)
    W = D.shape[1]
    INF = 10 ** 9
    dist, prev, pq = {}, {}, []
    for r in range(r0, r1 + 1):
        cost = 0 if (ink[r, c0] or not op[r, c0]) else 1
        dist[(r, c0)] = cost
        heapq.heappush(pq, (cost, r, c0))
    end = None
    while pq:
        d, r, c = heapq.heappop(pq)
        if dist.get((r, c), INF) < d:
            continue
        if c == c1:
            end = (r, c)
            break
        for dr in (-1, 0, 1):
            rr, cc = r + dr, c + 1
            if not (r0 <= rr <= r1) or cc >= W:
                continue
            nd = d + (0 if (ink[rr, cc] or not op[rr, cc]) else 1) + (0.01 if dr else 0)
            if nd < dist.get((rr, cc), INF):
                dist[(rr, cc)] = nd
                prev[(rr, cc)] = (r, c)
                heapq.heappush(pq, (nd, rr, cc))
    pts = [end]
    while pts[-1] in prev:
        pts.append(prev[pts[-1]])
    return pts[::-1]


def design_fists(cfg):
    """-> (design, {fist: mask in the design}, [(row, col) design colour squares the cuts crossed])"""
    D = load_png(os.path.join(SRC, "idle.png"))
    oc = tuple(cfg["outline"])
    op = D[..., 3] > 0
    ink = ink_of(D, oc)
    masks, cut = {}, []
    for name, (c0, c1, r0, r1) in cfg["fists"].items():
        pts = cut_path(D, oc, c0, c1, r0, r1)
        m = np.zeros(op.shape, bool)
        top = {}
        for r, c in pts:
            top[c] = min(r, top.get(c, r))
        for c, r in top.items():
            m[r:, c] = True
        masks[name] = m & op
        cut += [(r, c) for r, c in pts if op[r, c] and not ink[r, c]]
    return D, masks, cut


# ------------------------------------------------------------------------------------------------- placing
def find_design(f, D, search=4):
    """(dy, dx) of the design's top-left in a dense frame: its silhouette laid where it covers the frame's best"""
    H, W = f.shape[:2]
    h, w = D.shape[:2]
    fm, dm = f[..., 3] > 0, D[..., 3] > 0
    best = None
    for dy in range(-search, H - h + search + 1):
        for dx in range(-search, W - w + search + 1):
            ya, yb, xa, xb = max(0, dy), min(H, dy + h), max(0, dx), min(W, dx + w)
            if yb <= ya or xb <= xa:
                continue
            s = int((fm[ya:yb, xa:xb] == dm[ya - dy:yb - dy, xa - dx:xb - dx]).sum())
            if best is None or s > best[0]:
                best = (s, dy, dx)
    return best[1], best[2]


def own_ring(f, masks, ocs, depth=2):
    """each fist with the frame's outline round it that is its own: outline squares within `depth` of the fist's colour
    squares and nearer to them than to any other colour square of the frame (a frame whose outline grew a ring the
    design does not have - the flashed hit - keeps no ring of the fist behind)"""
    op = f[..., 3] > 0
    ink = ink_of(f, ocs)
    col = op & ~ink
    out = {}
    for nm, m in masks.items():
        mine = m & col
        rest = col & ~mine
        for d in range(1, depth + 1):
            near_mine = dilate(mine, d, np.ones((3, 3), bool))
            near_rest = dilate(rest, d, np.ones((3, 3), bool))
            m = m | (ink & near_mine & ~near_rest)
        out[nm] = m
    return out


def pieces(m):
    """8-connected pieces of a mask -> [(rows, cols)] (numpy only)"""
    seen = np.zeros(m.shape, bool)
    out = []
    H, W = m.shape
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        stack, ys, xs = [(y0, x0)], [], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            ys.append(y)
            xs.append(x)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        out.append((np.array(ys), np.array(xs)))
    return out


def pieces4(m):
    """4-connected pieces of a mask -> [(rows, cols)] (numpy only)"""
    seen = np.zeros(m.shape, bool)
    out = []
    H, W = m.shape
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        stack, ys, xs = [(y0, x0)], [], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            ys.append(y)
            xs.append(x)
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        out.append((np.array(ys), np.array(xs)))
    return out


def placed(mask, shape, dy, dx):
    out = np.zeros(shape[:2], bool)
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < shape[0]) & (tx >= 0) & (tx < shape[1])
    out[ty[ok], tx[ok]] = True
    return out


def lift(f, masks, ups, oc, cut=None, paint=None):
    """the frame with each fist's squares (masks[name], in the frame) moved ups[name] rows up, laid over the frame;
    cut: the moved fists' top-edge squares made outline (frame squares, before the move); what they leave is ground,
    a colour square bared to the ground beside it gets the outline (`paint`: the outline colour laid - a flashed
    frame's own; oc: every outline colour of the frame). -> (frame, bared squares outlined)"""
    paint = tuple(oc if isinstance(oc[0], (int, np.integer)) else oc[0]) if paint is None else paint
    out = f.copy()
    op = f[..., 3] > 0
    gone = np.zeros(op.shape, bool)
    for m in masks.values():
        gone |= m & op
    out[gone] = 0
    put = np.zeros(op.shape, bool)
    for name, m in masks.items():
        n = ups[name]
        ys, xs = np.nonzero(m & op)
        ok = ys - n >= 0
        out[ys[ok] - n, xs[ok]] = f[ys[ok], xs[ok]]
        put[ys[ok] - n, xs[ok]] = True
        if cut is not None:
            cm = cut & m
            cy, cx = np.nonzero(cm)
            okc = cy - n >= 0
            out[cy[okc] - n, cx[okc], :3] = paint
            out[cy[okc] - n, cx[okc], 3] = 255
    left = gone & ~put
    op2 = out[..., 3] > 0
    col = op2 & ~ink_of(out, oc)
    bare = ~op2 & dilate(col) & dilate(left)
    out[bare, :3] = paint
    out[bare, 3] = 255
    # what is left of the fists' old outline cut off on its own (a piece of the ring the frame's outline grew round
    # them with no colour beside any square of it): cleared - near the fists only (the drawing's own dark gaps
    # between his stones touch his stones, and stay)
    op3 = out[..., 3] > 0
    ink3 = ink_of(out, oc)
    col3 = op3 & ~ink3
    lone = ink3 & ~dilate(col3, 1, np.ones((3, 3), bool))
    near = dilate(gone | put, 3, np.ones((3, 3), bool))
    for comp in pieces(ink3):
        if lone[comp].all() and near[comp].any():
            out[comp] = 0
    # what the fists leave shut in by his pieces (not open to the ground round him) is a gap between his stones:
    # dark, as the drawing draws those gaps - not a hole of ground in him
    clear = out[..., 3] == 0
    was_hole = np.zeros(clear.shape, bool)
    for comp in pieces4(f[..., 3] == 0):
        ys_, xs_ = comp
        if not (ys_.min() == 0 or xs_.min() == 0 or ys_.max() == clear.shape[0] - 1 or xs_.max() == clear.shape[1] - 1):
            was_hole[comp] = True
    for comp in pieces4(clear):
        ys_, xs_ = comp
        H_, W_ = clear.shape
        if ys_.min() == 0 or xs_.min() == 0 or ys_.max() == H_ - 1 or xs_.max() == W_ - 1:
            continue
        if was_hole[comp].all():
            continue                                  # (a pocket the drawing has)
        if (left[comp].any() and not (f[..., 3][comp] == 0).all()) or len(comp[0]) <= 2:
            out[comp[0], comp[1], :3] = paint
            out[comp[0], comp[1], 3] = 255
    return out, bare


def one_masks(f1, fd, dmasks, ppu):
    """the 1x frame's fist squares: the 1x squares (ppu_rig.one_of's grid about the frames' centres, aligned where the
    1x frame and the dense one agree best) where most of the dense squares under them are the fist's"""
    h1, w1 = f1.shape[:2]
    H, W = fd.shape[:2]
    best = None
    for ay in (-0.5, -0.25, 0.0, 0.25, 0.5):
        for ax in (-0.5, -0.25, 0.0, 0.25, 0.5):
            yy = np.floor(H / 2 + ay + (np.arange(h1) - h1 // 2) * ppu).astype(int)
            xx = np.floor(W / 2 + ax + (np.arange(w1) - w1 // 2) * ppu).astype(int)
            oky, okx = (yy >= 0) & (yy < H), (xx >= 0) & (xx < W)
            g = np.zeros((h1, w1), bool)
            g[np.ix_(oky, okx)] = fd[np.ix_(yy[oky], xx[okx])][..., 3] > 0
            s = int((g == (f1[..., 3] > 0)).sum())
            if best is None or s > best[0]:
                best = (s, ay, ax)
    _, ay, ax = best
    out = {}
    for name, dm in dmasks.items():
        m = np.zeros((h1, w1), bool)
        for j in range(h1):
            ya, yb = H / 2 + ay + (j - h1 // 2 - 0.5) * ppu, H / 2 + ay + (j - h1 // 2 + 0.5) * ppu
            for i in range(w1):
                xa, xb = W / 2 + ax + (i - w1 // 2 - 0.5) * ppu, W / 2 + ax + (i - w1 // 2 + 0.5) * ppu
                blk = dm[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                         max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))]
                m[j, i] = blk.size > 0 and blk.mean() >= 0.5
        out[name] = m & (f1[..., 3] > 0)
    return out


def one_cut(f1, masks, oc):
    """the 1x fists' top edge: a fist colour square with a colour square of the arm right over it (made outline when
    the fist rises over the arm)"""
    op = f1[..., 3] > 0
    col = op & ~ink_of(f1, oc)
    allm = np.zeros(op.shape, bool)
    for m in masks.values():
        allm |= m
    above = np.zeros(op.shape, bool)
    above[1:] = col[:-1] & ~allm[:-1]
    return allm & col & above


def grow_src(hshape, lshape, k):
    """lo_ square -> the dense square ppu_hd.add_lo grew it from (ppu_hd.grow about the frame's centre, nearest,
    centred on the lo_ rect): (row of the dense square per lo_ row, col per lo_ col), -1 where none"""
    H, W = hshape
    c = 1.0 / k
    px, py = W / 2, H / 2
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    sx = np.floor(px + (np.arange(nx0 + nx1) - nx0 + 0.5) * c).astype(int)
    sy = np.floor(py + (np.arange(ny0 + ny1) - ny0 + 0.5) * c).astype(int)
    LH, LW = lshape
    ox, oy = int(np.floor(LW / 2 - nx0 + 0.5)), int(np.floor(LH / 2 - ny0 + 0.5))
    ry, rx = np.full(LH, -1), np.full(LW, -1)
    for i, s in enumerate(sy):
        if 0 <= i + oy < LH and 0 <= s < H:
            ry[i + oy] = s
    for i, s in enumerate(sx):
        if 0 <= i + ox < LW and 0 <= s < W:
            rx[i + ox] = s
    return ry, rx


def lo_masks(fl, fd, masks, cut, k):
    """the lo_ frame's fist squares and cut squares: the lo_ squares ppu_hd.add_lo grew from the dense frame's"""
    ry, rx = grow_src(fd.shape[:2], fl.shape[:2], k)
    oky, okx = ry >= 0, rx >= 0
    out = {}
    for nm, m in masks.items():
        mm = np.zeros(fl.shape[:2], bool)
        mm[np.ix_(oky, okx)] = m[np.ix_(ry[oky], rx[okx])]
        out[nm] = mm & (fl[..., 3] > 0)
    cm = np.zeros(fl.shape[:2], bool)
    cm[np.ix_(oky, okx)] = cut[np.ix_(ry[oky], rx[okx])]
    return out, cm


def lo_from(lo, hd_old, hd_new, k):
    """the lo_ frame with every square grown from a dense square that changed given its new value"""
    ry, rx = grow_src(hd_new.shape[:2], lo.shape[:2], k)
    ch = (hd_old != hd_new).any(-1)
    out = lo.copy()
    oky, okx = ry >= 0, rx >= 0
    sub = np.zeros(lo.shape[:2], bool)
    sub[np.ix_(oky, okx)] = ch[np.ix_(ry[oky], rx[okx])]
    ys, xs = np.nonzero(sub)
    out[ys, xs] = hd_new[ry[ys], rx[xs]]
    return out


# ------------------------------------------------------------------------------------------------- the frames
def load_cfg():
    with open(lp(DATA), encoding="utf-8") as f:
        return json.load(f)


def sheet_frames(an, px, tag):
    out = []
    for fr in an[tag]["frames"]:
        x, y, w, h = (int(round(fr["data"][q])) for q in ("x", "y", "w", "h"))
        out.append(((x, y, w, h), px[y:y + h, x:x + w].copy(), int(round(fr["duration"] * 1000))))
    return out


def strip(frames):
    H = max(a.shape[0] for a in frames)
    s = np.zeros((H, sum(a.shape[1] + 1 for a in frames) - 1, 4), np.uint8)
    x = 0
    for a in frames:
        s[:a.shape[0], x:x + a.shape[1]] = a
        x += a.shape[1] + 1
    return s


def unstrip(s, sizes):
    out, x = [], 0
    for w, h in sizes:
        out.append(s[:h, x:x + w].copy())
        x += w + 1
    return out


def init():
    """the base: the sheet's frames of the tags this tool changes and the installed run (hd_run, run, lo_run), as they
    are now - the tool starts from them every time"""
    cfg = load_cfg()
    hid, pack, ppu, size = T.resolve(HERO, T.all_heroes())
    an, px = T.read(hid, pack)
    entries, frames = [], []
    for tag in cfg["tags"] + ["run"]:
        for pre in ("hd_", "", "lo_"):
            for i, (r, a, ms) in enumerate(sheet_frames(an, px, pre + tag)):
                entries.append({"tag": pre + tag, "i": i, "size": [a.shape[1], a.shape[0]], "ms": ms})
                frames.append(a)
    base = cfg["base"]
    Image.fromarray(strip(frames), "RGBA").save(lp(os.path.join(ROOT, base + ".png")), optimize=True)
    with open(lp(os.path.join(ROOT, base + ".json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"from": "the sheet's frames before the fists rose (tft/champions/tft_brock)", "frames": entries}, f)
    print(f"{HERO}: base kept, {len(entries)} frames")


def read_base(cfg):
    with open(lp(os.path.join(ROOT, cfg["base"] + ".json")), encoding="utf-8") as f:
        meta = json.load(f)
    s = load_png(os.path.join(ROOT, cfg["base"] + ".png"))
    fr = unstrip(s, [e["size"] for e in meta["frames"]])
    out = {}
    for e, a in zip(meta["frames"], fr):
        out.setdefault(e["tag"], []).append((a, e["ms"]))
    return out


def make(cfg=None):
    """-> {tag: [frame]} for hd_ / 1x / lo_ of cfg["tags"] and "run" (the run's sources), info lines"""
    cfg = cfg or load_cfg()
    hid, pack, ppu, size = T.resolve(HERO, T.all_heroes())
    oc = tuple(cfg["outline"])
    tp = T.load_state().get(hid)
    k = UI_PPU * size / ppu
    base = read_base(cfg)
    D, dmasks, dcut = design_fists(cfg)
    cutm_design = np.zeros(D.shape[:2], bool)
    for r, c in dcut:
        cutm_design[r, c] = True
    n = int(cfg["rows"])
    n1 = int(cfg["one_rows"])
    new, info = {}, []
    for tag in cfg["tags"] + ["run"]:
        hd, one, lo = base["hd_" + tag], base[tag], base["lo_" + tag]
        sw = cfg.get("run", {}).get("swing", {}) if tag == "run" else {}
        new["hd_" + tag], new[tag], new["lo_" + tag] = [], [], []
        for i, ((fd, _), (f1, _), (fl, _)) in enumerate(zip(hd, one, lo)):
            dy, dx = find_design(fd, D)
            fl_ = i in cfg.get("flash", {}).get(tag, [])          # (the hit's first frame: whitened)
            ocs = [oc, flashed(oc)] if fl_ else [oc]
            paint = flashed(oc) if fl_ else oc
            masks = {nm: placed(m, fd.shape, dy, dx) & (fd[..., 3] > 0) for nm, m in dmasks.items()}
            masks = own_ring(fd, masks, ocs)
            cut = placed(cutm_design, fd.shape, dy, dx)
            ups = {nm: n + int(sw.get(nm, [0] * (i + 1))[i]) for nm in dmasks}
            g, bare = lift(fd, masks, ups, ocs, cut, paint)
            if tp is not None:
                g = T.change_fixed(g, tp["hd"], tp["outline"], tp["grow"])[0]
            m1 = one_masks(f1, fd, masks, ppu)
            ups1 = {nm: n1 + int(round(int(sw.get(nm, [0] * (i + 1))[i]) / ppu)) for nm in dmasks}
            g1, _ = lift(f1, m1, ups1, ocs, one_cut(f1, m1, ocs), paint)
            ml, cutl = lo_masks(fl, fd, masks, cut, k)
            ml = own_ring(fl, ml, ocs)
            upsl = {nm: int(round(u * k)) for nm, u in ups.items()}
            gl, _ = lift(fl, ml, upsl, ocs, cutl, paint)
            if tp is not None:
                gl = T.change_fixed(gl, tp["lo"], tp["outline"], tp["grow"])[0]
            new["hd_" + tag].append(g)
            new[tag].append(g1)
            new["lo_" + tag].append(gl)
            info.append(f"{tag} {i}: design at {dy},{dx}; fists up {ups} (1x {ups1}); dense changed "
                        f"{int((g != fd).any(-1).sum())}, 1x {int((g1 != f1).any(-1).sum())}, lo_ "
                        f"{int((gl != fl).any(-1).sum())}; bared edge outlined {int(bare.sum())}")
    return new, info, base


def run(check=False, review=None):
    cfg = load_cfg()
    hid, pack, ppu, size = T.resolve(HERO, T.all_heroes())
    new, info, base = make(cfg)
    an, px = T.read(hid, pack)
    px2 = px.copy()
    bad = []
    for tag in cfg["tags"]:
        for pre in ("hd_", "", "lo_"):
            for i, (r, a, ms) in enumerate(sheet_frames(an, px, pre + tag)):
                x, y, w, h = r
                b = new[pre + tag][i]
                if b.shape != a.shape:
                    sys.exit(f"{pre + tag} {i}: the made frame is {b.shape[1]}x{b.shape[0]}, its rect {w}x{h}")
                px2[y:y + h, x:x + w] = b
    n_sheet = int((px2 != px).any(-1).sum())
    if n_sheet:
        bad.append(f"sheet: {n_sheet} squares")
    # the strips tools/art/ppu_hd.py reads (assets/source/ppu/brock_<tag>.png): each frame its hd_ frame
    strips = []
    for tag in cfg["tags"]:
        name = "idle" if tag == "idle_base" else tag
        path = os.path.join(T.STRIPS, f"{SHORT}_{name}.png")
        with open(lp(path[:-4] + ".json"), encoding="utf-8") as f:
            sizes = json.load(f)["sizes"]
        s = load_png(path)
        fr = new["hd_" + tag]
        if [[a.shape[1], a.shape[0]] for a in fr] != sizes:
            sys.exit(f"{path}: sizes {sizes}, the tag's {[[a.shape[1], a.shape[0]] for a in fr]}")
        s2 = strip(fr)
        if s2.shape != s.shape or (s2 != s).any():
            bad.append(f"{os.path.relpath(path, ROOT)}: differs")
            strips.append((path, s2))
    # the run's sources (run_body_anim.py lays the run from them)
    runs = []
    meta_path = os.path.join(SRC, "brock_run_drawn.json")
    with open(lp(meta_path), encoding="utf-8") as f:
        meta = json.load(f)
    for suffix, tag in (("drawn", "hd_run"), ("one", "run"), ("lo", "lo_run")):
        path = os.path.join(SRC, f"brock_run_{suffix}.png")
        s2 = strip(new[tag])
        s = load_png(path) if os.path.exists(lp(path)) else None
        if s is None or s2.shape != s.shape or (s2 != s).any():
            bad.append(f"{os.path.relpath(path, ROOT)}: differs")
            runs.append((path, s2))
    want = {"sizes": [[a.shape[1], a.shape[0]] for a in new["hd_run"]],
            "one_sizes": [[a.shape[1], a.shape[0]] for a in new["run"]],
            "lo_sizes": [[a.shape[1], a.shape[0]] for a in new["lo_run"]]}
    for key_, v in want.items():
        if meta.get(key_) != v:
            bad.append(f"brock_run_drawn.json {key_}: {meta.get(key_)} != {v}")
    if review:
        write_review(review, base, new, cfg, info)
        print(f"{HERO}: review in {review}")
        return
    if check:
        if bad:
            print("\n".join(bad))
            sys.exit(f"{HERO}: fists not as brock_fists.py makes them - run tools/art/brock_fists.py, then "
                     "tools/art/run_body_anim.py --hero brock")
        print(f"ok: {HERO}'s fists are off the ground on every standing frame")
        return
    if n_sheet:
        Image.fromarray(px2, "RGBA").save(lp(T.stem(hid, pack) + "#sheet.png"), optimize=True)
    for path, s2 in strips + runs:
        Image.fromarray(s2, "RGBA").save(lp(path), optimize=True)
    meta.update(want)
    with open(lp(meta_path), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f)
    print("\n".join(info))
    print(f"{HERO}: " + ("; ".join(bad) if bad else "nothing to change"))


def write_review(out_dir, base, new, cfg, info):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "brock_fists.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(info) + "\n")
    for tag in cfg["tags"] + ["run"]:
        for pre, z in (("hd_", 6), ("", 8), ("lo_", 5)):
            olds = [a for a, _ in base[pre + tag]]
            news = new[pre + tag]
            H = max(a.shape[0] for a in olds + news)
            W = max(a.shape[1] for a in olds + news)
            rows = []
            for fs in (olds, news):
                row = np.zeros((H, (W + 2) * len(fs), 4), np.uint8)
                row[..., :3] = (96, 112, 84)
                row[..., 3] = 255
                for j, a in enumerate(fs):
                    oy, ox = (H - a.shape[0]) // 2, j * (W + 2) + (W - a.shape[1]) // 2
                    m = a[..., 3] > 0
                    sub = row[oy:oy + a.shape[0], ox:ox + a.shape[1]]
                    sub[m] = a[m]
                rows.append(row)
            img = np.concatenate([rows[0], np.zeros((2, rows[0].shape[1], 4), np.uint8), rows[1]], 0)
            Image.fromarray(np.repeat(np.repeat(img, z, 0), z, 1)).save(os.path.join(out_dir, f"{pre}{tag}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", metavar="DIR")
    a = ap.parse_args()
    if a.init:
        init()
        return
    run(a.check, a.review)


if __name__ == "__main__":
    main()
