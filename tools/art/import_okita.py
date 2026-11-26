#!/usr/bin/env python3
"""冲田总司（终末包 ragnarok_okita）的图：Codex 交的逻辑像素图集（assets/source/okita/atlases）。

    python tools/art/import_okita.py [--check]
    python tools/art/ppu_hd.py --hero okita          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero okita      # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-26 画的（okita_packs/outputs/okita_final_assets.zip，交接说明 assets/source/okita/HANDOFF.md）：动画角色设定的
样子（红格围巾、浅蓝羽织、深色袴、高马尾），已经是 Q 版像素画。一格 116×92 逻辑像素，脚底 (52, 84)，人站直 56 格；
特效格同样大，中心 (58, 46)。tools/art/ragnarok_atlas.py 按两倍最近邻读进来（像素画只按整数倍放大），PPU 8/3：
站直 112 格 = 42 个游戏像素，和别的终末英雄一样高；特效和人按 Codex 画的比例走（FX_PPU 同 PPU）。

画进他自己帧里的（会跟着他左右翻），位置照 frames.json 的 fx_events（离脚底的偏移，逻辑像素，这里乘 2），时间照 cues：
- 普攻第 5 帧（0.335 秒）的刀光 slash；
- 三段突（skill）第 2、4、6 帧（0.105 / 0.245 / 0.39 秒）各一道突刺光 thrust，画在身后：刀举在下巴的高度，光带的尾巴
  照 Codex 的位置画在前面会横过他的脸，画在身后只露出刀前面那一段；
- 鬼子（skill2）第 5 帧（0.39 秒）红眼启动的 oni；
- 终结突刺（ult）第 4 帧（0.3 秒）的 finisher：起手那颗白光照 Codex 的偏移 (44, -21) 正好落在脸上，往前挪到刀尖
  （偏移 (81, -21)：白光在刀尖，光柱往前打）。
放在别处的：刀刃命中 sword_hit、终结突刺命中 finisher_hit 放在目标身上；鬼子持续气息 oni_aura 是鬼子状态里挂在他身上的循环
（Codex：脚底往上 21 格，地上一圈红光）；踏步残影 quick_step 是脚底的一抹（Codex 说是可选的位移特效）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "okita")
ID = "ragnarok_okita"
HERO = "okita"
PPU = 2.667                 # 8/3，和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 2.667              # 特效和人一个比例（hd.rs 的 EFFECTS）
SOLE = RA.scaled((52, 84))
FX_ORIGIN = RA.scaled((58, 46))
CANVAS = (480, 320, (200, 260))


def at(dx, dy):
    """Codex 的偏移（离脚底，逻辑像素）-> 放大后的偏移。"""
    return RA.scaled((dx, dy))


def on_unit(dx, dy):
    """挂在单位身上的特效：Codex 说它的中心在脚底 + (dx, dy)；游戏把特效的中心放在单位的枢轴上（脚底往上 FEET 个游戏像素），
    所以特效格里对着枢轴的那一点要挪开同样的距离。"""
    ox, oy = at(dx, dy)
    return (FX_ORIGIN[0] - ox, round(FX_ORIGIN[1] - oy - A.FEET * FX_PPU))


# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "slash", 0.335, at(24, -25), None, FX_ORIGIN),
    ("skill", "thrust", 0.105, at(40, -24), None, FX_ORIGIN, "behind"),
    ("skill", "thrust", 0.245, at(44, -23), None, FX_ORIGIN, "behind"),
    ("skill", "thrust", 0.39, at(40, -21), None, FX_ORIGIN, "behind"),
    ("skill2", "oni", 0.39, at(0, -29), None, FX_ORIGIN),
    ("ult", "finisher", 0.3, at(81, -21), None, FX_ORIGIN),
]
TARGET_FX = {"sword_hit": FX_ORIGIN, "finisher_hit": FX_ORIGIN, "oni_aura": on_unit(0, -21), "quick_step": on_unit(-10, -4)}

OKITA = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
         "TARGET_FX": TARGET_FX, "CANVAS": CANVAS, "READ": RA.reader(SRC, "okita", ID)}

if __name__ == "__main__":
    A.main(OKITA, __doc__)
