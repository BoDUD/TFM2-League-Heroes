#!/usr/bin/env python3
"""Tidy Codex's strips of Akali (v2, "sharp almond eyes") and write them to the native strips.

    python tools/art/tidy_akali.py <Codex's delivery folder> [--review DIR]

Codex's step 2 (akali_strips_v2: the pack of assets/source/akali/MODEL_STRIPS.md, redrawn at the user's request with
a new design - sharp almond eyes, a slimmer body - and all ten actions plus a breathing idle) is clean: exact 8x8
blocks, binary alpha, only the design's 26 colours, nothing under the feet line, one 16x17 head block copied into every
upright frame (the eye white #FFF7E5 and the iris #6A3823 only in it), shut eyes on the hit and the falls. What it
lacks is the outline: the design's silhouette edge is 98% near-black, the action frames' 79-93% - the stretched arms,
the top's shoulders, the hair band and the bandages were drawn without it. So, on the game pixels of every frame:
  - an empty square 4-next to an opaque edge square that is neither near-black nor steel becomes the outline colour
    #11131D (the ring the design draws round its colours, added outside where it is missing, so a two-square arm
    reads like the design's). Steel is left open: the kunai, the kama and its chain are thin lines the base game
    draws without an outline (the archer's bow) - an outline would triple them;
  - nothing else changes: single outline squares stay (the design ends its hair spikes with them).
The design's dark hair and trousers shade #232632 is darker than tools/art/tidy_codex18.py's "black" (luma 40), so its
one_outline would repaint the design's own shading; it is not used. Codex's design (with the same completion) becomes
assets/source/native/akali_native.png (it replaces the user's earlier pick: the new eyes were the user's request), the
strips assets/source/native/akali_<tag>.png, the cells akali_cells.json (the pack's). Then run
tools/art/import_native.py --hero akali (idle: one drawing + BOB, steadied on the iris).
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
NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8
FEET = 11
OUTLINE = (0x11, 0x13, 0x1D)
STEEL = {(0xC9, 0xD5, 0xDD), (0x97, 0xA7, 0xB6), (0x65, 0x71, 0x83), (0x5B, 0x5C, 0x66)}
EYES = {(0xFF, 0xF7, 0xE5), (0x6A, 0x38, 0x23)}
DARK = 70                       # luma under this counts as an outline-dark edge already
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
TAGS = ["idle", "run", "attack", "attack_p", "skill", "skill2", "skill2_dash", "ult", "ult2", "hit", "dead"]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def blocks(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    if not np.isin(a[..., 3], [0, 255]).all():
        sys.exit(f"{path}: semi-transparent pixels")
    return b[:, 0, :, 0].copy()


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def complete(a):
    """Outline added outside the colour edges that have none; returns (frame, squares added). Single outline squares
    are kept: the design ends its hair spikes with them."""
    op = a[..., 3] > 0
    H, W = op.shape
    out = a.copy()
    added = 0
    for y in range(H):
        for x in range(W):
            if op[y, x]:
                continue
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and op[yy, xx]:
                    c = tuple(int(v) for v in a[yy, xx, :3])
                    if luma(c) >= DARK and c not in STEEL:
                        out[y, x] = OUTLINE + (255,)
                        added += 1
                        break
    return out, added


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("--review", help="write a sheet of every frame before/after at 4x here")
    a = ap.parse_args()
    D = a.delivery
    cells = json.load(open(os.path.join(D, "akali_cells.json"), encoding="utf-8"))
    cw, ch = cells["cell"]
    design = np.asarray(Image.open(lp(os.path.join(D, "design", "akali_design_1x.png"))).convert("RGBA"))
    design, n = complete(design)
    up(design).save(lp(os.path.join(NATIVE, "akali_native.png")))
    print(f"design: {n} outline squares added")
    man = json.load(open(os.path.join(D, "manifest.json"), encoding="utf-8"))
    pal = {tuple(int(h[k:k + 2], 16) for k in (1, 3, 5)) for h in man["palette"]}
    review = []
    for tag in TAGS:
        one = blocks(os.path.join(D, f"akali_{tag}.png"))
        cols = one.shape[1] // cw
        fixed = one.copy()
        report = []
        for i, fr in enumerate(cells["tags"][tag]):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            cell = one[y0:y0 + ch, x0:x0 + cw]
            new, n = complete(cell)
            fixed[y0:y0 + ch, x0:x0 + cw] = new
            op = new[..., 3] > 0
            px, py = fr["pivot"]
            below = int(op[py + FEET + 1:].any(axis=1).sum())
            report.append(f"{i + 1}:+{n}" + (f" below {below}" if below else ""))
            review.append((tag, i, cell, new))
            newcols = {tuple(int(v) for v in c) for c in new[op][:, :3]} - pal - {OUTLINE}
            if newcols:
                sys.exit(f"{tag} {i + 1}: colours outside the design's palette {newcols}")
        up(fixed).save(lp(os.path.join(NATIVE, f"akali_{tag}.png")))
        print(f"{tag:12s} " + " ".join(report))
    shutil.copyfile(os.path.join(D, "akali_cells.json"), lp(os.path.join(NATIVE, "akali_cells.json")))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        tiles = []
        for tag, i, before, after in review:
            ys, xs = np.nonzero(after[..., 3] > 0)
            box = (slice(max(0, ys.min() - 1), ys.max() + 2), slice(max(0, xs.min() - 1), xs.max() + 2))
            pair = np.concatenate([before[box], np.zeros((before[box].shape[0], 2, 4), np.uint8), after[box]], 1)
            im = Image.fromarray(pair)
            bg = Image.new("RGBA", im.size, (92, 98, 86, 255))
            bg.alpha_composite(im)
            tiles.append(bg.resize((im.width * 4, im.height * 4), Image.NEAREST))
        cols = 4
        W = max(t.width for t in tiles)
        H = max(t.height for t in tiles)
        sheet = Image.new("RGB", (W * cols, H * ((len(tiles) + cols - 1) // cols)), (30, 30, 30))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % cols) * W, (k // cols) * H))
        sheet.save(os.path.join(a.review, "akali_tidy_review.png"))
        print("review", os.path.join(a.review, "akali_tidy_review.png"), sheet.size)


if __name__ == "__main__":
    main()
