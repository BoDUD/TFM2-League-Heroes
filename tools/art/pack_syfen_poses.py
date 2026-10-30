#!/usr/bin/env python3
"""Sy'fen's pose pack for Codex (assets/source/syfen/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet7.wad.client, so his
skeletons are his animator's - Krug's, Nomsy's, Daeja's and Shi Oh Yu's way).

    python tools/art/pack_syfen_poses.py [--out D:/TFM2-Workshop/syfen_packs/syfen_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_syfen_picture.CLIPS), the head grown by HEAD_SCALE (step 0's B drew
it bigger than the model's). All are seen from the design's angle (side-on facing right, yaw 80: step 0's B). One
scale for all: the design pose's whole height (idle@0, the frame step 0's B was drawn from: the horn tips to his feet)
= the design's 101 rows (hd/idle.png: B-1 at 40 game px, PPU 2.52) at PX px a square; the lowest point of every pose on
y SOLE_Y, his root on the design's root column (by the ratio of the design's box to the model's).
attack2 is a wing-claw swipe, attack1 the wings flung wide and a low tail lash, spell a rear-up and a low lunge with the
jaws forward, intro a rear-up with the wings back. The run is TFT's own ON ALL FOURS (the wing-arms are the front legs),
one full 0.667 s cycle in 8 frames (the hind toes pass at ~30 and ~380 ms, the hands at ~155 and ~540: measured
2026-10-30, the near hind leg R_).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), ORANGE = the l_ wing-arm, PURPLE = the R_ wing-arm (each ending
in a big dot = the talons), PINK / CYAN = the l_ / R_ wing bone (from the hand out to the membrane's tip), RED = the l_
leg, BLUE = the R_ leg, BROWN = the tail, grey box = the head. The renders are mirrored: which arm is nearer the camera
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
from design_syfen_hd import lp  # noqa: E402
from pack_syfen_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "syfen")
PX, CANVAS, SOLE_Y = 8, 1254, 1176
ROWS = 101                     # hd/idle.png's height
HEAD_SCALE = 2.0               # the design's head against the model's (the head box heights, printed)
DESIGN = "idle@0"              # the frame step 0's B was drawn from
HEAD_BOX = (98, 0, 128, 42)    # the design's head (the crimson horns, the head plate, the eye, the teeth) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 80
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (120, 70, 30), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210)}
CHAINS = {"spine": ["Root", "Spine", "chest", "neck", "Neck_b", "head"],
          "L_arm": ["l_shoulder", "l_uparm", "l_forearm", "l_hand"],
          "R_arm": ["R_shoulder", "R_UpArm", "R_ForeArm", "R_hand"],
          "L_leg": ["hip", "l_thigh", "l_knee", "l_foot", "l_toe", "l_tip"],
          "R_leg": ["hip", "R_Thigh", "R_Knee", "R_Foot", "R_Toe", "R_Tip"],
          "tail": ["hip", "Tail_a", "Tail_b", "Tail_c", "Tail_d", "Tail_e", "Tail_f", "Tail_g"],
          "L_wing": ["l_hand", "l_wing"],
          "R_wing": ["R_hand", "R_Wing"]}
HEAD_JOINTS = ("head", "jaw")
TAIL_SCALE = 0.6             # the run and the lying pose: the tail shortened (B drew it shorter; the whole run fits the canvas)
LONG_TAIL = ("death@2700",)
ARM = {}
# one full cycle (0.667 s): the hind toes pass at ~30 and ~380 ms (both kept), the hands at ~155 and ~540
RUN_MS = [0, 40, 120, 200, 290, 380, 470, 560]

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a1_wind": ("attack2@200", 80, "翼爪起手：身子扭过去，近处的翅膀手臂收到身后蓄力",
                "WING CLAW WIND UP - the body twisted back, the near wing-arm drawn back behind him, gathering."),
    "a1_hit": ("attack2@400", 80, "翼爪：翅膀手臂往前横着抓出去，伸到最远，利爪张开（爪痕之后单独画）",
               "WING CLAW STRIKE - the wing-arm raking forward and across, reaching as far as it goes, talons open (the claw "
               "trail is drawn separately later)."),
    "a2_wind": ("attack1@200", 80, "甩尾起手：两条翅膀手臂向两边甩开，身子转过去",
                "TAIL LASH WIND UP - both wing-arms flung out to the sides, the body turning away."),
    "a2_hit": ("attack1@600", 80, "甩尾：身子压低，长尾巴贴地横扫过来，刀刃尾尖甩在前面",
               "TAIL LASH - crouched low, the long tail sweeping across along the ground, the blade tip whipping round in "
               "front."),
    "q_rear": ("spell@200", 80, "噬咬起手：身子挺起往后仰，头高高抬起，张开嘴",
               "BITE WIND UP - rearing up and back, the head raised high, the jaws opening."),
    "q_bite": ("spell@300", 80, "噬咬：整个身子往前低低扑出，头伸到最前面，大嘴咬下去（咬痕之后单独画）",
               "BITE - the whole body lunging low and forward, the head thrust out in front, the jaws snapping shut (the "
               "bite mark is drawn separately later)."),
    "e_spread": ("attack1@400", 80, "翼刃横扫起手：两条翅膀手臂完全张开，翼膜展得最大",
                 "WING SWEEP WIND UP - both wing-arms spread wide, the membranes opened as far as they go."),
    "e_sweep": ("attack2@500", 80, "翼刃横扫：翅膀手臂往前合拢扫过身前（扫出的弧光之后单独画）",
                "WING SWEEP - the wing-arms swept forward and closing in front of him (the sweep's arc is drawn separately "
                "later)."),
    "r_roar": ("intro@746", 80, "暴走起手：挺身后仰咆哮，翅膀手臂往后张开",
               "RAMPAGE ROAR - rearing up and roaring, the wing-arms thrown back."),
    "r_charge": ("spell@400", 80, "暴走冲锋：身子压到最低往前冲，头往前顶，翅膀手臂贴着身体往前（冲锋的残影之后单独画）",
                 "RAMPAGE CHARGE - the body as low as it goes, driving forward, the head pushed out in front, the wing-arms "
                 "close along the body (the charge trail is drawn separately later)."),
    "r_bite": ("spell@500", 80, "暴走猛咬：冲到后低头狠狠咬住，翅膀手臂撑在两边",
               "RAMPAGE BITE - arrived, the head ducked down biting hard, the wing-arms braced at his sides."),
    "d_fall": ("death@300", 80, "被打倒：往后一仰，翅膀手臂和尾巴乱扬",
               "KNOCKED BACK - thrown back, the wing-arms and the tail flung up."),
    "d_down": ("death@2700", 80, "倒地：整个趴在地上，翅膀摊开，尾巴拖在后面（金铲铲原样）",
               "DOWN - lying flat on the ground, the wings spread limp, the tail trailing behind (as in TFT)."),
}
for k, ms in enumerate(RUN_MS):
    POSES[f"run{k + 1}"] = (f"run@{ms}", 80,
                            f"移动 第 {k + 1}/8 帧（金铲铲的四肢着地奔跑，一整个循环，两条后腿各往前迈一次，翅膀手臂当前腿）",
                            f"RUN frame {k + 1} of 8 (TFT's run ON ALL FOURS, one whole cycle: each hind leg swings forward "
                            f"once, the wing-arms working as front legs).")


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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\syfen_packs\syfen_pose_pack")
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
