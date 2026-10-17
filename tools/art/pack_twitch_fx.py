#!/usr/bin/env python3
"""Build twitch_fx_pack.zip: step 3 of Twitch's sprite - Codex draws his effects (after tools/art/pack_khazix_fx.py).

    python tools/art/pack_twitch_fx.py [--no-zip] [--out DIR] [--only a_bolt,a_hit --name twitch_fx_redo_pack]

The pack (%TEMP%/tw_work/fx/twitch_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/twitch/PROMPTS_FX.md), design/twitch_design.png (8x), design/twitch_size.png (the design at 4x on the arena
colour with the feet line, a 10-px ruler and the base fighter beside him), design/twitch_shots.png (the finished action
frames at 4x from league/champions/league_twitch, with the point each picture starts from) and refs/lol_fx_ref.png
(League's own particle textures for Twitch, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/tw_work/fxref, extracted from Twitch.wad.client).
The effects are the views the kit binds (tools/kit/build_twitch.py: view_projectiles a_bolt, r_bolt, w_cask, w_pool;
view_effects a_hit, v_pop, w_hit, q_cast, q_out, q_reset, e_cast, r_cast, r_hit; view_buffs w_slow, q_as, r_on) and the
muzzle puff a_flash, baked into the attack's release frame (twitch_bake.json). League's colours: the venom's green
(the passive, W, E, R), the camouflage's violet-black smoke (Q), brass sparks. Light, smoke and splashes get no outline;
the bolt and the cask, objects, have one. Red side: the projectiles symmetric top to bottom, the buffs and the pictures
on him after the first tick symmetric left to right, the puddle both ways. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "tw_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "twitch", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "twitch_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VENOM = "#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C"     # Twitch's venom green: the passive, W, E, R
SMOKE = "#F4E8FF, #C8A8F0, #8A5CC0, #56347E, #2E1A48"             # the camouflage's violet-black smoke: Q
SPARK = "#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C"             # brass sparks: the muzzle, the reset
BRASS = "#0A0806, #7A4A10, #C88A1C, #FCC23A, #FFE68A, #8CD82A, #F2FFD0"   # the bolt and the cask (objects)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades "
        "and a white core - it must read on a dark battlefield), colours only from {ramps}.")
LEAD_OBJ = ("Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
            "a 1-square dark outline #0A0806 around the object, colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FIG = "do NOT draw the figure; leave its place empty"
VN = f"a venom green ramp ({VENOM})"
SM = f"a violet smoke ramp ({SMOKE})"
SK = f"a brass spark ramp ({SPARK})"
BR = f"brass and venom ({BRASS})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout, outlined object
FX = [
    # ---- the attack and the passive
    ("a_bolt", "普攻弩箭（飞行中，循环），4 帧",
     "view_projectiles `league_twitch_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "12 × 4",
     "图奇的弩箭：一根黄铜色的短箭，箭头是金色、带一点绿色毒液的光，后面拖两格淡绿光迹（参考 Arrow_Txt、AA_Posion_Smoke_Cloud）。"
     "朝右飞。**上下对称**。4 帧无缝循环（光迹闪一闪）。约 12 格长、4 格高。",
     BR,
     "a CROSSBOW BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a brass bolt 9 squares long "
     "and 1 square thick with a 3-square gold arrowhead pointing RIGHT, a tiny venom green glint on the head, a short "
     "pale green trail 3 squares long behind it; the trail flickers each frame.",
     row(4, 14, 6) + "; the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell.", True),
    ("a_flash", "普攻弩口的火光（烘进普攻第 3 帧），3 帧",
     "烘进普攻出手帧（`twitch_bake.json`：弩尖的位置，随人物朝向翻转）", "10 × 8",
     "弩箭射出去那一下弩口的一团绿色毒烟和黄铜色火星（参考 Z_Muzzle_Flash、AA_Posion_Smoke_Cloud）。朝右喷。3 帧。约 10 格宽、8 格高。",
     f"{VN} and {SK}",
     "a MUZZLE PUFF blowing to the RIGHT, 3 frames: 1 a bright pale green and white flash 6 squares across at the left "
     "middle with 3 brass sparks; 2 a puff of venom green smoke 8 squares across drifting right, 2 sparks; 3 the puff "
     "thinning into 3 small fading motes.",
     row(3, 12, 10) + "; the flash starts at the left middle of every cell.", False),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_twitch_a_hit`（跟随，画在人物上面）", "12",
     "弩箭打中、上了一层毒：一小团绿色毒液溅开，几滴绿毒往外飞（参考 P_Impact、common_aciddrops32）。约 12 格，居中画。",
     VN,
     "a VENOM SPLAT HIT, 4 frames: 1 a pale green-white splat 6 squares across at the center; 2 a venom green splash 10 "
     "squares across, 5 droplets flying out; 3 droplets falling, the splash breaking up; 4 a few fading drops.",
     row(4, 14, 14) + "; centered in every cell.", False),
    ("v_pop", "E 毒性爆发：每个中毒的敌人身上炸开，6 帧", "view_effects `league_twitch_v_pop`（跟随，画在人物上面）", "22",
     "毒性爆发：中毒的敌人身上炸开一团绿色的毒液爆炸，一圈毒刺往外扎，一团毒烟往上冒（参考 E_Tar_Spikes、E_Tar_Flash、E_Posion_Smoke_Cloud）。"
     "约 22 格，居中画。一个人身上有几层毒就会同时播几次（叠在一起），所以**每一帧都要亮**。",
     VN,
     "a TOXIC BURST, 6 frames: 1 a pale green-white flash 8 squares across at the center; 2 a venom green explosion 16 "
     "squares across with 8 sharp green spikes stabbing outward; 3 the spikes longest (20 squares across), a white core; "
     "4 the spikes breaking off, a cloud of green smoke rising; 5 the smoke drifting up, thinning; 6 a few fading wisps.",
     row(6, 24, 24) + "; centered in every cell.", False),
    # ---- W
    ("w_cask", "W 剧毒之桶：飞出去的毒桶（飞行中，循环），4 帧",
     "view_projectiles `league_twitch_w_cask`（抛物线飞行；上下对称）", "6 × 6",
     "图奇扔出去的毒桶：一个圆滚滚的小木桶，黄铜箍，桶口冒绿光，后面拖一小段绿色毒液（参考 W_Bottle_Txt、W_Acidball_Orb_Color、W_Mis_Trail）。"
     "**上下对称**（每一帧都对称：只让绿光和高光一闪一闪，不画旋转）。4 帧无缝循环。约 6 格。",
     BR,
     "a VENOM CASK in flight, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame: a round wooden cask 5 "
     "squares across with two brass hoops, its middle glowing venom green, 2 green droplets trailing to the LEFT; each "
     "frame the glow and the droplets pulse (no spinning).",
     row(4, 8, 8) + "; centered in every cell.", True),
    ("w_hit", "W 毒桶砸中（每个被砸中的人身上），5 帧", "view_effects `league_twitch_w_hit`（跟随，画在人物上面）", "16",
     "毒桶砸中：人身上溅满绿色毒液，几块碎木片和黄铜箍飞出去（参考 W_Splash、twitch_venom_bomb_splash、Venom_Bomb_Splash_A）。约 16 格，居中画。",
     f"{VN} and {SK}",
     "a VENOM SPLASH on a figure, 5 frames: 1 a pale green-white splash 8 squares across; 2 green venom splashing 14 squares "
     "across, 3 small brass splinters flying out; 3 venom dripping down, the splinters farther; 4 drips; 5 a few fading "
     "drops.",
     row(5, 18, 18) + "; centered in every cell.", False),
    ("w_pool", "W 毒池（地上，持续 3 秒，循环），4 帧",
     "view_projectiles `league_twitch_w_pool`（地上，不旋转，画在人物下面；上下左右都对称）", "56 × 22",
     "毒桶砸碎后地上的一滩绿色毒液：从斜上方看的扁椭圆，边上一圈亮绿，中间冒泡，几缕毒烟往上飘（参考 W_Splat_anim、W_Persist_Smoke_Color、W_Green_Ring）。"
     "**上下左右都对称**。4 帧无缝循环（气泡和烟换位置，但每一帧都对称）。约 56 格宽、22 格高——这是技能的范围（半径 28 格），画满。",
     VN,
     "a TOXIC PUDDLE on the ground seen from above at an angle, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT AND TOP "
     "TO BOTTOM in every frame: a flat venom green ellipse 54 squares wide and 20 tall with a bright pale green rim 1-2 "
     "squares thick and a darker green inside, 6 bubbles placed symmetrically (popping and growing frame to frame), a few "
     "thin green smoke wisps rising from it, symmetric too.",
     row(4, 58, 24) + "; centered in every cell.", False),
    ("w_slow", "W 减速（目标脚下，循环），4 帧", "view_buffs `league_twitch_w_slow`（画在脚下，左右对称）", "16 × 6",
     "被毒桶减速：脚下一小滩绿色毒液，几滴绿毒往下滴（参考 common_aciddrops32、stinkDrops_02）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。",
     VN,
     "a SLOWING VENOM PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a flat green ellipse "
     "puddle 14 squares wide and 4 tall, bubbling, 2 small drips falling into it each frame.",
     row(4, 18, 8) + "; centered in every cell.", False),
    # ---- Q
    ("q_cast", "Q 埋伏：隐身时炸开的毒烟（他身上），6 帧",
     "view_effects `league_twitch_q_cast`（技能第一 tick 播放、跟随；中心在站位点上面约 16 格）", "34 × 34",
     "图奇隐身：身边“噗”地炸开一团紫黑色的烟，烟里转着一圈绿光，几个小点散开（参考 Q_Bamf_Smoke_4x4、Q_Bamf_Swirl、Q_Cas_Dots）。"
     "**左右对称**，**中间留空**（人在中间）。6 帧：1 一圈光，2–4 烟炸开扩大，5–6 烟散开淡去。约 34 格宽、34 格高。",
     f"{SM} and {VN}",
     f"a STEALTH SMOKE POOF around a figure ({FIG}), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly "
     "empty: 1 a thin pale green ring 14 squares across at the center; 2-4 puffs of violet-black smoke bursting out round "
     "it to 32 squares across, a swirl of green motes inside; 5-6 the smoke thinning and fading upward.",
     row(6, 36, 36) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    ("q_out", "Q 现形（他身上，一闪），5 帧",
     "view_effects `league_twitch_q_out`（不跟随，左右对称；中心在站位点上面约 16 格）", "28",
     "从隐身里现形、攻速加成开始：一圈紫烟往外散开，一圈绿光闪一下（参考 Q_Camouflage_Ring_RGB、Q_Smoke）。**左右对称**，**中间留空**。约 28 格。",
     f"{SM} and {VN}",
     f"a REVEAL FLASH around a figure ({FIG}), 5 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left empty: 1 a "
     "flattened green ring 12 squares wide bright at his waist; 2-3 the ring widening to 26 squares, violet smoke wisps "
     "peeling off outward; 4 the smoke fading; 5 a few motes.",
     row(5, 30, 30) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    ("q_as", "Q 攻速加成（他身上，循环），4 帧", "view_buffs `league_twitch_q_as`（跟随，画在他身上，左右对称）", "26 × 12",
     "出隐身后的攻速加成：他腰两侧各一团小小的绿色毒火在跳（参考 Z_Green_Glow、Q_Buff_Colormap）。**左右对称**，**中间留空**（人在中间）。"
     "4 帧无缝循环。约 26 格宽、12 格高，两团各约 5 格，相距约 16 格。",
     VN,
     f"two small VENOM FLAMES at a figure's waist ({FIG}), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: one green-white "
     "flame 5 squares across on each side, 16 squares apart, the middle 12 squares empty; each frame the flames flicker and "
     "2 tiny motes rise.",
     row(4, 28, 14) + "; centered in every cell.", False),
    ("q_reset", "Q 刷新（击杀英雄，他头顶一闪），5 帧",
     "view_effects `league_twitch_q_reset`（不跟随，左右对称；中心在站位点上面约 34 格）", "16",
     "击杀英雄、埋伏刷新：他头顶亮一下一个小老鼠头的绿色标记（英雄联盟里中毒的人头上的小老鼠；参考 P_Rat_Icon）。**左右对称**。约 16 格，居中画。",
     f"{VN} and {SK}",
     "a RAT-HEAD GLINT, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a small green dot; 2 it opens into a simple rat-head icon 12 "
     "squares wide (two round ears, a pointed snout downward) in bright green with a white edge; 3 the icon brightest, 4 "
     "short brass rays round it; 4 the icon shrinking; 5 a fading dot.",
     row(5, 16, 16) + "; centered in every cell.", False),
    # ---- E
    ("e_cast", "E 毒性爆发：他身边炸开的毒云，6 帧",
     "view_effects `league_twitch_e_cast`（不跟随，画在人物下面，左右对称；中心在站位点上面约 12 格）", "44 × 30",
     "图奇放毒性爆发：身边一圈绿色毒云往外炸开，毒液像触手一样往四周甩（参考 E_Posion_Smoke_Cloud、E_Tar_Flash、W_Nova）。"
     "**左右对称**，**中间留空**（人在中间）。6 帧：1 一圈亮绿，2–4 毒云炸开扩大，5–6 散开淡去。约 44 格宽、30 格高。",
     VN,
     f"a TOXIC CLOUD BURST around a figure ({FIG}), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 14 squares left mostly "
     "empty: 1 a flattened pale green ring 16 squares wide at his waist; 2-4 green poison clouds and splashing venom "
     "streaks bursting outward to 42 squares wide and 28 tall; 5-6 the clouds thinning and fading.",
     row(6, 46, 32) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    # ---- R
    ("r_cast", "R 火力全开：开大的一下（他身上），6 帧",
     "view_effects `league_twitch_r_cast`（不跟随，左右对称；中心在站位点上面约 16 格）", "36 × 36",
     "图奇开大：身边一圈绿色的能量冲击波往外扩，几道绿色的光柱往上冲（参考 R_EnergyWave、R_Spotlight、R_Wispy_Ribbon）。**左右对称**，"
     "**中间留空**（人在中间）。6 帧：1 一圈光，2–4 冲击波扩大、光柱往上，5–6 散开。约 36 格宽、36 格高。",
     f"{VN} and {SK}",
     f"a POWER-UP SURGE around a figure ({FIG}), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly empty: "
     "1 a bright green ring 14 squares across at his waist; 2-4 the ring widening to 34 squares as a flattened shockwave, "
     "4 thin green light ribbons shooting up round him to 34 squares high, brass sparks; 5-6 the ribbons fading upward.",
     row(6, 38, 38) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    ("r_on", "R 火力全开中（他身上，循环，6 秒），4 帧", "view_buffs `league_twitch_r_on`（跟随，画在他身上，左右对称）", "30 × 36",
     "开大的 6 秒里：他身边一圈绿色的光丝在转，脚下一圈淡绿光（参考 R_Wispy_Ribbon、Z_Green_Glow）。**左右对称**，**中间留空**（人在中间）。"
     "4 帧无缝循环。约 30 格宽、36 格高。",
     VN,
     f"a GREEN POWER AURA around a figure ({FIG}), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT, the middle 18 squares "
     "wide left empty: thin green and pale green light ribbons (1 square thick) rising round the figure's place in a tall "
     "oval 28 squares wide and 34 tall, a flattened pale green ring at the feet, a few motes drifting up; each frame the "
     "ribbons move up a step.",
     row(4, 32, 38) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    ("r_bolt", "R 穿透弩箭（飞行中，循环），4 帧",
     "view_projectiles `league_twitch_r_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "22 × 6",
     "大招的穿透箭：一道绿色的能量箭，比普攻箭长一倍，箭头白亮，后面拖一条长长的绿光尾巴（参考 R_EnergyWave、common_AirSpiritStreak）。"
     "朝右飞。**上下对称**。4 帧无缝循环。约 22 格长、6 格高。",
     VN,
     "a PIERCING ENERGY BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a bright white-green "
     "arrowhead 4 squares long pointing RIGHT, a glowing green shaft 8 squares long, a tapering green light trail 10 "
     "squares long behind it; the trail ripples each frame.",
     row(4, 24, 8) + "; the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell.", False),
    ("r_hit", "R 穿透箭打中（每个被穿过的人身上），4 帧", "view_effects `league_twitch_r_hit`（跟随，画在人物上面）", "14",
     "穿透箭打中：一道绿色的能量火花横着炸开，几滴毒液溅出（参考 R_EnergyWave、P_Impact）。约 14 格，居中画。",
     f"{VN} and {SK}",
     "an ENERGY PIERCE HIT, 4 frames: 1 a horizontal white-green streak 12 squares long through the center; 2 a green burst "
     "10 squares across, 4 droplets and 3 brass sparks flying out; 3 sparks scattering; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell.", False),
]

GROUPS = [
    ("attack / passive", ["Twitch_Base_Arrow_Txt", "Twitch_Base_Z_Muzzle_Flash", "Twitch_Base_AA_Posion_Smoke_Cloud",
                          "Twitch_Base_P_Impact", "Twitch_Base_P_Poison_Smoke", "Twitch_Base_P_Rat_Icon"]),
    ("W", ["Twitch_Base_W_Bottle_Txt", "Twitch_Base_W_Acidball_Orb_Color", "Twitch_Base_W_Splash",
           "Twitch_Base_W_Splat_anim", "Twitch_Base_W_Persist_Smoke_Color", "Twitch_Base_W_Green_Ring"]),
    ("Q", ["Twitch_Base_Q_Bamf_Smoke_4x4", "Twitch_Base_Q_Bamf_Swirl", "Twitch_Base_Q_Cas_Dots",
           "Twitch_Base_Q_Camouflage_Ring_RGB", "Twitch_Base_Q_Smoke", "Twitch_Base_Z_Green_Glow"]),
    ("E", ["Twitch_Base_E_Tar_Spikes", "Twitch_Base_E_Tar_Flash", "Twitch_Base_E_Posion_Smoke_Cloud",
           "Twitch_Base_W_Nova", "common_aciddrops32", "twitch_venom_bomb_splash"]),
    ("R", ["Twitch_Base_R_EnergyWave", "Twitch_Base_R_Spotlight", "Twitch_Base_R_Wispy_Ribbon",
           "common_AirSpiritStreak", "Twitch_Base_Z_Poison_Smoke", "common_ring_highres"]),
]
# where the pictures start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point, dy from the soles]);
# the attack's crossbow tip from Codex's manifest (attack frame 3: bow_tip (78, 70), pivot (59, 70) -> +19, 11 up), W's
# throwing hand from fix_twitch_strips.hand_point (69, 81 on the design canvas: +5, 18 up)
SHOTS = [("attack", 3, "a_bolt / a_flash: 弩尖（箭从这里飞出）", [(19, -11)]), ("skill2", 3, "w_cask: 扔出（手）", [(5, -18)]),
         ("ult", 2, "r_cast / r_on: 站位点", "feet"), ("idle", 1, "q_cast / q_out / q_as / e_cast / q_reset: 站位点", "feet")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Twitch_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = design_1x()
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    img = Image.new("RGBA", (max(W * Z, 420), (pad + max(fig.shape[0], kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fig.shape[0], kn.shape[0])
    img.alpha_composite(Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST),
                        (pad * Z, (base - fig.shape[0]) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fig.shape[1]) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.shape[1] + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"图奇 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (league/champions/league_twitch, the imported sheet), each picture's starting
    point as a cyan cross (the standing point is the frame's pivot: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_twitch"))
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    px = sp.w // 2
    for tag, k, what, marks in SHOTS:
        f = np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA"))
        ys, xs = np.nonzero(f[..., 3] > 0)
        soles = int(ys.max())
        pts = [(px, soles + 1)] if marks == "feet" else [(px + dx, soles + 1 + dy) for dx, dy in marks]
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 260), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        for mx, my in pts:
            cx, cy = int((mx - x0) * Z), int((my - y0) * Z) + 24
            d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
            d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    W = sum(t.width + 10 for t in tiles)
    H = max(t.height for t in tiles)
    sheet = Image.new("RGB", (W, H), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 瘟疫之源 图奇：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/twitch_design.png`，8 倍，{h} 行、{w} 格宽）。")
    a(f"> - 大小对照 `design/twitch_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。图奇 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/twitch_shots.png`：定稿动作（4 倍），青色十字是特效的起点（弩尖、扔桶的手、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里图奇自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版皮肤：**毒液是亮绿色（被动、W、E、R）；隐身的烟是紫黑色；弩和火星是黄铜色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的烟雾、光环、火光只画外圈，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的弩箭、大招的穿透箭、毒桶画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "画在他身上、晚于技能开始播放的（`q_out`、`q_reset`、`e_cast`、`r_cast`）和挂在他身上、脚下循环的（`q_as`、`r_on`、`w_slow`）要**严格左右对称**（逐格对称）；"
      "地上的毒池 `w_pool` 上下左右都对称。只有 `a_flash`（弩口火光）是朝右的：它会烘进普攻的动作帧里，跟着人物一起翻转。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `twitch_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`twitch_fx_done.zip`）放在 outputs 里，或放在 `outputs/twitch-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「死亡毒液」 | 弩箭攻击，每一下给目标挂一层毒（每秒真实伤害） | `a_bolt` · `a_flash` · `a_hit` |")
    a("| 技能 1 = Q「埋伏」 | 隐身接近，出手现形后加攻速；击杀英雄刷新 | `q_cast` · `q_out` · `q_as` · `q_reset` |")
    a("| 技能 2 = W「剧毒之桶」→ E「毒性爆发」 | 扔毒桶（减速、上毒、留下毒池），再引爆所有中毒敌人身上的毒 | `w_cask` · `w_hit` · `w_pool` · `w_slow` · `e_cast` · `v_pop` |")
    a("| 大招 = R「火力全开」 | 6 秒内射程变长、弩箭变成直线穿透 | `r_cast` · `r_on` · `r_bolt` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、毒液、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。只有弩箭和毒桶（实物）有 1 格深色描边（`#0A0806`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("毒液绿（被动、W、E、R）", VENOM), ("隐身的紫黑烟（Q）", SMOKE), ("黄铜火星（弩口、刷新）", SPARK),
                        ("弩箭和毒桶（实物）", BRASS)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，"
      "毒桶半径 28000，大招箭宽 6000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout, obj) in enumerate(FX, 1):
        a(f"### {k}. `twitch_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a((LEAD_OBJ if obj else LEAD).format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `twitch_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `a_bolt` 从弩尖出（出手帧弩尖在站位点前面约 19 格、脚底上面 11 格，和站位点同高：`y_offset` 0），画面开头补几帧空的，让箭离开弩再出现；`r_bolt` 同一个出手点。")
    a("- `a_flash` 烘进普攻第 3 帧（`twitch_bake.json`），不做成特效（红色方翻转）。`q_cast` 在动作第一 tick 播放、跟随；"
      "`q_out`、`q_reset`、`e_cast`、`r_cast` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`w_pool` 是地上的投射物画面。")
    a("- 用 `pixel_1x/` 切格（import_twitch 的做法），断言对称；清掉 Codex 给光描的最深色边（尖刺、毒桶保留描边）；核对交回的张数和这份清单；"
      "量每张的平均亮度和最亮的一成，和包里别的英雄比。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="twitch_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack folder)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out or os.path.join(TMP, "fx"), a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: extract Twitch's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "twitch_design.png"))
    shape = size_sheet(os.path.join(out, "design", "twitch_size.png"))
    shots_sheet(os.path.join(out, "design", "twitch_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"twitch_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
    if not a.no_zip:
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
