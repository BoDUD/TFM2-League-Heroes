#!/usr/bin/env python3
"""Qiyana's legs redo pack for Codex (assets/source/qiyana/LEGS_PROMPTS.md): her poses with the legs too long drawn again
with the design's short chibi legs - only the legs (the user, 2026-10-22: 「做到完美了喊我review」; league_galio's run
route: the upper body kept, the legs on skeletons).

    python tools/art/pack_qiyana_legs.py [--out C:/t/qy_work/qiyana_legs_pack] [--check DIR]

Codex's first poses (codex_poses, read back by design_qiyana_poses.py at the head's scale) have the design's head, torso
and ring but adult legs: hem to soles 1.3-2 times the design's 18 rows (a_wind 79 rows tall against the idle's 60, the
lunges' back legs 24-38 squares where the design's whole leg is 19, run2 seven rows taller than run1). A lossless fix by
moving pieces of its legs read as broken legs (tried, 2026-10-22), so Codex draws the legs again on a picture that holds
everything else fixed: each pose's readback with its legs cut away (CUT: a polygon on the readback, squares inside
dropped; its upper body - head, torso, arms, ring, hair - stays square for square) is laid on the 1254 canvas at PX px a
square (the pack's grid, soles on y SOLE_Y), lowered so the new legs reach the ground: the legs are skeletons at the
design's own bone lengths from Codex's pelvis (PELVIS, on the readback), their directions the first pack's
(pack_qiyana_poses.POSES; the runs set anew in RUN so the legs alternate - contact, passing, contact with the other leg,
passing), the lowest foot on the ground (or `lift` rows over it). r_leap also gets its ring cut away and drawn again at
the design's size (RING_CUT; Codex drew it 1.35 times the idle's).
Writes <out>/ (and <out>.zip): LEGS_PROMPTS.md; per pose <k>_<name>_guide.png (the upper body on the grid with the leg
lines and the ground), <k>_<name>_first.png (Codex's own first drawing, the look of its legs and of what they hid);
0_design_legs.png (the design's legs, 8x: their length, thickness and colours). The guides keep the readback's squares on
the canvas grid from (0, 0), so the delivery is read back on the same 13 px squares (design_qiyana_legs.py) and the
upper body pasted back square for square: only the legs come from the redraw.
--check DIR: each guide beside its readback with the cut drawn (nothing else written).
"""
import argparse
import math
import os
import shutil
import sys

import json

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_qiyana_poses as P  # noqa: E402
from design_qiyana_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "qiyana")
PX, CANVAS, SOLE_Y = P.PX, P.CANVAS, P.SOLE_Y
GROUND = SOLE_Y // PX                     # the ground row on the canvas grid (92)
COLS = CANVAS // PX                       # 96 squares across

# pose -> (the readback's legs to cut away: a polygon in square edges; Codex's pelvis on the readback: the hem's middle)
CUT = {
    "a_wind": ([(50, 50), (60, 50), (60, 46), (71, 45), (72, 39), (97, 39), (97, 80), (50, 80)], (66.0, 45.5)),
    "a_strike": ([(0, 44), (8, 42), (36, 41), (38, 48), (36, 66), (0, 66)], (26.0, 41.5)),
    "q_wind": ([(28, 50), (46, 47), (48, 44), (78, 42), (86, 42), (86, 61), (28, 61)], (62.0, 44.5)),
    "q_sweep": ([(0, 43), (36, 41), (60, 41), (66, 47), (67, 55), (73, 55), (73, 64), (0, 64)], (47.0, 42.5)),
    "q_end": ([(9, 44), (34, 42), (43, 42), (43, 72), (9, 72)], (21.0, 44.5)),
    "e_dash": ([(15, 37), (82, 37), (82, 50), (15, 50)], (56.0, 38.5)),
    "e_hit": ([(0, 44), (30, 41), (46, 42), (62, 45), (62, 58), (0, 58)], (35.0, 42.5)),
    "r_leap": ([(26, 69), (62, 69), (62, 97), (26, 97)], (45.0, 70.0)),
    "r_slam": ([(0, 43), (35, 41), (58, 41), (62, 46), (62, 64), (0, 64)], (42.0, 42.5)),
    "run1": ([(4, 38), (30, 37), (40, 40), (52, 44), (52, 63), (4, 63)], (32.0, 40.5)),
    "run2": ([(4, 40), (30, 38), (42, 41), (52, 46), (52, 70), (4, 70)], (32.0, 41.0)),
    "run3": ([(4, 38), (30, 37), (42, 40), (58, 44), (58, 65), (4, 65)], (34.0, 40.5)),
    "run4": ([(4, 38), (30, 37), (42, 40), (56, 44), (56, 64), (4, 64)], (33.0, 40.5)),
}
RING_CUT = {}                             # pose -> polygon of the ring to cut away and draw again (none for now)
# the design's leg bones (hd/idle.png REST): thigh, shin, foot
BONES = (8.9, 6.3, 4.0)
HIPS = {"near_leg": (-4.0, 0.7), "far_leg": (4.0, 1.2)}   # the hips from the pelvis (the design's, turned little)
# the runs, set so the legs alternate: per leg (thigh, shin, foot) directions in degrees (0 straight down, 90 forward
# = image right, -90 back), the pelvis `lift` rows over its contact height (passing frames stand a row higher)
RUN = {
    "run1": dict(far_leg=(25, 8, 80), near_leg=(-30, -100, -150), lift=None),     # contact: far leg forward
    "run2": dict(near_leg=(4, -6, 80), far_leg=(75, -10, 70), lift=1),            # passing: near leg under her
    "run3": dict(near_leg=(25, 8, 80), far_leg=(-30, -100, -150), lift=None),     # contact: near leg forward
    "run4": dict(far_leg=(4, -6, 80), near_leg=(75, -10, 70), lift=1),            # passing: far leg under her
}
COL = {"near_leg": (230, 30, 30), "far_leg": (40, 90, 230)}
SPECK = 40                                # loose pieces smaller than this (squares) after the cut are old legs' bits


def readback(name):
    """The first readback (long legs): hd_first/ once design_qiyana_legs.py has written the joined poses over hd/."""
    path = os.path.join(SRC, "hd_first", f"pose_{name}.png")
    if not os.path.isfile(lp(path)):
        path = os.path.join(SRC, "hd", f"pose_{name}.png")
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


def mask(shape, poly):
    img = Image.new("L", (shape[1] * 4, shape[0] * 4), 0)
    ImageDraw.Draw(img).polygon([(x * 4, y * 4) for x, y in poly], fill=255)
    return np.asarray(img)[2::4, 2::4] > 0


def legs_of(name):
    """(near and far leg points relative to the pelvis, lift): the first pack's skeleton's legs (at the design's bone
    lengths) or the runs' new ones."""
    if name in RUN:
        r = RUN[name]
        out = {}
        for leg in ("near_leg", "far_leg"):
            p = HIPS[leg]
            pts = [p]
            for deg, L in zip(r[leg], BONES):
                p = P.along(p, deg, L)
                pts.append(p)
            out[leg] = pts
        return out, r["lift"]
    spec = P.POSES[name][3]
    sk = P.build(spec, spec["ring"])
    pel = sk["spine"][0]
    return ({leg: [(x - pel[0], y - pel[1]) for x, y in sk[leg]] for leg in ("near_leg", "far_leg")},
            spec["lift"])


def guide(name):
    """(the upper body with its legs cut away, its top-left square on the canvas grid, the legs on the canvas grid)."""
    rb = readback(name)
    poly, pel = CUT[name]
    keep = rb.copy()
    keep[mask(rb.shape, poly)] = 0
    if name in RING_CUT:
        keep[mask(rb.shape, RING_CUT[name])] = 0
    # bits of the old legs left outside the cut (a toe, a heel's outline) go: only the body's own big piece stays
    lbl, n = ndimage.label(keep[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        size = ndimage.sum(keep[..., 3] > 0, lbl, range(1, n + 1))
        for j in range(1, n + 1):
            if size[j - 1] < SPECK:
                keep[lbl == j] = 0
    legs, lift = legs_of(name)
    low = max(y for pts in legs.values() for _, y in pts)
    # the pelvis row on the canvas: the lowest foot on the ground, or lift rows over it
    pel_row = GROUND - (lift or 0) - low
    oy = int(round(pel_row - pel[1]))
    ys, xs = np.nonzero(keep[..., 3] > 0)
    xs_all = list(xs) + [pel[0] + x for pts in legs.values() for x, _ in pts]
    ox = int(round((COLS - (max(xs_all) + min(xs_all))) / 2))
    canv_legs = {leg: [(pel[0] + x + ox, pel[1] + y + oy) for x, y in pts] for leg, pts in legs.items()}
    return keep, (ox, oy), canv_legs


def grid_canvas():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(220, 220, 220, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(220, 220, 220, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def draw_guide(name):
    keep, (ox, oy), legs = guide(name)
    can = grid_canvas()
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(keep, PX)), (ox * PX, oy * PX))
    can.alpha_composite(lay)
    sk = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(sk)
    for leg in ("far_leg", "near_leg"):
        pts = [(x * PX, y * PX) for x, y in legs[leg]]
        dr.line(pts, fill=COL[leg] + (255,), width=8, joint="curve")
        for p in pts:
            dr.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=COL[leg] + (255,))
    can.alpha_composite(sk)
    return can, keep, (ox, oy), legs


def design_legs():
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    part = d[38:60, 20:52]
    im = Image.fromarray(up(part, 8))
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/qy_work/qiyana_legs_pack")
    ap.add_argument("--check")
    a = ap.parse_args()
    names = list(CUT)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        for name in names:
            rb = readback(name)
            Z = 6
            im = Image.fromarray(rb).resize((rb.shape[1] * Z, rb.shape[0] * Z), Image.NEAREST)
            bg = Image.new("RGBA", im.size, (235, 235, 235, 255))
            bg.alpha_composite(im)
            dr = ImageDraw.Draw(bg, "RGBA")
            dr.polygon([(x * Z, y * Z) for x, y in CUT[name][0]], outline=(255, 0, 0, 255), fill=(255, 0, 0, 50))
            px, py = CUT[name][1]
            dr.ellipse([px * Z - 6, py * Z - 6, px * Z + 6, py * Z + 6], fill=(0, 200, 0, 255))
            can = draw_guide(name)[0].convert("RGB").resize((CANVAS // 2, CANVAS // 2))
            h = max(bg.height, can.height)
            t = Image.new("RGB", (bg.width + can.width + 10, h), (255, 255, 255))
            t.paste(bg.convert("RGB"), (0, 0))
            t.paste(can, (bg.width + 10, 0))
            t.save(os.path.join(a.check, f"legs_{name}.png"))
            print(name)
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    design_legs().save(os.path.join(out, "0_design_legs.png"))
    meta = {}
    for k, name in enumerate(names, 1):
        can, keep, (ox, oy), legs = draw_guide(name)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_guide.png"))
        meta[name] = {"offset": [ox, oy], "legs": {g: [[round(x, 2), round(y, 2)] for x, y in pts] for g, pts in legs.items()}}
        shutil.copyfile(lp(os.path.join(SRC, "codex_poses", f"qiyana-pose-{name}.png")),
                        os.path.join(out, f"{k}_{name}_first.png"))
    with open(lp(os.path.join(SRC, "codex_legs_guides.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)                # where each upper body went on the canvas (for the readback)
    shutil.copyfile(lp(os.path.join(SRC, "LEGS_PROMPTS.md")), os.path.join(out, "LEGS_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
