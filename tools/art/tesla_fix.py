#!/usr/bin/env python3
"""尼古拉·特斯拉（ragnarok_tesla）Codex 交的图收色：身体和特效。

    python tools/art/tesla_fix.py            # 读 assets/source/tesla/runtime/sprites，写 assets/source/tesla/snapped
    python tools/art/tesla_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_tesla.py、ppu_hd.py --hero tesla、hero_reels.py --hero tesla

Codex 2026-11-23 交的（tesla_packs/outputs/tesla_assets_done.zip，以提交 7e3a2e0db 为准）：一格 256，脚底 (128, 232)，8 个动作
各 8 帧，特效八组各 8 帧（等离子脉冲拳和命中、特斯拉步的拖痕、瞬移的离场和到达闪光、神之监狱的展开和循环、双拳的冲击）。
机甲双拳，没有另贴的道具。
和小次郎一样（tools/art/kojiro_fix.py 有来由）收色：身体 64 色，特效每组 32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "tesla", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "tesla", "snapped")
BODY = ("ragnarok_tesla_native",)
FX = "ragnarok_tesla_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
