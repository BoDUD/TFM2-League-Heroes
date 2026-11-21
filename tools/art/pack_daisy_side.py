#!/usr/bin/env python3
"""小菊四分之三侧面的 GPT 图包（用户 2026-11-21：「小菊做成召唤物的话 行走动作也没做 都要补」「起码像安妮的熊那样吧
方向也不对」）：小菊现在只有正面的图，当召唤物走起来不转身。请 GPT 照正面定稿画同一个小菊的四分之三侧面朝右，再按英雄
联盟原版的动作画 14 个姿势（提示词 assets/source/ivern/DAISY_SIDE_PROMPTS.md）。

    python tools/art/pack_daisy_side.py [--league D:/TFM2-Workshop/px3d_local/daisy/pack] [--out <dir>]

图包里：
  0_daisy_front.png      正面定稿 assets/source/ivern/hd/daisy.png，每格 12 px 放在 1254 画布上，脚底 y 1200（和上一轮
                         POSE_PROMPTS 的 D0 一样）；
  1_tibbers_example.png  我们游戏里安妮的熊（league_annie_tibbers 单位图：站、走、挥爪），每格 8 px：召唤物就是这样朝右画的；
  B_<nn>_<pose>_league.png 英雄联盟原版小菊那一帧，tools/lol/pose_ref.py 渲染（--champ IvernMinion --wad Ivern --hq
                         --no-labels，默认的四分之三侧面朝右）。原版的图只在本地，不进仓库：--league 指向渲染好的目录；
  DAISY_SIDE_PROMPTS.md  提示词。
打成 <out>/daisy_side_pack.zip，提示词另放一份在旁边（发给用户时两样都附上）。
"""
import argparse
import json
import os
import shutil
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DESIGN = os.path.join(ROOT, "assets", "source", "ivern", "hd", "daisy.png")
PROMPTS = os.path.join(ROOT, "assets", "source", "ivern", "DAISY_SIDE_PROMPTS.md")
TIBBERS = os.path.join(ROOT, "league", "champions", "league_annie_tibbers")

CANVAS, SQ, SOLES = 1254, 12, 1200
# 姿势编号和原版那一帧（第 9 挨打、第 12 挥手原版没有）
POSES = [(0, "idle"), (1, "walk1"), (2, "walk2"), (3, "walk3"), (4, "walk4"), (5, "punch_up"), (6, "punch_down"),
         (7, "slam_up"), (8, "slam"), (10, "fall"), (11, "land"), (13, "slump"), (14, "crumble")]


def front_design():
    """正面定稿：每格 12 px，左右居中，脚底在 y 1200。"""
    d = Image.open(DESIGN).convert("RGBA")
    a = np.asarray(d)[..., 3] > 0
    ys, xs = np.nonzero(a)
    d = d.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    big = d.resize((d.width * SQ, d.height * SQ), Image.NEAREST)
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = (CANVAS - big.width) // 2 // SQ * SQ
    out.alpha_composite(big, (x, SOLES - big.height))
    return out


def tibbers_example():
    """安妮的熊的单位图：站一帧、走六帧、挥爪两帧，每格 8 px，浅底，脚底对齐。"""
    sheet = Image.open(TIBBERS + "#sheet.png").convert("RGBA")
    anims = json.loads(open(TIBBERS + "#anim.fanim", "rb").read().decode("utf-8-sig"))["anims"]
    cells = []
    for tag, picks in (("idle", [0]), ("run", range(6)), ("attack", [1, 2])):
        for i in picks:
            f = anims[tag]["frames"][i]["data"]
            x, y, w, h = (int(f[k]) for k in ("x", "y", "w", "h"))
            cells.append(sheet.crop((x, y, x + w, y + h)))
    k, gap = 8, 16
    H = max(c.height for c in cells) * k
    W = sum(c.width * k + gap for c in cells) + gap
    out = Image.new("RGBA", (W, H + 2 * gap), (225, 225, 225, 255))
    x = gap
    for c in cells:
        big = c.resize((c.width * k, c.height * k), Image.NEAREST)
        out.alpha_composite(big, (x, gap + H - big.height))
        x += big.width + gap
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--league", default="D:/TFM2-Workshop/px3d_local/daisy/pack",
                    help="pose_ref 渲染好的 league_<姿势>.png 所在目录（本地，不进仓库）")
    ap.add_argument("--out", default="D:/TFM2-Workshop/codex_packs/daisy_side")
    args = ap.parse_args()
    work = os.path.join(args.out, "pack")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    front_design().save(os.path.join(work, "0_daisy_front.png"))
    tibbers_example().save(os.path.join(work, "1_tibbers_example.png"))
    for n, pose in POSES:
        src = os.path.join(args.league, f"league_{pose}.png")
        if not os.path.exists(src):
            raise SystemExit(f"缺原版那一帧：{src}（先用 tools/lol/pose_ref.py 渲染）")
        shutil.copyfile(src, os.path.join(work, f"B_{n:02d}_{pose}_league.png"))
    shutil.copyfile(PROMPTS, os.path.join(work, "DAISY_SIDE_PROMPTS.md"))
    zpath = os.path.join(args.out, "daisy_side_pack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(os.listdir(work)):
            z.write(os.path.join(work, name), name)
    shutil.copyfile(PROMPTS, os.path.join(args.out, "小菊侧面_提示词.md"))
    print(f"{zpath}: {len(os.listdir(work))} files")


if __name__ == "__main__":
    main()
