#!/usr/bin/env python3
"""Build yunara_fx_pack.zip: step 3 of Yunara's sprite - Codex draws her effects (pack_kalista_fx.py's way).

    python tools/art/pack_yunara_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name yunara_fx_redo_pack]

The pack (%TEMP%/yu_work/fx/yunara_fx_pack, zipped into --out, default dist/yunara_packs) holds PROMPTS.md (also
written to assets/source/yunara/PROMPTS_FX.md), design/yunara_idle.png (her dense idle at 3x), design/yunara_size.png
(the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/yunara_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Yunara grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/yu_work/fxref, read out of Yunara.wad.client's base-skin particle paths by work/yu/fx_ref_yu.py).
The effects are the views the kit binds (tools/kit/build_yunara.py: view_projectiles a_bead, q_bead, w_bead, rw_beam;
view_effects a_hit, q_hit, q_sp_hit, q_spread, q_burst, w_hit, w_end, w_tick, rw_charge, rw_hit, e_cast, re_trail,
r_burst; view_buffs q_on, r_on, e_ms, w_slow0, rw_slow0).
Colours: her spirit light violet-blue with white cores (League's Tile / swirl textures are tinted that way), the
Transcendent State gold-white (the R star, her R form's gold rim), the beads her own bronze; light gets no outline.
Red side: the flying pictures (a_bead, q_bead, w_bead) and the laser (rw_beam: a LineRangeProjectile's view, turned to
the cast) symmetric top to bottom; every picture on a unit, on her, on the ground and every buff symmetric left to
right (the client never mirrors an effect picture).
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "yu_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "yunara", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_yunara")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SPIRIT = "#FFFFFF, #ECE8FF, #C3B8FF, #937FF7, #6450DC, #3A2A9E"   # her spirit light: white core to deep violet-blue
GOLD = "#FFFFFF, #FFF7DA, #FFE48E, #F8C244, #DF9B30, #9A5A18"     # the Transcendent State: white to warm gold
BRONZE = "#F8C244, #DF9B30, #A45132, #5B3335, #393033"           # her prayer beads (the design's own bronze)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, mist, sparks, rings or beams, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
SP = f"a spirit violet-blue ramp ({SPIRIT})"
GO = f"a transcendent gold ramp ({GOLD})"
BR = f"a bronze bead ramp ({BRONZE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
FEET = "; centered across, the figure's feet on the cell's bottom row."

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and Cultivation of Spirit (Q, folded into the attack)
    ("a_bead", "普攻：飞出去的铜念珠（朝目标飞，循环），2 帧", "view_projectiles `league_yunara_a_bead`（朝飞行方向转，画成朝右飞；上下对称）",
     "14 × 8", "普攻：一颗铜色念珠（圆，约 5 格，右上亮金、左下深棕，两三颗深色圆钉）朝右飞，后面拖一小段紫蓝色的灵气光尾（参考 BA_orb01、MissileLead、Trail10）。**上下对称**。",
     f"{BR} and {SP}",
     f"a BRONZE PRAYER BEAD flying to the RIGHT, 2 frames, a seamless loop, {TB}: a round bronze bead 5 squares across (bright "
     "gold on its upper right, dark brown on its lower left, two dark round studs placed symmetric top to bottom) with a thin "
     "dark outline; a violet-blue spirit trail 7 squares long and 3 tall behind it with a white core line, flickering between "
     "the two frames.",
     row(2, 14, 8) + "; the bead's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_bead", "灵蕴拳开启时的普攻念珠（朝目标飞，循环），4 帧", "view_projectiles `league_yunara_q_bead`（朝飞行方向转，画成朝右飞；上下对称）",
     "18 × 10", "灵蕴拳开启后的念珠：同样的铜念珠，整颗包在一圈白紫色的灵气里，后面拖一条更长更亮的紫蓝色光尾，几点灵气火星（参考 Q_orb01、Passive_orb01、Q_BeamAlpha）。**上下对称**。",
     f"{BR} and {SP}",
     f"an EMPOWERED BEAD flying to the RIGHT, 4 frames, a seamless loop, {TB}: the same bronze bead 5 squares across wrapped in a "
     "bright white-violet glow 8 squares across; a tapering violet-blue trail 10 squares long behind it with a white core, small "
     "spirit sparks above and below it at mirrored places, drifting between frames.",
     row(4, 18, 10) + "; the glow's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_yunara_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "念珠打中：一小团紫蓝色的灵气闪光，几道短短的紫色光线往外射（参考 Yunara_Q_Tar_Flare、Base_Generic_Sparks）。**左右对称**。约 10 格。", SP,
     f"a SMALL SPIRIT HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a violet-white flash 7 squares with a white core; "
     "3 the flash 10 squares, 6 short violet rays at mirrored places; 4 a few fading violet motes.",
     row(4, 12, 12) + CENTER),
    ("q_hit", "灵蕴拳开启时打中（目标身上），5 帧", "view_effects `league_yunara_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "灵蕴拳打中：一个白紫色的星形冲击（参考 Q_Impact_TarSplash 的星形溅射），外面一圈紫蓝色的冲击环，几点灵气碎光飞出。**左右对称**。约 16 格。",
     SP,
     f"an EMPOWERED SPIRIT IMPACT on a unit, 5 frames, {LR}: 1 a white flash 4 squares; 2 a white-violet starburst 10 squares "
     "with 8 sharp points at mirrored places and a white core; 3 the starburst 14 squares and a violet-blue ring 16 squares "
     "round it; 4 the ring fading, violet bits flying out at mirrored places; 5 fading motes.",
     row(5, 18, 18) + CENTER),
    ("q_sp_hit", "灵蕴拳溅射到旁边的敌人（目标身上），3 帧", "view_effects `league_yunara_q_sp_hit`（跟随，画在人物上面；左右对称）", "8",
     "溅射：旁边的敌人身上一小点紫色灵气火花。**左右对称**。约 8 格。", SP,
     f"a TINY SPIRIT SPARK on a unit, 3 frames, {LR}: 1 a white dot with a violet glow 3 squares; 2 a violet four-pointed spark "
     "8 squares with a white core; 3 fading violet motes.",
     row(3, 10, 10) + CENTER),
    ("q_spread", "灵蕴拳溅射：从目标脚下扩散的灵气环（地上，不跟随），4 帧", "view_effects `league_yunara_q_spread`（不跟随，地上；左右对称；大图表）", "60 × 20",
     "溅射范围：目标脚下一圈紫蓝色的灵气波纹（扁椭圆，从斜上方看）从小扩到大，然后散掉（参考 Q_OneShot_Ring_Swipe、Q_distortion_soundwaves）。**左右对称**。",
     SP,
     f"a SPIRIT RIPPLE spreading on the ground, 4 frames, {LR}: a flat violet-blue ellipse ring (seen from above at a slant, 3 times "
     "as wide as tall) with a white inner edge: 1 a ring 20 squares wide and 6 tall; 2 the ring 40 wide and 13 tall; 3 the ring "
     "60 wide and 20 tall, thinner; 4 the ring breaking into violet motes.",
     row(4, 62, 22) + "; the rings centered in every cell."),
    ("q_burst", "灵蕴拳开启（她身上，跟随），5 帧", "view_effects `league_yunara_q_burst`（跟随她，画在人物上面；左右对称；大图表）", "28 × 40",
     "灵蕴拳满了自动开启：她身边一下子腾起一圈紫蓝色的灵气火焰，往上窜后散成火星（参考 Fire_2x2、Passive_Eletile03、Aura_Self）。**左右对称**，中间身体位置留空（只画两边和外圈）。",
     SP,
     f"a SPIRIT FLARE round a figure, 5 frames, {LR}, the middle EMPTY (a clear area 16 squares wide and 34 tall where she "
     "stands, not drawn): 1 violet light at both sides of her waist; 2 violet-blue spirit flames 10 squares tall rising at both "
     "sides with white cores; 3 the flames 20 squares tall reaching her shoulders, sparks above; 4 the flames breaking into "
     "violet sparks drifting up; 5 the last sparks.",
     row(5, 28, 40) + FEET),
    # ---- W Arc of Judgment and R's W, Arc of Ruin
    ("w_bead", "W 善恶轮：旋转的大念珠（朝目标飞，循环），4 帧", "view_projectiles `league_yunara_w_bead`（朝飞行方向转，画成朝右飞；上下对称）",
     "18 × 14", "善恶轮：一颗大一点的铜念珠（约 8 格）在飞行中旋转，外面裹着一圈紫蓝色的旋涡光环（参考 W_BGSwirl、W_Circle、W_Symbol），后面一小段光尾。**上下对称**（旋涡的弧上下对称地画，四帧之间转动）。",
     f"{BR} and {SP}",
     f"a SPINNING BIG BEAD flying to the RIGHT, 4 frames, a seamless loop, {TB}: a bronze bead 8 squares across (bright gold, "
     "bronze, dark brown, three dark round studs) inside a violet-blue swirl ring 14 squares across made of two curved arcs at "
     "mirrored places top and bottom, with white cores; the bead's studs and the arcs turn a quarter round over the 4 frames; "
     "a short violet trail 4 squares behind.",
     row(4, 18, 14) + "; the ring's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_hit", "W 念珠打中（目标身上），4 帧", "view_effects `league_yunara_w_hit`（跟随，画在人物上面；左右对称）", "14",
     "善恶轮打中：一团铜金色加紫色的冲击，几道紫色的弧线绕着目标一闪（参考 W_OneShot_Ring_Swipe_shape）。**左右对称**。约 14 格。",
     f"{SP} and {BR}",
     f"a BEAD IMPACT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a gold-violet burst 10 squares with a white core; 3 "
     "two violet arcs 14 squares wide curving round it at mirrored places, gold sparks; 4 fading motes.",
     row(4, 16, 16) + CENTER),
    ("w_end", "W 念珠停下后原地旋转（地上，不跟随），6 帧", "view_effects `league_yunara_w_end`（不跟随，地上；左右对称）", "20 × 16",
     "念珠飞到头：在终点悬在地面上方原地旋转约 1 秒（脚下一圈紫色光环），最后化成光点散掉。**左右对称**。",
     f"{BR} and {SP}",
     f"a SPINNING BEAD hovering over the ground, 6 frames, {LR}: a bronze bead 8 squares across 4 squares above a flat violet "
     "ground ring 18 wide and 5 tall; frames 1-4 the bead's studs turn a quarter each frame (seen from the front, kept symmetric "
     "left to right by placing the studs in the middle column or in mirrored pairs) and violet swirl arcs circle it at mirrored "
     "places; frame 5 the bead flashing white-violet; frame 6 it breaks into violet motes, the ring fading.",
     row(6, 20, 16) + "; centered across, the ground ring's middle 3 squares above the cell's bottom row."),
    ("w_tick", "W 终点旋转时打到人（目标身上），3 帧", "view_effects `league_yunara_w_tick`（不跟随，目标身上；左右对称）", "10",
     "终点旋转时每次打到人：一道短短的紫色弧形划痕。**左右对称**（画成一个向上弯的弧）。约 10 格。", SP,
     f"a SMALL SPIRIT SLASH on a unit, 3 frames, {LR}: 1 a white dot; 2 a violet arc 10 squares wide curving upward (a smile "
     "shape, symmetric) with a white core line; 3 the arc fading into motes.",
     row(3, 12, 12) + CENTER),
    ("rw_charge", "大招期间 W 寂灭掌：头顶蓄力（她身上，跟随），4 帧", "view_effects `league_yunara_rw_charge`（跟随她，画在人物上面；左右对称；大图表）",
     "32 × 60", "寂灭掌蓄力：她把龙头珠举到头顶，龙头珠的位置亮起一颗金白色的四芒星（参考 R_CastSymbol02、R_Star），光往里收；只画星和光，**格子下面她站的位置留空**。**左右对称**。",
     GO,
     f"a GOLDEN CHARGE STAR high over a figure, 4 frames, {LR}; the figure (not drawn) stands in the lower part of the cell, "
     "its feet on the bottom row and its head 40 squares up: the star's middle 47 squares above the cell's bottom row, "
     "centered across: 1 a white-gold dot 4 squares; 2 a four-pointed gold-white star 14 squares tall and wide with a white "
     "core, thin gold rays drawn inward from 24 squares out; 3 the star 18 squares, brightest; 4 the star pulsing smaller, "
     "gold motes round it.",
     row(4, 32, 60) + "; the star's middle 47 squares above the bottom row, centered across."),
    ("rw_beam", "大招期间 W 寂灭掌：射线（施法方向，单次），6 帧", "view_projectiles `league_yunara_rw_beam`（LineRangeProjectile：画成朝右、从左端施法者处开始；上下对称；大图表）",
     "120 × 18", "寂灭掌：从她手边朝前射出一道金白色的射线，前几帧是细细的瞄准线（光慢慢变亮），然后整道射线爆开变粗（白芯、金边、外面一层紫色光晕），最后变细消失（参考 RW_Indicator01、VGU_Awaken_Line_Hori、Q_BeamAlpha）。"
     "**上下对称**，**最左边 6 格留空**（那是她的身体）。",
     f"{GO} and {SP}",
     f"a LASER BEAM shooting to the RIGHT, 6 frames, played once, {TB}, the leftmost 6 squares of every cell EMPTY (she stands "
     "there): 1 a thin gold aiming line 1 square tall along the cell's middle row from square 6 to the right edge, faint; 2 the "
     "line brighter, 2 squares tall, gold motes gathering at its left end; 3 the line 2 squares, white core; 4 the BEAM - 12 "
     "squares tall: a white core 4 squares, gold edges, a violet outer glow, from square 6 to the right edge, a bright gold "
     "flare 18 squares tall at its left end; 5 the beam 8 squares tall and fading at the edges; 6 a thin fading line and motes.",
     row(6, 120, 18) + "; the line on the cell's middle row in every cell."),
    ("rw_hit", "W 寂灭掌打中（目标身上），5 帧", "view_effects `league_yunara_rw_hit`（跟随，画在人物上面；左右对称）", "18",
     "射线打中：一团金白色的爆光，外面一圈紫色的冲击环，几道金色光线往外射（参考 R_Impact_TarSplash_D）。**左右对称**。约 18 格。",
     f"{GO} and {SP}",
     f"a GOLDEN BLAST on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 a gold-white burst 12 squares with a white core; "
     "3 a violet ring 18 squares round it, 8 gold rays at mirrored places; 4 the ring fading, gold sparks out; 5 fading motes.",
     row(5, 20, 20) + CENTER),
    # ---- E Kanmei's Steps and R's E, Untouchable Shadow
    ("e_cast", "E 明踪步：起步（她脚下，跟随），5 帧", "view_effects `league_yunara_e_cast`（跟随她，画在人物下面；左右对称）", "30 × 12",
     "明踪步：她脚下卷起一圈紫蓝色的风（扁椭圆的风环），两边各甩出几道风痕往上散（参考 E_Swipe_A、E_GroundSmoke02）。**左右对称**（不画方向）。",
     SP,
     f"a SPIRIT GUST at a figure's feet, 5 frames, {LR}: 1 a flat violet ellipse 12 wide and 4 tall on the ground; 2 the ellipse "
     "24 wide, two curved wind streaks rising at both sides; 3 the ellipse 30 wide, the streaks 8 squares up and thinning; 4 "
     "the streaks breaking into violet motes; 5 the last motes.",
     row(5, 30, 12) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
    ("re_trail", "大招期间 E 夜影翻：翻身冲刺（她身上，跟随），5 帧", "view_effects `league_yunara_re_trail`（跟随她，画在人物下面；左右对称；大图表）", "40 × 44",
     "夜影翻：她后空翻时身边一圈紫金色的残影光弧（像一个圆环形的光带绕着她转一圈），中间身体位置留空。**左右对称**（光弧在两边对称地转）。",
     f"{SP} and {GO}",
     f"a SPINNING LIGHT ARC round a flipping figure, 5 frames, {LR}, the middle EMPTY (a clear circle 24 squares across where "
     "she is, not drawn): two curved light ribbons, violet with gold edges and white cores, on a circle 36 squares across round "
     "the clear middle at mirrored places left and right; they sweep round the circle a quarter turn each frame (always "
     "mirrored left to right); frame 5 the ribbons fading into motes.",
     row(5, 40, 44) + "; the circle's middle 20 squares above the cell's bottom row, centered across."),
    # ---- R Transcend One's Self
    ("r_burst", "大招 定圣诀：进入超凡形态（她身上，跟随），6 帧", "view_effects `league_yunara_r_burst`（跟随她，画在人物后面；左右对称；大图表）",
     "56 × 64", "定圣诀：她身后亮起一颗巨大的金白色四芒星（参考 R_Star、R_StarDissolve、R_CastSymbol02），星芒向四周射出，一圈金色光环扩散，然后化成金色光点往上飘。画在她身后，所以中间可以画星，但不要画成实心的一大块。**左右对称**。",
     GO,
     f"a TRANSCENDENT STAR behind a figure, 6 frames, {LR} (the figure, not drawn, stands with its feet on the bottom row, 40 "
     "squares tall): 1 a white-gold flare 6 squares at her chest height (24 squares up); 2 a four-pointed gold-white star 30 "
     "squares tall and wide there, white core, long thin points; 3 the star 44 squares with a gold ring 40 squares round it; "
     "4 the ring 54 squares and thinner, the star shrinking; 5 gold motes rising from where the ring was; 6 the last motes.",
     row(6, 56, 64) + FEET),
    # ---- buffs
    ("q_on", "灵蕴拳开启中（她身上，循环），4 帧", "view_buffs `league_yunara_q_on`（跟随她，画在人物上面；左右对称）", "28 × 30",
     "灵蕴拳开启期间：她两边腰、手的高度一直有几团紫蓝色的灵气小火苗和火星在跳动。**左右对称**，中间身体位置留空。",
     SP,
     f"SPIRIT EMBERS round a figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear area 14 squares wide where she "
     "stands): small violet-blue spirit flames 3-5 squares tall with white cores at both sides between 12 and 26 squares above "
     "the cell's bottom row, flickering and rising a square between frames, a few sparks drifting up.",
     row(4, 28, 30) + FEET),
    ("r_on", "超凡形态中（她脚下和身后，循环），4 帧", "view_buffs `league_yunara_r_on`（跟随她，画在人物后面；左右对称；大图表）", "36 × 48",
     "超凡形态期间：她脚下一圈金色的光环（扁椭圆），身后不断有金色光点和细细的光丝往上飘。**左右对称**。",
     GO,
     f"a TRANSCENDENT AURA behind a figure, 4 frames, a seamless loop, {LR}: a flat gold ellipse ring 30 wide and 8 tall round "
     "the feet on the ground; gold motes and thin vertical gold light threads rising from it up to 44 squares, at mirrored "
     "places, moving up 3 squares between frames; nothing solid over the middle.",
     row(4, 36, 48) + FEET),
    ("e_ms", "明踪步加速中（她脚下，循环），4 帧", "view_buffs `league_yunara_e_ms`（跟随她，画在人物下面；左右对称）", "24 × 8",
     "加速期间：她脚下两边各有几道紫蓝色的小风痕在卷动（不画方向）。**左右对称**。",
     SP,
     f"SPIRIT WIND at a figure's feet, 4 frames, a seamless loop, {LR}: small curled violet wind streaks 4-6 squares long at both "
     "sides of the feet, 1-6 squares above the bottom row, curling round between frames.",
     row(4, 24, 8) + CENTER),
    ("w_slow0", "被善恶轮减速（敌人脚下，循环），4 帧", "view_buffs `league_yunara_w_slow0`（跟随，画在人物下面；左右对称）", "16 × 5",
     "被念珠减速：敌人脚下一圈淡淡的紫色光环，几点紫光轮流闪。**左右对称**。", SP,
     f"a FAINT VIOLET RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 14 squares wide and 4 tall "
     "in violet, 4 brighter motes on it at mirrored places taking turns to light up.",
     row(4, 16, 6) + CENTER),
    ("rw_slow0", "被寂灭掌减速（敌人脚下，循环），4 帧", "view_buffs `league_yunara_rw_slow0`（跟随，画在人物下面；左右对称）", "16 × 5",
     "被射线减速：敌人脚下一圈淡淡的金色光环，几点金光轮流闪。**左右对称**。", GO,
     f"a FAINT GOLD RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 14 squares wide and 4 tall "
     "in gold, 4 brighter motes on it at mirrored places taking turns to light up.",
     row(4, 16, 6) + CENTER),
]

GROUPS = [
    ("a_bead q_bead", ["Yunara_Base_BA_orb01", "Yunara_Base_Q_orb01", "Yunara_Base_Passive_orb01", "Yunara_Base_MissileLead",
                       "Yunara_Base_Trail10", "Yunara_Base_Q_BeamAlpha"]),
    ("a_hit q_* ", ["Yunara_Q_Tar_Flare", "Yunara_Base_Q_Impact_TarSplash", "Yunara_Base_Q_OneShot_Ring_Swipe_shape1",
                    "Yunara_Base_Q_distortion_soundwaves_01", "Yunara_Base_Fire_2x2", "Yunara_Base_Passive_Eletile03"]),
    ("w_*", ["Yunara_Base_W_BGSwirl", "Yunara_Base_W_Circle", "Yunara_Base_W_Symbol",
             "Yunara_Base_W_OneShot_Ring_Swipe_shape", "Yunara_Base_W_HeadDiffuse", "Yunara_Base_Tile01"]),
    ("rw_* r_*", ["Yunara_Base_R_Star", "Yunara_Base_R_CastSymbol02", "Yunara_Base_R_StarDissolve",
                  "Yunara_Base_R_Impact_TarSplash_D", "Yunara_Base_RW_Indicator01", "Yunara_Base_VGU_Awaken_Line_Hori"]),
    ("e_* re_trail", ["Yunara_Base_E_Swipe_A", "Yunara_Base_E_GroundSmoke02", "Yunara_Base_E_ErosionShapes01",
                      "Yunara_Base_Stringlowres", "Yunara_Base_Tile03", "Yunara_Base_Aura_Self"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_bead：普攻推掌出手"), ("skill", 5, "w_bead：W 推掌出手"), ("skill_r", 3, "rw_charge：龙头珠举过头顶蓄力"),
         ("skill_r", 6, "rw_beam：马步推出射线"), ("skill2_r", 3, "re_trail：后空翻"), ("ult", 3, "r_burst：进入超凡形态")]


def ref_sheet(path):
    S, LW = 180, 140
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
            d.text((LW + c * S + 4, y + 2), nm.replace("Yunara_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    img = Image.new("RGBA", (W * Z, (pad + top + 4) * Z + 64), (104, 112, 72, 255))
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
    d.text((8, 36), f"芸阿娜 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连念珠），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        py = f.shape[0] // 2 + 11                      # the frame's centre is the pivot, the feet 11 px under it
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0, x1 = int(min(xs.min(), px)) - 3, int(max(xs.max(), px)) + 4
        y0, y1 = int(min(ys.min(), py)) - 3, int(max(ys.max(), py)) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((px - x0) * Z), int((py - y0) * Z) + 24
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


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 不破之誓 芸阿娜：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/yunara_idle.png`：3/4 正面朝右站立，近侧手放在腰带上，远侧手向前伸，"
      f"手下挂着紫水晶龙头珠；身边漂着六颗铜念珠）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连念珠 {h} 格高、{w} 格宽；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/yunara_size.png`：她的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/yunara_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里芸阿娜自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色：**普攻、灵蕴拳、善恶轮、明踪步是紫蓝色的灵气（白芯）**，**大招「定圣诀」、超凡形态和寂灭掌射线是金白色**，**念珠是她自己的铜色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光圈、火焰只画外圈和两边，中间身体位置留空**。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bead`、`q_bead`、`w_bead` 和射线 `rw_beam` 画成朝右，**上下对称**（往左时会上下翻）。"
      "其余所有画面（打中、身上、脚下、头顶、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `yunara_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、格子宽高）和生图原稿 `raw/`，打包成 `yunara_fx_pack_done.zip`。"
      "**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「初生之誓」+ Q「灵蕴拳」 | 掷出铜念珠；攒满灵蕴自动开启：攻速、额外魔法伤害、溅射周围敌人 | `a_bead` · `a_hit` · `q_bead` · `q_hit` · `q_sp_hit` · `q_spread` · `q_burst` · `q_on` |")
    a("| 技能 1 = W「善恶轮」 / 超凡形态「寂灭掌」 | 旋转念珠飞出、终点原地旋转；超凡形态时改为金色射线 | `w_bead` · `w_hit` · `w_end` · `w_tick` · `w_slow0` · `rw_charge` · `rw_beam` · `rw_hit` · `rw_slow0` |")
    a("| 技能 2 = E「明踪步」 / 超凡形态「夜影翻」 | 加速；超凡形态时后空翻冲刺 | `e_cast` · `e_ms` · `re_trail` |")
    a("| 大招「定圣诀」 | 进入超凡形态 15 秒 | `r_burst` · `r_on` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、火星、光环、射线都没有黑描边，也不要用最深的颜色给形状描一圈边**（铜念珠例外：念珠可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("灵气紫蓝（普攻、灵蕴拳、善恶轮、明踪步）", SPIRIT), ("超凡金白（大招、寂灭掌、夜影翻的金边）", GOLD),
                        ("铜念珠", BRONZE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 57500，"
      "善恶轮飞行 110000，灵蕴拳溅射半径 30000，寂灭掌射线长 120000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `yunara_fx_{name}.png`：{title}\n")
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
        a(f"| `yunara_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_yunara_fx`（小的）和 `league_yunara_big`（q_spread、q_burst、rw_charge、rw_beam、re_trail、r_burst、r_on），tag = 名字（build_yunara.py 的 views，需要时把绑定的表改过来）。")
    a("- `a_bead`、`q_bead`、`w_bead` 是飞行投射物，画面朝飞行方向转；`rw_beam` 是 LineRangeProjectile 的画面（以线段中点为中心、朝施法方向转），帧时长按射线 34 tick 命中排（前 3 帧瞄准线约 540 ms，第 4 帧在命中时）；"
      "`q_spread`、`w_end`、`w_tick` 不跟随；`e_cast`、`re_trail`、`r_on`、`e_ms`、慢速圈画在人物下面（z -1），`r_burst` 也放到她身后（z -1）。")
    a("- 用 `pixel_1x/` 切格（import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="yunara_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "yunara_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/yu/fx_ref_yu.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = sheet_frames("hd_idle")[0]
    ys, xs = np.nonzero(hd[..., 3] > 0)
    hd = hd[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(np.repeat(np.repeat(hd, 3, 0), 3, 1)).save(os.path.join(out, "design", "yunara_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "yunara_size.png"))
    shots_sheet(os.path.join(out, "design", "yunara_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"yunara_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
