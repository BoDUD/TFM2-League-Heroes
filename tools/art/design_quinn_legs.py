#!/usr/bin/env python3
"""Quinn's leg poses from Codex (tools/art/pack_quinn_legs.py) read back on the idle design's grid: only the legs taken,
the idle's own upper body kept square for square (league_volibear's arm poses, design_volibear_poses.py).

    python tools/art/design_quinn_legs.py   # writes assets/source/quinn/hd/legs_<pose>.png (+ _8x), legs.json, legs_review.png

Codex (assets/source/quinn/codex_legs/quinn-legs, 2026-10-19, new-chat-4) drew each pose on the 22 px grid as asked
(the commonest one-colour run is 21 px, regrid reads 22: the figures come back 46-51 squares wide, 41-50 tall). Each
read-back is laid on the idle by the offset whose upper body (rows above HIP + the pose's drop) matches the idle's best;
from there down every square is the pose's legs - the greaves, plates, boots, the tassets and the cape's hem - its colour
snapped to the nearest of the idle's own colours. legs_<pose>.png
is the idle's upper body moved down `drop` rows over those legs; legs.json gives each pose's drop and leg rows.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402
from design_quinn_hd import lp  # noqa: E402
from pack_quinn_legs import HIP, POSES  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn", "codex_legs", "quinn-legs")
OUT = os.path.join(ROOT, "assets", "source", "quinn", "hd")
SIZE = 22.0
SEARCH = 8


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def palette():
    """The idle's own colours (the legs look like hers, and the rig's audit finds no colour outside the idle)."""
    d = load(os.path.join(OUT, "idle.png"))
    return np.array(sorted({tuple(int(v) for v in c) for c in d[d[..., 3] > 0][:, :3]}), int)


def snap(a, pal):
    out = a.copy()
    m = out[..., 3] > 0
    px = out[m][:, :3].astype(int)
    k = np.argmin(((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1), axis=1)
    out[m, :3] = pal[k]
    out[..., 3] = np.where(m, 255, 0)
    return out


def place(r, idle, drop):
    """(dy, dx) putting read-back r's squares on the idle's grid: the upper body (idle rows < HIP, moved down drop) the
    best colour match."""
    H, W = idle.shape[:2]
    up = idle[:HIP]
    m = up[..., 3] > 0
    best = None
    rys, rxs = np.nonzero(r[..., 3] > 0)
    for dy in range(rys.min() - SEARCH, rys.min() + SEARCH + 1):
        for dx in range(rxs.min() - SEARCH, rxs.min() + SEARCH + 1):
            y0, x0 = dy + drop, dx
            if y0 < 0 or x0 < 0 or y0 + HIP > r.shape[0] or x0 + W > r.shape[1]:
                continue
            sub = r[y0:y0 + HIP, x0:x0 + W]
            both = m & (sub[..., 3] > 0)
            miss = (m != (sub[..., 3] > 0)).sum()
            err = np.abs(sub[..., :3].astype(int) - up[..., :3].astype(int))[both].sum() / 60 + miss * 40
            if best is None or err < best[0]:
                best = (err, dy, dx)
    return best[1], best[2]


def main():
    idle = load(os.path.join(OUT, "idle.png"))
    H, W = idle.shape[:2]
    pal = palette()
    meta, tiles = {}, []
    for pose, (drop, _, _) in POSES.items():
        a = load(os.path.join(SRC, f"quinn-legs-{pose}.png"))
        r, _, _ = RG.regrid(a, SIZE)
        r[..., 3] = np.where(r[..., 3] >= 128, 255, 0)
        dy, dx = place(r, idle, drop)
        # the pose on a canvas of the idle's width (+ room either side for a long stride), rows from the idle's top
        PADX = 12
        canvas = np.zeros((H + 2, W + 2 * PADX, 4), np.uint8)
        for y in range(canvas.shape[0]):
            for x in range(canvas.shape[1]):
                ry, rx = dy + y, dx + x - PADX
                if 0 <= ry < r.shape[0] and 0 <= rx < r.shape[1] and r[ry, rx, 3]:
                    canvas[y, x] = r[ry, rx]
        legs = canvas.copy()
        legs[:HIP + drop] = 0
        legs = snap(legs, pal)
        full = legs.copy()
        upper = np.zeros_like(full)
        upper[drop:drop + HIP, PADX:PADX + W] = idle[:HIP]
        m = upper[..., 3] > 0
        full[m] = upper[m]
        # ground closed in between the legs, the tassets and the cape's hem (the idle has none there): the outline's dark
        # (memory gap-check: a slit between legs takes the leggings' dark)
        op = full[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op
        holes[:HIP + drop - 2] = False
        if holes.any():
            ink = (*PD.edge_colour(idle), 255)
            full[holes] = ink
            legs[holes] = ink
            print(pose, "closed", int(holes.sum()), "squares of ground between the legs")
        op = full[..., 3] > 0
        ys = np.nonzero(op.any(1))[0]
        full = full[:ys.max() + 1]
        legs = legs[:ys.max() + 1]
        Image.fromarray(full).save(lp(os.path.join(OUT, f"legs_{pose}.png")))
        Image.fromarray(np.repeat(np.repeat(full, 8, 0), 8, 1)).save(lp(os.path.join(OUT, f"legs_{pose}_8x.png")))
        Image.fromarray(legs).save(lp(os.path.join(OUT, f"legs_{pose}_only.png")))
        meta[pose] = {"drop": drop, "padx": PADX, "hip": HIP + drop, "rows": int(full.shape[0]), "offset": [int(dy), int(dx)]}
        tiles.append((pose, full))
        print(pose, "offset", dy, dx, "->", full.shape[1], "x", full.shape[0])
    with open(lp(os.path.join(OUT, "legs.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)
    z = 6
    Wt = sum(t.shape[1] * z + 12 for _, t in tiles) + W * z + 12
    Ht = max(t.shape[0] for _, t in tiles) * z + 24
    can = Image.new("RGBA", (Wt, Ht), (200, 200, 200, 255))
    dr = ImageDraw.Draw(can)
    x = 6
    for name, t in [("idle", idle)] + tiles:
        big = Image.fromarray(np.repeat(np.repeat(t, z, 0), z, 1))
        can.alpha_composite(big, (x, Ht - big.height - 4))
        dr.text((x, 4), name, fill=(20, 20, 20, 255))
        x += big.width + 12
    can.convert("RGB").save(lp(os.path.join(OUT, "legs_review.png")))


if __name__ == "__main__":
    main()
