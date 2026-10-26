#!/usr/bin/env python3
"""Draven's actions from Codex's whole-frame redraw (assets/source/draven/hd/casts: tools/art/pack_draven_actions.py's
pack, delivered 2026-10-26; the raw generations stay in Codex's outputs folder new-chat-3/outputs/draven-actions/raw),
read onto the design's squares:

1. read back: Codex's export laid every frame on 7-px squares from its own grid origin (export-log/<sheet>-export.txt:
   cell, grid_origin, logical size), each square one design colour, so each cell is read square for square from that
   origin; the standing point is the cell's middle (x 768, or 384 / 1152 in a two-cell sheet), the soles' line y 924;
2. placed on the design's grid: the standing point (the old pivot) on the column the design's shoes put it on (PIV:
   from the frames that stand as the idle does - Spinning Axe's), the soles on the design's soles' row. Skill's last
   frame is the idle pose itself (same_as_design): the design.

Checked frame by frame on delivery (nothing needed mending): every head the design's size (its outline laid over each
head at the headband's gem: crown to chin within a square), the axes where the old frames hold them (attack 4-5 the
far hand empty, E 4-5 and R 5-6 both), the run's feet where the old run puts them (the same stride the user approved
in 2026-10-10's run v4), one piece each.

    python tools/art/casts_draven_hd.py --review DIR      # every tag placed, at 2x
"""
import argparse
import json
import os
import re

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "draven", "hd")
SRC = os.path.join(HD, "casts")
P = 7                           # px a design square in the templates
GROUND_PX = 924                 # the templates' soles' line
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
STANDING = ["skill_1", "skill_2", "skill_3"]   # Spinning Axe: his shoes as the idle's


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


def sheets():
    with open(lp(os.path.join(SRC, "sheets.json")), encoding="utf-8") as f:
        return json.load(f)


def origins(name):
    """[(cell, grid_origin (x, y), logical (w, h))] from export-log/<name>-export.txt."""
    with open(lp(os.path.join(SRC, "export-log", f"{name}-export.txt")), encoding="utf-8-sig") as f:
        txt = f.read()
    out = []
    for m in re.finditer(r"cell=(\d+);.*?grid_origin=(\d+),(\d+);logical=(\d+)x(\d+)", txt):
        c, gx, gy, w, h = (int(v) for v in m.groups())
        out.append((c, (gx, gy), (w, h)))
    return out


def read(a, origin, size, standing_x):
    """The cell's squares from its grid origin -> (squares, the standing point's column, the soles' row + 1)."""
    gx, gy = origin
    w, h = size
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        for i in range(w):
            blk = a[gy + j * P:gy + (j + 1) * P, gx + i * P:gx + (i + 1) * P].reshape(-1, 4)
            u, n = np.unique(blk, axis=0, return_counts=True)
            out[j, i] = u[n.argmax()]
            if out[j, i, 3] < 128:
                out[j, i] = 0
    return out, (standing_x - gx) / P, (GROUND_PX - gy) / P


def read_all():
    """{"<tag>_<frame>": (squares, standing column, soles row + 1)} for every frame Codex drew."""
    out = {}
    for s in sheets()["sheets"]:
        a = np.asarray(Image.open(lp(os.path.join(SRC, s["name"] + ".png"))).convert("RGBA"))
        cells = s["cells"]
        cw = 1536 // cells
        for (c, origin, size), k in zip(sorted(origins(s["name"])), s["frames"]):
            out[f"{s['tag']}_{k}"] = read(a, origin, size, c * cw + cw / 2)
    return out


def shoes_mid(d, low=None):
    """The middle of his two shoes: the outer edges of what stands in the 3 rows over his lowest."""
    op = d[..., 3] > 0
    low = int(np.nonzero(op.any(1))[0].max()) if low is None else low
    xs = np.nonzero(op[low - 3:low + 1].any(0))[0]
    return (xs.min() + xs.max() + 1) / 2.0


D0 = design()
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)} for every frame of the old sheet's
    tags (skill's last frame the design itself)."""
    raw = read_all()
    off = np.median([shoes_mid(raw[n][0]) - raw[n][1] for n in STANDING])
    piv = shoes_mid(D0) - off                       # the design's column under the frames' standing point
    out = {}
    for n, (sq, sc, sr) in raw.items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        out[n] = (pic, int(round(xs.min() - sc + piv)), int(round(ys.min() - sr + GROUND)))
    for tag, ks in sheets().get("same_as_design", {}).items():
        for k in ks:
            out[f"{tag}_{k}"] = (D0, 0, 0)
    return out, piv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr, piv = placed()
    print("frames", len(fr), "standing column on the design", round(piv, 2))
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    for t in TAGS:
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        x0 = min(min(fr[n][1] for n in names), 0) - 2
        x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), D0.shape[1]) + 2
        y0 = min(min(fr[n][2] for n in names), 0) - 2
        y1 = GROUND + 2
        Z, W, Hh = 2, x1 - x0, y1 - y0
        tiles = [("design", (D0, 0, 0))] + [(n, fr[n]) for n in names]
        can = Image.new("RGB", (len(tiles) * (W * Z + 4), Hh * Z), (40, 40, 40))
        for i, (n, (pic, x, y)) in enumerate(tiles):
            tile = Image.new("RGBA", (W, Hh), (150, 165, 150, 255))
            tile.alpha_composite(Image.fromarray(pic), (x - x0, y - y0))
            can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
        can.save(os.path.join(a.review, f"placed_{t}.png"))
    print("written", a.review)


if __name__ == "__main__":
    main()
