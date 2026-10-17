#!/usr/bin/env python3
"""Build xerath_fx_pack.zip: step 3 of Xerath's sprite - Codex draws his effects (after tools/art/pack_tryndamere_fx.py).

    python tools/art/pack_xerath_fx.py [--no-zip] [--out DIR] [--only a_hit,q_beam --name xerath_fx_redo_pack]

The pack (%TEMP%/xr_work/fx/xerath_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/xerath/PROMPTS_FX.md), design/xerath_design.png (8x), design/xerath_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside him), design/xerath_shots.png (the finished
action frames at 4x - assets/source/native/xerath_<tag>.png - with the point each caster picture starts from) and
refs/lol_fx_ref.png (League's own particle textures for Xerath, grouped by the effect of ours they inform; Riot's art,
local only: it reads %TEMP%/xr_work/fxref, extracted from Xerath.wad.client).
The effects are the views the kit binds (tools/kit/build_xerath.py: view_projectiles a_orb, a_orb_p, q_beam, q_beam_s,
e_orb; view_effects a_flash, a_hit, p_surge, p_hit, q_charge, q_charge_s, q_fire, q_hit, e_cast, e_hit, w_mark, w_blast,
w_hit, r_rise, r_cast_shot, r_end, r_mark, r_bolt, r_hit; view_buffs e_stun, w_slow, r_chan). League's colours: the
bright cyan-blue arcane energy of his base skin with white-hot cores, a deep blue-violet for the ground scorch and the
rune circles. Light, beams and lightning get no outline; the bright-effects lesson (Nocturne) holds.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "xr_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "xerath", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "xerath_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ARC = "#FFFFFF, #E0FCFF, #9AF2FF, #4CD4FF, #1E8CF0, #1A48C0"     # the arcane energy: orbs, beams, blasts, sparks
DEEP = "#8AA8FF, #5A64E8, #3A34B0, #241C70, #120C3A"             # rune circles, ground scorch, the eye's dark iris
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, beams, lightning, runes, smoke or sparks (only the solid stone shards get a 1-square "
        "dark outline #0A0A12), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on "
        "a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h}"
FIG = "do NOT draw the figure; leave its place empty"
AC = f"an arcane cyan-blue ramp ({ARC})"
DC = f"a deep blue-violet ramp ({DEEP})"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_orb", "普攻法球（飞行中，循环），4 帧", "view_projectiles `league_xerath_a_orb`（朝飞行方向转，画成朝右飞）", "14 × 8",
     "泽拉斯普攻甩出的奥术法球：一颗亮青白色的小能量球，后面拖一小段青色的尾巴，几点火花（参考 Z_Mote、common_ball32、Z_EnergyWisps）。"
     "朝右飞（尾巴在左）。4 帧无缝循环（球的光一闪一闪、尾巴抖动）。约 14 格宽、8 格高，球在格子右半边的中间。",
     AC,
     "an ARCANE ORB in flight to the RIGHT, 4 frames, a seamless loop: a round orb 6 squares across, a white core with "
     "bright cyan and blue rims, a short tapering cyan trail 8 squares long to its LEFT, 2-3 tiny sparks; the orb's glow "
     "pulses and the trail flickers each frame.",
     ROW.format(n=4, shape="7:4", w=896, h=512) + " (each cell 224x128); the orb's center 3/5 of the way across and "
     "vertically centered in every cell."),
    ("a_orb_p", "法力澎湃的强化法球（飞行中，循环），4 帧", "view_projectiles `league_xerath_a_orb_p`（朝飞行方向转，画成朝右飞）",
     "20 × 12",
     "被动「法力澎湃」那一下普攻：比普通法球大一圈，外面绕着两三道细小的蓝色闪电，尾巴更长更亮（参考 Z_Bolts、Z_BoltsBlue、Z_Mote、"
     "Z_EnergySwirls）。朝右飞。4 帧无缝循环。约 20 格宽、12 格高。",
     AC,
     "an EMPOWERED ARCANE ORB in flight to the RIGHT, 4 frames, a seamless loop: a round orb 9 squares across (white core, "
     "cyan and blue rims), 2-3 thin crackling blue lightning arcs wrapped round it changing every frame, a bright tapering "
     "cyan trail 11 squares long to its LEFT, a few sparks.",
     ROW.format(n=4, shape="5:3", w=1280, h=768) + " (each cell 320x192); the orb's center 3/5 of the way across and "
     "vertically centered in every cell."),
    ("a_flash", "普攻出手：爪子前的闪光（施法者身上），3 帧",
     "view_effects `league_xerath_a_flash`（施法者身上，不跟随；格子中心放到出手帧的前爪）", "12",
     "甩出法球的那一下：前爪前面一下青白色的小闪光，几道往右散开的光丝（参考 common_flare-blue、Z_Nova）。约 12 格，居中画。",
     AC,
     "a SMALL CAST FLASH at a hand, 3 frames: 1 a white-cyan flash 8 squares across at the center with 4 short rays; 2 "
     "the flash smaller, rays streaking to the right; 3 a few fading sparks.",
     ROW.format(n=3, shape="square", w=768, h=256) + "; centered in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_xerath_a_hit`（跟随，画在人物上面）", "14",
     "法球打中：一团青白色的奥术光爆开，一圈细细的蓝光环，几点火花飞出去（参考 common_blast_nova、Z_Nova、Z_Rings）。约 14 格，居中画。",
     AC,
     "an ARCANE HIT, 4 frames: 1 a white-cyan burst 8 squares across at the center; 2 a thin blue ring 12 squares across "
     "spreading from it, 5 sparks flying out; 3 the ring fading, sparks further out; 4 a few fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("p_surge", "法力澎湃：强化普攻时手上的蓝光（施法者身上），4 帧",
     "view_effects `league_xerath_p_surge`（施法者身上，不跟随；格子中心放到出手帧的前爪）", "18",
     "被动这一下：前爪周围一下涌出一团蓝色能量，两三圈小光环往外扩，几道蓝色闪电（参考 Z_EnergySwirls、Z_Rings、Z_BoltsBlue）。约 18 格，居中画。",
     AC,
     "a MANA SURGE round a hand, 4 frames: 1 a swirl of bright cyan energy 10 squares across at the center; 2 two thin "
     "blue rings spreading out to 16 squares, 3 short blue lightning arcs; 3 the rings at the edge, sparks; 4 fading.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("p_hit", "法力澎湃打中（目标身上），5 帧", "view_effects `league_xerath_p_hit`（跟随，画在人物上面）", "20",
     "强化法球打中：比普通打中更大的青白色爆炸，一圈蓝光环往外冲，几道闪电和火花（参考 common_blast_nova、Z_Nova、Z_Bolts）。约 20 格，居中画。",
     AC,
     "an EMPOWERED ARCANE HIT, 5 frames: 1 a white-cyan burst 10 squares across; 2 a blue ring 16 squares across "
     "spreading from it, 3 crackling lightning arcs, sparks; 3 the ring at 20 squares, the burst fading; 4 sparks; 5 a "
     "few fading sparks.",
     ROW.format(n=5, shape="square", w=1280, h=256) + "; centered in every cell."),
    # ---- Q: Arcanopulse
    ("q_charge", "Q 蓄力：能量往前爪聚集（施法者身上，约 0.9 秒），8 帧",
     "view_effects `league_xerath_q_charge`（施法者身上，跟随；格子里的站位点放到他脚下）", "56 × 56",
     "Q「奥能脉冲」蓄满：泽拉斯举起双手蓄力，四周的蓝色光丝和光点被吸向**前爪**，前爪上的光球越来越大越来越亮，身边几道细闪电；"
     "最后一帧最亮（参考 Q_BeamEnergy、Z_EnergyWisps、Z_Mote、Z_BoltsThin）。中间是人，不要画人。前爪的位置：站位点右边 10 格、"
     "上面 20 格（`design/xerath_shots.png` 里 skill 5 的十字）。8 帧：1–2 光丝出现，3–6 往前爪聚、光球变大，7–8 光球最大（6 格）、闪电。"
     "约 56 格见方，站位点在格子底部往上 8 格的中间。",
     AC,
     f"an ENERGY CHARGE gathering at a raised hand ({FIG}), 8 frames: the hand's point is 10 squares right of and 20 "
     "squares above the standing point; 1-2 thin cyan light streaks and motes appear up to 24 squares round that point; "
     "3-6 they are drawn in toward it, a glowing white-cyan orb growing there from 2 to 5 squares; 7-8 the orb at its "
     "brightest, 6 squares, 2-3 thin blue lightning arcs flickering round it.",
     ROW.format(n=8, shape="square", w=2048, h=256) + "; the standing point 8 squares above the bottom, horizontally "
     "centered, in every cell (the hand's point 10 right of it, 20 above it)."),
    ("q_charge_s", "Q 快速蓄力（打小兵时，约 0.4 秒），4 帧",
     "view_effects `league_xerath_q_charge_s`（施法者身上，跟随；站位点放到他脚下）", "56 × 56",
     "同上，但短：4 帧里光丝很快聚到前爪，光球只到 4 格（参考 Q_BeamEnergy、Z_Mote）。格子和站位点同上。",
     AC,
     f"a QUICK ENERGY CHARGE at a raised hand ({FIG}), 4 frames: the hand's point 10 squares right of and 20 above the "
     "standing point; 1 a few cyan streaks round it; 2-3 drawn in, a white-cyan orb growing to 3 squares; 4 the orb at 4 "
     "squares, bright.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; the standing point 8 squares above the bottom, horizontally "
     "centered, in every cell."),
    ("q_fire", "Q 发射：前爪射出光束的闪光（施法者身上），3 帧",
     "view_effects `league_xerath_q_fire`（施法者身上，不跟随；格子中心放到出手帧的前爪）", "24 × 16",
     "光束发射的那一下：前爪前面一大团白青色的闪光，朝右喷出一道很亮的光（参考 Q_Beam、common_flare-blue、Z_Nova）。约 24 格宽、16 格高，"
     "闪光中心在格子左边三分之一处。",
     AC,
     "a BEAM MUZZLE FLASH at a hand, 3 frames: 1 a white-cyan flash 10 squares across at the point with a bright blast "
     "of light shooting 12 squares to the RIGHT; 2 the flash smaller, the blast thinning; 3 fading sparks.",
     ROW.format(n=3, shape="3:2", w=1152, h=512) + " (each cell 384x256); the flash's center 1/3 of the way across and "
     "vertically centered in every cell."),
    ("q_beam", "Q 奥能脉冲光束（蓄满，飞行中，循环），3 帧",
     "view_projectiles `league_xerath_q_beam`（朝飞行方向转，画成朝右飞；上下对称）", "56 × 12",
     "蓄满的奥能脉冲：一道很长很亮的光束，白色的芯、青色和蓝色的边，边上跳着细小的闪电，前端最亮（参考 Q_Beam、Q_Beam_01–03、"
     "Q_Beam_Mult、Z_EnergyStreaks）。朝右飞。**上下对称**（红方飞向左时会被上下翻转）。3 帧无缝循环（边缘的电光每帧变）。约 56 格长、12 格高。",
     AC,
     "a LONG ARCANE BEAM flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a straight beam 54 "
     "squares long and 6 squares thick, a white core 2 squares thick, bright cyan then blue edges, the front end a little "
     "wider and brightest, the back end tapering; thin crackling blue lightning flickering along both edges, different "
     "each frame.",
     ROW.format(n=3, shape="14:3", w=2688, h=192) + " (each cell 896x192); the beam vertically centered in every cell."),
    ("q_beam_s", "Q 快速蓄力的短光束（飞行中，循环），3 帧",
     "view_projectiles `league_xerath_q_beam_s`（朝飞行方向转，画成朝右飞；上下对称）", "36 × 10",
     "同上，短一些细一些（参考 Q_Beam）。上下对称，3 帧循环。约 36 格长、10 格高。",
     AC,
     "a SHORTER ARCANE BEAM flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a straight beam 34 "
     "squares long and 4 squares thick, a white core, cyan and blue edges, a little crackle along the edges.",
     ROW.format(n=3, shape="18:5", w=1728, h=160) + " (each cell 576x160); the beam vertically centered in every cell."),
    ("q_hit", "Q 打中（目标身上），4 帧", "view_effects `league_xerath_q_hit`（跟随，画在人物上面）", "14",
     "光束穿过：一道横着的青白色电光闪过，几点火花（参考 Z_BoltsThin、common_flare-blue）。约 14 格，居中画。",
     AC,
     "a BEAM STRIKE, 4 frames: 1 a horizontal white-cyan streak 14 squares long through the center with a flash 6 squares "
     "across; 2 the streak thinning, 3 short blue lightning forks; 3 sparks; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    # ---- E Shocking Orb -> W Eye of Destruction
    ("e_cast", "E 出手：前爪的电光（施法者身上），3 帧",
     "view_effects `league_xerath_e_cast`（施法者身上，不跟随；格子中心放到出手帧的前爪）", "16",
     "甩出冲击法球：前爪前面一下蓝白色的电光，几道短闪电往右（参考 Z_BoltsBlue、common_flare-blue）。约 16 格，居中画。",
     AC,
     "an ELECTRIC CAST FLASH at a hand, 3 frames: 1 a white-cyan flash 8 squares across with 3 short blue lightning forks "
     "to the right; 2 the forks longer and thinner; 3 fading sparks.",
     ROW.format(n=3, shape="square", w=768, h=256) + "; centered in every cell."),
    ("e_orb", "E 冲击法球（飞行中，循环），4 帧", "view_projectiles `league_xerath_e_orb`（朝飞行方向转，画成朝右飞）", "16 × 12",
     "冲击法球：一颗圆的蓝白色电球，外面绕着几道噼啪作响的闪电，后面一段短尾巴（参考 Z_Bolts、Z_WarpedSphere、Z_Mote、common_lightning_bea）。"
     "朝右飞。4 帧无缝循环（闪电每帧换形状）。约 16 格宽、12 格高。",
     AC,
     "a SHOCKING ORB in flight to the RIGHT, 4 frames, a seamless loop: a round electric orb 8 squares across (a white core, "
     "cyan and blue rims), 3-4 crackling blue-white lightning arcs jumping round it (different every frame), a short cyan "
     "trail 6 squares to its LEFT.",
     ROW.format(n=4, shape="4:3", w=1024, h=768) + " (each cell 256x192); the orb's center 3/5 of the way across and "
     "vertically centered in every cell."),
    ("e_hit", "E 打中：眩晕的电爆（目标身上），5 帧", "view_effects `league_xerath_e_hit`（跟随，画在人物上面）", "22",
     "冲击法球打中：一团很亮的蓝白色电爆，一圈电光往外，好几道闪电噼啪散开（参考 Z_Bolts、common_blast_nova、Z_Nova）。约 22 格，居中画。",
     AC,
     "an ELECTRIC SHOCK BURST, 5 frames: 1 a white-cyan flash 12 squares across; 2 a crackling ring of blue lightning 18 "
     "squares across, 5 lightning forks shooting out; 3 the ring at 22 squares, the forks thinner; 4 sparks; 5 a few "
     "fading sparks.",
     ROW.format(n=5, shape="square", w=1280, h=256) + "; centered in every cell."),
    ("e_stun", "E 眩晕：头上的电光（敌人身上，循环），4 帧", "view_buffs `league_xerath_e_stun`（循环，画在人物上面，头顶）", "14 × 8",
     "被晕住的敌人：头顶一圈扁扁的蓝色电光在转，几颗小电火花（参考 Z_BoltsThin、common_sparks32）。左右对称，4 帧无缝循环。约 14 格宽、8 格高，"
     "电光圈在格子底部往上 2 格（导入时放到头顶）。",
     AC,
     "a STUN MARK over a head, SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: a flattened ellipse 12 squares wide "
     "and 4 tall of crackling blue-white lightning circling, 3 bright sparks on it moving a quarter of the way round each "
     "frame.",
     ROW.format(n=4, shape="7:4", w=896, h=512) + " (each cell 224x128); the ellipse centered across, its bottom 2 "
     "squares above the bottom of every cell."),
    ("w_mark", "W 毁灭之眼：地上的预警法阵（落点，约 0.6 秒），8 帧",
     "view_effects `league_xerath_w_mark`（BIG，落点，不转；画在人物下面）", "56 × 28",
     "W「毁灭之眼」：目标脚下的地面出现一个奥术法阵——外圈一个青色的椭圆环（从斜上方看，宽是高的 2 倍，约 52 格宽），里面一圈深蓝紫色的"
     "符文环在转，正中一个小一点的亮环（中心区，约 22 格宽）像一只眼睛的瞳孔；法阵一帧比一帧亮，最后两帧最亮（随后光柱落下，见下一张）"
     "（参考 W_TargetRing、R_AoeRing_TX、Z_Rings、W_Scorch）。8 帧。约 56 格宽、28 格高，中心在格子正中。",
     f"{AC} and {DC}",
     "an ARCANE TARGET CIRCLE on the ground, seen from above at an angle (every ring a flattened ellipse twice as wide as "
     "tall), 8 frames: 1 a thin cyan outer ring 52 squares wide fades in; 2-4 a ring of deep blue-violet runes turning "
     "inside it, an inner bright ring 22 squares wide (the eye's pupil) appearing at the center; 5-6 everything brighter, "
     "the runes glowing cyan; 7-8 the brightest, a white glow filling the inner ring.",
     ROW.format(n=8, shape="2:1", w=4096, h=256) + " (each cell 512x256); the circle centered in every cell."),
    ("w_blast", "W 毁灭之眼：从天而降的光柱爆炸（落点），6 帧",
     "view_effects `league_xerath_w_blast`（BIG，落点，不转；画在人物上面）", "44 × 72",
     "法阵亮到最高时：一道粗大的青白色奥术光柱从天上直直砸到法阵中心，地面爆开一圈蓝白色的冲击波和火花，然后光柱变细消失（参考 W_SkyBeam、"
     "W_BlastDome、common_blast_nova、Z_Nova、Z_PraxisWave）。**光柱是竖直的**。6 帧：1 光柱从上落下到地面，2 光柱最粗、地面白光，3 冲击波"
     "往外（扁椭圆，40 格宽），4–5 光柱变细、火花，6 淡去。约 44 格宽、72 格高，地面中心在格子底部往上 12 格的中间。",
     f"{AC} and {DC}",
     "an ARCANE PILLAR crashing down onto a spot on the ground, 6 frames: 1 a thick vertical pillar of white-cyan light 12 "
     "squares wide coming straight down from the top of the cell to the ground point; 2 the pillar at its thickest, a "
     "white flash on the ground 20 squares wide; 3 a blue-white shockwave ring along the ground (a flattened ellipse twice "
     "as wide as tall, 40 squares wide), sparks; 4-5 the pillar thinning to a line, the ring fading, sparks rising; 6 "
     "fading motes.",
     ROW.format(n=6, shape="11:18", w=2112, h=576) + " (each cell 352x576); the ground point 12 squares (96 px) above "
     "the bottom, horizontally centered, in every cell."),
    ("w_hit", "W 打中（敌人身上），4 帧", "view_effects `league_xerath_w_hit`（跟随，画在人物上面）", "16",
     "被毁灭之眼砸中：一下蓝白色的闪光，几点往上溅的火花（参考 Z_Nova、common_sparks32）。约 16 格，居中画。",
     AC,
     "an ARCANE BLAST HIT, 4 frames: 1 a white-cyan flash 10 squares across; 2 sparks splashing up and out; 3 sparks "
     "higher; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("w_slow", "W 减速：脚下的标记（敌人身上，循环 2.5 秒），4 帧", "view_buffs `league_xerath_w_slow`（循环，画在脚下）", "18 × 8",
     "被减速的敌人：脚下一圈深蓝紫色的光，几缕往下沉的蓝光（参考 Z_Rings、W_Scorch）。左右对称，4 帧无缝循环。约 18 格宽、8 格高，贴着地面。",
     f"{DC} and {AC}",
     "a SLOW MARK at a figure's feet (do NOT draw the figure; SYMMETRIC LEFT AND RIGHT), 4 frames, a seamless loop: a "
     "flattened ellipse of deep blue-violet light on the ground (twice as wide as tall, 16 squares wide), 4 short cyan "
     "streaks sinking DOWN into it a square each frame.",
     ROW.format(n=4, shape="9:4", w=2304, h=256) + " (each cell 576x256); the ellipse at the bottom middle of every cell."),
    # ---- R Rite of the Arcane
    ("r_rise", "R 起手：飞升（施法者身上，0.5 秒），6 帧",
     "view_effects `league_xerath_r_rise`（BIG，施法者身上，跟随；格子里的站位点放到他脚下）", "52 × 72",
     "R「奥术仪式」开始：泽拉斯飞升，脚下一圈奥术法阵亮起，一道青白色的光柱从脚下冲上天，几片发光的石甲碎片和蓝色符文绕着他往上飘"
     "（参考 Z_PraxisWave、W_SkyBeam、Z_Rings、Z_EnergyWisps、Z_Energy_4x4）。中间是人，不要画人。**左右对称**。6 帧：1 脚下法阵亮起，"
     "2–3 光柱冲上去、符文和碎片升起，4 最亮，5–6 光柱变细、符文留在身边。约 52 格宽、72 格高，站位点在格子底部往上 8 格的中间。",
     f"{AC} and {DC}",
     f"an ASCENSION round a floating figure ({FIG}; SYMMETRIC LEFT AND RIGHT), 6 frames: 1 a flattened rune circle "
     "(twice as wide as tall, 40 squares wide) lights up on the ground round the standing point; 2-3 a column of "
     "white-cyan light rising from it past the top of the cell, behind the figure's place, its edges only (the figure's "
     "place inside stays mostly empty), glowing blue runes and a few small outlined stone shards rising round it; 4 the "
     "brightest; 5-6 the column thinning, runes floating at shoulder height.",
     ROW.format(n=6, shape="13:18", w=2496, h=576) + " (each cell 416x576); the standing point 8 squares (64 px) above "
     "the bottom, horizontally centered, in every cell."),
    ("r_chan", "R 引导：脚下转动的符文法阵（引导期间循环），6 帧",
     "view_buffs `league_xerath_r_chan`（BIG，循环，画在人物下面）", "48 × 24",
     "引导期间：泽拉斯脚下一圈缓缓转动的深蓝紫色符文法阵，外圈青色，几颗光点往上飘（参考 Z_PraxisWave、Z_Rings、R_AoeRing_TX、common_renekton_rune）。"
     "**左右对称、以站位点为中心**（人朝左朝右都用这一张）。6 帧无缝循环。约 48 格宽、24 格高，中心在格子正中。",
     f"{DC} and {AC}",
     "a TURNING RUNE CIRCLE on the ground under a floating figure, seen from above at an angle (a flattened ellipse twice "
     "as wide as tall, 44 squares wide), SYMMETRIC LEFT AND RIGHT, 6 frames, a seamless loop: a bright cyan outer ring, "
     "inside it a ring of deep blue-violet runes, a smaller inner ring; the runes shift round a step each frame; 3-4 small "
     "motes rising from the ring.",
     ROW.format(n=6, shape="2:1", w=3072, h=256) + " (each cell 512x256); the circle centered in every cell."),
    ("r_cast_shot", "R 每一发：前爪往上的闪光（施法者身上），3 帧",
     "view_effects `league_xerath_r_cast_shot`（施法者身上，不跟随；格子中心放到出手帧的前爪）", "16 × 20",
     "召唤一发炮击：前爪上一下青白色的闪光，一道细光往上冲出格子（参考 W_SkyBeam、common_flare-blue）。约 16 格宽、20 格高，闪光中心在格子下半部分。",
     AC,
     "a SUMMONING FLASH at a hand, 3 frames: 1 a white-cyan flash 8 squares across, a thin bright ray shooting UP from it "
     "to the top of the cell; 2 the ray thinner, sparks; 3 fading sparks.",
     ROW.format(n=3, shape="4:5", w=768, h=320) + " (each cell 256x320); the flash's center 2/3 of the way down, "
     "horizontally centered, in every cell."),
    ("r_end", "R 结束：落下的符文碎光（施法者身上），4 帧",
     "view_effects `league_xerath_r_end`（施法者身上，不跟随；格子里的站位点放到他脚下）", "32 × 48",
     "引导结束：身边的符文碎成一片蓝色光点落下来、消散（参考 Z_EnergyWisps、Z_Mote）。中间是人，不要画人。左右对称。4 帧。"
     "约 32 格宽、48 格高，站位点在格子底部往上 6 格的中间。",
     AC,
     f"FADING RUNES round a figure ({FIG}; SYMMETRIC LEFT AND RIGHT), 4 frames: 1 a dozen cyan rune glyphs and motes "
     "round the figure's place from its feet to its head; 2 they break into motes; 3 the motes drifting down; 4 a few "
     "fading motes near the ground.",
     ROW.format(n=4, shape="2:3", w=1024, h=384) + " (each cell 256x384); the standing point 6 squares above the bottom, "
     "horizontally centered, in every cell."),
    ("r_mark", "R 炮击预警：地上的瞄准圈（落点，约 0.6 秒），7 帧",
     "view_effects `league_xerath_r_mark`（BIG，落点，不转；画在人物下面）", "40 × 20",
     "R 每一发的落点：地上一个青色的瞄准圈（扁椭圆，约 36 格宽），里面一个十字和一圈深蓝紫色的符文，圈一帧比一帧缩小、变亮，最后一帧最亮"
     "（参考 R_AoeRing_TX、W_TargetRing、Z_Rings）。7 帧。约 40 格宽、20 格高，中心在格子正中。",
     f"{AC} and {DC}",
     "an ARTILLERY TARGET MARK on the ground, seen from above at an angle (a flattened ellipse twice as wide as tall), 7 "
     "frames: 1 a thin cyan ring 38 squares wide appears with 4 short tick marks pointing in; 2-5 a deep blue-violet rune "
     "ring inside it, the outer ring closing in to 30 squares, a small cross at the center, brighter each frame; 6-7 the "
     "brightest, white glow at the center.",
     ROW.format(n=7, shape="2:1", w=3584, h=256) + " (each cell 512x256); the mark centered in every cell."),
    ("r_bolt", "R 炮击：从天而降的奥术炮弹和爆炸（落点），7 帧",
     "view_effects `league_xerath_r_bolt`（BIG，落点，不转；画在人物上面）", "48 × 84",
     "奥术仪式的一发炮击：一道青白色的光弹拖着长长的光尾从天上**竖直**砸下来，落地炸开一大团蓝白色的爆炸，一圈冲击波和往上溅的火花，然后散去"
     "（参考 Z_Mortar、W_SkyBeam、common_blast_nova、Z_Nova、Z_BlastDarkStreak、Z_PraxisWave）。7 帧：1–2 光弹从格子顶上往下落（第 2 帧快落地），"
     "3 落地白光，4 爆炸最大、冲击波（扁椭圆，40 格宽），5–6 火花往上、烟散开，7 淡去。约 48 格宽、84 格高，地面中心在格子底部往上 12 格的中间。",
     f"{AC} and {DC}",
     "an ARCANE ARTILLERY SHELL falling straight down onto a spot, 7 frames: 1 a bright white-cyan bolt 6 squares wide "
     "with a long tapering trail coming down from the top of the cell; 2 the bolt just above the ground point; 3 a white "
     "flash on the ground 18 squares wide; 4 the explosion at its biggest - a blue-white burst 24 squares across and a "
     "shockwave ring along the ground (a flattened ellipse twice as wide as tall, 40 squares wide); 5-6 sparks thrown up, "
     "dark blue smoke spreading; 7 fading motes.",
     ROW.format(n=7, shape="4:7", w=1792, h=448) + " (each cell 256x448 at 2/3 scale - or 384x672 if you can: keep the "
     "4:7 shape); the ground point 1/7 of the cell height above the bottom, horizontally centered, in every cell."),
    ("r_hit", "R 炮击打中（敌人身上），4 帧", "view_effects `league_xerath_r_hit`（跟随，画在人物上面）", "18",
     "被炮击砸中：一下蓝白色的闪光和一圈电光（参考 Z_Nova、Z_Bolts）。约 18 格，居中画。",
     AC,
     "an ARTILLERY HIT, 4 frames: 1 a white-cyan flash 12 squares across; 2 a crackling blue ring 16 squares across, "
     "sparks; 3 sparks; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
]

GROUPS = [
    ("orb", ["Z_Mote", "common_ball32_01", "common_ball32_02", "Z_EnergyWisps", "Z_EnergySwirls_1x4", "Z_Nova"]),
    ("beam", ["Q_Beam", "Q_Beam_01", "Q_Beam_02", "Q_Beam_03", "Q_Beam_Mult", "Q_BeamEnergy"]),
    ("shock", ["Z_Bolts", "Z_BoltsBlue", "Z_BoltsThin", "Z_WarpedSphere_TX", "common_flare-blue", "common_blast_nova_bu"]),
    ("eye", ["W_TargetRing", "W_SkyBeam", "W_BlastDome", "W_Scorch", "Z_Rings", "Z_PraxisWave"]),
    ("rite", ["R_AoeRing_TX", "Z_Mortar", "Z_BlastDarkStreak", "Z_Energy_4x4", "Z_EnergyStreaks_1x4", "common_renekton_rune"]),
]
# where the caster pictures go: (tag, frame, what, mark: "feet" = the standing point, or (dx, dy) from it)
SHOTS = [("attack", 4, "a_flash / p_surge: 前爪", (18, -15)), ("skill", 5, "q_charge: 前爪（蓄力）", (10, -20)),
         ("skill", 6, "q_fire: 前爪（发射）", (18, -15)), ("skill2", 3, "e_cast: 前爪", (18, -15)),
         ("ult", 3, "r_rise: 脚下", "feet"), ("ult_shot", 1, "r_cast_shot: 前爪", (18, -15)), ("idle", 1, "r_chan / r_end: 脚下", "feet")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    on_disk = {os.path.splitext(f)[0] for f in os.listdir(REF)}
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            nm = next((x for x in sorted(on_disk) if x.lower().replace("xerath_base_", "").startswith(nm.lower())), nm)
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Xerath_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"泽拉斯 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def frame_of(tag, k):
    """Frame k (1-based) of the finished strip at 1x, cut round its cell, and its pivot in the cut."""
    cells = json.load(open(lp(os.path.join(NATIVE, "xerath_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    frs = cells["tags"][tag]
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(len(frs), 4)
    a = np.asarray(Image.open(lp(os.path.join(NATIVE, f"xerath_{tag}.png"))).convert("RGBA"))[4::8, 4::8]
    i = k - 1
    x0, y0 = (i % cols) * cw, (i // cols) * ch
    return a[y0:y0 + ch, x0:x0 + cw], frs[i]["pivot"]


def shots_sheet(path):
    """The finished action frames at 4x, the point each caster picture starts from as a cyan cross."""
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, mark in SHOTS:
        f, (px, py) = frame_of(tag, k)
        mx, my = (px, py + 11) if mark == "feet" else (px + mark[0], py + mark[1])
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0, x1 = min(xs.min(), mx) - 3, max(xs.max(), mx) + 4
        y0, y1 = min(ys.min(), my) - 3, max(ys.max(), my) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 220), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = (mx - x0) * Z + Z // 2, (my - y0) * Z + Z // 2 + 24
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
    a("# 远古巫灵 泽拉斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/xerath_design.png`，8 倍，{h} 行）。")
    a(f"> - 大小对照 `design/xerath_size.png`：定稿造型放大 4 倍，腿尖在红线上，上面是 10 格一段的刻度，右边是原版斗士。泽拉斯 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/xerath_shots.png`：普攻、Q、E、R 和待机的定稿动作（4 倍），青色十字是特效的起点（前爪或脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里泽拉斯自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**奥术能量是亮青蓝色带白芯（法球、光束、电光、光柱、炮击）；地面的法阵和符文是深蓝紫色带青色亮边**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的光柱、法阵、符文只画边，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要）**：飞行的东西（法球、光束、冲击法球）一律画成朝右飞，游戏会按飞行方向转；光束要**上下对称**（往左飞时会上下翻）。从天上砸下来的光柱和炮击、地上的法阵是**竖直不转**的，照写的方向画。挂在人身上或脚下的循环画面（`e_stun`、`w_slow`、`r_chan`）和 `r_rise`、`r_end` 要**左右对称**，人朝左朝右都用同一张。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `xerath_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`xerath_fx_done.zip`）放在 outputs 里，或放在 `outputs/xerath-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「法力澎湃」 | 甩出奥术法球；每 14 秒一次强化法球（额外魔法伤害、缩短小技能冷却），击杀单位让它提前 | `a_orb` · `a_flash` · `a_hit` · `a_orb_p` · `p_surge` · `p_hit` |")
    a("| 技能 1 = Q「奥能脉冲」 | 举手蓄力，然后朝前射出一道贯穿光束；附近有英雄时蓄满（更远更痛），只打小兵时快速蓄力 | `q_charge` · `q_charge_s` · `q_fire` · `q_beam` · `q_beam_s` · `q_hit` |")
    a("| 技能 2 = E「冲击法球」→ W「毁灭之眼」 | 先甩出冲击法球眩晕第一个敌人（越远晕越久），随后毁灭之眼在敌方英雄脚下亮起法阵、光柱落下（中心加伤、强减速） | `e_cast` · `e_orb` · `e_hit` · `e_stun` · `w_mark` · `w_blast` · `w_hit` · `w_slow` |")
    a("| 大招 = R「奥术仪式」 | 站定飞升引导，向远处的敌方英雄连发 4 发炮击：先出预警圈，0.6 秒后光弹从天而降爆炸 | `r_rise` · `r_chan` · `r_cast_shot` · `r_mark` · `r_bolt` · `r_hit` · `r_end` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、光束、闪电、符文、烟、火花没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的石甲碎片有 1 格深色描边（`#0A0A12`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("奥术青蓝（法球、光束、电光、光柱、炮击、命中）", ARC), ("深蓝紫（法阵、符文、地面焦痕、烟）", DEEP)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。")
    a("- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：W 的外圈半径 26000、中心 11000，R 每发的爆炸半径 18000，Q 光束宽 7000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `xerath_fx_{name}.png`：{title}\n")
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
        a(f"| `xerath_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `w_mark`、`r_mark`、`r_chan`、`w_slow` 的 z 是 -1（人物下面），`e_stun` 画在头顶；`w_blast`、`r_bolt` 竖直、不转（ViewEffect 打在落点上）。")
    a("- 施法者身上的画面按 `design/xerath_shots.png` 的十字把起点挪过去；晚于第一 tick 播放的（`a_flash`、`p_surge`、`q_fire`、`e_cast`、`r_cast_shot`、`r_end`）`is_follow` 为 false（红方方向）。`q_charge`、`r_rise` 在动作第一 tick 播放，跟随。")
    a("- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，石甲碎片保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；光束上下对称；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="xerath_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Xerath's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "xerath_design.png"))
    shape = size_sheet(os.path.join(out, "design", "xerath_size.png"))
    shots_sheet(os.path.join(out, "design", "xerath_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"xerath_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
    if not a.no_zip:
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
