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

2026-11-26 照原作改（用户：「我需要的是完美的还原度」），Codex 补画了三个动作（assets/source/zerofuku/fidelity、fidelity_hajun，
逻辑像素图集）：
- skill2 换成斧爻岚阵（原作第六回合：斧爻炸成无数追着人飞的黑刃；「怨气冲击」原作没有）：第 5 帧 0.312 秒斧爻在头顶炸开的黑气
  画在身后，飞出去的黑刃是弹道（ragnarok_zerofuku_proj 的 blade_flight，第 4-6 帧循环，跟着飞行方向转）。
- h_skill 换成魔廻天衝（原作：右臂化成鞭刃拧成巨大的黑钻头射出去，刺穿释迦的盾、打掉他的左眼；原来画的是人冲过去）：黑钻头
  是弹道（drill_flight）。
- h_ult 换成灼（原作：扯下左臂变成大剑全力往下劈；原来画的是横斩）：第 5 帧 0.44 秒大剑劈下的竖光画在前面，命中的光 sword_hit
  打在目标身上。
原来 E 的怨气、魔钻的螺旋、波旬大招的横斩痕去掉。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

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
# 2026-11-26 照原作补画的三个动作（Codex 的 frames.json 秒数），和零福共用动作长度：
# - skill2 斧爻岚阵 0.784 秒，要和波旬的 h_skill2 一样塞进 E 的 43 拍（0.717 秒）：0.312 秒炸开、0.377 秒出刃不动，最后两帧
#   收势缩短（0.255 -> 0.188 秒）；
# - h_skill 魔廻天衝 0.78 秒，要塞进 Q 的 35 拍（0.583 秒）：第 4 帧 0.315 秒射出不动，射出以后的五帧按比例缩（0.465 -> 0.268 秒）；
# - h_ult 灼 0.848 秒，第 5 帧 0.44 秒劈下不动，最后一帧拉长到大招的 56 拍（0.933 秒）
RETIME = {"h_attack": [0.090, 0.080, 0.064, 0.053, 0.058, 0.068, 0.086, 0.107],
          "skill2": [0.12, 0.105, 0.087, 0.065, 0.073, 0.079, 0.083, 0.105],
          "h_skill": [0.115, 0.105, 0.095, 0.035, 0.043, 0.048, 0.064, 0.078],
          "h_ult": [0.125, 0.12, 0.095, 0.1, 0.065, 0.083, 0.11, 0.235]}
FID = os.path.join(ROOT, "assets", "source", "zerofuku", "fidelity")
HID = os.path.join(ROOT, "assets", "source", "zerofuku", "fidelity_hajun")
REDRAW = [(FID, "zerofuku", {"skill2": "skill2"}, None), (HID, "hajun", {"h_skill": "h_skill", "h_ult": "h_ult"}, None)]
REDRAW_FX = [(FID, "zerofuku", {"axe_burst": "axe_burst", "flying_blade": "flying_blade"}, None),
             (HID, "hajun", {"drill_launch": "drill_launch", "sword_drop": "sword_drop", "sword_hit": "sword_hit"}, None)]
# 飞出去的黑刃、黑钻头：Codex 写了飞的时候循环第 4-6 帧
FX_SLICE = {"blade_flight": ("flying_blade", 3, 6), "drill_flight": ("drill_launch", 3, 6)}


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "cleaver_arc", 0.236, at(171, 155), None, FX_ORIGIN, "behind"),
    ("skill", "misfortune", 0.176, at(150, 140), None, FX_ORIGIN, "behind"),
    ("skill", "cleaver_arc", 0.285, at(175, 153), None, FX_ORIGIN, "behind"),
    # 斧爻岚阵：第 5 帧 0.312 秒斧爻在头顶炸开（画在身后，Codex 给的位置）
    ("skill2", "axe_burst", 0.312, RA.redraw_offset(FID, "axe_burst"), None, RA.redraw_point(FID, "fx", "axe_burst"), "behind"),
    ("ult", "shell_break", 0.580, at(129, 178), None, FX_ORIGIN, "behind"),
    # 波旬：普攻、Q 的时刻按重排后的（RETIME）
    ("h_attack", "demon_arc", 0.234, at(167, 151), None, FX_ORIGIN, "behind"),
    ("h_skill2", "demon_arc", 0.354, at(171, 174), None, FX_ORIGIN, "behind"),
    # 灼：第 5 帧 0.44 秒大剑劈下的竖光（画在前面，不压脸）
    ("h_ult", "sword_drop", 0.44, RA.redraw_offset(HID, "sword_drop"), None, RA.redraw_point(HID, "fx", "sword_drop")),
]
TARGET_FX = {"cleaver_impact": FX_ORIGIN, "demon_impact": FX_ORIGIN, "misfortune": FX_ORIGIN,
             "sword_hit": RA.redraw_point(HID, "fx", "sword_hit")}
# 弹道：追着人飞的黑刃、射出去的黑钻头（中心是 Codex 的挂点；按身体的密度画的）
PROJ_FX = {"blade_flight": RA.redraw_point(FID, "fx", "flying_blade"),
           "drill_flight": RA.redraw_point(HID, "fx", "drill_launch")}
PROJ_DENSITY = {"blade_flight": PPU, "drill_flight": PPU}

ZEROFUKU = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
            "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS, "REDRAW": REDRAW,
            "REDRAW_FX": REDRAW_FX, "FX_SLICE": FX_SLICE, "PROJ_FX": PROJ_FX, "PROJ_DENSITY": PROJ_DENSITY}

if __name__ == "__main__":
    A.main(ZEROFUKU, __doc__)
