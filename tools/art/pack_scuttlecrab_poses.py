#!/usr/bin/env python3
"""The Scuttle Crab's pose pack for Codex (assets/source/scuttlecrab/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from League's river-crab clips (TFT's set-18 mesh rides League's sru_crab skeleton
exactly; pack_scuttlecrab_picture.Model), pack_meepsie_poses' way.

    python tools/art/pack_scuttlecrab_poses.py [--out D:/TFM2-Workshop/scuttle_packs/scuttle_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_scuttlecrab_picture.CLIPS), the face (the stone face plate and the
eyes) grown by HEAD_SCALE (the design's face is bigger than the model's; Codex puts the design's own face on every pose
anyway). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole
height (idle@0, the frame step 0's A was drawn from: the antenna tops to the lowest leg tips) = the design's 80 rows
(hd/idle.png: A-1 at 30 game px, PPU 2.667, 1:1) at PX px a square; the lowest point of every pose on y SOLE_Y (a pose
marked "world" keeps the idle's ground instead: climbing out of the earth, what is under the red line is underground),
its root on the design's root column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's face 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the body (root to the shell's centre), YELLOW = the L_ antenna, ORANGE = the R_ antenna, PINK =
the L_ claw, CYAN = the R_ claw, RED = the three L_ legs, BLUE = the three R_ legs (the renders are mirrored: which side
is nearer the camera is written per pose), grey box = the face plate with the eyes.
Its run (League's quick scuttle, 0.53 s a full cycle of all six legs) is sampled at RUN_MS over the whole cycle
(tft-run-full-cycle).
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
from design_scuttlecrab_hd import lp  # noqa: E402
from pack_scuttlecrab_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scuttlecrab")
PX, CANVAS, SOLE_Y = 8, 1254, 1100
ROWS = 80                     # hd/idle.png's height
HEAD_SCALE = 1.4             # the model's face plate and eyes grown toward the design's (Codex wears the design's anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (54, 20, 108, 70)   # the design's face plate and eyes in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
LEGS = ("Front", "Mid", "Back")
CHAINS = {"body": ["Root", "Crab"],
          "L_stalk": ["Crab", "L_Stalk1", "L_Stalk2", "L_Stalk3", "L_Stalk4", "L_Stalk5", "L_Stalk6", "L_Stalk_Tip"],
          "R_stalk": ["Crab", "R_Stalk1", "R_Stalk2", "R_Stalk3", "R_Stalk4", "R_Stalk5", "R_Stalk6", "R_Stalk_Tip"],
          "L_claw": ["Crab", "L_Shoulder", "L_Elbow", "L_Wrist", "L_Claw"],
          "R_claw": ["Crab", "R_Shoulder", "R_Elbow", "R_Wrist", "R_Claw"],
          **{f"{s}_{leg}_leg": ["Crab", f"{s}_{leg}_Hip", f"{s}_{leg}_Knee", f"{s}_{leg}_Ankle", f"{s}_{leg}_Foot"]
             for s in "LR" for leg in LEGS}}
COL = {"body": (0, 170, 60), "L_stalk": (235, 200, 0), "R_stalk": (245, 130, 20), "L_claw": (240, 80, 170),
       "R_claw": (0, 190, 210), **{f"L_{leg}_leg": (230, 30, 30) for leg in LEGS},
       **{f"R_{leg}_leg": (40, 90, 230) for leg in LEGS}}
HEAD_JOINTS = ("Mouth", "Eye")
RUN_MS = (0, 66, 133, 199, 265, 331, 398, 464)   # one full 0.53 s cycle of the scuttle
RUN_ZH = tuple(f"跑 {k + 1}：小短腿飞快地倒腾（一圈 8 帧里的第 {k + 1} 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠"
               + ("；8 接回 1，循环" if k == 7 else "") for k in range(8))
RUN_EN = tuple(f"SCUTTLE {k + 1} - the short legs pattering fast (frame {k + 1} of an 8-frame cycle: the legs of each "
               "side lifting and setting down in turn, as in its reference), the shell bobbing with them."
               + (" 8 runs on into 1: the loop." if k == 7 else "") for k in range(8))

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English)[, "world"])
POSES = {
    "a_rise": ("dance@913", 35, "普攻「螃蟹舞」起手：用腿撑着整个站高，两只小钳子高高举起，触角竖直",
               "UP ON ITS LEGS - standing up tall on all its legs, both little claws raised high, the antennae "
               "straight up."),
    "a_hop": ("dance@1370", 35, "跳：一蹦跳离地面，腿在身下收起来，钳子往两边摆（舞步）",
              "HOP - bounced off the ground, the legs tucked under it, the claws swinging out to the sides (a dance "
              "step)."),
    "a_stomp": ("dance@685", 35, "落地踩：重重落回地面，身子压低，腿往外撑开（这一下打到身边一圈的敌人）",
                "STOMP - landing back hard, the body pressed low, the legs splayed out (this beat strikes everyone "
                "round it)."),
    "q_raise": ("idle_up@500", 35, "技能1「疾行神龛」起手：身子挺起来，两根触角往上举",
                "RISE - the body lifting up, both antennae swinging upward."),
    "q_call": ("idle_up@913", 35, "召唤神龛：两根触角高高竖直、黄绿尖朝天，像在召唤什么（地上的神龛之后单独画）",
               "CALL - both antennae raised straight up, the lime tips to the sky, as if calling something up (the "
               "shrine on the ground is drawn later, NOT here)."),
    "e_tuck": ("tuck@266", 35, "技能2「蟹壳护盾」起手：触角和腿往回收，身子往下缩",
               "TUCK - the antennae and the legs pulling in, the body sinking down."),
    "e_shell": ("shell@0", 35, "缩进壳里：腿、钳子、脸和触角全缩进甲壳，只剩一个圆鼓鼓的甲壳趴在地上（护盾的光之后单独画）",
                "IN ITS SHELL - legs, claws, face and antennae all pulled in: only the round plated shell sitting on "
                "the ground (the shield's glow is drawn later, NOT here)."),
    "e_pop": ("pop@79", 35, "弹出来：从壳里一下弹出，腿伸开，触角甩起来",
              "POP OUT - springing back out of the shell, the legs out, the antennae flicking up."),
    "r_up1": ("rise@699", 35, "大招「你挖得动吗？」钻出地面 1：甲壳和脸从土里拱出来一半（红线以下在地下，不画），触角往两边甩",
              "BURST OUT 1 - the shell and the face pushing half out of the earth (what is under the red line is "
              "underground: do NOT draw it), the antennae flung out to the sides.", "world"),
    "r_up2": ("rise@932", 35, "钻出地面 2：整只蟹从土里蹦出来，腿还垂在身下",
              "BURST OUT 2 - the whole crab springing out of the earth, the legs still dangling under it.", "world"),
    "r_up3": ("rise@1165", 35, "钻出地面 3：整只蟹落回地面，腿撑开站稳，触角往后甩（之后接回待机）",
              "BURST OUT 3 - the whole crab landing back on the ground, the legs spread wide to stand firm, the "
              "antennae swinging back (then it runs on into its idle).", "world"),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_down": ("shell@0", 35, "死亡：缩进壳里不动，两根触角软软地瘫在地上，眼睛暗下去",
               "DEAD - curled up in its shell and still, the two antennae lying limp on the ground, the eyes dark."),
}


class Poser:
    """Its mesh (face grown) and joints, projected as pack_scuttlecrab_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.anims.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, 1.0, scale={j: HEAD_SCALE for j in ("L_Mouth", "R_Mouth", "L_Eye", "R_Eye")})
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
    """The vertices mostly weighted to the face (the stone plate and the eyes)."""
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
    """Which legs and claw are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part, name in (("Mid_leg", "legs"), ("claw", "claw")):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part]])
        out.append(("L" if zl > zr else "R") + "_" + name)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\scuttle_packs\scuttle_pose_pack")
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

    idle_ground = SOLE_Y - pxy[:, 1].max() * scale
    for k, (name, (clip, yaw, _zh, _en, *how)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = idle_ground if "world" in how else SOLE_Y - xy[:, 1].max()
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
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "yaw", yaw, "near", near_leg(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
