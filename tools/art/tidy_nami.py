#!/usr/bin/env python3
"""Tidy Codex's strips of Nami and write them to the native strips.

    python tools/art/tidy_nami.py <Codex's delivery folder> [<fix folder>[@tag,tag] ...] [--check]

Nami's design is Codex's game-size drawing of the user's picture with face D and size W (tools/art/design_nami.py):
36x50, 21 colours, the amber #F2B233 only in her eyes, floating 3 rows over the feet line. Codex drew the seven
action strips from it on League's clips (assets/source/nami/MODEL_STRIPS.md; 96x96 cells, every pixel an 8x8
block) and pasted the design's head into every upright frame; the idle strip is the design itself (the pack's
nami_idle.png). The first delivery (nami_animation_pack, 16:04) passed every check but broke the staff in 13 frames
of five strips (the orb split off or missing, loose pieces round her); they went back (nami_strips_fix_pack ->
nami_animation_fix), while Codex's own second pass of the delivery (16:11) mended most of them and lowered R's leap
so that she plants the staff on the ground (its frames 2-3 went back on their own: nami_ult_fix_pack). A later
folder's nami_<tag>.png replaces the earlier one's; "<folder>@attack,skill" takes only those strips from it.
Two fixes on the game pixels:
  - the last frame of attack, skill, skill2, ult and hit is the design's stance (Codex's 16:11 choice): the exact
    design is put there, at the frame's standing point, so every action ends where the idle begins;
  - small pieces that are not
joined to the body (8-neighbour components of at most SPECK squares besides the biggest: a staff drawn as a one-square
diagonal line is joined corner to corner) are removed - Codex's stray squares and the bit of crown floating over her
head in run 5-8. Bigger loose pieces are reported, never removed: R 1 tosses the staff over her head and death 2
flings it from her hand on purpose.
Then each strip is checked - flat blocks, alpha 0 or 255, only the design's colours, the amber only in the head,
nothing under the feet line (the death's lying frames may reach two rows under it) - and the idle, the seven strips
and the cells are written to assets/source/native/. Then run import_native.py --hero nami.
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

SRC = os.path.join(ROOT, "assets", "source", "native")
Z, FEET = 8, 11
TAGS = ["run", "attack", "skill", "skill2", "ult", "hit", "dead"]
STANCE = {"attack", "skill", "skill2", "ult", "hit"}      # their last frame is the design's stance
EYE = (0xF2, 0xB2, 0x33)
FALL = {"dead": 2}                          # rows a frame may reach under the feet line
SPECK = 12                                 # the biggest loose piece removed
N8 = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    if not np.isin(a[..., 3], [0, 255]).all():
        sys.exit(f"{path}: semi-transparent pixels")
    return b[:, 0, :, 0].copy()


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def layout(n):
    return {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)


def pieces(op):
    """Label image and sizes of the 8-neighbour components of op."""
    lab = np.zeros(op.shape, int)
    sizes = [0]
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        k = len(sizes)
        lab[y, x] = k
        stack, n = [(y, x)], 0
        while stack:
            cy, cx = stack.pop()
            n += 1
            for dy, dx in N8:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = k
                    stack.append((ny, nx))
        sizes.append(n)
    return lab, sizes


def loose(cell):
    """Remove the pieces of at most SPECK squares besides the biggest; (squares removed, sizes of bigger loose pieces)."""
    lab, sizes = pieces(cell[..., 3] > 0)
    if len(sizes) <= 2:
        return 0, []
    big = int(np.argmax(sizes))
    gone, kept = 0, []
    for k in range(1, len(sizes)):
        if k == big:
            continue
        if sizes[k] > SPECK:
            kept.append(sizes[k])
            continue
        cell[lab == k] = 0
        gone += sizes[k]
    return gone, kept


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+", help="Codex's delivery, then any fix folders (later ones win; "
                                               "folder@tag,tag takes only those strips)")
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    a = ap.parse_args()
    srcs = []
    for f in a.folders:
        path, _, only = f.partition("@")
        srcs.append((path, set(only.split(",")) if only else None))
    base = srcs[0][0]
    cells = json.load(open(os.path.join(base, "nami_cells.json"), encoding="utf-8"))
    cw, ch = cells["cell"]
    idle = blocks(os.path.join(base, "nami_idle.png"))
    stance = idle[:ch, :cw]                                    # idle frame 1: the design at its standing point
    p0 = cells["tags"]["idle"][0]["pivot"]
    design = np.asarray(Image.open(G.lp(os.path.join(SRC, "nami_native.png"))).convert("RGBA"))[::Z, ::Z]
    pal = {tuple(int(v) for v in p[:3]) for p in design[design[..., 3] > 0]}
    out = {}
    for tag in TAGS:
        src = [f for f, only in srcs if (only is None or tag in only) and os.path.exists(os.path.join(f, f"nami_{tag}.png"))][-1]
        strip = blocks(os.path.join(src, f"nami_{tag}.png"))
        frs = cells["tags"][tag]
        cols = layout(len(frs))
        if strip.shape[:2] != (-(-len(frs) // cols) * ch, cols * cw):
            sys.exit(f"nami_{tag}.png: expected {cols} x {-(-len(frs) // cols)} cells of {cw}x{ch}")
        notes = []
        for i, fr in enumerate(frs):
            cell = strip[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw]
            if tag in STANCE and i == len(frs) - 1:
                dx, dy = fr["pivot"][0] - p0[0], fr["pivot"][1] - p0[1]
                cell[:] = 0
                cell[max(0, dy):ch + min(0, dy), max(0, dx):cw + min(0, dx)] =                     stance[max(0, -dy):ch - max(0, dy), max(0, -dx):cw - max(0, dx)]
            gone, kept = loose(cell)
            op = cell[..., 3] > 0
            new = {tuple(int(v) for v in p[:3]) for p in cell[op]} - pal
            low = int(np.nonzero(op.any(1))[0].max()) - (fr["pivot"][1] + FEET)
            amber = op & (cell[..., :3] == np.array(EYE, np.uint8)).all(-1)
            bad = []
            if new:
                bad.append(f"{len(new)} new colours")
            if low > FALL.get(tag, 0):
                bad.append(f"{low} rows under the feet line")
            if amber.any():
                ys, xs = np.nonzero(amber)
                if ys.max() - ys.min() > 7 or xs.max() - xs.min() > 7:     # both eyes, upright or turned
                    bad.append("amber outside the eyes")
            if bad:
                sys.exit(f"nami_{tag}.png frame {i + 1}: " + ", ".join(bad))
            notes.append(f"{i + 1}{'=stance' if tag in STANCE and i == len(frs) - 1 else ''}{'-' + str(gone) if gone else ''}"
                         f"{' loose ' + str(kept) if kept else ''}")
        out[tag] = strip
        print(f"{tag:7s} from {os.path.basename(os.path.normpath(src))}: " + " ".join(notes))
    if a.check:
        return
    up(idle).save(G.lp(os.path.join(SRC, "nami_idle.png")))
    for tag, strip in out.items():
        up(strip).save(G.lp(os.path.join(SRC, f"nami_{tag}.png")))
    with open(G.lp(os.path.join(SRC, "nami_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(cells, f, indent=1)
    print("wrote nami_idle.png, " + ", ".join(f"nami_{t}.png" for t in out) + ", nami_cells.json")


if __name__ == "__main__":
    main()
