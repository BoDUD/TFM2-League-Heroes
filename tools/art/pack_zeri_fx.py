#!/usr/bin/env python3
"""Build zeri_fx_pack.zip: step 3 of Zeri's sprite - Codex draws her effects (after tools/art/pack_syndra_fx.py).

    python tools/art/pack_zeri_fx.py [--no-zip] [--out DIR] [--only a_burst,a_hit --name zeri_fx_redo_pack]

The pack (%TEMP%/zr_work/fx/zeri_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/zeri/PROMPTS_FX.md), design/zeri_design.png (8x), design/zeri_size.png (the design at 4x on the arena
colour with the feet line, a 10-px ruler and the base fighter beside her), design/zeri_shots.png (the finished release
frames at 4x from league/champions/league_zeri, with the point each picture starts from) and refs/lol_fx_ref.png
(League's own particle textures for Zeri, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/zr_work/fxref, extracted from Zeri.wad.client by %TEMP%/zr_work/fx/fx_ref_zr.py).
The effects are the views the kit binds (tools/kit/build_zeri.py: view_projectiles a_burst, e_shot, r_shot, p_spark,
w_pulse, w_laser and the add-on's w_wall; view_effects a_hit, p_hit, p_ready, w_cast, w_hit, e_cast, e_hit, r_nova,
r_hit, r_zap; view_buffs p_slow, w_slow, p_shv, p_haste, e_on, r_on, r_st2). League's colours: her electricity is a
bright lime-yellow with white cores and cyan edges (W's beam runs from yellow to cyan), R's nova and overcharge add a
chromatic rainbow fringe. Light gets no outline. Red side: the flying rounds, pulses and sparks symmetric top to bottom,
the laser's line picture drawn in the right half of the cell from its centre (its view sits on the point the pulse
stopped on, turned from her to it) and symmetric top to bottom, every picture on a unit, the buffs and what plays on
her (p_ready, w_cast, e_cast, r_nova, the overcharge) symmetric left to right, the ground nova both ways. Codex also
delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "zr_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "zeri", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "zeri_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ZAP = "#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C"        # her electricity: lime-yellow, white core
CYAN = "#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8"                 # the edges, W's beam end, E's streaks
RAINBOW = "#FF8CF0, #B080FF, #FFB040"                                # R's chromatic fringe (a few squares only)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades "
        "and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
ZP = f"a lime electricity ramp ({ZAP})"
CY = f"a cyan ramp ({CYAN})"
RB = f"a rainbow fringe ({RAINBOW}, only as thin edges)"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame"
FIGURE = "the figure's place in the middle (14 x 36 squares, its bottom on the cell's bottom) EMPTY"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack: Q Burst Fire
    ("a_burst", "普攻 电火迸射：一串 7 发的连射弹（飞行中，循环），4 帧",
     "view_projectiles `league_zeri_a_burst`（直线弹，朝飞行方向转，画成朝右飞；上下对称）", "18 × 3",
     "泽丽的普攻是一串连发的电弹：画成一行 4–5 颗短短的黄绿色电弹（每颗 2–3 格长，白芯、柠檬黄光），前后排成一条约 18 格长的虚线，最前面一颗最亮（参考 Q_MissileHead01、Bullet_Front、Q_Electricity02）。"
     "朝右飞。**上下对称**。4 帧无缝循环（虚线往前挪一格、电光闪动）。约 18 格长、3 格高。",
     f"{ZP} and {CY}",
     f"a BURST OF ELECTRIC ROUNDS flying to the RIGHT, 4 frames, a seamless loop, {TB}: five short slugs in one row, each "
     "3 squares long and 1-2 tall (a white core, a lime-yellow glow, a faint cyan tip), spaced 1 square apart, 18 "
     "squares from the first to the last; the front slug the brightest; the row shifts forward one square each frame.",
     row(4, 20, 5) + "; the front slug 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_zeri_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "电弹打中：一小团黄绿色的电火花炸开，几根短短的电光往外跳（参考 Q_HitCircle、Hit01_vertical）。**左右对称**。约 10 格，居中画。",
     f"{ZP} and {CY}",
     f"a SMALL ELECTRIC HIT, 4 frames, {LR}: 1 a white-yellow flash 4 squares across; 2 a lime burst 8 squares across "
     "with short zigzag sparks at mirrored places; 3 the sparks flying out, cyan tips; 4 a few fading sparks.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- the passive: Living Battery
    ("p_spark", "被动 内能迁转：充满电后的电击弹（追踪，飞行中，循环），4 帧",
     "view_projectiles `league_zeri_p_spark`（追踪弹，朝飞行方向转；上下对称）", "12 × 9",
     "充满电的那一发：一颗噼啪作响的电球（白芯、柠檬黄、外圈青色电弧），后面拖一小段锯齿状的电光尾（参考 Q_MissileHead01、W_electricity02、Flare）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、9 格高。",
     f"{ZP} and {CY}",
     f"a CHARGED ELECTRIC SPARK flying to the RIGHT, 4 frames, a seamless loop, {TB}: a crackling ball 6 squares across "
     "at the right (a white core, lime-yellow, a ring of short cyan arcs), a jagged lightning tail 6 squares long behind "
     "it; the arcs jump round the ball frame to frame (keep each frame mirrored top to bottom).",
     row(4, 14, 11) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("p_hit", "电击弹打中（目标身上），5 帧", "view_effects `league_zeri_p_hit`（跟随；左右对称）", "16",
     "电击弹打中：一团更大的电爆，中心白光，外面一圈黄绿色的电弧，几道青色的电光往外劈（参考 Hit02_vertical、Q_HitCircle、W_Flash01）。**左右对称**。约 16 格，居中画。",
     f"{ZP} and {CY}",
     f"a CHARGED ELECTRIC BLAST, 5 frames, {LR}: 1 a white flash 6 squares across; 2 a lime-yellow burst 12 squares "
     "across with a white core; 3 zigzag lightning bolts out to mirrored places, cyan edges, 16 squares across; 4 the "
     "bolts breaking into sparks; 5 fading sparks.",
     row(5, 18, 18) + "; centered in every cell."),
    ("p_ready", "电量充满（她身上，充满的一刻），6 帧",
     "view_effects `league_zeri_p_ready`（跟随她，画在人物上面；左右对称；中间留空）", "30 × 42",
     "电池充满：她身边噼啪闪过一圈电光（从脚下往上窜到头顶），最后头顶上方一下亮光（参考 Flare、W_electricity02_Vertical、Glow06）。"
     "**中间人站的位置留空**，**左右对称**（逐格对称）。约 30 格宽、42 格高。",
     f"{ZP} and {CY}",
     f"a FULL CHARGE CRACKLE round a figure, 6 frames, {LR}, {FIGURE}: 1 two short lime arcs at the feet on both sides; "
     "2 the arcs climbing to the hips, small white sparks; 3 the arcs at the chest, cyan edges; 4 the arcs at the head, "
     "brightest; 5 a white-yellow star 6 squares across above the head, the arcs fading; 6 a few fading sparks.",
     row(6, 32, 44) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("p_shv", "护盾（她身上，持续 3 秒，循环），4 帧",
     "view_buffs `league_zeri_p_shv`（画在人物上面；左右对称；只画外圈，中间留空）", "30 × 44",
     "电击弹命中英雄后的护盾（装附加包时是偷来的盾）：围着她一圈椭圆形的电光护罩，只画外圈（柠檬黄的边、几处青色的电弧沿着边流动），里面空着让人能看见（参考 W_Shield、P_Shield_Reveal、EdgeGlow）。"
     "**左右对称**。4 帧无缝循环。约 30 格宽、44 格高。",
     f"{ZP} and {CY}",
     f"an ELECTRIC SHIELD round a figure, 4 frames, a seamless loop, {LR}, the inside EMPTY: an upright oval ring 28 "
     "squares wide and 42 tall, 1-2 squares thick, lime-yellow with a white highlight at the top, a few short cyan arcs "
     "running along the ring at mirrored places (they step round the ring each frame).",
     row(4, 32, 46) + "; centered across, the oval's bottom 1 square above the cell's bottom."),
    ("p_slow", "电击弹的减速（被减速的人脚下，循环），4 帧", "view_buffs `league_zeri_p_slow`（画在脚下；左右对称）", "14 × 5",
     "被电击弹减速：脚下一圈细细的黄绿色电环，环上有几个跳动的电火花（左右对称）。**左右对称**。4 帧无缝循环。",
     f"{ZP}",
     f"an ELECTRIC SLOW RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin lime ellipse 12 squares wide "
     "and 3 tall, small white-yellow sparks on it at mirrored places that flicker.",
     row(4, 16, 7) + "; centered in every cell."),
    ("p_haste", "被动的加速（她脚下，1.5 秒，循环），4 帧", "view_buffs `league_zeri_p_haste`（画在脚下；左右对称）", "18 × 6",
     "命中英雄后的加速：她脚边两侧几道短短的青色速度线和电火花（左右对称）（参考 W_Speedline、ZoomLines）。**左右对称**。4 帧无缝循环。",
     f"{CY} and {ZP}",
     f"SPEED STREAKS at a figure's feet, 4 frames, a seamless loop, {LR}: on each side of the feet two short cyan "
     "streaks 3-4 squares long and a small lime spark, mirrored; they flicker and shift one square up or down.",
     row(4, 20, 8) + "; centered in every cell."),
    # ---- W Ultrashock Laser
    ("w_cast", "W 强穿激光：蓄力（她身上，施法时），5 帧",
     "view_effects `league_zeri_w_cast`（施法时跟随她，画在人物上面；左右对称；中间留空）", "30 × 40",
     "W 蓄力：她身边几道电弧往中间收、越来越亮，然后一下闪光（参考 W_Wirlpool01、W_electricity02、W_Flash01）。"
     "**中间人站的位置留空**，**左右对称**。约 30 格宽、40 格高。",
     f"{ZP} and {CY}",
     f"a CHARGING SURGE round a figure, 5 frames, {LR}, {FIGURE}: 1 four faint lime arcs at the corners; 2 the arcs "
     "curving inward toward the chest, brighter; 3 the arcs close to the figure, white sparks; 4 a bright yellow-white "
     "ring 20 squares wide and 6 tall at chest height (only its left and right ends show beside the figure); 5 fading.",
     row(5, 32, 42) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("w_pulse", "W 射出的电脉冲（飞行中，循环），4 帧",
     "view_projectiles `league_zeri_w_pulse`（直线弹，朝飞行方向转；上下对称）", "16 × 7",
     "W 的电脉冲：一道又亮又长的电弹（白芯、柠檬黄、尾巴渐变成青色），前端尖、后面一条细的光尾（参考 W_mis_glowTrail、W_Trail03、W_color）。朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、7 格高。",
     f"{ZP} and {CY}",
     f"an ELECTRIC PULSE flying to the RIGHT, 4 frames, a seamless loop, {TB}: a pointed bolt 7 squares long and 5 tall "
     "at the right (a white core, lime-yellow body), a tapering trail 9 squares long behind it that turns from yellow "
     "to cyan, small arcs flickering along it.",
     row(4, 18, 9) + "; the bolt's tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_laser", "W 打中小兵后化成的长激光（地上的线，朝方向转），6 帧",
     "view_projectiles `league_zeri_w_laser`（线的画面：以脉冲停下的点为中心、朝泽丽→那一点的方向转；**画在格子右半边**；上下对称）",
     "200 × 13",
     "W 打中小兵或野怪后，从那里往外射出一道 100 格长的激光：白色的芯、柠檬黄的光、边上青色，越往外越变青（参考 W_color、W_BeamGrad、W_electricity02）。光束从起点往右「射」出去，第 2 帧射满，然后变细、碎成电火花。"
     "**整张图左半边是空的**（游戏把这张图的中心放在脉冲停下的点上，往外射）。**上下对称**。光束约 7 格高，起点处一团闪光。",
     f"{ZP} and {CY}",
     f"a LASER BEAM shooting to the RIGHT from the cell's CENTER, 6 frames, {TB}: the LEFT HALF of every cell stays EMPTY; "
     "the beam starts exactly at the cell's center: a white core 3 squares tall, lime-yellow round it, cyan edges, 7 "
     "squares tall, its color turning from yellow at the start to cyan at the far end, a bright white-yellow flash 9 "
     "squares across at the start; 1 the beam 40 squares long; 2 the full 100 squares, brightest; 3 the full beam; 4 the "
     "beam thinner (3 tall); 5 breaking into sparks along the line; 6 fading sparks.",
     row(6, 204, 15) + "; the beam's start on the cell's exact center column, vertically centered."),
    ("w_wall", "（附加包）W 撞墙后的长激光（飞行中，循环），4 帧",
     "view_projectiles `league_zeri_w_wall`（附加包生成的直线弹，朝飞行方向转；上下对称）", "40 × 9",
     "装了附加包时，W 打到墙后变成一道飞出去的长激光：一段很长的光束（白芯、柠檬黄、青色的边），前端最亮、后面渐渐淡成青色（参考 W_color、W_mis_glowTrail02）。朝右飞。**上下对称**。4 帧无缝循环。约 40 格长、9 格高。",
     f"{ZP} and {CY}",
     f"a FLYING LASER SEGMENT to the RIGHT, 4 frames, a seamless loop, {TB}: a beam 40 squares long and 7 tall (a white "
     "core 3 tall, lime-yellow, cyan edges), its front a bright rounded head, fading to cyan toward its tail; small "
     "arcs flicker along it.",
     row(4, 42, 11) + "; the beam's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_hit", "W 打中（目标身上），4 帧", "view_effects `league_zeri_w_hit`（跟随；左右对称）", "14",
     "W 打中：一团黄绿到青色的电爆，几道电弧往外劈（参考 W_Flash01、W_tar_Sphere）。**左右对称**。约 14 格，居中画。",
     f"{ZP} and {CY}",
     f"a LASER HIT, 4 frames, {LR}: 1 a white flash 6 squares across; 2 a lime-yellow burst 10 squares across with a "
     "cyan rim; 3 zigzag arcs out to mirrored places; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("w_slow", "W 的减速（被减速的人脚下，循环），4 帧", "view_buffs `league_zeri_w_slow`（画在脚下；左右对称）", "16 × 6",
     "被 W 减速：脚下一圈青色的电环，环上几道往中间收的短电弧（左右对称）。**左右对称**。4 帧无缝循环。",
     f"{CY} and {ZP}",
     f"a CYAN SLOW RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin cyan ellipse 14 squares wide and 4 "
     "tall, four short lime arcs at mirrored places that slide toward the center each frame.",
     row(4, 18, 8) + "; centered in every cell."),
    # ---- E Spark Surge
    ("e_cast", "E 灿丽花火：冲刺起步的电光（她脚下，施法时），5 帧",
     "view_effects `league_zeri_e_cast`（跟随她，画在人物下面；左右对称）", "44 × 18",
     "E 冲刺起步：脚下一圈电光炸开，两边各几道青色和黄绿色的速度线、电火花往外甩（参考 E_Dash、E_Lightning_flipbook、W_Speedline）。**左右对称**。约 44 格宽、18 格高。",
     f"{ZP} and {CY}",
     f"a DASH BURST on the ground round a figure's feet, 5 frames, {LR}: 1 a white-yellow flash 10 squares wide at the "
     "feet; 2 a lime ring 24 squares wide and 8 tall with cyan streaks out to both sides; 3 the ring 36 wide, zigzag "
     "sparks thrown out at mirrored places; 4 the ring 44 wide and 16 tall, thinner; 5 fading sparks.",
     row(5, 46, 20) + "; centered in every cell."),
    ("e_on", "E 生效中：步枪带电（她身上，持续 5 秒，循环），4 帧",
     "view_buffs `league_zeri_e_on`（画在人物上面；左右对称；中间留空）", "28 × 40",
     "E 之后的 5 秒普攻贯穿：她身边两侧噼啪闪着小电弧（左右对称地分布在肩、腰、膝旁边），中间留空（参考 E_Lightning_flipbook、R_Electricity_4x4）。**左右对称**。4 帧无缝循环。约 28 格宽、40 格高。",
     f"{ZP} and {CY}",
     f"CRACKLING ARCS round a figure, 4 frames, a seamless loop, {LR}, {FIGURE}: short lime zigzag arcs 3-4 squares long "
     "beside the shoulders, the waist and the knees on both sides, cyan tips, small white sparks; each frame the arcs "
     "jump to the next place (keep each frame mirrored).",
     row(4, 30, 42) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("e_shot", "E 生效时的贯穿弹（飞行中，循环），4 帧",
     "view_projectiles `league_zeri_e_shot`（直线弹，朝飞行方向转；上下对称）", "18 × 4",
     "E 的贯穿弹：一道细长锋利的电弹（白芯、青色），后面拖一条长的黄绿色光尾，前端一个小尖（参考 ER_MissileHead、Bullet_Front）。朝右飞。**上下对称**。4 帧无缝循环。约 18 格长、4 格高。",
     f"{CY} and {ZP}",
     f"a PIERCING ROUND flying to the RIGHT, 4 frames, a seamless loop, {TB}: a sharp slug 5 squares long and 2 tall at "
     "the right (a white core, cyan edges), a thin lime trail 13 squares long behind it, a tiny white tip; the trail "
     "flickers.",
     row(4, 20, 6) + "; the tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_hit", "贯穿弹打中（目标身上），4 帧", "view_effects `league_zeri_e_hit`（跟随；左右对称）", "10",
     "贯穿弹打中：一小团青色带黄绿芯的电火花，几根细电光往两边跳（左右对称）。**左右对称**。约 10 格，居中画。",
     f"{CY} and {ZP}",
     f"a PIERCE HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a cyan burst 8 squares across with a lime core; "
     "3 thin sparks out to both sides; 4 fading sparks.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- R Lightning Crash
    ("r_nova", "R 超限爆闪：以她为中心的电新星（地上，施法时），6 帧",
     "view_effects `league_zeri_r_nova`（跟随她，画在人物下面；上下左右都对称）", "150 × 60",
     "R：以她为中心炸开一圈巨大的电新星：一圈黄绿色的电光环从脚下往外扩到 150 格宽，环上有锯齿状的电弧和一点彩虹色的边，中心一下白光（参考 Shockwave01_Color、R_RainbowGlow、R_Electricity_4x4、R_Ray）。"
     "这是技能的范围（半径 75 格），从斜上方看的扁椭圆。**上下左右都对称**。约 150 格宽、60 格高。",
     f"{ZP}, {CY} and {RB}",
     f"a HUGE LIGHTNING NOVA on the ground round a figure, seen from above at an angle, 6 frames, {BOTH}: 1 a white-yellow "
     "flash 20 squares wide at the center; 2 a bright lime ring 60 squares wide and 24 tall with jagged arcs on it; 3 "
     "the ring 100 wide, cyan edges, a thin rainbow fringe outside; 4 the ring 140 wide; 5 the ring 150 wide and 60 "
     "tall, thinner, arcs flickering on it; 6 fading sparks along the ellipse.",
     row(6, 152, 62) + "; centered in every cell."),
    ("r_on", "R 超载中（她身上，持续 5 秒，循环），4 帧",
     "view_buffs `league_zeri_r_on`（画在人物上面；左右对称；中间留空）", "34 × 48",
     "超载 5 秒：她全身绕着明亮的电光（左右两侧各几道长的锯齿电弧从脚到头，外面一点彩虹色的边），头顶偶尔一下亮光，中间留空（参考 R_Electricity_4x4、R_ChainLightning01、R_RainbowGlow）。"
     "**左右对称**。4 帧无缝循环。约 34 格宽、48 格高。",
     f"{ZP}, {CY} and {RB}",
     f"an OVERCHARGE AURA round a figure, 4 frames, a seamless loop, {LR}, {FIGURE}: on each side two long jagged "
     "lightning arcs from the feet to above the head (lime-yellow, white cores, cyan edges, a thin rainbow fringe), "
     "small sparks; the arcs change shape every frame (keep each frame mirrored); frame 3 a small white star above the "
     "head.",
     row(4, 36, 50) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("r_st2", "R 超载被延长（她身上，循环），4 帧",
     "view_buffs `league_zeri_r_st2`（画在人物上面；左右对称；中间留空）", "34 × 48",
     "超载被命中英雄延长时：和超载一样的电光，但弱一些（两侧各一道电弧、没有头顶的亮光），表示快结束了。**左右对称**。4 帧无缝循环。约 34 格宽、48 格高。",
     f"{ZP} and {CY}",
     f"a FADING OVERCHARGE round a figure, 4 frames, a seamless loop, {LR}, {FIGURE}: on each side one jagged lightning "
     "arc from the hip to the shoulder (lime-yellow, white core, cyan edges), dimmer than a full aura, a few sparks; "
     "the arcs change shape every frame (keep each frame mirrored).",
     row(4, 36, 50) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("r_shot", "R 超载时的三连发（飞行中，循环），4 帧",
     "view_projectiles `league_zeri_r_shot`（直线弹，朝飞行方向转；上下对称）", "18 × 9",
     "超载时普攻变成三连发：三道平行的电弹线（中间一道最亮最长，上下两道短一点），白芯、柠檬黄、青色的尖（参考 R_MissileHead01、Q_MissileHead01）。朝右飞。**上下对称**。4 帧无缝循环。约 18 格长、9 格高。",
     f"{ZP} and {CY}",
     f"THREE PARALLEL ELECTRIC ROUNDS flying to the RIGHT, 4 frames, a seamless loop, {TB}: a middle round 16 squares "
     "long and 2 tall (a white core, lime-yellow, a cyan tip) and two rounds 12 long and 1-2 tall 3 squares above and "
     "below it, mirrored; small sparks between them flicker.",
     row(4, 20, 11) + "; the middle round's tip 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_hit", "R 电新星打中（目标身上），5 帧", "view_effects `league_zeri_r_hit`（跟随；左右对称）", "16",
     "电新星打中：一团明亮的电爆（白芯、柠檬黄、青色的边、一点彩虹色），几道锯齿电弧往外劈（参考 Hit02_vertical、R_RainbowGlow）。**左右对称**。约 16 格，居中画。",
     f"{ZP}, {CY} and {RB}",
     f"a NOVA HIT, 5 frames, {LR}: 1 a white flash 6 squares across; 2 a lime-yellow burst 12 squares across with cyan "
     "edges; 3 jagged bolts to mirrored places, a thin rainbow fringe; 4 sparks; 5 fading sparks.",
     row(5, 18, 18) + "; centered in every cell."),
    ("r_zap", "R 连锁闪电打中（每个被连锁的人身上），4 帧",
     "view_effects `league_zeri_r_zap`（跟随；左右对称）", "14 × 30",
     "三连发打中后的连锁闪电：一道闪电从上方劈到这个人身上（两股对称的锯齿电光从格子顶部往下汇到身体中间），落点一下电火花（参考 R_ChainLightning01、Hit01_vertical）。**左右对称**。约 14 格宽、30 格高。",
     f"{ZP} and {CY}",
     f"a CHAIN LIGHTNING STRIKE on a figure, 4 frames, {LR}: 1 two mirrored zigzag bolts from the cell's top corners "
     "meeting at the cell's middle (white cores, lime-yellow, cyan edges); 2 the bolts brightest, a white-yellow burst "
     "6 squares across where they meet; 3 the bolts breaking up, sparks; 4 fading sparks at the middle.",
     row(4, 16, 32) + "; centered across, the meeting point on the cell's middle."),
]

GROUPS = [
    ("attack", ["Zeri_Base_Q_MissileHead01", "Zeri_Base_Bullet_Front_LessBlur", "Zeri_Base_Q_MuzzleFlash03_Core",
                "Zeri_Base_Q_MuzzleFlash_Small", "Zeri_Base_Q_HitCircle", "Zeri_Base_Q_Electricity02"]),
    ("passive", ["Zeri_Base_W_Shield", "Zeri_P_Shield_Reveal", "Zeri_Base_EdgeGlow", "Zeri_Base_Flare",
                 "Zeri_Base_Hit01_vertical", "Zeri_Base_Hit02_vertical"]),
    ("W", ["Zeri_Base_W_color", "Zeri_Base_W_electricity02", "Zeri_Base_W_mis_glowTrail", "Zeri_Base_W_Trail03",
           "Zeri_Base_W_Flash01", "Zeri_Base_W_BeamGrad"]),
    ("E", ["Zeri_Base_E_Dash", "Zeri_Base_E_Lightning_flipbook", "Zeri_Base_ER_MissileHead", "Zeri_Base_W_Speedline",
           "Zeri_Base_E_Shell_RGB", "Zeri_Base_W_Wirlpool01"]),
    ("R", ["Zeri_Base_R_ChainLightning01", "Zeri_Base_R_Electricity_4x4", "Zeri_Base_R_RainbowGlow",
           "Zeri_Base_R_MissileHead01", "Zeri_Base_Shockwave01_Color", "Zeri_Base_R_Ray"]),
]
# where the pictures start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point, dy from the soles]);
# measured on the imported release frames (the rifle's electrodes: attack 3, W 4, R 3)
SHOTS = [("attack", 3, "a_burst / p_spark / e_shot / r_shot：枪口（子弹从这里飞出）", [(26, -18)]),
         ("skill", 4, "w_pulse：枪口（电脉冲从这里飞出）", [(25, -17)]),
         ("ult", 3, "r_nova：站位点（新星以她为中心）", "feet"),
         ("skill2", 1, "e_cast：站位点（冲刺起步）", "feet"),
         ("idle", 1, "p_ready / w_cast / 护盾 / 超载：站位点", "feet")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Zeri_Base_", "").replace("Zeri_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    a = a[4::8, 4::8] if a.shape[0] == 1024 else a
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
    d.text((8, 36), f"泽丽 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (league/champions/league_zeri, the imported sheet), each picture's starting
    point as a cyan cross (the standing point is the frame's pivot: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_zeri"))
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    PAD = 8
    px = sp.w // 2 + PAD
    for tag, k, what, marks in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
        ys, xs = np.nonzero(f[..., 3] > 0)
        soles = int(ys.max())
        pts = [(px, soles + 1)] if marks == "feet" else [(px + dx, soles + 1 + dy) for dx, dy in marks]
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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
    a("# 祖安花火 泽丽：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/zeri_design.png`，8 倍，{h} 行、{w} 格宽）。")
    a(f"> - 大小对照 `design/zeri_size.png`：定稿造型放大 4 倍，鞋底在红线上，上面是 10 格一段的刻度，右边是原版斗士。泽丽 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/zeri_shots.png`：定稿动作的出手帧（4 倍），青色十字是特效的起点（平端的步枪枪口、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里泽丽自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**她的电是明亮的柠檬黄绿色、白色的芯、青色的边；W 的激光从黄色渐变到青色；R 的新星和超载外面带一点彩虹色的边**。")
    a("> - **特效要亮**：每个电光、光束、火花都用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的电光（充满电、蓄力、护盾、E 生效、超载）只画外圈和两边，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的电弹、脉冲、电击弹、三连发、附加包的激光段（`a_burst`、`p_spark`、`w_pulse`、`w_wall`、`e_shot`、`r_shot`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "长激光 `w_laser` 是**线的画面**：游戏把整张图的**中心**放在脉冲停下的点上、朝「泽丽→那一点」的方向转，所以**激光只画在格子右半边、从正中间往右射**，同样**上下对称**。"
      "画在人身上、脚下的（打中、减速、加速、护盾、充满电、蓄力、冲刺电光、E 生效、超载、连锁闪电）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；"
      "地上的电新星 `r_nova` 上下左右都对称。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `zeri_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`zeri_fx_done.zip`）放在 outputs 里，或放在 `outputs/zeri-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 = Q「电火迸射」 | 一串 7 发的连射，打第一个挡路的敌人 | `a_burst` · `a_hit` |")
    a("| 被动「内能迁转」 | 普攻充电，充满后下一发变成追踪的电击弹（魔法伤害 + 减速，命中英雄得护盾和加速） | `p_ready` · `p_spark` · `p_hit` · `p_slow` · `p_shv` · `p_haste` |")
    a("| 技能 1 = W「强穿激光」 | 射出电脉冲打第一个敌人（伤害 + 减速）；先打中小兵或野怪时从那里化成一道长激光（附加包：打到墙也会） | `w_cast` · `w_pulse` · `w_laser` · `w_wall` · `w_hit` · `w_slow` |")
    a("| 技能 2 = E「灿丽花火」 | 按局势冲刺，之后 5 秒普攻贯穿并附带魔法伤害 | `e_cast` · `e_on` · `e_shot` · `e_hit` |")
    a("| 大招 = R「超限爆闪」 | 以她为中心的电新星，然后超载：攻速、移速，普攻变三连发并在敌人间连锁闪电 | `r_nova` · `r_hit` · `r_on` · `r_st2` · `r_shot` · `r_zap` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**电光、光束、火花、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只做很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("柠檬黄绿的电（子弹、电弧、新星、护盾）", ZAP), ("青色（边、W 激光的尾端、E 的贯穿弹、速度线）", CYAN),
                        ("彩虹色的边（只在 R 的新星、超载、打中上细细一圈）", RAINBOW)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 60000，"
      "W 激光长 100000、宽 9000，E 冲刺 30000，R 新星半径 75000，连锁闪电半径 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `zeri_fx_{name}.png`：{title}\n")
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
        a(f"| `zeri_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 子弹、电击弹、贯穿弹、三连发、电脉冲从平端步枪的枪口出（出手帧枪口在站位点前 25–26 格、脚底上 17–18 格）；`a_y` 按这个量（太高的直线弹会斜：最多抬到 13 格左右），画面开头补空帧走过枪口前的距离（追踪弹第一 tick 朝上）。")
    a("- `w_laser`：线的画面在脉冲停下的点、朝泽丽→那一点转（champion-data section 6）；按 204 格宽切格，确认左半边是空的、上下对称。`w_wall` 是附加包生成的直线弹（league_zeri:laser 效果），朝飞行方向转。")
    a("- `r_nova`：R 的出手 tick 跟随她播放（画在人物下面，z -1），上下左右逐格对称；`p_ready`、`w_cast`、`e_cast` 也跟随她、逐格左右对称；`e_on` 300 tick、`r_on` 300 tick、`r_st2` 最多 150 tick、`p_shv` 180 tick 循环。")
    a("- 用 `pixel_1x/` 切格（import_syndra 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="zeri_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Zeri's particle textures first (fx_ref_zr.py)")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    d = d if d.shape[0] == 1024 else np.repeat(np.repeat(d, 8, 0), 8, 1)
    Image.fromarray(d).save(os.path.join(out, "design", "zeri_design.png"))
    shape = size_sheet(os.path.join(out, "design", "zeri_size.png"))
    shots_sheet(os.path.join(out, "design", "zeri_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"zeri_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
