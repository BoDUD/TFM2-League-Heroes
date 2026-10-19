#!/usr/bin/env python3
"""Build yuumi_fx_pack.zip: step 3 of Yuumi's sprite - Codex draws her effects (pack_zoe_fx.py's way, pack_rammus_fx's
sheets reused).

    python <scratchpad>/fx_ref_yu.py           # League's particle textures -> C:/t/yu_work/fxref (Riot's art, local only)
    python tools/art/pack_yuumi_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name yuumi_fx_redo_pack]

The pack (C:/t/yu_work/fx/yuumi_fx_pack, zipped into --out, default dist/yuumi_packs) holds PROMPTS.md (also written to
assets/source/yuumi/PROMPTS_FX.md), design/yuumi_idle.png (her idle at 4x, the design's squares at PPU 1.5),
design/yuumi_size.png (her idle as the game shows it - 75 %, 24 game px - at 4x on the arena colour with the ground line,
a 10-px ruler and the base fighter), design/yuumi_shots.png (the finished action frames the pictures start from, as the
game shows them, 4x) and refs/lol_fx_ref.png (League's own particle textures for Yuumi grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_yuumi.py): view_projectiles a_bolt, q_missile, r_wave;
view_effects a_hit, p_hit, p_heal, q_hit, q_ehit, e_hit, w_heal, w_jump, w_land, r_cast, r_hit, r_heal; view_buffs
e_haste, q_slow, q_eslow, r_root (w_ride, the cat on the ally's head, is its own pack: pack_yuumi_ride.py). League's
colours: gold starlight sparkles, pink-violet magic, pink hearts for her heals. Red side: the client never mirrors an
effect picture, so every hit, buff and ground picture is symmetric left to right; a projectile's picture is turned with
its flight (drawn flying right, the trail behind it on the left), so it is symmetric top to bottom instead.
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

TMP = "C:/t/yu_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "yuumi", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_yuumi")
NAME = "yuumi_fx_pack"
SHOWN = 0.75            # hd.rs SIZES: the game draws her at 75 %
PPU = 1.5

GOLD = "#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210"       # gold starlight sparkles
MAGIC = "#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488"      # pink-violet magic
HEART = "#FFFFFF, #FFE4EE, #FF9EC4, #F0628E, #C03A6A, #6E1E3E"      # pink hearts (her heals)
GO = f"a gold starlight ramp ({GOLD})"
MA = f"a pink-violet magic ramp ({MAGIC})"
HE = f"a pink heart ramp ({HEART})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, energy, sparkles, hearts, waves, rings or magic circles")
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
CHAMP = RF.CHAMP
HER = "the small cat in her book stands in the middle, not drawn: 24 squares from the top of her antenna to the ground, about 22 squares wide"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack and Feline Friendship
    ("a_bolt", "普攻：书页光弹（弹道，循环），4 帧",
     "view_projectiles `league_yuumi_a_bolt`（跟着弹道转向；上下对称）", "10 × 8",
     "她普攻弹出去的小光弹：一颗粉紫色的小魔法球，白芯，后面拖一小串金色的星点（参考 core、sparkle、z_spark）。"
     "**朝右飞，尾巴在左边，上下严格对称**（游戏按飞行方向转这张图，往左飞时是倒过来的），4 帧循环。",
     f"{MA} and {GO}",
     "A LITTLE MAGIC BOLT, 4 frames, a seamless loop, " + TB + ": a round pink-violet orb 4 squares across with a white core "
     "at the right, a short trail of 3-4 gold sparkle squares behind it to the left; each frame the core flickers and the "
     "sparkles shift.",
     row(4, 10, 8) + "; the orb's middle on the cell's middle row, 3 squares from its right edge."),
    ("a_hit", "普攻：光弹打中目标，3 帧", "view_effects `league_yuumi_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "光弹打中的一下：一团粉紫色的小闪光，四周溅出几粒金色的星点（参考 e_flash、z_spark）。**左右对称**，约 12 × 12 格。",
     f"{MA} and {GO}",
     "A SMALL MAGIC HIT, 3 frames, " + LR + ": 1 a white-pink four-pointed flash 6 squares across; 2 the flash 9 across "
     "with 6 gold sparkle squares flying out; 3 only the sparkles further out, fading.",
     row(3, 12, 12) + CENTER),
    ("p_hit", "猫的博爱：强化普攻打中，4 帧", "view_effects `league_yuumi_p_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "被动「猫的博爱」那一下：一颗金白色的星形闪光，中间冒出一个粉色的小爱心，一圈金色、粉紫色的星点往外散（参考 ba_tar_star、"
     "z_scribbles 的爱心、sparkle）。**左右对称**，约 16 × 16 格。",
     f"{GO}, {HE} and {MA}",
     "A STAR-AND-HEART BURST, 4 frames, " + LR + ": 1 a white-gold star flash 8 squares across; 2 the flash 12 across with a "
     "small pink heart (5 squares wide) in its middle; 3 a ring of 8 gold and pink-violet sparkles 15 across, the heart "
     "rising a square; 4 only twinkling sparkles at the edge.",
     row(4, 16, 16) + CENTER),
    ("p_heal", "猫的博爱：她自己回血（她身上，跟随），4 帧", "view_effects `league_yuumi_p_heal`（跟随，画在人物上面 z 2；左右对称）",
     "18 × 20",
     "被动给自己（附身时也给队友）回血：几个粉色的小爱心和金色星点从她身边慢慢往上飘（参考 z_scribbles 的爱心、p_glow、sparkle）。"
     "**围着人画，身体位置留空**，**左右对称**，4 帧。",
     f"{HE} and {GO}",
     "HEALING HEARTS round a small unit, 4 frames, " + LR + " (" + HER + "): 1 two small pink hearts (3 squares wide) low at "
     "her left and right; 2 the hearts 4 squares higher, two gold sparkles above them; 3 the hearts higher still and a third "
     "heart at the top middle, more sparkles; 4 the hearts near the top, fading, the sparkles twinkling out.",
     row(4, 18, 20) + "; centered across, the middle of the cell on her middle."),
    # ---- Q Prowling Projectile
    ("q_missile", "Q 摸鱼飞弹：飞弹（弹道，循环），4 帧",
     "view_projectiles `league_yuumi_q_missile`（跟着弹道转向；上下对称）", "16 × 10",
     "她甩出去的摸鱼飞弹：一颗粉紫色的魔法光球，白芯外面一圈粉紫色的光晕，后面拖一条长长的金色星光尾巴（参考 q_flash、e_flash、"
     "wisptrail_add、sparkle）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     f"{MA} and {GO}",
     "A PROWLING MAGIC MISSILE, 4 frames, a seamless loop, " + TB + ": a round pink-violet orb 6 squares across with a white "
     "core inside a soft pink glow ring at the right, a tapering trail of gold starlight squares 9 squares long behind it to "
     "the left, widest next to the orb; each frame the core pulses and the trail's sparkles drift.",
     row(4, 16, 10) + "; the orb's middle on the cell's middle row, 4 squares from its right edge."),
    ("q_hit", "Q：飞弹打中，4 帧", "view_effects `league_yuumi_q_hit`（跟随目标，画在人物上面 z 2；左右对称）", "18 × 18",
     "飞弹打中目标：一团粉紫色的闪光，一圈粉紫色的魔法环炸开，几粒金色星点往外飞（参考 q_flash、e_ring、z_spark）。"
     "**左右对称**，约 18 × 18 格。",
     f"{MA} and {GO}",
     "A MAGIC IMPACT, 4 frames, " + LR + ": 1 a white-pink flash 8 squares across; 2 the flash 12 across and a thin "
     "pink-violet ring 14 across; 3 the ring 18 across, 6 gold sparkles flying out; 4 only fading sparkles and a faint ring.",
     row(4, 18, 18) + CENTER),
    ("q_ehit", "Q：飞了很远的强化命中，4 帧", "view_effects `league_yuumi_q_ehit`（跟随目标，画在人物上面 z 2；左右对称）", "24 × 24",
     "飞弹飞得够久、强化打中：比普通命中更大更亮，金白色的星形大闪光，一圈粉紫色的魔法环和一圈金色星点同时炸开（参考 qbv2_gold、"
     "fire_tile_gold、q_flash、ba_tar_star）。**左右对称**，约 24 × 24 格。",
     f"{GO} and {MA}",
     "A BIG EMPOWERED IMPACT, 4 frames, " + LR + ": 1 a white-gold star flash 10 squares across with 4 long rays; 2 the flash "
     "16 across inside a pink-violet ring 18 across; 3 the ring 22 across and a ring of 8 gold sparkles outside it; 4 only "
     "twinkling sparkles and a faint ring.",
     row(4, 24, 24) + CENTER),
    ("q_slow", "Q：减速（脚下，循环），4 帧", "view_buffs `league_yuumi_q_slow`（跟随，画在人物下面 z 1；左右对称；循环）", "16 × 6",
     "被飞弹减速：敌人脚下贴着地面一小圈粉紫色的魔法光点慢慢转（参考 e_ring、sparkle）。**只画在脚下的地面上**，**左右对称**，4 帧循环。",
     MA,
     "A SLOWING RING on the ground at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat ellipse 14 squares wide and "
     "4 tall drawn only as short pink-violet light streaks (1-3 squares) and a few white sparkle squares, mirrored; each frame "
     "the streaks move round the ellipse.",
     row(4, 16, 6) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    ("q_eslow", "Q：强化减速（脚下，循环），4 帧", "view_buffs `league_yuumi_q_eslow`（跟随，画在人物下面 z 1；左右对称；循环）",
     "20 × 8",
     "强化命中后的大减速：脚下更大更亮的一圈，粉紫色的光环里夹着金色星点（参考 e_ring、qbv2_gold）。**只画在脚下的地面上**，"
     "**左右对称**，4 帧循环。",
     f"{MA} and {GO}",
     "A STRONG SLOWING RING on the ground at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat ellipse 18 squares "
     "wide and 6 tall: a thin pink-violet light ring with 6 gold sparkle squares on it at mirrored places; each frame the "
     "sparkles move round the ring and the ring brightens and dims.",
     row(4, 20, 8) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- W You and Me! + E Zoomies
    ("e_hit", "W+E：旺盛精力给到队友（他身上），5 帧", "view_effects `league_yuumi_e_hit`（跟随，画在人物上面 z 2；左右对称）",
     "28 × 36",
     "她附身时把「旺盛精力」给队友：队友身上闪起一个金色的护盾泡（只画外圈），两边对称地划过几道金色、粉紫色的速度线，护盾泡收成星点"
     "（参考 wv3_shield_trail、e_streak、e_flash）。**围着人画，身体位置留空**，**左右对称**，5 帧。",
     f"{GO} and {MA}",
     "A SHIELD-AND-SPEED BURST round an ally, 5 frames, " + LR + " (" + CHAMP + "): 1 a thin gold shield outline (an upright "
     "oval 22 squares wide and 32 tall, only its rim, 1-2 squares thick) appearing; 2 the rim bright with white highlight "
     "squares and 4 gold and pink-violet speed streaks (6-8 squares long) flashing up at its left and right; 3 the rim "
     "pulsing, the streaks higher; 4 the rim breaking into gold sparkles; 5 only sparkles drifting up.",
     row(5, 28, 36) + "; centered across, the cell's bottom on the ground."),
    ("e_haste", "W+E：加速（他脚下，循环），4 帧", "view_buffs `league_yuumi_e_haste`（跟随，画在人物下面 z -1；左右对称；循环）",
     "26 × 8",
     "旺盛精力的攻速移速：队友脚下贴着地面转的一圈金色、粉紫色的星光条纹（参考 e_streak、wisptrail_add、sparkle）。"
     "**只画在脚下的地面上**，**左右对称**，4 帧循环。",
     f"{GO} and {MA}",
     "A SPEED SWIRL on the ground at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat ellipse 24 squares wide and "
     "6 tall drawn only as short curved streaks (2-4 squares long) of gold and pink-violet light, mirrored, with a few white "
     "sparkle squares; each frame the streaks move round the ellipse.",
     row(4, 26, 8) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    ("w_heal", "W：附身期间队友回血（他身上），4 帧", "view_effects `league_yuumi_w_heal`（跟随，画在人物上面 z 2；左右对称）",
     "16 × 18",
     "她趴在队友头上时，队友每秒回一点血：两三个粉色的小爱心从他胸口往上冒，带几粒金色星点（参考 z_scribbles 的爱心、sparkle）。"
     "**左右对称**，4 帧。",
     f"{HE} and {GO}",
     "SMALL HEALING HEARTS on an ally, 4 frames, " + LR + ": 1 one pink heart 3 squares wide at the middle; 2 two hearts "
     "rising at mirrored places, two gold sparkles; 3 the hearts higher, a third small heart; 4 the hearts fading at the top, "
     "sparkles twinkling out.",
     row(4, 16, 18) + CENTER),
    ("w_jump", "W：她跳走的地方（地上，不跟随），4 帧", "view_effects `league_yuumi_w_jump`（不跟随，画在人物下面 z 2；左右对称）",
     "18 × 14",
     "她扑向队友时原地留下的一下：一团粉紫色、金色的星光小爆，几粒星点往上飘（参考 e_flash、sparkle、smokeerode）。"
     "**左右对称**，4 帧。",
     f"{MA} and {GO}",
     "A SPARKLE PUFF where a small unit leaps away, 4 frames, " + LR + ": 1 a pink-white flash 8 squares across low over the "
     "ground; 2 a puff of pink-violet glow 14 across with 6 gold sparkles; 3 the sparkles drifting up and out, the glow "
     "thinner; 4 only a few sparkles high up.",
     row(4, 18, 14) + "; centered across, the puff's bottom 1 square above the cell's bottom row."),
    ("w_land", "W：她从队友身上跳下来落地（地上，不跟随），4 帧", "view_effects `league_yuumi_w_land`（不跟随，画在人物下面 z 2；左右对称）",
     "20 × 12",
     "附身结束、她跳下来落地：脚下一圈金色、粉紫色的星点往两边溅开，一道扁扁的光环（参考 e_ring、sparkle）。**左右对称**，4 帧。",
     f"{GO} and {MA}",
     "A LANDING SPARKLE on the ground, 4 frames, " + LR + ": 1 a flat white-gold flash 10 squares wide and 3 tall on the "
     "ground; 2 a flat pink-violet ring 16 wide and 4 tall, 6 gold sparkles splashing out to the left and right; 3 the ring "
     "20 wide and fainter, the sparkles further out; 4 only a few sparkles.",
     row(4, 20, 12) + "; centered across, the ring's bottom on the cell's bottom row."),
    # ---- R Final Chapter
    ("r_cast", "R 魔典终章：翻开魔典时脚下的魔法阵（跟随，大图表），6 帧",
     "view_effects `league_yuumi_r_cast`（跟随，画在人物下面 z -1；左右对称；大图表）", "40 × 20",
     "她把书立起来放大招：脚下的地面上展开一个粉紫色和金色的魔法阵（椭圆，外圈一道金色的光环，里面一圈粉紫色的花纹和小爱心符号），几片"
     "发光的书页从阵里往上飘，然后阵收拢（参考 r_indicator、r_glow、p_decal、z_scribbles）。**只画在地面上（她站在中间，不画人）**，"
     "**左右对称**，6 帧。",
     f"{MA}, {GO} and {HE}",
     "A MAGIC CIRCLE OPENING on the ground under a small caster, 6 frames, " + LR + " (" + HER + "): 1 a small gold ring on "
     "the ground (an ellipse 12 wide and 4 tall); 2 the circle 28 wide and 9 tall, a gold rim with an inner ring of "
     "pink-violet scroll-work; 3 the circle 36 wide and 12 tall, small pink heart and spiral glyphs on it at mirrored places, "
     "4 glowing cream page shapes (3x4 squares) rising above it at mirrored places; 4 the same, the pages higher; 5 the "
     "circle shrinking to 22 wide; 6 only a thin fading ring and a few sparkles.",
     row(6, 40, 20) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("r_wave", "R：魔典的波纹（弹道，循环，大图表），4 帧",
     "view_projectiles `league_yuumi_r_wave`（跟着弹道转向；上下对称；大图表）", "18 × 30",
     "魔典连发出去的波纹：一道竖着的弯月形光波，凸面朝右（朝飞的方向），粉紫色的光身、金色的亮边，后面带几粒金色星点和小书页的光片"
     "（参考 r_glow、r_indicator、wisptrail_add、fire_tile_gold）。**朝右飞，严格上下对称**，4 帧循环。",
     f"{MA} and {GO}",
     "A MAGIC WAVE, 4 frames, a seamless loop, " + TB + ": a tall crescent of light 26 squares tall and 6 thick, bulging to "
     "the RIGHT (the way it flies), its body pink-violet, its leading (right) edge a bright gold-white line, 4-5 gold sparkle "
     "squares and 2 small glowing page flecks trailing behind it on the left at mirrored places; each frame the gold edge "
     "shimmers and the sparkles drift back.",
     row(4, 18, 30) + "; the crescent's middle on the cell's middle row, its gold edge 2 squares from the cell's right edge."),
    ("r_hit", "R：波纹打中敌人，4 帧", "view_effects `league_yuumi_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "波纹扫过敌人：一团粉紫色的闪光，几片发光的书页碎片和金色星点散开（参考 r_glow、q_flash、sparkle）。**左右对称**，约 16 × 16 格。",
     f"{MA} and {GO}",
     "A WAVE HIT, 4 frames, " + LR + ": 1 a pink-white flash 7 squares across; 2 the flash 11 across with 4 glowing cream "
     "page flecks (2x3 squares) flying out at mirrored places; 3 the flecks further out with gold sparkles; 4 only fading "
     "sparkles.",
     row(4, 16, 16) + CENTER),
    ("r_heal", "R：波纹治疗队友，4 帧", "view_effects `league_yuumi_r_heal`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 16",
     "波纹扫过队友：队友身上冒起一个粉色的爱心和几粒金色星点（参考 z_scribbles 的爱心、p_glow）。**左右对称**，约 14 × 16 格。",
     f"{HE} and {GO}",
     "A HEALING HEART on an ally, 4 frames, " + LR + ": 1 a pink glow 6 squares across; 2 a pink heart 6 squares wide inside "
     "it, 4 gold sparkles round it; 3 the heart rising 3 squares, the sparkles further out; 4 the heart fading at the top.",
     row(4, 14, 16) + CENTER),
    ("r_root", "R：第三道波纹的定身（脚下，循环），4 帧", "view_buffs `league_yuumi_r_root`（跟随，画在人物上面 z 1；左右对称；循环）",
     "22 × 14",
     "被第三道波纹定住：敌人脚下缠着几圈粉紫色的发光书页丝带，带金色的边，丝带上的光一闪一闪（参考 r_indicator、z_scribbles、"
     "wisptrail_add）。**只画在脚和小腿的位置**，**左右对称**，4 帧循环。",
     f"{MA} and {GO}",
     "A BINDING OF GLOWING PAGE-RIBBONS round a unit's feet, 4 frames, a seamless loop, " + LR + ": two flat ellipse loops "
     "(18 squares wide, 4 tall, one 2 squares above the other) of pink-violet ribbon 1-2 squares thick with a gold edge, "
     "wrapped round the space where the legs are (the middle left open), small cream page flecks on them; each frame a "
     "bright white-gold glint runs along the ribbons (mirrored).",
     row(4, 22, 14) + "; centered across, the lower loop's bottom on the cell's bottom row."),
]
BIG_FX = ["r_cast", "r_wave"]
FLYING = ["a_bolt", "q_missile", "r_wave"]
GROUPS = [
    ("a_bolt a_hit p_hit p_heal", ["yuumi_base_core", "yuumi_base_z_spark", "yuumi_base_sparkle", "yuumi_base_ba_tar_star",
                                   "yuumi_base_z_scribbles_2", "yuumi_base_p_glow"]),
    ("q_missile q_hit q_ehit q_slow q_eslow", ["yuumi_base_q_flash", "yuumi_base_e_flash", "yuumi_base_qbv2_gold",
                                               "yuumi_base_fire_tile_gold", "yuumi_base_e_ring", "yuumi_base_wisptrail_add"]),
    ("e_hit e_haste w_heal w_jump w_land", ["yuumi_base_wv3_shield_trail", "yuumi_base_e_streak", "yuumi_base_e_sandflecks",
                                            "yuumi_base_smokeerode", "yuumi_base_p_decal", "yuumi_base_bigglow02"]),
    ("r_cast r_wave r_hit r_heal r_root", ["yuumi_base_r_indicator", "yuumi_base_r_indicator_outline", "yuumi_base_r_glow",
                                           "yuumi_base_p_decal", "yuumi_base_z_scribbles_2", "yuumi_base_wisptrail_add"]),
]
SHOTS = [("attack", 3, "a_bolt：扑到最前面时光弹飞出去；a_hit 在目标身上"), ("skill", 3, "q_missile：跳到最高时把飞弹甩出去"),
         ("skill2", 1, "w_jump：她起跳的地方（她扑向队友前）"), ("w_off", 3, "w_land：从队友身上跳下来落地的地方"),
         ("ult", 4, "r_cast：书立起来时脚下的魔法阵；r_wave 从她这里朝目标飞"), ("hit", 1, "挨打"),
         ("dead", 5, "死亡：钻进书里、书合上落地"), ("idle", 1, "待机（大小参考）")]


def configure():
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "悠米"


def shown_frames(tag):
    """The tag's hd_ frames as the game draws them (75 %: half a game px a dense pixel), each centred on her pivot."""
    out = []
    for f in RF.sheet_frames("hd_" + tag):
        k = SHOWN / PPU
        im = Image.fromarray(f).resize((max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))), Image.NEAREST)
        out.append(np.asarray(im))
    return out


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel, shown at 75 %)."""
    import rig_yuumi as Y
    F = Y.form()
    c = F.rig.finish(Y.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def size_sheet(path):
    """RF.size_sheet with her idle as the game shows it (75 %)."""
    keep = RF.first_1x

    def first(tag):
        f = shown_frames(tag)[0]
        ys, xs = np.nonzero(f[..., 3] > 0)
        return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    RF.first_1x = first
    try:
        return RF.size_sheet(path)
    finally:
        RF.first_1x = keep


def shots_sheet(path):
    """RF.shots_sheet with her frames as the game shows them (75 %, still centred on her pivot)."""
    keep = RF.sheet_frames
    RF.sheet_frames = lambda tag: shown_frames(tag) if not tag.startswith("hd_") else keep(tag)
    try:
        RF.shots_sheet(path)
    finally:
        RF.sheet_frames = keep


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 魔法猫咪 悠米：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/yuumi_idle.png`：淡紫蓝色的 Q 版小猫，坐在一本会飞的深红金边魔法书里，"
      f"金色头饰、金触须挂着蓝色小球，尾巴尖一簇金毛）。她在游戏里是**高清**的、而且**画小了**（{h} 格高、{w} 格宽，"
      f"比一般英雄矮一截）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/yuumi_size.png`：她在游戏里的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士（一般英雄的"
      "大小）。每条写的大小都是游戏像素（格）。")
    a("> - `design/yuumi_shots.png`：定稿动作（游戏里的大小，4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里悠米自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她的光是金色的星光和粉紫色的魔法**，**治疗是粉色的小爱心**，**大招的波纹是粉紫色带金边**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、头上、脚下、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（光弹、飞弹、波纹）"
      "**朝右飞、尾巴在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `yuumi_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/yuumi_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「猫的博爱」在里面） | 射出一颗小光弹；每隔几秒普攻英雄多一段伤害并给自己回血 | `a_bolt` · `a_hit` · `p_hit` · `p_heal` |")
    a("| 技能 1 = Q「摸鱼飞弹」 | 飞弹直线飞向敌人，飞得够久就强化：伤害更高、减速更强 | `q_missile` · `q_hit` · `q_ehit` · `q_slow` · `q_eslow` |")
    a("| 技能 2 = W「悠米出动！」+ E「旺盛精力」 | 扑到交战中的队友身上附身（趴在他头上），给他护盾、攻速移速，附身期间他持续回血；时间到跳下来 | "
      "`w_jump` · `e_hit` · `e_haste` · `w_heal` · `w_land`（头上的小猫另有一包） |")
    a("| 大招「魔典终章」 | 把书立起来，朝目标连发 5 道波纹：伤敌减速、治疗沿途队友，第 3 道定身 | `r_cast` · `r_wave` · `r_hit` · "
      "`r_heal` · `r_root` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、星点、爱心、波纹、光环、魔法阵都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色的星光", GOLD), ("粉紫色的魔法", MAGIC), ("粉色的爱心（治疗）", HEART)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（魔法阵、减速圈、加速圈、落地的光环）是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 50000，飞弹最远飞 100000，"
      "大招的波纹宽 24000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `yuumi_fx_{name}.png`：{title}\n")
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
        a(f"| `yuumi_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_yuumi_fx`（小的）和 `league_yuumi_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_yuumi.py 的 views）；`w_ride`（附身的小猫）来自 pack_yuumi_ride.py 的交付，也进 `league_yuumi_big`。")
    a(f"- 弹道图（{'、'.join(FLYING)}）断言上下对称，其余断言左右对称；`w_jump`、`w_land` 不跟随（起跳点、落点）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回"
      "（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="yuumi_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "yuumi_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run fx_ref_yu.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "yuumi_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "yuumi_size.png"))
    shots_sheet(os.path.join(out, "design", "yuumi_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"yuumi_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
