#!/usr/bin/env python3
"""雾绫（边境巡团 border_wuling，控场辅助）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_wuling.py [--check]
    python tools/art/ppu_hd.py --hero wuling        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero wuling    # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)。共用的设定、特效的放法在 tools/art/border_art.py。没有画进她自己帧里的特效。
弹道图（1 倍，border/effects/border_wuling_proj）：普攻 a_bolt（attack 八帧，中心 (58, 68)）。
放在单位身上的：
- 命中 a_hit（hit）：接触点；闻铃 p_bell（passive，敌人身上的铃印）：身上的 B.BODY；
- 系铃 q_bell（skill 第 1-3 帧，第 3 帧停 5 秒，地上的铃）、q_ripple（skill 第 4-8 帧，减速的水纹）：铃坐在水纹圈里，
  圈心各帧都在第 73-75 行，取第 74 行贴地 -> (64, 36)；
- 挪幕 e_curtain（skill2，立着的半透明幕）：Codex 这组绕格子中间放大，幕底那条青线一帧一帧往下走（v0.5.0 的四帧在
  第 90、100、109、106 行；v0.7.0 起每个特效 8 帧：v0.5.0 的第 k 帧是现在的第 2k-1 帧，后面跟一帧过渡，时长减半，过渡帧取前后两帧的中间），对齐到第 109 行（停 3.6 秒的那帧）贴地，幕一直站在
  同一条地线上；第 1-4 帧各 0.045 秒，第 5 帧 3.6 秒，第 6-8 帧各 0.03 秒。是放在点上的画面，引擎不转它，幕一直是立着的；
- 合幕 r_close（ult，两扇幕往锚点合拢，八帧各 0.05 秒）：底线 v0.5.0 的四帧在第 101、101、107、105 行（过渡帧取中间），
  对齐到第 105 行贴地。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

PROJ_FX = {"a_bolt": (58, 68)}
# 对齐以后贴地的那行（上下各补 32 行）
CURTAIN_ROW, CLOSE_ROW = 109 + 32, 105 + 32
TARGET_FX = {"a_hit": B.CONTACT, "p_bell": B.BODY, "q_bell": B.ground(74), "q_ripple": B.ground(74),
             "e_curtain": B.ground(CURTAIN_ROW), "r_close": B.ground(CLOSE_ROW)}


def fx_make(fx):
    curtain, _ = B.settle(B.frames(fx, "skill2", None, [0.045] * 4 + [3.6] + [0.03] * 3),
                          [90, 95, 100, 105, 109, 108, 106, 106], 109)
    close, _ = B.settle(fx["ult"], [101, 101, 101, 104, 107, 106, 105, 105], 105)
    return {"a_bolt": fx["attack"], "a_hit": fx["hit"], "p_bell": fx["passive"],
            "q_bell": B.frames(fx, "skill", [0, 1, 2], [0.039, 0.039, 5.0]), "q_ripple": B.frames(fx, "skill", [3, 4, 5, 6, 7]),
            "e_curtain": curtain, "r_close": close}


WULING = B.config("wuling", TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(WULING, __doc__)
