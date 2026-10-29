#!/usr/bin/env python3
"""Idas's pose pack for Codex (assets/source/idas/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet7.wad.client, so her
skeletons are her animator's - Krug's and Nomsy's way).

    python tools/art/pack_idas_poses.py [--out D:/TFM2-Workshop/idas_packs/idas_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_idas_picture.CLIPS), the head grown by HEAD_SCALE (step 0's B drew it
bigger than the model's). All are seen from the design's angle (side-on facing right, yaw 80: step 0's B). One scale for
all: the design pose's whole height (idle@0, the frame step 0's B was drawn from: the top of the crest to her feet) =
the design's 98 rows (hd/idle.png: B-1 at 40 game px, PPU 2.45, 1:1) at PX px a square; the lowest point of every pose
on y SOLE_Y, her root on the design's root column (PELVIS_COL: None places it by the ratio of the design's box to the
model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), ORANGE = the l_ wing-arm, PURPLE = the R_ wing-arm (each ending
in a big dot = the claw; the golden wing on the forearm is the PINK (l_) / CYAN (R_) line from the hand to the wing
joint), RED = the l_ leg, BLUE = the R_ leg, BROWN = the tail, grey box = the head. The renders are mirrored: which side
is nearer the camera is printed per pose.
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
from design_idas_hd import lp  # noqa: E402
from pack_idas_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "idas")
PX, CANVAS, SOLE_Y = 7, 1254, 1176
ROWS = 98                      # hd/idle.png's height
HEAD_SCALE = 1.6               # the design's head against the model's (the head box heights, printed)
DESIGN = "idle@0"              # the frame step 0's B was drawn from
HEAD_BOX = (77, 0, 127, 45)    # the design's head (the crest, the eye, the horns, the snout) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 80
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (120, 70, 30), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210)}
CHAINS = {"spine": ["Root", "Spine", "chest", "neck", "Neck_b", "head"],
          "L_arm": ["l_shoulder", "l_uparm", "l_forearm", "l_hand"],
          "R_arm": ["R_shoulder", "R_UpArm", "R_ForeArm", "R_hand"],
          "L_leg": ["hip", "l_thigh", "l_knee", "l_foot", "l_toe"],
          "R_leg": ["hip", "R_Thigh", "R_Knee", "R_Foot", "R_Toe"],
          "tail": ["hip", "Tail_a", "Tail_b", "Tail_c", "Tail_d", "Tail_e", "Tail_f", "Tail_g"],
          "L_wing": ["l_hand", "l_wing"], "R_wing": ["R_hand", "R_Wing"]}
HEAD_JOINTS = ("head", "jaw", "EYE")
# TFT's glide and her fall stretch the tail out to two bodies: shortened in those poses (the design's tail, step 0's B,
# is a body long), so the whole pose fits the canvas
TAIL_SCALE = 0.7
LONG_TAIL = tuple(f"run@{ms}" for ms in (0, 83, 166, 250, 333, 416, 500, 583)) + ("death@2500", "attack1@500")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack1@333", 80, "龙爪起手：往前跨一步，两只翅膀手臂往后上方收起蓄力，爪子张开（照骨架）",
               "WIND UP - a step forward, both wing-arms drawn back and up behind her (as in C and D), the claws open."),
    "a_claw": ("attack1@500", 80, "龙爪：身子压低往前扑，紫线那只爪子往前狠狠挥出去，橙线那只甩到身后，尾巴往后甩直",
               "CLAW - lunging forward low, the claw on the PURPLE line slashing forward, the arm on the ORANGE line flung "
               "back, the tail swung straight back."),
    "q_rear": ("celebration@622", 80, "黄金龙息起手：上身往后仰、龙头抬高，胸口鼓起来吸气，嘴闭着",
               "INHALE - the upper body leaning back, the head raised high, the chest puffed up, the mouth shut."),
    "q_breath": ("celebration@1600", 80, "黄金龙息：龙头往前伸，嘴张到最大往前喷（金色龙息之后单独画）",
                 "BREATHE - the head thrust forward, the mouth open as wide as it goes, breathing forward (the golden "
                 "breath is drawn separately later)."),
    "e_open": ("attack1@166", 80, "龙威振翅：两只翅膀手臂猛地向两边张开（前臂上的金翼完全展开），头抬起",
               "WINGS OPEN - both wing-arms flung wide to the sides (the golden wings on the forearms fully spread), "
               "the head up."),
    "e_roar": ("celebration@1866", 80, "龙威振翅：翅膀张着，龙头往前伸、张大嘴吼",
               "ROAR - the wings still spread, the head thrust forward, the mouth wide open in a roar."),
    "r_wrap": ("crouch@4500", 80, "黄金龙鳞：蹲下去，两只翅膀手臂收到身前把自己裹住",
               "WRAP - crouching low, both wing-arms drawn in front of her, wrapping herself in her wings."),
    "r_hold": ("crouch_loop@0", 80, "黄金龙鳞（裹着）：蹲着，翅膀挡在脸前面，金翼像一面盾",
               "SHELL - crouched, the wings held in front of her face like a golden shield."),
    "r_burst": ("celebration@2488", 80, "黄金龙鳞（展开）：猛地站起来，双翼往两边展开，仰头一吼",
                "BURST - standing up at once, both wings thrown open to the sides, the head up in a roar."),
    "run1": ("run@0", 80, "移动 1：张开翅膀贴着地面往前滑翔（金铲铲原样）",
             "GLIDE 1 - gliding low over the ground, the wings open."),
    "run2": ("run@83", 80, "移动 2", "GLIDE 2."),
    "run3": ("run@166", 80, "移动 3", "GLIDE 3."),
    "run4": ("run@250", 80, "移动 4", "GLIDE 4."),
    "run5": ("run@333", 80, "移动 5", "GLIDE 5."),
    "run6": ("run@416", 80, "移动 6", "GLIDE 6."),
    "run7": ("run@500", 80, "移动 7", "GLIDE 7."),
    "run8": ("run@583", 80, "移动 8", "GLIDE 8."),
    "d_fall": ("death@300", 80, "被打倒：被打得往后一仰、身子立起来、两只翅膀手臂乱抓",
               "KNOCKED BACK - thrown back, the body upright, the wing-arms flailing."),
    "d_down": ("death@2500", 80, "倒地：侧着倒在地上，翅膀摊开（金铲铲原样）",
               "DOWN - fallen on her side on the ground, the wings sprawled (as in TFT)."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_kobuko_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE,
                               scale={"Tail_a": TAIL_SCALE} if clip in LONG_TAIL else None)
        glob = pose_ref.globals_(self.m.joints, [pose_ref.trs(*p) for p in local])
        verts = pose_ref.skin(self.m.v, self.m.infl, self.m.bind_inv, glob)
        joints = np.array([g[:3, 3] for g in glob])
        return verts, joints

    @staticmethod
    def project(p, yaw, scale, ground, x0):
        """World points -> canvas (x, y): render_hq's camera at -yaw, then mirrored."""
        y_ = np.radians(-yaw)
        cy, sy = np.cos(y_), np.sin(y_)
        cp, sp = np.cos(np.radians(PITCH)), np.sin(np.radians(PITCH))
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
        v = p @ (rx @ ry).T
        return np.c_[CANVAS - (v[:, 0] * scale + x0), ground - v[:, 1] * scale], v[:, 2]


def head_vertices(poser):
    """The vertices mostly weighted to the head and what hangs off it (ears, topknot, beard, eyes, jaw)."""
    m = poser.m
    joint_of = np.array(m.infl)[m.v["bones"].astype(np.int64)]
    main = joint_of[np.arange(len(m.v)), np.argmax(m.v["w"], axis=1)]
    heads = {i for i, j in enumerate(m.joints) if any(k in j["name"] for k in HEAD_JOINTS)}
    return np.isin(main, list(heads))


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def skeleton(poser, xy, z, hbox, out, base=None):
    can = Image.new("RGB", (CANVAS, CANVAS), GREY)
    d = ImageDraw.Draw(can)
    grid(d)
    if base is not None:   # the design under its own skeleton, faded
        can = Image.blend(can, base.convert("RGB"), 0.55)
        d = ImageDraw.Draw(can)
    d.rectangle(hbox, outline=(110, 110, 110), width=3)
    order = sorted(CHAINS, key=lambda c: -np.mean([z[poser.names[n]] for n in CHAINS[c]]))   # far chains first
    for c in order:
        pts = [tuple(xy[poser.names[n]]) for n in CHAINS[c]]
        d.line(pts, fill=COL[c], width=7, joint="curve")
        for p in pts[:-1]:
            d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=COL[c])
        if c.endswith("arm"):
            p = pts[-1]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "L" if zl > zr else "R"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\idas_packs\idas_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # one scale for every pose: the design pose's whole height = the design's rows
    iv, _ = poser.pose(DESIGN)
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Root"]
    # the design on the canvas: its soles on SOLE_Y, centred; every pose's pelvis on the design's pelvis column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    if PELVIS_COL is None:   # the model's pelvis placed by the ratio of the design's box to the model's
        ix = Poser.project(iv, YAW, scale, 0.0, 0.0)[0][:, 0]
        jx = Poser.project(poser.pose(DESIGN)[1], YAW, scale, 0.0, 0.0)[0][pel, 0]
        x0, _, x1, _ = design.getbbox()
        col = x0 + (jx - ix.min()) / (ix.max() - ix.min()) * (x1 - x0)
        print("pelvis column", round(col, 1))
        pelvis_x = dx + round(col * PX)
    else:
        pelvis_x = dx + PELVIS_COL * PX + PX // 2
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge
        lo, hi = xy[:, 0].min() + shift, xy[:, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        tris = poser.tris
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near arm", near_arm(jz, poser))
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        im = pose_ref.render_hq(verts.copy(), tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS),
                                scale, ground, shift=x0 / CANVAS - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "yaw", yaw, "near arm", near_arm(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
