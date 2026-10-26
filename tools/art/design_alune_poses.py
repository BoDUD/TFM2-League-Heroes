#!/usr/bin/env python3
"""Alune's Codex poses (assets/source/alune/codex_poses/alune-poses: POSE_PROMPTS.md, 14 key poses of her own TFT clips
on her design, 2026-10-26) read back at the design's scale, in its colours, with the design's own head
(design_zaahen_poses.py's way).

    python tools/art/design_alune_poses.py --measure        # each pose's head match and its body against the skeleton
    python tools/art/design_alune_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_alune_poses.py                  # writes assets/source/alune/hd/pose_<name>.png (+ .json)
    python tools/art/design_alune_poses.py --rematch        # the same, the heads searched again (else the json's)

Codex's own 1254 exports are its raws fitted to the canvas and re-cut into 12 px cells (its HANDOFF: "whole-art fit",
majority colour a cell), muddier than the raws; the raws (raw/, soft alpha, ~9-10 px squares) are read. Her poses copy
the design's head, so the head gives the place and the scale: the head box HEAD (the horns, the silver hair with its
bun, the forehead gem and the face to the chin: hd/idle.png rows 0-23, columns 19-47) is matched against the raw
(design_shyvana_poses.match_head), the raw read on the matched head's own squares (sample_grid), then - where Codex drew
the body bigger or smaller round the head than her skeleton has it - brought to the skeleton's size by whole-line cuts or
repeats about the head's middle (BODY: the read-back's head top to its lowest square over the skeleton's, the skeletons
being her own clips projected at the design's scale, pack_alune_poses), every colour snapped to the design's own (Lab),
the design's head pasted square for square on Codex's head's place (the polygon POLY; one face in all frames), Codex's
own hair left round it and its own horns beside the pasted ones cleared, the outline closed. Each pose's json keeps where
the head box went (its top-left square), for rig_alune to place the pose. Heads Codex drew tipped (TILTED) are found
turned; those tipped only 10 degrees with the body (UPRIGHT) wear the design's upright head all the same, the one lying
on her back (LYING) the design's head turned a quarter (crown to the left, face up) - one face in every frame.
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
from design_alune_hd import lp  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_shyvana_poses import match_head, sample_grid  # noqa: E402
from design_zaahen_poses import finish, resize_lines  # noqa: E402
import pack_alune_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "alune", "codex_poses", "alune-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "alune", "hd")
HEAD = (0, 24, 19, 48)                           # rows / columns of the head box in hd/idle.png
# the horns, the hair and its bun, the forehead gem, the face to the chin, the earring - not the collar's lapels that
# reach up beside the chin (columns 29-34 from row 21) or the shoulders
POLY = [(39.0, 0.0), (41.0, 0.0), (43.0, 3.0), (44.0, 6.0), (47.0, 9.0), (48.0, 12.0), (48.0, 17.0), (47.0, 19.0),
        (45.0, 21.0), (43.0, 23.0), (41.0, 24.0), (35.0, 24.0), (34.0, 21.0), (27.0, 21.0), (25.0, 22.5), (20.0, 22.5),
        (19.0, 18.0), (21.0, 15.0), (24.0, 13.0), (25.0, 10.0), (27.0, 7.0), (29.0, 4.0), (31.0, 1.0), (34.0, 1.0),
        (35.0, 5.0), (37.0, 5.0)]
GROW_ROWS = 12                                   # the polygon grows by a square (its outline) above this row only
HORN_ROWS = 9                                    # the head box's rows from its top down to the hairline: the horns
SCALES = np.arange(7.0, 13.01, 0.25)             # Codex's squares round the head (asked 12 px)
TILTED = {"d_fall": range(-40, 41, 10), "d_down": range(-90, 91, 10), "r_call": range(-30, 31, 10)}   # heads Codex drew tipped
# the body's size round the head against the skeleton's (1.0 = the skeleton's). --measure 2026-10-26 (the read-back's
# head top to its lowest square over the skeleton's head box top to its lowest pixel): Codex drew every STANDING body
# 24-33% too big round the design's head (her standing figure as tall as the seated design with its crescent), the
# SEATED ones (Moonlight, the glide) at the design's size (0.98-1.05: set 1.0, the design's own build); the lying d_down
# has no height to measure: d_fall's
BODY = {"a_wind": 1.26, "a_throw": 1.24, "a_catch": 1.30, "q_raise": 1.25, "q_call": 1.24, "e_bless": 1.0,
        "r_raise": 1.33, "r_call": 1.28, "run1": 1.0, "run2": 1.0, "run3": 1.0, "run4": 1.0, "d_fall": 1.28,
        "d_down": 1.28}
# poses with a hand or the ring right over the head: the body brought down about the head's middle drew them down onto
# it, while the pasted head keeps the design's size (it reaches hh * (1 - k) / 2 rows over Codex's shrunk head) - that
# many copies of the row just over the head box go in there (whole-line repeats: the raised arms a little longer,
# nothing redrawn), so the hands hold the ring over the horns again
ROOM_OVER = {"r_raise"}
# tipped heads close enough to upright to wear the design's own (one face): Codex leant them 10 degrees with the body
UPRIGHT = {"r_call", "d_fall"}
# lying poses: the design's head turned a quarter (np.rot90's k: 1 = the crown to the image left, the face up - on her
# back), pasted on the middle of Codex's tipped head (a quarter turn is lossless: one face, never re-drawn)
LYING = {"d_down": 1}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
CACHE = "C:/t/al_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"alune-pose-{name}.png"))).convert("RGBA"))


def head_box(d):
    r0, r1, c0, c1 = HEAD
    return d[r0:r1, c0:c1]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    m = np.asarray(img) > 0
    grown = ndimage.binary_dilation(m, structure=np.ones((3, 3), bool))
    grown[GROW_ROWS:] = m[GROW_ROWS:]
    return grown & (d[..., 3] > 0)


def matched(name, again=False):
    """match_head's (px a square, x, y, cost, tilt) for a pose, kept in hd/pose_<name>.json ("match") once found."""
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    if not again and os.path.isfile(CACHE):
        c = json.load(open(CACHE, encoding="utf-8"))
        if name in c:
            return tuple(c[name])
    m = match_head(raw(name), head_box(design()), scales=SCALES, angles=TILTED.get(name, (0,)))
    c = json.load(open(CACHE, encoding="utf-8")) if os.path.isfile(CACHE) else {}
    c[name] = [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(c, fh)
    return m


def is_hair(rgb):
    """Her silver / ice-blue hair (the design's e2f8fc a5c2ed 839ed5: blue well over red, green near red) - not the
    glaive's cyan blades (green far over red), not the violet robe (red near blue, green low), not the skin."""
    rgb = rgb.astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (r > 110) & (b > 170) & (g - r >= 0) & (g - r < 45) & (b - r >= 20)


def clear_leftovers(fig, pasted, box):
    """Codex's own hair left round the pasted head: every hair-coloured square in `box` the paste did not lay takes the
    most common colour round it that is not hair, or goes clear where most round it is clear; repeated until none is
    left (design_zaahen_poses.clear_leftovers with her hair)."""
    y0, y1, x0, x1 = box
    for _ in range(12):
        op = fig[..., 3] > 0
        left = np.zeros(op.shape, bool)
        left[y0:y1, x0:x1] = True
        left &= op & ~pasted & is_hair(fig[..., :3])
        if not left.any():
            return fig
        out = fig.copy()
        for y, x in zip(*np.nonzero(left)):
            nb = fig[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
            clear = int((nb[:, 3] == 0).sum())
            keep = [tuple(c) for c in nb if c[3] > 0 and not is_hair(c[None, :3])[0]]
            if clear >= 5 or not keep:
                if clear >= 3:
                    out[y, x] = 0
                continue
            out[y, x] = max(set(keep), key=keep.count)
        fig = out
    return fig


def clear_horns(fig, pasted, box):
    """Codex's own horns left beside the pasted ones: in `box` (the horns' rows of the head box, three squares round),
    every part the paste did not lay that stays inside the box goes clear; a part that runs out of it (a raised arm, the
    glaive or the ring passing behind the head) stays."""
    y0, y1, x0, x1 = box
    sub = (fig[y0:y1, x0:x1, 3] > 0) & ~pasted[y0:y1, x0:x1]
    lb, n = ndimage.label(sub, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        m = lb == j
        ys, xs = np.nonzero(m)
        if ys.min() == 0 or ys.max() == m.shape[0] - 1 or xs.min() == 0 or xs.max() == m.shape[1] - 1:
            continue
        fig[y0:y1, x0:x1][m] = 0
    return fig


def skeleton_height(name):
    """Her skeleton's figure for the pose (pack_alune_poses on the 12 px canvas): the top of its grey head box (the
    horns) to the textured ref's lowest pixel, in squares - what the read-back's head top to its lowest square is brought
    to (a ring raised over the head is above the box: not counted, as in the read-back)."""
    stem = os.path.join(PK_OUT, f"{PK_NUM[name]}_{name}")
    sk = np.asarray(Image.open(lp(stem + "_skeleton.png")).convert("RGB")).astype(int)
    top = np.nonzero((np.abs(sk - np.array((110, 110, 110))).sum(-1) == 0).any(1))[0].min()
    ref = np.asarray(Image.open(lp(stem + "_ref.png")).convert("RGB")).astype(int)
    bg = np.array(PK.GREY)
    grid = np.array((212, 212, 212))
    fg = (np.abs(ref - bg).sum(-1) > 30) & (np.abs(ref - grid).sum(-1) > 30) & ~((ref[..., 0] > 200) &
                                                                                   (ref[..., 1] < 80))
    ys, _ = np.nonzero(fg)
    return (ys.max() - top + 1) / PK.PX


PK_OUT = r"C:\t\al_work\alune_pose_pack"
PK_NUM = {n: k + 2 for k, n in enumerate(PK.POSES)}


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    d = design()
    s, hx, hy, cost, ang = match
    r0, r1, c0, c1 = HEAD
    hw, hh = c1 - c0, r1 - r0
    a, (ci, cj) = sample_grid(raw(name), s, hx, hy)   # the head box's top-left at cell (ci, cj)
    k = 1.0 / BODY.get(name, 1.0)
    a, mid = resize_lines(a, k, (ci + hw / 2, cj + hh / 2))
    ci, cj = int(round(mid[0] - hw / 2)), int(round(mid[1] - hh / 2))
    if name in ROOM_OVER and k < 1.0:
        extra = int(round(hh * (1.0 - k) / 2))
        a = np.concatenate([a[:cj], np.repeat(a[cj - 1:cj], extra, 0), a[cj:]], 0)
        cj += extra
    fig = snap(a, d)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    if name in LYING:
        big_ = lay_head(big_, d, hm, (ci + hw / 2 + pad, cj + hh / 2 + pad), LYING[name])
    elif not ang or name in UPRIGHT:                   # a tipped head keeps Codex's own (the design's is upright)
        big_[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
        pasted = np.zeros(big_.shape[:2], bool)
        pasted[ys - r0 + cj + pad, xs - c0 + ci + pad] = True
        gy, gx = cj + pad, ci + pad
        big_ = clear_leftovers(big_, pasted, (max(0, gy - 4), gy + hh, max(0, gx - 4), gx + hw + 4))
        big_ = clear_horns(big_, pasted, (gy - 3, gy + HORN_ROWS, gx - 3, gx + hw + 3))
    big_ = finish(big_)
    op = big_[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        if (lb == j).sum() < SPECK:
            big_[lb == j] = 0
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), float(s), cost, ang


def lay_head(fig, d, hm, mid, k):
    """The design's head (its polygon's squares) turned k quarters, its middle on `mid` (column, row) of fig, over
    Codex's own head; Codex's hair left round it cleared (clear_leftovers in the turned head's box)."""
    r0, r1, c0, c1 = HEAD
    box = np.zeros((r1 - r0, c1 - c0, 4), np.uint8)
    m = hm[r0:r1, c0:c1]
    box[m] = d[r0:r1, c0:c1][m]
    turned = np.rot90(box, k)
    th, tw = turned.shape[:2]
    x0, y0 = int(round(mid[0] - tw / 2)), int(round(mid[1] - th / 2))
    tm = turned[..., 3] > 0
    ys, xs = np.nonzero(tm)
    fig[ys + y0, xs + x0] = turned[ys, xs]
    pasted = np.zeros(fig.shape[:2], bool)
    pasted[ys + y0, xs + x0] = True
    return clear_leftovers(fig, pasted, (max(0, y0 - 4), y0 + th + 4, max(0, x0 - 4), x0 + tw + 4))


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--rematch", action="store_true", help="search the heads again (else the json's)")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    if a.measure:
        for n in names:
            m = matched(n, a.rematch)
            s, x, y, cost, ang = m
            r = raw(n)
            op = r[..., 3] >= 128
            ys, xs = np.nonzero(op)
            got = (ys.max() - y) / s
            want = skeleton_height(n)
            print(f"{n:8s} {s:5.2f} px a square at ({x}, {y}) tilt {ang:4d} cost {cost:.4f}; figure "
                  f"{(xs.max() - xs.min()) / s:5.1f} x {(ys.max() - ys.min()) / s:5.1f} squares, head top to the lowest "
                  f"{got:5.1f}, skeleton {want:5.1f} -> BODY {got / want:4.2f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:8s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in NAMES if n in figs]
        rows = [tiles[i:i + 5] for i in range(0, len(tiles), 5)]
        for k, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"alune_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m) in figs.items():
        stem = f"pose_{n}"
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{stem}.png")))
        with open(lp(os.path.join(OUT, f"{stem}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])],
                       "match": [float(m[0]), int(m[1]), int(m[2]), float(m[3]), int(m[4])]}, fh)


if __name__ == "__main__":
    main()
