#!/usr/bin/env python3
"""Udyr's Codex poses (assets/source/udyr/codex_poses: POSE_PROMPTS.md, 29 key poses of League's clips on the four
stance designs) read back at the design's scale, in its colours, with the design's own head (design_shyvana_poses.py's
way).

    python tools/art/design_udyr_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_udyr_poses.py --sheet DIR      # all poses beside their stance's design (5x)
    python tools/art/design_udyr_poses.py                  # writes assets/source/udyr/hd/pose_<name>.png (+ .json)
    python tools/art/design_udyr_poses.py --rematch        # the same, the heads searched again (else the json's)

Every pose copies its stance design's head (1_head_<stance>.png of the pack), so the head gives the scale: the design's
head box (HEAD) scaled over a range of px a square is matched against the picture (masked colour distance by FFT, at half
size), the best scale and place kept. The picture is sampled on squares BODY times that size, the grid laid so the
matched head box keeps its middle (a square opaque when most of it is, the median colour), every colour snapped to the
stance design's own (Lab), the design's head pasted square for square on Codex's head's middle (HEAD_POLY: the hair's
crown, the face, the feather braid's top and the beard - one face in all frames), the outline closed. Each pose's json
keeps where the head box went (its top-left square), for rig_udyr to place the pose.
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_shyvana_poses import match_head, sample_grid  # noqa: E402
from design_udyr_model import lp  # noqa: E402
import pack_udyr_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "udyr", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "udyr", "hd")
NAMES = list(PK.POSES)
DESIGN = {"A": "idle.png", "Q": "q_idle.png", "E": "e_idle.png", "R": "r_idle.png"}
HEAD = {st: v[5] for st, v in PK.STANCES.items()}          # rows / columns of each design's head box (ends exclusive)
# each design's head to paste (x, y square edges on hd/<design>): the hair's crown, the face, the top of the feather braid
# and the beard - not the dreadlocks hanging down the back and shoulders (Codex's swing with each pose) nor the neck
HEAD_POLY = {
    "A": [(20.0, 0.0), (34.0, 0.0), (36.0, 8.0), (35.0, 21.0), (30.0, 22.0), (24.0, 22.0), (21.0, 14.0), (20.0, 6.0)],
    "Q": [(37.0, 11.0), (49.0, 11.0), (50.0, 18.0), (48.0, 30.0), (41.0, 30.0), (38.0, 22.0)],
    "E": [(42.0, 19.0), (53.0, 19.0), (54.0, 27.0), (52.0, 38.0), (45.0, 38.0), (42.0, 28.0)],
    "R": [(58.0, 23.0), (71.0, 23.0), (72.0, 32.0), (70.0, 43.0), (62.0, 43.0), (58.0, 32.0)],
}
SCALES = np.arange(8.0, 22.01, 0.25)
TILTED = {"d_hit": range(-40, 41, 10), "d_kneel": range(-40, 41, 10), "e_slam": range(-50, 51, 10),
          "e_leap": range(-30, 31, 10), "q_swipe": range(-30, 31, 10), "e_hook": range(-30, 31, 10),
          "r_thrust": range(-30, 31, 10), "r_flap": range(-30, 31, 10)}
# the squares each pose is read on (px): the pose's height in the picture over the guide's height in design squares
# (Codex drew each figure about as tall as its guide - League's frame brought to the design's size - but the heads 10-25%
# smaller than the design's against the bodies, so the head's own scale would read the bodies too big). Measured
# 2026-10-22 on the delivery (C:/t/ud_work/pose_scale.json).
GUIDE_H = {"a_punch": 62.7, "run1": 61.4, "run2": 57.6, "run3": 63.1, "run4": 59.5, "d_hit": 89.6, "d_kneel": 55.0,
           "q_wind": 62.3, "q_swipe": 61.7, "q_roar": 96.2, "q_run1": 69.1, "q_run2": 57.6, "q_run3": 67.5,
           "q_run4": 61.5, "e_hook": 61.7, "e_leap": 73.3, "e_slam": 47.4, "e_stomp": 81.6, "e_run1": 81.2,
           "e_run2": 65.9, "e_run3": 82.4, "e_run4": 65.3, "r_thrust": 67.2, "r_crouch": 67.8, "r_flap": 68.6,
           "r_run1": 94.0, "r_run2": 90.1, "r_run3": 95.1, "r_run4": 88.4}
# The squares a pose is read on: by default the size that gives the figure the stance design's area (Codex's figures
# keep their mass from pose to pose far better than their height - a stride or a crouch changes the height by a fifth,
# the area by a few per cent; the heights read the passing frames of the runs 10-20% small and the ram's poses a quarter
# small). A pose that folds or spreads a lot is set by hand, between its area and its height: the death's first blow
# (arms flung out), the kneel (legs folded under him: about 45 rows, three quarters of the idle's), the ram's leap and
# the phoenix taking wing (legs tucked, arms spread).
SCALE = {"d_hit": 17.5, "d_kneel": 20.5, "e_leap": 15.0, "r_flap": 13.7}


def own_scale(name):
    """px a square to read pose `name` on (SCALE, else the area rule)."""
    if name in SCALE:
        return SCALE[name]
    a = raw(name)
    return float(np.sqrt((a[..., 3] >= 128).sum() / (design(stance(name))[..., 3] > 0).sum()))


def stance(name):
    return PK.POSES[name][0]


def design(st):
    return np.asarray(Image.open(lp(os.path.join(OUT, DESIGN[st]))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"udyr-pose-{name}.png"))).convert("RGBA"))


def head_box(d, st):
    r0, r1, c0, c1 = HEAD[st]
    return d[r0:r1, c0:c1]


def head_mask(d, st):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(HEAD_POLY[st], fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


def finish(fig):
    """The outline closed; single enclosed holes the read-back left take the outline."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() <= 1:
            pad[h] = (*ink, 255)
    return pad


# the bodies against the heads in Codex's poses (the clean runs: the pose's sampling square over its head's): the
# design's head is pasted at its own size on a body read at the design's size, so the head is looked for at the body's
# square over this
BODY = {"A": 1.12, "Q": 1.25, "E": 1.2, "R": 1.22}
FACE = {  # rows / columns (ends exclusive) of each design's face, beard and the feather's top: the matching template
    "A": (6, 24, 21, 36), "Q": (15, 33, 37, 51), "E": (22, 38, 41, 54), "R": (26, 44, 58, 72)}


def feather(a, cut=128):
    """The feather braid's pixels: a saturated bright blue with almost no red (the phoenix's blades are a greyer navy
    with red in them, the eyes a pale cyan)."""
    rgb = a[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (a[..., 3] >= cut) & (b > 195) & (r < 40) & (g < 165)


def located(name):
    """(px a square, x, y, cost, tilt) for a pose's head box, found from its feather braid: the braid's top (where it
    hangs from beside the face) puts the design's head box where it sits in the design, at the body's square over BODY;
    then the face (FACE) is matched round there, a few squares each way, the scale +-10%."""
    st = stance(name)
    d = design(st)
    a = raw(name)
    s0 = own_scale(name) / BODY[st]
    fd = feather(d)
    fy, fx = np.nonzero(fd)
    top = fy.min()
    fxd = fx[fy <= top + 1].mean()
    fr = feather(a)
    lab, n = ndimage.label(fr, structure=np.ones((3, 3)))
    if not n:
        return None
    big_ = 1 + int(np.argmax(ndimage.sum(fr, lab, range(1, n + 1))))
    ry, rx = np.nonzero(lab == big_)
    rtop = ry.min()
    rxa = rx[ry <= rtop + s0].mean()
    f0, f1, g0, g1 = FACE[st]
    best = None
    for k in np.arange(0.9, 1.101, 0.05):
        sh = s0 * k
        # the face box's top-left on the picture as the feather puts it
        ex = rxa - (fxd + 0.5 - g0) * sh
        ey = rtop - (top - f0) * sh
        tmpl = d[f0:f1, g0:g1]
        H, W = int(round(tmpl.shape[0] * sh)), int(round(tmpl.shape[1] * sh))
        ys = np.minimum((np.arange(H) / sh).astype(int), tmpl.shape[0] - 1)
        xs = np.minimum((np.arange(W) / sh).astype(int), tmpl.shape[1] - 1)
        T = tmpl[np.ix_(ys, xs)]
        M = T[..., 3] > 0
        for dy in range(-int(3 * sh), int(3 * sh) + 1, 2):
            for dx in range(-int(3 * sh), int(3 * sh) + 1, 2):
                x0, y0 = int(round(ex + dx)), int(round(ey + dy))
                if x0 < 0 or y0 < 0 or x0 + W > a.shape[1] or y0 + H > a.shape[0]:
                    continue
                P = a[y0:y0 + H, x0:x0 + W]
                op = P[..., 3] >= 128
                diff = np.abs(P[..., :3].astype(float) - T[..., :3].astype(float)).sum(-1) / 765.0
                diff[~op] = 1.0
                cost = float(diff[M].mean())
                if best is None or cost < best[0]:
                    # the head box's top-left from the face box's
                    best = (cost, float(sh), int(round(x0 - (g0 - HEAD[st][2]) * sh)),
                            int(round(y0 - (f0 - HEAD[st][0]) * sh)))
    if best is None:
        return None
    return best[1], best[2], best[3], best[0], 0


CACHE = "C:/t/ud_work/pose_match_cache.json"      # the matches of the last run (a run takes ten minutes)


def matched(name, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found; the
    scales searched round the pose's own sampling square (0.6-1.3 of it: the heads came smaller than the bodies)."""
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = None
    if name not in TILTED:
        m = located(name)
    if m is None:
        st = stance(name)
        s0 = own_scale(name)
        m = match_head(raw(name), head_box(design(st), st), scales=np.arange(0.6 * s0, 1.3 * s0 + 0.01, 0.25),
                       angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f)
    return m


def read(name, match):
    """The pose on its design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    st = stance(name)
    d = design(st)
    a = raw(name)
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD[st]
    hw, hh = c1 - c0, r1 - r0
    s2 = own_scale(name)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(d, st)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if not ang:                                        # a tipped head keeps Codex's own (the design's is upright)
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
    big_ = finish(big_)
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), s2, cost, ang


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's match)")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure:
        for n in names:
            st = stance(n)
            s, x, y, cost, ang = match_head(raw(n), head_box(design(st), st), scales=SCALES,
                                            angles=TILTED.get(n, (0,)))
            print(f"{n:9s} {st} {s:5.2f} px a square, head at ({x}, {y}) tilted {ang}, cost {cost:.4f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:9s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        for st in DESIGN:
            tiles = [("design", design(st))] + [(n, f) for n, (f, _, _) in figs.items() if stance(n) == st]
            if len(tiles) == 1:
                continue
            Hm = max(t.shape[0] for _, t in tiles)
            W = sum(t.shape[1] * z + 12 for _, t in tiles)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in tiles:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"udyr_poses_{st}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as f:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, f)


if __name__ == "__main__":
    main()
