#!/usr/bin/env python3
"""Blitzcrank's action strips: Codex's delivery cleaned up (the user: "codex奇怪的地方请你善后 比如模型哪里少了之类的").

    python tools/art/fix_blitzcrank_strips.py [--check] [--review DIR]

Reads Codex's strips as delivered (assets/source/blitzcrank/codex_strips/blitzcrank_<tag>.png, one pixel per square,
the 128x112 cells of blitzcrank_cells.json) and the approved design (assets/source/native/blitzcrank_native.png,
standing point (64, 88)), and writes assets/source/native/blitzcrank_<tag>.png (8x) for import_native.py. In every
frame whose head is the design's (the pasted dome matches square for square round the eyes, 90% at least):
  1. both smokestacks as the design has them, from the eyes' top-left square: Codex put them back without their side
     outlines and left pieces of its own first stacks beside them - a two-column strip left of the near one, a cap
     stub between the dome and the far one, a brown bar over the dome. The near stack is rows -7..+1, columns
     -9..-3, the far one rows -5..+2, columns +6..+13 (the dome's own squares kept); the air over the dome and
     between it and the far stack is cleared, and the old strip left of the near one (rows -9..+1, columns -13..-10,
     a run at most 3 wide with nothing of the shoulder on its left).
  2. a second chest ring: in the attack (1-5), the hook's pull (3), the uppercut (1-4) and the fall (3-4) Codex left
     the ring's left arc a second time 5-8 squares further left (a "((" on the belly). The real ring is found square
     for square (30 of the design's 32 silver squares at least); every tall piece of ring colours (silver,
     blue-grey, the dark greys - not the outline) in the 11 columns left of it, 6 rows high or more with 4 silver
     squares, is painted over with the belly round it (each square takes the commonest belly colour of its
     neighbours, from the edge in).
The run: Codex moved each leg for the stride as row slices of the design (the hip stays, the foot moves up to six
squares) and every slice carried the hanging fist's inner column along - a dashed ladder down the outer side of each
leg (the swung fists are Codex's own drawing elsewhere). Each leg's slice is found row by row (one height for the
leg, the best column shift per row over the design's row: columns -14..-1 near, +1..+16 far; the foot, rows 7-11,
moves as one piece) and the fist's squares in it (FIST) that still equal the design's are cleared. The near leg (the
design draws it in front: its piston crosses the skirt's edge) is put back over the far one where Codex let the far
foot cover it (the crossing frames 3-5), and the far fist's wrist stub left beside the hip where Codex swung that fist
away (frames 2 and 5-8) and a speck of the near fist (frame 2) are cleared (STUB).
Codex later regenerated the run (HANDOFF_RUN_REGEN.md): its fists stay at the sides, the same leg always leads and the
trailing one is a brown block without a foot, so the first run, cleaned here, keeps the cross-step and the idle's legs.
Last, nothing below the soles' line (row 97 of the cell; the HP bar covers it): the lying body of the death's last two
frames reached 2 rows lower and moves up.
Frames where the raised uppercut arm crosses the stacks' boxes keep the arm (E 5-6 start the far stack lower and keep
the air); the hit's first frame leans back with its stacks tilted and stays as drawn.
--check compares with the files instead of writing them; --review DIR writes blitzcrank_fix.png (every changed frame
before and after, 6x round the head, and the run's legs).
"""
import argparse
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "blitzcrank", "codex_strips")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8
TAGS = ["run", "attack", "skill", "q_pull", "skill2", "ult", "hit", "dead"]
PINK = (0xF3, 0xA4, 0xD9)          # the eyes, a colour nothing else uses
PIVOT = (64, 88)                   # the design's standing point
HEAD = (60, 59, 68, 68)            # the head box on the design (x0, y0, x1, y1)
SURE = 0.9
FEET = 97                          # the soles' bottom row in the cell
NEAR = (-7, 1, -9, -3)             # rows, columns of the near stack from the eyes' top-left square
FAR = (-5, 2, 6, 13)               # the far stack (the dome's squares kept)
AIR = (-7, -5, -1, 8)              # over the dome and between it and the far stack
STRIP = (-9, 1, -13, -10)          # where the old near stack's strip stands
# (tag, frame): {"far0": first row of the far stack put back, "air": False} - the raised uppercut arm stays;
# None: left as Codex drew it (the hit's first frame leans back with its stacks tilted)
OVERRIDE = {("skill2", 4): {"far0": -4, "air": False}, ("skill2", 5): {"far0": -4, "air": False}, ("hit", 0): None}
SILVER = {(0xA2, 0xAE, 0xCC), (0xBF, 0xCD, 0xE0), (0xE2, 0xEB, 0xFC)}
RINGC = SILVER | {(0x67, 0x71, 0x8F), (0x37, 0x3E, 0x56), (0x45, 0x47, 0x59), (0x29, 0x25, 0x36)}
# the run's leg slices: the design's columns per side, and per design row the fist's columns in them (from the
# standing point); the near fist's last knuckle stands on the ground beside the heel (rows 9-11)
SLICE = {"near": (-14, -1), "far": (1, 16)}
FIST = {"near": {1: (-14, -9), 2: (-14, -9), 3: (-14, -9), 4: (-14, -10), 5: (-14, -9), 6: (-14, -9), 7: (-14, -11),
                 8: (-14, -11), 9: (-12, -12), 10: (-12, -12), 11: (-13, -13)},
        "far": {1: (11, 13), 2: (11, 13), 3: (12, 13), 4: (13, 13), 5: (13, 13), 6: (12, 13), 7: (13, 13),
                8: (13, 13)}}
# run frame (0-based): (row, first column, last column) from the standing point, leftovers cleared by hand
STUB = {1: [(-2, 10, 13), (-1, 10, 13), (0, 11, 13), (-1, -15, -15), (0, -16, -15)],
        4: [(-2, 10, 13), (-1, 10, 13), (0, 11, 13)],
        5: [(-2, 10, 13), (-1, 10, 13)],
        6: [(-1, 10, 10), (0, 11, 12)],
        7: [(-2, 10, 13), (-1, 10, 13)]}


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def load(path, z=1):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    if z > 1:
        a = a[z // 2::z, z // 2::z]
    a = a.copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def eyes(a):
    m = (a[..., :3] == PINK).all(-1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(m)
    return (int(ys.min()), int(xs.min())) if len(ys) else None


def pieces(op):
    lab = np.zeros(op.shape, int)
    n = 0
    for y0, x0 in zip(*np.nonzero(op)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        q = deque([(y0, x0)])
        while q:
            y, x = q.popleft()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < op.shape[0] and 0 <= xx < op.shape[1] and op[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        q.append((yy, xx))
    return n


def stacks(f, e, head, near, far, ov):
    """Step 1: the smokestacks as the design has them."""
    ch, cw = f.shape[:2]
    ey, ex = e

    def put(dy, dx, c):
        if 0 <= ey + dy < ch and 0 <= ex + dx < cw:
            f[ey + dy, ex + dx] = c
    r0, r1, c0, c1 = STRIP
    for dy in range(r0, r1 + 1):
        y = ey + dy
        xs = [x for x in range(ex + c0, ex + c1 + 1) if f[y, x, 3]]
        if not xs:
            continue
        run0 = min(xs)
        if max(xs) - run0 + 1 <= 3 and not f[y, run0 - 1, 3] and all(f[y, x, 3] for x in range(run0, max(xs) + 1)):
            for x in xs:
                f[y, x] = 0
    if ov.get("air", True):
        r0, r1, c0, c1 = AIR
        for dy in range(r0, r1 + 1):
            for dx in range(c0, c1 + 1):
                if (dy, dx) not in head and (dy, dx) not in far:
                    put(dy, dx, (0, 0, 0, 0))
    for (dy, dx), c in near.items():
        put(dy, dx, c)
    for (dy, dx), c in far.items():
        if dy >= ov.get("far0", FAR[0]):
            put(dy, dx, c)


def ghost_rings(f, px, py, ring):
    """Step 2: paint over the second ring arc left of the real one. Returns the squares painted."""
    ch, cw = f.shape[:2]
    sil = np.zeros((ch, cw), bool)
    for c in SILVER:
        sil |= (f[..., :3] == c).all(-1) & (f[..., 3] > 0)
    hits, oy, ox = max((sum(1 for dy, dx in ring if sil[py + dy + oy, px + dx + ox]), oy, ox)
                       for oy in range(-6, 7) for ox in range(-4, 5))
    if hits < 30:
        return 0
    rc = np.zeros((ch, cw), bool)
    for c in RINGC:
        rc |= (f[..., :3] == c).all(-1) & (f[..., 3] > 0)
    y0, y1, x0, x1 = py - 15 + oy, py - 1 + oy, px - 15 + ox, px - 4 + ox
    seen, ghost = set(), set()
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            if not rc[yy, xx] or (yy, xx) in seen:
                continue
            q, pts = deque([(yy, xx)]), []
            seen.add((yy, xx))
            while q:
                y, x = q.popleft()
                pts.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        p = (y + dy, x + dx)
                        if y0 <= p[0] <= y1 and x0 <= p[1] <= x1 and rc[p] and p not in seen:
                            seen.add(p)
                            q.append(p)
            ys = [p[0] for p in pts]
            if max(ys) - min(ys) + 1 >= 6 and sum(1 for p in pts if sil[p]) >= 4:
                ghost.update(pts)
    todo, n = set(ghost), len(ghost)
    while todo:
        done = {}
        for y, x in todo:
            near = [tuple(f[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if (dy or dx) and (y + dy, x + dx) not in todo and f[y + dy, x + dx, 3]
                    and tuple(f[y + dy, x + dx, :3]) not in RINGC and int(f[y + dy, x + dx, :3].sum()) > 120]
            if near:
                done[(y, x)] = max(set(near), key=near.count)
        if not done:
            break
        for (y, x), c in done.items():
            f[y, x] = c
        todo -= set(done)
    return n


def run_legs(f, px, py, des, k):
    """The run's fist ladders, the near leg in front, the stubs. Returns a note."""
    note, place = [], {}
    for side, (c0, c1) in SLICE.items():
        rows = {r: [(dx, tuple(des[PIVOT[1] + r, PIVOT[0] + dx])) for dx in range(c0, c1 + 1)
                    if des[PIVOT[1] + r, PIVOT[0] + dx, 3]] for r in range(1, 12)}

        def fit(r, dy):
            return max((sum(1 for dx, c in rows[r] if tuple(f[py + r + dy, px + dx + sx]) == c), -abs(sx), sx)
                       for sx in range(-7, 8))
        dy = max(range(-4, 3), key=lambda d: sum(fit(r, d)[0] for r in rows))
        # the foot (rows 7-11) moves as one piece: the other foot can hide its lower rows
        shifts = [fit(min(r, 8), dy)[2] for r in rows]
        cleared = 0
        for r, (q0, q1) in FIST[side].items():
            if fit(r, dy)[0] < 0.6 * len(rows[r]):
                continue
            for dx in range(q0, q1 + 1):
                y, x = py + r + dy, px + dx + shifts[r - 1]
                if des[PIVOT[1] + r, PIVOT[0] + dx, 3] and tuple(f[y, x]) == tuple(des[PIVOT[1] + r, PIVOT[0] + dx]):
                    f[y, x] = 0
                    cleared += 1
        note.append(f"{side} {dy:+d}/{','.join(f'{v:+d}' for v in shifts)} -{cleared}")
        place[side] = (dy, shifts, rows)
    dy, shifts, rows = place["near"]
    fist = {(r, dx) for r, (q0, q1) in FIST["near"].items() for dx in range(q0, q1 + 1)}
    front = 0
    for r in range(1, 12):
        for dx, c in rows[r]:
            y, x = py + r + dy, px + dx + shifts[r - 1]
            if (r, dx) not in fist and tuple(f[y, x]) != c:
                f[y, x] = c
                front += 1
    stub = 0
    for r, q0, q1 in STUB.get(k, []):
        for x in range(px + q0, px + q1 + 1):
            stub += int(f[py + r, x, 3] > 0)
            f[py + r, x] = 0
    return "; ".join(note) + f"; near leg in front +{front}, stub -{stub}"


def fix(tag, one, table, des, head, near, far, ring, shots):
    cw, ch = table["cell"]
    frs = table["tags"][tag]
    cols, _ = layout(len(frs))
    log = []
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * cw, (i // cols) * ch
        f = one[Y:Y + ch, X:X + cw]
        px, py = fr["pivot"]
        before = f.copy()
        e = eyes(f)
        if e is None or (tag, i) in OVERRIDE and OVERRIDE[(tag, i)] is None:
            note = "kept"
        else:
            ey, ex = e
            ok = sum(1 for (dy, dx), c in head.items()
                     if 0 <= ey + dy < ch and 0 <= ex + dx < cw and tuple(f[ey + dy, ex + dx]) == c)
            if ok < SURE * len(head):
                note = f"head {ok}/{len(head)}, kept"
            else:
                stacks(f, e, head, near, far, OVERRIDE.get((tag, i), {}))
                g = ghost_rings(f, px, py, ring)
                note = "stacks" + (f", ring -{g}" if g else "")
        if tag == "run":
            note += "; " + run_legs(f, px, py, des, i)
        low = int(np.nonzero(f[..., 3])[0].max())
        if low > FEET:
            f[:ch - (low - FEET)] = f[low - FEET:].copy()
            f[ch - (low - FEET):] = 0
            note += f", up {low - FEET}"
        changed = int((before != f).any(-1).sum())
        log.append(f"  {tag} {i + 1}: {changed} px ({note}), {pieces(f[..., 3] > 0)} piece(s)")
        if changed:
            shots.append((f"{tag} {i + 1}", before, f.copy(), e or (py - 30, px)))
    return log


def review(shots, path):
    Zv, H, W, per = 6, 30, 44, 4
    rows = -(-len(shots) // per)
    img = Image.new("RGBA", (per * (2 * W * Zv + 30), rows * (H * Zv + 26)), (150, 170, 120, 255))
    d = ImageDraw.Draw(img)
    for k, (lab, b, f, (ey, ex)) in enumerate(shots):
        X, Y = (k % per) * (2 * W * Zv + 30), (k // per) * (H * Zv + 26)
        for j, src in enumerate((b, f)):
            win = np.zeros((H, W, 4), np.uint8)
            for yy in range(H):
                for xx in range(W):
                    sy, sx = ey - 9 + yy, ex - 20 + xx
                    if 0 <= sy < src.shape[0] and 0 <= sx < src.shape[1]:
                        win[yy, xx] = src[sy, sx]
            img.alpha_composite(Image.fromarray(win).resize((W * Zv, H * Zv), Image.NEAREST),
                                (X + j * (W * Zv + 4), Y + 22))
        d.text((X + 2, Y + 4), lab + "  before | after", fill=(0, 0, 0, 255))
    img.convert("RGB").save(G.lp(path))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with assets/source/native instead of writing")
    ap.add_argument("--review", help="write blitzcrank_fix.png (before and after) to this folder")
    args = ap.parse_args()
    with open(G.lp(os.path.join(NATIVE, "blitzcrank_cells.json")), encoding="utf-8") as fh:
        table = json.load(fh)
    des = load(os.path.join(NATIVE, "blitzcrank_native.png"), Z)
    dey, dex = eyes(des)
    x0, y0, x1, y1 = HEAD
    head = {(y - dey, x - dex): tuple(des[y, x]) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if des[y, x, 3]}

    def box(rows_cols):
        r0, r1, c0, c1 = rows_cols
        return {(dy, dx): tuple(des[dey + dy, dex + dx]) for dy in range(r0, r1 + 1) for dx in range(c0, c1 + 1)
                if (dy, dx) not in head}
    near, far = box(NEAR), box(FAR)
    ring = [(dy, dx) for dy in range(-14, -2) for dx in range(-3, 10)
            if des[PIVOT[1] + dy, PIVOT[0] + dx, 3] and tuple(des[PIVOT[1] + dy, PIVOT[0] + dx, :3]) in SILVER]
    shots, bad = [], 0
    for tag in TAGS:
        one = load(os.path.join(SRC, f"blitzcrank_{tag}.png"))
        print("\n".join(fix(tag, one, table, des, head, near, far, ring, shots)))
        big = np.repeat(np.repeat(one, Z, 0), Z, 1)
        out = os.path.join(NATIVE, f"blitzcrank_{tag}.png")
        if args.check:
            same = os.path.exists(G.lp(out)) and np.array_equal(np.asarray(Image.open(G.lp(out)).convert("RGBA")), big)
            bad += not same
            print(f"assets/source/native/blitzcrank_{tag}.png: {'same' if same else 'DIFFERS'}")
        else:
            Image.fromarray(big).save(G.lp(out))
            print(f"wrote assets/source/native/blitzcrank_{tag}.png {big.shape[1]}x{big.shape[0]}")
    if args.review:
        os.makedirs(G.lp(args.review), exist_ok=True)
        review(shots, os.path.join(args.review, "blitzcrank_fix.png"))
        print(os.path.join(args.review, "blitzcrank_fix.png"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
