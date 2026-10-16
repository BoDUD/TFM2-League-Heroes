#!/usr/bin/env python3
"""Build pantheon_fx_pack.zip: step 3 of Pantheon's sprite - Codex draws his effects (pack_kalista_fx.py's way).

    python work/pn/fx_ref_pn.py pn          # League's particle textures -> %TEMP%/pn_work/fxref (Riot's art, local only)
    python tools/art/pack_pantheon_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name pantheon_fx_redo_pack]

The pack (%TEMP%/pn_work/fx/pantheon_fx_pack, zipped into --out, default dist/pantheon_packs) holds PROMPTS.md (also
written to assets/source/pantheon/PROMPTS_FX.md), design/pantheon_idle.png (his design at 4x), design/pantheon_size.png
(the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter), design/pantheon_shots.png
(the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for
Pantheon grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_pantheon.py: view_projectiles q_spear, q_thrust; view_effects
a_hit, p_ready, q_hit, w_hit, e_shield, e_stab, e_bash, e_hit, r_cast, r_mark, r_spear, r_sp_hit, r_land, r_hit and the
add-on's q_low; view_buffs r_slow, e_def). League's colours: his spear and shield's light gold to orange with a white
core, the comet's trail and his cape's deep blue-violet nebula with white stars, the landing's orange blast with rocks
and dust; light gets no outline.
Red side: the flying / line pictures (q_spear, q_thrust) symmetric top to bottom (they turn with the flight), every
picture on a unit, on him, on the ground and every buff symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "pn_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "pantheon", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_pantheon")
HD = os.path.join(ROOT, "assets", "source", "pantheon", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF6C8, #FFE066, #FFB627, #F07A12, #A4440B"      # his comet light: white core, pale gold to deep orange
COSMIC = "#FFFFFF, #C9D2FF, #7C83F0, #4A3FB5, #2B1F72, #160F3D"    # the nebula: white stars, lavender to deep blue-violet
FIRE = "#FFFFFF, #FFE9A8, #FFB13B, #F2581A, #B0280F, #5A1408"      # the landing blast
EARTH = "#E8DCC4, #C2AC88, #96805F, #6B5843, #463A2E"               # dust and rocks of the landing
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, fire, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"a golden comet ramp ({GOLD})"
CO = f"a cosmic nebula ramp ({COSMIC})"
FI = f"a fire blast ramp ({FIRE})"
ER = f"an earth ramp ({EARTH})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
FIG = "an upright figure 18 squares wide and 46 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- Comet Spear
    ("q_spear", "Q 贯星长枪：投出去的彗星长矛（朝目标飞，循环），4 帧",
     "view_projectiles `league_pantheon_q_spear`（朝飞行方向转，画成朝右飞；上下对称）", "30 × 10",
     "投出去的长矛化成一颗彗星：一支金色长矛（矛头在右边、又宽又亮，包在白金色的光里），后面拖一条金橙色的彗尾，彗尾外层是深蓝紫色的星云和几颗白色小星星"
     "（参考 Q_Mis_Air_Trail、Q_Mis_Cosmic_Trail、Q_Nebula_Streak、Q_Stardust、Q_Throw_Sparks）。**上下对称**。",
     f"{GO} and {CO}",
     f"a COMET SPEAR flying to the RIGHT, 4 frames, a seamless loop, {TB}: a golden spear 16 squares long and 1 square thick, its "
     "broad leaf blade 4 squares long wrapped in a white-gold glow 6 squares across at its RIGHT end; behind it a tapering "
     "gold-to-orange comet tail 12 squares long, outside it a thin deep blue-violet nebula haze with 3-4 tiny white stars at "
     "mirrored places, flickering between frames.",
     row(4, 32, 12) + "; the glow's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_thrust", "Q 贯星长枪：近戳的突刺光（一条线，朝目标），4 帧",
     "view_projectiles `league_pantheon_q_thrust`（突刺那条线的画面：朝目标方向转，画成朝右；上下对称；大图表）", "48 × 10",
     "近戳：一道金色的长矛突刺光从左往右刺出去，尖端在右边最亮，像一道金色的光枪，周围几缕金光和火星（参考 Q_tap_SpearHead_Blur、Q_Side_Trails、Q_Air_Trail）。**上下对称**。"
     "这张图的中心就是突刺线的中点：光从格子左边一直到右边。",
     GO,
     f"a GOLDEN SPEAR THRUST along a line to the RIGHT, 4 frames, {TB}: 1 a thin white-gold streak 20 squares long from the LEFT "
     "edge; 2 the streak shooting the whole 48 squares to a bright pointed spearhead of light 6 squares tall at the RIGHT end, gold "
     "side streaks 4 squares above and below it; 3 the same brightest with sparks flying off at mirrored places; 4 fading gold "
     "motes along the line.",
     row(4, 48, 10) + "; the line through the middle row of every cell."),
    ("q_hit", "Q 命中（目标身上），5 帧", "view_effects `league_pantheon_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "贯星长枪命中：一团金白色的闪光炸开，一颗四角星光闪一下，几道金色光线和火星往外射（参考 Q_Cross_Stars、Q_Glow02、Q_Throw_Sparks）。**左右对称**。约 16 格。",
     GO,
     f"a GOLDEN SPEAR IMPACT on a unit, 5 frames, {LR}: 1 a white flash 4 squares; 2 a gold burst 10 squares with a white core; 3 a "
     "four-pointed white-gold star 16 squares across over the burst, 8 short gold rays at mirrored places; 4 the star fading, gold "
     "sparks flying out; 5 fading motes.",
     row(5, 18, 18) + CENTER),
    ("q_low", "Q 斩杀（附加包：目标残血时，目标身上），5 帧", "view_effects `league_pantheon_q_low`（跟随，画在人物上面；左右对称）", "22",
     "附加包的贯星长枪斩杀：比普通命中更大更猛的金橙色爆闪，中间一颗大的白色十字星，外面一圈金色冲击环和星云色的碎光。**左右对称**。约 22 格。",
     f"{GO} and {CO}",
     f"a CRUSHING GOLDEN CRIT on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 a gold-orange burst 14 squares with a white "
     "core; 3 a big white four-pointed star 22 squares across, a gold shockwave ring 18 squares round it; 4 the ring breaking into gold "
     "and blue-violet sparks at mirrored places; 5 fading motes.",
     row(5, 24, 24) + CENTER),
    # ---- the attack and Mortal Will
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_pantheon_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "长矛刺中：一小团金色闪光和几颗火星（参考 Q_Throw_Sparks）。**左右对称**。约 10 格。", GO,
     f"a SMALL GOLDEN HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a gold flash 7 squares with a white core; 3 the "
     "flash 10 squares, 6 short gold sparks at mirrored places; 4 a few fading gold motes.",
     row(4, 12, 12) + CENTER),
    ("p_ready", "被动 矢志不退满层（他身上，跟随），5 帧", "view_effects `league_pantheon_p_ready`（跟随，画在他身上；左右对称）", "30 × 50",
     "被动满 5 层：他全身腾起一圈金橙色的战意火光，从脚下往上烧到头顶，几颗金色火星往上飘（参考 P_Enrage_Flare、P_Weapons_Glow、Aura_Self）。"
     f"**左右对称**，中间身体位置留空（{FIG}）。",
     GO,
     f"a BATTLE FLARE rising round a figure, 5 frames, {LR} ({FIG}): 1 gold light at both sides of the feet; 2 gold-orange "
     "flame tongues rising at both sides up to the waist; 3 the flames up past the head, a crown of gold flame spikes above it, "
     "brightest; 4 the flames thinning, gold sparks drifting up; 5 the last sparks.",
     row(5, 32, 52) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- Shield Vault
    ("w_hit", "W 斗盾跃击：盾砸中（目标身上），5 帧", "view_effects `league_pantheon_w_hit`（跟随，画在人物上面；左右对称）", "20",
     "盾砸下来：目标身上一团金色的冲击爆开，一圈金色冲击环，头顶几颗金色小星星转一圈（晕眩）（参考 W_Flare、W_Air_swoosh、W_Smoke）。**左右对称**。约 20 格。",
     GO,
     f"a SHIELD SLAM IMPACT on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 a gold burst 14 squares with a white core; 3 a "
     "gold shockwave ring 20 squares across, three small gold stars in a ring 8 squares above the middle; 4 the ring fading, the "
     "stars turning; 5 the stars and a few motes.",
     row(5, 22, 22) + CENTER),
    # ---- Aegis Assault
    ("e_shield", "E 神佑枪阵：举盾时他身上的神盾光（跟随，循环），6 帧", "view_effects `league_pantheon_e_shield`（跟随，画在他身上；左右对称；大图表）", "44 × 52",
     "举盾 1.5 秒：他身前身后一圈金色的神光，脚下一圈发光的金色光环，几道竖直的金色星芒从地面往上射，几颗金色小星星绕着他转（参考 E_Ground_Light、E_Star_Rays、E_Shield_Plane_Mult、Shield_Nebula）。"
     f"**左右对称**，中间身体位置留空（{FIG}），光要淡一点、不要盖住他。",
     f"{GO} and {CO}",
     f"a HOLY SHIELD GLOW round a figure, 6 frames, a seamless loop, {LR} ({FIG}): a glowing gold ground ellipse 40 squares wide "
     "and 10 tall under the feet; 6 thin vertical gold star rays rising from the ellipse at mirrored places, 20-40 squares tall, "
     "taking turns to brighten; a faint gold outline glow round the figure 26 wide and 50 tall; 4 small white-gold stars "
     "circling at mirrored places, a few blue-violet nebula motes.",
     row(6, 46, 54) + "; centered across, the ground ellipse's middle 4 squares above the cell's bottom row."),
    ("e_stab", "E 神佑枪阵：连刺命中（目标身上），3 帧", "view_effects `league_pantheon_e_stab`（跟随，画在人物上面；左右对称）", "8",
     "举盾连刺的每一下：一小点金色火花。**左右对称**。约 8 格（会连续出现很多次，要小）。", GO,
     f"a TINY GOLDEN SPARK on a unit, 3 frames, {LR}: 1 a white dot 2 squares; 2 a gold star 6 squares; 3 4 fading gold motes.",
     row(3, 10, 10) + CENTER),
    ("e_bash", "E 神佑枪阵：盾击的冲击波（地上，不跟随），5 帧", "view_effects `league_pantheon_e_bash`（不跟随，画在他身上；左右对称；大图表）", "48 × 22",
     "盾击：他脚下一圈金色的冲击波（扁椭圆）向外推开，地上扬起两团尘土（参考 E_Shield_Erode_Out、W_Smoke）。**左右对称**，只画地上的环和尘土。",
     f"{GO} and {ER}",
     f"a GOLDEN SHOCKWAVE on the ground, 5 frames, {LR}: 1 a white flash 8 squares on the ground; 2 a flat gold ring 24 wide and 7 "
     "tall with a bright white-gold rim; 3 the ring 40 wide, dust puffs kicked out at both ends; 4 the ring 48 wide and fading, the "
     "dust settling; 5 the last arcs.",
     row(5, 50, 24) + "; centered across, the ring's middle 5 squares above the cell's bottom row."),
    ("e_hit", "E 盾击命中（目标身上），4 帧", "view_effects `league_pantheon_e_hit`（跟随，画在人物上面；左右对称）", "16",
     "盾击命中：一团金色冲击和几道往外的金色光线。**左右对称**。约 16 格。", GO,
     f"a SHIELD BASH IMPACT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 a gold burst 12 squares with a white core; 3 the "
     "burst 16 squares with 8 gold rays at mirrored places; 4 fading motes.",
     row(4, 18, 18) + CENTER),
    # ---- Grand Starfall
    ("r_cast", "大招 大荒星陨：蓄力（他身上，跟随），6 帧", "view_effects `league_pantheon_r_cast`（跟随，画在他身上；左右对称；大图表）", "40 × 56",
     "大招蓄力 1 秒：他蹲下蓄力，周围的空气里聚起金橙色的光和深蓝紫色的星云，光点从四周往他身上收，头顶上方的星空越来越亮（参考 R_Nova_Mult、Kassadin_StarryBackdrop、Cape_Nebula、Q_Stardust）。"
     f"**左右对称**，中间身体位置留空（{FIG}）。",
     f"{GO} and {CO}",
     f"a STAR-POWER GATHERING round a figure, 6 frames, {LR} ({FIG}): 1 a faint blue-violet nebula haze at both sides; 2 gold and "
     "white star motes drifting in toward the figure from both sides; 3 a gold glow outline round the figure 28 wide and 52 tall, "
     "the nebula above the head brightening with white stars; 4 the motes streaming in faster, brightest; 5 a column of gold light "
     "8 squares wide rising above the head; 6 the column at full height, the motes gone.",
     row(6, 42, 58) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_mark", "大招：落点警示圈（地上，不跟随），6 帧", "view_effects `league_pantheon_r_mark`（不跟随，画在地上、人物下面；左右对称；大图表）", "64 × 20",
     "落点：地上一个大的金橙色椭圆圈，圈里一颗彗星落点的十字准心，从淡到亮一闪一闪（英雄联盟落点指示的样子）。**左右对称**，整个圈要大、要明显，但只是一圈线，中间是空的。",
     GO,
     f"a TARGET RING on the ground, 6 frames, {LR}: a flat gold-orange ellipse ring 64 squares wide and 20 tall, 1 square thick, with "
     "a thin inner ring 40 wide and four short tick marks pointing in at mirrored places; frames 1-2 faint, 3-4 bright with a white "
     "rim, 5-6 brightest and pulsing; the middle empty.",
     row(6, 66, 22) + CENTER),
    ("r_spear", "大招：从天而降的长矛（地上，不跟随），5 帧", "view_effects `league_pantheon_r_spear`（不跟随；左右对称；大图表）", "20 × 70",
     "长矛先砸下来：一支金色长矛从天上竖直往下落，矛头朝下，后面拖一条金橙色的火光，插进地面的那一刻炸出一团金光（参考 R_Mis_Trail、R_Comet_Streaks_Mult、Pantheon_R_Spear_Impact）。"
     "**左右对称**：矛竖直、在格子正中，矛头落点在格子底部。",
     f"{GO} and {FI}",
     f"a SPEAR FALLING FROM THE SKY, 5 frames, {LR}: 1 a golden spear 30 squares long pointing DOWN in the middle column near the "
     "cell's top, a gold-orange fire trail 20 squares above it; 2 the spear halfway down; 3 the spear's point driving into the ground "
     "at the cell's bottom, a white-gold flash 16 squares wide; 4 the spear stuck upright in the ground, a gold burst 20 squares wide "
     "round its foot; 5 the burst fading, the spear fading.",
     row(5, 22, 72) + "; the spear in the middle column of every cell, its point landing on the cell's bottom row."),
    ("r_sp_hit", "大招：长矛砸中（目标身上），4 帧", "view_effects `league_pantheon_r_sp_hit`（跟随，画在人物上面；左右对称）", "14",
     "长矛砸中：一团金橙色的冲击（白芯）。**左右对称**。约 14 格。", FI,
     f"a FIERY HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 an orange-gold burst 10 squares with a white core; 3 the "
     "burst 14 squares with 6 short orange rays at mirrored places; 4 fading embers.",
     row(4, 16, 16) + CENTER),
    ("r_land", "大招：落地爆炸（地上，不跟随），7 帧", "view_effects `league_pantheon_r_land`（不跟随，地上；左右对称；大图表）", "70 × 44",
     "像一颗彗星砸到地上：一团巨大的金橙色火球往上炸开（白芯），地上一圈冲击波向外推，地面裂开、石块往两边飞，外面一层深蓝紫色的星云烟（参考 R_Nova_Mult、R_ground_crack_03、R_GroundCracks_Glow、R_Rocks_2X2、R_OilySmoke、R_Comet_Impact_Smoke）。**左右对称**。",
     f"{FI}, {CO} and {ER}",
     f"a COMET IMPACT on the ground, 7 frames, {LR}: 1 a white flash 10 squares on the ground; 2 an orange-gold fireball 24 squares "
     "wide rising 24 squares with a white core, a flat ground ring 30 wide and 8 tall; 3 the fireball 34 wide and 36 tall, the ring "
     "50 wide, glowing ground cracks spreading at mirrored places, rocks thrown out at both sides; 4 the ring 66 wide, the fireball "
     "breaking into fire and blue-violet nebula smoke; 5 the smoke spreading, embers rising, rocks falling; 6 the smoke thinning, the "
     "cracks still glowing; 7 faint cracks and a few embers.",
     row(7, 72, 46) + "; centered across, the ground ring's middle 6 squares above the cell's bottom row."),
    ("r_hit", "大招：落地命中（目标身上），4 帧", "view_effects `league_pantheon_r_hit`（跟随，画在人物上面；左右对称）", "18",
     "落地冲击打中：一团金橙色火光和几道往外的火线。**左右对称**。约 18 格。", FI,
     f"a BLAST HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 an orange burst 12 squares with a white core; 3 the burst "
     "18 squares with 8 fiery rays at mirrored places; 4 fading embers.",
     row(4, 20, 20) + CENTER),
    # ---- buffs
    ("r_slow", "大招减速（敌人脚下，循环），4 帧", "view_buffs `league_pantheon_r_slow`（跟随，画在人物下面；左右对称）", "16 × 5",
     "被长矛砸中减速：敌人脚下一圈淡淡的金橙色裂纹光环，几点火星轮流亮。**左右对称**。", FI,
     f"a FAINT EMBER RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 14 squares wide and 4 tall "
     "in dim orange, 4 brighter embers on it at mirrored places taking turns to light up.",
     row(4, 16, 6) + CENTER),
    ("e_def", "E 强化：护甲加成（他身上，循环），4 帧", "view_buffs `league_pantheon_e_def`（跟随，画在他身上；左右对称）", "26 × 48",
     "强化神佑枪阵后的双抗加成：他身上一层淡淡的金色光边，几颗金色小星星在身边一闪一闪。**左右对称**，中间身体留空，要淡，不要盖住他。",
     GO,
     f"a FAINT GOLDEN GUARD round a figure, 4 frames, a seamless loop, {LR} ({FIG}): a thin dotted gold outline 24 wide and 48 tall, "
     "4 small white-gold stars at mirrored places taking turns to twinkle.",
     row(4, 28, 50) + "; centered across, the figure's feet on the cell's bottom row."),
]

GROUPS = [
    ("q_spear q_thrust", ["Pantheon_Base_Q_Mis_Air_Trail", "Pantheon_Base_Q_Mis_Cosmic_Trail", "Pantheon_Base_Q_Nebula_Streak_Mult",
                          "Pantheon_Base_Q_tap_SpearHead_Blur", "Pantheon_Base_Q_Side_Trails", "Pantheon_Base_Q_Throw_Sparks"]),
    ("q_hit q_low a_hit p_ready", ["Pantheon_Base_Q_Cross_Stars", "Pantheon_Base_Q_Glow02", "Pantheon_Base_Q_Stardust",
                                   "Pantheon_Base_P_Enrage_Flare", "Pantheon_Base_P_Weapons_Glow", "Aura_Self"]),
    ("w_hit e_*", ["Pantheon_Base_W_Flare", "Pantheon_Base_W_Air_swoosh", "Pantheon_Base_W_Smoke",
                   "Pantheon_Base_E_Ground_Light", "Pantheon_Base_E_Star_Rays", "Pantheon_Base_Shield_Nebula"]),
    ("r_cast r_spear", ["Pantheon_Base_R_Nova_Mult", "Kassadin_Skin05_I_StarryBackdrop", "Pantheon_Base_Cape_Nebula",
                        "Pantheon_Base_R_Mis_Trail", "Pantheon_Base_R_Comet_Streaks_Mult", "Pantheon_R_Spear_Impact_Diust_burst"]),
    ("r_land r_hit", ["Pantheon_Base_R_ground_crack_03", "Pantheon_Base_R_GroundCracks_Glow", "Pantheon_Base_R_Rocks_2X2",
                      "Pantheon_Base_R_OilySmoke_2x2", "Base_Pantheon_R_Comet_Impact_Smoke", "Pantheon_Base_R_Crack_Dissolve"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("skill", 3, "q_thrust：近戳出手"), ("skill_throw", 4, "q_spear：投矛出手"), ("skill2", 5, "w_hit：盾砸下"),
         ("e_hold", 2, "e_shield：举盾连刺"), ("e_bash", 3, "e_bash：盾击"), ("ult", 4, "r_cast：蓄力"),
         ("ult_land", 2, "r_land：落地")]


def ref_sheet(path):
    S, LW = 180, 170
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
            d.text((LW + c * S + 4, y + 2), nm.replace("Pantheon_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    img = Image.new("RGBA", (W * Z, (pad + top + 4) * Z + 64), (104, 112, 72, 255))
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
    d.text((8, 36), f"潘森 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连长矛和冠饰），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 260), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
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


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 不屈之枪 潘森：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/pantheon_idle.png`：3/4 正面朝右，金色全脸头盔、弯月冠饰，近侧手低握金色长矛，"
      f"远侧手臂挎大金圆盾，深蓝披风）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连长矛和冠饰 {h} 格高、{w} 格宽；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/pantheon_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/pantheon_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里潘森自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**长矛、盾和战意的光是金色到橙色（白芯）**，**彗星的尾巴和他披风里的星空是深蓝紫色的星云、带白色小星星**，**大招落地是金橙色的火光、石块和尘土**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住他。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `q_spear` 和近戳的 `q_thrust` 画成朝右，**上下对称**（往左时会上下翻）。"
      "其余所有画面（打中、身上、脚下、地上、天上落下的矛）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）——天降的长矛竖直，不要画成斜的。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `pantheon_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `pantheon_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「矢志不退」 | 长矛突刺；满 5 层时下一个技能强化 | `a_hit` · `p_ready` |")
    a("| 技能 1 = Q「贯星长枪」 | 近处向前突刺，远处投出长矛；附加包：残血目标伤害翻倍 | `q_thrust` · `q_spear` · `q_hit` · `q_low` |")
    a("| 技能 2 = W「斗盾跃击」+ E「神佑枪阵」 | W 跳到敌人身上用盾砸晕；E 举盾挡伤害、连刺，最后盾击 | `w_hit` · `e_shield` · `e_stab` · `e_bash` · `e_hit` · `e_def` |")
    a("| 大招「大荒星陨」 | 蓄力后跃上天空，长矛先砸下，再像彗星一样落地 | `r_cast` · `r_mark` · `r_spear` · `r_sp_hit` · `r_land` · `r_hit` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟、火星、星星、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（长矛例外：金色的矛身可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("彗星金（长矛、盾、战意的光）", GOLD), ("星云（彗尾、星空、烟）", COSMIC), ("火光（大招的长矛和落地）", FIRE),
                        ("土石（大招落地的尘土、石块、裂缝）", EARTH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 27000，"
      "近戳 48000 长，大招落地半径 32000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `pantheon_fx_{name}.png`：{title}\n")
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
        a(f"| `pantheon_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_pantheon_fx`（小的）和 `league_pantheon_big`（q_thrust、e_shield、e_bash、r_cast、r_mark、r_spear、r_land），tag = 名字（build_pantheon.py 的 views）。")
    a("- `q_spear`、`q_thrust` 是投射物，画面朝方向转；`e_bash`、`r_mark`、`r_spear`、`r_land` 不跟随；`r_mark`、`e_bash`、`r_land` 画在人物下面（z -1）；`e_shield` 要盖满举盾 1.5 秒（6 帧循环 x 250 ms）。")
    a("- 用 `pixel_1x/` 切格（import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="pantheon_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "pantheon_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/pn/fx_ref_pn.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 4, 0), 4, 1)).save(os.path.join(out, "design", "pantheon_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "pantheon_size.png"))
    shots_sheet(os.path.join(out, "design", "pantheon_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"pantheon_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
