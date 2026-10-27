#!/usr/bin/env python3
"""Vander's pose pack for Codex (assets/source/vander/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet13.wad.client, so his
skeletons are his animator's - Silco's, Maddie's and Loris's way).

    python tools/art/pack_vander_poses.py [--out C:/t/vd_work/vander_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_vander_picture.CLIPS, named by what they show), the head grown to
the design's (pose_ref.chibi, HEAD_SCALE 1.6: the design's head with the hair is about 0.27 of his crouched height,
TFT's model's ~0.17). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the design
pose's whole height (slam@990, the fighting stance step 0's B was drawn from: hair to soles) = the design's 80 rows
(hd/idle.png: B-2 at 40 game px, PPU 2.0) at PX px a square; the lowest point of every pose on y SOLE_Y, his pelvis
on the design pose's pelvis column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = the GAUNTLET arm (the joints' R_ chain:
his mesh weights the gauntlet to R_Hand; the renders are mirrored), CYAN = the BANDAGED fist arm (L_), RED = left leg,
BLUE = right leg, a GOLD ring = the gauntlet (round the R_ hand), grey box = the head.
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
from design_vander_hd import lp  # noqa: E402
from pack_vander_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vander")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 80                     # hd/idle.png's height
HEAD_SCALE = 1.6
DESIGN = "slam@990"            # the fighting stance step 0's B was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (42, 0, 68, 22)      # the design's head with the hair (hd/idle.png)
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "gauntlet": (210, 160, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle3"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle3"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw", "Eye", "Brow", "Lip", "Nose", "Mouth", "MidFace")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack@170", 35, "普攻起手：身子往后仰、站直，戴拳套的手抡到头后面，准备往下砸",
               "WIND-UP - rearing back upright, the GAUNTLET arm swung up behind his head, about to bring it down."),
    "a_punch": ("attack@420", 35, "铁拳：前脚大步跨出、身体压低前倾，拳套往前下方（画面右边）狠狠砸出去",
                "PUNCH - a long lunge onto the front foot, the body low and leaning forward, the GAUNTLET driven "
                "down and forward to the image right."),
    "a_back": ("attack@830", 35, "收势：从前冲收回半蹲，拳套收到身前（快回到定稿的架势）",
               "RECOVER - pulling back from the lunge into a half crouch, the gauntlet back in front of him (almost "
               "the design's stance)."),
    "q_guard": ("guard@500", 35, "地下猎犬（防御姿态）：深蹲马步，拳套竖着举在头的右边护住（不挡眼睛），另一只拳头护在胸前",
                "GUARD - a deep wide crouch, the GAUNTLET raised upright beside the right of his head as a guard "
                "(never over the eyes), the bandaged fist at his chest."),
    "e_crouch": ("attack2@170", 35, "铁拳突进起手：整个人缩成一团压低，准备往上弹",
                 "COIL - crouched very low, curled up, about to spring up."),
    "e_upper": ("attack2@500", 35, "上勾拳：从下往上弹起来，一只拳头笔直往上勾过头顶",
                "UPPERCUT - springing up from the crouch, one fist driven straight up over his head."),
    "r_air": ("leap@200", 35, "桥头死守起跳：整个人跳在半空，双臂张开往后甩，张嘴怒吼",
              "LEAP - high in the air, both arms flung open and back, shouting."),
    "r_land": ("slam@0", 35, "落地：重重落地半跪，拳套高高举过头顶准备砸下",
               "LAND - landing heavily in a low crouch, the GAUNTLET raised high over his head to strike."),
    "r_slam": ("slam@150", 35, "砸拳：拳套往前下方狠狠砸进地面，身体压到最低",
               "SLAM - the GAUNTLET smashed down and forward into the ground, his body at its lowest."),
    "run1": ("run@0", 35, "跑步 1：双拳举着像拳手一样小跑（金铲铲原样），前脚迈出",
             "RUN 1 - a boxer's jog, both fists up (as in the game), the front foot stepping out."),
    "run2": ("run@267", 35, "跑步 2：两脚交错", "RUN 2 - the legs passing."),
    "run3": ("run@533", 35, "跑步 3：另一只脚迈出", "RUN 3 - the other foot stepping out."),
    "run4": ("run@800", 35, "跑步 4：两脚交错", "RUN 4 - the legs passing again."),
    "d_fall": ("death@330", 35, "被击倒：踉跄着往前栽，膝盖弯下去",
               "STAGGER - stumbling forward, the knees giving way."),
    "d_down": ("death@1000", 35, "倒地：整个人脸朝下扑倒在地上（头朝画面右边）",
               "DOWN - lying face down on the ground, his head to the image right."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_vander_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE)
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
    """The vertices mostly weighted to the head and what hangs off it (horns, hair, earrings, eyes, jaw)."""
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


def skeleton(poser, joints, xy, z, hbox, out, base=None):
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
            p = pts[2]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    p = tuple(xy[poser.names["R_Hand"]])   # the gauntlet
    d.ellipse([p[0] - 26, p[1] - 26, p[0] + 26, p[1] + 26], outline=COL["gauntlet"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "CYAN (the bandaged arm)" if zl > zr else "ORANGE (the gauntlet arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\vd_work\vander_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # one scale for every pose: the design pose's whole height = the design's rows
    iv, ij = poser.pose(DESIGN)
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the design pose's pelvis lands on the same column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    ixy, _ = Poser.project(iv, YAW, scale, 0.0, 0.0)
    pelvis_x = dx + (ixy[pel, 0] - ixy[:, 0].min()) / (ixy[:, 0].max() - ixy[:, 0].min()) * design.width * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
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
        skeleton(poser, joints, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"),
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        tris = poser.tris
        im = pose_ref.render_hq(pv, tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS), scale,
                                ground, shift=x0 / CANVAS - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        notes[name] = near_arm(jz, poser)
        print(stem, clip, "yaw", yaw, "near arm", notes[name])
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
