#!/usr/bin/env python3
"""One canvas per frame for a redraw, and back (league_kayle's Codex redraw, assets/source/kayle/MODEL_REDRAW.md).

    python tools/art/native_frames.py split --hero kayle --out DIR [--width 64] [--scale 8]
    python tools/art/native_frames.py join --hero kayle --src DIR [--dry-run] [--out DIR]

The strips in assets/source/native (<hero>_<tag>.png: every game pixel an 8x8 block, the frames in the cells of
<hero>_cells.json read left to right, top to bottom) are too big to redraw whole when the cells are large: Kayle's
are 112x112 game pixels, her 16-frame run a 3584x3584 image. split cuts every frame out on a canvas of its own,
`--width` game pixels wide and as tall as the cell, the frame's pivot (the unit's point, from the cells table) at
the canvas's middle column and at the cell's pivot row, so every canvas lines up with every other: <hero>_<tag>_<NN>.png
(NN from 01) at `--scale` (8: the blocks as they are; 1: one pixel per game pixel), plus <hero>_frames.json (the
canvas, the pivot, the frames of each tag and their durations).

join puts redrawn canvases back into the strips, each at its frame's pivot, so tools/art/import_native.py cuts
them out where the current frames stand (head tracks, lunges, the knock-back of the death stay as they are). A
canvas may come at 1x or at any whole scale: every block is read as one game pixel by the colour most of its
pixels have (a stray pixel at a block's edge does not count), so a redraw whose blocks are a little off still
lands on the grid; a pixel is transparent when its alpha is below 128 or it is pure magenta (#FF00FF). Every
frame of every tag must be there; a missing one stops the join. --dry-run only checks and reports.

split then join gives the strips back byte for byte (checked on league_kayle).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")


def lp(path):
    """Deep files under this workspace pass MAX_PATH on Windows: open them through the \\\\?\\ prefix."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def load_cells(hero):
    with open(lp(os.path.join(SRC, f"{hero}_cells.json")), encoding="utf-8") as f:
        return json.load(f)


def frames_table(cells, width):
    cw, ch = cells["cell"]
    rows = {r["pivot"][1] for t in cells["tags"].values() for r in t}
    if len(rows) != 1:
        raise SystemExit(f"the frames' pivots sit on different rows {sorted(rows)}: one canvas row cannot hold them")
    return {"canvas": [width, ch], "pivot": [width // 2, rows.pop()], "scale": cells["scale"],
            "tags": {t: [{"frame": k + 1, "ms": r["ms"]} for k, r in enumerate(v)] for t, v in cells["tags"].items()}}


def boxes(cells, tag, width):
    """Per frame of a tag: (x0, y0) of its canvas in the strip, in game pixels."""
    cw, ch = cells["cell"]
    cols, _ = layout(len(cells["tags"][tag]))
    out = []
    for k, r in enumerate(cells["tags"][tag]):
        px, py = r["pivot"]
        x0 = (k % cols) * cw + px - width // 2
        if px - width // 2 < 0 or px - width // 2 + width > cw:
            raise SystemExit(f"{tag} frame {k + 1}: a {width}-pixel canvas round its pivot leaves the cell")
        out.append((x0, (k // cols) * ch))
    return out


def blocks_of(img, gw, gh):
    """An RGBA image of a canvas gw x gh game pixels at any whole scale -> gw x gh RGBA, each block read as the
    colour most of its pixels have; transparent where alpha < 128 or pure magenta."""
    a = np.asarray(img.convert("RGBA"))
    s = a.shape[1] // gw
    if a.shape[1] != gw * s or a.shape[0] != gh * s:
        raise SystemExit(f"a canvas must be {gw}x{gh} at a whole scale, not {a.shape[1]}x{a.shape[0]}")
    b = a.reshape(gh, s, gw, s, 4)
    corner = b[:, 0, :, 0, :]                                       # gh x gw: each block's first pixel
    even = (b == corner[:, None, :, None, :]).all(axis=(1, 3, 4))   # blocks of one colour are read straight

    def clear(px):
        return (px[..., 3] < 128) | ((px[..., 0] == 255) & (px[..., 1] == 0) & (px[..., 2] == 255))

    out = np.zeros((gh, gw, 4), np.uint8)
    solid = even & ~clear(corner)
    out[solid, :3] = corner[solid, :3]
    out[solid, 3] = 255
    for y, x in zip(*np.nonzero(~even)):                            # the rest by the colour most pixels have
        px = b[y, :, x, :].reshape(-1, 4)
        gone = clear(px)
        if gone.sum() * 2 >= len(px):
            continue
        keys, counts = np.unique(px[~gone][:, :3], axis=0, return_counts=True)
        out[y, x, :3] = keys[np.argmax(counts)]
        out[y, x, 3] = 255
    return out


def split(hero, out, width, scale):
    cells = load_cells(hero)
    z = cells["scale"]
    os.makedirs(out, exist_ok=True)
    table = frames_table(cells, width)
    gw, gh = table["canvas"]
    n = 0
    for tag in cells["tags"]:
        strip = Image.open(lp(os.path.join(SRC, f"{hero}_{tag}.png"))).convert("RGBA")
        for k, (x0, y0) in enumerate(boxes(cells, tag, width)):
            canvas = strip.crop((x0 * z, y0 * z, (x0 + gw) * z, (y0 + gh) * z))
            if scale != z:
                canvas = canvas.resize((gw * scale, gh * scale), Image.NEAREST)
            canvas.save(os.path.join(out, f"{hero}_{tag}_{k + 1:02d}.png"))
            n += 1
    with open(os.path.join(out, f"{hero}_frames.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(table, f, indent=1)
    print(f"{n} canvases of {gw}x{gh} game pixels (pivot {table['pivot']}) at {scale}x in {out}")


def join(hero, src, dry, out=None):
    out = out or SRC
    cells = load_cells(hero)
    z = cells["scale"]
    cw, ch = cells["cell"]
    table = json.load(open(os.path.join(src, f"{hero}_frames.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(src, f"{hero}_frames.json")) else frames_table(cells, 64)
    gw, gh = table["canvas"]
    missing = [f"{hero}_{t}_{k + 1:02d}.png" for t, v in cells["tags"].items() for k in range(len(v))
               if not os.path.exists(os.path.join(src, f"{hero}_{t}_{k + 1:02d}.png"))]
    if missing:
        raise SystemExit(f"{len(missing)} canvases missing, e.g. {', '.join(missing[:4])}")
    colours = set()
    for tag, rows in cells["tags"].items():
        cols, nrows = layout(len(rows))
        strip = np.zeros((nrows * ch, cols * cw, 4), np.uint8)
        for k, (x0, y0) in enumerate(boxes(cells, tag, gw)):
            g = blocks_of(Image.open(os.path.join(src, f"{hero}_{tag}_{k + 1:02d}.png")), gw, gh)
            strip[y0:y0 + gh, x0:x0 + gw] = g
            colours |= {tuple(c) for c in g[g[..., 3] > 0][:, :3]}
        img = Image.fromarray(strip, "RGBA").resize((cols * cw * z, nrows * ch * z), Image.NEAREST)
        if not dry:
            os.makedirs(lp(out), exist_ok=True)
            img.save(lp(os.path.join(out, f"{hero}_{tag}.png")))
    print(f"{'checked' if dry else 'wrote'} {len(cells['tags'])} strips of {hero}; {len(colours)} colours in all")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split")
    s.add_argument("--hero", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--width", type=int, default=64)
    s.add_argument("--scale", type=int, default=8)
    j = sub.add_parser("join")
    j.add_argument("--hero", required=True)
    j.add_argument("--src", required=True)
    j.add_argument("--dry-run", action="store_true")
    j.add_argument("--out", help="write the strips here instead of assets/source/native")
    a = ap.parse_args()
    if a.cmd == "split":
        split(a.hero, a.out, a.width, a.scale)
    else:
        join(a.hero, a.src, a.dry_run, a.out)


if __name__ == "__main__":
    main()
