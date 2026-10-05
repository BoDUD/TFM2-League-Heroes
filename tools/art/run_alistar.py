#!/usr/bin/env python3
"""Alistar's run: the design's own upper body striding on full-width single legs -> assets/source/native/alistar_run.png
(8x, the run cells of alistar_cells.json: 8 frames, standing point (60, 70), 125 ms).

    python tools/art/run_alistar.py

The user on earlier runs: 「牛头走路没有交叉步」「单脚走路的」「走路和待机的体型不一样」, then on Codex's leg redo 「GPT把手弄没了」,
「每次做到腿交叉步都做不好」「不要小碎步」. What went wrong before: the base sent to Codex had lost the far fist (it sat inside
split()'s far-leg box), Codex's rebuild squeezed GPT's legs to 7 squares and sheared them hip to hoof (sticks, hooves 4-6
wide against the idle's 10), and GPT's own 8 frames keep each hoof on its side (the "X" frames only bring the knees
together) - the hooves never pass, which reads as stepping on the spot.

Here GPT's leg drawing (codex_run/legs_redraw.png) is only a library of single legs, read on its own grid at full width
(regrid, ~13.9 px a square) and snapped to the design's leg colours; the upright pose is the design's own near leg:
  F   planted ahead (slant +4)          B   planted behind (-3.5)        V   upright (the design's leg)
  Bh  heel up, behind (-3, 12 rows)     S1  swinging through (+2.5, 11 rows)
Each hoof follows a real stride (CYCLE): planted ahead, sliding back under the body, heel up, toe off, lifted through,
reaching ahead; the two legs half a cycle apart from hips one square apart under the loincloth, so the hooves pass each
other twice a cycle (near minus far hoof x: +8 +1 -5 -6 -6 +1 +7 +8). Back to front: the far leg one shade darker (the
crossing reads at game size, as Taric's run), the far fist, the near leg, the upper body (hump, head, both shackled arms,
the loincloth) a row lower on the contacts (BOB). Then the outline is closed, slits between the legs shut, and outline
squares with no colour beside them dropped. The legs keep the idle's width (7-8 squares, hooves 9-10).
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
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
CELL_SOLE = CELL_PIVOT[1] + 11
BOB = [1, 0, 0, 0, 1, 0, 0, 0]    # the body a row lower on each contact
SQUARE = 13.86                    # legs_redraw.png pixels per square (its 4 x 2 cells are 32 squares each way)
LIB = {"F": (0, 1), "B": (3, 0), "Bh": (0, 0), "S1": (4, 1)}    # pose: (cell of legs_redraw.png, its left 0 / right 1 leg)
HIPS = {"near": CELL_PIVOT[0], "far": CELL_PIVOT[0] - 1}
# per phase (0 = the hoof planted ahead): the pose and the cell row of its top (rows above 68 hide under the belly)
CYCLE = [("F", 68), ("V", 68), ("B", 68), ("Bh", 68), ("Bh", 66), ("V", 65), ("S1", 67), ("F", 67)]
PHASE = {"near": 0, "far": 4}
DARKER = {(0x9A, 0x63, 0xF3): (0x73, 0x3D, 0xF5), (0x73, 0x3D, 0xF5): (0x55, 0x26, 0xC3),
          (0x55, 0x26, 0xC3): (0x3B, 0x18, 0x88), (0x3B, 0x18, 0x88): (0x15, 0x0B, 0x4B),
          (0x87, 0x3E, 0x28): (0x42, 0x17, 0x14)}


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


def pieces(op):
    """8-connected labels."""
    lab = np.zeros(op.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
    return lab, n


def drawn_legs(sheet, k, cols):
    """Cell k of legs_redraw.png: the legs under the guide's white body box, above its pink ground, read on their own
    grid, snapped to the leg colours, without the claw and chain bits that do not reach the ground."""
    im = sheet
    H, W = im.shape[:2]
    c = im[round((k // 4) * H / 2):round((k // 4 + 1) * H / 2), round((k % 4) * W / 4):round((k % 4 + 1) * W / 4)]
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    green = (g > r * 1.3 + 10) & (g > b * 1.3 + 10)
    white = (c.min(-1) > 200) & (np.abs(r - b) < 15)
    pink = (r > 215) & (g > 180) & (b > 180) & (r - b >= 15)
    top = np.nonzero(white[:250].sum(1) > 60)[0].max() + 1
    gnd = np.nonzero(pink.sum(1) > 200)[0].min()
    leg = ~(green | white | pink)
    leg[:top] = False
    leg[gnd + 40:] = False
    a = np.zeros(c.shape[:2] + (4,), np.uint8)
    a[..., :3] = c
    a[..., 3] = leg * 255
    grid, _, _ = RG.regrid(a, SQUARE)
    op = grid[..., 3] > 127
    lab, n = pieces(op)
    keep = np.zeros_like(op)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() >= 25 and np.nonzero(m)[0].max() >= op.shape[0] - 4:
            keep |= m
    out = np.zeros_like(grid)
    d = ((grid[..., None, :3].astype(int) - cols[None, None]) ** 2).sum(-1)
    out[..., :3] = cols[d.argmin(-1)]
    out[..., 3] = keep * 255
    return out


def crop(s):
    ys, xs = np.nonzero(s[..., 3])
    return s[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def library(des, masks):
    cols = np.array(sorted({col(des[y, x]) for y, x in zip(*np.nonzero(masks["far"] | masks["near"]))}))
    sheet = np.asarray(Image.open(lp(LEGS_PNG)).convert("RGB")).astype(int)
    lib = {}
    for name, (k, side) in LIB.items():
        g = drawn_legs(sheet, k, cols)
        lab, n = pieces(g[..., 3] > 0)
        order = sorted(range(1, n + 1), key=lambda i: np.nonzero(lab == i)[1].mean())
        s = np.zeros_like(g)
        m = lab == order[side]
        s[m] = g[m]
        lib[name] = crop(s)
    s = np.zeros_like(des)
    s[masks["near"]] = des[masks["near"]]
    lib["V"] = crop(s)
    return lib


def to_cell(img, bob):
    out = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    dx, dy = CELL_PIVOT[0] - PIVOT[0], CELL_PIVOT[1] - PIVOT[1] + bob
    for y, x in zip(*np.nonzero(img[..., 3])):
        if 0 <= y + dy < CELL[1] and 0 <= x + dx < CELL[0]:
            out[y + dy, x + dx] = img[y, x]
    return out


def place(s, hip, top, dark=False):
    """A leg with its top 4 rows centred on the hip."""
    L = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    X = int(round(hip - np.nonzero(s[:4, :, 3])[1].mean()))
    m = s[..., 3] > 0
    L[top:top + s.shape[0], X:X + s.shape[1]][m] = s[m]
    if dark:
        for y, x in zip(*np.nonzero(L[..., 3])):
            c = DARKER.get(col(L[y, x]))
            if c:
                L[y, x, :3] = c
    return L


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


def frame(lib, fist, upper, k):
    can = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    legs = {}
    for name in ("far", "near"):
        pose, top = CYCLE[(k + PHASE[name]) % 8]
        legs[name] = place(lib[pose], HIPS[name], top, dark=name == "far")
    over(can, legs["far"])
    over(can, to_cell(fist, BOB[k]))
    over(can, legs["near"])
    over(can, to_cell(upper, BOB[k]))
    pad = np.pad(can, ((2, 2), (2, 2), (0, 0)))
    pad, _, _ = G.complete_outline(pad, color=OUTLINE, feet=CELL_SOLE + 2)
    can = pad[2:-2, 2:-2].copy()
    can[CELL_SOLE + 1:] = 0
    for y, x in holes(can[..., 3] > 0):                                # slits shut between the legs and the fist
        can[y, x] = (*OUTLINE, 255)
    op = can[..., 3] > 0
    for y, x in zip(*np.nonzero(op[CELL_PIVOT[1] - 10:])):             # outline squares with no colour beside them
        y += CELL_PIVOT[1] - 10
        nb = can[y - 1:y + 2, x - 1:x + 2]
        if all(not nb[a, b, 3] or col(nb[a, b]) == OUTLINE for a in range(nb.shape[0]) for b in range(nb.shape[1])):
            can[y, x] = 0
    feet = {}
    for name, L in legs.items():
        ys, xs = np.nonzero(L[..., 3])
        feet[name] = float(xs[ys == ys.max()].mean())
    return can, feet["near"] - feet["far"]


def build():
    des = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[4::8, 4::8].copy()
    masks, upper = split(des)
    fist = np.zeros_like(des)
    fm = masks["far"].copy()
    fm[:FIST_ROWS[0]] = False
    fm[FIST_ROWS[1] + 1:] = False
    fist[fm] = des[fm]
    lib = library(des, masks)
    strip = np.zeros((2 * CELL[1], 4 * CELL[0], 4), np.uint8)
    report = []
    for k in range(8):
        can, d = frame(lib, fist, upper, k)
        strip[(k // 4) * CELL[1]:(k // 4 + 1) * CELL[1], (k % 4) * CELL[0]:(k % 4 + 1) * CELL[0]] = can
        report.append(round(d, 1))
    return strip, report


def main():
    strip, report = build()
    Image.fromarray(strip).resize((strip.shape[1] * 8, strip.shape[0] * 8), Image.NEAREST).save(lp(OUT))
    print("near - far hoof x per frame:", report)


if __name__ == "__main__":
    main()
