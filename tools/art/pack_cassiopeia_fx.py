#!/usr/bin/env python3
"""Build cassiopeia_fx_pack.zip: step 3 of Cassiopeia's sprite - Codex draws her effects (pack_wukong_fx.py's way).

    python ../work/cs/fx_ref_cs.py            # League's particle textures -> C:/t/cs_work/fxref (Riot's art, local only)
    python tools/art/pack_cassiopeia_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name cassiopeia_fx_redo_pack]

The pack (C:/t/cs_work/fx/cassiopeia_fx_pack, zipped into --out, default dist/cassiopeia_packs) holds PROMPTS.md (also
written to assets/source/cassiopeia/PROMPTS_FX.md), design/cassiopeia_idle.png (her idle at 4x, the design's squares at
PPU 1.3), design/cassiopeia_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the
base fighter), design/cassiopeia_shots.png (the finished action frames the pictures start from, 4x) and
refs/lol_fx_ref.png (League's own particle textures for Cassiopeia grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_cassiopeia.py): view_projectiles a_fang, w_bolt, r_wave (turned
with their flight: drawn pointing right, symmetric top to bottom); view_effects a_hit, q_warn, q_blast, q_hit, w_land,
w_field, r_cast, r_hit; view_buffs w_slow (Miasma's slow and grounding), r_slow (the gaze's slow), r_stone (the
petrified). League's colours: Twin Fang and Noxious Blast a bright poison green with yellow-white cores, Miasma's clouds
a deeper green, Petrifying Gaze a gold-green light, the petrified grey stone.
Red side: the client never mirrors an effect picture, so every effect and buff picture is symmetric left to right; the
three projectiles point right and are turned with their flight (symmetric top to bottom, so turned they never stand
upside down).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
TMP = "C:/t/cs_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "cassiopeia", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_cassiopeia")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "cassiopeia_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


POISON = "#FFFFFF, #F2FFB8, #C6F05A, #84D23A, #3E9A30, #1D5A2A"     # Twin Fang, Noxious Blast
MIASMA = "#E6FFB4, #B4EC66, #78C846, #4C9C3E, #2E6E3C, #1A442E"     # Miasma's clouds
GAZE = "#FFFFFF, #FFF6C4, #FFE07A, #D6EA62, #8ACB4C, #3C7A38"       # Petrifying Gaze
STONE = "#F0ECE4, #CBC3B6, #A1978A, #786E64, #534B45, #322D2A"      # the petrified
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
PO = f"a bright poison-green ramp ({POISON})"
MI = f"a deep poison-green cloud ramp ({MIASMA})"
GA = f"a gold-green light ramp ({GAZE})"
ST = f"a grey stone ramp ({STONE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns "
      "it to its flight: flying left it is turned half round and must not stand upside down)")
CENTER = "; centered in every cell."
HER = ("the serpent woman stands in the middle, not drawn: 44 squares from her crest to the ground, her upper body about "
       "20 squares wide above her coiled neck, her head 30-44 squares above the ground")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack: E Twin Fang
    ("a_fang", "普攻双生毒牙：飞出去的毒牙（弹道），3 帧（循环）",
     "view_projectiles `league_cassiopeia_a_fang`（随飞行方向转；画成**朝右**、**上下对称**）", "12 × 8",
     "她每 0.75 秒甩出的一颗毒牙：一颗发亮的绿色**蛇牙形状的毒液弹**（像一颗弯弯的尖牙，尖头朝右），中间白色，后面拖一小段绿色的尾迹，"
     "旁边一两颗绿色毒滴（参考 Cass_SnakeHead_E、E_Cass_Greek_Fang、Cass_E_SnakeTrail）。**尖头朝右、上下对称**（游戏会按飞的方向"
     "转它，往左飞时转半圈，上下对称才不会倒过来）。约 12 × 8 格。",
     PO,
     f"a FLYING VENOM FANG, 3 frames, a seamless loop, {TB}: a glowing green fang-shaped venom bolt 7 squares long and 4 "
     "tall, its sharp tip at the right, a white core along its middle, a short green trail 4 squares behind it (to the "
     "left), two tiny green drops at mirrored places above and below the trail; each frame the trail flickers.",
     row(3, 12, 8) + CENTER),
    ("a_hit", "毒牙命中（目标身上），4 帧", "view_effects `league_cassiopeia_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "毒牙咬中目标：一团绿色的毒液四溅，中间白黄色的闪光，几道短短的绿色尖刺往外甩，几滴毒液（参考 cass_greek_fang_hit、"
     "E_Tar_Flash、E_Tar_Spikes）。**左右对称**。约 12 格。",
     PO,
     f"a VENOM BITE on a unit, 4 frames, {LR}: 1 a white-yellow flash 5 squares; 2 a green splash 10 squares with a "
     "white core, 4 short sharp green spikes flung out at mirrored angles; 3 the splash thinner and 12 squares, a few "
     "green drops at mirrored places; 4 fading drops.",
     row(4, 12, 12) + CENTER),
    # ---- Q Noxious Blast
    ("q_warn", "Q 瘟毒爆炸：落点预警（地上，不跟随，循环），4 帧",
     "view_effects `league_cassiopeia_q_warn`（不跟随，画在人物下面 z -2；左右对称；落下前 0.4 秒一直在放；大图表）", "46 × 18",
     "瘟毒爆炸落下前地上的预警圈：一个**扁椭圆的绿色细圈**（从斜上方看的圆），圈里几道向中间收的短线，一闪一闪（参考 Q_Target、"
     "Q_Hit_Poison_Ring）。**只有圈，中间不填满**（敌人站在里面要看得见）。**左右对称**。",
     PO,
     f"A GROUND TARGET RING seen from above at an angle, 4 frames, a seamless loop, {LR}: a thin bright green ellipse 42 "
     "squares wide and 14 tall, 1 square thick (a lighter top edge), 6 short dashes inside it pointing at the middle "
     "(mirrored), the middle left empty; 1 dim; 2 brighter; 3 brightest with a white glint on the ring's top; 4 like 2.",
     row(4, 46, 18) + "; centered across, the ellipse's middle 9 squares above the cell's bottom row."),
    ("q_blast", "Q 瘟毒爆炸：落地炸开的毒爆（地上，不跟随），6 帧",
     "view_effects `league_cassiopeia_q_blast`（不跟随，画在人物上面 z 2；左右对称；大图表）", "48 × 40",
     "毒爆落地：地上猛地炸开一团绿色的毒液（几个鼓起来的毒泡破开），一圈扁的绿色冲击环往外扩，一团团绿色毒烟往上冒，几道毒液丝往外甩，"
     "然后毒烟慢慢散开（参考 Q_Hit_slam02、Q_Hit_Smoke_Clouds、Q_tar_cloud、Q_Hit_strands、Q_Hit_PoisonRing_Pulse）。**左右对称**，"
     "落点在格子中间偏下。",
     PO,
     f"A POISON BLAST bursting out of the ground seen from above at an angle, 6 frames, {LR}: 1 a white-green flash on "
     "the ground 10 squares wide; 2 bubbling green poison bursting up (round bubbles 3-6 squares, white highlights) 20 "
     "squares wide and 16 tall, a flat green shock ring on the ground (an ellipse 30 wide and 8 tall); 3 the ring 44 wide "
     "and 12 tall, green poison smoke puffs rising 26 squares, thin poison strands flung out at mirrored angles; 4 the "
     "smoke 32 squares tall, opening; 5 the smoke thinning and drifting out at both sides; 6 faint wisps and drops.",
     row(6, 48, 40) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("q_hit", "Q 中毒（目标身上），4 帧", "view_effects `league_cassiopeia_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "被瘟毒爆炸毒到的敌人身上冒出一小团绿色毒气，几个往上飘的毒泡（参考 Q_Hit_Gen_Orb01、Q_Hit_ball32、Q_Hit_color-poison_bell）。"
     "**左右对称**。约 14 格。",
     PO,
     f"POISONED: a puff on a unit, 4 frames, {LR}: 1 a small green puff 6 squares with a white-yellow core; 2 the puff 11 "
     "squares, 3 round green bubbles rising from it at mirrored places; 3 the bubbles higher, the puff thinning; 4 two "
     "small bubbles and wisps.",
     row(4, 14, 14) + CENTER),
    # ---- W Miasma
    ("w_bolt", "W 剧毒迷雾：飞出去的毒液弹（弹道），3 帧（循环）",
     "view_projectiles `league_cassiopeia_w_bolt`（随飞行方向转；画成**朝右**、**上下对称**）", "10 × 8",
     "她甩出去的毒液弹：一颗圆圆的深绿色毒液球，亮绿色的芯，后面拖一小段毒液尾巴（参考 W_Acidball_Color、W_Head_Lead_V3、"
     "W_Meteor_Tail）。**朝右、上下对称**。约 10 × 8 格。",
     MI,
     f"A FLYING ACID BALL, 3 frames, a seamless loop, {TB}: a round green poison ball 5 squares across (a bright green "
     "core with a white glint in the middle row), a short tapering green tail 4 squares behind it (to the left), two tiny "
     "drops at mirrored places above and below the tail; each frame the tail wobbles.",
     row(3, 10, 8) + CENTER),
    ("w_land", "W 毒液落地（地上，不跟随），4 帧",
     "view_effects `league_cassiopeia_w_land`（不跟随，画在人物下面 z -1；左右对称；大图表）", "40 × 16",
     "毒液弹落地：地上啪地溅开一滩绿色毒液（扁椭圆），几滴往外溅，冒出第一团毒雾（参考 W_Splat、W_Spit、W_Color_Texture_Splash）。"
     "**左右对称**。",
     MI,
     f"A POISON SPLAT on the ground seen from above at an angle, 4 frames, {LR}: 1 a white-green flash 8 squares wide on "
     "the ground; 2 a green splat (a flat ellipse 24 squares wide and 6 tall with ragged edges) and drops flung out at "
     "mirrored places; 3 the splat 34 wide and 9 tall, a first low green mist rising 4 squares; 4 the splat settling, "
     "the drops gone.",
     row(4, 40, 16) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("w_field", "W 剧毒迷雾：地上的毒雾（地上，不跟随，每 1/4 秒接着放），4 帧",
     "view_effects `league_cassiopeia_w_field`（不跟随，画在人物下面 z -1；左右对称；5 秒内每 15 tick 再放一次：4 帧连起来要能无缝"
     "接上；大图表）", "64 × 28",
     "地上一大片低低的深绿色毒雾：几团圆滚滚的毒雾团（扁的，贴着地面），里面几个冒泡的毒泡，雾团慢慢翻滚（参考 W_Poison_Cloud_Shapes、"
     "W_Greek_PoisonPool_Color、W_voidooze_bubbles、W_Smoke_Color）。**雾要低、要透**：雾团之间留空隙、中间偏下最浓，"
     "**站在里面的人上半身要看得见**（雾高不超过 14 格）。**左右对称**，第 4 帧要能接回第 1 帧。",
     MI,
     f"A LOW POISON MIASMA lying on the ground seen from above at an angle, 4 frames, a seamless loop (frame 4 flows back "
     f"into frame 1), {LR}: a field of flat rounded green poison cloud puffs (each 8-14 squares wide and 4-7 tall, a "
     "lighter top, a darker underside, no outline) filling an ellipse 60 squares wide and 18 tall, at most 14 squares "
     "high, with gaps between the puffs (units standing in it must stay visible), 4-6 small round poison bubbles rising "
     "and popping in it at mirrored places; each frame the puffs roll a square along the ring.",
     row(4, 64, 28) + "; centered across, the ellipse's middle 9 squares above the cell's bottom row."),
    ("w_slow", "W 减速 + 禁锢（敌人脚下，循环），4 帧",
     "view_buffs `league_cassiopeia_w_slow`（跟随，画在人物上面；左右对称；循环）", "20 × 12",
     f"在毒雾里被减速、不能用位移技能的敌人：脚下一圈绿色毒液缠着双脚（扁的毒液环），几个小毒泡往上冒（{CHAMP}，只画在他脚下，"
     "不要盖住身体）。**左右对称**。",
     MI,
     f"POISON AT A UNIT'S FEET, 4 frames, a seamless loop, {LR} ({CHAMP}): a flat green poison ring round its feet (an "
     "ellipse 16 squares wide and 5 tall, 2 squares thick, a lighter top edge), 3 tiny bubbles rising from it at "
     "mirrored places; each frame the bubbles rise a square and pop; nothing above 8 squares.",
     row(4, 20, 12) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
    # ---- R Petrifying Gaze
    ("r_cast", "R 石化凝视：她的眼睛放光（她身上，跟随），4 帧",
     "view_effects `league_cassiopeia_r_cast`（跟随，画在人物上面 z 3；左右对称；大图表）", "28 × 56",
     f"她放大招时眼睛和头上猛地亮起金绿色的光：她的头上一团金绿色的光芒，几道放射状的光线往四周射，额头位置一颗白色的亮星"
     f"（参考 R_cass_ult_eye、R_Flare-Sun_05、R_Light_Rays_01）。**左右对称**，光芒在她头的高度（{HER}），身体留空不画。",
     GA,
     f"A GLARE OF LIGHT round a figure's head, 4 frames, {LR} ({HER}): the light's middle 37 squares above the ground; 1 a "
     "white star 4 squares; 2 a gold-green burst 14 squares with a white core, 8 thin light rays shooting out in a star "
     "(mirrored); 3 the rays 24 squares across, thinner; 4 fading rays and a few sparkles; nothing below 26 squares.",
     row(4, 28, 56) + "; centered across, the figure's ground 2 squares above the cell's bottom row."),
    ("r_wave", "R 石化凝视：往前推出去的凝视波（弹道），4 帧（循环）",
     "view_projectiles `league_cassiopeia_r_wave`（随飞行方向转；画成**朝右**、**上下对称**；大图表）", "24 × 40",
     "从她眼睛里推出去的石化凝视：一道**向右凸的弧形金绿色光波**（像一个月牙，凸面朝右），光波上有几道往右的光束，中间最亮是白色，"
     "后面拖几道淡淡的光线（参考 R_Lightbeam、R_lightbeams、R_Aoe_Decal_side）。**朝右、上下对称**（游戏按飞的方向转它）。",
     GA,
     f"A WAVE OF PETRIFYING LIGHT, 4 frames, a seamless loop, {TB}: a crescent-shaped gold-green light wave 34 squares "
     "tall and 6 thick, bulging to the RIGHT, a white core along its middle, 5 short light beams pointing right out of "
     "its front at mirrored heights, faint trailing light streaks to the left; each frame the beams flicker and the "
     "crescent shimmers.",
     row(4, 24, 40) + CENTER),
    ("r_hit", "R 命中（目标身上），4 帧", "view_effects `league_cassiopeia_r_hit`（跟随，画在人物上面；左右对称）", "16",
     "被凝视扫中：一圈金绿色的闪光，几块灰色的小石屑往外崩（参考 R_Stone_Mult、Cassiopeia_Base_rock_debris、Hit_1）。"
     "**左右对称**。约 16 格。",
     f"{GA} and {ST}",
     f"A GAZE HIT on a unit, 4 frames, {LR}: 1 a gold-white flash 6 squares; 2 a gold-green burst 12 squares with a "
     "white core, 4 small grey stone chips (2x2 squares, a dark edge: solid) flying out at mirrored places; 3 the burst "
     "a thin ring 15 squares, the chips farther; 4 fading chips.",
     row(4, 16, 16) + CENTER),
    ("r_stone", "R 石化（被石化的敌人身上，循环），4 帧",
     "view_buffs `league_cassiopeia_r_stone`（跟随，画在人物上面 z 2；左右对称；循环，石化 2 秒内一直在）", "24 × 44",
     f"面朝她被石化的敌人：从脚往上长出一层**灰色的石壳**，把他的腿和腰包住（石块一块块的，亮面朝上，有裂纹），肩膀和头上落着几块石屑，"
     f"一闪一闪的白色高光（参考 Death_stonecass、R_Stone_Mult、rock_debris）。**左右对称**（{CHAMP}；石壳包住他下半身——从地面到"
     "18 格高，上半身只有零散的石片，脸要看得见）。",
     ST,
     f"A STONE CRUST over a unit, 4 frames, a seamless loop, {LR} ({CHAMP}): grey stone blocks (a light top face, a "
     "darker side, a 1-square dark outline: solid, with a few cracks) wrapping its legs and waist from the ground up to 18 "
     "squares high (the crust 20 squares wide at the ground, 16 at its top), a few loose stone chips (2x2 squares) on its "
     "shoulders and head at mirrored places, the face and chest left clear; each frame a white glint moves over the "
     "blocks.",
     row(4, 24, 44) + "; centered across, the unit's feet 2 squares above the cell's bottom row."),
    ("r_slow", "R 减速（背对她的敌人脚下，循环），4 帧",
     "view_buffs `league_cassiopeia_r_slow`（跟随，画在人物上面；左右对称；循环）", "20 × 12",
     f"背对她、只被减速的敌人：脚下一圈淡淡的金绿色光环，几颗灰色的小石屑在光环上（{CHAMP}，只画在他脚下）。**左右对称**。",
     f"{GA} and {ST}",
     f"A SLOWING RING at a unit's feet, 4 frames, a seamless loop, {LR} ({CHAMP}): a thin gold-green ellipse 16 squares "
     "wide and 5 tall round its feet (1 square thick, a lighter top), 4 tiny grey stone chips on it at mirrored places "
     "(1x1 or 2x1 squares, a dark edge); each frame a white glint moves along the ring; nothing above 8 squares.",
     row(4, 20, 12) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
]
BIG_FX = ["q_warn", "q_blast", "w_land", "w_field", "r_cast", "r_wave"]
REDO = {}
GROUPS = [
    ("a_fang a_hit", ["Cass_SnakeHead_E", "Cassiopeia_Base_E_Cass_Greek_Fang", "Cassiopeia_Base_E_Cass_Greek_Fang_Trail",
                      "Cass_E_SnakeTrail", "cass_greek_fang_hit", "Cassiopeia_Base_E_Tar_Flash",
                      "Cassiopeia_Base_E_Tar_Spikes"]),
    ("q_warn q_blast q_hit", ["Cassiopeia_Base_Q_Target", "Cassiopeia_Base_Q_Hit_Poison_Ring",
                              "Cassiopeia_Base_Q_Hit_slam02", "Cassiopeia_Base_Q_Hit_Smoke_Clouds_2x2_HC",
                              "Cassiopeia_Base_Q_tar_cloud", "Cassiopeia_Base_Q_Hit_strands",
                              "Cassiopeia_Base_Q_Hit_Gen_Orb01"]),
    ("w_bolt w_land w_field w_slow", ["Cassiopeia_Base_W_Acidball_Color", "Cassiopeia_Base_W_Head_Lead_V3",
                                      "Cassiopeia_Base_W_Splat", "Cassiopeia_Base_W_Poison_Cloud_Shapes",
                                      "Cassiopeia_Base_W_Greek_PoisonPool_Color", "Cassiopeia_Base_W_voidooze_bubbles",
                                      "Cassiopeia_Base_W_Smoke_Color"]),
    ("r_cast r_wave", ["Cassiopeia_Base_R_cass_ult_eye", "Cassiopeia_Base_R_Flare-Sun_05",
                       "Cassiopeia_Base_R_Light_Rays_01", "Cassiopeia_Base_R_Lightbeam", "Cassiopeia_Base_R_lightbeams",
                       "Cassiopeia_Base_R_Aoe_Decal_side"]),
    ("r_hit r_stone r_slow", ["Cassiopeia_Base_R_Stone_Mult", "Cassiopeia_Base_Death_stonecass",
                              "Cassiopeia_Base_rock_debris", "Cassiopeia_Base_R_Aoe_Dissolve", "Cassiopeia_Base_Hit_1"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_fang：毒牙从前面的爪子飞出；a_hit 打在目标身上"),
         ("skill", 3, "q_warn / q_blast：Q 落在目标脚下；q_hit 毒到的敌人"),
         ("skill2", 3, "w_bolt：毒液弹飞出；w_land / w_field 落在远处的地上；w_slow 在敌人脚下"),
         ("ult", 1, "r_cast：她的眼睛和头上放光"), ("ult", 3, "r_wave：凝视波往前推；r_hit / r_stone / r_slow 在敌人身上"),
         ("idle", 1, "待机（大小参考）")]


def ref_sheet(path):
    S, LW = 170, 200
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                cand = [f for f in os.listdir(REF) if f.startswith(nm)]
                if not cand:
                    sys.exit(f"missing reference {p}")
                p = os.path.join(REF, sorted(cand)[0])
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Cassiopeia_Base_", "").replace("Cassiopeia_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    anims = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(SHEET + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def first_1x(tag):
    f = sheet_frames(tag)[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    import tfm2_ase as T
    figs = [first_1x("idle")]
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
    d.text((8, 36), f"卡西奥佩娅 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is her pivot, FEET rows over the ground
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 440), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    cols = 4
    rows_ = (len(tiles) + cols - 1) // cols
    cw = max(t.width for t in tiles) + 10
    ch = max(t.height for t in tiles) + 10
    sheet = Image.new("RGB", (cols * cw, rows_ * ch), (60, 64, 50))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % cols) * cw, (i // cols) * ch))
    sheet.save(path)


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.3: 1.3 squares a game pixel)."""
    import rig_cassiopeia as M
    F = M.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 魔蛇之拥 卡西奥佩娅：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/cassiopeia_idle.png`：3/4 正面朝右的蛇身女人，金边翠绿蛇冠、"
      f"额头蓝宝石、紫眼影、金爪手套、金色胸衣和腰带，下半身是深绿色的蛇尾，蛇尾平铺在身后往左伸）。她在游戏里是**高清**的（每个游戏格子"
      f"里 1.3×1.3 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/cassiopeia_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/cassiopeia_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡西奥佩娅自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效"
      "分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**双生毒牙和瘟毒爆炸是亮的毒绿色（芯是白黄色）**，**剧毒迷雾是深一点的绿色毒雾**，"
      "**石化凝视是金绿色的光**，**被石化是灰色的石头**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（`r_stone` 例外：石壳就是要包住他的下半身）。")
    a("> - **三张弹道图（`a_fang`、`w_bolt`、`r_wave`）画成朝右飞、上下对称**：游戏会按飞的方向把它转过去，往左飞时转半圈，上下对称才不会"
      "倒过来。**其余所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 14]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `cassiopeia_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/cassiopeia_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 = E「双生毒牙」 | 每 0.75 秒甩出一颗追踪的毒牙，打中毒的目标伤害更高、给她回血 | `a_fang` · `a_hit` |")
    a("| 技能 1 = Q「瘟毒爆炸」 | 往目标脚下放，0.4 秒后炸开，范围里的敌人中毒 3 秒；打中英雄她加移速 | `q_warn` · `q_blast` · `q_hit` |")
    a("| 技能 2 = W「剧毒迷雾」 | 甩出毒液弹，落地后留下一片 5 秒的毒雾：持续掉血、减速、不能用位移技能 | `w_bolt` · `w_land` · `w_field` · "
      "`w_slow` |")
    a("| 大招「石化凝视」 | 眼睛放光，往面前扇形推出凝视波：面朝她的敌人石化 2 秒，背对她的减速 | `r_cast` · `r_wave` · `r_hit` · "
      "`r_stone` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、毒液、毒雾、毒泡、光环、光波都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：石壳、石屑可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("亮毒绿（毒牙、瘟毒爆炸）", POISON), ("深毒绿（剧毒迷雾）", MIASMA), ("金绿色的光（石化凝视）", GAZE),
                        ("灰色石头（石化）", STONE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：瘟毒爆炸的半径 22000，剧毒迷雾的半径 "
      "30000，凝视的扇形 72000 长、左右各 40 度）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `cassiopeia_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `cassiopeia_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_cassiopeia_fx`（小的）和 `league_cassiopeia_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_cassiopeia.py 的 views）。")
    a("- `q_warn` 在落下前的 24 tick 里循环；`w_field` 每 15 tick 再放一次（4 帧共 250 毫秒），5 秒里接成一片；`q_blast`、`w_land`、"
      "`w_field` 不跟随（地上的点）。弹道图朝右、上下对称（随飞行转）；其余全部左右对称。")
    a("- 用 `pixel_1x/` 切格（import_maokai_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（石壳、石屑保留描边）；核对交回的张数和"
      "这份清单；和 `raw/` 原稿对照读回（普朗克的教训：Codex 自己的 1 倍图可能洗白颜色，必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="cassiopeia_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "cassiopeia_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run ../work/cs/fx_ref_cs.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "cassiopeia_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "cassiopeia_size.png"))
    shots_sheet(os.path.join(out, "design", "cassiopeia_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"cassiopeia_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
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
