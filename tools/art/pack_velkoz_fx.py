#!/usr/bin/env python3
"""Build velkoz_fx_pack.zip: step 3 of Vel'Koz's sprite - Codex draws his effects (pack_zyra_fx.py's way,
pack_rammus_fx's sheets).

    python tools/lol/fx_ref_velkoz.py          # League's particle textures -> C:/t/vk_work/fxref (Riot's art, local only)
    python tools/art/pack_velkoz_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name velkoz_fx_redo_pack]

The pack (C:/t/vk_work/fx/velkoz_fx_pack, zipped into --out, default dist/velkoz_packs) holds PROMPTS.md (also written
to assets/source/velkoz/PROMPTS_FX.md), design/velkoz_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/velkoz_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/velkoz_shots.png (action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle
textures for Vel'Koz grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_velkoz.py): view_projectiles a_bolt, q_bolt (also q_bolt_f
and the add-on's q_split_bolt), w_rift (the rift line's picture), r_beam (the ray, cut into frames by
import_velkoz_fx.py from one long beam strip, league_lucian Q's standing beam); view_effects a_hit, q_hit, q_split,
q_split_hit, w_hit, e_mark, e_boom, e_hit, r_hit, p_s1, p_s2, p_full; view_buffs q_slow. League's colours: his void
energy (the bolts, the rift, the eruption's glow, the ray) is VIOLET-PURPLE with white-hot cores, his eye's plasma (Q)
MAGENTA, the passive's research mark a MAGENTA three-segment eye sign (League's p_eyecounter), the earth E throws up
dusty grey-brown. Red side: the client never mirrors an effect picture, so every hit, buff, mark and ground picture is
symmetric left to right; the projectiles and lines (a_bolt, q_bolt, w_rift, r_beam) are turned with their flight, so
they are drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/vk_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "velkoz", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_velkoz")
NAME = "velkoz_fx_pack"

VOID = "#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A"        # his void energy: bolts, rift, ray, eruption glow
PLASMA = "#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E"      # the eye's plasma (Q), the research mark
EARTH = "#E6DAC6, #B8A68A, #8A7860, #5E5040, #382E26"                # E's rocks and dust
VO = f"a violet-purple void ramp ({VOID})"
PL = f"a magenta plasma ramp ({PLASMA})"
EA = f"a dusty grey-brown earth ramp ({EARTH})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
UNIT = "a champion stands in the middle, not drawn: about 16 squares wide and 36 tall"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_bolt", "普攻：虚空能量弹（弹道，循环），4 帧", "view_projectiles `league_velkoz_a_bolt`（跟着弹道转向；上下对称）", "10 × 6",
     "从他的大眼睛射出的一小团紫色虚空能量：白色的芯，紫色的光，后面拖一小截紫色的尾巴（参考 ba_beam_bolts、ba_sparks、z_flare_purp）。"
     "**朝右飞、尾巴在左边，上下对称**，4 帧循环（光一闪一闪）。",
     VO,
     "A SMALL VOID BOLT, 4 frames, a seamless loop, " + TB + ": a round violet energy bolt 4 squares across with a white core "
     "1-2 squares, a tapering violet trail 5 squares long behind it on the left; each frame the core flickers and two tiny "
     "violet sparks shift along the trail.",
     row(4, 10, 6) + "; the bolt's middle on the cell's middle row, its head 1 square from the right edge."),
    ("a_hit", "普攻：打中目标，3 帧", "view_effects `league_velkoz_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "能量弹打中：一团紫色的光一闪，散成几点紫色的火星（参考 ba_sparks、z_sparks_grey）。**左右对称**，3 帧。",
     VO,
     "A SMALL VOID HIT, 3 frames, " + LR + ": 1 a white-violet flash 6 squares across; 2 a violet ring 9 squares across with "
     "4 sparks flying out diagonally; 3 only the fading sparks.",
     row(3, 12, 12) + CENTER),
    # ---- Q Plasma Fission
    ("q_bolt", "Q 等离子裂变：等离子弹（弹道，循环），4 帧", "view_projectiles `league_velkoz_q_bolt`（还有 q_bolt_f、附加包的 "
     "q_split_bolt；跟着弹道转向；上下对称）", "14 × 10",
     "从大眼睛射出的品红色等离子球：亮白的芯，品红色的球，外面一圈细细的紫色光环，后面一条闪着小星星的拖尾（参考 q_ball_mis、"
     "q_core_center_mis、q_core_ring_mis、q_smallstartrail）。**朝右飞、拖尾在左边，上下对称**，4 帧循环。",
     PL,
     "A MAGENTA PLASMA ORB, 4 frames, a seamless loop, " + TB + ": a round orb 6 squares across - a white core 2 squares, "
     "bright magenta round it, a thin violet-magenta ring just outside; a sparkling trail 7 squares long behind it on the "
     "left made of small magenta and white star sparks; each frame the ring pulses one square and the sparks shift.",
     row(4, 14, 10) + "; the orb's middle on the cell's middle row, its front 1 square from the right edge."),
    ("q_hit", "Q：等离子弹打中，5 帧", "view_effects `league_velkoz_q_hit`（跟随目标，画在人物上面 z 2；左右对称）", "20 × 20",
     "等离子球打中目标：品红色的等离子炸开，一圈亮环往外扩，中间白光（参考 q_splitexplosion、q_implode_circle、q_tar）。**左右对称**，5 帧。",
     PL,
     "A PLASMA BURST, 5 frames, " + LR + ": 1 a white flash 6 squares across with a magenta rim; 2 a bright magenta burst "
     "12 squares across, white in the middle; 3 a magenta ring 18 squares across, 2 squares thick, plasma droplets inside; "
     "4 the ring thinner and fainter, droplets falling; 5 only a few fading sparks.",
     row(5, 20, 20) + CENTER),
    ("q_split", "Q：命中点分裂（往上下两边射出两颗小等离子弹），6 帧",
     "view_effects `league_velkoz_q_split`（落点，不跟随，画在人物上面 z 2；左右对称、上下对称；大图表）", "16 × 46",
     "Q 打中东西的地方，等离子弹一分为二：命中点先亮一下，然后**两颗小一点的品红色等离子弹分别往正上方和正下方飞出去**，各拖一条星星尾巴，"
     "飞到格子的上下两头后散开（参考 q_splitexplosion、split_spark）。**左右对称，也上下对称**（上面那颗和下面那颗一模一样），6 帧。",
     PL,
     "A PLASMA BOLT SPLITTING IN TWO, 6 frames, " + LR + " and also SYMMETRIC TOP TO BOTTOM: 1 a white-magenta flash 8 "
     "squares across in the middle of the cell; 2 two small magenta orbs (4 squares across, white cores) leaving it, one "
     "going straight UP and one straight DOWN, 6 squares from the middle, a short sparkling trail behind each toward the "
     "middle; 3 the orbs 12 squares from the middle; 4 18 squares; 5 the orbs at the cell's top and bottom ends, fading; "
     "6 only fading sparks along the two paths.",
     row(6, 16, 46) + CENTER),
    ("q_split_hit", "Q：分裂弹打中，4 帧", "view_effects `league_velkoz_q_split_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 14",
     "分裂出来的小等离子弹打中：比 q_hit 小一号的品红色爆开（参考 q_tar）。**左右对称**，4 帧。",
     PL,
     "A SMALL PLASMA POP, 4 frames, " + LR + ": 1 a white flash 4 squares across; 2 a magenta burst 9 squares across; 3 a "
     "thin magenta ring 12 squares across; 4 fading sparks.",
     row(4, 14, 14) + CENTER),
    ("q_slow", "Q：减速（buff，目标脚下，循环），4 帧", "view_buffs `league_velkoz_q_slow`（跟随目标，画在人物下面 z -1；左右对称；循环）",
     "22 × 8",
     "被等离子减速的人脚下一圈品红色的黏稠等离子，冒着小泡（参考 q_tar、q_marker_glow）。**只画在脚下，不画人**，**左右对称**，4 帧循环。",
     PL,
     "A PLASMA SLOW UNDER A UNIT, 4 frames, a seamless loop, " + LR + " (" + UNIT + ", only its feet on the cell's bottom "
     "part): a flat magenta plasma ellipse on the ground (20 wide, 5 tall), a brighter rim, small bubbles rising 1-2 "
     "squares at mirrored places and popping; each frame different bubbles.",
     row(4, 22, 8) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
    # ---- W Void Rift (the attack's every third hit)
    ("w_rift", "W 虚空裂隙：一道裂隙（直线，从他往目标），10 帧",
     "view_projectiles `league_velkoz_w_rift`（LineRangeProjectile 的图，跟着方向转；画在线的正中间；上下对称；大图表）", "78 × 14",
     "他朝目标撕开一道 75 格长的虚空裂隙：先是地上一条锯齿形的紫色裂缝从左到右亮起来（第 1–3 帧），裂缝里透出白紫色的光（第 4–5 帧），"
     "然后整条裂缝**爆开**：白色的闪光，紫色的能量往上下两边喷（第 6–7 帧，这是第二段伤害），最后碎成紫色的火星散掉（第 8–10 帧）"
     "（参考 w_aoe_02、w_second_crack_tx_2、w_mis_groundtrench、w_missilehead_1、w_flash_hit）。整条裂隙**横着画、左右两头尖**，"
     "**上下对称**（游戏按方向转这张图），10 帧。",
     VO,
     "A VOID RIFT along the ground, 10 frames, " + TB.replace("flying RIGHT, the trail behind it on the LEFT, ", "lying "
     "ALONG the cell (left to right), ") + ": a long horizontal jagged crack 74 squares long, pointed at both ends: "
     "1 the crack's left third glowing violet, 1 square thick; 2 two thirds; 3 the whole crack, 2 squares thick, violet "
     "with a darker purple edge; 4 white light inside it, the crack 4 squares thick at its middle, tapering; 5 brighter, "
     "small violet sparks above and below at mirrored places; 6 it BURSTS: a white flash along the whole line, violet "
     "energy spraying 5 squares up and down; 7 the spray at its highest (6 squares), fading at the edges; 8 the crack "
     "breaking into violet fragments; 9 scattered sparks; 10 a few fading sparks.",
     row(10, 78, 14) + "; the crack's middle on the cell's middle row, its ends 2 squares from the cell's left and right."),
    ("w_hit", "W：裂隙打中，3 帧", "view_effects `league_velkoz_w_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 14",
     "裂隙伤到的人身上：紫色的能量碎片往上溅（参考 w_flash_hit）。**左右对称**，3 帧。",
     VO,
     "A RIFT HIT, 3 frames, " + LR + ": 1 a violet-white flash 6 squares across low in the cell; 2 violet shards spraying "
     "up and out in a V, 12 squares tall; 3 only fading sparks.",
     row(3, 14, 14) + CENTER),
    # ---- E Tectonic Disruption
    ("e_mark", "E 构造分解：地面裂开（预警，落点），6 帧",
     "view_effects `league_velkoz_e_mark`（落点，不跟随，画在人物下面 z -1；左右对称；大图表）", "48 × 18",
     "E 的落点地面先裂开：一个紫色发光的椭圆圈，圈里地面裂开一道道紫色的裂缝，越来越亮（约 0.55 秒后爆开）"
     "（参考 e_aoe、e_cracks、e_nova_ground、e_tar_darkground）。**只画在地面上**，**左右对称**，6 帧。",
     VO,
     "A GROUND TELEGRAPH, 6 frames, " + LR + ": a flat ellipse on the ground 44 wide and 15 tall: 1 a thin violet ellipse "
     "outline and a dark purple patch inside; 2 four short glowing violet cracks inside, from the middle outward, mirrored; "
     "3 the cracks longer, branching; 4 the cracks reaching the rim, the rim brighter; 5 the cracks white-violet, small dust "
     "specks lifting; 6 the brightest: the whole ellipse glowing, the cracks white.",
     row(6, 48, 18) + "; centered across and down."),
    ("e_boom", "E：地面爆开（落点），7 帧", "view_effects `league_velkoz_e_boom`（落点，不跟随，画在人物上面 z 2；左右对称；大图表）",
     "48 × 52",
     "落点爆开：地面炸起一堆碎石和尘土，中间一道紫色的虚空能量柱往上冲，碎石往两边飞（被击飞的人会飞起来）（参考 e_impactspike、"
     "e_firewall1、e_puffs、crater_01、e_lightning03）。**左右对称**（碎石也对称），7 帧，**底边是地面**。",
     VO + " and " + EA,
     "AN ERUPTION from the ground, 7 frames, " + LR + ": 1 a white-violet flash on the ground, an ellipse 30 wide and 8 "
     "tall; 2 a column of violet void energy shooting up from it, 12 squares wide and 30 tall, white in the middle, chunks "
     "of grey-brown rock (2-4 squares each, with dark edges) thrown up and out at mirrored places; 3 the column 44 tall, the "
     "rocks higher and wider apart, dust puffs at the ground on both sides; 4 the column breaking into violet flames at "
     "the top, the rocks at their highest; 5 the rocks falling, the energy fading to violet wisps; 6 dust settling, a "
     "few rocks on the ground; 7 faint dust.",
     row(7, 48, 52) + "; centered across, the ground ellipse's middle 4 squares above the cell's bottom row."),
    ("e_hit", "E：被炸中，3 帧", "view_effects `league_velkoz_e_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 14",
     "被炸飞的人身上：碎石和紫光一闪（参考 e_puffs）。**左右对称**，3 帧。",
     VO + " and " + EA,
     "A ROCK-AND-VOID HIT, 3 frames, " + LR + ": 1 a violet flash 6 squares across; 2 four small grey-brown rocks flying "
     "out diagonally with violet sparks; 3 fading sparks and dust.",
     row(3, 14, 14) + CENTER),
    # ---- R Life Form Disintegration Ray
    ("r_beam", "R 生命形态瓦解射线：射线（一整条，Claude 切成每一帧），4 帧",
     "view_projectiles `league_velkoz_r_beam`（Claude 把每帧切成从他眼睛射出的固定射线：league_lucian Q 的做法；上下对称；大图表）",
     "130 × 13",
     "大招的射线：从他的大眼睛射向前方的一整条光束，**长 128 格**：白色的芯（2 格），外面紫色，再外面一层淡淡的品红色光边，光束里有扭动的"
     "白紫色能量丝；**左端是一个圆形的亮光（眼睛处的发射点，9 格）**，右端渐渐变细、散开（参考 r_beam_middle、r_beamcore_02、r_energy、"
     "r_lightning、r_sides、r_end_line）。**横着画、上下对称**，4 帧循环（能量丝流动、光一闪一闪）。",
     VO,
     "A LONG DISINTEGRATION RAY, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the "
     "game turns the picture with its direction): a straight horizontal beam 128 squares long from a round white-violet "
     "flare 9 squares across at the LEFT end (where it leaves the eye); the beam 9 squares thick near the flare and 7 along "
     "its length - a white core 2 squares, violet round it, a thin pale magenta outer glow; twisting white-violet energy "
     "threads running along it; the RIGHT end thinning to 3 squares and breaking into violet sparks over its last 10 squares; "
     "each frame the threads move to the right and the flare pulses.",
     row(4, 130, 13) + "; the beam on the cell's middle row, the flare's middle 6 squares from the left edge."),
    ("r_hit", "R：射线灼烧（目标身上），4 帧", "view_effects `league_velkoz_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 16",
     "射线照到的人身上：紫色的能量灼烧，一团紫白色的火焰往上窜，几点火星（参考 r_hitbubble、r_impactfire、r_obscsparks）。"
     "**左右对称**，4 帧。",
     VO,
     "A RAY BURN on a target, 4 frames, " + LR + ": 1 a white-violet flash 6 squares across; 2 violet flames 10 squares "
     "wide licking up 12 squares, white at their base; 3 the flames higher and thinner, sparks rising; 4 fading wisps.",
     row(4, 14, 16) + CENTER),
    # ---- passive Organic Deconstruction
    ("p_s1", "被动 有机体解构：1 层（目标头上），4 帧", "view_effects `league_velkoz_p_s1`（跟随目标，画在人物上面 z 3；左右对称）",
     "13 × 11",
     "被技能打中的英雄头上出现维克兹的研究标记：一个**倒三角形、分成三瓣的品红色眼睛符号**（英雄联盟的 p_eyecounter），**亮了一瓣**"
     "（**下面正中那瓣**白色发亮，上面两瓣暗紫色）（参考 p_eyecounter_1、p_eyecounter_2、p_eyecounter_3glow、p_researchcounter_ring）。"
     "**左右对称**，4 帧：出现、停住、停住、变淡。",
     PL,
     "A RESEARCH MARK with 1 of 3 segments lit, 4 frames, " + LR + ": an inverted triangle sign 11 squares wide and 9 tall "
     "split into three petal segments (upper-left, upper-right, bottom middle) round a small dark centre; the BOTTOM MIDDLE "
     "segment lit white with a magenta rim, the two upper ones dark purple with a magenta edge; 1 it pops in a square "
     "smaller; 2 full size; 3 full size, the lit segment glowing; 4 fading.",
     row(4, 13, 11) + CENTER),
    ("p_s2", "被动：2 层（目标头上），4 帧", "view_effects `league_velkoz_p_s2`（跟随目标，画在人物上面 z 3；左右对称）", "13 × 11",
     "同一个标记，**亮了两瓣**（上面左右两瓣白色发亮，下面正中那瓣暗紫色）。**左右对称**，4 帧：出现、停住、停住、变淡。",
     PL,
     "THE SAME RESEARCH MARK with 2 of 3 segments lit, 4 frames, " + LR + ": the inverted triangle sign 11 squares wide "
     "and 9 tall, its two upper segments lit white with magenta rims, the bottom segment dark purple with a magenta edge; "
     "1 it pops in a square smaller; 2 full size; 3 full size, glowing; 4 fading.",
     row(4, 13, 11) + CENTER),
    ("p_full", "被动：3 层引爆真实伤害（目标身上），6 帧", "view_effects `league_velkoz_p_full`（跟随目标，画在人物上面 z 3；左右对称）",
     "28 × 28",
     "第 3 层：标记三瓣全亮、一闪，然后**爆开成一圈白色和品红色的几何碎片**，像被分解成碎块一样往外飞（参考 p_eyecounter_3glow、"
     "p_hit_slice、shards）。**左右对称**，6 帧。",
     PL,
     "A DECONSTRUCTION BURST, 6 frames, " + LR + ": 1 the inverted triangle sign (11 wide, 9 tall) with ALL THREE segments "
     "lit white, a magenta glow round it; 2 the sign flashing bigger (15 wide), white; 3 it shatters: angular white and "
     "magenta shards (triangles and slivers, 2-3 squares each) flying outward in a ring 20 squares across; 4 the shards "
     "26 squares apart, a thin magenta ring between them; 5 the shards smaller and fading; 6 a few fading specks.",
     row(6, 28, 28) + CENTER),
]
BIG_FX = ["q_split", "w_rift", "e_mark", "e_boom", "r_beam"]
FLYING = ["a_bolt", "q_bolt", "w_rift", "r_beam"]
GROUPS = [
    ("a_bolt a_hit", ["velkoz_base_ba_beam_bolts", "velkoz_base_ba_beam_glow", "velkoz_base_ba_sparks_rgba",
                      "velkoz_base_z_flare_purp"]),
    ("q_bolt q_hit q_split q_slow", ["velkoz_base_q_ball_mis_rgba", "velkoz_base_q_core_center_mis", "velkoz_base_q_core_ring_mis",
                                     "velkoz_base_q_splitexplosion", "velkoz_base_split_spark", "velkoz_base_q_tar"]),
    ("w_rift w_hit", ["velkoz_base_w_aoe_02", "velkoz_base_w_second_crack_tx_2", "velkoz_base_w_mis_groundtrench",
                      "velkoz_base_w_missilehead_1", "velkoz_base_w_flash_hit"]),
    ("e_mark e_boom e_hit", ["velkoz_base_e_aoe", "velkoz_base_e_cracks", "velkoz_base_e_nova_ground",
                             "velkoz_base_e_impactspike", "velkoz_base_e_firewall1", "velkoz_base_crater_01"]),
    ("r_beam r_hit", ["velkoz_base_r_beam_middle", "velkoz_base_r_beamcore_02", "velkoz_base_r_energy_01",
                      "velkoz_base_r_lightning", "velkoz_base_r_hitbubble", "velkoz_base_r_impactfire"]),
    ("p_s1 p_s2 p_full", ["velkoz_base_p_eyecounter_1", "velkoz_base_p_eyecounter_2", "velkoz_base_p_eyecounter_3glow",
                          "velkoz_base_p_researchcounter_ring", "velkoz_base_p_hit_slice_rgba", "shards"]),
]
SHOTS = [("attack", 3, "a_bolt：从大眼睛射出（a_hit 在目标身上）"), ("skill", 3, "q_bolt：从大眼睛射出；q_split 在打中的地方"),
         ("skill2", 3, "e_mark / e_boom：在目标点（不在他身上）"), ("ult_loop", 1, "r_beam：从大眼睛射向前方 128 格"),
         ("idle", 1, "待机（大小参考）")]


def configure():
    """pack_rammus_fx's sheets drawn from Vel'Koz's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "维克兹"


def design_sheet(path):
    """His idle at 4x, the design's own squares (PPU 1.5)."""
    d = np.asarray(Image.open(RF.lp(os.path.join(ROOT, "assets", "source", "velkoz", "hd", "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (d.shape[1] * 4 + 32, d.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 虚空之眼 维克兹：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/velkoz_idle.png`：3/4 正面朝右、飘在空中的虚空之眼——卡其金色的甲壳、"
      f"正中一只发光的品红色大眼睛和上面三只小眼睛，三条深青黑色、尖端品红的触手）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个"
      f"细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/velkoz_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/velkoz_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里维克兹自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**他的虚空能量（普攻、裂隙、射线、E 的能量柱）是紫色的、芯是白的**，**大眼睛射出的等离子"
      "（Q）是品红色的**，**被动的研究标记是品红色的三瓣眼睛符号**，**E 炸起的碎石是灰褐色的**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **光、能量、火焰、光环、冲击波都没有黑描边**；**碎石**有 1 格暗边。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、地上、头上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道和线**（普攻的能量弹、"
      "Q 的等离子弹、W 的裂隙、R 的射线）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `velkoz_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/velkoz_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（W「虚空裂隙」和被动在里面） | 从大眼睛发射虚空能量；每第 3 下朝目标撕开一道裂隙，裂隙随后爆开 | `a_bolt` · `a_hit` · "
      "`w_rift` · `w_hit` |")
    a("| 技能 1 = Q「等离子裂变」 | 发射等离子弹，打中减速并在命中点分裂成往两边飞的两颗 | `q_bolt` · `q_hit` · `q_split` · "
      "`q_split_hit` · `q_slow` |")
    a("| 技能 2 = E「构造分解」 | 目标区域地面裂开，随后爆开把敌人击飞 | `e_mark` · `e_boom` · `e_hit` |")
    a("| 大招「生命形态瓦解射线」 | 从大眼睛射出一道射线引导 2.5 秒，跟着目标烧 | `r_beam` · `r_hit` |")
    a("| 被动「有机体解构」 | 技能打中英雄叠层：头上的研究标记亮 1、2 瓣，第 3 层爆开造成真实伤害 | `p_s1` · `p_s2` · `p_full` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火焰、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（碎石可以有 1 格暗边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("紫色的虚空能量（普攻、裂隙、射线、能量柱）", VOID), ("品红色的等离子（Q、研究标记）", PLASMA),
                        ("灰褐色的碎石和尘土（E）", EARTH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（预警圈、减速的等离子）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 55000，裂隙长 75000，"
      "E 的半径 22000，射线长 120000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `velkoz_fx_{name}.png`：{title}\n")
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
        a(f"| `velkoz_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_velkoz_fx`（小的）和 `league_velkoz_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_velkoz.py 的 views；q_bolt_f 和附加包的 q_split_bolt 用 q_bolt 的 tag）。")
    a(f"- 弹道和线（{'、'.join(FLYING)}）断言上下对称，q_split 两个方向都对称，其余断言左右对称；q_split、e_mark、e_boom 不跟随（落点）。")
    a("- 时间：a_bolt 前 2 帧空（弹从他身体中间出来，先藏住穿过眼睛的那一段，league_malzahar 的做法）；w_rift 的爆开帧落在 w_det（19 tick），"
      "整条画面 w_life（34 tick）；e_mark 拉长到 e_delay（33 tick），e_boom 接在后面；r_beam 每一波 r_p（15 tick）一帧一 tick：从 4 帧的光束"
      "里取，每帧往回挪 1 像素（弹道每 tick 往前 1 像素），光束左端一直在他的眼睛上（弹道从他的站位点出发，眼睛在前面 8 像素）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（碎石的暗边保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="velkoz_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "velkoz_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_velkoz.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "velkoz_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "velkoz_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "velkoz_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"velkoz_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": ("top-bottom" if x[0] in FLYING else "left-right and top-bottom" if x[0] == "q_split"
                                 else "left-right")} for x in FX], f, ensure_ascii=False, indent=1)
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
