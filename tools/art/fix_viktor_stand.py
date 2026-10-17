#!/usr/bin/env python3
"""Viktor's standing legs in every action as in his walk (the user, 2026-10-10, at the ban/pick card after the walk's
legs were redone: 「所有动作都统一了吗 脚部 为啥BP界面还这样的」).

The walk (fix_viktor_run.py, viktor_walk_legs.py) stands on the near leg and its mirror image in the far lane - toes
outward, the cape's inner edge over the far thigh's outer side (the user's picks B and C). Every other strip still had
the design's far leg: a stub behind the lining. Standing still, the walk's legs are fix_viktor_run.legs_frame with both
legs at rest (STAND). In each frame where the design's near leg stands whole (found by an exact match of its pixels -
the idle, attack, Q, W, E, R, hit, the first death frame; a hop in R lifts it), every square the standing legs change
is written at that offset:

- where the frame still shows the design's own square there (with fix_viktor_leg.py's rear shin), the standing
  legs' square;
- where the frame is empty there (the staff carried away from the foot), the standing legs' square as they stand
  without the staff in front (else the far boot came out in loose bits round the hole the staff left);
- anything else (an arm, the staff, an effect over the legs) stays as it is.
An outline square written there that touches no colour (the cap the bare legs put under the staff's cut end) is
cleared again.

The idle breathes here too, on the same standing legs (BREATH, 8 x 140 ms as idle_breathe's recipe): the body and
the hip plates sink 0-0-1-2-2-2-1-0 rows over them as in the walk's landing (a thigh row less per row sunk), the staff's
lower part planted. import_native's shared breath (BREATHE_SKIP now) cut a shin row and leant the body a column over
the new legs: an orange square in the far boot, a pinhole beside the staff.

The run (its own legs) and the falling death (no standing leg) are left alone. Run after fix_viktor_strips.py and
fix_viktor_run.py, before tools/art/import_native.py:

    python tools/art/fix_viktor_stand.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fix_viktor_leg as L  # noqa: E402
import fix_viktor_run as R  # noqa: E402

S = R.S
Z = R.Z
STAND = ((0, 0, 0), (0, 0, 0), 0)     # near pose, far pose, rows sunk
SEARCH = ((-30, -20), (-22, -2))      # design -> cell offsets (rows, columns) to look for the near leg in
IDLE_AT = (-25, -13)                  # design -> idle cell: fix_viktor_leg.EDITS are in idle cell coordinates
BREATH = [0, 0, 1, 2, 2, 2, 1, 0]     # rows the body is down per idle frame
BREATH_MS = 140


def find(cell, part):
    """The (rows, columns) offset at which every square of `part` stands in `cell`, or None."""
    ys, xs = np.nonzero(part[..., 3])
    pat = part[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    m = pat[..., 3] > 0
    h, w = pat.shape[:2]
    for dy in range(*SEARCH[0]):
        for dx in range(*SEARCH[1]):
            y, x = ys.min() + dy, xs.min() + dx
            if 0 <= y and y + h <= cell.shape[0] and 0 <= x and x + w <= cell.shape[1] and \
                    np.array_equal(cell[y:y + h, x:x + w][m], pat[m]):
                return dy, dx
    return None


def main():
    design = np.array(Image.open(S.D.lp(S.D.OUT)).convert("RGBA"))
    old = design.copy()                              # the design as the strips carry it: the rear shin coloured in
    for r, c, col in L.EDITS:
        old[r - IDLE_AT[0], c - IDLE_AT[1]] = (*col, 255)
    parts = R.layers(design)
    stand = R.legs_frame(parts, *STAND)
    bare = R.legs_frame(parts[:2] + (np.zeros_like(parts[2]),) + parts[3:], *STAND)     # no staff in front
    changed = np.argwhere(((stand != old) | (bare != old)).any(-1))
    near = parts[3]
    with open(R.lp(os.path.join(R.NATIVE, "viktor_cells.json")), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    idle = [dict(cells["tags"]["idle"][0], ms=BREATH_MS) for _ in BREATH]
    cells["tags"]["idle"] = idle
    a = np.zeros((2 * ch, 4 * cw, 4), np.uint8)                   # import_native.layout(8): 4 x 2 cells
    for i, b in enumerate(BREATH):
        f = R.legs_frame(parts, *STAND[:2], b)
        px, py = idle[i]["pivot"]
        ys, xs = np.nonzero(f[..., 3])
        a[(i // 4) * ch + py - S.PIVOT[1] + ys, (i % 4) * cw + px - S.PIVOT[0] + xs] = f[ys, xs]
    Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST).save(
        R.lp(os.path.join(R.NATIVE, "viktor_idle.png")))
    with open(R.lp(os.path.join(R.NATIVE, "viktor_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(cells, indent=1, ensure_ascii=False))
    print(f"idle: breathing on the standing legs, body down {BREATH}")
    for tag in cells["tags"]:
        if tag in ("run", "idle"):
            continue
        a = R.load(f"viktor_{tag}.png")
        cols = a.shape[1] // cw
        done = []
        for i in range(len(cells["tags"][tag])):
            cell = a[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw]
            at = find(cell, near)
            if at is None:
                done.append("-")
                continue
            n = 0
            wrote = []
            for y, x in changed:
                Y, X = y + at[0], x + at[1]
                if not (0 <= Y < ch and 0 <= X < cw):
                    continue
                if np.array_equal(cell[Y, X], old[y, x]):
                    new = stand[y, x]
                elif not cell[Y, X, 3]:
                    new = bare[y, x]
                else:
                    continue
                if not np.array_equal(cell[Y, X], new):
                    cell[Y, X] = new
                    wrote.append((Y, X))
                    n += 1
            for Y, X in wrote:
                if cell[Y, X, 3] and tuple(int(v) for v in cell[Y, X, :3]) == R.OUT:
                    win = cell[max(0, Y - 1):Y + 2, max(0, X - 1):X + 2]
                    if not ((win[..., 3] > 0) & (win[..., :3] != np.array(R.OUT, np.uint8)).any(-1)).any():
                        cell[Y, X] = 0
            done.append(str(n))
        Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST).save(
            R.lp(os.path.join(R.NATIVE, f"viktor_{tag}.png")))
        print(f"{tag}: squares changed per frame {' '.join(done)} (- = no standing leg)")


if __name__ == "__main__":
    main()
