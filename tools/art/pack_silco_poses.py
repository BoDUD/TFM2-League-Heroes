#!/usr/bin/env python3
"""Silco's pose pack for Codex (assets/source/silco/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet13.wad.client, so his
skeletons are his animator's - Alune's way).

    python tools/art/pack_silco_poses.py [--out C:/t/sc_work/silco_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_silco_picture.CLIPS, named by what they show), the head grown to the
design's (pose_ref.chibi, HEAD_SCALE: the design's head is about a quarter of his height, TFT's model's a seventh) and
seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the idle frame's whole height (hair to soles)
= the design's 80 rows (hd/idle.png: step 0's A-1 at 40 game px, PPU 2.0) at PX px a square; the lowest point of every
pose on y SOLE_Y, his pelvis on the idle's pelvis column. The knife his TFT attacks swing is hidden (ours throw Shimmer
vials).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head, hair and face 8x: every pose wears it); per
pose <k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png
(its bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = his LEFT arm, PURPLE = his RIGHT arm,
RED = left leg, BLUE = right leg, GOLD = the cane (its two ends, from his model's cane), a GOLD ring = the Shimmer vial
in his hand, grey box = the head.
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
from design_silco_hd import lp  # noqa: E402
from pack_silco_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "silco")
PX, CANVAS, SOLE_Y = 13, 1254, 1176
ROWS = 80                     # hd/idle.png's height
HEAD_SCALE = 1.85
YAW = 35
HIDE = {"Knife"}
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "cane": (210, 160, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle3"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle3"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
VIAL = "Shimmer"
HEAD_JOINTS = ("Head", "Jaw", "hair", "Eye", "Brow", "Lip", "Nose", "Mouth", "Cheek")

# name -> (clip@ms, what it is for (Chinese), the pose line (English)), all seen at YAW
POSES = {
    "a_wind": ("attack@167", "普攻起手：身子往后一拧，近侧的手把一支微光药剂瓶举到肩膀后面（准备甩出去），另一只手夹着手杖",
               "WIND-UP - twisting back, his near hand lifting a glowing SHIMMER VIAL back over his shoulder, ready to "
               "fling it; the cane tucked under the other arm."),
    "a_throw": ("attack@333", "甩出药剂：身子往前探，近侧的手往前（画面右边）一甩，药剂瓶刚离手",
                "FLING - leaning forward, the near arm whipped out to the image right, the vial just leaving his hand."),
    "a_back": ("attack@667", "收势：站直，甩完的手收回身侧",
               "RECOVER - standing straight again, the throwing hand coming back to his side."),
    "q_wind": ("spell@247", "罐装畸变体起手：身子压低，近侧的手垂在身侧下方握着一个小铁皮储罐（发绿光的玻璃窗），另一只手拄杖",
               "CANISTER WIND-UP - crouching a little, his near hand low at his side gripping a small metal CANISTER with "
               "a glowing green window, the other hand on the cane."),
    "q_throw": ("spell@617", "扔出储罐：近侧的手臂高高往前上方甩起（在头的右上方，不挡脸），身子往后仰，另一只手拄着手杖",
                "CANISTER THROW - his near arm flung high and forward above the right of his head (never over the face), "
                "leaning back, the other hand leaning on the cane."),
    "e_show": ("idle2@0", "微光注射起手：把药剂瓶举到脸旁边端详（瓶子在脸的右边，不挡眼睛）",
               "SHOW THE DOSE - the glowing vial raised beside his face, looking at it (the vial right of the face, never "
               "over the eyes)."),
    "e_toss": ("attack2@500", "抛给队友：远侧的手往身后（画面左边）一伸、把药剂瓶抛给后面的队友，近侧的手拄着手杖",
               "TOSS THE DOSE - his far arm swept back to the image left tossing the vial to an ally behind him, the near "
               "hand on the cane."),
    "r_raise": ("spell@123", "炼金狂潮起手：抬起一条腿、把手杖挥起来，另一只手托着一个巨大的储罐（比他的头大，发绿光）",
                "FLOOD WIND-UP - one knee raised, the cane swung up, the other hand heaving up a HUGE CANISTER (bigger than "
                "his head, glowing green) at his side."),
    "r_throw": ("spell@740", "扔出巨型储罐：手臂笔直举过头顶往前（画面右边）一挥，巨型储罐已经脱手，身子往后仰，拄着手杖",
                "FLOOD THROW - his arm thrust straight up and forward over his head (to the image right), the huge "
                "canister already gone, leaning back on the cane."),
    "run1": ("run@0", "走路 1：拄着手杖往前走（金铲铲原样），前脚迈出",
             "WALK 1 - walking forward leaning on the cane (as in the game), the front foot stepping out."),
    "run2": ("run@533", "走路 2：两脚交错，手杖点地",
             "WALK 2 - the legs passing, the cane planted."),
    "run3": ("run@1067", "走路 3：另一只脚迈出",
             "WALK 3 - the other foot stepping out."),
    "run4": ("run@1600", "走路 4：两脚交错，手杖往前提",
             "WALK 4 - the legs passing, the cane lifted forward."),
    "d_fall": ("death@200", "被击倒：身子往后一弓、双手往上甩开（不挡脸），手杖脱手飞起",
               "STRUCK DOWN - doubled back, both arms flung up (never over the face), the cane flying out of his hand."),
    "d_down": ("death@900", "倒地：单膝跪倒、一只手撑地、低着头，手杖掉在身边地上",
               "DOWN - fallen to one knee, one hand on the ground, his head hanging, the cane lying beside him."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_silco_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = pose_ref.drop_submeshes(self.m.tris, self.m.subs, HIDE)
        cane = [s for s in self.m.subs if s[0] == "M_Cane"][0]
        self.cane = np.unique(self.m.tris[cane[1] // 3:(cane[1] + cane[2]) // 3].ravel())

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


def skeleton(poser, joints, xy, z, hbox, cane, out, base=None):
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
    d.line([tuple(cane[0]), tuple(cane[1])], fill=COL["cane"], width=7)
    p = xy[poser.names[VIAL]]
    d.ellipse([p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12], outline=COL["cane"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "ORANGE (his left)" if zl > zr else "PURPLE (his right)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sc_work\silco_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # one scale for every pose: the idle's whole height = the design's rows
    iv, ij = poser.pose("idle@0")
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the idle's pelvis lands on the same canvas column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    ixy, _ = Poser.project(iv, YAW, scale, 0.0, 0.0)
    pelvis_x = dx + (ixy[pel, 0] - ixy[:, 0].min()) / (ixy[:, 0].max() - ixy[:, 0].min()) * design.width * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop((8, 0, 36, 22))
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, _zh, _en)) in enumerate([("idle", ("idle@0", "", ""))] + list(POSES.items())):
        yaw = YAW
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        cv = xy[poser.cane]   # the cane's two ends: its points farthest apart along its main axis
        c0 = cv - cv.mean(0)
        axis = np.linalg.svd(c0, full_matrices=False)[2][0]
        t = c0 @ axis
        cane = (cv[np.argmin(t)], cv[np.argmax(t)])
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, joints, jxy, jz, hbox, cane, os.path.join(a.out, f"{stem}_skeleton.png"),
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        im = pose_ref.render_hq(pv, poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS), scale,
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
