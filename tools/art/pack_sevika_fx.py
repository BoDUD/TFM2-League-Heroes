#!/usr/bin/env python3
"""Build sevika_fx_pack.zip: step 3 of Sevika's sprite - Codex draws her effects and her three skill icons
(pack_renni_fx.py's way).

    python tools/lol/fx_ref_sevika.py           # her TFT particle textures -> C:/t/sv_work/fxref
    python tools/art/pack_sevika_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name sevika_fx_redo_pack]

The pack (C:/t/sv_work/fx/sevika_fx_pack, zipped into --out, default dist/sevika_packs) holds PROMPTS.md (also written
to assets/source/sevika/PROMPTS_FX.md), design/sevika_design.png (the approved idle at 4x on its own squares),
design/sevika_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (her own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_sevika.py, the user's picks 2026-10-29: top,
plan A 「百变铁手」): view_projectiles q_flame, p_rocket, e_fist; view_effects a_hit, a2_hit, p, p_rocket_hit, e_hit,
r_hit, r_kill, p_jackpot, p_shield; view_buffs q_burn, p_shimmer, p_triple, e_stun, r_bleed. Plus the three skill icons.
The punches, the flamethrower's stance, the extendo wind-up and the chomp are in her own frames.
Her colours: Jinx's graffiti on her arm - MAGENTA and CYAN paint, BRASS and TEAL plates; the flamethrower's FIRE; the
slot machine's GOLD coins and coloured bulbs; SHIMMER's violet-pink glow.
Red side: every effect picture is symmetric left to right (the client never mirrors an effect picture); the three
flying pictures (the flame, the rockets, the fist) point RIGHT and are turned with their flight, so they are drawn
symmetric TOP to BOTTOM instead (turned half round to the left they read the same).
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
DOC = os.path.join(ROOT, "assets", "source", "sevika", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "sevika", "hd")
NAME = "sevika_fx_pack"
PPU = 1.8

FIRE = "#FFFFFF, #FFF4B0, #FFC840, #F07A18, #B8360C, #5A1606"     # the flamethrower
PAINT = "#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44"             # Jinx's magenta graffiti
CYAN = "#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C"              # Jinx's cyan, the claws
BRASS = "#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A"             # the arm's brass
TEAL = "#C8FFF0, #6EE0C8, #2AA894, #146A5E, #0A3430"              # the arm's teal plates
GOLD = "#FFFFFF, #FFF6A0, #FFD830, #E09A10, #8A5206"              # the jackpot's coins
SHIMMER = "#FFE6FF, #F4A8FF, #C858F0, #7C24B8, #3C0E66"           # Shimmer's violet-pink glow
SMOKE = "#E8E4E0, #B0A8A4, #7A7270, #4A4444, #262222"             # rocket smoke, dust
CRIMSON = "#FF9A9A, #E83A4A, #A8162A, #5E0A18"                    # the bleed
FI = f"a fire ramp ({FIRE})"
PA = f"a magenta paint ramp ({PAINT})"
CY = f"a cyan paint ramp ({CYAN})"
BR = f"a brass ramp ({BRASS})"
TE = f"a teal metal ramp ({TEAL})"
GO = f"a gold coin ramp ({GOLD})"
SH = f"a Shimmer violet-pink ramp ({SHIMMER})"
SM = f"a smoke grey ramp ({SMOKE})"
CR = f"a crimson ramp ({CRIMSON})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and "
         "teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink "
         "glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning")
HER = "the broad-shouldered woman stands in the middle, not drawn: 30 squares wide and 39 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark brown frame with little "
        "riveted brass corners and a few magenta and cyan graffiti scratches, a deep murky teal-black inside, the "
        "symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and "
        "readable at 64 px")
ARM = ("her MECHANICAL ARM (brass, teal plates with magenta spikes, a huge pair of bright cyan claws with magenta "
       "tips)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：铁拳打中，4 帧", "view_effects `tft_sevika_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "机械臂一拳打在人身上：一个白热的**冲击闪光**，一圈**黄铜色的冲击环**，几点洋红和青色的漆点往两边崩开。**左右对称**，4 帧。",
     BR + ", " + PA + ", " + CY,
     "A HEAVY PUNCH IMPACT, 4 frames, " + LR + ": 1 a white-hot flash 7 squares across; 2 a brass-yellow shock ring 14 "
     "squares wide and 6 tall, a few magenta and cyan PAINT flecks (1-2 squares) knocked out to both sides "
     "(mirrored); 3 the ring wider and thinner, the flecks farther; 4 the last flecks fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("a2_hit", "第三下：爪钳夹住，5 帧", "view_effects `tft_sevika_a2_hit`（跟随目标，z 2；左右对称）", "20 × 20",
     "每第三下爪钳一夹：上下两排**亮青色的爪尖**猛地合拢（像一张嘴咬下），合上的地方炸开白光和洋红色的漆点。**左右对称**，5 帧。",
     CY + ", " + PA + ", " + BR,
     "A CLAW CLAMP, 5 frames, " + LR + ": 1 two rows of bright CYAN claw tips with magenta points, one above and one "
     "below the middle, wide open (16 squares wide, 14 apart); 2 the rows snapping toward each other; 3 the claws "
     "shut in the middle, a white flash 8 squares across where they meet, magenta paint flecks bursting out to both "
     "sides (mirrored); 4 the claws gone, the flecks flying; 5 the last flecks. " + MAGIC + ".",
     row(5, 20, 20) + CENTER),
    ("p", "百变铁手：老虎机转起来，8 帧", "view_effects `tft_sevika_p`（跟随她，在她头顶，z 4；左右对称）", "30 × 16",
     "每次放技能，她肩上的老虎机转一圈：她**头顶**冒出一个小老虎机面板——红棕色的框、**三个奶白色的转轮窗**，转轮里的图案"
     "（金币、星星、菱形，都要左右对称的图案）**往下滚动**，最后三个转轮一个接一个停下、框上的小灯珠一闪。**左右对称**（图案也对称），8 帧。",
     BR + ", " + GO + ", " + PA + ", " + CY,
     "A SLOT MACHINE SPIN over her head, 8 frames, " + LR + ": a small slot machine panel 26 squares wide and 12 tall "
     "(a red-brown frame with a brass rim, a row of tiny pink, purple and cyan bulbs along the top and bottom, THREE "
     "cream-white REEL windows side by side); 1 the panel pops up; 2-5 the reels spinning (their symbols - a gold "
     "coin, a star, a diamond, all symmetric shapes, never letters or numbers - streaking downward); 6 the left and "
     "right reels stop, 7 the middle one stops, 8 the bulbs flash. The panel and every symbol mirrored square for "
     "square. " + MAGIC + ".",
     row(8, 30, 16) + CENTER),
    ("p_rocket", "改件·火箭：飞行中，4 帧循环", "view_projectiles `tft_sevika_p_rocket`（飞向目标，随飞行方向旋转；上下对称、朝右）", "14 × 8",
     "从老虎机里射出的小火箭（金克丝的）：一枚**洋红和青色涂鸦的小火箭**，头朝右，尾巴喷着橙色的火和一小串灰烟。"
     "**朝右、上下对称**（游戏会按飞行方向转），4 帧循环。",
     PA + ", " + CY + ", " + FI + ", " + SM,
     "A SMALL ROCKET IN FLIGHT, 4 looping frames, " + TB + ": a little rocket 8 squares long and 3 tall, the nose "
     "pointing RIGHT, the body painted MAGENTA with a CYAN stripe and a cyan nose cone, two tiny fins (one above, one "
     "below); at its tail a flickering orange-white FLAME 3 squares long and a short puff of grey smoke behind it; "
     "frames 1-4 the flame flickering. " + MAGIC + ".",
     row(4, 14, 8) + CENTER),
    ("p_rocket_hit", "改件·火箭：炸开，5 帧", "view_effects `tft_sevika_p_rocket_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "小火箭炸在人身上：一团**橙色的小爆炸**，夹着洋红和青色的彩色碎纸 / 漆点四溅，最后一缕灰烟。**左右对称**，5 帧。",
     FI + ", " + PA + ", " + CY + ", " + SM,
     "A SMALL ROCKET BLAST, 5 frames, " + LR + ": 1 a white-yellow flash 6 squares across; 2 an orange fireball 12 "
     "squares across, magenta and cyan CONFETTI / paint bits (1-2 squares) bursting out to both sides (mirrored); "
     "3 the fireball breaking up, dark orange edges; 4 a grey smoke puff, the confetti falling; 5 the last wisps. "
     + MAGIC + ".",
     row(5, 18, 18) + CENTER),
    ("p_shield", "改件·护盾：亮起，6 帧", "view_effects `tft_sevika_p_shield`（跟随她，z 3；左右对称）", "40 × 44",
     "随到护盾：她身体两侧亮起两道**黄铜框的青色护盾弧**（像拼起来的铁板），弧上几颗金色铆钉一闪，洋红色的涂鸦条纹。身体位置留空。**左右对称**，6 帧。",
     TE + ", " + BR + ", " + PA,
     "A SHIELD PLATING, 6 frames, " + LR + ", " + HER + ": 1 two bright glints at both sides of her chest; 2 at both "
     "sides of her (mirrored) a tall curved TEAL shield arc 4 squares wide and 32 tall made of riveted plates with a "
     "BRASS rim and a magenta graffiti stripe, a white flash where it locks on; 3 the arcs whole, gold rivets "
     "glinting; 4 a glint running up the arcs; 5 the arcs dimmer; 6 only the rims glinting. The middle (the body) "
     "left empty. " + MAGIC + ".",
     row(6, 40, 44) + CENTER),
    ("p_jackpot", "改件·三倍：中头奖！8 帧", "view_effects `tft_sevika_p_jackpot`（大表，跟随她，z 4；左右对称）", "56 × 60",
     "中头奖：她头顶炸开一个**金币喷泉**——一大把金币往上喷、再往两边落下，夹着洋红和青色的彩带碎纸，头顶一圈金光，最后金币落到她脚边闪一闪。"
     "身体位置留空（金币从头顶和两侧落下）。**左右对称**，8 帧。",
     GO + ", " + PA + ", " + CY,
     "A JACKPOT FOUNTAIN, 8 frames, " + LR + ", " + HER + " (her head near the middle of the cell's upper half): 1 a "
     "gold flash 10 squares across over her head; 2 a column of GOLD COINS (round, 3 squares, a white glint each) "
     "shooting up from over her head, a gold light ring 30 squares wide and 8 tall; 3 the coins at the top of the "
     "cell spreading out to both sides (mirrored), magenta and cyan CONFETTI strips among them; 4-6 the coins and "
     "confetti raining down both sides of her; 7 the coins bouncing at her feet with glints; 8 the last glints. The "
     "middle (the body) left empty. " + MAGIC + ".",
     row(8, 56, 60) + CENTER),
    ("p_shimmer", "改件·微光：药劲上头（攻速），6 帧循环", "view_buffs `tft_sevika_p_shimmer`（跟随她，z 3；左右对称）", "36 × 44",
     "随到微光：身体两侧一闪一闪的**紫粉色光焰**（只画外圈几格亮边），几点紫粉色光点往上飘，脚下一圈淡淡的紫光。身体位置留空。**左右对称**，6 帧循环。",
     SH,
     "A SHIMMER RUSH, 6 looping frames, " + LR + ", " + HER + ": at both sides of her (mirrored) tall flickering "
     "violet-pink FLAME tongues 3 squares wide and 20 tall hugging her outline (only a bright edge and a few lit "
     "squares), a faint violet ring " + GROUND_E + " 28 squares wide and 7 tall at the bottom, a few pink motes "
     "drifting up; frames 1-6 the flames flickering and the motes rising. The middle (the body) left empty. "
     + MAGIC + ".",
     row(6, 36, 44) + CENTER),
    ("p_triple", "改件·三倍：头奖待命，6 帧循环", "view_buffs `tft_sevika_p_triple`（跟随她，头顶，z 4；左右对称）", "24 × 10",
     "中了头奖、下一个技能强化：她头顶转着**三枚金币**，一闪一闪。**左右对称**，6 帧循环。",
     GO + ", " + PA,
     "A JACKPOT READY over her head, 6 looping frames, " + LR + ": three GOLD COINS (3 squares round, a white glint) "
     "circling on a flat ring 20 squares wide and 4 tall, two tiny magenta sparkles between them; frames 1-6 the "
     "coins going round and glinting in turn. " + MAGIC + ".",
     row(6, 24, 10) + CENTER),
    ("q_flame", "喷火器：火焰，6 帧循环", "view_projectiles `tft_sevika_q_flame`（大表，一道从她指向目标的线，随方向旋转；上下对称、朝右）", "48 × 22",
     "机械臂爪钳里喷出来的**火焰**：从格子**左边中间**（她的爪钳）喷出，往右越喷越宽，像一个横放的喇叭；中心白黄、外圈橙红，"
     "前端翻滚着火舌和几缕黑烟，夹着几点洋红色的火星（金克丝的改装）。**朝右、上下对称**（游戏会按方向转，转到左边也一样），6 帧循环。",
     FI + ", " + PA + ", " + SM,
     "A FLAMETHROWER JET, 6 looping frames, " + TB + ": the fire starts at the LEFT EDGE of the cell, in the middle of "
     "its height (her claws), and roars out to the RIGHT, widening like a horizontal cone: 4 squares tall at the left "
     "edge, 20 squares tall at the right end; a white-yellow core along the middle, orange around it, red-orange "
     "tongues at the edges, curling fire tongues and a few dark smoke puffs at the far right end, a few magenta "
     "sparks in the flame; frames 1-6 the tongues rolling forward and flickering. " + MAGIC + ".",
     row(6, 48, 22) + CENTER),
    ("q_burn", "喷火器：被灼烧，6 帧循环", "view_buffs `tft_sevika_q_burn`（跟随被烧的人，身上，z 3；左右对称）", "16 × 20",
     "被喷火烧着的人身上：几簇**小火苗**往上窜，带着几点火星和一缕烟。**左右对称**，6 帧循环。",
     FI + ", " + SM,
     "A BURN, 6 looping frames, " + LR + ": two or three small FLAMES (3 squares wide, 6-9 tall) licking upward over "
     "the unit, white-yellow cores and orange-red tips, a few sparks and a thin grey smoke wisp rising above; "
     "frames 1-6 the flames flickering. " + MAGIC + ".",
     row(6, 16, 20) + CENTER),
    ("e_fist", "伸缩拳：飞出去的拳头，4 帧循环", "view_projectiles `tft_sevika_e_fist`（飞向目标，随飞行方向旋转；上下对称、朝右）", "30 × 14",
     "伸缩拳：机械臂的**大铁拳**（合上的爪钳像一张闭着的嘴）往右飞，后面拖着一根**黄铜色的弹簧**，弹簧一圈一圈地伸长。"
     "**朝右、上下对称**（爪钳上下两半一样），4 帧循环。",
     TE + ", " + BR + ", " + CY + ", " + PA,
     "AN EXTENDO-PUNCH FIST IN FLIGHT, 4 looping frames, " + TB + ": at the RIGHT end a big closed fist 12 squares "
     "long and 12 tall - teal armour plates with magenta spikes (as many above as below) and bright CYAN closed "
     "claws at its front (an upper and a lower claw, like a shut jaw); behind it, to the left, a BRASS coiled SPRING "
     "4 squares tall stretching back to the left edge of the cell (6-7 coils); frames 1-4 the spring coils "
     "stretching and a short white streak or two behind the fist. " + MAGIC + ".",
     row(4, 30, 14) + CENTER),
    ("e_hit", "伸缩拳：打中，6 帧", "view_effects `tft_sevika_e_hit`（跟随目标，z 2；左右对称）", "24 × 24",
     "铁拳打中人：一个大的白热闪光，一圈**黄铜色的冲击波**，洋红和青色的漆点大把溅开，几颗螺栓崩飞。**左右对称**，6 帧。",
     BR + ", " + PA + ", " + CY,
     "A BIG PUNCH IMPACT, 6 frames, " + LR + ": 1 a big white-hot flash 12 squares across; 2 a thick brass-yellow "
     "shock ring 20 squares wide and 8 tall, a burst of MAGENTA and CYAN paint splats (2-3 squares) thrown out to "
     "both sides (mirrored), two little gold bolts flying; 3 the ring wider and thinner, the splats farther; 4 the "
     "splats falling; 5 a puff of dust; 6 the last specks. " + MAGIC + ".",
     row(6, 24, 24) + CENTER),
    ("e_stun", "伸缩拳：撞晕，6 帧循环", "view_buffs `tft_sevika_e_stun`（跟随被晕的人，头顶，z 4；左右对称）", "20 × 10",
     "被撞晕的人头顶：几颗**洋红和青色的小星星**转圈。**左右对称**，6 帧循环。",
     PA + ", " + CY + ", " + BR,
     "A STUN OVER THE HEAD, 6 looping frames, " + LR + ": three small stars (3 squares) in magenta, cyan and brass "
     "circling on a flat ring 16 squares wide and 4 tall; frames 1-6 the stars going round. " + MAGIC + ".",
     row(6, 20, 10) + CENTER),
    ("r_hit", "嚼一嚼：咬一口，5 帧", "view_effects `tft_sevika_r_hit`（跟随目标，z 2；左右对称）", "26 × 26",
     "爪钳像一张大嘴咬下：上下两排**大的亮青色尖牙**（洋红尖头）猛地咬合在人身上，咬合处一道白光，洋红色的漆和金属碎片四溅。**左右对称**，5 帧。",
     CY + ", " + PA + ", " + BR,
     "A BIG CHOMP, 5 frames, " + LR + ": 1 a huge jaw - an upper and a lower row of big bright CYAN fangs with "
     "magenta tips - wide open around the middle (22 squares wide, 18 apart); 2 the jaws slamming shut; 3 the fangs "
     "interlocked across the middle, a white flash 12 squares wide along the bite, magenta paint and brass shards "
     "spraying out to both sides (mirrored); 4 the jaw gone, the shards falling; 5 the last specks. " + MAGIC + ".",
     row(5, 26, 26) + CENTER),
    ("r_bleed", "嚼一嚼：流血，6 帧循环", "view_buffs `tft_sevika_r_bleed`（跟随被咬的人，身上，z 3；左右对称）", "14 × 16",
     "被咬过之后流血：身上几道**暗红色的爪痕**一闪，几滴暗红的血珠往下滴。**左右对称**，6 帧循环。",
     CR,
     "A BLEED, 6 looping frames, " + LR + ": two short dark crimson claw SCRATCHES (1 square thick, 5 long, slanted, "
     "mirrored) on the unit, glinting in turn, and two or three crimson DROPS (1-2 squares) dripping down and "
     "fading; frames 1-6 the drops falling. " + MAGIC + ".",
     row(6, 14, 16) + CENTER),
    ("r_kill", "嚼一嚼：咬死（斩杀），8 帧", "view_effects `tft_sevika_r_kill`（大表，跟随目标，z 3；左右对称）", "44 × 44",
     "目标血太少被一口咬死：一张**巨大的青色铁嘴**从上下合拢，咬合时爆出一大片**洋红和青色的油漆喷溅**（金克丝的涂鸦），"
     "中间一个白色的大星形闪光，最后漆点慢慢落下。**左右对称**，8 帧。",
     CY + ", " + PA + ", " + BR + ", " + GO,
     "AN EXECUTION CHOMP, 8 frames, " + LR + ": 1 a HUGE jaw (upper and lower rows of bright CYAN fangs with magenta "
     "tips, brass gums) wide open, 40 squares wide; 2 the jaws slamming shut; 3 the fangs locked across the middle, "
     "a big white STAR flash 20 squares across; 4 a big burst of MAGENTA and CYAN PAINT SPLATTER blasting out to both "
     "sides (mirrored) with a few gold sparks, the jaw fading; 5 the splatter at its widest, 40 squares; 6-7 the "
     "paint drops falling; 8 a few last drops. " + MAGIC + ".",
     row(8, 44, 44) + CENTER),
]
ICONS = [
    ("skill", "技能 1「喷火器」图标", "skill_icons[0] `asset/tft/icons/tft_sevika_skill`",
     "机械臂的爪钳张开朝右，从里面喷出一大团橙色的火焰。",
     ICON + ": " + ARM + "'s claws open at the left, a big roaring cone of orange-white FIRE blasting out of them to "
     "the right, a few magenta sparks. Colours: " + FI + ", " + CY + ", " + BR + ", " + TE + "."),
    ("skill2", "技能 2「伸缩拳」图标", "skill_icons[1] `asset/tft/icons/tft_sevika_skill2`",
     "一个合着爪钳的大铁拳从左下往右上飞出，后面拖着一根黄铜弹簧，拳头前面一道冲击光。",
     ICON + ": a big closed mechanical FIST (teal plates, magenta spikes, cyan claws shut) flying from the lower left "
     "to the upper right on a stretched BRASS SPRING, a white impact flash in front of it. Colours: " + TE + ", " + BR
     + ", " + CY + ", " + PA + "."),
    ("ult", "大招「嚼一嚼」图标", "skill_icons[2] `asset/tft/icons/tft_sevika_ult`",
     "一张巨大的青色铁嘴（上下两排尖牙）正在咬合，洋红色的油漆四溅。",
     ICON + ": a HUGE mechanical JAW seen from the front - an upper and a lower row of bright CYAN fangs with magenta "
     "tips biting shut in the middle, MAGENTA paint splattering out, a gold glint. Colours: " + CY + ", " + PA + ", "
     + BR + ", " + GO + "."),
]
BIG_FX = ["q_flame", "p_jackpot", "r_kill"]

GROUPS = [
    ("q_flame q_burn (the flamethrower)", ["tft7_shyvana_base_r_flamemesh", "petchoncc_skin36_fire02",
                                           "flame_trail_gradient", "tft7_shyvana_firesmoke_2x2", "color-flamesword"]),
    ("a_hit e_hit e_fist (the punches)", ["tft13_lieutenant_base_boxingglove_extend", "tft13_lieutenant_base_q_hit_blast",
                                          "tft13_lieutenant_base_q_hit_flash", "jinx_skin60_ba_hit_impact",
                                          "tft6_jayce_base_shockwave"]),
    ("p_rocket p_rocket_hit (Jinx's rockets)", ["tft13_jinx_base_particles_1_291", "jinx_skin60_smear_sparks",
                                                "ziggs_base_q_trail_smoke", "tft13_jinx_base_burnmark",
                                                "base_splatters_dissolve"]),
    ("p p_jackpot p_triple (slot machine, coins)", ["common_coin04", "draven_base_color-goldcoin", "tft_coin_boom_trail",
                                                    "preseason_turret_shield_break_coin", "tft13_lieutenant_base_star"]),
    ("r_hit r_kill a2_hit (the chomp, paint)", ["tft13_lieutenant_base_q_hanpaint_trail05", "tft13_lieutenant_goo_rgb",
                                                "tft13_lieutenant_rework_base_q_groundcracks_v05",
                                                "tft13_lieutenant_base_q_detonationring_02", "common_blooddrops"]),
    ("p_shield p_shimmer e_stun", ["akshan_skin10_shield", "tft9_nilah_base_w_shieldedge", "aura_self_128_4",
                                   "energymote_64", "base_sparkle"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Sevika at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"塞薇卡 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 塞薇卡：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/sevika_design.png`："
      "祖安的女打手、炼金男爵，肩宽结实，深棕往后梳的头发；左臂是一条被金克丝涂成洋红 / 青色的巨大黄铜机械臂，肩上一台小老虎机，手是一副亮青色的大爪钳）。"
      f"塞薇卡在游戏里是**高清**的（每个游戏格子里约 1.8×1.8 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sevika_size.png`：塞薇卡缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里塞薇卡自己的特效贴图（**灰色的形状，游戏里再染色**：火焰、伸缩拳、火箭、金币、油漆、冲击环），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **塞薇卡的特效是她那条被金克丝改装过的机械臂**：喷火器的**橙色火焰**、黄铜和青绿色的金属、金克丝的**洋红 / 青色油漆和涂鸦**、"
      "老虎机的**金币**和彩色灯珠、**微光（Shimmer）的紫粉色光**；不要魔法符文，不要光滑的霓虹光束，不要闪电。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、火焰、冲击波、烟、油漆溅射没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：留在原地的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**三张会飞的图（`q_flame` 火焰、`p_rocket` 火箭、"
      "`e_fist` 拳头）都朝右画、严格上下对称**：游戏按飞行方向把它们转过去，转到左边时上下颠倒也要看起来一样。"
      "出拳、平举机械臂、冲刺、咬下的动作都画在她自己的动作帧里，这里不画。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sevika_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `sevika_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「百变铁手」 | 每次放技能，肩上的老虎机转一圈，随机一个改件：火箭（向随机敌人连射几枚小火箭）/ 护盾 / 微光（攻速）/ "
      "三倍（中头奖：这次技能强化） | `p` · `p_rocket` · `p_rocket_hit` · `p_shield` · `p_shimmer` · `p_jackpot` · `p_triple` |")
    a("| 普攻「机械铁拳」 | 机械臂一记重拳；每第三下爪钳一夹，伤害更高 | `a_hit` · `a2_hit` |")
    a("| 技能 1 =「喷火器」 | 机械臂平举，对前方扇形持续喷火、灼烧，喷火时自己减伤 | `q_flame` · `q_burn` |")
    a("| 技能 2 =「伸缩拳」 | 拳头带着弹簧射出去打中目标、击退；撞到后面的敌人，两人都眩晕 | `e_fist` · `e_hit` · `e_stun` |")
    a("| 大招 =「嚼一嚼」 | 冲到目标面前，爪钳像嘴一样连咬两口：眩晕 + 流血；血量很低时直接咬死，再冲向附近下一个 | `r_hit` · `r_bleed` · `r_kill` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火焰、冲击波、烟没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火焰（喷火器）", FIRE), ("洋红油漆（金克丝）", PAINT), ("青色油漆、爪钳", CYAN), ("黄铜（机械臂）", BRASS),
                        ("青绿金属（机械臂装甲）", TEAL), ("金币（老虎机）", GOLD), ("微光紫粉", SHIMMER), ("烟、尘土", SMOKE),
                        ("暗红（流血）", CRIMSON)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 不要文字、字母、数字（老虎机的转轮里画金币、星星、菱形这些对称的图案）。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sevika_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, zh, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `sevika_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `sevika_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `sevika_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_sevika_fx`（小的）和 `tft_sevika_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 留在原地的全部断言左右对称；q_flame、p_rocket、e_fist 断言上下对称（朝右）。")
    a("- 老虎机（p）每次 Q / E / R 都播；火箭、护盾、微光、头奖由 tft.dll 摇到后播 / 挂上（--plain 的数据每次放三分之一的火箭、护盾、微光）。")
    a("- q_flame 是 LineRangeProjectile 的图（从她到目标的线，锚点在线的起点那头：导入时核对）。")
    a("- 用 `pixel_1x/` 切格（import_renni_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sevika_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "sevika_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_sevika.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "sevika_design.png"))
    shape = size_sheet(os.path.join(out, "design", "sevika_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in ("q_flame", "p_rocket", "e_fist") else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sevika_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"sevika_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
                   if not a.only else []), f, ensure_ascii=False, indent=1)
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
