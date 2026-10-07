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
front of it), the near leg (image right, rig/far_leg) last, the far one a shade darker (DARKER); each leg follows CYCLE
(rig_gwen.bent: knee and ankle columns, rows lifted - the planted foot slides back, the swinging one comes forward
lifted; the other leg half a cycle later), drawn in toward the other by HIP_IN so the swinging far leg crosses in front
of the near one. The first rebuild (feet 6 columns either way) read as a crab: 「走路和螃蟹一样？」; league_gwen's kick
cycle never crossed: 「走路没有明显的交叉步感觉」.
The run now comes from Codex's leg swap (RUN_SRC: League's walk redrawn as his legs under the design's upper body, the
user: 「不行啊 还是看不出」 at the rebuilds).
Fix 3 (the user at R's frames: 「这里的法杖歪修了吗？」): Codex turned the near arm with the staff -10 / -15 degrees in R's
frames 2-4 (nearest-neighbour, about the shoulder STAFF_TURN_CENTRE - found by matching its pixels exactly), and the
one-square shaft came out in uneven steps; League holds the staff upright in R. Those pixels are taken out, the
part is put back unturned with the same shift (the shaft's kink fixed), and what neither covers takes its neighbours'
commonest colour (or stays clear) - after the design's legs and torso go in under it where they stood (Codex's turned
staff had covered the far leg, which it never drew: 「像素消失」).
"""
import json
import math
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
LEG_TOP, KNEE_ROW, BOOT_ROW, SOLES = 88, 93, 96, 99
# one leg's cycle: (knee columns, ankle columns from where it stands, + = forward = image right; rows lifted): the
# planted foot slides back 3 -> -3, the swinging one comes forward lifted; the other leg half a cycle later. HIP_IN
# draws the legs toward each other (nothing at the hip, all of it from the knee down) so the swinging far leg passes
# in front of the near one: a crossing step. The first rebuild slid the feet 6 columns either way without it, a
# straddle 20 columns wide (「走路和螃蟹一样？」); league_gwen's kick cycle after it never crossed (「走路没有明显的
# 交叉步感觉」)
CYCLE = [(1, 3, 0), (0, 1, 0), (0, -1, 0), (-1, -3, 0), (-1, -2, 1), (0, 0, 2), (1, 2, 2), (1, 3, 1)]
HIP_IN = {"near": -2, "far": 2}
BOB = [0, -1, -1, 0, 0, -1, -1, 0]   # Codex's bob
# the far leg one shade darker (the step-2 prompt's rule), so the crossed legs read apart
DARKER = {"#A3AAD6": "#7E86B8", "#7E86B8": "#5B6194", "#5B6194": "#3E4270", "#3E4270": "#3A2C40",
          "#FFF1A0": "#F7D04A", "#F7D04A": "#D49A1E", "#D49A1E": "#8A5A10", "#FF8A1E": "#C8400A",
          "#6F86AE": "#5B6194"}
STAFF_TURN_CENTRE = (61.0, 80.0)   # canvas coordinates of the design
UPRIGHT = {"ult"}                  # strips whose turned staff goes upright
# the run Codex redrew from League's walk (pack_viktor_run.py, RUN_SWAP.md): its legs over the design's upper body; the
# rebuilds from the design's two legs above (CYCLE) stay for reference
RUN_SRC = os.path.join(REPO, "assets", "source", "viktor", "codex_run", "viktor-run", "viktor_run.png")
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


def bent(part, knee, ankle, lift, hip_in=0):
    """The leg's own rows moved whole (rig_gwen.bent): row by row along hip -> knee -> ankle, the foot rows at the
    ankle, all lifted; hip_in from nothing at the hip to all of it at the knee."""
    out = np.zeros_like(part)
    for y in range(LEG_TOP, SOLES + 1):
        inward = hip_in * min(1.0, (y - LEG_TOP) / (KNEE_ROW - LEG_TOP))
        if y <= KNEE_ROW:
            dx = knee * (y - LEG_TOP) / (KNEE_ROW - LEG_TOP)
        elif y < BOOT_ROW:
            dx = knee + (ankle - knee) * (y - KNEE_ROW) / (BOOT_ROW - KNEE_ROW)
        else:
            dx = ankle
        dx = int(np.floor(dx + inward + 0.5))
        row = np.roll(part[y], dx, axis=0)
        m = row[:, 3] > 0
        out[y - lift][m] = row[m]
    return out


def darker(part):
    out = part.copy()
    for a, b in DARKER.items():
        m = (part[..., 3] > 0) & (part[..., :3] == D.hx(a)).all(-1)
        out[m, :3] = D.hx(b)
    return out


def legs():
    near = np.array(Image.open(D.lp(os.path.join(RIG, "far_leg_1x.png"))).convert("RGBA"))   # Codex's names swapped
    far = np.array(Image.open(D.lp(os.path.join(RIG, "near_leg_1x.png"))).convert("RGBA"))
    return near, far


def run_frames(design):
    near, far = legs()
    body = design.copy()
    body[(near[..., 3] > 0) | (far[..., 3] > 0)] = 0
    far = darker(far)
    out = []
    for k in range(8):
        c = bent(far, *CYCLE[(k + 4) % 8], hip_in=HIP_IN["far"])
        b = np.roll(body, BOB[k], axis=0)
        m = b[..., 3] > 0
        c[m] = b[m]
        n = bent(near, *CYCLE[k], hip_in=HIP_IN["near"])
        m = n[..., 3] > 0
        c[m] = n[m]
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


def turned(part, ang, centre):
    """Codex's rotation: each target pixel samples the part at R(-a)(t - c) + c, nearest."""
    a = math.radians(ang)
    cx, cy = centre
    ty, tx = np.mgrid[0:128, 0:128]
    sx = np.floor(np.cos(a) * (tx - cx) + np.sin(a) * (ty - cy) + cx + 0.5).astype(int)
    sy = np.floor(-np.sin(a) * (tx - cx) + np.cos(a) * (ty - cy) + cy + 0.5).astype(int)
    ok = (sx >= 0) & (sx < 128) & (sy >= 0) & (sy < 128)
    out = part[sy.clip(0, 127), sx.clip(0, 127)].copy()
    out[~ok] = 0
    return out


def kinked_part(part):
    """The rig's near arm and staff with design_viktor's kink fix (step 1b) on its shaft."""
    c = part[D.Y0:D.Y0 + D.H, D.X0:D.X0 + D.W].copy()
    D.kink(c)
    out = part.copy()
    out[D.Y0:D.Y0 + D.H, D.X0:D.X0 + D.W] = c
    return out


def upright(strip, tag, manifest):
    part = np.array(Image.open(D.lp(os.path.join(RIG, "near_arm_staff_1x.png"))).convert("RGBA"))
    straight = kinked_part(part)
    torso = np.array(Image.open(D.lp(os.path.join(RIG, "torso_1x.png"))).convert("RGBA"))
    cw, ch = manifest["cell_1x"]
    cols = strip.shape[1] // cw
    n = 0
    for i, f in enumerate(manifest["animations"][tag]["frames"]):
        rig = f["rig"]
        ang = rig["near_arm_staff_angle_deg"]
        if not ang:
            continue
        cx, cy = (i % cols) * cw, (i // cols) * ch
        px, py = f["pivot_cell_1x"]
        ox = cx + px - PIVOT[0] + rig["whole_shift"][0] + rig["near_arm_staff_shift"][0]
        oy = cy + py - PIVOT[1] + rig["whole_shift"][1] + rig["near_arm_staff_shift"][1]
        old = turned(part, ang, STAFF_TURN_CENTRE)
        ys, xs = np.nonzero(old[..., 3] > 0)
        hole = np.zeros(strip.shape[:2], bool)
        for y, x in zip(ys + oy, xs + ox):
            hole[y, x] = True
        for (y, x), p in zip(zip(ys + oy, xs + ox), old[ys, xs]):
            if np.array_equal(strip[y, x], p):
                strip[y, x] = 0
        # under it: the design's legs and torso where they stood (Codex drew the turned staff over the far leg)
        wx = cx + px - PIVOT[0] + rig["whole_shift"][0]
        wy = cy + py - PIVOT[1] + rig["whole_shift"][1]
        for under in (*legs(), torso):
            ys, xs = np.nonzero(under[..., 3] > 0)
            m = hole[ys + wy, xs + wx] & (strip[ys + wy, xs + wx, 3] == 0)
            strip[ys[m] + wy, xs[m] + wx] = under[ys[m], xs[m]]
        ys, xs = np.nonzero(straight[..., 3] > 0)
        strip[ys + oy, xs + ox] = straight[ys, xs]
        hole[ys + oy, xs + ox] = False
        hole &= strip[..., 3] == 0
        for _ in range(3):           # the uncovered squares: their neighbours' commonest colour, else clear
            fill = []
            for y, x in zip(*np.nonzero(hole)):
                nb = [tuple(strip[y + dy, x + dx]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
                      if not hole[y + dy, x + dx]]
                op = [q for q in nb if q[3]]
                if len(op) >= 3:
                    fill.append((y, x, max(sorted(set(op)), key=op.count)))
            for y, x, c in fill:
                strip[y, x] = c
                hole[y, x] = False
        n += 1
    return n


def main():
    piece = old_piece()
    for tag in TAGS:
        big = np.array(Image.open(D.lp(os.path.join(CODEX, f"viktor_{tag}.png"))).convert("RGBA"))
        one = big[Z // 2::Z, Z // 2::Z].copy()
        if tag == "run" and os.path.exists(RUN_SRC):
            one = np.array(Image.open(D.lp(RUN_SRC)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
        elif tag == "run":
            design = np.array(Image.open(D.lp(D.OUT)).convert("RGBA"))
            with open(os.path.join(CODEX, "viktor_cells.json"), encoding="utf-8") as f:
                place_run(one, json.load(f), run_frames(design))
        # the rebuilt run comes from the fixed design: its shaft matches the old piece too (the column left behind takes
        # the same cape colour), and a second pass would move it again
        n = 0 if tag == "run" else fix(one, piece)
        if tag in UPRIGHT:
            with open(os.path.join(CODEX, "manifest.json"), encoding="utf-8") as f:
                n3 = upright(one, tag, json.load(f))
            print(f"{tag:9s} staff upright in {n3} frame(s)")
        Image.fromarray(np.repeat(np.repeat(one, Z, 0), Z, 1)).save(D.lp(os.path.join(NATIVE, f"viktor_{tag}.png")))
        print(f"{tag:9s} shaft fixed in {n} frame(s)")
    shutil.copyfile(os.path.join(CODEX, "viktor_cells.json"), os.path.join(NATIVE, "viktor_cells.json"))


if __name__ == "__main__":
    main()
