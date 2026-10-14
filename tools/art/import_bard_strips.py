#!/usr/bin/env python3
"""league_bard's action frames from Codex's step-2 fine drafts (assets/source/bard/codex_strips/bard-strips) on the
design's grid (PPU 1.5: one square = one dense pixel), the way tools/art/design_bard_hd.py made the front.

    python tools/art/import_bard_strips.py [--review DIR] [--only tag]

Codex drew the 38 frames as fine drafts on the pack's canvas (tools/art/pack_bard_strips.py: 1536 x 1024, a design
square 11 px, the soles on y 980, the feet's middle x 640), but each at its own size (its HANDOFF: sizes and places
drift) - the head 0.97x to 1.72x the reference. So per frame:
  * the head found by normalised cross-correlation against the front draft's mask + antenna on the pack's canvas, over
    scales (HEADS: centre and scale, refined at full resolution; tools in the docstring of head_match);
  * the size, one per action (tag_scales): Codex drew the head and the body at sizes that differ from frame to frame
    (the run's heads up to 1.7x, its bodies 0.9x - 1.4x) but each action's frames alike (it drew each with the one
    before attached); per-frame measures pumped the size (a leaning frame came out big), so every action takes the
    geometric mean of its median head scale (the match) and its median body size (head centre to the lowest row
    against the pack's front); the lying death frames their head scale x the standing ones' body / head ratio;
  * the cut: the draft quantised to the design's 32 colours and voted down in blocks of 11 x scale px (clear where half
    or more is, outline where a third of the drawn part is near-black), the head's centre on the design's head centre;
  * placed: the lowest square on the ground row SOLE; the planted actions' feet (the iron pegs in the bottom rows)
    centred on the standing column PIV_C, the run and the death keep the head over the design's;
  * one face (memory one-face-all-frames): the design's own 10 x 10 mask and antenna pasted on the frame's head centre;
  * the outline closed (strips.complete_outline), grown by one square (the design's 2), notches closed, two majority
    passes with the thin parts kept (design_bard_hd.calm's rules).
run = the idle walking (run_frames: the pegs stepping in turn under the body, the body bobbing - Codex's run kept no
leg order); idle = the design breathing (the upper body a square up and back), hit = the design 2 / 1 squares back.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_bard_hd as D  # noqa: E402

ROOT = D.ROOT
SRC = D.SRC
CODEX = os.path.join(SRC, "codex_strips", "bard-strips")
K = D.K
LEG = D.LEG
PX = 11.0                          # pack canvas px a design square at head scale 1 (pack_bard_strips.py PX)
COLS, ROWS = 140, 96               # the frame canvas (design squares)
PIV_C, SOLE = 62, 86               # the standing column (between the feet) and the soles' row
DESIGN_FEET, DESIGN_SOLE = 31, 57  # the design's feet middle column and its soles' row
D_DX, D_DY = PIV_C - DESIGN_FEET, SOLE - DESIGN_SOLE
D_MASK = (37.5 + D_DX, 12.5 + D_DY)          # the design's mask centre on the canvas (col, row)
TAGS = [("run", 8), ("attack", 5), ("skill", 5), ("skill2", 5), ("skill2_e", 4), ("ult", 5), ("dead", 6)]
PLANTED = {"attack", "skill", "skill2", "skill2_e", "ult"}
# head centre (draft px) and scale per frame: normalised cross-correlation of the front draft's mask + antenna
# (pack design/bard_front_on_canvas.png, centre 706.5, 488.5, box -48..48 x -95..42) over scales 0.8-1.85 at half
# resolution, then 0.02 steps at full resolution round the best (attack 1 and skill2 1 started from the brown-disc
# finder: their coarse match fell on the hip bell). 2026-10-14.
HEADS = {
    "attack_1": (734.3, 403.8, 1.12), "attack_2": (718.2, 362.5, 1.18), "attack_3": (688.4, 366.1, 1.08),
    "attack_4": (692.2, 327.4, 1.2), "attack_5": (660.7, 381.6, 1.17),
    "dead_1": (809.4, 456.0, 1.1), "dead_2": (718.7, 348.6, 1.17), "dead_3": (712.5, 340.7, 1.33),
    "dead_4": (858.5, 410.7, 1.33), "dead_5": (881.0, 521.8, 1.3), "dead_6": (878.0, 506.7, 1.32),
    "run_1": (791.7, 508.6, 1.17), "run_2": (872.9, 390.3, 1.4), "run_3": (872.9, 390.3, 1.4),
    "run_4": (925.7, 357.4, 1.56), "run_5": (926.4, 348.5, 1.72), "run_6": (904.6, 305.2, 1.6),
    "run_7": (902.6, 266.1, 1.62), "run_8": (905.6, 276.1, 1.62),
    "skill2_1": (749.9, 490.1, 1.07), "skill2_2": (776.2, 452.5, 1.18), "skill2_3": (795.2, 368.5, 1.18),
    "skill2_4": (754.4, 412.1, 1.08), "skill2_5": (738.9, 380.1, 1.07),
    "skill2_e_1": (730.0, 465.7, 0.97), "skill2_e_2": (698.0, 347.7, 0.97), "skill2_e_3": (702.2, 333.5, 1.18),
    "skill2_e_4": (714.0, 402.3, 1.03),
    "skill_1": (745.4, 412.1, 1.08), "skill_2": (778.8, 451.7, 1.15), "skill_3": (716.4, 444.0, 1.1),
    "skill_4": (703.0, 442.3, 1.03), "skill_5": (719.9, 439.1, 1.07),
    "ult_1": (693.9, 469.2, 1.05), "ult_2": (776.9, 482.1, 1.07), "ult_3": (762.4, 466.1, 1.08),
    "ult_4": (819.3, 432.8, 1.12), "ult_5": (758.9, 457.1, 1.07),
}
IRON = {LEG['A']}                     # the peg feet's colour
REF_HEAD_TO_SOLE = 980 - 488.5        # the pack's front on the canvas: its mask centre to its soles (px)
# frames lying or sitting: no head-to-soles height to measure; their size from the head match times the body / head
# ratio of the standing frames of the same action (dead 1, 2: 0.98)
LYING = {"dead_3", "dead_4", "dead_5", "dead_6"}


def design():
    return np.array(Image.open(D.OUT).convert("RGBA"))


def palette():
    d = design()
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0)


def cut(a, pal, px, head, at):
    """The draft `a` voted down to the canvas in blocks of `px` draft px, the draft's `head` (x, y) on the canvas
    point `at` (col, row) - a block's centre."""
    op = a[..., 3] > 0
    H, W = op.shape
    L = D.lab(pal.astype(float))
    idx = np.full(op.shape, -1)
    flat = D.lab(a[..., :3].astype(float))[op]
    best = np.empty(len(flat), int)
    for i in range(0, len(flat), 200000):
        best[i:i + 200000] = ((flat[i:i + 200000, None] - L[None]) ** 2).sum(-1).argmin(1)
    idx[op] = best
    k0 = int(np.where((pal == K).all(1))[0][0])
    idx[op & (a[..., :3].astype(int).sum(-1) < 90)] = k0
    out = np.full((ROWS, COLS), -1)
    hx, hy = head
    ac, ar = at
    for r in range(ROWS):
        y0 = hy + (r - ar - 0.5) * px
        y1 = y0 + px
        if y1 <= 0 or y0 >= H:
            continue
        ys = slice(max(0, int(np.floor(y0))), min(H, int(np.ceil(y1))))
        for c in range(COLS):
            x0 = hx + (c - ac - 0.5) * px
            x1 = x0 + px
            if x1 <= 0 or x0 >= W:
                continue
            xs = slice(max(0, int(np.floor(x0))), min(W, int(np.ceil(x1))))
            blk = idx[ys, xs].ravel()
            if blk.size == 0 or (blk < 0).sum() * 2 >= blk.size:
                continue
            drawn = blk[blk >= 0]
            if (drawn == k0).sum() >= 0.34 * drawn.size:
                out[r, c] = k0
                continue
            vals, cnt = np.unique(drawn[drawn != k0], return_counts=True)
            out[r, c] = vals[cnt.argmax()]
    img = np.zeros((ROWS, COLS, 4), np.uint8)
    m = out >= 0
    img[m, :3] = pal[out[m]]
    img[m, 3] = 255
    return img


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys = slice(max(0, dy), min(H, H + dy))
    xs = slice(max(0, dx), min(W, W + dx))
    out[ys, xs] = a[max(0, -dy):min(H, H - dy), max(0, -dx):min(W, W - dx)]
    return out


def feet_middle(a):
    """The middle between the outermost iron squares of the bottom 12 rows (a lifted peg counted too), or None."""
    op = a[..., 3] > 0
    rows = np.nonzero(op.any(1))[0]
    if not len(rows):
        return None
    bot = rows.max()
    band = a[max(0, bot - 11):bot + 1]
    iron = np.array([[tuple(int(v) for v in p[:3]) in IRON and p[3] > 0 for p in row] for row in band])
    xs = np.nonzero(iron.any(0))[0]
    return None if len(xs) < 2 else (xs.min() + xs.max()) / 2


def head_template():
    """The design's mask + antenna: (cells mask, colours) round the mask centre (37.5, 12.5)."""
    d = design()
    mask_cols = {LEG['m'], LEG['l'], LEG['O'], LEG['y'], LEG['Y']}
    m = np.zeros(d.shape[:2], bool)
    for r in range(8, 18):
        for c in range(33, 43):
            m[r, c] = d[r, c, 3] > 0 and tuple(int(v) for v in d[r, c, :3]) in mask_cols
    m = ndimage.binary_fill_holes(m)
    ant = np.zeros_like(m)
    for r in range(0, 9):
        for c in range(34, 41):
            ant[r, c] = d[r, c, 3] > 0 and tuple(int(v) for v in d[r, c, :3]) in {LEG['T'], LEG['y'], LEG['O'], LEG['m']}
    core = m | ant
    cells = core | (ndimage.binary_dilation(core, structure=D.CROSS) & (d[..., 3] > 0) &
                    (d[..., :3] == K).all(-1))
    ys, xs = np.nonzero(cells)
    return [(int(y) - 12.5, int(x) - 37.5, d[y, x].copy()) for y, x in zip(ys, xs)]


def paste_head(a, centre, tpl):
    cc, cr = centre
    for dy, dx, px in tpl:
        r, c = int(round(cr + dy)), int(round(cc + dx))
        if 0 <= r < a.shape[0] and 0 <= c < a.shape[1]:
            a[r, c] = px
    return a


def finish(a, keep_boxes=()):
    a, _, _ = D.strips.complete_outline(a, color=K)
    a = D.grow(a)[1:-1, 1:-1]          # grown in place (the canvas has room round the figure)
    for src, dst in (('R', 'M'), ('Y', 'O'), ('g', 'T')):
        m = (a[..., :3] == LEG[src]).all(-1) & (a[..., 3] > 0)
        a[m, :3] = LEG[dst]
    keep = np.zeros(a.shape[:2], bool)
    for r0, r1, c0, c1 in keep_boxes:
        keep[max(0, r0):r1, max(0, c0):c1] = True
    for k in 'DOTyXtq':
        keep |= (a[..., :3] == LEG[k]).all(-1)
    op = a[..., 3] > 0
    for _ in range(2):
        a = D.pd_majority(a, op, keep)
    return close_small(notches(a))


def close_small(a, most=24):
    """Ground showing inside the figure (memory gap-check): enclosed clear pockets of `most` squares or fewer (the air
    between the horn's bells and the arm: the front has it dark) and
    one-square cracks between two drawn squares (left-right or up-down) become outline."""
    while True:
        op = a[..., 3] > 0
        lab, n = ndimage.label(~op)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        fill = np.zeros_like(op)
        for j in range(1, n + 1):
            if j not in border and (lab == j).sum() <= most:
                fill |= lab == j
        p = np.pad(op, 1)
        fill |= ~op & ((p[:-2, 1:-1] & p[2:, 1:-1]) | (p[1:-1, :-2] & p[1:-1, 2:]))
        if not fill.any():
            return a
        a[fill, :3] = K
        a[fill, 3] = 255


def notches(a):
    while True:
        op = a[..., 3] > 0
        p = np.pad(op, 1)
        n = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        m = ~op & (n >= 3)
        if not m.any():
            return a
        a[m, :3] = K
        a[m, 3] = 255


def body_size(a, key):
    """A standing frame's head centre to its lowest row over the pack's front's (None for the lying ones)."""
    if key in LYING:
        return None
    hy = HEADS[key][1]
    rows = np.nonzero((a[..., 3] > 0).any(1))[0]
    return (rows.max() - hy) / REF_HEAD_TO_SOLE


def group(key):
    tag = key.rsplit("_", 1)[0]
    return "dead_down" if key in LYING else ("dead_up" if tag == "dead" else tag)


def tag_scales():
    """One size per action (Codex drew each action's frames with the one before attached, so they agree within an
    action far better than the measures of single frames do): the geometric mean of the action's median head scale
    and median body size; the lying death frames: their head scale x the standing death frames' body / head ratio."""
    heads, bodies = {}, {}
    for key, (_, _, s) in HEADS.items():
        a = np.array(Image.open(os.path.join(CODEX, f"bard_{key}.png")).convert("RGBA"))
        a[a[..., 3] < 128] = 0
        g = group(key)
        heads.setdefault(g, []).append(s)
        b = body_size(a, key)
        if b is not None:
            bodies.setdefault(g, []).append(b)
    out = {}
    for g in heads:
        h = float(np.median(heads[g]))
        out[g] = float(np.sqrt(h * np.median(bodies[g]))) if g in bodies else None
    up = out["dead_up"] / float(np.median(heads["dead_up"]))
    out["dead_down"] = float(np.median(heads["dead_down"])) * up
    return out


def frame(tag, i, pal, tpl, scales):
    key = f"{tag}_{i}"
    hx, hy, _ = HEADS[key]
    a = np.array(Image.open(os.path.join(CODEX, f"bard_{key}.png")).convert("RGBA"))
    a[a[..., 3] < 128] = 0
    s = scales[group(key)]
    can = cut(a, pal, PX * s, (hx, hy), D_MASK)
    rows = np.nonzero((can[..., 3] > 0).any(1))[0]
    dy = SOLE - int(rows.max())
    dx = 0
    if tag in PLANTED:
        fm = feet_middle(can)
        if fm is not None:
            dx = int(round(PIV_C - fm))
    can = shift(can, dx, dy)
    centre = (D_MASK[0] + dx, D_MASK[1] + dy)
    can = paste_head(can, centre, tpl)
    hc, hr = int(round(centre[0])), int(round(centre[1]))
    can = finish(can, [(hr - 15, hr + 7, hc - 6, hc + 7)])
    rows = np.nonzero((can[..., 3] > 0).any(1))[0]          # the grown outline went a row below the soles
    return shift(can, 0, SOLE - int(rows.max())), centre


def on_canvas(dx=0, dy=0):
    d = design()
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[D_DY + dy:D_DY + dy + d.shape[0], D_DX + dx:D_DX + dx + d.shape[1]] = d
    return can


# ------------------------------------------------------------------------------------------------ the run (rigged)
# Codex's run kept no leg order (one peg, then two, the same one ahead) and its sizes grew over the cycle, so the run is
# the idle walking (league_braum's approved walk on the idle, memory run-legs-caitlyn-way: the legs alternate and
# cross): the two iron pegs cut out under the trousers (design rows from PEG_ROW), each stepping in RUN_PHASES - the
# near peg (image left) and the far one half a cycle apart, the lifted one moving forward (+x, he faces right) - drawn
# first, the body over them (the trousers' bottom outline covers the pegs' tops, so a peg never leaves the body); the
# body a square up at mid-swing.
PEG_ROW = 52                                     # design rows from here down are the pegs (the band above stays body)
NEAR_COLS, FAR_COLS = (17, 28), (35, 43)         # design columns of the near and the far peg
PEG_TOP = 50                                     # the pegs' sprites start here (hidden under the band)
#            dx  lift
RUN_PHASES = [(-3, 0), (-2, -2), (0, -3), (2, -2), (3, 0), (2, 0), (0, 0), (-2, 0)]
RUN_BOB = [0, -1, -2, -1, 0, -1, -2, -1]
RUN_MS = 110.0


def run_frames():
    d = design()
    op = d[..., 3] > 0
    body = d.copy()
    sprites = []
    for c0, c1 in (FAR_COLS, NEAR_COLS):            # far first: the near peg is drawn over it
        spr = np.zeros_like(d)
        spr[PEG_TOP:, c0:c1] = d[PEG_TOP:, c0:c1]
        sprites.append(spr)
        body[PEG_ROW:, c0:c1] = 0
        band = body[PEG_TOP:PEG_ROW, c0:c1]
        iron = (band[..., :3] == LEG['A']).all(-1) & (band[..., 3] > 0)
        band[iron] = (*K, 255)                      # the pegs' tops in the band: outline (the peg shows below)
    out = []
    for k in range(8):
        can = np.zeros((ROWS, COLS, 4), np.uint8)
        for j, spr in enumerate(sprites):            # j 0: far (half a cycle on), 1: near
            dx, lift = RUN_PHASES[(k + (4 if j == 0 else 0)) % 8]
            sub = shift(np.pad(spr, ((0, ROWS - spr.shape[0]), (0, COLS - spr.shape[1]), (0, 0))), D_DX + dx, D_DY + lift)
            m = sub[..., 3] > 0
            can[m] = sub[m]
        b = shift(np.pad(body, ((0, ROWS - body.shape[0]), (0, COLS - body.shape[1]), (0, 0))), D_DX, D_DY + RUN_BOB[k])
        m = b[..., 3] > 0
        can[m] = b[m]
        rows = np.nonzero((can[..., 3] > 0).any(1))[0]
        can = shift(can, 0, SOLE - int(rows.max()))
        out.append((notches(can), RUN_MS))
    return out


# ------------------------------------------------------------------------------------------------ the idle (breathing)
# league_galio's breathing (rig_galio.breathe): the upper body - everything above the design's WAIST row but the hip
# bell and the horn's bells hanging at the left (columns < BELLS_C) - a square up and back; the squares it uncovers
# take the colour of the square under them.
WAIST = 36
BELLS_C = 12
BREATH = [(0, 300.0), (0, 200.0), (1, 300.0), (1, 200.0)]


def breathe(can, mask, k):
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
            elif below < can.shape[0] and out[below, x, 3] > 0:
                out[y, x] = out[below, x]
    return out


def idle_frames():
    can = on_canvas()
    op = can[..., 3] > 0
    yy, xx = np.mgrid[0:ROWS, 0:COLS]
    mask = op & (yy < D_DY + WAIST) & (xx >= D_DX + BELLS_C)
    return [(notches(breathe(can, mask, k)), ms) for k, ms in BREATH]


def frames():
    pal = palette()
    tpl = head_template()
    out = {"idle": idle_frames()}
    cells = json.load(open(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "ba_work", "pose_n",
                                        "bard_cells.json"), encoding="utf-8"))["tags"]
    scales = tag_scales()
    print("sizes:", ", ".join(f"{g} {v:.3f}" for g, v in sorted(scales.items())))
    for tag, n in TAGS:
        if tag == "run":
            out[tag] = run_frames()
            continue
        out[tag] = [(frame(tag, i, pal, tpl, scales)[0], float(cells[tag][i - 1]["ms"])) for i in range(1, n + 1)]
    out["hit"] = [(on_canvas(dx=-2), 80.0), (on_canvas(dx=-1), 120.0)]
    return out


def review(acts, path, z=6):
    tiles = []
    for tag, fr in acts.items():
        for k, (a, _) in enumerate(fr):
            tiles.append((f"{tag}_{k + 1}", a))
    W = COLS * z
    H = ROWS * z
    per = 6
    rows = (len(tiles) + per - 1) // per
    big = Image.new("RGBA", (per * W, rows * (H + 14)), (255, 0, 255, 255))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(big)
    for n, (name, a) in enumerate(tiles):
        x, y = (n % per) * W, (n // per) * (H + 14)
        big.alpha_composite(Image.fromarray(a).resize((W, H), Image.NEAREST), (x, y + 14))
        dr.text((x + 4, y + 1), name, fill=(255, 255, 255, 255))
        dr.line([(x, y + 14 + (SOLE + 1) * z), (x + W, y + 14 + (SOLE + 1) * z)], fill=(0, 200, 255, 255))
        dr.line([(x + (PIV_C + 0.5) * z, y + 14 + (SOLE - 2) * z), (x + (PIV_C + 0.5) * z, y + 14 + (SOLE + 3) * z)],
                fill=(0, 200, 255, 255), width=2)
    big.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write a contact sheet of every frame at 6x on magenta here")
    a = ap.parse_args()
    acts = frames()
    out = os.path.join(SRC, "frames")
    os.makedirs(out, exist_ok=True)
    meta = {}
    for tag, fr in acts.items():
        for k, (a_, ms) in enumerate(fr):
            Image.fromarray(a_).save(os.path.join(out, f"{tag}_{k + 1}.png"))
            meta.setdefault(tag, []).append(ms)
    with open(os.path.join(out, "frames.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"canvas": [COLS, ROWS], "standing": [PIV_C, SOLE], "ms": meta}, f, indent=1)
    if a.review:
        review(acts, a.review)
    print("frames:", ", ".join(f"{t} {len(f)}" for t, f in acts.items()))


if __name__ == "__main__":
    main()
