#!/usr/bin/env python3
"""Cho'Gath's pose pack for Codex (assets/source/chogath/POSE_PROMPTS.md): the poses his actions need that the side
design cannot give by whole-square moves - League rears him up on his hind legs and slams him down in the attack, E's
spikes, Q, W and R, and lays him on his side in the death.

    python tools/art/pack_chogath_poses.py [--out %TEMP%/cg_work/chogath_pose_pack] [--lol D:/WeGameApps/lol]
    python tools/art/pack_chogath_poses.py --redo     # round 2: rise, rear, slam thicker (%TEMP%/cg_work/chogath_pose_pack2)

Every pose is ONE 1254 picture at 16 px a square, soles on y 1120 - the grid of the step-1 redraws, which came back on
the count (side redraw 2026-10-19). Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the
approved side design on that grid with its own skeleton drawn over it: what each line stands for); 1_idle_head.png (the
idle's head, 8x: every pose wears it); 2_side_design.png (the side design on the grid, clean); per pose
p<k>_<name>_skeleton.png (the grid, the ground, the skeleton at the design's own segment lengths and a grey box where
the head goes) and p<k>_<name>_league.png (League's frame for it, side-on: the pose to copy; Riot's, kept local).
Skeleton colours: green = spine and tail, thin dark green = the back (the carapace's top; the scythes grow from its
front end), red = the NEAR legs (in front, full tone), blue = the FAR legs (behind,
darker), orange = the NEAR scythe arm, purple = the FAR scythe arm; grey box = the head (idle head, never redrawn).
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
from design_chogath_hd import lp  # noqa: E402
from pack_chogath_model import CANVAS, GREY, PX, SOLE_Y, TMP  # noqa: E402
from pack_chogath_side import HEAD  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "chogath")
GROUND = SOLE_Y // PX - 1          # the soles' row on the canvas grid (69)
DX, DY = 3, GROUND - 44            # the side design's (0, 0) on the canvas grid (its soles on row 44)
COL = {"spine": (0, 170, 60), "near": (230, 30, 30), "far": (40, 90, 230), "near_s": (255, 140, 0),
       "far_s": (150, 60, 200)}
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 24 x 21 squares

# the side design's skeleton, design squares (x, y): measured on hd/side.png (71 x 45)
REST = {
    "spine": [(24, 28), (27, 31), (50, 30)],
    "tail": [(24, 28), (12, 27), (1, 25)],
    "near_hind": [(27, 32), (30, 38), (27, 44)], "far_hind": [(24, 32), (24, 38), (21, 44)],
    "near_front": [(54, 33), (58, 38), (60, 44)], "far_front": [(50, 33), (47, 38), (49, 44)],
    "near_s": [(47, 12), (56, 4), (62, 2), (69, 17)], "far_s": [(40, 13), (46, 6), (51, 6), (56, 14)],
    "head": (56, 30),
}
# the poses, canvas squares (soles on row 69); League's frame for each (clip, ms) and what it is for
POSES = {
    "crouch": (dict(spine=[(24, 57), (27, 60), (49, 59)], tail=[(24, 57), (12, 58), (2, 55)],
                    near_hind=[(27, 60), (31, 64), (28, 69)], far_hind=[(24, 60), (23, 64), (21, 69)],
                    near_front=[(51, 61), (55, 64), (57, 69)], far_front=[(47, 61), (44, 65), (46, 69)],
                    near_s=[(44, 41), (48, 31), (41, 28), (33, 36)], far_s=[(38, 42), (40, 34), (34, 32), (28, 39)],
                    head=(54, 60)),
               ("chogath_attack2", 150), "蓄力：身子压低、头往回缩、两条镰刀臂往后拉"),
    "rise": (dict(spine=[(30, 54), (32, 55), (46, 40)], tail=[(30, 54), (18, 60), (5, 62)],
                  near_hind=[(32, 55), (36, 62), (33, 69)], far_hind=[(29, 55), (28, 62), (26, 69)],
                  near_front=[(47, 43), (52, 47), (55, 44)], far_front=[(44, 44), (48, 49), (51, 47)],
                  near_s=[(40, 38), (48, 22), (56, 16), (64, 26)], far_s=[(37, 40), (36, 24), (30, 16), (24, 22)],
                  head=(52, 34)),
             ("chogath_attack2", 250), "半起身：后腿撑地、上身斜着抬起来、前爪离地、镰刀臂举高"),
    "rear": (dict(spine=[(32, 54), (34, 52), (37, 30)], tail=[(32, 54), (20, 62), (6, 66)],
                  near_hind=[(35, 52), (40, 60), (37, 69)], far_hind=[(32, 52), (30, 60), (31, 69)],
                  near_front=[(39, 33), (46, 37), (50, 31)], far_front=[(36, 33), (42, 38), (46, 34)],
                  near_s=[(22, 28), (28, 14), (36, 6), (46, 8)], far_s=[(19, 29), (12, 16), (6, 8), (2, 14)],
                  head=(44, 24), abs_s=True),
             ("chogath_attack2", 400), "直立：只用后腿站着、身子竖直、前爪抬在胸前、两条镰刀臂高高举起张开"),
    "slam": (dict(spine=[(26, 48), (28, 50), (50, 58)], tail=[(26, 48), (16, 40), (8, 32)],
                  near_hind=[(29, 51), (27, 60), (24, 69)], far_hind=[(26, 51), (22, 60), (20, 69)],
                  near_front=[(51, 59), (58, 62), (64, 69)], far_front=[(48, 60), (52, 65), (56, 69)],
                  near_s=[(55, 44), (64, 36), (72, 40), (76, 52)], far_s=[(52, 45), (58, 37), (66, 38), (71, 47)],
                  head=(61, 59), abs_s=True),
             ("chogath_attack2", 504), "下砸：整个身子往前扑下去、头和前爪砸到地面、后腿往后蹬直、尾巴翘起、镰刀臂往前下方劈"),
    "lunge": (dict(spine=[(25, 52), (28, 54), (52, 50)], tail=[(25, 52), (12, 52), (2, 48)],
                   near_hind=[(28, 54), (26, 62), (22, 69)], far_hind=[(26, 54), (29, 62), (26, 69)],
                   near_front=[(53, 53), (60, 56), (66, 58)], far_front=[(50, 54), (56, 59), (61, 62)],
                   near_s=[(46, 42), (52, 30), (46, 24), (38, 30)], far_s=[(42, 43), (46, 32), (40, 27), (33, 33)],
                   head=(64, 46)),
              ("chogath_spell2", 167), "扑咬：身子往前伸长、头往前探到半空、大嘴张到最大、前爪往前抓、后腿蹬地"),
    "fall": (dict(spine=[(27, 58), (30, 61), (50, 62)], tail=[(27, 58), (15, 62), (3, 64)],
                  near_hind=[(31, 61), (35, 64), (32, 69)], far_hind=[(28, 61), (27, 65), (25, 69)],
                  near_front=[(52, 62), (55, 66), (59, 69)], far_front=[(49, 62), (48, 66), (51, 69)],
                  near_s=[(44, 48), (50, 40), (42, 40), (34, 48)], far_s=[(40, 50), (44, 42), (36, 44), (30, 52)],
                  head=(58, 59)),
             ("chogath_death", 600), "瘫倒：四条腿都软下去、肚子贴近地面、头垂到地上、镰刀臂往后耷拉"),
    "lie": (dict(spine=[(22, 62), (24, 62), (48, 62)], tail=[(22, 62), (10, 66), (0, 67)],
                 near_hind=[(26, 63), (32, 66), (38, 68)], far_hind=[(24, 62), (30, 63), (36, 64)],
                 near_front=[(47, 63), (53, 66), (56, 69)], far_front=[(45, 62), (50, 63), (54, 64)],
                 near_s=[(36, 56), (30, 52), (22, 56), (14, 62)], far_s=[(40, 56), (34, 50), (26, 52), (18, 58)],
                 head=(60, 59)),
            ("chogath_death", 2000), "侧躺：整个身子侧着躺在地上（肚子朝外）、四条腿软软地伸出来、尾巴平放、镰刀臂瘫在背后的地上"),
}


def canvas_grid():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def c(p):
    """A square's middle on the canvas in px."""
    return ((p[0] + 0.5) * PX, (p[1] + 0.5) * PX)


BACK = 15                          # the carapace's top above the spine line, squares (side design: spine ~row 30, back ~15)


def with_back(sk):
    """The pose with its back line (the carapace's top: the spine moved BACK squares to the body's upper side) and both
    scythe arms moved whole so they grow from the back's front end (the near one there, the far one 3 squares behind)."""
    (hx, hy), (sx, sy) = sk["spine"][-2], sk["spine"][-1]
    vx, vy = sx - hx, sy - hy
    n = (vx * vx + vy * vy) ** 0.5
    nx, ny = vy / n, -vx / n
    back = [(hx + nx * BACK, hy + ny * BACK), (sx + nx * BACK, sy + ny * BACK)]
    out = dict(sk, back=back)
    if sk.get("abs_s"):                # placed by hand from the back's front end (kept off the head and the canvas edge)
        return out
    for name, behind in (("near_s", 0), ("far_s", 3)):
        rx, ry = back[1][0] - vx / n * behind, back[1][1] - vy / n * behind
        x0, y0 = sk[name][0]
        out[name] = [(x + rx - x0, y + ry - y0) for x, y in sk[name]]
    return out


def skeleton(can, sk, label, alpha=255):
    sk = with_back(sk)
    dr = ImageDraw.Draw(can, "RGBA")
    hx, hy = sk["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    pts = [c(p) for p in sk["back"]]
    dr.line(pts, fill=(0, 110, 40, alpha), width=4)
    for name, key in (("far_s", "far_s"), ("far_hind", "far"), ("far_front", "far"), ("tail", "spine"),
                      ("spine", "spine"), ("near_hind", "near"), ("near_front", "near"), ("near_s", "near_s")):
        pts = [c(p) for p in sk[name]]
        dr.line(pts, fill=COL[key] + (alpha,), width=7, joint="curve")
        for p in pts:
            dr.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=COL[key] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, clip, ms, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Chogath",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.3",
           "--ground", "0.8", "--width", "2.4", "--yaw", "80", "--name", "f", "--out", work,
           "--frame", f"{clip}@{ms}"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "chogath_pose_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    side = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "side.png"))).convert("RGBA"))
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    # the design and its own skeleton (design squares moved onto the canvas grid)
    rest = {k: ([(x + DX, y + DY) for x, y in v] if k != "head" else (v[0] + DX, v[1] + DY)) for k, v in REST.items()}
    base = canvas_grid()
    base.alpha_composite(on_grid(side, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved side design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_side_design.png"))
    r0, r1, c0, c1 = HEAD
    h = idle[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "1_idle_head.png"))
    for k, (name, (sk, (clip, ms), what)) in enumerate(POSES.items(), 3):
        can = canvas_grid()
        skeleton(can, sk, f"{k}: {name} - skeleton on the 16 px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, clip, ms, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, clip, ms)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__" and "--redo" not in sys.argv:
    main()


# ------------------------------------------------------------------------------------------------- round 2
REDO = ["rise", "rear", "slam"]


def redo(out):
    """Round 2 (assets/source/chogath/POSE_PROMPTS_2.md): rise, rear and slam came back with the hind legs thin and
    long and the upright torso slim next to the side design (read back at the side design's scale, 8x). Writes <out>/
    (and <out>.zip): POSE_PROMPTS_2.md, A_side_design_8x.png (the side design, 8x), B_idle_head.png, and per pose
    <name>_round1.png (Codex's round-1 picture: the pose to keep) and <name>_readback_8x.png (round 1 read back at
    the game's scale beside the side design, the same 8x: too thin)."""
    import design_chogath_poses as DP
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    side = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "side.png"))).convert("RGBA"))
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))

    def big(a, z=8):
        im = Image.fromarray(up(a, z))
        bg = Image.new("RGBA", im.size, GREY + (255,))
        bg.alpha_composite(im)
        return bg.convert("RGB")
    big(side).save(os.path.join(out, "A_side_design_8x.png"))
    r0, r1, c0, c1 = HEAD
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "B_idle_head.png"))
    for n in REDO:
        shutil.copyfile(lp(os.path.join(DP.SRC, f"chogath-pose-{n}.png")), os.path.join(out, f"{n}_round1.png"))
        fig = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"pose_{n}.png"))).convert("RGBA"))
        a, b = big(side), big(fig)
        can = Image.new("RGB", (a.width + b.width + 40, max(a.height, b.height) + 40), (255, 255, 255))
        can.paste(a, (0, can.height - a.height))
        can.paste(b, (a.width + 40, can.height - b.height))
        ImageDraw.Draw(can).text((8, 8), f"left: the approved side design   right: round-1 {n} at the same scale "
                                          "(hind legs too thin and long, body too slim)", fill=(30, 30, 30))
        can.save(os.path.join(out, f"{n}_readback_8x.png"))
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS_2.md")), os.path.join(out, "POSE_PROMPTS_2.md"))
    print(shutil.make_archive(out, "zip", out))


if __name__ == "__main__" and "--redo" in sys.argv:
    redo(os.path.join(TMP, "chogath_pose_pack2"))
