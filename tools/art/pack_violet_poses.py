#!/usr/bin/env python3
"""Violet's pose pack for Codex (assets/source/violet/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet13.wad.client, so her
skeletons are her animator's - Vander's way).

    python tools/art/pack_violet_poses.py [--out C:/t/vo_work/violet_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_violet_picture.CLIPS, named by what they show), the head grown to
the design's (pose_ref.chibi, HEAD_SCALE: the design's head with the hair is about a third of her height, TFT's
model's much less). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the design
pose's whole height (spell@0, the fighting stance step 0's B was drawn from: hair to soles) = the design's 76 rows
(hd/idle.png: B-1 at 38 game px, PPU 2.0) at PX px a square; the lowest point of every pose on y SOLE_Y, her pelvis
on the design pose's pelvis column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = her R_ arm, CYAN = her L_ arm (her
skeleton has no fingers: each arm ends at its Glove joint; the renders are mirrored), RED = left leg, BLUE = right leg,
a GOLD ring round each hand = the two gauntlets, grey box = the head.
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
from design_violet_hd import lp  # noqa: E402
from pack_violet_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "violet")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 76                     # hd/idle.png's height
HEAD_SCALE = 1.7
DESIGN = "spell@0"             # the fighting stance step 0's B was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (19, 0, 47, 27)      # the design's head with the hair (hd/idle.png)
PELVIS_COL = 32                 # the design's pelvis column: between its legs (cols 10-28 and 36-56 at row 56)
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "gauntlet": (210, 160, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Glove"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Glove"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw", "Eye", "Brow", "Lip", "Nose", "Mouth", "MidFace")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack@65", 35, "普攻起手：后脚撑地，一只拳套抡到头的后上方蓄力",
               "WIND-UP - weight on the back foot, one GAUNTLET swung up behind and above her head, about to punch."),
    "a_punch": ("attack@260", 35, "直拳：前脚大步弓步、身体压低前倾，拳套笔直往前（画面右边）打出去",
                "PUNCH - a long low lunge onto the front foot, the body leaning forward, one GAUNTLET driven straight "
                "forward to the image right."),
    "a_back": ("attack@1040", 35, "收势：从弓步收回半蹲，两只拳套收回身前（快回到定稿的架势）",
               "RECOVER - pulling back from the lunge into a half crouch, both gauntlets back in front of her (almost "
               "the design's stance)."),
    "q_jab1": ("spell@375", 35, "1-2-3连招第 1 拳：弓步，一记刺拳笔直往前打出",
               "JAB 1 - a lunge, one gauntlet shot straight forward in a jab."),
    "q_jab2": ("spell@625", 35, "第 2 拳：换另一只拳套往前刺，身体还压得很低",
               "JAB 2 - the OTHER gauntlet jabbing forward, the body still low."),
    "q_coil": ("spell@1000", 35, "蓄力：深蹲，一只拳套高高举到头后面，准备上勾拳",
               "COIL - a deep crouch, one gauntlet drawn high behind her head, about to uppercut."),
    "q_upper": ("spell@1500", 35, "第 3 拳上勾拳：整个人跳起来，一只拳套笔直往上勾过头顶",
                "UPPERCUT - leaping up off the ground, one gauntlet driven straight up over her head."),
    "q_land": ("spell@1750", 35, "落地：落回地面半蹲，拳套收在身前",
               "LAND - back on the ground in a half crouch, the gauntlets in front of her."),
    "e_dash": ("attack2@255", 35, "冲拳：整个人往前扑，身体几乎贴着地面平飞，一只拳套顶在最前面",
               "RUSH - flinging herself forward, the body low and nearly flat, one gauntlet leading at the front."),
    "e_punch": ("attack2@510", 35, "冲拳打中：弓步站稳，拳套往前打到底",
                "RUSH PUNCH - landed in a lunge, the leading gauntlet punched all the way out."),
    "r_air": ("attack2@1105", 35, "底城怒拳起跳：跳在半空，两只拳套举在胸前，膝盖收起来",
              "LEAP - high in the air, both gauntlets up at her chest, the knees drawn up."),
    "r_land": ("attack2@1275", 35, "落地：两脚大大分开重重落地，压低重心",
               "LAND - landing heavily, feet planted wide, the body dropped low."),
    "r_slam": ("attack2@850", 35, "砸地：整个人压到最低，打头的拳套往前下方狠狠砸进地面",
               "SLAM - crouched at her lowest, the leading gauntlet smashed down and forward into the ground."),
    "run1": ("run@0", 35, "跑步 1：双拳套举着小跑（金铲铲原样），前脚迈出",
             "RUN 1 - a jog, both gauntlets up (as in the game), the front foot stepping out."),
    "run2": ("run@233", 35, "跑步 2：两脚交错", "RUN 2 - the legs passing."),
    "run3": ("run@466", 35, "跑步 3：另一只脚迈出", "RUN 3 - the other foot stepping out."),
    "run4": ("run@700", 35, "跑步 4：两脚交错", "RUN 4 - the legs passing again."),
    "d_fall": ("death@250", 35, "被击倒：被打得往后仰，两只拳套甩开",
               "KNOCKED BACK - thrown backwards, both gauntlets flung out."),
    "d_down": ("death@860", 35, "倒地：仰面倒在地上（头朝画面右边）",
               "DOWN - lying on her back on the ground, her head to the image right."),
}


class Poser:
    """Her mesh (head grown) and joints, projected as pack_violet_picture's renders (mirrored: facing image right)."""

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
    for hand in ("L_Hand", "R_Hand"):   # the two gauntlets
        p = tuple(xy[poser.names[hand]])
        d.ellipse([p[0] - 26, p[1] - 26, p[0] + 26, p[1] + 26], outline=COL["gauntlet"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "CYAN (the L_ arm)" if zl > zr else "ORANGE (the R_ arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\vo_work\violet_pose_pack")
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
    pelvis_x = dx + PELVIS_COL * PX + PX // 2   # the bbox-ratio way put the skeleton far left (Kobuko's lesson)
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
