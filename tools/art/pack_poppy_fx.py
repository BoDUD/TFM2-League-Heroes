#!/usr/bin/env python3
"""Build poppy_fx_pack.zip: step 3 of Poppy's sprite - Codex draws her effects (pack_cassiopeia_fx.py's way).

    python ../work/pp/fx_ref_pp.py            # League's particle textures -> C:/t/pp_work/fxref (Riot's art, local only)
    python tools/art/pack_poppy_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name poppy_fx_redo_pack]

The pack (C:/t/pp_work/fx/poppy_fx_pack, zipped into --out, default dist/poppy_packs) holds PROMPTS.md (also written to
assets/source/poppy/PROMPTS_FX.md), design/poppy_idle.png (her idle at 4x, the design's squares at PPU 1.3),
design/poppy_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/poppy_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Poppy grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_poppy.py): view_projectiles p_buckler, r_wave (turned with
their flight: drawn pointing right, symmetric top to bottom); view_effects a_hit, p_lie, p_pick, q_slam, q_crack,
q_burst, q_hit, w_cast, w_block, e_hit, e_wall, r_charge, r_tap, r_hit; view_buffs p_shown (the buckler's shield),
w_on (Steadfast Presence's aura), e_stun. League's colours: her light is a warm gold and amber (the buckler, the
shield, the aura, the hammer's glow), the ground she smashes brown dust and rock chips, the wall stun a purple flash.
Red side: the client never mirrors an effect picture, so every effect and buff picture is symmetric left to right; the
two projectiles point right and are turned with their flight (symmetric top to bottom, so turned they never stand
upside down).
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
TMP = "C:/t/pp_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "poppy", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_poppy")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "poppy_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614"       # the buckler's light, the shield, the aura
STEEL = "#FFFFFF, #E4E6EA, #B8BCC6, #8A8F9C, #5E6270, #383B46"      # the buckler's iron face
DUST = "#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18"       # dust, cracked ground, rock chips
STUN = "#FFFFFF, #F2D8FF, #C890FF, #9A5AE6, #6A34B4, #3E1C70"       # the wall stun's flash
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with "
        "its lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"a warm gold light ramp ({GOLD})"
SE = f"a steel ramp ({STEEL})"
DU = f"a dusty brown ramp ({DUST})"
SU = f"a purple flash ramp ({STUN})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns "
      "it to its flight: flying left it is turned half round and must not stand upside down)")
CENTER = "; centered in every cell."
HER = ("the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 "
       "squares wide, her head 20-36 squares above the ground")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- passive Iron Ambassador
    ("p_buckler", "被动钢铁大使：扔出去的圆盾（弹道），4 帧（循环）",
     "view_projectiles `league_poppy_p_buckler`（随飞行方向转；画成**朝右**、**上下对称**）", "12 × 12",
     "她扔出去的圆盾：一面**圆形的小盾牌**，铁灰色的盾面，**金色的盾边**，中间一个金色的圆钉，飞的时候在转（每帧盾面上的亮光转一点），"
     "后面拖一小段金色的光尾（参考 P_Shield_v2、P_shield_trail、P_mis_edge）。**上下对称**（游戏按飞的方向转它）。约 12 × 12 格。",
     f"{GO} and {SE}",
     f"A SPINNING ROUND BUCKLER in flight, 4 frames, a seamless loop, {TB}: a round shield 9 squares across seen "
     "face-on - a steel-grey face, a 1-square bright GOLD rim, a 2x2 gold boss in the middle (a 1-square dark edge round "
     "the rim: it is solid metal) - a short gold light trail 3 squares behind it (to the left); each frame the white "
     "glint on its face moves a quarter round the boss.",
     row(4, 12, 12) + CENTER),
    ("p_lie", "被动：落在地上的圆盾（地上，不跟随，每 1/4 秒接着放），2 帧",
     "view_effects `league_poppy_p_lie`（不跟随，画在人物下面 z -1；左右对称；落地后 4 秒内每 15 tick 再放一次：2 帧连起来要能接上）",
     "14 × 8",
     "弹回来落在地上、等她去捡的圆盾：**平躺在地上的圆盾**（从斜上方看是扁椭圆），金边铁面，下面一圈淡淡的金光，一闪一闪"
     "（参考 P_Shield_ground_v2、P_ground_indicator_ring、P_shield_ground_vertglow）。**左右对称**。约 14 × 8 格。",
     f"{GO} and {SE}",
     f"A BUCKLER LYING ON THE GROUND seen from above at an angle, 2 frames, a seamless loop, {LR}: a flat round shield "
     "(an ellipse 10 squares wide and 4 tall: the steel face, a 1-square gold rim, the gold boss, a 1-square dark edge: "
     "solid) with a faint gold glow ring round it on the ground (an ellipse 13 wide and 6 tall, no outline); 1 the glow "
     "dim; 2 the glow brighter with a white glint on the rim's top.",
     row(2, 14, 8) + "; centered across, the shield's middle 3 squares above the cell's bottom row."),
    ("p_pick", "被动：捡起圆盾（她身上，跟随），4 帧",
     "view_effects `league_poppy_p_pick`（跟随，画在人物上面 z 2；左右对称）", "28 × 40",
     f"她走过去捡起圆盾的一瞬间：从地上往上冲起一圈金光，金色的光点往上飘，她身上亮一下（{HER}；身体留空不画）"
     "（参考 P_activate_flash、P_Buff_glow、P_bokeh_dots）。**左右对称**。",
     GO,
     f"A GOLD PICK-UP FLASH round a figure, 4 frames, {LR} ({HER}): 1 a gold ring on the ground (an ellipse 20 squares "
     "wide and 6 tall) and a white star 3 squares at her feet; 2 gold light streaks rising from the ring 14 squares up "
     "at mirrored places, a few gold sparkles; 3 the streaks 24 squares up and thinner, sparkles round her waist; 4 "
     "fading sparkles high up; the middle (her body) left clear.",
     row(4, 28, 40) + "; centered across, the figure's ground 2 squares above the cell's bottom row."),
    ("p_shown", "被动：盾的护盾（她身上，循环）", "view_buffs `league_poppy_p_shown`（跟随，画在人物下面 z -1；左右对称；循环，护盾 3 秒内一直在）",
     "30 × 40",
     f"捡起圆盾后她身上的护盾：**一圈半透明感的金色光罩**围着她（只画边缘：一道金色的弧线轮廓，顶上最亮），上面几道金色的光纹慢慢流动"
     f"（参考 P_Aura_Self_02、R_Shield_ring、P_shield_glow）。**只画外圈，她的身体位置留空**（{HER}）。**左右对称**，4 帧循环。",
     GO,
     f"A GOLD SHIELD BUBBLE round a figure, 4 frames, a seamless loop, {LR} ({HER}): a rounded shield outline (an upright "
     "oval 26 squares wide and 36 tall, sitting on the ground) drawn only as a 1-2 square gold edge, brightest at its "
     "top, a lighter inner line 1 square inside it on the top third; 3 short gold light lines running round it at "
     "mirrored places; each frame the lines move 2 squares along the edge; everything inside the oval left clear.",
     row(4, 30, 40) + "; centered across, the oval's bottom 2 squares above the cell's bottom row."),
    # ---- attack
    ("a_hit", "普攻 / 圆盾命中（目标身上），4 帧", "view_effects `league_poppy_a_hit`（跟随，画在人物上面；左右对称）", "14",
     "锤子或圆盾打中目标：一下金白色的闪光，几道金色的短尖刺往外，几颗棕色的小石屑（参考 BA_flash、E_impact_flash、R_dirtbits）。"
     "**左右对称**。约 14 格。",
     f"{GO} and {DU}",
     f"A HAMMER BLOW on a unit, 4 frames, {LR}: 1 a white-gold flash 5 squares; 2 a gold star burst 11 squares with a "
     "white core, 4 short sharp gold spikes at mirrored angles; 3 the burst a thin ring 13 squares, 4 small brown rock "
     "chips (2x2 squares, a dark edge: solid) flying out at mirrored places; 4 fading chips.",
     row(4, 14, 14) + CENTER),
    # ---- Q Hammer Shock
    ("q_slam", "Q 圣锤猛击：锤子砸地（地上，不跟随），5 帧",
     "view_effects `league_poppy_q_slam`（不跟随，画在人物上面 z -1；左右对称；大图表）", "44 × 30",
     "锤子砸到地上：地面猛地一亮，一圈扁的金色冲击环往外扩，一团棕色的尘土和碎石往上崩，几道裂纹往外射（参考 poppy_base_Q_mis_ground_hit1、"
     "poppy_base_Q_mis_ground_hit2、Q_dust_SandSlam、poppy_base_Q_Hit_Rocks、Q_crack_radial）。**左右对称**，落点在格子中间偏下。",
     f"{GO} and {DU}",
     f"A HAMMER SLAM INTO THE GROUND seen from above at an angle, 5 frames, {LR}: 1 a white-gold flash on the ground 12 "
     "squares wide; 2 a flat gold shock ring on the ground (an ellipse 26 wide and 8 tall) and brown dust bursting up 12 "
     "squares, 6 brown rock chips (2x2 / 3x2 squares, a dark edge: solid) flung up at mirrored places; 3 the ring 38 "
     "wide and 12 tall, the dust 18 squares tall, short dark cracks running out on the ground; 4 the dust opening and "
     "falling, the chips coming down; 5 thin dust and the cracks.",
     row(5, 44, 30) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("q_crack", "Q：裂开的地面（地上，不跟随，每 1/4 秒接着放），4 帧",
     "view_effects `league_poppy_q_crack`（不跟随，画在人物下面 z -2；左右对称；1 秒内每 15 tick 再放一次：4 帧连起来要能无缝接上；"
     "大图表）", "40 × 16",
     "锤子砸过的地方：地上一片**裂开的地面**（从斜上方看是扁椭圆），裂缝里透出金色的光，一闪一闪地越来越亮（1 秒后要再炸一次）"
     "（参考 poppy_base_Q_mis_ground_hit_buildup、poppy_base_Q_mis_ground_hit2_glow、Q_crack_radial）。**只画地面**，站在上面的人要看得见。"
     "**左右对称**。",
     f"{GO} and {DU}",
     f"CRACKED GLOWING GROUND seen from above at an angle, 4 frames, a seamless loop, {LR}: a flat ellipse 36 squares wide "
     "and 12 tall of brown cracked ground (darker cracks radiating from the middle, a few loose chips), gold light "
     "glowing out of the cracks; frame by frame the gold glow pulses brighter (1 dim, 2 brighter, 3 brightest with white "
     "in the middle crack, 4 like 2); nothing taller than 3 squares above the ground.",
     row(4, 40, 16) + "; centered across, the ellipse's middle 7 squares above the cell's bottom row."),
    ("q_burst", "Q：地面再炸一次（地上，不跟随），5 帧",
     "view_effects `league_poppy_q_burst`（不跟随，画在人物上面 z -1；左右对称；大图表）", "44 × 34",
     "1 秒后裂开的地面再炸一次：裂缝里猛地喷出金色的光柱和尘土，一圈更大的金色冲击环，碎石往上崩（参考 poppy_base_Q_mis_ground_hit2_glow2、"
     "R_Nova_Ground、R_Impact_Rock_Crater、poppy_base_Q_Hit2_Rocks）。**左右对称**。",
     f"{GO} and {DU}",
     f"A RUPTURE OF THE CRACKED GROUND seen from above at an angle, 5 frames, {LR}: 1 the cracks flash white-gold (an "
     "ellipse 30 wide and 10 tall); 2 gold light jets bursting up out of the cracks (4 jets at mirrored places, 3 squares "
     "wide, 16 tall, white cores) and a gold shock ring 34 wide and 10 tall; 3 the jets 24 tall, brown dust and rock "
     "chips (a dark edge: solid) thrown up at mirrored places; 4 the jets thinning, the dust 20 tall; 5 dust settling.",
     row(5, 44, 34) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("q_hit", "Q 命中（目标身上），4 帧", "view_effects `league_poppy_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "被震到的敌人：脚下崩起一小团棕色尘土，几颗碎石，一圈金色的小冲击（参考 poppy_base_Q_Hit_streaks、poppy_base_Q_Hit_Rocks）。"
     "**左右对称**。约 16 格。",
     f"{GO} and {DU}",
     f"A SHOCK HIT on a unit, 4 frames, {LR}: 1 a gold flash 6 squares; 2 a gold ring 12 squares, brown dust puffing up "
     "at mirrored places; 3 4 rock chips (2x2 squares, a dark edge) flying up, the ring thinner; 4 fading dust.",
     row(4, 16, 16) + CENTER),
    # ---- W Steadfast Presence
    ("w_cast", "W 坚定风采：开启（她身上，跟随），4 帧",
     "view_effects `league_poppy_w_cast`（跟随，画在人物下面 z -1；左右对称；大图表）", "44 × 44",
     f"她开启坚定风采：脚下猛地亮起一圈金色的光环，往上冲起一道**金色的光罩**（半个圆顶，只画边缘），几道金光往上射，然后光罩收回去"
     f"变成脚下的光环（参考 W_groundIcon、W_dome_mult、Poppy_base_W_Shield_edge、W_speed_sparks）。**她的身体位置留空**（{HER}）。"
     "**左右对称**。",
     GO,
     f"A GOLD DOME RISING round a figure, 4 frames, {LR} ({HER}): 1 a bright gold ring on the ground (an ellipse 30 "
     "squares wide and 9 tall) with a white glint; 2 a dome outline rising from it (a half oval 34 wide and 26 tall, a "
     "1-2 square gold edge, brightest at its top) and 4 gold streaks shooting up at mirrored places; 3 the dome 40 wide "
     "and 38 tall, thinner, gold sparkles on it; 4 the dome fading, the ground ring left; everything inside the dome "
     "clear.",
     row(4, 44, 44) + "; centered across, the figure's ground 3 squares above the cell's bottom row."),
    ("w_on", "W：光环（她脚下，循环）", "view_buffs `league_poppy_w_on`（跟随，画在人物下面 z -1；左右对称；循环，2 秒内一直在；大图表）",
     "72 × 26",
     "坚定风采开着的 2 秒：她脚下一个**大大的金色光环**（光环就是阻挡突进的范围），光环边上几道金色的光纹慢慢转，几颗金色的光点往上飘"
     "（参考 poppy_base_W_buff_ground、poppy_base_W_buff_ground2、W_Block_ripples）。**只画地上的环，中间不填满**。**左右对称**，4 帧循环。",
     GO,
     f"A WIDE GOLD AURA RING on the ground round a figure, 4 frames, a seamless loop, {LR}: a gold ring seen from above "
     "at an angle (an ellipse 70 squares wide and 22 tall, 1-2 squares thick, a lighter top edge), 6 short gold rune "
     "marks on it at mirrored places, 4 small gold sparkles rising from it; each frame the marks move 3 squares along "
     "the ring and the sparkles rise; the inside left empty.",
     row(4, 72, 26) + "; centered across, the ellipse's middle 12 squares above the cell's bottom row."),
    ("w_block", "W：挡下突进（被挡下的敌人身上），4 帧", "view_effects `league_poppy_w_block`（跟随，画在人物上面 z 2；左右对称）", "24 × 28",
     f"冲进光环被挡下的敌人：撞上一道金色的光墙（一圈金色的波纹炸开），金色的盾形光一闪，几道冲击线（参考 W_hit_ripple、W_hit_tar、"
     f"Poppy_base_W_Shield_edge_lines_hit）。**左右对称**（{CHAMP}）。",
     GO,
     f"A DASH BLOCKED by a gold barrier on a unit, 4 frames, {LR} ({CHAMP}): 1 a white-gold flash 8 squares at its "
     "chest; 2 a gold ripple ring 16 squares across (2 squares thick, white inside edge) with a small gold shield shape "
     "in its middle; 3 the ripple 22 squares, thinner, 6 short gold impact lines at mirrored angles; 4 fading sparkles.",
     row(4, 24, 28) + "; centered across, the unit's feet 2 squares above the cell's bottom row."),
    # ---- E Heroic Charge
    ("e_hit", "E 英勇冲锋：撞上目标（目标身上），4 帧", "view_effects `league_poppy_e_hit`（跟随，画在人物上面；左右对称）", "18",
     "她冲上去撞中目标：一下金白色的大闪光，一圈冲击，几道往外的速度线和尘土（参考 E_Impact_glow、E_impact_flash、E_swooshLines）。"
     "**左右对称**。约 18 格。",
     f"{GO} and {DU}",
     f"A CHARGE IMPACT on a unit, 4 frames, {LR}: 1 a white-gold flash 8 squares; 2 a gold burst 15 squares with a white "
     "core, 6 sharp gold rays at mirrored angles; 3 a gold ring 17 squares and brown dust puffs at both sides; 4 "
     "fading dust and sparkles.",
     row(4, 18, 18) + CENTER),
    ("e_wall", "E：撞到墙上（目标身上，扩展包用），5 帧", "view_effects `league_poppy_e_wall`（跟随，画在人物上面 z 2；左右对称）", "26 × 30",
     f"被她推着撞到墙上的敌人：碎石崩飞，一大团尘土，一下**紫色的闪光**（英雄联盟里撞墙眩晕是紫金色的）"
     f"（参考 E_impact_flash_purple、E_Stun_Smoke、poppy_base_E_Hit_Rocks、E_SmokeCloud）。**左右对称**（{CHAMP}）。",
     f"{SU}, {GO} and {DU}",
     f"A SLAM INTO A WALL on a unit, 5 frames, {LR} ({CHAMP}): 1 a white-purple flash 10 squares at its chest; 2 a purple "
     "and gold star burst 20 squares, 6 brown rock chips (2x2 / 3x3 squares, a dark edge: solid) flying out at mirrored "
     "places; 3 a big brown dust cloud 24 squares round it (lighter top, no outline), the chips farther; 4 the dust "
     "thinning, purple sparkles; 5 thin dust.",
     row(5, 26, 30) + "; centered across, the unit's feet 2 squares above the cell's bottom row."),
    ("e_stun", "E：眩晕（敌人头上，循环），4 帧", "view_buffs `league_poppy_e_stun`（跟随，画在人物上面 z 3；左右对称；循环）", "16 × 10",
     f"被撞晕的敌人头上：几颗转圈的金色和紫色小星星（参考 E_Stun_Smoke、E_spark）。**画在头上**（{CHAMP}，星星在 34–42 格高）。"
     "**左右对称**。",
     f"{SU} and {GO}",
     f"STUN STARS circling over a unit's head, 4 frames, a seamless loop, {LR}: 3 small stars (3x3 squares, white "
     "cores; gold and purple) on a flat ellipse 14 squares wide and 4 tall; each frame they move a quarter round it.",
     row(4, 16, 10) + CENTER),
    # ---- R Keeper's Verdict
    ("r_charge", "R 持卫的裁决：蓄力（她身上，跟随，循环），4 帧",
     "view_effects `league_poppy_r_charge`（跟随，画在人物上面 z 3；左右对称；蓄力 40 tick 里一直在放；大图表）", "40 × 44",
     f"她压低身子蓄力的时候：身边一圈越来越亮的金色旋光（金色的光往她身上收），脚下一圈金光，几颗金色的光点被吸过来"
     f"（参考 poppy_base_R_channel_spin、poppy_base_R_channel_Ball、R_Cas_sparks_instant、R_hammer_spark）。**她的身体位置留空**"
     f"（{HER}）。**左右对称**，4 帧循环。",
     GO,
     f"GATHERING GOLD POWER round a figure, 4 frames, a seamless loop, {LR} ({HER}): a gold ring on the ground (an "
     "ellipse 30 squares wide and 8 tall), 6 gold light streaks curving in toward her from 18 squares out at mirrored "
     "places, 6 small gold sparkles drawn in; each frame the streaks move 2 squares inward and the ring brightens; the "
     "middle (her body) left clear.",
     row(4, 40, 44) + "; centered across, the figure's ground 3 squares above the cell's bottom row."),
    ("r_wave", "R：往前推出去的锤击冲击波（弹道），4 帧（循环）",
     "view_projectiles `league_poppy_r_wave`（随飞行方向转；画成**朝右**、**上下对称**；大图表）", "26 × 22",
     "她抡锤推出去的冲击波：一道**向右凸的弧形金色冲击波**（月牙形，凸面朝右），前面最亮是白色，后面拖着棕色的尘土和几颗碎石"
     "（参考 R_Mis_ground、poppy_base_R_mis_Light、R_mis_dust、poppy_base_R_tarTrail）。**朝右、上下对称**。",
     f"{GO} and {DU}",
     f"A HAMMER SHOCKWAVE in flight, 4 frames, a seamless loop, {TB}: a crescent-shaped gold shockwave 18 squares tall "
     "and 4 thick, bulging to the RIGHT, a white edge on its front, brown dust 10 squares trailing behind it (to the "
     "left), 4 small rock chips (2x2, a dark edge) in the dust at mirrored heights; each frame the dust churns and the "
     "crescent flickers.",
     row(4, 26, 22) + CENTER),
    ("r_tap", "R：点放的砸地（地上，不跟随），5 帧",
     "view_effects `league_poppy_r_tap`（不跟随，画在人物上面 z -1；左右对称；大图表）", "60 × 32",
     "没蓄力就放的大招：锤子砸在她身前的地上，一圈大大的金色冲击环往外扩，尘土和碎石往上冲（附近的敌人都被击飞）"
     "（参考 R_land_ring、R_Nova_Ground、R_Hammer_hit_dustSpikes、R_dustCloud）。**左右对称**。",
     f"{GO} and {DU}",
     f"A BIG HAMMER QUAKE seen from above at an angle, 5 frames, {LR}: 1 a white-gold flash on the ground 14 squares "
     "wide; 2 a gold shock ring (an ellipse 36 wide and 10 tall) and dust spikes shooting up round it (8 spikes at "
     "mirrored places, 2 squares wide, 8-12 tall); 3 the ring 54 wide and 16 tall, brown dust 16 squares tall, rock "
     "chips (a dark edge: solid) flung up; 4 the dust falling; 5 thin dust and a faint ring.",
     row(5, 60, 32) + "; centered across, the ellipse's middle 8 squares above the cell's bottom row."),
    ("r_hit", "R 命中（目标身上），4 帧", "view_effects `league_poppy_r_hit`（跟随，画在人物上面；左右对称）", "20",
     "被大招打中的敌人：一下很大的金白色闪光，金色的冲击环，几道往外的光线和碎石（参考 R_Hit_Flash、R_impact_sharpFlash、"
     "R_hit_hammer_glow、R_dirtbits）。**左右对称**。约 20 格。",
     f"{GO} and {DU}",
     f"A HEAVY HAMMER HIT on a unit, 4 frames, {LR}: 1 a white-gold flash 9 squares; 2 a gold star burst 17 squares with a "
     "white core, 8 sharp rays at mirrored angles; 3 a gold ring 19 squares, 4 rock chips (a dark edge) flying out; 4 "
     "fading sparkles and chips.",
     row(4, 20, 20) + CENTER),
]
BIG_FX = ["q_slam", "q_crack", "q_burst", "w_cast", "w_on", "r_charge", "r_wave", "r_tap"]
REDO = {}
GROUPS = [
    ("p_buckler p_lie p_pick p_shown", ["Poppy_Base_P_Shield_v2", "Poppy_Base_P_Shield_ground_v2",
                                        "Poppy_Base_P_shield_trail", "Poppy_Base_P_ground_indicator_ring",
                                        "Poppy_Base_P_activate_flash", "Poppy_Base_P_Aura_Self_02",
                                        "Poppy_Base_R_Shield_ring"]),
    ("a_hit q_hit e_hit r_hit", ["Poppy_Base_BA_flash", "Poppy_Base_E_impact_flash", "Poppy_Base_E_Impact_glow",
                                 "Poppy_Base_R_Hit_Flash", "Poppy_Base_R_impact_sharpFlash", "Poppy_Base_R_dirtbits",
                                 "poppy_base_Q_Hit_Rocks"]),
    ("q_slam q_crack q_burst", ["poppy_base_Q_mis_ground_hit1", "poppy_base_Q_mis_ground_hit2",
                                "poppy_base_Q_mis_ground_hit_buildup", "poppy_base_Q_mis_ground_hit2_glow",
                                "Poppy_Base_Q_crack_radial", "Poppy_Base_Q_dust_SandSlam", "Poppy_Base_R_Nova_Ground"]),
    ("w_cast w_on w_block", ["Poppy_Base_W_groundIcon", "Poppy_Base_W_dome_mult", "poppy_base_W_buff_ground",
                             "poppy_base_W_buff_ground2", "Poppy_Base_W_hit_ripple", "Poppy_Base_W_hit_tar",
                             "Poppy_base_W_Shield_edge_lines_hit"]),
    ("e_wall e_stun", ["Poppy_Base_E_impact_flash_purple", "Poppy_Base_E_Stun_Smoke", "poppy_base_E_Hit_Rocks",
                       "Poppy_Base_E_SmokeCloud", "Poppy_Base_E_spark", "Poppy_Base_E_swooshLines"]),
    ("r_charge r_wave r_tap", ["poppy_base_R_channel_spin", "poppy_base_R_channel_Ball", "Poppy_Base_R_Mis_ground",
                               "poppy_base_R_mis_Light", "Poppy_Base_R_land_ring", "Poppy_Base_R_Hammer_hit_dustSpikes",
                               "Poppy_Base_R_dustCloud"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_hit：锤子横扫打中前面的目标；被动时同一下扔出 p_buckler"),
         ("skill", 3, "q_slam：锤子砸在她身前的地上（技能落点在目标脚下）；q_crack / q_burst 同一个点"),
         ("skill2", 2, "e_hit：冲上去撞中目标；e_wall / e_stun 在被推到墙边的敌人身上"),
         ("ult_charge", 1, "r_charge：蓄力时围着她"), ("ult", 2, "r_wave：横扫推出冲击波；r_hit 在敌人身上"),
         ("ult_tap", 2, "r_tap：点放砸在她身前"), ("idle", 1, "待机（大小参考；p_pick / p_shown / w_cast / w_on 围着她）")]


def ref_sheet(path):
    S, LW = 170, 200
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                cand = [f for f in os.listdir(REF) if f.startswith(nm)]
                if not cand:
                    sys.exit(f"missing reference {p}")
                p = os.path.join(REF, sorted(cand)[0])
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Poppy_Base_", "").replace("poppy_base_", "").replace("Poppy_base_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    anims = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(SHEET + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def first_1x(tag):
    f = sheet_frames(tag)[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    import tfm2_ase as T
    figs = [first_1x("idle")]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] for f in figs)
    img = Image.new("RGBA", (max(W * Z, 560), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
    x = pad
    for f in figs:
        img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                            (x * Z, (base - f.shape[0]) * Z + 64))
        x += f.shape[1] + pad
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"波比 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is her pivot, FEET rows over the ground
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 440), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    cols = 4
    rows_ = (len(tiles) + cols - 1) // cols
    cw = max(t.width for t in tiles) + 10
    ch = max(t.height for t in tiles) + 10
    sheet = Image.new("RGB", (cols * cw, rows_ * ch), (60, 64, 50))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % cols) * cw, (i // cols) * ch))
    sheet.save(path)


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.3: 1.3 squares a game pixel)."""
    import rig_poppy as M
    F = M.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 圣锤之毅 波比：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/poppy_idle.png`：3/4 正面朝右的约德尔女孩，浅蓝皮肤、浅金色双马尾、"
      f"紫红眼睛、红围巾、深紫褐皮甲和铜金甲片，身边竖着一把灰钢锤头、红锤柄的巨锤）。她在游戏里是**高清**的（每个游戏格子里 1.3×1.3 个"
      f"细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/poppy_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/poppy_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里波比自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她的光是暖金色 / 琥珀色**（圆盾、护盾、光环、锤子的光），**砸地是棕色的尘土和碎石**，"
      "**撞墙眩晕是紫金色的闪光**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **两张弹道图（`p_buckler`、`r_wave`）画成朝右飞、上下对称**：游戏会按飞的方向把它转过去，往左飞时转半圈，上下对称才不会"
      "倒过来。**其余所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 14]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `poppy_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/poppy_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「钢铁大使」（在普攻里） | 每隔一段时间下一次普攻扔出圆盾，圆盾弹回来落在地上，她走过去捡起来得到护盾 | `p_buckler` · `p_lie` · "
      "`p_pick` · `p_shown` |")
    a("| 普攻 | 锤子横扫 | `a_hit` |")
    a("| 技能 1 = Q「圣锤猛击」 | 锤子砸地，地面裂开减速，1 秒后再炸一次 | `q_slam` · `q_crack` · `q_burst` · `q_hit` |")
    a("| W「坚定风采」（跟着她的其他技能自动开） | 加移速，身边 2 秒的光环挡下冲进来的突进 | `w_cast` · `w_on` · `w_block` |")
    a("| 技能 2 = E「英勇冲锋」 | 冲向目标撞上去并推着走，撞到墙上就眩晕 | `e_hit` · `e_wall` · `e_stun` |")
    a("| 大招「持卫的裁决」 | 蓄力后抡锤推出冲击波，把敌人打飞很远；近身时点放砸地击飞 | `r_charge` · `r_wave` · `r_tap` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、毒液、毒雾、毒泡、光环、光波都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：石壳、石屑可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("暖金色的光（圆盾、护盾、光环、锤击）", GOLD), ("钢铁（圆盾的盾面）", STEEL), ("棕色尘土和碎石", DUST),
                        ("紫色闪光（撞墙眩晕）", STUN)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 的半径 18000，W 光环的半径 35000，"
      "大招点放的半径 28000，大招冲击波宽 18000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `poppy_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `poppy_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_poppy_fx`（小的）和 `league_poppy_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_poppy.py 的 views）。")
    a("- `p_lie` 落地后 4 秒里每 15 tick 再放一次；`q_crack` 1 秒里每 15 tick 再放一次；`r_charge` 在蓄力的 40 tick 里循环；`p_lie`、"
      "`q_slam`、`q_crack`、`q_burst`、`r_tap` 不跟随（地上的点）。弹道图朝右、上下对称（随飞行转）；其余全部左右对称。")
    a("- 用 `pixel_1x/` 切格（import_cassiopeia_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（圆盾、碎石保留描边）；核对交回的张数和"
      "这份清单；和 `raw/` 原稿对照读回（普朗克的教训：Codex 自己的 1 倍图可能洗白颜色，必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="poppy_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "poppy_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run ../work/pp/fx_ref_pp.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "poppy_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "poppy_size.png"))
    shots_sheet(os.path.join(out, "design", "poppy_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"poppy_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(lp(zpath)):
            os.remove(lp(zpath))
        with zipfile.ZipFile(lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
