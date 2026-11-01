#!/usr/bin/env python3
"""The Sentry's pose pack for Codex (assets/source/sentry/POSE_PROMPTS.md): the whole-figure poses of its actions,
each laid out from the approved design's own three parts.

    python tools/art/pack_sentry_poses.py [--out D:/TFM2-Workshop/sentry_packs/sentry_pose_pack] [--lol "D:/Riot Games/League of Legends"]

The Sentry has no limbs: two crystal shards and the azure core between them. Its TFT clips (pack_sentry_picture.CLIPS)
only bob it, lift and tip it when it fires, and split the halves when it dies (measured 2026-11-02: the halves stay
28 apart in every clip but death's, which throws them ~100 apart and lays them down) - so the skills' poses (the halves
parting for the laser, splitting for Rift Leap, opening wide for Prism Sweep) are ours. Each pose is the design
(hd/idle.png: A-3, 28 x 44 at PPU 1.29, 1:1) cut into its parts - LEFT shard, RIGHT shard, CORE (part_masks) - each
moved, turned (nearest-neighbour, about its bottom tip) and the core grown by GLOW rings, then the whole lifted and
leaned: a LAYOUT guide at PX px a square on the canvas (the design's lowest point on SOLE_Y, lifted poses above it),
drawn in the design's own colours (*_layout.png) and as flat part colours (*_parts.png: red = the left shard, blue =
the right shard, yellow = the core). Where a clip has the pose, the model's frame is rendered too (*_ref.png,
same canvas and height: a_fire = attack@300, d_split = death@375, d_down = death@1125).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square), 0_parts.png (its three
parts in colour), 1_core.png (the core 12x); per pose <k>_<name>_layout.png, <k>_<name>_parts.png (+ _ref.png).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
import pose_ref  # noqa: E402
from design_sentry_hd import lp  # noqa: E402
from design_sentry_model import CORE_BOX  # noqa: E402
from pack_sentry_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sentry")
PX, CANVAS, SOLE_Y = 12, 1254, 1100
ROWS = 44                      # hd/idle.png's height
YAW, PITCH = 20, 12            # the design's angle (step 0's A)
GREY = (225, 225, 225)
PART_COL = {"L": (220, 50, 50), "R": (50, 100, 230), "C": (245, 200, 0)}
# where the left shard ends on each design row (left < SPLIT <= right), read off hd/idle.png: above the hole the
# double outline between the shards, through the hole its middle, under it the empty gap column
SPLIT = [(0, 13, 14), (13, 16, 16), (16, 18, 17), (18, 29, 15), (29, 44, 16)]
L_TIP, R_TIP = (11.5, 43.5), (19.5, 40.5)   # the shards' bottom tips (what each turns about)

# name -> (dict of moves, model clip@ms or None, what it is for (Chinese), the pose line (English))
# moves: L / R = (dx, dy, degrees clockwise: + leans its top to the right), C = (dx, dy, glow rings),
#        lift = rows off the design's ground, lean = degrees the whole turns about the lowest point, dark = core out
POSES = {
    "a_rise": ({"lift": 3, "lean": -6, "C": (0, 0, 1)}, None,
               "普攻起手：整只往上一抬、往后仰一点，蓝核亮一圈",
               "RISE - the whole figure lifted a little and tipped back slightly, the core one ring brighter."),
    "a_fire": ({"lift": 2, "lean": 10, "C": (0, 0, 2)}, "attack@300",
               "开火：往前一倾，蓝核亮两圈（光弹不画）",
               "FIRE - tipped forward, the core two rings bright (do NOT draw the bolt)."),
    "q_open": ({"lift": 2, "L": (-1, 0, -4), "R": (1, 0, 4), "C": (0, 0, 1)}, None,
               "技能1「蔚蓝激光」起手：两块石头往两边让开一点，蓝核变亮",
               "PART - the two shards easing apart a little, the core brightening."),
    "q_beam1": ({"lift": 2, "lean": 4, "L": (-2, 0, -6), "R": (2, 0, 7), "C": (1, 0, 2)}, None,
                "引导激光（循环第 1 帧）：两块石头分开、稍稍前倾，蓝核亮两圈（激光不画）",
                "LASING 1 of 2 - the shards apart, leaning forward a little, the core two rings bright (do NOT draw "
                "the laser)."),
    "q_beam2": ({"lift": 3, "lean": 4, "L": (-2, 0, -6), "R": (2, 0, 7), "C": (1, 0, 3)}, None,
                "引导激光（循环第 2 帧）：同上，整只高一格，蓝核亮三圈（一明一暗地闪）",
                "LASING 2 of 2 - the same one square higher, the core three rings bright (it pulses between the two)."),
    "e_split": ({"lift": 2, "L": (-6, 0, -10), "R": (6, 0, 12), "C": (0, 0, 1)}, None,
                "技能2「裂石跃迁」：两块石头猛地往左右分开，蓝核单独悬在中间（碎石不画）",
                "SPLIT - the two shards flung apart to the left and right, the core hanging alone between them "
                "(do NOT draw any rubble)."),
    "e_close": ({"lift": 1, "L": (-2, 0, -3), "R": (2, 0, 3)}, None,
                "合回去：两块石头往中间合拢，快贴上了",
                "CLOSING - the shards coming back together, nearly touching again."),
    "r_open": ({"lift": 3, "L": (-3, 0, -18), "R": (3, 0, 18), "C": (0, -1, 2)}, None,
               "大招「棱镜扫射」起手：两块石头上端往外张开成 V 字，蓝核亮两圈",
               "OPEN - the shards' tops swung outward into a V, the core two rings bright."),
    "r_blast": ({"lift": 3, "lean": 5, "L": (-4, 0, -26), "R": (4, 0, 26), "C": (1, -1, 4)}, None,
                "扫射：V 字张到最大，蓝核亮到发白、最大（光柱不画）",
                "BLAST - the V opened as wide as it goes, the core at its biggest, white-hot (do NOT draw the beam)."),
    **{f"run{k + 1}": ({"lift": lift, "lean": 12}, None, zh, en) for k, (lift, zh, en) in enumerate((
        (1, "飘移 1/4：整只往前倾着飘", "GLIDE 1 of 4 - leaning forward, floating along."),
        (2, "飘移 2/4：往上浮一格", "GLIDE 2 of 4 - one square higher."),
        (3, "飘移 3/4：浮到最高", "GLIDE 3 of 4 - at its highest."),
        (2, "飘移 4/4：往下回一格（4 接回 1，循环）", "GLIDE 4 of 4 - one square lower again (4 runs on into 1).")))},
    "d_split": ({"lift": 1, "L": (-3, 0, -35), "R": (4, 0, 40), "C": (0, 2, 0), "dark": 1}, "death@375",
                "被打碎：两块石头往两边倒开，蓝核变暗",
                "BREAKING - the two shards falling apart to either side, the core dimming."),
    "d_down": ({"L": "down", "R": "down", "dark": 2}, "death@1125",
               "倒地：两块石头左右各一块躺在地上，蓝核熄灭（暗灰蓝色，不发光，掉在两块中间的地上）",
               "DOWN - both shards lying on the ground, one to each side, the core gone out (a dull dark grey-blue, "
               "no glow) lying between them."),
}


# ===================== the design's parts =====================

def part_masks(d):
    """LEFT / RIGHT / CORE masks of hd/idle.png: the core = the azure and near-white squares inside CORE_BOX (the
    hole's pale blue inner wall stays on the shards), the rest split by SPLIT."""
    op = d[..., 3] > 0
    r, g, b = (d[..., k].astype(int) for k in range(3))
    yy, xx = np.mgrid[:d.shape[0], :d.shape[1]]
    x0, y0, x1, y1 = CORE_BOX
    inbox = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
    core = op & inbox & (((b > 110) & (b - r > 40)) | ((r > 190) & (g > 220) & (b > 220)))   # azure + its white middle
    split = np.zeros(d.shape[0], int)
    for a, z, s in SPLIT:
        split[a:z] = s
    left = op & ~core & (xx < split[:, None])
    return {"L": left, "R": op & ~core & ~left, "C": core}


def turn(layer, deg, about):
    """A layer turned `deg` clockwise on screen about `about` (nearest neighbour, inverse mapped: no holes)."""
    if not deg:
        return layer
    h, w = layer.shape[:2]
    pad = max(h, w)
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
    yy, xx = np.mgrid[:out.shape[0], :out.shape[1]]
    t = np.radians(deg)
    fx, fy = xx - pad + 0.5 - about[0], yy - pad + 0.5 - about[1]
    sx = np.cos(t) * fx + np.sin(t) * fy + about[0]
    sy = -np.sin(t) * fx + np.cos(t) * fy + about[1]
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    ok = (ix >= 0) & (ix < w) & (iy >= 0) & (iy < h)
    out[ok] = layer[iy[ok], ix[ok]]
    return out, pad


def glow(core, rings, dark=0):
    """The core grown by `rings` rings of bright blue, its centre whitened; dark = 1 dimmed, 2 out (grey-blue)."""
    out = core.copy()
    op = out[..., 3] > 0
    for k in range(rings):
        grow = op.copy()
        grow[1:] |= op[:-1]
        grow[:-1] |= op[1:]
        grow[:, 1:] |= op[:, :-1]
        grow[:, :-1] |= op[:, 1:]
        ring = grow & ~op
        out[ring] = (40, 150, 255, 255) if k == rings - 1 else (90, 200, 255, 255)
        op = grow
    if rings >= 3:   # white-hot middle
        ys, xs = np.nonzero(core[..., 3] > 0)
        cy, cx = ys.mean(), xs.mean()
        yy, xx = np.mgrid[:out.shape[0], :out.shape[1]]
        hot = op & ((yy - cy) ** 2 + (xx - cx) ** 2 <= (rings + 1.5) ** 2)
        out[hot] = (235, 250, 255, 255)
    if dark:
        m = out[..., 3] > 0
        rgb = out[m, :3].astype(float)
        grey = rgb.mean(1, keepdims=True)
        mix = (rgb * 0.45 + grey * 0.55) * 0.6 if dark == 1 else grey * 0.35 + np.array([18, 26, 40])
        out[m, :3] = np.clip(mix, 0, 255).astype(np.uint8)
    return out


def compose(d, masks, moves, colour=False):
    """The pose on a design-sized-plus-margin canvas: (image, its origin offset). Painting order: the far shard (right,
    it sits behind at 3/4), the core, the near shard (left)."""
    M = 40
    can = np.zeros((d.shape[0] + 2 * M, d.shape[1] + 2 * M, 4), np.uint8)
    lay = {}
    for k in ("L", "R", "C"):
        part = np.zeros_like(d)
        part[masks[k]] = d[masks[k]]
        if colour:
            part[masks[k], :3] = PART_COL[k]
        lay[k] = part
    if "dark" in moves or "C" in moves:
        cx, cy, rings = moves.get("C", (0, 0, 0))
        lay["C"] = glow(lay["C"], rings, 0 if colour else moves.get("dark", 0))
        if colour:
            lay["C"][lay["C"][..., 3] > 0, :3] = PART_COL["C"]
        lay["C"] = np.roll(lay["C"], (cy, cx), (0, 1))
    for k in ("R", "C", "L"):
        mv = moves.get(k)
        part = lay[k]
        if k in ("L", "R") and mv == "down":   # lying on the ground: a quarter turn outward, bottom tip inward
            ys, xs = np.nonzero(part[..., 3] > 0)
            sub = part[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            sub = np.rot90(sub, 1 if k == "L" else -1)
            h, w = sub.shape[:2]
            top = M + d.shape[0] - h
            left = M + (d.shape[1] // 2 - w - 1 if k == "L" else d.shape[1] // 2 + 1)
            dst = can[top:top + h, left:left + w]
            m = sub[..., 3] > 0
            dst[m] = sub[m]
            continue
        if k == "C" and moves.get("L") == "down":   # the dead core on the ground between them
            ys, xs = np.nonzero(part[..., 3] > 0)
            sub = part[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            h, w = sub.shape[:2]
            top, left = M + d.shape[0] - h, M + d.shape[1] // 2 - w // 2
            m = sub[..., 3] > 0
            can[top:top + h, left:left + w][m] = sub[m]
            continue
        dx, dy, deg = mv if (mv and k != "C") else (0, 0, 0)
        tip = L_TIP if k == "L" else R_TIP
        if deg:
            part, pad = turn(part, deg, tip)
        else:
            pad = 0
        ys, xs = np.nonzero(part[..., 3] > 0)
        ty, tx = ys - pad + M + dy, xs - pad + M + dx
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        can[ty[ok], tx[ok]] = part[ys[ok], xs[ok]]
    lean = moves.get("lean", 0)
    if lean:
        ys, xs = np.nonzero(can[..., 3] > 0)
        can, pad = turn(can, lean, ((xs.min() + xs.max() + 1) / 2, ys.max() + 1))
        can = can[pad:pad + d.shape[0] + 2 * M, pad:pad + d.shape[1] + 2 * M]
    return can, M


def grid(dr):
    for k in range(0, CANVAS, PX):
        dr.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        dr.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def on_canvas(img, M, lift, d, path):
    """A composed pose at PX a square: the design's columns centred, its ground on SOLE_Y, `lift` rows above it."""
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    grid(ImageDraw.Draw(can))
    dx = (CANVAS - d.shape[1] * PX) // 2 // PX * PX - M * PX
    dy = SOLE_Y - (d.shape[0] + M + lift) * PX
    big = Image.fromarray(img).resize((img.shape[1] * PX, img.shape[0] * PX), Image.NEAREST)
    can.alpha_composite(big, (dx, dy))
    can.convert("RGB").save(lp(path))


def render_ref(model, clip, path):
    """The model's frame at the design's angle and height (idle@0 = ROWS rows), its lowest point on SOLE_Y."""
    rest = model.posed("idle@0")
    pv = model.posed(clip).copy()
    scale = ROWS * PX / np.ptp(rest[:, 1]) * 0.98
    im = pose_ref.render_hq(pv, model.tris, model.v["uv"], model.tex, -YAW, PITCH, (CANVAS, CANVAS), scale,
                            SOLE_Y + pv[:, 1].min() * scale).transpose(Image.FLIP_LEFT_RIGHT)
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    grid(ImageDraw.Draw(can))
    can.alpha_composite(im)
    can.convert("RGB").save(lp(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\sentry_packs\sentry_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")).copy()
    assert d.shape[0] == ROWS, d.shape
    masks = part_masks(d)
    print("parts", {k: int(m.sum()) for k, m in masks.items()}, "of", int((d[..., 3] > 0).sum()))
    model = Model(a.lol)
    img, M = compose(d, masks, {})
    on_canvas(img, M, 0, d, os.path.join(a.out, "0_design.png"))
    img, M = compose(d, masks, {}, colour=True)
    on_canvas(img, M, 0, d, os.path.join(a.out, "0_parts.png"))
    x0, y0, x1, y1 = CORE_BOX
    core = Image.fromarray(d[y0:y1, x0:x1])
    bg = Image.new("RGBA", core.size, GREY + (255,))
    bg.alpha_composite(core)
    bg.convert("RGB").resize((core.width * 12, core.height * 12), Image.NEAREST).save(lp(os.path.join(a.out, "1_core.png")))
    for k, (name, (moves, clip, _zh, _en)) in enumerate(POSES.items()):
        stem = os.path.join(a.out, f"{k + 2}_{name}")
        lift = moves.get("lift", 0)
        img, M = compose(d, masks, moves)
        on_canvas(img, M, lift, d, stem + "_layout.png")
        img, M = compose(d, masks, moves, colour=True)
        on_canvas(img, M, lift, d, stem + "_parts.png")
        if clip:
            render_ref(model, clip, stem + "_ref.png")
        print(stem, moves, clip or "")
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
