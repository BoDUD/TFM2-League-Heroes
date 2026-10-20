#!/usr/bin/env python3
"""Build mel_fx_pack.zip: step 3 of Mel's sprite - Codex (or Gemini) draws her effects (pack_warwick_fx.py's way,
pack_rammus_fx's sheets).

    python tools/lol/fx_ref_mel.py          # League's particle textures -> C:/t/ml_work/fxref (Riot's art, local only)
    python tools/art/pack_mel_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name mel_fx_redo_pack]

The pack (C:/t/ml_work/fx/mel_fx_pack, zipped into --out, default dist/mel_packs) holds PROMPTS.md (also written to
assets/source/mel/PROMPTS_FX.md), design/mel_idle.png (her idle at 4x, the design's squares at PPU 1.5),
design/mel_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/mel_shots.png (action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle textures
for Mel grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_mel.py): view_projectiles a_bolt (also the add-on's reflected
bolt w_back), p_bolt, e_orb; view_effects a_hit, p_hit, q_volley, q_hit, e_burn, r_cast, r_hit (and the add-on's
x_hit); view_buffs w_on (Rebuttal's barrier), e_bound, e_slow, p_3 / p_6 / p_9 (Searing Brilliance's charged bolts) and
the add-on's m_mark (Overwhelm). League's colours: her magic is RADIANT GOLD light with a white core, touched with her
robe's CRIMSON-PINK sparks; Golden Eclipse is a dark disc with a blazing gold corona. Red side: the client never mirrors
an effect picture, so every hit, buff, caster and ground picture is symmetric left to right; the projectiles (bolts,
orb) are turned to their flight by the game and point right.
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

TMP = "C:/t/ml_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "mel", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_mel")
NAME = "mel_fx_pack"

GOLD = "#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10"         # her radiant light: bolts, volley, orb, beams
PINK = "#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33"                    # her robe's crimson-pink sparks and trails
ECL = "#FFFFFF, #FFF2B0, #FFC94A, #D4831C, #5A2A1A, #24101A"            # Golden Eclipse: corona over a dark disc
GO = f"a radiant gold ramp ({GOLD})"
PI = f"a crimson-pink spark ramp ({PINK})"
EC = f"an eclipse ramp ({ECL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
HER = ("the noblewoman mage stands in the middle, not drawn: 43 squares from the top of her hair bun to the ground, "
       "about 40 squares wide with her robe")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
row = RF.row
POINT = "pointing RIGHT (its head at the cell's right, its tail toward the left; the game turns it to its flight)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack and the passive
    ("a_bolt", "普攻：金色光弹（弹道，循环），3 帧", "view_projectiles `league_mel_a_bolt`（弹道：游戏会把它转到飞行方向；附加包反弹回去的光弹也用这张）",
     "12 × 7",
     "她的普攻：一颗金色的光弹，**头朝右**（游戏会转到飞行方向）：亮白的菱形弹头，后面拖一小段由金到粉红的尾巴，尾巴一帧一帧闪动"
     "（参考 basicattack_constellation_line、basicattack_wisps、p_yellow_ray）。3 帧循环。",
     GO + " and " + PI,
     "A RADIANT BOLT, 3 frames, a loop, " + POINT + ": a bright white-gold diamond head 4 squares long, behind it a "
     "tapering tail 7 squares long going from gold to crimson-pink, two tiny pink sparks trailing; each frame the tail "
     "flickers (its sparks at other places).",
     row(3, 12, 7) + "; the bolt centred vertically, its head touching the cell's right side."),
    ("p_bolt", "灼灼之光：小光弹（弹道，循环），3 帧", "view_projectiles `league_mel_p_bolt`（弹道，游戏会转到飞行方向）", "8 × 5",
     "放技能后下一次普攻多射出的小光弹：比普攻的小一号，粉金色，**头朝右**，3 帧循环（参考 p_flecks、p_glowdust）。",
     PI + " and " + GO,
     "A SMALL SPARK BOLT, 3 frames, a loop, " + POINT + ": a white-pink head 2 squares long with a short gold-pink tail "
     "4 squares long; the tail flickering.",
     row(3, 8, 5) + "; the bolt centred vertically, its head touching the cell's right side."),
    ("a_hit", "普攻打中：金色星芒，4 帧", "view_effects `league_mel_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "光弹打中目标：一颗金色的星芒炸开（白芯、四道长芒四道短芒），然后散成几点金色和粉红的光点（参考 basicattack_mark_mult、"
     "w_impact_flare、r_hit1）。**左右对称**，4 帧。",
     GO + " and " + PI,
     "A RADIANT HIT, 4 frames, " + LR + ": 1 a white core flash 4 squares across; 2 an eight-point gold star 14 squares "
     "across (four long rays, four short diagonal ones); 3 the star thinner, gold and pink motes flying out at mirrored "
     "places; 4 only fading motes.",
     row(4, 16, 16) + CENTER),
    ("p_hit", "小光弹打中，3 帧", "view_effects `league_mel_p_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "小光弹打中：一个小小的粉金色火花，3 帧，**左右对称**。",
     PI,
     "A SMALL SPARK, 3 frames, " + LR + ": 1 a white-pink plus sign 5 squares across; 2 a pink four-point star 8 across; "
     "3 two fading pink motes at mirrored places.",
     row(3, 10, 10) + CENTER),
    ("p_3", "灼灼之光：蓄好 3 颗光弹（她身上，循环），4 帧", "view_buffs `league_mel_p_3`（跟随她，z 2；左右对称；循环）", "44 × 14",
     "放了一个技能后，下一次普攻会多射 3 颗光弹：她腰两边浮着 **3 颗**小小的金色光球（中间一颗、左右各一颗，排成一道微弯的弧），"
     "一闪一闪地上下浮动（参考 p_glowdust、packed_glows）。**她站在中间不画人**，**左右对称**，4 帧循环。",
     GO,
     "THREE FLOATING LIGHT ORBS round a mage's waist, 4 frames, a loop, " + LR + " (" + HER + ", her body area left "
     "EMPTY): three small gold orbs, each 3 squares across with a white core, on a gentle arc across the cell (one at "
     "the middle top, one at each end a little lower, 36 squares apart end to end); each frame they bob a square up or "
     "down in turn and glimmer.",
     row(4, 44, 14) + CENTER),
    ("p_6", "灼灼之光：蓄好 6 颗光弹（她身上，循环），4 帧", "view_buffs `league_mel_p_6`（跟随她，z 2；左右对称；循环）", "48 × 18",
     "放了两个技能：**6 颗**光球（左右各 3 颗，排成两道弧），其它同 p_3。",
     GO,
     "SIX FLOATING LIGHT ORBS round a mage's waist, 4 frames, a loop, " + LR + " (" + HER + ", her body area left "
     "EMPTY): six small gold orbs (3 squares across, white cores), three on each side on two mirrored arcs, 40 squares "
     "apart end to end; they bob and glimmer in turn.",
     row(4, 48, 18) + CENTER),
    ("p_9", "灼灼之光：蓄满 9 颗光弹（她身上，循环），4 帧", "view_buffs `league_mel_p_9`（跟随她，z 2；左右对称；循环）", "52 × 22",
     "蓄满了：**9 颗**光球围成一个扁圆的环（前面中间一颗最亮），金色更亮，带一点粉红的光晕，其它同 p_3。",
     GO + " and " + PI,
     "NINE FLOATING LIGHT ORBS in a flat ring round a mage's waist, 4 frames, a loop, " + LR + " (" + HER + ", her body "
     "area left EMPTY): nine gold orbs (3 squares across, white cores, a faint pink halo) on a flat ellipse 46 squares "
     "wide and 16 tall, the front middle one the brightest; each frame they glimmer in turn.",
     row(4, 52, 22) + CENTER),
    # ---- Q Radiant Volley
    ("q_volley", "Q 耀光齐射：一阵光弹从天而降（地上那一点，不跟随），8 帧",
     "view_effects `league_mel_q_volley`（放在落点上，不跟随，画在人物上面 z 3；左右对称；大图表）", "48 × 56",
     "Q 的落点：**六颗金色光弹从正上方一颗接一颗砸下来**，落在一个约 36 格宽的椭圆范围里（落点左右对称地分布），每颗落地炸成一朵小"
     "金星，地上一圈淡淡的金色光晕（参考 q_flame_ring、r_airbullet、r_hit3）。一共 8 帧（约 0.6 秒，和 Q 连续 6 次爆炸对上）。",
     GO + " and " + PI,
     "A VOLLEY OF FALLING BOLTS onto a spot, 8 frames, " + LR + ": a faint gold ground ellipse 36 squares wide and 10 tall "
     "at the cell's bottom; six radiant bolts (each a white-gold streak 2 squares wide, 10 tall, a pink tail above it) "
     "fall STRAIGHT DOWN from the top of the cell one after another, landing at mirrored spots inside the ellipse, two at "
     "a time: 1 two streaks high up; 2 those two lower, two more appearing at the top; 3 the first two land - two small "
     "gold stars (8 across) on the ground; 4-6 the same for the next pairs, the stars of the earlier ones fading into "
     "motes; 7 the last stars and motes; 8 only the fading ground ellipse and motes.",
     row(8, 48, 56) + "; centered across, the ground ellipse's middle 6 squares above the cell's bottom row."),
    ("q_hit", "Q：爆炸打中（敌人身上），3 帧", "view_effects `league_mel_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "每次爆炸打中一个敌人：一朵金粉色的小爆光，3 帧，**左右对称**（参考 r_hit3）。",
     GO + " and " + PI,
     "A SMALL GOLD-PINK BURST, 3 frames, " + LR + ": 1 a white core 4 squares; 2 a round gold burst 12 across with pink "
     "edges; 3 broken into pink and gold motes, fading.",
     row(3, 14, 14) + CENTER),
    # ---- E Solar Snare
    ("e_orb", "E 阳炎涡旋：阳炎法球（弹道，循环），4 帧", "view_projectiles `league_mel_e_orb`（弹道，游戏会转到飞行方向；大图表）", "28 × 28",
     "E 射出的阳炎法球：一颗小太阳，白芯金身，外面一圈短短的金色光芒（像太阳的光刺），再外面一圈淡淡的粉红光晕，光芒一帧一帧转动"
     "（参考 e_tar_center、e_tar_centerglowpattern、e_scroll、q_flame_ring）。圆的，**上下左右都对称**，4 帧循环。",
     GO + " and " + PI,
     "A RADIANT SUN ORB in flight, 4 frames, a loop, symmetric in every direction: a white-gold core 10 squares across, a "
     "ring of twelve short gold sun rays round it (each 3-4 squares), a faint crimson-pink halo ring outside them; each "
     "frame the rays turn a little (one twelfth of a turn) and the core pulses.",
     row(4, 28, 28) + CENTER),
    ("e_bound", "E：禁锢（被禁锢的敌人身上，循环），4 帧", "view_buffs `league_mel_e_bound`（跟随目标，z 3；左右对称；循环）", "26 × 30",
     "被法球中心禁锢住的敌人：两道扁扁的金色光环一上一下箍住他的腿和腰，环上带着太阳光刺，一闪一闪地收紧（参考 e_wall、e_aoe_mult、"
     "e_binarymult）。**被禁锢的人站在中间不画**，**左右对称**，4 帧循环。",
     GO,
     "A SOLAR SNARE ROUND A CHAMPION, 4 frames, a loop, " + LR + " (" + CHAMP + ", the body area left EMPTY): two flat gold "
     "light rings (ellipses 22 wide and 6 tall, 2 squares thick, white inner edge), one at the knees and one at the waist, "
     "short sun-ray spikes standing out of them at mirrored places; the rings pulse tighter and brighter on frames 1 and "
     "3.",
     row(4, 26, 30) + "; centered across, the lower ring 4 squares above the cell's bottom row."),
    ("e_slow", "E：外圈减速的光晕（敌人脚下，循环），4 帧", "view_buffs `league_mel_e_slow`（跟随目标，画在人物下面 z -1；左右对称；循环）",
     "26 × 10",
     "被法球外圈扫到、减速中的敌人：脚下一圈金色的光晕，几点金色的光尘往上飘（参考 e_aoe_damagehotspot、e_groundtrail）。"
     "**只画在脚下**，**左右对称**，4 帧循环。",
     GO,
     "A GOLD GLOW under a champion's feet, 4 frames, a loop, " + LR + ": a glowing gold ellipse on the ground 22 squares "
     "wide and 6 tall, its rim brightest; a few gold dust motes rising from it at mirrored places, a little higher each "
     "frame, new ones starting low.",
     row(4, 26, 10) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
    ("e_burn", "E：灼烧（敌人身上），3 帧", "view_effects `league_mel_e_burn`（跟随目标，z 2；左右对称）", "12 × 14",
     "外圈的持续伤害每跳一次：一小簇金橙色的火苗往上一窜（参考 deathfire_mask、q_flame_ring），3 帧，**左右对称**。",
     GO,
     "A SMALL GOLD FLAME LICK, 3 frames, " + LR + ": 1 a small gold flame 4 wide, 5 tall at the bottom middle; 2 it rises "
     "to 9 tall with a white core and two tongues; 3 broken into gold sparks drifting up.",
     row(3, 12, 14) + CENTER),
    # ---- R Golden Eclipse
    ("r_cast", "R 鎏金蚀日：头顶升起日蚀（她身上，跟随），8 帧",
     "view_effects `league_mel_r_cast`（跟随她，画在人物上面 z 2；左右对称；大图表）", "64 × 80",
     "R：她头顶上方升起一轮**金色的日蚀**——中间一个深色的圆盘（深紫黑），一圈耀眼的金色日冕，长长的细金光往四周放射，越来越亮，"
     "最后一闪（参考 r_centershine、r_glow、r_s_05、r_space、r_zone_aoe_glow）。**她站在格子下半部不画人，日蚀在她头顶上方**，"
     "**左右对称**，8 帧。",
     EC,
     "A GOLDEN ECLIPSE rising over a mage's head, 8 frames, " + LR + " (" + HER + " in the lower part of the cell, her "
     "standing point at the bottom middle, her body area left EMPTY): high above her (its centre 14 squares under the "
     "cell's top) 1 a small gold spark; 2 a gold ring 8 across; 3 the ring 16 across with a DARK DISC (deep plum-black) "
     "filling it; 4 the corona - a blazing gold rim 2-3 squares thick round the dark disc, eight long thin gold rays "
     "reaching out 10-14 squares; 5 the rays longer, a white flash on the rim; 6 like 4, brighter; 7 the rays shrinking, "
     "the disc fading to gold; 8 only fading gold motes.",
     row(8, 64, 80) + "; centered across."),
    ("r_hit", "R：天降金光（每个带残影的敌人身上），6 帧", "view_effects `league_mel_r_hit`（跟随目标，z 2；左右对称；大图表）",
     "24 × 60",
     "R 打中每一个带残影的敌人：一道金色的光柱从天上直直劈到他身上，脚下炸开一朵金星，光柱慢慢变细消失（参考 r_skybeam、"
     "r_evolve_godlay、r_hit1、r_hit3）。**光柱竖直、从格子顶上一直到底**，敌人站在格子底部中间（不画人），**左右对称**，6 帧。",
     GO + " and " + PI,
     "A GOLDEN SKY BEAM striking a champion, 6 frames, " + LR + " (" + CHAMP + " at the bottom middle, not drawn): 1 a thin "
     "white line straight down from the top of the cell to the ground at the bottom middle; 2 the beam 6 squares wide, "
     "white core, gold edges, the full height; 3 the beam full and a gold star 18 squares across bursting on the ground at "
     "its foot, pink sparks; 4 the beam thinner, the star becoming a ring; 5 only a thin beam and motes; 6 fading motes.",
     row(6, 24, 60) + "; centered across, the beam's foot on the cell's bottom row."),
    # ---- W Rebuttal (the barrier: the main pack's every 25 s, the add-on's on an incoming projectile)
    ("w_on", "W 灵魂折镜：屏障（她身上，循环），4 帧", "view_buffs `league_mel_w_on`（跟随她，画在人物上面 z 3；左右对称；循环；大图表）",
     "60 × 64",
     "W 的屏障：一层**像镜子一样的金色护罩**罩住她：高高的蛋形外壳（只画边：2 格宽的淡金亮边），上面有几道直直的折线像镜面的切面，"
     "几处白色的反光一帧一帧移动（参考 shield、w_shieldmask28、w_reflect_color_ramp、w_impact_flare）。**她站在中间不画人，只画罩子的边、"
     "切面线和反光**，**左右对称**，4 帧循环。",
     GO,
     "A MIRROR-GOLD BARRIER round a mage, 4 frames, a loop, " + LR + " (" + HER + ", her body area left EMPTY): a tall "
     "egg-shaped shell outline round her, 56 squares wide and 62 tall, its bottom open at the ground, its rim 2 squares "
     "of pale gold with a white inner edge; a few straight facet lines across its upper part like the cuts of a mirror "
     "(mirrored left and right); white glints on the rim that move a few squares round it each frame.",
     row(4, 60, 64) + "; centered across, the shell's open bottom on the cell's bottom row."),
    # ---- the add-on (league_mel): Overwhelm's mark and its execute
    ("m_mark", "附加包：夺命残影（敌人头上，循环），4 帧", "view_buffs `league_mel_m_mark`（附加包；跟随目标，z 3；左右对称；循环）", "14 × 12",
     "附加包里带残影的敌人头上：一个小小的金色日蚀印记（金环、深色的芯），一明一暗地跳动（参考 basicattack_mark_mult、"
     "r_circle_normal）。**左右对称**，4 帧循环。",
     EC,
     "A SMALL ECLIPSE SIGIL over a head, 4 frames, a loop, " + LR + ": a gold ring 8 squares across, 2 squares thick, round "
     "a dark plum-black core, four tiny gold rays (up, down, left, right); 1 dim, 2 bright, 3 the brightest with a white "
     "glint on the rim, 4 dim again.",
     row(4, 14, 12) + CENTER),
    ("x_hit", "附加包：残影处决（敌人身上），6 帧", "view_effects `league_mel_x_hit`（附加包；跟随目标，z 2；左右对称；大图表）", "40 × 48",
     "附加包里残影够了直接处决：敌人身上的日蚀印记猛地一亮，炸成一大片金色碎片和粉红的火花，中间一道竖直的金光（参考 r_evolve_blast、"
     "z_backblast、r_hit1）。**被处决的人站在中间不画**，**左右对称**，6 帧。",
     EC + " and " + PI,
     "AN ECLIPSE EXECUTION BURST on a champion, 6 frames, " + LR + " (" + CHAMP + ", the body area left EMPTY in frames "
     "1-2): 1 an eclipse sigil (gold ring, dark core) 10 squares across at chest height; 2 the sigil flashing white, 16 "
     "across; 3 it bursts - gold shards (small triangles) flying out in a mirrored ring 36 across, a white vertical light "
     "14 squares tall at the middle, pink sparks; 4 the shards further out, smaller; 5 only shards and motes; 6 fading "
     "motes.",
     row(6, 40, 48) + "; centered across, the sigil's middle 26 squares above the cell's bottom row."),
]
BIG_FX = ["q_volley", "e_orb", "r_cast", "r_hit", "w_on", "x_hit"]
GROUPS = [
    ("a_bolt p_bolt a_hit p_hit", ["mel_base_basicattack_constellation_line", "mel_base_basicattack_wisps",
                                   "mel_base_basicattack_mark_mult", "mel_base_p_yellow_ray", "mel_base_p_flecks",
                                   "mel_base_w_impact_flare"]),
    ("p_3 p_6 p_9", ["mel_base_p_glowdust", "mel_base_packed_glows", "mel_base_basicattack_heath_swirl",
                     "mel_base_mist"]),
    ("q_volley q_hit", ["mel_base_q_flame_ring", "mel_base_r_airbullet", "mel_base_r_hit3", "mel_base_r_hit1"]),
    ("e_orb e_bound e_slow e_burn", ["e_tar_center", "e_tar_centerglowpattern", "e_scroll", "e_wall", "e_aoe_mult",
                                     "e_aoe_damagehotspot"]),
    ("r_cast r_hit", ["mel_r_centershine_tar", "mel_base_r_glow_01", "mel_base_r_s_05", "mel_base_r_skybeam",
                      "mel_base_r_evolve_godlay", "mel_base_r_zone_aoe_glow_1"]),
    ("w_on", ["mel_base_shield", "mel_base_w_shieldmask28", "mel_base_w_reflect_color_ramp_01_brighter",
              "mel_base_w_impact_flare", "mel_base_w_air_swoosh"]),
    ("m_mark x_hit", ["mel_base_basicattack_mark_mult", "mel_base_r_circle_normal", "mel_base_r_evolve_blast",
                      "mel_base_z_backblast"]),
]
SHOTS = [("attack", 3, "a_bolt：光弹从她伸出去的手上飞出；a_hit 在目标身上"),
         ("skill", 4, "q_volley：落在目标那一点（不在她身上）；p_3 在她腰两边"),
         ("skill2", 3, "e_orb：法球贴地朝前飞出；e_bound / e_slow / e_burn 在敌人身上"),
         ("ult", 3, "r_cast：她头顶上方的日蚀"), ("ult", 4, "r_hit：每个带残影的敌人身上（天降金光）"),
         ("idle", 1, "待机（大小参考）；w_on 罩住她")]


def configure():
    """pack_rammus_fx's sheets drawn from Mel's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "梅尔"


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    d = np.asarray(Image.open(RF.lp(os.path.join(ROOT, "assets", "source", "mel", "hd", "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (d.shape[1] * 4 + 32, d.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 流光镜影 梅尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/mel_idle.png`：3/4 正面朝右的诺克萨斯贵族女法师，深棕色皮肤、高高的黑色卷发髻、"
      f"金色额饰和大耳环，青绿色紧身连体衣、银白护甲，深红色长袍和喇叭袖、金色衬里，身后一条拖地的长袍）。她在游戏里是**高清**的（每个游戏格子里 "
      f"1.5×1.5 个细像素），{h} 格高、{w} 格宽（连拖尾）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/mel_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/mel_shots.png`：动作帧（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里梅尔自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，"
      "不要提交。颜色照英雄联盟原版：**她的魔法是耀眼的金色光**（白芯、金身），**带一点她长袍那种深红-粉红的火花和拖尾**；**大招鎏金蚀日是一轮"
      "金色的日蚀**（深色的圆盘、耀眼的金色日冕）；**W 是镜子一样的金色屏障**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了三张弹道图（a_bolt、p_bolt 头朝右；e_orb 本来就是圆的），其余**全部严格左右对称**（逐格对称：这些画面在红色方"
      "不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `mel_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/mel_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「灼灼之光」和 W「灵魂折镜」在里面） | 射出金色光弹；放技能后下次普攻多射 3 / 6 / 9 颗小光弹；每 25 秒第一次打中英雄时张开屏障 | "
      "`a_bolt` · `a_hit` · `p_bolt` · `p_hit` · `p_3` · `p_6` · `p_9` · `w_on` |")
    a("| 技能 1 = Q「耀光齐射」 | 一阵光弹落在目标那一点，连续爆炸 6 次 | `q_volley` · `q_hit` |")
    a("| 技能 2 = E「阳炎涡旋」 | 射出阳炎法球，中心禁锢、外圈减速并灼烧 | `e_orb` · `e_bound` · `e_slow` · `e_burn` |")
    a("| 大招「鎏金蚀日」 | 头顶升起日蚀，天降金光打所有带残影的敌人 | `r_cast` · `r_hit` |")
    a("| 附加包 | 夺命残影的印记、残影够了直接处决 | `m_mark` · `x_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、光环、光柱都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（日蚀中间的深色圆盘本身是深色，可以）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色光（光弹、光雨、法球、光柱、屏障、光球）", GOLD), ("深红-粉红的火花（拖尾、火花、点缀）", PINK),
                        ("日蚀（日冕和深色圆盘）", ECL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（光晕）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、她身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，Q 每次爆炸的半径 "
      "20000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `mel_fx_{name}.png`：{title}\n")
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
        a(f"| `mel_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_mel_fx`（小的）和 `league_mel_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_mel.py 的 views；w_on 绑在 buff `league_mel_w_on` 上，p_3 / p_6 / p_9 绑在同名 buff 上；附加包的反弹光弹 w_back 用 a_bolt 的帧）。")
    a("- 除了三张弹道图，全部断言左右对称；`e_slow` 画在人物下面（z -1），`q_volley`、`e_bound`、`m_mark`、`w_on` 在上面（z 3）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉给光描的最深色边（日蚀的深色圆盘保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。用户也可能用 Gemini 画好直接给图片（沃里克的做法：process_warwick_fx.py）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="mel_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "mel_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_mel.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "mel_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "mel_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "mel_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"mel_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "none (a projectile, turned by the game)" if x[0] in ("a_bolt", "p_bolt") else
                    "left-right"} for x in FX], f, ensure_ascii=False, indent=1)
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
