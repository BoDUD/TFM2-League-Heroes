#!/usr/bin/env python3
"""Milio's dense design (the boy of his first design with League's backpack added): Codex's picture drawn from
tools/art/pack_milio_ppu.py's pack (the fluffy dark indigo curls, the big amber eyes and the grin, the red tunic with
the golden shoulder pads and cream tassels, the teal sash, the magenta kilt, the sandals, League's big gourd-shaped
backpack (cream canvas, teal scale bands, gold trims, the teal cap, the purple rope he grips at his chest, the wooden
frame) and, apart above it, his round fire spirit) read back on its own squares, design_khazix_hd's way.

    python tools/art/design_milio_v2.py [--pitch P] [--spirit] [--review DIR]

Codex delivered (2026-11-09, Documents/Codex/2026-11-09/new-chat/outputs/milio_ppu_done.zip, the five of this PR
together) milio-ppu/raw/milio-original.png - its raw generation: 1254 x 1254 with soft alpha, not cut to 6-px squares,
kept as hd/raw/milio-A.png (Codex's own milio-A.png is that re-placed on 6-px squares by nearest-neighbour sampling: not
read). Its squares drift (no one grid fits the whole picture) and its outline is about two of them thick - so it is read
at 3 pitches (PITCHES: 11.83 px ~ PPU 2.2, 9.91 px ~ PPU 2.65, 14.58 px ~ PPU 1.8) for the user to choose from, the face
on the same snapped lines (FACES empty: batch 4 found each square's mean dulls small eyes into what rings them).
Syndra's reader: the grid fitted (design_fiora_hd.fit, PITCH), each line snapped to the strongest colour edge near it,
each square the palette colour most of its middle has, the outline closed where the read lost it. Its rows from the top
of his hair to his soles over his 1x sprite's 33 make the PPU (the user, 2026-11-09: 「再补一个吧 米利欧 现在我们做的背后没有葫芦」). The
picture holds the boy with his backpack and, apart above it, his fire spirit (a layer of its own in the rig): each is
read alone on the one palette (PART; --spirit), the boy's rows making the PPU.
The default read's backpack is the 14.58 read's (small_pack(): Codex drew it ~0.8 as big in every action frame).
-> hd/design.png (the default read) or hd/design_<raw>_p<pitch>.png (the spirit: the same with _spirit). With --review
DIR: <dir>/milio_ppu_size*.png (the design beside Veigar, Seraphine, Ezreal and his sprite now, as the game draws them)
and <dir>/milio_ppu_closeup*.png (the picture | the read).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_ahri_hd as AH  # noqa: E402
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402
import strips as G  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
AH.HD = os.path.join(ROOT, "assets", "source", "milio", "hd")
# the user's picks (2026-11-09): 「泽丽2.1 佐伊2.64 米利欧2.21 其他都1.8」
AH.RAW, AH.PITCH = "milio-A.png", (11.77, 11.89)    # 11.83 px, the user's pick: PPU 2.21
# per picture: the squares read at (px range) and how far a line may snap to a colour edge (under half a square)
PITCHES = {"milio-A.png": {"11.83": ((11.77, 11.89), 5), "9.91": ((9.85, 9.97), 4), "14.58": ((14.52, 14.64), 7)}}
DEFAULT = ("milio-A.png", "11.83")
# per picture: the face (x0, y0, x1, y1 px of the picture) read by the uniform grid at every pitch - none here: each
# square's mean dulls small eyes into what rings them (batch 4: Kha'Zix's maw, Blitzcrank's and Lillia's eyes); the
# snapped lines keep them (Kennen's and Lissandra's way)
FACES = {}
# per picture: thin lines the squares cut into dashes, the line's colour as (r, g, b) bounds, laid on the grid along
# their skeletons (thin_lines()) - none here
THIN = {}
THIN_WIDTH, THIN_LENGTH = 10, 100
PART = "boy"                    # the boy with his backpack (the largest piece) or "spirit" (every other
                                # piece): apart in the picture, read alone (part_mask())
AH.COLOURS = 64                 # (as Talon's)
OLD = 33                        # his 1x idle_base, the top of his hair to his soles
PEERS = ["milio", "veigar", "seraphine", "ezreal"]


SNAP = 5                        # px a grid line may move to the strongest colour edge near it
FACE = None                     # px box of the picture read by the uniform grid (None: the snapped lines)
CORE = 0.2                      # each square's colour is read from its middle (this much of it off each side)
FACE_DARK = 0.5                 # in the face, a square this much near-black is a dark line's (native())
FACE_GLOW = 0.15                # in the face, a square this much glowing amber is the eyes (native()): the mean with
                                # the brown skin round them dulls small glowing eyes to dark dots (Aatrox's fix, the
                                # user: 「剑魔的头看起来只看后面」)


def lines(e, pitch, phase, n):
    """The square boundaries along one axis: the fitted grid (pitch, phase), each line moved to the strongest colour
    edge within SNAP px of it - Codex's squares drift up to half a square off one grid across the picture."""
    out = []
    for x in np.arange(phase, n, pitch):
        c = int(round(x))
        lo, hi = max(0, c - SNAP), min(n, c + SNAP + 1)
        w = e[lo:hi]
        best = lo + int(np.argmax(w - 0.01 * np.abs(np.arange(lo, hi) - c))) if w.size and w.max() > 0 else c
        if out and best - out[-1] < pitch * 0.6:
            best = c                    # (two lines on one edge: this one stays where the grid puts it)
        if not out or best - out[-1] >= pitch * 0.4:
            out.append(best)
    return out


def thin_lines(q, a, op, idx, pal, xs, ys):
    """THIN's lines laid on the grid in place: each thin component of the line colour skeletonised, the square under
    every skeleton pixel the palette colour most of the component has - an unbroken line one square wide."""
    (r0, r1), (g0, g1), (b0, b1) = THIN[AH.RAW]
    rgb = a[..., :3].astype(int)
    m = op & (rgb[..., 0] >= r0) & (rgb[..., 0] <= r1) & (rgb[..., 1] >= g0) & (rgb[..., 1] <= g1) & \
        (rgb[..., 2] >= b0) & (rgb[..., 2] <= b1)
    lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
    for k, sl in enumerate(ndimage.find_objects(lbl), 1):
        c = lbl[sl] == k
        sk = skeletonize(c)
        if sk.sum() < THIN_LENGTH or c.sum() > THIN_WIDTH * sk.sum():
            continue
        col = pal[np.bincount(idx[sl][c], minlength=len(pal)).argmax()]
        sy, sx = np.nonzero(sk)
        j = np.searchsorted(ys, sy + sl[0].start, side="right") - 1
        i = np.searchsorted(xs, sx + sl[1].start, side="right") - 1
        ok = (j >= 0) & (j < q.shape[0]) & (i >= 0) & (i < q.shape[1])
        q[j[ok], i[ok], :3] = col
        q[j[ok], i[ok], 3] = 255


def part_mask(op):
    """The picture's pixels of PART: the boy with his backpack (its largest piece) or his fire spirit (every other
    piece) - apart in Codex's picture (18 px between them), not always in a coarse read, so cut before the read."""
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    boy = lab == 1 + int(np.argmax(ndimage.sum(op, lab, range(1, n + 1))))
    return boy if PART == "boy" else op & ~boy


def native():
    """The picture on its own squares: the palette (48 colours) from a first read on the fitted grid
    (design_ahri_hd.native), every raw pixel snapped to it (Lab), then each square - between the snapped lines - the
    palette colour most of its middle pixels have (one of the drawing's colours, never a blend of two squares)."""
    first, pal, _ = AH.native()
    a = np.asarray(Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    op = part_mask(a[..., 3] > 0)                # (the boy or his spirit)
    a[~op] = 0
    lab = V.srgb2lab(a[op][:, :3].astype(float))
    plab = V.srgb2lab(pal.astype(float))
    idx = np.full(a.shape[:2], -1)
    idx[op] = np.concatenate([((lab[i:i + 200000, None] - plab[None]) ** 2).sum(-1).argmin(1)
                              for i in range(0, len(lab), 200000)])
    FD.PITCH = AH.PITCH
    (px, phx), (py, phy) = FD.fit(a, op, 1), FD.fit(a, op, 0)
    xs = lines(FD.RG.profile(a, op, 1), px, phx, a.shape[1])
    ys = lines(FD.RG.profile(a, op, 0), py, phy, a.shape[0])
    q = np.zeros((len(ys) - 1, len(xs) - 1, 4), np.uint8)
    for j in range(len(ys) - 1):
        y0, y1 = ys[j], ys[j + 1]
        dy = int((y1 - y0) * CORE)
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            dx = int((x1 - x0) * CORE)
            win = idx[y0 + dy:y1 - dy, x0 + dx:x1 - dx].ravel()
            if (win >= 0).sum() * 2 <= win.size:
                continue
            q[j, i, :3] = pal[np.bincount(win[win >= 0], minlength=len(pal)).argmax()]
            q[j, i, 3] = 255
    if AH.RAW in THIN:
        thin_lines(q, a, op, idx, pal, xs, ys)
    q = FD.crop(q)
    if FACE is None:
        return q, pal
    # the face: the snapped lines lean on the strong edges round it and lose the eyes and the mouth; on the uniform
    # grid laid over the figure's box (its rows / the read's rows) each square the palette colour nearest the mean of
    # all its pixels (Lab) - Codex's ~8-10 px strokes (the eyes, the lashes, the mouth, the grin's teeth) run across
    # squares, under half of each, and a majority loses them - or, past FACE_DARK of it near-black, the dark colour
    # nearest that mean (the line itself)
    ys_, xs_ = np.nonzero(op)
    by, bx = ys_.min(), xs_.min()
    ky, kx = (ys_.max() + 1 - by) / q.shape[0], (xs_.max() + 1 - bx) / q.shape[1]
    fx0, fy0, fx1, fy1 = FACE
    labs = np.zeros(a.shape[:2] + (3,))
    labs[op] = lab
    black = op & (a[..., :3].max(-1) < 70)
    rgb_ = a[..., :3].astype(int)
    glow = op & (rgb_[..., 0] >= 220) & (rgb_[..., 1] >= 140) & (rgb_[..., 2] <= 80)   # his amber eyes
    dark = np.flatnonzero(pal.max(-1) < 70)             # the palette's near-black (outline) colours
    r0, r1 = int((fy0 - by) / ky), int(np.ceil((fy1 - by) / ky))
    c0, c1 = int((fx0 - bx) / kx), int(np.ceil((fx1 - bx) / kx))
    for j in range(r0, r1):
        for i in range(c0, c1):
            y0, y1 = int(by + j * ky), int(np.ceil(by + (j + 1) * ky))
            x0, x1 = int(bx + i * kx), int(np.ceil(bx + (i + 1) * kx))
            w = op[y0:y1, x0:x1]
            if w.sum() * 2 <= w.size:
                q[j, i] = 0
                continue
            g = glow[y0:y1, x0:x1] & w
            if g.sum() >= FACE_GLOW * w.sum():         # an eye: its own glowing colour, not the mean with the black round it
                m = labs[y0:y1, x0:x1][g].mean(0)
                q[j, i, :3] = pal[((plab - m) ** 2).sum(-1).argmin()]
                q[j, i, 3] = 255
                continue
            m = labs[y0:y1, x0:x1][w].mean(0)
            near = dark if black[y0:y1, x0:x1].sum() >= FACE_DARK * w.sum() else np.arange(len(pal))
            q[j, i, :3] = pal[near[((plab[near] - m) ** 2).sum(-1).argmin()]]
            q[j, i, 3] = 255
    return q, pal


def read():
    """Codex's picture on its own squares, cut to colours, its outline closed, cropped - as Codex drew it."""
    q, pal = native()
    # where the read lost Codex's outline: closed again in the outline colour (strips.complete_outline)
    out = AH.outline_of(pal)
    q = G.complete_outline(q, color=out)[0]
    # and the dark squares on the rim (the outline averaged with what it rings) the outline colour
    op = q[..., 3] > 0
    rim = op & ~ndimage.binary_erosion(op, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    q[rim & (q[..., :3].astype(int).sum(-1) < 170), :3] = out
    ys, xs = np.nonzero(q[..., 3])
    return q[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def design():
    q = read()
    return q, q.shape[0] / OLD


# The backpack in every action frame Codex drew (casts_milio_hd) is ~0.8 as big as in this picture (its own colours'
# squares and its box, his curls as big as here) - and the idle is this design held between snippets of those actions,
# so the pack would shrink and grow (the user, 2026-11-09: 「千万别出现模型一大一小的问题」). The default read takes its
# backpack from the read at PACK_PITCH (11.83 / 14.58 = 0.81 of the boy's size), behind the boy of its own read: the
# foot of the pack's frame (PACK_FOOT, a square of the 11.83 read) kept where it was, PACK_IN squares in under his back
# (it sits against him, as in the actions), the pack's colours the 11.83 read's nearest (one palette).
PACK_PITCH = "14.58"
PACK_FOOT = (59, 27)
PACK_IN = (0, 2)
# the boy from these squares of the 11.83 read rightwards, by rows (read off it at 18x: his hair's left edge, the rope
# over his shoulder, his sleeve, the hand gripping the frame, his back, his legs); left of that the backpack
BOY_FROM = [(0, 20, 26), (20, 24, 28), (24, 26, 27), (26, 34, 28), (34, 39, 23), (39, 56, 28), (56, 999, 27)]
BOY_CUT = 24                    # his own colours: 90 % of their squares or more right of this column of the read
GAP = 2                         # squares of ground between the pack and his back filled with the outline colour


def boy_from(y):
    return next(x for a, b, x in BOY_FROM if a <= y < b)


def own_colours(q, cut):
    """The boy's own colours in a read: 4 squares or more, 90 % of them or more right of `cut`, not near-black."""
    op = q[..., 3] > 0
    cols, inv = np.unique(q[op][:, :3], axis=0, return_inverse=True)
    xs = np.nonzero(op)[1]
    keep = []
    for i, c in enumerate(cols):
        x = xs[inv.ravel() == i]
        if (x >= cut).sum() >= 4 and (x >= cut).sum() >= 0.9 * len(x) and c.max() >= 60:
            keep.append(c)
    return np.array(keep, int).reshape(-1, 3)


def small_pack(fine, coarse):
    """(the design, the columns cropped off its left): the fine read's boy over the coarse read's backpack."""
    pf, pc = float(DEFAULT[1]), float(PACK_PITCH)
    hf, wf = fine.shape[:2]
    hc, wc = coarse.shape[:2]
    boy = np.zeros((hf, wf), bool)
    for y in range(hf):
        boy[y, boy_from(y):] = True
    boy &= fine[..., 3] > 0
    # the coarse read's pack: left of the same line carried over (a point of the picture maps between the two reads by
    # the bottom-right corner they share - his front and his soles), less the boy's own colours there, its largest piece
    pack = np.zeros((hc, wc), bool)
    for y in range(hc):
        fy = max(0, int(hf + (y + 0.5 - hc) * pc / pf))
        pack[y, :max(0, int(np.floor(wc + (boy_from(fy) - wf) * pf / pc)))] = True
    own = own_colours(coarse, int(round(wc + (BOY_CUT - wf) * pf / pc)))
    rgb = coarse[..., :3].astype(int)
    mine = (np.abs(rgb[:, :, None, :] - own[None, None]).sum(-1) == 0).any(-1)
    pack &= (coarse[..., 3] > 0) & ~mine
    lbl, n = ndimage.label(pack, structure=np.ones((3, 3)))
    pack = lbl == 1 + int(np.argmax(ndimage.sum(pack, lbl, range(1, n + 1))))
    # its colours the fine read's nearest (Lab)
    pal = np.unique(fine[fine[..., 3] > 0][:, :3], axis=0)
    plab = V.srgb2lab(pal.astype(float))
    src = coarse.copy()
    ys, xs = np.nonzero(pack)
    lab = V.srgb2lab(src[ys, xs, :3].astype(float))
    src[ys, xs, :3] = pal[((lab[:, None] - plab[None]) ** 2).sum(-1).argmin(1)]
    fy, fx = PACK_FOOT
    oy = int(round(fy - (hc + (fy - hf) * pf / pc))) + PACK_IN[0]
    ox = int(round(fx - (wc + (fx - wf) * pf / pc))) + PACK_IN[1]
    m = 4
    can = np.zeros((hf + 2 * m, wf + 2 * m, 4), np.uint8)
    can[ys + oy + m, xs + ox + m] = src[ys, xs]
    in_pack = np.zeros(can.shape[:2], bool)
    in_pack[ys + oy + m, xs + ox + m] = True
    by, bx = np.nonzero(boy)
    can[by + m, bx + m] = fine[by, bx]
    in_boy = np.zeros(can.shape[:2], bool)
    in_boy[by + m, bx + m] = True
    # ground left between the pack and his back (GAP squares or fewer in a row): the outline colour, where they meet
    dark = pal[pal.max(1) < 40]
    ocol = dark[np.argmax([((fine[..., :3] == c).all(-1) & (fine[..., 3] > 0)).sum() for c in dark])]
    for y in range(can.shape[0]):
        px, bxs = np.nonzero(in_pack[y])[0], np.nonzero(in_boy[y])[0]
        if not len(px) or not len(bxs):
            continue
        a, b = px.max() + 1, bxs[bxs > px.max()].min() if (bxs > px.max()).any() else None
        if b is not None and 0 < b - a <= GAP and not (can[y, a:b, 3] > 0).any():
            can[y, a:b, :3] = ocol
            can[y, a:b, 3] = 255
    ys, xs = np.nonzero(can[..., 3])
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1], xs.min() - m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=DEFAULT[0], choices=sorted(PITCHES))
    ap.add_argument("--pitch", help="one of the picture's PITCHES (default: its first)")
    ap.add_argument("--spirit", action="store_true", help="read his fire spirit, not the boy")
    ap.add_argument("--review")
    a = ap.parse_args()
    global SNAP, FACE, PART
    p = a.pitch or (DEFAULT[1] if a.raw == DEFAULT[0] else next(iter(PITCHES[a.raw])))
    FACE = FACES.get(a.raw)
    AH.RAW = a.raw
    PART = "spirit" if a.spirit else "boy"
    AH.PITCH, SNAP = PITCHES[a.raw][p]
    d, ppu = design()
    stem = ("design" if (a.raw, p) == DEFAULT else f"design_{a.raw[:-4]}_p{p}") + ("_spirit" if a.spirit else "")
    if stem == "design":
        # the backpack as the actions draw it (small_pack()); the read with Codex's own backpack: design_bigpack.png
        Image.fromarray(d).save(AH.lp(os.path.join(AH.HD, "design_bigpack.png")))
        AH.PITCH, SNAP = PITCHES[a.raw][PACK_PITCH]
        coarse = read()
        AH.PITCH, SNAP = PITCHES[a.raw][p]
        d, left = small_pack(d, coarse)
        print(f"backpack from the {PACK_PITCH} read: {left} columns off the left")
    tail = "" if stem == "design" else stem[len("design"):]
    Image.fromarray(d).save(AH.lp(os.path.join(AH.HD, stem + ".png")))
    print(f"design {d.shape[1]}x{d.shape[0]} = PPU {ppu:.3f} at {OLD} rows, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if a.spirit or not a.review:          # (the size review: the boy)
        return
    from preview_dense import SIZES
    os.makedirs(a.review, exist_ok=True)
    cells = [(f"new: {d.shape[0] / ppu:.1f}px (PPU {ppu:.2f})", FD.shown(Image.fromarray(d), ppu, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        k = SIZES.get(h, 1.0)
        cells.append((("now" if h == PEERS[0] else h) + (f" {p}" if p != 1 else " 1x") + (f" x{k}" if k != 1 else ""),
                      FD.shown(f, p / k, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, f"milio_ppu_size{tail}.png"))
    raw = Image.open(AH.lp(os.path.join(AH.HD, "raw", AH.RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 700 / d.shape[0]
    close = [("the picture", raw.resize((round(raw.width * 700 / raw.height), 700), Image.LANCZOS)),
             (f"design {d.shape[1]}x{d.shape[0]}", FD.shown(Image.fromarray(d).resize((round(d.shape[1] * z), 700),
                                                                                    Image.NEAREST), 1, 1))]
    FD.strip(close).convert("RGB").save(os.path.join(a.review, f"milio_ppu_closeup{tail}.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
