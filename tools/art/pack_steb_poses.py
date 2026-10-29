#!/usr/bin/env python3
"""Steb's pose pack for Codex (assets/source/steb/POSE_PROMPTS.md): the whole-body poses of his actions, each on a
skeleton projected from his OWN clips (his model and clips are in the Riot client's TFTSet13.wad.client, so his
skeletons are his animator's - Sevika's way).

    python tools/art/pack_steb_poses.py [--out C:/t/sb_work/steb_pose_pack] [--lol "D:/Riot Games/League of Legends"]

Every pose is one frame of one of his clips (pack_steb_picture.CLIPS), the head grown to the design's (pose_ref.chibi,
HEAD_SCALE). Seen from the design's angle (3/4 facing right, yaw 35) unless a pose gives its own: TFT's combat clips
turn him side-on to the target, so a frame that showed his back is seen from a yaw that shows his front. One scale for
all: the design pose's body height (idle@0, the idle step 0's A was drawn from: quiff to soles, the batons and the
backpack left out) = the design's 106 body rows (hd/idle.png: A-1, PPU 2.6, 1:1) at PX px a square; the lowest point
of every pose on y SOLE_Y, his pelvis on the design pose's pelvis column.
The run is its own pack (pack_steb_run.py: the whole cycle, the toe squares, the near and far legs' colours).
The batons: the skeleton draws each as a PURPLE bar between its two ends (the farthest-apart vertices of that baton,
the Weapon submesh's vertices weighted to L_Weapon / R_Weapon), a GOLD dot on its brass head (the end whose texture is
yellower); the backpack's outline in BROWN (the hull of the Backpack submesh).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design.png (the design at PX px a square on the canvas, its own
skeleton over it in 0_design_skeleton.png); 1_head.png (the design's head 8x: every pose wears it); per pose
<k>_<name>_ref.png (his model in that frame, textured, on the same canvas and grid) and <k>_<name>_skeleton.png (its
bones on the grid).
Skeleton colours: green = the spine (pelvis to the base of the neck), ORANGE = his R_ arm, CYAN = his L_ arm, RED = left
leg, BLUE = right leg, PURPLE = the batons (GOLD dot = the brass head), BROWN = the backpack, grey box = the head.
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
from design_steb_hd import lp  # noqa: E402
from pack_steb_picture import Model, CLIPS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "steb")
PX, CANVAS, SOLE_Y = 9, 1254, 1176
ROWS = 106                    # hd/idle.png's body rows (quiff to soles: rows 0-105)
HEAD_SCALE = 2.2              # the chibi head 30 rows tall, the design's 31 (C:/t/sb_work/headscale.py)
DESIGN = "idle@0"             # the idle step 0's A was drawn from
YAW = 35
MARGIN = 60
HEAD_BOX = (35, 0, 64, 31)      # the design's head with the quiff and the fin ears (hd/idle.png)
PELVIS_COL = 51                 # the design's pelvis column: between its legs (cols 36-50 and 52-64 at row 75)
PITCH = 12
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "R_arm": (255, 140, 0), "L_arm": (0, 175, 210), "L_leg": (230, 30, 30),
       "R_leg": (40, 90, 230), "baton": (120, 40, 170), "head": (230, 175, 20), "pack": (130, 75, 30)}
CHAINS = {"spine": ["Pelvis", "Spine1", "Chest", "Neck"],
          "L_arm": ["L_Shoulder", "L_Elbow", "L_Hand", "L_Middle1"],
          "R_arm": ["R_Shoulder", "R_Elbow", "R_Hand", "R_Middle1"],
          "L_leg": ["L_Hip", "L_KneeLower", "L_Foot", "L_Toe"], "R_leg": ["R_Hip", "R_KneeLower", "R_Foot", "R_Toe"]}
HEAD_JOINTS = ("Head", "Eye", "Brow", "Jaw", "Lip", "MouthCrnr", "Teeth")

RUN_MS = [0, 200, 350, 500, 650, 800, 950, 1100]   # the run's frames (ms): pack_steb_run.py draws them
# name -> (clip@ms, yaw, what it is for (Chinese), the pose line (English))
POSES = {
    "a_wind": ("attack2@296", -36, "普攻（双警棍连击）第一下 1：近处的手把警棍高高举到右上方，蓄力",
               "BATON WIND-UP - the near hand raising its baton high to the upper right, loading the blow."),
    "a_hit": ("attack2@445", 35, "第一下 2：弓步往前，警棍狠狠往右前下方劈下去（技能1的重击也用这一帧）",
              "BATON STRIKE - lunging forward, the baton slammed down to the front-right."),
    "a2_wind": ("attack1@0", 35, "第二下 1：换另一根警棍，两臂张开，身体往后一拧蓄力",
                "SECOND BATON WIND-UP - the other baton now, both arms spread, the body twisted back to load."),
    "a2_hit": ("attack1@326", 35, "第二下 2：另一根警棍横着扫出去，打向右前方",
               "SECOND BATON SWEEP - the other baton swept across to the front-right."),
    "q_dose": ("spell@983", 35, "技能1 战地医疗 1：两脚分开站稳，把警棍发光的黄铜头按在自己胸口，给自己打一针（绿光之后单独画，不画）",
               "FIELD MEDICINE - feet planted apart, pressing a baton's glowing brass head to his own chest: a "
               "dose of medicine (the green glow comes later: do NOT draw it)."),
    "q_raise": ("attack2@593", 35, "技能1 2：压低身子，把警棍竖着高高举起，准备砸下去",
                "STRIKE RAISE - crouched low, a baton raised straight up, about to smash down."),
    "e_raise": ("spell@590", 35, "技能2 通缉令 1：站直，两根警棍竖着举在身体两侧——发通缉！",
                "WANTED CALL - standing tall, both batons held upright at his sides: a call to his squad."),
    "e_point": ("attack2@741", 35, "通缉令 2：压低身子，两根警棍平举对准右前方的目标（标记之后单独画，不画）",
                "WANTED AIM - crouched, both batons held level and aimed at the target to the front-right (the "
                "mark comes later: do NOT draw it)."),
    "r_cross": ("dance@0", 35, "大招 医疗背包 1：两根警棍在头顶交叉，召集队友",
                "MEDIC'S PACK RALLY - both batons crossed high over his head, rallying his squad."),
    "r_squat": ("dance@275", 35, "大招 2：两腿分开稳稳地蹲下，双手撑在膝上，背后的大背包朝上（背包打开的光之后单独画，不画）",
                "MEDIC'S PACK BRACE - a wide, steady squat, hands on his knees, the big backpack on his back "
                "facing up (the light of the opened pack comes later: do NOT draw it)."),
    "d_fall": ("death@380", 35, "被击倒：跪倒在地、身体往后仰，警棍脱手",
               "KNOCKED DOWN - dropped to his knees, the body thrown back, the batons slipping from his hands."),
    "d_down": ("death@1100", 35, "倒地：趴在地上（金铲铲原样），背包在背上，警棍落在身边",
               "DOWN - lying face down on the ground (as in the game), the backpack on his back, the batons "
               "beside him."),
}


class Poser:
    """His mesh (head grown) and joints, projected as pack_steb_picture's renders (mirrored: facing image right)."""

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


def main_joint(m):
    """Each vertex's main joint (its largest weight)."""
    joint_of = np.array(m.infl)[m.v["bones"].astype(np.int64)]
    return joint_of[np.arange(len(m.v)), np.argmax(m.v["w"], axis=1)]


def vertices_of(poser, keys):
    """The vertices mostly weighted to the joints whose names hold one of `keys`."""
    m = poser.m
    sel = {i for i, j in enumerate(m.joints) if any(k in j["name"] for k in keys)}
    return np.isin(main_joint(m), list(sel))


def part_vertices(poser, part):
    """A submesh's vertices ("body", "pack", "weapon")."""
    sel = np.zeros(len(poser.m.v), bool)
    sel[np.unique(poser.m.parts[part][0])] = True
    return sel


def batons(poser):
    """Each baton's vertices (the Weapon submesh, by the weapon joint it hangs on) and a yellowness per vertex (its
    texel in the weapon map: the brass head is the yellow end)."""
    m = poser.m
    weapon = part_vertices(poser, "weapon")
    tex = np.asarray(m.tri_tex[1][2].convert("RGB")).astype(float)
    h, w = tex.shape[:2]
    uv = m.v["uv"]
    px = tex[np.clip((uv[:, 1] * h).astype(int), 0, h - 1), np.clip((uv[:, 0] * w).astype(int), 0, w - 1)]
    yellow = (px[:, 0] + px[:, 1]) / 2 - px[:, 2]
    out = []
    for side in ("L_Weapon", "R_Weapon"):
        sel = weapon & vertices_of(poser, (side,))
        if sel.sum() > 10:
            out.append((sel, yellow))
    return out


def baton_line(xy, sel, yellow):
    """A baton's two ends on the canvas (its points farthest apart along its main axis), the brass head first."""
    p = xy[sel]
    c = p.mean(0)
    _, _, vt = np.linalg.svd(p - c, full_matrices=False)
    t = (p - c) @ vt[0]
    a, b = p[np.argmin(t)], p[np.argmax(t)]
    k = max(3, len(t) // 8)
    ya = yellow[sel][np.argsort(t)[:k]].mean()
    yb = yellow[sel][np.argsort(t)[-k:]].mean()
    return (tuple(a), tuple(b)) if ya >= yb else (tuple(b), tuple(a))


def hull(points):
    """The convex hull of 2D points (monotone chain)."""
    pts = sorted(set(map(tuple, np.round(points, 1))))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def grid(d):
    for k in range(0, CANVAS, PX):
        d.line([(k, 0), (k, CANVAS)], fill=(212, 212, 212))
        d.line([(0, k), (CANVAS, k)], fill=(212, 212, 212))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40), width=2)


def skeleton(poser, xy_j, z, hbox, out, sticks, pack, base=None):
    can = Image.new("RGB", (CANVAS, CANVAS), GREY)
    d = ImageDraw.Draw(can)
    grid(d)
    if base is not None:   # the design under its own skeleton, faded
        can = Image.blend(can, base.convert("RGB"), 0.55)
        d = ImageDraw.Draw(can)
    if len(pack) >= 3:
        d.polygon(pack, outline=COL["pack"], width=5)
    d.rectangle(hbox, outline=(110, 110, 110), width=3)
    order = sorted(CHAINS, key=lambda c: -np.mean([z[poser.names[n]] for n in CHAINS[c]]))   # far chains first
    for c in order:
        pts = [tuple(xy_j[poser.names[n]]) for n in CHAINS[c]]
        d.line(pts, fill=COL[c], width=6, joint="curve")
        for p in pts[:-1]:
            d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=COL[c])
        if c.endswith("arm"):
            p = pts[2]
            d.ellipse([p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10], fill=COL[c])
    for brass, rod in sticks:
        d.line([brass, rod], fill=COL["baton"], width=8)
        d.ellipse([brass[0] - 11, brass[1] - 11, brass[0] + 11, brass[1] + 11], fill=COL["head"])
    can.save(lp(out))


def near_arm(z, poser):
    """Which arm is nearer the camera (the larger z is nearer: render_hq draws the largest z on top)."""
    zl = np.mean([z[poser.names[n]] for n in CHAINS["L_arm"]])
    zr = np.mean([z[poser.names[n]] for n in CHAINS["R_arm"]])
    return "CYAN (the L_ arm)" if zl > zr else "ORANGE (the R_ arm)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"C:\t\sb_work\steb_pose_pack")
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    if os.path.isdir(lp(a.out)):   # no files left from an earlier pack
        shutil.rmtree(lp(a.out))
    os.makedirs(lp(a.out))
    poser = Poser(a.lol)
    hv = vertices_of(poser, HEAD_JOINTS) & part_vertices(poser, "body")
    body = part_vertices(poser, "body")
    packv = part_vertices(poser, "pack")
    sticks_v = batons(poser)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    assert design.height == ROWS, design.size   # his quiff starts on row 0

    # one scale for every pose: the design pose's body height (batons and pack left out) = the design's body rows
    iv, _ = poser.pose(DESIGN)
    pxy, _ = Poser.project(iv, YAW, 1.0, 0.0, 0.0)
    scale = ROWS * PX / (pxy[body, 1].max() - pxy[body, 1].min())
    pel = poser.names["Pelvis"]
    # the design on the canvas: its soles on SOLE_Y, centred; the design pose's pelvis lands on the same column
    dx = (CANVAS - design.width * PX) // 2 // PX * PX
    dy = SOLE_Y - design.height * PX
    pelvis_x = dx + PELVIS_COL * PX + PX // 2
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    can.alpha_composite(design.resize((design.width * PX, design.height * PX), Image.NEAREST), (dx, dy))
    can.convert("RGB").save(lp(os.path.join(a.out, "0_design.png")))
    head = design.crop(HEAD_BOX)
    Image.alpha_composite(Image.new("RGBA", head.size, GREY + (255,)), head).convert("RGB").resize(
        (head.width * 8, head.height * 8), Image.NEAREST).save(lp(os.path.join(a.out, "1_head.png")))

    for k, (name, (clip, yaw, _zh, _en)) in enumerate([("idle", (DESIGN, YAW, "", ""))] + list(POSES.items())):
        verts, joints = poser.pose(clip)
        xy, z = Poser.project(verts, yaw, scale, 0.0, 0.0)
        ground = SOLE_Y - xy[:, 1].max()
        jxy, jz = Poser.project(joints, yaw, scale, 0.0, 0.0)
        shift = pelvis_x - jxy[pel, 0]
        # a pose that would leave the canvas moved back inside, MARGIN from the edge (his body; a baton may run off)
        lo, hi = xy[body, 0].min() + shift, xy[body, 0].max() + shift
        shift += max(0, MARGIN - lo) - max(0, hi - (CANVAS - MARGIN))
        xy[:, 0] += shift
        xy[:, 1] += ground
        jxy[:, 0] += shift
        jxy[:, 1] += ground
        hx, hy = xy[hv, 0], xy[hv, 1]
        hbox = (hx.min(), hy.min(), hx.max(), hy.max())
        stem = "0_design" if name == "idle" else f"{k + 1}_{name}"
        sticks = [baton_line(xy, sel, yellow) for sel, yellow in sticks_v]
        pack = hull(xy[packv])
        skeleton(poser, jxy, jz, hbox, os.path.join(a.out, f"{stem}_skeleton.png"), sticks, pack,
                 can if name == "idle" else None)
        if name == "idle":
            continue
        im = pose_ref.render_hq(verts.copy(), poser.tris, poser.m.v["uv"], poser.m.tex, -yaw, PITCH, (CANVAS, CANVAS),
                                scale, ground, shift=-shift / CANVAS - 0.5,
                                tri_tex=poser.m.tri_tex).transpose(Image.FLIP_LEFT_RIGHT)
        ref = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
        d = ImageDraw.Draw(ref)
        grid(d)
        ref.alpha_composite(im)
        ref.convert("RGB").save(lp(os.path.join(a.out, f"{stem}_ref.png")))
        top = min(xy[:, 1].min(), hbox[1])
        print(stem, clip, "yaw", yaw, "near arm", near_arm(jz, poser), f"top {top:.0f}")
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), lp(os.path.join(a.out, "POSE_PROMPTS.md")))
    zp = shutil.make_archive(a.out, "zip", a.out)
    print("written", zp)


if __name__ == "__main__":
    main()
