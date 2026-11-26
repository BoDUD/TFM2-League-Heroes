#!/usr/bin/env python3
"""波塞冬（终末包 ragnarok_poseidon）的图：Codex 按两倍密度重画的身体（assets/source/poseidon/rebuild）。

    python tools/art/poseidon_rebuild_fix.py        # 先收色、按两倍重出特效（rebuild/codex 是 Codex 的原样）
    python tools/art/import_poseidon.py [--check]
    python tools/art/ppu_hd.py --hero poseidon      # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero poseidon  # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-21 先交了 128 格的一版（分支 codex/ragnarok-poseidon-assets，提交 9f20d5975，assets/source/poseidon/
runtime/sprites：脚底点 (64, 116)，人站直约 58 格，PPU 1.65 是 35 个游戏像素），和重画过的吕布、索尔、亚当放在一起
颗粒太粗（用户：「波塞冬像素太低」），又照重画那三个人的标准画了两倍的：一格 256，脚底 (128, 232)，帧序、时长和
128 格那版一样，三叉戟是同一把 158 像素的 trident_master。PPU 3.3，个子不变。引擎是 tools/art/ragnarok_art.py。

整帧平移（SHIFT，只挪不画）：Codex 新画的帧在格子里站的位置和 128 格那版不一样，拿两版每帧头的位置比（各自待机第 1 帧
的头当模板，只平移找最像的地方），待机两版一样；
- 跑步每帧前后差得多（第 5 帧往前 23 格、第 8 帧往后 17 格），跑起来人在前后滑：逐帧挪回 128 格那版的位置；
- 普攻、怒涛连刺、暴雨斜刺、大洪水整个动作比待机往前了 8-10 格，一出手身子就往前跳、收招再跳回来：每个动作整个挪一个数
  （各帧差值的中位数），Codex 画的动作轨迹不变；倒地挪 6 格；受击两种量法一正一负、都只有 2 格，不挪。

画进他自己帧里的（会跟着他左右翻）：普攻 0.225 秒的戟风；怒涛连刺 0.225 秒的扇形戟风；暴雨斜刺 0.18 秒的升势和 0.285 秒的
坠刺；大洪水 0 秒起的蓄势。锚点是离脚底的偏移（两倍帧的像素，挪之前的帧里量的，引擎挪身子时特效一起挪）：
戟风、扇形戟风照 Codex 的 cues.json 和戟尖的距离（比戟尖靠后 18、24 格），戟尖用 Codex 的 grips_hd256.json（握点、角度、
握点在杆上的位置）算；升势、坠刺、蓄势照 cues.json 乘 2 再跟着身子（头的位置）挪：新画的斜刺落下时身子更靠前、
戟尖更靠后，升势的大浪头（0.34-0.5 秒，身子已经在往下劈）和坠刺要是跟着戟尖，会压在脸上、盖住胸口；跟着身子和
128 格那版一样，浪头在头的右上方，坠刺从戟头往右下。
放在目标身上的：普攻和斜刺的命中水花 thrust_hit、连刺和大洪水每一轮的 flurry_hit、大洪水围住目标的环形戟影
flood_barrage（都是对称的，不怕不翻）。特效格都以中心对齐。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "poseidon", "rebuild")
ID = "ragnarok_poseidon"
HERO = "poseidon"
UP = 2.0                    # 两倍密度：一格 256
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = round(1.65 * UP / 1.2, 3)   # 2.75（放大前 3.3）
FX_PPU = round(1.65 * UP, 3)     # 3.3：特效图不放大


def up(p):
    """Codex 128 格里的坐标 -> 两倍图里的。"""
    return (round(p[0] * UP), round(p[1] * UP))


SOLE = up((64, 116))
FX_ORIGIN = up((64, 64))    # 特效格的中心
CANVAS = (round(288 * UP), round(224 * UP), up((144, 176)))

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心)
BAKE = [
    ("attack", "thrust_wind", 0.225, (87, -64), None, FX_ORIGIN),     # 普攻第 4 帧戟尖 (232, 168)，往回 18
    ("skill", "flurry_wind", 0.225, (90, -48), None, FX_ORIGIN),      # 连刺第 4 帧戟尖 (242, 184)，往回 24
    ("skill2", "rain_rise", 0.18, (48, -102), None, FX_ORIGIN),       # cues (84, 63) 乘 2，跟着身子往右 8、往下 4
    ("skill2", "rain_fall", 0.285, (100, -38), None, FX_ORIGIN),      # cues (105, 97) 乘 2，跟着身子往右 18（按戟尖放会盖住脸）
    ("ult", "flood_charge", 0.0, (14, -53), None, FX_ORIGIN),         # cues (70, 89) 乘 2，身子往右下各 1、2 格
]
RETIME = {}
TARGET_FX = {"thrust_hit": FX_ORIGIN, "flurry_hit": FX_ORIGIN, "flood_barrage": FX_ORIGIN}
SHIFT = {
    "run": [-4, 3, 4, -1, -23, -4, 6, 17],
    "attack": -10, "skill": -8, "skill2": -8, "ult": -10, "dead": -6,
}

POSEIDON = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
            "TARGET_FX": TARGET_FX, "CANVAS": CANVAS, "SHIFT": SHIFT}

if __name__ == "__main__":
    A.main(POSEIDON, __doc__)
