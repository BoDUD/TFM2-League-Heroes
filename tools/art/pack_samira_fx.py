#!/usr/bin/env python3
"""Build samira_fx_pack.zip: step 3 of Samira's sprite - Codex draws her effects (after tools/art/pack_xerath_fx.py).

    python tools/art/pack_samira_fx.py [--no-zip] [--out DIR] [--only a_hit,q_bullet --name samira_fx_redo_pack]

The pack (%TEMP%/sm_work/fx/samira_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/samira/PROMPTS_FX.md), design/samira_design.png (8x), design/samira_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside her), design/samira_shots.png (the finished
action frames at 4x - tools/art/rig_samira.py - with the point each picture drawn on her starts from) and
refs/lol_fx_ref.png (League's own particle textures for Samira, grouped by the effect of ours they inform; Riot's art,
local only: it reads %TEMP%/sm_work/fxref, extracted from Samira.wad.client by the session's fx_ref_sm.py).
The effects are the views the kit binds (tools/kit/build_samira.py: view_projectiles a_bullet, q_bullet, r_bullet;
view_effects a_hit, a_slash_hit, j_up, q_hit, q_slash_hit, q_slash, e_dash, e_hit, e_reset, w_hit, r_hit, g_up, g_s;
view_buffs g1..g6 (one sheet of the Style letters), w_spin, r_on) and the pictures drawn into her own frames at import
(a_flash, q_flash, r_flash at the muzzles, a_slash along the sword's chop: the client mirrors her frames with her facing
and never an effect picture, so a muzzle flash that points must ride in the frames - league_jhin's). League's colours:
white-hot gold and orange gunfire, the greatsword's fire a crimson red-orange, crimson rose petals in R, the Style
letters gold to red, the desert sand of E's dash. Light, fire and sparks get no outline (the bright-effects lesson);
only the Style letters have a dark outline, to read over the battle.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sm_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "samira", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "samira_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GUN = "#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208"      # gunfire: muzzle flashes, bullets, gun hits
BLADE = "#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18"    # the greatsword's fire: slashes, the whirl, sword hits
ROSE = "#FFB4C4, #F25A7E, #C8264A, #7E1230"                       # R's rose petals
GOLD = "#FFFFFF, #FFF0A0, #FFD040, #E89A10, #A85A08"              # the Style letters and their flashes
SAND = "#F2DDB4, #D2B07C, #A8844E, #6E5232"                       # E's dust
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades "
        "and a white-hot core - it must read on a dark battlefield), colours only from {ramps}.")
LEAD_LETTERS = ("Pixel art game UI sprite sheet for a small tactics game: chunky square pixels, hard edges, no "
                "anti-aliasing, bold blocky letters with a 1-square dark outline #1A0A0E so they read over the battle, "
                "colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FIG = "do NOT draw the figure; leave its place empty"
GF = f"a gunfire ramp ({GUN})"
BF = f"a crimson blade-fire ramp ({BLADE})"
RP = f"a rose-petal ramp ({ROSE})"
GL = f"a gold ramp ({GOLD})"
SD = f"a desert-sand ramp ({SAND})"


def row(n, cw, ch):
    """One row of n cells of cw x ch squares at 16 px a square."""
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack: the gun, the sword, the juggle
    ("a_bullet", "普攻子弹（飞行中，循环），4 帧", "view_projectiles `league_samira_a_bullet`（朝飞行方向转，画成朝右飞；上下对称）",
     "12 × 4",
     "莎弥拉普攻打出的子弹：一颗短短的白金色发光弹头，后面一小段橙色的曳光尾巴（参考 BA_MuzzleGradients、Q_Bullet_Glow、Q_Trail）。朝右飞（尾巴在左）。"
     "**上下对称**（往左飞时会上下翻）。4 帧无缝循环（弹头一闪一闪、尾巴抖动）。约 12 格长、4 格高，弹头在格子右边四分之三处。",
     GF,
     "a BULLET TRACER in flight to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a white-hot slug 3 "
     "squares long and 2 tall at the front, a tapering gold-to-orange tracer trail 9 squares long to its LEFT; the slug "
     "flickers and the trail shimmers each frame.",
     row(4, 16, 8) + "; the slug's front 3/4 of the way across and vertically centered in every cell."),
    ("a_flash", "普攻开火：枪口火光（画进她自己的开火帧），3 帧",
     "画进 `samira_attack` 第 4 帧起（枪口，`design/samira_shots.png` attack 4 的十字；导入时烘进精灵帧）", "14 × 10",
     "左轮开火的那一下：枪口前一团白金色的星形火光，往右喷出一小束橙色的火舌，几道尖细的光芒（参考 BA_MuzzleFlash_Backdrop、BA_Sharp_Ray、"
     "BA_MuzzleGradients）。**朝右**（枪口在格子左边中间）。3 帧：1 最亮最大，2 变小、火舌往右，3 几点火星。约 14 格宽、10 格高。",
     GF,
     "a GUN MUZZLE FLASH pointing RIGHT, 3 frames: the muzzle point is 2 squares from the LEFT edge, vertically centered; 1 "
     "a white-hot star flash 6 squares across at the muzzle with 4 sharp rays and a gold-orange flame cone shooting 10 "
     "squares to the RIGHT; 2 the flash smaller, the cone thinner; 3 a few fading sparks.",
     row(3, 16, 12) + "; the muzzle point 2 squares from the left edge, vertically centered, in every cell."),
    ("a_hit", "普攻子弹打中（目标身上），4 帧", "view_effects `league_samira_a_hit`（跟随，画在人物上面）", "12",
     "子弹打中：一个白金色的四角星形闪光，几点橙色火星飞出去（参考 BA_Tar_Flare、Q_Impact_Flare、Q_Embers）。约 12 格，居中画。",
     GF,
     "a BULLET HIT, 4 frames: 1 a white-hot four-pointed star flash 8 squares across at the center; 2 the star smaller, "
     "5 gold-orange sparks flying out; 3 sparks further out; 4 a few fading embers.",
     row(4, 14, 14) + "; centered in every cell."),
    ("a_slash", "普攻挥剑：剑砍下去的火焰弧光（画进她自己的挥砍帧），3 帧",
     "画进 `samira_attack_m` 第 4 帧起（`design/samira_shots.png` attack_m 4 的十字是弧的中心；导入时烘进精灵帧）", "28 × 30",
     "近身普攻那一剑：大剑从右上往右下劈下去，剑身后面拖一道新月形的红橙色火焰弧光，边缘白亮（参考 BA_Outer_Flare、BA_Outer_Flare_Erode、"
     "R_Swipe_Edge、Q_Swipe_Erode）。**朝右**：弧从格子右上方弯到右下方，凸的一边朝右。3 帧：1 整道弧最亮，2 弧变细、尾端碎成火星，3 几点火星。"
     "约 28 格宽、30 格高，弧的圆心在格子左边三分之一处的中间。",
     BF,
     "a SWORD SLASH ARC facing RIGHT, 3 frames: a crescent of crimson blade-fire 4 squares thick at its middle, bulging "
     "to the RIGHT, sweeping from the top right of the cell down to the bottom right, a white-hot leading edge on its "
     "outer side, the inner edge fading to red; 1 the whole arc at its brightest; 2 the arc thinner, its tail breaking "
     "into sparks; 3 a few fading sparks along the path.",
     row(3, 30, 32) + "; the arc's center of curvature 1/3 of the way across and vertically centered in every cell."),
    ("a_slash_hit", "普攻挥剑打中（目标身上），4 帧", "view_effects `league_samira_a_slash_hit`（跟随，画在人物上面）", "16",
     "大剑砍中：一道斜着的红色刀痕闪过，白色的芯，几点火星（参考 Q_Impact_Flare、Q_Melee_Flash）。约 16 格，居中画。",
     BF,
     "a SWORD HIT, 4 frames: 1 a diagonal crimson slash streak 14 squares long through the center (from the top right "
     "down to the bottom left), a white-hot core; 2 the streak thinner, a flash 6 squares across at its middle, sparks; 3 "
     "sparks scattering; 4 fading embers.",
     row(4, 18, 18) + "; centered in every cell."),
    ("j_up", "被动：挑飞（被控住的敌方英雄身上），4 帧", "view_effects `league_samira_j_up`（跟随，画在人物上面）", "20 × 28",
     "被动的连击：莎弥拉冲到被控住的敌人身边，从下往上一剑把他挑起来：一道从地面往上撩的红橙色弧光，脚下一小团沙尘（参考 Q_Air_swoosh、"
     "BA_Outer_Flare、E_Dash_DirtTrail）。中间是人，不要画人。4 帧：1 脚下沙尘、弧光从脚下起，2 弧光往上最亮，3 弧光到头顶、火星，4 淡去。"
     "约 20 格宽、28 格高，敌人的站位点在格子底部往上 4 格的中间。",
     f"{BF} and {SD}",
     f"an UPWARD SWORD SWOOSH lifting a figure ({FIG}), 4 frames: 1 a puff of sand dust 12 squares wide at the "
     "standing point, a crimson blade-fire arc starting at the ground; 2 the arc sweeping UP past the figure's place, "
     "at its brightest, 4 squares thick, white-hot edge; 3 the arc's tip above the figure's head, sparks; 4 fading "
     "sparks and dust.",
     row(4, 22, 30) + "; the standing point 4 squares above the bottom, horizontally centered, in every cell."),
    # ---- Q: Flair
    ("q_bullet", "Q 交火：远程的子弹（飞行中，循环），4 帧", "view_projectiles `league_samira_q_bullet`（朝飞行方向转，画成朝右飞；上下对称）",
     "22 × 7",
     "Q 用枪时射出的子弹：比普攻的大一号，白热的弹头外面一圈金色的光，后面一道长长的橙红色火焰尾巴，两边几道细细的气流线（参考 Q_Bullet_Glow、"
     "Q_Trail、Q_SideTrail、Q_Flare_Ray）。朝右飞。**上下对称**。4 帧无缝循环。约 22 格长、7 格高。",
     GF,
     "a BIG FLAMING BULLET in flight to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a white-hot slug 4 "
     "squares long and 3 tall with a gold glow round it at the front, a tapering orange-to-red flame trail 16 squares long "
     "to its LEFT, two thin pale streaks along its sides; the flame flickers each frame.",
     row(4, 24, 10) + "; the slug's front 7/8 of the way across and vertically centered in every cell."),
    ("q_flash", "Q 开枪：更大的枪口火光（画进她自己的开火帧），3 帧",
     "画进 `samira_skill` 第 3 帧起（枪口，`design/samira_shots.png` skill 3 的十字；导入时烘进精灵帧）", "20 × 14",
     "Q 用枪的那一下：比普攻大一圈的枪口火光，一团白金色的爆闪，往右喷出一大束橙红色火舌和尖锐光芒，几点火星（参考 Q_Muzzle_Flash、"
     "Q_Flare_Ray、BA_Sharp_Ray）。**朝右**（枪口在格子左边中间）。3 帧：1 最大最亮，2 火舌往右变长变细，3 火星。约 20 格宽、14 格高。",
     GF,
     "a BIG MUZZLE BLAST pointing RIGHT, 3 frames: the muzzle point 2 squares from the LEFT edge, vertically centered; 1 a "
     "white-hot burst 8 squares across at the muzzle with 6 sharp rays and a big gold-orange flame cone shooting 14 "
     "squares to the RIGHT; 2 the cone longer and thinner, red at its edges; 3 fading sparks.",
     row(3, 22, 16) + "; the muzzle point 2 squares from the left edge, vertically centered, in every cell."),
    ("q_hit", "Q 子弹打中（目标身上），4 帧", "view_effects `league_samira_q_hit`（跟随，画在人物上面）", "16",
     "Q 的子弹打中：一下大一点的白金色爆闪，四片尖锐的光刺往外，几点橙色火星（参考 Q_Impact_Flare、Q_Embers、Q_Throw_Sparks）。约 16 格，居中画。",
     GF,
     "a BIG BULLET IMPACT, 4 frames: 1 a white-hot flash 10 squares across with 4 sharp shard-like rays; 2 a gold ring 14 "
     "squares across spreading, 6 orange sparks; 3 sparks further out; 4 fading embers.",
     row(4, 18, 18) + "; centered in every cell."),
    ("q_slash", "Q 交火：近身的半月剑斩（施法者身上，大），4 帧",
     "view_effects `league_samira_q_slash`（BIG，施法者身上，跟随；格子里的站位点放到她脚下，导入时前面补空帧对上挥剑帧）", "44 × 44",
     "Q 在近身时用剑：一记横扫面前的半月斩，一大道新月形的红橙色火焰弧光从她头顶上方扫到身前的地面，凸的一边朝右，边缘白亮，扫过的地方几片火星"
     "（参考 Q_Melee_Border、Q_Melee_Border_Burn_In、Q_Melee_Flash、Q_Swipe_Filler、Q_Swipe_Erode）。中间是人，不要画人。**朝右**。4 帧："
     "1 弧光从头顶上方起、最亮，2 整道弧扫完（最大，约 40 格高），3 弧光变细碎成火星，4 淡去。约 44 格见方，站位点在格子左边 12 格、底部往上 6 格。",
     BF,
     f"a HUGE HALF-MOON SWORD SWEEP in front of a figure ({FIG}), facing RIGHT, 4 frames: a crescent of crimson "
     "blade-fire bulging to the RIGHT, its inner edge 6 squares in front of the figure's place; 1 the arc starting above "
     "the figure's head, white-hot; 2 the full arc swept from above the head down to the ground in front, 40 squares "
     "tall and 6 thick at its middle, white-hot outer edge, red inner edge, sparks along it; 3 the arc thinner, breaking "
     "into sparks; 4 fading sparks.",
     row(4, 44, 44) + "; the standing point 12 squares from the left edge and 6 squares above the bottom in every cell."),
    ("q_slash_hit", "Q 剑斩打中（目标身上），4 帧", "view_effects `league_samira_q_slash_hit`（跟随，画在人物上面）", "18",
     "半月斩砍中：一个红色的刀痕交叉，白色的芯，一圈火星（参考 Q_Melee_Flash、Q_Impact_Flare）。约 18 格，居中画。",
     BF,
     "a HEAVY SWORD HIT, 4 frames: 1 two crossing crimson slash streaks 16 squares long (an X) with a white-hot center 6 "
     "squares across; 2 the streaks thinner, a ring of 8 sparks; 3 sparks further out; 4 fading embers.",
     row(4, 20, 20) + "; centered in every cell."),
    # ---- skill2: E Wild Rush -> W Blade Whirl
    ("e_dash", "E 狂飙：冲刺的拖尾（施法者身上，大），4 帧",
     "view_effects `league_samira_e_dash`（BIG，施法者身上，跟随；格子里的站位点放到她脚下）", "48 × 24",
     "E 冲刺：她身后拖出几道红橙色的速度线，脚下扬起一路黄沙，几颗弹壳和小石子飞起来（参考 Samira_E_Dash、E_Dash_DirtTrail、E_Rocks、E_Shells）。"
     "中间是人，不要画人。**朝右冲**：拖尾和沙尘都在站位点的**左边**（身后）。4 帧：1 速度线和沙尘从脚下起，2 拖尾最长（往左约 36 格），3 变淡、沙尘散开，"
     "4 几点沙。约 48 格宽、24 格高，站位点在格子右边往左 8 格、底部往上 4 格。",
     f"{BF} and {SD}",
     f"a DASH TRAIL behind a figure rushing to the RIGHT ({FIG}), 4 frames: 1 three crimson-orange speed streaks and a "
     "kick of sand dust starting at the standing point; 2 the streaks at their longest, trailing 36 squares to the LEFT "
     "of the standing point at waist and knee height, the dust cloud along the ground behind, 2-3 small brass shell "
     "casings and pebbles flying; 3 the streaks fading, the dust spreading; 4 a few drifting dust specks.",
     row(4, 48, 24) + "; the standing point 8 squares from the right edge and 4 squares above the bottom in every cell."),
    ("e_hit", "E 冲刺砍中（目标身上），4 帧", "view_effects `league_samira_e_hit`（跟随，画在人物上面）", "16",
     "冲过去砍中：一道横着的红色刀痕，一小团沙尘（参考 Q_Melee_Flash、E_Dash_DirtTrail）。约 16 格，居中画。",
     f"{BF} and {SD}",
     "a DASH SLASH HIT, 4 frames: 1 a horizontal crimson slash streak 14 squares long through the center with a white-hot "
     "core; 2 the streak thinner, a puff of sand dust; 3 sparks and dust; 4 fading.",
     row(4, 18, 18) + "; centered in every cell."),
    ("e_reset", "E 刷新：击杀后的金光（施法者身上），4 帧", "view_effects `league_samira_e_reset`（施法者身上，不跟随；左右对称）", "22",
     "E 的击杀刷新：她身上一下金色的光环往外扩，几颗金色的星光往上飘（参考 Taunt_Star、Ring_Glow）。**左右对称**。约 22 格，居中画（她的腰部）。",
     GL,
     "a RESET FLASH round a figure, SYMMETRIC LEFT AND RIGHT, 4 frames: 1 a gold ring 10 squares across with a white flash; "
     "2 the ring spreading to 18 squares, 4 four-pointed gold stars rising; 3 the ring fading, stars higher; 4 a few "
     "fading stars.",
     row(4, 24, 24) + "; centered in every cell."),
    ("w_spin", "W 锋旋：绕身旋转的剑刃火环（她身上，循环，大），4 帧",
     "view_buffs `league_samira_w_spin`（BIG，循环，画在人物上面；左右对称）", "64 × 40",
     "W 锋旋：她原地转圈挥剑，身边一圈扁扁的红橙色剑刃火环在转，环上几道白亮的刀光，几点火星甩出去（参考 W_Border、W_Block_Flash、"
     "R_Swipe_Edge）。中间是人，不要画人：**只画环，人的位置留空**（环从人的前面和后面绕过，前面那一段可以盖住一点腰）。**左右对称**（人朝左朝右都用这一张）。"
     "4 帧无缝循环（刀光每帧往前转四分之一圈）。环约 60 格宽、22 格高，环的中心在站位点上面 14 格；格子 64 格宽、40 格高，站位点在底部往上 6 格的中间。",
     BF,
     f"a SPINNING BLADE RING round a figure ({FIG}; draw only the ring), SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless "
     "loop: a flattened ring of crimson blade-fire 60 squares wide and 22 tall (seen from above at an angle), its center 14 "
     "squares above the standing point, 2-3 squares thick, with 3 bright white-hot blade glints on it that move a quarter "
     "of the way round each frame, a few sparks flung outward; the figure's place inside the ring stays empty.",
     row(4, 64, 40) + "; the standing point 6 squares above the bottom, horizontally centered, in every cell."),
    ("w_hit", "W 锋旋砍中（目标身上），4 帧", "view_effects `league_samira_w_hit`（跟随，画在人物上面）", "16",
     "被锋旋砍中：一道弯弯的红色刀痕扫过，白色的芯，几点火星（参考 R_Swipe_Edge、Q_Melee_Flash）。约 16 格，居中画。",
     BF,
     "a WHIRL SLASH HIT, 4 frames: 1 a curved crimson slash streak 14 squares long sweeping across the center, white-hot "
     "core; 2 the streak thinner, 5 sparks; 3 sparks further out; 4 fading embers.",
     row(4, 18, 18) + "; centered in every cell."),
    # ---- R: Inferno Trigger
    ("r_on", "R 炼狱扳机：开大时身边的枪火和玫瑰花瓣（她身上，循环，大），4 帧",
     "view_buffs `league_samira_r_on`（BIG，循环，画在人物上面；左右对称）", "64 × 56",
     "R 炼狱扳机：她原地转圈双枪乱射，身边一圈一闪一闪的金橙色枪火和曳光、几道红色的气旋，深红色的玫瑰花瓣往外飘（参考 R_Swipe、R_Swipe_Edge、"
     "R_Electric_Energy、R_Energy_Ray、R_Rose_Petals）。中间是人，不要画人：**只画周围，人的位置留空**。**左右对称**。4 帧无缝循环（枪火每帧换位置、"
     "花瓣往外飘）。约 64 格宽、56 格高，站位点在格子底部往上 6 格的中间。",
     f"{GF}, {BF} and {RP}",
     f"a GUNFIRE STORM round a spinning figure ({FIG}; draw only round it), SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless "
     "loop: a flattened swirl of crimson fire 56 squares wide round the figure's waist, 6-8 short white-gold tracer "
     "streaks and muzzle sparks flashing outward in all directions at shoulder height (in new places each frame), 8-10 "
     "crimson rose petals (each 2-3 squares) drifting outward; the figure's place stays empty.",
     row(4, 64, 56) + "; the standing point 6 squares above the bottom, horizontally centered, in every cell."),
    ("r_flash", "R 开火：两把枪口的小火光（画进她自己的开大帧），2 帧",
     "画进 `samira_ult` 第 2–9 帧（两把枪口，`design/samira_shots.png` ult 2 的两个十字；朝左那把用镜像；导入时烘进精灵帧）", "10 × 8",
     "开大时每一发：枪口一小团白金色的火光，往右喷一点火舌（参考 BA_MuzzleFlash_Backdrop、BA_Sharp_Ray）。**朝右**（枪口在格子左边中间）。"
     "2 帧：1 亮，2 小。约 10 格宽、8 格高。",
     GF,
     "a SMALL MUZZLE FLASH pointing RIGHT, 2 frames: the muzzle point 2 squares from the LEFT edge, vertically centered; 1 a "
     "white-hot flash 4 squares across with 3 short rays and a gold flame 6 squares to the RIGHT; 2 smaller, sparks.",
     row(2, 12, 10) + "; the muzzle point 2 squares from the left edge, vertically centered, in every cell."),
    ("r_bullet", "R 的子弹（飞行中，循环），3 帧", "view_projectiles `league_samira_r_bullet`（朝飞行方向转，画成朝右飞；上下对称）",
     "16 × 5",
     "炼狱扳机射向周围敌人的子弹：一颗红橙色的曳光弹，后面一段淡淡的烟尾（参考 R_Tracer、R_Bullet、R_Smoke_Trail）。朝右飞。**上下对称**。"
     "3 帧无缝循环。约 16 格长、5 格高。",
     GF,
     "a RED TRACER ROUND in flight to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a white-hot slug 3 "
     "squares long at the front, an orange-red tracer 7 squares long behind it, then a faint grey-orange smoke wisp 5 "
     "squares long to its LEFT (use the darker gunfire shades for the smoke).",
     row(3, 18, 8) + "; the slug's front 7/8 of the way across and vertically centered in every cell."),
    ("r_hit", "R 子弹打中（敌人身上），4 帧", "view_effects `league_samira_r_hit`（跟随，画在人物上面）", "14",
     "被炼狱扳机打中：一小团橙红色的火光，一片深红色的玫瑰花瓣飘开（参考 BA_Tar_Flare、R_Rose_Petals）。约 14 格，居中画。",
     f"{GF} and {RP}",
     "a FIERY HIT, 4 frames: 1 a white-gold flash 8 squares across; 2 a small orange-red burst 12 squares across, one "
     "crimson rose petal (3 squares) flying off; 3 embers and the petal drifting; 4 fading.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- the passive: Style
    ("g_letters", "被动「悍勇本色」：头顶的连招评分字母 E D C B A S（她身上，常驻），6 格（每格一个字母）",
     "view_buffs `league_samira_g1`…`g6`（每格一个字母：g1 = E … g6 = S；画在头顶，不旋转）", "10 × 10（S 12 × 12）",
     "被动的连招评分：每打出一种不同的招式升一级，从 E 升到 S，字母显示在她头顶。6 个格子依次是 **E、D、C、B、A、S** 六个粗体像素字母，"
     "像格斗游戏的评分：E、D、C 偏金黄，B、A 金橙，**S 最大最亮**，带一点火焰和红色的边（参考 Passive_timer_ring、P_Screen_Flames）。"
     "这里字母要有 1 格深色描边，才能在战斗里看清；字母**不要镜像**，正常的方向。每格一个字母，居中。约 10 格高（S 约 12 格）。",
     f"{GL} and {BF}",
     "SIX STYLE GRADE LETTERS, one per cell, in this order: E, D, C, B, A, S - bold blocky pixel letters (upright, normal "
     "reading direction, NOT mirrored) like a fighting game's style rank: E, D and C 9 squares tall in gold, B and A 10 "
     "squares tall in gold-orange with a white highlight on their top edges, S 12 squares tall, the brightest - gold "
     "with a white-hot top edge, a crimson underside and 3-4 small flame tongues licking up from it.",
     row(6, 16, 16) + "; each letter centered in its cell."),
    ("g_up", "被动升级：头顶的金色闪光（她身上），3 帧", "view_effects `league_samira_g_up`（施法者身上，不跟随，头顶；左右对称）", "16",
     "评分升一级的那一下：头顶一下金色的星形闪光，几颗小星星往外蹦（参考 Taunt_Star、Ring_Glow）。**左右对称**。约 16 格，居中画。",
     GL,
     "a GRADE-UP SPARKLE, SYMMETRIC LEFT AND RIGHT, 3 frames: 1 a white-gold four-pointed star flash 10 squares across; 2 "
     "a thin gold ring 14 squares across, 4 tiny stars popping out; 3 fading stars.",
     row(3, 18, 18) + "; centered in every cell."),
    ("g_s", "被动到 S：头顶的火焰金光（她身上），4 帧", "view_effects `league_samira_g_s`（施法者身上，不跟随，头顶；左右对称）", "28",
     "评分到 S 的那一下：头顶一下大团金红色的爆闪，一圈火焰光环往外扩，火星往上窜（参考 Passive_timer_ring、P_Screen_Flames、Ring_Glow）。"
     "**左右对称**。约 28 格，居中画。",
     f"{GL} and {BF}",
     "an S-RANK BURST, SYMMETRIC LEFT AND RIGHT, 4 frames: 1 a white-gold flash 12 squares across; 2 a ring of crimson "
     "and gold flame 22 squares across spreading, 6 sparks shooting up; 3 the ring at 28 squares, thinner, sparks higher; "
     "4 fading embers.",
     row(4, 30, 30) + "; centered in every cell."),
]

GROUPS = [
    ("gun", ["Samira_Base_BA_MuzzleFlash_Backdrop", "Samira_Base_BA_MuzzleGradients", "Samira_Base_BA_Sharp_Ray",
             "Samira_BA_Tar_Flare", "Samira_Base_Q_Muzzle_Flash", "Samira_Base_Q_Flare_Ray"]),
    ("bullet", ["Samira_Base_Q_Bullet_Glow", "Samira_Base_Q_Trail", "Samira_Base_Q_SideTrail", "Samira_Base_R_Tracer",
                "Samira_Base_R_Bullet", "Samira_Base_R_Smoke_Trail"]),
    ("hit", ["Samira_Base_Q_Impact_Flare", "Samira_Base_Q_Embers", "Samira_Base_Q_Throw_Sparks", "Samira_Base_Q_Melee_Flash",
             "Samira_Q_Hit_Lens_Flare", "Samira_Base_Taunt_Star"]),
    ("sword", ["Samira_Base_BA_Outer_Flare", "Samira_Base_BA_Outer_Flare_Erode", "Samira_Base_Q_Melee_Border",
               "Samira_Base_Q_Swipe_Filler", "Samira_Base_Q_Air_swoosh", "Samira_Base_R_Swipe_Edge"]),
    ("E / W", ["Samira_E_Dash", "Samira_Base_E_Dash_DirtTrail", "Samira_Base_E_Rocks", "Samira_Base_E_Shells",
               "Samira_Base_W_Border", "Samira_Base_W_Block_Flash"]),
    ("R / style", ["Samira_Base_R_Swipe", "Samira_Base_R_Electric_Energy", "Samira_Base_R_Energy_Ray",
                   "Samira_Base_R_Rose_Petals", "Samira_Base_Passive_timer_ring", "Samira_Base_P_Screen_Flames"]),
]
# where the pictures drawn on her start: (tag, frame, what, marks: "feet" = the standing point under her soles - the
# prompts' "standing point", 11 rows under the engine's pivot - or [(dx, dy) from the pivot])
SHOTS = [("attack", 4, "a_flash: 枪口", [(23, -11.5)]), ("skill", 3, "q_flash: 枪口", [(23, -12.5)]),
         ("attack_m", 4, "a_slash: 弧的中心", [(10, -8)]), ("skill_m", 4, "q_slash: 站位点", "feet"),
         ("skill2", 1, "e_dash: 站位点（拖尾往左）", "feet"), ("skill2", 4, "w_spin: 环的中心（腰）", [(0, -3)]),
         ("ult", 2, "r_flash: 两把枪口", [(24, -11.5), (-26.5, -12.5)]), ("ult", 2, "r_on: 站位点", "feet"),
         ("idle", 1, "g 字母 / g_up / g_s: 头顶", [(0, -34)])]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Samira_Base_", "").replace("Samira_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside her."""
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
    d.text((8, 36), f"莎弥拉 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (rig_samira.py), each picture's starting point as a cyan cross."""
    import rig_samira as RS
    P = RS.Parts()
    built = {}
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    px, py = RS.PIVOT
    for tag, k, what, marks in SHOTS:
        if tag not in built:
            built[tag] = RS.frames(P, tag)
        f = built[tag][k - 1]
        pts = [(px, RS.SOLES + 1)] if marks == "feet" else [(px + dx, py + dy) for dx, dy in marks]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 230), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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
    a("# 沙漠玫瑰 莎弥拉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/samira_design.png`，8 倍，{h} 行）。")
    a(f"> - 大小对照 `design/samira_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。莎弥拉 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/samira_shots.png`：定稿动作（4 倍），青色十字是特效的起点（枪口、剑弧中心、脚下、头顶），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里莎弥拉自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**枪火和子弹是白热的金黄、橙色；大剑的火焰是深红到红橙；R 有深红色的玫瑰花瓣；E 冲刺扬起黄沙；被动评分字母金黄到红**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白热的芯，暗底上一眼能看见。")
    a("> - **围着人的剑环、枪火只画外圈，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要）**：子弹一律画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。枪口火光、挥剑弧光、Q 的半月斩、E 的拖尾都画成**朝右**。挂在她身上循环的画面（`w_spin`、`r_on`）和 `e_reset`、`g_up`、`g_s` 要**左右对称**，人朝左朝右都用同一张。评分字母**不要镜像**。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `samira_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`samira_fx_done.zip`）放在 outputs 里，或放在 `outputs/samira-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「悍勇本色」 | 远处开枪、近身挥剑；被控住的敌方英雄会被她冲过去挑飞；打出不同的招式时评分从 E 升到 S，头顶显示字母 | `a_bullet` · `a_flash` · `a_hit` · `a_slash` · `a_slash_hit` · `j_up` · `g_letters` · `g_up` · `g_s` |")
    a("| 技能 1 = Q「交火」 | 敌人在身边就用剑横扫面前的半月范围，否则开枪打出一发直线子弹（打中第一个敌人） | `q_flash` · `q_bullet` · `q_hit` · `q_slash` · `q_slash_hit` |")
    a("| 技能 2 = E「狂飙」→ W「锋旋」 | 冲向敌方英雄并穿过去，路上砍中的敌人受伤；落地接锋旋：原地转圈挥剑砍两下，转的时候受到的普攻伤害降低；击杀英雄刷新 E | `e_dash` · `e_hit` · `e_reset` · `w_spin` · `w_hit` |")
    a("| 大招 = R「炼狱扳机」 | 评分到 S 才能放：原地转圈双枪乱射 2 秒，周围的敌人每 0.2 秒挨一枪，期间吸血 | `r_on` · `r_flash` · `r_bullet` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、刀光、烟、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。只有被动的评分字母有 1 格深色描边（`#1A0A0E`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("枪火（枪口火光、子弹、枪打中）", GUN), ("剑火（挥剑弧光、半月斩、锋旋、剑打中、挑飞）", BLADE),
                        ("玫瑰花瓣（R）", ROSE), ("金色（评分字母、升级闪光、E 刷新）", GOLD), ("黄沙（E 冲刺、挑飞的尘土）", SAND)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，"
      "Q 半月斩半径 32000、子弹宽 5000，E 冲刺砍中的范围半径 22000，W 锋旋半径 32000，R 的射程半径 55000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `samira_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a((LEAD_LETTERS if name == "g_letters" else LEAD).format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `samira_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 画进精灵帧的（`a_flash`、`q_flash`、`r_flash`、`a_slash`）写进 `assets/source/native/samira_bake.json`，`import_native.py` 烘进 attack / skill / "
      "ult / attack_m 的帧（客户端只镜像英雄自己的帧，不镜像特效图：烬的枪口火光）；`r_flash` 朝左那把用镜像；火光在开火帧之内结束。")
    a("- 子弹从枪口出（开火帧枪口在站位点上面约 11.5 格）：`y_offset` 不超过 8000（子弹会朝目标的站位点斜飞），画面开头补几帧空的，"
      "让子弹飞过枪口（23 格）再出现；开枪的声音和火光、子弹在同一个 `Delayed` 里。")
    a("- `q_slash`、`e_dash` 在动作第一 tick 播放，跟随；`q_slash` 前面补空帧对上 skill_m 第 4 帧（140 ms）。`e_reset`、`g_up`、`g_s` 晚于第一 tick，"
      "`is_follow` 为 false，左右对称；`w_spin`、`r_on` 循环、左右对称；评分字母画在头顶（站位点上面约 34 格），不镜像。")
    a("- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，评分字母保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，"
      "和包里别的英雄比；子弹上下对称；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="samira_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Samira's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "samira_design.png"))
    shape = size_sheet(os.path.join(out, "design", "samira_size.png"))
    shots_sheet(os.path.join(out, "design", "samira_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"samira_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
