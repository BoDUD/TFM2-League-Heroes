#!/usr/bin/env python3
"""Maddie's pose pack for Codex (assets/source/maddie/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet13.wad.client, so her
skeletons are her animator's - Silco's way).

    python tools/art/pack_maddie_poses.py [--out C:/t/md_work/maddie_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_maddie_picture.CLIPS, named by what they show), the head grown to the
design's (pose_ref.chibi, HEAD_SCALE 2.0: the design's head with the beret is about 0.30 of her height, TFT's model's
0.17) and seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the idle frame's whole height
(beret to soles) = the design's 57 rows (hd/idle.png: step 0's A-1 at 38 game px, PPU 1.5) at PX px a square; the
lowest point of every pose on y SOLE_Y, her pelvis on the idle's pelvis column. Wanted (e_point) has no clip of its
own: it is her celebration's pointing arm, the rifle (which floats free in that clip) hidden - she keeps it on her
shoulder as in the idle.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head, beret and face 8x: every pose wears it); per
pose <k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png
(its bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = her LEFT arm, PURPLE = her RIGHT arm,
RED = left leg, BLUE = right leg, GOLD = the rifle (its two ends, from her model's rifle), a GOLD ring = the MUZZLE end,
grey box = the head.
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
from design_maddie_hd import lp  # noqa: E402
from pack_maddie_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "maddie")
PX, CANVAS, SOLE_Y = 18, 1254, 1176
ROWS = 57                     # hd/idle.png's height
HEAD_SCALE = 2.0
YAW = 35
HIDE = set()
RIFLE = "Maddie_Weapon_Mat"
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "rifle": (210, 160, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle3"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle3"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
MUZZLE = "Weapon_Shooter"
HEAD_JOINTS = ("Head", "Jaw", "Eye", "Brow", "Lip", "Nose", "Mouth", "MidFace")
NO_RIFLE = {"e_point"}   # the celebration's rifle floats free: hidden, drawn on her shoulder

# name -> (clip@ms, what it is for (Chinese), the pose line (English)), all seen at YAW
POSES = {
    "a_aim": ("attack@0", "普攻起手：两脚前后分开、膝盖微弯，双手把步枪端平在腰间，枪口朝右（画面右边）",
              "AIM - feet apart one before the other, knees a little bent, both hands holding the rifle level at her "
              "waist, the muzzle to the image right."),
    "a_fire": ("attack@250", "开枪：身子微微前压，枪口朝右，后坐力刚到（这一帧枪还平着）",
               "FIRE - leaning a little into the shot, the rifle level, the muzzle to the image right, the kick just "
               "starting."),
    "a_kick": ("attack@450", "后坐力：步枪被顶得枪口朝上竖起来（在头的左上方，不挡脸），双手还握着枪",
               "RECOIL - the kick throws the rifle up, the muzzle pointing up above the left of her head (never over "
               "the face), both hands still on it."),
    "a_back": ("attack@900", "放平：步枪重新端平在胸前，准备下一枪",
               "BACK DOWN - the rifle brought level again at her chest, ready for the next shot."),
    "q_crouch": ("spell@0", "连拨击锤起手：压低重心半蹲，枪托抵肩，枪口朝右",
                 "FAN WIND-UP - dropping into a half crouch, the stock at her shoulder, the muzzle to the image right."),
    "q_fire": ("spell@600", "连开 6 枪：半蹲、枪托抵肩、脸贴着枪，枪口朝右稳稳地连开（这一帧是开枪的瞬间）",
               "FAN THE HAMMER - half crouched, the stock at her shoulder, her cheek on the rifle, the muzzle steady to "
               "the image right, firing shot after shot (this frame: a shot going off)."),
    "e_point": ("dance@1200", "通缉令：步枪扛在近处的肩上（和待机一样），远处的手往前（画面右边）一伸、食指指向目标",
                "WANTED - the rifle resting on her near shoulder as in the idle, her far arm thrust out to the image "
                "right, the index finger pointing at the target."),
    "r_aim": ("spell@1100", "执法狙杀瞄准：蹲得更低更稳，枪托抵肩、眼睛贴着瞄具，枪口朝右，一动不动",
              "SNIPE AIM - crouched lower and steadier, the stock at her shoulder, her eye at the sight, the muzzle to "
              "the image right, holding perfectly still."),
    "r_fire": ("attack2@600", "狙击开火：巨大的后坐力把步枪顶得往后上方扬起（在头的左上方，不挡脸），身子往后一仰",
               "SNIPE SHOT - the huge kick throws the rifle up and back above the left of her head (never over the "
               "face), her body rocked back."),
    "run1": ("run@0", "跑步 1：端着步枪低姿小跑（金铲铲原样），前脚迈出",
             "RUN 1 - jogging low with the rifle held across her hips (as in the game), the front foot stepping out."),
    "run2": ("run@190", "跑步 2：两脚交错", "RUN 2 - the legs passing."),
    "run3": ("run@380", "跑步 3：另一只脚迈出", "RUN 3 - the other foot stepping out."),
    "run4": ("run@570", "跑步 4：两脚交错", "RUN 4 - the legs passing again."),
    "d_fall": ("death@150", "被击倒：被打得往后仰、双手往上甩开（不挡脸），步枪脱手",
               "STRUCK DOWN - thrown backwards, both arms flung up (never over the face), the rifle leaving her hands."),
    "d_down": ("death@650", "倒地：仰面倒在地上，步枪掉在身边",
               "DOWN - lying on her back on the ground, the rifle fallen beside her."),
}


class Poser:
    """Her mesh (head grown) and joints, projected as pack_maddie_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = pose_ref.drop_submeshes(self.m.tris, self.m.subs, HIDE)
        rifle = [s for s in self.m.subs if s[0] == RIFLE][0]
        self.rifle = np.unique(self.m.tris[rifle[1] // 3:(rifle[1] + rifle[2]) // 3].ravel())

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


def skeleton(poser, joints, xy, z, hbox, rifle, out, base=None):
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
    if rifle is not None:   # (butt, muzzle)
        d.line([tuple(rifle[0]), tuple(rifle[1])], fill=COL["rifle"], width=9)
        p = rifle[1]
        d.ellipse([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14], outline=COL["rifle"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "ORANGE (her left)" if zl > zr else "PURPLE (her right)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\md_work\maddie_pose_pack")
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
    head = design.crop((16, 0, 44, 20))
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
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge
        lo, hi = xy[:, 0].min() + shift, xy[:, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        rifle = None
        if name not in NO_RIFLE:   # the rifle's two ends along its main axis, the one nearer the muzzle bone second
            cv = xy[poser.rifle]
            c0 = cv - cv.mean(0)
            axis = np.linalg.svd(c0, full_matrices=False)[2][0]
            t = c0 @ axis
            ends = (cv[np.argmin(t)], cv[np.argmax(t)])
            mz = jxy[poser.names[MUZZLE]]
            rifle = ends if np.hypot(*(ends[1] - mz)) <= np.hypot(*(ends[0] - mz)) else ends[::-1]
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, joints, jxy, jz, hbox, rifle, os.path.join(a.out, f"{stem}_skeleton.png"),
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        tris = pose_ref.drop_submeshes(poser.m.tris, poser.m.subs, {RIFLE}) if name in NO_RIFLE else poser.tris
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
