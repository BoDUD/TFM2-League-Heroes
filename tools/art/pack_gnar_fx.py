#!/usr/bin/env python3
"""Build gnar_fx_pack.zip: step 3 of Gnar's sprite - Codex draws his effects (pack_zyra_fx.py's way, pack_rammus_fx's
sheets).

    python tools/lol/fx_ref_gnar.py            # League's particle textures -> C:/t/gn_work/fxref (local only)
    python tools/art/pack_gnar_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name gnar_fx_redo_pack]

The pack (C:/t/gn_work/fx/gnar_fx_pack, zipped into --out, default dist/gnar_packs) holds PROMPTS.md (also written to
assets/source/gnar/PROMPTS_FX.md), design/gnar_idle.png (both forms' idles at 4x, the designs' squares at PPU 1.5),
design/gnar_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/gnar_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_gnar.py): view_projectiles a_boom, q_boom (also q_back: the
boomerang coming home), q_rock; view_effects a_hit, a_hyper, m_hit, q_hit, q_catch, q2_hit, q_rest, q_pick, e_hit,
c_slam, c_hit, w_quake, w_hit, r_wave, r_hit, tf_mega, tf_mini; view_buffs full, hyper, q_slow, q2_slow. League's colours:
Mini's boomerang ivory bone with white-blue swooshes; his rage red-orange with white flashes; Mega's blows brown dust,
rock debris and white impact flashes; the transform a red-orange blast of fur and steam. Red side: the client never
mirrors an effect picture, so every hit, buff and ground picture is symmetric left to right; a projectile's picture is
turned with its flight (drawn flying right), so it is symmetric top to bottom.
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

TMP = "C:/t/gn_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "gnar", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_gnar")
NAME = "gnar_fx_pack"

RAGE = "#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412"      # his rage: red-orange flare, the transform
BONE = "#FFFDF2, #F4E8C4, #DCC48E, #B4935E, #7E6238, #4A3820"      # the boomerang's ivory bone and brown leather
SWOOSH = "#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8"              # the boomerang's white-blue swooshes and glints
DUST = "#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A"       # dirt, dust clouds
ROCK = "#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422"       # the boulder, rock chips (solid: outlined)
CREST = "#F2FDFF, #A6F0FF, #4CC8FF, #1E86E8, #0E46A8"               # Mega's electric-blue crest energy
RA = f"a red-orange rage ramp ({RAGE})"
BO = f"an ivory bone ramp ({BONE})"
SW = f"a white-blue swoosh ramp ({SWOOSH})"
DU = f"a brown dust ramp ({DUST})"
RO = f"a grey rock ramp ({ROCK})"
CR = f"an electric-blue crest ramp ({CREST})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - "
                       "the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character")
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
MINI = "Mini Gnar stands in the middle, not drawn: 32 squares tall (his huge ears and skull cap included), 30 wide"
MEGA = "Mega Gnar stands in the middle, not drawn: 44 squares tall, about 62 wide (a hunched beast on his knuckles)"
UNIT = "a champion stands in the middle, not drawn: about 16 squares wide and 36 tall"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- Mini: the auto attack, Hyper
    ("a_boom", "迷你普攻：小回力标（弹道，循环），4 帧", "view_projectiles `league_gnar_a_boom`（跟着弹道转向；上下对称）", "10 × 10",
     "迷你纳尔普攻扔出去的小回力标在空中旋转：象牙色的弯骨头，中间缠着棕色皮条，转起来带一圈白蓝色的弧线残影（参考 q_weapon、"
     "q_weapon_blur）。**朝右飞，残影在左边，上下严格对称**：4 帧循环里骨头分别是横着、竖着、两个斜着的叠影、一圈转动的弧光。",
     f"{BO} and {SW}",
     "A SMALL SPINNING BOOMERANG, 4 frames, a seamless loop, " + TB + ": 1 the ivory bone boomerang lying flat across the "
     "cell (8 squares long, 2 thick, brown leather wrapped round its middle, 1-square near-black outline); 2 the bone "
     "standing upright through the middle (the same bone turned a quarter); 3 the bone's two diagonals crossing (an X, "
     "the spin's blur); 4 a white-blue ring of motion arcs 8 across with the bone's ends as two ivory dots at left and "
     "right; each frame a short white-blue swoosh trail at the left.",
     row(4, 10, 10) + "; the boomerang's middle on the cell's middle."),
    ("a_hit", "迷你普攻：打中目标，3 帧", "view_effects `league_gnar_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "回力标打中目标：一下白色和象牙色的小闪光，几道短短的白蓝色弧线往外弹（参考 ba_hit、ba_hit_spike）。**左右对称**。",
     f"{SW} and {BO}",
     "A SMALL BOOMERANG HIT, 3 frames, " + LR + ": 1 a white four-pointed flash 6 squares across; 2 the flash 9 across with "
     "4 short white-blue arcs flying out at mirrored diagonals and 2 ivory chips; 3 only the arcs further out, fading.",
     row(3, 12, 12) + CENTER),
    ("a_hyper", "亢奋：第 3 下的强化命中，4 帧", "view_effects `league_gnar_a_hyper`（跟随目标，z 2；左右对称）", "18 × 18",
     "亢奋（W 被动）第 3 下打中：一圈橙红色的爆发，中间白色的芯，几颗黄色的小星星往外蹦，带一圈冲击波（参考 enrage_buf_star、"
     "ba_tar_centerflare、ba_crack_radial）。**左右对称**。",
     f"{RA}",
     "A HYPER BURST, 4 frames, " + LR + ": 1 a white-hot core 4 across inside an orange flare 8 across; 2 a red-orange "
     "starburst 14 across with 6 small yellow-orange stars flung out at mirrored places; 3 an orange shock ring 16 across "
     "(1-2 squares thick), the stars further out; 4 the ring breaking into embers, two stars left, fading.",
     row(4, 18, 18) + CENTER),
    ("hyper", "亢奋：加速的时候（身上，循环），4 帧", "view_buffs `league_gnar_hyper`（跟随，画在人物下面 z -1；左右对称；循环）", "24 × 8",
     "亢奋加速时：迷你纳尔脚下两边几道橙黄色的速度线和小尘土，一闪一闪（参考 p_speed_trail、p_dust）。**只画在脚下的地面上**，"
     "**左右对称**，4 帧循环。",
     f"{RA} and {DU}",
     "HYPER SPEED LINES at a unit's feet, 4 frames, a seamless loop, " + LR + " (" + MINI + ", only the bottom 8 squares "
     "used, his feet's area in the middle left EMPTY): on each side 3 short orange-yellow speed streaks (3-6 squares) "
     "along the ground and 2 small dust puffs; each frame the streaks slide outward and fade, new ones start near the feet.",
     row(4, 24, 8) + "; centered across, the streaks' bottom on the cell's bottom row."),
    ("full", "狂怒基因：怒气满了（身上，循环），4 帧", "view_buffs `league_gnar_full`（跟随，画在人物上面 z 3；左右对称；循环）", "34 × 36",
     "怒气满、马上要变身的时候：迷你纳尔身上冒出一圈红橙色的怒火光焰和热气，几颗火星往上飘（参考 p_fur_red、p_radial、"
     "p_transform_hotpoint、z_glow_maroon）。**围着人画，身体位置留空**（只画外圈和头顶），**左右对称**，4 帧循环。",
     f"{RA}",
     "A RAGE AURA round a unit, 4 frames, a seamless loop, " + LR + " (" + MINI + ", his body area left EMPTY): flickering "
     "red-orange flame tongues rising round his outline (3-6 squares tall, brighter at the top), white-hot sparks and "
     "small steam puffs rising above his head; each frame the tongues sway and the sparks climb 2 squares.",
     row(4, 34, 36) + "; centered across, the flames' bottom on the cell's bottom row."),
    # ---- Mini: Q Boomerang Throw
    ("q_boom", "迷你 Q：大回力标（弹道，循环），4 帧", "view_projectiles `league_gnar_q_boom` 和 `q_back`（飞出去和飞回来都用；跟着弹道转向；上下对称）",
     "16 × 16",
     "Q 扔出去的大回力标：和普攻一样的象牙色骨头回力标，大一倍，转起来一圈白蓝色的弧光更明显，后面一道白蓝色的风尾（参考 q_weapon、"
     "q_weapon_blur、q_rip_ani）。**朝右飞，风尾在左边，上下严格对称**，4 帧循环（横、竖、斜叉、弧光圈）。",
     f"{BO} and {SW}",
     "A BIG SPINNING BOOMERANG, 4 frames, a seamless loop, " + TB + ": 1 the ivory bone boomerang flat across the cell "
     "(13 squares long, 3 thick, brown leather wrapped round its middle, 1-square near-black outline, a white glint); 2 "
     "the bone upright through the middle; 3 the bone's two diagonals crossing (the spin's blur); 4 a bright white-blue "
     "ring of motion arcs 13 across with the bone's ends as two ivory chunks at left and right; each frame a white-blue "
     "wind streak 5 squares long at the left.",
     row(4, 16, 16) + "; the boomerang's middle on the cell's middle."),
    ("q_hit", "迷你 Q：回力标打中，3 帧", "view_effects `league_gnar_q_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "大回力标打中敌人：一下白色闪光，一道交叉的白蓝色斩痕，几块碎屑（参考 q_hit、q_hit_dot）。**左右对称**。",
     f"{SW} and {BO}",
     "A BOOMERANG STRIKE, 3 frames, " + LR + ": 1 a white flash 7 across; 2 two crossing white-blue slash arcs (an X 13 wide) "
     "over the flash, 4 ivory chips flying out at mirrored diagonals; 3 only the chips and two fading arc ends.",
     row(3, 16, 16) + CENTER),
    ("q_catch", "迷你 Q：接住回力标，3 帧", "view_effects `league_gnar_q_catch`（跟随纳尔，z 3；左右对称）", "16 × 16",
     "回力标飞回来、纳尔接住：一圈白蓝色的小闪光和一圈转动的弧线，像收回来时最后一转（参考 q_weapon_catch1）。**左右对称**。",
     f"{SW}",
     "A CATCH FLASH, 3 frames, " + LR + ": 1 a white-blue ring of motion arcs 12 across closing in; 2 a bright white star "
     "flash 8 across at the middle with 4 tiny sparkles at mirrored places; 3 two small fading sparkles.",
     row(3, 16, 16) + CENTER),
    ("q_slow", "迷你 Q：被回力标减速（身上，循环），4 帧", "view_buffs `league_gnar_q_slow`（跟随，z 3；左右对称；循环）", "16 × 8",
     "被回力标减速：敌人头顶上一圈慢慢转的白蓝色小弧线（像被风卷住）。**只画在头顶上方**，**左右对称**，4 帧循环。",
     f"{SW}",
     "A SLOW SWIRL above a unit's head, 4 frames, a seamless loop, " + LR + ": a flat white-blue ring of 4 short arcs "
     "(an ellipse 14 wide and 4 tall); each frame the arcs move a quarter round (mirrored left and right).",
     row(4, 16, 8) + "; centered across, the ring in the cell's middle."),
    # ---- Mini: E Hop
    ("e_hit", "迷你 E：踩着敌人弹起来，3 帧", "view_effects `league_gnar_e_hit`（跟随目标，z 2；左右对称）", "16 × 14",
     "迷你纳尔从敌人头上弹起来：一下白蓝色的星形闪光（英雄联盟里是蓝色的星），几颗小星星和一小团尘土（参考 e_hitstar、e_dustcloud）。"
     "**左右对称**。",
     f"{SW} and {DU}",
     "A HOP BOUNCE, 3 frames, " + LR + ": 1 a white-blue four-pointed star flash 6 across; 2 the star 10 across, 4 small "
     "white-blue stars popping out at mirrored places, a small dust puff under it; 3 only the small stars and the puff, "
     "fading.",
     row(3, 16, 14) + CENTER),
    # ---- Mega: the punch
    ("m_hit", "巨型普攻：拳头砸中，4 帧", "view_effects `league_gnar_m_hit`（跟随目标，z 2；左右对称）", "20 × 18",
     "巨型纳尔一拳砸中：一大团白色冲击闪光，四周的褐色尘土和几块碎石飞出去（参考 gnarbig ba_rocks、ba_dot_tar、w_flashwhite）。"
     "**左右对称**。",
     f"{DU}, {RO} and {RA}",
     "A HEAVY PUNCH IMPACT, 4 frames, " + LR + ": 1 a white impact flash 8 across with an orange rim; 2 a white-orange "
     "starburst 14 across, 4 grey rock chips (outlined) flying out at mirrored diagonals; 3 a brown dust cloud ring 18 "
     "across, the chips further out; 4 only drifting dust, fading.",
     row(4, 20, 18) + CENTER),
    # ---- Mega: Q Boulder Toss
    ("q_rock", "巨型 Q：大石头（弹道，循环），4 帧", "view_projectiles `league_gnar_q_rock`（跟着弹道转向；上下对称）", "18 × 16",
     "巨型纳尔扔出去的大石头：一块圆圆的灰色巨石，上面有裂纹和一点青苔，转着飞，后面拖一道褐色的尘土尾巴（参考 q_rock、q_swoosh、"
     "q_dirtbits）。**朝右飞，尘土尾在左边，上下严格对称**，4 帧循环（石头的裂纹转一圈）。实心的石头有 1 格近黑描边。",
     f"{RO} and {DU}",
     "A FLYING BOULDER, 4 frames, a seamless loop, " + TB + ": a round grey boulder 12 squares across at the right (cracks "
     "and chips drawn so the boulder looks the same turned upside down, 1-square near-black outline, a light top-left "
     "edge mirrored by a light bottom-left edge), each frame its cracks turned a step (rolling); a brown dust trail 6 "
     "squares long at its left with 2 small pebbles above and below (mirrored).",
     row(4, 18, 16) + "; the boulder's middle on the cell's middle row, 6 squares from its right edge."),
    ("q2_hit", "巨型 Q：石头砸中，5 帧", "view_effects `league_gnar_q2_hit`（不跟随，z 2；左右对称）", "34 × 24",
     "石头砸中第一个敌人、周围都受伤：一大团白色冲击闪光，一圈褐色的尘土冲击波往外推，碎石飞溅（参考 q_hit_shock、q_rock_crater、"
     "q_dust_shadow）。**左右对称**，范围约 32 格宽。",
     f"{DU}, {RO} and {RA}",
     "A BOULDER SMASH, 5 frames, " + LR + ": 1 a white flash 10 across; 2 a white-orange burst 18 across, 6 grey rock chips "
     "(outlined) flying out at mirrored places; 3 a brown dust shock ring 30 across and 10 tall (an ellipse seen from "
     "above), the chips at its rim; 4 the ring 32 across breaking into dust clouds; 5 only drifting dust, fading.",
     row(5, 34, 24) + "; centered across, the ring's middle 8 squares above the cell's bottom row."),
    ("q_rest", "巨型 Q：落在地上的石头（3 秒，循环），4 帧", "view_effects `league_gnar_q_rest`（不跟随，画在人物下面 z -1；左右对称）",
     "16 × 12",
     "石头停下来以后落在地上等纳尔来捡：一块灰色巨石半埋在一小圈裂开的地面里，周围一点尘土慢慢落下，石头上偶尔闪一下（参考 q_rock、"
     "q_rock_crater、q_rockhud）。**左右对称**，4 帧循环（尘土落下、闪光）。实心的石头有 1 格近黑描边。",
     f"{RO} and {DU}",
     "A BOULDER RESTING ON THE GROUND, 4 frames, a seamless loop, " + LR + ": a round grey boulder 11 squares across sitting "
     "in a small cracked dent in the ground (a flat ellipse 15 wide and 4 tall), 1-square near-black outline round the "
     "boulder; 1-2 a few dust specks settling round it; 3 a white glint on its top; 4 still.",
     row(4, 16, 12) + "; centered across, the dent's bottom on the cell's bottom row."),
    ("q_pick", "巨型 Q：捡回石头，3 帧", "view_effects `league_gnar_q_pick`（跟随纳尔，z 3；左右对称）", "20 × 16",
     "纳尔把石头捡回来：一团褐色的尘土扬起来，中间一下白色闪光（参考 q_dirtbits、p_dust）。**左右对称**。",
     f"{DU}",
     "A PICK-UP PUFF, 3 frames, " + LR + ": 1 a white flash 6 across low in the cell; 2 a brown dust puff 16 across rising "
     "around it, 4 pebbles at mirrored places; 3 the dust thinning and drifting up, fading.",
     row(3, 20, 16) + "; centered across, the puff's bottom on the cell's bottom row."),
    ("q2_slow", "巨型 Q：被石头减速（身上，循环），4 帧", "view_buffs `league_gnar_q2_slow`（跟随，画在人物下面 z -1；左右对称；循环）",
     "18 × 6",
     "被石头砸中减速：敌人脚下一小圈翻起的碎土和小石子（参考 q_dirtbits）。**只画在脚下的地面上**，**左右对称**，4 帧循环。",
     f"{DU} and {RO}",
     "STIRRED EARTH at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat brown dirt ellipse 16 wide and 3 tall "
     "with 4 pebbles bobbing at mirrored places; each frame the pebbles hop a square and dust drifts.",
     row(4, 18, 6) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- Mega: E Crunch
    ("c_slam", "巨型 E：猛踏落地（地面冲击，大图），5 帧", "view_effects `league_gnar_c_slam`（不跟随，画在人物下面 z -1；左右对称）",
     "48 × 26",
     "巨型纳尔跳起来砸在地上：地面炸开一圈白色冲击波，一圈褐色尘土环往外推，地上裂开几道缝，碎石飞起来（参考 e_big_aoe_dustring、"
     "e_big_aoe_pebbles、e_land_hit、e_crackflash）。**左右对称**，范围约 44 格宽（从斜上方看的椭圆）。",
     f"{DU}, {RO} and {RA}",
     "CRUNCH LANDING, 5 frames, " + LR + ": 1 a white flash on the ground 16 across with 4 short cracks radiating from it; "
     "2 a white-orange shock ring 30 across and 9 tall (an ellipse seen from above), 6 grey rock chips (outlined) flying "
     "up at mirrored places; 3 a brown dust ring 44 across and 14 tall rolling outward, the cracks glowing orange; 4 the "
     "dust ring breaking into clouds, the chips falling; 5 only fading dust and the cracks.",
     row(5, 48, 26) + "; centered across, the ellipse's middle 9 squares above the cell's bottom row."),
    ("c_hit", "巨型 E：猛踏打中，3 帧", "view_effects `league_gnar_c_hit`（跟随目标，z 2；左右对称）", "16 × 14",
     "猛踏打中敌人：一下橙白色的闪光，一小团尘土（参考 gnarbig e_hitbubble、e_land_hit_spike）。**左右对称**。",
     f"{RA} and {DU}",
     "A CRUNCH HIT, 3 frames, " + LR + ": 1 an orange-white flash 7 across; 2 the flash 11 across with a small dust puff "
     "under it and 2 chips at mirrored places; 3 only the dust, fading.",
     row(3, 16, 14) + CENTER),
    # ---- Mega: W Wallop
    ("w_quake", "巨型 W：痛殴砸地（围着他，大图），5 帧", "view_effects `league_gnar_w_quake`（跟随纳尔，画在人物下面 z -1；左右对称）",
     "60 × 26",
     "巨型纳尔双拳砸地：以他为中心地面裂开放射状的大裂缝，裂缝里闪白光，一圈褐色尘土冲起来，碎石飞溅（参考 gnarbig w_cracks_radial、"
     "w_pow_area、w_dust、gnar w_groundcrack、w_impactpuffs）。**左右对称**，范围约 56 格宽（从斜上方看的椭圆），中间他站的地方留空。",
     f"{DU}, {RO} and {RA}",
     "WALLOP SMASH round a unit, 5 frames, " + LR + " (" + MEGA + ", only the ground drawn): 1 white flashes where his fists "
     "hit at both sides of the middle, 6 cracks radiating across the ground (an ellipse 40 wide and 12 tall); 2 the "
     "cracks 56 wide glowing white-orange, a brown dust wall bursting up 8 squares at the cracks' ends, 6 rock chips "
     "(outlined) flying at mirrored places; 3 the dust 12 tall rolling outward; 4 the dust settling, the cracks dimming; "
     "5 only faint cracks and drifting dust.",
     row(5, 60, 26) + "; centered across, the ellipse's middle 8 squares above the cell's bottom row."),
    ("w_hit", "巨型 W：痛殴打中、眩晕，5 帧", "view_effects `league_gnar_w_hit`（跟随目标，z 3；左右对称）", "20 × 30",
     "痛殴打中敌人：身上一下白色冲击闪光，然后头顶一圈转圈的黄色小星星（被打晕了）（参考 w_flashwhite、enrage_buf_star）。"
     "**人站在中间不画**，**左右对称**，5 帧。",
     f"{RA} and {DU}",
     "A STUNNING BLOW, 5 frames, " + LR + " (" + UNIT + ", its body area left EMPTY): 1 a white impact flash 10 across at "
     "the cell's middle height; 2 the flash 14 across with dust at its sides; 3 a ring of 5 small yellow stars appearing "
     "above the head (an ellipse 12 wide and 4 tall at the cell's top); 4 the stars a quarter round; 5 the stars another "
     "quarter round, dimmer.",
     row(5, 20, 30) + "; centered across, the stars' ring 3 squares from the cell's top."),
    # ---- Mega: R GNAR!
    ("r_wave", "巨型 R：呐啊！冲击波（围着他，大图），6 帧", "view_effects `league_gnar_r_wave`（不跟随，画在人物下面 z -1；左右对称）",
     "70 × 40",
     "大招：巨型纳尔一吼把周围的敌人全掀飞：以他为中心一圈巨大的白色冲击波环往外推，地面碎石和尘土被卷起来，几道红橙色的爪痕状气浪往四周扫"
     "（参考 gnarbig r_aoe、r_distort、r_debris1、r_scratch、gnar r_rocks、r_trail）。**左右对称**，范围约 64 格宽（从斜上方看的椭圆）。",
     f"{RA}, {DU} and {RO}",
     "A GNAR! SHOCKWAVE round a unit, 6 frames, " + LR + " (" + MEGA + ", only the ground and the air round him drawn, his "
     "body area left EMPTY): 1 a white shock ring 24 across and 8 tall on the ground round him; 2 the ring 46 across, "
     "4 red-orange claw-swipe gusts (curved streaks 10 long) sweeping outward at mirrored diagonals, rock chips (outlined) "
     "and dust lifting; 3 the ring 64 across and 20 tall, the gusts at its rim, debris flying outward; 4 the ring breaking "
     "into dust clouds; 5 the dust and debris settling; 6 faint dust only.",
     row(6, 70, 40) + "; centered across, the ellipse's middle 12 squares above the cell's bottom row."),
    ("r_hit", "巨型 R：被掀飞的敌人，4 帧", "view_effects `league_gnar_r_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "被呐啊掀飞的敌人：一下红橙白色的闪光，几道往外甩的气浪和碎石（参考 gnarbig r_land_hit、r_scratch）。**左右对称**。",
     f"{RA}, {DU} and {RO}",
     "A THROWN IMPACT, 4 frames, " + LR + ": 1 a red-orange-white flash 8 across; 2 a burst 14 across with 4 curved gust "
     "streaks flung out at mirrored diagonals; 3 2 rock chips (outlined) and dust at mirrored places, the streaks fading; "
     "4 only fading dust.",
     row(4, 18, 18) + CENTER),
    # ---- the transform
    ("tf_mega", "变身：迷你变巨型（大图），6 帧", "view_effects `league_gnar_tf_mega`（跟随纳尔，画在人物上面 z 3；左右对称）", "72 × 56",
     "迷你纳尔怒气满变成巨型纳尔：先一团白热的光把他包住，然后炸开一大团红橙色的怒火、热气和飞起的红毛，最后烟散开露出巨型纳尔（参考 "
     "p_transform_white、p_transform_hotpoint、p_transform_zap_ani、p_fur_red、p_pop_rgba、p_radial）。**围着人画、中间留空不要盖住他**"
     "（第 1–3 帧可以盖住中间：那时他正在变），**左右对称**，6 帧。",
     f"{RA}",
     "A RAGE TRANSFORMATION, 6 frames, " + LR + " (the small cub grows into the beast in the middle, not drawn: 32 tall "
     "at the start, 44 tall and 62 wide at the end): 1 a white-hot glow ball 20 across low in the middle; 2 the glow 32 "
     "across with red-orange zaps crackling round it; 3 a huge red-orange blast 60 across and 48 tall covering the "
     "middle, tufts of red fur flying out; 4 the blast opening into a ring of flame and steam round the edge (the middle "
     "clear), fur tufts further out; 5 the ring thinning into smoke puffs and sparks; 6 only a few drifting smoke puffs "
     "and sparks.",
     row(6, 72, 56) + "; centered across, the blast's bottom on the cell's bottom row."),
    ("tf_mini", "变回：巨型变迷你（大图），5 帧", "view_effects `league_gnar_tf_mini`（跟随纳尔，z 3；左右对称）", "60 × 46",
     "巨型纳尔变回迷你：一团白色的烟“噗”地炸开把他包住，烟散开时飘出几撮红毛（参考 p_pop_dust_rgba、p_transform_shrink_rgba、p_trans）。"
     "**左右对称**，5 帧（第 1–2 帧盖住中间）。",
     f"{DU} and {RA}",
     "A POOF BACK TO SMALL, 5 frames, " + LR + " (the beast shrinks back into the cub in the middle, not drawn): 1 a white "
     "smoke cloud 40 across and 36 tall puffing out over the middle; 2 the cloud 56 across, round billowy puffs; 3 the "
     "cloud opening (the middle clear), 4 small red fur tufts drifting; 4 the puffs thinning at the edge; 5 a few faint "
     "puffs only.",
     row(5, 60, 46) + "; centered across, the cloud's bottom on the cell's bottom row."),
]
BIG_FX = ["c_slam", "w_quake", "r_wave", "tf_mega", "tf_mini"]
FLYING = ["a_boom", "q_boom", "q_rock"]
GROUPS = [
    ("a_boom q_boom q_catch", ["gnar_base_q_weapon", "gnar_base_q_weapon_blur", "gnar_base_q_weapon_catch1",
                               "gnar_base_p_chalkline_pop", "gnar_base_q_cone_ani"]),
    ("a_hit q_hit a_hyper hyper", ["gnar_base_ba_hit", "gnar_base_ba_hit_spike", "gnar_base_q_hit",
                                   "gnar_base_ba_tar_centerflare", "gnar_base_ba_tar_groundflame", "gnar_base_p_flash"]),
    ("q_rock q2_hit q_rest q_pick", ["gnarbig_base_q_dirtbits", "gnar_dirtbits", "gnarbig_base_q_rock_crater",
                                     "gnarbig_base_q_rockhud", "gnarbig_base_q_dust_shadow", "gnar_base_w_pop_dust"]),
    ("e_hit c_slam c_hit", ["gnar_base_e_hitstar", "gnar_base_e_dustcloud", "gnar_base_e_big_aoe_dustring",
                            "gnar_base_e_big_aoe_pebbles", "gnarbig_base_e_land_hit", "gnarbig_base_e_hitbubble"]),
    ("m_hit w_quake w_hit", ["gnar_base_w_groundcrack", "gnar_base_w_impactpuffs", "gnar_base_w_pebbles",
                             "gnarbig_base_w_pow_area", "gnarbig_base_ba_rocks", "gnarbig_base_ba_dot_tar"]),
    ("r_wave r_hit", ["gnarbig_base_r_aoe", "gnarbig_base_r_land_hit", "gnar_base_r_trail", "gnarbig_base_r_scratch",
                      "gnarbig_base_r_debris1"]),
    ("tf_mega tf_mini full", ["gnar_base_p_transform_zap_ani", "gnar_base_p_transform_hotpoint", "gnar_base_p_flares",
                              "gnar_base_p_radial_1", "gnar_base_p_dust", "gnar_base_p_fur2"]),
]
SHOTS = [("attack", 3, "a_boom：小回力标从身前的手里飞出去"),
         ("skill", 4, "q_boom：扔出去的大回力标从手里飞出去，飞回来时 q_catch"),
         ("skill2", 3, "e_hit：跳到敌人头上时在敌人身上"), ("transform", 4, "tf_mega：变身（之后是巨型）"),
         ("m_attack", 4, "m_hit：巨型下扑一拳砸在前面的目标上"), ("m_skill", 4, "q_rock：巨型扔出去的大石头"),
         ("m_skill2", 6, "c_slam：跳起来落地的地方（以他为中心）"), ("m_wallop", 4, "w_quake：拳头砸地，以他为中心"),
         ("ult", 3, "r_wave：直立起来把周围全掀飞，以他为中心"), ("idle", 1, "迷你待机（大小参考）"),
         ("m_idle", 1, "巨型待机（大小参考）")]


def configure():
    """pack_rammus_fx's sheets drawn from Gnar's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "迷你纳尔"


def design_sheet(path):
    """Both forms' designs at 4x (PPU 1.5)."""
    ims = [np.asarray(Image.open(RF.lp(os.path.join(ROOT, "assets", "source", "gnar", "hd", n))).convert("RGBA"))
           for n in ("idle.png", "m_idle.png", "m_side.png")]
    W = sum(t.shape[1] * 4 + 32 for t in ims)
    H = max(t.shape[0] for t in ims) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    x = 16
    for t in ims:
        bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (x, H - 16 - t.shape[0] * 4))
        x += t.shape[1] * 4 + 32
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 迷失之牙 纳尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/gnar_idle.png`：左边迷你纳尔——橙色毛茸茸的小约德尔、大耳朵、"
      f"骨头头盔、手里一把骨头回力标；右边巨型纳尔——弓着背的深红色巨兽、电光蓝毛刺、两根大獠牙、巨大的拳头）。他在游戏里是**高清**的"
      f"（每个游戏格子里 1.5×1.5 个细像素），迷你 {h} 格高、{w} 格宽，巨型 44 格高、约 62 格宽；**特效照常按游戏格子画**（1 格 = 1 个"
      f"游戏像素），不用画成高清。")
    a("> - 大小对照 `design/gnar_size.png`：迷你纳尔的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小"
      "都是游戏像素（格）。")
    a("> - `design/gnar_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里纳尔自己的特效贴图（迷你和巨型两套），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**迷你的回力标是象牙色骨头，带白蓝色的风弧**；**怒气和变身是红橙色的火光、白热的闪光**；**巨型的拳头、石头、"
      "砸地是褐色尘土、灰色碎石和白色冲击闪光**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **实心的东西（回力标、石头、碎石）有 1 格近黑描边**，像人物一样；**光、风弧、尘土、烟、冲击波没有描边**。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（变身的前几帧除外，写在那一条里）。")
    a("> - **对称**：打中、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（两种回力标、石头）"
      "**朝右飞、后面在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的；回力标转圈的几帧用横、竖、斜叉、弧光圈，"
      "每帧都上下对称）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gnar_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/gnar_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 迷你扔小回力标（每第 3 下亢奋）；巨型一拳砸下 | `a_boom` · `a_hit` · `a_hyper` · `hyper` · `m_hit` |")
    a("| 被动「狂怒基因」 | 怒气满了身上冒怒火，变成巨型 / 变回迷你 | `full` · `tf_mega` · `tf_mini` |")
    a("| 技能 1 = Q | 迷你：回力标飞出去再飞回来、接住；巨型：扔大石头，石头停在地上可以捡回来 | `q_boom` · `q_hit` · `q_catch` · `q_slow` · "
      "`q_rock` · `q2_hit` · `q_rest` · `q_pick` · `q2_slow` |")
    a("| 技能 2 = E / W | 迷你：轻跳踩敌人的头弹起来；巨型：猛踏跳起来砸地，接痛殴双拳砸地晕眩前面的敌人 | `e_hit` · `c_slam` · `c_hit` · "
      "`w_quake` · `w_hit` |")
    a("| 大招「呐啊！」 | 巨型一吼把周围的敌人全掀飞 | `r_wave` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、风弧、尘土、烟、冲击波没有黑描边**；**回力标、石头、碎石有 1 格近黑描边**。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("怒气、变身的红橙火光", RAGE), ("回力标的象牙色骨头和棕色皮条", BONE), ("回力标的白蓝风弧", SWOOSH),
                        ("褐色尘土", DUST), ("灰色石头、碎石", ROCK), ("巨型的电光蓝", CREST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（冲击波、尘土环、裂缝）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：迷你普攻射程 42000，巨型的石头"
      "砸中半径 16000，猛踏半径 18000，大招半径 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `gnar_fx_{name}.png`：{title}\n")
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
        a(f"| `gnar_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_gnar_fx`（小的）和 `league_gnar_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_gnar.py 的 views；q_back 用 q_boom 的帧）。")
    a(f"- 弹道图（{'、'.join(FLYING)}）断言上下对称，其余断言左右对称；q2_hit、q_rest、c_slam、r_wave 不跟随（落点）；w_quake 是新加的"
      "CasterViewEffect（痛殴砸地那一 tick）。")
    a("- q_rest 循环到 pick_t（3 秒）；full、hyper、q_slow、q2_slow 是 buff 循环。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（回力标、石头、碎石的描边保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="gnar_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "gnar_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_gnar.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "gnar_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "gnar_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "gnar_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"gnar_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
