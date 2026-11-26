#!/usr/bin/env python3
"""列奥尼达斯（终末包 ragnarok_leonidas）的图：Codex 交的两倍密度身体和特效（assets/source/leonidas）。

    python tools/art/leonidas_fix.py                   # 先重贴盾、收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_leonidas.py [--check]
    python tools/art/ppu_hd.py --hero leonidas         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero leonidas     # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-23 画的（leonidas_packs/outputs/leonidas_assets_done.zip，以提交 35546c8f5 为准，交接说明
assets/source/leonidas/HANDOFF.md）：动画第三季第九回合的样子（黑色战术上衣、白发束、银白胡须、脸上的旧疤、蓝迷彩裤），钢蓝的
圆盾，方阵冲锋时换成带 Λ 的红铜盾。一格 256，脚底 (128, 232)。普攻是盾击，技能是链盾（盾连着钢链甩出去再收回来）和举盾（挡下、
反弹光箭），大招是方阵冲锋。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点，除了尘土都画在前面（都在盾那一边，碰不到脸）：盾击的钢弧
0.236 秒，链盾飞盘的尾迹 0.237 秒、钢链回卷 0.336 秒，举盾的盾沿光 0.217 秒、反弹的光箭 0.354 秒（举盾时身上挂着反伤，这一下
就是挡回去的那一箭）；方阵冲锋脚下的尘土 0.423 秒画在身后（画在前面一大团盖住两条腿，冲锋扬起的土本来也在身后）。放在目标身上的：盾击和链盾的命中 shield_hit、方阵冲锋的冲击 phalanx_hit。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "leonidas", "snapped")
ID = "ragnarok_leonidas"
HERO = "leonidas"
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
    ("attack", "steel_sweep", 0.236, at(190, 151), None, FX_ORIGIN),
    ("skill", "discus_wake", 0.237, at(210, 146), None, FX_ORIGIN),
    ("skill", "chain_recoil", 0.336, at(180, 170), None, FX_ORIGIN),
    ("skill2", "brace_rim", 0.217, at(178, 162), None, FX_ORIGIN),
    ("skill2", "arrow_reflect", 0.354, at(184, 156), None, FX_ORIGIN),
    ("ult", "phalanx_dust", 0.423, at(156, 206), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"shield_hit": FX_ORIGIN, "phalanx_hit": FX_ORIGIN}

LEONIDAS = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
            "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(LEONIDAS, __doc__)
