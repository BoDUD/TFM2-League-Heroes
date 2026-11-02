#!/usr/bin/env python3
"""The Rift Herald's (峡谷先锋) pose pack for Codex (assets/source/riftherald/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's
TFTSet16.wad.client, so its skeletons are its animator's - the Cinderling's way).

    python tools/art/pack_riftherald_poses.py [--out D:/TFM2-Workshop/riftherald_packs/riftherald_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_riftherald_picture.CLIPS), the head grown by HEAD_SCALE. All are seen
from the design's angle (3/4 facing right, yaw 50). One scale for all: the design pose's whole height (idle@0, the frame
step 0's A was drawn from: the shell's top to the soles) = the design's 88 rows (hd/idle.png: A-1 at 44 game px, PPU
2.0) at PX px a square; the lowest point of every pose on y SOLE_Y - except the poses in AIR, which keep their height
above the design's ground (the flip into the charge) - its root on the design's root column (PELVIS_COL: None places it
by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's face 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), PINK = the L_ front arm (shoulder to pincer), CYAN = the R_ front
arm, RED = the L_ hind leg, BLUE = the R_ hind leg, YELLOW = the tail, grey box = the head. The two small rear arms are
left out (they hide under the shell).
Its run is TFT's own (run, 1.17 s): six frames over ONE full cycle, both feet's passings in it (the tft run rule).
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
from design_riftherald_hd import lp  # noqa: E402
from pack_riftherald_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "riftherald")
PX, CANVAS, SOLE_Y = 8, 1254, 1176
ROWS = 88                     # hd/idle.png's height
HEAD_SCALE = 1.2             # the model's small face grown toward the design's (Codex wears the design's face anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (60, 18, 104, 56)   # the design's face (the magenta eyes, the fangs, the near tusk) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 50
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (235, 200, 0)}
CHAINS = {"spine": ["Root", "Spine1", "Spine2", "Neck", "Head"],
          "L_arm": ["Spine2", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand", "L_Index1", "L_Index2"],
          "R_arm": ["Spine2", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Hand", "R_Index1", "R_Index2"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_Toe"],
          "tail": ["Pelvis", "C_Tail1", "C_Tail2", "C_Tail3", "C_Tail4", "C_Tail5"]}
HEAD_JOINTS = ("Head", "Jaw", "L_Eye", "R_Eye")
AIR = {"e_flip"}   # kept at its height above the ground
BURIED = set()

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_raise": ("attack@220", 50, "普攻「裂钳」举起：上身抬起，近处那只大钳爪高高举起、张开，准备砸下",
                "RAISE - the upper body lifted, the near big pincer raised high and open, about to strike down."),
    "a_strike": ("attack@450", 50, "普攻砸下：身子往前压，大钳爪往前下方砸到地面高度，钳口合上",
                 "STRIKE - lunging forward, the pincer slammed down and forward to the ground, its jaws shut."),
    "q_wind": ("spin@120", 50, "技能1「回旋横扫」起手：身子往一边扭，两只钳爪往外张开，尾巴甩向另一边",
               "WIND UP - the body twisting to one side, both pincers swung out wide, the tail swung the other way."),
    "q_spin": ("spin@350", 50, "转圈：身子转过去（看到一部分背甲和背后的粉红竖眼），钳爪和尾巴平着甩出去",
               "SPIN - turned half round (part of the shell's back and the pink slit eye show), pincers and tail "
               "flung out flat."),
    "q_end": ("spin@650", 50, "转回来：身子转回朝右，钳爪还张在两边，尾巴扫过身前",
              "SPIN END - turned back to face right, the pincers still spread wide, the tail sweeping in front."),
    "e_rear": ("spell@1900", 50, "技能2「虚空冲锋」蓄力 / 大招长啸：后腿直立站起来，头往上仰，两只钳爪张开举在身前（和原图 B 一样）",
               "REAR UP - standing upright on its hind legs, the head tilted up, both pincers open and raised in "
               "front (like step 0's picture B)."),
    "e_flip": ("charge@340", 70, "冲锋翻身：往前一扑、翻过身去，头朝下、背甲朝前（身子腾空）",
               "FLIP - diving forward and rolling over, head down, the domed shell leading (off the ground)."),
    "e_charge": ("charge@900", 70, "冲锋：翻过来用背甲朝前顶着往前冲，钳爪收在身下，尾巴拖在后面",
                 "CHARGE - rolled over, ramming forward shell first, the pincers tucked under, the tail trailing."),
    "r_crouch": ("spell@900", 50, "大招「扭曲护甲」蓄力：身子压低、缩进甲壳，钳爪收在胸前",
                 "CROUCH - pressed low, drawn into its shell, the pincers pulled to the chest."),
    "r_slam": ("spell@2600", 50, "大招猛击：从直立状态往前扑下，两只钳爪一起砸在身前地面上",
               "SLAM - crashing down forward from upright, both pincers smashed into the ground in front."),
    "run1": ("run@0", 50, "小跑 1（一整个循环的 6 帧之一，6 接回 1）", "RUN 1 of 6 - one full cycle, 6 runs on into 1."),
    "run2": ("run@195", 50, "小跑 2", "RUN 2 of 6."),
    "run3": ("run@390", 50, "小跑 3", "RUN 3 of 6."),
    "run4": ("run@585", 50, "小跑 4", "RUN 4 of 6."),
    "run5": ("run@780", 50, "小跑 5", "RUN 5 of 6."),
    "run6": ("run@975", 50, "小跑 6", "RUN 6 of 6."),
    "d_fall": ("death@300", 50, "被打倒：往一边歪倒，钳爪松开，尾巴甩起",
               "FALL - toppling over sideways, the pincers going limp, the tail flung up."),
    "d_down": ("death@1000", 50, "倒地：翻倒在甲壳上不动，眼睛和甲壳上的洋红斑熄灭（画成暗紫色）",
               "DOWN - lying still, rolled onto its shell, the eyes and the magenta spots gone dark (a dull dark "
               "violet, no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_riftherald_picture's renders (mirrored: facing image right)."""

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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\riftherald_packs\riftherald_pose_pack")
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

    ixy, _ = Poser.project(poser.pose(DESIGN)[0], YAW, scale, 0.0, 0.0)
    idle_ground = SOLE_Y - ixy[:, 1].max()
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        if name in AIR or name in BURIED:   # its height above (or depth under) the design's ground kept
            ground = idle_ground
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
        if name in BURIED:   # under the ground: nothing to draw
            ImageDraw.Draw(ref).rectangle((0, SOLE_Y + 1, CANVAS, CANVAS), fill=GREY + (255,))
            grid(ImageDraw.Draw(ref))
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "yaw", yaw, "near", near_leg(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
