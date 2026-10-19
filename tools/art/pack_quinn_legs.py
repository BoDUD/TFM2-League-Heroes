#!/usr/bin/env python3
"""Quinn's leg-pose pack for Codex (assets/source/quinn/LEG_PROMPTS.md): the approved idle design, same squares, with
only the LEGS drawn anew in six poses League's clips go through, so the rigged actions stop standing on the idle's legs
(the user, 2026-10-19: 「英雄联盟里面腿部动作一直在变换的 我们的不变」). league_volibear's arm-pose way (pack_volibear_poses.py
/ design_volibear_poses.py): Codex draws on the design's own grid; I keep the design's upper body square for square and
take only the legs back.

    python tools/art/pack_quinn_legs.py [--out %TEMP%/qn_work/quinn_leg_pack] [--lol D:/WeGameApps/lol]

Each pose: the idle (hd/idle.png, 45 x 49) at PX px a square on the 1254 canvas (the step-1 place: crest y 132, soles
y 1210), its upper body (rows above HIP) moved down DROP[pose] whole squares, the legs left empty - the target - and
League's frame of that pose (pose_ref, Riot's model: kept local). Writes <out>/ (and <out>.zip): LEG_PROMPTS.md,
0_design.png (the idle on the grid, the hip line red), <n>_<pose>_target.png, <n>_<pose>_lol.png.
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
from design_quinn_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "qn_work")
CANVAS, PX = 1254, 22
X0, Y0 = 154, 132               # the design's (0, 0) on the canvas (pack_quinn_model: crest y 132, soles y 1210)
HIP = 33                        # rows from here down are the legs (rig_quinn.LEG_TOP)
GROUND = Y0 + 49 * PX           # 1210
# pose -> (squares the upper body goes down, League's frame, what the legs do)
POSES = {
    "kneel": (8, "Quinn_Spell4_Channel@1250", "down on one knee"),
    "lunge": (3, "quinn_spell1@350", "a lunge forward"),
    "wide": (2, "Quinn_attack1@120", "a wide aiming stance"),
    "back": (1, "Quinn_idle1@1200", "the weight on the back leg"),
    "tuck": (0, "Quinn_spell3_flip@100", "both legs tucked up in the air"),
    "step": (0, "Quinn_idle1@0", "the feet close together"),
}


def grid(img, lines=()):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(img)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    for y, c, label in lines:
        dr.line([(0, y), (CANVAS, y)], fill=c, width=3)
        dr.text((12, y - 16), label, fill=c)
    return lay.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "quinn_leg_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(d, PX)), (X0, Y0))
    hip_y = Y0 + HIP * PX
    grid(can, [(hip_y, (230, 40, 40, 255), f"hip line y {hip_y}: the legs start here"),
               (GROUND, (40, 40, 230, 255), f"ground y {GROUND}")]).save(os.path.join(out, "0_design.png"))
    upper = d.copy()
    upper[HIP:] = 0
    work = out + "_work"
    for n, (pose, (drop, frame, what)) in enumerate(POSES.items(), 1):
        t = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        t.paste(Image.fromarray(up(upper, PX)), (X0, Y0 + drop * PX))
        grid(t, [(hip_y + drop * PX, (230, 40, 40, 255), f"hip line y {hip_y + drop * PX} (upper body {drop} squares down)"),
                 (GROUND, (40, 40, 230, 255), f"ground y {GROUND}")]).save(os.path.join(out, f"{n}_{pose}_target.png"))
        cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ", "Quinn",
               "--hq", "--mirror", "--yaw", "60", "--size", "700", "--no-labels", "--name", pose, "--out", work,
               "--frame", frame]
        subprocess.run(cmd, check=True, capture_output=True)
        shutil.copyfile(os.path.join(work, pose + ".png"), os.path.join(out, f"{n}_{pose}_lol.png"))
        print(pose, drop, frame)
    shutil.copyfile(lp(os.path.join(SRC, "LEG_PROMPTS.md")), os.path.join(out, "LEG_PROMPTS.md"))
    print(shutil.make_archive(out, "zip", out))


if __name__ == "__main__":
    main()
