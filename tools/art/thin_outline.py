#!/usr/bin/env python3
"""Even dark outlines on the dense (PPU) hero frames: KEEP squares of the hero's own outline round its body, as
league_orianna's (the user, 2026-11-14, on a screenshot of Fizz: 「有些英雄黑边太粗了 都检查一下 发条那种就正常」; on
2026-11-15, after the first run: 「菲兹怎么头顶多了一块」「游戏百科里的黑边好像没处理好」「还有劫没有黑边 感觉过度高清了」).

    python -I tools/art/thin_outline.py --hero fizz [--hero zed ...]      # rewrite the heroes' hd_ / lo_ frames (+ strips)
    python -I tools/art/thin_outline.py --check                           # every hero in thin_outline.json: exit 1 when
                                                                          # a frame would still change (CI)
    python -I tools/art/thin_outline.py --hero fizz --dry --review DIR    # before / after pictures, nothing written
    python -I tools/art/thin_outline.py --hero fizz --fresh               # measure the band again (frames redrawn)
    python -I tools/art/thin_outline.py --audit [--json PATH]             # every dense hero of both packs: band, game px

Why bands differ. A dense frame's outline is the design's own (as Codex drew it, read on the design's squares) plus the
squares tools/art/ppu_restyle.py grew round it (RESTYLE `edge`: 2 for most heroes redone since 2026-11-01, 0 for the
ones before, league_zed's, league_jinx's ...). On the battlefield a frame is drawn at 1 / PPU (hd.rs HEROES; SIZES on
top), so n squares of outline are n x SIZES / PPU game pixels: league_orianna 2 squares at 2.25 = 0.89 (「正常」),
league_fizz 4 at 1.8125 = 2.2, league_zed 1 at 1.625 = 0.62.

The body never changes - not a square, not its shape: every square not of the hero's outline colour(s), and the dark
parts of the design in outline colour (see below). Only the outline round it does, so the frame shows the body the
design drew with an even outline (the first run, 5095e7de8, painted the band's inner squares with the body's colour:
the body grew into its old outline - Fizz's head two squares taller, 「头顶多了一块」).

- Outline colours: the commonest colour of the frames' outermost layer, with the near-identical near-blacks of the outer
  six layers (league_orianna's design outline (9, 3, 15) under the restyle's (8, 2, 16); RGB L1 distance <= 24).
- KEEP: the whole number of squares nearest TARGET (1 game px) by ratio, sqrt(n(n-1)) <= PPU / SIZES < sqrt(n(n+1)):
  1 below 1.414, 2 up to 2.449 (league_orianna's 2 at 2.25), 3 up to 3.46; the lo_ frames (UI_PPU 1.5) keep 2.
- The band (Manhattan layers from the clear squares; outline colour at depth 1, then at each next depth where it
  touches the band one layer out and has two band squares beside it or goes no deeper) measured once over the hero's
  frames before the first run - the median and the 85th percentile of its edge squares' depth - and kept in
  thin_outline.json (after the run the frames no longer show it).
- Median over KEEP (`thin`): every outline square farther than KEEP from the body (steps through the figure) is cleared,
  from the outside in - the ring outside KEEP goes, the KEEP squares touching the body stay; the silhouette shrinks by
  that ring, the same way in every frame. Bounded: an outline square farther than BAND + 1 from the body is a dark part
  of the design (black hair, a blade, the slit between a trident's tines) and stays with everything within
  BAND + 1 - KEEP of it (so it keeps its shape and its root); the outline between two parts (body on both sides within
  3 squares, across or along a diagonal) stays; only squares reached from the outside through squares to clear go, so
  no hole opens inside the figure.
- Median under KEEP (`grow`): every clear square within KEEP of the body gets the outline colour (the commonest
  outline colour, or the darkest colour of the outermost layer when that layer is not dark), but not a clear gap
  between two parts (body on both sides within KEEP + 1): the gap stays open. A frame's rect is not grown, so where
  the drawing touches it (a hair tip on the top row) the new outline stops there (0.1-3 % of the squares).
- Median KEEP: left alone.
- One pass is a fixed point (the body and the kept squares decide; a second pass finds nothing); --check wants a pass to
  change nothing.

thin_outline.json: {hero id: {"outline": [[r, g, b], ...], "grow": [r, g, b], "hd": {"band", "deep", "median", "keep"},
"lo": {...}}}, written by the first run of a hero; a later run uses it (--keep N changes the hd_ "keep" of the heroes
named). A hero whose entry is {"skip": why} is never touched. Run over the heroes after a pipeline run that writes their
dense frames again (tools/art/ppu_restyle.py, ppu_hd.py): CI's --check fails until it is (--fresh if they were redrawn).

Frames another tool makes from a hero's own frames (DERIVED) are not changed here: that tool makes them again from the
changed frames - league_aatrox's hover tags, tools/art/hover_aatrox.py (run it after this; its --check is in CI). So
do league_kogmaw's void form (tools/art/unit_kogmaw_void.py) and league_illaoi's spirits (tools/art/illaoi_souls.py):
their own sheets, made from these.

The strips tools/art/ppu_hd.py reads (assets/source/ppu/<hero>_<tag>.png) get the same change where every frame of the
strip is its sheet's hd_ frame square for square, so `ppu_hd.py --hero <hero>` writes the changed frames again. Their
own source (assets/source/ppu/orig/, tools/art/ppu_restyle.py) is not touched: a restyle run writes the old outline,
and this tool has to run after it.
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


def keys(a):
    return (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2].astype(np.int64)


def unkey(k):
    return np.stack([(k >> 16) & 255, (k >> 8) & 255, k & 255], -1).astype(np.uint8)


def luma(k):
    c = unkey(k).astype(float)
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]




# ------------------------------------------------------------------------------------------------------- the band
def outline_colours(frames):
    """The hero's outline colours from its dense frames: the commonest colour of the outermost layer first, then its
    near-identical near-blacks found in the outer six layers ([] when the outermost layer's commonest is not dark)."""
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
    if base.max() > 64:                     # the edge is a body colour: no outline
        return []
    out = [c0]
    for k in sorted(outer, key=lambda k: (-outer[k], k)):
        c = unkey(np.array(k)).astype(int)
        if k != c0 and np.abs(c - base).sum() <= NEAR and c.max() <= 64:
            out.append(k)
    return [unkey(np.array(k)).tolist() for k in out]


def darkest_edge(frames):
    """The commonest of the outermost layer's colours within 10 luma of its darkest - an outline to grow where the
    outermost layer is not dark."""
    cnt = {}
    for a in frames:
        op = a[..., 3] > 0
        if not op.any():
            continue
        v, n = np.unique(keys(a)[depth(op, 1) == 1], return_counts=True)
        for k, c in zip(v.tolist(), n.tolist()):
            cnt[k] = cnt.get(k, 0) + c
    if not cnt:
        return [0, 0, 0]
    ks = np.array(sorted(cnt))
    lum = luma(ks)
    dark = [int(k) for k, l in zip(ks, lum) if l <= lum.min() + 10]
    return unkey(np.array(max(dark, key=lambda k: (cnt[k], -k)))).tolist()


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


def mode(P):
    """"thin" (the usual band over KEEP), "grow" (under it) or None."""
    return "thin" if P["median"] > P["keep"] else "grow" if P["median"] < P["keep"] else None


# ------------------------------------------------------------------------------------------------------- the change
def steps_from(src, through, cap):
    """Steps (4-neighbour, inside `through`) from the nearest square of `src`; cap + 1 where farther."""
    d = np.full(src.shape, cap + 1, np.int32)
    d[src] = 0
    front = src.copy()
    for step in range(1, cap + 1):
        new = dil4(front) & through & (d > cap)
        if not new.any():
            break
        d[new] = step
        front = new
    return d


def between(body, s):
    """Squares with body on both opposite sides within s squares (across, up and down, or along a diagonal)."""
    out = np.zeros(body.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        pos = np.zeros(body.shape, bool)
        neg = np.zeros(body.shape, bool)
        for k in range(1, s + 1):
            pos |= shift(body, k * dy, k * dx, False)
            neg |= shift(body, -k * dy, -k * dx, False)
        out |= pos & neg
    return out


def thin_ring(a, oc, K, D):
    """The outline ring farther than K from the body cleared from the outside in (see the module's notes) -> (frame,
    the squares cleared)."""
    op = a[..., 3] > 0
    O = is_outline(a, oc)
    body = op & ~O
    if not body.any() or not O.any():
        return a, np.zeros(op.shape, bool)
    d = steps_from(body, op, D + 1)
    keep = O & (d > D)                                  # a dark part of the design, and its root
    for _ in range(max(0, D - K)):
        keep = dil4(keep)
    keep |= between(body, min(D - K + 1, 3))            # the outline between two parts
    go = O & (d > K) & (d <= D) & ~keep
    gone = np.zeros(op.shape, bool)
    out_ = ~op
    while True:
        reach = np.zeros(op.shape, bool)
        for dy, dx in N4:
            reach |= shift(out_ | gone, dy, dx, True)    # the frame's border is outside
        new = go & ~gone & reach
        if not new.any():
            break
        gone |= new
    out = a.copy()
    out[gone] = 0
    return out, gone


def grow_ring(a, oc, K, colour):
    """Clear squares within K of the body painted `colour`, a gap between two parts left open -> (frame, squares)."""
    op = a[..., 3] > 0
    O = is_outline(a, oc) if oc else np.zeros(op.shape, bool)
    body = op & ~O
    if not body.any():
        return a, np.zeros(op.shape, bool)
    d = steps_from(body, np.ones(op.shape, bool), K)
    new = ~op & (d <= K) & ~between(body, K + 1)
    out = a.copy()
    out[new, :3] = colour
    out[new, 3] = 255
    return out, new


def change(a, P, oc, colour):
    """One frame -> (new frame, squares changed)."""
    m = mode(P)
    if m is None or not (a[..., 3] > 0).any():
        return a, 0
    if m == "thin":
        if not oc:
            return a, 0
        b, sq = thin_ring(a, oc, P["keep"], P["deep"])
    else:
        b, sq = grow_ring(a, oc, P["keep"], colour)
    return b, int(sq.sum())


def change_fixed(a, P, oc, colour, rounds=6):
    """change() until nothing changes (one round; the rest only proves it)."""
    out, total = a, 0
    for _ in range(rounds):
        nxt, n = change(out, P, oc, colour)
        if not n:
            return out, total
        total += n
        out = nxt
    raise RuntimeError("thin_outline: no fixed point")


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
    """-> {"outline", "grow", "hd": {"band", "deep", "median", "keep"}, "lo": {...}}: the stored ones, else (or `fresh`)
    measured now from the frames as they are."""
    if hero in state and not fresh and not state[hero].get("skip"):
        p = json.loads(json.dumps(state[hero]))
    else:
        der = DERIVED.get(hero, ())
        hd = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "hd_", der)]
        lo = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "lo_", der)]
        oc = outline_colours(hd)
        p = {"outline": oc, "grow": oc[0] if oc else darkest_edge(hd), "hd": kind_params(hd, oc, keep_for(ppu / size)),
             "lo": kind_params(lo, oc, keep_for(UI_PPU)) if lo else
             {"band": 0, "deep": 1, "median": float(keep_for(UI_PPU)), "keep": keep_for(UI_PPU)}}
    if keep is not None:
        p["hd"]["keep"] = keep
    return p


def run_hero(row, state, write, keep=None, review=None, fresh=False):
    """One hero's sheet (and strips) changed -> report dict; with write=False nothing is written."""
    hero, pack, ppu, size = row
    if state.get(hero, {}).get("skip"):
        return {"hero": hero, "skip": state[hero]["skip"], "params": state[hero], "changed": False}
    anims, px = read(hero, pack)
    before = px.copy()
    p = params(hero, pack, ppu, size, anims, px, state, keep, fresh)
    oc = p["outline"]
    der = DERIVED.get(hero, ())
    rep = {"hero": hero, "params": p, "frames": {}, "squares": {}, "mode": {k: mode(p[k]) for k in ("hd", "lo")}}
    new_frames = {}
    for kind, prefix in (("hd", "hd_"), ("lo", "lo_")):
        n_fr = n_sq = 0
        for x, y, w, h in rects(anims, prefix, der):
            a = px[y:y + h, x:x + w]
            b, n = change_fixed(a, p[kind], oc, p["grow"])
            body = (a[..., 3] > 0) & ~is_outline(a, oc)
            if (b[body] != a[body]).any():
                raise AssertionError(f"{hero}: the body changed at {(x, y, w, h)}")
            moved = (b != a).any(-1)
            if (moved & ~((a[..., 3] == 0) | is_outline(a, oc))).any():
                raise AssertionError(f"{hero}: a square neither clear nor outline changed at {(x, y, w, h)}")
            if n:
                n_fr += 1
                n_sq += n
                new_frames[(x, y, w, h)] = b
        rep["frames"][kind], rep["squares"][kind] = n_fr, n_sq
    after = px.copy()
    for (x, y, w, h), b in new_frames.items():
        after[y:y + h, x:x + w] = b
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
            strips.append((tag, "changed"))
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
    der = DERIVED.get(hero, ())
    hd = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "hd_", der)]
    lo = [px[y:y + h, x:x + w] for x, y, w, h in rects(anims, "lo_", der)]
    skip = state.get(hero, {}).get("skip")
    p = params(hero, pack, ppu, size, anims, px, {k: v for k, v in state.items() if not v.get("skip")})
    oc = p["outline"]
    med = measure(hd, oc)[0] if oc else 0.0
    sq = {"hd": 0, "lo": 0}
    if not skip:
        for kind, fr in (("hd", hd), ("lo", lo)):
            for a in fr:
                sq[kind] += change_fixed(a, p[kind], oc, p["grow"])[1]
    return {"hero": hero, "pack": pack, "ppu": ppu, "size": size, "outline": oc[0] if oc else None,
            "outline_n": len(oc), "band_median": med, "band": p["hd"]["band"], "game_px": round(med * size / ppu, 2),
            "keep": p["hd"]["keep"], "keep_px": round(p["hd"]["keep"] * size / ppu, 2), "mode": mode(p["hd"]),
            "lo_median": p["lo"].get("median"), "lo_mode": mode(p["lo"]), "squares": sq["hd"], "squares_lo": sq["lo"],
            "done": hero in state and not skip, "skip": skip}


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
              f"{'keep':>4s} {'-> px':>5s} {'mode':>5s} {'squares':>8s} {'lo_':>5s}")
        for r in res:
            print(f"{r['hero']:24s} {r['ppu']:6.3f} {r['size']:5.2f} {str(tuple(r['outline'] or ())):>15s} "
                  f"{r['band_median']:5.1f} {r['band']:4d} {r['game_px']:7.2f} {r['keep']:4d} {r['keep_px']:5.2f} "
                  f"{str(r['mode']):>5s} {r['squares']:8d} {str(r['lo_mode']):>5s}"
                  + (f"  (skip: {r['skip'][:40]})" if r["skip"] else "  (done)" if r["done"] else ""))
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
        print(f"{row[0]}: outline {p['outline']}; hd {rep['mode']['hd'] or '-'} (median {p['hd']['median']} keep "
              f"{p['hd']['keep']}), lo_ {rep['mode']['lo'] or '-'} (median {p['lo'].get('median')} keep {p['lo']['keep']}); "
              f"{rep['frames']['hd']} hd_ / {rep['frames']['lo']} lo_ frames, "
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
