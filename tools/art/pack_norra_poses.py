#!/usr/bin/env python3
"""Norra's pose pack for Codex (assets/source/norra/POSE_PROMPTS.md): the whole-body poses of her actions (the user,
2026-10-26: actions by Codex on skeletons, 「按视频做骨架包」 - pack_locke_poses.py's way).

    python tools/art/pack_norra_poses.py [--out C:/t/nr_work/norra_pose_pack] [--refs C:/t/nr_work/video_refs]
                                         [--check DIR]

Norra has no clips anywhere we can read (League's client dropped TFT set 12; CommunityDragon keeps her mesh, no
skeleton), so every pose follows frames cut from videos (the user: 「你去参考一下视频 里面动作怎么放的」, --refs: sheets
of frames, Riot's, kept local, never committed): the TFT unit's own animations in Riot's "Norra Revealed" (YouTube
1RTOUNxqAA4: her idle with a hand at her chin and a gold ring in the other, the gold flash that summons Yuumi, the
attack that POINTS at the target, the cast in a purple swirl that ends with an arm thrust straight up) and the Wild Rift
champion in "Wild Rift presents: Norra" (wpwNeNiKPz0: her little-step walk, the gold portal rings of her ult).
Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 0's A-1 at 36 game
px, PPU 2.0, with the gold ring drawn in: 46 x 72) sits at squares (DX + shift, DY) on it. The skeletons are set by
hand after those frames: every bone at the design's OWN length (measured on hd/idle.png at 14x: REST), only its
direction set per pose (POSES), the lowest foot on the ground unless the pose lifts it. The prompt gives the arms'
lengths in squares and asks Codex to count them; her legs are short and hidden under the robe (its hem moves with
them).
THE RING (the user: 「加金环」): a small gold portal ring (RING_D squares across) in her NEAR hand (image left); she points
and throws with the FAR arm (image right) - her arms are short under a big hat, and the near arm reaching to the right
crossed her face in every pointing pose; `ring` = the ring centre's direction from the near hand (degrees, ang()'s way;
None: no ring in the hand - it flew); drawn as a gold circle.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png; 1_head.png (the design's hat, head and face 8x:
every pose wears it); 2_design.png; per pose <k>_<name>_skeleton.png and <k>_<name>_video.png (the frames it follows,
cut from the video sheets and enlarged).
--check DIR: each skeleton beside its video frames, and the design's own skeleton over the design.
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR
leg (image right), PURPLE = the POINT arm (the far arm, image right: the one that points and throws), ORANGE = the RING
arm (the near arm, image left, holding the ring); grey box = the head (hat, wrap, glasses, face - never redrawn); gold
circle = the ring.
"""
import argparse
import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_norra_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "norra")
PX, CANVAS, SOLE_Y = 14, 1254, 1176
GREY = (225, 225, 225)
GROUND = 72                        # the design's soles' bottom edge (rows)
DX, DY = 21, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 84)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "point_arm": (150, 60, 200),
       "ring_arm": (255, 140, 0)}
HEAD = (0, 47, 7, 44)              # rows / columns of the hat, the head wrap, the glasses and the face in hd/idle.png
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 37 x 47 squares
FACE = (19, 38, 34, 46)            # the face (glasses, nose, mouth): x0, x1, y0, y1 in design squares
RING_D = 7                         # the ring across (squares)
RING_RGB = (242, 194, 58)

# the design's own skeleton, measured on hd/idle.png (46 x 72, square edges, at 14x): the head box's middle; the spine
# pelvis (under the red sash's knot) -> the base of the neck (under the scarf's bone clasp); each arm shoulder, elbow,
# wrist, the fingers' tips (both hang a little off the robe: the near hand on the image left gripping the ring, the far
# hand on the image right); each leg hip, knee, ankle, toes (short, under the robe: only the dark
# shoes show at its hem); the ring's centre from the far hand
REST = {
    "head": (25.5, 23.5),
    "spine": [(27.0, 61.0), (27.0, 47.0)],
    "ring_arm": [(17.0, 48.0), (15.0, 54.0), (15.0, 58.5), (15.0, 61.0)],
    "point_arm": [(35.0, 48.0), (36.5, 53.5), (36.5, 58.0), (37.0, 60.5)],
    "near_leg": [(24.0, 62.0), (23.0, 66.0), (22.0, 70.0), (24.0, 71.5)],
    "far_leg": [(31.0, 62.0), (32.0, 66.0), (33.0, 70.0), (35.0, 71.5)],
    "ring": -60.0,
}

# the video frames each pose follows: sheet -> (columns, cell width, cell height) as cut in the browser (px of the
# saved 800-wide screenshot), then per pose [(sheet, cell index)]
SHEETS = {"tft_attack_cast_49-56s.jpg": (6, 133.3, 114.4, "TFT, Riot's reveal video, 49.6 s + 0.3 s a cell"),
          "tft_idle_summon_43-50s.jpg": (6, 133.3, 124.5, "TFT, Riot's reveal video, 43.0 s + 0.4 s a cell"),
          "wr_walk.jpg": (5, 160.0, 168.8, "Wild Rift, her walk, 18.5 s + 0.33 s a cell"),
          "wr_ult_portals.jpg": (6, 133.3, 96.0, "Wild Rift, her ult's gold portal rings, 58 s + 0.57 s a cell"),
          "wr_idle_with_yuumi.jpg": (6, 133.3, 99.6, "Wild Rift, standing by Yuumi, 38 s + 0.67 s a cell")}

# the poses: name -> (refs, what it is for (Chinese), the pose line (English), the skeleton: the pelvis (design
# squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole figure is moved on
# the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right, 180 up, -90 to
# the image left) - each bone at the design's own length (REST). A limb is "rest", three angles, or (target, side, last
# angle) - the wrist / ankle at the target with the elbow / knee solved (side -1 bends a downward limb's middle joint
# to the image right, +1 to the image left). "ring": the ring's direction from the far hand (None: no ring).
POSES = {
    "a_wind": ([("tft_attack_cast_49-56s.jpg", 9), ("tft_attack_cast_49-56s.jpg", 0)],
               "普攻起手：身子微微往后收，指人的那只手（远侧，画面右边）弯起来收到胸前、食指竖起，拿金环的手（近侧，画面左边）往身后摆开，两脚稍稍分开（普攻蓄力）",
               "WIND-UP - leaning back a little, the POINT hand (the far one, image right) drawn in to her chest with the "
               "index finger up, the RING hand (the near one, image left) swung out behind her, the feet a little apart.",
               dict(pelvis=(27.0, 61.0), lift=None, shift=0, spine=-174, ring=-90.0,
                    point_arm=(-20, -95, -110), ring_arm=(-45, -65, -75),
                    near_leg=((21.0, 71.5), 1, 70), far_leg=((34.0, 71.5), -1, 80))),
    "a_point": ([("tft_attack_cast_49-56s.jpg", 3), ("tft_attack_cast_49-56s.jpg", 6)],
                "普攻指向：远侧那只手往前上方（画面右上）伸直，食指指着目标（魔法弹从这里飞出去，手在头的右边，不挡脸），拿金环的手往身后下方摆，身子往前倾一点，前脚往前迈（普攻打出）",
                "POINT - the POINT arm (far, image right) stretched straight out to the upper right (up 40 degrees, beside "
                "her head, never over the face), the index finger pointing at the target, the RING arm (near) swung down "
                "and back, the body leaning a little forward, the front foot forward.",
                dict(pelvis=(27.0, 61.0), lift=None, shift=-2, spine=172, ring=-80.0,
                     point_arm=(125, 128, 130), ring_arm=(-30, -45, -50),
                     near_leg=((22.0, 71.5), 1, 70), far_leg=((36.0, 71.5), -1, 85))),
    "q_swirl": ([("tft_attack_cast_49-56s.jpg", 12), ("tft_attack_cast_49-56s.jpg", 13)],
                "开门蓄力：膝盖微弯、身子缩一点，两只手捧在胸前（在下巴下面，不挡脸），金环举在两手之间，帽子和垂耳跟着往下压（次元门狂欢起手：次元门在她身边打开，特效以后画）",
                "GATHER - the knees a little bent, the body drawn in, BOTH hands held together before her chest under her "
                "chin (never over the face) with the RING held between them, the hat and the ears dipping with her.",
                dict(pelvis=(27.0, 62.0), lift=None, shift=0, spine=178, ring=90.0,
                     point_arm=(-30, -100, -110), ring_arm=(30, 95, 100),
                     near_leg=((23.0, 71.5), 1, 60), far_leg=((33.0, 71.5), -1, 80))),
    "q_throw": ([("tft_attack_cast_49-56s.jpg", 14), ("tft_attack_cast_49-56s.jpg", 15)],
                "抛球：踮起脚、身子往上伸直，远侧那只手笔直举过头顶、在头的右边往前上方一扬（次元球从手里抛出去了，手张开），拿金环的手放在身侧（次元门狂欢抛出）",
                "THROW UP - on tiptoe and stretching tall, the POINT arm (far) thrust straight UP beside the right of her "
                "head and a little forward (the hand open: the portal ball has just left it; never over the face), the "
                "RING hand (near) down at her side.",
                dict(pelvis=(27.0, 60.0), lift=1, shift=0, spine=-178, ring=-60.0,
                     point_arm=(160, 155, 150), ring_arm=(-15, -25, -30),
                     near_leg=(5, 0, 60), far_leg=(-5, 0, 80))),
    "e_open": ([("tft_idle_summon_43-50s.jpg", 4), ("tft_idle_summon_43-50s.jpg", 5)],
               "举环开门：拿金环的手（近侧，画面左边）高高举向左上方，把金环举在头的左边（不挡脸），远侧那只手往身侧（画面右边）张开、手掌朝外，身子挺直（异界来物：开出次元门）",
               "RAISE THE RING - the RING arm (near, image left) lifted high to the upper left, the ring held up beside the "
               "left of her head (never over the face), the POINT arm (far) spread out to her side on the image right with "
               "the palm open, the body straight.",
               dict(pelvis=(27.0, 61.0), lift=None, shift=4, spine=-178, ring=-150.0,
                    point_arm=(60, 70, 75), ring_arm=(-140, -140, -145),
                    near_leg=((23.0, 71.5), 1, 70), far_leg=((33.0, 71.5), -1, 80))),
    "r_raise": ([("wr_ult_portals.jpg", 10), ("wr_ult_portals.jpg", 12)],
                "双手高举：整个人往上浮起（脚离地约 3 格），两只手臂在头的两边高高举起成 V 字（不挡脸），金环举在近侧那只手里，长袍下摆往下垂、往外扬（门槛之书：头顶打开大门）",
                "BOTH ARMS UP - floating up off the ground (the feet about 3 squares up), BOTH arms raised high on either side "
                "of her head in a V (never over the face; the ring in the near hand), the robe's hem hanging and flaring.",
                dict(pelvis=(27.0, 59.0), lift=3, shift=0, spine=180, ring=-165.0,
                     point_arm=(150, 155, 160), ring_arm=(-150, -155, -160),
                     near_leg=(5, 0, 30), far_leg=(-5, 0, 40))),
    "r_cast": ([("wr_ult_portals.jpg", 16), ("wr_ult_portals.jpg", 18)],
               "往下压：落回地面、身子往前倾，两只手一起往前下方（画面右下）推出去，手掌朝下（把书页从门里压下去），金环在近侧手里（门槛之书：落下）",
               "PUSH DOWN - landed again and leaning forward, BOTH arms thrust out together to the lower right (the palms "
               "down, pushing the page down through the gate), the ring in the near hand.",
               dict(pelvis=(27.0, 61.0), lift=None, shift=-3, spine=165, ring=10.0,
                    point_arm=(80, 70, 65), ring_arm=(85, 75, 70),
                    near_leg=((21.0, 71.5), 1, 70), far_leg=((36.0, 71.5), -1, 85))),
    "run1": ([("wr_walk.jpg", 0), ("wr_walk.jpg", 1)],
             "跑 1（远侧脚往前迈、着地，近侧脚在后面蹬）：小碎步，身子往前倾，长袍下摆往后飘，两只垂耳往后甩，两只手稍稍张开在身侧（拿金环的近侧手往后、远侧手往前摆）",
             "RUN 1 - little steps: the FAR foot reaching forward and landing, the NEAR foot pushing off behind, the body "
             "leaning forward, the robe's hem and both ears swinging back, the arms a little out at her sides (the near "
             "one with the ring back, the far one forward).",
             dict(pelvis=(27.0, 61.0), lift=None, shift=0, spine=170, ring=-70.0,
                  point_arm=(40, 60, 70), ring_arm=(-30, -20, -10),
                  near_leg=((20.0, 70.5), 1, -60), far_leg=((35.0, 71.5), -1, 80))),
    "run2": ([("wr_walk.jpg", 2)],
             "跑 2（近侧脚在身下撑地，远侧脚抬起来往前收）：身子高一格，两只手摆回身边",
             "RUN 2 - the near foot under her carrying her, the FAR foot lifted and coming forward, the body one square "
             "higher, both arms passing close to her sides.",
             dict(pelvis=(27.0, 60.0), lift=1, shift=0, spine=172, ring=-60.0,
                  point_arm=(15, 25, 30), ring_arm=(-10, 0, 0),
                  near_leg=((26.0, 71.5), 1, 70), far_leg=((33.0, 68.0), -1, 70))),
    "run3": ([("wr_walk.jpg", 3)],
             "跑 3（近侧脚往前迈、着地，远侧脚在后面蹬）：身子往前倾，拿金环的近侧手往前摆，远侧手往后摆",
             "RUN 3 - little steps: the NEAR foot reaching forward and landing, the FAR foot pushing off behind, the body "
             "leaning forward, the near arm with the ring swinging forward, the far arm back.",
             dict(pelvis=(27.0, 61.0), lift=None, shift=0, spine=170, ring=-30.0,
                  point_arm=(-20, -10, 0), ring_arm=(30, 50, 60),
                  near_leg=((32.0, 71.5), -1, 80), far_leg=((25.0, 70.5), 1, -60))),
    "run4": ([("wr_walk.jpg", 4)],
             "跑 4（远侧脚在身下撑地，近侧脚抬起来往前收）：身子高一格，两只手摆回身边",
             "RUN 4 - the far foot under her carrying her, the NEAR foot lifted and coming forward, the body one square "
             "higher, both arms passing close to her sides.",
             dict(pelvis=(27.0, 60.0), lift=1, shift=0, spine=172, ring=-60.0,
                  point_arm=(5, 15, 20), ring_arm=(0, 10, 10),
                  near_leg=((28.0, 68.0), -1, 70), far_leg=((31.0, 71.5), -1, 80))),
    "d_fall": ([],
               "被打倒：被打得往后（画面左边）仰倒、膝盖发软，两只手臂往上甩开（不挡脸），金环从手里飞出去（手里空了），帽子跟着头往后仰（死亡第一下）",
               "KNOCKED BACK - thrown back toward the image left, the knees giving way, both arms flung up (never over the "
               "face), the RING flying out of her hand (the hand empty), the hat going back with her head.",
               dict(pelvis=(28.0, 62.0), lift=None, shift=4, spine=-155, ring=None,
                    point_arm=(120, 140, 150), ring_arm=(-140, -160, -170),
                    near_leg=((23.0, 71.5), 1, 60), far_leg=((34.0, 71.5), -1, 80))),
    # the head is pasted upright, so she sits slumped rather than lying flat
    "d_down": ([],
               "坐倒在地：一屁股坐在地上，长袍铺在身下，两条短腿往前伸，两只手撑在身后的地上，头微微垂下，金环掉在她身前的地上（死亡：倒地）",
               "SAT DOWN - sat down on the ground, the robe spread under her, the short legs stuck out in front, both hands "
               "propped on the ground behind her, the head hanging a little, the RING lying on the ground in front of her.",
               dict(pelvis=(26.0, 69.0), lift=None, shift=2, spine=-170, ring=None,
                    point_arm=(20, 30, 0), ring_arm=(-30, -20, 0),
                    near_leg=(70, 80, 100), far_leg=(80, 90, 110))),
}


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned); the ring by the near hand. The lowest foot on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("point_arm", neck, rs[1], 1.0), ("ring_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5)):
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(name)
        if len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    hand = sk["ring_arm"][2]
    sk["ring"] = [] if spec["ring"] is None else [along(hand, spec["ring"], RING_D / 2 + 0.5)]
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    return {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}


def to_canvas(sk, shift=0):
    return {k: (v[0] + DX + shift, v[1] + DY) if k == "head" else [(x + DX + shift, y + DY) for x, y in v]
            for k, v in sk.items()}


def c(p):
    return (p[0] * PX, p[1] * PX)


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "point_arm", "spine", "near_leg", "ring_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    for p in s["ring"]:
        x, y = c(p)
        r = RING_D / 2 * PX
        dr.ellipse([x - r, y - r, x + r, y + r], outline=RING_RGB + (alpha,), width=PX)
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def canvas_grid():
    IP.PX, IP.CANVAS, IP.SOLE_Y = PX, CANVAS, SOLE_Y
    return _grid()


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def video_frames(refs_dir, refs, z=3):
    """The cells a pose follows, cut from the video sheets, side by side, z times bigger."""
    cells = []
    for sheet, k in refs:
        cols, cw, ch, _ = SHEETS[sheet]
        im = Image.open(os.path.join(refs_dir, sheet)).convert("RGB")
        x, y = (k % cols) * cw, (k // cols) * ch
        cell = im.crop((round(x), round(y), round(x + cw), round(y + ch)))
        cells.append(cell.resize((cell.width * z, cell.height * z), Image.LANCZOS))
    out = Image.new("RGB", (sum(c_.width for c_ in cells) + 8 * (len(cells) - 1), max(c_.height for c_ in cells)),
                    (255, 255, 255))
    x = 0
    for c_ in cells:
        out.paste(c_, (x, 0))
        x += c_.width + 8
    return out


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), refs, zh, en)
            for name, (refs, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone, the head box and the ring on the canvas; no hand or ring over the face."""
    out = []
    pts = [p for k in ("spine", "point_arm", "ring_arm", "near_leg", "far_leg", "ring") for p in s[k]]
    bad = [(round(x), round(y)) for x, y in pts if x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6]
    if bad:
        out.append(f"off the canvas / below the ground at {bad[:3]}")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["point_arm"][2:] + s["ring_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    face += [p for p in s["ring"] if fx0 - RING_D / 2 <= p[0] <= fx1 + RING_D / 2 and fy0 - RING_D / 2 <= p[1] <= fy1 +
             RING_D / 2]
    if face:
        out.append(f"hand / ring over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/nr_work/norra_pose_pack")
    ap.add_argument("--refs", default="C:/t/nr_work/video_refs")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), ring=REST["ring"],
                                point_arm="rest", ring_arm="rest", near_leg="rest", far_leg="rest")))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    r0, r1, c0, c1 = HEAD
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        names = a.only.split(",") if a.only else list(poses)
        tiles = []
        for name in names:
            s, refs, zh, en = poses[name]
            can = canvas_grid()
            hx, hy = s["head"]
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name)
            vf = video_frames(a.refs, refs) if refs else Image.new("RGB", (10, 10), (255, 255, 255))
            sk = can.convert("RGB").resize((CANVAS * 2 // 5, CANVAS * 2 // 5))
            vf = vf.resize((round(vf.width * sk.height / vf.height), sk.height))
            t = Image.new("RGB", (sk.width + vf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(vf, (sk.width, 0))
            tiles.append(t)
        tile_sheet(tiles, os.path.join(a.check, "poses_check.png"))
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
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, refs, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        if refs:   # the videos show no death: those two follow the text alone
            video_frames(a.refs, refs).save(os.path.join(out, f"{k}_{name}_video.png"))
        print(name, refs)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
