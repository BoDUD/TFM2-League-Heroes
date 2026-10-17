#!/usr/bin/env python3
"""Build brand_fx_pack.zip: step 3 of Brand's sprite - Codex draws his effects (after tools/art/pack_gwen_fx.py).

    python tools/art/pack_brand_fx.py [--no-zip] [--out DIR] [--only a_hit,q_ball --name brand_fx_redo_pack]

The pack (%TEMP%/bd_work/fx/brand_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/brand/PROMPTS_FX.md), design/brand_design.png (8x), design/brand_size.png (the design at 4x on the arena
colour with the feet line, a 10-px ruler and the base fighter beside him), design/brand_shots.png (the action frames at
4x - tools/art/rig_brand.py - with the points the pictures drawn on him start from) and refs/lol_fx_ref.png (League's
own particle textures for Brand, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/bd_work/fxref, extracted from Brand.wad.client by the session's fx_ref_bd2.py).
The effects are the views the kit binds (tools/kit/build_brand.py: view_projectiles a_bolt, q_ball, r_ball; view_effects
a_hit, w_mark, w_pillar, w_hit, e_flare, e_hit, q_hit, r_cast, r_drop, r_hit, p_s1..p_s3 (one sheet of three cells),
p_boom, p_hit; view_buffs p_burn, p_unstable, q_stun, r_slow) and one picture drawn into his own frames at import
(c_flash at the fire hands: the attack's throw, E's flung arms, Q's thrust, W's slam). League's colours: fire from a
white-hot yellow core through orange to deep red, the lava cracks orange, black tar smoke at the edges. Fire gets no
outline (the bright-effects lesson); only the stack pips have a dark outline, to read over the battle.
Red side (the user's rule): the projectiles are turned to their flight - symmetric top and bottom; r_cast plays after
the action's first tick (not following) and every buff - symmetric left and right; c_flash rides in his frames.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "bd_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "brand", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "brand_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFDF0, #FFF2A8, #FFD64A, #FFA41C, #FF6A0C, #E0360A, #A81A08, #5E0C06"   # flames, fireballs, blasts
LAVA = "#FFF2B0, #FFC23A, #F27A12, #C2400C, #7A1E0A, #3A0E08"                    # lava drops, cracks, embers
TAR = "#6A5660, #4A3C44, #2E2228, #1A1216"                                         # black smoke at the edges
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around fire, sparks or smoke, BRIGHT colours (each flame lit with its lightest shades and a "
        "white-hot core - it must read on a dark battlefield), colours only from {ramps}.")
LEAD_MARKS = ("Pixel art game UI sprite sheet for a small tactics game: chunky square pixels, hard edges, no "
              "anti-aliasing, small bold marks with a 1-square dark outline #1A0A08 so they read over the battle, "
              "colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
FIG = "do NOT draw the figure; leave its place empty"
FR = f"a fire ramp ({FIRE})"
LV = f"a lava ramp ({LAVA})"
TR = f"a tar-smoke ramp ({TAR})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return (f"one horizontal row of {n} equal {shape} cells, image size {n * cw * 16}x{ch * 16} (each cell "
            f"{cw * 16}x{ch * 16}, 16 px a square)")


def grid(n, cols, cw, ch):
    rows = -(-n // cols)
    return (f"{rows} rows of {cols} equal {cw}:{ch} cells, image size {cols * cw * 16}x{rows * ch * 16} (each cell "
            f"{cw * 16}x{ch * 16}, 16 px a square), read left to right, the top row first")


def missile(what, length, thick, trail, frames=4):
    return (f"{what} flying to the RIGHT, the picture SYMMETRIC TOP AND BOTTOM (the game turns it to face its flight), "
            f"{frames} frames, a seamless loop: the head at the RIGHT, {thick} squares across with a white-hot core, "
            f"the flames licking back into a tapering trail {trail} squares long toward the LEFT, small sparks shed "
            f"behind; the flames flicker a little each frame. The whole picture about {length} squares long.")


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- drawn into his own frames (the client mirrors his frames, never an effect picture)
    ("c_flash", "施法火光：火焰手上爆一团火（画进他自己的出手帧），4 帧",
     "画进 attack 第 4 帧、skill2 第 3 帧（两只手）和第 6 帧、skill 第 4 帧（两只手）（`design/brand_shots.png` 的十字：火焰手；导入时烘进精灵帧）",
     "16",
     "出手那一下火焰手上爆开一团火：白热的芯、一圈橙红的火舌往外窜、几颗火星（参考 Q_Impact_04、Spark_Orange、common_Flare-Sun、Fire_Hand）。"
     "**左右上下都对称**（会用在不同方向的手上）。4 帧：1 一小团白热的光，2 火舌最大，3 火舌散开、火星飞出，4 几点火星淡去。约 16 格，居中画。",
     FR,
     "a FIRE FLASH bursting from a burning hand, SYMMETRIC in every direction, 4 frames: 1 a small white-hot glow 6 "
     "squares across at the center; 2 a burst of yellow-orange flame tongues 14 squares across round a white-hot core; "
     "3 the tongues breaking up, 6 orange sparks flying out; 4 a few fading sparks.",
     row(4, 18, 18) + "; centered in every cell."),
    ("r_cast", "R 烈焰风暴施放：他身边卷起的火焰（他身上，不跟随），6 帧",
     "view_effects `league_brand_r_cast`（施放第 4 tick 起，不跟随，画在人物上面；**左右对称**）", "40 × 48",
     "R 起跳时身边卷起一圈火：几道火焰从脚下螺旋往上卷，头顶一团火星，脚下一圈热浪（参考 R_Inhale、W_Swirl、W_FireUp、common_flames01）。"
     "人的位置留空，只画外围。**左右对称**。6 帧：1 脚下一圈火亮起，2–4 火焰绕着身体往上卷，5 在头顶聚成一团火星，6 散去。站位点在格子底部往上 3 格的中间。",
     FR,
     f"a SWIRL OF FIRE round a figure ({FIG}; only round it), SYMMETRIC LEFT AND RIGHT, 6 frames: 1 a flat ring of "
     "flame 30 squares wide at the feet lighting up; 2-4 tongues of fire spiralling up round the figure's place from the "
     "feet to above the head (40 squares tall); 5 the flames gathering into a burst of sparks 12 squares across above "
     "the head; 6 fading sparks.",
     row(6, 40, 48) + "; the standing point 3 squares above the bottom, horizontally centered, in every cell."),
    # ---- projectiles (turned to the flight: symmetric top and bottom)
    ("a_bolt", "普攻：一颗小火球（飞行，按方向转动），4 帧", "view_projectiles `league_brand_a_bolt`（循环；**上下对称**）",
     "14 × 6", "普攻扔出去的小火球：白热的芯、橙色火团、后面一小截火尾和几颗火星（参考 Trail02、Brandfiretrail、Q_Sparks_2x2）。"
     "**朝右飞、上下对称**。4 帧循环。约 14 格长、6 格高。",
     FR, missile("a SMALL FIREBALL", 14, 5, 8), row(4, 16, 8) + "; the fireball's head 2 squares from the right edge, "
     "vertically centered, in every cell."),
    ("q_ball", "Q 火焰烙印：一颗大火球（飞行，按方向转动），4 帧", "view_projectiles `league_brand_q_ball`（循环；**上下对称**）",
     "24 × 10", "Q 的火球：比普攻的大一圈，白热的芯、翻滚的橙红火焰、一条长长的火尾和黑烟，几颗火星往后甩（参考 Q_Smoke_Trail、"
     "Q_LavaSplurt01、Q_Sparks_2x2、Brand_Base_Trail）。**朝右飞、上下对称**。4 帧循环。约 24 格长、10 格高。",
     f"{FR} and {TR}", missile("a BIG ROLLING FIREBALL with a little black smoke at its trail's end", 24, 9, 15),
     row(4, 26, 12) + "; the fireball's head 2 squares from the right edge, vertically centered, in every cell."),
    ("r_ball", "R 火种：一颗熔岩火种（飞行，按方向转动），4 帧", "view_projectiles `league_brand_r_ball`（循环；**上下对称**）",
     "18 × 10", "R 的火种：一颗滴着熔岩的火球，外面绕着两圈小火星，后面拖一条熔岩火尾（参考 R_LavaDrop、R_LavaTrail、R_Trail03、"
     "R_Rocks_2x2）。**朝右飞、上下对称**。4 帧循环。约 18 格长、10 格高。",
     f"{FR} and {LV}", missile("a MOLTEN FIRE SEED (a lava-dripping fireball with sparks circling it)", 18, 8, 10),
     row(4, 20, 12) + "; the seed's head 2 squares from the right edge, vertically centered, in every cell."),
    # ---- on the targets
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_brand_a_hit`（跟随，画在人物上面）", "14",
     "小火球打中：一小团火爆开，几颗火星（参考 Q_Impact_04、Spark_Orange）。约 14 格，居中画。",
     FR, "a SMALL FIRE HIT, 4 frames: 1 a white-hot flash 6 squares across; 2 a burst of orange flame 12 squares "
     "across; 3 the flame breaking into sparks; 4 fading embers.", row(4, 16, 16) + "; centered in every cell."),
    ("q_hit", "Q 火球打中（目标身上，接着晕眩），5 帧", "view_effects `league_brand_q_hit`（跟随，画在人物上面）", "22",
     "Q 火球打中：一团大火爆开，火舌往四周窜，一圈火星和一点黑烟（参考 Q_Impact_04、Q_LavaSplurt01、Q_ErosionPack01、Q_Ash）。"
     "约 22 格，居中画。",
     f"{FR} and {TR}", "a BIG FIREBALL IMPACT, 5 frames: 1 a white-hot flash 10 squares across; 2 a burst of "
     "yellow-orange flame 20 squares across; 3 flame tongues spreading out, a ring of sparks; 4 the fire breaking up, "
     "a little black smoke; 5 fading embers and smoke.", row(5, 24, 24) + "; centered in every cell."),
    ("e_hit", "E 烈火燃烧点燃（每个被点燃的敌人身上），5 帧", "view_effects `league_brand_e_hit`（跟随，画在人物上面）", "18 × 24",
     "被 E 点燃：脚下一团火猛地往上窜，把人包住一下（参考 E_Conflagration_Shockwave、W_FireUp、common_flames01）。"
     "人的位置中间要淡，只是一闪。**左右对称**。5 帧：1 脚下一圈火，2–3 火往上窜到头顶，4 回落，5 余烬。站位点在格子底部往上 3 格的中间。",
     FR, f"a BURST OF FLAME ENGULFING a figure ({FIG}: the flames round it, its middle faint), SYMMETRIC LEFT AND "
     "RIGHT, 5 frames: 1 a flat ring of fire 16 squares wide at the feet; 2-3 tongues of flame shooting up round the "
     "figure's place to above the head (22 squares tall); 4 the flames falling back; 5 embers.",
     row(5, 20, 26) + "; the standing point 3 squares above the bottom, horizontally centered, in every cell."),
    ("r_drop", "R 弹跳：一颗火种从上面砸下来（落在被弹到的敌人身上），4 帧",
     "view_effects `league_brand_r_drop`（跟随，画在人物上面；**左右对称**；它播完时 r_hit 正好爆开）", "14 × 40",
     "R 的火种在敌人之间弹跳：每次弹到下一个敌人，就画成一颗带火尾的熔岩火种从上面斜着砸下来（参考 R_LavaDrop、R_LavaTrail、R_Trail03）。"
     "**左右对称**（竖直往下落）。4 帧：1 火种在格子顶部出现，2–3 往下落、火尾拉长，4 落到底部（站位点上面约 12 格，人的胸口）。约 14 格宽、40 格高。",
     f"{FR} and {LV}", "a MOLTEN FIRE SEED DROPPING straight down onto a figure, SYMMETRIC LEFT AND RIGHT, 4 frames: "
     "a lava-dripping fireball 8 squares across with a white-hot core and a flame trail streaming up behind it; 1 the "
     "seed at the top of the cell; 2-3 the seed falling, the trail longer; 4 the seed at its lowest point, 12 squares "
     "above the standing point (the figure's chest), the trail 20 squares long above it.",
     row(4, 16, 42) + "; the standing point at the bottom center of every cell (the seed never goes below 12 squares "
     "above it)."),
    ("r_hit", "R 火种打中（敌人身上），4 帧", "view_effects `league_brand_r_hit`（跟随，画在人物上面）", "18",
     "火种打中：一团熔岩火爆开，几滴熔岩溅出去（参考 R_Impact_04、R_Explosion_Texture、R_Rocks_2x2）。约 18 格，居中画。",
     f"{FR} and {LV}", "a LAVA IMPACT, 4 frames: 1 a white-hot flash 8 squares across; 2 a burst of fire 16 squares "
     "across; 3 lava droplets splashing out, sparks; 4 fading embers.", row(4, 20, 20) + "; centered in every cell."),
    ("p_hit", "被动引爆波及（每个被炸到的敌人身上），4 帧", "view_effects `league_brand_p_hit`（跟随，画在人物上面）", "16",
     "被被动爆炸炸到：一团火光一闪，几颗火星（参考 P_Tar_Impact_Erode、Spark_Orange）。约 16 格，居中画。",
     f"{FR} and {TR}", "a FIRE BLAST HIT, 4 frames: 1 a white-hot flash 8 squares across; 2 orange fire 14 squares "
     "across with a little black smoke; 3 sparks; 4 fading.", row(4, 18, 18) + "; centered in every cell."),
    # ---- on the ground / at a point (BIG, never turned: symmetric left and right)
    ("w_mark", "W 烈焰之柱预警：地上一圈发光的火纹（大，约 0.6 秒），6 帧",
     "view_effects `league_brand_w_mark`（BIG，画在人物下面，不跟随；**左右对称**；第 2–5 帧循环到火柱落下）", "48 × 22",
     "W 落下前地上的预警：一个扁椭圆的火圈，圈里地面裂开、透出熔岩的光，边上一圈小火苗，越来越亮（参考 W_Decal_Outeredge、W_LavaCracks、"
     "W_GroundCracks、MagicCircle03、Circle）。从斜上方看是扁的椭圆（约 46 格宽、20 格高），**左右对称**。6 帧：1 圈刚亮起，2–5 圈和裂纹"
     "越来越亮（这 4 帧能循环），6 最亮。椭圆居中。",
     f"{FR} and {LV}", "a FIRE WARNING CIRCLE on the ground seen from above at an angle, SYMMETRIC LEFT AND RIGHT, 6 "
     "frames: a flat ellipse 46 squares wide and 20 tall: a glowing orange ring along its edge with small flame "
     "licks, the ground inside cracked with glowing lava lines; 1 the ring faint; 2-5 the ring and the cracks growing "
     "brighter (these four frames loop); 6 the brightest.", grid(6, 3, 50, 24) + "; the ellipse centered in every cell."),
    ("w_pillar", "W 烈焰之柱：地上冲起的火柱（大），7 帧",
     "view_effects `league_brand_w_pillar`（BIG，不跟随，画在人物上面；**左右对称**；第 4 帧时伤害落下）", "48 × 72",
     "W 的火柱：地面炸开，一根粗大的火柱从椭圆里冲天而起，火舌翻滚，顶上爆成一团火，地上一圈冲击波和碎石（参考 W_FireWall、W_FireUp、"
     "W_Fire_Trail_Up、W_ImpactSprite2x2、W_Ring_Shockwave_2、W_Impactspike）。**左右对称**。7 帧：1 地面一圈白光，2 火柱冲到一半，"
     "3 火柱冲到最高（约 70 格），4 最亮、地上冲击波，5 火柱开始变细，6 散成火舌和火星，7 余烬和一点黑烟。火柱底部的椭圆中心在格子底部往上 10 格。",
     f"{FR} and {TR}", "a PILLAR OF FLAME erupting from the ground, SYMMETRIC LEFT AND RIGHT, 7 frames: its base a flat "
     "ellipse 46 squares wide and 20 tall centered 10 squares above the bottom of the cell; 1 the ground flashing "
     "white-orange inside the ellipse; 2 a column of fire 20 squares wide shooting up halfway; 3 the column at full "
     "height (70 squares), rolling flames, a burst of fire at the top; 4 the brightest, a shockwave ring spreading on "
     "the ground; 5 the column thinning; 6 breaking into flame tongues and sparks; 7 embers and a little black smoke.",
     row(7, 50, 74) + "; the base ellipse centered 10 squares above the bottom in every cell."),
    ("e_flare", "E 烈火燃烧：火从目标往四周蔓延的火环（大），6 帧",
     "view_effects `league_brand_e_flare`（BIG，不跟随，画在人物上面；**左右对称**）", "60 × 28",
     "E 的蔓延：目标脚下一团火往四周扩散成一圈火环，地上留下一圈烧焦的痕迹（参考 E_Conflagration_Shockwave、E_CircleThin、E_Swirl、"
     "E_GroundCracks_Outer、Tar_Ground_erode）。从斜上方看是扁的椭圆（最大约 58 格宽、26 格高），**左右对称**。6 帧：1 中心一团火，"
     "2–4 火环往外扩到最大，5 火环散成火苗，6 只剩焦痕和余烬。椭圆居中。",
     f"{FR} and {TR}", "a RING OF FIRE SPREADING on the ground seen from above at an angle, SYMMETRIC LEFT AND RIGHT, 6 "
     "frames: 1 a burst of fire 12 squares across at the center; 2-4 a ring of flame expanding into a flat ellipse "
     "(at most 58 squares wide and 26 tall), flame tongues standing up along it; 5 the ring breaking into small "
     "flames; 6 only a scorched ring and embers.", grid(6, 3, 62, 30) + "; the ellipse centered in every cell."),
    ("p_boom", "被动「炽热之焰」三层引爆：大爆炸（大），7 帧",
     "view_effects `league_brand_p_boom`（BIG，不跟随，画在人物上面；**左右对称**）", "56 × 44",
     "三层被动引爆：被点燃的英雄身上轰地炸开一团大火球，一圈火环和黑烟往外冲，碎火星四溅（参考 P_15、P_Tar_Impact_Erode、"
     "P_Smoke_2_Erosion、R_Explosion_Texture、common_Flare-Sun）。要比其他命中都大都亮。**左右对称**。7 帧：1 一团白热的光，2–3 火球膨胀到最大，"
     "4 一圈火环和黑烟往外冲，5–6 火球散开、火星四溅，7 余烬和烟。爆炸中心在格子中间偏下（地面上的人的胸口）。",
     f"{FR} and {TR}", "a BIG FIRE EXPLOSION, SYMMETRIC LEFT AND RIGHT, 7 frames: 1 a white-hot flash 12 squares "
     "across; 2-3 a fireball swelling to 36 squares across, a white-hot core; 4 a flat ring of fire and black smoke "
     "rushing out (54 squares wide); 5-6 the fireball breaking up, sparks flying everywhere; 7 embers and drifting "
     "smoke.", row(7, 58, 46) + "; the blast's center 18 squares above the bottom, horizontally centered, in every "
     "cell."),
    # ---- the passive's stacks over the head (marks, outlined)
    ("p_stacks", "被动层数：头顶 1 / 2 / 3 个小火苗记号（目标身上，一闪），3 格",
     "view_effects `league_brand_p_s1`…`p_s3`（第 k 格是 k 层：画 k 个火苗；画在头顶，不旋转）", "20 × 8",
     "技能打中英雄叠被动：在他头顶亮起 1、2、3 个小火苗记号（第 3 个亮起时要引爆）。3 个格子一样大，**第 1 格画 1 个火苗、第 2 格 2 个、"
     "第 3 格 3 个**（从左往右排，居中），第 3 格的三个火苗更大更亮。每个火苗约 4 格宽、6 格高，白黄的芯、橙红的火，1 格深色描边"
     "（参考 P_FlameTimer、P_TimerSpike）。",
     FR, "STACK MARKS, 3 cells: cell 1 one small flame mark at the center, cell 2 two flame marks side by side, "
     "cell 3 three flame marks side by side, a little bigger and brighter; each mark a tiny flame 4 squares wide and 6 "
     "tall, a white-yellow core, orange-red flame, a 1-square dark outline; the marks evenly spaced and centered.",
     row(3, 20, 8) + "."),
    # ---- buffs on the units (looping, symmetric left and right)
    ("p_burn", "被动「烈焰焚身」：燃烧中的敌人身上的小火（循环），4 帧",
     "view_buffs `league_brand_p_burn`（循环，画在人物上面；**左右对称**）", "22 × 30",
     "被点燃（烈焰焚身）时：身上几簇小火苗往上窜，几颗火星往上飘（参考 P_Fire_Mult、common_flames01、Spark_Orange）。"
     "不要挡住人：只画几簇小火和火星。**左右对称**。4 帧无缝循环。站位点在格子底部往上 3 格的中间。",
     FR, f"SMALL FLAMES ON a burning figure ({FIG}; only a few flames and sparks), SYMMETRIC LEFT AND RIGHT, 4 frames, "
     "a seamless loop: 3-4 small flame tongues 4-6 squares tall flickering at the figure's shoulders, waist and knees "
     "on both sides, 4 sparks rising, moving up a little each frame; the figure's middle stays empty.",
     row(4, 22, 30) + "; the standing point 3 squares above the bottom, horizontally centered, in every cell."),
    ("p_unstable", "被动三层：快要爆炸的火焰计时圈（2 秒，循环），4 帧",
     "view_buffs `league_brand_p_unstable`（循环，画在人物上面；**左右对称**）", "34 × 16",
     "三层后 2 秒要爆炸：脚下一圈发红发亮的火焰圈，圈上一圈尖刺状的火舌一跳一跳，像倒计时（参考 P_FlameTimer、P_TimerLine、P_TimerSpike、"
     "P_Timer_Line_03）。从斜上方看是扁的椭圆，**左右对称**。4 帧无缝循环（火舌一明一暗地跳）。站位点在格子中间。约 34 格宽、16 格高。",
     FR, "an UNSTABLE FIRE TIMER RING at a figure's feet, SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: a flat "
     "ellipse of glowing red-orange fire 30 squares wide and 12 tall round the standing point (the cell's center), "
     "8 spiky flame tongues 4 squares tall standing up along it, pulsing bright and dim in turn.",
     row(4, 34, 16) + "; the standing point at the center of every cell."),
    ("q_stun", "Q 晕眩：头顶转圈的火星（循环），4 帧",
     "view_buffs `league_brand_q_stun`（循环，画在人物上面；**左右对称**）", "20 × 8",
     "被火焰烙印晕住：头顶一圈小火星转圈（参考 Spark_Star、Spark_Orange）。扁椭圆，**左右对称**。4 帧无缝循环。约 20 格宽、8 格高，"
     "画在格子正中（导入时放到头顶）。",
     FR, "a STUN HALO, SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: 4 small four-pointed fire stars (3 squares "
     "each, white-hot cores) circling along a flat ellipse 18 squares wide and 5 tall, moving a quarter turn each frame.",
     row(4, 20, 8) + "; the ellipse centered in every cell."),
    ("r_slow", "R 减速：脚下一圈余烬（循环），4 帧", "view_buffs `league_brand_r_slow`（循环，画在人物下面；**左右对称**）", "26 × 10",
     "被 R 打到减速：脚下一圈烧红的地面和几簇小火苗（参考 Tar_Ground_erode、W_Tar_Wisps_4x1）。扁椭圆，**左右对称**。4 帧无缝循环。"
     "站位点在格子中间。约 26 格宽、10 格高。",
     f"{FR} and {TR}", "a SMOLDERING PATCH at a figure's feet, SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: a "
     "flat ellipse 24 squares wide and 8 tall of glowing embers and black tar round the standing point (the cell's "
     "center), 3 small flames flickering on it.", row(4, 26, 10) + "; the standing point at the center of every cell."),
]

GROUPS = [
    ("fireball", ["Brand_Base_Q_Impact_04", "Brand_Base_Q_LavaSplurt01", "Brand_Base_Q_Smoke_Trail", "Brand_Base_Trail02",
                  "Brandfiretrail", "Brand_Base_Q_Sparks_2x2"]),
    ("pillar", ["Brand_Base_W_FireWall", "Brand_Base_W_FireUp", "Brand_Base_W_Fire_Trail_Up", "Brand_Base_W_LavaCracks",
                "Brand_Base_W_Decal_Outeredge", "Brand_Base_W_Ring_Shockwave_2"]),
    ("spread", ["Brand_Base_E_Conflagration_Shockwave", "Brand_Base_E_CircleThin", "Brand_Base_E_Swirl",
                "Brand_Base_E_GroundCracks_Outer", "Brand_Base_Tar_Ground_erode", "Brand_Base_MagicCircle03"]),
    ("seed", ["Brand_Base_R_LavaDrop", "Brand_Base_R_LavaTrail", "Brand_Base_R_Trail03", "Brand_Base_R_Impact_04",
              "Brand_Base_R_Explosion_Texture", "Brand_Base_R_Rocks_2x2"]),
    ("blaze", ["Brand_Base_P_FlameTimer", "Brand_Base_P_TimerSpike", "Brand_Base_P_15", "Brand_Base_P_Fire_Mult",
               "Brand_Base_P_Tar_Impact_Erode", "Brand_Base_Spark_Orange"]),
]


def hand_points():
    """Where the fire hands are in the frames the flash is drawn into (rig_brand's quarter turns of the hand centres)."""
    import rig_brand as R
    back_hand, front_hand = (50.0, 84.5), (78.0, 86.5)

    def turned(hand, sh, k):
        dx, dy = hand[0] - sh[0], hand[1] - sh[1]
        for _ in range((k or 0) % 4):
            dx, dy = -dy, dx                    # a quarter turn clockwise on screen
        return sh[0] + dx, sh[1] + dy

    def hands(tag, n, which):
        back, front, dx, dy, crouch = R.STAND[tag][n - 1]
        pts = []
        if "back" in which:
            x, y = turned(back_hand, R.BACK_SHOULDER, back)
            pts.append((x + dx, y + dy + (crouch if y < R.KNEES else 0)))
        if "front" in which:
            x, y = turned(front_hand, R.FRONT_SHOULDER, front)
            pts.append((x + dx, y + dy + (crouch if y < R.KNEES else 0)))
        return pts

    return R, [("attack", 4, "c_flash: 出手的火焰手", hands("attack", 4, "front")),
               ("skill2", 3, "c_flash: E 张开的两只手", hands("skill2", 3, "back front")),
               ("skill2", 6, "c_flash: Q 推出的手", hands("skill2", 6, "front")),
               ("skill", 4, "c_flash: W 砸地的两只手", hands("skill", 4, "back front")),
               ("ult", 4, "r_cast: 站位点（他身边）", [(R.PIVOT[0], 100.0)])]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 12, 14, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(240, 230, 220, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.exists(p):
                continue
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Brand_Base_", "")[:26], fill=(210, 190, 170, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = design_1x()
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    img = Image.new("RGBA", (max(W * Z, 420), (pad + max(fig.shape[0], kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fig.shape[0], kn.shape[0])
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
    d.text((8, 36), f"布兰德 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The action frames at 4x (rig_brand.py), each picture's starting point as a cyan cross."""
    R, shots = hand_points()
    P = R.Parts()
    built = {}
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, pts in shots:
        if tag not in built:
            built[tag] = R.frames(P, tag)
        f = built[tag][k - 1]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 230), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        for mx, my in pts:
            cx, cy = int((mx - x0) * Z), int((my - y0) * Z) + 24
            d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
            d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    W = sum(t.width + 10 for t in tiles)
    H = max(t.height for t in tiles)
    sheet = Image.new("RGB", (W, H), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)
    return shots


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 复仇焰魂 布兰德：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/brand_design.png`，8 倍，连火焰 {h} 行）。")
    a(f"> - 大小对照 `design/brand_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。布兰德 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/brand_shots.png`：定稿动作（4 倍），青色十字是特效的起点（出手的火焰手、站位点），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里布兰德自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**火是白热的黄芯→橙→深红；熔岩是橙黄带黑；边上一点黑色焦油烟**。")
    a("> - **特效要亮**：每团火都要有最亮的几档和白热的芯，暗底上一眼能看见。")
    a("> - **挂在人身上的画面只画外围，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方规则）**：三种飞行道具（`a_bolt`、`q_ball`、`r_ball`）画成朝右飞，游戏会按飞行方向转，所以要**上下对称**。"
      "施法火光 `c_flash` 画进他自己的动作帧，要**各个方向都对称**。地上的、人身上的、他身边的（`r_cast`、`w_mark`、`w_pillar`、`e_flare`、`p_boom`、"
      "`e_hit`、`r_drop`、各个 buff）都要**左右对称**。头顶的层数记号不旋转。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `brand_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等大的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`brand_fx_done.zip`）放在 outputs 里，或放在 `outputs/brand-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「炽热之焰」 | 扔小火球；技能命中点燃敌人（烈焰焚身，持续灼烧）；技能命中英雄叠层，第 3 层时那个英雄 2 秒后爆炸，炸到周围的敌人 | `c_flash` · `a_bolt` · `a_hit` · `p_burn` · `p_stacks` · `p_unstable` · `p_boom` · `p_hit` |")
    a("| 技能 1 = W「烈焰之柱」 | 短暂延迟后在目标处冲起火柱，范围伤害并点燃 | `c_flash` · `w_mark` · `w_pillar` |")
    a("| 技能 2 = E「烈火燃烧」→ Q「火焰烙印」 | 点燃敌方英雄并蔓延到周围；随后火球打中第一个敌人并晕眩；打中英雄时再接一个烈焰之柱 | `c_flash` · `e_flare` · `e_hit` · `q_ball` · `q_hit` · `q_stun` |")
    a("| 大招 = R「烈焰风暴」 | 火种在敌人间弹跳 5 次，优先英雄，每次伤害、点燃并减速 | `r_cast` · `r_ball` · `r_drop` · `r_hit` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、火星、烟没有黑描边，也不要用最深的颜色给形状描一圈边**。只有头顶的层数记号有 1 格深色描边（`#1A0A08`）。")
    a("- **要亮**：每团火都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀（烟）。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火（火球、火柱、爆炸、火苗）", FIRE), ("熔岩（火种、熔岩滴、裂纹）", LAVA), ("焦油烟（边上的黑烟）", TAR)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在人身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 52000，"
      "W 火柱半径 23000，E 蔓延半径 24000 / 40000，被动爆炸半径 26000，R 弹跳范围 55000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `brand_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a((LEAD_MARKS if name == "p_stacks" else LEAD).format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `brand_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `c_flash` 写进 `assets/source/native/brand_bake.json`，烘进 attack 第 4 帧、skill2 第 3 帧（两只手）和第 6 帧、skill 第 4 帧（两只手）"
      "（客户端只镜像英雄自己的帧，不镜像特效图）；光在动作帧之内结束。")
    a("- `r_cast` 在 R 施放第 4 tick 起播放，不跟随（is_follow false），左右对称；buff（p_burn、p_unstable、q_stun、r_slow）左右对称、循环；"
      "`q_stun` 放到头顶（站位点上面约 46 格）；`p_stacks` 拆成 p_s1…p_s3（每个一张，画在头顶）。")
    a("- 三种飞行道具导入后用 lint 量上下翻转后的差别（要几乎为 0）；`w_mark` 2–5 帧循环铺满 w_delay（36 tick），`w_pillar` 第 4 帧对上伤害；"
      "`r_drop` 播完（r_fall 6 tick）时 `r_hit` 爆开。")
    a("- 清掉 Codex 给火描的最深色边（`import_riven.py` 的 `unrim`，层数记号保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，"
      "和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="brand_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack folder)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out or os.path.join(TMP, "fx"), a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: extract Brand's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "brand_design.png"))
    shape = size_sheet(os.path.join(out, "design", "brand_size.png"))
    shots = shots_sheet(os.path.join(out, "design", "brand_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump({"fx": [{"file": f"brand_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX],
                   "points": [{"tag": t, "frame": k, "what": w, "points": p} for t, k, w, p in shots]},
                  f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
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
