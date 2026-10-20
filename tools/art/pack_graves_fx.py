#!/usr/bin/env python3
"""Build graves_fx_pack.zip: step 3 of Graves's sprite - Codex draws his effects (pack_karthus_fx.py's way).

    python <scratchpad>/fx_ref_gv.py          # League's particle textures -> C:/t/gv_work/fxref (Riot's art, local only)
    python tools/art/pack_graves_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name graves_fx_redo_pack]

The pack (C:/t/gv_work/fx/graves_fx_pack, zipped into --out, default dist/graves_packs) holds PROMPTS.md (also written to
assets/source/graves/PROMPTS_FX.md), design/graves_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/graves_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/graves_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Graves grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_graves.py): view_projectiles a_shot, q_shell, w_can, r_shell;
view_effects a_hit (a_spread and q_hit2 too), q_hit (r_hit2 too), q_blast, w_smoke, e_dust, r_hit, r_blast; view_buffs
e_grit, w_slow - and three muzzle blasts drawn into his own frames by tools/art/rig_graves.py (a_flash on the shot of
attack / attack2, q_flash on Q's, r_flash on R's): the client never mirrors an effect picture, so a picture with a front
and a back that rides on him goes into his frames, which the game does mirror (the skill's rule "Both sides").
League's colours: gunfire orange and gold with white cores, grey gunsmoke, Smoke Screen's dark grey-green cloud,
Quickdraw's brown dust and True Grit's gold. Every picture is symmetric left to right but the projectiles (drawn
pointing right and symmetric top to bottom: the game turns them) and the three muzzle blasts (pointing right: baked).
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
TMP = "C:/t/gv_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "graves", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_graves")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "graves_fx_pack"
SIZE_LABEL = "格雷福斯"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFFFF, #FFF6C8, #FFD86A, #FFA42E, #F0641E, #A8301A"     # gunfire: white core, gold, orange, deep red edge
SMOKE = "#ECE8DE, #C4BEB2, #96907F, #6A655B, #44413B"             # grey gunsmoke
CLOUD = "#C8D2C4, #96A296, #6C786E, #4A544C, #2E3632, #1C2220"   # Smoke Screen's dark grey-green cloud
DUST = "#EEDCB4, #CCAE80, #A2845A, #74593C, #4C3A28"              # Quickdraw's dust
GOLD = "#FFFFFF, #FFF2B0, #FFD24A, #E0A020, #A86A10"              # True Grit's gold, the shells' brass
STEEL = "#FFFFFF, #D8D8DC, #9C9CA4, #62626C, #34343C, #1A1A20"   # the shells' and the canister's steel
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around fire, flashes, smoke, dust or rings (a solid object - a shell, a canister - keeps a 1-square "
        "near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must "
        "read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FI = f"a gunfire ramp ({FIRE})"
SM = f"a grey gunsmoke ramp ({SMOKE})"
CL = f"a dark grey-green smoke ramp ({CLOUD})"
DU = f"a dust ramp ({DUST})"
GO = f"a gold ramp ({GOLD})"
ST = f"a steel ramp ({STEEL})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("POINTING RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to the way it "
      "flies, so shot to the left it is turned upside down)")
RIGHT = ("POINTING RIGHT (it comes out of the shotgun's muzzle, which is at the cell's LEFT edge, middle row; the game "
         "draws it into his own frames, which it mirrors on the red side)")
CENTER = "; centered in every cell."
HIM = ("the gunslinger stands in the middle, not drawn: 38 squares from his hair to the ground, 26 squares wide without "
       "his shotgun")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the shotgun (passive New Destiny + the attack)
    ("a_flash", "普攻：霰弹枪口的火光（烤进他的开枪帧，朝右），3 帧",
     "rig_graves.py 烤进 attack / attack2 的开枪帧（第 3 帧起，枪口处；朝右，不对称）", "16 × 12",
     "霰弹枪开火：枪口喷出一团扇形的橙黄色火光，中间白芯，前面几道金色的弹丸火星往前飞散，后面一点灰烟（参考 cast_muzzleflash、"
     "muzzle_flash_01、sparks）。**朝右画**（枪口在格子左边正中），火光往右张开成扇形。3 帧：1 最亮最大、2 火光变小、弹丸火星飞远、3 只剩"
     "一缕灰烟和两三点火星。",
     f"{FI} and {SM}",
     "A SHOTGUN MUZZLE BLAST, 3 frames, " + RIGHT + ": 1 a fan of orange-gold fire opening to the right from the cell's left "
     "edge (8 squares long, 9 tall at its open end), a white core 3 squares at the muzzle, 5 short gold pellet streaks (1x2 "
     "squares) flying ahead of it; 2 the fire smaller (5 squares), the streaks further right, a small grey smoke puff at "
     "the muzzle; 3 only a fading grey smoke puff (4 squares) and 2 orange sparks.",
     row(3, 16, 12) + "; the muzzle at the left edge of each cell, on its middle row."),
    ("a_shot", "普攻：飞出去的弹丸（弹道，转向飞行方向），2 帧",
     "view_projectiles `league_graves_a_shot`（追踪弹，跟着方向转；上下对称；循环）", "8 × 4",
     "霰弹的弹丸：一颗白热的小弹丸，后面拖着一条短短的橙色光迹（参考 ba_bullet_trail、ba_mis_shell）。**朝右画、上下对称**。2 帧循环。",
     FI,
     "A HOT PELLET, 2 frames, a seamless loop, " + TB + ": a white-hot pellet 2 squares at the cell's right end and an orange "
     "streak 5 squares long behind it (to the left), 1-2 squares thick, fading to its tail; frame 2 the streak a square "
     "shorter and brighter.",
     row(2, 8, 4) + "; the pellet on the cell's middle rows."),
    ("a_hit", "普攻：弹丸打中（也用在扇形和 Q 爆炸打中的人身上），3 帧",
     "view_effects `league_graves_a_hit` / `a_spread` / `q_hit2`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "弹丸打中：一团橙白色的小火花，几粒金色的碎屑往外溅，一小团灰烟（参考 hit_flash、hit_sparks、ba_impactpuffs）。**左右对称**。",
     f"{FI} and {SM}",
     "A PELLET IMPACT, 3 frames, " + LR + ": 1 a white-orange flash 5 squares across with 4 short rays; 2 the flash 7 across, "
     "6 gold sparks (1 square) flying out at mirrored places, a small grey puff; 3 only the grey puff (6 squares) and the "
     "sparks further out, fading.",
     row(3, 12, 12) + CENTER),
    # ---- Q End of the Line
    ("q_flash", "Q 穷途末路：发射榴弹时的枪口爆焰（烤进他的 Q 帧，朝右），4 帧",
     "rig_graves.py 烤进 skill 的第 3 帧起（枪口处；朝右，不对称）", "20 × 14",
     "发射榴弹：比普攻更大的一团枪口爆焰，橙红色的火往前喷，外面一圈灰白色的烟环往外扩（参考 q_bomb_gun_spray、muzzle_flash_01）。"
     "**朝右画**（枪口在格子左边正中）。4 帧：1 火焰喷出、2 最大、3 火变成烟环、4 烟散开。",
     f"{FI} and {SM}",
     "A CANNON BLAST from the shotgun, 4 frames, " + RIGHT + ": 1 a burst of orange-red fire from the left edge 10 squares "
     "long, a white core; 2 the fire 14 squares long and 11 tall, a ring of pale grey smoke round its root; 3 the fire "
     "gone, the smoke ring 12 squares across drifting right, a few embers; 4 only thin grey smoke wisps.",
     row(4, 20, 14) + "; the muzzle at the left edge of each cell, on its middle row."),
    ("q_shell", "Q：飞出去的榴弹（弹道，转向飞行方向），2 帧",
     "view_projectiles `league_graves_q_shell`（直线弹，跟着方向转；上下对称；循环）", "12 × 6",
     "穷途末路的榴弹：一颗黄铜色的炮弹，弹头黑色、中间一圈发光的橙色弹带，后面拖一缕火光和灰烟（参考 q_missile_mesh_tex、q_mis_bar、"
     "q_mis_gunpowder）。**朝右画、上下对称**。2 帧循环。",
     f"{GO}, {ST} and {FI}",
     "AN EXPLOSIVE SHELL, 2 frames, a seamless loop, " + TB + ": a brass shell 6 squares long and 4 tall with a black nose to "
     "the right and a glowing orange band round its middle, a 1-square near-black outline; behind it (to the left) a fiery "
     "orange tail 5 squares long fading into a grey puff; frame 2 the tail flickers (a square longer, the band brighter).",
     row(2, 12, 6) + "; the shell on the cell's middle rows, its nose 1 square from the right edge."),
    ("q_hit", "Q：榴弹飞过时打中的人（也用在大招爆炸打中的人身上），3 帧",
     "view_effects `league_graves_q_hit` / `r_hit2`（跟随目标，画在人物上面 z 2；左右对称）", "14 × 14",
     "被榴弹撞到：一团橙红色的爆点和几块飞溅的黑色弹片（参考 q_fb_explosion_centerflare、sparks）。**左右对称**。",
     f"{FI} and {SM}",
     "A SHELL STRIKE, 3 frames, " + LR + ": 1 an orange-red burst 7 squares across, a white core; 2 the burst 10 across, 6 dark "
     "shrapnel bits and 6 gold sparks flying out at mirrored places; 3 a grey smoke puff 9 squares across, the sparks fading.",
     row(3, 14, 14) + CENTER),
    ("q_blast", "Q：榴弹落地后 1 秒爆炸（不跟随），9 帧",
     "end_effects of the shell → view_effects `league_graves_q_blast`（落点，不跟随，画在人物上面 z 1；左右对称；大图表）",
     "48 × 40",
     "榴弹停下：地上一颗**圆形**的黑色炸弹（金色的箍、顶上一盏闪烁的红灯，冒着火星），**等 1 秒**（前 5 帧：红灯一亮一灭、火星往上冒），"
     "然后**轰的一声炸开**（后 4 帧：一团巨大的橙黄色火球、黑红色的烟往上翻、碎石和火星四溅、地上留一圈烧焦的痕迹）（参考 "
     "q_mis_bomb_grounddecal、q_fb_explosion_centerflare、q_explo_burn、poofexplo、q_bomb_groundspray）。**左右对称**（炸弹画成圆的）。",
     f"{FI}, {SM}, {ST} and {GO}",
     "A BOMB THAT WAITS, THEN BLOWS UP, 9 frames, " + LR + ": frames 1-5 a round black bomb (7 squares across, a gold band "
     "round it, a 1-square near-black outline) sitting on the ground in the middle of the cell, a red light on its top "
     "that is bright on frames 1, 3 and 5 and dark on 2 and 4, 2-3 orange sparks rising from it (mirrored), a dark scorch "
     "ellipse under it (14 wide, 4 tall); 6 the bomb gone in a white-gold flash 16 squares across with 8 long rays; 7 a huge "
     "orange-gold fireball 40 squares wide and 30 tall, white core, dark red edges, 10 sparks and dark rubble bits flying "
     "out at mirrored places; 8 the fireball breaking into rolling grey-black smoke 36 wide rising, embers; 9 only thin "
     "smoke puffs high up and the scorch ring on the ground (34 wide, 8 tall).",
     row(9, 48, 40) + "; centered across, the bomb's bottom 6 squares above the cell's bottom row (the ground)."),
    # ---- W Smoke Screen (in the attack)
    ("w_can", "W 烟幕弹：扔出去的烟幕罐（抛物线弹），2 帧",
     "view_projectiles `league_graves_w_can`（抛物线弹；左右、上下都对称；循环）", "6 × 6",
     "烟幕罐：一个圆圆的金属罐，喷着一缕灰绿色的烟（参考 canister_texture、smokebomb_swirl）。**左右、上下都对称**（它在空中翻滚）。2 帧循环。",
     f"{ST} and {CL}",
     "A SPINNING SMOKE CANISTER, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM, square for square: a "
     "round steel canister 4 squares across with a 1-square near-black outline and a lighter rim, grey-green smoke squares "
     "puffing from it; frame 2 the smoke squares on the other diagonal (still mirrored both ways).",
     row(2, 6, 6) + CENTER),
    ("w_smoke", "W：落地炸开的烟幕（不跟随，4 秒），8 帧",
     "end_effects of the canister → view_effects `league_graves_w_smoke`（落点，不跟随，画在人物上面 z 1；左右对称；大图表）",
     "52 × 34",
     "烟幕弹落地：先一团灰白色的冲击烟爆开，然后变成一大团**深灰绿色的浓烟**（贴着地面的圆顶，宽约 48 格），烟团慢慢翻滚 4 秒，最后变淡"
     "散掉（参考 smokebomb_swirl_green、dustcloud、smoke08、grenadesmoke）。**左右对称**，8 帧：1 冲击、2–7 浓烟翻滚（循环用）、8 散掉。"
     "烟要**半遮半透**：用浓淡几档的灰绿色方块拼出团块，中间留几块稍亮的缝，不要整片糊成一块。",
     CL,
     "A SMOKE SCREEN CLOUD, 8 frames, " + LR + ": 1 a pale grey-white impact puff 16 squares across on the ground with 6 smoke "
     "jets; 2 a dome of dark grey-green smoke 40 squares wide and 24 tall sitting on the ground, built from round puffs in "
     "4 shades with lighter tops, a few lighter gaps; 3-7 the same dome 48 squares wide and 28 tall, its puffs rolling: each "
     "frame every puff turns a little (frame 7 leads back into frame 3), wisps curling off both sides at mirrored places; "
     "8 the cloud thinned to separate pale puffs.",
     row(8, 52, 34) + "; centered across, the cloud's bottom on the cell's bottom row (the ground)."),
    ("w_slow", "W：被烟幕减速的敌人脚下（循环），2 帧",
     "view_buffs `league_graves_w_slow`（跟随，画在人物上面 z 2；左右对称；循环）", "16 × 6",
     "被烟幕弹减速：脚下几缕灰绿色的烟绕着（参考 smoke05）。**左右对称**，2 帧循环。",
     CL,
     "SMOKE WISPS at a unit's feet, 2 frames, a seamless loop, " + LR + ": a flat grey-green smoke ellipse 14 squares wide and 3 "
     "tall with 4 small curling wisps (2x3) rising from it at mirrored places; frame 2 the wisps curl the other way, a "
     "shade lighter.",
     row(2, 16, 6) + "; centered across, the ellipse on the cell's bottom rows."),
    # ---- E Quickdraw
    ("e_dust", "E 快速拔枪：冲刺起步时扬起的尘土（不跟随），4 帧",
     "view_effects `league_graves_e_dust`（CasterViewEffect，不跟随，画在人物下面 z -1；左右对称）", "26 × 10",
     "快速拔枪起步：脚下一团棕黄色的尘土往两边扬起，几块小石子跳起来（参考 dustcloud、e_ground_shadow）。**左右对称**，贴着地面。",
     DU,
     "A DUST KICK on the ground, 4 frames, " + LR + ": 1 a flat dust burst 10 squares wide on the ground; 2 two dust clouds "
     "rolling out to the left and right (each 9 wide, 6 tall), 4 pebbles (1 square) hopping at mirrored places; 3 the clouds "
     "13 squares out to each side, thinner, lighter on top; 4 only faint dust puffs at both ends.",
     row(4, 26, 10) + "; centered across, the dust's bottom on the cell's bottom row (the ground)."),
    ("e_grit", "E：纯爷们的护甲层（他脚下，跟随，循环），2 帧",
     "view_buffs `league_graves_e_g1`（tag e_grit；跟随他，画在人物下面 z -1；左右对称；循环）", "32 × 10",
     "纯爷们叠着的时候：他脚下一圈淡淡的金色光环（地上的椭圆，宽约 28 格），几点金色的小星光（参考 e_ring_gold）。**左右对称**，"
     "**只画地上的圈**（" + HIM + "）。2 帧循环。",
     GO,
     "A GOLD RING ON THE GROUND round a standing figure, 2 frames, a seamless loop, " + LR + " (" + HIM + "): a thin gold ring "
     "(an ellipse 28 squares wide and 8 tall, 1 square thick, brighter at its left and right ends) and 4 small gold glints "
     "(plus shapes, 3 squares) on it at mirrored places; frame 2 the glints at the other mirrored pair of places, the ring a "
     "shade brighter. The middle of the ellipse stays empty.",
     row(2, 32, 10) + "; centered across, the ellipse's middle 4 squares above the cell's bottom row."),
    # ---- R Collateral Damage
    ("r_flash", "R 终极爆弹：开大的枪口巨焰（烤进他的 R 帧，朝右），4 帧",
     "rig_graves.py 烤进 ult 的第 3 帧起（枪口处；朝右，不对称）", "28 × 18",
     "终极爆弹出膛：一团巨大的枪口爆焰，橙红色带金边的火往前猛喷、外面一圈翻滚的灰烟、几道向前的冲击线（参考 muzzle_flash_01、"
     "q_bomb_gun_spray、smoke_mult）。**朝右画**（枪口在格子左边正中）。4 帧：1 闪光、2 最大的火、3 火变烟、4 烟散。",
     f"{FI} and {SM}",
     "A HUGE MUZZLE BLAST, 4 frames, " + RIGHT + ": 1 a white-gold flash at the left edge 8 squares across with long rays; 2 a "
     "cone of orange-red fire with gold edges 22 squares long and 16 tall at its open end, a white core, 3 straight shock "
     "lines ahead of it; 3 the fire turning into a rolling grey smoke cloud 18 squares across, embers; 4 thin smoke wisps.",
     row(4, 28, 18) + "; the muzzle at the left edge of each cell, on its middle row."),
    ("r_shell", "R：飞出去的爆弹（弹道，转向飞行方向），2 帧",
     "view_projectiles `league_graves_r_shell`（直线弹，跟着方向转；上下对称；循环）", "18 × 8",
     "终极爆弹：一颗大的发光炮弹，金色的弹体、白热的弹头，后面拖一条长长的火焰尾巴（参考 e_mis_flametrail、q_missile_mesh_tex）。"
     "**朝右画、上下对称**。2 帧循环。",
     f"{FI} and {GO}",
     "A BIG BLAZING SHELL, 2 frames, a seamless loop, " + TB + ": a gold shell 7 squares long and 5 tall with a white-hot nose "
     "to the right (a 1-square near-black outline round the shell), a flame tail 10 squares long behind it (to the left), "
     "orange to deep red, flickering; frame 2 the tail's tongues shifted (mirrored top and bottom), a square longer.",
     row(2, 18, 8) + "; the shell on the cell's middle rows, its nose 1 square from the right edge."),
    ("r_hit", "R：爆弹打中第一个敌方英雄（跟随），4 帧",
     "view_effects `league_graves_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "20 × 20",
     "爆弹正中英雄：一团刺眼的白金色闪光，一圈橙色的冲击环往外扩（参考 hit_flash、q_fb_explosion_centerflare）。**左右对称**（" + CHAMP + "）。",
     f"{FI} and {GO}",
     "A HEAVY HIT, 4 frames, " + LR + ": 1 a white-gold flash 10 squares across with 8 rays; 2 the flash 14 across inside an "
     "orange ring 16 across; 3 the ring 19 across and thinner, sparks flying out at mirrored places; 4 only a faint ring and "
     "a few sparks.",
     row(4, 20, 20) + CENTER),
    ("r_blast", "R：打中后炸开的大爆炸（不跟随），5 帧",
     "lob end_effects → view_effects `league_graves_r_blast`（打中的位置，不跟随，画在人物上面 z 2；左右对称；大图表）", "50 × 38",
     "终极爆弹炸开：一团巨大的橙黄色爆炸火球、往外飞的黑色弹片和火星、翻滚上升的黑烟（参考 q_explo_burn、poofexplo、smoke_mult、"
     "sparks）。**左右对称**（附加包里伤害是英雄身后的锥形，画面照样画成一团对称的爆炸）。5 帧。",
     f"{FI}, {SM} and {GO}",
     "A BIG EXPLOSION, 5 frames, " + LR + ": 1 a white flash 14 squares across; 2 an orange-gold fireball 36 squares wide and "
     "26 tall, a white core, 12 shrapnel bits and sparks flying out at mirrored places; 3 the fireball 44 wide, its top "
     "turning into rolling black-grey smoke, embers; 4 a smoke column 30 wide rising, the fire inside it fading to deep "
     "red; 5 thin smoke puffs high up.",
     row(5, 50, 38) + "; centered across, the explosion's foot 6 squares above the cell's bottom row."),
]
BIG_FX = ["q_blast", "w_smoke", "r_blast"]
BAKED = ["a_flash", "q_flash", "r_flash"]

REDO = {}
GROUPS = [
    ("a_flash a_shot a_hit", ["graves_base_cast_muzzleflash", "muzzle_flash_01", "graves_base_ba_bullet_trail",
                              "graves_base_hit_flash", "graves_base_hit_sparks", "graves_ba_impactpuffs_2x2"]),
    ("q_flash q_shell q_hit q_blast", ["graves_base_q_bomb_gun_spray", "graves_base_q_missile_mesh_tex",
                                       "graves_base_q_mis_bar", "graves_base_q_mis_bomb_grounddecal",
                                       "graves_base_q_fb_explosion_centerflare", "graves_base_q_explo_burn",
                                       "poofexplo"]),
    ("w_can w_smoke w_slow", ["graves_canister_texture", "graves_smokebomb_swirl_green", "graves_dustcloud",
                              "smoke08", "graves_grenadesmoke_eyex"]),
    ("e_dust e_grit", ["graves_dustcloud", "graves_base_e_ground_shadow", "graves_base_e_ring_gold_01", "gold_dust"]),
    ("r_flash r_shell r_hit r_blast", ["graves_base_e_mis_flametrail", "muzzle_flash_01", "graves_base_smoke_mult",
                                       "graves_base_sparks", "graves_base_hit_flash", "graves_base_q_explo_burn"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_flash：开枪的这一帧，火光从枪口往右喷；a_shot 飞向目标，a_hit 在被打中的人身上"),
         ("skill", 3, "q_flash：低身发射榴弹；q_shell 往前飞，停下后 q_blast 等 1 秒爆炸"),
         ("skill2", 2, "e_dust：快速拔枪起步时脚下扬起尘土；e_grit 是之后脚下的金色光环"),
         ("ult", 3, "r_flash：把枪端到肩高开大；r_shell 飞向英雄，r_hit / r_blast 在打中的地方"),
         ("idle", 1, "待机（大小参考；w_smoke 是普攻每 12 秒扔出的烟幕）")]


def ref_sheet(path):
    S, LW = 170, 220
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        for k, word in enumerate(label.split()):
            d.text((10, y + S // 2 - 30 + k * 24), word, fill=(230, 240, 250, 255), font=font)
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                cand = [f for f in os.listdir(REF) if f.startswith(nm)]
                if not cand:
                    sys.exit(f"missing reference {p}")
                p = os.path.join(REF, sorted(cand)[0])
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("graves_base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"{SIZE_LABEL} {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    import rig_graves as M
    F = M.form()
    c = F.rig.finish(M.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 法外狂徒 格雷福斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/graves_idle.png`：3/4 正面朝右的魁梧枪手，往后梳的黑头发、"
      f"黑络腮胡，深红围巾，棕色皮马甲和金边大护肩，两手平端一把黑钢配金色的双管霰弹枪）。他在游戏里是**高清**的（每个游戏格子里 "
      f"1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/graves_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/graves_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里格雷福斯自己的特效贴图（大多是单色形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**枪火是橙黄色带白芯**、**枪烟是灰色**、**烟幕弹是深灰绿色的浓烟**、**快速拔枪是棕黄色的"
      "尘土**、**纯爷们是金色**。")
    a("> - **特效要亮**：每团火、每道光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a(f"> - **对称**：大部分严格**左右对称**（逐格对称：这些画面在红色方不会镜像）；四张弹道图（`a_shot` 弹丸、`q_shell` 榴弹、"
      "`r_shell` 爆弹）**朝右画、上下对称**（游戏把它转到飞行方向），`w_can` 烟幕罐左右上下都对称；三张枪口火光（`a_flash`、`q_flash`、"
      "`r_flash`）**朝右画**（枪口在格子左边正中），我会把它们画进他自己的开枪帧里（他的帧在红色方会镜像）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 12]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `graves_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/graves_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「新命运」、W「烟幕弹」在里面） | 霰弹枪一扇开火，两发后装弹；每 12 秒朝英雄扔一颗烟幕弹 | `a_flash` · `a_shot` · "
      "`a_hit` · `w_can` · `w_smoke` · `w_slow` |")
    a("| 技能 1 = Q「穷途末路」 | 发射榴弹，穿过的敌人受伤，停下 1 秒后爆炸 | `q_flash` · `q_shell` · `q_hit` · `q_blast` |")
    a("| 技能 2 = E「快速拔枪」 | 冲刺一段，叠纯爷们双抗 | `e_dust` · `e_grit` |")
    a("| 大招「终极爆弹」 | 后坐力往后跳，爆弹打中第一个英雄后炸开 | `r_flash` · `r_shell` · `r_hit` · `r_blast` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、烟、尘土、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**；"
      "实物（榴弹、烟幕罐、炸弹）有 1 格近黑描边。")
    a("- **要亮**：每个火光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("枪火", FIRE), ("灰色枪烟", SMOKE), ("烟幕的深灰绿", CLOUD), ("尘土", DUST), ("金色", GOLD),
                        ("钢铁（弹壳、罐子）", STEEL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：普攻射程 46000，烟幕半径 24000，"
      "榴弹爆炸半径 24000，大招爆炸半径 32000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `graves_fx_{name}.png`：{title}\n")
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
        a(f"| `graves_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_graves_fx`（小的）和 `league_graves_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_graves.py 的 views）；三张枪口火光（" + "、".join(BAKED) + "）不进表，rig_graves.py 把它们放在枪口烤进开枪帧"
      "（.over 层，ppu_restyle 的 fx）。")
    a("- 弹道（a_shot、q_shell、r_shell）跟着方向转；`w_can` 是抛物线弹的画面；`q_blast` 在榴弹停下的 end_effects 里，前 5 帧要放满 "
      "q_fuse（60 tick），第 6 帧正好在爆炸那一 tick；`w_smoke` 在烟幕罐落地的 end_effects 里，要放满 w_cloud（240 tick：3–7 帧循环）；"
      "`e_dust` 是 CasterViewEffect（不跟随）；`e_grit` / `w_slow` 是循环的 view_buffs。其余跟随、左右对称。")
    a("- 用 `pixel_1x/` 切格（import_karthus_fx 的做法），断言对称；清掉 Codex 给火光描的最深色边；核对交回的张数和这份清单；和 `raw/` "
      "原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="graves_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "graves_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run fx_ref_gv.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "graves_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "graves_size.png"))
    shots_sheet(os.path.join(out, "design", "graves_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"graves_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
