#!/usr/bin/env python3
"""秦始皇（终末包 ragnarok_qin）的图：Codex 交的两倍密度身体和特效（assets/source/qin）。

    python tools/art/qin_fix.py                     # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_qin.py [--check]
    python tools/art/ppu_hd.py --hero qin           # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero qin       # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-22 画的（qin_packs/outputs/qin_assets_done.zip，以提交 969382a77 为准，交接说明 assets/source/qin/HANDOFF.md）：
动画第三季的造型（白眼罩、红纹、金指爪、红金外袍），一格 256，脚底 (128, 232)。普攻是指爪，技能是波流龟气弹（吸一口气吐出
气弹）和神罗铠袖·承力天凤（举袖接住，再回推），大招是始皇勾践剑（显剑时摘下眼罩）。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：指爪的爪痕 0.236 秒、天凤回推 0.354 秒、勾践剑显形的
剑光 0.305 秒和斩出去的剑痕 0.510 秒，扫过身前，画在身后；神罗铠袖的护势 0.217 秒就是两条袖子上的光，画在前面。
放在目标身上的：指爪的命中 claw_impact（普攻、天凤、勾践剑都用）、气弹炸开的星 star_pop。飞出去的气弹：
ragnarok/effects/ragnarok_qin_proj，1 倍（PROJ_FX，跟着飞行方向转；它是个圆泡，转了看着一样）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "qin", "snapped")
ID = "ragnarok_qin"
HERO = "qin"
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
    ("attack", "claw_arc", 0.236, at(170, 158), None, FX_ORIGIN, "behind"),
    ("skill2", "armor_guard", 0.217, at(147, 155), None, FX_ORIGIN),
    ("skill2", "phoenix_reversal", 0.354, at(172, 158), None, FX_ORIGIN, "behind"),
    ("ult", "sword_glint", 0.305, at(151, 154), None, FX_ORIGIN, "behind"),
    ("ult", "jian_slash", 0.510, at(183, 148), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"claw_impact": FX_ORIGIN, "star_pop": FX_ORIGIN}
PROJ_FX = {"air_bubble": FX_ORIGIN}

QIN = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
       "TARGET_FX": TARGET_FX, "PROJ_FX": PROJ_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(QIN, __doc__)
