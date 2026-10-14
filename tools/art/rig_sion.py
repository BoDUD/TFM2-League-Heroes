#!/usr/bin/env python3
"""league_sion's sheets from Codex's step-2 strips (assets/source/sion/codex_strips) and the PPU design (hd/front.png).

    python tools/art/rig_sion.py [--review DIR] [--frames-only]

Codex drew 36 action frames on the pack's 7-px grid (tools/art/pack_sion_strips.py: 219 x 146 squares, the standing
point column PIV_X, the soles' row SOLE; the design pasted at DESIGN_AT), in the design's 27 colours, and pasted the
design's head into every frame by translation (its HEAD_POLY). Here, for every frame:
  * the size: Codex's bodies came out 5-22 % bigger than the design's (the parts' areas: skin, trousers, loin cloth),
    while its closing frames are the design itself - the hero swelled on every cast and shrank back. Each action's
    frames are brought to the design's size by one factor (SCALE: 1 / the median of its frames' measures,
    body_scale()), as tools/art/design_sion.py brought the design down: whole rows and columns deleted, the ones most
    like their neighbours, evenly spread (design_riven.pick), the soles kept on SOLE and the standing column on PIV_X;
    the head is taken out first and pasted back the design's size on the shrunken neck (one face, one size);
  * the outline closed where the cut or the paste left it open (strips.complete_outline + close_all), loose specks
    cleared, pinholes filled (specks, pinholes);
  * W (skill2_w): Codex's frame 2 swung the axe overhead and drew the far gauntlet as a block - dropped; the flex is
    frames 1, 3, 3 (held), then the design;
  * idle = the design breathing (the upper body BREATH rows up over the legs), hit = the design moved 2 and 1 squares
    back, run = the design walking league_nautilus / league_braum's way (walk_frame; the user: 「你向前那样冲刺模型永远会变形」),
    ult (R's charge) = Codex's charge pose, its upper body bobbing over its planted legs (ULT_BOB).
The canvas is the game's density (PPU 1.52: the design's 67 squares crown to soles for 44 game px). Each frame is then
written twice (tools/art/rig_bard.py's way): the dense frame (the canvas itself round the pivot -> assets/source/ppu/
sion_<tag>.png + .json, ppu_hd.py's drawn strips) and the 1x frame (pixel_down.pixelate at 1 / PPU) for the sheet's
plain tags; `python tools/art/ppu_hd.py --hero sion` then adds the hd_ / lo_ tags.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import design_riven as R  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sion")
CODEX = os.path.join(SRC, "codex_strips")
DESIGN = os.path.join(SRC, "hd", "front.png")
FRAMES = os.path.join(SRC, "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_sion")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
PPU = 1.52                      # canvas squares a game pixel (design_sion.HD_PPU)
FEET = 11                       # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
# On the battlefield he is drawn at SIZE of the 1x size (addons/league_main/src/hd.rs SIZES; the user, 2026-10-14:
# 「模型太大了吧 和铁男差不多大就行了吧」 -> 80 % (Mordekaiser's body area on a true-scale sheet), then 「调成90%」 ->
# 90 %, 1.69 squares a game pixel): the DLL scales about the frame's centre, so every dense frame is drawn SHIFT rows
# lower - the soles, (FEET + 0.5) x PPU under the pivot, land there again (tools/art/rig_braum.py's way)
SIZE = 0.90
SHIFT = round((FEET + 0.5) * PPU * (1 / SIZE - 1))
COLS, ROWS = 219, 146
PIV_X, SOLE = 100, 140          # pack_sion_strips.py
DESIGN_AT = (43, 66)            # the design's top-left on the canvas (pack_sion_strips.py's print)
OUTLINE = (8, 7, 7)
# the head object Codex pasted by translation (its restore_strip_heads.py): stake, ribbon, bald head, jaw cage - in
# design coordinates (x, y)
HEAD_POLY = [(40, 0), (60, 0), (60, 8), (63, 10), (65, 14), (65, 20), (62, 24), (56, 24), (52, 21), (50, 19), (50, 14),
             (40, 14)]
NECK = (22, 57)                 # the design's jaw bottom (row, col): the head sits on the neck there
# the body parts whose areas measure a frame's size against the design's (the head is the design's in every frame)
SKIN = [(157, 158, 188), (125, 110, 151), (189, 202, 219), (209, 222, 235), (94, 69, 112)]
CLOTH = [(108, 97, 55)]
TROUSERS = [(117, 61, 32), (91, 47, 25), (71, 23, 37), (48, 18, 27), (78, 51, 42), (51, 31, 27)]
# Codex's frames per tag (its file numbers) in the order the tag plays them; "design" = the design itself (the
# closing frames Codex took from the design)
TAGS = {
    "attack": [1, 2, 3, 4, "design"],
    "skill_charge": [1, 2, 3, 4],
    "skill": [1, 2, 3, 4, "design"],
    "skill2": [1, 2, 3, 4, "design"],
    "skill2_w": [1, 3, 3, "design"],
    "ult_hit": [1, 2, 3, 4, "design"],
    "dead": [1, 2, 3, 4, 5, 5],
}
# frame times (ms): the pack's cells.json; skill2_w: frame 2 dropped, frame 3 shown in its place and held
MS = {
    "attack": [70, 80, 60, 90, 110], "skill_charge": [130, 170, 170, 200], "skill": [60, 60, 80, 100, 100],
    "skill2": [60, 70, 90, 90, 100], "skill2_w": [60, 90, 120, 120], "ult_hit": [60, 60, 80, 100, 120],
    "dead": [100, 120, 150, 150, 200, 400],
}
# frames still bigger than their neighbours after their tag's factor, by eye and measure (body_scale): Q's slam frame 1
# came out 13 % over the charge it follows (both arms up, shoulders wider) - shrunk again by this much
SCALE_FIX = {("skill", 1): 0.91}
BREATH = [0, 1, 2, 2, 1, 0]
IDLE_MS = 160
# the design's legs (rows, columns; ends exclusive): under the belt (WALK_BAND), clear of the axe blade at the near
# side and of the far hand hanging beside the far thigh
WALK_BAND = 52
WALK_NEAR = ((53, 62, 31, 50), (62, 75, 28, 50))
WALK_FAR = ((53, 63, 61, 81), (63, 75, 61, 87))
CLOTH_BOX = ((53, 75, 50, 61),)       # the loin cloth between them: it hangs from the belt, it does not breathe
# per frame: the near leg's (columns forward, rows lifted), the far leg's, the figure's rise (canvas squares:
# league_nautilus's 1x steps x PPU, as league_galio's)
WALK = [((0, 0), (0, 3), 2), ((0, 0), (2, 5), 3), ((0, 0), (2, 2), 2), ((0, 0), (2, 0), 0),
        ((0, 3), (0, 0), 2), ((2, 5), (0, 0), 3), ((2, 2), (0, 0), 2), ((2, 0), (0, 0), 0)]
WALK_MS = 115
CRACK = 3                       # bare squares a step opens, this many columns wide at most: a crack
SPECK = 8
PINHOLE = 6
# R's charge: Codex's charge pose (ult 1, brought to the design's size by its own measure) is a sprint stride, one foot
# off the ground - the user's rule for the big heroes: no sprint (「你向前那样冲刺模型永远会变形」). Its upper body charges on
# the design's own legs walking (walk_frame's steps): its legs (canvas rows from ULT_CUT[0], columns ULT_CUT[1]..[2]) go,
# the rest is moved ULT_SHIFT (rows, columns) so its belt's lower edge sits on the design's (WALK_BAND) over the legs'
# middle; the near arm with the axe and the far arm hanging beside the far leg stay as drawn.
# Cut at its chest (the reviewer: its near thigh, drawn beside its belt, stacked a second thigh and knee over the
# design's): the design's waist under it (ULT_WAIST: belt and furnace, design rows, columns), the legs from the belt.
ULT_CUT = (101, 73, 130)
ULT_WAIST = ((38, 53, 36, 70),)       # from column 36: the design's haft top stays out
ULT_SHIFT = (5, -8)
ULT_MS = 104                    # 8 steps over R's 50-tick charge
# the design's far boot (canvas rows, columns of the idle) for a far leg Codex left off at the knee
FAR_BOOT = (128, 141, 105, 129)
# hand fixes after the review (2026-10-14, an independent reviewer's 12 defects), on each Codex frame after its cut and
# paste, before tidy - (tag, play position from 1) -> operations in order:
#   ("clear", (x0, y0, x1, y1)): every square in the box (inclusive) but the pasted head's own is cleared - Codex's old
#       stake, skull-top and neck lines beside the pasted head (tidy outlines what they leave);
#   ("lower", k): the frame k rows down, nothing under SOLE (the planted boots on the ground; a blade on it bites in);
#   ("legs", b0, n[, (r0, r1)]): n whole rows taken from rows b0..SOLE-1, the least loss (legs Codex drew too long),
#       rows r0..r1 kept (the bone ring beside the legs: the trim flattened it);
#   ("boot", x0): the design's far boot behind the frame, its sole on SOLE from column x0 (Q's slam: the far leg ended at
#       the knee);
#   ("stake",): Codex's wider stake beside the pasted one cleared (stake());
#   ("neck", x0, x1, y0): Codex's neck lines beside the jaw cleared down to the shoulder (neck());
#   ("axe", box, ring[, "ring"]): the blade inside box taken out and put back last, where its foot went, at most the
#       design's size (the reviewer: up to 382 squares of steel against the design's 247); ring: its foot's (row,
#       column) when the bone ring is hidden; "ring": it follows the bone ring (kept out of a leg trim) instead;
#   ("haft", box): after the blade is back, a slit between it and the haft filled with the haft's wood;
#   ("foot", x0, x1, y0, k): a boot Codex left floating set down k rows (foot());
#   ("fist", x0, y0): a fist (FIST) on the haft; ("pauldron", dy, dx): the design's pauldron, moved as the head
#       (E and W drew it a third smaller, as loose plates); ("plates", box): the forearm's wrap as iron plates;
#   ("cloth", box): the design's loin cloth for Codex's; ("slit", box): 1-square slits between limbs closed;
#   ("ring", box): a bone ring drawn bigger than the design's 6 x 6 swapped for the design's (after the axe is back);
#   ("stretch", x0, x1, y0, k): a floating lower leg drawn k rows longer down to the ground (stretch());
#   ("ink", [(x, y), ...]): squares that take the outline
FIX = {
    # the axe's second spike over its head, the haft's butt past the arm and two lone line squares (it read
    # double-headed); a fist on the haft
    ("attack", 1): [("clear", (61, 40, 73, 48)), ("clear", (68, 49, 73, 54)), ("clear", (89, 59, 94, 68)),
                    ("clear", (60, 47, 60, 47)), ("clear", (93, 69, 93, 69)), ("fist", 70, 55)],
    ("attack", 2): [("legs", 109, 8), ("cloth", (92, 112, 114, 132)), ("ink", [(113, 130), (114, 130), (113, 119),
                                                                            (113, 120)])],
    # the haft came out of the crotch: a fist on it; the back lower leg set on the ground along its slope
    ("attack", 3): [("fist", 112, 111), ("stretch", 58, 90, 116, 3), ("stretch", 112, 127, 118, 4)],
    ("attack", 4): [("axe", (156, 113, 196, 141), None), ("lower", 3), ("stretch", 105, 125, 116, 3),
                    ("ring", (156, 118, 176, 137))],
    ("skill_charge", 1): [("stake",), ("slit", (123, 113, 130, 120)), ("axe", (24, 60, 53, 96), None)],
    ("skill_charge", 2): [("axe", (24, 52, 58, 88), None)],
    ("skill", 1): [("slit", (68, 67, 75, 75)), ("slit", (75, 72, 81, 82)), ("ring", (64, 70, 82, 86))],
    ("skill", 2): [("clear", (88, 69, 101, 71)), ("axe", (141, 90, 181, 131), None), ("legs", 111, 6),
                   ("stretch", 57, 88, 122, 1), ("ring", (144, 100, 162, 120))],
    ("skill", 3): [("lower", 12), ("boot", 124), ("ring", (138, 125, 158, 141))],
    ("skill", 4): [("stake",), ("lower", 13), ("boot", 124), ("ring", (138, 125, 158, 141))],
    ("skill2", 1): [("neck", 86, 91, 66), ("clear", (92, 68, 95, 73)), ("pauldron", 0, 0),
                    ("ink", [(91, 81), (91, 82), (92, 82), (93, 83)]), ("plates", (124, 95, 144, 101))],
    ("skill2", 2): [("neck", 91, 96, 62), ("clear", (97, 64, 100, 68)), ("pauldron", 0, 0),
                    ("axe", (38, 112, 80, 141), None), ("legs", 112, 5), ("plates", (128, 96, 151, 102)),
                    ("stretch", 69, 94, 120, 1)],
    ("skill2", 3): [("stake",), ("lower", 1), ("slit", (87, 104, 99, 115)), ("slit", (82, 117, 89, 123)),
                    ("slit", (117, 80, 128, 87))],
    ("skill2", 4): [("stake",), ("lower", 1)],
    ("skill2_w", 1): [("pauldron", 0, 0), ("plates", (132, 99, 148, 104)), ("stretch", 77, 100, 120, 1)],
    ("skill2_w", 2): [("neck", 100, 105, 67), ("clear", (58, 92, 70, 98)), ("clear", (65, 98, 68, 101)),
                      ("clear", (62, 98, 62, 99)), ("clear", (63, 99, 64, 99)), ("clear", (57, 96, 57, 96)),
                      ("pauldron", 0, 0), ("plates", (136, 91, 152, 97)), ("ring", (40, 95, 58, 112))],
    ("skill2_w", 3): [("neck", 100, 105, 67), ("clear", (58, 92, 70, 98)), ("clear", (65, 98, 68, 101)),
                      ("clear", (62, 98, 62, 99)), ("clear", (63, 99, 64, 99)), ("clear", (57, 96, 57, 96)),
                      ("pauldron", 0, 0), ("plates", (136, 91, 152, 97)), ("ring", (40, 95, 58, 112))],
    # (the scaled frame, before ULT_SHIFT) Codex's wrap bits under the near armpit
    ("ult", 1): [("stake",), ("clear", (80, 97, 84, 100)), ("axe", (20, 102, 66, 130), None)],
    ("ult_hit", 1): [("axe", (39, 106, 84, 126), None), ("legs", 111, 6)],
    ("ult_hit", 2): [("stake",), ("axe", (148, 117, 182, 141), None), ("lower", 1), ("ring", (145, 110, 162, 127))],
    # its blade keeps Codex's squares: lowered 6, the ground hides half of it, and the resized one cracked (the reviewer)
    ("ult_hit", 3): [("stake",), ("lower", 6), ("ring", (118, 114, 136, 136))],
    # the loin cloth swelled to 166 squares (the design's 99): the design's
    ("ult_hit", 4): [("cloth", (88, 108, 116, 136)), ("slit", (128, 108, 133, 113)), ("axe", (128, 122, 176, 141), None),
                     ("lower", 4), ("stretch", 108, 127, 122, 1)],
    ("dead", 1): [("neck", 83, 88, 59), ("axe", (38, 119, 74, 141), None, "ring"), ("legs", 109, 8, (115, 123)),
                  ("haft", (57, 131, 66, 137)),
                  ("cloth", (104, 112, 120, 128))],
    ("dead", 2): [("neck", 93, 98, 53), ("slit", (128, 93, 129, 96)), ("axe", (46, 117, 84, 141), None, "ring"),
                  ("legs", 107, 10, (112, 121)), ("lower", 1), ("clear", (99, 68, 99, 72)),
                  ("ink", [(76, 124), (75, 127)]), ("stretch", 83, 107, 118, 1)],
    ("dead", 3): [("slit", (91, 106, 94, 110))],
    ("dead", 4): [("neck", 97, 102, 66), ("clear", (103, 66, 106, 72))],
    ("dead", 5): [("stake",), ("slit", (93, 118, 97, 122))],
    ("dead", 6): [("stake",), ("slit", (93, 118, 97, 122))],
}


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def design():
    return load(DESIGN)


def on_canvas(d, dx=0, dy=0):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    x0, y0 = DESIGN_AT
    can[y0 + dy:y0 + dy + d.shape[0], x0 + dx:x0 + dx + d.shape[1]] = d
    return can


def head_mask(own=False):
    """The head object's squares in the design (HEAD_POLY, opaque); own: without the shoulder's edge the polygon takes in
    left of the head (rows 13-14, columns before 50) - Codex pasted those design squares too, a grey stroke beside the
    head wherever the shoulder is lower than the design's - nor the shoulder's skin the polygon takes in under the jaw's
    left corner (rows 16 on, columns up to 53: the reviewer's light sliver beside the jaw in every frame whose shoulder
    sits elsewhere)."""
    d = design()
    m = Image.new("L", (d.shape[1], d.shape[0]))
    ImageDraw.Draw(m).polygon(HEAD_POLY, fill=255)
    m = (np.asarray(m) > 0) & (d[..., 3] > 0)
    if own:
        m[13:15, :50] = False
        skin = np.zeros_like(m)
        for c in SKIN:
            skin |= (d[..., :3] == c).all(-1)
        skin[:16] = False
        skin[:, 54:] = False
        m &= ~skin
    return m


def find_head(a):
    """Codex's translation of the pasted head: (dy, dx) from the design's own place on the canvas, the most squares equal."""
    d, hm = design(), head_mask()
    ys, xs = np.nonzero(hm)
    want = d[ys, xs]
    x0, y0 = DESIGN_AT
    best = (-1, 0, 0)
    for dy in range(-40, 30):
        for dx in range(-40, 50):
            yy, xx = ys + y0 + dy, xs + x0 + dx
            if yy.min() < 0 or xx.min() < 0 or yy.max() >= ROWS or xx.max() >= COLS:
                continue
            n = int((a[yy, xx] == want).all(-1).sum())
            if n > best[0]:
                best = (n, dy, dx)
    assert best[0] >= 0.9 * len(ys), f"no pasted head found ({best[0]} of {len(ys)} squares)"
    return best[1], best[2]


def paste_head(a, dy, dx):
    d, hm = design(), head_mask(own=True)
    ys, xs = np.nonzero(hm)
    x0, y0 = DESIGN_AT
    a[ys + y0 + dy, xs + x0 + dx] = d[ys, xs]
    return a


def body_scale(a):
    """A frame's size against the design's: the square root of its skin, loin cloth and trousers' area over the
    design's (the head is the design's own everywhere)."""
    def area(x):
        n = 0
        for c in SKIN + CLOTH + TROUSERS:
            n += int(((x[..., 3] > 0) & (x[..., :3] == c).all(-1)).sum())
        return n
    return (area(a) / area(design())) ** 0.5


def keys(a):
    return np.where(a[..., 3] > 0, (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2], -1)


def least(lines, n_out):
    """design_riven.pick at the offset that loses least: the n_out lines kept, the others the most like a neighbour."""
    if n_out >= len(lines):
        return list(range(len(lines)))
    best = None
    for off in range(3):
        k, lost = R.pick(lines, n_out, off)
        if k is not None and (best is None or lost < best[1]):
            best = (k, lost)
    return best[0]


def shrink(a, f):
    """The canvas `a` brought to f of its size by deleting whole rows and columns (the soles' row SOLE and the standing
    column PIV_X kept where they are). -> (canvas, row map, column map: old index -> new index of the nearest kept)."""
    k = keys(a)
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    top, left, right = ys.min(), xs.min(), xs.max()
    rows = list(range(top, SOLE))
    kr = least([k[y] for y in rows], round((SOLE + 1 - top) * f) - 1)
    kept_r = [rows[i] for i in kr] + [SOLE]
    lcols, rcols = list(range(left, PIV_X)), list(range(PIV_X + 1, right + 1))
    kl = least([k[:, x] for x in lcols], round(len(lcols) * f)) if lcols else []
    kr2 = least([k[:, x] for x in rcols], round(len(rcols) * f)) if rcols else []
    kept_l, kept_rc = [lcols[i] for i in kl], [rcols[i] for i in kr2]
    out = np.zeros_like(a)
    new_y = {y: SOLE - (len(kept_r) - 1 - i) for i, y in enumerate(kept_r)}
    new_x = {x: PIV_X - (len(kept_l) - i) for i, x in enumerate(kept_l)}
    new_x[PIV_X] = PIV_X
    new_x.update({x: PIV_X + 1 + i for i, x in enumerate(kept_rc)})
    yk, xk = np.array(sorted(new_y)), np.array(sorted(new_x))
    out[np.ix_([new_y[y] for y in yk], [new_x[x] for x in xk])] = a[np.ix_(yk, xk)]
    ymap = lambda y: new_y[yk[np.abs(yk - y).argmin()]]
    xmap = lambda x: new_x[xk[np.abs(xk - x).argmin()]]
    return out, ymap, xmap


def specks(a, most=SPECK):
    """Loose pieces apart from the figure, at most `most` squares, cleared."""
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lab, range(1, n + 1))
        for i, z in enumerate(sizes, 1):
            if z <= most:
                a[lab == i] = 0
    return a


RIBBON_EDGE = [(129, 0, 1), (156, 1, 5)]   # the ribbon's own dark red rim (the design draws it with no black line)


def close_all(a):
    """Every light square still touching the ground 4-wise gets an outline square there (nothing under SOLE); the
    ribbon's dark red rim is its edge already, as in the design (a black line round it in the actions only flickered)."""
    op = a[..., 3] > 0
    light = op & (a[..., :3].astype(int).sum(-1) >= 70)
    for c in RIBBON_EDGE:
        light &= ~(a[..., :3] == c).all(-1)
    out = a.copy()
    for y, x in zip(*np.nonzero(light)):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy <= SOLE and 0 <= xx < COLS and not op[yy, xx]:
                out[yy, xx] = (*OUTLINE, 255)
    return out


def pinholes(a, most=PINHOLE):
    lab, n = ndimage.label(a[..., 3] == 0)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    for i in range(1, n + 1):
        if i not in border and (lab == i).sum() <= most:
            a[lab == i] = (*OUTLINE, 255)
    return a


ORPHAN_ROW = 110                # canvas rows from here down (under the belt): where moving legs meet the axe
CLOTH_COLS = (92, 105)          # canvas columns of the loin cloth: its tatters' 1-square tips are drawn so


def orphans(a):
    """Outline stubs that outline nothing: a dark square under ORPHAN_ROW with at most one opaque 4-neighbour and no
    light square among its 8 - what a moved part leaves of a shared edge (the boot's edge on the axe blade's when he
    breathes or lifts the foot: a 1-square stick hanging there). Again until none is left (a stick's next square becomes
    one). Thick outlines keep their corners (two neighbours)."""
    for _ in range(6):
        op = a[..., 3] > 0
        dark = op & (a[..., :3].astype(int).sum(-1) < 70)
        light = op & ~dark
        for c in RIBBON_EDGE:
            light |= (a[..., :3] == c).all(-1) & op
        p = np.pad(op, 1)
        n4 = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        near = ndimage.binary_dilation(light, structure=np.ones((3, 3)))
        m = dark & (n4 <= 1) & ~near
        m[:ORPHAN_ROW] = False
        m[:, CLOTH_COLS[0]:CLOTH_COLS[1]] = False
        if not m.any():
            break
        a[m] = 0
    return a


def tidy(a):
    a = orphans(specks(a))
    a = G.complete_outline(a, color=OUTLINE, feet=SOLE)[0]
    a = pinholes(close_all(a))
    a[SOLE + 1:] = 0
    return a


def codex(tag, n):
    return load(os.path.join(CODEX, f"sion_{tag}_{n}_1x.png"))


RIBBON = [(251, 38, 24), (129, 0, 1), (156, 1, 5), (252, 99, 46)]   # the ribbon's (and the eyes') reds


def scaled_frame(a, f):
    """A Codex frame without its head, shrunk by f, the design's head pasted back on the shrunken neck. Squares of the
    ribbon's reds outside the pasted head are what Codex's own generated ribbon left (its restore script cleared most):
    they go too (a red tatter under the ribbon). -> (the canvas, not yet tidied; the head's offset (rows, columns) from
    its place in the design)."""
    dy, dx = find_head(a)
    hm = head_mask()
    ys, xs = np.nonzero(hm)
    x0, y0 = DESIGN_AT
    b = a.copy()
    b[ys + y0 + dy, xs + x0 + dx] = 0
    for c in RIBBON:
        b[(b[..., :3] == c).all(-1) & (b[..., 3] > 0)] = 0
    s, ymap, xmap = shrink(b, f)
    ny, nx = ymap(NECK[0] + y0 + dy), xmap(NECK[1] + x0 + dx)
    off = (ny - (NECK[0] + y0), nx - (NECK[1] + x0))
    return paste_head(s, *off), off


def head_at(off):
    """The pasted head's own squares on the canvas (head_mask(own=True) moved by off)."""
    m = np.zeros((ROWS, COLS), bool)
    ys, xs = np.nonzero(head_mask(own=True))
    x0, y0 = DESIGN_AT
    m[ys + y0 + off[0], xs + x0 + off[1]] = True
    return m


def scale_of(tag):
    """1 / the median size of the tag's own Codex frames (not the design copies)."""
    nums = sorted({n for n in TAGS[tag] if n != "design"})
    return 1.0 / float(np.median([body_scale(codex(tag, n)) for n in nums]))


def actions():
    d = design()
    idle = on_canvas(d)
    out = {"idle": [(tidy(breathe(idle, upper(idle), k)), IDLE_MS) for k in BREATH],
           "run": [(tidy(walk_frame(idle, n_, f_, r_)), WALK_MS) for n_, f_, r_ in WALK]}
    for tag, nums in TAGS.items():
        f = scale_of(tag)
        frames = []
        for pos, (n, ms) in enumerate(zip(nums, MS[tag]), 1):
            if n == "design":
                frames.append((tidy(idle.copy()), ms))
                continue
            p, off = scaled_frame(codex(tag, n), f * SCALE_FIX.get((tag, n), 1.0))
            frames.append((tidy(fixed(tag, pos, p, off)), ms))
        out[tag] = frames
    out["hit"] = [(tidy(on_canvas(d, dx=-2)), 80.0), (tidy(on_canvas(d, dx=-1)), 120.0)]
    out["ult"] = [(f, ULT_MS) for f in charge()]
    return out


def clear(a, box, head):
    """Every square in the box (x0, y0, x1, y1, inclusive) but the pasted head's own, cleared."""
    x0, y0, x1, y1 = box
    m = np.zeros(head.shape, bool)
    m[y0:y1 + 1, x0:x1 + 1] = True
    a[m & ~head] = 0
    return a


def rows_moved(a, src):
    """a's rows src (kept, top to bottom) set down to end on SOLE; the rows over them bare."""
    out = np.zeros_like(a)
    out[SOLE + 1 - len(src):SOLE + 1] = a[src]
    return out


def lower(a, k):
    """The frame k rows down, nothing under SOLE. -> (frame, the rows kept)"""
    src = list(range(SOLE + 1 - k))
    return rows_moved(a, src), src


def drop_rows(a, b0, n, keep=None):
    """n whole rows taken from rows b0..SOLE-1 (but the rows of keep (r0, r1)), the ones most like a neighbour;
    everything above moves down. -> (frame, the rows kept)"""
    k = keys(a)
    rows = [y for y in range(b0, SOLE) if not keep or not keep[0] <= y <= keep[1]]
    kept = [rows[i] for i in least([k[y] for y in rows], len(rows) - n)]
    gone = set(rows) - set(kept)
    src = [y for y in range(SOLE + 1) if y not in gone]
    return rows_moved(a, src), src


def moved_row(y, src):
    """Where row y went when the rows src were kept and set down on SOLE (a dropped row: its nearest kept one's)."""
    src = np.array(src)
    return SOLE + 1 - len(src) + int(np.abs(src - y).argmin())


def foot(a, x0, x1, y0, k):
    """A boot set down k rows onto the ground: columns x0..x1 from row y0 move k rows down, the k rows they leave take
    the row above them (the shin grows)."""
    sub = a[y0:SOLE + 1 - k, x0:x1 + 1].copy()
    a[y0 + k:SOLE + 1, x0:x1 + 1] = sub
    a[y0:y0 + k, x0:x1 + 1] = a[y0 - 1, x0:x1 + 1]
    return a


def far_boot(a, x0):
    """The design's far boot (FAR_BOOT, its rows on the idle canvas) behind the frame: its sole on SOLE from column x0,
    drawn only where the frame is bare."""
    r0, r1, c0, c1 = FAR_BOOT
    boot = on_canvas(design())[r0:r1, c0:c1]
    sub = a[SOLE + 1 - (r1 - r0):SOLE + 1, x0:x0 + (c1 - c0)]
    m = (sub[..., 3] == 0) & (boot[..., 3] > 0)
    sub[m] = boot[m]
    return a


def stake(a, off):
    """Codex's wider stake beside the pasted one: dark squares where the design's stake band (head rows 0-8, design
    columns 54-61) is bare, cleared."""
    d = design()
    band = d[..., 3] == 0
    band[9:] = False
    band[:, :54] = False
    band[:, 62:] = False
    ys, xs = np.nonzero(band)
    yy, xx = ys + DESIGN_AT[1] + off[0], xs + DESIGN_AT[0] + off[1]
    p = a[yy, xx]
    dark = (p[:, 3] > 0) & (p[:, :3].astype(int).sum(1) < 250)
    a[yy[dark], xx[dark]] = 0
    return a


def neck(a, x0, x1, y0, head):
    """Codex's neck lines beside the jaw (columns x0..x1): in each column, every square from row y0 down to the
    shoulder's first light square that is not the pasted head, cleared."""
    for x in range(x0, x1 + 1):
        for y in range(y0, SOLE):
            p = a[y, x]
            if head[y, x]:
                continue
            if p[3] and int(p[:3].astype(int).sum()) >= 250:
                break
            a[y, x] = 0
    return a


BLADE = [(157, 158, 188), (114, 125, 140), (209, 222, 235)]   # the axe blade's steels (the first is skin too)
BLADE_HI = (209, 222, 235)                                      # its edge's highlight, the blade's alone: the seed
RING = [(152, 150, 128), (212, 208, 178)]                       # the bone ring at the blade's foot
AXE_AREA = 247                                                  # the design's blade, squares of its steels
AXE_TOL = 0.92                  # a blade within a sixth of the design's area keeps its squares (resizing costs)


SKIN_ONLY = [(125, 110, 151), (189, 202, 219), (94, 69, 112)]   # skin tones the blade never uses


def blade_of(a, box):
    """The axe blade inside box (x0, y0, x1, y1): its steel squares joined to the edge's highlight - the shared pale
    steel only where no skin tone touches it (a hand on the haft is not the blade: the reviewer saw hands cut out and
    pasted back shrunk) - what they enclose and the outline round them. -> (mask, its steel squares)"""
    x0, y0, x1, y1 = box
    op = a[..., 3] > 0
    inb = np.zeros(op.shape, bool)
    inb[y0:y1 + 1, x0:x1 + 1] = True
    skin = np.zeros(op.shape, bool)
    for c in SKIN_ONLY:
        skin |= op & (a[..., :3] == c).all(-1)
    near_skin = ndimage.binary_dilation(skin, structure=np.ones((3, 3)), iterations=2)
    steel = np.zeros(op.shape, bool)
    for c in BLADE:
        m = op & (a[..., :3] == c).all(-1)
        if c == BLADE[0]:
            m &= ~near_skin
        steel |= m
    steel &= inb
    lab, _ = ndimage.label(steel)
    hi = steel & (a[..., :3] == BLADE_HI).all(-1)
    m = np.isin(lab, list(set(np.unique(lab[hi]).tolist()) - {0}))
    ring = np.zeros(op.shape, bool)
    for c in RING:
        ring |= op & (a[..., :3] == c).all(-1)
    ring = ndimage.binary_dilation(ndimage.binary_fill_holes(ring), structure=np.ones((3, 3)))
    body = ndimage.binary_fill_holes(m) & op & inb & ~skin & ~ring
    rim = ndimage.binary_dilation(body, structure=np.ones((3, 3))) & ~body & op & inb & ~ring &         (a[..., :3] == OUTLINE).all(-1)
    return body | rim, int((m & steel).sum())


def ring_at(a, box):
    """The bone ring's middle inside box (row, column), None when it is hidden."""
    x0, y0, x1, y1 = box
    m = np.zeros(a.shape[:2], bool)
    for c in RING:
        m |= (a[..., 3] > 0) & (a[..., :3] == c).all(-1)
    m[:y0] = m[y1 + 1:] = False
    m[:, :x0] = m[:, x1 + 1:] = False
    ys, xs = np.nonzero(m)
    return (float(ys.mean()), float(xs.mean())) if len(ys) else None


def resampled(sub, s, anchor):
    """The object `sub` (its own box) at s of its size, every square the commonest colour of the squares under it when
    they cover half of it - the crescent keeps its curve, where deleting whole rows and columns sawed its edge (the
    reviewer; letting the edge's highlight win from a quarter whitened the blades). -> (object, where `anchor` went)"""
    H, W = sub.shape[:2]
    h, w = max(1, round(H * s)), max(1, round(W * s))
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        y0, y1 = int(np.floor(j * H / h)), max(int(np.floor(j * H / h)) + 1, int(np.ceil((j + 1) * H / h)))
        for i in range(w):
            x0, x1 = int(np.floor(i * W / w)), max(int(np.floor(i * W / w)) + 1, int(np.ceil((i + 1) * W / w)))
            win = sub[y0:y1, x0:x1].reshape(-1, 4)
            op = win[:, 3] > 0
            if op.mean() < 0.5:
                continue
            cols, cnt = np.unique(win[op][:, :3], axis=0, return_counts=True)
            out[j, i, :3], out[j, i, 3] = cols[int(cnt.argmax())], 255
    return out, (min(h - 1, int(anchor[0] * h / H)), min(w - 1, int(anchor[1] * w / W)))


# a fist round the haft where Codex drew none (the design's near fist: dark wrap, black lines; light from the top left)
FIST = [". B B B B B . .",
        "B k k m b b B .",
        "B m k b B b b B",
        "B b b B b b b B",
        "B b B d b B b B",
        ". B b b b b B .",
        ". . B B B B . ."]
# pale knuckles over the wrap (the design's near hand: the reviewer saw plain brown blobs)
FIST_COLOURS = {"B": OUTLINE, "b": (51, 31, 27), "d": (78, 51, 42), "k": (189, 202, 219), "m": (157, 158, 188)}
IRON_OF = {(117, 61, 32): (65, 69, 75), (91, 47, 25): (39, 40, 44), (78, 51, 42): (65, 69, 75),
           (51, 31, 27): (39, 40, 44)}      # the forearm's wrap as the gauntlet's iron plates
CLOTHS = [(108, 97, 55), (38, 42, 30)]      # the loin cloth and its fold


def fist(a, x0, y0):
    for j, row in enumerate(FIST):
        for i, ch in enumerate(row.split()):
            if ch != ".":
                a[y0 + j, x0 + i] = (*FIST_COLOURS[ch], 255)
    return a


def pauldron_mask():
    """The design's spiked pauldron on the idle canvas: its iron and lines right of the head, down to row 97 (under it
    the far arm hangs), the largest piece."""
    idle = on_canvas(design())
    reg = np.zeros((ROWS, COLS), bool)
    reg[70:98, 104:141] = True
    m = np.zeros_like(reg)
    for c in [(39, 40, 44), (65, 69, 75), (114, 125, 140), OUTLINE]:
        m |= (idle[..., 3] > 0) & (idle[..., :3] == c).all(-1)
    m &= reg & ~head_at((0, 0))
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    m = lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))
    return ndimage.binary_fill_holes(m) & (idle[..., 3] > 0) & ~head_at((0, 0))


def pauldron(a, off, dy, dx):
    """The design's pauldron pasted on the far shoulder: moved as the head is, and (dy, dx) more."""
    idle = on_canvas(design())
    ys, xs = np.nonzero(pauldron_mask())
    a[ys + off[0] + dy, xs + off[1] + dx] = idle[ys, xs]
    return a


def plates(a, box):
    """The forearm's wrap in box (x0, y0, x1, y1) as iron plates (IRON_OF)."""
    x0, y0, x1, y1 = box
    sub = a[y0:y1 + 1, x0:x1 + 1]
    for c, to in IRON_OF.items():
        sub[(sub[..., 3] > 0) & (sub[..., :3] == c).all(-1), :3] = to
    return a


def cloth(a, box):
    """The loin cloth in box (x0, y0, x1, y1) replaced by the design's: Codex's cloth squares cleared, the design's cloth
    pasted with its top row on the cleared cloth's and its middle under the cleared cloth's middle."""
    x0, y0, x1, y1 = box
    m = np.zeros((ROWS, COLS), bool)
    for c in CLOTHS:
        m |= (a[..., 3] > 0) & (a[..., :3] == c).all(-1)
    m[:y0] = m[y1 + 1:] = False
    m[:, :x0] = m[:, x1 + 1:] = False
    main = m & (a[..., :3] == CLOTHS[0]).all(-1)
    ys, xs = np.nonzero(main)
    top, mid = ys.min(), (xs.min() + xs.max()) / 2
    a[m] = 0
    # its outline too: dark squares round it that line nothing else light (the reviewer: the old cloth's black line
    # stayed, pockets of ground inside it)
    op = a[..., 3] > 0
    light = op & (a[..., :3].astype(int).sum(-1) >= 70)
    near_light = ndimage.binary_dilation(light, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    rim = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op & ~light & ~near_light
    a[rim] = 0
    idle = on_canvas(design())
    dm = np.zeros((ROWS, COLS), bool)
    for c in CLOTHS:
        dm |= (idle[..., 3] > 0) & (idle[..., :3] == c).all(-1)
    dm &= box_mask(CLOTH_BOX)
    dy_, dx_ = np.nonzero(dm)
    oy, ox = top - dy_.min(), int(round(mid - (dx_.min() + dx_.max()) / 2))
    a[dy_ + oy, dx_ + ox] = idle[dy_, dx_]
    return a


def slit(a, box):
    """1-square slits between limbs in box (x0, y0, x1, y1): bare squares with the figure on two opposite sides (left
    and right, above and below, or across a diagonal) take the outline, until none is left."""
    x0, y0, x1, y1 = box
    for _ in range(6):
        op = a[..., 3] > 0
        fill = []
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if op[y, x]:
                    continue
                if any(op[y + dy, x + dx] and op[y - dy, x - dx] for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1))):
                    fill.append((y, x))
        if not fill:
            break
        for y, x in fill:
            a[y, x] = (*OUTLINE, 255)
    return a


def ring_fix(a, box):
    """A bone ring Codex drew bigger than the design's (in box): its squares darkened, the design's ring set on its
    middle (the haft and the hand round it are dark already)."""
    x0, y0, x1, y1 = box
    m = np.zeros((ROWS, COLS), bool)
    for c in RING:
        m |= (a[..., 3] > 0) & (a[..., :3] == c).all(-1)
    m[:y0] = m[y1 + 1:] = False
    m[:, :x0] = m[:, x1 + 1:] = False
    ys, xs = np.nonzero(m)
    if not len(ys) or (ys.max() - ys.min() < 6 and xs.max() - xs.min() < 6):
        return a
    cy, cx = ys.mean(), xs.mean()
    a[m, :3] = OUTLINE
    idle = on_canvas(design())
    d = np.zeros((ROWS, COLS), bool)
    for c in RING:
        d |= (idle[..., 3] > 0) & (idle[..., :3] == c).all(-1)
    d[:105] = False
    dy_, dx_ = np.nonzero(d)
    oy, ox = int(round(cy - dy_.mean())), int(round(cx - dx_.mean()))
    a[dy_ + oy, dx_ + ox] = idle[dy_, dx_]
    return a


def haft_fill(a, box):
    """Bare squares in box (x0, y0, x1, y1) with the figure on two opposite sides take the haft's dark wood."""
    x0, y0, x1, y1 = box
    for _ in range(4):
        op = a[..., 3] > 0
        fill = [(y, x) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if not op[y, x] and
                any(op[y + dy, x + dx] and op[y - dy, x - dx] for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)))]
        if not fill:
            break
        for y, x in fill:
            a[y, x] = (51, 31, 27, 255)
    return a


def stretch(a, x0, x1, y0, k):
    """A lower leg Codex left floating set down k rows: in columns x0..x1 the rows from y0 to the soles are drawn
    k rows longer (each row nearest above, spread evenly) - the shin grows along its own slope, the boot lands."""
    n = SOLE + 1 - y0
    src = a[y0:SOLE + 1 - k, x0:x1 + 1].copy()
    a[y0:SOLE + 1, x0:x1 + 1] = src[np.minimum(src.shape[0] - 1, (np.arange(n) * (n - k) // n))]
    for x in range(x0, x1 + 1):         # a sole line doubled by the stretch: the upper one takes the boot's colour
        line = [(a[y, x, 3] > 0) and tuple(a[y, x, :3]) == OUTLINE for y in (SOLE, SOLE - 1, SOLE - 2)]
        if line[0] and line[1] and not line[2] and a[SOLE - 2, x, 3] > 0:
            a[SOLE - 1, x] = a[SOLE - 2, x]
    return a


def ink(a, pts):
    for x, y in pts:
        a[y, x] = (*OUTLINE, 255)
    return a


def fixed(tag, pos, a, off):
    """FIX's operations for this frame, in order; an axe blade taken out ("axe") goes back last where its foot went,
    no bigger than the design's (AXE_AREA)."""
    head = head_at(off)
    axe, maps, rings, hafts = None, [], [], []
    for op in FIX.get((tag, pos), ()):
        if op[0] == "axe":
            box = op[1]
            m, area = blade_of(a, box)
            ring = ring_at(a, box) or op[2]
            ys, xs = np.nonzero(m)
            sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
            sub[ys - ys.min(), xs - xs.min()] = a[ys, xs]
            i = int(((ys - ring[0]) ** 2 + (xs - ring[1]) ** 2).argmin())      # the blade's square at the ring
            anchor = (int(ys[i] - ys.min()), int(xs[i] - xs.min()))
            s = min(1.0, (AXE_AREA / area) ** 0.5) if area else 1.0
            if s < AXE_TOL:
                sub, anchor = resampled(sub, s, anchor)
            a[m] = 0
            follow = len(op) > 3 and op[3] == "ring"
            axe = (sub, anchor, (int(ys[i]), int(xs[i])), ring if follow and ring_at(a, box) else None, box)
        elif op[0] == "clear":
            a = clear(a, op[1], head)
        elif op[0] == "stake":
            a = stake(a, off)
        elif op[0] == "neck":
            a = neck(a, op[1], op[2], op[3], head)
        elif op[0] in ("lower", "legs"):
            a, src = lower(a, op[1]) if op[0] == "lower" else drop_rows(a, *op[1:])
            head = rows_moved(head[..., None].astype(np.uint8), src)[..., 0] > 0
            maps.append(src)
        elif op[0] == "boot":
            a = far_boot(a, op[1])
        elif op[0] == "foot":
            a = foot(a, *op[1:])
        elif op[0] == "fist":
            a = fist(a, op[1], op[2])
        elif op[0] == "pauldron":
            a = pauldron(a, off, op[1], op[2])
        elif op[0] == "plates":
            a = plates(a, op[1])
        elif op[0] == "cloth":
            a = cloth(a, op[1])
        elif op[0] == "slit":
            a = slit(a, op[1])
        elif op[0] == "ring":
            rings.append(op[1])
        elif op[0] == "haft":
            hafts.append(op[1])
        elif op[0] == "stretch":
            a = stretch(a, *op[1:])
        elif op[0] == "ink":
            a = ink(a, op[1])
        else:
            raise ValueError(op)
    if axe:
        sub, (ay, ax), (py, px), ring0, (bx0, by0, bx1, by1) = axe
        ring1 = ring_at(a, (bx0 - 4, by0 - 4, bx1 + 4, min(SOLE, by1 + 14))) if ring0 else None
        if ring1:               # with the ring (its rows kept out of a trim: dead 1/2) - by its own row a trim left a
            py += int(round(ring1[0] - ring0[0]))           # hole at the haft; elsewhere the ring itself moved with the
            px += int(round(ring1[1] - ring0[1]))           # stretches and trims, so the blade keeps its own row's mapping
        else:
            for src in maps:
                py = moved_row(py, src)
        ys, xs = np.nonzero(sub[..., 3] > 0)
        yy, xx = ys + py - ay, xs + px - ax
        ok = (yy >= 0) & (yy <= SOLE) & (xx >= 0) & (xx < COLS)
        a[yy[ok], xx[ok]] = sub[ys[ok], xs[ok]]
    for box in rings:                   # over the blade put back
        a = ring_fix(a, box)
    for box in hafts:                   # a slit left between the haft and the blade: the haft's dark wood
        a = haft_fill(a, box)
    return a


def charge():
    """R's charge frames: Codex's charge pose's upper body (cut at its chest: ULT_CUT) over the design's waist (its belt
    and furnace, ULT_WAIST) and its legs walking - Codex's near thigh, drawn beside its belt, stacked a second thigh over
    the design's (the reviewer)."""
    u = codex("ult", 1)
    u, off = scaled_frame(u, 1.0 / body_scale(u))
    u = fixed("ult", 1, u, off)
    r0, c0, c1 = ULT_CUT
    u[r0:, c0:c1] = 0
    dy, dx = ULT_SHIFT
    top = np.zeros_like(u)
    ys, xs = np.nonzero(u[..., 3] > 0)
    top[ys + dy, xs + dx] = u[ys, xs]
    legs = on_canvas(design())
    legs[~box_mask(WALK_NEAR + WALK_FAR + CLOTH_BOX + ULT_WAIST)] = 0
    out = []
    for n_, f_, r_ in WALK:
        w = walk_frame(legs, n_, f_, r_)
        t = np.roll(top, -r_, axis=0)
        m = t[..., 3] > 0
        w[m] = t[m]
        out.append(tidy(largest(w)))
    return out


def largest(a):
    """Only the figure's own piece (8-connected): the cut leaves the near boot's edge column behind as a loose stick."""
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lab, range(1, n + 1))
        a[(lab > 0) & (lab != 1 + int(np.argmax(sizes)))] = 0
    return a


def box_mask(boxes, dy=0, dx=0):
    m = np.zeros((ROWS, COLS), bool)
    x0, y0 = DESIGN_AT
    for r0, r1, c0, c1 in boxes:
        m[y0 + dy + r0:y0 + dy + r1, x0 + dx + c0:x0 + dx + c1] = True
    return m


def breathe(can, mask, k):
    """The masked squares moved k rows up; of the squares they uncover only those right over the squares that stay
    (the legs and the loin cloth: the belt's seam) take the colour of the square under them - every other edge just
    moves (the reviewer: filling under every moved edge from the moved squares blinked pixels at the stake, the
    ribbon, the pauldron and the hands)."""
    if k == 0:
        return can.copy()
    out = can.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    rest = out.copy()
    out[ys - k, xs] = can[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            below = y + 1
            while below < can.shape[0] and out[below, x, 3] == 0 and mask[below, x]:
                below += 1
            if below < can.shape[0] and rest[below, x, 3] > 0:
                out[y, x] = rest[below, x]
    return out


def upper(can):
    """The idle's squares that breathe: all but the legs and the loin cloth."""
    return (can[..., 3] > 0) & ~box_mask(WALK_NEAR + WALK_FAR + CLOTH_BOX)


def walk_frame(idle, near_step, far_step, rise):
    """league_galio's / league_braum's walk on the idle: each leg's squares moved (dx, -lift) after losing their top
    `lift` rows; the far leg first, the near one over it, the body over both; the whole frame `rise` rows up; the cracks
    a step opens take the outline."""
    H, W = idle.shape[:2]
    op = idle[..., 3] > 0
    near, far = box_mask(WALK_NEAR) & op, box_mask(WALK_FAR) & op
    band = DESIGN_AT[1] + WALK_BAND
    body = idle.copy()
    body[near | far] = 0
    out = np.zeros_like(idle)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        leg = np.where(m[..., None], idle, 0).astype(np.uint8)
        leg[:band + 1 + lift] = 0
        ys, xs = np.nonzero(leg[..., 3] > 0)
        ok = (ys - lift >= 0) & (xs + dx < W)
        out[ys[ok] - lift, xs[ok] + dx] = leg[ys[ok], xs[ok]]
    m = body[..., 3] > 0
    out[m] = body[m]
    ground = np.zeros_like(op)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        if lift:
            ys, xs = np.nonzero(m)
            ground[ys.max() - lift + 1:ys.max() + 1, xs.min():xs.max() + dx + 1] = True
    own = ndimage.binary_fill_holes(op) & ~op
    for _ in range(3):
        wop = out[..., 3] > 0
        crack = (op & ~wop & ~ground) | (ndimage.binary_fill_holes(wop) & ~wop & ~own)
        fill = np.zeros_like(crack)
        for arr in (crack, crack.T):
            f = fill if arr is crack else fill.T
            for y in np.nonzero(arr.any(1))[0]:
                xs = np.nonzero(arr[y])[0]
                for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
                    if len(run) <= CRACK:
                        f[y, run] = True
        if not fill.any():
            break
        out[fill] = (*OUTLINE, 255)
    return np.roll(out, -rise, axis=0)


def review_sheet(frames, path, z=4):
    tiles = [Image.fromarray(c) for c, _ in frames]
    op = np.zeros((ROWS, COLS), bool)
    for c, _ in frames:
        op |= c[..., 3] > 0
    ys, xs = np.nonzero(op)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    w, h = box[2] - box[0], box[3] - box[1]
    big = Image.new("RGBA", (len(tiles) * (w * z + 6), h * z), (255, 0, 255, 255))
    for k, t in enumerate(tiles):
        c = t.crop(box)
        big.alpha_composite(c.resize((w * z, h * z), Image.NEAREST), (k * (w * z + 6), 0))
    big.convert("RGB").save(path)


ORDER = ["idle", "run", "attack", "skill_charge", "skill", "skill2", "skill2_w", "ult", "ult_hit", "hit", "dead"]


def pivot():
    """The pivot's centre on the canvas: the standing column's centre, (FEET + 0.5) 1x rows above the soles' bottom
    edge (tools/art/rig_bard.py's)."""
    return PIV_X + 0.5, SOLE + 1 - (FEET + 0.5) * PPU


def one_x(can, p):
    """The 1x frame: pixel_down.pixelate at 1 / PPU on a grid whose square round the pivot is centred on it; odd size,
    the pivot's square in the middle, and wide and tall enough that round(PPU x its size) holds the dense frame without
    growing it (the DLL wants hd_idle exactly round(PPU x the 1x width))."""
    px, py = p
    lo, (nx0, ny0) = PD.pixelate(can, 1 / PPU, (px - PPU / 2, py - PPU / 2), OUTLINE)
    ys, xs = np.nonzero(lo[..., 3])
    hw, hh = max(nx0 - xs.min(), xs.max() - nx0), max(ny0 - ys.min(), ys.max() - ny0)
    dy, dx = np.nonzero(can[..., 3])
    need_w = max(px - dx.min(), dx.max() + 1 - px)
    need_h = max(py - dy.min(), dy.max() + 1 - py)
    while round((2 * hw + 1) * PPU) / 2 < need_w:
        hw += 1
    while round((2 * hh + 1) * PPU) / 2 < need_h:
        hh += 1
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    out[ys - ny0 + hh, xs - nx0 + hw] = lo[ys, xs]
    out, _, _ = G.complete_outline(out, color=OUTLINE, feet=hh + FEET)
    return out


def dense(can, one, p):
    """The game's frame: the canvas SHIFT rows lower on a frame of round(PPU x the 1x frame's size), grown alike at
    both ends where the drawing needs more, the pivot at its centre."""
    lx, ly = p
    W, H = round(one.shape[1] * PPU), round(one.shape[0] * PPU)
    ys, xs = np.nonzero(can[..., 3])
    yd = ys + SHIFT
    while W / 2 < max(lx - xs.min(), xs.max() + 1 - lx):
        W += 2
    while H / 2 < max(ly - yd.min(), yd.max() + 1 - ly):
        H += 2
    f = np.zeros((H, W, 4), np.uint8)
    ox, oy = int(np.floor(W / 2 - lx + 0.5)), int(np.floor(H / 2 - ly + 0.5))
    f[yd + oy, xs + ox] = can[ys, xs]
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's canvas frames at 4x on magenta here")
    ap.add_argument("--frames-only", action="store_true", help="only the review sheets, no game files")
    a = ap.parse_args()
    acts = actions()
    p = pivot()
    sheet = {}
    for tag in ORDER:
        frames = acts[tag]
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            review_sheet(frames, os.path.join(a.review, f"sion_{tag}.png"))
        if a.frames_only:
            continue
        ones, hds = [], []
        for can, ms in frames:
            one = one_x(can, p)
            ones.append((one, round(float(ms), 3)))
            hds.append(dense(can, one, p))
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"sion_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"sion_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
    if sheet:
        w, h = G.write_sheet(STEM, sheet)
        print(f"league/champions/league_sion#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
