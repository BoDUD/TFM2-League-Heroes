#!/usr/bin/env python3
"""Silco's Codex poses (assets/source/silco/codex_poses/silco-poses: POSE_PROMPTS.md, 15 key poses of his own TFT clips
on his design, 2026-10-27) read back at the design's scale, in its colours, with the design's own head
(design_alune_poses.py's way).

    python tools/art/design_silco_poses.py --measure        # each pose's head match and its body against the skeleton
    python tools/art/design_silco_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_silco_poses.py                  # writes assets/source/silco/hd/pose_<name>.png (+ .json)
    python tools/art/design_silco_poses.py --rematch        # the same, the heads searched again (else the json's)

Codex's own 1254 exports are its raws cleaned and moved down to the ground line (its HANDOFF); the raws (raw/, soft
alpha, ~10 px squares; a_back, q_throw and r_throw in their -corrected redraws, the ones Codex picked) are read. His
poses copy the design's head, so the head gives the place and the scale: the head box HEAD (the slicked hair with its
tuft, the face with the scarred eye, to the chin: hd/idle.png rows 0-18, columns 11-28) is matched against the raw
(design_shyvana_poses.match_head), the raw read on the matched head's own squares (sample_grid), brought to the
skeleton's size where Codex drew the body bigger or smaller round the head (BODY, from --measure), every colour snapped
to the design's own (Lab), the design's head pasted square for square on Codex's head's place (the polygon POLY: one face
in all frames), Codex's own hair left round it cleared, the outline closed. Each pose's json keeps where the head box went
(its top-left square), for rig_silco to place the pose. Heads Codex drew tipped (TILTED) keep Codex's own head unless
UPRIGHT (close enough to wear the design's).
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
from design_silco_hd import lp  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_shyvana_poses import match_head, sample_grid  # noqa: E402
from design_zaahen_poses import finish, resize_lines  # noqa: E402
import pack_silco_poses as PK  # noqa: E402
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "silco", "codex_poses", "silco-poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "silco", "hd")
HEAD = (0, 19, 11, 29)                           # rows / columns of the head box in hd/idle.png
# the slicked hair and its tuft, the face with the scarred eye, the jaw to the chin - not the magenta collar rising
# beside the chin (columns 17-20 from row 16) or the shoulders
POLY = [(15.0, 0.0), (25.0, 0.0), (28.0, 4.0), (28.0, 9.0), (29.0, 11.0), (28.5, 17.0), (27.0, 19.0), (21.0, 19.0),
        (20.5, 16.0), (17.0, 15.5), (14.0, 14.5), (13.0, 12.0), (11.5, 10.0), (11.0, 6.0), (12.0, 3.0)]
GROW_ROWS = 10                                   # the polygon grows by a square (its outline) above this row only
HORN_ROWS = 4                                    # the head box's rows from its top down: the hair's tuft
SCALES = np.arange(7.0, 14.01, 0.25)             # Codex's squares round the head (asked 13 px)
CORRECTED = {"a_back": "-corrected", "q_throw": "-corrected", "r_throw": "-corrected"}
TILTED = {"d_fall": range(-40, 41, 10), "d_down": range(-90, 91, 10), "a_throw": range(-30, 31, 10),
          "a_wind": range(-30, 31, 10)}
# the body's size round the head (1.0 = the design's). --measure 2026-10-27: Codex drew the upright poses 82.8-86.3
# squares from the hair to the soles round the design's head (a_back 84.1, e_show 86.3, q_wind 82.8; the design is 80):
# about 5% too big. His TFT clips stoop (the walk, the throws, the fall: their skeletons 59-78 squares) where Codex drew
# him upright, so the skeletons' heights would squash those poses: one scale for every pose, the design's build
BODY = {n: 1.05 for n in ("a_wind", "a_throw", "a_back", "q_wind", "q_throw", "e_show", "e_toss", "r_raise", "r_throw",
                          "run1", "run2", "run3", "run4", "d_fall", "d_down")}
# Codex's heads in the canister throws and the flood's wind-up came out smaller round their bodies (matched at 11-11.75
# px a square against 12.5-13 elsewhere): read on their own squares those bodies stood 94-96 rows; brought to the
# others' build (the throws leaning back ~80 rows, the raised knee ~80 under its head box). The second walk frame and the
# vial shown at the face stood 3-4 rows over the rest
BODY.update({"q_throw": 1.24, "r_throw": 1.24, "r_raise": 1.21, "run2": 1.10, "run3": 1.08, "e_show": 1.09})
ROOM_OVER = set()
UPRIGHT = set()
LYING = {}
SPECK = 6                                        # parts apart from the figure smaller than this are dropped
HOLE = 15                                        # clear holes up to this many squares inside the figure are closed
# poses whose loose parts go too: the vial Codex drew already flying off the hand in the fling (57 squares apart; the
# attack's projectile a_vial is that vial). The fall's flying cane (far bigger) stays
SPECKS = {"a_throw": 80}
CACHE = "C:/t/sc_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"silco-pose-{name}{CORRECTED.get(name, '')}.png"))).convert("RGBA"))


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
    """His black / dark grey hair (the design's 40393f and its grey streaks: grey, mid-dark) - not the near-black
    outline (0b010a), not the brown waistcoat or boots (red well over blue), not the magenta shirt."""
    rgb = rgb.astype(int)
    mx, mn = rgb.max(-1), rgb.min(-1)
    return (mx > 45) & (mx < 135) & (mx - mn < 22)


def clear_leftovers(fig, pasted, box):
    """Codex's own hair left round the pasted head: every hair-coloured square in `box` the paste did not lay takes the
    most common colour round it that is not hair, or goes clear where most round it is clear; repeated until none is
    left (design_zaahen_poses.clear_leftovers with his hair)."""
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
    """Codex's own hair tuft left beside the pasted one: in `box` (the tuft's rows of the head box, three squares round),
    every part the paste did not lay that stays inside the box goes clear; a part that runs out of it (a raised arm, the
    cane or a vial passing behind the head) stays."""
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
    """His skeleton's figure for the pose (pack_silco_poses on the 13 px canvas): the top of its grey head box (the
    hair) to the textured ref's lowest pixel, in squares - what the read-back's head top to its lowest square is brought
    to (an arm raised over the head is above the box: not counted, as in the read-back)."""
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


PK_OUT = r"C:\t\sc_work\silco_pose_pack"
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
    big_ = close_gaps(big_, d)
    op = big_[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    for j in range(1, n + 1):
        if (lb == j).sum() < SPECKS.get(name, SPECK):
            big_[lb == j] = 0
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), float(s), cost, ang


def close_gaps(fig, d):
    """The gap check (the user's rule: no ground showing through the body): the clear holes the figure closes in that
    are no bigger than HOLE squares (between the legs, under an arm; the loops the cane closes are far bigger) and every
    one-square crack between two opaque squares across or up and down take the design's outline colour."""
    out = fig.copy()
    ink = tuple(PD.edge_colour(d))[:3] + (255,)
    op = out[..., 3] > 0
    h = ndimage.binary_fill_holes(op) & ~op
    lb, n = ndimage.label(h)
    for j in range(1, n + 1):
        if (lb == j).sum() <= HOLE:
            out[lb == j] = ink
    op = out[..., 3] > 0
    p = np.pad(op, 1)
    crack = ~op & ((p[1:-1, :-2] & p[1:-1, 2:]) | (p[:-2, 1:-1] & p[2:, 1:-1]))
    out[crack] = ink
    return out


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
            path = os.path.join(a.sheet, f"silco_poses_{k}.png")
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
