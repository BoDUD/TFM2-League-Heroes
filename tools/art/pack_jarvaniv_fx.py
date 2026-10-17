#!/usr/bin/env python3
"""Build jarvaniv_fx_pack.zip: step 3 of Jarvan IV's sprite - Codex draws his effects (pack_nasus_fx.py's way).

    python work/jv/fx_ref_jv.py              # League's particle textures -> %TEMP%/jv_work/fxref (Riot's art, local only)
    python tools/art/pack_jarvaniv_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name jarvaniv_fx_redo_pack]

The pack (%TEMP%/jv_work/fx/jarvaniv_fx_pack, zipped into --out, default dist/jarvaniv_packs) holds PROMPTS.md (also
written to assets/source/jarvaniv/PROMPTS_FX.md), design/jarvaniv_idle.png (his idle at 4x, the design's squares at
PPU 1.5), design/jarvaniv_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base
fighter), design/jarvaniv_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Jarvan IV grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_jarvaniv.py: no projectile picture - the thrusts, the thrown
standard and the leap fly unseen, the motion is in his frames; view_effects a_hit, p_hit, q_hit, q_land, e_flag, e_hit,
w_cast, w_hit, r_ring, r_hit, r_zap; view_buffs q_shred, f_as, w_on, w_slow). League's colours: the thrusts and
Martial Cadence gold-white, Dragon Strike cyan-blue speed light, its armour shred League's RED cracked shield, the
Demacian Standard a gold pole with a blue banner, Golden Aegis a gold shell with a blue ground shockwave, Cataclysm
grey-brown rock walls with dust; light gets no outline, solid things (the standard, the shield icon, rocks) may.
Red side: the client never mirrors an effect picture, so every picture is symmetric left to right (the standard too:
its banner hangs straight down from a crossbar).
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "jv_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "jarvaniv", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_jarvaniv")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "jarvaniv_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A"      # the thrusts, Martial Cadence, the standard's pole
BLUE = "#FFFFFF, #DDF4FF, #8ED2FF, #3C96F0, #2258B8, #12306E"      # Dragon Strike's speed light, Golden Aegis' shockwave
RED = "#FFFFFF, #FFD6C8, #FF8060, #E2341E, #9C1610, #520A08"       # the armour shred shield
BANNER = "#FFFFFF, #D2E2FF, #7CA4EA, #3566C4, #1F3E8A, #10224E"    # the Demacian Standard's banner
ROCK = "#EFE6D6, #CDBD9E, #A08C6C, #74624A, #4C4032, #2C241C"      # Cataclysm's walls, rubble and dust
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"a gold gleam ramp ({GOLD})"
BL = f"a cyan-blue speed-light ramp ({BLUE})"
RE = f"a crimson ramp ({RED})"
BA = f"a royal blue banner ramp ({BANNER})"
RO = f"a grey-brown rock and dust ramp ({ROCK})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HIM = "an armoured knight 18 squares wide and 40 tall stands in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack + the passive
    ("a_hit", "普攻命中：骑枪枪尖刺中（目标身上），4 帧", "view_effects `league_jarvaniv_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "枪尖刺中的一下：一颗白色的四芒星闪光，中间一道横着的金白色刺击光（往左右两边一样长），金色火星往外飞（参考 BA_HitEffect、"
     "BA_sliver、BA_color-firefade）。**左右对称**。约 12 格。",
     GO,
     f"a LANCE THRUST IMPACT on a unit, 4 frames, {LR}: 1 a white four-pointed star flash 4 squares; 2 a gold-white "
     "horizontal thrust streak 12 squares wide and 2 tall through the middle with a white core, the star's thin rays 8 "
     "squares long; 3 the streak fading, 6 gold sparks flying out at mirrored places; 4 fading sparks.",
     row(4, 12, 12) + CENTER),
    ("p_hit", "被动「战争律动」触发（目标身上），5 帧", "view_effects `league_jarvaniv_p_hit`（跟随，画在人物上面；左右对称）", "16",
     "战争律动触发（按目标最大生命值额外伤害）：目标身上先一道金白闪光，然后白色的裂纹从中心往四周裂开（像盔甲被打裂，参考 P_Cracks），"
     "金色碎片往外飞，最后裂纹淡去。**左右对称**。约 16 格。",
     GO,
     f"a MARTIAL CADENCE CRACK on a unit, 5 frames, {LR}: 1 a gold-white flash 6 squares; 2 white cracks bursting out "
     "from the centre (6 jagged lines 1 square thick and 5 squares long at mirrored angles) round a gold glow; 3 the "
     "cracks 8 squares long, gold shards flying out at mirrored places; 4 the cracks fading, the shards farther out; 5 "
     "faint cracks and two shards.",
     row(5, 16, 16) + CENTER),
    # ---- Q Dragon Strike
    ("q_hit", "Q 巨龙撞击命中（目标身上），4 帧", "view_effects `league_jarvaniv_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "骑枪带着蓝白色的冲击刺穿目标：一团白芯的青蓝色光爆，几道蓝白色的速度线往左右两边横着射出，蓝色火星（参考 Q_Streak、Q_ball01、"
     "Q_speedlines、Q_color-movequick）。**左右对称**。约 14 格。",
     BL,
     f"a DRAGON STRIKE HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares with a cyan rim; 2 a cyan-blue burst 10 "
     "squares with a white core, 4 blue-white speed streaks 6 squares long shooting out sideways (2 to each side, "
     "mirrored); 3 the burst 14 squares and thinner, blue sparks at mirrored places; 4 fading blue motes.",
     row(4, 14, 14) + CENTER),
    ("q_shred", "Q 破甲：头顶的红色裂盾（敌人身上，3 秒，循环），4 帧",
     "view_buffs `league_jarvaniv_q_shred`（跟随，画在人物上面；左右对称；循环）", "10 × 12",
     "被巨龙撞击打中的敌人护甲降低：头顶浮着一面**红色的小盾牌，中间一道裂缝**，裂缝发亮，一闪一闪（英雄联盟用的就是这个红色裂盾，"
     "参考 Q_armor_shred）。**左右对称**（裂缝画成竖直的对称折线）。",
     RE,
     f"a CRACKED RED SHIELD floating over a unit's head, 4 frames, a seamless loop, {LR}: a small heater shield 7 squares "
     "wide and 8 tall in crimson with a darker red rim (a 1-square dark edge is allowed: it is a solid thing), a jagged "
     "crack running straight down its middle (a symmetric zigzag 1 square wide) glowing white-orange; 1 the crack dim; "
     "2 brighter; 3 brightest, 2 tiny red chips beside the shield at mirrored places; 4 like 2.",
     row(4, 10, 12) + CENTER),
    ("q_land", "E→Q 落地冲击：落到军旗处，挑飞周围的敌人（地上，不跟随），6 帧",
     "view_effects `league_jarvaniv_q_land`（不跟随，画在人物下面 z -1；左右对称；大图表）", "40 × 24",
     "他拖着骑枪冲到军旗那里落地，把周围的敌人挑飞：落点一道白蓝闪光，地上一圈青蓝色的冲击波往外扩（从斜上方看是扁椭圆，最大直径 34 格），"
     "几道蓝白色的光往上冲（挑飞的感觉），尘土和小石块往外、往上飞（参考 Q_GlobalTargetHit01、Q_SwirlRing_tx、DirtBits、X_Small_Stone）。"
     "**左右对称**。",
     f"{BL} and {RO}",
     f"a LANDING SHOCKWAVE on the ground seen from above at an angle, 6 frames, {LR}: 1 a white-blue flash ellipse 12 "
     "squares wide and 4 tall at the ground's middle; 2 a cyan-blue shock ring on the ground (an ellipse 20 squares wide "
     "and 7 tall with a white inner edge), 4 blue-white streaks shooting UP from it at mirrored places (the knock-up), "
     "dust puffs; 3 the ring 30 squares wide and 10 tall, small stones and dirt bits flying up and out at mirrored "
     "places; 4 the ring 34 wide and fading, the stones at their highest; 5 dust settling, stones falling; 6 faint dust.",
     row(6, 40, 24) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    # ---- E Demacian Standard
    ("e_flag", "E 德邦军旗：插在地上的军旗（地上，不跟随，8 秒），8 帧（1–2 落地、3–6 循环、7–8 消失）",
     "view_effects `league_jarvaniv_e_flag`（不跟随，画在人物上面 z 1；左右对称；大图表；3–6 帧循环铺满 8 秒）", "24 × 56",
     "他扔出的德邦军旗插进地里，站 8 秒：一根**金色的旗杆**（2 格粗、约 46 格高，顶上一个金色的翼形枪尖饰），尖饰下面一根金色横杆，"
     "横杆下面**垂着一面蓝色的旗帜**（约 14 格宽、20 格高，金边，中间一个金色的德玛西亚双翼徽记，下端剪成燕尾）。旗帜**正面朝前、"
     "直直往下垂，左右对称**（不往一边飘：游戏在红色方不会把图镜像）。第 1 帧旗从上往下落（整面旗在原位置上方 10 格，上面拖一道金光）；"
     "第 2 帧插进地面：杆脚一圈尘土和金色火花；第 3–6 帧旗帜轻轻起伏（下摆和两边微微波动，左右对称），杆脚一点淡金色的光一明一暗，"
     "第 6 帧接得回第 3 帧；第 7 帧整面旗变淡；第 8 帧只剩几粒金色光点。旗杆和旗帜是实心的东西，可以有一圈深色边"
     "（参考 E_Flag 的蓝金配色、英雄联盟里的德邦军旗）。",
     f"{GO} and {BA} and {RO}",
     f"THE DEMACIAN STANDARD planted in the ground, 8 frames (1-2 it lands, 3-6 a seamless loop while it stands, 7-8 it "
     f"vanishes), {LR}: a tall GOLD pole 2 squares thick and 46 squares tall standing upright in the middle, its foot "
     "2 squares above the cell's bottom row, a gold winged spear-tip finial on top, a gold crossbar 16 squares wide under "
     "the finial; hanging straight down from the crossbar a ROYAL BLUE BANNER 14 squares wide and 20 tall with a gold "
     "border and a gold winged emblem in its middle, its bottom cut in a swallowtail (solid things: a 1-square dark "
     "outline is allowed round the pole and the banner); 1 the standard dropping from above: the whole standard 10 "
     "squares above its place, a gold streak of light trailing above it; 2 it strikes the ground: a dust ring round its "
     "foot (an ellipse 18 squares wide and 5 tall) and gold sparks at mirrored places; 3, 4, 5, 6 standing: the "
     "banner's lower edge and sides rippling gently (symmetric ripples), a soft gold glow at the pole's foot pulsing, "
     "frame 6 flows back into frame 3; 7 the whole standard faded (lighter, fewer details); 8 only a few gold sparkles "
     "where it stood.",
     row(8, 24, 56) + CENTER),
    ("e_hit", "E 军旗砸中（目标身上），4 帧", "view_effects `league_jarvaniv_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "军旗落地砸到附近的敌人：金白色的冲击闪光，金色和蓝色的碎光往外飞（参考 E_BlastShapes）。**左右对称**。约 14 格。",
     f"{GO} and {BA}",
     f"a STANDARD IMPACT on a unit, 4 frames, {LR}: 1 a gold-white flash 5 squares; 2 a gold burst 10 squares with a "
     "white core and 4 blue shards at mirrored places; 3 the burst 14 squares and thinner, gold and blue sparks flying "
     "out; 4 fading sparks.",
     row(4, 14, 14) + CENTER),
    ("f_as", "军旗光环：友方英雄脚下的攻速光环（循环），4 帧",
     "view_buffs `league_jarvaniv_f_as`（跟随，画在人物下面；左右对称；循环）", "18 × 10",
     "站在军旗附近的友方英雄攻速提高：脚下一圈细细的金色光环（扁椭圆，近的一边亮），往上飘几粒金色和蓝色的小光点。**左右对称**，"
     "只画在脚下，不要盖住人。",
     f"{GO} and {BA}",
     f"a RALLY AURA at a champion's feet, 4 frames, a seamless loop, {LR}: a thin gold ring on the ground (an ellipse 16 "
     "squares wide and 5 tall, brighter on its near side), 4 small gold and blue motes rising from it at mirrored places, "
     "each frame a little higher (frame 4 flows back into frame 1).",
     row(4, 18, 10) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
    # ---- W Golden Aegis (cast by the watch)
    ("w_cast", "W 黄金圣盾：施放（他身上，跟随），6 帧",
     "view_effects `league_jarvaniv_w_cast`（跟随，画在他上面 z 2；左右对称；大图表）", "48 × 54",
     f"他举起骑枪召唤黄金圣盾：胸口一道金白闪光，一层金色的护盾光壳从他身上撑开（包住全身的竖椭圆，只画 1–2 格粗的边和高光，"
     f"中间身体位置留空），同时地上一圈蓝色的冲击波往外扩（减速身边的敌人）（参考 W_template_shield、W_template_shockwave_blue、"
     f"W_color-righteousfury）。**左右对称**，中间身体位置留空（{HIM}）。",
     f"{GO} and {BL}",
     f"GOLDEN AEGIS cast round a figure, 6 frames, {LR} ({HIM}): 1 a white-gold flash 10 squares at its chest; 2 a "
     "golden shield shell springing up round the whole figure (an upright ellipse outline 34 squares wide and 46 tall, "
     "1-2 squares thick, white-gold highlights on its upper left and right, the inside left empty), a blue shockwave ring "
     "starting on the ground (an ellipse 20 wide and 6 tall); 3 the shell brightest, the ground ring 36 wide and 11 tall "
     "in blue with a white inner edge; 4 the ring 46 wide and fading, gold sparks on the shell at mirrored places; 5 the "
     "shell dimmer; 6 the shell faint, a few gold motes.",
     row(6, 48, 54) + "; centered across, the figure's feet (the ring's middle) 4 squares above the cell's bottom row."),
    ("w_on", "W 圣盾持续：护盾光壳（他身上，4 秒，循环），4 帧",
     "view_buffs `league_jarvaniv_w_on`（跟随，画在他上面；左右对称；循环）", "40 × 50",
     f"护盾还在的时候：他身上一层淡淡的金色光壳（竖椭圆的边，1 格粗），边上流动着金白色的高光，一闪一闪。只画边，中间身体位置留空"
     f"（{HIM}）。**左右对称**。",
     GO,
     f"a GOLDEN SHIELD SHELL round a figure, 4 frames, a seamless loop, {LR} ({HIM}): an upright ellipse outline 34 "
     "squares wide and 46 tall, 1 square thick, pale gold, the inside empty; bright white-gold glints sliding round it (2 "
     "at mirrored places in each frame, a little higher each frame); frame 4 flows back into frame 1.",
     row(4, 40, 50) + "; centered across, the figure's feet 2 squares above the cell's bottom row."),
    ("w_hit", "W 冲击命中（敌人身上），4 帧", "view_effects `league_jarvaniv_w_hit`（跟随，画在人物上面；左右对称）", "12",
     "圣盾的冲击波打中身边的敌人：一圈蓝色的冲击光，蓝白色的火星（参考 W_template_shockwave_blue）。**左右对称**。约 12 格。",
     BL,
     f"a SHOCK HIT on a unit, 4 frames, {LR}: 1 a blue-white flash 4 squares; 2 a blue ring 8 squares with a white inner "
     "edge; 3 the ring 12 squares and thinner, blue sparks at mirrored places; 4 fading motes.",
     row(4, 12, 12) + CENTER),
    ("w_slow", "W 减速（敌人脚下，2 秒，循环），4 帧",
     "view_buffs `league_jarvaniv_w_slow`（跟随，画在人物下面；左右对称；循环）", "16 × 8",
     "被减速的敌人脚下：一圈蓝色的光环，几道往下压的蓝色短线，一明一暗。**左右对称**，只画在脚下。",
     BL,
     f"a SLOW at a unit's feet, 4 frames, a seamless loop, {LR}: a blue ring on the ground (an ellipse 14 squares wide "
     "and 4 tall), 4 short blue streaks pressing down onto it at mirrored places; 1 dim, 2 bright, 3 brightest, 4 bright.",
     row(4, 16, 8) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
    # ---- R Cataclysm
    ("r_ring", "R 天崩地裂：围住敌人的岩墙环（地上，不跟随，3.5 秒），8 帧（1–3 升起、4–7 循环、8 崩塌）",
     "view_effects `league_jarvaniv_r_ring`（不跟随，画在人物下面 z -1；左右对称；大图表；4–7 帧循环铺满 3.5 秒）", "80 × 40",
     "他从天而降砸进地面，周围升起一圈岩石墙把敌人围在里面（从斜上方看是扁椭圆：宽 72 格、高 24 格）：第 1 帧落点一道金白闪光，"
     "地面裂开一道道裂纹伸到椭圆边（参考 R_slicegroundcracks）；第 2 帧沿着整个椭圆冒出尘土和碎石；第 3 帧一圈参差不齐的**灰褐色石墙**"
     "从地里升起（一块块石头 4–6 格宽、8–12 格高，近处的石头沿着椭圆的近边，远处的沿着远边、小一点），碎石往外飞；第 4–7 帧石墙立着"
     "（每帧石缝里冒一点尘土，第 7 帧接得回第 4 帧）；第 8 帧石墙崩塌成一圈矮矮的碎石和尘土（参考 R_Wall_TUpdate、R_Ground_rock、"
     "R_Smoke、R_Wall_death_01_Dust、X_Small_Stone）。**中间留空**（他和敌人站在里面）。**左右对称**。实心的石头可以有一圈深色边。",
     f"{RO} and {GO}",
     f"CATACLYSM: A RING OF ROCK WALLS rising round an arena seen from above at an angle, 8 frames (1-3 it rises, 4-7 a "
     f"seamless loop while it stands, 8 it crumbles), {LR}: the arena an ellipse 72 squares wide and 24 tall on the "
     "ground, its middle 12 squares above the cell's bottom row, the middle left empty (units stand there); 1 a gold-white "
     "flash 10 squares at the ellipse's middle and ground cracks (jagged dark lines) running out to the ellipse at "
     "mirrored angles; 2 dust and small stones bursting up all along the ellipse; 3 a ring of jagged grey-brown stone "
     "walls risen along the whole ellipse: separate rocks 4 to 6 squares wide and 8 to 12 squares tall standing side by "
     "side round it (the near rocks along the ellipse's near edge, the far rocks along its far edge and smaller), dust "
     "puffs at their feet, stones flying out; 4, 5, 6, 7 the walls standing, thin dust trickling from a few cracks between "
     "the rocks (different each frame, frame 7 flows back into frame 4); 8 the walls crumbled into a low ring of rubble "
     "and dust. Solid rocks may have a 1-square dark outline.",
     row(8, 80, 40) + CENTER),
    ("r_hit", "R 落地伤害（敌人身上），4 帧", "view_effects `league_jarvaniv_r_hit`（跟随，画在人物上面；左右对称）", "14",
     "天崩地裂砸到敌人：金白色的闪光，灰褐色的碎石和尘土往外炸开（参考 R_tar_gather、DirtBits）。**左右对称**。约 14 格。",
     f"{RO} and {GO}",
     f"a CRUSHING IMPACT on a unit, 4 frames, {LR}: 1 a gold-white flash 5 squares; 2 a burst of grey-brown rock chips "
     "and dust 10 squares with an orange-white core; 3 the chips 14 squares out at mirrored places, dust puffs; 4 "
     "settling dust.",
     row(4, 14, 14) + CENTER),
    ("r_zap", "R 撞墙被拉回（敌人身上），4 帧", "view_effects `league_jarvaniv_r_zap`（跟随，画在人物上面；左右对称）", "12",
     "想跑出岩墙的敌人撞到墙被拉回圈里：一小团尘土加几粒金色火星。**左右对称**。约 12 格。",
     f"{RO} and {GO}",
     f"a WALL BUMP on a unit, 4 frames, {LR}: 1 a small gold-white flash 3 squares; 2 a dust puff 8 squares with gold "
     "sparks; 3 the puff 12 squares and fading, sparks at mirrored places; 4 faint dust.",
     row(4, 12, 12) + CENTER),
]
BIG_FX = ["q_land", "e_flag", "w_cast", "r_ring"]
REDO = {}
GROUPS = [
    ("a_hit p_hit", ["JarvanIV_Base_BA_HitEffect", "JarvanIV_Base_BA_sliver", "JarvanIV_Base_BA_blast_nova_bunny_04",
                     "JarvanIV_Base_BA_color-firefade", "Jarvan_Base_P_Cracks", "JarvanIV_Flare-Sun_13"]),
    ("q_hit q_land", ["JarvanIV_Base_Q_Streak", "JarvanIV_Base_Q_ball01", "JarvanIV_Base_Q_speedlines",
                      "JarvanIV_Base_Q_color-movequick", "JarvanIV_Base_Q_GlobalTargetHit01", "JarvanIV_Base_Q_SwirlRing_tx"]),
    ("q_shred", ["Jarvan_Base_Q_armor_shred", "JarvanIV_Base_Q_armordebuff"]),
    ("e_flag e_hit f_as", ["JarvanIV_Base_E_Flag", "JarvanIV_Base_E_BlastShapes", "JarvanIV_glow-soft"]),
    ("w_cast w_on w_hit w_slow", ["JarvanIV_Base_W_template_shield", "JarvanIV_Base_W_template_shockwave_blue",
                                  "JarvanIV_Base_W_color-righteousfury", "JarvanIV_Base_W_Summoner_Banish"]),
    ("r_ring r_hit r_zap", ["Jarvan_Base_R_Wall_TUpdate", "Jarvan_Base_R_Ground_rock", "JarvanIV_Base_R_slicegroundcracks",
                            "JarvanIV_Base_R_Smoke", "JarvanIV_Base_R_Wall_death_01_Dust", "JarvanIV_Base_X_Small_Stone",
                            "JarvanIV_DirtBits", "JarvanIV_Base_R_tar_gather"]),
]
FEET = 11                                             # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit / p_hit：枪尖刺中前方的目标"), ("skill", 3, "e_flag：举手把军旗扔出去，军旗落在远处"),
         ("skill_dash", 1, "E→Q：拖着骑枪冲向军旗"), ("skill_land", 1, "q_land：落到军旗那里，挑飞周围的敌人"),
         ("skill2", 4, "q_hit：Q 单放，枪刺出去"), ("skill_w", 3, "w_cast / w_on：举枪召唤黄金圣盾"),
         ("ult", 2, "R：跳起来"), ("ult", 4, "r_ring：砸下来，骑枪插进地里，岩墙环升起")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("JarvanIV_Base_", "").replace("Jarvan_Base_", "")
                   .replace("JarvanIV_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"嘉文四世 {figs[0].shape[1]}×{figs[0].shape[0]} 格（含竖着的骑枪），原版斗士 {figs[1].shape[1]}×"
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
    import rig_jarvaniv as J
    F = J.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)).save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 嘉文四世：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/jarvaniv_idle.png`：3/4 正面朝右的年轻王子，金色王冠头盔、"
      f"深蓝羽冠，金色大肩甲和胸甲，深藏青的衣服和裙甲，护膝上镶蓝宝石，手里一根很长的银白枪头骑枪）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连竖着的骑枪 {h} 格高、{w} 格宽；"
      f"**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/jarvaniv_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/jarvaniv_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。他的普攻、Q 都是骑枪刺出去的，"
      "扔军旗、Q 冲刺、R 跳跃的飞行都在他自己的动作里，**特效都画在目标身上、他身上或地上，没有飞行的弹道**。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里嘉文四世自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**普攻和战争律动是金白色**，**巨龙撞击是青蓝色的速度光**，**它的破甲是英雄联盟的红色裂盾**，"
      "**德邦军旗是金色旗杆加蓝色旗帜**，**黄金圣盾是金色光壳加地上的蓝色冲击波**，**天崩地裂是灰褐色的岩石墙和尘土**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。")
    a("> - **全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他和目标朝左时也是同一张图（军旗也一样：旗帜从横杆上正面朝前直直垂下）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 15]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `jarvaniv_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格左右对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/jarvaniv_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。"
      "中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「战争律动」 | 骑枪刺击；对同一个英雄隔一段时间的第一下按最大生命值额外伤害 | `a_hit` · `p_hit` |")
    a("| 技能 1 = E→Q「德邦军旗 → 巨龙撞击」 | 扔出军旗插在地上（砸到附近的敌人，8 秒里给身边的友方英雄加攻速），再刺出骑枪拖着自己冲到军旗那里，"
      "挑飞路上和落点周围的敌人，降低护甲 | `e_flag` · `e_hit` · `f_as` · `q_hit` · `q_shred` · `q_land` |")
    a("| 技能 2 = Q「巨龙撞击」单放 | 骑枪向前刺出一条直线，打中的敌人降低护甲 | `q_hit` · `q_shred` |")
    a("| 自动放的 W「黄金圣盾」 | 给自己一层护盾（4 秒），并减速身边的敌人 | `w_cast` · `w_on` · `w_hit` · `w_slow` |")
    a("| 大招「天崩地裂」 | 跳到敌方英雄身边砸下，周围升起一圈岩墙把敌人困住 3.5 秒；想跑出去的会被拉回来 | `r_ring` · `r_hit` · `r_zap` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：军旗、红色裂盾、岩石可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色光泽（普攻、战争律动、军旗的旗杆、黄金圣盾）", GOLD), ("青蓝速度光（巨龙撞击、圣盾的冲击波）", BLUE),
                        ("红色（破甲裂盾）", RED), ("德玛西亚蓝（军旗的旗帜）", BANNER), ("灰褐岩石和尘土（天崩地裂、落地尘土）", ROCK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：军旗砸中半径 16000，"
      "军旗光环半径 40000，黄金圣盾半径 30000，天崩地裂的岩墙环半径 36000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `jarvaniv_fx_{name}.png`：{title}\n")
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
        a(f"| `jarvaniv_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_jarvaniv_fx`（小的）和 `league_jarvaniv_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_jarvaniv.py 的 views）。")
    a("- 没有投射物画面（views_p 为空）。`q_land`、`e_flag`、`r_ring` 不跟随（地上的晚播画面）；`q_land`、`r_ring` 画在人物下面（z -1），"
      "`e_flag` 在上面（z 1）；`e_flag` 第 3–6 帧循环铺满 8 秒（f_t 480 tick），`r_ring` 第 4–7 帧铺满 3.5 秒（r_t 210 tick）。")
    a("- 用 `pixel_1x/` 切格（import_nasus_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="jarvaniv_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "jarvaniv_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/jv/fx_ref_jv.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "jarvaniv_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "jarvaniv_size.png"))
    shots_sheet(os.path.join(out, "design", "jarvaniv_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"jarvaniv_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
