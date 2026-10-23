#!/usr/bin/env python3
"""Bel'Veth's pose pack for Codex (assets/source/belveth/POSE_PROMPTS.md): the whole-body poses her League clips go
through - her wing-arms (folded like a cloak in the design) raised, swung and spread, her tail raised and slammed
(pack_singed_poses.py's way, with wings and a tail in place of arms, legs and a plate).

    python tools/art/pack_belveth_poses.py [--out C:/t/bv_work/belveth_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, the claws on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-1 cut
to 82 rows, 86 x 82, PPU 1.75) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's
frames (tools/lol/pose_ref.py at the 3/4 camera; ours keep the face to the front-right): every bone at the design's OWN
length (measured on hd/idle.png at 11x: REST), only its direction set per pose (POSES), the lowest claw (or the tail
lying on the ground) on the ground unless the pose lifts her (she hovers in League: `lift`). No run here: she glides,
so the move is rigged from the design (rig_belveth.py).
THE HEAD (hd/idle.png rows 11-31, columns 46-67: the crest, the gold ornament, the face, the chin) is pasted on every
pose upright, never turned. THE COLLAR (the two tall shoulder spikes and the high collar round the head: the design's
squares above row 31 outside the head box) is rigid: moved with the neck, drawn translucent on the skeletons.
THE WINGS are her arms: each a chain shoulder -> elbow -> wrist -> tip along the wing's leading edge (in the design they
hang down round her as the cloak: the near one's edge ends at the cloak's lower left, the far one's at its lower
right); the membrane spans from that edge to her body (drawn as a translucent sheet to the hem).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png; 1_head.png (8x); 2_design.png; per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (the hem's middle to the base of the neck), ORANGE = the NEAR wing's edge (image
left) with its translucent teal membrane, PURPLE = the FAR wing's edge (image right), MAGENTA = the tail (from its root
at the back of the hem to its tip), PINK = the claws (near and far), grey box = the head, the translucent violet shape =
the collar and the shoulder spikes.
"""
import argparse
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_belveth_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "belveth")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
GROUND = 82                        # the design's claws' bottom edge (rows)
DX, DY = 14, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its claws on row 108)
COL = {"spine": (0, 170, 60), "near_wing": (255, 140, 0), "far_wing": (150, 60, 200), "tail": (230, 0, 200),
       "near_claw": (255, 120, 200), "far_claw": (255, 120, 200), "membrane": (40, 120, 140)}
HEAD = (11, 31, 46, 67)            # rows / columns of the head in hd/idle.png (ends exclusive): the crest to the chin
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 21 x 20 squares
FACE = (53, 65, 17, 30)            # the face (the eyes, the chin): x0, x1, y0, y1 in design squares
COLLAR_ROW = 31                    # the collar and the spikes: the design's squares above this row outside the head box


def collar_mask(d):
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r0, r1, c0, c1 = HEAD
    inside = (yy >= r0) & (yy < r1) & (xx >= c0) & (xx < c1)
    return (yy < COLLAR_ROW) & (d[..., 3] > 0) & ~inside


# the design's own skeleton, measured on hd/idle.png (86 x 82, square edges): the head box's middle; the spine from the
# hem's middle to the base of the neck; each wing's leading edge shoulder (the orb), elbow (the gold joint on the near
# side), wrist, tip (the cloak's lower corner); the claws' roots under the hem and their tips; the tail's root at the back
# of the hem to its tip on the ground at the far left
REST = {
    "head": (56.5, 21.0),
    "spine": [(57.0, 60.0), (56.0, 31.0)],
    "near_wing": [(48.0, 33.0), (39.0, 33.0), (36.0, 47.0), (32.0, 68.0)],
    "far_wing": [(66.0, 34.0), (71.0, 44.0), (76.0, 58.0), (84.0, 76.0)],
    "near_claw": [(52.0, 66.0), (49.0, 73.0), (47.0, 80.0)],
    "far_claw": [(66.0, 66.0), (68.0, 73.0), (70.0, 80.0)],
    "tail": [(42.0, 70.0), (32.0, 77.0), (20.0, 78.0), (8.0, 77.0), (2.0, 72.0)],
}
LIMBS = ("near_wing", "far_wing", "near_claw", "far_claw", "tail")
TOP_LIMBS = ("near_wing", "far_wing")   # rooted at the neck (turned with the spine); the rest at the hem (half)

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# hem's middle "pelvis" (design squares), "lift" (rows the lowest claw is off the ground; None: on it), "shift" (squares
# the whole figure is moved on the canvas), the spine's direction and every limb as "rest" or its bones' directions
# (degrees: 0 straight down, 90 to the image right, 180 up, -90 to the image left), each bone at the design's length.
POSES = {
    "a_wind": ("attack_slow1a@100",
               "举翼：身子微微往后（画面左边）仰，近侧的膜翼（画面左边）高高举到头的左上方、翼尖朝上像一把刀（翼膜张开，不挡脸），远侧的膜翼照定稿垂着裹在身上（普攻起手）",
               "WIND-UP - leaning back a little to the image left, the NEAR wing-arm (image left) raised high up beside her "
               "head on the image left, its tip pointing up like a blade, the membrane opened (never over the face); the far "
               "wing still folded round her as in the design.",
               dict(pelvis=(57.0, 60.0), lift=None, shift=2, spine=-172, near_wing=(-110, -150, -175),
                    far_wing="rest", near_claw="rest", far_claw="rest", tail="rest")),
    "a_slash": ("attack_slow1a@333",
                "劈下：身子往前（画面右边）压，近侧的膜翼从上往下劈到身前右下方（翼尖朝右下，从胸口下面扫过去，不挡脸），远侧的膜翼收在身后（普攻打中）",
                "THE SLASH - leaning forward to the image right, the NEAR wing-arm brought down across her front to the "
                "lower right (its tip to the lower right, sweeping below her chest, never over the face); the far wing "
                "drawn back behind her.",
                dict(pelvis=(57.0, 60.0), lift=None, shift=-4, spine=165, near_wing=(70, 110, 130),
                     far_wing=(-10, -20, -15), near_claw="rest", far_claw="rest", tail="rest")),
    "q_dash": ("q_spell1@133",
               "突进：整个身子几乎放平往前（画面右边）冲，头在最前面（脸照样朝右前方），两只膜翼往后收紧贴着身子、翼尖拖在身后左边，尾巴在身后拉直，爪子往后拖，离地飘着（虚空激流）",
               "THE DASH - the whole body almost level, rushing forward to the image right with the head in front (the "
               "face still to the front-right), both wing-arms swept back tight along her body with their tips trailing "
               "behind on the image left, the tail stretched straight out behind, the claws trailing back; flying low "
               "off the ground.",
               dict(pelvis=(50.0, 64.0), lift=6, shift=6, spine=118, near_wing=(-80, -95, -100),
                    far_wing=(-70, -85, -95), near_claw=(-60, -70), far_claw=(-50, -60), tail=(-90, -92, -95, -100))),
    "w_coil": ("spell2_0@489",
               "扬尾：身子往后（画面左边）仰，尾巴从身后高高扬起、绕过她背后翘到头的左上方（尾尖朝右，不挡脸），两只膜翼照定稿裹在身上（上觐沉渊：起手）",
               "THE COIL - leaning back to the image left, the TAIL raised high from behind her, arching up past her back "
               "to above her head on the image left (its tip curling to the right, never over the face); both wings "
               "folded round her as in the design.",
               dict(pelvis=(57.0, 60.0), lift=None, shift=4, spine=-165, near_wing="rest", far_wing="rest",
                    near_claw="rest", far_claw="rest", tail=(-160, 180, 170, 140))),
    "w_slam": ("spell2_0@733",
               "砸地：身子往前（画面右边）压，尾巴从她身下甩到身前右边、平平地砸在地上（尾尖在最右边），两只膜翼往身后上方张开保持平衡（近侧的在左上、远侧的在右上，都不挡脸）（上觐沉渊：砸地）",
               "THE SLAM - leaning forward to the image right, the TAIL swung under her to the front and SLAMMED flat on "
               "the ground on the image right (its tip furthest right), both wing-arms opened up behind her for balance "
               "(the near one to the upper left, the far one to the upper right, never over the face).",
               dict(pelvis=(55.0, 60.0), lift=None, shift=-8, spine=160, near_wing=(-110, -140, -160),
                    far_wing=(135, 155, 175), near_claw="rest", far_claw="rest", tail=(35, 70, 85, 90))),
    "e_spin1": ("spell3_attack_slow@200",
                "旋风·收：微微离地，两只膜翼在身体两边竖直举起、翼尖朝上高过肩刺（像两把竖起的刀，不挡脸），尾巴绕在身下（搠面皇锋：旋转）",
                "THE STORM, UP - lifted a little off the ground, BOTH wing-arms raised straight up along her sides, their "
                "tips above the shoulder spikes (two blades standing up, never over the face), the tail curled under her.",
                dict(pelvis=(57.0, 60.0), lift=4, shift=0, spine=180, near_wing=(-140, -175, 170),
                     far_wing=(140, 175, -170), near_claw=(-10, 0), far_claw=(10, 0), tail=(-60, -100, -120, -150))),
    "e_spin2": ("spell3_attack_slow@600",
                "旋风·扫：微微离地，两只膜翼往两边斜向下张开横扫（翼尖在左下和右下），身子挺直，尾巴绕在身下（搠面皇锋：横扫）",
                "THE STORM, OUT - lifted a little off the ground, BOTH wing-arms spread out and down to the sides, slashing "
                "(the tips to the lower left and the lower right), the body upright, the tail curled under her.",
                dict(pelvis=(57.0, 60.0), lift=4, shift=-4, spine=180, near_wing=(-45, -40, -35),
                     far_wing=(45, 40, 35), near_claw=(-10, 0), far_claw=(10, 0), tail=(-60, -100, -120, -150))),
    "r_curl": ("spell4@1111",
               "蜷缩：身子往前弓、压低，两只膜翼收拢交叉裹在身前腰下（不挡脸），爪子弯着（万载豪筵：吞下珊瑚、蜕变前）",
               "THE CURL - hunched forward and low, both wing-arms drawn in and crossed round the front of her lower body "
               "(below the face), the claws bent.",
               dict(pelvis=(57.0, 63.0), lift=None, shift=0, spine=160, near_wing=(60, 30, 10),
                    far_wing=(-30, -20, -10), near_claw=(-40, 10), far_claw=(40, -10), tail="rest")),
    "r_rise": ("spell4@2778",
               "展开：离地升起、挺直，两只膜翼往两边高高张开（翼尖在头的左上和右上，不挡脸），尾巴在身后扬起（万载豪筵：化为真身）",
               "THE RISE - rising off the ground, tall and upright, BOTH wing-arms spread high and wide (the tips above "
               "her head to the upper left and upper right, never over the face), the tail raised behind her.",
               dict(pelvis=(57.0, 60.0), lift=5, shift=0, spine=180, near_wing=(-140, -160, -150),
                    far_wing=(140, 160, 150), near_claw=(-15, -5), far_claw=(15, 5), tail=(-100, -130, -150, -170))),
    "d_reel": ("death@622",
               "踉跄：身子往后（画面左边）倒，两只膜翼无力地往两边垂下张开，尾巴软软地拖在地上（死亡第一下）",
               "REELING - falling back to the image left, both wing-arms drooping open to the sides, the tail limp on the "
               "ground.",
               dict(pelvis=(58.0, 61.0), lift=None, shift=2, spine=-155, near_wing=(-50, -30, -20),
                    far_wing=(40, 30, 20), near_claw="rest", far_claw="rest", tail="rest")),
    "d_down": ("death@1244",
               "倒下：身子瘫软沉到地上、往后仰，两只膜翼摊平铺在地上两边，尾巴软软地拖在地上（死亡）",
               "DOWN - sunk limp to the ground and leaning back, both wing-arms spread flat on the ground at her sides, the "
               "tail lying limp.",
               dict(pelvis=(57.0, 70.0), lift=None, shift=-2, spine=-150, near_wing=(-70, -80, -90),
                    far_wing=(40, 60, 80), near_claw=(-60, -80), far_claw=(60, 80), tail="rest")),
}


def ang(a, b):
    """The direction a -> b in degrees (0 = straight down, 90 = to the image right; y down)."""
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def along(p, deg, length):
    r = math.radians(deg)
    return (p[0] + length * math.sin(r), p[1] + length * math.cos(r))


def turned(v, deg):
    """A vector turned the way ang() counts: +deg turns straight down towards the image right."""
    r = math.radians(deg)
    x, y = v
    return (x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r))


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the wings' shoulders where the design has them
    by the neck, turned with the spine, the claws' and the tail's roots by the hem turned half as much; the head box
    upright over the neck (the head is pasted, never turned), the collar with the neck. The lowest claw (or tail) on
    the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1]),
          "neck_shift": (neck[0] - rs[1][0], neck[1] - rs[1][1])}
    for name in LIMBS:
        top = name in TOP_LIMBS
        base, base_rest, k = (neck, rs[1], 1.0) if top else (pel, rs[0], 0.5)
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        assert len(sp) == len(lengths(name)), (name, sp)
        for a_, l_ in zip(sp, lengths(name)):
            pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for name in ("near_claw", "far_claw", "tail") for _, y in sk[name])
    dy = REST["near_claw"][-1][1] - (spec["lift"] or 0) - low
    moved = {}
    for k, v in sk.items():
        if k in ("head", "neck_shift"):
            moved[k] = (v[0], v[1] + dy)
        else:
            moved[k] = [(x, y + dy) for x, y in v]
    return moved


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k == "neck_shift":
            out[k] = v
        else:
            out[k] = [(x + DX + shift, y + DY) for x, y in v]
    out["origin"] = (DX + shift + out["neck_shift"][0], DY + out["neck_shift"][1])
    return out


def canvas_grid():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def c(p):
    """A point in design square edges, already on the canvas grid, in canvas px."""
    return (p[0] * PX, p[1] * PX)


def collar_layer(idle, origin, alpha):
    """The design's collar and shoulder spikes, moved with the neck (origin: the design's (0, 0) on the canvas grid)."""
    m = collar_mask(idle)
    lay = np.zeros(idle.shape[:2] + (4,), np.uint8)
    lay[m] = (150, 40, 150, alpha)
    im = Image.fromarray(up(lay, PX))
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(im, (round(origin[0] * PX), round(origin[1] * PX)))
    return out


def skeleton(can, s, label, idle, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    can.alpha_composite(collar_layer(idle, s["origin"], 110 if alpha == 255 else 70))
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    for w in ("far_wing", "near_wing"):   # the membranes: from the wing's edge back to the hem's middle
        dr.polygon([c(p) for p in s[w]] + [c(s["spine"][0])], fill=COL["membrane"] + (60 if alpha == 255 else 35,))
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("tail", "far_claw", "far_wing", "spine", "near_claw", "near_wing"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for p in pts:
            rr = 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work):
    """League's frame at the 3/4 camera."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Belveth",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
           "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone and head box on the canvas; no wing over the face."""
    out = []
    pts = [p for k in ("spine",) + LIMBS for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1:
        out.append("head off the top")
    fx0, fx1 = hx + FACE[0] - REST["head"][0], hx + FACE[1] - REST["head"][0]
    fy0, fy1 = hy + FACE[2] - REST["head"][1], hy + FACE[3] - REST["head"][1]
    over = []
    for w in ("near_wing", "far_wing", "tail"):   # every point along the edges, a twentieth of a bone apart
        for p, q in zip(s[w], s[w][1:]):
            over += [(p[0] + (q[0] - p[0]) * f / 20, p[1] + (q[1] - p[1]) * f / 20) for f in range(21)]
    face = [p for p in over if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/bv_work/belveth_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]),
                                **{k: "rest" for k in LIMBS})))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", idle, 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        names = a.only.split(",") if a.only else list(poses)
        cache = os.path.join(a.check, "_league")
        os.makedirs(cache, exist_ok=True)
        tiles = []
        for name in names:
            s, frame, zh, en = poses[name]
            can = canvas_grid()
            hx, hy = s["head"]                       # the design's head in its box, to judge the proportions
            r0, r1, c0, c1 = HEAD
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name, idle)
            fpath = os.path.join(cache, name + ".png")
            if not os.path.isfile(fpath):
                lol_frame(a.lol, frame, os.path.join(a.check, "_work")).save(fpath)
            lf = Image.open(fpath).convert("RGB")
            sk = can.convert("RGB").resize((CANVAS * 2 // 5, CANVAS * 2 // 5))
            lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
            t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(lf, (sk.width, 0))
            tiles.append(t)
        W = max(t.width for t in tiles)
        cols = 3
        rows_ = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (W * cols, tiles[0].height * rows_), (255, 255, 255))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % cols) * W, (k // cols) * t.height))
        sheet.save(os.path.join(a.check, "poses_check.png"))
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", idle, 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (claws on y {SOLE_Y})", idle)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
