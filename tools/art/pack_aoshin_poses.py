#!/usr/bin/env python3
"""Ao Shin's pose pack for Codex (assets/source/aoshin/POSE_PROMPTS.md): the whole-body poses of his actions, each on
a skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet7.wad.client, so his
skeletons are his animator's - Krug's way).

    python tools/art/pack_aoshin_poses.py [--out C:/t/ao_work/aoshin_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_aoshin_picture.CLIPS, named by what they show), the head grown by
HEAD_SCALE (Codex drew the chibi's mask and mane bigger than the model's). All are seen from the design's angle (3/4
facing right, yaw 35). One scale for all: the design pose's whole height (idle@0, the hover step 0's A was drawn from:
the horns to the lowest curl of the tail) = the design's 76 rows (hd/idle.png: A-1 at 38 game px, PPU 2.0) at PX px a
square; the lowest point of every pose on y SOLE_Y, his hips (Tail0, the root of his body: he has no pelvis joint) on
the design pose's column (PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the neck (the hips to the head), CYAN = the tail, ORANGE = the joints' L_ arm, PURPLE = the
R_ arm (the renders are mirrored: which one is nearer the camera is written per pose), RED = left hind leg, BLUE =
right hind leg, grey box = the head with the mask, horns and beard.
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
from design_aoshin_hd import lp  # noqa: E402
from pack_aoshin_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aoshin")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 76                     # hd/idle.png's height
HEAD_SCALE = 1.0
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (20, 0, 58, 34)     # the design's head (the gold mask, the eyes, the horns, the beard) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "tail": (0, 200, 220), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Tail0", "Neck1", "Neck2", "Neck3", "Neck4", "Head"],
          "tail": ["Tail0", "Tail1", "Tail2", "Tail3", "Tail4", "Tail5", "Tail6", "Tail7", "Tail8", "Tail9", "Tail10",
                   "Tail11"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle1"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle1"],
          "L_leg": ["L_Hip", "L_Knee", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_Knee", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw", "Horn", "Hair")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_coil": ("attack2@0", 35, "普攻起手：身子往后一缩、头压低，蓄势要扑",
               "COIL - the body drawn back, the head low, gathering to lunge."),
    "a_lunge": ("attack@190", 35, "球状闪电：整个身体往右前方扑出去，嘴张开（闪电球从嘴里吐出）",
                "LUNGE - the whole body thrown forward to the front-right, the jaw open (the ball lightning leaves the "
                "mouth)."),
    "a_back": ("attack@570", 35, "收势：身体往回收，重新竖起来（接近定稿）",
               "RECOVER - pulling back, rising upright again (close to the design)."),
    "q_rear": ("spell@190", 35, "雷息蓄力：竖直立起、头往后仰，吸一口气",
               "REAR - straight up, the head tipped back, drawing breath."),
    "q_breath": ("attack3@380", 35, "雷息：头和脖子猛地往前伸出去，嘴张大喷出闪电，身体跟着往前压低",
                 "BREATH - the head and neck thrust far forward, the jaw wide open breathing lightning, the body "
                 "leaning low behind it."),
    "e_rise": ("spell_loop@1286", 35, "腾云：身体往后仰着飞起来，两只爪子护在胸前（向后飞开）",
               "CLOUD RIDE - leaning back and rising, both claws held up in front of the chest (flying away "
               "backwards)."),
    "r_call": ("spell@571", 35, "闪电暴雨起手：竖直悬浮，两只爪子举起、张开",
               "CALL - hovering straight up, both claws raised and spread."),
    "r_storm": ("celebrate@1500", 35, "闪电暴雨：挺胸，两条手臂向两边张开召来雷云",
                "STORM - the chest thrust out, both arms flung wide to call down the storm."),
    "run1": ("run@0", 35, "飞行 1：身体放平向前飞，尾巴拖在后上方",
             "FLY 1 - the body level, flying forward, the tail trailing up behind."),
    "run2": ("run@130", 35, "飞行 2：身体波浪起伏往下", "FLY 2 - the body undulating down."),
    "run3": ("run@260", 35, "飞行 3：最低处、身体拉长", "FLY 3 - at the lowest, the body stretched."),
    "run4": ("run@400", 35, "飞行 4：往上抬起", "FLY 4 - rising again."),
    "d_hit": ("death@300", 35, "阵亡 1：被击中，竖直往后一挺", "STRUCK - hit, jerking upright and back."),
    "d_back": ("death@900", 35, "阵亡 2：仰面翻过去，两爪张开", "THROWN BACK - flipped over face-up, both claws spread."),
    "d_away": ("death@2200", 35, "阵亡 3：转过身去、无力地垂着（之后淡出）",
               "SLUMPED - turned away, hanging limp (then he fades)."),
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
    ap.add_argument("--out", default=r"C:\t\ao_work\aoshin_pose_pack")
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
    pel = poser.names["Tail0"]
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
