#!/usr/bin/env python3
"""Ornn's run, drawn on the design (the user, 2026-10-21, on Codex's four run poses: 「奥恩走路是这样走的？」 then
「跑步用定稿的上身，你自己画腿的跑步循环（像格雷福斯那样），大锤只轻微摆动」).

    python tools/art/ornn_legs.py --check DIR      # the eight run frames at 10x + a GIF

His design (hd/idle.png, 71 x 66) shows almost no leg: the plum apron hangs to row 58 and only two boots stand under it
(the near one at columns 25-31, half behind the big hammer's head; the far one at 45-58), so the stride is the boots'
(graves_legs' rule, one foot in eight phases and the other four on, shrunk to his stubby legs):
  * the body (every row above LEG_ROW, the apron, both arms and hammers) is the design's own, never redrawn; it sets a
    row or two down while his weight comes onto a foot under him (BOB) and leans a column forward for the run (LEAN);
  * each boot is the design's own, cut whole (BOOTS) and only moved by whole squares: planted it slides back under him,
    lifted it swings forward a row or two up (PHASES); the near boot in front of the apron, the far one behind it;
  * a lifted boot overlaps the apron's hem (the near one in front of it: the knee raised), so no leg stub is needed;
  * the hammers sway with the stride a column either way (the big one with the near arm's swing, the small one
    against it) - their heads only, the design's own squares (HAMMERS), the hands holding them stay; the big head is
    carried CARRY rows off the ground (League's run holds the hammers), so the near boot shows under it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "ornn", "hd")
INK = (1, 0, 0)
LEG_ROW = 59                       # the design's rows from here down (between LEG_COLS) are the boots
LEG_COLS = (24, 60)
PLUM = [(51, 16, 25), (78, 20, 43), (111, 27, 55), (78, 20, 43)]   # a leg stub's colours across (back edge to front)
# the boots on hd/idle.png: (rows, cols) boxes, the outline included; steel squares (a hammer's) never taken
BOOTS = {"near": ((58, 64), (25, 32)), "far": ((58, 64), (44, 58))}
# the hammers' heads (and the handle's end) on hd/idle.png: (rows, cols) boxes, steel squares and their outline
HAMMERS = {"big": ((44, 66), (0, 29)), "small": ((49, 63), (57, 71))}
# one boot's eight phases: (columns forward, rows up); the near boot plays phase k in frame k, the far one k + 4
PHASES = [(3, 0), (1, 0), (-1, 0), (-3, 0), (-3, 1), (-1, 3), (2, 3), (3, 1)]
BOB = [0, 1, 2, 1, 0, 1, 2, 1]     # the body rows down: lowest at mid-stance (the planted foot under him), up as the
                                   # step passes - a heavy bouncing trot (a single row was lost at game size: under a
                                   # game pixel, the user's 「奥恩走路是这样走的？」 compared with League's)
LEAN = 1                           # the body a column forward for the whole run
SWAY = [0, -1, -1, 0, 0, 1, 1, 0]  # the big hammer's head, columns (the small one the other way)
CARRY = 2                          # the big hammer's head carried this many rows off the ground while he runs (League's
                                   # run: the hammers held, not dragged) - the near boot shows under it


def steel(d):
    rgb = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (rgb[..., 2] > rgb[..., 0] + 25)


def box_mask(shape, rows, cols):
    m = np.zeros(shape[:2], bool)
    m[rows[0]:rows[1] + 1, cols[0]:cols[1] + 1] = True
    return m


def boot_mask(d, key):
    (r0, r1), (c0, c1) = BOOTS[key]
    return box_mask(d.shape, (max(r0, LEG_ROW - 1), r1), (c0, c1)) & (d[..., 3] > 0) & ~steel(d) & \
        (np.arange(d.shape[0])[:, None] >= LEG_ROW - 1)


def hammer_mask(d, key):
    (r0, r1), (c0, c1) = HAMMERS[key]
    box = box_mask(d.shape, (r0, r1), (c0, c1))
    s = steel(d) & box
    lb, n = ndimage.label(s)
    if n:
        sizes = ndimage.sum(s, lb, range(1, n + 1))
        s = lb == (1 + int(np.argmax(sizes)))         # the head: the biggest steel blob in the box
    ring = ndimage.binary_dilation(s) & ~s & box & (d[..., 3] > 0) & (d[..., :3].astype(int).sum(2) < 60)
    return s | ring


def paste(can, src, mask, dx, dy, under=False):
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = can[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    can[ty, tx] = src[ys, xs]


def stub(can, top, bottom, x0, x1):
    """A leg stub from row `top` down to row `bottom` (inclusive) between columns x0..x1, the outline round it."""
    if bottom < top:
        return
    w = x1 - x0 + 1
    for y in range(top, bottom + 1):
        for i in range(w):
            c = PLUM[min(len(PLUM) - 1, i * len(PLUM) // w)]
            can[y, x0 + i] = (*c, 255)
        for x in (x0 - 1, x1 + 1):
            if can[y, x, 3] == 0:
                can[y, x] = (*INK, 255)


def frame(d, k, pad=(4, 4)):
    """Run frame k (0-7) on the design's grid padded by `pad` (columns, rows): the boots, the stubs, the body."""
    px, py = pad
    H, W = d.shape[:2]
    can = np.zeros((H + 2 * py, W + 2 * px, 4), np.uint8)
    legs = box_mask(d.shape, (LEG_ROW, H - 1), LEG_COLS) & ~steel(d)
    hb, hs = hammer_mask(d, "big"), hammer_mask(d, "small")
    body = d.copy()
    body[legs] = 0
    body[hb | hs] = 0
    bob = BOB[k]
    # the far boot (behind the apron) and its stub
    for key, ph in (("far", (k + 4) % 8),):
        fx, fy = PHASES[ph]
        m = boot_mask(d, key)
        paste(can, d, m, px + fx + LEAN, py - fy)
    # the body over it (a row down on BOB), the apron's hem its lowest rows
    paste(can, body, body[..., 3] > 0, px + LEAN, py + bob)
    # the near boot in front of the apron
    nx, ny = PHASES[k]
    paste(can, d, boot_mask(d, "near"), px + nx + LEAN, py - ny)
    # the hammers' heads, swayed (the big one carried off the ground)
    s = SWAY[k]
    paste(can, d, hb, px + LEAN + s, py + bob - CARRY)
    paste(can, d, hs, px + LEAN - s, py + bob)
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    a = ap.parse_args()
    os.makedirs(a.check, exist_ok=True)
    d = np.asarray(Image.open(os.path.join(SRC, "idle.png")).convert("RGBA")).copy()
    frs = [frame(d, k) for k in range(8)]
    z = 10
    tiles = []
    for k, t in enumerate(frs):
        bg = np.zeros(t.shape, np.uint8)
        bg[...] = (200, 205, 195, 255)
        m = t[..., 3] > 0
        bg[m] = t[m]
        im = Image.fromarray(np.repeat(np.repeat(bg, z, 0), z, 1)).convert("RGB")
        ImageDraw.Draw(im).text((4, 4), str(k + 1), fill=(0, 0, 255))
        tiles.append(im)
    w, h = tiles[0].size
    sh = Image.new("RGB", (4 * (w + 8), 2 * (h + 8)), (255, 255, 255))
    for i, im in enumerate(tiles):
        sh.paste(im, ((i % 4) * (w + 8), (i // 4) * (h + 8)))
    sh.save(os.path.join(a.check, "ornn_run_legs.png"))
    gif = []
    for t in frs:
        bg = Image.new("RGBA", (t.shape[1], t.shape[0]), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(t))
        gif.append(bg.convert("RGB").resize((t.shape[1] * 5, t.shape[0] * 5), Image.NEAREST))
    gif[0].save(os.path.join(a.check, "ornn_run_legs.gif"), save_all=True, append_images=gif[1:], duration=110, loop=0)
    print("written", a.check)


if __name__ == "__main__":
    main()
