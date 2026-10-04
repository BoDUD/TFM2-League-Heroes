#!/usr/bin/env python3
"""Import Aatrox's effects (assets/source/aatrox/PROMPTS_FX.md, 24 sheets; w_ring and w_snap redrawn 66 wide for the
33000 ring) as the game sheets league_aatrox_fx and league_aatrox_big.

    python tools/art/import_aatrox.py --raw <Codex's delivery> --ring <the ring redraw> [--only p_swing q2_body ...]
                                                                       # raw -> native strips (all, or the named ones)
    python tools/art/import_aatrox.py                                  # native strips -> sheets

The native strips that other scripts draw or cut come after --raw: tools/art/chain_aatrox.py (w_chain_grow, from
w_chain), tools/art/warn_aatrox.py (q1_warn, q2_warn, q3_warn and the fear's ground ring r_fear_ring),
tools/art/import_redo_aatrox.py (r_aura, r_burst);
--raw keeps their cells in aatrox_fx_anchors.json (Codex's delivery: at_work/codex5/aatrox_fx_done, the ring redraw
at_work/codex6/aatrox_fx_ring_done; --only p_swing q2_body rebuilds the two the effects audit had resized).

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
(their pieces of 1% of the frame and up; sparks do not stretch it), the pack's sizes; `xmul` / `ymul` shorten one
axis after it (the passive's streak: 21 px instead of 36, so it ends on a target 40-44 px off, not 13 px past it; Q2's
impact fan +-18 rows instead of +-26, inside its warning's trapezoid). The projectiles (the chain, its
links, Q1 and Q2's ground shapes) are made exactly symmetric about their anchor's row (the game turns them with their
flight). The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; the soles
11 under it), measured on the finished strips (tools/art/rig_aatrox.py): the sword's tip in the passive's thrust
(attack_p 4, the tip at (24, -8..-5)) (22, -7), the blades' tips on each Q's blow (frame 6, one spot per form: the base
strips and World Ender's q*_r), the red claw in W 4 (16, -13);
the line pictures on the line's middle (a LineRangeProjectile is drawn centred on it: Q1 45000 long, Q2 26000 - the
fan's point on the caster, 13 px back); rings round a unit's feet 9 under the pivot (FEET).
Timings (60 ticks a second, whole ticks; the effects audit of 2026-10-04 found effects ahead of the blade):
  * the slashes start on the blow (body frame 6, tick 36): the arc (frame 2) for a tick, then the full arc or the
    burst - frame 1, a glint where the blade was not yet, is left out; build_aatrox.py plays them on the blow from
    the shape's point (a cast that lays no shape shows none), standing where he strikes; Q3's arc is drawn with its
    foot 10 px ahead of its burst's: its tick sits 10 px back (Q3_ARC), its foot on the blade's tip like the burst's;
  * the passive's streak starts with the thrust (attack_p 4, tick 18 = p_hit_t), its glint and growth a tick each;
  * Q's warning runs the whole wind-up (tools/art/warn_aatrox.py, one frame each STEP ticks): q*_tele, _b, _c, on
    picture-only twins of the shape re-laid at TELE_T from where he stands (on Ally: the enemy AI does not dodge
    them; _c only when E does not dash - build_aatrox.py), play the frames up to LOCK_T, each its own ticks', and
    q*_body, on the real shape laid at
    LOCK_T, the rest until the blow, then the impact in whole ticks (its first frame, a few loose squares where the
    warning had been whole, is left out: the ground shape blinked out for 2 ticks on the blow);
  * E's trail: e_dash behind him for the rush, e_dash_back (the same trail turned round) for the hop back, its
    bright head at his front as he hops, 3 px a tick, then on the spot he lands on, the streak cut at his front where
    he started (HOP_CLIP: it ran 14 px past it);
  * the projectiles start with an empty tick (a projectile's first move points its picture up; import_lucian.py's
    RAY_SKIP); the chain shows from its first move (chain_aatrox.py SHOW 0, under him), the claw's flash (w_throw)
    only until its head comes out from under his arm (tick 17);
  * the W ring appears and turns to 1.5 s (the main pack and the native add-on addons/league_aatrox_chain both play
    league_aatrox_w_ring; w_link, the links the add-on flies to the ring's centre, is bound by the add-on's kit only).
  * R's fear: a ring turning on the ground round the feet, under the unit (r_fear_ring, warn_aatrox.py).
Codex's frames get a few clean-ups as the sheets are made (TIDY: loose sparks off - every single-square one of
r_renew and the W ring -, every frame of r_renew mirrored: it follows him, and the red side draws a following
picture unmirrored).
Native strips no sheet uses (kept as Codex's import, not built): aatrox_fx_r_feared.png (the swirl over the head,
replaced by r_fear_ring) and aatrox_fx_r_transform.png (replaced by import_redo_aatrox.py's r_burst).
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

# raw strip -> native: frames n, size (game px) over measure, anchor, ramps; mirror (projectiles), src (the ring redraw);
# xmul / ymul: one axis shortened after the scale (xmul also a list, one a frame)
RAW = {
    "a_hit": dict(n=4, size=14, measure="m", anchor=("fixed", "core", 0), ramps="FIRE"),
    # the long streak (frame 3, x 627-1212) runs over two of the manifest's cells: cut at the drawing's gaps instead;
    # 36 px long it ran from the blade's tip (22 px ahead) to 57 px ahead, 13 px past a target at 44 (the empowered
    # attack starts 24-44 px from its target, the SDK log): 21 px, the streak ends on him; the glint (frame 1, a star
    # on the blade's tip) keeps its shape
    "p_swing": dict(n=5, size=36, measure="w", anchor="left", ramps="FIRE", cuts=[0, 160, 580, 1225, 1630, 1983],
                    xmul=[1.0, 0.58, 0.58, 0.58, 0.58]),
    "p_hit": dict(n=5, size=22, measure="m", anchor=("fixed", "core", 0), ramps="FIRE SHADE"),
    "q1_slash": dict(n=5, size=44, measure="h", anchor=("fixed", "bottom", 2), ramps="FIRE DUST"),
    "q2_slash": dict(n=5, size=30, measure="h", anchor=("fixed", "right", 2), ramps="FIRE"),
    "q3_slash": dict(n=5, size=44, measure="h", anchor=("fixed", "bottom", 2), ramps="FIRE SHADE"),
    "q1_body": dict(n=4, size=46, measure="w", anchor="cell", ramps="FIRE", mirror=True),
    # the fan's far crescent spanned +-26 rows across a +-18 warning (warn_aatrox.py Q2 half1): pressed to +-18
    "q2_body": dict(n=4, size=36, measure="w", anchor=("fixed", "left", 1), ramps="FIRE", mirror=True, ymul=0.69),
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


def from_raw(folders, only=None):
    manifests = {}
    for key, folder in folders.items():
        with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
            manifests[key] = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    apath = G.lp(os.path.join(SRC, "aatrox_fx_anchors.json"))
    anchors = {}
    if os.path.exists(apath):                  # the cells of the strips other scripts made (and the ones not rebuilt)
        with open(apath, encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
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
        xmul = spec.get("xmul", 1.0)
        sxs = [s * (xmul[k] if isinstance(xmul, list) else xmul) for k in range(len(rects))]
        sy = s * spec.get("ymul", 1.0)
        anc = [anchor(spec["anchor"], k, a, masks, rects, labels) for k in range(len(rects))]
        boxes = []
        for m in masks:
            ys, xs = np.nonzero(m)
            boxes.append((xs.min(), xs.max() + 1, ys.min(), ys.max() + 1))
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) * sx for (ax, _), b, sx in zip(anc, boxes, sxs)) - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * sy - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(rects), 4), np.uint8)
        H, W = solid.shape
        for i, m in enumerate(masks):
            ax, ay = anc[i]
            sx = sxs[i]
            cell = np.zeros((th, tw, 4), np.uint8)
            for r in range(th):
                sy0 = int(math.floor(ay + (r - U - 0.5) / sy))
                sy1 = max(int(math.floor(ay + (r - U + 0.5) / sy)), sy0 + 1)
                sy0, sy1 = max(0, sy0), min(H, sy1)
                if sy1 <= sy0:
                    continue
                for c in range(tw):
                    sx0 = int(math.floor(ax + (c - L - 0.5) / sx))
                    sx1 = max(int(math.floor(ax + (c - L + 0.5) / sx)), sx0 + 1)
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
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {max(sxs):.4f} x {sy:.4f} ({spec['size']} px "
              f"over {ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    with open(apath, "w", encoding="utf-8", newline="\n") as f:     # the format the other scripts write
        json.dump(anchors, f, indent=1)


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
# the Q blows (frame 6), one spot per form: the base strips (tools/art/fix_aatrox_q.py) hold the design's greatsword,
# World Ender's forms (q*_r, import_redo_aatrox.py) still Codex's 1.2-1.4x blade, 9-13 px further out - one spot for
# both left the arc and the burst 9 px in front of the base blade. Measured with --tips on the Q strips of 15:06
# (phase 1b): re-run it and move these whenever the Q strips change
Q1_TIP = (25, 10)           # skill 6, the tip at (25, 7..9): the arc's foot under it on the soles' row
Q1_TIP_R = (37, 10)         # skill_r 6, the tip on the ground at (37, 8..9)
# the crescent's outer rim (the anchor; the drawing reaches 3 px past it) 4 px short of the level blade's tip: q2 6 at
# (28, -3..-1) - the anchor at 24, drawn to 27, so the blade's outlined tip is not drawn inside the crescent's white
# rim (at 25 it ended on the tip and the tip's black squares showed as specks in the fire); q2_r 6 at (41, -2..1) -
# the anchor at 34, drawn to 37 on that longer blade, 2.5 px past the trapezoid (inside it the crescent stood 9 px off
# the blade)
Q2_TIP = (24, -2)
Q2_TIP_R = (34, -2)
Q3_TIP = (28, 10)           # q3 6, the slam: the tip at (28, 6..8), the burst's foot under it on the ground
Q3_TIP_R = (38, 10)         # q3_r 6, the tip on the ground at (38, 10)
Q3_ARC = -10                # q3_slash frame 2 (the arc) has its foot 10 px ahead of the burst's: placed 10 px back
CLAW = (16, -13)            # the red claw in W 4: its tip at (16, -14..-12)
HIT = (0, -8)               # a hit on the upper body of a 32-44 px unit
BODY = (0, -6)              # round the body (the chains wrapping him, the renewal ring)
FEET = (0, 9)               # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLES = (0, 11)             # the ground under a unit (its soles' row)
BEHIND = (-2, 6)            # E's trail: its bright head at his back, low
FRONT = (2, 6)              # the hop back's trail (turned round): its bright head at his front
# E's trails do not follow him (is_follow false: played from E's Delayed, see build_aatrox.py) - they stay on the
# spot he dashes from, so each tick's frame is placed where he is that tick: his move from the spot E starts at,
# ticks 0, 1, 2... of the dash (SDK moves, 28 logged games, 2026-10-04 - the first step lands in E's own tick):
# the rush (RushTime 3000 x 7) 4 px a tick until it reaches its target, 22 px on 5 of 5 logged rushes; the hop back
# (MoveBack 3000 x 6) 2 px a tick, then 5.5 px on its last tick, 17 px (24 of 24 logged hops). One frame for the
# rush laid at its start left the streak on ground behind his starting spot while he ran 21 px on (the review,
# fix round 2: a 12-21 px gap between its bright head and his back)
RUSH_X = (4, 8, 12, 16, 20, 22)
HOP_X = (-2, -4, -6, -8, -10, -12, -17)
# each trail cut where he started: the rush's streak at his back there, the hop's at his front there (the whole
# 30-px streak ran over ground he never crossed - 14 px past his front on the hop, 29 px behind his back on the
# rush); in the frames while he moves pieces under 6 squares are left out (the cut left a 2-square sliver at his
# toe on the hop's first tick, a white speck - fix round 2; the fading frames keep their embers)
RUSH_CUT = {"clip": (-3, 60), "least": 6}
HOP_CUT = {"clip": (-60, 3), "least": 6}
Q1_LINE = (0, 0)            # the Q1 line's middle (45000 long): the rectangle from him
Q2_POINT = (-13, 0)         # the Q2 fan's point on the caster (a 26000 line, centred)
Q2_WARN = (1, 0)            # the trapezoid's middle, 14 px ahead of him (7 behind to 34.5 ahead)
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
Q_BLOW = 36                 # Q's blow, ticks from the cast (build_aatrox.py q_hit_t: body frame 6)
FX = {
    "a_hit": [("a_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    # with the thrust (attack_p 4, ticks 18-24; build_aatrox.py plays it at p_hit_t): the glint on the blade's tip and
    # the streak's growth a tick each, the full streak (frame 3) from tick 20 (it started 4 ticks before the thrust,
    # in front of a blade still drawn back); its last ember gone on tick 30, when the blade is drawn back (attack_p 6 -
    # 4 ticks long it floated alone in the air for 2)
    # frame 5 (a lone 2-square ember) left out, its 2 ticks on the fading streak (frame 4): gone on tick 30 still
    "p_swing": [("p_swing", seq(range(4), [TICK, TICK, 4 * TICK, 6 * TICK]), [P_TIP])],
    "p_hit": [("p_hit", seq(range(5), [40, 50, 60, 80, 100]), [HIT])],
    # on the blow (body frame 6, the blade down, tick Q_BLOW): the arc a tick, then the full arc (Q1, Q2) or the burst
    # (Q3) - frame 1 (the glint up where the blade was not yet) is left out. build_aatrox.py plays them on the blow
    # (a Delayed from the shape's point: only a cast that lays its shapes shows one), where he stands then; q*_slash_r
    # on World Ender's forms
    **{f"q{k}_slash{f}": [(f"q{k}_slash", seq([1], ms[:1]), [(spot[0] + arc, spot[1])]),
                          (f"q{k}_slash", seq(range(2, 5), ms[1:]), [spot])]
       for k, ms, spots, arc in ((1, [TICK, 5 * TICK, 5 * TICK, 6 * TICK], (Q1_TIP, Q1_TIP_R), 0),
                                 (2, [TICK, 5 * TICK, 5 * TICK, 6 * TICK], (Q2_TIP, Q2_TIP_R), 0),
                                 (3, [TICK, 6 * TICK, 7 * TICK, 8 * TICK], (Q3_TIP, Q3_TIP_R), Q3_ARC))
       for f, spot in (("", spots[0]), ("_r", spots[1]))},
    "q_hit": [("q_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "q_edge": [("q_edge", seq(range(5), [40, 50, 60, 80, 100]), [SOLES])],
    # E's trails, a frame each tick of the dash with its bright head where he is (RUSH_X / HOP_X), cut where he started
    # (RUSH_CUT / HOP_CUT), then fading on the spot he lands on: the rush's at his back, the hop back's (the trail
    # turned round) at his front
    "e_dash": [("e_dash", [(f, TICK)], [(BEHIND[0] + x, BEHIND[1])], RUSH_CUT)
               for f, x in zip((0, 0, 0, 1, 1, 1), RUSH_X)]
              + [("e_dash", seq((2, 3), [4 * TICK, 5 * TICK]), [(BEHIND[0] + RUSH_X[-1], BEHIND[1])],
                  {"clip": RUSH_CUT["clip"]})],
    "e_dash_back": [("e_dash", [(f, TICK)], [(FRONT[0] + x, FRONT[1])], "flip", HOP_CUT)
                    for f, x in zip((0, 0, 0, 1, 1, 1, 1), HOP_X)]
                   + [("e_dash", seq((2, 3), [4 * TICK, 5 * TICK]), [(FRONT[0] + HOP_X[-1], FRONT[1])], "flip",
                      {"clip": HOP_CUT["clip"]})],
    # the claw's flash as W's throw starts (skill2 4, ticks 14-16): the chain shows from its first moving tick (chain_
    # aatrox.py SHOW 0) and its burning head is out from under his arm on tick 17, 5 px under the claw (the projectile's
    # height): the flash's ember and wisp (frames 3-4, to tick 21) burnt on in the claw beside it - two fire spots
    # (the review, phase 1b) - and are left out
    "w_throw": [("w_throw", seq(range(2), [TICK, 2 * TICK]), [CLAW])],
    # the chain: 66000 at 2200 a tick = 30 ticks, paid out from his hand (tools/art/chain_aatrox.py: frame k = the claw
    # k x 2.2 px out and the links back to his hand, empty until it leaves the claw); the links: up to 33000 at 2500 =
    # 13 ticks
    "w_chain": [("w_chain_grow", [(EMPTY, TICK)] + seq(range(30), [TICK] * 29 + [1000]), [(0, 0)])],
    "w_link": [("w_link", flight(4, 50, 300), [(0, 0)])],
    "w_hit": [("w_hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "w_yank": [("w_yank", seq(range(4), [40, 60, 80, 100]), [BODY])],
    "w_slowed": [("w_slowed", seq(range(4), [100] * 4), [FEET])],
    # 1.5 s of fear (90 ticks): a ring turning on the ground round the feet (build_aatrox.py z -1, under the unit);
    # the swirl over the head (aatrox_fx_r_feared.png) lay on tall champions' faces and floated over minions
    "r_feared": [("r_fear_ring", loop([0, 1, 2, 3], 6 * TICK, 1500), [FEET])],
    "r_renew": [("r_renew", seq(range(5), [50, 70, 90, 110, 130]), [BODY])],
}
# Q's warning over the whole wind-up, a frame each STEP ticks (tools/art/warn_aatrox.py): before LOCK_T on the
# picture-only twins build_aatrox.py lays at TELE_T (q*_tele, _b, _c: each re-aimed from where he stands then - he
# walks on through the wind-up - and showing the frames of its own ticks, so the fill runs on from one to the next;
# _c only when E does not dash on tick 18: the warning is off for the dash), then q*_body on the real shape laid at
# q_lock_t (the rest until the blow on tick 36,
# League's 0.6 s, then the impact). Q1 / Q2's twins are the same line as the real shape (drawn on its middle); a line's
# last frame is held a tick more - it goes on its last tick, the next appears that tick, so they meet without a gap.
# Q3's are ViewEffects on the point, as q3_body: each ends with its frames.
LOCK_T, STEP = 26, 2
TELE_T = (0, 9, 18)         # build_aatrox.py TELE_T
TELE_TAGS = ("tele", "tele_b", "tele_c")


def warn_ticks(t0, t1, line):
    """The warning's frames for ticks t0..t1 - 1 of the wind-up (frame = tick // STEP); a line's last one a tick more."""
    out, t = [], t0
    while t < t1:
        f = t // STEP
        e = min(t1, (f + 1) * STEP)
        out.append((f, (e - t) * TICK))
        t = e
    if line:
        out[-1] = (out[-1][0], out[-1][1] + TICK)
    return out


WARN = seq(range(LOCK_T // STEP, Q_BLOW // STEP), [STEP * TICK] * ((Q_BLOW - LOCK_T) // STEP))
TELE_SPOTS = {1: Q1_LINE, 2: Q2_WARN, 3: FEET}
BIG = {
    **{f"q{k}_{name}": [(f"q{k}_warn", warn_ticks(t0, t1, k < 3), [TELE_SPOTS[k]])]
       for k in (1, 2, 3)
       for name, t0, t1 in zip(TELE_TAGS, TELE_T, TELE_T[1:] + (LOCK_T,))},
    # the impact from its second frame (the first was 8 / 138 / 81 squares after a warning of 585 / 1218 / 1565), in
    # whole ticks
    "q1_body": [("q1_warn", WARN, [Q1_LINE]), ("q1_body", seq(range(1, 4), [4 * TICK, 5 * TICK, 6 * TICK]), [Q1_LINE])],
    "q2_body": [("q2_warn", WARN, [Q2_WARN]), ("q2_body", seq(range(1, 4), [4 * TICK, 5 * TICK, 6 * TICK]), [Q2_POINT])],
    "q3_body": [("q3_warn", WARN, [FEET]), ("q3_body", seq(range(1, 5), [4 * TICK, 5 * TICK, 7 * TICK, 10 * TICK]), [FEET])],
    # the ring (the main pack's and the add-on's): appears, turns to 1.5 s
    "w_ring": [("w_ring", seq([0, 1], [60, 60]) + loop([2, 3, 4, 5], 80, 1280) + seq([5], [100]), [FEET])],
    "w_snap": [("w_snap", seq(range(5), [50, 60, 70, 80, 100]), [FEET])],
    # with the ult's 48 ticks (800 ms): the flash and the ground ring only (import_redo_aatrox.py r_burst - the fire
    # wings went, Codex's transformation strip unfolds League's wings)
    "r_transform": [("r_burst", seq(range(8), [40, 70, 90, 110, 120, 130, 120, 120]), [SOLES])],
    # the wings loop of Codex's redo (import_redo_aatrox.py): anchored on the standing point, behind him
    "r_aura": [("r_aura", seq(range(6), [150] * 6), [(0, 0)])],
}


def place(cell, anchor_px, spots, clip=None):
    """The cell with its anchor on every spot (from the pivot), as one frame centred on the pivot; `clip` (x0, x1): only
    the columns x0..x1 from the pivot kept."""
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
    if clip:
        xs_ = np.arange(canvas.shape[1]) + u0
        canvas[:, (xs_ < clip[0]) | (xs_ > clip[1])] = 0
    return G.centre_frame(canvas, u0, r0)


# clean-ups of Codex's frames when the sheets are made (the native strips stay as imported): frame (from 0, or "*" for
# every frame, done first and again after any mirror) -> the smallest piece kept (8-connected squares; smaller ones are
# loose sparks), "mirror" / "mirror_r" - the left / right half (anchor column kept) mirrored onto the other, for a
# picture that follows him (r_renew: is_follow, which the red side draws unmirrored), or "unspeck" - a dark square
# with bright squares on all four sides takes their colour (a black dot inside a glow)
TIDY = {
    "p_swing": {3: 2},          # the streak's tail: a lone square behind it
    # the fading ring and its flames were lopsided (mirror overlap 0.37 / 0.29): the ring's right half (one piece of
    # 195; the left half left it in three) and the flames' left half (3 flames, fewer sparks); the first three too
    # (fix round 3: the red side drew them flipped, mirror overlap 0.84-0.91), each by the half that keeps it in the
    # fewest pieces (1, 2 and 1; the other half left 5, 5 and 5)
    "r_renew": {"*": 2, 0: "mirror_r", 1: "mirror", 2: "mirror_r", 3: "mirror_r", 4: "mirror"},
    # the ring's flames: single squares in the loop frames (fix round 2)
    "w_ring": {"*": 2},
    # the pillar burst (frame 3): one 34163F square inside its white core read as a black dot for 6 ticks
    "q3_slash": {2: "unspeck"},
}


def pieces(mask):
    """8-connected pieces of a mask as lists of (y, x)."""
    seen = np.zeros_like(mask)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        todo, piece = [(y0, x0)], []
        seen[y0, x0] = True
        while todo:
            y, x = todo.pop()
            piece.append((y, x))
            for dy, dx in N8:
                yy, xx = y + dy, x + dx
                if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1] and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    todo.append((yy, xx))
        out.append(piece)
    return out


def tidy(src, strip, anchor_px):
    strip = [c.copy() for c in strip]
    rules = dict(TIDY.get(src, {}))
    least = rules.pop("*", None)
    steps = [(k, least) for k in range(len(strip))] if least else []
    # the loose sparks off again after the mirrors (a mirrored half can leave a single square at the anchor column)
    for k, how in steps + list(rules.items()) + (steps if any(isinstance(h, str) for h in rules.values()) else []):
        c = strip[k]
        if how == "unspeck":
            lum = c[..., :3].astype(int).sum(-1) * (c[..., 3] > 0)
            for y in range(1, c.shape[0] - 1):
                for x in range(1, c.shape[1] - 1):
                    nb = [(y + dy, x + dx) for dy, dx in N4]
                    if c[y, x, 3] and lum[y, x] < 300 and all(lum[q] > 500 for q in nb):
                        cols = [tuple(c[q]) for q in nb]
                        c[y, x] = max(set(cols), key=cols.count)
        elif how in ("mirror", "mirror_r"):
            ax, src = anchor_px[0], c.copy()
            dst = range(ax + 1, c.shape[1]) if how == "mirror" else range(0, ax)
            for x in dst:
                c[:, x] = src[:, 2 * ax - x] if 0 <= 2 * ax - x < c.shape[1] else 0
        else:
            for piece in pieces(c[..., 3] > 0):
                if len(piece) < how:
                    for y, x in piece:
                        c[y, x] = 0
    return strip


def build(table):
    with open(G.lp(os.path.join(SRC, "aatrox_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    out = {}
    for tag, parts in table.items():
        out[tag] = []
        for src, frames, spots, *how in parts:
            if src == EMPTY:
                out[tag] += [(np.zeros((3, 3, 4), np.uint8), ms) for _, ms in frames]
                continue
            strip = tidy(src, cells(src, anchors[src]["frames"]), anchors[src]["anchor"])
            ax, ay = anchors[src]["anchor"]
            if "flip" in how:                  # the strip turned round left to right, its anchor with it
                strip = [c[:, ::-1] for c in strip]
                ax = strip[0].shape[1] - 1 - ax
            cut = next((h for h in how if isinstance(h, dict)), {})
            for k, ms in frames:
                if k == EMPTY:
                    out[tag].append((np.zeros((3, 3, 4), np.uint8), ms))
                    continue
                f = place(strip[k], (ax, ay), spots, cut.get("clip"))
                if cut.get("least"):            # pieces under `least` squares left out (the slivers a cut leaves)
                    for piece in pieces(f[..., 3] > 0):
                        if len(piece) < cut["least"]:
                            for y, x in piece:
                                f[y, x] = 0
                out[tag].append((f, ms))
    return out


# the spots measured on a body frame (strip tag, frame from 1) and how each sits on that frame's forward-most square
# (the blade's tip or the claw): --tips compares them with the strips as they are now
TIPS = {
    "P_TIP": (("attack_p", 4), ("attack_p_r", 4)),      # the streak's root 2 px behind the tip, on its rows
    "Q1_TIP": (("skill", 6),),                          # the arc's foot under the tip, on the ground (row 10)
    "Q1_TIP_R": (("skill_r", 6),),
    "Q2_TIP": (("q2", 6),),                             # the crescent's rim 4 px short of the tip
    "Q2_TIP_R": (("q2_r", 6),),
    "Q3_TIP": (("q3", 6),),                             # the burst's foot under the tip, on the ground
    "Q3_TIP_R": (("q3_r", 6),),
    "CLAW": (("skill2", 4),),                           # the claw's tip, its middle row
}


def tips():
    """The forward-most square of each measured frame in assets/source/native (pivot-relative, rows as a span) next
    to the spot that rests on it: run it after the action strips change, the spots are constants."""
    native = os.path.join(ROOT, "assets", "source", "native")
    with open(G.lp(os.path.join(native, "aatrox_cells.json")), encoding="utf-8") as f:
        c = json.load(f)
    cw, ch = c["cell"]
    z = c["scale"]
    for name, frames in TIPS.items():
        out = []
        for tag, k in frames:
            big = np.asarray(Image.open(G.lp(os.path.join(native, f"aatrox_{tag}.png"))).convert("RGBA"))
            cols = big.shape[1] // (cw * z)
            x0, y0 = ((k - 1) % cols) * cw * z, ((k - 1) // cols) * ch * z
            im = big[y0 + z // 2:y0 + ch * z:z, x0 + z // 2:x0 + cw * z:z]
            px, py = c["tags"][tag][k - 1]["pivot"]
            ys, xs = np.nonzero(im[..., 3] > 0)
            rows = ys[xs == xs.max()] - py
            out.append(f"{tag} {k}: ({xs.max() - px}, {rows.min()}..{rows.max()})")
        print(f"{name:7s} {str(globals()[name]):10s} " + "   ".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--ring", help="the ring redraw's folder (w_ring and w_snap 66 wide), with --raw")
    ap.add_argument("--only", nargs="+", choices=sorted(RAW), help="with --raw: rebuild just these native strips")
    ap.add_argument("--tips", action="store_true", help="only print the spots next to the action strips' tips")
    args = ap.parse_args()
    if args.tips:
        return tips()
    if args.raw:
        if not args.ring:
            sys.exit("--raw needs --ring (w_ring and w_snap come from the 66-wide redraw)")
        from_raw({"raw": args.raw, "ring": args.ring}, args.only)
    for sheet, table in (("league_aatrox_fx", FX), ("league_aatrox_big", BIG)):
        tags = build(table)
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
