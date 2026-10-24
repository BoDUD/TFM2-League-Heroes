#!/usr/bin/env python3
"""Aurelion Sol's pose pack for Codex (assets/source/aurelionsol/POSE_PROMPTS.md): the whole-body poses his League
clips go through - a floating dragon with two clawed arms and a nebula tail (pack_belveth_poses.py's way, with arms in
place of her wings and no collar).

    python tools/art/pack_aurelionsol_poses.py [--out C:/t/as_work/aurelionsol_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, the lowest point on y SOLE_Y - the design hd/idle.png (Codex's step-1
A-2, 56 x 77, PPU 1.75) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames
(tools/lol/pose_ref.py at the 3/4 camera; ours keep the face to the front-right): every bone at the design's OWN length
(measured on hd/idle.png at 12x: REST), only its direction set per pose (POSES), the lowest point (the tail's tip, or a
claw) on the ground unless `lift` raises it (he floats: the hover comes with the frames, as Vel'Koz's FLOAT). League's
skin draws the tail as an untextured mesh (black in the renders): it shows how the tail moves. No run here: he flies,
so the move is rigged from the step-1 B design (hd/run.png).
THE HEAD (hd/idle.png rows 0-32, columns 3-38: the mane, the gold crown and horns, the face, the chin's gold point) is
pasted on every pose upright, never turned - except q_breath, where Codex opens the jaw (the breath).
THE ARMS: each a chain shoulder -> elbow -> wrist -> claw tip; the back spikes ride on the body.
THE TAIL: from its root under the chest (the body's lowest middle) to its tip, five bones.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png; 1_head.png (8x); 2_design.png; per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (the body's lowest middle to the base of the neck), ORANGE = the NEAR arm (image
left), PURPLE = the FAR arm (image right), MAGENTA = the nebula tail (from its root under the chest to its tip), grey box
= the head.
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
from design_aurelionsol_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aurelionsol")
PX, CANVAS, SOLE_Y = 11, 1254, 1188
GREY = (225, 225, 225)
GROUND = 77                        # the design's tail tip's bottom edge (rows)
DX, DY = 30, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its tail tip on row 108)
COL = {"spine": (0, 170, 60), "near_arm": (255, 140, 0), "far_arm": (150, 60, 200), "tail": (230, 0, 200)}
HEAD = (0, 32, 3, 38)              # rows / columns of the head in hd/idle.png (ends exclusive): the mane top to the chin
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 35 x 32 squares
FACE = (24, 38, 18, 32)            # the face (the eyes, the teeth, the chin): x0, x1, y0, y1 in design squares

# the design's own skeleton, measured on hd/idle.png (56 x 77, square edges): the head box's middle; the spine from the
# body's lowest middle to the base of the neck; each arm's shoulder, elbow (the bracer's top), wrist and the longest
# claw's tip; the tail's root under the chest, its S curl and its tip on the ground
REST = {
    "head": (20.5, 16.0),
    "spine": [(22.0, 52.0), (24.0, 31.0)],
    "near_arm": [(14.0, 38.0), (8.0, 43.0), (6.0, 48.0), (4.0, 58.0)],
    "far_arm": [(32.0, 40.0), (38.0, 45.0), (43.0, 45.0), (55.0, 42.0)],
    "tail": [(22.0, 52.0), (30.0, 58.0), (28.0, 63.0), (18.0, 67.0), (20.0, 73.0), (31.0, 76.0)],
}
LIMBS = ("near_arm", "far_arm", "tail")
TOP_LIMBS = ("near_arm", "far_arm")   # rooted at the neck (turned with the spine); the tail at the body's end (half)
GROUND_LIMBS = ("tail",)   # he floats: only the tail sets the lowest point (an arm may hang lower in the air)

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# body's lowest middle "pelvis" (design squares), "lift" (rows the lowest point is off the ground; None: on it), "shift"
# (squares the whole figure is moved on the canvas), "ground" (the limbs whose lowest point stands on the line: the tail
# alone unless the tail is raised), the spine's direction and every limb as "rest" or its bones'
# directions (degrees: 0 straight down, 90 to the image right, 180 up, -90 to the image left), each bone at the design's
# length.
POSES = {
    "a_wind": ("aurelionsol_attack1@150",
               "扬爪：身子往上挺、微微后仰（画面左边），远侧的爪子（画面右边）抬到头的右边、高过肩膀（爪心里握着一颗小星星的位置，不挡脸），近侧的爪子收在胸前下方，尾巴在身下垂着（普攻起手）",
               "WIND-UP - rearing up tall and leaning back a little to the image left, the FAR clawed arm (image right) "
               "raised up beside his head on the image right, above the shoulder, as if holding a small star, the near arm drawn in below his "
               "chest, the nebula tail hanging down beneath him.",
               dict(pelvis=(22.0, 52.0), lift=None, shift=0, spine=-176, near_arm=(-20, 20, 40),
                    far_arm=(125, 150, 170), tail=(10, -5, -20, 5, 30))),
    "a_throw": ("aurelionsol_attack1@300",
                "甩出：身子往前（画面右边）探，脖子往前伸，远侧的爪子往前用力甩出去（手臂伸直、爪子张开朝右），近侧的爪子往后摆，尾巴往身后左边甩（普攻甩出星星）",
                "THE THROW - lunging forward to the image right, the neck stretched forward, the FAR clawed arm flung out "
                "straight to the image right with the claws open (the star let go), the near arm swung back, the tail "
                "swept out behind him to the image left.",
                dict(pelvis=(22.0, 52.0), lift=None, shift=-6, spine=150, near_arm=(-60, -40, -30),
                     far_arm=(95, 92, 95), tail=(-60, -85, -100, -80, -95))),
    "q_wind": ("aurelionsol_spell1_newtst@225",
               "吸气：脖子往后缩、胸口挺起来（像深吸一口气），头抬高一点，两只爪子收在胸前两侧，尾巴往身后卷起（星河冲荡：起手）",
               "THE BREATH IN - the neck drawn back and the chest puffed out (a deep breath in), the head held a little "
               "higher, both clawed arms drawn in at the sides of his chest, the tail curling up behind him.",
               dict(pelvis=(22.0, 52.0), lift=None, shift=2, spine=-170, near_arm=(-10, 40, 70),
                    far_arm=(20, 60, 80), tail=(-40, -80, -120, -150, -100))),
    "q_breath": ("aurelionsol_spell1_loop@250",
                 "吐息：身子往前（画面右边）压，脖子往前伸，嘴巴张大（下颌往下张开，露出上下两排牙和嘴里的亮光；龙息本身不画，后面单画），两只爪子张开在身前两侧，尾巴在身后卷着（星河冲荡：吐息）",
                 "THE BREATH - leaning forward to the image right with the neck stretched out and the JAW WIDE OPEN (the "
                 "lower jaw dropped, both rows of teeth showing and a glow inside the mouth; the breath beam itself is "
                 "NOT drawn), both clawed arms spread at the front sides of his body, the tail curled behind him.",
                 dict(pelvis=(22.0, 52.0), lift=None, shift=-4, spine=155, near_arm=(-40, -10, 10),
                      far_arm=(60, 85, 100), tail=(-50, -90, -130, -100, -70))),
    "e_reach": ("aurelionsol_spell3_new@250",
                "伸爪：身子往前倾，远侧的爪子往前上方伸出去、爪子张开（在前方召唤黑洞），近侧的爪子往后下方摆，尾巴往身后上方扬起（星芒凝汇：召唤）",
                "THE REACH - leaning forward, the FAR clawed arm reaching forward and up with the claws spread (calling "
                "the black hole in front of him), the near arm swung back and down, the tail raised up behind him.",
                dict(pelvis=(22.0, 52.0), lift=None, shift=-2, spine=165, near_arm=(-50, -30, -20),
                     far_arm=(115, 125, 135), tail=(-50, -95, -130, -160, -175))),
    "e_hold": ("aurelionsol_spell3_new@600",
               "捧星：两只爪子在胸前下方合拢、爪心相对（像官方原画里捧着一颗星星，中间留空，黑洞后面单画），身子微微前弓，尾巴照定稿卷在身下（星芒凝汇：凝聚）",
               "THE CUPPED CLAWS - both clawed arms brought together in front of his lower chest, the palms facing each "
               "other with a gap between them (as in the official art, holding a star; the black hole is drawn later), "
               "hunched forward a little, the tail curled under him as in the design.",
               dict(pelvis=(22.0, 52.0), lift=None, shift=0, spine=168, near_arm=(40, 80, 95),
                    far_arm=(20, -10, -60), tail="rest")),
    "r_call": ("aurelionsol_spell4_calamity@482",
               "召星：身子挺直往上，远侧的爪子在头的右边高高举起、朝天张开（从天上拽星星，不挡脸），近侧的爪子往下张开，尾巴在身下摆向右边（星落：召唤）",
               "THE CALL - upright and stretched tall, the FAR clawed arm raised high on the image right of his head, up "
               "with the claws open (never over the face) (pulling a star down from the sky), the near arm spread down, the tail swinging under him to "
               "the image right.",
               dict(pelvis=(22.0, 52.0), lift=None, shift=0, spine=180, near_arm=(-45, -25, -15),
                    far_arm=(135, 155, 168), tail=(20, 40, 15, -20, -50))),
    "r_pull": ("aurelionsol_spell4_calamity@1206",
               "拽下：身子往前下方猛地一弓，远侧的爪子从头顶往下拽到身前右下方（爪子握紧），近侧的爪子往后，尾巴往身后上方甩起（星落：砸下）",
               "THE PULL DOWN - hunched sharply forward and down, the FAR clawed arm yanked down from above to the front "
               "lower right (the claws clenched), the near arm back, the tail whipped up behind him.",
               dict(pelvis=(22.0, 52.0), lift=None, shift=-4, spine=140, ground=LIMBS, near_arm=(-60, -40, -30),
                    far_arm=(50, 30, 20), tail=(-110, -140, -165, 175, 160))),
    "d_rear": ("aurelionsol_death@375",
               "仰倒：身子往后（画面左边）仰，头往后抬，两只爪子往两边无力地张开，尾巴在身下松松地垂着（死亡第一下）",
               "REARING BACK - falling back to the image left, the head thrown back, both clawed arms flung limply open "
               "to the sides, the tail hanging loose beneath him.",
               dict(pelvis=(22.0, 52.0), lift=None, shift=2, spine=-158, near_arm=(-100, -115, -130),
                    far_arm=(95, 105, 115), tail=(5, -10, -25, -10, 15))),
    "d_down": ("aurelionsol_death@2625",
               "倒下：身子瘫软地沉到地上、往后斜躺，两只爪子摊在地上，星云尾巴平平地拖在身后左边的地上（死亡）",
               "DOWN - sunk limp to the ground and lying tilted back, both clawed arms spread on the ground, the nebula "
               "tail lying flat on the ground behind him to the image left.",
               dict(pelvis=(26.0, 66.0), lift=None, shift=4, spine=-128, near_arm=(-80, -90, -95),
                    far_arm=(-5, 35, 75), tail=(-75, -88, -95, -92, -96))),
}


def ang(a, b):
    """The direction a -> b in degrees (0 = straight down, 90 = to the image right; y down)."""
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def along(p, deg, length):
    r = math.radians(deg)
    return (p[0] + length * math.sin(r), p[1] + length * math.cos(r))


def turned(v, deg):
    """A vector turned the way ang() counts: +deg turns straight down towards the image right."""
    r = math.radians(deg)
    x, y = v
    return (x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r))


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the arms' shoulders where the design has them
    by the neck, turned with the spine, the tail's root at the body's end turned half as much; the head box upright over
    the neck (the head is pasted, never turned). The lowest point on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1]),
          "neck_shift": (neck[0] - rs[1][0], neck[1] - rs[1][1])}
    for name in LIMBS:
        top = name in TOP_LIMBS
        base, base_rest, k = (neck, rs[1], 1.0) if top else (pel, rs[0], 0.5)
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        assert len(sp) == len(lengths(name)), (name, sp)
        for a_, l_ in zip(sp, lengths(name)):
            pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for name in spec.get("ground", GROUND_LIMBS) for _, y in sk[name])
    dy = GROUND - (spec["lift"] or 0) - low
    moved = {}
    for k, v in sk.items():
        if k in ("head", "neck_shift"):
            moved[k] = (v[0], v[1] + dy)
        else:
            moved[k] = [(x, y + dy) for x, y in v]
    return moved


def to_canvas(sk, shift=0):
    out = {}
    for k, v in sk.items():
        if k == "head":
            out[k] = (v[0] + DX + shift, v[1] + DY)
        elif k == "neck_shift":
            out[k] = v
        else:
            out[k] = [(x + DX + shift, y + DY) for x, y in v]
    out["origin"] = (DX + shift + out["neck_shift"][0], DY + out["neck_shift"][1])
    return out


def canvas_grid():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def c(p):
    """A point in design square edges, already on the canvas grid, in canvas px."""
    return (p[0] * PX, p[1] * PX)


def skeleton(can, s, label, idle, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("tail", "far_arm", "spine", "near_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for p in pts:
            rr = 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work):
    """League's frame at the 3/4 camera."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "AurelionSol",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900",
           "--fit", "0.3", "--ground", "0.72", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work,
           "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone and head box on the canvas; no arm or tail over the face."""
    out = []
    pts = [p for k in ("spine",) + LIMBS for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1:
        out.append("head off the top")
    fx0, fx1 = hx + FACE[0] - REST["head"][0], hx + FACE[1] - REST["head"][0]
    fy0, fy1 = hy + FACE[2] - REST["head"][1], hy + FACE[3] - REST["head"][1]
    over = []
    for w in LIMBS:   # every point along the bones, a twentieth of a bone apart
        for p, q in zip(s[w], s[w][1:]):
            over += [(p[0] + (q[0] - p[0]) * f / 20, p[1] + (q[1] - p[1]) * f / 20) for f in range(21)]
    face = [p for p in over if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face:
        out.append(f"over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/as_work/aurelionsol_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]),
                                **{k: "rest" for k in LIMBS})))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", idle, 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        names = a.only.split(",") if a.only else list(poses)
        cache = os.path.join(a.check, "_league")
        os.makedirs(cache, exist_ok=True)
        tiles = []
        for name in names:
            s, frame, zh, en = poses[name]
            can = canvas_grid()
            hx, hy = s["head"]                       # the design's head in its box, to judge the proportions
            r0, r1, c0, c1 = HEAD
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name, idle)
            fpath = os.path.join(cache, name + ".png")
            if not os.path.isfile(fpath):
                lol_frame(a.lol, frame, os.path.join(a.check, "_work")).save(fpath)
            lf = Image.open(fpath).convert("RGB")
            sk = can.convert("RGB").resize((CANVAS * 2 // 5, CANVAS * 2 // 5))
            lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
            t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(lf, (sk.width, 0))
            tiles.append(t)
        W = max(t.width for t in tiles)
        cols = 3
        rows_ = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (W * cols, tiles[0].height * rows_), (255, 255, 255))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % cols) * W, (k // cols) * t.height))
        sheet.save(os.path.join(a.check, "poses_check.png"))
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", idle, 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (lowest point on y {SOLE_Y})", idle)
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
