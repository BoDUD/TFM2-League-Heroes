#!/usr/bin/env python3
"""The Mighty Mech's pose pack for Codex (assets/source/mightymech/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's
TFTSet17.wad.client, so its skeletons are its animator's: Root Pelvis Spine1-3 Neck Head, L/R Clavicle Shoulder Elbow
Hand, L/R Hip KneeUpper/Lower Foot, Tail_1-4, Sword (a root bone of its own between the hands) and the blade-wings
L_Wing1-8_B / R_Wing1-8_SKN, each hung on Spine3).

    python tools/art/pack_mightymech_poses.py [--out D:/TFM2-Workshop/mightymech_packs/mightymech_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_mightymech_picture.CLIPS) at a yaw picked by eye (2026-11-03: the
clips' roots face different ways; each pose is turned to the design's 3/4), the head left at the model's size (the grey
box is the design's own head carried by the Head joint). One scale for all: the design pose's whole height
(sword_idle@500, the frame step 0's B was drawn from: the spike tips to its soles) = the design's 80 rows (hd/idle.png:
B-1 at 40 game px, PPU 2.0) at PX px a square; the lowest point of its body (not the blade-wings or the sword) on y SOLE_Y, its root on the design's root
column (by the ratio of the design's box to the model's).
Codex drew B as the MIRROR of the step-0 render (the sword forward to the right), so every picture here is the mirror of
pack_thex_poses' view: built the same way on the mirrored design, then flipped as a whole when saved.
The user picked B (the Ultimate form with the giant sword) as the look: it always holds the sword. Clips of its normal
form (no sword in hand: the stance, the leap, the transform, the breaking) leave the Sword bone lying on the ground;
there the sword is left out of the render and its line (DROPPED, by the bone's height) and the pose's line says how to
hold it.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), PINK = the L_ arm, CYAN = the R_ arm, RED = the L_ leg, BLUE =
the R_ leg, BROWN = the tail, BLACK = the sword (the hilt to the tip), DARK RED / ORANGE spokes = the L_ / R_ blade-wings,
grey box = the head.
Its run (TFT's walk with the sword held upright, 2.13 s a full cycle of both legs) is sampled at RUN_MS over the whole
cycle: the L (red) foot highest ~266 ms, the R (blue) ~1332 (gait probe 2026-11-03; tft-run-full-cycle: a half cycle
reads as legs that never swap).
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
from design_mightymech_hd import lp  # noqa: E402
from pack_mightymech_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "mightymech")
PX, CANVAS, SOLE_Y = 9, 1254, 1176
ROWS = 80                       # hd/idle.png's height
DESIGN = ("sword_idle@500", 20)  # the frame and yaw step 0's B was drawn from
HEAD_BOX = (34, 20, 50, 38)     # on hd/idle.png (design_mightymech_model.FACE_BOX): helmet, V horn, face plate, visor
MARGIN = 40
PITCH = 12
DROPPED = 15.0                  # the Sword bone this low: the clip leaves it on the ground (a normal-form clip)
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (150, 90, 40), "sword": (20, 20, 20), "L_wing": (150, 0, 30),
       "R_wing": (255, 130, 0)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Spine3", "Neck", "Head"],
          "L_arm": ["Spine3", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand"],
          "R_arm": ["Spine3", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Hand"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot"],
          "tail": ["Pelvis", "Tail_1", "Tail_2", "Tail_3", "Tail_4"]}
WINGS = {"L_wing": [f"L_Wing{k}_B" for k in range(1, 9)], "R_wing": [f"R_Wing{k}_SKN" for k in range(1, 9)]}
HEAD_JOINTS = ("Head", "Neck")
RUN_MS = (0, 266, 533, 799, 1066, 1332, 1598, 1865)   # one full 2.13 s cycle: the L (red) foot's step, then the R (blue)
RUN_ZH = ("跑 1：红线那条腿在后面刚要抬起来往前迈，蓝线那条腿踩地；双手握剑竖在身前，刃翼收在背后",
          "跑 2：红线的腿抬到最高，往前送",
          "跑 3：红线的腿在前面落下来",
          "跑 4：红线的腿踩地，蓝线的腿在后面（换脚）",
          "跑 5：蓝线的腿抬起来往前迈",
          "跑 6：蓝线的腿抬到最高，往前送",
          "跑 7：蓝线的腿在前面落下来",
          "跑 8：蓝线的腿踩地，红线的腿在后面（8 接回 1，循环）")
RUN_EN = ("RUN 1 - the RED-line leg behind, just about to lift and step forward, the BLUE-line leg planted; the giant "
          "sword gripped in both hands and held upright in front of the chest, the blade-wings folded behind.",
          "RUN 2 - the RED-line leg at its highest, swinging forward.",
          "RUN 3 - the RED-line leg coming down in front.",
          "RUN 4 - the RED-line leg planted, the BLUE-line leg behind (the change of feet).",
          "RUN 5 - the BLUE-line leg lifting, stepping forward.",
          "RUN 6 - the BLUE-line leg at its highest, swinging forward.",
          "RUN 7 - the BLUE-line leg coming down in front.",
          "RUN 8 - the BLUE-line leg planted, the RED-line leg behind (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_up": ("chop@208", 50, "普攻「活塞重斩」起手：双手把巨剑高高举过头顶，身子往后仰",
             "RAISE - the giant sword lifted high over its head in both hands, the body leaning back."),
    "a_down": ("chop@416", 20, "重斩落下：巨剑往前下方劈到底，剑尖指向右前方地面，弓步压低",
               "CHOP - the giant sword chopped down forward to the ground, the tip low in front to the right, "
               "lunging low."),
    "q_brace": ("stance@876", 20, "技能「引力矩阵」：刃翼向两边张开成一圈罩住自己，双脚站稳；巨剑剑尖朝下立在身前（模型里这段剑掉在地上，参考图里没画剑）",
                "BRACE - the blade-wings spread wide all round it like a shield, feet planted; the giant sword stood "
                "point-down in front of it, both hands on the hilt (the render leaves the sword out)."),
    "e_crouch": ("leap@260", 20, "技能2「机甲飞跃」起跳前：深蹲蓄力，巨剑拖在身侧，刃翼往上竖",
                 "CROUCH - squatting deep before a leap, the sword trailing low at its side, the blade-wings raised."),
    "e_air": ("leap@1043", 20, "跃在空中：双腿收起，刃翼张开，巨剑举在身前往下准备砸（参考图里没画剑）",
              "AIRBORNE - in the air, legs tucked up, the blade-wings spread, the sword held up in front ready to "
              "strike down (the render leaves the sword out)."),
    "e_land": ("land@294", -40, "落地：单膝压低，巨剑砸进地里",
               "LANDING - come down low on one knee, the giant sword driven into the ground in front."),
    "r_flare": ("transform@982", 20, "大招「究极变形」：挺身站直，刃翼一下子全部张开成扇形大光环，巨剑剑尖朝下立在身前（参考图里没画剑）",
                "TRANSFORM - standing tall, every blade-wing flared out into a big fan behind it, the giant sword stood "
                "point-down in front of it (the render leaves the sword out)."),
    "r_slash": ("summon@1748", 20, "超级战刃：巨剑往前横扫出去，剑身伸直到最远，身子跟着前倾",
                "SUPER BLADE - the giant sword swept out forward at full reach, the blade straight out, the body "
                "leaning into it."),
    **{f"run{k + 1}": (f"sword_walk@{t}", -10, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("break@388", 50, "被打倒：往前踉跄，身上的装甲碎片崩飞，巨剑脱手往下掉",
               "BREAKING - staggering forward, armour pieces breaking off, the giant sword slipping from its hands."),
    "d_down": ("break@1165", 50, "倒下：跪坐着垂下头，黄眼罩和黄灯熄灭（画成暗灰、不发光），巨剑倒在身边地上",
               "DOWN - slumped on its knees, the head hanging, the yellow visor and lamps gone dark (a dull grey, no "
               "glow), the giant sword lying on the ground beside it."),
}


class Poser:
    """Its mesh and joints, projected as pack_mightymech_picture's renders (mirrored: thex's view; flipped at saving)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.sword_v = np.setdiff1d(np.unique(self.m.tris), np.unique(self.m.no_sword))
        # the body's own vertices (not the blade-wings, not the sword): the ground goes under these, since the break
        # clip throws wing blades off below its feet
        wing = {self.names[n] for ns in WINGS.values() for n in ns}
        main = np.array(self.m.infl)[self.m.v["bones"].astype(np.int64)][np.arange(len(self.m.v)),
                                                                           np.argmax(self.m.v["w"], axis=1)]
        self.body_v = np.setdiff1d(np.nonzero(~np.isin(main, list(wing)))[0], self.sword_v)

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.m.joints, [pose_ref.trs(*p) for p in local])
        verts = pose_ref.skin(self.m.v, self.m.infl, self.m.bind_inv, glob)
        joints = np.array([g[:3, 3] for g in glob])
        return verts, joints

    def dropped(self, joints):
        return joints[self.names["Sword"], 1] < DROPPED

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


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def skeleton(poser, xy, z, sword, hbox, out, base=None):
    """The bones on the grid; `sword` = (hilt, tip) on the canvas, or None when the clip drops it."""
    can = Image.new("RGB", (CANVAS, CANVAS), GREY)
    d = ImageDraw.Draw(can)
    grid(d)
    if base is not None:   # the design under its own skeleton, faded
        can = Image.blend(can, base.convert("RGB"), 0.55)
        d = ImageDraw.Draw(can)
    d.rectangle(hbox, outline=(110, 110, 110), width=3)
    spine3 = tuple(xy[poser.names["Spine3"]])
    lines = [(c, [tuple(xy[poser.names[n]]) for n in CHAINS[c]], np.mean([z[poser.names[n]] for n in CHAINS[c]]))
             for c in CHAINS]
    lines += [(c, [spine3, tuple(xy[poser.names[n]])], z[poser.names[n]]) for c, ns in WINGS.items() for n in ns]
    if sword is not None:
        lines.append(("sword", [tuple(sword[0]), tuple(sword[1])], sword[2]))
    for c, pts, _ in sorted(lines, key=lambda t: -t[2]):   # far ones first
        d.line(pts, fill=COL[c], width=4 if c.endswith("wing") else 7, joint="curve")
        for p in pts[:-1]:
            d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=COL[c])
    can.transpose(Image.FLIP_LEFT_RIGHT).save(lp(out))


def near_parts(z, poser):
    """Which leg and arm are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part in ("leg", "arm"):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part]])
        out.append(("L" if zl > zr else "R") + "_" + part)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\mightymech_packs\mightymech_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size
    mirror = design.transpose(Image.FLIP_LEFT_RIGHT)   # built in thex's (mirrored) view, flipped back at saving
    W = design.width
    hb = (W - HEAD_BOX[2], HEAD_BOX[1], W - HEAD_BOX[0], HEAD_BOX[3])

    # one scale for every pose: the design pose's whole height = the design's rows
    dclip, dyaw = DESIGN
    iv, ij = poser.pose(dclip)
    (pxy, _) = Poser.project(iv, dyaw, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Root"]
    # the design on the canvas: its soles on SOLE_Y, centred; every pose's root on the design's root column
    dx = (CANVAS - W * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    ix = Poser.project(iv, dyaw, scale, 0.0, 0.0)[0][:, 0]
    jx = Poser.project(ij, dyaw, scale, 0.0, 0.0)[0][pel, 0]
    x0, _, x1, _ = mirror.getbbox()
    col = x0 + (jx - ix.min()) / (ix.max() - ix.min()) * (x1 - x0)
    print("root column", round(col, 1))
    root_x = dx + round(col * PX)
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(mirror.resize((W * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.transpose(Image.FLIP_LEFT_RIGHT).convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (dclip, dyaw, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        dropped = poser.dropped(joints)
        shown = np.setdiff1d(np.arange(len(verts)), poser.sword_v) if dropped else np.arange(len(verts))
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[poser.body_v, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = root_x - jxy[pel, 0]
        # a pose that would leave the canvas moved back inside, MARGIN from the edge
        lo, hi = np.percentile(xy[shown, 0], 0.5) + shift, np.percentile(xy[shown, 0], 99.5) + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        sword = None
        if not dropped:   # the hilt (the Sword bone) to the sword vertex farthest from it
            hilt = jxy[poser.names["Sword"]]
            sv = xy[poser.sword_v]
            tip = sv[np.argmax(((sv - hilt) ** 2).sum(1))]
            sword = (hilt, tip, jz[poser.names["Sword"]])
        # the grey box = the design's own head (HEAD_BOX on the canvas) carried by the Head joint from the design pose
        hj = jxy[poser.names["Head"]]
        if name == "idle":
            hj0 = hj.copy()
        bx0, by0 = dx + hb[0] * PX, dy + hb[1] * PX
        bx1, by1 = dx + hb[2] * PX, dy + hb[3] * PX
        hbox = (bx0 + hj[0] - hj0[0], by0 + hj[1] - hj0[1], bx1 + hj[0] - hj0[0], by1 + hj[1] - hj0[1])
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, jxy, jz, sword, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("design near", near_parts(jz, poser))
            continue
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        tris = poser.m.no_sword if dropped else poser.m.tris
        im = pose_ref.render_hq(verts.copy(), tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS),
                                scale, ground, shift=x0 / CANVAS - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.transpose(Image.FLIP_LEFT_RIGHT).convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "yaw", yaw, "near", near_parts(jz, poser), "(sword dropped: left out)" if dropped else "")
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
