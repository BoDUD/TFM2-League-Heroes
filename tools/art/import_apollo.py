#!/usr/bin/env python3
"""阿波罗（终末包 ragnarok_apollo）的图：Codex 交的两倍密度身体和特效（assets/source/apollo）。

    python tools/art/apollo_fix.py                   # 先重贴弓和女神像、收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_apollo.py [--check]
    python tools/art/ppu_hd.py --hero apollo         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero apollo     # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-23 画的（apollo_packs/outputs/apollo_assets_done.zip，以提交 ab889d460 为准，交接说明
assets/source/apollo/HANDOFF.md）：动画第三季第九回合的样子（粉红长发、金月桂、白底金蓝刺绣的衣服、金蓝拳甲）。一格 256，
脚底 (128, 232)。普攻是日轮拳，技能是阿尔忒弥斯之丝（光丝缠住目标）和光之矢（光弓成形、拉弦、放箭），大招是银箭突进
（阿尔忒弥斯的女神像在身后显现，用光索把阿波罗自己当银箭射出去）。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：
- 日轮拳的拳光 0.236 秒、光丝投出 0.237 秒、离弦的光 0.354 秒画在前面；
- 光弓成形的光 0.217 秒、女神像显现的光 0.305 秒画在身后：那是一个大日轮（126×114 格），画在前面会盖住他的脸，女神像那次
  还整个盖住女神像；画在身后就是从他（和像）背后透出来的一圈光；
- 银箭突进 0.510 秒：金色的箭影，画在身后（他自己就是那支箭，箭影裹着他；画在前面会从脸上划过去），箭头对着出拳的手
  （特效格里的 (170, 128) 放在手上，箭影最长的时候箭尖在拳头前面一点），手跟着身体走：第 5 帧在 (199, 154)、离地以后
  在 (193, 139)（Codex 的 follow）。
放在别处的：日轮拳和光箭的命中 punch_hit、光丝的收束 thread_bind 放在目标身上；光箭 light_arrow 是弹道画面（1 倍，跟着飞的
方向转）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "apollo", "snapped")
ID = "ragnarok_apollo"
HERO = "apollo"
# 和别的终末英雄一样按联盟英雄的个子（2026-11-22「放大到联盟大小」以后的 PPU）：特效图（FX_PPU）不放大，命中和范围按游戏里的距离走
PPU = 2.75                  # 和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
DASH_TIP = (170, 128)       # 银箭的箭影放在手上的那一点（箭尖最远到 189）
CANVAS = (576, 448, (288, 352))

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
BANKS = [(f"{ID}_native", {t: t for t in ACTS})]
TAGS = list(ACTS)


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# 银箭突进时出拳的手（大招的 8 个身体帧，第 5 帧以前用不到）
FIST = [at(199, 154)] * 5 + [at(193, 139)] * 3

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "sun_jab", 0.236, at(175, 153), None, FX_ORIGIN),
    ("skill", "thread_cast", 0.237, at(173, 159), None, FX_ORIGIN),
    ("skill2", "summon", 0.217, at(159, 160), None, FX_ORIGIN, "behind"),
    ("skill2", "bow_release", 0.354, at(182, 151), None, FX_ORIGIN),
    ("ult", "summon", 0.305, at(88, 148), None, FX_ORIGIN, "behind"),
    ("ult", "sun_dash", 0.510, FIST, None, DASH_TIP, "behind"),
]
TARGET_FX = {"punch_hit": FX_ORIGIN, "thread_bind": FX_ORIGIN}
PROJ_FX = {"light_arrow": FX_ORIGIN}

APOLLO = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
          "TARGET_FX": TARGET_FX, "PROJ_FX": PROJ_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(APOLLO, __doc__)
