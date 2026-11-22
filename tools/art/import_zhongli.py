#!/usr/bin/env python3
"""钟砾（边境巡团 border_zhongli，站桩射手）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_zhongli.py [--check]
    python tools/art/ppu_hd.py --hero zhongli       # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero zhongli   # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)。共用的设定、特效的放法在 tools/art/border_art.py。

画进他自己帧里的（跟着他左右翻）：
- 压簧 skill：机械臂上的弹簧和琥珀色的蓄力，第 2、3 帧（0.14-0.38 秒）放，跟着前臂走：第 2 帧双臂收在胸前，弹簧的中心
  放在臂甲 (110, 124)；第 3、4 帧手臂伸直，放在前臂 (156, 114)。画在身后（弹簧比他的前臂大，画在前面会盖住脸）。
放在单位身上的：命中 a_hit（hit）：接触点；落架 e_shield（skill2，琥珀小盾）：身上的 (64, 84)；
定脚 p_feet（passive，两只机械支脚落地）：放在他自己脚下，支脚落稳时底边在第 88 行 -> (64, 50)。
弹道图（1 倍，border/effects/border_zhongli_proj，朝右）：普攻 a_bolt（attack 八帧，中心 (57, 68)）、
齐鸣每一发 r_bolt（ult 四帧，中心 (63, 68)）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

# (动作, 特效, 开始秒, 离脚底的锚点（按身体帧给一串）, 每帧秒数, 特效格里对上锚点的那点, "behind")
BAKE = [
    ("skill", "skill", 0.14, [B.at(110, 124), B.at(110, 124), B.at(156, 114), B.at(156, 114)], None, B.FX_CENTRE,
     "behind"),
]
TARGET_FX = {"a_hit": B.CONTACT, "p_feet": B.ground(88), "e_shield": B.BODY}
PROJ_FX = {"a_bolt": (57, 68), "r_bolt": (63, 68)}


def fx_make(fx):
    return {"a_hit": fx["hit"], "p_feet": fx["passive"], "e_shield": fx["skill2"], "a_bolt": fx["attack"],
            "r_bolt": fx["ult"]}


ZHONGLI = B.config("zhongli", BAKE=BAKE, TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(ZHONGLI, __doc__)
