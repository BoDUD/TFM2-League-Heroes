#!/usr/bin/env python3
"""湿婆（终末包 ragnarok_shiva）的图：Codex 交的两倍密度身体（常态、轮回舞踊的燃烧形态）和特效（assets/source/shiva）。

    python tools/art/shiva_fix.py                   # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_shiva.py [--check]
    python tools/art/ppu_hd.py --hero shiva         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero shiva     # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-22 画的（shiva_packs/outputs/shiva_assets_done.zip，交接说明 assets/source/shiva/HANDOFF.md）：动画第二季第五回合的
造型，四臂、三眼、黄额巾；轮回舞踊的燃烧形态是赤铜肤色、散发。一格 256，脚底 (128, 232)，人站直 116 格，PPU 3.3 是 35 个游戏像素。
引擎是 tools/art/ragnarok_art.py。

两张图合成一张（BANKS）：常态 8 个动作原名；燃烧形态 8 个动作 h_*。大招 ult 是变身本身（第 5 帧 0.51 秒起已经是燃烧造型）。
ragnarok.dll（addons/ragnarok/src/shiva.rs）的显示钩子在他身上有轮回舞踊的 buff 时把待机、跑、普攻、两个技能、挨打、倒下换成 h_*；
形态结束时数据放 h_ult（最后一记高踢）。两种形态共用普攻和 Q 的动作：h_attack、h_skill 按常态的节奏重排时长（RETIME：普攻第 5 帧
打到的时刻 0.287 秒、总长 0.606 秒；Q 两下 0.237 / 0.336 秒、总长 0.583 秒），E 两版一样长，不用排。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点。扫过头、脸的画在身后（"behind"）：四臂的拳风 0.236 秒、
Q 的交叉 0.237 秒和横扫 0.336 秒、变身点燃的火 0.51 秒、燃烧形态的火鞭（普攻、Q、收尾高踢）；舞步、火步落在脚下，画在前面。
放在目标身上的：常态的命中 silver_hit、燃烧形态和高踢的命中 final_hit。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shiva", "snapped")
ID = "ragnarok_shiva"
HERO = "shiva"
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = 2.75                  # 放大前 3.3；和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图不放大（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (576, 448, (288, 352))

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
H_ACTS = tuple(f"h_{t}" for t in ACTS)
BANKS = [
    (f"{ID}_native", {t: t for t in ACTS}),
    (f"{ID}_tandava_native", {t: t for t in H_ACTS}),
]
TAGS = list(ACTS) + list(H_ACTS)
# h_attack 81, 72, 57, 47 | 54, 64, 80, 100 毫秒 -> 前四帧 0.287 秒、后四帧 0.319 秒（和常态普攻一样）
# h_skill 89, 73, 53 | 44, 48 | 49, 72, 94 毫秒 -> 0.237 | 0.099 | 0.247 秒（和常态 Q 一样两下打到的时刻）
RETIME = {"h_attack": [0.090, 0.080, 0.064, 0.053, 0.058, 0.068, 0.086, 0.107],
          "h_skill": [0.098, 0.080, 0.059, 0.047, 0.052, 0.056, 0.083, 0.108]}


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "arm_sweep", 0.236, at(159, 155), None, FX_ORIGIN, "behind"),
    ("skill", "dance_cross", 0.237, at(164, 149), None, FX_ORIGIN, "behind"),
    ("skill", "arm_sweep", 0.336, at(168, 158), None, FX_ORIGIN, "behind"),
    ("skill2", "dance_step", 0.292, at(126, 220), None, FX_ORIGIN),
    ("ult", "ignite", 0.510, at(125, 180), None, FX_ORIGIN, "behind"),
    # 燃烧形态：普攻和 Q 的时刻按重排后的（RETIME）
    ("h_attack", "flame_whip", 0.234, at(160, 150), None, FX_ORIGIN, "behind"),
    ("h_skill", "dance_cross", 0.237, at(160, 150), None, FX_ORIGIN, "behind"),
    ("h_skill", "flame_whip", 0.336, at(164, 152), None, FX_ORIGIN, "behind"),
    ("h_skill2", "firestep", 0.292, at(125, 222), None, FX_ORIGIN),
    ("h_ult", "flame_whip", 0.423, at(183, 155), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"silver_hit": FX_ORIGIN, "final_hit": FX_ORIGIN}

SHIVA = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
         "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(SHIVA, __doc__)
