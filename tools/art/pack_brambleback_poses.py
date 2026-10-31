#!/usr/bin/env python3
"""The Crimson Brambleback's pose pack for Codex (assets/source/brambleback/POSE_PROMPTS.md): the whole-body poses of
its actions, each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's
TFTSet18.wad.client, so its skeletons are its animator's - the Sentinel's way).

    python tools/art/pack_brambleback_poses.py [--out D:/TFM2-Workshop/brambleback_packs/brambleback_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_brambleback_picture.CLIPS), the head grown by HEAD_SCALE (the
design's head is bigger than the model's tiny one; Codex puts the design's own head on every pose anyway). All are seen
from the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole height (idle@0, the
frame step 0's A was drawn from: the back branches to the claws) = the design's 68 rows (hd/idle.png: A-1 at 40 game
px, PPU 1.7) at PX px a square; the lowest point of every pose on y SOLE_Y, its root on the design's root column
(PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), PINK = the L_ arm (shoulder to claw), CYAN = the R_ arm, RED =
the L_ leg, BLUE = the R_ leg (the renders are mirrored: which side is nearer the camera is written per pose), grey box
= the head.
Its run (TFT's knuckle-walking gallop, 1.07 s a full cycle) is sampled at RUN_MS over the whole cycle (measured from
the claws' and toes' heights, 2026-10-31): the L claw swings 0-400 ms and lands at ~400, the R claw swings 540-940 and
lands at ~940; the R back foot swings 0-330, the L back foot 340-670 (tft-run-full-cycle: one whole cycle, both
passings).
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
from design_brambleback_hd import lp  # noqa: E402
from pack_brambleback_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "brambleback")
PX, CANVAS, SOLE_Y = 8, 1254, 1176
ROWS = 68                     # hd/idle.png's height
HEAD_SCALE = 1.4             # the model's head grown toward the design's (Codex wears the design's head anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (64, 18, 92, 44)    # the design's head (the wedge, its two red eyes, the forehead spiral) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Head"],
          "L_arm": ["Spine2", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand", "L_Claw"],
          "R_arm": ["Spine2", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Hand", "R_Claw"],
          "L_leg": ["Pelvis", "L_Hip", "L_Knee", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_Knee", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head",)
RUN_MS = (0, 133, 266, 400, 533, 666, 800, 933)   # one full 1.07 s cycle: the L claw's swing, then the R claw's
RUN_ZH = ("跑 1：粉线前爪刚离地往前抡，青线前爪撑在最前面；蓝线后腿抬起往前",
          "跑 2：粉线前爪抡起往前送，蓝线后腿在空中往前",
          "跑 3：粉线前爪抡到最高最前，蓝线后腿落到身子下面，红线后腿撑地",
          "跑 4：粉线前爪在最前面落地撑住；红线后腿抬起",
          "跑 5：青线前爪离地往前抡，红线后腿往前送",
          "跑 6：青线前爪抡起往前送，红线后腿落地",
          "跑 7：青线前爪抡到最高最前，两条后腿撑地",
          "跑 8：青线前爪在最前面落地撑住（8 接回 1，循环）")
RUN_EN = ("GALLOP 1 - the PINK front arm just leaving the ground to swing forward, the CYAN front claw planted far "
          "ahead; the BLUE back leg lifting forward.",
          "GALLOP 2 - the PINK front arm swinging up and forward, the BLUE back leg forward in the air.",
          "GALLOP 3 - the PINK front arm at its highest and furthest forward, the BLUE back leg landing under the "
          "body, the RED back leg planted.",
          "GALLOP 4 - the PINK front claw landing far ahead, the weight onto it; the RED back leg lifting.",
          "GALLOP 5 - the CYAN front arm leaving the ground to swing forward, the RED back leg swinging forward.",
          "GALLOP 6 - the CYAN front arm swinging up and forward, the RED back leg landing.",
          "GALLOP 7 - the CYAN front arm at its highest and furthest forward, both back legs planted.",
          "GALLOP 8 - the CYAN front claw landing far ahead (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_raise": ("attack@208", 35, "普攻「荆爪横扫」起手：用后腿立起身子，一只长臂把大爪高高举起，另一只撑着",
                "RAISE - rising on its back legs, one long arm lifting its big claws high, the other arm "
                "supporting."),
    "a_swipe": ("attack@416", 35, "横扫：举起的大爪往前往下狠狠扫到身前地上，身子往前扑低",
                "SWIPE - the raised claws raked down and forward onto the ground in front, the body lunging low."),
    "q_jump": ("leap@170", 35, "技能1「荆棘飞扑」跃起：四肢收在身下，整个身子腾空往前扑（脚离地）",
               "JUMP - springing into the air, all four limbs tucked under the body, flying forward (feet off "
               "the ground)."),
    "q_reach": ("leap@312", 35, "扑到最高：身子挺直，一只长臂把大爪高高举过头顶，准备扑下",
                "REACH - at the top of the pounce, the body stretched up, one long arm lifting its claws high over "
                "its head, about to strike down."),
    "q_land": ("leap@470", 35, "扑落：大爪砸在身前地上，四肢着地压低，身子往前压",
               "LAND - the claws crashing down onto the ground in front, landing low on all fours, the body pressed "
               "forward."),
    "e_crouch": ("roar@179", 35, "技能2「绯红咆哮」蓄力：四肢收拢、身子缩起来压低，背上的红核亮起",
                 "CROUCH - gathering itself, limbs drawn in, the body crouched low and tight, the red core on its "
                 "back glowing."),
    "e_rear": ("roar@537", 35, "怒吼：用后腿人立起来，挺起胸口，两只长臂张开，抬头怒吼",
               "REAR AND ROAR - standing up on its back legs, chest thrust out, both long arms spread, the head up, "
               "roaring."),
    "r_rear": ("slam@400", 35, "大招「猩红之怒」起手：人立到最高，两只大爪一起高高举过头顶",
               "BOTH CLAWS HIGH - reared up at its tallest on its back legs, both claws raised together high over "
               "its head."),
    "r_slam": ("slam@540", 35, "双爪砸地：两只大爪一起狠狠砸在身前地上，身子深深压低，背上的树枝往前倾",
               "SLAM - both claws smashed together into the ground in front, the body bent far down, the back "
               "branches tipped forward."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_rear": ("death@300", 35, "被打倒：猛地往后人立起来，两臂无力地垂着",
               "STAGGER - jerking up onto its back legs, both arms hanging limp."),
    "d_down": ("death@2050", 35, "倒地：整个趴平在地上不动，背上的红核和眼睛熄灭（画成暗红褐色）",
               "DOWN - collapsed flat on the ground, lying still, the red core and the eyes gone dark (a dull dark "
               "red-brown, no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_brambleback_picture's renders (mirrored: facing image right)."""

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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\brambleback_packs\brambleback_pose_pack")
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
