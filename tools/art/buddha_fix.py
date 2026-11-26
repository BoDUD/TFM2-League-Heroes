#!/usr/bin/env python3
"""释迦（ragnarok_buddha）Codex 交的图收色：身体和特效。

    python tools/art/buddha_fix.py            # 读 assets/source/buddha/runtime/sprites，写 assets/source/buddha/snapped
    python tools/art/buddha_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_buddha.py、ppu_hd.py --hero buddha、hero_reels.py --hero buddha

Codex 2026-11-22 交的（buddha_packs/outputs/buddha_assets_done.zip）：一格 256，脚底 (128, 232)，8 个动作各 8 帧，特效八组各 8 帧
（六道棍的横扫和命中、未来视、撤步的气流、观音盾的莲光和挡击、大圆寂刀·零的显形和斩击）。和小次郎一样（tools/art/kojiro_fix.py
有来由）收色：身体 64 色，特效每组 32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "buddha", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "buddha", "snapped")
BODY = ("ragnarok_buddha_native",)
FX = "ragnarok_buddha_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
