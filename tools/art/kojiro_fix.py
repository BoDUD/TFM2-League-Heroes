#!/usr/bin/env python3
"""佐佐木小次郎（ragnarok_kojiro）Codex 交的图收色：身体、双刀待机、特效。

    python tools/art/kojiro_fix.py            # 读 assets/source/kojiro/runtime/sprites，写 assets/source/kojiro/snapped
    python tools/art/kojiro_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_kojiro.py、ppu_hd.py --hero kojiro、hero_reels.py --hero kojiro

Codex 2026-11-21 交的（kojiro_packs/outputs/kojiro_assets_done.zip）已经是两倍密度：一格 256，脚底 (128, 232)，单刀 8 个动作
各 8 帧、双刀待机 8 帧，特效四组各 8 帧。图是缩小的手绘，身体 13 万多种颜色、双刀待机 2 万多、特效 4 万多：ppu_hd.py 出 lo_
（选人、百科）和 ragnarok_art.py 出 1 倍帧都拿「这一帧最常见的 64 / 96 种颜色」当调色板，颜色一散就挑歪（吕布、亚当那次皮肤
一块深一块浅、整个人发黄发粉）。所以：

- 身体和双刀待机合起来收到 64 色（同一套调色板：换成双刀时衣服、头发的颜色不跳）；
- 特效每组收到 32 色（和 Codex 自己出特效时一样多）：画进身体帧里时，lo_ 帧的调色板不会被一堆零散的蓝白挤掉。

都是中位切分、不抖动，每个像素换成最近的颜色（ragnarok_repixel.median_cut）。Codex 的原样在 runtime/sprites，只读。
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kojiro", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "kojiro", "snapped")
BODY = ("ragnarok_kojiro_native", "ragnarok_kojiro_niten_native")
FX = "ragnarok_kojiro_fx_native"
BODY_COLOURS = 64
FX_COLOURS = 32


def read(stem):
    sheet = np.asarray(Image.open(os.path.join(SRC, stem + "#sheet.png")).convert("RGBA"))
    fanim = json.load(open(os.path.join(SRC, stem + "#anim.fanim"), encoding="utf-8-sig"))
    return sheet, fanim


def snap_to(sheet, pal, mask=None):
    """不透明像素（mask 给了就只管 mask 里的）换成 pal 里最近的颜色。"""
    out = sheet.copy()
    op = sheet[..., 3] > 0
    if mask is not None:
        op &= mask
    cols = sheet[op][:, :3].astype(int)
    snapped = np.empty_like(cols)
    for i in range(0, len(cols), 20000):
        d = ((cols[i:i + 20000, None, :] - pal[None]) ** 2).sum(-1)
        snapped[i:i + 20000] = pal[np.argmin(d, 1)]
    out[op, :3] = snapped
    return out


def make(_up=None):
    outs = []
    bodies = [read(s) for s in BODY]
    pool = np.concatenate([s[s[..., 3] > 0][:, :3] for s, _ in bodies])
    pal = R.median_cut(pool, BODY_COLOURS)
    for stem, (sheet, fanim) in zip(BODY, bodies):
        outs.append((os.path.join(OUT, stem), snap_to(sheet, pal), fanim))
    sheet, fanim = read(FX)
    out = sheet.copy()
    for tag, a in fanim["anims"].items():
        mask = np.zeros(sheet.shape[:2], bool)
        for f in a["frames"]:
            d = f["data"]
            x, y, w, h = (int(d[k]) for k in "xywh")
            mask[y:y + h, x:x + w] = True
        cols = sheet[mask & (sheet[..., 3] > 0)][:, :3]
        out = snap_to(out, R.median_cut(cols, FX_COLOURS), mask)
    outs.append((os.path.join(OUT, FX), out, fanim))
    return outs


if __name__ == "__main__":
    R.run(__doc__, make, 2)
