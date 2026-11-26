#!/usr/bin/env python3
"""雷电为右卫门（终末包 ragnarok_raiden）的图：Codex 交的两倍密度身体、肌肉解放的过渡和特效（assets/source/raiden）。

    python tools/art/raiden_fix.py                  # 先收色（snapped/，Codex 的原样在 runtime/sprites）
    python tools/art/import_raiden.py [--check]
    python tools/art/ppu_hd.py --hero raiden        # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero raiden    # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-22 画的（raiden_packs/outputs/raiden_assets_done.zip，交接说明 assets/source/raiden/HANDOFF.md）：动画第二季第五回合的
造型（白鬓、扇形束发、深蓝膝带、红色肌肉拘束纹），一格 256，脚底 (128, 232)，人站直 123 格，PPU 3.3 是 37 个游戏像素（和赫拉克勒斯
一样高）。引擎是 tools/art/ragnarok_art.py。

两张图合成一张（BANKS）：8 个动作原名；肌肉解放的过渡 muscle_release（每条命第一次放八咫乌之前，数据用 CasterAnimation 放）。

画进他自己帧里的（会跟着他左右翻），锚点照 Codex 的 cues.json 减去脚底点。都很大（一组 200 格左右宽）：扫过头、脸的画在身后
（"behind"，用户说过盖住脸不行）：普攻的掌风 0.257 秒、连掌两下的掌风 0.269 / 0.371 秒、八咫乌蓄劲的气 0.282 秒和推出去的冲击波
0.474 秒、肌肉解放迸出来的红纹 0.391 秒（一圈光环罩着身子）；四股落地的尘土 0.398 秒和地面震环 0.464 秒在脚下，画在前面。
放在目标身上的：掌的命中 palm_contact、八咫乌的命中 yatagarasu_impact。

2026-11-26 照原作改（用户：「我需要的是完美的还原度」）：「四股」在原作不是招式名，skill2 换成 Codex 补画的狮子舞
（assets/source/raiden/fidelity，逻辑像素图集；原作第五回合：双手撑地倒立，整个人往前倒，用两只脚掌跺下去）：第 6 帧 0.432 秒
双脚落地的冲击画在脚下（前面）。往前倒的那段是技能自己往前挪（RushTime），画里的前移扣掉（SHIFT），人画在原地。原来四股的
尘土和震环去掉。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "raiden", "snapped")
ID = "ragnarok_raiden"
HERO = "raiden"
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = 2.75                  # 放大前 3.3；和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 3.3                # 特效图不放大（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (128, 128)      # 特效格的中心
CANVAS = (576, 448, (288, 352))

ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
BANKS = [
    (f"{ID}_native", {t: t for t in ACTS}),
    (f"{ID}_release_native", {"muscle_release": "muscle_release"}),
]
TAGS = list(ACTS) + ["muscle_release"]


def at(x, y):
    """Codex 的锚点（256 格里的坐标）-> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


FID = os.path.join(ROOT, "assets", "source", "raiden", "fidelity")
REDRAW = [(FID, "raiden", {"skill2": "skill2"}, None)]
REDRAW_FX = [(FID, "raiden", {"stomp_wave": "stomp_wave"}, None)]
# 往前倒是技能自己的位移：画里的前移扣掉
SHIFT = {"skill2": RA.redraw_shift(FID, "skill2")}

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "palm_sweep", 0.257, at(160, 157), None, FX_ORIGIN, "behind"),
    ("skill", "palm_sweep", 0.269, at(157, 150), None, FX_ORIGIN, "behind"),
    ("skill", "palm_sweep", 0.371, at(161, 157), None, FX_ORIGIN, "behind"),
    # 狮子舞：第 6 帧双脚落地的冲击（Codex 的 frames.json：脚底前方 (10, 0)）
    ("skill2", "stomp_wave", 0.432, RA.redraw_offset(FID, "stomp_wave"), None, RA.redraw_point(FID, "fx", "stomp_wave")),
    ("ult", "compress_air", 0.282, at(131, 150), None, FX_ORIGIN, "behind"),
    ("ult", "yatagarasu_wave", 0.474, at(170, 148), None, FX_ORIGIN, "behind"),
    ("muscle_release", "release_seams", 0.391, at(128, 156), None, FX_ORIGIN, "behind"),
]
TARGET_FX = {"palm_contact": FX_ORIGIN, "yatagarasu_impact": FX_ORIGIN}

RAIDEN = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
          "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS, "REDRAW": REDRAW,
          "REDRAW_FX": REDRAW_FX, "SHIFT": SHIFT}

if __name__ == "__main__":
    A.main(RAIDEN, __doc__)
