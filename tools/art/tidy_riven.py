#!/usr/bin/env python3
"""Check Codex's ten Riven strips, tidy them and write them to the native strips.

    python tools/art/tidy_riven.py <Codex's delivery folder>     # riven_animation_pack/ of the 65-frame delivery

Codex drew the strips from the approved design (assets/source/riven/MODEL_STRIPS.md) on the reference cells
(96x96 game pixels, assets/source/native/riven_cells.json): every game pixel one flat 8x8 block, only the design's
27 colours, alpha 0 or 255, the design's head copied into every frame (two 2x2 eyes on one row), the last frame of
every action the design itself. That is checked here (the script stops on a failure), then two fixes:
  - one outline: the black just inside the outline turned into the material's own darkest shade, outline spurs
    and lone specks off (tools/art/tidy_codex18.py's one_outline, here design_riven.one_outline); the head Codex
    pasted (its manifest's head_origin and rotation, reference/head_master_1x.png) and the ring round it are left
    alone, so every frame keeps the design's head, and frames that are the design itself are not touched;
  - the run floated: its soles stood 3-5 rows over the feet line in all eight frames (League's run, which the
    references showed, plants a foot in four). The whole strip moves down RUN_DROP rows, which puts the soles of
    frames 4 and 7 on the line and keeps the head's one-row bob.
Writes assets/source/native/riven_<tag>.png (8x) and riven_idle.png (the design on the idle pivots, from the pack),
then run import_native.py --hero riven (EYES steadies idle and run on the eyes' green).
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
import design_riven as D  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["run", "attack", "skill", "q2", "q3", "skill2", "ult", "r_slash", "hit", "dead"]
EYES = [(0xFF, 0xFF, 0xFF), (0x16, 0x3A, 0x22), (0x3E, 0x8E, 0x48)]
FALL = {"dead": 2}              # rows a frame may reach under the feet line
RUN_DROP = 3


def blocks(path):
    a = np.asarray(Image.open(D.lp(path)).convert("RGBA"))
    if a.shape[0] % Z or a.shape[1] % Z:
        sys.exit(f"{path}: not a multiple of {Z}")
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    if not np.isin(a[..., 3], [0, 255]).all():
        sys.exit(f"{path}: semi-transparent pixels")
    return b[:, 0, :, 0].copy()


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def colours(a):
    return {tuple(int(v) for v in p) for p in a[a[..., 3] > 0][:, :3]}


def head(shape, master, origin, rotation):
    """The head Codex pasted (its master's opaque squares at the frame's head_origin, turned clockwise by the
    frame's rotation) and the ring round it: left alone, so every frame keeps the design's head square for square."""
    hm = np.rot90(master, k=-(rotation // 90)) if rotation else master
    m = np.zeros(shape, bool)
    x, y = origin
    h, w = hm.shape[:2]
    m[y:y + h, x:x + w] = hm[..., 3] > 0
    grown = m.copy()
    for dy, dx in D.N8:
        grown |= D.shifted(m, dy, dx)
    return grown


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    args = ap.parse_args()
    with open(D.lp(os.path.join(SRC, "riven_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    design = blocks(os.path.join(SRC, "riven_native.png"))
    ys, xs = np.nonzero(design[..., 3] > 0)
    body = design[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    palette = colours(design)
    cw, ch = cells["cell"][:2]
    master = np.asarray(Image.open(D.lp(os.path.join(args.delivery, "reference", "head_master_1x.png"))).convert("RGBA"))
    with open(D.lp(os.path.join(args.delivery, "manifest.json")), encoding="utf-8") as f:
        manifest = {k: [(fr["head_origin"], fr["head_rotation_clockwise"]) for fr in v["frames"]]
                    for k, v in json.load(f)["animations"].items()}
    idle = np.asarray(Image.open(D.lp(os.path.join(args.delivery, "reference", "riven_idle.png"))).convert("RGBA"))
    Image.fromarray(idle).save(D.lp(os.path.join(SRC, "riven_idle.png")))
    for tag in TAGS:
        a = blocks(os.path.join(args.delivery, f"riven_{tag}.png"))
        extra = colours(a) - palette
        if extra:
            sys.exit(f"{tag}: colours not in the design: {sorted(extra)}")
        fr = cells["tags"][tag]
        cols = layout(len(fr))
        out = a.copy()
        changed = []
        for i, f in enumerate(fr):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c = a[y0:y0 + ch, x0:x0 + cw]
            op = c[..., 3] > 0
            ys, xs = np.nonzero(op)
            eyes = sum(int((op & np.all(c[..., :3] == np.array(e, np.uint8), -1)).sum()) for e in EYES[1:])
            if eyes != 6:
                sys.exit(f"{tag} frame {i + 1}: {eyes} eye squares (dark and green), not 6")
            crop = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            if crop.shape == body.shape and (crop == body).all():
                changed.append(0)
                continue
            origin, rotation = manifest[tag][i]
            hm = np.rot90(master, k=-(rotation // 90)) if rotation else master
            x, y = origin
            pasted = c[y:y + hm.shape[0], x:x + hm.shape[1]]
            if pasted.shape != hm.shape or not (pasted[hm[..., 3] > 0] == hm[hm[..., 3] > 0]).all():
                sys.exit(f"{tag} frame {i + 1}: the head is not the design's at {origin}")
            t = D.one_outline(c, head(c.shape[:2], master, origin, rotation))
            changed.append(int(np.any(t != c, -1).sum()))
            if tag == "run":
                t = np.concatenate([np.zeros((RUN_DROP, cw, 4), np.uint8), t[:ch - RUN_DROP]])
            low = int(np.nonzero(t[..., 3] > 0)[0].max()) - (f["pivot"][1] + 11)
            if low > FALL.get(tag, 0):
                sys.exit(f"{tag} frame {i + 1}: {low} rows under the feet line")
            out[y0:y0 + ch, x0:x0 + cw] = t
        big = Image.fromarray(out).resize((out.shape[1] * Z, out.shape[0] * Z), Image.NEAREST)
        big.save(D.lp(os.path.join(SRC, f"riven_{tag}.png")))
        print(f"riven_{tag}.png  {len(fr)} frames, pixels changed per frame {changed}")


if __name__ == "__main__":
    main()
