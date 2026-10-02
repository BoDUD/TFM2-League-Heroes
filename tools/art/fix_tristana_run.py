#!/usr/bin/env python3
"""Tristana's run legs in the idle's materials: Codex's cross-step (legs v2) with the legs redrawn.

    python tools/art/fix_tristana_run.py [--check]

Codex's legs v2 (assets/source/tristana/codex_run_legs/tristana_run.png, as delivered) gave the run its cross-step
but painted both legs as brown leather - the near leg light brown, the far leg dark brown, as the prompt asked for
one shade lighter and darker - so the leg on the left of the screen turned light and dark brown by turns and never
looked like the idle's ("走路的时候左腿和待机的不一样"); black rows cut the shins from the feet and a hidden leg was a
black block in frames 1, 5 and 6 ("清理一下黑边也别忘了 弄干净一点").
Everything from the hips row down (columns from the hips row's start, 23 wide; the cannon's bell further right) is
redrawn here on Codex's feet and knees: the idle's lilac thighs, dark brown wraps with a lighter one in the middle
and lilac bare feet, both legs the same colours; the outline is one ring, the 4-neighbour ring of the shorts and the
legs (with the corners under a sole), the leg in front ringed over the one behind, so the front leg is the one whose
ring cuts the other. The shorts' crotch on the hips row stays; nothing above it changes.
Then both ears the left one (tools/art/tristana_ears.py), on Codex's head: one row taller than the design's between the
goggles and the face, so the head is found by its middle (the hair and the face between the ears).
Writes assets/source/native/tristana_run.png (8x, cells and pivots unchanged); then run
tools/art/import_native.py --hero tristana. --check compares with the file instead of writing it.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_akali as D  # noqa: E402
import shrink_tristana as S  # noqa: E402
import tristana_ears as EARS  # noqa: E402
from native_refs import layout  # noqa: E402

SRC = os.path.join(S.ROOT, "assets", "source", "tristana", "codex_run_legs", "tristana_run.png")
OUT = os.path.join(S.OUT, "tristana_run.png")
PAL = {"#": S.OUTLINE, "S": (223, 180, 235), "s": (184, 137, 209), "d": (68, 42, 35), "b": (115, 72, 50),
       "k": (135, 96, 46), "g": (65, 73, 45)}
HIPS = [None, "#", "#", "#", "S", "S", "S", "d", "b", "g", "g", "#"]   # the hips row as Codex drew it (columns 0-11)
CROTCH = {7: "d", 8: "b", 9: "g", 10: "g"}                             # the shorts' crotch on the hips row, kept


def rows(*spec):
    """(row, column, colours) triples, rows from the hips row (0) down -> {row: {column: colour}}"""
    out = {}
    for r, x, cs in spec:
        for i, c in enumerate(cs):
            out.setdefault(r, {})[x + i] = c
    return out


# the legs, on Codex's feet and knees (rows from the hips row, columns from its start)
PLANTED = rows((1, 9, "SSs"), (2, 9, "SSs"), (3, 9, "bSS"), (4, 9, "dkd"), (5, 9, "dSSs"), (6, 10, "SSSs"))
LIFTED = rows((1, 7, "SSs"), (2, 3, "SSdkdS"))                         # knee bent, shin and foot back
BEHIND2 = rows((0, 11, "SSSs"), (1, 10, "SSSSs"), (2, 10, "SSSs"), (3, 9, "bSSs"), (4, 8, "dkd"), (5, 7, "dkd"),
               (6, 6, "sSS"), (7, 5, "SSSs"))                          # stretched behind, toe off the ground
FORWARD2 = rows((4, 12, "dk"), (5, 13, "dSS"), (6, 14, "SSSs"))         # swinging forward under her (mostly hidden)
FORWARD6 = rows((0, 11, "SSSs"), (1, 11, "SSs"), (2, 10, "SSSs"), (3, 10, "dkd"), (3, 14, "SS"), (4, 10, "dkdSSSs"))
BEHIND6 = rows((1, 9, "SSs"), (2, 8, "bSS"), (3, 7, "dkd"), (4, 6, "sSS"), (5, 5, "SSSs"))
TUCKED = rows((0, 4, "SSS"), (1, 6, "SSSSs"), (2, 5, "SSSSs"), (3, 5, "bSSs"), (4, 5, "dkd"), (5, 5, "sSS"),
              (6, 4, "SSSs"))                                          # behind her, knee bent
KNEE_UP = rows((0, 12, "SSSs"), (1, 14, "SSSs"), (2, 15, "SSs"), (3, 15, "bSS"), (4, 16, "dkd"), (5, 17, "kd"),
               (6, 17, "SS"), (7, 16, "SSSs"))                         # in front, knee lifted
BACK4 = rows((1, 7, "SSSs"), (2, 6, "dkdS"), (3, 3, "SSSs"))            # lifted behind as she lands
LANDING = rows((0, 12, "SSSs"), (1, 13, "SSs"), (2, 14, "SSs"), (3, 14, "SSSs"), (4, 15, "bSS"), (5, 15, "dkd"),
               (6, 16, "dkSS"), (7, 17, "SSSs"))                       # straight in front, the heel down
LEGS = {1: (LIFTED, PLANTED), 2: (FORWARD2, BEHIND2), 3: (KNEE_UP, TUCKED), 4: (LANDING, BACK4),
        5: (PLANTED, LIFTED), 6: (BEHIND6, FORWARD6), 7: (TUCKED, KNEE_UP), 8: (BACK4, LANDING)}   # (behind, in front)
H, WIDE = 12, 23                                                       # the region: rows from the shorts' bottom


def name(p):
    return next((k for k, v in PAL.items() if v == tuple(int(c) for c in p[:3])), "?") if p[3] else "."


def hips(a):
    """The hips row and its first column: the row reading ###SSSdbgg# from the figure's left + 6."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    x0 = int(xs.min()) + 5
    for y in range(ys.min(), ys.max() + 1):
        if [name(a[y, x0 + i]) for i in range(1, 12)] == HIPS[1:]:
            return y, x0
    sys.exit("no hips row")


def ring4(mask):
    """The 4-neighbour ring of a mask, with the corners under it (a sole's ends)."""
    p = np.pad(mask, 1)
    out = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | p[:-2, :-2] | p[:-2, 2:]
    return out & ~mask


def redraw(a, k):
    a = a.copy()
    h, x0 = hips(a)
    reg = a[h - 1:h - 1 + H, x0:x0 + WIDE].copy()      # row 0 the shorts' bottom (read only), row 1 the hips row
    left = reg[1, :4].copy()
    reg[1:] = 0
    reg[1, :4] = left
    body = np.zeros((H, WIDE), bool)
    body[0] = (reg[0, :, 3] > 0) & ~(reg[0, :, :3] == PAL["#"]).all(-1)
    for x, c in CROTCH.items():
        reg[1, x] = PAL[c] + (255,)
        body[1, x] = True
    masks = []
    for leg in LEGS[k]:
        m = np.zeros((H, WIDE), bool)
        for r, xs in leg.items():
            for x, c in xs.items():
                reg[r + 1, x] = PAL[c] + (255,)
                m[r + 1, x] = True
        masks.append(m)
    behind, front = masks
    rings = (ring4(body | behind) & ~(body | behind | front), ring4(front) & ~(body | front))
    for rg in rings:
        rg[0] = False
        reg[rg] = PAL["#"] + (255,)
    a[h - 1:h - 1 + H, x0:x0 + WIDE] = reg
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the file instead of writing it")
    o = ap.parse_args()
    with open(S.CELLS, encoding="utf-8") as f:
        cell = tuple(json.load(f)["cell"])
    frames = S.strip_frames(SRC, 8, cell)[0]
    new = [redraw(a, k) for k, a in enumerate(frames, 1)]
    idle = S.strip_frames(os.path.join(S.OUT, "tristana_idle.png"), 6, cell)[0][0]
    for k, f in enumerate(new):                     # both ears the left one, as shrink_tristana.py does
        dx, dy, found = EARS.find(f, idle)
        if found < EARS.FOUND:
            sys.exit(f"run {k + 1}: the head's middle is not in it ({found:.0%})")
        new[k] = EARS.same_ears(f, dx, dy)
    strip = S.to_strip(new, layout(8), cell)
    if o.check:
        old = np.asarray(Image.open(D.lp(OUT)).convert("RGBA"))
        same = old.shape == strip.shape and (old == strip).all()
        print(("same " if same else "DIFFERENT ") + OUT)
        sys.exit(0 if same else 1)
    Image.fromarray(strip).save(D.lp(OUT))
    print("written", OUT)


if __name__ == "__main__":
    main()
