#!/usr/bin/env python3
"""Import Taliyah's effects (assets/source/taliyah/PROMPTS_FX.md, 14 pictures) as the game sheets league_taliyah_fx and
league_taliyah_big.

    python tools/art/import_taliyah_fx.py [--src DIR] [--review out.png]

The source is the step-3 delivery (assets/source/taliyah/codex_fx/taliyah_fx, Codex 2026-10-24/new-chat-2:
pixel_1x/taliyah_fx_<name>.png, one row of equal frames each at game size, frame sizes in manifest.json "assets"
(cell_1x, frames, symmetry); alpha 0 / 255; the pebble, the threaded rock and the boulder drawn flying right and
symmetric top to bottom, every other one symmetric left to right - checked again here, then made an odd number of
squares across the symmetric way). Each frame is placed as the kit plays it (import_singed_fx.py's way): spots are game
px from the pivot (x forward, y down); a unit's soles are 11 under it, a ground point's too. Anchors: "core" (the
cell's middle), "bottom" (the lowest drawn row of all its frames).
Fixed on import (whole squares only, the symmetry kept):
  - Codex's frames drifted up and down inside their cells (its readback cut each frame from a hand-laid raw row):
    the worked ground's bottom row went 9 -> 7 over its six frames, the minefield's 15 -> 11, the surf dust's 7 -> 4 -
    a ground picture hopping 2-4 rows every loop. Each frame of those is moved so its lowest row sits on SETTLE's.
  - e_mines frames 3 and 4 carried crumbs of the next raw row on their top row (one-square dots, short bars): every
    piece lying on row 0 alone is cleared.
  - e_blast's stun ring (frames 2-4, rows 0-15 of a 24-row cell: Codex put it at a target's chest) is lifted RING_UP
    rows on a taller cell, so it circles a head (31-37 rows over the soles); the burst and its shards stay at the feet.
The lasting pictures are a few frames stretched to their zone's life (tools/kit/build_taliyah.py): the worked ground
q_gt 480 ticks (8 s: cracking open, four lying frames looped, fading), the minefield e_t 240 ticks (the mines falling,
four lying frames looped, crumbling), the wall r_t 300 ticks (rising, four standing frames looped, collapsing); the
stun ring loops while a stun lasts; the buffs (the slow, the surf dust) and the three projectiles loop; the rest play
once.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from import_hwei_fx import anchor, lp, odd  # noqa: E402
from build_taliyah import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "taliyah", "codex_fx", "taliyah_fx")
# the horizontal wall's stretch, drawn later (the user, 2026-10-24: 「大招的墙可以竖着放横着放吧」; Codex new-chat-2)
SRC_WALL = os.path.join(ROOT, "assets", "source", "taliyah", "codex_fx_wall", "taliyah_fx_wall")
MOD = os.path.join(ROOT, "league")

BIG = {"q_ground", "e_mines", "w_erupt", "w_warn", "r_wall", "r_wall_h"}
FLYING = {"a_rock", "q_rock", "q_boulder"}      # turned with their flight: drawn going right, symmetric top to bottom
HIT = (0, -14)                  # a hit on the upper body of a 32-46 px unit
GROUND = (0, 12)                # a picture's lowest row on the ground line
SOLES = (0, 11)                 # on the ground under a unit or a point (the wall's middle row)
LINE = (0, 0)                   # a projectile's point
SETTLE = {"q_ground": 9, "e_mines": 15, "surf": 7}   # each frame's lowest row put here
RING_UP = 18                    # e_blast: the stun ring lifted this many rows (the cell grown as much on top)
RING_ROWS = 16                  # e_blast's rows 0-15 hold the ring in frames 2-4 (frame 1's shards are lower)

seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


def lasting(opening, looped, closing, total):
    """An opening (frames with ms), the looped frames at their ms repeated while the total lasts, a closing: a picture
    stretched to a zone's life (total ms)."""
    head = sum(ms for _, ms in opening) + sum(ms for _, ms in closing)
    per = sum(ms for _, ms in looped)
    n = max(1, round((total - head) / per))
    return opening + looped * n + closing


T = lambda ticks: ticks * 1000 / 60     # noqa: E731

# tag -> (picture, anchor, frames with ms, spots)
FX = {
    # the pebble: flying, its shatter on the upper body
    "a_rock": ("a_rock", "core", loop(4, 60), [LINE]),
    "a_hit": ("a_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    # Threaded Volley: the threaded rocks, their strikes; on Worked Ground the boulder and its smash (dust at the feet)
    "q_rock": ("q_rock", "core", loop(4, 60), [LINE]),
    "q_hit": ("q_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    "q_boulder": ("q_boulder", "core", loop(4, 80), [LINE]),
    "q_big_hit": ("q_big_hit", "bottom", seq(range(4), [60, 80, 100, 120]), [GROUND]),
    # Worked Ground under her: cracking open, lying (frames 1-4 looped), fading - q_gt ticks
    "q_ground": ("q_ground", "bottom", lasting(seq([0], [150]), seq([1, 2, 3, 4], [160] * 4), seq([5], [300]),
                                               T(P["q_gt"])), [GROUND]),
    # Seismic Shove: the eruption, the heave on the thrown; Unraveled Earth: the minefield (falling, lying 2-5 looped,
    # crumbling - e_t ticks), a mine's blast and the stun ring over the head (frames 2-3 looped)
    "w_erupt": ("w_erupt", "bottom", seq(range(5), [70, 90, 110, 130, 150]), [GROUND]),
    # W's warning under the target: the eruption's first frame (its gold crack ring) held until it erupts (w_delay)
    "w_warn": ("w_erupt", "bottom", seq([0], [T(P["w_delay"])]), [GROUND]),
    "w_hit": ("w_hit", "core", seq(range(3), [50, 70, 90]), [HIT]),
    "e_mines": ("e_mines", "bottom", lasting(seq([0, 1], [100, 150]), seq([2, 3, 4, 5], [180] * 4),
                                             seq([6, 7], [250, 250]), T(P["e_t"])), [GROUND]),
    "e_blast": ("e_blast", "bottom", seq([0, 1, 2, 3, 2, 3], [60, 80, 90, 90, 90, 90]), [GROUND]),
    # the slow (the boulder, the mines, the wall) at the feet
    "slow": ("slow", "bottom", loop(4, 110), [GROUND]),
    # Weaver's Wall: rising, standing (frames 2-5 looped), collapsing - r_t ticks; its middle row on the landing point
    "r_wall": ("r_wall", "core", lasting(seq([0, 1], [120, 150]), seq([2, 3, 4, 5], [160] * 4), seq([6, 7], [220, 260]),
                                         T(P["r_t"])), [SOLES]),
    # Weaver's Wall far: a stretch of the horizontal wall where each hidden line stops (r_n of them, r_seg apart), rising,
    # standing (frames 2-5 looped), collapsing - r_t ticks; its feet on the ground line
    "r_wall_h": ("r_wall_h", "bottom", lasting(seq([0, 1], [120, 150]), seq([2, 3, 4, 5], [160] * 4),
                                               seq([6, 7], [220, 260]), T(P["r_t"])), [GROUND]),
    # Rock Surfing: the dust under the boulder while she surfs
    "surf": ("surf", "bottom", loop(4, 90), [GROUND]),
}


def settle(c, row):
    """The frame moved by whole rows so its lowest drawn row is `row`."""
    ys = np.nonzero(c[..., 3].any(1))[0]
    return np.roll(c, row - int(ys.max()), axis=0)


def crumbs_off(c):
    """Pieces lying on row 0 alone cleared (crumbs of the next raw row)."""
    lb, n = ndimage.label(c[..., 3] > 0, structure=np.ones((3, 3)))
    out = c.copy()
    for j in range(1, n + 1):
        ys = np.nonzero((lb == j).any(1))[0]
        if ys.max() == 0:
            out[lb == j] = 0
    return out


def ring_up(cells_):
    """e_blast on a cell RING_UP rows taller: frames 2-4's ring (rows < RING_ROWS) lifted, the rest where it was."""
    out = []
    for k, c in enumerate(cells_):
        h, w = c.shape[:2]
        big = np.zeros((h + RING_UP, w, 4), np.uint8)
        big[RING_UP:] = c
        if k >= 1:
            ring = big[RING_UP:RING_UP + RING_ROWS].copy()
            big[RING_UP:RING_UP + RING_ROWS] = 0
            big[:RING_ROWS] = ring
        out.append(big)
    return out


def cells(name, meta, src):
    a = np.asarray(Image.open(lp(meta["pixel_1x"])).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = meta["cell_1x"]
    if a.shape[1] != w * meta["frames"] or a.shape[0] != h:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {meta['frames']} cells of {w}x{h}")
    out = [a[:h, k * w:(k + 1) * w].copy() for k in range(meta["frames"])]
    for k, c in enumerate(out):
        mirror = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == mirror).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric {'top to bottom' if name in FLYING else 'left to right'}")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    if name == "e_mines":
        out = [crumbs_off(c) for c in out]
    if name in SETTLE:
        out = [settle(c, SETTLE[name]) for c in out]
    if name == "e_blast":
        out = ring_up(out)
    return [odd_(c, name) for c in out]


def odd_(c, name):
    """import_hwei_fx.odd with this hero's projectiles."""
    if name in FLYING:
        n = c.shape[0]
        return c if n % 2 else np.insert(c, n // 2, c[n // 2], axis=0)
    return odd(c, name)


def manifest(*srcs):
    """{name: the manifest's entry, pixel_1x = its strip's path} over the deliveries (a later one adds its pictures)."""
    meta = {}
    for src in srcs:
        man = json.load(open(lp(os.path.join(src, "manifest.json")), encoding="utf-8-sig"))
        for e in man["assets"]:
            f = os.path.basename(e["file"])
            name = e.get("name") or f[:-4].replace("taliyah_fx_", "")
            meta[name] = dict(e, pixel_1x=os.path.join(src, "pixel_1x", f))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC, help="the delivery (the folder holding manifest.json and pixel_1x/)")
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    meta = manifest(a.src, SRC_WALL)
    pics = {v[0] for v in FX.values()}
    if set(meta) != pics:
        sys.exit(f"delivered {sorted(meta)} against the kit's {sorted(pics)}")
    allc = {n: cells(n, meta[n], a.src) for n in pics}
    tables = {"league_taliyah_fx": {}, "league_taliyah_big": {}}
    for tag, (pic, kind, frames, spots) in FX.items():
        cs = allc[pic]
        if len(cs) < 1 + max(k for k, _ in frames):
            sys.exit(f"{tag}: {len(cs)} frames delivered, the timing plays {1 + max(k for k, _ in frames)}")
        anc = anchor(cs, kind)
        out = [(J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["league_taliyah_big" if tag in BIG else "league_taliyah_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        from PIL import ImageDraw
        Z = 6
        rows = []
        for name in sorted(allc):
            cs = allc[name]
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        sheet = Image.new("RGB", (W, sum(r.height + 10 for _, r in rows)), (20, 20, 26))
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(lp(a.review))
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
