#!/usr/bin/env python3
"""Build zyra_fx_pack.zip: step 3 of Zyra's sprite - Codex draws her effects (pack_vex_fx.py's way, pack_rammus_fx's
sheets).

    python tools/lol/fx_ref_zyra.py            # League's particle textures + her plants -> C:/t/zy_work/fxref (local only)
    python tools/art/pack_zyra_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name zyra_fx_redo_pack]

The pack (C:/t/zy_work/fx/zyra_fx_pack, zipped into --out, default dist/zyra_packs) holds PROMPTS.md (also written to
assets/source/zyra/PROMPTS_FX.md), design/zyra_idle.png (her idle at 4x, the design's squares at PPU 1.7),
design/zyra_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/zyra_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures and her plants, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_zyra.py) and the add-on's (addons/league_zyra): view_projectiles
a_seed, e_roots, t_spit (the add-on's seed plants' spit); view_effects a_hit, q_burst, q_hit, t_plant, t_hit, v_plant,
v_hit, r_thicket, r_hit, r_knock, s_seed (the add-on's seeds on the ground); view_buffs e_bound, v_slow. League's
colours: her magic is MAGENTA-PINK thorns and GREEN sap and leaves on DARK PURPLE vines. Red side: the client never
mirrors an effect picture, so every hit, buff and ground picture is symmetric left to right and her plants are drawn
from the front; a projectile's picture is turned with its flight (drawn flying right), so it is symmetric top to bottom.
The plants live 5 s: their pictures are long tags (grow, sway with a strike on every second, wilt) the importer times.
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/zy_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "zyra", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_zyra")
NAME = "zyra_fx_pack"

THORN = "#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A"      # her magenta-pink thorns and petals
LEAF = "#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14"       # leaves, vines' green, sap
VINE = "#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C"       # the dark purple vines, roots and stalks
GLOW = "#FFFFFF, #F6FFD2, #DCF58A, #A6DA48"                          # the bright green sap glow
TH = f"a magenta-pink thorn ramp ({THORN})"
LE = f"a leaf-green ramp ({LEAF})"
VI = f"a dark purple vine ramp ({VINE})"
GL = f"a bright sap-green glow ramp ({GLOW})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns "
                       "DO have a 1-square near-black outline like a character")
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
UNIT = "a champion stands in the middle, not drawn: about 16 squares wide and 36 tall"
row = RF.row
FRONT = ("drawn FROM THE FRONT, facing the viewer, its stalk upright in the middle (the game never mirrors it: it must "
         "look right on both sides)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_seed", "普攻：荆棘种子（弹道，循环），4 帧", "view_projectiles `league_zyra_a_seed`（跟着弹道转向；上下对称）", "10 × 8",
     "她普攻甩出去的一颗荆棘种子：粉红色的小种球，两片小绿叶，后面拖一小段粉红色的火花尾迹（参考 w_seed、aa_mis_trail、flare_pink）。"
     "**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     f"{TH} and {LE}",
     "A THORNY SEED, 4 frames, a seamless loop, " + TB + ": at the right a magenta-pink seed bulb 4 squares across with a "
     "1-square near-black outline and a white glint, two tiny green leaf flicks at its back (one above, one mirrored "
     "below); behind it to the left a short tapering pink spark trail 4 squares long; each frame the trail flickers "
     "(symmetric top and bottom).",
     row(4, 10, 8) + "; the bulb's middle on the cell's middle row, 3 squares from its right edge."),
    ("a_hit", "普攻：打中目标，3 帧", "view_effects `league_zyra_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "种子打中目标：一团粉红色的小闪光，几片碎叶和绿色汁液溅开（参考 flare_pink、leaves、poison_spatter）。**左右对称**。",
     f"{TH}, {LE} and {GL}",
     "A SMALL SEED HIT, 3 frames, " + LR + ": 1 a pink-white four-pointed flash 6 squares across; 2 the flash 9 across with "
     "4 small green leaf bits and sap drops at mirrored places; 3 only the leaf bits further out, fading.",
     row(3, 12, 12) + CENTER),
    # ---- Q Deadly Spines + the Thorn Spitter
    ("q_burst", "Q 致命棘刺：目标点地面炸出棘刺（地上，不跟随），6 帧",
     "view_effects `league_zyra_q_burst`（不跟随，画在人物下面 z -1；左右对称；大图表）", "48 × 30",
     "Q 落点：先是一片绿色的藤蔓在地上铺开（一个扁的椭圆），裂缝里透出粉红色的光，然后一簇又高又尖的粉红色棘刺从藤蔓里猛地刺出来，"
     "带着绿色汁液溅起，最后棘刺缩回、藤蔓碎叶散掉（参考 q_vinesbase、q_spines、q_leaves、ground_cracks）。**左右对称**，6 帧。范围约 44 格宽。",
     f"{TH}, {LE}, {VI} and {GL}",
     "DEADLY SPINES bursting from the ground, 6 frames, " + LR + ": 1 thick green vines spreading flat across the ground "
     "(a flat ellipse 30 squares wide and 8 tall); 2 the vines covering an ellipse 44 wide and 13 tall, pink light glowing "
     "in the cracks between them; 3 a cluster of 9 tall magenta-pink thorn spikes bursting up out of the vines at mirrored "
     "places (the middle one 22 squares tall, the outer ones shorter), each spike with a 1-square near-black outline; "
     "4 the spikes at full height, green sap splashing off them; 5 the spikes sinking back to half height; 6 only "
     "scattered vine bits and leaves on the ground, fading.",
     row(6, 48, 30) + "; centered across, the ellipse's middle 7 squares above the cell's bottom row."),
    ("q_hit", "Q：棘刺扎中目标，4 帧", "view_effects `league_zyra_q_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 14",
     "棘刺扎中目标：粉红色的尖刺从下往上扎了一下，闪一下光，绿色汁液溅开（参考 poison_spike、flare_pink）。**左右对称**。",
     f"{TH} and {GL}",
     "A SPINE STAB, 4 frames, " + LR + ": 1 three sharp pink thorn spikes stabbing up from the bottom (the middle one 8 "
     "tall); 2 a pink-white flash 9 across where they meet, green sap drops flying out; 3 the flash 13 across, the "
     "spikes gone; 4 only fading sap drops.",
     row(4, 14, 14) + CENTER),
    ("t_plant", "荆棘喷射者：种子长出来、站着摇、吐刺、枯萎（地上，不跟随），10 帧",
     "view_effects `league_zyra_t_plant`（不跟随，画在人物下面 z 0；左右对称；大图表；活 5 秒）", "20 × 26",
     "Q 长出来的植物（英雄联盟的荆棘喷射者，附图里的 plant_thorn_spitter）：一株深紫色的弯茎植物，顶上一个**粉红色的大花苞头**，"
     "花苞外面包着绿色的萼片，根部是一圈深紫色的叶子。**从正面画**（花苞头正对着看的人），10 帧：1–3 从地上的种子长出来（种子裂开、"
     "冒出芽、长成整株）；4–7 站着轻轻摇摆（左、中、右、中）；8 吐刺（花苞张开、里面露出粉红色的光）；9–10 枯萎缩回地里。"
     "实心的植物有 1 格近黑描边，像人物一样。",
     f"{VI}, {TH} and {LE}",
     "A THORN SPITTER PLANT, " + FRONT + ", 10 frames: 1 a pink seed bulb on the ground cracking open; 2 a dark purple "
     "sprout 8 squares tall with a small closed bud; 3 the grown plant - a dark purple stalk 14 squares tall rising from a "
     "ring of dark purple leaves at the ground, on top a big magenta-pink flower-bud head 8 squares across wrapped in green "
     "sepals, facing the viewer; 4 to 7 the plant swaying gently (the head a square left, back in the middle, a square "
     "right, back in the middle); 8 the bud opening wide, pink light glowing inside it (spitting); 9 the plant drooping, "
     "its head hanging; 10 it shrinking back into a small heap of withered leaves. 1-square near-black outline round the "
     "solid plant.",
     row(10, 20, 26) + "; centered across, its leaves' bottom on the cell's bottom row."),
    ("t_hit", "荆棘喷射者：吐的刺打中，3 帧", "view_effects `league_zyra_t_hit`（跟随目标，画在人物上面 z 2；左右对称）", "10 × 10",
     "植物吐的刺打中敌人：一下小小的粉红色刺爆（参考 poison_spike）。**左右对称**。",
     f"{TH} and {GL}",
     "A SMALL THORN HIT, 3 frames, " + LR + ": 1 a pink flash 4 across; 2 4 tiny pink thorn shards flying out at mirrored "
     "diagonals; 3 only two fading sparks.",
     row(3, 10, 10) + CENTER),
    ("t_spit", "荆棘喷射者：吐出来的刺（弹道，附加包用，循环），2 帧",
     "view_projectiles `league_zyra_t_spit`（附加包：种子长出来的植物吐的刺；跟着弹道转向；上下对称）", "8 × 4",
     "附加包里植物吐出去的一根刺：一根细长的粉红色尖刺，后面一点点火花。**朝右飞，上下严格对称**，2 帧循环。",
     TH,
     "A FLYING THORN, 2 frames, a seamless loop, " + TB + ": a slim magenta-pink spine 6 squares long, pointed at the right, "
     "1-square near-black outline, a 2-square spark behind it that flickers.",
     row(2, 8, 4) + "; the spine on the cell's middle row."),
    # ---- E Grasping Roots + the Vine Lasher
    ("e_roots", "E 缠绕之根：贯穿地面的藤蔓（弹道，循环），4 帧",
     "view_projectiles `league_zyra_e_roots`（跟着弹道转向；上下对称）", "22 × 10",
     "E 放出去的藤蔓：地面裂开往前窜，裂缝里冒出一丛丛带刺的深紫色藤蔓和绿叶，最前面的藤蔓头张开（参考 rootgrasp、props_vines_green、"
     "ground_cracks）。**朝右窜，后面在左边，上下严格对称**，4 帧循环。",
     f"{VI}, {LE} and {TH}",
     "GRASPING ROOTS tearing along the ground, 4 frames, a seamless loop, " + TB + ": a band of thorny dark purple vines and "
     "green leaves 22 squares long and 8 tall, thickest at the right where a cluster of vine tips curls open with pink "
     "thorns, thinning to a crack with small sprouts at the left; each frame the vines writhe and new sprouts pop up "
     "(symmetric top and bottom). 1-square near-black outline round the solid vines.",
     row(4, 22, 10) + "; the band on the cell's middle row, its head 2 squares from the right edge."),
    ("e_bound", "E：被藤蔓缠住脚（敌人脚下，循环），4 帧",
     "view_buffs `league_zyra_e_bound`（跟随，画在人物上面 z 3；左右对称；循环；禁锢期间）", "20 × 16",
     "被禁锢的时候：地上冒出几根深紫色带刺的藤蔓缠住敌人的脚和小腿，藤蔓尖上冒绿光（参考 rootgrasp、props_vines_green）。"
     "**只画藤蔓（人站在中间不画）**，**左右对称**，4 帧循环。",
     f"{VI}, {LE} and {GL}",
     "ROOTS BINDING a unit's legs, 4 frames, a seamless loop, " + LR + " (" + UNIT + ", only the bottom 14 squares of the "
     "cell used): 4 thorny dark purple vines rising from the ground at both sides of the legs and coiling across in front "
     "of them up to 12 squares high, small green leaves on them, glowing green tips; each frame the vines tighten and "
     "loosen a square. 1-square near-black outline round the solid vines.",
     row(4, 20, 16) + "; centered across, the roots' bottom on the cell's bottom row."),
    ("v_plant", "藤蔓鞭击者：种子长出来、站着摇、抽打、枯萎（地上，不跟随），10 帧",
     "view_effects `league_zyra_v_plant`（不跟随，画在人物下面 z 0；左右对称；大图表；活 5 秒）", "18 × 28",
     "E 长出来的植物（英雄联盟的藤蔓鞭击者，附图里的 plant_vine_lasher）：一根深紫色带刺的长藤茎从一丛深紫色的叶子里竖起来，"
     "顶端是一个粉红色的矛尖，茎上一排粉红色的刺。**从正面画**，10 帧：1–3 从种子长出来；4–7 站着摇摆（左、中、右、中）；"
     "8 抽打（藤茎猛地卷成一个 S 形、矛尖一闪）；9–10 枯萎缩回地里。实心的植物有 1 格近黑描边。",
     f"{VI}, {TH} and {LE}",
     "A VINE LASHER PLANT, " + FRONT + ", 10 frames: 1 a pink seed bulb on the ground cracking open; 2 a dark purple sprout "
     "9 squares tall; 3 the grown plant - a thorny dark purple vine stalk 22 squares tall rising from a clump of dark "
     "purple leaves at the ground, a row of small pink thorns along it, a magenta-pink spearhead tip at the top; 4 to 7 "
     "the stalk swaying (its top 2 squares left, back in the middle, 2 squares right, back in the middle); 8 the stalk "
     "whipping into an S-curve, its tip flashing pink-white (lashing); 9 the stalk drooping over; 10 it shrinking back into "
     "a small heap of withered leaves. 1-square near-black outline round the solid plant.",
     row(10, 18, 28) + "; centered across, its leaves' bottom on the cell's bottom row."),
    ("v_hit", "藤蔓鞭击者：抽中目标，3 帧", "view_effects `league_zyra_v_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 12",
     "藤蔓抽中敌人：一道交叉的绿色鞭痕闪一下，几片碎叶（参考 flash_green_sharp、leaves）。**左右对称**。",
     f"{LE} and {GL}",
     "A VINE LASH HIT, 3 frames, " + LR + ": 1 two crossing bright green lash streaks (an X 10 wide); 2 the X flashing "
     "green-white with 4 leaf bits flying out at mirrored places; 3 only the leaf bits, fading.",
     row(3, 14, 12) + CENTER),
    ("v_slow", "藤蔓鞭击者：被减速（敌人脚下，循环），4 帧",
     "view_buffs `league_zyra_v_slow`（跟随，画在人物下面 z -1；左右对称；循环）", "18 × 6",
     "被藤蔓鞭击者减速：敌人脚下一小滩黏糊糊的绿色汁液，冒出几根细细的小藤须（参考 slime、poison_dots）。**只画在脚下的地面上**，"
     "**左右对称**，4 帧循环。",
     f"{LE} and {GL}",
     "STICKY SAP at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat green sap ellipse 16 wide and 3 tall with "
     "bright glints, 3 tiny curling vine tendrils (2-3 squares) rising from it at mirrored places; each frame the tendrils "
     "curl and the glints move.",
     row(4, 18, 6) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- R Stranglethorns
    ("r_thicket", "R 绞杀之藤：扭曲的密林（地上，不跟随），10 帧",
     "view_effects `league_zyra_r_thicket`（不跟随，画在人物下面 z -1；左右对称；大图表；约 3 秒）", "70 × 44",
     "大招：目标点的地上先亮起一圈绿色的符文环，里面藤蔓疯长，长成一片扭曲的带刺密林（深紫色的藤蔓纠缠成一圈矮丛，上面开着粉红色的刺和花苞），"
     "在里面扭动两秒，然后所有藤蔓**猛地往上一收、像笼子一样合拢**（把里面的人击飞），最后散成碎叶（参考 rootgrasp、e_groundring、"
     "plant_props、buf_enrage）。**左右对称**，10 帧。范围约 64 格宽。",
     f"{VI}, {LE}, {TH} and {GL}",
     "STRANGLETHORNS, a twisted thicket, 10 frames, " + LR + ": 1 a bright green rune ring on the ground (a flat ellipse 64 "
     "squares wide and 20 tall) with 4 small leaf sigils at mirrored places; 2 green vines sprawling inside it; 3 dark "
     "purple thorny vines rising all round the ring into a low tangled thicket 10 squares tall; 4 to 6 the thicket "
     "writhing (3 frames that loop: the vines twist a square, pink thorns and buds on them pulse); 7 the vines whipping "
     "upward and inward like a closing cage, 30 squares tall in the middle; 8 the cage snapping shut with a burst of "
     "pink-white light at its top; 9 the vines falling apart; 10 only leaves and a fading ring. 1-square near-black outline "
     "round the solid vines (none round light or rings).",
     row(10, 70, 44) + "; centered across, the ellipse's middle 10 squares above the cell's bottom row."),
    ("r_hit", "R：密林打中，4 帧", "view_effects `league_zyra_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "密林长出来时打中里面的敌人：几根带刺的藤蔓抽过去，粉红绿色的闪光（参考 flare_pink、flash_green_sharp）。**左右对称**。",
     f"{TH}, {LE} and {GL}",
     "A THORN BURST, 4 frames, " + LR + ": 1 a pink-white flash 7 across; 2 4 thorny vine lashes crossing it at mirrored "
     "diagonals; 3 a green sap ring 14 across, the lashes fading; 4 only sap drops.",
     row(4, 16, 16) + CENTER),
    ("r_knock", "R：藤蔓把敌人往上掀（他身上），4 帧", "view_effects `league_zyra_r_knock`（跟随目标，画在人物上面 z 2；左右对称）",
     "16 × 26",
     "密林合拢、把敌人击飞：一丛带刺的深紫色藤蔓从他脚下猛地往上冲，藤蔓尖上闪粉红色的光（参考 rootgrasp、poison_spike）。"
     "**人站在中间不画**，**左右对称**，4 帧。",
     f"{VI}, {TH} and {GL}",
     "VINES SURGING UP under a unit, 4 frames, " + LR + " (" + UNIT + ", its body area left EMPTY): 1 vine tips breaking the "
     "ground at both sides of its feet; 2 thorny dark purple vines shooting up both sides to 18 squares; 3 the vines at "
     "24 squares, their pink tips flashing, curling in over its head; 4 the vines falling away, sap drops. 1-square "
     "near-black outline round the solid vines.",
     row(4, 16, 26) + "; centered across, the vines' bottom on the cell's bottom row."),
    # ---- the add-on's seeds
    ("s_seed", "种子：落在地上的种子（地上，附加包用，循环），4 帧",
     "view_effects `league_zyra_s_seed`（附加包：她身边掉在地上的种子，每 1 秒重放；不跟随；左右对称）", "10 × 8",
     "附加包里掉在地上的种子（英雄联盟 W 的种子，附图里的 plant_seed）：一颗粉红色的种球，下面几片绿叶托着，一闪一闪地发光。"
     "**左右对称**，4 帧循环（1 秒一轮）。",
     f"{TH} and {LE}",
     "A SEED ON THE GROUND, 4 frames, a seamless loop, " + LR + ": a magenta-pink seed bulb 5 squares across, closed like a "
     "bud, cupped by 4 green leaves at the ground, 1-square near-black outline; each frame a soft pink glow round it pulses "
     "(1 square wider on frames 2 and 3).",
     row(4, 10, 8) + "; centered across, the leaves' bottom on the cell's bottom row."),
]
BIG_FX = ["q_burst", "t_plant", "v_plant", "r_thicket"]
FLYING = ["a_seed", "t_spit", "e_roots"]
GROUPS = [
    ("a_seed a_hit t_spit t_hit", ["zyra_base_w_seed", "zyra_base_aa_mis_trail", "zyra_base_flare_pink", "zyra_base_leaves",
                                   "zyra_base_poison_spike", "zyra_base_poison_spatter"]),
    ("q_burst q_hit", ["zyra_base_q_vinesbase", "zyra_q_spines", "zyra_base_q_leaves", "zyra_base_ground_cracks",
                       "zyra_base_q_dustpuffs", "zyra_base_q_flares"]),
    ("t_plant v_plant s_seed", ["plant_thorn_spitter", "plant_vine_lasher", "plant_seed", "zyra_base_plant_props",
                                "zyra_base_plant_props_02"]),
    ("e_roots e_bound v_hit v_slow", ["zyra_base_rootgrasp", "zyra_base_props_vines_green", "zyra_base_flash_green_sharp",
                                      "zyra_base_slime", "zyra_base_poison_dots", "zyra_base_spore"]),
    ("r_thicket r_hit r_knock", ["zyra_base_e_groundring", "zyra_base_plant_props_green_vines", "zyra_base_buf_enrage",
                                 "zyra_base_flare_green", "zyra_base_p_wisps"]),
]
SHOTS = [("attack", 3, "a_seed：甩到身前的手，种子从这里飞出去；a_hit 在目标身上"), ("skill", 3, "q_burst：双手甩开，目标点地面炸出棘刺"),
         ("skill2", 3, "e_roots：手砸到地上，藤蔓从这里往前窜"), ("ult", 4, "r_thicket：双手张开召唤，目标点长出密林"),
         ("idle", 1, "待机（大小参考）")]


def configure():
    """pack_rammus_fx's sheets drawn from Zyra's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "婕拉"


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.7)."""
    import rig_zyra as Z
    D = Z.Design()
    t = D.d0
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 荆棘之兴 婕拉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/zyra_idle.png`：3/4 正面朝右的植物女人，一大蓬深红-品红的头发、"
      f"两只黄绿色的叶片角，绿叶抹胸和短裤，深紫色带刺的长腿，手腕上垂着品红色的鞭藤）。她在游戏里是**高清**的（每个游戏格子里 1.7×1.7 个"
      f"细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/zyra_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/zyra_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里婕拉自己的特效贴图和她的三种植物（荆棘喷射者、藤蔓鞭击者、种子），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她的魔法是品红-粉红色的刺**，**绿色的叶子和汁液**，长在**深紫色的藤蔓**上。")
    a("> - **植物是她的标志**：Q 落点长出荆棘喷射者（粉红花苞头的植物），E 落点长出藤蔓鞭击者（带矛尖的长藤），大招是一整片扭曲的密林。"
      "植物在地上活 5 秒，图里画出**长出来 → 站着摇 → 出手 → 枯萎**，Claude 按时间拼成一条长动画。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯；深紫色的藤蔓要有偏紫的亮边，暗底上一眼能看见。")
    a("> - **实心的东西（植物、藤蔓、树根、刺）有 1 格近黑描边**，像人物一样；**光、汁液、闪光、符文环没有描边**。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**植物从正面画**（正对着看的人，"
      "摇摆的那几帧左右各一次）。**弹道图**（种子、吐的刺、藤蔓）**朝右飞、后面在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zyra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/zyra_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 甩出一颗荆棘种子 | `a_seed` · `a_hit` |")
    a("| 技能 1 = Q「致命棘刺」 | 目标点地面炸出棘刺，种子长成荆棘喷射者，每秒吐刺打一个敌人 | `q_burst` · `q_hit` · `t_plant` · `t_hit` |")
    a("| 技能 2 = E「缠绕之根」 | 贯穿地面的藤蔓禁锢一条线上的敌人，种子长成藤蔓鞭击者，每秒抽打并减速 | `e_roots` · `e_bound` · `v_plant` · "
      "`v_hit` · `v_slow` |")
    a("| 大招「绞杀之藤」 | 目标点长出扭曲的密林，打中里面的敌人，2 秒后合拢把还在里面的敌人击飞 | `r_thicket` · `r_hit` · `r_knock` |")
    a("| 附加包（被动「荆棘花园」） | 种子落在她身边的地上，Q / E 落在种子旁边多长一株植物，植物吐出看得见的刺 | `s_seed` · `t_spit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、汁液、闪光、符文环没有黑描边**；**植物、藤蔓、树根、刺有 1 格近黑描边**。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("品红-粉红的刺和花", THORN), ("叶子和藤蔓的绿", LEAF), ("深紫色的藤蔓、树根、植物的茎", VINE),
                        ("亮绿色的汁液光", GLOW)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（棘刺的藤蔓、密林的符文环、减速的汁液）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，Q 的爆炸半径 22000，"
      "大招密林的半径 32000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `zyra_fx_{name}.png`：{title}\n")
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
        a(f"| `zyra_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_zyra_fx`（小的）和 `league_zyra_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_zyra.py 的 views；s_seed、t_spit 是附加包副本的 views）。")
    a(f"- 弹道图（{'、'.join(FLYING)}）断言上下对称，其余断言左右对称（植物的摇摆帧除外）；q_burst、t_plant、v_plant、r_thicket 不跟随（落点）。")
    a("- 植物的长 tag：长出来 3 帧（共约 0.3 秒，第一次出手前），之后每 1 秒一轮：出手帧 + 4 帧摇摆，最后 2 帧枯萎，总长 = 植物活的时间"
      "（build_zyra.P 的 t_life / v_life）；密林的 tag：符文环、长出来、扭动循环到 r_knock、合拢、散掉。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（实心植物的描边保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="zyra_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "zyra_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_zyra.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "zyra_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "zyra_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "zyra_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"zyra_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "left-right"} for x in FX], f,
                  ensure_ascii=False, indent=1)
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
