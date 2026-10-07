#!/usr/bin/env python3
"""Build lillia_fx_pack.zip: step 3 of Lillia's sprite - Codex draws her effects (after tools/art/pack_seraphine_fx.py).

    python tools/art/pack_lillia_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name lillia_fx_redo_pack]

The pack (%TEMP%/ll_work/fx/lillia_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/lillia/PROMPTS_FX.md), design/lillia_design.png (8x), design/lillia_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside her), design/lillia_shots.png (the action
frames from tools/art/rig_lillia.py at 4x, with the points the seed and the pictures on her start from) and refs/lol_fx_ref.png (League's own
particle textures for Lillia, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/ll_work/fxref, extracted from Lillia.wad.client).
The effects are the views the kit binds (tools/kit/build_lillia.py: view_projectiles e_seed; view_effects a_hit, q_spin,
q_hit, e_hit, e_land, w_mark, w_land, w_hit, w_sweet, r_cast, wake; view_buffs prance (p1-p4), drowsy, sleep, e_slow)
and the add-on's dust (league_lillia_dust, addons/league_lillia). League's colours: her dream dust blue-violet with pink
and cyan sparkles, Q's blooms pink-violet with gold flash spikes, W's rings violet and teal, the swirlseed orange with a
blue swirl, R's lullaby blue dream swirls. Light gets no outline. Red side: the seed symmetric top to bottom, every
picture on a unit and every buff symmetric left to right, the ground pictures both ways; q_spin and r_cast are played
on her (q_spin at the action's first tick, following her; r_cast later, not following) and both are drawn left-right
symmetric, so nothing rides in her action frames. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ll_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "lillia", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "lillia_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


DREAM = "#FFFFFF, #E6E8FF, #A8B0FF, #6A6AE8, #3A2C9A"             # her dream dust, the sleep (her hooves' violet)
PINK = "#FFFFFF, #FFE0F0, #FF9AD0, #F04AA8, #B8075E"              # the blooms (her hair)
CYAN = "#FFFFFF, #D8FBFF, #8AE8FF, #56C8FE, #1E8AC8"              # sparkles, the bough's blossom, W's edge
GOLD = "#FFFFFF, #FFF6C0, #FBD70B, #E8A010, #8A5A10"              # the lantern's light, the flash spikes
SEED = "#FFFFFF, #FFE0B0, #FFA840, #FF7F00, #D84A0A"              # the swirlseed (her fawn colours)
LEAF = "#E8FFD0, #B1DC43, #3E8A2A, #036A2E"                        # petals and leaves (accents only)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, dust, petals, sparkles or rings, BRIGHT colours (each shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
DR = f"a blue-violet dream ramp ({DREAM})"
PK = f"a pink bloom ramp ({PINK})"
CY = f"a cyan sparkle ramp ({CYAN})"
GD = f"a gold lantern-light ramp ({GOLD})"
SD = f"an orange seed ramp ({SEED})"
LF = f"leaf-green accents ({LEAF}) used sparingly"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_lillia_a_hit`（跟随，画在人物上面；左右对称）", "14",
     "莉莉娅用枝条打中：目标身上炸开一朵粉紫色的小花光，几片花瓣和蓝紫色梦尘往外散（参考 ba_glow、mystic_butterfly 花瓣、w_hit_flash）。**左右对称**。约 14 格，居中画。",
     f"{PK} and {DR}",
     f"a BLOSSOM HIT, 4 frames, {LR}: 1 a white-pink 4-point star 6 squares across at the center; 2 a pink-violet burst "
     "10 squares across with 4 small petals flying out at mirrored places; 3 the petals farther, blue-violet dust motes "
     "round it; 4 a few fading motes.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- Q Blooming Blows
    ("q_spin", "Q 飞花挞：她转枝条时脚下绽开的花环（地上，跟着她，画在人物下面），6 帧",
     "view_effects `league_lillia_q_spin`（施法第一刻在她身上播放，跟随，画在人物下面；上下左右都对称）", "56 × 22",
     "莉莉娅抡枝条转一圈：脚下从斜上方看的扁椭圆花环一下绽开——外圈是一道亮粉紫色的扫光（Q 的外圈，打中会多一下真实伤害），内圈淡一点，环上撒花瓣和金色闪光（参考 q_outerring、q_indicator、q_slashult、q_hit_flash_spikes、mystic_butterfly）。"
     "**上下左右都对称**，**中间留空**（她站在中间）。外圈是技能范围（半径 26 格）：最大一帧约 56 格宽、22 格高；内圈约 24 格宽。",
     f"{PK}, {DR} and {GD}",
     f"a BLOOMING RING on the ground round her, seen from above at an angle, 6 frames, {BOTH}, its middle EMPTY: 1 a thin "
     "white-pink ellipse 24 squares wide; 2 an outer ring 44 squares wide, 2 squares thick, bright pink with a violet "
     "outer edge, a fainter inner ring 24 squares wide; 3 the outer ring 54 squares wide and 20 tall, brightest, 8 petals "
     "and 4 gold flash glints on it at mirrored places; 4 the rings thinner, the petals flying outward; 5 the rings "
     "breaking into petals and dust; 6 a few fading petals.",
     row(6, 58, 24) + "; centered in every cell."),
    ("q_hit", "Q 打中（每个被打中的人身上），4 帧", "view_effects `league_lillia_q_hit`（跟随；左右对称）", "16",
     "被飞花挞打中：人身上一道横着的金白色闪刺（像花开时的闪光）加一团粉紫色花光，几颗梦尘（参考 q_hit_flash_spikes_yellow、q_sparks、w_hit_flash）。**左右对称**。约 16 格，居中画。",
     f"{PK}, {GD} and {DR}",
     f"a BLOOM STRIKE HIT, 4 frames, {LR}: 1 a white-gold horizontal flash spike 14 squares wide and 2 tall through the "
     "center; 2 the spike with a pink-violet burst 9 squares across at its middle; 3 the burst opening into 6 petals at "
     "mirrored places, blue-violet motes; 4 fading motes.",
     row(4, 18, 18) + "; centered in every cell."),
    # ---- E Swirlseed
    ("e_seed", "E 流涡种：抛出去的种子（飞行中，循环），4 帧",
     "view_projectiles `league_lillia_e_seed`（抛物线飞行；上下对称）", "8 × 8",
     "莉莉娅抛出的流涡种：一颗圆圆的橙色种子，上面有一道蓝色的光，外面一圈淡淡的金光，后面拖两颗梦尘光点（参考 seed_tx_cm 的颜色、e_glow、e_mote）。"
     "**上下对称**（不要画旋涡线，旋涡不对称；用一圈一亮一暗的光表现在转）。4 帧无缝循环。约 8 格。",
     f"{SD}, {CY} and {DR}",
     f"a SWIRLSEED in flight, 4 frames, a seamless loop, {TB}: a round orange seed 5 squares across with a lit top-and-"
     "bottom-symmetric shine, a thin cyan band across its middle, a soft gold glow round it, 2 small blue-violet motes "
     "trailing to the LEFT at mirrored heights; the glow and the band brighten and dim frame to frame (no spinning lines).",
     row(4, 10, 10) + "; centered in every cell."),
    ("e_land", "E 种子落地炸开（落点地上，画在人物下面），5 帧",
     "view_effects `league_lillia_e_land`（落点上，不旋转，画在人物下面；上下左右都对称）", "20 × 8",
     "种子落地：地上一圈从斜上方看的扁椭圆橙色光环炸开，几片叶子和蓝紫色梦尘往外散（参考 e_backdrop、e_energystreaksadd、lillia_e_ground）。"
     "**上下左右都对称**。这是种子的范围（半径 9 格）：约 20 格宽、8 格高。",
     f"{SD}, {DR} and {LF}",
     f"a SEED BURST on the ground seen from above at an angle, 5 frames, {BOTH}: 1 a bright white-orange ellipse 6 "
     "squares wide; 2 an orange ring 14 squares wide, 4 leaves and 4 violet motes at mirrored places; 3 the ring 20 "
     "squares wide and 8 tall, thinner; 4 the ring breaking into motes; 5 a few fading motes.",
     row(5, 22, 10) + "; centered in every cell."),
    ("e_hit", "E 打中（被种子砸中的人身上），4 帧", "view_effects `league_lillia_e_hit`（跟随；左右对称）", "14",
     "被种子砸中：人身上一团橙金色的光炸开，一圈蓝紫色梦尘（参考 e_glow、e_mote）。**左右对称**。约 14 格，居中画。",
     f"{SD} and {DR}",
     f"a SEED HIT, 4 frames, {LR}: 1 a white-orange flash 6 squares across; 2 an orange burst 10 squares across with a "
     "thin violet ring round it; 3 the ring wider, 6 motes at mirrored places; 4 fading motes.",
     row(4, 16, 16) + "; centered in every cell."),
    ("e_slow", "E 减速（被减速的人脚下，循环），4 帧", "view_buffs `league_lillia_e_slow`（画在脚下；左右对称）", "16 × 6",
     "被种子减速：脚下一团贴地的蓝紫色梦雾，几颗小光点一闪一闪（参考 e_buff_swirls 的颜色、smoke）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。",
     DR,
     f"a SLOWING DREAM MIST under a figure's feet, 4 frames, a seamless loop, {LR}: a flat ellipse of blue-violet mist "
     "14 squares wide and 4 tall, paler in the middle, 4 small sparkles at mirrored places; it pulses and the sparkles "
     "twinkle.",
     row(4, 18, 8) + "; centered in every cell."),
    # ---- W Watch Out! Eep!
    ("w_mark", "W 惊惶木：要砸下去的地方的预警圈（地上，画在人物下面），6 帧",
     "view_effects `league_lillia_w_mark`（落点上，不旋转，画在人物最下面；上下左右都对称）", "46 × 18",
     "W 蓄力 0.5 秒时地上的预警：一圈紫色的扁椭圆圈（范围），正中间一个小的亮青色椭圆（甜点，砸中这里伤害 3 倍），一圈细光从外圈往里收（倒计时）（参考 w_decal、w_decal_edge、w_circle_normal、w_timer_ring）。"
     "**上下左右都对称**。外圈约 46 格宽、18 格高（半径 22 格），中间甜点约 9 格宽、4 格高。",
     f"{DR} and {CY}",
     f"a WARNING CIRCLE on the ground seen from above at an angle, 6 frames, {BOTH}: an elliptical ring 44 squares wide "
     "and 16 tall, 1 square thick, violet with a faint violet fill inside, and a bright cyan ellipse 9 squares wide and 4 "
     "tall at the center; a thin white-cyan ring shrinks from the outer ring toward the center: 44 wide in frame 1, then "
     "36, 28, 20, 14 and 10 wide in frame 6; the center ellipse brightens each frame.",
     row(6, 48, 20) + "; centered in every cell."),
    ("w_land", "W 砸地（落点地上，画在人物下面），6 帧",
     "view_effects `league_lillia_w_land`（落点上，不旋转，画在人物下面；上下左右都对称）", "48 × 20",
     "枝条砸下来：地上一圈紫青色的冲击波扩开，中间一朵大的白粉色闪光，几片花瓣和碎光往外飞（参考 w_shockwave、w_inner_ring、w_hit_flash、w_core、w_swipe_mult）。"
     "**上下左右都对称**。最大一帧约 48 格宽、20 格高。",
     f"{DR}, {CY} and {PK}",
     f"a SLAM SHOCKWAVE on the ground seen from above at an angle, 6 frames, {BOTH}: 1 a white flash ellipse 10 squares "
     "wide at the center; 2 a ring 24 squares wide, 2 squares thick, violet with a teal outer edge, a pink-white flash "
     "inside; 3 the ring 38 squares wide, 8 petals and sparks flying out at mirrored places; 4 the ring 46 squares wide "
     "and 18 tall, thinner; 5 breaking into sparks; 6 a few fading sparks.",
     row(6, 50, 22) + "; centered in every cell."),
    ("w_hit", "W 打中（被砸中的人身上），4 帧", "view_effects `league_lillia_w_hit`（跟随；左右对称）", "16",
     "被 W 砸中：人身上一团紫色的光炸开，一圈青色细环（参考 w_hit_flash、w_shockwave）。**左右对称**。约 16 格，居中画。",
     f"{DR} and {CY}",
     f"a SLAM HIT, 4 frames, {LR}: 1 a white-violet 4-point star 7 squares across; 2 a violet burst 11 squares across "
     "with a thin cyan ring; 3 the ring wider, 6 sparks at mirrored places; 4 fading sparks.",
     row(4, 18, 18) + "; centered in every cell."),
    ("w_sweet", "W 甜点暴击（正中间被砸中的人身上），5 帧", "view_effects `league_lillia_w_sweet`（跟随；左右对称）", "22",
     "W 正中甜点：人身上一颗很亮的金白色大星光炸开，八道金光往外射，一圈粉紫色花光（参考 w_hit_flash、q_hit_flash_spikes_yellow、w_core）。**左右对称**。约 22 格，居中画。",
     f"{GD}, {PK} and {DR}",
     f"a CRITICAL SLAM BURST, 5 frames, {LR}: 1 a white 8-point star 10 squares across; 2 a gold-white burst 16 squares "
     "across with 8 long gold rays and a pink-violet ring; 3 the rays longest (22 squares across), a white core; 4 the "
     "rays breaking into sparkles and petals; 5 fading sparkles.",
     row(5, 24, 24) + "; centered in every cell."),
    # ---- R Lilting Lullaby
    ("r_cast", "R 夜阑谣：她身边的催眠曲光（施法后，她身上），6 帧",
     "view_effects `league_lillia_r_cast`（施法后播放、不跟随，画在人物上面；左右对称）", "44 × 52",
     "莉莉娅唱起夜阑谣：她身边升起几道蓝色的梦境漩涡光带（左右镜像），脚下一圈蓝紫色光，许多梦尘光点和小星星往上飘（参考 r_stun_swirl、r_tar_rootcylinder、r_groundlight、r_indicator 的配色）。"
     "**左右对称**，**中间留空**（她站在中间，光只画在身边和外面）。6 帧：亮起、最亮、飘散。约 44 格宽、52 格高，底边是她的脚底。",
     f"{DR}, {CY} and {PK}",
     f"a LULLABY AURA round her, 6 frames, {LR}, the figure's place EMPTY (the middle 22 x 44 squares): 1 a blue-violet "
     "ellipse glow 30 squares wide on the ground at the bottom; 2 two blue dream ribbons rising from it at the left and "
     "the right (mirrored), curling outward, 8 motes; 3 the ribbons reaching the top, brightest, cyan and pink sparkles "
     "and tiny stars drifting up at mirrored places; 4 the ribbons thinning, the motes higher; 5 fading; 6 a few motes.",
     row(6, 46, 54) + "; centered across, the ground glow on the cell's bottom."),
    ("drowsy", "R 困倦（被催眠的英雄头顶，循环），4 帧", "view_buffs `league_lillia_drowsy`（跟随，画在人物上面；左右对称）", "18 × 10",
     "困倦：头顶飘着一团淡蓝紫色的梦雾，几颗小光点慢慢往下沉（参考 e_buff_swirls、r_sandflecks）。**左右对称**。4 帧无缝循环。约 18 格宽、10 格高。",
     DR,
     f"a DROWSY HAZE over a head, 4 frames, a seamless loop, {LR}: a soft blue-violet haze 16 squares wide and 6 tall, "
     "6 small motes at mirrored places drifting down 1 square a frame and fading in again at the top.",
     row(4, 20, 12) + "; centered across, the haze in the cell's top half."),
    ("sleep", "R 昏睡（睡着的英雄头顶，循环），4 帧", "view_buffs `league_lillia_sleep`（跟随，画在人物上面；左右对称）", "18 × 14",
     "昏睡：头顶一个发光的蓝紫色梦泡泡，泡泡里一弯小月亮（月亮朝上开口，左右对称的“碗”形），泡泡两边各一颗小星星一闪一闪（参考 r_stun_swirl、r_portal_tex 的配色）。**左右对称**。4 帧无缝循环（泡泡轻轻胀缩）。约 18 格宽、14 格高。",
     f"{DR}, {GD} and {CY}",
     f"a SLEEP BUBBLE over a head, 4 frames, a seamless loop, {LR}: a round blue-violet glowing bubble outline 10 squares "
     "across with a pale inside, a small gold crescent inside it opening UPWARD (a symmetric bowl shape), one small cyan "
     "star on each side of the bubble (mirrored); the bubble swells 1 square and back, the stars twinkle.",
     row(4, 20, 16) + "; centered in every cell."),
    ("wake", "R 被打醒（醒来的英雄身上），5 帧", "view_effects `league_lillia_wake`（跟随；左右对称）", "18",
     "睡着的人被打醒：梦泡泡“啪”地破开，蓝白色的光炸开，碎成梦尘散掉（参考 w_hit_flash、r_sandflecks）。**左右对称**。约 18 格，居中画。",
     f"{DR} and {CY}",
     f"a DREAM POP, 5 frames, {LR}: 1 a round blue-violet bubble outline 10 squares across; 2 the bubble bursting into a "
     "white-cyan 8-point flash 14 squares across; 3 bubble shards and motes flying out at mirrored places; 4 the motes "
     "farther and fading; 5 a few fading motes.",
     row(5, 20, 20) + "; centered in every cell."),
    # ---- the passive: Dream-Laden Bough + Prance
    ("dust", "被动 梦满枝：中了梦尘的敌人身上（循环），4 帧",
     "view_buffs `league_lillia_dust`（附加包里的梦尘 buff；跟随；左右对称）", "22 × 30",
     "中了梦尘：敌人身边绕着一圈细细的蓝紫色梦尘光点和几颗粉色小星光（参考 p_buff_swirls、e_mote、lens-rainbow 的配色）。"
     "**左右对称**，**中间留空**（人在中间，只画外面一圈飘着的光点）。4 帧无缝循环（光点轻轻上下浮动、一闪一闪）。约 22 格宽、30 格高。",
     f"{DR} and {PK}",
     f"DREAM DUST round a figure, 4 frames, a seamless loop, {LR}, the figure's place EMPTY (the middle 14 x 26 squares): "
     "10 small blue-violet motes and 4 tiny pink star glints placed round the empty middle at mirrored places, more near "
     "the head; each frame different mirrored pairs brighten and they drift 1 square up and down.",
     row(4, 24, 32) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("prance", "被动 腾跃：加速时脚下（循环），4 帧", "view_buffs `league_lillia_p1`–`p4`（同一张，画在脚下；左右对称）", "26 × 8",
     "腾跃加速：莉莉娅的蹄子下飘起几片粉色花瓣和蓝紫色梦尘，左右各两道短短的速度光（左右镜像）（参考 mystic_butterfly 花瓣、trail10）。"
     "**左右对称**。4 帧无缝循环。约 26 格宽、8 格高。",
     f"{PK}, {DR} and {LF}",
     f"PRANCING PETALS under a figure's hooves, 4 frames, a seamless loop, {LR}: a faint blue-violet ground glow 20 "
     "squares wide and 3 tall, 4 pink petals and 4 motes rising from it at mirrored places, two short pale speed streaks "
     "at each side (mirrored); the petals rise 1 square a frame and fade in again at the bottom.",
     row(4, 28, 10) + "; centered across, the glow on the cell's bottom."),
]

GROUPS = [
    ("attack / Q", ["Lillia_Base_BA_Glow_Test", "Lillia_Base_Mystic_Butterfly", "Lillia_Base_Q_OuterRing",
                    "Lillia_Base_Q_Indicator", "Lillia_Base_Q_Hit_Flash_Spikes_Yellow", "Lillia_Base_Q_Sparks"]),
    ("E", ["Lillia_Base_Seed_TX_CM", "Lillia_Base_E_Glow", "Lillia_Base_E_Mote", "Lillia_Base_E_Backdrop",
           "Lillia_Base_E_EnergyStreaksAdd", "Lillia_E_Ground"]),
    ("W", ["Lillia_Base_W_Decal", "Lillia_Base_W_Decal_Edge", "Lillia_Base_W_Circle_Normal",
           "Lillia_Base_W_Shockwave", "Lillia_Base_W_Inner_Ring", "Lillia_Base_W_Hit_Flash"]),
    ("R", ["Lillia_Base_R_Stun_Swirl", "Lillia_Base_R_Tar_RootCylinder", "Lillia_Base_R_GroundLight_01",
           "Lillia_Base_R_Indicator", "Lillia_Base_R_Portal_Tex", "Lillia_Base_R_SandFlecks"]),
    ("dust / prance", ["Lillia_Base_P_Buff_Swirls", "Lillia_Base_E_Buff_Swirls", "Lillia_Base_Lens-Rainbow",
                       "Lillia_Base_Trail10", "Lillia_Base_W_Core", "Lillia_Base_Smoke"]),
]
# where the pictures start: (tag, frame, what, mark): "feet" = the standing point, "blossom" = the bough's cyan tip
SHOTS = [("skill", 3, "q_spin / q_hit: 她转一圈（花环在脚下）", "feet"),
         ("skill2", 3, "e_seed: 枝头（种子从这里抛出）", "blossom"),
         ("ult", 3, "r_cast / dust / prance: 站位点", "feet")]


def ref_sheet(path):
    S, LW = 180, 110
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm.lower() + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Lillia_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"莉莉娅 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The action frames (tools/art/rig_lillia.py) at 4x, each picture's starting point as a cyan cross: the standing
    point, or the bough's cyan blossom."""
    import design_lillia as DL
    import rig_lillia as R
    P = R.Parts()
    F = R.build(P)
    blossom = np.array(DL.hx(DL.LETTERS["j"]), np.uint8)
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, mark in SHOTS:
        f = F[tag][k - 1]
        ys, xs = np.nonzero(f[..., 3] > 0)
        if mark == "feet":
            pts = [(R.PIVOT[0], R.SOLES)]
        else:
            by, bx = np.nonzero((f[..., :3] == blossom).all(-1) & (f[..., 3] > 0))
            k = int(np.argmax((bx - R.PIVOT[0]) ** 2 + (by - R.SOLES) ** 2))      # the tip: the farthest cyan square
            pts = [(float(bx[k]) + 0.5, float(by[k]) + 0.5)]
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
    a("# 含羞蓓蕾 莉莉娅：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/lillia_design.png`，8 倍，{h} 行、{w} 格宽，连枝头到蹄子）。")
    a(f"> - 大小对照 `design/lillia_size.png`：定稿造型放大 4 倍，蹄子在红线上，上面是 10 格一段的刻度，右边是原版斗士。莉莉娅 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/lillia_shots.png`：定稿动作（4 倍），青色十字是特效的起点（枝头、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里莉莉娅自己的特效贴图（不少是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**梦尘是蓝紫色带粉色、青色小星光；Q 的花是粉紫色，闪光是金白色；W 的圈是紫色和青色；E 的种子是橙色带一道蓝光；R 是蓝色的梦境漩涡**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的光环、花环、梦尘只画外圈，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的种子 `e_seed` 画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "画在人身上、头顶、脚下的（打中、困倦、昏睡、被打醒、梦尘、减速、腾跃、夜阑谣）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；"
      "地上的 `q_spin`、`e_land`、`w_mark`、`w_land` 上下左右都对称。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `lillia_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`lillia_fx_done.zip`）放在 outputs 里，或放在 `outputs/lillia-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「梦满枝」「腾跃」 | 用枝条打；技能打中的敌人中梦尘（持续掉血），她回血；技能打中加速 | `a_hit` · `dust` · `prance` |")
    a("| 技能 1 = Q「飞花挞」 | 抡枝条转一圈，外圈多打一下真实伤害 | `q_spin` · `q_hit` |")
    a("| 技能 2 = E「流涡种」→ W「惊惶木」 | 抛出种子砸中减速；接着蓄力人立，往前方一个圈砸下去，正中甜点 3 倍伤害 | `e_seed` · `e_land` · `e_hit` · `e_slow` · `w_mark` · `w_land` · `w_hit` · `w_sweet` |")
    a("| 大招 = R「夜阑谣」 | 唱催眠曲：中了梦尘的敌方英雄先困倦减速，再昏睡，被打会醒并受伤 | `r_cast` · `drowsy` · `sleep` · `wake` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、梦尘、花瓣、星光、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("蓝紫梦尘", DREAM), ("粉色花光", PINK), ("青色星光", CYAN), ("金色灯光、闪光", GOLD),
                        ("橙色种子", SEED), ("叶绿点缀", LEAF)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "Q 半径 26000（内圈 12000），种子范围 9000，W 半径 22000（甜点 4000））。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `lillia_fx_{name}.png`：{title}\n")
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
        a(f"| `lillia_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 种子从枝头抛出（出手帧第 3 帧，青色十字）；抛物线弹道，画面开头补几帧空的，让种子离开枝头再出现。")
    a("- 没有烘进动作帧的特效：`q_spin` 第一 tick 在她身上播放、跟随，`r_cast` 晚于第一 tick、`is_follow` 为 false，两张都逐格左右对称；"
      "`q_spin`、`e_land`、`w_land` 画在人物下面（z -1），`w_mark` 更下面（z -2）。")
    a("- `prance` 一张绑 view_buffs 的 `p1`–`p4`（tag `prance`）；`dust` 只在附加包的数据里绑 view_buffs `league_lillia_dust`（主包的梦尘没有 buff）。")
    a("- 用 `pixel_1x/` 切格（import_twitch 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "量每张的平均亮度和最亮的一成，和包里别的英雄比。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="lillia_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Lillia's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "lillia_design.png"))
    shape = size_sheet(os.path.join(out, "design", "lillia_size.png"))
    shots_sheet(os.path.join(out, "design", "lillia_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"lillia_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
