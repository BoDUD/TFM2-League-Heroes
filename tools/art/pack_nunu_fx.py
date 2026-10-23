#!/usr/bin/env python3
"""Build nunu_fx_pack.zip: step 3 of Nunu & Willump's sprite - Codex (or Gemini) draws their effects (pack_illaoi_fx.py's
way).

    python tools/lol/fx_ref_nunu.py           # League's particle textures -> C:/t/nu_work/fxref (Riot's art, local only)
    python tools/art/pack_nunu_fx.py [--no-zip] [--out DIR] [--only a_hit,p_hit --name nunu_fx_redo_pack]

The pack (C:/t/nu_work/fx/nunu_fx_pack, zipped into --out, default dist/nunu_packs) holds PROMPTS.md (also written to
assets/source/nunu/PROMPTS_FX.md), design/nunu_design.png (the idle at 4x, its own squares), design/nunu_size.png (at
game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Nunu & Willump, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_nunu.py, the user's picks 2026-10-23: jungle, layout A - W / E
/ R, Q in the passive): view_effects a_hit, p_hit, q_hit, e_hit, e_root_hit, w_dust, w_hit, w_burst, w_big, r_storm,
r_burst, r_hit; view_projectiles e_ball; view_buffs p_on, p_buff, e_slow, e_mark, e_root, r_slow, r_shield. The
snowball Willump rolls (W) is drawn in his own frames by the pose pack, not here.
League's colours: SNOW white and FROST blue (the snowballs, the blizzard, the ice), Willump's glowing CYAN (his eyes,
the swirls on his fur, the Freljord's call), pale ice crystals; the dirt and snow kicked up. Red side: the client never
mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right; a projectile is
turned with its flight, so it is drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/nu_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "nunu", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "nunu", "hd")
NAME = "nunu_fx_pack"
PPU = 1.37

SNOW = "#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0"              # snowballs, snow puffs, the blizzard's flakes
FROST = "#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A"    # frost, ice, the cold blue light
CYAN = "#FFFFFF, #C8FFFF, #6CF0FF, #20C0E8, #0A7AB0"              # Willump's glow: his eyes, his swirls, the call
ICE = "#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0"                # ice crystals, shackles, the shield
DIRT = "#E8DCC8, #B8A890, #887860, #584C3C"                        # dirt and pebbles kicked up under the snow
SN = f"a snow ramp ({SNOW})"
FR = f"a frost-blue ramp ({FROST})"
CY = f"a glowing cyan ramp ({CYAN})"
IC = f"a pale ice ramp ({ICE})"
DI = f"a dirt ramp ({DIRT})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
FRELJORD = ("everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice "
            "crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
THEM = "Nunu & Willump stand in the middle, not drawn: 37 squares wide and 46 tall"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack and passive
    ("a_hit", "普攻：威朗普的爪子拍中，3 帧", "view_effects `league_nunu_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "威朗普一爪子拍在敌人身上：一团白色的雪粉炸开，几道冰蓝色的爪痕光（参考 attack_swipe、ba_flash_sharp）。**左右对称**，3 帧。",
     SN + ", " + FR,
     "A CLAW SWIPE LANDING, 3 frames, " + LR + ": 1 a white flash 5 squares across; 2 a puff of white snow powder 11 "
     "across with two short frost-blue claw streaks crossing in an X; 3 the snow powder drifting out and fading. " +
     FRELJORD + ".",
     row(3, 12, 12) + CENTER),
    ("p_hit", "被动溅射：拍到周围的人，3 帧", "view_effects `league_nunu_p_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "弗雷尔卓德的召唤期间，威朗普的普攻溅到旁边的敌人：一小团冰蓝色的雪雾。**左右对称**，3 帧。",
     FR + ", " + SN,
     "A SMALL SPLASH OF FROST on a unit, 3 frames, " + LR + ": 1 a frost-blue flash 3 across; 2 a ring of frost-blue "
     "snow powder 9 across; 3 the powder fading. " + FRELJORD + ".",
     row(3, 10, 10) + CENTER),
    ("q_hit", "被动里的吞噬：威朗普咬一口，4 帧", "view_effects `league_nunu_q_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "威朗普张嘴一口咬下去：**上下两排白色的大牙印**合上（参考 q_biteswipe），一团雪粉和冰屑炸开，几颗青色的光点往上飘。**左右对称**，4 帧。",
     SN + ", " + CY,
     "A BIG BITE, 4 frames, " + LR + ": 1 two rows of big white pointed teeth shapes, an upper row and a lower row 14 "
     "squares wide, open with a gap of 8 squares; 2 the rows snapping shut in the middle, a white flash; 3 a burst of "
     "snow powder and ice chips 15 across; 4 the powder fading, a few glowing cyan motes rising. " + FRELJORD + ".",
     row(4, 16, 16) + CENTER),
    ("p_on", "弗雷尔卓德的召唤：自己脚下的寒风，4 帧循环", "view_buffs `league_nunu_p_on`（跟随，脚下，z -1；左右对称）", "40 × 12",
     "被动触发后努努和威朗普脚下：一圈**青色发光的寒风旋**往前卷（参考 nunu_wind_swirl、p_bufftransfer），几粒雪花。**左右对称**，4 帧循环。",
     CY + ", " + SN,
     "A WINTER WIND " + FEET + ", 4 looping frames, " + LR + ", " + THEM + ": a ring of glowing cyan wind streaks 38 "
     "squares wide and 10 tall swirling round the feet, mirrored, a few white snowflakes in it; the streaks turn a step "
     "round the ring each frame. " + FRELJORD + ".",
     row(4, 40, 12) + CENTER),
    ("p_buff", "弗雷尔卓德的召唤：队友脚下的寒风，4 帧循环", "view_buffs `league_nunu_p_buff`（跟随队友，脚下，z -1；左右对称）",
     "20 × 8",
     "被动给附近一个队友加攻速移速：他脚下一圈小的青色寒风旋，和 p_on 一样的画法，小一号。**左右对称**，4 帧循环。",
     CY + ", " + SN,
     "A SMALL WINTER WIND " + FEET + ", 4 looping frames, " + LR + ": a ring of glowing cyan wind streaks 18 squares "
     "wide and 6 tall, mirrored, two snowflakes; the streaks turn a step each frame. " + FRELJORD + ".",
     row(4, 20, 8) + CENTER),
    # ---- skill: W Biggest Snowball Ever!
    ("w_dust", "史上最大雪球：滚动时扬起的雪尘，6 帧", "view_effects `league_nunu_w_dust`（地上，不跟随，z -1；左右对称）",
     "28 × 12",
     "威朗普推着雪球开始滚的那一下，地上扬起的一团雪尘和碎冰（参考 w_hit_dust、w_trail、snowdust）。**左右对称**，6 帧。",
     SN + ", " + DI,
     "SNOW KICKED UP, 6 frames, " + LR + ", " + FEET + ", centred: 1 a low white puff 8 wide; 2 two puffs of snow "
     "rolling out to both sides 18 wide, a few dirt pebbles; 3 the puffs 24 wide and 6 tall; 4 the puffs 26 wide, "
     "thinning; 5 wisps of snow; 6 a few flakes. " + FRELJORD + ".",
     row(6, 28, 12) + CENTER),
    ("w_hit", "史上最大雪球：撞中的人身上，4 帧", "view_effects `league_nunu_w_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "被雪球撞飞的人身上：一团白色的雪块和冰屑炸开。**左右对称**，4 帧。",
     SN + ", " + FR,
     "A SNOWBALL HIT ON A UNIT, 4 frames, " + LR + ": 1 a white flash 6 across; 2 chunks of packed snow bursting out 14 "
     "across at mirrored places, frost-blue shading on their undersides; 3 the chunks 17 across, smaller, with snow "
     "powder; 4 the powder fading. " + FRELJORD + ".",
     row(4, 18, 18) + CENTER),
    ("w_burst", "史上最大雪球：小雪球撞碎，6 帧", "view_effects `league_nunu_w_burst`（大表，地上，不跟随，z 2；左右对称）",
     "40 × 26",
     "雪球滚得不远就撞上：雪球**炸成一大团雪块**，雪粉往两边喷，地上一圈白雪（参考 w_hit_flash、w_hit_dust、snow_chunks）。**左右对称**，6 帧。",
     SN + ", " + FR + ", " + DI,
     "A SNOWBALL SHATTERING, 6 frames, " + LR + ", the ball's centre 8 squares above the ground in the cell's middle: 1 "
     "a white flash 14 across; 2 the ball bursting into big chunks of packed snow flying out 28 across at mirrored "
     "places, frost-blue shading under them; 3 the chunks 36 across and falling, snow powder spraying up 10 squares; "
     "4 the chunks landing in a ring of snow 38 wide on the ground; 5 the powder settling; 6 a low drift of snow and a "
     "few flakes. " + FRELJORD + ".",
     row(6, 40, 26) + CENTER),
    ("w_big", "史上最大雪球：滚大了的雪球撞碎，7 帧", "view_effects `league_nunu_w_big`（大表，地上，不跟随，z 2；左右对称）",
     "56 × 34",
     "雪球滚得远、滚得大再撞上：比 w_burst 大一圈，**一圈冰蓝色的冲击波**贴着地面扩开，雪块飞得更高更远。**左右对称**，7 帧。",
     SN + ", " + FR + ", " + IC,
     "A GIANT SNOWBALL SHATTERING, 7 frames, " + LR + ", the ball's centre 12 squares above the ground in the cell's "
     "middle: 1 a white flash 20 across; 2 the ball bursting, big snow chunks flying out 36 across; 3 a frost-blue "
     "shockwave ring on the ground 40 wide and 12 tall, the chunks 48 across and rising, snow powder spraying 16 up; 4 "
     "the ring 52 wide, the chunks falling; 5 the chunks landing in a snow ring, ice crystals glinting; 6 the powder "
     "settling; 7 a low drift and a few glints. " + FRELJORD + ".",
     row(7, 56, 34) + CENTER),
    # ---- skill2: E Snowball Barrage
    ("e_ball", "雪球飞射：飞出去的小雪球，4 帧循环", "view_projectiles `league_nunu_e_ball`（弹道，z 2；上下对称）", "12 × 8",
     "努努扔出的小雪球：一颗白色的雪球（4 格大），后面一道冰蓝色的雪粉尾巴（参考 e_snowball、e_missile_trail）。**朝右飞，上下对称**，4 帧循环。",
     SN + ", " + FR,
     "A SMALL FLYING SNOWBALL, 4 looping frames, " + TB + ": a round white snowball 4 squares across at the front "
     "(right), one white highlight square in its middle row, frost-blue shading on its back half, and a trail of "
     "frost-blue snow powder 7 squares long behind it on the left; the trail flickers a step each frame. " + FRELJORD +
     ".",
     row(4, 12, 8) + CENTER),
    ("e_hit", "雪球飞射：雪球打中，3 帧", "view_effects `league_nunu_e_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "小雪球砸在人身上：一小团白色雪粉炸开（参考 e_hit_flash、e_snow_spark）。**左右对称**，3 帧。",
     SN + ", " + FR,
     "A SNOWBALL SPLAT, 3 frames, " + LR + ": 1 a white flash 3 across; 2 a star of white snow powder 9 across; 3 the "
     "powder falling and fading. " + FRELJORD + ".",
     row(3, 10, 10) + CENTER),
    ("e_slow", "雪球飞射：被打中减速，4 帧循环", "view_buffs `league_nunu_e_slow`（跟随，脚下，z -1；左右对称）", "16 × 8",
     "被雪球打中的人脚下：一圈积雪和冰蓝色的寒气（参考 e_ground_pool_erosion）。**左右对称**，4 帧循环。",
     SN + ", " + FR,
     "A PATCH OF SNOW " + FEET + ", 4 looping frames, " + LR + ": a low patch of white snow 14 squares wide and 4 tall "
     "with frost-blue cold mist curling over it, mirrored; the mist curls a step each frame. " + FRELJORD + ".",
     row(4, 16, 8) + CENTER),
    ("e_mark", "雪球飞射：被打中的英雄头上的雪花记号，4 帧循环", "view_buffs `league_nunu_e_mark`（跟随，头顶，z 3；左右对称）",
     "10 × 10",
     "被雪球打中的英雄头顶：一枚**冰蓝色的雪花记号**一闪一闪（参考 e_mark），提醒扔完会把他冻住。**左右对称**，4 帧循环。",
     IC + ", " + CY,
     "A SNOWFLAKE MARK floating over a head, 4 looping frames, " + LR + ": a six-armed snowflake 8 squares across drawn in "
     "pale ice-blue lines with a glowing cyan centre; it pulses brighter in frames 2-3. The cell's bottom sits on top of "
     "the head. " + FRELJORD + ".",
     row(4, 10, 10) + CENTER),
    ("e_root_hit", "雪球飞射：冻住的那一下，5 帧", "view_effects `league_nunu_e_root_hit`（跟随目标，z 2；左右对称）", "22 × 30",
     "扔完雪球后，被打中的英雄**脚下冒出冰柱把他冻住**的那一下：冰尖从地里刺出来，冰屑炸开（参考 e_icerock、e_vfx_root_snow、e_ice_sparks）。"
     "**左右对称**，5 帧。",
     IC + ", " + FR + ", " + SN,
     "ICE BURSTING UP AROUND A UNIT, 5 frames, " + LR + ", " + TARGET + ": 1 a frost-blue crack on the ground 16 wide; "
     "2 pale ice spikes stabbing up round the feet to 8 squares high at mirrored places; 3 the spikes 14 high with ice "
     "chips and snow flying out; 4 the spikes standing, a white glint on each; 5 the chips gone, the spikes still. The "
     "body's place left empty. " + FRELJORD + ".",
     row(5, 22, 30) + CENTER),
    ("e_root", "雪球飞射：被冻住，4 帧循环", "view_buffs `league_nunu_e_root`（跟随，脚下，z 3；左右对称）", "20 × 14",
     "被冻住的英雄：**腿上包着一圈冰块**（从脚到膝盖），冰上一点白色的反光在闪。**只画腿外面一圈冰，身体位置留空**。**左右对称**，4 帧循环。",
     IC + ", " + FR,
     "ICE SHACKLES on the legs, 4 looping frames, " + LR + ", the bottom of a standing unit 16 squares wide in the middle, "
     "not drawn: a jagged block of pale ice 18 squares wide and 12 tall round the feet and shins, its outer facets in "
     "3 ice shades, a few frost-blue cracks, a white glint that moves to a new facet each frame. The legs' place inside "
     "left mostly see-through: only the ice's rim and facets. " + FRELJORD + ".",
     row(4, 20, 14) + CENTER),
    # ---- ult: R Absolute Zero
    ("r_storm", "绝对零度：引导中的暴风雪，6 帧循环", "view_effects `league_nunu_r_storm`（大表，跟随，z -1；左右对称）",
     "110 × 44",
     "努努和威朗普引导大招：脚下一大圈**冰蓝色的冰霜圆**（参考 r_ground、r_ring_outer、r_icecrack），圈里刮着**白色的雪花**和寒风往中间卷"
     "（参考 r_snow_flake、r_snowdrift）。圈很大（直径约 110 格），**只画地上的冰圈和飘的雪，中间他们站的位置留空**。**左右对称**，6 帧循环（引导约 2.5 秒）。",
     FR + ", " + SN + ", " + IC,
     "A BLIZZARD ON THE GROUND, 6 looping frames, " + LR + ", " + FEET + ": a big frost-blue ring 108 squares wide and 36 "
     "tall on the ground, its edge a band of ice crystals and frost cracks, a faint frost fill inside; white snowflakes "
     "and streaks of wind swirling over the ring towards its middle at mirrored places, up to 8 squares above the "
     "ground; the flakes and streaks move a step round the ring each frame. The middle 40 squares left clear (they "
     "stand there). " + FRELJORD + ".",
     row(6, 110, 44) + CENTER),
    ("r_burst", "绝对零度：引导结束的爆发，7 帧", "view_effects `league_nunu_r_burst`（大表，地上，不跟随，z 2；左右对称）",
     "110 × 50",
     "大招结束那一下：整个冰圈**猛地炸开**，白光一闪，冰柱和冰屑从圈里往上刺，一圈白色的寒气冲击波往外扩（参考 r_circle_splash、p_nova_ground、"
     "z_crystals）。**左右对称**，7 帧。",
     FR + ", " + IC + ", " + SN,
     "THE BLIZZARD EXPLODING, 7 frames, " + LR + ", " + FEET + ", centred: 1 a huge white-blue flash over the whole ring "
     "100 wide and 30 tall; 2 jagged ice spikes stabbing up across the ring to 16 squares high, a frost-blue shockwave "
     "ring 104 wide; 3 the spikes shattering into ice chips flying up and out, white cold mist rolling; 4 the chips "
     "falling, the mist ring 108 wide and low; 5 frost cracks glowing on the ground; 6 the mist thinning; 7 a few "
     "flakes and glints. " + FRELJORD + ".",
     row(7, 110, 50) + CENTER),
    ("r_hit", "绝对零度：爆发打中的人，4 帧", "view_effects `league_nunu_r_hit`（跟随目标，z 2；左右对称）", "16 × 20",
     "被大招爆发打中的人身上：一团冰屑和白色寒气炸开。**左右对称**，4 帧。",
     IC + ", " + SN,
     "A FROST BURST ON A UNIT, 4 frames, " + LR + ": 1 a white flash 5 across; 2 shards of pale ice bursting out 13 "
     "across; 3 the shards 15 across with white cold mist; 4 the mist fading. " + FRELJORD + ".",
     row(4, 16, 20) + CENTER),
    ("r_slow", "绝对零度：圈里被减速，4 帧循环", "view_buffs `league_nunu_r_slow`（跟随，身上，z 3；左右对称）", "18 × 36",
     "在暴风雪里被减速的人：身上**结了一层霜**（身体外圈一圈白色的霜边），雪花打在他身上。**只画外圈，身体位置留空**。**左右对称**，4 帧循环。",
     IC + ", " + SN,
     "FROSTED OVER, 4 looping frames, " + LR + ", " + TARGET + ": a thin rim of white frost 1 square outside the body's "
     "edge (an upright shape 16 wide and 34 tall, drawn only as its rim, the inside empty), little ice crystals stuck on "
     "it at mirrored places, a few snowflakes blowing past; the flakes move a step each frame. " + FRELJORD + ".",
     row(4, 18, 36) + CENTER),
    ("r_shield", "绝对零度：引导中的冰护盾，6 帧循环", "view_buffs `league_nunu_r_shield`（跟随他们，z 3；左右对称）",
     "44 × 50",
     "引导大招时努努和威朗普身上的护盾：一层**半透明的淡冰蓝色冰壳**围着他们（只画外圈的冰棱和几道反光），上面有寒气飘（参考 z_shieldring）。"
     "**只画外圈，身体位置留空**。**左右对称**，6 帧循环。",
     IC + ", " + CY,
     "AN ICE SHELL round them, 6 looping frames, " + LR + ", " + THEM + ": a dome-shaped rim of pale ice 42 squares wide "
     "and 48 tall drawn only as its edge (2 squares thick) with ice facets and 3-4 white glints, a glowing cyan line "
     "along its base on the ground, wisps of cold mist rising from it; the glints move round the rim a step each frame. "
     "The inside left empty. " + FRELJORD + ".",
     row(6, 44, 50) + CENTER),
]
BIG_FX = ["w_burst", "w_big", "r_storm", "r_burst"]
FLYING = ["e_ball"]
FORWARD = []

GROUPS = [
    ("a_hit p_hit (claw swipes)", ["nunu_base_attack_swipe_v01", "nunu_base_ba2", "nunu_base_ba_flash_sharp",
                                   "nunu_base_p_impactpuffs_2x2"]),
    ("q_hit (Consume)", ["nunu_base_q_biteswipe_v02", "nunu_base_ba_heal_sparks", "snow_chunks", "nunu_base_snowdust"]),
    ("p_on p_buff (the call)", ["color_nunu_wind_swirl", "nunu_base_p_bufftransfer_4x4_sparkle",
                                "nunu_base_p_bufftransfer_meshswipe", "nunu_base_p_cloudring"]),
    ("w_dust w_hit w_burst w_big (snowball)", ["nunu_base_w_hit_dust", "nunu_base_w_hit_flash", "nunu_base_w_trail",
                                               "nunu_base_z_snowchunks_01"]),
    ("e_ball e_hit e_slow (barrage)", ["nunu_base_e_snowball_v02", "nunu_base_e_missile_trail", "nunu_base_e_hit_flash",
                                       "nunu_base_e_ground_pool_erosion"]),
    ("e_mark e_root_hit e_root", ["nunu_base_e_mark_v15", "nunu_base_e_icerock", "nunu_base_e_vfx_root_snow",
                                  "nunu_base_e_ice_sparks"]),
    ("r_storm (Absolute Zero)", ["nunu_base_r_ground_nocrack_v01", "nunu_base_r_ring_outer", "nunu_base_r_snow_flake",
                                 "nunu_base_r_snowdrift"]),
    ("r_burst r_hit r_shield", ["nunu_base_r_circle_splash", "nunu_base_p_nova_ground", "nunu_base_z_crystals",
                                "nunu_base_z_shieldring"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", ppu=PPU):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / ppu, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Nunu & Willump at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"努努和威朗普 {figs[0].shape[1]}×{figs[0].shape[0]} 格，"
                    f"原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
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
    a("# 雪原双子 努努和威朗普：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/nunu_design.png`：Q 版的大雪人威朗普——淡蓝白毛、蓝色螺旋纹、发蓝光的眼睛、"
      "棕色大鹿角——头上骑着小男孩努努，蓝兜帽、橙斗篷）。"
      f"他们在游戏里是**高清**的（每个游戏格子里 1.37×1.37 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/nunu_size.png`：努努和威朗普放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里努努自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**努努和威朗普来自冰雪的弗雷尔卓德，所有特效都是冬天的魔法**：压实的**白雪**、**冰蓝色的冰和寒气**、威朗普身上**发光的青色螺旋**、"
      "**冰晶**、雪粉和一点泥土，不要光滑的霓虹光束，也不要火。")
    a("> - **威朗普推的大雪球不在这份里**：它画在他推雪球的动作帧里（姿势包）；这里只画雪球滚动扬起的雪尘、撞碎时的爆开和打中的人身上。")
    a("> - **特效要亮**：每片雪、每道冰光都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **雪、冰光、寒气、冲击波都没有黑描边**（雪块和冰块也不要描黑边，用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nunu_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/nunu_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 威朗普用爪子拍 | `a_hit` |")
    a("| 被动「弗雷尔卓德的召唤」（并入 Q 吞噬） | 每第 3 下普攻是威朗普咬一口（回血，对小兵野怪更痛）；咬完他们和一个队友加攻速移速，普攻溅射周围 | "
      "`q_hit` · `p_on` · `p_buff` · `p_hit` |")
    a("| 技能 1 =「史上最大雪球！」 | 威朗普推着雪球冲向敌人，滚得越远越大，撞上把人击飞 | `w_dust` · `w_hit` · `w_burst` · `w_big` |")
    a("| 技能 2 =「雪球飞射」 | 努努连扔 6 个雪球（打中减速），扔完把被打中的英雄冻住 | `e_ball` · `e_hit` · `e_slow` · `e_mark` · "
      "`e_root_hit` · `e_root` |")
    a("| 大招 =「绝对零度」 | 原地引导一阵大暴风雪，圈里的人越来越慢，自己有冰护盾，结束时整圈爆开 | `r_storm` · `r_slow` · `r_shield` · "
      "`r_burst` · `r_hit` |\n")
    a("连招：**雪球 → 雪球飞射**（雪球把人撞飞，努努接着扔），**雪球飞射 → 绝对零度**（冻住的人跑不掉，大招引导更快），**绝对零度 → 吞噬**"
      "（暴风雪爆开后威朗普咬一口）。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**雪、冰光、寒气、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **都是冬天的魔法**：白雪、冰蓝寒气、青色螺旋光、冰晶、雪粉；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("白雪", SNOW), ("冰蓝寒气", FROST), ("威朗普的青光", CYAN), ("冰晶", ICE), ("泥土", DIRT)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（雪尘、冰圈、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `nunu_fx_{name}.png`：{title}\n")
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
        a(f"| `nunu_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_nunu_fx`（小的）和 `league_nunu_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_nunu.py 的 views）。雪球本身在威朗普的 skill / skill_roll 帧里（姿势包），w_dust 垫在起滚那一下，w_burst / w_big 是撞上的那一下"
      "（滚的时间短 / 长）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称；r_storm 跟随他们引导约 2.5 秒（循环），r_shield 同时长，e_root 0.75 秒。")
    a("- 用 `pixel_1x/` 切格（import_illaoi_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="nunu_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "nunu_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_nunu.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "nunu_design.png"))
    shape = size_sheet(os.path.join(out, "design", "nunu_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"nunu_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
