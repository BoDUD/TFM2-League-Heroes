#!/usr/bin/env python3
"""Build sion_fx_pack.zip: step 3 of Sion's sprite - Codex draws his effects (after tools/art/pack_galio_fx.py).

    python tools/art/pack_sion_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name sion_fx_redo_pack]

The pack (%TEMP%/sn_work/fx/sion_fx_pack, zipped into --out, default dist/sion_packs) holds PROMPTS.md (also written to
assets/source/sion/PROMPTS_FX.md), design/sion_idle.png (his dense 3/4 front design at 3x), design/sion_size.png (the
1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter beside him),
design/sion_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Sion, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/sn_work/fxref, extracted from Sion.wad.client by %TEMP%/sn_work/fx/fx_ref_sn.py (the base skin's: few, mostly
grey shapes tinted in game) and fx_ref_sn2.py (Hextech Sion's Q, roar and furnace shapes - for their shapes only).
The effects are the views the kit binds (tools/kit/build_sion.py): view_projectiles q_warn (the charge's line on the
ground), q_slam (the smash along it, added with this pack), e_roar; view_effects a_hit, k_soul (a kill's soul drawn
into him), q_hit, e_hit, w_burst, w_hit, r_hit, r_crash; view_buffs w_sh, r_go, e_shred, p_zombie (the add-on's
zombie). League's colours: Sion's blood-red soul light (crimson to pink-white), the furnace's embers (orange), the
smoke of the undead, the dust and rubble of the smashed ground; light gets no outline. Red side: the lines on the
ground and the roar (q_warn, q_slam, e_roar) symmetric top to bottom (they turn with the cast), every other picture
symmetric left to right. Sizes follow the kit's numbers (1 game px = 1000 units).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
from build_sion import P  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sn_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "sion", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_sion")
HD_FRONT = os.path.join(ROOT, "assets", "source", "sion", "hd", "front.png")   # the approved dense design
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def px(units):
    return int(round(units / 1000))


SOUL = "#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E"     # blood-red soul light: white core to dark crimson
EMBER = "#FFF4D6, #FFD27A, #FF9A3A, #E85A1A"                      # the furnace's embers
SMOKE = "#6A4A52, #45303A, #2A1C22"                               # the smoke of the undead
DUST = "#E8DECF, #C2B39C, #94846E, #66584A, #40362E"              # dust and rubble of the smashed ground
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
SL = f"a blood-red soul ramp ({SOUL})"
EM = f"an ember ramp ({EMBER})"
SM = f"a dark smoke ramp ({SMOKE})"
DS = f"a dust ramp ({DUST})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

import pixel_down as PD  # noqa: E402
from ppu_hd import PPU as HD_PPUS  # noqa: E402

HD_PPU = HD_PPUS["sion"]                # his dense frames' squares a 1x pixel
SIZE = PD.sizes_of().get("sion", 1.0)   # he is shown at SIZE on the battlefield (hd.rs SIZES): the pictures round him too


def b(n):
    """A size round his body: n at 100 %, at the size he is shown."""
    return int(round(n * SIZE))


QL, QW = px(P["q_len"]) + 2, 2 * px(P["q_w"]) + 4      # the line on the ground: its length, the band drawn across it
ER = 2 * px(P["e_rad"]) + 10                            # the roar's front, top to bottom
WR = 2 * px(P["w_r"])                                   # the blast's ring, across
# the crash's ring: the slow's r_r plus the units' collision radii, drawn big from the start (Galio's landing, 46 wide
# at first, was redrawn 84 after the user: 「这个R的特效做大点啊」「加里奥的R特效这么小？」)
RR = 80

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and Soul Furnace's kills
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_sion_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "巨斧劈中：目标身上一道竖着的白红色劈痕一闪，裂成两道往两边弯的血红色月牙，溅出几点火星（参考 Q_Hit1_cresent、Q_Hi1_weaponswipe 的形状）。**左右对称**。约 12 格，居中画。",
     SL,
     f"an AXE CLEAVE HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a vertical white-red cleave "
     "slash 12 squares tall and 2 wide with a white core; 3 the slash splitting into two blood-red crescents curving "
     "outward at mirrored places, 4 red sparks flying out; 4 a few fading sparks.",
     row(4, 14, 14) + "; centered in every cell."),
    ("k_soul", "灵魂熔炉：杀死一个单位，灵魂被他吸进胸口（他身上），5 帧",
     "view_effects `league_sion_k_soul`（跟随，画在人物上面，z 3；左右对称）", "14 × 24",
     "每杀一个单位永久加生命：一小团血红色的灵魂火（水滴形的小鬼火，两个并排的小黑眼点）从上面落进他胸口，胸口红光一亮，冒出几道短光（参考 Passive_Body_TX 胸口的红光）。**左右对称**。",
     SL,
     f"a SOUL DRAWN INTO A CHEST, 5 frames, {LR}: 1 a small blood-red ghost wisp (a teardrop flame 5 squares wide and 7 "
     "tall, pointing up, two small dark eye dots side by side on its middle line) at the top of the cell; 2 the wisp "
     "lower, stretched downward; 3 the wisp at the cell's middle, shrinking into a red-white glow 6 squares across; "
     "4 the glow 10 squares across with 4 short red rays at mirrored places; 5 a fading glow.",
     row(5, 16, 26) + "; centered across; the glow of frames 3-5 centered 8 squares above the cell's bottom."),
    # ---- Q Decimating Smash
    ("q_warn", "Q 残虐猛击：蓄力时身前地上的范围（地上，循环），4 帧",
     f"view_projectiles `league_sion_q_warn`（LineRangeProjectile：画在人物下面，朝施放方向转，画成朝右；上下对称；左端是他站的地方）",
     f"{QL} × {QW}",
     f"蓄力的时候身前地上一条血红色的长方形范围（敌人看得见要砸哪里，参考英雄联盟 Q 的红色指示）：边框亮红色，里面暗红色（导入时 Claude 把里面调成半透明），中间一排朝右的箭头一闪一闪往前推。**上下对称**，朝右（左端在他脚下）。约 {QL} 格长、{QW} 格宽。",
     SL,
     f"a DANGER ZONE ON THE GROUND seen from above, pointing to the RIGHT, 4 frames, a seamless loop, {TB}: a flat "
     f"rectangle with slightly rounded ends, {QL} squares long and {QW} wide; its border 1-2 squares thick in bright red "
     "with white-pink highlights, the inside filled with flat dark crimson; a row of 4 chevrons (>) in red-pink along "
     "the middle line, the brightest chevron moving one step to the right each frame.",
     row(4, QL + 2, QW + 2) + "; centered in every cell."),
    ("q_slam", "Q 砸地：斧头砸下去，裂缝沿着范围往前裂开（地上，播一次），5 帧",
     f"view_projectiles `league_sion_q_slam`（新加：Q 砸地那一下的 LineRangeProjectile，画在人物下面，朝施放方向转，画成朝右；上下对称；左端是他站的地方；播一次）",
     f"{QL} × {QW}",
     f"斧头砸地：从左端（他脚下）一道发红光的地裂沿着中线往右裂到头，裂缝两边对称地分出小岔，沿路炸起尘土和碎石（参考 Q_Hit2_groundcracks、Q_Hit2_scortch、Q_Hit2_groundsmoke）。**上下对称**，朝右。约 {QL} 格长、{QW} 格宽。",
     f"{SL} and {DS}",
     f"a GROUND SMASH CRACKING FORWARD seen from above, pointing to the RIGHT, 5 frames, {TB}: 1 a white-red flash 8 "
     "squares across at the LEFT end (where the axe lands) and a short glowing crack starting from it; 2 a jagged crack "
     "along the middle line glowing red with a white core, reaching halfway, small side branches mirrored above and "
     "below it, dust puffs bursting at the left end; 3 the crack reaching the RIGHT end, dust and rubble bursting along "
     f"it at mirrored places, {QW} squares across at most; 4 the dust thinning, the crack dark red; 5 a faint dark crack "
     "and a few dust specks.",
     row(5, QL + 2, QW + 2) + "; centered in every cell; the crack starts 1 square from the LEFT edge."),
    ("q_hit", "Q 砸中、击飞（目标身上），5 帧", "view_effects `league_sion_q_hit`（跟随，画在人物上面；左右对称）", "18 × 24",
     "被砸中击飞：目标身上血红色的冲击炸开，几道红光往上冲，带一点尘土。**左右对称**。",
     f"{SL} and {DS}",
     f"a KNOCK-UP SMASH HIT on a unit, 5 frames, {LR}: 1 a white-red flash 6 squares; 2 a blood-red burst 12 squares "
     "across with a white core; 3 the burst's ring 18 squares across, 3 red streaks shooting upward at mirrored places, "
     "dust puffs at its bottom; 4 the streaks higher and thinner; 5 fading sparks.",
     row(5, 20, 26) + "; centered across, the burst's middle 9 squares above the cell's bottom."),
    # ---- E Roar of the Slayer
    ("e_roar", "E 杀手怒吼：飞出去的怒吼冲击波（直线飞，循环），4 帧",
     "view_projectiles `league_sion_e_roar`（朝飞行方向转，画成朝右飞；上下对称）", f"14 × {ER}",
     "从嘴里吼出去的冲击波：三道一层套一层的血红色弧（像 「)))」），最前面那道最大、带白色高光，后面两道小一点，一闪一闪往前推（参考 distortion_soundwaves 的圆波）。**上下对称**，朝右飞。",
     SL,
     f"a ROAR SHOCKWAVE flying to the RIGHT, 4 frames, a seamless loop, {TB}: three nested blood-red arcs like ')))', "
     f"each 2 squares thick, the front arc {ER} squares tall with a white-pink highlight, the two behind it smaller "
     f"({ER - 6} and {ER - 12} tall); the arcs brightening one after another from back to front.",
     row(4, 16, ER + 2) + "; the front arc 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_hit", "E 怒吼打中（目标身上），4 帧", "view_effects `league_sion_e_hit`（跟随，画在人物上面；左右对称）", "16",
     "被怒吼打中：目标身上一圈血红色的冲击波扩开、碎成火星。**左右对称**。约 16 格。",
     SL,
     f"a ROAR HIT on a unit, 4 frames, {LR}: 1 a red ring 6 squares across; 2 a blood-red ring 12 squares across, 2 "
     "squares thick, white inner edge; 3 the ring 16 squares across breaking into 6 sparks at mirrored places; "
     "4 fading sparks.",
     row(4, 18, 18) + "; centered in every cell."),
    ("e_shred", "E 破甲（被吼中的人头顶，循环），4 帧", "view_buffs `league_sion_e_shred`（跟随，画在人物上面；左右对称）", "10 × 10",
     "护甲被削：头顶一个小小的灰色盾牌，正中一道血红色的裂纹从上裂到下，一闪一闪。**左右对称**。",
     f"{SL} and {DS}",
     f"a CRACKED SHIELD MARK over a head, 4 frames, a seamless loop, {LR}: a small pale grey-beige shield shape 8 squares "
     "wide and 9 tall with a blood-red crack straight down its middle line, the crack pulsing brighter and dimmer, two "
     "small red chips falling off at mirrored places.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- W Soul Furnace
    ("w_sh", "W 灵魂熔炉：护盾（他身上，跟着他，循环），4 帧",
     "view_buffs `league_sion_w_sh`（跟随，画在人物上面；左右对称；中间人形位置留空）", f"{b(60)} × {b(58)}",
     "护盾：他周围一圈血红色和橙色的灵魂火，沿着一个大椭圆的边往上烧（火舌朝上），顶上白热的高光，边上几只小鬼火（带两个小黑眼点）对称地绕着飘。**中间人形位置留空**，**左右对称**。",
     f"{SL} and {EM}",
     f"a SOUL FURNACE SHIELD round a big figure, 4 frames, a seamless loop, {LR}, its inside EMPTY (a clear upright area "
     f"{b(48)} squares wide and {b(48)} tall): the rim of an ellipse {b(60)} squares wide and {b(58)} tall made of "
     "blood-red and orange flames 2-4 squares tall licking upward, white-hot highlights at its top, 4 small red ghost "
     "wisps (teardrop flames with two dark eye dots) on the rim at mirrored places; the flames flickering in turn, the "
     "wisps one step higher each frame.",
     row(4, b(60) + 2, b(58) + 2) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    ("w_burst", "W 引爆：护盾炸开（他脚下，不跟随），5 帧",
     "view_effects `league_sion_w_burst`（不跟随，画在人物上面；左右对称）", f"{WR} × 28",
     f"护盾撑满 3 秒还没破就炸开：地上一圈血红色加橙色的火焰冲击环往外扩（扁椭圆），环上火舌往上窜，火星往外飞，最后一点黑烟。**左右对称**，中间人形位置留空。范围约 {WR} 格宽。",
     f"{SL}, {EM} and {SM}",
     f"a FURNACE BLAST from a figure, 5 frames, {LR}, the middle above the ring EMPTY (a clear upright area 40 squares "
     "wide and 20 tall): 1 a white-red flash ring at the feet 16 squares wide; 2 a blood-red fire ring 36 squares wide "
     f"and 13 tall, 2 squares thick, with flame tongues rising at mirrored places; 3 the ring {WR} wide and 20 tall, "
     "flame tongues 8 squares tall round it, orange embers flying outward at mirrored places; 4 the ring breaking into "
     "embers and dark smoke puffs; 5 fading smoke.",
     row(5, WR + 2, 30) + "; centered across, the ring's middle 6 squares above the cell's bottom."),
    ("w_hit", "W 炸中（目标身上），4 帧", "view_effects `league_sion_w_hit`（跟随，画在人物上面；左右对称）", "14",
     "被熔炉炸中：目标身上一团血红色的火焰炸开往上窜，火星，一小团黑烟。**左右对称**。",
     f"{SL}, {EM} and {SM}",
     f"a SOUL-FIRE HIT on a unit, 4 frames, {LR}: 1 a white-red flash 4 squares; 2 a blood-red flame burst 10 squares "
     "across, white core; 3 the flames 14 squares across licking upward, orange embers at mirrored places; 4 fading "
     "embers and a small puff of dark smoke.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- R Unstoppable Onslaught
    ("r_go", "R 蛮横冲撞：冲锋中（他身上，跟着他，循环），4 帧",
     "view_buffs `league_sion_r_go`（跟随，画在人物下面；左右对称；中间人形位置留空）", f"{b(56)} × {b(40)}",
     "冲锋时：脚下一圈发红光的扁椭圆，两边对称地扬起尘土，身体两边几道血红色的光往上飘（像一身红色的怒气）。**中间人形位置留空**，**左右对称**。",
     f"{SL} and {DS}",
     f"an ONSLAUGHT AURA round a big charging figure, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright "
     f"area {b(40)} squares wide and {b(30)} tall above the ground ring): a flat glowing red ellipse {b(44)} squares wide "
     f"and {b(9)} tall at the feet; dust clouds kicked up at both of its ends at mirrored places; red light streaks and "
     f"embers rising along both sides of the figure up to {b(36)} squares high, one step higher each frame.",
     row(4, b(56) + 2, b(40) + 2) + f"; centered across, the ellipse's middle {b(5)} squares above the cell's bottom."),
    ("r_crash", "R 撞上：砸地冲击（他脚下，不跟随），6 帧",
     "view_effects `league_sion_r_crash`（不跟随，画在人物下面；左右对称）", f"{RR} × 44",
     f"撞上英雄的一下：地上一圈血红色的大冲击环炸开，中间裂开几道发红光的地裂，碎石和尘土往上冲。**左右对称**。大招要大：约 {RR} 格宽（比他自己还宽一截）。",
     f"{SL} and {DS}",
     f"a HEAVY CRASH on the ground, 6 frames, {LR}: 1 a white-red flash 18 squares wide; 2 a flat blood-red shock ring 50 "
     f"squares wide and 16 tall, a dark crimson inner ring; 3 the ring {RR} wide and 26 tall, 2-3 squares thick, glowing "
     "red cracks radiating from the middle at mirrored places, rubble and dust clumps rising 16 squares at mirrored "
     "places; 4 the dust higher, the ring thinning; 5 the cracks dimmer, the dust settling; 6 faint cracks.",
     row(6, RR + 2, 46) + "; centered across, the ring's middle 14 squares above the cell's bottom."),
    ("r_hit", "R 撞飞（被撞的人身上），4 帧", "view_effects `league_sion_r_hit`（跟随，画在人物上面；左右对称）", "18 × 28",
     "被撞飞：目标身上一个血红色的大 X 形冲击一闪，几道红光往上冲。**左右对称**。",
     SL,
     f"a CRIMSON UPWARD HIT on a unit, 4 frames, {LR}: 1 a white-red flash 6 squares; 2 a blood-red X-shaped shock 14 "
     "squares across with a white core; 3 3 red streaks shooting upward at mirrored places, the X fading; 4 fading "
     "motes.",
     row(4, 20, 30) + "; centered across, the X's middle 9 squares above the cell's bottom."),
    # ---- the add-on's Glory in Death
    ("p_zombie", "被动 死亡荣耀：亡灵状态（他身上，跟着他，循环），4 帧",
     "view_buffs `league_sion_p_zombie`（附加包加的 buff；跟随，画在人物上面；左右对称；中间人形位置留空）", f"{b(62)} × {b(62)}",
     "第一次被打死后变成亡灵继续打：他周围暗红色和黑红色的死亡之火往上烧，几只淡红色的小骷髅鬼火往上飘，脚下一圈暗红色的地光（参考 Passive_Body_TX、Passive_Axe_shards）。**中间人形位置留空**，**左右对称**。",
     f"{SL} and {SM}",
     f"a DEATH-FIRE AURA round a big figure, 4 frames, a seamless loop, {LR}, its inside EMPTY (a clear upright area "
     f"{b(48)} squares wide and {b(50)} tall): dark crimson and smoky black-red flames {b(4)}-{b(8)} squares tall rising "
     f"along both sides of the figure; a dark red glowing ring {b(52)} squares wide and {b(10)} tall at the feet; 4 small "
     "pale-red skull wisps rising at mirrored places, one step higher each frame; red embers.",
     row(4, b(62) + 2, b(62) + 2) + f"; centered across, the ring's middle {b(5)} squares above the cell's bottom."),
]

GROUPS = [
    ("a_hit q_*", ["Sion_Skin01_Q_Hit1_cresent", "Sion_Skin01_Q_Hi1_weaponswipe", "Sion_Skin01_Q_Hit2_groundcracks",
                   "Sion_Skin01_Q_Hit2_scortch", "Sion_Base_Q_Hit2_groundsmoke", "Sion_Skin01_Q_Hit2_rays"]),
    ("e_*", ["Sion_Skin01_distortion_soundwaves_01", "Sion_Skin01_Q_Hit3_spikes"]),
    ("w_* k_*", ["Sion_Skin01_Q_Cas1_weaponglow", "Sion_Base_Passive_Body_TX"]),
    ("r_* p_*", ["Sion_Skin01_Q_Hit2_charged", "Sion_Skin01_Q_Hit1_ground", "Sion_Base_Passive_Axe_shards",
                 "Sion_Base_Passive_Weapon"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：斧头劈到的地方（画在目标身上）"),
         ("skill_charge", 2, "q_warn：蓄力，身前地上的范围"),
         ("skill", 3, "q_slam：斧头砸地，地裂往前"),
         ("skill2", 3, "e_roar：怒吼往前飞"),
         ("skill2_w", 3, "w_sh：熔炉护盾罩住他"),
         ("ult", 1, "r_go：冲锋"),
         ("ult_hit", 2, "r_crash：撞上")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Sion_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def shown(a, Z):
    """A dense (hd_) frame as the game shows it, Z screen px a game px: scaled SIZE / PPU, nearest."""
    k = Z * SIZE / HD_PPU
    return np.asarray(Image.fromarray(np.ascontiguousarray(a)).resize(
        (max(1, round(a.shape[1] * k)), max(1, round(a.shape[0] * k))), Image.NEAREST))


def size_sheet(path):
    """His idle as the game shows it (hd_ frame at SIZE) at 4x on the arena colour, the feet line, a 10-px ruler and the
    base fighter beside him (4x). -> his size in game px (h, w)."""
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("hd_idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    Z, pad = 4, 6
    fig = shown(f[ys.min():ys.max() + 1, xs.min():xs.max() + 1], Z)
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    kn = np.repeat(np.repeat(kn, Z, 0), Z, 1)
    W = pad * Z + fig.shape[1] + pad * Z + kn.shape[1] + pad * Z
    Hh = max(fig.shape[0], kn.shape[0])
    img = Image.new("RGBA", (max(W, 640), pad * Z + Hh + 16 + 64), (104, 112, 72, 255))
    base = pad * Z + Hh + 64
    img.alpha_composite(Image.fromarray(fig), (pad * Z, base - fig.shape[0]))
    img.alpha_composite(Image.fromarray(kn), (2 * pad * Z + fig.shape[1], base - kn.shape[0]))
    d = ImageDraw.Draw(img)
    d.line([(0, base), (img.width, base)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    gw, gh = round(fig.shape[1] / Z), round(fig.shape[0] / Z)
    for i in range(0, gw + 1, 10):
        x = pad * Z + i * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"赛恩 {gw}×{gh} 格（连斧头，游戏里显示 {round(SIZE * 100)}%），原版斗士 "
                    f"{kn.shape[1] // Z}×{kn.shape[0] // Z} 格（都是 4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return gh, gw


def shots_sheet(path):
    """The finished action frames as the game shows them (hd_ frames at SIZE), 4x, his standing point a cyan cross."""
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    Z, PAD = 4, 48
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    idle = np.asarray(sp.frames[sp.tag_frames("hd_idle")[0]].convert("RGBA"))
    ground = np.nonzero(idle[..., 3] > 0)[0].max() + 1 - idle.shape[0] / 2     # the soles' line under the centre (dense)
    tiles = []
    for tag, k, what in SHOTS:
        a = np.asarray(sp.frames[sp.tag_frames("hd_" + tag)[k - 1]].convert("RGBA"))
        g = shown(a, Z)
        px_ = g.shape[1] // 2 + PAD
        f = np.pad(g, ((PAD, PAD), (PAD, PAD), (0, 0)))
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px_, PAD + round((a.shape[0] / 2 + ground) * g.shape[0] / a.shape[0]))
        x0, x1 = int(min(xs.min(), pt[0])) - 12, int(max(xs.max(), pt[0])) + 16
        y0, y1 = int(ys.min()) - 12, int(ys.max()) + 16
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1], 330), sub.shape[0] + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int(pt[0] - x0), int(pt[1] - y0) + 24
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
    a("# 亡灵战神 赛恩：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/sion_idle.png`：游戏里的 3/4 正面待机，巨斧垂在近侧腿边）。他在游戏里是**高清**的（这张图是高清造型放大 3 倍），**游戏里显示成 {round(SIZE * 100)}%：连斧头约 {h} 格高、{w} 格宽**（每个游戏格子里约 {HD_PPU / SIZE:.1f} 个细像素）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sion_size.png`：待机按游戏里显示的大小放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/sion_shots.png`：定稿动作（按游戏里显示的大小放大 4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里赛恩的特效贴图（原皮的贴图大多是灰色形状、游戏里再上色，所以也放了海克斯皮肤的 Q、怒吼、熔炉的形状——**只看形状**），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**血红色的灵魂光（深红到粉白）、熔炉的橙色火星、亡灵的暗红黑烟、砸碎地面的尘土和碎石**。")
    a("> - **特效要亮**：每道光、每团火都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的护盾、火焰、光环只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方不会镜像）**：地上的 `q_warn`、`q_slam` 和飞出去的 `e_roar` 画成朝右，**上下对称**（往左放时会上下翻）。"
      "其余所有画面（打中、身上、脚下、头顶、地上的冲击环）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sion_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `sion_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「灵魂熔炉」 | 巨斧劈砍；每杀一个单位永久加最大生命 | `a_hit` · `k_soul` |")
    a("| 技能 1 = Q「残虐猛击」 | 原地蓄力，身前地上出现范围；砸地，范围里的敌人被击飞 | `q_warn` · `q_slam` · `q_hit` |")
    a("| 技能 2 = E「杀手怒吼」+ W「灵魂熔炉」 | 怒吼冲击波直线飞出，减速、破甲；被英雄贴近时开熔炉护盾，3 秒后还在就炸开 | `e_roar` · `e_hit` · `e_shred` · `w_sh` · `w_burst` · `w_hit` |")
    a("| 大招 = R「蛮横冲撞」 | 免控冲向远处的英雄，撞上击飞，周围减速 | `r_go` · `r_crash` · `r_hit` |")
    a("| 附加包被动「死亡荣耀」 | 第一次被打死后变成亡灵继续打一阵 | `p_zombie` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟、冲击环、尘土都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个光和火的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("血红色灵魂光", SOUL), ("熔炉火星", EMBER), ("亡灵黑烟", SMOKE), ("尘土和碎石", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）；`q_warn`、`q_slam` 是从正上方看的地面长条（游戏会把它转到施放方向）。")
    a("- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 {P['atk_range']}，"
      f"Q 范围长 {P['q_len']}、半宽 {P['q_w']}，E 飞 {P['e_len']}、半径 {P['e_rad']}，W 炸开半径 {P['w_r']}，R 撞上减速半径 {P['r_r']}）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sion_fx_{name}.png`：{title}\n")
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
        a(f"| `sion_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_sion_fx`（小的）和 `league_sion_big`（q_warn、q_slam、w_sh、w_burst、r_go、r_crash、p_zombie），tag = 名字（build_sion.py 的 views；"
      "`q_slam` 这次新加：Q 砸地的 LineRangeProjectile 带上这张，`repeat: false`，delay 拉到画面播完）。")
    a("- `q_warn`、`q_slam`、`e_roar` 是投射物，画面朝施放方向转；`q_warn` 的里面导入时调成半透明（只留边框和箭头不透明）；`w_burst`、`r_crash` 不跟随；`e_shred` 头顶；`w_sh`、`r_go`、`p_zombie` 中间必须是空的。")
    a("- 用 `pixel_1x/` 切格（import_kassadin / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sion_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "sion_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/sn_work/fx/fx_ref_sn.py and fx_ref_sn2.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 3, 0), 3, 1)).save(os.path.join(out, "design", "sion_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "sion_size.png"))
    shots_sheet(os.path.join(out, "design", "sion_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sion_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
