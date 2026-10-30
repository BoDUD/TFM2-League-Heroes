#!/usr/bin/env python3
"""Zippy's pose pack for Codex (assets/source/zippy/POSE_PROMPTS.md): the whole-body poses of its actions, each on a
skeleton projected from its OWN clips (its model and clips are in the Riot client's TFTSet7.wad.client, so its
skeletons are its animator's - Nomsy's and Terra's way).

    python tools/art/pack_zippy_poses.py [--out D:/TFM2-Workshop/zippy_packs/zippy_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_zippy_picture.CLIPS), the head grown by HEAD_SCALE (the design's head
is much bigger than the model's; Codex puts the design's own head on every pose anyway). All are seen from the design's
angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole height (idle@0, the frame step 0's A was
drawn from: the head spikes to its soles) = the design's 83 rows (hd/idle.png: A-1 at 38 game px, PPU 2.2, 1:1) at PX
px a square; the lowest point of every pose on y SOLE_Y (a pose in the air is drawn standing on the line too: the rig
lifts it), its root on the design's root column (PELVIS_COL: None places it by the ratio of the design's box to the
model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), RED = the L_ leg, BLUE = the R_ leg, BROWN = the tail, PINK = the
L_ feather lock (Kled's mount's "ears": the long pink feathers hanging from the neck, which spread like wings when it
leaps), CYAN = the R_ feather lock (the renders are mirrored: which side is nearer the camera is written per pose), grey
box = the head.
Its run (TFT's sprint, 0.8 s a full cycle of both legs) is sampled at RUN_MS: both passings (the toes level, ~260 and
~740 ms) and both reaches (the R toe 39 ahead at 120, the L toe 88 ahead at 520), measured with C:/t/zz_work/gait.py
(tft-run-full-cycle: a half cycle reads as legs that never swap). The near leg is R (the larger depth).
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
from design_zippy_hd import lp  # noqa: E402
from pack_zippy_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zippy")
PX, CANVAS, SOLE_Y = 10, 1254, 1176
ROWS = 83                     # hd/idle.png's height
HEAD_SCALE = 1.5             # the model's head grown toward the design's (Codex wears the design's head anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (20, 0, 52, 34)     # the design's head (the spikes, the black shards, the eye, the mouth) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_leg": (230, 30, 30), "R_leg": (40, 90, 230), "tail": (120, 70, 30),
       "L_feather": (240, 80, 170), "R_feather": (0, 190, 210)}
CHAINS = {"spine": ["Mount_Root", "Mount_Spine1", "Mount_Spine2", "Mount_Neck", "Mount_Head"],
          "L_leg": ["Mount_Pelvis", "Mount_L_Hip", "Mount_L_KneeUpper", "Mount_L_KneeLower", "Mount_L_Foot",
                    "Mount_L_Toe"],
          "R_leg": ["Mount_Pelvis", "Mount_R_Hip", "Mount_R_KneeUpper", "Mount_R_KneeLower", "Mount_R_Foot",
                    "Mount_R_Toe"],
          "tail": ["Mount_Pelvis", "Mount_Tail1", "Mount_Tail2", "Mount_Tail3", "Mount_Tail4"],
          "L_feather": ["Mount_Neck", "Mount_L_Ear_Mid1", "Mount_L_Ear_Mid2"],
          "R_feather": ["Mount_Neck", "Mount_R_Ear_Mid1", "Mount_R_Ear_Mid2"]}
HEAD_JOINTS = ("Head", "Jaw", "Lip", "Tongue", "Mouth", "Eye", "Brow")
RUN_MS = (0, 120, 260, 360, 480, 560, 660, 740)   # one full 0.8 s cycle: R reach, R ahead, passing, L ahead ... passing
RUN_ZH = ("跑 1：身子前倾平伸，尾巴往后伸直；近处（蓝）的腿在前、远处（红）的腿在后",
          "跑 2：近处的腿伸到最前",
          "跑 3：两腿交错（近处的腿踩地往后蹬，远处的腿抬起往前收）",
          "跑 4：远处的腿到前面",
          "跑 5：远处的腿伸到最前",
          "跑 6：远处的腿落地",
          "跑 7：两腿交错（远处的腿往后蹬，近处的腿往前收）",
          "跑 8：近处的腿回到前面（8 接回 1，循环）")
RUN_EN = ("RUN 1 - the body leaning forward level, the tail stretched straight back; the near (blue) leg ahead, the "
          "far (red) leg behind.",
          "RUN 2 - the near leg at its furthest forward.",
          "RUN 3 - PASSING: the legs cross (the near leg pushing back on the ground, the far leg lifted and coming "
          "forward).",
          "RUN 4 - the far leg now in front.",
          "RUN 5 - the far leg at its furthest forward.",
          "RUN 6 - the far leg coming down.",
          "RUN 7 - PASSING: the legs cross again (the far leg pushing back, the near leg coming forward).",
          "RUN 8 - the near leg in front again (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("celebration@633", 35, "普攻「利爪踢」起手：一条腿高高抬起、膝盖往前收，另一条腿站稳",
               "WIND UP - one leg raised high, the knee drawn up in front, standing firm on the other."),
    "a_kick": ("death@916", 35, "踢出：抬起的那条腿往前猛地蹬直，大爪朝前，身子和头往后仰（脸还是定稿那张，只是跟着往后倾）",
               "KICK - the raised leg thrust straight forward, the big claws first, the body and the head leaning back "
               "(still image A's face, only tilted back with the body)."),
    "q_crouch": ("attack@64", 35, "技能1「后空翻踢」起手：身子压低、两腿弯曲蓄力，头往后仰",
                 "CROUCH - the body low, both legs bent to spring, the head tipping back."),
    "q_flip": ("attack@258", 35, "后空翻：身子往后翻，一条腿高高踢过头顶（画在地面线上，游戏里会抬高）",
               "FLIP - the body flipping over backwards, one leg kicked high over its head (drawn standing on the "
               "ground line: the game lifts it)."),
    "q_kick": ("attack@387", 35, "踢中：翻到一半，两只脚往前上方踢出去，头在后下方",
               "KICK - halfway through the flip, both feet kicking up and forward, the head low behind."),
    "q_land": ("attack@516", 35, "落地：两脚落回地上，身子蹲低，头抬起来",
               "LAND - both feet back on the ground, the body crouched, the head coming up."),
    "e_curl": ("leap@670", 35, "技能2「翻滚冲锋」起手：身子蜷起来，两侧的玫红长羽毛往身前包，快要缩成一个球",
               "CURL - the body curling up, the long pink feathers at both sides wrapping round it, almost a ball."),
    "e_ball": ("spell@0", 35, "羽毛球：整个身子缩成一个圆球，外面是玫红长羽毛包着，露出一点马鞍和爪子（游戏里会让它转起来滚）",
               "BALL - the whole body curled into a round ball wrapped in the pink feathers, a bit of the saddle and "
               "the claws showing (the game spins it to roll)."),
    "r_crouch": ("leap@95", 35, "大招「翻滚突袭」起手：身子压低，两腿深蹲蓄力准备起跳",
                 "CROUCH - the body low, both legs deeply bent, about to spring."),
    "r_spring": ("leap@574", 35, "跃起：腾空往上跳，两腿收在身下，两侧的玫红长羽毛像翅膀一样张开（画在地面线上，游戏里会抬高）",
                 "SPRING - leaping up into the air, both legs tucked under the body, the long pink feathers at both "
                 "sides spread like wings (drawn standing on the ground line: the game lifts it)."),
    "r_open": ("curl@412", 35, "空中张开：从球里一下张开，羽毛像翅膀一样大张，嘴张大，两腿往下伸准备砸下去",
               "BURST OPEN - bursting out of the ball in the air, the feathers spread wide like wings, the mouth "
               "wide open, both legs reaching down to crash."),
    "r_land": ("curl@962", 35, "砸地落下：两腿着地、身子蹲低前倾，羽毛往后扬",
               "LAND - crashing down on both feet, the body crouched low and leaning forward, the feathers swept "
               "back."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@1166", 35, "被打倒：一条腿站着摇晃，身子往后仰，头往后甩（脸还是定稿那张，跟着往后倾）",
               "FALLING - staggering on one leg, the body tipping back, the head thrown back (still image A's face, "
               "tilted back with the body)."),
    "d_down": ("leap@862", 35, "倒地：缩成一个羽毛球躺在地上不动，眼睛闭上（画成 X 或一条线）",
               "DOWN - curled up in a feather ball lying still on the ground, the eyes shut (an X or a line)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_zippy_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, 1.0, scale={"Mount_Head": HEAD_SCALE})
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
    """The vertices mostly weighted to the head and what hangs off it (jaw, lips, tongue, eyes, brows)."""
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
    """Which leg is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_leg"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_leg"]])
    return "L" if zl > zr else "R"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\zippy_packs\zippy_pose_pack")
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
    pel = poser.names["Mount_Root"]
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
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near leg", near_leg(jz, poser))
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
        print(stem, clip, "yaw", yaw, "near leg", near_leg(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
