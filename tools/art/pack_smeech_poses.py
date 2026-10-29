#!/usr/bin/env python3
"""Smeech's pose pack for Codex (assets/source/smeech/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet13.wad.client, so his
skeletons are his animator's - Scar's way).

    python tools/art/pack_smeech_poses.py [--out C:/t/sm_work/smeech_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_smeech_picture.CLIPS, named by what they show), the head grown to the
design's (pose_ref.chibi, HEAD_SCALE: the design's head with the hat and the ears is over half his crouched height,
TFT's model's much less). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the
design pose's whole height (crouch@1160, the ambush crouch step 0's B was drawn from: hat to soles) = the design's 87
rows (hd/idle.png: B-1 at 36 game px, PPU 2.4) at PX px a square; the lowest point of every pose on y SOLE_Y, his pelvis
on the design pose's pelvis column.
His claws are his hands: each arm line runs on past the hand to the tip of the middle claw (R_/L_Middle4), so the
claw's length shows on the skeleton.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = his R_ arm, CYAN = his L_ arm (both
the same mechanical arm; the line's last stretch = the claw), RED = left leg, BLUE = right leg, grey box = the head.
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
from design_smeech_hd import lp  # noqa: E402
from pack_smeech_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "smeech")
PX, CANVAS, SOLE_Y = 9, 1254, 1176   # 9 px: the 128-square-wide crouch fits the canvas
ROWS = 87                     # hd/idle.png's height
HEAD_SCALE = 2.2
DESIGN = "crouch@1160"         # the ambush crouch step 0's B was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (50, 0, 111, 51)     # the design's head with the hat and the ears (hd/idle.png)
PELVIS_COL = 55                 # the design's pelvis column: over the shorts, between the legs
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle4"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle4"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Hat", "Ear", "Eye", "Brow", "Jaw", "Nose", "Mouth", "Lip", "Tongue")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
WALK = [
    (0, "走路 1：长腿大步走（金铲铲原样），弓着背，两只爪子在身前甩",
     "WALK 1 - a long-legged loping stride (as in the game), hunched, the claws swinging in front of him."),
    (125, "走路 2", "WALK 2"), (250, "走路 3", "WALK 3"), (375, "走路 4", "WALK 4"), (500, "走路 5", "WALK 5"),
    (625, "走路 6", "WALK 6"), (750, "走路 7", "WALK 7"), (875, "走路 8", "WALK 8"),
]
POSES = {
    "a_rake": ("slash@0", 35, "爪击 1：身体猛地往前扑低，两只爪子往右前下方抓出去，爪指张开",
               "RAKE - lunging forward and low, both claws raked out to the lower front-right, the claw fingers "
               "spread."),
    "a_back": ("slash@120", 35, "爪击收回：蹲回去，爪子收到身前地面附近",
               "RECOVER - crouched back down, the claws pulled in near the ground in front of him."),
    "a_wind2": ("stabs@250", 35, "爪击 2 起手：一只爪子往后拉到身后，另一只护在身前",
                "WIND-UP - one claw drawn far back behind him, the other held in front."),
    "a_thrust": ("stabs@700", 35, "爪击 2 / 连斩：蹲着把一只爪子笔直往前（画面右）刺出去，爪指朝前张开",
                 "THRUST - crouched, one claw driven straight forward (image right), the claw fingers spread "
                 "forward."),
    "q_crouch": ("leap@90", 35, "废铁黑客起跳前：趴得很低、像要扑出去，爪子撑在身前地上",
                 "GATHER - crouched very low like a cat about to pounce, the claws planted on the ground in front."),
    "q_air": ("leap@450", 35, "腾空：跳在半空，两只爪子高高张开举过头，腿缩起来",
              "IN THE AIR - leaping, both claws spread high above his head, the legs tucked up."),
    "q_dive": ("pounce@280", 35, "扑下：在半空往前下方扑，两只爪子伸在最前面往下抓",
               "DIVE - in mid-air pouncing down and forward, both claws reaching out in front, raking down."),
    "q_land": ("pounce@490", 35, "落地：弓步落地，身子压低往前，一只爪子刺在前面",
               "LAND - landing in a low lunge, leaning forward, one claw stabbed out in front."),
    "e_wind": ("arms@500", 35, "拆解起手：两只爪子大大张开高举在两边，爪指朝上",
               "RIP WIND-UP - both claws thrown wide and high to the sides, the claw fingers up."),
    "e_rip": ("spread@900", 35, "拆解：蹲低，两只爪子往两边狠狠撕开（一只往前一只往后，几乎平伸）",
              "RIP - crouched low, both claws torn apart to the sides (one forward, one back, almost level)."),
    **{f"run{i + 1}": (f"run@{ms}", 35, zh, en) for i, (ms, zh, en) in enumerate(WALK)},
    "d_fall": ("death@900", 35, "被击倒：身体一僵往后倒，礼帽从头上掉了，落在他身后（画面左）的地上，照参考图",
               "KNOCKED DOWN - stiff, falling over backwards, the TOP HAT knocked off his head and lying on the "
               "ground behind him (image left), as in the reference."),
    "d_down": ("death@1160", 35, "倒地：仰面平躺在地上，礼帽掉在头旁边的地上",
               "DOWN - lying flat on his back on the ground, the top hat fallen on the ground beside his head."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_smeech_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE)
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


def vertices_of(poser, keys):
    """The vertices mostly weighted to the joints whose names hold one of `keys`."""
    m = poser.m
    joint_of = np.array(m.infl)[m.v["bones"].astype(np.int64)]
    main = joint_of[np.arange(len(m.v)), np.argmax(m.v["w"], axis=1)]
    sel = {i for i, j in enumerate(m.joints) if any(k in j["name"] for k in keys)}
    return np.isin(main, list(sel))


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def skeleton(poser, joints, xy, z, hbox, out, base=None):
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
        if c.endswith("arm"):   # the hand (the claw's root), and a ring at the claw's tip
            p, q = pts[2], pts[3]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
            d.ellipse([q[0] - 9, q[1] - 9, q[0] + 9, q[1] + 9], outline=COL[c], width=4)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "CYAN (the L_ arm)" if zl > zr else "ORANGE (the R_ arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sm_work\smeech_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = vertices_of(poser, HEAD_JOINTS)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # one scale for every pose: the design pose's whole height = the design's rows
    iv, ij = poser.pose(DESIGN)
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the design pose's pelvis lands on the same column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    pelvis_x = dx + PELVIS_COL * PX + PX // 2
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground, claws far out) moved back inside, MARGIN from the edge
        lo, hi = xy[:, 0].min() + shift, xy[:, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        if name == "idle":
            print("design pose head box", round((hbox[2] - hbox[0]) / PX, 1), "x", round((hbox[3] - hbox[1]) / PX, 1),
                  "squares (the design's", HEAD_BOX[2] - HEAD_BOX[0], "x", HEAD_BOX[3] - HEAD_BOX[1], ")")
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, joints, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"),
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift
        im = pose_ref.render_hq(pv, poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS), scale,
                                ground, shift=x0 / CANVAS - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        notes[name] = near_arm(jz, poser)
        print(stem, clip, "yaw", yaw, "near arm", notes[name])
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
