#!/usr/bin/env python3
"""鹭芯（边境巡团 border_luxin，追击刺客）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_luxin.py [--check]
    python tools/art/ppu_hd.py --hero luxin         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero luxin     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)。共用的设定、特效的放法在 tools/art/border_art.py。

画进她自己帧里的（跟着她左右翻）：
- 贴风 skill：往前的风痕，第 2、3 帧（0.14-0.38 秒，蹲身、前冲）放，中心放在她刀前 (170, 143)，画在身后（拖尾不盖住她）。
放在单位身上的：普攻打中 a_hit（attack）、受击 hit：接触点；追羽 p_feather（passive，逃跑的敌人身后的羽迹）：贴地，
羽毛的中间 (64, 68) 落在脚下 -> (64, 30)。
弹道图（1 倍，border/effects/border_luxin_proj，朝右，引擎按方向转）：
- 折鸢 e_kite_r：一道细风线上飞着一只纸鸢。Codex 这组绕格子中间放大，风线一帧一帧往下走（v0.5.0 的四帧在第 83、96、103、
  98 行；v0.7.0 起每个特效 8 帧：v0.5.0 的第 k 帧是现在的第 2k-1 帧，后面跟一帧过渡，时长减半，过渡帧取前后两帧的中间），先对齐到第 103 行（第 5 帧，停 3.6 秒的那张），再从风线的两头往外接（只往外添，纸鸢、星光和光雾一个像素都不挪），
  接的是这帧风线中间那段的典型横截面，粗细、颜色一样，加长到 40 个游戏像素；
  第 1-4 帧各 0.045 秒，第 5 帧 3.6 秒，第 6-8 帧各 0.03 秒。图的中心在风线的中点。e_kite_l 是它上下翻过来的（往左时用）；
- 收线 r_cut_r：每次冲刺一道交叉的羽刃（ult 八帧原样，中心 (64, 68)），r_cut_l 是它上下翻过来的。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格里对上锚点的那点[, "behind"])
BAKE = [
    ("skill", "skill", 0.14, B.at(170, 143), None, B.FX_CENTRE, "behind"),
]
TARGET_FX = {"a_hit": B.CONTACT, "hit": B.CONTACT, "p_feather": B.ground(68)}
# 风线的中心对齐、加长以后才知道（fx_make 填进来）
PROJ_FX = {"e_kite_r": None, "e_kite_l": None, "r_cut_r": B.FX_CENTRE, "r_cut_l": B.FX_CENTRE}
KITE_ROWS = [83, 90, 96, 100, 103, 101, 98, 98]
KITE = round(40 * B.FX_PPU)    # 40 个游戏像素


def fx_make(fx):
    kite, row = B.settle(B.frames(fx, "skill2", None, [0.045] * 4 + [3.6] + [0.03] * 3), KITE_ROWS, 103)
    line = np.nonzero((np.logical_or.reduce([a[..., 3] > 0 for a, _ in kite]))[row - 2:row + 3].any(0))[0]
    kite, c = B.extend_ends(kite, ((line.min() + line.max()) / 2, row), KITE)
    H = kite[0][0].shape[0]
    PROJ_FX["e_kite_r"], PROJ_FX["e_kite_l"] = c, (c[0], H - 1 - c[1])
    return {"a_hit": fx["attack"], "p_feather": fx["passive"], "e_kite_r": kite, "e_kite_l": B.flip_tb(kite),
            "r_cut_r": fx["ult"], "r_cut_l": B.flip_tb(fx["ult"])}


LUXIN = B.config("luxin", BAKE=BAKE, TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(LUXIN, __doc__)
