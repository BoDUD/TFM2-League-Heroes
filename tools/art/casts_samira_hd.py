#!/usr/bin/env python3
"""Samira's actions from Codex's whole-frame redraw (assets/source/samira/hd/casts: tools/art/pack_samira_actions.py's
pack, delivered 2026-10-25; the raw generations stay in Codex's outputs folder new-chat-6/outputs/samira-actions/raw),
read onto the design's squares:

1. read back: Codex scaled every frame by its own figure (its head's top and soles on y 904) onto the design's colours,
   so the squares are no one grid; each cell is read on 5.5-px squares from its standing point (the cell's middle) and
   the soles' line, every square the colour most of its pixels have (read). Her standing frames come out 102-105 rows
   tall (the design 105), her face 16-19 squares wide;
2. two frames Codex got wrong take a frame of the same delivery in their place (SUBST): Flair (sword)'s wind-up raised
   the sword in her NEAR hand (the user's rule: a weapon stays in one hand) and the whirl's raised frame drew her a
   size smaller - both take the sword attack's wind-up (attack_m_2, the far hand's sword raised high);
3. placed on the design's grid: the standing point (the old pivot) on the column the design's shoes put it on (PIV),
   the soles on the design's soles' row; the run with her face in one column (Codex wandered a frame 12 squares off).
   Frames that repeat an earlier pose (frame-index.json `same_as`) take its result.

    python tools/art/casts_samira_hd.py --review DIR      # every tag placed, at 2x
"""
import argparse
import json
import os
import colorsys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "samira", "hd")
SRC = os.path.join(HD, "casts")
P = 5.5                         # px a design square in the templates
GROUND_PX = 904                 # the templates' soles' line
TAGS = ["run", "attack", "attack_m", "skill", "skill_m", "skill2", "ult", "hit", "dead"]
SUBST = {"skill_m_2": "attack_m_2", "skill2_10": "attack_m_2"}
STANDING = ["attack_1", "skill_1", "attack_m_8", "skill_m_8", "hit_1", "skill2_16"]   # her shoes as the design's


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def design():
    return np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))


def index():
    with open(lp(os.path.join(SRC, "frame-index.json")), encoding="utf-8") as f:
        return json.load(f)


def read(a, x0, cw):
    """The cell [x0, x0 + cw) on 5.5-px squares -> (squares, the standing point's column, the soles' row + 1)."""
    cx = x0 + cw / 2.0
    nl, nr = int((cx - x0) // P), int((x0 + cw - cx) // P)
    nt, nb = int(GROUND_PX // P), int((a.shape[0] - GROUND_PX) // P)
    out = np.zeros((nt + nb, nl + nr, 4), np.uint8)
    for j in range(nt + nb):
        ya, yb = int(round(GROUND_PX - (nt - j) * P)), int(round(GROUND_PX - (nt - j - 1) * P))
        for i in range(nl + nr):
            xa, xb = int(round(cx - (nl - i) * P)), int(round(cx - (nl - i - 1) * P))
            blk = a[ya:yb, xa:xb].reshape(-1, 4)
            on = blk[blk[:, 3] > 0]
            if len(on) * 2 < len(blk):
                continue
            cols, n = np.unique(on[:, :3], axis=0, return_counts=True)
            out[j, i, :3] = cols[n.argmax()]
            out[j, i, 3] = 255
    return out, nl, nt


def read_all():
    """{"<tag>_<frame>": (squares, standing column, soles row + 1)} for every frame Codex drew once."""
    sheets, out = {}, {}
    for tag, fr in index().items():
        for k, f in fr.items():
            if f.get("same_as"):
                continue
            if f["sheet"] not in sheets:
                sheets[f["sheet"]] = np.asarray(Image.open(lp(os.path.join(SRC, f["sheet"]))).convert("RGBA"))
            out[f"{tag}_{k}"] = read(sheets[f["sheet"]], f["cell"] * f["cell_width"], f["cell_width"])
    for n, src in SUBST.items():
        out[n] = out[src]
    return out


def shoes_mid(d, low=None):
    """The middle of her two shoes: the outer edges of what stands in the 3 rows over her lowest."""
    op = d[..., 3] > 0
    low = int(np.nonzero(op.any(1))[0].max()) if low is None else low
    xs = np.nonzero(op[low - 3:low + 1].any(0))[0]
    return (xs.min() + xs.max() + 1) / 2.0


def skin(p):
    h, s, v = colorsys.rgb_to_hsv(*(p / 255.0))
    return 5 <= h * 360 <= 40 and 0.25 <= s <= 0.75 and v >= 0.5


def face_x(d):
    """The middle column of her face: the largest piece of skin in her top 40 rows."""
    op = d[..., 3] > 0
    top = np.nonzero(op.any(1))[0].min()
    sk = np.zeros(op.shape, bool)
    ys, xs = np.nonzero(op[top:top + 40])
    for y, x in zip(ys + top, xs):
        sk[y, x] = skin(d[y, x, :3].astype(float))
    lbl, n = ndimage.label(sk, structure=np.ones((3, 3)))
    k = int(np.argmax(ndimage.sum(sk, lbl, range(1, n + 1)))) + 1
    xs = np.nonzero(lbl == k)[1]
    return (xs.min() + xs.max() + 1) / 2.0


def pinholes(a, most=3):
    """Gaps of up to `most` squares walled in on every side (the read's: a square whose pixels were half clear) filled
    with the colour most of their neighbours have."""
    op = a[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = a.copy()
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > most:
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m & op
        cols, cnt = np.unique(a[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    return out


D0 = design()
GROUND = int(np.nonzero(D0[..., 3].any(1))[0].max()) + 1       # the row under the design's soles


def placed():
    """{"<tag>_<frame>": (picture, x, y of its top-left on the design's grid)} for every frame."""
    raw = read_all()
    off = np.median([shoes_mid(raw[n][0]) - raw[n][1] for n in STANDING])
    piv = shoes_mid(D0) - off                       # the design's column under the frames' standing point
    run = sorted(n for n in raw if n.rsplit("_", 1)[0] == "run")
    fx = {n: face_x(raw[n][0]) - raw[n][1] for n in run}
    mean = float(np.mean(list(fx.values())))
    done = {}
    for n, (sq, nl, nt) in raw.items():
        ys, xs = np.nonzero(sq[..., 3] > 0)
        pic = pinholes(sq[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
        dx = int(round(mean - fx[n])) if n in fx else 0
        done[n] = (pic, int(round(xs.min() - nl + piv)) + dx, int(ys.min() - nt + GROUND))
    out = {}
    for tag, fr in index().items():
        for k, f in fr.items():
            out[f"{tag}_{k}"] = done[f"{tag}_{f['same_as']}"] if f.get("same_as") else done[f"{tag}_{k}"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fr = placed()
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    import pickle
    with open(os.path.join(a.review, "frames.pkl"), "wb") as f:
        pickle.dump(fr, f)
    for t in TAGS:
        names = sorted([n for n in fr if n.rsplit("_", 1)[0] == t], key=lambda n: int(n.rsplit("_", 1)[1]))
        x0 = min(min(fr[n][1] for n in names), 0) - 2
        x1 = max(max(fr[n][1] + fr[n][0].shape[1] for n in names), D0.shape[1]) + 2
        y0 = min(min(fr[n][2] for n in names), 0) - 2
        y1 = GROUND + 2
        Z, W, Hh = 2, x1 - x0, y1 - y0
        tiles = [("design", (D0, 0, 0))] + [(n, fr[n]) for n in names]
        can = Image.new("RGB", (len(tiles) * (W * Z + 4), Hh * Z), (40, 40, 40))
        for i, (n, (pic, x, y)) in enumerate(tiles):
            tile = Image.new("RGBA", (W, Hh), (150, 165, 150, 255))
            tile.alpha_composite(Image.fromarray(pic), (x - x0, y - y0))
            can.paste(tile.convert("RGB").resize((W * Z, Hh * Z), Image.NEAREST), (i * (W * Z + 4), 0))
        can.save(os.path.join(a.review, f"placed_{t}.png"))
    print("written", a.review)


if __name__ == "__main__":
    main()
