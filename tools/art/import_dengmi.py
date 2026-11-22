#!/usr/bin/env python3
"""灯弥（边境巡团 border_dengmi，提灯师）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_dengmi.py [--check]
    python tools/art/ppu_hd.py --hero dengmi        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero dengmi    # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)，站高 104 格（32 个游戏像素）。共用的设定、特效的放法在 tools/art/border_art.py。
没有画进她自己帧里的特效。
弹道图（1 倍，border/effects/border_dengmi_proj）：普攻的琥珀灯火 a_mote（attack 八帧，中心 (58, 68)）。
放在单位身上的：
- 命中 a_hit（hit，接触点）；
- 递灯 q_shield（skill，六角薄盾套在队友身上）、存光 p_glow（passive，水母灯，身上）：身上的 B.BODY；
- 引路 e_path（skill2，三个脚印连着紫色的路）：贴地，脚印路的中间 (64, 68) 落在队友脚下 -> (64, 30)；
- 收灯 r_ring（ult，套环脉冲）：贴地，量出来圈的中心在第 74 行（第 2-4 帧圈上下沿的中点，顶上那颗星把整张图的中心
  抬到了 68），圈心落在目标脚下 -> (64, 36)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

TARGET_FX = {"a_hit": B.CONTACT, "q_shield": B.BODY, "e_path": B.ground(68), "r_ring": B.ground(74), "p_glow": B.BODY}
PROJ_FX = {"a_mote": (58, 68)}


def fx_make(fx):
    return {"a_hit": fx["hit"], "q_shield": fx["skill"], "e_path": fx["skill2"], "r_ring": fx["ult"],
            "p_glow": fx["passive"], "a_mote": fx["attack"]}


DENGMI = B.config("dengmi", TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(DENGMI, __doc__)
