#!/usr/bin/env python3
"""league_milio's action frames from Codex's step-2 drafts on the dense design's grid (one square = one design square:
the boy 95 squares from his hair top to his soles, ORIG_PPU = 95 / 32 a game pixel).

    python tools/art/import_milio_strips.py --prepare <delivery>/raw      (once: the drafts -> codex_strips/)
    python tools/art/import_milio_strips.py [--review DIR] [--only TAG]

league_kindred's way (tools/art/import_kindred_strips.py), without the bow:
  * prepare: every draft pixel with alpha >= ALPHA snapped to the design's 40 colours (Lab), kept as an indexed PNG
    cropped to the figure (codex_strips/<name>.png, crops.json: its place on the pack's 1536 x 1024 canvas);
  * the head: the design's head (hd/head.png - the front's hair, face and neck, the one every frame gets) matched in
    the draft by a masked colour SSD over scales (head_match) -> the draft's px per design square and the head's place;
  * the size: one per action (the median head scale of its frames, HEADS overriding a poor match);
  * the cut: the draft voted down in blocks of that size (each square the commonest colour; clear where half or more
    is clear; the outline where 40 % or more of it is), the pack's standing point on the frame canvas's;
  * one face (memory one-face-all-frames): the design's head pasted where it matches best, Codex's own hair / face
    left round it cleared (clear_old_head);
  * placed: the soles of the planted frames on the ground row SOLE, their middle on PIV (the run: by the head);
  * cleaned: loose pieces, pinholes and the outline (strips.complete_outline).
The fire spirit's flicker loop (spirit_float) is read the same way against hd/front_spirit.png (spirit_frames).
Writes assets/source/milio/frames/<tag>_<n>.png (COLS x ROWS, RGBA) and frames.json (the canvas's standing column
and ground row, per frame the head's top-left and scale, the spirit frames' size).
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

SRC = os.path.join(ROOT, "assets", "source", "milio")
CODEX = os.path.join(SRC, "codex_strips")
OUT = os.path.join(SRC, "frames")
ALPHA = 160
CANVAS = (1024, 1536)             # the drafts' canvas (rows, cols)
PACK_PX = 6                       # tools/art/pack_milio_strips.py: px a design square in the pack
PACK_PIV = ((120 + 0.5) * PACK_PX, (160 + 1) * PACK_PX)   # its standing point (x) and ground line (y) in draft px
TAGS = [("run", 8), ("attack", 5), ("skill", 6), ("skill2", 5), ("ult", 6), ("dead", 6), ("spirit_float", 4)]

COLS, ROWS = 230, 175             # the frame canvas (design squares)
PIV, SOLE = 105, 150              # the standing column and the soles' row on it
GREY_LAB = np.array([200.0, 0.0, 0.0])   # clear draft pixels in the match: far from every colour


def design(name):
    return np.asarray(Image.open(os.path.join(SRC, "hd", name)).convert("RGBA")).copy()


def palette():
    """The design's colours (hd/front.png holds every one of the side's too), sorted by brightness."""
    cols = []
    for n in ("front.png", "side.png"):
        a = design(n)
        cols.append(a[a[..., 3] > 0][:, :3])
    pal = np.unique(np.concatenate(cols), axis=0)
    return pal[np.argsort(pal.astype(int).sum(1), kind="stable")]


PAL = palette()
KEY = {tuple(int(v) for v in c): i for i, c in enumerate(PAL)}
OUTLINE = 0                       # the darkest colour: the near-black outline
LAB = dv.srgb2lab(PAL.astype(float))


def snap(rgb):
    lab = dv.srgb2lab(rgb.astype(float))
    out = np.empty(len(lab), int)
    for i in range(0, len(lab), 100000):
        out[i:i + 100000] = ((lab[i:i + 100000, None] - LAB[None]) ** 2).sum(-1).argmin(1)
    return out


def to_idx(rgba):
    out = np.full(rgba.shape[:2], -1)
    m = rgba[..., 3] > 0
    out[m] = [KEY[tuple(int(v) for v in p)] for p in rgba[m][:, :3]]
    return out


def to_rgba(can):
    out = np.zeros(can.shape + (4,), np.uint8)
    m = can >= 0
    out[m, :3] = PAL[can[m]]
    out[m, 3] = 255
    return out


def hue_class():
    """Each palette colour's kind: hair (the dark indigos and blue-violets: blue over both red and green), skin (the
    face's oranges and browns), dark (the outline), other (the clothes, the spirit). Measured on hd/head.png: hair
    3 6 10 11 23, skin 25 29 33 34 (the teal collar and the gold and cream are clothes)."""
    rgb = PAL.astype(int)
    kind = np.array(["other"] * len(PAL), object)
    dark = rgb.sum(1) < 75
    hair = (rgb[:, 2] > rgb[:, 0] + 8) & (rgb[:, 2] > rgb[:, 1] + 8) & (rgb[:, 0] >= 15) & ~dark
    skin = (rgb[:, 0] > 170) & (rgb[:, 1] > 80) & (rgb[:, 1] < 137) & (rgb[:, 2] < 60) & (rgb[:, 0] - rgb[:, 1] > 60)
    kind[dark] = "dark"
    kind[hair] = "hair"
    kind[skin] = "skin"
    return kind


# ------------------------------------------------------------------------------------------------- the drafts
def prepare(raw):
    os.makedirs(CODEX, exist_ok=True)
    crops = {}
    flat = [0, 0, 0] + [int(v) for c in PAL for v in c]
    for tag, n in TAGS:
        for k in range(1, n + 1):
            name = f"milio_{tag}_{k}"
            a = np.asarray(Image.open(os.path.join(raw, name + ".png")).convert("RGBA"))
            if a.shape[:2] != CANVAS:
                sys.exit(f"{name}: {a.shape[1]}x{a.shape[0]}, not the pack's 1536x1024")
            op = a[..., 3] >= ALPHA
            ys, xs = np.nonzero(op)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            idx = np.zeros(op.shape, np.uint8)
            idx[op] = snap(a[op][:, :3]) + 1
            im = Image.fromarray(idx[y0:y1, x0:x1], "P")
            im.putpalette(flat + [0] * (768 - len(flat)))
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


# ------------------------------------------------------------------------------------------------- the head match
def lab_image(idx):
    out = np.empty(idx.shape + (3,))
    out[idx < 0] = GREY_LAB
    out[idx >= 0] = LAB[idx[idx >= 0]]
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
    h, w = t.shape[:2]
    return np.asarray(Image.fromarray(t).resize((max(1, round(w * s)), max(1, round(h * s))), Image.NEAREST))


def match(idx, tpl, scales):
    """(score, s, x, y): the template's top-left corner at (x, y) draft px, s draft px a square."""
    I = lab_image(idx)
    I2 = I[::2, ::2]
    best = None
    for s in scales:
        t = scaled(tpl, s / 2)
        if t.shape[0] >= I2.shape[0] or t.shape[1] >= I2.shape[1]:
            continue
        e = masked_ssd(I2, dv.srgb2lab(t[..., :3].astype(float)), t[..., 3] > 0)
        j = np.unravel_index(np.argmin(e), e.shape)
        if best is None or e[j] < best[0]:
            best = (e[j], s, j[1] * 2, j[0] * 2)
    _, s0, x0, y0 = best
    for s in (np.arange(s0 - 0.12, s0 + 0.121, 0.03) if len(scales) > 1 else [s0]):
        t = scaled(tpl, s)
        ya, xa = max(0, y0 - 12), max(0, x0 - 12)
        sub = I[ya:y0 + t.shape[0] + 12, xa:x0 + t.shape[1] + 12]
        if sub.shape[0] < t.shape[0] or sub.shape[1] < t.shape[1]:
            continue
        e = masked_ssd(sub, dv.srgb2lab(t[..., :3].astype(float)), t[..., 3] > 0)
        j = np.unravel_index(np.argmin(e), e.shape)
        if e[j] <= best[0]:
            best = (e[j], s, xa + j[1], ya + j[0])
    return best


HEAD = design("head.png")
SCALES = np.arange(4.6, 9.01, 0.1)
# per frame overrides of the head match: (draft px a square, top-left x, y in draft px) - filled after a review of the
# matches (match_all prints them)
HEADS = {}
BAD = set()                       # frames whose match is poor: the action's median scale, the head by hand / none
# off the ground: the height Codex drew them over its own ground line (the action's planted frames' lowest draft row:
# Codex drifts its ground line between frames, so planted frames go on SOLE whatever it drew) - Q's hop and kick
# (skill_2-4: 18-23 squares, about 7 game px) and R's jump (ult_2, ult_3: 15 and 10 squares)
AIR = {"skill_2", "skill_3", "skill_4", "ult_2", "ult_3"}
NO_HEAD = set()                   # lying / face down: Codex's own head kept
# the actions' last frames, back to standing: the side design itself (Codex's redraws of the stance drift a square
# here and there - its own derived set used the design there too)
RETURN = {"attack_5", "skill_6", "skill2_5", "ult_6"}


def side_on_canvas():
    """hd/side.png on the frame canvas: its feet's middle on PIV, its soles on SOLE; (canvas, the head's top-left)."""
    import json as _j
    info = _j.load(open(os.path.join(SRC, "hd", "design.json"), encoding="utf-8"))
    side = to_idx(design("side.png"))
    h, w = side.shape
    x0 = int(round(PIV - info["side"]["standing_col"]))
    y0 = SOLE - (h - 1)
    can = np.full((ROWS, COLS), -1)
    can[y0:y0 + h, x0:x0 + w] = side
    hy, hx = info["head"]["side_at"]
    return can, (y0 + hy, x0 + hx)


CLOTH = [2, 7, 9, 12, 15, 16, 17, 22, 24, 28, 13, 19]   # the tunic's reds, the kilt's magentas, the sash's teals
SANDAL = [5, 8, 14, 21, 30]       # the sandals' browns (the side design's both feet: rows 80 down)
CLOTH_PER_HAIR = 1.15             # Codex's frames: the clothes' scale over the hair's (median of the 36)
SANDAL_PER_HAIR = 1.27            # ... the sandals' (Codex draws them bigger than the design)


def frame_scale(idx):
    """Draft px a design square. Codex drew the frames at sizes from 5.8 to 8.5 px a square (within an action too), and
    its redrawn heads match the template poorly at any scale (masked SSD errors 1400-2450, scales all over 4.5-7.9).
    Three areas measure it - the hair's (the head: hidden where hands cover it, ult_2 / ult_3; small where Codex drew
    the head small, skill_5), the clothes' (smaller where the kilt folds in a crouch) and the sandals' (bigger in some
    poses) - each brought to the hair's by its median ratio; the median of the three is the scale (2026-10-15: ult_2 and
    ult_3 cut at the hair's alone came out a size too big, skill_5 too)."""
    side = to_idx(design("side.png"))
    hair = float(np.sqrt(np.isin(idx, HAIR).sum() / np.isin(to_idx(HEAD), HAIR).sum()))
    cloth = float(np.sqrt(np.isin(idx, CLOTH).sum() / np.isin(side, CLOTH).sum())) / CLOTH_PER_HAIR
    feet = np.isin(side, SANDAL)
    feet[:80] = False
    sandal = float(np.sqrt(np.isin(idx, SANDAL).sum() / feet.sum())) / SANDAL_PER_HAIR
    return float(np.median([hair, cloth, sandal]))


def head_tpl_face():
    """The template's hair and face (no collar, no outline): what the match compares."""
    t = HEAD.copy()
    i = to_idx(t)
    t[~np.isin(i, HAIR + SKIN)] = 0
    return t


def match_all(only=None):
    out = {}
    tpl = head_tpl_face()
    for tag, n in TAGS:
        if tag.startswith("spirit") or (only and tag != only):
            continue
        for k in range(1, n + 1):
            name = f"{tag}_{k}"
            idx = load_draft("milio_" + name)
            s = frame_scale(idx)
            e, s, x, y = match(idx, tpl, [s])
            # the template's box (the face-only template keeps HEAD's box: same top-left)
            out[name] = (round(float(s), 3), int(x), int(y), round(float(e), 1))
            print(f'    "{name}": ({s:.2f}, {x}, {y}),   # err {e:.1f}')
    return out


# ------------------------------------------------------------------------------------------------- the cut
def block_vote(idx, s, x, y, hr, hc):
    """The draft voted down to the canvas in blocks of s draft px; the block of square (hr, hc) starts at draft (x, y).
    Each square: clear where half or more is clear; the outline where 40 % or more of the drawn part is; else the
    commonest colour."""
    H, W = idx.shape
    cols = np.floor((np.arange(W) - x) / s).astype(int) + hc
    rows = np.floor((np.arange(H) - y) / s).astype(int) + hr
    ok_c = (cols >= 0) & (cols < COLS)
    ok_r = (rows >= 0) & (rows < ROWS)
    sub = idx[np.ix_(ok_r, ok_c)]
    rr = np.repeat(rows[ok_r][:, None], ok_c.sum(), 1)
    cc = np.repeat(cols[ok_c][None, :], ok_r.sum(), 0)
    sq = (rr * COLS + cc).ravel()
    npal = len(PAL) + 1
    k = sub.ravel() + 1
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


def action_scale(tag, heads):
    good = [v[0] for k, v in heads.items() if k.rsplit("_", 1)[0] == tag and k not in BAD]
    return float(np.median(good))


def cut_frame(name, heads):
    """(canvas of palette indices, the head template's top-left (row, col) on it, scale)."""
    s0, x, y = heads[name][:3]
    s = action_scale(name.rsplit("_", 1)[0], heads) if name in BAD else s0
    # the head's top-left in draft px kept; its box centred when the action's scale differs from the frame's match
    x += HEAD.shape[1] * (s0 - s) / 2
    y += HEAD.shape[0] * (s0 - s) / 2
    hc = int(round(PIV + (x - PACK_PIV[0]) / s))
    hr = int(round(SOLE + 1 + (y - PACK_PIV[1]) / s))
    can = block_vote(load_draft("milio_" + name), s, x, y, hr, hc)
    return can, (hr, hc), s


SOLES_KIND = None


def feet_cols(can):
    """The columns of the sandals: brown squares in the frame's lowest 8 rows."""
    op = can >= 0
    ys, _ = np.nonzero(op)
    low = np.zeros_like(op)
    low[ys.max() - 7:ys.max() + 1] = True
    return np.nonzero((low & op & ~np.isin(can, [OUTLINE])).any(0))[0]


RUN_HEAD_COL = None               # the run: every frame's head left column here (set from run_1 unless given)


def draft_bottom(name):
    d = load_draft("milio_" + name)
    return int(np.nonzero((d >= 0).any(1))[0].max())


def ground(can, name, head, s, place=None):
    """Lowest drawn square on SOLE, the feet's middle on PIV (the run: the head on RUN_COL). An airborne frame (AIR)
    keeps its height over the ground - (the action's planted frames' median lowest draft row - its own) / s squares -
    and the action's mean horizontal shift (`place`: (that ground row in draft px, the planted frames' mean dc))."""
    hr, hc = head
    op = can >= 0
    ys, xs = np.nonzero(op)
    if name in AIR:
        g_draft, dc_mean = place
        lift = int(round((g_draft - draft_bottom(name)) / s))
        dr = SOLE - lift - ys.max()
        dc = int(round(dc_mean))
    else:
        dr = SOLE - ys.max()
        dc = 0
        if name.startswith("run"):
            dc = (RUN_COL[0] - hc) if RUN_COL[0] is not None else 0
        elif not name.startswith("dead"):
            fx = feet_cols(can)
            if len(fx):
                dc = int(round(PIV - (fx.min() + fx.max()) / 2.0))
    return shift(can, dr, dc), (hr + dr, hc + dc), dc


RUN_COL = [None]


# ------------------------------------------------------------------------------------------------- one face
def head_mask_at(head):
    m = np.zeros((ROWS, COLS), bool)
    hr, hc = head
    ys, xs = np.nonzero(HEAD[..., 3] > 0)
    ok = (ys + hr >= 0) & (ys + hr < ROWS) & (xs + hc >= 0) & (xs + hc < COLS)
    m[ys[ok] + hr, xs[ok] + hc] = True
    return m


def arms_near_head(can, head):
    """Codex's arms that pass by or over the head: its skin pieces (4-joined) of ARM_MIN squares or more with at least
    ARM_OUT of them outside the template (grown a square) - a raised fist, a palm beside the face - plus the outline
    squares round them. Its face slivers beside the template are smaller or lie inside it."""
    hb = ndimage.binary_dilation(head_mask_at(head))
    skin = np.isin(can, SKIN)
    lbl, n = ndimage.label(skin)
    arms = np.zeros_like(skin)
    for j in range(1, n + 1):
        m = lbl == j
        size = int(m.sum())
        if size >= ARM_MIN and (m & ~hb).sum() >= ARM_OUT * size:
            arms |= m
    ring = ndimage.binary_dilation(arms, structure=np.ones((3, 3))) & np.isin(can, [OUTLINE, 1])
    return arms | ring


ARM_MIN = 20
ARM_OUT = 0.35


def paste_head(can, head, arms=None):
    """The design's head over the frame; where Codex's arm passes over its hair or outline (`arms`), the arm stays in
    front (its face - skin, eyes, mouth - is never covered)."""
    out = can.copy()
    hr, hc = head
    ys, xs = np.nonzero(HEAD[..., 3] > 0)
    for y, x in zip(ys, xs):
        r, c = hr + y, hc + x
        if not (0 <= r < ROWS and 0 <= c < COLS):
            continue
        v = KEY[tuple(int(v) for v in HEAD[y, x, :3])]
        if arms is not None and arms[r, c] and (v in HAIR or v in (OUTLINE, 1)):
            continue
        out[r, c] = v
    return out


KIND = hue_class()
HAIR = [i for i, k in enumerate(KIND) if k == "hair"]
SKIN = [i for i, k in enumerate(KIND) if k == "skin"]


def clear_old_head(can, head, reach=8, arms=None):
    """Codex's own head round the pasted one: its hair pieces (8-joined) outside the template within `reach` of it, and
    its face slivers - skin pieces of at most SLIVER squares touching the template - never an arm (`arms`); then the
    outline squares left with nothing drawn but outline within two squares. Cleared; the outline closed afterwards."""
    hb = head_mask_at(head)
    ring = ndimage.binary_dilation(hb, iterations=reach) & ~hb
    near = ndimage.binary_dilation(hb, structure=np.ones((3, 3)))
    keep = arms if arms is not None else np.zeros_like(hb)
    rm = np.zeros_like(hb)
    hair = (can >= 0) & np.isin(can, HAIR) & ~hb & ~keep
    lbl, n = ndimage.label(hair, structure=np.ones((3, 3)))
    for j in range(1, n + 1):
        piece = lbl == j
        if (piece & ring).sum() >= 0.8 * piece.sum():
            rm |= piece
    skin = (can >= 0) & np.isin(can, SKIN) & ~hb & ~keep
    lbl, n = ndimage.label(skin, structure=np.ones((3, 3)))
    for j in range(1, n + 1):
        piece = lbl == j
        if piece.sum() <= SLIVER and (piece & near).any():
            rm |= piece
    out = can.copy()
    out[rm] = -1
    # Codex's own head outline left round the pasted one: dark squares outside the template, within `reach` of it, with
    # no square of the body (anything drawn but the template and the outline) within two - they closed slits of ground
    # against the pasted hair (run_3, skill_2, dead_6 had them)
    drawn = out >= 0
    dark = drawn & np.isin(out, [OUTLINE, 1])
    body = drawn & ~dark & ~hb
    lone = dark & ring & ~ndimage.binary_dilation(body, structure=np.ones((5, 5)))
    out[lone] = -1
    return out, int(rm.sum() + lone.sum())


SLIVER = 12


# ------------------------------------------------------------------------------------------------- the clean-up
HOLE_FILL = 40                    # enclosed holes up to this many squares are filled (memory gap-check: at 2.2 squares a
                                  # game pixel they read as specks of ground): pinholes up to 4 with the colour round
                                  # them, the rest with the outline - bigger ones (a palm held beside the face, a bent arm
                                  # off the body) are real gaps and stay


def final_clean(can, min_piece=30, most_hole=4):
    out = can.copy()
    op = out >= 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < min_piece:
                out[lbl == k] = -1
    op = out >= 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > HOLE_FILL:
            continue
        if m.sum() > most_hole:
            # the gap in the shade of what closes it (a fist against the tunic: the tunic's darkest red) - black read
            # as a hole of its own at game size
            ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op & ~np.isin(out, [OUTLINE, 1])
            cols = np.unique(out[ring])
            out[m] = cols[np.argmin(PAL[cols].astype(int).sum(1))] if len(cols) else OUTLINE
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        vals, cnt = np.unique(out[ring], return_counts=True)
        out[m] = vals[cnt.argmax()]
    return out


def close_outline(can):
    import strips as G
    rgba = G.complete_outline(to_rgba(can), color=tuple(int(v) for v in PAL[OUTLINE]))[0]
    return to_idx(rgba)


def review_strip(path, row, z=4):
    from PIL import ImageDraw
    ys, xs = np.nonzero(np.any([r[..., 3] > 0 for r in row], 0))
    y0, y1 = max(0, ys.min() - 2), min(ROWS, max(ys.max(), SOLE) + 3)
    x0, x1 = max(0, xs.min() - 2), min(COLS, xs.max() + 3)
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


# ------------------------------------------------------------------------------------------------- the run's legs
# Codex drew the near (light) leg in front in all eight run frames - a bound, not League's run, whose legs take turns
# (league_kindred's drafts did the same). Its frames differ in how high the back foot is: run_8 both feet down (the
# contact), run_5 the back foot just off the ground, run_2 half way up, run_4 kicked up high under the body. So the loop
# plays them in that order twice, the second time with the two legs' shades swapped in place (shapes and places
# untouched: the forward leg drawn in the far leg's darker skin, the back one in the near leg's light skin) - each leg
# goes contact, push, lift, kick, then forward again (league_kindred's RUN_ORDER way, accepted 2026-10-14).
RUN_ORDER = [("run_8", False), ("run_5", False), ("run_2", False), ("run_4", False),
             ("run_8", True), ("run_5", True), ("run_2", True), ("run_4", True)]
LEG_SKIN = [20, 25, 29, 33, 34]                    # the legs' skin, dark to light
TO_FAR = {34: 29, 33: 29, 29: 25, 25: 20}          # the near (light) leg drawn as the far one
TO_NEAR = {29: 33, 25: 29, 20: 25}                 # the far (dark) leg drawn as the near one
# the column between the back leg and the front one, read off each frame at 8x (2026-10-15; a gap search in the bottom
# rows missed run_2, whose back foot is off the ground)
RUN_SPLIT = {"run_8": 114, "run_5": 110, "run_2": 112, "run_4": 112}
LEG_REACH = 30                     # a leg's skin piece reaches within this many rows of the frame's lowest row (the
                                   # fists, at the chest and the hips, never do)


def swap_legs(name, can):
    """The two legs' skin swapped: the legs' skin pieces (8-joined, under the face, reaching down near the feet) left of
    RUN_SPLIT (the back leg) lightened, right of it (the front leg) darkened. Whole pieces, so a thigh reaching across
    the split keeps one shade; the fists and arms are never touched."""
    split = RUN_SPLIT[name]
    skin = np.isin(can, LEG_SKIN)
    skin[:100] = False
    low = int(np.nonzero((can >= 0).any(1))[0].max())
    lbl, n = ndimage.label(skin, structure=np.ones((3, 3)))
    out = can.copy()
    nb = nf = 0
    for j in range(1, n + 1):
        m = lbl == j
        ys, xs = np.nonzero(m)
        if m.sum() < 4 or ys.max() < low - LEG_REACH:
            continue
        back = xs.mean() < split
        cmap = TO_NEAR if back else TO_FAR
        for y, x in zip(ys, xs):
            out[y, x] = cmap.get(int(can[y, x]), int(can[y, x]))
        if back:
            nb += int(m.sum())
        else:
            nf += int(m.sum())
    print(f"{name} swapped: split col {split}, back leg {nb} squares lightened, front leg {nf} darkened")
    return out


# ------------------------------------------------------------------------------------------------- the spirit
SPIRIT = design("front_spirit.png")


def spirit_frames():
    """The spirit's loop, cut at its own matched scale, cropped (its float in rows kept as drawn: 'lift')."""
    ys, xs = np.nonzero(SPIRIT[..., 3] > 0)
    tpl = SPIRIT[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = []
    for k in range(1, 5):
        idx = load_draft(f"milio_spirit_float_{k}")
        e, s, x, y = match(idx, tpl, np.arange(4.0, 9.01, 0.1))
        H, W = idx.shape
        rows = int(np.ceil((H - y) / s)) + 4
        cols = int(np.ceil((W - x) / s)) + 4
        global ROWS, COLS
        R0, C0 = ROWS, COLS
        ROWS, COLS = rows + 10, cols + 10
        can = block_vote(idx, s, x, y, 10, 10)
        ROWS, COLS = R0, C0
        can = final_clean(can, min_piece=6)
        can = close_outline(can)
        out.append((can, (float(s), int(x), int(y), float(e))))
        print(f"spirit_float_{k}: scale {s:.2f} at ({x}, {y}) err {e:.1f}")
    return out


# ------------------------------------------------------------------------------------------------- run
def run(a):
    heads = json.load(open(os.path.join(CODEX, "heads.json"), encoding="utf-8"))
    heads = {k: tuple(v) for k, v in heads.items()}
    heads.update(HEADS)
    os.makedirs(OUT, exist_ok=True)
    meta_path = os.path.join(OUT, "frames.json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.isfile(meta_path) else {}
    meta.update({"standing": [PIV, SOLE], "canvas": [COLS, ROWS], "orig_ppu": 95 / 32})
    meta.setdefault("heads", {})
    for tag, n in TAGS:
        if a.only and tag != a.only:
            continue
        if tag.startswith("spirit"):
            sp = spirit_frames()
            for k, (can, info) in enumerate(sp, 1):
                ys, xs = np.nonzero(can >= 0)
                Image.fromarray(to_rgba(can[ys.min():ys.max() + 1, xs.min():xs.max() + 1])).save(
                    os.path.join(OUT, f"{tag}_{k}.png"))
                meta.setdefault("spirit", {})[f"{tag}_{k}"] = {"match": info, "top": int(ys.min()), "left": int(xs.min())}
            continue
        row = []
        cuts = {}
        for k in range(1, n + 1):
            name = f"{tag}_{k}"
            can, head, s = cut_frame(name, heads)
            if tag == "run" and k == 1 and RUN_COL[0] is None:
                RUN_COL[0] = head[1]
            cuts[name] = (can, head, s)
        planted = [nm for nm in cuts if nm not in AIR]
        dcs = {}
        for name in planted:
            can, head, s = cuts[name]
            can, head, dcs[name] = ground(can, name, head, s)
            cuts[name] = (can, head, s)
        place = (float(np.median([draft_bottom(nm) for nm in planted])),
                 float(np.mean(list(dcs.values()))) if dcs else 0.0)
        for name in cuts:
            if name in AIR:
                can, head, s = cuts[name]
                can, head, _ = ground(can, name, head, s, place)
                cuts[name] = (can, head, s)
        finished = {}
        for k in range(1, n + 1):
            name = f"{tag}_{k}"
            can, head, s = cuts[name]
            n_old = 0
            if name in RETURN:
                can, head = side_on_canvas()
                finished[name] = can
                meta["heads"][name] = {"at": [int(head[0]), int(head[1])], "scale": None, "pasted": True,
                                       "design": "side"}
                print(f"{name}: the side design")
                continue
            if name not in NO_HEAD:
                arms = arms_near_head(can, head)
                can, n_old = clear_old_head(can, head, arms=arms)
                can = paste_head(can, head, arms)
            can = final_clean(can)
            can = close_outline(can)
            can = final_clean(can)            # the closed outline can enclose a square or two
            finished[name] = can
            meta["heads"][name] = {"at": [int(head[0]), int(head[1])], "scale": round(s, 3),
                                   "pasted": name not in NO_HEAD}
            print(f"{name}: scale {s:.2f}, head at {head}, old head squares cleared {n_old}")
        if tag == "run":
            order = []
            for k, (src, swapped) in enumerate(RUN_ORDER, 1):
                can = swap_legs(src, finished[src]) if swapped else finished[src]
                order.append((f"run_{k}", can, src, swapped))
            meta["run_order"] = [[src, swapped] for _, _, src, swapped in order]
            out = [(nm, can) for nm, can, _, _ in order]
        else:
            out = list(finished.items())
        for name, can in out:
            rgba = to_rgba(can)
            Image.fromarray(rgba).save(os.path.join(OUT, f"{name}.png"))
            row.append(rgba)
        if a.review and row:
            os.makedirs(a.review, exist_ok=True)
            review_strip(os.path.join(a.review, f"{tag}.png"), row)
    with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", metavar="RAW_DIR")
    ap.add_argument("--match", action="store_true", help="match the head in every draft, write codex_strips/heads.json")
    ap.add_argument("--review")
    ap.add_argument("--only")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    if a.match:
        m = match_all(a.only)
        path = os.path.join(CODEX, "heads.json")
        old = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else {}
        old.update(m)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(old, f, indent=1)
        return
    run(a)


if __name__ == "__main__":
    main()
