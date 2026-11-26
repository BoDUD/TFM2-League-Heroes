#!/usr/bin/env python3
"""秦始皇（ragnarok_qin）Codex 交的图收色：身体和特效。

    python tools/art/qin_fix.py            # 读 assets/source/qin/runtime/sprites，写 assets/source/qin/snapped
    python tools/art/qin_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_qin.py、ppu_hd.py --hero qin、hero_reels.py --hero qin

Codex 2026-11-22 交的（qin_packs/outputs/qin_assets_done.zip，以提交 969382a77 为准）：一格 256，脚底 (128, 232)，8 个动作
各 8 帧，特效八组各 8 帧（指爪的爪痕和命中、波流龟的气弹和炸开、神罗铠袖的护势、承力天凤的回推、始皇勾践剑的显形和斩击）。
勾践剑只在大招第 3-7 帧出现，Codex 照 sword-registration.json 贴的：每帧同一把剑、同一个长度（87），只转角度，不用改。
和小次郎一样（tools/art/kojiro_fix.py 有来由）收色：身体 64 色，特效每组 32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "qin", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "qin", "snapped")
BODY = ("ragnarok_qin_native",)
FX = "ragnarok_qin_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
