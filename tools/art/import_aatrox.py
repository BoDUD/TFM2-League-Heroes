#!/usr/bin/env python3
"""Import Aatrox's effects (assets/source/aatrox/PROMPTS_FX.md, 24 sheets; w_ring and w_snap redrawn 66 wide for the
33000 ring) as the game sheets league_aatrox_fx and league_aatrox_big.

    python tools/art/import_aatrox.py --raw <Codex's delivery> --ring <the ring redraw>   # once: raw -> native strips
    python tools/art/import_aatrox.py                                                   # native strips -> sheets

--raw turns each frame of Codex's image-model drafts (every frame's cell in manifest.json, `assets[].frames[].rect` =
[x, y, w, h]) into a cell of a native strip (assets/source/aatrox/aatrox_fx_<name>.png, 8x, plus
aatrox_fx_anchors.json) the way import_jhin.py does: each game pixel the majority colour of the source pixels it covers,
opaque when a quarter of them are solid (alpha 100 and up), every colour snapped to the ramps the pack gave that effect
(FIRE with one more blood red, B8102A - the drafts' main red, darker than E0202E -, SHADE, IRON, DUST for Q1's
rubble), then the ring comes off the glows (an edge pixel in a ramp's darkest shade goes when two lighter neighbours
hold the shape, else it takes the next shade) - not off the iron, whose outline is drawn.
The drafts often draw past their cells (the slashes and bursts touch their neighbours), so a frame is made of whole
connected pieces: every piece goes to the cell that holds most of it, and one spread over cells (w_link's chain runs
on through all four) is cut at the cells' borders; p_swing's long streak runs over two cells, so its frames are cut
at the drawing's own gaps (`cuts`).
One scale per strip: `size` game px over the widest (w), tallest (h) or larger side (m) of the frames' main shapes
(their pieces of 1% of the frame and up; sparks do not stretch it), the pack's sizes. The projectiles (the chain, its
links, Q1 and Q2's ground shapes) are made exactly symmetric about their anchor's row (the game turns them with their
flight). The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles
11 under it), measured on the finished strips (tools/art/rig_aatrox.py): the sword's tip in the passive's thrust
(attack_p 4) and Q2's sweep (q2 5) (22, -7), on the ground in Q1 and Q3's slam (skill 5, q3 5) (11, 7), the red claw
in W 4 (18, -12); the line pictures on the line's middle (a LineRangeProjectile is drawn centred on it: Q1 46000 long,
Q2 30000 - the fan's point on the caster, 15 px back); rings round a unit's feet 9 under the pivot (FEET). Timings
(60 ticks a second): the slashes start 4 ticks before the blade lands (build_aatrox.py plays them at hit_t - 4) so
their full arc (frame 3) shows on the hit tick; the passive's streak 3 ticks before its hit; the projectiles start
with an empty tick (a projectile's first move points its picture up; import_lucian.py's RAY_SKIP); the W ring: the
main pack's w_ring appears and turns to 1.5 s; the native add-on (addons/league_aatrox_chain) plays w_ring_in
(appear + one turn, RING_IN 24 ticks) and then w_ring_beat (one turn, RING_BEAT 16 ticks) while the chain holds.
Writes league/effects/league_aatrox_fx and league_aatrox_big (the ground shapes, the ring, the transformation, the
wings).
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aatrox")
MOD = os.path.join(ROOT, "league")
Z = 8

RAMPS = {
    "FIRE": ["8F0E2B", "B8102A", "E0202E", "FF5A2A", "FFB347", "FFF0B8", "FFFFFF"],
    "SHADE": ["1A0A22", "34163F", "5A2E6E", "8E5BA8", "C9A6D8"],
    "IRON": ["1A1624", "39334A", "625B74", "9A93A8", "D9D4DE"],      # the chains, an object with its outline
    "DUST": ["6E4A30", "9A7048", "C49A66", "E8C892"],                # Q1's rubble
}
# a glow's darkest shade at its edge -> the next shade
RIM = {"8F0E2B": "B8102A", "1A0A22": "34163F"}
# the iron's outline and dark holes outnumber its grey links once ~20 source pixels make one: they count less in
# the majority vote, so the chains stay grey (all-dark chains were the first import)
WEIGHT = {"1A1624": 0.35, "39334A": 0.7}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps; mirror (projectiles), src (the ring redraw)
RAW = {
    "a_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="FIRE"),
    # the long streak (frame 3, x 627-1212) runs over two of the manifest's cells: cut at the drawing's gaps instead
    "p_swing": dict(n=5, size=36, measure="w", anchor="left", ramps="FIRE", cuts=[0, 160, 580, 1225, 1630, 1983]),
    "p_hit": dict(n=5, size=22, measure="m", anchor=("fixed", "core", 0), ramps="FIRE SHADE"),
    "q1_slash": dict(n=5, size=44, measure="h", anchor=("fixed", "bottom", 2), ramps="FIRE DUST"),
    "q2_slash": dict(n=5, size=30, measure="h", anchor=("fixed", "right", 2), ramps="FIRE"),
    "q3_slash": dict(n=5, size=44, measure="h", anchor=("fixed", "bottom", 2), ramps="FIRE SHADE"),
    "q1_body": dict(n=4, size=46, measure="w", anchor="cell", ramps="FIRE", mirror=True),
    "q2_body": dict(n=4, size=36, measure="w", anchor=("fixed", "left", 1), ramps="FIRE", mirror=True),
    "q3_body": dict(n=5, size=40, measure="w", anchor=("fixed", "center", 1), ramps="FIRE SHADE"),
    "q_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="FIRE"),
    "q_edge": dict(n=5, size=30, measure="h", anchor=("fixed", "bottom", 1), ramps="FIRE"),
    "e_dash": dict(n=4, size=30, measure="w", anchor=("fixed", "right", 0), ramps="FIRE SHADE"),
    "w_throw": dict(n=4, size=14, measure="w", anchor=("fixed", "left", 1), ramps="FIRE SHADE"),
    "w_chain": dict(n=4, size=24, measure="w", anchor="head", ramps="IRON FIRE", mirror=True),
    "w_link": dict(n=4, size=16, measure="w", anchor="cell", ramps="IRON FIRE", mirror=True),
    "w_hit": dict(n=4, size=16, measure="m", anchor=("fixed", "core", 0), ramps="FIRE IRON"),
    "w_ring": dict(n=6, size=66, measure="w", anchor=("fixed", "center", 2), ramps="FIRE SHADE IRON", src="ring"),
    "w_snap": dict(n=5, size=66, measure="w", anchor=("fixed", "center", 0), ramps="FIRE IRON", src="ring"),
    "w_yank": dict(n=4, size=18, measure="m", anchor=("fixed", "center", 1), ramps="IRON FIRE"),
    "w_slowed": dict(n=4, size=20, measure="w", anchor=("fixed", "center", 0), ramps="IRON FIRE"),
    "r_transform": dict(n=8, size=46, measure="w", anchor=("fixed", "bottom", 3), ramps="FIRE SHADE"),
    "r_aura": dict(n=6, size=46, measure="w", anchor=("fixed", "bottom", 0), ramps="FIRE SHADE"),
    "r_feared": dict(n=4, size=10, measure="m", anchor=("fixed", "center", 0), ramps="SHADE FIRE"),
    "r_renew": dict(n=5, size=30, measure="m", anchor=("fixed", "center", 1), ramps="FIRE"),
}


def palette(names):
    hexes_ = [h for r in names.split() for h in RAMPS[r]]
    return hexes_, np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes_], float)


def hexes(a):
    return np.array([["%02X%02X%02X" % tuple(int(v) for v in p[:3]) for p in row] for row in a])


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = m[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
    return out


def unrim(a):
    a = a.copy()
    op = a[..., 3] > 0
    hx = hexes(a)
    rim = op & np.isin(hx, list(RIM))
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    lit = sum(shifted(op & ~rim, dy, dx).astype(int) for dy, dx in N8)
    target = rim & edge
    gone = target & (lit >= 2)
    a[gone] = 0
    for dark, nxt in RIM.items():
        m = target & ~gone & (hx == dark)
        a[m, :3] = [int(nxt[i:i + 2], 16) for i in (0, 2, 4)]
    return a


def snap(a, solid, pal):
    """Palette index of every solid pixel (-1 elsewhere)."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - pal[None]) ** 2).sum(2).argmin(1)
    return idx


def mirror(cell, U):
    """Exactly symmetric about row U: the upper half copied onto the lower."""
    out = cell.copy()
    for r in range(U):
        if 2 * U - r < cell.shape[0]:
            out[2 * U - r] = cell[r]
    return out


def bright(a):
    return (a[..., 3] >= 100) & (a[..., :3].min(-1) >= 215)


# ----------------------------------------------------------------------------- frames from connected pieces
def label(mask):
    """8-connected pieces of a mask: row runs joined by union-find. Returns (labels, count); 0 = empty."""
    parent = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    runs, prev = [], []
    for y in range(mask.shape[0]):
        d = np.diff(np.concatenate(([0], mask[y].astype(np.int8), [0])))
        cur = []
        j = 0
        for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            rid = len(parent)
            parent.append(rid)
            cur.append((s, e, rid))
            runs.append((y, s, e, rid))
            while j < len(prev) and prev[j][1] < s:     # previous runs ending left of this one (8-connected: e >= s)
                j += 1
            k = j
            while k < len(prev) and prev[k][0] <= e:
                a, b = find(rid), find(prev[k][2])
                if a != b:
                    parent[a] = b
                k += 1
        prev = cur
    labels = np.zeros(mask.shape, np.int32)
    roots = {}
    for y, s, e, rid in runs:
        labels[y, s:e] = roots.setdefault(find(rid), len(roots) + 1)
    return labels, len(roots)


def frame_masks(solid, rects):
    """Each frame's pixels: whole pieces go to the cell holding most of them; a piece with under 80% in one cell is
    cut at the cells' borders."""
    labels, n = label(solid)
    owner = np.zeros(n + 1, int) - 1
    split = np.zeros(n + 1, bool)
    counts = np.zeros((n + 1, len(rects)), int)
    for i, (x, y, w, h) in enumerate(rects):
        sub = labels[y:y + h, x:x + w]
        counts[:, i] = np.bincount(sub.ravel(), minlength=n + 1)[:n + 1]
    total = counts.sum(1)
    for c in range(1, n + 1):
        if total[c] == 0:
            continue
        best = counts[c].argmax()
        if counts[c, best] >= 0.8 * total[c]:
            owner[c] = best
        else:
            split[c] = True
    masks = []
    for i, (x, y, w, h) in enumerate(rects):
        m = (owner[labels] == i) & (labels > 0)
        inside = np.zeros_like(m)
        inside[y:y + h, x:x + w] = True
        m |= split[labels] & inside
        masks.append(m)
    return masks, labels


def main_part(mask, labels):
    """A frame's main shapes: its pieces of 1% of its pixels and up (sparks left out)."""
    ids, cnt = np.unique(labels[mask], return_counts=True)
    keep = ids[cnt >= max(1, 0.01 * mask.sum())]
    m = mask & np.isin(labels, keep)
    return m if m.any() else mask


def main_box(mask, labels):
    """Bounding box (x0, x1, y0, y1) of a frame's main shapes."""
    ys, xs = np.nonzero(main_part(mask, labels))
    return xs.min(), xs.max() + 1, ys.min(), ys.max() + 1


def anchor(how, k, a, masks, rects, labels):
    """(x, y) of frame k's anchor in the source."""
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2, y + h / 2
    if how[0] == "fixed":                  # frame j's anchor, the same spot in every cell
        j = how[2]
        ax, ay = anchor(how[1], j, a, masks, rects, labels)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    m = main_part(masks[k], labels)
    x0, x1, y0, y1 = main_box(m, labels)
    b = bright(a) & m
    if how == "center":
        return (x0 + x1) / 2, (y0 + y1) / 2
    if how == "head":                      # the white core in the drawing's front half
        b[:, :int(x0 + 0.5 * (x1 - x0))] = False
        by, bx = np.nonzero(b)
        if not len(bx):
            return (x0 + x1) / 2, (y0 + y1) / 2
        return (bx.min() + bx.max() + 1) / 2, (by.min() + by.max() + 1) / 2
    if how == "core":                      # the white flash's middle
        by, bx = np.nonzero(b)
        if len(bx) < 20:
            return (x0 + x1) / 2, (y0 + y1) / 2
        return bx.mean() + 0.5, by.mean() + 0.5
    if how in ("left", "right"):           # a streak's end, halfway down its bright rows
        by, bx = np.nonzero(b)
        if len(bx) < 5:
            by, bx = np.nonzero(m)
        return (bx.min() if how == "left" else bx.max() + 1), (by.min() + by.max() + 1) / 2
    if how == "bottom":                    # the ground under a burst / a ring: the middle of its lowest rows
        ys, xs = np.nonzero(m[:, x0:x1])
        low = ys >= y1 - max(2, int(0.04 * (y1 - y0)))
        return x0 + xs[low].mean() + 0.5, y1
    raise ValueError(how)


def from_raw(folders):
    manifests = {}
    for key, folder in folders.items():
        with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
            manifests[key] = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        key = spec.get("src", "raw")
        fn = f"aatrox_fx_{name}.png"
        hexes_, pal = palette(spec["ramps"])
        weight = np.array([WEIGHT.get(h, 1.0) for h in hexes_])
        a = np.asarray(Image.open(G.lp(os.path.join(folders[key], fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifests[key][fn]["frames"]]
        if "cuts" in spec:
            c = spec["cuts"]
            rects = [[c[i], 0, c[i + 1] - c[i], a.shape[0]] for i in range(len(c) - 1)]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        masks, labels = frame_masks(solid, rects)
        idx = snap(a, solid, pal)
        mains = [main_box(m, labels) for m in masks]
        ext = {"w": max(b[1] - b[0] for b in mains), "h": max(b[3] - b[2] for b in mains)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, masks, rects, labels) for k in range(len(rects))]
        boxes = []
        for m in masks:
            ys, xs = np.nonzero(m)
            boxes.append((xs.min(), xs.max() + 1, ys.min(), ys.max() + 1))
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        H, W = solid.shape
        for i, m in enumerate(masks):
            ax, ay = anc[i]
            cell = np.zeros((th, tw, 4), np.uint8)
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / s))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / s)), sy0 + 1)
                sy0, sy1 = max(0, sy0), min(H, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / s))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / s)), sx0 + 1)
                    sx0, sx1 = max(0, sx0), min(W, sx1)
                    if sx1 <= sx0:
                        continue
                    mm = m[sy0:sy1, sx0:sx1]
                    if mm.mean() < 1 / 4:
                        continue
                    picked = idx[sy0:sy1, sx0:sx1][mm]
                    col = np.bincount(picked, weights=weight[picked], minlength=len(pal)).argmax()
                    cell[r, c, :3] = pal[col]
                    cell[r, c, 3] = 255
            cell = unrim(cell)
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "aatrox_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"aatrox_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"aatrox_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


# spots from the pivot (game px, x right, y down), measured on the finished strips (rig_aatrox.py: the tip = the fist
# reached from the near shoulder + 19 along the blade's angle; the claw = the far fist in THROW + 4)
P_TIP = (22, -7)            # the passive's thrust, attack_p 4 (the blade level, ahead)
Q1_TIP = (11, 10)           # the blade on the ground, skill 5 (its tip (11, 7)): the arc's foot on the soles' row
Q2_TIP = (24, -9)           # the sweep's reach, q2 5 (the tip at (22, -7)), the crescent's rim just beyond it
Q3_TIP = (12, 10)           # q3 5, the slam (the tip (11, 7)): the burst's foot on the ground
CLAW = (18, -12)            # the red claw in W 4
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
BODY = (0, -6)              # round the body (the chains wrapping him, the renewal ring)
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # the ground under a unit (its soles' row)
BEHIND = (-2, 6)            # E's trail: its bright head at his back, low
OVER = (0, -16)             # the fear swirl over a minion's head
Q1_LINE = (0, 0)            # the Q1 line's middle (46000 long)
Q2_POINT = (-15, 0)         # the Q2 fan's point on the caster (a 30000 line, centred)
EMPTY = "empty"             # a frame with nothing in it (a projectile's first tick)


def seq(frames, ms):
    return list(zip(frames, ms))


def flight(n, ms, total, lead=1):
    """`lead` empty ticks (a projectile's first move points its picture up), then n frames of ms looped over `total`
    ms, the last held a second (a `repeat: false` view must not run out mid-flight)."""
    k = max(1, math.ceil(total / ms))
    return [(EMPTY, lead * 1000 / 60)] + seq([i % n for i in range(k)], [ms] * (k - 1) + [1000])


def loop(frames, ms, total):
    """`frames` (a list) played round and round at `ms` each to `total` ms."""
    k = max(1, round(total / ms))
    return seq([frames[i % len(frames)] for i in range(k)], [ms] * k)


TICK = 1000 / 60
FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # starts 3 ticks before the passive's hit: the streak at full length (frame 3) on the hit
    "p_swing": [("p_swing", seq(range(5), [2 * TICK, 2 * TICK, 67, 67, 67]), [P_TIP])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    # the slashes start 4 ticks before the blade lands (frames 1-2, the glint and the arc's start), frame 3 on the hit
    "q1_slash": [("q1_slash", seq(range(5), [2 * TICK, 2 * TICK, 83, 83, 100]), [Q1_TIP])],
    "q2_slash": [("q2_slash", seq(range(5), [2 * TICK, 2 * TICK, 83, 83, 100]), [Q2_TIP])],
    "q3_slash": [("q3_slash", seq(range(5), [2 * TICK, 2 * TICK, 100, 120, 140]), [Q3_TIP])],
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_edge": [("q_edge", seq(range(5), [40, 50, 60, 80, 100]), [SOLES])],
    "e_dash": [("e_dash", seq(range(4), [50, 60, 70, 80]), [BEHIND])],
    # the claw's flash inside W's throw frame (4: 5 ticks)
    "w_throw": [("w_throw", seq(range(4), [TICK, 2 * TICK, 2 * TICK, 2 * TICK]), [CLAW])],
    # the chain: 66000 at 5000 a tick = 13 ticks; the links: up to 33000 at 2500 = 13 ticks
    "w_chain": [("w_chain", flight(4, 50, 300), [(0, 0)])],
    "w_link": [("w_link", flight(4, 50, 300), [(0, 0)])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_yank": [("w_yank", seq(range(4), [40, 60, 80, 100]), [BODY])],
    "w_slowed": [("w_slowed", seq(range(4), [100] * 4), [FEET])],
    # 1.5 s of fear (90 ticks): the swirl turns over the head
    "r_feared": [("r_feared", loop([0, 1, 2, 3], 90, 1500), [OVER])],
    "r_renew": [("r_renew", seq(range(5), [50, 70, 90, 110, 130]), [BODY])],
}
# the ring: RING_IN = 24 ticks (400 ms), RING_BEAT = 16 ticks (267 ms) - addons/league_aatrox_chain/src/lib.rs
RING_IN = seq(range(6), [60, 60, 70, 70, 70, 70])
RING_BEAT = seq([2, 3, 4, 5], [67, 67, 67, 66])
BIG = {
    "q1_body": [("q1_body", seq(range(4), [40, 60, 80, 100]), [Q1_LINE])],
    "q2_body": [("q2_body", seq(range(4), [40, 60, 80, 100]), [Q2_POINT])],
    "q3_body": [("q3_body", seq(range(5), [40, 60, 80, 120, 160]), [FEET])],
    # the main pack's ring: appears, turns to 1.5 s
    "w_ring": [("w_ring", seq([0, 1], [60, 60]) + loop([2, 3, 4, 5], 80, 1280) + seq([5], [100]), [FEET])],
    "w_ring_in": [("w_ring", RING_IN, [FEET])],
    "w_ring_beat": [("w_ring", RING_BEAT, [FEET])],
    "w_snap": [("w_snap", seq(range(5), [50, 60, 70, 80, 100]), [FEET])],
    # with the ult's 40 ticks (667 ms)
    "r_transform": [("r_transform", seq(range(8), [40, 60, 70, 80, 90, 100, 110, 120]), [SOLES])],
    "r_aura": [("r_aura", seq(range(6), [100] * 6), [SOLES])],
}


def place(cell, anchor_px, spots):
    """The cell with its anchor on every spot (from the pivot), as one frame centred on the pivot."""
    ax, ay = anchor_px
    h, w = cell.shape[:2]
    xs = [int(round(sx - ax)) for sx, _ in spots]
    ys = [int(round(sy - ay)) for _, sy in spots]
    u0, r0 = min(xs), min(ys)
    canvas = np.zeros((max(ys) - r0 + h, max(xs) - u0 + w, 4), np.uint8)
    for x, y in zip(xs, ys):
        sub = canvas[y - r0:y - r0 + h, x - u0:x - u0 + w]
        m = cell[..., 3] > 0
        sub[m] = cell[m]
    return G.centre_frame(canvas, u0, r0)


def build(table):
    with open(G.lp(os.path.join(SRC, "aatrox_fx_anchors.json")), encoding="utf-8") as f:
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
                out[tag].append((place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--ring", help="the ring redraw's folder (w_ring and w_snap 66 wide), with --raw")
    args = ap.parse_args()
    if args.raw:
        if not args.ring:
            sys.exit("--raw needs --ring (w_ring and w_snap come from the 66-wide redraw)")
        from_raw({"raw": args.raw, "ring": args.ring})
    for sheet, table in (("league_aatrox_fx", FX), ("league_aatrox_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
