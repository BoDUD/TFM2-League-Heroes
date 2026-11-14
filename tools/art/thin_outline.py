#!/usr/bin/env python3
"""Thinner dark outlines on the dense (PPU) hero frames, from the inside (the user, 2026-11-14, on a screenshot of Fizz:
「有些英雄黑边太粗了 都检查一下 发条那种就正常」).

    python -I tools/art/thin_outline.py --hero fizz [--hero darius ...]   # rewrite the heroes' hd_ / lo_ frames (+ strips)
    python -I tools/art/thin_outline.py --check                           # every hero in thin_outline.json: exit 1 when
                                                                          # a frame would still change (CI)
    python -I tools/art/thin_outline.py --hero fizz --dry --review DIR    # before / after pictures, nothing written
    python -I tools/art/thin_outline.py --hero fizz --fresh               # measure BAND again (frames redrawn thick)
    python -I tools/art/thin_outline.py --audit [--json PATH]             # every dense hero of both packs: band, game px

Why the band is thick. Most dense frames carry a near-black outline band several squares deep: the design's own
outline as Codex drew it, read on the design's squares, plus the squares tools/art/ppu_restyle.py grew round it
(RESTYLE `edge`: 2 for most of the heroes redone since 2026-11-01 - the user then: 「伊芙琳可以加点黑边 避免过度高清」
「诺手现在应该也要加点」「狼人加点黑边」). On the battlefield a frame is drawn at 1 / PPU (hd.rs HEROES; SIZES on top), so a
band of n squares is n x SIZES / PPU game pixels: league_orianna 2 squares at 2.25 = 0.89 (the user's 「正常」),
league_fizz 4 at 1.8125 = 2.2, league_darius 4 at 1.45 = 2.8.

What changes. Only squares of the hero's own outline colour(s) that belong to the band - the run of those colours from
the frame's clear edge inward - and only deeper than KEEP squares from the edge: they take the colour of the body right
behind them. The silhouette (every alpha value) never changes, so the model is exactly as big as before (「模型不要变大变
小」); the .fanim is not touched (league.dll embeds the .fanim only).

- Outline colours: the commonest colour of the frames' outermost layer, with the near-identical near-blacks of the outer
  six layers (league_orianna's design outline (9, 3, 15) under the restyle's (8, 2, 16); RGB L1 distance <= 24). A hero
  whose outermost colour is not dark has no outline to thin.
- Layers: Manhattan depth from the clear squares (grow_edge's CROSS growth is the same measure). The band: the outline
  colour at depth 1, then at each next depth where it touches the band one layer out and either has two band squares
  beside it at its own depth or goes no deeper - an inner line running in from the edge is not band.
- KEEP: the whole number of squares nearest TARGET (1 game px) by ratio, sqrt(n(n-1)) <= PPU / SIZES < sqrt(n(n+1)):
  1 below 1.414, 2 up to 2.449 (league_orianna's 2 at 2.25), 3 up to 3.46; the lo_ frames (UI_PPU 1.5) keep 2.
- BAND: the 85th percentile of the edge squares' band depth over the hero's frames (and the median), measured once before
  the first run and kept in thin_outline.json - after the run the frames no longer show it. A hero whose median band is
  KEEP or less is left alone (league_orianna, league_garen).
- What stays as drawn:
  * a band running deeper than BAND + 1 (black hair, the slit between a trident's tines), with the squares in front of it;
  * a thin part - a staff, a ring, a claw, a tine: its width inside the kept outline (a disc or upright square of the
    silhouette holding the square; dark blobs of 3 x 3 the change never reaches, a ring's eye, counted as holes) less its
    own band beyond KEEP on both sides is 2 or less (league_darius's staff: 2 squares in a band of 4), and the band behind
    a kept square;
  * the band between two parts (body colour on both sides within 3 squares: a face and a pauldron, a staff and a body);
  * a lone square to change among kept ones at its depth (it would grow a one-square spike).
- The colour: the body square the band square is nearest (grown from the body outward, the square straight inside first),
  the commonest of the body's edge colours round it (5 x 5: a single odd square there is not grown into a ray); a
  highlight (40+ luma over the commonest body colour round it, over the body square behind it, or over the median luma of
  the body round it - league_brand's yellow eye on his dark face) is not grown - the body's colour there takes its
  place, the highlight stays where it was drawn. Then a band square left alone inside the new colour, and a speck of 3
  squares or fewer the change cut off (the end of an inner line that ran into the band), take the colour round them.
- Every rule reads what the change leaves alone (alpha, the colours deeper than BAND + 1, the kept squares, the stored
  BAND / KEEP), so one pass is a fixed point; thin_fixed() repeats it until nothing changes (2026-11-15, 81 heroes: a
  second pass changed 0-14 squares of a hero), and --check wants a pass to change nothing.

thin_outline.json: {hero id: {"outline": [[r, g, b], ...], "hd": {"band", "deep", "median", "keep"}, "lo": {...}}},
written by the first run of a hero; a later run uses it (--keep N changes the hd_ "keep" of the heroes named). A hero
whose entry is {"skip": why} is never touched (league_akshan: his new frames are in the install tree, not here yet;
league_volibear: his storm-form twins). Run over the heroes after a pipeline run that writes their dense frames again
(tools/art/ppu_restyle.py, ppu_hd.py): CI's --check fails until it is.

Frames another tool makes from a hero's own frames (DERIVED) are not thinned here: that tool makes them again from the
thinned frames - league_aatrox's hover tags, tools/art/hover_aatrox.py (run it after this; its --check is in CI).

The strips tools/art/ppu_hd.py reads (assets/source/ppu/<hero>_<tag>.png) get the same change where every frame of the
strip is its sheet's hd_ frame square for square, so `ppu_hd.py --hero <hero>` writes the thinned frames again. Their
own source (assets/source/ppu/orig/, tools/art/ppu_restyle.py) is not touched: a restyle run writes thick strips, and
this tool has to run after it.
"""
import argparse
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PACKS = ("league", "tft")
TABLES = {"league": os.path.join(ROOT, "addons", "league_main", "src", "hd.rs"),
          "tft": os.path.join(ROOT, "addons", "tft", "src", "hd.rs")}
STRIPS = os.path.join(ROOT, "assets", "source", "ppu")
STATE = os.path.join(HERE, "thin_outline.json")
UI_PPU = 1.5            # the lo_ frames' squares a displayed game pixel (tools/art/ppu_hd.py UI_PPU)
TARGET = 1.0            # game pixels of outline wanted (league_orianna's 2 squares at 2.25 = 0.89)
NEAR = 24               # RGB L1 distance of an outline colour's near-identical twins
PERCENTILE = 85         # BAND: this percentile of the edge squares' band depth
HIGHLIGHT = 40          # luma over the body round it or behind it: a highlight, not grown
N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
N8 = N4 + ((-1, -1), (-1, 1), (1, -1), (1, 1))


# ------------------------------------------------------------------------------------------------------- the tables
def table(pack):
    """hd.rs HEROES and SIZES of a pack -> ({id: ppu}, {id: size})."""
    src = open(TABLES[pack], encoding="utf-8").read()
    m = re.search(r"pub const HEROES[^=]*=\s*&\[(.*?)\n\];", src, re.S)
    ppu = {h: float(v) for h, v in re.findall(r'\(\s*"(\w+)",\s*([0-9.]+),\s*include_str!', m.group(1))}
    m = re.search(r"pub const SIZES[^=]*=\s*&\[(.*?)\];", src, re.S)
    size = {h: float(v) for h, v in re.findall(r'\("(\w+)",\s*([0-9.]+)\)', m.group(1))} if m else {}
    return ppu, size


def all_heroes():
    """[(id, pack, ppu, size)] for every dense hero of both packs, in table order."""
    out = []
    for pack in PACKS:
        ppu, size = table(pack)
        out += [(h, pack, p, size.get(h, 1.0)) for h, p in ppu.items()]
    return out


def resolve(name, heroes):
    """'fizz', 'league_fizz', 'powder' or 'tft_powder' -> its (id, pack, ppu, size)."""
    for row in heroes:
        if name in (row[0], row[0].split("_", 1)[1]):
            return row
    sys.exit(f"{name}: not a dense hero (HEROES in addons/league_main/src/hd.rs or addons/tft/src/hd.rs)")


def keep_for(density):
    """The whole number of squares nearest TARGET game px, by ratio: n with sqrt(n(n-1)) <= density x TARGET < sqrt(n(n+1))."""
    d, n = density * TARGET, 1
    while d >= math.sqrt(n * (n + 1)):
        n += 1
    return n


def stem(hero, pack):
    return os.path.join(ROOT, pack, "champions", hero)


def strip_name(hero):
    return hero.split("_", 1)[1]


# ------------------------------------------------------------------------------------------------------- the sheet
def read(hero, pack):
    with open(stem(hero, pack) + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    px = np.array(Image.open(stem(hero, pack) + "#sheet.png").convert("RGBA"))
    return anims, px


def is_fx(tag):
    """An effect layer kept in the hero's sheet (league_kayn's skill2_fx1, league_aatrox's q2_fx1): no body, not ours."""
    return re.search(r"_fx\d*$", tag) is not None


# a hero's tags another tool makes from its own frames: not thinned here, made again by that tool from the thinned ones
DERIVED = {
    # tools/art/hover_aatrox.py: the hover (r_hover, r_run), r_hit's push back and flash, r_ult settling on the hover -
    # REST and ult's frames moved, bent or flashed (its --check in CI wants them as it makes them)
    "league_aatrox": ("r_hover", "r_run", "r_hit", "r_ult"),
}


def rects(anims, prefix, derived=()):
    """The distinct frame rects of the `prefix` tags (hd_ / lo_) -> [(x, y, w, h)]: effect layers left out, and the rects
    only `derived` tags use."""
    seen, fx, own = [], set(), set()
    for tag, a in anims.items():
        if not tag.startswith(prefix):
            continue
        base = tag[len(prefix):]
        for f in a["frames"]:
            d = f["data"]
            r = tuple(int(d[k]) for k in ("x", "y", "w", "h"))
            if is_fx(base):
                fx.add(r)
                continue
            if r not in seen:
                seen.append(r)
            if base not in derived:
                own.add(r)
    return [r for r in seen if r not in fx and r in own]


# ------------------------------------------------------------------------------------------------------- geometry
def shift(m, dy, dx, fill=0):
    """out[y, x] = m[y + dy, x + dx], `fill` outside."""
    H, W = m.shape[:2]
    out = np.full_like(m, fill)
    out[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)] = m[max(0, dy):H - max(0, -dy), max(0, dx):W - max(0, -dx)]
    return out


def dil4(m):
    out = m.copy()
    for dy, dx in N4:
        out |= shift(m, dy, dx, False)
    return out


def ero4(m):
    out = m.copy()
    for dy, dx in N4:
        out &= shift(m, dy, dx, False)
    return out


def depth(op, cap):
    """Manhattan depth of every opaque square from the clear ones (the frame's border is clear): 1 on the edge, ... up
    to cap + 1 for everything deeper; 0 where clear."""
    L = np.zeros(op.shape, np.int32)
    cur, d = op.copy(), 1
    while cur.any() and d <= cap:
        e = ero4(cur)
        L[cur & ~e] = d
        cur, d = e, d + 1
    L[cur] = cap + 1
    return L


def open_sq(m, k):
    """The union of every k x k square wholly inside m."""
    if k <= 1:
        return m.copy()
    H, W = m.shape
    if H < k or W < k:
        return np.zeros_like(m)
    c = np.zeros((H + 1, W + 1), np.int32)
    c[1:, 1:] = m.astype(np.int32).cumsum(0).cumsum(1)
    full = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) == k * k      # top-left corners, (H-k+1, W-k+1)
    e = np.zeros((H + 1, W + 1), np.int32)
    e[1:H - k + 2, 1:W - k + 2] = full.astype(np.int32)
    e = e.cumsum(0).cumsum(1)
    ys, xs = np.arange(H), np.arange(W)
    y0, x0 = np.maximum(ys - k + 1, 0), np.maximum(xs - k + 1, 0)
    cnt = e[(ys + 1)[:, None], (xs + 1)[None, :]] - e[y0[:, None], (xs + 1)[None, :]] - \
        e[(ys + 1)[:, None], x0[None, :]] + e[y0[:, None], x0[None, :]]
    return cnt > 0


def label4(m):
    """4-connected parts of m numbered 1.. (0 outside m)."""
    H, W = m.shape
    lab = np.where(m, np.arange(1, H * W + 1, dtype=np.int64).reshape(H, W), 0)
    while True:
        prev = lab
        for dy, dx in N4:
            nb = shift(lab, dy, dx, 0)
            lab = np.where(m & (nb > 0) & (nb < lab), nb, lab)
        if (lab == prev).all():
            break
    u = np.unique(lab[lab > 0])
    remap = np.zeros(int(lab.max()) + 1, np.int64)
    remap[u] = np.arange(1, len(u) + 1)
    return remap[lab]


def keys(a):
    return (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2].astype(np.int64)


def unkey(k):
    return np.stack([(k >> 16) & 255, (k >> 8) & 255, k & 255], -1).astype(np.uint8)


def luma(k):
    c = unkey(k).astype(float)
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def window_mode(key, mask, r, prefer=None):
    """Every square: the commonest key among the squares of `mask` in its (2r+1)^2 window (-1 where none); ties go to
    `prefer` (the square's own key) when it is among the commonest, else to the first in window order."""
    H, W = key.shape
    offs = [(dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1)]
    ks = np.stack([shift(key, dy, dx, -1) for dy, dx in offs])
    ms = np.stack([shift(mask, dy, dx, False) for dy, dx in offs])
    ks = np.where(ms, ks, -1)
    cnt = np.zeros(ks.shape, np.int32)
    for j in range(len(offs)):
        cnt += (ks == ks[j][None]) & (ks[j][None] >= 0)
    cnt[ks < 0] = 0
    best = cnt.max(0)
    pick = ks[np.argmax(cnt, 0), np.arange(H)[:, None], np.arange(W)[None, :]]
    if prefer is not None:
        own = np.zeros((H, W), np.int32)
        for j in range(len(offs)):
            own += (ks[j] == prefer) & (prefer >= 0)
        pick = np.where((own == best) & (best > 0), prefer, pick)
    return np.where(best > 0, pick, -1)


# ------------------------------------------------------------------------------------------------------- the band
def outline_colours(frames):
    """The hero's outline colours from its dense frames: the commonest colour of the outermost layer first, then its
    near-identical near-blacks found in the outer six layers."""
    edge, outer = {}, {}
    for a in frames:
        op = a[..., 3] > 0
        if not op.any():
            continue
        L = depth(op, 6)
        for m, acc in ((L == 1, edge), ((L >= 1) & (L <= 6), outer)):
            v, n = np.unique(keys(a)[m], return_counts=True)
            for k, c in zip(v.tolist(), n.tolist()):
                acc[k] = acc.get(k, 0) + c
    if not edge:
        return []
    c0 = max(edge, key=lambda k: (edge[k], k))
    base = unkey(np.array(c0)).astype(int)
    if base.max() > 64:                     # the edge is a body colour: no outline to thin
        return []
    out = [c0]
    for k in sorted(outer, key=lambda k: (-outer[k], k)):
        c = unkey(np.array(k)).astype(int)
        if k != c0 and np.abs(c - base).sum() <= NEAR and c.max() <= 64:
            out.append(k)
    return [unkey(np.array(k)).tolist() for k in out]


def is_outline(a, oc):
    k = keys(a)
    m = np.zeros(k.shape, bool)
    for c in oc:
        m |= k == ((c[0] << 16) | (c[1] << 8) | c[2])
    return m & (a[..., 3] > 0)


def band(a, oc, cap):
    """-> (op, L, O, Bo): opaque, depth, outline colour, the band - outline colour at depth 1, then at each next depth
    touching the band one layer out and either with two band squares beside it at its own depth (8-neighbours) or going
    no deeper (a bump of the band): an inner line running in from the edge is neither - down to cap."""
    op = a[..., 3] > 0
    L = depth(op, cap + 1)
    O = is_outline(a, oc)
    Bo = O & (L == 1)
    prev = Bo
    for n in range(2, cap + 1):
        cur = O & (L == n) & dil4(prev)
        side = np.zeros(cur.shape, np.int32)
        for dy, dx in N8:
            side += shift(cur, dy, dx, False)
        on = dil4(O & (L == n + 1))
        cur &= (side >= 2) | ~on
        Bo |= cur
        prev = cur
        if not cur.any():
            break
    return op, L, O, Bo


def edge_depths(a, oc, cap=12):
    """The band depth under every square of the outermost layer (0 where it is not outline colour)."""
    op, L, O, Bo = band(a, oc, cap)
    reach = np.where(Bo, L, 0)
    for n in range(cap - 1, 0, -1):
        deeper = np.zeros(L.shape, np.int32)
        for dy, dx in N4:
            deeper = np.maximum(deeper, shift(np.where(Bo & (L == n + 1), reach, 0), dy, dx, 0))
        lay = Bo & (L == n)
        reach[lay] = np.maximum(reach[lay], deeper[lay])
    return reach[op & (L == 1)]


def measure(frames, oc):
    """-> (median, 85th percentile) band depth over every edge square of the frames."""
    d = np.concatenate([edge_depths(a, oc) for a in frames if (a[..., 3] > 0).any()] or [np.zeros(1, np.int32)])
    return float(np.median(d)), int(np.ceil(np.percentile(d, PERCENTILE)))


def kind_params(frames, oc, keep):
    """{"band": the 85th percentile of the edge squares' band depth, "deep": that + 1, "median": the median's, "keep"}."""
    med, p85 = measure(frames, oc)
    return {"band": p85, "deep": p85 + 1, "median": med, "keep": keep}


# ------------------------------------------------------------------------------------------------------- the change
def part_width(R, most):
    """Each square of R: how wide the part of R holding it is - 2r + 1 for the biggest disc of radius r inside R that
    holds it (round, so a diagonal staff reads as wide as an upright one and a round head's edge as wide as the head),
    counted up to `most`."""
    rmax = most // 2 + 1
    offs = sorted(((dy, dx) for dy in range(-rmax, rmax + 1) for dx in range(-rmax, rmax + 1)
                   if 0 < dy * dy + dx * dx <= rmax * rmax), key=lambda o: (o[0] * o[0] + o[1] * o[1], o))
    d2 = np.where(R, rmax * rmax + 1, 0)                 # squared distance to the nearest square outside R
    out = ~R
    for dy, dx in offs:
        q = dy * dy + dx * dx
        hit = shift(out, dy, dx, True) & (d2 > q)
        d2[hit] = q
    width = R.astype(np.int32)
    for r in range(1, rmax):
        centres = d2 > (r + 0.5) ** 2                  # a disc of radius r round it stays inside R
        if not centres.any():
            break
        disc = np.zeros(R.shape, bool)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dy * dy + dx * dx <= r * r:
                    disc |= shift(centres, dy, dx, False)
        width[disc & R] = 2 * r + 1
    return width


def square_width(R, most):
    """Each square of R: the biggest k <= most with a k x k square inside R holding it (exact for upright parts, odd
    or even, where part_width's discs read 2n as 2n - 1)."""
    w = R.astype(np.int32)
    for k in range(2, most + 1):
        o = open_sq(R, k)
        if not o.any():
            break
        w[o] = k
    return w


def thin(a, oc, P, masks=False):
    """One frame -> (new frame, {what changed}). P: {"band": the hero's usual band depth, "deep": a band deeper than this
    is a dark part of the design, "keep": squares kept}. masks: the stats also hold the band, cone and slim masks."""
    out = a.copy()
    T, D, K = P["band"], P["deep"], P["keep"]
    if P.get("median", T) <= K or T <= K or not (a[..., 3] > 0).any():      # the usual band already thin enough
        return out, {"filled": 0}
    op, L, O, Bo = band(a, oc, D + 1)
    X = Bo & (L > K) & (L <= D)
    if not X.any():
        return out, {"filled": 0}
    H, W = op.shape
    # a band running deeper than D (black hair, a slit between a trident's tines) and the squares in front of it, out
    # to the kept outline - read off the colours at depth D and deeper only, which the change never reaches: outline
    # colour at D + 1 touching outline colour at D with two such beside it at its depth (a mass, not the end of a line)
    deep = O & (L == D + 1) & dil4(O & (L == D))
    side = np.zeros(deep.shape, np.int32)
    for dy, dx in N8:
        side += shift(deep, dy, dx, False)
    cone = deep & (side >= 2)
    for n in range(D, K, -1):
        cone |= op & (L == n) & dil4(cone & (L == n + 1))
    # a thin part (a staff, a ring, a claw, a tine) keeps its band as drawn: its width inside the kept outline (less the
    # dark blobs no change reaches: a ring's eye, a slit's end) less its own band beyond KEEP on both sides is 2 or less -
    # its own band: how deep the outline colour runs inward from it, one layer a step (league_darius's staff: 2 squares
    # in a band of 4 where his usual band is 3). A part kept so keeps that band and is read the same by a second run
    holes = open_sq(O & ((L > D) | cone), 3)
    R = op & (L > K) & ~holes
    run = np.where(O & (L <= D + 1), L, 0)
    for n in range(D, K, -1):
        inner = np.zeros(L.shape, np.int32)
        for dy, dx in N4:
            inner = np.maximum(inner, shift(np.where(O & (L == n + 1), run, 0), dy, dx, 0))
        lay = O & (L == n)
        run[lay] = np.maximum(run[lay], inner[lay])
    width = np.maximum(part_width(R, 2 * (D - K) + 6), square_width(R, 2 * (D - K) + 6))
    zone = O & (L > K) & (L <= D)                       # (any outline square at the band's depths, band or not yet)
    slim = zone & (width - 2 * (np.minimum(run, D) - K) <= 2)
    for n in range(K + 1, D):                           # and the outline behind a kept square, so its run stays whole
        slim |= zone & (L == n + 1) & dil4(slim & (L == n))
    # the band between two parts (a face and a pauldron, a staff and the body): body colour on both sides of it within
    # BAND - KEEP + 1 squares (3 at most), across or along a diagonal - two outlines merged there, kept as drawn (a second
    # run finds it so or finds more body, never less)
    core = op & ~O
    s_ = min(T - K + 1, 3)
    slit = np.zeros(L.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        pos = np.zeros(L.shape, bool)
        neg = np.zeros(L.shape, bool)
        for k in range(1, s_ + 1):
            pos |= shift(core, k * dy, k * dx, False)
            neg |= shift(core, -k * dy, -k * dx, False)
        slit |= pos & neg
    ok = X & ~cone & ~slim & ~slit
    # a lone square to change among kept ones at its depth would grow a one-square spike of colour: kept too (read off
    # the kept squares, which stay as they are, so a second run reads it the same)
    free = zone & ~cone & ~slim & ~slit
    mates = np.zeros(L.shape, np.int32)
    for dy, dx in N8:
        mates += shift(free, dy, dx, False) & (shift(L, dy, dx, 0) == L)
    ok &= mates >= 1
    # colours: grown from the body (not outline colour) outward through the squares to change, the one straight
    # inside first
    key = keys(a)
    edge_body = core & dil4(ok)
    smooth = window_mode(key, edge_body, 2, prefer=key)            # along the body's edge
    common = window_mode(key, core, 2)                             # the body round it
    # the body square straight behind it (one layer deeper)
    behind = np.full(L.shape, -1, np.int64)
    bestL = np.zeros(L.shape, np.int32)
    for dy, dx in N4:
        nk = shift(np.where(core, key, -1), dy, dx, -1)
        nL = shift(L, dy, dx, 0)
        take = (nk >= 0) & (nL > L) & (nL > bestL)
        behind[take], bestL[take] = nk[take], nL[take]
    s_l = luma(np.maximum(smooth, 0))
    lift = (smooth >= 0) & (common >= 0) & (s_l - luma(np.maximum(common, 0)) > HIGHLIGHT)
    rim = (smooth >= 0) & (behind >= 0) & (s_l - luma(np.maximum(behind, 0)) > HIGHLIGHT)
    # a highlight on the body's edge is not grown, what is behind it is (the highlight stays where it was drawn)
    colour = np.where(lift, common, np.where(rim, behind, smooth))
    # and a small bright thing on the edge of a body of many shades (league_brand's eye on his dark face: the eye's
    # yellow the commonest single colour round it): over the median luma of the body round it, the commonest colour of
    # the body there that is not
    lum_core = np.where(core, luma(key), np.nan)
    stack = np.stack([shift(lum_core, dy, dx, np.nan) for dy in range(-2, 3) for dx in range(-2, 3)])
    with np.errstate(all="ignore"):
        med = np.nanmedian(np.where(np.isnan(stack).all(0, keepdims=True), 0.0, stack), 0)
    c_l = luma(np.maximum(colour, 0))
    for y, x in zip(*np.nonzero(edge_body & (colour >= 0) & (c_l - med > HIGHLIGHT))):
        y0, y1, x0, x1 = max(0, y - 2), y + 3, max(0, x - 2), x + 3
        ks = key[y0:y1, x0:x1][core[y0:y1, x0:x1]]
        ks = ks[luma(ks) <= med[y, x] + HIGHLIGHT / 2]
        if len(ks):
            v, n = np.unique(ks, return_counts=True)
            colour[y, x] = v[np.argmax(n)]
    colour = np.where(core & (colour < 0), key, colour)
    have = np.where(core, colour, -1)
    todo = ok.copy()
    while todo.any():
        best = np.full((H, W), -1, np.int32)
        got = np.full((H, W), -1, np.int64)
        for dy, dx in N4:
            nb = shift(have, dy, dx, -1)
            nL = shift(L, dy, dx, -1)
            take = todo & (nb >= 0) & (nL > best)
            got[take], best[take] = nb[take], nL[take]
        new = todo & (got >= 0)
        if not new.any():
            break
        have[new] = got[new]
        todo &= ~new
    filled = ok & (have >= 0)
    out[filled, :3] = unkey(have[filled])
    # an outline square of the band's depths left alone inside the new colour (three sides or more not outline, going
    # no deeper: not an inner line's end): the colour round it
    left = (L > K) & (L <= D + 1) & ~cone & ~slim & ~slit
    while True:
        Oc = is_outline(out, oc)
        deeper_o = np.zeros((H, W), bool)
        for dy, dx in N4:
            deeper_o |= shift(Oc, dy, dx, False) & (shift(L, dy, dx, 0) > L)
        cur = left & Oc & ~deeper_o
        k2 = keys(out)
        n = np.zeros((H, W), np.int32)
        for dy, dx in N4:
            n += shift(op & ~Oc, dy, dx, False)
        st = cur & (n >= 3)
        if not st.any():
            break
        nb = np.stack([np.where(shift(op & ~Oc, dy, dx, False), shift(k2, dy, dx, -1), -1) for dy, dx in N4])
        cnt = np.zeros(nb.shape, np.int32)
        for j in range(4):
            cnt += (nb == nb[j][None]) & (nb[j][None] >= 0)
        cnt[nb < 0] = 0
        pick = nb[np.argmax(cnt, 0), np.arange(H)[:, None], np.arange(W)[None, :]]
        out[st, :3] = unkey(pick[st])
        filled |= st
    # a speck of outline colour (three squares or fewer) the change cut off inside the new colour - the end of an
    # inner line that ran into the band, now touching neither the kept outline nor the outline deeper in: the colour
    # round it
    if filled.any():
        Oc = is_outline(out, oc)
        loose = Oc & left & dil4(filled)
        lab = label4(Oc & (L > K) & (L <= D + 1))
        if lab.max():
            n_lab = lab.max() + 1
            size = np.bincount(lab.ravel(), minlength=n_lab)
            anchored = np.zeros(n_lab, bool)
            touch = dil4(Oc & ((L <= K) | (L > D + 1)))
            anchored[np.unique(lab[touch & (lab > 0)])] = True
            fixed = np.zeros(n_lab, bool)
            fixed[np.unique(lab[(cone | slim | slit) & (lab > 0)])] = True
            bad = (size <= 3) & ~anchored & ~fixed
            bad[0] = False
            speck = loose & bad[lab]
            if speck.any():
                k2 = keys(out)
                nb = np.stack([np.where(shift(op & ~Oc, dy, dx, False), shift(k2, dy, dx, -1), -1) for dy, dx in N8])
                cnt = np.zeros(nb.shape, np.int32)
                for j in range(len(N8)):
                    cnt += (nb == nb[j][None]) & (nb[j][None] >= 0)
                cnt[nb < 0] = 0
                pick = nb[np.argmax(cnt, 0), np.arange(H)[:, None], np.arange(W)[None, :]]
                speck &= pick >= 0
                spk = np.zeros(lab.max() + 1, bool)
                spk[np.unique(lab[speck])] = True
                whole = spk[lab] & (lab > 0)              # every square of such a speck, from its own neighbours
                for _ in range(3):
                    cur = whole & is_outline(out, oc)
                    if not cur.any():
                        break
                    k2 = keys(out)
                    Oc2 = is_outline(out, oc)
                    nb = np.stack([np.where(shift(op & ~Oc2, dy, dx, False), shift(k2, dy, dx, -1), -1) for dy, dx in N8])
                    cnt = np.zeros(nb.shape, np.int32)
                    for j in range(len(N8)):
                        cnt += (nb == nb[j][None]) & (nb[j][None] >= 0)
                    cnt[nb < 0] = 0
                    pick = nb[np.argmax(cnt, 0), np.arange(H)[:, None], np.arange(W)[None, :]]
                    put = cur & (pick >= 0)
                    out[put, :3] = unkey(pick[put])
                    filled |= put
    st = {"filled": int(filled.sum()), "band": int(X.sum())}
    if masks:
        st.update(X=X, cone=cone, slim=slim, filled_mask=filled)
    return out, st


def thin_fixed(a, oc, P, rounds=12):
    """thin() until nothing changes (one round normally; the rest only proves it)."""
    out, total = a, 0
    for _ in range(rounds):
        nxt, st = thin(out, oc, P)
        if not st["filled"]:
            break
        total += st["filled"]
        out = nxt
    else:
        raise RuntimeError("thin_outline: no fixed point")
    return out, total


# ------------------------------------------------------------------------------------------------------- per hero
def load_state():
    if os.path.isfile(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n" + ",\n".join(f'  "{h}": ' + json.dumps(state[h], separators=(", ", ": "), ensure_ascii=False)
                                     for h in sorted(state)) + "\n}\n")


def params(hero, pack, ppu, size, anims, px, state, keep=None, fresh=False):
    """-> {"outline", "hd": {"band", "deep", "median", "keep"}, "lo": {...}}: the stored ones, else (or `fresh`) measured
    now from the frames as they are."""
    if hero in state and not fresh:
        p = json.loads(json.dumps(state[hero]))
    else:
        der = DERIVED.get(hero, ())
        hd = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "hd_", der)]
        lo = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "lo_", der)]
        oc = outline_colours(hd)
        p = {"outline": oc, "hd": kind_params(hd, oc, keep_for(ppu / size)),
             "lo": kind_params(lo, oc, keep_for(UI_PPU)) if lo else {"band": 0, "deep": 1, "keep": keep_for(UI_PPU)}}
    if keep is not None:
        p["hd"]["keep"] = keep
    return p


def run_hero(row, state, write, keep=None, review=None, fresh=False):
    """Thin one hero's sheet (and strips) -> report dict; with write=False nothing is written."""
    hero, pack, ppu, size = row
    if state.get(hero, {}).get("skip"):
        return {"hero": hero, "skip": state[hero]["skip"], "params": state[hero], "changed": False}
    anims, px = read(hero, pack)
    before = px.copy()
    p = params(hero, pack, ppu, size, anims, px, state, keep, fresh)
    oc = p["outline"]
    der = DERIVED.get(hero, ())
    rep = {"hero": hero, "params": p, "frames": {}, "squares": {}}
    new_frames = {}
    for kind, prefix in (("hd", "hd_"), ("lo", "lo_")):
        n_fr = n_sq = 0
        for x, y, w, h in rects(anims, prefix, der):
            a = px[y:y + h, x:x + w]
            b, n = thin_fixed(a, oc, p[kind]) if oc else (a, 0)
            if (b[..., 3] != a[..., 3]).any():
                raise AssertionError(f"{hero}: the silhouette changed at {(x, y, w, h)}")
            if n:
                n_fr += 1
                n_sq += n
                new_frames[(x, y, w, h)] = b
        rep["frames"][kind], rep["squares"][kind] = n_fr, n_sq
    after = px.copy()
    for (x, y, w, h), b in new_frames.items():
        after[y:y + h, x:x + w] = b
    if (after[..., 3] != before[..., 3]).any():
        raise AssertionError(f"{hero}: the sheet's alpha changed")
    rep["changed"] = bool(new_frames)
    # the strips ppu_hd.py reads: the same change where each frame is its sheet frame as it was
    strips = []
    for tag, a in anims.items():
        if tag.startswith(("hd_", "lo_")) or is_fx(tag) or "hd_" + tag not in anims or tag in der:
            continue
        path = os.path.join(STRIPS, f"{strip_name(hero)}_{tag}.png")
        if not os.path.isfile(path):
            continue
        s = np.array(Image.open(path).convert("RGBA"))
        for src in ("hd_" + tag, "hd_" + tag + "_base"):         # an idle's strip is its breathing loop, idle_base
            s2, x0, same = s.copy(), 0, src in anims
            for f in anims.get(src, {}).get("frames", []):
                d = f["data"]
                x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
                if x0 + w > s.shape[1] or h > s.shape[0] or not (s[:h, x0:x0 + w] == before[y:y + h, x:x + w]).all():
                    same = False
                    break
                s2[:h, x0:x0 + w] = after[y:y + h, x:x + w]
                x0 += w + 1
            if same:
                break
        if not same:
            strips.append((tag, "left (not the sheet's frames)"))
        elif (s2 != s).any():
            strips.append((tag, "thinned"))
            if write:
                Image.fromarray(s2, "RGBA").save(path, optimize=True)
    rep["strips"] = strips
    if write and new_frames:
        Image.fromarray(after, "RGBA").save(stem(hero, pack) + "#sheet.png", optimize=True)
    rep["write_state"] = p if write else None
    if write:
        state[hero] = p
    if review:
        rep["review"] = review_sheet(row, anims, before, after, p, review)
    rep["width"] = widths(anims, before, after, p, ppu, size, der)
    return rep


def widths(anims, before, after, p, ppu, size, derived=()):
    """Median band depth over the hd_ frames' edge squares before / after, in squares and game px."""
    oc = p["outline"]
    out = {}
    if not oc:
        return {"before": (0.0, 0.0), "after": (0.0, 0.0)}
    for name, px in (("before", before), ("after", after)):
        fr = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "hd_", derived)]
        med, _ = measure(fr, oc)
        out[name] = (med, med * size / ppu)
    return out


# ------------------------------------------------------------------------------------------------------- review
def review_sheet(row, anims, before, after, p, out_dir):
    """Before / after at the game's size x4 (idle, run, attack, the BP card's frame) and the idle at 8 x the squares."""
    from PIL import ImageDraw
    hero, pack, ppu, size = row
    bg = np.array([88, 118, 76, 255], np.uint8)

    def frame(px, tag, i=0):
        fr = anims.get(tag, {}).get("frames", [])
        if not fr:
            return None
        d = fr[min(i, len(fr) - 1)]["data"]
        x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
        a = px[y:y + h, x:x + w]
        return np.where(a[..., 3:4] > 0, a, bg)

    def game(a, s):
        return Image.fromarray(a).resize((max(1, round(a.shape[1] * s)), max(1, round(a.shape[0] * s))), Image.NEAREST)

    # the game's size x4: a dense square is size / PPU game px, a lo_ square 1 / UI_PPU
    picks = [("hd_idle", 0, 4 * size / ppu), ("hd_run", 2, 4 * size / ppu), ("hd_attack", 2, 4 * size / ppu),
             ("lo_idle", 0, 4 / UI_PPU)]
    tiles = []
    for tag, i, s in picks:
        a, b = frame(before, tag, i), frame(after, tag, i)
        if a is None:
            continue
        tiles.append((f"{tag}[{i}]", game(a, s), game(b, s)))
    big_a, big_b = frame(before, "hd_idle"), frame(after, "hd_idle")
    z = 8
    zoom_a = Image.fromarray(big_a).resize((big_a.shape[1] * z, big_a.shape[0] * z), Image.NEAREST)
    zoom_b = Image.fromarray(big_b).resize((big_b.shape[1] * z, big_b.shape[0] * z), Image.NEAREST)
    pad = 12
    tw = sum(max(t[1].width, t[2].width) + pad for t in tiles) + pad
    th = max(t[1].height for t in tiles) * 2 + 3 * pad + 14
    W = max(tw, zoom_a.width * 2 + 3 * pad)
    H = th + zoom_a.height + 2 * pad + 14
    sheet = Image.new("RGB", (W, H), (40, 40, 46))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 2), f"{hero}  PPU {ppu:g}  size {size:g}  outline {p['outline'][:1]}  band {p['hd']['band']} -> keep "
                     f"{p['hd']['keep']} (hd), lo_ band {p['lo']['band']} -> {p['lo']['keep']}   top: before, below: after",
           fill=(230, 230, 230))
    x = pad
    rh = max(t[1].height for t in tiles)
    for name, ia, ib in tiles:
        d.text((x, 14), name, fill=(200, 200, 200))
        sheet.paste(ia, (x, 26))
        sheet.paste(ib, (x, 26 + rh + pad))
        x += max(ia.width, ib.width) + pad
    y = th
    d.text((pad, y), "hd_idle[0], 8 x the squares: before | after", fill=(200, 200, 200))
    sheet.paste(zoom_a, (pad, y + 14))
    sheet.paste(zoom_b, (2 * pad + zoom_a.width, y + 14))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{hero}_thin_outline.png")
    sheet.save(path)
    return path


# ------------------------------------------------------------------------------------------------------- audit
def audit_row(row, state):
    hero, pack, ppu, size = row
    anims, px = read(hero, pack)
    hd = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "hd_", DERIVED.get(hero, ()))]
    p = params(hero, pack, ppu, size, anims, px, {k: v for k, v in state.items() if not v.get("skip")})
    oc = p["outline"]
    med, _ = measure(hd, oc)
    T, K = p["hd"]["band"], p["hd"]["keep"]
    filled = band_sq = 0
    for a in hd:
        if not oc:
            break
        b, n = thin_fixed(a, oc, p["hd"])
        filled += n
        op, L, O, Bo = band(a, oc, max(T, 1))
        band_sq += int(Bo.sum())
    return {"hero": hero, "pack": pack, "ppu": ppu, "size": size, "outline": oc[0] if oc else None,
            "outline_n": len(oc), "band_median": med, "band": T, "game_px": round(med * size / ppu, 2),
            "keep": K, "keep_px": round(K * size / ppu, 2), "squares": filled,
            "share": round(filled / max(1, band_sq), 3), "thinned": hero in state and not state[hero].get("skip"),
            "skip": state.get(hero, {}).get("skip")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hero", action="append", default=[], help="hero (fizz, league_fizz, powder ...); repeat or comma")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when a frame would change")
    ap.add_argument("--dry", action="store_true", help="write nothing")
    ap.add_argument("--review", help="before / after pictures into this folder")
    ap.add_argument("--keep", type=int, help="squares of outline to keep for the heroes named (stored)")
    ap.add_argument("--fresh", action="store_true", help="measure the heroes' bands again (their frames drawn anew)")
    ap.add_argument("--audit", action="store_true", help="every dense hero: outline, band, PPU, game px, would change")
    ap.add_argument("--json", help="--audit: also write the rows here")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()
    heroes = all_heroes()
    state = load_state()
    names = [n for h in args.hero for n in h.split(",") if n]
    if args.audit:
        rows = [resolve(n, heroes) for n in names] if names else heroes
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            res = list(ex.map(audit_row, rows, [state] * len(rows)))
        print(f"{'hero':24s} {'PPU':>6s} {'size':>5s} {'outline':>15s} {'band':>5s} {'p85':>4s} {'game px':>7s} "
              f"{'keep':>4s} {'-> px':>5s} {'squares':>8s} {'share':>6s}")
        for r in res:
            print(f"{r['hero']:24s} {r['ppu']:6.3f} {r['size']:5.2f} {str(tuple(r['outline'] or ())):>15s} "
                  f"{r['band_median']:5.1f} {r['band']:4d} {r['game_px']:7.2f} {r['keep']:4d} {r['keep_px']:5.2f} "
                  f"{r['squares']:8d} {r['share']:6.1%}" + ("  (thinned)" if r["thinned"] else ""))
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1)
        return
    if args.check and not names:
        names = sorted(h for h in state if not state[h].get("skip"))
    if not names:
        ap.error("--hero, --check or --audit")
    rows = [resolve(n, heroes) for n in names]
    write = not (args.dry or args.check)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=max(1, min(args.jobs, len(rows)))) as ex:
        reps = list(ex.map(run_hero, rows, [state] * len(rows), [write] * len(rows), [args.keep] * len(rows),
                           [args.review] * len(rows), [args.fresh] * len(rows)))
    bad = []
    for row, rep in zip(rows, reps):
        if rep.get("skip"):
            print(f"{row[0]}: skipped - {rep['skip']}")
            continue
        if args.check:
            if row[0] not in state:
                bad.append(f"{row[0]}: never thinned (not in {os.path.relpath(STATE, ROOT)})")
            elif rep["changed"]:
                bad.append(f"{row[0]}: {rep['squares']} squares would change ({rep['frames']} frames) - run "
                           f"python -I tools/art/thin_outline.py --hero {row[0]} (--fresh if its frames were drawn anew)")
            continue
        if rep.get("write_state") is not None:
            state[row[0]] = rep["write_state"]
        p, wd = rep["params"], rep["width"]
        print(f"{row[0]}: outline {p['outline']}; hd band {p['hd']['band']} -> keep {p['hd']['keep']}, lo_ band "
              f"{p['lo']['band']} -> {p['lo']['keep']}; {rep['frames']['hd']} hd_ / {rep['frames']['lo']} lo_ frames, "
              f"{rep['squares']['hd']} / {rep['squares']['lo']} squares; median band {wd['before'][0]:.1f} -> "
              f"{wd['after'][0]:.1f} squares = {wd['before'][1]:.2f} -> {wd['after'][1]:.2f} game px"
              + (f"; strips: {', '.join(f'{t} {s}' for t, s in rep['strips'])}" if rep["strips"] else "")
              + (f"; review {rep['review']}" if rep.get("review") else "")
              + ("; now run tools/art/hover_aatrox.py" if row[0] == "league_aatrox" and rep["changed"] else ""))
    if args.check:
        if bad:
            print("\n".join(["FAILED:"] + bad))
            sys.exit(1)
        print(f"ok: {len(rows)} heroes, nothing to change")
        return
    if write:
        save_state(state)


if __name__ == "__main__":
    main()
