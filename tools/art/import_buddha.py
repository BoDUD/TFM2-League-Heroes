#!/usr/bin/env python3
"""释迦（终末包 ragnarok_buddha）的图：Codex 交的两倍密度身体和特效（assets/source/buddha）。

    python tools/art/buddha_fix.py                  # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_buddha.py [--check]
    python tools/art/ppu_hd.py --hero buddha        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero buddha    # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-22 画的（buddha_packs/outputs/buddha_assets_done.zip，交接说明 assets/source/buddha/HANDOFF.md）：动画第二季的造型
（银灰发髻、粉色眼镜、深蓝背心、白紫下装、金色披带），一格 256，脚底 (128, 232)，PPU 3.3。普攻是六道棍，技能是六道棍变的枪刃
和观音盾，大招是第 15 话的大圆寂刀·零（七枝刀的样子），受击是未来视看穿以后的撤步。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：扫过身前、靠近脸的画在身后（"behind"，用户说过盖住
脸不行）：普攻的棍风 0.236 秒、枪刃的棍风 0.237 秒、未来视的准星 0.122 秒（罩着眼镜，在头后面只露出外圈）、观音盾的莲光
0.217 秒、大圆寂刀蓄的气 0.305 秒和斩出去的刀光 0.510 秒；撤步的气流 0.141 秒在脚下，画在前面。
放在目标身上的：棍的命中 staff_impact、观音盾挡击 shield_impact；放在他身上的：未来视 future_sight（被动）、莲光 lotus_guard
（观音盾收起时）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "buddha", "snapped")
ID = "ragnarok_buddha"
HERO = "buddha"
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = 2.75                  # 放大前 3.3；和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图不放大（hd.rs 的 EFFECTS）
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
    ("attack", "staff_sweep", 0.236, at(170, 159), None, FX_ORIGIN, "behind"),
    ("skill", "staff_sweep", 0.237, at(178, 157), None, FX_ORIGIN, "behind"),
    ("skill2", "future_sight", 0.122, at(142, 118), None, FX_ORIGIN, "behind"),
    ("skill2", "lotus_guard", 0.217, at(165, 164), None, FX_ORIGIN, "behind"),
    ("hit", "dodge_trail", 0.141, at(115, 224), None, FX_ORIGIN),
    ("ult", "nirvana_charge", 0.305, at(157, 156), None, FX_ORIGIN, "behind"),
    ("ult", "nirvana_slash", 0.510, at(183, 153), None, FX_ORIGIN, "behind"),
]
# 放在他身上的两个按身子对位：单位的落点在脚底上面 FEET 个游戏像素，眼镜、胸口离脚底 GLASSES、CHEST 格（高清帧），
# 两者差多少游戏像素按特效图的密度换成格挪上去（左右不挪，转身时不偏）；打在别人身上的和别的英雄一样放在落点
# 放大以后：眼镜离脚底 114 格 / PPU 个游戏像素，落点离脚底 FEET 个游戏像素，差多少按特效图的密度换成格（准星 +99、莲光 +46）
GLASSES, CHEST = 114, 70
TARGET_FX = {"staff_impact": FX_ORIGIN, "shield_impact": FX_ORIGIN,
             "future_sight": (128, 128 + round((GLASSES / PPU - A.FEET) * FX_PPU)),
             "lotus_guard": (128, 128 + round((CHEST / PPU - A.FEET) * FX_PPU))}

BUDDHA = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
          "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(BUDDHA, __doc__)
