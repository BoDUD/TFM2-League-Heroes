#!/usr/bin/env python3
"""Quinn's leg pack, round 2 (assets/source/quinn/LEG_PROMPTS_2.md): the legs drawn by Codex along a skeleton per frame,
every segment as long as the idle's own, for six action poses and the eight-frame run.

    python tools/art/pack_quinn_legs2.py [--out %TEMP%/qn_work/quinn_leg_pack2] [--lol D:/WeGameApps/lol]

Round 1 (pack_quinn_legs.py) let Codex draw legs freely under the idle's upper body: the user, 2026-10-19: 「腿部各种变形
这叫改好了？ 你自己bureview吗」 - the straight legs of `back` and `lunge` came back about a third longer than the idle's,
`kneel` dropped the body 8 rows and crushed both legs into a heap, every pose redrew the cape's hem, and the knees and
boots changed shape from pose to pose; and 「还有走路时腿都看不出变换的」 - the rig's walk only slid the idle's legs. The
route that worked for league_galio (memory run-legs-caitlyn-way): Codex redraws only the legs, per frame, along red /
blue skeleton lines (hip - knee - ankle - toe) whose thigh and shin are the design's own lengths; the cape's hem and
everything above the hip stay the design's squares (drawn in, not to be changed). ADC runs: straight legs, a scissor
stride (「所有的AD都是画直了移动的」).
Writes <out>/ (and <out>.zip): LEG_PROMPTS_2.md; 1_poses_body.png / 1_poses_guide.png (six cells: the body with the
legs taken away, and the same with the skeletons), 2_run_body.png / 2_run_guide.png (eight cells), 3_legs_sample.png
(the idle's two legs cut out, 8x: the drawing to repeat), 4_poses_lol.png (League's frames, Riot's model, kept local).
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
from design_quinn_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "qn_work")
PX = 7                            # pixels a square on the sheets (league_galio's run pack: 7)
CW, CH = 66, 58                   # a cell in squares
STAND = (24, 54)                  # the cell square the idle's standing point (column 18) and ground (row 49) go on
STAND_COL, GROUND = 18, 49
HIP_ROW = 33                      # the legs start here (rig_quinn.LEG_TOP); left of CAPE_X the cape's hem stays
CAPE_X = 7
# the idle's legs measured on hd/idle.png (8x ruler): near (image left) hip (11.5, 34), knee (11, 40), ankle (10, 45),
# toe (13, 47.5); far (image right) knee (20.5, 41), ankle (21, 45.5), toe (24, 47.5), its hip hidden behind the body at
# the near one's height (both a little bent standing: 11.5 rows hip to ankle on a 12.5 leg)
THIGH, SHIN, FOOT = 6.5, 6.0, 3.5
NEAR_HIP, FAR_HIP = (11.5, 34.0), (19.5, 34.0)
ANKLE_Y = 45.5                    # an ankle on the ground (the sole two rows under it)
RED, BLUE = (255, 40, 40), (40, 110, 255)
KEY = (0, 255, 0)                 # the sheets' background: the green Codex keeps and I key out


def leg(hip, knee_dir, shin_dir, toe=(1, 0)):
    """hip + the thigh along knee_dir (degrees from straight down, + = forward / image right), the shin along shin_dir."""
    a, b = math.radians(knee_dir), math.radians(shin_dir)
    knee = (hip[0] + THIGH * math.sin(a), hip[1] + THIGH * math.cos(a))
    ankle = (knee[0] + SHIN * math.sin(b), knee[1] + SHIN * math.cos(b))
    toe_pt = (ankle[0] + FOOT * toe[0], ankle[1] + FOOT * toe[1] + 1.5)
    return [hip, knee, ankle, toe_pt]


def grounded(hip, ankle_x, bend=0.0):
    """A leg from hip to an ankle on the ground at ankle_x; bend > 0 pushes the knee forward (squares)."""
    dx = ankle_x - hip[0]
    L = THIGH + SHIN
    dy = math.sqrt(max(0.0, L * L - dx * dx)) if not bend else None
    if not bend:
        y = hip[1] + dy
        return [hip, (hip[0] + dx * THIGH / L, hip[1] + dy * THIGH / L), (ankle_x, y), (ankle_x + FOOT, y + 1.5)], y
    raise ValueError


def lowered(points, dy):
    return [(x, y + dy) for x, y in points]


def poses():
    """name -> (drop: rows the body goes down, near leg points, far leg points). Every leg: thigh THIGH, shin SHIN."""
    out = {}
    # crouch (landing, hit): both knees forward, the shins back to the feet under her
    n = leg(NEAR_HIP, 55, -25)
    f = leg(FAR_HIP, 55, -25)
    drop = ANKLE_Y - n[2][1]
    out["crouch"] = (drop, lowered(n, drop), lowered(f, drop))
    # kneel (R's call): the far leg's thigh forward level and its shin straight down to the ground; the near leg's
    # thigh straight down to the knee on the ground and its shin lying back along it
    f = leg(FAR_HIP, 90, 0)
    drop = ANKLE_Y - f[2][1]
    n = leg(NEAR_HIP, 0, -90, toe=(-1, 0))
    out["kneel"] = (drop, lowered(n, drop), lowered(f, drop))
    # lunge (Q, E's leap): the front (far) leg's thigh 50 degrees forward, its shin straight down; the back (near) leg
    # straight back to the ground
    f = leg(FAR_HIP, 50, 0)
    drop = ANKLE_Y - f[2][1]
    hip_n = (NEAR_HIP[0], NEAR_HIP[1] + drop)
    dy = ANKLE_Y - hip_n[1]
    dx = -math.sqrt(max(0.0, (THIGH + SHIN) ** 2 - dy * dy))
    n = [hip_n, (hip_n[0] + dx * THIGH / (THIGH + SHIN), hip_n[1] + dy * THIGH / (THIGH + SHIN)),
         (hip_n[0] + dx, ANKLE_Y), (hip_n[0] + dx + FOOT * 0.6, ANKLE_Y + 1.5)]
    out["lunge"] = (drop, n, lowered(f, drop))
    # wide (the attack's aim): both legs straight, the feet planted wide apart
    n, yn = grounded(NEAR_HIP, NEAR_HIP[0] - 4.5)
    f, yf = grounded(FAR_HIP, FAR_HIP[0] + 4.5)
    drop = max(0.0, ANKLE_Y - max(yn, yf))       # straight legs a little longer than the idle's bent ones: never up
    out["wide"] = (drop, lowered(n, drop), lowered(f, drop))
    # tuck (E's somersault, Skystrike's drop): both knees pulled up forward, the shins hanging back under them
    n = leg(NEAR_HIP, 100, 20)
    f = leg(FAR_HIP, 95, 15)
    out["tuck"] = (0, n, f)
    # step (the idle's shift): both legs straight, the boots side by side under her
    n, yn = grounded(NEAR_HIP, 14.0)
    f, yf = grounded(FAR_HIP, 17.0)
    drop = max(0.0, ANKLE_Y - max(yn, yf))
    out["step"] = (drop, lowered(n, drop), lowered(f, drop))
    return out


# the run: straight legs (hip - ankle at THIGH + SHIN), a scissor stride; the near leg's ankle from its hip, 8 phases
# (planted ahead and passing under, pushed off behind, lifted and swung through); the far leg four phases on; the body
# down a row as a foot lands
RUN = [(5.5, 0), (3.0, 0), (0.0, 0), (-3.0, 0), (-5.5, 1.5), (-3.5, 4.0), (0.5, 4.5), (4.5, 2.0)]
RUN_BOB = [1, 0, 0, 0, 1, 0, 0, 0]


def run_leg(hip, ax, lift):
    L = THIGH + SHIN
    if lift == 0:
        dy = math.sqrt(L * L - ax * ax)
        knee = (hip[0] + ax * THIGH / L, hip[1] + dy * THIGH / L)
        ankle = (hip[0] + ax, hip[1] + dy)
    else:   # a lifted leg bends at the knee: the knee forward of the hip-ankle line
        ay = ANKLE_Y - lift
        d = math.hypot(ax, ay - hip[1])
        d = min(d, L - 0.01)
        mid = (hip[0] + ax / 2, (hip[1] + ay) / 2)
        h = math.sqrt(max(0.0, THIGH * THIGH - (d / 2) ** 2))
        ux, uy = ax / d, (ay - hip[1]) / d
        knee = (mid[0] + uy * h, mid[1] - ux * h)          # the side of the line toward the front
        if knee[0] < mid[0]:
            knee = (mid[0] - uy * h, mid[1] + ux * h)
        ankle = (hip[0] + ax, ay)
    return [hip, knee, ankle, (ankle[0] + FOOT, ankle[1] + 1.5)]


def run_frames():
    out = []
    for k in range(8):
        bob = RUN_BOB[k]
        nax, nl = RUN[k]
        fax, fl = RUN[(k + 4) % 8]
        nh = (NEAR_HIP[0], NEAR_HIP[1] + bob)
        fh = (FAR_HIP[0] - 3.0, FAR_HIP[1] + bob)        # the hips closer in a stride
        out.append((bob, run_leg(nh, nax, nl), run_leg(fh, fax, fl)))
    return out


def body(d):
    """The idle without its legs (the cape's hem, left of CAPE_X, stays)."""
    b = d.copy()
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    b[(yy >= HIP_ROW) & (xx >= CAPE_X)] = 0
    return b


def cell(b, drop, legs=None):
    """A cell: the body moved down drop rows, at PX px a square; with legs, the skeleton lines over it."""
    img = Image.new("RGBA", (CW * PX, CH * PX), KEY + (255,))
    ox, oy = STAND[0] - STAND_COL, STAND[1] - GROUND
    lay = np.zeros((CH, CW, 4), np.uint8)
    y0 = oy + int(round(drop))
    lay[y0:y0 + b.shape[0], ox:ox + b.shape[1]] = b[:CH - y0, :CW - ox]
    img.alpha_composite(Image.fromarray(np.repeat(np.repeat(lay, PX, 0), PX, 1)))
    dr = ImageDraw.Draw(img)
    dr.line([(0, STAND[1] * PX), (CW * PX, STAND[1] * PX)], fill=(0, 150, 0, 255), width=1)
    if legs:
        for pts, c in ((legs[1], BLUE), (legs[0], RED)):          # far first
            q = [((x + ox + 0.5) * PX, (y + oy + 0.5) * PX) for x, y in pts]
            dr.line(q, fill=c + (255,), width=4)
            for x, y in q[:3]:
                dr.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c + (255,))
    return img


def sheet(cells, cols):
    rows = (len(cells) + cols - 1) // cols
    out = Image.new("RGB", (cols * CW * PX, rows * CH * PX), KEY)
    for i, c in enumerate(cells):
        out.paste(c.convert("RGB"), ((i % cols) * CW * PX, (i // cols) * CH * PX))
    dr = ImageDraw.Draw(out)
    for i in range(1, cols):
        dr.line([(i * CW * PX, 0), (i * CW * PX, out.height)], fill=(0, 120, 0), width=2)
    for j in range(1, rows):
        dr.line([(0, j * CH * PX), (out.width, j * CH * PX)], fill=(0, 120, 0), width=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "quinn_leg_pack2"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    b = body(d)
    P = poses()
    names = ["crouch", "kneel", "lunge", "wide", "tuck", "step"]
    sheet([cell(b, P[n][0]) for n in names], 3).save(os.path.join(out, "1_poses_body.png"))
    sheet([cell(b, P[n][0], (P[n][1], P[n][2])) for n in names], 3).save(os.path.join(out, "1_poses_guide.png"))
    R = run_frames()
    sheet([cell(b, bob) for bob, _, _ in R], 4).save(os.path.join(out, "2_run_body.png"))
    sheet([cell(b, bob, (n, f)) for bob, n, f in R], 4).save(os.path.join(out, "2_run_guide.png"))
    # the idle's legs cut out, 8x, the near one tinted red at its edge, the far one blue
    legs = d.copy()
    yy, xx = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    legs[~((yy >= HIP_ROW) & (xx >= CAPE_X))] = 0
    lg = legs[HIP_ROW:, CAPE_X:27]
    smp = Image.new("RGBA", (lg.shape[1] * 8, lg.shape[0] * 8), (225, 225, 225, 255))
    smp.alpha_composite(Image.fromarray(np.repeat(np.repeat(lg, 8, 0), 8, 1)))
    smp.convert("RGB").save(os.path.join(out, "3_legs_sample.png"))
    work = out + "_work"
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ", "Quinn",
           "--hq", "--mirror", "--yaw", "60", "--size", "500", "--no-labels", "--name", "poses", "--out", work,
           "--frame", "Quinn_Spell4_Channel@250", "--frame", "Quinn_Spell4_Channel@1250", "--frame", "quinn_spell1@350",
           "--frame", "Quinn_attack1@120", "--frame", "Quinn_spell3_flip@100", "--frame", "Quinn_idle1@0"]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.copyfile(os.path.join(work, "poses.png"), os.path.join(out, "4_poses_lol.png"))
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ", "Quinn",
           "--anim", "Quinn_run", "--frames", "8", "--t1", "0.9", "--mirror", "--yaw", "60", "--size", "400",
           "--no-labels", "--out", work]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.copyfile(os.path.join(work, "Quinn_run.png"), os.path.join(out, "5_run_lol.png"))
    shutil.copyfile(lp(os.path.join(SRC, "LEG_PROMPTS_2.md")), os.path.join(out, "LEG_PROMPTS_2.md"))
    print(shutil.make_archive(out, "zip", out))
    for n in names:
        print(n, "drop", round(P[n][0], 2), "near", [tuple(round(v, 1) for v in p) for p in P[n][1]],
              "far", [tuple(round(v, 1) for v in p) for p in P[n][2]])


if __name__ == "__main__":
    main()
