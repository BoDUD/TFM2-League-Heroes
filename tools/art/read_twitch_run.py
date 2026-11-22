#!/usr/bin/env python3
"""图奇跑步的 Codex 重画读回来（用户 2026-11-22：「老鼠的跑步姿势有点怪 让codex帮忙重做一下」「codex交付了 你需要把不干净的
黑边都处理了」）。

Codex 交的是 assets/source/twitch/codex_run/run_1.png、run_2.png（raw.png 是它生成的原图）：和模板一样 2048 x 1920，2 x 2 格，
每格 1024 x 960，每个 8 x 8 块都是一个颜色、对齐模板的网格，透明度只有 0 / 255，颜色都是设计图里的。所以这里不用猜网格：

1. 每格每 8 像素取一个点，得到 128 x 120 格的一帧（设计图的一格）；
2. 每格的颜色换成设计图（assets/source/twitch/hd/design.png）里最接近的那个（这次一格都不用换）；
3. 放进 rig_twitch_hd.py 的画布：模板的十字（第 64 列）是站位点，地面线（第 85 行）是脚底下面那一行，所以格子 (x, y)
   放到画布 (x - 64 + CX, y - 85 + GY)；
4. 黑边理干净（clean()，用户「你需要把不干净的黑边都处理了」）：设计图外缘 81% 是近黑描边 (14, 10, 16)，Codex 这 8 帧外缘
   只有三成是，其余拿深棕 (35, 24, 22)、深灰 (27, 33, 36)、暗棕 (53, 35, 24) 冒充描边，还挂着一格厚的浅棕毛边、几个碎点
   和毛刺，看着发脏。只动边上，身子里面的画不改：
   - 和身子不连着的碎点（SPECK 格以下）删掉；
   - 最外一圈（挨着透明）的 DARK 几种颜色换成描边色；
   - 挂在描边外面的一格浅色毛边（往里只挨着描边、不挨着身子）删掉；
   - 描边上支出来的毛刺（8 邻里不透明的不到 2 格）删掉，删到没有为止。
   描边多厚交给后面的 thin_outline.py --hero twitch（图奇的高清帧描边统一补到 2 格）；
5. 写 assets/source/twitch/codex_run/frames/run_<1..8>.png（画布大小）。rig_twitch_hd.py 看到这 8 张就拿它们当 run
   （TWITCH_RIG_RUN=1 还是原来那版）。

    python tools/art/read_twitch_run.py [--preview DIR]
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
SRC = os.path.join(ROOT, "assets", "source", "twitch", "codex_run")
OUT = os.path.join(SRC, "frames")
DESIGN = os.path.join(ROOT, "assets", "source", "twitch", "hd", "design.png")
SQ = 8
CELL = (1024, 960)
PIVOT = (64, 60)           # 模板十字所在的格
GROUND = PIVOT[1] + 25     # 模板地面线所在的格（这一行往上是脚）
OUTLINE = (14, 10, 16)     # 设计图的描边色（casts_twitch_hd.OUTLINE）
DARK = [(35, 24, 22), (27, 33, 36), (53, 35, 24)]   # Codex 在最外一圈冒充描边的颜色
SPECK = 3                  # 和身子不连着、这么多格以下的一块是碎点（嘴边那几个 1-2 格的）；设计图自己就有一截 9 格的
                           # 弩弦浮在弩上方，不和身子连着，留着
FOUR = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
EIGHT = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def count(mask, kernel):
    return ndimage.convolve(mask.astype(int), kernel, mode="constant")


def clean(f):
    """黑边理干净（见文件头第 4 步）。返回（新帧，{删的碎点, 换成描边, 删的毛边, 删的毛刺}）。"""
    a = f.copy()
    n = {"speck": 0, "dark": 0, "fringe": 0, "spur": 0}
    op = a[..., 3] > 0
    lab, k = ndimage.label(op, structure=np.ones((3, 3)))
    if k > 1:
        sz = ndimage.sum(op, lab, range(1, k + 1))
        main = 1 + int(np.argmax(sz))
        for i in range(1, k + 1):
            if i != main and sz[i - 1] <= SPECK:
                a[lab == i] = 0
                n["speck"] += int(sz[i - 1])
    op = a[..., 3] > 0
    edge = op & (count(~op, FOUR) > 0)
    rgb = a[..., :3].astype(int)
    dark = np.zeros(op.shape, bool)
    for c in DARK:
        dark |= (rgb == np.array(c)).all(-1)
    m = edge & dark
    a[m, :3] = OUTLINE
    n["dark"] = int(m.sum())
    for _ in range(4):
        op = a[..., 3] > 0
        isout = op & (a[..., :3].astype(int) == np.array(OUTLINE)).all(-1)
        body = op & ~isout
        edge = op & (count(~op, FOUR) > 0)
        fringe = edge & body & (count(body, FOUR) == 0) & (count(isout, FOUR) > 0)
        if not fringe.any():
            break
        a[fringe] = 0
        n["fringe"] += int(fringe.sum())
    # 毛刺只删从一大块边上单独支出去的那一格（它唯一的邻格周围还有 4 格以上），删一遍、不反复啃：
    # 一格粗的细线（弩弦、弩尖）两头也只有一个邻格，但那个邻格也是细线，留着
    op = a[..., 3] > 0
    isout = op & (a[..., :3].astype(int) == np.array(OUTLINE)).all(-1)
    nb = count(op, EIGHT)
    solid = ndimage.binary_dilation(op & (nb >= 4), structure=np.ones((3, 3)))
    spur = isout & (nb == 1) & solid
    a[spur] = 0
    n["spur"] = int(spur.sum())
    return a, n


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
    """不透明的格换成设计图里最近的颜色；返回（新帧，换掉的格数）。"""
    out = np.zeros_like(f)
    op = f[..., 3] > 0
    cols = f[op][:, :3].astype(int)
    d2 = ((cols[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    new = pal[d2.argmin(1)]
    out[op, :3] = new
    out[op, 3] = 255
    return out, int((new != cols).any(1).sum())


def rig():
    os.environ["TWITCH_RIG_RUN"] = "1"
    import rig_twitch_hd as RT
    return RT.make_rig(RT.Design())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    ap.add_argument("--raw", action="store_true", help="不理黑边（Codex 原样，比对用）")
    a = ap.parse_args()
    R = rig()
    pal = palette()
    os.makedirs(OUT, exist_ok=True)
    out = []
    for k, f in enumerate(cells()):
        s, moved = snap(f, pal)
        if not a.raw:
            s, n = clean(s)
            print(f"frame {k + 1} 黑边: 碎点 {n['speck']} 格, 换成描边 {n['dark']} 格, 毛边 {n['fringe']} 格, 毛刺 {n['spur']} 格")
        can = R.canvas()
        ys, xs = np.nonzero(s[..., 3] > 0)
        ty, tx = ys - GROUND + R.GY, xs - PIVOT[0] + R.CX
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        if not ok.all():
            sys.exit(f"frame {k + 1}: {int((~ok).sum())} 格落到画布外")
        can[ty, tx] = s[ys, xs]
        out.append(can)
        Image.fromarray(can).save(os.path.join(OUT, f"run_{k + 1}.png"))
        print(f"frame {k + 1}: {len(ys)} 格, 最低一行 {ys.max()} (地面线 {GROUND}), 列 {xs.min()}..{xs.max()}, 换色 {moved} 格")
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        x0 = min(np.nonzero(c[..., 3] > 0)[1].min() for c in out) - 2
        x1 = max(np.nonzero(c[..., 3] > 0)[1].max() for c in out) + 3
        y0 = min(np.nonzero(c[..., 3] > 0)[0].min() for c in out) - 2
        y1 = R.GY + 2
        tiles = [c[y0:y1, x0:x1] for c in out]
        z = 3
        W = sum(t.shape[1] + 2 for t in tiles)
        im = Image.new("RGBA", (W, y1 - y0), (96, 112, 96, 255))
        x = 0
        for t in tiles:
            im.alpha_composite(Image.fromarray(t), (x, 0))
            x += t.shape[1] + 2
        im.resize((W * z, (y1 - y0) * z), Image.NEAREST).save(os.path.join(a.preview, "codex_run_read.png"))


if __name__ == "__main__":
    main()
