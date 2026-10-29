#!/usr/bin/env python3
"""Renni's pose pack for Codex (assets/source/renni/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet13.wad.client, so her
skeletons are her animator's - Violet's and Scar's way).

    python tools/art/pack_renni_poses.py [--out C:/t/rn_work/renni_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_renni_picture.CLIPS, named by what they show), the head grown to the
design's (pose_ref.chibi, HEAD_SCALE: the design's head with the hair is over a third of her height, TFT's model's
much less). All are seen from the design's angle (3/4 facing right, yaw 35). No grind pose for the charge: lift@200
swung the saw back over her head, so the charge's grind plays the attack's frames. One scale for all: the design pose's
body height (stance@0, the stance step 0's B was drawn from: hair to soles, the saw left out) = the design's 76 body
rows (hd/idle.png: B-1 at 38 game px, PPU 2.0) at PX px a square; the lowest point of every pose on y SOLE_Y, her
pelvis on the design pose's pelvis column.
Her chainsaw: the skeleton draws it itself - a bar along the main axis of the saw's vertices (submesh Weapon), a GOLD
triangle at its BAR TIPS (the end away from the engine joint ChainsawEngine), a ring at the ENGINE end.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = her R_ arm, CYAN = her L_ arm, RED =
left leg, BLUE = right leg, PURPLE = the chainsaw (a ring at the engine, a GOLD triangle at the bar tips), grey box =
the head.
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
from design_renni_hd import lp  # noqa: E402
from pack_renni_picture import Model, CLIPS, SKN  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renni")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 76                     # hd/idle.png's body rows (hair to soles: rows 1-76)
HEAD_SCALE = 1.7
DESIGN = "stance@0"            # the stance step 0's B was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (24, 0, 48, 29)      # the design's head with the hair and the respirator (hd/idle.png)
PELVIS_COL = 27                 # the design's pelvis column: between its legs (cols 10-23 and 28- at row 56)
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "spear": (120, 40, 170), "point": (230, 175, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle1"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle1"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Eye", "Brow", "Jaw", "Lip", "MouthCrnr", "Teeth", "HeadTube")
SAW_SUBMESH = "Weapon"

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
RUN = [
    (0, "跑 1：弓着身子跑（金铲铲原样），链锯低低地拎在身侧",
     "RUN 1 - a hunched run (as in the game), the chainsaw carried low at her side."),
    (141, "跑 2", "RUN 2"), (283, "跑 3", "RUN 3"), (424, "跑 4", "RUN 4"), (566, "跑 5", "RUN 5"),
    (707, "跑 6", "RUN 6"), (849, "跑 7", "RUN 7"), (990, "跑 8", "RUN 8"),
]
POSES = {
    "a_push": ("stance@320", 35, "普攻（链锯研磨）：定稿的架势，身体往前压，链锯往前一顶，导板尖顶在最前面",
               "GRIND PUSH - the design's stance leaning in, the chainsaw shoved forward, the BAR TIPS leading."),
    "a_grind": ("stance@640", 35, "研磨：链锯顶在前面上下颠一下（锯着目标），身体随之一沉",
                "GRIND - the saw held out in front, jolting as it bites, her body dipping with it."),
    "q_charge": ("lift@0", 35, "链锯冲撞：大弓步往前冲，身体压得很低，链锯平端顶在最前面",
                 "CHARGE - a deep forward lunge, body low, the chainsaw level and thrust out ahead."),
    "e_guard": ("idle@860", 35, "锯刃格挡：两脚叉开站稳，链锯竖起来挡在身前（导板朝上，引擎在胸前），像一面盾",
                "SAW GUARD - feet planted wide, the chainsaw raised UPRIGHT in front of her body (the bars up, the "
                "engine at her chest) like a shield."),
    "r_ram": ("lift@330", 35, "泥奔者重击 1：链锯往前上方一顶，把目标挑起来（不画目标）",
              "RAM - the saw driven forward and upward to hook the target (do NOT draw the target)."),
    "r_heave": ("lift@600", 35, "举起：链锯往头顶上抡，导板朝上",
                "HEAVE - swinging the saw up over her head, the bars rising."),
    "r_hold": ("hold@0", 35, "举在头顶：双手把链锯直直举过头顶，导板朝天（目标挂在上面，不画）",
               "HOLD - both arms straight up, the chainsaw held high overhead, the bars pointing to the sky (the "
               "target hangs on it: do NOT draw it)."),
    "r_slam": ("slam@470", 35, "砸地：整个人往前扑，链锯狠狠砸在面前的地上",
               "SLAM - lunging forward, the chainsaw smashed down onto the ground in front of her."),
    "r_after": ("slam@940", 35, "砸完：链锯拖在地上，慢慢回到架势",
                "AFTER THE SLAM - the saw dragging on the ground, rising back toward the stance."),
    **{f"run{i + 1}": (f"run@{ms}", 35, zh, en) for i, (ms, zh, en) in enumerate(RUN)},
    "d_fall": ("death@333", 35, "被击倒：被打得往上往后飞，链锯脱手",
               "KNOCKED BACK - thrown up and back, the saw flying from her hands."),
    "d_down": ("death@1000", 35, "倒地：仰面平躺在地上，链锯掉在身边",
               "DOWN - lying flat on her back, the saw dropped beside her."),
}


class Poser:
    """Her mesh (head grown) and joints, projected as pack_renni_picture's renders (mirrored: facing image right)."""

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


def saw_vertices(poser):
    """The chainsaw's vertices: its submesh's vertex range."""
    b = poser.m.w.read_path(SKN)
    return pose_ref.submesh_vertex_maps(b, len(poser.m.v), [([SAW_SUBMESH], 1)]) == 1


def saw_line(xy, sv, engine_xy):
    """The saw's two ends on the canvas (engine end, bar tips): the extremes of its vertices along their main axis;
    the tips are the end away from the engine joint."""
    p = xy[sv]
    c = p.mean(axis=0)
    _, _, vt = np.linalg.svd(p - c, full_matrices=False)
    t = (p - c) @ vt[0]
    engine, tips = sorted([c + vt[0] * t.min(), c + vt[0] * t.max()], key=lambda e: np.hypot(*(e - engine_xy)))
    return tuple(engine), tuple(tips)


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
    ap.add_argument("--out", default=r"C:\t\rn_work\renni_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = vertices_of(poser, HEAD_JOINTS)
    sv = saw_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS + 1, design.size   # her hair starts on row 1

    # one scale for every pose: the design pose's body height (the saw left out) = the design's body rows
    iv, ij = poser.pose(DESIGN)
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[~sv, 1].max() - pxy[~sv, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the design pose's pelvis lands on the same column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - design.height * PX
    pelvis_x = dx + PELVIS_COL * PX + PX // 2   # the bbox-ratio way put the skeleton far left (Kobuko's lesson)
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, design.height * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] +
                                                            list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (lying on the ground) moved back inside, MARGIN from the edge (her body:
        # the saw lying beside her may run off it)
        lo, hi = xy[~sv, 0].min() + shift, xy[~sv, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        spear = saw_line(xy, sv, jxy[poser.names["ChainsawEngine"]])
        skeleton(poser, joints, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), spear,
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        im = pose_ref.render_hq(pv, poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS), scale,
                                ground, shift=x0 / CANVAS - 0.5, tri_tex=poser.m.tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
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
