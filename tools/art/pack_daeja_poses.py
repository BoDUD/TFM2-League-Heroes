#!/usr/bin/env python3
"""Daeja's pose pack for Codex (assets/source/daeja/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet7.wad.client, so his
skeletons are his animator's - Krug's and Nomsy's way).

    python tools/art/pack_daeja_poses.py [--out D:/TFM2-Workshop/daeja_packs/daeja_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_daeja_picture.CLIPS), the head grown by HEAD_SCALE (step 0's A drew it
bigger than the model's). All are seen from the design's angle (3/4 facing right, yaw 35: step 0's A). One scale for
all: the design pose's whole height (idle@0, the frame step 0's A was drawn from: the wing tips to his feet) = the
design's 69 rows (hd/idle.png: A-1 at 40 game px, PPU 1.72, 1:1) at PX px a square; the lowest point of every pose on
y SOLE_Y, his root on the design's root column (by the ratio of the design's box to the model's).
His clips have no attack: the attack poses are the idle with the near arm turned at the shoulder and the elbow (ARM),
a wind-up and a punch. The run is TFT's own, one full 0.97 s cycle (both legs pass: the toes measured, 2026-10-30) in
8 frames 121 ms apart.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), ORANGE = the L_ arm, PURPLE = the R_ arm (each ending in a big
dot = the fist), RED = the L_ leg, BLUE = the R_ leg, BROWN = the tail, PINK = the L_ wing (its seven ribs' roots from
the back out to the tip), CYAN = the R_ wing, grey box = the head. The renders are mirrored: which arm is nearer the
camera is printed per pose.
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
from design_daeja_hd import lp  # noqa: E402
from pack_daeja_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "daeja")
PX, CANVAS, SOLE_Y = 10, 1254, 1176
ROWS = 69                      # hd/idle.png's height
HEAD_SCALE = 2.0               # the design's head against the model's (the head box heights, printed)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (24, 16, 46, 36)    # the design's head (the crests, the mask, the eyes, the mane) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (120, 70, 30), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210)}
CHAINS = {"spine": ["Root", "Pelvis", "Spine1", "Spine2", "Spine3", "Neck", "Head"],
          "L_arm": ["L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand"],
          "R_arm": ["R_Clavicle", "R_Shoulder", "R_Elbow", "R_Hand"],
          "L_leg": ["Pelvis", "L_Hip", "L_KneeUpper", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_KneeUpper", "R_Foot", "R_Toe"],
          "tail": ["Tail_1_SKN", "Tail_2_SKN", "Tail_3_SKN", "Tail_4_SKN"],
          "L_wing": ["Spine3"] + [f"L_Wing{k}_B" for k in (1, 2, 3, 4, 5, 6, 8)],
          "R_wing": ["Spine3"] + [f"R_Wing{k}_SKN" for k in (1, 2, 3, 4, 5, 6, 8)]}
HEAD_JOINTS = ("Head",)
TAIL_SCALE = 1.0
LONG_TAIL = ()
# the attack (his clips have none): the idle with the near (L_: mirrored, image right) arm turned, (axis in the parent's
# frame, degrees) per joint, picked from renders (2026-10-30): the fist drawn back to the chest, then thrust out level
ARM = {
    "a_wind": {"L_Shoulder": ((1, 0, 0), -45), "L_Elbow": ((0, 1, 0), 60)},
    "a_punch": {"L_Shoulder": ((0, 0, 1), -80)},
}
RUN_MS = [round(966 * k / 8) for k in range(8)]

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("idle@0", 35, "风弹起手：橙线那只（近处的）拳头弯起来收到胸前蓄力（照骨架）",
               "WIND UP - the near fist on the ORANGE line bent and drawn back to his chest, gathering (as in the skeleton)."),
    "a_punch": ("idle@0", 35, "风弹：橙线那只（近处的）拳头平平地往前猛推出去（风弹之后单独画），紫线那只留在身边",
                "PUNCH - the near fist on the ORANGE line thrust straight out forward at chest height (the wind bolt is "
                "drawn separately later), the arm on the PURPLE line at his side."),
    "q_raise": ("spell@0", 35, "罡风轰击起手：两片翅膀张开往后上方高高扬起，身子前倾蓄力",
                "WINGS BACK - both wings opened and raised high behind him, the body leaning forward, gathering."),
    "q_sweep": ("spell@250", 35, "罡风轰击：两片翅膀猛地往前扫到身前（冲击波之后单独画）",
                "SWEEP - both wings swept hard forward in front of him (the shock wave is drawn separately later)."),
    "e_beat": ("celebration@0", 35, "振翼退风：两片翅膀向两边完全展开猛扇一下",
               "WINGBEAT - both wings spread fully to the sides in one hard beat."),
    "e_hop": ("spell@583", 35, "振翼退风（跳起）：借风离地，腿收起，翅膀张着",
              "HOP - lifted off the ground by the wind, the legs drawn up, the wings spread."),
    "r_up": ("intro@361", 35, "苍穹罡风（起飞）：蹲低蓄力，翅膀向两边张开，准备飞起",
             "TAKE OFF - crouched low, the wings spread to the sides, about to fly up."),
    "r_fly1": ("celebration@0", 35, "苍穹罡风（飞行·平展）：翅膀平平展开（之后整体抬离地面）",
               "FLY, WINGS LEVEL - the wings spread level (lifted off the ground later)."),
    "r_fly2": ("spell@0", 35, "苍穹罡风（飞行·上扬）：翅膀扬到最高（之后整体抬离地面）",
               "FLY, WINGS UP - the wings raised to the top of the beat (lifted off the ground later)."),
    "r_blast": ("spell@250", 35, "苍穹罡风（轰出）：在空中把翅膀往前扫（之后整体抬离地面）",
                "BLAST - in the air, the wings swept forward (lifted off the ground later)."),
    "r_land": ("intro@541", 35, "苍穹罡风（落地）：落地蹲下，翅膀半张",
               "LAND - landed, crouched, the wings half open."),
    "d_fall": ("death@416", 35, "被打倒：往后一仰，身子立起来，翅膀乱扬",
               "KNOCKED BACK - thrown back, the body upright, the wings flung up."),
    "d_down": ("death@4166", 35, "倒地：跪倒在地，垂下头（金铲铲原样）",
               "DOWN - fallen to his knees, the head hanging (as in TFT)."),
}
for k, ms in enumerate(RUN_MS):
    POSES[f"run{k + 1}"] = (f"run@{ms}", 35, f"移动 第 {k + 1}/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次）",
                            f"RUN frame {k + 1} of 8 (TFT's run, one whole cycle: each leg swings forward once).")


def turned(joints, local, turns):
    """`local` with a rotation about an axis of the parent's frame put before each named joint's own."""
    names = [j["name"] for j in joints]
    out = list(local)
    for name, (axis, deg) in turns.items():
        i = names.index(name)
        t, r, s_ = out[i]
        ax = np.asarray(axis, float) / np.linalg.norm(axis)
        h = np.radians(deg) / 2
        x1, y1, z1, w1 = np.r_[ax * np.sin(h), np.cos(h)]   # x y z w
        x2, y2, z2, w2 = r
        out[i] = (t, np.array([w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                               w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2, w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2]), s_)
    return out


class Poser:
    """His mesh (head grown) and joints, projected as pack_kobuko_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip, turns=None):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        long_tail = clip in LONG_TAIL or name == "run"
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE, scale={"Tail_a": TAIL_SCALE} if long_tail else None)
        if turns:
            local = turned(self.m.joints, local, turns)
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
    """The vertices mostly weighted to the head and what hangs off it (ears, topknot, beard, eyes, jaw)."""
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
        if c.endswith("arm"):
            p = pts[-1]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "L" if zl > zr else "R"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\daeja_packs\daeja_pose_pack")
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
    hy = pxy[hv, 1]
    print("head box / height: model (grown)", round(np.ptp(hy) / np.ptp(pxy[:, 1]), 3), "design",
          round((HEAD_BOX[3] - HEAD_BOX[1]) / ROWS, 3))
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
        verts, joints = poser.pose(clip, ARM.get(name))
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge
        lo, hi = xy[:, 0].min() + shift, xy[:, 0].max() + shift
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
            print("idle near arm", near_arm(jz, poser))
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
        print(stem, clip, "yaw", yaw, "near arm", near_arm(jz, poser))
    if os.path.exists(lp(os.path.join(SRC, "POSE_PROMPTS.md"))):
        shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
