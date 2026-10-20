#!/usr/bin/env python3
"""Zyra's step-1 designs (assets/source/zyra/codex_model, 2026-10-20, Codex new-chat-5) read back on their own grids and
brought to the game's count: 74 rows from her hair top to her soles (43.5 game px at PPU 1.7).

    python tools/art/design_zyra_model.py --options DIR     # the candidates side by side
    python tools/art/design_zyra_model.py                   # writes assets/source/zyra/hd/{idle,side}.png

Codex's squares (regrid's guesses; asked 16 px): A-1 16 px (74 rows), A-2 14.5 px (77), SA-1 12 px (95), SA-2 12 px (94;
its two whips cross in front of her). Each read back with regrid at its own size (alpha >= 128); then, the
design-tryndamere way: its own K colours (design_varus.kmeans), whole rows then columns dropped to the count
(design_riven.keep_axis: least loss, never the eyes' rows / columns), the width in proportion, strips.complete_outline
with the face kept. The written pair shares one palette (K colours by k-means over both read-backs together).
The user (2026-10-20): 「动作帧不是你自己做吗 ... 做出来」 - the picks and the rig are mine. First cut to 66 rows (PPU 1.5)
with the faces redrawn square by square (FACE, redraw_face - kept, unused): the user, 「提高点ppu像素吧 如果太糊的话」「脸部
完全变形了啊」 - so PPU 1.7: A-1's own 74 rows as drawn, SA-1 cut 95 -> 74 with its whole head's rows and columns kept, both
with Codex's own faces.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zyra", "codex_model", "zyra-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "zyra", "hd")
ROWS, K = 74, 30
PICKS = {"idle": "A-1", "side": "SA-1"}
# name -> (Codex's square px, rows wanted, eye rows, eye columns) on its own read-back
DRAFTS = {
    "A-1": (16.0, ROWS, range(16, 25), range(36, 47)),     # 74 rows as drawn: nothing cut
    "A-2": (14.5, ROWS, range(18, 26), range(40, 51)),
    "SA-1": (12.0, ROWS, range(8, 32), range(28, 47)),     # the head kept whole: horns, hair round the face, face, chin
    "SA-2": (12.0, ROWS, range(18, 26), range(34, 45)),
}


# The faces redrawn square by square (codex-face-half-squares: the read-backs' eyes were one-square amber / orange specks
# at different heights): skin over the face box, both eyes 2 x 2 under a dark lid line (League's narrowed glowing eyes),
# the upper row bright amber with a pale glint at the near side, the lower row deep orange; a 2-square dark lip.
INK, SKIN, SKIN2 = (4, 1, 3), (251, 222, 174), (222, 170, 132)
AMBER, GLINT, AMBER2, LIP = (249, 176, 12), (255, 238, 140), (214, 96, 8), (96, 1, 36)
FACE = {  # part -> (rows, cols of the skin box, far eye column, near eye column, lid row, mouth (row, first column))
    "idle": (range(15, 22), range(33, 40), 33, 37, 15, (20, 35)),
    "side": (range(14, 21), range(22, 29), 22, 26, 14, (19, 25)),
}


def redraw_face(fig, part):
    """FACE[part] (rows / columns of the written design) painted over the figure."""
    rr, cc, far, near, lid, (my, mx) = FACE[part]
    out = fig.copy()
    for y in rr:
        # the chin tapers: the last two rows lose the far cheek's column(s) and the near edge's (hair shows there)
        lo = cc.start + max(0, y - (rr.stop - 3))
        hi = cc.stop - (1 if y == rr.stop - 1 else 0)
        for x in range(lo, hi):
            out[y, x] = (*(SKIN2 if y == rr.stop - 1 else SKIN), 255)
        if y >= rr.stop - 2:
            out[y, lo - 1] = (*INK, 255)
    # the read-back's own amber / orange eye specks just outside the box go to skin
    for y in range(lid, lid + 3):
        for x in (cc.start - 1, cc.stop, cc.stop + 1):
            r, g, b_, a_ = (int(v) for v in out[y, x])
            if a_ and r > 170 and 60 < g < 235 and b_ < 120:
                out[y, x] = (*SKIN, 255)
    for ex in (far, near):
        out[lid, ex], out[lid, ex + 1] = (*INK, 255), (*INK, 255)
        out[lid + 1, ex], out[lid + 1, ex + 1] = (*AMBER, 255), (*GLINT, 255)
        out[lid + 2, ex], out[lid + 2, ex + 1] = (*AMBER2, 255), (*AMBER2, 255)
    out[my, mx], out[my, mx + 1] = (*LIP, 255), (*LIP, 255)
    return out


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read_back(name):
    size = DRAFTS[name][0]
    raw, _, _ = regrid(np.asarray(Image.open(lp(os.path.join(SRC, f"zyra-model-{name}-raw.png"))).convert("RGBA")), size)
    ys, xs = np.nonzero(raw[..., 3] >= 128)
    raw = raw[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    return raw


def recolour(raw):
    idx, pal = dv.kmeans(raw, K)
    idx = np.where(raw[..., 3] > 0, idx, -1)
    return idx, pal


def paint(idx, pal):
    fig = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    fig[m, :3] = pal[idx[m]]
    fig[m, 3] = 255
    return fig


def keep_axis(lines, target, protect):
    """design_riven.keep_axis, also when the protected run touches an end (an empty part loses nothing)."""
    n = len(lines)
    lo, hi = min(protect), max(protect) + 1
    parts = [list(range(0, lo)), list(range(hi, n))]
    drop = n - target
    q0 = round(drop * len(parts[0]) / max(1, len(parts[0]) + len(parts[1])))
    kept = []
    for part, q in zip(parts, (q0, drop - q0)):
        if not part or q <= 0:
            kept.append(part)
            continue
        sub = [lines[i] for i in part]
        best = None
        for off in range(3):
            k, lost = R.pick(sub, len(part) - q, off)
            if k is not None and (best is None or lost < best[1]):
                best = (k, lost)
        kept.append([part[i] for i in best[0]])
    return kept[0] + list(range(lo, hi)) + kept[1]


def joint(names):
    """{name: (colour index map, shared palette)} with K colours over all the read-backs together."""
    raws = [read_back(n) for n in names]
    h = max(r.shape[0] for r in raws)
    both = np.zeros((h, sum(r.shape[1] for r in raws), 4), np.uint8)
    x = 0
    for r in raws:
        both[:r.shape[0], x:x + r.shape[1]] = r
        x += r.shape[1]
    idx, pal = recolour(both)
    out, x = {}, 0
    for n, r in zip(names, raws):
        out[n] = (np.where(r[..., 3] > 0, idx[:r.shape[0], x:x + r.shape[1]], -1), pal)
        x += r.shape[1]
    return out


def cut(name, coloured=None):
    """The draft at the count: (picture, rows kept, columns kept)."""
    _, rows_to, fr, fc = DRAFTS[name]
    idx, pal = coloured if coloured is not None else recolour(read_back(name))
    H, W = idx.shape
    if rows_to is None or rows_to >= H:
        return paint(idx, pal), list(range(H)), list(range(W))
    protect_r = fr if fr is not None else range(H // 2, H // 2 + 1)
    protect_c = fc if fc is not None else range(W // 2, W // 2 + 1)
    rows = [0] + [r + 1 for r in keep_axis([idx[y] for y in range(1, H)], rows_to - 1,
                                             range(protect_r.start - 1, protect_r.stop - 1))]
    sub = idx[rows]
    cols = keep_axis([sub[:, x] for x in range(W)], round(W * rows_to / H), protect_c)
    fig = paint(idx[np.ix_(rows, cols)], pal)
    keep = np.zeros(fig.shape[:2], bool)
    if fr is not None:
        r_in = [rows.index(r) for r in fr if r in rows]
        c_in = [cols.index(c) for c in fc if c in cols]
        keep[min(r_in):max(r_in) + 1, min(c_in):max(c_in) + 1] = True
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1], rows, cols


def voted(name):
    raw = read_back(name)
    idx, pal = recolour(raw)
    fig = paint(idx, pal)
    k = DRAFTS[name][1] / fig.shape[0]
    g, _ = PD.pixelate(fig, k, (fig.shape[1] / 2, fig.shape[0]), PD.edge_colour(fig))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def sheet(cells, path, k=6, game=3):
    """Each candidate at k x (one square = k px) and below it as the game draws it (1/1.5 game px a square, game x)."""
    ims = []
    for label, a in cells:
        big = Image.fromarray(np.repeat(np.repeat(a, k, 0), k, 1))
        s = game / 1.5
        small = Image.fromarray(a).resize((round(a.shape[1] * s), round(a.shape[0] * s)), Image.NEAREST)
        ims.append((f"{label}  {a.shape[1]}x{a.shape[0]}", big, small))
    gap = 24
    W = sum(max(b.width, s.width) for _, b, s in ims) + gap * (len(ims) + 1)
    H = max(b.height for _, b, _ in ims) + max(s.height for _, _, s in ims) + 80
    can = Image.new("RGBA", (W, H), (196, 200, 190, 255))
    dr = ImageDraw.Draw(can)
    x = gap
    hb = max(b.height for _, b, _ in ims)
    for label, b, s in ims:
        dr.text((x, 6), label, fill=(20, 20, 20, 255))
        can.alpha_composite(b, (x, 24 + hb - b.height))
        can.alpha_composite(s, (x, H - 12 - s.height))
        x += max(b.width, s.width) + gap
    can.convert("RGB").save(lp(path))
    print(path, can.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--options", help="write the candidates sheet into this folder")
    a = ap.parse_args()
    if a.options:
        os.makedirs(lp(a.options), exist_ok=True)
        cells = [(n, cut(n)[0]) for n in DRAFTS]
        sheet(cells, os.path.join(a.options, "zyra_model_options.png"))
        for n in DRAFTS:
            r = read_back(n)
            Image.fromarray(r).save(lp(os.path.join(a.options, f"raw_{n}.png")))
            print(n, "read back", r.shape[1], "x", r.shape[0])
        for n, c in cells:
            Image.fromarray(c).save(lp(os.path.join(a.options, f"opt_{n.replace(' ', '_')}.png")))
        return
    os.makedirs(lp(OUT), exist_ok=True)
    col = joint(list(PICKS.values()))
    for part, name in PICKS.items():
        fig, rows, cols = cut(name, col[name])
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{part}.png")))
        Image.fromarray(np.repeat(np.repeat(fig, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{part}_4x.png")))
        print(part, name, fig.shape[1], "x", fig.shape[0], "rows kept", len(rows), "of", max(rows) + 1)


if __name__ == "__main__":
    main()
