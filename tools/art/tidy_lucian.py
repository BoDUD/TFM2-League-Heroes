#!/usr/bin/env python3
"""Check Codex's strips of Lucian's redesign and write them to the native strips.

    python tools/art/tidy_lucian.py <Codex's delivery folder>

The redesign follows the user's picture: Codex drew the design at game size (assets/source/lucian/MODEL_REDESIGN.md),
Claude regridded and tidied it (near-twin colours merged into 19, the eyes in colours of their own - white #F4F2EA,
iris #3F6A74 - one outline), then Codex drew the ten strips from it (MODEL_REDESIGN_STRIPS.md) on the reference
cells: 96x96 game pixels, every pixel an 8x8 block, the design's head copied into every frame. The face was refined
in the user's Codex session before the strips (thin brows in the hair's browns, a closed mouth of two squares;
codex_model/redesign_strips_face_edit_record.json). The strips are used as delivered; this checks them - flat
blocks, alpha 0 or 255, only the design's colours, both irises in every frame, nothing under the feet line (the
fall may reach two rows under it) - and writes the design, the ten strips and the cells to assets/source/native/.
(The first model's fixes - its run widened, its Q frames re-aimed, its nose flattened - went with it.)
Then run import_native.py --hero lucian (EYES steadies idle and run on the irises).
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
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "native")
Z, CELL = 8, 96
TAGS = ["idle", "run", "attack", "passive", "skill", "skill2", "skill2_back", "ult", "hit", "dead"]
IRIS = (0x3F, 0x6A, 0x74)
FALL = {"dead": 2}             # rows a frame may reach under the feet line


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery", help="Codex's delivery folder (lucian_<tag>.png, lucian_native.png, lucian_cells.json)")
    args = ap.parse_args()
    with open(G.lp(os.path.join(args.delivery, "lucian_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)["tags"]
    design = blocks(os.path.join(args.delivery, "lucian_native.png"))
    palette = colours(design)
    for name in ["native"] + TAGS:
        a = blocks(os.path.join(args.delivery, f"lucian_{name}.png"))
        extra = colours(a) - palette
        if extra:
            sys.exit(f"lucian_{name}.png: colours not in the design: {sorted(extra)}")
        if name != "native":
            frames = cells[name]
            cols = layout(len(frames))
            for k, fr in enumerate(frames):
                cx, cy = (k % cols) * CELL, (k // cols) * CELL
                c = a[cy:cy + CELL, cx:cx + CELL]
                px, py = fr["pivot"]
                low = int(np.nonzero((c[..., 3] > 0).any(1))[0].max()) - (py + 11)
                iris = int(((c[..., :3] == IRIS).all(-1) & (c[..., 3] > 0)).sum())
                if low > FALL.get(name, 0):
                    sys.exit(f"lucian_{name}.png frame {k + 1}: {low} rows under the feet line")
                if iris != 2:
                    sys.exit(f"lucian_{name}.png frame {k + 1}: {iris} iris pixels, not the two eyes")
        shutil.copyfile(G.lp(os.path.join(args.delivery, f"lucian_{name}.png")),
                        G.lp(os.path.join(SRC, f"lucian_{name}.png")))
        print(f"lucian_{name}.png: {len(colours(a))} colours, checked")
    shutil.copyfile(G.lp(os.path.join(args.delivery, "lucian_cells.json")), G.lp(os.path.join(SRC, "lucian_cells.json")))
    print("wrote", len(TAGS) + 1, "images and lucian_cells.json to assets/source/native/")


if __name__ == "__main__":
    main()
