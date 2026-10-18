#!/usr/bin/env python3
"""Build gangplank_fx_pack.zip: step 3 of Gangplank's sprite - Codex draws his effects (pack_ziggs_fx.py's way).

    python work/gp/fx_ref_gp.py                 # League's particle textures -> C:/t/gp_work/fxref (Riot's art, local only)
    python tools/art/pack_gangplank_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name gangplank_fx_redo_pack]

The pack (%TEMP%/gp_work/fx/gangplank_fx_pack, zipped into --out, default dist/gangplank_packs) holds PROMPTS.md (also
written to assets/source/gangplank/PROMPTS_FX.md), design/gangplank_idle.png (his idle at 4x, the design's squares at
PPU 1.5), design/gangplank_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base
fighter), design/gangplank_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Gangplank grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_gangplank.py): projectiles q_bullet, e_throw (turned with their
flight, so each is symmetric top to bottom); view_effects a_hit, p_hit, q_hit, e_land, e_keg, e_keg_lit, e_boom, e_hit,
r_warn, r_wave, r_hit; view_buffs p_ms, e_slow, w_imm, r_slow; and three pictures drawn into his own frames (they have a
front: the game mirrors his frames with him, never an effect picture - skill rule "Both sides"): q_flash (the muzzle on
Q's shot frame), w_cast (the orange at his mouth), r_cast (the flare out of the raised cannon). League's colours:
orange-hot fire and gold for his passive and the pistol, brown wood and dark iron for the kegs and the cannonballs, grey
powder smoke, a citrus orange for W, burnt orange-red for the barrage's area; light gets no outline, solid things (the
kegs, the cannonballs, the orange) may. Every other picture is symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gp_work")
REF = "C:/t/gp_work/fxref"
DOC = os.path.join(ROOT, "assets", "source", "gangplank", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_gangplank")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "gangplank_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410"      # blasts, burns, sparks
GOLD = "#FFFFFF, #FFF4C8, #FFD86A, #F2A82E, #B86A18, #5E3008"      # the pistol's flash, coins, the passive's gleam
WOOD = "#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A"      # the kegs' staves, splinters
IRON = "#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418"      # hoops, cannonballs
SMOKE = "#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424"     # powder smoke, dust
CITRUS = "#FFFFFF, #FFF2B0, #FFD04A, #FF9E1E, #E06A10, #8A3A08"    # the orange, W's glow (+ a leaf #7CC24A / #3E7A28)
WARN = "#FFFFFF, #FFD0B0, #FF8A4A, #E2481E, #A0241A, #56100C"      # the barrage's area
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FI = f"a fire and spark ramp ({FIRE})"
GO = f"a gold light ramp ({GOLD})"
WO = f"a wood ramp ({WOOD})"
IR = f"a dark iron ramp ({IRON})"
SM = f"a powder smoke and dust grey ramp ({SMOKE})"
CI = f"a citrus orange ramp ({CITRUS}) with a small leaf in #7CC24A and #3E7A28"
WA = f"a burnt orange-red ramp ({WARN})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: "
      "flying left it is flipped over)")
FLY = "; it flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically."
OWN = "(drawn into his own action frames, which the game mirrors with him, so it may point one way)"
OWN_ZH = "（这张画进他自己的动作帧，会跟着他一起翻，所以可以有方向）"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack + the passive
    ("a_hit", "普攻命中：弯刀砍中（目标身上），4 帧", "view_effects `league_gangplank_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "弯刀砍中：两道交叉的橙红色灼热刀痕（一个 X），白色的芯，几粒火星往外飞（参考 BA_sword_trail、P_sword_blade、hit_sparks）。"
     "**左右对称**。约 12 格。",
     FI,
     f"a CUTLASS SLASH HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 two crossed orange-hot slash streaks "
     "(an X 10 squares, one stroke the mirror of the other) with a white core; 3 the X 12 squares fading, sparks flying "
     "out at mirrored places; 4 two embers drifting.",
     row(4, 12, 12) + CENTER),
    ("p_hit", "被动「烈火审讯」点燃（目标身上），5 帧", "view_effects `league_gangplank_p_hit`（跟随，画在人物上面；左右对称）", "16",
     "被动的那一刀点着了敌人：先一下白黄色的闪光，然后橙色的火苗从敌人身上往上窜，两边各几道火舌，火星往上飘，最后火小下去冒点烟"
     "（参考 P_sword_flames、taunt_flames）。**左右对称**。约 16 格。",
     f"{FI} and {SM}",
     f"a FIRE IGNITION on a unit, 5 frames, {LR}: 1 a white-yellow flash 6 squares; 2 orange flames bursting up 10 squares "
     "from the middle; 3 flames 14 squares tall licking up both sides (mirrored), embers rising; 4 the flames dying down, "
     "embers floating up; 5 small flames and a little grey smoke.",
     row(5, 16, 16) + CENTER),
    ("p_ms", "被动加速（他脚下，2 秒，循环），4 帧", "view_buffs `league_gangplank_p_ms`（跟随，画在人物下面 z -1；左右对称；循环）",
     "22 × 8",
     "被动点着敌人后他跑得更快：脚下两边几道白金色的速度线（参考 P_speedstreaks），一闪一闪。**左右对称**（两边都画），只画在脚下。",
     GO,
     f"SPEED STREAKS at a unit's feet, 4 frames, a seamless loop, {LR}: three short white-gold streak lines on each side "
     "of the feet (the middle 8 squares left clear), 3-7 squares long, low along the ground; they slide outward and "
     "fade in turn so the loop flows.",
     row(4, 22, 8) + "; centered across, the streaks' lowest row on the cell's bottom row."),
    # ---- Q Parrrley
    ("q_flash", "Q 枪火谈判：枪口火光（画进他开枪那一帧），3 帧", "画进他的动作帧（skill 第 3 帧的炮口）；可以有方向", "16 × 12",
     "开枪时炮口喷出的火光：炮口（格子左边中间）一团白黄色的星形闪光，往右喷出一锥橙黄色的火焰，接着一团灰色的火药烟"
     f"（参考 cast_muzzleflash、Gangplank_base_cast_muzzelflash、q_smoketrail）。{OWN_ZH}，**朝右画**。",
     f"{GO} and {FI} and {SM}",
     f"a MUZZLE FLASH from a cannon pointing RIGHT, 3 frames {OWN}: 1 a white-yellow star burst 6 squares at the "
     "cell's left edge (the muzzle) with a cone of white-gold flame 8 squares pointing right; 2 the cone 14 squares "
     "orange-gold with sparks flying ahead; 3 a grey powder smoke puff 8 squares drifting right, two embers.",
     row(3, 16, 12) + "; the muzzle at the middle of each cell's left edge."),
    ("q_bullet", "Q 子弹（飞行中），2 帧循环", "view_projectiles `league_gangplank_q_bullet`（随飞行方向转动；上下对称；循环）", "10 × 6",
     "飞出去的子弹：一颗发白金色光的圆弹（约 3 格），身后（左边）拖一小段橙金色的光尾（参考 Q_missile_bullet、q_smoketrail）。**上下对称**。",
     f"{GO} and {FI}",
     f"a PISTOL SHOT in flight, 2 frames, a seamless loop, {TB}: a glowing white-gold round shot 3 squares with a short "
     "orange-gold trail 6 squares behind it (to the left, mirrored top to bottom); the trail flickers between the frames.",
     row(2, 10, 6) + FLY),
    ("q_hit", "Q 打中（目标身上），4 帧", "view_effects `league_gangplank_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "子弹打中：白光一闪，一团橙金色的火光带几道星芒，然后两枚金币从两边弹起来一闪（枪火谈判会抢金币，参考 Q_tar_hitflash、Q_coin、"
     "q_tar_sparks）。**左右对称**。约 14 格。",
     f"{GO} and {FI}",
     f"a SHOT HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 an orange-gold burst 9 squares with four short "
     "star rays; 3 the burst 12 squares fading, two GOLD COINS (3 squares each, a white glint) popping up at mirrored "
     "places; 4 the coins higher and glinting, two embers.",
     row(4, 14, 14) + CENTER),
    # ---- E Powder Keg
    ("e_throw", "E 火药桶（飞行中），3 帧循环", "view_projectiles `league_gangplank_e_throw`（随飞行方向转动；上下对称；循环）",
     "12 × 10",
     "扔到敌人脚下的火药桶：一个小木桶横躺着顺着飞行方向（约 8 格长、6 格高，两道深色铁箍竖着），**上下对称**，所以桶上不画图案；"
     "三帧里木纹高光轮换，像在翻滚。木桶是实心的，可以有一圈深色边。",
     f"{WO} and {IR}",
     f"a POWDER KEG in flight, 3 frames, a seamless loop, {TB}: a small wooden barrel lying along the flight, 8 squares "
     "long and 6 tall, two dark iron hoops across it, bulging in the middle; the stave highlights shift each frame as "
     "if it tumbles. Solid: a 1-square dark outline round the barrel is allowed.",
     row(3, 12, 10) + FLY),
    ("e_land", "E 火药桶落地（地上，不跟随），4 帧", "view_effects `league_gangplank_e_land`（不跟随，画在人物下面 z -1；左右对称）",
     "26 × 10",
     "桶落地：地上往两边溅起一圈灰尘（参考 E_barrel_smoke、E_ground_shadow）。**左右对称**，中间空着（桶本身在 e_keg 里画）。",
     SM,
     f"a KEG LANDING on the ground, 4 frames, {LR}: 1 dust puffs 8 squares wide on the ground at both sides of the "
     "middle (the middle 6 squares clear); 2 the dust thrown out 18 squares wide and 4 tall; 3 24 squares wide and "
     "thinner; 4 faint dust.",
     row(4, 26, 10) + "; centered across, the dust's base on the cell's bottom row."),
    ("e_keg", "E 地上的火药桶（还不能引爆），2 帧循环",
     "view_effects `league_gangplank_e_keg`（不跟随，画在人物上面 z 1；左右对称；每 0.17 秒重贴）", "14 × 16",
     "放在地上的火药桶（刚落地，还没到能引爆的时候）：一个**正立的木桶**（约 10 格宽、12 格高），三道深色铁箍，桶身正面一个白色的**骷髅交叉骨**"
     "标记，顶上一截短短的麻绳引线（**没点着**）。两帧只是木头上的高光微微闪一下（参考 E_barrel_image）。**左右对称**。"
     "木桶是实心的，可以有一圈深色边。",
     f"{WO} and {IR}",
     f"A POWDER KEG standing on the ground, 2 frames, a seamless loop, {LR}: an upright wooden barrel 10 squares wide and "
     "12 tall, bulging in the middle, three dark iron hoops, a small white skull-and-crossbones mark on its front, a short "
     "unlit rope fuse on top; the frames differ only in a faint shimmer on the staves. Solid: a 1-square dark outline "
     "round the barrel is allowed.",
     row(2, 14, 16) + "; centered across, the barrel's lowest square on the cell's bottom row."),
    ("e_keg_lit", "E 能引爆的火药桶（引线点着），2 帧循环",
     "view_effects `league_gangplank_e_keg_lit`（不跟随，画在人物上面 z 1；左右对称）", "14 × 18",
     "同一个火药桶（和 e_keg 一模一样，逐格相同），但引线**已经点着**：顶上一团闪动的黄橙色火星，桶底周围一圈淡淡的橙光，表示现在一枪就能引爆"
     "（参考 e_fuze_glow、Gangplank_base_e_fuze_center_glow）。**左右对称**。",
     f"{WO} and {IR} and {FI}",
     f"THE SAME POWDER KEG, ripe, 2 frames, a seamless loop, {LR}: the barrel of e_keg square for square (the same "
     "place in the cell), its rope fuse LIT: a bright yellow-orange spark 3 squares on top flickering between the frames, "
     "a faint orange glow 1 square round the barrel's base.",
     row(2, 14, 18) + "; centered across, the barrel's lowest square on the cell's bottom row."),
    ("e_boom", "E 火药桶爆炸（地上，不跟随），7 帧",
     "view_effects `league_gangplank_e_boom`（不跟随，画在人物上面 z 2；左右对称；大图表）", "64 × 48",
     "火药桶炸开（半径约 30 格）：白光一闪，一团橙黄色的火球从地上冒起，木桶碎片和铁箍往四周飞，地上一圈火往外推，接着变成翻滚的黑灰色火药烟，"
     "最后地上一块焦黑淡去（参考 E_barrel_lightflash、E_barrel_spikes、E_crit_woodpieces、E_barrel_smoke）。**左右对称**。",
     f"{FI} and {SM} and {WO}",
     f"A POWDER KEG EXPLOSION on the ground, 7 frames, {LR}: 1 a white flash 12 squares at the middle just above the "
     "ground; 2 an orange-yellow fireball 24 squares wide rising with a white core, wooden splinters flying out at "
     "mirrored places; 3 the fireball 40 squares wide and 30 tall, a ring of fire along the ground (an ellipse 56 wide "
     "and 18 tall), splinters and iron hoop pieces flying out and up; 4 rolling black-grey powder smoke 50 squares wide "
     "with fire inside; 5 the smoke thinner and higher, embers; 6 faint smoke, a dark scorch ellipse on the ground; 7 the "
     "scorch fading.",
     row(7, 64, 48) + "; centered across, the ground (the blast's base) 5 squares above the cell's bottom row."),
    ("e_hit", "E 被火药桶炸中（目标身上），4 帧", "view_effects `league_gangplank_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "被桶炸中的敌人身上：橙色的爆炸火光加几片木屑（参考 E_crit_woodpieces、hit_flash）。**左右对称**。约 14 格。",
     f"{FI} and {WO}",
     f"a KEG BLAST HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 an orange burst 10 squares with a white "
     "core; 3 the burst 14 squares breaking up, four wooden splinters flying out at mirrored places; 4 grey smoke puffs.",
     row(4, 14, 14) + CENTER),
    ("e_slow", "E 减速（敌人脚下，2 秒，循环），4 帧", "view_buffs `league_gangplank_e_slow`（跟随，画在人物下面 z -1；左右对称；循环）",
     "16 × 6",
     "被桶炸到减速的敌人脚下：地上一圈灰色的火药烟，几粒橙色余烬。**左右对称**，只画在脚下。",
     f"{SM} and {FI}",
     f"a SLOW at a unit's feet, 4 frames, a seamless loop, {LR}: a grey powder smoke ring on the ground (an ellipse 14 "
     "squares wide and 4 tall), 4 orange embers on it at mirrored places; 1 dim, 2 bright, 3 brightest, 4 bright.",
     row(4, 16, 6) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
    # ---- W Remove Scurvy
    ("w_cast", "W 坏血病疗法：咬一口橘子（画进他吃东西的帧），3 帧", "画进他的动作帧（skill_w 第 2–3 帧，嘴边的手上）；可以有方向",
     "10 × 10",
     "他咬的橘子：第 1 帧一个完整的圆橘子（约 6 格，橙色，顶上一片小绿叶）；第 2 帧咬掉一口，几滴黄橙色的果汁飞出来；第 3 帧剩下半个，"
     f"几点果汁亮光（参考 w_spit、Gangplank_W_Heal_Light）。{OWN_ZH}。橘子是实心的，可以有一圈深色边。",
     CI,
     f"an ORANGE being bitten, 3 frames {OWN}: 1 a whole round orange 6 squares with a highlight and a tiny green leaf on "
     "top; 2 the orange with a bite taken out of its right side, three bright juice drops flying right; 3 half an orange "
     "left, small juice sparkles. Solid: a 1-square dark outline round the fruit is allowed.",
     row(3, 10, 10) + CENTER),
    ("w_imm", "W 吃完后的免控光（他脚下和身边，1 秒，循环），4 帧",
     "view_buffs `league_gangplank_w_imm`（跟随，画在人物下面 z -1；左右对称；循环）", "36 × 14",
     "吃完橘子后的 1 秒免控：脚下一圈金橙色的光环（扁椭圆宽 30 格、高 8 格），两边往上飘几粒柑橘色的亮点（参考 Gangplank_base_W_heal_glow、"
     "common_Aura_Self）。**左右对称**，中间身体的位置留空。",
     CI,
     f"A CLEANSE GLOW round a unit's feet, 4 frames, a seamless loop, {LR}: a golden-orange ring on the ground (an "
     "ellipse 30 squares wide and 8 tall, 1-2 squares thick, brightest at the front), small citrus sparkles rising at "
     "both sides (mirrored); the ring's light runs round and the sparkles rise and fade in turn.",
     row(4, 36, 14) + "; centered across, the ellipse's middle 4 squares above the cell's bottom row."),
    # ---- R Cannon Barrage
    ("r_cast", "R 加农炮幕：朝天打出的信号弹（画进他举炮的帧），4 帧", "画进他的动作帧（ult 第 3–4 帧，朝天的炮口上方）；可以有方向",
     "12 × 44",
     "他朝天开出的信号弹：炮口（格子底边中间）先一团白黄色的闪光，一颗红橙色的信号弹拖着亮尾巴直直往上冲，到顶上炸开成一颗小星，"
     f"下面留一条渐淡的烟（参考 R_cas_glowspark、R_cast_sparks）。{OWN_ZH}。",
     f"{FI} and {WA} and {SM}",
     f"A SIGNAL FLARE shot straight up from a cannon's muzzle at the middle of the cell's bottom edge, 4 frames {OWN}: "
     "1 a white-yellow muzzle burst 6 squares; 2 a bright red-orange flare with a white head streaking up 24 squares, a "
     "bright trail; 3 the flare at the top (38 squares up) bursting into a red-orange star 8 squares, a grey smoke trail "
     "below it; 4 the star's sparks falling, the smoke trail fading.",
     row(4, 12, 44) + "; the muzzle at the middle of the cell's bottom edge."),
    ("r_warn", "R 落点预警（地上，不跟随，1 秒），8 帧",
     "view_effects `league_gangplank_r_warn`（不跟随，画在人物下面 z -2；左右对称；大图表）", "92 × 34",
     "信号弹飞向落点的 1 秒里，地上的范围圈（从斜上方看的扁椭圆：宽 88 格、高 30 格）：一圈焦橙红色的虚线外圈，中间一个淡一点的内圈"
     "（宽 34 格），几个小小的准星标记，8 帧里越来越亮，最后一帧最亮（马上开炮）（参考 R_land_Outerring、R_center_AoE_ring、"
     "R_ground_decal）。**左右对称**。",
     WA,
     f"THE BARRAGE AREA marked on the ground seen from above at an angle, 8 frames, {LR}: a burnt orange-red dashed outer "
     "ring (an ellipse 88 squares wide and 30 tall, 1-2 squares thick), a fainter inner ring (an ellipse 34 wide and 12 "
     "tall), four small crosshair marks inside at mirrored places; over the 8 frames the rings grow brighter, frame 8 "
     "the brightest with white edges.",
     row(8, 92, 34) + "; centered across, the ellipse's middle 15 squares above the cell's bottom row."),
    ("r_wave", "R 一波炮弹落下（地上，不跟随，0.5 秒），6 帧",
     "view_effects `league_gangplank_r_wave`（不跟随，画在人物上面 z 2；左右对称；大图表；每 0.5 秒一波，共 12 波）", "96 × 84",
     "从海上船里打过来的一波炮弹砸进范围里（范围是地上的扁椭圆宽 88 格、高 30 格）：**三颗铁炮弹**（每颗约 5 格，黑铁色带白色高光，"
     "一颗在中间，两颗在左右对称的位置）从天上拖着火尾巴砸下来，落地炸开三团橙色的火光，泥土碎块往上飞，冒黑灰烟，地上留下裂纹淡去"
     "（参考 R_cannonball_large、R_cannonball_trail、R_hit_dirtbits、R_hit_groundcrack、R_hit_aoering）。**左右对称**，画面是正立的（不会被转）。",
     f"{IR} and {FI} and {SM}",
     f"ONE WAVE of a cannon barrage falling into an area, 6 frames, {LR} (an upright picture, never turned): the area is an "
     "ellipse 88 squares wide and 30 tall on the ground whose middle is 16 squares above the cell's bottom; three dark "
     "iron cannonballs 5 squares each (a white highlight) fall at mirrored places - one in the middle, two 26 squares to "
     "either side - with fiery orange trails: 1 the balls high, their bottoms 60 squares above the ground, trails 10 "
     "squares; 2 the balls 25 squares above the ground; 3 hitting the ground: three orange-white explosions 14 squares, "
     "dirt chunks flying up; 4 the explosions 20 squares with dark smoke, ground cracks; 5 grey smoke puffs rising; 6 "
     "faint smoke and cracks fading.",
     row(6, 96, 84) + "; centered across, the ellipse's middle 16 squares above the cell's bottom row."),
    ("r_hit", "R 被炮弹打中（敌人身上），4 帧", "view_effects `league_gangplank_r_hit`（跟随，画在人物上面；左右对称）", "14",
     "被炮弹炸到的敌人身上：橙红色的火光加泥土碎块。**左右对称**。约 14 格。",
     f"{FI} and {SM}",
     f"a CANNONBALL HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 an orange-red burst 11 squares with a "
     "white core; 3 the burst 14 squares, dirt chunks and embers at mirrored places; 4 smoke wisps.",
     row(4, 14, 14) + CENTER),
    ("r_slow", "R 减速（敌人脚下，0.5 秒，循环），4 帧", "view_buffs `league_gangplank_r_slow`（跟随，画在人物下面 z -1；左右对称；循环）",
     "16 × 6",
     "被炮弹减速的敌人脚下：地上一圈泥土和灰烬。**左右对称**，只画在脚下。",
     SM,
     f"a SLOW at a unit's feet, 4 frames, a seamless loop, {LR}: a ring of dirt and ash on the ground (an ellipse 14 "
     "squares wide and 4 tall) with small dirt bits at mirrored places; 1 dim, 2 bright, 3 brightest, 4 bright.",
     row(4, 16, 6) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
]
BIG_FX = ["e_boom", "r_warn", "r_wave"]
OWN_FX = {"q_flash": ("skill", [3]), "w_cast": ("skill_w", [2, 3]), "r_cast": ("ult", [3, 4])}
REDO = {}
GROUPS = [
    ("a_hit p_hit p_ms", ["Gangplank_Base_BA_sword_trail", "Gangplank_Base_P_sword_blade", "Gangplank_Base_P_sword_flames",
                          "Gangplank_Base_taunt_flames", "Gangplank_Base_P_speedstreaks", "Gangplank_Base_hit_sparks"]),
    ("q_flash q_bullet q_hit", ["Gangplank_Base_cast_muzzleflash", "Gangplank_base_cast_muzzelflash",
                                "Gangplank_Base_Q_missile_bullet", "Gangplank_base_q_smoketrail",
                                "Gangplank_Base_Q_tar_hitflash", "Gangplank_Base_Q_coin"]),
    ("e_throw e_land e_keg e_keg_lit", ["Gangplank_Base_E_barrel_image", "Gangplank_Base_E_ground_shadow",
                                        "Gangplank_Base_e_fuze_glow", "Gangplank_base_e_fuze_center_glow",
                                        "Gangplank_Base_E_barrel_smoke"]),
    ("e_boom e_hit e_slow", ["Gangplank_Base_E_barrel_lightflash", "Gangplank_Base_E_barrel_spikes",
                             "Gangplank_Base_E_crit_woodpieces", "Gangplank_Base_e_smoke", "Gangplank_Base_hit_flash"]),
    ("w_cast w_imm", ["Gangplank_Base_w_spit", "Gangplank_W_Heal_Light", "Gangplank_base_W_heal_glow", "common_Aura_Self"]),
    ("r_cast r_warn", ["Gangplank_Base_R_cas_glowspark", "Gangplank_Base_R_cast_sparks", "Gangplank_Base_R_land_Outerring",
                       "Gangplank_Base_R_center_AoE_ring", "Gangplank_Base_R_ground_decal"]),
    ("r_wave r_hit r_slow", ["Gangplank_Base_R_cannonball_large", "Gangplank_Base_R_cannonball_trail",
                             "Gangplank_Base_R_hit_dirtbits", "Gangplank_Base_R_hit_groundcrack",
                             "Gangplank_Base_R_hit_aoering"]),
]
FEET = 11                                             # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：弯刀劈下（命中画在目标身上）"), ("skill", 3, "q_flash：开枪这一帧，枪口火光画在右边炮口"),
         ("skill2", 3, "e_throw：放桶（桶由技能扔到敌人脚下）"), ("skill_w", 2, "w_cast：橘子画在嘴边那只手里"),
         ("ult", 3, "r_cast：信号弹从朝天的炮口往上打"), ("run", 3, "p_ms：被动加速时画在脚下"),
         ("idle", 1, "待机"), ("hit", 2, "受击")]


def ref_sheet(path):
    S, LW = 170, 170
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                sys.exit(f"missing reference {p}")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Gangplank_Base_", "").replace("Gangplank_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"普朗克 {figs[0].shape[1]}×{figs[0].shape[0]} 格（含弯刀），原版斗士 {figs[1].shape[1]}×"
                    f"{figs[1].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
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
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is his pivot, FEET rows over the ground
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
    """His idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    import rig_gangplank as J
    F = J.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)).save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 普朗克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/gangplank_idle.png`：3/4 正面朝右的海盗船长，黑色月牙海盗帽、"
      f"花白长胡子，青绿领子、赤膊，红腰带，背后深紫长外套，近侧手把金色手炮扛在肩上，远侧手拿一把刀尖烧红的锯齿弯刀）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连弯刀 {h} 格高、{w} 格宽；"
      f"**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/gangplank_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - `design/gangplank_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里普朗克自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**被动和刀是烧红的橙色火**，**手枪的火光和金币是金色**，**火药桶是棕色木桶加黑铁箍、"
      "爆炸是橙黄色的火加黑灰色火药烟**，**W 是橘子的柑橘橙**，**大招的范围是焦橙红色，炮弹是黑铁色**。")
    a("> - **特效要亮**：每团光、每次爆炸都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **飞行中的东西（q_bullet 子弹、e_throw 火药桶）上下对称**：游戏会把飞行的图按飞的方向转，往左飞时整张图上下翻过来。")
    a("> - **q_flash 枪口火光、w_cast 橘子、r_cast 信号弹三张会画进他自己的动作帧**（会跟着他一起翻面），所以可以有方向，按每条写的朝向画。")
    a("> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他朝左时也是同一张图。")
    a("> - **围着人的画面中间身体位置留空**，不要盖住人。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 20]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gangplank_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、"
      "透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的名字 `name`、帧数、"
      "每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/gangplank_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 "
      f"`outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「烈火审讯」 | 弯刀砍；每隔一段时间下一刀点燃敌人（真实伤害的灼烧），自己加速 | `a_hit` · `p_hit` · `p_ms` |")
    a("| 技能 1 = Q「枪火谈判」 | 手枪平端开一枪（会暴击、带被动），打中能引爆旁边能引爆的火药桶 | `q_flash`（画进动作） · `q_bullet` · `q_hit` |")
    a("| 技能 2 = E「火药桶」 | 把火药桶扔到敌人脚下，落地 1 秒后引线点着；被他的枪或刀引爆，炸伤并减速范围里的敌人 | "
      "`e_throw` · `e_land` · `e_keg` · `e_keg_lit` · `e_boom` · `e_hit` · `e_slow` |")
    a("| 自动吃的 W「坏血病疗法」 | 被控住或被围时咬一口橘子，回血并短暂免控 | `w_cast`（画进动作） · `w_imm` |")
    a("| 大招「加农炮幕」 | 朝天打信号弹，海上的船往一大片范围里一波一波地砸炮弹（12 波、6 秒），每波伤害并减速 | "
      "`r_cast`（画进动作） · `r_warn` · `r_wave` · `r_hit` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：火药桶、炮弹、橘子可以有一圈深色边）。")
    a("- **要亮**：每个光和火的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火和火星（所有爆炸、灼烧、刀痕）", FIRE), ("金色光（手枪火光、金币、加速）", GOLD), ("木头（火药桶、木屑）", WOOD),
                        ("黑铁（铁箍、炮弹）", IRON), ("火药烟和尘土", SMOKE), ("柑橘橙（橘子、W 的光，叶子用 #7CC24A / #3E7A28）", CITRUS),
                        ("焦橙红（大招范围、信号弹）", WARN)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：火药桶爆炸半径 30000，"
      "大招范围半径 44000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `gangplank_fx_{name}.png`：{title}\n")
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
        a(f"| `gangplank_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_gangplank_fx`（小的）和 `league_gangplank_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_gangplank.py 的 views）。")
    a(f"- 画进动作帧的三张（{'、'.join(OWN_FX)}）：按 rig_gangplank 的帧把它们放到炮口 / 嘴边的手 / 朝天的炮口（skill 第 3 帧、"
      "skill_w 第 2–3 帧、ult 第 3–4 帧），用 Rig.bake 的 over 层画进 PPU 帧，kit 里不再播 CasterViewEffect。")
    a("- 投射物 `q_bullet`、`e_throw` 是 view_projectiles（随飞行方向转动，断言上下对称）；其余（画进动作的三张除外）断言左右对称。"
      "`e_keg`、`e_keg_lit` 每 10 tick 在落点重贴一次（2 帧 × 83 ms），`r_wave` 每 30 tick 一波（6 帧铺满 500 ms），"
      "`r_warn` 8 帧铺满信号弹飞行的 60 tick。")
    a("- 用 `pixel_1x/` 切格（import_ziggs_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="gangplank_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "gangplank_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/gp/fx_ref_gp.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "gangplank_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "gangplank_size.png"))
    shots_sheet(os.path.join(out, "design", "gangplank_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"gangplank_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
