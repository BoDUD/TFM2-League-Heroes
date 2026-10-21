#!/usr/bin/env python3
"""Ornn's run, drawn on the design (the user, 2026-10-21, on Codex's four run poses: 「奥恩走路是这样走的？」 then
「跑步用定稿的上身，你自己画腿的跑步循环（像格雷福斯那样），大锤只轻微摆动」; on the first draw: 「左腿变形了吧？跑步节奏的确对了」
「应该是左脚变形了」).

    python tools/art/ornn_legs.py --check DIR      # the eight run frames at 10x, the feet at 16x + a GIF

His design (hd/idle.png, 71 x 66) shows almost no leg: the plum apron hangs to row 58, the far boot stands right of it
and the near one is a dark lump half behind the big hammer's head - its leg was never drawn. So the legs are drawn
(graves_legs' rule, one foot in eight phases and the other four on):
  * the body (all but the boots, the apron, both arms and hammers) is the design's own, never redrawn; it sets one or
    two rows down while his weight comes onto the foot under him (BOB, a bouncing trot) and leans a column forward
    (LEAN);
  * both feet are the design's own far boot (its lit long boot, toe to the right) stamped whole - a smaller, darker
    boot drawn here did not match the idle's foot (「右脚也应该调一调吧 看着不协调」); each joined to the apron by a short
    leg band from its hip under the apron to the boot's shaft, the far foot first, the near one over it, the apron over
    both (the boots' shafts go up under it), moved by whole squares only: planted a boot slides back under him, lifted it swings
    forward a row or two up (PHASES, the same stride for both feet, half a cycle apart - a wider far stride looked out of
    step: 「右脚也应该调一调吧 看着不协调」). No boot steps back further than a column (NEAR_BACK), so the big hammer's head
    never hides all but a sliver of the near one (the first draw: a one-square sliver read as a twisted foot);
  * the design's own boots are taken out first (BOOT_AREAS), the apron's tip kept;
  * the hammers' heads move only where nothing opens behind them (the first draw split the big head, its box stopped
    at column 29, and swung it left off the body: a hole): the big head is taken whole (the largest steel blob of its
    box), carried CARRY rows off the ground (League's run holds the hammers) and swings a column forward at most
    (BIG_SWAY); the small head a column back at most (SMALL_SWAY), against it.
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
INK = (1, 0, 0, 255)


def rgb(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255, 255)


LEG_NEAR = [rgb(0x331019), rgb(0x4e142b), rgb(0x6f1b37), rgb(0x331019)]     # a leg band across, back to front
LEG_FAR = [rgb(0x2a0c14), rgb(0x331019), rgb(0x4e142b), rgb(0x2a0c14)]
# the design's own boots taken out: (x0, x1, y0, y1) boxes; the near boot's, and the far boot's two (right of the
# apron's edge, and its bottom under the apron's right corner) - steel (a hammer) never taken
NEAR_AREA = (24, 31, 57, 63)
FAR_AREAS = [(49, 58, 56, 63), (44, 48, 59, 63)]
# both feet are the design's far boot (its lit long boot, 14 x 8 from (44, 56), toe to the right) stamped whole: a
# drawn smaller, darker boot did not match the idle's foot (「右脚也应该调一调吧 看着不协调」)
BOOT_AT = (44, 56)
SHAFT = 7.0                        # the ankle: this many squares right of the boot's left edge (its shaft's middle)
# the hips (x, y) under the apron and each boot's left edge standing (phase 0 adds its dx); the far boot's at dx 0 is
# the design's own place
HIP = {"near": (33.0, 56.0), "far": (51.0, 56.0)}
FOOT_X = {"near": 27, "far": 44}
# one boot's eight phases: (columns forward, rows up); the near boot plays phase k in frame k, the far one k + 4
PHASES = [(3, 0), (2, 0), (0, 0), (-1, 0), (-1, 1), (0, 2), (2, 2), (3, 1)]   # both feet the same stride
NEAR_BACK = -1                     # the near boot never further back than this (the hammer's head hides it)
BOB = [0, 1, 2, 1, 0, 1, 2, 1]     # the body rows down: lowest at mid-stance, a heavy bouncing trot
LEAN = 1                           # the body a column forward for the whole run
CARRY = 2                          # the big hammer's head carried this many rows off the ground (it bobs with him)
BIG_SWAY = [0, 0, 1, 1, 1, 1, 0, 0]       # the big head, columns forward (never back: a hole would open behind it)
SMALL_SWAY = [-1, -1, 0, 0, 0, 0, -1, -1]  # the small head, columns back (never forward), against the big one
HAMMERS = {"big": ((40, 66), (0, 34)), "small": ((48, 64), (56, 71))}


def steel(d):
    c = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (c[..., 2] > c[..., 0] + 25)


def hammer_mask(d, key):
    """A hammer's head whole: the largest steel blob in its box, with the outline squares round it."""
    (r0, r1), (c0, c1) = HAMMERS[key]
    box = np.zeros(d.shape[:2], bool)
    box[r0:r1 + 1, c0:c1 + 1] = True
    s = steel(d) & box
    lb, n = ndimage.label(s)
    if n:
        sizes = ndimage.sum(s, lb, range(1, n + 1))
        s = lb == (1 + int(np.argmax(sizes)))
    dark = (d[..., 3] > 0) & (d[..., :3].astype(int).sum(2) < 40)
    return s | (ndimage.binary_dilation(s) & ~s & dark)


def area_mask(d, areas):
    m = np.zeros(d.shape[:2], bool)
    for x0, x1, y0, y1 in areas:
        m[y0:y1 + 1, x0:x1 + 1] = True
    return m & (d[..., 3] > 0) & ~steel(d)


def boots_mask(d):
    return area_mask(d, [NEAR_AREA] + FAR_AREAS)


def boot_sprite(d):
    """The design's far boot: (its squares relative to BOOT_AT, their colours, its height)."""
    m = area_mask(d, FAR_AREAS)
    ys, xs = np.nonzero(m)
    return np.stack([xs - BOOT_AT[0], ys - BOOT_AT[1]], 1), d[ys, xs], ys.max() + 1 - BOOT_AT[1]


FAR_SHIFT = -3                     # the far foot's stride set back: its most forward step is the design's own place, so
                                   # its toe never reaches past the idle's outline (the first stride put it 3 squares out
                                   # under the molten arm: 「脚部凸出身体了」「右脚」)


def phase(key, k):
    dx, up = PHASES[k if key == "near" else (k + 4) % 8]
    if key == "near":
        dx = max(dx, NEAR_BACK)
    else:
        dx += FAR_SHIFT
    return dx, up


def put(can, src, mask, dx, dy):
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
    can[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]


def boot(can, sprite, x0, top):
    offs, cols, _ = sprite
    for (ox, oy), c in zip(offs, cols):
        y, x = top + oy, x0 + ox
        if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
            can[y, x] = c


def leg(can, hip, ankle, colours):
    """A leg band 4 squares wide from the hip down to the ankle (the boot's shaft top), the outline round it."""
    (hx, hy), (ax, ay) = hip, ankle
    rows = range(int(round(hy)), int(round(ay)) + 1)
    cells = {}
    n = max(1, len(rows) - 1)
    for j, y in enumerate(rows):
        cx = hx + (ax - hx) * j / n
        x0 = int(round(cx - 2))
        for i in range(4):
            cells[(x0 + i, y)] = colours[i]
    ring = {(x + dx, y + dy) for (x, y) in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)
    for (x, y) in ring:
        if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
            can[y, x] = INK
    for (x, y), c in cells.items():
        if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
            can[y, x] = c


def frame(d, k, pad=(4, 4)):
    """Run frame k (0-7) on the design's grid padded by `pad` (columns, rows)."""
    px, py = pad
    H, W = d.shape[:2]
    can = np.zeros((H + 2 * py, W + 2 * px, 4), np.uint8)
    hb, hs = hammer_mask(d, "big"), hammer_mask(d, "small")
    sprite = boot_sprite(d)
    body = d.copy()
    body[boots_mask(d) | hb | hs] = 0
    bob = BOB[k]
    ox, oy = px + LEAN, py                       # the design's (0, 0) on the canvas, standing
    # the far leg and boot, then the near ones (nearer, over the far foot), the body (the apron) over both legs' tops
    for key, colours in (("far", LEG_FAR), ("near", LEG_NEAR)):
        dx, up = phase(key, k)
        x0 = ox + FOOT_X[key] + dx
        top = oy + BOOT_AT[1] - up
        leg(can, (ox + HIP[key][0], oy + HIP[key][1] + bob), (x0 + SHAFT, top + 1), colours)
        boot(can, sprite, x0, top)
    put(can, body, body[..., 3] > 0, ox, oy + bob)
    # the hammers' heads over everything
    put(can, d, hb, ox + BIG_SWAY[k], oy + bob - CARRY)
    put(can, d, hs, ox + SMALL_SWAY[k], oy + bob)
    return can


def holes(can):
    """Transparent squares shut in by the figure (a frame should have none the design does not)."""
    op = can[..., 3] > 0
    return int((ndimage.binary_fill_holes(op) & ~op).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    a = ap.parse_args()
    os.makedirs(a.check, exist_ok=True)
    d = np.asarray(Image.open(os.path.join(SRC, "idle.png")).convert("RGBA")).copy()
    pad0 = np.zeros((d.shape[0] + 8, d.shape[1] + 8, 4), np.uint8)
    pad0[4:-4, 4:-4] = d
    frs = [frame(d, k) for k in range(8)]
    print("enclosed holes: design", holes(pad0), "frames", [holes(f) for f in frs])
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
    z = 16
    feet = []
    for k, t in enumerate([pad0] + frs):
        c = t[54:71, 20:66]
        bg = np.zeros(c.shape, np.uint8)
        bg[...] = (200, 205, 195, 255)
        m = c[..., 3] > 0
        bg[m] = c[m]
        im = Image.fromarray(np.repeat(np.repeat(bg, z, 0), z, 1)).convert("RGB")
        ImageDraw.Draw(im).text((4, 4), "idle" if k == 0 else str(k), fill=(0, 0, 255))
        feet.append(im)
    w, h = feet[0].size
    sh = Image.new("RGB", (3 * (w + 6), 3 * (h + 6)), (255, 255, 255))
    for i, im in enumerate(feet):
        sh.paste(im, ((i % 3) * (w + 6), (i // 3) * (h + 6)))
    sh.save(os.path.join(a.check, "ornn_run_feet.png"))
    gif = []
    for t in frs:
        bg = Image.new("RGBA", (t.shape[1], t.shape[0]), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(t))
        gif.append(bg.convert("RGB").resize((t.shape[1] * 5, t.shape[0] * 5), Image.NEAREST))
    gif[0].save(os.path.join(a.check, "ornn_run_legs.gif"), save_all=True, append_images=gif[1:], duration=110, loop=0)
    print("written", a.check)


if __name__ == "__main__":
    main()
