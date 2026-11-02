#!/usr/bin/env python3
"""The Elder Dragon's pose pack for Codex (assets/source/elderdragon/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from League's own clips for it (the TFT model carries League's sru_dragon_elder
skeleton; pack_elderdragon_picture.CLIPS names the clips - the Sentinel's and the Raptor's way).

    python tools/art/pack_elderdragon_poses.py [--out D:/TFM2-Workshop/elderdragon_packs/elderdragon_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips, the head grown by HEAD_SCALE (the design's head is bigger than the
model's). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole
height (idle@0, the frame step 0's A was drawn from: the highest wing tip to its claws) = the design's 125 rows
(hd/idle.png: A-1 at 44 game px, PPU 2.84, 1:1) at PX px a square (6: the design is 167 squares wide); the lowest point
of every pose on y SOLE_Y, its root on the design's root column (PELVIS_COL: None places it by the ratio of the design's
box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine and neck to the head and the jaw, BROWN = the tail, PINK = the L_ wing, CYAN = the
R_ wing, ORANGE = the L_ front leg, PURPLE = the R_ front leg, RED = the L_ hind leg, BLUE = the R_ hind leg (the renders
are mirrored: which side is nearer the camera is written per pose), grey box = the head.
League's Elder Dragon has no run: it moves FLYING LOW, its hover clip (2.33 s, one full beat cycle of the wings)
sampled evenly at RUN_MS (tft-run-full-cycle: the whole cycle); the ult's flight reuses those frames.
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
from design_elderdragon_hd import lp  # noqa: E402
from pack_elderdragon_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "elderdragon")
PX, CANVAS, SOLE_Y = 6, 1254, 1176
ROWS = 125                     # hd/idle.png's height
HEAD_SCALE = 1.6             # the model's head grown toward the design's (Codex wears the design's head anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (100, 70, 152, 118)   # the design's head (the jaw, the horns, the eye, the glowing mouth) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "tail": (140, 90, 40), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210),
       "L_front": (245, 150, 30), "R_front": (130, 60, 200), "L_leg": (230, 30, 30), "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Pelvis", "Root", "Spine1", "Spine2", "Spine3", "Spine4", "Neck", "Neck1", "Head", "Jaw"],
          "tail": ["Pelvis", "Tail1", "Tail2", "Tail3", "Tail4", "Tail5"],
          "L_wing": ["Spine4", "L_Wing_Clavicle", "L_Wing_Upper", "L_Wing_Mid1", "L_Wing_Mid", "L_Wing_Lower",
                     "L_Wing_Tip"],
          "R_wing": ["Spine4", "R_Wing_Clavicle", "R_Wing_Upper", "R_Wing_Mid1", "R_Wing_Mid", "R_Wing_Lower",
                     "R_Wing_Tip"],
          "L_front": ["Spine4", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Paw", "L_PawToe"],
          "R_front": ["Spine4", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Paw", "R_PawToe"],
          "L_leg": ["Pelvis", "L_Pelvis", "L_Hip", "L_Knee", "L_Ankle", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Pelvis", "R_Hip", "R_Knee", "R_Ankle", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw")
RUN_MS = (0, 291, 583, 875, 1166, 1458, 1750, 2041)   # one full 2.33 s beat of the wings (hover), evenly
RUN_ZH = ("飞 1：两只翅膀举到最高，往上张开",
          "飞 2：翅膀开始往下扇",
          "飞 3：翅膀扇到一半，平着往两边伸",
          "飞 4：翅膀扇到最低，身子被托起",
          "飞 5：翅膀从最低处收拢往回提",
          "飞 6：翅膀往上提到一半",
          "飞 7：翅膀快要举到最高",
          "飞 8：翅膀回到最高（8 接回 1，循环）")
RUN_EN = ("FLY 1 - both wings raised to the top, spread upward.",
          "FLY 2 - the wings starting the downstroke.",
          "FLY 3 - the wings half way down, stretched out level to both sides.",
          "FLY 4 - the wings at the bottom of the stroke, the body lifted.",
          "FLY 5 - the wings folding in from the bottom, drawn back up.",
          "FLY 6 - the wings half way up.",
          "FLY 7 - the wings nearly at the top.",
          "FLY 8 - the wings back at the top (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_back": ("bite@600", 35, "普攻「龙焰撕咬」起手：脑袋往后上方一缩，脖子弯起来，嘴微张，蓄力",
               "GATHER - the head drawn back and up, the neck arched, the jaws a little open, winding up."),
    "a_bite": ("bite@950", 35, "咬：脑袋猛地往前下方一探，嘴张大咬下去（嘴里青光），前身压低前冲",
               "BITE - the head thrust forward and down, the jaws wide open biting (the cyan glow inside), the front of "
               "the body low and lunging."),
    "q_rear": ("breath@800", 35, "技能1「烈焰吐息」起手：前身稍抬，脑袋往后仰，嘴张开，胸口和嘴里的青光变亮（吸气）",
               "INHALE - the front of the body lifting a little, the head tipped back, the jaws open, the cyan glow in "
               "the chest and mouth brightening."),
    "q_breath": ("breath@1150", 35, "喷火：脖子往前伸直、脑袋压低朝前，嘴张到最大（嘴里亮青光）——火焰之后单独画，这里不画",
                 "BREATHE - the neck stretched straight forward, the head low facing front, the jaws open as wide as "
                 "they go (bright cyan inside) - the fire itself is drawn later, NOT here."),
    "e_rear": ("wings@300", 35, "技能2「龙翼风暴」起手：前身立起来，两只大翅膀高高举过头顶完全张开",
               "REAR UP - the front of the body rearing up, both big wings raised high over the head, fully spread."),
    "e_slam": ("wings@600", 35, "扇下：两只翅膀猛地往下往前拍到底，前爪落地，身子压低",
               "BEAT DOWN - both wings beaten hard down and forward to the bottom, the front paws back on the ground, "
               "the body low."),
    "r_jump": ("leap@856", 35, "大招「绝伦火热」起飞：后腿一蹬跃上天空，翅膀张开往上举，四条腿收在身下",
               "TAKE OFF - springing up into the sky off the hind legs, the wings spread and raised, all four legs "
               "tucked under it."),
    "r_land": ("leap@1284", 35, "砸落：从天上砸回地面，四条腿重重着地、身子压到最低，翅膀往两边撑开",
               "SLAM DOWN - crashing back onto the ground, all four legs landing hard, the body pressed down as low as "
               "it goes, the wings braced out to both sides."),
    **{f"run{k + 1}": (f"hover@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@1070", 35, "被打倒：身子一沉，翅膀垂下，脑袋往下耷拉，腿开始发软",
               "SINKING - the body sagging, the wings drooping, the head hanging down, the legs giving way."),
    "d_down": ("death@2497", 35, "倒地：侧翻倒在地上不动，翅膀摊开，眼睛和嘴的青光熄灭（画成暗灰蓝色，不发光）",
               "DOWN - collapsed onto its side, lying still, the wings sprawled, the glow of the eyes and mouth gone out "
               "(a dull dark grey-blue, no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_elderdragon_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        wad, h = CLIPS[name]
        anim = pose_ref.read_anim(self.m.wads[wad].read(h))
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
    """Which leg and wing are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part in ("front", "leg", "wing"):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part]])
        out.append(("L" if zl > zr else "R") + "_" + part)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\elderdragon_packs\elderdragon_pose_pack")
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
