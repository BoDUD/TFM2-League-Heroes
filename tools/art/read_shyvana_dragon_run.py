#!/usr/bin/env python3
"""龙女龙形态跑步的 Codex 重画读回来（用户 2026-11-22：「龙女变形的龙的跑步姿势也可以让codex重画一下 现在也很僵硬」
「codex交付了」）。

Codex 交了两版（assets/source/shyvana/codex_dragon_run/：用的是第二版 run_1.png、run_2.png，raw_v2.png 是它生成的原图）。
两张都和模板一样：2048 x 1920，2 x 2 格，每格 1024 x 960，每个 8 x 8 块都是一个颜色、对齐模板的网格，透明度只有 0 / 255。
所以这里不用猜网格：

1. 每格每 8 像素取一个点，得到 128 x 120 格的一帧（设计图的一格）；
2. 每格的颜色换成设计图（assets/source/shyvana/hd/d_idle.png）里最接近的那个；
3. 放进 rig_shyvana.py 的画布：模板的十字（第 64 列、第 60 行）就是站位点，地面线在它下面 17 格（第 77 行），所以格子
   (x, y) 放到画布 (x - 64 + CX, y - 77 + GY)，帧和帧之间的上下原样保留；
4. 每帧整帧左右平移 STEADY 格（见下），身子的前后晃收到英雄联盟那么大；
5. 写 assets/source/shyvana/codex_dragon_run/frames/d_run_<1..8>.png（画布大小）。rig_shyvana.py 看到这 8 张就拿它们当 d_run
   （SHYVANA_RIG_RUN=1 还是原来挪方块那版）。

    python tools/art/read_shyvana_dragon_run.py [--as-drawn] [--preview DIR]
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
SRC = os.path.join(ROOT, "assets", "source", "shyvana", "codex_dragon_run")
OUT = os.path.join(SRC, "frames")
DESIGN = os.path.join(ROOT, "assets", "source", "shyvana", "hd", "d_idle.png")
SQ = 8
CELL = (1024, 960)
PIVOT = (64, 60)           # 模板十字所在的格
GROUND = PIVOT[1] + 17     # 模板地面线所在的格（这一行往上是脚）
# Codex 画的第 6-8 帧整条龙比 1-5 帧靠前 6-7 格，循环接回第 1 帧时往回跳 8 格（鬃毛和全身方块的平均位置都这样）。
# 每帧整帧左右平移这么多格（不改一个方块），让身子（鬃毛和全身中心的平均）照英雄联盟 run1 头的前后晃走：
# 联盟 [+1.8, +0.5, -0.9, -1.4, -0.8, -1.0, +0.3, +1.5] 格（native_pose 渲的头的位置，0.64 格一联盟像素）。
# 用户两版对比后选了「收小前后晃」，默认就平移；--as-drawn 是 Codex 原样
STEADY = [6, 3, 1, 0, 1, -6, -4, -3]


def palette():
    d = np.array(Image.open(DESIGN).convert("RGBA"))
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)


def cells():
    """8 帧，每帧 120 x 128 格（RGBA）。先确认每个 8 x 8 块都是一个颜色。"""
    out = []
    for name in ("run_1.png", "run_2.png"):
        a = np.array(Image.open(os.path.join(SRC, name)).convert("RGBA"))
        H, W = a.shape[:2]
        b = a.reshape(H // SQ, SQ, W // SQ, SQ, 4)
        if not (b == b[:, :1, :, :1]).all():
            sys.exit(f"{name}: 有不是一个颜色的 8 x 8 块，网格对不上")
        g = a[::SQ, ::SQ]
        ch, cw = CELL[1] // SQ, CELL[0] // SQ
        for k in range(4):
            y0, x0 = (k // 2) * ch, (k % 2) * cw
            out.append(g[y0:y0 + ch, x0:x0 + cw].copy())
    return out


def snap(f, pal):
    """不透明的格换成设计图里最近的颜色；返回（新帧，换掉的格数，最大色差）。"""
    out = np.zeros_like(f)
    op = f[..., 3] > 0
    cols = f[op][:, :3].astype(int)
    d2 = ((cols[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    k = d2.argmin(1)
    new = pal[k]
    out[op, :3] = new
    out[op, 3] = 255
    moved = int((new != cols).any(1).sum())
    return out, moved, float(np.sqrt(d2.min(1).max())) if len(cols) else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    ap.add_argument("--as-drawn", action="store_true", help="Codex 原样，不平移 STEADY")
    a = ap.parse_args()
    os.environ["SHYVANA_RIG_RUN"] = "1"
    import rig_shyvana as RS
    C = RS.Canvas()
    pal = palette()
    frames = cells()
    os.makedirs(OUT, exist_ok=True)
    out = []
    for k, f in enumerate(frames):
        s, moved, worst = snap(f, pal)
        can = C.blank()
        ys, xs = np.nonzero(s[..., 3] > 0)
        ty, tx = ys - GROUND + C.rig.GY, xs - PIVOT[0] + C.rig.CX + (0 if a.as_drawn else STEADY[k])
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        if not ok.all():
            sys.exit(f"frame {k + 1}: {int((~ok).sum())} 格落到画布外")
        can[ty, tx] = s[ys, xs]
        out.append(can)
        Image.fromarray(can).save(os.path.join(OUT, f"d_run_{k + 1}.png"))
        print(f"frame {k + 1}: {len(ys)} 格, 最低一行 {ys.max()} (地面线 {GROUND}), 列 {xs.min()}..{xs.max()}, "
              f"换色 {moved} 格, 最大色差 {worst:.1f}")
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        x0 = min(np.nonzero(c[..., 3] > 0)[1].min() for c in out) - 2
        x1 = max(np.nonzero(c[..., 3] > 0)[1].max() for c in out) + 3
        y0 = min(np.nonzero(c[..., 3] > 0)[0].min() for c in out) - 2
        y1 = C.rig.GY + 2
        tiles = [c[y0:y1, x0:x1] for c in out]
        z = 3
        W = sum(t.shape[1] + 2 for t in tiles)
        im = Image.new("RGBA", (W, y1 - y0), (96, 112, 96, 255))
        x = 0
        for t in tiles:
            im.alpha_composite(Image.fromarray(t), (x, 0))
            x += t.shape[1] + 2
        im.resize((W * z, (y1 - y0) * z), Image.NEAREST).save(os.path.join(a.preview, "codex_d_run_read.png"))


if __name__ == "__main__":
    main()
