#!/usr/bin/env python3
"""The Crimson Raptor's pose pack for Codex (assets/source/raptor/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's
TFTSet18.wad.client, so its skeletons are its animator's - the Sentinel's, Nomsy's and Zippy's way).

    python tools/art/pack_raptor_poses.py [--out D:/TFM2-Workshop/raptor_packs/raptor_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_raptor_picture.CLIPS), the head grown by HEAD_SCALE (the design's
head is bigger than the model's). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all:
the design pose's whole height (idle@0, the frame step 0's A was drawn from: the crest to its claws) = the design's 56
rows (hd/idle.png: A-1 at 36 game px, PPU 1.56, 1:1) at PX px a square; the lowest point of every pose on y SOLE_Y,
its root on the design's root column (PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (rump to the head and the lower beak), BROWN = the tail, PINK = the L_ wing,
CYAN = the R_ wing, RED = the L_ leg, BLUE = the R_ leg (the renders are mirrored: which side is nearer the camera is
written per pose), grey box = the head.
Its run (TFT's quick hopping bird run, 1.2 s a full cycle of both legs) is sampled evenly at RUN_MS over the whole
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
from design_raptor_hd import lp  # noqa: E402
from pack_raptor_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "raptor")
PX, CANVAS, SOLE_Y = 10, 1254, 1176
ROWS = 56                     # hd/idle.png's height
HEAD_SCALE = 1.3             # the model's head grown toward the design's (Codex wears the design's head anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (44, 16, 75, 52)    # the design's head (the brown hooked beak, the two orange eyes) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "tail": (140, 90, 40), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210),
       "L_leg": (230, 30, 30), "R_leg": (40, 90, 230)}
# (not from Spine1_null: an animated null that leaves the body in the spawn and death clips)
CHAINS = {"spine": ["Pelvis", "Spine1", "Head", "Jaw"],
          "tail": ["Tail1", "Tail2", "Tail3"],
          "L_wing": ["L_Wing1", "L_Wing2"],
          "R_wing": ["R_Wing1", "R_Wing2"],
          "L_leg": ["Pelvis", "L_Hip", "L_Knee", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_Knee", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Jaw", "Tongue")
RUN_MS = (0, 150, 300, 450, 600, 750, 900, 1050)   # one full 1.2 s cycle of both legs, evenly
RUN_ZH = ("跑 1：近处的腿往前伸、准备落地，远处的腿在后面蹬地",
          "跑 2：近处的腿落地，身子压低",
          "跑 3：近处的腿撑住、往后蹬，远处的腿收起往前",
          "跑 4：近处的腿蹬到最后，远处的腿抬到最高（腾空）",
          "跑 5：远处的腿往前伸、准备落地，近处的腿在后面",
          "跑 6：远处的腿落地，身子压低",
          "跑 7：远处的腿往后蹬，近处的腿收起往前",
          "跑 8：远处的腿蹬到最后，近处的腿抬到最高（8 接回 1，循环）")
RUN_EN = ("RUN 1 - the near leg reaching forward to land, the far leg pushing off behind.",
          "RUN 2 - the near leg landing, the body dipping low.",
          "RUN 3 - the near leg planted and pushing back, the far leg tucking up and swinging forward.",
          "RUN 4 - the near leg pushed back to the end, the far leg at its highest (in the air).",
          "RUN 5 - the far leg reaching forward to land, the near leg behind.",
          "RUN 6 - the far leg landing, the body dipping low.",
          "RUN 7 - the far leg pushing back, the near leg tucking up and swinging forward.",
          "RUN 8 - the far leg pushed back to the end, the near leg at its highest (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_back": ("attack@333", 35, "普攻「锋羽射击」起手：羽冠和背羽一下竖起炸开，脑袋往后上方缩、蓄力",
               "GATHER - the crest and back feathers bristling up, the head drawn back and up, winding up."),
    "a_jab": ("attack@666", 35, "射出：脑袋猛地往前一探、嘴张开（嘴里橙光），身子压低前冲，尾羽往后拉直",
              "JAB - the head thrust sharply forward, the beak open (the orange glow inside), the body low and "
              "lunging, the tail stretched straight back."),
    "q_rear": ("attack2@350", 35, "技能1「羽刃扇射」起手：身子往后仰，两只小翅膀开始张开，羽冠竖起",
               "REAR - the body rearing back, the two small wings starting to open, the crest raised."),
    "q_spread": ("attack2@500", 35, "甩出：两只翅膀和羽冠全部张开成一大圈扇形（红紫两色尖羽），嘴张大朝前",
                 "FAN OUT - both wings and the crest spread wide into a big fan of red and purple spiky feathers, "
                 "the beak wide open facing front."),
    "e_hop": ("spawn@200", 35, "技能2「惊飞跃退」：受惊往后一跳，整只鸟腾在空中，两条腿收在身下、爪子张开",
              "HOP - startled, hopping backwards: the whole bird up in the air, both legs tucked under it, the talons "
              "spread."),
    "e_land": ("spawn@600", 35, "落地：两脚着地蹲低，嘴张开尖叫（嘴里橙光），羽毛还炸着",
               "LAND - landed on both feet, crouched low, the beak open screeching (the orange glow inside), the "
               "feathers still bristling."),
    "r_rear": ("roar@200", 35, "大招「鸟群之家」起手：两条腿站直、身子挺高，脑袋往后仰",
               "RISE - standing up tall on straight legs, the body raised, the head tipped back."),
    "r_call": ("roar@400", 35, "召唤：仰头张大嘴大叫（嘴张到最大，嘴里橙光），羽冠竖起，呼唤小鸟",
               "CALL - the head up, the beak open as wide as it goes (the orange glow inside), the crest raised, "
               "calling the flock."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@150", 35, "被打倒：猛地往后仰、踉跄，嘴张开，两条腿离地乱蹬",
               "HIT DOWN - thrown back rearing and staggering, the beak open, both legs kicking off the ground."),
    "d_down": ("death@1000", 35, "倒地：翻倒侧躺在地上不动，两条腿朝天，眼睛熄灭（画成暗褐色，不发光）",
               "DOWN - toppled over onto its side, lying still, the legs up, the eyes gone dark (a dull dark brown, "
               "no glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_raptor_picture's renders (mirrored: facing image right)."""

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
    """Which leg and wing are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part in ("leg", "wing"):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part]])
        out.append(("L" if zl > zr else "R") + "_" + part)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\raptor_packs\raptor_pose_pack")
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
