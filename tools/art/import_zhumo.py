#!/usr/bin/env python3
"""铸沫（边境巡团 border_zhumo，铜火锻匠）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_zhumo.py [--check]
    python tools/art/ppu_hd.py --hero zhumo         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero zhumo     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)，站高 108 格（33 个游戏像素）。共用的设定、特效的放法在 tools/art/border_art.py。

画进他自己帧里的（跟着他左右翻）：
- 压坯 skill：熔铁往下砸的弧和地上的火星（特效八帧：第 1-4 张往下劈的弧，第 5 张砸地那下，第 6-8 张火星）。v0.7.0 起他
  先把锤举过头顶（到 0.20 秒），0.20 秒落锤、0.26 秒砸地，所以拆成两段放：弧 q_arc 0.18-0.26 秒每张 0.02 秒，跟着落锤，
  画在身后（他蹲得低，画在前面会糊在脸上）；砸地和火星 q_smash 0.26 秒起照特效自己的时长，画在前面。特效贴地的那条线
  量出来在第 102 行（砸地那张亮团的底 104-106、火星的底 97），这一点 (64, 102) 对上锤子落地处的地面 (153, 184)。
放在单位身上的：
- 普攻打中 a_hit（attack）、受击 hit：接触点；
- 回火 e_temper（skill2，围着他的几道金属环）、余温 p_heat（passive，余烬）：身上的 (64, 84)；
- 开炉 r_furnace（ult，炉火圈）：圈的中心对他脚底。量出来地上那圈椭圆在第 1 张的中线上是 78-84 行（后沿）和
  100-106 行（前沿），x=40 那边 83-103 行，圈心在第 92 行 -> (64, 54)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格里对上锚点的那点)
BAKE = [
    ("skill", "q_arc", 0.18, B.at(153, 184), 0.02, (64, 102), "behind"),
    ("skill", "q_smash", 0.26, B.at(153, 184), None, (64, 102)),
]
TARGET_FX = {"a_hit": B.CONTACT, "hit": B.CONTACT, "e_temper": B.BODY, "r_furnace": B.ground(92), "p_heat": B.BODY}


def fx_make(fx):
    return {"a_hit": fx["attack"], "e_temper": fx["skill2"], "r_furnace": fx["ult"], "p_heat": fx["passive"],
            "q_arc": fx["skill"][:4], "q_smash": fx["skill"][4:]}


ZHUMO = B.config("zhumo", BAKE=BAKE, TARGET_FX=TARGET_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(ZHUMO, __doc__)
