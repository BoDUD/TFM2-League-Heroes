#!/usr/bin/env python3
"""Hwei's legs redo pack for Codex (assets/source/hwei/LEGS_PROMPTS.md): the poses whose legs Codex drew too long drawn
again with the design's short chibi legs - only the legs (pack_qiyana_legs.py's way: the upper body kept, the legs on
skeletons; the user, 2026-10-22: 「动作帧做到完美后再喊我review」).

    python tools/art/pack_hwei_legs.py [--out C:/t/hw_work/hwei_legs_pack] [--check DIR]
    python tools/art/pack_hwei_legs.py --pack2 --out C:/t/hw_work/hwei_legs_pack2   # q_throw, qw_point

Codex's poses (codex_poses, read back by design_hwei_poses.py at the head's scale, the design's brush put in) have the
design's head, coat, arms and brush but long legs in many: the hip to the soles 1.1-2 times the skeleton's (design
bones: thigh 8, shin 6, foot 6 squares) - q_wind 1.6, qe_raise 2.0, ew_high 1.4, r_open 1.6, run3 1.5, run4 1.4 - and
the four runs do not alternate (run1 and run3 both carry the near leg behind, run2 and run4 both stand on it). So Codex
draws the legs of POSES again on a picture that holds everything else fixed: each readback with its legs cut away is
laid on the 1254 canvas at PX px a square (the pose pack's grid, soles on y SOLE_Y), lowered so new legs of the
design's bone lengths reach the ground from its hip.
The legs to cut are found by colour (cut()): below the hip line, the trousers, the ribbon bows, the shins, the anklet,
the loafers and their outline - and every piece below the line no longer joined to the upper body (the shoes' trim);
never the brush (where the design's brush is drawn, brush_hwei.render). EXTRA polygons cut the leg colours above the
line too (the runs' old kicked-up feet). The hip: where the pose's skeleton puts the pelvis against its head box
(Codex drew the torso to the skeleton; the coat hides the hips). The legs are the pose pack's skeletons (POSES, the
design's bone lengths) from that hip; the runs set anew in RUN so the legs alternate - contact, passing, contact with the
other leg, passing - the passing frames a row higher. d_stagger's dropped brush is cut too (lowering the body would sink
it under the ground) and drawn again on the ground by design_hwei_legs.py.
Writes <out>/ (and <out>.zip): LEGS_PROMPTS.md; per pose <k>_<name>_guide.png (the upper body on the grid with the leg
lines and the ground), <k>_<name>_first.png (Codex's own first drawing: the look of the legs and of what they hid);
0_design_legs.png (the design's legs, 8x). assets/source/hwei/codex_legs_guides.json keeps where each upper body went.
--check DIR: each readback with its cut tinted, beside its guide (nothing else written).
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import brush_hwei as BR  # noqa: E402
import pack_hwei_poses as P  # noqa: E402
from design_hwei_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hwei")
PX, CANVAS, SOLE_Y = P.PX, P.CANVAS, P.SOLE_Y
GROUND = SOLE_Y // PX                     # the ground row on the canvas grid (100)
COLS = CANVAS // PX                       # 104 squares across
NAMES = ["q_wind", "qe_raise", "ew_high", "r_open", "r_fling", "ee_swing", "run1", "run2", "run3", "run4",
         "d_stagger"]
# found after the pack went out: the lunges' legs measured along the leg (hip to toe) - qw_point's back leg 29 squares,
# q_throw's 23-25, the design's reach 20 - sent as a second pack (--pack2)
NAMES2 = ["q_throw", "qw_point"]
# the legs' colours in the design's palette: trousers, ribbon bows, shins, anklet, loafers
LEG = [(19, 60, 51), (14, 34, 37), (118, 66, 39), (92, 49, 38), (146, 77, 46), (70, 34, 37), (155, 92, 46),
       (4, 162, 176), (0, 198, 220), (1, 126, 98), (0, 136, 122), (253, 223, 193), (242, 184, 148), (230, 40, 194),
       (188, 24, 190)]
INK = (10, 0, 14)
NAVY = [(19, 34, 78), (17, 42, 67), (12, 15, 38), (26, 54, 136), (37, 85, 166), (31, 70, 109)]   # the coat
# polygons (readback squares) where everything but the coat's navy is cut, above the hip line too: the runs' old feet
# kicked up behind (their loafers' gold buckles and the bows' dark teal are no leg colour of the design's), qw_point's
# old back thigh reaching out under the coat over the line (left a stick behind the shorter new leg)
EXTRA = {"run1": [(2, 50), (14, 50), (14, 53), (19, 53), (19, 61), (2, 61)],
         "run3": [(2, 54), (13, 54), (13, 57), (21, 57), (21, 65), (2, 65)],
         "qw_point": [(12, 58), (23, 58), (23, 61), (12, 61)]}
# polygons never cut: d_stagger's near hand reaching out below the hip line
KEEP = {"d_stagger": [(3, 53), (17, 53), (17, 61), (3, 61)]}
LYING = {"d_stagger"}                    # the dropped brush cut with the legs (drawn again on the ground)
BONES = (8.0, 6.0, 6.0)                  # the design's thigh, shin, foot (hd/idle.png REST)
HIPS = {"near_leg": (-4.0, 0.0), "far_leg": (4.0, 0.0)}   # the hips from the pelvis (the design's)
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
    """The first readback (long legs): hd_first/ once design_hwei_legs.py has written the joined poses over hd/."""
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


def brush_of(meta, shape):
    b = meta["brush"]
    _, m = BR.render(shape, tuple(b["grip"]), b["deg"])
    return m


def colour_is(rgb, op, cols, tol=6):
    m = np.zeros(op.shape, bool)
    for c in cols:
        m |= (np.abs(rgb - np.array(c)).sum(-1) <= tol)
    return m & op


def cut(name):
    """(readback, its legs to cut away, the hip on it, the brush's mask)."""
    rb, meta = readback(name)
    H, W = rb.shape[:2]
    rgb, op = rb[..., :3].astype(int), rb[..., 3] > 0
    px, py = hip(name, meta)
    line = int(round(py))
    brush = ndimage.binary_dilation(brush_of(meta, (H, W)), iterations=1)
    below = np.mgrid[0:H, 0:W][0] >= line
    leg = colour_is(rgb, op, LEG)
    zone = below.copy()
    m = leg & zone & ~brush
    if name in EXTRA:
        ex = poly_mask((H, W), EXTRA[name])
        zone |= ex
        m |= ex & op & ~colour_is(rgb, op, NAVY) & ~brush
    ink = colour_is(rgb, op, [INK])
    m |= ndimage.binary_dilation(m, np.ones((3, 3), bool)) & ink & zone & ~brush
    # pieces below the line no longer joined to the upper body (the loafers' trim, a bow's dark side) go with the legs
    rest = op & ~m
    lbl, n = ndimage.label(rest)
    if n:
        above = np.unique(lbl[(~below) & rest])
        keep_ids = set(above.tolist()) | set(np.unique(lbl[brush & rest]).tolist())
        for j in range(1, n + 1):
            if j not in keep_ids:
                m |= lbl == j
    if name in LYING:
        m |= brush & op
    if name in KEEP:
        m &= ~poly_mask((H, W), KEEP[name])
    return rb, m, (px, py), brush


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
    rb, m, (px, py), _ = cut(name)
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
    part = d[50:76, 10:44]
    im = Image.fromarray(up(part, 8))
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/hw_work/hwei_legs_pack")
    ap.add_argument("--check")
    ap.add_argument("--pack2", action="store_true", help="the second pack (NAMES2), numbered after the first")
    a = ap.parse_args()
    names = NAMES2 if a.pack2 else NAMES
    first_k = len(NAMES) + 1 if a.pack2 else 1
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        for name in names:
            rb, m, (px, py), _ = cut(name)
            Z = 6
            v = rb.copy()
            v[m, :3] = (v[m, :3] * 0.35 + np.array([255, 40, 40]) * 0.65).astype(np.uint8)
            im = Image.fromarray(v).resize((rb.shape[1] * Z, rb.shape[0] * Z), Image.NEAREST)
            bg = Image.new("RGBA", im.size, (235, 235, 235, 255))
            bg.alpha_composite(im)
            dr = ImageDraw.Draw(bg, "RGBA")
            dr.line([(0, round(py) * Z), (bg.width, round(py) * Z)], fill=(0, 120, 255, 255), width=2)
            dr.ellipse([px * Z - 6, py * Z - 6, px * Z + 6, py * Z + 6], fill=(0, 200, 0, 255))
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
    gpath = lp(os.path.join(SRC, "codex_legs_guides.json"))
    meta = json.load(open(gpath, encoding="utf-8")) if os.path.isfile(gpath) else {}
    for k, name in enumerate(names, first_k):
        can, keep, (ox, oy), legs = draw_guide(name)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_guide.png"))
        meta[name] = {"offset": [ox, oy], "legs": {g: [[round(x, 2), round(y, 2)] for x, y in pts]
                                                   for g, pts in legs.items()}}
        shutil.copyfile(lp(os.path.join(SRC, "codex_poses", "hwei-poses", f"hwei-pose-{name}.png")),
                        os.path.join(out, f"{k}_{name}_first.png"))
    with open(lp(os.path.join(SRC, "codex_legs_guides.json")), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)                # where each upper body went on the canvas (for the readback)
    doc = "LEGS_PROMPTS_2.md" if a.pack2 else "LEGS_PROMPTS.md"
    shutil.copyfile(lp(os.path.join(SRC, doc)), os.path.join(out, doc))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
