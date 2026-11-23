#!/usr/bin/env python3
"""别西卜（终末包 ragnarok_beelzebub）的图：Codex 交的两倍密度身体和特效（assets/source/beelzebub）。

    python tools/art/beelzebub_fix.py               # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_beelzebub.py [--check]
    python tools/art/ppu_hd.py --hero beelzebub     # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero beelzebub # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-23 画的（beelzebub_packs/outputs/beelzebub_assets_done.zip，以提交 ce16a3f54 为准，交接说明
assets/source/beelzebub/HANDOFF.md）：动画第三季的造型（黑发、深色高领长袍、紫纹长带、阿波弥俄斯骸骨杖），一格 256，
脚底 (128, 232)。普攻是右手的振动掌，技能是骸骨杖放的振动波（暴食的堕天使）和地狱之门的振动屏障，大招是虚神〈混沌〉。
引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：振动掌的掌风 0.236 秒、振动波 0.237 秒和扩散的波纹
0.285 秒，扫过身前，画在身后；地狱之门的屏障 0.217 秒、格挡涟漪 0.354 秒是挡在他身前的，画在前面；混沌的黑核 0.305 秒在他手前，
画在前面；爆发 0.510 秒一开始是个比他还大的黑球，画在前面会把人连脸整个盖住，画在身后。放在目标身上的：振动掌的命中 palm_hit（普攻、振动波、混沌都用）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "beelzebub", "snapped")
ID = "ragnarok_beelzebub"
HERO = "beelzebub"
# 和别的终末英雄一样按联盟英雄的个子（2026-11-22「放大到联盟大小」以后的 PPU）：特效图（FX_PPU）不放大，命中和范围按游戏里的距离走
PPU = 2.75                  # 和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (576, 448, (288, 352))

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
BANKS = [(f"{ID}_native", {t: t for t in ACTS})]
TAGS = list(ACTS)


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "palm_cut", 0.236, at(172, 155), None, FX_ORIGIN, "behind"),
    ("skill", "sorat_wave", 0.237, at(222, 150), None, FX_ORIGIN, "behind"),
    ("skill", "dark_ripples", 0.285, at(203, 176), None, FX_ORIGIN, "behind"),
    ("skill2", "guard_field", 0.217, at(164, 160), None, FX_ORIGIN),
    ("skill2", "guard_block", 0.354, at(177, 157), None, FX_ORIGIN),
    ("ult", "chaos_core", 0.305, at(155, 161), None, FX_ORIGIN),
    ("ult", "chaos_burst", 0.510, at(155, 161), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"palm_hit": FX_ORIGIN}

BEELZEBUB = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
             "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(BEELZEBUB, __doc__)
