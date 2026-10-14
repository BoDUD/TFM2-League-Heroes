#!/usr/bin/env python3
"""league_smolder's action frames from Codex's step-2 fine drafts (assets/source/smolder/codex_strips) on the design's
grid (PPU 1.5: one square = one dense pixel), the way tools/art/design_smolder.py made the design.

    python tools/art/import_smolder_strips.py [--review DIR]

Codex drew the 42 frames as fine drafts (~6-px squares) on the pack's canvas (tools/art/pack_smolder_strips.py:
1536 x 1024, a design square 12 px, the soles on y 990, the feet's middle x 760), each a little bigger or smaller than
the design (its HANDOFF; run 3-5 ~1.15x, attack 1-2 with bodies 10 % bigger than their heads) and 6-10 squares right of
the design draft (it followed the skeletons). So per frame:
  * the head: normalised cross-correlation of the design draft's face on the pack canvas (FACE_BOX: the crest's front,
    both eyes, the snout and the grin) over scales 0.78-1.6 (HEADS: the face's centre in the frame, the frame's scale,
    the NCC; 2026-10-15 with the scratchpad headmatch.py, refined at full resolution); WHOLE: the figure's size from its
    drawn area against the draft's;
  * the size (SIZES): with the wings folded the geometric mean of the head scale and the whole size (Bard's way), with
    them spread the head alone, SIZE_SET where the face is turned or thrown back (weak match);
  * the cut (design_smolder's way, not means): every pixel snapped to the design's colours (Lab), then each square of
    12 x size px the commonest drawn colour it covers, the outline where near-black covers 40 % or more of the drawn
    part, clear where half or more is clear, the grid scaled round the pack's standing point (760, 990);
  * placed: an action's first frame stands its feet's middle over the design's, the rest keep Codex's moves from it;
    the run's head held on one column RUN_LEAN squares ahead of the idle's (no sliding inside the loop); every
    grounded frame's lowest square on the ground row SOLE, the flight's frames where Codex drew them and lifted
    (PLACE: 2 squares at the jump and the landing, 5-6 in the loop - Codex hovered them 0-2 squares, a hop in game);
  * one face (memory one-face-all-frames): the design's eyes (FACE "eyes") and grin ("full") pasted on the frame's face
    where the head is the design's way up; the frames not listed keep Codex's own face (eyes shut: the sneeze, the shout
    thrown back, the death);
  * the outline closed (strips.complete_outline), specks gone, one-square cracks and pinholes closed, one calm pass (a
    lit square never turns outline), every near-black square the one outline colour K.
idle = the design breathing (everything above the legs a square up and back), hit = the design 2 / 1 squares back with
a white flash on the first frame.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "smolder")
DESIGN = os.path.join(SRC, "hd", "front.png")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
PX = 12.0                          # pack canvas px a design square (pack_smolder_strips.py PX)
STAND = (760.0, 990.0)            # the pack's standing point (the feet's middle on the soles' line)
REF_TL = (297.0, 453.0)            # the design's top-left corner on the pack canvas (NCC of the design x12 on the draft)
FACE_BOX = (770, 550, 965, 700)    # the face matched, pack canvas px; its centre:
REF_FACE = ((FACE_BOX[0] + FACE_BOX[2]) / 2, (FACE_BOX[1] + FACE_BOX[3]) / 2)
D_FACE = ((REF_FACE[0] - REF_TL[0]) / PX, (REF_FACE[1] - REF_TL[1]) / PX)   # ... in design squares (47.54, 14.33)
COLS, ROWS = 128, 86               # the frame canvas (design squares): the pack canvas / 12
DX, DY = 25, 38                    # the design's top-left square on the canvas (REF_TL / 12, rounded)
SOLE = DY + 44                     # the ground row: the design's soles
PIV_C = DX + 38                    # the standing column: the middle of the design's feet (cols 21-56; pack x 760)
K = (7, 0, 16)                     # the outline: the design's commonest near-black
DARK = 120                         # r + g + b under this: outline
TAGS = [("run", 8), ("attack", 5), ("skill", 5), ("skill2", 5), ("skill2_e", 8), ("ult", 5), ("dead", 6)]
AIR = {"skill2_e_2", "skill2_e_3", "skill2_e_4", "skill2_e_5", "skill2_e_6", "skill2_e_7"}
# the face's centre (pack canvas px) and the frame's scale against the design, NCC of FACE_BOX over scales 0.78-1.6
# (half resolution, then 0.01 steps at full resolution; 2026-10-15, the scratchpad headmatch.py), and the NCC; the
# scale is the better of that match and a second one on the upper face alone (crest, brow, eyes: 770-965 x 545-652,
# no mouth) where the second matched better - an open mouth or puffed cheeks pulled the first (attack 2, attack 3,
# skill 1, 3, 4, 5, skill2_e 7, ult 2, ult 4: 1.11 -> 1.02, dead 2, 3)
HEADS = {
    "run_1": (947.9, 612.8, 0.99, 0.927), "run_2": (931.3, 593.8, 1.04, 0.868), "run_3": (971.7, 568.8, 1.18, 0.834),
    "run_4": (1006.3, 568.4, 1.16, 0.837), "run_5": (992.4, 564.9, 1.16, 0.859), "run_6": (966.7, 593.8, 1.04, 0.876),
    "run_7": (973.9, 602.6, 1.03, 0.875), "run_8": (982.1, 600.0, 1.06, 0.825),
    "attack_1": (976.1, 669.8, 0.95, 0.584), "attack_2": (988.9, 596.7, 0.97, 0.618),
    "attack_3": (1067.3, 578.3, 1.14, 0.647), "attack_4": (1031.1, 509.6, 1.14, 0.716),
    "attack_5": (888.5, 626.7, 0.99, 0.852),
    "skill_1": (936.7, 540.1, 1.09, 0.738), "skill_2": (953.2, 716.6, 1.04, 0.666), "skill_3": (990.6, 684.8, 1.04, 0.723),
    "skill_4": (980.5, 596.2, 1.11, 0.753), "skill_5": (975.3, 584.8, 1.16, 0.847),
    "skill2_1": (986.6, 516.2, 1.16, 0.495), "skill2_2": (912.5, 464.6, 1.01, 0.431),
    "skill2_3": (911.0, 485.1, 1.03, 0.445), "skill2_4": (1034.8, 694.6, 1.02, 0.441),
    "skill2_5": (954.6, 530.4, 1.20, 0.814),
    "skill2_e_1": (1015.8, 609.6, 1.20, 0.709), "skill2_e_2": (1017.9, 511.6, 1.16, 0.777),
    "skill2_e_3": (1035.3, 537.1, 1.16, 0.755), "skill2_e_4": (971.4, 536.4, 1.20, 0.700),
    "skill2_e_5": (994.2, 429.6, 1.20, 0.603), "skill2_e_6": (959.3, 510.7, 1.14, 0.744),
    "skill2_e_7": (961.1, 620.4, 1.11, 0.646), "skill2_e_8": (936.9, 608.0, 1.08, 0.744),
    "ult_1": (900.7, 583.0, 1.03, 0.776), "ult_2": (918.6, 650.4, 0.99, 0.766), "ult_3": (673.3, 893.8, 0.84, 0.387),
    "ult_4": (986.2, 452.9, 1.02, 0.639), "ult_5": (970.4, 541.5, 1.19, 0.912),
    "dead_1": (929.2, 634.4, 1.09, 0.402), "dead_2": (842.3, 607.6, 0.92, 0.516), "dead_3": (868.9, 592.8, 1.10, 0.503),
    "dead_4": (1020.4, 702.1, 1.19, 0.436), "dead_5": (1178.7, 771.1, 1.26, 0.432), "dead_6": (1178.7, 771.1, 1.26, 0.432),
}
# the whole figure's size against the pack's design draft: sqrt(drawn pixels / the draft's), alpha >= 128 (2026-10-15)
WHOLE = {
    "run_1": 0.98, "run_2": 1.01, "run_3": 1.13, "run_4": 1.12, "run_5": 1.10, "run_6": 1.02, "run_7": 1.04, "run_8": 1.05,
    "attack_1": 1.07, "attack_2": 1.12, "attack_3": 1.17, "attack_4": 1.20, "attack_5": 0.99,
    "skill_5": 1.15, "skill2_5": 1.22, "skill2_e_8": 1.05, "ult_1": 1.08, "ult_2": 1.03, "ult_5": 1.19,
    "dead_1": 1.00, "dead_2": 1.05, "dead_3": 1.12, "dead_4": 1.12, "dead_5": 1.25, "dead_6": 1.25,
}
# the frame's size: where the wings are folded (the figure the design's shape) the geometric mean of its head scale and
# its whole size (Bard's way: Codex drew some bodies bigger than their heads - attack 1 / 2 by 10 % - and a size from
# the head alone pumped those bodies); with the wings spread, the head alone; where the face is turned or thrown back
# the match is weak (NCC < 0.5) and the size is set here instead (the action's neighbours)
SIZE_SET = {"skill2_1": 1.17, "skill2_2": 1.17, "skill2_3": 1.17, "skill2_4": 1.17, "ult_3": 1.03}
SIZES = {k: SIZE_SET.get(k, float(np.sqrt(v[2] * WHOLE[k])) if k in WHOLE else v[2]) for k, v in HEADS.items()}
# one face: "full" = the design's eyes and grin, "eyes" = its eyes over Codex's open mouth; frames not listed keep
# Codex's own face (eyes shut: the sneeze, the shout thrown back, the death)
FACE = {**{f"run_{i}": "full" for i in range(1, 9)}, "attack_1": "full", "attack_2": "eyes", "attack_3": "eyes",
        "attack_4": "eyes", "attack_5": "full", "skill_1": "eyes", "skill_2": "eyes", "skill_3": "eyes",
        "skill_4": "eyes", "skill_5": "full", "skill2_5": "full",
        **{f"skill2_e_{i}": "eyes" for i in range(1, 8)}, "skill2_e_8": "full",
        "ult_1": "eyes", "ult_2": "eyes", "ult_4": "eyes", "ult_5": "full"}
# per-frame moves (squares) over the placement: the flight lifted off the ground (Codex hovered it 0-2 squares over its
# red line - read in game as a hop; League's flap flight is well clear of the ground): 2 at the jump and the landing, 5-6
# in the loop, the face bobbing 4 rows over it (Codex's e_5 sat 7 higher than e_4); e_3 also 4 squares back (Codex drew it 4-5 ahead of e_4-e_6: the loop lurched at every wing beat)
PLACE = {"skill2_e_2": (0, -2), "skill2_e_3": (-4, -5), "skill2_e_4": (0, -7), "skill2_e_5": (0, -3),
         "skill2_e_6": (0, -5), "skill2_e_7": (0, -2)}
RUN_LEAN = 2
# the frames that end an action back in the standing pose: laid over the idle (overlap_dx)
RETURN = {"attack_5", "skill_5", "skill2_5", "skill2_e_8", "ult_5"}
LINE_LUM = 20                      # luminance under this: the outline (K is 4, the darkest colour, navy (32, 30, 71), 35)
HOLE_MAX = 9                       # enclosed pockets up to this many squares become outline (holes())
PAINT = {}                         # per-frame hand fixes after the finish (filled below the helpers)


def design():
    d = np.array(Image.open(DESIGN).convert("RGBA"))
    dark = (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < DARK)
    d[dark, :3] = K
    return d


def palette():
    d = design()
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0)


def read(key):
    a = np.array(Image.open(os.path.join(CODEX, f"smolder_{key}.png")).convert("RGBA"))
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def snap(a, pal):
    """Palette indices (-1 clear) of every pixel: the outline under DARK, else the nearest design colour (Lab)."""
    op = a[..., 3] > 0
    idx = np.full(op.shape, -1, int)
    dark = op & (a[..., :3].astype(int).sum(-1) < DARK)
    k0 = int(np.nonzero((pal == K).all(1))[0][0])
    idx[dark] = k0
    m = op & ~dark
    lit = pal.astype(int).sum(1) >= DARK
    lab_p = PD._lab(pal[lit].astype(float))
    lit_ix = np.nonzero(lit)[0]
    px = PD._lab(a[m][:, :3].astype(float))
    best = np.empty(len(px), int)
    for i in range(0, len(px), 200000):
        best[i:i + 200000] = ((px[i:i + 200000, None] - lab_p[None]) ** 2).sum(-1).argmin(1)
    idx[m] = lit_ix[best]
    return idx, k0


def cut(a, pal, s):
    """The frame `a` voted down onto the canvas: squares of PX x s frame px round the pack's standing point (760, 990),
    which lands on the canvas's (PIV_C + 0.5, SOLE + 1): Codex drew every frame round it, so its place is kept."""
    idx, k0 = snap(a, pal)
    H, W = idx.shape
    c = PX * s
    gx0, gy0 = STAND[0] - (PIV_C + 0.5) * c, STAND[1] - (SOLE + 1) * c      # frame px of the canvas's (0, 0)
    # every frame pixel's square on the canvas
    cx = np.floor((np.arange(W) + 0.5 - gx0) / c).astype(int)
    cy = np.floor((np.arange(H) + 0.5 - gy0) / c).astype(int)
    out = np.zeros((ROWS, COLS, 4), np.uint8)
    n = len(pal) + 1
    ok_x = (cx >= 0) & (cx < COLS)
    ok_y = (cy >= 0) & (cy < ROWS)
    ys, xs = np.nonzero(ok_y[:, None] & ok_x[None, :])
    cell = cy[ys] * COLS + cx[xs]
    lab = idx[ys, xs] + 1                                # 0 clear
    votes = np.zeros((ROWS * COLS, n))
    np.add.at(votes, (cell, lab), 1.0)
    tot = votes.sum(1)
    drawn = tot - votes[:, 0]
    keep = (tot > 0) & (drawn * 2 > tot)
    dark = votes[:, k0 + 1] >= 0.4 * np.maximum(drawn, 1)
    lit_votes = votes[:, 1:].copy()
    lit_votes[:, k0] = -1
    pick = np.where(dark, k0, lit_votes.argmax(1))
    flat = out.reshape(-1, 4)
    flat[keep, :3] = pal[pick[keep]]
    flat[keep, 3] = 255
    return out


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys = slice(max(0, dy), min(H, H + dy))
    xs = slice(max(0, dx), min(W, W + dx))
    out[ys, xs] = a[max(0, -dy):min(H, H - dy), max(0, -dx):min(W, W - dx)]
    return out


def close_small(a, most=4):
    """Ground showing inside the figure (memory gap-check): enclosed clear pockets of `most` squares or fewer and
    one-square cracks between two drawn squares (left-right or up-down) become outline."""
    while True:
        op = a[..., 3] > 0
        lab, n = ndimage.label(~op)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        fill = np.zeros_like(op)
        for j in range(1, n + 1):
            if j not in border and (lab == j).sum() <= most:
                fill |= lab == j
        p = np.pad(op, 1)
        fill |= ~op & ((p[:-2, 1:-1] & p[2:, 1:-1]) | (p[1:-1, :-2] & p[1:-1, 2:]))
        if not fill.any():
            return a
        a[fill, :3] = K
        a[fill, 3] = 255


def pinholes(a, most=3):
    """Enclosed holes of at most `most` squares take the commonest colour round them."""
    op = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() > most:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
        a[m, :3] = cols[cnt.argmax()]
        a[m, 3] = 255
    return a


def specks(a, most=2):
    """Loose bits of `most` squares or fewer, not touching the figure (Codex's haze kept at the cut) go."""
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        for j, sz in enumerate(sizes, 1):
            if sz <= most:
                a[lab == j] = 0
    return a


def holes(a, most=HOLE_MAX):
    """Enclosed clear pockets of `most` squares or fewer become outline (the reviewer's 6-8 square slits through the
    mane / wing where the design has none); the tail's curl and the gaps under the wings are bigger and stay."""
    op = a[..., 3] > 0
    lab, n = ndimage.label(~op)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    for j in range(1, n + 1):
        m = lab == j
        if j not in border and m.sum() <= most:
            a[m, :3] = K
            a[m, 3] = 255
    return a


def caps(a, feet):
    """The outline the cut loses at the tips: over every lit square with clear above in the figure's top 6 rows (the
    flame tufts, the horn and wing tips) and under every lit square with clear below in the feet's rows (the ground row
    itself takes the outline: nothing goes under it)."""
    op = a[..., 3] > 0
    lit = op & (a[..., :3].astype(int).sum(-1) >= DARK)
    top = int(np.nonzero(op.any(1))[0][0])
    for y, x in zip(*np.nonzero(lit)):
        if top <= y <= top + 5 and y > 0 and not op[y - 1, x]:
            a[y - 1, x] = (*K, 255)
        if y >= SOLE - 8 and (y + 1 >= ROWS or not op[y + 1, x]):
            if feet is not None and y >= feet:
                a[y, x] = (*K, 255)
            elif y + 1 < ROWS:
                a[y + 1, x] = (*K, 255)
    return a


def finish(can, keep, feet=None):
    """The cut frame tidied: specks out, the outline closed (nothing under the ground row `feet` when given), cracks and
    small pockets closed, one calm pass (a lit square never turns outline), the tips' outline, every near-black square
    the outline colour K."""
    can = specks(can)
    # dark=LINE_LUM: only the outline itself is "dark" - the wings' navies (luminance 35-65) are colour and get an
    # outline too (with complete_outline's default 70 the navy wing edges stayed open: e_4's underside, the chest)
    can, _, _ = G.complete_outline(can, color=K, feet=feet, dark=LINE_LUM)
    can = close_small(can)
    op = can[..., 3] > 0
    lit = op & (can[..., :3].astype(int).sum(-1) >= DARK)
    e = PD._majority(can, op, keep | ~lit)
    grew = (e[..., :3].astype(int).sum(-1) < DARK) & lit
    e[grew] = can[grew]
    e = pinholes(e)
    e = holes(e)
    e = caps(e, feet)
    if feet is not None:
        e[feet + 1:] = 0
    dark = (e[..., 3] > 0) & (e[..., :3].astype(int).sum(-1) < DARK)
    e[dark, :3] = K
    return e


# the design's face (design squares, rows / cols): both eyes with the brow between, and the grin
EYES = (11, 18, 36, 55)            # rows 11-17, cols 36-54
GRIN = (17, 21, 43, 54)            # rows 17-20, cols 43-53


def paste_face(can, at, how):
    """The design's eyes (and grin) on the frame, the design square under the matched face centre `at` (canvas
    squares) where the design has it (D_FACE)."""
    d = design()
    oc = int(round(at[0] - D_FACE[0]))
    orow = int(round(at[1] - D_FACE[1]))
    boxes = [EYES] + ([GRIN] if how == "full" else [])
    keep = np.zeros(can.shape[:2], bool)
    for r0, r1, c0, c1 in boxes:
        for r in range(r0, r1):
            for c in range(c0, c1):
                if d[r, c, 3] == 0:
                    continue
                y, x = r + orow, c + oc
                if 0 <= y < ROWS and 0 <= x < COLS and can[y, x, 3] > 0:
                    can[y, x] = d[r, c]
                    keep[y, x] = True
    return can, keep


def face_at(key, dx=0, dy=0):
    """The matched face centre on the canvas (squares) for the frame's size, moved as the frame was."""
    hx, hy = HEADS[key][:2]
    c = PX * SIZES[key]
    return (PIV_C + 0.5 + (hx - STAND[0]) / c + dx, SOLE + 1 + (hy - STAND[1]) / c + dy)


def feet_mid(can, rows=3):
    """The middle of the lowest `rows` rows' drawn columns (first to last)."""
    op = can[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    xs = np.nonzero(op[ys[-1] - rows + 1:ys[-1] + 1].any(0))[0]
    return (xs.min() + xs.max()) / 2.0


def lowest(can):
    return int(np.nonzero((can[..., 3] > 0).any(1))[0][-1])


def ground_row(can, need=3):
    """The lowest row holding a run of `need` or more drawn squares - a sole, not the 1-2 square outline stubs the cut
    leaves under a claw (the reviewer: 14 frames stood on such stubs, their soles a row over the ground)."""
    op = can[..., 3] > 0
    for y in range(ROWS - 1, -1, -1):
        r = np.concatenate([[0], op[y].astype(int), [0]])
        d = np.diff(r)
        if len(d) and ((np.nonzero(d < 0)[0] - np.nonzero(d > 0)[0]) >= need).any():
            return y
    return lowest(can)


def overlap_dx(can, ref, reach=6):
    """The sideways move (squares) that lays `can` best over `ref` (most shared drawn squares)."""
    a, b = can[..., 3] > 0, ref[..., 3] > 0
    best = max(range(-reach, reach + 1), key=lambda dx: (np.roll(a, dx, axis=1) & b).sum())
    return best


def tag_frames(tag, n, pal, idle):
    """Every frame of an action: cut, moved (see the docstring), one face, finished."""
    keys = [f"{tag}_{i}" for i in range(1, n + 1)]
    cuts = {k: cut(read(k), pal, SIZES[k]) for k in keys}
    d_feet = DX + 38.5                                 # the design's feet middle (cols 21-56) on the canvas
    moves = {}
    if tag == "run":
        # the head held on one column, RUN_LEAN squares ahead of the idle's (Codex drew the trot 6-8 squares right of
        # the design: a jump at every start), the feet on the ground: no sliding inside the loop
        hc = DX + D_FACE[0] + RUN_LEAN
        for k in keys:
            moves[k] = (int(round(hc - face_at(k)[0])), SOLE - ground_row(cuts[k]))
    else:
        # the action's first frame stands its feet's middle over the design's; the rest keep Codex's moves from it
        dx = int(round(d_feet - feet_mid(cuts[keys[0]])))
        for k in keys:
            if k in AIR:
                low = lowest(cuts[k])
                moves[k] = (dx, -max(0, low - SOLE))
            else:
                moves[k] = (dx, SOLE - ground_row(cuts[k]))
    for k in RETURN & set(keys):
        # back to the standing pose: laid over the idle where it fits best (Codex ended attack and W 4 squares left of
        # the idle and R 2 right: a jump back at every end)
        m = shift(cuts[k], *moves[k])
        moves[k] = (moves[k][0] + overlap_dx(m, idle), moves[k][1])
    out = []
    for k in keys:
        dx, dy = moves[k]
        pdx, pdy = PLACE.get(k, (0, 0))
        can = shift(cuts[k], dx + pdx, dy + pdy)
        feet = None if k in AIR else SOLE
        if feet is not None:
            can[feet + 1:] = 0
        keep = np.zeros(can.shape[:2], bool)
        if k in FACE:
            can, keep = paste_face(can, face_at(k, dx + pdx, dy + pdy), FACE[k])
        can = finish(can, keep, feet)
        if k in PAINT:
            can = PAINT[k](can)
        out.append(can)
    return out


# ------------------------------------------------------------------------------------------- hand fixes (PAINT)
PINK = (253, 121, 154)             # the cape's lower fringe
ORANGE = (253, 133, 65)            # the tail's underside


def decape(box, tail_cols):
    """E's take-off and first loop frame: Codex left the folded cape (its pink fringe) hanging under the spread wings -
    a third wing that blinked on every loop (e_4-e_6 have none; its HANDOFF flagged it). The fringe inside `box` goes,
    the band left over it - the tail's base - gets the tail's orange underside in the columns `tail_cols` (not the hind
    leg's), loose outline goes, the outline closed again."""
    x0, y0, x1, y1 = box

    def fix(can):
        sub = can[y0:y1, x0:x1]
        pink = (sub[..., :3] == PINK).all(-1) & (sub[..., 3] > 0)
        sub[pink] = 0
        for x in range(*tail_cols):
            col = can[y0:y1, x]
            lit = (col[:, 3] > 0) & (col[:, :3].astype(int).sum(-1) >= DARK)
            ys = np.nonzero(lit)[0]
            if len(ys):
                can[y0 + ys[-1], x, :3] = ORANGE
        op = can[..., 3] > 0
        lit = op & (can[..., :3].astype(int).sum(-1) >= DARK)
        near = ndimage.binary_dilation(lit, structure=np.ones((3, 3)))
        loose = op & ~lit & ~near
        loose[:y0], loose[y1:], loose[:, :x0], loose[:, x1:] = False, False, False, False
        can[loose] = 0
        can, _, _ = G.complete_outline(can, color=K)
        return holes(close_small(can))
    return fix


def letters():
    """The design's colours by letter (a = the outline K, then by colour value: the letters.py table)."""
    import string
    pal = [tuple(int(v) for v in c) for c in palette()]
    return {string.ascii_letters[i]: c for i, c in enumerate(pal)}


def patch(rows):
    """Hand pixels: [(row, first column, letters)] - a letter is a design colour (letters()), '.' clear, ' ' kept."""
    def fix(can):
        lut = letters()
        for r, c0, txt in rows:
            for i, ch in enumerate(txt):
                if ch == " ":
                    continue
                can[r, c0 + i] = (0, 0, 0, 0) if ch == "." else (*lut[ch], 255)
        return can
    return fix


HORN_COLS = {(252, 94, 41), (244, 185, 103), (253, 133, 65), (31, 163, 157), (12, 98, 107)}   # flame + teal horn
WING_COLS = {(148, 10, 68), (40, 40, 93), (54, 60, 126), (200, 19, 64), (90, 9, 57), (32, 30, 71)}


def horn_ring(box):
    """Q 2-3: the near wing's root runs up behind the head and the cut merged the far horn and its flame into it (Codex
    drew them in front of the wing): the flame + horn squares inside `box` get an outline wherever they touch the wing's
    colours, so the horn reads in front of the wing again."""
    x0, y0, x1, y1 = box

    def fix(can):
        rgb = [[tuple(int(v) for v in can[y, x, :3]) for x in range(COLS)] for y in range(ROWS)]
        horn = np.zeros((ROWS, COLS), bool)
        for y in range(y0, y1):
            for x in range(x0, x1):
                horn[y, x] = can[y, x, 3] > 0 and rgb[y][x] in HORN_COLS
        ring = ndimage.binary_dilation(horn, structure=np.ones((3, 3))) & ~horn
        for y, x in zip(*np.nonzero(ring)):
            if can[y, x, 3] > 0 and rgb[y][x] in WING_COLS:
                can[y, x] = (*K, 255)
        return can
    return fix


def trim(box):
    """Squares inside `box` cleared, the outline closed under what is left above it (R 3's wing tips hung to a row over
    the ground next to the feet: they read as touching it)."""
    x0, y0, x1, y1 = box

    def fix(can):
        can[y0:y1, x0:x1] = 0
        y = y0 - 1
        for x in range(x0, x1):
            if can[y, x, 3] > 0 and int(can[y, x, :3].astype(int).sum()) >= DARK:
                can[y0, x] = (*K, 255)
        return can
    return fix


HIND = (36, 57)                    # the run's hind leg columns (canvas): everything left of the front legs
HIND_REACH = 3                     # a hind foot this many rows or fewer over the ground is planted


def plant_hind(can):
    """The run: Codex drew the hind feet 2-5 rows over the ground in every frame (the reviewer: it read as hopping on the
    front legs). Where the hind foot is HIND_REACH rows or fewer up, its lower leg is drawn that much longer - the rows
    from 3 over the foot's bottom moved down onto the ground row, the row they left repeated - so the hind foot stands
    on the ground; the frames with the hind leg swung forward (2 rows or more higher) keep it lifted."""
    x0, x1 = HIND
    op = can[..., 3] > 0
    rows = np.nonzero(op[66:SOLE + 1, x0:x1].any(1))[0]
    if not len(rows):
        return can
    rb = 66 + int(rows[-1])
    g = SOLE - rb
    if g < 1 or g > HIND_REACH:
        return can
    rc = rb - 3
    cols = [x for x in range(x0, x1) if op[rc:rb + 1, x].any()]
    old = can.copy()
    for x in cols:
        for r in range(rb, rc - 1, -1):
            can[r + g, x] = old[r, x]
        for r in range(rc, rc + g):
            can[r, x] = old[rc, x]
    can, _, _ = G.complete_outline(can, color=K, feet=SOLE, dark=LINE_LUM)
    return close_small(can)


def chain(*fixes):
    def fix(can):
        for f in fixes:
            can = f(can)
        return can
    return fix


def on_canvas(dx=0, dy=0):
    d = design()
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[DY + dy:DY + dy + d.shape[0], DX + dx:DX + dx + d.shape[1]] = d
    return can


# the idle: the design breathing - everything above the legs (design rows < WAIST) a square up, the squares it
# uncovers the colour under them; the legs and the feet stay
WAIST = 35
IDLE = [(0, 220), (0, 180), (1, 260), (1, 180)]


def breathe(can, mask, k):
    if k == 0:
        return can.copy()
    out = can.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    rest = out.copy()
    out[ys - k, xs] = can[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            below = y + 1
            while below < can.shape[0] and out[below, x, 3] == 0 and mask[below, x]:
                below += 1
            if below < can.shape[0] and rest[below, x, 3] > 0:
                out[y, x] = rest[below, x]
            elif below < can.shape[0] and out[below, x, 3] > 0:
                out[y, x] = out[below, x]
    return out


def idle_frames():
    can = on_canvas()
    op = can[..., 3] > 0
    yy = np.mgrid[0:ROWS, 0:COLS][0]
    mask = op & (yy < DY + WAIST)
    out = []
    for k, ms in IDLE:
        b = breathe(can, mask, k)
        b, _, _ = G.complete_outline(b, color=K, feet=SOLE, dark=LINE_LUM)   # the waist's step opens the chest's edge
        out.append((close_small(b), float(ms)))
    return out


def hit_frames(idle):
    """The idle's first frame (its cracks closed) 2 / 1 squares back, the first flashed white."""
    out = []
    for dx, flash, ms in ((-2, True, 90), (-1, False, 120)):
        a = shift(idle, dx, 0)
        if flash:
            m = a[..., 3] > 0
            a[m, :3] = (a[m, :3].astype(int) * 0.45 + 255 * 0.55).astype(np.uint8)
        out.append((a, float(ms)))
    return out


PAINT.update({
    **{f"run_{i}": plant_hind for i in range(1, 9)},
    "ult_3": trim((30, 79, 47, 82)),
    # Q 2-3: the far horn and its flame outlined off the wing's root (the reviewer: the root swallowed the horn)
    "skill_2": horn_ring((66, 43, 76, 54)),
    "skill_3": horn_ring((69, 42, 78, 53)),
    # Q 4 and E 4: the near wing's root met the far cheek with no line between (it read as a long snout)
    "skill_4": patch([(55, 82, "a"), (57, 82, "a")]),
    "skill2_e_4": patch([(49, 81, "a")]),
    # dead 3: Codex drew it with its eyes open (4 x 4, not the design's) between the shut-eyed dead 2 and dead 4 - they
    # blinked open in the fall; shut like dead 2's: the eyes filled with the face's apricot / cream, a dark arc each
    "dead_3": patch([(52, 62, "nnn"),
                     (53, 60, "naaaat"), (54, 59, "nannnnat"), (55, 59, "nnnnntt"), (56, 60, "nnnt"),
                     (49, 70, "nn"), (50, 70, "aaa"), (51, 70, "nn")]),
    "skill2_e_2": decape((28, 57, 51, 70), (31, 45)),
    "skill2_e_3": decape((24, 54, 48, 67), (26, 43)),
})


def frames():
    pal = palette()
    cells = json.load(open(os.path.join(CODEX, "cells.json"), encoding="utf-8"))
    ms = {f["file"][len("smolder_"):-4]: f["ms"] for f in cells["frames"]}
    out = {"idle": idle_frames()}
    idle = out["idle"][0][0]
    for tag, n in TAGS:
        out[tag] = [(f, float(ms[f"{tag}_{i}"])) for i, f in enumerate(tag_frames(tag, n, pal, idle), 1)]
    out["hit"] = hit_frames(idle)
    return out


def review(acts, path, z=4):
    from PIL import ImageDraw
    tiles = [(f"{t}_{k + 1}", a) for t, fr in acts.items() for k, (a, _) in enumerate(fr)]
    W, H = COLS * z, ROWS * z
    per = 6
    rows = (len(tiles) + per - 1) // per
    big = Image.new("RGBA", (per * W, rows * (H + 14)), (150, 160, 150, 255))
    dr = ImageDraw.Draw(big)
    for n, (name, a) in enumerate(tiles):
        x, y = (n % per) * W, (n // per) * (H + 14)
        big.alpha_composite(Image.fromarray(a).resize((W, H), Image.NEAREST), (x, y + 14))
        dr.text((x + 4, y + 1), name, fill=(255, 255, 255, 255))
        dr.line([(x, y + 14 + (SOLE + 1) * z), (x + W, y + 14 + (SOLE + 1) * z)], fill=(0, 90, 255, 255))
        dr.line([(x + (PIV_C + 0.5) * z, y + 14 + (SOLE - 2) * z), (x + (PIV_C + 0.5) * z, y + 14 + (SOLE + 3) * z)],
                fill=(0, 90, 255, 255), width=2)
    big.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a contact sheet of every frame at 4x here")
    a = ap.parse_args()
    acts = frames()
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for tag, fr in acts.items():
        for k, (f, ms) in enumerate(fr):
            Image.fromarray(f).save(os.path.join(OUT, f"{tag}_{k + 1}.png"))
            meta.setdefault(tag, []).append(ms)
    with open(os.path.join(OUT, "frames.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"canvas": [COLS, ROWS], "standing": [PIV_C, SOLE], "ms": meta}, f, indent=1)
    if a.review:
        review(acts, a.review)
    print("frames:", ", ".join(f"{t} {len(f)}" for t, f in acts.items()))


if __name__ == "__main__":
    main()
