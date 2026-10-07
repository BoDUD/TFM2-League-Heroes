#!/usr/bin/env python3
"""Build viktor_fx_pack.zip: step 3 of Viktor's sprite - Codex draws his effects (after tools/art/pack_seraphine_fx.py).

    python tools/art/pack_viktor_fx.py [--no-zip] [--out DIR] [--only a_bolt,a_hit --name viktor_fx_redo_pack]

The pack (%TEMP%/vk_work/fx/viktor_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/viktor/PROMPTS_FX.md), design/viktor_design.png (8x), design/viktor_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside him), design/viktor_shots.png (the finished
action frames at 4x from league/champions/league_viktor, with the point each picture starts from) and refs/lol_fx_ref.png
(League's own particle textures for Viktor, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/vk_work/fxref, extracted from Viktor.wad.client).
The effects are the views the kit binds (tools/kit/build_viktor.py: view_projectiles a_bolt, a_blast, q_bolt, e_ray,
e_after; view_effects a_hit, a_blast_hit, q_hit, q_shield, w_field, w_burst, w_stun, e_hit, e_after_hit, r_land, r_storm,
r_storm_big, r_hit, evo; view_buffs w_slow, evo_slow, q_buff (tag q_charged), q_ms). League's colours: arcane violet (the
claw, the field, the storm), hextech gold-orange with white cores (Q, the ray), cyan (the claw's core, Q's shield).
Light gets no outline. Red side: the bolts symmetric top to bottom, the ray's line pictures drawn in the right half of
the cell from its centre (the view sits on the landing point, turned from him to it) and symmetric top to bottom, every
picture on a unit and every buff symmetric left to right, the ground pictures both ways. Codex also delivers pixel_1x/
game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "vk_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "viktor", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "viktor_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VIOLET = "#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8"            # arcane light: the claw, the field, the storm
CYAN = "#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8"              # the claw's hextech core, Q's shield
GOLD = "#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C"              # hextech gold-orange: Q, the ray
STORM = "#FFFFFF, #D8D0FF, #8C7CF0, #4A3CB0, #241A60"             # the storm's darker swirl (dark shades sparingly)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a "
        "white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VI = f"an arcane violet ramp ({VIOLET})"
CY = f"a hextech cyan ramp ({CYAN})"
GD = f"a hextech gold ramp ({GOLD})"
ST = f"a storm violet ramp ({STORM})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and Q's charge
    ("a_bolt", "普攻：飞出去的奥术光弹（飞行中，循环），4 帧",
     "view_projectiles `league_viktor_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "8 × 5",
     "维克托的普攻：一颗蓝紫色的小光弹，前面一颗白芯，后面拖一小段蓝紫光尾（参考 BA_Muzzle、BA_Trail、BA_GlowAlpha）。朝右飞。**上下对称**。4 帧无缝循环。约 8 格长、5 格高。",
     VI,
     f"an ARCANE BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white core 2 squares across at the right, "
     "a violet glow round it, a short tapering violet trail 5 squares long behind it to the left; the trail flickers "
     "frame to frame.",
     row(4, 10, 6) + "; the bolt's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_blast", "Q 强化后的普攻：更大的金色海克斯光弹（飞行中，循环），4 帧",
     "view_projectiles `league_viktor_a_blast`（同上；上下对称）", "12 × 8",
     "虹吸能量强化的下一次普攻：一颗更大的金白色光弹，外面一圈细的青色电弧，后面拖金色光尾（参考 Q_Sphere、Q_mis_glowTrail02、Q_ElecAnim）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、8 格高。",
     f"{GD} and {CY}",
     f"a CHARGED HEXTECH BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a bright white-gold orb 4 squares "
     "across at the right, a thin cyan electric arc crackling round it, a gold trail 6 squares long behind it; the arcs "
     "jump to mirrored places each frame.",
     row(4, 14, 10) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_viktor_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "普攻打中：一朵蓝紫色的小星光炸开（参考 Flash、Hit_Spark_blue）。**左右对称**。约 10 格，居中画。",
     VI,
     f"an ARCANE SPARK HIT, 4 frames, {LR}: 1 a white-violet 4-point star 5 squares across; 2 a violet burst 7 squares "
     "across; 3 four sparks flying out diagonally; 4 a few fading sparks.",
     row(4, 12, 12) + "; centered in every cell."),
    ("a_blast_hit", "强化普攻打中，5 帧", "view_effects `league_viktor_a_blast_hit`（跟随；左右对称）", "16",
     "强化普攻打中：一团金白色的海克斯光炸开，一圈青色电弧往外扩（参考 Q_Buf_Hit_Burst、Q_Impact_Cross）。**左右对称**。约 16 格，居中画。",
     f"{GD} and {CY}",
     f"a HEXTECH BURST, 5 frames, {LR}: 1 a white-gold flash 8 squares across; 2 a gold cross-shaped burst 12 squares "
     "across; 3 a thin cyan ring 14 squares across with small electric arcs; 4 the ring wider and fading, sparks; 5 a "
     "few fading sparks.",
     row(5, 18, 18) + "; centered in every cell."),
    ("q_bolt", "Q 虹吸能量：法杖射出的海克斯光弹（飞行中，循环），4 帧",
     "view_projectiles `league_viktor_q_bolt`（朝飞行方向转；上下对称）", "12 × 8",
     "Q 的光弹：一颗金白色的海克斯光球，外面一圈青色的六边形光环，后面拖一道金色光尾（参考 Q_Missile_Head、Q_HextechRing04、Q_mis_glowTrail02）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、8 格高。",
     f"{GD} and {CY}",
     f"a HEXTECH MISSILE flying to the RIGHT, 4 frames, a seamless loop, {TB}: a bright white-gold orb 4 squares across "
     "inside a thin cyan hexagon ring 7 squares across, a gold trail 6 squares long behind it; the ring brightens and dims "
     "frame to frame (no spinning).",
     row(4, 14, 10) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_hit", "Q 打中（目标身上），4 帧", "view_effects `league_viktor_q_hit`（跟随；左右对称）", "14",
     "Q 打中：金白色的星光炸开，一圈六边形的青色光环往外扩（参考 Q_Ring、Q_Flares_03）。**左右对称**。约 14 格，居中画。",
     f"{GD} and {CY}",
     f"a HEXTECH HIT, 4 frames, {LR}: 1 a white-gold star 7 squares across; 2 a gold burst 10 squares across inside a "
     "thin cyan hexagon outline 12 squares across; 3 the hexagon wider and thinner, sparks; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("q_shield", "Q 护盾：打中后他身上亮起的护盾（他身上），5 帧",
     "view_effects `league_viktor_q_shield`（施法后，不跟随，画在人物上面；左右对称）", "26 × 34",
     "Q 打中后维克托得到护盾：他身上亮起一层青白色的六边形能量泡（只画外圈，中间留空），从下往上亮起再淡下去（参考 Q_template_shield、Q_shield_Mult、Shield_gradient）。**左右对称**。约 26 格宽、34 格高。",
     CY,
     f"a HEXTECH SHIELD BUBBLE round a figure, 5 frames, {LR}, its inside EMPTY: an upright ellipse outline 24 squares "
     "wide and 32 tall made of small cyan hexagon segments, 1 the bottom third lit; 2 the whole outline lit, white "
     "highlights at the top; 3 brightest, a few hexagons flashing white; 4 dimmer; 5 fading to a few segments.",
     row(5, 28, 36) + "; the bubble centered in every cell, its bottom 1 square above the cell's bottom."),
    ("q_charged", "Q 强化普攻就绪（他身上，循环），4 帧", "view_buffs `league_viktor_q_buff`（跟随；左右对称）", "26 × 34",
     "Q 之后下一次普攻会强化：维克托身边绕着两颗金色的小光点（左右对称地上下浮动，中间留空，不挡人）（参考 idle_BightSpark、Glow5）。**左右对称**。4 帧无缝循环。",
     GD,
     f"TWO HEXTECH SPARKS floating round a figure, 4 frames, a seamless loop, {LR}, the figure's place EMPTY: two small "
     "white-gold glowing sparks (3 squares across, a 1-square white core) at mirrored places beside the figure's waist, "
     "rising and falling 2 squares together.",
     row(4, 28, 36) + "; the figure area is the middle 16 x 32 squares, its bottom on the cell's bottom."),
    ("q_ms", "Q 升级后的加速（脚下，循环），4 帧", "view_buffs `league_viktor_q_ms`（画在脚下；左右对称）", "18 × 6",
     "Q 升级后的移速：脚下一圈细的青色光环，两边各几道往后的短光线（左右对称）。**左右对称**。4 帧无缝循环。",
     CY,
     f"a SPEED RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin cyan ellipse 16 squares wide and 4 "
     "tall, 2 short horizontal light dashes on each side at mirrored places; the dashes slide outward each frame.",
     row(4, 20, 8) + "; centered in every cell."),
    # ---- W Gravity Field
    ("w_field", "W 重力场：地上的引力场（地上，画在人物下面，持续 4 秒），10 帧",
     "view_effects `league_viktor_w_field`（落点上，不旋转，画在人物下面；上下左右都对称）", "64 × 26",
     "重力场：地上一个从斜上方看的扁椭圆引力场，外圈一道蓝紫色光环，里面几圈细的同心环慢慢往中间收，中间一颗发光的小核（参考 W_Circle_normal、W_Pulses、W_TrampleAOE_Glow、W_LightBeam）。"
     "**上下左右都对称**。这是技能的范围（半径 30 格），约 64 格宽、26 格高。帧 1–2 展开，3–8 循环收缩（引力往里吸），9–10 淡出。",
     f"{VI} and {CY}",
     f"a GRAVITY FIELD on the ground seen from above at an angle, 10 frames, {BOTH}: an elliptical field 60 squares wide "
     "and 24 tall: a bright violet outer ring 2 squares thick, 3 thin inner violet rings, a small glowing white-cyan core "
     "at the center; 1-2 the field opening from the center to full size; 3-8 the inner rings stepping inward toward the "
     "core one ring per frame (a pull), the outer ring pulsing; 9-10 fading out.",
     row(10, 64, 28) + "; centered in every cell."),
    ("w_burst", "W 晕眩爆发：力场里的人被晕的那一下（地上），5 帧",
     "view_effects `league_viktor_w_burst`（落点上，不旋转，画在人物下面；上下左右都对称）", "64 × 26",
     "1.25 秒后力场爆发晕眩：整个椭圆一下子亮起，从中心往外炸开一圈亮紫白色的冲击波（参考 Shockwave_SpaceNoise、W_SetShine01）。**上下左右都对称**。约 64 格宽、26 格高。",
     f"{VI} and {CY}",
     f"a GRAVITY BURST on the ground seen from above at an angle, 5 frames, {BOTH}: 1 the whole ellipse (60 x 24 squares) "
     "flashes white-violet; 2 a bright shockwave ring 2 squares thick racing out from the center, 30 squares wide; 3 the "
     "ring 50 wide; 4 the ring 60 wide and thin; 5 fading sparks.",
     row(5, 64, 28) + "; centered in every cell."),
    ("w_stun", "W 晕眩（被晕的人头顶，循环），4 帧", "view_effects `league_viktor_w_stun`（跟随；左右对称）", "18 × 8",
     "被重力场晕住：头顶一圈扁扁的蓝紫色引力环，环上几颗小光点在转（参考 Viktor_Base_Ringlight、W_Aug_ElecNoise）。**左右对称**。约 18 格宽、8 格高。",
     VI,
     f"a GRAVITY HALO over a head, 4 frames, {LR}: a flat violet ellipse 16 squares wide and 5 tall, 4 small white-violet "
     "dots on it at mirrored places that step round the ring each frame (keep each frame mirrored), a faint glow inside.",
     row(4, 20, 10) + "; centered in every cell."),
    ("w_slow", "W 减速（被减速的人脚下，循环），4 帧", "view_buffs `league_viktor_w_slow`（画在脚下；左右对称）", "16 × 6",
     "被重力场减速：脚下一圈蓝紫色的细光环，环里有往中间收的短线（左右对称）。**左右对称**。4 帧无缝循环。",
     VI,
     f"a SLOWING RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin violet ellipse 14 squares wide and 4 "
     "tall, 4 short inward ticks at mirrored places that slide toward the center each frame.",
     row(4, 18, 8) + "; centered in every cell."),
    ("evo_slow", "进化后技能附带的减速（被减速的人脚下，循环），4 帧", "view_buffs `league_viktor_evo_slow`（画在脚下；左右对称）",
     "14 × 5",
     "升级后技能附带的减速：脚下一圈细的金色光环，两边各一个小光点（左右对称）。**左右对称**。4 帧无缝循环。",
     GD,
     f"a GOLD SLOW RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin gold ellipse 12 squares wide and 3 "
     "tall with a small white-gold spark on each side at mirrored places, brightening and dimming.",
     row(4, 16, 7) + "; centered in every cell."),
    # ---- E Hextech Ray
    ("e_ray", "E 海克斯射线：从目标处往外扫的光束（地上的线，朝方向转），6 帧",
     "view_projectiles `league_viktor_e_ray`（线的画面：以落点为中心、朝维克托→落点的方向转；**画在格子右半边**；上下对称）",
     "140 × 26",
     "海克斯射线：从落点（格子正中）往右射出一道 70 格长的光束，白色的芯、金橙色的光、边上一点蓝紫，光束从起点往右「扫」出去，第 3 帧扫满，然后淡出（参考 E_Trail_55、E_Trench、E_Flare、Beamhead_Centre）。"
     "**整张图左半边是空的**（游戏把这张图的中心放在目标脚下，往外扫）。**上下对称**。光束起点处窄（约 4 格高），越往外越宽（末端约 10 格高）。",
     f"{GD} and {VI}",
     f"a HEXTECH RAY sweeping to the RIGHT from the cell's CENTER, 6 frames, {TB}: the LEFT HALF of every cell stays EMPTY; "
     "the beam starts exactly at the cell's center and reaches right: a white core 2 squares tall, a gold-orange glow "
     "round it, thin violet edges, 4 squares tall at the start widening to 10 squares at its end, a bright gold-white "
     "flare at its tip; 1 the beam 20 squares long; 2 50 long; 3 the full 70 squares, brightest; 4 the full beam; 5 the "
     "beam thinner, breaking into sparks; 6 fading sparks along the line.",
     row(6, 144, 28) + "; the beam's start on the cell's exact center column, vertically centered."),
    ("e_after", "E 升级的余波：沿射线路径的一串爆炸（地上的线，朝方向转），6 帧",
     "view_projectiles `league_viktor_e_after`（同 e_ray：格子右半边、上下对称）", "140 × 26",
     "余波：射线 1 秒后沿同一条路径炸开一串金橙色的小爆炸，从起点往外依次炸开（参考 Foundation_ImpactSpike、Ground_Trail、E_ErosionShapes）。**整张图左半边是空的**，**上下对称**。",
     f"{GD} and {VI}",
     f"an AFTERSHOCK along a line to the RIGHT from the cell's CENTER, 6 frames, {TB}: the LEFT HALF of every cell stays "
     "EMPTY; along a 70-square line from the center to the right, a chain of round gold-orange blasts 8 squares across "
     "(white cores, violet sparks) bursting one after another from the start outward: 1 two blasts near the start; 2 four "
     "blasts to 30 squares; 3 six blasts to 50; 4 the whole line of blasts to 70, brightest; 5 the blasts shrinking into "
     "sparks; 6 fading sparks.",
     row(6, 144, 28) + "; the line's start on the cell's exact center column, vertically centered."),
    ("e_hit", "E 打中（每个被射线打中的人身上），4 帧", "view_effects `league_viktor_e_hit`（跟随；左右对称）", "12",
     "被射线打中：人身上一团金白色的灼烧光，几颗金色火星往上飞（参考 E_Flare、Ember_Sharp）。**左右对称**。约 12 格，居中画。",
     GD,
     f"a RAY BURN HIT, 4 frames, {LR}: 1 a white-gold flash 6 squares across; 2 a gold-orange burst 10 squares across; 3 "
     "embers rising at mirrored places; 4 fading embers.",
     row(4, 14, 14) + "; centered in every cell."),
    ("e_after_hit", "E 余波打中，4 帧", "view_effects `league_viktor_e_after_hit`（跟随；左右对称）", "14",
     "被余波打中：一团更大的金橙色爆炸，带蓝紫色的火花（参考 Foundation_ImpactSpike、Paint_Sparks）。**左右对称**。约 14 格，居中画。",
     f"{GD} and {VI}",
     f"an AFTERSHOCK BLAST, 4 frames, {LR}: 1 a white-gold flash 8 squares across; 2 a round gold-orange blast 12 squares "
     "across with violet sparks; 3 the blast breaking up; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- R Arcane Storm
    ("r_land", "R 奥术风暴落下的爆发（地上），6 帧",
     "view_effects `league_viktor_r_land`（落点上，不旋转，画在人物下面；上下左右都对称）", "64 × 26",
     "风暴落下：地上一圈从斜上方看的扁椭圆，蓝紫色的冲击波从中间炸开，环上有海克斯符文的光点（参考 R_RadiusRing_Glows、R_HextechRing02、R_ground_glow、R_Runes）。**上下左右都对称**。这是风暴的范围（半径 30 格），约 64 格宽、26 格高。",
     f"{VI} and {CY}",
     f"an ARCANE STORM IMPACT on the ground seen from above at an angle, 6 frames, {BOTH}: 1 a white-violet flash 14 "
     "squares wide at the center; 2 a violet ring 30 squares wide with small cyan rune dots on it; 3 the ring 46 wide, the "
     "inside glowing; 4 the ring 60 wide and 24 tall; 5 the ring thinner, sparks; 6 fading sparks.",
     row(6, 64, 28) + "; centered in every cell."),
    ("r_storm", "R 奥术风暴：跟着英雄走的风暴（他身上，每秒播一次），6 帧",
     "view_effects `league_viktor_r_storm`（跟随英雄，画在人物上面；左右对称）", "60 × 56",
     "奥术风暴：英雄头顶一团旋转的蓝紫色风暴云，几道白紫色的闪电往下劈到他脚边，脚下一圈扁椭圆的紫色光环（参考 R_Stormwall_02、R_Bolts、R_beam_Bolts、R_Proc_Lightning、R_Glow_Edge）。"
     "**中间人站的位置留空、不画实心的东西**（闪电只在两边），**左右对称**（旋涡用对称的形状表现，不画朝一个方向转）。6 帧连起来 1 秒，循环播放。约 60 格宽、56 格高（风暴云在上，光环在下）。",
     f"{ST}, {VI} and {CY}",
     f"an ARCANE STORM over a figure, 6 frames, a seamless loop, {LR}, the figure's place in the middle EMPTY: at the top "
     "a swirling storm cloud 40 squares wide and 12 tall (dark violet with brighter violet and white edges, its swirl "
     "drawn as a symmetric spiral pattern, no one-way spin), at the bottom a flat violet ring 56 squares wide and 20 tall "
     "on the ground; two jagged white-violet lightning bolts striking down from the cloud to the ring at mirrored places "
     "LEFT and RIGHT of the figure (never through the middle); each frame the bolts and the cloud's bright edges change "
     "(keep every frame mirrored).",
     row(6, 62, 58) + "; the ring's bottom on the cell's bottom, centered across."),
    ("r_storm_big", "R 升级后变大的风暴（他身上，每秒播一次），6 帧",
     "view_effects `league_viktor_r_storm_big`（同上；左右对称）", "76 × 64",
     "同 r_storm，但更大更亮（范围半径 38 格）：风暴云更宽、闪电三道（两边各一道 + 背后一道细的往两边分叉），光环约 76 格宽。**中间留空，左右对称**。",
     f"{ST}, {VI} and {CY}",
     f"a GREATER ARCANE STORM over a figure, 6 frames, a seamless loop, {LR}, the figure's place in the middle EMPTY: as a "
     "storm cloud 52 squares wide and 14 tall at the top, a flat violet ring 72 squares wide and 26 tall at the bottom, "
     "lightning bolts striking down at mirrored places left and right of the figure (two on each side), brighter cyan "
     "sparks on the ring; each frame changes, every frame mirrored.",
     row(6, 78, 66) + "; the ring's bottom on the cell's bottom, centered across."),
    ("r_hit", "R 风暴每秒打中（每个被打中的人身上），4 帧", "view_effects `league_viktor_r_hit`（跟随；左右对称）", "12 × 18",
     "被风暴打中：一道细的白紫色闪电从上往下劈到人身上，落点炸开一小圈紫色火花（参考 R_hit_sparks、R_Proc_Lightning）。**左右对称**（闪电竖直居中）。约 12 格宽、18 格高。",
     f"{VI} and {CY}",
     f"a LIGHTNING STRIKE HIT, 4 frames, {LR}: 1 a thin white-violet lightning bolt striking straight down the middle, 16 "
     "squares tall, its zigzag mirrored; 2 the bolt brightest, a violet spark burst 8 squares across at its foot; 3 the "
     "bolt gone, sparks flying out at mirrored places; 4 fading sparks.",
     row(4, 14, 20) + "; the burst at the bottom-center of every cell."),
    # ---- the passive
    ("evo", "光荣进化：升级技能时他身上的海克斯光（他身上），6 帧",
     "view_effects `league_viktor_evo`（施法后，不跟随，画在人物上面；左右对称）", "30 × 44",
     "光荣进化升级一个技能：他脚下亮起一圈金色的海克斯光环往上升，几道金色光线往上射，身边飘起金色和青色的小光点（只画外圈和光线，中间留空）（参考 Star_Rays、Stardust、Skin18_Add_Gold、Ringlight）。**左右对称**。约 30 格宽、44 格高。",
     f"{GD} and {CY}",
     f"a HEXTECH EVOLUTION round a figure, 6 frames, {LR}, the figure's place EMPTY: 1 a gold ellipse ring 24 squares wide "
     "and 6 tall at the feet; 2 the ring rising to the waist, 4 thin vertical gold light rays at mirrored places; 3 the "
     "ring at the chest, the rays tallest, small gold and cyan sparks rising; 4 the ring at the head, bright; 5 the ring "
     "above the head, fading, sparks; 6 fading sparks.",
     row(6, 32, 46) + "; centered across, the feet ring on the cell's bottom."),
]

GROUPS = [
    ("attack", ["Viktor_Base_BA_Muzzle", "Viktor_Base_BA_Trail", "Viktor_Base_BA_GlowAlpha", "Viktor_Base_Flash",
                "Hit_Spark_blue", "Viktor_Base_Glow5"]),
    ("Q", ["Viktor_Rework_Base_Q_Missile_Head_2", "Viktor_Base_Q_HextechRing04", "Viktor_Base_Q_mis_glowTrail02",
           "Viktor_Base_Q_Buf_Hit_Burst", "Viktor_Rework_Base_Q_Impact_Cross", "Viktor_Base_Q_template_shield"]),
    ("W", ["Viktor_Base_W_Circle_normal", "Viktor_Base_W_Pulses_V02", "Viktor_Base_W_TrampleAOE_Glow",
           "Viktor_Base_W_LightBeam", "Viktor_Shockwave_SpaceNoise", "Viktor_Base_Ringlight"]),
    ("E", ["Viktor_Base_E_Trail_55", "Viktor_Base_E_Trench2", "Viktor_Base_E_Flare", "Viktor_Base_Beamhead_Centre",
           "Viktor_Base_Foundation_ImpactSpike_2x2", "Viktor_Rework_Base_Ember_Sharp"]),
    ("R", ["Viktor_Base_R_Stormwall_02", "Viktor_Base_R_Bolts", "Viktor_Base_R_beam_Bolts", "Viktor_Base_R_Proc_Lightning",
           "Viktor_Base_R_RadiusRing_Glows", "Viktor_Base_R_Runes"]),
    ("evolve", ["Viktor_Base_Star_Rays", "Viktor_Base_Stardust", "Viktor_Skin18_Add_Gold", "Viktor_Base_Erosion",
                "Viktor_Base_EnergyStrands", "Viktor_Base_idle_BightSpark"]),
]
# where the pictures start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point, dy from the soles]);
# from Codex's manifest anchors (the pivot 11 squares over the soles)
SHOTS = [("attack", 3, "a_bolt / a_blast: 远侧手（光弹从这里飞出）", [(18, -18)]),
         ("skill", 3, "q_bolt: 法杖头（光弹从这里射出）", [(8, -21)]),
         ("skill2", 3, "W: 甩出去的手（重力场落在敌人脚下，不从手上画）", [(17, -16)]),
         ("skill2_e", 3, "E: 金爪光核（射线画在目标处，不从这里画）", [(14, -27)]),
         ("idle", 1, "q_shield / q_charged / evo: 站位点", "feet")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Viktor_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"维克托 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (league/champions/league_viktor, the imported sheet), each picture's starting
    point as a cyan cross (the standing point is the frame's pivot: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_viktor"))
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    PAD = 12                                       # his head, the claw and the staff reach the frame's top
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
    a("# 奥术先驱 维克托：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/viktor_design.png`，8 倍，{h} 行、{w} 格宽）。")
    a(f"> - 大小对照 `design/viktor_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。维克托 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/viktor_shots.png`：定稿动作（4 倍），青色十字是特效的起点（伸出去的手、法杖头、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里维克托自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**他的奥术光是蓝紫色（机械臂、重力场、风暴），海克斯光是金橙色带白芯（Q、射线），Q 的护盾和机械臂的光核是青色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见；风暴云可以用一点深紫，但边缘要亮。")
    a("> - **围着人的光环、护盾泡泡、风暴、进化光只画外圈和两边，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的光弹（`a_bolt`、`a_blast`、`q_bolt`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "射线 `e_ray`、余波 `e_after` 是**线的画面**：游戏把整张图的**中心**放在目标脚下、朝「维克托→目标」的方向转，所以**光束只画在格子右半边、从正中间往右扫**，同样**上下对称**。"
      "画在人身上、脚下的（打中、晕眩、减速、护盾、强化光点、风暴、进化）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；"
      "地上的 `w_field`、`w_burst`、`r_land` 上下左右都对称。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `viktor_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`viktor_fx_done.zip`）放在 outputs 里，或放在 `outputs/viktor-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「光荣进化」 | 奥术光弹普攻；按等级依次升级 E、Q、W、R（升级时身上亮金光） | `a_bolt` · `a_hit` · `evo` · `evo_slow` |")
    a("| 技能 1 = Q「虹吸能量」 | 法杖射出海克斯光弹，打中得到护盾；4 秒内下一次普攻强化；升级后护盾更强并加速 | `q_bolt` · `q_hit` · `q_shield` · `q_charged` · `q_ms` · `a_blast` · `a_blast_hit` |")
    a("| 技能 2 = W「重力场」→ E「海克斯射线」 | 敌方英雄脚下放重力场：减速，1.25 秒后场内的人被晕；接着从目标处往外扫一道射线；升级后射线 1 秒后有余波 | `w_field` · `w_slow` · `w_burst` · `w_stun` · `e_ray` · `e_hit` · `e_after` · `e_after_hit` |")
    a("| 大招 = R「奥术风暴」 | 风暴落在敌方英雄身上、跟着他走，每秒打一下；目标阵亡就转到附近英雄；升级后风暴变大 | `r_land` · `r_storm` · `r_storm_big` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、射线、闪电、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀（风暴云可以多用一点）。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("蓝紫奥术光（普攻、重力场、风暴、闪电）", VIOLET), ("青色海克斯光（光核、Q 护盾、电弧）", CYAN),
                        ("金橙海克斯光（Q、射线、余波、进化）", GOLD), ("风暴深紫（风暴云）", STORM)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，"
      "重力场半径 30000，射线长 70000，风暴半径 30000（升级后 38000））。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `viktor_fx_{name}.png`：{title}\n")
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
        a(f"| `viktor_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 光弹从远侧手（普攻，出手帧手在站位点前 18 格、脚底上 18 格）和法杖头（Q）出；`bolt_y` 不超过约 8 格（太高的弹道会斜），画面开头补一帧空的（追踪弹第一 tick 朝上）。")
    a("- `e_ray` / `e_after`：线的画面在落点、朝施法者→落点转（champion-data section 6；hit = DirDot 锥形）；按 140 格宽切格，确认左半边是空的、上下对称。")
    a("- 没有烘进动作帧的特效：`q_shield`、`evo` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`w_field`、`w_burst`、`r_land` 画在人物下面（z -2 / -1）；`r_storm` 每秒一次，帧长合计约 1 秒。")
    a("- 用 `pixel_1x/` 切格（import_twitch / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单（`q_charged` 的文件绑定 view_buffs 的 `q_buff`）。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="viktor_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Viktor's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "viktor_design.png"))
    shape = size_sheet(os.path.join(out, "design", "viktor_size.png"))
    shots_sheet(os.path.join(out, "design", "viktor_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"viktor_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
