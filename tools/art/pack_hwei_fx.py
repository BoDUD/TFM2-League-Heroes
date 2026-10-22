#!/usr/bin/env python3
"""Build hwei_fx_pack.zip: step 3 of Hwei's sprite - Codex (or Gemini) draws his effects (pack_udyr_fx.py's way).

    python tools/lol/fx_ref_hwei.py             # League's particle textures -> C:/t/hw_work/fxref (Riot's art, local only)
    python tools/art/pack_hwei_fx.py [--no-zip] [--out DIR] [--only a_hit,q_q_hit --name hwei_fx_redo_pack]

The pack (C:/t/hw_work/fx/hwei_fx_pack, zipped into --out, default dist/hwei_packs) holds PROMPTS.md (also written to
assets/source/hwei/PROMPTS_FX.md), design/hwei_design.png (the idle at 4x, its squares at PPU 1.5), design/hwei_size.png
(at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and
refs/lol_fx_ref.png (League's own particle textures for Hwei, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_hwei.py): view_projectiles a_ink, q_q_ball (q_q_ball2 too),
e_q_face, r_paint; view_effects a_hit, p_burst, q_w_tell, q_w_hit, q_q_hit, q_e_lava, e_q_hit, e_w_open, e_w_hit,
e_e_open, e_e_hit, w_pool, w_shield, r_canvas, r_burst, r_hit; view_buffs p_mark, e_bound, w_haste, slow (q_e_slow,
e_slow and r_slow share it).
League's colours (Hwei's three subjects are three palettes of paint): Disaster (Q) RED-ORANGE fire paint and a GOLD-WHITE
bolt, Serenity (W, in the passive) TEAL-BLUE, Torment (E) VIOLET-MAGENTA, his ult a dark INDIGO canvas with gold strands
and magenta-orange strokes; the signature (passive) a GOLD brush-ring with his glyph (hwei_base_p_indicator01). Red side:
the client never mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right (a
face, an eye and the jaws are drawn from the front, symmetric); a projectile is turned with its flight, so it is drawn
flying right and symmetric top to bottom (Grim Visage flies as a violet streak, its face shows on the hit).
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

TMP = "C:/t/hw_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "hwei", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "hwei", "hd")
NAME = "hwei_fx_pack"
PPU = 1.5

FIRE = "#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14"      # Disaster: red-orange fire paint, lava
BOLT = "#FFFFFF, #FFF8D8, #FFE07A, #F2B630, #B8781A"               # Disaster: the gold-white bolt
CALM = "#FFFFFF, #DDFBFF, #8CEAF2, #3CC4D8, #1F86B8, #18467E"      # Serenity: teal-blue
DREAD = "#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060"     # Torment: violet-magenta
INK = "#5A5E9A, #33366E, #1C1D44, #0E0E24"                         # his indigo ink
GOLD = "#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416"               # the signature, the gold strands
FI = f"a red-orange fire-paint ramp ({FIRE})"
BO = f"a gold-white lightning ramp ({BOLT})"
CA = f"a teal-blue paint ramp ({CALM})"
DR = f"a violet-magenta paint ramp ({DREAD})"
IN = f"an indigo ink ramp ({INK})"
GO = f"a gold ramp ({GOLD})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
PAINT = ("everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth "
         "neon energy; flat shades, the lit side of a stroke one shade lighter")
HIM = "he stands in the middle, not drawn: a slim painter 42 squares wide and 51 tall with his crescent and brush"
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack and passive
    ("a_ink", "普攻：甩出去的一团墨，4 帧循环", "view_projectiles `league_hwei_a_ink`（弹道，z 2；上下对称）", "12 × 6",
     "画笔甩出的一团靛蓝色的墨，后面拖一道笔触，边上一点金色的颜料点。**朝右飞，上下对称**，4 帧循环。",
     IN + ", " + GO,
     "AN INK BLOB flung by a brush, 4 looping frames, " + TB + ": a round indigo blob 4 squares across with a lighter "
     "highlight square in front, a tapering dry-brush stroke 7 squares long behind it, two gold paint specks beside the "
     "stroke at mirrored places; the stroke's ragged end shifts a little each frame. " + PAINT + ".",
     row(4, 12, 6) + CENTER),
    ("a_hit", "普攻：墨团打中，3 帧", "view_effects `league_hwei_a_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "墨团溅开：一圈靛蓝色的墨点向外溅，中间一个金色的小闪。**左右对称**，3 帧。",
     IN + ", " + GO,
     "AN INK SPLASH, 3 frames, " + LR + ": 1 a gold-white flash 3 squares across inside an indigo blot 5 across; 2 the "
     "blot burst into 8 indigo droplets at mirrored places, 8 squares across; 3 only 6 small droplets further out, "
     "fading to the darkest shade. " + PAINT + ".",
     row(3, 10, 10) + CENTER),
    ("p_mark", "被动落款：敌人脚下的落款印，6 帧循环", "view_buffs `league_hwei_p_mark`（跟随目标，z -1；左右对称）", "20 × 8",
     "被落款的敌人脚下：一圈金色的笔触圆环（从斜上方看的椭圆），中间一个金色的印章字形（参考 p_indicator01，"
     "**画成左右对称的篆字形状**）。金光在圈上慢慢流动。**左右对称**，6 帧循环。",
     GO + ", " + IN,
     "A PAINTER'S SEAL " + FEET + ", 6 looping frames, " + LR + ": a gold dry-brush ring 20 squares wide and 7 tall, "
     "drawn as one thick stroke that does not quite close at the back, and in its middle a small upright gold seal glyph "
     "(like a carved signature stamp, 4 squares wide, symmetric), dark indigo ink under the ring; a brighter gold "
     "highlight runs round the ring through the frames, mirrored on both sides. " + PAINT + ".",
     row(6, 20, 8) + CENTER),
    ("p_burst", "被动落款引爆：印章炸开，7 帧", "view_effects `league_hwei_p_burst`（大表，跟随目标，z 3；左右对称）", "28 × 28",
     "落款完成：脚下的金色印章亮起，一道金色和靛蓝的颜料柱从地上冲起来炸开，碎成金点。**左右对称**，7 帧。",
     GO + ", " + IN,
     "A SIGNATURE BURSTING, 7 frames, " + LR + ", " + TARGET + ": 1 the gold seal ring on the ground (22 wide, 7 tall) "
     "flashing white-gold; 2 a column of gold and indigo paint 8 squares wide shooting up from it to 14 squares; 3 the "
     "column 22 squares tall, its top splitting into two curling strokes; 4 it bursts: gold and indigo paint blobs flung "
     "out in a ring 26 squares across; 5 the blobs falling, a gold flash at the bottom; 6 gold specks and drips; 7 a few "
     "gold specks fading. " + PAINT + ".",
     row(7, 28, 28) + CENTER),
    # ---- skill: Subject: Disaster
    ("q_q_ball", "灾·没骨火：火焰颜料球，4 帧循环", "view_projectiles `league_hwei_q_q_ball`（弹道，z 2；上下对称）", "16 × 8",
     "一团红橙色的火焰颜料朝前飞，后面拖着火舌一样的笔触（参考 qe_firelicks）。**朝右飞，上下对称**，4 帧循环。",
     FI,
     "A FIREBALL OF PAINT, 4 looping frames, " + TB + ": a round ball 6 squares across, white-yellow core, orange and red "
     "rings, in front; behind it three flame-lick brush strokes trailing 9 squares to the left, the middle one longest, "
     "the outer two mirrored; the licks flicker each frame. " + PAINT + ".",
     row(4, 16, 8) + CENTER),
    ("q_q_hit", "灾·没骨火：火球炸开，5 帧", "view_effects `league_hwei_q_q_hit`（跟随目标，z 2；左右对称）", "20 × 20",
     "火焰颜料炸开：一团红橙色的火向四周溅开，火舌往上卷。**左右对称**，5 帧。",
     FI,
     "A FIRE-PAINT EXPLOSION, 5 frames, " + LR + ", " + TARGET + ": 1 a white-yellow flash 6 across at the middle; 2 a "
     "burst of orange-red paint 14 across with flame licks pointing out; 3 the flames 18 across, licks curling upward, "
     "drops of red paint flung out at mirrored places; 4 the flames sinking into dark red smoke-paint; 5 a few embers "
     "and drips. " + PAINT + ".",
     row(5, 20, 20) + CENTER),
    ("q_w_tell", "灾·攒聚雷：目标头顶的预警，6 帧", "view_effects `league_hwei_q_w_tell`（跟随目标，z 2；左右对称）", "16 × 24",
     "雷要劈下来之前：目标头顶上方聚起一团金色的颜料云，金线往中间收，越来越亮。**左右对称**，6 帧（约 0.75 秒）。",
     BO + ", " + IN,
     "A GATHERING BOLT, 6 frames, " + LR + ", " + TARGET + " (its head at the bottom of the cell): a small indigo paint "
     "cloud 10 squares wide hanging 6 squares above the head, gold strands spiralling into it from both sides, mirrored; "
     "frame by frame the strands get shorter and the cloud's gold core brighter, frame 6 a white-gold spark in the "
     "cloud with a thin gold line hinting down. " + PAINT + ".",
     row(6, 16, 24) + CENTER),
    ("q_w_hit", "灾·攒聚雷：金雷劈下，6 帧", "view_effects `league_hwei_q_w_hit`（大表，跟随目标，z 3；左右对称）", "24 × 48",
     "一道金白色的雷从上面劈到目标身上（参考 innerbolt，**画成竖直、左右对称的锯齿**），落地炸开一圈金色的颜料。**左右对称**，6 帧。",
     BO + ", " + IN,
     "A GOLD LIGHTNING BOLT, 6 frames, " + LR + ", " + TARGET + " (feet on the bottom of the cell): 1 a thin white line "
     "from the top of the cell to the feet; 2 the full bolt 6 squares wide, a white core with gold edges, zigzag bends "
     "mirrored on both sides, as if painted in one vertical stroke; 3 the bolt at its brightest with a gold splash "
     "ring 22 wide and 6 tall at the feet; 4 the bolt thinning, gold sparks flying out; 5 only the splash ring and "
     "drips; 6 a few gold specks. " + PAINT + ".",
     row(6, 24, 48) + CENTER),
    ("q_e_lava", "灾·连皴山：熔岩地带，12 帧（2.5 秒）", "view_effects `league_hwei_q_e_lava`（大表，地上不跟随，z -1；左右对称）",
     "44 × 20",
     "地上画出一片熔岩：像山水画的皴法一样的裂开的岩块，缝里流着红橙色的岩浆，火舌往上冒（参考 qe_firelicks、groundcrack）。"
     "先裂开、再烧一阵、最后暗下去。**左右对称**，12 帧，一共约 2.5 秒。",
     FI + ", " + IN,
     "A LAVA FIELD painted on the ground, 12 frames, " + LR + ": an oval " + FEET + " 40 squares wide and 13 tall; 1-2 "
     "dark ink cracks spreading from the middle; 3-4 the cracks glowing orange, dark rock plates between them drawn "
     "with short parallel brush strokes like an ink landscape; 5-9 molten red-orange lava in the cracks, small flame "
     "licks rising 4-6 squares at mirrored places, flickering frame by frame; 10-11 the flames gone, the cracks dimming "
     "to dark red; 12 only faint dark cracks. " + PAINT + ".",
     row(12, 44, 20) + CENTER),
    ("slow", "减速：脚下的墨滴，4 帧循环", "view_buffs `league_hwei_q_e_slow` / `e_slow` / `r_slow`（跟随，z -1；左右对称）",
     "16 × 8",
     "被减速的敌人脚下：一滩靛蓝色的墨，几滴墨往下滴，像脚被墨粘住。**左右对称**，4 帧循环。",
     IN,
     "STICKY INK " + FEET + ", 4 looping frames, " + LR + ": an indigo ink puddle 14 squares wide and 4 tall, two short "
     "ink drips rising up the legs' place at mirrored spots and sliding down through the frames, a lighter highlight "
     "square on the puddle. " + PAINT + ".",
     row(4, 16, 8) + CENTER),
    # ---- skill2: Subject: Torment
    ("e_q_face", "悚·阴沉变意：飞出去的紫色笔触，4 帧循环", "view_projectiles `league_hwei_e_q_face`（弹道，z 2；上下对称）",
     "16 × 8",
     "一道紫红色的颜料笔触往前飞，前头一团亮的颜料，后面拖两道卷曲的尾巴。**朝右飞，上下对称**（脸在打中时才出现），4 帧循环。",
     DR,
     "A VIOLET PAINT STREAK, 4 looping frames, " + TB + ": a bright magenta-white blob 4 squares across in front, two "
     "curling violet tails 10 squares long behind it, mirrored top and bottom, their curls shifting each frame. " +
     PAINT + ".",
     row(4, 16, 8) + CENTER),
    ("e_q_hit", "悚·阴沉变意：狞笑的鬼脸，6 帧", "view_effects `league_hwei_e_q_hit`（跟随目标，z 3；左右对称）", "24 × 24",
     "打中的敌人身前浮出一张**紫色颜料画的狞笑鬼脸**（参考 eq_mouth：两只歪着的眼睛、一张大大的弯嘴，**正面、左右对称**），"
     "脸一闪一闪，敌人被吓跑。**左右对称**，6 帧。",
     DR + ", " + IN,
     "A GRIM VISAGE, 6 frames, " + LR + ", " + TARGET + " (the face in front of its chest): a ghostly face painted with "
     "a few thick violet-magenta strokes, seen from the front: two slanted hollow eyes (each a curved stroke ring 4 "
     "squares across) and one huge grinning crescent mouth 14 squares wide with a few teeth, no outline of a head, "
     "dark indigo ink inside the eyes and the mouth; 1 strokes appearing; 2 the face whole; 3 the face 2 squares "
     "bigger, the eyes flashing magenta-white; 4 like 2; 5 the strokes breaking into drips; 6 a few violet drips "
     "falling. " + PAINT + ".",
     row(6, 24, 24) + CENTER),
    ("e_w_open", "悚·滞涩幽瞳：头上睁开的眼睛，8 帧", "view_effects `league_hwei_e_w_open`（跟随目标，z 3；左右对称）", "20 × 28",
     "目标头顶上方慢慢睁开一只**紫色的大眼睛**（参考 ew_eyeicon：一只竖着的眼，上下左右四道尖光），越睁越大，盯着它（约 0.65 秒）。**左右对称**，8 帧。",
     DR + ", " + IN,
     "AN EYE OPENING, 8 frames, " + LR + ", " + TARGET + " (its head at the bottom of the cell): above the head a painted "
     "almond-shaped eye seen from the front, 12 squares wide, its two lids violet strokes, the iris a magenta ring "
     "round a dark indigo pupil, a white highlight square, four thin violet rays (up, down, left, right) like a "
     "four-pointed star round it; 1 a closed lid line; 2-4 the lids opening wider; 5-8 the eye fully open, the iris "
     "glowing brighter each frame, the rays growing longer. " + PAINT + ".",
     row(8, 20, 28) + CENTER),
    ("e_w_hit", "悚·滞涩幽瞳：眼睛射下定身，5 帧", "view_effects `league_hwei_e_w_hit`（跟随目标，z 3；左右对称）", "20 × 40",
     "眼睛睁到最大，一道紫色的光柱从眼睛射到目标身上，脚下一圈紫色的颜料把它定住。**左右对称**，5 帧。",
     DR + ", " + IN,
     "THE GAZE STRIKING, 5 frames, " + LR + ", " + TARGET + " (feet on the bottom of the cell): 1 the eye at the top wide "
     "open, flashing magenta-white; 2 a violet beam 6 squares wide from the eye down to the feet; 3 the beam bright, "
     "a violet paint ring 18 wide and 5 tall splashed on the ground at the feet; 4 the beam thinning, the eye closing; "
     "5 only the ground ring and the eye's lid line. " + PAINT + ".",
     row(5, 20, 40) + CENTER),
    ("e_bound", "悚·定身：腿上缠的紫色颜料，4 帧循环", "view_buffs `league_hwei_e_bound`（跟随，z 3；左右对称）", "16 × 16",
     "被定住的敌人腿上：几道紫色的颜料笔触像藤一样缠住两条腿，脚下一滩墨。**左右对称**，4 帧循环。",
     DR + ", " + IN,
     "PAINT BINDING THE LEGS, 4 looping frames, " + LR + ": round the lower half of a standing unit (its legs in the "
     "middle, not drawn), three violet brush strokes wrapped like loose bands at 3 heights, each 12 squares wide and "
     "drawn as an ellipse arc (front half only), an indigo puddle under them; the bands pulse lighter and darker in "
     "turn through the frames. " + PAINT + ".",
     row(4, 16, 16) + CENTER),
    ("e_e_open", "悚·双钩血喉：獠牙张开，6 帧", "view_effects `league_hwei_e_e_open`（跟随目标，z 3；左右对称）", "28 × 24",
     "目标身边张开一张**紫红色颜料画的大嘴**：上下两排弯钩獠牙（参考 ee_teeth01），一左一右把它围住，越张越大（约 0.5 秒）。**左右对称**，6 帧。",
     DR + ", " + IN,
     "JAWS OPENING, 6 frames, " + LR + ", " + TARGET + ": a huge mouth painted round the unit, seen from the front: an "
     "upper row of 5 curved hook fangs hanging from a violet stroke above its head and a lower row of 5 fangs rising "
     "from a stroke at its feet, the fangs ivory-white with magenta tips, the gums dark violet, the inside of the mouth "
     "empty (the unit shows through); frame by frame the jaws open wider (from 8 to 20 squares apart), the fangs "
     "trembling. " + PAINT + ".",
     row(6, 28, 24) + CENTER),
    ("e_e_hit", "悚·双钩血喉：獠牙咬合，5 帧", "view_effects `league_hwei_e_e_hit`（跟随目标，z 3；左右对称）", "28 × 24",
     "大嘴猛地合上：上下獠牙咬在一起，溅出紫红色的颜料。**左右对称**，5 帧。",
     DR + ", " + IN,
     "JAWS SNAPPING SHUT, 5 frames, " + LR + ", " + TARGET + ": 1 the jaws (as in e_e_open) slamming together at the "
     "unit's middle, the fangs interlocking; 2 a magenta-white flash where they meet, violet paint splashing out to both "
     "sides; 3 the jaws shut, splashes 26 squares across; 4 the jaws breaking into violet strokes and drips; 5 a few "
     "drips falling. " + PAINT + ".",
     row(5, 28, 24) + CENTER),
    # ---- Serenity (folded into the passive)
    ("w_pool", "靖·渲浓：脚下的青蓝色水池，6 帧", "view_effects `league_hwei_w_pool`（大表，跟随他，z -1；左右对称）", "40 × 16",
     "放悚时他脚下化开一片**青蓝色的颜料水池**（参考 w_shield），一圈涟漪往外荡开，几片花瓣漂着（参考 petal2x2）。**左右对称**，6 帧。",
     CA,
     "A POOL OF REFLECTION, 6 frames, " + LR + ", " + HIM + ": " + FEET + ": 1 a teal splash 10 squares wide spreading "
     "under him; 2 a round pool of teal-blue paint 30 wide and 10 tall, a white highlight arc on its far edge; 3-4 a "
     "ripple ring travelling outward to 38 wide, two pale petals floating at mirrored places; 5 the pool fading at the "
     "edge; 6 a thin teal ring and the petals. " + PAINT + ".",
     row(6, 40, 16) + CENTER),
    ("w_shield", "靖·渲浓：队友身上的护盾，5 帧", "view_effects `league_hwei_w_shield`（跟随队友，z 3；左右对称）", "22 × 40",
     "队友身上罩上一层青蓝色的颜料光罩：一个椭圆的笔触圈从脚下升起包住身子，闪一下变淡。**左右对称**，5 帧。",
     CA,
     "A PAINTED SHIELD, 5 frames, " + LR + ", " + TARGET + ": 1 a teal ring on the ground at the feet; 2 the ring rising "
     "as a tall oval of teal-blue brush stroke round the unit (only the outline stroke, 3 squares thick, the middle "
     "empty); 3 the oval whole, a white highlight stroke on its upper left and its mirror on the upper right; 4 the "
     "stroke thinning; 5 a few teal specks. " + PAINT + ".",
     row(5, 22, 40) + CENTER),
    ("w_haste", "靖·飞染：脚下的青色笔触，4 帧循环", "view_buffs `league_hwei_w_haste`（跟随他，z -1；左右对称）", "24 × 8",
     "加速时他脚边：几道青蓝色的笔触往两边扫开，像风吹过水面。**左右对称**，4 帧循环。",
     CA,
     "A FLEETING CURRENT " + FEET + ", 4 looping frames, " + LR + ": four short teal-blue brush strokes, two on each side "
     "of the feet, sweeping outward along the ground, each 6 squares long, their dry-brush tails flicking further out "
     "frame by frame. " + PAINT + ".",
     row(4, 24, 8) + CENTER),
    # ---- ult: Spiraling Despair
    ("r_paint", "大招·焚心绚华绘：飞出去的颜料团，4 帧循环", "view_projectiles `league_hwei_r_paint`（弹道，z 2；上下对称）",
     "20 × 10",
     "一团旋转的颜料往前飞：深靛蓝的芯，外面绕着紫红和橙色的笔触，夹几缕金线。**朝右飞，上下对称**，4 帧循环。",
     IN + ", " + DR + ", " + FI + ", " + GO,
     "A SPIRALING PAINT BOLT, 4 looping frames, " + TB + ": a dark indigo ball 6 squares across with a magenta rim in "
     "front, round it two brush strokes - magenta and orange - spiralling into a tail 12 squares long, mirrored top and "
     "bottom, a gold strand between them; the spiral turns a quarter each frame. " + PAINT + ".",
     row(4, 20, 10) + CENTER),
    ("r_canvas", "大招·焚心绚华绘：展开的画卷，14 帧（3 秒）", "view_effects `league_hwei_r_canvas`（大表，地上不跟随，z -1；左右对称）",
     "56 × 22",
     "打中的地方地上展开一幅**旋转的画卷**：深靛蓝的底，紫红和橙色的笔触一圈圈往外旋，金线流动，越转越大（参考 r_cracks、goldstrand）。"
     "约 3 秒，最后几帧颜色越来越亮、快要炸开。**左右对称**，14 帧。",
     IN + ", " + DR + ", " + FI + ", " + GO,
     "A SPIRALING CANVAS painted on the ground, 14 frames, " + LR + ": an oval " + FEET + " growing from 20 squares wide "
     "(frame 1) to 52 wide and 17 tall (frame 6) and staying; a dark indigo ink ground, on it magenta and orange brush "
     "strokes curling round the middle in a mirrored double spiral, thin gold strands between them, cracks of light in "
     "the middle; through the frames the strokes turn and shimmer; frames 12-14 everything brighter, the cracks "
     "white-hot, as if about to burst. " + PAINT + ".",
     row(14, 56, 22) + CENTER),
    ("r_burst", "大招·焚心绚华绘：画卷爆炸，7 帧", "view_effects `league_hwei_r_burst`（大表，地上不跟随，z 3；左右对称）", "56 × 44",
     "画卷炸开：一大团紫红、橙色、靛蓝的颜料从地上炸起来，金线四射，颜料块往外甩。**左右对称**，7 帧。",
     IN + ", " + DR + ", " + FI + ", " + GO,
     "THE CANVAS EXPLODING, 7 frames, " + LR + ", the blast's base on the bottom middle of the cell: 1 a white-gold flash "
     "18 across on the ground; 2 a fountain of magenta, orange and indigo paint 30 wide shooting up 24 squares; 3 the "
     "burst 50 wide and 40 tall, gold strands flying out, paint blobs flung to both sides; 4 the paint falling in big "
     "drops; 5 dark indigo smoke-paint with orange embers; 6 drips and specks; 7 a few specks. " + PAINT + ".",
     row(7, 56, 44) + CENTER),
    ("r_hit", "大招：被炸到的颜料溅，4 帧", "view_effects `league_hwei_r_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被大招炸到的敌人身上：紫红和橙色的颜料溅开。**左右对称**，4 帧。",
     DR + ", " + FI,
     "A PAINT SPLASH ON A UNIT, 4 frames, " + LR + ": 1 a magenta-white flash 4 across; 2 magenta and orange paint "
     "splashing out 12 across at mirrored places; 3 drops further out; 4 a few drips. " + PAINT + ".",
     row(4, 14, 14) + CENTER),
]
BIG_FX = ["p_burst", "q_w_hit", "q_e_lava", "w_pool", "r_canvas", "r_burst"]
FLYING = ["a_ink", "q_q_ball", "e_q_face", "r_paint"]
FORWARD = []

GROUPS = [
    ("a_ink a_hit (brush, ink)", ["hwei_base_brushstroke01", "hwei_base_paintstrokediffuse", "hwei_base_dotsmol",
                                  "hwei_base_missilehead01"]),
    ("p_mark p_burst (the signature)", ["hwei_base_p_indicator01", "hwei_base_p_icon", "hwei_base_goldstrand01",
                                        "hwei_base_glow_ring"]),
    ("q_q_ball q_q_hit q_e_lava (fire, lava)", ["hwei_base_qe_firelicks", "hwei_base_groundcrack01base",
                                                "hwei_base_crackgroundslow01", "vgu_flameshape"]),
    ("q_w_tell q_w_hit (the bolt)", ["hwei_base_innerbolt", "hwei_base_goldstrandthin", "hwei_base_shape01",
                                     "hwei_base_tile05"]),
    ("e_q_face e_q_hit e_w_open e_w_hit", ["hwei_base_eq_mouth", "hwei_base_ew_eyeicon", "hwei_base_ew_pointer",
                                           "hwei_base_e_oilysmoke_erode"]),
    ("e_e_open e_e_hit e_bound slow", ["hwei_base_ee_teeth01", "hwei_base_paintstrokediffuse03",
                                       "hwei_base_generic_strokediffuse", "hwei_base_tile06"]),
    ("w_pool w_shield w_haste", ["hwei_base_w_shield", "hwei_base_petal2x2", "hwei_base_wave_vertical",
                                 "hwei_base_w_dash_sub"]),
    ("r_paint r_canvas r_burst r_hit", ["hwei_base_r_cracks", "hwei_base_paintstrokediffuse_rotate",
                                        "hwei_base_goldstrand01dissolve", "hwei_base_foundation_palette_ssgold"]),
]


def design_1x():
    """The idle at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / PPU, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Hwei at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"彗 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares (PPU 1.5)."""
    a = np.asarray(Image.open(RF.lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 异画师 彗：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/hwei_design.png`：瘦高的年轻画师，墨绿乱发、靛蓝外套和青绿翻领、"
      "橙色衬衫、一支红蓝笔头的大画笔斜指地面、背后一道弯月形的墨痕）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连墨痕 {h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/hwei_size.png`：彗放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里彗自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**彗是画家，所有特效都是颜料**：粗笔触、干笔的毛边、颜料团和颜料滴，不要光滑的霓虹能量。颜色按主题分：**灾（Q）红橙色的火焰颜料和金白色的雷**，"
      "**靖（并进被动）青蓝色**，**悚（E）紫红色**，**大招深靛蓝的底、紫红和橙色的笔触、金线**，**落款金色**；他自己的墨是靛蓝色。")
    a("> - **特效要亮**：每道颜料都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **颜料、光、雷、火都没有黑描边**（鬼脸、獠牙、眼睛也是颜料画的，不要描黑边）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像；鬼脸、眼睛、大嘴都画正面）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `hwei_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/hwei_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 画笔甩出一团墨 | `a_ink` · `a_hit` |")
    a("| 被动「落款」 | 伤害技能打中英雄留下落款，再打中一次就引爆 | `p_mark` · `p_burst` |")
    a("| 技能 1 =「主题：灾」 | 被控住的英雄 → 攒聚雷（金雷劈下）；有英雄 → 没骨火（火球）；清线清野 → 连皴山（熔岩地带，减速） | "
      "`q_w_tell` · `q_w_hit` · `q_q_ball` · `q_q_hit` · `q_e_lava` · `slow` |")
    a("| 技能 2 =「主题：悚」 | 贴脸的英雄 → 阴沉变意（狞笑鬼脸，恐惧）；否则轮流：滞涩幽瞳（头上睁眼，定身）/ 双钩血喉（獠牙咬合，定住减速） | "
      "`e_q_face` · `e_q_hit` · `e_w_open` · `e_w_hit` · `e_bound` · `e_e_open` · `e_e_hit` · `slow` |")
    a("| 被动里的「主题：靖」 | 每次放悚：渲浓（脚下水池，自己和队友护盾）；每次放灾：飞染（加速） | `w_pool` · `w_shield` · `w_haste` |")
    a("| 大招 =「焚心绚华绘」 | 颜料团飞向英雄，打中的地方展开旋转画卷（持续伤害、减速），3 秒后爆炸 | `r_paint` · `r_canvas` · "
      "`r_burst` · `r_hit` · `slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**颜料、光、雷、火没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **都是颜料**：粗笔触、干笔的毛边、颜料团和颜料滴；每段笔触 2–3 档平涂，亮的一边浅一档。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("灾·火焰颜料", FIRE), ("灾·金雷", BOLT), ("靖·青蓝", CALM), ("悚·紫红", DREAD), ("他的墨·靛蓝", INK),
                        ("落款·金色", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（落款印、熔岩、水池、画卷）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：画卷半径 25000，熔岩半径 20000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `hwei_fx_{name}.png`：{title}\n")
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
        a(f"| `hwei_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_hwei_fx`（小的）和 `league_hwei_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_hwei.py 的 views；q_q_ball2 用 q_q_ball，三种减速用 slow）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；q_w_tell、e_w_open 放在目标头顶（view 的 y 偏移），"
      "q_e_lava 帧长合计 2.5 秒、r_canvas 3 秒（r_t 180 tick），w_pool 跟随他。")
    a("- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="hwei_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "hwei_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_hwei.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "hwei_design.png"))
    shape = size_sheet(os.path.join(out, "design", "hwei_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"hwei_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
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
