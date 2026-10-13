#!/usr/bin/env python3
"""Build mordekaiser_fx_pack.zip: step 3 of Mordekaiser's sprite - Codex draws his effects (after tools/art/pack_corki_fx.py).

    python tools/art/pack_mordekaiser_fx.py [--no-zip] [--only a_hit,q_hit --name mordekaiser_fx_redo_pack]

The pack (dist/mordekaiser_packs/mordekaiser_fx_pack, zipped next to it) holds PROMPTS.md (also written to
assets/source/mordekaiser/PROMPTS_FX.md), design/mordekaiser_idle.png (his dense idle as league.dll shows it, 2x),
design/mordekaiser_size.png (beside the base fighter at game size, the ground line, a 10-px ruler),
design/mordekaiser_shots.png (the frames the pictures start from, the cyan cross his standing point) and
refs/lol_fx_ref.png (League's own particle textures for Mordekaiser, grouped by the effect of ours they inform; Riot's
art, local only: it reads %TEMP%/mk_work/fxref, extracted from Mordekaiser.wad.client's base-skin particles by
%TEMP%/mk_work/fx/fx_ref_mk.py). The effects are the views the kit binds (tools/kit/build_mordekaiser.py:
view_projectiles q_crack, e_beam; view_effects a_hit, p_aura, p_hit, q_slam, q_hit, q_iso_hit, e_hit, w_shield, w_heal,
r_cast, r_mark, r_realm (the add-on's banish picture), r_pull, r_win; view_buffs r_curse). League's colours: ghost-teal
soul light, dark smoke, iron shards, grey stone dust for the slam. Light, smoke and dust get no outline. Red side: the
two lines symmetric top to bottom (turned to the cast), every other picture symmetric left to right. Codex also
delivers pixel_1x/.
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
import ppu_hd as P  # noqa: E402

REF = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mk_work", "fxref")
DOC = os.path.join(ROOT, "assets", "source", "mordekaiser", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_mordekaiser")
OUT = os.path.join(ROOT, "dist", "mordekaiser_packs")
K = 5                                                            # his PPU

SOUL = "#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C"     # the ghost-teal soul light (Darkness Rise, grasp, realm)
DARK = "#5A6478, #343A48, #1E2230, #0E1016"                       # dark smoke and shadow
IRON = "#E0E6F0, #A8B0C0, #6E7688, #3E4452"                       # iron sparks and shards
DUST = "#E6DCC8, #B8AC94, #8A7E6A, #5C5446"                       # stone dust and rubble (the slam)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a "
        "white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
SO = f"a ghost-teal soul ramp ({SOUL})"
DK = f"a dark smoke ramp ({DARK})"
IR = f"an iron ramp ({IRON})"
DU = f"a stone dust ramp ({DUST})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it toward the cast; cast to the left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_mordekaiser_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "锤子砸中：中间一下灰白色的金属冲击闪光，四周溅出几块铁色碎片和一点青绿色的灵魂火星（参考 AutoAttackSwipe、Z_Flash）。**左右对称**。约 12 格，居中画。",
     f"{IR} and {SO}",
     f"a HEAVY MACE HIT, 4 frames, {LR}: 1 a white-grey impact flash 5 squares across; 2 an iron starburst 11 squares "
     "across with 4-6 blunt rays and two teal sparks at mirrored places; 3 iron shards and teal sparks flying out at "
     "mirrored places; 4 a few fading shards.",
     row(4, 14, 14) + "; centered in every cell."),
    # ---- passive Darkness Rise
    ("p_aura", "被动「黑暗起兮」光环（他脚下，每 0.5 秒一下），4 帧", "view_effects `league_mordekaiser_p_aura`（跟随，画在人物下面一层；左右对称）",
     "50 × 18",
     "叠满 3 层后他身边的黑暗光环：地上一圈扁椭圆的暗色旋风（约 48 格宽、16 格高），里面绕着几缕青绿色的灵魂火和黑烟（参考 Passive_Ring、Passive_Cyclone、Passive_RipplesEdge）。**左右对称**。每 0.5 秒播一次，4 帧连起来像在转。**椭圆中间（他站的地方，约 20 格宽）留空**，只画外圈。",
     f"{SO} and {DK}",
     f"a DARK AURA RING on the ground, 4 frames played once every half second, {LR}: an ellipse 48 squares wide and 16 "
     "tall, its middle 20 squares wide EMPTY; along the ring dark smoke wisps (2-4 squares thick) and 4-6 short teal "
     "soul-flame tongues at mirrored places, all moving a little each frame as if circling; frame 1 the ring forming "
     "brighter, frames 2-3 swirling, frame 4 fading.",
     row(4, 52, 20) + "; centered across, the ellipse's middle 9 squares above the cell's bottom."),
    ("p_hit", "被动光环烧到的敌人（身上），3 帧", "view_effects `league_mordekaiser_p_hit`（跟随，画在人物上面；左右对称）", "10",
     "被黑暗光环烧到：身上冒起一小团青绿色的灵魂火和黑烟，一闪就没。**左右对称**。约 10 格，要小、要快。",
     f"{SO} and {DK}",
     f"a SMALL SOUL BURN on a unit, 3 frames, {LR}: 1 two teal flame tongues 3-4 squares tall at mirrored places with a "
     "white core; 2 the flames taller with a wisp of dark smoke; 3 fading smoke.",
     row(3, 12, 12) + "; centered in every cell."),
    # ---- Q Obliterate
    ("q_crack", "Q 破灭之锤砸出的地裂（一条直线，0.4 秒），6 帧", "view_projectiles `league_mordekaiser_q_crack`（朝施法方向转，画成朝右；上下对称）",
     "44 × 14",
     "锤子砸地后，从他身前往目标方向裂开的一条地面裂纹：一道锯齿状的暗色裂缝，裂缝里透出青绿色的光，两边翻起碎石和尘土（参考 Q_GroundHit、Q_Ground_ShockWave、Q_Impact_Dust）。**画成朝右的一条横线，上下对称**（往左放时游戏会上下翻）。6 帧依次播放：裂开、发光、尘土扬起、变暗消失。",
     f"{SO}, {DU} and {DK}",
     f"a GROUND CRACK LINE pointing to the RIGHT, 6 frames played once, {TB}: a jagged dark crack 42 squares long "
     "(2-3 squares wide) along the middle with teal light glowing inside it; frame 1 the crack running out from the left "
     "end to two thirds; frame 2 the whole length, the teal glow brightest; frame 3 stone dust and small rubble puffing "
     "up on both sides (mirrored top to bottom), 4-5 squares out; frame 4 the dust higher, the glow dimmer; frame 5 "
     "fading dust; frame 6 only the dark crack.",
     row(6, 46, 16) + "; the line along the middle of each cell, from 2 squares in at the left to 2 squares in at the right."),
    ("q_slam", "Q 锤子砸地的冲击（他身前，留在原地），5 帧", "view_effects `league_mordekaiser_q_slam`（不跟随，画在人物下面一层；左右对称）",
     "30 × 14",
     "砸地那一下：他脚下一圈扁椭圆的冲击波，地面裂开几道短裂纹，碎石和灰尘往两边扬起（参考 Q_Ground_ShockWave、Rocks、Impact_Dust）。**左右对称**，中间上半部分留空（不要挡住他）。",
     f"{DU} and {SO}",
     f"a GROUND SLAM SHOCKWAVE, 5 frames, {LR}, the upper middle 12 squares wide EMPTY: 1 a white-teal flash 8 squares "
     "across at the bottom middle; 2 a ring of dust and teal light bursting out, an ellipse 20 squares wide and 6 "
     "tall, 4 short cracks at mirrored places; 3 the ring at 28 x 9, rubble chunks flying at mirrored places; 4 dust "
     "puffs rising; 5 fading dust.",
     row(5, 32, 16) + "; centered across, the ring's middle 4 squares above the cell's bottom."),
    ("q_hit", "Q 砸中（被砸中的人身上），4 帧", "view_effects `league_mordekaiser_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "被锤子砸中：一团青绿色和铁灰色的冲击闪光，碎片溅开。**左右对称**。约 14 格。",
     f"{SO} and {IR}",
     f"a SMASH HIT on a unit, 4 frames, {LR}: 1 a white-teal flash 6 squares; 2 a teal-and-iron starburst 13 squares "
     "across; 3 shards and teal sparks at mirrored places; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("q_iso_hit", "Q 孤立砸中（只砸中一个人，更重），5 帧", "view_effects `league_mordekaiser_q_iso_hit`（跟随，画在人物上面；左右对称）", "20",
     "只砸中一个敌人时伤害更高：比上一张更大更亮，中间一团白色到青绿色的爆裂，外面一圈青绿色的冲击环（参考 Q_GroundHitGlow）。**左右对称**。约 20 格。",
     f"{SO} and {IR}",
     f"a HEAVY ISOLATED SMASH on a unit, 5 frames, {LR}: 1 a white flash 8 squares; 2 a white-teal burst 16 squares "
     "across with sharp rays; 3 a teal ring 20 squares across around fading rays, iron shards at mirrored places; 4 the "
     "ring breaking into teal sparks; 5 fading sparks.",
     row(5, 22, 22) + "; centered in every cell."),
    # ---- E Death's Grasp
    ("e_beam", "E 断魂一扼（从他手里伸出去的一道鬼爪，0.3 秒），5 帧", "view_projectiles `league_mordekaiser_e_beam`（朝施法方向转，画成朝右；上下对称）",
     "56 × 12",
     "他伸手甩出的鬼爪：一道青绿色的灵魂光束从左端（他的手）往右伸出去，右端是一只张开的幽灵爪子（三根爪尖，上下对称排列），然后爪子收拢、光束往回拉（参考 E_Cast_Beam、E_Cast_Trail、E_Souls、E_Slash_A）。**画成朝右的一条横线，上下对称**。",
     f"{SO} and {DK}",
     f"a GHOSTLY GRASPING BEAM pointing to the RIGHT, 5 frames played once, {TB}: frame 1 a teal soul beam 3 squares "
     "thick shooting from the left end to the middle; frame 2 the beam reaching the right end, an open spectral claw "
     "there 10 squares tall with three hooked claw tips spread up, middle and down (mirrored top to bottom), white-teal "
     "core; frame 3 the claw closing (the tips curling in), dark smoke wisps along the beam; frame 4 the beam pulling "
     "back toward the left, the claw small; frame 5 fading wisps.",
     row(5, 58, 14) + "; the beam along the middle of each cell, from 1 square in at the left to 1 square in at the right."),
    ("e_hit", "E 抓中（被拉的人身上），4 帧", "view_effects `league_mordekaiser_e_hit`（跟随，画在人物上面；左右对称）", "16",
     "被鬼爪抓住：几道青绿色的爪痕从两边往中间合拢，身上冒一圈暗色的烟（参考 E_Slash_A、E_Souls）。**左右对称**。约 16 格。",
     f"{SO} and {DK}",
     f"a CLAW GRIP on a unit, 4 frames, {LR}: 1 three teal claw streaks on each side, 6 squares long, curving in toward "
     "the middle (mirrored); 2 the streaks meeting in the middle with a white-teal flash; 3 a ring of dark smoke 14 "
     "squares across with teal sparks; 4 fading smoke.",
     row(4, 18, 18) + "; centered in every cell."),
    # ---- W Indestructible
    ("w_shield", "W 不坏之身的护盾（他身上），6 帧", "view_effects `league_mordekaiser_w_shield`（跟随，画在人物上面；左右对称）", "30 × 40",
     "护盾升起：他身体四周一圈青绿色的灵魂碎片和铁色的盔甲碎片往上飞旋，聚成一个竖着的椭圆光圈（参考 W_Glow、W_LightRay、W_Small_Mote、W_Concuss）。**左右对称**。**中间（他的身体，约 18 格宽、30 格高）留空**，只画外圈。",
     f"{SO} and {IR}",
     f"a SHIELD AURA around a big body, 6 frames played once, {LR}, the middle 18 squares wide and 30 tall EMPTY: 1 teal "
     "motes rising from the ground at mirrored places; 2 the motes and small iron shards spiralling up both sides; 3 a "
     "tall teal ellipse outline 28 squares wide and 38 tall forming from them (2 squares thick, white highlights); 4 the "
     "ellipse full and bright; 5 the ellipse thinner, motes drifting off; 6 a few fading motes.",
     row(6, 32, 42) + "; centered across, the ellipse's bottom 1 square above the cell's bottom."),
    ("w_heal", "W 消耗护盾回血（他身上），5 帧", "view_effects `league_mordekaiser_w_heal`（跟随，画在人物上面；左右对称）", "22 × 32",
     "护盾化成生命：几缕青绿色的灵魂从他身边往上升，在头顶附近散开成亮点（参考 W_LightRay、W_Small_Mote）。**左右对称**，中间身体部分只画细的升起光线，不要整块盖住他。",
     SO,
     f"a SOUL HEAL rising, 5 frames played once, {LR}: 1 four teal soul wisps 2 squares wide at the bottom at mirrored "
     "places; 2 the wisps rising 12 squares, curling; 3 the wisps at the top, bright white-teal heads; 4 the wisps "
     "bursting into small teal stars at the top; 5 fading stars.",
     row(5, 24, 34) + "; centered across, the wisps starting at the cell's bottom."),
    # ---- R Realm of Death
    ("r_cast", "R 轮回绝境出手（他身上，留在原地），7 帧", "view_effects `league_mordekaiser_r_cast`（不跟随，画在人物上面；左右对称）",
     "40 × 32",
     "开大那一下：他周围炸开一团暗绿色到黑色的漩涡，里面窜出几道青绿色的灵魂闪电（参考 R_Malestrom、R_SoulLightning、R_energy_ball）。**左右对称**。中间（他的身体，约 16 格宽、28 格高）只留细的闪电，不要整块挡住他。",
     f"{SO} and {DK}",
     f"a DARK VORTEX BURST, 7 frames played once, {LR}, the middle 16 squares wide and 28 tall nearly EMPTY (only thin "
     "lightning crossing it): 1 a teal flash 8 squares at the middle; 2 a dark smoke ring 24 squares across spinning "
     "out; 3 the ring 36 squares across with 4 jagged teal lightning bolts at mirrored places; 4 the lightning reaching "
     "outward, dark wisps; 5 the ring breaking into dark wisps; 6 fading wisps and sparks; 7 a few sparks.",
     row(7, 42, 34) + "; centered in every cell."),
    ("r_mark", "R 被诅咒的人（身上，开大那一下），5 帧", "view_effects `league_mordekaiser_r_mark`（跟随，画在人物上面；左右对称）", "16",
     "被诅咒：身上浮现一个青绿色的诅咒印记（像他头盔的冠形），一闪后化成青烟（参考 R_Crown_Glow、R_CausticSpecter）。**左右对称**。约 16 格。",
     f"{SO} and {DK}",
     f"a CURSE SIGIL on a unit, 5 frames, {LR}: 1 a white-teal flash 6 squares; 2 a teal crown-shaped sigil 12 squares "
     "wide (three upward spikes, the middle one tallest) with a ring under it; 3 the sigil bright with dark smoke "
     "around; 4 the sigil breaking into teal motes; 5 fading motes.",
     row(5, 18, 18) + "; centered in every cell."),
    ("r_realm", "R 死亡领域（两人被拖进去后原地留下的漩涡，循环），8 帧",
     "附加包放逐时的画面 `league_mordekaiser_r_realm`（不跟随，画在人物下面一层；左右对称；循环播放约 7 秒）", "46 × 24",
     "两人被拖进领域后，原地留下的一个暗色领域入口：地上一圈扁椭圆的黑绿色漩涡（约 44 格宽），外圈是一道青绿色的灵魂墙光边，里面的黑烟和青色丝线一圈圈往中间转（参考 R_Malestrom、R_SoulWall、R_Tendrils、R_Ground_A）。**左右对称**。8 帧**无缝循环**（会一直播到领域结束）。",
     f"{SO} and {DK}",
     f"a DARK REALM PORTAL on the ground, 8 frames, a SEAMLESS LOOP, {LR}: an ellipse 44 squares wide and 14 tall, its "
     "rim a teal soul-light wall 2 squares thick with short upright teal flames along it (3-6 squares tall) at mirrored "
     "places; inside, black-green smoke and thin teal threads spiralling toward the middle, the pattern advancing a "
     "little each frame so frame 8 leads back into frame 1; a soft darker core in the middle.",
     row(8, 48, 26) + "; centered across, the ellipse's middle 9 squares above the cell's bottom."),
    ("r_pull", "R 拉回（跑远的被诅咒者身上），4 帧", "view_effects `league_mordekaiser_r_pull`（跟随，画在人物上面；左右对称）", "14",
     "跑远了被拉回：身上缠起一圈青绿色的灵魂锁链光，往中间一收（参考 R_SoulTether）。**左右对称**。约 14 格。",
     SO,
     f"a SOUL TETHER YANK on a unit, 4 frames, {LR}: 1 a teal ring 12 squares across made of short chain-like dashes; 2 "
     "the ring tightening to 8 squares, brighter; 3 a white-teal flash at the middle; 4 fading motes.",
     row(4, 16, 16) + "; centered in every cell."),
    ("r_win", "R 领域里击杀（他身上，吸走灵魂），6 帧", "view_effects `league_mordekaiser_r_win`（跟随，画在人物上面；左右对称）", "26 × 34",
     "领域里杀死对手：一团青绿色的灵魂从上方旋转落进他身体，身上闪一下（参考 R_Wispy、R_energy_ball）。**左右对称**，中间身体部分只画细的灵魂丝，不要整块盖住他。",
     SO,
     f"a SOUL ABSORBED, 6 frames played once, {LR}: 1 a teal soul orb 6 squares wide at the top middle with two wisp "
     "tails curling down at mirrored places; 2 the orb lower, the tails spiralling; 3 the orb at the chest height "
     "splitting into wisps that wrap both sides; 4 a white-teal flash ring 20 squares across at the middle; 5 motes "
     "rising; 6 fading motes.",
     row(6, 28, 36) + "; centered across."),
    ("r_curse", "R 诅咒（被诅咒的人头顶，循环），4 帧", "view_buffs `league_mordekaiser_r_curse`（跟随，画在人物上面；左右对称）", "10 × 6",
     "被诅咒期间头顶一个小小的青绿色冠形印记（三根尖），轻轻闪。**左右对称**。4 帧无缝循环，画在格子上部。",
     SO,
     f"a SMALL CURSE CROWN above a head, 4 frames, a seamless loop, {LR}: a crown shape 7 squares wide and 5 tall in "
     "teal with a light rim (three spikes, the middle one tallest), pulsing brighter on frames 2-3.",
     row(4, 12, 8) + "; centered across, the crown in the top half of the cell."),
]

GROUPS = [
    ("a_* q_*", ["Mordekaiser_Base_AutoAttackSwipe", "Mordekaiser_Q_GroundHit", "Mordekaiser_Q_GroundHitGlow",
                 "Mordekaiser_Q_Impact_Dust", "Mordekaiser_Base_Q_Ground_ShockWave", "Mordekaiser_Base_Rocks"]),
    ("p_* w_*", ["Mordekaiser_Passive_Ring", "Mordekaiser_Base_Passive_Cyclone", "Mordekaiser_Base_Passive_RipplesEdge",
                 "Mordekaiser_Base_W_Glow", "Mordekaiser_Base_W_LightRay", "Mordekaiser_Base_W_Small_Mote"]),
    ("e_*", ["Mordekaiser_Base_E_Cast_Beam", "Mordekaiser_Base_E_Cast_Trail", "Mordekaiser_Base_E_Slash_A",
             "Mordekaiser_E_Souls", "Mordekaiser_Base_E_Ground_ShockWave", "Mordekaiser_E_Fire"]),
    ("r_*", ["Mordekaiser_Base_R_Malestrom", "Mordekaiser_Base_R_SoulLightning", "Mordekaiser_Base_R_SoulTether",
             "Mordekaiser_Base_R_SoulWall", "Mordekaiser_Base_R_Tendrils", "Mordekaiser_Base_R_Crown_Glow"]),
]
# the frames the pictures start from: (tag, frame index, what)
SHOTS = [("attack", 2, "a_hit：锤子砸下打中目标（青十字 = 站位点）"),
         ("skill", 1, "q_crack：从他身前往右裂开；q_slam 在他脚下"),
         ("skill2", 1, "e_beam：从伸出的那只手往右甩出"),
         ("ult", 1, "r_cast：开大时在他身上；r_realm 是两人消失后原地的漩涡"),
         ("idle", 0, "p_aura（脚下一圈）/ w_shield / w_heal / r_win：站位点")]


def dense(tag, i):
    sh = P.read_sheet(SHEET)
    return sh["hd_" + tag][i][0]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Mordekaiser_Base_", "").replace("Mordekaiser_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)




def size_sheet(path):
    """His dense idle at game size x 4 (league.dll draws it PPU times finer), the base fighter beside him, the ground."""
    import tfm2_ase as T
    Z = 4
    f = dense("idle", 0)
    fig = Image.fromarray(f).resize((round(f.shape[1] * Z / K), round(f.shape[0] * Z / K)), Image.NEAREST)
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    kf = Image.fromarray(k).resize((k.shape[1] * Z, k.shape[0] * Z), Image.NEAREST)
    W = fig.width + kf.width + 60
    H = max(fig.height, kf.height) + 80
    img = Image.new("RGBA", (W, H), (104, 112, 72, 255))
    cy = 70 + max(fig.height, kf.height) // 2           # both frames centred on their pivots on one row
    img.alpha_composite(fig, (20, cy - fig.height // 2))
    img.alpha_composite(kf, (40 + fig.width, cy - kf.height // 2))
    d = ImageDraw.Draw(img)
    g = cy + 11 * Z + Z // 2
    d.line([(0, g), (W, g)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.width // Z + 1, 10):
        x = 20 + i * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    ys, xs = np.nonzero(f[..., 3] > 0)
    fw, fh = round((xs.max() - xs.min() + 1) / K), round((ys.max() - ys.min() + 1) / K)
    d.text((8, 36), f"莫德凯撒约 {fw}×{fh} 格（游戏像素，连锤子），原版斗士（4 倍，红线是地面）", fill=(255, 255, 255, 255),
           font=font)
    img.convert("RGB").save(path)
    return fh, fw


def shots_sheet(path):
    """The finished frames at game size x 4 (dense / PPU), his standing point as a cyan cross."""
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, i, what in SHOTS:
        f = dense(tag, i)
        im0 = Image.fromarray(f).resize((round(f.shape[1] * Z / K), round(f.shape[0] * Z / K)), Image.NEAREST)
        im = Image.new("RGBA", (max(im0.width, 330), im0.height + 24), (104, 112, 72, 255))
        im.alpha_composite(im0, (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = im0.width // 2, 24 + im0.height // 2
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {i + 1}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape
    L = []
    a = L.append
    a("# 莫德凯撒 铁铠冥魂：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定：重甲巨人扛着大锤（`design/mordekaiser_idle.png`，游戏里连锤子约 {w} 格宽、{h} 格高，"
      "图是高清帧，游戏里按 5 倍密度显示）。特效照常按游戏像素画（1 格 = 1 个游戏像素），和其他英雄一样。")
    a("> - 大小对照 `design/mordekaiser_size.png`：他和原版斗士按游戏大小放大 4 倍，红线是地面，上面是 10 格一段的刻度。每条写的大小都是游戏像素（格）。")
    a("> - `design/mordekaiser_shots.png`：定稿动作（游戏大小 x4），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里莫德凯撒自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "颜色照英雄联盟原版：**青绿色的灵魂光**（被动、E 鬼爪、R 领域）、**黑色的烟**、铁灰色碎片、Q 砸地的灰色碎石和尘土。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **方向（重要，红色方会镜像）**：两条直线（`q_crack` 地裂、`e_beam` 鬼爪）画成朝右，游戏会按施法方向转，而且要**上下对称**（往左放时会上下翻）。"
      "其余所有画面（打中、光环、护盾、漩涡、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `mordekaiser_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `mordekaiser_fx_pack_done.zip`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「黑暗起兮」 | 锤子砸人；叠满 3 层后身边一圈黑暗光环持续烧周围的敌人 | `a_hit` · `p_aura` · `p_hit` |")
    a("| 技能 1 = Q「破灭之锤」 | 锤子砸地，往前裂开一条直线；只砸中一个人时更重 | `q_crack` · `q_slam` · `q_hit` · `q_iso_hit` |")
    a("| 技能 2 = E「断魂一扼」+ W「不坏之身」 | 甩出鬼爪把敌人拉过来；被贴脸时升起护盾，最后化成生命 | `e_beam` · `e_hit` · `w_shield` · `w_heal` |")
    a("| 大招 = R「轮回绝境」 | 诅咒对面核心，把两人拖进死亡领域单挑（原地留漩涡）；跑远被拉回；领域里击杀吸走灵魂 | `r_cast` · `r_mark` · `r_realm` · `r_pull` · `r_win` · `r_curse` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、尘土、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("灵魂青绿", SOUL), ("黑烟", DARK), ("铁色碎片", IRON), ("碎石尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在人身上、脚下的画面按每条写的站位画，**格子里留出空的位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "被动光环半径 24000，Q 直线 42000 长、半宽 6000，E 直线 54000 长、半宽 6000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `mordekaiser_fx_{name}.png`：{title}\n")
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
        a(f"| `mordekaiser_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_mordekaiser_fx`（小的）和 `league_mordekaiser_big`（p_aura、q_crack、q_slam、e_beam、r_cast、r_realm），tag = 名字（build_mordekaiser.py 的 views；r_realm 由附加包放逐时播放）。")
    a("- `q_crack`、`e_beam` 是只带画面的 LineRangeProjectile（画在直线中点，朝施法方向转）；`q_slam`、`r_cast`、`r_realm` 不跟随；`p_aura`、`q_slam`、`r_realm` 画在人物下面（z -1）；`r_curse` 头顶 buff（z 3）。")
    a("- 用 `pixel_1x/` 切格（import_gragas 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="mordekaiser_fx_pack", help="the pack's name (folder and zip)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(OUT, a.name)
    zpath = os.path.join(OUT, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/mk_work/fx/fx_ref_mk.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    f = dense("idle", 0)
    Image.fromarray(np.repeat(np.repeat(f, 2, 0), 2, 1)).save(os.path.join(out, "design", "mordekaiser_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "mordekaiser_size.png"))
    shots_sheet(os.path.join(out, "design", "mordekaiser_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as fh:
        json.dump([{"file": f"mordekaiser_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], fh,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
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
