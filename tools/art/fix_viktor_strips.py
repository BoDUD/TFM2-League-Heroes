#!/usr/bin/env python3
"""Viktor's action strips from Codex's step-2 delivery (assets/source/viktor/codex_strips/, Codex's rig of the design's
parts; the user: 「帮我完成下一步吧」) into assets/source/native/ for tools/art/import_native.py.

    python tools/art/fix_viktor_strips.py

Fix 1 (the user, at the design: 「法杖这一段有点歪 可以顺便修复了」): the staff's lower shaft stood one column right of
its upper part (design_viktor.py step 1b). Codex's frames carry the design's staff, upright or turned whole, so in
every frame the old lower piece (its four columns, rows 31-40 of the figure) is found by an exact match of its pixels
and moved one column left the same way (design_viktor.kink). A piece the rig turned is not upright and is not matched;
the count per strip is printed. The death's lying frames carry the staff turned a quarter: the strip is searched turned
too (np.rot90, both ways and upside down) and fixed in that orientation (the user: 「法杖是歪的」 at the lying frames).
Fix 2 (the user: 「走路交叉步是反的 你不觉得奇怪吗」): Codex's rig named the legs the wrong way round - its "far_leg" is the
image-right leg with the big foot (the near one, darkened and swapped in front and behind every half cycle) - and its
cycle slid the planted foot forward and the lifted one back, then jumped both back (the legs' offsets read from its
frames: -8..+6 and +8..-6). The run is rebuilt from the design: the body as Codex's idle (its bob kept: up a row in
frames 2, 3, 6, 7), the far leg (image left, rig/near_leg) drawn first and the body over it (the cape and the staff in
front of it), the near leg (image right, rig/far_leg) last, both in the design's own colours; RUN gives each leg's
offset (dx, lift) per frame: the planted foot slides back, the lifted one comes forward, LEG_AMP columns either way, so
the feet swap front and back; a leg's rows shear from the hip (the top HIP_SHARE of the offset) to the foot (all of it).
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import design_viktor as D  # noqa: E402

CODEX = os.path.join(REPO, "assets", "source", "viktor", "codex_strips")
NATIVE = os.path.join(REPO, "assets", "source", "native")
RIG = os.path.join(CODEX, "rig")
PIVOT = (64, 88)                 # the design's standing point on its 128x128 canvas
LEG_AMP, HIP_SHARE = 6, 0.4
# per frame: (near dx, near lift), (far dx, far lift); body dy (Codex's bob)
RUN = [((6, 0), (-6, 0), 0), ((3, 0), (-3, 1), -1), ((0, 0), (0, 2), -1), ((-3, 0), (3, 1), 0),
       ((-6, 0), (6, 0), 0), ((-3, 1), (3, 0), -1), ((0, 2), (0, 0), -1), ((3, 1), (-3, 0), 0)]
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
Z = 8


def old_piece():
    """The design's lower shaft before fix 1 (Codex's frames were built from that design): (piece, opaque mask)."""
    a = np.array(Image.open(D.lp(D.SRC)).convert("RGBA"))
    c = a[D.Y0:D.Y0 + D.H, D.X0:D.X0 + D.W].copy()
    D.staff(c)
    a0, b0 = D.KINK_COLS
    rows = list(D.KINK_ROWS)
    return c[rows[0]:rows[-1] + 1, a0:b0]


def fix_upright(strip, piece):
    """Every exact match of the piece in the strip (1x): the shaft moved one column left, as design_viktor.kink."""
    h, w = piece.shape[:2]
    H, W = strip.shape[:2]
    hits = 0
    for y in range(H - h + 1):
        for x in range(1, W - w):
            if not np.array_equal(strip[y:y + h, x:x + w], piece):
                continue
            for r in range(y, y + h):
                old = strip[r].copy()
                strip[r, x - 1:x + w - 1] = old[x:x + w]
                right = old[x + w]
                if right[3] and tuple(int(v) for v in right[:3]) in D.CAPE:
                    strip[r, x + w - 1] = right
                elif right[3]:
                    strip[r, x + w - 1, :3], strip[r, x + w - 1, 3] = D.INK, 255
                else:
                    strip[r, x + w - 1] = 0
            hits += 1
    return hits


def fix(strip, piece):
    """fix_upright in the strip as it is, turned a quarter both ways and upside down."""
    hits = 0
    for k in (0, 1, 3, 2):
        t = np.ascontiguousarray(np.rot90(strip, k))
        n = fix_upright(t, piece)
        if n:
            strip[...] = np.rot90(t, -k)
            hits += n
    return hits


def leg(canvas, part, dx, lift):
    """Draw the leg (its pixels on the design canvas) sheared from the hip: row r of the leg moves dx x (HIP_SHARE +
    (1 - HIP_SHARE) x depth) columns and the whole leg `lift` rows up."""
    ys, xs = np.nonzero(part[..., 3] > 0)
    top, bot = ys.min(), ys.max()
    for y, x in zip(ys, xs):
        k = HIP_SHARE + (1 - HIP_SHARE) * (y - top) / max(1, bot - top)
        canvas[y - lift, x + int(round(dx * k))] = part[y, x]


def run_frames(design):
    near = np.array(Image.open(D.lp(os.path.join(RIG, "far_leg_1x.png"))).convert("RGBA"))   # Codex's names swapped
    far = np.array(Image.open(D.lp(os.path.join(RIG, "near_leg_1x.png"))).convert("RGBA"))
    body = design.copy()
    body[(near[..., 3] > 0) | (far[..., 3] > 0)] = 0
    out = []
    for (ndx, nl), (fdx, fl), bob in RUN:
        c = np.zeros_like(design)
        leg(c, far, fdx, fl)
        b = np.roll(body, bob, axis=0)
        m = b[..., 3] > 0
        c[m] = b[m]
        leg(c, near, ndx, nl)
        out.append(c)
    return out


def place_run(strip, cells, frames):
    """Each rebuilt frame into its cell, the design's pivot on the cell's pivot."""
    cw, ch = cells["cell"]
    cols = strip.shape[1] // cw
    strip[...] = 0
    for i, (fr, f) in enumerate(zip(cells["tags"]["run"], frames)):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        px, py = fr["pivot"]
        ys, xs = np.nonzero(f[..., 3] > 0)
        strip[cy + py - PIVOT[1] + ys, cx + px - PIVOT[0] + xs] = f[ys, xs]


def main():
    piece = old_piece()
    for tag in TAGS:
        big = np.array(Image.open(D.lp(os.path.join(CODEX, f"viktor_{tag}.png"))).convert("RGBA"))
        one = big[Z // 2::Z, Z // 2::Z].copy()
        if tag == "run":
            design = np.array(Image.open(D.lp(D.OUT)).convert("RGBA"))
            with open(os.path.join(CODEX, "viktor_cells.json"), encoding="utf-8") as f:
                place_run(one, json.load(f), run_frames(design))
        # the rebuilt run comes from the fixed design: its shaft matches the old piece too (the column left behind takes
        # the same cape colour), and a second pass would move it again
        n = 0 if tag == "run" else fix(one, piece)
        Image.fromarray(np.repeat(np.repeat(one, Z, 0), Z, 1)).save(D.lp(os.path.join(NATIVE, f"viktor_{tag}.png")))
        print(f"{tag:9s} shaft fixed in {n} frame(s)")
    shutil.copyfile(os.path.join(CODEX, "viktor_cells.json"), os.path.join(NATIVE, "viktor_cells.json"))


if __name__ == "__main__":
    main()
