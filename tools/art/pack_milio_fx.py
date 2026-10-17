#!/usr/bin/env python3
"""Build milio_fx_pack.zip: step 3 of Milio's sprite - Codex draws his effects (tools/art/pack_kindred_fx.py's way:
effects at game pixels, plus pictures drawn into his own dense frames).

    python tools/art/pack_milio_fx.py [--no-zip] [--out DIR] [--only a_hit,q_land --name milio_fx_redo_pack]

The pack (%LOCALAPPDATA%/Temp/mi_work/fx/milio_fx_pack, zipped into --out, default dist/milio_packs) holds PROMPTS.md
(also written to assets/source/milio/PROMPTS_FX.md), design/milio_designs.png (the front design with the fire spirit,
the side design at 3x), design/milio_size.png (his 1x idle at 4x on the arena colour with the feet line, a 10-px ruler
and the base fighter), design/milio_shots.png (finished action frames, 1x at 4x, the points his pictures start from),
bake/milio_bake_<name>_<n>.png (the frame a picture is drawn INTO: his finished dense frame - the hd_ tag of
league/champions/league_milio, 2.2 squares a game pixel - faded on a guide canvas at BAKE_PX px a square, the points it
starts from as crosses) and refs/lol_fx_ref.png (League's own particle textures for Milio, grouped by the effect of
ours they inform; Riot's art, local only: %LOCALAPPDATA%/Temp/mi_work/fxref from Temp/mi_work/fx/fx_ref_mi.py).
The effects are the views the kit binds (tools/kit/build_milio.py: view_projectiles a_ball, q_ball, e_ball;
view_effects a_hit, q_hit, q_fall, q_land, q_burn, e_hug, w_heal, r_hit; view_buffs fired, e_on, w_fire, q_slow) and
the pictures drawn into his frames at import (BAKE): the client mirrors his frames with his facing and never an effect
picture, so whatever has a front and a back on him - the fireball leaving his palm, the ball at his foot and the kick,
the warm flame off his raised hand, the fire gathering over his hands and sweeping out along his arms in R - rides in
the frames (art-spec, league_nilah / league_kindred).
League's colours: Milio's fire is warm and friendly (white-yellow cores, gold to orange, a red-orange rim - no dark
smoke but the slow's embers); the heals add soft mint and green; Breath of Life a touch of rainbow sparkle. Light and
fire get no outline. Red side: projectiles symmetric top to bottom (they are turned to their flight); pictures on a
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

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mi_work")
REF = os.path.join(TMP, "fxref")
SRC = os.path.join(ROOT, "assets", "source", "milio")
DOC = os.path.join(SRC, "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_milio")
HD = os.path.join(SRC, "hd")
PRE = chr(92) * 2 + "?" + chr(92)
FEET = 11.5                         # 1x px from the pivot down to the soles' bottom edge
HD_PPU = P.PPU["milio"]             # his finished dense frames (2.2 squares a game pixel)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFFFF, #FFF6C7, #FFD84D, #FFA22E, #F4631E, #C33A1A"       # his friendly fire: white core, yellow, gold, orange
HUG = "#FFFFFF, #FFF1C2, #FFC861, #FF9A3C, #E06A2C"                 # Warm Hugs' shield: white, cream, gold, orange
HEAL = "#FFFFFF, #FFF6D6, #FFE08A, #C8F5A8, #7FE08E, #43B86A"       # the campfire's and R's heal: white, cream, mint, green
EMBER = "#FFD84D, #FFA22E, #F4631E, #C33A1A, #7A3B2A, #4A2620"      # the slow's embers: gold to red-orange, brown smoke
SPARK = "#FFFFFF, #9BE7FF, #C79BFF, #FFE08A"                        # R's rainbow sparkle accents (a few motes only)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around fire, light, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a "
        "white or pale core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, {px} px a square)"
FR_ = f"a warm fire ramp ({FIRE})"
HU_ = f"a warm shield ramp ({HUG})"
HE_ = f"a warm heal ramp ({HEAL})"
EM_ = f"an ember ramp ({EMBER})"
SP_ = f"a few rainbow sparkle accents ({SPARK})"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = "SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight)"
CENTER = "; centered in every cell."


def row(n, cw, ch, px=16):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * px, h=ch * px, cw=cw * px, ch=ch * px, px=px)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- in flight (turned to their flight)
    ("a_ball", "普攻小火球（飞行中，循环），4 帧",
     "view_projectiles `league_milio_a_ball`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 6",
     "米利欧甩出去的小火球：圆圆的一团火，白黄色的芯、金色到橙色的火，后面拖一小段火苗尾巴（参考 Flame01、Flame_Trail、BA_mis_glowTrail）。"
     "朝右飞。**上下对称**。4 帧无缝循环（火苗尾巴一跳一跳）。约 10 格长、6 格高。", FR_,
     f"a SMALL FIREBALL flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round ball of fire 5 squares across with "
     "a white-yellow core 2 squares, gold and orange round it, a red-orange rim only at the back; a tapering tail of "
     "orange flame tongues 5 squares long behind it; the tail flickers each frame.",
     row(4, 12, 8) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_ball", "Q 火爆飞踢：踢出去的大火球（飞行中，循环），4 帧",
     "view_projectiles `league_milio_q_ball`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 10",
     "踢出去的火球：比普攻大，一颗圆滚滚的大火球，外圈一圈跳动的火舌，后面拖一条更长的火焰尾巴，带几点火星（参考 Q_OrbEdge、Flame01、Flame_Trail）。"
     "**不要画脸**（它会被转向，脸会倒过来）。朝右飞。**上下对称**。4 帧无缝循环（火舌转动、火星往后飘）。约 16 格长、10 格高。", FR_,
     f"a BIG KICKED FIREBALL flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round ball 8 squares across - a "
     "white-yellow core 3 squares, gold and orange fire round it, a ring of small flame tongues on its edge - and a "
     "tapering tail of orange and red-orange flame 8 squares long behind it with 3 bright sparks; the flame tongues turn "
     "and the sparks drift back a square each frame; no face.",
     row(4, 18, 12) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_ball", "E 融融情谊：飞向队友的暖焰（飞行中，循环），4 帧",
     "view_projectiles `league_milio_e_ball`（朝飞行方向转，画成朝右飞；上下对称）", "12 × 6",
     "送给队友的一团暖焰：一团软软的金黄色火苗，奶油色的芯，后面飘着两缕弯弯的暖光丝（参考 E_Wisp_Trail、E_Mis_Trail_Arrow）。"
     "朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、6 格高。", HU_,
     f"a WARM WISP flying to the RIGHT, 4 frames, a seamless loop, {TB}: a soft round flame 5 squares across with a cream "
     "core 2 squares and gold and orange round it, two curling ribbons of warm light 1 square thick trailing 7 squares "
     "behind it (one above, one below, mirrored); the ribbons wave each frame.",
     row(4, 14, 8) + "; the flame's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    # ---- on a target
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_milio_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "小火球打中：一团火炸开，几颗火星往外蹦（参考 Sparkle、Flame01）。**左右对称**。约 12 格。", FR_,
     f"a SMALL FIRE HIT, 4 frames, {LR}: 1 a white-yellow flash 4 squares across; 2 a burst of orange fire 9 squares "
     "across with a white core and 4 flame tongues at mirrored places; 3 the tongues flying out to 12 squares, 4 sparks; "
     "4 a few fading sparks.",
     row(4, 14, 14) + CENTER),
    ("q_hit", "Q 火球踢中第一个敌人（目标身上，把它撞退），5 帧",
     "view_effects `league_milio_q_hit`（跟随，画在人物上面；左右对称）", "20",
     "火球撞上第一个敌人把它撞退：一个大一点的冲击——白黄色的闪光，一圈橙色的火环往外冲，几道火舌和火星（参考 Q_Tar_Impact、FlareRing、Sparkle）。"
     "**左右对称**。约 20 格。", FR_,
     f"a FIERY IMPACT, 5 frames, {LR}: 1 a white flash 6 squares across; 2 a white-yellow burst 12 squares across with a "
     "ring of orange fire round it; 3 the ring 20 squares across, 6 flame tongues and 6 sparks thrown out at mirrored "
     "places; 4 the ring breaking into flames; 5 fading sparks.",
     row(5, 22, 22) + CENTER),
    ("q_burn", "Q 火球落地烧到的敌人（每个目标身上），4 帧",
     "view_effects `league_milio_q_burn`（跟随，画在人物上面；左右对称）", "14 × 16",
     "火球落下来烧到的敌人：身上腾起几簇火苗、火星往上飘（参考 Flame01_2x2、Sparks）。**左右对称**，中间人形位置大致留空（6 格宽）。约 14 格宽、16 格高。",
     FR_,
     f"FLAMES CATCHING a figure, 4 frames, {LR}, a clear upright gap 6 squares wide in the middle: 1 small flames 3 "
     "squares tall at both sides near the bottom; 2 the flames 8 squares tall licking upward at both sides; 3 the flames "
     "at their top (14 squares), sparks rising; 4 the flames shrinking, embers.",
     row(4, 16, 18) + "; centered across, the flames' roots on the cell's bottom rows."),
    ("e_hug", "E 融融情谊：暖焰抱住队友、套上护盾（队友身上），5 帧",
     "view_effects `league_milio_e_hug`（跟随，画在人物上面；左右对称）", "26 × 32",
     "暖焰飞到队友身上抱住他：两条暖光像两只手臂一样从两边合拢，套上金色的护盾，一闪（参考 E_Shield02、E_Shield_Patterns、E_tar_Sphere、E_Face）。"
     "**左右对称**，中间人形位置留空（10 格宽、26 格高）。约 26 格宽、32 格高。", HU_,
     f"a WARM HUG round a figure, 5 frames, {LR}, the middle EMPTY (a clear upright area 10 squares wide and 26 tall): 1 "
     "two ribbons of warm light at both sides, low; 2 the ribbons sweeping up round the figure like two arms closing; "
     "3 they meet above the head as a golden shield outline (an upright oval 26 squares wide and 32 tall, 1-2 squares "
     "thick) with 4 cream sparkles at mirrored places; 4 the oval at its brightest; 5 the oval thinning to a few gold "
     "glints.",
     row(5, 28, 34) + "; centered across, the oval's bottom on the cell's bottom row."),
    ("w_heal", "W 依依不舍：营火给范围里的队友回血（队友身上，每秒一次），5 帧",
     "view_effects `league_milio_w_heal`（跟随，画在人物上面；左右对称）", "18 × 26",
     "营火每秒给周围的队友回一口血：脚下一圈暖光，几个小小的金色和薄荷绿的十字星光往上飘（参考 W_Heal、W_Overhead_Star、W_Sparks01）。"
     "**左右对称**，中间人形位置留空（8 格宽）。约 18 格宽、26 格高。", HE_,
     f"a WARM HEAL PULSE round a figure, 5 frames, {LR}, the middle EMPTY (a clear upright area 8 squares wide and 22 "
     "tall): 1 a small cream ellipse glow 12 squares wide on the ground at the bottom; 2 four small four-pointed stars "
     "(gold and mint, 3 squares) rising at both sides; 3 the stars at 14-20 squares, a few green motes; 4 the stars "
     "fading at the top; 5 the last glints.",
     row(5, 20, 28) + "; centered across, the ground glow on the cell's bottom row."),
    ("r_hit", "R 生生不息：给身边每个队友回血、净化（队友身上），6 帧",
     "view_effects `league_milio_r_hit`（跟随，画在人物上面；左右对称）", "28 × 36",
     "生生不息落到每个队友身上：脚下一圈金色的光环亮起，暖暖的火光和薄荷绿的治疗光一起从两边往上升，顶上开出一朵星光，带几点彩虹色的小光点"
     "（参考 R_Ring_Glow、R_AoE_Rune、R_flarebuilding、R_FlareRainbow、W_Heal）。**左右对称**，中间人形位置留空（10 格宽、28 格高）。约 28 格宽、36 格高。",
     f"{HE_}, {FR_} and {SP_}",
     f"a BREATH OF LIFE round a figure, 6 frames, {LR}, the middle EMPTY (a clear upright area 10 squares wide and 28 "
     "tall): 1 a gold ellipse ring 20 squares wide on the ground at the bottom; 2 warm flame light and mint healing light "
     "rising at both sides to 18 squares; 3 the light at its top (34 squares), a white four-pointed star 8 squares "
     "across blooming above the middle, 4 tiny rainbow sparkle motes (pale cyan, lilac) at mirrored places; 4 the star "
     "bright, green and gold motes rising; 5 the light thinning; 6 the last glints.",
     row(6, 30, 38) + "; centered across, the ground ring on the cell's bottom rows."),
    # ---- the fall and the landing (big)
    ("q_fall", "Q 火球从天上落向落点（地上，0.6 秒，大），6 帧",
     "view_effects `league_milio_q_fall`（BIG，不跟随，留在落点；左右对称；整个 0.6 秒落下的过程）", "50 × 64",
     "火球撞退敌人后飞上天、再落回来：画在落点上——地上先出现一个淡淡的伊施塔尔符文圆（从斜上方看的扁椭圆，半径 25 个游戏像素，参考 "
     "Q_IxtalDecal、Q_Ground_Decal），火球从格子顶上往下掉、越来越近（越掉越大一点），第 6 帧刚好落到椭圆中心。**左右对称**（火球画成正面看的圆球，"
     "火焰尾巴朝上）。这张很大：按**每格 8 像素**画。", FR_,
     f"a FIREBALL FALLING onto a spot, 6 frames, {LR}: on the ground at the bottom a faint flat ellipse 50 squares wide "
     "and 20 tall - a thin ring of warm orange light 1 square thick with a simple round rune pattern inside (thin gold "
     "arcs, mostly empty) - growing a little brighter frame by frame; above it a round fireball (white-yellow core, gold "
     "and orange fire, a short flame tail pointing UP) falling straight down the middle: 1 at the very top of the cell, 6 "
     "squares across; 2-5 lower and a little bigger each frame; 6 just touching the ellipse's center, 10 squares across, "
     "the rune ring at its brightest.",
     row(6, 54, 68, px=8) + "; centered across, the ellipse's center 10 squares above the cell's bottom edge."),
    ("q_land", "Q 火球落地爆开（地上，大），6 帧",
     "view_effects `league_milio_q_land`（BIG，不跟随，留在落点；左右对称）", "56 × 40",
     "火球砸到地上炸开：一团白黄色的火光炸起，一圈火焰沿着地面往外推到半径 25 个游戏像素（从斜上方看的扁椭圆），几块火星往四周飞（参考 Q_Smoke_Erode、"
     "FlareRing、Corki_R_Flame_Ring、Sparks）。要亮，但地上的圈里面别涂满。**左右对称**。这张很大：按**每格 8 像素**画。", FR_,
     f"a FIREBALL LANDING BURST, 6 frames, {LR}: 1 a white-yellow flash 12 squares across at the ground point; 2 a burst "
     "of fire 20 squares wide and 24 tall rising from it, a ring of flames starting out along the ground; 3 the fire "
     "column at its height (30 squares), the ground ring a flat ellipse 40 squares wide and 16 tall made of small flame "
     "tongues 2-4 squares tall; 4 the ring at full size (56 wide, 22 tall), 8 sparks flying out at mirrored places, the "
     "column breaking up; 5 the ring thinning to embers; 6 fading embers. The inside of the ring stays mostly empty.",
     row(6, 60, 44, px=8) + "; centered across, the ground point (the ellipse's center) 12 squares above the cell's "
                           "bottom edge."),
    # ---- buffs (loops on the unit)
    ("fired", "被动 热情洋溢：被米利欧技能碰到的队友（队友身上，5 秒，循环），4 帧",
     "view_buffs `league_milio_fired`（跟随，画在人物上面；左右对称）", "20 × 24",
     "被热情洋溢点燃的队友：手边和脚边跳着几颗小小的火星，一圈淡淡的暖光，**要克制**（很多人会同时带着它，持续 5 秒），别盖住人"
     "（参考 P_Pillar、P_WispTrail、Sparkle）。**左右对称**，中间人形位置留空（10 格宽）。4 帧无缝循环。约 20 格宽、24 格高。", FR_,
     f"a WARM GLOW of a fired-up figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 10 "
     "squares wide and 22 tall): small flame motes (1-2 squares) at both sides at hand and foot height, 2 thin upward "
     "flame wisps 4 squares tall at both sides, the motes taking turns to flare up; SUBTLE - small and sparse.",
     row(4, 22, 26) + "; centered across, the lowest motes on the cell's bottom rows."),
    ("e_on", "E 融融情谊的护盾（队友身上，护盾在就一直在，循环），4 帧",
     "view_buffs `league_milio_e_on`（跟随，画在人物上面；左右对称）", "26 × 32",
     "护盾还在的时候：队友身边一个金色的竖椭圆护盾——只有一圈细细的边（1-2 格），中间完全空着，边上几点奶油色的光一闪一闪、慢慢转（参考 "
     "E_Shield02、E_Shield_Pan、E_Shield_Patterns）。**左右对称**。4 帧无缝循环。约 26 格宽、32 格高。", HU_,
     f"a WARM SHIELD round a figure, 4 frames, a seamless loop, {LR}: the thin outline of an upright oval 26 squares wide "
     "and 32 tall, 1 square thick (2 at its sides), gold with cream highlights, completely EMPTY inside; 4 cream "
     "sparkles 2 squares big on the outline at mirrored places, moving a little along it each frame; a soft orange "
     "shimmer on the outline's lower half.",
     row(4, 28, 34) + "; centered across, the oval's bottom on the cell's bottom row."),
    ("w_fire", "W 依依不舍：跟着队友脚下的营火圈（地上，6 秒，循环，大），4 帧",
     "view_buffs `league_milio_w_fire`（BIG，画在人物下面，跟着队友走；左右对称、上下对称）", "70 × 28",
     "依依不舍：队友脚下一圈跟着他走的温暖营火——从斜上方看的扁椭圆（半径 35 个游戏像素），边上一圈小小的火苗一跳一跳，偶尔几颗火星，"
     "里面是空的、只有极淡的几点暖光（参考 W_Ring_Glow_Thicker、W_Rune02、W_Fire_Caustic、W_Indicator_Dot）。不能挡住站在里面的人。"
     "**左右对称**、**上下对称**。4 帧无缝循环。这张很大：按**每格 8 像素**画。", FR_,
     f"a CAMPFIRE RING on the ground seen from above at an angle, 4 frames, a seamless loop, {LR} and top to bottom: a "
     "flat ellipse 70 squares wide and 28 tall whose rim is a ring of small warm flames (tongues 2-5 squares tall, gold "
     "and orange with white-yellow tips) with a thin orange glow line 1 square thick; 4 sparks at mirrored places; the "
     "inside EMPTY but for 6 tiny faint warm dots; the flames flicker each frame, mirrored in every frame.",
     row(4, 74, 32, px=8) + CENTER),
    ("q_slow", "Q 落地的减速（敌人脚下，1.5 秒，循环），4 帧",
     "view_buffs `league_milio_q_slow`（跟随，画在人物下面；左右对称）", "16 × 8",
     "被火球砸中减速的敌人：脚下冒着几缕余烬和淡淡的烟，几颗火星（参考 Smoke2x2、Sparks）。**左右对称**。4 帧无缝循环。约 16 格宽、8 格高。", EM_,
     f"SMOULDERING EMBERS at a figure's feet, 4 frames, a seamless loop, {LR}: a flat patch 16 squares wide and 4 tall "
     "of glowing embers (gold and red-orange squares) on the ground, 4 small wisps of brown smoke 2-3 squares tall "
     "rising at mirrored places, 2 sparks; the embers pulse and the wisps drift up each frame.",
     row(4, 18, 10) + "; centered across, the ember patch on the cell's bottom rows."),
]
# pictures drawn INTO his own frames, on his finished dense grid (the hd_ tags, 2.2 squares a game pixel): name, tag,
# frames, over / under him, title (zh), description (zh), ramps, the effect (en) per frame
BAKE_PX = 8                          # guide px a square: 192 x 128 squares (or 128 x 192) on Codex's 1536 x 1024
LAND = (192, 128, (96, 64))          # canvas squares, the pivot's square (his frame centred on it)
PORT = (128, 192, (64, 96))
BAKE = [
    ("a_fling", "attack", (3,), "over", "普攻：手心甩出的小火球（画进普攻第 3 帧）",
     "米利欧把手往前一甩：张开的手心（青色十字）前面一团小火球正要飞出去，手心一闪暖光，后面拖一小段火苗。画在他**上面**，别挡住脸。", FR_,
     {3: "a SMALL FIREBALL leaving the open palm: a round ball of fire 10 squares across (white-yellow core 4 squares, "
         "gold and orange fire) centered 8 squares RIGHT of the cyan cross (the palm), a warm flash 12 squares across at "
         "the cyan cross, a short tail of orange flame tongues 8 squares long between the palm and the ball; nothing over "
         "his face."}),
    ("q_ready", "skill", (3,), "over", "Q 火爆飞踢：脚前准备踢的火球（画进 Q 第 3 帧）",
     "踢之前：一颗圆滚滚的大火球悬在他脚前（青色十字是球心），他的腿往后收准备踢。火球的样子和第一部分的 `q_ball` 一样（白黄芯、金橙火、"
     "一圈小火舌），但这里**正面看、不拖尾巴**，只有火舌往上跳。画在他**上面**。", FR_,
     {3: "a BIG FIREBALL hovering in front of the feet: a round ball 16 squares across centered on the cyan cross - a "
         "white-yellow core 6 squares, gold and orange fire, a ring of small flame tongues on its edge licking upward - "
         "no tail; nothing over his face."}),
    ("q_kick", "skill", (4,), "over", "Q 火爆飞踢：一脚踢中火球（画进 Q 第 4 帧）",
     "踢中的一下：踢出去的脚（黄色十字，脚尖）前面炸开一团白黄色的冲击光，火球被踢飞、往**右**飞出去（离开脚 10 格左右，拖一条火焰尾巴），"
     "几颗火星往四周蹦。画在他**上面**，别挡住脸。", FR_,
     {4: "the KICK: a white-yellow impact flash 16 squares across at the yellow cross (the kicking foot's toes), the "
         "big fireball (16 squares across, white-yellow core, gold and orange fire) flying off to the RIGHT with its "
         "center 18 squares right of the yellow cross, a tail of orange flame 14 squares long between the foot and the "
         "ball, 6 sparks 2-3 squares big bursting out round the foot; nothing over his face."}),
    ("e_gather", "skill2", (2,), "over", "E 融融情谊：举起的手里聚起暖焰（画进 E 第 2 帧）",
     "米利欧举起手：张开的手心（青色十字）上方聚起一团软软的金黄暖焰，两缕暖光丝绕着它转。画在他**上面**，别挡住脸。", HU_,
     {2: "a WARM FLAME gathering over the raised palm: a soft round flame 12 squares across (cream core 5 squares, gold "
         "and orange round it) just above the cyan cross (the palm), two curling ribbons of warm light 2 squares thick "
         "circling it; nothing over his face."}),
    ("e_send", "skill2", (3,), "over", "E 融融情谊：暖焰从手里飞出去（画进 E 第 3 帧）",
     "暖焰从高举的手心（青色十字）往**右上**飞出去送给队友：手心一闪奶油色的光，一团暖焰离开手 10 格左右，后面拖两缕弯弯的光丝。画在他**上面**。", HU_,
     {3: "the WARM FLAME SENT: a cream flash 12 squares across at the cyan cross (the raised palm), the soft round flame "
         "(12 squares across, cream core, gold and orange) flying off up and to the RIGHT with its center 14 squares "
         "right of and 8 squares above the cyan cross, two curling ribbons of warm light 2 squares thick trailing back "
         "to the palm; nothing over his face."}),
    ("r_rise", "ult", (3,), "over", "R 生生不息：跳到最高点，双手上方聚起火焰（画进大招第 3 帧）",
     "跳到最高点：两只举起的手（青色、黄色十字）上方各卷起一团暖焰，两团火之间连成一道金色的光弧，几颗火星往上飘。画在他**上面**，别挡住脸。",
     f"{FR_} and {SP_}",
     {3: "FIRE GATHERING over two raised hands: a curl of warm flame 12 squares across rising over the cyan cross and "
         "another over the yellow cross (the two hands), a golden arc of light 3 squares thick joining them over the "
         "head, 6 sparks and 2 tiny rainbow sparkles rising; nothing over his face."}),
    ("r_burst", "ult", (4,), "over", "R 生生不息：落地张开双臂，暖光往四周涌出去（画进大招第 4 帧）",
     "落地、双臂张开像拥抱大家：两只手（青色、黄色十字）沿着手臂往外涌出两道暖光和火焰，脚下一圈金色的光环亮起（从斜上方看的扁椭圆，"
     "宽 70 格），一朵白色的星光在他胸前闪一下，几点薄荷绿和彩虹色的小光点。画在他**上面**，别挡住脸。", f"{FR_}, {HE_} and {SP_}",
     {4: "a WARM BURST from open arms: a sweep of warm flame and light 8 squares thick streaming outward 20 squares "
         "beyond the cyan cross (one hand, to the LEFT) and 20 squares beyond the yellow cross (the other hand, to the "
         "RIGHT); a flat gold ellipse ring 70 squares wide and 18 tall, 2 squares thick, round his feet on the ground "
         "line; a white four-pointed star 10 squares across at his chest; 8 mint and 4 rainbow sparkle motes 2 squares "
         "big round him; nothing over his face."}),
    ("r_fade", "ult", (5,), "over", "R 生生不息：暖光散开的余光（画进大招第 5 帧）",
     "暖光散开：两只手（青色、黄色十字）边上留着两小团火苗，脚下的光环变淡变细，金色和薄荷绿的光点往上飘散。画在他**上面**，别挡住脸。",
     f"{FR_} and {HE_}",
     {5: "the BURST FADING: two small curls of warm flame 6 squares across at the cyan cross and the yellow cross (the "
         "two hands), a thin faint gold ellipse ring 70 squares wide and 18 tall, 1 square thick, round his feet on the "
         "ground line, 10 gold and mint motes 2 squares big drifting up round him; nothing over his face."}),
]
GROUPS = [
    ("fire / balls", ["Milio_Base_Flame01_2x2_AlphaBlend", "Milio_Base_Flame_Trail", "Milio_Base_BA_mis_glowTrail02",
                      "Milio_Base_Q_OrbEdge", "Milio_Base_FIre_ColorPalette", "Milio_Base_Sparkle"]),
    ("Q fall / land", ["Milio_Base_Q_IxtalDecal_Add", "Milio_Base_Q_IxtalDecal_Core", "Milio_Base_Q_Ground_Decal_Additive",
                       "Milio_Base_Q_Tar_Impact_Erode", "Milio_Base_Q_Smoke_Erode", "Corki_Base_R_Flame_Ring"]),
    ("E hug / shield", ["Milio_Base_E_Shield02", "Milio_Base_E_Shield_Patterns", "Milio_Base_E_tar_Sphere",
                        "Milio_Base_E_Wisp_Trail", "Milio_Base_E_Mis_Trail_Arrow", "Milio_Base_E_Face_01"]),
    ("W campfire / heal", ["Milio_Base_W_Ring_Glow_Thicker", "Milio_Base_W_Rune02_Outer", "Milio_Base_W_Fire_Caustic01",
                           "Milio_Base_W_Heal", "Milio_Base_W_Overhead_Star", "Milio_Base_W_Indicator_Dot"]),
    ("R breath", ["Milio_Base_R_Ring_Glow", "Milio_Base_R_AoE_Rune", "Milio_Base_R_flarebuilding",
                  "Milio_Base_R_FlareRainbow", "Milio_Base_R_Swirl_OuterRing", "Milio_Rainbow_Ring01"]),
    ("passive / slow", ["Milio_Base_P_Pillar", "Milio_Base_P_WispTrail_Add", "Milio_Base_P_Nova", "Milio_Base_Smoke2x2",
                        "Sparks", "Milio_Base_W_Sparks01"]),
]
# where the pictures on him start (tag, frame, what, marks: "feet" = his standing point on the soles' line, or
# [(dx, dy)] in game px from the pivot, x forward, y down; the soles 11.5 under it)
SHOTS = [("idle", 1, "fired / e_on / w_heal / r_hit：队友身上（脚底在红线上）", "feet"),
         ("attack", 3, "a_ball：从手心飞出（手心高度）", ("a_fling", 3, "cyan")),
         ("skill", 4, "q_ball：从踢出去的脚飞出", ("q_kick", 4, "yellow")),
         ("ult", 4, "r_hit 落到身边队友：他脚下", "feet")]
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
            d.text((LW + c * S + 4, y + 2), nm.replace("Milio_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    pics = [crop(np.asarray(Image.open(os.path.join(HD, f)).convert("RGBA"))) for f in ("front.png", "side.png")]
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
    d.text((8, 36), f"米利欧 {fig.shape[1]}×{fig.shape[0]} 格（连火精灵），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
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


def skin_mask(a):
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (rgb[..., 0] > 170) & (rgb[..., 1] > 80) & (rgb[..., 1] < 145) & (rgb[..., 2] < 70) & \
        (rgb[..., 0] - rgb[..., 1] > 60)


def sandal_mask(a):
    rgb = a[..., :3].astype(int)
    return (a[..., 3] > 0) & (rgb[..., 0] > 60) & (rgb[..., 0] < 190) & (rgb[..., 1] > 35) & (rgb[..., 1] < 135) & \
        (rgb[..., 2] < 60) & (rgb[..., 0] - rgb[..., 1] > 25) & (rgb[..., 0] - rgb[..., 1] < 75)


def bake_points(name, tag, k, a):
    """{"cyan": (x, y), "yellow": (x, y)} on the dense frame a (its pixels) for this picture."""
    from scipy import ndimage
    op = a[..., 3] > 0
    H, W = a.shape[:2]
    ys, xs = np.nonzero(op)
    skin = skin_mask(a)
    pts = {}
    if name == "a_fling":                        # the open palm: the rightmost skin
        sy, sx = np.nonzero(skin)
        near = sx >= sx.max() - 4
        pts["cyan"] = (float(sx[near].mean()), float(sy[near].mean()))
    elif name == "q_ready":                      # in front of his feet, at shin height
        low = op.copy()
        low[:int(ys.max() - 0.35 * (ys.max() - ys.min()))] = False
        lx = np.nonzero(low.any(0))[0]
        pts["cyan"] = (float(lx.max() + 10), float(ys.max() - 14))
    elif name == "q_kick":                       # the kicking foot: the rightmost sandal squares
        sd = sandal_mask(a)
        sy, sx = np.nonzero(sd)
        near = sx >= sx.max() - 4
        pts["yellow"] = (float(sx[near].mean()), float(sy[near].mean()))
    elif name in ("e_gather", "e_send"):         # the raised palm: the topmost skin
        sy, sx = np.nonzero(skin)
        top = sy <= sy.min() + 4
        pts["cyan"] = (float(sx[top].mean()), float(sy[top].mean()))
    elif name == "r_rise":                       # two raised hands: the two topmost skin pieces
        top = skin.copy()
        top[int(ys.min() + 0.35 * (ys.max() - ys.min())):] = False
        lbl, n = ndimage.label(top, structure=np.ones((3, 3)))
        sizes = ndimage.sum(top, lbl, range(1, n + 1))
        big = sorted([i + 1 for i in np.argsort(-sizes)[:2]], key=lambda j: np.nonzero(lbl == j)[1].mean())
        for col, j in zip(("cyan", "yellow"), big):
            yy, xx = np.nonzero(lbl == j)
            t = yy <= yy.min() + 3
            pts[col] = (float(xx[t].mean()), float(yy[t].mean()))
    elif name in ("r_burst", "r_fade"):          # open arms: the leftmost and the rightmost skin
        sy, sx = np.nonzero(skin)
        lft, rgt = sx <= sx.min() + 3, sx >= sx.max() - 3
        pts["cyan"] = (float(sx[lft].mean()), float(sy[lft].mean()))
        pts["yellow"] = (float(sx[rgt].mean()), float(sy[rgt].mean()))
    return pts


def bake_guides(out):
    """bake/milio_bake_<name>_<n>.png: the finished dense frame faded on the guide canvas (LAND or PORT squares at
    BAKE_PX, his pivot on the canvas' pivot square), a light grid every 10 squares, the ground line red, the frame's box
    grey, the points as crosses. -> {(name, n): {"canvas": [w, h], "frame": [x0, y0, w, h], "cyan" / "yellow": [x, y]}}."""
    cells = {}
    for name, tag, ks, _, *_ in BAKE:
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
            img.save(os.path.join(out, f"milio_bake_{name}_{k}.png"))
            cells[(name, k)] = cell
    return cells


def document(shape, cells):
    h, w = shape[:2]
    L = []
    a = L.append
    n_bake = sum(len(b[2]) for b in BAKE)
    a("# 米利欧（明烛）：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图 + {n_bake} 张画进他动作帧的图。** 造型和动作已定（`design/milio_designs.png`：3/4 正面待机"
      "（男孩 + 肩后的小火精灵）、侧身；动作都是侧身朝右，火精灵飘在他身后）。")
    a(f"> - 他在游戏里是**高清**的：每个游戏像素里 2.2×2.2 个细格子；1 倍时 {w}×{h} 格（连火精灵）。")
    a("> - **两种画法**：")
    a(f"> 1. 第一部分 {len(FX)} 张普通特效（火球、打中、落点、队友身上的光、地上的营火圈）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。"
      "大小对照 `design/milio_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；"
      "`design/milio_shots.png` 是定稿动作（4 倍），青色十字是火球飞出、特效落下的位置。")
    a("> 2. 第二部分是**画进他自己动作帧**的图（他的帧会随朝向镜像，特效图不会，所以手心的火球、脚前的火球和踢中的一下、举手的暖焰、"
      "大招时双手的火这些有方向的东西必须画进帧里）。这些按**他的高清细格子**画：`bake/milio_bake_<名字>_<帧>.png` 是那一帧的定位图"
      f"（横图 {LAND[0]}×{LAND[1]} 格或竖图 {PORT[0]}×{PORT[1]} 格，每格 {BAKE_PX} 像素；他本人画成淡灰色、只用来对位置；灰框是这一帧的范围，"
      "红线是地面，每 10 格一道浅线；青色、黄色十字是起点）。**在同样大小、同样格子的图上只画特效，背景透明，不要画他本人**；Claude 按格子取回，"
      "直接叠进他的帧。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里米利欧自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**米利欧的火是温暖友好的火：白黄色的芯、金色到橙色、外圈红橙**（没有黑烟，只有减速的余烬带一点褐色烟）；"
      "**治疗加一点薄荷绿**；**大招带几颗彩虹色的小光点**。")
    a("> - **特效要亮**：每团火、每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画两边，中间身体位置留空**；地上的营火圈和落点符文圈里面基本是空的，不要涂满；**队友身上的 buff（热情洋溢、护盾）要克制**，"
      "很多人会同时带着它们。")
    a("> - **方向（重要，红色方不会镜像）**：飞行的火球画成**朝右飞、上下对称**（游戏会把它转向飞行方向；**飞行的火球上不要画脸**，转向后脸会倒过来）；"
      "打中、目标身上、地上的画面和队友身上的 buff 都要**严格左右对称**（逐格对称）。第二部分画进帧里的图照定位图的方向画（火球往右飞），不用对称。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `milio_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），"
      f"以及 `milio_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（{LAND[0]}×{LAND[1]} 或 {PORT[0]}×{PORT[1]}）。"
      "透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`（**原样，不要自己整理**），打包成 "
      "`milio_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**；**每张图单独交付，不要只给一张总览图**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「热情洋溢！」 | 甩出小火球；被他的技能碰到的队友 5 秒内攻击力和法强提高（身上跳着小火星） | `a_fling`（帧里）· `a_ball` · "
      "`a_hit` · `fired` |")
    a("| 技能 1 = Q「火爆飞踢」 | 踢出一颗大火球，撞退第一个敌人；火球飞上天再落下，砸中周围的敌人并减速 | `q_ready`（帧里）· `q_kick`（帧里）· "
      "`q_ball` · `q_hit` · `q_fall` · `q_land` · `q_burn` · `q_slow` |")
    a("| 技能 2 = E「融融情谊」+ W「依依不舍」 | E：送一团暖焰给队友，套上护盾、加移速；W 冷却好时同一下在他脚下点起营火，营火跟着他走、每秒给周围队友回血、"
      "加射程 | `e_gather`（帧里）· `e_send`（帧里）· `e_ball` · `e_hug` · `e_on` · `w_fire` · `w_heal` |")
    a("| 大招「生生不息」 | 跳起、落地张开双臂：身边所有队友回血、免控、加韧性 | `r_rise`（帧里）· `r_burst`（帧里）· `r_fade`（帧里）· `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、火星、光丝都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("米利欧的火（火球、打中、落地、营火、热情洋溢）", FIRE), ("融融情谊（暖焰、护盾）", HUG),
                        ("治疗（营火回血、大招）", HEAL), ("余烬（减速）", EMBER), ("大招的彩虹小光点（只点缀几颗）", SPARK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。")
    a("- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 第一部分：特效（{len(FX)} 张，游戏格子）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位："
      "普攻射程 53000，Q 落地半径 25000，营火半径 35000）。三张大图（q_fall、q_land、w_fire）按每格 8 像素画，其余每格 16 像素。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `milio_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a(f"## 第二部分：画进他动作帧的图（{n_bake} 张，他的高清格子）\n")
    a(f"每张都在对应的定位图 `bake/milio_bake_<名字>_<帧>.png` 上画：同样大小（横图 {LAND[0] * BAKE_PX}×{LAND[1] * BAKE_PX}、竖图 "
      f"{PORT[0] * BAKE_PX}×{PORT[1] * BAKE_PX} 像素）、每格 {BAKE_PX} 像素，格子和定位图完全对齐；**只画特效，不画他**，背景透明。"
      "他本人在定位图里是淡灰色，只用来对位置。青色、黄色十字是起点（手心、脚尖、球心）。画在他**上面**的会盖住他（所以都别盖住他的脸）。"
      "尽量画在灰框里，飞出去的火球和光可以伸出灰框。注意这里 1 格只有游戏里的 0.45 个像素，所以线条至少 2 格粗，太细的进游戏就看不见了。\n")
    k0 = len(FX)
    for name, tag, ks, layer, title, zh, ramps, effects in BAKE:
        k0 += 1
        a(f"### {k0}. {title}\n")
        a(zh + "\n")
        for k in ks:
            c = cells[(name, k)]
            where = "，".join(f"{'青色' if col == 'cyan' else '黄色'}十字在第 {c[col][0]} 列、第 {c[col][1]} 行"
                             for col in ("cyan", "yellow") if col in c)
            a(f"**`milio_bake_{name}_{k}.png`**（定位图 `bake/milio_bake_{name}_{k}.png`，{c['canvas'][0]}×{c['canvas'][1]} 格，{where}）：\n")
            crosses = "; ".join(f"the {col} cross of the guide is at square ({c[col][0]}, {c[col][1]})"
                                for col in ("cyan", "yellow") if col in c)
            a("```text")
            a(LEAD.format(ramps=ramps).replace("VFX sprite sheet", "VFX overlay on a character frame"))
            a(f"Effect: {effects[k]}")
            a(f"Layout: ONE image {c['canvas'][0] * BAKE_PX}x{c['canvas'][1] * BAKE_PX}, the same size and {BAKE_PX}-px "
              f"square grid as the guide picture (a {c['canvas'][0]} x {c['canvas'][1]} square grid); {crosses}, counted "
              "from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the "
              f"crosses or the lines. {TAIL}")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `milio_fx_{name}` | {bind} | {size} |")
    for name, tag, ks, layer, *_ in BAKE:
        a(f"| `milio_bake_{name}_<帧>` | 画进 `hd_{tag}` 第 {'、'.join(str(k) for k in ks)} 帧（{'人物上面' if layer == 'over' else '人物后面'}） | 高清格子 |")
    a("")
    a("- 两张表：`asset/league/effects/league_milio_fx`（小的）和 `league_milio_fx_big`（q_fall、q_land、w_fire），tag = 名字（build_milio.py 的 views）。")
    a("- 队友身上的 fired、e_on、w_heal、r_hit、e_hug 底边放在脚底线（站位点下方 11.5 格）；地上的 w_fire 椭圆中心、q_land / q_fall 的落点放在脚底线；"
      "q_fall 6 帧摊满火球飞行的 36 tick；w_fire 4 帧按营火 360 tick 循环。")
    a("- 画进帧的图在 restyle 之后（rig_milio.py --pinholes 那一步）按 `fx_bake_cells.json` 从画布上切下这一帧的范围，叠到 "
      "`assets/source/ppu/milio_<tag>.png` 的高清帧上，伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新。")
    a("- 用 `pixel_1x/` 切格（import_kindred_fx 的做法；Codex 自己读回太小太糊时从 raw 重读），断言对称；清掉 Codex 给火描的最深色边；"
      "核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, BAKE
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="milio_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "milio_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run Temp/mi_work/fx/fx_ref_mi.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs", "bake"):
        os.makedirs(os.path.join(out, sub))
    designs(os.path.join(out, "design", "milio_designs.png"))
    shape = size_sheet(os.path.join(out, "design", "milio_size.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    cells = bake_guides(os.path.join(out, "bake"))
    CELLS.update(cells)
    shots_sheet(os.path.join(out, "design", "milio_shots.png"))
    doc = document(shape, cells)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"milio_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX] +
                  [{"file": f"milio_bake_{b[0]}_{k}.png", "into": f"hd_{b[1]} {k}", "layer": b[3]}
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
