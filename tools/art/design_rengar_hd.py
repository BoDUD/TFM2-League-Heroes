#!/usr/bin/env python3
"""Rengar's dense design: Codex's picture (tools/art/pack_rengar_ppu.py's pack, traced from his sprite now - the hunched
stalking crouch) read back on its own squares, design_leesin_hd's way.

    python tools/art/design_rengar_hd.py [--review DIR]

Codex delivered (2026-10-27, Documents/Codex/2026-10-27/new-chat-6) raw/rengar-selected-original.png (archived as
hd/raw/rengar-A.png): asked for 11-px squares with true alpha, it came 1254 x 1254 on ~15 x 14.6-px squares with soft
alpha. Its own export (rengar-A.png / rengar-A-grid.png) squeezed the figure into 62 x 62 by nearest - the face lost,
the body stretched tall - so it is NOT used. The raw is read on its own squares (design_fiora_hd.grid, alpha under 128
dropped), cut to colours by k-means, the outline closed where the read lost it, and kept as drawn: its rows from the
horn's tip to the soles over his 1x sprite's 40 make the PPU (~1.5, as asked).
-> hd/design.png. With --review DIR: <dir>/rengar_ppu_size.png (the design beside this pack's PPU 1.5 heroes and Rengar
now, as the game draws them, hd.rs SIZES applied) and <dir>/rengar_ppu_closeup.png (Codex's picture | the read).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_ahri_hd as AH  # noqa: E402
import design_fiora_hd as FD  # noqa: E402
import strips as G  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
AH.HD = os.path.join(ROOT, "assets", "source", "rengar", "hd")
AH.RAW, AH.PITCH = "rengar-A.png", (12.0, 17.0)  # its own square (~15.1 x 14.6 px)
OLD = 40                        # his 1x idle, the horn's tip to his soles
PEERS = ["rengar", "leesin", "udyr", "xinzhao", "khazix"]


def read():
    """Codex's picture on its own squares, cut to colours, its outline closed, cropped - his tail as Codex drew it."""
    q, pal, _ = AH.native()
    # where the read lost Codex's outline: closed again in the outline colour (strips.complete_outline)
    out = AH.outline_of(pal)
    q = G.complete_outline(q, color=out)[0]
    # and the dark squares on the rim (the outline averaged with what it rings) the outline colour
    op = q[..., 3] > 0
    rim = op & ~ndimage.binary_erosion(op, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    q[rim & (q[..., :3].astype(int).sum(-1) < 170), :3] = out
    ys, xs = np.nonzero(q[..., 3])
    return q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def box(full):
    ys, xs = np.nonzero(full[..., 3])
    return slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)


def bare():
    """The design without a tail, cut as the design is (the rig draws the tail on its sunk frames: the root sinks with
    him, the end stays on the ground; and the point between his feet is measured on it - the tail's end lies there)."""
    q = read()
    return untail(q, FRONT)[box(retail(q))]


def design():
    q = read()
    full = retail(q)
    return full[box(full)], q.shape[0] / OLD


# The tail. Codex drew it in front of him - curled up right of his far hand, its end behind the hand - after the design
# prompt misread his old sprite (「尾巴从身后卷到右下」); in game it read as growing out of the hand (「怎么尾巴在手上？」, then
# 「尾巴还是不对」 once a root had been drawn on from the hand). League's Rengar and his old sprite have it behind him: a
# thin tail out of his rump hanging to the ground behind his back foot (the old sprite showed only its white end on the
# ground there). So the front tail is taken off (untail) and one drawn behind him (tail): out of his rump, down behind
# the near leg and the claw, along the ground behind his back foot to a gold ring and a white tuft - painted only where
# the picture is empty, so the leg and the claw stay in front of it.
H = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # noqa: E731
OUTLINE = H("0b0009")
BLUES = tuple(H(c) for c in ("9ea5c8", "7d86b1", "67719d", "525b85"))     # the tail's blues, lit -> shade
GOLDS = tuple(H(c) for c in ("fccf20", "fcbf07", "dd7410"))              # its ring
WHITES = (H("f6f6f6"), H("c3c7de"))                                         # its tuft
# what Codex drew the front tail in: its blues, the tuft's whites, the ring's golds
TAIL_COLS = tuple(H(c) for c in ("9ea5c8", "7d86b1", "67719d", "525b85", "3b4165", "c3c7de", "f6f6f6", "fcbf07",
                                 "f89f06", "fccf20", "dd7410", "fbaf06", "ed880b"))
FRONT = (20, 43, 63, 76)        # the design's front tail: rows 20-42, columns 63-75 (right of the far hand)
BACK = ((43, 25), (48, 20), (53, 17), (56, 15), (57, 9), (56.6, 3))      # its new tail (row, column) Bezier points


def colour_in(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == c).all(-1)
    return m & (a[..., 3] > 0)


def untail(a, box, grow=6):
    """a without the tail drawn in box (r0, r1, c0, c1): the tail-coloured pieces reaching into the box, followed up to
    `grow` squares out of it, and the outline round them that rings nothing else; then, round what was taken off, the
    outline left hanging (no fill next to it) trimmed and the bits cut loose from the body (inside the grown box)
    dropped."""
    r0, r1, c0, c1 = box
    ok = colour_in(a, TAIL_COLS)
    inbox, near = np.zeros_like(ok), np.zeros_like(ok)
    inbox[max(0, r0):r1, max(0, c0):c1] = True
    near[max(0, r0 - grow):r1 + grow, max(0, c0 - grow):c1 + grow] = True
    lbl, _ = ndimage.label(ok & near)
    m = np.isin(lbl, list(set(np.unique(lbl[ok & inbox])) - {0}))
    four = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    line = colour_in(a, [OUTLINE])
    other = (a[..., 3] > 0) & ~m & ~line
    ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & line & ~ndimage.binary_dilation(other, structure=four)
    q = a.copy()
    q[m | ring] = 0
    zone = ndimage.binary_dilation(m | ring, structure=np.ones((3, 3)), iterations=2)
    while True:
        line = colour_in(q, [OUTLINE])
        fill = (q[..., 3] > 0) & ~line
        hang = zone & line & ~ndimage.binary_dilation(fill, structure=np.ones((3, 3)))
        if not hang.any():
            break
        q[hang] = 0
    op = q[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        main = int(np.argmax(ndimage.sum(op, lbl, range(1, n + 1)))) + 1
        for k in range(1, n + 1):
            if k != main and not ((lbl == k) & ~near).any():
                q[lbl == k] = 0
    return q


def bezier(ctrl, n=400):
    P = [np.array(c, float) for c in ctrl]
    out = []
    for t in np.linspace(0, 1, n):
        Q = P
        while len(Q) > 1:
            Q = [Q[i] * (1 - t) + Q[i + 1] * t for i in range(len(Q) - 1)]
        out.append(Q[0])
    return np.array(out)


def tail(a, ctrl, ground=None, r0=1.5, r1=1.15, ring=(0.70, 0.77), tuft=0.80, tuft_w=1.9):
    """a with the tail along the Bezier ctrl [(row, column) ...] drawn where a is empty: r0 -> r1 squares from its
    middle line, a gold ring over `ring` (of its length), a white tuft from `tuft` to its end (a teardrop, tuft_w at its
    widest), its upper side lit, outlined; nothing on rows from `ground` down (the soles' line)."""
    q = a.copy()
    pts = bezier(ctrl)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    T = np.r_[0, np.cumsum(seg)] / seg.sum()
    tan = np.gradient(pts, axis=0)
    nrm = np.stack([-tan[:, 1], tan[:, 0]], 1) / np.maximum(1e-9, np.hypot(*tan.T))[:, None]
    nrm[nrm[:, 0] > 0] *= -1                                   # each normal pointing up the picture: the lit side
    for y in range(max(0, int(pts[:, 0].min()) - 4), min(q.shape[0], int(pts[:, 0].max()) + 5)):
        if ground is not None and y >= ground:
            continue
        for x in range(max(0, int(pts[:, 1].min()) - 4), min(q.shape[1], int(pts[:, 1].max()) + 5)):
            if q[y, x, 3]:
                continue
            c = np.array([y + 0.5, x + 0.5])
            d = np.hypot(*(pts - c).T)
            i = int(np.argmin(d))
            t = T[i]
            if t < tuft:
                r = r0 + (r1 - r0) * t / tuft
            else:
                s = (t - tuft) / (1 - tuft)
                r = max(0.4, tuft_w * max(0.0, np.sin(np.pi * (0.25 + 0.75 * s))) ** 0.8)
            if d[i] > r + 1.0:
                continue
            if d[i] > r:
                q[y, x] = (*OUTLINE, 255)
                continue
            side = (c - pts[i]) @ nrm[i] / r                    # +1 its top edge, -1 its bottom edge
            if t >= tuft:
                col = WHITES[0] if side > -0.35 else WHITES[1]
            elif ring[0] <= t <= ring[1]:
                col = GOLDS[0] if side > 0.3 else GOLDS[1] if side > -0.4 else GOLDS[2]
            else:
                col = BLUES[0] if side > 0.55 else BLUES[1] if side > 0.0 else BLUES[2] if side > -0.55 else BLUES[3]
            q[y, x] = (*col, 255)
    return q


def retail(q):
    return tail(untail(q, FRONT), BACK, ground=q.shape[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    d, ppu = design()
    Image.fromarray(d).save(AH.lp(os.path.join(AH.HD, "design.png")))
    print(f"design {d.shape[1]}x{d.shape[0]} = PPU {ppu:.3f} at {OLD} rows, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    from preview_dense import SIZES
    os.makedirs(a.review, exist_ok=True)
    cells = [(f"new: {d.shape[0] / ppu:.1f}px (PPU {ppu:.2f})", FD.shown(Image.fromarray(d), ppu, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        k = SIZES.get(h, 1.0)
        cells.append((("now" if h == "rengar" else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "rengar_ppu_size.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("Codex's picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, "rengar_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
