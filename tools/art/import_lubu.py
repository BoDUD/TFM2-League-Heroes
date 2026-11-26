#!/usr/bin/env python3
"""Lu Bu's sheets (the ragnarok pack, ragnarok_lubu) from Codex's delivery in assets/source/lubu/codex_v02.

    python tools/art/import_lubu.py [--check]
    python tools/art/ppu_hd.py --hero lubu          # then: the hd_ and lo_ tags from the dense strips written here

2026-11-21 起读 assets/source/lubu/rebuild：Codex 照动画第一季重画的两倍帧（一格 256，脚底点 (128, 232)，个子和原来一样）。
身体先过 tools/art/lubu_rebuild_fix.py（整套 64 帧用一个头），特效图是 tools/art/lubu_fx.py 照 Codex 的原画按两倍重出的。
下面讲 128 格的地方都乘 2；烤进身体的特效位置按新画的帧重新量过（BAKE 上面的说明）。顺序：
    python tools/art/lubu_rebuild_fix.py && python tools/art/import_lubu.py && python tools/art/ppu_hd.py --hero lubu
    python tools/art/hero_reels.py --hero lubu

Codex drew him (2026-11-20, branch codex/ragnarok-lubu-assets-v02, commit 00d78f3) in 128 x 128 cells, the soles' point
at (64, 116): 66 rows from his hair to his soles, 73 to the plume's tip - dense frames already. At PPU 1.65 (PPU
below) he stands 40 game px to his hair, 44 to the plume, a little over the base heroes' 35 (Lu Bu is a giant).

- The swing pictures go into his own frames (BAKE): the client never mirrors an effect picture and does mirror his
  frames, so a crescent drawn pointing right would point right on the red side too (SKILL.md "Both sides"). Each
  effect frame is laid on the body frame showing at that moment, its cell's centre at the soles plus Codex's anchor
  (asset_manifest_v02.json effect_anchors_logical, the way his preview.html lays them); the body frames are cut where
  an effect frame starts or ends (import_native's way), the effect over the body. The ult's charge plays stretched over
  the whole 1.18 s gathering, as in the preview.
- The 1x frames: each dense frame brought to 1 / PPU squares by pixel_down.pixelate (the pack's way: the mean of each
  square snapped to the frame's own colours, near-black squares outline), on a grid one of whose squares has the pivot
  at its centre; the pivot 11.5 game px over the soles (every base and pack sheet), at the centre of an odd frame.
- The dense frames: assets/source/ppu/lubu_<tag>.png, each round(PPU x its 1x frame), the pivot at its centre, 1 px
  gaps - ppu_hd.py reads them as drawn strips (drawn_strip) and writes hd_<tag> and lo_<tag>.
- The effects the kit plays on a unit (hit_spark on every hit, ult_impact where the cut lands, shield_break when a
  shield really breaks): ragnarok/effects/ragnarok_lubu_fx, brought to 1x by pixel_down.scale_fx (no outline, light
  has none), centred on the unit's pivot - ult_impact by its ground line (Codex's cell row 116) 11.5 game px under it,
  shield_break lifted to the chest - each with its hd_ twin (Codex's frames as drawn), an empty idle / hd_idle pair
  for the PPU: addons/ragnarok/src/hd.rs lists the sheet in EFFECTS and DRAWN_EFFECTS (view effects only).
--check rebuilds everything in memory and compares it with the files.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

# 2026-11-21 Codex 照动画第一季重画的两倍帧（assets/source/lubu/rebuild，一格 256，脚底点 (128, 232)，个子和原来一样）：
# PPU 和 FX_PPU 都乘 2。下面的数还是 Codex 128 格里量的，用 up() 乘两倍
SRC = os.path.join(ROOT, "assets", "source", "lubu", "rebuild")
ID = "ragnarok_lubu"
HERO = "lubu"
# tools/art/ppu_hd.py PPU and addons/ragnarok/src/hd.rs HEROES say the same. 1.65 at first (40 game px to his hair); the
# user, 2026-11-20, beside Thor: 「吕布是不是有点大啊 缩小一点 比雷神高出来不少」 - 1.94 = 1.65 / 0.85: the same pixels drawn
# 85 % as big, 34 game px to his hair (Thor 33), 37.6 to the plume
UP = 2.0
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = round(1.94 * UP / 1.2, 3)   # 3.233（放大前 3.88）
FX_PPU = round(1.65 * UP, 3)  # 3.3: his effect sheets keep Codex's size: hits and the wave go by game distance, not by his size


def up(p):
    """Codex 128 格里的坐标 -> 两倍格子里的。"""
    return (round(p[0] * UP), round(p[1] * UP))


SOLE = up((64, 116))        # Codex's cells: the soles' point (the bottom edge of the feet's last row)
FX_ORIGIN = up((64, 64))    # 特效格的中心
CANVAS = (round(288 * UP), round(224 * UP), up((144, 176)))
# (action, effect, from seconds, anchor from the soles, seconds a frame or None for the effect's own, the effect cell's
# point that goes on the anchor)
# 锚点是两倍格子里的像素（往右为正、往上为负），特效格的中心放在脚底点加上它；给一串就是每个身体帧一个（特效跟着戟走）。
# 2026-11-21 按重画的帧重新量的。戟尖、戟头的位置：weapon_master 按 checks.csv 的角度和位置画回每帧量出来（64 帧都是同一把
# 戟），每帧都放大看过：
# - 普攻是端平了往前捅，第 3-5 帧戟尖到 x 251-254、y 170：月牙挥痕（凸的一边朝前）最前端摆在戟尖前面一点，上下居中在
#   戟杆那一行；再往后放，最大那帧月牙的上角会擦到脸
# - 横扫：戟从脖子后面（第 3、4 帧扛在肩上，戟尖在身后）抡到身前腰的高度（第 5、6 帧戟尖 x 233-254、y 173）：月牙的头
#   对着戟尖，尾巴扫过身前，上下居中在戟杆那一行
# - 破阵：突刺的亮头在戟尖上（第 5、6 帧戟尖 (238, 187) (243, 178)），拖尾顺着戟杆；第 7、8 帧戟往回收，突刺留在前面
#   慢慢散掉，只跟着戟杆那一行往下一点（这时人站直了，再高拖尾会盖到胡子；跟着戟缩回来，碎光全落在胸口上）；前 4 帧
#   没有特效
# - 天喰蓄力：光团在戟头上跟着走（第 1 帧端在腰间、第 2、3 帧斜着举起、第 4 帧举过头顶）；第 5 帧戟往下劈，光团留在
#   头顶举戟的地方，接着斩击从那里往下劈到戟尖（跟着戟到右下角的话，斩击又从头顶开始，光一下子跳下去又跳回来）
# - 天喰斩击：一道从头顶前上方斜劈到身前地面的弧，下端在第 6 帧戟尖 (253, 216) 前面一点；再往左放，弧会从脸前擦过
THRUST_AT = [(47, -51)] * 5 + [(52, -60), (48, -53), (40, -55)]
CHARGE_AT = [(57, -60), (54, -102), (53, -136)] + [(55, -146)] * 5
BAKE = [
    ("attack", "attack_swipe", 0.26, (92, -70), None, FX_ORIGIN),
    ("skill", "sweep", 0.42, (50, -80), None, FX_ORIGIN),
    ("skill2", "thrust", 0.34, THRUST_AT, None, FX_ORIGIN),
    ("ult", "ult_charge", 0.0, CHARGE_AT, 1.18 / 8, FX_ORIGIN),
    ("ult", "ult_release", 1.18, (76, -80), None, FX_ORIGIN),
]
# the attack is a 30-tick action (build_lubu atk_dur): the recovery frames shortened so the swing still ends inside it,
# the blow on frame 4 at 0.32 s as drawn
RETIME = {"attack": [0.08, 0.08, 0.10, 0.06, 0.06, 0.04, 0.04, 0.04]}
# effects played on a unit: Codex's tag, the cell's point that goes on the unit's pivot (x, y in Codex's px)
TARGET_FX = {
    "hit_spark": FX_ORIGIN,
    "shield_break": up((64, 64 + 14)),      # lifted ~8 game px: on his chest, not his belt
    "ult_impact": (SOLE[0], SOLE[1] - A.FEET * FX_PPU),   # the burst's ground line under the pivot like the soles
}

# Codex's first redraw round (2026-11-20, branch codex/ragnarok-lubu-req1): the halberd whole again in attack 3-5 and
# skill 4-5 (codex_v02's sheet replaced, the other 59 frames byte for byte the same) and Sky Eater's wave along the cut
# (codex_req1/ragnarok_lubu_wave_native: 8 frames of 132 x 40, drawn pointing right, top and bottom alike) - the picture
# of the ult's view-only line (build_lubu.py r_wave), at 1x like every projectile picture, its centre the line's middle
# 斩波在游戏里是 1 倍的弹道图，没重画：按最近邻放大两倍读进来，和别的特效一样密；当弹道图缩回 1 倍时用原来那张，
# 和原来逐字节一样
EXTRA_FX = [(os.path.join(ROOT, "assets", "source", "lubu", "codex_req1", f"{ID}_wave_native"), round(UP))]
PROJ_FX = {"ult_wave": up((66, 20))}

# 整帧左右挪（只挪不画，画进去的特效跟着挪）：Codex 重画的帧「脚底按原动作对齐」，可各动作站的位置和 128 格那版不一样：
# 拿两版的头（重画的是同一个头，lubu_rebuild_fix.py）和脚离落点的距离比，待机、受击整个人往前站了 12-14 格，普攻、横扫
# 6-7 格，破阵、天喰和原来差不多，一出手、一挨打身子就前后跳（索尔的待机也是这样，SHIFT 待机 -6）。各动作挪到 128 格那版
# 的位置（头和脚两种量法的平均）；跑步还逐帧挪：头离落点 22、21、19、22、25、25、16、31 格，最后一帧上身往前一冲，
# 128 格那版八帧头一动不动，挪成头都在待机前 2 格（和那版一样）
SHIFT = {"idle": -14, "run": [-13, -12, -10, -13, -16, -16, -7, -22], "attack": -7, "skill": -6, "skill2": -3,
         "ult": 2, "hit": -9, "dead": -8}

LUBU = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME, "TARGET_FX": TARGET_FX,
        "EXTRA_FX": EXTRA_FX, "PROJ_FX": PROJ_FX, "CANVAS": CANVAS, "SHIFT": SHIFT}

if __name__ == "__main__":
    A.main(LUBU, __doc__)
