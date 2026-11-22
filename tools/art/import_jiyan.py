#!/usr/bin/env python3
"""霁砚（边境巡团 border_jiyan，远程炮台）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_jiyan.py [--check]
    python tools/art/ppu_hd.py --hero jiyan         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero jiyan     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)。共用的设定、特效的放法在 tools/art/border_art.py。没有画进他自己帧里的特效。
弹道图（1 倍，border/effects/border_jiyan_proj，朝右，引擎按方向转）：
- 普攻 a_bolt（attack 八帧，中心 (60, 68)）；
- 长刻 q_beam_r：沿瞄准线的细星束（skill 八帧各 0.039 秒），左头是星盘、右头是星光，中线在第 68 行；星盘（第 48 列以左）
  和星光（第 92 列以右）原样，中间那段束按最近邻拉长（束横着是匀的，看不出拉过、不糊），整条 80 个游戏像素，图的
  中心在整条的中点。q_beam_l 是它上下翻过来的（往左时用）。
放在单位身上的：
- 命中 a_hit（hit）：接触点；
- 定标 p_mark（passive，地上的坐标盘）：第 1-4 帧，第 5 帧停 3.5 秒，第 6-8 帧；盘心量出来在第 66-73 行，取第 72 行贴地
  -> (64, 34)；
- 照盘 e_chart（skill2，六分仪立在星盘上）：第 1-4 帧，第 5 帧停 1.0 秒，第 6-8 帧；地上那圈星盘的中心在第 100 行 -> (64, 62)；
- 星历 r_warn（ult 第 1-3 帧，第 3 帧拉到一共 0.5 秒，预警圈）、r_star（ult 第 4-8 帧，星刻落地）：v0.5.0 第 1 帧的圈画在
  第 69 行，第 2、3 帧的盘在第 93 行，第 4 帧的余光在第 85 行（v0.7.0 起每个特效 8 帧：v0.5.0 的第 k 帧是现在的第 2k-1 帧，后面跟一帧过渡，时长减半，过渡帧取前后两帧的中间）；
  都对齐到第 93 行贴地，预警圈和落点是同一个地方。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

PROJ_FX = {"a_bolt": (60, 68), "q_beam_r": None, "q_beam_l": None}
BEAM = round(80 * B.PPU)    # 80 个游戏像素
# 星历：r_warn / r_star 对齐以后贴地的那行（上下各补 32 行：第 93 行 -> 125）
WARN_ROW = 93 + 32
TARGET_FX = {"a_hit": B.CONTACT, "p_mark": B.ground(72), "e_chart": B.ground(100), "r_warn": B.ground(WARN_ROW),
             "r_star": B.ground(WARN_ROW)}


def fx_make(fx):
    beam = B.frames(fx, "skill")
    xs = np.nonzero(np.logical_or.reduce([a[..., 3] > 0 for a, _ in beam]).any(0))[0]
    beam, c = B.stretch_mid(beam, ((xs.min() + xs.max()) / 2, 68), BEAM, 48, 92)
    H = beam[0][0].shape[0]
    PROJ_FX["q_beam_r"], PROJ_FX["q_beam_l"] = c, (c[0], H - 1 - c[1])
    warn, _ = B.settle(B.frames(fx, "ult", [0, 1, 2], [0.05, 0.05, 0.4]), [69, 81, 93], 93)
    star, _ = B.settle(B.frames(fx, "ult", [3, 4, 5, 6, 7]), [93, 93, 89, 85, 85], 93)
    return {"a_bolt": fx["attack"], "q_beam_r": beam, "q_beam_l": B.flip_tb(beam), "a_hit": fx["hit"],
            "p_mark": B.frames(fx, "passive", None, [0.04] * 4 + [3.5] + [0.027] * 3),
            "e_chart": B.frames(fx, "skill2", None, [0.045] * 4 + [1.0] + [0.03] * 3), "r_warn": warn, "r_star": star}


JIYAN = B.config("jiyan", TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(JIYAN, __doc__)
