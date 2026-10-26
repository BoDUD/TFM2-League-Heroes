#!/usr/bin/env python3
"""Skarner's Codex poses (assets/source/skarner/codex_poses/skarner-poses: POSE_PROMPTS.md, 18 key poses of his League
clips on his design, 2026-10-26) read back at the design's scale, in its colours, with the design's own head
(design_trundle_poses.py's way).

    python tools/art/design_skarner_poses.py --measure        # each pose's head match over a range of scales
    python tools/art/design_skarner_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_skarner_poses.py                  # writes assets/source/skarner/hd/pose_<name>.png (+ .json)

Codex drew these off the 9 px grid, each at its own size (its HANDOFF: soft alpha, no common grid, heads redrawn), so
the head gives the place and a first scale: the design's hood and face scaled over SCALES px a square matched against
the picture, each place checked by eye (HEAD_AT). Codex drew every head smaller
round its body than the design has it (Shyvana's case, BODY_ALL there): read at the head's squares the claws, the
carapace and the legs stood 10-25% bigger than the idle's (checked with the idle's outline laid on each pose, its head on
the pose's head, at 1.0 / 1.1 / 1.2 / 1.3 times the head's squares, 2026-10-26). BODY is the factor per pose at which
the body (the claws, the carapace's top line, the legs' reach) lies on the idle's outline; the pose is sampled on
squares that size (one square = one of the design's), the grid laid through Codex's head box, every colour snapped to
the design's own (Lab; the boulder's from hd/rock.png in the poses holding it), the design's head pasted square for
square with its middle on Codex's head's middle (the polygon POLY: one face in every frame), the outline closed. Each
pose's json keeps where the head box went (its top-left square), for rig_skarner to place the pose.
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
from design_skarner_hd import lp  # noqa: E402
import pack_skarner_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "skarner", "codex_poses", "skarner-poses")
OUT = os.path.join(ROOT, "assets", "source", "skarner", "hd")
# the silver hood and the bone face in hd/idle.png: its box (columns, rows; ends exclusive) and its outline - not the
# claws beside it nor the carapace over it
HEAD_BOX = (43, 33, 62, 58)
POLY = [(45.5, 33.5), (53.0, 33.5), (56.0, 35.5), (58.5, 38.5), (60.5, 42.5), (60.5, 50.0), (59.5, 55.5), (56.0, 57.0),
        (48.0, 57.0), (45.5, 53.5), (44.0, 48.0), (43.0, 41.0), (43.0, 36.0)]
SCALES = np.arange(8.0, 15.01, 0.25)
# Codex's head per pose: (px a square, the head template's top-left in those squares) - the design's hood and face
# (columns 44-61, rows 34-57 of hd/idle.png, its bone / silver / orange squares) matched over SCALES on the picture
# put on black, each found place checked by eye (2026-10-26; design_shyvana_poses.match_head put q_dig's on the boulder)
HEAD_AT = {"a_wind": (10.25, 65, 79), "a_strike": (10.5, 68, 90), "q_dig": (9.25, 54, 98), "q_lift": (12.0, 56, 68),
           "t_wind": (12.25, 59, 68), "t_throw": (8.75, 75, 110), "w_rear": (10.5, 63, 75), "w_slam": (10.75, 70, 75),
           "e_charge": (11.25, 73, 63), "e_grab": (12.0, 55, 61), "r_lash": (9.5, 78, 85), "r_hold": (12.75, 54, 68),
           "run1": (11.5, 64, 76), "run2": (11.75, 65, 73), "run3": (11.25, 66, 77), "run4": (11.0, 69, 78),
           "d_rear": (9.75, 72, 72), "d_down": (9.0, 94, 110)}
HEAD_MID = (53.0, 46.0)        # the template's middle in hd/idle.png (columns 44 + 9, rows 34 + 12)
# the body's factor over the head's squares per pose (the idle's outline on each pose, its head on the pose's head, at
# 1.0 / 1.1 / 1.2 / 1.3 times, 2026-10-26)
BODY = {"a_wind": 1.2, "a_strike": 1.2, "q_dig": 1.2, "q_lift": 1.1, "t_wind": 1.1, "t_throw": 1.25, "w_rear": 1.2,
        "w_slam": 1.2, "e_charge": 1.2, "e_grab": 1.2, "r_lash": 1.2, "r_hold": 1.1, "run1": 1.1, "run2": 1.1,
        "run3": 1.1, "run4": 1.1, "d_rear": 1.2, "d_down": 1.2}
ROCK = {"q_dig", "q_lift", "t_wind"}               # the poses holding the boulder: its colours from hd/rock.png
CACHE = "C:/t/sk_work/pose_match_cache.json"
NAMES = list(PK.POSES)


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"skarner-pose-{name}.png"))).convert("RGBA"))


def head_box(d):
    c0, r0, c1, r1 = HEAD_BOX
    return d[r0:r1, c0:c1]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(POLY, fill=255)
    return (np.asarray(img) > 0) & (d[..., 3] > 0)


HOLE = 8           # enclosed clear specks up to this many squares are ground showing between Codex's soft segments


def finish(fig):
    """The outline closed; the enclosed specks of ground the read-back left (HOLE squares or fewer: between tail
    segments, at the joints - the tails' real curls are bigger) closed: with the outline where most of the squares round
    a speck are the outline or dark, else with the commonest colour round it."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lb, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lb == j
        if h.sum() > HOLE:
            continue
        rim = ndimage.binary_dilation(h) & ~h & op
        cols = [tuple(c) for c in pad[rim][:, :3]]
        dark = sum(1 for c in cols if sum(c) < 120)
        fill = ink if dark * 2 >= len(cols) else max(set(cols), key=cols.count)
        pad[h, :3] = fill
        pad[h, 3] = 255
    return pad


def matched(name, again=False):
    """(px a square, x, y) of Codex's head template's top-left in the picture's px."""
    f, hx, hy = HEAD_AT[name]
    return f, hx * f, hy * f


def palette_ref(name):
    """The colours a pose snaps to: the idle's, and the boulder's for the poses holding it."""
    d = design()
    if name not in ROCK:
        return d
    r = design("rock.png")
    return np.concatenate([d.reshape(-1, 4), r.reshape(-1, 4)])[None]


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px)."""
    d = design()
    fh, px, py = match
    s = fh * BODY[name]
    c0, r0, c1, r1 = HEAD_BOX
    a, (ci, cj) = sample_grid(raw(name), s, px, py)    # the grid's lines through Codex's head template's top-left
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    fig = snap(a, palette_ref(name))
    # Codex's head middle in the new squares; the design's head laid with its middle (HEAD_MID) there
    mx = ci + 9 * fh / s
    my = cj + 12 * fh / s
    bx, by = int(round(mx - (HEAD_MID[0] - c0))), int(round(my - (HEAD_MID[1] - r0)))
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big_ = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    big_[ys - r0 + by + pad, xs - c0 + bx + pad] = d[ys, xs]
    big_ = finish(big_)
    ys2, xs2 = np.nonzero(big_[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big_[y0:ys2.max() + 1, x0:xs2.max() + 1], (bx + pad + 1 - x0, by + pad + 1 - y0), float(s)


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
        d = design()
        for n in names:
            s, x, y, cost, ang = match_head(raw(n), head_box(d), scales=SCALES)
            print(f"{n:9s} head {s:5.2f} px a square at ({x}, {y}), cost {cost:.4f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s = read(n, m)
        figs[n] = (fig, at, m, s)
        print(f"{n:9s} head {m[0]:5.2f} x {BODY[n]} = {s:5.2f} px a square -> {fig.shape[1]} x {fig.shape[0]}, "
              f"head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", design())] + [(n, figs[n][0]) for n in names if n in figs]
        rows = [tiles[i:i + 4] for i in range(0, len(tiles), 4)]
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
            path = os.path.join(a.sheet, f"skarner_poses_{k}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, m, s) in figs.items():
        stem = f"pose_{n}"
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"{stem}.png")))
        with open(lp(os.path.join(OUT, f"{stem}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [int(at[0]), int(at[1])], "scale": s, "head": list(HEAD_AT[n])}, fh)


if __name__ == "__main__":
    main()
