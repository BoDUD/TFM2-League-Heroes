#!/usr/bin/env python3
"""Import Kai'Sa's effects (assets/source/kaisa/PROMPTS.md, 1-20) as the game sheet league_kaisa_fx.

    python tools/art/import_kaisa.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_kaisa.py                                   # native strips -> the effect sheet

The body comes from tools/art/fix_kaisa_strips.py and import_native.py. Codex delivered image-model drafts
(outputs/kaisa-fx, 2026-10-02 14:14: 1659-2172 x 724-948 px, soft alpha, free colours; HANDOFF and manifest in
assets/source/kaisa/codex_fx), every frame's rectangle in manifest.json (`assets[].frames[].rect` = [x, y, w, h], the
pl_stack 6 x 4 and the shield 6 x 2 read row by row). --raw turns each frame into a cell of a native strip
(assets/source/kaisa/kaisa_fx_<name>.png, 8x, plus kaisa_fx_anchors.json): each game pixel the majority colour of
the source pixels it covers, opaque when a third of them are solid (alpha 100 and up), every colour snapped to the
pack's 19 (plasma, the white-pink cores, void violet, gold, smoke); then the ring comes off the glows (an edge pixel
in a ramp's darkest shade goes when two lighter neighbours hold the shape, else it takes the next shade). One scale
per strip: `size` game px over the drawings' widest (w), tallest (h) or larger side (m), the pack's sizes. The three
projectiles are made exactly symmetric about their core's row (the game turns them with their flight).
Anchors (source pixels, the same spot in every cell unless the drawing itself moves): the projectiles on their
white-pink core (its front half); the palm flash, the cannon's charge and blast on their left edge at the core's row
(the palm / the mouth: frame 2's cone, frame 2's converging point, frame 1's blast); the hits and the rupture on frame
1's flash; the stack mark on its cell's middle; the pod's flash on its plume's foot; the ground pictures (E's ring,
R's launch and landing, the evolution's column) on the middle of their ring; the arcs, the invisibility outline and
the shield on their drawings' foot (the feet they were drawn round); the dash trail on its right edge (her).
Q and W's projectiles are drawn here instead (`drawn()`, kaisa_fx_q_missile.png and kaisa_fx_w_bolt.png written for
review): Codex's pink dart and cone looked nothing like League's (the user: "Q和w特效和lol不一样", "Q应该是多重激光吧
w应该做大点吧 飞得距离很远啊"). League's own textures (Kaisa_Base_W_Bullet, W_plasma, Q_cas_smoke in Kaisa.wad.client)
give the colours: W a lilac bullet (#C87FF2) with a pink-white core (#F9D9EF) and magenta plasma arcs (#E66AD7) on
deep violet (#5A1368); Q magenta-purple (#AE45BF). Q's missile is a laser 26 px long, 1 row with a glow row on either side
near its white-pink head, growing out of the pod over its first two frames; W's is a 45 x 13 bullet: the elongated head,
a tapering wavy trail, a magenta arc mirrored above and below, its first frame with a short trail. W's charge, blast and
hit keep Codex's drawings in League's violet (the plasma ramp mapped onto the bullet's), the blast 26 px, the hit 30.
The second step places every cell by its anchor on a spot from the pivot (game px, x right, y down; measured on
league/champions/league_kaisa: the attack's palm (19, -9) in frame 3 and (23, -10) in frame 4, W's cannon (22, -6)
while it charges (frames 3-4) and (24, -16) as it fires (frame 5), Q's pods' openings (-13, -29) and (15, -29) in
frame 3, the soles 11 under the pivot) and times it by the kit: the attack bolt leaves her palm 9 px up (the kit's
y_offset -3000 lifts it 8) and starts empty for the 3 ticks it spends inside her (19 px at 7000 a tick), W's bolt for
2 (24 px at 14000), then they loop and hold (`repeat: false`); Q's missiles come out of the pods (y_offset -24000,
29 px up). W's charge waits for the cannon to come up (170 ms) and burns to the shot (383 ms); W's blast sits
between the cannon (-16) and its bolt (8 px up). The plasma marks last 1 s over the target's head (the kit plays one
per hit), the shield 2 s (its 120 ticks), the E arcs 1 s (replayed every second of the attack speed).
Writes league/effects/league_kaisa_fx.
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

SRC = os.path.join(ROOT, "assets", "source", "kaisa")
MOD = os.path.join(ROOT, "league")
Z = 8

PLASMA = ["4A0C63", "8E1FB8", "D23CF0", "F408EA", "FF9BF5"]
HOT = ["FFFFFF", "FFE3FB", "FFC2F6"]
VIOLET = ["2B1450", "5226A0", "8A55E6", "BFA2FF"]
GOLD = ["8D6246", "D7A965", "F7D896"]
SMOKE = ["2A1F46", "463970", "6D5EA2", "A99BD6"]
PAL_HEX = PLASMA + HOT + VIOLET + GOLD + SMOKE
# W in League's violet: the bullet's ramp (Kaisa_Base_W_Bullet, W_plasma), dark to light; Codex's plasma ramp and the
# pinker cores mapped onto it for W's charge, blast and hit
W_RAMP = ["2B1450", "5A1368", "8A55E6", "C87FF2", "F9D9EF", "FFFFFF"]
W_ARC = "E66AD7"
VOID = dict(zip(PLASMA, W_RAMP[:5]), FFE3FB="F9D9EF", FFC2F6="F9D9EF")
# Q's laser: League's Q magenta-purple (Kaisa_Base_Q_cas_smoke), dark to light
Q_RAMP = ["5A1368", "AE45BF", "E66AD7", "FFCADD", "FFFFFF"]
PAL = np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in PAL_HEX], float)
# a ramp's darkest shade at a glow's edge -> the next shade (smoke keeps its dark edge: it is a cloud, not a glow)
RIM = {"4A0C63": "8E1FB8", "2B1450": "5226A0"}
N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# raw strip -> native: frames n, size (game px) over measure, anchor, mirror (projectiles)
RAW = {
    "bolt": dict(n=4, size=12, measure="w", anchor="head", mirror=True),
    "shot": dict(n=4, size=12, measure="w", anchor=("fixed", "left", 1)),
    "hit": dict(n=4, size=10, measure="m", anchor=("fixed", "core", 0)),
    "pl_stack": dict(n=24, size=16, measure="w", anchor="gem", pips=True),
    "p_burst": dict(n=7, size=26, measure="m", anchor=("fixed", "core", 0)),
    "e_cast": dict(n=6, size=42, measure="h", anchor=("fixed", "ring", 0)),
    "e_aura": dict(n=6, size=34, measure="h", anchor=("fixed", "foot", None)),
    "e_invis": dict(n=5, size=42, measure="h", anchor=("fixed", "foot", None)),
    "q_pod": dict(n=5, size=12, measure="h", anchor=("fixed", "plume", 1)),
    "q_hit": dict(n=5, size=14, measure="m", anchor=("fixed", "core", 0)),
    "w_charge": dict(n=5, size=16, measure="w", anchor=("fixed", "left", 1), void=True),
    "w_muzzle": dict(n=5, size=26, measure="w", anchor=("fixed", "left", 0), void=True),
    "w_hit": dict(n=6, size=30, measure="m", anchor=("fixed", "core", 0), void=True),
    "r_launch": dict(n=6, size=28, measure="w", anchor=("fixed", "ring", 2)),
    "r_trail": dict(n=4, size=36, measure="w", anchor=("fixed", "right", 0)),
    "r_land": dict(n=5, size=26, measure="w", anchor=("fixed", "ring", 1)),
    "r_shield": dict(n=12, size=42, measure="h", anchor=("fixed", "foot", None)),
    "evolve": dict(n=8, size=56, measure="h", anchor=("fixed", "ring", 0)),
}


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


def snap(a, solid):
    """Palette index of every solid pixel (-1 elsewhere)."""
    idx = np.full(a.shape[:2], -1, int)
    ys, xs = np.nonzero(solid)
    for k in range(0, len(ys), 100000):
        px = a[ys[k:k + 100000], xs[k:k + 100000], :3].astype(float)
        idx[ys[k:k + 100000], xs[k:k + 100000]] = ((px[:, None] - PAL[None]) ** 2).sum(2).argmin(1)
    return idx


LIT_PIP = [["FFE3FB", "F408EA"], ["F408EA", "D23CF0"]]
DIM_PIP = [["5226A0", "2B1450"], ["2B1450", "2B1450"]]
FADE_PIP = [["D23CF0", "8E1FB8"], ["8E1FB8", "8E1FB8"]]


def pips(cell, ax, ay, i):
    """The stack mark's row of four pips, redrawn so the count reads at game size (Codex's pips touch each other once
    shrunk): everything 3 rows under the gem cleared, four 2x2 squares a square apart 4-5 rows under it - row r of the
    strip has r + 1 lit (white-pink on magenta), the rest dark violet; the last frame of each row (the fade) dims the
    lit ones."""
    out = cell.copy()
    out[ay + 3:] = 0
    lit, fade = i // 6 + 1, i % 6 == 5
    for p in range(4):
        x0 = ax - 5 + 3 * p
        pat = (FADE_PIP if fade else LIT_PIP) if p < lit else DIM_PIP
        for dy in range(2):
            for dx in range(2):
                h = pat[dy][dx]
                out[ay + 4 + dy, x0 + dx, :3] = [int(h[k:k + 2], 16) for k in (0, 2, 4)]
                out[ay + 4 + dy, x0 + dx, 3] = 255
    return out


def mirror(cell, U):
    out = cell.copy()
    for r in range(U):
        if 2 * U - r < cell.shape[0]:
            out[2 * U - r] = cell[r]
    return out


def bright(a):
    return (a[..., 3] >= 100) & (a[..., :3].min(-1) >= 215)


def anchor(how, k, a, solid, rects):
    """(x, y) of frame k's anchor in the source."""
    x, y, w, h = rects[k]
    if how == "cell":
        return x + w / 2, y + h / 2
    if how[0] == "fixed":                  # frame j's anchor, the same spot in every cell
        if how[1] == "foot":
            ax, ay = foot(solid, rects)
            return x + ax - rects[0][0], y + ay - rects[0][1]
        j = how[2]
        ax, ay = anchor(how[1], j, a, solid, rects)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    b = bright(a[y:y + h, x:x + w])
    if how == "head":                      # the white-pink core in the drawing's front half
        b[:, :int(x0 + 0.5 * (x1 - x0))] = False
        by, bx = np.nonzero(b)
        if not len(bx):
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + (bx.min() + bx.max() + 1) / 2, y + (by.min() + by.max() + 1) / 2
    if how == "gem":                       # the stack mark's gem: the white-pink core over the pips' row
        b[int(y0 + 0.6 * (y1 - y0)):] = False
        by, bx = np.nonzero(b)
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how == "core":                      # the white-pink flash's middle
        by, bx = np.nonzero(b)
        if len(bx) < 20:
            return x + (x0 + x1) / 2, y + (y0 + y1) / 2
        return x + bx.mean() + 0.5, y + by.mean() + 0.5
    if how in ("left", "right"):           # the drawing's left (right) edge at its core's row
        cut = b.copy()
        third = int(0.35 * (x1 - x0))
        if how == "left":
            cut[:, x0 + third:] = False
        else:
            cut[:, :x1 - third] = False
        by, bx = np.nonzero(cut)
        row = (by.mean() + 0.5) if len(by) else (y0 + y1) / 2
        return x + (x0 if how == "left" else x1), y + row
    if how == "plume":                     # the plume's foot: the middle of its lowest rows
        m = ys >= y1 - max(3, (y1 - y0) // 20)
        return x + xs[m].mean() + 0.5, y + y1
    if how == "ring":                      # the ring's middle: the lower 40% of the drawing
        low = s.copy()
        low[:int(y1 - 0.4 * (y1 - y0))] = False
        ly, lx = np.nonzero(low)
        return x + (lx.min() + lx.max() + 1) / 2, y + (ly.min() + ly.max() + 1) / 2
    raise ValueError(how)


def foot(solid, rects):
    """The middle of the lowest drawn row over all frames (the feet the drawings were made round), in frame 0's
    coordinates."""
    lows, mids = [], []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        lows.append(ys.max() + 1)
        mids.append((xs.min() + xs.max() + 1) / 2)
    return rects[0][0] + float(np.median(mids)), rects[0][1] + max(lows)


def from_raw(folder):
    with open(G.lp(os.path.join(folder, "manifest.json")), encoding="utf-8-sig") as f:
        manifest = {os.path.basename(a["file"]): a for a in json.load(f)["assets"]}
    anchors = {}
    for name, spec in RAW.items():
        fn = f"kaisa_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        rects = [[int(v) for v in f["rect"]] for f in manifest[fn]["frames"]]
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        idx = snap(a, solid)
        boxes = []
        for x, y, w, h in rects:
            ys, xs = np.nonzero(solid[y:y + h, x:x + w])
            boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
        ext = {"w": max(b[1] - b[0] for b in boxes), "h": max(b[3] - b[2] for b in boxes)}
        ext["m"] = max(ext["w"], ext["h"])
        s = spec["size"] / ext[spec["measure"]]
        anc = [anchor(spec["anchor"], k, a, solid, rects) for k in range(len(rects))]
        L = max(math.ceil(max(max(ax - b[0], b[1] - ax) for (ax, _), b in zip(anc, boxes)) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(ay - b[2], b[3] - ay) for (_, ay), b in zip(anc, boxes)) * s - 0.5), 0) + 1
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
                    if m.mean() < 1 / 3:
                        continue
                    col = np.bincount(idx[sy0:sy1, sx0:sx1][m], minlength=len(PAL)).argmax()
                    cell[r, c, :3] = PAL[col]
                    cell[r, c, 3] = 255
            cell = unrim(cell)
            if spec.get("void"):
                hx = hexes(cell)
                for old, new in VOID.items():
                    cell[hx == old, :3] = [int(new[k:k + 2], 16) for k in (0, 2, 4)]
            if spec.get("pips"):
                cell = pips(cell, L, U, i)
            if spec.get("mirror"):
                cell = mirror(cell, U)
            out[:, i * tw:(i + 1) * tw] = cell
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(rects)}
        hot = np.isin(hexes(out), HOT).sum()
        print(f"{fn}  {len(rects)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over "
              f"{ext[spec['measure']]}), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours, {hot} core px")
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(os.path.join(SRC, "kaisa_fx_anchors.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def put(a, x, y, h):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
        a[y, x, :3] = [int(h[k:k + 2], 16) for k in (0, 2, 4)]
        a[y, x, 3] = 255


def w_bullet(phase, trail=None, length=45, height=13):
    """W's void bullet pointing right: an elongated lilac head with a pink-white core toward the front, a tapering wavy
    violet trail with a magenta arc, exactly symmetric about the middle row; `trail` cuts the trail short (the start)."""
    H, W = height, length
    cy = H // 2
    a = np.zeros((H, W, 4), np.uint8)
    hx, rx, ry = W - 9, 8.5, 4.6
    tail0 = 0 if trail is None else max(0, int(hx - trail))
    for x in range(tail0, int(hx) + 1):
        u = (x - tail0) / max(1.0, hx - tail0)
        half = 0.6 + 3.2 * u ** 0.8
        for y in range(H):
            d = abs(y - cy)
            if d <= half:
                f = d / max(half, 0.01)
                if u < 0.25:
                    c = W_RAMP[1] if f < 0.6 else W_RAMP[0]
                elif u < 0.6:
                    c = W_RAMP[2] if f < 0.5 else W_RAMP[1]
                else:
                    c = W_RAMP[3] if f < 0.45 else W_RAMP[2]
                put(a, x, y, c)
    for x in range(tail0 + 2, int(hx) - 2):
        u = (x - tail0) / max(1.0, hx - tail0)
        put(a, x, int(round(cy - (1.5 + 2.2 * u) - 1.2 * math.sin(phase + x * 0.55))), W_ARC)
    for y in range(H):
        for x in range(int(hx - rx) - 1, W):
            e = ((x - hx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if e <= 1.0:
                ei = ((x - (hx + 2)) / (rx * 0.55)) ** 2 + ((y - cy) / (ry * 0.5)) ** 2
                ec = ((x - (hx + 3.5)) / (rx * 0.25)) ** 2 + ((y - cy) / (ry * 0.22)) ** 2
                put(a, x, y, W_RAMP[5] if ec <= 1 else (W_RAMP[4] if ei <= 1 else (W_RAMP[3] if e <= 0.75 else W_RAMP[2])))
    for k in range(3):
        put(a, int(hx - 4 - 5 * k - (phase * 3) % 4), cy - 5 + (k % 2), W_RAMP[4])
    for r in range(cy):
        a[H - 1 - r] = a[r]
    return a, (int(hx), cy)


def q_laser(length, flick):
    """Q's missile as a laser pointing right: a white-pink head, a 1-row magenta-purple beam behind it, glowing a row
    above and below near the head, darkening to the tail; `flick` alternates the glow."""
    H, W = 5, 28
    cy, head = 2, W - 3
    a = np.zeros((H, W, 4), np.uint8)
    tail = max(0, head - length)
    for x in range(tail, head):
        u = (x - tail) / max(1, head - tail)
        put(a, x, cy, Q_RAMP[0] if u < 0.18 else (Q_RAMP[1] if u < 0.5 else (Q_RAMP[2] if u < 0.85 else Q_RAMP[3])))
        if u > (0.45 if flick else 0.55):
            g = Q_RAMP[1] if u < 0.8 else Q_RAMP[2]
            put(a, x, cy - 1, g)
            put(a, x, cy + 1, g)
    for dx, dy, c in ((0, 0, Q_RAMP[4]), (1, 0, Q_RAMP[4]), (-1, 0, Q_RAMP[3]), (0, -1, Q_RAMP[3]), (0, 1, Q_RAMP[3]),
                      (2, 0, Q_RAMP[3])):
        put(a, head + dx, cy + dy, c)
    if flick:
        put(a, head - 2, cy - 2, Q_RAMP[2])
        put(a, head - 2, cy + 2, Q_RAMP[2])
    return a, (head, cy)


def drawn():
    """The two drawn projectile strips (native 8x files for review) and their anchors (the head)."""
    strips = {"q_missile": [q_laser(8, 0), q_laser(16, 1), q_laser(26, 0), q_laser(26, 1)],
              "w_bolt": [w_bullet(0.0, trail=12)] + [w_bullet(p) for p in (0.0, 1.6, 3.2, 4.8)]}
    out = {}
    for name, frames in strips.items():
        cells_ = [f for f, _ in frames]
        out[name] = {"cell": [cells_[0].shape[1], cells_[0].shape[0]], "anchor": list(frames[0][1]),
                     "frames": len(cells_)}
        Image.fromarray(np.repeat(np.repeat(np.concatenate(cells_, 1), Z, 0), Z, 1), "RGBA").save(
            G.lp(os.path.join(SRC, f"kaisa_fx_{name}.png")))
    return out


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"kaisa_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"kaisa_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


PALM3, PALM4 = (19.5, -9), (23.5, -10)     # just past the hand's last pixel: attack frames 3 and 4
CANNON_LOW = (22.5, -6)                    # W's cannon mouth as it charges (frames 3-4)
BLAST = (24.5, -13)                        # W's blast: between the raised cannon (-16) and the bolt (8 px up)
PODS = [(-13, -29), (15, -29)]             # Q frame 3: the tops of the pods' magenta panels
HIT = (0, -8)                              # a hit on the upper body of a 32-44 px unit
OVERHEAD = (0, -33)                        # over a 32-44 px unit's head: the plasma mark
SOLES = (0, 11)                            # the ground under a unit (its soles' row)
TRAIL = (-4, -10)                          # behind her chest while she flies
TICK = 1000 / 60


def flight(lead_ticks, loops=4, ms=60):
    """A projectile: empty while it is inside her, the 4-frame loop, then frame 1 held (repeat: false)."""
    lead = [(None, round(lead_ticks * TICK))] if lead_ticks else []
    return lead + [(k, ms) for k in [0, 1, 2, 3] * loops] + [(0, 3000)]


def seq(frames, ms):
    return list(zip(frames, ms))


def pl(k):
    base = 6 * (k - 1)
    return [("pl_stack", seq([base, base + 1, base + 2, base + 3, base + 4, base + 5], [60, 210, 210, 210, 210, 100]),
             [OVERHEAD])]


FX = {
    "bolt": [("bolt", flight(3), [(0, 0)])],
    # the laser grows out of the pod over two frames, then flickers; the bullet starts a tick later than it leaves
    # her pivot, with a short trail, then loops (repeat: false, the last frame held)
    "q_missile": [("q_missile", seq([0, 1] + [2, 3] * 12 + [2], [33, 33] + [60] * 24 + [3000]), [(0, 0)])],
    "w_bolt": [("w_bolt", [(None, 17)] + seq([0] + [1, 2, 3, 4] * 3 + [1], [33] + [50] * 12 + [3000]), [(0, 0)])],
    "shot": [("shot", seq([0], [57]), [PALM3]), ("shot", seq([1, 2, 3], [40, 50, 60]), [PALM4])],
    "hit": [("hit", seq(range(4), [40, 50, 60, 70]), [HIT])],
    "pl_1": pl(1), "pl_2": pl(2), "pl_3": pl(3), "pl_4": pl(4),
    "p_burst": [("p_burst", seq(range(7), [40, 50, 60, 70, 80, 90, 100]), [HIT])],
    "e_cast": [("e_cast", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES])],
    "e_aura": [("e_aura", seq(list(range(6)) * 2, [83] * 12), [SOLES])],
    "e_invis": [("e_invis", seq(range(5), [100] * 5), [SOLES])],
    "q_cast": [("q_pod", seq(range(5), [50, 60, 70, 80, 90]), PODS)],
    "q_hit": [("q_hit", seq(range(5), [40, 50, 60, 70, 80]), [HIT])],
    "w_charge": [("w_charge", [(None, 170)] + seq(range(5), [42] * 5), [CANNON_LOW])],
    "w_muzzle": [("w_muzzle", seq(range(5), [30, 40, 50, 60, 70]), [BLAST])],
    "w_hit": [("w_hit", seq(range(6), [50, 60, 70, 80, 90, 100]), [HIT])],
    "r_launch": [("r_launch", seq(range(6), [50, 60, 70, 80, 90, 100]), [SOLES])],
    "r_trail": [("r_trail", seq([0, 1, 2, 3] * 2, [40] * 8), [TRAIL])],
    "r_land": [("r_land", seq(range(5), [50, 60, 70, 80, 90]), [SOLES])],
    "r_shield": [("r_shield", seq([0, 1] + list(range(2, 10)) * 2 + [10, 11], [60, 60] + [100] * 16 + [100, 100]),
                  [SOLES])],
    "evolve": [("evolve", seq(range(8), [60, 70, 80, 90, 100, 110, 120, 130]), [SOLES])],
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


def build():
    with open(G.lp(os.path.join(SRC, "kaisa_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    anchors.update(drawn())
    out = {}
    for tag, parts in FX.items():
        out[tag] = []
        for src, frames, spots in parts:
            strip = cells(src, anchors[src]["frames"])
            for k, ms in frames:
                if k is None:
                    out[tag].append((np.zeros((1, 1, 4), np.uint8), ms))
                else:
                    out[tag].append((place(strip[k], anchors[src]["anchor"], spots), ms))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    tags = build()
    w, h = G.write_sheet(os.path.join(MOD, "effects", "league_kaisa_fx"), tags)
    print(f"league/effects/league_kaisa_fx#sheet.png {w}x{h}: " + ", ".join(
        f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
