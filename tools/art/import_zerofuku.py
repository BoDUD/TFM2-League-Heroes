#!/usr/bin/env python3
"""零福／波旬（终末包 ragnarok_zerofuku）的图：Codex 交的两倍密度身体（零福、波旬）和特效（assets/source/zerofuku）。

    python tools/art/zerofuku_fix.py                    # 先重贴斧爻、收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_zerofuku.py [--check]
    python tools/art/ppu_hd.py --hero zerofuku          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero zerofuku      # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-22 画的（zerofuku_packs/outputs/zerofuku_assets_done.zip 和之后的提交 e8ff128fd，交接说明
assets/source/zerofuku/HANDOFF.md）：动画第二季第六回合的零福（长紫发、红角、扛着斧爻）和吞了他破茧出来的波旬（银发、长赤角，
前臂能化成刃和钻）。一格 256（零福重贴斧子以后宽 272，见 zerofuku_fix.py），脚底 (128, 232)。零福站直 116 格、波旬连角 125 格，
PPU 3.3 是 35、38 个游戏像素（原作里波旬就比零福高大）。引擎是 tools/art/ragnarok_art.py。

两张图合成一张（BANKS）：零福 8 个动作原名；波旬 8 个动作 h_*。大招 ult 是破茧本身（零福被暗茧吞没，第 6 帧 0.58 秒波旬现身）。
ragnarok.dll（addons/ragnarok/src/zerofuku.rs）的显示钩子在他身上有波旬的 buff 时把待机、跑、普攻、两个技能、挨打、倒下换成 h_*；
波旬再放大招（重臂刃横断）数据用 CasterAnimation 放 h_ult。两种形态的普攻、Q 共用一个动作长度：h_attack、h_skill 按零福的节奏
重排时长（RETIME：普攻第 5 帧打到的时刻 0.287 秒、总长 0.606 秒；Q 第 5 帧 0.285 秒、总长 0.583 秒）；h_ult 挥刃的快慢不动，
最后一帧收势多站一会儿，凑满破茧的 0.93 秒（大招一个动作长度）。E 两版一样长，不用排。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点。扫过头、脸的画在身后（"behind"，用户说过盖住脸不行）：
斧爻的斩痕（普攻 0.236 秒、Q 落斧 0.285 秒）、Q 蓄的不幸 0.176 秒、破茧的碎壳 0.58 秒、波旬臂刃的斩痕（普攻、E、大招）和魔钻
的螺旋；E 的怨气从脚下涌出，画在前面。
放在目标身上的：斧爻的命中 cleaver_impact、波旬的命中 demon_impact、被动挂上的不幸 misfortune。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zerofuku", "snapped")
ID = "ragnarok_zerofuku"
HERO = "zerofuku"
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
    (f"{ID}_hajun_native", {t: t for t in H_ACTS}),
]
TAGS = list(ACTS) + list(H_ACTS)

# h_attack 81, 72, 57, 47 | 54, 64, 80, 100 毫秒 -> 前四帧 0.287 秒、后四帧 0.319 秒（和零福的普攻一样）
# h_skill 89, 73, 53, 44 | 48, 49, 72, 94 毫秒 -> 前四帧 0.285 秒、后四帧 0.298 秒（和零福的 Q 一样）
# h_ult 145, 113, 94, 71 | 61, 69, 99, 142 毫秒：挥刃不动，最后一帧 0.142 -> 0.278 秒，总长 0.93 秒（和破茧一样）
RETIME = {"h_attack": [0.090, 0.080, 0.064, 0.053, 0.058, 0.068, 0.086, 0.107],
          "h_skill": [0.098, 0.080, 0.058, 0.049, 0.054, 0.056, 0.082, 0.106],
          "h_ult": [0.145, 0.113, 0.094, 0.071, 0.061, 0.069, 0.099, 0.278]}


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "cleaver_arc", 0.236, at(171, 155), None, FX_ORIGIN, "behind"),
    ("skill", "misfortune", 0.176, at(150, 140), None, FX_ORIGIN, "behind"),
    ("skill", "cleaver_arc", 0.285, at(175, 153), None, FX_ORIGIN, "behind"),
    ("skill2", "ground_surge", 0.292, at(173, 214), None, FX_ORIGIN),
    ("ult", "shell_break", 0.580, at(129, 178), None, FX_ORIGIN, "behind"),
    # 波旬：普攻、Q 的时刻按重排后的（RETIME）
    ("h_attack", "demon_arc", 0.234, at(167, 151), None, FX_ORIGIN, "behind"),
    ("h_skill", "drill_spiral", 0.285, at(187, 153), None, FX_ORIGIN, "behind"),
    ("h_skill2", "demon_arc", 0.354, at(171, 174), None, FX_ORIGIN, "behind"),
    ("h_ult", "demon_arc", 0.423, at(186, 156), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"cleaver_impact": FX_ORIGIN, "demon_impact": FX_ORIGIN, "misfortune": FX_ORIGIN}

ZEROFUKU = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
            "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(ZEROFUKU, __doc__)
