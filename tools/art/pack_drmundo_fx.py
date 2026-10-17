#!/usr/bin/env python3
"""Build drmundo_fx_pack.zip: step 3 of Dr. Mundo's sprite - Codex draws his effects (pack_kalista_fx.py's way).

    python tools/art/pack_drmundo_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name drmundo_fx_redo_pack]

The pack (%TEMP%/md_work/fx/drmundo_fx_pack, zipped into --out, default dist/drmundo_packs) holds PROMPTS.md (also
written to assets/source/drmundo/PROMPTS_FX.md), design/drmundo_idle.png (his dense design at 3x),
design/drmundo_saw.png (the design's bone saw at 8x: the Bonesaw's picture is this saw spinning),
design/drmundo_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/drmundo_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Dr. Mundo grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/md_work/fxref, read out of DrMundo.wad.client's base-skin particle paths).
The effects are the views the kit binds (tools/kit/build_drmundo.py: view_projectiles q_saw, e_fling, p_tank;
view_effects a_hit, e_hit, e_fling_hit, q_hit, q_heal, w_start, w_zap, w_burst, w_end_hit, r_cast, p_shake, p_land,
p_pick, p_break; view_buffs q_slow, w_on, r_on).
Colours: his chemicals a toxic green (the Bonesaw's trail, the tank, the dose), Heart Zapper an electric cyan, the
blows white-hot with a warm edge; light gets no outline.
Red side: the flying pictures spin or tumble (q_saw, e_fling: right either way up); the tank on the ground turns with
its zone, (1, 0) or (-1, 0), so it looks the same turned half round; every other picture symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "md_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "drmundo", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_drmundo")
HD = os.path.join(ROOT, "assets", "source", "drmundo", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


CHEM = "#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220"     # his chemicals: white-lime core to deep toxic green
ZAP = "#FFFFFF, #E0FDFF, #8CEBFF, #38C2F5, #1C78C8, #0F3A78"      # Heart Zapper: white core, electric cyan to deep blue
HOT = "#FFFFFF, #FFF4CF, #FFD27A, #FF9A3C, #D85A20"               # the blows: white-hot with a warm edge
STEEL = "#F2FAFA, #C4D8D8, #8FA6AA, #5C6E74, #2E3A40"            # the saw's steel, the tank's glass and metal
DUST = "#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39"             # dust where things land
PINK = "#FFE0F2, #FF7CC8, #F0309A, #A8166A"                      # his gems' pink, a few sparks in the dose
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
CH = f"a toxic chemical green ramp ({CHEM})"
ZP = f"an electric cyan ramp ({ZAP})"
HT = f"a white-hot impact ramp ({HOT})"
ST = f"a steel ramp ({STEEL})"
DU = f"an earth-dust ramp ({DUST})"
PK = f"a pink ramp ({PINK})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
HALF = ("POINT-SYMMETRIC in every frame: it looks EXACTLY the same turned half round (180 degrees) about the cell's centre "
        "(the game turns it upside down on the red side)")
CENTER = "; centered in every cell."
FEET = "; centered across, the figure's feet on the cell's bottom row."

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- Q Infected Bonesaw
    ("q_saw", "Q 病毒屠刀：飞出去的骨锯（朝目标飞，循环），4 帧",
     "view_projectiles `league_drmundo_q_saw`（朝飞行方向转；它在转，倒过来也一样）", "20 × 20",
     "扔出去的骨锯：就是他手里那把（`design/drmundo_saw.png`：钢青刀身、下缘大锯齿、锈橙刀背、青蓝刀箍），**整把在空中打转**，"
     "4 帧各转 90°，后面拖一圈绿色的化学残影 / 液滴（参考 Q_Trail、Q_Bonesaw_Glow、Q_OilySmoke）。",
     f"{ST}, {CH} and the saw's own rusty orange and teal",
     "his BONE SAW (the attached saw picture: teal-steel blade, a row of big saw teeth on one edge, a rusty orange back, a teal "
     "band at the grip) SPINNING in flight, 4 frames, a seamless loop: the whole saw turned 90 degrees further each frame round "
     "its middle, 16 squares long; a curved smear of toxic green light and a few green droplets trailing the turning blade.",
     row(4, 22, 22) + CENTER),
    ("q_hit", "Q 骨锯命中（目标身上），5 帧", "view_effects `league_drmundo_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "骨锯砍中：一道白热的交叉斩痕一闪，绿色的化学液体往两边溅开（参考 Q_Spear_Impact_Diust_burst、Q_OilySmoke、Droplets）。**左右对称**。约 16 格。",
     f"{HT} and {CH}",
     f"a SAW HIT on a unit, 5 frames, {LR}: 1 a white flash 4 squares; 2 an X of two white-hot slash lines 12 squares across with a "
     "white core; 3 the X fading, toxic green goo bursting out to both sides 16 squares wide in mirrored splashes; 4 green droplets "
     "flying out and falling; 5 a few fading green drops.",
     row(5, 18, 18) + CENTER),
    ("q_heal", "Q 打中回血（他身上），4 帧", "view_effects `league_drmundo_q_heal`（跟随，画在他身上；左右对称）", "14 × 20",
     "打中回血：他身边几个绿色的「+」和光点往上飘。**左右对称**，中间他的身体位置留空（只画两边和头顶）。",
     CH,
     f"HEALING PLUSES rising round a figure, 4 frames, {LR}, the middle EMPTY (a clear area 10 squares wide where he stands): "
     "1 two small green plus signs at his sides at waist height; 2 the pluses 3 squares bigger, rising 4 squares, two more "
     "motes; 3 rising to his shoulders, a small plus over his head; 4 fading up.",
     row(4, 16, 22) + FEET),
    ("q_slow", "Q 减速（敌人脚下，循环），4 帧", "view_buffs `league_drmundo_q_slow`（跟随，画在人物下面；左右对称）", "16 × 5",
     "被骨锯减速：敌人脚下一摊冒泡的绿色化学黏液（扁椭圆），几个小泡轮流冒起来。**左右对称**。", CH,
     f"a TOXIC GOO PUDDLE under a figure's feet, 4 frames, a seamless loop, {LR}: a flat ellipse of green goo 14 squares wide and "
     "4 tall, a lighter rim; small bubbles at mirrored places taking turns to swell and pop.",
     row(4, 16, 6) + CENTER),
    # ---- attack and E Blunt Force Trauma
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_drmundo_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "骨锯劈中：一小团白热的冲击闪光，几道短光线往外射。**左右对称**。约 10 格。", HT,
     f"a SMALL CHOP HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a white-hot flash 7 squares with a white core; 3 the "
     "flash 10 squares, 6 short warm rays at mirrored places; 4 a few fading warm sparks.",
     row(4, 12, 12) + CENTER),
    ("e_hit", "E 大力行医：药箱砸中（目标身上），5 帧", "view_effects `league_drmundo_e_hit`（跟随，画在人物上面；左右对称）", "20",
     "药箱砸中：一个大大的白热冲击星（四角星）+ 一圈冲击环炸开，几颗绿色药丸 / 碎片和星星往外飞（参考 Q_Rocks、Wukong_Base_Sparkles、Dr_Mundo_Base_E_BuffDrips）。**左右对称**。约 20 格。",
     f"{HT} and {CH}",
     f"a HEAVY BASH on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 a four-pointed white-hot impact star 16 squares with a "
     "white core; 3 the star and a warm shock ring 20 squares across, small green pill-shaped bits and white stars flying out at "
     "mirrored places; 4 the ring fading, the bits further out; 5 fading sparks.",
     row(5, 22, 22) + CENTER),
    ("e_fling", "E 打飞的尸体（朝后方飞，循环），4 帧", "view_projectiles `league_drmundo_e_fling`（朝飞行方向转；它在翻滚，倒过来也一样）", "12 × 10",
     "被药箱打飞的小兵尸体：一团软塌塌的深灰紫色小身体在空中翻滚，4 帧各转 90°，后面拖两三道白色的速度线（参考 Sion_Skin05_Sl_Dust、Q_Smoke）。不用画清楚是哪种小兵。",
     f"{DU}, a dark grey-purple body ramp (#B8A8C8, #7A6890, #4C3E60, #2A2038) and white speed lines",
     "a LIMP SMALL BODY TUMBLING through the air, 4 frames, a seamless loop: a vague dark grey-purple rag-doll shape 9 squares "
     "long (a round head, a lump of a body, two floppy limbs), turned 90 degrees further each frame round its middle; three short "
     "white speed lines behind it and a puff of dust at its tail.",
     row(4, 14, 12) + CENTER),
    ("e_fling_hit", "E 尸体撞到敌人（目标身上），4 帧", "view_effects `league_drmundo_e_fling_hit`（跟随，画在人物上面；左右对称）", "14",
     "尸体撞中：一团土黄色的撞击尘土炸开，中间一下白光。**左右对称**。约 14 格。", f"{DU} and {HT}",
     f"a THUD on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a puff of dust 10 squares with a white-hot core; 3 the dust "
     "14 squares, clods flying out at mirrored places; 4 settling dust.",
     row(4, 16, 16) + CENTER),
    # ---- W Heart Zapper
    ("w_on", "W 电击疗法：开着的电流光环（他身上，循环），4 帧",
     "view_buffs `league_drmundo_w_on`（跟随，画在他下面一层；左右对称；大图表）", "44 × 30",
     "电击疗法开着时：他身边一圈噼啪作响的青蓝色电流——腰部一圈扁扁的电光椭圆，几道小闪电从肩上（电极）往下跳到椭圆上，4 帧闪电位置轮流变（参考 P_Lightning03、W_LightningErosion03）。"
     "**左右对称**（闪电可以左右对称地成对出现），中间他的身体位置留空。",
     ZP,
     f"a CRACKLING ELECTRIC AURA round a big figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear area 28 squares wide "
     "and 30 tall where he stands): a flat crackling ring of cyan electricity 44 squares wide and 10 tall round his waist; small "
     "jagged cyan-white bolts jumping down from his shoulders (16 squares above the ring, both sides, mirrored) to the ring, in "
     "different places each frame; a few blue sparks.",
     row(4, 46, 34) + FEET),
    ("w_start", "W 开启：心脏电击（他身上，不跟随），4 帧",
     "view_effects `league_drmundo_w_start`（跟随，画在他身上；左右对称；大图表）", "32 × 30",
     "开启电击疗法：他两边肩头（电极）各炸出一团青白色的电火花，两道电弧往胸口汇合，一闪（参考 P_Capacitor_Erode、P_Ray_Mult）。**左右对称**，中间身体留空（只画两肩和胸前的电弧）。",
     ZP,
     f"a HEART SHOCK on a big figure, 4 frames, {LR} (a figure 28 squares wide and 30 tall in the middle, not drawn - only the "
     "sparks on him): 1 two cyan-white sparks at his shoulders, 22 squares apart, 20 squares up; 2 the sparks 6 squares across, "
     "two jagged bolts arcing from them toward the middle of his chest; 3 the bolts meeting in a white flash 8 squares on his "
     "chest; 4 fading sparks.",
     row(4, 34, 32) + FEET),
    ("w_zap", "W 每跳电到的敌人（目标身上），3 帧", "view_effects `league_drmundo_w_zap`（跟随，画在人物上面；左右对称）", "10 × 16",
     "电流每跳一次：目标身上一道竖着的小闪电劈下来，脚边几点火花。**左右对称**（闪电竖直、左右对称地画两道细的）。",
     ZP,
     f"a SMALL ZAP on a unit, 3 frames, {LR}: 1 two thin jagged cyan-white bolts coming down from 14 squares up, mirrored; 2 the "
     "bolts reaching the bottom, a white flash 4 squares there, a few sparks out to both sides; 3 fading sparks.",
     row(3, 12, 18) + "; centered across, the bolts' ends on the cell's bottom row."),
    ("w_burst", "W 放电：一圈电流炸开（他身上，不跟随），5 帧",
     "view_effects `league_drmundo_w_burst`（跟随，画在他身上；左右对称；大图表）", "48 × 32",
     "结束放电：以他为中心炸开一大圈青蓝色的电流冲击环（扁椭圆，从腰部往外扩到 48 格宽），一圈闪电往外射，中间一团白光（参考 W_LightningErosion03、Bubble）。**左右对称**，中间身体留空。",
     ZP,
     f"an ELECTRIC DISCHARGE round a big figure, 5 frames, {LR}, the middle EMPTY (a clear area 28 squares wide and 30 tall): 1 a "
     "white flash on his chest 10 squares; 2 a flat cyan shock ring 28 squares wide and 8 tall round his waist with a white "
     "core line; 3 the ring 40 wide, 8 jagged bolts shooting out of it at mirrored places; 4 the ring 48 wide and breaking up, "
     "sparks; 5 the last sparks.",
     row(5, 50, 34) + FEET),
    ("w_end_hit", "W 放电电到的敌人（目标身上），4 帧", "view_effects `league_drmundo_w_end_hit`（跟随，画在人物上面；左右对称）", "16",
     "放电电中：目标全身被一团青白色的电网包住一闪。**左右对称**。约 16 格。", ZP,
     f"an ELECTROCUTION on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a tangle of jagged cyan bolts 14 squares wide and 16 "
     "tall with a white core; 3 the tangle brightest, sparks out at mirrored places; 4 fading sparks.",
     row(4, 18, 18) + CENTER),
    # ---- R Maximum Dosage
    ("r_cast", "R 极限剂量：注射发动（他身上，不跟随），6 帧",
     "view_effects `league_drmundo_r_cast`（跟随，画在他身上；左右对称；大图表）", "40 × 40",
     "极限剂量：他身上爆出一大团绿色的化学液体和光（从胸口往外、往上冲），几颗粉红色的火花，绿色的泡泡往上冒（参考 R_Chemical_Mult、R_Droplets、R_ClothRing、R_Eye_Glow、Bubble）。"
     "**左右对称**，中间身体留空（只画四周和头顶）。",
     f"{CH} and {PK}",
     f"a CHEMICAL SURGE round a big figure, 6 frames, {LR}, the middle EMPTY (a clear area 26 squares wide and 30 tall where he "
     "stands): 1 a green glow ring 30 wide and 8 tall round his feet; 2 toxic green liquid splashing up at both sides to his "
     "shoulders in mirrored arcs, a white-lime core; 3 the splash at its highest, 40 squares tall, bubbles and a few pink sparks "
     "flying up; 4 the splash falling, bubbles rising over his head; 5 droplets falling, bubbles popping; 6 a faint green "
     "shimmer.",
     row(6, 42, 42) + FEET),
    ("r_on", "R 生效中（他身上，循环），4 帧", "view_buffs `league_drmundo_r_on`（跟随，画在他身上；左右对称）", "30 × 34",
     "极限剂量生效的 10 秒：他身边几颗绿色的泡泡慢慢往上冒、偶尔一滴绿色液体往下滴，眼睛那里一点粉红光（不用画眼睛，只画身体两边和头顶的泡泡）。"
     "**左右对称**，要稀疏，不要遮住他。",
     f"{CH} and {PK}",
     f"RISING BUBBLES round a big figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear area 24 squares wide and 30 "
     "tall): 4-6 small toxic green bubbles (2-3 squares) at both sides at mirrored places drifting up 3 squares a frame and "
     "popping at his shoulders, one green drip falling at each side; sparse - most of the cell empty.",
     row(4, 32, 36) + FEET),
    # ---- the passive: the chem-tank
    ("p_shake", "被动：挣脱控制（他身上），5 帧", "view_effects `league_drmundo_p_shake`（跟随，画在他身上；左右对称）", "30 × 30",
     "想去哪就去哪：他把控制甩开——一圈白绿色的碎玻璃 / 碎光片从他身上往外炸开（参考 P_Glass_Shards_2x2、R_Eye_Glow）。**左右对称**，中间身体留空。",
     f"{CH} and {ST}",
     f"a SHRUG-OFF BURST round a big figure, 5 frames, {LR}, the middle EMPTY (a clear area 24 squares wide and 28 tall): 1 a "
     "green-white ring of light 26 squares wide round his chest; 2 the ring shattering into glassy shards and green sparks; 3 the "
     "shards flying out at mirrored places, 30 squares across; 4 the shards spinning further and dimming; 5 a few motes.",
     row(5, 32, 32) + FEET),
    ("p_tank", "被动：地上的药罐（地上，循环），2 帧",
     "view_projectiles `league_drmundo_p_tank`（区域的画面：红色方会转 180°，所以要中心对称）", "12 × 8",
     "掉在地上的化学药罐（捡起来回血、减被动冷却）：一个**矮胖的圆罐子，从斜上方看**——金属的圆形罐口和罐底边、玻璃罐身里装着发光的绿色药水、"
     "罐子周围地上一圈淡绿光，药水的亮光 2 帧轮流闪。**中心对称**：整张转 180° 必须一模一样（不要画有上下、左右之分的东西，例如标签、斜放的罐子、只在一边的高光）。",
     f"{CH} and {ST}",
     f"a SQUAT CHEMICAL TANK lying on the ground seen from above at an angle, 2 frames, a seamless loop, {HALF}: an oval glass "
     "canister 10 squares wide and 6 tall with a steel rim all round, filled with glowing toxic green liquid, two steel clasps at "
     "its left and right ends (mirrored), a faint green glow ring on the ground round it 12 wide and 8 tall; the liquid's "
     "brightness pulsing between the frames - every highlight placed so the picture turned 180 degrees is the same.",
     row(2, 14, 10) + CENTER),
    ("p_land", "被动：药罐落地（地上，不跟随），4 帧", "view_effects `league_drmundo_p_land`（不跟随，地上；左右对称）", "16 × 8",
     "药罐落地：落点一小股尘土往两边溅，一圈绿色的光环一闪。**左右对称**。", f"{DU} and {CH}",
     f"a LANDING PUFF on the ground, 4 frames, {LR}: 1 a white flash 3 squares on the ground; 2 dust kicked out to both sides 12 "
     "squares wide, a flat green ring 10 wide; 3 the dust 16 wide and settling, the ring fading; 4 faint dust.",
     row(4, 18, 10) + "; centered across, the ground's middle 3 squares above the cell's bottom row."),
    ("p_pick", "被动：捡起药罐回血（地上，不跟随），4 帧", "view_effects `league_drmundo_p_pick`（不跟随；左右对称）", "16 × 20",
     "捡起药罐：一团绿色的光往上冲，几个绿色的「+」往上飘。**左右对称**。", CH,
     f"a HEALING BURST rising, 4 frames, {LR}: 1 a green flash 6 squares at the bottom; 2 a column of green light 8 wide rising 14 "
     "squares, two plus signs at its sides; 3 the column fading up, the pluses at 18 squares; 4 a few rising motes.",
     row(4, 18, 22) + "; centered across, the burst's foot on the cell's bottom row."),
    ("p_break", "被动：药罐被敌人踩碎（地上，不跟随），4 帧", "view_effects `league_drmundo_p_break`（不跟随，地上；左右对称）", "16 × 10",
     "药罐被踩碎：碎玻璃片往两边飞，绿色的药水溅开成一摊。**左右对称**。", f"{ST} and {CH}",
     f"a SMASHED TANK on the ground, 4 frames, {LR}: 1 a white flash 4 squares; 2 glass shards flying out to both sides at mirrored "
     "places, green liquid splashing up 6 squares; 3 the splash falling into a flat green puddle 14 wide and 4 tall, shards on "
     "the ground; 4 the puddle fading.",
     row(4, 18, 12) + "; centered across, the ground's middle 3 squares above the cell's bottom row."),
]
BIG = {"w_on", "w_start", "w_burst", "r_cast"}

GROUPS = [
    ("q_saw q_hit q_slow", ["DrMundo_Base_Q_Trail", "DrMundo_Base_Q_Bonesaw_Glow", "DrMundo_Base_Q_OilySmoke_2x2",
                            "DrMundo_Q_Spear_Impact_Diust_burst", "DrMundo_Base_Q_Ground_Crack", "DrMundo_P_Puddle_Goop"]),
    ("e_hit e_fling", ["DrMundo_Base_Q_Rocks_2X2", "Wukong_Base_Sparkles", "Dr_Mundo_Base_E_BuffDrips",
                       "Sion_Skin05_Sl_Dust_01", "DrMundo_Base_Q_Smoke", "DrMundo_Base_Smokey_Trail"]),
    ("w_*", ["DrMundo_Base_P_Lightning03", "DrMundo_Base_W_LightningErosion03", "DrMundo_Base_P_Capacitor_Erode",
             "DrMundo_Base_P_Ray_Mult", "DrMundo_Base_Bubble", "Aura_Self"]),
    ("r_cast r_on", ["DrMundo_Base_R_Chemical_Mult", "DrMundo_Base_R_Droplets", "DrMundo_Base_R_ClothRing",
                     "DrMundo_Base_R_Eye_Glow", "DrMundo_Base_R_glow_distort", "DrMundo_R_Bubble_Erode"]),
    ("p_*", ["DrMundo_Base_P_Glass_Shards_2x2", "DrMundo_Base_P_Bubble_Mask", "DrMundo_P_Puddle_Erode",
             "DrMundo_P_Puddle_Goop", "DrMundo_Base_R_Puddle_Mask", "bigglow02"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：普攻劈下"), ("attack_e", 3, "e_hit：药箱抡出"), ("skill", 4, "q_saw：扔出骨锯"),
         ("skill2", 2, "w_start / w_on：开启电击"), ("skill2_end", 2, "w_burst：放电"), ("ult", 5, "r_cast：注射吼叫")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("DrMundo_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"蒙多 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连骨锯），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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


def saw_ref(path):
    """The design's bone saw (design A, columns 0-34, rows 56-89) at 8x: the Bonesaw's flying picture is this saw."""
    des = np.asarray(Image.open(lp(os.path.join(HD, "A.png"))).convert("RGBA"))
    saw = des[56:90, 0:35].copy()
    m = np.zeros(saw.shape[:2], bool)
    for y in range(saw.shape[0]):
        for x in range(saw.shape[1]):
            r, g, b, al = (int(v) for v in saw[y, x])
            purple = b > r and b > g + 30 and r > 50
            m[y, x] = al > 0 and not purple
    saw[~m] = 0
    bg = Image.new("RGBA", (saw.shape[1] * 8, saw.shape[0] * 8), (104, 112, 72, 255))
    bg.alpha_composite(Image.fromarray(saw).resize(bg.size, Image.NEAREST))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 蒙多医生（祖安狂人）：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/drmundo_idle.png`：3/4 正面朝右的紫色大块头，近侧手拎着骨锯）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连骨锯 {h} 格高、{w} 格宽；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/drmundo_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/drmundo_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。`design/drmundo_saw.png`：他的骨锯（8 倍），飞出去的 `q_saw` 就是这把锯。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里蒙多自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色：**化学药剂是毒绿色**（骨锯的残影、减速黏液、药罐、极限剂量），**电击疗法是青蓝色的电**，**砍中、砸中是白热的冲击光**，药剂里点缀几颗**粉红**火花（他肩上宝石的颜色）。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着他的光环、电流、液体只画外圈和两边，中间他的身体位置留空**——他是个大块头（宽约 28 格、高约 30 格），每条都写了留空多大。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `q_saw`（骨锯）和 `e_fling`（被打飞的尸体）在空中**打转 / 翻滚**，倒过来看也一样，所以随便哪一面朝上都行。"
      "`p_tank`（地上的药罐）在红色方会被**转 180°**，所以要**中心对称**（转半圈一模一样）。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `drmundo_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `drmundo_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + E「大力行医」 | 骨锯劈砍；每隔几秒一次抡药箱的强化普攻，打死的小兵被打飞撞伤后面的敌人 | `a_hit` · `e_hit` · `e_fling` · `e_fling_hit` |")
    a("| 技能 1 = Q「病毒屠刀」 | 扔出骨锯，打中第一个单位：伤害、减速、回血 | `q_saw` · `q_hit` · `q_heal` · `q_slow` |")
    a("| 技能 2 = W「电击疗法」 | 开启后身边持续电人，结束时放电，打中英雄回灰色生命 | `w_start` · `w_on` · `w_zap` · `w_burst` · `w_end_hit` |")
    a("| 大招「极限剂量」 | 给自己注射：回血、加最大生命、移速 | `r_cast` · `r_on` |")
    a("| 被动「想去哪就去哪」 | 挣脱控制，丢下药罐；捡起回血，被敌人踩到就碎 | `p_shake` · `p_tank` · `p_land` · `p_pick` · `p_break` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、黏液、火花、闪电、碎片、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（例外：骨锯、药罐的金属和玻璃、被打飞的尸体，可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("毒绿化学药剂", CHEM), ("青蓝电流", ZAP), ("白热冲击", HOT), ("钢 / 玻璃 / 金属", STEEL), ("尘土", DUST),
                        ("粉红火花", PINK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 25000，"
      "Q 射程 70000，电击疗法半径 22000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `drmundo_fx_{name}.png`：{title}\n")
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
        a(f"| `drmundo_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_drmundo_fx`（小的）和 `league_drmundo_big`（" + "、".join(sorted(BIG)) +
      "），tag = 名字（build_drmundo.py 的 views）。")
    a("- `q_saw`、`e_fling` 是飞行投射物（画面朝飞行方向转，它们本来就在转）；`p_tank` 是地上区域的画面（会转 180°，断言中心对称）；"
      "`p_land`、`p_pick`、`p_break` 不跟随；`q_slow` 脚下 buff（z -1）；`w_on` 他下面一层（z -1）。")
    a("- 用 `pixel_1x/` 切格，断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="drmundo_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "drmundo_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: extract them first (Temp/md_work/py/fxref.py)")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "A.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 3, 0), 3, 1)).save(os.path.join(out, "design", "drmundo_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "drmundo_size.png"))
    shots_sheet(os.path.join(out, "design", "drmundo_shots.png"))
    saw_ref(os.path.join(out, "design", "drmundo_saw.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"drmundo_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
