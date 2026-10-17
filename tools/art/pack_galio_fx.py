#!/usr/bin/env python3
"""Build galio_fx_pack.zip: step 3 of Galio's sprite - Codex draws his effects (after tools/art/pack_braum_fx.py).

    python tools/art/pack_galio_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name galio_fx_redo_pack]

The pack (%TEMP%/gl_work/fx/galio_fx_pack, zipped into --out, default dist/galio_packs) holds PROMPTS.md (also written to
assets/source/galio/PROMPTS_FX.md), design/galio_idle.png (his dense 3/4 front design at 3x), design/galio_size.png (the
1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter beside him),
design/galio_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Galio, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/gl_work/fxref, extracted from Galio.wad.client's base-skin particles by %TEMP%/gl_work/fx/fx_ref_gl.py).
The effects are the views the kit binds (tools/kit/build_galio.py: view_projectiles q_wind; view_effects a_hit, p_hit,
p_ring, w_ps, q_burst, q_hit, q_tornado, e_dash, e_hit, w_charge, w_burst, r_cast, r_land, r_hit; view_buffs w_taunt,
r_shield). League's colours: pale cyan-white wind, blue petricite magic (the shield, the passive's nova), Demacian gold
(the ult, the taunt's sigil), stone dust; light gets no outline. Red side: the windblasts (q_wind) symmetric top to
bottom (they turn with the flight), every other picture symmetric left to right.
He is shown at 85 % in game (hd.rs SIZES): about 36 x 44 game px with his wings.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gl_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "galio", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_galio")
HD_FRONT = os.path.join(ROOT, "assets", "source", "galio", "hd", "front.png")   # the approved dense design
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


WIND = "#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6"               # wind: white core to sky blue
MAGIC = "#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80"     # petricite magic: white to deep blue
GOLD = "#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12"               # Demacian gold light
DUST = "#F2EEE4, #D6CDBB, #B3A68E, #8A7D66"                        # stone dust and pebbles
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
WD = f"a wind ramp ({WIND})"
MG = f"a blue magic ramp ({MAGIC})"
GD = f"a gold ramp ({GOLD})"
DS = f"a stone dust ramp ({DUST})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_galio_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "石拳打中：目标身上白色冲击一闪，一圈淡淡的碎石尘往外弹（参考 BA_BlastShapes、P_ImpactPuffs）。**左右对称**。约 12 格，居中画。",
     f"{WD} and {DS}",
     f"a STONE-FIST HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a pale cyan-white burst 10 squares across "
     "with a white core; 3 a ring of grey-beige dust puffs 12 squares across with 4 small pebbles flying out at mirrored "
     "places; 4 a few fading dust specks.",
     row(4, 14, 14) + "; centered in every cell."),
    ("p_hit", "被动 巨像重击：砸中的目标（目标身上），5 帧", "view_effects `league_galio_p_hit`（跟随，画在人物上面；左右对称）", "18",
     "被动重击砸中：目标身上蓝色的魔法冲击炸开（白芯，蓝色光圈），几块碎石往外飞（参考 P_Nova_Ground、P_Pebbles）。**左右对称**。约 18 格。",
     f"{MG} and {DS}",
     f"a BLUE MAGIC SLAM HIT on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 a blue magic burst 12 squares "
     "across, white core; 3 the burst 18 squares across with a bright blue rim, 4 pebbles flying out at mirrored places; "
     "4 the rim breaking into blue sparks; 5 fading sparks and dust.",
     row(5, 20, 20) + "; centered in every cell."),
    ("p_ring", "被动 巨像重击：他身前地上的冲击波（地上，不跟随），5 帧", "view_effects `league_galio_p_ring`（不跟随，画在人物下面；左右对称）",
     "34 × 12",
     "双拳砸地的冲击波：地上一圈蓝色的魔法冲击环往外扩（从斜上方看的扁椭圆），里面一圈尘土（参考 P_Ring_Shockwave）。**左右对称**。范围约 34 格宽。",
     f"{MG} and {DS}",
     f"a GROUND SHOCK RING, 5 frames, {LR}: 1 a white flash on the ground 8 squares wide; 2 a flat blue ring 20 squares "
     "wide and 7 tall, 2 squares thick, white inner edge; 3 the ring 30 wide and 10 tall with grey-beige dust puffs on "
     "its inner edge; 4 the ring 34 wide and 12 tall, thinning, dust rising a little; 5 a faint broken ring and dust.",
     row(5, 36, 14) + "; centered in every cell."),
    ("w_ps", "杜朗护盾 被动：魔法护盾一闪（他身上），5 帧", "view_effects `league_galio_w_ps`（跟随，画在人物上面；左右对称）", "40 × 46",
     "被动护盾生成：他周围一层蓝色的护盾光一闪（大椭圆的外圈，参考 W_ShieldRing、Wings_Glow），**中间人形位置留空**，几点白光在边上闪。**左右对称**。",
     MG,
     f"a SHIELD SHIMMER round a big figure, 5 frames, {LR}, its inside EMPTY (a clear upright area 34 squares wide and "
     "40 tall): 1 a faint blue rim at the figure's sides; 2 the rim of an ellipse 40 squares wide and 46 tall, 1-2 "
     "squares thick, white highlights at the top; 3 the rim brightest, 4 white sparkles on it at mirrored places; 4 the "
     "rim fading from the bottom up; 5 a few fading sparkles.",
     row(5, 42, 48) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- Q Winds of War
    ("q_wind", "Q 战争罡风：飞出去的两道风（朝落点飞，循环），4 帧",
     "view_projectiles `league_galio_q_wind`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 12",
     "翅膀扇出的两道风合在一起往前飞：两股白青色的风刃上下各一，前端尖、后面拖着风痕（参考 Q_Mis_Front、Q_Mis_Tail、Q_Mis_Dirt_Sides）。**上下对称**。",
     WD,
     f"TWIN WIND BLASTS flying to the RIGHT, 4 frames, a seamless loop, {TB}: two curved white-cyan wind blades, one above "
     "and one below the middle line, 8 squares long, their points meeting at the front (right); behind them wispy wind "
     "streaks 6 squares long, flickering in turn.",
     row(4, 18, 14) + "; the blades' tips 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_burst", "Q 风落地炸开（落点，不跟随），5 帧", "view_effects `league_galio_q_burst`（不跟随，画在人物上面；左右对称）", "30 × 22",
     "风落地的一下：地上一圈白青色的风圈炸开（扁椭圆），往上冲起几股风，夹着一点尘土（参考 Q_Land_Nova、Q_BlastStreaks）。**左右对称**。地上圈约 30 格宽。",
     f"{WD} and {DS}",
     f"a WIND BURST on the ground, 5 frames, {LR}: 1 a white flash 8 squares; 2 a flat white-cyan wind ring 20 squares "
     "wide and 7 tall; 3 the ring 30 wide and 10 tall with 4 upward wind streaks 12 squares tall at mirrored places; "
     "4 the streaks higher and thinner, a little dust at the ring; 5 fading wisps.",
     row(5, 32, 24) + "; centered across, the ring's middle 5 squares above the cell's bottom."),
    ("q_tornado", "Q 龙卷风（落点，不跟随，持续 2 秒），8 帧", "view_effects `league_galio_q_tornado`（不跟随，画在人物上面；左右对称；8 帧铺满 2 秒）",
     "26 × 36",
     "落点留下一个竖着的龙卷风，转 2 秒：下窄上宽的漏斗形，白青色的风一圈圈绕着，夹着几块碎石和尘土（参考 Q_Tar_Tornado_BurstWind、Q_Tornado_swirl）。**左右对称**（旋转靠一圈圈风带的亮暗交替往上移表现，每帧逐格左右对称）。第 1 帧刚升起，第 8 帧散开。",
     f"{WD} and {DS}",
     f"an UPRIGHT TORNADO, 8 frames, {LR}: a funnel narrow at the bottom (8 squares) and wide at the top (26 squares), "
     "36 squares tall, made of white-cyan wind bands; the bright bands move up one step each frame (the spin shown by "
     "light and dark bands, every frame mirrored); a few grey pebbles and dust specks at mirrored places; 1 the funnel "
     "half grown; 2-7 full; 8 breaking into wisps.",
     row(8, 28, 38) + "; centered across, the funnel's tip on the cell's bottom row."),
    ("q_hit", "Q 风打中（目标身上），4 帧", "view_effects `league_galio_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "风刃打中目标：白青色的风交叉一闪（一个 X 形的风痕），散成几缕风。**左右对称**。约 14 格。",
     WD,
     f"a WIND SLASH HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 an X of two white-cyan wind slashes 12 "
     "squares across; 3 the X 14 squares across, curling wisps at its ends; 4 fading wisps.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- E Justice Punch
    ("e_dash", "E 正义冲拳：冲锋时脚下（他身上，跟着他），4 帧", "view_effects `league_galio_e_dash`（跟随，画在人物下面；左右对称）", "30 × 12",
     "冲出去时脚下扬起的尘土和风：地面上一团扁扁的尘土往两边散，夹着白青色的风痕（参考 E_Dirt_Takeoff、E_Ground_Slide）。**左右对称**。",
     f"{DS} and {WD}",
     f"a DUST KICK-UP under a charging figure's feet, 4 frames, {LR}: 1 a flat dust puff 14 squares wide and 4 tall; "
     "2 the puff 24 wide and 7 tall, white-cyan wind streaks at both sides; 3 the dust 30 wide spreading out, 4 pebbles; "
     "4 thinning dust.",
     row(4, 32, 14) + "; centered across, the puff's middle 3 squares above the cell's bottom."),
    ("e_hit", "E 冲拳打中（被击飞的人身上），5 帧", "view_effects `league_galio_e_hit`（跟随，画在人物上面；左右对称）", "20",
     "冲拳打中、把人打飞：目标身上金白色的冲击一闪，一圈蓝色光环，往上冲起几道风（击飞，参考 E_Hit_Flash、E_Tar_BlastShapes、E_Tar_Complete）。**左右对称**。约 20 格。",
     f"{GD}, {MG} and {WD}",
     f"a KNOCK-UP PUNCH HIT on a unit, 5 frames, {LR}: 1 a white-gold flash 6 squares; 2 a gold star burst 12 squares "
     "across with a white core; 3 a blue ring 18 squares across round it and 4 white-cyan wind streaks shooting upward "
     "at mirrored places; 4 the streaks higher, the ring fading; 5 fading sparks.",
     row(5, 22, 26) + "; centered across, the burst's middle 9 squares above the cell's bottom."),
    # ---- W Shield of Durand
    ("w_charge", "W 杜朗护盾：蓄力的护盾（他身上，跟着他），4 帧", "view_effects `league_galio_w_charge`（跟随，画在人物上面；左右对称；蓄力约 0.8 秒）",
     "44 × 50",
     "蓄力时罩住他的蓝色护盾：一层蓝色光罩（只画外圈和几道光纹，**中间人形位置留空**），外圈上几点白光一闪，脚下一圈尘土（参考 W_ShieldRing、W_Cast_Dust、W_wisps）。**左右对称**。",
     f"{MG} and {DS}",
     f"a BLUE SHIELD DOME round a big crouching figure, 4 frames, {LR}, its inside EMPTY (a clear upright area 36 "
     "squares wide and 42 tall): 1 the dome's rim forming, an ellipse 44 squares wide and 50 tall, 1 square thick; 2 the "
     "rim 2 squares thick with white highlights at the top and sides, a ring of dust at its foot; 3 the rim brightest, "
     "4 white sparkles moving up it at mirrored places; 4 the same, sparkles one step higher.",
     row(4, 46, 52) + "; centered across, the dome's bottom on the cell's bottom row."),
    ("w_burst", "W 放开：嘲讽冲击波（他脚下，不跟随），5 帧", "view_effects `league_galio_w_burst`（不跟随，画在人物上面；左右对称）", "52 × 26",
     "护盾一放，蓝色冲击波往四周扩开（地上一圈大的扁椭圆环），往上冒几道蓝白的光，碎石和尘土往外飞（参考 W_ShieldRing、W_rock_debris、W_Dust_Balls）。**左右对称**，中间人形位置留空。范围约 52 格宽。",
     f"{MG} and {DS}",
     f"a BLUE SHOCKWAVE from a figure, 5 frames, {LR}, the middle above the ring EMPTY (a clear upright area 30 squares "
     "wide and 20 tall): 1 a white flash ring at the feet 16 squares wide; 2 a blue ring 34 squares wide and 12 tall, 2 "
     "squares thick, with 4 blue-white light streaks rising at mirrored places; 3 the ring 52 wide and 18 tall, rocks and "
     "dust flying outward at mirrored places; 4 the ring breaking into blue sparks; 5 fading dust.",
     row(5, 56, 28) + "; centered across, the ring's middle 6 squares above the cell's bottom."),
    # ---- R Hero's Entrance
    ("r_cast", "R 英雄登场：引导（他身上，跟着他，约 2 秒），6 帧", "view_effects `league_galio_r_cast`（跟随，画在人物上面；左右对称；6 帧铺满引导时间）",
     "40 × 52",
     "准备飞向队友时的金色光：他周围金色的光点和光带往上升，脚下一圈金色光环（参考 R_Cas_Glow、R_Cas_Hover_Ringflare），**中间人形位置留空**。**左右对称**。",
     f"{GD} and {WD}",
     f"a RISING GOLDEN LIGHT round a big figure, 6 frames, {LR}, its inside EMPTY (a clear upright area 32 squares wide "
     "and 44 tall): a flat gold ring at the feet 36 squares wide and 10 tall; gold light streaks and motes rising along "
     "both sides at mirrored places, each frame one step higher; 1 the ring forming; 2-5 the ring bright, motes rising; "
     "6 the ring and streaks brightest (the take-off).",
     row(6, 42, 54) + "; centered across, the ring's middle 4 squares above the cell's bottom."),
    ("r_land", "R 落地砸地（落点，不跟随），6 帧", "view_effects `league_galio_r_land`（不跟随，画在人物下面；左右对称）", "46 × 30",
     "从天上砸下来的一下：地上金色和蓝色的大冲击环炸开，地面裂开几道发光的裂纹，尘土冲天（参考 R_Impact_Ground_Cracks、R_Tar_Impact、R_Ground_Indicator 的金色翅膀圈）。**左右对称**。范围约 46 格宽。",
     f"{GD}, {MG} and {DS}",
     f"a HEAVY LANDING on the ground, 6 frames, {LR}: 1 a white-gold flash 14 squares wide; 2 a flat gold ring 28 "
     "squares wide and 9 tall, a blue inner ring; 3 the rings 46 wide and 14 tall, glowing gold cracks radiating from the "
     "middle, dust clumps rising 14 squares at mirrored places; 4 the dust higher, the rings thinning; 5 cracks glowing "
     "dimmer, dust settling; 6 faint cracks.",
     row(6, 48, 32) + "; centered across, the rings' middle 7 squares above the cell's bottom."),
    ("r_hit", "R 击飞（被打中的人身上），4 帧", "view_effects `league_galio_r_hit`（跟随，画在人物上面；左右对称）", "16",
     "被落地冲击击飞：目标身上金色的冲击一闪，几道光往上冲（参考 R__Tar_Stylized_Hit、R_centerFlare）。**左右对称**。约 16 格。",
     f"{GD} and {WD}",
     f"a GOLDEN UPWARD HIT on a unit, 4 frames, {LR}: 1 a white-gold flash 6 squares; 2 a gold star 12 squares across; "
     "3 3 gold streaks shooting upward at mirrored places, the star fading; 4 fading motes.",
     row(4, 18, 24) + "; centered across, the star's middle 8 squares above the cell's bottom."),
    # ---- buffs
    ("w_taunt", "W 嘲讽（被嘲讽的人头顶，循环），4 帧", "view_buffs `league_galio_w_taunt`（跟随，画在人物上面；左右对称）", "12 × 8",
     "被嘲讽的人头顶：一个小小的金色德玛西亚翅膀徽记（两只展开的小翅膀中间一个盾形，参考 R_Ground_Indicator 的翅膀图案），一闪一闪。**左右对称**。画在格子上部。",
     GD,
     f"a GOLD WINGED SIGIL over a head, 4 frames, a seamless loop, {LR}: two small spread wings 4 squares each round a "
     "small shield shape 4 squares wide, 12 squares wide in all, pulsing brighter and dimmer, two white sparkles.",
     row(4, 14, 48) + "; the sigil's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty."),
    ("r_shield", "R 给队友的护盾（队友身上，循环），4 帧", "view_buffs `league_galio_r_shield`（跟随，画在人物上面；左右对称）", "22 × 30",
     "英雄登场给队友的护盾：一层蓝金色的护盾光罩罩住队友（普通英雄大小，只画外圈，**中间人形位置留空**），外圈上金色光点慢慢转（亮暗交替）。**左右对称**。",
     f"{MG} and {GD}",
     f"a SHIELD BUBBLE round a normal-size figure, 4 frames, a seamless loop, {LR}, its inside EMPTY (a clear upright "
     "area 16 squares wide and 24 tall): the rim of an ellipse 22 squares wide and 30 tall, 1 square thick, blue with "
     "white highlights at the top, 4 small gold motes on it at mirrored places taking turns to brighten.",
     row(4, 24, 32) + "; centered across, the ellipse's bottom on the cell's bottom row."),
]

GROUPS = [
    ("a_hit p_*", ["Galio_Base_BA_BlastShapes", "Galio_Base_BA_bluering", "Galio_Base_P_Nova_Ground",
                   "Galio_Base_P_Ring_Shockwave", "Galio_Base_P_ImpactPuffs_2x2", "Galio_Base_P_Pebbles_4x4"]),
    ("q_*", ["Galio_Base_Q_Mis_Front", "Galio_Q_Mis_Tail", "Galio_Q_Mis_Dirt_Sides_V03", "Galio_Q_Tar_Tornado_BurstWind_V04",
             "Galio_Base_Q_Tornado_swirl", "Galio_Base_Q_Land_Nova"]),
    ("e_*", ["Galio_Base_E_Dirt_Takeoff_Specs", "Galio_Base_E_Ground_Slide", "Galio_Base_E_Hit_Flash",
             "Galio_Base_E_Tar_BlastShapes", "Galio_E_Tar_Complete", "Galio_Base_E_CloudRing"]),
    ("w_*", ["Galio_W_ShieldRing", "Galio_Base_W_Cast_Dust_v03", "Galio_Base_W_rock_debris", "Galio_Base_W_wisps_blend",
             "Galio_Base_W_Dust_Balls", "Galio_Base_Wings_Glow_Mult"]),
    ("r_*", ["Galio_Base_R_Cas_Glow", "Galio_Base_R_Cas_Hover_Ringflare", "Galio_Base_R_Impact_Ground_Cracks_V03",
             "Galio_Base_R_Tar_Impact", "Galio_Base_R_Ground_Indicator_Outside_v02", "Galio_Base_R__Tar_Stylized_Hit"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：出拳打到的地方（画在目标身上）"),
         ("attack2", 4, "p_hit / p_ring：双拳砸地"),
         ("skill", 3, "q_wind：翅膀扇出风"),
         ("skill2", 4, "e_hit / e_dash：冲拳"),
         ("w_charge", 1, "w_charge：蓄力护盾罩住他"),
         ("w_burst", 3, "w_burst：放开"),
         ("ult_loop", 1, "r_cast：引导"),
         ("ult_land", 2, "r_land：落地砸地")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Galio_Base_", "").replace("Galio_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def idle_1x():
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
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
    d.text((8, 36), f"加里奥 {fig.shape[1]}×{fig.shape[0]} 格（连翅膀，100%；游戏里显示 85%），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
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
    a("# 正义巨像 加里奥：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/galio_idle.png`：游戏里的 3/4 正面待机，金色翅膀高高竖起）。他在游戏里是**高清**的（PPU：每个游戏格子里 2×2 个细像素，这张图是高清造型放大 3 倍），1 倍图连翅膀 {h} 格高、{w} 格宽，**游戏里显示成 85%（约 36 × 44 格）**；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/galio_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/galio_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里加里奥自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**白青色的风、蓝色的禁魔石魔法光（护盾、被动冲击）、德玛西亚的金色光（大招、嘲讽徽记）、石头的尘土和碎石**。")
    a("> - **特效要亮**：每道光、每股风都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的护盾、光罩、冲击环只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的风 `q_wind` 画成朝右，**上下对称**（往左放时会上下翻）。"
      "其余所有画面（打中、身上、脚下、头顶、地上的冲击环、龙卷风）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `galio_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `galio_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「巨像重击」 | 石拳；每几秒一次双拳砸地的范围魔法伤害；杜朗护盾被动的魔法护盾 | `a_hit` · `p_hit` · `p_ring` · `w_ps` |")
    a("| 技能 1 = Q「战争罡风」 | 扇出两道风，落地炸开并留下龙卷风 | `q_wind` · `q_burst` · `q_tornado` · `q_hit` |")
    a("| 技能 2 = E「正义冲拳」+ W「杜朗护盾」 | 冲锋击飞第一个英雄；蓄力护盾减伤，放开时嘲讽周围敌人 | `e_dash` · `e_hit` · `w_charge` · `w_burst` · `w_taunt` |")
    a("| 大招 = R「英雄登场」 | 给苦战的队友护盾，引导后飞过去，落地击飞敌人 | `r_cast` · `r_shield` · `r_land` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、风、魔法、冲击环、尘土都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("风", WIND), ("蓝色魔法光", MAGIC), ("金色光", GOLD), ("尘土和碎石", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "被动范围半径 16000，Q 落点半径 15000、龙卷风半径 13000，W 半径 26000，R 落地半径 22000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `galio_fx_{name}.png`：{title}\n")
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
        a(f"| `galio_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_galio_fx`（小的）和 `league_galio_big`（p_ring、q_burst、q_tornado、w_charge、w_burst、r_land），tag = 名字（build_galio.py 的 views）。")
    a("- `q_wind` 是投射物（抛物线），画面朝飞行方向转；`p_ring`、`q_burst`、`q_tornado`、`w_burst`、`r_land` 不跟随；`w_taunt` 头顶（z 3）；`w_charge`、`w_ps`、`r_cast`、`r_shield` 中间必须是空的；`q_tornado` 8 帧铺满 2 秒，`r_cast` 6 帧铺满 2 秒，`w_charge` 循环到蓄力结束。")
    a("- 用 `pixel_1x/` 切格（import_kassadin / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="galio_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "galio_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/gl_work/fx/fx_ref_gl.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 3, 0), 3, 1)).save(os.path.join(out, "design", "galio_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "galio_size.png"))
    shots_sheet(os.path.join(out, "design", "galio_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"galio_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
