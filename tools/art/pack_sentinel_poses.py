#!/usr/bin/env python3
"""The Blue Sentinel's pose pack for Codex (assets/source/sentinel/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's
TFTSet18.wad.client, so its skeletons are its animator's - Nomsy's, Terra's and Zippy's way).

    python tools/art/pack_sentinel_poses.py [--out D:/TFM2-Workshop/sentinel_packs/sentinel_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_sentinel_picture.CLIPS), the head grown by HEAD_SCALE (the design's
head is bigger than the model's tiny one; Codex puts the design's own head on every pose anyway). All are seen from
the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole height (idle@0, the frame
step 0's A was drawn from: the shoulder boulders to its soles) = the design's 68 rows (hd/idle.png: A-1 at 40 game px,
PPU 1.7, 1:1) at PX px a square; the lowest point of every pose on y SOLE_Y, its root on the design's root column
(PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), PINK = the L_ arm (shoulder to fist), CYAN = the R_ arm, RED =
the L_ leg, BLUE = the R_ leg (the renders are mirrored: which side is nearer the camera is written per pose), grey box
= the head.
Its run (TFT's lumbering walk-run, 1.3 s a full cycle of both legs) is sampled at RUN_MS over the whole cycle: the R
foot lifted 0-350 ms and down at ~400, the L foot lifted 550-1000 and down at ~1050 (measured with C:/t/bg_work/gait.py;
tft-run-full-cycle: a half cycle reads as legs that never swap).
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
from design_sentinel_hd import lp  # noqa: E402
from pack_sentinel_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sentinel")
PX, CANVAS, SOLE_Y = 8, 1254, 1176
ROWS = 68                     # hd/idle.png's height
HEAD_SCALE = 1.4             # the model's head grown toward the design's (Codex wears the design's head anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (52, 8, 72, 30)     # the design's head (the pale stump, its notch and cyan eye) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Spine3", "Head"],
          "L_arm": ["Spine3", "L_Clavicle", "L_Shoulder", "L_ElbowUpper", "L_ElbowLower", "L_Wrist", "L_Hand",
                    "L_Middle1"],
          "R_arm": ["Spine3", "R_Clavicle", "R_Shoulder", "R_ElbowUpper", "R_ElbowLower", "R_Wrist", "R_Hand",
                    "R_Middle1"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head",)
RUN_MS = (0, 160, 330, 480, 650, 810, 980, 1140)   # one full 1.3 s cycle: the R foot's swing, then the L foot's
RUN_ZH = ("走 1：近处的脚刚抬起往前迈，远处的脚踩地；两只巨拳跟着前后摆",
          "走 2：近处的脚抬到最高、往前送",
          "走 3：近处的脚落地，重心压上去",
          "走 4：两脚都踩地，身子往前压（换脚）",
          "走 5：远处的脚抬起往前迈",
          "走 6：远处的脚抬到最高、往前送",
          "走 7：远处的脚落地",
          "走 8：两脚踩地换回近处的脚（8 接回 1，循环）")
RUN_EN = ("WALK 1 - the near foot just lifting to step forward, the far foot planted; the two huge fists swinging.",
          "WALK 2 - the near foot at its highest, swinging forward.",
          "WALK 3 - the near foot coming down, the weight onto it.",
          "WALK 4 - both feet on the ground, the body pressing forward (the change of feet).",
          "WALK 5 - the far foot lifting to step forward.",
          "WALK 6 - the far foot at its highest, swinging forward.",
          "WALK 7 - the far foot coming down.",
          "WALK 8 - both feet on the ground, back to the near foot (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_raise": ("attack@318", 35, "普攻「岩拳猛击」起手：一只巨拳高高举过头顶，身子往后挺，另一只拳头垂在身前",
                "RAISE - one huge fist raised high over its head, the body leaning back, the other fist hanging in "
                "front."),
    "a_slam": ("attack@635", 35, "砸下：举起的拳头狠狠砸到身前地上，身子往前压低，弓着背",
               "SLAM - the raised fist smashed down onto the ground in front, the body bent forward and low, the "
               "back hunched."),
    "q_raise": ("slam@254", 35, "技能1「双拳重砸」起手：两只巨拳一起抡到肩膀上方，身子挺起",
                "RAISE BOTH - both huge fists swung up to above the shoulders together, the body rising up."),
    "q_slam": ("slam@635", 35, "双拳砸地：两只拳头一起砸在身前地上，身子弓下去，脑袋压低",
               "BOTH FISTS DOWN - both fists smashed into the ground in front together, the body bent down, the head "
               "low."),
    "e_brace": ("spawn@2597", 35, "技能2「雕纹石肤」起手：两只巨拳收到胸前，弓背缩起来护住身子",
                "BRACE - both huge fists drawn in before the chest, hunched and closed up to guard its body."),
    "e_roar": ("spawn@3541", 35, "张开：两臂往两侧大张，挺起胸口（胸口的 V 形青光正对前方），像在怒吼",
               "SPREAD - both arms flung wide to the sides, the chest pushed out (the V of cyan glow facing front), "
               "as if roaring."),
    "r_raise": ("slam@381", 35, "大招「蔚蓝冲击波」起手：两只巨拳一起高高举过头顶，伸到最直，身子挺得最高",
                "BOTH FISTS HIGH - both huge fists raised together high over its head, the arms stretched straight up, "
                "the body at its tallest."),
    "r_slam": ("slam@762", 35, "猛砸地面：两只拳头一起狠狠砸进身前地面，身子深深弓下去，肩上的石块往前倾",
               "SMASH - both fists smashed together deep into the ground in front, the body bent far down, the "
               "shoulder boulders tipped forward."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@1241", 35, "被打倒：身子往前跪倒，两只拳头撑不住垂到地上",
               "FALLING - sinking forward onto its knees, both fists sagging to the ground, no longer holding it up."),
    "d_down": ("death@2793", 35, "倒地：整个趴倒在地上，碎成一堆石头不动，独眼熄灭（画成暗青色）",
               "DOWN - collapsed flat on the ground as a heap of stones, lying still, the one eye gone dark (a dull "
               "dark teal, no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_sentinel_picture's renders (mirrored: facing image right)."""

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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\sentinel_packs\sentinel_pose_pack")
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
