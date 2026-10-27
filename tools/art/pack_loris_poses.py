#!/usr/bin/env python3
"""Loris's pose pack for Codex (assets/source/loris/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet16.wad.client, so his
skeletons are his animator's - Silco's and Maddie's way).

    python tools/art/pack_loris_poses.py [--out C:/t/lo_work/loris_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_loris_picture.CLIPS, named by what they show), the head grown to the
design's (pose_ref.chibi, HEAD_SCALE 2.0: the design's head with the hair is about 0.25 of his height, TFT's model's
0.13). Most are seen from the design's angle (3/4 facing right, yaw 35); his charge and the lifted shield are turned
further (yaw 70) - in those clips he turns toward the camera behind the shield, which would hide all of him. One scale
for all: the design pose's whole height (attack@0, the frame step 0's B was drawn from: hair to soles) = the design's
84 rows (hd/idle.png: B-1 at 42 game px, PPU 2.0) at PX px a square; the lowest point of every pose on y SOLE_Y, his
pelvis on the design pose's pelvis column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = the FIST arm (the joints' L_ chain; the
renders are mirrored), PURPLE = the SHIELD arm, RED = left leg, BLUE = right leg, GOLD outline = the shield (his model's shield seen in that
frame), a GOLD ring = the TOP of the shield (the end with the star emblem), grey box = the head.
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
from design_loris_hd import lp  # noqa: E402
from pack_loris_picture import Model, CLIPS, SHIELD, drop  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "loris")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 84                     # hd/idle.png's height
HEAD_SCALE = 2.0
DESIGN = "attack@0"            # the frame step 0's B was drawn from
YAW = 35
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "shield": (210, 160, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle3"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle3"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw", "Eye", "Brow", "Lip", "Nose", "Mouth", "MidFace")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack2@199", 35, "普攻起手：半蹲，远处的手把巨盾从身侧提到身前举起来，准备抡出去",
               "WIND-UP - dropping into a half crouch, the far arm lifting the great shield from his side up in front "
               "of him, about to swing it."),
    "a_bash": ("attack@385", 70, "盾击：巨盾横着抡过头顶砸向右边，近处的拳头同时往右（画面右边）打出去",
               "SHIELD BASH - the shield swung flat over his head toward the image right, the near fist punching out "
               "to the image right at the same time, legs braced wide."),
    "a_back": ("attack2@1599", 35, "收势：站直，巨盾回到身侧竖着，拳头收回胸前（和定稿差不多）",
               "RECOVER - standing up again, the shield back upright at his side, the fist back at his chest (close "
               "to the design)."),
    "q_raise": ("spell@600", 70, "皮城争斗起手：压低重心，把巨盾举到身前（画面右边）挡住，准备冲锋",
                "BRACE - crouching low, the great shield raised in front of him to the image right like a wall, ready "
                "to charge."),
    "q_charge1": ("charge@0", 70, "冲锋 1：顶着巨盾往右猛冲，前脚迈出，身子压在盾后面",
                  "CHARGE 1 - rushing to the image right behind the raised shield, the front foot stepping out, his "
                  "weight thrown behind the shield."),
    "q_charge2": ("charge@237", 70, "冲锋 2：两脚交错，盾还顶在身前", "CHARGE 2 - the legs passing, the shield still "
                  "held up in front."),
    "e_plant": ("idle@0", 35, "盾卫 / 嘲讽：巨盾立在身前的地上、双臂交叉搭在盾沿上（金铲铲的待机，第 0 步的 A）",
                "PLANTED - the great shield standing on the ground in front of him, both forearms crossed on its top "
                "edge, his head and shoulders over it (step 0's picture A)."),
    "r_lift": ("spell@277", 70, "钢铁防线举盾：双手把巨盾高高举过头顶（盾在头的右上方，不挡脸）",
               "LIFT - both arms heaving the great shield up high above his head, the shield above the right of his "
               "head (never over the face)."),
    "r_slam": ("spell@450", 35, "砸地：巨盾狠狠砸进身前的地里，人半蹲在盾后面压住",
               "SLAM - the shield driven down into the ground in front of him, he crouches behind it pressing it "
               "down."),
    "run1": ("run@0", 35, "跑步 1：盾提在身侧沉重地小跑（金铲铲原样），前脚迈出",
             "RUN 1 - a heavy jog with the shield carried upright at his side (as in the game), the front foot "
             "stepping out."),
    "run2": ("run@283", 35, "跑步 2：两脚交错", "RUN 2 - the legs passing."),
    "run3": ("run@566", 35, "跑步 3：另一只脚迈出", "RUN 3 - the other foot stepping out."),
    "run4": ("run@850", 35, "跑步 4：两脚交错", "RUN 4 - the legs passing again."),
    "d_fall": ("death@170", 35, "被击倒：人被打得往后一仰、仰头，巨盾脱手、竖着往他身后（画面左边）倒",
               "STRUCK - he reels back, his head thrown up, the shield slipping from his hand and tipping over "
               "upright behind him (image left)."),
    "d_kneel": ("death@511", 80, "跪倒：双膝跪地、低着头，巨盾平躺在他身后（画面左边）的地上",
                "KNEEL - down on his knees, head bowed, the shield lying flat on the ground just behind him (image "
                "left)."),
    "d_down": ("death@1362", 80, "倒地：整个人扑倒在地上（头朝画面右边），巨盾平躺在他身后的地上",
               "DOWN - lying face down on the ground, his head to the image right, the shield lying flat on the "
               "ground just behind him (image left)."),
}
# the death clip flings the shield far off (its model frame would leave the canvas): hidden, the prompt places it
NO_SHIELD = {"d_fall", "d_kneel", "d_down"}


class Poser:
    """His mesh (head grown) and joints, projected as pack_loris_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris
        _n, si, ic = self.m.subs[SHIELD]
        self.shield = np.unique(self.m.tris[si // 3:(si + ic) // 3].ravel())

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


def hull(pts):
    """The convex outline of 2D points (monotone chain), counter-clockwise."""
    pts = sorted(set(map(tuple, np.round(pts, 1))))
    if len(pts) < 3:
        return pts

    def half(ps):
        out = []
        for p in ps:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(p)
        return out
    return half(pts)[:-1] + half(pts[::-1])[:-1]


def skeleton(poser, joints, xy, z, hbox, shield, out, base=None):
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
    if shield is not None:   # (its outline, its top)
        outline, p = shield
        d.line(outline + outline[:1], fill=COL["shield"], width=7)
        d.ellipse([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14], outline=COL["shield"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "ORANGE (the fist arm)" if zl > zr else "PURPLE (the shield arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\lo_work\loris_pose_pack")
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
    head = design.crop((8, 0, 44, 24))
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    # the shield's top: its highest vertex in the design pose, followed through every pose
    top = poser.shield[np.argmax(iv[poser.shield, 1])]
    notes = {}
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        keep = np.setdiff1d(np.arange(len(xy)), poser.shield) if name in NO_SHIELD else np.arange(len(xy))
        ground = SOLE_Y - xy[keep, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge
        body = np.setdiff1d(np.arange(len(xy)), poser.shield) if name in NO_SHIELD else np.arange(len(xy))
        # (percentiles: a few loose fragment vertices of his mesh fly off with the death clip's shield)
        lo, hi = np.percentile(xy[body, 0], 0.5) + shift, np.percentile(xy[body, 0], 99.5) + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        shield = None if name in NO_SHIELD else (hull(xy[poser.shield]), tuple(xy[top]))
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, joints, jxy, jz, hbox, shield, os.path.join(a.out, f"{stem}_skeleton.png"),
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        tris = drop(poser.m.tris, poser.m.subs, {SHIELD}) if name in NO_SHIELD else poser.tris
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
