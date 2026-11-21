#!/usr/bin/env python3
"""炼金跑步：把 Codex 交回的 3 张原图（outputs/singed-run/raw/run_<k>_raw.png，每张三格 512 x 1024，透明底）读回成高清
帧（hd_run，PPU 1.39，一格设计图 = 一个高清像素）。

    python tools/art/read_singed_run.py --raw <codex>/outputs/singed-run/raw --out <dir> [--px 8.15]

Codex 自己的读回（frames_1x）为了让头对上模板的圈，把整张图缩到了 0.85，人比设计图小一圈（药罐 9-10 x 8-9 格，设计图
11 x 10），在游戏里就是一跑起来人变小（「模型不要变大变小」）。这里不缩：原图按 --px 像素一格读（按药罐量出来约 8.15，正好
是设计图的大小）。

每一格：
- 透明度用原图自己的 alpha（>= 220 算人物），颜色映射到设计图（游戏里高清待机第 0 帧）的 36 色；
- 网格在 0..px 的偏移里找和原图方块最对齐的（每格里和多数颜色不同的像素最少），每格取多数透明度、多数颜色；
- 位置：模板的站位点（格子里 x = 256）放在画布的中心列，地面线（y = 874）放在 GROUND_ROW。之后再整体挪到踩地的
  鞋底落在待机的地面上、裁成以站位点为中心的帧（place_singed_run.py）。

写出 <out>/frame_<k>.png（W x H，透明底）和 <out>/info.json（每帧网格偏移、人物范围、最低一行）。
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

CELL = (512, 1024)
STAND_X, GROUND_Y = 256, 874             # 模板格子里的站位点和地面线
W, H = 71, 110                           # 读回用的画布（比待机帧大：踢到后面的腿、比模板画低的脚都放得下）
CX = W / 2                               # 站位点在画布里的列（中心）
GROUND_ROW = 80                          # 模板地面线在画布里的行（Codex 把脚画在它下面约 10 格）


def palette_of(design):
    a = np.array(Image.open(design).convert("RGBA"))
    return np.unique(a[a[..., 3] > 0][:, :3], axis=0).astype(np.int32)


def to_index(rgb, pal):
    """每个像素最近的调色板颜色序号。"""
    d = ((rgb[..., None, :].astype(np.int32) - pal[None, None, :, :]) ** 2).sum(-1)
    return d.argmin(-1)


def read_cell(raw, pal, px):
    """一格原图 -> (帧, 信息)。"""
    op = raw[..., 3] >= 220
    idx = to_index(raw[..., :3], pal)
    idx[~op] = -1
    ys, xs = np.nonzero(op)
    best = None
    # 网格偏移：原图里 (STAND_X + ox, GROUND_Y + oy) 是一条格线，偏移在 ±px/2 里找
    for ox in np.arange(-px / 2, px / 2, 1.0):
        for oy in np.arange(-px / 2, px / 2, 1.0):
            frame, impure, n = sample(idx, px, ox, oy, pal, (ys.min(), ys.max(), xs.min(), xs.max()))
            score = impure / max(n, 1)
            if best is None or score < best[0]:
                best = (score, ox, oy, frame)
    score, ox, oy, frame = best
    a = np.array(frame)
    rows = np.nonzero(a[..., 3].any(1))[0]
    cols = np.nonzero(a[..., 3].any(0))[0]
    info = dict(offset=[float(ox), float(oy)], impure=round(float(score), 3),
                rows=[int(rows.min()), int(rows.max())], cols=[int(cols.min()), int(cols.max())],
                opaque=int((a[..., 3] > 0).sum()))
    return frame, info


def sample(idx, px, ox, oy, pal, box):
    """按 px 一格、格线过 (STAND_X + ox + (c - CX) * px, GROUND_Y + oy + (r - GROUND_ROW) * px) 读一帧。"""
    out = np.zeros((H, W, 4), np.uint8)
    impure = 0
    n = 0
    y0, y1, x0, x1 = box
    for r in range(H):
        top = GROUND_Y + oy + (r - GROUND_ROW) * px
        if top + px < y0 or top > y1 + 1:
            continue
        for c in range(W):
            left = STAND_X + ox + (c - CX) * px
            if left + px < x0 or left > x1 + 1:
                continue
            ya, yb = int(np.ceil(top)), int(np.ceil(top + px))
            xa, xb = int(np.ceil(left)), int(np.ceil(left + px))
            if yb <= 0 or xb <= 0 or ya >= idx.shape[0] or xa >= idx.shape[1]:
                continue
            blk = idx[max(ya, 0):yb, max(xa, 0):xb].ravel()
            if blk.size == 0:
                continue
            on = blk[blk >= 0]
            if on.size * 2 < blk.size:          # 多数透明
                continue
            vals, cnt = np.unique(on, return_counts=True)
            k = vals[cnt.argmax()]
            out[r, c, :3] = pal[k]
            out[r, c, 3] = 255
            impure += blk.size - cnt.max()
            n += blk.size
    return Image.fromarray(out), impure, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="Codex 的 outputs/singed-run/raw")
    ap.add_argument("--out", required=True)
    ap.add_argument("--px", type=float, default=8.15, help="原图多少像素一格")
    ap.add_argument("--design", default=os.path.join("C:/t/singed_run_pack/refs/design_1x.png"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pal = palette_of(a.design)
    infos = []
    k = 0
    for sheet in (1, 2, 3):
        raw = np.array(Image.open(os.path.join(a.raw, f"run_{sheet}_raw.png")).convert("RGBA"))
        for cell in range(2 if sheet == 3 else 3):
            k += 1
            frame, info = read_cell(raw[:, cell * CELL[0]:(cell + 1) * CELL[0]], pal, a.px)
            frame.save(os.path.join(a.out, f"frame_{k}.png"))
            info["frame"] = k
            infos.append(info)
            print(f"frame {k}: offset {info['offset']}, impure {info['impure']}, rows {info['rows']}, cols {info['cols']}, "
                  f"{info['opaque']} px")
    with open(os.path.join(a.out, "info.json"), "w", encoding="utf-8") as f:
        json.dump(dict(px=a.px, frames=infos), f, indent=1)


if __name__ == "__main__":
    main()
