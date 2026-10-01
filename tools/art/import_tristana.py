#!/usr/bin/env python3
"""Import Tristana's effects (assets/source/tristana/PROMPTS.md, 1-19) as game sheets.

    python tools/art/import_tristana.py --raw <Codex's delivery folder>   # once: raw PNGs -> native strips
    python tools/art/import_tristana.py                                   # native strips -> effect sheets

The body comes from Codex's strips and tools/art/import_native.py (the death's last frames from
tools/art/fix_tristana_dead.py). Codex delivered image-model drafts (1402-2172 x 724-1774 px, soft alpha, free
colours) in equal cells, several in two or three rows, with every frame's rectangle and a drawing point in
manifest.json (`assets[].frames[].rect`, `attachment_hint_px`); without a manifest --raw finds the frames itself (the
rows split at the widest empty band near each equal division, then the frames in each row). Every frame becomes a cell
of a native strip the way tools/art/import_veigar.py does it: each game pixel the majority colour of the source pixels
it covers, opaque when a third of them are solid (alpha 100 and up), every colour snapped to the pack's 22 (fire,
smoke, iron, brass, the bomb's red lights; the gold is the fire's and the brass's).
One scale per strip, set by the kit (1000 distance units a pixel) and her cannon's bell (11 rows since she was cut
to 34 rows; the sizes on her cannon went down by 0.8 with it): the cannonball 12 px long with its tail (the ball 4),
the charge 10 with its fuse, Buster Shot's ball 16; the muzzle flashes 14 (attack), 11 (E, down and forward) and 24
(R); the hit 14, the stack spark 10, R's hit 24; the bomb on a
unit 13 wide with its fuse (10 was lost on a 35 px body); the explosions 48 (E, its circle 25000), 58 (four stacks)
and 34 (a kill); W's landing 44 (its circle 22000) and R's blast 40 (20000); Rapid Fire's steam burst 13 wide and its
wisp 10 tall; W's reset 12 tall; the stun stars 16 wide.
Anchors: the drafts place a drawing a little differently in each cell, so what must hold still is measured on every
frame - the three projectiles on the iron ball's middle (their dark pixels in the front half of the drawing; the tail
and the fuse trail behind), mirrored top to bottom into exact symmetry (the game turns them to their flight); the bomb
on its body (the rows where its dark iron is at least 40% as wide as at its widest: the fuse and the red lights over it
stay out); the attack's and R's flashes on their left edge's middle (the muzzle), E's on its upper-left point (it
blasts down and forward); the ground pictures on the ground (the middle of their row's drawings and, under it, the
ring's middle: the row of the widest ring's left and right ends - an ellipse is widest across its middle - the same
height over the drawings' foot in every row of the draft). What moves in its cell keeps the move: the hits, the stack
spark, R's hit, W's reset (the rocket's hop) and the stun stars (their orbit) on Codex's point in each cell, the steam
burst and its wisp on their first frame's spark ring and ember, the same spot in every cell.
The bomb gets a 1-px ring round its body, orange in the dark frame and gold in the bright one (a blink with the
light): black iron on Darius's armour showed only its brass band. No other outline.
The second step places every cell by its anchor - the projectiles on their point, the flashes on the muzzle of her
firing frame (attack 3, E 3, R 3: the bells end at (27, 3), (20, 8) and (20, 4) from the pivot; E's fire moves to
(19, 8) with its 4th frame, R's burns out in its 90 ms shot frame, the smoke stays; the projectiles'
`y_offset` lift them near those heights: 2000 / 9000 / 6000, 3-4 px over the bells' middles - larger values lengthened
the flights and cost her 0.7 kills a game), Rapid Fire's burst on the idle's bell (25, 2) as E's strip ends and its
wisp on the bell's top, the hits on the upper body, the bomb and its spark on the chest, the ground pictures 11 px
under the pivot (the soles), the stars over the head, the rocket over her goggles - and times each view by the kit:
the projectiles start empty for the ticks they spend inside her (her pivot to the bell: 5, 5 and 3 ticks at 6000, 4500
and 7000 a tick), then loop, and hold their first frame after 1 s (`repeat: false`, so nothing shows over her body);
the bomb's two frames last 10 ticks, its replay period; the stun stars last the 30-tick stun; the wisp is 1 s, played
every second of Rapid Fire. Writes assets/source/tristana/tristana_fx_<name>.png plus tristana_fx_anchors.json, and
league/effects/league_tristana_fx and league_tristana_big (e_boom, e_boom4, w_land, r_blast).
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
from import_morgana import Frames, load_manifest, rect  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "tristana")
MOD = os.path.join(ROOT, "league")
Z = 8
# her firing frames' muzzles (the bell's end, from the pivot; tools/art/import_native.py's sheet, facing right)
MUZZLE_ATTACK = (27, 3)                # the idle's bell moved with the attack's 3rd and 4th frames (ATTACK_PATH +2, +1)
MUZZLE_E = (20, 8)
MUZZLE_E4 = (19, 8)                    # E's 4th frame: the bell a square back
MUZZLE_R = (20, 4)
# the flashes follow the bell (the user: "枪口的火还是没跟着枪的方向 固定住了"): a caster view stays where it was put
# on her while the sprite moves under it, so each flash's fire is timed to the frames whose bell is where it is drawn
# - the attack's 3rd and 4th frames hold the bell still (130 ms of fire), E's fire moves a square back with its 4th
# frame, R's fire fits its 90 ms shot frame before the recoil throws the cannon over her head; the smoke after it
# stays where it was blown out
BELL = (25, 2)                         # the idle's bell: Rapid Fire's spark ring when E's strip ends, its steam
STEAM = (22, -2)                       # the wisp's ember on the bell's top (it trails the bell in the shots' recoil)
HIT = (0, -8)                          # a hit on the upper body of a 35-41 px hero
CHEST = (0, -8)                        # the bomb and its stack spark
BODY = (0, -6)                         # R's hit on the middle of the body
GROUND = (0, 11)                       # the soles: 11 px under a unit's pivot
OVERHEAD = (0, -30)                    # over a 35-41 px hero's crown (the stun stars)
HER_HEAD = (0, -29)                    # over her goggles (the idle's top row is -22): W's reset
# the pack's colours (PROMPTS.md): fire, smoke, iron, brass, red lights (the gold is the fire's and the brass's)
PAL = np.array([(0xFF, 0xFF, 0xFF), (0xFF, 0xF6, 0xC8), (0xFF, 0xD8, 0x4A), (0xFF, 0x9A, 0x1F), (0xF2, 0x56, 0x1B),
                (0xB8, 0x26, 0x0F), (0x5E, 0x12, 0x08),
                (0xE6, 0xE0, 0xD8), (0xB9, 0xB0, 0xA6), (0x85, 0x7B, 0x72), (0x57, 0x4F, 0x4A), (0x36, 0x30, 0x2D),
                (0x1A, 0x1A, 0x22), (0x34, 0x34, 0x3F), (0x58, 0x58, 0x66), (0x8A, 0x8A, 0x99),
                (0x87, 0x60, 0x2E), (0xC8, 0x99, 0x4E), (0xE6, 0xBF, 0x86),
                (0x82, 0x1D, 0x3F), (0xD1, 0x38, 0x45), (0xFF, 0x6A, 0x6A)], float)

# raw strip -> native: n frames in a grid (columns, rows) of the draft, row by row, size in game px of `measure` ("w"
# the widest drawing, "h" the tallest), anchor (see the docstring): per frame "head", "bomb", "left", "upleft";
# ("ground", ring frame); ("hint",) the manifest's `attachment_hint_px` in every cell (where Codex drew to: the
# drawings keep their own motion); ("fixed", how, k): `how` measured on frame k, the same spot in every cell;
# "mirror" for the projectiles
RAW = {
    "bolt": dict(n=4, grid=(4, 1), size=12, measure="w", anchor="head", mirror=True),
    "e_charge": dict(n=4, grid=(4, 1), size=10, measure="w", anchor="head", mirror=True),
    "r_ball": dict(n=4, grid=(2, 2), size=16, measure="w", anchor="head", mirror=True),
    "shot": dict(n=5, grid=(3, 2), size=14, measure="w", anchor="left"),
    "e_shot": dict(n=4, grid=(4, 1), size=11, measure="w", anchor="upleft"),
    "r_muzzle": dict(n=6, grid=(3, 2), size=24, measure="w", anchor="left"),
    "hit": dict(n=5, grid=(5, 1), size=14, measure="w", anchor=("hint",)),
    "e_stack": dict(n=3, grid=(3, 1), size=10, measure="w", anchor=("hint",)),
    "r_hit": dict(n=6, grid=(3, 2), size=24, measure="w", anchor=("hint",)),
    "e_bomb": dict(n=8, grid=(2, 4), size=13, measure="w", anchor="bomb", rim=((0xFF, 0x9A, 0x1F), (0xFF, 0xD8, 0x4A))),
    "e_boom": dict(n=8, grid=(4, 2), size=48, measure="w", anchor=("ground", 1)),
    "e_boom4": dict(n=9, grid=(3, 3), size=58, measure="w", anchor=("ground", 1)),
    "p_boom": dict(n=6, grid=(3, 2), size=34, measure="w", anchor=("ground", 1)),
    "w_land": dict(n=6, grid=(3, 2), size=44, measure="w", anchor=("ground", 2)),
    "r_blast": dict(n=6, grid=(3, 2), size=40, measure="w", anchor=("ground", 2)),
    "q_cast": dict(n=5, grid=(3, 2), size=13, measure="w", anchor=("fixed", "centre", 0)),
    "q_rapid": dict(n=4, grid=(4, 1), size=10, measure="h", anchor=("fixed", "lowest", 0)),
    "w_ready": dict(n=5, grid=(5, 1), size=12, measure="h", anchor=("hint",)),
    "r_stun": dict(n=4, grid=(4, 1), size=16, measure="w", anchor=("hint",)),
}


def cuts(occ, n, lo, hi):
    """n-1 cut points in [lo, hi): the middle of the widest empty run within 45% of a cell of each equal division."""
    out = []
    for k in range(1, n):
        target = lo + (hi - lo) * k / n
        win = (hi - lo) / n * 0.45
        a, b = int(target - win), int(target + win)
        best, start = None, None
        for x in range(a, b):
            if occ[x] == 0:
                start = x if start is None else start
                if best is None or x - start + 1 > best[0]:
                    best = (x - start + 1, start)
            else:
                start = None
        if best is None:
            sys.exit(f"no empty band between frames near {target:.0f}")
        out.append(best[1] + best[0] // 2)
    return out


def find_frames(solid, cols, rows, n):
    """The first n frame rectangles [x, y, w, h], row by row: rows split first, then the frames in each row."""
    H, W = solid.shape
    ys = [0] + cuts(solid.sum(1), rows, 0, H) + [H]
    rects = []
    for r in range(rows):
        xs = [0] + cuts(solid[ys[r]:ys[r + 1]].sum(0), cols, 0, W) + [W]
        rects += [[xs[c], ys[r], xs[c + 1] - xs[c], ys[r + 1] - ys[r]] for c in range(cols)]
    return rects[:n]


def dark(a):
    """The iron: solid, dark and grey (the smoke's browns and the fire's reds are warmer)."""
    rgb = a[..., :3].astype(int)
    return (a[..., 3] >= 100) & (rgb.max(-1) < 96) & (rgb.max(-1) - rgb.min(-1) < 40)


def anchor_of(how, k, a, solid, rects, fr, ground, hints):
    """(x, y) of the anchor of frame k, in the draft's pixels."""
    x, y, w, h = rects[k]
    if how[0] == "hint":              # Codex's attachment point in the cell (the cell's middle without a manifest)
        hx, hy = hints[k] if hints else (w / 2, h / 2)
        return x + hx, y + hy
    if how[0] == "fixed":             # frame how[2]'s anchor, the same spot in every cell
        j = how[2]
        ax, ay = anchor_of(how[1], j, a, solid, rects, fr, ground, hints)
        return x + ax - rects[j][0], y + ay - rects[j][1]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if how == "head":                 # the iron ball: its dark pixels in the front (right) 55% of the drawing
        d = dark(a[y:y + h, x:x + w])
        d[:, :int(x1 - 0.55 * (x1 - x0))] = False
        dy, dx = np.nonzero(d)
        return x + (dx.min() + dx.max() + 1) / 2, y + (dy.min() + dy.max() + 1) / 2
    if how == "bomb":                 # the bomb's body: the rows where its iron is 40% as wide as at its widest
        d = dark(a[y:y + h, x:x + w])
        rw = d.sum(1)
        rr = np.nonzero(rw >= 0.4 * rw.max())[0]
        cc = np.nonzero(d[rr.min():rr.max() + 1].any(0))[0]
        return x + (cc.min() + cc.max() + 1) / 2, y + (rr.min() + rr.max() + 1) / 2
    if how == "left":                 # the muzzle: the left edge's middle
        return x + x0, y + (y0 + y1) / 2
    if how == "upleft":               # the solid pixels nearest the upper-left corner (x + y smallest)
        v = xs + ys
        m = v <= np.sort(v)[min(20, len(v) - 1)]
        return x + xs[m].mean(), y + ys[m].mean()
    if how == "lowleft":              # the solid pixels nearest the lower-left corner (y - x largest)
        v = ys - xs
        m = v >= np.sort(v)[::-1][min(20, len(v) - 1)]
        return x + xs[m].mean(), y + ys[m].mean() + 1
    if how == "lowest":               # the lowest solid pixels (the ember under the steam)
        m = ys >= y1 - 3
        return x + xs[m].mean(), y + y1
    if how == "box":
        return x + (x0 + x1) / 2, y + (y0 + y1) / 2
    if how == "centre":
        return fr.anchor("centre", k, 0), fr.anchor("centre", k, 1)
    if how[0] == "ground":
        return ground[k]
    raise ValueError(how)


def ground_points(solid, rects, cols, ring):
    """Every frame's ground point: x the middle of its row's drawings, y the ring's middle - the widest ring's left and
    right ends (frame `ring`) lie on it - the same height over the row's foot (the median drawing bottom) in every
    row."""
    boxes = []
    for x, y, w, h in rects:
        ys, xs = np.nonzero(solid[y:y + h, x:x + w])
        boxes.append((x + xs.min(), x + xs.max() + 1, y + ys.min(), y + ys.max() + 1))
    x, y, w, h = rects[ring]
    s = solid[y:y + h, x:x + w]
    ys, xs = np.nonzero(s)
    ends = (xs <= xs.min() + max(2, (xs.max() - xs.min()) // 50)) | (xs >= xs.max() - max(2, (xs.max() - xs.min()) // 50))
    mid = y + ys[ends].mean()
    rows = [list(range(r * cols, (r + 1) * cols)) for r in range(len(rects) // cols)]
    foot = {i: np.median([boxes[j][3] for j in row]) for row in rows for i in row}
    rise = foot[ring] - mid
    cx = {i: np.median([(boxes[j][0] + boxes[j][1]) / 2 - rects[j][0] for j in row]) for row in rows for i in row}
    return {i: (rects[i][0] + cx[i], foot[i] - rise) for i in range(len(rects))}


def rim(cell, colour):
    """A 1-px ring of `colour` round the biggest piece (the bomb and its fuse): black iron on a dark body (Darius's
    armour) showed only its brass band."""
    m = cell[..., 3] > 0
    lab = np.zeros(m.shape, int)
    best, n = None, 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]:
            continue
        n += 1
        todo, size = [(y0, x0)], 0
        lab[y0, x0] = n
        while todo:
            y, x = todo.pop()
            size += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    todo.append((ny, nx))
        if best is None or size > best[0]:
            best = (size, n)
    body = lab == best[1]
    grow = body.copy()
    grow[1:] |= body[:-1]
    grow[:-1] |= body[1:]
    grow[:, 1:] |= body[:, :-1]
    grow[:, :-1] |= body[:, 1:]
    ring = grow & ~m
    out = cell.copy()
    out[ring, :3] = colour
    out[ring, 3] = 255
    return out


def mirror(cell, U):
    """The top half (rows 0..U) mirrored onto the bottom: exact symmetry about the anchor row."""
    out = cell.copy()
    for r in range(U):
        out[2 * U - r] = cell[r]
    return out


def from_raw(folder, only=None):
    manifest = load_manifest(folder)
    path = os.path.join(SRC, "tristana_fx_anchors.json")
    anchors = {}
    if only and os.path.exists(G.lp(path)):
        with open(G.lp(path), encoding="utf-8") as f:
            anchors = json.load(f)
    for name, spec in RAW.items():
        if only and name not in only:
            continue
        fn = f"tristana_fx_{name}.png"
        a = np.asarray(Image.open(G.lp(os.path.join(folder, fn))).convert("RGBA")).copy()
        solid = a[..., 3] >= 100
        cols, rows = spec["grid"]
        if fn in manifest:
            rects = [rect(f) for f in manifest[fn]["frames"]]
            hints = [f.get("attachment_hint_px") for f in manifest[fn]["frames"]]
            hints = hints if all(hints) else None
            if manifest[fn]["layout"]["columns"] != cols:
                sys.exit(f"{fn}: the manifest has {manifest[fn]['layout']['columns']} columns, not {cols}")
        else:
            rects, hints = find_frames(solid, cols, rows, spec["n"]), None
        if len(rects) != spec["n"]:
            sys.exit(f"{fn}: {len(rects)} frames, not {spec['n']}")
        used = list(range(len(rects)))
        fr = Frames(a, solid, rects)
        idx = ((a[..., :3].reshape(-1, 1, 3).astype(float) - PAL[None]) ** 2).sum(2).argmin(1).reshape(a.shape[:2])
        ext = max(fr.extent(spec["measure"], k) for k in used)
        s = spec["size"] / ext
        how = spec["anchor"]
        ground = ground_points(solid, rects, cols, how[1]) if how[0] == "ground" else None
        anc = {k: anchor_of(how, k, a, solid, rects, fr, ground, hints) for k in used}
        L = max(math.ceil(max(max(anc[k][0] - fr.box[k][0], fr.box[k][1] - anc[k][0]) for k in used) * s - 0.5), 0) + 1
        U = max(math.ceil(max(max(anc[k][1] - fr.box[k][2], fr.box[k][3] - anc[k][1]) for k in used) * s - 0.5), 0) + 1
        tw, th = 2 * L + 1, 2 * U + 1
        out = np.zeros((th, tw * len(used), 4), np.uint8)
        for i, k in enumerate(used):
            x, y, w, h = rects[k]
            ax, ay = anc[k]
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
                    out[r, i * tw + c, :3] = PAL[col]
                    out[r, i * tw + c, 3] = 255
            if spec.get("mirror"):
                out[:, i * tw:(i + 1) * tw] = mirror(out[:, i * tw:(i + 1) * tw], U)
            if spec.get("rim"):                 # the blink: the dark frame's ring orange, the bright frame's gold
                out[:, i * tw:(i + 1) * tw] = rim(out[:, i * tw:(i + 1) * tw], spec["rim"][k % 2])
        os.makedirs(G.lp(SRC), exist_ok=True)
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, fn)))
        anchors[name] = {"cell": [tw, th], "anchor": [L, U], "frames": len(used)}
        print(f"{fn}  {len(used)} cells of {tw}x{th}, anchor {L},{U}, scale {s:.4f} ({spec['size']} px over {ext} "
              f"source px), {len(np.unique(out[out[..., 3] > 0][:, :3], axis=0))} colours")
    anchors = {k: anchors[k] for k in RAW if k in anchors}
    text = "{\n" + ",\n".join(f'  "{k}": {json.dumps(v)}' for k, v in anchors.items()) + "\n}\n"
    with open(G.lp(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def cells(name, n):
    a = np.asarray(Image.open(G.lp(os.path.join(SRC, f"tristana_fx_{name}.png"))).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"tristana_fx_{name}.png is not made of flat {Z}x{Z} blocks")
    a = b[:, 0, :, 0].copy()
    w = a.shape[1] // n
    return [a[:, k * w:(k + 1) * w] for k in range(n)]


def flight(lead_ms):
    """A projectile's frames: empty while it crosses her (pivot to the bell), the 4-frame loop for 1 s, then its first
    frame held (repeat: false - the tag must outlast any flight)."""
    return [(None, lead_ms)] + [(k, 60) for k in [0, 1, 2, 3] * 4] + [(0, 3000)]


# sprite: {tag: [(strip, [(frame or None, ms), ...], spot of the anchor from the pivot), ...]}
def seq(frames, ms):
    return list(zip(frames, ms))


STARS = [0, 1, 2, 3]                    # the stun (30 ticks): the loop once, 125 ms a frame
FX = {
    "league_tristana_fx": {
        "bolt": [("bolt", flight(80), (0, 0))],
        "e_charge": [("e_charge", flight(80), (0, 0))],
        "r_ball": [("r_ball", flight(50), (0, 0))],
        "shot": [("shot", seq(range(5), [25, 30, 35, 50, 60]), MUZZLE_ATTACK)],
        "e_shot": [("e_shot", seq([0], [60]), MUZZLE_E), ("e_shot", seq([1, 2, 3], [40, 50, 50]), MUZZLE_E4)],
        "hit": [("hit", seq(range(5), [50] * 5), HIT)],
        "p_boom": [("p_boom", seq(range(6), [50, 60, 70, 80, 90, 100]), GROUND)],
        "e_bomb0": [("e_bomb", seq([0, 1], [84, 84]), CHEST)],
        "e_bomb1": [("e_bomb", seq([2, 3], [84, 84]), CHEST)],
        "e_bomb2": [("e_bomb", seq([4, 5], [84, 84]), CHEST)],
        "e_bomb3": [("e_bomb", seq([6, 7], [84, 84]), CHEST)],
        "e_stack": [("e_stack", seq(range(3), [60] * 3), CHEST)],
        "q_cast": [("q_cast", seq(range(5), [70] * 5), BELL)],
        "q_rapid": [("q_rapid", seq([0, 1, 2, 3] * 2, [125] * 8), STEAM)],
        "w_ready": [("w_ready", seq(range(5), [60, 70, 80, 90, 100]), HER_HEAD)],
        "r_muzzle": [("r_muzzle", seq(range(6), [20, 20, 25, 25, 100, 110]), MUZZLE_R)],
        "r_hit": [("r_hit", seq(range(6), [50, 60, 70, 80, 90, 100]), BODY)],
        "r_stun": [("r_stun", seq(STARS, [125] * 4), OVERHEAD)],
    },
    "league_tristana_big": {
        "e_boom": [("e_boom", seq(range(8), [50, 60, 70, 80, 90, 100, 110, 120]), GROUND)],
        "e_boom4": [("e_boom4", seq(range(9), [50, 60, 70, 80, 90, 100, 110, 120, 130]), GROUND)],
        "w_land": [("w_land", seq(range(6), [60, 70, 80, 90, 100, 110]), GROUND)],
        "r_blast": [("r_blast", seq(range(6), [60, 70, 80, 90, 100, 110]), GROUND)],
    },
}


def build():
    with open(G.lp(os.path.join(SRC, "tristana_fx_anchors.json")), encoding="utf-8") as f:
        anchors = json.load(f)
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, parts in tags.items():
            out[tag] = []
            for src, frames, (sx, sy) in parts:
                ax, ay = anchors[src]["anchor"]
                strip = cells(src, anchors[src]["frames"])
                for k, ms in frames:
                    if k is None:
                        out[tag].append((np.zeros((1, 1, 4), np.uint8), ms))
                    else:
                        out[tag].append((G.centre_frame(strip[k], sx - ax, sy - ay), ms))
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the native strips from its raw PNGs first")
    ap.add_argument("--only", action="append", help="with --raw: only this strip (repeatable)")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw, args.only)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
