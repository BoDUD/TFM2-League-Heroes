#!/usr/bin/env python3
"""Kobuko's pose pack for Codex (assets/source/kobuko/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet15.wad.client, so his
skeletons are his animator's - Silco's, Maddie's and Loris's way).

    python tools/art/pack_kobuko_poses.py [--out C:/t/kb_work/kobuko_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_kobuko_picture.CLIPS, named by what they show), the head grown a
little to the design's (pose_ref.chibi, HEAD_SCALE 1.1: TFT's model is a chibi already, its head with the ears and the
topknot 0.38 of his height, the design's about 0.42). All are seen from the design's angle (3/4 facing right, yaw 35)
but the lying death (yaw 80, laid along the ground). One scale for all: the design pose's whole height (idle@0, the
frame step 0's A was drawn from: topknot to soles) = the design's 80 rows (hd/idle.png: A-1 at 40 game px, PPU 2.0) at
PX px a square; the lowest point of every pose on y SOLE_Y, his pelvis on the design pose's pelvis column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = the joints' L_ arm, PURPLE = the R_ arm
(the renders are mirrored: which one is nearer the camera is written per pose), RED = left leg, BLUE = right leg, grey
box = the head.
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
from design_kobuko_hd import lp  # noqa: E402
from pack_kobuko_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kobuko")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 80                     # hd/idle.png's height
HEAD_SCALE = 1.1
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (0, 0, 64, 36)      # the design's head (the topknot, the ears, the face, the beard) in hd/idle.png
PELVIS_COL = 41                # the design's pelvis column: midway between its legs (cols 19-31 and 50-67 at the knees)
YAW = 35
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle2"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle2"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw", "Beard", "Hair", "Ear", "Lip", "Eye", "Brow", "Nose", "Mouth", "Moustache", "Cheek",
               "Ponytail", "Tongue", "Teeth")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack@100", 35, "普攻起手：侧身压低，近处的大爪子收到腰前蓄力",
               "WIND-UP - turning and crouching a little, the near big paw drawn back low at his waist, gathering "
               "force."),
    "a_strike": ("attack@533", 35, "猫爪掌：近处的手臂猛地往右（画面右边）推出一掌，掌心朝前",
                 "PALM STRIKE - the near arm thrust out hard to the image right, the open palm facing forward."),
    "a_back": ("attack@1333", 35, "收势：站直，手收回（接近定稿）",
               "RECOVER - standing up again, the arms coming back (close to the design)."),
    "q_raise": ("spell@400", 35, "金爪真言起手：半蹲，双臂往上抬起，两只大爪子张开、掌心朝前（金色漩涡朝外）",
                "MANTRA - half crouching, both huge arms lifting, the paws open with the palms (the golden spirals) "
                "facing out."),
    "q_spread": ("spell@929", 35, "金爪真言：双臂向两边大大张开，挺胸（护盾套上的一刻）",
                 "SPREAD - both arms flung wide open to the sides, chest out (the moment the shield comes on)."),
    "q_claw": ("attack2@533", 35, "金爪重掌：大步上前，近处的手掌往右前方狠狠拍出（发光的金色掌心朝外）",
               "GOLDEN CLAW - a big step forward, the near open palm slammed out to the front-right, its glowing "
               "golden spiral facing out."),
    "e_crouch": ("spell@190", 35, "猛虎扑 / 游戏结束起跳：深蹲，双爪垂到身前，准备一跃而起",
                 "CROUCH - squatting deep, both paws hanging low in front, coiled to spring up."),
    "e_leap": ("leap@60", 35, "腾空：整个人向上弹起，身体伸直，一条腿收起",
               "LEAP - springing up off the ground, body stretched, one leg tucked."),
    "e_land": ("attack3@533", 35, "落地猛击：落地扎稳，双掌一起往前下方猛推（砸向敌人）",
               "CRASH - landed in a wide stance, both palms driven forward and down together (onto the enemy)."),
    "run1": ("run@0", 35, "跑步 1：圆滚滚地小跑，前脚迈出，手臂前后摆",
             "RUN 1 - a waddling jog, the front foot stepping out, the arms swinging."),
    "run2": ("run@267", 35, "跑步 2：两脚交错", "RUN 2 - the legs passing."),
    "run3": ("run@533", 35, "跑步 3：另一只脚迈出", "RUN 3 - the other foot stepping out."),
    "run4": ("run@800", 35, "跑步 4：两脚交错", "RUN 4 - the legs passing again."),
    "d_hit": ("death@60", 35, "被击中：往后一仰，双臂甩开",
              "STRUCK - reeling back, the arms flung out."),
    "d_fall": ("death@200", 35, "踉跄扑倒：身子往前栽下去",
               "FALLING - pitching forward, going down."),
    "d_down": ("death@1000", 80, "倒地：整个人趴在地上（头朝画面右边），手臂摊开",
               "DOWN - lying face down on the ground, his head to the image right, the arms sprawled."),
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
            p = pts[2]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "L" if zl > zr else "R"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\kb_work\kobuko_pose_pack")
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
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; every pose's pelvis on the design's pelvis column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
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
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near arm", near_arm(jz, poser))
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        im = pose_ref.render_hq(verts.copy(), poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS),
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
