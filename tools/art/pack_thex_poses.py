#!/usr/bin/env python3
"""T-Hex's pose pack for Codex (assets/source/thex/POSE_PROMPTS.md): the whole-body poses of its actions, each on a
skeleton projected from its OWN clips (its model and clips are in the Riot client's TFTSet16.wad.client, so its
skeletons are its animator's: Root Pelvis Spine1-2 Neck Head Jaw, L/R Clavicle Shoulder Elbow, L_Hand fingers (the claw)
and R_Weapon (the gatling), L/R Hip KneeUpper/Lower Foot toes, Tail1-5, L/R_Back_Cover1-3 = the back plates that open
into missile pods).

    python tools/art/pack_thex_poses.py [--out D:/TFM2-Workshop/thex_packs/thex_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_thex_picture.CLIPS), the head left at the model's size (HEAD_SCALE
1.0: the grey box is the design's own head carried by the Head joint). All are seen from the design's angle (3/4 facing
right, yaw 35). One scale for all: the design pose's whole height (idle@0, the frame step 0's A was drawn from: the ear
spikes to its soles) = the design's 76 rows (hd/idle.png: A-1 at 40 game px, PPU 1.9, 1:1) at PX px a square; the
lowest point of every pose on y SOLE_Y, its root on the design's root column (PELVIS_COL: None places it by the ratio
of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), purple = the jaw, PINK = the L_ arm (the claw), CYAN = the R_
arm (the gatling), RED = the L_ leg, BLUE = the R_ leg, BROWN = the tail, YELLOW / ORANGE = the L_ / R_ back plate
(the missile pods), grey box = the head.
Its run (TFT's bird-legged run, 1.27 s a full cycle of both legs) is sampled at RUN_MS over the whole cycle: the L (red)
foot lifted ~60-570 ms (highest ~320), the R (blue) foot lifted ~570-1140 (highest ~950) (gait probe 2026-11-02;
tft-run-full-cycle: a half cycle reads as legs that never swap).
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
from design_thex_hd import lp  # noqa: E402
from pack_thex_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "thex")
PX, CANVAS, SOLE_Y = 9, 1254, 1176
ROWS = 76                     # hd/idle.png's height
HEAD_SCALE = 1.0             # the model's head as it is (the grey box carries the design's head)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (58, 0, 101, 34)    # the design's head (the copper helmet, the blue visor, the near eye, the jaw and teeth)
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "jaw": (140, 60, 200), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210),
       "L_leg": (230, 30, 30), "R_leg": (40, 90, 230), "tail": (150, 90, 40), "L_pod": (225, 195, 0),
       "R_pod": (255, 130, 0)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Neck", "Head"],
          "jaw": ["Head", "Jaw"],
          "L_arm": ["Spine2", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand", "L_Middle1"],
          "R_arm": ["Spine2", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Weapon"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_ToeB1"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_ToeB1"],
          "tail": ["Pelvis", "Tail1", "Tail2", "Tail3", "Tail4", "Tail5"],
          "L_pod": ["Spine2", "L_Back_Cover1", "L_Back_Cover2", "L_Back_Cover3"],
          "R_pod": ["Spine2", "R_Back_Cover1", "R_Back_Cover2", "R_Back_Cover3"]}
HEAD_JOINTS = ("Head", "Jaw")
RUN_MS = (0, 159, 317, 476, 635, 794, 952, 1111)   # one full 1.27 s cycle: the L (red) foot's swing, then the R (blue)
RUN_ZH = ("跑 1：红线那条腿在后面刚要抬起来往前迈，蓝线那条腿踩地；身子前倾、尾巴放平，加特林端在胸前",
          "跑 2：红线的腿抬起来往前送",
          "跑 3：红线的腿抬到最高，在身子下面往前摆",
          "跑 4：红线的腿在前面落下来",
          "跑 5：红线的腿踩地，蓝线的腿在后面开始抬（换脚）",
          "跑 6：蓝线的腿抬起来往前送",
          "跑 7：蓝线的腿抬到最高，在身子下面往前摆",
          "跑 8：蓝线的腿在前面落下来（8 接回 1，循环）")
RUN_EN = ("RUN 1 - the RED-line leg behind, just about to lift and step forward, the BLUE-line leg planted; the body "
          "leaning forward, the tail level, the gatling held at the chest.",
          "RUN 2 - the RED-line leg lifted, swinging forward.",
          "RUN 3 - the RED-line leg at its highest, swinging forward under the body.",
          "RUN 4 - the RED-line leg coming down in front.",
          "RUN 5 - the RED-line leg planted, the BLUE-line leg starting to lift behind (the change of feet).",
          "RUN 6 - the BLUE-line leg lifted, swinging forward.",
          "RUN 7 - the BLUE-line leg at its highest, swinging forward under the body.",
          "RUN 8 - the BLUE-line leg coming down in front (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_aim": ("attack@100", 35, "普攻「加特林弹幕」：弓身站稳，加特林平端朝前瞄准",
              "AIM - crouched and planted, the gatling levelled forward, aiming."),
    "a_recoil": ("attack@500", 35, "开火的后坐：加特林被震得往后一缩，身子跟着微微后仰",
                 "RECOIL - the gatling kicked back by its fire, the body rocking back a little."),
    "q_fire": ("channel2@722", 35, "技能1「追踪导弹」：背上两块铜甲翻开竖起（导弹舱打开），加特林平端，头往前探",
               "PODS OPEN - the two copper back plates flipped up (the missile pods open), the gatling levelled, the "
               "head pushed forward."),
    "e_charge": ("rise@0", 35, "技能2「霸龙冲撞」：压低身子往前冲，头低着往前顶，尾巴绷直",
                 "CHARGE - the body low and lunging forward, the head down and driving ahead, the tail stiff behind."),
    "e_bite": ("roar@233", 35, "咬：头往前猛地一伸，大嘴张到最大咬下去",
               "BITE - the head snapping forward, the jaws opened wide to bite."),
    "r_open": ("channel@900", 35, "大招「海克斯军械库」起手：背甲正在往上翻开，加特林抬起来",
               "PODS RISING - the back plates halfway up, opening, the gatling coming up."),
    "r_fire": ("channel@3177", 35, "大招持续开火：背甲完全翻开竖起，加特林平端朝前，张大嘴（激光从嘴里射出，我后面画）",
               "FULL FIRE - the back plates fully raised, the gatling levelled forward, the mouth wide open (the laser "
               "comes out of it later, not drawn)."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@2619", 35, "被打倒：踉跄着侧身倒下去",
               "FALLING - staggering and toppling over sideways."),
    "d_down": ("death@3666", 35, "倒地：侧躺在地上不动，面罩和蓝色发光面板熄灭（画成暗蓝灰、不发光）",
               "DOWN - lying on its side on the ground, still, the visor and the blue panels gone dark (a dull dark "
               "blue-grey, no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_thex_picture's renders (mirrored: facing image right)."""

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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\thex_packs\thex_pose_pack")
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
        # the grey box = the design's own head (HEAD_BOX on the canvas) carried by the Head joint from the idle
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
