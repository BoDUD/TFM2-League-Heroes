#!/usr/bin/env python3
"""赫拉克勒斯（终末包 ragnarok_heracles）的图：Codex 交的两倍密度身体（常态、刻耳柏洛斯形态）和特效（assets/source/heracles）。

    python tools/art/heracles_fix.py                # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_heracles.py [--check]
    python tools/art/ppu_hd.py --hero heracles      # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero heracles  # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-21 画的（heracles_packs/outputs/heracles_assets_done.zip，交接说明 assets/source/heracles/HANDOFF.md）：动画第二季
第四回合的造型，一格 256，脚底 (128, 232)，人站直 121 格，PPU 3.3 是 37 个游戏像素（比小次郎、波塞冬高三个像素：他本来就
是大个子）。引擎是 tools/art/ragnarok_art.py。

两张图合成一张（BANKS）：常态（拿狮头巨棒）8 个动作原名；第十二御业以后的刻耳柏洛斯形态（空手、肩背骨爪）8 个动作 c_*。
大招 ult 是变身本身（第 5 帧起已经空手）。ragnarok.dll（addons/ragnarok/src/heracles.rs）的显示钩子在他身上有刻耳柏洛斯的
buff 时把待机、跑、普攻、两个技能、挨打、倒下换成 c_*；形态结束时数据放 c_ult（最后一记重拳砸地）。
两种形态共用一个普攻：c_attack 按普攻的节奏重排时长（RETIME：第 5 帧拳头打到的那一刻落在 0.33 秒，和巨棒打到同一刻，
总长和普攻一样 0.671 秒）。两个技能的 c_ 版和常态的总长一样，不用排。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点。都很大（一组 200 格左右宽），扫过头、脸的
画在身后（"behind"，小次郎、索尔那次用户说过盖住脸不行）：巨棒挥出的弧光 0.272 秒、狮子御业的狮头 0.317 秒、变身的
光环 0.32 秒和觉醒 0.59 秒、拳风（c_attack 0.219 秒、c_ult 0.329 秒）、刻耳柏洛斯护势的光环 0.218 秒；砸在他前面地上的
冲击（skill2 0.371 秒、c_ult 0.401 秒）画在前面。放在目标身上的：巨棒命中 club_hit、拳头命中 cerberus_hit。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heracles", "snapped")
ID = "ragnarok_heracles"
HERO = "heracles"
PPU = 3.3                   # 和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (576, 448, (288, 352))

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
C_ACTS = tuple(f"c_{t}" for t in ACTS)
BANKS = [
    (f"{ID}_native", {t: t for t in ACTS}),
    (f"{ID}_cerberus_native", {t: t for t in C_ACTS}),
]
TAGS = list(ACTS) + list(C_ACTS)
# c_attack 87, 75, 57, 49 | 56, 63, 83, 105 毫秒：前四帧拉到 0.33 秒（普攻第 5 帧打到的时刻）、后四帧拉到 0.341 秒
RETIME = {"c_attack": [0.107, 0.092, 0.070, 0.061, 0.062, 0.070, 0.092, 0.117]}


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "club_swing", 0.272, at(160, 154), None, FX_ORIGIN, "behind"),
    ("skill", "lion_wave", 0.317, at(165, 155), None, FX_ORIGIN, "behind"),
    ("skill2", "ground_impact", 0.371, at(184, 218), None, FX_ORIGIN),
    ("ult", "cerberus_ring", 0.320, at(128, 161), None, FX_ORIGIN, "behind"),
    ("ult", "cerberus_awaken", 0.590, at(128, 150), None, FX_ORIGIN, "behind"),
    ("c_attack", "fist_trail", 0.270, at(166, 156), None, FX_ORIGIN, "behind"),
    ("c_skill2", "cerberus_ring", 0.218, at(128, 162), None, FX_ORIGIN, "behind"),
    ("c_ult", "fist_trail", 0.329, at(164, 144), None, FX_ORIGIN, "behind"),
    ("c_ult", "ground_impact", 0.401, at(181, 202), None, FX_ORIGIN),
]
TARGET_FX = {"club_hit": FX_ORIGIN, "cerberus_hit": FX_ORIGIN}

HERACLES = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
            "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS}

if __name__ == "__main__":
    A.main(HERACLES, __doc__)
