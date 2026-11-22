#!/usr/bin/env python3
"""殷渡（边境巡团 border_yindu，开团坦克）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_yindu.py [--check]
    python tools/art/ppu_hd.py --hero yindu         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero yindu     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)。共用的设定、特效的放法在 tools/art/border_art.py。

画进他自己帧里的（跟着他左右翻）：
- 扣舷 skill：朝右的铜边水撞角，第 2、3 帧（0.14-0.38 秒，蹲身、顶盾）放，贴地放在盾前 (190, 184)。Codex 这组是绕格子中间
  放大的，水线一帧一帧往下走（v0.5.0 的四帧量出来第 79、90、100、89 行，v0.7.0 起每个特效 8 帧：v0.5.0 的第 k 帧是现在的第 2k-1 帧，后面跟一帧过渡，时长减半，过渡帧取前后两帧的中间），先对齐到
  第 90 行再放，水线贴住地面。
放在单位身上的：
- 普攻打中 a_hit（attack）、受击 hit：接触点；迎汐 p_tide（passive，身上）：B.BODY；
- 立标 e_buoy（skill2 第 1-3 帧，第 3 帧停 6 秒）、收标 e_buoy_end（skill2 第 4-8 帧）：浮标立在水圈里，水圈的中心
  量出来在第 87-92 行（几帧差不多），取第 90 行贴地 -> (64, 52)；
- 合汛 r_tide（ult，两道浪墙往中间合）：Codex 说枢轴放在汇合点（左右的汇合在 x=64）；浪墙的底（铜边、贴地的水）
  量出来在第 84-92 行，取第 88 行贴地 -> (64, 50)。第 1-4 帧各 0.075 秒，第 5-8 帧各 0.05 秒（最高那下第 5 帧在
  0.30 秒，代码那一刻结算）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

RAM_ROWS = [79, 85, 90, 95, 100, 95, 89, 89]    # 撞角每帧的水线（偶数帧量的，过渡帧取中间）
RAM_GROUND = 90
# 撞角对齐以后贴地那行：上下各补 32 行
BAKE = [
    ("skill", "ram", 0.14, B.at(190, 184), None, (64, RAM_GROUND + 32)),
]
TARGET_FX = {"a_hit": B.CONTACT, "hit": B.CONTACT, "p_tide": B.BODY, "e_buoy": B.ground(90), "e_buoy_end": B.ground(90),
             "r_tide": B.ground(88)}


def fx_make(fx):
    ram, _ = B.settle(fx["skill"], RAM_ROWS, RAM_GROUND)
    return {"ram": ram, "a_hit": fx["attack"], "p_tide": fx["passive"],
            "e_buoy": B.frames(fx, "skill2", [0, 1, 2], [0.045, 0.045, 6.0]),
            "e_buoy_end": B.frames(fx, "skill2", [3, 4, 5, 6, 7]),
            "r_tide": B.frames(fx, "ult", None, [0.075] * 4 + [0.05] * 4)}


YINDU = B.config("yindu", BAKE=BAKE, TARGET_FX=TARGET_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(YINDU, __doc__)
