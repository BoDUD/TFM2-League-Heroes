#!/usr/bin/env python3
"""Import Mordekaiser's effects (assets/source/mordekaiser/PROMPTS_FX.md, 17 pictures) as the game sheets
league_mordekaiser_fx and league_mordekaiser_big.

    python tools/art/import_mordekaiser.py [--review out.png]

Codex delivered ten overview sheets (assets/source/mordekaiser/codex_fx/mordekaiser_fx_sheet1..10.png: every effect a row
or two of its frames, each at its own scale, soft alpha), no game-size copies - the user pasted them (the PNGs from
Downloads, lossless). Kassadin's importer (tools/art/import_kassadin.py) does the rest the same way:
  * every frame is cut from its own box (BOXES: the sheet, the frame's y band and x range - a pair of mirrored halves is
    one frame), only the pieces whose middle lies in the band (rows touch);
  * one scale per effect (its biggest frame to the prompt's size, SIZE), every game pixel the commonest colour of the
    sheet pixels under it snapped to the prompt's ramps (a brighter one wins: the white cores stay), clear when under
    45% covered;
  * the red side: the line (e_beam: turned with the cast) symmetric top to bottom, everything else left to right - the
    fuller half mirrored onto the other about the frame's own axis, checked square for square;
  * the line laid out from his position: every frame's left edge on the picture's left edge (the grasp leaves his
    hand), the picture as long as the line (LINE_W);
  * the realm vortex (the add-on's banish picture) looped over the realm's 7 s.
Obliterate's pictures (q_slam, q_burst, q_hit, q_iso_hit) are drawn by tools/art/fx_mordekaiser_q.py instead (the user:
「铁男1技能的特效感觉也不足」): Codex's (sheets 1, 3, 4, 5) were small for him, and its crack - a line picture turned
with the cast - floated above the line on the red side.
Spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Times from the kit
(build_mordekaiser.P, 60 ticks a second).
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

SRC = os.path.join(ROOT, "assets", "source", "mordekaiser", "codex_fx")
MOD = os.path.join(ROOT, "league")
SHEETS = {n: f"mordekaiser_fx_sheet{n}.png" for n in range(1, 11)}

# the prompt's ramps (pack_mordekaiser_fx.py)
SOUL = ["#FFFFFF", "#D8FFF8", "#7CFFEE", "#22E0D0", "#0E9C98", "#0A5A5C"]
DARK = ["#5A6478", "#343A48", "#1E2230", "#0E1016"]
IRON = ["#E0E6F0", "#A8B0C0", "#6E7688", "#3E4452"]
DUST = ["#E6DCC8", "#B8AC94", "#8A7E6A", "#5C5446"]
DARKS = {(0x1E, 0x22, 0x30), (0x0E, 0x10, 0x16), (0x34, 0x3A, 0x48)}


def rows(sheet, band, xs):
    return [(sheet, band, x) for x in xs]


# effect -> [(sheet, (y0, y1) band, (x0, x1)) per frame]
BOXES = {
    "p_hit": rows(1, (572, 950), [(110, 455), (558, 979), (1078, 1456)]),
    "p_aura": rows(2, (289, 602), [(21, 613), (651, 1241)]) + rows(2, (693, 998), [(25, 618), (659, 1214)]),
    "a_hit": rows(5, (217, 531), [(106, 224), (274, 584), (605, 939), (977, 1191)]),
    "e_beam": rows(6, (244, 563), [(22, 345), (392, 857), (910, 1319), (1379, 1730), (1786, 2147)]),
    "e_hit": rows(7, (68, 469), [(49, 398), (420, 779), (803, 1141), (1158, 1509)]),
    "w_shield": rows(7, (518, 967), [(31, 246), (261, 500), (505, 762), (771, 1047), (1050, 1297), (1313, 1508)]),
    "w_heal": rows(8, (111, 508), [(37, 268), (326, 615), (651, 877), (940, 1221), (1273, 1493)]),
    "r_mark": rows(8, (569, 935), [(37, 285), (326, 575), (615, 921), (961, 1216), (1267, 1499)]),
    "r_cast": rows(9, (0, 372), [(45, 365), (400, 750), (765, 1110), (1125, 1525)])
    + rows(9, (372, 595), [(245, 620), (650, 975), (1030, 1310)]),
    "r_pull": rows(9, (615, 829), [(96, 410), (480, 731), (804, 1076), (1148, 1422)]),
    "r_curse": rows(9, (866, 1003), [(304, 437), (547, 730), (816, 987), (1100, 1233)]),
    "r_realm": rows(10, (67, 262), [(44, 386), (414, 756), (781, 1128), (1146, 1493)])
    + rows(10, (276, 461), [(47, 385), (413, 754), (781, 1124), (1151, 1488)]),
    "r_win": rows(10, (512, 745), [(293, 556), (639, 897), (981, 1220)])
    + rows(10, (745, 1000), [(293, 556), (639, 897), (981, 1220)]),
}
# the biggest frame's size in game px: ("w" | "h", n) (the small ones a little over the prompt's, Kassadin's way)
SIZE = {"a_hit": ("w", 14), "p_aura": ("w", 50), "p_hit": ("w", 12), "e_beam": ("w", 54), "e_hit": ("w", 16),
        "w_shield": ("h", 40),
        "w_heal": ("h", 32), "r_cast": ("w", 40), "r_mark": ("w", 16), "r_realm": ("w", 46), "r_pull": ("w", 14),
        "r_win": ("h", 34), "r_curse": ("w", 10)}
SYM = {"e_beam": "tb"}                               # every other one "lr"
AXIS = {}
LINE_W = {"e_beam": 54}                              # the line's picture: as long as the line (e_len)
HIT = (0, -14)                  # a hit on the upper body of a 36-44 px unit
OVER = (0, -36)                 # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit or a point


def palette():
    cols = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in SOUL + DARK + IRON + DUST]
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
    crops = [crop(sheets[n], band, xr) for n, band, xr in BOXES[name]]
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


def common_cell(frames, sym, oy_list, s, band, keep_rows=True, bottom=False):
    """Every frame on one cell: lr effects share their axis column and keep their rows as cut (the band's rows
    scaled), tb effects share their axis row."""
    if sym == "lr":
        half = max(f.shape[1] // 2 for f in frames)
        H = max(f.shape[0] for f in frames)
        cell = []
        for f in frames:
            c = np.zeros((H, 2 * half + 1, 4), np.uint8)
            x = half - f.shape[1] // 2
            if bottom:              # a picture standing on the ground: every frame's lowest square on the cell's last row
                ys = np.nonzero(f[..., 3].any(1))[0]
                g = f[:ys.max() + 1] if len(ys) else f
                c[H - g.shape[0]:, x:x + f.shape[1]] = g
            else:
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
            sys.exit(f"mordekaiser_fx_{name} cell {k + 1} is not symmetric left to right")
        if sym == "tb" and not (c == c[::-1]).all():
            sys.exit(f"mordekaiser_fx_{name} cell {k + 1} is not symmetric top to bottom")


def line(frames, width):
    """A line's picture: `width` wide (his position the left edge), every frame's left edge there, the frames' middle
    rows on the picture's middle row (odd height: the top-to-bottom symmetry kept)."""
    H = max(f.shape[0] for f in frames)
    H += 1 - H % 2
    out = []
    for f in frames:
        c = np.zeros((H, width, 4), np.uint8)
        xs = np.nonzero(f[..., 3].any(0))[0]
        g = f[:, xs.min():xs.max() + 1][:, :width]
        y = (H - g.shape[0]) // 2
        c[y:y + g.shape[0], :g.shape[1]] = g
        out.append(c)
    return out


def build_cells(sheets):
    cells = {}
    for name in BOXES:
        frames, s, crops = frames_of(name, sheets)
        sym = SYM.get(name, "lr")
        if name in LINE_W:
            cs = line(frames, LINE_W[name])
        else:
            cs = common_cell(frames, sym, None, s, None, bottom=FX[name][0] != "core")
        cs, _ = trim_rows(cs) if sym == "lr" else (cs, 0)
        if sym == "tb":                      # trim columns shared by every cell, keep the rows symmetric
            any_col = np.zeros(cs[0].shape[1], bool)
            for c in cs:
                any_col |= c[..., 3].any(0)
            xs = np.nonzero(any_col)[0]
            if name not in LINE_W:
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
# effect -> (anchor kind, frames with ms, spots)
FX = {
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Darkness Rise: a pulse every p_per 30 ticks (500 ms), the ring round his feet
    "p_aura": ("ring", seq(range(4), [120, 120, 130, 130]), [SOLES]),
    "p_hit": ("core", seq(range(3), [40, 50, 60]), [HIT]),
    # Q: tools/art/fx_mordekaiser_q.py (main() adds them)
    # E: the grasp along its 18-tick picture line (300 ms) from his hand's height
    "e_beam": ("core", seq(range(5), [50, 60, 60, 60, 70]), [(0, -8)]),
    "e_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # W: the shield rising round him, the heal 2.5 s later
    "w_shield": (("feet", 1), seq(range(6), [60, 80, 100, 120, 100, 80]), [SOLES]),
    "w_heal": (("feet", 0), seq(range(5), [60, 80, 80, 80, 80]), [SOLES]),
    # R
    # the burst round him: its columns rise from the ground (frames 2-7), the first frame's star mid-body
    "r_cast": (("feet", 1), seq(range(7), [40, 50, 60, 60, 60, 70, 70]), [SOLES]),
    "r_mark": ("core", seq(range(5), [50, 60, 60, 70, 80]), [HIT]),
    # the realm's vortex where they stood: the add-on banishes both r_t 420 ticks (7 s) - its 8 frames looped 9 times
    "r_realm": ("ring", seq(list(range(8)) * 9, [100] * 72), [SOLES]),
    "r_pull": ("core", seq(range(4), [50, 60, 60, 70]), [HIT]),
    "r_win": (("feet", 0), seq(range(6), [50, 60, 70, 70, 70, 80]), [SOLES]),
    # the curse over the cursed one's head while it lasts
    "r_curse": ("core", seq(range(4), [100] * 4), [OVER]),
}
BIG = {"p_aura", "q_slam", "q_burst", "e_beam", "r_cast", "r_realm"}


def ring_anchor(cells):
    """A ground ring's middle row: the row of the fullest frame's lower half with the most squares."""
    c = max(cells, key=lambda x: int((x[..., 3] > 0).sum()))
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
    tables = {"league_mordekaiser_fx": {}, "league_mordekaiser_big": {}}
    for name, (kind, frames, spots) in FX.items():
        cs = cells[name]
        anc = ring_anchor(cs) if kind == "ring" else anchor(cs[0], kind)
        out = []
        for k, ms in frames:
            if k == EMPTY:
                out.append((np.zeros((3, 3, 4), np.uint8), ms))
                continue
            out.append((J.place(cs[k], anc, spots), ms))
        tables["league_mordekaiser_big" if name in BIG else "league_mordekaiser_fx"][name] = out
    import fx_mordekaiser_q
    for name, out in fx_mordekaiser_q.frames().items():
        tables["league_mordekaiser_big" if name in BIG else "league_mordekaiser_fx"][name] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
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
