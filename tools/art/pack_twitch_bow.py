#!/usr/bin/env python3
"""图奇跑步的弩让 Codex 照设计图的长度重画（用户 2026-11-22：「让 Codex 重画弩」）。

Codex 交的跑步（assets/source/twitch/codex_run/run_1.png、run_2.png）别的都对，弩却画短了：把设计图按护目镜对到第 2、3、7 帧上，
头完全重合，弩尖比设计图的短 9-11 格（设计图的弩从握弩的手到弩尖约 55 格，Codex 的约 45 格）。这个包只改弩：

- 模板就是 Codex 自己交的两张图，每格里加蓝色标记：一根竖线是弩尖该到的地方（它现在弩尖往右 TIP_MORE 格），一条横线从它现在的弩尖
  连过去；
- 参考图：设计图 8 倍、设计图的弩单独放大（BOW_POLY：连握弩的手和弩上的绿药罐）、第 3 帧叠上设计图弩的轮廓（短了多少一眼看出）。

    python tools/art/pack_twitch_bow.py --out <pack>

写出 <pack>/（templates/、refs/）和旁边的 twitch_bow_pack.zip（提示词 assets/source/twitch/RUN_BOW_PROMPT.md 一起放进去）。
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_twitch_run as PR  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "twitch")
CODEX = os.path.join(SRC, "codex_run")
SQ, CELL = PR.SQ, PR.CELL
TIP_MORE = 10                            # 弩尖要再往右几格
BLUE = (0, 120, 255, 255)


def marked(name):
    """Codex 交的一张图（2 x 2 格），每格画上弩尖该到的蓝竖线和从现在弩尖连过去的蓝横线。"""
    im = Image.open(os.path.join(CODEX, name)).convert("RGBA")
    a = np.array(im)
    d = ImageDraw.Draw(im)
    for k in range(4):
        x0, y0 = (k % 2) * CELL[0], (k // 2) * CELL[1]
        op = a[y0:y0 + CELL[1]:SQ, x0:x0 + CELL[0]:SQ, 3] > 0
        ys, xs = np.nonzero(op)
        tip = xs.max()
        rows = np.nonzero(op[:, tip - 2:tip + 1].any(1))[0]
        r0, r1 = rows.min(), rows.max()
        to = tip + TIP_MORE
        cx = x0 + to * SQ + SQ // 2
        d.rectangle([cx - 3, y0 + (r0 - 4) * SQ, cx + 3, y0 + (r1 + 5) * SQ], fill=BLUE)
        mid = y0 + ((r0 + r1) // 2) * SQ + SQ // 2
        for x in range(x0 + (tip + 1) * SQ, cx - 3, 12):
            d.line([(x, mid), (min(x + 6, cx - 4), mid)], fill=BLUE, width=3)
    return im


def bow_crop(d):
    """设计图的弩（BOW_POLY：连握弩的手和绿药罐）单独放大 8 倍，白底，外面一圈留白；头那块（下巴的牙）不要，
    贴着下巴的绿药罐留着。"""
    r, g, b = (d[..., i].astype(int) for i in range(3))
    green = (g > r + 30) & (g > b)
    m = PR.poly(PR.BOW_POLY, d.shape) & ~(PR.poly(PR.HEAD_POLY, d.shape) & ~green) & (d[..., 3] > 0)
    out = np.zeros_like(d)
    out[m] = d[m]
    ys, xs = np.nonzero(m)
    c = out[ys.min() - 2:ys.max() + 3, xs.min() - 2:xs.max() + 3]
    return PR.on(Image.fromarray(c), SQ)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--overlay", required=True, help="第 3 帧叠设计图弩轮廓的那张图")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "templates"))
    os.makedirs(os.path.join(out, "refs"))
    for name in ("run_1.png", "run_2.png"):
        marked(name).save(os.path.join(out, "templates", name))
    d = np.array(Image.open(PR.DESIGN).convert("RGBA"))
    PR.on(Image.fromarray(d), SQ).save(os.path.join(out, "refs", "1_twitch_design_8x.png"))
    bow_crop(d).save(os.path.join(out, "refs", "2_crossbow_design_8x.png"))
    shutil.copy(a.overlay, os.path.join(out, "refs", "3_crossbow_too_short_frame3.png"))
    prompt = os.path.join(SRC, "RUN_BOW_PROMPT.md")
    if os.path.isfile(prompt):
        shutil.copy(prompt, os.path.join(out, "RUN_BOW_PROMPT.md"))
    zp = shutil.make_archive(os.path.join(os.path.dirname(os.path.abspath(out)), "twitch_bow_pack"), "zip", out)
    print("pack:", out, "zip:", zp)


if __name__ == "__main__":
    main()
