#!/usr/bin/env python3
"""Build heimerdinger_fx_pack.zip: step 3 of Heimerdinger's sprite - Codex draws his effects (pack_shyvana_fx.py's way;
the user, 2026-10-21: 「趁着这段时间把特效包整理好了给我」, while Codex draws the pose packs).

    python tools/lol/fx_ref_heimerdinger.py    # League's particle textures -> C:/t/hd_work/fxref (Riot's art, local only)
    python tools/art/pack_heimerdinger_fx.py [--no-zip] [--out DIR] [--only a_hit,t_hit --name heimerdinger_fx_redo_pack]

The pack (C:/t/hd_work/fx/heimerdinger_fx_pack, zipped into --out, default dist/heimerdinger_packs) holds PROMPTS.md (also
written to assets/source/heimerdinger/PROMPTS_FX.md), design/heimerdinger_designs.png (him and both turrets at 4x, the
designs' own squares at PPU 1.5), design/heimerdinger_size.png (the three at game size, 4x, on the arena colour with the
ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png (League's own particle textures for him and his
turrets, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_heimerdinger.py) and what the frames and the add-on draw:
view_projectiles a_bolt, w_rocket, e_grenade, re_grenade (the grenades' lobs get pictures), the add-on's turret shots
t_shot, t_beam_line, x_shot; view_effects a_hit, w_hit, t_hit, t_beam, e_blast, e_hit, r_up, re_blast, x_hit, x_beam;
view_buffs e_slow (x_slow shares it), haste; drawn into the frames (bake / rig): w_flash (the crane's launch, attack_w),
t_dust / t_muzzle / t_gone and x_dust / x_muzzle / x_gone (the turrets' own tags: deploy, each shot, breaking),
dead_burst (the backpack bursting). League's colours: his hextech is BLUE-WHITE electricity (the bolt, E's storm, R's
upgrade, the apex turret), the turret's shots and W's rockets ORANGE-GOLD fire with grey smoke, the charged beams BLUE, the
CH-3X grenade RED; the turret's deploy a golden hexagon. Red side: the client never mirrors an effect picture, so every
hit, buff, ground, turret and body picture is symmetric left to right; the projectiles are turned with their flight, so
they are drawn flying right and symmetric top to bottom (the grenades round, safe either way); w_flash points forward
(right) and is baked into his frames, so it needs no symmetry.
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
import pixel_down as PD  # noqa: E402

TMP = "C:/t/hd_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "heimerdinger", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd")
NAME = "heimerdinger_fx_pack"
PPU = 1.5

HEX = "#FFFFFF, #D8FBFF, #8CEBFF, #38C4F0, #1A86D8, #1A4CA0, #102860"      # hextech blue-white electricity
BOLT = "#FFFFFF, #E2F4FF, #9FD8FF, #5C9CFF, #4A58E0, #3A2CA0"              # E's lightning: white to blue-violet
FIRE = "#FFFFFF, #FFF4B8, #FFD24A, #FF9A22, #E8561A, #A82A14"              # the turret's shots, W's rockets, the death
GOLD = "#FFFFFF, #FFF0B0, #FFC94A, #E89A20, #A8641A"                       # the turret's deploy hexagon, the passive
RED = "#FFFFFF, #FFE0D0, #FF8A6A, #F23A2A, #B01A22, #6A0E18"               # the CH-3X lightning grenade
SMOKE = "#D2CEC8, #A09A94, #6E6862, #46423E"                               # smoke (the turret's breaking, the rockets)
METAL = "#E0E2EA, #A6A8B4, #6C6E7C, #3E404C"                               # nuts, screws, the grenade's shell
HX = f"a hextech blue-white electric ramp ({HEX})"
BO = f"a white to blue-violet lightning ramp ({BOLT})"
FI = f"an orange-gold fire ramp ({FIRE})"
GO = f"a golden light ramp ({GOLD})"
RE = f"a red lightning ramp ({RED})"
SM = f"a grey smoke ramp ({SMOKE})"
ME = f"a steel grey metal ramp ({METAL})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
ROUND = ("ROUND and SYMMETRIC both left to right and top to bottom in every frame, square for square (the game turns it "
         "with its arc)")
FWD = "pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry)"
CENTER = RF.CENTER
row = RF.row
HIM = "he stands in the middle, not drawn: 34 squares wide and 36 tall"
TUR = "the turret stands in the middle, not drawn: 26 squares wide and 20 tall, its muzzle facing the viewer"
APEX = "the apex turret stands in the middle, not drawn: 25 squares wide and 30 tall, its muzzle facing the viewer"
GROUND = ("a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the "
          "feet are")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_bolt", "普攻：海克斯电光弹，飞行中循环 4 帧", "view_projectiles `league_heimerdinger_a_bolt`（朝飞行方向转）", "10 × 6",
     "扳手射出的一小团海克斯电光：白色的芯、蓝色的电光，后面拖一小段噼啪的电弧（参考 aa_tar、z_small_lighting）。**朝右飞、上下对称**，循环 4 帧。",
     HX,
     "A SMALL HEXTECH ENERGY BOLT, looping 4 frames, " + TB + ": a white core 2 squares across in a blue glow, a short "
     "crackling blue tail of 4-5 squares behind it, two tiny arcs flickering above and below the tail (mirrored).",
     row(4, 10, 6) + CENTER),
    ("a_hit", "普攻：电光打中目标，3 帧", "view_effects `league_heimerdinger_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "电光打中：一个白色四角星闪一下，周围迸出几道蓝色小电弧和火花（参考 aa_tar、z_impact_anim）。**左右对称**，3 帧。",
     HX,
     "AN ELECTRIC HIT, 3 frames, " + LR + ": 1 a white four-pointed star flash 7 squares across with a blue rim; 2 the star "
     "shrinking, four short blue zigzag arcs and sparks flying out diagonally; 3 only fading sparks.",
     row(3, 12, 12) + CENTER),
    # ---- W Hextech Micro-Rockets (every third attack, from the backpack crane)
    ("w_rocket", "W 海克斯科技微型导弹：飞行中的小导弹，循环 3 帧", "view_projectiles `league_heimerdinger_w_rocket`（朝飞行方向转）",
     "12 × 6",
     "一枚小导弹：红白相间的弹身、淡色弹头、红色尾翼，尾巴喷出橙金色的火焰和一小团灰烟（参考 hextech_missile、w_missile_flames、"
     "w_missile_glow、w_aftersmoke）。**朝右飞、上下对称**，循环 3 帧（火焰一闪一闪）。",
     FI + ", " + SM + " and white and red for the rocket's body",
     "A TINY ROCKET, looping 3 frames, " + TB + ": a slim rocket 6 squares long (a pale nose on the right, a white body "
     "with a red band, two small red fins at its tail), an orange-gold flame jet of 3-4 squares behind it flickering from "
     "frame to frame, and a small grey smoke puff at the end of the flame.",
     row(3, 12, 6) + CENTER),
    ("w_flash", "W：机械臂发射导弹的火光，3 帧（画进他的动作帧）", "画进 attack_w 帧（机械臂爪子处；朝右）", "10 × 10",
     "机械臂的爪子发射导弹那一下：一团橙金色的火光往前喷，后面冒一小团灰烟。**朝右画**（画进他的动作帧，不用对称），3 帧：亮、散、烟。",
     FI + " and " + SM,
     "A LAUNCH FLASH, 3 frames, " + FWD + ": 1 a bright orange-gold burst 6 squares across with a white core, pointing to "
     "the right; 2 the burst fading to orange, a grey smoke puff growing on its left; 3 only the grey smoke puff.",
     row(3, 10, 10) + CENTER),
    ("w_hit", "W：导弹打中目标的小爆炸，4 帧", "view_effects `league_heimerdinger_w_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "导弹炸开：一团橙金色的火球，散出几点火星，然后变成灰烟（参考 w_tar_bubble、heimer_base_death_fireball）。**左右对称**，4 帧。",
     FI + " and " + SM,
     "A SMALL ROCKET EXPLOSION, 4 frames, " + LR + ": 1 a white-yellow flash 6 squares across; 2 an orange fireball 10 "
     "squares across with a thin orange ring round it; 3 the fireball breaking into orange sparks and grey smoke; 4 a "
     "fading grey smoke puff.",
     row(4, 14, 14) + CENTER),
    # ---- Q H-28G Evolution Turret
    ("t_dust", "Q 进化炮台：炮台落地展开，地上一圈，5 帧（画进炮台出现的动画）", "画进炮台 t_turret 动画的开头（脚下，z -1；左右对称）",
     "30 × 12",
     "炮台放到地上那一下：地面上闪出一个金色的六边形光框（从斜上方看是扁的），一道青色的光横着一扫，四周扬起一点灰尘（参考 "
     "q_turret_spawn_hexagon、q_turret_spawn_flares）。**左右对称**，5 帧。" + "炮台站在中间（不用画）。",
     GO + ", " + HX + " and " + SM,
     "A TURRET DEPLOYING, 5 frames, " + LR + ": 1 a small golden hexagon outline on the ground (" + GROUND + "), 10 squares "
     "wide; 2 the hexagon 24 squares wide and bright, a thin cyan light line sweeping across it; 3 the hexagon at its "
     "widest, small grey dust puffs at its two ends; 4 the hexagon fading, the dust drifting out; 5 only faint dust.",
     row(5, 30, 12) + "; " + TUR + ", its feet on the middle of the ellipse."),
    ("t_muzzle", "Q：炮台开火的炮口火光，3 帧（画进炮台的动画）", "画进炮台 t_turret 动画（炮口正对着看画的人；上下左右都对称）",
     "10 × 10",
     "炮台开一炮：炮口正对着看画的人，所以火光是从中间往四周放射的一朵橙金色的星形火光（参考 q_turret_muzzle）。**上下左右都对称**，"
     "3 帧：小、最亮、散。",
     FI,
     "A MUZZLE FLASH SEEN HEAD ON, 3 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM: 1 a small white-yellow star 4 "
     "squares across; 2 an orange-gold starburst 9 squares across with four longer points and four shorter ones, a white "
     "core; 3 the points fading to orange sparks.",
     row(3, 10, 10) + CENTER),
    ("t_shot", "Q：炮台打出的炮弹，飞行中循环 2 帧", "view_projectiles `league_heimerdinger_t_shot`（附加包：从炮台飞向目标）", "8 × 5",
     "炮台打出的一发炮弹：橙金色发光的小弹丸，后面拖一道短短的火光尾巴（参考 q_turret_mis、q_turret_mis_head）。**朝右飞、上下对称**，"
     "循环 2 帧。",
     FI,
     "A TURRET SHELL, looping 2 frames, " + TB + ": a glowing orange-gold pellet 2-3 squares across with a white core, a "
     "short bright streak of 4 squares behind it.",
     row(2, 8, 5) + CENTER),
    ("t_hit", "Q：炮弹打中目标，3 帧", "view_effects `league_heimerdinger_t_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "炮弹打中：一个橙色的光圈一闪（参考 q_turret_tar_bubble），迸出几点火星。**左右对称**，3 帧。",
     FI,
     "A SHELL HIT, 3 frames, " + LR + ": 1 a white-yellow flash 4 squares across inside a thin orange ring 8 squares "
     "across; 2 the ring broken into arcs, four orange sparks flying out; 3 fading sparks.",
     row(3, 10, 10) + CENTER),
    ("t_beam", "Q：炮台对被控制的英雄放的充能光束（打中处），4 帧", "view_effects `league_heimerdinger_t_beam`（跟随目标，z 2；左右对称）",
     "26 × 14",
     "炮台的充能光束打中被晕住的英雄：一道蓝白色的激光横着穿过目标（左右两头一样长），目标身上一个蓝色的光圈和白色的电火花（参考 "
     "q_turret_charged_mis、q_charged_tar_bubble、q_charged_impact_anim）。**左右对称**，4 帧。",
     HX,
     "A CHARGED BEAM HITTING, 4 frames, " + LR + ": 1 a thin white-blue laser line straight across the whole cell through "
     "its middle; 2 the line 3 squares thick and bright with a blue ring 10 squares across round the middle and white "
     "sparks; 3 the line thinning, the ring breaking into arcs; 4 fading blue sparks.",
     row(4, 26, 14) + CENTER),
    ("t_beam_line", "Q：充能光束本身（飞向目标），循环 3 帧", "view_projectiles `league_heimerdinger_t_beam_line`（附加包：从炮台射向目标）",
     "24 × 6",
     "充能光束：一段蓝白色的激光往前射，前端最亮（参考 q_turret_charged_mis）。**朝右飞、上下对称**，循环 3 帧（光芯一闪一闪）。",
     HX,
     "A LASER BOLT, looping 3 frames, " + TB + ": a straight beam 24 squares long, a white core line 1 square thick in a "
     "blue glow 3 squares thick, its head on the right brighter and a little wider, flickering from frame to frame.",
     row(3, 24, 6) + CENTER),
    ("t_gone", "Q：炮台到时间损坏消失，4 帧（画进炮台动画的结尾）", "画进炮台 t_turret 动画的结尾（左右对称）", "24 × 18",
     "炮台到时间了：冒出一团灰烟，几点橙色火星，崩出两三个小螺母和螺丝（参考 heimer_base_death_flares、nut_01、screw_02）。"
     "**左右对称**，4 帧。炮台站在中间（不用画）。",
     SM + ", " + FI + " and " + ME,
     "A TURRET BREAKING DOWN, 4 frames, " + LR + ": 1 a puff of grey smoke over the turret's place with a few orange "
     "sparks; 2 the smoke bigger, two tiny steel nuts and a screw flying up and out (mirrored pairs); 3 the smoke "
     "drifting up, the nuts falling; 4 a fading smoke wisp.",
     row(4, 24, 18) + "; " + TUR + "."),
    # ---- E CH-2 Electron Storm Grenade
    ("e_grenade", "E 电子风暴手雷：飞行中的手雷，循环 4 帧", "view_projectiles `league_heimerdinger_e_grenade`（抛物线飞行）", "9 × 9",
     "一颗圆手雷：深灰色金属壳、两道发光的蓝色环带、一个小拉环，表面噼啪冒电火花（参考 e_grenade_tx、z_electricity）。**圆形、上下左右"
     "都对称**，循环 4 帧（电火花一闪一闪，像在旋转）。",
     ME + " and " + HX,
     "AN ELECTRIC GRENADE, looping 4 frames, " + ROUND + ": a dark steel ball 7 squares across, two glowing blue bands "
     "round it, tiny blue sparks crackling on its edge at different places in each frame.",
     row(4, 9, 9) + CENTER),
    ("e_blast", "E：手雷落地爆出电子风暴，6 帧", "view_effects `league_heimerdinger_e_blast`（落点，不跟随；画在人物下面 z -1）",
     "54 × 36",
     "手雷炸开：先一个蓝白色的星形闪光，往上喷出一束青色的光线，地上一圈深蓝色的冲击波往外扩，几道蓝紫色的闪电往四周劈出去，最后电光"
     "慢慢散掉（参考 e_blast_flash、e_explo_rays、e_shockwave、e_cas_bubble、z_electricity）。半径约 23 格（地面椭圆约 46 格宽）。"
     "**左右对称**，6 帧。",
     HX + " and " + BO,
     "AN ELECTRON STORM BLAST, 6 frames, " + LR + ": 1 a white-blue star flash 12 squares across in the middle of the "
     "ground; 2 a fan of cyan rays bursting up from it 20 squares high, a thin dark-blue shockwave ring on the ground (" +
     GROUND + ") 20 squares wide; 3 the ring 46 squares wide and bright blue, four jagged blue-violet lightning bolts "
     "arcing out over it (mirrored); 4 the bolts flickering, small electric crackles all over the ring; 5 the ring "
     "fading, a few crackles left; 6 faint blue sparks.",
     row(6, 54, 36) + "; the ground ellipse's middle 6 squares above the bottom of each cell."),
    ("e_hit", "E：被电到的敌人身上冒电，3 帧", "view_effects `league_heimerdinger_e_hit`（跟随目标，z 2；左右对称）", "14 × 18",
     "被电子风暴打中：目标身上爬满蓝紫色的小闪电（参考 z_electricity、z_small_lighting）。**左右对称**，3 帧。",
     BO,
     "AN ELECTRIC SHOCK ON A BODY, 3 frames, " + LR + ": jagged blue-violet zigzag arcs crawling up a body-sized space "
     "(10 squares wide, 16 tall), white sparks where they bend, the arcs in different places in each frame (mirrored "
     "pairs); the middle of the cell left mostly clear (the body).",
     row(3, 14, 18) + CENTER),
    ("e_slow", "E：减速时脚下的电光，循环 4 帧", "view_buffs `league_heimerdinger_e_slow`（也给 x_slow 用；跟随，画在人物下面 z -1）",
     "22 × 8",
     "被减速的敌人脚下噼啪冒电：地上一圈淡蓝色的椭圆，上面跳着几点小电火花。**左右对称**，循环 4 帧。",
     HX,
     "AN ELECTRIC SLOW UNDER THE FEET, looping 4 frames, " + LR + ": a faint blue ring on the ground (" + GROUND + ") 20 "
     "squares wide, tiny white-blue sparks jumping at different places on it in each frame (mirrored).",
     row(4, 22, 8) + CENTER),
    # ---- R UPGRADE!!!
    ("r_up", "R 升级！！！：头顶上的升级光，6 帧", "view_effects `league_heimerdinger_r_up`（跟随他，z 2；左右对称）", "40 × 36",
     "大招按下：头顶上爆出一团青蓝色的光，几道白色的光线放射出去，还有几个小齿轮和六角螺母往上蹦（参考 r_cast_flares、r_glowy_rays、"
     "r_flash_colormap、nut_01）。只画在头顶和头的四周，**身体位置留空**。**左右对称**，6 帧。",
     HX + " and " + ME,
     "AN UPGRADE BURST OVER HIS HEAD, 6 frames, " + LR + ": 1 a cyan flash 8 squares across just above his head; 2 a "
     "bright cyan-white burst 18 squares across with white rays fanning up and out; 3 the rays longest, two small gears "
     "and two hex nuts popping up from it (mirrored pairs); 4 the gears at their highest, the burst fading to blue; 5 "
     "the gears falling, faint rays; 6 a few blue sparks.",
     row(6, 40, 36) + "; " + HIM + ", his head's top 14 squares below the top of the cell; draw nothing over his face."),
    ("re_grenade", "R 强化 E（CH-3X 闪电手雷）：飞行中的手雷，循环 4 帧", "view_projectiles `league_heimerdinger_re_grenade`（抛物线飞行）",
     "11 × 11",
     "升级后的手雷：更大，红色的壳、金色的环带，表面窜着红白色的电火花（参考 e_grenade_tx_ult、e_impact_flash_ult）。**圆形、上下左右"
     "都对称**，循环 4 帧。",
     RE + " and " + ME,
     "A LIGHTNING GRENADE, looping 4 frames, " + ROUND + ": a red steel ball 9 squares across with two golden bands, "
     "red-white sparks crackling on its edge at different places in each frame.",
     row(4, 11, 11) + CENTER),
    ("re_blast", "R 强化 E：闪电手雷的大爆炸，7 帧", "view_effects `league_heimerdinger_re_blast`（落点，不跟随；z -1）", "58 × 42",
     "闪电手雷炸开：一个红白色的大闪光，几道粗的蓝白闪电往四周劈，地上一圈红色的冲击波往外扩，然后散成电火花（参考 e_impact_flash_ult、"
     "r_lightning、e_shockwave）。半径约 25 格（地面椭圆约 50 格宽），比普通 E 更大更猛。**左右对称**，7 帧。",
     RE + " and " + HX,
     "A LIGHTNING GRENADE BLAST, 7 frames, " + LR + ": 1 a red-white star flash 16 squares across in the middle of the "
     "ground; 2 the flash bigger with red rays, a red shockwave ring on the ground (" + GROUND + ") 24 squares wide; 3 the "
     "ring 50 squares wide, six thick white-blue lightning bolts striking down and out from the middle (mirrored); 4 the "
     "bolts branching, crackles all over the ring; 5 the ring fading, the bolts thinner; 6 sparks; 7 a few fading sparks.",
     row(7, 58, 42) + "; the ground ellipse's middle 7 squares above the bottom of each cell."),
    # ---- R upgraded Q: H-28Q Apex Turret
    ("x_dust", "R 强化 Q（巨型炮台）：落地展开，6 帧（画进巨型炮台出现的动画）", "画进巨型炮台 x_turret 动画的开头（脚下，z -1；左右对称）",
     "40 × 30",
     "巨型炮台落地：一道蓝色的光柱从地上升起（参考 r_megaturret_spawn_cylinder），地上一圈蓝色的光环，四周冒出灰烟（参考 "
     "r_megaturret_cas_smoke）。**左右对称**，6 帧。巨型炮台站在中间（不用画）。",
     HX + " and " + SM,
     "AN APEX TURRET DEPLOYING, 6 frames, " + LR + ": 1 a blue ring on the ground (" + GROUND + ") 14 squares wide; 2 a "
     "blue light column 16 squares wide rising from the ring to the top of the cell, the ring 30 squares wide; 3 the "
     "column brightest with a white core, grey smoke puffs at the ring's ends; 4 the column thinning; 5 the column gone, "
     "the smoke drifting; 6 faint smoke.",
     row(6, 40, 30) + "; " + APEX + ", its feet on the middle of the ellipse."),
    ("x_muzzle", "R 强化 Q：巨型炮台开火的炮口光，3 帧（画进巨型炮台的动画）", "画进巨型炮台 x_turret 动画（炮口正对着看画的人；上下左右都对称）",
     "14 × 14",
     "巨型炮台开一炮：炮口正对着看画的人，一朵蓝白色的等离子星形光从中间往四周放射（参考 r_megaturret_glow、r_megaturret_mis_rings）。"
     "**上下左右都对称**，3 帧。",
     HX,
     "A PLASMA MUZZLE FLASH SEEN HEAD ON, 3 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM: 1 a white-blue star 6 "
     "squares across; 2 a blue-white starburst 13 squares across with a blue ring round it, a white core; 3 the ring and "
     "the points fading to blue sparks.",
     row(3, 14, 14) + CENTER),
    ("x_shot", "R 强化 Q：巨型炮台打出的等离子弹，循环 3 帧", "view_projectiles `league_heimerdinger_x_shot`（附加包：从巨型炮台飞向目标）",
     "12 × 8",
     "巨型炮台的等离子弹：蓝白色发光的弹头，外面套两圈蓝色的光环，后面拖一道蓝色的尾巴（参考 r_megaturret_mis_rings）。"
     "**朝右飞、上下对称**，循环 3 帧。",
     HX,
     "A PLASMA SHELL, looping 3 frames, " + TB + ": a white-blue glowing head 4 squares across, two thin blue rings round "
     "it, a blue streak of 6 squares behind it, flickering from frame to frame.",
     row(3, 12, 8) + CENTER),
    ("x_hit", "R 强化 Q：等离子弹打中目标，4 帧", "view_effects `league_heimerdinger_x_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "等离子弹打中：一团蓝白色的光爆开，白色的火花往外溅（参考 r_megaturret_impact_anim、r_megaturret_glow）。**左右对称**，4 帧。",
     HX,
     "A PLASMA HIT, 4 frames, " + LR + ": 1 a white flash 6 squares across; 2 a blue-white burst 13 squares across with "
     "white spikes; 3 the burst breaking into white sparks flying out; 4 fading blue sparks.",
     row(4, 16, 16) + CENTER),
    ("x_beam", "R 强化 Q：巨型炮台的充能光束（打中处），4 帧", "view_effects `league_heimerdinger_x_beam`（跟随目标，z 2；左右对称）",
     "32 × 16",
     "巨型炮台的大光束打中被控制的英雄：一道更粗的蓝白激光横着穿过目标，目标身上爆开一圈青色的冲击光（参考 "
     "r_megaturret_charged_blowback、r_megaturret_charged_glow）。**左右对称**，4 帧。",
     HX,
     "A BIG CHARGED BEAM HITTING, 4 frames, " + LR + ": 1 a white-blue laser 2 squares thick straight across the whole cell "
     "through its middle; 2 the laser 4 squares thick, a cyan ring of jagged light 14 squares across bursting round the "
     "middle; 3 the laser thinning, the ring's jagged sparks flying out; 4 fading cyan sparks.",
     row(4, 32, 16) + CENTER),
    ("x_gone", "R 强化 Q：巨型炮台到时间损坏，5 帧（画进巨型炮台动画的结尾）", "画进巨型炮台 x_turret 动画的结尾（左右对称）", "30 × 26",
     "巨型炮台到时间了：一团更大的灰烟，蓝色的电火花乱窜，崩出几个螺母螺丝。**左右对称**，5 帧。巨型炮台站在中间（不用画）。",
     SM + ", " + HX + " and " + ME,
     "AN APEX TURRET BREAKING DOWN, 5 frames, " + LR + ": 1 blue sparks crackling over the turret's place; 2 a big grey "
     "smoke puff, three steel nuts and screws flying up and out (mirrored pairs); 3 the smoke at its biggest, blue sparks "
     "in it; 4 the smoke drifting up, the nuts falling; 5 a fading smoke wisp.",
     row(5, 30, 26) + "; " + APEX + "."),
    # ---- the passive Hextech Affinity
    ("haste", "被动 海克斯科技亲和：炮台旁加速，脚下循环 3 帧", "view_buffs `league_heimerdinger_haste`（跟随他，画在人物下面 z -1）",
     "20 × 8",
     "在炮台旁边加速：脚下一圈淡金色的六边形光纹，上面闪着几点青色的小光点。**左右对称**，循环 3 帧。",
     GO + " and " + HX,
     "A SPEED GLOW UNDER THE FEET, looping 3 frames, " + LR + ": a faint golden hexagon outline on the ground (" + GROUND +
     ") 18 squares wide, three or four tiny cyan glints at different places on it in each frame (mirrored).",
     row(3, 20, 8) + CENTER),
    # ---- death
    ("dead_burst", "死亡：背包炸开，5 帧（画进他的死亡帧）", "画进 dead 帧（背包处；左右对称）", "34 × 26",
     "背包炸开：一团橙红色的火球爆开，冒出灰烟，螺母、螺丝和小齿轮往外飞（参考 heimer_base_death_fireball、heimer_base_death_flares、"
     "death_smoke、nut_01、screw_02、screw_03）。**左右对称**，5 帧。",
     FI + ", " + SM + " and " + ME,
     "A BACKPACK BURSTING, 5 frames, " + LR + ": 1 a white-yellow flash 10 squares across; 2 an orange-red fireball 20 "
     "squares across, two steel nuts, two screws and a small gear flying out (mirrored pairs); 3 the fireball breaking "
     "into grey smoke, the parts further out; 4 a big grey smoke cloud, the parts falling; 5 the smoke fading.",
     row(5, 34, 26) + CENTER),
]
BIG_FX = ["e_blast", "re_blast", "r_up", "x_dust", "x_gone", "dead_burst", "t_dust"]
FLYING = ["a_bolt", "w_rocket", "t_shot", "t_beam_line", "x_shot"]
ROUNDS = ["e_grenade", "re_grenade", "t_muzzle", "x_muzzle"]
FORWARD = ["w_flash"]

GROUPS = [
    ("a_bolt / a_hit", ["heimerdinger_base_aa_tar", "heimerdinger_base_z_small_lighting_4x4",
                        "heimerdinger_base_z_impact_anim", "heimerdinger_base_flare_rgb"]),
    ("w_rocket / w_flash / w_hit", ["heimerdinger_hextech_missile_04", "heimerdinger_base_w_missile_flames",
                                     "heimerdinger_base_w_missile_glow", "heimerdinger_base_w_aftersmoke_2x2",
                                     "heimerdinger_base_w_tar_bubble"]),
    ("t_dust / t_muzzle / t_shot / t_hit", ["heimerdinger_base_q_turret_spawn_hexagon",
                                            "heimerdinger_base_q_turret_spawn_flares", "heimerdinger_base_q_turret_muzzle",
                                            "heimerdinger_base_q_turret_mis", "heimerdinger_base_q_turret_tar_bubble"]),
    ("t_beam / t_beam_line / t_gone", ["heimerdinger_base_q_turret_charged_mis", "heimerdinger_base_q_charged_tar_bubble",
                                       "heimerdinger_base_q_charged_impact_anim_2", "heimer_base_death_flares",
                                       "nut_01"]),
    ("e_grenade / e_blast", ["heimerdinger_base_e_grenade_tx", "heimerdinger_base_e_blast_flash",
                             "heimerdinger_base_e_explo_rays", "heimerdinger_base_e_shockwave",
                             "heimerdinger_base_e_cas_bubble"]),
    ("e_hit / e_slow", ["heimerdinger_base_z_electricity_2x2", "heimerdinger_base_e_swirl",
                        "heimerdinger_base_e_ring_swirl", "heimerdinger_base_e_ground_flash"]),
    ("r_up / haste", ["heimerdinger_base_r_cast_flares", "heimerdinger_base_r_glowy_rays",
                      "heimerdinger_base_r_flash_colormap", "heimerdinger_base_r_antenna_glow", "screw_02"]),
    ("re_grenade / re_blast", ["heimerdinger_base_e_grenade_tx_ult", "heimerdinger_base_e_impact_flash_ult",
                               "heimerdinger_base_r_lightning", "heimerdinger_base_e_swirl_ult"]),
    ("x_dust / x_muzzle / x_shot", ["heimerdinger_base_r_megaturret_spawn_cylinder",
                                    "heimerdinger_base_r_megaturret_cas_smoke", "heimerdinger_base_r_megaturret_glow",
                                    "heimerdinger_base_r_megaturret_mis_rings"]),
    ("x_hit / x_beam / x_gone", ["heimerdinger_base_r_megaturret_impact_anim",
                                 "heimerdinger_base_r_megaturret_charged_blowback",
                                 "heimerdinger_base_r_megaturret_charged_glow", "screw_03"]),
    ("dead_burst", ["heimer_base_death_fireball_01", "heimer_base_death_fireball_02", "heimerdinger_base_death_smoke_01",
                    "heimerdinger_base_recall_smoke"]),
]


def at_1x(name):
    """A design (hd/<name>.png, PPU 1.5) brought to the game's squares (pixel_down.pixelate), as the game shows it."""
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, name + ".png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / PPU, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Him and both turrets at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    import tfm2_ase as T
    figs = [at_1x("idle"), at_1x("turret"), at_1x("apex")]
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
    d.text((8, 36), f"黑默丁格 {figs[0].shape[1]}×{figs[0].shape[0]} 格，炮台 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"巨型炮台 {figs[2].shape[1]}×{figs[2].shape[0]} 格，原版斗士 {figs[3].shape[1]}×{figs[3].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return [f.shape for f in figs]


def design_sheet(path):
    """Him and both turrets at 4x, the designs' own squares (PPU 1.5)."""
    parts = [np.asarray(Image.open(RF.lp(os.path.join(HD, n + ".png"))).convert("RGBA")) for n in ("idle", "turret", "apex")]
    W = sum(p.shape[1] for p in parts) * 4 + 16 * (len(parts) + 1)
    H = max(p.shape[0] for p in parts) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    x = 16
    for p in parts:
        bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(p, 4, 0), 4, 1)), (x, H - 16 - p.shape[0] * 4))
        x += p.shape[1] * 4 + 16
    bg.convert("RGB").save(path)


def document(shapes):
    (h, w), (th, tw), (xh, xw) = [s[:2] for s in shapes[:3]]
    L = []
    a = L.append
    a("# 大发明家 黑默丁格：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/heimerdinger_designs.png`：左边是他——3/4 正面朝右、金黄色大团头发、"
      "红框青蓝护目镜、白八字胡、墨绿灰外套、橙色多功能工具和灰绿扳手；中间是 Q 的小炮台——四条腿、两根排气筒、大红炮口，正面；右边是"
      "大招的巨型炮台——两边大齿轮、三脚架，正面）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），他 "
      f"{h} 格高、{w} 格宽，小炮台 {th}×{tw} 格，巨型炮台 {xh}×{xw} 格；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/heimerdinger_size.png`：他和两座炮台在游戏里的大小（放大 4 倍），地面在红线上，上面是 10 格一段的刻度，右边是"
      "原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里黑默丁格和炮台自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了"
      "行，只在本地用，不要提交。颜色照英雄联盟原版：**他的海克斯科技是蓝白色的电光**（普攻、E 的电子风暴、R 的升级、巨型炮台）；"
      "**小炮台的炮弹和 W 的导弹是橙金色的火光，带灰烟**；**充能光束是蓝白色的**；**升级后的闪电手雷是红色的**；**炮台落地是一个金色的"
      "六边形**。")
    a("> - **特效要亮**：每团火、每道电光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **火焰、电光、光环、冲击波都没有黑描边**；**灰烟、金属零件（螺母、螺丝、手雷壳）**可以有 1 格暗边。")
    a("> - **围着人或炮台的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、地上、身上、炮台上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（电光弹、导弹、"
      "炮弹、光束、等离子弹）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的）。**两颗手雷和两朵炮口光**"
      "是圆的，**上下左右都对称**。**导弹发射的火光**（w_flash）**朝右画**，会画进他的动作帧里，不用对称。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `heimerdinger_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度"
      "只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 "
      f"`cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/heimerdinger_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 "
      f"`outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（W「海克斯科技微型导弹」在里面） | 扳手射出电光弹；每第 3 次普攻背包机械臂发射 5 枚导弹 | `a_bolt` · `a_hit` · `w_rocket` · "
      "`w_flash` · `w_hit` |")
    a("| 技能 1 = Q「H-28 G 进化炮台」 | 放下炮台（最多 3 座），炮台每秒打一发炮弹，对被控制的英雄放充能光束，10 秒后损坏 | `t_dust` · "
      "`t_muzzle` · `t_shot` · `t_hit` · `t_beam` · `t_beam_line` · `t_gone` |")
    a("| 被动「海克斯科技亲和」 | 在自己的炮台旁移速提高 | `haste` |")
    a("| 技能 2 = E「CH-2 电子风暴手雷」 | 扔出手雷，落地爆出电子风暴：伤害、减速，正中心眩晕 | `e_grenade` · `e_blast` · `e_hit` · "
      "`e_slow` |")
    a("| 大招「升级！！！」 | 头顶升级的光；敌人扎堆时连扔 3 颗闪电手雷，否则放下巨型炮台 | `r_up` · `re_grenade` · `re_blast` · "
      "`x_dust` · `x_muzzle` · `x_shot` · `x_hit` · `x_beam` · `x_gone` |")
    a("| 死亡 | 背包炸开 | `dead_burst` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火焰、电光、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（灰烟、金属零件可以有 1 格暗边）。")
    a("- **要亮**：每个火焰、电光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海克斯蓝白电光", HEX), ("E 的闪电（白到蓝紫）", BOLT), ("火光（炮弹、导弹、爆炸）", FIRE),
                        ("金色（炮台落地的六边形、被动）", GOLD), ("闪电手雷（红）", RED), ("灰烟", SMOKE), ("金属（螺母、螺丝、手雷壳）", METAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（六边形、冲击波、减速）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、炮台上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人或炮台**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：普攻射程 55000，炮台射程 50000，"
      "E 半径 23000、正中眩晕半径 11000，闪电手雷半径 25000，巨型炮台射程 60000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `heimerdinger_fx_{name}.png`：{title}\n")
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
        a(f"| `heimerdinger_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_heimerdinger_fx`（小的）和 `league_heimerdinger_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_heimerdinger.py 的 views；x_slow 的 tag 用 e_slow）。炮台本身（t_turret、x_turret）是我从定稿做的高清帧"
      "（PPU 1.5，hd.rs EFFECTS），t_dust / t_muzzle / t_gone、x_dust / x_muzzle / x_gone 合进它们的动画（出现、每一炮、损坏）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；圆的（{'、'.join(ROUNDS)}）断言上下左右都对称；w_flash 朝右、画进 attack_w 帧；"
      "dead_burst 画进 dead 帧；其余断言左右对称；e_blast、re_blast 不跟随（落点）。t_shot、t_beam_line、x_shot 给附加包"
      "（炮台的炮弹从炮台飞向目标）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给火焰描的最深色边（灰烟、金属零件的暗边保留）；核对交回的张数和这份"
      "清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def configure():
    RF.REF, RF.GROUPS, RF.SIZE_LABEL = REF, GROUPS, "黑默丁格"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="heimerdinger_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "..", "..", "..", "dist", "heimerdinger_packs"),
                    help="folder for the zip (the main checkout's dist/)")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.normpath(os.path.join(a.out, a.name + ".zip"))
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_heimerdinger.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "heimerdinger_designs.png"))
    shapes = size_sheet(os.path.join(out, "design", "heimerdinger_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"heimerdinger_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": ("top-bottom" if x[0] in FLYING else "both" if x[0] in ROUNDS
                                 else "none (points right)" if x[0] in FORWARD else "left-right")} for x in FX],
                  f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shapes)
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
