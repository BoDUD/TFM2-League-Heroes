#!/usr/bin/env python3
"""澜缇（边境巡团 border_lanti，反击战士）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_lanti.py [--check]
    python tools/art/ppu_hd.py --hero lanti         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero lanti     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)。共用的设定、特效的放法在 tools/art/border_art.py。没有画进她自己帧里的特效。
放在单位身上的：普攻打中 a_hit（attack）、受击 hit、双棱每一拳打中时的拳光 q_punch（skill）：接触点 (64, 68)；
折纹 p_mark（passive，被标记的敌人身上的镜纹）、候击 e_guard（skill2，围着她的翡翠护环）：身上的 (64, 84)。
q_punch 画的拳头朝右（特效图不会跟着左右翻）：另出一张左右翻过来的 q_punch_l，border.dll 按她出拳的方向挑
（她在目标右边、往左打时放 _l）。
弹道图（1 倍，border/effects/border_lanti_proj，朝右）：还响往前推的玻璃浪 r_wave（ult 四帧，中心 (63, 68)），
r_wave_l 是它上下翻过来的（往左推时引擎把图转 180 度，翻过来的转回来还是正的）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

TARGET_FX = {"a_hit": B.CONTACT, "hit": B.CONTACT, "p_mark": B.BODY, "q_punch": B.CONTACT, "q_punch_l": B.CONTACT,
             "e_guard": B.BODY}
PROJ_FX = {"r_wave": (63, 68), "r_wave_l": (63, 68)}


def fx_make(fx):
    return {"a_hit": fx["attack"], "p_mark": fx["passive"], "q_punch": fx["skill"], "q_punch_l": B.flip_lr(fx["skill"]),
            "e_guard": fx["skill2"],
            "r_wave": fx["ult"], "r_wave_l": B.flip_tb(fx["ult"])}


LANTI = B.config("lanti", TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(LANTI, __doc__)
