#!/usr/bin/env python3
"""Gnar's 11 key poses from Codex (assets/source/gnar/POSE_PROMPTS.md; delivered 2026-10-20 as gnar_poses_done.zip) read
back on the designs' own squares, in their colours, with their heads.

    python tools/art/read_gnar_poses.py [--src DIR] [--review DIR]

The pictures are 1254 x 1254 with soft alpha and no exact grid, and Codex scaled some whole compositions to keep the
fists and tusks on the canvas (its HANDOFF.md says so), so the squares are measured from the head: the approved head
(pack_gnar_poses.FORMS: Mega's side head 30 x 36 squares, Mini's 40 x 27) is matched against each picture brought down
at every square size SIZES[form] and grid phase (skimage's normalised cross-correlation on the three colour channels);
the best size and phase sample the picture into squares (a square drawn where most of it is, its colour the commonest
of its drawn pixels), every colour snapped to the design's own (Lab), and the matched place gets the design's head
square for square (one face in all frames). Mega's bodies came out bigger than the head asks: each is read again
at the size that gives it the side design's amount of body (its drawn squares outside the head), the head kept on
Codex's head's middle. Writes assets/source/gnar/poses/<name>.png (design squares, the figure's
box) and pose_fit.json (size, phase, where the head sat, the match score).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from skimage.feature import match_template

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_gnar_hd import lp  # noqa: E402
from design_varus import srgb2lab  # noqa: E402
import pack_gnar_poses as PP  # noqa: E402

SRC = "C:/t/gn_work/poses_in_172358/gnar-poses"
OUT = os.path.join(ROOT, "assets", "source", "gnar", "poses")
POSES = {"m_crouch": "mega", "m_swing": "mega", "m_rear": "mega", "m_slam": "mega", "m_lunge": "mega", "m_leap": "mega",
         "m_lift": "mega", "a_windup": "mini", "a_throw": "mini", "a_hop": "mini", "a_crouch": "mini"}
SIZES = {"mega": np.arange(6.0, 14.01, 0.25), "mini": np.arange(12.0, 26.01, 0.5)}
BACK = 7                         # Mega's head box columns that are mane (rig_gnar NECK_BAND 84 - box 78 + 1)
# colours a pose may need that its design lacks: the boulder Mega lifts (the effects' rock ramp, pack_gnar_fx.ROCK)
EXTRA = {"m_lift": [(0xEC, 0xEA, 0xE4), (0xC4, 0xC0, 0xB6), (0x96, 0x92, 0x8A), (0x6C, 0x68, 0x62), (0x46, 0x42, 0x3E),
                    (0x26, 0x24, 0x22)]}


def design(form):
    f = PP.FORMS[form]
    d = np.asarray(Image.open(lp(os.path.join(PP.SRC, "hd", f["design"]))).convert("RGBA"))
    r0, r1, c0, c1 = f["head"]
    return d, d[r0:r1, c0:c1]


def down(img, s, ox, oy):
    """The picture sampled at s px a square from (ox, oy): (rgb of each square's commonest drawn colour - the mean of
    its drawn pixels here, the snap comes after -, drawn fraction)."""
    a = img.astype(float)
    H, W = a.shape[:2]
    ny, nx = int((H - oy) // s), int((W - ox) // s)
    ys = (oy + np.arange(ny + 1) * s).round().astype(int)
    xs = (ox + np.arange(nx + 1) * s).round().astype(int)
    al = (a[..., 3] >= 128).astype(float)
    rgb = a[..., :3] * al[..., None]
    # summed-area tables
    S = np.pad(np.cumsum(np.cumsum(al, 0), 1), ((1, 0), (1, 0)))
    C = np.pad(np.cumsum(np.cumsum(rgb, 0), 1), ((1, 0), (1, 0), (0, 0)))
    y0, y1 = ys[:-1], ys[1:]
    x0, x1 = xs[:-1], xs[1:]
    area = (y1 - y0)[:, None] * (x1 - x0)[None, :]
    cnt = S[y1][:, x1] - S[y0][:, x1] - S[y1][:, x0] + S[y0][:, x0]
    col = C[y1][:, x1] - C[y0][:, x1] - C[y1][:, x0] + C[y0][:, x0]
    mean = col / np.maximum(cnt, 1)[..., None]
    return mean, cnt / area


def score_head(img, head, s, ox, oy):
    mean, frac = down(img, s, ox, oy)
    hm = head[..., :3].astype(float)
    hop = head[..., 3] > 0
    if mean.shape[0] < head.shape[0] or mean.shape[1] < head.shape[1]:
        return -1, None
    tot = 0
    for ch in range(3):
        t = np.where(hop, hm[..., ch], 0)
        im = np.where(frac > 0.5, mean[..., ch], 0)
        tot = tot + match_template(im, t)
    tot /= 3
    k = np.unravel_index(np.argmax(tot), tot.shape)
    return float(tot[k]), (int(k[0]), int(k[1]))


def fit(img, head, sizes):
    best = (-2, None, None)
    for s in sizes:
        for ph in (0.0, 1 / 3, 2 / 3):
            sc, at = score_head(img, head, s, ph * s, ph * s)
            if sc > best[0]:
                best = (sc, (float(s), ph * s, ph * s), at)
    # finer phases at the best size
    sc0, (s, _, _), _ = best
    for px in np.linspace(0, s, 6, endpoint=False):
        for py in np.linspace(0, s, 6, endpoint=False):
            sc, at = score_head(img, head, s, px, py)
            if sc > best[0]:
                best = (sc, (s, float(px), float(py)), at)
    return best


def snap(mean, op, d, extra=()):
    """Every drawn square's colour to the nearest of the design's own (Lab), and of `extra`."""
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    if len(extra):
        pal = np.concatenate([pal, np.asarray(extra, np.uint8)])
    lab_p = srgb2lab(pal.reshape(1, -1, 3).astype(np.uint8)).reshape(-1, 3)
    out = np.zeros(mean.shape[:2] + (4,), np.uint8)
    px = mean[op].clip(0, 255).astype(np.uint8)
    lab = srgb2lab(px.reshape(1, -1, 3)).reshape(-1, 3)
    idx = ((lab[:, None] - lab_p[None]) ** 2).sum(-1).argmin(1)
    out[op, :3] = pal[idx]
    out[op, 3] = 255
    return out


def head_mask(form):
    """The head's own squares inside its box (rig_gnar's parts: Mega's side head without the mane and body fur the box
    takes in on its left - pasted whole, its straight edge stood as a seam on the new body)."""
    import rig_gnar as RG
    C = RG.Canvas()
    f = C.mega if form == "mega" else C.mini
    r0, r1, c0, c1 = PP.FORMS[form]["head"]
    d, head = design(form)
    m = f.masks["head"][r0:r1, c0:c1] if "head" in f.masks else np.ones(head.shape[:2], bool)
    return m & (head[..., 3] > 0)


def body_area(fig, head_box, extra=()):
    """Drawn squares outside the head's box (and not in the extra colours: the boulder)."""
    op = fig[..., 3] > 0
    y0, y1, x0, x1 = head_box
    op[max(0, y0):y1, max(0, x0):x1] = False
    for c in extra:
        op &= ~(fig[..., :3] == np.asarray(c, np.uint8)).all(-1)
    return int(op.sum())


def read(name, form, src):
    img = np.asarray(Image.open(lp(os.path.join(src, f"gnar-pose-{name}.png"))).convert("RGBA"))
    d, head = design(form)
    hh, hw = head.shape[:2]
    extra = EXTRA.get(name, ())
    sc, (s, ox, oy), (hy, hx) = fit(img, head, SIZES[form])
    mean, frac = down(img, s, ox, oy)
    fig = snap(mean, frac > 0.5, d, extra)
    cy, cx = oy + (hy + hh / 2) * s, ox + (hx + hw / 2) * s       # the head's middle in the picture's px
    s2 = s
    if form == "mega":
        # Codex drew Mega's bodies bigger than its head asks (a body 1.2-1.5 times the side design's next to the same
        # head): each pose brought to the side design's amount of body, the design's head over Codex's smaller one
        r0, r1, c0, c1 = PP.FORMS[form]["head"]
        a_d = body_area(d, (r0, r1, c0, c1))
        a_p = body_area(fig, (hy, hy + hh, hx, hx + hw), extra)
        s2 = s * max(1.0, float(np.sqrt(a_p / a_d)))
        mean, frac = down(img, s2, ox % s2, oy % s2)
        fig = snap(mean, frac > 0.5, d, extra)
    hy2 = int(round((cy - oy % s2) / s2 - hh / 2))
    hx2 = int(round((cx - ox % s2) / s2 - hw / 2))
    pad = 40
    fig = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    hy2, hx2 = hy2 + pad, hx2 + pad
    hop = head_mask(form)
    reg = fig[hy2:hy2 + hh, hx2:hx2 + hw]
    back = np.zeros_like(hop)
    if form == "mega":                       # the head's back (mane) only fills where Codex drew nothing: its own
        back[:, :BACK] = True                # mane meets its body there, the design's would stand as a straight edge
    hop_face = hop & ~back
    hop_back = hop & back & (reg[..., 3] == 0)
    reg[hop_face] = head[hop_face]
    reg[hop_back] = head[hop_back]
    ys, xs = np.nonzero(fig[..., 3] > 0)
    box = (int(ys.min()), int(ys.max()) + 1, int(xs.min()), int(xs.max()) + 1)
    crop = fig[box[0]:box[1], box[2]:box[3]]
    return crop, dict(score=round(sc, 3), square_px=round(s2, 2), head_square_px=s, phase=[round(ox, 2), round(oy, 2)],
                      head_at=[hx2 - box[2], hy2 - box[0]], box=list(crop.shape[1::-1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    fits, figs = {}, {}
    for name, form in POSES.items():
        crop, info = read(name, form, a.src)
        Image.fromarray(crop).save(lp(os.path.join(OUT, f"{name}.png")))
        fits[name] = info
        figs[name] = (form, crop)
        print(name, info)
    with open(lp(os.path.join(OUT, "pose_fit.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(fits, f, indent=1)
    if a.review:
        from PIL import ImageDraw
        os.makedirs(a.review, exist_ok=True)
        for form in ("mega", "mini"):
            d, _ = design(form)
            items = [("design", d)] + [(n, c) for n, (fm, c) in figs.items() if fm == form]
            z = 6 if form == "mega" else 8
            H = max(c.shape[0] for _, c in items) * z + 20
            W = sum(c.shape[1] * z + 12 for _, c in items)
            sheet = Image.new("RGB", (W, H), (40, 44, 36))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, c in items:
                bg = Image.new("RGBA", (c.shape[1], c.shape[0]), (96, 112, 96, 255))
                bg.alpha_composite(Image.fromarray(c))
                t = bg.convert("RGB").resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST)
                sheet.paste(t, (x, H - t.height))
                dr.text((x + 2, 2), n, fill=(255, 255, 0))
                x += t.width + 12
            path = os.path.join(a.review, f"gnar_poses_{form}.png")
            sheet.save(path)
            print(path, sheet.size)


if __name__ == "__main__":
    main()
