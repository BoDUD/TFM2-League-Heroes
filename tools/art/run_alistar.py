#!/usr/bin/env python3
"""Alistar's run: the design's own upper body on Codex's two legs -> assets/source/native/alistar_run.png (8x, the
run cells of alistar_cells.json: 8 frames, standing point (60, 70), 125 ms).

    python tools/art/run_alistar.py

The user, on the first run built from Codex's draft: 「牛头走路没有交叉步」「单脚走路的」「走路和待机的体型不一样？？走路还会变大？？」.
The redo (assets/source/alistar/RUN_REDO.md) gave Codex the design minus its legs in every cell and asked for the two
legs only; it delivered them as a GPT leg drawing (codex_run/legs_redraw.png) placed per leg on hip and hoof guides by
its codex_run/rebuild_run.py. This rebuilds those same leg layers and composes, back to front: the far leg, the far
fist, the near leg, the upper body (the hump, head, both shackled arms, the loincloth), a row lower on the contacts
(BOB). The far fist - the purple block under the far shackle, in front of the far thigh - sat inside the far leg's
box of split(), so the redo's base and Codex's run lost it (「GPT把手弄没了」); it is put back from the design. Then the
outline is closed, the slits shut between the legs filled, and the outline spurs it leaves dropped.
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "alistar_native.png")
OUT = os.path.join(NATIVE, "alistar_run.png")
LEGS_PNG = os.path.join(ROOT, "assets", "source", "alistar", "codex_run", "legs_redraw.png")
PIVOT = (64, 88)                  # the design canvas's standing point; its soles on row 99
SOLE = 99
OUTLINE = (0x12, 0x03, 0x19)
CHAIN = {(0x44, 0x3A, 0x3F), (0xA8, 0x82, 0x6E)}                                 # the far shackle's chain
CLOTH = {(0x87, 0x3E, 0x28), (0xC8, 0x67, 0x2F), (0xF5, 0xB7, 0x43), (0xFB, 0xD5, 0x9B), (0x42, 0x17, 0x14)}
# the legs on the design canvas: (rows, columns) boxes; the hooves (rows 95-99) whole, above them the fur only
LEGS = {"far": dict(top=86, x0=44, x1=60, hip=(54.0, 87.0), chain_x=49),
        "near": dict(top=86, x0=60, x1=74, hip=(66.0, 87.0), chain_x=None)}
HOOF_ROW = 95
FIST_ROWS = (86, 93)              # the far box's rows that are the far fist
CELL = (128, 96)
CELL_PIVOT = (60, 70)             # the soles on row 81
BOB = [1, 0, 0, 0, 1, 0, 0, 0]    # the body a row lower on each contact
# Codex's leg placement (codex_run/rebuild_run.py): the leg colours it snaps to, which drawn leg each frame uses
# (cell of legs_redraw.png, its left or right leg), and the targets (near hoof x, lift, far hoof x, lift)
LEGCOLS = np.array([(18, 3, 25), (21, 11, 75), (59, 24, 136), (85, 38, 195), (115, 61, 245), (154, 99, 243),
                    (66, 23, 20), (135, 62, 40)])
NEAR_SRC = [(0, "right"), (1, "right"), (0, "right"), (3, "left"), (4, "left"), (5, "left"), (4, "left"), (7, "right")]
FAR_SRC = [(0, "left"), (1, "left"), (3, "right"), (3, "right"), (4, "right"), (5, "right"), (7, "right"), (7, "left")]
TARGETS = [(62.5, 0, 52, 1), (60, 0, 53.5, 3), (57.5, 0, 57, 3), (55, 0, 60, 1), (53, 1, 61.5, 0), (54.5, 3, 59, 0),
           (58, 3, 56.5, 0), (61, 1, 54, 0)]
HIP_X = {"far": 56, "near": 59}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def col(p):
    return tuple(int(v) for v in p[:3])


def split(des):
    """The two legs' masks and the upper body (the design without them)."""
    op = des[..., 3] > 0
    masks = {}
    for name, L in LEGS.items():
        m = np.zeros(op.shape, bool)
        for y in range(L["top"], SOLE + 1):
            for x in range(L["x0"], L["x1"]):
                if not op[y, x]:
                    continue
                c = col(des[y, x])
                if y >= HOOF_ROW:
                    m[y, x] = True
                    continue
                if c in CLOTH or (L["chain_x"] is not None and x < L["chain_x"] and c in CHAIN | {OUTLINE}):
                    continue
                if c in CHAIN:
                    continue
                m[y, x] = True
        masks[name] = m
    # a pixel claimed by both (the shared column) goes to the near leg
    masks["far"] &= ~masks["near"]
    upper = des.copy()
    for m in masks.values():
        upper[m] = 0
    return masks, upper


def drawn_leg(sheet, i, side):
    """One leg of legs_redraw.png's cell i, read on its 32-square grid and snapped to the leg colours."""
    w, h = sheet.size
    x, y = i % 4, i // 4
    cell = sheet.crop((round(x * w / 4), round(y * h / 2), round((x + 1) * w / 4), round((y + 1) * h / 2)))
    a = np.array(cell.resize((32, 32), Image.Resampling.NEAREST)).astype(float)
    green = (a[..., 1] > a[..., 0] * 1.3 + 10) & (a[..., 1] > a[..., 2] * 1.3 + 10)
    pale = (a.min(axis=2) > 175) | ((a[..., 0] > 210) & (a[..., 1] > 110) & (a[..., 2] > 110))
    dist = ((a[:, :, None, :] - LEGCOLS[None, None]) ** 2).sum(axis=3)
    b = np.zeros((32, 32, 4), np.uint8)
    b[..., :3] = LEGCOLS[dist.argmin(axis=2)]
    b[..., 3] = np.where(green | pale, 0, 255)
    crop = b[11:24, 1:14] if side == "left" else b[11:24, 17:29]
    ys, xs = np.nonzero(crop[..., 3])
    return Image.fromarray(crop[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def leg_layer(sheet, source, hx, tx, lift):
    """The leg squeezed to 7 squares and hip-to-hoof rows, its top centred on the hip, its hoof on the target."""
    top, foot = CELL_PIVOT[1] - 2, CELL_PIVOT[1] + 11 - lift
    hh = foot - top + 1
    leg = np.array(drawn_leg(sheet, *source).resize((7, hh), Image.Resampling.NEAREST))
    mask = leg[..., 3] > 0
    bx, tx_ = np.nonzero(mask[-1])[0], np.nonzero(mask[0])[0]
    bc = (bx.min() + bx.max()) / 2 if len(bx) else 3
    tc = (tx_.min() + tx_.max()) / 2 if len(tx_) else 3
    layer = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    for row in range(hh):
        t = row / max(1, hh - 1)
        shift = round((hx - tc) * (1 - t) + (tx - bc) * t)
        for c in np.nonzero(mask[row])[0]:
            if 0 <= shift + c < CELL[0]:
                layer[top + row, shift + c] = leg[row, c]
    for y, x in zip(*np.nonzero(layer[..., 3])):                       # lone squares of the drawing's backdrop
        if np.count_nonzero(layer[max(0, y - 1):y + 2, max(0, x - 1):x + 2, 3]) == 1:
            layer[y, x] = 0
    return layer


def to_cell(img, bob):
    out = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    dx, dy = CELL_PIVOT[0] - PIVOT[0], CELL_PIVOT[1] - PIVOT[1] + bob
    for y, x in zip(*np.nonzero(img[..., 3])):
        if 0 <= y + dy < CELL[1] and 0 <= x + dx < CELL[0]:
            out[y + dy, x + dx] = img[y, x]
    return out


def over(can, layer):
    m = layer[..., 3] > 0
    can[m] = layer[m]


def holes(op):
    """Transparent squares the outside cannot reach."""
    H, W = op.shape
    out = np.zeros_like(op)
    q = deque((y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and not op[y, x])
    for p in q:
        out[p] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < H and 0 <= nx < W and not op[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                q.append((ny, nx))
    return list(zip(*np.nonzero(~op & ~out)))


def frame(sheet, fist, upper, k):
    nx, nl, fx, fl = TARGETS[k]
    can = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    over(can, leg_layer(sheet, FAR_SRC[k], HIP_X["far"], fx, fl))
    over(can, to_cell(fist, BOB[k]))
    over(can, leg_layer(sheet, NEAR_SRC[k], HIP_X["near"], nx, nl))
    over(can, to_cell(upper, BOB[k]))
    pad = np.pad(can, ((2, 2), (2, 2), (0, 0)))
    pad, _, _ = G.complete_outline(pad, color=OUTLINE, feet=CELL_PIVOT[1] + 13)
    can = pad[2:-2, 2:-2].copy()
    can[CELL_PIVOT[1] + 12:] = 0
    for y, x in holes(can[..., 3] > 0):                                # slits shut between the legs and the fist
        can[y, x] = (*OUTLINE, 255)
    op = can[..., 3] > 0
    for y, x in zip(*np.nonzero(op[CELL_PIVOT[1] - 6:])):              # outline spurs the closing pass left
        y += CELL_PIVOT[1] - 6
        if op[y - 1:y + 2, x - 1:x + 2].sum() <= 2 and col(can[y, x]) == OUTLINE:
            can[y, x] = 0
    return can


def build():
    des = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[4::8, 4::8].copy()
    masks, upper = split(des)
    fist = np.zeros_like(des)
    fm = masks["far"].copy()
    fm[:FIST_ROWS[0]] = False
    fm[FIST_ROWS[1] + 1:] = False
    fist[fm] = des[fm]
    sheet = Image.open(lp(LEGS_PNG)).convert("RGB")
    strip = np.zeros((2 * CELL[1], 4 * CELL[0], 4), np.uint8)
    for k in range(8):
        strip[(k // 4) * CELL[1]:(k // 4 + 1) * CELL[1], (k % 4) * CELL[0]:(k % 4 + 1) * CELL[0]] = frame(sheet, fist, upper, k)
    return strip


def main():
    strip = build()
    Image.fromarray(strip).resize((strip.shape[1] * 8, strip.shape[0] * 8), Image.NEAREST).save(lp(OUT))
    print("near - far hoof x per frame:", [t[0] - t[2] for t in TARGETS])


if __name__ == "__main__":
    main()
