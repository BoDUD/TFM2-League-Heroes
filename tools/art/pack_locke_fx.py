#!/usr/bin/env python3
"""Build locke_fx_pack.zip: step 3 of Locke's sprite - Codex draws his effects (pack_trundle_fx.py's way).

    python tools/lol/fx_ref_locke.py            # League's particle textures -> C:/t/lk_work/fxref (Riot's art, local only)
    python tools/art/pack_locke_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name locke_fx_redo_pack]

The pack (C:/t/lk_work/fx/locke_fx_pack, zipped into --out, default dist/locke_packs) holds PROMPTS.md (also written to
assets/source/locke/PROMPTS_FX.md), design/locke_design.png (the approved idle at 4x on its own squares),
design/locke_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/lol_fx_ref.png (League's own particle textures for Locke, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_locke.py, the user's picks 2026-10-26: mid, layout A - Q / E /
R, W in the passive): view_projectiles q_nail, r_case; view_effects a_hit, q_hit, q_pop, e_out, e_in, e_hit, e_dash,
w_ign, w_end, r_land, r_hit, r_tick, r_seal, p_reset; view_buffs slow (q_slow, r_slow), q_mark, r_mark, w_aura (w_on).
League's colours: his SOUL FIRE (white and pale cyan to bright blue and indigo: the W look of step 0's B), ASH (pale to
dark warm grey: the Ashen Exorcist), the SEAL's magenta-purple (the bands of his case), the SILVER of his nails, a few
EMBER sparks. Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is
symmetric left to right; the two projectiles point right and are symmetric top to bottom (the game turns them).
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

TMP = "C:/t/lk_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "locke", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "locke", "hd")
NAME = "locke_fx_pack"
PPU = 2.0

SOUL = "#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8"    # his soul fire: white core to bright blue and indigo
ASH = "#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C"              # ash and soot: the Ashen Exorcist
SEAL = "#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050"             # the seal: the magenta-purple of his case's bands
SILVER = "#FFFFFF, #E2ECF2, #AEC0CC, #6E8496"                    # his silver nails
EMBER = "#FFF4C8, #FFC46A, #F07A32"                              # a few ember sparks
SO = f"a soul fire ramp ({SOUL})"
AS = f"an ash ramp ({ASH})"
SE = f"a magenta-purple seal ramp ({SEAL})"
SI = f"a silver ramp ({SILVER})"
EM = f"an ember ramp ({EMBER})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
TB = "pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight)"
EXO = ("everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash "
       "and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no "
       "orange fire (only a few ember sparks where written)")
TARGET = "the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = "Locke stands in the middle, not drawn: about 27 squares wide and 44 tall"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- projectiles
    ("q_nail", "伏魔三钉：飞出去的钉子，4 帧循环", "view_projectiles `league_locke_q_nail`（弹道，z 2；朝右、上下对称）", "16 × 8",
     "扔出去的**驱魔大钉**：一根银色的长钉，钉尖朝右，钉身裹着一层冷蓝白的灵魂火，后面拖着一条蓝色的火尾和几点灰烬（参考 q_trail、"
     "q_mis_nailedgeblend、q_cursed_trail）。**朝右飞，上下对称**，4 帧循环。",
     SI + ", " + SO + ", " + AS,
     "A FLYING SOUL NAIL, 4 looping frames, " + TB + ": a long silver nail 9 squares long with its point on the right and "
     "a flat round head on the left, wrapped in thin white-cyan soul flame, a tapering blue flame tail 6 squares long "
     "behind it with a few ash flecks; frames 1-4 the tail flickering. " + EXO + ".",
     row(4, 16, 8) + CENTER),
    ("r_case", "万魔狱：飞出去的棺匣，4 帧循环", "view_projectiles `league_locke_r_case`（弹道，z 2；朝右、上下对称）", "24 × 12",
     "扔出去的**封印棺匣**：横着飞的黑色六边形长匣（品红紫箍带、银色菱形钉），匣身缝隙里透出品红紫的光，后面拖着一条紫蓝的烟尾"
     "（参考 r_mis_firemask、r_totem_idle_blurtrail）。**朝右飞，上下对称**（匣子正面、背面一样），4 帧循环。",
     SE + ", " + SO + ", " + AS,
     "A FLYING BINDING CASE, 4 looping frames, " + TB + ": a long black hexagonal case 16 squares long and 6 tall lying "
     "along the flight, magenta-purple bands round it and small silver diamond studs, a magenta glow leaking from its "
     "seams; a short trail of violet-blue smoke and ash behind it on the left; frames 1-4 the glow pulsing and the trail "
     "curling. The case has a 1-square near-black outline. " + EXO + ".",
     row(4, 24, 12) + CENTER),
    # ---- attack and passive
    ("a_hit", "普攻：钉子刺中，3 帧", "view_effects `league_locke_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "钉子捅中：一个银白的十字星闪，四周迸出几点冷蓝的灵魂火星（被动「圣银穿心」的附加魔法伤害）。**左右对称**，3 帧。",
     SI + ", " + SO,
     "A SILVER STAKE HIT, 3 frames, " + LR + ": 1 a white four-point star flash 6 squares across; 2 the star 10 across "
     "with cold blue sparks bursting out at mirrored places; 3 the sparks further out, dimming into ash flecks. " + EXO + ".",
     row(3, 14, 14) + CENTER),
    # ---- skill: Q Ritual Nails
    ("q_hit", "伏魔三钉：钉子扎中，3 帧", "view_effects `league_locke_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "钉子扎中敌人：一圈冷蓝的火花炸开、中间一下白光，几点灰烬往外飞（参考 q_proc_tar、q_tar）。**左右对称**，3 帧。",
     SO + ", " + AS,
     "A NAIL STRIKING, 3 frames, " + LR + ": 1 a bright white-cyan spiky star 8 squares across; 2 a ring of cold blue "
     "soul sparks 12 across bursting out at mirrored places; 3 the sparks dimming into ash flecks. " + EXO + ".",
     row(3, 14, 14) + CENTER),
    ("q_mark", "伏魔三钉：头顶的钉子印记，4 帧循环", "view_buffs `league_locke_q_mark`（跟随目标，头顶，z 3；左右对称）", "14 × 10",
     "被钉上印记的人头顶：**三根小银钉**，中间一根竖着、两边两根往外斜，下面托着一弯冷蓝的月牙（参考 nail_ui_01：洛克在英雄联盟里就是这个印记）。"
     "一闪一闪。**左右对称**，4 帧循环。",
     SI + ", " + SO,
     "A NAIL MARK OVER THE HEAD, 4 looping frames, " + LR + ": three small silver nails pointing down, the middle one "
     "upright and 6 squares tall, the side ones leaning out, resting on a thin cold-blue crescent moon 12 squares wide "
     "that cups them from below; frames 1-4 the nails glinting in turn and the crescent pulsing. " + EXO + ".",
     row(4, 14, 10) + CENTER),
    ("q_pop", "伏魔三钉：印记被引爆，4 帧", "view_effects `league_locke_q_pop`（跟随目标，z 2；左右对称）", "22 × 26",
     "洛克普攻把钉子印记引爆：几根灵魂钉从四周往目标身上一起扎进去，冷蓝的火一下炸开（参考 q_consume_inward）。"
     "**身体位置留空**，钉子和火只在外圈。**左右对称**，4 帧。",
     SO + ", " + SI + ", " + AS,
     "THE NAILS DRIVEN IN, 4 frames, " + LR + ", " + TARGET + ": 1 three ghostly silver-blue nails in a ring around the "
     "unit's middle, 20 across, points inward; 2 the nails darting inward; 3 a burst of cold blue soul flame 18 across at "
     "the middle with white sparks; 4 ash flecks drifting away. The middle (the body) mostly empty. " + EXO + ".",
     row(4, 22, 26) + CENTER),
    ("slow", "减速：脚下一圈灰烬，4 帧循环", "view_buffs `league_locke_q_slow` / `league_locke_r_slow`（跟随，脚下，z -1；左右对称）",
     "16 × 8",
     "被减速：脚下一圈灰黑的灰烬和几缕冷蓝的火苗，灰烬往上飘。**左右对称**，4 帧循环。",
     AS + ", " + SO,
     "AN ASH SLOW AT THE FEET, 4 looping frames, " + LR + ", " + FEET + ": a thin ellipse of grey ash 14 wide with a few "
     "small cold blue flames on it; frames 1-4 the flames flickering in turn and ash flecks drifting up. " + EXO + ".",
     row(4, 16, 8) + CENTER),
    # ---- skill2: E Ashen Pursuit
    ("e_out", "灰猎无影：原地消散，5 帧", "view_effects `league_locke_e_out`（在洛克出发的地方，z 2，不跟随；左右对称）", "30 × 48",
     "洛克瞬移走：原地他的身影**化成一团灰烬**往上散开，脚下一圈冷蓝的符文圈一闪（参考 e_ash_erosion、e_sigilring）。"
     "**左右对称**，5 帧。",
     AS + ", " + SO,
     "VANISHING INTO ASH, 5 frames, " + LR + ", " + HIM + ": 1 a cold blue sigil ring 22 wide flashing " + FEET + " and a "
     "tall column of grey ash flakes in his shape 18 wide and 40 tall; 2 the column breaking up into drifting ash; 3 the "
     "ash scattering up and out, a few blue embers; 4 thin ash wisps high up; 5 the last flakes fading. " + EXO + ".",
     row(5, 30, 48) + CENTER),
    ("e_in", "灰猎无影：在目标身边出现，5 帧", "view_effects `league_locke_e_in`（在洛克落脚的地方，z 2，不跟随；左右对称）", "30 × 48",
     "洛克从灰烬里出现：一团灰烬从四周**往中间卷回来**、凝成他的身形，脚下冷蓝的符文圈亮起（参考 e_blinkend_swirlin、e_sigilring）。"
     "**身体位置留空**。**左右对称**，5 帧。",
     AS + ", " + SO,
     "REAPPEARING FROM ASH, 5 frames, " + LR + ", " + HIM + ": 1 ash flakes scattered wide 28 across; 2 the ash swirling "
     "inward at both sides; 3 the ash drawn into a tall column 18 wide, a cold blue sigil ring 22 wide lighting up " + FEET +
     "; 4 a bright white-blue flash at the column's edges; 5 the last ash and the ring fading. The middle (his body) left "
     "empty from frame 3. " + EXO + ".",
     row(5, 30, 48) + CENTER),
    ("e_hit", "灰猎无影：落地的灵魂冲击，4 帧", "view_effects `league_locke_e_hit`（跟随，z 2；左右对称）", "44 × 18",
     "落地时一圈冷蓝的灵魂火**贴地往外推开**，带起灰烬（参考 e_groundwave），打到周围的敌人。**左右对称**，4 帧。",
     SO + ", " + AS,
     "A SOUL SHOCKWAVE ON THE GROUND, 4 frames, " + LR + ", " + FEET + ": 1 a white-blue flash ellipse 12 wide; 2 a ring of "
     "cold blue soul flame 28 wide pushing out; 3 the ring 40 wide, breaking into blue flames and ash; 4 ash puffs fading "
     "at both ends. " + EXO + ".",
     row(4, 44, 18) + CENTER),
    ("e_dash", "灰猎无影：冲刺的残影，4 帧", "view_effects `league_locke_e_dash`（在洛克身上，z 2，不跟随；左右对称）", "40 × 20",
     "E 之后那一下冲刺普攻：他身后（两边都是）一道横着的灰烬残影和冷蓝的斩痕（参考 e_slash_front、e_slash_mid、e_string_trail）。"
     "这张在红色方也不翻，所以**左右对称**画成一条横着的斩痕，4 帧。",
     SO + ", " + AS + ", " + SI,
     "A DASH SLASH, 4 frames, " + LR + ": 1 a thin horizontal white-blue slash line 30 squares long at the middle; 2 the "
     "slash 38 long and 4 tall with a silver edge and cold blue flame along it; 3 the slash breaking into a row of ash "
     "streaks; 4 ash streaks fading. " + EXO + ".",
     row(4, 40, 20) + CENTER),
    ("p_reset", "灰猎无影：参与击杀、E 刷新，4 帧", "view_effects `league_locke_p_reset`（跟随洛克，z 2；左右对称）", "26 × 16",
     "参与击杀后 E 重置：洛克头顶一圈冷蓝的符文环亮一下，几点灰烬往上冒。**左右对称**，4 帧。",
     SO + ", " + AS,
     "A RESET SIGIL OVER HIS HEAD, 4 frames, " + LR + ": 1 a thin cold blue ring 10 wide; 2 the ring 22 wide with four "
     "small rune marks at its top, bottom, left and right; 3 the ring flashing white; 4 the ring fading into ash flecks "
     "rising. " + EXO + ".",
     row(4, 26, 16) + CENTER),
    # ---- passive: W Soul Ignition
    ("w_ign", "灵焰仪式：点燃灵魂，6 帧", "view_effects `league_locke_w_ign`（跟随洛克，z 2；左右对称）", "36 × 52",
     "洛克点燃自己的灵魂：脚下一圈冷蓝的光环，**一圈冷蓝白的灵魂火从脚下往上卷起来**、包住他的外圈，顶上散出火星（参考 w_fire_swirl、"
     "w_cas_sheenring、w_groundwind）。火只在他身体外圈，**身体位置留空**。**左右对称**，6 帧。",
     SO + ", " + AS,
     "A SOUL IGNITING, 6 frames, " + LR + ", " + HIM + ": 1 a bright white-blue ring 20 wide " + FEET + "; 2 tongues of "
     "cold blue-white soul flame rising at both sides of him to his waist; 3 the flames swirling up to his shoulders; 4 "
     "the flames over his head, a white flash ring at his chest height at the sides; 5 the flames thinning, blue sparks "
     "flying up; 6 a few sparks and ash flecks. The middle (his body) left empty. " + EXO + ".",
     row(6, 36, 52) + CENTER),
    ("w_aura", "灵焰仪式：身上燃着的灵魂火，6 帧循环", "view_buffs `league_locke_w_on`（跟随洛克，z -1；左右对称）", "34 × 50",
     "W 持续时（4 秒）他身边一直燃着冷蓝的灵魂火：几缕火苗贴着他身体两侧往上飘、脚下一圈淡淡的光（他这时攻速、移速变快，同时被灵魂火灼烧）。"
     "**身体位置留空**。**左右对称**，6 帧循环。",
     SO + ", " + AS,
     "A SOUL FIRE AURA, 6 looping frames, " + LR + ", " + HIM + ": a soft ellipse of cold blue light " + FEET + " 22 wide, "
     "thin tongues of white-blue soul flame licking up both sides of his body to above his shoulders; frames 1-6 the "
     "flames rising and flickering in turn, a few blue sparks drifting up. The middle (his body) left empty. " + EXO + ".",
     row(6, 34, 50) + CENTER),
    ("w_end", "灵焰仪式：结束时回血，5 帧", "view_effects `league_locke_w_end`（跟随洛克，z 2；左右对称）", "30 × 46",
     "W 结束、把烧掉的血补回来：灵魂火**往里收回他身上**，几点冷蓝的光点从四周飘回来、头顶一个小小的白光（参考 q_consume_inward）。"
     "**身体位置留空**。**左右对称**，5 帧。",
     SO,
     "A SOUL FIRE DRAWN BACK IN, 5 frames, " + LR + ", " + HIM + ": 1 cold blue motes scattered around him 28 wide; 2 the "
     "motes drifting inward at both sides; 3 thin blue streaks converging on his chest height at both sides; 4 a small "
     "white plus sparkle over his head; 5 the last motes fading. The middle (his body) left empty. " + EXO + ".",
     row(5, 30, 46) + CENTER),
    # ---- ult: R Purgatory
    ("r_land", "万魔狱：棺匣落地、封印圈，8 帧", "view_effects `league_locke_r_land`（大表，落点，z 1，不跟随；左右对称）", "60 × 46",
     "棺匣砸在地上：**黑色棺匣竖着插进地面**（正面看，品红紫箍带、银菱形钉，有近黑描边），地上一大圈**品红紫的封印法阵**亮起来"
     "（圆圈、四个符文、中间十字，参考 r_tell_outercircle、r_totem_timer_runes、r_aoe_flash_totem），冷蓝的冲击和灰烬往外推开。"
     "法阵最大时**横向 50 格、纵向 16 格**。**左右对称**，8 帧。",
     SE + ", " + SO + ", " + AS,
     "A BINDING CASE SLAMMING DOWN, 8 frames, " + LR + ": the case seen from the FRONT, standing upright in the middle "
     "with its foot on the ground line 6 squares above the bottom: a black hexagonal case 10 squares wide and 26 tall with "
     "magenta-purple bands and silver diamond studs and a 1-square near-black outline. 1 the case dropping in from the "
     "top, a white flash where it lands; 2 the case planted, a cold blue shockwave ring 24 wide " + FEET + "; 3 a "
     "magenta-purple seal circle 40 wide lighting up on the ground round it, ash bursting out at both sides; 4 the circle "
     "50 wide and 16 tall with four rune marks at its left, right, front and back and a cross through it, magenta light "
     "rising from the case's seams; 5-6 the runes glowing, ash settling; 7 the circle dimming; 8 the case and a faint "
     "circle. Frames 4-6 MUST fill 50 squares across. " + EXO + ".",
     row(8, 60, 46) + CENTER),
    ("r_hit", "万魔狱：被砸中，4 帧", "view_effects `league_locke_r_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "被棺匣的冲击打中：一下品红紫的闪光，四周迸出冷蓝的火花和灰烬。**左右对称**，4 帧。",
     SE + ", " + SO + ", " + AS,
     "A SEAL BLAST HIT, 4 frames, " + LR + ": 1 a magenta-white flash 8 squares across; 2 a burst of magenta-purple and "
     "cold blue sparks 16 across at mirrored places; 3 the sparks further out, ash flecks; 4 fading ash. " + EXO + ".",
     row(4, 18, 18) + CENTER),
    ("r_mark", "万魔狱：被标记的人，6 帧循环", "view_buffs `league_locke_r_mark`（跟随目标，z 3；左右对称）", "24 × 40",
     "被大招标记的人（4 秒内血量低于处决线就会被封印）：身体外圈一圈**品红紫的封印符文**慢慢转，头顶一个小小的品红紫十字符号"
     "（参考 r_tell_outercircle、r_totem_timer_runes）。**身体位置留空**。**左右对称**，6 帧循环。",
     SE,
     "A SEAL MARK ON A UNIT, 6 looping frames, " + LR + ", " + TARGET + ": a loose ring of small magenta-purple rune marks "
     "around the unit's middle 22 wide seen slightly from above, and a small magenta cross sigil 6 squares tall over its "
     "head; frames 1-6 the runes glowing in turn around the ring and the sigil pulsing. The middle (the body) left "
     "empty. " + EXO + ".",
     row(6, 24, 40) + CENTER),
    ("r_tick", "万魔狱：处决检查，3 帧", "view_effects `league_locke_r_tick`（跟随目标，z 2；左右对称）", "12 × 12",
     "标记每隔一会儿收紧一下：目标身上一个小小的品红紫符文一闪。**左右对称**，3 帧。",
     SE,
     "A SEAL PULSE, 3 frames, " + LR + ": 1 a small magenta rune mark 4 squares tall; 2 the rune 6 tall with a thin "
     "magenta ring 10 wide round it; 3 the ring fading. " + EXO + ".",
     row(3, 12, 12) + CENTER),
    ("r_seal", "万魔狱：封印成功，6 帧", "view_effects `league_locke_r_seal`（跟随洛克，z 2；左右对称）", "30 × 48",
     "封印了一个英雄、法器回到洛克手里：一道品红紫的灵魂光从高处**落进他身后的棺匣**，他身上闪一下品红紫的光、往上冒符文（大招冷却减少、"
     "处决线变高）。**身体位置留空**。**左右对称**，6 帧。",
     SE + ", " + SO,
     "A SOUL SEALED, 6 frames, " + LR + ", " + HIM + ": 1 a magenta-white soul wisp high above him; 2 the wisp streaking "
     "down toward him; 3 a magenta flash around his outline at both sides; 4 three small magenta runes rising at both "
     "sides of him; 5 the runes higher, dimmer; 6 the last motes fading. The middle (his body) left empty. " + EXO + ".",
     row(6, 30, 48) + CENTER),
]
BIG_FX = ["r_land"]
FLYING = ["q_nail", "r_case"]
FORWARD = []

GROUPS = [
    ("q_nail q_hit (the nails)", ["locke_base_q_trail_06", "locke_q_mis_nailedgeblend_mask", "locke_q_cursed_trail_base3",
                                  "lock_base_q_proc_tarcenter", "lock_base_q_tar"]),
    ("q_mark q_pop (the mark)", ["nail_ui_01_all_revised", "nail_ui_01_moon", "locke_q_consume_inward",
                                 "locke_q_tar_dissolve"]),
    ("e_out e_in e_hit e_dash (the pursuit)", ["locke_e_ash_erosion", "locke_e_blinkend_swirlin", "locke_e_sigilring_blur",
                                               "locke_base_e_groundwave_reduced", "locke_e_slash_front_sharp_1"]),
    ("w_ign w_aura w_end (the soul fire)", ["locke_base_w_fire_swirl", "locke_w_cas_sheenring", "locke_base_w_groundwind",
                                            "locke_base_w_head_cone", "locke_base_4x4fire"]),
    ("r_case r_land (the case)", ["locke_base_r_mis_firemask", "locke_base_r_totem_idle_blurtrail", "lock_base_r_tell_outercircle",
                                  "locke_base_r_totem_timer_runes", "locke_base_r_aoe_flash_totem_a"]),
    ("r_hit r_mark r_seal (the seal)", ["locke_base_r_aoe_tar_mid", "lock_base_r_totemconsume_decal",
                                        "locke_base_r_smoke_4x4", "locke_base_ring_00_erosion"]),
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
    """Locke at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"洛克 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 灰烬驱魔人 洛克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/locke_design.png`：Q 版年轻驱魔人，金发、紫色圆眼镜、咧嘴笑、"
      "深青绿长风衣、宝蓝敞领衬衫、背上黑色棺匣、手里银钉）。"
      f"洛克在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/locke_size.png`：洛克缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里洛克自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**洛克是灰烬驱魔人，特效都是灵魂火和灰烬**：**冷色的灵魂火**（白、浅青、亮蓝到靛蓝——就是他 W 变身时的颜色）、"
      "**灰烬**（浅灰到深灰）、封印用的**品红紫**（和他棺匣的箍带一样）、钉子的**银色**，偶尔几点**橙黄火星**；不要光滑的霓虹光束，也不要橙红色的普通火。")
    a("> - **特效要亮**：每道光、每团火都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **光、火、灰烬、符文没有黑描边**；**只有棺匣这个“东西”（`r_case`、`r_land` 里的匣子）有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了两个弹道，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——棺匣落地 `r_land` **正面**看。"
      "**弹道**（`" + "`、`".join(FLYING) + "`）**朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `locke_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「圣银穿心」 | 拿钉子捅，附带魔法伤害；打英雄会引爆 Q 的钉子印记 | `a_hit` · `q_pop` |")
    a("| 被动里的 W「灵焰仪式」 | E 落到英雄身边时点燃灵魂：攻速、移速变快，每秒烧掉一点自己的血，结束时补回来 | `w_ign` · `w_aura` · `w_end` |")
    a("| 技能 1 =「伏魔三钉」 | 连扔三颗钉：伤害、减速、在英雄头上留下钉子印记 | `q_nail` · `q_hit` · `q_mark` · `slow` |")
    a("| 技能 2 =「灰猎无影」 | 化成灰烬瞬移到英雄身边、落地冲击，下一次普攻冲刺穿过目标；参与击杀刷新 | `e_out` · `e_in` · `e_hit` · `e_dash` · `p_reset` |")
    a("| 大招 =「万魔狱」 | 抡起棺匣扔出去：落地伤害、减速、给英雄打上封印标记，血量低于处决线就被封印 | `r_case` · `r_land` · `r_hit` · `r_mark` · `r_tick` · `r_seal` · `slow` |\n")
    a("连招：**钉子扎中英雄 → 灰猎无影马上好**，**闪到英雄身边 → 立即点燃灵魂**，**参与击杀 → 灰猎无影刷新**，**大招标记 → 伏魔三钉马上好**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、灰烬没有黑描边，也不要用最深的颜色给形状描一圈边**（棺匣除外）。")
    a("- **都是灵魂火和灰烬**：冷蓝的灵魂火、灰烬、品红紫的封印、银色的钉；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("灵魂火", SOUL), ("灰烬", ASH), ("封印·品红紫", SEAL), ("银钉", SILVER), ("火星", EMBER)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（光环、法阵、灰烬）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `locke_fx_{name}.png`：{title}\n")
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
        a(f"| `locke_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_locke_fx`（小的）和 `league_locke_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_locke.py 的 views；buff 的 tag：w_on → w_aura、q_slow / r_slow → slow）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称。")
    a("- 用 `pixel_1x/` 切格（import_trundle_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="locke_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "locke_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_locke.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "locke_design.png"))
    shape = size_sheet(os.path.join(out, "design", "locke_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"locke_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "left-right"} for x in FX], f, ensure_ascii=False, indent=1)
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
