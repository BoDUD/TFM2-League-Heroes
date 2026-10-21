#!/usr/bin/env python3
"""Shyvana's pose pack for Codex (assets/source/shyvana/POSE_PROMPTS.md): the whole-body poses her human form goes
through in League's clips that the 3/4 design cannot give by moving its own parts - the jumping slashes, Emberstrike's
somersault and tail sweep, the throw, the leap into the dragon, the fall (the user, 2026-10-21: 「做到完美后喊我review
如果有动作实在做不出 就让codex帮忙」; Sylas's / Warwick's skeleton way).

    python tools/art/pack_shyvana_poses.py [--out C:/t/sv_work/shyvana_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at 14 px a square, soles on y 1176 - the design hd/idle.png (Codex's step-1 A-2, 40 x 63)
sits at squares (DX, DY) on it. The skeletons are set by hand after League's frames (League's joints moved onto the design
bone by bone - tools/lol/league_joints.py on assets/source/shyvana/poses.json - came out wrong wherever she turns or
tumbles: bones seen end-on, the head under the neck): every bone at the design's OWN length (measured on hd/idle.png:
REST), only its direction set per pose (POSES), the feet on the ground unless the pose lifts them.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its horn crown, 8x: every pose wears it); 2_design.png (the design on the grid);
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left) to its claws, PURPLE = the FAR arm (image right), YELLOW = the tail
(from its root behind the hips to its golden tip); grey box = the head (the design's head, never redrawn).
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
from design_shyvana_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shyvana")
PX, CANVAS, SOLE_Y = 14, 1254, 1176
GREY = (225, 225, 225)
GROUND = 63                        # the design's soles' bottom edge (rows)
DX, DY = 24, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 84)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "tail": (240, 210, 0)}
HEAD = (0, 21, 13, 40)             # rows / columns of the head with its horn crown in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 27 x 21 squares

# the design's own skeleton, measured on hd/idle.png (40 x 63, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the claws' tip; each leg hip, knee, ankle, toes; the tail from its
# root behind the near hip to its golden tip
REST = {
    "head": (26.5, 10.5),
    "spine": [(24.5, 41.0), (25.0, 22.0)],
    "near_arm": [(19.0, 24.0), (16.0, 31.0), (15.0, 37.0), (14.0, 40.5)],
    "far_arm": [(31.5, 23.0), (34.5, 30.5), (35.5, 36.0), (36.5, 40.5)],
    "near_leg": [(19.5, 42.0), (18.5, 50.0), (15.5, 57.0), (13.5, 62.5)],
    "far_leg": [(29.5, 42.0), (31.5, 50.0), (33.5, 57.0), (36.5, 62.5)],
    "tail": [(13.0, 39.0), (8.0, 43.0), (4.0, 47.5), (2.5, 51.5), (4.0, 55.0), (8.5, 56.5)],
}

# the poses: name -> (League's frame (clip@ms, poses.json's clips), what it is for (Chinese), the pose line (English),
# the skeleton: the pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), the spine's
# direction and every bone's (degrees: 0 straight down, 90 to the image right, 180 up, -90 to the image left) - each bone
# at the design's own length (REST), so a limb is never stretched or shortened
POSES = {
    "crouch": ("attack1_start@0", "蓄势下蹲：两腿深蹲，身子压低前倾，两只爪子收在胸前，尾巴在身后卷起（普攻、E、R 的起手）",
               "CROUCH - both knees deeply bent, the body low and leaning forward, both clawed hands held up before her "
               "chest, the tail curled up behind her.",
               dict(pelvis=(24.0, 49.0), lift=None, spine=150, near_arm=((35.0, 38.0), 1, 100), far_arm=((42.0, 36.0), 1, 95),
                    near_leg=((18.0, 57.5), -1, -20), far_leg=((31.0, 57.5), -1, 25), tail=(-60, -25, -80, -140, -175))),
    "rise": ("attack1_start@280", "扬爪：身子挺直往上，远侧手臂高高举过头顶，近侧手臂垂在身侧，两腿前后分开，尾巴平甩在身后（普攻出手前、Q 一段起手）",
             "RISE - standing tall and reaching up, the FAR arm raised high over her head with the claws open, the near "
             "arm down at her side, the legs apart (the near leg bent behind, the far leg straight), the tail swung out "
             "level behind her.",
             dict(pelvis=(24.5, 40.0), lift=None, spine=175, near_arm=((17.0, 37.0), 1, -10), far_arm=((35.0, 8.0), 1, 165),
                  near_leg=((15.0, 56.5), -1, -20), far_leg=((32.5, 56.5), -1, 25), tail=(-95, -92, -88, -95, -120))),
    "slash": ("spell1_attack1@390", "挥爪横斩：落地两腿大开蹲低，身子前倾，远侧手臂往前下方斩到身前（爪子在腰的高度），近侧手臂垂在身后，尾巴往后上方扬起（普攻命中、Q 一段命中）",
              "SLASH - landed in a wide low stance, the body leaning forward, the FAR arm slashed forward and down so "
              "its claws end in front of her at waist height, the near arm hanging back, the tail raised up and back "
              "behind her.",
              dict(pelvis=(24.0, 47.0), lift=None, spine=140, near_arm=((19.0, 41.0), 1, -20), far_arm=((46.0, 42.0), 1, 70),
                   near_leg=((13.0, 57.0), -1, -30), far_leg=((35.0, 57.5), -1, 30), tail=(-120, -140, -155, -160, -140))),
    "flip": ("spell1_attack2_start@280", "空翻：在空中蜷成一团往前翻，两膝收到胸前，头埋向前下方，尾巴从背后绕过头顶划一道大弧（Q 二段起手）",
             "FLIP - curled up in the air somersaulting forward, both knees pulled up to the chest, the head tucked "
             "forward and down, the tail swinging from her back up over the top of her head in a big arc.",
             dict(pelvis=(24.0, 38.0), lift=9, spine=150, near_arm=((28.0, 40.0), 1, 60), far_arm=((31.0, 41.0), 1, 60),
                  near_leg=((21.0, 43.0), -1, 60), far_leg=((27.0, 44.0), -1, 60), tail=(-160, 170, 140, 110, 95))),
    "sweep": ("spell1_attack2_hit@150", "落地甩尾：蹲得很低，远侧手臂往前上方扬起、近侧手臂弯在胸前，尾巴贴着地面往前扫到身前（Q 二段命中）",
              "SWEEP - landed in a very low crouch, the FAR arm flung up and forward, the near arm bent before her "
              "chest, the tail sweeping forward low along the ground in front of her.",
              dict(pelvis=(23.0, 50.0), lift=None, spine=155, near_arm=((32.0, 36.0), 1, 140), far_arm=((44.0, 22.0), 1, 135),
                   near_leg=((14.0, 58.0), -1, -30), far_leg=((32.0, 58.0), -1, 30), tail=(10, 60, 85, 92, 95))),
    "throw": ("spell3@360", "掷出火球：两腿前后弓步，身子前倾，远侧手臂朝前伸直（爪子张开，和肩一样高），近侧手臂往身后拉直，尾巴平伸在身后（E 爆炎吐息）",
              "THROW - a forward lunge, the body leaning forward, the FAR arm thrust straight forward at shoulder height "
              "with the claws open, the near arm pulled straight back behind her, the tail stretched out level behind.",
              dict(pelvis=(23.5, 44.0), lift=None, spine=160, near_arm=((5.0, 26.0), -1, -95), far_arm=((46.0, 25.0), 1, 90),
                   near_leg=((12.0, 57.5), -1, -40), far_leg=((33.0, 57.5), -1, 30), tail=(-95, -90, -88, -92, -110))),
    "leap": ("spell4_cast@260", "腾空跃起：整个人往上跃起离地（脚离地约 10 格），身子挺直、头仰起，近侧手臂往后下方甩、远侧手臂弯在身前，两腿在下面拖着，尾巴垂在身后（R 起跳，在空中化龙）",
             "LEAP - launching straight up into the air (the feet about 10 squares above the ground), the body "
             "stretched tall, the head up, the near arm swept down and back, the far arm bent before her, both legs "
             "trailing below, the tail hanging down behind her.",
             dict(pelvis=(24.5, 32.0), lift=10, spine=178, near_arm=((12.0, 34.0), 1, -40), far_arm=((36.0, 30.0), 1, 150),
                  near_leg=((22.0, 47.0), -1, -10), far_leg=((28.0, 46.0), -1, 20), tail=(-30, -10, 0, 5, 20))),
    "stagger": ("death@250", "中招后仰：两腿大开站着，身子往后仰、头往后甩，两只手臂往两边甩开，尾巴从身后甩到肩膀上方（死亡第一下）",
                "STAGGER - struck: standing with the legs wide apart, bending back, the head thrown back, both arms "
                "flung out to both sides, the tail whipped up behind her above the shoulder.",
                dict(pelvis=(25.0, 41.0), lift=None, spine=-165, near_arm=((6.0, 22.0), -1, -100), far_arm=((44.0, 20.0), 1, 95),
                     near_leg=((14.0, 56.5), -1, -25), far_leg=((36.0, 56.5), 1, 30), tail=(-170, 165, 140, 115, 100))),
    "kneel": ("death@750", "跪倒：两膝往里弯、身子往下塌，头往后仰，远侧手臂往前伸、近侧手臂垂着，尾巴拖在身后（死亡第二下）",
              "KNEEL - the knees buckling inwards, the body sinking down, the head tipped back, the far arm reaching "
              "forward, the near arm hanging, the tail trailing behind her.",
              dict(pelvis=(25.0, 47.0), lift=None, spine=-175, near_arm=((18.0, 42.0), 1, 0), far_arm=((41.0, 30.0), 1, 90),
                   near_leg=((17.0, 57.5), -1, -20), far_leg=((33.0, 57.5), 1, 25), tail=(-70, -60, -85, -100, -110))),
    "collapse": ("death@1600", "伏倒：跪着往前趴，两只手撑在身前地上，头低到地面附近（朝画面右边），尾巴贴着地面伸在身后（死亡）",
                 "COLLAPSE - fallen forward onto both knees and both hands, the head low near the ground at the image "
                 "right, the tail lying along the ground stretched out behind her.",
                 dict(pelvis=(19.0, 51.0), lift=None, spine=110, near_arm=((38.0, 58.0), 1, 80), far_arm=((43.0, 58.0), 1, 80),
                      near_leg=((10.0, 61.0), -1, -95), far_leg=((16.0, 61.0), -1, -95), tail=(-95, -92, -90, -95, -105))),
    "run1": ("run@0", "跑步 1（近侧腿在前着地）：身子前倾，远侧手臂往前摆、近侧手臂往后摆，尾巴平伸在身后",
             "RUN 1 - running leaning forward: the NEAR leg forward with its foot landing, the far leg pushing off "
             "behind, the far arm swinging forward, the near arm swinging back, the tail stretched out level behind.",
             dict(pelvis=(24.5, 41.0), lift=None, spine=160, near_arm=((12.0, 34.0), -1, -60), far_arm=((38.0, 33.0), 1, 90),
                  near_leg=((30.0, 57.0), -1, 30), far_leg=((14.0, 55.0), -1, -60), tail=(-100, -95, -90, -95, -110))),
    "run2": ("run@225", "跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，尾巴平伸在身后",
             "RUN 2 - running: the near leg under the body carrying her, the far knee lifted forward, the body one "
             "square higher, the arms at her sides, the tail level behind.",
             dict(pelvis=(24.5, 40.0), lift=None, spine=162, near_arm=((17.0, 37.0), 1, -10), far_arm=((34.0, 37.0), 1, 10),
                  near_leg=((23.0, 57.5), -1, 0), far_leg=((33.0, 49.0), -1, 40), tail=(-100, -95, -90, -95, -110))),
    "run3": ("run@450", "跑步 3（远侧腿在前着地）：近侧手臂往前摆（在下巴下面，不挡脸）、远侧手臂往后摆，尾巴平伸在身后",
             "RUN 3 - running leaning forward: the FAR leg forward with its foot landing, the near leg pushing off "
             "behind, the near arm swinging forward (below the chin, never over the face), the far arm swinging back, "
             "the tail level behind.",
             dict(pelvis=(24.5, 41.0), lift=None, spine=160, near_arm=((32.0, 34.0), 1, 90), far_arm=((24.0, 36.0), -1, -40),
                  near_leg=((12.0, 55.0), -1, -60), far_leg=((33.0, 57.0), -1, 35), tail=(-100, -95, -90, -95, -110))),
    "run4": ("run@675", "跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，尾巴平伸在身后",
             "RUN 4 - running: the far leg under the body carrying her, the near knee lifted forward, the body one "
             "square higher, the arms at her sides, the tail level behind.",
             dict(pelvis=(24.5, 40.0), lift=None, spine=162, near_arm=((17.0, 37.0), 1, -10), far_arm=((34.0, 37.0), 1, 10),
                  near_leg=((27.0, 49.0), -1, 40), far_leg=((26.0, 57.5), -1, 10), tail=(-100, -95, -90, -95, -110))),
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


def bend(H, A, l1, l2, side):
    """The middle joint of a two-bone limb from H towards A (A pulled in or pushed out to what the bones reach): `side`
    +1 bulges it to the right of the line H -> A as seen walking along it... in screen terms: to the image right of a
    limb pointing down, below a limb pointing right (rig_zyra.knee's `forward`)."""
    vx, vy = A[0] - H[0], A[1] - H[1]
    d = math.hypot(vx, vy) or 1e-9
    d2 = max(abs(l1 - l2) + 0.3, min(l1 + l2 - 0.05, d))
    ux, uy = vx / d, vy / d
    a = (l1 * l1 - l2 * l2 + d2 * d2) / (2 * d2)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = -uy, ux
    if side < 0:
        px, py = -px, -py
    M = (H[0] + ux * a + px * h, H[1] + uy * a + py * h)
    return M, (H[0] + ux * d2, H[1] + uy * d2)


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips and the tail's root turned half as much (the hips turn less than the
    chest); the head box upright over the neck (the head is pasted, never turned). An arm or a leg is either three
    angles, or (target, side, last angle): the wrist / ankle put at the target (design squares, before the ground is
    set) with the elbow / knee solved at the design's lengths and bulging to `side`, then the claws / the foot at the
    last angle. The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0    # the shorter way round (-165 is 16.5 past up)
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("near_arm", neck, rs[1], 1.0), ("far_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5),
                                     ("tail", pel, rs[0], 0.5)):
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(name)
        sp = spec[name]
        if len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for leg in ("near_leg", "far_leg") for _, y in sk[leg])
    dy = REST["near_leg"][-1][1] - (spec["lift"] or 0) - low
    return {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}


def to_canvas(sk):
    return {k: ((v[0] + DX, v[1] + DY) if k == "head" else [(x + DX, y + DY) for x, y in v]) for k, v in sk.items()}


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


def skeleton(can, s, label, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("tail", 7), ("far_leg", 7), ("far_arm", 7), ("spine", 7), ("near_leg", 7), ("near_arm", 7)]
    for name, w in order:
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=w, joint="curve")
        for p in pts:
            r = 6
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Shyvana",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.4",
           "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work, "--frame", frame]
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
    return {name: (to_canvas(build(spec)), frame, zh, en) for name, (frame, zh, en, spec) in POSES.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/sv_work/shyvana_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--frames", help="League's frames already rendered here as <name>.png (lol_frame's look)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(REST)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        tiles = []
        for name, (s, frame, zh, en) in poses.items():
            can = canvas_grid()
            skeleton(can, s, name)
            if a.frames and os.path.isfile(os.path.join(a.frames, name + ".png")):
                lf = Image.open(os.path.join(a.frames, name + ".png")).convert("RGB")
            else:
                lf = lol_frame(a.lol, frame, os.path.join(a.check, "_work"))
            sk = can.convert("RGB").crop((0, 300, CANVAS, SOLE_Y + 40)).resize((CANVAS * 2 // 5, (SOLE_Y - 260) * 2 // 5))
            lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
            t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(lf, (sk.width, 0))
            tiles.append(t)
        W = max(t.width for t in tiles)
        cols = 2
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
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        if a.frames and os.path.isfile(os.path.join(a.frames, name + ".png")):
            shutil.copyfile(os.path.join(a.frames, name + ".png"), os.path.join(out, f"{k}_{name}_league.png"))
        else:
            lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
