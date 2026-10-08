#!/usr/bin/env python3
"""Samira's second design (2026-10-09): the user's own ChatGPT picture cut to game size by whole rows and columns,
league_vladimir's way, written to assets/source/native/samira_native.png.

    python tools/art/design_samira2.py [--check]

Why: the first design (design_samira.py, Codex's draft cut to 40 rows) read as a jumble at game size; the user: 「这莎
弥拉做的也太抽象了」. After my own drafts were turned down (「太丑了」) the user made a picture in ChatGPT
(assets/source/samira/gpt_picture/samira-gpt-1009.png: hands on her hips, the greatsword slanting behind her from the
upper left to the lower right with a red tassel at the pommel, the braid with gold rings at image right, the eyepatch
and its red strap, the green top with the red sash, green trousers, boots with red cuffs) and asked: 「按照做吸血鬼
的方法慢慢调成这样吧」.
Steps:
  1. CUT (tools/art/design_vladimir.py's build_keep, its module settings pointed at this picture): the picture read
     back on its own grid (the skill's regrid.py: 20 px squares) = 53 x 45, every square one of K colours of its own
     (design_varus.kmeans); to ROWS rows: the hair above FACE_ROWS squeezed to CREST rows, FACE_ROWS (the strap, the
     eyepatch, the open eye, the mouth) whole, the rest by design_riven.pick; the columns by design_riven.keep_axis
     with FACE_COLS whole; strips.complete_outline; on the 128 canvas (the soles on row 99, the feet's middle on
     column 64). The user's picks: 39 rows (「39行」), the hair squeezed to 7 rows (「压7行」). No automatic crumb
     clean-up (it painted the gold hair ornaments and holster squares black).
  2. CUT_FIXES: the red tassel's square the cut turned into outline (the ribbon read as two bits), two pinholes.
  3. HEAD (the user: 「头还是有点大」「缩小点」, option A of three): HEAD_DROP rows of the hair deleted inside the head
     (rows HEAD), the head above them sinking back onto the neck - the greatsword's upper part (SWORD: pommel, tassel,
     grip, guard, the blade down to the near shoulder) lifted off first (what it hid of the hair takes the hair's colour
     beside it) and put back where it was, so the blade stays straight.
  4. FACE (「脸型有点奇怪」, option F4 of four): the cut had kept the read-back's forehead rows 8, 10, 11 (3 -> 6 squares
     wide at once) and chin rows 17, 18, 20 (11 -> 5: row 19's taper gone) - the jaw now from read-back row 19 and the
     forehead from row 9 (FACE_ROWS_SWAP; read-back column c sits on canvas column c + FACE_OFF there), and the right
     cheek a column narrower (CHEEK_COL deleted inside the head rows; the braid below moves with it).
  5. POLISH (「精修一下」): the near holster's pistol barrel, cut into a zigzag of single silver squares, drawn back as
     the picture's straight barrel two squares wide (steel and silver, a white top) under the holster.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as dv  # noqa: E402
import design_vladimir as V  # noqa: E402
import rigkit as K  # noqa: E402
import strips  # noqa: E402

PICTURE = os.path.join(ROOT, "assets", "source", "samira", "gpt_picture", "samira-gpt-1009.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "samira_native.png")
ROWS, CREST, K_COLOURS = 38, 7, 26        # rows passed to the cut (39 with the outline); hair rows; colours
FACE_ROWS = range(12, 18)                 # on the read-back: the strap, the eyepatch, the open eye, the mouth
FACE_COLS = range(19, 31)                 # the strap's cheek end, the patch, the open eye, the temple
Z = 8
INK = (5, 2, 6)
TASSEL = (147, 2, 34)
NAVY = (16, 22, 36)
# step 2, (x, y) on the 128 canvas: colour
CUT_FIXES = {(46, 66): TASSEL, (45, 66): INK,    # the tassel's link between the pommel and its hanging end
             (65, 77): INK, (68, 78): NAVY}      # pinholes: under the chin, on the far shoulder
# step 3
HEAD = range(61, 77)                      # the hair's top .. the chin's outline row; the collar starts on row 77
HEAD_DROP = [62, 65]                      # hair rows deleted (the least change from the next row)
SWORD = [(46, 64), (47, 64), (46, 65), (47, 65), (48, 65), (46, 66), (47, 66), (48, 66), (45, 67), (46, 67), (47, 67),
         (48, 67), (45, 68), (49, 68), (49, 69), (51, 69), (50, 70), (51, 70), (49, 71), (50, 71), (49, 72), (50, 72),
         (51, 72), (50, 73), (51, 73), (50, 74), (51, 74), (52, 74), (51, 75), (52, 75), (53, 75), (52, 76), (53, 76),
         (54, 76), (55, 76), (52, 77), (53, 77), (54, 77), (53, 78)]
# step 4
FACE_OFF = 38                             # read-back column + 38 = canvas column (read-back columns 16-30)
FACE_ROWS_SWAP = {75: (19, 18, 30),       # canvas row: (read-back row, first and last read-back column)
                  66: (9, 18, 30)}
CHEEK_COL = 67                            # the right cheek's column, deleted inside the head rows
BRAID_ROWS = range(77, 86)                # the braid below the head: its squares at columns >= 72 move with it
# step 5: (x, y): colour - the barrel at columns 53-54, rows 88-92 (white top, then steel | silver)
STEEL, SILVER, WHITE = (126, 128, 134), (176, 178, 187), (230, 229, 224)
POLISH = {(53, 88): WHITE, (54, 88): WHITE,
          **{(53, y): STEEL for y in range(89, 93)}, **{(54, y): SILVER for y in range(89, 93)},
          **{(52, y): INK for y in range(88, 93)}, (55, 91): INK, (55, 92): INK, (53, 93): INK, (54, 93): INK}


def cut():
    V.RAW, V.FACE_ROWS, V.FACE_COLS, V.K = PICTURE, FACE_ROWS, FACE_COLS, K_COLOURS
    a = V.build_keep(ROWS, clean=False, crest=CREST)
    for (x, y), c in CUT_FIXES.items():
        a[y, x, :3] = c
        a[y, x, 3] = 255
    return a


def finish(a):
    a, _, _ = strips.complete_outline(a, color=INK, feet=99, keep=np.zeros(a.shape[:2], bool))
    while True:
        gone = K.orphan_outline(a, INK)
        if not gone.any():
            return a
        a[gone] = 0


def is_ink(p):
    return p[3] and tuple(int(v) for v in p[:3]) == INK


def shrink_head(a):
    """Step 3."""
    m = np.zeros(a.shape[:2], bool)
    for x, y in SWORD:
        m[y, x] = True
    sword = np.zeros_like(a)
    sword[m] = a[m]
    head = a.copy()
    head[m] = 0
    for x, y in SWORD:                    # what the sword hid of the hair: the hair's colour beside it
        if y in HEAD:
            for dx in (1, 2, 3):
                q = head[y, x + dx]
                if q[3] and not is_ink(q):
                    head[y, x] = q
                    break
    keep = [y for y in HEAD if y not in HEAD_DROP]
    block = head[keep].copy()
    head[HEAD.start:HEAD.stop] = 0
    head[HEAD.stop - len(keep):HEAD.stop] = block
    head[m] = sword[m]
    return finish(head)


def face(a, rb):
    """Step 4: the swapped rows in the cut's own K colours (design_varus.kmeans of the read-back, as step 1)."""
    idx, pal = dv.kmeans(rb, K_COLOURS)
    for y, (src, c0, c1) in FACE_ROWS_SWAP.items():     # the jaw first, then the forehead, each outlined
        for c in range(c0, c1 + 1):
            if idx[src, c] >= 0:
                a[y, c + FACE_OFF, :3] = pal[idx[src, c]]
                a[y, c + FACE_OFF, 3] = 255
            else:
                a[y, c + FACE_OFF] = 0
        a = finish(a)
    b = a.copy()
    for y in HEAD:
        b[y, CHEEK_COL:127] = a[y, CHEEK_COL + 1:128]
        b[y, 127] = 0
    for y in BRAID_ROWS:
        for x in range(CHEEK_COL, 127):
            if x + 1 >= 72 and a[y, x + 1, 3]:
                b[y, x] = a[y, x + 1]
                b[y, x + 1] = 0
    return finish(b)


def polish(a):
    """Step 5."""
    for (x, y), c in POLISH.items():
        a[y, x, :3] = c
        a[y, x, 3] = 255
    return finish(a)


def build():
    a = cut()
    a = shrink_head(a)
    a = face(a, V.read_back())
    return polish(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    a = build()
    big = np.repeat(np.repeat(a, Z, 0), Z, 1)
    if args.check:
        cur = np.asarray(Image.open(V.lp(OUT)).convert("RGBA"))
        same = np.array_equal(cur, big)
        print("samira_native.png", "matches" if same else "DIFFERS")
        sys.exit(0 if same else 1)
    Image.fromarray(big).save(V.lp(OUT))
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    print(f"{OUT}: rows {ys.min()}-{ys.max()} ({ys.max() - ys.min() + 1}), cols {xs.min()}-{xs.max()}, "
          f"{len({tuple(p[:3]) for p in a[op]})} colours, {len(K.pieces(a))} piece(s)")


if __name__ == "__main__":
    main()
