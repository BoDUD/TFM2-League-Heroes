#!/usr/bin/env python3
"""开膛手杰克（ragnarok_jack）Codex 交的图收色：身体和特效。

    python tools/art/jack_fix.py            # 读 assets/source/jack/runtime/sprites，写 assets/source/jack/snapped
    python tools/art/jack_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_jack.py、ppu_hd.py --hero jack、hero_reels.py --hero jack

Codex 2026-11-21 交的（jack_packs/outputs/jack_assets_done.zip）：一格 256，脚底 (128, 232)，8 个动作各 8 帧，特效八组各 8 帧
（飞刀、扇形飞刀、命中、雾、伞前的护弧、手套触物、单片镜的异色、收招）。和小次郎一样（tools/art/kojiro_fix.py 有来由）
收色：身体 64 色，特效每组 32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "jack", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "jack", "snapped")
BODY = ("ragnarok_jack_native",)
FX = "ragnarok_jack_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
