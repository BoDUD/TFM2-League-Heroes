#!/usr/bin/env python3
"""锤石的灯笼（用户 2026-11-22：「锤石的灯笼是不是完全没有 我是没见过」「你这个灯笼重做吧」「让codex画吧」「用PPU弄成高清的啊」）。

Codex 照锤石手里那盏画的灯笼（assets/source/thresh/lantern/codex_lantern_raw.png，提示词 assets/source/thresh/LANTERN_PROMPT.md；
它只交回一盏立着的灯）在这里读回、做成两段动画，写进一张单独的特效图 league/effects/league_thresh_lantern，PPU 5：
锤石别的特效在 league_thresh_fx 里是 PPU 2，缩到那么粗灯笼的窗和翘檐就糊了；league.dll 的特效表按每张图自己的 PPU 画
（tools/art/fx_ppu_table.py 从 hd_idle 和 idle 的尺寸比读出来）。

- 读回：原图的格子大约 14.5 像素一格（生图模型的格子不齐），按 LAMP_H 格高切格，每格投票取最多的颜色（先把原图归成 COLOURS 种，
  不取平均：颜色不糊），描边占得多就取描边，外轮廓补一圈最暗的颜色。
- w_ground：落在地上的灯（附加包 league_thresh_lantern 0.2.0 放）。灯尖离地 HOVER 格浮着、上下晃 1 格，窗里的光一明一暗，
  地上一圈魂火绿的光一涨一缩，几点魂火往上飘。4 × 125 ms，再接一帧和第 1 帧一样的 100 ms：附加包每 0.5 秒重播一段，
  接上的地方两张一样的图叠在一起看不出来。落点在画面正中，地面在正中往下 FEET 格（和护盾、Box 一样）。
- w_lantern：飞的灯笼（主包锤石的投射物 league_thresh_w_lantern）。游戏按飞的方向转这张图，所以灯笼横放（提环朝后、底尖朝前）、
  上半照到下半（上下对称），后面拖一道魂火。4 × 70 ms。
- 1x 帧由高清帧每 5×5 投票缩出来（没有 league.dll 时才用）。

    python tools/art/fx_thresh_lantern.py --preview DIR   # 只出预览图，不动仓库
    python tools/art/fx_thresh_lantern.py                 # 写 league/effects/league_thresh_lantern#sheet.png / #anim.fanim
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "thresh", "lantern", "codex_lantern_raw.png")
STEM = os.path.join(ROOT, "league", "effects", "league_thresh_lantern")
PPU = 5
LAMP_H = 83            # 灯笼读回来多少格高（PPU 5：16.6 个游戏像素）
COLOURS = 24
FEET = 11              # 地面在画面正中往下几个游戏像素
HOVER = 3              # 灯尖离地几个游戏像素
# 画布（1x 的尺寸，奇数：正中一格；高清 = 1x × PPU）
GROUND_1X = (29, 31)
FLY_1X = (49, 9)
DARK = 60              # 三色加起来低于这个算描边一类的暗色


def read_lantern():
    a = np.array(Image.open(SRC).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] > 128, 255, 0).astype(np.uint8)
    ys, xs = np.nonzero(a[..., 3])
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    op = a[..., 3] > 0
    q = Image.fromarray(a[op][:, :3].reshape(-1, 1, 3)).quantize(colors=COLOURS, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[:COLOURS * 3]).reshape(-1, 3)
    idx = np.full(a.shape[:2], -1, int)
    idx[op] = np.array(q).reshape(-1)
    lum = pal.sum(1)
    H0, W0 = a.shape[:2]
    s = H0 / LAMP_H
    w = int(round(W0 / s)) | 1
    xo = (w * s - W0) / 2
    out = np.zeros((LAMP_H, w, 4), np.uint8)
    for ty in range(LAMP_H):
        y0, y1 = int(ty * s), max(int((ty + 1) * s), int(ty * s) + 1)
        for tx in range(w):
            x0, x1 = max(0, int(tx * s - xo)), min(W0, int((tx + 1) * s - xo))
            if x1 <= x0:
                continue
            cell = idx[y0:y1, x0:x1].ravel()
            opq = cell[cell >= 0]
            if opq.size * 2 < cell.size:
                continue
            cnt = np.bincount(opq, minlength=len(pal))
            dark = lum < DARK
            if cnt[dark].sum() >= 0.35 * cell.size:
                k = int(np.argmax(np.where(dark, cnt, -1)))
            else:
                k = int(np.argmax(np.where(dark, -1, cnt)))
                if cnt[k] == 0:
                    k = int(np.argmax(cnt))
            out[ty, tx] = (*pal[k], 255)
    # 外轮廓一圈最暗的颜色
    op = out[..., 3] > 0
    edge = np.zeros_like(op)
    edge[1:] |= ~op[:-1]
    edge[:-1] |= ~op[1:]
    edge[:, 1:] |= ~op[:, :-1]
    edge[:, :-1] |= ~op[:, 1:]
    edge &= op
    out[edge, :3] = pal[int(np.argmin(lum))]
    return out


def greens(a):
    """灯里发绿光的格子（绿明显高过红和蓝）。"""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (g > r + 40) & (g > b + 20)


def glow(lamp, step):
    """窗光明暗：step > 0 亮一档（往薄荷白靠），< 0 暗一档（往深绿靠）。"""
    out = lamp.copy()
    m = greens(lamp)
    c = out[m, :3].astype(float)
    if step > 0:
        c = c + (np.array([235, 255, 240]) - c) * 0.35 * step
    elif step < 0:
        c = c * (1 - 0.22 * -step)
    out[m, :3] = np.clip(c, 0, 255).astype(np.uint8)
    return out


def soul(level):
    """魂火绿：0 最暗 .. 4 最亮（从灯笼窗的颜色取）。"""
    return [(6, 94, 54), (2, 157, 51), (16, 243, 72), (195, 251, 207), (236, 255, 240)][level]


def put(can, x, y, rgb):
    h, w = can.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        can[y, x] = (*rgb, 255)


def lay(can, img, x0, y0):
    m = img[..., 3] > 0
    ys, xs = np.nonzero(m)
    for y, x in zip(ys + y0, xs + x0):
        if 0 <= y < can.shape[0] and 0 <= x < can.shape[1]:
            can[y, x] = img[y - y0, x - x0]


def ring(can, cx, cy, rx, ry, thick):
    """地上的光圈：一圈实心方块，后半圈暗、前半圈绿，只有前沿外圈亮，几点亮的。"""
    h, w = can.shape[:2]
    inner = 1 - thick / ry
    for y in range(h):
        for x in range(w):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            r = (dx * dx + dy * dy) ** 0.5
            if inner <= r <= 1.0:
                front = y >= cy
                edge = r > 1 - 0.3 * thick / ry
                put(can, x, y, soul(2 if (front and edge) else 1 if front else 0))
    for ang in (0.45, 1.25, 2.25, 2.8):
        x = int(round(cx + rx * 0.96 * np.cos(ang)))
        y = int(round(cy + ry * 0.96 * np.sin(ang)))
        for d in ((0, 0), (1, 0), (0, 1), (1, 1)):
            put(can, x + d[0], y + d[1], soul(3))


def wisp(can, x, y, size, level):
    """一点往上飘的魂火：一个小方块，上面尖一点。"""
    for dy in range(size):
        half = max(0, (size - 1 - dy) // 2) if dy < size - 1 else 0
        for dx in range(-half, half + 1):
            put(can, x + dx, y + dy, soul(level if dy else min(4, level + 1)))


def ground_frames(lamp):
    W, H = GROUND_1X[0] * PPU, GROUND_1X[1] * PPU
    cx, cy = W // 2, H // 2
    gy = cy + FEET * PPU
    lh, lw = lamp.shape[:2]
    bob = [0, -2, -5, -2]
    steps = [0, 1, 0, -1]
    rings = [(50, 14), (52, 15), (54, 16), (52, 15)]
    # 魂火：(相对正中的 x, 第 1 帧离地多高, 大小)，每帧往上 9 格、越飘越小
    wisps = [(-30, 30, 6), (27, 52, 5), (-16, 74, 4)]
    out = []
    for i in range(4):
        can = np.zeros((H, W, 4), np.uint8)
        ring(can, cx, gy, *rings[i], thick=4)
        l = glow(lamp, steps[i])
        lay(can, l, cx - lw // 2, gy - HOVER * PPU - lh + bob[i])
        for dx, up0, size in wisps:
            up_ = up0 + 9 * i
            s = max(2, size - i)
            wisp(can, cx + dx, gy - up_, s, 2 if i < 3 else 1)
        out.append((can, 125))
    out.append((out[0][0].copy(), 100))
    return out


def flying_frames(lamp):
    side = np.ascontiguousarray(np.rot90(lamp, 1))          # 逆时针转：提环到左边
    sh, sw = side.shape[:2]
    half = sh // 2
    side[sh - half:] = side[:half][::-1]                     # 上半照到下半：上下对称
    W, H = FLY_1X[0] * PPU, FLY_1X[1] * PPU
    cx, cy = W // 2, H // 2
    out = []
    left = cx - sw // 2
    for i in range(4):
        can = np.zeros((H, W, 4), np.uint8)
        # 尾巴：一道往后收细的魂火，边沿按帧起伏流动（火舌），里面亮、外面暗；几粒火星往后飘
        L = 80
        for k in range(L):
            x = left - 1 - k
            t = 11 * (1 - k / L) ** 0.8 + 1.6 * np.sin(k / 3.2 - i * np.pi / 2) * (1 - k / L)
            if t < 0.6:
                continue
            for dy in range(-int(t), int(t) + 1):
                core = abs(dy) <= t * 0.35
                mid = abs(dy) <= t * 0.7
                lvl = (4 if k < 10 else 3 if k < 30 else 2) if core else (3 if k < 14 else 2 if k < 45 else 1) if mid                     else (2 if k < 25 else 1 if k < 60 else 0)
                put(can, x, cy + dy, soul(lvl))
        for k0, dy0 in ((18, -12), (40, 9), (58, -7), (70, 5)):
            k = (k0 + i * 7) % 82
            for d in ((0, 0), (1, 0), (0, 1), (1, 1)):
                put(can, left - 1 - k + d[0], cy + dy0 + d[1], soul(3 if k < 40 else 2))
        lay(can, side, cx - sw // 2, cy - sh // 2)
        top = can[:cy]
        can[cy + 1:] = top[::-1][:H - cy - 1]
        out.append((can, 70))
    return out


def down(frames):
    """高清帧缩成 1x：每 PPU×PPU 投票，过半透明就透明，暗色占得多取暗色。"""
    res = []
    for f, ms in frames:
        H, W = f.shape[:2]
        h, w = H // PPU, W // PPU
        o = np.zeros((h, w, 4), np.uint8)
        for y in range(h):
            for x in range(w):
                blk = f[y * PPU:(y + 1) * PPU, x * PPU:(x + 1) * PPU].reshape(-1, 4)
                opq = blk[blk[:, 3] > 0]
                if len(opq) * 2 < len(blk):
                    continue
                cols, cnt = np.unique(opq[:, :3], axis=0, return_counts=True)
                dark = cols.sum(1) < DARK
                if cnt[dark].sum() >= 0.35 * len(blk):
                    k = int(np.argmax(np.where(dark, cnt, -1)))
                else:
                    k = int(np.argmax(np.where(dark, -1, cnt))) if (~dark).any() else int(np.argmax(cnt))
                o[y, x] = (*cols[k], 255)
        res.append((o, ms))
    return res


def build():
    lamp = read_lantern()
    gr = ground_frames(lamp)
    fl = flying_frames(lamp)
    idle_hd = np.zeros((PPU, PPU, 4), np.uint8)
    idle_1x = np.zeros((1, 1, 4), np.uint8)
    return {"idle": [(idle_1x, 100)], "w_lantern": down(fl), "w_ground": down(gr),
            "hd_idle": [(idle_hd, 100)], "hd_w_lantern": fl, "hd_w_ground": gr}, lamp


def preview(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    sheet, lamp = build()
    bg = (58, 72, 48, 255)
    for tag in ("hd_w_ground", "hd_w_lantern", "w_ground", "w_lantern"):
        fr = sheet[tag]
        z = 3 if tag.startswith("hd_") else 8
        W = sum(f.shape[1] + 2 for f, _ in fr)
        H = max(f.shape[0] for f, _ in fr)
        can = Image.new("RGBA", (W, H), bg)
        x = 0
        for f, _ in fr:
            can.alpha_composite(Image.fromarray(f), (x, 0))
            x += f.shape[1] + 2
        can.resize((W * z, H * z), Image.NEAREST).save(os.path.join(out_dir, f"thresh_lantern_{tag}.png"))
    Image.fromarray(lamp).resize((lamp.shape[1] * 6, lamp.shape[0] * 6), Image.NEAREST).save(
        os.path.join(out_dir, "thresh_lantern_read_back.png"))
    print("lantern", lamp.shape[:2], {t: [f.shape[:2] for f, _ in v][:1] for t, v in sheet.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    if a.preview:
        preview(a.preview)
        return
    sheet, _ = build()
    G.write_sheet(STEM, sheet, share=True)
    print("wrote", os.path.relpath(STEM, ROOT) + "#sheet.png / #anim.fanim:", {t: len(v) for t, v in sheet.items()})


if __name__ == "__main__":
    main()
