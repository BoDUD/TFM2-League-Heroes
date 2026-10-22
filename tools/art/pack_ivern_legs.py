#!/usr/bin/env python3
"""Ivern's legs redo pack for Codex (assets/source/ivern/LEGS_PROMPTS.md): the poses whose legs Codex drew too long drawn
again with the design's short chibi legs - only the legs (pack_hwei_legs.py's way: the upper body kept, the legs on
skeletons; the user, 2026-10-22: 「你处理吧 完美了喊我review」).

    python tools/art/pack_ivern_legs.py [--out C:/t/iv_work/ivern_legs_pack] [--check DIR]

Codex's poses (codex_poses, read back by design_ivern_poses.py at the head's scale) have the design's head, beard, arms,
twig and apple but long legs in the standing ones: the head box's bottom to the soles 39-46 rows against the design's
35 (a_wind 43, a_throw 41, e_give 39, q_wind 39, q_fling 41, r_call 42, r_leap 46 with an 8-row hop, run1-4 39-44),
the legs hip to sole about 21-25 squares against the design's 16 (thigh 6, shin 5, root foot 6). So Codex draws the
legs of POSES again on a picture that holds everything else fixed: each readback with its legs cut away is laid on the
1254 canvas at PX px a square (the pose pack's grid, soles on y SOLE_Y), lowered so new legs of the design's bone
lengths reach the ground from its hip.
The legs to cut are found by colour (cut()): below the hip line, the bark browns, the berries and their outline - and
every piece below the line no longer joined to the upper body; his arms are the same bark, so KEEP polygons hold the
hands, the seed, the twig and the apple that reach below the line, and EXTRA cuts a tucked knee above it. The hip: where the pose's skeleton puts the pelvis against its
head box. The legs are the pose pack's skeletons (POSES, the design's bone lengths) from that hip; the runs set anew
in RUN so the legs alternate - contact, passing, contact with the other leg, passing - the passing frames a row higher.
Writes <out>/ (and <out>.zip): LEGS_PROMPTS.md; per pose <k>_<name>_guide.png (the upper body on the grid with the leg
lines and the ground), <k>_<name>_first.png (Codex's own first drawing: the look of the legs and of what they hid);
0_design_legs.png (the design's legs, 8x). assets/source/ivern/codex_legs_guides.json keeps where each upper body went.
--check DIR: each readback with its cut tinted, beside its guide (nothing else written).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_ivern_poses as P  # noqa: E402
from design_ivern_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ivern")
PX, CANVAS, SOLE_Y = P.PX, P.CANVAS, P.SOLE_Y
GROUND = SOLE_Y // PX                     # the ground row on the canvas grid (100)
COLS = CANVAS // PX                       # 104 squares across
NAMES = ["a_wind", "a_throw", "e_give", "q_wind", "q_fling", "r_call", "r_leap", "run1", "run2", "run3", "run4"]
# the legs' colours in the design's palette: the bark browns, the berries
LEG = [(115, 52, 31), (211, 107, 55), (67, 29, 21), (155, 72, 39), (250, 24, 30), (109, 5, 11), (78, 10, 11),
       (254, 168, 128)]
INK = (2, 0, 8)
# polygons (readback squares) never cut: the hands, the twig, the seed and the apple below the hip line (--check)
KEEP = {"a_wind": [(0, 37), (17, 37), (17, 48), (0, 48)],          # the seed hand swung back low
        "r_call": [(41, 60), (57, 60), (57, 76), (41, 76)],          # the apple hand at his side
        "run4": [(0, 35), (12, 35), (12, 48), (0, 48)]}              # the twig hand swinging low
# polygons cut whole, above the hip line too: r_leap's old tucked near knee
EXTRA = {"r_leap": [(0, 50), (18, 50), (18, 66), (0, 66)]}
BONES = tuple(P.lengths("near_leg"))     # the design's thigh, shin, root foot (hd/idle.png REST)
_pel = P.REST["spine"][0]
HIPS = {leg: (P.REST[leg][0][0] - _pel[0], P.REST[leg][0][1] - _pel[1]) for leg in ("near_leg", "far_leg")}
# the runs, set so the legs alternate: per leg (thigh, shin, foot) directions in degrees (0 straight down, 90 forward
# = image right, -90 back), `lift` rows over the ground (the passing frames stand a row higher)
RUN = {
    "run1": dict(far_leg=(25, 8, 80), near_leg=(-35, -95, -150), lift=None),     # contact: the far leg forward
    "run2": dict(near_leg=(4, -4, 85), far_leg=(70, -5, 75), lift=1),            # passing: the near leg under him
    "run3": dict(near_leg=(25, 8, 80), far_leg=(-35, -95, -150), lift=None),     # contact: the near leg forward
    "run4": dict(far_leg=(4, -4, 85), near_leg=(70, -5, 75), lift=1),            # passing: the far leg under him
}
COL = {"near_leg": (230, 30, 30), "far_leg": (40, 90, 230)}


def readback(name):
    """The first readback (long legs): hd_first/ once design_ivern_legs.py has written the joined poses over hd/."""
    path = os.path.join(SRC, "hd_first", f"pose_{name}.png")
    if not os.path.isfile(lp(path)):
        path = os.path.join(SRC, "hd", f"pose_{name}.png")
    with open(lp(path[:-4] + ".json"), encoding="utf-8") as f:
        meta = json.load(f)
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy(), meta


def poly_mask(shape, poly):
    img = Image.new("L", (shape[1] * 4, shape[0] * 4), 0)
    ImageDraw.Draw(img).polygon([(x * 4, y * 4) for x, y in poly], fill=255)
    return np.asarray(img)[2::4, 2::4] > 0


def hip(name, meta):
    """The pelvis on the readback: the skeleton's pelvis against its head box, put on the readback's head box."""
    sk = P.build(P.POSES[name][3])
    hx, hy = sk["head"]
    pel = sk["spine"][0]
    ax, ay = meta["head_at"]
    return ax + pel[0] - (hx - P.HW / 2), ay + pel[1] - (hy - P.HH / 2)


def colour_is(rgb, op, cols, tol=6):
    m = np.zeros(op.shape, bool)
    for c in cols:
        m |= (np.abs(rgb - np.array(c)).sum(-1) <= tol)
    return m & op


def cut(name):
    """(readback, its legs to cut away, the hip on it)."""
    rb, meta = readback(name)
    H, W = rb.shape[:2]
    rgb, op = rb[..., :3].astype(int), rb[..., 3] > 0
    px, py = hip(name, meta)
    line = int(round(py))
    keep = poly_mask((H, W), KEEP[name]) if name in KEEP else np.zeros((H, W), bool)
    below = np.mgrid[0:H, 0:W][0] >= line
    zone = below.copy()
    m = colour_is(rgb, op, LEG) & zone & ~keep
    if name in EXTRA:                     # everything in it goes: the old knee with its outline and leaf bits
        ex = poly_mask((H, W), EXTRA[name])
        zone |= ex
        m |= ex & op
    ink = colour_is(rgb, op, [INK])
    m |= ndimage.binary_dilation(m, np.ones((3, 3), bool)) & ink & zone & ~keep
    # pieces below the line no longer joined to the upper body go with the legs
    rest = op & ~m
    lbl, n = ndimage.label(rest)
    if n:
        joined = set(np.unique(lbl[(~below) & rest]).tolist()) | set(np.unique(lbl[keep & rest]).tolist())
        for j in range(1, n + 1):
            if j not in joined:
                m |= lbl == j
    return rb, m, (px, py)


def legs_of(name):
    """(near and far leg points relative to the pelvis, lift): the pose pack's skeleton's legs (the design's bone
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
    sk = P.build(spec)
    pel = sk["spine"][0]
    return ({leg: [(x - pel[0], y - pel[1]) for x, y in sk[leg]] for leg in ("near_leg", "far_leg")},
            spec["lift"])


def guide(name):
    """(the upper body with its legs cut away, its top-left square on the canvas grid, the legs on the canvas grid)."""
    rb, m, (px, py) = cut(name)
    keep = rb.copy()
    keep[m] = 0
    legs, lift = legs_of(name)
    low = max(y for pts in legs.values() for _, y in pts)
    pel_row = GROUND - (lift or 0) - low                 # the pelvis row: the lowest foot on the ground, or lifted
    oy = int(round(pel_row - py))
    ys, xs = np.nonzero(keep[..., 3] > 0)
    xs_all = list(xs) + [px + x for pts in legs.values() for x, _ in pts]
    ox = int(round((COLS - (max(xs_all) + min(xs_all))) / 2))
    canv_legs = {leg: [(px + x + ox, py + y + oy) for x, y in pts] for leg, pts in legs.items()}
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
    part = d[38:60, 12:52]
    im = Image.fromarray(up(part, 8))
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/iv_work/ivern_legs_pack")
    ap.add_argument("--check")
    a = ap.parse_args()
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        tiles = []
        for name in NAMES:
            rb, m, (px, py) = cut(name)
            Z = 6
            v = rb.copy()
            v[m, :3] = (v[m, :3] * 0.35 + np.array([255, 40, 40]) * 0.65).astype(np.uint8)
            im = Image.fromarray(v).resize((rb.shape[1] * Z, rb.shape[0] * Z), Image.NEAREST)
            bg = Image.new("RGBA", im.size, (235, 235, 235, 255))
            bg.alpha_composite(im)
            dr = ImageDraw.Draw(bg, "RGBA")
            dr.line([(0, round(py) * Z), (bg.width, round(py) * Z)], fill=(0, 120, 255, 255), width=2)
            dr.ellipse([px * Z - 6, py * Z - 6, px * Z + 6, py * Z + 6], fill=(0, 200, 0, 255))
            for x in range(0, rb.shape[1], 5):
                dr.text((x * Z + 1, 1), str(x), fill=(0, 0, 0, 255))
            for y in range(0, rb.shape[0], 5):
                dr.text((1, y * Z + 1), str(y), fill=(0, 0, 0, 255))
            can = draw_guide(name)[0].convert("RGB").resize((CANVAS // 2, CANVAS // 2))
            h = max(bg.height, can.height)
            t = Image.new("RGB", (bg.width + can.width + 10, h), (255, 255, 255))
            t.paste(bg.convert("RGB"), (0, 0))
            t.paste(can, (bg.width + 10, 0))
            t.save(os.path.join(a.check, f"legs_{name}.png"))
            print(name, "hip", (round(px, 1), round(py, 1)), "cut", int(m.sum()))
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    design_legs().save(os.path.join(out, "0_design_legs.png"))
    meta = {}
    for k, name in enumerate(NAMES, 1):
        can, keep, (ox, oy), legs = draw_guide(name)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_guide.png"))
        meta[name] = {"offset": [ox, oy], "legs": {g: [[round(x, 2), round(y, 2)] for x, y in pts]
                                                   for g, pts in legs.items()}}
        shutil.copyfile(lp(os.path.join(SRC, "codex_poses", "ivern-poses", f"ivern-pose-{name}.png")),
                        os.path.join(out, f"{k}_{name}_first.png"))
    with open(lp(os.path.join(SRC, "codex_legs_guides.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)                # where each upper body went on the canvas (for the readback)
    shutil.copyfile(lp(os.path.join(SRC, "LEGS_PROMPTS.md")), os.path.join(out, "LEGS_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
