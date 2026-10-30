#!/usr/bin/env python3
"""Terra's pose pack for Codex (assets/source/terra/POSE_PROMPTS.md): the whole-body poses of her actions, each on a
skeleton projected from her OWN clips (her model and clips are in the Riot client's TFTSet7.wad.client, so her
skeletons are her animator's - Nomsy's way).

    python tools/art/pack_terra_poses.py [--out C:/t/te_work/terra_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of her clips (pack_terra_picture.CLIPS), the head grown to the design's chibi share (HEAD_SCALE
1.7: head 0.375 of the idle's width and 0.73 of its height, the design 0.36 / 0.73). All are seen from the design's angle (3/4 facing right, yaw 35). One scale for
all: the design pose's whole height (idle@0, the frame step 0's A was drawn from: the wing-bone tips to her soles) = the
design's 52 rows (hd/idle.png: A-1 at 36 game px, PPU 1.45, 1:1) at PX px a square; the lowest point of every pose on
y SOLE_Y (a pose in the air is drawn standing on the line too: the rig lifts it), her root on the design's root column
(PELVIS_COL: None places it by the ratio of the design's box to the model's).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (her model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (root to the head), ORANGE = the L_ front leg, PURPLE = the R_ front leg, RED = the
L_ hind leg, BLUE = the R_ hind leg, BROWN = the tail, PINK = the L_ wing, CYAN = the R_ wing (the renders are mirrored:
which side is nearer the camera is written per pose), grey box = the head.
Her flight (TFT's run: she flies everywhere, the body turned to the camera, nose down) keeps the design's body: in
HOVER_POSES the spine, neck, head and tail take the idle's transforms, the wings and legs keep the flight's. Spread, her
wings span about three of her bodies, so in WING_POSES both are shrunk to WING_SCALE.
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
from design_terra_hd import lp  # noqa: E402
from pack_terra_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "terra")
PX, CANVAS, SOLE_Y = 9, 1254, 1176
ROWS = 52                     # hd/idle.png's height
HEAD_SCALE = 1.7             # the model's head grown to the design's share (0.36 of the width, 0.73 of the height)
DESIGN = "idle@0"              # the frame step 0's A was drawn from
HEAD_BOX = (55, 12, 86, 50)    # the design's head (the brow plates, the eye, the fangs, the jaw) in hd/idle.png
PELVIS_COL = None              # None: by the box ratio (printed)
YAW = 35
MARGIN = 40
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "L_arm": (255, 140, 0), "R_arm": (150, 60, 200), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "tail": (120, 70, 30), "L_wing": (240, 80, 170), "R_wing": (0, 190, 210)}
CHAINS = {"spine": ["Root", "Spine1", "Spine2", "Spine3", "Spine4", "Neck", "Neck1", "Head"],
          "L_arm": ["L_Clavicle", "L_Shoulder", "L_Elbow", "L_Paw", "L_PawToe"],
          "R_arm": ["R_Clavicle", "R_Shoulder", "R_Elbow", "R_Paw", "R_PawToe"],
          "L_leg": ["Pelvis", "L_Hip", "L_Knee", "L_Ankle", "L_Foot", "L_Toe"],
          "R_leg": ["Pelvis", "R_Hip", "R_Knee", "R_Ankle", "R_Foot", "R_Toe"],
          "tail": ["Pelvis", "Tail1", "Tail2", "Tail3", "Tail4", "Tail5", "Tail6"],
          "L_wing": ["L_Wing_Clavicle", "L_Wing_Upper", "L_Wing_Mid1", "L_Wing_Mid", "L_Wing_Lower", "L_Wing_Tip"],
          "R_wing": ["R_Wing_Clavicle", "R_Wing_Upper", "R_Wing_Mid1", "R_Wing_Mid", "R_Wing_Lower", "R_Wing_Tip"]}
HEAD_JOINTS = ("Head", "Jaw", "Gill")
WING_SCALE = 0.6
RUN_MS = (0, 146, 292, 438, 584, 876)   # one wing beat of TFT's flight (1.17 s): up, top, level, down, bottom, rising
HOVER_POSES = tuple(f"run@{t}" for t in RUN_MS)
WING_POSES = HOVER_POSES + ("attack@850", "attack@1000", "bite@150", "spell@500", "spell@875", "celebration@500",
                            "celebration@1250", "death@1000")
BODY_JOINTS = ("Root", "Spine1", "Spine2", "Spine3", "Spine4", "Neck", "Neck1", "Head", "Jaw", "Pelvis", "Tail1", "Tail2",
               "Tail3", "Tail4", "Tail5", "Tail6")
WING_LINES = {}   # (Nomsy's straight wing lines: Terra's own wings turn with her body)
WING_JOINTS = ()

# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack@850", 35, "普攻「岩爪」起手：前身抬起、头往后上方仰，翅膀半张，蓄力",
               "WIND UP - the front of the body lifted, the head drawn back and up, the wings half open, gathering."),
    "a_hit": ("attack@1000", 35, "岩爪落下：头和前身猛地往前下方压，近处的前爪往前拍下，嘴张开咬",
              "STRIKE - the head and the front of the body slammed forward and down, the near front claw raking "
              "forward, the jaw open snapping."),
    "q_crouch": ("bite@150", 35, "技能1「裂地咬」起手：身子压低蹲伏，头贴近地面，翅膀张开，准备扑出去",
                 "CROUCH - the body pressed low, the head down near the ground, the wings open, about to pounce."),
    "q_pounce": ("spell@875", 35, "扑出：整个身子腾空往前扑，前爪伸向前方，翅膀往后扬（画在地面线上，游戏里会抬高）",
                 "POUNCE - the whole body leaping forward off the ground, the front claws reaching ahead, the wings "
                 "swept back (drawn standing on the ground line: the game lifts it)."),
    "q_bite": ("spell@1250", 35, "落地猛咬：前爪落地，头低低地往前伸，嘴张到最大咬下去",
               "BITE - landing on the front claws, the head low and thrust forward, the jaw open as wide as it goes, "
               "biting down."),
    "e_spread": ("celebration@500", 35, "技能2「龙威咆哮」起手：前身抬起，两只翅膀往上张开",
                 "SPREAD - the front of the body rising, both wings opening upwards."),
    "e_roar": ("celebration@1250", 35, "咆哮：头仰起来、嘴张到最大朝天咆哮，翅膀高高张开",
               "ROAR - the head thrown up, the jaw wide open roaring at the sky, the wings spread high."),
    "r_rear": ("spell@500", 35, "大招「地震」抬身：后腿撑地、前身高高立起，前爪离地，翅膀往上扬（三踏每一踏都从这里开始）",
               "REAR UP - on the hind legs, the front of the body raised high, the front claws off the ground, the "
               "wings up (every one of the three stomps starts here)."),
    "r_stomp": ("spell@1125", 35, "重踏：前爪重重踏在地上，身子往下一沉，头低下，翅膀往下压",
                "STOMP - the front claws slammed down hard on the ground, the body sinking, the head low, the wings "
                "pushed down."),
    "r_roar": ("spell@1625", 35, "地震结束：蹲伏着张大嘴咆哮，翅膀收拢一半（之后岩甲发光）",
               "QUAKE ROAR - crouched, the jaw wide open roaring, the wings half folded (her rock armour glows "
               "after it)."),
    "run1": ("run@0", 35, "移动（贴地低飞）1：翅膀高高往上扬，身子保持待机的 3/4 朝右，四条腿收在身下",
             "FLY 1 - the wings raised high, the body as in the idle (3/4 facing right), the four legs tucked under "
             "her."),
    "run2": ("run@146", 35, "飞 2：翅膀在最高处", "FLY 2 - the wings at the top of the beat."),
    "run3": ("run@292", 35, "飞 3：翅膀往两边平平展开", "FLY 3 - the wings spread out level."),
    "run4": ("run@438", 35, "飞 4：翅膀往下扇", "FLY 4 - the wings beating down."),
    "run5": ("run@584", 35, "飞 5：翅膀扇到最低", "FLY 5 - the wings at the bottom of the beat."),
    "run6": ("run@876", 35, "飞 6：翅膀收回往上抬（6 接回 1，循环就是扇翅膀）",
             "FLY 6 - the wings coming back up (6 runs on into 1: the beat loops)."),
    "d_fall": ("death@1000", 35, "被打倒：身子往一边歪倒砸向地面，一只翅膀翘起",
               "FALLING - the body crashing over to one side onto the ground, one wing sticking up."),
    "d_down": ("death@7500", 35, "倒地：趴在地上，头垂在地面，翅膀瘫在背上（金铲铲原样）",
               "DOWN - lying flat on the ground, the head resting on the ground, the wings slumped on her back "
               "(as in TFT)."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_kobuko_picture's renders (mirrored: facing image right)."""

    def __init__(self, lol):
        self.m = Model(lol)
        self.names = {j["name"]: i for i, j in enumerate(self.m.joints)}
        self.tris = self.m.tris

    def pose(self, clip):
        name, ms = clip.split("@")
        anim = pose_ref.read_anim(self.m.w.read(CLIPS[name]))
        local = pose_ref.local_pose(self.m.joints, anim, float(ms) / 1000.0)
        if clip in HOVER_POSES:   # her body as in the design (TFT's flight turns her to face the camera, nose down)
            idle = pose_ref.local_pose(self.m.joints, pose_ref.read_anim(self.m.w.read(CLIPS["idle"])), 0.0)
            for n in BODY_JOINTS:   # the whole local transform: TFT's flight also moves the spine joints
                i = self.names[n]
                local[i] = idle[i]
        local = pose_ref.chibi(self.m.joints, local, HEAD_SCALE)
        # the wings shrunk in the poses that spread them (WING_POSES: spread, her wings span three bodies)
        shrink = {}
        if clip in WING_POSES:
            shrink.update({"L_Wing_Upper": WING_SCALE, "R_Wing_Upper": WING_SCALE})
        for n, k in shrink.items():
            i = self.names[n]
            t, r, sc = local[i]
            local[i] = (t, r, sc * k)
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
    ap.add_argument("--out", default=r"C:\t\te_work\terra_pose_pack")
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
        if clip in WING_LINES:
            nl, na, fl, fa = WING_LINES[clip]
            for side, length, ang, sign in (("R", nl, na, -1), ("L", fl, fa, 1)):
                root = jxy[poser.names[f"{side}_Wing1"]].copy()
                step = np.array([sign * np.cos(np.radians(ang)), -np.sin(np.radians(ang))]) * length * PX
                jxy[poser.names[f"{side}_Wing2"]] = root + step * 0.45
                jxy[poser.names[f"{side}_Wing3"]] = root + step
            joint_of = np.array(poser.m.infl)[poser.m.v["bones"].astype(np.int64)]
            main_j = joint_of[np.arange(len(poser.m.v)), np.argmax(poser.m.v["w"], axis=1)]
            wing = np.isin(main_j, [poser.names[n] for n in WING_JOINTS])
            tris = tris[~wing[tris].any(axis=1)]
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
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
