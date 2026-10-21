#!/usr/bin/env python3
"""Build ornn_fx_pack.zip: step 3 of Ornn's sprite - Codex (or Gemini) draws his effects (pack_mel_fx.py's way,
pack_rammus_fx's sheets).

    python tools/lol/fx_ref_ornn.py         # League's particle textures -> C:/t/on_work/fxref (Riot's art, local only)
    python tools/art/pack_ornn_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name ornn_fx_redo_pack]

The pack (C:/t/on_work/fx/ornn_fx_pack, zipped into --out, default C:/t/on_work) holds PROMPTS.md (also written to
assets/source/ornn/PROMPTS_FX.md), design/ornn_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/ornn_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/ornn_shots.png (action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle
textures for Ornn grouped by the effect they inform, and League's ram - OrnnRam in his WAD - from above, from the side
and as it springs up: rendered here with tools/lol/pose_ref.py).
The effects are the views the kit binds (tools/kit/build_ornn.py): view_projectiles q_fissure, r_ram (r_ram2 takes the
same picture); view_effects a_hit, br_pop, w_fire, w_hit, q_slam, q_hit, q_rise, q_pillar, e_quake, e_hit, r_call,
r_rise, r_butt, r_hit; view_buffs brittle, w_shown. League's colours: his fire is forge fire - a white-yellow core,
yellow-orange body, red-orange edges, dark smoke; his rock is dark basalt with glowing orange cracks; the ram is dark
rock with crimson horns and molten legs. Red side: the client never mirrors an effect picture, so every hit, buff,
ground and caster picture is symmetric left to right; the two projectiles (the fissure's head, the ram seen from above)
point right and are symmetric top to bottom (the game turns them to their flight); the fire breath w_fire has a front
and a back, so it goes into his own skill_w frames (tools/fix/bake_caster_fx.py) and points right.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/on_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "ornn", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_ornn")
NAME = "ornn_fx_pack"

FIRE = "#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A"      # forge fire, lava, glowing cracks
ROCK = "#9C8F94, #6E6168, #463B44, #2A2129, #140E14"               # dark basalt (solid: outlined)
DUST = "#EFE2CC, #C9B394, #9A8366, #6B5843"                        # dust
HORN = "#FF8A9A, #E2334F, #A01A35, #5E1024, #2A0A14"               # the ram's crimson horns
FI = f"a forge-fire ramp ({FIRE})"
RO = f"a dark basalt ramp ({ROCK})"
DU = f"a dust ramp ({DUST})"
HO = f"a crimson horn ramp ({HORN})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so it must look the "
      "same upside down)")
CENTER = RF.CENTER
HIM = ("the huge horned smith stands in the middle, not drawn: 44 squares from the top of his horns to the ground, about "
       "47 squares wide")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
row = RF.row
POINT = "POINTING RIGHT (its head at the cell's right, its tail toward the left; the game turns it to its flight)"
SOLID = "a near-black outline round the solid rock only (never round fire, sparks, dust or glow)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack, the passive (Brittle), W in the attack
    ("a_hit", "普攻打中：大锤砸击，4 帧", "view_effects `league_ornn_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "18 × 18",
     "大锤砸中目标：中间一闪白黄的冲击光，一圈橙红的火星和灰色碎石向两边飞溅，底下扬起一点灰尘，最后剩几粒火星（参考 ba_clouds、"
     "z_splash_2x2、r_sparks-orange）。**左右对称**，4 帧。",
     FI + " and " + DU,
     "A HAMMER IMPACT, 4 frames, " + LR + ": 1 a white-yellow flash 6 squares across ringed with short orange sparks; 2 a "
     "burst 16 across - orange-red embers flying out at mirrored angles, small grey rock chips, a puff of dust at the "
     "bottom; 3 the embers further out and smaller, the dust spreading; 4 a few fading embers and dust.",
     row(4, 18, 18) + CENTER),
    ("br_pop", "易碎引爆：烧红的外壳炸裂，5 帧", "view_effects `league_ornn_br_pop`（跟随目标，z 2；左右对称）", "26 × 26",
     "普攻打中**易碎**的英雄：他身上一层烧红开裂的外壳猛地炸开——先是一圈发光的裂纹，然后白黄的闪光，几块带橙色发光边的黑色碎壳向"
     "四周飞出，火星四溅（参考 q_jhin_base_e_ash、bufftransfer_sparkle_red、recall_ember）。**左右对称**，5 帧。",
     FI + " and " + RO,
     "A BRITTLE SHELL SHATTERING, 5 frames, " + LR + ": 1 a jagged ring of glowing orange crack lines 16 squares across; "
     "2 a white-yellow flash 10 across in the middle, the cracks blazing; 3 dark rock shards (each 2-3 squares, with "
     "glowing orange edges) flying out in a mirrored ring 22 across, orange sparks between them; 4 the shards further out "
     "and smaller, falling; 5 a few fading embers. " + SOLID + ".",
     row(5, 26, 26) + CENTER),
    ("brittle", "易碎（敌人头上，循环），4 帧", "view_buffs `league_ornn_brittle`（跟随目标，z 3；左右对称；循环）", "14 × 10",
     "被奥恩的 W / E / R 打中的英雄**易碎**了：头上一枚小小的裂开的熔岩印记——一块黑色的圆石，十字形的裂缝里透着橙黄色的光，一明"
     "一暗地跳动（参考 livingforge_base_z_glow、recall_ember）。**左右对称**，4 帧循环。",
     RO + " and " + FI,
     "A SMALL CRACKED EMBER SIGIL over a head, 4 frames, a loop, " + LR + ": a dark rock disc 8 squares across with a "
     "jagged cross-shaped crack glowing orange-yellow; 1 dim, 2 the crack brighter, 3 the brightest with two tiny sparks "
     "above it at mirrored places, 4 dim again. " + SOLID + ".",
     row(4, 14, 10) + CENTER),
    ("w_fire", "W 风箱炎息：朝前喷出的火（他嘴里，循环），6 帧",
     "view_effects `league_ornn_w_fire`（他自己的 skill_w 帧里：烤进动作帧，bake_caster_fx；头朝右；大图表）", "48 × 30",
     "奥恩低头朝前喷出的一大股火焰：从格子左边中间（他的嘴）开始，朝右越来越宽的锥形火焰，芯是白黄，身子橙黄，边上卷起一团团红橙的"
     "火舌和几缕黑烟，尽头散成火星（参考 w_rumble_skin03_r_flamemesh、w_fuzzyshad、w_sparks-orange、distort-heat）。**头朝右**"
     "（这张会画进他自己的动作帧里，红色方随人物一起翻过来），6 帧循环，火舌一帧一帧往前翻滚。",
     FI,
     "A ROARING FIRE BREATH, 6 frames, a loop, POINTING RIGHT (its root at the cell's left middle - his mouth - widening to "
     "the right): a cone of fire 46 squares long, 4 squares tall at the root and 26 at the far end, a white-yellow core "
     "along its middle, a yellow-orange body, red-orange curling tongues on its edges and a few dark smoke puffs on top, "
     "embers scattering past its end; each frame the tongues roll forward (the loop seamless).",
     row(6, 48, 30) + "; the cone's root touching the cell's left side, vertically centered."),
    ("w_hit", "喷火打中：小火舌，3 帧", "view_effects `league_ornn_w_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "喷火每一下打中敌人：身上冒起一小簇火舌。**左右对称**，3 帧。",
     FI,
     "A SMALL FLAME LICK, 3 frames, " + LR + ": 1 an orange flame 4 squares wide and 5 tall with a yellow core; 2 two "
     "tongues 7 wide and 8 tall; 3 fading embers.",
     row(3, 10, 10) + CENTER),
    ("w_shown", "风箱炎息的护盾（他身上，循环），4 帧", "view_buffs `league_ornn_w_shown`（跟随他，z 3；左右对称；循环）", "60 × 54",
     "喷火时他得到的护盾：围着他一圈像烧红的铁一样的热浪外框——橙红色发光的椭圆，顶上更亮，零星往上飘的火星；**中间他的身体位置"
     "留空**，不要盖住人（参考 livingforge_base_w_metal_texture、distort-heat）。**左右对称**，4 帧循环。",
     FI,
     "A HEAT SHIELD round a huge figure, 4 frames, a loop, " + LR + " (" + HIM + ", his body area left EMPTY): an oval "
     "outline 56 squares wide and 50 tall, 2 squares thick, of glowing orange-red heat like red-hot iron, a brighter "
     "yellow rim along its top, small sparks rising from it at mirrored places; each frame the glow ripples round the oval "
     "and the sparks move up.",
     row(4, 60, 54) + CENTER),
    # ---- Q Volcanic Rupture (the combo's pillar)
    ("q_slam", "Q 熔岩拳砸地（他脚下），5 帧", "view_effects `league_ornn_q_slam`（他身上，不跟随，画在人物下面 z -1；左右对称；大图表）",
     "44 × 16",
     "熔岩拳砸地：他脚下的地面炸开一圈尘土和碎石，几道发红的裂缝朝左右两边延伸出去（参考 q_aatrox_r_explosion_firering、"
     "q_dustcloud_erosion）。从斜上方看的地面，**左右对称**，5 帧。",
     FI + ", " + DU + " and " + RO,
     "A GROUND SLAM at his feet, seen from slightly above, 5 frames, " + LR + ": 1 a white-yellow flash on the ground 8 "
     "squares wide; 2 a dust ring 30 wide and 8 tall, rock chips jumping up at mirrored places, red-orange cracks starting "
     "in the ground; 3 the dust ring 40 wide, the glowing cracks running out to both sides; 4 the dust thinning, the cracks "
     "dimmer; 5 faint dust and two dim cracks.",
     row(5, 44, 16) + CENTER),
    ("q_fissure", "Q 火山突堑：贴地冲出的裂隙头（弹道，循环），3 帧",
     "view_projectiles `league_ornn_q_fissure`（弹道：游戏会转到前进方向；头朝右、上下对称；大图表）", "22 × 12",
     "裂隙往前冲的那一头，**从正上方看**：地面被撕开一道锯齿形的口子，口子里透着黄橙的熔岩光，前端最宽、熔岩和火星往两边喷，后面渐渐"
     "收窄成一道细缝（参考 q_new_solar_tag、z_rockdebris）。**头朝右、上下严格对称**（游戏会把它转到前进方向），3 帧循环。",
     FI + " and " + RO,
     "THE HEAD OF A RUNNING GROUND FISSURE seen from directly above, 3 frames, a loop, " + POINT + " and " + TB + ": a "
     "jagged crack in dark rock 20 squares long, glowing yellow-orange inside, 8 squares wide at its head where lava "
     "drops and sparks spurt out at mirrored places, narrowing to 2 at its left end; each frame the spurts and sparks "
     "change.",
     row(3, 22, 12) + "; the crack centred vertically, its head touching the cell's right side."),
    ("q_hit", "裂隙打中：熔岩碎石溅射，4 帧", "view_effects `league_ornn_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "裂隙打中敌人：一闪橙光，熔岩滴和黑色碎石向两边溅起又落下。**左右对称**，4 帧。",
     FI + " and " + RO,
     "A LAVA AND ROCK SPLASH, 4 frames, " + LR + ": 1 an orange flash 5 squares across; 2 lava drops and dark rock chips "
     "flung up and out 12 across at mirrored places; 3 falling, smaller; 4 a few embers.",
     row(4, 14, 14) + CENTER),
    ("q_rise", "Q 熔岩柱升起（裂隙尽头的地上，不跟随），6 帧",
     "view_effects `league_ornn_q_rise`（放在裂隙尽头，不跟随，z 1；左右对称；大图表）", "20 × 44",
     "裂隙尽头升起的柱子（**Q→E 连招撞的就是它**）：先是地面隆起裂开、裂缝里透出橙光，然后一根尖顶的黑色玄武岩柱一截一截顶出来，"
     "柱身上爬着发光的橙黄裂纹，柱脚一圈碎石。**左右对称**，6 帧，最后一帧就是立好的柱子（和下一张 q_pillar 外形一样）。",
     RO + ", " + FI + " and " + DU,
     "A BASALT PILLAR RISING from the ground, 6 frames, " + LR + ", its base on the cell's bottom row: 1 the ground bulging "
     "and cracking, orange light in the cracks, dust 16 squares wide; 2 a jagged rock tip 6 squares tall breaking out, "
     "sparks; 3 the pillar 18 tall; 4 30 tall, dust and pebbles falling off it; 5 40 tall; 6 the finished pillar 42 tall "
     "and 14 wide: a chunky column of dark basalt with a pointed jagged top, glowing yellow-orange cracks running down it, "
     "a ring of broken rocks round its base. " + SOLID + ".",
     row(6, 20, 44) + "; the pillar centered across, its base on the cell's bottom row."),
    ("q_pillar", "熔岩柱（立着，循环），2 帧", "view_effects `league_ornn_q_pillar`（裂隙尽头，每 0.25 秒盖一次，z 1；左右对称；大图表）",
     "20 × 44",
     "立好的柱子，**和 q_rise 第 6 帧外形完全一样**，只是裂纹里的熔岩一明一暗。**左右对称**，2 帧循环。",
     RO + " and " + FI,
     "THE FINISHED BASALT PILLAR exactly as frame 6 of the previous sheet (42 squares tall, 14 wide, its base on the "
     "cell's bottom row, " + LR + "), 2 frames, a loop: 1 its glowing cracks dimmer, 2 brighter with a tiny ember rising "
     "from its top. " + SOLID + ".",
     row(2, 20, 44) + "; the pillar centered across, its base on the cell's bottom row."),
    # ---- E Searing Charge (the combo's quake)
    ("e_quake", "E 撞柱的地震（以他为中心），6 帧", "view_effects `league_ornn_e_quake`（他身上，不跟随，z -1；左右对称；大图表）",
     "64 × 26",
     "**Q→E 连招**：冲撞撞碎柱子（附加包里撞墙也算）的一瞬，他脚下炸开一圈冲击波——地面裂开、尘土和火焰翻卷，柱子的黑色碎石块向"
     "四周飞起再落下（参考 e_sion_base_r_explo_clouds、e_cas_spit、riftherald_smoke_dust）。从斜上方看的地面，**左右对称**，6 帧。",
     FI + ", " + RO + " and " + DU,
     "A QUAKE SHOCKWAVE at his feet, seen from slightly above, 6 frames, " + LR + ": 1 a white-yellow flash on the ground "
     "12 squares wide; 2 a ring of dust and fire 36 wide and 10 tall, broken basalt chunks (2-4 squares, glowing orange "
     "edges) flying up at mirrored places; 3 the ring 52 wide, the chunks higher and further out, glowing cracks in the "
     "ground; 4 the ring 60 wide, the chunks falling; 5 the dust thinning, chunks on the ground; 6 faint dust. " + SOLID +
     ".",
     row(6, 64, 26) + "; the ground ring's middle 9 squares above the cell's bottom row."),
    ("e_hit", "冲撞打中，4 帧", "view_effects `league_ornn_e_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "冲撞撞上敌人：一闪白黄的冲击光，尘土和橙色火星炸开。**左右对称**，4 帧。",
     FI + " and " + DU,
     "A RAMMING IMPACT, 4 frames, " + LR + ": 1 a white-yellow flash 6 squares across; 2 a burst of dust and orange "
     "sparks 16 across; 3 the dust spreading, the sparks smaller; 4 fading dust.",
     row(4, 18, 18) + CENTER),
    # ---- R Call of the Forge God (the combo's two steps)
    ("r_call", "R 召唤（他脚下），6 帧", "view_effects `league_ornn_r_call`（他身上，不跟随，z -1；左右对称；大图表）", "56 × 18",
     "**R 第一段**：他砸锤召唤熔铸之神，脚下亮起一圈橙红的符文光环——环上是和他羊角上一样的方折回纹，向外扩散，地缝里冒出火舌"
     "（参考 livingforge_base_z_indicator_mult、recall_rgba）。从斜上方看的地面，**左右对称**，6 帧。",
     FI,
     "A SUMMONING RING at his feet, seen from slightly above, 6 frames, " + LR + ": 1 a small glowing ring 12 squares "
     "wide; 2 the ring 30 wide and 8 tall, orange-red, angular key-pattern runes glowing on it at mirrored places; 3 the "
     "ring 46 wide, the runes brightest, short flames licking up from it; 4 the ring 52 wide, the flames higher; 5 dimming; "
     "6 a faint ring.",
     row(6, 56, 18) + CENTER),
    ("r_rise", "R 公羊现身：远处的地上喷出火柱（不跟随），5 帧",
     "view_effects `league_ornn_r_rise`（放在远处公羊出发的点，不跟随，z 1；左右对称；大图表）", "34 × 40",
     "公羊在远处出现的地方：地面裂开，喷出一根高高的火柱，四周飞溅火星和碎石，公羊就从火里冲出来（公羊本身是下一张 r_ram；参考 "
     "`refs/lol_fx_ref.png` 里公羊跃出的样子 ornnram_spawn）。**左右对称**，5 帧。",
     FI + " and " + RO,
     "A FIRE ERUPTION from the ground, 5 frames, " + LR + ", its base on the cell's bottom row: 1 glowing cracks on the "
     "ground 20 squares wide; 2 a burst of fire 14 wide and 20 tall, rock chips flying out at mirrored places; 3 a tall "
     "column of fire 18 wide and 36 tall, a white-yellow core, red-orange edges, dark smoke at its top; 4 the column "
     "breaking into flames and embers; 5 embers and smoke fading.",
     row(5, 34, 40) + "; the eruption centered across, its base on the cell's bottom row."),
    ("r_ram", "R 熔岩公羊（弹道，循环），4 帧",
     "view_projectiles `league_ornn_r_ram`（弹道：游戏会转到奔跑方向；头朝右、上下对称；第二段头槌顶回去的 r_ram2 也用这张；大图表）",
     "40 × 28",
     "熔铸之神召唤的熔岩公羊，**从正上方往下看**（参考 `refs/lol_fx_ref.png` 里的 ornnram_top / ornnram_side）：头朝右，一对巨大的"
     "弯角向上下两边盘开（角尖深红、靠近头的地方暗铁色、刻着暗红的槽），头前一对发光的眼睛；身体是一块宽宽的深灰绿色岩石，背上刻着"
     "方折回纹的符文；后半身和四条短腿是发光的熔岩（橙黄），腿往上下两边撑开；身后拖着一条火焰尾巴。**头朝右、上下严格对称**（游戏会"
     "把它转到奔跑方向；从上往下看，往左跑也不会倒过来），4 帧循环（前后腿交替、火焰闪动，像在奔跑）。",
     RO + ", " + HO + " and " + FI,
     "A CHARGING LAVA RAM SEEN FROM DIRECTLY ABOVE, 4 frames, a loop, " + POINT + " and " + TB + ": the head at the "
     "right with two HUGE CURLED HORNS sweeping out to the top and to the bottom (crimson tips, dark iron near the head, "
     "dark red grooves), two glowing eyes at the head's front; the body a broad oval of dark grey-green rock 16 squares "
     "long with an angular key-pattern rune on its back; the hindquarters and the four short legs glowing molten "
     "orange-yellow, the legs splayed to the top and the bottom; a flame tail trailing left; each frame the legs swap "
     "(the front pair forward and the back pair back, then the other way) and the tail's flames flicker. " + SOLID +
     " (the horns and the rock body).",
     row(4, 40, 28) + "; the ram centred vertically, its horns' front touching the cell's right side."),
    ("r_butt", "R 头槌（他身前），4 帧", "view_effects `league_ornn_r_butt`（他身上，画在人物上面 z 3；左右对称；大图表）", "34 × 34",
     "**R 第二段**：公羊冲到身边，他用羊角把它顶回去的一瞬：一个白黄的大冲击闪光，一圈红橙的火焰冲击环，火星四溅。**左右对称**，4 帧。",
     FI,
     "A HEADBUTT IMPACT, 4 frames, " + LR + ": 1 a white-yellow flash 10 squares across; 2 a ring of fire 28 across, thick "
     "and orange-red, sparks bursting out at mirrored angles; 3 the ring 32 across and thinner, the embers further out; "
     "4 fading embers.",
     row(4, 34, 34) + CENTER),
    ("r_hit", "公羊撞中：火焰爆开，4 帧", "view_effects `league_ornn_r_hit`（跟随目标，z 2；左右对称）", "22 × 22",
     "公羊（来回两趟）撞中敌人：一团火焰爆开，夹着黑色碎石。**左右对称**，4 帧。",
     FI + " and " + RO,
     "A FIRE BURST, 4 frames, " + LR + ": 1 a white-yellow flash 6 squares across; 2 a burst of flames 18 across, "
     "orange-red, with dark rock chips at mirrored places; 3 the flames breaking into embers; 4 fading embers and smoke.",
     row(4, 22, 22) + CENTER),
]
BIG_FX = ["w_fire", "q_slam", "q_fissure", "q_rise", "q_pillar", "e_quake", "r_call", "r_rise", "r_ram", "r_butt"]
GROUPS = [
    ("a_hit e_hit q_hit", ["ornn_base_ba_clouds", "ornn_base_ba_trail_tex", "ornn_base_d_dirt", "ornn_base__z_rockdebris",
                           "ornn_base_z_splash_2x2", "ornn_base_r_sparks-orange"]),
    ("brittle br_pop", ["ornn_base_q_jhin_base_e_ash_01", "ornn_base_q_ivern_base_p_bufftransfer_4x4_sparkle_red",
                        "ornn_base_recall_ember", "livingforge_base_z_glow"]),
    ("w_fire w_hit w_shown", ["ornn_base_w_rumble_skin03_r_flamemesh", "ornn_base_w_rumble_skin03_r_flamemesh_mult",
                              "ornn_base_w_fuzzyshad", "livingforge_base_w_sparks-orange",
                              "livingforge_base_w_metal_texture", "distort-heat"]),
    ("q_slam q_fissure q_rise q_pillar", ["ornn_base_q_aatrox_r_explosion_firering", "ornn_base_q_dustcloud_erosion",
                                          "livingforge_base_q_bigglow02", "ornn_base_q_new_solar_tag",
                                          "ornn_base__z_rockdebris", "sru_dustcloud_mult"]),
    ("e_quake", ["ornn_base_e_sion_base_r_explo_clouds", "ornn_base_e_cas_spit", "sru_riftherald_smoke_dust",
                 "ornn_base_z_cloud_erosion", "ornn_base_z_clouds"]),
    ("r_call r_rise r_butt r_hit", ["ornn_base_r_sparks-orange", "ornn_base_recall_sword_hot", "ornn_base_recall_rgba",
                                    "livingforge_base_z_indicator_mult", "ornn_base_idle_horn_smokecloud"]),
    ("r_ram (League's ram)", ["ornnram_top", "ornnram_side", "ornnram_spawn"]),
]
SHOTS = [("attack", 3, "a_hit：大锤砸在前面的目标上（打中的目标身上）"),
         ("skill_w", 2, "w_fire：从他嘴里朝前喷（我会画进这一帧）；w_shown 罩住他；w_hit 在敌人身上"),
         ("skill", 3, "q_slam：熔岩拳砸地，他脚下；q_fissure 贴地朝前冲出；q_rise / q_pillar 立在裂隙尽头"),
         ("skill2", 1, "E 低头冲撞（冲刺中）；e_hit 在撞上的敌人身上"),
         ("skill2_hit", 1, "e_quake：撞碎柱子的地震，以他为中心"),
         ("ult", 3, "r_call：砸锤召唤，他脚下；r_rise 在远处；r_ram 公羊朝他冲回来"),
         ("ult_butt", 3, "r_butt：头槌把公羊顶回去，他身前；r_ram2 公羊被顶回去"),
         ("idle", 1, "待机（大小参考）；brittle 在敌人头上")]
# League's ram (OrnnRam in his WAD) rendered for the references: name -> (frames, yaw, pitch, size, fit, ground, width)
RAM = {"ornnram_top": (["ornnram_run@150"], 90, 85, 700, 0.6, 0.6, 1.4),
       "ornnram_side": (["ornnram_run@150"], 90, 12, 700, 0.6, 0.8, 1.8),
       "ornnram_spawn": (["ornnram_spawn@200", "ornnram_spawn@600", "ornnram_spawn@1000"], 90, 12, 500, 0.6, 0.85, 1.3)}


def configure():
    """pack_rammus_fx's sheets drawn from Ornn's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "奥恩"


def render_ram(lol):
    """League's ram into REF (rendered once; Riot's art, local only)."""
    for name, (frames, yaw, pitch, size, fit, ground, width) in RAM.items():
        if os.path.isfile(os.path.join(REF, name + ".png")):
            continue
        cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "OrnnRam",
               "--wad", "Ornn", "--hq", "--bg", "16,16,20", "--no-labels", "--size", str(size), "--fit", str(fit),
               "--ground", str(ground), "--width", str(width), "--yaw", str(yaw), "--pitch", str(pitch), "--name", name,
               "--out", REF] + [x for f in frames for x in ("--frame", f)]
        subprocess.run(cmd, check=True, capture_output=True)


def design_sheet(path):
    """His idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    d = np.asarray(Image.open(RF.lp(os.path.join(ROOT, "assets", "source", "ornn", "hd", "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (d.shape[1] * 4 + 32, d.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 山隐之焰 奥恩：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/ornn_idle.png`：3/4 正面朝右、驼背的羊角半神铁匠，灰蓝皮肤，"
      f"一对深铁灰带暗红符文的大羊角，深红鬃毛和大胡子，青铜羊角胸甲，近侧手里一把钢青大锤，远侧手臂从肘部往下是熔岩、握着小锤）。他在游戏里"
      f"是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/ornn_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/ornn_shots.png`：动作帧（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奥恩自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行；"
      "最后一行是英雄联盟里**大招的熔岩公羊**（从正上方、从侧面、跃出地面三个角度）。只在本地用，不要提交。颜色照英雄联盟原版："
      "**他的火是锻炉的火**（白黄的芯、橙黄的身、红橙的边、一点黑烟），**他的石头是黑色的玄武岩、裂缝里透着橙黄的熔岩光**，"
      "**公羊是带符文的黑色岩石身体、深红的大角、发光的熔岩腿和火焰尾巴**。")
    a("> - **特效要亮**：每团火和光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：两张弹道图（`q_fissure` 裂隙头、`r_ram` 公羊）**头朝右、上下严格对称**（游戏会把它们转到前进方向，往左跑时整张"
      "倒过来，所以要从正上方看、上下对称）；`w_fire` 喷火**头朝右**（我会把它画进他自己的动作帧里）；其余**全部严格左右对称**"
      "（逐格对称：这些画面在红色方不会镜像）。")
    a("> - **连招**：`q_rise` / `q_pillar` 是 Q 立起来的熔岩柱，`e_quake` 是 E 撞碎柱子的地震（Q→E）；`r_call` → `r_rise` → `r_ram` 是"
      "R 第一段召唤公羊冲回来，`r_butt` 是第二段头槌把公羊顶回去（R1→R2）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ornn_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/ornn_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「活体锻炉」的易碎和 W「风箱炎息」在里面） | 大锤砸击；打中易碎的英雄引爆；每 12 秒喷火（不可阻挡、护盾） | "
      "`a_hit` · `br_pop` · `brittle` · `w_fire` · `w_hit` · `w_shown` |")
    a("| 技能 1 = Q「火山突堑」 | 熔岩拳砸地，裂隙贴地冲出，尽头升起熔岩柱 | `q_slam` · `q_fissure` · `q_hit` · `q_rise` · `q_pillar` |")
    a("| 技能 2 = E「炽烈冲锋」 | 低头冲撞；撞碎柱子时地震击飞（Q→E 连招） | `e_quake` · `e_hit` |")
    a("| 大招「熔铸之神的召唤」 | 召唤熔岩公羊从远处冲回来，到身边时头槌顶回去击飞（R1→R2 连招） | `r_call` · `r_rise` · `r_ram` · "
      "`r_butt` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**；"
      "**只有实心的石头**（熔岩柱、碎石块、公羊的岩石身体和角、易碎的碎壳）有一圈近黑的描边。")
    a("- **要亮**：每个火和光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("锻炉的火（火焰、熔岩、发光的裂纹、火星）", FIRE), ("黑色玄武岩（柱子、碎石、公羊的身体）", ROCK),
                        ("尘土", DUST), ("公羊的深红大角", HORN)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（尘土环、符文环、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、他身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 25000，Q 的裂隙最长 "
      "80000，E 地震的半径 30000，公羊的宽 24000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `ornn_fx_{name}.png`：{title}\n")
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
        a(f"| `ornn_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_ornn_fx`（小的）和 `league_ornn_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_ornn.py 的 views；`r_ram2` 用 `r_ram` 的帧；`brittle`、`w_shown` 绑在同名 buff 上）。")
    a("- `w_fire` 不进特效表：用 tools/fix/bake_caster_fx.py 的做法画进他的 skill_w 帧（嘴的位置），数据里的 CasterViewEffect 去掉；"
      "其余除了两张弹道图全部断言左右对称，两张弹道图断言上下对称。")
    a("- `q_rise`、`q_pillar`、`r_rise` 底边对在落点的地面上；`q_slam`、`e_quake`、`r_call` 画在人物下面（z -1），`r_butt`、`brittle`、"
      "`w_shown` 在上面（z 3）；`q_pillar` 每 15 tick 盖一次，两帧的循环要接得上 `q_rise` 的最后一帧。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉给火、光描的最深色边（石头的描边保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。用户也可能用 Gemini 画好直接给图片（沃里克、格雷福斯的做法：process_*_fx.py）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="ornn_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=TMP, help="folder for the zip")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_ornn.py first")
    render_ram(a.lol)
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "ornn_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "ornn_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "ornn_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    for name in RAM:
        shutil.copyfile(os.path.join(REF, name + ".png"), os.path.join(out, "refs", name + ".png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"ornn_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": ("top-bottom (a projectile, turned by the game, pointing right)" if x[0] in ("q_fissure", "r_ram")
                                 else "none (pointing right: baked into his own frames)" if x[0] == "w_fire" else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
