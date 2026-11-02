#!/usr/bin/env python3
"""Baron Nashor's pose pack for Codex (assets/source/baronnashor/POSE_PROMPTS.md): the whole-body poses of its actions,
each on a skeleton projected from game clips. TFT's Baron has NO legs (a serpent column out of the ground), but the
user had Codex give the design two short hind legs (「画个腿，不然怎么看出来走动」), so every pose is two models at once:
  - the body (the S-curved neck, the head, the two small heads, the two low claws) from Baron's OWN clips
    (pack_baronnashor_picture.CLIPS; TFTSet16.wad.client: Root Spine_1-3 Neck Head Face Jaw, L/R_MiniBaron1-3/_Head =
    the small heads on their thin arms, L/R_LargeArm_Shoulder/Elbow/Hand = the low claws), its world ground point
    (where the column comes out of the earth; its mesh reaches below its Root joint) on the design's hips;
  - the legs from T-Hex's (the same set's two-legged dinosaur, pack_thex_picture.CLIPS: Pelvis L/R_Hip KneeUpper
    KneeLower Foot ToeB1), its Pelvis on the same hips, scaled so its idle leg (pelvis to the lowest toe) is the
    design's leg (HIP_ROW to the soles); a pose with LEGS None has none (under the ground).

    python tools/art/pack_baronnashor_poses.py [--out D:/TFM2-Workshop/baronnashor_packs/baronnashor_pose_pack] [--lol "D:/Riot Games/League of Legends"]

All are seen from the design's angle (3/4 facing right, yaw 35). Baron's scale: its idle's projected height from its
ground point to the crest tips = the design's HIP_ROW rows (hd/idle.png: A-1 at 46 game px, PPU 2.04, 1:1) at PX px a
square. Every pose's lowest leg point on y SOLE_Y (a pose without legs: Baron's ground point there, and nothing of him
below the ground line is drawn); the hips on the design's HIP_COL column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (Baron's model in that frame, textured, legless, with the leg skeleton drawn over it) and
<k>_<name>_skeleton.png (its bones on the grid).
Skeleton colours: green = the spine (the hips to the head), purple = the jaw, PINK / CYAN = the L_ / R_ small head on its
arm, YELLOW / ORANGE = the L_ / R_ low claw, RED = the L_ leg, BLUE = the R_ leg, grey box = the head.
Its run is T-Hex's bird-legged run (1.27 s a full cycle of both legs) at RUN_MS: the L (red) foot lifted ~60-570 ms, the
R (blue) ~570-1140 (tft-run-full-cycle: a half cycle reads as legs that never swap); the body is Baron's idle at the
same ms, bobbing with T-Hex's pelvis.
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
import pack_baronnashor_picture as BP  # noqa: E402
import pack_thex_picture as TP  # noqa: E402
from design_baronnashor_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "baronnashor")
PX, CANVAS, SOLE_Y = 9, 1254, 1176
ROWS = 94                    # hd/idle.png's height
HIP_ROW, HIP_COL = 70, 31    # the design's hips (the purple gem above the legs), where both models meet
DESIGN = "idle@0"
HEAD_BOX = (24, 16, 48, 42)  # the design's head: the blue head, the eyes, the red mouth, the tusks
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "jaw": (140, 60, 200), "L_mini": (240, 80, 170), "R_mini": (0, 190, 210),
       "L_claw": (225, 195, 0), "R_claw": (255, 130, 0), "L_leg": (230, 30, 30), "R_leg": (40, 90, 230)}
BARON = {"spine": ["Root", "Spine_1", "Spine_2", "Spine_3", "Neck", "Head"],
         "jaw": ["Head", "Face", "Jaw"],
         "L_mini": ["Neck", "L_MiniBaron1", "L_MiniBaron2", "L_MiniBaron3", "L_MiniBaron_Head"],
         "R_mini": ["Neck", "R_MiniBaron1", "R_MiniBaron2", "R_MiniBaron3", "R_MiniBaron_Head"],
         "L_claw": ["Root", "L_LargeArm_Shoulder", "L_LargeArm_Elbow", "L_LargeArm_Hand"],
         "R_claw": ["Root", "R_LargeArm_Shoulder", "R_LargeArm_Elbow", "R_LargeArm_Hand"]}
LEGS = {"L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_ToeB1"],
        "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_ToeB1"]}
SOLES = ("L_Foot", "L_ToeB1", "L_ToeB2", "L_ToeB3", "R_Foot", "R_ToeB1", "R_ToeB2", "R_ToeB3")
HEAD_JOINTS = ("Head", "Face", "Jaw")
RUN_MS = (0, 159, 317, 476, 635, 794, 952, 1111)   # one full 1.27 s cycle: the L (red) foot's swing, then the R (blue)
RUN_ZH = ("跑 1：红线那条腿在后面刚要抬起来往前迈，蓝线那条腿踩地；身子微微前倾，头往前探",
          "跑 2：红线的腿抬起来往前送",
          "跑 3：红线的腿抬到最高，在身子下面往前摆",
          "跑 4：红线的腿在前面落下来",
          "跑 5：红线的腿踩地，蓝线的腿在后面开始抬（换脚）",
          "跑 6：蓝线的腿抬起来往前送",
          "跑 7：蓝线的腿抬到最高，在身子下面往前摆",
          "跑 8：蓝线的腿在前面落下来（8 接回 1，循环）")
RUN_EN = ("RUN 1 - the RED-line leg behind, just about to lift and step forward, the BLUE-line leg planted; the body "
          "leaning forward a little, the head pushed forward.",
          "RUN 2 - the RED-line leg lifted, swinging forward.",
          "RUN 3 - the RED-line leg at its highest, swinging forward under the body.",
          "RUN 4 - the RED-line leg coming down in front.",
          "RUN 5 - the RED-line leg planted, the BLUE-line leg starting to lift behind (the change of feet).",
          "RUN 6 - the BLUE-line leg lifted, swinging forward.",
          "RUN 7 - the BLUE-line leg at its highest, swinging forward under the body.",
          "RUN 8 - the BLUE-line leg coming down in front (8 runs on into 1: the loop).")

# name -> (Baron clip@ms, T-Hex legs clip@ms or None, what it is for (Chinese), the pose line (English))
POSES = {
    "a_rear": ("attack@416", "idle@0", "普攻「腐蚀撕咬」起手：身子往后一仰，头高高抬起、嘴张开，准备咬下去",
               "REAR BACK - the neck drawn back and up, the head high, the mouth open, about to strike."),
    "a_bite": ("attack@560", "idle@0", "咬下去：头往前下方猛地一咬，大嘴张到最大",
               "BITE - the head snapping down and forward, the jaws opened wide."),
    "q_breath": ("spell2@957", "idle@0", "技能1「腐蚀吐息」：头往前低低探出、大嘴张开朝前喷（酸液我后面画），两只爪子张开",
                 "BREATH - the head thrust low and forward, the mouth wide open toward the front (the acid comes "
                 "out of it later, not drawn), both low claws spread."),
    "e_dive": ("burrow@300", "rise@0", "技能2「钻地突袭」：压低身子蹲下、头往下扎，准备钻进地里",
               "DIVE - crouched low on bent legs, the head ducking down toward the ground, about to burrow."),
    "e_dig": ("burrowed@400", None, "在地下穿行：整个身子都在地下，只有头冠的几根鳍刺露在地面上（地面和土堆是特效，不画）",
              "UNDERGROUND - the whole body under the ground: only the tips of the crest fins stick up above the "
              "ground line (the earth itself is drawn later, not here)."),
    "e_rise": ("unburrow@300", "rise@200", "破土而出：从地里猛地蹿出来，身子挺直往上，头高高抬起",
               "BURST OUT - springing up out of the ground, the body shooting straight up, the head held high."),
    "r_rear": ("spell@478", "idle@0", "大招「虚空之怒」起手：伸直身子高高立起，头抬高、嘴大张，头冠鳍刺全竖起（你第 0 步 B 图那样）",
               "REAR UP - the body stretched straight up and tall, the head raised high, the mouth wide open, every "
               "crest fin standing up (like your picture B of step 0)."),
    "r_slam": ("spell@957", "idle@0", "猛砸：整个身子往前下方砸下去，头和两只爪子砸向地面（尖刺我后面画）",
               "SLAM - the whole body crashing down and forward, the head and both low claws driving into the "
               "ground (the spikes come later, not drawn)."),
    "r_spit": ("spell2@1436", "idle@0", "连续吐酸：头往前伸、嘴张开往前吐（酸液我后面画），身子微微前倾",
               "SPIT - the head pushed forward, the mouth open, spitting forward (the acid comes later, not drawn), "
               "the body leaning forward a little."),
    **{f"run{k + 1}": (f"idle@{t}", f"run@{t}", zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@1100", "death@2619", "被打倒：摇晃着往前侧身倒下去",
               "FALLING - swaying and toppling over sideways to the front."),
    "d_down": ("death@1165", "death@3666", "倒地：侧躺在地上不动，眼睛熄灭（画成暗黄、不发光）",
               "DOWN - lying on its side on the ground, still, the eyes gone dark (a dull dark yellow, no glow)."),
}
BARON_CLIPS = {**BP.CLIPS}


class Rig:
    """One model's mesh and joints, posed by its own clips and projected as the step-0 renders (mirrored: facing
    image right)."""

    def __init__(self, model, clips):
        self.m, self.clips = model, clips
        self.names = {j["name"]: i for i, j in enumerate(model.joints)}

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(self.clips[name]))
        t = float(ms) / 1000.0
        local = pose_ref.local_pose(self.m.joints, anim, t)
        glob = pose_ref.globals_(self.m.joints, [pose_ref.trs(*p) for p in local])
        verts = pose_ref.skin(self.m.v, self.m.infl, self.m.bind_inv, glob)
        return verts, np.array([g[:3, 3] for g in glob])

    def at(self, xy, name):
        return xy[self.names[name]]


def project(p, yaw, scale):
    """World points -> canvas offsets (x, y) before placing, and depth: render_hq's camera at -yaw, then mirrored."""
    y_ = np.radians(-yaw)
    cy, sy = np.cos(y_), np.sin(y_)
    cp, sp = np.cos(np.radians(PITCH)), np.sin(np.radians(PITCH))
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    v = p @ (rx @ ry).T
    return np.c_[-v[:, 0] * scale, -v[:, 1] * scale], v[:, 2]


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def draw_bones(d, chains):
    """chains: [(colour, [points], depth)], far ones first."""
    for colour, pts, _ in sorted(chains, key=lambda c: -c[2]):
        d.line(pts, fill=colour, width=7, joint="curve")
        for p in pts[:-1]:
            d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=colour)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\baronnashor_packs\baronnashor_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    baron = Rig(BP.Model(a.lol), BARON_CLIPS)
    thex = Rig(TP.Model(a.lol), TP.CLIPS)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # Baron's scale: its idle's ground point (the world origin, projected to 0) to its highest point = the design's
    # hips to its crest (HIP_ROW rows)
    bv, _ = baron.pose(DESIGN)
    sb = HIP_ROW * PX / -project(bv, YAW, 1.0)[0][:, 1].min()
    # T-Hex's legs: its idle's pelvis to its lowest toe = the design's leg (ROWS - HIP_ROW rows)
    _, tj = thex.pose("idle@0")
    txy = project(tj, YAW, 1.0)[0]
    low = max(thex.at(txy, s)[1] for s in SOLES)
    st = (ROWS - HIP_ROW) * PX / (low - thex.at(txy, "Pelvis")[1])
    print(f"scales: Baron {sb:.2f}, T-Hex legs {st:.2f}")

    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    hip_x = dx + HIP_COL * PX + PX // 2
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    hj0 = None
    for k, (name, (clip, legs, _zh, _en)) in enumerate([("idle", (DESIGN, "idle@0", "", ""))] + list(POSES.items())):
        verts, joints = baron.pose(clip)
        vxy, _ = project(verts, YAW, sb)
        jxy, jz = project(joints, YAW, sb)
        chains = []
        if legs is not None:
            _, lj = thex.pose(legs)
            lxy, lz = project(lj, YAW, st)
            pel = thex.at(lxy, "Pelvis")
            lxy = lxy - pel                                  # the legs about their pelvis
            hip_y = SOLE_Y - max(thex.at(lxy, s)[1] for s in SOLES)
            lxy = lxy + (hip_x, hip_y)
            for c, names in LEGS.items():
                chains.append((COL[c], [tuple(thex.at(lxy, n)) for n in names],
                               np.mean([lz[thex.names[n]] for n in names])))
        else:
            hip_y = SOLE_Y
        shift = np.array([hip_x, hip_y], dtype=float)   # the world origin (its ground point) on the hips
        # a pose that would leave the canvas (lying down) moved back inside, MARGIN from the edge
        lo, hi = np.percentile(vxy[:, 0], 0.5) + shift[0], np.percentile(vxy[:, 0], 99.5) + shift[0]
        dxm = max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        shift[0] += dxm
        chains = [(c, [(x + dxm, y) for x, y in pts], z) for c, pts, z in chains]
        vxy, jxy = vxy + shift, jxy + shift
        for c, names in BARON.items():
            pts = [tuple(baron.at(jxy, n)) for n in names]
            if c == "spine":   # down to the hips, where the legs join it
                pts = [tuple(shift)] + pts
            chains.append((COL[c], pts, np.mean([jz[baron.names[n]] for n in names])))
        # the grey box = the design's own head (HEAD_BOX on the canvas) carried by the Head joint from the idle
        hj = baron.at(jxy, "Head")
        if hj0 is None:
            hj0 = hj.copy()
        hbox = (dx + HEAD_BOX[0] * PX + hj[0] - hj0[0], dy + HEAD_BOX[1] * PX + hj[1] - hj0[1],
                dx + HEAD_BOX[2] * PX + hj[0] - hj0[0], dy + HEAD_BOX[3] * PX + hj[1] - hj0[1])
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        sk = Image.new("RGB", (CANVAS, CANVAS), GREY)
        d = ImageDraw.Draw(sk)
        grid(d)
        if name == "idle":   # the design under its own skeleton, faded
            sk = Image.blend(sk, can.convert("RGB"), 0.55)
            d = ImageDraw.Draw(sk)
        d.rectangle(hbox, outline=(110, 110, 110), width=3)
        draw_bones(d, chains)
        sk.save(lp(os.path.join(a.out, f"{stem}_skeleton.png")))
        if name == "idle":
            continue
        # Baron's textured model in the same place (render_hq: x = CANVAS - (v0 * scale + CANVAS * (0.5 + s)) after
        # the flip, y = ground - v1 * scale), the legs' bones over it
        s_ = 0.5 - shift[0] / CANVAS
        ground = shift[1]
        im = pose_ref.render_hq(verts.copy(), baron.m.tris, baron.m.v["uv"], baron.m.tex, -YAW, PITCH,
                                (CANVAS, CANVAS), sb, ground, shift=s_).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        if legs is None:   # under the ground: nothing below the ground line
            im = np.asarray(im).copy()
            im[SOLE_Y:, :, 3] = 0
            im = Image.fromarray(im)
        ref.alpha_composite(im)
        d = ImageDraw.Draw(ref)
        draw_bones(d, [c for c in chains if c[0] in (COL["L_leg"], COL["R_leg"])])
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, legs)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
