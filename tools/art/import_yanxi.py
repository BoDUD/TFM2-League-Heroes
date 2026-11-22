#!/usr/bin/env python3
"""盐汐（边境巡团 border_yanxi，盐晶法师）的图：Codex 交的身体和特效（assets/source/border），收过色的在 snapped/。

    python tools/art/border_fix.py                  # 先收色
    python tools/art/import_yanxi.py [--check]
    python tools/art/ppu_hd.py --hero yanxi         # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero yanxi     # 最后出待机和选人动图（顺序不能换）

一格 256，脚底 (128, 184)，站高 104 格（32 个游戏像素）。共用的设定、特效的放法在 tools/art/border_art.py。
没有画进她自己帧里的特效。
（v0.7.1 撒线 skill 的第 5 帧是 2x2 的粗马赛克，跳过过一回；v0.7.2 Codex 照前后两帧补画清楚了，照常用。）
弹道图（1 倍，border/effects/border_yanxi_proj，朝右，引擎按飞的方向转）：
- 普攻的盐晶碎片 a_shard（attack 八帧，中心 (60, 68)）；
- 撒线的盐带 q_band_r：Codex 画的盐带往右上斜着（约 13 度），按铺满那帧（第 5 帧）的主方向转平（最近邻），从两头 22% 处
  切开加长到 50 个游戏像素（盐带 50000 长、14000 宽），只补贴着中线的那段晶体，不拉糊；第 1-4 帧各 0.039 秒，第 5 帧停
  3.6 秒，第 6-8 帧各 0.033 秒（盐带 4 秒；v0.7.0 起每个特效 8 帧，v0.5.0 的第 k 帧是现在的第 2k-1 帧，后面跟一帧过渡）。q_band_l 是它上下翻过来的：盐带往左铺时引擎把图转 180 度，翻过来的再转回来晶体还是朝上；
- 退潮的晶浪 r_wave_r：Codex 画的浪头朝左，弹道的图要朝右，左右翻过来；r_wave_l 是它上下翻过来的（往左收时用）。
放在单位身上的：命中 a_hit（hit，接触点）、凝结 e_burst（skill2，盐楔在目标身上炸开）、析晶 p_crystal（passive，
被标记的敌人身上的盐晶）：身上的 B.BODY。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import border_art as B  # noqa: E402
import ragnarok_art as A  # noqa: E402

TARGET_FX = {"a_hit": B.CONTACT, "e_burst": B.BODY, "p_crystal": B.BODY}
# 盐带的中心转平、加长以后才知道（fx_make 填进来）
PROJ_FX = {"a_shard": (60, 68), "q_band_r": None, "q_band_l": None, "r_wave_r": (64, 68), "r_wave_l": (64, 68)}
BAND = round(50 * B.FX_PPU)    # 50 个游戏像素


def fx_make(fx):
    mx, my, d = B.axis_of(fx["skill"][4][0])
    flat, c = B.turn_flat(B.frames(fx, "skill", None, [0.039] * 4 + [3.6] + [0.033] * 3), (mx, my), d, 184)
    band, c = B.lengthen(flat, c, BAND, period=24)
    H = band[0][0].shape[0]
    PROJ_FX["q_band_r"], PROJ_FX["q_band_l"] = c, (c[0], H - 1 - c[1])
    wave = B.flip_lr(fx["ult"])
    return {"a_hit": fx["hit"], "e_burst": fx["skill2"], "p_crystal": fx["passive"], "a_shard": fx["attack"],
            "q_band_r": band, "q_band_l": B.flip_tb(band), "r_wave_r": wave, "r_wave_l": B.flip_tb(wave)}


YANXI = B.config("yanxi", TARGET_FX=TARGET_FX, PROJ_FX=PROJ_FX, FX_MAKE=fx_make)

if __name__ == "__main__":
    A.main(YANXI, __doc__)
