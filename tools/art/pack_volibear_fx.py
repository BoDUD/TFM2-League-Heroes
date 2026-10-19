#!/usr/bin/env python3
"""Build volibear_fx_pack.zip: step 3 of Volibear's sprite - Codex draws his effects (pack_poppy_fx.py's way).

    python %LOCALAPPDATA%/Temp/vb_work/fx/fx_ref_vb.py   # League's particle textures -> %TEMP%/vb_work/fxref (local only)
    python tools/art/pack_volibear_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name volibear_fx_redo_pack]

The pack (%TEMP%/vb_work/fx/volibear_fx_pack, zipped into --out, default %TEMP%/vb_work) holds PROMPTS.md (also written to
assets/source/volibear/PROMPTS_FX.md), design/volibear_idle.png (his idle at 4x, the design's squares at PPU 1.2),
design/volibear_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base
fighter), design/volibear_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Volibear grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_volibear.py): view_projectiles p_bolt (turned with its flight:
drawn pointing right, symmetric top to bottom); view_effects a_hit, p_hit, w_hit, w_heal, q_hit, e_cloud, e_bolt,
e_hit, r_land, r_hit, r_tower (the add-on's silenced tower); view_buffs w_mark, q_ms, q_stun, e_slow, e_sh, r_form.
League's colours: his storm is electric cyan and white lightning over deep storm blue, the shield and the claws ice
blue, the Frenzied Maul mark a blue-white claw sign.
Red side: the client never mirrors an effect picture, so every effect and buff picture is symmetric left to right; the
projectile points right and is turned with its flight (symmetric top to bottom, so turned it never stands upside down).
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
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "vb_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "volibear", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_volibear")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "volibear_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BOLT = "#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4"      # lightning: white core, cyan, electric blue
STORM = "#C6D0E8, #8A98C2, #5C6898, #3C4472, #262B50, #151832"     # the storm cloud, its shadow on the ground
ICE = "#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C"       # the shield, the claws' ice
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit "
        "with its lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
BO = f"an electric lightning ramp ({BOLT})"
ST = f"a dark storm-cloud ramp ({STORM})"
IC = f"an ice-blue ramp ({ICE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns "
      "it to its flight: flying left it is turned half round and must not stand upside down)")
CENTER = "; centered in every cell."
HIM = ("the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, "
       "his head 32-44 squares above the ground")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- passive The Relentless Storm
    ("p_bolt", "被动狂雷渐起：满层后攻击放出的闪电（弹道），4 帧（循环）",
     "view_projectiles `league_volibear_p_bolt`（随飞行方向转；画成**朝右**、**上下对称**）", "20 × 10",
     "满 5 层后他攻击时从目标身上跳出去的闪电：一道**横着的锯齿形闪电**，白色的芯、青蓝色的外光，两头分出几根细小的电叉，"
     "每帧锯齿的折法都不一样（参考 Passive_Static_01、jacobsLadder、wiggleSpark_01）。**朝右、上下对称**。约 20 × 10 格。",
     BO,
     f"A CRACKLING LIGHTNING BOLT in flight, 4 frames, a seamless loop, {TB}: a horizontal jagged lightning bolt 18 "
     "squares long, a 1-square white core inside a 1-square cyan glow, 3 zigzag bends, 2 thin forks at each end at "
     "mirrored places; each frame the zigzag bends differently and a few cyan sparks flicker round it.",
     row(4, 20, 10) + CENTER),
    ("p_hit", "被动：闪电打中（目标身上），4 帧", "view_effects `league_volibear_p_hit`（跟随，画在人物上面；左右对称）", "16 × 20",
     "闪电打中的敌人：一下白色的电光，几道细小的闪电从上往下劈在身上，电火花往外溅（参考 Passive_tar_flipbook、Static_01、sparkMote）。"
     "**左右对称**。约 16 × 20 格。",
     BO,
     f"A LIGHTNING STRIKE on a unit, 4 frames, {LR}: 1 a white flash 6 squares; 2 2 thin jagged bolts striking down "
     "from 18 squares up onto it at mirrored places, a cyan burst 10 squares with a white core; 3 the bolts fading, 8 "
     "small cyan sparks flying out at mirrored angles; 4 a few fading sparks.",
     row(4, 16, 20) + "; centered across, the burst's middle 7 squares above the cell's bottom row."),
    # ---- attack and W Frenzied Maul
    ("a_hit", "普攻：熊掌抓中（目标身上），4 帧", "view_effects `league_volibear_a_hit`（跟随，画在人物上面；左右对称）", "16",
     "冰蓝色的熊爪抓中目标：三道交叉的爪痕一闪，冰蓝色的光（参考 Swipe_A、Slash_B、Scratch、Flash_01）。**左右对称**（爪痕成 X 形交叉）。"
     "约 16 格。",
     f"{IC} and {BO}",
     f"A CLAW STRIKE on a unit, 4 frames, {LR}: 1 a white-blue flash 6 squares; 2 two crossing sets of 3 claw marks "
     "(an X of curved light streaks 14 squares across, white cores, ice-blue edges); 3 the marks thinner, small ice "
     "chips and sparks flying out at mirrored places; 4 fading marks.",
     row(4, 16, 16) + CENTER),
    ("w_hit", "W 暴怒撕咬：撕咬命中（目标身上），5 帧", "view_effects `league_volibear_w_hit`（跟随，画在人物上面；左右对称）", "22 × 22",
     "他扑上去撕咬：一张**冰蓝色发光的熊嘴虚影**（上下两排尖牙）猛地合上，咬合处炸开电光和爪痕（参考 W_Head_Mesh、W_Head_Teeth、"
     "W_Slash_B、W_Scratch）。**左右对称**（熊嘴正面朝外）。约 22 格。",
     f"{IC} and {BO}",
     f"A GLOWING BEAR BITE on a unit, 5 frames, {LR}: 1 a ghostly ice-blue bear jaw seen from the front, open (an upper "
     "and a lower row of 5 sharp white fangs each, 18 squares across, light edges, no outline); 2 the jaws closing; 3 "
     "the jaws shut with a white flash 12 squares where they meet and 6 cyan sparks; 4 two sets of claw marks crossing "
     "(an X, 18 squares) as the jaw fades; 5 fading sparks.",
     row(5, 22, 22) + CENTER),
    ("w_mark", "W：标记（被咬的敌人头上，循环），4 帧",
     "view_buffs `league_volibear_w_mark`（跟随，画在人物上面 z 3；左右对称；循环，8 秒内一直在）", "14 × 12",
     f"被咬过的敌人头上：一个**蓝白色发光的爪痕标记**（三道竖着的爪痕，下面一道弧线，像熊掌的符文），一闪一闪（参考 W_Marked_02、"
     f"W_Marked_X_01）。**画在头上**（{CHAMP}，标记在 38–48 格高）。**左右对称**。",
     f"{IC} and {BO}",
     f"A CLAW MARK RUNE over a unit's head, 4 frames, a seamless loop, {LR}: 3 short vertical claw strokes side by side "
     "over a curved stroke (a bear-paw sign 10 squares wide and 9 tall, white cores, ice-blue edges, no outline); 1 dim, "
     "2 brighter, 3 brightest with 4 small sparks round it at mirrored places, 4 like 2.",
     row(4, 14, 12) + CENTER),
    ("w_heal", "W：第二口回血（他身上），4 帧", "view_effects `league_volibear_w_heal`（跟随，画在人物上面 z 2；左右对称）", "40 × 48",
     f"咬第二口回血的时候他身上：一圈冰蓝色的光从脚下往上冲，几道蓝白色的光点往上飘（参考 Aura_Self、glowspecks、Flare_Omnimax）。"
     f"**他的身体位置留空**（{HIM}）。**左右对称**。",
     f"{IC} and {BO}",
     f"AN ICE-BLUE HEALING SURGE round a figure, 4 frames, {LR} ({HIM}): 1 an ice-blue ring on the ground (an ellipse 34 "
     "squares wide and 9 tall) with a white glint; 2 light streaks rising from it 18 squares at mirrored places, blue "
     "sparkles; 3 the streaks 36 squares up and thinner, sparkles round his chest; 4 fading sparkles high up; the middle "
     "(his body) left clear.",
     row(4, 40, 48) + "; centered across, the figure's ground 2 squares above the cell's bottom row."),
    # ---- Q Thundering Smash
    ("q_ms", "Q 擂首一击：冲锋时身上的电光（他身上，循环），4 帧",
     "view_buffs `league_volibear_q_ms`（跟随，画在人物下面 z -1；左右对称；循环，冲锋 4 秒内一直在）", "56 × 40",
     f"他四脚着地冲锋时：身上缠着几道跳动的电光，背后拖着青蓝色的电火花，脚下一闪一闪（参考 Q_Underlit、Q_Footprint、Static_01、"
     f"lightningMist_01）。**只画他身体的外围和脚下**（他四脚着地时约 60 格长、30 格高），**身体中间留空**。**左右对称**，4 帧循环。",
     BO,
     f"CRACKLING ELECTRICITY round a running beast, 4 frames, a seamless loop, {LR} (a four-legged bear 52 squares long "
     "and 30 tall stands in the middle, not drawn): 6 short jagged electric arcs (white cores, cyan glow) jumping on its "
     "outline at mirrored places, small cyan sparks round it, a flat cyan glow on the ground under it (an ellipse 48 "
     "wide and 6 tall); each frame the arcs jump to new places; the body's middle left clear.",
     row(4, 56, 40) + "; centered across, the ground glow 3 squares above the cell's bottom row."),
    ("q_hit", "Q：扑砸命中（目标身上），5 帧", "view_effects `league_volibear_q_hit`（跟随，画在人物上面；左右对称）", "26 × 30",
     "他扑上去把敌人砸晕：一道很粗的闪电从上劈下来，砸中的地方炸开一圈白色电光和冲击环，碎冰和电火花往外飞（参考 Q_Swipe_A、"
     "Star_Flash、Nova、flying_shards）。**左右对称**。",
     f"{BO} and {IC}",
     f"A THUNDERING SMASH on a unit, 5 frames, {LR}: 1 a thick white-cyan lightning bolt striking straight down onto it "
     "from 28 squares up; 2 a white star burst 16 squares where it lands, a cyan shock ring 22 squares wide and 6 tall "
     "on the ground; 3 ice shards (2x2 / 3x2 squares, a dark blue edge: solid) and cyan sparks flying out at mirrored "
     "places; 4 the ring fading; 5 a few sparks.",
     row(5, 26, 30) + "; centered across, the ring's middle 3 squares above the cell's bottom row."),
    ("q_stun", "Q：眩晕（敌人头上，循环），4 帧", "view_buffs `league_volibear_q_stun`（跟随，画在人物上面 z 3；左右对称；循环）", "16 × 10",
     f"被砸晕的敌人头上：几道转圈的小电光和电火花（参考 sparkMote、wiggleSpark_01）。**画在头上**（{CHAMP}，电光在 36–44 格高）。"
     "**左右对称**。",
     BO,
     f"STUN SPARKS circling over a unit's head, 4 frames, a seamless loop, {LR}: 3 small zigzag sparks (3x3 squares, "
     "white cores, cyan glow) on a flat ellipse 14 squares wide and 4 tall; each frame they move a quarter round it.",
     row(4, 16, 10) + CENTER),
    # ---- E Sky Splitter
    ("e_cloud", "E 霹天雳地：落雷前的预警（地上，不跟随），4 帧",
     "view_effects `league_volibear_e_cloud`（不跟随，画在人物下面 z -1；左右对称；大图表）", "64 × 24",
     "雷落下来之前地上的预警：地上一圈**深蓝色的雷云阴影**（从斜上方看是扁椭圆），边上一圈青蓝色的电光慢慢变亮，中间几道细电弧"
     "（参考 E_AOE_Warning_A、E_AOE_Warning_B、E_Tornado_Indicator_Mult、Ult_Clouds_A）。**只画地面**，站在上面的人要看得见。"
     "**左右对称**。",
     f"{ST} and {BO}",
     f"A STORM WARNING CIRCLE on the ground seen from above at an angle, 4 frames, {LR}: a flat ellipse 60 squares wide "
     "and 20 tall - a dark storm-blue shadow inside (half transparent look: sparse dark squares, the ground showing "
     "through), a 1-2 square cyan rim; 1 the rim dim; 2 brighter, 3 thin cyan arcs crackling across the inside at "
     "mirrored places; 4 the rim brightest with a white top edge; nothing taller than 3 squares above the ground.",
     row(4, 64, 24) + "; centered across, the ellipse's middle 10 squares above the cell's bottom row."),
    ("e_bolt", "E：从天而降的大雷（地上，不跟随），5 帧",
     "view_effects `league_volibear_e_bolt`（不跟随，画在人物上面 z 3；左右对称；大图表）", "40 × 96",
     "一道**从天上劈下来的巨大闪电柱**：又粗又亮，白色的芯、青蓝色的外光，顶上一团深蓝的雷云，劈到地上炸开一大团电光（参考 E_skyBolt_01、"
     "skyBolt_01、E_skyBolt_Hit_01、E_Glow_01）。**竖直的、左右对称**（游戏不转它）。",
     f"{BO} and {ST}",
     f"A HUGE LIGHTNING BOLT FROM THE SKY, 5 frames, {LR}: a vertical jagged lightning column from the top of the cell "
     "to the ground (6 squares thick, a 2-square white core, cyan glow; its zigzag mirrored left to right), a small dark "
     "storm cloud at its top (24 squares wide); 1 a thin bolt; 2 the full thick bolt and a white flash 20 squares on "
     "the ground; 3 the bolt flickering, a cyan burst on the ground 36 squares wide and 12 tall; 4 the bolt thin, sparks "
     "on the ground; 5 fading sparks.",
     row(5, 40, 96) + "; centered across, the ground point 4 squares above the cell's bottom row."),
    ("e_hit", "E：被雷劈中（目标身上），4 帧", "view_effects `league_volibear_e_hit`（跟随，画在人物上面；左右对称）", "18",
     "被落雷劈中的敌人：身上一下白光，电弧缠着身体跳动（参考 E_skyBolt_Hit_01、Static_01）。**左右对称**。约 18 格。",
     BO,
     f"AN ELECTROCUTED UNIT, 4 frames, {LR}: 1 a white flash 8 squares; 2 a cyan burst 14 squares and 4 jagged arcs "
     "round it at mirrored places; 3 the arcs crackling, small sparks; 4 fading sparks.",
     row(4, 18, 18) + CENTER),
    ("e_slow", "E：减速（敌人脚下，循环），4 帧", "view_buffs `league_volibear_e_slow`（跟随，画在人物下面 z -1；左右对称；循环，2 秒）",
     "24 × 8",
     "被雷劈过减速的敌人脚下：一圈淡淡的青蓝色电光，几颗小电火花（参考 lightningMist_01、sparkMote）。**只画地面**。**左右对称**。",
     BO,
     f"A FAINT ELECTRIC RING at a unit's feet, 4 frames, a seamless loop, {LR}: a thin cyan ring on the ground (an ellipse "
     "20 squares wide and 5 tall, 1 square thick) with 4 small sparks on it at mirrored places; each frame the sparks "
     "move along the ring.",
     row(4, 24, 8) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
    ("e_sh", "E：护盾（他身上，循环），4 帧", "view_buffs `league_volibear_e_sh`（跟随，画在人物上面 z 3；左右对称；循环，3 秒）", "50 × 52",
     f"他站在落雷里得到的护盾：**一圈冰蓝色的电光罩**围着他（只画边缘：一道冰蓝色的弧形轮廓，顶上最亮），上面几道电光流动"
     f"（参考 E_ShieldAura、E_bubbleGrad_01、E_wigglRipple_01）。**只画外圈，他的身体位置留空**（{HIM}）。**左右对称**，4 帧循环。",
     f"{IC} and {BO}",
     f"AN ICE-BLUE ELECTRIC SHIELD BUBBLE round a figure, 4 frames, a seamless loop, {LR} ({HIM}): a rounded shield outline "
     "(an upright oval 46 squares wide and 48 tall, sitting on the ground) drawn only as a 1-2 square ice-blue edge, "
     "brightest at its top, a lighter inner line on the top third; 4 small electric arcs running along it at mirrored "
     "places; each frame the arcs move 3 squares along the edge; everything inside the oval left clear.",
     row(4, 50, 52) + "; centered across, the oval's bottom 2 squares above the cell's bottom row."),
    # ---- R Stormbringer
    ("r_land", "R 天声震落：落地砸地（他身上，跟随），6 帧",
     "view_effects `league_volibear_r_land`（跟随，画在人物下面 z -1；左右对称；大图表）", "80 × 40",
     "他跳起来砸到地上：地上一下白光，一圈巨大的青蓝色电光冲击环往外扩，地面裂开一个坑，几道闪电从坑里往上窜，碎冰和电火花往外飞"
     "（参考 R_landingCrater_Add、R_landingCrater_Blend_01、R_AOE_Warning、Nova、R_landing_blowBack）。**左右对称**，落点在格子中间偏下。",
     f"{BO}, {ST} and {IC}",
     f"A THUNDEROUS LANDING seen from above at an angle, 6 frames, {LR}: 1 a white flash on the ground 20 squares wide; 2 "
     "a cyan shock ring on the ground (an ellipse 44 wide and 12 tall) and a dark storm-blue crater (an ellipse 30 wide "
     "and 9 tall, cracked); 3 the ring 66 wide and 18 tall, 4 jagged lightning arcs shooting up from the crater 16 "
     "squares at mirrored places, ice shards (a dark blue edge: solid) flung out; 4 the ring 76 wide, thinner, the arcs "
     "fading; 5 sparks and the crater; 6 the crater fading.",
     row(6, 80, 40) + "; centered across, the ellipse's middle 9 squares above the cell's bottom row."),
    ("r_hit", "R 命中（目标身上），4 帧", "view_effects `league_volibear_r_hit`（跟随，画在人物上面；左右对称）", "20",
     "被大招砸中的敌人：一下很大的白色电光，青蓝色的冲击环，几道往外的电弧（参考 Star_Flash、R_tar_flipbook、Flash_01）。**左右对称**。"
     "约 20 格。",
     BO,
     f"A HEAVY THUNDER HIT on a unit, 4 frames, {LR}: 1 a white flash 9 squares; 2 a cyan star burst 17 squares with a "
     "white core, 6 jagged arcs at mirrored angles; 3 a cyan ring 19 squares, sparks flying out; 4 fading sparks.",
     row(4, 20, 20) + CENTER),
    ("r_form", "R：风暴形态（他身上，循环），4 帧",
     "view_buffs `league_volibear_r_form`（跟随，画在人物下面 z -1；左右对称；循环，12 秒；大图表）", "60 × 60",
     f"大招落地后 12 秒的风暴形态：他背后一圈**深蓝色的雷云光晕**，上面电光不停地跳，肩膀上方几道竖着的冰蓝色电光尖刺（英雄联盟里他变大、"
     f"背上长出冰刺和雷电鬃毛）（参考 R_auraArc_underLight_01、R_Background、R_Avatar_Blend_01、Ult_Clouds_A、R_iceGrad）。"
     f"**画在他身体外围和背后，身体留空**（{HIM}）。**左右对称**，4 帧循环。",
     f"{ST}, {BO} and {IC}",
     f"A STORM AURA behind and round a figure, 4 frames, a seamless loop, {LR} ({HIM}): a dark storm-blue halo behind his "
     "upper body (a ring 52 squares wide and 40 tall around his shoulders and head, 3-4 squares thick, cloudy edge, no "
     "outline), 6 upright ice-blue spikes of light 6-10 squares tall rising from his shoulders at mirrored places, small "
     "jagged lightning arcs jumping on the halo; each frame the arcs jump to new places and the spikes flicker; the "
     "middle (his body) left clear.",
     row(4, 60, 60) + "; centered across, the figure's ground 2 squares above the cell's bottom row."),
    ("r_tower", "R：防御塔失效（敌方防御塔身上，扩展包用，循环），4 帧",
     "view_effects `league_volibear_r_tower`（跟随，画在防御塔上面 z 3；左右对称；扩展包里落地附近的敌方塔每 15 tick 放一次）", "30 × 50",
     "被大招打失效的防御塔：塔身上缠着跳动的电弧，顶上一团小雷云，一闪一闪（参考 R_Tower_Static_01、Static_01、jacobsLadder）。"
     "**左右对称**（一座 26 格宽、46 格高的塔站在中间，不画塔）。",
     f"{BO} and {ST}",
     f"ELECTRIC ARCS CRAWLING OVER A TOWER, 4 frames, a seamless loop, {LR} (a tower 26 squares wide and 46 tall stands "
     "in the middle, not drawn): a small dark storm cloud over its top (20 squares wide), 6 jagged arcs (white cores, cyan "
     "glow) clinging to its sides at mirrored places, small sparks; each frame the arcs jump to new places.",
     row(4, 30, 50) + "; centered across, the tower's base 2 squares above the cell's bottom row."),
]
BIG_FX = ["q_ms", "e_cloud", "e_bolt", "e_sh", "w_heal", "r_land", "r_form", "r_tower"]
REDO = {}
GROUPS = [
    ("p_bolt p_hit q_stun e_hit e_slow", ["Volibear_Base_Passive_Static_01", "Volibear_Base_jacobsLadder",
                                          "Volibear_Base_wiggleSpark_01", "Volibear_Base_Passive_tar_flipbook",
                                          "Volibear_Base_sparkMote", "Volibear_Base_Static_01",
                                          "Volibear_Base_lightningMist_01"]),
    ("a_hit w_hit w_mark", ["Volibear_Base_Swipe_A", "Volibear_Base_Slash_B", "Volibear_Base_Scratch",
                            "Volibear_Base_W_Head_Mesh", "Volibear_Base_W_Head_Teeth", "Volibear_Base_W_Marked_02",
                            "Volibear_Base_W_Marked_X_01"]),
    ("w_heal q_ms q_hit", ["Aura_Self", "Volibear_Base_glowspecks", "Volibear_Base_Q_Underlit",
                           "Volibear_Base_Q_Footprint", "Volibear_Base_Q_Swipe_A", "Volibear_Base_Star_Flash",
                           "Volibear_Base_flying_shards"]),
    ("e_cloud e_bolt e_sh", ["Volibear_Base_E_AOE_Warning_A", "Volibear_Base_E_AOE_Warning_B",
                             "Volibear_Base_E_skyBolt_01", "Volibear_Base_E_skyBolt_Hit_01", "Volibear_Base_E_Glow_01",
                             "Volibear_Base_E_ShieldAura", "Volibear_Base_E_bubbleGrad_01"]),
    ("r_land r_hit r_form r_tower", ["Volibear_Base_R_landingCrater_Add", "Volibear_Base_R_landingCrater_Blend_01",
                                     "Volibear_Base_Nova", "Volibear_Base_R_auraArc_underLight_01",
                                     "Volibear_Base_Ult_Clouds_A", "Volibear_Base_R_Tower_Static_01",
                                     "Volibear_Base_R_Avatar_Blend_01"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：熊掌往前下方抓中目标；满层时同一下放出 p_bolt"),
         ("attack_w", 3, "w_hit：双爪扑上去撕咬；w_mark 在被咬的敌人头上，w_heal 在他身上"),
         ("skill_run", 1, "q_ms：四脚着地冲锋时缠在他身上"), ("skill", 4, "q_hit：扑下来砸中目标"),
         ("skill2", 3, "举爪召雷：e_cloud / e_bolt 落在远处的目标点"), ("ult", 3, "跳起来"),
         ("ult_land", 1, "r_land：落地砸地；r_form 之后 12 秒围着他"),
         ("idle", 1, "待机（大小参考；w_heal / e_sh / r_form 围着他）")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Volibear_Base_", "")[:26],
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
    d.text((8, 36), f"沃利贝尔 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    """His idle at 4x, the design's own squares (PPU 1.2: 1.2 squares a game pixel)."""
    import rig_volibear as M
    F = M.Form()
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
    a("# 不灭狂雷 沃利贝尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/volibear_idle.png`：3/4 正面朝右、用后腿站立的白色雷霆巨熊，"
      f"白毛带冰蓝、腿和脚掌深灰紫、两条白毛辫、冰蓝水晶爪子）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），"
      f"{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/volibear_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/volibear_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里沃利贝尔自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**他的雷电是白芯的青蓝色电光**，**雷云是深蓝色**，**护盾和爪子是冰蓝色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **弹道图 `p_bolt` 画成朝右飞、上下对称**：游戏会按飞的方向把它转过去，往左飞时转半圈，上下对称才不会倒过来。**其余所有图全部严格"
      "左右对称**（逐格对称）：这些画面在红色方不会镜像。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 14]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `volibear_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/volibear_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「狂雷渐起」（在普攻里） | 攻击叠攻速，满 5 层后攻击放出闪电打附近的敌人 | `p_bolt` · `p_hit` |")
    a("| 普攻 | 熊掌往前下方抓 | `a_hit` |")
    a("| W「暴怒撕咬」（每 5 秒普攻变成撕咬） | 撕咬并标记，再咬带标记的敌人加伤并回血 | `w_hit` · `w_mark` · `w_heal` |")
    a("| 技能 1 = Q「擂首一击」 | 四脚着地冲向敌人，扑上去砸晕 | `q_ms` · `q_hit` · `q_stun` |")
    a("| 技能 2 = E「霹天雳地」 | 远处落下一道大雷，减速；他站在雷里得到护盾 | `e_cloud` · `e_bolt` · `e_hit` · `e_slow` · `e_sh` |")
    a("| 大招「天声震落」 | 跳过去砸地，周围敌人受伤减速，之后 12 秒风暴形态；附近的敌方防御塔失效（扩展包） | `r_land` · `r_hit` · "
      "`r_form` · `r_tower` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、闪电、雷云、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：碎冰可以有一圈深蓝色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("青蓝色电光（闪电、雷击、冲击环）", BOLT), ("深蓝色雷云", STORM), ("冰蓝色（护盾、爪子、碎冰）", ICE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：E 落雷的半径 30000，大招落地的半径 "
      "32000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `volibear_fx_{name}.png`：{title}\n")
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
        a(f"| `volibear_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_volibear_fx`（小的）和 `league_volibear_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_volibear.py 的 views）。")
    a("- `e_cloud`、`e_bolt` 不跟随（地上的点）；`q_ms`、`e_sh`、`r_form`、`w_mark`、`q_stun`、`e_slow` 是循环的 buff 图；弹道图朝右、"
      "上下对称（随飞行转）；其余全部左右对称。")
    a("- 用 `pixel_1x/` 切格（import_poppy_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（碎冰保留描边）；核对交回的张数和"
      "这份清单；和 `raw/` 原稿对照读回（Codex 自己的 1 倍图可能洗白颜色，必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="volibear_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=TMP, help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run %LOCALAPPDATA%/Temp/vb_work/fx/fx_ref_vb.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "volibear_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "volibear_size.png"))
    shots_sheet(os.path.join(out, "design", "volibear_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"volibear_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
