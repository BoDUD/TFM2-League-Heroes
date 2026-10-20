#!/usr/bin/env python3
"""Graves's run legs, drawn - league_caitlyn's way (tools/art/fix_caitlyn_run_v2.py: ONE leg in eight phases, the other
leg the same phases four on) with quinn_legs' bands (tools/art/quinn_legs.py: a thigh band and a shin band of constant
width coloured across by the trousers' own colours, an outline ring round them, the far leg drawn first and the near
one with its ring over it) and the side design's own boots stamped whole and flat (never turned, slid or resized).

    python tools/art/graves_legs.py --check DIR      # the eight run frames' legs at 12x + one leg's phases + a GIF

The user, 2026-10-20, on Codex's redrawn run legs (tools/art/import_graves_run.py): 「还是有点变形吧」「膝盖那里 你看不出吗」
「你自己利用工具修吧」「这里没露出空档啊」「这里还是有点不对吧」 - Codex bent the kicked-up back leg backwards at the
knee (the thigh going back, the shin hanging down under it), put a boot's brown on knees and shins and ran the two
legs together into one block. Here every frame's legs follow one rule:
  * both hips under the pelvis (the side design's rows from CUT down are drawn - its own legs stand apart in a stride,
    so its thigh tops could never cross), each phase's thigh top a little forward or back as the leg swings (PHASES:
    the hip's column), so the stride opens as wide as the design's own stance;
  * every knee bends forward (the shin never points further forward than its thigh; the kicked-up heel goes back and
    up), the thigh 7 squares wide in the design's khaki with its light front edge, the shin 8 wide in its dark greys,
    no knee plate (on legs as short and wide as his a pad and a round knee read as a lump);
  * the boots are the design's: its long side-on boot (toe forward) on a foot ahead of or under him, its short boot
    (the far foot seen from behind) on a foot pushed back or kicked up;
  * a planted foot stays on the ground (its knee takes the body's bob), the far leg's thigh a shade darker so the two
    thighs part where they cross, the body a row down as his weight comes onto the foot under him (BOB) and the whole
    figure a row up while both feet are off the ground (LIFT).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quinn_legs as QL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "graves")
INK = (9, 1, 10)
K_D, K_M, K_L = 0x5d503d, 0x7f7052, 0xa5966c       # the trousers' khaki: dark, middle, light
G_D, G_L = 0x29232c, 0x454350                       # the trouser legs' dark grey under the knee: dark, light
# the bands' colours across (back edge to front edge, a leg pointing down)
THIGH_ROW = [K_D, K_M, K_M, K_M, K_M, K_L, K_D]
SHIN_ROW = [G_D, G_D, G_L, G_D, G_L, G_L, G_D, G_D]
FAR_DARKER = {K_L: K_M, K_M: K_D}                   # the far thigh a shade darker (its shin and boot as they are)
# the side design's boots (rows, cols, the outline included) and their ankles (the middle of the trouser leg's bottom)
BOOTS = {"long": ((50, 56), (36, 54), (43.5, 50.0)),     # the near boot, side-on, toe forward
         "short": ((50, 55), (15, 25), (21.5, 50.0))}    # the far boot, seen from behind
CUT = 38                       # the side design's rows from here down are the legs (the pelvis ends on row 37) ...
FLAP = [(38, 23, 28), (39, 23, 28), (40, 23, 28), (41, 24, 24)]   # ... but the coat's brown flap (row, cols) stays
HIP_Y = 38.0                   # the hips' row: the thighs' tops under the pelvis
GROUND_ANKLE = 50.0            # a planted foot's ankle row (its boot's sole on the design's ground)
# one leg's eight phases: (the hip's column, the knee from the hip, the ankle from the hip, the boot); the near leg plays
# phase k in frame k, the far leg phase k + 4
PHASES = [
    (38.5, (3.5, 7.0), (5.5, 12.0), "long"),     # 1 just landed ahead of him
    (36.0, (0.5, 7.5), (0.0, 12.0), "long"),     # 2 under him, his weight on it
    (33.0, (-2.0, 7.5), (-5.5, 12.0), "long"),   # 3 sliding back under him
    (32.5, (-3.0, 7.0), (-6.5, 12.0), "short"),  # 4 pushing off behind
    (30.5, (-4.0, 6.5), (-9.5, 12.5), "short"),  # 5 the toe leaving the ground behind
    (32.0, (-2.5, 7.0), (-8.5, 4.0), "short"),   # 6 the heel kicked up behind (high enough to leave no pocket of
                                                 #   ground shut in over the planted foot's heel)
    (39.0, (7.0, 3.0), (5.0, 8.0), "long"),      # 7 swung through, the knee up in front, the shin tucked back
                                                 #   under it (its boot clear of the planted leg: a gap, no crack)
    (37.5, (5.0, 6.0), (8.5, 11.0), "long"),     # 8 reaching forward to land
]
PLANTED = [True, True, True, True, True, False, False, False]
BOB = [0, 1, 0, 0, 0, 1, 0, 0]      # the body (and hips) a row down: his weight on the foot under him
LIFT = [0, 0, 0, 1, 0, 0, 0, 1]     # both feet off the ground: the whole figure a row up
SLIT_ROWS = 5                       # rows under the hips where a one-square slit between the thighs is closed


def rgb(h):
    return np.array(((h >> 16) & 255, (h >> 8) & 255, h & 255, 255), np.uint8)


def boot(side, name):
    """(offsets of the boot's squares from its ankle, their colours) cut from the side design."""
    (r0, r1), (c0, c1), (ax, ay) = BOOTS[name]
    ys, xs = np.nonzero(side[r0:r1 + 1, c0:c1 + 1, 3] > 0)
    ys, xs = ys + r0, xs + c0
    return np.stack([xs + 0.5 - ax, ys + 0.5 - ay], 1), side[ys, xs]


def part(side, name, far):
    """quinn_legs' part: the bands' colours (the far thigh darker), the boot, no knee plate."""
    thigh = [rgb(FAR_DARKER.get(h, h) if far else h) for h in THIGH_ROW]
    return dict(thigh=np.array(thigh), shin=np.array([rgb(h) for h in SHIN_ROW]), boot=boot(side, name), plate=[])


def geometry(k, bob=0):
    """Phase k's (hip, knee, ankle) in design squares with the body `bob` rows down: a planted foot stays where it
    stands (the knee solved at the phase's own lengths), a lifted one moves with the hips."""
    hx, (kx, ky), (ax, ay), _ = PHASES[k]
    H = np.array((hx, HIP_Y + bob))
    if PLANTED[k] and bob:
        K, A = QL.reach_to(H, (hx + ax, HIP_Y + ay), math.hypot(kx, ky), math.hypot(ax - kx, ay - ky))
        return H, K, A
    return H, H + (kx, ky), H + (ax, ay)


def body(side):
    """The side design without its legs: the rows from CUT down cleared but the coat's brown flap."""
    b = side.copy()
    keep = np.zeros(side.shape[:2], bool)
    for y, c0, c1 in FLAP:
        keep[y, c0:c1 + 1] = True
    cut = np.zeros(side.shape[:2], bool)
    cut[CUT:] = True
    b[cut & ~keep] = 0
    return b


def draw(can, side, k, at):
    """Frame k's two legs on can: the near leg at phase k over the far leg at phase k + 4, the design's (0, 0) at canvas
    square `at` (the frame's LIFT already in it; the hips take BOB themselves)."""
    QL.INK = INK
    QL.KNEE_R = 0.0
    o = np.asarray(at, float)
    geo, parts = {}, {}
    for key, ph in (("near", k), ("far", (k + 4) % 8)):
        H, K, A = geometry(ph, BOB[k])
        geo[key] = (H + o, K + o, A + o, 0)
        parts[key] = part(side, PHASES[ph][3], key == "far")
    QL.draw_legs(can, geo, parts)
    # the top of the gap between the thighs: where the two thighs' outlines leave a one-square slit of ground under
    # the pelvis (a dotted crack, gap-check), the slit takes the outline - the gap opens below it
    y0 = int(round(at[1] + HIP_Y))
    for y in range(y0, y0 + SLIT_ROWS):
        row = can[y, :, 3] > 0
        for x in range(1, can.shape[1] - 1):
            if not row[x] and row[x - 1] and row[x + 1]:
                can[y, x] = (*INK, 255)


def frame(side, k, pad=(15, 6)):
    """Run frame k (0-7) on its own canvas: the legs, the body over them (BOB rows down), all LIFT rows up."""
    px, py = pad
    can = np.zeros((side.shape[0] + 2 * py, side.shape[1] + 2 * px, 4), np.uint8)
    at = (px, py - LIFT[k])
    draw(can, side, k, at)
    b = body(side)
    m = b[..., 3] > 0
    y0 = py - LIFT[k] + BOB[k]
    sub = can[y0:y0 + side.shape[0], px:px + side.shape[1]]
    sub[m] = b[m]
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", required=True)
    a = ap.parse_args()
    os.makedirs(a.check, exist_ok=True)
    side = np.asarray(Image.open(os.path.join(SRC, "hd", "side.png")).convert("RGBA")).copy()
    frs = [frame(side, k) for k in range(8)]
    z = 12
    tiles = []
    for k, t in enumerate(frs):
        c = t[34 + 6:58 + 6, 12 + 15:62 + 15]
        bg = np.zeros(c.shape, np.uint8)
        bg[...] = (200, 205, 195, 255)
        m = c[..., 3] > 0
        bg[m] = c[m]
        im = Image.fromarray(np.repeat(np.repeat(bg, z, 0), z, 1)).convert("RGB")
        ImageDraw.Draw(im).text((4, 4), str(k + 1), fill=(0, 0, 255))
        tiles.append(im)
    w, h = tiles[0].size
    sh = Image.new("RGB", (2 * (w + 8), 4 * (h + 8)), (255, 255, 255))
    for i, im in enumerate(tiles):
        sh.paste(im, ((i % 2) * (w + 8), (i // 2) * (h + 8)))
    sh.save(os.path.join(a.check, "graves_run_legs.png"))
    gif = []
    for t in frs:
        bg = Image.new("RGBA", (t.shape[1], t.shape[0]), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(t))
        gif.append(bg.convert("RGB").resize((t.shape[1] * 5, t.shape[0] * 5), Image.NEAREST))
    gif[0].save(os.path.join(a.check, "graves_run_legs.gif"), save_all=True, append_images=gif[1:], duration=115,
                loop=0)
    print("written", a.check)


if __name__ == "__main__":
    main()
