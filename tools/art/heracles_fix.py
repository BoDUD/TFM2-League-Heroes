#!/usr/bin/env python3
"""赫拉克勒斯（ragnarok_heracles）Codex 交的图收色：常态、刻耳柏洛斯形态两张身体图和特效。

    python tools/art/heracles_fix.py            # 读 assets/source/heracles/runtime/sprites，写 assets/source/heracles/snapped
    python tools/art/heracles_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_heracles.py、ppu_hd.py --hero heracles、hero_reels.py --hero heracles

Codex 2026-11-21 交的（heracles_packs/outputs/heracles_assets_done.zip）：一格 256，脚底 (128, 232)，常态拿狮头巨棒 8 个动作、
第十二御业以后空手的刻耳柏洛斯形态 8 个动作（c_*），各 8 帧；特效八组各 8 帧。图是缩小的手绘，颜色几万种，和小次郎一样
（tools/art/kojiro_fix.py 有来由）收色：两张身体图合起来 64 色（同一套调色板，变身时皮肤、头发、皮裙的颜色不跳），
特效每组 32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heracles", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "heracles", "snapped")
BODY = ("ragnarok_heracles_native", "ragnarok_heracles_cerberus_native")
FX = "ragnarok_heracles_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
