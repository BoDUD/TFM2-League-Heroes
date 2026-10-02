#!/usr/bin/env python3
"""Caitlyn's run rebuilt from her idle: the idle's upper body on legs drawn after League's run.

    python tools/art/fix_caitlyn_run.py [--check] [--preview DIR]

Codex's run (codex_strips, 2026-10-01) held the rifle level at arm's length like a bayonet charge on wide lunging
strides; League's Caitlyn jogs with the rifle carried as in her idle (the stock at the hip, the barrel up and
forward) on short steps under her body (the user: "这个走路姿势有点问题吧", "有点不自然"). Each frame here is
- the idle's frame (tools/art/fix_caitlyn_skirt.py: the strips' shorter skirt) from the skirt's lining up (rows to 2
  under the pivot: head, hat, hair, rifle, skirt and its dark lining as one block; the lining's thigh tops turned to
  lining, the run's legs come out under it), lowered by League's step: 0, 1, 2, 1, 0, 1, 2, 1 rows (League's pelvis moves 1.7 px at her height,
  run@0 and @467 highest, @233 and @700 lowest);
- two legs in the idle's materials (navy tights, dark brown boots with a light back edge, the gold cuff and toe cap),
  three squares wide like the idle's, after League's run joints projected at game size through the reference camera
  (tools/lol/pose_joints.py: the near leg - her right, on the left of the screen - plants under her in 1-3 while the
  far one kicks its heel up behind and swings through, then they swap in 5-7; 4 and 8 are the landings). League's
  feet move only 3 px fore and aft at this size, so the two legs would hide each other: the swing here is about 1.6x
  League's, the phases and heights its own;
- one outline ring per leg, the far leg first and the near leg's ring laid over it, so the near leg reads in front;
  the hem's outline is left to import_native's COMPLETE.
Writes assets/source/native/caitlyn_run.png (8x, the cells and pivots of caitlyn_cells.json); then run
tools/art/import_native.py --hero caitlyn. --check compares with the file instead of writing it.
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
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from native_refs import Z, layout  # noqa: E402

NAT = os.path.join(ROOT, "assets", "source", "native")
OUT = os.path.join(NAT, "caitlyn_run.png")
HEM = 2                                   # the skirt's lining: the last row of the upper body under the pivot
DY = [0, 1, 2, 1, 0, 1, 2, 1]             # League's step
PAL = {"c": "1D1C34", "f": "D7AE50", "m": "A07335", "i": "4E2D22", "e": "6F4434", "d": "301A28"}
LINING = "23102D"
RING = "100216"
X0 = -8                                   # the legs' grids: columns from -8, rows from 3 to 10

# each frame: (far leg, near leg), rows 3..10, columns from X0; "." empty
LEGS = [
    # 1: the near leg planted under her, the far one bent up behind it
    ([".......ccc......",
      "......ccc.......",
      ".....ccc........",
      "..fmiic.........",
      ".eiii...........",
      ".ef.............",
      "................",
      "................"],
     ["....ccc.........",
      "....ccc.........",
      ".....fmi........",
      ".....mii........",
      ".....mii........",
      ".....mii........",
      ".....eiii.......",
      ".....eeff......."]),
    # 2: planted; the far heel kicked up behind
    ([".......ccc......",
      ".......ccc......",
      "..fmiiccc.......",
      ".eiiii..........",
      ".ef.............",
      "................",
      "................",
      "................"],
     ["....ccc.........",
      "....ccc.........",
      "....ccc.........",
      ".....fmi........",
      ".....mii........",
      ".....mii........",
      ".....eiii.......",
      ".....eeff......."]),
    # 3: lowest; the far knee swings through in front, its foot tucked under
    ([".......ccc......",
      ".......ccc......",
      "........ccc.....",
      ".....fmiicc.....",
      ".....eiiii......",
      "......eff.......",
      "................",
      "................"],
     ["....ccc.........",
      "....ccc.........",
      "....ccc.........",
      "....ccc.........",
      "....fmi.........",
      "....mii.........",
      "....eiii........",
      "....eeff........"]),
    # 4: the far foot lands in front, the near leg pushes off behind
    ([".......ccc......",
      ".......ccc......",
      "........ccc.....",
      "........fmi.....",
      "........mii.....",
      "........mii.....",
      "........eiii....",
      "........eeff...."],
     ["....ccc.........",
      "...ccc..........",
      "...ccc..........",
      "..fmi...........",
      "..mii...........",
      ".mii............",
      ".eii............",
      "eef............."]),
    # 5: the far leg planted, the near one bent up behind
    ([".......ccc......",
      ".......ccc......",
      ".......ccc......",
      "........fmi.....",
      "........mii.....",
      "........mii.....",
      "........eiii....",
      "........eeff...."],
     ["....ccc.........",
      "...ccc..........",
      "..cccc..........",
      ".fmiic..........",
      "eiii............",
      "eff.............",
      "................",
      "................"]),
    # 6: planted; the near heel kicked up behind
    ([".......ccc......",
      ".......ccc......",
      ".......ccc......",
      "........fmi.....",
      "........mii.....",
      "........mii.....",
      "........eiii....",
      "........eeff...."],
     ["....ccc.........",
      "....ccc.........",
      ".fmiiccc........",
      "eiiii...........",
      "eff.............",
      "................",
      "................",
      "................"]),
    # 7: lowest; the near knee swings through, its foot tucked under
    ([".......ccc......",
      ".......ccc......",
      ".......ccc......",
      ".......ccc......",
      ".......fmi......",
      ".......mii......",
      ".......eiii.....",
      ".......eeff....."],
     ["....ccc.........",
      "....ccc.........",
      ".....ccc........",
      "..fmiicc........",
      "..eiiii.........",
      "...eff..........",
      "................",
      "................"]),
    # 8: the near foot lands in front, the far leg pushes off behind it
    ([".......ccc......",
      "......ccc.......",
      "......ccc.......",
      ".....fmi........",
      ".....mii........",
      "....mii.........",
      "....eii.........",
      "...eef.........."],
     ["....ccc.........",
      "....ccc.........",
      ".....ccc........",
      ".....fmi........",
      ".....mii........",
      ".....mii........",
      ".....eiii.......",
      ".....eeff......."]),
]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lp(path):
    return G.lp(path)


def cells_of(path, n, cell):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    cols, _ = layout(n)
    cw, ch = cell
    return [a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw].copy() for k in range(n)]


def leg(grid):
    """{(x, y): rgb} of one leg grid."""
    out = {}
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch != ".":
                out[(X0 + c, 3 + r)] = rgb(PAL[ch])
    return out


def ring(px):
    """The 4-neighbour ring of a leg, plus the corners under its soles."""
    out = set()
    for (x, y) in px:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in px:
                out.add((x + dx, y + dy))
        if (x, y + 1) not in px:
            for dx in (-1, 1):
                if (x + dx, y + 1) not in px and (x + dx, y) not in px:
                    out.add((x + dx, y + 1))
    return out


def frame(body, k, size, pivot):
    """One run frame on its cell: the legs, then the idle's upper body lowered by DY[k]."""
    far, near = (leg(g) for g in LEGS[k])
    out = np.zeros(size + (4,), np.uint8)
    px, py = pivot

    def put(x, y, c):
        if 0 <= py + y < size[0] and 0 <= px + x < size[1]:
            out[py + y, px + x, :3] = c
            out[py + y, px + x, 3] = 255

    for part in (far, near):
        for (x, y) in ring(part):
            put(x, y, rgb(RING))
        for (x, y), c in part.items():
            put(x, y, c)
    for (x, y), c in body.items():
        put(x, y + DY[k], c)
    return out


def build():
    cells = json.load(open(lp(os.path.join(NAT, "caitlyn_cells.json")), encoding="utf-8"))
    cell = tuple(cells["cell"])
    idle = cells_of(os.path.join(NAT, "caitlyn_idle.png"), len(cells["tags"]["idle"]), cell)[0]
    ix, iy = cells["tags"]["idle"][0]["pivot"]
    body = {}
    for y, x in zip(*np.nonzero(idle[..., 3])):
        if y - iy <= HEM:
            c = tuple(int(v) for v in idle[y, x, :3])
            if y - iy == HEM and c == rgb(PAL["c"]):         # the idle's thigh tops in the lining row
                c = rgb(LINING)
            body[(int(x - ix), int(y - iy))] = c
    run = cells["tags"]["run"]
    frames = [frame(body, k, (cell[1], cell[0]), tuple(run[k]["pivot"])) for k in range(len(run))]
    cols, rows = layout(len(frames))
    sheet = np.zeros((rows * cell[1], cols * cell[0], 4), np.uint8)
    for k, f in enumerate(frames):
        sheet[(k // cols) * cell[1]:(k // cols + 1) * cell[1], (k % cols) * cell[0]:(k % cols + 1) * cell[0]] = f
    return np.repeat(np.repeat(sheet, Z, 0), Z, 1), frames, run


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview", help="also write run_fix.png (every frame at 10x) and run_fix.gif (3x) there")
    a = ap.parse_args()
    big, frames, run = build()
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        same = old.shape == big.shape and (old == big).all()
        print("identical" if same else "DIFFERENT", OUT)
        sys.exit(0 if same else 1)
    Image.fromarray(big, "RGBA").save(lp(OUT))
    print(OUT, big.shape[1], "x", big.shape[0])
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        crops = []
        for f, r in zip(frames, run):
            px, py = r["pivot"]
            crops.append(f[py - 32:py + 14, px - 22:px + 26])
        bg = (92, 98, 86, 255)
        tiles = []
        for c in crops:
            t = Image.new("RGBA", (c.shape[1], c.shape[0]), bg)
            t.alpha_composite(Image.fromarray(c, "RGBA"))
            tiles.append(t)
        w, h = tiles[0].size
        strip = Image.new("RGBA", (w * 4, h * 2), bg)
        for k, t in enumerate(tiles):
            strip.paste(t, ((k % 4) * w, (k // 4) * h))
        strip.resize((strip.width * 10, strip.height * 10), Image.NEAREST).save(os.path.join(a.preview, "run_fix.png"))
        gif = [t.resize((w * 4, h * 4), Image.NEAREST).convert("RGB") for t in tiles]
        gif[0].save(os.path.join(a.preview, "run_fix.gif"), save_all=True, append_images=gif[1:],
                    duration=[r["ms"] for r in run], loop=0)


if __name__ == "__main__":
    main()
