#!/usr/bin/env python3
"""Scar's pose pack for Codex (assets/source/scar/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet13.wad.client, so his
skeletons are his animator's - Violet's way).

    python tools/art/pack_scar_poses.py [--out C:/t/sc_work/scar_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_scar_picture.CLIPS, named by what they show), the head grown to the
design's (pose_ref.chibi, HEAD_SCALE: the design's head with the ears and the mohawk is over a third of his height,
TFT's model's much less). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for all: the
design pose's whole height (attack@0, the guard step 0's B was drawn from: mohawk to soles) = the design's 76 rows
(hd/idle.png: B-1 at 38 game px, PPU 2.0) at PX px a square; the lowest point of every pose on y SOLE_Y, his pelvis on
the design pose's pelvis column.
His spear: TFT's clips mostly carry it point BACK (his attack is a backhand sweep), the design point FORWARD. So the
skeleton draws the spear itself - its shaft along the model's spear (the main axis of its vertices) - and puts the
POINT at the end each pose names (POSES' tip: "model" = where the model has it, "flip" = the other end).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = his R_ arm (the BANDAGED one), CYAN =
his L_ arm (bare purple, the orange bracer), RED = left leg, BLUE = right leg, PURPLE = the spear's shaft with a GOLD
triangle at its POINT, grey box = the head.
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
from design_scar_hd import lp  # noqa: E402
from pack_scar_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scar")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 76                     # hd/idle.png's height
HEAD_SCALE = 1.7
DESIGN = "attack@0"            # the guard step 0's B was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (30, 0, 57, 29)      # the design's head with the ears and the mohawk (hd/idle.png)
PELVIS_COL = 36                 # the design's pelvis column: between its legs (cols 20-34 and 39-54 at row 56)
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "spear": (120, 40, 170), "point": (230, 175, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle1"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle1"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Ear", "Eyelid")
SPEAR_JOINTS = ("Weapon",)

# name -> (clip@ms, yaw, where the spear's point goes, what it is for (Chinese), the pose line (English))
WALK = [
    (0, "走路 1：吊儿郎当地大步走（金铲铲原样），长矛竖着拿在身侧、矛尖朝下",
     "WALK 1 - a loose, swaggering stride (as in the game), the spear carried upright at his side, the point down."),
    (133, "走路 2", "WALK 2"), (266, "走路 3", "WALK 3"), (400, "走路 4", "WALK 4"), (533, "走路 5", "WALK 5"),
    (666, "走路 6", "WALK 6"), (800, "走路 7", "WALK 7"), (933, "走路 8", "WALK 8"),
]
POSES = {
    "a_wind": ("attack@0", 35, "flip", "普攻起手：定稿的架势往后收一点，长矛收在腰边，矛尖朝前（画面右）",
               "WIND-UP - the design's guard drawn back a little, the spear pulled in at his waist, the POINT forward "
               "(image right)."),
    "a_thrust": ("attack@385", 35, "flip", "长矛刺击：身体前压，两只手把长矛顺着矛杆笔直往前（画面右）捅出去，矛尖在最前面",
                 "THRUST - leaning forward, both hands driving the spear straight forward along its shaft (image "
                 "right), the POINT leading."),
    "a_back": ("attack@674", 35, "flip", "收矛：长矛收回身前，快回到定稿的架势",
               "RECOVER - the spear pulled back in front of him, almost the design's guard."),
    "surf": ("leap@1365", 35, "model", "野火冲刺 / 野火突袭：压低身子蹲在悬浮滑板上（脚下画一块野火帮的滑板），长矛平端、矛尖朝前",
             "HOVERBOARD RIDE - crouched low ON A HOVERBOARD under his feet (a small Firelight board, see below), "
             "the spear held level, the POINT forward."),
    "surf_hit": ("leap@1062", 35, "model", "冲刺捅矛：还站在滑板上，身体往前探，长矛往前捅出去",
                 "RIDE STRIKE - still on the hoverboard, reaching forward, the spear thrust out in front, the POINT "
                 "forward."),
    "q_wind": ("spell@133", 35, "model", "水坑狙击惊喜起手：身体往后仰，长矛竖在近处，空着的那只手往后拉准备扔炸弹",
               "BOMB WIND-UP - leaning back, the spear upright at his near side, the free hand drawn back to throw."),
    "q_throw": ("spell@400", 35, "model", "扔炸弹：那只手往右前上方甩出去（手里不画炸弹，炸弹另画），长矛斜在身前",
                "THROW - the free arm flung out forward and up to the image right (NO bomb in the hand: the bombs "
                "are drawn apart), the spear slanting in front of him."),
    "q_hold": ("spell@800", 35, "model", "扔完：一只拳头举在头旁边，长矛斜在身前，矛尖朝右下",
               "AFTER THE THROW - one fist raised beside his head, the spear slanting across him, the point to the "
               "lower right."),
    "e_wind": ("spell@0", 35, "flip", "长矛横扫起手：身体拧向后方，长矛抡到身后低处",
               "SWEEP WIND-UP - the body twisted back, the spear swung low behind him."),
    "e_sweep": ("leap@1214", 35, "model", "横扫：压低身子大弓步，长矛平着往前扫出去，矛尖在最右边",
                "SWEEP - a deep low lunge, the spear swept out level in front of him, the POINT at the far right."),
    "r_jump": ("leap@455", 35, "flip", "野火突袭起跳：跳起来，一只手举高，准备落到滑板上",
               "JUMP - hopping up, one arm thrown high, about to land on the hoverboard."),
    "r_land": ("leap@1062", 35, "model", "突袭落地：从滑板上跳下来重重落地，压低身子，长矛平端朝前",
               "LAND - off the board, landing hard and low, the spear held level, the POINT forward."),
    **{f"run{i + 1}": (f"run@{ms}", 35, "model", zh, en) for i, (ms, zh, en) in enumerate(WALK)},
    "d_fall": ("death@295", 35, "model", "被击倒：被打得往后仰，长矛脱手往上飞",
               "KNOCKED BACK - thrown backwards, the spear flying out of his hands."),
    "d_down": ("death@590", 35, "model", "倒地：仰面倒在地上，长矛掉在身边",
               "DOWN - lying on his back on the ground, the spear dropped beside him."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_scar_picture's renders (mirrored: facing image right)."""

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


def spear_line(xy, sv, head_xy, tip):
    """The spear's two ends on the canvas (butt, point): the extremes of its vertices along their main axis; the point
    is the end nearer the model's spearhead joint, or the other one ("flip")."""
    p = xy[sv]
    c = p.mean(axis=0)
    _, _, vt = np.linalg.svd(p - c, full_matrices=False)
    t = (p - c) @ vt[0]
    ends = sorted([c + vt[0] * t.min(), c + vt[0] * t.max()], key=lambda e: np.hypot(*(e - head_xy)))
    point, butt = ends
    if tip == "flip":
        point, butt = butt, point
    return tuple(butt), tuple(point)


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def skeleton(poser, joints, xy, z, hbox, out, spear, base=None):
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
            p = pts[2]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    butt, point = spear   # the shaft, then a triangle at the point
    d.line([butt, point], fill=COL["spear"], width=9)
    ux, uy = point[0] - butt[0], point[1] - butt[1]
    n_ = max(1e-6, float(np.hypot(ux, uy)))
    ux, uy = ux / n_, uy / n_
    tri = [(point[0] + ux * 30, point[1] + uy * 30), (point[0] - uy * 22, point[1] + ux * 22),
           (point[0] + uy * 22, point[1] - ux * 22)]
    d.polygon(tri, fill=COL["point"])
    d.ellipse([butt[0] - 9, butt[1] - 9, butt[0] + 9, butt[1] + 9], fill=COL["spear"])
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "CYAN (the L_ arm)" if zl > zr else "ORANGE (the R_ arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sc_work\scar_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = vertices_of(poser, HEAD_JOINTS)
    sv = vertices_of(poser, SPEAR_JOINTS)
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
    pelvis_x = dx + PELVIS_COL * PX + PX // 2   # the bbox-ratio way put the skeleton far left (Kobuko's lesson)
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, yaw, tip, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "flip", "", ""))] +
                                                            list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge (his body:
        # the spear lying beside him may run off it)
        lo, hi = xy[~sv, 0].min() + shift, xy[~sv, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        spear = spear_line(xy, sv, jxy[poser.names["Weapon_Spearhead"]], tip)
        skeleton(poser, joints, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), spear,
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        tris = poser.tris
        im = pose_ref.render_hq(pv, tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS), scale,
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
