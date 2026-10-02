"""Caitlyn with longer legs and slimmer back hair (tools/art/import_native.py TIDY, on her finished frames).

tidy(tag, k, frame) -> frame
  frame: HxWx4 uint8, the pivot at the centre pixel, soles row = centre + 11, empty rows over her (import_native pads
  6); the frame that comes back is the same size, her body up to LEGS rows higher in it.

Players found her legs too short and her too fat (2026-10-03); the user: "女警被玩家指摘腿太短 太胖 参考oppi的女警调整一波".
oppi's Caitlyn (workshop 3774304166, champions/caitlyn2.aseprite) stands 37 rows: 8 of hat, legs 8 rows of 2-3 px
thin strokes; ours stood 41 rows with hat and face half her height, 9 rows of legs in thick boots and a wide mass of
hair behind her back. Of the three options shown (A legs +3, B legs +4, C legs +3 and the back hair 2 squares in) the
user had Claude pick one: C.
  legs:  the cheapest row between pivot +2 and +9 where her legs are thin strokes - runs no wider than 7 squares
         (or one crossed run up to 14: a run's passing frames), 16 squares at most, 3+ rows over her lowest pixel and
         not mostly outline (a boot's sole or edge) - is repeated LEGS more times; every row above it moves up LEGS
         rows, the boots and soles stay. A frame with no such row moves up whole when it is off the ground (E's hop
         back: it keeps its height over her stride) and stays as drawn when the legs are folded (Q's kneeling shot
         3-7, W's crouch 3-4, the death from 3 on, R's kneeling channel 3-8 - KEEP holds R 5-7, where thin shins
         show, at the kneel's height). Idle, run, attack, Headshot, E and hit all stand LEGS rows taller.
  hair:  in the rows from under the hat brim to the skirt's hem (pivot -24 .. +2) where her left edge is the navy
         hair or its outline, the edge comes HAIR squares in and the new edge takes the outline colour (the rifle's
         stock and her arm, when they are the edge, stay); hair tips the cut leaves floating (Q 1-3, the hop in E 4-6,
         R 8: 1-3 squares each) go with it.
Nothing is redrawn: rows are repeated, squares at the hair's edge cleared.
The rifle rises with her: the muzzles in tools/art/import_caitlyn.py and the kit's bullet y_offsets follow the
frames they fire on (attack, Headshot and E 3 px higher; Q and R fire kneeling and stay).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                ".claude", "skills", "tfm2-hero-mod", "scripts"))
from strips import label  # noqa: E402

LEGS = 3                        # rows the legs grow
HAIR = 2                        # squares the back hair comes in
LOOSE = 8                       # pieces under this many squares the hair cut leaves floating are cleared
OUTLINE = (0x10, 0x02, 0x16)    # her outline (fix_caitlyn_run.RING) where the hair's new edge has none
# (tag, slot) kept at the kneel's height: R's kneeling channel is slots 2-7; the rule finds thin shins in 4-6
KEEP = {("ult", 4), ("ult", 5), ("ult", 6)}


def lum(p):
    return 0.299 * int(p[0]) + 0.587 * int(p[1]) + 0.114 * int(p[2])


def is_hair(p):
    """Her navy hair: blue well over red, no greener than blue, dark."""
    r, g, b = int(p[0]), int(p[1]), int(p[2])
    return p[3] > 0 and b > r + 25 and b > g and lum(p) < 120


def is_dark(p):
    return p[3] > 0 and lum(p) < 35


def run_widths(row):
    """Widths of the opaque runs in a row, left to right."""
    m = row[:, 3] > 0
    out, w = [], 0
    for v in m:
        if v:
            w += 1
        elif w:
            out.append(w)
            w = 0
    if w:
        out.append(w)
    return out


def leg_row(f, lo=2, hi=9, max_leg=7):
    """The row (frame index) to repeat, or None: see the module's legs rule."""
    H = f.shape[0]
    py = H // 2
    ys = np.nonzero(f[..., 3].any(1))[0]
    lowest = ys[-1] if len(ys) else H - 1
    best = None
    for y in range(py + lo, min(lowest - 2, py + hi + 1)):
        ws = run_widths(f[y])
        if ws and max(ws) <= max_leg * (1 if len(ws) >= 2 else 2) and sum(ws) <= 16:
            on = f[y, :, 3] > 0
            dark = sum(1 for x in np.nonzero(on)[0] if is_dark(f[y, x]))
            if dark > 0.6 * on.sum():
                continue
            if best is None or sum(ws) < best[0]:
                best = (sum(ws), y)
    return None if best is None else best[1]


def legs(f, n, keep=False):
    """The frame n rows longer in the legs (same size: its top n rows must be empty, import_native pads 6)."""
    H = f.shape[0]
    py = H // 2
    if f[:n, :, 3].any():
        raise ValueError("no room over the frame to grow")
    if keep:
        return f.copy()
    out = np.zeros_like(f)
    y = leg_row(f)
    if y is None:
        ys = np.nonzero(f[..., 3].any(1))[0]
        if len(ys) and ys[-1] < py + 10:                  # off the ground: up whole
            out[0:H - n] = f[n:]
            return out
        return f.copy()                                   # folded legs: as drawn
    out[0:y + 1 - n] = f[n:y + 1]                         # the row and everything above it: up n
    out[y + 1 - n:y + 1] = f[y]                           # the row again, n times
    out[y + 1:] = f[y + 1:]                               # the boots: where they were
    return out


def hair(f, k):
    """The left edge k squares in where it is hair or its outline, pivot rows -24 .. +2."""
    py = f.shape[0] // 2
    out = f.copy()
    for y in range(max(0, py - 24), min(f.shape[0] - 1, py + 2) + 1):
        xs = np.nonzero(f[y, :, 3] > 0)[0]
        if not len(xs):
            continue
        x0 = xs[0]
        seg = [f[y, x] for x in range(x0, min(f.shape[1], x0 + k + 2))]
        if not all(is_hair(p) or is_dark(p) for p in seg) or not any(is_hair(p) for p in seg[1:]):
            continue
        out[y, x0:x0 + k] = 0
        if is_hair(out[y, x0 + k]):
            out[y, x0 + k, :3] = f[y, x0, :3] if is_dark(f[y, x0]) else OUTLINE
            out[y, x0 + k, 3] = 255
    return floating(f, out)


def floating(before, after, limit=LOOSE):
    """after without the small pieces that were part of before's main body (cut off by the hair cut)."""
    lab0, _ = label(before[..., 3] > 0)
    main0 = np.bincount(lab0.ravel())[1:].argmax() + 1
    lab, n = label(after[..., 3] > 0)
    sizes = np.bincount(lab.ravel())
    out = after.copy()
    for c in range(1, n + 1):
        m = lab == c
        if sizes[c] < limit and (lab0[m] == main0).all():
            out[m] = 0
    return out


def tidy(tag, k, frame):
    return legs(hair(np.asarray(frame, np.uint8), HAIR), LEGS, keep=(tag, k) in KEEP)
