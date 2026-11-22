#!/usr/bin/env python3
"""岑垒（边境巡团 border_cenlei，珊瑚盾卫）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_cenlei.py [--check]
    python tools/art/ppu_hd.py --hero cenlei        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero cenlei    # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)，站高 110 格（PPU 3.3 是 33 个游戏像素）。共用的设定、特效的放法在 tools/art/border_art.py。

画进他自己帧里的（跟着他左右翻）：
- 横楔 skill：朝右的盾扫，0.20 秒起每帧 0.03 秒（特效八帧；Codex 的 0.039 一帧要放到他收盾以后才最亮，看着和盾脱节）：
  0.26 秒（盾推到身前、技能打中）扫过盾面，最亮那下在 0.32-0.35 秒，还在出盾的那几帧里（0.20-0.37 秒）；特效格的中心放在盾前
  (190, 146)（盾的中心约 (180, 146)），最亮那下在脚底前面 37 个游戏像素；
- 卸城 ult：三道浪楔一个扇面，0.40 秒（盾压在身前下方）起，扇面收拢的那点（特效格 (22, 70)）放在盾的前沿 (176, 152)。
放在单位身上的：普攻打中 a_hit（attack，接触点）、受击 hit（接触点）、接肩 e_ward（skill2，套在队友身上）、
背压 p_pearl（passive，身上）。
弹道图 r_fan（1 倍，border/effects/border_cenlei_proj）：同一个扇面（ult 八帧各 0.05 秒），朝右，扇面的中间在图的中心，
宽 35 个游戏像素；只在塞拉斯偷到卸城时用（线形区域 46000 长，引擎按施法方向转）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格里对上锚点的那点)
BAKE = [
    ("skill", "skill", 0.20, B.at(190, 146), 0.03, B.FX_CENTRE),
    ("ult", "ult", 0.40, B.at(176, 152), None, (22, 70)),
]
TARGET_FX = {"a_hit": B.CONTACT, "hit": B.CONTACT, "e_ward": B.BODY, "p_pearl": B.BODY}
PROJ_FX = {"r_fan": B.FX_CENTRE}


def fx_make(fx):
    """塞进特效表的新标签：Codex 的标签换成技能里叫的名字。"""
    return {"a_hit": fx["attack"], "e_ward": fx["skill2"], "p_pearl": fx["passive"], "r_fan": fx["ult"]}


CENLEI = B.config("cenlei", BAKE=BAKE, TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(CENLEI, __doc__)
