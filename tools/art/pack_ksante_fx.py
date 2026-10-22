#!/usr/bin/env python3
"""Build ksante_fx_pack.zip: step 3 of K'Sante's sprite - Codex (or Gemini) draws his effects (pack_neeko_fx.py's way).

    python tools/lol/fx_ref_ksante.py           # League's particle textures -> C:/t/ks_work/fxref (Riot's art, local only)
    python tools/art/pack_ksante_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name ksante_fx_redo_pack]

The pack (C:/t/ks_work/fx/ksante_fx_pack, zipped into --out, default dist/ksante_packs) holds PROMPTS.md (also written to
assets/source/ksante/PROMPTS_FX.md), design/ksante_designs.png (both stances' designs at 4x, their squares at PPU 1.5),
design/ksante_size.png (both at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/lol_fx_ref.png (League's own particle textures for K'Sante, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_ksante.py): view_projectiles q3_wave; view_effects a_hit, p_hit,
q_hit, q3_hit, w_brace, w_land, w_hit, r_hit, r_slam, ao_on; view_buffs p_mark (the armed passive, on him), q_slow,
ao_aura (All Out, on him); plus the forward pictures drawn into his own frames (tools/fix/bake_caster_fx.py's way):
a_swipe, ao_swipe, q_crack, q3_burst, w_trail. League's colours: his ntofos' energy is TEAL-CYAN with SAND-BROWN dust
and grey-teal stone chips; the passive and the ult are GOLD (kente-pattern diamonds); All Out adds VIOLET-BLUE blades
of light. Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is
symmetric left to right; the projectile is turned with its flight, so it is drawn flying right and symmetric top to
bottom; the baked ones point forward (right) and need no symmetry.
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

TMP = "C:/t/ks_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "ksante", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "ksante", "hd")
NAME = "ksante_fx_pack"
PPU = 1.5

TEAL = "#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A"      # the ntofos' energy: white core to deep teal
SAND = "#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628"               # dust and sand
ROCK = "#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A"               # stone chips (solid: outlined)
GOLD = "#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E"               # the passive and the ult, kente diamonds
VIOLET = "#F2E6FF, #BFA2FF, #8A62F0, #5A38C0, #2E1C70"             # All Out's blades of light
TE = f"a teal-cyan energy ramp ({TEAL})"
SA = f"a sand-dust ramp ({SAND})"
RO = f"a grey-teal stone ramp ({ROCK})"
GO = f"a gold light ramp ({GOLD})"
VI = f"a violet-blue light ramp ({VIOLET})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
FWD = "pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry)"
CENTER = RF.CENTER
row = RF.row
HIM = "he stands in the middle, not drawn: a big man 26 squares wide and 43 tall (with his ntofos at his sides 44 wide, 48 tall)"
HIM_AO = "he stands in the middle, not drawn: hunched, 36 squares wide and 37 tall, his clubs reaching out to 54 wide"
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
SOLID = "SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack and the passive
    ("a_hit", "普攻：打中目标，3 帧", "view_effects `league_ksante_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "陀斧砸中：一团青白色的闪光，几块青灰色的小石屑溅开（参考 ksante_base_hit_region）。**左右对称**，3 帧。",
     TE + ", " + RO,
     "A HEAVY HIT, 3 frames, " + LR + ": 1 a teal-white four-pointed flash 6 squares across; 2 the flash 9 across with 4 "
     "small stone chips flying out at mirrored places; 3 only the chips further out and a few teal specks. " + SOLID + ".",
     row(3, 12, 12) + CENTER),
    ("p_hit", "被动 血性本能：被标记后的那一下普攻，4 帧", "view_effects `league_ksante_p_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "技能标记过的敌人被下一次普攻打中：一个金色的菱形纹样（肯特布的菱形套菱形）一下亮起又碎成菱形小光点（参考 ksante_base_kentepattern、"
     "p_diamond、ba_passive_swipe_bg）。**左右对称**，4 帧。",
     GO + ", " + TE,
     "A GOLD DIAMOND BURST, 4 frames, " + LR + ": 1 a gold-white flash 6 squares across; 2 a gold diamond outline 12 "
     "squares tall with a smaller diamond inside it (a kente-cloth motif), white core; 3 the diamonds breaking into 8 tiny "
     "gold diamond sparks flying out at mirrored places; 4 fading sparks with a few teal specks.",
     row(4, 16, 16) + CENTER),
    ("p_mark", "被动：下一次普攻已经强化（他身上，循环），4 帧", "view_buffs `league_ksante_mark`（跟着他，循环，z -1；左右对称）",
     "36 × 8",
     "他的技能打中敌人后、下一次普攻会更痛的那几秒：他脚下一圈金色的小菱形，一闪一闪地转（参考 ksante_base_p_diamond）。**中间留空**，"
     "**左右对称**，4 帧循环。",
     GO,
     "A RING OF GOLD DIAMONDS, 4 frames, a seamless loop, " + LR + ": a flat ring on the ground round his feet (an "
     "ellipse 32 squares wide and 6 tall) made of 10 tiny gold diamonds, each winking bright in turn so the light runs "
     "round; the middle EMPTY.",
     row(4, 36, 8) + "; the ellipse's middle on the cell's middle; " + HIM + " (only his feet reach the cell)."),
    ("a_swipe", "普攻：陀斧挥过的弧光（画进他的帧），4 帧", "画进他自己的 attack 帧（bake_caster_fx；朝右）", "40 × 32",
     "陀斧往前横扫的那一下：一道青白色的宽弧形风光，从他身后上方扫到身前下方，带几粒沙尘（参考 ksante_base_ba_swipe_bg、p_swipe_light）。"
     "**朝右**（画进他的帧里，不用对称），4 帧。",
     TE + ", " + SA,
     "A SWING ARC, 4 frames, " + FWD + ": 1 the start of a thick crescent of teal-white wind at the upper left; 2 the "
     "crescent swept round in front of him (from the upper left over to the lower right, 30 squares long, 6 thick at its "
     "middle, white along its leading edge); 3 the crescent at the lower right thinning, sand specks thrown off its tail; "
     "4 fading teal and sand specks.",
     row(4, 40, 32) + "; " + HIM + " - his feet on the cell's bottom row, 14 squares from its left edge."),
    # ---- Q Ntofo Strikes
    ("q_crack", "Q 无双陀斧一、二段：往前的一道裂地（画进他的帧），5 帧", "画进他自己的 skill / skill_b 帧（bake_caster_fx；朝右）",
     "44 × 16",
     "陀斧砸地，地面往前裂开一道短短的直线：裂缝一路往右延伸，裂缝上冒起沙尘和青色的水花一样的能量（参考 ksante_base_q_ground_crack_fill、"
     "q_linearsplashes_02、q_rect_flash、q_melee_dust）。**朝右**，5 帧。",
     SA + ", " + TE + ", " + RO,
     "A LINE OF CRACKED GROUND, 5 frames, " + FWD + ": 1 a flash where the ntofo hits at the left; 2 a crack in the "
     "ground running 20 squares to the right, sand puffing up along it; 3 the crack 38 squares long, teal splashes of "
     "energy leaping up along it like water (4 to 7 squares tall), stone chips; 4 the splashes falling, dust drifting; "
     "5 the crack and a little dust fading. " + SOLID + ".",
     row(5, 44, 16) + "; the crack lies on the cell's 3rd row from the bottom; he stands at the cell's left edge (not "
     "drawn), the ntofo striking 4 squares from the left."),
    ("q_hit", "Q 一、二段打中的敌人，3 帧", "view_effects `league_ksante_q_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被裂地打中：一团沙尘往上冒，几滴青色能量溅开（参考 ksante_base_q_hit、q_sand_smoke）。**左右对称**，3 帧。",
     SA + ", " + TE,
     "A SAND BURST HIT, 3 frames, " + LR + ": 1 a teal-white flash 6 squares across low in the cell; 2 a puff of sand "
     "dust 10 squares wide rising, 4 teal drops flying out at mirrored places; 3 the dust thinning, the drops falling.",
     row(3, 14, 14) + CENTER),
    ("q_slow", "Q 减速（敌人脚下，循环），4 帧", "view_buffs `league_ksante_q_slow`（跟着目标，循环，z -1；左右对称）", "20 × 6",
     "被减速的敌人脚下：一小圈沙尘在打转。**中间留空**，**左右对称**，4 帧循环。",
     SA,
     "A SWIRL OF SAND, 4 frames, a seamless loop, " + LR + ": a flat ring of sand dust round the target's feet (an "
     "ellipse 18 squares wide and 4 tall), puffs of dust moving round it in turn; the middle EMPTY.",
     row(4, 20, 6) + "; the ellipse's middle on the cell's middle; " + TARGET + " (only its feet reach the cell)."),
    ("q3_burst", "Q 三段：两把陀斧砸地的爆发（画进他的帧），5 帧", "画进他自己的 skill_c 帧（bake_caster_fx；朝右）", "36 × 22",
     "两把陀斧一起砸在身前：地面炸开，沙土和石块往上往前喷，一道青色的冲击波开始往右推（之后由 q3_wave 接着飞）"
     "（参考 ksante_base_q_walldestruction、q_spike2、q_blastshapes）。**朝右**，5 帧。",
     SA + ", " + TE + ", " + RO,
     "A GROUND ERUPTION, 5 frames, " + FWD + ": 1 a white-teal flash on the ground in front of him; 2 the ground bursting "
     "up in front: a fan of sand and stone shards thrown up and forward (16 squares tall), a teal glow at its base; "
     "3 a wall of teal energy rising and starting to roll to the right, rocks flying; 4 the wall leaving the cell at the "
     "right, dust settling; 5 dust and a few shards. " + SOLID + ".",
     row(5, 36, 22) + "; the burst's base on the cell's bottom row, starting 6 squares from its left edge; he stands at "
     "the cell's left edge (not drawn)."),
    ("q3_wave", "Q 三段：往前推的冲击波（弹道，循环），4 帧", "view_projectiles `league_ksante_q3_wave`（随飞行方向转；上下对称）",
     "40 × 16",
     "往前推、把敌人拉回来的冲击波：一道横着的青色能量浪，里面卷着沙尘，前沿最亮，后面拖着沙尘尾迹（参考 ksante_base_q3_crack_trail、"
     "q_waves、q_air_swoosh）。**朝右飞、后面在左，上下对称**，4 帧循环。",
     TE + ", " + SA,
     "A ROLLING SHOCKWAVE, 4 frames, a seamless loop, " + TB + ": a horizontal surge of teal energy 24 squares long and "
     "12 tall at its front (a bright white-teal crescent leading edge at the right, curving back above and below the "
     "middle line), sand dust churning inside it, a tapering sand trail 14 squares long behind it; each frame the crest "
     "and the dust churn.",
     row(4, 40, 16) + "; the wave's middle on the cell's middle row, its leading edge 2 squares from the right edge."),
    ("q3_hit", "Q 三段打中的敌人（被拉回来），4 帧", "view_effects `league_ksante_q3_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "被冲击波卷中：青色的能量浪拍在身上，沙尘四溅。**左右对称**，4 帧。",
     TE + ", " + SA,
     "A WAVE CRASH HIT, 4 frames, " + LR + ": 1 a teal-white flash 8 squares across; 2 a ring of teal energy splashing "
     "out 16 squares wide with sand in it; 3 the splash breaking into teal drops and dust at mirrored places; 4 fading "
     "drops and dust.",
     row(4, 18, 18) + CENTER),
    # ---- W Path Maker
    ("w_brace", "W 辟路先锋：蓄力减伤（他身上），6 帧", "view_effects `league_ksante_w_brace`（他身上，z 3；左右对称）", "52 × 54",
     "顶着陀斧蓄力的 0.75 秒：他身边一层青色的护盾光一点点合拢，护盾外圈闪着小光点（参考 ksante_base_w_shieldbegin、e_shield_outer）。"
     "**只画护盾的外圈，中间他的身体位置留空**，**左右对称**，6 帧（越来越亮）。",
     TE,
     "A BRACING SHIELD, 6 frames, " + LR + ": a shell of teal light round an upright big body (only its broken outline "
     "and a few bright streaks: 48 squares wide, 50 tall, its bottom open at the ground), small sparkles running along "
     "it; frame by frame it closes and brightens, frame 6 brightest with a white rim. The middle EMPTY where his body is.",
     row(6, 52, 54) + "; " + HIM + " (his feet on the cell's bottom row, 2 squares up)."),
    ("w_trail", "W 冲撞时脚下扬起的沙尘（画进他的帧），4 帧", "画进他自己的 skill2_dash 帧（bake_caster_fx；朝右）", "32 × 18",
     "他顶着陀斧往前冲时，脚后跟扬起一路沙尘往后飘（参考 ksante_base_w_wave_texture、q_sand_smoke）。**朝右**（尘往左后方飘），4 帧循环。",
     SA,
     "A DUST TRAIL, 4 frames, a seamless loop, " + FWD + ": clouds of sand dust kicked up at the right (where his feet "
     "are) and streaming back to the left along the ground, rising up to 12 squares, thinning towards the left; each "
     "frame the clouds roll back.",
     row(4, 32, 18) + "; his feet at the cell's bottom right corner (not drawn)."),
    ("w_land", "W 撞上的那一下（地上），5 帧", "view_effects `league_ksante_w_land`（他身上撞到的地方，不跟随，z -1；左右对称）",
     "56 × 24",
     "撞到敌人那一下：地上炸开一圈沙尘冲击环（从斜上方看的椭圆，约 52 格宽、14 格高），石块往外飞，几道青色的光往上冲（参考 "
     "ksante_base_w_ring_02、w_wave_rock_mult、w_front_cone_v02）。**左右对称**，5 帧。",
     SA + ", " + TE + ", " + RO,
     "A GROUND IMPACT, 5 frames, " + LR + ": 1 a white-teal flash in the middle of the ground; 2 a flat ring of sand "
     "dust spreading on the ground (an ellipse 36 squares wide and 10 tall) with 4 short teal light streaks shooting up; "
     "3 the ring 52 wide, stone chips flying out at mirrored places; 4 the dust ring thinning, chips falling; 5 last dust "
     "and specks. " + SOLID + ".",
     row(5, 56, 24) + "; the ground ellipse's middle 8 squares above the cell's bottom, centered."),
    ("w_hit", "W 撞中的敌人（击退、晕眩），4 帧", "view_effects `league_ksante_w_hit`（跟随目标，z 2；左右对称）", "18 × 20",
     "被撞中：青白色的撞击星形一闪、石屑飞散，头上转起一圈小星星（晕眩）。**左右对称**，4 帧。",
     TE + ", " + RO + ", " + GO,
     "A RAM HIT, 4 frames, " + LR + ": 1 a teal-white impact star 12 squares across in the lower middle with 4 stone "
     "chips; 2 the star fading, the chips further out, a ring of 4 tiny gold stars appearing at the top; 3 the star ring "
     "turning; 4 the stars fading. " + SOLID + ".",
     row(4, 18, 20) + CENTER),
    # ---- R All Out
    ("r_hit", "R 傲岸雄姿：盾击打中的敌人，4 帧", "view_effects `league_ksante_r_hit`（跟随目标，z 2；左右对称）", "22 × 22",
     "被大招撞飞的那一下：一团金橙色的爆光，几道光线往四周射出（参考 ksante_base_r_ray_shockwave、r_slam_arrow）。**左右对称**，4 帧。",
     GO + ", " + SA,
     "A GOLD BLAST HIT, 4 frames, " + LR + ": 1 a white-gold flash 10 squares across; 2 a gold burst 18 squares across "
     "with 8 short light rays shooting out at mirrored places; 3 the rays longer and thinner, sand specks; 4 fading "
     "rays and specks.",
     row(4, 22, 22) + CENTER),
    ("r_slam", "R 追上去砸地（敌人脚下），6 帧", "view_effects `league_ksante_r_slam`（跟随目标，z -1；左右对称）", "64 × 44",
     "他追上去把敌人砸在地上：地上砸出一个碎裂的坑（从斜上方看的椭圆），金色的光柱从坑里冲起，石块和沙尘飞起来（参考 ksante_base_r_crater、"
     "r_rockcrater_mult、r_flame_ring、r_groundsmoke02）。**左右对称**，6 帧：落下一闪、坑裂开、光柱最高、石块飞散、尘土、消失。",
     GO + ", " + SA + ", " + RO,
     "A CRATER SLAM, 6 frames, " + LR + ": 1 a white-gold flash on the ground in the middle; 2 a cracked crater on the "
     "ground (an ellipse 40 squares wide and 12 tall, its cracks radiating, glowing gold); 3 a column of gold light 30 "
     "squares tall rising from the crater, a flat gold shock ring spreading (an ellipse 60 wide and 16 tall, only its "
     "rim lit); 4 rocks and sand thrown up and out at mirrored places, the column fading; 5 dust settling round the "
     "crater; 6 the crater's last glow and dust. " + SOLID + ".",
     row(6, 64, 44) + "; the crater's middle 8 squares above the cell's bottom, centered; " + TARGET + "."),
    ("ao_on", "R 进入全盛姿态的那一下（他身上），6 帧", "view_effects `league_ksante_ao_on`（他身上，z 3；左右对称）", "60 × 58",
     "他甩开陀斧、进入全盛姿态：胸口一下爆出金白色的光，金色的菱形纹样和紫蓝色的刀光往外旋转散开，最后在他身边留下一圈光（参考 "
     "ksante_base_r_weapon_glow、r_rainbow_glow、ao_w_blade_sub_texture、kentepattern）。**左右对称**，6 帧。第 1、2 帧的光可以盖住他，"
     "之后中间留空。",
     GO + ", " + VI + ", " + TE,
     "AN ALL OUT BURST, 6 frames, " + LR + ": 1 a white-gold flash 16 squares across at the chest height of a hunched big "
     "body; 2 a big gold burst 34 squares across with 8 gold kente diamonds flying out; 3 the diamonds spinning outward "
     "with violet-blue blades of light between them (curved streaks, mirrored), the middle opening up; 4 a ring of gold "
     "and violet light round the body (only its rim: 50 squares wide, 50 tall); 5 the ring breaking into gold and violet "
     "sparks; 6 last sparks. From frame 3 the middle is EMPTY where his body is.",
     row(6, 60, 58) + "; " + HIM_AO + " (his feet on the cell's bottom row, 2 squares up)."),
    ("ao_aura", "全盛姿态（他身上，循环），4 帧", "view_buffs `league_ksante_ao`（跟着他，循环，z -1；左右对称）", "58 × 14",
     "全盛的 15 秒：他脚下一圈紫蓝色和金色的光焰，边上一闪一闪地往上窜（参考 ksante_base_r_underglow、ao_w_wind）。**中间留空**，"
     "**左右对称**，4 帧循环。",
     VI + ", " + GO,
     "AN ALL OUT AURA, 4 frames, a seamless loop, " + LR + ": a flat ring of violet-blue light on the ground round his "
     "feet (an ellipse 52 squares wide and 8 tall, only its rim lit), small violet and gold flame tongues licking up from "
     "the rim (up to 6 squares) in turn, a few gold motes rising; the middle EMPTY.",
     row(4, 58, 14) + "; the ellipse's middle 4 squares above the cell's bottom, centered; " + HIM_AO +
     " (only his feet reach the cell)."),
    ("ao_swipe", "全盛普攻：两根长棍横扫的弧光（画进他的帧），4 帧", "画进他自己的 ao_attack 帧（bake_caster_fx；朝右）", "70 × 30",
     "全盛的普攻：两根长棍往两边抡开，两道紫蓝色带金边的宽弧光从他身前往左右两边扫出去（参考 ksante_base_ao_w_wind、ao_w_blade_sub_texture）。"
     "画进他的帧里（不用对称），4 帧。",
     VI + ", " + GO,
     "A DOUBLE SWEEP, 4 frames, " + FWD + ": 1 two thick violet-blue crescents starting in front of his chest; 2 the "
     "crescents sweeping out to both sides (the right one a little bigger and in front, 30 squares long each, gold "
     "leading edges); 3 the crescents at their widest, thinning, gold sparks thrown off; 4 fading violet and gold specks.",
     row(4, 70, 30) + "; " + HIM_AO + " - his feet on the cell's bottom row, centered."),
]
BIG_FX = ["q3_wave", "w_brace", "w_land", "r_slam", "ao_on", "ao_aura"]
FLYING = ["q3_wave"]
FORWARD = ["a_swipe", "q_crack", "q3_burst", "w_trail", "ao_swipe"]

GROUPS = [
    ("a_hit p_hit p_mark a_swipe", ["ksante_base_hit_region", "ksante_base_ba_swipe_bg", "ksante_base_ba_passive_swipe_bg",
                                    "ksante_base_p_swipe_light", "ksante_base_kentepattern", "ksante_base_p_diamond"]),
    ("q_crack q_hit q_slow", ["ksante_base_q_ground_crack_fill", "ksante_base_q_linearsplashes_02", "ksante_base_q_hit",
                              "ksante_base_q_sand_smoke", "ksante_base_q_melee_dust", "ksante_base_q_rect_flash"]),
    ("q3_burst q3_wave q3_hit", ["ksante_base_q3_crack_trail", "ksante_base_q_waves", "ksante_base_q_walldestruction",
                                 "ksante_base_q_air_swoosh", "ksante_base_q_spike2", "ksante_base_q3_indicator_ring"]),
    ("w_brace w_trail w_land w_hit", ["ksante_base_w_shieldbegin", "ksante_base_e_shield_outer", "ksante_base_w_wave_texture",
                                      "ksante_base_w_front_cone_v02", "ksante_base_w_ring_02", "ksante_base_w_wave_rock_mult"]),
    ("r_hit r_slam", ["ksante_base_r_crater", "ksante_base_r_ray_shockwave", "ksante_base_r_rockcrater_mult",
                      "ksante_base_r_flame_ring", "ksante_base_r_slam_arrow", "ksante_base_r_groundsmoke02"]),
    ("ao_on ao_aura ao_swipe", ["ksante_base_r_weapon_glow", "ksante_base_r_rainbow_glow", "ksante_base_ao_w_blade_sub_texture",
                                "ksante_base_ao_w_cracks_tex", "ksante_base_r_underglow", "ksante_base_ao_w_wind"]),
]


def design_1x(name):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(RF.lp(os.path.join(HD, name))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / PPU, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Both stances at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x("idle.png"), design_1x("ao_idle.png")]
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
    d.text((8, 36), f"奎桑提 普通 {figs[0].shape[1]}×{figs[0].shape[0]} 格、全盛 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape, figs[1].shape


def design_sheet(path):
    """Both designs at 4x, their own squares (PPU 1.5)."""
    ims = [np.asarray(Image.open(RF.lp(os.path.join(HD, n))).convert("RGBA")) for n in ("idle.png", "ao_idle.png")]
    W = sum(a.shape[1] * 4 + 32 for a in ims)
    H = max(a.shape[0] for a in ims) * 4 + 32
    bg = Image.new("RGBA", (W, H), (225, 225, 225, 255))
    x = 16
    for a in ims:
        bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (x, H - 16 - a.shape[0] * 4))
        x += a.shape[1] * 4 + 32
    bg.convert("RGB").save(path)


def document(shapes):
    (h, w), (ah, aw) = shapes[0][:2], shapes[1][:2]
    L = []
    a = L.append
    a("# 纳祖芒荣耀 奎桑提：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/ksante_designs.png`：左边普通姿态——3/4 正面朝右的大块头，深红外套、"
      "金色护肩和金绳徽章、蓝紫围巾、黑络腮胡，两把嵌青色水晶的青石陀斧竖在身边；右边全盛姿态——弓背半蹲、两根长棍甩开）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），普通姿态 {h} 格高、{w} 格宽，全盛 {ah} 格高、{aw} 格宽；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/ksante_size.png`：两种姿态放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奎桑提自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**陀斧的能量是青色（像水花一样的青白色光），配沙土色的尘烟和青灰色的石屑**；"
      "**被动和大招是金色**（肯特布纹样的菱形）；**全盛姿态多了紫蓝色的刀光**。")
    a("> - **特效要亮**：每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **光、尘烟、光环、冲击波都没有黑描边**；**实物**（石屑、碎石块）有 1 格近黑描边。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（`ao_on` 的第 1、2 帧除外）。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q3_wave`）"
      "**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进他自己帧里的**（`" + "`、`".join(FORWARD) +
      "`）**朝右画，不用对称**（跟着他的身体一起翻转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ksante_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/ksante_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「血性本能」 | 陀斧横扫；技能打中过的敌人，下一次普攻额外伤害 | `a_swipe` · `a_hit` · `p_mark` · `p_hit` |")
    a("| 技能 1 = Q「无双陀斧」 | 一、二段往前裂地减速；第三段两把陀斧砸地，冲击波把敌人拉回来 | `q_crack` · `q_hit` · `q_slow` · "
      "`q3_burst` · `q3_wave` · `q3_hit` |")
    a("| 技能 2 = W「辟路先锋」 | 顶着陀斧蓄力减伤（带护盾），然后冲撞击退、晕眩 | `w_brace` · `w_trail` · `w_land` · `w_hit` |")
    a("| 大招「傲岸雄姿」 | 盾击撞飞敌人，追上去砸地，进入全盛姿态 15 秒 | `r_hit` · `r_slam` · `ao_on` · `ao_aura` · `ao_swipe` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、尘烟、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实物——石屑、碎石块——有 1 格近黑描边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("青色能量", TEAL), ("沙土尘烟", SAND), ("青灰石屑（实物）", ROCK), ("金色（被动、大招）", GOLD),
                        ("紫蓝刀光（全盛）", VIOLET)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（冲击环、坑、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 三段冲击波宽 9000，"
      "W 撞击半径 16000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `ksante_fx_{name}.png`：{title}\n")
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
        a(f"| `ksante_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_ksante_fx`（小的）和 `league_ksante_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_ksante.py 的 views：p_mark 的 tag 是 `p_mark`，buff 名是 `league_ksante_mark`；ao_aura 的 buff 名是 `league_ksante_ao`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；朝前的（{'、'.join(FORWARD)}）用 tools/fix/bake_caster_fx.py 画进他的帧"
      "（attack / skill / skill_b / skill_c / skill2_dash / ao_attack），不进表；其余断言左右对称；w_brace、ao_on、p_mark、ao_aura 跟随他。")
    a("- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="ksante_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "ksante_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_ksante.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "ksante_designs.png"))
    shapes = size_sheet(os.path.join(out, "design", "ksante_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"ksante_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
