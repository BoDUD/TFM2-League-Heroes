#!/usr/bin/env python3
"""Orianna's step-1 takes (Codex image_gen, 2026-10-16, assets/source/orianna/codex_model) read back on their own grid
and brought to the user's size - bun top to soles BODY game rows at DENS squares a game pixel (「38 行」, PPU 1.5), the
ball BALL squares across (「球稍小一点」) - two ways, for the user to compare:
  cut  whole rows and columns deleted (design_akali.dp_keep: never two neighbours, the cheapest lines first), every
       square left as Codex drew it;
  px   pixel_down.pixelate (each new square the commonest colour under it, outline-first), the size sheet's way.

    python tools/art/design_orianna_cut.py [--review DIR]

Asked for 12-px squares on a 1024 canvas (57 squares tall, the ball 14), Codex gave 1254 px pictures: her takes on
squares of about 8.5 (take 1, Fourier 9.9 across / 7.4 down: uneven) and 10.3 px (take 2), 118 and 99 squares tall; the
balls on about 10.5 and 16 px, 30 and 29 squares across; alpha soft (hard alpha >= 128 here). Each: regrid at SIZE, a
k-means palette (her COLOURS, the ball's BALL_COLOURS), then the two ways. Writes assets/source/orianna/hd/
model<take>{,_cut,_px}.png and ball<take>{,_cut,_px}.png; with --review <dir>/orianna_model_takes.png (every version
8x) and <dir>/orianna_model_lineup.png (at game size next to the pack's mids, Darius and Shen, 4x).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_akali as DA  # noqa: E402
import design_varus as V  # noqa: E402
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "orianna")
CHAMPS = os.path.join(ROOT, "league", "champions")
BODY, DENS = 38, 1.5
ROWS = round(BODY * DENS)          # 57 squares bun top to soles
BALL = 14
SIZE = {"model-1": 8.5, "model-2": 10.3, "ball-1": 10.5, "ball-2": 16.0}
COLOURS, BALL_COLOURS = 36, 16
PEERS = [("lux", 1.0), ("syndra", 1.0), ("katarina", 1.5), ("darius", 1.0), ("shen", 1.0)]
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def read(name, colours):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"orianna-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, SIZE[name])
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    d = crop(d)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, colours)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def weights(d):
    """Dark (outline) squares and the teal eyes / violet panels cost more to delete."""
    rgb = d[..., :3].astype(int)
    w = np.ones(d.shape[:2])
    w[rgb.sum(-1) < 120] = 3.0
    teal = (rgb[..., 1] > 150) & (rgb[..., 2] > 150) & (rgb[..., 0] < 120)
    violet = (rgb[..., 2] > 170) & (rgb[..., 0] > 150) & (rgb[..., 1] < 170)
    w[teal | violet] = 6.0
    w[d[..., 3] == 0] = 0.5
    return w


def teal(d):
    rgb = d[..., :3].astype(int)
    return (d[..., 3] > 0) & (rgb[..., 1] > 140) & (rgb[..., 2] > 140) & (rgb[..., 0] < 130)


def cut(d, k):
    """The eyes' rows and columns are never deleted (they went first: 2-3 teal squares cost little against the
    outline's; take 2's cut lost both eyes)."""
    h, w = d.shape[:2]
    wt = weights(d)
    code = d.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)   # one number a square
    eye = teal(d)
    rows, _ = DA.dp_keep(list(code), list(wt), max(round(h * k), (h + 1) // 2),
                         hard=set(np.nonzero(eye.any(1))[0].tolist()))
    sub = code[rows]
    cols, _ = DA.dp_keep(list(sub.T), list(wt[rows].T), max(round(w * k), (w + 1) // 2),
                         hard=set(np.nonzero(eye[rows].any(0))[0].tolist()))
    return d[rows][:, cols]


# model2's gear emblem at the throat (rows 33-36, columns 28-32) and the clear columns between the hanging hand and the
# skirt (13-15): kept by even_cut (the emblem's ring broke into a dark lump, the hand ran into the skirt)
EMBLEM = (range(33, 37), list(range(28, 33)) + [13, 14, 15])


def even_cut(d, rows, cols, keep=EMBLEM):
    """d brought to rows x cols by deleting whole lines spread evenly over the figure: the lines to go are split into
    equal windows and each window drops its cheapest line (the squares differing from the nearer-looking neighbour,
    weighted), never the eyes' lines nor a line next to one just dropped. dp_keep's global choice (cut()) took most of
    them from the legs - plain rows - and shortened them by a third and clipped the far boot (PPU 2.2, 2026-10-16)."""
    wt = weights(d)
    eye = teal(d)

    def drop(a, w, n_keep, hard):
        n = a.shape[0]
        k = n - n_keep
        code = a.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)

        def cost(j):
            c = []
            for m in (j - 1, j + 1):
                if 0 <= m < n:
                    c.append(float(((code[j] != code[m]) * np.maximum(w[j], w[m])).sum()))
            return min(c) if c else 0.0
        gone = []
        edges = np.linspace(0, n, k + 1)
        for i in range(k):
            lo, hi = int(round(edges[i])), int(round(edges[i + 1]))
            cand = [j for j in range(max(lo, 1), min(hi, n - 1)) if j not in hard and (j - 1) not in gone]
            if not cand:
                cand = [j for j in range(lo, hi) if j not in hard]
            gone.append(min(cand, key=cost))
        return [j for j in range(n) if j not in gone]

    hard_r = set(np.nonzero(eye.any(1))[0].tolist()) | set(keep[0])
    keep_r = drop(d, wt, rows, hard_r)
    sub = d[keep_r]
    hard_c = set(np.nonzero(eye[keep_r].any(0))[0].tolist()) | set(keep[1])
    keep_c = drop(sub.transpose(1, 0, 2), wt[keep_r].T, cols, hard_c)
    return sub[:, keep_c]


def frame0(hero):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    tag = "hd_idle" if "hd_idle" in anims else "idle"
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im.crop(im.getbbox())


def strip(cells, scale_of, top=24, gap=18):
    ims = [(lab, Image.fromarray(a) if isinstance(a, np.ndarray) else a) for lab, a in cells]
    ims = [(lab, im.resize((round(im.width * scale_of(lab)), round(im.height * scale_of(lab))), Image.NEAREST))
           for lab, im in ims]
    W = sum(im.width for _, im in ims) + gap * (len(ims) + 1)
    H = max(im.height for _, im in ims) + top + gap
    can = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for lab, im in ims:
        can.alpha_composite(im, (x, H - gap - im.height))
        dr.text((x, 6), lab, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    out = {}
    for name in SIZE:
        ball = name.startswith("ball")
        d = read(name, BALL_COLOURS if ball else COLOURS)
        k = (BALL / max(d.shape[:2])) if ball else ROWS / d.shape[0]
        c = cut(d, k)
        p, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
        p = crop(p)
        stem = name.replace("-", "")
        for tag, im in (("", d), ("_cut", c), ("_px", p)):
            Image.fromarray(im).save(lp(os.path.join(SRC, "hd", f"{stem}{tag}.png")))
        out[name] = (d, c, p)
        print(f"{name}: read back {d.shape[1]}x{d.shape[0]}, k {k:.3f} -> cut {c.shape[1]}x{c.shape[0]}, "
              f"px {p.shape[1]}x{p.shape[0]}")
    if not a.review:
        return
    cells = []
    for name, (d, c, p) in out.items():
        cells += [(f"{name} cut", c), (f"{name} px", p)]
    os.makedirs(a.review, exist_ok=True)
    strip(cells, lambda lab: 8).convert("RGB").save(os.path.join(a.review, "orianna_model_takes.png"))
    ppu = dict(PEERS)
    lineup = cells + [(h, frame0(h)) for h, _ in PEERS]
    strip(lineup, lambda lab: 4 / DENS if lab.split()[0] in SIZE else 4 / ppu[lab]) \
        .convert("RGB").save(os.path.join(a.review, "orianna_model_lineup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
