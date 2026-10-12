#!/usr/bin/env python3
"""Import Kassadin's effects (assets/source/kassadin/PROMPTS_FX.md, 12 pictures) as the game sheets league_kassadin_fx
and league_kassadin_big.

    python tools/art/import_kassadin.py [--review out.png]

Codex delivered two overview sheets only (assets/source/kassadin/codex_fx/kassadin_fx_sheet1.webp and sheet2.webp:
every effect a row of its frames, each row at its own scale, lossy WebP), no game-size copies; the user chose
「直接用这两张图」 and 「有问题的地方你修复」「还有别少特效 少的话你补」「然后蓝色红色方技能不要颠倒」. So here:
  * every frame is cut from its box (BOXES: the row's y band, each frame's x range - a pair of mirrored halves is one
    frame), only the pieces whose middle lies in the band (the rows touch);
  * one scale per effect (its biggest frame to the prompt's size, SIZE), every game pixel the commonest colour of the
    sheet pixels under it snapped to the prompt's ramps (a brighter one wins from 35%: the white cores stay), clear when
    under 45% covered;
  * the red side (the client never mirrors an effect picture; a turned picture stands upside down cast leftward): the
    orb and the cone (turned with the cast) made symmetric top to bottom, everything else left to right - the fuller
    half mirrored onto the other about the frame's own axis (found by the best mirror overlap, or AXIS where Codex drew
    one half only: R's arrival frames 5-6), checked square for square;
  * lone dark specks dropped; E's cone laid out as the prompt asks (one picture from him, its left edge, to 42 squares
    ahead, its right edge): Codex drew its six frames as wave groups side by side, each group placed with its front at
    CONE_FRONT.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_kassadin.P, 60 ticks a second).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kassadin", "codex_fx")
MOD = os.path.join(ROOT, "league")
SHEETS = {1: "kassadin_fx_sheet1.webp", 2: "kassadin_fx_sheet2.webp"}

# the prompt's ramps (pack_kassadin_fx.py)
VOID = ["#FFFFFF", "#F0DCFF", "#CC96FF", "#A055FF", "#7426DC", "#4A119A"]
MAG = ["#FFD6F6", "#FF80E2", "#E632C6", "#A8188E"]
DARK = ["#3A1466", "#24093F", "#140426"]
SHELL = ["#E2E6FF", "#AEB8FF", "#7280F4", "#4248C6"]
DARKS = {(0x3A, 0x14, 0x66), (0x24, 0x09, 0x3F), (0x14, 0x04, 0x26), (0x4A, 0x11, 0x9A)}

# effect -> (sheet, (y0, y1) band, [(x0, x1) per frame])
BOXES = {
    "a_hit": (2, (10, 102), [(85, 172), (183, 320), (343, 472), (497, 660)]),
    "w_hit": (2, (102, 212), [(35, 127), (133, 312), (318, 500), (505, 660), (665, 810)]),
    "q_orb": (2, (212, 292), [(68, 224), (246, 427), (448, 619), (648, 797)]),
    "q_hit": (2, (288, 400), [(62, 158), (178, 327), (343, 497), (522, 657), (665, 790)]),
    "q_shield": (2, (402, 512), [(48, 157), (168, 277), (303, 417), (433, 547), (566, 682), (690, 800)]),
    "e_hit": (2, (512, 580), [(68, 170), (195, 412), (418, 627), (638, 797)]),
    "e_slow": (2, (580, 650), [(22, 210), (230, 420), (438, 624), (648, 820)]),
    "q_sil": (2, (652, 722), [(62, 195), (252, 393), (465, 600), (665, 793)]),
    "r_hit": (2, (722, 842), [(42, 188), (212, 442), (448, 623), (642, 810)]),
    "e_cone": (1, (275, 525), [(28, 105), (135, 305), (328, 528), (540, 725), (732, 835), (838, 1065)]),
    "r_out": (1, (615, 975), [(20, 100), (133, 293), (300, 605), (622, 755), (793, 880), (918, 1070)]),
    "r_in": (1, (1080, 1365), [(20, 85), (98, 195), (200, 405), (420, 685), (698, 835), (838, 965), (970, 1068)]),
}
# the biggest frame's size in game px: ("w" | "h", n)
# (the small ones a little over the prompt's sizes: at those the drafts' thin rays and the orb's ring broke up)
SIZE = {"a_hit": ("w", 18), "w_hit": ("w", 26), "q_orb": ("w", 22), "q_hit": ("w", 20), "q_shield": ("h", 42),
        "e_hit": ("w", 20), "e_slow": ("w", 22), "q_sil": ("w", 14), "r_hit": ("w", 20), "e_cone": ("h", 50),
        "r_out": ("h", 40), "r_in": ("w", 46)}
SYM = {"q_orb": "tb", "e_cone": "tb"}                 # every other one "lr"
# where Codex drew one half only: (effect, frame) -> the axis column in the sheet
AXIS = {("r_in", 4): 827, ("r_in", 5): 900}
CONE_W, CONE_FRONT = 43, [14, 30, 41, 42, 42, 42]     # E's picture: 43 wide (odd), each frame's front column
HIT = (0, -12)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -34)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit or a point


def palette():
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in VOID + MAG + DARK + SHELL]
    return np.array(cols, np.uint8)


PAL = palette()
PAL_LAB = srgb2lab(PAL.astype(float))
PAL_LUM = PAL.astype(float) @ np.array([0.3, 0.59, 0.11])
BRIGHT = 200                    # white, lilac, pale pink and pale blue: the cores and the thin rays


def load(n):
    return np.asarray(Image.open(os.path.join(SRC, SHEETS[n])).convert("RGBA")).astype(np.int16)


def crop(sheet, band, xr):
    """The frame's box; pieces of the next rows (their middle outside the band) cleared."""
    y0, y1 = band
    x0, x1 = xr
    pad = 6
    a = sheet[max(0, y0 - pad):y1 + pad, x0:x1].copy()
    from scipy import ndimage
    op = a[..., 3] > 40
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        ys, _ = np.nonzero(lab == i)
        mid = ys.mean() + max(0, y0 - pad)
        if not (y0 <= mid < y1):
            a[lab == i] = 0
    return a, (x0, max(0, y0 - pad))


def snap(rgb):
    """Nearest colour of the prompt's ramps (Lab)."""
    lab = srgb2lab(rgb.reshape(-1, 3).astype(float))
    d = ((lab[:, None] - PAL_LAB[None]) ** 2).sum(-1)
    return d.argmin(1).reshape(rgb.shape[:2])


def shrink(a, s):
    """Every game pixel from the sheet pixels under it, snapped to the prompt's ramps: when a fifth of them or more is
    a bright colour (the white and lilac cores, thin rays included), the brightest colour with a tenth or more;
    otherwise, when 45% or more is covered, the commonest (a brighter one wins from 35%); else clear."""
    H, W = a.shape[:2]
    h, w = max(1, int(round(H * s))), max(1, int(round(W * s)))
    idx = snap(np.clip(a[..., :3], 0, 255))
    alpha = a[..., 3] > 100
    bright = PAL_LUM >= BRIGHT
    out = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        ya, yb = int(j / s), max(int(j / s) + 1, int((j + 1) / s))
        for i in range(w):
            xa, xb = int(i / s), max(int(i / s) + 1, int((i + 1) / s))
            m = alpha[ya:yb, xa:xb]
            if m.size == 0 or not m.any():
                continue
            ids, cnt = np.unique(idx[ya:yb, xa:xb][m], return_counts=True)
            share = cnt / m.size
            lit = share[bright[ids]].sum()
            if lit >= 0.2:
                cand = [(PAL_LUM[ids[k]], ids[k]) for k in range(len(ids)) if bright[ids[k]] and share[k] >= 0.1]
                best = max(cand)[1] if cand else ids[np.argmax(np.where(bright[ids], cnt, -1))]
            elif m.mean() >= 0.45:
                share = cnt / cnt.sum()
                best = ids[cnt.argmax()]
                for k in np.argsort(-PAL_LUM[ids]):
                    if share[k] >= 0.35:
                        if PAL_LUM[ids[k]] > PAL_LUM[best]:
                            best = ids[k]
                        break
            else:
                continue
            out[j, i, :3] = PAL[best]
            out[j, i, 3] = 255
    return out


def best_axis(m, lo, hi):
    """The column (or between two) about which the mask overlaps its mirror the most."""
    best = None
    for c2 in range(2 * lo, 2 * hi + 1):           # the axis at c2 / 2
        c = c2 / 2.0
        ys, xs = np.nonzero(m)
        mx = np.round(2 * c - xs).astype(int)
        ok = (mx >= 0) & (mx < m.shape[1])
        score = m[ys[ok], mx[ok]].sum() - (~ok).sum()
        if best is None or score > best[0]:
            best = (score, c)
    return best[1]


def mirror_lr(a, axis):
    """Symmetric left to right about `axis` (a column or a half): the fuller half kept and mirrored; an odd width with
    the axis on the middle column."""
    m = a[..., 3] > 0
    H, W = m.shape
    if axis != int(axis):                          # between two columns: double the one left of it
        k = int(axis)
        a = np.concatenate([a[:, :k + 1], a[:, k:k + 1], a[:, k + 1:]], 1)
        axis = k + 1
        m = a[..., 3] > 0
        H, W = m.shape
    axis = int(axis)
    half = max(axis, W - 1 - axis)
    out = np.zeros((H, 2 * half + 1, 4), np.uint8)
    left = a[:, max(0, axis - half):axis + 1]
    right = a[:, axis:min(W, axis + half + 1)]
    L = np.zeros((H, half + 1, 4), np.uint8)
    L[:, half + 1 - left.shape[1]:] = left
    Rr = np.zeros((H, half + 1, 4), np.uint8)
    Rr[:, :right.shape[1]] = right
    keep = L if (L[..., 3] > 0).sum() >= (Rr[..., 3] > 0).sum() else Rr[:, ::-1]
    out[:, :half + 1] = keep
    out[:, half:] = keep[:, ::-1]
    return out


def mirror_tb(a, axis):
    return np.ascontiguousarray(np.transpose(mirror_lr(np.ascontiguousarray(np.transpose(a, (1, 0, 2))), axis),
                                             (1, 0, 2)))


def despeckle(a):
    """Lone dark squares (a dark ramp colour with no square of the picture beside it) go."""
    from scipy import ndimage
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    out = a.copy()
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) <= 2 and all(tuple(int(v) for v in a[y, x, :3]) in DARKS for y, x in zip(ys, xs)):
            out[ys, xs] = 0
    return out


def frames_of(name, sheets):
    """The effect's game-size frames, symmetric, on one shared cell (equal sizes, the effect's middle shared)."""
    n, band, boxes = BOXES[name]
    sheet = sheets[n]
    crops = [crop(sheet, band, xr) for xr in boxes]
    # one scale: the biggest frame's content to SIZE
    dim, target = SIZE[name]
    ext = []
    for a, _ in crops:
        ys, xs = np.nonzero(a[..., 3] > 40)
        ext.append((xs.max() - xs.min() + 1) if dim == "w" else (ys.max() - ys.min() + 1))
    s = target / max(ext)
    sym = SYM.get(name, "lr")
    out = []
    # the effect's own middle row (lr effects) or column (tb effects) shared by every frame: from the union of crops
    for k, (a, (ox, oy)) in enumerate(crops):
        g = shrink(a, s)
        m = g[..., 3] > 0
        if not m.any():
            out.append(g)
            continue
        if sym == "lr":
            if (name, k) in AXIS:
                axis = (AXIS[(name, k)] - ox) * s - 0.5
                axis = round(axis * 2) / 2.0
            else:
                xs = np.nonzero(m.any(0))[0]
                axis = best_axis(m, int(xs.min()), int(xs.max()))
            g = mirror_lr(g, axis)
        else:
            ys = np.nonzero(m.any(1))[0]
            axis = best_axis(np.ascontiguousarray(m.T), int(ys.min()), int(ys.max()))
            g = mirror_tb(g, axis)
        out.append(despeckle(g))
    return out, s, crops


def common_cell(frames, sym, oy_list, s, band, keep_rows=True):
    """Every frame on one cell: lr effects share their axis column and keep their rows as cut (the band's rows
    scaled), tb effects share their axis row."""
    if sym == "lr":
        half = max(f.shape[1] // 2 for f in frames)
        H = max(f.shape[0] for f in frames)
        cell = []
        for f in frames:
            c = np.zeros((H, 2 * half + 1, 4), np.uint8)
            x = half - f.shape[1] // 2
            c[:f.shape[0], x:x + f.shape[1]] = f
            cell.append(c)
        return cell
    half = max(f.shape[0] // 2 for f in frames)
    W = max(f.shape[1] for f in frames)
    cell = []
    for f in frames:
        c = np.zeros((2 * half + 1, W, 4), np.uint8)
        y = half - f.shape[0] // 2
        c[y:y + f.shape[0], :f.shape[1]] = f
        cell.append(c)
    return cell


def trim_rows(cells):
    """Clear rows top and bottom shared by every cell go."""
    any_row = np.zeros(cells[0].shape[0], bool)
    for c in cells:
        any_row |= c[..., 3].any(1)
    ys = np.nonzero(any_row)[0]
    return [c[ys.min():ys.max() + 1] for c in cells], int(ys.min())


def check(name, cells, sym):
    for k, c in enumerate(cells):
        if sym == "lr" and not (c == c[:, ::-1]).all():
            sys.exit(f"kassadin_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym == "tb" and not (c == c[::-1]).all():
            sys.exit(f"kassadin_fx_{name} cell {k + 1} is not symmetric top to bottom")


def cone(frames):
    """E's picture: CONE_W wide (his position the left edge, 42 squares ahead the right edge), every wave group with
    its front at CONE_FRONT[k], the groups' middle rows on the picture's middle row."""
    H = max(f.shape[0] for f in frames)
    H += 1 - H % 2
    out = []
    for f, front in zip(frames, CONE_FRONT):
        c = np.zeros((H, CONE_W, 4), np.uint8)
        xs = np.nonzero(f[..., 3].any(0))[0]
        g = f[:, xs.min():xs.max() + 1]
        x1 = front + 1
        x0 = x1 - g.shape[1]
        sx0 = max(0, -x0)
        y = (H - g.shape[0]) // 2
        c[y:y + g.shape[0], max(0, x0):x1] = g[:, sx0:]
        out.append(c)
    return out


def build_cells(sheets):
    cells = {}
    for name in BOXES:
        frames, s, crops = frames_of(name, sheets)
        sym = SYM.get(name, "lr")
        if name == "e_cone":
            cs = cone(frames)
        else:
            cs = common_cell(frames, sym, None, s, BOXES[name][1])
        cs, _ = trim_rows(cs) if sym == "lr" else (cs, 0)
        if sym == "tb":                      # trim columns shared by every cell, keep the rows symmetric
            any_col = np.zeros(cs[0].shape[1], bool)
            for c in cs:
                any_col |= c[..., 3].any(0)
            xs = np.nonzero(any_col)[0]
            if name != "e_cone":
                cs = [c[:, xs.min():xs.max() + 1] for c in cs]
            any_row = np.zeros(cs[0].shape[0], bool)
            for c in cs:
                any_row |= c[..., 3].any(1)
            ys = np.nonzero(any_row)[0]
            top = min(ys.min(), cs[0].shape[0] - 1 - ys.max())
            cs = [c[top:c.shape[0] - top] for c in cs]
        check(name, cs, sym)
        cells[name] = cs
    return cells


def anchor(cell, kind):
    h, w = cell.shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1 - kind[1]]


EMPTY = J.EMPTY
seq = J.seq
flight = J.flight
# effect -> (anchor kind, frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "w_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # the orb: Q flies q_range 50000 at q_speed 3000 a tick, ~17 ticks (283 ms)
    "q_orb": ("core", flight(4, 60, 400), [(0, 0)]),
    "q_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    # the shield on him for q_sh_t 90 ticks (1.5 s): it appears, holds, cracks
    "q_shield": (("feet", 0), seq(range(6), [60, 300, 300, 400, 300, 140]), [SOLES]),
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # the cone's picture over its zone's 20 ticks (333 ms)
    "e_cone": ("core", seq(range(6), [50, 50, 55, 55, 60, 63]), [(0, 0)]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # buffs (looped while they last): the slow 60 ticks, the silence 60
    "e_slow": ("core", seq(range(4), [100] * 4), [SOLES]),
    "q_sil": ("core", seq(range(4), [100] * 4), [OVER]),
    # R: where he left (the rift standing on the ground) and where he lands (the ring on the ground)
    "r_out": (("feet", 2), seq(range(6), [40, 50, 60, 60, 60, 70]), [SOLES]),
    "r_in": ("ring", seq(range(7), [40, 50, 60, 60, 70, 80, 90]), [SOLES]),
}
BIG = {"e_cone", "r_out", "r_in"}


def ring_anchor(cells):
    """R's arrival: the ground ring's middle row - the row of frame 4 (the widest ring) with the most squares."""
    c = cells[3]
    rows = (c[..., 3] > 0).sum(1)
    low = np.arange(len(rows)) >= len(rows) * 0.5
    y = int(np.argmax(np.where(low, rows, -1)))
    return [(c.shape[1] - 1) / 2, y]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    sheets = {n: load(n) for n in SHEETS}
    cells = build_cells(sheets)
    tables = {"league_kassadin_fx": {}, "league_kassadin_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        anc = ring_anchor(cs) if kind == "ring" else anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_kassadin_big" if name in BIG else "league_kassadin_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        Z = 6
        rows = []
        for name, cs in cells.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append((name, img))
        W = max(r.width for _, r in rows) + 120
        Ht = sum(r.height + 10 for _, r in rows)
        sheet = Image.new("RGB", (W, Ht), (20, 20, 26))
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        y = 0
        for name, r in rows:
            sheet.paste(r.convert("RGB"), (120, y))
            d.text((4, y + 4), name, fill=(255, 255, 255))
            y += r.height + 10
        sheet.save(a.review)
        print("review", a.review, sheet.size)


if __name__ == "__main__":
    main()
