#!/usr/bin/env python3
"""须佐之男命（终末包 ragnarok_susanoo）的图：Codex 交的逻辑像素图集（assets/source/susanoo/atlases）。

    python tools/art/import_susanoo.py [--check]
    python tools/art/ppu_hd.py --hero susanoo        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero susanoo    # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-23 画的（susanoo_packs/output，提交 890ad4437，交接说明 assets/source/susanoo/HANDOFF.md）：漫画彩页的样子
（深蓝长发、银白刘海、鬼面肩甲），一把鬼切天叢雲，Q 版像素画。一格 132×96 逻辑像素，脚底 (60, 88)，人站直 56 格；特效格
同样大，中心 (66, 48)。和冲田一样（tools/art/import_okita.py）：两倍最近邻读进来，PPU 8/3，站直 42 个游戏像素，特效和人
一个比例。

Codex 只给了时间（frames.json 的 cues），没给位置；位置照他的刀和手在那一帧的地方定（逻辑像素，离脚底），不挡脸
（脸在脚底往上 40-51 格、往前 -2 到 16 格）：
- 普攻第 4 帧（0.28 秒）的刀光 slash：刀从头顶往前劈下，刀光放在身前；
- 天魔反（skill）第 1 帧（0 秒）的蓄势 windup 画在身后，第 5 帧（0.3 秒）的剑压 wave 在刀尖前面往前冲；
- 异形架势（skill2）第 2 帧（0.105 秒）的架势剑气 stance_aura 画在身后，第 5 帧（0.39 秒）的架势释放 stance_flash 在身前；
- 无装剑（ult）第 1 帧（0 秒）的蓄势 last_windup、第 4 帧（0.3 秒）伸出的手前面的裂光 last_cut。
放在目标身上的：命中火花 hit_spark。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "susanoo")
ID = "ragnarok_susanoo"
HERO = "susanoo"
PPU = 2.667                 # 8/3，和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 2.667
SOLE = RA.scaled((60, 88))
FX_ORIGIN = RA.scaled((66, 48))
CANVAS = (480, 320, (200, 260))


def at(dx, dy):
    """偏移（离脚底，逻辑像素）-> 放大后的偏移。"""
    return RA.scaled((dx, dy))


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "slash", 0.28, at(30, -34), None, FX_ORIGIN),
    ("skill", "windup", 0.0, at(10, -26), None, FX_ORIGIN, "behind"),
    ("skill", "wave", 0.3, at(58, -40), None, FX_ORIGIN),
    ("skill2", "stance_aura", 0.105, at(0, -24), None, FX_ORIGIN, "behind"),
    ("skill2", "stance_flash", 0.39, at(30, -28), None, FX_ORIGIN),
    ("ult", "last_windup", 0.0, at(14, -30), None, FX_ORIGIN, "behind"),
    ("ult", "last_cut", 0.3, at(52, -38), None, FX_ORIGIN),
]
TARGET_FX = {"hit_spark": FX_ORIGIN}

SUSANOO = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
           "TARGET_FX": TARGET_FX, "CANVAS": CANVAS, "READ": RA.reader(SRC, "susanoo", ID)}

if __name__ == "__main__":
    A.main(SUSANOO, __doc__)
