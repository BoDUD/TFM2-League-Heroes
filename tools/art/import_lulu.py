#!/usr/bin/env python3
"""Import Lulu's effects (assets/source/lulu/PROMPTS_FX.md, 21 sheets) as the game sheets league_lulu_fx and
league_lulu_big.

    python tools/art/import_lulu.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_lulu.py                                   # native strips -> the effect sheets

The body comes from import_native.py (work/lul's strip fixes built the strips). --raw turns each frame of Codex's
image-model drafts (every frame's cell in manifest.json, `assets[].frames[].rect` = [x, y, w, h]: Codex cut between
the frames at transparent columns, so the cells are not all equal) into a cell of a native strip
(assets/source/lulu/lulu_fx_<name>.png, 8x, plus lulu_fx_anchors.json) the way import_jhin.py does: each game pixel the
majority colour of the source pixels it covers, opaque when a quarter of them are solid (alpha 100 and up), every
colour snapped to the ramps the pack gave that effect (PINK glitter, VIOLET light, GOLD glints, GREEN growth and the
critter's FUR with its plum outline), then the ring comes off the glows (an edge pixel in a ramp's darkest shade goes
when two lighter neighbours hold the shape, else it takes the next shade) - not off the critter's fur. One scale per
strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m), the pack's sizes. The six bolts
that are a light with a tail are made exactly symmetric about their core's row (the game turns them with their flight);
the spinning Whimsy ball is not.
The polymorph's critter (the frames with its plum outline) is a figure, not a glow: at the smoke's scale it came out
12 px wide, its outline broken into specks and its face a few dark dots. It is sampled apart, `critter` game px wide
(one scale per strip, over the outline boxes' median width, so the puff's last frame and the loop show it at one size),
standing where it stood in the smoke, and a game pixel is outline once an eighth of its source pixels are outline
(a majority vote drops a 4 px line under 13 px blocks), on the quarter-pixel shift of the grid that keeps its eyes;
the smaller critter under it is painted over with the smoke round it.
Anchors (source pixels): the bolts on their white core (its front half), frame by frame; everything drawn in place
on one spot per strip (`grid`: the median of the frames' own anchors, each measured from its frame's equal share of
the sheet - per frame, the polymorph's loop slid 6 px from frame to frame with its smoke's lowest row): the hits on
their flash or box, the rings on the ground on the ring's widest row, the pictures standing on a figure (the
polymorph, the growth's pillar, the knock-up) on the middle of their lowest row, Pix's shield ring on its widest row.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles 11 under
the pivot) and times it by the kit (work/lul/build_lulu.py, 60 ticks a second): the bolts stay unseen for their first
ticks (they leave her pivot; see FX) and loop over their longest flight; the polymorph's puff (pre) and its end
(remove) frame its loop; the growth's ring grows, loops for the 7 s and fades (the kit plays R's pictures 7 ticks
after the cast, with the ult's frame 3). Writes league/effects/league_lulu_fx and league_lulu_big (R's pillar and
ring).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import import_twistedfate as TF  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lulu")
MOD = os.path.join(ROOT, "league")
Z = 8

# the pack's ramps, darkest first (work/lul/fx_pack_lu.py)
RAMPS = {
    "PINK": ["7A1890", "B020B8", "E040D0", "FF70E0", "FFB0F0", "FFE6FA", "FFFFFF"],
    "VIOLET": ["3A1C90", "5A30C8", "7A50F0", "9A80FF", "C0B0FF", "E8E0FF", "FFFFFF"],
    "GOLD": ["FF9E21", "FFC63A", "FFE47A", "FFF8D6", "FFFFFF"],
    "GREEN": ["2A7A22", "4AAE2C", "7CD83A", "B4F04E", "DCFF8A", "F4FFD6", "FFFFFF"],
    "FUR": ["2A1430", "5A2E66", "8A4A8A", "C068A8", "E890C0", "F8C0DC", "FFE6F2", "FFFFFF"],
}
# a glow's darkest shade at its edge -> the next shade (the critter's plum outline stays)
RIM = {"7A1890": "B020B8", "3A1C90": "5A30C8", "FF9E21": "FFC63A", "2A7A22": "4AAE2C"}

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps, mirror (bolts)
RAW = {
    "a_bolt": dict(n=3, size=10, measure="w", anchor="head", ramps="PINK VIOLET GOLD", mirror=True),
    "p_bolt": dict(n=3, size=6, measure="w", anchor="head", ramps="PINK VIOLET", mirror=True),
    "a_hit": dict(n=4, size=12, measure="m", anchor=("grid", "core"), ramps="PINK VIOLET GOLD"),
    "p_hit": dict(n=3, size=8, measure="m", anchor=("grid", "box"), ramps="PINK VIOLET"),
    "q_lance": dict(n=4, size=20, measure="w", anchor="head", ramps="PINK VIOLET GOLD", mirror=True),
    "q_pix": dict(n=4, size=16, measure="w", anchor="head", ramps="PINK VIOLET", mirror=True),
    "q_hit": dict(n=5, size=16, measure="m", anchor=("grid", "box"), ramps="PINK VIOLET GOLD"),
    "q_slow2": dict(n=4, size=18, measure="w", anchor=("grid", "ellipse"), ramps="PINK VIOLET"),
    "w_bolt": dict(n=4, size=12, measure="w", anchor="head", ramps="PINK VIOLET GOLD"),
    "w_poly_in": dict(n=4, size=36, measure="h", anchor=("grid", "low"), ramps="PINK VIOLET FUR", critter=18),
    "w_poly": dict(n=6, size=32, measure="h", anchor=("grid", "low"), ramps="PINK VIOLET FUR", critter=18),
    "w_poly_out": dict(n=4, size=36, measure="h", anchor=("grid", "low"), ramps="PINK VIOLET FUR"),
    "e_pix": dict(n=4, size=12, measure="w", anchor="head", ramps="VIOLET PINK", mirror=True),
    "e_land": dict(n=5, size=26, measure="h", anchor=("grid", "ellipse"), ramps="VIOLET PINK GOLD"),
    "e_on": dict(n=6, size=44, measure="h", anchor=("grid", "ellipse"), ramps="VIOLET PINK GOLD"),
    "w_haste": dict(n=4, size=20, measure="w", anchor=("grid", "ellipse"), ramps="GOLD PINK"),
    "r_burst": dict(n=7, size=52, measure="h", anchor=("grid", "low"), ramps="GREEN GOLD PINK"),
    "r_hit": dict(n=5, size=26, measure="h", anchor=("grid", "low"), ramps="GREEN GOLD PINK"),
    "r_on_in": dict(n=4, size=48, measure="w", anchor=("grid", "ellipse"), ramps="GREEN GOLD PINK"),
    "r_on": dict(n=6, size=48, measure="w", anchor=("grid", "ellipse"), ramps="GREEN GOLD PINK"),
    "r_on_out": dict(n=4, size=48, measure="w", anchor=("grid", "ellipse"), ramps="GREEN GOLD PINK"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def unrim(a):
    J.RIM = RIM
    return J.unrim(a)


OUTLINE = "2A1430"
FUR = set(RAMPS["FUR"]) - {"FFFFFF"}


def critter_of(solid, outline):
    """The critter in one frame (source arrays cut to its rect): (mask, box x0, x1, y0, y1) - its outline and all it
    closes in (the outside flooded from round the outline's box) - or None when the frame has no critter. Its snapped
    outline has gaps the flood runs through (one frame's whole body came out empty), so the outline is thickened 2, 3,
    ... px until the inside holds 65% of the box (the critter fills ~75% of it)."""
    if outline.sum() < 1000:
        return None
    ys, xs = np.nonzero(outline)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    P = 8
    for grow in range(2, P):
        wall = np.pad(outline[y0:y1, x0:x1], P)
        for _ in range(grow):
            wall[1:] |= wall[:-1].copy()
            wall[:-1] |= wall[1:].copy()
            wall[:, 1:] |= wall[:, :-1].copy()
            wall[:, :-1] |= wall[:, 1:].copy()
        reach = np.zeros_like(wall)
        reach[0], reach[-1], reach[:, 0], reach[:, -1] = True, True, True, True
        while True:
            grown = reach.copy()
            grown[1:] |= reach[:-1]
            grown[:-1] |= reach[1:]
            grown[:, 1:] |= reach[:, :-1]
            grown[:, :-1] |= reach[:, 1:]
            grown &= ~wall
            if (grown == reach).all():
                break
            reach = grown
        inside = ~reach[P:-P, P:-P]
        if inside.mean() >= 0.65:
            break
    m = np.zeros_like(outline)
    m[y0:y1, x0:x1] = inside
    return m & solid, (x0, x1, y0, y1)


def legible(cell, hit):
    """How well a sampled critter reads: its irises (the violet in the upper two thirds: the eyes, up to four pixels)
    against the outline pixels left alone (a broken line)."""
    hx = J.hexes(cell)
    o = hit & (hx == OUTLINE)
    near = sum(J.shifted(o, dy, dx).astype(int) for dy, dx in J.N8)
    alone = int((o & (near <= 1)).sum())
    ys = np.nonzero(hit.any(1))[0]
    upper = np.zeros_like(hit)
    upper[ys.min():ys.min() + (ys.max() - ys.min()) * 2 // 3] = True
    iris = int((hit & upper & np.isin(hx, RAMPS["VIOLET"][:5])).sum())
    return min(iris, 4) * 10 - alone


def paste_critter(cell, idx, crit, outline, pal, box, at, s_c):
    """The critter sampled at s_c with its bottom middle on `at` (cell px, x y): a pixel is outline when an eighth of
    its source pixels are, else the majority of the critter's other colours; it needs a quarter covered."""
    x0, x1, y0, y1 = box
    bx, by = (x0 + x1) / 2, y1
    th, tw = cell.shape[:2]
    H, W = crit.shape
    hit = np.zeros((th, tw), bool)
    for r in range(th):
        sy = by + (r + 0.5 - at[1]) / s_c
        r0, r1 = int(math.floor(sy - 0.5 / s_c)), int(math.floor(sy + 0.5 / s_c))
        r0, r1 = max(0, r0), min(H, max(r1, r0 + 1))
        if r1 <= r0:
            continue
        for c in range(tw):
            sx = bx + (c + 0.5 - at[0]) / s_c
            c0, c1 = int(math.floor(sx - 0.5 / s_c)), int(math.floor(sx + 0.5 / s_c))
            c0, c1 = max(0, c0), min(W, max(c1, c0 + 1))
            if c1 <= c0:
                continue
            m = crit[r0:r1, c0:c1]
            if m.mean() < 1 / 4:
                continue
            o = m & outline[r0:r1, c0:c1]
            if o.mean() >= 1 / 8:
                k = idx[r0:r1, c0:c1][o][0]
            else:
                k = np.bincount(idx[r0:r1, c0:c1][m & ~o], minlength=len(pal)).argmax()
            cell[r, c, :3] = pal[k]
            cell[r, c, 3] = 255
            hit[r, c] = True
    return hit


def smoke_over(cell, keep, hexes_):
    """Fur and outline pixels outside `keep` (the smaller critter's remains) take the colour most of their non-fur
    neighbours have; with none, they go."""
    hx = J.hexes(cell)
    left = (cell[..., 3] > 0) & ~keep & np.isin(hx, list(FUR))
    for r, c in zip(*np.nonzero(left)):
        near = [tuple(cell[v, u, :3]) for v in range(r - 1, r + 2) for u in range(c - 1, c + 2)
                if 0 <= v < cell.shape[0] and 0 <= u < cell.shape[1] and (v, u) != (r, c) and cell[v, u, 3]
                and not left[v, u] and not keep[v, u]]
        if near:
            cell[r, c, :3] = max(set(near), key=near.count)
        else:
            cell[r, c] = 0
    return int(left.sum())


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"lulu_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = J.snap(a, solid, pal)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        if spec["anchor"][0] == "grid":
            # drawn in place: one spot for the whole strip - the median of the frames' own anchors (their sparks
            # and Codex's cuts drift) from each frame's equal share of the sheet
            n, cw = len(rects), a.shape[1] / len(rects)
            own = [TF.anchor(spec["anchor"][1], k, a, solid, rects, s) for k in range(n)]
            mx = float(np.median([ox - k * cw for k, (ox, _) in enumerate(own)]))
            my = float(np.median([oy for _, oy in own]))
            anc = [(k * cw + mx, my) for k in range(n)]
        else:
            anc = [TF.anchor(spec["anchor"], k, a, solid, rects, s) for k in range(len(rects))]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        crits, s_c, o_i = [None] * len(rects), 0, None
        if spec.get("critter"):
            o_i = hexes_.index(OUTLINE)
            crits = [critter_of(solid[y:y + h, x:x + w], idx[y:y + h, x:x + w] == o_i) for x, y, w, h in rects]
            s_c = spec["critter"] / float(np.median([c[1][1] - c[1][0] for c in crits if c]))
            for (x, y, _, _), (ax, ay), cr in zip(rects, anc, crits):
                if cr:                                   # the bigger critter widens the cell
                    x0, x1, y0, y1 = cr[1]
                    fx, fy = (x + (x0 + x1) / 2 - ax) * s, (y + y1 - ay) * s
                    L = max(L, math.ceil(abs(fx) + (x1 - x0) / 2 * s_c) + 1)
                    U = max(U, math.ceil(max(abs(fy), abs(fy - (y1 - y0) * s_c))) + 1)
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        for i, (x, y, w, h) in enumerate(rects):
            ax, ay = anc[i]
            cell = np.zeros((th, tw, 4), np.uint8)
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(y, sy0), min(y + h, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(x, sx0), min(x + w, sx1)
                    if sx1 <= sx0:
                        continue
                    m = solid[sy0:sy1, sx0:sx1]
                    if m.mean() < 1 / 4:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            cell = unrim(cell)
            if crits[i]:
                # at 1.75 source "pixels" a game pixel, where the grid falls decides whether the eyes survive: of
                # 16 quarter-pixel shifts the one that reads best (legible)
                cm, cbox = crits[i]
                x0, x1, y0, y1 = cbox
                sub = idx[y:y + h, x:x + w]
                best = None
                for q in range(16):
                    at = (L + 0.5 + (x + (x0 + x1) / 2 - ax) * s + q % 4 / 4,
                          U + 0.5 + (y + y1 - ay) * s + q // 4 / 4)
                    trial = cell.copy()
                    keep = paste_critter(trial, sub, cm, (sub == o_i) & cm, pal, cbox, at, s_c)
                    score = legible(trial, keep)
                    if best is None or score > best[0]:
                        best = (score, trial, keep, at)
                score, cell, keep, at = best
                print(f"  {name} {i}: critter {keep.sum()} px at {at[0]:.2f},{at[1]:.2f} (reads {score}), "
                      f"{smoke_over(cell, keep, hexes_)} smaller-critter px smoked over")
            if spec.get("mirror"):
                cell = J.mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "lulu_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"lulu_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"lulu_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down)
HIT = (0, -10)              # a hit on the upper body of a 36-44 px champion
CHEST = (0, -6)             # the shield's flash on the chest
MID = (0, -11)              # the middle of a 44 px figure (the shield ring stands round it)
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # a picture standing on a unit's feet
seq = J.seq
EMPTY = J.EMPTY


def flight(n, ms, total, lead):
    return J.flight(n, ms, total, lead=lead)


R_LOOP = 420 * 1000 // 60                  # the growth: r_t ticks (7 s)
POLY_LOOP = 105 * 1000 // 60               # the polymorph: w_t ticks (1.75 s)
FX = {
    # the bolts leave her pivot at 5 px a tick, lifted to the staff held level in the release frames (5-9 px up,
    # build_lulu's y_offsets); her staff reaches 38 px ahead and her attack 55, so a bolt hidden until the hook would
    # show for two ticks: they appear past her front (10-16 px) and run along the staff out of its hook. Pix's three
    # bolts and his lance a tick later (they leave from over her head)
    "a_bolt": [("a_bolt", flight(3, 60, 400, lead=2), [(0, 0)])],
    "p_bolt": [("p_bolt", flight(3, 60, 400, lead=3), [(0, 0)])],
    "q_lance": [("q_lance", flight(4, 60, 900, lead=3), [(0, 0)])],
    "q_pix": [("q_pix", flight(4, 60, 900, lead=3), [(0, 0)])],
    "w_bolt": [("w_bolt", flight(4, 60, 500, lead=2), [(0, 0)])],
    "e_pix": [("e_pix", flight(4, 60, 800, lead=2), [(0, 0)])],
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "p_hit": [("p_hit", seq(range(3), [40, 50, 60]), [HIT])],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "e_land": [("e_land", seq(range(5), [50, 60, 70, 80, 90]), [CHEST])],
    "r_hit": [("r_hit", seq(range(5), [50, 60, 80, 100, 120]), [SOLES])],
    # buffs: they loop while they last
    "q_slow2": [("q_slow2", seq(range(4), [100] * 4), [FEET])],
    "w_haste": [("w_haste", seq(range(4), [100] * 4), [FEET])],
    "e_on": [("e_on", seq(range(6), [100] * 6), [MID])],
    "w_poly_in": [("w_poly_in", seq(range(4), [50, 50, 60, 60]), [SOLES])],
    "w_poly": [("w_poly", seq(range(6), [100] * 6), [SOLES])],
    "w_poly_out": [("w_poly_out", seq(range(4), [60, 60, 70, 80]), [SOLES])],
}
BIG = {
    "r_burst": [("r_burst", seq(range(7), [50, 60, 70, 80, 90, 100, 110]), [SOLES])],
    "r_on_in": [("r_on_in", seq(range(4), [60, 60, 70, 80]), [FEET])],
    "r_on": [("r_on", seq(range(6), [120] * 6), [FEET])],
    "r_on_out": [("r_on_out", seq(range(4), [80, 80, 90, 100]), [FEET])],
}


def build(table):
    with open(G.lp(os.path.join(SRC, "lulu_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                out[tag].append((J.place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sheet, table in (("league_lulu_fx", FX), ("league_lulu_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
