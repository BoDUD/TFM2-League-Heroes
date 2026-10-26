#!/usr/bin/env python3
"""Alune's pose pack for Codex (assets/source/alune/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (Norra / Zaahen got skeletons set by hand after videos; Alune's model and clips
are in the Riot client's TFTSet18.wad.client, so her skeletons are her animator's).

    python tools/art/pack_alune_poses.py [--out C:/t/al_work/alune_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_alune_picture.CLIPS, named by what they show), posed with TFM2's
chibi head (pose_ref.chibi, HEAD_SCALE: the design's head is about a third of her height) and seen from the design's
angle (3/4 facing right: her sitting clips at yaw 305 like the design's references, her standing ones at 35 - they turn
her body round to face the target). One scale for all: the idle frame's whole height (horns to the crescent's foot) =
the design's 90 rows (hd/idle.png: step 0's A-1 at 46 game px, PPU 2.0, the horn tip trimmed) at PX px a square; the
lowest point of every pose on y SOLE_Y, her pelvis on the idle's pelvis column.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head, horns, hair and face 8x: every pose wears
it); per pose <k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and
<k>_<name>_skeleton.png (its bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = her LEFT arm, PURPLE = her RIGHT arm
(which one is near the camera depends on the pose: the prompt says it), RED = left leg, BLUE = right leg (both mostly
under the robe), GOLD = the crescent glaive (its handle line, a dot at the spiral ring's moon orb), grey box = the head.
The run is not her own clip (TFT's run stands her on the crescent far above it, the ring floating over her head: far
taller than the design); the run here is the idle's gliding seat, leaning on, from the idle clip.
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
from design_alune_hd import lp  # noqa: E402
from pack_alune_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "alune")
PX, CANVAS, SOLE_Y = 12, 1254, 1176
ROWS = 90                     # hd/idle.png's height
HEAD_SCALE = 1.6
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "glaive": (210, 160, 20)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Spine2", "Spine3", "Neck"],
          "L_arm": ["L_Shoulder", "L_ElbowLower", "L_Hand", "L_Middle3"],
          "R_arm": ["R_Shoulder", "R_ElbowLower", "R_Hand", "R_Middle3"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"],
          "glaive": ["Weapon", "Weapon_Center", "Buffbone_Glb_Weapon_1"]}
ORB = "Weapon_Orb1"
HEAD_JOINTS = ("Head", "Jaw", "L_Horn", "R_Horn", "Hair", "PonyTail", "EarRing", "Eye", "Mouth")

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack@0", 35,
               "普攻起手：从月牙上站起来，身子往前压，双手把螺旋月环平端在身前（像端着一个大飞盘），远侧那只手在环下面托着",
               "WIND-UP - standing now, leaning forward, BOTH hands holding the SPIRAL RING flat before her like a big "
               "disc, about to fling it."),
    "a_throw": ("attack@400", 35,
                "甩出月环：身子往前探、后脚抬起，近侧那只手把月环平着往前（画面右边）推出去，月环离手飞向目标",
                "FLING - leaning far forward, the back foot lifted, the near arm pushing the SPIRAL RING out flat to the "
                "image right at chest height, the ring just leaving her hand."),
    "a_catch": ("attack@933", 35,
                "收回：身子收回站直，手往身前伸着接住飞回来的月环（月环回到手边）",
                "CATCH - straightening up again, the hand out before her catching the SPIRAL RING as it comes back."),
    "q_raise": ("spell@0", 35,
                "引月起手：站着，把螺旋月环竖着举在身侧（画面右边、肩膀高度），像一面发光的圆盾，另一只手放在胸前",
                "RAISE THE RING - standing, the SPIRAL RING held UPRIGHT at her side (image right, shoulder height) like a "
                "round shield, her other hand on her chest."),
    "q_call": ("dance@3400", 35,
               "召唤月光碎片：一只手握拳高高举过头顶（在头的左后方，不挡脸），月环竖在身侧，脸朝右前方（月光碎片从天上落下）",
               "CALL DOWN - one fist thrust high over her head (behind the left of the head, never over the face), the "
               "SPIRAL RING upright at her side, her face to the front-right (the moonshards fall now)."),
    "e_bless": ("idle2@278", 305,
                "月华（坐着放）：还坐在月牙上，近侧那只手往上方一扬、手掌朝上（给队友加攻速），另一只手留在胸前",
                "MOONLIGHT - still SITTING on the crescent as in the design, one hand swept up and out with the palm open "
                "(blessing her allies), the other arm still across her chest."),
    "r_raise": ("dance@10200", 35,
                "满月起手：站着，双手把螺旋月环高高举过头顶（月环在头的上方和后方，像一轮光环，不挡脸）",
                "MOON RISES - standing, BOTH hands lifting the SPIRAL RING high above and behind her head like a halo "
                "(never over the face)."),
    "r_call": ("dance@2267", 35,
               "满月降临：一只手笔直指向天空（在头的旁边），身子往后仰，月环甩在身侧下方（满月从天上砸下来）",
               "MOON FALLS - one arm thrust straight up at the sky beside her head, leaning back, the SPIRAL RING swung "
               "down at her side (the full moon is falling now)."),
    "run1": ("idle@0", 305,
             "移动 1：和定稿一样侧坐在月牙上，整个人往前（画面右边）倾一点，像坐着滑行；头发、长袍下摆往后（画面左边）飘",
             "GLIDE 1 - SITTING on the crescent exactly as in the design, the whole figure tilted a little forward (to "
             "the image right) as she glides, her hair and the robe's hem streaming back (to the image left)."),
    "run2": ("idle@417", 305,
             "移动 2：同上，整体往上浮一格，下摆往后飘得更开",
             "GLIDE 2 - the same, one square higher, the hem streaming further back."),
    "run3": ("idle@833", 305,
             "移动 3：同 1，下摆往回收一点",
             "GLIDE 3 - as GLIDE 1, the hem swinging in a little."),
    "run4": ("idle@1250", 305,
             "移动 4：同 2，整体往下沉回原位",
             "GLIDE 4 - as GLIDE 2, sinking back down."),
    "d_fall": ("death@208", 305,
               "被击倒：从月牙上往后（画面左边）仰倒，双手往上甩开（不挡脸），月牙法杖从身下滑开",
               "KNOCKED OFF - thrown back off the crescent toward the image left, both arms flung up (never over the "
               "face), the glaive sliding out from under her."),
    "d_down": ("death@1458", 305,
               "倒地：仰躺在地上，长袍铺开，月牙法杖碎成几个圆环散落在她身边",
               "DOWN - lying on her back on the ground, the robe spread out, the crescent glaive BROKEN into a few loose "
               "rings lying around her."),
}


class Poser:
    """Her chibi-posed mesh and joints, projected as pack_alune_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}

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


def head_vertices(poser):
    """The vertices mostly weighted to the head and what hangs off it (horns, hair, earrings, eyes, jaw)."""
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
        if c.endswith("arm"):
            p = pts[2]
            d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=COL[c])
    p = xy[poser.names[ORB]]
    d.ellipse([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14], outline=COL["glaive"], width=6)
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "ORANGE (her left)" if zl > zr else "PURPLE (her right)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\al_work\alune_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    hv = head_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # one scale for every pose: the idle's whole height = the design's rows
    iv, ij = poser.pose("idle@0")
    (pxy, _) = Poser.project(iv, 305, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the idle's pelvis lands on the same canvas column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    ixy, _ = Poser.project(iv, 305, scale, 0.0, 0.0)
    pelvis_x = dx + (ixy[pel, 0] - ixy[:, 0].min()) / (ixy[:, 0].max() - ixy[:, 0].min()) * design.width * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop((14, 0, 56, 30))
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    notes = {}
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", ("idle@0", 305, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, joints, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"),
                 can if name == "idle" else None)
        if name == "idle":
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        pv = verts.copy()
        x0 = -shift   # project() drew v0 * scale + 0 then flipped and moved by shift: render_hq's x origin is -shift
        im = pose_ref.render_hq(pv, poser.m.tris, poser.m.v["uv"], None, -yaw, PITCH, (CANVAS, CANVAS), scale,
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
