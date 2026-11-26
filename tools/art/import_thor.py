#!/usr/bin/env python3
"""索尔（终末包，ragnarok_thor）的图：assets/source/thor/rebuild 里 Codex 照动画第一季重画的两倍帧。

    python tools/art/thor_rebuild_fix.py            # 先：从 Codex 的原画重出两倍帧（统一大小、换头）
    python tools/art/thor_fx.py                     # 特效图按身体的密度出
    python tools/art/import_thor.py [--check]
    python tools/art/ppu_hd.py --hero thor          # then the hd_ and lo_ tags
    python tools/art/hero_reels.py --hero thor      # then the idle and ban/pick reels (always in this order)

Codex 2026-11-21 重画（D:/TFM2-Workshop/ragnarok_hd_packs，交接说明 rebuild/CODEX_HANDOFF.md）：一格 256，脚底点
(128, 232)，头发到脚底约 89 格，锤头 122 x 40。PPU 2.67，游戏里头顶 33 个游戏像素（和原来一样高）。引擎是
tools/art/ragnarok_art.py（吕布的 import_lubu.py 写了每一步为什么这样）。

- 画进他自己帧里的（有前有后的画面）：普攻从 0.34 秒起的挥锤弧光（每帧 35 毫秒，0.6 秒的普攻里放得完），技能从 0.43 秒
  起的砸地雷电（每帧 42 毫秒，和动作一起结束），大招 1.24 秒蓄力里的雷圈（拉长到 1.24 秒）和 1.24 秒起的落雷。
- 2026-11-26 照原作改（用户：「我需要的是完美的还原度」）：skill2 换成 Codex 补画的铁手套格挡（assets/source/thor/fidelity，
  逻辑像素图集，按他 Q 版的像素格 2x2 放大两倍正好是 hd_；第 2 帧起手套金属光画在前面、第 4 帧格挡火花画在身后）。原来 E 的扔锤挪进大招
  「觉醒雷槌」（原作：觉醒的雷槌扔出去、像回旋镖一样飞回来、接住、把速度和离心力变成一击）：
  ult 是原来 skill2 的出手（第 0-3 帧，第 3 帧刚松手），ult_wait 是锤子飞出去时的空手（第 4-6 帧：技能用 CasterAnimation
  一直放到锤子回来），ult_catch 是第 7 帧锤子回到肩上，只在锤子真飞回来时放（BackToCasterLinearProjectile 的 end_effects，
  build_thor.py，同 league_sivir 的 Q），不按时间放；ult_slam 是原来大招从第 4 帧（锤子举过头顶）起的后半段：接住以后举锤、
  1.24 秒那一帧的落雷砸下。原来大招前 1.06 秒的蓄力（锤子横在胸前、竖在身前）不用了。
- 打在人身上的：雷击（每一锤）、大招落地的冲击（地面那行对着脚底）、雷槌觉醒的红纹（人正中：打在人身上的画面不会镜像；
  高度是锤子扛在肩上的高度）。
- 飞出去的雷槌：ragnarok/effects/ragnarok_thor_proj，1 倍（回旋镖的画面，跟着飞行方向转；它在转圈，来回看着一样）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

# 2026-11-21 Codex 照动画第一季重画的两倍帧（assets/source/thor/rebuild，一格 256，脚底点 (128, 232)；
# tools/art/thor_rebuild_fix.py 从他的原画重出，统一了大小、换了头）。他在格子里画得比原来小（站高约 89 格，原来两倍是 110），
# 所以 PPU 跟着降到 2.67，游戏里个子不变（33 个游戏像素）；特效图也按这个密度出（tools/art/thor_fx.py，一格 207）
SRC = os.path.join(ROOT, "assets", "source", "thor", "rebuild")
ID = "ragnarok_thor"
HERO = "thor"
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
# 2026-11-26 Codex 整个重画的 Q 版（assets/source/thor/q_redo，tools/art/thor_q_redo.py 原样接进来）也是按这个密度画的。
# 这里画的原画帧最后都换成 Q 版（ragnarok_q_pixel.py），只剩格挡用这里导的
PPU = 2.225                 # 放大前 2.67；tools/art/ppu_hd.py PPU and addons/ragnarok/src/hd.rs HEROES say the same
FX_PPU = 2.67               # 特效图不放大（hd.rs 的 EFFECTS）
SOLE = (128, 232)
FX_ORIGIN = (103, 103)      # 特效格（thor_fx.CELL = 207）的中心
GROUND = (103, 188)         # 落在地上的特效（雷电、大招落地）九成高度那行：thor_fx.GROUND_ROW
CANVAS = (576, 448, (288, 352))
# (action, effect, from seconds, anchor from the soles, seconds a frame or None, the effect's origin in its cell)
# 锚点都是在新帧上量的（两倍格子的像素，从脚底点算）：
# - 挥锤弧光（右边是弧、开口朝左）：普攻第 3 帧锤子举在身后（-48 度），第 4、5 帧抡到身前竖着往下砸（65、56 度），第 6 帧
#   拍在地上。锤子外头那一端绕着手（约 (150, 168)）从右上 (171, 102) 经右边 (220, 168) 扫到身前地上 (188, 228)：弧光鼓出来
#   的那边（特效格里约 (152, 103)）放在右边、比锤子外沿再出去一点，看着是锤头扫过的轨迹，不压在锤身上；
# - 砸地雷电：技能第 5-7 帧锤子平拍在地上（中心 x 163-171，前半截 171-232），雷电的地面中心 x 192：锤子前半截上，判定区
#   （q_off 14000 = 23 个游戏像素 = 61 格）和锤子前半截中心（约 200）之间；
# - 大招蓄力：跟着锤子走，每个身体帧一个锚点，圈的中心（特效格里约 (102, 98)）对着那帧锤头的中心：第 1 帧横拿在胸前（锤子往下
#   挪了 8 格，露出头和肩膀：thor_rebuild_fix.py 的 HAMMER_DY）、
#   第 2、3 帧竖在身前、第 4、5 帧举过头顶。雷圈画在他和锤子后面（"behind"）：锤子横在胸前、竖在身前的时候，
#   画在前面会从脸上划过（用户：「雷神这里有点不对？」），画在后面就是锤子和人周围一圈电光；
# - 大招落雷：雷的落点（炸开那团，特效格里约 (118, 152)）落在拍在地上的锤子前半截上面 (195, 195)，雷从他身前斜着劈下来，
#   不从头上过
# 照原作补画的格挡（2026-11-26）和原来的大招换了地方：
FID = os.path.join(ROOT, "assets", "source", "thor", "fidelity")
# 原来的标签 -> 本表的标签：原来 E 的扔锤成了大招，原来的大招只留后半段（ult_slam）
BANKS = [(f"{ID}_native", {"idle": "idle", "run": "run", "attack": "attack", "skill": "skill", "skill2": "ult",
                            "hit": "hit", "dead": "dead", "ult": "ult_slam"})]
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead", "ult_slam"]
CUT = {"ult_slam": 4}
HEAD = 0.18 + 0.2 + 0.28 + 0.4      # 原来大招切掉的前 4 帧（1.06 秒）
REDRAW = [(FID, "thor", {"skill2": "skill2"}, None)]
REDRAW_FX = [(FID, "thor", {"gauntlet_sheen": "gauntlet_sheen", "block_impact": "block_impact"}, None)]
BAKE = [
    ("attack", "hammer_swing", 0.34, (54, -72), 0.035, FX_ORIGIN),
    ("skill", "ground_lightning", 0.43, (64, 0), 0.042, GROUND),
    # 原来大招的雷圈和落雷照原来的时间放（切掉的 1.06 秒往前挪）：雷圈的最后两帧围着举过头顶的锤子，1.24 秒落雷
    ("ult_slam", "ult_charge", -HEAD, [(11, -84)] * 4, 1.24 / 8, FX_ORIGIN, "behind"),
    ("ult_slam", "ult_slam", 1.24 - HEAD, (52, -86), None, FX_ORIGIN),
    # 格挡：Codex 的 frames.json（逻辑像素，乘 hd_multiplier）：第 2 帧 0.11 秒手套金属光、第 4 帧 0.29 秒格挡火花。
    # v3 的金属光斜着从脸上划过、火花扩散到人的两三倍大盖住脸；返工版（RAGNAROK_FIDELITY_REDRAW_FIX_PROMPT.md）金属光对准交叉的
    # 手套前沿（不碰脸：头顶往下、头中线往前的像素），火花放在身后
    # 2026-11-26 第二次返工（身高照游戏里的待机，红发顶离脚底 42-45 个逻辑像素）：两个特效按帧挂在手套上（frames.json 的
    # frame_offsets，每个身体帧一个）
    ("skill2", "gauntlet_sheen", 0.11, [RA.redraw_offset(FID, "gauntlet_sheen", frame=i) for i in range(1, 9)], None,
     RA.redraw_point(FID, "fx", "gauntlet_sheen")),
    ("skill2", "block_impact", 0.29, [RA.redraw_offset(FID, "block_impact", frame=i) for i in range(1, 9)], None,
     RA.redraw_point(FID, "fx", "block_impact"), "behind"),
]
# the attack is a 36-tick action (build_thor atk_dur): the blow on frame 4 at 0.42 s as drawn, the recovery shortened;
# the slam a 46-tick one (q_dur), its blow (frame 4, 0.62 s as drawn) at q_hit 26 = 0.43 s, so the wind-up is played
# 0.69x and the ground lightning (8 frames, 42 ms each) ends with it
RETIME = {"attack": [0.12, 0.10, 0.12, 0.08, 0.05, 0.05, 0.04, 0.04],
          "skill": [0.10, 0.10, 0.12, 0.11, 0.08, 0.08, 0.09, 0.09]}
# 大招（原来 skill2 的帧）：0-3 出手（动作自己的标签），4-6 锤子飞出去时的空手（ult_wait，技能的 CasterAnimation 一直放到锤子
# 回来），7 接住（ult_catch，锤子飞回来的 end_effects 放）
SPLIT = {"ult": [("ult_wait", 4), ("ult_catch", 7)]}
# 待机的锤子扛在肩上：雷槌觉醒的红纹画在锤头中心的高度，左右在人正中（打在人身上的画面不会镜像）。原来按原画
# （rebuild/checks.csv 待机 8 帧的平均：离脚底 87 格，PPU 2.225 时 39 个游戏像素）；2026-11-26 换成 Q 版重画的锤子：
# 待机 8 帧锤头（头顶以上的灰白像素）中心平均离脚底 95 个 hd_ 像素（42.5 个游戏像素）
SHOULDER = 95
TARGET_FX = {
    "thunder_hit": FX_ORIGIN,
    "ult_impact": (GROUND[0], GROUND[1] - A.FEET * FX_PPU),
    # 锤头在他身上的高度按放大后的个子：（离脚底的游戏像素 - 落点离脚底）x 特效图的密度
    "hammer_awakening": (FX_ORIGIN[0], FX_ORIGIN[1] + round((SHOULDER / PPU - A.FEET) * FX_PPU)),
}
PROJ_FX = {"hammer_flight": (103.5, 103.5)}   # 飞锤的锤头中心（thor_fx.flight：格子正中）
# 待机整体比跑步、普攻、技能站得靠前（胸口、腰、肩上的锤子都偏右 6 格），一停下来人会往前跳一下：整体挪回去（不重画）
SHIFT = {"idle": -6}

THOR = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
        "TARGET_FX": TARGET_FX, "SPLIT": SPLIT, "PROJ_FX": PROJ_FX, "SHIFT": SHIFT, "CANVAS": CANVAS,
        "BANKS": BANKS, "TAGS": TAGS, "CUT": CUT, "REDRAW": REDRAW, "REDRAW_FX": REDRAW_FX}

if __name__ == "__main__":
    A.main(THOR, __doc__)
