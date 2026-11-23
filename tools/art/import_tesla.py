#!/usr/bin/env python3
"""尼古拉·特斯拉（终末包 ragnarok_tesla）的图：Codex 交的两倍密度身体和特效（assets/source/tesla）。

    python tools/art/tesla_fix.py                   # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_tesla.py [--check]
    python tools/art/ppu_hd.py --hero tesla         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero tesla     # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-23 画的（tesla_packs/outputs/tesla_assets_done.zip，以提交 7e3a2e0db 为准，交接说明 assets/source/tesla/HANDOFF.md）：
动画第三季的超人自动机兵 β（铜金外甲、深蓝关节、胸口线圈、青绿背环），一格 256，脚底 (128, 232)。普攻是等离子脉冲拳，技能是
特斯拉步（起跳、离场、到达）和神之监狱（金色的立方体牢笼），大招是双向电光拳（两拳）。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：普攻和大招两拳的拳风 0.236 / 0.423 / 0.510 秒画在身后；
特斯拉步脚下的拖痕 0.176 秒、到达的闪光 0.285 秒画在前面。放在别处的：
- 离场的闪光 warp_depart：数据在起跳那一拍放在他当时站的地方（不跟着走），瞬移以后还留在原地；
- 命中 punch_hit（普攻）、twin_impact（大招）放在目标身上；
- 神之监狱的牢笼 zone_deploy / zone_idle：套在被关的人身上，一个接一个放的特效画面（跟着人、不转方向、走高清；区域的画面会跟着
  施放方向转，方块牢笼一转就歪；buff 的画面游戏只画 1 倍，用户：「这个弄高清点」）。牢笼的底边对着脚底：单位的落点在脚底上面 FEET 个游戏像素，按特效图的密度是 FEET x FX_PPU 格，牢笼
  格子底边在 220 格，原点放在 220 - 38 = 182。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "tesla", "snapped")
ID = "ragnarok_tesla"
HERO = "tesla"
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
    ("attack", "plasma_punch", 0.236, at(187, 150), None, FX_ORIGIN, "behind"),
    ("skill", "step_trail", 0.176, at(98, 226), None, FX_ORIGIN),
    ("skill", "warp_arrive", 0.285, at(145, 177), None, FX_ORIGIN),
    ("ult", "plasma_punch", 0.423, at(184, 157), None, FX_ORIGIN, "behind"),
    ("ult", "plasma_punch", 0.510, at(198, 148), None, FX_ORIGIN, "behind"),
]
CAGE_BOTTOM = 220           # 牢笼格子的底边（特效格里的坐标）
CAGE = (128, CAGE_BOTTOM - round(A.FEET * FX_PPU))
TARGET_FX = {"punch_hit": FX_ORIGIN, "twin_impact": FX_ORIGIN, "warp_depart": FX_ORIGIN, "zone_deploy": CAGE, "zone_idle": CAGE}

TESLA = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
         "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(TESLA, __doc__)
