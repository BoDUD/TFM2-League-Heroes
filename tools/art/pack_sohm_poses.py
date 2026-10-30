#!/usr/bin/env python3
"""Sohm's pose pack for Codex (assets/source/sohm/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet7.wad.client, so her
skeletons are her animator's - Krug's, Nomsy's, Daeja's, Shi Oh Yu's and Sy'fen's way).

    python tools/art/pack_sohm_poses.py [--out D:/TFM2-Workshop/sohm_packs/sohm_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_sohm_picture.CLIPS), the head grown by HEAD_SCALE (step 0's B drew
it bigger than the model's). All are seen from the design's angle (side-on facing right, yaw 80: step 0's B). One
scale for all: the design pose's whole height (idle@0, the frame step 0's B was drawn from: the antler tips to the
bottom of her coil) = the design's 72 rows (hd/idle.png: B-1 at 40 game px, PPU 1.8) at PX px a square; the lowest
point of every pose on y SOLE_Y, her neck root (ANCHOR) on the design's column (by the ratio of the design's box to
the model's).
attack rears up tall and flicks forward, the unnamed coil clip rears up and thrusts forward in an S, spell dives,
curls, rises straight up and swirls back. Her run is TFT's swim (run1): coiled, laid out flat swimming, coiled again
over 2.67 s with no repeating stroke, so the move is RUN_MS's four frames of the flat swim (the tail sweeping from
raised to level) played forward and back (rig_sohm.py).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the body (the hips up the neck to the head), ORANGE = the L_ little arm, PURPLE = the R_
little arm (each ending in a big dot = the claws), RED = the L_ hind leg, BLUE = the R_ hind leg, BROWN = the tail,
PINK / CYAN = the L_ / R_ kelp tail fin, grey box = the head. The renders are mirrored: which arm is nearer the camera
is printed per pose.
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
from design_sohm_hd import lp  # noqa: E402
from pack_sohm_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sohm")
PX, CANVAS, SOLE_Y = 8, 1254, 1176
ROWS = 72                      # hd/idle.png's height
HEAD_SCALE = 1.8               # the design's head against the model's (the head box heights, printed)
DESIGN = "idle@0"              # the frame step 0's B was drawn from
HEAD_BOX = (26, 0, 58, 46)     # the design's head (the coral antlers, the crown and gem, the ear, the eye, the snout)
PELVIS_COL = None              # None: by the box ratio (printed)
ANCHOR = "Neck1"               # the joint put on the design's column (her Root stays on the ground under her)
YAW = 80
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (120, 70, 30), "L_fin": (240, 80, 170), "R_fin": (0, 190, 210)}
CHAINS = {"spine": ["Spine6", "Spine5", "Spine4", "Spine3", "Spine2", "Spine1", "Neck1", "Neck2", "Neck3", "Neck4",
                    "Neck5", "Head"],
          "L_arm": ["L_Clavicle", "L_Shoulder", "L_ElbowUpper", "L_ElbowLower", "L_Wrist"],
          "R_arm": ["R_Clavicle", "R_Shoulder", "R_ElbowUpper", "R_ElbowLower", "R_Wrist"],
          "L_leg": ["L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_Toe"],
          "R_leg": ["R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_Toe"],
          "tail": ["Tail1", "Tail2", "Tail3", "Tail4", "Tail5", "Tail6", "Tail7", "Tail8", "Tail9", "Tail10", "Tail11",
                   "Tail12", "Tail13", "Tail14"],
          "L_fin": ["Tail5", "L_TailFin1_1", "L_TailFin1_2", "L_TailFin1_3"],
          "R_fin": ["Tail5", "R_TailFin1_1", "R_TailFin1_2", "R_TailFin1_3"]}
HEAD_JOINTS = ("Head", "Jaw", "Ear")
TAIL_SCALE = 0.7             # the swim: the tail shortened (B drew it coiled tight; laid out flat it would be twice her)
LONG_TAIL = ()
ARM = {}
# the flat swim of TFT's run1 (no repeating stroke): four frames, played forward and back
RUN_MS = [900, 1100, 1300, 1500]

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_rear": ("attack@266", 80, "水泡弹起手：身子往上一挺拉得很长，头高高抬起",
               "WATER BOLT WIND UP - rising tall, the long body stretched up, the head raised high."),
    "a_spit": ("attack@400", 80, "水泡弹：头往前一甩吐出水弹，身子在下面弯成一个钩（水弹之后单独画）",
               "WATER BOLT - the head flicked forward spitting, the body curled into a hook under her (the bolt is "
               "drawn separately later)."),
    "q_rise": ("coil@150", 80, "潮涌起手：挺身往上，两只小爪收在胸前蓄力",
               "TIDEBLOSSOM WIND UP - rearing up tall, the two little claws drawn in to her chest, gathering."),
    "q_send": ("coil@750", 80, "潮涌：整个身子往前一送，弯成一个 S，头和小爪推向前方（水浪之后单独画）",
               "TIDEBLOSSOM - the whole body thrown forward in an S, the head and the little claws pushing out in front "
               "(the wave is drawn separately later)."),
    "e_gather": ("idle@800", 80, "海潮护佑起手：身子盘紧，小爪合在胸前",
                 "TIDECALLER WIND UP - the body coiled tight, the little claws together at her chest."),
    "e_push": ("attack@533", 80, "海潮护佑：头往前伸，两只小爪往前一推（水盾之后单独画）",
               "TIDECALLER - the head reaching forward, both little claws pushing out in front (the water shield is drawn "
               "separately later)."),
    "r_coil": ("spell@413", 80, "潮汐绽放起手：身子低低盘成一圈，蓄力",
               "TIDAL BLOOM WIND UP - the body curled low into a ring, gathering."),
    "r_rise": ("spell@826", 80, "潮汐绽放：整个身子笔直地往上冲起，头在最高处，尾巴在下面甩开",
               "TIDAL BLOOM - the whole body shooting straight up, the head at the very top, the tail flung out below."),
    "r_swirl": ("spell@1653", 80, "潮汐绽放收尾：在空中转一圈，尾巴绕着身子甩成一个环",
                "TIDAL BLOOM END - turning over in the air, the tail swung round her body in a ring."),
    "d_fall": ("death@200", 80, "被打倒：身子一扭往下掉，鬃毛和尾巴乱甩",
               "KNOCKED DOWN - twisted and dropping, the mane and the tail flung about."),
    "d_down": ("death@1800", 80, "倒地：盘着身子侧躺在地上（金铲铲原样）",
               "DOWN - lying on her side on the ground, the body loosely coiled (as in TFT)."),
}
for k, ms in enumerate(RUN_MS):
    POSES[f"run{k + 1}"] = (f"run@{ms}", 80,
                            f"移动 第 {k + 1}/{len(RUN_MS)} 帧（金铲铲的游动：身子平着往前游，尾巴从翘起慢慢摆平；来回播放）",
                            f"SWIM frame {k + 1} of {len(RUN_MS)} (TFT's swim: the body laid out flat swimming forward, the "
                            f"tail sweeping from raised to level; played forward and back).")


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
    """Her mesh (head grown) and joints, projected as pack_kobuko_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip, turns=None):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        long_tail = clip in LONG_TAIL or name == "run"
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE, scale={"Tail1": TAIL_SCALE} if long_tail else None)
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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\sohm_packs\sohm_pose_pack")
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
    pel = poser.names[ANCHOR]
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
