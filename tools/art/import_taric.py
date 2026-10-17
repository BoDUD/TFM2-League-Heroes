#!/usr/bin/env python3
"""Import Taric's effects (assets/source/taric/PROMPTS.md, 1-14) as game sheets.

    python tools/art/import_taric.py --raw <Codex's delivery folder>   # once: Codex's strips -> taric_fx_<name>.png
    python tools/art/import_taric.py                                   # the strips -> effect sheets

The body comes from tools/art/export_taric.py and import_native.py. Codex drew the effects at game size: every strip
is 8x8 blocks of a 1x drawing in the cells PROMPTS.md asked for (the beam, the ally's burst and Q's circle in rows of
four), only the pack's colours (starlight, gem violet, R's gold, the heal's mint), no half-transparent pixel. --raw
checks that, reads the cells left to right, top to bottom and writes them as one row (assets/source/taric/
taric_fx_<name>.png, 8x). No scaling (but the beam's length, below), no palette pass and no outline (effects carry
none).
Placement: a point of the cell goes to a spot from the pivot (11 px over the soles), the same point in every frame
(Codex drew each strip registered in its cells):
  - the hits (the basic attack's, Bravado's) on their cell's middle, on the upper body;
  - the pictures round a figure (Bravado's glow, the stun, the heal, the shield, R's flash and glow) with the row
    their figure's space ends on (the heal's first sparks, the shield's foot) on the soles and the cell's middle
    column on the pivot;
  - the ground rings (Q's circle, the ally's Dazzle burst, the link's sigil) with their ellipse's middle 2 px over
    the soles (a ring round the feet);
  - the beam, the picture of a LineRangeProjectile, centred on its rectangle and turned with it (champion-data
    "Cone / fan"): the cell's middle on the rectangle's. Codex drew it for a 62000 line (62 px from Taric to the
    line's end); the sheet stretches it along the line to the kit's length (E_LENGTH, 1 px per 1000, each column
    taken from the nearest drawn one), so it still reaches from Taric to the end;
  - the gem that flies to the ally on its violet stone (the trail behind it);
  - R's call with its cell's bottom middle on the soles (the halo high over the head).
Durations follow the kit (league/champion/league_taric.data_champion): the beam charges in frames 1-8 for the 44
ticks before its hit (apply 45) and bursts in 9-12; the ally's burst starts 2 ticks later (the link's lob) and hits
on the same tick; the stun's stars last its 75 ticks; R's call fills the 150 ticks before the invulnerability, its
frames 9-10 on it.
Writes league/effects/league_taric_fx and league_taric_big (the beam, the rings and R's call, bigger than the rest).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "taric")
MOD = os.path.join(ROOT, "league")
Z = 8
SOLES = 11                              # the soles' row under the pivot
HIT = (0, -7)                           # a hit on the upper body
GROUND = (0, 9)                         # the middle of a ring round a unit's feet
# name: frames and their layout in Codex's strip (columns, rows)
LAYOUT = {"hit": (5, 1), "p_hit": (6, 1), "p_glow": (4, 1), "e_beam": (4, 3), "e_hit": (6, 1), "e_ally": (4, 3),
          "q_cast": (4, 2), "q_heal": (6, 1), "w_bolt": (4, 1), "w_bind": (6, 1), "w_link": (4, 1),
          "r_call": (10, 1), "r_shine": (6, 1), "r_invuln": (4, 1)}
GEM = {(0xF4, 0xEE, 0xFF), (0xC9, 0xB8, 0xFF), (0x9A, 0x7C, 0xF6), (0x6A, 0x4C, 0xE0), (0x45, 0x30, 0x9E)}


def lp(p):
    return G.lp(p)


def blocks(path):
    """The 1x drawing of an 8x strip; exits if a block is not one flat colour or a pixel is half-transparent."""
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    H, W = a.shape[:2]
    if H % Z or W % Z:
        sys.exit(f"{path}: {W}x{H} is not a multiple of {Z}")
    b = a.reshape(H // Z, Z, W // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    if ((out[..., 3] > 0) & (out[..., 3] < 255)).any():
        sys.exit(f"{path}: half-transparent pixels")
    out[out[..., 3] == 0] = 0
    return out


def from_raw(folder):
    """Codex's taric_fx_<name>.png (its cells in LAYOUT) -> assets/source/taric/taric_fx_<name>.png, one row."""
    for name, (c, r) in LAYOUT.items():
        a = blocks(os.path.join(folder, f"taric_fx_{name}.png"))
        ch, cw = a.shape[0] // r, a.shape[1] // c
        if (ch * r, cw * c) != a.shape[:2]:
            sys.exit(f"taric_fx_{name}.png: {a.shape[1]}x{a.shape[0]} is not {c}x{r} equal cells")
        row = np.concatenate([a[k // c * ch:(k // c + 1) * ch, k % c * cw:(k % c + 1) * cw] for k in range(c * r)], 1)
        Image.fromarray(np.repeat(np.repeat(row, Z, 0), Z, 1), "RGBA").save(lp(os.path.join(SRC, f"taric_fx_{name}.png")))
        cols = len(np.unique(row[row[..., 3] > 0][:, :3], axis=0))
        print(f"taric_fx_{name}.png  {c * r} cells of {cw}x{ch}, {cols} colours")


def cells(name):
    a = blocks(os.path.join(SRC, f"taric_fx_{name}.png"))
    c, r = LAYOUT[name]
    w = a.shape[1] // (c * r)
    return [a[:, k * w:(k + 1) * w] for k in range(c * r)]


def rows_of(frames):
    ys = np.nonzero(np.any([f[..., 3] > 0 for f in frames], 0).any(1))[0]
    return ys.min(), ys.max()


def ring_middle(frames):
    """The ellipse's middle row: halfway between the top and bottom rows of the widest rows (at least 80% of the
    widest) of the frames given - the rays or sparks over a ring would lift a box's middle."""
    op = np.any([f[..., 3] > 0 for f in frames], 0)
    xs = [np.nonzero(op[y])[0] for y in range(op.shape[0])]
    w = np.array([x.max() - x.min() + 1 if len(x) else 0 for x in xs])
    wide = np.nonzero(w >= 0.8 * w.max())[0]
    return (wide.min() + wide.max()) / 2.0


def gem_centre(frame):
    m = (frame[..., 3] > 0) & np.array([[tuple(p[:3]) in GEM for p in row] for row in frame])
    ys, xs = np.nonzero(m)
    return int(round(xs.mean())), int(round(ys.mean()))


def spots(name, fr):
    """(cell x, cell y) of the point placed, and where it goes from the pivot."""
    h, w = fr[0].shape[:2]
    mid = (w // 2, h // 2)
    if name in ("hit", "p_hit"):
        return mid, HIT
    if name in ("p_glow", "e_hit", "q_heal", "w_bind", "r_shine", "r_invuln"):
        return (w // 2, FEET_ROW[name]), (0, SOLES)
    if name in ("q_cast", "e_ally", "w_link"):
        return (w // 2, int(round(ring_middle([fr[k] for k in RING_FRAMES[name]])))), GROUND
    if name == "e_beam":
        return mid, (0, 0)
    if name == "w_bolt":
        return gem_centre(fr[0]), (0, 0)
    if name == "r_call":
        return (w // 2, h - 1), (0, SOLES)
    raise KeyError(name)


# the row of each figure picture's cell that stands on the soles: where its figure's space ends (measured on the
# drawings: the heal's first ring of sparks and the shield's foot end there; the glow, the stun and R's pictures,
# drawn a figure 40 tall in 48 rows, 3 rows over the bottom)
FEET_ROW = {"p_glow": 45, "e_hit": 45, "q_heal": 45, "w_bind": 37, "r_shine": 45, "r_invuln": 45}
# frames whose ellipse is whole and bare (no burst, no rays): Q's circle 3 and 8, the ally's burst 1-8, the sigil
RING_FRAMES = {"q_cast": [2, 6], "e_ally": list(range(8)), "w_link": [0, 1, 2, 3]}


def ms_over(total, n):
    """n frame durations summing to total ms."""
    return [round(total * (k + 1) / n) - round(total * k / n) for k in range(n)]


TICK = 1000 / 60.0
E_HIT = 44                             # the beam's hit: apply 45 - 1 ticks after it appears
E_ALLY_HIT = 42                        # the ally's zone: apply 43 - 1, started 2 ticks after the beam
STUN = 75                              # the stun's ticks
R_WAIT = 150                           # R's call to the invulnerability
E_DRAWN = 62000                        # the beam's length in Codex's drawing (64 px with its two end pixels)
E_LENGTH = 80000                       # the beam's `length` in the kit


def stretch_beam(frame):
    """A beam frame drawn for E_DRAWN stretched along the line to E_LENGTH (1 px per 1000): each new column is the
    nearest drawn one, so a few columns repeat and nothing is blended."""
    w = frame.shape[1]
    nw = w + round((E_LENGTH - E_DRAWN) / 1000)
    return frame[:, ((np.arange(nw) + 0.5) * w / nw).astype(int)]

# sprite: {tag: (strip, ms per frame)}
FX = {
    "league_taric_fx": {
        "hit": ("hit", [50] * 5),
        "p_hit": ("p_hit", [50, 60, 60, 60, 60, 60]),
        "p_glow": ("p_glow", [110] * 4),
        "e_hit": ("e_hit", [80] + ms_over(round(STUN * TICK) - 80, 5)),
        "q_heal": ("q_heal", [60] * 6),
        "w_bolt": ("w_bolt", [60] * 4),
        "w_bind": ("w_bind", [60, 70, 80, 80, 70, 70]),
        "w_link": ("w_link", [120] * 4),
        "r_shine": ("r_shine", [60, 70, 70, 80, 80, 80]),
        "r_invuln": ("r_invuln", [110] * 4),
    },
    "league_taric_big": {
        "e_beam": ("e_beam", ms_over(round(E_HIT * TICK), 8) + [50] * 4),
        "e_ally": ("e_ally", ms_over(round(E_ALLY_HIT * TICK), 8) + [50] * 4),
        "q_cast": ("q_cast", [50, 60, 60, 70, 70, 70, 70, 70]),
        "r_call": ("r_call", ms_over(round(R_WAIT * TICK), 8) + [100, 150]),
    },
}


def build():
    sheets = {}
    for sprite, tags in FX.items():
        out = {}
        for tag, (src, ms) in tags.items():
            fr = cells(src)
            if src == "e_beam":
                fr = [stretch_beam(f) for f in fr]
            if len(fr) != len(ms):
                sys.exit(f"{src}: {len(fr)} frames, {len(ms)} durations")
            (ax, ay), (sx, sy) = spots(src, fr)
            out[tag] = [(G.centre_frame(f, sx - ax, sy - ay), m) for f, m in zip(fr, ms)]
        sheets[sprite] = out
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="Codex's delivery folder: rebuild the strips from its PNGs first")
    args = ap.parse_args()
    if args.raw:
        from_raw(args.raw)
    for sprite, tags in build().items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sprite), tags)
        print(f"league/effects/{sprite}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in tags.items()))


if __name__ == "__main__":
    main()
