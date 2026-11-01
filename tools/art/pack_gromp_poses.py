#!/usr/bin/env python3
"""Gromp's pose pack for Codex (assets/source/gromp/POSE_PROMPTS.md): the whole-body poses of its actions, each on a
skeleton projected from its OWN clips (its model and clips are in the Riot client: TFTSet18.wad.client and Map11's
sru_gromp on the same skeleton - the Murk Wolf's way).

    python tools/art/pack_gromp_poses.py [--out D:/TFM2-Workshop/gromp_packs/gromp_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of its clips (pack_gromp_picture.CLIPS). Its death clip sinks it into the ground within
0.1 s (nothing to draw), so the two death poses are the idle frame tipped over backwards by TILT degrees about its
side-to-side axis (d_down: on its back, belly up). All are seen from the design's angle (3/4 facing right, yaw 35). One
scale for all: the design pose's whole height (idle@0, the frame step 0's A was drawn from: the mushroom caps to its
feet) = the design's 54 rows (hd/idle.png: A-1 at 32 game px, PPU 1.69, 1:1) at PX px a square; the lowest point of
every pose on y SOLE_Y, its root on the design's root column (by the ratio of the design's box to the model's). The
head is not grown: its Head joint carries half the body (Codex wears the design's head anyway).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (its model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (rump to shoulders), BROWN = the belly (the throat sac's bones), ORANGE = the head
(to the upper lip), YELLOW = the lower jaw, RED / BLUE = the L_ / R_ front leg, PINK / CYAN = the L_ / R_ hind leg (the
renders are mirrored: which side is nearer the camera is written per pose), grey box = the face.
Its run is one hop (TFT's 0.53 s clip: crouch, push off, stretched out in the air, land), sampled evenly at RUN_MS over
the whole clip (tft-run-full-cycle).
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
from design_gromp_hd import lp  # noqa: E402
from pack_gromp_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gromp")
PX, CANVAS, SOLE_Y = 7, 1254, 1176
ROWS = 54                      # hd/idle.png's height
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (44, 0, 92, 30)     # the design's face (the blue mushroom, the brow, the eyes, the tusks) in hd/idle.png
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "belly": (140, 90, 40), "head": (245, 140, 0), "jaw": (230, 210, 0),
       "L_front": (230, 30, 30), "R_front": (40, 90, 230), "L_hind": (240, 80, 170), "R_hind": (0, 190, 210)}
CHAINS = {"spine": ["Pelvis", "Root", "Spine1"],
          "belly": ["Spine1", "Chest1", "Chest2"],
          "head": ["Spine1", "Head", "Upper_Lip"],
          "jaw": ["Head", "Jaw", "L_Lip"],
          "L_front": ["Spine1", "L_Clavicle", "L_Shoulder", "L_Elbow", "L_Hand", "L_Finger"],
          "R_front": ["Spine1", "R_Clavicle", "R_Shoulder", "R_Elbow", "R_Hand", "R_Finger"],
          "L_hind": ["Pelvis", "L_Hip", "L_KneeUpper", "L_KneeLower", "L_Foot", "L_Toe"],
          "R_hind": ["Pelvis", "R_Hip", "R_KneeUpper", "R_KneeLower", "R_Foot", "R_Toe"]}
FACE_JOINTS = ("Jaw", "Upper_Lip", "L_Lip", "R_Lip", "L_Eye", "R_Eye")
RUN_MS = (0, 66, 133, 200, 266, 333, 400, 466)   # the one 0.53 s hop, evenly
RUN_ZH = ("蛙跳 1/8：蹲着，准备起跳", "蛙跳 2/8：后腿开始蹬，身子抬起来", "蛙跳 3/8：蹬离地面，前爪伸向前方",
          "蛙跳 4/8：腾空，整个身子往前伸长，后腿在后面蹬直", "蛙跳 5/8：腾空最远，后腿拖在后面",
          "蛙跳 6/8：往下落，前爪先着地", "蛙跳 7/8：落地，身子压扁一点、后腿收回",
          "蛙跳 8/8：重新蹲好（8 接回 1，循环）")
RUN_EN = ("HOP 1 of 8 - crouched, about to spring.", "HOP 2 of 8 - the hind legs starting to push, the body rising.",
          "HOP 3 of 8 - pushing off the ground, the front hands reaching forward.",
          "HOP 4 of 8 - in the air, the whole body stretched forward, the hind legs kicked out straight behind.",
          "HOP 5 of 8 - at the farthest, the hind legs trailing behind.",
          "HOP 6 of 8 - coming down, the front hands touching first.",
          "HOP 7 of 8 - landing, the body squashed a little, the hind legs drawn in.",
          "HOP 8 of 8 - crouched again (8 runs on into 1: the loop).")

# name -> (clip@ms, yaw, tilt back in degrees, what it is for (Chinese), the pose line (English))
POSES = {
    "a_back": ("spit@133", 35, 0, "普攻「毒涎吐射」起手：头往后一收，肚子吸气鼓起一点",
               "GATHER - the head drawn back a little, the belly drawing breath."),
    "a_spit": ("spit@266", 35, 0, "吐出：头往前上方一探，嘴张开吐出一口（口水不画，只画张开的嘴）",
               "SPIT - the head thrust up and forward, the mouth open (do NOT draw the spit itself)."),
    "q_puff": ("puff@650", 35, 0, "技能1「打嗝泡泡」起手：肚子鼓到很大，身子往后坐一点，嘴闭着",
               "SWELL - the belly blown up big and round, the body sitting back a little, the mouth shut."),
    "q_belch": ("roar@380", 35, 0, "打嗝：仰起身子，嘴张到最大往前打一个嗝（舌头不伸出来，泡泡不画）",
                "BELCH - reared up, the mouth open as wide as it goes, belching forward (the tongue NOT out, do "
                "NOT draw the bubble)."),
    "e_back": ("attack@228", 35, 0, "技能2「黏液沼泽」起手：身子往后缩、压低，头收回",
               "DRAW BACK - the body pulled back and low, the head pulled in."),
    "e_spit": ("attack@380", 35, 0, "往地上吐黏液：身子往前一扑，头往前下方伸，嘴张开（舌头不伸出来，黏液不画）",
               "SPIT DOWN - lunging forward, the head reaching forward and down, the mouth open (the tongue NOT out, "
               "do NOT draw the slime)."),
    "r_rear": ("roar@228", 35, 0, "大招「毒沼大嗝」起手：身子高高仰起，肚子开始鼓起来",
               "REAR UP - the body rearing up high, the belly starting to swell."),
    "r_belch": ("roar@456", 35, 0, "大嗝：头高高仰起、嘴张到最大，肚子鼓到最大（比 q_puff 还大），往前喷出一大口（毒雾不画）",
                "BIG BELCH - the head thrown up high, the mouth open as wide as it goes, the belly at its BIGGEST "
                "(even bigger than in q_puff), blasting forward (do NOT draw the poison cloud)."),
    **{f"run{k + 1}": (f"run@{t}", 35, 0, zh, en) for k, (t, zh, en) in enumerate(zip(RUN_MS, RUN_ZH, RUN_EN))},
    "d_fall": ("idle@0", 35, 45, "被打倒：往后翻倒，前半身翘起，四条腿离地乱蹬，嘴张开",
               "KNOCKED OVER - tipping over backwards, the front half up in the air, all four legs off the ground "
               "kicking, the mouth open."),
    "d_down": ("idle@0", 35, 160, "倒地：肚皮朝天仰躺在地上，四条腿朝上，眼睛熄灭（画成暗灰色，不发光）",
               "DOWN - lying on its back, the belly up, all four legs in the air, the eyes gone dark (a dull dark "
               "grey, no glow)."),
}


class Poser:
    """Its mesh and joints, projected as pack_gromp_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris
        # the vertices the drawn triangles use: the hidden spawn mesh and mini Gromp lie far below it
        self.vis = np.zeros(len(self.m.v), bool)
        self.vis[np.unique(self.tris)] = True

    def pose(self, clip, tilt=0):
        name, ms = clip.split("@")
        wad, h = CLIPS[name]
        anim = pose_ref.read_anim(self.m.wads[wad].read(h))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        glob = pose_ref.globals_(self.m.joints, [pose_ref.trs(*p) for p in local])
        verts = pose_ref.skin(self.m.v, self.m.infl, self.m.bind_inv, glob)
        joints = np.array([g[:3, 3] for g in glob])
        if tilt:   # the whole body tipped over backwards about its side-to-side axis (model x) through the root
            c, s = np.cos(np.radians(-tilt)), np.sin(np.radians(-tilt))
            rot = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
            at = joints[self.names["Root"]]
            verts = (verts - at) @ rot.T + at
            joints = (joints - at) @ rot.T + at
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


def face_vertices(poser):
    """The vertices mostly weighted to the face (jaw, lips, eyes)."""
    m = poser.m
    joint_of = np.array(m.infl)[m.v["bones"].astype(np.int64)]
    main = joint_of[np.arange(len(m.v)), np.argmax(m.v["w"], axis=1)]
    face = {i for i, j in enumerate(m.joints) if j["name"] in FACE_JOINTS}
    return np.isin(main, list(face)) & poser.vis


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


def near_side(z, poser):
    """Which legs are nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    out = []
    for part in ("front", "hind"):
        zl = np.mean([z[poser.names[n]] for n in CHAINS["L_" + part][1:]])
        zr = np.mean([z[poser.names[n]] for n in CHAINS["R_" + part][1:]])
        out.append(("L" if zl > zr else "R") + "_" + part)
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\TFM2-Workshop\gromp_packs\gromp_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    os.makedirs(lp(a.out), exist_ok=True)
    poser = Poser(a.lol)
    fv = face_vertices(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size

    # one scale for every pose: the design pose's whole height = the design's rows
    iv, ij = poser.pose(DESIGN)
    iv = iv[poser.vis]
    (pxy, _) = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[:, 1].max() - pxy[:, 1].min())
    pel = poser.names["Root"]
    # the design on the canvas: its soles on SOLE_Y, centred; every pose's root on the design's root column, placed by
    # the ratio of the design's box to the model's
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - ROWS * PX
    ix = Poser.project(iv, YAW, scale, 0.0, 0.0)[0][:, 0]
    jx = Poser.project(ij, YAW, scale, 0.0, 0.0)[0][pel, 0]
    x0, _, x1, _ = design.getbbox()
    col = x0 + (jx - ix.min()) / (ix.max() - ix.min()) * (x1 - x0)
    print("root column", round(col, 1))
    pelvis_x = dx + round(col * PX)
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, ROWS * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    for k, (name, (clip, yaw, tilt, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, 0, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip, tilt)
        xy, _ = Poser.project(verts[poser.vis], yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas (the hop stretched out, lying on its back) moved back inside
        lo, hi = np.percentile(xy[:, 0], 0.5) + shift, np.percentile(xy[:, 0], 99.5) + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[fv[poser.vis], 0], xy[fv[poser.vis], 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), can if name == "idle" else None)
        if name == "idle":
            print("idle near", near_side(jz, poser))
            continue
        # the textured model in the same place: render_hq's own projection (x0 from the mirrored shift)
        im = pose_ref.render_hq(verts.copy(), poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS),
                                scale, ground, shift=-shift / CANVAS - 0.5).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        print(stem, clip, "tilt", tilt, "near", near_side(jz, poser))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
