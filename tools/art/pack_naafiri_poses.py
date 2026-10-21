#!/usr/bin/env python3
"""Naafiri's pose pack for Codex (assets/source/naafiri/POSE_PROMPTS.md): the whole-body poses her League clips go
through that the 3/4 design cannot give by moving its own parts - rearing with the jaws wide, the lunge, the leap that
flings the dagger, the low blade-flare and the flat dash of the pursuit, the howl, the fall, the gallop - and a
packmate's gallop and diving bite (the user, 2026-10-21: write the prompts for Codex when the sprites are made).

    python tools/art/pack_naafiri_poses.py [--out C:/t/nf_work/naafiri_pose_pack] [--lol D:/WeGameApps/lol]

A quadruped has no skeleton the human packs' way (pack_shyvana_poses.py), so each pose's guide is League's own frame
rendered with TFM2's proportions (pose_ref.py --head 1.6 --legs 0.85, 3/4 facing right, the 'Hand' submesh hidden) at the
design's scale: one factor for all of her poses, from her idle's height to the design's 45 rows (the packmate's: its idle
to 24 rows), so the poses keep their sizes against each other; the paws on the ground (the fling as high as League's clip has it; the dash and the gallop's flight a few squares
up).
Every pose is ONE 1254 picture: hers at 11 px a square with the paws on y 1188, the packmate's at 22 px on y 1188.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_naafiri.png / 0_design_packmate.png (the designs on the grid,
where they stand); 1_head_naafiri.png / 1_head_packmate.png (the heads, 8x: every pose wears them); per pose
<k>_<name>_guide.png (League's frame on the grid at the size to draw, the ground line red) and <k>_<name>_league.png (the
frame large: Riot's, kept local).
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_naafiri_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "naafiri")
CANVAS, GROUND_Y = 1254, 1188
GREY = (225, 225, 225)
SIZE, WIDTH, FIT, GROUND = 1000, 2.6, 0.3, 0.75      # the render cell (the idle's paws are the ground)
# who -> (champ, idle frame, design, rows, px a square, head box in the design (rows, columns, ends exclusive))
WHO = {"naafiri": ("Naafiri", "Idle@0", "idle.png", 45, 11, (14, 40, 46, 68)),
       "packmate": ("NaafiriPackmate", "idle1@0", "pack.png", 24, 22, (3, 18, 30, 49))}
# the poses in order: name -> (who, League's frame, what it is for (Chinese), the pose line (English))
POSES = {
    "crouch": ("naafiri", "attack1@0",
               "蓄势：后腿下蹲、前身微微抬起，头往前伸、嘴微张，刀刃鬃毛往后贴，尾巴在身后（普攻、大招的起手）",
               "CROUCH - gathering to spring: the hind legs bent low, the front a little raised, the head stretched "
               "forward with the jaws slightly open, the blade mane laid back, the tail behind her."),
    "rear": ("naafiri", "attack1@250",
             "人立张嘴：前身高高抬起、两只前爪离地，头仰起、嘴张到最大露出满口尖牙，刀刃鬃毛竖起（普攻出手前、E 剔骨本能起手）",
             "REAR - rearing up on the hind legs, both fore paws off the ground, the head thrown up with the jaws "
             "opened as wide as they go (all the fangs and the dark red mouth), the blade mane standing up."),
    "lunge": ("naafiri", "attack1@500",
              "前扑撕咬：身子贴低往前伸到最长，头往前伸、咬下去，前腿往前探、后腿往后蹬，尾巴平伸在身后（普攻命中、扑中后撕咬）",
              "LUNGE - stretched out low and long, the head thrust forward biting, the fore legs reaching forward, the "
              "hind legs pushing back, the tail stretched out level behind."),
    "fling": ("naafiri", "Spell1_Idle@300",
              "跃空甩匕首：整个身子跃起离地，弓成一道弧，头往前下方甩，嘴里的匕首甩出去的那一下（Q 暗裔犬牙）",
              "FLING - leaping off the ground with the body arched in a curve, the head whipped forward and down as "
              "she flings the dagger from her jaws, the legs tucked under her, the tail streaming behind."),
    "flare": ("naafiri", "Spell2Cast@500",
              "压低张刃：前身压到最低、几乎贴地，后身抬高，刀刃鬃毛往前上方整片张开，头低着盯着前面（大招猎狗血性的起手）",
              "FLARE - the front pressed down almost to the ground, the hindquarters raised, the whole blade mane "
              "fanned out forward and up, the head low and staring ahead (the pounce's wind-up)."),
    "dash": ("naafiri", "Spell2Dash@250",
             "贴地飞扑：整个身子拉直成一条线往前飞，四条腿收在身下往前后伸直，刀刃鬃毛往后平贴，尾巴拉直在后面（大招飞扑、E 冲刺）",
             "DASH - flying forward stretched into one straight line, the four legs stretched forward and back under "
             "her, the blade mane swept flat backwards, the tail straight out behind (the pounce and the dash)."),
    "rise": ("naafiri", "Spell3Idle@500",
             "人立仰头：前身斜斜往上立起，头仰向前上方，前爪离地，后腿撑地，尾巴扬起（E 剔骨本能撕裂）",
             "RISE - reared diagonally up on the hind legs, the head raised forward and up, the fore paws off the "
             "ground, the tail lifted (Eviscerate's shred)."),
    "howl": ("naafiri", "Death@2271",
             "仰天长嚎：坐在后腿上，前腿撑直，脖子和头笔直朝天，嘴张开嚎叫，刀刃鬃毛竖起（大招暴吼、阵亡第一下）",
             "HOWL - sitting back on the hind legs with the fore legs braced straight, the neck and head pointed "
             "straight up at the sky, the jaws open howling, the blade mane standing up (the roar)."),
    "lie": ("naafiri", "Death@3179",
            "趴倒：整个身子侧趴在地上，四条腿伸向一边，头贴在地上（朝画面右边），刀刃鬃毛平贴，尾巴拖在地上（阵亡）",
            "LIE - fallen and lying flat on her side on the ground, the four legs stretched out to one side, the head "
            "resting on the ground at the image right, the blade mane flat, the tail lying along the ground."),
    "run1": ("naafiri", "Run@0", "奔跑 1：前腿往前伸、后腿往后蹬，身子拉长（四足奔跑的腾空伸展）",
             "RUN 1 - galloping: the fore legs reaching forward, the hind legs kicked back, the body stretched long."),
    "run2": ("naafiri", "Run@200", "奔跑 2：前腿着地往后收，后腿往前收到肚子下面，身子缩短拱起",
             "RUN 2 - galloping: the fore paws on the ground drawing back, the hind legs swung forward under the belly, "
             "the body gathered and arched."),
    "run3": ("naafiri", "Run@400", "奔跑 3：后腿着地往后蹬，前腿离地往前伸",
             "RUN 3 - galloping: the hind paws on the ground pushing back, the fore legs off the ground reaching forward."),
    "run4": ("naafiri", "Run@600", "奔跑 4：四条腿都收在身下，身子腾空、最高",
             "RUN 4 - galloping: all four legs gathered under her, the body off the ground at its highest."),
    "p_run1": ("packmate", "runVariant1@0", "伙伴奔跑 1：前腿往前伸、后腿往后蹬",
               "PACKMATE RUN 1 - the fore legs reaching forward, the hind legs kicked back."),
    "p_run2": ("packmate", "runVariant1@200", "伙伴奔跑 2：前腿着地往后收、后腿往前收",
               "PACKMATE RUN 2 - the fore paws down drawing back, the hind legs swung forward."),
    "p_run3": ("packmate", "runVariant1@400", "伙伴奔跑 3：后腿着地往后蹬、前腿往前伸",
               "PACKMATE RUN 3 - the hind paws down pushing back, the fore legs reaching forward."),
    "p_run4": ("packmate", "runVariant1@600", "伙伴奔跑 4：四条腿收在身下、身子最高",
               "PACKMATE RUN 4 - all four legs gathered under it, the body at its highest."),
    "p_bite": ("packmate", "NaafiriPackmate_Attack1@200",
               "伙伴扑咬：往前下方扑下去，头和头盔的刀刃朝前下方，后腿蹬直（伙伴撕咬目标）",
               "PACKMATE BITE - diving forward and down onto its prey, the head and the helmet's blade pointing "
               "forward-down, the hind legs pushed straight."),
}


# squares a pose's lowest point is off the ground (None: as high as League's clip has it); the rest stand on it
LIFT = {"fling": None, "dash": 3, "run4": 2, "p_run4": 1}


def render(lol, champ, frame, name, out):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ, "--wad",
           "Naafiri", "--hide-submeshes", "--mirror", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--head", "1.6", "--legs", "0.85", "--size", str(SIZE), "--width", str(WIDTH), "--fit", str(FIT),
           "--ground", str(GROUND), "--yaw", "35", "--frame", frame, "--name", name, "--out", out]
    subprocess.run(cmd, check=True, capture_output=True)
    return Image.open(os.path.join(out, name + ".png")).convert("RGB")


def keyed(im):
    a = np.asarray(im.convert("RGBA")).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 20] = 0
    return Image.fromarray(a)


def grid(can, px, label):
    d = ImageDraw.Draw(can)
    for k in range(0, CANVAS // px + 1):
        c = (150, 150, 150, 255) if k % 5 == 0 else (205, 205, 205, 255)
        d.line([(k * px, 0), (k * px, CANVAS)], fill=c)
        d.line([(0, k * px), (CANVAS, k * px)], fill=c)
    d.line([(0, GROUND_Y), (CANVAS, GROUND_Y)], fill=(220, 40, 40, 255), width=3)
    d.text((10, 10), label, fill=(30, 30, 30, 255))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/nf_work/naafiri_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out, work = a.out, a.out + "_render"
    for d in (out, work):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
    scale = {}
    for who, (champ, idle, design, rows, px, (r0, r1, c0, c1)) in WHO.items():
        im = keyed(render(a.lol, champ, idle, f"idle_{who}", work))
        x0, y0, x1, y1 = im.getbbox()
        scale[who] = (rows * px / (y1 - y0), y1)              # the idle's height -> the design's rows; its paws = ground
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", design))).convert("RGBA"))
        can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
        grid(can, px, f"{who}: the design, {d.shape[1]} x {d.shape[0]} squares of {px} px, paws on the red line")
        big = Image.fromarray(up(d, px))
        can.alpha_composite(big, ((CANVAS - big.width) // 2 // px * px, GROUND_Y - big.height))
        can.convert("RGB").save(os.path.join(out, f"0_design_{who}.png"))
        h = d[r0:r1, c0:c1]
        hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
        hb.alpha_composite(Image.fromarray(up(h, 8)))
        hb.convert("RGB").save(os.path.join(out, f"1_head_{who}.png"))
    report = []
    for k, (name, (who, frame, _, _)) in enumerate(POSES.items(), start=2):
        champ, _, _, rows, px, _ = WHO[who]
        im = keyed(render(a.lol, champ, frame, name, work))
        x0, y0, x1, y1 = im.getbbox()
        fig = im.crop((x0, y0, x1, y1))
        k_, ground = scale[who]
        fig = fig.resize((round(fig.width * k_), round(fig.height * k_)), Image.LANCZOS)
        lift = LIFT.get(name, 0)
        # on the ground unless the pose leaves it: the clips' root heights differ, so only the fling keeps its own
        bottom = GROUND_Y - round((ground - y1) * k_) if lift is None else GROUND_Y - lift * px
        can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
        grid(can, px, f"{name}: League's frame at the size to draw ({px} px a square, {fig.width / px:.0f} x "
                      f"{fig.height / px:.0f} squares), the ground red")
        left = max(px, min(CANVAS - fig.width - px, (CANVAS - fig.width) // 2))
        can.alpha_composite(fig, (left, bottom - fig.height))
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_guide.png"))
        big = im.crop((x0, y0, x1, y1))
        big.convert("RGB").save(os.path.join(out, f"{k}_{name}_league.png"))
        report.append(f"{k:2d} {name:8s} {who:8s} {fig.width / px:5.1f} x {fig.height / px:5.1f} squares, bottom y {bottom}"
                      + ("  TOO WIDE" if fig.width > CANVAS - 2 * px else ""))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("\n".join(report), "\n->", zp)


if __name__ == "__main__":
    main()
