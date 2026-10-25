#!/usr/bin/env python3
"""Skarner's pose pack for Codex (assets/source/skarner/POSE_PROMPTS.md): the whole-body poses his League clips go
through (the user, 2026-10-26: 「Codex 照骨架画」 - pack_trundle_poses.py's way, for a scorpion's body).

    python tools/art/pack_skarner_poses.py [--out C:/t/sk_work/skarner_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (step 0's A as drawn, 80 x
59) sits at squares (DX, DY) on it. The skeletons are set by hand after League's frames (POSES; League's own 2D joints,
tools/lol/skarner_joints.py, foreshorten too much to retarget - Impale's body pitches toward the camera): every chain is
a polyline measured on hd/idle.png (REST, design squares) cut into as many bones as League's chain has (in the ratio of
League's idle bones), and in a pose every bone keeps its design length (Quinn's lesson: Codex keeps no length unless given
one): the body turns about the tail root and sinks or rises on its legs, each tail is an arc of its own bones, the claws
turn from their rest bones, the feet stay planted or step (the knees solved). The design's face already hangs on the
ground line, so the body never sinks it lower, and a claw that would dig into the ground turns up until it rests on it.
Chains: the body (green: the tail root to the face), the three tails (cyan / light blue / steel blue, each ending in its
stinger - a filled wedge), the two claws (ORANGE = the near claw, image left of the face; PURPLE = the far claw), six legs
(RED = the near three, BLUE = the far three), the grey box = the head (the silver hood and the bone face, never redrawn),
the grey-green ellipse = the boulder (only in the poses holding it).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md (assets/source/skarner/POSE_PROMPTS.md); 0_design_skeleton.png (the
design on the grid with its own skeleton); 1_head.png (the design's head, 8x: every pose wears it); 2_design.png and
2b_rock.png (the designs on the grid: the idle, the boulder held); per pose <k>_<name>_skeleton.png and
<k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local). --check DIR: each skeleton beside League's
frame and the design's own skeleton over the design (nothing else written).
"""
import argparse
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
from design_skarner_hd import lp  # noqa: E402
import skarner_joints as SJ  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "skarner")
PX, CANVAS, SOLE_Y = 9, 1254, 1188
GREY = (225, 225, 225)
GROUND = 59                         # the design's soles' bottom edge (rows)
DX, DY = 29, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 132)
IDLE = "Idlebase@0"
HEAD = (40, 33, 64, 59)             # x0, y0, x1, y1 of the silver hood and the face in hd/idle.png (ends exclusive)
STINGER = 9.0                       # a stinger's length beyond its tail's last joint (squares, the design's)
ROCK = (56, 24)                     # the boulder's width and height (squares: rock.png's 61 x 56 box, the tails over it)
B_SCALE = 9.7 / 8.7                 # rock.png's squares in idle.png's (Codex drew B on 9.7 px, A on 8.7)

# League chain -> (the joints it is drawn through, its colour, the design's polyline in hd/idle.png squares)
CHAINS = {
    "body": (["Hip", "Torso_A", "Head"], (0, 170, 60), [(22, 34), (38, 40), (53, 47)]),
    "tail_r": (SJ.CHAINS["tail_r"], (0, 200, 220), [(21, 34), (13, 33), (7, 27), (6, 20), (9, 14), (15, 11), (20, 14)]),
    "tail_c": (SJ.CHAINS["tail_c"], (110, 225, 255), [(24, 33), (19, 27), (18, 20), (22, 13), (28, 7), (31, 5), (34, 8)]),
    "tail_l": (SJ.CHAINS["tail_l"], (40, 110, 200), [(28, 33), (33, 30), (33, 22), (36, 16), (42, 12), (46, 11), (50, 14)]),
    "claw_r": (["R_Claw_A", "R_Claw_B", "R_Claw_C", "R_Pincer"], (255, 140, 0), [(40, 41), (36, 45), (38, 50), (45, 57)]),
    "claw_l": (["L_Claw_A", "L_Claw_B", "L_Claw_C", "L_Pincer"], (150, 60, 200), [(60, 41), (65, 38), (70, 41), (78, 51)]),
    "leg_rb": (["R_LegBack_A", "R_LegBack_C", "R_LegBack_F"], (230, 30, 30), [(20, 42), (8, 46), (3, 57)]),
    "leg_rm": (["R_LegMid_A", "R_LegMid_C", "R_LegMid_F"], (230, 30, 30), [(26, 45), (19, 50), (17, 58)]),
    "leg_rf": (["R_LegFront_A", "R_LegFront_C", "R_LegFront_D"], (230, 30, 30), [(32, 46), (30, 52), (33, 58)]),
    "leg_lb": (["L_LegBack_A", "L_LegBack_C", "L_LegBack_F"], (40, 90, 230), [(38, 45), (42, 51), (45, 58)]),
    "leg_lf": (["L_LegFront_A", "L_LegFront_C", "L_LegFront_D"], (40, 90, 230), [(48, 47), (50, 52), (52, 58)]),
    "leg_lm": (["L_LegMid_A", "L_LegMid_C", "L_LegMid_F"], (40, 90, 230), [(58, 46), (64, 51), (66, 58)]),
}
TAILS = ("tail_r", "tail_c", "tail_l")
LEGS = tuple(k for k in CHAINS if k.startswith("leg_"))
# drawn far first: the far legs and claw, the body, the tails, the near legs and claw last
ORDER = ("leg_lb", "leg_lf", "leg_lm", "claw_l", "body", "tail_l", "tail_c", "tail_r", "leg_rb", "leg_rm", "leg_rf",
         "claw_r")

# name -> (League's frame, what it is for (Chinese), the pose line (English), the skeleton). The skeleton is set by hand
# after League's frame (the frames' own 2D joints foreshorten too much to retarget: Impale's body pitches toward the
# camera): "tilt" (degrees the body turns about the tail root, + = the front up), "dy" (squares the body sinks on its
# planted legs, - = rises), "lift" (squares the whole figure is off the ground), each tail (a0, turn): its first bone's
# direction and the turn from bone to bone (degrees, 0 = image right, 90 = down, -90 = up; every bone at the design's
# length), each claw (three turns from its rest bones, degrees), each foot (dx, dy) from where it stands (squares; the
# knee solved), "rock" the boulder's centre (design squares, or "tips": held on the stingers). Missing = as designed.
GAIT_A, GAIT_B = ("leg_rb", "leg_rf", "leg_lm"), ("leg_rm", "leg_lb", "leg_lf")


def feet(group, dx, dy=0.0):
    return {g: (dx, dy) for g in group}


POSES = {
    "a_wind": ("BaseAttack1@250", "普攻起手：前半身抬起、身子往后坐，三根尾巴往后上方高高扬起蓄力，两只钳子张开",
               "WIND-UP - rearing back, the front of his body lifted, the THREE TAILS raised high up and back, ready to strike, both claws spread open.",
               dict(tilt=12, dy=-1, tails={"tail_r": (-150, 14), "tail_c": (-125, 14), "tail_l": (-100, 14)},
                    claws={"claw_r": (-40, -30, -20), "claw_l": (-30, -25, -20)})),
    "a_strike": ("BaseAttack1@420", "普攻扎下：身子往前压低，三根尾巴从头顶往前下方扎下去（毒刺在身前右边），钳子往前夹",
                 "STRIKE - lunging forward and low, the THREE TAILS whipping over his head and stabbing down in front of him (the stingers on the image right), the claws snapping forward.",
                 dict(tilt=-6, dy=2, tails={"tail_r": (-115, 34), "tail_c": (-100, 33), "tail_l": (-85, 32)},
                      claws={"claw_r": (-20, -10, 0), "claw_l": (10, 10, 10)})),
    "q_dig": ("Spell1_Pickup_v2@250", "掘石：身子压到最低，三根尾巴从背上往前弯下去插进地里，抓住身前地上的大巨石（巨石在身前地上）",
              "DIG - pressing his body down low, the THREE TAILS bending over his back and plunging down in front of him, their stingers gripping the BOULDER lying on the ground before him.",
              dict(tilt=-8, dy=3, tails={"tail_r": (-65, 22), "tail_c": (-60, 22), "tail_l": (-55, 22)},
                   claws={"claw_r": (20, 20, 10), "claw_l": (20, 20, 10)}, rock=(66, 47))),
    "q_lift": ("Spell1_Pickup_v2@500", "举石：三根尾巴把巨石从地里拔起来、举到背上头顶，身子往上挺",
               "LIFT - the THREE TAILS tearing the BOULDER up out of the ground and swinging it up over his back, his body rising.",
               dict(tilt=6, dy=-1, tails={"tail_r": (-130, 30), "tail_c": (-115, 30), "tail_l": (-100, 30)},
                    claws={"claw_r": (-15, -10, 0), "claw_l": (-15, -10, 0)}, rock="tips")),
    "t_wind": ("Spell1_Toss_to_Idle@250", "扔石起手：三根尾巴把巨石往后上方高高举起，身子往后仰，准备扔",
               "TOSS WIND-UP - the THREE TAILS lifting the BOULDER high up and back over him, his body leaning back, about to throw.",
               dict(tilt=10, dy=0, tails={"tail_r": (-140, 10), "tail_c": (-125, 10), "tail_l": (-110, 10)},
                    claws={"claw_r": (-25, -20, -10), "claw_l": (-25, -20, -10)}, rock="tips")),
    "t_throw": ("Spell1_Toss_to_Idle@375", "扔出巨石：三根尾巴猛地往前甩直（毒刺朝身前右边），巨石已经扔出去了（不画巨石），身子往前冲",
                "THROW - the THREE TAILS snapping forward straight out in front of him (the stingers to the image right), the boulder already thrown (no boulder), his body thrusting forward.",
                dict(tilt=-4, dy=1, tails={"tail_r": (-70, 12), "tail_c": (-55, 11), "tail_l": (-40, 10)})),
    "w_rear": ("Spell2@61", "震地起跳：整个身子往上蹦起来（六条腿离地），尾巴蜷在背上，钳子往上张开",
               "QUAKE LEAP - his whole body bouncing up off the ground (all six legs off the ground), the tails curled over his back, the claws raised wide open.",
               dict(tilt=8, lift=6, claws={"claw_r": (-50, -30, -20), "claw_l": (-40, -30, -20)},
                    feet=feet(GAIT_A + GAIT_B, 0, -2))),
    "w_slam": ("Spell2@244", "砸地：身子重重砸回地面、压得很低，六条腿往外撑开，钳子砸在地上（震地壁垒的地震）",
               "SLAM - crashing back down on the ground, pressed very low, all six legs braced out wide, the claws slamming down on the ground (the earthquake).",
               dict(tilt=-4, dy=4, claws={"claw_r": (25, 20, 10), "claw_l": (30, 25, 15)},
                    feet={"leg_rb": (-3, 0), "leg_rm": (-2, 0), "leg_rf": (1, 0), "leg_lb": (-1, 0), "leg_lf": (2, 0),
                          "leg_lm": (3, 0)})),
    "e_charge": ("Spell3_Startup@167", "冲锋：身子压低往前冲，头和钳子在最前面，尾巴往后上方拖着（以绪塔尔冲击）",
                 "CHARGE - his body low, rushing forward head first, the claws pushed out in front, the tails streaming up and back behind him.",
                 dict(tilt=-5, dy=2, tails={"tail_r": (-165, 8), "tail_c": (-150, 8), "tail_l": (-135, 8)},
                      claws={"claw_r": (-40, -30, -20), "claw_l": (-30, -25, -20)},
                      feet=dict(**feet(GAIT_A, 3), **feet(GAIT_B, -3)))),
    "e_grab": ("Spell3_Grab@375", "夹住拖走：两只钳子在身前夹紧（夹着一个敌人，不画敌人），身子低着往前推，尾巴竖起来",
               "GRAB - both claws clamped together in front of him (holding an enemy - do NOT draw the enemy), his body low pushing forward, the tails raised up.",
               dict(tilt=-3, dy=2, tails={"tail_r": (-115, 8), "tail_c": (-100, 8), "tail_l": (-85, 8)},
                    claws={"claw_r": (-55, -20, -30), "claw_l": (5, -5, -25)})),
    "r_lash": ("Spell4_Hit1@100", "毒刺贯体：三根尾巴从背上往前上方一起甩出去、伸得很长（毒刺在身前右边最远处），身子往前探",
               "IMPALE - the THREE TAILS lashing forward together over his back, stretched far out in front (the stingers far out on the image right), his body leaning forward.",
               dict(tilt=-6, dy=1, tails={"tail_r": (-100, 18), "tail_c": (-90, 17), "tail_l": (-80, 16)},
                    claws={"claw_r": (-20, -10, 0), "claw_l": (-10, -10, 0)})),
    "r_hold": ("Spell4_channel@500", "压制拖行：三根尾巴从高处往前弯下来（扎住敌人，不画敌人），身子低着站稳",
               "HOLD - the THREE TAILS arched high and bending down in front of him (impaling the enemies - do NOT draw them), his body low and braced.",
               dict(tilt=-3, dy=2, tails={"tail_r": (-100, 26), "tail_c": (-90, 25), "tail_l": (-80, 24)})),
    "run1": ("Runbase@0", "跑 1：六条腿交替迈步（照骨架），身子平着往前，尾巴竖在背上",
             "RUN 1 - scuttling forward, the six legs stepping as the skeleton shows, the body level, the tails up over his back.",
             dict(feet=dict(**feet(GAIT_A, 3), **feet(GAIT_B, -3)))),
    "run2": ("Runbase@417", "跑 2：一组腿抬起往前（照骨架），身子高一格",
             "RUN 2 - one set of legs lifted swinging forward, as the skeleton shows, the body a square higher.",
             dict(dy=-1, feet=feet(GAIT_A, 0, -3))),
    "run3": ("Runbase@833", "跑 3：照骨架换另一组腿往前迈", "RUN 3 - the other legs reaching forward, as the skeleton shows.",
             dict(feet=dict(**feet(GAIT_A, -3), **feet(GAIT_B, 3)))),
    "run4": ("Runbase@1250", "跑 4：另一组腿抬起往前（照骨架），身子高一格",
             "RUN 4 - the other set of legs lifted swinging forward, as the skeleton shows, the body a square higher.",
             dict(dy=-1, feet=feet(GAIT_B, 0, -3))),
    "d_rear": ("Death@512", "被打倒：身子往上一挺、尾巴往上僵直，腿发软（死亡第一下）",
               "STRUCK DOWN - his body jerking up, the tails stiff straight up, the legs buckling.",
               dict(tilt=14, dy=1, tails={"tail_r": (-110, 2), "tail_c": (-95, 2), "tail_l": (-80, 2)},
                    claws={"claw_r": (-30, -20, -10), "claw_l": (-30, -20, -10)})),
    "d_down": ("Death@1025", "倒地：整个身子趴平在地上，六条腿瘫开，三根尾巴软软地平摊在身后地上（死亡：倒地）",
               "DEAD - lying flat on the ground, the six legs sprawled out, the three tails limp along the ground behind him.",
               dict(tilt=12, dy=8, tails={"tail_r": (174, 2), "tail_c": (170, 2), "tail_l": (166, 2)},
                    claws={"claw_r": (20, 20, 20), "claw_l": (30, 30, 20)},
                    feet={"leg_rb": (-5, 0), "leg_rm": (-3, 0), "leg_rf": (2, 0), "leg_lb": (-2, 0), "leg_lf": (3, 0),
                          "leg_lm": (5, 0)})),
}


def resample(poly, ratios):
    """`poly` cut into len(ratios) bones at the ratios' share of its length (the joints, len(ratios) + 1 points)."""
    pts = np.asarray(poly, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    want = np.concatenate([[0.0], np.cumsum(ratios)]) / sum(ratios) * cum[-1]
    out = []
    for s in want:
        i = min(int(np.searchsorted(cum, s, side="right")) - 1, len(seg) - 1)
        t = (s - cum[i]) / seg[i] if seg[i] else 0.0
        out.append(tuple(pts[i] + t * (pts[i + 1] - pts[i])))
    return out


def ang(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


class Rig:
    def __init__(self, lol):
        self.sk = SJ.Skarner(lol)
        self.idle = self.sk.frame(IDLE)
        hip, head = self.idle["Hip"], self.idle["Head"]
        d_hip, d_head = CHAINS["body"][2][0], CHAINS["body"][2][-1]
        self.k = math.dist(d_hip, d_head) / math.dist(hip[:2], head[:2])   # design squares per League unit
        self.rest = {}
        for name, (joints, _, poly) in CHAINS.items():
            L = [self.idle[j][:2] for j in joints]
            ratios = [max(math.dist(L[i], L[i + 1]), 1e-3) for i in range(len(L) - 1)]
            self.rest[name] = resample(poly, ratios)

    def pose(self, sk):
        """{chain: [points in design squares]}, the head box's offset, the boulder's centre (or None)."""
        tilt, dy, lift = sk.get("tilt", 0.0), sk.get("dy", 0.0), sk.get("lift", 0.0)
        hip = self.rest["body"][0]
        t = math.radians(-tilt)

        def turned(p):
            x, y = p[0] - hip[0], p[1] - hip[1]
            return (hip[0] + x * math.cos(t) - y * math.sin(t), hip[1] + x * math.sin(t) + y * math.cos(t))

        # the face hangs on the ground line in the design: the body never sinks it into the ground
        face = self.rest["body"][-1]
        dy = min(dy, GROUND - (turned(face)[1] + HEAD[3] - face[1]))

        def body(p):   # turned about the tail root, sunk by dy
            x, y = turned(p)
            return (x, y + dy)

        out = {"body": [body(p) for p in self.rest["body"]]}
        for name in TAILS:
            rest = self.rest[name]
            spec = sk.get("tails", {}).get(name)
            if spec is None:
                out[name] = [body(p) for p in rest]
                continue
            a0, turn = spec
            pts = [body(rest[0])]
            for i in range(len(rest) - 1):
                L, a = math.dist(rest[i], rest[i + 1]), math.radians(a0 + turn * i)
                pts.append((pts[-1][0] + L * math.cos(a), pts[-1][1] + L * math.sin(a)))
            out[name] = pts
        for name in ("claw_r", "claw_l"):
            rest = self.rest[name]
            turns = sk.get("claws", {}).get(name, (0, 0, 0))
            for up in range(0, 120, 5):   # a claw that would dig into the ground turns up until it rests on it
                pts = [body(rest[0])]
                for i in range(len(rest) - 1):
                    L = math.dist(rest[i], rest[i + 1])
                    a = ang(rest[i], rest[i + 1]) + t + math.radians(turns[i] - up)
                    pts.append((pts[-1][0] + L * math.cos(a), pts[-1][1] + L * math.sin(a)))
                if max(p[1] for p in pts) <= GROUND + 0.5:
                    break
            out[name] = pts
        for name in LEGS:
            h, kn, ft = self.rest[name]
            fx, fy = sk.get("feet", {}).get(name, (0.0, 0.0))
            hp, foot = body(h), (ft[0] + fx, ft[1] + fy)
            out[name] = [hp, knee(hp, foot, math.dist(h, kn), math.dist(kn, ft), side(h, kn, ft)), foot]
        if lift:
            out = {c: [(x, y - lift) for x, y in pts] for c, pts in out.items()}
        hx, hy = out["body"][-1]
        head = (hx - self.rest["body"][-1][0], hy - self.rest["body"][-1][1])
        rock = sk.get("rock")
        if rock == "tips":   # held up on the stingers: its centre under their mean, half its height down
            tips = [out[c][-1] for c in TAILS]
            rock = (sum(p[0] for p in tips) / 3, sum(p[1] for p in tips) / 3 + ROCK[1] / 2 - 2)
        return out, head, rock


def side(h, k, f):
    """Which side of the hip -> foot line the knee bends to (+1 / -1)."""
    return 1.0 if (f[0] - h[0]) * (k[1] - h[1]) - (f[1] - h[1]) * (k[0] - h[0]) > 0 else -1.0


def knee(h, f, a, b, s):
    """The knee of a two-bone leg (thigh a, shin b) from the hip h to the foot f, bent to side s (the foot pulled in
    when it is out of reach)."""
    d = math.dist(h, f)
    if d >= a + b - 1e-6:
        r = (a + b - 1e-3) / d
        f = (h[0] + (f[0] - h[0]) * r, h[1] + (f[1] - h[1]) * r)
        d = a + b - 1e-3
    d = max(d, abs(a - b) + 1e-3)
    x = (a * a - b * b + d * d) / (2 * d)
    y = math.sqrt(max(a * a - x * x, 0.0))
    ux, uy = (f[0] - h[0]) / d, (f[1] - h[1]) / d
    return (h[0] + ux * x - s * uy * y, h[1] + uy * x + s * ux * y)


def stinger(p, q):
    """The stinger's wedge beyond the tail's last bone p -> q."""
    a = ang(p, q)
    tip = (q[0] + STINGER * math.cos(a), q[1] + STINGER * math.sin(a))
    n = (-math.sin(a) * 3.0, math.cos(a) * 3.0)
    return [(q[0] + n[0], q[1] + n[1]), tip, (q[0] - n[0], q[1] - n[1])]


def draw_skeleton(chains, head, rock, design=None, shift=0):
    """The canvas: the grid, the ground line, the design underneath (optional), the skeleton."""
    can = Image.new("RGBA", (CANVAS, CANVAS), GREY + (255,))
    d = ImageDraw.Draw(can)
    for i in range(0, CANVAS + 1, PX):
        c = (205, 205, 205, 255) if (i // PX) % 10 else (185, 185, 185, 255)
        d.line([(i, 0), (i, CANVAS)], fill=c)
        d.line([(0, i), (CANVAS, i)], fill=c)
    if design is not None:
        im = design.resize((design.width * PX, design.height * PX), Image.NEAREST)
        can.alpha_composite(im, ((DX + shift) * PX, DY * PX))
    over = Image.new("RGBA", can.size, (0, 0, 0, 0))
    o = ImageDraw.Draw(over)
    P = lambda p: ((DX + shift + p[0]) * PX, (DY + p[1]) * PX)
    if rock is not None:
        w, h = ROCK
        x, y = P(rock)
        o.ellipse([x - w * PX / 2, y - h * PX / 2, x + w * PX / 2, y + h * PX / 2], fill=(140, 160, 130, 150),
                  outline=(80, 100, 70, 255), width=3)
    hx0, hy0, hx1, hy1 = HEAD
    o.rectangle([P((hx0 + head[0], hy0 + head[1])), P((hx1 + head[0], hy1 + head[1]))], outline=(110, 110, 110, 255),
                width=4)
    for name in ORDER:
        _, col, _ = CHAINS[name]
        pts = [P(p) for p in chains[name]]
        o.line(pts, fill=col + (255,), width=8, joint="curve")
        for i, (x, y) in enumerate(pts):
            r = 9 if i == len(pts) - 1 else 6
            o.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
        if name in TAILS:
            o.polygon([P(p) for p in stinger(chains[name][-2], chains[name][-1])], fill=col + (255,),
                      outline=(20, 20, 20, 255))
    can.alpha_composite(over)
    d = ImageDraw.Draw(can)
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(220, 40, 40, 255), width=3)
    return can


def fit_shift(chains, rock):
    """Squares to move the figure so every point (and the boulder) stays on the canvas with a margin."""
    xs = [p[0] for pts in chains.values() for p in pts]
    if rock is not None:
        xs += [rock[0] - ROCK[0] / 2, rock[0] + ROCK[0] / 2]
    lo, hi = DX + min(xs) - STINGER, DX + max(xs) + STINGER
    n = CANVAS // PX
    return int(math.ceil(3 - lo)) if lo < 3 else (int(math.floor(n - 3 - hi)) if hi > n - 3 else 0)


def league(lol, spec, rock, out, name):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Skarner",
           "--hq", "--fit-all", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1100",
           "--fit", "0.36", "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", name, "--out", out, "--frame", spec]
    cmd += ["--submesh-texture", "Stone=Props"] if rock else ["--hide-submeshes"]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    m = np.abs(a - GREY).sum(axis=2) > 12
    ys, xs = np.nonzero(m)
    pad = 30
    im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad))).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/sk_work/skarner_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--no-league", action="store_true", help="reuse the League frames already in --out")
    a = ap.parse_args()
    rig = Rig(a.lol)
    design = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")
    rock_d = Image.open(lp(os.path.join(SRC, "hd", "rock.png"))).convert("RGBA")
    out = a.check or a.out
    os.makedirs(out, exist_ok=True)
    rest = {c: rig.rest[c] for c in CHAINS}
    draw_skeleton(rest, (0, 0), None, design).convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    print("K", round(rig.k, 4), "design squares per League unit")
    for k, (name, (spec, _, _, skel)) in enumerate(POSES.items(), start=3):
        chains, head, rk = rig.pose(skel)
        rock = rk is not None
        shift = fit_shift(chains, rk)
        can = draw_skeleton(chains, head, rk, shift=shift)
        sk_path = os.path.join(out, f"{k}_{name}_skeleton.png")
        can.convert("RGB").save(sk_path)
        lg = f"{k}_{name}_league"
        if not a.no_league:
            league(a.lol, spec, rock, out, lg)
        if a.check:
            l_im = Image.open(os.path.join(out, lg + ".png")).convert("RGB")
            l_im = l_im.resize((round(l_im.width * 600 / l_im.height), 600))
            s_im = can.convert("RGB").resize((600, 600))
            both = Image.new("RGB", (l_im.width + 600, 600), (255, 255, 255))
            both.paste(s_im, (0, 0))
            both.paste(l_im, (600, 0))
            both.save(os.path.join(out, f"check_{k}_{name}.png"))
        print(name, spec, "shift", shift, "boulder" if rk else "")
    if a.check:
        return
    hx0, hy0, hx1, hy1 = HEAD
    head = design.crop((hx0, hy0, hx1, hy1))
    pad = Image.new("RGBA", (head.width + 2, head.height + 2), GREY + (255,))
    pad.alpha_composite(head, (1, 1))
    pad.convert("RGB").resize((pad.width * 8, pad.height * 8), Image.NEAREST).save(os.path.join(out, "1_head.png"))
    for img, fname, scale in ((design, "2_design.png", 1.0), (rock_d, "2b_rock.png", B_SCALE)):
        can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        w, h = round(img.width * scale), round(img.height * scale)
        im = img.resize((w * PX, h * PX), Image.NEAREST)
        can.alpha_composite(im, (DX * PX, SOLE_Y - h * PX))
        can.save(os.path.join(out, fname))
    shutil.copyfile(os.path.join(SRC, "POSE_PROMPTS.md"), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()
