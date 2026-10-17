#!/usr/bin/env python3
"""Renekton's rear (image-left) foot drawn as his front foot (the user, 2026-10-08: 「左右脚不应该一样吗？现在不一样啊」).

The design's front foot is the blue shin into a grey ankle plate, the teal foot and three orange claws (rows 95-99,
columns 72-87); the rear foot under the blue knee guard was a brown and dark-grey stub with gold claws. The front
foot's rows 95-99 go 25 columns to the left, onto the rear shin (its blue at columns 48-50): only the old rear foot's
squares (rows 95-99, columns 47-57) are cleared first and only the front foot's drawn squares are put down, so the tail
(columns 41-46) and the tip of the loincloth (column 61, rows 94-95) stay. The same edit goes into every cell of the
approved idle strip (the design six times), and Codex's rig takes the wider foot with the rear leg (its foot box to
column 62 from row 96), so the run moves the whole foot.

Then 「脚后跟翘起来的是什么啊 尾巴吗 ？？？」「左脚后跟」: the tail's hooked tip (rows 92-99, columns 39-46), lying behind
the rear heel, read as a spur on the new foot - the user picked 「去掉尾巴尖」: those squares go, and the outline squares
left with no colour beside them there (TAIL_ZONE); the idle strip and the rig's design take the same edit.

    python tools/art/fix_renekton_foot.py         # the foot (once)
    python tools/art/fix_renekton_foot.py --tail  # the tail tip (once)
    # then the rig (rebuild.py, from a short path), fix_renekton_strips.py, import_native
"""
import os
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native", "renekton_native.png")
RIG = os.path.join(ROOT, "assets", "source", "renekton", "codex_strips_narrow", "rig")
APPROVED = os.path.join(RIG, "approved_source", "design", "renekton_design_1x.png")
IDLE = os.path.join(RIG, "approved_source", "renekton_idle.png")
REBUILD = os.path.join(RIG, "rebuild.py")
ROWS = (95, 100)                 # the feet's rows (the soles' outline on 99)
FRONT = (72, 88)                 # the front foot's columns
SHIFT = -25                      # onto the rear shin
OLD = (47, 58)                   # the old rear foot's columns, cleared
TAIL = (92, 100, 39, 47)         # the tail's hooked tip behind the rear heel: rows r0..r1-1, columns c0..c1-1
TAIL_ZONE = (88, 100, 36, 48)    # where outline squares left bare by it go
INK = (0x04, 0x04, 0x03)


def lp(p):
    return "\\\\?\\" + os.path.abspath(p)


def edited(d):
    out = d.copy()
    r0, r1 = ROWS
    out[r0:r1, OLD[0]:OLD[1]] = 0
    block = d[r0:r1, FRONT[0]:FRONT[1]]
    for y in range(block.shape[0]):
        for x in range(block.shape[1]):
            if block[y, x, 3]:
                out[r0 + y, FRONT[0] + SHIFT + x] = block[y, x]
    return out


def tail_off(d):
    out = d.copy()
    r0, r1, c0, c1 = TAIL
    out[r0:r1, c0:c1] = 0
    z = np.zeros(out.shape[:2], bool)
    z[TAIL_ZONE[0]:TAIL_ZONE[1], TAIL_ZONE[2]:TAIL_ZONE[3]] = True
    # the leg's edge the tail covered gets its outline (there only)
    closed, _, _ = strips.complete_outline(out.copy(), color=INK, feet=99)
    out[z] = closed[z]
    while True:
        op = out[..., 3] > 0
        ink = op & (out[..., :3] == INK).all(-1)
        col = op & ~ink
        near = np.zeros_like(col)
        near[1:] |= col[:-1]
        near[:-1] |= col[1:]
        near[:, 1:] |= col[:, :-1]
        near[:, :-1] |= col[:, 1:]
        gone = ink & ~near & z
        if not gone.any():
            return out
        out[gone] = 0


def apply(d, new):
    """The edit into the design, the rig's copy of it and the six cells of the idle strip."""
    Image.fromarray(new).save(lp(NATIVE))
    Image.fromarray(new).save(lp(APPROVED))
    big = np.asarray(Image.open(lp(IDLE)).convert("RGBA")).copy()
    small = big[4::8, 4::8].copy()
    ys, xs = np.nonzero(d[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    tpl = d[y0:y1, x0:x1]
    cells = 0
    H, W = small.shape[:2]
    for oy in range(0, H - (y1 - y0) + 1):
        for ox in range(0, W - (x1 - x0) + 1):
            win = small[oy:oy + y1 - y0, ox:ox + x1 - x0]
            if (win[..., 3] > 0).sum() == (tpl[..., 3] > 0).sum() and (win == tpl).all():
                dy, dx = oy - y0, ox - x0
                for (yy, xx) in zip(*np.nonzero((new != d).any(-1))):
                    big[(yy + dy) * 8:(yy + dy + 1) * 8, (xx + dx) * 8:(xx + dx + 1) * 8] = new[yy, xx]
                cells += 1
    if cells != 6:
        sys.exit(f"renekton_idle.png: found the design in {cells} cells, not 6 - nothing written to the idle")
    Image.fromarray(big).save(lp(IDLE))
    return cells


def main():
    d = np.asarray(Image.open(lp(NATIVE)).convert("RGBA")).copy()
    if "--tail" in sys.argv:
        r0, r1, c0, c1 = TAIL
        if not d[r0:r1, c0:c1, 3].any():
            sys.exit("renekton_native.png: the tail tip is gone already")
        new = tail_off(d)
        cells = apply(d, new)
        print(f"tail tip: {int((new != d).any(-1).sum())} squares; renekton_idle.png: {cells} cells")
        return
    r0, r1 = ROWS
    if (d[r0:r1, FRONT[0] + SHIFT:FRONT[1] + SHIFT] == d[r0:r1, FRONT[0]:FRONT[1]])[..., 3].all() and \
            (d[r0:r1, FRONT[0] + SHIFT:FRONT[1] + SHIFT, :3] == d[r0:r1, FRONT[0]:FRONT[1], :3]).all():
        sys.exit("renekton_native.png: the rear foot is the front foot already")
    new = edited(d)
    n = int((new != d).any(-1).sum())
    Image.fromarray(new).save(lp(NATIVE))
    Image.fromarray(new).save(lp(APPROVED))
    # the idle strip: the design six times at 8x - find the design in each cell and make the same edit there
    big = np.asarray(Image.open(lp(IDLE)).convert("RGBA")).copy()
    small = big[4::8, 4::8].copy()
    ys, xs = np.nonzero(d[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    tpl = d[y0:y1, x0:x1]
    cells = 0
    H, W = small.shape[:2]
    for oy in range(0, H - (y1 - y0) + 1):
        for ox in range(0, W - (x1 - x0) + 1):
            win = small[oy:oy + y1 - y0, ox:ox + x1 - x0]
            if (win[..., 3] > 0).sum() == (tpl[..., 3] > 0).sum() and (win == tpl).all():
                dy, dx = oy - y0, ox - x0
                for (yy, xx) in zip(*np.nonzero((new != d).any(-1))):
                    big[(yy + dy) * 8:(yy + dy + 1) * 8, (xx + dx) * 8:(xx + dx + 1) * 8] = new[yy, xx]
                cells += 1
    if cells != 6:
        sys.exit(f"renekton_idle.png: found the design in {cells} cells, not 6 - nothing written to the idle")
    Image.fromarray(big).save(lp(IDLE))
    # the rig: the rear leg's foot box reaches the new toes (columns 61-62 from row 96; the loincloth's tip is above)
    src = open(lp(REBUILD), encoding="utf-8").read()
    old = "foot=((yy>=94)&(xx>=43)&(xx<=60)) if name=='rearleg'"
    new_s = "foot=(((yy>=94)&(xx>=43)&(xx<=60))|((yy>=96)&(xx>=61)&(xx<=62))) if name=='rearleg'"
    if old in src:
        src = src.replace(old, new_s)
        src = src.replace("  foot=(((yy>=94)", "  # Claude, 2026-10-08: the rear foot drawn as the front one reaches column 62 (tools/art/fix_renekton_foot.py)\n  foot=(((yy>=94)", 1)
        open(lp(REBUILD), "w", encoding="utf-8").write(src)
    print(f"renekton_native.png + the rig's design: {n} squares; renekton_idle.png: {cells} cells; rebuild.py foot box")


if __name__ == "__main__":
    main()
