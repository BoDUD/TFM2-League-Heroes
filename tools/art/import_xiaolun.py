#!/usr/bin/env python3
"""绡轮（边境巡团 border_xiaolun，潮弩信使）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_xiaolun.py [--check]
    python tools/art/ppu_hd.py --hero xiaolun       # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero xiaolun   # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)，站高 102 格（31 个游戏像素）。共用的设定、特效的放法在 tools/art/border_art.py。

画进她自己帧里的（跟着她左右翻；都画在身后，不盖脸）：
- 切角 skill：两道钴蓝的侧步拖影，0.05 秒起（她第 2、3 帧侧滑），特效格的中心放在她身后起步的地方 (88, 160)；
- 放扣 skill2：弩扣上裂开的两片紫弧，0.26 秒起（第 3 帧，弩横在胸前），中心放在弩扣 (140, 132)。
弹道图（1 倍，border/effects/border_xiaolun_proj，朝右，引擎按飞的方向转）：普攻的银弩箭 a_bolt（attack 八帧，箭的中间在
图的中心 (57, 68)）、满弧每一发的星弧箭 r_arrow（ult 四帧，中心 (60, 68)）。
放在单位身上的：命中 a_hit（hit，接触点）、走弦 p_ring（passive，身上）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格里对上锚点的那点[, "behind"])
BAKE = [
    ("skill", "skill", 0.05, B.at(88, 160), None, B.FX_CENTRE, "behind"),
    ("skill2", "skill2", 0.26, B.at(140, 132), None, B.FX_CENTRE, "behind"),
]
TARGET_FX = {"a_hit": B.CONTACT, "p_ring": B.BODY}
PROJ_FX = {"a_bolt": (57, 68), "r_arrow": (60, 68)}


def fx_make(fx):
    return {"a_hit": fx["hit"], "p_ring": fx["passive"], "a_bolt": fx["attack"], "r_arrow": fx["ult"]}


XIAOLUN = B.config("xiaolun", BAKE=BAKE, TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(XIAOLUN, __doc__)
