#!/usr/bin/env python3
"""Meepsie's pose pack for Codex (assets/source/meepsie/POSE_PROMPTS.md): the whole-body poses of its actions, each on
a skeleton projected from its OWN clips (its model and clips are in the Riot client's TFTSet17.wad.client, so its
skeletons are its animator's - pack_sentinel_poses' way).

    python tools/art/pack_meepsie_poses.py [--out D:/TFM2-Workshop/meepsie_packs/meepsie_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_meepsie_picture.CLIPS), the meep pilot grown by HEAD_SCALE (the
design's pilot and cockpit are bigger than the model's; Codex puts the design's own pilot on every pose anyway). All
are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the design pose's whole height (idle@0,
the frame step 0's A was drawn from: the mushroom tops to its soles) = the design's 115 rows (hd/idle.png: A-1 at 40
game px, PPU 2.875, 1:1) at PX px a square; the lowest point of every pose on y SOLE_Y, its root on the design's root
column (PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's cockpit and pilot 8x: every pose wears it); per
pose <k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png
(its bones on the grid).
Skeleton colours: green = the spine (root to the top of the body), YELLOW = the meep pilot (cockpit to its head), PINK =
the L_ arm (shoulder to fist), CYAN = the R_ arm, RED = the L_ leg, BLUE = the R_ leg (the renders are mirrored: which
side is nearer the camera is written per pose), grey box = the cockpit with the pilot.
Its run (TFT's lumbering walk, 1.3 s a full cycle of both legs) is sampled at RUN_MS over the whole cycle (measured with
C:/t/mp_work/gait.py on the model's own forward axis; tft-run-full-cycle): the R foot lifted 0-350 ms (highest ~240,
down ~400, the widest split ~330), the passing at ~570 (gap 0), the L foot lifted 520-1000 (highest ~800, down ~1040,
the widest split ~1000), the second passing at ~1250.
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
from design_meepsie_hd import lp  # noqa: E402
from pack_meepsie_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "meepsie")
PX, CANVAS, SOLE_Y = 6, 1254, 1176
ROWS = 115                    # hd/idle.png's height
HEAD_SCALE = 1.25            # the model's meep pilot grown toward the design's (Codex wears the design's anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (62, 18, 104, 58)   # the design's cockpit with the pilot (antenna, eyes, smile, hands) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "meep": (235, 200, 0), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Spine3", "Head"],
          "meep": ["Spine3", "Meep_Root", "Meep_Chest", "Meep_Head", "Meep_Hair"],
          "L_arm": ["Spine3", "L_Clavicle", "L_Shoulder", "L_ElbowUpper", "L_ElbowLower", "L_Wrist", "L_Hand",
                    "L_Middle1"],
          "R_arm": ["Spine3", "R_Clavicle", "R_Shoulder", "R_ElbowUpper", "R_ElbowLower", "R_Wrist", "R_Hand",
                    "R_Middle1"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Meep_",)
RUN_MS = (80, 240, 400, 570, 760, 960, 1080, 1250)   # one full 1.3 s cycle with both passings (570, 1250)
RUN_ZH = ("走 1：近处的脚抬起往前迈，远处的脚踩地；两只巨拳跟着一前一后摆",
          "走 2：近处的脚抬到最高、往前送",
          "走 3：近处的脚落在前面，两脚分到最开，重心压上去",
          "走 4：两腿交错（近处的脚在后面踩地，远处的脚抬起从旁边经过）",
          "走 5：远处的脚抬到最高、往前送",
          "走 6：远处的脚伸到最前",
          "走 7：远处的脚落地，两脚分到最开",
          "走 8：两腿交错（远处的脚在后面踩地，近处的脚抬起经过）；8 接回 1，循环")
RUN_EN = ("WALK 1 - the near foot lifting to step forward, the far foot planted; the two huge fists swinging one forward, "
          "one back.",
          "WALK 2 - the near foot at its highest, swinging forward.",
          "WALK 3 - the near foot coming down in front, the feet at their widest apart, the weight onto it.",
          "WALK 4 - the legs passing (the near foot planted behind, the far foot lifted, swinging past it).",
          "WALK 5 - the far foot at its highest, swinging forward.",
          "WALK 6 - the far foot reaching furthest forward.",
          "WALK 7 - the far foot coming down, the feet at their widest apart.",
          "WALK 8 - the legs passing (the far foot planted behind, the near foot lifted, swinging past it); 8 runs on "
          "into 1: the loop.")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_raise": ("attack@450", 35, "普攻「月岩重拳」起手：一只巨拳高高举过头顶，身子往后一挺，另一只拳头垂在身侧",
                "RAISE - one huge fist raised high over the top of its body, the body leaning back, the other fist "
                "hanging at its side."),
    "a_punch": ("attack@800", 35, "砸下：举起的拳头往前下方狠狠砸下去，身子往前弓，叶子蘑菇顶朝前",
                "PUNCH DOWN - the raised fist smashed forward and down, the body bent forward, the leaf and mushroom "
                "cap tipped toward the front."),
    "q_raise": ("attack2@300", 35, "技能1「月尘震地」起手：一只巨拳抡到头顶上方，蓄力",
                "WIND UP - one huge fist swung up above the top of its body, gathering strength."),
    "q_smash": ("attack2@600", 35, "震地：拳头整个砸进身前地面，身子压到很低往前扑（震波之后单独画，这里不画）",
                "QUAKE - the fist smashed whole into the ground in front, the body thrown low and forward (the "
                "shockwave is drawn later, NOT here)."),
    "e_ready": ("idle2@800", 35, "技能2「治疗木灵」起手：身子微微弓下，驾驶舱里的小木灵挺起身子",
                "READY - the body hunched a little, the meep pilot sitting up tall in its cockpit."),
    "e_call": ("fist@130", 35, "放木灵：一只手高高举起张开手掌，像在放飞东西；小木灵双手举高欢呼（飞出的小木灵之后单独画）",
               "RELEASE - one arm raised high with the hand open, as if letting something fly; the meep pilot cheering "
               "with both little arms up (the flying meeps are drawn later, NOT here)."),
    "r_jump": ("spell@300", 35, "大招「宇宙大爆炸」起跳：一蹬地跳到空中，两臂往两边张开，两腿收在身下",
               "LEAP - sprung off the ground into the air, both arms flung out to the sides, both legs tucked under it."),
    "r_air": ("spell@700", 35, "空中最高点：两只巨拳一起高举过头顶，身子挺直",
              "TOP OF THE LEAP - both huge fists raised together high over the top of its body, the body stretched "
              "straight."),
    "r_land": ("spell@1100", 35, "砸落：落回地面，两只巨拳一起砸进身前地面，膝盖弯下",
               "SLAM DOWN - landing back on the ground, both huge fists smashed into the ground in front together, the "
               "knees bent."),
    "r_slam": ("spell@1300", 35, "落地压低：两只拳头撑在地上，身子压到最低（冲击波之后单独画，这里不画）",
               "IMPACT - both fists planted on the ground, the body pressed down as low as it goes (the blast is drawn "
               "later, NOT here)."),
    **{f"run{k + 1}": (f"run@{t}", 35, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("death@900", 35, "被打倒：身子往前一栽，膝盖跪下，两只拳头垂到地上",
               "FALLING - tipping forward, the knees buckling, both fists sagging to the ground."),
    "d_down": ("death@1166", 35, "倒地：跪着往前折成一团石头不动，两只拳头摊在地上，叶子蘑菇顶朝前；小木灵缩进驾驶舱里看不见",
               "DOWN - folded forward on its knees into a still heap of stones, both fists slumped on the ground, the leaf "
               "and mushroom cap tipped forward; the meep pilot ducked down out of sight in its cockpit."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_meepsie_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, 1.0, scale={"Meep_Root": HEAD_SCALE})
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
    """The vertices mostly weighted to the meep pilot."""
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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\meepsie_packs\meepsie_pose_pack")
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
