#!/usr/bin/env python3
"""Brock's pose pack for Codex (assets/source/brock/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet16.wad.client, so his
skeletons are his animator's - the Blue Sentinel's way, whose rig his matches: Root Pelvis Spine1-3 Head, L/R Clavicle
Shoulder ElbowUpper/Lower Hand fingers, L/R Hip KneeUpper/Lower Foot Toe; no wrist joint).

    python tools/art/pack_brock_poses.py [--out D:/TFM2-Workshop/brock_packs/brock_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_brock_picture.CLIPS), the head left at the model's size
(HEAD_SCALE 1.0: the grey box is the design's own head carried by the Head joint, not the model's tall hood). All are seen
from the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole height (idle@0, the
frame step 0's A was drawn from: the bonsai top to his soles) = the design's 51 rows (hd/idle.png: A-1 at 44 game px,
PPU 1.16, 1:1) at PX px a square; the lowest point of every pose on y SOLE_Y (the jump's airborne frames too: the rig
lifts them), its root on the design's root column (PELVIS_COL: None places it by the ratio of the design's box to the
model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), PINK = the L_ arm (shoulder to fist), CYAN = the R_ arm, RED =
the L_ leg, BLUE = the R_ leg, grey box = the head.
His run (TFT's hunched lope, 1.33 s a full cycle of both legs) is sampled at RUN_MS over the whole cycle: the L (red)
foot lifted 0-250 ms and down at ~330, the R (blue) foot lifted 415-830 and down at ~910 (C:/t/br_work/s/gait.py;
tft-run-full-cycle: a half cycle reads as legs that never swap).
His two hook clips (attack2 / attack3) turn the whole body round on the root: Q's throw and E's reach are taken from
them before the body turns its back.
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
from design_brock_hd import lp  # noqa: E402
from pack_brock_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "brock")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 51                     # hd/idle.png's height
HEAD_SCALE = 1.0             # the model's head as it is (the grey box carries the design's head)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (32, 8, 46, 24)     # the design's head (the grey-blue hood, the orange face plate, the two ring eyes)
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Spine3", "Head"],
          "L_arm": ["Spine3", "L_Clavicle", "L_Shoulder", "L_ElbowUpper", "L_ElbowLower", "L_Hand",
                    "L_Middle1"],
          "R_arm": ["Spine3", "R_Clavicle", "R_Shoulder", "R_ElbowUpper", "R_ElbowLower", "R_Hand",
                    "R_Middle1"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head",)
RUN_MS = (0, 166, 333, 500, 666, 833, 1000, 1166)   # one full 1.33 s cycle: the L (red) foot's swing, then the R (blue)
RUN_ZH = ("跑 1：红线那条腿刚从后面抬起来往前迈，蓝线那条腿踩地；两只巨拳一前一后摆",
          "跑 2：红线的腿抬着往前送，到半空",
          "跑 3：红线的腿在前面落地，重心压上去",
          "跑 4：两脚都踩地，蓝线的腿在后面开始抬（换脚）",
          "跑 5：蓝线的腿从后面抬起来，抬到最高",
          "跑 6：蓝线的腿抬着往前送，到半空",
          "跑 7：蓝线的腿在前面落地",
          "跑 8：两脚踩地，红线的腿在后面开始抬（8 接回 1，循环）")
RUN_EN = ("RUN 1 - the RED-line leg just lifting from behind to step forward, the BLUE-line leg planted; the two huge "
          "fists swinging one forward, one back.",
          "RUN 2 - the RED-line leg lifted, swinging forward, in mid-air.",
          "RUN 3 - the RED-line leg coming down in front, the weight onto it.",
          "RUN 4 - both feet on the ground, the BLUE-line leg starting to lift behind (the change of feet).",
          "RUN 5 - the BLUE-line leg lifted from behind, at its highest.",
          "RUN 6 - the BLUE-line leg lifted, swinging forward, in mid-air.",
          "RUN 7 - the BLUE-line leg coming down in front.",
          "RUN 8 - both feet on the ground, the RED-line leg starting to lift behind (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_raise": ("attack@420", 35, "普攻「震地拳」起手：两只巨拳并在一起高高举过头顶，身子往后挺，腿叉开站稳",
                "RAISE - both huge fists held together high over his head, the body leaning back, the legs apart and "
                "planted."),
    "a_slam": ("attack@650", 35, "砸下：两只拳头一起狠狠砸到身前地上，身子往前压低、弓着背，膝盖弯下去",
               "SLAM - both fists smashed together onto the ground in front, the body bent forward and low, the back "
               "hunched, the knees bent."),
    "q_wind": ("attack2@330", 35, "技能1「巨岩投掷」起手：上身往后拧，一只巨拳往身后高高抡起（等会儿扔出大石头），另一只拳头在身前",
               "WIND-UP - the upper body twisted back, one huge fist swung far back and up behind him (about to hurl "
               "a boulder), the other fist in front."),
    "q_throw": ("attack2@570", 35, "扔出：抡起的拳头往前狠狠甩出去，手臂伸到身前，上身跟着往前拧",
                "THROW - the swung fist hurled forward, the arm reaching out in front, the upper body twisting "
                "forward after it."),
    "e_plant": ("attack3@330", 35, "技能2「苔藤缠握」起手：侧过身子，一只巨拳收到胸前蓄力",
                "GATHER - turned sideways, one huge fist drawn in before the chest, gathering."),
    "e_reach": ("attack3@630", 35, "伸出：那只拳头往前下方猛地捅出去（树根会从地下钻向敌人），身子压低",
                "REACH - that fist thrust forward and down (his roots will burst from the ground toward the enemy), "
                "the body low."),
    "r_crouch": ("spell@0", 35, "大招「震地猛击」起跳前：深深蹲下蓄力，两只巨拳垂在身前",
                 "CROUCH - squatting deep to jump, both huge fists hanging in front, gathering."),
    "r_leap": ("spell@360", 35, "跃起：双腿蹬直往上跳，两只巨拳往两侧张开（画在地面线上，离地的高度我来加）",
               "LEAP - the legs pushing straight up off the ground, both huge fists flung out to the sides (draw it "
               "standing on the ground line: the height of the jump is added later)."),
    "r_air": ("spell@540", 35, "空中最高点：两只巨拳并在一起高高举过头顶，准备砸下来，两腿收起（同样画在地面线上）",
              "TOP OF THE JUMP - both huge fists held together high over his head, ready to come down, the legs "
              "drawn up (also drawn on the ground line)."),
    "r_land": ("spell@1080", 35, "落地猛砸：重重落地蹲下，两只拳头一起砸进身前地面，身子深深弓下去",
               "LANDING SLAM - landed hard in a deep squat, both fists smashed together into the ground in front, the "
               "body bent far down."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@1928", 35, "被打倒：身子往前倒下去，两只拳头撑不住",
               "FALLING - toppling forward, both fists no longer holding him up."),
    "d_down": ("death@2571", 35, "倒地：整个人脸朝下趴在地上不动，两只巨拳摊在两边，脸板和眼睛熄灭（画成暗橙褐色、不发光）",
               "DOWN - lying flat on his face on the ground, still, both huge fists sprawled at his sides, the face "
               "plate and the eyes gone dark (a dull dark orange-brown, no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_brock_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, 1.0, scale={"Head": HEAD_SCALE})
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
    """The vertices mostly weighted to the head."""
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
    can.save(lp(out))


def near_leg(z, poser):
    """Which leg and arm are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part in ("leg", "arm"):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part]])
        out.append(("L" if zl > zr else "R") + "_" + part)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\brock_packs\brock_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
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
        lo, hi = np.percentile(xy[:, 0], 0.5) + shift, np.percentile(xy[:, 0], 99.5) + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        # the grey box = the design's own head (HEAD_BOX on the canvas) carried by the Head joint from the idle: the
        # model's pointed hood stands far higher than the design's, so its vertices' box sat above the design's face
        hj = jxy[poser.names["Head"]]
        if name == "idle":
            hj0 = hj.copy()
        bx0, by0 = dx + HEAD_BOX[0] * PX, dy + HEAD_BOX[1] * PX
        bx1, by1 = dx + HEAD_BOX[2] * PX, dy + HEAD_BOX[3] * PX
        hbox = (bx0 + hj[0] - hj0[0], by0 + hj[1] - hj0[1], bx1 + hj[0] - hj0[0], by1 + hj[1] - hj0[1])
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        tris = poser.tris
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near", near_leg(jz, poser))
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
        print(stem, clip, "yaw", yaw, "near", near_leg(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
