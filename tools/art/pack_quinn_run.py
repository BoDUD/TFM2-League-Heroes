#!/usr/bin/env python3
"""Quinn run skin-swap pack for Codex (league_akshan's accepted way, tools/art/pack_akshan_run.py: a caped marksman's run
= Codex's skin swap over an approved run). My rig walk (the design's legs stepped whole, tools/art/rig_quinn.walk) had no
crossing step: the idle's legs stand apart in a 3/4 stance and cannot cross from their own squares (memory
run-legs-caitlyn-way, akshan: 「走路没交叉步啊」).

    python tools/art/pack_quinn_run.py [--out %TEMP%/qn_work/quinn_run_pack] [--lol D:/WeGameApps/lol]

Image 1 = this pack's league_akshan run (hd_run, 7 frames: the cape thrown back, a scissor stride, the body bobbing; the
user accepted it 2026-10-18), on a green key, Z x; image 2 = Quinn's approved idle (the skin, the one face), same cell and
scale; image 3 = her approved side view (the body seen side-on); image 4 = League's own Quinn run (pose_ref, Riot's
model: kept local). A short Chinese prompt. Akshan's frames are drawn 1:1 (his run is 52 rows hair to soles, hers 49).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_quinn_hd import lp  # noqa: E402

CHAMPS = os.path.join(ROOT, "league", "champions")
SRC = os.path.join(ROOT, "assets", "source", "quinn", "hd")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "qn_work")
Z = 6
CW, CH = 64, 62                  # a cell in squares
FEET = 59                        # the soles' row inside a cell
KEY = (0, 255, 0)

PROMPT = """# 奎因 跑步 换皮（骨架 + 皮囊）

**用画图模型（image_gen）画。**上传顺序：图1 = `1_动作骨架_阿克尚跑步.png`，图2 = `2_角色_奎因定稿.png`，图3 = `3_奎因侧面定稿.png`，图4 = `4_英雄联盟奎因跑步.png`（只看动作）。

---

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（德玛西亚之翼 奎因）。

1. 保留图1所有帧的位置、大小、排列顺序：横排 7 帧，从左到右；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作：披风往身后飘开，两条腿露在披风前面，**一前一后交叉迈步（剪刀步）**，往后收的腿弯膝、鞋跟抬起，两腿每半圈换一次前后；身体上下起伏、稍微前倾（图4 是英雄联盟原版的跑步，可以对照）。
3. 身体结构、配色、特征完全换成图2：金色鹰翼面甲（两边往上翘的翼尖）、深蓝兜帽、面甲下的深紫色头发、琥珀色眼睛、红嘴唇；近侧的大块金色羽毛肩甲、棕色皮革胸甲和皮带、深紫蓝作战服、腰两侧金边的羽毛护甲片、背后蓝紫色的羽毛披风（随步子往后飘）、银灰手套、深紫色护腿、膝盖和小腿前面的金色护板、尖头深棕靴子（图3 是她的侧面，可以对照身体侧过来的样子）。
4. 头：**和图2 完全一样**（同一张脸、同样的面甲和兜帽、同样的格子），跟着身体上下动，不要转成侧脸，不要变大变小。
5. 手：**绑着连弩的右手臂和图2 一样朝前（朝右）平端着连弩**，连弩的大小、颜色、横着的弩臂和图2 完全一样，跟着身体上下动，不要变形；另一只手握拳随步子前后摆。**图1 举在头边的枪不要画**。
6. 体型和图2一样大（头盔尖到鞋底 49 格），头和身体比例和图2 一样，不要变大变小、变胖变瘦；两条腿的颜色一样（护腿、靴子都和图2 一样），远处那条腿可以暗一档。
7. 像素画：方块大小和图2 一样（每个像素方块一样大，整齐对格），1 格深色描边，不要抗锯齿、不要渐变、不要模糊。

背景保持纯绿色 #00FF00（和角色差异最大的纯色），方便抠图。风格保持与原图一致。重点在于精准复刻原图的"动作骨架"，只是换了"皮囊"。

交付：7 帧的整张图（和图1一样横排、一样大小），放在 `outputs/quinn-run/`，原始生成图放 `raw/`，附 `generation-prompts.txt`，**最后**写 `HANDOFF.md`，再打包成 `outputs/quinn_run_done.zip`。可以画两稿。
"""


def frames(hero, tag):
    anims = json.load(open(lp(os.path.join(CHAMPS, f"league_{hero}#anim.fanim")), encoding="utf-8-sig"))["anims"]
    sheet = Image.open(lp(os.path.join(CHAMPS, f"league_{hero}#sheet.png"))).convert("RGBA")
    out = []
    for f in anims[tag]["frames"]:
        d = f["data"]
        im = sheet.crop((int(d["x"]), int(d["y"]), int(d["x"] + d["w"]), int(d["y"] + d["h"])))
        out.append(np.asarray(im))
    return out


def soles(a):
    return np.nonzero(a[..., 3].any(1))[0].max()


def in_cell(a, ground):
    """a's squares in a CW x CH cell: its row `ground` on FEET, centred."""
    cell = np.zeros((CH, CW, 4), np.uint8)
    xs = np.nonzero(a[..., 3].any(0))[0]
    mid = (xs.min() + xs.max() + 1) // 2
    for y in range(a.shape[0]):
        Y = FEET - ground + y
        if 0 <= Y < CH:
            for x in range(a.shape[1]):
                X = CW // 2 - mid + x
                if 0 <= X < CW and a[y, x, 3]:
                    cell[Y, X] = a[y, x]
    return cell


def keyed(a):
    out = np.zeros(a.shape[:2] + (3,), np.uint8)
    out[:] = KEY
    m = a[..., 3] > 0
    out[m] = a[m][:, :3]
    return Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "quinn_run_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    run = frames("akshan", "hd_run")
    strip = np.concatenate([in_cell(f, soles(f)) for f in run], axis=1)
    keyed(strip).save(os.path.join(out, "1_动作骨架_阿克尚跑步.png"))
    for src, dst in (("idle.png", "2_角色_奎因定稿.png"), ("side.png", "3_奎因侧面定稿.png")):
        d = np.asarray(Image.open(lp(os.path.join(SRC, src))).convert("RGBA"))
        keyed(in_cell(d, soles(d))).save(os.path.join(out, dst))
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", a.lol, "--champ", "Quinn",
           "--anim", "Quinn_run", "--frames", "7", "--t1", "0.9", "--mirror", "--yaw", "60", "--size", "360",
           "--no-labels", "--out", out + "_work"]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.copyfile(os.path.join(out + "_work", "Quinn_run.png"), os.path.join(out, "4_英雄联盟奎因跑步.png"))
    with open(os.path.join(out, "PROMPT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(PROMPT)
    zp = shutil.make_archive(out, "zip", out)
    print(zp, "strip", strip.shape[:2], "x", Z)


if __name__ == "__main__":
    main()
