#!/usr/bin/env python3
"""Murk Wolf's pose pack for Codex (assets/source/murkwolf/POSE_PROMPTS.md): the whole-body poses of its actions,
each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's TFTSet18.wad.client, so
its skeletons are its animator's - the Raptor's way).

    python tools/art/pack_murkwolf_poses.py [--out D:/TFM2-Workshop/murkwolf_packs/murkwolf_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_murkwolf_picture.CLIPS), the heads grown by HEAD_SCALE (the
design's heads are bigger than the model's). Its clips have no howl: a pose's LIFT turns both necks (and all they
carry) about their roots in world space, the muzzles up for a negative lift, down for a positive one. All are seen
from the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole height (idle@0, the
frame step 0's A was drawn from: the tail tip to its claws) = the design's 60 rows (hd/idle.png: A-1 at 36 game px,
PPU 1.67, 1:1) at PX px a square; the lowest point of every pose on y SOLE_Y, its root on the design's root column
(PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's two heads 8x: every pose wears them); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (rump to shoulders), BROWN = the tail, ORANGE = the L_ neck and head (its last
stretch the lower jaw), YELLOW = the R_ neck and head, RED / BLUE = the L_ / R_ front leg, PINK / CYAN = the L_ / R_
hind leg (the renders are mirrored: which side is nearer the camera is written per pose), grey box = the heads.
Its run (TFT's stretched gallop, 0.8 s a full cycle of all four legs) is sampled evenly at RUN_MS over the whole
cycle (tft-run-full-cycle: a half cycle reads as legs that never swap).
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
from design_murkwolf_hd import lp  # noqa: E402
from pack_murkwolf_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "murkwolf")
PX, CANVAS, SOLE_Y = 10, 1254, 1176
ROWS = 60                     # hd/idle.png's height
HEAD_SCALE = 1.3             # the model's heads grown toward the design's (Codex wears the design's heads anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (38, 12, 83, 52)    # the design's two heads (ears, cyan eyes, pink mouths, white ruffs) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "tail": (140, 90, 40), "L_head": (245, 140, 0), "R_head": (230, 210, 0),
       "L_front": (230, 30, 30), "R_front": (40, 90, 230), "L_hind": (240, 80, 170), "R_hind": (0, 190, 210)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Spine3"],
          "tail": ["Pelvis", "Tail1", "Tail2", "Tail3", "Tail4"],
          "L_head": ["Spine3", "L_Neck", "L_Head", "L_Jaw"],
          "R_head": ["Spine3", "R_Neck", "R_Head", "R_Jaw"],
          "L_front": ["Spine3", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Paw", "L_PawToe"],
          "R_front": ["Spine3", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Paw", "R_PawToe"],
          "L_hind": ["Pelvis", "L_Hip", "L_Knee", "L_Ankle", "L_Foot", "L_Toe"],
          "R_hind": ["Pelvis", "R_Hip", "R_Knee", "R_Ankle", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("L_Head", "R_Head", "L_Jaw", "R_Jaw")   # (the ears hang from the heads: L_Head_L_Ear ...)
NECKS = ("L_Neck", "R_Neck")
RUN_MS = (0, 100, 200, 300, 400, 500, 600, 700)   # one full 0.8 s gallop, evenly
RUN_ZH = tuple(f"跑 {k}/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点"
               + ("（8 接回 1，循环）" if k == 8 else "") for k in range(1, 9))
RUN_EN = tuple(f"RUN {k} of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the "
               f"front legs, pink / cyan the hind legs), the body bobbing slightly with the stride"
               + (" (8 runs on into 1: the loop)." if k == 8 else ".") for k in range(1, 9))

# name -> (clip@ms, yaw, neck lift in degrees, what it is for (Chinese), the pose line (English))
POSES = {
    "a_back": ("attack@333", 35, 0, "普攻「双头撕咬」起手：身子往后一缩、压低，两个头收回、准备扑咬",
               "GATHER - the body drawn back and low, both heads pulled in, ready to snap."),
    "a_bite": ("attack@416", 35, 0, "咬下：往前一扑，两个头一起往前上方探出，两张嘴张到最大（粉色嘴里、黄色尖牙）",
               "BITE - lunging forward, both heads thrust forward and up, both jaws open as wide as they go (pink "
               "mouths, yellow fangs)."),
    "q_crouch": ("attack2@167", 35, 0, "技能1「撕裂之爪」起手：后腿蹲下蓄力，前身压低，准备起跳",
                 "CROUCH - the hind legs coiled, the chest low, about to spring."),
    "q_leap": ("attack2@333", 35, 0, "起跳扑向目标：整只狼用后腿蹬起、身子竖起来，两只前爪张开举高，两张嘴张开",
               "LEAP - springing up off the hind legs, the body reared upright, both front paws raised with the "
               "claws spread, both mouths open."),
    "q_rend": ("attack2@500", 35, 0, "落下撕扯：整个身子扑落压低，两只前爪往前下方狠狠抓下去，两个头低着咬",
               "REND - crashing down low, both front paws raking forward and down hard, both heads low and biting."),
    "e_gather": ("idle@0", 35, 15, "技能2「狂战士之嚎」起手：两个头低下来吸气，身子绷紧",
                 "BREATHE IN - both heads lowered, the body tense."),
    "e_howl": ("idle@0", 35, -55, "嚎叫：两个头一起高高仰起、嘴朝天张开长嚎，前腿撑住",
               "HOWL - both heads thrown back, muzzles pointing at the sky, mouths open howling, the front legs "
               "braced."),
    "r_growl": ("crouch@500", 35, 20, "大招「狼群攻击」起手：身子伏低，两个头压低龇牙低吼",
                "GROWL - crouched low, both heads down, baring the fangs."),
    "r_bark": ("attack@834", 35, -25, "号令狼群：站高、尾巴竖起，两个头朝前上方张嘴大吼",
               "COMMAND - standing tall, the tail raised high, both heads up and forward, mouths open barking."),
    **{f"run{k + 1}": (f"run@{t}", 35, 0, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@150", 35, 0, "被打倒：被掀翻，身子扭着往后仰，四条腿离地乱蹬，嘴张开",
               "THROWN - flipped up and twisting backwards, all four legs kicking off the ground, the mouths open."),
    "d_down": ("death@1333", 35, 0, "倒地：侧躺在地上不动，眼睛熄灭（画成暗灰色，不发光）",
               "DOWN - lying still on its side, the eyes gone dark (a dull dark grey, no glow)."),
}


class Poser:
    """Its mesh (heads grown) and joints, projected as pack_murkwolf_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def subtree(self, root):
        out = {root}
        for i, j in enumerate(self.m.joints):   # parents come first in SKL order
            if j["parent"] in out:
                out.add(i)
        return out

    def pose(self, clip, lift=0):
        name, ms = clip.split("@")
        wad, h = CLIPS[name]
        anim = pose_ref.read_anim(self.m.wads[wad].read(h))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, 1.0, scale={"L_Head": HEAD_SCALE, "R_Head": HEAD_SCALE})
        glob = pose_ref.globals_(self.m.joints, [pose_ref.trs(*p) for p in local])
        if lift:   # both necks turned about their roots, about the body's side-to-side axis (model x)
            c, s = np.cos(np.radians(lift)), np.sin(np.radians(lift))
            rot = np.eye(4)
            rot[1:3, 1:3] = [[c, -s], [s, c]]
            for neck in NECKS:
                n = self.names[neck]
                to, back = np.eye(4), np.eye(4)
                to[:3, 3], back[:3, 3] = glob[n][:3, 3], -glob[n][:3, 3]
                for k in self.subtree(n):
                    glob[k] = to @ rot @ back @ glob[k]
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
    """The vertices mostly weighted to the two heads (and their jaws and ears)."""
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


def near_side(z, poser):
    """Which head and legs are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part in ("head", "front", "hind"):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part][1:]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part][1:]])
        out.append(("L" if zl > zr else "R") + "_" + part)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\murkwolf_packs\murkwolf_pose_pack")
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
    # the design on the canvas: its soles on SOLE_Y, centred; every pose's root on the design's root column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    if PELVIS_COL is None:   # the model's root placed by the ratio of the design's box to the model's
        ix = Poser.project(iv, YAW, scale, 0.0, 0.0)[0][:, 0]
        jx = Poser.project(poser.pose(DESIGN)[1], YAW, scale, 0.0, 0.0)[0][pel, 0]
        x0, _, x1, _ = design.getbbox()
        col = x0 + (jx - ix.min()) / (ix.max() - ix.min()) * (x1 - x0)
        print("root column", round(col, 1))
        pelvis_x = dx + round(col * PX)
    else:
        pelvis_x = dx + PELVIS_COL * PX + PX // 2
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    for k, (name, (clip, yaw, lift, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, 0, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip, lift)
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (thrown, lying on the ground) moved back inside, MARGIN from the edge
        lo, hi = np.percentile(xy[:, 0], 0.5) + shift, np.percentile(xy[:, 0], 99.5) + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near", near_side(jz, poser))
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        im = pose_ref.render_hq(verts.copy(), poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS),
                                scale, ground, shift=-shift / CANVAS - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "lift", lift, "near", near_side(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
