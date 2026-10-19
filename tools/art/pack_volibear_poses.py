#!/usr/bin/env python3
"""Volibear's pose pack for Codex (assets/source/volibear/POSE_PROMPTS.md): A) the approved front design with only the
arms drawn again in four poses on the design's exact grid; B) the walk as a skin swap over oppi's Alistar run.

    python tools/art/pack_volibear_poses.py [--out %TEMP%/vb_work/volibear_pose_pack] [--lol D:/WeGameApps/lol]

Why (2026-10-19): the design's arms hang huge beside the body; posed from its own squares a quarter-turned arm became
a horizontal log of fur (「左手严重变形」), moved whole it shrugged, mirrored top to bottom it still read wrong (「看了还是
奇怪 你改不好就让codex帮忙」); the walk moved each leg whole under the belly and never crossed (「走路也没交叉换步 腿看起来
都没变的」). Akshan / Gangplank's way: a limb pose the design lacks -> one Codex "same design, only these arms" picture
on the design's grid, the changed squares stamped (design_akshan_poses.py); a run with crossing steps -> Codex's skin
swap over an oppi run (pack_akshan_run.py; Alistar: the nearest hunched, heavy, bipedal beast in LoL Reborn).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md;
  A/1_design.png (the front design at PX px a square on the 1254 canvas, room above for raised arms and on the right
    for arms reaching forward), A/2_grid.png (the grid every 5 squares, ear-top and ground lines), A/3_arms_closeup.png
    (both arms at 10x), A/4a..4c_lol_*.png (League's poses), A/5_not_like_this.png (the rejected posings, 6x);
  B/1_动作骨架_oppi走路.png (oppi's Alistar run, 9 frames on green, scaled to our 54 rows), B/2_角色_沃利贝尔定稿.png (the
    design in the same cell), B/3_英雄联盟沃利贝尔跑步.png.
League's renders and oppi's frames are kept local, never committed.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import rig_volibear as V  # noqa: E402
import tfm2_ase as T  # noqa: E402

lp = V.lp
SRC = os.path.join(ROOT, "assets", "source", "volibear")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "vb_work")
OPPI = r"D:/steam/steamapps/workshop/content/3009300/3774304166/champions/alistair.aseprite"
PX = 15
CANVAS = 1254
X0, Y0 = 210, 330        # the design's (0, 0): 51 x 54 squares -> 765 x 810 px, soles on y 1140; 22 rows above for
                         # raised arms, 18 columns on the right for arms reaching forward
GREY = (225, 225, 225)
# League's poses: name -> (frame, yaw)
# (League has no clear both-arms-up frame: that pose is described in words, its arm shape from 4a)
POSES = {"4a_lol_one_arm_up.png": ("volibear_spell3@1000", 45),
         "4b_lol_rake.png": ("Volibear_Attack_1@300", 45),
         "4c_lol_maul.png": ("Volibear_Spell2_Slash@317", 45)}
Z = 6                    # B: screen px a square
CW, CH = 96, 74          # B: a cell in our squares
FEET = 70                # B: the soles' row inside a cell
BODY = 54                # our design: ear top to soles
KEY = (0, 255, 0)


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def on_canvas(d):
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(d, PX)), (X0, Y0))
    return can


def render(lol, frame, yaw, path):
    work = os.path.dirname(path)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Volibear", "--hq",
           "--mirror", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1400", "--fit",
           "0.45", "--ground", "0.88", "--width", "1.6", "--yaw", str(yaw), "--name", "r", "--out", work, "--frame",
           frame]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "r.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    m = np.abs(a - GREY).sum(-1) > 12
    ys, xs = np.nonzero(m)
    pad = 30
    im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), xs.max() + pad, ys.max() + pad)).save(path)
    os.remove(os.path.join(work, "r.png"))


def part_a(out, lol):
    os.makedirs(out)
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelB.png"))).convert("RGBA"))
    H, W = d.shape[:2]
    on_canvas(d).save(os.path.join(out, "1_design.png"))
    grid = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    grid.alpha_composite(on_canvas(d))
    dr = ImageDraw.Draw(grid)
    for c in range(-(X0 // PX), (CANVAS - X0) // PX + 1, 5):
        dr.line([(X0 + c * PX, 0), (X0 + c * PX, CANVAS)], fill=(205, 205, 205, 255))
    for r in range(-(Y0 // PX), (CANVAS - Y0) // PX + 1, 5):
        dr.line([(0, Y0 + r * PX), (CANVAS, Y0 + r * PX)], fill=(205, 205, 205, 255))
    dr.line([(0, Y0), (CANVAS, Y0)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, Y0 + H * PX), (CANVAS, Y0 + H * PX)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, CANVAS - 24), f"one square = {PX} px, {W} x {H} squares from x {X0}, y {Y0}; green = ear top y {Y0}, "
                               f"red = ground y {Y0 + H * PX}", fill=(40, 40, 40, 255))
    grid.convert("RGB").save(os.path.join(out, "2_grid.png"))
    D = V.front()
    tiles = []
    for k in ("near_arm", "far_arm"):
        m = D.parts[k]
        ys, xs = np.nonzero(m)
        sub = np.where(m[..., None], d, 0)[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
        bg = Image.new("RGBA", (sub.shape[1], sub.shape[0]), GREY + (255,))
        bg.alpha_composite(Image.fromarray(sub))
        tiles.append(bg.convert("RGB").resize((sub.shape[1] * 10, sub.shape[0] * 10), Image.NEAREST))
    sheet = Image.new("RGB", (tiles[0].width + tiles[1].width + 40, max(t.height for t in tiles)), (255, 255, 255))
    sheet.paste(tiles[0], (0, 0))
    sheet.paste(tiles[1], (tiles[0].width + 40, 0))
    sheet.save(os.path.join(out, "3_arms_closeup.png"))
    for name, (frame, yaw) in POSES.items():
        render(lol, frame, yaw, os.path.join(out, name))
    # the rejected posings: a quarter-turned arm (a log of fur), both arms turned forward, the arms moved whole up (a
    # shrug), the arms mirrored top to bottom
    F = V.Form()
    p = F.pose
    bad = [p(near_rot=3, near=(2, 2)), p(near_rot=1, near=(4, 7), near_back=True, far_rot=1, far=(-1, 5)),
           p(near=(-3, -6), near_back=True, far=(0, -6)), p(near_up=True, far_up=True, near_back=True, near=(2, 2))]
    bad = [F.rig.finish(c) for c in bad]
    allc = np.stack(bad)
    ys, xs = np.nonzero(allc[..., 3].max(0))
    y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    z = 6
    sheet = Image.new("RGB", ((x1 - x0) * z * len(bad) + 20 * (len(bad) - 1), (y1 - y0) * z), (255, 255, 255))
    for k, c in enumerate(bad):
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), GREY + (255,))
        bg.alpha_composite(Image.fromarray(c[y0:y1, x0:x1]))
        sheet.paste(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST),
                    (k * ((x1 - x0) * z + 20), 0))
    sheet.save(os.path.join(out, "5_not_like_this.png"))


def on_key(a):
    out = np.zeros(a.shape[:2] + (3,), np.uint8)
    out[:] = KEY
    m = a[..., 3] > 0
    out[m] = a[m][:, :3]
    return out


def part_b(out, lol):
    os.makedirs(out)
    s = T.load_sprite(OPPI)
    t = s.tag("run")
    run = [np.asarray(s.frames[i].convert("RGBA")) for i in range(t["frm"], t["to"] + 1)]
    idle = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    iy = np.nonzero(idle[..., 3].any(1))[0]
    k = BODY / (iy.max() - iy.min() + 1)
    soles = iy.max()
    allm = np.zeros(run[0].shape[:2], bool)
    for f in run:
        allm |= f[..., 3] > 0
    yy, xx = np.nonzero(allm)
    x0, x1, y0 = xx.min(), xx.max() + 1, yy.min()
    n_ = len(run)
    cols = 5
    rows = -(-n_ // cols)
    sheet = np.zeros((rows * CH, cols * CW, 4), np.uint8)
    for n, f in enumerate(run):
        crop = f[y0:soles + 1, x0:x1]
        im = Image.fromarray(crop).resize((round(crop.shape[1] * k), round(crop.shape[0] * k)), Image.NEAREST)
        a = np.asarray(im)
        h, w = a.shape[:2]
        Y, X = (n // cols) * CH + FEET - h + 1, (n % cols) * CW + (CW - w) // 2
        Y0_ = max(Y, (n // cols) * CH)
        a = a[Y0_ - Y:]
        m = a[..., 3] > 0
        sheet[Y0_:Y0_ + a.shape[0], X:X + w][m] = a[m]
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelB.png"))).convert("RGBA"))
    cell = np.zeros((CH, CW, 4), np.uint8)
    dy, dx = FEET - d.shape[0] + 1, (CW - d.shape[1]) // 2
    m = d[..., 3] > 0
    cell[dy:dy + d.shape[0], dx:dx + d.shape[1]][m] = d[m]
    Image.fromarray(up(on_key(sheet), Z)).save(os.path.join(out, "1_动作骨架_oppi走路.png"))
    Image.fromarray(up(on_key(cell), Z)).save(os.path.join(out, "2_角色_沃利贝尔定稿.png"))
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Volibear",
           "--anim", "volibear_run", "--frames", "8", "--hide-submeshes", "--mirror", "--yaw", "60", "--size", "300",
           "--out", out]
    subprocess.run(cmd, check=True, capture_output=True)
    os.replace(os.path.join(out, "volibear_run.png"), os.path.join(out, "3_英雄联盟沃利贝尔跑步.png"))
    print("B: oppi scale", round(k, 3), "frames", n_, "sheet", sheet.shape[:2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "volibear_pose_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    part_a(os.path.join(out, "A"), a.lol)
    part_b(os.path.join(out, "B"), a.lol)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("->", zp)


if __name__ == "__main__":
    main()
