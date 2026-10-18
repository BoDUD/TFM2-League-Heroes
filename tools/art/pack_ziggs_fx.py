#!/usr/bin/env python3
"""Build ziggs_fx_pack.zip: step 3 of Ziggs's sprite - Codex draws his effects (pack_jarvaniv_fx.py's way).

    python work/zg/fx_ref_zg.py              # League's particle textures -> %TEMP%/zg_work/fxref (Riot's art, local only)
    python tools/art/pack_ziggs_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name ziggs_fx_redo_pack]

The pack (%TEMP%/zg_work/fx/ziggs_fx_pack, zipped into --out, default dist/ziggs_packs) holds PROMPTS.md (also written to
assets/source/ziggs/PROMPTS_FX.md), design/ziggs_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/ziggs_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/ziggs_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Ziggs grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_ziggs.py): projectiles a_bomb, p_bomb, e_throw, r_bomb (turned
with their flight, so each is symmetric top to bottom: a round bomb with its fuse's sparks trailing behind); view_effects
a_hit, p_hit, q_bomb (the bouncing bomb, stamped on its path at the heights q_air<h> by the import), q_bounce, q_hit,
q_blast, e_land, e_field, e_hit, w_blast, w_hit, r_cast, r_warn, r_boom, r_hit; view_buffs e_slow. League's colours:
red skull bombs, orange-yellow fire, Hextech blue-white flares (Short Fuse, the mines' lights), grey smoke; light gets no
outline, solid things (bombs, mines, the satchel) may. Red side: the client never mirrors an effect picture, so every
non-projectile picture is symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "zg_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "ziggs", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_ziggs")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "ziggs_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410"      # the blasts, the fuses' sparks
HEX = "#FFFFFF, #E4F6FF, #9ADCFF, #46A8F0, #2462C0, #123274"       # Hextech light: Short Fuse, the mines' flares
BOMB = "#FFE8E0, #F2564A, #C8281E, #8A1612, #4E0A0A, #1E0606"      # the bombs' red shells (+ white skulls)
SMOKE = "#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424"     # smoke, dust, the satchel's grey
WARN = "#FFFFFF, #FFD0C8, #FF7A66, #E8302A, #A0141A, #560A10"      # R's target ring and skull mark
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FI = f"a fire and spark ramp ({FIRE})"
HX = f"a Hextech blue-white light ramp ({HEX})"
BO = f"a bomb-shell red ramp ({BOMB}) with pure white for the skull"
SM = f"a smoke and dust grey ramp ({SMOKE})"
WA = f"a warning red ramp ({WARN})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HIM = "a small figure 40 squares wide and 32 tall stands in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

TB = "SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over)"
FLY = "; the bomb flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically."

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack + the passive
    ("a_bomb", "普攻的小炸弹（飞行中），3 帧循环", "view_projectiles `league_ziggs_a_bomb`（随飞行方向转动；上下对称；循环）", "10 × 8",
     "普攻扔出去的小炸弹：一颗红色圆炸弹（约 6 格），身后（左边）拖着引线冒出的黄橙色火星尾巴。**上下对称**（飞向左边时游戏会把图上下翻过来），"
     "所以炸弹上不画骷髅，引线火星画在身后。三帧火星闪动。",
     f"{BO} and {FI}",
     f"a SMALL ROUND BOMB in flight, 3 frames, a seamless loop, {TB}: a round red bomb 6 squares across with a white "
     "highlight on its upper right and the same on its lower right, a short trail of yellow-orange fuse sparks streaming "
     "behind it (to the left, 4 squares long, mirrored top to bottom); the sparks flicker differently in each frame.",
     row(3, 10, 8) + FLY),
    ("p_bomb", "被动「一触即发」的强化炸弹（飞行中），3 帧循环", "view_projectiles `league_ziggs_p_bomb`（随飞行方向转动；上下对称；循环）",
     "14 × 10",
     "被动触发时扔出去的大一号炸弹：红色圆炸弹（约 8 格）外面裹着一圈蓝白色的海克斯电光，身后拖着更长的火星和蓝光尾巴（参考 P_Flare）。"
     "**上下对称**。",
     f"{BO} and {HX} and {FI}",
     f"a BIG HEXTECH BOMB in flight, 3 frames, a seamless loop, {TB}: a round red bomb 8 squares across ringed by a "
     "crackling Hextech blue-white glow 1-2 squares thick, a trail of yellow-orange sparks and blue-white motes 6 squares "
     "long streaming behind it (to the left), mirrored top to bottom; the glow and sparks flicker differently each frame.",
     row(3, 14, 10) + FLY),
    ("a_hit", "普攻命中：小爆炸（目标身上），4 帧", "view_effects `league_ziggs_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "小炸弹炸开：白芯的橙黄色小火球，几粒火星往外飞，一缕灰烟（参考 FireHit、FlashOrange）。**左右对称**。约 12 格。",
     f"{FI} and {SM}",
     f"a SMALL BOMB BLAST on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 an orange-yellow fireball 9 squares with "
     "a white core; 3 the fireball 12 squares breaking up, sparks flying out at mirrored places, a little grey smoke; 4 "
     "grey smoke puffs and two embers.",
     row(4, 12, 12) + CENTER),
    ("p_hit", "被动命中：海克斯爆炸（目标身上），5 帧", "view_effects `league_ziggs_p_hit`（跟随，画在人物上面；左右对称）", "18",
     "强化炸弹炸开：先一道蓝白色的海克斯星芒闪光（参考 P_Flare、Q_FlareOmni），再一团橙黄色的火球，蓝色电光和火星往外飞。**左右对称**。约 18 格。",
     f"{HX} and {FI}",
     f"a HEXTECH BLAST on a unit, 5 frames, {LR}: 1 a blue-white star flare 8 squares (4 thin rays); 2 an orange-yellow "
     "fireball 12 squares with a white core inside a blue-white ring; 3 the fireball 16 squares, blue sparks and orange "
     "embers flying out at mirrored places; 4 the fire breaking into smoke, the ring faint; 5 smoke puffs and blue motes.",
     row(5, 18, 18) + CENTER),
    # ---- Q Bouncing Bomb
    ("q_bomb", "Q 弹跳炸弹：空中的炸弹（会被我按不同高度贴在路径上），3 帧",
     "view_effects `league_ziggs_q_air<高度>`（不跟随；左右对称；由导入脚本按高度抬起）", "12 × 14",
     "Q 扔出去一跳一跳的炸弹本身：一颗**正立**的红色圆炸弹（约 8 格），正面一个**白色骷髅**，顶上一小截深色引线和黄橙色火星。"
     "三帧只是火星闪动（炸弹不转）。**左右对称**。我会把它按弧线的高度一帧帧贴在弹跳路径上，所以这里只画一颗炸弹，炸弹的底边放在格子最底行。",
     f"{BO} and {FI}",
     f"THE BOUNCING BOMB itself, upright, 3 frames, {LR}: a round red bomb 8 squares across, a clear WHITE SKULL on its "
     "front (3 squares wide), a white highlight on its upper left and right, a short dark fuse on top and a yellow-orange "
     "spark 2-3 squares on the fuse; the frames differ only in the spark's flicker (the bomb does not turn). Solid: a "
     "1-square dark outline round the bomb is allowed.",
     row(3, 12, 14) + "; centered across, the bomb's lowest square on the cell's bottom row."),
    ("q_bounce", "Q 弹跳：落地没炸的一下（地上），3 帧", "view_effects `league_ziggs_q_bounce`（不跟随，画在人物上面 z 1；左右对称）",
     "16 × 8",
     "炸弹落地弹起（附近没有敌人，没有爆炸）：地上一小圈尘土往两边溅开，几粒火星。**左右对称**，画在格子底部（地面）。",
     f"{SM} and {FI}",
     f"a BOUNCE on the ground, 3 frames, {LR}: 1 a small dust splash 6 squares wide on the ground line with two sparks; 2 "
     "the dust thrown out to both sides 14 squares wide and 4 tall; 3 faint settling dust.",
     row(3, 16, 8) + "; centered across, the dust's base on the cell's bottom row."),
    ("q_hit", "Q 炸中（目标身上），4 帧", "view_effects `league_ziggs_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "弹跳炸弹炸到敌人：白芯的橙色火光加黑灰色的冲击碎片（参考 Q_BlastShapes、Q_cinder）。**左右对称**。约 14 格。",
     f"{FI} and {SM}",
     f"a BOMB HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 an orange burst 10 squares with a white core "
     "and dark spiky blast shapes round it at mirrored places; 3 the burst 14 squares and thinner, embers flying out; 4 "
     "smoke wisps and embers.",
     row(4, 14, 14) + CENTER),
    ("q_blast", "Q 爆炸：炸弹在地上炸开（地上，不跟随），6 帧",
     "view_effects `league_ziggs_q_blast`（不跟随，画在人物上面 z 2；左右对称；大图表）", "40 × 36",
     "弹跳炸弹在落点炸开（半径约 20 格）：一道白光，地上冒起一团橙黄色的火球，周围一圈尖刺状的爆炸冲击（参考 Q_BlastShapes、Q_explosion_smoke、"
     "Q_ringglow），然后变成一团往上翻的灰烟，地上留下一圈焦黑的痕迹淡去。**左右对称**。",
     f"{FI} and {SM}",
     f"a BOMB EXPLOSION on the ground, 6 frames, {LR}: 1 a white flash 10 squares just above the ground; 2 an orange-yellow "
     "fireball 18 squares wide rising from the ground with a white core, a ring of spiky orange blast shapes along the "
     "ground (an ellipse 30 squares wide and 9 tall); 3 the fireball 26 squares wide and 22 tall, dark debris and embers "
     "flying out and up at mirrored places; 4 the fire turning into rolling grey smoke 30 squares wide, its top 30 "
     "squares above the ground; 5 the smoke thinner and higher, a dark scorch ellipse on the ground; 6 faint smoke and "
     "the scorch fading.",
     row(6, 40, 36) + "; centered across, the ground (the explosion's base) 4 squares above the cell's bottom row."),
    # ---- E Hexplosive Minefield
    ("e_throw", "E 雷区：飞出去的一把地雷（飞行中），2 帧循环", "view_projectiles `league_ziggs_e_throw`（随飞行方向转动；上下对称；循环）",
     "12 × 10",
     "扔出去的一把地雷：三颗小小的圆地雷（每颗 4 格，深灰金属壳、中间一点红灯）挤成一团，身后一点火星。**上下对称**。",
     f"{SM} and {WA} and {FI}",
     f"A HANDFUL OF MINES in flight, 2 frames, a seamless loop, {TB}: three small round mines 4 squares each (dark grey metal "
     "shells, a red light in each middle) clustered together (one in front, two behind mirrored top and bottom), a few "
     "sparks trailing to the left; the red lights blink between the frames.",
     row(2, 12, 10) + FLY),
    ("e_land", "E 地雷落地散开（地上，不跟随），4 帧", "view_effects `league_ziggs_e_land`（不跟随，画在人物下面 z -1；左右对称；大图表）",
     "64 × 26",
     "一把地雷落在地上四散开（雷区是从斜上方看的扁椭圆：宽 60 格、高 22 格）：中间一点白光，尘土往外溅成一圈（参考 BlastRing、E_SoftIndicator），"
     "最后尘土淡去。**左右对称**，中间空着（地雷本身在 e_field 里画）。",
     f"{SM} and {FI}",
     f"MINES LANDING on the ground seen from above at an angle, 4 frames, {LR}: 1 a white flash 8 squares at the "
     "ellipse's middle; 2 a ring of dust thrown out along an ellipse 40 squares wide and 15 tall; 3 the dust ring 60 "
     "squares wide and 22 tall and thinner; 4 faint dust on the ellipse.",
     row(4, 64, 26) + "; centered across, the ellipse's middle 11 squares above the cell's bottom row."),
    ("e_field", "E 雷区：躺在地上的地雷（地上，不跟随，循环），3 帧",
     "view_effects `league_ziggs_e_field`（不跟随，画在人物下面 z -1；左右对称；大图表；每 0.25 秒重贴一次，共 5 秒）", "64 × 26",
     "雷区持续的时候：扁椭圆范围（宽 60 格、高 22 格）里散着**十颗小地雷**（每颗约 4×3 格：深灰金属壳，顶上一个红灯，"
     "近的大一点、远的小一点），地上一圈很淡的红色范围线（参考 E_SoftIndicator、color-bombground）。三帧里地雷的红灯轮流一亮一暗，"
     "第 3 帧接得回第 1 帧。**左右对称**（十颗地雷左右成对摆）。地雷是实心的东西，可以有一圈深色边。",
     f"{SM} and {WA}",
     f"A MINEFIELD lying on the ground seen from above at an angle, 3 frames, a seamless loop, {LR}: a faint thin red ring "
     "on the ground (an ellipse 60 squares wide and 22 tall, 1 square thick, dotted so it reads faint); inside it TEN "
     "SMALL MINES scattered evenly in mirrored pairs (each 4 squares wide and 3 tall: a dark grey metal dome with a "
     "lighter top edge and a red light on top; the near ones (lower) a little bigger, the far ones smaller); the red "
     "lights blink in turn (in each frame a different set is bright red with a white centre, the rest dark red); frame 3 "
     "flows back into frame 1. Solid mines may have a 1-square dark outline.",
     row(3, 64, 26) + "; centered across, the ellipse's middle 11 squares above the cell's bottom row."),
    ("e_hit", "E 地雷炸中（目标身上），4 帧", "view_effects `league_ziggs_e_hit`（跟随，画在人物上面；左右对称）", "16",
     "踩中地雷：脚下一团橙色的小爆炸，夹着蓝白色的海克斯火花（参考 Q_Sparks、FlashOrange）。**左右对称**。约 16 格，偏低（在脚边）。",
     f"{FI} and {HX}",
     f"a MINE BLAST at a unit's feet, 4 frames, {LR}: 1 a white-blue flash 5 squares low in the cell; 2 an orange burst "
     "12 squares with a white core, blue-white sparks at mirrored places; 3 the burst 16 squares wide breaking up, "
     "embers flying up; 4 grey smoke puffs.",
     row(4, 16, 16) + "; centered across, the blast's middle 5 squares above the cell's bottom row."),
    ("e_slow", "E 减速（敌人脚下，1.5 秒，循环），4 帧", "view_buffs `league_ziggs_e_slow`（跟随，画在人物下面；左右对称；循环）",
     "16 × 8",
     "被地雷减速的敌人脚下：一圈焦黑冒烟的地面加几粒火星，往下压的感觉。**左右对称**，只画在脚下。",
     f"{SM} and {FI}",
     f"a SLOW at a unit's feet, 4 frames, a seamless loop, {LR}: a dark smoky ring on the ground (an ellipse 14 squares "
     "wide and 4 tall), 4 orange embers on it at mirrored places and small grey smoke wisps; 1 dim, 2 bright, 3 "
     "brightest, 4 bright.",
     row(4, 16, 8) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
    # ---- W Satchel Charge
    ("w_blast", "W 定点爆破：脚下的炸药包炸开（他脚下，不跟随），6 帧",
     "view_effects `league_ziggs_w_blast`（施放者身上播、不跟随，画在人物上面 z 2；左右对称；大图表）", "52 × 44",
     f"炸药包在他脚下炸开，把敌人和他自己都炸飞（半径约 30 格）：第 1 帧地上一个灰色的炸药包（参考 Ziggs_Satchel 的样子：灰色帆布包、"
     f"一圈金属扣）亮起来；第 2 帧白光一闪；第 3 帧一团大的橙黄色爆炸往四周冲开，两边各有几道白色的气浪弧线往外推（参考 Mult_Windblast、"
     f"Q_Swipe01）；第 4–5 帧碎石和灰烟往外、往上飞（参考 W_rock_debris_blur）；第 6 帧只剩灰烟。**左右对称**，中间身体位置不要整块盖死"
     f"（{HIM}，他在第 3 帧已经被炸飞）。",
     f"{FI} and {SM}",
     f"A SATCHEL CHARGE BLAST at a figure's feet, 6 frames, {LR} ({HIM}): 1 a grey canvas satchel 8 squares wide and 5 "
     "tall with metal clasps on the ground in the middle, glowing orange at its seams; 2 a white flash 14 squares "
     "from the satchel; 3 a big orange-yellow blast 34 squares wide and 22 tall bursting out along the ground with a "
     "white core, white blast-wave arcs pushing outward on both sides at mirrored places; 4 the blast 44 squares wide, "
     "rock chips and dark debris flying out and up; 5 rolling grey smoke 46 squares wide, embers; 6 thin smoke.",
     row(6, 52, 44) + "; centered across, the ground (the satchel's base) 4 squares above the cell's bottom row."),
    ("w_hit", "W 炸中（目标身上），4 帧", "view_effects `league_ziggs_w_hit`（跟随，画在人物上面；左右对称）", "12",
     "被炸药包炸飞的敌人身上：橙色火光加白色的气浪弧线。**左右对称**。约 12 格。",
     f"{FI} and {SM}",
     f"a BLAST HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 an orange burst 9 squares with white blast-wave "
     "arcs on both sides; 3 the burst 12 squares fading, embers; 4 smoke wisps.",
     row(4, 12, 12) + CENTER),
    # ---- R Mega Inferno Bomb
    ("r_cast", "R 科学的地狱火炮：举在头顶的大炸弹（他身上，跟随），4 帧",
     "view_effects `league_ziggs_r_cast`（跟随，画在他上面 z 3；左右对称；大图表）", "30 × 60",
     f"他举起超大号的炸弹准备扔：头顶上方一颗**正立的大红炸弹**（约 22 格圆，正面一个大大的白色骷髅（参考 Ziggs_R_Skull），几道金属箍，"
     f"顶上粗引线和一大团黄橙色火星）。第 1 帧炸弹出现（一圈白光）；第 2–3 帧举着（火星闪动）；第 4 帧炸弹没了（已经扔出去），只剩几粒火星。"
     f"**左右对称**。炸弹的底边在格子底边往上 32 格（他两只举起的手在炸弹两边下方）；格子下面空着（{HIM}）。",
     f"{BO} and {FI}",
     f"THE MEGA BOMB held over a figure's head, 4 frames, {LR} ({HIM}): a BIG upright round red bomb 22 squares across, "
     "a big WHITE SKULL on its front (8 squares wide), two dark metal bands round it, a white highlight on its upper left "
     "and right, a thick dark fuse on top with a big yellow-orange spark 4 squares; 1 the bomb appearing in a white ring "
     "flash; 2 held, the spark bright; 3 held, the spark flickering differently; 4 the bomb gone, only 4 sparks where it "
     "was. Solid: a 1-square dark outline round the bomb is allowed.",
     row(4, 30, 60) + "; centered across, the bomb's lowest square 32 squares above the cell's bottom row."),
    ("r_bomb", "R 飞行中的大炸弹，3 帧循环", "view_projectiles `league_ziggs_r_bomb`（随飞行方向转动；上下对称；循环；大图表）", "28 × 20",
     "飞出去的超大炸弹：红色大圆炸弹（约 16 格）有几道深色金属箍，身后拖着一大串火焰和烟（参考 R_SmokeTrail、Flame_trail_gradient）。"
     "**上下对称**（飞向左边时会被上下翻过来），所以飞行中的炸弹上不画骷髅。",
     f"{BO} and {FI} and {SM}",
     f"THE MEGA BOMB in flight, 3 frames, a seamless loop, {TB}: a big round red bomb 16 squares across with two dark "
     "metal bands (straight across, symmetric), a white highlight top and bottom (mirrored), a thick trail of "
     "yellow-orange flame and grey smoke 12 squares long streaming behind it (to the left); the flames flicker each "
     "frame.",
     row(3, 28, 20) + FLY),
    ("r_warn", "R 落点预警（地上，不跟随，约 1.2 秒），8 帧",
     "view_effects `league_ziggs_r_warn`（不跟随，画在人物下面 z -2；左右对称；大图表）", "84 × 34",
     "大炸弹飞行的 1.2 秒里，落点地上的预警：一圈**红色的圆圈**（从斜上方看的扁椭圆：宽 80 格、高 30 格，参考 R_Ring_Indicator、R_Circle_normal），"
     "中间一个小一点的内圈（中心爆炸区，宽 36 格、高 14 格），正中间一个**红白色的骷髅标记**（参考 Ziggs_R_Center_Indicator），"
     "8 帧里红圈越来越亮、内圈往里收、骷髅一闪一闪，最后一帧最亮（马上要炸）。**左右对称**。",
     WA,
     f"A TARGET WARNING on the ground seen from above at an angle, 8 frames, {LR}: an outer red ring (an ellipse 80 "
     "squares wide and 30 tall, 1-2 squares thick) and an inner ring (an ellipse 36 wide and 14 tall), a red-and-white "
     "skull mark 10 squares wide flat on the ground in the middle; over the 8 frames the rings grow brighter and the inner "
     "ring shrinks a little each frame (36 -> 24 squares wide), the skull blinking (bright in 2, 4, 6, 8); frame 8 the "
     "brightest with white edges.",
     row(8, 84, 34) + "; centered across, the ellipse's middle 15 squares above the cell's bottom row."),
    ("r_boom", "R 大爆炸（地上，不跟随），8 帧", "view_effects `league_ziggs_r_boom`（不跟随，画在人物上面 z 2；左右对称；大图表）",
     "96 × 72",
     "超大炸弹落地爆炸（外圈半径约 40 格，中心 18 格）：白光一闪，一个巨大的橙黄色火球从地上升起，地上一圈红橙色的冲击波往外扩，"
     "火球变成一朵往上翻的蘑菇状灰黑烟云，碎石火星往四周飞，最后地上留下一圈焦黑的痕迹（参考 R_Storm_R_Dome、R_BlastStreaks、R_Colors、"
     "common_FB_explosion）。**左右对称**。",
     f"{FI} and {SM} and {WA}",
     f"A HUGE EXPLOSION on the ground, 8 frames, {LR}: 1 a white flash 20 squares just above the ground; 2 a huge "
     "orange-yellow fireball dome 40 squares wide and 26 tall rising from the ground with a white core; 3 the dome 60 "
     "squares wide and 40 tall, a red-orange shockwave ring along the ground (an ellipse 80 squares wide and 28 tall), "
     "blast streaks shooting up and out at mirrored angles; 4 the fireball rising into a mushroom of fire and dark smoke "
     "60 squares tall, debris and embers flying out; 5 the mushroom of grey-black smoke 70 tall, the fire inside dimmer; "
     "6 the smoke spreading 80 wide, the ring fading; 7 thinner smoke, a dark scorch ellipse on the ground; 8 faint "
     "smoke and the scorch.",
     row(8, 96, 72) + "; centered across, the ground (the explosion's base) 6 squares above the cell's bottom row."),
    ("r_hit", "R 炸中（敌人身上），4 帧", "view_effects `league_ziggs_r_hit`（跟随，画在人物上面；左右对称）", "14",
     "被大炸弹炸中的敌人身上：橙红色火光加黑烟和火星。**左右对称**。约 14 格。",
     f"{FI} and {SM}",
     f"a HEAVY BLAST HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 an orange-red burst 11 squares with a "
     "white core; 3 the burst 14 squares, black smoke and embers at mirrored places; 4 smoke wisps.",
     row(4, 14, 14) + CENTER),
]
BIG_FX = ["q_blast", "e_land", "e_field", "w_blast", "r_cast", "r_bomb", "r_warn", "r_boom"]
REDO = {}
GROUPS = [
    ("a_bomb p_bomb a_hit p_hit", ["FireHit", "FlashOrange", "Ziggs_Base_P_Flare",
                                   "common_FB_explosion_centerFlare", "Ziggs_Base_Q_Sparks"]),
    ("q_bomb q_bounce q_hit q_blast", ["Ziggs_Base_Q_BlastShapes", "Ziggs_Base_Q_explosion_smoke_mult",
                                       "Ziggs_Base_Q_FlareOmni", "Ziggs_Base_Q_Smoke02", "Ziggs_Base_Q_ringglow",
                                       "Ziggs_Base_Q_cinder"]),
    ("e_throw e_land e_field e_hit e_slow", ["Ziggs_Base_E_SoftIndicator", "Ziggs_Base_BlastRing", "Ziggs_Base_Crater_01",
                                             "color-bombground"]),
    ("w_blast w_hit", ["Ziggs_Satchel", "Ziggs_Base_W_rock_debris_blur", "Ziggs_Base_W_up_cylinder",
                       "Ziggs_Base_Mult_Windblast", "Ziggs_Base_Q_Swipe01"]),
    ("r_cast r_bomb r_warn", ["Ziggs_R_Skull", "Ziggs_R_Center_Indicator", "Ziggs_Base_R_Ring_Indicator_V2",
                              "Ziggs_Base_R_Circle_normal", "Ziggs_Base_R_SmokeTrail"]),
    ("r_boom r_hit", ["Ziggs_Base_R_Storm_R_Dome", "Ziggs_Base_R_BlastStreaks", "Ziggs_Base_R_Colors",
                      "Ziggs_Base_R_Mask", "common_FB_explosion_cloud"]),
]
FEET = 11                                             # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_bomb / p_bomb：远侧手把小炸弹扔出去"), ("skill", 4, "q_bomb：Q 抛出弹跳炸弹"),
         ("skill2", 3, "e_throw：甩出一把地雷"), ("skill_w", 2, "w_blast：脚下的炸药包炸开（下一帧他被炸飞）"),
         ("skill_w", 4, "被炸飞到空中"), ("ult", 2, "r_cast：大炸弹画在举起的两只手上方"),
         ("ult", 4, "r_bomb：把大炸弹推出去"), ("idle", 1, "待机")]


def ref_sheet(path):
    S, LW = 170, 170
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                sys.exit(f"missing reference {p}")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Ziggs_Base_", "").replace("Ziggs_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"吉格斯 {figs[0].shape[1]}×{figs[0].shape[0]} 格（含两颗炸弹），原版斗士 {figs[1].shape[1]}×"
                    f"{figs[1].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
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
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is his pivot, FEET rows over the ground
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
    """His idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    import rig_ziggs as J
    F = J.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)).save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 吉格斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/ziggs_idle.png`：3/4 正面朝右的约德尔爆破专家，蓝红条纹头盔、"
      f"绿色护目镜、尖耳朵、咧嘴白牙、米黄胡子，红外套、牛仔蓝背带裤，两只手各托一颗带白骷髅的红炸弹）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连两颗炸弹 {h} 格高、{w} 格宽；"
      f"**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/ziggs_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/ziggs_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里吉格斯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**炸弹是带白骷髅的红色圆炸弹**，**爆炸是橙黄色的火加灰烟**，**被动和地雷的火花带蓝白色的海克斯光**，"
      "**大招落点是红色的圆圈加骷髅标记**。")
    a("> - **特效要亮**：每团光、每次爆炸都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **飞行中的炸弹（a_bomb、p_bomb、e_throw、r_bomb）上下对称**：游戏会把飞行的图按飞的方向转，往左飞时整张图上下翻过来，"
      "所以飞行中的炸弹不画骷髅，引线的火星画成拖在身后（左边）的尾巴，上下对称。")
    a("> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他朝左时也是同一张图。")
    a("> - **围着人的画面中间身体位置留空**，不要盖住人。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 20]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ziggs_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/ziggs_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。"
      "中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「一触即发」 | 扔小炸弹；每隔一段时间下一次普攻扔一颗海克斯强化炸弹，多一份魔法伤害 | `a_bomb` · `a_hit` · `p_bomb` · `p_hit` |")
    a("| 技能 1 = Q「弹跳炸弹」 | 炸弹沿直线一跳一跳（最多落地三次），落地时附近有敌人就爆炸 | `q_bomb`（空中） · `q_bounce` · `q_blast` · `q_hit` |")
    a("| 技能 2 = E「海克斯爆破雷区」 | 扔出一把地雷散在地上 5 秒，敌人踩到就炸并减速 | `e_throw` · `e_land` · `e_field` · `e_hit` · `e_slow` |")
    a("| 自动放的 W「定点爆破」 | 敌人贴脸时炸药包在脚下炸开，把敌人炸开、自己也被炸飞 | `w_blast` · `w_hit` |")
    a("| 大招「科学的地狱火炮」 | 举起超大炸弹扔到很远的地方，落点先有红圈预警，中心伤害更高 | `r_cast` · `r_bomb` · `r_warn` · `r_boom` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：炸弹、地雷、炸药包可以有一圈深色边）。")
    a("- **要亮**：每个光和火的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火和火星（所有爆炸、引线）", FIRE), ("海克斯蓝白光（被动、地雷的火花）", HEX), ("炸弹的红色外壳（加纯白的骷髅）", BOMB),
                        ("烟和尘土、炸药包的灰", SMOKE), ("预警红（大招落点、地雷的红灯）", WARN)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 爆炸半径 20000，雷区半径 30000，"
      "炸药包半径 30000，大招外圈 40000、中心 18000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `ziggs_fx_{name}.png`：{title}\n")
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
        a(f"| `ziggs_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_ziggs_fx`（小的）和 `league_ziggs_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_ziggs.py 的 views）。`q_bomb` 不直接绑定：导入时按 build_ziggs.air_heights 的高度把它抬起，生成 `q_air<h>` 各 tag（每个 3 帧，50 ms）。")
    a("- 投射物 `a_bomb`、`p_bomb`、`e_throw`、`r_bomb` 是 view_projectiles（随飞行方向转动，断言上下对称）；其余断言左右对称。"
      "`e_field` 每 15 tick 在落点重贴一次（3 帧 × 83 ms），`r_warn` 8 帧铺满飞行的 70 tick。`w_blast` 不跟随（他被炸飞后爆炸留在原地）。")
    a("- 用 `pixel_1x/` 切格（import_jarvaniv_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="ziggs_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "ziggs_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/zg/fx_ref_zg.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "ziggs_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "ziggs_size.png"))
    shots_sheet(os.path.join(out, "design", "ziggs_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"ziggs_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
