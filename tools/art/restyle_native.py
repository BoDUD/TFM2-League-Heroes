#!/usr/bin/env python3
"""Game strips straight from League's animation, drawn in the hero's own pixel style.

    python tools/lol/native_pose.py assets/source/darius/poses.json --out DIR --alpha --parts
    python tools/art/restyle_native.py assets/source/darius/poses.json --renders DIR

Darius's strips from Codex were assembled square by square and read as cut-outs (the body changed
size between frames, the cape was a red slab), so his frames come from League's model instead.
native_pose.py renders every tag at game size on a transparent background (<hero>_pose_<tag>.png,
8x) with a part map beside it (<hero>_parts_<tag>.png: head, weapon, body). This turns every 8x8
block into one pixel in the design sheet's palette and writes assets/source/native/<hero>_<tag>.png,
the strips import_native.py cuts, plus <hero>_cells.json copied from DIR (the same cells and pivots):
  - colour: each render pixel votes for a colour by part and hue - the weapon on the weapon ramp by
    brightness; on the body crimson (red hue), skin (tan) or steel, each on its ramp, bright steel as
    the trim colour - and a block takes the colour with the most weighted votes. A block is opaque
    when half covered, a weapon block already at 20 of its 64 pixels, so a thin handle stays whole.
  - cleanup: a pixel whose four neighbours share another colour takes theirs (twice).
  - outline: one outline pixel outside the silhouette (a thin limb keeps its colour) and on the body
    along the weapon; the frame then moves up a pixel, so the outline under the soles lies on League's
    sole row and the pivot stays 11.5 px above it.
  - head: League's head goes, and the design sheet's head (the spec's rect, minus the `cut` pixels
    that belong to the body) goes where League's head joint is, as far from the joint as League's
    head starts in the first idle frame, behind the weapon. A head whose crown points back past 60
    degrees (the cells' "tilt": lying on his back) turns a quarter; a bowed head stays upright.
    "turn" in the spec moves that limit, for all tags or per tag with "*" for the rest (Amumu lies
    at 52-64 degrees, while his jumps throw the head back 50-65: {"dead": 50, "*": 180}).
Spec, in the hero's poses.json: "restyle": {"head": {"rect": [x, y, w, h], "cut": [[x, y], ...]},
"outline": "<hex>", "weapon" / "steel" / "cloth" / "skin": [["<hex>", <up to brightness>], ...,
["<hex>"]], "trim": ["<hex>", <from brightness>], "weights": {"<hex>": <vote weight>},
"turn": 60 or {"<tag>": <degrees>, "*": <degrees>}}.
A hero without a weapon, red cloth or skin (Amumu, all bandages) gives every ramp the same colours.
The design sheet is assets/source/native/<hero>_native.png. The renders show Riot's model: keep them
local.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
HEAD, WEAPON, BODY = 0, 1, 2      # the strongest channel of native_pose's part colours: red, green, blue
TURN = 60


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hsv(a):
    """Hue in degrees, saturation and value (0-1) of an RGB array in 0-1."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx


class Palette:
    def __init__(self, spec):
        cols, self.ramps = [], {}
        for name in ("weapon", "steel", "cloth", "skin"):
            for c in spec[name]:
                if c[0] not in cols:
                    cols.append(c[0])
            self.ramps[name] = ([cols.index(c[0]) for c in spec[name]], [c[1] for c in spec[name][:-1]])
        if spec["trim"][0] not in cols:
            cols.append(spec["trim"][0])
        self.trim = (cols.index(spec["trim"][0]), spec["trim"][1])
        self.rgb = np.array([rgb(c) for c in cols], np.uint8)
        self.weight = np.array([spec.get("weights", {}).get(c, 1.0) for c in cols])
        self.outline = rgb(spec["outline"])

    def ramp(self, name, v):
        idx, cuts = self.ramps[name]
        return np.array(idx)[np.searchsorted(cuts, v)]

    def votes(self, px, part):
        """The colour index each render pixel votes for (-1: none)."""
        h, s, v = hsv(px / 255.0)
        out = np.full(v.shape, -1, np.int32)
        w = part == WEAPON
        out[w] = self.ramp("weapon", v[w])
        b = part == BODY
        red = b & ((h < 20) | (h > 330)) & (s > 0.35) & (v > 0.08)
        tan = b & ~red & (h >= 10) & (h <= 50) & (s > 0.25) & (v > 0.22)
        steel = b & ~red & ~tan
        out[red] = self.ramp("cloth", v[red])
        out[tan] = self.ramp("skin", v[tan])
        out[steel] = self.ramp("steel", v[steel])
        out[steel & (v > self.trim[1])] = self.trim[0]
        return out


def per_block(a, w, h):
    """(h*Z, w*Z) -> (h, w, Z*Z): the render pixels of each game pixel."""
    return a.reshape(h, Z, w, Z).transpose(0, 2, 1, 3).reshape(h, w, Z * Z)


def lonely(a, rounds=2):
    """A pixel whose four neighbours share one other colour takes it."""
    for _ in range(rounds):
        c = a[..., :3].astype(np.int64)
        key = np.where(a[..., 3] > 0, (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2], -1)
        p = np.pad(key, 1, constant_values=-2)
        n = [p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]]
        swap = (n[0] == n[1]) & (n[1] == n[2]) & (n[2] == n[3]) & (n[0] >= 0) & (key >= 0) & (key != n[0])
        v = n[0][swap]
        a[swap, 0], a[swap, 1], a[swap, 2] = (v >> 16) & 255, (v >> 8) & 255, v & 255
    return a


def near(m):
    """Pixels with a 4-neighbour in mask m."""
    p = np.pad(m, 1)
    return p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def body(pal, hi, pa, w, h):
    """One frame without its head: (RGBA game pixels, weapon mask, League's head in the 8x render)."""
    op = (hi[..., 3] >= 128) & (pa[..., 3] >= 128)
    part = np.where(op, pa[..., :3].argmax(-1), -1)
    bv, bp = per_block(pal.votes(hi[..., :3], part), w, h), per_block(part, w, h)
    count = np.stack([(bp == k).sum(-1) for k in (HEAD, WEAPON, BODY)], -1)
    main = count.argmax(-1)
    score = np.stack([(bv == k).sum(-1) * pal.weight[k] for k in range(len(pal.rgb))], -1)
    on = ((bp >= 0).mean(-1) >= 0.5) | ((main == WEAPON) & (count[..., WEAPON] >= 20))
    keep = on & (main != HEAD)
    a = np.zeros((h, w, 4), np.uint8)
    a[keep, :3] = pal.rgb[score.argmax(-1)[keep]]
    a[keep, 3] = 255
    a = lonely(a)
    weapon = keep & (main == WEAPON)
    o = a[..., 3] > 0
    ring = ~o & near(o)
    a[ring | (o & ~weapon & near(weapon)), :3] = pal.outline
    a[ring, 3] = 255
    a = np.concatenate([a[1:], np.zeros((1, w, 4), np.uint8)])       # the outline under the soles on the sole row
    weapon = np.concatenate([weapon[1:], np.zeros((1, w), bool)])
    return a, weapon, part == HEAD


def paste_head(a, weapon, head, joint, tilt, turn=TURN):
    """Paste the head grid (list of rows of hex or None) with League's head joint at joint[0] (x, y), given
    as the joint's place inside the upright head: joint = (x, y, jx, jy)."""
    x, y, jx, jy = joint
    g = np.array([[c or "" for c in row] for row in head], dtype=object)
    H, W = g.shape
    if tilt <= -turn:                      # lying on his back: the crown points left, the face up
        g, (jx, jy) = np.rot90(g, 1), (jy, W - jx)
    x0, y0 = int(round(x - jx)), int(round(y - jy))
    for j, row in enumerate(g):
        for i, c in enumerate(row):
            yy, xx = y0 + j, x0 + i
            if c and 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and not weapon[yy, xx]:
                a[yy, xx] = rgb(c) + (255,)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--renders", required=True, help="native_pose.py --alpha --parts output folder")
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    hero, rs = spec["hero"], spec["restyle"]
    pal = Palette(rs)
    cells_path = os.path.join(args.renders, f"{hero}_cells.json")
    with open(cells_path, encoding="utf-8") as f:
        table = json.load(f)
    w, h = table["cell"]
    design = np.asarray(Image.open(G.lp(os.path.join(SRC, f"{hero}_native.png"))).convert("RGBA"))[::Z, ::Z]
    x0, y0, hw, hh = rs["head"]["rect"]
    cut = {tuple(p) for p in rs["head"].get("cut", [])}
    head = [["%02X%02X%02X" % tuple(design[y0 + j, x0 + i, :3])
             if design[y0 + j, x0 + i, 3] and (x0 + i, y0 + j) not in cut else None for i in range(hw)] for j in range(hh)]

    def frames(tag):
        n = len(table["tags"][tag])
        cols, _ = layout(n)
        hi = np.asarray(Image.open(G.lp(os.path.join(args.renders, f"{hero}_pose_{tag}.png"))).convert("RGBA")).astype(np.float32)
        pa = np.asarray(Image.open(G.lp(os.path.join(args.renders, f"{hero}_parts_{tag}.png"))).convert("RGBA")).astype(np.float32)
        for k in range(n):
            sl = (slice(k // cols * h * Z, (k // cols + 1) * h * Z), slice(k % cols * w * Z, (k % cols + 1) * w * Z))
            yield (*body(pal, hi[sl], pa[sl], w, h), table["tags"][tag][k])

    # where the drawn head starts from League's head joint: where League's head starts in the first idle frame
    _, _, league_head, first = next(frames("idle"))
    ys, xs = np.nonzero(league_head)
    jx, jy = first["head"][0] - xs.min() // Z, first["head"][1] - ys.min() // Z
    for tag, rows in table["tags"].items():
        cols, nrows = layout(len(rows))
        sheet = np.zeros((nrows * h, cols * w, 4), np.uint8)
        for k, (a, weapon, _, cell) in enumerate(frames(tag)):
            turn = rs.get("turn", TURN)
            if isinstance(turn, dict):         # per tag, "*" for the rest
                turn = turn.get(tag, turn.get("*", TURN))
            paste_head(a, weapon, head, (cell["head"][0], cell["head"][1], jx, jy), cell.get("tilt", 0), turn)
            sheet[k // cols * h:(k // cols + 1) * h, k % cols * w:(k % cols + 1) * w] = a
        Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, f"{hero}_{tag}.png")))
        colours = len(np.unique(sheet[sheet[..., 3] > 0][:, :3], axis=0))
        print(f"{hero}_{tag}.png  {len(rows)} frames, {colours} colours")
    shutil.copyfile(cells_path, os.path.join(SRC, f"{hero}_cells.json"))
    print(f"head joint {jx:.1f}, {jy:.1f} inside the drawn head; {hero}_cells.json copied")


if __name__ == "__main__":
    main()
