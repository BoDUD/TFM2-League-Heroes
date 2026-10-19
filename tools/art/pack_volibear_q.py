#!/usr/bin/env python3
"""Volibear's Q pack for Codex (assets/source/volibear/Q_PROMPTS.md): Thundering Smash as League plays it - the charge on
all fours (Volibear_spell1_run) and the pounce that rears up and slams down onto all fours (Volibear_spell1_attack_
stationary).

    python tools/art/pack_volibear_q.py [--out %TEMP%/vb_work/volibear_q_pack] [--lol D:/WeGameApps/lol]

Why (2026-10-19): the user, 「Q技能的释放技能姿势和英雄联盟不一样？」 - our Q charged with the upright walk and smashed with R's
both-arms-up rear and a forward thrust; League's runs on all fours and lands on all fours. The design stands on two
legs, so the four-legged poses are Codex's (the user: 「你改不好就让codex帮忙」).
Writes <out>/ (and <out>.zip): Q_PROMPTS.md;
  1_动作骨架_奈德丽豹形态跑步.png: league_nidalee's cougar run (hd_c_run, 8 frames, this pack's own art) on green, scaled
    so its body is BEAR_LEN of our squares long - the four-legged skeleton for the charge;
  2_角色_沃利贝尔定稿.png: the design in the same square size; 3_英雄联盟_Q冲锋.png: League's spell1_run (6 frames);
  4_英雄联盟_Q扑砸.png: League's spell1_attack_stationary (6 frames); 5_扑砸格子.png: five empty green cells of the
  charge's size with the ground line, for the pounce.
League's renders stay local (never committed).
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
import ppu_rig as R  # noqa: E402

lp = R.lp
SRC = os.path.join(ROOT, "assets", "source", "volibear")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "vb_work")
Z = 6                     # screen px a square
CW, CH = 84, 60           # a cell in our squares
FEET = 56                 # the soles' row inside a cell
BEAR_LEN = 62             # the bear on all fours, nose to rump, in our squares (standing he is 54 tall, 51 wide)
KEY = (0, 255, 0)
GREY = (225, 225, 225)


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def on_key(a):
    out = np.zeros(a.shape[:2] + (3,), np.uint8)
    out[:] = KEY
    m = a[..., 3] > 0
    out[m] = a[m][:, :3]
    return out


def sheet_cells(frames, cols):
    rows = -(-len(frames) // cols)
    sheet = np.zeros((rows * CH, cols * CW, 4), np.uint8)
    for n, a in enumerate(frames):
        h, w = a.shape[:2]
        Y, X = (n // cols) * CH + FEET - h + 1, (n % cols) * CW + (CW - w) // 2
        y0 = max(Y, (n // cols) * CH)
        a = a[y0 - Y:]
        m = a[..., 3] > 0
        sheet[y0:y0 + a.shape[0], X:X + w][m] = a[m]
    return sheet


def lol_strip(lol, clip, times, out, name):
    work = os.path.join(out, "_r")
    os.makedirs(work, exist_ok=True)
    tiles = []
    for t in times:
        cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Volibear",
               "--hq", "--mirror", "--hide-submeshes", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size",
               "900", "--fit", "0.3", "--ground", "0.9", "--width", "1.4", "--yaw", "55", "--name", "f", "--out", work,
               "--frame", f"{clip}@{t}"]
        subprocess.run(cmd, check=True, capture_output=True)
        tiles.append(Image.open(os.path.join(work, "f.png")).convert("RGB"))
    shutil.rmtree(work)
    # one crop box for all (the motion stays readable), then side by side
    boxes = []
    for im in tiles:
        a = np.asarray(im).astype(int)
        ys, xs = np.nonzero(np.abs(a - GREY).sum(-1) > 12)
        boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    x0 = min(b[0] for b in boxes) - 20
    y0 = min(b[1] for b in boxes) - 20
    x1 = max(b[2] for b in boxes) + 20
    y1 = max(b[3] for b in boxes) + 20
    crops = [im.crop((x0, y0, x1, y1)) for im in tiles]
    w, h = crops[0].size
    strip = Image.new("RGB", (w * len(crops) + 8 * (len(crops) - 1), h + 20), (255, 255, 255))
    d = ImageDraw.Draw(strip)
    for i, c in enumerate(crops):
        strip.paste(c, (i * (w + 8), 20))
        d.text((i * (w + 8) + 4, 4), f"{i + 1}  ({times[i]} ms)", fill=(40, 40, 40))
    strip.save(os.path.join(out, name))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "volibear_q_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    # the dense cougar run (hd_ tags are left out of sheet_of: read them straight)
    import json
    stem = os.path.join(R.MOD, "champions", "league_nidalee")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    px = np.asarray(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    run = []
    for f_ in anims["hd_c_run"]["frames"]:
        d = f_["data"]
        x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
        run.append(px[y:y + h, x:x + w].copy())
    crops = []
    for f in run:                                     # (the frames' cells differ in size: each cropped to itself)
        ys, xs = np.nonzero(f[..., 3] > 0)
        crops.append(f[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    k = BEAR_LEN / max(c.shape[1] for c in crops)
    frames = [np.asarray(Image.fromarray(c).resize((round(c.shape[1] * k), round(c.shape[0] * k)), Image.NEAREST))
              for c in crops]
    sheet = sheet_cells(frames, 4)
    Image.fromarray(up(on_key(sheet), Z)).save(os.path.join(out, "1_动作骨架_奈德丽豹形态跑步.png"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelB.png"))).convert("RGBA"))
    cell = np.zeros((CH, CW, 4), np.uint8)
    dy = max(0, FEET - d.shape[0] + 1)
    dd = d[d.shape[0] - (FEET + 1 - dy):]
    cell[dy:dy + dd.shape[0], (CW - d.shape[1]) // 2:(CW - d.shape[1]) // 2 + d.shape[1]] = dd
    Image.fromarray(up(on_key(cell), Z)).save(os.path.join(out, "2_角色_沃利贝尔定稿.png"))
    lol_strip(a.lol, "Volibear_spell1_run", [0, 111, 222, 333, 444, 556], out, "3_英雄联盟_Q冲锋.png")
    lol_strip(a.lol, "Volibear_spell1_attack_stationary", [0, 80, 160, 240, 320, 420], out, "4_英雄联盟_Q扑砸.png")
    empty = np.zeros((CH, 5 * CW, 4), np.uint8)
    g = Image.fromarray(up(on_key(empty), Z))
    dr = ImageDraw.Draw(g)
    for i in range(5):
        dr.rectangle([i * CW * Z, 0, (i + 1) * CW * Z - 1, CH * Z - 1], outline=(0, 160, 0))
        dr.text((i * CW * Z + 8, 8), str(i + 1), fill=(0, 90, 0))
    dr.line([(0, (FEET + 1) * Z), (5 * CW * Z, (FEET + 1) * Z)], fill=(230, 40, 40), width=2)
    g.save(os.path.join(out, "5_扑砸格子.png"))
    shutil.copyfile(lp(os.path.join(SRC, "Q_PROMPTS.md")), os.path.join(out, "Q_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("cougar scale", round(k, 3), "run frames", [f.shape[:2] for f in frames][:2], "->", zp)


if __name__ == "__main__":
    main()
