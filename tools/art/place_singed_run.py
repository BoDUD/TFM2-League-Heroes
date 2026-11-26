#!/usr/bin/env python3
"""炼金跑步：读回、锁好脸的 8 帧（read_singed_run.py -> lock_singed_face.py，71 x 110 的画布）放成游戏里的高清帧：
57 x 106，中心是枢轴（站位点），踩地那几帧的鞋底落在待机的地面上（中心往下 16 行的上面一行）。

    python tools/art/place_singed_run.py --frames <lock_singed_face.py 的输出> --out <dir>

8 帧一起挪同样的距离，不一帧一帧对地面：Codex 画的腾空（第 5 帧离地 5 行）、身子的起伏都留着。之后
cross_singed_legs.py 排交叉步，singed_run_sheet.py 写进贴图表。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_singed_run as R  # noqa: E402

WF, HF = 57, 106                          # 高清帧：中心对站位点
SOLES = 90                                # 读回画布里踩地那几帧的鞋底行（Codex 把脚画在模板地面线下面约 10 格）
GROUND_F = HF // 2 + 16                   # 高清帧里地面所在的行（鞋底在它上面一行），和待机一样


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dx = int(round(WF / 2 - R.CX))        # 画布的列 -> 高清帧的列
    dy = (GROUND_F - 1) - SOLES           # 画布的行 -> 高清帧的行
    for k in range(1, 9):
        src = np.array(Image.open(os.path.join(a.frames, f"frame_{k}.png")).convert("RGBA"))
        out = np.zeros((HF, WF, 4), np.uint8)
        ys, xs = np.nonzero(src[..., 3] > 0)
        ny, nx = ys + dy, xs + dx
        if ny.min() < 0 or nx.min() < 0 or nx.max() >= WF or ny.max() >= HF:
            raise SystemExit(f"frame {k}: 放不进 {WF} x {HF}（行 {ny.min()}-{ny.max()}，列 {nx.min()}-{nx.max()}）")
        out[ny, nx] = src[ys, xs]
        Image.fromarray(out).save(os.path.join(a.out, f"frame_{k}.png"))
        print(f"frame {k}: rows {ny.min()}-{ny.max()} (ground row {GROUND_F}), cols {nx.min()}-{nx.max()}")


if __name__ == "__main__":
    main()
