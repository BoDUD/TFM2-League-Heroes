#!/usr/bin/env python3
"""巨型纳尔跑步的 Codex 重画读回来（用户 2026-11-22：「不然你让codex帮忙 这个大纳尔」「纳尔重画的也交付了」）。

Codex 交的是 assets/source/gnar/codex_mega_run/mega-gnar-run-v2.png：2 行 × 4 格，每格 448×312，一格一帧，透明度干净，
但「像素」不是一张整齐的网格（3–5 像素一块，缩放过）。这里：

1. 每帧按 SCALE 像素一格（身子宽度和设计对上）切格投票：过半透明就透明，否则取最多的那个颜色；
2. 每格的颜色换成设计图（assets/source/gnar/hd/m_side.png）里最接近的那个，生图的杂色不留；
3. 放进 rig_gnar.py 的画布：横向让外框中心和绑骨那版同一帧对上，竖向让 8 帧里最低的脚落在地面（GY 上一行），
   帧和帧之间 Codex 画的上下起伏原样保留；
4. 写 assets/source/gnar/codex_mega_run/frames/m_run_<1..8>.png（画布大小）。rig_gnar.py 看到这 8 张就拿它们当 m_run。

    python tools/art/read_gnar_mega_run.py [--preview DIR]
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
SRC = os.path.join(ROOT, "assets", "source", "gnar", "codex_mega_run", "mega-gnar-run-v2.png")
OUT = os.path.join(ROOT, "assets", "source", "gnar", "codex_mega_run", "frames")
DESIGN = os.path.join(ROOT, "assets", "source", "gnar", "hd", "m_side.png")
CELL = (448, 312)
SCALE = 3.75


def palette():
    d = np.array(Image.open(DESIGN).convert("RGBA"))
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    return cols.astype(int)


def read(cell, pal, scale, ox, oy):
    H, W = cell.shape[:2]
    h, w = int((H - oy) // scale), int((W - ox) // scale)
    out = np.zeros((h, w, 4), np.uint8)
    for ty in range(h):
        y0, y1 = int(oy + ty * scale), int(oy + (ty + 1) * scale)
        for tx in range(w):
            x0, x1 = int(ox + tx * scale), int(ox + (tx + 1) * scale)
            blk = cell[y0:y1, x0:x1].reshape(-1, 4)
            opq = blk[blk[:, 3] > 0]
            if len(opq) * 2 < len(blk):
                continue
            cols, cnt = np.unique(opq[:, :3], axis=0, return_counts=True)
            c = cols[int(np.argmax(cnt))].astype(int)
            k = int(np.argmin(((pal - c) ** 2).sum(1)))
            out[ty, tx] = (*pal[k], 255)
    return out


def best_read(cell, pal):
    """原图本来就没有整齐的网格，偏移试不出更好的：从左上角切。"""
    return read(cell, pal, SCALE, 0, 0)


def bbox(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return xs.min(), xs.max(), ys.min(), ys.max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    os.environ["GNAR_RIG_RUN"] = "1"                  # 对齐用绑骨那版，不用已经读回的 Codex 帧
    import rig_gnar as RG
    C = RG.Canvas()
    guide = RG.frames_all(C)["m_run"]
    sheet = np.array(Image.open(SRC).convert("RGBA"))
    pal = palette()
    frames = []
    for k in range(8):
        x0, y0 = (k % 4) * CELL[0], (k // 4) * CELL[1]
        frames.append(best_read(sheet[y0:y0 + CELL[1], x0:x0 + CELL[0]], pal))
    low = max(bbox(f)[3] for f in frames)
    out = []
    for k, f in enumerate(frames):
        gx0, gx1, _, _ = bbox(guide[k])
        fx0, fx1, _, _ = bbox(f)
        dx = int(round((gx0 + gx1) / 2 - (fx0 + fx1) / 2))
        dy = (C.rig.GY - 1) - low
        can = C.blank()
        ys, xs = np.nonzero(f[..., 3] > 0)
        can[ys + dy, xs + dx] = f[ys, xs]
        out.append(can)
    os.makedirs(OUT, exist_ok=True)
    for k, can in enumerate(out):
        Image.fromarray(can).save(os.path.join(OUT, f"m_run_{k + 1}.png"))
    print("read back:", [f.shape[:2] for f in frames], "-> canvas", out[0].shape[:2], "palette", len(pal))
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        x0 = min(bbox(c)[0] for c in out) - 2
        x1 = max(bbox(c)[1] for c in out) + 3
        y0 = min(bbox(c)[2] for c in out) - 2
        y1 = C.rig.GY + 2
        tiles = [c[y0:y1, x0:x1] for c in out]
        z = 3
        W = sum(t.shape[1] + 2 for t in tiles)
        im = Image.new("RGBA", (W, y1 - y0), (96, 112, 96, 255))
        x = 0
        for t in tiles:
            im.alpha_composite(Image.fromarray(t), (x, 0))
            x += t.shape[1] + 2
        im.resize((W * z, (y1 - y0) * z), Image.NEAREST).save(os.path.join(a.preview, "codex_m_run_read.png"))


if __name__ == "__main__":
    main()
