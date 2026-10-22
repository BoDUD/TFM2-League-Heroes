#!/usr/bin/env python3
"""K'Sante's Codex poses (assets/source/ksante/codex_poses: POSE_PROMPTS.md, League's whole-body poses of both stances on
skeletons) read back at the design's scale, in its colours, with the design's own head - design_shyvana_poses.py's way,
per stance.

    python tools/art/design_ksante_poses.py --measure        # each pose's scale and head position (the head matched)
    python tools/art/design_ksante_poses.py --sheet DIR      # all poses beside their design (5x)
    python tools/art/design_ksante_poses.py                  # writes assets/source/ksante/hd/pose_<name>.png (+ .json)
    python tools/art/design_ksante_poses.py --rematch        # the same, the heads searched again (else the json's)

Every pose copies its stance's head (1_head_base.png / 1_head_ao.png of the pack), so the head gives the scale: the
design's head (HEAD_POLY, the hair, the face and the beard down to the chin, its gold - the earring, a pauldron's corner
- and blue - the scarf - squares left out, they move with the shoulders) scaled over a range of px a square is matched
against the picture (masked colour distance by FFT, at half size), the best scale and place kept. The picture is then
sampled on squares of the body's own scale (body_px), laid so the matched head box keeps its middle, every colour snapped to
the design's own (Lab), the design's head pasted square for square there (one face in all frames), the outline closed.
(The squares: not BODY times the head's as for Shyvana - see body_px.)
Each pose's json keeps where the head box went (its top-left square), for rig_ksante to place the pose.
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
import design_shyvana_poses as SP  # noqa: E402  match_head, sample_grid, finish
from design_chogath_side import snap  # noqa: E402
from design_ksante_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ksante", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "ksante", "hd")
BASE = ["a_back", "a_strike", "q_up", "q_down", "q2_down", "q3_up", "q3_slam", "w_wall", "w_dash", "r_bash", "r_fly",
        "d_slump", "d_kneel", "run1", "run2", "run3", "run4"]
AO = ["ao_swing_back", "ao_swing", "ao_leap", "ao_smash", "ao_cross", "ao_charge", "ao_run1", "ao_run2", "ao_run3",
      "ao_run4"]
# each stance: its design, the head box (rows / columns, ends exclusive) and the head polygon (x, y square edges): the
# hair, the face and the beard down to the chin - not the scarf, the shoulders or the ntofos
STANCES = {
    "base": dict(file="idle.png", head=(7, 26, 22, 44),
                 poly=[(22, 9), (24, 7), (39, 7), (42, 10), (43, 13), (42, 16), (40, 22), (39, 25), (29, 25),
                       (26, 23), (23, 22), (22, 18)]),
    "ao": dict(file="ao_idle.png", head=(0, 22, 36, 62),
               poly=[(36, 4), (39, 2), (42, 1), (50, 0), (56, 0), (60, 3), (62, 7), (61, 11), (59, 14), (58, 19),
                     (55, 22), (44, 22), (40, 20), (38, 15), (36, 10)]),
}
SCALES = np.arange(7.0, 16.01, 0.25)
TILTED = {"d_slump": range(-30, 31, 10), "d_kneel": range(-30, 31, 10), "r_fly": range(-40, 41, 10),
          "r_bash": range(-30, 31, 10)}
# The squares a pose is read on: Codex drew every figure bigger than its skeleton (run 2: 895 px tall where the
# skeleton was 720) and the heads smaller than the bodies, 1.0-1.5 times smaller from pose to pose - neither its own
# squares (8-10 px) nor the head's give the design's size, and the skeletons' heights fail wherever it crouched or flew
# its own way (r_fly read 18.9 px). The body's area does: the squares of the body that are neither the head, the
# ntofos / clubs (teal-grey stone, cyan crystals, grey) nor the outline, against the design's (base 1242, All Out 867),
# give each pose's px a design square (body_px); the design's head goes on the matched head's middle.


def body_mask(a, head_box=None):
    """The body's lit squares: drawn, not dark (the outline), not stone (hue 165-215 with some saturation: the ntofos'
    teal-grey and cyan) nor grey; the head box left out."""
    f = a[..., :3].astype(float) / 255
    mx, mn = f.max(-1), f.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    dd = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, (60 * ((g - b) / dd) + 360) % 360,
                   np.where(mx == g, 60 * ((b - r) / dd) + 120, 60 * ((r - g) / dd) + 240))
    stone = (hue > 165) & (hue < 215) & (sat > 0.12)
    grey = (sat < 0.12) & (mx > 0.3)
    m = (a[..., 3] >= 128) & (mx > 0.28) & ~stone & ~grey
    if head_box is not None:
        x0, y0, x1, y1 = head_box
        m[max(0, y0):y1, max(0, x0):x1] = False
    return m


def body_px(name, match):
    """px a design square for a pose: the square root of its body's area over the design's."""
    st = stance_of(name)
    d = design(st)
    r0, r1, c0, c1 = STANCES[st]["head"]
    s, hx, hy = match[:3]
    a_d = body_mask(d, (c0, r0, c1, r1)).sum()
    a_p = body_mask(raw(name), (int(hx), int(hy), int(hx + (c1 - c0) * s), int(hy + (r1 - r0) * s))).sum()
    return float((a_p / a_d) ** 0.5)


def stance_of(name):
    return "ao" if name.startswith("ao_") else "base"


def design(stance):
    return np.asarray(Image.open(lp(os.path.join(OUT, STANCES[stance]["file"])))).copy()


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, f"ksante-pose-{name.replace('_', '-')}.png"))).convert("RGBA"))


def available():
    return [n for n in BASE + AO if os.path.isfile(lp(os.path.join(SRC, f"ksante-pose-{n.replace('_', '-')}.png")))]


def head_mask(stance, d):
    """The head polygon's squares that are drawn and neither gold (the earring, a pauldron's edge) nor blue (the scarf)."""
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(STANCES[stance]["poly"], fill=255)
    f = d[..., :3].astype(int)
    gold = (f[..., 0] > 140) & (f[..., 2] < 60) & (f[..., 1] > 70)
    blue = (f[..., 2] > 140) & (f[..., 0] < 110)
    return (np.asarray(img) > 0) & (d[..., 3] > 0) & ~gold & ~blue


def head_box(stance, d):
    """The head box with only the head mask's squares drawn (the matcher's mask is its alpha)."""
    r0, r1, c0, c1 = STANCES[stance]["head"]
    box = d[r0:r1, c0:c1].copy()
    box[~head_mask(stance, d)[r0:r1, c0:c1]] = 0
    return box


def matched(name, again=False):
    st = stance_of(name)
    path = lp(os.path.join(OUT, f"pose_{name}.json"))
    if not again and os.path.isfile(path):
        m = json.load(open(path, encoding="utf-8")).get("match")
        if m:
            return tuple(m)
    return SP.match_head(raw(name), head_box(st, design(st)), scales=SCALES, angles=TILTED.get(name, (0,)))


def read(name, match):
    """The pose on the design's grid with the design's head -> (figure, the head box's top-left square in it, the
    squares' size in px, the head match's cost and tilt)."""
    st = stance_of(name)
    d = design(st)
    r0, r1, c0, c1 = STANCES[st]["head"]
    hw, hh = c1 - c0, r1 - r0
    a = raw(name)
    s, hx, hy, cost, ang = match
    s2 = body_px(name, match)
    cx, cy = hx + hw * s / 2, hy + hh * s / 2
    fig, (ci, cj) = SP.sample_grid(a, s2, cx - hw * s2 / 2, cy - hh * s2 / 2)
    fig = snap(fig, d)
    hm = head_mask(st, d)
    ys, xs = np.nonzero(hm)
    pad = 24
    big = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    big[ys - r0 + cj + pad, xs - c0 + ci + pad] = d[ys, xs]
    big = SP.finish(big)
    ys2, xs2 = np.nonzero(big[..., 3] > 0)
    y0, x0 = ys2.min(), xs2.min()
    return big[y0:ys2.max() + 1, x0:xs2.max() + 1], (ci + pad + 1 - x0, cj + pad + 1 - y0), s2, cost, ang


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
    ap.add_argument("--only", help="comma-separated pose names")
    a = ap.parse_args()
    names = [n for n in available() if not a.only or n in a.only.split(",")]
    if a.measure:
        for n in names:
            st = stance_of(n)
            s, x, y, cost, ang = SP.match_head(raw(n), head_box(st, design(st)), scales=SCALES,
                                               angles=TILTED.get(n, (0,)))
            print(f"{n:14s} {s:5.2f} px a square, head at ({x}, {y}) tilted {ang}, cost {cost:.4f}")
        return
    figs = {}
    for n in names:
        m = matched(n, a.rematch)
        fig, at, s, cost, ang = read(n, m)
        figs[n] = (fig, at, m)
        print(f"{n:14s} {s:5.2f} px a square, tilt {ang}, cost {cost:.4f} -> {fig.shape[1]} x {fig.shape[0]}, head box at {at}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 5
        for st, group in (("base", BASE), ("ao", AO)):
            tiles = [("design", design(st))] + [(n, figs[n][0]) for n in group if n in figs]
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
            path = os.path.join(a.sheet, f"ksante_poses_{st}.png")
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
