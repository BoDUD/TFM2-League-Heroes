#!/usr/bin/env python3
"""LeBlanc's action strips: Codex's step-2 delivery made clean (the user: "有奇怪的地方你再调一下吧 codex太笨了").

    python tools/art/fix_leblanc_strips.py [--check] [--review DIR]

Codex drew the eight strips from the approved 43-row design (assets/source/leblanc/MODEL_STRIPS.md) and pasted the
design's head into every frame (assets/source/leblanc/codex_strips/, as delivered: 8x, its HANDOFF and checks). Its own
checks passed (blocks, palette, alpha, feet line, the head square for square); what they did not see is fixed here:
1. Every frame: pieces cut off from the figure that are mostly outline or sit on the cell's top rows go (the outline
   of Codex's own head left beside the pasted one, a smear on top of the attack's 4th and 5th), then the outline
   squares that outline nothing (no coloured square among their 8 neighbours: a second black ring along the cape's
   edge, tails), repeated - design_leblanc.black_crumbs, the rule the design was cleaned with - and what that cuts
   off up to CRUMB squares.
2. Frame fixes (FIXES below), each a few squares, the rest Codex's. The run is Codex's redo (RUN_REDO.md; its first
   run kept one wide stance - my own leg redraw on it was turned down: "做的不行 让codex帮忙重做吧"), the head's
   surroundings checked clean.
Writes assets/source/native/leblanc_<tag>.png (8x), leblanc_ult.png (Q's: R repeats her last spell with that spell's
own animation) and leblanc_cells.json (the pack's, with ult); then run tools/art/import_native.py --hero leblanc. --check compares with the files instead of writing them.
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
sys.path.insert(0, HERE)
import design_leblanc as D  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "leblanc", "codex_strips")
# strips Codex drew again: the run (RUN_REDO.md - its first run kept one wide stance, "走路没有交叉步 平行走路？")
REDO = {"run": os.path.join(ROOT, "assets", "source", "leblanc", "codex_run_redo")}
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_back", "e", "hit", "dead"]
OUTLINE = D.OUTLINE
SMALL = 15                      # squares: a cut-off piece at most this big that is mostly outline is a leftover
TOP = 2                         # rows: a cut-off piece reaching the cell's top rows is a smear
CRUMB = 12                      # squares: after the outline crumbs, any piece this small left cut off goes too (the
                                # navy bar of Codex's head beside the lying one, a black tail cut from the cape)


def lp(p):
    return D.lp(p)


def load(tag):
    src = REDO.get(tag, SRC)
    a = np.asarray(Image.open(lp(os.path.join(src, f"leblanc_{tag}.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def pieces(op):
    """8-connected pieces of the opaque squares: a label image and the sizes."""
    lab = np.zeros(op.shape, int)
    sizes = {}
    H, W = op.shape
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        n += 1
        stack, k = [(y, x)], 0
        lab[y, x] = n
        while stack:
            cy, cx = stack.pop()
            k += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        stack.append((ny, nx))
        sizes[n] = k
    return lab, sizes


def leftovers(f, any_colour=0):
    """Step 1's cut-off pieces: mostly outline and small, or on the top rows (or, with any_colour, any piece that
    small)."""
    f = f.copy()
    op = f[..., 3] > 0
    if not op.any():
        return f, 0
    lab, sizes = pieces(op)
    body = max(sizes, key=sizes.get)
    dark = op & np.all(f[..., :3] == np.array(OUTLINE), -1)
    gone = 0
    for k, n in sizes.items():
        if k == body:
            continue
        m = lab == k
        if (n <= SMALL and dark[m].mean() >= 0.5) or np.nonzero(m)[0].min() < TOP or n <= any_colour:
            f[m] = 0
            gone += n
    return f, gone


def clean(f):
    f, gone = leftovers(f)
    g = D.black_crumbs(f, np.zeros(f.shape[:2], bool))
    g, more = leftovers(g, CRUMB)
    return g, gone + more, int(((f[..., 3] > 0) & (g[..., 3] == 0)).sum()) - more


# ------------------------------------------------------------------------------------------------ 2 frame fixes
HEAD = os.path.join(ROOT, "assets", "source", "native", "leblanc_native.png")
HEAD_ROWS = (57, 75)            # the design's head: the diadem's tip to the chin (design_leblanc, the strips pack)
HEAD_MAX_COL = 71               # the staff starts at column 72
HALO = 3                        # squares round the head where only the head may be
EARS = 15                       # head rows from the top down to the ear-cuffs' bottom


def design_head():
    d = np.asarray(Image.open(lp(HEAD)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    r0, r1 = HEAD_ROWS
    m = np.zeros(d.shape[:2], bool)
    m[r0:r1 + 1, :HEAD_MAX_COL + 1] = d[r0:r1 + 1, :HEAD_MAX_COL + 1, 3] > 0
    ys, xs = np.nonzero(m)
    y0, x0 = ys.min(), xs.min()
    return d[y0:ys.max() + 1, x0:xs.max() + 1], m[y0:ys.max() + 1, x0:xs.max() + 1]


def head_halo(f, pivot):
    """The run: Codex's own ear-cuffs (gold, 1-2 squares) stayed beside the pasted head in frames 5-8 and flickered
    by the ears as she ran ("走路的时候左右耳会冒出来什么东西"). Round the head (found square for square), from its top
    down to the ear-cuffs, only the head stays within HALO squares of it."""
    g = f.copy()
    head, hm = design_head()
    best = (0, 0, 0)
    for y in range(g.shape[0] - head.shape[0] + 1):
        for x in range(g.shape[1] - head.shape[1] + 1):
            s = (np.all(g[y:y + head.shape[0], x:x + head.shape[1]] == head, -1) & hm).sum()
            if s > best[0]:
                best = (s, x, y)
    s, hx, hy = best
    if s < hm.sum():
        raise ValueError(f"the design's head is not in this frame ({s}/{hm.sum()})")
    m = np.zeros(g.shape[:2], bool)
    m[hy:hy + head.shape[0], hx:hx + head.shape[1]] = hm
    near = np.zeros_like(m)
    for dy in range(-HALO, HALO + 1):
        for dx in range(-HALO, HALO + 1):
            near |= np.roll(np.roll(m, dy, 0), dx, 1)
    near &= ~m
    near[hy + EARS + 1:] = False
    g[near] = 0
    return g


NAVY = (0x13, 0x0F, 0x31)


def attack3_staff(f, pivot):
    """The staff swung over her head runs behind it: its upper half (the crystal) stopped two squares short of the
    hair and floated, its lower end came out three rows under the upper half's line (y = x - 2 in the cell). The upper
    half goes on to the hair (two navy squares and their outline), the lower end moves up onto the line, behind
    whatever is there."""
    g = f.copy()
    for x, y in ((38, 35), (39, 36)):
        g[y, x] = NAVY + (255,)
    for x, y in ((38, 34), (39, 35), (40, 36), (38, 36), (39, 37)):
        if g[y, x, 3] == 0:
            g[y, x] = OUTLINE + (255,)
    end = g[50:57, 55:62].copy()
    g[50:57, 55:62] = 0
    m = end[..., 3] > 0
    reg = g[47:54, 55:62]
    put = m & (reg[..., 3] == 0)
    reg[put] = end[put]
    return g


ARM_X = 33                      # the attack's thrust frames: cut-off pieces wholly left of this column are the stick


def near_arm(f, pivot):
    """The attack's thrust frames drew the near arm swung back as a two-square black stick off her cheek, cut off from
    the body: it goes, the arm hidden behind her as in the frames round them (E's near arm pasted on her shoulder
    stood out as a block beside the face). The staff, cut off from her hand by a corner, stays."""
    g = f.copy()
    lab, sizes = pieces(g[..., 3] > 0)
    body = max(sizes, key=sizes.get)
    for k, n in sizes.items():
        if k != body and n <= 40 and np.nonzero(lab == k)[1].max() < ARM_X:
            g[lab == k] = 0
    return g


FIXES = {("attack", 3): attack3_staff, ("attack", 4): near_arm, ("attack", 5): near_arm}


def run(frames, pivots):
    """The run, Codex's redo (codex_run_redo: a crossing stride, passing in frames 3 and 7, a foot on the line in every
    frame): every frame still loses whatever stands beside the head (head_halo; Codex cleared it this time)."""
    return [head_halo(f, p) for f, p in zip(frames, pivots)]


TAG_FIXES = {"run": run}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    ap.add_argument("--review", help="write before/after sheets to this folder")
    o = ap.parse_args()
    with open(lp(os.path.join(SRC, "leblanc_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    same = True
    for tag in TAGS:
        a = load(tag)
        cols = a.shape[1] // cw
        out = a.copy()
        done = []
        for i in range(len(cells["tags"][tag])):
            r, c = divmod(i, cols)
            f = a[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]
            g, gone, crumbs = clean(f) if tag != "idle" else (f, 0, 0)
            fix = FIXES.get((tag, i + 1))
            if fix:
                g = fix(g, cells["tags"][tag][i]["pivot"])
            done.append(g)
            if gone or crumbs or fix:
                print(f"  {tag:11s} {i + 1}: leftovers -{gone}, outline crumbs -{crumbs}"
                      + (f", {fix.__name__}" if fix else ""))
        if tag in TAG_FIXES:
            done = TAG_FIXES[tag](done, [row["pivot"] for row in cells["tags"][tag]])
            print(f"  {tag:11s} all: {TAG_FIXES[tag].__name__}")
        for i, g in enumerate(done):
            r, c = divmod(i, cols)
            out[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw] = g
        big = np.repeat(np.repeat(out, Z, 0), Z, 1)
        path = os.path.join(OUT, f"leblanc_{tag}.png")
        if o.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            ok = old.shape == big.shape and (old == big).all()
            same &= ok
            print(("same " if ok else "DIFFERENT ") + os.path.basename(path))
        else:
            Image.fromarray(big).save(lp(path))
        if o.review:
            os.makedirs(o.review, exist_ok=True)
            Image.fromarray(np.concatenate([a, np.zeros((4, a.shape[1], 4), np.uint8), out], 0)).resize(
                (a.shape[1] * 4, (a.shape[0] * 2 + 4) * 4), Image.NEAREST).save(os.path.join(o.review, f"{tag}.png"))
    # R repeats her last spell with that spell's own animation: the ult tag is Q's strip
    path = os.path.join(OUT, "leblanc_ult.png")
    spec = dict(cells, tags={**cells["tags"], "ult": cells["tags"]["skill"]})
    if o.check:
        a, b = (np.asarray(Image.open(lp(os.path.join(OUT, f"leblanc_{t}.png")))) for t in ("skill", "ult"))
        with open(lp(os.path.join(OUT, "leblanc_cells.json")), encoding="utf-8") as f:
            ok = a.shape == b.shape and (a == b).all() and json.load(f) == spec
        print(("same " if ok else "DIFFERENT ") + "leblanc_ult.png, leblanc_cells.json")
        sys.exit(0 if same and ok else 1)
    shutil.copyfile(lp(os.path.join(OUT, "leblanc_skill.png")), lp(path))
    with open(lp(os.path.join(OUT, "leblanc_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, indent=1)
    print("written", OUT)


if __name__ == "__main__":
    main()
