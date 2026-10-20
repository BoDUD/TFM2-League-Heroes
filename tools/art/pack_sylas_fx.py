#!/usr/bin/env python3
"""Build sylas_fx_pack.zip: step 3 of Sylas's sprite - Codex draws his effects (pack_warwick_fx.py's way,
pack_rammus_fx's sheets).

    python tools/lol/fx_ref_sylas.py          # League's particle textures -> C:/t/sy_work/fxref (Riot's art, local only)
    python tools/art/pack_sylas_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name sylas_fx_redo_pack]

The pack (C:/t/sy_work/fx/sylas_fx_pack, zipped into --out, default dist/sylas_packs) holds PROMPTS.md (also written to
assets/source/sylas/PROMPTS_FX.md), design/sylas_idle.png (his design at 4x: assets/source/sylas/hd/idle.png once
step 1 is in, else step 0's A cut to the count), design/sylas_size.png (the design brought to game pixels at 4x on the
arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png (League's own particle
textures for Sylas grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_sylas.py, both builds): view_projectiles q_chain, e_chain,
r_hook (+ the add-on's r2_arrow); view_effects a_hit, p_spin, p_hit, w_hit, w_heal, q_hit, q_cross, q_hit2, e_hit,
r_steal, r_got, r2_boom, r2_hit (+ the add-on's r2_slam, r2_song, r2_blink); view_buffs p_1, q_slow, r_have (the add-on's
r2_slow reuses q_slow). League's colours: his chains are GOLD, his magic BLUE-VIOLET LIGHTNING with white cores (the
passive, Kingslayer, the steal), Chain Lash's burst a GOLD-ORANGE flare. Red side: the client never mirrors an effect
picture, so every hit, buff and ground picture is symmetric left to right; a projectile's picture turns with its flight
(drawn pointing right, so it must be symmetric top to bottom).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/sy_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "sylas", "PROMPTS_FX.md")
SRC = os.path.join(ROOT, "assets", "source", "sylas")
NAME = "sylas_fx_pack"
PPU = 1.2

GOLD = "#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408"        # the chains
BOLT = "#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C"        # his blue-violet lightning
FLARE = "#FFFFFF, #FFF2B0, #FFC040, #FF8A1A, #C24A0A, #5C1A04"       # Chain Lash's burst
HEAL = "#FFFFFF, #E2F4FF, #A8DCFF, #6AA8F0, #3A64B4, #1C2C5C"        # Kingslayer's heal, the song
GO = f"a gold chain ramp ({GOLD})"
BO = f"a blue-violet lightning ramp ({BOLT})"
FL = f"a gold-orange flare ramp ({FLARE})"
HE = f"a pale sky-blue ramp ({HEAL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: drawn pointing "
      "RIGHT, upside down when it flies left)")
HIM = ("the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without "
       "his chains")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack + the passive
    ("a_hit", "普攻：锁链打中，3 帧", "view_effects `league_sylas_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "他甩链打中目标：一团金色的火花，中间一小道蓝紫色的电光（参考 ba_hit_directional2、ba_hit_tar_muzzle、hit_spark）。**左右对称**，3 帧。",
     GO + " and " + BO,
     "A CHAIN STRIKE ON A TARGET, 3 frames, " + LR + ": 1 a white flash 6 squares across with four short gold rays; 2 a gold "
     "spark burst 12 squares across, a small blue-violet lightning zigzag through its middle (mirrored); 3 a few gold sparks "
     "flying out and fading.", row(3, 16, 16) + CENTER),
    ("p_spin", "被动 破敌禁法：挥链横扫一圈（他身边，跟随），5 帧",
     "view_effects `league_sylas_p_spin`（跟随他，画在人物下面 z -1；左右对称；大图表）", "60 × 30",
     "有层数时普攻变成挥链横扫：一圈金色的锁链带着蓝紫色的闪电在他腰部高度绕他转一圈（从斜上方看是扁椭圆），地上一圈蓝色的光（参考 p_slash、"
     "p_swipe_highlight、p_lightning、z_chains）。**他站在中间不画人，只画外圈**，**左右对称**，5 帧。",
     GO + " and " + BO,
     "A WHIRL OF CHAINS ROUND A MAN, 5 frames, " + LR + " (" + HIM + ", his body area left EMPTY): a flat ellipse 56 wide and "
     "16 tall drawn as a ring of GOLD CHAIN LINKS (each link 2x2 with a hole) at his waist height, blue-violet lightning "
     "crackling along it: 1 the ring's two front halves sweeping in from both sides; 2 the whole ring closed, bright, white "
     "lightning on its front; 3 the ring brightest, short lightning bolts shooting out at mirrored places; 4 the links "
     "fading into a blue-violet streak ring; 5 only sparks.",
     row(5, 60, 30) + "; centered across, the ring's middle 12 squares above the cell's bottom row."),
    ("p_hit", "被动：横扫打中的敌人，3 帧", "view_effects `league_sylas_p_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "横扫打中的每个敌人身上一小团蓝紫色的电光（参考 p_hit_electricity、p_hit_core、p_hit_sparks）。**左右对称**，3 帧。", BO,
     "A LIGHTNING CRACKLE ON A TARGET, 3 frames, " + LR + ": 1 a white core 4 squares across; 2 a blue-violet star of 6 "
     "zigzag bolts 12 squares across; 3 the bolts broken into sparks, fading.", row(3, 14, 14) + CENTER),
    ("w_hit", "W 弑君突刺：刺中（目标身上），4 帧", "view_effects `league_sylas_w_hit`（跟随目标，z 2；左右对称）", "20 × 20",
     "突刺刺中英雄：一团蓝紫色的魔法爆开，中间白光，四周一圈闪电和碎片（参考 w_hit_electricity、w_hit_shockwave、w_hit_tar_muzzle）。"
     "**左右对称**，4 帧。", BO,
     "A MAGIC STAB BURST ON A TARGET, 4 frames, " + LR + ": 1 a white flash 6 squares across; 2 a blue-violet burst 16 "
     "squares across with a white core and a thin ring; 3 lightning bolts and little petricite shards flying out at "
     "mirrored places; 4 sparks and shards fading.", row(4, 20, 20) + CENTER),
    ("w_heal", "W：回血（他身上，跟随），5 帧", "view_effects `league_sylas_w_heal`（跟随他，z 3；左右对称）", "34 × 44",
     "突刺回血：从他脚下升起淡蓝色的光丝，往他胸口聚过去，最后一闪（参考 w_glow、w_swirl、w_energy_trail）。**他站在中间不画人，只画两边**，"
     "**左右对称**，5 帧。", HE,
     "A HEAL ROUND A MAN, 5 frames, " + LR + " (" + HIM + ", his body area left EMPTY): 1 a thin pale-blue ellipse on the "
     "ground under him (28 wide, 6 tall); 2 six thin wisps of light rising at his left and right; 3 the wisps higher, curving "
     "in toward his chest (two thirds up); 4 the wisps meeting in the middle with a white flash; 5 only the fading ellipse "
     "and two sparks.", row(5, 34, 44) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
    # ---- Q Chain Lash
    ("q_chain", "Q 锁链鞭击：飞出去的两条锁链（弹道，循环），3 帧",
     "view_projectiles `league_sylas_q_chain`（随飞行方向转，画成**朝右**；上下对称；循环）", "30 × 10",
     "Q 甩出的两条锁链交叉着往前飞：两条金色的锁链一上一下拧在一起，最前面一道蓝紫色的电光（参考 z_chains、z_chains_glow、q_electricity）。"
     "**画成朝右飞**，**上下对称**（往左飞时游戏会把它转个方向），3 帧循环。", GO + " and " + BO,
     "TWO CHAINS FLYING RIGHT, 3 frames, a seamless loop, " + TB + ": two GOLD CHAINS (links 2x2 with a hole) stretched "
     "horizontally, one above the other, twisting round each other so they cross at two places (mirrored top and bottom), "
     "their front ends at the right joined by a small bright blue-violet lightning tip; the twist shifts one link each "
     "frame.", row(3, 30, 10) + "; the chains across the cell's middle row."),
    ("q_hit", "Q：锁链抽中，3 帧", "view_effects `league_sylas_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "锁链抽中路上的敌人：一道金色的 X 形火花（参考 q_hit_flash、q_hit_wispy、q_impact_target）。**左右对称**，3 帧。", GO,
     "A LASH HIT, 3 frames, " + LR + ": 1 a white flash 4 squares across; 2 a gold X of two crossed streaks 12 squares "
     "across; 3 the X fading into sparks.", row(3, 14, 14) + CENTER),
    ("q_cross", "Q：交叉点蓄力、爆炸（地上，不跟随），10 帧",
     "view_effects `league_sylas_q_cross`（落点，不跟随，画在人物下面 z -1；左右对称；大图表）", "40 × 40",
     "两条锁链交叉在地上（从斜上方看的 X），交叉点越来越亮（约 0.6 秒，前 6 帧），然后爆炸：金橙色的光柱从交叉点冲起来、一圈冲击波（后 4 帧）"
     "（参考 q_ground_impact、q_impact_glow、q_fb_explosion_centerflare、q_glowball_color、q_explosion_ring）。**左右对称**，10 帧。",
     GO + " and " + FL,
     "A CHAIN CROSSING THAT BURSTS, 10 frames, " + LR + ": the lower half of the cell is the ground seen from above at a "
     "slant: 1 two gold chain lines lying on the ground in a flat X (36 wide, 12 tall) with a small gold glow where they "
     "cross; 2-6 the crossing glow growing brighter each frame (a gold-white diamond, 4 then 10 squares wide), sparks "
     "crawling along the chains; 7 a bright white-gold flash at the crossing, the chains glowing white; 8 a gold-orange "
     "burst column 14 wide rising 24 squares from the crossing, a flat orange ring on the ground 36 wide; 9 the column "
     "breaking into flares, the ring wider and thinner; 10 only embers and the fading ring.",
     row(10, 40, 40) + "; centered across, the crossing 10 squares above the cell's bottom row."),
    ("q_hit2", "Q：爆炸打中，3 帧", "view_effects `league_sylas_q_hit2`（跟随目标，z 2；左右对称）", "16 × 16",
     "爆炸打中的敌人身上一团金橙色的火花（参考 q_hit_flash、q_fb_explosion_centerflare）。**左右对称**，3 帧。", FL,
     "A FLARE HIT, 3 frames, " + LR + ": 1 a white core 5 squares across; 2 a gold-orange burst 14 squares across with "
     "short rays; 3 embers, fading.", row(3, 16, 16) + CENTER),
    # ---- E Abscond / Abduct
    ("e_chain", "E 强掳：甩出去的锁链（弹道，循环），3 帧",
     "view_projectiles `league_sylas_e_chain`（随飞行方向转，画成**朝右**；上下对称；循环）", "24 × 8",
     "E 甩出的一条锁链：一条拉直的金色锁链，最前面是一个发蓝光的禁魔石锁扣（参考 e_mis_tip、e_trail、z_chain）。**画成朝右飞**，**上下对称**，"
     "3 帧循环。", GO + " and " + BO,
     "ONE CHAIN FLYING RIGHT, 3 frames, a seamless loop, " + TB + ": a straight GOLD CHAIN of links (2x2 with a hole) "
     "across the cell, at its right end a pale stone shackle tip glowing blue-violet (6 squares long, pointed), a faint "
     "blue streak along the chain behind it; the links shift one square each frame.",
     row(3, 24, 8) + "; across the cell's middle row."),
    ("e_hit", "E：锁链缠住、击飞（目标身上），4 帧", "view_effects `league_sylas_e_hit`（跟随目标，z 2；左右对称）", "22 × 30",
     "锁链缠住被拉的英雄、把他击飞：一圈金色的锁链绕在他腰上，下面几道往上的白色气流（击飞），蓝紫色火花（参考 e_hit_spin、e_prison_mult、"
     "e2_swipe）。**被缠的人站在中间不画，只画锁链和气流**，**左右对称**，4 帧。", GO + " and " + BO,
     "A CHAIN SNARE AND KNOCK-UP ON A CHAMPION, 4 frames, " + LR + " (" + CHAMP + ", the body area left EMPTY): 1 a gold "
     "chain ring (an ellipse 20 wide and 6 tall) snapping round the waist with a white flash; 2 the ring bright, blue-violet "
     "sparks at its sides, three short white UP streaks under the feet; 3 the streaks longer, the ring tight; 4 the ring "
     "fading into sparks.", row(4, 22, 30) + "; centered across, the waist ring 12 squares above the cell's bottom row."),
    # ---- R Hijack
    ("r_hook", "R 其人之道：偷大招的锁链（弹道，循环），3 帧",
     "view_projectiles `league_sylas_r_hook`（随飞行方向转，画成**朝右**；上下对称；循环）", "26 × 10",
     "R 甩出的锁链：一条金色锁链，前面一个发蓝紫光的爪形锁扣，链子周围缠着闪电（参考 r_hookmis_head、r_mis_shackles、r_lightning_beam）。"
     "**画成朝右飞**，**上下对称**，3 帧循环。", GO + " and " + BO,
     "A STEALING CHAIN FLYING RIGHT, 3 frames, a seamless loop, " + TB + ": a straight GOLD CHAIN of links across the cell, "
     "at its right end a glowing blue-violet claw-shaped head (two prongs, one up and one down, mirrored, 7 squares long), "
     "a thin blue-violet lightning zigzag wrapping the chain (mirrored above and below); the lightning flickers each frame.",
     row(3, 26, 10) + "; across the cell's middle row."),
    ("r_steal", "R：锁住、夺走大招（被偷的英雄身上），6 帧", "view_effects `league_sylas_r_steal`（跟随目标，z 2；左右对称）", "26 × 40",
     "被偷的英雄身上：两道金色的锁链交叉缠住他，一团蓝紫色的能量被从他胸口扯出来、往上飘走（参考 r_hit_electricity、r_swirl_01、r_bits）。"
     "**被偷的人站在中间不画**，**左右对称**，6 帧。", GO + " and " + BO,
     "A HIJACK ON A CHAMPION, 6 frames, " + LR + " (" + CHAMP + ", the body area left EMPTY except the energy): 1 two gold "
     "chains crossing in an X over the body with a white flash; 2 the X bright, blue-violet lightning crawling on it; 3 a "
     "glowing blue-violet orb (6 squares) torn out at chest height in the middle; 4 the orb rising 8 squares, trailing "
     "sparks; 5 the orb at the top of the cell, the chains fading; 6 only sparks.",
     row(6, 26, 40) + "; centered across, the chest 22 squares above the cell's bottom row."),
    ("r_got", "R：拿到夺来的大招（他身上，跟随），5 帧", "view_effects `league_sylas_r_got`（跟随他，z 3；左右对称）", "32 × 26",
     "他拿到夺来的大招：两团蓝紫色的能量从两边飞进他两只镣铐，在胸前汇成一个亮点一闪（参考 r_hand_smokeybits、r_return_lightning、"
     "r_lightning_cas）。**他站在中间不画人**，**左右对称**，5 帧。", BO,
     "A STOLEN POWER COMING HOME, 5 frames, " + LR + " (" + HIM + ", his body area left EMPTY): 1 two blue-violet sparks at "
     "the cell's left and right edges at hand height; 2 the sparks flying in, trailing lightning; 3 both reaching his hands "
     "(8 squares from the middle each) with small white flashes; 4 a bright white-violet point in the middle at chest "
     "height with two short arcs; 5 fading.", row(5, 32, 26) + CENTER),
    ("r2_boom", "R：放出夺来的大招（落点，不跟随），7 帧",
     "view_effects `league_sylas_r2_boom`（落点，不跟随，z -1；左右对称；大图表）", "48 × 48",
     "第二次 R 在目标处爆发：一道蓝紫色的闪电从天上劈下来，落地炸开一圈金色和蓝紫色的冲击波（参考 r_lightning_beam_bright、r_electricity、"
     "r_timer、w_shockwave_sharp）。**左右对称**（闪电劈下来的那一道画在正中、竖直），7 帧。", BO + " and " + GO,
     "A STOLEN ULTIMATE STRIKING DOWN, 7 frames, " + LR + ": 1 a thin white-violet line falling from the cell's top to the "
     "ground point (8 squares above the bottom, middle); 2 a thick blue-violet lightning bolt 6 wide straight down the "
     "middle with mirrored side branches, a white flash at the ground; 3 a blast 30 squares across at the ground point, "
     "white core, a flat gold ring on the ground 40 wide; 4 the blast 40 across, lightning arcs spraying out at mirrored "
     "places; 5 the ring 46 wide and thin, the blast breaking up; 6 sparks and wisps; 7 fading.",
     row(7, 48, 48) + "; centered across, the ground point 8 squares above the cell's bottom row."),
    ("r2_hit", "R：爆发打中，3 帧", "view_effects `league_sylas_r2_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "被夺来的大招打中的敌人身上一团蓝紫色的电光（参考 r_hit_electricity）。**左右对称**，3 帧。", BO,
     "A HEAVY LIGHTNING HIT, 3 frames, " + LR + ": 1 a white flash 6 squares across; 2 a blue-violet burst 16 squares "
     "across with four zigzag bolts; 3 sparks, fading.", row(3, 18, 18) + CENTER),
    # ---- buffs
    ("p_1", "被动：有层数（他两只镣铐上，buff，循环），4 帧", "view_buffs `league_sylas_p_1`（跟随他，z 3；左右对称；循环）", "40 × 24",
     "破敌禁法存着层数时：他两只镣铐上噼啪跳着蓝紫色的小电光（参考 p_ready_buff、p_lightning、passive_scroll）。**他站在中间不画人，只在两只"
     "手的位置画电光**，**左右对称**，4 帧循环。", BO,
     "CRACKLING MANACLES, 4 frames, a seamless loop, " + LR + " (" + HIM + ", his body area left EMPTY): at his two hands "
     "(14 squares left and right of the middle, 10 squares above the cell's bottom row) small blue-violet lightning sparks "
     "(4-6 squares) jumping and flickering, a white point in each; the sparks change shape each frame.",
     row(4, 40, 24) + "; centered across."),
    ("q_slow", "Q：减速（目标脚下，buff，循环），4 帧", "view_buffs `league_sylas_q_slow`（跟随目标，z -1；左右对称；循环）", "20 × 8",
     "被锁链减速的敌人脚下一圈暗金色的光，几节锁链的影子在上面慢慢转（参考 q_ringmult、q_ground）。**左右对称**，4 帧循环。", GO,
     "A SLOW RING under a target's feet, 4 frames, a seamless loop, " + LR + ": a dim gold ellipse 18 wide and 5 tall on the "
     "ground, a few dark-gold chain-link marks along its rim shifting one square round each frame (mirrored).",
     row(4, 20, 8) + CENTER),
    ("r_have", "R：握着夺来的大招（他头顶上，buff，循环），4 帧", "view_buffs `league_sylas_r_have`（跟随他，z 3；左右对称；循环）",
     "18 × 12",
     "他握着夺来的大招时头顶上漂着一个蓝紫色的发光印记（菱形的禁魔石符文，四周一圈小电光）（参考 r_timer_mult、r_swirl_01）。"
     "**画在他头顶上方**，**左右对称**，4 帧循环。", BO,
     "A STOLEN-POWER SIGIL over a head, 4 frames, a seamless loop, " + LR + ": a glowing blue-violet diamond rune 8 squares "
     "wide in the middle with a white core, small lightning sparks circling it (mirrored); it bobs one square up and down.",
     row(4, 18, 12) + CENTER),
    # ---- the add-on's stolen ults
    ("r2_arrow", "附加包 R（射手）：贯穿长箭（弹道，循环），3 帧",
     "view_projectiles `league_sylas_r2_arrow`（随飞行方向转，画成**朝右**；上下对称；循环）", "28 × 8",
     "偷到射手的大招：一支蓝紫色和金色的能量长箭朝右飞，尾巴拖着光（参考 r_beam_trail_vert、r_trail_04）。**上下对称**，3 帧循环。",
     BO + " and " + GO,
     "A STOLEN ENERGY ARROW FLYING RIGHT, 3 frames, a seamless loop, " + TB + ": a long arrow of blue-violet energy with a "
     "white-gold pointed head at the right (8 squares long), its shaft 2 squares thick, a tapering trail of gold sparks to "
     "the left; the trail flickers each frame.", row(3, 28, 8) + "; across the cell's middle row."),
    ("r2_slam", "附加包 R（近战）：落地重砸（落点，不跟随），6 帧",
     "view_effects `league_sylas_r2_slam`（不跟随，z -1；左右对称；大图表）", "56 × 24",
     "偷到近战的大招：他跃起砸地，地上一圈金色的裂纹和蓝紫色的冲击波往外扩（参考 q_ground_impact、w_buff_ground、shards_2x2）。**左右对称**，"
     "6 帧。", GO + " and " + BO,
     "A GROUND SLAM, 6 frames, " + LR + ": 1 a white flash on the ground point; 2 gold cracks running out from it in a flat "
     "star (mirrored), a blue-violet ring 20 wide; 3 the ring 36 wide, rock chips thrown up at mirrored places; 4 the ring "
     "50 wide, thin; 5 the cracks glowing dim, dust; 6 fading.",
     row(6, 56, 24) + "; centered across, the ground point 8 squares above the cell's bottom row."),
    ("r2_song", "附加包 R（辅助）：治疗之歌（他身边，跟随），6 帧",
     "view_effects `league_sylas_r2_song`（跟随他，z -1；左右对称；大图表）", "60 × 44",
     "偷到辅助的大招：他脚下一大圈淡蓝色的光环往外扩，几个音符和光点往上飘（参考 w_buff_ground、w_glow）。**他站在中间不画人**，**左右对称**，6 帧。",
     HE,
     "A HEALING SONG ROUND A MAN, 6 frames, " + LR + " (" + HIM + ", his body area left EMPTY): 1 a pale-blue ellipse on the "
     "ground under him 20 wide; 2 the ellipse 40 wide, four small music notes rising at mirrored places; 3 the ellipse 56 "
     "wide, the notes higher with light motes; 4 the notes at the cell's top; 5 the ellipse thinning; 6 fading.",
     row(6, 60, 44) + "; centered across, the ellipse's middle 4 squares above the cell's bottom row."),
    ("r2_blink", "附加包 R（刺客）：闪身（他身上，跟随），4 帧", "view_effects `league_sylas_r2_blink`（跟随他，z 3；左右对称）",
     "24 × 40",
     "偷到刺客的大招：他闪到目标身边，身上一团蓝紫色的烟和残影散开（参考 r_stealth_into_swooshies_rgba、r_smokeerode）。**他站在中间不画人**，"
     "**左右对称**，4 帧。", BO,
     "A BLINK OF SMOKE ROUND A MAN, 4 frames, " + LR + " (" + HIM + ", his body area left EMPTY): 1 a white-violet flash "
     "outline round where he stands; 2 blue-violet smoke puffs bursting out at his left and right; 3 the puffs bigger and "
     "darker, curling up; 4 fading wisps.", row(4, 24, 40) + "; centered across, his feet on the cell's bottom row."),
]
BIG_FX = ["p_spin", "q_cross", "r2_boom", "r2_slam", "r2_song"]
P_ = "sylas_base_"
GROUPS = [
    ("a_hit", [P_ + "ba_hit_directional2", P_ + "ba_hit_tar_muzzle", P_ + "hit_spark", P_ + "ba_swipe1"]),
    ("p_spin p_hit p_1", [P_ + "p_slash", P_ + "p_swipe_highlight", P_ + "p_lightning", P_ + "p_hit_electricity",
                          P_ + "p_hit_core", P_ + "z_chains"]),
    ("w_hit w_heal", [P_ + "w_hit_electricity", P_ + "w_hit_shockwave", P_ + "w_hit_tar_muzzle", P_ + "w_glow",
                      P_ + "w_swirl"]),
    ("q_chain q_hit", [P_ + "z_chains", P_ + "z_chains_glow", P_ + "q_electricity", P_ + "q_hit_flash", P_ + "q_impact_target"]),
    ("q_cross q_hit2", [P_ + "q_ground_impact", P_ + "q_impact_glow", P_ + "q_fb_explosion_cent", P_ + "q_glowball_color",
                        P_ + "q_explosion_ring"]),
    ("e_chain e_hit", [P_ + "e_mis_tip", P_ + "e_trail", P_ + "z_chain", P_ + "e_hit_spin", P_ + "e_prison_mult"]),
    ("r_hook r_steal r_got", [P_ + "r_hookmis_head", P_ + "r_mis_shackles", P_ + "r_lightning_beam", P_ + "r_hit_electricity",
                              P_ + "r_swirl_01", P_ + "r_return_lightning"]),
    ("r2_boom r2_hit r_have", [P_ + "r_lightning_beam_bright", P_ + "r_electricity", P_ + "r_timer", P_ + "w_shockwave_sharp",
                               P_ + "r_timer_mult"]),
]


def lp(path):
    return RF.lp(path)


def design():
    """His design: step 1's idle once it is in, else step 0's A brought to the 46 rows (pack_sylas_model's target)."""
    p = os.path.join(SRC, "hd", "idle.png")
    if os.path.exists(lp(p)):
        return np.asarray(Image.open(lp(p)).convert("RGBA"))
    import pixel_down as PD
    from review_sylas_size import body_height
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 46 / body_height(d), (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    op = g[..., 3] > 0
    return g[np.ix_(np.any(op, 1), np.any(op, 0))]


def design_sheet(path, d):
    bg = Image.new("RGBA", (d.shape[1] * 4 + 32, d.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def size_sheet(path, d):
    """The design at game pixels (PPU squares a game pixel) beside the base fighter, 4x, a 10-px ruler."""
    import tfm2_ase as T
    im = Image.fromarray(d).resize((round(d.shape[1] / PPU), round(d.shape[0] / PPU)), Image.NEAREST)
    figs = [np.asarray(im)]
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
    dr = ImageDraw.Draw(img)
    dr.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        dr.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        dr.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    dr.text((8, 36), f"塞拉斯 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
            fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 解脱者 塞拉斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/sylas_idle.png`：3/4 正面朝右、赤裸上身的男人，黑色长发、短黑胡子，"
      f"深青灰的高领围巾和金色护颈片，两只很大的白色石头镣铐，金色的锁链拖在地上，深青绿长裤）。他在游戏里是**高清**的（每个游戏格子里 "
      f"{PPU}×{PPU} 个细像素），约 {h} 格高、{w} 格宽（连锁链）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sylas_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里塞拉斯自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**他的锁链是金色的**，**他的魔法（被动、突刺、偷大招）是蓝紫色的闪电，白色的芯**，"
      "**锁链鞭击的爆炸是金橙色的**，**回血是淡蓝色的**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**弹道（q_chain、e_chain、r_hook、"
      "r2_arrow）画成朝右飞、严格上下对称**（游戏会按飞行方向转它，往左飞时整张倒过来）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sylas_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/sylas_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「破敌禁法」和 W「弑君突刺」在里面） | 甩链；放完技能后挥链横扫一圈；每隔一阵对英雄的普攻变成突刺、回血 | `a_hit` · "
      "`p_spin` · `p_hit` · `p_1` · `w_hit` · `w_heal` |")
    a("| 技能 1 = Q「锁链鞭击」 | 两条锁链交叉在目标处，减速，延迟后交叉点爆炸 | `q_chain` · `q_hit` · `q_slow` · `q_cross` · `q_hit2` |")
    a("| 技能 2 = E「潜掠/强掳」 | 突进，再甩出锁链，命中的英雄被击飞、把自己拉过去 | `e_chain` · `e_hit` |")
    a("| 大招「其人之道」 | 第一次：锁链锁住英雄、夺走大招；第二次：在目标处放出夺来的大招 | `r_hook` · `r_steal` · `r_got` · `r_have` · "
      "`r2_boom` · `r2_hit` |")
    a("| 附加包的大招（按被偷的人的类别） | 射手 = 贯穿长箭，近战 = 跃起重砸，辅助 = 治疗之歌，刺客 = 闪身重击（法师 = 上面的 r2_boom） | "
      "`r2_arrow` · `r2_slam` · `r2_song` · `r2_blink` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、闪电、烟、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈"
      "边**（锁链的链环可以有一圈暗金色的边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色（锁链）", GOLD), ("蓝紫色（闪电、魔法）", BOLT), ("金橙色（锁链鞭击的爆炸）", FLARE),
                        ("淡蓝色（回血、治疗之歌）", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（冲击波、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、他身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 26000，锁链鞭击的射程 "
      "60000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sylas_fx_{name}.png`：{title}\n")
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
        a(f"| `sylas_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_sylas_fx`（小的）和 `league_sylas_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_sylas.py 的 views；p_1 / q_slow / r_have 绑在同名 buff 上，附加包的 r2_slow 用 q_slow 的图）。")
    a("- 打中、身上、地上的断言左右对称，弹道断言上下对称；`p_spin`、`q_cross`、`r2_boom`、`r2_slam`、`r2_song`、`q_slow` 画在他下面"
      "（z -1），`w_heal`、`r_got`、`r_have`、`p_1`、`r2_blink` 在上面（z 3）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（链环的暗金边保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sylas_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "sylas_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_sylas.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = design()
    design_sheet(os.path.join(out, "design", "sylas_idle.png"), d)
    shape = size_sheet(os.path.join(out, "design", "sylas_size.png"), d)
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sylas_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[2].startswith("view_projectiles") else "left-right"} for x in FX],
                  f, ensure_ascii=False, indent=1)
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
