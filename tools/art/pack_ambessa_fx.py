#!/usr/bin/env python3
"""Build ambessa_fx_pack.zip: step 3 of Ambessa's sprite - Codex draws her effects (pack_belveth_fx.py's way).

    python tools/lol/fx_ref_ambessa.py             # League's particle textures -> C:/t/am_work/fxref (Riot's art, local only)
    python tools/art/pack_ambessa_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name ambessa_fx_redo_pack]

The pack (C:/t/am_work/fx/ambessa_fx_pack, zipped into --out, default dist/ambessa_packs) holds PROMPTS.md (also written to
assets/source/ambessa/PROMPTS_FX.md), design/ambessa_design.png (the idle at 4x, its own squares), design/ambessa_size.png
(at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Ambessa, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_ambessa.py): view_projectiles q2_crack; view_effects a_hit,
pw_hit, st_land, q_hit, q2_hit, e_lash (big), e_hit, w_brace, w_slam (big), w_hit, r_blink (big), r_pin, r_crash (big),
and the add-on's q_tip, w_crit (addons/league_ambessa); view_buffs slow (e_slow), pw_aura (pw); plus the forward pictures
drawn into her own frames (tools/fix/bake_caster_fx.py's way, K'Sante's): q_sweep (the half circle in front of her: the
kit's q_sweep view goes) and st_dash (the step's trail: the kit's st_dash view goes).
League's colours: SILVER-WHITE blade slashes with AMBER-GOLD sparks and embers (her drakehound blades), a BRONZE-GOLD
shield light for Repudiation, DARK SMOKE and dust; Public Execution adds Noxian CRIMSON. Red side: the client never
mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right; the projectile is
turned with its flight, so it is drawn flying right and symmetric top to bottom; the baked ones point forward (right)
and need no symmetry.
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

TMP = "C:/t/am_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "ambessa", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "ambessa", "hd")
NAME = "ambessa_fx_pack"
PPU = 2.0

STEEL = "#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272"             # the blades' silver-white slashes
EMBER = "#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410"             # amber-gold sparks and embers
BRONZE = "#FFF6CC, #EED088, #C49446, #865A22, #4E3212"            # Repudiation's shield light
CRIMSON = "#FFE0D6, #F47A62, #CC3226, #8A161C, #4C0A10"           # Noxian crimson (Public Execution)
SMOKE = "#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422"             # dark smoke and dust
ROCK = "#D2C6B6, #A09080, #6E6052, #443A32, #26201C"              # rock chips (solid: outlined)
ST = f"a silver-white steel ramp ({STEEL})"
EM = f"an amber-gold ember ramp ({EMBER})"
BR = f"a bronze-gold shield light ramp ({BRONZE})"
CR = f"a Noxian crimson ramp ({CRIMSON})"
SM = f"a dark smoke and dust ramp ({SMOKE})"
RO = f"a rock ramp ({ROCK})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
FWD = "pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry)"
CENTER = RF.CENTER
row = RF.row
BLADES = ("her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with "
          "amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; "
          "flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HER = "Ambessa stands in the middle, not drawn: {w} squares wide (with her blades) and {h} tall"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack and the passive
    ("a_hit", "普攻：双刀砍中，3 帧", "view_effects `league_ambessa_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "左右开弓的双刀砍中敌人（参考 ba_autoattacks_alpha）：中间一下白色的闪光，**两道银白色的月牙刀痕交叉成 X**，"
     "刀痕前沿是琥珀金色，边上溅开几颗琥珀色的火星。**左右对称**，3 帧。",
     ST + ", " + EM,
     "A TWIN BLADE STRIKE, 3 frames, " + LR + ": 1 a white flash 6 squares across; 2 two sharp silver-white crescent cuts "
     "crossing in an X 13 across, amber-gold edges, a few amber sparks flying out at mirrored places; 3 the cuts thinner "
     "and dimmer, the sparks further out, fading. " + BLADES + ". " + TARGET + ".",
     row(3, 14, 14) + CENTER),
    ("pw_hit", "龙犬之步：冲刺后强化的那一刀砍中，4 帧", "view_effects `league_ambessa_pw_hit`（跟随目标，z 2；左右对称）",
     "22 × 20",
     "龙犬之步以后强化的普攻（参考 p_specialattack_swipe_shape、p_specialattack_flow_shape）：比普通一刀大得多——"
     "**一道竖着的粗月牙刀光劈下来**，落点炸开一圈琥珀金色的火花，几块火星往上飞。**左右对称**，4 帧。",
     ST + ", " + EM,
     "A HEAVY CLEAVE, 4 frames, " + LR + ": 1 a tall white-silver vertical crescent slash 18 squares tall coming down "
     "through the middle, pointed at both ends, amber edges; 2 an amber-gold burst of sparks 20 wide where it lands, "
     "the slash at its brightest; 3 the sparks flying up and out at mirrored places, the slash thinning; 4 a few embers "
     "drifting, fading. " + BLADES + ". " + TARGET + ".",
     row(4, 22, 20) + CENTER),
    ("pw_aura", "龙犬之步：强化期间脚下的琥珀色气流，4 帧循环",
     "view_buffs `league_ambessa_pw`（tag `pw_aura`，跟随她，脚下，z -1；左右对称；约 3 秒）", "40 × 10",
     "冲刺以后攻速变快、下一刀强化的那几秒：她脚下**两缕琥珀色的气流**往两边打旋，几颗火星往上飘。**左右对称**，4 帧循环。",
     EM + ", " + SM,
     "AN EMBER STIR, 4 looping frames, " + LR + ": two thin amber-gold swirls curling out from under her to both sides "
     + FEET + " 38 wide, three small embers rising at mirrored places, a faint dark smoke wisp at each end; the swirls "
     "turn and the embers rise frame to frame so the loop flows. Sparse and light. " + BLADES + ".",
     row(4, 40, 10) + CENTER),
    ("st_dash", "龙犬之步：往前冲刺的拖影（画进她的帧），4 帧", "画进她自己的 step 帧（bake_caster_fx；朝右；kit 的 st_dash 去掉）",
     "44 × 22",
     "每放完一个技能往前冲的那一步（参考 z_dash_indicator_alpha、z_chainsmask_alpha、z_generic_smoke_shape1）："
     "她身后**拖着几道横着的银白色速度线**，两条铁链在身后甩成弧，脚下扬起一小团暗色的尘土。**朝右**，4 帧。",
     ST + ", " + SM + ", " + EM,
     "A DASH TRAIL, 4 frames, " + FWD + ": 1 three long horizontal silver-white speed streaks behind her (on the cell's "
     "left), a small dark dust puff at her heels; 2 the streaks longest (30 squares), two curved dark iron chain arcs "
     "trailing behind with amber glints; 3 the streaks breaking up, the dust rolling back; 4 a few streaks and dust "
     "fading. " + BLADES + ".",
     row(4, 44, 22) + "; she stands at the cell's RIGHT part (not drawn, her feet on the cell's bottom row, her body "
     "about 26 squares wide at the right edge); everything trails behind her on the left."),
    ("st_land", "龙犬之步：冲到的地方扬起的尘土，3 帧", "view_effects `league_ambessa_st_land`（在落脚的地上，不跟随，z -1；左右对称）",
     "28 × 10",
     "冲刺停下的地方：脚下**一圈暗色的尘土往两边扬开**，几颗小石子和火星弹起来。**左右对称**，3 帧。",
     SM + ", " + EM + ", " + RO,
     "A SKID OF DUST, 3 frames, " + LR + ": 1 a flat dark dust ring 14 wide " + FEET + "; 2 the dust puffing out to both "
     "sides 26 wide, a few pebbles and amber sparks bouncing up at mirrored places; 3 the dust thinning, fading.",
     row(3, 28, 10) + CENTER),
    # ---- Q Cunning Sweep / Sundering Slam
    ("q_sweep", "狡诈横扫：身前的半圈刀光（画进她的帧），4 帧", "画进她自己的 skill 帧（bake_caster_fx；朝右；kit 的 q_sweep 去掉）",
     "60 × 34",
     "狡诈横扫（参考 q_broad_swipe_stylized_alpha、q_broad_swipe_chains_shape、q_broad_sweetspot_shape）："
     "两把刀连着铁链**在她身前横扫出半个圆**——一道宽宽的银白色月牙刀光从她背后扫到身前，"
     "**最外面的一圈（刀尖扫到的地方）最亮、是琥珀金色**，铁链在刀光里面，火星从外圈甩出去。**朝右**，4 帧。",
     ST + ", " + EM + ", " + SM,
     "A HALF-CIRCLE SWEEP, 4 frames, " + FWD + ": 1 a thin silver-white arc starting above and behind her; 2 a broad "
     "silver-white crescent sweeping round in FRONT of her (a half circle 30 squares in radius, from above her to below "
     "in front, the open side towards her), dark iron chain links inside it, its OUTER rim - the blades' edge - the "
     "brightest amber-gold; 3 the crescent complete, amber sparks thrown out from the outer rim; 4 the crescent breaking "
     "into fading streaks. " + BLADES + ".",
     row(4, 60, 34) + "; she stands at the cell's LEFT part (not drawn: her feet on the cell's bottom row, the middle of "
     "her body 14 squares from the left edge, 48 tall); the half circle in front of her, to the right."),
    ("q_hit", "狡诈横扫：被扫中，3 帧", "view_effects `league_ambessa_q_hit`（跟随目标，z 2；左右对称）", "18 × 14",
     "被横扫扫中：一道**横着的银白色刀痕**从中间划过（两头一样尖），上下崩开几颗琥珀色的火星。**左右对称**，3 帧。",
     ST + ", " + EM,
     "A PASSING CUT, 3 frames, " + LR + ": 1 a white-silver horizontal slash 16 squares long, pointed at both ends, "
     "through the middle; 2 the slash wider with amber edges, amber sparks bursting up and down at mirrored places; 3 "
     "the sparks drifting out, fading. " + BLADES + ". " + TARGET + ".",
     row(3, 18, 14) + CENTER),
    ("q_tip", "狡诈横扫：刀尖扫中（附加包），3 帧", "view_effects `league_ambessa_q_tip`（附加包播，跟随目标，z 2；左右对称）",
     "20 × 20",
     "附加包：只有被**刀尖**扫中的敌人才多吃伤害（参考 q_broad_tar_shape、q_broad_tar2_shape）："
     "比 q_hit 更狠——**两道琥珀金色的刀痕交叉成一个大 X**（英雄联盟里就是这个 X），一圈锋利的银白色小碎光往外炸。**左右对称**，3 帧。",
     EM + ", " + ST,
     "A CRITICAL EDGE, 3 frames, " + LR + ": 1 a bright white-gold flash 8 squares across; 2 two thick amber-gold slash "
     "marks crossing in a big X 18 squares across, white cores, a ring of small sharp silver glints bursting out at "
     "mirrored places; 3 the X thinner, the glints further out, fading. " + BLADES + ". " + TARGET + ".",
     row(3, 20, 20) + CENTER),
    ("q2_crack", "裂地重击：沿直线往前裂开的地面，4 帧循环",
     "view_projectiles `league_ambessa_q2_crack`（大表，直线，z 2；上下对称）", "44 × 12",
     "裂地重击（参考 q_precise_whipsmash_dirwave、q_precise_whip_decal_shape、q_precise_whipexposion_shape_1）："
     "双刀砸在地上，**一道裂缝沿直线往前裂开**，裂缝里透出琥珀色的光，前头翻起碎石和尘土。**朝右飞、上下对称**，4 帧循环。",
     EM + ", " + SM + ", " + RO,
     "A GROUND RIFT, 4 looping frames, " + TB + ": a jagged crack 40 squares long along the middle line glowing amber "
     "inside, its front a burst of rock chips and dark dust thrown up and down equally, dust settling behind on the left; "
     "the rock chips rise and fall in turn so the loop surges.",
     row(4, 44, 12) + CENTER),
    ("q2_hit", "裂地重击：被砸中，3 帧", "view_effects `league_ambessa_q2_hit`（跟随目标，z 2；左右对称）", "18 × 20",
     "被裂地重击砸中（参考 q_precise_whipsmash_impact_shape）：脚下**一团琥珀色的冲击往上炸**，碎石往两边飞。**左右对称**，3 帧。",
     EM + ", " + RO + ", " + SM,
     "A SLAM FROM ABOVE, 3 frames, " + LR + ": 1 an amber-gold impact burst " + FEET + " 14 wide and a white flash on "
     "the target; 2 rock chips and dark dust flying up and out 18 wide at mirrored places; 3 the dust settling, fading. "
     + TARGET + ".",
     row(3, 18, 20) + CENTER),
    # ---- E Lacerate
    ("e_lash", "割裂：铁链甩着刀绕身转一圈，5 帧", "view_effects `league_ambessa_e_lash`（大表，跟随她，z 3；左右对称）",
     "{ew} × 36",
     "割裂（参考 e_swirl_sharpedge_shape、e_oneshot_ring_swipe_shape、e_swipetrail）：她抡着铁链，"
     "**两把刀在身边甩出一整圈银白色的刀光**（一圈椭圆形的旋风，外圈锋利、琥珀金色的边），铁链在里面，脚下扬起一圈暗色的尘土。"
     "她在中间不画，**身体的位置留空**。**左右对称**，5 帧。",
     ST + ", " + EM + ", " + SM,
     "A WHIRL OF CHAINED BLADES, 5 frames, " + LR + "; " + HER + " - leave her body's place EMPTY: 1 two thin silver arcs "
     "starting at her sides at mirrored places; 2 a full whirling ring of silver-white crescent slashes round her ({ew2} "
     "wide and 30 tall, an ellipse), dark iron chain links inside it, amber-gold outer edges; 3 the ring at its "
     "brightest, amber sparks thrown out at mirrored places, a dark dust ring " + FEET + "; 4 the ring breaking into "
     "streaks; 5 fading streaks and dust. " + BLADES + ".",
     "{erow}" + CENTER),
    ("e_hit", "割裂：被甩中，3 帧", "view_effects `league_ambessa_e_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被铁链甩来的刀割中（参考 e_oneshot_tar_dirimpact_shape）：**一道竖着的银白色月牙刀痕**加几颗琥珀色的火星。**左右对称**，3 帧。",
     ST + ", " + EM,
     "A LASH CUT, 3 frames, " + LR + ": 1 a white-silver vertical crescent slash 12 squares tall in the middle, pointed "
     "at both ends; 2 the slash with amber edges, amber sparks splashing out at mirrored places; 3 fading. " + BLADES
     + ". " + TARGET + ".",
     row(3, 14, 14) + CENTER),
    ("slow", "割裂：减速，脚下缠着的暗色尘土，4 帧循环",
     "view_buffs `league_ambessa_e_slow`（tag `slow`，跟随，脚下，z -1；左右对称）", "18 × 7",
     "被割裂减速的敌人脚下：一小圈**暗色的尘土**绕着脚转，几道细细的银白色划痕一闪一闪。**左右对称**，4 帧循环。",
     SM + ", " + ST,
     "A HOBBLE, 4 looping frames, " + LR + ": a flat dark dust ring " + FEET + " 16 wide and 5 tall, two short thin "
     "silver scratch marks at mirrored places flashing in turn, a dust puff going round.",
     row(4, 18, 7) + CENTER),
    # ---- W Repudiation
    ("w_brace", "拒斥：格挡时身前的护盾光，4 帧", "view_effects `league_ambessa_w_brace`（跟随她，z 3；左右对称；约 0.4 秒）",
     "{bw} × 44",
     "拒斥格挡（参考 w_shieldgradient_shape、w_parry_wind_shape、w_flash_shape）：她举刀挡住，身边**一层青铜金色的护盾光**"
     "罩住她（一个半透明的弧形外壳，边上亮、中间很淡），外面一圈风往两边卷。她在中间不画，**身体的位置留空**。**左右对称**，4 帧。",
     BR + ", " + ST,
     "A BRACING SHELL, 4 frames, " + LR + "; " + HER + " - leave her body's place EMPTY: 1 a bronze-gold flash at her "
     "chest 10 wide; 2 a shell of bronze-gold light round her (a tall dome {bw2} wide and 42 tall: only its rim drawn, "
     "bright and 2 squares thick, a few faint inner shimmer marks), thin silver wind curls at both sides at mirrored "
     "places; 3 the shell steady, the curls further out; 4 the shell flickering, thinner. Light and sparse inside: she "
     "must stay readable.",
     "{brow}" + CENTER),
    ("w_slam", "拒斥：双刀砸地的冲击波，5 帧", "view_effects `league_ambessa_w_slam`（大表，在她身边的地上，跟随她，z -1；左右对称）",
     "54 × 20",
     "拒斥砸地（参考 w_release_shockwave_shape、w_release_ring_shape、w_distortion）：双刀砸在身边的地上，"
     "**地面炸开一圈青铜金色的冲击波**，暗色的尘土和碎石往两边溅起来。**左右对称**，5 帧。",
     BR + ", " + EM + ", " + SM + ", " + RO,
     "A SLAM SHOCKWAVE, 5 frames, " + LR + ": 1 a white-gold impact flash 16 squares wide " + FEET + "; 2 a bronze-gold "
     "shock ring 36 wide, dark dust bursting up at both sides; 3 the ring 52 wide, rock chips flying up at mirrored "
     "places; 4 the rocks falling, amber cracks on the ground; 5 the cracks and the ring fading.",
     row(5, 54, 20) + CENTER),
    ("w_hit", "拒斥：被砸地打中，3 帧", "view_effects `league_ambessa_w_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被拒斥的砸地打中：身上一下青铜金色的闪光，几块碎石往两边弹开。**左右对称**，3 帧。",
     BR + ", " + RO,
     "A SHOCK HIT, 3 frames, " + LR + ": 1 a white-gold flash 6 squares across on the target's chest; 2 a bronze-gold "
     "burst 14 across, rock chips bouncing out at mirrored places; 3 fading. " + TARGET + ".",
     row(3, 16, 16) + CENTER),
    ("w_crit", "拒斥：格挡时挨了打，砸地加强（附加包），4 帧",
     "view_effects `league_ambessa_w_crit`（附加包，跟随目标，z 2；左右对称）", "22 × 22",
     "附加包：格挡时被敌方英雄或野怪打到，砸地就加强——打中的敌人身上**炸开一圈亮金色带一点深红的冲击**，比 w_hit 大一圈、亮一档。"
     "**左右对称**，4 帧。",
     BR + ", " + EM + ", " + CR,
     "A RETALIATION BURST, 4 frames, " + LR + ": 1 a white-gold flash 10 squares across; 2 a bronze-gold burst ring 20 "
     "across with crimson inner sparks at mirrored places; 3 the ring thinning, amber shards flying out; 4 fading. "
     + TARGET + ".",
     row(4, 22, 22) + CENTER),
    # ---- R Public Execution
    ("r_blink", "公开处决：闪走的地方留下的暗影，4 帧",
     "view_effects `league_ambessa_r_blink`（大表，在她出发的地方，不跟随，z 3；左右对称）", "{rw} × 48",
     "公开处决（参考 r_warning_wind_alpha、z_distortion_shape、z_generic_smoke_shape1）：她一下闪到敌人身边，"
     "原地**炸开一团暗色的烟**，几道深红色的风痕往两边卷，烟里是她身体的轮廓、正在散开。**左右对称**，4 帧。",
     SM + ", " + CR,
     "A VANISHING, 4 frames, " + LR + ": 1 her silhouette's place filled with a burst of dark smoke {rw2} wide and 44 "
     "tall, two crimson wind streaks curling out to both sides at mirrored places; 2 the smoke bursting outward, the "
     "streaks longer; 3 the smoke thinning into curls; 4 a few wisps fading.",
     "{rrow}" + CENTER),
    ("r_pin", "公开处决：被按住压制，4 帧循环", "view_effects `league_ambessa_r_pin`（跟随目标，z 2；左右对称；约 0.6 秒）",
     "22 × 30",
     "被她抓住、压制的敌人（参考 ambessa_r_marker、r_position_marker_shape1）：身上**缠着一圈深红色的光**，"
     "脚下一个深红色的标记圈，头顶两道交叉的深红色刀痕（诺克萨斯的处决标记）。**左右对称**，4 帧循环。",
     CR + ", " + ST,
     "A SUPPRESSION MARK, 4 looping frames, " + LR + ": a crimson ring " + FEET + " 20 wide, a thin crimson band "
     "circling the target's waist, above its head a small crimson X of two crossed blade marks 10 squares across with "
     "silver edges; the ring and the band pulse brighter and dimmer in turn. " + TARGET + ".",
     row(4, 22, 30) + CENTER),
    ("r_crash", "公开处决：把敌人砸进地里，6 帧", "view_effects `league_ambessa_r_crash`（大表，在目标的地上，不跟随，z -1；左右对称）",
     "64 × 30",
     "公开处决砸下（参考 r_hurl_impact_shape、r_hurl_impact_decal_shape、r_decalorganic_alpha、r_residual_decal_shape）："
     "把敌人狠狠砸进地里，**地面砸出一个大坑**——一下白金色的闪光，一圈深红带琥珀色的冲击波贴着地往外推，碎石和暗色的尘土往上往两边飞，"
     "最后地上留下一圈裂开的坑。**左右对称**，6 帧。",
     CR + ", " + EM + ", " + SM + ", " + RO,
     "A CRATERING SLAM, 6 frames, " + LR + ": 1 a white-gold impact flash 20 squares wide " + FEET + "; 2 a crimson and "
     "amber shock ring 40 wide on the ground, rock chips and dark dust bursting up at mirrored places; 3 the ring 60 wide, "
     "the rocks high; 4 the rocks falling, a cracked crater on the ground 30 wide with glowing amber cracks; 5 the ring "
     "thin, dust settling; 6 the crater and the cracks fading.",
     row(6, 64, 30) + CENTER),
]
BIG_FX = ["q2_crack", "e_lash", "w_slam", "r_blink", "r_crash"]
FLYING = ["q2_crack"]
FORWARD = ["q_sweep", "st_dash"]
ADDON = ["q_tip", "w_crit"]

GROUPS = [
    ("a_hit pw_hit pw_aura", ["ambessa_base_ba_autoattacks_alpha", "ambessa_base_p_specialattack_swipe_shape",
                              "ambessa_base_p_specialattack_flow_shape", "ambessa_base_p_specialattack_wispymask"]),
    ("st_dash st_land", ["ambessa_base_z_dash_indicator_alpha", "ambessa_base_z_chainsmask_alpha",
                         "ambessa_base_z_generic_smoke_shape1", "ambessa_base_z_motes_shape"]),
    ("q_sweep q_hit q_tip", ["ambessa_base_q_broad_swipe_stylized_alpha", "ambessa_base_q_broad_swipe_chains_shape",
                             "ambessa_base_q_broad_sweetspot_shape", "ambessa_base_q_broad_tar_shape"]),
    ("q2_crack q2_hit", ["ambessa_base_q_precise_whipsmash_dirwave", "ambessa_base_q_precise_whip_decal_shape",
                         "ambessa_base_q_precise_whipexposion_shape_1", "ambessa_base_q_precise_whipsmash_impact_shape"]),
    ("e_lash e_hit slow", ["ambessa_base_e_swirl_sharpedge_shape", "ambessa_base_e_oneshot_ring_swipe_shape",
                           "ambessa_base_e_swipetrail", "ambessa_base_e_oneshot_tar_dirimpact_shape"]),
    ("w_brace w_slam w_hit w_crit", ["ambessa_base_w_shieldgradient_shape", "ambessa_base_w_parry_wind_shape",
                                     "ambessa_base_w_release_shockwave_shape", "ambessa_base_w_flash_shape"]),
    ("r_blink r_pin r_crash", ["ambessa_base_r_warning_wind_alpha", "ambessa_r_marker", "ambessa_base_r_hurl_impact_shape",
                               "ambessa_base_r_hurl_impact_decal_shape"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", ppu=PPU):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / ppu, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Ambessa at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
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
    d.text((8, 36), f"安蓓萨 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def sized(shape):
    """FX with her size filled in: the pictures round her are as wide as she is, and a margin."""
    h, w = shape[:2]
    ew, bw, rw = w + 14, w + 8, w + 6
    her = HER.format(w=w, h=h)
    sub = {"{ew}": str(ew), "{ew2}": str(ew - 4), "{erow}": row(5, ew, 36),
           "{bw}": str(bw), "{bw2}": str(bw - 2), "{brow}": row(4, bw, 44),
           "{rw}": str(rw), "{rw2}": str(rw - 4), "{rrow}": row(4, rw, 48), HER: her}
    out = []
    for x in FX:
        x = list(x)
        for i in (3, 6, 7):
            for k, v in sub.items():
                x[i] = x[i].replace(k, v)
        out.append(tuple(x))
    return out


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 战争女族长 安蓓萨：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/ambessa_design.png`：Q 版的诺克萨斯女军阀——银白色往后梳的波浪短发、"
      "深棕色皮肤、红唇、金耳环；肩上一圈深青绿色的尖毛领；黑铁胸甲、红围巾、红腰布；黑色的大护臂；**两只手各握一把带钩的月牙形龙犬刃**，"
      f"刀柄连着粗铁链）。她在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽，连两把刀）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/ambessa_size.png`：安蓓萨放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里安蓓萨自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。"
      "**安蓓萨的特效是她那两把连着铁链的龙犬刃**：**锋利的银白色月牙刀光**，前沿**琥珀金色**，甩出**琥珀色的火星**，加上**暗色的烟尘和碎石**；"
      "拒斥的护盾是**青铜金色**的光；公开处决加一点**诺克萨斯的深红**。不要魔法光晕、不要电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。")
    a("> - **刀光、冲击波、火星、烟尘都没有黑描边**（用它自己最深的一档）；只有碎石、铁链这种实心的东西有深色的边。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进她自己帧里的**（`" +
      "`、`".join(FORWARD) + "`）**朝右画，不用对称**（她的帧在红色方会镜像）。")
    a("> - **持续的画面**（强化期间的气流、减速、压制）只画几帧循环，Claude 导入时按时长拉开循环。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ambessa_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/ambessa_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 双刀左右开弓地砍 | `a_hit` |")
    a("| 被动「龙犬之步」 | 每放一个技能就往目标冲一步，之后几秒攻速变快、下一刀强化 | `st_dash` · `st_land` · `pw_aura` · `pw_hit` |")
    a("| 技能 1 =「狡诈横扫」→「裂地重击」 | 身前横扫半圈（刀尖扫到的多吃伤害）；扫中以后马上双刀砸地，一道裂缝沿直线往前 | "
      "`q_sweep` · `q_hit` · `q_tip` · `q2_crack` · `q2_hit` |")
    a("| 技能 2 =「割裂」 | 抡着铁链甩刀绕身一圈，打中的减速；冲刺以后再甩一圈 | `e_lash` · `e_hit` · `slow` |")
    a("| 自动放的「拒斥」 | 敌方英雄靠近时格挡（护盾），然后砸地；格挡时挨了打砸地更狠 | `w_brace` · `w_slam` · `w_hit` · `w_crit` |")
    a("| 大招 =「公开处决」 | 闪到敌方英雄身边，按住（压制），再把它砸进地里（眩晕） | `r_blink` · `r_pin` · `r_crash` |\n")
    a("连招：**横扫扫中 → 马上裂地重击**，**每个技能 → 龙犬之步冲刺 → 强化普攻**，**割裂 → 冲刺 → 再甩一圈**，"
      "**公开处决砸下 → 马上横扫 → 裂地重击**，拒斥也重新可用。`q_tip`、`w_crit` 只在附加包里播。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、冲击波、火星、烟尘没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的亮点。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("刀光·银白", STEEL), ("火星·琥珀金", EMBER), ("护盾·青铜金", BRONZE), ("诺克萨斯·深红", CRIMSON),
                        ("烟尘·暗灰褐", SMOKE), ("碎石", ROCK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的东西（冲击波、裂缝、坑、脚下的圈）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `ambessa_fx_{name}.png`：{title}\n")
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
        a(f"| `ambessa_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_ambessa_fx`（小的）和 `league_ambessa_big`（{'、'.join(x for x in BIG_FX if x in [f[0] for f in FX])}），"
      "tag = 名字（build_ambessa.py 的 views；e_slow 用 `slow`，pw 用 `pw_aura`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；朝前的（{'、'.join(FORWARD)}）用 tools/fix/bake_caster_fx.py 画进她的 skill / step 帧，"
      "build_ambessa.py 里的 `q_sweep`、`st_dash` 两个 view 去掉；其余断言左右对称。pw_aura 循环 pw_t，slow 循环 e_slow_t，r_pin 循环 r_sup。")
    a(f"- 附加包的（{'、'.join(ADDON)}）只进 `--native` 的副本（addons/league_ambessa 的 override）。")
    a("- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="ambessa_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "ambessa_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_ambessa.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "ambessa_design.png"))
    shape = size_sheet(os.path.join(out, "design", "ambessa_size.png"))
    FX = sized(shape)
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"ambessa_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
