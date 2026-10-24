#!/usr/bin/env python3
"""league_twitch redone at PPU 2.2 (the user, 2026-10-24: 「我们利用PPU可以重做一下图奇」): the design is the user's own
picture read back (tools/art/design_twitch_hd.py, 109 x 71, the goggle and the grin redrawn by hand), every action
Codex's whole-frame redraw of the old sheet's frames mended onto the design (tools/art/casts_twitch_hd.py: his size,
the design's head, placed on the ground), the idle the design standing.

    python tools/art/rig_twitch_hd.py --review DIR      # every tag at 3x + GIFs
    python tools/art/rig_twitch_hd.py                   # orig strips + the 1x sheet
    then: ppu_restyle.py --hero twitch, ppu_hd.py --hero twitch, hero_reels.py --hero twitch

Mended here, past what casts_twitch_hd does for every frame:
- Venom Cask (skill2): Codex threw the cask with a third arm that grew out of the back of the backpack while the near
  hand kept the crossbow (the user, 2026-10-24: 「还有第三只手的问题需要解决 codex解决不了」「这不就是第三只手吗」). That arm
  is cut away and the far arm throws overhead from behind his head: frames 1-2 frame 2's own forearm and cask raised
  over his head between the ears (rising), frame 3 frame 3's own open claw mirrored, thrown forward and up past the
  far ear (the release), frame 4 no arm (it drops back behind him); the near hand keeps the crossbow throughout. The
  backpack's edge where the arm left gets its outline.
- the death: Codex's frames reordered (DEAD_ORDER): it drew a second flight after the first landing, and two more lying
  poses than the fall needs (the last pair with the crossbow under him), so knocked back, still flying, the landing,
  the bounce, then lying still.
- the hit's first frame flashes (every PPU hero's); the attack's flash (a_flash) is laid in by the bake as before.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import casts_twitch_hd as CT  # noqa: E402
import ppu_rig as R  # noqa: E402

HERO = "twitch"
PPU = 2.2
OUTLINE = CT.OUTLINE
# the death's frames by Codex's numbers: flying (1), flying lower (3), landed (2), the bounce (4), lying (5, 6 held)
DEAD_ORDER = [1, 3, 2, 4, 5, 6, 6, 6]
# Venom Cask: the third arm's squares (design grid, per Codex frame) and the far arm's pieces moved
W_CUT = {
    1: lambda x, y: (x <= 33) & (y >= 15) & (y <= 34),             # the cask held back left of the backpack
    2: lambda x, y: ((x <= 34) & (y <= 25)) | ((x <= 41) & (y < 13)),  # the cask raised over the backpack
    3: lambda x, y: (x <= 31) & (y <= 27),                         # the open claw raised over the backpack
    4: lambda x, y: (x >= 88) & (y <= 36),                         # the claw reaching past the snout
}
W_CASK = 2                      # the frame whose cut is the raised forearm with the cask
W_CLAW = 3                      # the frame whose cut is the open claw
W_LIFT = {1: (32, -2), 2: (31, -8)}         # the cask's move (dx, dy) in frames 1 and 2: over the head, rising
W_THROW = (70, 31, -8)          # frame 3: the claw mirrored, its root (x 31) to x 70, dy -8: past the far ear
# squares cleared by hand (x0, y0, x1, y1 on the design grid, inclusive): what is left of Codex's own head past the
# design's where casts_twitch_hd cannot tell it from the crossbow - the Spray and Pray recoil's nose, its snout turned up
ERASE = {"ult_2": [(56, 13, 61, 19)]}
# the tail: Codex drew the right frame of each two-frame sheet with the tail flung up (the left one curled low, as the
# design), so it flicked every frame; the right frame takes its left neighbour's tail
TAIL_FROM = {"attack": {2: 1, 4: 3, 6: 5, 8: 7}, "skill": {2: 1}, "skill2_e": {2: 1, 4: 3}}
COAT_RGB = [0x25353A, 0x1B2124]                                   # the coat's blue-greens
TAIL_BOX = (-40, 26, 24, 68)    # x0, x1, y0, y1: where the tail is, left of the coat
TAIL_REACH = 12                 # a tail piece reaches this far left
ROOT = 3                        # columns: a tail's root, by the coat


class Design:
    """The bits of ppu_rig.Design a Rig needs, for a design read from hd/design.png."""

    def __init__(self):
        self.hero, self.ppu = HERO, PPU
        self.d = CT.design()
        self.d0 = self.d.copy()
        self.H, self.W = self.d.shape[:2]
        self.px, self.ground = CT.PIVOT_COL, CT.GROUND
        self.outline = OUTLINE


def place(rig, d, x, y):
    """A design-grid picture (top-left x, y) on a rig canvas."""
    can = rig.canvas()
    m = d[..., 3] > 0
    ys, xs = np.nonzero(m)
    ty, tx = ys + rig.oy + y, xs + rig.ox + x
    if ty.min() < 0 or tx.min() < 0 or ty.max() >= rig.CH or tx.max() >= rig.CW:
        sys.exit(f"a frame leaves the canvas: rows {ty.min()}..{ty.max()} of {rig.CH}, cols {tx.min()}..{tx.max()} of "
                 f"{rig.CW}")
    can[ty, tx] = d[ys, xs]
    return can


def on_grid(rig, can):
    """Design-grid test arrays (x, y) for every square of a rig canvas."""
    yy, xx = np.mgrid[0:rig.CH, 0:rig.CW]
    return xx - rig.ox, yy - rig.oy


def cut(rig, can, test):
    """-> (the squares where test(x, y) holds, the canvas without them, their mask)."""
    x, y = on_grid(rig, can)
    m = test(x, y) & (can[..., 3] > 0)
    piece = np.zeros_like(can)
    piece[m] = can[m]
    rest = can.copy()
    rest[m] = 0
    return piece, rest, m


def edge_outline(can, gone):
    """The squares next to the cut (4-neighbours) left on the figure's edge take the outline."""
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    op = can[..., 3] > 0
    ring = op & ndimage.binary_dilation(gone, cross) & ndimage.binary_dilation(~op, cross)
    out = can.copy()
    out[ring, :3] = OUTLINE
    return out


def moved(piece, dx, dy, flip=False):
    p = piece[:, ::-1] if flip else piece
    out = np.zeros_like(piece)
    ys, xs = np.nonzero(p[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < p.shape[0]) & (tx >= 0) & (tx < p.shape[1])
    out[ty[ok], tx[ok]] = p[ys[ok], xs[ok]]
    return out


def behind(can, piece):
    """piece laid under the figure: only on its empty squares."""
    out = can.copy()
    m = (piece[..., 3] > 0) & (can[..., 3] == 0)
    out[m] = piece[m]
    return out


def venom_cask(rig, cans):
    """{1..4: canvas} of skill2 -> the third arm gone, the far arm overhead (the docstring)."""
    rest, gone, pieces = {}, {}, {}
    for k, test in W_CUT.items():
        pieces[k], rest[k], gone[k] = cut(rig, cans[k], test)
        rest[k] = edge_outline(rest[k], gone[k])
    out = {k: behind(rest[k], moved(pieces[W_CASK], *W_LIFT[k])) for k in W_LIFT}
    to, root, dy = W_THROW
    # mirrored about the canvas: column c -> CW - 1 - c, so the root column (design x root) lands at design x to
    c_root = rig.ox + root
    dx = (rig.ox + to) - (rig.CW - 1 - c_root)
    out[3] = behind(rest[3], moved(pieces[W_CLAW], dx, dy, flip=True))
    out[4] = rest[4]
    return out


def tail_mask(rig, can):
    """The tail's squares: within TAIL_BOX (left of the coat), every square reached from its far end (x <= TAIL_REACH)
    without touching the coat (COAT_RGB, its blue-greens) - the stripes in Codex's many tans and greys and the outline
    round them, not the hem's edge."""
    x, y = on_grid(rig, can)
    x0, x1, y0, y1 = TAIL_BOX
    box = (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)
    rgb = CT.rgb24(can)
    op = can[..., 3] > 0
    coat = op & np.isin(rgb, COAT_RGB)
    way = box & op & ~ndimage.binary_dilation(coat, np.ones((3, 3), bool))
    lbl, _ = ndimage.label(way)
    far = set(np.unique(lbl[way & (x <= TAIL_REACH)])) - {0}
    return np.isin(lbl, list(far))


def tail_root(m):
    """Where a tail goes in under the coat: the middle of its squares in the ROOT columns nearest the coat."""
    ys, xs = np.nonzero(m)
    near = xs >= xs.max() - ROOT + 1
    return xs[near].mean(), ys[near].mean()


def same_tail(rig, can, ref):
    """can with its tail swapped for ref's, moved so the two go in under the coat at one place (tail_root) and laid
    behind the coat: Codex drew each sheet's right frame with the tail flung up and the left one with it curled low, so
    the tail flicked every frame."""
    m = tail_mask(rig, can)
    rm = tail_mask(rig, ref)
    (cx, cy), (rx, ry) = tail_root(m), tail_root(rm)
    out = can.copy()
    out[m] = 0
    piece = np.zeros_like(ref)
    piece[rm] = ref[rm]
    piece = moved(piece, int(round(cx - rx)), int(round(cy - ry)))
    return edge_outline(behind(out, piece), m & (behind(out, piece)[..., 3] == 0))


def frames(rig):
    sheet = R.sheet_of(HERO)
    casts = CT.placed()
    stand = place(rig, CT.design(), 0, 0)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        ms = [m for _, m in sheet[tag]]
        n = len(ms)
        if tag == "idle_base":
            out[tag] = [(stand.copy(), m) for m in ms]
            continue
        if tag not in CT.TAGS:
            sys.exit(f"{tag}: no frames")
        order = DEAD_ORDER if tag == "dead" else list(range(1, n + 1))
        cans = {k: place(rig, *casts[f"{tag}_{k}"]) for k in set(order)}
        for k in cans:
            for x0, y0, x1, y1 in ERASE.get(f"{tag}_{k}", ()):
                _, cans[k], gone = cut(rig, cans[k], lambda x, y: (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1))
                cans[k] = edge_outline(cans[k], gone)
        if tag == "skill2":
            cans = venom_cask(rig, cans)
        for k, ref in TAIL_FROM.get(tag, {}).items():
            cans[k] = CT.despeck(same_tail(rig, cans[k], cans[ref]), CT.SPECK)   # (the old tail's last specks)
        fr = [cans[k].copy() for k in order]
        if len(fr) != n:
            sys.exit(f"{tag}: {len(fr)} frames for the sheet's {n}")
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        for c in fr:
            c[rig.GY:] = 0
        out[tag] = list(zip(fr, ms))
    out["idle"] = list(out["idle_base"])
    acts = rig.bake(out)
    for t in acts:
        if t in sheet and t != "idle" and [round(m) for _, m in acts[t]] != [round(m) for _, m in sheet[t]]:
            sys.exit(f"{t}: {[round(m) for _, m in acts[t]]} against the sheet's {[m for _, m in sheet[t]]}")
    return {t: acts[t] for t in sheet if t in acts}


def make_rig(D):
    rig = R.Rig(D, pad=(40, 40, 40, 4))       # the tail and the crossbow reach out, the cask goes over his head
    rig.idle_canvas = place(rig, D.d0, 0, 0)
    return rig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    D = Design()
    rig = make_rig(D)
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
