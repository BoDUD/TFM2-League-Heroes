#!/usr/bin/env python3
"""Powder's pose pack for Codex (assets/source/powder/POSE_PROMPTS.md): the clean head every frame wears, her action
poses and her run, each figure drawn along a skeleton whose segments are the design's own lengths.

    python tools/art/pack_powder_poses.py [--out %TEMP%/pw_work/powder_pose_pack] [--lol D:/WeGameApps/lol]

Why (2026-10-19): the approved side draft (S-2) cut to 53 rows is 24 squares wide with a near arm two squares thick that
hardly parts from the body - its own squares cannot be posed without the deformations the user rejects
(rig-deformation-checks); the approved idle (A-2) holds a hand at her chin, so the face every frame carries
(one-face-all-frames) needs that hand taken away. And legs drawn freely by Codex come back stretched or crushed
(codex-legs-need-skeletons): every pose here is a red / blue stick figure at the design's lengths, the head a circle of
the design's size, the figure 53 rows like the designs.
Lengths measured on hd/idle.png (53 rows, sole row 52): head top row 0, chin row 21 (head circle 22 squares across);
shoulder row 26; hip joint row 38 (the tunic's hem at 39-40); knee row 44.5, ankle row 50.5 (tall boots from row 45),
the toe 4 squares ahead of the ankle; the arm from the shoulder: upper arm 5.5, forearm 4.5, the hand 2.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_head_fix.png (the idle's head at 22 px squares, the hand's squares
marked magenta: redraw those as chin, jaw, neck and collar; every other square kept); 1_poses_guide.png (7 cells:
wind / throw / crouch / toss / slam / hop / hit) and 2_run_guide.png (8 cells), skeletons on green; 3_look_idle.png and
3_look_side.png (the approved designs, 8x: the look, the colours, the clothes); 4_tft_poses.png and 4_tft_run.png (TFT's
own model in the matching frames: Riot's, kept local).
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
from design_powder_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "powder")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "pw_work")
PX = 7                            # pixels a square on the guide sheets
CW, CH = 46, 64                   # a cell in squares
GROUND = 60                       # the cell row the soles stand on
HIP_X = 21                        # the cell column of the hip joint
# the design's lengths (squares) and rows above the sole row
SOLE = 52
HIP_UP, HEAD_R = SOLE - 38, 11.0
TORSO = 38 - 26                   # hip joint to shoulder
THIGH, SHIN, FOOT = 6.5, 6.0, 4.0
UPPER, FORE, HAND = 5.5, 4.5, 2.0
NECK = 26 - 21                    # shoulder to chin
RED, BLUE, GREY, KEY = (255, 40, 40), (40, 110, 255), (90, 90, 90), (0, 255, 0)
# head fix: the hand at her chin in hd/idle.png (rows / columns, read at 16x)
HEAD_ROWS = 27
HAND_SQ = [(19, 13, 18), (20, 12, 19), (21, 12, 19), (22, 12, 19), (23, 11, 17), (24, 11, 16), (25, 11, 15),
           (26, 12, 14)]   # (row, first column, last column): the fist (rows 20-22) and the arm wrap running down-left


def ray(p, deg, length):
    """From p along deg (0 = straight down, 90 = forward / image right, 180 = up, 270 = back)."""
    a = math.radians(deg)
    return (p[0] + length * math.sin(a), p[1] + length * math.cos(a))


def figure(lean=0.0, up=0.0, dx=0.0, near_arm=(10, 10), far_arm=(-10, -10), near_leg=(0, 0), far_leg=(0, 0)):
    """The stick figure: lean = the torso's degrees forward (+) from upright; up = rows the hip is above its standing
    height (negative: lower); arms (upper, forearm) and legs (thigh, shin) in ray() degrees. -> dict of joints in cell
    squares (x right, y down)."""
    hip = (HIP_X + dx, GROUND - HIP_UP - up)
    shoulder = ray(hip, 180 - lean, TORSO)
    chin = ray(shoulder, 180 - lean, NECK)
    head = ray(chin, 180 - lean * 0.4, HEAD_R)
    j = {"hip": hip, "shoulder": shoulder, "chin": chin, "head": head}
    for side, (ua, fa) in (("near", near_arm), ("far", far_arm)):
        elbow = ray(shoulder, ua, UPPER)
        wrist = ray(elbow, fa, FORE)
        j[side + "_arm"] = [shoulder, elbow, wrist, ray(wrist, fa, HAND)]
    for side, (ta, sa) in (("near", near_leg), ("far", far_leg)):
        knee = ray(hip, ta, THIGH)
        ankle = ray(knee, sa, SHIN)
        j[side + "_leg"] = [hip, knee, ankle, (ankle[0] + FOOT, ankle[1] + 1.5)]
    return j


def grounded(j):
    """Lower the whole figure so its lowest sole sits on GROUND (a pose that crouches comes down)."""
    low = max(p[1] for k in ("near_leg", "far_leg") for p in j[k][2:]) + 0.5
    dy = GROUND - low
    out = {}
    for k, v in j.items():
        out[k] = [(x, y + dy) for x, y in v] if isinstance(v, list) else (v[0], v[1] + dy)
    return out


# name -> (TFT frame for the reference, the figure, grounded): every limb at the design's length
POSES = {
    # attack 1/2 and R 1/2: drawn back to throw (TFT attack_1 at 229 ms) - the near arm up behind her head (never over
    # the face), the weight on the back leg, the front leg stepped forward
    "wind": ("attack_1@229", dict(lean=-12, near_arm=(215, 245), far_arm=(60, 80), near_leg=(-15, -10),
                                  far_leg=(25, 5)), True),
    # attack 2/2, R 2/2, Q's release: the throw (TFT attack_1 at 458 ms) - leaning forward, the near arm flung forward at
    # shoulder height, a lunge: the front leg bent, the back leg straight back
    "throw": ("attack_1@458", dict(lean=22, near_arm=(105, 95), far_arm=(-40, -20), near_leg=(-35, -35),
                                   far_leg=(45, 0)), True),
    # Q 1/2: crouched low with the monkey held near the ground in both hands (TFT Spell at 583 ms)
    "crouch": ("Spell@583", dict(lean=28, near_arm=(35, 70), far_arm=(45, 80), near_leg=(75, -15),
                                 far_leg=(70, -20)), True),
    # Q 2/2: the underhand toss, rising (TFT attack_2 at 458 ms) - the near arm swung forward and up to chest height,
    # in front of her and below the face (higher, it crossed the face), the legs straightening in a short step
    "toss": ("attack_2@458", dict(lean=8, near_arm=(115, 125), far_arm=(-30, -10), near_leg=(-18, -18),
                                  far_leg=(18, 5)), True),
    # E 1/2: the smoke bomb slammed down at her feet (TFT attack_1 at 688 ms) - bent forward, the near arm thrown down
    "slam": ("attack_1@688", dict(lean=35, near_arm=(55, 25), far_arm=(-20, 10), near_leg=(30, -15),
                                  far_leg=(40, -5)), True),
    # E 2/2: the hop back - in the air, the knees tucked up, both arms forward for balance
    "hop": ("Death@138", dict(lean=-10, up=7, near_arm=(80, 70), far_arm=(70, 60), near_leg=(75, -10),
                              far_leg=(60, -25)), False),
    # hit (and the death's start): knocked back - the upper body back, the arms bent in front of the chest
    "hit": ("Death@0", dict(lean=-18, near_arm=(40, 120), far_arm=(30, 110), near_leg=(-8, -8), far_leg=(12, 0)), True),
}
# the run: a child's run (TFT's Run, league_jinx's run for the stride): the near leg's ankle (ahead of the hip, lift)
# over 8 phases, the far leg four on; the body down a row as a foot lands; the arms swinging against the legs
RUN = [(5.0, 0), (2.5, 0), (0.0, 0), (-3.0, 0), (-5.0, 1.5), (-3.5, 4.5), (0.5, 5.0), (4.0, 2.0)]
RUN_BOB = [1, 0, 0, 0, 1, 0, 0, 0]
RUN_ARM = [-35, -20, 0, 20, 35, 20, 0, -20]      # the near arm's upper-arm swing (degrees forward of down)


def run_leg(hip, ax, lift):
    """A run leg from the hip to an ankle ax ahead and lift rows up (0: on the ground); the knee bends forward."""
    L = THIGH + SHIN
    ay = GROUND - 2.0 - lift
    d = min(math.hypot(ax, ay - hip[1]), L - 0.01)
    mid = ((2 * hip[0] + ax) / 2, (hip[1] + ay) / 2)
    h = math.sqrt(max(0.0, THIGH * THIGH - (d / 2) ** 2))
    ux, uy = ax / d, (ay - hip[1]) / d
    knee = (mid[0] + uy * h, mid[1] - ux * h)
    if knee[0] < mid[0]:
        knee = (mid[0] - uy * h, mid[1] + ux * h)
    ankle = (hip[0] + ax, ay)
    return [hip, knee, ankle, (ankle[0] + FOOT, ankle[1] + 1.5)]


def run_figures():
    out = []
    for k in range(8):
        j = figure(lean=8, up=-RUN_BOB[k] - 0.5, near_arm=(RUN_ARM[k], RUN_ARM[k] + 60),
                   far_arm=(-RUN_ARM[k], -RUN_ARM[k] + 60))
        nax, nl = RUN[k]
        fax, fl = RUN[(k + 4) % 8]
        j["near_leg"] = run_leg(j["hip"], nax, nl)
        j["far_leg"] = run_leg(j["hip"], fax, fl)
        out.append((f"run {k + 1}", j))
    return out


def draw_cell(j, label):
    im = Image.new("RGB", (CW * PX, CH * PX), KEY)
    d = ImageDraw.Draw(im)
    P = lambda p: (p[0] * PX, p[1] * PX)
    for x in range(0, CW * PX, PX * 5):
        d.line([(x, 0), (x, CH * PX)], fill=(60, 230, 60))
    for y in range(GROUND * PX % (PX * 5), CH * PX, PX * 5):
        d.line([(0, y), (CW * PX, y)], fill=(60, 230, 60))
    d.line([(0, GROUND * PX), (CW * PX, GROUND * PX)], fill=(120, 80, 40), width=2)
    # the far limbs first (blue), then the torso and head (grey), then the near limbs (red)
    for k in ("far_leg", "far_arm"):
        d.line([P(p) for p in j[k]], fill=BLUE, width=PX)
        for p in j[k][:3]:
            d.ellipse([P((p[0] - .6, p[1] - .6)), P((p[0] + .6, p[1] + .6))], fill=(0, 40, 160))
    d.line([P(j["hip"]), P(j["shoulder"]), P(j["chin"])], fill=GREY, width=PX * 2)
    h = j["head"]
    d.ellipse([P((h[0] - HEAD_R, h[1] - HEAD_R)), P((h[0] + HEAD_R, h[1] + HEAD_R))], outline=GREY, width=PX // 2 + 1)
    d.line([P((h[0] + 2, h[1] + 2)), P((h[0] + 9, h[1] + 2))], fill=GREY, width=2)    # the eyes' row, facing right
    for k in ("near_leg", "near_arm"):
        d.line([P(p) for p in j[k]], fill=RED, width=PX)
        for p in j[k][:3]:
            d.ellipse([P((p[0] - .6, p[1] - .6)), P((p[0] + .6, p[1] + .6))], fill=(160, 0, 0))
    d.text((6, 6), label, fill=(0, 0, 0))
    return im


def tile(cells, cols, gap=PX * 2):
    rows = (len(cells) + cols - 1) // cols
    W, H = cells[0].width, cells[0].height
    sheet = Image.new("RGB", (cols * W + (cols + 1) * gap, rows * H + (rows + 1) * gap), (255, 255, 255))
    for i, c in enumerate(cells):
        sheet.paste(c, (gap + (i % cols) * (W + gap), gap + (i // cols) * (H + gap)))
    return sheet


def big(path, z, grey=(225, 225, 225)):
    a = Image.open(lp(path)).convert("RGBA")
    bg = Image.new("RGBA", a.size, grey + (255,))
    bg.alpha_composite(a)
    return bg.convert("RGB").resize((a.width * z, a.height * z), Image.NEAREST)


def head_fix():
    """The idle's head (rows 0-HEAD_ROWS) at 22 px squares, the hand's squares marked magenta."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))[:HEAD_ROWS].copy()
    for r, c0, c1 in HAND_SQ:
        if r < HEAD_ROWS:
            a[r, c0:c1 + 1] = (255, 0, 255, 255)
    im = Image.new("RGBA", (a.shape[1], a.shape[0]), (225, 225, 225, 255))
    im.alpha_composite(Image.fromarray(a))
    return im.convert("RGB").resize((a.shape[1] * 22, a.shape[0] * 22), Image.NEAREST)


def tft_strip(lol, frames, name, out):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "TFT13_Blue",
           "--wad-file", "TFTSet13.wad.client", "--hide-submesh", "Bomb", "--hide-submesh", "Monkey", "--hq",
           "--mirror", "--bg", "225,225,225", "--yaw", "70", "--size", "360", "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    return os.path.join(out, name + ".png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "powder_pose_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    head_fix().save(os.path.join(out, "0_head_fix.png"))
    cells = []
    for name, (_, kw, g) in POSES.items():
        j = figure(**kw)
        cells.append(draw_cell(grounded(j) if g else j, name))
    tile(cells, 4).save(os.path.join(out, "1_poses_guide.png"))
    tile([draw_cell(j, label) for label, j in run_figures()], 4).save(os.path.join(out, "2_run_guide.png"))
    big(os.path.join(SRC, "hd", "idle.png"), 8).save(os.path.join(out, "3_look_idle.png"))
    big(os.path.join(SRC, "hd", "side.png"), 8).save(os.path.join(out, "3_look_side.png"))
    shutil.copyfile(tft_strip(a.lol, [f for f, _, _ in POSES.values()], "4_tft_poses", out + "_measure"),
                    os.path.join(out, "4_tft_poses.png"))
    shutil.copyfile(tft_strip(a.lol, [f"Run@{k * 104}" for k in range(8)], "4_tft_run", out + "_measure"),
                    os.path.join(out, "4_tft_run.png"))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("written", zp)


if __name__ == "__main__":
    main()
