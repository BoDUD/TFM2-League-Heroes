#!/usr/bin/env python3
"""Build jayce_fx_pack.zip: step 3 of Jayce's sprite - Codex draws his effects (tools/art/pack_milio_fx.py's way:
effects at game pixels, plus pictures drawn into his own dense frames).

    python tools/art/pack_jayce_fx.py [--no-zip] [--out DIR] [--only a_hit,q_land --name jayce_fx_redo_pack]

The pack (%LOCALAPPDATA%/Temp/jy_work/fx/jayce_fx_pack, zipped into --out, default dist/jayce_packs) holds PROMPTS.md
(also written to assets/source/jayce/PROMPTS_FX.md), design/jayce_designs.png (the four designs at 3x),
design/jayce_size.png (his 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/jayce_shots.png (finished action frames, 1x at 4x, the points his pictures start from),
bake/jayce_bake_<name>_<n>.png (the frame a picture is drawn INTO: his finished dense frame - the hd_ tag of
league/champions/league_jayce, 1.5 squares a game pixel - faded on a guide canvas at BAKE_PX px a square, the point it
starts from as a cross) and refs/lol_fx_ref.png (League's own particle textures for Jayce, grouped by the effect of ours
they inform; Riot's art, local only: %LOCALAPPDATA%/Temp/jy_work/fxref from Temp/jy_work/fx/fx_ref_jy.py).
The effects are the views the kit binds (tools/kit/build_jayce.py: view_projectiles c_bolt, cq_orb, gq_orb;
view_effects a_hit, c_hit, q_land, q_hit, e_blow, w_field, w_zap, cq_hit, cq_boom, gate, gq_hit, gq_boom, tf_spark;
view_buffs q_slow, hyper, shred, haste (also g_haste), guard) and the pictures drawn into his frames at import (BAKE):
the client mirrors his frames with his facing and never an effect picture, so whatever has a front and a back on him -
the cannon's muzzle flashes and charging glows, the hammer's lightning swipe, slam and crackle - rides in the frames
(art-spec, league_milio / league_kindred).
League's colours: Jayce's hextech lightning is white-hot cores, pale cyan, cyan to a deep electric blue; the hammer's
strikes add hextech gold-amber sparks (his Color_Fade ramps); the shred debuff his blue-and-gold shield sign. Light and
lightning get no outline. Red side: projectiles symmetric top to bottom (they are turned to their flight); pictures on a
unit, on the ground and the buffs symmetric left to right.
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
import ppu_hd as P  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "jy_work")
REF = os.path.join(TMP, "fxref")
SRC = os.path.join(ROOT, "assets", "source", "jayce")
DOC = os.path.join(SRC, "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_jayce")
HD = os.path.join(SRC, "hd")
PRE = chr(92) * 2 + "?" + chr(92)
FEET = 11.5                         # 1x px from the pivot down to the soles' bottom edge
HD_PPU = P.PPU["jayce"]             # his finished dense frames (1.5 squares a game pixel)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ELEC = "#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8"      # hextech lightning: white core, pale cyan, cyan, blue
GOLD = "#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E"                # hextech gold-amber sparks (the hammer's strikes)
GATE = "#FFFFFF, #CFF8FF, #5EE6F2, #2BB0C8, #1F6F96, #E8C46A, #A9782E"  # the gate: cyan energy, a gold frame
SHRED = "#FFFFFF, #9FE6FF, #3FA9F5, #FFD25A, #E08A2A, #7A4A9E"      # the shred sign: blue and gold, a violet edge
SPEED = "#FFFFFF, #D6F6FF, #8FE3FF, #48B9F0"                        # haste streaks
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and "
        "a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, {px} px a square)"
EL_ = f"a hextech lightning ramp ({ELEC})"
GO_ = f"a hextech gold ramp ({GOLD})"
GA_ = f"a gate ramp ({GATE})"
SH_ = f"a shred-sign ramp ({SHRED})"
SP_ = f"a speed ramp ({SPEED})"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = "SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight)"
CENTER = "; centered in every cell."


def row(n, cw, ch, px=16):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * px, h=ch * px, cw=cw * px, ch=ch * px, px=px)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- in flight (turned to their flight)
    ("c_bolt", "炮形普攻：电光弹（飞行中，循环），4 帧",
     "view_projectiles `league_jayce_c_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 5",
     "加农炮打出的电光弹：一颗白亮的小能量弹，青蓝色外圈，后面拖一小段电光尾巴（参考 Jayce_Base_Projectile、Lightning_Trail）。朝右飞。"
     "**上下对称**。4 帧无缝循环（尾巴的电光一闪一闪）。约 10 格长、5 格高。", EL_,
     f"a SMALL ENERGY BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a bright oval head 4 squares long "
     "and 3 tall with a white core and pale cyan round it, a cyan-blue tail 6 squares long tapering behind it with "
     "tiny lightning kinks mirrored above and below; the tail flickers each frame.",
     row(4, 12, 7) + "; the head's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("cq_orb", "炮形 Q 电能震荡：电球（飞行中，循环），4 帧",
     "view_projectiles `league_jayce_cq_orb`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 10",
     "电能震荡的电球：一颗圆滚滚的能量球，白亮的芯、淡青到青蓝，外面绕着几道细细的电弧，后面一条短短的电光尾巴（参考 Jayce_Base_Projectile、"
     "Lightning_flipbook、SphereWaves）。朝右飞。**上下对称**。4 帧无缝循环（电弧转动）。约 16 格长、10 格高。", EL_,
     f"an ELECTRIC ORB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round orb 8 squares across - a white "
     "core 3 squares, pale cyan and cyan round it, a thin blue rim - with 2-3 thin lightning arcs (1 square thick) "
     "crackling over its surface mirrored top and bottom, and a short cyan tail 7 squares long behind it; the arcs "
     "move each frame.",
     row(4, 18, 12) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    # ---- on a target
    ("a_hit", "锤形普攻打中（目标身上），4 帧", "view_effects `league_jayce_a_hit`（跟随，画在人物上面；左右对称）", "14",
     "大锤砸中：一团白亮的冲击，带金色火星和几道短短的电光往外蹦（参考 Jayce_Hit_Flash、Hammer_Burst）。**左右对称**。约 14 格。",
     f"{EL_} and {GO_}",
     f"a HAMMER HIT, 4 frames, {LR}: 1 a white flash 5 squares across; 2 a burst 11 squares across - a white core, "
     "pale cyan, 4 short cyan lightning kinks and 4 gold sparks at mirrored places; 3 the kinks and sparks flying out to "
     "14 squares; 4 a few fading sparks.",
     row(4, 16, 16) + CENTER),
    ("c_hit", "炮形普攻打中（目标身上），4 帧", "view_effects `league_jayce_c_hit`（跟随，画在人物上面；左右对称）", "12",
     "电光弹打中：小小的一团电光炸开，几颗青蓝色电火花（参考 Jayce_Hit_Flash、Lightning_flipbook）。**左右对称**。约 12 格。", EL_,
     f"a SMALL ELECTRIC HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a burst 9 squares across - white core, "
     "pale cyan, 4 tiny lightning sparks at mirrored places; 3 the sparks at 12 squares; 4 fading sparks.",
     row(4, 14, 14) + CENTER),
    ("q_hit", "锤形 Q 苍穹之跃砸中的敌人（每个目标身上），4 帧",
     "view_effects `league_jayce_q_hit`（跟随，画在人物上面；左右对称）", "16 × 18",
     "苍穹之跃砸到的敌人：身上一下电击——几道竖着的电光从脚下往上跳，带金色火星（参考 Lightning_02、Jayce_Base_Energy）。**左右对称**，"
     "中间人形位置大致留空（6 格宽）。约 16 格宽、18 格高。", f"{EL_} and {GO_}",
     f"a SHOCK on a figure, 4 frames, {LR}, a clear upright gap 6 squares wide in the middle: 1 small jagged lightning "
     "bolts 4 squares tall at both sides near the bottom; 2 the bolts jumping up to 14 squares, gold sparks; 3 the "
     "bolts at their brightest, 18 squares; 4 the last sparks.",
     row(4, 18, 20) + "; centered across, the bolts' roots on the cell's bottom rows."),
    ("e_blow", "锤形 E 雷霆一击打中（目标身上，把它击飞），5 帧",
     "view_effects `league_jayce_e_blow`（跟随，画在人物上面；左右对称）", "20",
     "雷霆一击把敌人打飞：一个大一点的冲击——白亮的闪光，一圈青蓝色的电环往外冲，几道电弧和金色火星（参考 Jayce_Base_Shockwave、"
     "Hammer_Burst、Hit_Flash）。**左右对称**。约 20 格。", f"{EL_} and {GO_}",
     f"a THUNDERING IMPACT, 5 frames, {LR}: 1 a white flash 6 squares across; 2 a white-cyan burst 12 squares across "
     "with a ring of cyan lightning round it; 3 the ring 20 squares across, 6 lightning arcs and 6 gold sparks thrown out "
     "at mirrored places; 4 the ring breaking into arcs; 5 fading sparks.",
     row(5, 22, 22) + CENTER),
    ("w_zap", "锤形 W 闪电领域电到的敌人（目标身上，每半秒），3 帧",
     "view_effects `league_jayce_w_zap`（跟随，画在人物上面；左右对称）", "10 × 16",
     "闪电领域每半秒电一下周围的敌人：一道竖着的细闪电从上面劈下来，落点一小团白光（参考 Lightning_02、Plasma_Beam1）。**左右对称**"
     "（闪电画在正中间，左右的折线对称）。约 10 格宽、16 格高。", EL_,
     f"a SMALL LIGHTNING STRIKE, 3 frames, {LR}: 1 a thin jagged lightning bolt 1-2 squares thick from the top of the "
     "cell down the middle to the bottom, its kinks mirrored left and right, a white flash 4 squares at its foot; 2 the "
     "bolt at its brightest with 2 tiny side branches mirrored; 3 the bolt fading, sparks at the foot.",
     row(3, 12, 18) + "; centered across, the bolt's foot on the cell's bottom rows."),
    ("cq_hit", "炮形 Q 电球打中的敌人（目标身上），4 帧",
     "view_effects `league_jayce_cq_hit`（跟随，画在人物上面；左右对称）", "14",
     "电能震荡炸到的敌人：身上一团电光，几道细电弧（参考 Lightning_flipbook、Hit_Flash）。**左右对称**。约 14 格。", EL_,
     f"an ELECTRIC SHOCK on a figure, 4 frames, {LR}: 1 a white-cyan flash 6 squares across; 2 a burst 12 squares "
     "across with 4 thin lightning arcs at mirrored places; 3 the arcs at 14 squares; 4 fading sparks.",
     row(4, 16, 16) + CENTER),
    ("gq_hit", "大招 加速电炮打中的敌人（目标身上），5 帧",
     "view_effects `league_jayce_gq_hit`（跟随，画在人物上面；左右对称）", "20",
     "加速电炮炸到的敌人：比普通电球更猛的电击，一圈电环 + 多道电弧（参考 Jayce_Base_Shockwave、Lightning_flipbook）。**左右对称**。约 20 格。",
     EL_,
     f"a BIG ELECTRIC SHOCK on a figure, 5 frames, {LR}: 1 a white flash 8 squares across; 2 a burst 16 squares across "
     "with a ring of cyan lightning; 3 the ring 20 squares across, 8 lightning arcs at mirrored places; 4 the arcs "
     "breaking up; 5 fading sparks.",
     row(5, 22, 22) + CENTER),
    ("tf_spark", "变形（锤 ↔ 炮）的瞬间（他身上，跟着他），4 帧",
     "view_effects `league_jayce_tf_spark`（CasterViewEffect，跟随，画在人物上面；**严格左右对称**）", "28 × 34",
     "变形的一瞬间：他身边亮起一圈海克斯能量——两边各几道往上窜的电光和金色齿轮状的小光点，脚下一圈亮环（参考 Jayce_Base_Energy、"
     "Jayce_Aura、Color_Flashes）。**严格左右对称**（这张画在他身上，游戏不会镜像），中间人形位置留空（10 格宽、26 格高）。约 28 格宽、34 格高。",
     f"{EL_} and {GO_}",
     f"a HEXTECH TRANSFORM FLASH round a figure, 4 frames, {LR}, the middle EMPTY (a clear upright area 10 squares wide "
     "and 26 tall): 1 a thin bright ellipse ring 20 squares wide on the ground at the bottom; 2 cyan lightning wisps "
     "and gold spark motes rising at both sides to 24 squares; 3 the wisps at their top (34 squares), 4 small gold "
     "gear-shaped glints at mirrored places; 4 fading motes.",
     row(4, 30, 36) + "; centered across, the ground ring on the cell's bottom rows."),
    # ---- the ground (big)
    ("q_land", "锤形 Q 苍穹之跃落地（地上，大），6 帧",
     "view_effects `league_jayce_q_land`（BIG，不跟随，留在落点；左右对称）", "40 × 24",
     "他从天上砸下来：落点炸开一团白亮的冲击，一圈电光冲击波沿着地面往外推到半径 18 个游戏像素（从斜上方看的扁椭圆），地面裂开几道发光的裂纹，"
     "几块金色火星往四周飞（参考 Jayce_Base_Shockwave、Jayce_Base_Crack、Hammer_Burst）。要亮，但地上的圈里面别涂满。**左右对称**。"
     "这张很大：按**每格 8 像素**画。", f"{EL_} and {GO_}",
     f"a HAMMER SLAM SHOCKWAVE, 6 frames, {LR}: 1 a white flash 10 squares across at the ground point; 2 a burst of "
     "white-cyan light 16 squares wide and 14 tall rising from it, a ring of lightning starting out along the ground; 3 "
     "the ring a flat ellipse 30 squares wide and 12 tall made of short jagged lightning (1-2 squares thick), 4 glowing "
     "cracks 6 squares long on the ground from the centre at mirrored places; 4 the ring at full size (40 wide, 16 tall), "
     "8 gold sparks flying out at mirrored places; 5 the ring thinning, the cracks fading; 6 fading sparks. The inside of "
     "the ring stays mostly empty.",
     row(6, 44, 28, px=8) + "; centered across, the ground point (the ellipse's center) 10 squares above the cell's "
                           "bottom edge."),
    ("w_field", "锤形 W 闪电领域（他脚下跟着他，4 秒，大），8 帧",
     "view_effects `league_jayce_w_field`（BIG，跟随，画在人物下面；左右对称、上下对称；8 帧摊满 4 秒）", "44 × 18",
     "闪电领域：他脚下一圈跟着他走的电场——从斜上方看的扁椭圆（半径 20 个游戏像素），边上一圈噼啪跳动的细电光，偶尔一道电弧跳过椭圆，"
     "里面是空的、只有极淡的几点青光（参考 SphereWaves、Lightning_flipbook、Jayce_Aura）。不能挡住站在里面的他。**左右对称**、**上下对称**。"
     "8 帧（每帧电光位置都变一点，前后连起来像一直在噼啪响）。这张很大：按**每格 8 像素**画。", EL_,
     f"an ELECTRIC FIELD RING on the ground seen from above at an angle, 8 frames, {LR} and top to bottom: a flat ellipse "
     "44 squares wide and 18 tall whose rim is a ring of short crackling lightning (1-2 squares thick, white-cyan with "
     "blue) with a thin cyan glow line; 2 small lightning arcs jumping along the rim at mirrored places, in different "
     "places each frame; the inside EMPTY but for 6 tiny faint cyan dots; mirrored in every frame.",
     row(8, 48, 22, px=8) + CENTER),
    ("cq_boom", "炮形 Q 电球爆炸（落点，大），5 帧",
     "view_effects `league_jayce_cq_boom`（BIG，不跟随，留在爆点；左右对称）", "30",
     "电能震荡的电球撞到敌人炸开：一团白亮的电光炸起，一圈青蓝色的电环冲到半径 15 个游戏像素，几道电弧往外蹦（参考 Jayce_Base_Shockwave、"
     "Lightning_flipbook、SphereWaves）。**左右对称**。这张很大：按**每格 8 像素**画。", EL_,
     f"an ELECTRIC BLAST, 5 frames, {LR}: 1 a white flash 8 squares across; 2 a ball of white-cyan light 16 squares "
     "across; 3 a ring of cyan lightning 26 squares across round a fading core, 8 lightning arcs at mirrored places; 4 the "
     "ring at 30 squares, breaking up; 5 fading sparks.",
     row(5, 34, 34, px=8) + CENTER),
    ("gq_boom", "大招 加速电炮爆炸（落点，大），6 帧",
     "view_effects `league_jayce_gq_boom`（BIG，不跟随，留在爆点；左右对称）", "42",
     "加速电炮的大电球炸开：比普通的更大更猛——白亮的核心，两圈电环冲到半径 21 个游戏像素，很多道电弧和金色火星（参考 Jayce_Base_Shockwave、"
     "Lightning_flipbook、Color_Flashes）。**左右对称**。这张很大：按**每格 8 像素**画。", f"{EL_} and {GO_}",
     f"a BIG ELECTRIC BLAST, 6 frames, {LR}: 1 a white flash 10 squares across; 2 a ball of white-cyan light 22 squares "
     "across; 3 an inner ring 26 and an outer ring 34 squares across of cyan lightning, 10 arcs at mirrored places; 4 the "
     "outer ring at 42 squares, 8 gold sparks; 5 the rings breaking up; 6 fading sparks.",
     row(6, 46, 46, px=8) + CENTER),
    ("gate", "大招：加速之门（放在他面前，大），6 帧",
     "view_effects `league_jayce_gate`（BIG，不跟随，留在放门的地方；**严格左右对称**）", "34 × 40",
     "加速之门：一座海克斯科技的拱门立起来——两根金色的门柱（海克斯机械的样子），中间是一片发光的青色能量门面，门顶一道弧（参考 "
     "Jayce_Gent_GateBlue_TX_CM 的门柱、Jayce_Aura）。从正面看（**严格左右对称**，游戏不会镜像）。第 1–2 帧门柱从地上升起，第 3–5 帧能量门面亮起、"
     "闪烁，第 6 帧变淡。约 34 格宽、40 格高。这张很大：按**每格 8 像素**画。", GA_,
     f"an ACCELERATION GATE seen from the front, 6 frames, {LR}: two upright hextech pillars 4 squares wide and 36 tall "
     "(gold frames with cyan glowing slots) standing 30 squares apart on the ground, an arch across their tops; between "
     "them a sheet of glowing cyan energy (semi-solid squares in 2-3 cyan shades, a few white streaks); 1 the pillars "
     "rising out of the ground, 12 squares tall; 2 the pillars full height; 3 the energy sheet lighting up from the "
     "bottom; 4 the sheet full and bright; 5 the sheet flickering, streaks moving up; 6 the whole gate faded to half.",
     row(6, 38, 44, px=8) + "; centered across, the pillars' feet on the cell's bottom rows."),
    # ---- buffs (loops on the unit)
    ("q_slow", "Q 苍穹之跃的减速（敌人脚下，2 秒，循环），4 帧",
     "view_buffs `league_jayce_q_slow`（跟随，画在人物下面；左右对称）", "16 × 8",
     "被砸中减速的敌人：脚下一小圈静电，几颗电火花跳动（参考 Lightning_flipbook、common_Slow-Wake）。**左右对称**。4 帧无缝循环。约 16 格宽、8 格高。",
     EL_,
     f"STATIC at a figure's feet, 4 frames, a seamless loop, {LR}: a flat ellipse 16 squares wide and 5 tall of faint "
     "cyan static (dots and 1-square kinks) on the ground, 4 tiny sparks jumping up 2-3 squares at mirrored places; the "
     "sparks change places each frame.",
     row(4, 18, 10) + "; centered across, the ellipse on the cell's bottom rows."),
    ("hyper", "炮形 W 超能电荷（他身上，3 发，循环），4 帧",
     "view_buffs `league_jayce_hyper`（跟随，画在人物上面；左右对称）", "26 × 30",
     "超能电荷：他身边环绕着蓝色电光——两边各一道绕身的电弧，几颗电火花往上飘，**要克制**、别盖住他（参考 Lightning_flipbook、"
     "Jayce_Base_Energy）。**左右对称**，中间人形位置留空（10 格宽、24 格高）。4 帧无缝循环。约 26 格宽、30 格高。", EL_,
     f"a HYPER CHARGE AURA round a figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 10 "
     "squares wide and 24 tall): a thin curved lightning arc (1 square thick) at each side from hip to shoulder height, "
     "6 small sparks rising at mirrored places; the arcs flicker and the sparks rise a square each frame; SUBTLE - thin "
     "and sparse.",
     row(4, 28, 32) + "; centered across, the lowest sparks on the cell's bottom rows."),
    ("shred", "变炮后第一发打中的削甲（敌人头上，5 秒，循环），4 帧",
     "view_buffs `league_jayce_shred`（跟随，画在人物上面；左右对称）", "12 × 12",
     "被削甲削魔抗的敌人：头上一个小小的碎裂护盾标记——左半边金色、右半边蓝色的盾牌被一道裂缝劈开，轻轻闪（参考 Global_Debuff_Armor_MR_Shred）。"
     "**左右对称**（裂缝画在正中间竖直，左右两半形状对称，颜色左金右蓝也可以）。4 帧无缝循环（轻轻上下浮动 1 格、闪光）。约 12 格。", SH_,
     f"a SHREDDED SHIELD SIGN, 4 frames, a seamless loop, {LR} in shape (left half gold, right half blue is fine): a "
     "small shield 10 squares wide and 11 tall split down the middle by a jagged vertical crack 1 square wide, a "
     "1-square violet rim; 1 at rest; 2 one square higher, a white glint on its top edge; 3 at rest; 4 one square lower.",
     row(4, 14, 14) + CENTER),
    ("haste", "被动 / 加速之门的加速（他脚下，循环），4 帧",
     "view_buffs `league_jayce_haste`、`league_jayce_g_haste`（跟随，画在人物下面；左右对称）", "20 × 8",
     "海克斯科技电容 / 加速之门的加速：脚下一圈淡蓝的光，两边各几道短短的速度线往上飘（参考 Jayce_speedlines、Jayce_Aura）。**左右对称**"
     "（速度线画成竖直往上飘，不要朝左或朝右）。4 帧无缝循环。约 20 格宽、8 格高。", SP_,
     f"a HASTE GLOW at a figure's feet, 4 frames, a seamless loop, {LR}: a flat ellipse 20 squares wide and 5 tall of "
     "light cyan glow on the ground, 3 short vertical streaks (1 square wide, 2-4 tall) rising at each side at mirrored "
     "places; the streaks move up and fade each frame.",
     row(4, 22, 10) + "; centered across, the ellipse on the cell's bottom rows."),
    ("guard", "变锤形的护甲 / 魔抗加成（他身上，4 秒，循环），4 帧",
     "view_buffs `league_jayce_guard`（跟随，画在人物上面；左右对称）", "26 × 32",
     "变成锤形后短暂的护甲加成：他身边一个淡淡的金色六边形护盾——只有一圈细细的边（1 格），中间完全空着，边上几点光一闪一闪（参考 "
     "Jayce_Color_Fade、Jayce_Base_Glow）。**要克制**。**左右对称**。4 帧无缝循环。约 26 格宽、32 格高。", GO_,
     f"a THIN HEXAGON SHIELD round a figure, 4 frames, a seamless loop, {LR}: the outline of an upright hexagon 26 "
     "squares wide and 32 tall, 1 square thick, pale gold with white highlights, completely EMPTY inside; 4 white-gold "
     "glints on the outline at mirrored places, moving along it each frame; SUBTLE.",
     row(4, 28, 34) + "; centered across, the hexagon's bottom on the cell's bottom row."),
]
# the big sheet's effects (8 px a square, league_jayce_big)
BIG = {"gq_orb", "q_land", "w_field", "cq_boom", "gq_boom", "gate"}
FX.insert(2, ("gq_orb", "大招 加速电炮：穿过加速门的大电球（飞行中，循环，大），4 帧",
              "view_projectiles `league_jayce_gq_orb`（BIG，朝飞行方向转，画成朝右飞；上下对称）", "26 × 14",
              "穿过加速之门后的大电球：比电能震荡的电球大一圈、更亮，外面绕着更多电弧，后面一条长长的电光尾巴，尾巴边上几道金色的加速线（参考 "
              "Jayce_Base_Projectile、Lightning_Trail、Jayce_speedlines）。朝右飞。**上下对称**。4 帧无缝循环。约 26 格长、14 格高。"
              "这张很大：按**每格 8 像素**画。", f"{EL_} and {GO_}",
              f"an ACCELERATED ELECTRIC ORB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round orb 12 squares "
              "across - a white core 5 squares, pale cyan and cyan round it, a blue rim - with 4 lightning arcs crackling "
              "over it mirrored top and bottom, a cyan tail 14 squares long behind it and 2 thin gold speed lines along "
              "the tail mirrored above and below; the arcs and the tail flicker each frame.",
              row(4, 30, 18, px=8) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."))
# pictures drawn INTO his own frames, on his finished dense grid (the hd_ tags, 1.5 squares a game pixel): name, tag,
# frames, over / under him, title (zh), description (zh), ramps, the effect (en) per frame; where = the point rule
BAKE_PX = 6                          # guide px a square: 256 x 170 squares (or 170 x 256) on Codex's 1536 x 1024
LAND = (256, 170, (128, 85))         # canvas squares, the pivot's square (his frame centred on it)
PORT = (170, 256, (85, 128))
BAKE = [
    ("a_swipe", "attack", (4,), "over", "锤形普攻：大锤横扫的电光拖影（画进普攻第 4 帧）",
     "大锤横着扫到最前面：锤头（青色十字）后面拖一道弧形的电光拖影（从上往下弯到锤头），锤头一圈电火花。画在他**上面**，别挡住脸。",
     f"{EL_} and {GO_}",
     {4: "a LIGHTNING SWIPE behind the swinging hammer head: a curved trail of crackling white-cyan light 4-6 squares "
         "thick arcing from above his shoulder down to the cyan cross (the hammer head), 6 gold and cyan sparks round the "
         "cyan cross; nothing over his face."}, "right"),
    ("q_slam", "skill", (5,), "over", "锤形 Q 苍穹之跃：锤头砸地的电光（画进 Q 第 5 帧）",
     "锤头砸进地面（青色十字）：锤头四周炸开一团白亮的电光，几道电弧往上窜，金色火星往两边飞。画在他**上面**。", f"{EL_} and {GO_}",
     {5: "a LIGHTNING SLAM at the hammer head on the ground: a white flash 16 squares across centered on the cyan cross, "
         "4 jagged lightning arcs (2 squares thick) leaping up 14-20 squares from it, 8 gold sparks flying out low to "
         "both sides; nothing over his face."}, "right_low"),
    ("e_arc", "skill2", (4,), "over", "锤形 E 雷霆一击：往上挑的锤头带出的电弧（画进 E 第 4 帧）",
     "大锤往右上方挑起（青色十字是锤头）：锤头后面一道往上弯的电弧拖影，锤头一团电光爆开。画在他**上面**，别挡住脸。", f"{EL_} and {GO_}",
     {4: "a THUNDER ARC: a curved trail of crackling white-cyan lightning 4-6 squares thick sweeping up from below to the "
         "cyan cross (the raised hammer head), a burst of white-cyan light 14 squares across at the cyan cross with 6 gold "
         "sparks; nothing over his face."}, "top_right"),
    ("w_crown", "w_cast", (3,), "over", "锤形 W 闪电领域：高举的锤头上噼啪的闪电（画进 W 第 3 帧）",
     "大锤竖直高举（青色十字是锤头）：锤头周围噼啪地缠着几道闪电，一道闪电往天上窜，锤头一团白光。画在他**上面**。", EL_,
     {3: "LIGHTNING CROWNING the raised hammer head: a white-cyan glow 14 squares across round the cyan cross (the hammer "
         "head), 5 jagged lightning arcs (2 squares thick) crackling round it, one bolt shooting straight up 20 squares "
         "from it; nothing over his face."}, "top"),
    ("c_flash", "c_attack", (2,), "over", "炮形普攻：炮口火光（画进炮形普攻第 2 帧）",
     "开炮的一下：炮口（青色十字）前面一团白亮的炮口火光，往右喷出一小股电光。画在他**上面**。", EL_,
     {2: "a MUZZLE FLASH at the cannon's muzzle: a burst of white-cyan light 12 squares across centered 4 squares RIGHT "
         "of the cyan cross (the muzzle), 3 short spikes of light pointing right (the middle one longest, 10 squares), a "
         "ring of tiny sparks; nothing over his face."}, "right"),
    ("cq_charge", "c_skill", (3,), "over", "炮形 Q 电能震荡：竖起的炮口蓄能（画进炮形 Q 第 3 帧）",
     "炮几乎竖起来蓄能（青色十字是炮口）：炮口上方聚起一团旋转的电球，几道细电弧往里收。画在他**上面**。", EL_,
     {3: "CHARGING at the raised muzzle: a round glowing orb 10 squares across just above the cyan cross (the muzzle) - "
         "white core, pale cyan, cyan - with 5 thin lightning arcs curling inward to it; nothing over his face."}, "top"),
    ("cq_fire", "c_skill", (4,), "over", "炮形 Q 电能震荡：电球出膛（画进炮形 Q 第 4 帧）",
     "电球从炮口（青色十字）喷出去：炮口一团大的炮口火光，电球刚离开炮口往右飞（球心离炮口 12 格左右，后面拖电光）。画在他**上面**。", EL_,
     {4: "the ORB FIRED: a muzzle flash of white-cyan light 16 squares across at the cyan cross (the muzzle), the electric "
         "orb (10 squares across, white core, cyan, thin arcs) flying off to the RIGHT with its center 14 squares right of "
         "the cyan cross, a cyan trail between the muzzle and the orb; nothing over his face."}, "right"),
    ("hyper_glow", "c_skill2", (3,), "over", "炮形 W 超能电荷：炮身充能（画进炮形 W 第 3 帧）",
     "炮斜举着充能（青色十字是炮口）：炮口一团电光，沿着炮身跳几道细电弧。画在他**上面**，别挡住脸。", EL_,
     {3: "CHARGING the cannon: a white-cyan glow 10 squares across at the cyan cross (the muzzle), 4 thin lightning arcs "
         "(1-2 squares thick) jumping along the barrel back from the muzzle 20 squares, a few sparks; nothing over his "
         "face."}, "top_right"),
    ("g_charge", "ult", (4,), "over", "大招 加速电炮：竖起的炮口蓄满能（画进大招第 4 帧）",
     "炮竖起来蓄满能（青色十字是炮口）：炮口上方一团更大的电球，几道电弧往里收，旁边几道金色的光往上冲。画在他**上面**。",
     f"{EL_} and {GO_}",
     {4: "FULL CHARGE at the raised muzzle: a big round glowing orb 14 squares across just above the cyan cross (the "
         "muzzle), 6 lightning arcs curling inward to it, 4 gold streaks rising beside it; nothing over his face."}, "top"),
    ("g_fire", "ult", (5,), "over", "大招 加速电炮：大电球出膛（画进大招第 5 帧）",
     "大电球从炮口（青色十字）喷出去：炮口一大团炮口火光，大电球刚离开炮口往右飞（球心离炮口 16 格左右，后面拖长长的电光和金色加速线）。"
     "画在他**上面**。", f"{EL_} and {GO_}",
     {5: "the BIG ORB FIRED: a muzzle blast of white-cyan light 20 squares across at the cyan cross (the muzzle), the big "
         "orb (14 squares across, white core, cyan, arcs) flying off to the RIGHT with its center 18 squares right of the "
         "cyan cross, a long cyan trail and 2 thin gold speed lines between the muzzle and the orb; nothing over his "
         "face."}, "right"),
]
GROUPS = [
    ("bolts / orbs", ["Jayce_Base_Projectile", "Jayce_Base_Projectile_Blur", "Jayce_Base_Lightning_Trail",
                      "Jayce_Base_SphereWaves", "Jayce_Plasma_Beam1", "Jayce_speedlines"]),
    ("hits / blasts", ["Jayce_Hit_Flash", "Jayce_Hammer_Burst", "Jayce_Base_Shockwave", "Jayce_Shockwave",
                       "Jayce_Base_Lightning_Flash", "Jayce_Base_Star"]),
    ("lightning", ["Jayce_Base_Lightning_flipbook", "Jayce_Lightning_02", "Jayce_Base_Lightning_Scrolling",
                   "Jayce_Base_Energy", "Jayce_Lightning_Glow", "Jayce_Base_VerticalSwipe"]),
    ("ground / slam", ["Jayce_Base_Crack", "Jayce_Base_Crescent", "Jayce_Base_DonutGlow", "Jayce_Aura",
                       "Jayce_Hammer_Marks_SENT", "Jayce_Base_Embers"]),
    ("gate / colours", ["Jayce_Gent_GateBlue_TX_CM", "Jayce_Wall_Ball_TX", "Jayce_Color_Fade", "Jayce_Color_Fade2",
                        "Jayce_Color_Flashes", "Jayce_base_TX_CM"]),
    ("buffs", ["Global_Debuff_Armor_MR_Shred", "common_Slow-Wake", "Jayce_Base_Glow", "Jayce_Base_DonutGradient",
               "common_Sparks_BW", "Jayce_Confetti"]),
]
# where the pictures on him start (tag, frame, what, marks: "feet" = his standing point on the soles' line, or a bake
# guide's cross (name, n, "cyan"))
SHOTS = [("idle", 1, "q_slow / hyper / haste / guard / shred / tf_spark / w_field：他或目标身上（脚底在红线上）", "feet"),
         ("c_attack", 2, "c_bolt：从炮口飞出", ("c_flash", 2, "cyan")),
         ("c_skill", 4, "cq_orb：从炮口飞出", ("cq_fire", 4, "cyan")),
         ("ult", 5, "gq_orb：从炮口飞出", ("g_fire", 5, "cyan")),
         ("skill", 5, "q_land：锤头砸地", ("q_slam", 5, "cyan"))]
CELLS = {}                         # bake_guides' cells, for SHOTS' marks taken from them


def ref_sheet(path):
    S, LW = 180, 140
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                continue
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Jayce_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


SHEETS = {}


def frames_of(tag):
    if not SHEETS:
        SHEETS.update(P.read_sheet(SHEET))
    return [a for a, _ in SHEETS[tag]]


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def designs(path):
    pics = [crop(np.asarray(Image.open(os.path.join(HD, f)).convert("RGBA")))
            for f in ("hammer_front.png", "hammer_side.png", "cannon_front.png", "cannon_side.png")]
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + 12 * (len(pics) - 1)
    both = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        both[H - p.shape[0]:, x:x + p.shape[1]] = p
        x += p.shape[1] + 12
    Image.fromarray(np.repeat(np.repeat(both, 3, 0), 3, 1)).save(path)


def size_sheet(path):
    """His 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter."""
    import tfm2_ase as T
    fig = crop(frames_of("idle")[0])
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    kn = crop(np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA")))
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    top = max(fig.shape[0], kn.shape[0])
    img = Image.new("RGBA", (max(W * Z, 760), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
    img.alpha_composite(Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST),
                        (pad * Z, (base - fig.shape[0]) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fig.shape[1]) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.shape[1] + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"杰斯 {fig.shape[1]}×{fig.shape[0]} 格（连锤），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """Finished action frames (1x) at 4x, each picture's starting point as a cyan cross."""
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, marks in SHOTS:
        f = np.pad(frames_of(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px, py = f.shape[1] / 2.0, f.shape[0] / 2.0
        if marks == "feet":
            pts = [(px, py + FEET)]
        else:                          # a point of a bake guide (its dense frame centred on the pivot) in 1x px
            bn, bk, col = marks
            c = CELLS[(bn, bk)]
            x0, y0, W, H = c["frame"]
            cx, cy = c[col]
            pts = [(px + (cx + 0.5 - x0 - W / 2.0) / HD_PPU, py + (cy + 0.5 - y0 - H / 2.0) / HD_PPU)]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        for mx, my in pts:
            cx, cy = int((mx - x0) * Z), int((my - y0) * Z) + 24
            d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
            d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def bake_points(name, tag, k, a):
    """{"cyan": (x, y)} on the dense frame a (its pixels): the weapon's tip by the BAKE entry's rule - "right" the
    rightmost squares, "top" the topmost, "right_low" the rightmost of the lowest 40 %, "top_right" the squares furthest
    up and right (x - y)."""
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    rule = next(b[8] for b in BAKE if b[0] == name)
    if rule == "right":
        sel = xs >= xs.max() - 2
    elif rule == "top":
        sel = ys <= ys.min() + 2
    elif rule == "right_low":
        low = ys >= ys.max() - 0.4 * (ys.max() - ys.min())
        sel = low & (xs >= xs[low].max() - 2)
    else:
        v = xs - ys
        sel = v >= v.max() - 3
    return {"cyan": (float(xs[sel].mean()), float(ys[sel].mean()))}


def bake_guides(out):
    """bake/milio_bake_<name>_<n>.png: the finished dense frame faded on the guide canvas (LAND or PORT squares at
    BAKE_PX, his pivot on the canvas' pivot square), a light grid every 10 squares, the ground line red, the frame's box
    grey, the points as crosses. -> {(name, n): {"canvas": [w, h], "frame": [x0, y0, w, h], "cyan" / "yellow": [x, y]}}."""
    cells = {}
    for name, tag, ks, *_ in BAKE:
        for k in ks:
            a = frames_of("hd_" + tag)[k - 1]
            H, W = a.shape[:2]
            CW, CH, (gx, gy) = LAND if H / 2 <= LAND[2][1] - 4 and W / 2 <= LAND[2][0] else PORT
            x0, y0 = gx - W // 2, gy - H // 2
            assert x0 >= 0 and y0 >= 0 and x0 + W <= CW and y0 + H <= CH, (name, k, W, H)
            can = np.zeros((CH, CW, 4), np.uint8)
            can[y0:y0 + H, x0:x0 + W] = a
            img = Image.new("RGB", (CW * BAKE_PX, CH * BAKE_PX), (36, 40, 52))
            g = np.asarray(Image.fromarray(can).resize((CW * BAKE_PX, CH * BAKE_PX), Image.NEAREST)).astype(float)
            m = g[..., 3:] / 255.0
            grey = g[..., :3].mean(-1, keepdims=True) * 0.35 + 70
            base = np.asarray(img).astype(float)
            img = Image.fromarray((base * (1 - m) + grey * m).astype(np.uint8))
            d = ImageDraw.Draw(img)
            for x in range(0, CW + 1, 10):
                d.line([(x * BAKE_PX, 0), (x * BAKE_PX, img.height)], fill=(52, 58, 72))
            for y in range(0, CH + 1, 10):
                d.line([(0, y * BAKE_PX), (img.width, y * BAKE_PX)], fill=(52, 58, 72))
            ground = y0 + H / 2.0 + FEET * HD_PPU
            d.line([(0, ground * BAKE_PX), (img.width, ground * BAKE_PX)], fill=(150, 60, 60), width=2)
            d.rectangle([x0 * BAKE_PX, y0 * BAKE_PX, (x0 + W) * BAKE_PX - 1, (y0 + H) * BAKE_PX - 1],
                        outline=(96, 100, 112))
            pts = bake_points(name, tag, k, a)
            cell = {"canvas": [CW, CH], "px": BAKE_PX, "frame": [x0, y0, W, H], "into": f"hd_{tag} {k}",
                    "ppu": HD_PPU}
            for colour, rgb in (("cyan", (0, 255, 255)), ("yellow", (255, 220, 40))):
                if colour not in pts:
                    continue
                px_, py_ = pts[colour]
                cx, cy = int(round(px_ + x0)), int(round(py_ + y0))
                cell[colour] = [cx, cy]
                X, Y = (cx + 0.5) * BAKE_PX, (cy + 0.5) * BAKE_PX
                d.line([(X - 18, Y), (X + 18, Y)], fill=rgb, width=3)
                d.line([(X, Y - 18), (X, Y + 18)], fill=rgb, width=3)
            img.save(os.path.join(out, f"jayce_bake_{name}_{k}.png"))
            cells[(name, k)] = cell
    return cells


def document(shape, cells):
    h, w = shape[:2]
    L = []
    a = L.append
    n_bake = sum(len(b[2]) for b in BAKE)
    a("# 杰斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图 + {n_bake} 张画进他动作帧的图。** 造型和动作已定（`design/jayce_designs.png`：锤形正面、锤形侧身、"
      "炮形正面、炮形侧身；动作都是侧身朝右）。**全部用生图（image_gen）画，不要用代码拼方块。**")
    a(f"> - 他在游戏里是**高清**的：每个游戏像素里 1.5×1.5 个细格子；1 倍时锤形待机 {w}×{h} 格（连锤）。")
    a("> - **两种画法**：")
    a(f"> 1. 第一部分 {len(FX)} 张普通特效（电光弹、电球、打中、落地冲击、闪电领域、加速之门、身上的 buff）**照常按游戏格子画**（1 格 = 1 个游戏像素），"
      "不用画成高清。大小对照 `design/jayce_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；"
      "`design/jayce_shots.png` 是定稿动作（4 倍），青色十字是电光弹 / 电球飞出、锤头砸地的位置。")
    a("> 2. 第二部分是**画进他自己动作帧**的图（他的帧会随朝向镜像，特效图不会，所以炮口火光、炮口蓄能、锤头的电光拖影和砸地这些有方向的东西"
      "必须画进帧里）。这些按**他的高清细格子**画：`bake/jayce_bake_<名字>_<帧>.png` 是那一帧的定位图"
      f"（横图 {LAND[0]}×{LAND[1]} 格或竖图 {PORT[0]}×{PORT[1]} 格，每格 {BAKE_PX} 像素；他本人画成淡灰色、只用来对位置；灰框是这一帧的范围，"
      "红线是地面，每 10 格一道浅线；青色十字是起点：炮口或锤头）。**在同样大小、同样格子的图上只画特效，背景透明，不要画他本人**；Claude 按格子取回，"
      "直接叠进他的帧。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里杰斯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**海克斯科技的电光：白亮的芯、淡青、青色到深一点的电蓝**；**锤子砸中的地方加海克斯金色火星**；"
      "**加速之门是金色门柱 + 青色能量门面**；**削甲标记是左金右蓝的碎盾牌**。")
    a("> - **特效要亮**：每道电光、每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画两边，中间身体位置留空**；地上的冲击圈和闪电领域里面基本是空的，不要涂满；**他身上的 buff（超能电荷、护甲加成）要克制**。")
    a("> - **方向（重要，红色方不会镜像）**：飞行的电光弹 / 电球画成**朝右飞、上下对称**（游戏会把它转向飞行方向）；打中、目标身上、地上的画面、"
      "加速之门和身上的 buff 都要**严格左右对称**（逐格对称）。第二部分画进帧里的图照定位图的方向画（往右喷），不用对称。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `jayce_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），"
      f"以及 `jayce_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（{LAND[0]}×{LAND[1]} 或 {PORT[0]}×{PORT[1]}）。"
      "透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`（**原样，不要自己整理**），打包成 "
      "`jayce_fx_pack_done.zip`。**每张图单独交付，不要只给一张总览图**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 变形（锤 ↔ 炮）+ 被动「海克斯科技电容」 | 锤形大锤横扫 / 炮形电光弹；变形时一闪 + 加速，变炮后第一发削甲，变锤后加护甲 | "
      "`a_swipe`（帧里）· `a_hit` · `c_flash`（帧里）· `c_bolt` · `c_hit` · `tf_spark` · `haste` · `shred` · `guard` |")
    a("| 技能 1 = 锤形 Q「苍穹之跃」/ 炮形 Q「电能震荡」 | 锤形跳起砸向敌人，落点范围伤害 + 减速；炮形打出电球，撞到第一个敌人爆炸 | "
      "`q_slam`（帧里）· `q_land` · `q_hit` · `q_slow` · `cq_charge`（帧里）· `cq_fire`（帧里）· `cq_orb` · `cq_boom` · `cq_hit` |")
    a("| 技能 2 = 锤形 E「雷霆一击」+ W「闪电领域」/ 炮形 W「超能电荷」 | E 把敌人击飞；E 冷却时开闪电领域（脚下电场每半秒电一次周围敌人）；"
      "炮形 W 接下来 3 发更快更痛 | `e_arc`（帧里）· `e_blow` · `w_crown`（帧里）· `w_field` · `w_zap` · `hyper_glow`（帧里）· `hyper` |")
    a("| 大招「加速电炮」 | 立刻变炮，放下加速之门，打出穿门的大电球（更快、更远、更痛、爆炸更大） | `gate` · `g_charge`（帧里）· "
      "`g_fire`（帧里）· `gq_orb` · `gq_boom` · `gq_hit` · `haste` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**电光、光、火星都没有黑描边，也不要用最深的颜色给形状描一圈边**（加速之门的门柱是实物，可以有描边）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海克斯电光（电光弹、电球、打中、闪电领域、超能电荷）", ELEC), ("海克斯金色火星（锤子砸中、护甲加成）", GOLD),
                        ("加速之门", GATE), ("削甲标记", SHRED), ("加速", SPEED)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆炸居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。")
    a("- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 第一部分：特效（{len(FX)} 张，游戏格子）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位："
      "苍穹之跃落点半径 18000，闪电领域半径 20000，电能震荡爆炸半径 15000，加速电炮爆炸半径 21000）。大图（"
      + "、".join(sorted(BIG)) + "）按每格 8 像素画，其余每格 16 像素。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `jayce_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a(f"## 第二部分：画进他动作帧的图（{n_bake} 张，他的高清格子）\n")
    a(f"每张都在对应的定位图 `bake/jayce_bake_<名字>_<帧>.png` 上画：同样大小（横图 {LAND[0] * BAKE_PX}×{LAND[1] * BAKE_PX}、竖图 "
      f"{PORT[0] * BAKE_PX}×{PORT[1] * BAKE_PX} 像素）、每格 {BAKE_PX} 像素，格子和定位图完全对齐；**只画特效，不画他**，背景透明。"
      "他本人在定位图里是淡灰色，只用来对位置。青色十字是起点（炮口或锤头）。画在他**上面**的会盖住他（所以都别盖住他的脸）。"
      "尽量画在灰框里，喷出去的电球和光可以伸出灰框。注意这里 1 格只有游戏里的 0.67 个像素，所以线条至少 3 格粗，太细的进游戏就看不见了。\n")
    k0 = len(FX)
    for name, tag, ks, layer, title, zh, ramps, effects, _ in BAKE:
        k0 += 1
        a(f"### {k0}. {title}\n")
        a(zh + "\n")
        for k in ks:
            c = cells[(name, k)]
            where = f"青色十字在第 {c['cyan'][0]} 列、第 {c['cyan'][1]} 行"
            a(f"**`jayce_bake_{name}_{k}.png`**（定位图 `bake/jayce_bake_{name}_{k}.png`，{c['canvas'][0]}×{c['canvas'][1]} 格，{where}）：\n")
            crosses = f"the cyan cross of the guide is at square ({c['cyan'][0]}, {c['cyan'][1]})"
            a("```text")
            a(LEAD.format(ramps=ramps).replace("VFX sprite sheet", "VFX overlay on a character frame"))
            a(f"Effect: {effects[k]}")
            a(f"Layout: ONE image {c['canvas'][0] * BAKE_PX}x{c['canvas'][1] * BAKE_PX}, the same size and {BAKE_PX}-px "
              f"square grid as the guide picture (a {c['canvas'][0]} x {c['canvas'][1]} square grid); {crosses}, counted "
              "from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the "
              f"cross or the lines. {TAIL}")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `jayce_fx_{name}` | {bind} | {size} |")
    for name, tag, ks, layer, *_ in BAKE:
        a(f"| `jayce_bake_{name}_<帧>` | 画进 `hd_{tag}` 第 {'、'.join(str(k) for k in ks)} 帧（{'人物上面' if layer == 'over' else '人物后面'}） | 高清格子 |")
    a("")
    a("- 两张表：`asset/league/effects/league_jayce_fx`（小的）和 `league_jayce_big`（" + "、".join(sorted(BIG)) +
      "），tag = 名字（build_jayce.py 的 views）。")
    a("- 目标身上的 q_hit、w_zap、hyper、guard、tf_spark 底边放在脚底线（站位点下方 11.5 格）；地上的 w_field 椭圆中心、q_land 的落点、gate 的门柱底放在"
      "脚底线；w_field 8 帧摊满 240 tick；gate 6 帧约 1.2 秒；炮弹 / 电球的 y_offset 按 `design/jayce_shots.png` 的炮口高度重设"
      "（build_jayce c_y / cq_y / r_y）。")
    a("- 画进帧的图在 restyle 之后（rig_jayce.py --pinholes 那一步）按 `fx_bake_cells.json` 从画布上切下这一帧的范围，叠到 "
      "`assets/source/ppu/jayce_<tag>.png` 的高清帧上，伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新（rig_milio.bake 的做法）。")
    a("- 用 `pixel_1x/` 切格（import_milio_fx 的做法；Codex 自己读回太小太糊时从 raw 重读），断言对称；清掉 Codex 给电光描的最深色边；"
      "核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, BAKE
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="jayce_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "jayce_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        BAKE = [x for x in BAKE if x[0] in keep]
        if len(FX) + len(BAKE) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run Temp/jy_work/fx/fx_ref_jy.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs", "bake"):
        os.makedirs(os.path.join(out, sub))
    designs(os.path.join(out, "design", "jayce_designs.png"))
    shape = size_sheet(os.path.join(out, "design", "jayce_size.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    cells = bake_guides(os.path.join(out, "bake"))
    CELLS.update(cells)
    shots_sheet(os.path.join(out, "design", "jayce_shots.png"))
    doc = document(shape, cells)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"jayce_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "sheet": "big" if x[0] in BIG else "fx"} for x in FX] +
                  [{"file": f"jayce_bake_{b[0]}_{k}.png", "into": f"hd_{b[1]} {k}", "layer": b[3]}
                   for b in BAKE for k in b[2]], f, ensure_ascii=False, indent=1)
    cells_json = {f"{n}_{k}": c for (n, k), c in cells.items()}
    for path in (os.path.join(out, "bake_cells.json"),) + (() if a.only else
                                                          (os.path.join(SRC, "fx_bake_cells.json"),)):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cells_json, f, indent=1)
    print(len(FX), "effects,", sum(len(b[2]) for b in BAKE), "frame overlays;", DOC, shape)
    if not a.no_zip:
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
