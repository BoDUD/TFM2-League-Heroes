#!/usr/bin/env python3
"""league_kindred's action frames from Codex's step-2 drafts on the dense design's grid (one square = one dense pixel).

    python tools/art/import_kindred_strips.py --prepare <delivery>/raw      (once: the drafts -> codex_strips/)
    python tools/art/import_kindred_strips.py [--review DIR] [--only TAG]

Codex drew the 49 frames (outputs/kindred_strips_done.zip, 2026-10-14) on the pack's 1536 x 1024 canvas
(tools/art/pack_kindred_strips.py: 5 px a design square, the hooves on y 985, the standing point x 827.5) but with
squares of about 6 px, redrew the mask and the bow in every frame and drew each action at its own size (its HANDOFF
lists these). Its own 5-px read-back resampled the 6-px squares, so the drafts are read here instead:
  * prepare: every draft pixel with alpha >= ALPHA snapped to the design's 40 colours (Lab), kept as an indexed PNG
    cropped to the figure (codex_strips/<name>.png, crops.json: its place on the canvas) - the drafts themselves are
    58 MB and stay in the delivery;
  * the head: the side design's mask head (design_kindred_hd.MASK_POLY on hd/side.png, its own outline ring) matched
    in the draft by a masked colour SSD over scales (head_match) -> the draft's px per design square and the head's
    place;
  * the size, one per action (the median head scale of its frames; Bard's lesson: per-frame measures pump the size);
  * the cut: the draft voted down in blocks of that size (each square the commonest colour; clear where half or more
    is clear), the pack's standing point on the frame canvas's standing point;
  * one face (memory one-face-all-frames): the design's mask head pasted where it matches best;
  * one bow: the design's bow (limbs and tips, rigid, only moved; level in the lying death frames) pasted over Codex's,
    its string drawn from tip to tip, or through the drawing hand when the frame draws it;
  * placed: the lowest square of the planted frames on the ground row SOLE;
  * the run: Codex had the same leg forward in seven of its eight frames - RUN_ORDER plays its frames with three of
    them drawn with the two legs' shades swapped in place (no shape moved), so the legs take turns;
  * cleaned: specks, holes and cracks closed, the outline closed (strips.complete_outline).
Writes assets/source/kindred/frames/kindred_<tag>_<n>.png (COLS x ROWS) and frames.json.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, signal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as dv  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kindred")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
ALPHA = 160
CANVAS = (1024, 1536)             # the drafts' canvas (rows, cols)
PACK_PIV = (827.5, 985.0)         # the pack's standing point (x) and ground line (y) in draft px
TAGS = [("run", 8), ("attack", 5), ("skill", 6), ("skill2", 5), ("w_cast", 4), ("ult", 6), ("dead", 6),
        ("wolf_float", 4), ("wolf_bite", 5)]


def palette():
    """The design's 40 colours (hd/front.png holds every one of them), sorted."""
    a = np.asarray(Image.open(os.path.join(SRC, "hd", "front.png")).convert("RGBA"))
    return np.unique(a[a[..., 3] > 0][:, :3], axis=0)


def snap(rgb, pal):
    lab = dv.srgb2lab(rgb.astype(float))
    pl = dv.srgb2lab(pal.astype(float))
    out = np.empty(len(lab), int)
    for i in range(0, len(lab), 100000):
        out[i:i + 100000] = ((lab[i:i + 100000, None] - pl[None]) ** 2).sum(-1).argmin(1)
    return out


def prepare(raw):
    pal = palette()
    os.makedirs(CODEX, exist_ok=True)
    crops = {}
    for tag, n in TAGS:
        for k in range(1, n + 1):
            name = f"kindred_{tag}_{k}"
            a = np.asarray(Image.open(os.path.join(raw, name + ".png")).convert("RGBA"))
            op = a[..., 3] >= ALPHA
            ys, xs = np.nonzero(op)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            idx = np.zeros(op.shape, np.uint8)
            idx[op] = snap(a[op][:, :3], pal) + 1
            im = Image.fromarray(idx[y0:y1, x0:x1], "P")
            flat = [0, 0, 0] + [int(v) for c in pal for v in c]
            im.putpalette(flat + [0] * (768 - len(flat)))
            im.info["transparency"] = 0
            im.save(os.path.join(CODEX, name + ".png"), transparency=0)
            crops[name] = [int(x0), int(y0)]
            print(name, (x1 - x0, y1 - y0))
    with open(os.path.join(CODEX, "crops.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(crops, f, indent=1)


def load_draft(name):
    """The draft as palette indices on the full canvas (-1 clear)."""
    crops = json.load(open(os.path.join(CODEX, "crops.json"), encoding="utf-8"))
    p = np.asarray(Image.open(os.path.join(CODEX, name + ".png")))
    x0, y0 = crops[name]
    out = np.full(CANVAS, -1, int)
    out[y0:y0 + p.shape[0], x0:x0 + p.shape[1]] = p.astype(int) - 1
    return out


# ----------------------------------------------------------------------------------------------- the design's parts
SIDE_HEAD_OFF = (-1, -2)          # where design_kindred_hd.paste_head put the front's mask on side A (rows, cols)
GREY_LAB = np.array([200.0, 0.0, 0.0])   # clear draft pixels in the match: far from every colour


def side_design():
    return np.asarray(Image.open(os.path.join(SRC, "hd", "side.png")).convert("RGBA")).copy()


def head_template():
    """The side design's mask head: (RGBA crop, its top-left (row, col) on hd/side.png)."""
    import design_kindred_hd as K
    side = side_design()
    poly = [(r + SIDE_HEAD_OFF[0], c + SIDE_HEAD_OFF[1]) for r, c in K.MASK_POLY]
    rgb = side[..., :3].astype(float)
    lab = dv.srgb2lab(rgb)
    fur = (lab[..., 0] > 60) & (lab[..., 1] > -15) & (lab[..., 2] < 5)
    dark = rgb.sum(-1) < 90
    m = K.poly_mask(side.shape, poly) & (side[..., 3] > 0) & ~fur
    m &= ~dark | ndimage.binary_dilation(m & ~dark, structure=np.ones((3, 3)), iterations=2)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    t = side[y0:y1, x0:x1].copy()
    t[~m[y0:y1, x0:x1]] = 0
    return t, (int(y0), int(x0))


FUR_WHITES = [38, 33, 34, 29]     # the hood's whites and light blues round the mask


def paste_template():
    """What is pasted: the mask as one solid piece - its own colours inside MASK_POLY with the holes filled, and the
    design's outline round it, whole. (The polygon cut the two-square outline on a slant, and the pasted mask's edge
    came out dotted where Codex's head was smaller.) -> (RGBA on head_template's box origin, (dy, dx) of its top-left
    against head_template's)."""
    import design_kindred_hd as K
    side = side_design()
    idx = design_idx(side)
    _, (ty0, tx0) = head_template()
    poly = K.poly_mask(idx.shape, [(r + SIDE_HEAD_OFF[0], c + SIDE_HEAD_OFF[1]) for r, c in K.MASK_POLY])
    core = poly & (idx >= 0) & ~np.isin(idx, FUR_WHITES + [OUTLINE, NAVY, 22])
    filled = ndimage.binary_fill_holes(core)
    ring = ndimage.binary_dilation(filled, iterations=2) & np.isin(idx, [OUTLINE, 1, NAVY])
    m = ndimage.binary_fill_holes(filled | ring)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    t = side[y0:y1, x0:x1].copy()
    sub = m[y0:y1, x0:x1]
    t[~sub] = 0
    gap = sub & (t[..., 3] == 0)                     # a hole the design left clear: outline
    t[gap] = tuple(int(v) for v in palette()[OUTLINE]) + (255,)
    return t, (int(y0 - ty0), int(x0 - tx0))


def lab_image(idx, pal):
    pl = dv.srgb2lab(pal.astype(float))
    out = np.empty(idx.shape + (3,))
    out[idx < 0] = GREY_LAB
    out[idx >= 0] = pl[idx[idx >= 0]]
    return out


def masked_ssd(I, T, M):
    """Mean squared Lab error of template T (h, w, 3) under mask M at every place in I (valid positions)."""
    n = M.sum()
    tot = 0.0
    for ch in range(3):
        Mf = M[::-1, ::-1].astype(float)
        TMf = (T[..., ch] * M)[::-1, ::-1]
        s1 = signal.fftconvolve(I[..., ch] ** 2, Mf, mode="valid")
        s2 = signal.fftconvolve(I[..., ch], TMf, mode="valid")
        s3 = (T[..., ch] ** 2 * M).sum()
        tot = tot + s1 - 2 * s2 + s3
    return tot / n


def scaled(t, s):
    """The template (RGBA) at s draft px a square (nearest)."""
    h, w = t.shape[:2]
    return np.asarray(Image.fromarray(t).resize((max(1, round(w * s)), max(1, round(h * s))), Image.NEAREST))


def head_match(idx, pal, tpl, scales=np.arange(4.4, 8.01, 0.1), box=None):
    """(score, s, x, y): the template's top-left corner at (x, y) draft px, s draft px a square."""
    I = lab_image(idx, pal)
    I2 = I[::2, ::2]
    best = None
    for s in scales:
        t = scaled(tpl, s / 2)
        T = lab_image(np.where(t[..., 3] > 0, 0, -1), pal)
        T = dv.srgb2lab(t[..., :3].astype(float))
        M = t[..., 3] > 0
        if t.shape[0] >= I2.shape[0] or t.shape[1] >= I2.shape[1]:
            continue
        e = masked_ssd(I2, T, M)
        j = np.unravel_index(np.argmin(e), e.shape)
        if best is None or e[j] < best[0]:
            best = (e[j], s, j[1] * 2, j[0] * 2)
    # refine at full resolution
    _, s0, x0, y0 = best
    for s in np.arange(s0 - 0.12, s0 + 0.121, 0.03):
        t = scaled(tpl, s)
        T = dv.srgb2lab(t[..., :3].astype(float))
        M = t[..., 3] > 0
        ya, xa = max(0, y0 - 12), max(0, x0 - 12)
        sub = I[ya:y0 + t.shape[0] + 12, xa:x0 + t.shape[1] + 12]
        if sub.shape[0] < t.shape[0] or sub.shape[1] < t.shape[1]:
            continue
        e = masked_ssd(sub, T, M)
        j = np.unravel_index(np.argmin(e), e.shape)
        if e[j] < best[0] or best[1] == s0:
            if e[j] <= best[0]:
                best = (e[j], s, xa + j[1], ya + j[0])
    return best


# ------------------------------------------------------------------------------------------------- the frames
COLS, ROWS = 360, 240             # the frame canvas (design squares): the E lunge spans 281 squares, raised bows 40 over
PIV, SOLE = 175, 222              # the standing column and the hooves' row on it
SIDE_MID, SIDE_SOLE = 162, 165    # hd/side.png: the hooves' middle column and their last row
SIDE_DX, SIDE_DY = PIV - SIDE_MID, SOLE - SIDE_SOLE
OUTLINE = 0                       # palette index of the near-black outline (the darkest colour)
HOOF = {1, 6}                     # palette indices of the hooves (the side design's bottom rows)
# per frame: the head match (draft px a square, the template's top-left x, y in draft px), from head_match
# (masked Lab SSD of the side design's mask head over 4.4-8.0 at half resolution, refined at full; 2026-10-14). The
# drafts' sizes drift within an action (Q 4.56 -> 5.71: the error curves have clear minima, and the standing frames'
# ear-to-hoof heights agree with them), so every frame is cut at its own scale; where Codex turned the head (the ult's
# raised-bow frame, the lying death frames) the match is poor and the action's median scale is used instead (BAD).
HEADS = {
    "run_1": (4.50, 955, 238), "run_2": (4.50, 946, 246), "run_3": (4.80, 948, 224), "run_4": (4.80, 926, 221),
    "run_5": (5.10, 904, 216), "run_6": (4.41, 955, 287), "run_7": (5.03, 890, 215), "run_8": (4.80, 890, 228),
    "attack_1": (4.60, 820, 174), "attack_2": (4.86, 783, 286), "attack_3": (4.70, 792, 298),
    "attack_4": (5.00, 832, 258), "attack_5": (4.86, 831, 221),
    "skill_1": (4.56, 849, 438), "skill_2": (4.59, 889, 266), "skill_3": (4.70, 838, 232), "skill_4": (4.50, 818, 232),
    "skill_5": (5.71, 812, 274), "skill_6": (5.40, 736, 161),
    "skill2_1": (4.44, 839, 213), "skill2_2": (5.60, 876, 264), "skill2_3": (4.86, 895, 320),
    "skill2_4": (5.43, 908, 267), "skill2_5": (5.30, 814, 103),
    "w_cast_1": (4.60, 792, 306), "w_cast_2": (4.28, 790, 321), "w_cast_3": (5.00, 842, 214),
    "w_cast_4": (5.10, 810, 160),
    "ult_1": (4.82, 817, 313), "ult_2": (4.90, 841, 376), "ult_3": (4.70, 896, 472), "ult_4": (4.83, 798, 222),
    "ult_5": (4.13, 755, 334), "ult_6": (4.76, 782, 218),
    "dead_1": (4.28, 890, 404), "dead_2": (4.73, 891, 382), "dead_3": (4.80, 936, 434), "dead_4": (4.28, 1071, 498),
    "dead_5": (4.31, 1047, 568), "dead_6": (4.31, 1069, 724),
}
# ult_5: Codex drew her 0.85x there (its HANDOFF: 「R 高举弓帧的身体明显变小」; legs from the fur skirt to the hooves
# 190 draft px against 216-227 in ult_4 / ult_6, about 46 squares at 4.8) -> 4.13 from the legs; the head (bowed and
# turned: the colour match put it 23 squares too low) placed by its near eye (draft 448, 812 = the template's 27.7, 13.9)
BAD = {"dead_4", "dead_5", "dead_6"}
AIR = {"skill_3", "skill_4"}       # off the ground: kept at the height the draft has them over its ground line


def block_vote(idx, s, x, y, hr, hc):
    """The draft (palette indices) voted down to the canvas in blocks of s draft px; the block of square (hr, hc)
    starts at draft (x, y). Each square: clear where half or more is clear; the outline where 40 % or more of the drawn
    part is; else the commonest colour."""
    H, W = idx.shape
    cols = np.floor((np.arange(W) - x) / s).astype(int) + hc
    rows = np.floor((np.arange(H) - y) / s).astype(int) + hr
    ok_c = (cols >= 0) & (cols < COLS)
    ok_r = (rows >= 0) & (rows < ROWS)
    sub = idx[np.ix_(ok_r, ok_c)]
    rr = np.repeat(rows[ok_r][:, None], ok_c.sum(), 1)
    cc = np.repeat(cols[ok_c][None, :], ok_r.sum(), 0)
    sq = (rr * COLS + cc).ravel()
    npal = 41
    k = sub.ravel() + 1                                  # 0 clear, 1.. colours
    cnt = np.bincount(sq * npal + k, minlength=ROWS * COLS * npal).reshape(ROWS * COLS, npal)
    tot = cnt.sum(1)
    drawn = tot - cnt[:, 0]
    out = np.full(ROWS * COLS, -1)
    keep = (tot > 0) & (drawn * 2 > tot)
    best = cnt[:, 1:].argmax(1)
    out[keep] = best[keep]
    dark = keep & (cnt[:, 1 + OUTLINE] >= 0.4 * np.maximum(drawn, 1))
    out[dark] = OUTLINE
    return out.reshape(ROWS, COLS)


def shift(a, dr, dc, fill=-1):
    out = np.full_like(a, fill)
    H, W = a.shape[:2]
    ys0, ys1 = max(0, dr), min(H, H + dr)
    xs0, xs1 = max(0, dc), min(W, W + dc)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dr:ys1 - dr, xs0 - dc:xs1 - dc]
    return out


def frame_scale(name):
    tag = name.rsplit("_", 1)[0]
    if name in BAD:
        return float(np.median([v[0] for k, v in HEADS.items() if k.rsplit("_", 1)[0] == tag and k not in BAD]))
    return HEADS[name][0]


def cut_frame(name):
    """(canvas of palette indices, the head template's top-left (row, col) on it, scale)."""
    tpl, _ = head_template()
    s0, x, y = HEADS[name]
    s = frame_scale(name)
    if s != s0:                                   # a poor head match: centre the template's box at the found place
        x += (tpl.shape[1] * (s0 - s)) / 2
        y += (tpl.shape[0] * (s0 - s)) / 2
    hc = int(round(PIV + (x - PACK_PIV[0]) / s))
    hr = int(round(SOLE + 1 + (y - PACK_PIV[1]) / s))
    can = block_vote(load_draft("kindred_" + name), s, x, y, hr, hc)
    return can, (hr, hc), s


def ground(can, name, head):
    """Lowest drawn square on SOLE (the airborne frames keep their height), the hooves' middle on PIV."""
    hr, hc = head
    op = can >= 0
    ys, xs = np.nonzero(op)
    dr = 0 if name in AIR else SOLE - ys.max()
    hoof = np.isin(can, list(HOOF))
    low = hoof & (np.arange(ROWS)[:, None] >= ys.max() - 12)
    hx = np.nonzero(low)[1]
    if name in AIR:                               # off the ground: the hooves' middle wherever they are
        hx = np.nonzero(hoof)[1]
    dc = int(round(PIV - (hx.min() + hx.max()) / 2.0)) if len(hx) and not name.startswith("dead") else 0
    if name.startswith("run"):                    # the body steady, the legs swinging under it: by the head
        dc = RUN_HEAD_COL - hc
    return shift(can, dr, dc), (hr + dr, hc + dc)


def paste_head(can, head):
    tpl, (dy, dx) = paste_template()
    pal = palette()
    hr, hc = head[0] + dy, head[1] + dx
    key = {tuple(int(v) for v in c): i for i, c in enumerate(pal)}
    ys, xs = np.nonzero(tpl[..., 3] > 0)
    out = can.copy()
    for y, x in zip(ys, xs):
        r, c = hr + y, hc + x
        if 0 <= r < ROWS and 0 <= c < COLS:
            out[r, c] = key[tuple(int(v) for v in tpl[y, x, :3])]
    return out


# Codex's own heads sit a square or a few off the pasted one, so its ears, crescent or cheek stick out beside the
# design's mask (doubled ears: 2026-10-14 review). The mask's own violets near the pasted mask, joined to it, go, with
# their outline; what lies inside the figure is filled from the fur round it, never with the mask's colours.
MASKC = [23, 5, 15]               # the mask's violets (9 is the legs' too: only beside removed squares)
NO_HEAD = {"dead_3", "dead_4", "dead_5", "dead_6"}   # falling / lying: Codex's own head (Nilah's way, art memory)


def clear_old_head(can, head):
    hb = head_box(head)
    ring = ndimage.binary_dilation(hb, iterations=10) & ~hb
    near = ndimage.binary_dilation(hb, iterations=2)
    old = ring & np.isin(can, MASKC)
    lbl, m = ndimage.label(old, structure=np.ones((3, 3)))
    rm = np.zeros_like(old)
    for j in range(1, m + 1):
        piece = lbl == j
        if (piece & near).any():
            rm |= piece
    rm |= ring & (can == 9) & ndimage.binary_dilation(rm, structure=np.ones((3, 3)))
    dark = np.isin(can, [OUTLINE, 1])
    body = (can >= 0) & ~dark & ~np.isin(can, MASKC + [9]) & ~hb
    rm |= (ndimage.binary_dilation(rm, structure=np.ones((3, 3))) & dark & ~hb
           & ~ndimage.binary_dilation(body, structure=np.ones((3, 3))))
    out = inpaint(can, rm, avoid=MASKC + [9])
    # the old ears' outline left round nothing: dark squares in the ring with no coloured square 4-next to them
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    for _ in range(3):
        drawn = out >= 0
        dk = drawn & np.isin(out, [OUTLINE, 1])
        lit = drawn & ~dk
        bare = dk & ring & ~ndimage.binary_dilation(lit, structure=cross)
        if not bare.any():
            break
        out[bare] = -1
        rm |= bare
    return out, int(rm.sum())


# ------------------------------------------------------------------------------------------------- one bow
# The design's bow (hd/side.png, rows 0-165, columns BOW_C0...): its limbs right of the string, the top tip hooking
# back over the string to column 179, the string three columns (navy, white, navy) from TIP_ROWS[0] to TIP_ROWS[1];
# the hand covers rows 75-88 there, so the grip under it is rebuilt straight (the limb's width at rows 74 and 89:
# outline 193, limb 194-199, outline 200). (A first box from column 186 cut the hook off.)
BOW_C0, BOW_C1 = 178, 236
STRING_C = 189                    # the string's white column (188 and 190 navy)
TIP_ROWS = (19, 147)              # the string's ends on the tips, as drawn on side.png
GRIP_ROW = 82                     # the grip's middle (under the hand)
BOWCORE = {7, 8, 13, 14, 17, 18, 20, 24}      # colours only the bow has (the legs, fur and mask use 10, 21, 25)
STRINGC = {38, 34, 33, 6}         # the string: white core, navy sides
SKIN = {25, 26, 28, 29, 32, 33, 34, 38}       # the hands and arms (pale lavender to white)
NAVY, WHITE = 6, 38
ARROWC = [22, 31, 35, 37, 39]     # the greys and creams of Codex's arrows (shaft, head)


def design_idx(a):
    pal = palette()
    key = {tuple(int(v) for v in c): i for i, c in enumerate(pal)}
    out = np.full(a.shape[:2], -1)
    m = a[..., 3] > 0
    out[m] = [key[tuple(int(v) for v in p)] for p in a[m][:, :3]]
    return out


def bow_template(string=True):
    """The design bow on its box (palette indices, -1 clear); local (row, col) = (design row, design col - BOW_C0)."""
    side = design_idx(side_design())
    bt = side[0:166, BOW_C0:BOW_C1].copy()
    bt[75:90, 0:207 - BOW_C0] = -1                         # the hand and the arm (columns 178-206; row 89 its edge)
    g0 = 193 - BOW_C0
    for r in range(75, 90):                                # the grip under the hand
        bt[r, g0] = OUTLINE
        bt[r, g0 + 1:g0 + 7] = [13, 13, 17, 17, 20, 17]
        bt[r, g0 + 7] = OUTLINE
    # only the bow: the pieces holding its own colours (the fur, the arm and the front hoof reach into the box)
    lbl, n = ndimage.label(bt >= 0, structure=np.ones((3, 3)))
    core = np.isin(bt, list(BOWCORE))
    keep = [k for k in range(1, n + 1) if (core & (lbl == k)).sum() >= 20]
    bt[~np.isin(lbl, keep)] = -1
    sc = STRING_C - BOW_C0
    bt[TIP_ROWS[0]:TIP_ROWS[1] + 1, sc - 1:sc + 2] = -1
    if string:
        for r in range(TIP_ROWS[0], TIP_ROWS[1] + 1):
            bt[r, sc - 1:sc + 2] = [NAVY, WHITE, NAVY]
    return bt


def line_px(a, b):
    """Integer points on the segment a -> b (row, col), Bresenham-like (every step one row or one column)."""
    (r0, c0), (r1, c1) = a, b
    n = int(max(abs(r1 - r0), abs(c1 - c0))) + 1
    rr = np.rint(np.linspace(r0, r1, n)).astype(int)
    cc = np.rint(np.linspace(c0, c1, n)).astype(int)
    return rr, cc


def seg_dist(pts, a, b):
    """Distance of points (N, 2) to the segment a-b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    t = np.clip(((pts - a) @ d) / max(d @ d, 1e-9), 0, 1)
    return np.hypot(*(pts - (a + t[:, None] * d)).T)


def thin_white(can):
    """White squares in lines one or two squares wide (the string), not in the fur's broad white."""
    white = np.isin(can, [WHITE, 34])
    broad = ndimage.binary_opening(white, structure=np.ones((3, 3)))
    return white & ~ndimage.binary_dilation(broad, iterations=1)


def hough_lines(pts, n_lines=2, min_len=30, gap=24):
    """Straight runs in the points (row, col): [(a, b, inliers)], the longest first. Each line: the Hough peak over
    directions, its inliers within 1.2 squares, cut to its longest run with gaps under `gap` squares (the string
    passes behind the head)."""
    pts = np.asarray(pts, float)
    lines = []
    left = np.ones(len(pts), bool)
    for _ in range(n_lines):
        P = pts[left]
        if len(P) < min_len // 2:
            break
        best = None
        for th in np.radians(np.arange(-88, 89, 1.0)):
            d = np.array([np.cos(th), np.sin(th)])
            nrm = np.array([-d[1], d[0]])
            rho = P @ nrm
            h, edges = np.histogram(rho, bins=np.arange(rho.min() - 1, rho.max() + 2, 1.0))
            k = h.argmax()
            if best is None or h[k] > best[0]:
                best = (h[k], d, nrm, (edges[k] + edges[k + 1]) / 2)
        _, d, nrm, rho0 = best
        dist = np.abs(pts @ nrm - rho0)
        inl = left & (dist <= 1.2)
        t = pts[inl] @ d
        order = np.argsort(t)
        ts = t[order]
        idx = np.nonzero(inl)[0][order]
        runs, start = [], 0
        for i in range(1, len(ts) + 1):
            if i == len(ts) or ts[i] - ts[i - 1] > gap:
                runs.append((ts[i - 1] - ts[start], start, i))
                start = i
        length, s0, s1 = max(runs)
        if length < min_len:
            break
        members = idx[s0:s1]
        a, b = pts[members[0]], pts[members[-1]]
        lines.append((a, b, members))
        left[members] = False
        left &= ~((np.abs(pts @ nrm - rho0) <= 1.5) & (pts @ d >= ts[s0] - 1) & (pts @ d <= ts[s1 - 1] + 1))
    return lines


LINES = []                                 # every line old_string found (its two ends), for inpaint's sides


def edge_like(can, sq, a, b, off=3):
    """True when the line runs along the silhouette: at most of its squares one side (off squares across) is clear
    and the other drawn in a body colour - a white rim of fur or tail inside the outline, not a string or an arrow
    (those have clear, dark or body colour on BOTH sides). The first version erased such rims with their outline
    (2026-10-14: a thin ring of the silhouette gone on the tail's top and the fur's back)."""
    d = np.asarray(b, float) - np.asarray(a, float)
    L = np.hypot(*d)
    if L < 1:
        return False
    n = np.array([-d[1], d[0]]) / L
    H, W = can.shape
    edge = 0
    for r, c in sq:
        sides = []
        for sgn in (1, -1):
            rr, cc = int(round(r + sgn * off * n[0])), int(round(c + sgn * off * n[1]))
            v = can[rr, cc] if 0 <= rr < H and 0 <= cc < W else -1
            sides.append("clear" if v < 0 else ("dark" if v in (OUTLINE, 1, NAVY) else "lit"))
        if "clear" in sides and "lit" in sides:
            edge += 1
    return edge > 0.4 * len(sq)


def old_string(can, region, foot, rest=False):
    """Codex's string and arrows: {"top", "bottom": the string's ends at the bow, "draw": the draw point or None,
    "erase": the squares to clear}. Thin white lines (hough_lines) near the bow: a near-level one is an arrow (Codex
    drew some; none are wanted); a line with an end at the bow is the string - two meeting left of the bow, or one
    leaving the bow (the other half behind the body), is a drawn string; one along the bow is a string at rest."""
    LINES.clear()
    tw = thin_white(can)
    near = ndimage.binary_dilation(region | foot, iterations=100)
    pts = np.argwhere(tw & near)
    if len(pts) < 15:
        return None
    lines = hough_lines(pts, n_lines=4, min_len=15)
    if not lines:
        return None
    reach = ndimage.binary_dilation(region | foot, iterations=8)
    top_row = int(np.nonzero((can >= 0).any(1))[0].min())
    reach[:top_row + 4, :] = True                 # Codex's bow ran over its canvas's top in some frames
    arrow_reach = ndimage.binary_dilation(region | foot, iterations=15)
    erase, arrows, strings = [], [], []
    for a, b, m in lines:
        if edge_like(can, pts[m], a, b):
            continue                              # the fur's or the tail's white rim along the outline
        dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
        if dr < 0.35 * dc:
            # an arrow: nocked on the bow, so one end reaches it
            if arrow_reach[int(a[0]), int(a[1])] or arrow_reach[int(b[0]), int(b[1])]:
                arrows.append(pts[m])
                LINES.append((a, b))
            continue
        ea, eb = bool(reach[int(a[0]), int(a[1])]), bool(reach[int(b[0]), int(b[1])])
        if not (ea or eb) and not (rest and np.hypot(*(a - b)) >= 40):
            continue
        erase.append(pts[m])
        LINES.append((a, b))
        strings.append((a, b, ea, eb))
    out = {"erase": np.concatenate(erase) if erase else np.zeros((0, 2), int),
           "arrows": np.concatenate(arrows) if arrows else np.zeros((0, 2), int), "draw": None, "top": None,
           "bottom": None}
    diag = []
    for a, b, ea, eb in strings:
        if ea and eb and abs(a[1] - b[1]) < 0.25 * abs(a[0] - b[0]):
            top, bot = (a, b) if a[0] < b[0] else (b, a)
            out["top"], out["bottom"] = tuple(int(v) for v in top), tuple(int(v) for v in bot)
            return out                            # at rest
        tip, far = (a, b) if (ea and not eb) or (ea and eb and a[1] > b[1]) else (b, a)
        if tip[1] - far[1] >= 12:
            diag.append((tip, far))
    if len(diag) >= 2:
        (t1, f1), (t2, f2) = sorted(diag, key=lambda x: x[0][0])[:2]
        if abs(t1[0] - t2[0]) > 50:
            d1, d2 = f1 - t1, f2 - t2
            A = np.array([d1, -d2]).T
            if abs(np.linalg.det(A)) > 1e-6:
                t = np.linalg.solve(A, t2 - t1)
                q = t1 + t[0] * d1
                if (q[1] < min(t1[1], t2[1]) - 8 and t1[0] < q[0] < t2[0]
                        and np.hypot(*(q - f1)) < 50 and np.hypot(*(q - f2)) < 50):
                    out["draw"] = (int(round(q[0])), int(round(q[1])))
                    return out
    if diag:
        tip, far = max(diag, key=lambda x: np.hypot(*(x[0] - x[1])))
        out["draw"] = (int(round(far[0])), int(round(far[1])))
    return out


def inpaint(can, holes, k=4, lines=(), across=7, avoid=()):
    """Erased squares that lie inside the figure - drawn squares within k of them on both sides along a row or along
    a column (an arrow drawn over the arm, a string over the fur) - take the commonest colour of their drawn
    neighbours, filled from the edges inwards (the outline only where nothing else is next to them); the others (the
    arrow or the string where they crossed the background) stay clear."""
    can = can.copy()
    can[holes] = -1
    drawn = can >= 0
    H, W = can.shape
    inside = np.zeros_like(holes)
    for r, c in zip(*np.nonzero(holes)):
        up = drawn[max(0, r - k):r, c].any()
        dn = drawn[r + 1:r + k + 1, c].any()
        lf = drawn[r, max(0, c - k):c].any()
        rt = drawn[r, c + 1:c + k + 1].any()
        inside[r, c] = (up and dn) or (lf and rt)
    # a string / an arrow crossing a limb at a slant: drawn on both sides within `across` squares at right angles to
    # the line (dead_3's string over her forearm - the row / column test missed the slanting band)
    for a, b in lines:
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b - a
        L = np.hypot(*d)
        if L < 1:
            continue
        n = np.array([-d[1], d[0]]) / L
        for r, c in zip(*np.nonzero(holes & ~inside)):
            if seg_dist(np.array([[r, c]], float), a, b)[0] > 5:
                continue
            side = []
            for sgn in (1, -1):
                hit = False
                for t in range(1, across + 1):
                    rr, cc = int(round(r + sgn * t * n[0])), int(round(c + sgn * t * n[1]))
                    if 0 <= rr < H and 0 <= cc < W and drawn[rr, cc]:
                        hit = True
                        break
                side.append(hit)
            if all(side):
                inside[r, c] = True
    todo = holes & inside
    for _ in range(60):
        if not todo.any():
            break
        nxt = todo.copy()
        fill = []
        for r, c in zip(*np.nonzero(todo)):
            nb = can[max(0, r - 1):r + 2, max(0, c - 1):c + 2].ravel()
            nb = nb[nb >= 0]
            if len(nb) < 2:
                continue
            lit = nb[(nb != OUTLINE) & ~np.isin(nb, list(avoid))]
            vals, cnt = np.unique(lit if len(lit) else nb, return_counts=True)
            fill.append((r, c, vals[cnt.argmax()]))
        for r, c, v in fill:
            can[r, c] = v
            nxt[r, c] = False
        if (nxt == todo).all():
            break
        todo = nxt
    return can


def fix_bow(can, name, head):
    """Codex's bow, string and arrows out; the design's bow in (rigid, only moved; laid level in the lying death
    frames), its grip under Codex's hand; the string from its tips to the draw point, or straight at rest."""
    lying = name in LYING_BOW
    bt = bow_template(string=True)
    if lying:
        bt = np.rot90(bt, LYING_BOW[name])
    limb = np.isin(bt, list(BOWCORE)).astype(float)
    core = np.isin(can, list(BOWCORE))
    pad = 60
    corr = signal.fftconvolve(np.pad(core.astype(float), pad), limb[::-1, ::-1], mode="valid")
    j = np.unravel_index(np.argmax(corr), corr.shape)
    oy, ox = int(j[0] - pad), int(j[1] - pad)
    hb = head_box(head)

    def footprint(oy, ox):
        f = np.zeros((ROWS, COLS), bool)
        ys, xs = np.nonzero(bt >= 0)
        ok = (ys + oy >= 0) & (ys + oy < ROWS) & (xs + ox >= 0) & (xs + ox < COLS)
        f[ys[ok] + oy, xs[ok] + ox] = True
        return f
    foot = footprint(oy, ox)
    zone = ndimage.binary_dilation(foot, structure=np.ones((33, 17)))
    if name in WIDE:
        zone = ndimage.binary_dilation(zone, structure=np.ones((61, 61)))
    # Codex's bow: the bow-only colour pieces mostly in the zone, their holes, their outline and rims
    lbl, n = ndimage.label(core, structure=np.ones((3, 3)))
    region = np.zeros_like(core)
    for k in range(1, n + 1):
        piece = lbl == k
        if (piece & zone).sum() * 2 >= piece.sum() and not (piece & hb).sum() * 2 >= piece.sum():
            region |= piece
    region = ndimage.binary_fill_holes(region) & (can >= 0)
    region |= ndimage.binary_dilation(region, structure=np.ones((3, 3))) & np.isin(can, [OUTLINE, NAVY])
    for _ in range(2):
        grow = ndimage.binary_dilation(region, structure=np.ones((3, 3))) & zone
        # (not 21 / 25: the arms and legs are drawn in those violets - taking them cut dead_3's forearm off,
        # the user: 「手还断了？」)
        region |= grow & np.isin(can, [OUTLINE, NAVY, 10, 11, 27, 2, 3, 4])
    hand = np.isin(can, list(SKIN)) & ~region & ~hb
    # the grip goes into Codex's hand (the user: 「手还断了？」 - placed by Codex's tilted bow, the upright bow missed the
    # hand): the fist is the hand-coloured piece touching Codex's bow in its middle rows; the design's fist spans
    # rows 75-88 and columns 186-210 round the grip, so its middle (81.5, 198) goes on the fist's middle
    if not lying and region.any():
        rys = np.nonzero(region.any(1))[0]
        r0, r1 = rys.min(), rys.max()
        band = np.zeros_like(region)
        band[int(r0 + 0.25 * (r1 - r0)):int(r0 + 0.75 * (r1 - r0)) + 1] = True
        touch = hand & ndimage.binary_dilation(region, iterations=2) & band
        if name in GRIP:
            hy, hx = GRIP[name]
        elif touch.sum() >= 6:
            lbl_t, nt = ndimage.label(touch, structure=np.ones((3, 3)))
            big = int(np.argmax(ndimage.sum(touch, lbl_t, range(1, nt + 1)))) + 1
            # the whole fist: the hand squares within 6 of that touching piece
            fist = hand & ndimage.binary_dilation(lbl_t == big, iterations=6)
            hy, hx = np.argwhere(fist).mean(0)
        else:
            hy = hx = None
        if hy is not None:
            oy = int(round(hy - 81.5))
            ox = int(round(hx - (198 - BOW_C0)))
            foot = footprint(oy, ox)
        FIST[0] = (hy, hx)
    s = old_string(can, region, foot, rest=name in REST)
    erase = region.copy()
    draw_point = None
    if s is not None:
        # each found line's whole width: its white core, the white beside it (one square), the dark edges (up to
        # three; Codex's string is outline, white, white, outline; its arrows have a grey shaft, dark fletching).
        # Never the pale colours further out: where the string crossed her arm they are the arm (a band of 3 white
        # squares cut dead_3's forearm off - 「手还断了？」); inpaint fills the arm in under the string.
        for key, dark_band, dark_cols in (("erase", 7, [OUTLINE, 1, NAVY]),
                                          ("arrows", 5, [OUTLINE, 1, NAVY] + ARROWC)):
            sq = s[key]
            if len(sq):
                lines = np.zeros_like(erase)
                lines[sq[:, 0], sq[:, 1]] = True
                erase |= lines
                erase |= ndimage.binary_dilation(lines, structure=np.ones((3, 3))) & np.isin(can, [WHITE, 34])
                erase |= ndimage.binary_dilation(lines, structure=np.ones((dark_band, dark_band))) & np.isin(
                    can, dark_cols)
        draw_point = None if name in REST else s["draw"]
    shaft = None
    if draw_point is not None and FIST[0] is not None and FIST[0][0] is not None:
        # Codex's nocked arrow lying along the bow arm (a dark / grey line between the drawing hand and the grip, inside
        # the arm: skill_5, skill2_3 - read as a bar on the arm at game size): its squares within 3 of the segment from
        # the draw point to the fist, with the arm's own colours above and below them
        a_, b_ = np.array(draw_point, float), np.array(FIST[0], float)
        pts = np.argwhere(np.isin(can, [OUTLINE, 1, NAVY] + ARROWC))
        near_seg = pts[seg_dist(pts.astype(float), a_, b_) <= 3.0]
        lit = (can >= 0) & ~np.isin(can, [OUTLINE, 1, NAVY] + ARROWC)
        for r, c in near_seg:
            if lit[max(0, r - 3):r, c].any() and lit[r + 1:r + 4, c].any() and not hb[r, c]:
                erase[r, c] = True
        shaft = (tuple(a_), tuple(b_))
    for r0, c0, r1, c1 in EXTRA_ERASE.get(name, ()):
        box = np.zeros_like(erase)
        box[r0:r1 + 1, c0:c1 + 1] = True
        erase |= box & (can >= 0)
    erase &= ~hb
    ZONE[0] = ndimage.binary_dilation(erase, structure=np.ones((13, 13)))
    out = inpaint(can, erase, lines=list(LINES))
    sc = STRING_C - BOW_C0
    ys, xs = np.nonzero(bt >= 0)
    for y, x in zip(ys, xs):
        r, c = y + oy, x + ox
        if not (0 <= r < ROWS and 0 <= c < COLS):
            continue
        string_px = (not lying) and sc - 1 <= x <= sc + 1 and TIP_ROWS[0] <= y <= TIP_ROWS[1]
        if string_px and draw_point is not None:
            continue
        if hand[r, c] and abs(y - GRIP_ROW) <= 9:
            continue
        out[r, c] = bt[y, x]
    drawn = np.zeros((ROWS, COLS), bool)
    if draw_point is not None:
        # a slanting string two squares of white wide with a navy edge each side: one square of white between two navy
        # came out a dark grey bar once the frames went to Zeri's density (the area mean of 2.86 / 4.53 squares)
        for tip in ((TIP_ROWS[0] + oy, sc + ox), (TIP_ROWS[1] + oy, sc + ox)):
            rr, cc = line_px(tip, draw_point)
            steep = abs(draw_point[0] - tip[0]) >= abs(draw_point[1] - tip[1])
            across = ((0, -1), (0, 2), (0, 1)) if steep else ((-1, 0), (2, 0), (1, 0))   # navy, navy, white
            for r, c in zip(rr, cc):
                if not (0 <= r < ROWS and 0 <= c < COLS) or hb[r, c]:
                    continue
                if hand[r, c] and abs(r - draw_point[0]) + abs(c - draw_point[1]) <= 6:
                    continue
                for j, (dr, dc) in enumerate(across):
                    rn, cn = r + dr, c + dc
                    if not (0 <= rn < ROWS and 0 <= cn < COLS) or hb[rn, cn]:
                        continue
                    if j < 2 and out[rn, cn] != WHITE and not drawn[rn, cn]:
                        out[rn, cn] = NAVY
                        drawn[rn, cn] = True
                    elif j == 2:
                        out[rn, cn] = WHITE
                        drawn[rn, cn] = True
                out[r, c] = WHITE
                drawn[r, c] = True
    # the new bow and the string drawn here (a first version took every white and navy square of the frame for it,
    # so the clean-up below never saw Codex's string ends)
    BOWMASK[0] = footprint(oy, ox) | drawn
    return out, (oy, ox), draw_point


BOWMASK = [None]                           # the new bow's squares (and its drawn string) of the last fix_bow
ZONE = [None]                              # where the last fix_bow erased Codex's bow / string / arrows, grown by 6
FIST = [None]                              # the fist's middle (row, col) the last fix_bow put the grip on
# frame -> the fist's middle (row, col), read off Codex's drawing at 4x where the finder took a leg or the fur for the
# hand (the bow held close to the body; 2026-10-14)
GRIP = {"attack_5": (134.5, 213), "ult_2": (148, 237), "ult_6": (134, 208)}
LYING_BOW = {"dead_5": 1, "dead_6": 1}     # the bow laid level (np.rot90 turns): the lying death frames
WIDE = {"w_cast_2", "ult_5", "dead_3", "dead_4"}   # Codex's bow tilted or raised: cleared from a wider zone
# Codex's old bow left where no zone reaches it, cleared by hand (rows r0-r1, cols c0-c1 inclusive): dead_5's lower
# tip under her body (a wider zone took her shoulder pad, which has the bow's teal and violets, for the bow)
EXTRA_ERASE = {"dead_5": [(195, 126, 212, 153)]}
# the string at rest (straight, as on the design) whatever Codex drew: the run, the frames after a shot, the casts
# that only hold or raise the bow, the death
# (not w_cast_1, ult_1, dead_1: Codex drew her back hand on the string there - a straight string left it floating)
REST = ({"attack_4", "attack_5", "skill_6", "skill2_4", "skill2_5"} | {f"w_cast_{k}" for k in range(2, 5)}
        | {f"ult_{k}" for k in range(2, 7)} | {f"dead_{k}" for k in range(2, 7)} | {f"run_{k}" for k in range(1, 9)})
RUN_HEAD_COL = 164                # the run: every frame's head (template's left column) here - the idle's place


def thin_dark(out, bow=None):
    """(thin dark squares, lit squares): dark squares (outline, navy) in lines at most two squares wide - the old
    string's edges, an outline ring - not in a dark mass three or more squares across (the hooves are navy and
    near-black: a first version without this cleared them, 2026-10-14); lit = every other drawn square."""
    op = out >= 0
    if bow is not None:
        op = op & ~bow
    dark = op & np.isin(out, [OUTLINE, 1, NAVY])
    thick = ndimage.binary_opening(dark, structure=np.ones((3, 3)))
    thin = dark & ~ndimage.binary_dilation(thick, structure=np.ones((3, 3)))
    return thin, op & ~dark


def final_clean(can, bow=None, zone=None, head=None):
    """Thin dark lines with no coloured square within two (left from Codex's bow and string), and loose pieces under
    40 squares (the old bow's tips, its specks), cleared."""
    # "no body colour near" = none within three squares: Codex's outline is two to three squares thick, and with two
    # the outer square of a three-square ring counted as loose - peeled off from the bow it ran round the whole
    # silhouette (2026-10-14: a missing outer ring on the fur and the tail). Both steps stay where Codex's bow was.
    out = can.copy()
    thin, lit = thin_dark(out)
    loose = thin & ~ndimage.binary_dilation(lit, structure=np.ones((7, 7)))
    if zone is not None:                       # only where Codex's bow was (the fur's spiky tips stay)
        loose &= zone
    out[loose] = -1
    # the old string's dark edges left beside the new bow: thin dark squares with no body colour within three, peeled
    # off from the new bow outwards, a few squares at most
    if bow is not None:
        touched = bow.copy()
        for _ in range(6):
            dk, lit = thin_dark(out, bow)
            peel = dk & ~ndimage.binary_dilation(lit, structure=np.ones((7, 7))) & ndimage.binary_dilation(
                touched, structure=np.ones((3, 3)))
            if zone is not None:
                peel &= zone
            if not peel.any():
                break
            out[peel] = -1
            touched |= peel
    # Codex's old string's short ends: thin white runs (with the dark squares beside them) that touch no body colour -
    # only the background, the outline or the new bow (dead_3's tick by the snout, dead_5 / dead_6's dashes)
    if bow is not None:
        op = out >= 0
        pale = [WHITE, 34, 33, 39]                 # the string's white and the light blues next to it
        white = op & np.isin(out, pale) & ~bow
        thick_w = ndimage.binary_opening(white, structure=np.ones((3, 3)))
        tw = white & ~ndimage.binary_dilation(thick_w, structure=np.ones((3, 3)))
        dark = op & np.isin(out, [OUTLINE, 1, NAVY])
        body = op & ~bow & ~dark & ~np.isin(out, pale)
        near_head = ndimage.binary_dilation(head_box(head), iterations=4) if head is not None else np.zeros_like(tw)
        lbl, n = ndimage.label(tw, structure=np.ones((3, 3)))
        for k in range(1, n + 1):
            piece = lbl == k
            if piece.sum() > 24 or (ndimage.binary_dilation(piece, structure=np.ones((3, 3))) & body).any():
                continue
            if (piece & near_head).any():             # the fur under the pasted mask's chin is Codex's, keep it
                continue
            ring = ndimage.binary_dilation(piece, structure=np.ones((3, 3))) & dark & ~bow
            ring &= ~ndimage.binary_dilation(body, structure=np.ones((3, 3)))
            out[piece | ring] = -1
    # loose pieces - counted with the new bow left out, so the old bow's bits that touch only the new bow go too
    op = (out >= 0) & (~bow if bow is not None else True)
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < 40:
                out[lbl == k] = -1
    return out


def head_box(head):
    tpl, (dy, dx) = paste_template()
    m = np.zeros((ROWS, COLS), bool)
    hr, hc = head[0] + dy, head[1] + dx
    ys, xs = np.nonzero(tpl[..., 3] > 0)
    ok = (ys + hr >= 0) & (ys + hr < ROWS) & (xs + hc >= 0) & (xs + hc < COLS)
    m[ys[ok] + hr, xs[ok] + hc] = True
    return m


def to_rgba(can, pal):
    out = np.zeros(can.shape + (4,), np.uint8)
    m = can >= 0
    out[m, :3] = pal[can[m]]
    out[m, 3] = 255
    return out


def review_strip(path, row):
    from PIL import ImageDraw
    ys, xs = np.nonzero(np.any([r[..., 3] > 0 for r in row], 0))
    y0, y1 = max(0, ys.min() - 2), min(ROWS, max(ys.max(), SOLE) + 3)
    x0, x1 = max(0, xs.min() - 2), min(COLS, xs.max() + 3)
    z = 3
    w, h = (x1 - x0) * z, (y1 - y0) * z
    big = Image.new("RGBA", (len(row) * (w + 8), h), (110, 120, 100, 255))
    d = ImageDraw.Draw(big)
    for i, r in enumerate(row):
        big.alpha_composite(Image.fromarray(r[y0:y1, x0:x1]).resize((w, h), Image.NEAREST), (i * (w + 8), 0))
        gy = (SOLE + 1 - y0) * z
        d.line([(i * (w + 8), gy), (i * (w + 8) + w, gy)], fill=(255, 0, 0, 255))
        px = i * (w + 8) + (PIV - x0) * z + z // 2
        d.line([(px, gy - 8), (px, gy + 8)], fill=(0, 0, 255, 255))
    big.convert("RGB").save(path)


def close_outline(can, pal):
    """strips.complete_outline on the frame (the figure's ring closed where an erase or a paste opened it)."""
    import strips as G
    rgba = to_rgba(can, pal)
    rgba = G.complete_outline(rgba, color=tuple(int(v) for v in pal[OUTLINE]))[0]
    key = {tuple(int(v) for v in c): i for i, c in enumerate(pal)}
    out = np.full(can.shape, -1)
    m = rgba[..., 3] > 0
    out[m] = [key[tuple(int(v) for v in p)] for p in rgba[m][:, :3]]
    return out


# ------------------------------------------------------------------------------------------------- the run's legs
# Codex drew the near (light) leg in front in seven of its eight run frames - a bound, not League's run, whose legs
# take turns (2026-10-14 review against the native_pose skeletons). Its fifth frame has them the other way round. So
# the loop is Codex's own frames in this order, three of them with the two legs' shades swapped (shapes and places
# untouched - the forward leg drawn dark as the far leg, the back one light as the near leg): the near leg then goes
# forward contact, stance, push, back, kick, knee-up, reach; the far leg half a loop later. (Moving the legs' shapes
# onto each other's hips was tried first: the hips under the fur skirt are not where the legs' visible tops are, and
# the legs came out misplaced.)
RUN_ORDER = [("run_1", False), ("run_3", False), ("run_4", True), ("run_1", True), ("run_5", False),
             ("run_3", True), ("run_4", False), ("run_6", False)]
LEG_DARK = [9, 5, 12, 13, 15, 16]
LEG_LIGHT = [20, 21, 25, 28, 29]
# per swapped frame: a square on the far (dark) leg, one on the near (light) leg, and the box (rows from, cols from-to)
# that keeps the near leg's flood out of the fur skirt's own violets
RUN_LEGS = {"run_1": dict(far=(185, 90), near=(190, 177), box=(160, 158, 215)),
            "run_3": dict(far=(168, 135), near=(185, 168), box=(162, 160, 210)),
            "run_4": dict(far=(185, 140), near=(175, 168), box=(150, 160, 200))}
TO_LIGHT = {5: 20, 9: 21, 15: 20, 12: 21, 13: 25, 16: 28}       # by brightness rank
TO_DARK = {20: 9, 21: 12, 25: 13, 28: 16, 29: 16}               # 21 -> 12: the side design's far leg


def leg_flood(allowed, seed):
    lbl, _ = ndimage.label(allowed, structure=np.ones((3, 3)))
    r, c = seed
    if lbl[r, c] == 0:
        ys, xs = np.nonzero(lbl)
        j = np.argmin((ys - r) ** 2 + (xs - c) ** 2)
        r, c = ys[j], xs[j]
    return lbl == lbl[r, c]


def run_legs(name, can):
    """(near leg, far leg) masks of a processed run frame: colour floods from hand-set squares (the hooves and
    outlines stay as they are)."""
    spec = RUN_LEGS[name]
    far = leg_flood(np.isin(can, LEG_DARK), spec["far"])
    r0, c0, c1 = spec["box"]
    box = np.zeros_like(far)
    box[r0:, c0:c1] = True
    near = leg_flood(np.isin(can, LEG_LIGHT) & box & ~far, spec["near"])
    top = np.nonzero(far.any(1))[0].min()
    low = np.zeros_like(far)
    low[top + (SOLE - top) // 2:] = True                 # the far leg's own light tufts by its fetlock
    far |= np.isin(can, LEG_LIGHT) & ndimage.binary_dilation(far, iterations=3) & low & ~near
    return near, far


def swap_shades(name, can):
    near, far = run_legs(name, can)
    out = can.copy()
    for m, cmap in ((near, TO_DARK), (far, TO_LIGHT)):
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            out[y, x] = cmap.get(int(can[y, x]), int(can[y, x]))
    print(name, "legs swapped: near", int(near.sum()), "far", int(far.sum()))
    return out


def to_idx(rgba, pal):
    key = {tuple(int(v) for v in c): i for i, c in enumerate(pal)}
    out = np.full(rgba.shape[:2], -1)
    m = rgba[..., 3] > 0
    out[m] = [key[tuple(int(v) for v in p)] for p in rgba[m][:, :3]]
    return out


def run(a):
    pal = palette()
    os.makedirs(OUT, exist_ok=True)
    for tag, n in TAGS:
        if tag.startswith("wolf") or (a.only and tag != a.only):
            continue
        row = []
        codex_run = {}
        for k in range(1, n + 1):
            name = f"{tag}_{k}"
            can, head, s = cut_frame(name)
            can, head = ground(can, name, head)
            can, bow_at, draw = fix_bow(can, name, head)
            if name not in NO_HEAD:
                can = paste_head(can, head)
                can, n_old = clear_old_head(can, head)
            can = final_clean(can, BOWMASK[0], ZONE[0], head)
            can = close_outline(can, pal)
            print(name, "scale %.2f" % s, "head", head, "bow", bow_at, "draw", draw, "fist", FIST[0])
            if tag == "run":
                codex_run[name] = can
                continue
            rgba = to_rgba(can, pal)
            Image.fromarray(rgba).save(os.path.join(OUT, f"kindred_{name}.png"))
            row.append(rgba)
        if tag == "run":
            for k, (src, swapped) in enumerate(RUN_ORDER, 1):
                can = swap_shades(src, codex_run[src]) if swapped else codex_run[src]
                rgba = to_rgba(can, pal)
                Image.fromarray(rgba).save(os.path.join(OUT, f"kindred_run_{k}.png"))
                row.append(rgba)
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            review_strip(os.path.join(a.review, f"{tag}.png"), row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", metavar="RAW_DIR")
    ap.add_argument("--review")
    ap.add_argument("--only")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    run(a)


if __name__ == "__main__":
    main()
