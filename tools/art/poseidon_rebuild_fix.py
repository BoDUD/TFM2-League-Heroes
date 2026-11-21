#!/usr/bin/env python3
"""波塞冬 Codex 按两倍密度重画的身体帧（assets/source/poseidon/rebuild）的收色，和照两倍重出的特效。

    python tools/art/poseidon_rebuild_fix.py            # 读 rebuild/codex/ 的原样，写 rebuild/ 的身体图和特效图
    python tools/art/poseidon_rebuild_fix.py --check    # 和现在的 rebuild/ 不一样就退出 1
    然后 tools/art/import_poseidon.py、ppu_hd.py --hero poseidon、hero_reels.py --hero poseidon

Codex 交的原样（2026-11-21，ragnarok_hd_packs/outputs/poseidon_rebuild_done.zip：一格 256、脚底 (128, 232)，帧序、
时长和 128 格那版一样，三叉戟是同一把 158 像素的 trident_master）放在 rebuild/codex/，这里只读它，不改它。

1. 收色：Codex 这版有 16 万多种颜色。ppu_hd.py 出 lo_（选人、百科用的）和 ragnarok_art.py 出 1 倍帧都拿「这一帧最常见
   的 64 / 96 种颜色」当调色板，颜色一散就挑歪（亚当那次绿短裤成了棕的、整个人发粉）。整张图收到 64 色（中位切分，
   不抖动，每个像素换成最近的那个颜色），3 倍放大看和原来几乎一样，裙甲和绿裤的过渡稍微多一点色阶。
2. 特效：Codex 这次只重画了身体，特效还是 128 格那套。用他自己的 effect_frames（tools/build_art.py，每段特效一个缩放）
   把格子和尺寸都乘 2，从原画（art/fxa..fxd.png）重新取一遍，和身体一样细；乘 1 时和他交的 128 格逐像素一样。

跑步时人在格子里前后滑、出手时比待机往前跳的问题不在这里改，在 tools/art/import_poseidon.py 的 SHIFT（整帧平移）。
"""
import importlib.util
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "poseidon")
DIR = os.path.join(SRC, "rebuild")
CODEX = os.path.join(DIR, "codex", "ragnarok_poseidon_native")     # Codex 交的原样
OUT = os.path.join(DIR, "ragnarok_poseidon_native")
CODEX_FX = os.path.join(SRC, "runtime", "sprites", "ragnarok_poseidon_fx_native")   # 128 格的特效，排法照它
FX_OUT = os.path.join(DIR, "ragnarok_poseidon_fx_native")
UP = 2
COLOURS = 64


def codex_tool():
    """Codex 的 build_art.py（它 import 同目录的 trident）。"""
    tools = os.path.join(SRC, "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location("poseidon_build_art", os.path.join(tools, "build_art.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def body():
    sheet = np.asarray(Image.open(CODEX + "#sheet.png").convert("RGBA"))
    fanim = json.load(open(CODEX + "#anim.fanim", encoding="utf-8-sig"))
    return R.snap(sheet, COLOURS), fanim


def effects(up):
    """Codex 的特效按 up 倍出：格子和每段特效的尺寸都乘 up（matte 的判断照他的 main()）。"""
    B = codex_tool()
    B.CELL = round(B.CELL * up)
    out = {}
    for file, specs in B.FX.items():
        source = Image.open(B.SOURCE / f"{file}.png").convert("RGBA")
        matte = np.median(np.asarray(source)[:, :, 3]) > 155
        tiles = list(B.grid(source, 4, 4))
        for i, (name, size, _ms) in enumerate(specs):
            out[name] = [np.asarray(f) for f in B.effect_frames(tiles[i * 8:(i + 1) * 8], size * up, matte)]
    return out


def make(up):
    sheet, fanim = body()
    return [(OUT, sheet, fanim), (FX_OUT, *R.sheet_of(effects(up), CODEX_FX, up))]


if __name__ == "__main__":
    R.run(__doc__, make, UP)
