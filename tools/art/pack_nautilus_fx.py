#!/usr/bin/env python3
"""Build nautilus_fx_pack.zip: step 3 of Nautilus's sprite - Codex draws his effects (after tools/art/pack_viego_fx.py).

    python tools/art/pack_nautilus_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name nautilus_fx_redo_pack]

The pack (%TEMP%/nt_work/fx/nautilus_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/nautilus/PROMPTS_FX.md), design/nautilus_idle.png (his side-on idle at 8x, as imported),
design/nautilus_size.png (the idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter
beside him), design/nautilus_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Nautilus, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/nt_work/fxref, extracted from Nautilus.wad.client).
The effects are the views the kit binds (tools/kit/build_nautilus.py: view_projectiles q_anchor, r_wave; view_effects
a_hit, p_hit, q_hit, w_hit, e_hit, r_hit, r_up, r_cast, e_wave1-3; view_buffs p_root, e_slow, r_stun, w_on). League's
colours: sea water - foam white, aqua and teal over deep blue-green - the anchor's iron greys and the helmet's bronze;
the shield a teal-green glow. Light and water get no outline; the flying anchor is an object and has one. Red side: the
flying pictures symmetric top to bottom, every picture on a unit and every buff symmetric left to right, the ground
pictures both ways. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "nt_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "nautilus", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_nautilus")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


SEA = "#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8"          # foam and sea light: splashes, waves, flashes
DEEP = "#0E7C86, #0B5D6E, #0A4158, #082A3F"                  # deep water (only inside the water, edges light)
GLOW = "#FFFFFF, #CFFFE9, #7DF5C8, #00E9BE, #03A688"          # Titan's Wrath shield glow (his suit's sea-green seams)
IRON = "#F6E4C8, #B2B0A8, #70747A, #3D4150, #2D3041, #070211"  # the anchor's iron (the design's own greys)
RUST = "#FAAC2A, #DC741C, #A84217, #6F2610"                  # bronze and rust (the anchor's band, rope, helmet)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white "
        "foam core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
SE = f"a sea-foam ramp ({SEA})"
DP = f"a deep water ramp ({DEEP}; its darkest shades only inside the water, every edge in the lighter shades)"
GL = f"a sea-green glow ramp ({GLOW})"
IR = f"the anchor's iron greys ({IRON}; #070211 is its 1-square outline)"
RU = f"bronze and rust ({RUST})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻砸中（目标身上），4 帧", "view_effects `league_nautilus_a_hit`（跟随，画在人物上面；左右对称）", "14",
     "铁锚砸中：一团白色水花往四周溅开（左右对称），中间一道白光，几颗水珠飞出去（参考 BA_Hit_tar_sharp、BA_waterbits）。**左右对称**。约 14 格，居中画。",
     SE,
     f"an ANCHOR SMASH HIT, 4 frames, {LR}: 1 a white flash 5 squares across; 2 a burst of white-aqua water splashing out "
     "12 squares across, white foam in the middle; 3 the splash wider and thinner, water drops flying out at mirrored "
     "places; 4 a few fading drops.",
     row(4, 16, 16) + "; centered in every cell."),
    ("p_hit", "被动排山倒海：禁锢时的一击（目标身上），5 帧", "view_effects `league_nautilus_p_hit`（跟随，画在人物上面；左右对称）",
     "18",
     "排山倒海定身的那一下：一道竖直的水柱从地面往上冲起（居中），四周溅开一圈水花，一圈蓝绿色的光环往外扩（参考 P_land_splash、P_splash_circular）。**左右对称**。约 18 格宽、22 格高，水柱底在格子底部。",
     f"{SE} and {DP}",
     f"a WATER SURGE on a unit, 5 frames, {LR}: 1 a flat white-aqua splash 10 squares wide on the ground; 2 a column of "
     "water 6 squares wide shooting up the middle 20 squares tall, white foam at its top; 3 the column breaking into "
     "foam, a ring of splashes 18 squares wide at the bottom; 4 drops falling at mirrored places; 5 fading drops.",
     row(5, 20, 24) + "; centered across, the splash on the cell's bottom."),
    ("p_root", "被动的禁锢（被定住的人脚下，循环），4 帧", "view_buffs `league_nautilus_p_root`（跟随，画在人物下面；左右对称）",
     "18 × 7",
     "被定在原地：脚下一圈从斜上方看的扁椭圆漩涡水圈，蓝绿色亮边，里面深水色，几条水纹往中间收（参考 Passive_timer_ring、Seafoam）。**左右对称**（水纹每帧换到对称的位置，不画朝一个方向转）。4 帧无缝循环。",
     f"{SE} and {DP}",
     f"a WATER SNARE under a figure's feet, 4 frames, a seamless loop, {LR}: an ellipse of swirling water 16 squares "
     "wide and 5 tall, a bright aqua foam edge, deep water inside, 4 short foam ripples at mirrored places that move "
     "inward each frame.",
     row(4, 20, 9) + "; centered in every cell."),
    # ---- Q Dredge Line
    ("q_anchor", "Q 疏通航道：飞出去的铁锚（飞行中，循环），4 帧",
     "view_projectiles `league_nautilus_q_anchor`（朝飞行方向转，画成朝右飞；上下对称）", "22 × 14",
     "Q 抛出去的铁锚：从侧面看的整把锚朝右飞——右边是锚冠（两只弯钩锚爪**上下对称**地张开），中间是锚杆和一圈红箍，左边拖一段铁链（链环一节一节），锚冠前面一点白色水花（参考 Q_MissileHead、Q_rope_chain）。锚是铁的实物，用定稿的灰色，有 1 格黑描边。**上下对称**。4 帧无缝循环（水花和链环抖动）。约 22 格长、14 格高。",
     f"{IR}, {RU} and {SE}",
     f"a FLYING ANCHOR to the RIGHT, 4 frames, a seamless loop, {TB}: at the right the anchor's crown seen from the side, "
     "its two hooked flukes curving back, one up and one down (mirrored), 12 squares tall; a straight iron shank 10 "
     "squares long to the left with one red-rust band; behind it a short iron chain of 4 links trailing to the left edge; "
     "a little white-aqua foam splashing off the crown's front (mirrored). The anchor and the chain are solid iron with a "
     "1-square #070211 outline; the foam has no outline. The foam and the chain links jiggle each frame.",
     row(4, 24, 16) + "; the crown's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_hit", "Q 钩中（被钩中的英雄身上），4 帧", "view_effects `league_nautilus_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "铁锚钩中：一团大的白色水花炸开，一圈铁链环形的水纹往外（参考 Q_land_splash、Q_splash_circular）。**左右对称**。约 16 格，居中画。",
     SE,
     f"an ANCHOR HOOK HIT, 4 frames, {LR}: 1 a white flash 6 squares across; 2 a big burst of white-aqua water 14 "
     "squares across; 3 a thin foam ring 16 squares across, drops at mirrored places; 4 fading drops.",
     row(4, 18, 18) + "; centered in every cell."),
    # ---- skill2: W Titan's Wrath + E Riptide
    ("w_on", "W 泰坦之怒：护盾（他身上，循环），4 帧", "view_buffs `league_nautilus_w_on`（跟随，画在人物上面；左右对称）", "30 × 42",
     "护盾期间：他周围一层细的蓝绿色发光外壳（竖的椭圆，只画外圈），外圈上几道流动的光纹（参考 W_shield_glow、W_Nautilus_Skin04_W_Shield、W_blue_green_light）。**中间留空、左右对称**。4 帧无缝循环。约 30 格宽、42 格高。",
     GL,
     f"a SEA-GREEN SHIELD round a figure, 4 frames, a seamless loop, {LR}, its inside EMPTY: an upright ellipse outline "
     "28 squares wide and 40 tall, 1-2 squares thick, glowing sea-green with white glints at mirrored places that move to "
     "new mirrored places each frame.",
     row(4, 32, 44) + "; the shell centered in every cell, its bottom 1 square above the cell's bottom."),
    ("w_hit", "W 护盾期间的普攻余波（目标周围），4 帧", "view_effects `league_nautilus_w_hit`（跟随；左右对称）", "20 × 10",
     "护盾时普攻会伤到目标周围：目标脚下一圈蓝绿色的电光水波往外扩（从斜上方看的扁椭圆）（参考 W_EnergyStreak、W_ping_light）。**左右对称**。约 20 格宽、10 格高。",
     f"{GL} and {SE}",
     f"a GLOWING SPLASH RING round a unit, 4 frames, {LR}: 1 a sea-green flash 6 squares wide; 2 a sea-green ellipse ring "
     "14 squares wide and 6 tall with short sparks; 3 the ring 20 wide, thinner; 4 fading sparks at mirrored places.",
     row(4, 22, 12) + "; centered in every cell."),
    ("e_wave1", "E 暗流涌动：第一波（他脚下，地面），5 帧",
     "view_effects `league_nautilus_e_wave1`（施法时，不跟随，画在人物下面；上下左右都对称）", "36 × 14",
     "他捶地后地面炸起三波浪：第一波是一圈小的、从斜上方看的扁椭圆水浪，浪尖白色泡沫，里面深水色（参考 E_Splash_Ring、E_Cas_Puddle_Ripples、E_explosion_tar_SplashFlip）。**上下左右都对称**。约 36 格宽、14 格高。",
     f"{SE} and {DP}",
     f"a GROUND WAVE (the first and smallest), 5 frames, {BOTH}: an elliptical ring of crashing water seen from above at "
     "an angle, white foam crests along it; 1 a ring 14 squares wide; 2 24 wide, foam spraying up; 3 30 wide; 4 36 wide "
     "and 14 tall, breaking; 5 foam fading.",
     row(5, 38, 16) + "; centered in every cell."),
    ("e_wave2", "E 暗流涌动：第二波（地面），5 帧",
     "view_effects `league_nautilus_e_wave2`（施法时，不跟随，画在人物下面；上下左右都对称）", "52 × 20",
     "第二波：同样的浪圈，更大一圈（参考同上）。**上下左右都对称**。约 52 格宽、20 格高。",
     f"{SE} and {DP}",
     f"a GROUND WAVE (the second), 5 frames, {BOTH}: an elliptical ring of crashing water seen from above at an angle, "
     "white foam crests; 1 a ring 26 squares wide; 2 38 wide, foam spraying up; 3 46 wide; 4 52 wide and 20 tall, "
     "breaking; 5 foam fading.",
     row(5, 54, 22) + "; centered in every cell."),
    ("e_wave3", "E 暗流涌动：第三波（地面），5 帧",
     "view_effects `league_nautilus_e_wave3`（施法时，不跟随，画在人物下面；上下左右都对称）", "68 × 26",
     "第三波：最大的一圈，就是 E 的范围（半径 32 格）（参考同上）。**上下左右都对称**。约 68 格宽、26 格高。",
     f"{SE} and {DP}",
     f"a GROUND WAVE (the third and largest), 5 frames, {BOTH}: an elliptical ring of crashing water seen from above at "
     "an angle, white foam crests; 1 a ring 36 squares wide; 2 52 wide, foam spraying up; 3 62 wide; 4 68 wide and 26 "
     "tall, breaking; 5 foam fading.",
     row(5, 70, 28) + "; centered in every cell."),
    ("e_hit", "E 冲中（每个被浪打中的人身上），4 帧", "view_effects `league_nautilus_e_hit`（跟随；左右对称）", "12",
     "被浪冲中：一团小水花往上溅（参考 E_impact_flash、E_water_bolts）。**左右对称**。约 12 格，居中画。",
     SE,
     f"a WAVE HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 water splashing up 10 squares wide; 3 drops at "
     "mirrored places; 4 fading drops.",
     row(4, 14, 14) + "; centered in every cell."),
    ("e_slow", "E 的减速（被减速的人脚下，循环），4 帧", "view_buffs `league_nautilus_e_slow`（跟随，画在人物下面；左右对称）",
     "16 × 6",
     "被暗流减速：脚下一圈浅浅的水洼，泡沫亮边，几条水纹往中间收。**左右对称**。4 帧无缝循环。",
     f"{SE} and {DP}",
     f"a PUDDLE SLOW under a figure's feet, 4 frames, a seamless loop, {LR}: a shallow water ellipse 14 squares wide and 4 "
     "tall with a white-aqua foam edge, 4 short ripples at mirrored places drifting inward each frame.",
     row(4, 18, 8) + "; centered in every cell."),
    # ---- R Depth Charge
    ("r_cast", "R 深海冲击：起手（他脚下），5 帧", "view_effects `league_nautilus_r_cast`（施法时，不跟随，画在人物下面；左右对称）",
     "28 × 12",
     "R 砸地：他脚下炸起一圈白色水花和尘土，中间一道青色的光往下钻进地里（参考 R_impact_flash、R_groundDust、R_greenRing）。**左右对称**，只在脚边。约 28 格宽、12 格高。",
     f"{SE} and {DP}",
     f"a DEPTH CHARGE LAUNCH at a figure's feet, 5 frames, {LR}: 1 a flat white-aqua flash 12 squares wide on the ground; "
     "2 water and dust bursting out to both sides 24 squares wide; 3 a teal ring 28 wide; 4 thinning; 5 fading drops.",
     row(5, 30, 14) + "; centered across, the bottom on the cell's bottom."),
    ("r_wave", "R 深海冲击：地下冲过去的冲击波（飞行中，循环），4 帧",
     "view_projectiles `league_nautilus_r_wave`（朝飞行方向转，画成朝右走；上下对称）", "24 × 14",
     "冲击波从地下朝目标冲过去：一道朝右走的水浪隆起，前端白色浪花高高翻起，后面拖一串越来越小的水花和裂开的地面（参考 R_waterspike32、R_aqua_nova、Crater）。朝右走。**上下对称**（游戏会把它转向；往左走时上下翻）。4 帧无缝循环。约 24 格长、14 格高。",
     f"{SE} and {DP}",
     f"a SHOCKWAVE RUSHING to the RIGHT, 4 frames, a seamless loop, {TB}: at the right a crest of white-aqua water "
     "spikes 12 squares tall bursting up and down (mirrored), deep water in its middle, a trail of smaller splashes 12 "
     "squares long behind it to the left (mirrored); the spikes and splashes change each frame.",
     row(4, 26, 16) + "; the crest's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_up", "R 冲击波掀起沿途的敌人（身上），4 帧", "view_effects `league_nautilus_r_up`（跟随；左右对称）", "14 × 18",
     "沿途被掀起：脚下一根水柱把人顶起来（竖直居中），水花往两边溅（参考 R_waterspike32）。**左右对称**。约 14 格宽、18 格高。",
     SE,
     f"a WATER SPIKE under a unit, 4 frames, {LR}: 1 a white splash 8 squares wide on the ground; 2 a spike of water 6 "
     "squares wide shooting up 16 squares tall in the middle; 3 the spike breaking into foam; 4 fading drops.",
     row(4, 16, 20) + "; centered across, the splash on the cell's bottom."),
    ("r_hit", "R 命中目标（目标身上，大），6 帧", "view_effects `league_nautilus_r_hit`（跟随，画在人物上面；左右对称）", "30 × 40",
     "深海冲击命中：目标脚下炸起一根巨大的水柱，把人冲上天（中间留出人的位置，水柱在人的两边和身后往上冲），顶上白色浪花散开，地面一圈蓝绿色冲击环（参考 R_aqua_nova、R_waterspike32、R_greenRing、R_impact_flash）。**左右对称**。约 30 格宽、40 格高。",
     f"{SE} and {DP}",
     f"a GREAT WATER ERUPTION round a unit, 6 frames, {LR}, the unit's place in the middle (12 x 24 squares, from the "
     "bottom) EMPTY: 1 a white flash 14 squares wide on the ground and a teal ring 24 wide; 2 two thick columns of water "
     "bursting up both sides 36 squares tall, deep water inside, white foam edges; 3 the columns' tops crashing into white "
     "foam over the middle; 4 water falling at mirrored places; 5 drops and thin foam; 6 fading drops.",
     row(6, 32, 42) + "; centered across, the ground ring's bottom on the cell's bottom."),
    ("r_stun", "R 的眩晕（头顶，循环），4 帧", "view_buffs `league_nautilus_r_stun`（跟随；左右对称）", "16 × 7",
     "被晕住：头顶绕着一圈扁扁的水泡和小鱼形状的光点（参考 waterdots）。**左右对称**（光点每帧换到对称的位置）。4 帧无缝循环。约 16 格宽、7 格高。",
     SE,
     f"a DAZE RING of bubbles over a head, 4 frames, a seamless loop, {LR}: a flat ellipse 16 squares wide and 5 tall of "
     "small white-aqua bubbles, 4 bright bubbles on it at mirrored places that step to new mirrored places each frame.",
     row(4, 18, 9) + "; centered in every cell."),
]

GROUPS = [
    ("a_hit p_*", ["Nautilus_Base_BA_Hit_tar_sharp", "Nautilus_Base_BA_waterbits", "Nautilus_Base_P_land_splash",
                   "Nautilus_Base_P_splash_circular", "Nautilus_Base_Passive_timer_ring", "Nautilus_Base_Seafoam_1"]),
    ("q_*", ["Nautilus_Base_Q_MissileHead", "Nautilus_Base_Q_rope_chain_07", "Nautilus_Base_Q_land_splash",
             "Nautilus_Base_Q_splash_circular"]),
    ("w_*", ["Nautilus_Base_W_shield_glow", "Nautilus_Base_W_Nautilus_Skin04_W_Shield",
             "Nautilus_Base_W_blue_green_light_01", "Nautilus_Base_W_EnergyStreak_2x2"]),
    ("e_*", ["Nautilus_Base_E_Splash_Ring", "Nautilus_Base_E_Cas_Puddle_Ripples", "Nautilus_Base_E_explosion_tar_SplashFlip",
             "Nautilus_Base_E_Splash_4x2", "Nautilus_Base_E_water_bolts", "Nautilus_Base_E_impact_flash"]),
    ("r_*", ["Nautilus_Base_R_aqua_nova_04", "Nautilus_Base_R_waterspike32", "Nautilus_Base_R_greenRing",
             "Nautilus_Base_R_groundDust", "Nautilus_Base_R_impact_flash", "Nautilus_Base_Crater_01"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 4, "a_hit：锚砸到的地方（打中画在目标身上）"),
         ("skill", 5, "q_anchor：锚从手里飞出去"),
         ("skill2", 3, "e_wave1-3：捶地，浪从脚下往外"),
         ("ult", 5, "r_cast / r_wave：砸地，冲击波从脚下往前"),
         ("idle", 1, "w_on / p_root / e_slow：站位点")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Nautilus_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def idle_1x():
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = idle_1x()
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
    d.text((8, 36), f"诺提勒斯 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (the imported sheet), his standing point as a cyan cross."""
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    px = sp.w // 2 + PAD
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 330), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 深海泰坦 诺提勒斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/nautilus_idle.png`：游戏里的侧身待机，8 倍，连背上的锚 {h} 行、{w} 格宽）。")
    a("> - 大小对照 `design/nautilus_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/nautilus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里诺提勒斯自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**深海的水 = 白色泡沫 + 浅青、海蓝绿，里面是深蓝绿**；W 的护盾是他身上缝线那种海绿色的光；飞出去的锚是定稿的灰色铁锚。")
    a("> - **特效要亮**：每团水花都要用最亮的几档和白色泡沫芯，暗底上一眼能看见；深水色只在水的里面，**边缘一定是亮的泡沫和浅青**。")
    a("> - **围着人的护盾、水柱只画外圈和两边，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的锚和冲击波（`q_anchor`、`r_wave`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻；锚爪一上一下对称张开）。"
      "画在人身上、脚下、头顶的（打中、禁锢、护盾、减速、晕眩、掀起）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；"
      "地上的 `e_wave1-3` 上下左右都对称；`r_cast` 左右对称。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nautilus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `nautilus_fx_pack_done.zip`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「排山倒海」 | 抡锚砸；打英雄时把它定在原地（之后 6 秒不再触发） | `a_hit` · `p_hit` · `p_root` |")
    a("| 技能 1 = Q「疏通航道」 | 抛出铁锚，钩中第一个敌方英雄，把两人拉到一起 | `q_anchor` · `q_hit` |")
    a("| 技能 2 = W「泰坦之怒」+ E「暗流涌动」 | 护盾（期间普攻伤到目标周围）；捶地，三波浪往外，冲中的人减速 | `w_on` · `w_hit` · `e_wave1` · `e_wave2` · `e_wave3` · `e_hit` · `e_slow` |")
    a("| 大招 = R「深海冲击」 | 砸地，冲击波从地下冲向一名敌方英雄，沿途的人被掀起，目标被巨大的水柱冲上天再晕住 | `r_cast` · `r_wave` · `r_up` · `r_hit` · `r_stun` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水花、光、浪、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**；只有飞出去的铁锚（实物）有 1 格黑描边。")
    a("- **要亮**：每个形状都有白色泡沫或最亮一档的芯；深水色只在里面。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海水泡沫（水花、浪尖、闪光）", SEA), ("深水（水的身体：深色只在里面）", DEEP),
                        ("海绿光（W 护盾）", GLOW), ("铁锚的灰（定稿，#070211 是描边）", IRON), ("铜锈（锚上的红箍和绳）", RUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "Q 飞 85000，W 余波半径 18000，E 半径 32000，R 射程 80000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `nautilus_fx_{name}.png`：{title}\n")
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
        a(f"| `nautilus_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_nautilus_fx`（小的）和 `league_nautilus_big`（r_hit、r_wave、e_wave1-3），tag = 名字（build_nautilus.py 的 views）。")
    a("- `q_anchor` 是直线飞的（line），`y_offset` 3000；`r_wave` 是追踪弹（homing）：画面开头补一帧空的（追踪弹第一 tick 朝上）。")
    a("- `e_wave1-3`、`r_cast` 不跟随、画在人物下面（z -1）；`p_root`、`e_slow` 是脚下的 buff（z -1）；`w_on`、`r_stun` 画在人物上面（z 3），所以 `w_on` 中间必须是空的。")
    a("- 用 `pixel_1x/` 切格（import_viktor / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="nautilus_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Nautilus's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    fig = idle_1x()
    Image.fromarray(np.repeat(np.repeat(fig, 8, 0), 8, 1)).save(os.path.join(out, "design", "nautilus_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "nautilus_size.png"))
    shots_sheet(os.path.join(out, "design", "nautilus_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"nautilus_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
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
