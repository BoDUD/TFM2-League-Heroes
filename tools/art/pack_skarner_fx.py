#!/usr/bin/env python3
"""Build skarner_fx_pack.zip: step 3 of Skarner's sprite - Codex draws his effects (pack_trundle_fx.py's way).

    python tools/lol/fx_ref_skarner.py          # League's particle textures -> C:/t/sk_work/fxref (Riot's art, local only)
    python tools/art/pack_skarner_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name skarner_fx_redo_pack]

The pack (C:/t/sk_work/fx/skarner_fx_pack, zipped into --out, default dist/skarner_packs) holds PROMPTS.md (also written
to assets/source/skarner/PROMPTS_FX.md), design/skarner_design.png (the approved idle and the boulder design at 4x on
their own squares), design/skarner_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px
ruler and the base fighter) and refs/lol_fx_ref.png (League's own particle textures for Skarner, grouped by the effect
they inform).
The effects are the views the kit binds (tools/kit/build_skarner.py, the user's picks 2026-10-26: jungle, layout A - Q /
E / R, W in the passive): view_effects a_hit, p_burst, q_hit, q_land, w_quake, w_hit, e_hit, e_slam, r_hit; view_buffs
p_quake, slow (q_slow, w_slow), w_shield (w_on), stun (e_stun), r_held, r_haste, q_held (rock: the boulder he holds,
over his back); view_projectiles q_rock (the thrown boulder), r_spike (Impale's lash down its line).
League's colours: Ixtal's TEAL CRYSTAL (white facets to deep teal), the stingers' ORANGE CORE, the EARTH of his quakes
(sand, dust, brown rock bits) and the BOULDER's grey-green stone. Red side: the client never mirrors an effect picture,
so every hit, buff, ground and body picture is symmetric left to right; the two projectiles fly to the right and are
symmetric top to bottom (the game turns them with their flight).
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

TMP = "C:/t/sk_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "skarner", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "skarner", "hd")
NAME = "skarner_fx_pack"
PPU = 1.75

CRYSTAL = "#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468"    # Ixtal crystal: white facets to deep teal
CORE = "#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006"                 # the stingers' orange core
EARTH = "#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A"                # sand, dust and rock bits of his quakes
STONE = "#DCE4D0, #AABA9E, #7E8E74, #56644E, #38422F"                # the boulder's grey-green stone
CR = f"a teal crystal ramp ({CRYSTAL})"
CO = f"an orange core ramp ({CORE})"
EA = f"an earth and dust ramp ({EARTH})"
ST = f"a grey-green stone ramp ({STONE})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
TB = ("drawn FLYING TO THE RIGHT (its back on the left) and SYMMETRIC TOP TO BOTTOM in every frame, square for square "
      "(the game turns it with its flight)")
IXTAL = ("everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets "
         "and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green "
         "stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls")
TARGET = "the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = "Skarner stands in the middle, not drawn: about 46 squares wide and 34 tall (a low, wide scorpion)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：毒刺扎中，3 帧", "view_effects `league_skarner_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "水晶毒刺扎在敌人身上：中间一下白光，一圈青绿的碎水晶往外崩，夹着两三点橙色火星（参考 hiteffect、r_hit_flash_spikes、p_impacttero）。"
     "**左右对称**，3 帧。",
     CR + ", " + CO,
     "A CRYSTAL STINGER STAB LANDING, 3 frames, " + LR + ": 1 a white-teal flash 6 squares across with a small orange "
     "core; 2 a ring of angular teal crystal shards bursting out 12 across at mirrored places, two orange sparks; 3 the "
     "shards further out, dimming into dust. " + IXTAL + ".",
     row(3, 14, 14) + CENTER),
    # ---- passive: Quaking
    ("p_quake", "战栗：脚下一直在震，4 帧循环", "view_buffs `league_skarner_p_quake`（跟随目标，脚下，z -1；左右对称）", "18 × 8",
     "被战栗的人（掉最大生命值的魔法伤害，4 秒）：脚下的地面裂开、一圈细裂纹一闪一闪，裂缝里透出橙色的光，几颗小石子往上跳（参考 w_cracks_light、"
     "revive_ground_crack、p_rockbits）。**左右对称**，4 帧循环。",
     EA + ", " + CO,
     "A QUAKING GROUND AT THE FEET, 4 looping frames, " + LR + ", " + FEET + ": an ellipse of cracked ground 16 wide, "
     "thin dark cracks glowing orange inside; frames 1-4 the cracks flickering in turn and a few small pebbles hopping up "
     "2-3 squares and falling at mirrored places. " + IXTAL + ".",
     row(4, 18, 8) + CENTER),
    ("p_burst", "战栗：满层开始战栗，5 帧", "view_effects `league_skarner_p_burst`（跟随目标，z 2；左右对称）", "24 × 24",
     "战栗叠满的一刻：目标身上一圈震波往外一荡，几片青绿水晶和橙色碎光往外崩（参考 distortion_soundwaves、ba_ring、spark_round_bloom）。"
     "光只画在外圈，**身体位置留空**。**左右对称**，5 帧。",
     CR + ", " + CO + ", " + EA,
     "A TREMOR BURSTING AROUND A UNIT, 5 frames, " + LR + ", " + TARGET + ": 1 a thin orange ring 8 across at the middle; "
     "2 a teal-and-white vibration ring 18 across with small crystal shards on it; 3 the ring 22 across, orange sparks "
     "flying out at mirrored places; 4 two faint ripple arcs at both sides, dust; 5 the last sparks fading. The middle "
     "(the body) left empty. " + IXTAL + ".",
     row(5, 24, 24) + CENTER),
    # ---- skill: Q Shattered Earth / Upheaval
    ("q_hit", "撼地：举着巨石砸中，4 帧", "view_effects `league_skarner_q_hit`（跟随目标，z 2；左右对称）", "20 × 18",
     "举着巨石时的强化普攻打中（周围的人一起受伤）：一下白光，一圈灰绿的碎石块和沙尘往四周崩开（参考 q_impact_cross、q_impactspike、q_rocks、"
     "q_smoke_dust）。**左右对称**，4 帧。",
     ST + ", " + EA,
     "A BOULDER-EMPOWERED BLOW LANDING, 4 frames, " + LR + ": 1 a white flash 6 across; 2 a burst of grey-green rock "
     "chunks (2-3 squares each) flying out 16 across at mirrored places; 3 the chunks further out and a puff of sand dust "
     "18 across; 4 the dust settling, a few pebbles falling. " + IXTAL + ".",
     row(4, 20, 18) + CENTER),
    ("q_land", "擎天：巨石砸在地上，5 帧", "view_effects `league_skarner_q_land`（地上，z 1，不跟随；左右对称）", "36 × 18",
     "扔出去的巨石落地砸开：地上砸出一个坑，一圈碎石和尘土往外炸开（参考 q_craterobsi、q_rockpickup_halfcrater、q_blastshapes、q_groundsmoke）。"
     "**正面看，左右对称**，5 帧。",
     ST + ", " + EA,
     "A BOULDER CRASHING INTO THE GROUND, 5 frames, " + LR + ", seen from the front-above, centred on the ground point: 1 "
     "a white impact flash 10 wide; 2 a dark crater ellipse 18 wide, grey-green rock fragments flying up and out to both "
     "sides; 3 a ring of sand dust 30 wide rolling out, fragments at their highest; 4 the dust ring 34 wide, fragments "
     "falling; 5 the dust thinning around a cracked crater. " + IXTAL + ".",
     row(5, 36, 18) + CENTER),
    ("q_rock", "擎天：飞出去的巨石，2 帧循环", "view_projectiles `league_skarner_q_throw`（弹道，z 2；朝右画、上下对称）", "16 × 14",
     "扔出去在空中飞的巨石：照 `design/skarner_design.png` 右边那块**灰绿色多面体巨石**画（缩到游戏大小，几道裂缝），后面拖一缕沙尘。"
     "**朝右飞、上下对称**，2 帧循环（石头稍微转一下）。",
     ST + ", " + EA,
     "THE THROWN BOULDER IN FLIGHT, 2 looping frames, " + TB + ": a faceted grey-green boulder 11 wide and 10 tall with "
     "a few dark cracks (the boulder of the design picture), a short trail of sand dust behind it on the left; frame 2 "
     "the boulder turned a little, its facets shifted. Every stone square has a 1-square near-black outline (it is a solid "
     "thing), the dust none. " + IXTAL + ".",
     row(2, 16, 14) + CENTER),
    ("q_held", "撼地：举在背上的巨石，4 帧循环", "view_buffs `league_skarner_rock`（大表，跟随斯卡纳，z 3；左右对称）", "64 × 56",
     "举着巨石的时候（强化 3 下普攻或者扔出去之前），他背上一直有这块巨石：照 `design/skarner_design.png` 右边那块巨石画（灰绿色多面体、几道裂缝），"
     "**横着摆、在格子的上半部、左右居中**，大约 34 格宽、16 格高，底边差不多在格子从下往上 28 格的地方（他的三根毒刺就扎在巨石底下）；石头下面几颗小石子和沙往下掉。"
     "格子下半部是他自己的身体，**留空、不要画他**。**左右对称**，4 帧循环（只有掉下来的小石子在动）。",
     ST + ", " + EA,
     "A BIG BOULDER HELD UP OVER A SCORPION'S BACK, 4 looping frames, " + LR + ", " + HIM + " in the lower part of the "
     "cell: in the UPPER part, centred left to right, a long faceted grey-green boulder lying sideways, 34 squares wide "
     "and 16 tall, its bottom edge about 28 squares above the bottom of the cell, a few dark cracks across it (the "
     "boulder of the design picture); frames 1-4 the boulder still, small pebbles and sand trickling down from its "
     "underside at mirrored places. The lower part (his body) left empty. Every stone square has a 1-square near-black "
     "outline (it is a solid thing), the sand none. " + IXTAL + ".",
     row(4, 64, 56) + CENTER),
    ("slow", "减速：脚下一圈沙尘，4 帧循环", "view_buffs `league_skarner_q_slow` / `league_skarner_w_slow`（跟随，脚下，z -1；左右对称）",
     "16 × 8",
     "被减速：脚下一圈翻起来的沙尘和小石子，裂纹里一点点青光。**左右对称**，4 帧循环。",
     EA + ", " + CR,
     "A DUST SLOW AT THE FEET, 4 looping frames, " + LR + ", " + FEET + ": a thin ellipse of churned sand 14 wide with "
     "small pebbles and two faint teal glints; frames 1-4 the sand swirling slowly and a few grains drifting up. " +
     IXTAL + ".",
     row(4, 16, 8) + CENTER),
    # ---- passive: W Seismic Bastion
    ("w_quake", "震地壁垒：地震冲击波，6 帧", "view_effects `league_skarner_w_quake`（大表，地上，z -1，不跟随；左右对称）", "84 × 28",
     "冲锋拖完人以后他砸地：从他脚下**一圈地震波往外推开**——地面裂开、一圈碎石和沙尘往外滚，裂缝里透出橙色和青色的光（参考 w_ring_shockwave、"
     "shockwave、w_cracks_erosion、w_rocks、w_smoke）。地震的范围要大：最大时**横向 80 格、纵向 26 格**（比他身子宽一倍）。**左右对称**，6 帧。",
     EA + ", " + CO + ", " + CR,
     "AN EARTHQUAKE SHOCKWAVE AROUND HIM, 6 frames, " + LR + ", " + FEET + ", centred, growing to a BIG ellipse 80 squares "
     "wide and 26 tall: 1 a bright crack star 16 wide, orange light in the cracks; 2 a ring of churned ground and rock "
     "bits 36 wide rolling out; 3 the ring 56 wide, rock chunks thrown up at both sides, teal crystal glints in the cracks; "
     "4 the ring 72 wide, a wall of sand dust along it; 5 the ring 80 wide breaking into dust puffs, the cracked ground "
     "behind it; 6 the dust thinning, the last cracks fading. Frames 4-6 MUST reach 80 squares across. " + IXTAL + ".",
     row(6, 84, 28) + CENTER),
    ("w_shield", "震地壁垒：身上的水晶护盾，6 帧循环", "view_buffs `league_skarner_w_on`（跟随斯卡纳，z 3；左右对称）", "54 × 42",
     "护盾在的 3 秒里：他身外一层**半透明感的青绿水晶外壳**——用一圈棱角分明的水晶面围住他的轮廓（只画边缘那一圈和几块亮面，中间是他自己），"
     "几处亮面一闪一闪（参考 w_shield_pan、w_sheen、shield_bubble）。**只画外圈，身体位置留空**。**左右对称**，6 帧循环。",
     CR,
     "A CRYSTAL SHIELD AROUND A SCORPION, 6 looping frames, " + LR + ", " + HIM + ": a ring of angular teal crystal facets "
     "outlining him, 50 squares wide and 38 tall, drawn as a thin shell (2-3 squares thick) with a few bigger bright "
     "facets on top; frames 1-6 a white glint travelling over the facets around the shell. The middle (his body) left "
     "empty. " + IXTAL + ".",
     row(6, 54, 42) + CENTER),
    ("w_hit", "震地壁垒：被地震打中，4 帧", "view_effects `league_skarner_w_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "地震波打到的人：脚下的地面往上一顶，碎石和沙尘从他脚下冲上来。**左右对称**，4 帧。",
     EA + ", " + CO,
     "A QUAKE HITTING A UNIT, 4 frames, " + LR + ", " + TARGET + ": 1 a crack with orange light at the feet; 2 rock bits "
     "and sand bursting up 10 squares at both sides of the feet; 3 the bits at their highest, a dust cloud 16 wide; 4 the "
     "dust settling. " + IXTAL + ".",
     row(4, 18, 18) + CENTER),
    # ---- skill2: E Ixtal's Impact
    ("e_hit", "以绪塔尔冲击：撞上英雄，4 帧", "view_effects `league_skarner_e_hit`（跟随目标，z 2；左右对称）", "22 × 20",
     "冲锋撞上英雄的一下（接着把他拖走）：一下白光，一圈沙尘和碎水晶往两边炸开（参考 e_skirt、p_dust、sandstreaks）。**左右对称**，4 帧。",
     EA + ", " + CR,
     "A CHARGE SLAMMING INTO A UNIT, 4 frames, " + LR + ": 1 a white flash 8 across; 2 a burst of sand dust and teal "
     "crystal shards 18 across at mirrored places; 3 two dust plumes thrown out to both sides; 4 the dust thinning. " +
     IXTAL + ".",
     row(4, 22, 20) + CENTER),
    ("e_slam", "以绪塔尔冲击：砸停、晕眩，5 帧", "view_effects `league_skarner_e_slam`（跟随目标，z 2；左右对称）", "28 × 30",
     "拖着的英雄被砸停（晕眩）：他身上炸开一圈碎石和水晶，橙色的光一冲，周围的地面裂开（附加包里是撞在墙上）（参考 crater_mesh_erode、"
     "q_impactspike、r_impact_flare）。光和碎石只画在外圈，**身体位置留空**。**左右对称**，5 帧。",
     EA + ", " + CR + ", " + CO,
     "A UNIT SLAMMED HARD AND STUNNED, 5 frames, " + LR + ", " + TARGET + ": 1 an orange flash at the middle 10 across; "
     "2 a ring of rock chunks and teal crystal shards bursting out 24 across; 3 orange light flaring up 20 squares at both "
     "sides, cracks in the ground at the feet; 4 dust rolling out at both sides; 5 the last bits falling. The middle (the "
     "body) left empty. " + IXTAL + ".",
     row(5, 28, 30) + CENTER),
    ("stun", "晕眩：头上转圈的水晶碎片，4 帧循环", "view_buffs `league_skarner_e_stun`（跟随目标，头顶，z 3；左右对称）", "16 × 8",
     "被晕住的人：头顶一圈小小的青绿水晶碎片和橙色亮点在转。**左右对称**，4 帧循环。",
     CR + ", " + CO,
     "A STUN OVER THE HEAD, 4 looping frames, " + LR + ": a small flat ellipse 14 wide of four tiny teal crystal shards "
     "and two orange sparks circling; frames 1-4 the shards moved a quarter round each frame, mirrored left to right. " +
     IXTAL + ".",
     row(4, 16, 8) + CENTER),
    # ---- ult: R Impale
    ("r_spike", "毒刺贯体：尾巴扫出去的那一下，3 帧循环", "view_projectiles `league_skarner_r_lash`（大表，弹道，z 2；朝右画、上下对称）",
     "36 × 14",
     "三根尾巴往前一起扎出去：一道往前飞的冲击——**三枚青绿水晶毒刺**一前两后排成一个箭头，尖朝右，后面拖着橙色和青色的速度线（参考 r_tap_spear_sharp、"
     "r_wave_texture、r_wave_child_speedlines、r_missile_head）。**朝右飞、上下对称**，3 帧循环。",
     CR + ", " + CO,
     "THREE CRYSTAL STINGERS LASHING FORWARD, 3 looping frames, " + TB + ": three teal crystal stinger tips with orange "
     "cores, one in front at the middle and two a little behind above and below (an arrowhead 14 squares long, 10 tall), "
     "all pointing right, with streaks of orange and teal speed lines trailing 20 squares behind them; frames 1-3 the "
     "speed lines flickering and the tips glinting in turn. Every crystal square has a 1-square near-black outline, the "
     "speed lines none. " + IXTAL + ".",
     row(3, 36, 14) + CENTER),
    ("r_hit", "毒刺贯体：扎中英雄，5 帧", "view_effects `league_skarner_r_hit`（跟随目标，z 2；左右对称）", "26 × 30",
     "毒刺扎中、把人压制住：目标身上一下橙色的亮闪，一圈尖尖的水晶刺往外炸，然后几道橙色的光丝缠住他（参考 r_hit_flash_spikes、r_impact_flare、"
     "suppress、r_mark_distort）。光只画在外圈，**身体位置留空**。**左右对称**，5 帧。",
     CO + ", " + CR,
     "A UNIT IMPALED AND SUPPRESSED, 5 frames, " + LR + ", " + TARGET + ": 1 an orange-white flash 10 across at the "
     "middle; 2 a star of sharp teal crystal spikes bursting out 24 across; 3 the spikes breaking off, thin orange light "
     "threads wrapping around the unit at both sides; 4 the threads tightening, orange motes; 5 a faint orange ring. The "
     "middle (the body) left empty. " + IXTAL + ".",
     row(5, 26, 30) + CENTER),
    ("r_held", "毒刺贯体：被压制拖着走，6 帧循环", "view_buffs `league_skarner_r_held`（跟随目标，z 3；左右对称）", "26 × 34",
     "被压制的 1.5 秒里：目标身上**一圈橙色的光丝**把他捆住，头顶上方三枚小小的水晶毒刺尖朝下扎着他（参考 suppress、suppress_dark、"
     "generic_string_strands）。只画外圈和头顶，**身体位置留空**。**左右对称**，6 帧循环。",
     CO + ", " + CR,
     "A SUPPRESSED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": a loose ring of thin glowing orange threads "
     "around the unit's middle, 24 wide, seen slightly from above, and above its head three small teal crystal stinger "
     "tips pointing down at it; frames 1-6 the threads pulsing brighter in turn, a few orange motes drifting. The middle "
     "(the body) left empty. " + IXTAL + ".",
     row(6, 26, 34) + CENTER),
    ("r_haste", "毒刺贯体：加速的沙尘，4 帧循环", "view_buffs `league_skarner_r_haste`（跟随斯卡纳，脚下，z -1；左右对称）", "50 × 12",
     "扎中人以后他加速：脚下两边扬起一溜沙尘和速度线（参考 sandstreaks、r_air_trail）。**左右对称**，4 帧循环。",
     EA + ", " + CR,
     "A HASTE AT A SCORPION'S FEET, 4 looping frames, " + LR + ", " + FEET + ", " + HIM + ": a flat band of sand dust 48 "
     "wide along the ground with short horizontal speed streaks at both ends and two faint teal glints; frames 1-4 the "
     "streaks flickering and the dust puffs rolling outward at both ends. " + IXTAL + ".",
     row(4, 50, 12) + CENTER),
]
BIG_FX = ["q_held", "w_quake", "r_spike"]
FLYING = ["q_rock", "r_spike"]

GROUPS = [
    ("a_hit (the stinger)", ["skarner_rework_base_r_hit_flash_spikes_yellow", "skarner_rework_base_p_impacttero",
                             "hiteffect_gradient_64_2", "triangle_spark_06"]),
    ("p_quake p_burst (Quaking)", ["skarner_rework_w_cracks_light", "skarner_rework_base_revive_ground_crack",
                                   "skarner_rework_distortion_soundwaves_01", "skarner_rework_base_ba_ring"]),
    ("q_hit q_land (the boulder strikes)", ["skarner_rework_base_q_impact_cross", "skarner_rework_base_q_impactspike",
                                            "skarner_rework_base_q_craterobsi", "skarner_rework_base_q_rockpickup_halfcrater"]),
    ("q_rock q_held (the boulder)", ["skarner_rework_base_q_rocks_2x2", "skarner_rework_base_q_rocktiling",
                                     "skarner_rework_base_q_smoke_dust_white", "skarner_rework_base_props_tx_cm"]),
    ("w_quake w_hit (the earthquake)", ["skarner_rework_base_w_ring_shockwave_2", "skarner_rework_base_shockwave",
                                        "skarner_rework_w_cracks_erosion", "skarner_rework_base_w_rocks_2x2"]),
    ("w_shield (the crystal shield)", ["skarner_rework_base_w_shield_pan", "skarner_rework_base_w_sheen2",
                                       "3121_template_shield_bubble_child", "skarner_rework_base_w_shield_bubble_child_text_mask"]),
    ("e_hit e_slam slow r_haste (charge, dust)", ["skarner_rework_base_e_skirt", "skarner_rework_base_p_dust",
                                                  "skarner_rework_base_sandstreaks_gray", "skarner_rework_base_crater_mesh_erode"]),
    ("r_spike r_hit r_held (Impale)", ["skarner_rework_base_r_tap_spear_sharp", "skarner_rework_base_r_wave_texture",
                                       "skarner_rework_base_r_impact_flare", "suppress"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Skarner at game size (and holding the boulder) next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x(), design_1x("rock", 9.7 / 8.7 / PPU)]
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
    d.text((8, 36), f"斯卡纳 {figs[0].shape[1]}×{figs[0].shape[0]} 格，举石 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
           f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle and the boulder design at 4x, their own squares, side by side."""
    ims = [np.asarray(Image.open(lp(os.path.join(HD, f"{n}.png"))).convert("RGBA")) for n in ("idle", "rock")]
    W = sum(a.shape[1] * 4 for a in ims) + 48
    H = max(a.shape[0] for a in ims) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    x = 16
    for a in ims:
        bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (x, H - 16 - a.shape[0] * 4))
        x += a.shape[1] * 4 + 16
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 上古领主 斯卡纳：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/skarner_design.png`：左边是 Q 版水晶蝎子——青绿甲壳、橙白花纹、骨白骷髅小脸和"
      "银白头甲、两只大钳子、三根带青绿水晶毒刺和橙色核心的尾巴、六条钩爪腿；右边是同一个他用尾巴举着**灰绿色的大巨石**）。"
      f"斯卡纳在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/skarner_size.png`：斯卡纳（和举石的他）缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里斯卡纳自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**斯卡纳是以绪塔尔的上古水晶蝎子，特效都是水晶和大地**：**青绿水晶**（白色棱面到深青）、毒刺的**橙色核心**、地震的**沙尘、碎石**、"
      "巨石的**灰绿色石头**；不要光滑的霓虹光束，不要火，也不要魔法漩涡。")
    a("> - **特效要亮**：每道光、每片水晶都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、沙尘、速度线没有黑描边**（碎水晶、碎石也不要描黑边，用它自己最深的一档）；**只有巨石（`q_rock`、`q_held`）和尾巴毒刺（`r_spike`）"
      "这几个“东西”有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了两个弹道，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" + "`、`".join(FLYING) +
      "`）**朝右飞、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `skarner_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 毒刺扎 + 钳子夹 | `a_hit` |")
    a("| 被动「战栗」（并入 W 震地壁垒） | 普攻、巨石、毒刺贯体叠战栗，满层每秒掉最大生命值；冲锋拖完人时出护盾 + 地震波 | `p_quake` · `p_burst` · `w_quake` · `w_shield` · `w_hit` · `slow` |")
    a("| 技能 1 =「撼地 / 擎天」 | 从地里掘出巨石举着，强化 3 下普攻（周围的人一起受伤，第 3 下打最大生命值 + 减速）；举久了就扔出去 | `q_held` · `q_hit` · `q_rock` · `q_land` · `slow` |")
    a("| 技能 2 =「以绪塔尔冲击」 | 往前冲锋，撞上英雄拖着走，砸停晕眩 | `e_hit` · `e_slam` · `stun` |")
    a("| 大招 =「毒刺贯体」 | 三根尾巴往前扎，压制线上的英雄并拖着走，自己加速 | `r_spike` · `r_hit` · `r_held` · `r_haste` |\n")
    a("连招：**举着巨石放大招 → 先扔出擎天**，**冲锋拖完人 → 撼地马上好**，**大招扎中 → 战栗直接叠满**，**巨石第 3 下打中英雄 → 冲锋冷却缩短**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙尘、速度线没有黑描边，也不要用最深的颜色给形状描一圈边**（巨石、毒刺除外）。")
    a("- **都是水晶和大地**：青绿、橙、沙土、灰绿；每个形状 2–3 档平涂，水晶用棱角分明的几何面。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("水晶·青绿", CRYSTAL), ("核心·橙", CORE), ("大地·沙尘", EARTH), ("巨石·灰绿", STONE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（地震、裂纹、沙尘）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `skarner_fx_{name}.png`：{title}\n")
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
        a(f"| `skarner_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_skarner_fx`（小的）和 `league_skarner_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_skarner.py 的 views；buff 的 tag：q_slow / w_slow → slow、w_on → w_shield、e_stun → stun、rock → q_held；"
      "弹道：q_throw → q_rock、r_lash → r_spike）。")
    a("- 弹道（" + "、".join(FLYING) + "）断言上下对称，其余断言左右对称。")
    a("- q_held 的格子下半部是他自己：导入时让巨石的底边落在 idle 三根毒刺的高度（hd/idle.png 第 10–22 行，PPU 1.75）。")
    a("- 用 `pixel_1x/` 切格（import_trundle_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="skarner_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "skarner_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_skarner.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "skarner_design.png"))
    shape = size_sheet(os.path.join(out, "design", "skarner_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"skarner_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "left-right"} for x in FX],
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
