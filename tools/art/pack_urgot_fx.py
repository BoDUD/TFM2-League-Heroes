#!/usr/bin/env python3
"""Build urgot_fx_pack.zip: step 3 of Urgot's sprite - Codex draws his effects (pack_pantheon_fx.py's way).

    python work/ur/fx_ref_ur.py             # League's particle textures -> %TEMP%/ur_work/fxref (Riot's art, local only)
    python tools/art/pack_urgot_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name urgot_fx_redo_pack]

The pack (%TEMP%/ur_work/fx/urgot_fx_pack, zipped into --out, default dist/urgot_packs) holds PROMPTS.md (also written
to assets/source/urgot/PROMPTS_FX.md), design/urgot_idle.png (his design at 4x), design/urgot_size.png (the 1x idle at
4x on the arena colour with the feet line, a 10-px ruler and the base fighter), design/urgot_shots.png (the finished
action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for Urgot grouped by
the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_urgot.py: view_projectiles a_shot, w_shot, p_fan, q_charge,
r_drill; view_effects a_hit, w_hit, p_hit, q_mark, q_blast, q_hit, e_shield, e_hit, e_fling, r_hit, r_reel, r_ex,
r_fear; view_buffs q_slow, r_leash, w_on, r_flee). The muzzle flashes are already drawn into his own frames
(tools/art/rig_urgot.py). League's colours: his shotgun fire orange-yellow with a white core, the chemicals toxic green
(acid, the drill's glow, the explosions), steel for the canister and the drill; light gets no outline.
Red side: the flying / line pictures (a_shot, w_shot, p_fan, q_charge, r_drill) symmetric top to bottom (they turn with
the flight), every picture on a unit, on him, on the ground and every buff symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ur_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "urgot", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_urgot")
HD = os.path.join(ROOT, "assets", "source", "urgot", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F"      # his shotgun fire: white core, pale yellow to rust
TOXIC = "#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12"     # the chemicals: white-lime core to deep green
STEEL = "#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F"               # the canister, the drill, the barbs
FEAR = "#F4E8FF, #C49BFF, #8A4FE0, #55279E, #2A1150"                # the dread of the execution
DIRT = "#C9A27A, #9A7350, #6B4B33, #3E2A1C"                          # dirt and rubble
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FI = f"a shotgun fire ramp ({FIRE})"
TX = f"a toxic green ramp ({TOXIC})"
ST = f"a steel ramp ({STEEL})"
FE = f"a dread violet ramp ({FEAR})"
DI = f"a dirt ramp ({DIRT})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame (it may be drawn turned either way)"
CENTER = "; centered in every cell."
FIG = "a wide figure 46 squares wide and 42 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack, Purge and Echoing Flames
    ("a_shot", "普攻：霰弹（朝目标飞，循环），3 帧",
     "view_projectiles `league_urgot_a_shot`（朝飞行方向转，画成朝右飞；上下对称）", "12 × 6",
     "炮臂打出去的一团霰弹：几颗亮橙黄色的弹丸挤在一起往右飞，最前面最亮（白芯），后面拖短短的火光尾巴（参考 Z_PierceSpark、Z_BrightSpark、BA_Mis_Air）。**上下对称**。",
     FI,
     f"a SHOTGUN SLUG CLUSTER flying to the RIGHT, 3 frames, a seamless loop, {TB}: 5 bright pellets (2 squares each, white "
     "cores) in a tight wedge pointing right, the front one biggest; short orange-yellow streak tails 4-6 squares behind them, "
     "flickering between frames.",
     row(3, 14, 8) + "; the front pellet 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_shot", "W 净除：机枪子弹（朝目标飞，循环），2 帧",
     "view_projectiles `league_urgot_w_shot`（朝飞行方向转，画成朝右飞；上下对称）", "8 × 3",
     "净除的机枪曳光弹：一道细长的亮黄色光弹，白色弹头在右边（会连续出现很多发，要小）。**上下对称**。",
     FI,
     f"a THIN TRACER BULLET flying to the RIGHT, 2 frames, a seamless loop, {TB}: a white 2-square head at the RIGHT end, a "
     "yellow-to-orange streak 6 squares long behind it, 1 square thick (2 at the head), the streak's length flickering.",
     row(2, 10, 4) + "; vertically centered."),
    ("p_fan", "被动 回响烈焰：腿上霰弹喷出的扇形火焰（一条线，朝目标），4 帧",
     "view_projectiles `league_urgot_p_fan`（扇形那条线的画面：朝目标方向转，画成朝右；上下对称；大图表）", "52 × 24",
     "腿上的霰弹枪喷出一道扇形的火焰：尖端在左边（他的腿），向右张开成一个扇形，里面是一颗颗亮橙黄色的弹丸和火舌，外缘带一点毒绿色的火星（参考 Z_BlastStreaks、Z_BlastShapes、Z_ShockBlasts、Z_PierceSpark）。"
     "**上下对称**。这张图的中心就是扇形线的中点：从格子左边一直到右边。",
     f"{FI} and {TX}",
     f"a SHOTGUN BLAST CONE to the RIGHT, 4 frames, {TB}: 1 a white-yellow flash 6 squares at the LEFT edge (the apex), a few "
     "pellets leaving; 2 a fan of orange-yellow flame streaks and white-cored pellets opening from the apex to 16 squares tall "
     "halfway; 3 the fan reaching the RIGHT edge, 24 squares tall there, pellets scattered over it at mirrored places, a few "
     "toxic green sparks at its outer edges; 4 the fan breaking into fading pellets and sparks near the right end.",
     row(4, 52, 24) + "; the apex in the middle of the LEFT edge, the fan symmetric about the middle row."),
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_urgot_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "霰弹打中：一团橙黄色的弹片火花炸开。**左右对称**。约 10 格。", FI,
     f"a SHOTGUN HIT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 an orange-yellow burst 8 squares with a white core; "
     "3 the burst 10 squares, 6 pellet sparks flying out at mirrored places; 4 fading sparks.",
     row(4, 12, 12) + CENTER),
    ("w_hit", "W 净除：机枪命中（目标身上），3 帧", "view_effects `league_urgot_w_hit`（跟随，画在人物上面；左右对称）", "6",
     "机枪每一发打中：一小点黄色火花（会连续出现很多次，要小）。**左右对称**。约 6 格。", FI,
     f"a TINY BULLET SPARK on a unit, 3 frames, {LR}: 1 a white dot 2 squares; 2 a yellow star 5 squares; 3 4 fading motes.",
     row(3, 8, 8) + CENTER),
    ("p_hit", "被动 回响烈焰：命中（目标身上），4 帧", "view_effects `league_urgot_p_hit`（跟随，画在人物上面；左右对称）", "14",
     "腿上霰弹打中：比普攻大一点的橙黄色爆炸，混着毒绿色的火星（参考 Z_ExplosionFireGreen、Z_FlareOmni）。**左右对称**。约 14 格。",
     f"{FI} and {TX}",
     f"a BLAST HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 an orange-yellow burst 10 squares with a white core; 3 "
     "the burst 14 squares, toxic green sparks and pellet streaks flying out at mirrored places; 4 fading green and orange motes.",
     row(4, 16, 16) + CENTER),
    ("w_on", "W 净除：开火期间脚下（跟随他，循环），4 帧",
     "view_buffs `league_urgot_w_on`（跟随，画在他下面；左右对称）", "48 × 12",
     "净除开火的 4 秒里：他脚下一圈淡淡的橙黄色热浪光圈（扁椭圆），几个弹壳和火星在光圈上跳（参考 W_Aura_Self、P_sparks）。**左右对称**，只画地上的光圈，中间身体位置不画东西，要淡一点。",
     FI,
     f"a FAINT HEAT RING on the ground round a figure, 4 frames, a seamless loop, {LR}: a flat orange-yellow ellipse ring 46 "
     "squares wide and 10 tall, 1-2 squares thick, half transparent-looking (use the darker shades), its brightness running "
     "round; 4 small brass shell casings (2 squares) and sparks hopping on the ring at mirrored places, taking turns.",
     row(4, 48, 12) + "; centered."),
    # ---- Corrosive Charge
    ("q_charge", "Q 腐蚀电荷：飞行中的电荷罐（循环），4 帧",
     "view_projectiles `league_urgot_q_charge`（抛物线飞行；上下左右都对称）", "8 × 8",
     "抛出去的腐蚀电荷：一个钢制的小罐子，中间一圈发亮的毒绿色液体，两头是钢盖，翻滚着飞（参考 Q_Projectile_TX_CM 的罐子）。**上下左右都对称**（每帧可以转 90°）。",
     f"{ST} and {TX}",
     f"a TUMBLING CHEMICAL CANISTER, 4 frames, a seamless loop, {BOTH}: a steel capsule 6 squares long and 4 thick with steel "
     "caps at both ends and a glowing toxic green band in the middle, turned 0, 45, 90 and 135 degrees in the 4 frames, a "
     "faint green glow 1 square round the band.",
     row(4, 10, 10) + CENTER),
    ("q_mark", "Q 腐蚀电荷：落点标记（地上，不跟随，循环），4 帧",
     "view_effects `league_urgot_q_mark`（电荷飞行时画在落点，不跟随，画在人物下面；左右对称）", "42 × 14",
     "电荷还在空中时，地上的落点：一圈毒绿色的警示圆环（扁椭圆），里面几道细细的绿色十字线，闪烁。**左右对称**。",
     TX,
     f"a TOXIC TARGET RING on the ground, 4 frames, a seamless loop, {LR}: a flat toxic green ellipse ring 40 squares wide and 13 "
     "tall, 1 square thick, with 4 short tick marks at its top, bottom, left and right, a faint green cross in its middle; the "
     "ring's brightness pulsing (frames 2-3 brightest).",
     row(4, 42, 14) + "; centered."),
    ("q_blast", "Q 腐蚀电荷：落地后的酸液爆炸（地上，不跟随），7 帧",
     "view_effects `league_urgot_q_blast`（画在落点，不跟随；左右对称；大图表）", "44 × 30",
     "电荷落地：前 3 帧是落在地上的罐子在闪绿光（0.2 秒的引信），然后炸成一团毒绿色的酸液爆炸，地上溅开一圈绿色酸液，飞起几块泥土（参考 Z_ExplosionFireGreen、Q_Acidflicker、Q_DirtChunks、Q_crater、Z_SmokePoofs）。"
     "**左右对称**。爆炸范围约 42 格宽（扁椭圆的地面 + 往上的爆炸）。",
     f"{TX} and {ST} and {DI}",
     f"a CANISTER LANDING THEN AN ACID EXPLOSION, 7 frames, {LR}: 1-3 the small steel canister (6 squares) lying in the middle of "
     "the cell's lower part, its green band blinking brighter each frame; 4 a white-lime flash 12 squares; 5 a toxic green "
     "explosion 30 squares wide and 24 tall rising from the ground, a flat acid splash ellipse 42 wide and 12 tall under it, dirt "
     "chunks thrown out at mirrored places; 6 the explosion breaking into green smoke puffs, the splash ring at full width; 7 "
     "the splash fading, a few green drops and dirt bits.",
     row(7, 44, 30) + "; centered across, the ground ellipse's middle 6 squares above the cell's bottom row."),
    ("q_hit", "Q 腐蚀电荷：命中（目标身上），4 帧", "view_effects `league_urgot_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "被酸液溅到：目标身上溅开一团毒绿色的酸液，几滴往下流（参考 P_fluid、Q_Acidflicker）。**左右对称**。约 14 格。", TX,
     f"an ACID SPLASH on a unit, 4 frames, {LR}: 1 a white-lime flash 4 squares; 2 a toxic green splash 12 squares with lime "
     "highlights; 3 green droplets flying out and dripping down at mirrored places, 14 squares; 4 a few green drips falling.",
     row(4, 16, 16) + CENTER),
    ("q_slow", "Q 腐蚀电荷：减速（目标脚下，跟随，循环），4 帧",
     "view_buffs `league_urgot_q_slow`（跟随，画在人物下面；左右对称）", "20 × 6",
     "被减速时脚下：一小滩冒泡的毒绿色酸液（扁椭圆）。**左右对称**。", TX,
     f"a BUBBLING ACID PUDDLE on the ground, 4 frames, a seamless loop, {LR}: a flat toxic green puddle ellipse 18 squares wide "
     "and 5 tall, darker at its rim, 3-4 lime bubbles rising and popping at mirrored places, taking turns.",
     row(4, 20, 6) + "; centered."),
    # ---- Disdain
    ("e_shield", "E 鄙弃：冲锋时他身上的护盾（跟随），6 帧",
     "view_effects `league_urgot_e_shield`（跟随，画在他身上；左右对称）", "56 × 50",
     "冲锋开始时他获得的护盾：一层钢灰色带毒绿色边光的护甲力场罩住他，从脚下往上合拢，亮一下后变淡（参考 W_Aura_Self、P_GlowingVents）。"
     f"**左右对称**，中间身体位置留空（{FIG}），光要淡一点、不要盖住他。",
     f"{ST} and {TX}",
     f"a STEEL ENERGY SHIELD closing round a wide figure, 6 frames, {LR} ({FIG}): 1 steel-grey light at both sides of the feet; "
     "2 two curved steel-grey plates of light rising at both sides with toxic green edges; 3 the plates meeting above the head "
     "into a dome outline 54 squares wide and 48 tall, a few hex lines on it; 4 the dome brightest, green glints running along "
     "its edge; 5-6 the dome fading to a faint outline.",
     row(6, 58, 52) + "; centered across, the figure's feet on the cell's bottom row."),
    ("e_hit", "E 鄙弃：撞上英雄（目标身上），4 帧", "view_effects `league_urgot_e_hit`（跟随，画在人物上面；左右对称）", "18",
     "冲锋撞上英雄：一团钢灰色和橙色的冲击火花炸开，一圈冲击环，头顶几颗小星星（眩晕）。**左右对称**。约 18 格。",
     f"{ST} and {FI}",
     f"a CRUSHING IMPACT on a unit, 4 frames, {LR}: 1 a white flash 6 squares; 2 a steel-grey and orange burst 14 squares; 3 a "
     "shockwave ring 18 squares across, three small yellow stars in a ring 8 squares above the middle; 4 the ring fading, the "
     "stars turning.",
     row(4, 20, 20) + CENTER),
    ("e_fling", "E 鄙弃：被甩到身后落地（目标身上），5 帧",
     "view_effects `league_urgot_e_fling`（跟随，画在人物上面；左右对称）", "26 × 14",
     "被甩过他头顶、砸在他身后：落地扬起一圈尘土和碎石（扁的），中间一下钢灰色的冲击（参考 Z_SmokePoofs、Q_DirtChunks）。**左右对称**，只画地上的尘土和冲击。",
     f"{DI} and {ST}",
     f"a SLAM INTO THE GROUND under a unit, 5 frames, {LR}: 1 a steel-white flash 8 squares on the ground; 2 a flat dust ring 18 "
     "wide and 6 tall bursting out, pebbles thrown up at mirrored places; 3 the dust 26 wide, two dust clouds at both ends; 4-5 "
     "the dust thinning and settling.",
     row(5, 28, 16) + "; centered across, the ground on the cell's bottom third."),
    # ---- Fear Beyond Death
    ("r_drill", "R 超越死亡的恐惧：化学钻头（朝目标飞，循环），4 帧",
     "view_projectiles `league_urgot_r_drill`（朝飞行方向转，画成朝右飞；上下对称）", "18 × 8",
     "从胸口发射的化学钻头：一个钢制的锥形钻头（尖端朝右），钻头上一圈螺旋纹在转，尾部一颗发光的毒绿色化学球，后面拖一条绿色的光尾（参考 R_Projectile_TX_CM 的钻头和绿球、Z_EnergyStreaksAdd）。**上下对称**。",
     f"{ST} and {TX}",
     f"a CHEM-DRILL flying to the RIGHT, 4 frames, a seamless loop, {TB}: a steel cone drill 10 squares long pointing RIGHT, "
     "its spiral grooves shifting a square each frame (spinning), a glowing toxic green orb 4 squares at its back end, a green "
     "light trail 6 squares behind it, flickering.",
     row(4, 20, 10) + "; the drill's tip 1 square from the RIGHT edge, vertically centered."),
    ("r_hit", "R 超越死亡的恐惧：钻头钉中（目标身上），5 帧", "view_effects `league_urgot_r_hit`（跟随，画在人物上面；左右对称）", "18",
     "钻头钉进英雄：一团毒绿色的化学爆闪，钢灰色的碎屑和火花往外飞。**左右对称**。约 18 格。",
     f"{TX} and {ST}",
     f"a DRILL IMPALING HIT on a unit, 5 frames, {LR}: 1 a white-lime flash 6 squares; 2 a toxic green burst 14 squares; 3 the "
     "burst 18 squares, steel-grey shards and yellow sparks flying out at mirrored places; 4 green smoke wisps; 5 fading motes.",
     row(5, 20, 20) + CENTER),
    ("r_leash", "R：被拴住期间（目标身上，跟随，循环），4 帧",
     "view_buffs `league_urgot_r_leash`（跟随，画在人物上面；左右对称）", "26 × 30",
     "被钻头拴住的 4 秒里：目标身上缠着一圈发光的毒绿色化学锁链（扁椭圆，绕在腰上），胸口一点绿光在跳（像心跳），锁链上的绿光一节一节地流动。**左右对称**，中间身体位置留空（一个约 18 格宽、30 格高的人），要淡一点。",
     f"{TX} and {ST}",
     f"a GLOWING CHEMICAL CHAIN round a figure's waist, 4 frames, a seamless loop, {LR} (an upright figure 18 squares wide and "
     "30 tall stands in the middle, not drawn): a flat ellipse of steel chain links 24 squares wide and 7 tall at the waist "
     "(14 squares above the bottom row), toxic green light running along the links frame by frame; a small green pulse 3 "
     "squares at the chest growing and shrinking.",
     row(4, 26, 30) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_reel", "R：被拽回来（目标身上），4 帧", "view_effects `league_urgot_r_reel`（跟随，画在人物上面；左右对称）", "22 × 30",
     "被拽向厄加特：目标身上一圈毒绿色的牵引光收紧，几道绿色光线往中间收（参考 Z_EnergyStreaksAdd）。**左右对称**，中间身体位置留空，要淡一点。",
     TX,
     f"a TIGHTENING GREEN PULL round a figure, 4 frames, {LR} (an upright figure 18 squares wide and 30 tall stands in the "
     "middle, not drawn): toxic green streaks at both sides converging on the figure, a green ellipse at the waist shrinking "
     "from 22 to 14 squares wide over the frames, lime glints.",
     row(4, 24, 32) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_ex", "R：处决（目标身上），6 帧", "view_effects `league_urgot_r_ex`（跟随，画在人物上面；左右对称；大图表）", "34",
     "处决：目标被拽进来碾碎，一团很大的毒绿色和深紫色的爆炸，中间一颗白色的爆闪，外面一圈紫黑色的冲击环（参考 R_flare-omnimax、Z_ExplosionFireGreen、R_ShockDistortion）。**左右对称**。约 34 格。",
     f"{TX} and {FE}",
     f"an EXECUTION BURST on a unit, 6 frames, {LR}: 1 a white flash 8 squares; 2 a toxic green explosion 22 squares with a "
     "white core; 3 the explosion 30 squares, a violet shockwave ring 34 squares round it; 4 the ring breaking into violet and "
     "green shards at mirrored places; 5 green smoke and violet motes; 6 fading motes.",
     row(6, 36, 36) + CENTER),
    ("r_fear", "R：处决后周围敌人恐惧的冲击波（他身边，跟随），6 帧",
     "view_effects `league_urgot_r_fear`（跟随，画在他下面；左右对称；大图表）", "84 × 30",
     "处决成功：他脚下一圈深紫色带毒绿色的恐惧冲击波（扁椭圆）向外推开，地上几缕紫色的雾往外飘（参考 R_ShockDistortion、Z_SoftClouds）。**左右对称**，只画地上的环和雾。",
     f"{FE} and {TX}",
     f"a DREAD SHOCKWAVE on the ground round a wide figure, 6 frames, {LR}: 1 a violet flash 14 squares on the ground; 2 a flat "
     "violet ellipse ring 36 wide and 12 tall with a bright lavender rim and green sparks; 3 the ring 60 wide; 4 the ring 84 wide, "
     "violet mist wisps drifting outward at mirrored places; 5-6 the ring and the mist fading.",
     row(6, 86, 30) + "; centered across, the ring's middle 8 squares above the cell's bottom row."),
    ("r_flee", "R：恐惧中（敌人头顶，跟随，循环），4 帧",
     "view_buffs `league_urgot_r_flee`（跟随，画在人物上面；左右对称）", "10 × 10",
     "被吓跑的敌人头顶：一个小小的深紫色骷髅幽火在晃，带一点绿光。**左右对称**。", f"{FE} and {TX}",
     f"a TINY DREAD SKULL WISP above a head, 4 frames, a seamless loop, {LR}: a small violet skull 6 squares with two green eye "
     "dots, a lavender flame wisp 3 squares above it flickering, the skull bobbing a square up and down.",
     row(4, 10, 10) + "; centered across, the skull in the cell's lower half."),
]
BIG_FX = ("p_fan", "q_blast", "r_ex", "r_fear")
GROUPS = [
    ("a_shot w_shot a_hit w_hit", ["Urgot_Base_Z_PierceSpark", "Urgot_Base_Z_BrightSpark", "Urgot_Base_BA_Mis_Air",
                                   "Urgot_Base_BA_Rivet", "Urgot_Base_Z_FlareOmni"]),
    ("p_fan p_hit", ["Urgot_Base_Z_BlastStreaks", "Urgot_Base_Z_BlastShapes", "Urgot_Base_Z_ShockBlasts",
                     "Urgot_Base_Passive_Ready_Shapes_4x2", "Urgot_Base_Passive_Ready_Z_Ring_02_Dissolve"]),
    ("w_on", ["Urgot_Base_W_Aura_Self", "Urgot_Base_P_sparks", "Urgot_Base_P_GlowingVents"]),
    ("q_charge q_mark q_blast q_hit q_slow", ["Urgot_Base_Q_Projectile_TX_CM", "Urgot_Base_Z_ExplosionFireGreen",
                                              "Urgot_Base_Q_Acidflicker", "Urgot_Base_Q_DirtChunks", "Urgot_Base_Q_crater",
                                              "Urgot_Base_P_fluid"]),
    ("e_shield e_hit e_fling", ["Urgot_Base_W_Aura_Self", "Urgot_Base_Z_SmokePoofs", "Urgot_Base_Z_SoftClouds"]),
    ("r_drill r_hit r_leash r_reel", ["Urgot_Base_R_Projectile_TX_CM", "Urgot_Base_Z_EnergyStreaksAdd",
                                      "Urgot_Base_Z_cinder", "Urgot_Base_r_Stardust_Mult"]),
    ("r_ex r_fear r_flee", ["Urgot_Base_R_flare-omnimax", "Urgot_Base_R_ShockDistortion", "Urgot_Base_Z_FireMult",
                            "Urgot_Base_Z_SoftCircle"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 2, "a_shot：普攻开火（炮口火光已画进帧）"), ("attack_w", 1, "w_shot：机枪"),
         ("skill", 2, "q_charge：抛出电荷"), ("skill2", 3, "e_hit：撞上英雄"), ("ult", 3, "r_drill：胸口发射钻头")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Urgot_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"厄加特 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连炮臂），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 无畏战车 厄加特：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/urgot_idle.png`：3/4 正面朝右，苍白光头、防毒面具、毒绿软管，"
      f"头顶举着巨大的霰弹炮臂，下面是青铜底盘和六条带盾甲的机械腿）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），"
      f"连炮臂 {h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/urgot_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/urgot_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。**炮口火光已经画进他自己的帧里了，不用再画。**")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里厄加特自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**霰弹的火光是橙黄色（白芯）**，**化学药剂（酸液、钻头的光、爆炸）是毒绿色**，**电荷罐和钻头是钢灰色**，**处决和恐惧带一点深紫色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住人。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_shot`、`w_shot`、`r_drill` 和腿上霰弹的扇形 `p_fan` 画成朝右，**上下对称**（往左时会上下翻）；"
      "电荷罐 `q_charge` 上下左右都对称。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `urgot_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `urgot_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「回响烈焰」 | 炮臂打霰弹；腿上的霰弹枪轮流朝目标喷扇形火焰 | `a_shot` · `a_hit` · `p_fan` · `p_hit` |")
    a("| W「净除」（Q 或 E 打中后自动开 4 秒） | 普攻换成机枪连射 | `w_shot` · `w_hit` · `w_on` |")
    a("| 技能 1 = Q「腐蚀电荷」 | 抛出电荷罐，落地 0.2 秒后炸成酸液，减速 | `q_charge` · `q_mark` · `q_blast` · `q_hit` · `q_slow` |")
    a("| 技能 2 = E「鄙弃」 | 带护盾冲向英雄，撞上后眩晕并甩到身后 | `e_shield` · `e_hit` · `e_fling` |")
    a("| 大招「超越死亡的恐惧」 | 胸口发射化学钻头钉住英雄，4 秒后拽回来处决，处决成功周围敌人恐惧 | `r_drill` · `r_hit` · `r_leash` · `r_reel` · `r_ex` · `r_fear` · `r_flee` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟、火星、酸液、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（电荷罐和钻头例外：钢制的东西可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("霰弹火光", FIRE), ("毒绿化学药剂", TOXIC), ("钢（电荷罐、钻头、锁链）", STEEL), ("深紫恐惧（处决、恐惧）", FEAR),
                        ("泥土", DIRT)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 38000，"
      "腿上霰弹的扇形 52000 长，电荷爆炸半径 21000，恐惧半径 40000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `urgot_fx_{name}.png`：{title}\n")
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
        a(f"| `urgot_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_urgot_fx`（小的）和 `league_urgot_big`（{'、'.join(BIG_FX)}），tag = 名字（build_urgot.py 的 views）。")
    a("- `a_shot`、`w_shot`、`p_fan`、`q_charge`、`r_drill` 是投射物，画面朝方向转；`q_mark`、`q_blast` 不跟随；`q_mark`、`r_fear`、`q_slow`、`w_on` 画在人物下面（z -1）；"
      "`q_blast` 前 3 帧（引信）要盖满 q_apply 的 0.2 秒。")
    a("- 用 `pixel_1x/` 切格（import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="urgot_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "urgot_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/ur/fx_ref_ur.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 4, 0), 4, 1)).save(os.path.join(out, "design", "urgot_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "urgot_size.png"))
    shots_sheet(os.path.join(out, "design", "urgot_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"urgot_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
