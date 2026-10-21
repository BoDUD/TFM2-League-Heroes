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
  * both feet are ONE boot drawn here (BOOT: a squat boot, toe to the right, the design's own plum and brown shades),
    the near one in full tone, the far one a shade darker (FAR); each joined to the apron by a short leg band from its
    hip under the apron to the boot's shaft (the far leg behind the apron, the near leg's band behind the apron too,
    its boot in front of it), both moved by whole squares only: planted a boot slides back under him, lifted it swings
    forward a row or more up (PHASES). The near boot never steps back further than NEAR_BACK, so the big hammer's head
    never hides all but a sliver of it (the first draw: a one-square sliver read as a twisted foot);
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
GROUND = 63                        # the boots' sole row (the outline under the soles) on the design


def rgb(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255, 255)


# the boot, toe to the right (k outline, L its light top / heel edge, M mid, D dark, H the toe's light): the design's
# own boot shades (its far boot: 331019, 4e142b, 763528, 874223)
BOOT = [".kkkkk....",
        "kLMMDDk...",
        "kMMDDDDkk.",
        "kMDDDDDLHk",
        "kDDDDDDDDk",
        ".kkkkkkkk."]
BOOT_NEAR = {"k": INK, "L": rgb(0x763528), "M": rgb(0x4e142b), "D": rgb(0x331019), "H": rgb(0x874223)}
FAR = {"k": INK, "L": rgb(0x4e142b), "M": rgb(0x3d131e), "D": rgb(0x2a0c14), "H": rgb(0x662b26)}
LEG_NEAR = [rgb(0x331019), rgb(0x4e142b), rgb(0x6f1b37), rgb(0x331019)]     # a leg band across, back to front
LEG_FAR = [rgb(0x2a0c14), rgb(0x331019), rgb(0x4e142b), rgb(0x2a0c14)]
SHAFT = 2.5                        # the ankle: this many squares right of the boot's left edge (the shaft's middle)
# the hips (x, y) under the apron and each boot's left edge standing (phase 0 adds its dx)
HIP = {"near": (33.0, 56.0), "far": (47.0, 56.0)}
FOOT_X = {"near": 28, "far": 45}
# the design's own boots taken out: (x0, x1, y0, y1) boxes; the near boot's, and the far boot's two (right of the
# apron's edge, and its bottom under the apron's right corner) - steel (a hammer) never taken
BOOT_AREAS = [(24, 31, 57, 63), (49, 58, 56, 63), (44, 48, 59, 63)]
# one boot's eight phases: (columns forward, rows up); the near boot plays phase k in frame k, the far one k + 4
PHASES = [(3, 0), (1, 0), (-1, 0), (-3, 0), (-3, 1), (-1, 3), (2, 3), (3, 1)]
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


def boots_mask(d):
    m = np.zeros(d.shape[:2], bool)
    for x0, x1, y0, y1 in BOOT_AREAS:
        m[y0:y1 + 1, x0:x1 + 1] = True
    return m & (d[..., 3] > 0) & ~steel(d)


def phase(key, k):
    dx, up = PHASES[k if key == "near" else (k + 4) % 8]
    if key == "near":
        dx = max(dx, NEAR_BACK)
    return dx, up


def put(can, src, mask, dx, dy):
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
    can[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]


def boot(can, x0, top, colours):
    for j, line in enumerate(BOOT):
        for i, ch in enumerate(line):
            if ch != ".":
                can[top + j, x0 + i] = colours[ch]


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
    body = d.copy()
    body[boots_mask(d) | hb | hs] = 0
    bob = BOB[k]
    ox, oy = px + LEAN, py                       # the design's (0, 0) on the canvas, standing
    feet = {}
    for key in ("far", "near"):
        dx, up = phase(key, k)
        x0 = ox + FOOT_X[key] + dx
        top = oy + GROUND - (len(BOOT) - 1) - up
        hip = (ox + HIP[key][0], oy + HIP[key][1] + bob)
        feet[key] = (x0, top, hip, (x0 + SHAFT, top + 1))
    # the far leg and boot, the near leg's band (both behind the apron), the body over them
    x0, top, hip, ankle = feet["far"]
    leg(can, hip, ankle, LEG_FAR)
    boot(can, x0, top, FAR)
    x0, top, hip, ankle = feet["near"]
    leg(can, hip, ankle, LEG_NEAR)
    put(can, body, body[..., 3] > 0, ox, oy + bob)
    # the near boot in front of the apron, the hammers' heads over everything
    boot(can, x0, top, BOOT_NEAR)
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
