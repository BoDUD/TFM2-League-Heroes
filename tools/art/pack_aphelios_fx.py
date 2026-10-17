#!/usr/bin/env python3
"""Build aphelios_fx_pack.zip: step 3 of Aphelios's sprite - Codex draws his effects (pack_pantheon_fx.py's way).

    python work/ap/fx_ref_ap.py             # League's particle textures -> %TEMP%/ap_work/fxref (Riot's art, local only)
    python tools/art/pack_aphelios_fx.py [--no-zip] [--out DIR] [--only a_hit,q_c_hit --name aphelios_fx_redo_pack]

The pack (%TEMP%/ap_work/fx/aphelios_fx_pack, zipped into --out, default dist/aphelios_packs) holds PROMPTS.md (also
written to assets/source/aphelios/PROMPTS_FX.md), design/aphelios_idle.png (his design at 4x), design/aphelios_size.png
(the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter), design/aphelios_shots.png
(the finished action frames the pictures start from, 4x, the muzzle marked) and refs/lol_fx_ref.png (League's own
particle textures for Aphelios grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_aphelios.py). Each weapon keeps League's colour: Calibrum
green-teal, Severum red, Gravitum violet, Infernum blue, Crescendum white-silver; the moonlight (the swap, the ult) pale
moon blue-white. Two pictures are drawn once and multiplied by Claude: the weapon aura under his feet (mw, recoloured
to each weapon) and the muzzle flash (muzzle, recoloured and moved to each weapon's muzzle); several bindings share a
picture (q_s_bolt = a_sev, a_inf_s = a_inf, q_s_off / q_i_off / r_c_shot = off_bolt or q_c_pop, r_slow = g_slow).
Red side: the flying pictures symmetric top to bottom (they turn with the flight); the sentry (a zone's picture turns
180 degrees on the red side) point-symmetric; Infernum's wave the only directional caster picture (played late:
is_follow false, memory red-side-caster-pictures); every other picture symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ap_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "aphelios", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_aphelios")
HD = os.path.join(ROOT, "assets", "source", "aphelios", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GREEN = "#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B"     # Calibrum
RED = "#FFFFFF, #FFD9D9, #FF8080, #E8394A, #A31D35, #5C0F22"       # Severum
VIOLET = "#FFFFFF, #E8D9FF, #B78FFF, #7B4FE2, #4C2BA8, #25124F"    # Gravitum
BLUE = "#FFFFFF, #D9EFFF, #80C6FF, #3B87F0, #1F50B8, #0E2560"      # Infernum
SILVER = "#FFFFFF, #F3F6FF, #CFD9F0, #9CAACC, #6B7899, #3C4560"    # Crescendum
MOON = "#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B"      # the moonlight (the swap, the ult)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with "
        "its lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
G = f"a moon-green ramp ({GREEN})"
R = f"a crimson ramp ({RED})"
V = f"a violet ramp ({VIOLET})"
B = f"an azure flame ramp ({BLUE})"
S = f"a silver ramp ({SILVER})"
M = f"a pale moonlight ramp ({MOON})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
PT = ("POINT-SYMMETRIC in every frame (the same picture turned 180 degrees: on the red side the game turns it upside "
      "down and back to front)")
CENTER = "; centered in every cell."
FIG = "an upright slim figure 18 squares wide and 46 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the five weapons' shots
    ("a_cal", "通碧普攻：狙击子弹（朝目标飞，循环），3 帧",
     "view_projectiles `league_aphelios_a_cal`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 5",
     "通碧的子弹：一颗细长的月绿色光弹，前端白色最亮，后面拖一条青绿色的细尾巴（参考 BA_calibrum_mis、BA_mis_core_radiance、BA_HexTrail）。**上下对称**。",
     G, f"a SLIM MOON-GREEN SNIPER BULLET flying to the RIGHT, 3 frames, a seamless loop, {TB}: a bright white-green core 4 "
        "squares long and 2 thick at the RIGHT end, a tapering green trail 12 squares long behind it, flickering.",
     row(3, 18, 7) + "; the core's front 1 square from the RIGHT edge, vertically centered."),
    ("a_sev", "断魄普攻：镰刃弹（朝目标飞，循环），3 帧",
     "view_projectiles `league_aphelios_a_sev`，Q 断魄的连射 `q_s_bolt` 也用它（朝飞行方向转；上下对称）", "9 × 7",
     "断魄的子弹：一枚小小的血红色月牙形光弹（像一片弯刃），白芯，后面一点红色拖尾（参考 BA_severum_galaxy、BA_severum_hit_core）。**上下对称**（月牙开口朝后）。",
     R, f"a SMALL CRIMSON CRESCENT BOLT flying to the RIGHT, 3 frames, a seamless loop, {TB}: a crescent 5 squares tall, its "
        "round side forward (RIGHT), opening backward, a white core line, a short red streak 4 squares behind it.",
     row(3, 11, 9) + CENTER),
    ("a_grav", "坠明普攻：重力弹（朝目标飞，循环），4 帧",
     "view_projectiles `league_aphelios_a_grav`（朝飞行方向转；上下对称）", "10 × 7",
     "坠明的子弹：一颗紫色的小月球（暗紫色外圈、亮紫白色的芯），后面拖一条紫色的旋涡尾巴（参考 BA_gravitum_mis_head_trail、Gravitum_weapon_eclipse）。**上下对称**。",
     V, f"a VIOLET GRAVITY ORB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round orb 5 squares across (deep violet rim, "
        "a white-violet core) at the RIGHT end, a swirling violet trail 6 squares behind it, the swirl turning between frames.",
     row(4, 12, 9) + CENTER),
    ("a_inf", "荧焰普攻：蓝焰弹（朝目标飞，循环），3 帧",
     "view_projectiles `league_aphelios_a_inf`，溅射弹 `a_inf_s` 也用它（朝飞行方向转；上下对称）", "12 × 7",
     "荧焰的子弹：一团蓝色的火焰弹，前端白色，后面散开几缕蓝火（参考 BA_infernum_mis_shape、Q_infernum_flame）。**上下对称**。",
     B, f"an AZURE FLAME BOLT flying to the RIGHT, 3 frames, a seamless loop, {TB}: a flame head 5 squares across with a white "
        "core at the RIGHT end, 3 tongues of blue fire trailing 7 squares behind it at mirrored places.",
     row(3, 14, 9) + CENTER),
    ("a_cre", "折镜普攻：回旋刃（朝目标飞，转着飞，循环），4 帧",
     "view_projectiles `league_aphelios_a_cre`（朝飞行方向转；上下对称）", "9 × 9",
     "折镜扔出去的回旋刃：一枚银白色的双月牙飞轮，转着飞，中间一个圆环（参考 BA_crescendum_trail、Ripper_Shuriken_Highlights）。每一帧**上下对称**（转的四个角度都要对称）。",
     S, f"a SPINNING SILVER CHAKRAM flying to the RIGHT, 4 frames of one turn, a seamless loop, {TB}: two crescent blades 9 "
        "squares across round a small ring, white-silver with a white core, a faint silver motion arc behind it; frame 1 the "
        "blades level, 2 turned 45 degrees, 3 upright, 4 turned 135 degrees (each frame mirrored top to bottom).",
     row(4, 11, 11) + CENTER),
    # ---- Calibrum's Moonshot
    ("q_c_shot", "Q 通碧·狙杀：月光狙击弹（朝目标飞，循环），4 帧",
     "view_projectiles `league_aphelios_q_c_shot`（朝飞行方向转；上下对称；大图表）", "34 × 9",
     "通碧 Q 的狙击：一道又长又亮的月绿色光束弹，前端一颗白色的弹头，后面一条长长的绿色光尾，两边几颗绿色光点（参考 Q_calibrum_mis_02、Q_calibrum_mis_core、Q_beam_line_calibrum）。**上下对称**。",
     G, f"a LONG MOON-GREEN SNIPER BEAM flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white bullet head 6 squares long "
        "and 3 thick at the RIGHT end in a green glow 7 squares tall, a straight green light trail 26 squares long behind it, "
        "fading toward the LEFT, a few green motes at mirrored places flickering.",
     row(4, 36, 11) + "; the head's front 1 square from the RIGHT edge, vertically centered."),
    ("q_c_hit", "Q 通碧命中：月痕（目标身上），5 帧", "view_effects `league_aphelios_q_c_hit`（跟随，画在人物上面；左右对称）", "16",
     "通碧 Q 打中：一团绿白色的闪光，目标身上留下一个绿色的月牙标记符号（参考 BA_calibrum_symbol、Q_core_calibrum）。**左右对称**（月牙上下开口）。约 16 格。",
     G, f"a MOON-GREEN MARK on a unit, 5 frames, {LR}: 1 a white flash 4 squares; 2 a green burst 12 squares with a white core; 3 "
        "a green crescent-moon sigil 10 squares across, its points up, a thin green ring 16 squares round it; 4 the ring fading, "
        "the sigil glowing; 5 the sigil fading.",
     row(5, 18, 18) + CENTER),
    ("q_c_pop", "月痕引爆：追射弹（朝目标飞）+ 引爆（目标身上），飞行 3 帧 + 引爆 4 帧",
     "view_projectiles `league_aphelios_q_c_pop`（追射弹，上下对称；大招的通碧追射 `r_c_shot` 也用它），"
     "view_effects `league_aphelios_q_c_pop`（引爆，跟随，左右对称）", "弹 12 × 5；引爆 18",
     "画两张：① 追射弹：比普攻更亮更快的绿色光弹（**上下对称**）；② 引爆：月痕炸开，一团绿白色的爆闪和一圈绿色光环（**左右对称**）。",
     G, f"TWO STRIPS. (A) a FAST MOON-GREEN BOLT flying to the RIGHT, 3 frames, a seamless loop, {TB}: a white-green core 4 "
        f"squares long, a green trail 8 squares behind it. (B) a GREEN MARK BURSTING on a unit, 4 frames, {LR}: 1 a white flash "
        "6 squares; 2 a green burst 14 squares with a white core; 3 a green ring 18 squares across breaking into motes; 4 fading "
        "motes.",
     "(A) " + row(3, 14, 7) + "; (B) " + row(4, 20, 20) + CENTER),
    # ---- Severum's Onslaught
    ("q_s_on", "Q 断魄·恒月强袭：他脚下的血色旋光（跟随，循环），4 帧",
     "view_effects `league_aphelios_q_s_on`（跟随，画在他身上、人物下面；左右对称）", "30 × 10",
     "断魄 Q 的加速连射：他脚下一圈血红色的光环在转，几道红色弧光绕着他（参考 Q_severum_ground_ring、Q_severum_swirls、Q_Severum_cas_ground_glow）。**左右对称**，只画地上的环和绕身的弧，中间身体留空。",
     R, f"a CRIMSON GROUND SWIRL under a figure, 4 frames, a seamless loop, {LR}: a flat red ellipse ring 28 squares wide and 8 "
        "tall with a bright rim, 4 short red arcs on it at mirrored places moving round between frames, a few red motes.",
     row(4, 30, 12) + CENTER),
    ("q_s_hit", "Q 断魄连射命中（目标身上），3 帧", "view_effects `league_aphelios_q_s_hit`（跟随，画在人物上面；左右对称）", "9",
     "断魄的每一发打中：一小道红色的十字刃光。**左右对称**。约 9 格（会连续出现很多次，要小）。", R,
     f"a TINY CRIMSON SLASH on a unit, 3 frames, {LR}: 1 a white dot 2 squares; 2 a red X-shaped slash 8 squares; 3 fading red motes.",
     row(3, 11, 11) + CENTER),
    ("off_bolt", "副手追击弹（朝目标飞，循环），3 帧",
     "view_projectiles `league_aphelios_q_s_off` / `q_i_off`（副手武器的追击弹；上下对称）", "11 × 5",
     "副手武器的子弹（断魄 Q 的每第二发、荧焰 Q 波后的追击）：一颗银白带一点淡紫的月光弹，后面一条短尾巴（参考 BA_mis_cas、BA_mis_reaper_glow）。**上下对称**。",
     M, f"a PALE MOONLIGHT BOLT flying to the RIGHT, 3 frames, a seamless loop, {TB}: a white core 4 squares long at the RIGHT end in "
        "a pale blue glow 4 squares tall, a pale trail 7 squares behind it.",
     row(3, 13, 7) + CENTER),
    # ---- Gravitum's Binding Eclipse
    ("q_g_cast", "Q 坠明·引力枷锁：施放时他脚下的月蚀（跟随），5 帧",
     "view_effects `league_aphelios_q_g_cast`（跟随，画在他身上、人物下面；左右对称；大图表）", "36 × 12",
     "坠明 Q 发动：他脚下一个紫色的月蚀圈（暗紫色的圆盘、亮紫色的边，中间一个黑色的月影），往外扩一下（参考 E_Eclips01、E_eclipse-bead、Gravitum_weapon_eclipse）。**左右对称**。",
     V, f"a VIOLET ECLIPSE on the ground under a figure, 5 frames, {LR}: 1 a small violet ellipse 10 squares wide; 2 an eclipse "
        "ellipse 24 wide and 8 tall: a dark violet disc with a bright violet rim and a black moon-shadow in the middle; 3 the "
        "eclipse 36 wide, the rim brightest with violet beads round it at mirrored places; 4 the beads rising as motes; 5 fading.",
     row(5, 38, 14) + CENTER),
    ("q_g_hit", "Q 坠明定身（目标身上），6 帧", "view_effects `league_aphelios_q_g_hit`（跟随，画在人物上面；左右对称）", "20 × 26",
     "被定身：目标脚下一圈紫色的月蚀环，几根紫色的光羽从环上竖起来把人钉住，头顶一颗小小的紫色月亮（参考 root_feathers、Q_gravitum_root_indicator、Radiance_Stun_ground_mult）。"
     f"**左右对称**，中间身体留空（{FIG.replace('18 squares wide and 46 tall', '12 wide and 24 tall')}）。",
     V, f"a VIOLET ROOT on a unit, 6 frames, {LR} (an upright figure 12 squares wide and 24 tall stands in the middle, not "
        "drawn): 1 a violet ring 18 squares wide and 5 tall at the feet; 2 four violet light feathers rising from the ring at "
        "mirrored places, 8 squares tall; 3 the feathers 14 squares tall, bright, a small violet moon 4 squares above the head; "
        "4-5 the same pulsing; 6 fading.",
     row(6, 22, 28) + "; centered across, the ring's middle 2 squares above the cell's bottom row."),
    # ---- Infernum's Duskwave
    ("q_i_wave", "Q 荧焰·余晖波：向前喷出的扇形蓝焰（他身上，不跟随），5 帧",
     "view_effects `league_aphelios_q_i_wave`（**不跟随**，画在他身上；有方向：画成朝右，大图表）", "48 × 30",
     "荧焰 Q：从他手上的荧焰往前（右边）喷出一道扇形的蓝色火焰波，从窄到宽向右推出去 45 格，边上是白色和最亮的蓝（参考 Q_infernum_cas_swipe、Q_infernum_flame_shapes、Q_infernum_ground）。"
     "**这张有方向**：画成朝右，扇形的尖在格子左边（他手的位置），往右张开，上下对称。",
     B, "an AZURE FLAME WAVE blasting to the RIGHT, 5 frames, symmetric top to bottom: the fan's point at the LEFT middle (the "
        "hand), opening to the RIGHT to 90 degrees; 1 a white-blue flash 6 squares at the point; 2 a flame fan 20 squares long; "
        "3 the fan 40 squares long and 28 tall at its far end, brightest, white-blue leading edge; 4 the fan 46 squares long, "
        "breaking into blue flame tongues; 5 fading blue embers along the fan.",
     row(5, 50, 32) + "; the fan's point 2 squares from the LEFT edge, vertically centered."),
    ("q_i_hit", "Q 荧焰命中（目标身上），4 帧", "view_effects `league_aphelios_q_i_hit`（跟随，画在人物上面；左右对称）", "14",
     "被蓝焰烧到：一团蓝色火焰往上窜（白芯）。**左右对称**。约 14 格。", B,
     f"an AZURE BURN on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a blue flame burst 10 squares with a white core; 3 "
     "blue flames 14 squares rising; 4 fading embers.",
     row(4, 16, 16) + CENTER),
    # ---- Crescendum's Sentry
    ("q_r_turret", "Q 折镜·驻灵哨卫：地上的哨塔（不跟随，循环），6 帧",
     "view_projectiles `league_aphelios_q_r_turret`（哨塔区域的画面，持续 5 秒；**中心对称**；大图表）", "22 × 22",
     "折镜的哨塔：一个悬在半空的银白色双月牙飞轮在慢慢转，下面地上一圈淡淡的银白光环，飞轮周围有月光的光点（参考 Q_orbitum_ripple、Q_orbitum_blade_erode、Weapon_alphacircle）。"
     "**中心对称**（每一帧转 180 度后和自己一样：红色方游戏会把这张图倒过来）。",
     S, f"a HOVERING SILVER SENTRY, 6 frames, a seamless loop, {PT}: a double-crescent chakram 14 squares across hovering in the "
        "middle, turning 30 degrees a frame (a 180 degree turn over the loop), a white ring hub; a faint silver ground ring "
        "20 squares wide and 6 tall under it, silver motes round it at point-mirrored places.",
     row(6, 24, 24) + CENTER),
    ("q_r_hit", "Q 折镜哨塔击中（目标身上），3 帧", "view_effects `league_aphelios_q_r_hit`（跟随，画在人物上面；左右对称）", "10",
     "哨塔每一下打中：一小团银白色的闪光。**左右对称**。约 10 格。", S,
     f"a SMALL SILVER HIT on a unit, 3 frames, {LR}: 1 a white dot 2 squares; 2 a silver star burst 9 squares; 3 fading motes.",
     row(3, 12, 12) + CENTER),
    # ---- shared
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_aphelios_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "所有子弹打中：一小团月光白的闪光和几颗火星（参考 BA_Rifle_hit、BA_hit_tar_muzzle）。**左右对称**。约 10 格。", M,
     f"a SMALL MOONLIGHT HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a pale flash 7 squares with a white core; 3 the "
     "flash 10 squares, 6 short pale sparks at mirrored places; 4 a few fading motes.",
     row(4, 12, 12) + CENTER),
    ("muzzle", "枪口火光（他身上，跟随），3 帧",
     "view_effects `league_aphelios_m_<武器>`（Claude 按五把武器换色、挪到各自的枪口；画成朝右）", "10 × 8",
     "开枪那一刻枪口的闪光：一团朝右喷出的白绿色火光（画成通碧的绿色，Claude 换色给其他武器）（参考 BA_calibrum_cas_flash、BA_infernum_cas_flash）。"
     "画成朝右：火光的根部在格子左边中间（枪口），往右喷，上下对称。",
     G, "a MUZZLE FLASH blasting to the RIGHT, 3 frames, symmetric top to bottom: 1 a white star 4 squares at the LEFT middle; 2 a "
        "white-green flash 9 squares long shooting right, 2 small side spikes at mirrored places; 3 fading green motes.",
     row(3, 12, 10) + "; the flash's root 1 square from the LEFT edge, vertically centered."),
    ("swap", "换武器的月光（他身上，跟随），5 帧", "view_effects `league_aphelios_swap`（跟随，画在他身上；左右对称）", "26 × 48",
     "换武器（打空换下一把、W 换手）：一道淡蓝白的月光从他身边划一圈，一弯月牙的光闪过他的身体，几片月光羽毛往上飘（参考 Weapon_color_hold、BA_feather_full_erosion、R_symbol_swipe）。"
     f"**左右对称**，中间身体留空（{FIG}），要淡一点，不要盖住他。",
     M, f"a MOONLIGHT SWIRL round a figure, 5 frames, {LR} ({FIG}): 1 pale motes at both sides of the waist; 2 two thin moonlight "
        "arcs sweeping up both sides; 3 the arcs meeting above the head as a crescent 14 squares wide, brightest; 4 the crescent "
        "fading, 6 small light feathers drifting up at mirrored places; 5 the last feathers.",
     row(5, 28, 50) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- Moonlight Vigil
    ("r_cast", "大招 清辉夜凝：施放（他身上，跟随），5 帧",
     "view_effects `league_aphelios_r_cast`（跟随，画在他身上、人物下面；左右对称；大图表）", "36 × 52",
     "大招发动：他身后浮现姐姐 Alune 的淡淡月光身影（只画一个发光的月牙和光晕，不画人），脚下一圈月光的光环，光点往他手上收（参考 R_alune_figure、R_alune_shoulder_flare、R_cas_hand_motes、R_cas_Decal_base）。"
     f"**左右对称**，中间身体留空（{FIG}）。",
     M, f"a MOONLIGHT RISING behind a figure, 5 frames, {LR} ({FIG}): 1 a pale ground ellipse 30 squares wide and 8 tall under the "
        "feet; 2 a large pale crescent moon 24 squares wide rising behind the head; 3 the crescent brightest with a soft halo 34 "
        "wide, pale motes drifting in toward the figure at mirrored places; 4 the motes gathering, the ellipse glowing; 5 fading.",
     row(5, 38, 54) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_moon", "大招：月光弹（朝目标飞，循环），4 帧",
     "view_projectiles `league_aphelios_r_moon`（朝飞行方向转；上下对称；大图表）", "28 × 13",
     "大招的月光：一颗发光的满月（白色的月面、淡蓝的光晕），后面一条长长的月光尾巴和几颗光点（参考 R_mis_moon、R_moonbeam、R_mis_beam_motes、R_mis_brightspot）。**上下对称**。",
     M, f"a GLOWING FULL MOON flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white moon disc 9 squares across with a pale "
        "blue halo 13 squares at the RIGHT end, a moonlight trail 18 squares long behind it, a few pale motes at mirrored places "
        "flickering.",
     row(4, 30, 15) + "; the halo's front 1 square from the RIGHT edge, vertically centered."),
    ("r_boom", "大招：月光爆炸（地上，不跟随），6 帧",
     "view_effects `league_aphelios_r_boom`（不跟随，地上；左右对称；大图表）", "48 × 34",
     "月光在第一个英雄身上炸开：一圈月光冲击环向外推，中间一根月光柱往上冲（白芯），地上一个月牙形的光印（参考 R_explosion_beam、R_explosion_beam_boom、R_explosion_shapes、R_ring_var1、R_Decal_RGB）。**左右对称**。",
     M, f"a MOONLIGHT BURST on the ground, 6 frames, {LR}: 1 a white flash 10 squares on the ground; 2 a pillar of white-blue light 8 "
        "squares wide rising 24 squares, a flat ground ring 24 wide and 8 tall; 3 the pillar 32 tall, the ring 40 wide with a "
        "bright rim, a crescent-moon sigil on the ground inside it; 4 the ring 48 wide, the pillar breaking into motes; 5 the motes "
        "rising, the sigil fading; 6 the last motes.",
     row(6, 50, 36) + "; centered across, the ground ring's middle 5 squares above the cell's bottom row."),
    ("r_hit", "大招命中（目标身上），4 帧", "view_effects `league_aphelios_r_hit`（跟随，画在人物上面；左右对称）", "18",
     "被月光炸到：一团淡蓝白的闪光和几道往外的月光。**左右对称**。约 18 格。", M,
     f"a MOONLIGHT HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 a pale blue burst 12 squares with a white core; 3 "
     "the burst 18 squares with 8 light rays at mirrored places; 4 fading motes.",
     row(4, 20, 20) + CENTER),
    # ---- buffs
    ("mw", "主手武器光环（他脚下，循环），4 帧",
     "view_buffs `league_aphelios_mw_<武器>`（跟随，画在人物下面；左右对称；Claude 按五把武器换色）", "22 × 6",
     "他脚下一圈淡淡的武器光环，告诉玩家现在主手是哪把（画成通碧的绿色，Claude 换成五种颜色）：一个扁的光环，上面一弯小月牙，几颗光点轮流亮。**左右对称**，要淡。",
     G, f"a FAINT WEAPON SIGIL under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse ring 20 squares wide and 5 "
        "tall in dim green, a small crescent mark 4 squares wide at its front middle, 4 brighter motes on the ring at mirrored "
        "places taking turns to light up.",
     row(4, 22, 7) + CENTER),
    ("g_slow", "坠明减速（敌人脚下，循环），4 帧",
     "view_buffs `league_aphelios_g_slow`（跟随，画在人物下面；左右对称；大招坠明的减速 `r_slow` 也用它）", "16 × 5",
     "被坠明打中减速：敌人脚下一圈淡紫色的重力环，几颗紫色光点往下沉。**左右对称**。", V,
     f"a FAINT GRAVITY RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 14 squares wide and 4 tall in "
     "dim violet, 4 violet motes sinking onto it at mirrored places.",
     row(4, 16, 6) + CENTER),
    ("q_s_haste", "断魄加速（他脚下，循环），4 帧",
     "view_buffs `league_aphelios_q_s_haste`（跟随，画在人物下面；左右对称）", "18 × 6",
     "断魄 Q 的移速加成：他脚下两侧几道红色的风痕往后拖。**左右对称**，要淡。", R,
     f"FAINT CRIMSON SPEED STREAKS under a figure's feet, 4 frames, a seamless loop, {LR}: 3 short red streaks at each side of a "
     "16-square gap, flickering between frames.",
     row(4, 20, 7) + CENTER),
    ("cre", "折镜回旋刃层数（他身边环绕，循环），4 帧",
     "view_buffs `league_aphelios_cre`（跟随，画在他身上；左右对称）", "26 × 30",
     "折镜每叠一层：他身边绕着转的小回旋刃（画 3 枚，绕着他的胸口转一圈）（参考 BA_crescendum_trail）。**左右对称**，中间身体留空，要小，不要盖住他。",
     S, f"SMALL SILVER CHAKRAMS ORBITING a figure's chest, 4 frames, a seamless loop, {LR} (an upright slim figure 18 squares wide "
        "stands in the middle, not drawn): three tiny double-blade chakrams 4 squares across on an orbit ellipse 26 wide and 8 "
        "tall around the chest, placed so every frame mirrors left to right (two at the sides, one front or back), moving round "
        "between frames.",
     row(4, 28, 32) + "; the orbit's middle 20 squares above the cell's bottom row."),
]

GROUPS = [
    ("a_cal q_c_* muzzle", ["Aphelios_Base_BA_calibrum_mis", "Aphelios_Base_BA_mis_core_radiance", "Aphelios_Base_BA_calibrum_cas_flash",
                            "Aphelios_Base_BA_calibrum_symbol", "Aphelios_Base_Q_calibrum_mis_02", "Aphelios_Base_Q_core_calibrum"]),
    ("a_sev q_s_* a_grav q_g_*", ["Aphelios_Base_BA_severum_galaxy", "Aphelios_Base_Q_severum_ground_ring", "Aphelios_Base_Q_severum_swirls",
                                  "Aphelios_Base_BA_gravitum_mis_head_trail", "Aphelios_Base_E_Eclips01", "Aphelios_Base_root_feathers"]),
    ("a_inf q_i_* a_cre q_r_*", ["Aphelios_Base_BA_infernum_mis_shape", "Aphelios_Base_Q_infernum_cas_swipe",
                                 "Aphelios_Base_Q_infernum_flame_shapes", "Aphelios_Base_BA_crescendum_trail",
                                 "Aphelios_Base_Q_orbitum_ripple", "Aphelios_Base_Ripper_Shuriken_Highlights"]),
    ("swap r_cast r_moon", ["Aphelios_Base_Weapon_color_hold", "Aphelios_Base_BA_feather_full_erosion", "Aphelios_Base_R_alune_figure",
                            "Aphelios_Base_R_cas_hand_motes", "Aphelios_Base_R_mis_moon", "Aphelios_Base_R_moonbeam"]),
    ("r_boom r_hit a_hit", ["Aphelios_Base_R_explosion_beam", "Aphelios_Base_R_explosion_shapes", "Aphelios_Base_R_ring_var1",
                            "Aphelios_Base_R_Decal_RGB", "Aphelios_Base_BA_Rifle_hit", "Aphelios_Base_BA_hit_tar_muzzle"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point, the magenta
# one the muzzle
SHOTS = [("a_cal", 2, "a_cal：通碧开枪"), ("a_sev", 2, "a_sev：断魄开枪"), ("a_grav", 2, "a_grav：坠明开炮"),
         ("a_inf", 2, "a_inf：荧焰喷射"), ("a_cre", 2, "a_cre：回旋刃扔出"), ("q_grav", 2, "q_g_cast：坠明举炮"),
         ("q_inf", 2, "q_i_wave：余晖波"), ("ult", 3, "r_moon：月光射出")]


def ref_sheet(path):
    S_, LW = 180, 190
    sheet = Image.new("RGBA", (LW + 6 * S_, len(GROUPS) * (S_ + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S_ + 16)
        d.text((6, y + S_ // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                continue
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S_ - 12, S_ - 22))
            sheet.alpha_composite(im, (LW + c * S_ + (S_ - im.width) // 2, y + 16 + (S_ - 16 - im.height) // 2))
            d.text((LW + c * S_ + 4, y + 2), nm.replace("Aphelios_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"厄斐琉斯 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连背上的通碧），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 220), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
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


def done_sheet(path):
    """The delivered effects (assets/source/aphelios/codex_fx/pixel_1x) at 8x, one strip a row, on the arena's dark."""
    src = os.path.join(ROOT, "assets", "source", "aphelios", "codex_fx", "pixel_1x")
    if not os.path.isdir(lp(src)):
        return 0
    rows = []
    for fn in sorted(os.listdir(lp(src))):
        im = Image.open(lp(os.path.join(src, fn))).convert("RGBA")
        rows.append((fn[len("aphelios_fx_"):-4], im.resize((im.width * 8, im.height * 8), Image.NEAREST)))
    W = max(r.width for _, r in rows) + 200
    sheet = Image.new("RGB", (W, sum(r.height + 12 for _, r in rows)), (16, 22, 34))
    d = ImageDraw.Draw(sheet)
    y = 0
    for name, r in rows:
        d.text((6, y + 4), name, fill=(230, 240, 250))
        sheet.paste(r, (200, y), r)
        y += r.height + 12
    sheet.save(path)
    return len(rows)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 残月之肃 厄斐琉斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/aphelios_idle.png`：3/4 正面朝右，清瘦，黑发遮一只眼，灰蓝长外套、宽青绿围巾，"
      f"背上靠着冰蓝色的长枪通碧）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连背上的通碧 {h} 格高、{w} 格宽；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 他有**五把月石武器**，每把在英雄联盟里有自己的颜色，特效照这个配色：**通碧 月绿色**、**断魄 血红色**、**坠明 紫色**、**荧焰 天蓝色火焰**、"
      "**折镜 银白色**；换武器和大招是**淡蓝白的月光**（他姐姐 Alune 的月光）。")
    a("> - 大小对照 `design/aphelios_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/aphelios_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里厄斐琉斯自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住他。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的子弹、光束、月光弹画成朝右，**上下对称**（往左时会上下翻）。"
      "折镜的哨塔要**中心对称**（转 180 度后和自己一样）。荧焰的余晖波和枪口火光画成朝右（有方向）。"
      "其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aphelios_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `aphelios_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 主手武器开火：通碧狙击弹、断魄镰刃弹、坠明重力弹（减速）、荧焰蓝焰弹（溅射）、折镜回旋刃（叠层）；每把 20 发，打空换下一把 | "
      "`a_cal` · `a_sev` · `a_grav` · `a_inf` · `a_cre` · `a_hit` · `muzzle` · `swap` · `mw` · `g_slow` · `cre` |")
    a("| 技能 1 = Q「武器技能」 | 通碧狙杀（月痕 + 追射）、断魄恒月强袭（加速连射）、坠明引力枷锁（定身）、荧焰余晖波（扇形波 + 副手追击）、折镜驻灵哨卫（哨塔） | "
      "`q_c_shot` · `q_c_hit` · `q_c_pop` · `q_s_on` · `q_s_hit` · `q_s_haste` · `off_bolt` · `q_g_cast` · `q_g_hit` · `q_i_wave` · `q_i_hit` · `q_r_turret` · `q_r_hit` |")
    a("| 技能 2 = W「月相轮转」 | 主手和副手交换 | `swap` |")
    a("| 大招「清辉夜凝」 | 射出月光，在第一个英雄处爆炸，再按主手武器加效果 | `r_cast` · `r_moon` · `r_boom` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、子弹、火、烟、火星、星星、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（回旋刃、哨塔的飞轮例外：可以有一圈深银色的边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("月绿（通碧）", GREEN), ("血红（断魄）", RED), ("紫（坠明）", VIOLET), ("天蓝火焰（荧焰）", BLUE),
                        ("银白（折镜）", SILVER), ("月光（换武器、大招）", MOON)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 55000，"
      "荧焰波 45000，哨塔半径 35000，大招爆炸半径 22000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `aphelios_fx_{name}.png`：{title}\n")
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
        a(f"| `aphelios_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_aphelios_fx`（小的）和 `league_aphelios_big`（q_c_shot、q_g_cast、q_i_wave、q_r_turret、r_cast、r_moon、r_boom），tag = 名字（build_aphelios.py 的 views）。")
    a("- `mw` 换色成 mw_cal / mw_sev / mw_grav / mw_inf / mw_cre；`muzzle` 换色并按各武器的枪口位置画成 m_cal / m_sev / m_grav / m_inf / m_cre（开枪那一帧，"
      "攻击开始时播放、跟随，前面空帧补到开枪的时刻）；`q_c_pop` 拆成飞行弹和引爆两个 tag。")
    a("- `q_i_wave` 晚于动作第一刻播放，**is_follow false**（红色方的规则）；`r_boom` 不跟随；`q_s_on`、`q_g_cast`、`r_cast`、`mw`、`g_slow`、`q_s_haste` 画在人物下面（z -1）。")
    a("- 用 `pixel_1x/` 切格（import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="aphelios_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "aphelios_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/ap/fx_ref_ap.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 4, 0), 4, 1)).save(os.path.join(out, "design", "aphelios_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "aphelios_size.png"))
    shots_sheet(os.path.join(out, "design", "aphelios_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    if a.only:
        # a redraw / remainder pack: its own delivery name, and the effects already done as the style to keep
        doc = doc.replace("aphelios_fx_pack_done.zip", f"{a.name}_done.zip")
        done = done_sheet(os.path.join(out, "refs", "done_effects.png"))
        if done:
            doc = doc.replace("\n## 技能方案", f"\n> - **这一包只画这 {len(FX)} 张**；已经交付的 {done} 张特效在 "
                              "`refs/done_effects.png`（8 倍），画风、亮度、像素大小和它们保持一致。\n\n## 技能方案", 1)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"aphelios_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
