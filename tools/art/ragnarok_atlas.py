#!/usr/bin/env python3
"""终末包里按「逻辑像素图集」交付的英雄（冲田总司、须佐之男）：读 Codex 的 atlases/ 给 tools/art/ragnarok_art.py 用。

Codex 2026-11-23 起的交付不再是 #sheet.png / #anim.fanim，而是：
- atlases/<名>_actor.png、atlases/<名>_fx.png：一个动作（或一个特效）一行，每行 8 格，格子大小 frames.json 的 cell；
- atlases/frames.json：每格的矩形和秒数（actor / fx 两组），脚底点 ground，特效格的中心 fx_cell_anchor；
- *_4x.png 是严格的四倍最近邻，不用（和逻辑图一模一样，只是大）。

这里按整数倍 ZOOM 最近邻放大成「密度帧」交给引擎（像素画不能按小数缩放，不然像素大小不一）；英雄在游戏里多大由
import_<英雄>.py 的 PPU 定（逻辑图 56 格高、放大两倍 112 格，PPU 8/3 就是 42 个游戏像素，和别的终末英雄一样）。
"""
import json
import os

import numpy as np
from PIL import Image

ZOOM = 2


def meta(root):
    with open(os.path.join(root, "atlases", "frames.json"), encoding="utf-8") as f:
        return json.load(f)


def bank(root, kind, png, zoom=ZOOM):
    """{标签: [(放大后的帧, 秒)]}：kind 是 frames.json 里的 actor 或 fx。"""
    m = meta(root)
    px = np.asarray(Image.open(os.path.join(root, "atlases", png)).convert("RGBA"))
    out = {}
    for tag, clip in m[kind].items():
        frames = []
        for f in clip["frames"]:
            a = px[f["y"]:f["y"] + f["h"], f["x"]:f["x"] + f["w"]]
            frames.append((np.repeat(np.repeat(a, zoom, 0), zoom, 1).copy(), float(f["duration"])))
        out[tag] = frames
    return out


def reader(root, name, hero_id, zoom=ZOOM):
    """给 ragnarok_art 的 READ：<id>_native 是角色图，<id>_fx_native 是特效图。"""
    def read(stem):
        if stem == f"{hero_id}_native":
            return bank(root, "actor", f"{name}_actor.png", zoom)
        if stem == f"{hero_id}_fx_native":
            return bank(root, "fx", f"{name}_fx.png", zoom)
        raise KeyError(stem)
    return read


def scaled(point, zoom=ZOOM):
    """逻辑图上的点 -> 放大后的点。"""
    return (point[0] * zoom, point[1] * zoom)
