#!/usr/bin/env python3
"""Build qiyana_fx_pack.zip: step 3 of Qiyana's sprite - Codex (or Gemini) draws her effects (pack_naafiri_fx.py's way).

    python tools/lol/fx_ref_qiyana.py         # League's particle textures -> C:/t/qy_work/fxref (Riot's art, local only)
    python tools/art/pack_qiyana_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name qiyana_fx_redo_pack]

The pack (C:/t/qy_work/fx/qiyana_fx_pack, zipped into --out, default dist/qiyana_packs) holds PROMPTS.md (also written
to assets/source/qiyana/PROMPTS_FX.md), design/qiyana_designs.png (the step-0 design brought to her 60 squares at PPU
1.5, 4x), design/qiyana_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/lol_fx_ref.png (League's own particle textures for Qiyana, grouped by the effect they inform).
Step 1 (the game-size model) is still with Codex, so the design sheet is the step-0 picture cut to her size: the
effects only need where she stands and how big she is.
The effects are the views the kit binds (tools/kit/build_qiyana.py): view_projectiles r_wave; view_effects a_hit,
w_hit, p_hit, w_on, q_swing, q_w, q_r, q_g, q_hit, q_w_hit, q_r_hit, q_g_hit, e_hit, r_swing, r_burst, r_hit;
view_buffs el_g, el_w, el_r, q_slow, q_haste. League's colours: her royal power GOLD with TEAL (her jewels), the three
elements GRASS green (leaves and blades of grass), RIVER blue (water and ice), ROCK amber-brown (stone and dust); R
mixes all three. Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is
symmetric left to right; the projectile is turned with its flight, so it is drawn flying right and symmetric top to
bottom; the forward pictures (FORWARD: Q's four sweeps, R's swing and its burst) are drawn into her own frames
(tools/fix/bake_caster_fx.py) and point right with no symmetry - the kit's CasterViewEffects for them become copies of
her skill / ult animations with the picture in (one per element) when the frames exist.
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
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/qy_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "qiyana", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "qiyana", "hd")
NAME = "qiyana_fx_pack"
PPU = 1.5
ROWS = 60   # her design's rows at PPU 1.5 (the user's 40 game px)

GOLD = "#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210"      # her royal light: strikes, the crown
TEAL = "#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466"               # her jewels' teal (accents, the enchant)
GRASS = "#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C"              # grass: leaves, blades of grass
RIVER = "#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A"     # river: water, spray, ice
ROCK = "#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10"      # rock: stone chips, dust (chips solid: outlined)
GO = f"a royal gold light ramp ({GOLD})"
TE = f"teal jewel accents ({TEAL})"
GR = f"a grass-green ramp ({GRASS})"
RI = f"a river blue water-and-ice ramp ({RIVER})"
RO = f"a rock amber-brown stone-and-dust ramp ({ROCK})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
FWD = "pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry)"
CENTER = RF.CENTER
row = RF.row
HER = "she stands in the middle, not drawn: 40 squares from her crest to her soles, her body about 14 squares wide"
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
FRONT = ("she stands at the cell's LEFT edge, not drawn (her front - the side she faces - at about 8 squares from the left "
         "edge, her soles on the cell's bottom row)")
SOLID = "SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack, the passive, Terrashape's enchant
    ("a_hit", "普攻：圆环砍中目标，3 帧", "view_effects `league_qiyana_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "圆环砍中：一道金色的弧形刃光一闪，芯是白的，带两三点青绿色的火星（参考 ba_hit_tar_sharp、z_slash）。**左右对称**，3 帧。",
     GO + ", " + TE,
     "A BLADE HIT, 3 frames, " + LR + ": 1 two short curved gold slash arcs crossing in an X 9 squares across with a "
     "white core; 2 the arcs fading, a few gold and teal sparks flying out; 3 fading sparks.",
     row(3, 12, 12) + CENTER),
    ("w_hit", "附魔普攻的额外伤害，3 帧", "view_effects `league_qiyana_w_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "武器附了元素时普攻多打的一下：一小团亮光，绕着三颗小光点——绿（草）、蓝（水）、琥珀（石），不分元素都用这一张。**左右对称**，3 帧。",
     GO + ", " + GR + ", " + RI + ", " + RO,
     "AN ENCHANTED STRIKE, 3 frames, " + LR + ": 1 a small gold star flash 5 squares across with a white core; 2 three "
     "tiny motes bursting out of it - one green, one blue, one amber; 3 the motes fading.",
     row(3, 10, 10) + CENTER),
    ("p_hit", "被动 凌人贵气：第一下的额外伤害，4 帧", "view_effects `league_qiyana_p_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "对一个敌人的第一下：目标头上方亮起一顶小小的金色王冠（嵌一块青绿宝石，像她的头冠），往下一压碎成金光。**左右对称**，4 帧。",
     GO + ", " + TE,
     "A ROYAL MARK, 4 frames, " + LR + ": 1 a small gold crown (a row of 5 points, a teal gem in the middle, 9 squares "
     "wide) appearing in the cell's upper half; 2 brightest, a white glint on it; 3 the crown pressing down and breaking "
     "into gold shards; 4 the shards fading.",
     row(4, 14, 14) + CENTER),
    ("w_on", "E 落地附魔（方圆塑令）：武器吸取元素，4 帧", "view_effects `league_qiyana_w_on`（她身上，z 3；左右对称）", "30 × 34",
     "突进落地、圆环附上元素的一刻：她脚下一圈金色光环亮起，一股金青色的光带绕着她旋上去，夹着三色的小光点（绿、蓝、琥珀）。"
     "**中间她的身体位置留空**（只画外圈），**左右对称**，4 帧（参考 w_gainele_tex、w_flares_03）。",
     GO + ", " + TE + ", " + GR + ", " + RI + ", " + RO,
     "AN ENCHANT SWIRL, 4 frames, " + LR + ": 1 a flat gold ground ellipse 26 squares wide and 6 tall lighting up at the "
     "bottom; 2 two gold-teal light ribbons rising from it at both sides; 3 the ribbons high at both sides, small green, "
     "blue and amber motes along them; 4 fading motes. The middle EMPTY where her body is.",
     row(4, 30, 34) + "; the ellipse on the cell's bottom rows; " + HER + " (her soles on the cell's bottom row)."),
    # ---- Q Edge of Ixtal: the sweeps in front of her (drawn into her frames) and their hits
    ("q_swing", "Q 以绪塔尔之锋（没有元素）：圆环横扫，4 帧", "画进她的 skill 帧（朝右，不对称）", "40 × 26",
     "没有元素时的 Q：圆环往前横扫出一道宽宽的金色月牙刃光（芯白，边上一点青绿），从她身前左上扫到右下。**朝右画，不对称**，4 帧。",
     GO + ", " + TE,
     "A SWEEPING CRESCENT, 4 frames, " + FWD + ": 1 the start of a thick gold crescent at her front, upper left; 2 the "
     "whole crescent sweeping out to the right, 30 squares long and 8 thick at its middle, a white leading edge, a thin "
     "teal rim; 3 the crescent thinning at the right; 4 gold sparks fading at its end.",
     row(4, 40, 26) + "; " + FRONT + "."),
    ("q_w", "Q 河流：水与冰的横扫，4 帧", "画进她的 skill_w 帧（朝右，不对称）", "44 × 26",
     "河流元素的 Q：横扫出一道蓝色的水浪月牙，浪尖上凝出几片白蓝色的冰晶（参考 q_iceshards、q_water_tar_icetex）。**朝右画，不对称**，4 帧。",
     RI,
     "A WATER CRESCENT, 4 frames, " + FWD + ": 1 a curl of blue water starting at her front; 2 a thick crescent wave of "
     "blue water sweeping out to the right, 34 squares long, white spray on its crest; 3 the wave freezing at its end into "
     "a few pale blue ice shards; 4 the shards and droplets falling. " + SOLID + ".",
     row(4, 44, 26) + "; " + FRONT + "."),
    ("q_r", "Q 岩石：地刺破土，5 帧", "画进她的 skill_r 帧（朝右，不对称）", "44 × 28",
     "岩石元素的 Q：圆环砸向前方的地面，一排琥珀棕色的尖石从地里接连冒出，越往前越高，扬起尘土（参考 q_earth_break、w_mis_rock_spikes）。"
     "**朝右画，不对称**，5 帧。",
     RO + ", " + GO,
     "A ROW OF ROCK SPIKES, 5 frames, " + FWD + ": 1 a gold flash and cracks on the ground at her front; 2 three jagged "
     "amber-brown stone spikes bursting up in a row to the right, growing taller (6, 10 and 14 squares); 3 all spikes up, "
     "dust clouds at their feet, stone chips flying; 4 the spikes crumbling; 5 dust and falling chips. " + SOLID + ".",
     row(5, 44, 28) + "; the spikes stand on the cell's bottom row; " + FRONT + "."),
    ("q_g", "Q 草丛：草叶刃风，4 帧", "画进她的 skill_g 帧（朝右，不对称）", "44 × 26",
     "草丛元素的 Q：横扫出一阵绿色的风，卷着一片片细长的草叶刃往前飞（参考 q_mis_grass_bw、z_grass）。**朝右画，不对称**，4 帧。",
     GR + ", " + GO,
     "A GUST OF GRASS BLADES, 4 frames, " + FWD + ": 1 a green swirl starting at her front; 2 a crescent of green wind "
     "sweeping out to the right, 34 squares long, full of long thin grass blades and leaves; 3 the blades flying on ahead "
     "of it; 4 a few leaves fluttering away.",
     row(4, 44, 26) + "; " + FRONT + "."),
    ("q_hit", "Q 打中（没有元素），3 帧", "view_effects `league_qiyana_q_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "横扫打中：一道横的金色刃光带一圈小火星。**左右对称**，3 帧。",
     GO + ", " + TE,
     "A SWEEP HIT, 3 frames, " + LR + ": 1 a horizontal gold slash streak 11 squares long with a white core; 2 it "
     "breaking into gold and teal sparks flying out to both sides; 3 fading sparks.",
     row(3, 12, 12) + CENTER),
    ("q_w_hit", "Q 河流打中：冰定身，4 帧", "view_effects `league_qiyana_q_w_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "被河流 Q 打中、定在原地：水花溅开，目标脚下冻出一圈尖尖的冰晶把脚锁住（0.5 秒）。**左右对称**，4 帧。",
     RI,
     "A FREEZING SPLASH, 4 frames, " + LR + ": 1 a blue water splash bursting up in the middle; 2 the water falling, a "
     "ring of pale blue ice shards growing up round the bottom (where the feet are), 6 squares tall; 3 the ice ring full, "
     "white glints on it; 4 the ice cracking into small shards. " + SOLID + ".",
     row(4, 18, 16) + "; the ice ring on the cell's bottom rows; " + TARGET + " (only its lower 16 squares are in the "
     "cell)."),
    ("q_r_hit", "Q 岩石打中，4 帧", "view_effects `league_qiyana_q_r_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被岩石 Q 打中：一团琥珀色的石块迸开，尘土四散，中间一闪金光。**左右对称**，4 帧。",
     RO + ", " + GO,
     "A ROCK BURST, 4 frames, " + LR + ": 1 a gold flash with a white core in the middle; 2 amber-brown stone chips "
     "(2-3 squares each) bursting out to both sides with dust; 3 the chips farther, the dust spreading; 4 dust fading. "
     + SOLID + ".",
     row(4, 16, 16) + CENTER),
    ("q_g_hit", "Q 草丛打中，3 帧", "view_effects `league_qiyana_q_g_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被草丛 Q 打中：几片锋利的草叶从两边划过，留下两道绿色的刃痕。**左右对称**，3 帧。",
     GR,
     "A LEAF CUT, 3 frames, " + LR + ": 1 two green slash streaks crossing in an X with a pale core, leaves at their "
     "ends; 2 the streaks fading, 4 leaves fluttering out to both sides; 3 fading leaves.",
     row(3, 14, 14) + CENTER),
    # ---- E Audacity
    ("e_hit", "E 天纵之勇：突进砍中，3 帧", "view_effects `league_qiyana_e_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "突进砍中：一个大的金色 X 刃光，中间一颗青绿色的星点。**左右对称**，3 帧。",
     GO + ", " + TE,
     "A DASH STRIKE, 3 frames, " + LR + ": 1 a big gold X of two slash streaks 12 squares across, a white core and a "
     "teal star in the middle; 2 the X fading, gold sparks flying out; 3 fading sparks.",
     row(3, 14, 14) + CENTER),
    # ---- R Supreme Display of Talent
    ("r_swing", "大招 惊才绝景：圆环抡一大圈，4 帧", "画进她的 ult 帧（朝右，不对称）", "36 × 36",
     "大招起手：她把圆环抡过头顶往前一挥，留下一道几乎一整圈的金色刃光，青绿色的边，往前（右）收尾最亮。**朝右画，不对称**，4 帧。",
     GO + ", " + TE,
     "A GREAT CIRCLE SWING, 4 frames, " + FWD + ": 1 a gold arc starting behind her at the upper left; 2 the arc sweeping "
     "over the top, a thick gold ring two thirds round, white leading edge, teal rim; 3 the arc coming down in front at "
     "the right, brightest there; 4 gold sparks fading at the front.",
     row(4, 36, 36) + "; she stands in the middle of the cell, not drawn (40 squares tall: her head reaches the top "
     "rows), her soles on the cell's bottom row."),
    ("r_burst", "大招：冲击波在她脚前爆开，4 帧", "画进她的 ult 帧（朝右，不对称）", "40 × 20",
     "圆环砸地、冲击波出发的一刻：她身前的地面炸开，石块、水花、草叶三样一起往前（右）喷出去（参考 r_cas_wave、r_explode_ground）。"
     "**朝右画，不对称**，4 帧。",
     GO + ", " + RO + ", " + RI + ", " + GR,
     "A GROUND BLAST, 4 frames, " + FWD + ": 1 a gold flash on the ground at her front; 2 the ground bursting forward: "
     "amber stone chips, blue water spray and green grass blades thrown up and to the right in a fan 14 squares tall; "
     "3 the fan farther right, dust behind it; 4 falling bits and dust. " + SOLID + ".",
     row(4, 40, 20) + "; the blast on the cell's bottom rows; " + FRONT + "."),
    ("r_wave", "大招的冲击波（飞行），4 帧", "view_projectiles `league_qiyana_r_wave`（随飞行方向转；上下对称）", "32 × 22",
     "往前推进的冲击波：一道竖着的弧形波前（像一面往前推的墙），前沿金白色，里面混着碎石、水花和草叶，后面拖着尘土（参考 r_cas_wave、"
     "r_edge2、r_mis_water_freeze、r_windwall_rocks_tex）。**朝右飞、上下对称**，4 帧循环。",
     GO + ", " + RO + ", " + RI + ", " + GR,
     "A ROLLING SHOCKWAVE, 4 frames, a seamless loop, " + TB + ": a tall curved wave front (a ')' shape 20 squares tall "
     "at the right), its leading edge gold-white, inside it tumbling amber stone chips, blue water spray and green grass "
     "blades (placed square for square the same above and below the middle line), a trail of dust and spray 14 squares "
     "long behind it on the left; the bits tumble a little each frame. " + SOLID + ".",
     row(4, 32, 22) + CENTER),
    ("r_hit", "大招打中：击退后眩晕，4 帧", "view_effects `league_qiyana_r_hit`（跟随目标，z 2；左右对称）", "20 × 20",
     "被冲击波打中：一大团爆开——金光、石块、冰晶、草叶一起迸出（三种元素一起引爆）。**左右对称**，4 帧。",
     GO + ", " + RO + ", " + RI + ", " + GR,
     "AN ELEMENTAL BURST, 4 frames, " + LR + ": 1 a big gold flash 12 squares across with a white core; 2 a ring "
     "bursting out of it: amber stone chips, pale blue ice shards and green leaves, placed in mirror pairs; 3 the ring "
     "wider, dust and spray; 4 fading bits. " + SOLID + ".",
     row(4, 20, 20) + CENTER),
    # ---- buffs
    ("el_g", "带着草丛元素（循环），4 帧", "view_buffs `league_qiyana_el_g`（跟着她，循环，z 3；左右对称）", "34 × 12",
     "武器附了草丛：她腰部一圈有三四片绿色的小叶子绕着转（前面的叶子亮、后面的暗）。**中间她的身体位置留空**，**左右对称**，4 帧循环。",
     GR,
     "ORBITING LEAVES, 4 frames, a seamless loop, " + LR + ": four small green leaves (2-3 squares) on a flat ellipse 30 "
     "squares wide and 8 tall round her waist, placed in mirror pairs, stepping round it each frame, the front ones "
     "brighter; the middle EMPTY.",
     row(4, 34, 12) + "; the ellipse on the cell's middle; " + HER + " (the cell is at her waist)."),
    ("el_w", "带着河流元素（循环），4 帧", "view_buffs `league_qiyana_el_w`（跟着她，循环，z 3；左右对称）", "34 × 12",
     "武器附了河流：她腰部一圈有几颗蓝色的水珠绕着转，带一点白色的水光。**中间留空**，**左右对称**，4 帧循环。",
     RI,
     "ORBITING WATER DROPS, 4 frames, a seamless loop, " + LR + ": four blue water drops (2 squares, a white glint) on a "
     "flat ellipse 30 squares wide and 8 tall round her waist, placed in mirror pairs, stepping round it each frame, "
     "the front ones brighter, a thin stream of droplets between them; the middle EMPTY.",
     row(4, 34, 12) + "; the ellipse on the cell's middle; " + HER + " (the cell is at her waist)."),
    ("el_r", "带着岩石元素（循环），4 帧", "view_buffs `league_qiyana_el_r`（跟着她，循环，z 3；左右对称）", "34 × 12",
     "武器附了岩石：她腰部一圈有几块琥珀色的小石块绕着转，带一点尘土。**中间留空**，**左右对称**，4 帧循环。",
     RO,
     "ORBITING STONES, 4 frames, a seamless loop, " + LR + ": four small amber-brown stone chips (2-3 squares) on a flat "
     "ellipse 30 squares wide and 8 tall round her waist, placed in mirror pairs, stepping round it each frame, the front "
     "ones brighter, a little dust behind each; the middle EMPTY. " + SOLID + ".",
     row(4, 34, 12) + "; the ellipse on the cell's middle; " + HER + " (the cell is at her waist)."),
    ("q_slow", "河流 Q 之后减速（循环），4 帧", "view_buffs `league_qiyana_q_slow`（跟着目标，循环，z 3；左右对称）", "18 × 8",
     "被减速的敌人：脚下一小片蓝色的水洼，冒着白色的寒气。**左右对称**，4 帧循环。",
     RI,
     "A COLD PUDDLE, 4 frames, a seamless loop, " + LR + ": a flat blue puddle ellipse 16 squares wide and 4 tall on the "
     "cell's bottom rows, two or three small white frost wisps rising from it in turn.",
     row(4, 18, 8) + "; " + TARGET + " (only its feet reach the cell)."),
    ("q_haste", "草丛 Q 之后加速（循环），4 帧", "view_buffs `league_qiyana_q_haste`（跟着她，循环，z -1；左右对称）", "30 × 10",
     "草丛 Q 的伪装加速：她脚下有一圈细细的绿色风痕，几片草叶贴地打转。**中间留空**，**左右对称**，4 帧循环。",
     GR,
     "A GRASS WIND AT THE FEET, 4 frames, a seamless loop, " + LR + ": a thin green wind ellipse 26 squares wide and 6 "
     "tall on the cell's bottom rows (only its rim drawn), three small grass blades whirling along it in mirror pairs; "
     "the middle EMPTY.",
     row(4, 30, 10) + "; " + HER + " (only her feet reach the cell)."),
]
BIG_FX = ["q_swing", "q_w", "q_r", "q_g", "r_swing", "r_burst", "r_wave"]
FLYING = ["r_wave"]
FORWARD = ["q_swing", "q_w", "q_r", "q_g", "r_swing", "r_burst"]

GROUPS = [
    ("a_hit / q_hit / e_hit / p_hit", ["qiyana_base_ba_hit_tar_sharp", "qiyana_base_gp_swipeglowburst",
                                       "qiyana_base_z_slash", "qiyana_base_gp_alphaglows"]),
    ("w_on / w_hit / el_*", ["qiyana_base_w_gainele_tex", "qiyana_base_w_flares_03", "qiyana_base_blade_water_01",
                             "qiyana_base_weapon_earth_shard", "qiyana_base_qw_mis_leaves"]),
    ("q_g / q_g_hit / q_haste", ["qiyana_base_q_mis_grass_bw", "qiyana_base_z_grass", "qiyana_base_w_mis_grass_bw",
                                 "qiyana_base_wq_earth_meshtex"]),
    ("q_w / q_w_hit / q_slow", ["qiyana_base_q_iceshards", "qiyana_base_q_water_tar_icetex", "qiyana_base_r_ice_glow",
                                "qiyana_base_r_icespike_texture"]),
    ("q_r / q_r_hit", ["qiyana_base_q_earth_break", "qiyana_base_q_ground_clump", "qiyana_base_w_mis_rock_spikes",
                       "gnarbig_base_q_rocks"]),
    ("r_swing / r_burst / r_wave / r_hit", ["qiyana_base_r_cas_wave", "qiyana_base_r_edge2",
                                            "qiyana_base_r_mis_water_freeze_erode", "qiyana_base_r_windwall_rocks_tex",
                                            "qiyana_base_r_explode_ground"]),
]


def design():
    """Her step-0 design brought to her squares (ROWS at PPU 1.5), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, "A.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, ROWS / d.shape[0], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def design_1x():
    """The design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, "A.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, ROWS / d.shape[0] / PPU, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Her at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    import tfm2_ase as T
    figs = [design_1x()]
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
    d.text((8, 36), f"奇亚娜 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """Her design at 4x on its own squares (PPU 1.5)."""
    a = design()
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 元素女皇 奇亚娜：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型（`design/qiyana_designs.png`）：3/4 正面朝右的高傲女王——暖棕皮肤、银白长发、"
      "金王冠和白玉尖冠、青绿抹胸短裙、深色紧身裤，远侧的手握着竖在身边的大圆环刀刃。"
      f"她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽（连圆环）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/qiyana_size.png`：她放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奇亚娜自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她自己的光是金色、带青绿色的宝石点缀**；三种元素——**草丛是绿色的草叶**、"
      "**河流是蓝色的水和冰**、**岩石是琥珀棕色的石块和尘土**；大招三种一起。")
    a("> - **特效要亮**：每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **光、水、草叶、尘土、光环、冲击波都没有黑描边**；**实物**（碎石块、冰晶）有 1 格近黑描边。")
    a("> - **围着人的画面只画外圈、脚下或腰间，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`r_wave`）"
      "**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进她自己帧里的**（`" + "`、`".join(FORWARD) +
      "`）**朝右画，不用对称**（跟着她的身体一起翻转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `qiyana_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/qiyana_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「凌人贵气」 | 挥圆环砍；对每个敌人的第一下额外伤害；武器附了元素时普攻多一点魔法伤害 | `a_hit` · `p_hit` · `w_hit` |")
    a("| 技能 1 = Q「以绪塔尔之锋」 | 圆环往前横扫；附了元素就用掉它：河流定身减速、岩石加伤、草丛伪装加速 | `q_swing` · `q_w` · `q_r` · "
      "`q_g` · `q_hit` · `q_w_hit` · `q_r_hit` · `q_g_hit` · `q_slow` · `q_haste` |")
    a("| 技能 2 = E「天纵之勇」+ W「方圆塑令」 | 突进到敌人身上砍一下，落地给武器附一种元素，刷新 Q | `e_hit` · `w_on` · `el_g` · "
      "`el_w` · `el_r` |")
    a("| 大招「惊才绝景」 | 圆环抡一大圈砸地，冲击波往前推，打中的击退再眩晕 | `r_swing` · `r_burst` · `r_wave` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、水、草叶、尘土、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实物——碎石块、冰晶——有 1 格近黑描边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("她的金光", GOLD), ("宝石青绿（点缀）", TEAL), ("草丛（绿）", GRASS), ("河流（蓝，水和冰）", RIVER),
                        ("岩石（琥珀棕，石块和尘土）", ROCK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面和腰间的圈是从斜上方看的椭圆（宽是高的 3–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 横扫约 34000，大招冲击波 60000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `qiyana_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `qiyana_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_qiyana_fx`（小的）和 `league_qiyana_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_qiyana.py 的 views）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；朝前的（{'、'.join(FORWARD)}）用 tools/fix/bake_caster_fx.py 画进她的帧"
      "（Q 的四种各一份 skill 动作：skill / skill_w / skill_r / skill_g，build_qiyana.py 里的 cview 换成对应的 CasterAnimation）；"
      "其余断言左右对称；w_on、el_*、q_haste 跟随她。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="qiyana_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "qiyana_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    RF.REF, RF.GROUPS = REF, GROUPS
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_qiyana.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "qiyana_designs.png"))
    shape = size_sheet(os.path.join(out, "design", "qiyana_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"qiyana_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(RF.lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(RF.lp(zpath)):
            os.remove(RF.lp(zpath))
        with zipfile.ZipFile(RF.lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(RF.lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
