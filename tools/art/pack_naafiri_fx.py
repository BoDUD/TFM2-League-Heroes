#!/usr/bin/env python3
"""Build naafiri_fx_pack.zip: step 3 of Naafiri's sprite - Codex (or Gemini) draws her effects (pack_shyvana_fx.py's way).

    python tools/lol/fx_ref_naafiri.py         # League's particle textures -> C:/t/nf_work/fxref (Riot's art, local only)
    python tools/art/pack_naafiri_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name naafiri_fx_redo_pack]

The pack (C:/t/nf_work/fx/naafiri_fx_pack, zipped into --out, default dist/naafiri_packs) holds PROMPTS.md (also written
to assets/source/naafiri/PROMPTS_FX.md), design/naafiri_designs.png (her and a packmate at 4x, the designs' squares at
PPU 1.5), design/naafiri_size.png (both at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/lol_fx_ref.png (League's own particle textures for Naafiri, grouped by the effect they inform).
Her frames are not rigged yet (Codex's key poses come first), so the pack has no action shots: every effect says where
it plays from her design.
The effects are the views the kit binds (tools/kit/build_naafiri.py): view_projectiles q_dagger, q2_dagger, q_leap;
view_effects a_hit, pk_bite, pk_bite4, pk_leap, pk_ride, q_hit, q_bleed, q2_hit, q_heal, e_slash, e_slash2, e_hit,
r_roar, r_hit, r_reset; view_buffs pack_aura (league_naafiri_pack4), r_shred, r_shield. League's colours: her darkin
power is CRIMSON with white-hot cores and DARK VIOLET shadows, mint-green glints on the blades' edges; the daggers bone
and steel; the heal crimson-gold. Red side: the client never mirrors an effect picture, so every hit, buff, ground and
body picture is symmetric left to right; the projectiles are turned with their flight, so they are drawn flying right
and symmetric top to bottom (a dagger spinning as a disc reads the same both ways).
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

TMP = "C:/t/nf_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "naafiri", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "naafiri", "hd")
NAME = "naafiri_fx_pack"
PPU = 1.5

CRIMSON = "#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C"   # her darkin power: white core to deep crimson
VIOLET = "#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650"             # the darkin shadow: the roar, the aura
MINT = "#F0FFF8, #A8F2D0, #56CFA0, #2E8E70"                        # the blades' glint (accents only)
BONE = "#FFF8E8, #EEDCB4, #C8AC80, #8E7250, #5A4632"               # the daggers' bone hilt (solid: outlined)
STEEL = "#FFFFFF, #DDE6EE, #A8B6C4, #6E7C8C, #3E4652"              # the daggers' blade (solid: outlined)
HEAL = "#FFFFFF, #FFE8C8, #FFB070, #F06A4A, #B8303A"               # her heal: crimson-gold motes
PACK = "#FF5A5A, #D8243A, #A01428, #640C1A, #A8B4C4, #6E7C8C, #3E4652, #FFE070, #0E0A12"   # a packmate (solid)
CR = f"a crimson darkin-power ramp ({CRIMSON})"
VI = f"a dark violet shadow ramp ({VIOLET})"
MI = f"mint-green glints ({MINT}) as accents only"
BO = f"a bone ramp ({BONE})"
ST = f"a steel ramp ({STEEL})"
HE = f"a crimson-gold heal ramp ({HEAL})"
PK = f"the packmate's own colours ({PACK}: crimson body, slate-grey helmet and blade, a yellow eye, a near-black outline)"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
HER = "she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs"
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
SOLID = ("SOLID OBJECTS (the daggers, the packmates) have a 1-square near-black outline; light, blood, slashes and "
         "shockwaves have none")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack and the passive
    ("a_hit", "普攻：撕咬打中目标，3 帧", "view_effects `league_naafiri_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "狼牙咬中：上下两排白色尖牙合拢的一闪，中间迸出深红色的血光（参考 naafiri_base_ba_fangs01、foundation_impactspike）。**左右对称**，3 帧。",
     CR,
     "A BITE HIT, 3 frames, " + LR + ": 1 two rows of white fangs (an upper and a lower arc, 5 fangs each) snapping "
     "together with a crimson flash between them; 2 the fangs closed, a crimson burst of 6 short spikes flying out; "
     "3 only the fading crimson specks.",
     row(3, 12, 12) + CENTER),
    ("pk_bite", "被动 狂烈种群：狗群的一口（两只），3 帧", "view_effects `league_naafiri_pk_bite`（跟随目标，z 2；左右对称）", "10 × 10",
     "狗群在目标身上咬一口：两侧各一道小小的咬痕（三颗牙），一闪深红（比普攻小、暗一些）。**左右对称**，3 帧。",
     CR,
     "A SMALL PACK BITE, 3 frames, " + LR + ": 1 two small bite marks (three white fangs each) snapping in from the left "
     "and the right sides; 2 a small crimson splash between them; 3 fading crimson specks. Smaller and darker than the "
     "leader's bite.",
     row(3, 10, 10) + CENTER),
    ("pk_bite4", "暴吼时狗群的一口（四只），3 帧", "view_effects `league_naafiri_pk_bite4`（跟随目标，z 2；左右对称）", "16 × 14",
     "暴吼期间狗群翻倍：四道咬痕从四个方向咬上去，深红加一点暗紫。**左右对称**，3 帧。",
     CR + ", " + VI,
     "A BIG PACK BITE, 3 frames, " + LR + ": 1 four bite marks (three white fangs each) snapping in from the upper left, "
     "the upper right, the lower left and the lower right; 2 a crimson splash in the middle with dark violet wisps; "
     "3 fading crimson and violet specks.",
     row(3, 16, 14) + CENTER),
    ("pk_leap", "Q 命中后狗群扑上去，4 帧", "view_effects `league_naafiri_pk_leap`（跟随目标，z 2；左右对称）", "16 × 12",
     "Q 的匕首命中英雄、狗群扑上去的那一下：目标身上从两侧冲来两道深红色的残影（像两只狗扑来的速度线），撞在一起一闪。**左右对称**，4 帧。",
     CR,
     "A PACK POUNCE, 4 frames, " + LR + ": 1 two short crimson speed streaks coming in low from the left and the right "
     "edges; 2 the streaks halfway, bending up toward the middle; 3 they meet in a crimson flash; 4 fading specks.",
     row(4, 16, 12) + CENTER),
    ("pk_ride", "狗群扑在目标身上撕咬（循环），4 帧", "view_effects `league_naafiri_pk_ride`（跟随目标，z -1；左右对称）", "40 × 20",
     "Q 命中的英雄身上：**两只小伙伴**（照 `design/naafiri_designs.png` 右边的伙伴，缩到 14 格长左右）一左一右扑在目标脚边撕咬——"
     "左边那只朝右、右边那只朝左（互为镜像），头一下一下往中间咬。**中间目标的身体位置留空**，**左右对称**，4 帧循环。",
     PK + ", " + CR,
     "TWO SMALL HOUNDS MAULING, 4 frames, a seamless loop, " + LR + ": two small crimson hounds with slate-grey bony "
     "helmets (each about 14 squares long and 8 tall) at the bottom left and the bottom right, the left one facing "
     "RIGHT and the right one facing LEFT (mirror images), both biting toward the middle: 1 heads drawn back; 2 heads "
     "lunging in, jaws open; 3 jaws closed with a small crimson splash at each; 4 heads drawing back. " + SOLID + ".",
     row(4, 40, 20) + "; the hounds' paws on the cell's bottom row; " + TARGET + " (only its lower 20 squares are in "
     "the cell)."),
    # ---- Q Darkin Daggers
    ("q_dagger", "Q 暗裔犬牙：飞出去的匕首，4 帧", "view_projectiles `league_naafiri_q_dagger`（随飞行方向转；上下对称）", "10 × 6",
     "旋转飞出的暗裔匕首：骨柄加弯刃，转成一个圆盘，后面拖一小道深红残光（参考 naafiri_base_q_missile01、foundation_missile）。"
     "**朝右飞、上下对称**，4 帧（转一圈）。",
     ST + ", " + BO + ", " + CR,
     "A SPINNING DARKIN DAGGER, 4 frames, " + TB + ": a curved steel blade with a bone hilt spinning end over end so "
     "it reads as a disc 5 squares across (the blade's glint at a different place each frame), a short crimson streak "
     "trailing 4 squares behind it. " + SOLID + ".",
     row(4, 10, 6) + CENTER),
    ("q2_dagger", "Q 第二把匕首（更大、更红），4 帧", "view_projectiles `league_naafiri_q2_dagger`（随飞行方向转；上下对称）", "12 × 8",
     "第二把匕首：比第一把大一圈，刃上裹着一层深红色的光，拖的残光更长。**朝右飞、上下对称**，4 帧。",
     ST + ", " + BO + ", " + CR,
     "A SECOND, BIGGER DAGGER, 4 frames, " + TB + ": like a spinning darkin dagger but 7 squares across, its blade "
     "wrapped in a crimson glow, a crimson streak trailing 5 squares behind it. " + SOLID + ".",
     row(4, 12, 8) + CENTER),
    ("q_leap", "狗群扑向目标的速度线，3 帧", "view_projectiles `league_naafiri_q_leap`（随飞行方向转；上下对称）", "16 × 5",
     "跟着匕首扑向目标的狗群，只画成一道贴地的深红色速度线（参考 naafiripackmate_speedboostline）。**朝右飞、上下对称**，3 帧。",
     CR,
     "A PACK SPEED STREAK, 3 frames, " + TB + ": three thin crimson streaks, the middle one longest (14 squares), "
     "pointed at the right end, fading to the left; each frame they flicker.",
     row(3, 16, 5) + CENTER),
    ("q_hit", "Q 第一把匕首打中，3 帧", "view_effects `league_naafiri_q_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "匕首扎中：一道深红色的十字刺光，带几滴血珠飞散。**左右对称**，3 帧。",
     CR,
     "A DAGGER HIT, 3 frames, " + LR + ": 1 a crimson four-pointed star flash 7 squares across with a white core; "
     "2 the star breaking up, 5 crimson drops flying out; 3 only falling drops.",
     row(3, 12, 12) + CENTER),
    ("q_bleed", "Q 流血（每次跳伤害时播），3 帧", "view_effects `league_naafiri_q_bleed`（跟随目标，z 2；左右对称）", "10 × 14",
     "流血跳一下：目标身上冒出几滴深红色的血珠往下滴。**左右对称**，3 帧。",
     CR,
     "A BLEED TICK, 3 frames, " + LR + ": 1 three crimson drops appearing at the top; 2 the drops falling with short "
     "trails; 3 fading drops at the bottom.",
     row(3, 10, 14) + CENTER),
    ("q2_hit", "Q 第二把匕首打中（更大），4 帧", "view_effects `league_naafiri_q2_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "第二把匕首扎中：更大的深红色爆开，中间一道交叉的刃光，外圈一圈暗紫色碎片。**左右对称**，4 帧。",
     CR + ", " + VI,
     "A HEAVY DAGGER HIT, 4 frames, " + LR + ": 1 an X of two crimson blade streaks 12 squares across with a white "
     "core; 2 a crimson burst with dark violet shards flying out; 3 the shards farther, the burst fading; 4 last specks.",
     row(4, 16, 16) + CENTER),
    ("q_heal", "第二把匕首命中英雄时回血，4 帧", "view_effects `league_naafiri_q_heal`（她身上，z 3；左右对称）", "30 × 22",
     "她回血：身边升起几点深红带金的光点（不是绿色），往上飘。**中间她的身体位置留空**，**左右对称**，4 帧。",
     HE,
     "A HEAL, 4 frames, " + LR + ": small crimson-gold light motes (2-3 squares, white cores) rising at both sides of a "
     "low body and above it, a few plus-shaped glints; the middle EMPTY where the body is.",
     row(4, 30, 22) + "; " + HER + " (its middle part)."),
    # ---- E Eviscerate
    ("e_slash", "E 剔骨本能：周围第一圈撕裂，4 帧", "view_effects `league_naafiri_e_slash`（她身上，z -1；左右对称）", "56 × 26",
     "落地后在身边转圈撕裂：一圈深红色的爪痕弧线绕着她（地面上的椭圆，前后都有），刃尖带一点薄荷绿的闪光。"
     "**中间她的身体位置留空**，**左右对称**，4 帧：起、最亮、散开、余痕。",
     CR + ", " + MI,
     "A CIRCLE OF CLAW SLASHES, 4 frames, " + LR + ": four curved crimson slash arcs sweeping round a flat ground "
     "ellipse 50 squares wide and 16 tall (two at the front, two at the back), white at their leading edges, a few mint "
     "glints at the tips; 1 the arcs half drawn; 2 full and brightest; 3 breaking into crimson shreds; 4 fading shreds.",
     row(4, 56, 26) + "; the ellipse's middle on the cell's middle, 4 squares above the bottom; " + HER + "."),
    ("e_slash2", "E 第二圈撕裂（更大），4 帧", "view_effects `league_naafiri_e_slash2`（她身上，z -1；左右对称）", "64 × 30",
     "第二下撕裂：更大一圈，深红加暗紫，碎片飞得更远。**中间留空**，**左右对称**，4 帧。",
     CR + ", " + VI + ", " + MI,
     "A WIDER CIRCLE OF CLAW SLASHES, 4 frames, " + LR + ": like the first but on an ellipse 58 squares wide and 18 "
     "tall, crimson arcs with dark violet edges, shreds flying farther out; 1 half drawn; 2 brightest; 3 breaking; "
     "4 fading.",
     row(4, 64, 30) + "; the ellipse's middle on the cell's middle, 4 squares above the bottom; " + HER + "."),
    ("e_hit", "E 打中的敌人，3 帧", "view_effects `league_naafiri_e_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "被撕裂打中：两道交叉的深红爪痕。**左右对称**，3 帧。",
     CR,
     "A CLAW HIT, 3 frames, " + LR + ": 1 two crossing crimson claw streaks (an X, 9 squares) with a white core; 2 the "
     "streaks fading, 4 specks flying out; 3 fading specks.",
     row(3, 12, 12) + CENTER),
    # ---- ult: the roar and the pounce
    ("r_roar", "大招起手 暴吼：怒吼的冲击波，5 帧", "view_effects `league_naafiri_r_roar`（她身上，z 3；左右对称）", "64 × 40",
     "她仰天一吼：从她头部的位置往外扩散两圈暗紫色加深红的音波弧（像吼声的冲击波），地上一圈暗紫色的光环，几点深红的火星往上飞"
     "（参考 naafiri_base_r_flash_sharp、r_cas_outline、r_eyes01）。**中间她的身体位置留空**，**左右对称**，5 帧。",
     VI + ", " + CR,
     "A ROAR SHOCKWAVE, 5 frames, " + LR + ": 1 a small dark violet flash above the middle (where her raised head is); "
     "2 two wide sound-wave arcs (crimson inner, violet outer) spreading out to both sides, a violet ring on the ground "
     "round her; 3 the arcs at the cell's sides, the ground ring widest; 4 the arcs breaking up, crimson sparks rising; "
     "5 last sparks. The middle EMPTY where the body is.",
     row(5, 64, 40) + "; " + HER + " (its paws on the cell's bottom row)."),
    ("r_hit", "大招 猎狗血性：扑中目标，4 帧", "view_effects `league_naafiri_r_hit`（跟随目标，z 2；左右对称）", "22 × 20",
     "扑中英雄：一大口深红色的獠牙咬合（上下两排大牙），外圈暗紫色的冲击，迸出血光（参考 naafiri_base_r_tar_alpha1）。**左右对称**，4 帧。",
     CR + ", " + VI,
     "A POUNCE HIT, 4 frames, " + LR + ": 1 two big rows of white fangs (8 fangs each, upper and lower arcs 18 squares "
     "wide) snapping shut; 2 a crimson burst between them, a dark violet ring flashing out; 3 the fangs gone, crimson "
     "spikes and violet shards flying out; 4 fading specks.",
     row(4, 22, 20) + CENTER),
    ("r_reset", "参与击杀、可以再扑一次，4 帧", "view_effects `league_naafiri_r_reset`（她身上，z 3；左右对称）", "24 × 20",
     "参与击杀后大招刷新：她头顶上方亮起一对发光的深红色狼眼（参考 naafiri_base_r_eyes01），一闪后化成火星。**左右对称**，4 帧。",
     CR + ", " + VI,
     "A PAIR OF GLOWING EYES, 4 frames, " + LR + ": 1 two slanted crimson eyes (each 5 squares wide, white cores) "
     "flaring open in a dark violet haze high above the middle; 2 brightest; 3 narrowing; 4 breaking into rising "
     "crimson sparks.",
     row(4, 24, 20) + "; the eyes in the cell's upper half; " + HER + " below (only her top is in the cell)."),
    # ---- buffs
    ("pack_aura", "暴吼期间（循环），4 帧", "view_buffs `league_naafiri_pack4`（tag pack_aura；跟着她，循环，z -1；左右对称）",
     "60 × 18",
     "暴吼的 5 秒：她脚下一圈暗紫色的光环，边上几缕深红色的雾气往上飘（狗群翻倍的气势）。**中间留空**，**左右对称**，4 帧循环。",
     VI + ", " + CR,
     "A PACK AURA, 4 frames, a seamless loop, " + LR + ": a flat dark violet ground ellipse 54 squares wide and 10 "
     "tall round her paws (only its rim lit), a few crimson wisps rising from the rim at both sides, flickering in turn; "
     "the middle EMPTY.",
     row(4, 60, 18) + "; the ellipse's middle on the cell's middle; " + HER + " (only her paws reach the cell)."),
    ("r_shred", "大招减护甲（循环），4 帧", "view_buffs `league_naafiri_r_shred`（跟着目标，循环，z 3；左右对称）", "14 × 10",
     "被扑中的英雄护甲被撕开：头顶一块裂开的暗红色小盾，裂缝一闪一闪。**左右对称**，4 帧循环。",
     CR + ", " + ST,
     "A SHREDDED ARMOUR MARK, 4 frames, a seamless loop, " + LR + ": a small steel shield icon 8 squares tall with a "
     "crimson claw rent down its middle (three slashes), the rent glowing brighter and dimmer in turn. " + SOLID + ".",
     row(4, 14, 10) + CENTER),
    ("r_shield", "再扑一次时的护盾（循环），4 帧", "view_buffs `league_naafiri_r_shield`（跟着她，循环，z 3；左右对称）", "58 × 36",
     "第二次扑出带的护盾：罩住她的一层深红色半透明感的光膜（像素画里用一圈亮边加稀疏的内纹表现，不要整片涂满），边缘几处薄荷绿的闪光。"
     "**中间她的身体位置留空**（只画外圈和稀疏纹），**左右对称**，4 帧循环。",
     CR + ", " + MI,
     "A SHIELD BUBBLE, 4 frames, a seamless loop, " + LR + ": a dome-shaped crimson outline round a low body (54 squares "
     "wide, 32 tall, its bottom on the cell's bottom), a 1-square bright rim with a white highlight at the top, a few "
     "sparse crimson streaks inside the rim (never filled), mint glints moving round the rim; the middle EMPTY.",
     row(4, 58, 36) + "; " + HER + " (its paws on the cell's bottom row)."),
]
BIG_FX = ["pk_bite4", "pk_ride", "e_slash", "e_slash2", "r_roar", "pack_aura", "r_shield"]
FLYING = ["q_dagger", "q2_dagger", "q_leap"]

GROUPS = [
    ("a_hit / pk_bite / r_hit", ["naafiri_base_ba_fangs01", "naafiri_base_foundation_impactspike_2x2",
                                 "naafiri_base_foundation_impactspike_2x2_dissolve", "naafiri_base_r_tar_alpha1"]),
    ("q_dagger / q2_dagger / q_leap", ["naafiri_base_q_missile01", "naafiri_base_foundation_missile01",
                                       "naafiri_base_foundation_missile02", "naafiri_base_foundation_missile03",
                                       "naafiripackmate_speedboostline"]),
    ("q_hit / q_bleed / q_heal", ["naafiri_base_q_alpha_20", "naafiri_base_q_dissolve", "naafiri_base_2x2_sparkle",
                                  "naafiri_base_foundation_glow01"]),
    ("e_slash / e_hit", ["naafiri_base_foundation_tile01", "naafiri_base_foundation_tile02", "naafiri_base_tipmask",
                         "naafiri_base_foundation_glow02"]),
    ("r_roar / r_reset / pack_aura", ["naafiri_base_r_flash_sharp", "naafiri_base_r_cas_outline", "naafiri_base_r_eyes01",
                                      "naafiri_base_r_packmatehead", "naafiri_base_glowavatar01"]),
    ("r_shield / r_shred", ["naafiri_base_r_shield01", "naafiri_base_w_indicatorbase",
                            "naafiri_base_w_overheadidicator01", "naafiri_base_w_overheadidicator03"]),
]


def design_1x(name):
    """The design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, name))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / PPU, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Her and a packmate at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    import tfm2_ase as T
    figs = [design_1x("idle.png"), design_1x("pack.png")]
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
    d.text((8, 36), f"纳亚菲利 {figs[0].shape[1]}×{figs[0].shape[0]} 格，伙伴 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape, figs[1].shape


def design_sheet(path):
    """Her and a packmate at 4x, the designs' own squares (PPU 1.5)."""
    a = np.asarray(Image.open(RF.lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    b = np.asarray(Image.open(RF.lp(os.path.join(HD, "pack.png"))).convert("RGBA"))
    W = (a.shape[1] + b.shape[1]) * 4 + 48
    H = max(a.shape[0], b.shape[0]) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, H - 16 - a.shape[0] * 4))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(b, 4, 0), 4, 1)), (32 + a.shape[1] * 4, H - 16 - b.shape[0] * 4))
    bg.convert("RGB").save(path)


def document(shapes):
    (h, w), (ph, pw) = shapes[0][:2], shapes[1][:2]
    L = []
    a = L.append
    a("# 百裂冥犬 纳亚菲利：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/naafiri_designs.png`：左边纳亚菲利——3/4 正面朝右的四足猎犬、红色狼头白色口鼻、"
      f"石板蓝甲壳、深紫色刀刃鬃毛镶薄荷绿边；右边狗群伙伴——深红色的小猎犬、灰色骨头盔）。她在游戏里是**高清**的（每个游戏格子里 "
      f"1.5×1.5 个细像素），{h} 格高、{w} 格长，伙伴 {ph} 格高、{pw} 格长；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/naafiri_size.png`：她和伙伴放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏"
      "像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里纳亚菲利自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她的暗裔之力是深红色的、芯是白的，影子是暗紫色**；刀刃边上偶尔一点**薄荷绿**的闪光；"
      "**匕首是钢刃加骨柄**；**回血是深红带金**（不是绿色）。")
    a("> - **特效要亮**：每道光、每团血光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **光、血光、斩痕、冲击波、光环都没有黑描边**；**实物**（匕首、狗群伙伴、小盾）有 1 格近黑描边。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（两把匕首、狗群的速度线）"
      "**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的；匕首转成圆盘就两边一样）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `naafiri_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/naafiri_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「狂烈种群」 | 扑咬；每次普攻和技能命中，狗群也咬一口（暴吼时四只） | `a_hit` · `pk_bite` · `pk_bite4` |")
    a("| 技能 1 = Q「暗裔犬牙」 | 甩出匕首、流血；狗群扑上命中的英雄撕咬 3 秒；下一次普攻甩出第二把，命中英雄回血 | `q_dagger` · `q_leap` · "
      "`q_hit` · `q_bleed` · `pk_leap` · `pk_ride` · `q2_dagger` · `q2_hit` · `q_heal` |")
    a("| 技能 2 = E「剔骨本能」 | 冲到目标身上，周围撕裂两圈 | `e_slash` · `e_slash2` · `e_hit` |")
    a("| 大招「暴吼」+「猎狗血性」 | 先吼（不可选取、狗群翻倍 5 秒），再扑向英雄（减速、减护甲）；参与击杀后可带护盾再扑一次 | `r_roar` · "
      "`pack_aura` · `r_hit` · `r_shred` · `r_reset` · `r_shield` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、血光、斩痕、冲击波、光环没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实物——匕首、伙伴、小盾——有 1 格近黑描边）。")
    a("- **要亮**：每个光、血光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("暗裔之力（深红）", CRIMSON), ("暗影（暗紫）", VIOLET), ("刀刃闪光（薄荷绿，只做点缀）", MINT),
                        ("匕首骨柄", BONE), ("匕首钢刃", STEEL), ("回血（深红带金）", HEAL), ("狗群伙伴", PACK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（撕裂、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**（`pk_ride` 里的两只小狗是要画的）。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：E 撕裂半径 18000，大招射程 60000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `naafiri_fx_{name}.png`：{title}\n")
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
        a(f"| `naafiri_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_naafiri_fx`（小的）和 `league_naafiri_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_naafiri.py 的 views；buff pack4 的 tag 是 pack_aura）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；e_slash、e_slash2、r_roar、pack_aura、r_shield 跟随她。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="naafiri_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "naafiri_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_naafiri.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "naafiri_designs.png"))
    shapes = size_sheet(os.path.join(out, "design", "naafiri_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"naafiri_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "left-right"} for x in FX], f, ensure_ascii=False,
                  indent=1)
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
