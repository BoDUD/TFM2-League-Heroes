#!/usr/bin/env python3
"""伏梭（边境巡团 border_fusuo，银梭斥候）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_fusuo.py [--check]
    python tools/art/ppu_hd.py --hero fusuo         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero fusuo     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)，站高 106 格（32 个游戏像素）。共用的设定、特效的放法在 tools/art/border_art.py。

画进他自己帧里的（跟着他左右翻）：
- 掠阶 skill：朝右的银色突进刀光，第 2、3 帧（0.14-0.38 秒，蹲身、前冲）放，最大那张在前冲那帧里；特效格的中心放在
  他胸前 (165, 140)，画在身后（刀光的拖尾不盖住他，尖头露在刀尖前面）。
放在单位身上的：
- 普攻打中 a_hit（attack）、受击 hit：接触点；
- 数步 p_track（passive，脚印围到准星上）：贴地，准星 (64, 68) 落在被跟踪的人脚下 -> (64, 30)；
- 留扣 e_anchor（skill2 第 1-3 帧，第 3 帧停 4 秒）：留在原地的回撤点，贴地；停住那帧下面那块椭圆的底座量出来在第 96 行，
  落在地上 -> (64, 58)，两片月牙立在它上面；
- 回撤 e_recall（skill2 第 4-8 帧，一圈椭圆环）：贴地，环心 (64, 68) 在他脚下 -> (64, 30)。
（v0.7.0 起 Codex 的特效每个 8 帧：v0.5.0 的第 k 帧是现在的第 2k-1 帧，后面跟一帧过渡，每帧时长减半。）
弹道图（1 倍，border/effects/border_fusuo_proj）：
- 错拍 r_line：Codex 画的是从左下到右上的斜线，按第 1 帧细线的主方向（约 45 度）转平、朝右（最近邻，不糊），再每帧从两头
  22% 处切开加长到 75 个游戏像素（斩线区域 75000 长、6000 宽，引擎把图的中心放在线的中点、按施法方向转；预警的细线
  也是整条长）：接出来的那段照切口那一列贴着中线的部分（细线、刀光本身）补，粗细不变、不起条纹，中间的亮芯和飞出去
  的碎片原样。第 1 帧（预警细线）0.40 秒，第 2-8 帧各 0.05 秒
  （一共 0.75 秒；0.57 秒结算，最亮的第 5 帧在 0.55-0.60 秒）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格里对上锚点的那点[, "behind"])
BAKE = [
    ("skill", "skill", 0.14, B.at(165, 140), None, B.FX_CENTRE, "behind"),
]
TARGET_FX = {"a_hit": B.CONTACT, "hit": B.CONTACT, "p_track": B.ground(68), "e_anchor": B.ground(96),
             "e_recall": B.ground(68)}
# r_line 的中心转平、加长以后才知道（fx_make 填进来）
PROJ_FX = {"r_line": None}
LINE = round(75 * B.PPU)    # 75 个游戏像素


def fx_make(fx):
    out = {"a_hit": fx["attack"], "p_track": fx["passive"],
           "e_anchor": B.frames(fx, "skill2", [0, 1, 2], [0.045, 0.045, 4.0]),
           "e_recall": B.frames(fx, "skill2", [3, 4, 5, 6, 7])}
    mx, my, d = B.axis_of(fx["ult"][0][0])
    flat, c = B.turn_flat(B.frames(fx, "ult", None, [0.40] + [0.05] * 7), (mx, my), d, 184)
    out["r_line"], PROJ_FX["r_line"] = B.lengthen(flat, c, LINE, each=True)
    return out


FUSUO = B.config("fusuo", BAKE=BAKE, TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(FUSUO, __doc__)
