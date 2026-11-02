#!/usr/bin/env python3
"""The Cinderling's (绯红树怪) pose pack for Codex (assets/source/cinderling/POSE_PROMPTS.md): the whole-body poses of its
actions, each on a skeleton projected from its OWN clips (its model and clips are in the Riot client's
TFTSet18.wad.client, so its skeletons are its animator's - the Crimson Brambleback's way).

    python tools/art/pack_cinderling_poses.py [--out D:/TFM2-Workshop/cinderling_packs/cinderling_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_cinderling_picture.CLIPS), the head (the wooden mask) grown by
HEAD_SCALE. All are seen from the design's angle (3/4 facing right, yaw 40). One scale for all: the design pose's
whole height (idle@0, the frame step 0's A was drawn from: the tallest leaf to the claws) = the design's 70 rows
(hd/idle.png: A-1 at 30 game px, PPU 2.33) at PX px a square; the lowest point of every pose on y SOLE_Y - except the
poses in AIR, which keep their height above the design's ground (the hops, the leap out of the ground), and BURIED,
whose lower half is under the ground (cut at the red line in the reference) - its root on the design's root column
(PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's mask 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), PINK = the L_ front leg (shoulder to paw), CYAN = the R_ front
leg, RED = the L_ back leg, BLUE = the R_ back leg, YELLOW = the tallest leaf of the mane (C_Leaf), grey box = the head.
It has NO run clip: its run is four hops from its own attack (attack@312 crouched, 468 springing, 624 in the air,
780 landing - the hop it makes to attack, without the fling), a small critter bounding along.
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
from design_cinderling_hd import lp  # noqa: E402
from pack_cinderling_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "cinderling")
PX, CANVAS, SOLE_Y = 8, 1254, 1176
ROWS = 70                     # hd/idle.png's height
HEAD_SCALE = 1.3             # the model's mask grown toward the design's (Codex wears the design's mask anyway)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (40, 26, 80, 60)    # the design's mask (the big eye, the G spiral, the fangs) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 40
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (240, 80, 170), "R_arm": (0, 190, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "mane": (235, 200, 0)}
CHAINS = {"spine": ["Root", "Spine1", "Spine2", "Neck", "Head"],
          "L_arm": ["Spine2", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand", "L_Paw"],
          "R_arm": ["Spine2", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Hand", "R_Paw"],
          "L_leg": ["Root", "L_Hip", "L_Knee", "L_Foot", "L_Toe"],
          "R_leg": ["Root", "R_Hip", "R_Knee", "R_Foot", "R_Toe"],
          "mane": ["Spine1", "C_Leaf1", "C_Leaf2"]}
HEAD_JOINTS = ("Head", "Jaw", "L_Mask", "R_Mask")
AIR = {"a_fling", "run2", "run3", "e_pop"}   # kept at their height above the ground
BURIED = {"e_dig"}                           # half under the ground

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_fling": ("attack@520", 40, "普攻「余烬叶」：往前一蹦（脚离地），背上的叶子往后上方甩起（甩出去的叶子是特效，这里只画身体和鬃毛）",
                "FLING - hopping forward off the ground, the leaf mane flung up and back as it throws a leaf (draw "
                "the body and the mane only, no flying leaf)."),
    "q_bristle": ("rear@120", 40, "技能1「刃叶」蓄力：身子往后缩、压低，背上的叶子鬃毛全部高高竖起、张开",
                  "BRISTLE - drawing back and crouching low, the whole leaf mane raised tall and fanned open."),
    "q_throw": ("rear@180", 40, "刃叶甩出：身子往前一探，前爪往前伸，叶子鬃毛往前甩（飞出去的叶刃是特效）",
                "THROW - lunging forward, the front paws reaching ahead, the leaf mane whipped forward (no flying "
                "leaves: they are separate effects)."),
    "e_dig": ("spawn@1180", 40, "技能2「钻土突袭」钻地：下半身已经钻进地里（红线以下什么都不画），只露出面具、前爪和背上的叶子",
              "DIG - half sunk into the ground: everything below the red ground line is hidden (draw nothing below "
              "it), only the mask, the front paws and the leaf mane above the ground."),
    "e_pop": ("spawn@1320", 40, "钻出：从地里一跃而出，整个身子腾空（脚离地），四肢往下伸、准备落地",
              "POP OUT - bursting up out of the ground into the air (feet off the ground), the legs reaching down "
              "to land."),
    "r_rear": ("rear@540", 40, "大招「燎原叶暴」：用后腿站起来，身子挺直，两只前爪往前张开，面具抬起",
               "REAR UP - standing up on its back legs, the body upright, both front paws spread forward, the mask "
               "raised."),
    "r_roar": ("rear@660", 40, "站立怒吼：后腿站立，身子往后仰到最高，前爪收在胸前，叶子鬃毛竖在背后（叶子着火是特效）",
               "ROAR - standing on its back legs, leaning back at its tallest, the front paws drawn to the chest, "
               "the leaf mane standing behind it (the fire is a separate effect)."),
    "run1": ("attack@312", 40, "蹦 1：四肢收拢、身子压低蹲紧，准备往前蹦",
             "HOP 1 - crouched low and tight on all fours, gathering to hop forward."),
    "run2": ("attack@468", 40, "蹦 2：后腿一蹬往前上方蹦起（脚离地），前爪往前伸，叶子往后飘",
             "HOP 2 - the back legs kicking off, springing up and forward (feet off the ground), the front paws "
             "reaching ahead, the leaves streaming back."),
    "run3": ("attack@624", 40, "蹦 3：在空中最高处，四肢舒展，叶子往后飘",
             "HOP 3 - at the top of the hop in the air, the legs stretched, the leaves streaming back."),
    "run4": ("attack@780", 40, "蹦 4：前爪先落地，身子往前压，后腿跟上（4 接回 1，循环）",
             "HOP 4 - landing on the front paws first, the body pressed forward, the back legs coming down (4 runs "
             "on into 1: the loop)."),
    "d_flip": ("death@250", 40, "被打倒：往后一翻，身子竖起来翻过去，四肢乱蹬",
               "FLIP - knocked over backwards, the body flipping up and over, the legs flailing."),
    "d_down": ("death@1000", 40, "倒地：四脚朝天仰面躺在地上不动，眼睛和螺旋纹熄灭（画成暗褐色）",
               "DOWN - lying still on its back, legs up, the eye and the spiral gone dark (a dull dark brown, no "
               "glow)."),
}


class Poser:
    """Its mesh (head grown) and joints, projected as pack_cinderling_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        local = pose_ref.chibi(self.m.joints, local, 1.0, scale={"Head": HEAD_SCALE})
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
    """The vertices mostly weighted to the head."""
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
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\cinderling_packs\cinderling_pose_pack")
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

    ixy, _ = Poser.project(poser.pose(DESIGN)[0], YAW, scale, 0.0, 0.0)
    idle_ground = SOLE_Y - ixy[:, 1].max()
    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, _ = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        if name in AIR or name in BURIED:   # its height above (or depth under) the design's ground kept
            ground = idle_ground
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
        if name in BURIED:   # under the ground: nothing to draw
            ImageDraw.Draw(ref).rectangle((0, SOLE_Y + 1, CANVAS, CANVAS), fill=GREY + (255,))
            grid(ImageDraw.Draw(ref))
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "yaw", yaw, "near", near_leg(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
