#!/usr/bin/env python3
"""Nomsy's pose pack for Codex (assets/source/nomsy/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet7.wad.client, so her
skeletons are her animator's - Krug's way).

    python tools/art/pack_nomsy_poses.py [--out C:/t/nm_work/nomsy_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_nomsy_picture.CLIPS), the head as the model has it (HEAD_SCALE 1.0:
step 0's A was drawn close to the model). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for
all: the design pose's whole height (idle@0, the frame step 0's A was drawn from: the top of the far wing to her feet)
= the design's 94 rows (hd/idle.png: A-1 at 36 game px, PPU 2.6, 1:1) at PX px a square; the lowest point of every
pose on y SOLE_Y (a pose in the air is drawn standing on the line too: the rig lifts it), her root on the design's
root column (PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), ORANGE = the joints' L_ front leg, PURPLE = the R_ front leg,
RED = left hind leg, BLUE = right hind leg, BROWN = the short tail, PINK = the L_ wing, CYAN = the R_ wing (the renders
are mirrored: which one is nearer the camera is written per pose), grey box = the head.
The model's tongue is pulled back into the mouth in every pose (TONGUE_SCALE: TFT's attack lashes it out a body long);
in the poses that spread the wings (WING_POSES) both wings are shrunk to WING_SCALE (spread, TFT's wings span 2.5 of
her bodies: about 100 game px).
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
from design_nomsy_hd import lp  # noqa: E402
from pack_nomsy_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nomsy")
PX, CANVAS, SOLE_Y = 7, 1254, 1176
ROWS = 94                     # hd/idle.png's height
HEAD_SCALE = 1.0
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (72, 0, 129, 56)    # the design's head (the spikes, the eyes, the tusks, the mouth) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 60
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (120, 70, 30), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210)}
CHAINS = {"spine": ["Root", "Chest", "Neck", "Head"],
          "L_arm": ["L_Clavicle", "L_Arm", "L_Elbow", "L_Hand"],
          "R_arm": ["R_Clavicle", "R_Arm", "R_Elbow", "R_Hand"],
          "L_leg": ["Root", "L_Leg", "L_Knee", "L_Foot"], "R_leg": ["Root", "R_Leg", "R_Knee", "R_Foot"],
          "tail": ["Root", "Tail", "Tail1", "Tail2", "Tail3", "Tail4"],
          "L_wing": ["Chest", "L_Wing1", "L_Wing2", "L_Wing3"], "R_wing": ["Chest", "R_Wing1", "R_Wing2", "R_Wing3"]}
HEAD_JOINTS = ("Head", "Eye")
TONGUE_SCALE = 0.15
WING_SCALE = 0.5
WING_POSES = ("spell@362", "celebration@3250", "celebration@3550", "celebration@4000", "celebration@4162")
# the hover's body turned back to the design's: these joints take the idle's rotations, the wings and legs keep the
# flight's
HOVER_POSES = ("celebration@3250", "celebration@3550", "celebration@4000")
BODY_JOINTS = ("Root", "Chest", "Neck", "Head", "Tail", "Tail1", "Tail2", "Tail3", "Tail4", "Jaw")
# ...and their wings are drawn from the design's, not the model's (turned back with the body, the model's wings fold
# away behind her): the render leaves them out and the skeleton gets one straight line per wing from its root, in
# squares and degrees above the level (near = R_Wing, reaching back to the image left as in the design; far = L_Wing,
# rising behind her head to the image right): (near length, near angle, far length, far angle)
WING_LINES = {"celebration@3250": (44, 55, 34, 70), "celebration@3550": (48, 8, 36, 20),
              "celebration@4000": (44, -35, 32, -25)}
WING_JOINTS = ("L_Wing1", "L_Wing2", "L_Wing3", "R_Wing1", "R_Wing2", "R_Wing3")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_rear": ("attack@335", 35, "普攻起手：后腿撑着、上身抬起往后仰，头抬高，嘴巴闭着蓄力",
               "REAR BACK - on her hind legs, the upper body lifted and leaning back, the head high, the mouth shut, "
               "gathering a breath."),
    "a_spit": ("attack@558", 35, "吐小火团：头猛地往前伸，嘴张大（舌头留在嘴里，不要伸出来；火团之后单独画）",
               "SPIT - the head thrust forward, the mouth WIDE OPEN (the tongue stays inside the mouth, not lashed "
               "out; the fire is drawn separately later)."),
    "q_rise": ("spell@120", 35, "火球！起手：后腿蹬地、整个身子立起来，头朝天张嘴大吼",
               "RISE - pushing off the hind legs, the whole body upright, the head up to the sky, the mouth open in a "
               "roar."),
    "q_roar": ("spell@362", 35, "火球！跳在空中：身子蜷着、翅膀张开，张嘴朝前上方喷出火球（画在地面线上，游戏里会抬高）",
               "LEAP - up in the air, the body curled, the wings open, the mouth open towards the upper front "
               "throwing the fireball (drawn standing on the ground line: the game lifts it)."),
    "e_back": ("attack@223", 35, "龙息起手：上身抬起、头往后仰到最高，胸口鼓起来吸气",
               "INHALE - the upper body raised, the head thrown back as far as it goes, the chest puffed up."),
    "e_breath": ("attack@670", 35, "龙息：头低下来往前伸，嘴张到最大往前喷（火焰之后单独画）",
                 "BREATHE - the head lowered and stretched forward, the mouth open as wide as it goes, breathing "
                 "forward (the flame is drawn separately later)."),
    "r_up": ("celebration@3250", 35, "龙神飞升起飞 / 扇翅 1：在空中，两只翅膀高高举起（往上扬到最高），四条小短腿垂着（画在地面线上，游戏里会抬高）",
             "WINGS UP - in the air, both wings raised high (the top of the beat), the four stubby legs hanging "
             "(drawn on the ground line: the game lifts it)."),
    "r_fly1": ("celebration@3550", 35, "盘旋 / 扇翅 2：两只翅膀向两边平平展开",
               "WINGS LEVEL - the same hover, both wings spread out level to the sides."),
    "r_fly2": ("celebration@4000", 35, "盘旋 / 扇翅 3：两只翅膀往下扇到最低（扇翅 1→2→3→2 循环就是扇翅膀）",
               "WINGS DOWN - the same hover, both wings beaten down to the bottom (UP -> LEVEL -> DOWN -> LEVEL loops "
               "the flapping)."),
    "r_land": ("celebration@4162", 35, "落地：四脚落地、身子一沉，翅膀正在收起",
               "LANDING - down on all fours, the body sinking with the impact, the wings folding."),
    "run1": ("run@0", 35, "移动 1：摇摇摆摆地往前蹦", "WADDLE 1 - hopping forward in a waddle."),
    "run2": ("run@75", 35, "移动 2", "WADDLE 2."),
    "run3": ("run@150", 35, "移动 3", "WADDLE 3."),
    "run4": ("run@225", 35, "移动 4", "WADDLE 4."),
    "run5": ("run@300", 35, "移动 5", "WADDLE 5."),
    "run6": ("run@375", 35, "移动 6", "WADDLE 6."),
    "run7": ("run@450", 35, "移动 7", "WADDLE 7."),
    "run8": ("run@525", 35, "移动 8", "WADDLE 8."),
    "d_fall": ("death@249", 35, "被打倒：被打得往后一仰、身子立起来、两只前爪乱抓",
               "KNOCKED BACK - thrown back, the body upright, the front claws flailing."),
    "d_down": ("death@749", 35, "倒地：翻倒、四脚朝天躺在地上（金铲铲原样）",
               "DOWN - rolled over, lying on her back with all four feet in the air (as in TFT)."),
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
        if clip in HOVER_POSES:   # her body as in the design (TFT's flight turns her to face the camera, nose down)
            idle = pose_ref.local_pose(self.m.joints, pose_ref.read_anim(self.m.w.read(CLIPS["idle"])), 0.0)
            for n in BODY_JOINTS:
                i = self.names[n]
                local[i] = (local[i][0], idle[i][1], local[i][2])
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE)
        # the tongue pulled back into the mouth (TFT's attack lashes it out); the wings shrunk in the poses that spread
        # them (WING_POSES: TFT's flight wings span 2.5 bodies, too wide for the game)
        shrink = {"Tongue1": TONGUE_SCALE}
        if clip in WING_POSES:
            shrink.update({"L_Wing1": WING_SCALE, "R_Wing1": WING_SCALE})
        for n, k in shrink.items():
            i = self.names[n]
            t, r, sc = local[i]
            local[i] = (t, r, sc * k)
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
            p = pts[-1]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "L" if zl > zr else "R"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\nm_work\nomsy_pose_pack")
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
        tris = poser.tris
        if clip in WING_LINES:
            nl, na, fl, fa = WING_LINES[clip]
            for side, length, ang, sign in (("R", nl, na, -1), ("L", fl, fa, 1)):
                root = jxy[poser.names[f"{side}_Wing1"]].copy()
                step = np.array([sign * np.cos(np.radians(ang)), -np.sin(np.radians(ang))]) * length * PX
                jxy[poser.names[f"{side}_Wing2"]] = root + step * 0.45
                jxy[poser.names[f"{side}_Wing3"]] = root + step
            joint_of = np.array(poser.m.infl)[poser.m.v["bones"].astype(np.int64)]
            main_j = joint_of[np.arange(len(poser.m.v)), np.argmax(poser.m.v["w"], axis=1)]
            wing = np.isin(main_j, [poser.names[n] for n in WING_JOINTS])
            tris = tris[~wing[tris].any(axis=1)]
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near arm", near_arm(jz, poser))
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
        print(stem, clip, "yaw", yaw, "near arm", near_arm(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
