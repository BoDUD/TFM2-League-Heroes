#!/usr/bin/env python3
"""Build nilah_fx_pack.zip: step 3 of Nilah's sprite - Codex draws her effects (pack_nidalee_fx.py's way, with
pack_samira_fx.py's pictures drawn into the hero's own frames).

    python tools/art/pack_nilah_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name nilah_fx_redo_pack]

The pack (%LOCALAPPDATA%/Temp/nl_work/fx/nilah_fx_pack, zipped into --out, default dist/nilah_packs) holds PROMPTS.md
(also written to assets/source/nilah/PROMPTS_FX.md), design/nilah_designs.png (her front and side designs at 3x),
design/nilah_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/nilah_shots.png (the finished action frames, 1x at 4x, the point each picture on her starts from as a cyan
cross), bake/nilah_bake_<name>_<n>.png (the action frame a picture is drawn INTO, the figure faded on its own dense
grid at 7 px a square, the blade's tip as a cyan cross - the guide Codex draws on) and refs/lol_fx_ref.png (League's
own particle textures for Nilah, grouped by the effect of ours they inform; Riot's art, local only: it reads
%LOCALAPPDATA%/Temp/nl_work/fxref, extracted from Nilah.wad.client's base skin by Temp/nl_work/fx/fx_ref_nl.py).
The effects are the views the kit binds (tools/kit/build_nilah.py: view_effects a_hit, qa_hit, q_hit, eq_hit, eq_spin,
e_hit, w_ally, r_hit, r_pull, r_heal, r_spin, r_burst; view_buffs q_on, w_on, w_ally) and the pictures drawn into her
own frames at import (BAKE: the whip lashing out of the blade in attack / attack_q / skill, the water wake behind the
Slipstream dash in skill2): the client mirrors her frames with her facing and never an effect picture, so a lash that
points must ride in the frames (league_jhin's, league_samira's). She is a dense (PPU 2.5) hero, so those are drawn on
her own dense grid; the rest at game pixels like every pack's effects. League's colours: her water - white cores, sky to
deep blue - with the joy's iridescent pastels (pink, lilac, mint, gold) in W and R; light gets no outline.
Red side: every picture on a unit, on her, on the ground and every buff symmetric left to right.
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
import import_nilah_strips as I  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "nl_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "nilah", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_nilah")
HD = os.path.join(ROOT, "assets", "source", "nilah", "hd")
FRAMES = I.OUT
PRE = chr(92) * 2 + "?" + chr(92)
PPU = 2.5
FEET = 11


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


WATER = "#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294"          # her water: white core to deep blue
JOY = "#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A"    # the joy: iridescent pastels (W, R, heals)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a "
        "white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
WR = f"a water ramp ({WATER})"
JR = f"an iridescent joy ramp ({JOY})"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- hits on the target
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_nilah_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "鞭刃抽中：一小团水花炸开，白芯，几滴蓝色水珠往外溅（参考 BA_LinearSplashes、BA_Crit_Tar、Splash_2x2）。**左右对称**。约 12 格。", WR,
     f"a SMALL WATER-WHIP HIT, 4 frames, {LR}: 1 a white flash 4 squares; 2 a round water splash 9 squares across with a "
     "white core, 6 droplets at mirrored places; 3 the splash 12 squares, droplets flying out; 4 a few fading droplets.",
     row(4, 14, 14) + CENTER),
    ("qa_hit", "强化普攻打中（被扫到的每个敌人），4 帧", "view_effects `league_nilah_qa_hit`（跟随，画在人物上面；左右对称）", "14",
     "游刃万变期间的普攻扫中：比普攻大一点的水花，中间一道竖直的白亮水刃划痕，边上几点彩色亮光（参考 BA_Swipe、Light_sparks）。"
     "**左右对称**（划痕竖直）。约 14 格。", f"{WR} and {JR}",
     f"a WATER SLASH HIT, 4 frames, {LR}: 1 a white flash 5 squares; 2 a vertical slash streak of white-blue water 12 squares "
     "tall through the center, a splash 10 squares round it; 3 the splash 14 squares, 4 tiny iridescent glints at mirrored "
     "places; 4 fading droplets and glints.",
     row(4, 16, 16) + CENTER),
    ("q_hit", "Q 游刃万变：鞭子抽中（直线上的每个敌人），5 帧", "view_effects `league_nilah_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "Q 的长鞭抽中：一个白亮的 X 形水刃交叉划痕，水花往两边对称溅开（参考 Q_Swipe、Q_Water、Q_MissBubbles）。**左右对称**。约 16 格。", WR,
     f"a WHIP-LASH HIT, 5 frames, {LR}: 1 a white flash 6 squares; 2 two crossing water streaks (an X) 14 squares long with "
     "white cores; 3 the X at its brightest, a splash 16 squares round it, droplets at mirrored places; 4 the X breaking into "
     "spray; 5 fading droplets.",
     row(5, 18, 18) + CENTER),
    ("eq_hit", "E 之后的旋转斩：扫中（每个敌人），4 帧", "view_effects `league_nilah_eq_hit`（跟随，画在人物上面；左右对称）", "14",
     "旋转一圈扫中：一圈小小的水环炸开，白芯（参考 E_Q_Fill、E_WaterCrescent）。**左右对称**。约 14 格。", WR,
     f"a SPIN-CUT HIT, 4 frames, {LR}: 1 a white flash 5 squares; 2 a small water ring 10 squares across, white inner edge; "
     "3 the ring 14 squares, breaking into 6 droplets at mirrored places; 4 fading droplets.",
     row(4, 16, 16) + CENTER),
    ("e_hit", "E 纵情逐流：冲过去时打中（每个敌人），4 帧", "view_effects `league_nilah_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "冲刺穿过时的打中：一道竖直的水浪冲起来又落下，两边溅水花（参考 E_Dash_Tar_Splash、E_AirBullet）。**左右对称**。约 14 格。", WR,
     f"a DASH HIT, 4 frames, {LR}: 1 a white flash 5 squares; 2 a vertical column of white-blue water 12 squares tall, "
     "splashes at both sides; 3 the column falling into a splash 14 squares wide; 4 fading droplets.",
     row(4, 16, 16) + CENTER),
    ("r_hit", "R 神恩激荡：旋转中每一下打中（每个敌人），4 帧", "view_effects `league_nilah_r_hit`（跟随，画在人物上面；左右对称）", "12",
     "大招旋转时一下一下打中：小小的白亮 X 划痕加几点水珠（参考 R_Cone_Hit、R_Swipe_Mult）。**左右对称**。约 12 格（这张会连着出现很多次，要小、要快）。", WR,
     f"a QUICK CUT HIT, 4 frames, {LR}: 1 a white dot 3 squares; 2 a small X of white-blue streaks 9 squares across; 3 the X "
     "12 squares, 4 droplets at mirrored places; 4 fading.",
     row(4, 14, 14) + CENTER),
    ("r_pull", "R 神恩激荡：最后一下把敌人拉过来（每个敌人），5 帧", "view_effects `league_nilah_r_pull`（跟随，画在人物上面；左右对称）", "18",
     "大招最后一击：敌人身上一个水的漩涡往里收，再炸开一团大水花（参考 R_buf_Shock、R_splash_ring、R_Flash）。**左右对称**。约 18 格。", WR,
     f"a PULL-IN BURST, 5 frames, {LR}: 1 a ring of water 18 squares across; 2 the ring drawn inward to 10 squares, curling "
     "streaks at mirrored places; 3 a white flash 8 squares at the center; 4 a water burst 18 squares across with droplets at "
     "mirrored places; 5 fading droplets.",
     row(5, 20, 20) + CENTER),
    # ---- on allies
    ("w_ally", "W 轻纱飞漾：碰到队友的那一下（队友身上），5 帧", "view_effects `league_nilah_w_ally`（跟随，画在人物上面；左右对称）", "18",
     "队友被纱幕碰到：一团欢快的彩色光丝和亮片往外绽开（粉、淡紫、薄荷、金，白芯；参考 W_Sparkle、W_WaterThreads、W_Halo）。"
     "**左右对称**，中间人形位置留空。约 18 格。", JR,
     f"a JOYFUL SPARKLE BURST round a figure, 5 frames, {LR}, the middle EMPTY (a clear upright area 8 squares wide and 14 "
     "tall): 1 4 white sparkles at mirrored places; 2 curling iridescent ribbons rising at both sides 16 squares tall; 3 the "
     "ribbons and 8 sparkles at their brightest, 18 squares across; 4 the ribbons thinning; 5 a few fading sparkles.",
     row(5, 20, 22) + "; centered across, the bottom of the shape 1 square above the cell's bottom."),
    ("r_heal", "R 神恩激荡：治疗和护盾（队友和她自己身上），5 帧", "view_effects `league_nilah_r_heal`（跟随，画在人物上面；左右对称）",
     "16 × 22",
     "大招把伤害转成治疗和护盾：队友身上一层水光从脚下升起，几个水泡和彩色亮片往上飘，最后在身前合成一层淡淡的光罩（参考 R_Waves_color、"
     "R_GradientV、common_waterdots）。**左右对称**，中间人形位置留空。", f"{WR} and {JR}",
     f"a HEAL-AND-SHIELD RISE round a figure, 5 frames, {LR}, the middle EMPTY (a clear upright area 8 squares wide and 18 "
     "tall): 1 a water glow on the ground 12 squares wide; 2 water light rising at both sides 16 squares tall, 3 bubbles; 3 "
     "the light at its top, iridescent sparkles at mirrored places; 4 a thin bright arc over the empty middle (the shield); "
     "5 fading bubbles.",
     row(5, 18, 24) + "; centered across, the glow's bottom on the cell's bottom row."),
    # ---- round her (big)
    ("eq_spin", "E 之后的旋转斩：鞭子绕她一圈（她身上，大），5 帧", "view_effects `league_nilah_eq_spin`（BIG，她身上，跟随；左右对称）", "56 × 24",
     "E 冲过去后接 Q 的旋转：鞭刃带着水光在她腰间绕一整圈（从斜上方看的扁椭圆环，前后都画），水花往外甩（参考 E_Q_Wave_Mask、"
     "E_WaterCrescent、Q_Swipe2）。**左右对称**，中间她的身体位置留空。", WR,
     f"a WHIP SPIN RING round a figure at waist height, 5 frames, {LR}, the middle EMPTY (a clear upright area 12 squares "
     "wide and 20 tall over the center): 1 a thin white-blue arc across the front of an ellipse 40 squares wide; 2 the whole "
     "ellipse ring 52 squares wide and 20 tall, 3 squares thick, white leading edge; 3 the ring at its brightest, 56 squares "
     "wide, spray flying out at mirrored places; 4 the ring breaking into a circle of droplets; 5 fading droplets.",
     row(5, 58, 26) + "; the ellipse centered in every cell."),
    ("r_spin", "R 神恩激荡：旋转的鞭刃风暴（她身上，大，1 秒），8 帧", "view_effects `league_nilah_r_spin`（BIG，她身上，跟随；左右对称）", "76 × 32",
     "大招 1 秒的旋转：几道带水光的鞭刃环一层层绕着她转（扁椭圆，内圈快外圈慢），水珠和彩色亮片被甩出去，地上一圈涟漪（参考 R_Orbit、"
     "R_Sword_Trail2、R_trail、R_Puddle_Ripples、RainbowGrad_Soft）。**左右对称**，中间她的身体位置留空。8 帧连着播一秒，最后一帧接下一张爆发。",
     f"{WR} and {JR}",
     f"a WHIRLING WHIP STORM round a figure, 8 frames, {LR}, the middle EMPTY (a clear upright area 14 squares wide and 26 "
     "tall over the center): two or three nested elliptical rings of white-blue water light (the outer 76 squares wide and "
     "30 tall, the inner 50 wide), each 2-3 squares thick, their bright arcs moving round frame to frame; droplets and "
     "iridescent glints thrown outward at mirrored places; a thin ripple ellipse on the ground under them; the rings grow "
     "from frame 1 to frame 3, stay at full size 4-7, and tighten in frame 8.",
     row(8, 78, 34) + "; the ellipses centered in every cell."),
    ("r_burst", "R 神恩激荡：最后的爆发（她身上，大），5 帧", "view_effects `league_nilah_r_burst`（BIG，她身上，跟随；左右对称）", "80 × 36",
     "大招最后把人拉过来的一下：一圈大水浪从她身边往外炸开，带着彩色的光，再落成水珠（参考 BlastRing、R_splash_ring、R_EnergyStreaksAdd、"
     "R_Flash）。**左右对称**，中间她的身体位置留空。", f"{WR} and {JR}",
     f"a GREAT WATER BURST round a figure, 5 frames, {LR}, the middle EMPTY (a clear upright area 14 squares wide and 26 tall "
     "over the center): 1 a white flash ring 30 squares wide; 2 a thick ring of water 56 squares wide and 24 tall bursting "
     "outward, iridescent edge; 3 the ring 80 squares wide, spray at mirrored places; 4 the ring breaking into droplets; 5 "
     "fading droplets and glints.",
     row(5, 82, 38) + "; the rings centered in every cell."),
    # ---- buffs
    ("q_on", "Q 游刃万变：4 秒强化（她身上，循环），4 帧", "view_buffs `league_nilah_q_on`（跟随，画在人物上面；左右对称）", "24 × 30",
     "游刃万变期间（攻击距离变长、普攻横扫、吸血）：她身上淡淡的一圈水光，几滴水珠绕着她慢慢转（参考 Q_cas_glow、Droplet_Rotate、"
     "common_waterdots）。要淡，不能挡住她。**左右对称**，中间人形位置留空。", WR,
     f"a FAINT WATER AURA round a figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 12 squares "
     "wide and 24 tall): 6 small droplets (2 squares each) at mirrored places round the empty middle, taking turns to "
     "brighten, and thin pale-blue arcs at both sides that shimmer.",
     row(4, 26, 32) + CENTER),
    ("w_on", "W 轻纱飞漾：她身上的纱幕（循环，大），6 帧", "view_buffs `league_nilah_w_on`（BIG，跟随，画在人物上面；左右对称）", "34 × 46",
     "纱幕（2.25 秒躲开所有普攻）：一层半透明感的彩色薄纱绕着她飘（粉、淡紫、薄荷、金色的光带，像流动的丝），几个亮片闪烁（参考 W_Aura_Flames、"
     "W_WispTrail_Add、W_Halo_1、W_Sparkle）。像素画里不要半透明：用细的光带和亮片表现轻盈。**左右对称**，中间人形位置留空。", JR,
     f"a FLOWING IRIDESCENT VEIL round a figure, 6 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 14 "
     "squares wide and 36 tall): thin flowing ribbons of pink, lilac, mint and gold light (2 squares thick) rising and "
     "curling up both sides to 46 squares tall, 6 white sparkles at mirrored places taking turns; the ribbons' waves move "
     "up a little each frame.",
     row(6, 36, 48) + "; centered across, the ribbons' bottom 1 square above the cell's bottom."),
    ("w_ally_veil", "W 轻纱飞漾：队友身上的纱幕（循环，大），6 帧",
     "view_buffs `league_nilah_w_ally`（BIG 表里 tag 叫 w_ally；跟随，画在人物上面；左右对称）", "30 × 42",
     "被碰到的队友 1.5 秒也有纱幕：和她身上那张一样的彩色光带，细一点、少一点。**左右对称**，中间人形位置留空。", JR,
     f"a THIN IRIDESCENT VEIL round a figure, 6 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 12 "
     "squares wide and 32 tall): two thin flowing ribbons of pink, lilac, mint and gold light (1-2 squares thick) curling up "
     "both sides to 42 squares tall, 4 white sparkles at mirrored places taking turns.",
     row(6, 32, 44) + "; centered across, the ribbons' bottom 1 square above the cell's bottom."),
]
# pictures drawn INTO her own frames (on her dense grid, the guide's canvas): name, tag, frames, over / under the
# figure, title (zh), description (zh), ramps, the effect (en) per frame
BAKE_W, BAKE_H = 260, 146          # the guide canvas in her dense squares (the frames' 219 x 146, room ahead for Q)
BAKE_PX = 7
BAKE = [
    ("a_lash", "attack", (3, 4), "over", "普攻：鞭刃从刃尖甩出去（画进她的普攻第 3、4 帧）",
     "普攻刺出去那一下，折叠的鞭刃从刃尖松开甩出去，像一条带水光的细鞭：第 3 帧伸出一半、波浪形；第 4 帧伸直到最远，鞭尖炸开一小团水花。"
     "鞭子从图上青色十字（刃尖）开始往**右**伸。", WR,
     {3: "a THIN WATER-LIGHT WHIP uncoiling to the RIGHT from the cyan cross (the blade's tip): a wavy ribbon 2-3 squares "
         "thick and 14 squares long with a white core, a few droplets along it.",
      4: "the WHIP fully out to the RIGHT from the cyan cross: a nearly straight ribbon 2-3 squares thick and 20 squares long "
         "with a white core, ending in a small crack-splash 6 squares across at its tip, droplets flying."}),
    ("qa_lash", "attack_q", (3, 4), "over", "强化普攻：更长的鞭子加扇形水刃（画进她的强化普攻第 3、4 帧）",
     "游刃万变期间的普攻：鞭子甩得更远（攻击距离 +12.5），鞭尖前面扇开一片扇形的水刃，扫中扇形里的敌人。第 3 帧鞭子伸出、扇形刚出现；"
     "第 4 帧扇形最大，带水花。从青色十字（刃尖）往**右**。", WR,
     {3: "a WATER-LIGHT WHIP to the RIGHT from the cyan cross: a ribbon 3 squares thick and 26 squares long with a white "
         "core, a narrow fan of water starting to open ahead of its tip.",
      4: "the WHIP 32 squares long to the RIGHT from the cyan cross, and ahead of its tip a WIDE FAN of water slashes opening "
         "to the right (about 40 degrees across, 30 squares deep, 3-4 curved white-edged streaks), spray at its rim."}),
    ("q_lash", "skill", (4, 5), "over", "Q 游刃万变：直线长鞭（画进她的 Q 第 4、5 帧）",
     "Q 把鞭刃甩成一条笔直的长鞭，一直抽到 62 个游戏像素远（格子里第 235 列，图上有黄线标出）：第 4 帧整条鞭子伸直，"
     "细长（2-3 格粗）、白芯、沿路有水珠，鞭尖一团水花；第 5 帧鞭子收回，原来的位置留下一道正在散开的水雾线。从青色十字（刃尖）往**右**。",
     WR,
     {4: "a LONG STRAIGHT WATER-LIGHT WHIP to the RIGHT from the cyan cross to the yellow line: 2-3 squares thick with a "
         "white core, small droplets along it, a splash 8 squares across at its tip on the yellow line.",
      5: "the whip gone: along the same line a thin fading streak of water spray and droplets, brightest near the tip, "
         "breaking up."}),
    ("e_trail", "skill2", (1, 2, 3), "under", "E 纵情逐流：冲刺时身后的水痕（画进她的 E 第 1、2、3 帧，画在她身后）",
     "冲刺穿过敌人时，她身后拖一条流动的水带（从她的腰和拖在后面的鞭刃往**左**拖出去，约 40 格长），水珠往后飞，"
     "第 1 帧短，第 2 帧最长，第 3 帧开始散。画在人物**后面**（被人物挡住的地方不用画）。", WR,
     {1: "a FLOWING WATER WAKE trailing to the LEFT from the figure's waist: a wavy ribbon 4-6 squares thick and 24 squares "
         "long, white crest along its top, droplets behind.",
      2: "the WAKE at its longest: 40 squares to the LEFT from the figure's waist, 6 squares thick near her thinning to the "
         "end, white crest, droplets flying back.",
      3: "the WAKE breaking up: 36 squares long, its far half turning into spray and droplets."}),
]
GROUPS = [
    ("whip / lash", ["Nilah_Base_BA_Swipe_01", "Nilah_Base_BA_Swipe_02", "Nilah_Base_Q_Swipe", "Nilah_Base_Q_Swipe2",
                     "Nilah_Base_Q_Water", "Nilah_Base_Trail_Horizontal"]),
    ("hits", ["Nilah_Base_BA_LinearSplashes_02", "Nilah_Base_BA_Crit_Tar", "Nilah_base_BA_Crit_flare", "Nilah_Base_Splash_2x2",
              "Nilah_Base_Q_MissBubbles", "Nilah_Base_Light_sparks"]),
    ("E dash / spin", ["Nilah_Base_E_Dash_Wake_Ground", "Nilah_Base_E_Dash_Tar_Splash", "Nilah_Base_E_WaterCrescent_2x2",
                       "Nilah_Base_E_Q_Wave_Mask", "Nilah_Base_E_Q_Fill", "Nilah_Base_E_AirBullet"]),
    ("W veil", ["Nilah_Base_W_Aura_Flames", "Nilah_Base_W_WispTrail_Add", "Nilah_Base_W_Halo_1", "Nilah_Base_W_Sparkle",
                "Nilah_Base_W_WaterThreads_2x2", "Nilah_Base_RainbowGrad_Soft"]),
    ("R storm", ["Nilah_Base_R_Orbit", "Nilah_Base_R_Sword_Trail2", "Nilah_Base_R_trail", "Nilah_Base_R_Puddle_Ripples",
                 "Nilah_Base_R_splash_ring", "Nilah_Base_BlastRing"]),
    ("R hits / heal", ["Nilah_Base_R_Cone_Hit", "Nilah_Base_R_buf_Shock", "Nilah_Base_R_Flash", "Nilah_Base_R_Waves_color",
                       "Nilah_Base_R_EnergyStreaksAdd", "common_waterdots"]),
]
# where the pictures on her start (tag, frame, what, marks: "feet" = her standing point under the soles, or [(dx, dy)]
# in game px from the pivot (x forward, y down; the soles 11 under it))
SHOTS = [("q_spin", 2, "eq_spin: 环的中心（站位点上方 7 格）", [(0, -7)]),
         ("ult", 3, "r_spin / r_burst: 环的中心（站位点上方 7 格）", [(0, -7)]),
         ("idle", 1, "q_on / w_on: 身体中间", [(0, -9)]), ("w_cast", 2, "w_on 起手", "feet")]


def ref_sheet(path):
    S, LW = 180, 120
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                continue
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Nilah_Base_", "").replace("Nilah_base_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    return [np.asarray(sp.frames[i].convert("RGBA")) for i in sp.tag_frames(tag)]


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def designs(path):
    front = crop(np.asarray(Image.open(os.path.join(HD, "front.png")).convert("RGBA")))
    side = crop(np.asarray(Image.open(os.path.join(HD, "side.png")).convert("RGBA")))
    H = max(front.shape[0], side.shape[0])
    both = np.zeros((H, front.shape[1] + 12 + side.shape[1], 4), np.uint8)
    both[H - front.shape[0]:, :front.shape[1]] = front
    both[H - side.shape[0]:, front.shape[1] + 12:] = side
    Image.fromarray(np.repeat(np.repeat(both, 3, 0), 3, 1)).save(path)


def size_sheet(path):
    """Her 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter."""
    import tfm2_ase as T
    fig = crop(sheet_frames("idle")[0])
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    kn = crop(k)
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    top = max(fig.shape[0], kn.shape[0])
    img = Image.new("RGBA", (max(W * Z, 720), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
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
    d.text((8, 36), f"尼菈 {fig.shape[1]}×{fig.shape[0]} 格（连举起的刃，游戏里显示 90%），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames (1x) at 4x, each picture's starting point as a cyan cross."""
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, marks in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px, py = f.shape[1] / 2.0, f.shape[0] / 2.0
        pts = [(px, py + FEET)] if marks == "feet" else [(px + dx, py + dy) for dx, dy in marks]
        ys, xs = np.nonzero(f[..., 3] > 0)
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
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def blade_tip(a, left=False):
    """The figure's rightmost (or leftmost) square and its row: the blade's tip in a thrust."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    x = xs.min() if left else xs.max()
    return int(x), int(np.median(ys[xs == x]))


def bake_guides(out):
    """bake/nilah_bake_<name>_<n>.png: the frame faded on the BAKE_W x BAKE_H canvas at BAKE_PX a square, a light grid
    every 10 squares, the cyan cross on the blade's tip (or the waist for the wake), Q's reach as a yellow line.
    -> {(name, n): anchor (x, y) in squares}."""
    fr = json.load(open(os.path.join(FRAMES, "frames.json"), encoding="utf-8"))
    anchors = {}
    for name, tag, ks, _, *_ in BAKE:
        for k in ks:
            a = np.asarray(Image.open(os.path.join(FRAMES, fr[tag][k - 1][0])).convert("RGBA"))
            if name == "e_trail":
                op = a[..., 3] > 0
                ys, xs = np.nonzero(op)
                anchor = (int(np.median(xs)), int(np.median(ys)))     # the waist, about
            else:
                anchor = blade_tip(a)
            anchors[(name, k)] = anchor
            can = np.zeros((BAKE_H, BAKE_W, 4), np.uint8)
            can[:a.shape[0], :a.shape[1]] = a
            img = Image.new("RGB", (BAKE_W * BAKE_PX, BAKE_H * BAKE_PX), (36, 40, 52))
            g = np.asarray(Image.fromarray(can).resize((BAKE_W * BAKE_PX, BAKE_H * BAKE_PX), Image.NEAREST)).astype(float)
            m = g[..., 3:] / 255.0
            grey = g[..., :3].mean(-1, keepdims=True) * 0.35 + 70
            base = np.asarray(img).astype(float)
            img = Image.fromarray((base * (1 - m) + grey * m).astype(np.uint8))
            d = ImageDraw.Draw(img)
            for x in range(0, BAKE_W + 1, 10):
                d.line([(x * BAKE_PX, 0), (x * BAKE_PX, img.height)], fill=(52, 58, 72))
            for y in range(0, BAKE_H + 1, 10):
                d.line([(0, y * BAKE_PX), (img.width, y * BAKE_PX)], fill=(52, 58, 72))
            d.line([(0, (I.SOLE + 1) * BAKE_PX), (img.width, (I.SOLE + 1) * BAKE_PX)], fill=(150, 60, 60), width=2)
            if name == "q_lash":
                qx = int(I.PIV + 62 * PPU)
                d.line([(qx * BAKE_PX, 0), (qx * BAKE_PX, img.height)], fill=(255, 220, 40), width=3)
            cx, cy = (anchor[0] + 0.5) * BAKE_PX, (anchor[1] + 0.5) * BAKE_PX
            d.line([(cx - 18, cy), (cx + 18, cy)], fill=(0, 255, 255), width=3)
            d.line([(cx, cy - 18), (cx, cy + 18)], fill=(0, 255, 255), width=3)
            img.save(os.path.join(out, f"nilah_bake_{name}_{k}.png"))
    return anchors


def document(shape, anchors):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 不羁之悦 尼菈：给 Codex 的特效提示词（第 3 步）\n")
    n_bake = sum(len(b[2]) for b in BAKE)
    a(f"> **这一份是 {len(FX)} 张特效图 + {n_bake} 张画进她动作帧的鞭子 / 水痕图。** 造型和动作已定（`design/nilah_designs.png`：3/4 正面待机和侧面；"
      "动作都是侧面朝右）。")
    a(f"> - 她在游戏里是**高清**的：每个游戏像素里 2.5×2.5 个细格子；1 倍时 {w}×{h} 格（连举起的刃），游戏里再按 90% 显示。")
    a("> - **两种画法**：")
    a("> 1. 第一部分 15 张普通特效（打中、绕身、纱幕）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。大小对照 `design/nilah_size.png`"
      "（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；`design/nilah_shots.png` 是定稿动作（4 倍），青色十字是绕身特效的中心。")
    a("> 2. 第二部分是**画进她自己动作帧**的鞭子和水痕（她的帧会随朝向镜像，特效图不会，所以有方向的鞭子必须画进帧里）。这些按**她的高清细格子**画："
      f"`bake/nilah_bake_<名字>_<帧>.png` 是那一帧的定位图（{BAKE_W}×{BAKE_H} 格，每格 {BAKE_PX} 像素，她本人画成淡灰色、只用来对位置，"
      "青色十字是起点，红线是地面，每 10 格一道浅线）。**在同样大小、同样格子的图上只画特效，背景透明，不要画她本人**；Claude 按格子取回，直接叠进她的帧。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里尼菈自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**她的鞭刃和招式都是水：白芯、天蓝到深蓝的水光、水珠和水花**；**W 纱幕和大招的治疗带着彩虹般的粉、淡紫、薄荷、金色光**。")
    a("> - **特效要亮**：每道水光、每个亮片都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的环、纱幕只画外圈和两边，中间身体位置留空**。")
    a("> - **方向（重要，红色方不会镜像）**：第一部分所有画面（打中、她身上、队友身上、绕身的环和纱幕）都要**严格左右对称**（逐格对称）——划痕一律竖直或 X 形。"
      "第二部分画进帧里的鞭子和水痕照定位图的方向画（鞭子朝右，水痕朝左），不用对称。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nilah_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），以及 `nilah_bake_<名字>_<帧>.png`"
      f"（第二部分，{BAKE_W * BAKE_PX}×{BAKE_H * BAKE_PX}，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（{BAKE_W}×{BAKE_H}）。透明度只有 0 和 255、要求对称的逐格对称。"
      "附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `nilah_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「喜色川流」 | 鞭刃抽击；Q 强化期间攻击距离变长、横扫扇形、吸血 | `a_lash`（帧里）· `a_hit` · `qa_lash`（帧里）· `qa_hit` · `q_on` |")
    a("| 技能 1 = Q「游刃万变」 | 鞭子甩成一条直线长鞭抽过去，之后 4 秒强化；E 之后是原地旋转一圈 | `q_lash`（帧里）· `q_hit` · `eq_spin` · `eq_hit` |")
    a("| 技能 2 = E「纵情逐流」+ W「轻纱飞漾」 | E 冲刺穿过敌人（两层充能）；E 都用掉时开 W：躲开普攻、加速，碰到的队友也有纱幕 | `e_trail`（帧里）· `e_hit` · `w_on` · `w_ally`（碰到的那一下）· `w_ally_veil`（队友身上的纱幕） |")
    a("| 大招「神恩激荡」 | 原地旋转 1 秒连续打，最后把周围敌人拉过来；伤害转成队友和自己的治疗、护盾 | `r_spin` · `r_hit` · `r_burst` · `r_pull` · `r_heal` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水光、水花、亮片、光带都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("水（鞭子、打中、旋转、水痕）", WATER), ("彩虹（W 纱幕、大招的治疗和光）", JOY)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 第一部分：特效（{len(FX)} 张，游戏格子）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位："
      "普攻距离 30000，Q 直线 62000，E 后旋转半径 28000，E 落点半径 16000，大招半径 38000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `nilah_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a(f"## 第二部分：画进她动作帧的鞭子和水痕（{n_bake} 张，她的高清格子）\n")
    a(f"每张都在对应的定位图 `bake/nilah_bake_<名字>_<帧>.png` 上画：同样 {BAKE_W * BAKE_PX}×{BAKE_H * BAKE_PX} 像素、每格 {BAKE_PX} 像素、"
      f"{BAKE_W}×{BAKE_H} 格，格子和定位图完全对齐；**只画特效，不画她**，背景透明。她本人在定位图里是淡灰色，只用来对位置。"
      "鞭子从青色十字（刃尖）开始；她身前的鞭子画在她**上面**（会盖住她），身后的水痕画在她**后面**（被她挡住的部分不用画）。\n")
    k0 = len(FX)
    for name, tag, ks, layer, title, zh, ramps, effects in BAKE:
        a(f"### {k0 + 1}. {title}\n")
        k0 += 1
        a(zh + "\n")
        for k in ks:
            x, y = anchors[(name, k)]
            a(f"**`nilah_bake_{name}_{k}.png`**（定位图 `bake/nilah_bake_{name}_{k}.png`，起点青色十字在第 {x} 列、第 {y} 行）：\n")
            a("```text")
            a(LEAD.format(ramps=ramps).replace("VFX sprite sheet", "VFX overlay on a character frame"))
            a(f"Effect: {effects[k]}")
            a(f"Layout: ONE image {BAKE_W * BAKE_PX}x{BAKE_H * BAKE_PX}, the same size and {BAKE_PX}-px square grid as the "
              f"guide picture (a {BAKE_W} x {BAKE_H} square grid); the cyan cross of the guide is at square ({x}, {y}) "
              f"counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the "
              f"cross or the lines. {TAIL}")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `nilah_fx_{name}` | {bind} | {size} |")
    for name, tag, ks, layer, *_ in BAKE:
        a(f"| `nilah_bake_{name}_<帧>` | 画进 `{tag}` 第 {'、'.join(str(k) for k in ks)} 帧（{'人物上面' if layer == 'over' else '人物后面'}） | 高清格子 |")
    a("")
    a("- 两张表：`asset/league/effects/league_nilah_fx`（小的）和 `league_nilah_big`（eq_spin、r_spin、r_burst、w_on，和 tag 叫 w_ally 的 `w_ally_veil`），"
      "tag = 名字（build_nilah.py 的 views）。")
    a("- 画进帧的四张在 restyle 加粗外描边之后叠到高清帧上（它们没有描边），1 倍表一起更新；`e_trail` 画进帧以后，技能里的 `cview(\"e_trail\")` 和它的 view 一起删掉。")
    a("- 用 `pixel_1x/` 切格（import_nidalee / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, BAKE
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="nilah_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "nilah_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        BAKE = [x for x in BAKE if x[0] in keep]
        if len(FX) + len(BAKE) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run Temp/nl_work/fx/fx_ref_nl.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs", "bake"):
        os.makedirs(os.path.join(out, sub))
    designs(os.path.join(out, "design", "nilah_designs.png"))
    shape = size_sheet(os.path.join(out, "design", "nilah_size.png"))
    shots_sheet(os.path.join(out, "design", "nilah_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    anchors = bake_guides(os.path.join(out, "bake"))
    doc = document(shape, anchors)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"nilah_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX] +
                  [{"file": f"nilah_bake_{b[0]}_{k}.png", "into": f"{b[1]} {k}", "layer": b[3],
                    "anchor": list(anchors[(b[0], k)]), "canvas": [BAKE_W, BAKE_H], "px": BAKE_PX}
                   for b in BAKE for k in b[2]], f, ensure_ascii=False, indent=1)
    print(len(FX), "effects,", sum(len(b[2]) for b in BAKE), "frame overlays;", DOC, shape)
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
