#!/usr/bin/env python3
"""哈迪斯（终末包 ragnarok_hades）的图：Codex 交的两倍密度身体和特效（assets/source/hades）。

    python tools/art/hades_fix.py                   # 先重贴待机的枪、收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_hades.py [--check]
    python tools/art/ppu_hd.py --hero hades         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero hades     # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-22 画的（hades_packs/outputs/hades_assets_done.zip，以提交 6adc388f9 为准，交接说明 assets/source/hades/HANDOFF.md）：
动画第三季的造型（白外套、银发、蓝额纹），一格 256，脚底 (128, 232)。普攻是双叉枪直刺，技能是珀耳塞福涅式的风压斩和双叉枪
重砸，大招是换上强化枪头（伊科尔·德斯莫斯）后的直线突刺（这一段换成无袖战斗服，收招回到常态）。引擎是 tools/art/ragnarok_art.py。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点：刺出去的枪风 0.236 秒、风压斩 0.237 秒、伊科尔觉醒
0.305 秒（绕着枪头的血光，在枪后面，不挡枪和手）、德斯莫斯的突刺 0.510 秒，这些扫过身前，画在身后；重砸砸开的地面 0.354 秒和
扬起的尘土 0.425 秒在脚下，画在前面。放在目标身上的：枪的命中 thrust_hit、德斯莫斯的命中 desmos_hit。

2026-11-26 照原作改（用户：「我需要的是完美的还原度」）：skill 换成 Codex 补画的冥府の鉄槌（ペルセポネ・カリコロン，
assets/source/hades/fidelity，逻辑像素图集，按他 Q 版的像素格 2x2；原作第七回合：跳起来往下刺，地面炸开、甩出风刃）：第 5 帧
0.38 秒落枪爆地（他这时蹲得很低，爆地照 Codex 的位置画在前面会盖住脸，放到身后）和往前甩出的风刃（画在前面）。跳起落下是原地，
画里的前后移动不扣（最后一帧回到原处）。原来原地挥枪的风压 wind_crescent 去掉。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "hades", "snapped")
ID = "ragnarok_hades"
HERO = "hades"
# 和别的终末英雄一样按联盟英雄的个子（2026-11-22「放大到联盟大小」以后的 PPU）：特效图（FX_PPU）不放大，命中和范围按游戏里的距离走
PPU = 2.75                  # 和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (840, 520, (300, 420))   # 2026-11-26 补画的特效往前甩得远（原来 (576, 448, (288, 352))）

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
BANKS = [(f"{ID}_native", {t: t for t in ACTS})]
TAGS = list(ACTS)


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
FID = os.path.join(ROOT, "assets", "source", "hades", "fidelity")
REDRAW = [(FID, "hades", {"skill": "skill"}, None)]
# 他原来的 E 也有一条 ground_break：补画的落枪爆地改名 spear_break
REDRAW_FX = [(FID, "hades", {"ground_break": "spear_break", "air_edge": "air_edge"}, None)]
BAKE = [
    ("attack", "thrust", 0.236, at(210, 155), None, FX_ORIGIN, "behind"),
    # 冥府の鉄槌：0.38 秒落枪爆地（身后）、往前甩出的风刃（前面）
    ("skill", "spear_break", 0.38, RA.redraw_offset(FID, "ground_break"), None, RA.redraw_point(FID, "fx", "ground_break"),
     "behind"),
    ("skill", "air_edge", 0.38, RA.redraw_offset(FID, "air_edge"), None, RA.redraw_point(FID, "fx", "air_edge")),
    ("skill2", "ground_break", 0.354, at(207, 218), None, FX_ORIGIN),
    ("skill2", "sweep_dust", 0.425, at(166, 219), None, FX_ORIGIN),
    ("ult", "ichor_awakening", 0.305, at(161, 150), None, FX_ORIGIN, "behind"),
    ("ult", "desmos_thrust", 0.510, at(215, 161), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"thrust_hit": FX_ORIGIN, "desmos_hit": FX_ORIGIN}

HADES = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
         "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS,
         "REDRAW": REDRAW, "REDRAW_FX": REDRAW_FX}

if __name__ == "__main__":
    A.main(HADES, __doc__)
