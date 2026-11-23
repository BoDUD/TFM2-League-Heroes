#!/usr/bin/env python3
"""别西卜（ragnarok_beelzebub）Codex 交的图收色：身体和特效。

    python tools/art/beelzebub_fix.py            # 读 assets/source/beelzebub/runtime/sprites，写 assets/source/beelzebub/snapped
    python tools/art/beelzebub_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_beelzebub.py、ppu_hd.py --hero beelzebub、hero_reels.py --hero beelzebub

Codex 2026-11-23 交的（beelzebub_packs/outputs/beelzebub_assets_done.zip，以提交 ce16a3f54 为准）：一格 256，脚底 (128, 232)，8 个动作
各 8 帧，特效八组各 8 帧（振动掌的掌风和命中、暴食的堕天使的振动波和扩散的波纹、地狱之门的屏障和格挡涟漪、虚神〈混沌〉的黑核和爆发）。
骸骨杖（阿波弥俄斯）是 Codex 照 staff-registration.json 贴的同一根直杖，每帧长度一样（103），待机的角度跟着呼吸慢慢摆
（-115° 到 -118°，不是来回跳），掉杖以后四帧锁住，不用改。
和小次郎一样（tools/art/kojiro_fix.py 有来由）收色：身体 64 色，特效每组 32 色。Codex 的原样在 runtime/sprites，只读。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "beelzebub", "runtime", "sprites")
OUT = os.path.join(ROOT, "assets", "source", "beelzebub", "snapped")
BODY = ("ragnarok_beelzebub_native",)
FX = "ragnarok_beelzebub_fx_native"


def make(_up=None):
    return R.snap_delivery(SRC, OUT, BODY, FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
