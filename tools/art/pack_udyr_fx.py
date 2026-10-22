#!/usr/bin/env python3
"""Build udyr_fx_pack.zip: step 3 of Udyr's sprite - Codex (or Gemini) draws his effects (pack_ksante_fx.py's way).

    python tools/lol/fx_ref_udyr.py             # League's particle textures -> C:/t/ud_work/fxref (Riot's art, local only)
    python tools/art/pack_udyr_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name udyr_fx_redo_pack]

The pack (C:/t/ud_work/fx/udyr_fx_pack, zipped into --out, default dist/udyr_packs) holds PROMPTS.md (also written to
assets/source/udyr/PROMPTS_FX.md), design/udyr_designs.png (the four stances' designs at 4x, their squares at PPU 1.5),
design/udyr_size.png (all four at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/lol_fx_ref.png (League's own particle textures for Udyr, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_udyr.py): view_projectiles q_bolt, r_rel; view_effects a_hit,
q_on, q_wake, q_hit, q_bolt_hit, e_on, e_wake, e_hit, r_on, r_hit, r_rel_hit, w_on, w_heal; view_buffs q_as, e_ms,
e_imm, e_stun, r_storm, r_slow, w_sh; plus the forward pictures drawn into his own frames (tools/fix/bake_caster_fx.py's
way): q_swipe (the bear's claw arcs in q_attack), e_trail (the ram's fire behind him in e_run).
League's colours (the 2022 rework, its four spirits): the Bear (Q) is VIOLET-BLUE LIGHTNING, the Ram (E) ORANGE FIRE,
the Phoenix (R) ICE BLUE wind and shards, the Boar (W, in the passive) JADE GREEN; each stance has its spirit's sigil
(udyr_base_vgu_stanceicon_2x2: a bear, a boar, a ram, a phoenix head), shown over his head as he enters it. Red side:
the client never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right;
a projectile is turned with its flight, so it is drawn flying right and symmetric top to bottom; the baked ones point
forward (right) and need no symmetry.
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

TMP = "C:/t/ud_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "udyr", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "udyr", "hd")
NAME = "udyr_fx_pack"
PPU = 1.5
DESIGNS = ("idle.png", "q_idle.png", "e_idle.png", "r_idle.png")

VOLT = "#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78"      # the Bear: violet-blue lightning
FIRE = "#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08"      # the Ram: fire
ICE = "#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86"       # the Phoenix: ice and wind
JADE = "#FFFFFF, #E0FFE8, #9CF0B8, #4ED08A, #1E9A5E, #0E5A3A"      # the Boar: the iron mantle and its healing
DUST = "#F4E8D0, #D2BC94, #A08A66, #6E5C44"                        # dust kicked up
VO = f"a violet-blue lightning ramp ({VOLT})"
FI = f"an orange fire ramp ({FIRE})"
IC = f"an ice-blue ramp ({ICE})"
JA = f"a jade-green light ramp ({JADE})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
FWD = "pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry)"
CENTER = RF.CENTER
row = RF.row
HIM = "he stands in the middle, not drawn: a burly man 33 squares wide and 40 tall, fists raised"
HIM_Q = "he stands in the middle, not drawn: hunched like a bear, 43 squares wide and 41 tall"
HIM_E = "he stands in the middle, not drawn: head low under two big ram horns, 43 squares wide and 46 tall"
HIM_R = "he stands in the middle, not drawn: arms spread wide, 59 squares wide and 49 tall"
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
SOLID = "SOLID OBJECTS (ice shards) have a 1-square near-black outline; light, lightning, fire, wind and dust have none"


def sigil(animal, colour):
    return (f"A SPIRIT SIGIL rising over his head, 5 frames, {LR}: 1 a small {colour}"
            f" flash 4 squares across; 2 the {animal} HEAD SIGIL appearing, a bold flat emblem seen from the front (like a "
            f"carved totem mask, as in udyr_base_vgu_stanceicon_2x2), 12 squares wide, white core and lit edges; 3 the "
            f"sigil at full brightness with 4 short rays; 4 the sigil 1 square higher, its inner lines fading; 5 only its "
            f"outline in its darkest shades, breaking into specks.")


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_hit", "普攻：拳头打中，3 帧", "view_effects `league_udyr_a_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "缠绷带的拳头砸中：一团白色的冲击闪光带一点尘土。**左右对称**，3 帧。",
     DU + ", " + FI,
     "A PUNCH HIT, 3 frames, " + LR + ": 1 a white-yellow four-pointed flash 5 squares across; 2 the flash 8 across with "
     "a ring of dust puffs at mirrored places; 3 only a few dust puffs further out.",
     row(3, 10, 10) + CENTER),
    # ---- Q Wilding Claw (the Bear)
    ("q_on", "Q 狂暴爪击：熊之灵的图腾在他头上亮起，5 帧", "view_effects `league_udyr_q_on`（他身上，z 3；左右对称）", "16 × 16",
     "进入熊姿态：一个**熊头图腾**（正面的熊头，像刻出来的图腾面具，参考 stanceicon 里的熊）在他头顶亮起又散掉，紫蓝色的电光。**左右对称**，5 帧。",
     VO,
     sigil("BEAR", "violet-blue"),
     row(5, 16, 16) + "; the sigil's middle on the cell's middle (the cell sits over his head)."),
    ("q_wake", "Q 觉醒：熊之灵的闪电在他身上炸开，6 帧", "view_effects `league_udyr_q_wake`（他身上，z 3；左右对称）", "50 × 50",
     "同一姿态再放 Q（觉醒）：紫蓝色的闪电从他身边四周劈下、在他周围一圈噼啪作响（参考 q_ele 系列），熊头图腾在头顶。**左右对称**，6 帧。**身体位置留空**。",
     VO,
     "AN AWAKENING STORM OF LIGHTNING round him, 6 frames, " + LR + ": 1 four short lightning forks crackling at "
     "mirrored places round the edge of the cell; 2 two big jagged bolts striking down on both sides of him from the "
     "top of the cell to the ground, white cores; 3 the bolts at full length with branches, a ring of sparks on the "
     "ground ellipse round his feet; 4 a BEAR HEAD SIGIL 12 squares wide flashing over his head, the bolts shorter; 5 "
     "small arcs jumping round him; 6 fading sparks. The middle (his body: 28 squares wide, 40 tall) stays EMPTY.",
     row(6, 50, 50) + "; " + HIM_Q + " (his feet on the cell's bottom row, 2 squares up)."),
    ("q_as", "Q 熊爪状态：脚下的电光（循环），4 帧", "view_buffs `league_udyr_q_as`（跟着他，循环，z -1；左右对称）", "34 × 10",
     "熊姿态的攻速加成还在：他脚下一圈贴着地面的紫蓝色电弧，偶尔往上跳一点火花。**左右对称**，4 帧循环。",
     VO,
     "A CRACKLING GROUND RING, 4 frames looping, " + LR + ": a flat ellipse of small violet-blue electric arcs 34 squares "
     "wide and 8 tall on the ground, a few sparks jumping 2-3 squares up from it, the arcs at different places each "
     "frame; the inside of the ellipse empty.",
     row(4, 34, 10) + "; the ellipse's middle on the cell's middle; " + HIM_Q + " (only his feet reach the cell)."),
    ("q_swipe", "Q 熊爪攻击：往前抓出的三道爪痕弧光（画进他的帧），3 帧", "画进他自己的 q_attack 帧（bake_caster_fx；朝右）", "28 × 24",
     "熊姿态的普攻：熊爪往前一抓，三道并排的紫蓝色爪痕弧光（带白芯）。**朝右画**，3 帧。",
     VO,
     "THREE CLAW STREAKS, 3 frames, " + FWD + ": 1 three parallel thin arcs starting at the cell's left side, curving "
     "down-forward; 2 the three arcs at full length (24 squares), white cores, violet edges, small sparks at their ends; "
     "3 the arcs thinning and breaking into specks.",
     row(3, 28, 24) + "; his fist at the cell's left edge, half way up (not drawn)."),
    ("q_hit", "Q 强化攻击打中：三道爪痕，4 帧", "view_effects `league_udyr_q_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "熊爪打中敌人：三道竖着的紫蓝色爪痕一闪，四周跳电火花。**左右对称**，4 帧。",
     VO,
     "THREE CLAW MARKS, 4 frames, " + LR + ": 1 a white flash 6 squares across; 2 three vertical claw slashes side by "
     "side, the middle one longest (14 squares), white cores, violet edges; 3 the slashes with sparks jumping off at "
     "mirrored places; 4 fading slashes and specks.",
     row(4, 18, 18) + CENTER),
    ("q_bolt", "Q 觉醒的闪电球（弹道，循环），4 帧", "view_projectiles `league_udyr_q_bolt`（随飞行方向转；上下对称）", "10 × 8",
     "觉醒熊爪召来的闪电，飞向目标的一小团电光球。**朝右飞、上下对称**，4 帧循环。",
     VO,
     "A SMALL BALL OF LIGHTNING, 4 frames looping, " + TB + ": a white core 3 squares across inside a violet-blue "
     "crackle, two short arcs trailing behind on the left, the arcs at different places each frame.",
     row(4, 10, 8) + "; the ball's middle on the cell's middle row, 2 squares from the right edge."),
    ("q_bolt_hit", "Q 觉醒：闪电劈在目标身上，5 帧", "view_effects `league_udyr_q_bolt_hit`（跟随目标，z 2；左右对称）", "22 × 48",
     "觉醒熊爪的闪电从天上直直劈到敌人身上，落地炸开一圈电花。**左右对称**（中间一道直的主干，两边对称的分叉），5 帧。",
     VO,
     "A LIGHTNING STRIKE from the sky, 5 frames, " + LR + ": 1 a thin white line from the top of the cell to the ground "
     "row; 2 the bolt at full width (3 squares, white core, violet edges) with MIRRORED zig-zag branches on both sides; "
     "3 the bolt and a flash on the ground ellipse (16 x 5 squares) at its foot; 4 the bolt gone, the ground flash with "
     "sparks flying out at mirrored places; 5 fading sparks.",
     row(5, 22, 48) + "; the ground ellipse's middle 3 squares above the cell's bottom, centered; " + TARGET + "."),
    # ---- E Blazing Stampede (the Ram)
    ("e_on", "E 踏火蛮冲：公羊之灵的图腾在他头上亮起，5 帧", "view_effects `league_udyr_e_on`（他身上，z 3；左右对称）", "16 × 16",
     "进入公羊姿态：一个**公羊头图腾**（正面的羊头，两只卷角）在他头顶亮起又散掉，橙色的火光。**左右对称**，5 帧。",
     FI,
     sigil("RAM (two curled horns)", "orange"),
     row(5, 16, 16) + "; the sigil's middle on the cell's middle (the cell sits over his head)."),
    ("e_wake", "E 觉醒：他身边腾起一圈火焰，6 帧", "view_effects `league_udyr_e_wake`（他身上，z 3；左右对称）", "50 × 52",
     "同一姿态再放 E（觉醒，免控）：他脚下炸开一圈火焰往上腾起，公羊头图腾在头顶。**左右对称**，6 帧。**身体位置留空**。",
     FI,
     "A RING OF FIRE BURSTING UP round him, 6 frames, " + LR + ": 1 a ring of embers on the ground ellipse (40 x 10 "
     "squares) round his feet; 2 flames rising from the ring on both sides, 12 squares tall; 3 the flames at full "
     "height (24 squares) curling inward at the top like horns, white-yellow cores; 4 a RAM HEAD SIGIL 12 squares wide "
     "flashing over his head, the flames lower; 5 low flames and embers rising; 6 a few embers. The middle (his body: "
     "30 squares wide, 44 tall) stays EMPTY.",
     row(6, 50, 52) + "; " + HIM_E + " (his feet on the cell's bottom row, 2 squares up)."),
    ("e_ms", "E 公羊状态：脚下的火（循环），4 帧", "view_buffs `league_udyr_e_ms`（跟着他，循环，z -1；左右对称）", "30 × 10",
     "公羊姿态的移速加成还在：他脚下贴地的一圈小火苗，往上飘火星。**左右对称**，4 帧循环。",
     FI,
     "LOW FLAMES AT HIS FEET, 4 frames looping, " + LR + ": a flat ellipse of small flame tongues 30 squares wide and 6 "
     "tall on the ground, a few embers drifting 2-4 squares up, the flames flickering differently each frame; the "
     "inside of the ellipse empty.",
     row(4, 30, 10) + "; the ellipse's middle on the cell's middle; " + HIM_E + " (only his feet reach the cell)."),
    ("e_imm", "E 觉醒免控：头顶一圈火焰角环（循环），4 帧", "view_buffs `league_udyr_e_imm`（跟着他，循环，z 3；左右对称）", "20 × 8",
     "觉醒后免疫定身：他头顶一圈燃烧的光环，两边各翘起一只火焰羊角。**左右对称**，4 帧循环。",
     FI,
     "A BURNING HALO over his head, 4 frames looping, " + LR + ": a flat glowing ellipse 14 squares wide and 3 tall, a "
     "small flame horn curling up and out on each end, the flames flickering differently each frame.",
     row(4, 20, 8) + "; the halo's middle on the cell's middle (the cell sits just over his head)."),
    ("e_trail", "E 冲锋：身后拖着的火焰（画进他的帧），4 帧", "画进他自己的 e_run 帧（bake_caster_fx；朝右）", "36 × 18",
     "公羊冲锋：他身后（左边）拖出一道贴地的火焰尾巴，脚下溅火星。**朝右画**，4 帧。",
     FI + ", " + DU,
     "A FIRE TRAIL behind a charge, 4 frames, " + FWD + ": a tongue of fire lying low along the ground, thickest at the "
     "right end (his feet) and thinning to the LEFT, embers and dust puffs flying back; the flames move each frame.",
     row(4, 36, 18) + "; his feet at the cell's bottom right corner (not drawn)."),
    ("e_hit", "E 撞上：晕眩的那一下，4 帧", "view_effects `league_udyr_e_hit`（跟随目标，z 2；左右对称）", "24 × 24",
     "公羊冲撞的一击打中：一团橙色火焰爆开，地上一圈裂开的尘土。**左右对称**，4 帧。",
     FI + ", " + DU,
     "A FIERY RAM IMPACT, 4 frames, " + LR + ": 1 a white-yellow flash 8 squares across; 2 a burst of fire 18 squares "
     "across with flame tongues at mirrored places, a ring of dust on the ground ellipse; 3 the fire breaking into "
     "embers, the dust ring wider; 4 fading embers and dust.",
     row(4, 24, 24) + CENTER),
    ("e_stun", "E 晕眩（敌人头上，循环），4 帧", "view_buffs `league_udyr_e_stun`（跟着目标，循环，z 3；左右对称）", "16 × 6",
     "被撞晕的敌人头上转着的几颗小火星。**左右对称**，4 帧循环。",
     FI,
     "STUN EMBERS circling, 4 frames looping, " + LR + ": three small star-shaped embers on a flat ellipse 14 squares "
     "wide and 4 tall, moving round it frame by frame (each frame mirrored left to right as a whole picture).",
     row(4, 16, 6) + "; the ellipse's middle on the cell's middle (the cell sits over the target's head)."),
    # ---- R Wingborne Storm (the Phoenix)
    ("r_on", "R 极凌飓风：凤凰之灵的图腾在他头上亮起，5 帧", "view_effects `league_udyr_r_on`（他身上，z 3；左右对称）", "16 × 16",
     "进入凤凰姿态：一个**凤凰头图腾**（正面的鸟头，两边张开的羽冠）在他头顶亮起又散掉，冰蓝色的光。**左右对称**，5 帧。",
     IC,
     sigil("PHOENIX (a bird head with a fan of crest feathers)", "ice-blue"),
     row(5, 16, 16) + "; the sigil's middle on the cell's middle (the cell sits over his head)."),
    ("r_storm", "R 冰风暴围着他转（循环），6 帧", "view_buffs `league_udyr_r_storm`（跟着他，循环，z 3；左右对称）", "64 × 44",
     "凤凰的冰风暴绕着他转：几条冰蓝色的风带绕成一个斜着看的大圈，里面卷着冰晶碎片和雪花，前面的风带从他脚前经过、后面的从他背后绕过。"
     "**左右对称**（每一帧整体左右对称），6 帧循环。**身体位置留空**。",
     IC,
     "A GLACIAL STORM WHIRLING round him, 6 frames looping, " + LR + ": three or four bands of icy wind circling on a big "
     "ellipse (60 squares wide, 18 tall, its middle 10 squares above the ground) with small ice shards and snowflakes "
     "carried in them, the bands and the shards at new places each frame as if spinning; a faint second ring higher "
     "up (at his chest) narrower; white cores on the bands. " + SOLID + ". The middle (his body: 34 squares wide, 46 "
     "tall) stays EMPTY except the bands passing in front of his legs.",
     row(6, 64, 44) + "; " + HIM_R + " (his feet on the cell's bottom row, 4 squares up)."),
    ("r_hit", "R 风暴刮中的敌人，3 帧", "view_effects `league_udyr_r_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "风暴刮中：几片冰晶擦过、一小团寒气。**左右对称**，3 帧。",
     IC,
     "AN ICE GRAZE, 3 frames, " + LR + ": 1 a white flash 4 squares across; 2 four small ice shards flying out at "
     "mirrored places with a puff of frost; 3 the shards further out, the frost fading. " + SOLID + ".",
     row(3, 14, 14) + CENTER),
    ("r_slow", "R 减速（敌人脚下，循环），4 帧", "view_buffs `league_udyr_r_slow` 和 `r2_slow`（跟着目标，循环，z -1；左右对称）", "20 × 6",
     "被冰风暴减速的敌人：脚下一圈结霜的地面，几颗小冰晶。**左右对称**，4 帧循环。",
     IC,
     "A FROST PATCH, 4 frames looping, " + LR + ": a flat ellipse of frost 20 squares wide and 5 tall on the ground with "
     "tiny ice crystals glinting at different places each frame.",
     row(4, 20, 6) + "; the ellipse's middle on the cell's middle; " + TARGET + " (only its feet reach the cell)."),
    ("r_rel", "R 风暴放出去：飞向敌人的冰风旋涡（弹道，循环），4 帧", "view_projectiles `league_udyr_r_rel`（随飞行方向转；上下对称）",
     "30 × 20",
     "风暴结束时被放出去追敌人：一团往前飞的冰风旋涡，前头像一只展翅的冰凤凰的轮廓。**朝右飞、上下对称**，4 帧循环。",
     IC,
     "A FLYING ICE STORM, 4 frames looping, " + TB + ": a spinning ball of icy wind 14 squares across at the right end, "
     "two swept-back WING SHAPES of wind and feathers spreading up and down from it (mirrored top to bottom), a trail "
     "of snow and shards behind on the left; the wind bands turn each frame. " + SOLID + ".",
     row(4, 30, 20) + "; the ball's middle on the cell's middle row, 2 squares from the right edge."),
    ("r_rel_hit", "R 风暴炸在敌人身上，6 帧", "view_effects `league_udyr_r_rel_hit`（跟随目标，z 2；左右对称）", "36 × 36",
     "放出去的风暴砸中：冰风往四周炸开，冰晶飞散，地上一圈霜。**左右对称**，6 帧。",
     IC,
     "AN ICE STORM BURST, 6 frames, " + LR + ": 1 a white flash 8 squares across; 2 a ring of icy wind 20 squares "
     "across with ice shards flying out at mirrored places; 3 the ring 30 across, the shards further out, a frost "
     "ellipse on the ground (30 x 8); 4 the wind breaking into curls; 5 the shards falling, snowflakes; 6 fading frost "
     "and specks. " + SOLID + ".",
     row(6, 36, 36) + CENTER),
    # ---- W Iron Mantle (the Boar, in the passive)
    ("w_on", "被动·坚铁甲胄：野猪之灵的护盾罩上来，6 帧", "view_effects `league_udyr_w_on`（他身上，z 3；左右对称）", "48 × 52",
     "坚铁甲胄发动：头顶亮起**野猪头图腾**，一层玉绿色的护盾从上往下罩住他（只画护盾的外沿和几道亮纹）。**左右对称**，6 帧。**身体位置留空**。",
     JA,
     "AN IRON MANTLE CLOSING round him, 6 frames, " + LR + ": 1 a BOAR HEAD SIGIL (a front-facing boar head with tusks) "
     "12 squares wide flashing over his head; 2 a jade-green shell edge appearing at the top, an arch 30 squares wide; "
     "3 the edge sweeping down both sides into a tall rounded dome 44 wide and 48 tall, angular plate lines on it like "
     "a boar's bristled hide; 4 the whole dome outline bright; 5 the dome dimmer with a few bright plate edges; 6 a "
     "faint outline. Only the dome's EDGE (2-3 squares thick) and a few plate lines are drawn; the middle (his body) "
     "stays EMPTY.",
     row(6, 48, 52) + "; " + HIM + " (his feet on the cell's bottom row, 2 squares up)."),
    ("w_sh", "被动·坚铁甲胄的护盾（他身上，循环），4 帧", "view_buffs `league_udyr_w_sh`（跟着他，循环，z 3；左右对称）", "46 × 50",
     "护盾还在：罩着他的玉绿色护盾外沿，一道亮光沿着外沿慢慢流动。**左右对称**，4 帧循环。**身体位置留空**。",
     JA,
     "A SHIMMERING SHIELD DOME, 4 frames looping, " + LR + ": the outline of a tall rounded dome 44 squares wide and 48 "
     "tall, 1-2 squares thick, in its middle shades with a few angular plate lines, a bright highlight travelling down "
     "both sides at the same height (mirrored) frame by frame. The middle (his body) stays EMPTY.",
     row(4, 46, 50) + "; " + HIM + " (his feet on the cell's bottom row, 2 squares up)."),
    ("w_heal", "被动·坚铁甲胄：攻击回血，4 帧", "view_effects `league_udyr_w_heal`（他身上，z 3；左右对称）", "24 × 30",
     "坚铁甲胄期间的攻击回血：玉绿色的光点和几道往上飘的光线从他身上升起。**左右对称**，4 帧。",
     JA,
     "A HEALING RISE, 4 frames, " + LR + ": 1 four small jade sparkles at mirrored places low on the cell; 2 thin rays of "
     "light rising from them, 8 squares tall; 3 the rays higher and a few small plus-shaped sparkles; 4 fading sparkles "
     "at the top.",
     row(4, 24, 30) + "; his chest in the cell's middle (not drawn)."),
]
BIG_FX = ["q_wake", "q_bolt_hit", "e_wake", "r_storm", "r_rel", "r_rel_hit", "w_on", "w_sh"]
FLYING = ["q_bolt", "r_rel"]
FORWARD = ["q_swipe", "e_trail"]

GROUPS = [
    ("sigils (q_on e_on r_on w_on)", ["udyr_base_vgu_stanceicon_2x2", "udyr_base_vgu_awaken_spirit",
                                      "udyr_base_vgu_awaken_glow", "udyr_base_vgu_awaken_sharpshape"]),
    ("a_hit q_hit q_swipe q_as", ["udyr_base_vgu_impact01", "udyr_base_vgu_q_beararms_mask", "udyr_base_vgu_q_ele_glow",
                                  "udyr_base_vgu_q_ele_flat_energy"]),
    ("q_wake q_bolt q_bolt_hit", ["udyr_base_vgu_q_ele_long", "udyr_base_vgu_q_ele_long_blur",
                                  "udyr_base_vgu_q_ele_tilehori01", "udyr_base_vgu_awaken_flipbook04"]),
    ("e_on e_wake e_ms e_trail e_imm", ["udyr_base_vgu_flameshape", "udyr_base_vgu_flameshape_errode",
                                        "udyr_base_vgu_e_softbeam", "udyr_base_vgu_e_ashe2x2"]),
    ("e_hit e_stun", ["udyr_base_vgu_e_impactgroundcrater", "udyr_base_vgu_e_craterdissolve", "udyr_base_shockwave",
                      "udyr_base_smokeerode"]),
    ("r_storm r_hit r_slow", ["udyr_base_vgu_r_iceshards", "udyr_base_vgu_r_trail", "udyr_base_vgu_generic_icesmoke",
                              "udyr_base_vgu_r_tile01"]),
    ("r_rel r_rel_hit", ["udyr_base_vgu_r_2x2_feathers", "udyr_base_vgu_crystaltexture", "udyr_base_vgu_generic_ribbon",
                         "udyr_base_vgu_awaken_energytrail"]),
    ("w_on w_sh w_heal", ["udyr_base_vgu_w_shield_3dshape", "udyr_base_vgu_w_boaredge", "udyr_base_vgu_w_rimglow",
                          "udyr_base_vgu_w_healrays"]),
]


def design_1x(name):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, name))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / PPU, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The four stances at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x(n) for n in DESIGNS]
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
    sz = "、".join(f"{lab} {f.shape[1]}×{f.shape[0]}" for lab, f in zip(("平常", "熊", "公羊", "凤凰"), figs))
    d.text((8, 36), f"乌迪尔 {sz} 格，原版斗士 {figs[4].shape[1]}×{figs[4].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255),
           font=font)
    img.convert("RGB").save(path)
    return [f.shape for f in figs[:4]]


def design_sheet(path):
    """The four designs at 4x, their own squares (PPU 1.5)."""
    ims = [np.asarray(Image.open(RF.lp(os.path.join(HD, n))).convert("RGBA")) for n in DESIGNS]
    W = sum(a.shape[1] * 4 + 32 for a in ims)
    H = max(a.shape[0] for a in ims) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    x = 16
    for a in ims:
        bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (x, H - 16 - a.shape[0] * 4))
        x += a.shape[1] * 4 + 32
    bg.convert("RGB").save(path)


def document(shapes):
    (h, w), (qh, qw), (eh, ew), (rh, rw) = [s[:2] for s in shapes]
    L = []
    a = L.append
    a("# 兽灵行者 乌迪尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/udyr_designs.png`，从左到右：平常护头的姿势——光膀子的壮汉，"
      "暗红纹身、深色长脏辫和络腮胡、一根蓝羽毛发辫、白绷带拳头、橙红大念珠；熊姿态——披着熊皮、熊头盖在拳头上；公羊姿态——两只大卷羊角；"
      "凤凰姿态——两臂张开、胳膊上一排深蓝羽刃）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），平常 {h} 格高、{w} 格宽，熊 {qh}×{qw}，公羊 {eh}×{ew}，"
      f"凤凰 {rh}×{rw}（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/udyr_size.png`：四种姿态放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里乌迪尔自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。**第一行的 stanceicon 是四个兽灵的图腾**（熊、野猪、公羊、凤凰的正面头像），`q_on`、`e_on`、`r_on`、`w_on` "
      "里的图腾照它画。颜色按兽灵分：**熊（Q）紫蓝色闪电**，**公羊（E）橙色火焰**，**凤凰（R）冰蓝色的风和冰晶**，**野猪（被动里的坚铁甲胄）玉绿色**。")
    a("> - **特效要亮**：每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **光、闪电、火、风、尘土都没有黑描边**；**实物**（冰晶碎片）有 1 格近黑描边。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" + "`、`".join(FLYING) +
      "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进他自己帧里的**（`" + "`、`".join(FORWARD) +
      "`）**朝右画，不用对称**（跟着他的身体一起翻转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `udyr_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/udyr_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 缠绷带的拳头，熊姿态时是熊爪 | `a_hit` · `q_swipe` |")
    a("| 技能 1 = Q「狂暴爪击」（熊） | 进入熊姿态，接下来两拳加攻速、加伤；同一姿态再放（觉醒）两拳召来闪电 | `q_on` · `q_wake` · `q_as` · "
      "`q_swipe` · `q_hit` · `q_bolt` · `q_bolt_hit` |")
    a("| 技能 2 = E「踏火蛮冲」（公羊） | 进入公羊姿态，加速冲到敌人面前撞晕；觉醒时免疫定身 | `e_on` · `e_wake` · `e_ms` · `e_imm` · "
      "`e_trail` · `e_hit` · `e_stun` |")
    a("| 大招 = R「极凌飓风」（凤凰） | 进入凤凰姿态，冰风暴绕身伤害减速，结束时把风暴放出去追敌人 | `r_on` · `r_storm` · `r_hit` · "
      "`r_slow` · `r_rel` · `r_rel_hit` |")
    a("| 被动「众灵纽带」+ W「坚铁甲胄」（野猪） | 放技能后两次攻击加攻速；隔一段时间放技能时罩上护盾，接下来两拳回血 | `w_on` · `w_sh` · "
      "`w_heal` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、闪电、火、风、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实物——冰晶碎片——有 1 格近黑描边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("熊·紫蓝闪电", VOLT), ("公羊·橙色火焰", FIRE), ("凤凰·冰蓝", ICE), ("野猪·玉绿", JADE),
                        ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（火圈、霜、风暴的圈）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：冰风暴半径 17000，"
      "闪电溅射半径 9000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `udyr_fx_{name}.png`：{title}\n")
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
        a(f"| `udyr_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_udyr_fx`（小的）和 `league_udyr_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_udyr.py 的 views；r2_slow 的 tag 是 `r_slow`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；朝前的（{'、'.join(FORWARD)}）用 tools/fix/bake_caster_fx.py 画进他的帧"
      "（q_attack / e_run），不进表；其余断言左右对称；q_on、e_on、r_on 放在他头顶（view 的 y 偏移），w_on、w_sh、r_storm 跟随他。")
    a("- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="udyr_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "udyr_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_udyr.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "udyr_designs.png"))
    shapes = size_sheet(os.path.join(out, "design", "udyr_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"udyr_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
