#!/usr/bin/env python3
"""Build shyvana_fx_pack.zip: step 3 of Shyvana's sprite - Codex draws her effects (pack_velkoz_fx.py's way).

    python tools/lol/fx_ref_shyvana.py         # League's particle textures -> C:/t/sv_work/fxref (Riot's art, local only)
    python tools/art/pack_shyvana_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name shyvana_fx_redo_pack]

The pack (C:/t/sv_work/fx/shyvana_fx_pack, zipped into --out, default dist/shyvana_packs) holds PROMPTS.md (also written
to assets/source/shyvana/PROMPTS_FX.md), design/shyvana_designs.png (her and the dragon at 4x, the designs' squares at
PPU 1.5), design/shyvana_size.png (both forms at game size, 4x, on the arena colour with the ground line, a 10-px ruler
and the base fighter), design/shyvana_shots.png (frames from tools/art/rig_shyvana.py the pictures start from, 4x; her
own actions come from Codex's poses, so her idle stands for them) and refs/lol_fx_ref.png (League's own particle
textures for Shyvana and her dragon, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_shyvana.py): view_projectiles e_ball, de_ball, r_breath;
view_effects a_hit, q_slash, d_q_slash, q_hit, q2_wave, d_q2_wave, q2_hit, q3_hit, w_blast, w_hit, w_heal, e_hit, e_blast,
de_hit, de_blast, de_singe, r_hit, r_land, tf_dragon, tf_human; view_buffs w_aegis (league_shyvana_w_on), fury_full
(league_shyvana_full), e_slow. League's colours: her fire is ORANGE and GOLD with white-hot cores, deepening to crimson
at its edges (the dragon's breath and fireball a deeper orange-red); the bite's true damage white-gold; the dragon's
heal green-gold. Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is
symmetric left to right; the projectiles (e_ball, de_ball, r_breath) are turned with their flight, so they are drawn
flying right and symmetric top to bottom; q_slash and d_q_slash point forward (right) and are baked into her frames
(tools/fix/bake_caster_fx.py), so they need no symmetry.
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

TMP = "C:/t/sv_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "shyvana", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "shyvana", "hd")
NAME = "shyvana_fx_pack"

FIRE = "#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420"      # her flames: white core to crimson edge
DRAGON = "#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A"    # the dragon's breath and fireball
GOLD = "#FFFFFF, #FFF6C8, #FFE07A, #F6B83A, #C8862A"                        # the bite's true damage, the aegis' rim
HEAL = "#F4FFE6, #D2F58C, #8AD84E, #4AA444, #2A6E3A"                        # the dragon's heal
ASH = "#B8AAA0, #847872, #5A4E4C, #3A3032"                                   # ash and smoke (the turn back)
FI = f"an orange fire ramp ({FIRE})"
DR = f"a deep orange-red dragon-fire ramp ({DRAGON})"
GO = f"a white-gold light ramp ({GOLD})"
HE = f"a green-gold heal ramp ({HEAL})"
AS = f"a grey ash ramp ({ASH})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
FWD = "pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry)"
CENTER = RF.CENTER
row = RF.row
HER = "she stands in the middle, not drawn: 27 squares wide and 42 tall"
DRAG = "the dragon stands in the middle, not drawn: 71 squares long and 43 tall, low on four legs"
GROUND = ("a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the "
          "feet are")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_hit", "普攻：爪击打中目标，3 帧", "view_effects `league_shyvana_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "龙爪抓中：三道短短的橙红色爪痕交叉一闪，迸出几点火星（参考 claw_slashforward、tar_flash_fire、base_generic_sparks_add）。"
     "**左右对称**，3 帧。",
     FI,
     "A CLAW HIT, 3 frames, " + LR + ": 1 a white-gold flash 5 squares across with three short orange claw streaks crossing "
     "it (an X and a vertical stroke); 2 the streaks fading to red, 4 sparks flying out diagonally; 3 only the fading sparks.",
     row(3, 12, 12) + CENTER),
    # ---- Q Emberstrike
    ("q_slash", "Q 焚焰打击（人形）：前方的火焰斩击，4 帧", "view_effects `league_shyvana_q_slash`（她身上，画进她的动作帧；朝右）",
     "30 × 22",
     "她的爪子往前横斩，在身前划出一道弯月形的火焰爪痕（三道平行的火弧，参考 claw_slashforward、fire_claw、shyvana_base_ba_edgeaoe）。"
     "**朝右画**（会画进她的动作帧里，不用左右对称），4 帧：起、最亮、散开、余烬。",
     FI,
     "A FIERY CLAW SLASH, 4 frames, " + FWD + ": three parallel curved flame streaks sweeping in a crescent from the upper "
     "left to the lower right in front of her, 22 squares long, white-gold at their leading edge, orange behind, crimson at "
     "the tail; 1 the streaks half drawn; 2 full and brightest; 3 breaking into flame tongues; 4 only embers drifting.",
     row(4, 30, 22) + "; the crescent's middle on the cell's middle, its points toward the right; " + HER +
     " at the cell's left edge."),
    ("d_q_slash", "Q 焚焰打击（龙形）：翼击掀起的火焰气浪，4 帧", "view_effects `league_shyvana_d_q_slash`（龙身上，画进龙的动作帧；朝右）",
     "48 × 34",
     "龙的翅膀往前一拍，前方卷起一大片带火的气浪（一道宽的弧形火浪往前推，参考 shyvanadragon_base_q_swipe_a、shyvana_q_cloudtextures、"
     "shyvana_base_tileflames02）。**朝右画**（会画进龙的动作帧），4 帧。",
     DR,
     "A WING-GUST OF FIRE, 4 frames, " + FWD + ": a wide curved wave of flame and hot wind pushing forward to the right, "
     "34 squares tall at its front, tongues of flame along its front edge, a white-yellow inner rim; 1 forming; 2 full; "
     "3 rolling forward and thinning; 4 only flame wisps.",
     row(4, 48, 34) + "; the wave's front edge 4 squares from the right of the cell; " + DRAG + " to the left of the cell."),
    ("q_hit", "Q：斩击打中目标，3 帧", "view_effects `league_shyvana_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "斩击打中：一团橙色火焰溅开（参考 shyvana_base_q_impact_tarsplash）。**左右对称**，3 帧。",
     FI,
     "A FIERY SPLASH HIT, 3 frames, " + LR + ": 1 a white core 4 squares across with a jagged orange splash 10 squares "
     "across; 2 the splash breaking into 8 flame tongues; 3 small flames and embers.",
     row(3, 14, 14) + CENTER),
    ("q2_wave", "Q 二段（人形）：横扫时脚下一圈火，5 帧", "view_effects `league_shyvana_q2_wave`（跟随她，画在人物后面 z -1；左右对称）",
     "60 × 24",
     "她转身横扫，脚下贴着地面炸开一圈火焰（地上的椭圆火环，往外扩散，参考 shyvana_base_ba_edgeaoe、shyvana_base_ground01、"
     "shyvana_base_ring_softglow2）。**左右对称**，5 帧。",
     FI,
     "A RING OF FIRE ON THE GROUND, 5 frames, " + LR + ": " + GROUND + "; 1 a thin bright ring 30 squares wide; 2 grown to 50 "
     "wide with short flame tongues rising along its far half; 3 full, 58 wide, flames 8 squares tall; 4 the flames sinking; "
     "5 only a faint scorched ring with embers.",
     row(5, 60, 24) + "; the ellipse's middle 6 squares above the cell's bottom; " + HER + " in the middle."),
    ("d_q2_wave", "Q 二段（龙形）：甩尾扫出的大火弧，5 帧", "view_effects `league_shyvana_d_q2_wave`（跟随龙，z -1；左右对称）",
     "90 × 34",
     "龙转身甩尾，尾巴扫过的地方贴地掀起一大圈火焰（比人形的大，参考 shyvanadragon_base_emote_linearsplashes_02_gs、"
     "shyvana_base_ba_edgeaoe、shyvana_base_ground02）。**左右对称**，5 帧。",
     DR,
     "A BIG SWEEPING FIRE RING ON THE GROUND, 5 frames, " + LR + ": " + GROUND + "; 1 a bright ring 50 squares wide; 2 grown "
     "to 76 wide with flames rising along it; 3 full, 88 wide, flames 12 squares tall; 4 the flames sinking; 5 scorched "
     "ring and embers.",
     row(5, 90, 34) + "; the ellipse's middle 8 squares above the cell's bottom; " + DRAG + " in the middle."),
    ("q2_hit", "Q 二段：扫中目标，3 帧", "view_effects `league_shyvana_q2_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "扫中：一团火焰爆开（参考 tar_flash_fire）。**左右对称**，3 帧。",
     FI,
     "A FIRE BURST HIT, 3 frames, " + LR + ": 1 a white-orange star flash 7 squares across; 2 a round burst of flame 11 "
     "squares across; 3 small flames and embers rising.",
     row(3, 12, 12) + CENTER),
    ("q3_hit", "Q 三段（龙形）：撕咬，4 帧", "view_effects `league_shyvana_q3_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "龙一口咬下（真实伤害）：上下两排白金色的獠牙从两边合拢，咬住时一闪白光（参考 sowflash_spark）。**左右对称**，4 帧。",
     GO,
     "A DRAGON BITE, 4 frames, " + LR + ": 1 two curved rows of 5 white-gold fangs, one above and one below, 10 squares "
     "apart; 2 the rows closing to 4 squares apart; 3 snapped shut with a white flash 12 squares across; 4 gold sparks "
     "scattering.",
     row(4, 16, 16) + CENTER),
    # ---- W Inferno Aegis
    ("w_aegis", "W 烈火圣盾：包着她的火焰护盾（循环），6 帧", "view_buffs `league_shyvana_w_on`（tag w_aegis；跟着她，循环，z 2；"
     "左右对称；龙形也用这张）", "44 × 50",
     "一圈烈焰包着她：外面一层淡金色的护盾光边，火焰在护盾边上往上窜（参考 shyvana_base_w_shield_mesh2、shyvana_base_w_shieldfresnelring、"
     "shyvana_base_vgu_w_ele_flat_energy、shyvana_base_tileflames02）。**中间她的身体位置留空**，**左右对称**，6 帧循环。",
     FI,
     "A FLAME SHIELD AROUND A BODY, 6 frames, a seamless loop, " + LR + ": a gold dome outline 40 squares wide and 46 tall "
     "(1 square thick, pale gold, broken in places) with orange flames 4-8 squares tall licking up along its lower two "
     "thirds on both sides, and a flat ring of fire on the ground; the inside EMPTY where her body is (only the dome's thin "
     "rim crosses in front at the bottom); each frame the flames rise and flicker in turn.",
     row(6, 44, 50) + "; the dome's bottom 3 squares above the cell's bottom; " + HER + " in the middle."),
    ("w_blast", "W 烈火圣盾：护盾爆开，6 帧", "view_effects `league_shyvana_w_blast`（跟随她，z -1；左右对称）", "72 × 46",
     "护盾时间到，烈焰向四周炸开：先是一圈很亮的火环贴地扩散，再冲起一圈火焰（参考 shyvana_base_ba_edgeaoe、shyvana_base_ring_softglow2、"
     "tar_flash_fire）。**左右对称**，6 帧。",
     FI,
     "A FIRE NOVA AROUND A BODY, 6 frames, " + LR + ": 1 a white-gold flash at the feet, a ring 20 squares wide; 2 the ring "
     "racing out to 48 wide, flames bursting up around it 16 tall; 3 full, 70 wide, a wall of flame 24 squares tall round "
     "the ring's far half, low flames on its near half; 4 the flames curling and fading to red; 5 smoke-orange wisps; "
     "6 a faint scorched ring.",
     row(6, 72, 46) + "; the ground ellipse's middle 8 squares above the cell's bottom; " + HER + " in the middle."),
    ("w_hit", "W：爆炸打中目标，3 帧", "view_effects `league_shyvana_w_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "被爆炸波及：身上一团火（参考 tar_flash_fire）。**左右对称**，3 帧。",
     FI,
     "A SMALL FIRE HIT, 3 frames, " + LR + ": 1 an orange flash 6 squares across; 2 three flame tongues rising 9 squares; "
     "3 embers.",
     row(3, 12, 12) + CENTER),
    ("w_heal", "W（龙形）：爆炸打中英雄时回血，5 帧", "view_effects `league_shyvana_w_heal`（跟随她，z 3；左右对称）", "26 × 30",
     "龙形时护盾爆炸打中英雄会回血：身上冒起一圈绿金色的光点往上飘（参考 shyvana_base_w_heal_ray、shyvana_base_w_heal_spark）。"
     "**中间身体位置留空，左右对称**，5 帧。",
     HE,
     "A HEAL BURST, 5 frames, " + LR + ": soft green-gold light rising round a body: 1 a ring of 8 bright green-gold motes "
     "at the feet; 2 the motes rising as short vertical streaks 6 squares long; 3 at chest height with a small white plus "
     "sign over the head; 4 near the top, fading; 5 a few last motes. The middle EMPTY where the body is.",
     row(5, 26, 30) + "; the motes start 2 squares above the cell's bottom; " + HER + " in the middle."),
    # ---- E Molten Burst
    ("e_ball", "E 爆炎吐息（人形）：火球（弹道，循环），4 帧", "view_projectiles `league_shyvana_e_ball`（跟着弹道转向；上下对称）",
     "16 × 10",
     "她掷出的火球：白黄色的芯，橙色的火团，后面拖一截飘动的火焰尾巴（参考 shyvana_base_missilehead01、shyvana_base_e_mis_flametrail、"
     "shyvana_base_foundation_missile02）。**朝右飞、尾巴在左边，上下对称**，4 帧循环。",
     FI,
     "A FIREBALL, 4 frames, a seamless loop, " + TB + ": a round fireball 6 squares across with a white-yellow core 2-3 "
     "squares, a tapering flame trail 8 squares long behind it on the left; each frame the flames of the trail shift back "
     "a square and the core flickers.",
     row(4, 16, 10) + "; the ball's middle on the cell's middle row, its front 1 square from the right edge."),
    ("e_hit", "E：火球打中目标，3 帧", "view_effects `league_shyvana_e_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "火球砸中：一团火焰（参考 tar_flash_fire）。**左右对称**，3 帧。",
     FI,
     "A FIREBALL HIT, 3 frames, " + LR + ": 1 a white-orange flash 6 squares across; 2 a burst of flame 10 squares across; "
     "3 small flames.",
     row(3, 12, 12) + CENTER),
    ("e_blast", "E：火球在落点炸开，5 帧", "view_effects `league_shyvana_e_blast`（落点，不跟随，z -1；左右对称）", "34 × 30",
     "火球炸开：地上一圈火，往上冒起火焰（参考 shyvana_base_e_ground_mask、shyvana_base_e_decalglow、tar_flash_fire）。**左右对称**，5 帧。",
     FI,
     "A FIREBALL BURST ON THE GROUND, 5 frames, " + LR + ": " + GROUND + "; 1 a white flash 10 squares across; 2 a ring of "
     "fire 26 wide with flames bursting up 16 squares; 3 full, 32 wide, flames 22 tall; 4 the flames sinking; 5 a scorched "
     "patch with embers.",
     row(5, 34, 30) + "; the ground ellipse's middle 5 squares above the cell's bottom; centered across."),
    ("de_ball", "E（龙形）：大火球（弹道，循环），4 帧", "view_projectiles `league_shyvana_de_ball`（跟着弹道转向；上下对称）",
     "26 × 16",
     "龙喷出的大火球：比人形的大一倍，深橙红色，拖着一大截火焰（参考 shyvana_base_e_mis_flametrail、shyvana_e_flameoutline、"
     "shyvana_base_missilehead01）。**朝右飞、尾巴在左边，上下对称**，4 帧循环。",
     DR,
     "A BIG DRAGON FIREBALL, 4 frames, a seamless loop, " + TB + ": a fireball 10 squares across with a white-yellow core "
     "4 squares, a wide flame trail 14 squares long behind it on the left; each frame the trail's flames shift back and "
     "the core pulses.",
     row(4, 26, 16) + "; the ball's middle on the cell's middle row, its front 1 square from the right edge."),
    ("de_hit", "E（龙形）：大火球穿过打中的目标，3 帧", "view_effects `league_shyvana_de_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "大火球穿过时身上一团火（参考 tar_flash_fire）。**左右对称**，3 帧。",
     DR,
     "A BIG FIRE HIT, 3 frames, " + LR + ": 1 a white-orange flash 7 squares across; 2 a burst of deep orange flame 12 "
     "squares across; 3 flames and embers.",
     row(3, 14, 14) + CENTER),
    ("de_blast", "E（龙形）：大火球在终点炸开，6 帧", "view_effects `league_shyvana_de_blast`（落点，不跟随，z -1；左右对称）", "64 × 44",
     "大火球在终点炸开一大片火海（参考 shyvana_base_ground03、shyvana_base_ba_edgeaoe、tar_flash_fire）。**左右对称**，6 帧。",
     DR,
     "A BIG FIRE EXPLOSION ON THE GROUND, 6 frames, " + LR + ": " + GROUND + "; 1 a white flash 16 squares across; 2 a ring "
     "of fire 44 wide, flames bursting up 26 squares; 3 full, 60 wide, flames 34 tall; 4 the flames curling and reddening; "
     "5 low flames; 6 a scorched patch with embers.",
     row(6, 64, 44) + "; the ground ellipse's middle 7 squares above the cell's bottom; centered across."),
    ("de_singe", "E（龙形）：燃烧的地面烧到目标，3 帧", "view_effects `league_shyvana_de_singe`（跟随目标，z 2；左右对称）", "10 × 12",
     "站在燃烧的地面上被烧：脚下冒出几簇小火苗（参考 shyvana_base_fire_2x2）。**左右对称**，3 帧。",
     DR,
     "SMALL FLAMES AT THE FEET, 3 frames, " + LR + ": three small flame tongues 4-7 squares tall rising from the bottom "
     "middle of the cell, flickering frame to frame, a few embers above.",
     row(3, 10, 12) + "; the flames rise from the cell's bottom middle."),
    ("e_slow", "E：被减速（循环），4 帧", "view_buffs `league_shyvana_e_slow`（跟着目标，循环，z 3；左右对称）", "16 × 8",
     "被火球减速：脚下一圈慢慢冒烟的余烬（参考 shyvana_base_burning_ash）。**左右对称**，4 帧循环。",
     FI,
     "SMOULDERING EMBERS AT THE FEET, 4 frames, a seamless loop, " + LR + ": " + GROUND + " 14 squares wide of glowing orange "
     "embers and dark ash, two thin wisps of grey-orange smoke rising 3-4 squares; each frame the embers glow in turn.",
     row(4, 16, 8) + "; the ellipse's middle 2 squares above the cell's bottom."),
    # ---- R Dragon's Descent
    ("r_breath", "R 魔龙降世：沿途喷出的龙息（弹道，循环），4 帧", "view_projectiles `league_shyvana_r_breath`（跟着弹道转向；上下对称）",
     "44 × 20",
     "龙飞过去时往下喷的一大股火焰：一条宽宽的火流往前冲（参考 shyvana_base_vgu_w_ele_flat_energy、shyvana_base_tileflames02、"
     "shyvana_base_e_mis_flametrail）。**朝右飞、后面在左边，上下对称**，4 帧循环。",
     DR,
     "A STREAM OF DRAGON FIRE, 4 frames, a seamless loop, " + TB + ": a wide rolling stream of flame 40 squares long and 16 "
     "tall, a white-yellow core along its middle, orange then red-crimson flame tongues at its top and bottom edges, its "
     "front rounded and brightest; each frame the flame tongues roll back along the stream.",
     row(4, 44, 20) + "; the stream's middle on the cell's middle row, its front 2 squares from the right edge."),
    ("r_hit", "R：被龙息烧到（恐惧），4 帧", "view_effects `league_shyvana_r_hit`（跟随目标，z 2；左右对称）", "14 × 18",
     "被龙息喷中：身上一团火，冒起几缕往上飘的黑紫色恐惧烟（参考 tar_flash_fire、shyvana_base_burning_ash）。**左右对称**，4 帧。",
     DR,
     "A DRAGON-FIRE HIT WITH FEAR, 4 frames, " + LR + ": 1 an orange flash 8 squares across at chest height; 2 a burst of "
     "flame 12 across; 3 the flames rising with two dark violet smoke wisps curling up above the head; 4 wisps and embers.",
     row(4, 14, 18) + "; the burst 7 squares above the cell's bottom; centered across."),
    ("r_land", "R：龙落地的冲击，6 帧", "view_effects `league_shyvana_r_land`（跟随龙，z -1；左右对称）", "86 × 36",
     "龙从空中砸到地上：一圈火焰和尘土贴地冲开（参考 shyvana_base_ground01、shyvana_base_vgu_distortring、shyvana_base_ba_edgeaoe）。"
     "**左右对称**，6 帧。",
     DR,
     "A FIERY LANDING SHOCKWAVE, 6 frames, " + LR + ": " + GROUND + "; 1 a white flash under the body 20 squares wide; 2 a "
     "ring of fire and dust 50 wide racing out, cracks of glowing orange on the ground; 3 full, 84 wide, flames 10 squares "
     "tall along the ring; 4 the ring fading, dust rising; 5 glowing cracks and embers; 6 faint embers.",
     row(6, 86, 36) + "; the ground ellipse's middle 8 squares above the cell's bottom; " + DRAG + " in the middle."),
    ("tf_dragon", "R：化身为龙的火焰，6 帧", "view_effects `league_shyvana_tf_dragon`（跟随她，z 3；左右对称）", "64 × 64",
     "她在空中化龙：一团火焰把她整个包住然后炸开（火柱、往外甩的火翼形状，参考 shyvana_base_vgu_awaken_sharpshape、"
     "shyvana_base_vgu_awaken_tile03、shyvana_base_vgu_awaken_ribbonmask01）。**左右对称**，6 帧。",
     DR,
     "A DRAGON TRANSFORMATION BURST, 6 frames, " + LR + ": 1 a white-gold flash 16 squares across in the middle; 2 a "
     "column of fire 40 squares tall wrapping the middle; 3 the fire flaring out into two huge wing-shaped flame sheets to "
     "both sides, 60 squares wide; 4 the flame wings breaking into tongues; 5 embers spiralling out; 6 a few embers.",
     row(6, 64, 64) + "; centered in every cell (the middle of the burst on the cell's middle)."),
    ("tf_human", "龙形结束：变回人的烟火，5 帧", "view_effects `league_shyvana_tf_human`（跟随她，z 3；左右对称）", "48 × 48",
     "魔龙时间到，变回人形：一团火焰收拢、散成火星和灰烟（参考 shyvana_base_burning_ash、tar_flash_fire_dissolve）。**左右对称**，5 帧。",
     FI,
     "A TURN-BACK BURST, 5 frames, " + LR + ": 1 a ring of fire 40 squares wide collapsing inward; 2 a bright orange flash "
     "20 across in the middle; 3 the flash breaking into embers and grey ash puffs (" + ASH + "); 4 ash and embers "
     "drifting up; 5 a few last embers.",
     row(5, 48, 48) + CENTER),
    ("fury_full", "龙怒攒满（循环），4 帧", "view_buffs `league_shyvana_full`（tag fury_full；跟着她，循环，z 3；左右对称）", "30 × 44",
     "龙怒攒满、可以化龙：她身边一圈跳动的小火苗往上窜（两侧肩膀和手边，参考 shyvana_base_fire_2x2、shyvana_base_w_sparks）。"
     "**中间她的身体位置留空**，**左右对称**，4 帧循环。",
     FI,
     "A DRAGON-FURY AURA, 4 frames, a seamless loop, " + LR + ": small orange flame tongues 3-6 squares tall rising at both "
     "sides of a standing body (at the shoulders and at the hands), a few gold sparks drifting up; the middle EMPTY where "
     "the body is; each frame the flames flicker in turn.",
     row(4, 30, 44) + "; " + HER + " in the middle."),
]
BIG_FX = ["d_q_slash", "q2_wave", "d_q2_wave", "w_aegis", "w_blast", "e_blast", "de_ball", "de_blast", "r_breath",
          "r_land", "tf_dragon", "tf_human"]
FLYING = ["e_ball", "de_ball", "r_breath"]
FORWARD = ["q_slash", "d_q_slash"]

GROUPS = [
    ("a_hit / q_hit / hits", ["claw_slashforward", "tar_flash_fire", "shyvana_base_q_impact_tarsplash",
                              "base_generic_sparks_add", "sowflash_spark"]),
    ("q_slash / d_q_slash", ["fire_claw", "shyvana_base_ba_edgeaoe", "shyvanadragon_base_q_swipe_a",
                             "shyvana_q_cloudtextures", "shyvana_base_tileflames02"]),
    ("q2_wave / w_blast / r_land", ["shyvana_base_ring_softglow2", "shyvana_base_ground01", "shyvana_base_ground02",
                                    "shyvana_base_vgu_distortring", "shyvanadragon_base_emote_linearsplashes_02_gs"]),
    ("w_aegis / w_heal", ["shyvana_base_w_shield_mesh2", "shyvana_base_w_shieldfresnelring", "shyvana_base_w_shieldicon",
                          "shyvana_base_w_heal_ray", "shyvana_base_w_heal_spark"]),
    ("e_ball / de_ball / r_breath", ["shyvana_base_missilehead01", "shyvana_base_e_mis_flametrail",
                                     "shyvana_base_foundation_missile02", "shyvana_e_flameoutline",
                                     "shyvana_base_vgu_w_ele_flat_energy"]),
    ("e_blast / de_blast / e_slow", ["shyvana_base_e_ground_mask", "shyvana_base_e_decalglow", "shyvana_base_ground03",
                                     "shyvana_base_burning_ash", "shyvana_base_fire_2x2"]),
    ("tf_dragon / tf_human / fury", ["shyvana_base_vgu_awaken_sharpshape", "shyvana_base_vgu_awaken_tile03",
                                     "shyvana_base_vgu_awaken_ribbonmask01", "shyvana_base_w_sparks",
                                     "shyvana_base_fire_grad"]),
]
# frames the pictures start from: (tag, frame, what appears there) - rig_shyvana's frames
SHOTS = [("idle", 1, "她（Q 斩击、W 护盾、E 火球从这里出手）"), ("d_attack", 4, "龙爪耙下：a_hit"),
         ("d_skill", 4, "翼击：d_q_slash 在前方"), ("d_skill_b", 5, "甩尾：d_q2_wave 在脚下"),
         ("d_bite", 4, "撕咬：q3_hit 在目标身上"), ("d_skill2", 4, "张嘴喷大火球：de_ball 从嘴里出"),
         ("d_fly", 1, "R 飞行：r_breath 往前喷"), ("d_fly", 4, "R 落地：r_land 在脚下")]


def rig_1x():
    """{tag: [1x frame]} from rig_shyvana's canvases (ppu_rig.Rig.export's way: the commonest colour of each PPU block
    about the pivot)."""
    import ppu_rig as R
    import rig_shyvana as S
    C = S.Canvas()
    acts = S.frames(C)
    out = {}
    px, py = float(C.rig.CX), C.rig.GY - R.FEET * S.PPU
    for tag, fr in acts.items():
        ones = []
        for can, _ in fr:
            body = C.rig.finish(can)
            ys, xs = np.nonzero(body[..., 3] > 0)
            hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / S.PPU - 0.5))
            hh = max(int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / S.PPU - 0.5)), int(np.ceil(R.FEET)) + 1)
            ones.append(R.one_of(body, px, py, hw, hh, S.PPU))
        out[tag] = ones
    return out


_ONES = {}


def sheet_frames(tag):
    if not _ONES:
        _ONES.update(rig_1x())
    return _ONES[tag]


def first_1x(tag):
    f = sheet_frames(tag)[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Both forms at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    import tfm2_ase as T
    figs = [first_1x("idle"), first_1x("d_idle")]
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
    d.text((8, 36), f"希瓦娜 {figs[0].shape[1]}×{figs[0].shape[0]} 格，龙形 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape, figs[1].shape


def design_sheet(path):
    """Her and the dragon at 4x, the designs' own squares (PPU 1.5)."""
    a = np.asarray(Image.open(RF.lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    b = np.asarray(Image.open(RF.lp(os.path.join(HD, "d_idle.png"))).convert("RGBA"))
    W = (a.shape[1] + b.shape[1]) * 4 + 48
    H = max(a.shape[0], b.shape[0]) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, H - 16 - a.shape[0] * 4))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(b, 4, 0), 4, 1)), (32 + a.shape[1] * 4, H - 16 - b.shape[0] * 4))
    bg.convert("RGB").save(path)


def configure():
    """pack_rammus_fx's reference sheet from Shyvana's textures; its shots from rig_shyvana's frames."""
    RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = REF, GROUPS, SHOTS, "希瓦娜"
    RF.sheet_frames = sheet_frames


def document(shapes):
    (h, w), (dh, dw) = shapes[0][:2], shapes[1][:2]
    L = []
    a = L.append
    a("# 龙血武姬 希瓦娜：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/shyvana_designs.png`：左边人形——3/4 正面朝右、淡紫皮肤、金橙长发、"
      f"深红龙角冠、青银胸甲、深红长尾；右边龙形——深红巨龙、两只抬起的翅膀、橙黄火焰鬃毛）。她在游戏里是**高清**的（每个游戏格子里 "
      f"1.5×1.5 个细像素），人形 {h} 格高、{w} 格宽，龙形 {dh} 格高、{dw} 格长；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），"
      "不用画成高清。")
    a("> - 大小对照 `design/shyvana_size.png`：人形和龙形放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小"
      "都是游戏像素（格）。")
    a("> - `design/shyvana_shots.png`：动作帧（4 倍），青色十字是她的站位点；每张写了特效出现在哪里（人形的动作还在画，用待机代替）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里希瓦娜和她的龙自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了"
      "行，只在本地用，不要提交。颜色照英雄联盟原版：**她的火焰是橙色和金色的、芯是白的，边缘变成深红**；**龙的火（龙息、大火球）更深一些，"
      "橙红色**；**撕咬（真实伤害）是白金色**；**龙形回血是绿金色**。")
    a("> - **特效要亮**：每团火、每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **火焰、光、光环、冲击波都没有黑描边**；**灰烟**可以有 1 格暗边。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（火球、大火球、龙息）"
      "**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的）。**两张斩击**（q_slash、d_q_slash）**朝右画**，"
      "会画进她的动作帧里，不用对称。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `shyvana_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/shyvana_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（W「烈火圣盾」在里面） | 爪击；每 12 秒的普攻带出火焰护盾，2.5 秒后爆炸，龙形时炸到英雄回血 | `a_hit` · `w_aegis` · "
      "`w_blast` · `w_hit` · `w_heal` |")
    a("| 技能 1 = Q「焚焰打击」 | 人形：斩击 → 横扫；龙形：翼击 → 甩尾 → 撕咬（接在之后的普攻上） | `q_slash` · `d_q_slash` · `q_hit` · "
      "`q2_wave` · `d_q2_wave` · `q2_hit` · `q3_hit` |")
    a("| 技能 2 = E「爆炎吐息」 | 人形掷火球，命中或到终点爆炸并减速；龙形喷大火球，穿透、终点炸开、留下燃烧的地面 | `e_ball` · `e_hit` · "
      "`e_blast` · `e_slow` · `de_ball` · `de_hit` · `de_blast` · `de_singe` |")
    a("| 大招「魔龙降世」 | 龙怒攒满时化身为龙，飞向敌方英雄，一路喷火使敌人恐惧，落地 | `fury_full` · `tf_dragon` · `r_breath` · "
      "`r_hit` · `r_land` · `tf_human` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火焰、光、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（灰烟可以有 1 格暗边）。")
    a("- **要亮**：每个火焰、光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("她的火焰（橙金色）", FIRE), ("龙的火（橙红色）", DRAGON), ("撕咬、护盾光边（白金色）", GOLD),
                        ("龙形回血（绿金色）", HEAL), ("灰烟（变回人）", ASH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（火环、爆炸、余烬）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 二段的半径 26000，W 爆炸半径 33000，"
      "E 射程 70000、落点半径 15000，龙形 E 射程 90000、终点半径 30000，R 的龙息宽 18000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `shyvana_fx_{name}.png`：{title}\n")
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
        a(f"| `shyvana_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_shyvana_fx`（小的）和 `league_shyvana_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_shyvana.py 的 views；buff w_on 的 tag 是 w_aegis，full 的 tag 是 fury_full）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；斩击（{'、'.join(FORWARD)}）朝右、用 tools/fix/bake_caster_fx.py 画进她的帧（人形 "
      "skill、龙形 d_skill 的出手帧）；其余断言左右对称；e_blast、de_blast 不跟随（落点）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给火焰描的最深色边（灰烟的暗边保留）；核对交回的张数和这份清单；和 "
      "`raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="shyvana_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "shyvana_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_shyvana.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "shyvana_designs.png"))
    shapes = size_sheet(os.path.join(out, "design", "shyvana_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "shyvana_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"shyvana_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": ("top-bottom" if x[0] in FLYING else "none (points right)" if x[0] in FORWARD
                                 else "left-right")} for x in FX], f, ensure_ascii=False, indent=1)
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
