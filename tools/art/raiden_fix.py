#!/usr/bin/env python3
"""雷电为右卫门（ragnarok_raiden）Codex 交的图收色：身体、肌肉解放的过渡和特效。

    python tools/art/raiden_fix.py            # 读 assets/source/raiden/runtime/sprites，写 assets/source/raiden/snapped
    python tools/art/raiden_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_raiden.py、ppu_hd.py --hero raiden、hero_reels.py --hero raiden

Codex 2026-11-22 交的（raiden_packs/outputs/raiden_assets_done.zip）：一格 256，脚底 (128, 232)，8 个动作各 8 帧，另有肌肉解放的
过渡 8 帧（ragnarok_raiden_release_native），特效八组各 8 帧（掌风、命中、四股的尘土和震环、肌肉解放的红纹、八咫乌的蓄劲、
冲击波和命中）。和小次郎一样（tools/art/kojiro_fix.py 有来由）收色：身体和过渡合起来 64 色（同一套调色板），特效每组
32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "raiden", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "raiden", "snapped")
BODY = ("ragnarok_raiden_native", "ragnarok_raiden_release_native")
FX = "ragnarok_raiden_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
