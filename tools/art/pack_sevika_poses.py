#!/usr/bin/env python3
"""Sevika's pose pack for Codex (assets/source/sevika/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet13.wad.client, so her
skeletons are her animator's - Renni's way).

    python tools/art/pack_sevika_poses.py [--out C:/t/sv_work/sevika_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_sevika_picture.CLIPS, named by what they show), the head grown to
the design's (pose_ref.chibi, HEAD_SCALE). All are seen from the design's angle (3/4 facing right, yaw 35). One scale
for all: the design pose's body height (guard@0, the standing guard step 0's A was drawn from: hair to soles, the
mechanical arm left out) = the design's 70 body rows (hd/idle.png: A-1, PPU 1.8, 1:1) at PX px a square; the lowest
point of every pose on y SOLE_Y, her pelvis on the design pose's pelvis column. d_down has no clip of its own (TFT's
death throws her off the board): the start of her fall laid on its back (ROT degrees in the picture plane).
Her mechanical arm: the skeleton draws it itself - the CYAN L_ arm to the hand, then a PURPLE bar from the hand to the
CLAW TIPS (the arm's vertex farthest from its elbow, submesh Arm_Mat) with a GOLD triangle on them, and a purple ring
on the shoulder where the slot machine sits (L_ShoulderArmor).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = her R_ arm (the flesh arm), CYAN = her
L_ arm (the mechanical arm), RED = left leg, BLUE = right leg, PURPLE = the claws (a GOLD triangle at their tips) and
the slot machine's ring, grey box = the head.
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
from design_sevika_hd import lp  # noqa: E402
from pack_sevika_picture import Model, CLIPS, SKN  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sevika")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 70                     # hd/idle.png's body rows (hair to soles: rows 0-69)
HEAD_SCALE = 1.7
DESIGN = "guard@0"             # the standing guard step 0's A was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (4, 0, 35, 22)       # the design's head with the hair (hd/idle.png)
PELVIS_COL = 24                 # the design's pelvis column: between its legs (cols 10-19 and 29- at row 52)
ROT = -82                       # d_down: the fall laid on its back
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "spear": (120, 40, 170), "point": (230, 175, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle1"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Eye", "Brow", "Jaw", "Lip", "MouthCrnr", "Teeth", "NoseTip")
ARM_SUBMESH = "Arm_Mat"

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English)); a clip ending in "~" is laid down (ROT)
RUN = [
    (0, "跑 1：往前跑（金铲铲原样），机械臂收在胸前、随步子甩动",
     "RUN 1 - running forward (as in the game), the mechanical arm carried in front of her chest, swinging."),
    (117, "跑 2", "RUN 2"), (233, "跑 3", "RUN 3"), (350, "跑 4", "RUN 4"), (467, "跑 5", "RUN 5"),
    (584, "跑 6", "RUN 6"), (700, "跑 7", "RUN 7"), (817, "跑 8", "RUN 8"),
]
POSES = {
    "a_wind": ("guard@560", 35, "普攻（机械铁拳）1：机械臂往后上方一抡蓄力，举在肩后",
               "PUNCH WIND-UP - the mechanical arm drawn back and up behind her shoulder, loading."),
    "a_punch": ("guard@200", 35, "普攻 2：一记重拳打出去，机械臂伸直打向右前方，爪钳在最前面",
                "PUNCH - a heavy punch thrown, the mechanical arm thrust straight out to the front-right, the claws "
                "leading."),
    "a2_raise": ("uppercut@300", 35, "第三下（钳击）1：机械臂举过头顶，爪钳张开",
                 "CLAMP RAISE - the mechanical arm swung up over her head, the claws open."),
    "a2_clamp": ("uppercut@520", 35, "钳击 2：机械臂往前下方砸下去，爪钳合上夹住（不画目标）",
                 "CLAMP - the arm brought down forward, the claws snapping shut (do NOT draw the target)."),
    "q_flame": ("flame@0", 35, "喷火器：两脚分开站稳，机械臂平举朝右前方，爪钳张开对准前方（火焰之后单独画，不画）",
                "FLAMETHROWER - feet planted apart, the mechanical arm held LEVEL to the front-right, the claws "
                "open and aimed ahead (the flame comes later: do NOT draw it)."),
    "q_flame2": ("flame@330", 35, "喷火 2：同一个姿势，后坐力让身体和机械臂轻轻一顿",
                 "FLAMETHROWER 2 - the same pose, the recoil jolting her body and the arm slightly."),
    "e_wind": ("punch@475", 35, "伸缩拳 1：身体压低，机械臂往后拉、蓄力",
               "EXTENDO WIND-UP - body low, the mechanical arm pulled back, loading."),
    "e_punch": ("punch@760", 35, "伸缩拳 2：机械臂猛地往前打直，朝右前方（拳头带着弹簧飞出去，之后单独画，不画）",
                "EXTENDO PUNCH - the arm thrown straight out to the front-right (the fist flies off on a spring "
                "later: do NOT draw the fist or the spring)."),
    "e_back": ("punch@1427", 35, "伸缩拳 3：收回机械臂，回到架势",
               "EXTENDO RECOVER - the arm pulled back in, returning to the guard."),
    "r_dash": ("dash@95", 35, "嚼一嚼 1：压低身子往前猛冲，机械臂伸在前面",
               "CHOMP DASH - a low dive forward, the mechanical arm reaching out ahead."),
    "r_raise": ("chomp@214", 35, "嚼一嚼 2：机械臂高高举起，爪钳像嘴一样大大张开",
                "CHOMP RAISE - the mechanical arm raised high, the claws opened wide like a jaw."),
    "r_bite": ("chomp@428", 35, "嚼一嚼 3：机械臂狠狠往前下方砸下，爪钳咬合在面前的地上（目标就在那里，不画）",
               "CHOMP BITE - the arm slammed down forward, the claws biting shut on the ground in front of her (the "
               "target is there: do NOT draw it)."),
    "r_lift": ("chomp@856", 35, "嚼一嚼 4：把机械臂再抡起来，准备咬第二口",
               "CHOMP LIFT - the arm swung back up for the next bite."),
    **{f"run{i + 1}": (f"run@{ms}", 35, zh, en) for i, (ms, zh, en) in enumerate(RUN)},
    "d_fall": ("death@100", 35, "被击倒：被打得往后飞，机械臂甩开",
               "KNOCKED BACK - thrown up and back, the mechanical arm flung out."),
    "d_down": ("death@100~", 35, "倒地：仰面躺在地上，机械臂摊在身边",
               "DOWN - lying on her back on the ground, the mechanical arm lying beside her."),
}


class Poser:
    """Her mesh (head grown) and joints, projected as pack_sevika_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        laid = clip.endswith("~")
        name, ms = clip.rstrip("~").split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE)
        glob = pose_ref.globals_(self.m.joints, [pose_ref.trs(*p) for p in local])
        verts = pose_ref.skin(self.m.v, self.m.infl, self.m.bind_inv, glob)
        joints = np.array([g[:3, 3] for g in glob])
        if laid:   # laid down in the picture plane about the pelvis
            r = np.radians(ROT)
            c, s_ = np.cos(r), np.sin(r)
            rz = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])
            o = joints[self.names["Pelvis"]].copy()
            verts = verts.copy()
            verts[:, :3] = (verts[:, :3] - o) @ rz.T + o
            joints = (joints - o) @ rz.T + o
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


def vertices_of(poser, keys):
    """The vertices mostly weighted to the joints whose names hold one of `keys`."""
    m = poser.m
    joint_of = np.array(m.infl)[m.v["bones"].astype(np.int64)]
    main = joint_of[np.arange(len(m.v)), np.argmax(m.v["w"], axis=1)]
    sel = {i for i, j in enumerate(m.joints) if any(k in j["name"] for k in keys)}
    return np.isin(main, list(sel))


def arm_vertices(poser):
    """The mechanical arm's vertices: its submesh's vertex range."""
    b = poser.m.w.read_path(SKN)
    return pose_ref.submesh_vertex_maps(b, len(poser.m.v), [([ARM_SUBMESH], 1)]) == 1


def claw_line(xy, cv, hand_xy):
    """The hand and the claw tips on the canvas: of the claws' vertices (weighted to L_ClampA / L_ClampB) the one
    farthest from the hand."""
    p = xy[cv]
    tips = p[np.argmax(np.hypot(p[:, 0] - hand_xy[0], p[:, 1] - hand_xy[1]))]
    return tuple(hand_xy), tuple(tips)


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def skeleton(poser, joints, xy, z, hbox, out, spear, ring, base=None):
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
    butt, point = spear   # the shaft, then a triangle at the point
    d.line([butt, point], fill=COL["spear"], width=9)
    ux, uy = point[0] - butt[0], point[1] - butt[1]
    n_ = max(1e-6, float(np.hypot(ux, uy)))
    ux, uy = ux / n_, uy / n_
    tri = [(point[0] + ux * 30, point[1] + uy * 30), (point[0] - uy * 22, point[1] + ux * 22),
           (point[0] + uy * 22, point[1] - ux * 22)]
    d.polygon(tri, fill=COL["point"])
    d.ellipse([butt[0] - 9, butt[1] - 9, butt[0] + 9, butt[1] + 9], fill=COL["spear"])
    d.ellipse([ring[0] - 16, ring[1] - 16, ring[0] + 16, ring[1] + 16], outline=COL["spear"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "CYAN (the L_ arm)" if zl > zr else "ORANGE (the R_ arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sv_work\sevika_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = vertices_of(poser, HEAD_JOINTS)
    sv = arm_vertices(poser)
    cv = vertices_of(poser, ("L_Clamp",))
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size   # her hair starts on row 0

    # one scale for every pose: the design pose's body height (the arm left out) = the design's body rows
    iv, ij = poser.pose(DESIGN)
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[~sv, 1].max() - pxy[~sv, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the design pose's pelvis lands on the same column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - design.height * PX
    pelvis_x = dx + PELVIS_COL * PX + PX // 2   # the bbox-ratio way put the skeleton far left (Kobuko's lesson)
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, design.height * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] +
                                                            list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge (her body:
        # the arm lying beside her may run off it)
        lo, hi = xy[~sv, 0].min() + shift, xy[~sv, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        spear = claw_line(xy, cv, jxy[poser.names["L_Hand"]])
        ring = tuple(jxy[poser.names["L_ShoulderArmor"]])
        skeleton(poser, joints, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), spear, ring,
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        im = pose_ref.render_hq(pv, poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS), scale,
                                ground, shift=x0 / CANVAS - 0.5, tri_tex=poser.m.tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
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
