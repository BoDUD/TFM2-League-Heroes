#!/usr/bin/env python3
"""Build elise_fx_pack.zip: step 3 of Elise's sprite - Codex draws her effects (pack_nidalee_fx.py's way).

    python tools/art/pack_elise_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name elise_fx_redo_pack]

The pack (%TEMP%/el_work/fx/elise_fx_pack, zipped into --out, default dist/elise_packs) holds PROMPTS.md (also written
to assets/source/elise/PROMPTS_FX.md), design/elise_idle.png (her dense designs, both forms, at 3x),
design/elise_size.png (the 1x idles at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter
beside them), design/elise_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Elise, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/el_work/fxref, read out of Elise.wad.client's base-skin particle paths by %TEMP%/el_work/fx_ref_el.py).
The effects are the views the kit binds (tools/kit/build_elise.py: view_projectiles a_spit, q_bolt, e_web, w_spider;
view_effects a_hit, c_hit, sl_bite1-3, q_hit, cq_hit, e_hit, w_boom, w_hit, ce_up, ce_land, ce_hit, cw_frenzy,
tf_spider, tf_human, r_cast; view_buffs cw_on).
League's colours: crimson venom with violet smoke (her spit, Neurotoxin, the bites), grey-white silk with a red glint
(the cocoon, Rappel's thread), the spiderlings black with glowing red backs, the turns dark violet smoke with crimson
sparks; light gets no outline.
Red side: the flying pictures (a_spit, q_bolt, e_web, w_spider - the spiderling seen from above) symmetric top to
bottom (they turn with the flight), every picture on a unit, on her, on the ground and every buff symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "el_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "elise", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_elise")
HD = os.path.join(ROOT, "assets", "source", "elise", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


CRIMSON = "#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618"   # venom, bites, frenzy: white core to deep blood red
VIOLET = "#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452"             # her smoke, the turns
SILK = "#FFFFFF, #ECEAF2, #C9C6D6, #9D99B0, #6E6A82"               # web, cocoon, Rappel's thread
CHITIN = "#4A3550, #2A1E30, #120C16"                              # the spiderlings' bodies (with crimson backs and eyes)
EARTH = "#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39"             # dust kicked up by the landing
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
CR = f"a crimson venom ramp ({CRIMSON})"
VI = f"a violet smoke ramp ({VIOLET})"
SK = f"a silk ramp ({SILK})"
CH = f"a chitin ramp ({CHITIN})"
ER = f"an earth-dust ramp ({EARTH})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."


def bites(k):
    where = {1: "ONE spiderling clinging at the top middle (on the head's place)",
             2: "TWO spiderlings clinging at the left and right sides at waist height, mirrored",
             3: "THREE spiderlings: one at the top middle and two at the left and right sides at waist height, mirrored"}[k]
    return (f"sl_bite{k}", f"被动 小蜘蛛撕咬（{k} 只，目标身上），3 帧",
            f"view_effects `league_elise_sl_bite{k}`（跟随，画在人物上面；左右对称）", "16 × 26",
            f"蜘蛛形普攻时小蜘蛛扑在目标身上撕咬：{k} 只黑色小蜘蛛（背上发红光、红眼睛，参考 EliseSpiderling 和 W_SpiderShape），"
            "咬下去时有一小点深红的咬痕闪光。**左右对称**，中间人形位置留空（只画小蜘蛛扑上来的位置）。",
            f"{CH} and {CR}",
            f"SPIDERLINGS BITING a figure, 3 frames, {LR}, the middle EMPTY except where they cling (an upright figure 10 squares "
            f"wide and 22 tall stands there, not drawn): {where}; each spiderling 5 squares wide and 4 tall seen from the front, "
            "a black body with a glowing crimson back and two red eye dots, legs splayed; 1 the spiderlings leaping on; 2 biting, "
            "a small crimson bite flash 3 squares at each; 3 holding on, the flashes fading.",
            row(3, 16, 26) + "; centered across, the figure's feet on the cell's bottom row.")


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the human's attack, Neurotoxin
    ("a_spit", "普攻：吐出去的毒液（朝目标飞，循环），2 帧", "view_projectiles `league_elise_a_spit`（朝飞行方向转，画成朝右飞；上下对称）",
     "12 × 5", "人形普攻甩出去的毒液：一团深红色的毒液球（白芯），后面一小段紫色的烟尾（参考 BA_Head_01、BA_Streak、BA_GlowTrail）。**上下对称**。",
     f"{CR} and {VI}",
     f"a VENOM GLOB flying to the RIGHT, 2 frames, a seamless loop, {TB}: a crimson venom drop 5 squares long and 3 tall with a "
     "white core at its front; a short violet smoke tail 5 squares long behind it, flickering between the two frames.",
     row(2, 14, 6) + "; the glob's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_bolt", "Q 神经毒素：毒液弹（朝目标飞，循环），4 帧", "view_projectiles `league_elise_q_bolt`（朝飞行方向转，画成朝右飞；上下对称）",
     "20 × 8", "神经毒素：一颗更大的毒液弹，深红色的芯外面缠着一圈紫色的毒烟，后面拖一条渐细的紫红色尾巴和几点毒液火星（参考 Q_Mis_Shockwaves、Elise_Qtrail、Q_Sharp）。**上下对称**。",
     f"{CR} and {VI}",
     f"a NEUROTOXIN BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a crimson venom orb 6 squares across with a white "
     "core, wrapped in a ring of violet toxic smoke 2 squares thick; a tapering violet-and-crimson trail 10 squares long behind "
     "it; 2 crimson motes at mirrored places flickering in turn.",
     row(4, 22, 10) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_elise_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "毒液打中：一小团深红色的毒液溅开（白芯），几滴往外飞（参考 Star_Flash）。**左右对称**。约 10 格。", CR,
     f"a SMALL VENOM SPLASH on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a crimson splash 7 squares across with a white "
     "core; 3 the splash 10 squares, 6 droplets flying out at mirrored places; 4 a few fading droplets.",
     row(4, 12, 12) + CENTER),
    ("q_hit", "Q 神经毒素打中（目标身上），5 帧", "view_effects `league_elise_q_hit`（跟随，画在人物上面；左右对称）", "18",
     "神经毒素命中：一团深红色的毒液炸开（白芯），外面一圈紫色的毒烟往外翻卷，几滴毒液溅出（参考 Q_Impact03、Q_SmokeErosionT）。**左右对称**。约 18 格。",
     f"{CR} and {VI}",
     f"a NEUROTOXIN IMPACT on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 a crimson venom burst 10 squares across with a "
     "white core; 3 the burst 16 squares across, violet smoke curling out at both sides; 4 the smoke 18 squares, venom droplets "
     "at mirrored places; 5 fading smoke and droplets.",
     row(5, 20, 20) + CENTER),
    # ---- the spider's attack and Venomous Bite, the passive's spiderlings
    ("c_hit", "蜘蛛普攻打中（目标身上），4 帧", "view_effects `league_elise_c_hit`（跟随，画在人物上面；左右对称）", "12",
     "蜘蛛前腿刺中：两道深红色的弯钩刺痕从左右两边同时划下、交在中间，交点一闪（参考 Q_bite、Impacts02_ErosionSheet）。**左右对称**。约 12 格。", CR,
     f"a STAB-HIT on a unit, 4 frames, {LR}: two curved crimson hook marks sweeping DOWN from the upper left and upper right at "
     "once, meeting in the middle; 1 the two hooks starting 8 squares apart; 2 the hooks meeting, a white flash 3 squares where "
     "they meet; 3 the marks 12 squares tall, the flash fading; 4 the marks fading.",
     row(4, 14, 14) + CENTER),
    ("cq_hit", "Q 剧毒之蜇打中（目标身上），5 帧", "view_effects `league_elise_cq_hit`（跟随，画在人物上面；左右对称）", "20",
     "剧毒之蜇：两颗巨大的弯毒牙从左右两边合拢咬下（参考 Q_bite 那对白色的弯牙），咬合处喷出一团深红的毒液和紫色的毒烟。**左右对称**。约 20 格。",
     f"{CR} and {VI}",
     f"a VENOMOUS BITE on a unit, 5 frames, {LR}: two huge curved fangs, white with crimson tips, closing in from the left and the "
     "right; 1 the fangs wide apart 18 squares, open; 2 the fangs closing; 3 the fangs meeting in the middle, a crimson venom "
     "burst 12 squares with a white core between them; 4 the burst 20 squares, violet smoke at both sides; 5 the fangs gone, "
     "fading venom droplets.",
     row(5, 22, 22) + CENTER),
    bites(1), bites(2), bites(3),
    # ---- Cocoon, Volatile Spiderling
    ("e_web", "E 结茧：飞出去的茧（朝目标飞，循环），4 帧", "view_projectiles `league_elise_e_web`（朝飞行方向转，画成朝右飞；上下对称）",
     "16 × 9", "结茧：一团旋转的蛛丝茧（灰白色的丝一圈圈缠着，中间一点红光），后面拖几根蛛丝（参考 E_Cocoon、E_SpiderWeb_01、E_Trail）。**上下对称**。",
     f"{SK} and {CR}",
     f"a SPINNING COCOON flying to the RIGHT, 4 frames, a seamless loop, {TB}: a ball of grey-white silk 7 squares across, strands "
     "wound round it, a small crimson glint at its centre, the strands' bright lines moving round between frames; 3 silk "
     "threads 7 squares long trailing behind it, mirrored above and below.",
     row(4, 18, 10) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_hit", "E 结茧：被茧住的目标（目标身上），6 帧", "view_effects `league_elise_e_hit`（跟随，画在人物上面；左右对称）", "16 × 26",
     "被茧住（晕眩）：一层层灰白色的蛛丝从脚下往上缠住目标，缠成一个茧的轮廓，丝上有几点红光（参考 E_Cocoon、Elise_OuterWeb、E_SoftStrings）。"
     "第 4 帧会停很久（晕眩约 1.7 秒）。**左右对称**，丝可以横着盖过身体，但不要画成实心的一团。",
     f"{SK} and {CR}",
     f"a SILK COCOON wrapping a figure, 6 frames, {LR} (an upright figure 10 squares wide and 22 tall stands in the middle, not "
     "drawn): 1 silk strands shooting up from the ground at both sides; 2 strands wrapping round the legs, crossing in front; "
     "3 the strands up to the shoulders, a cocoon outline 14 squares wide and 24 tall; 4 the full cocoon of crossing strands "
     "with gaps between them, 3 crimson glints at mirrored places (this frame is held for a second and a half); 5 the strands "
     "snapping at both sides; 6 loose strands falling.",
     row(6, 16, 28) + "; centered across, the figure's feet on the cell's bottom row."),
    ("w_spider", "W 自爆蜘蛛：爬过去的小蜘蛛（朝目标走，循环），4 帧", "view_projectiles `league_elise_w_spider`（朝飞行方向转，画成朝右爬；上下对称）",
     "10 × 10", "自爆蜘蛛：一只从上往下看的黑色小蜘蛛，头朝右，背上发着红光，八条腿上下对称地交替迈步（参考 W_SpiderShape、W_SpiderEyes_01、EliseSpiderling）。**上下对称**。",
     f"{CH} and {CR}",
     f"a SMALL SPIDER seen from ABOVE crawling to the RIGHT, 4 frames, a seamless loop, {TB}: a black body 5 squares long, a "
     "glowing crimson back with a white-hot spot, red eye dots at the head's front (right), four legs above and four below "
     "mirrored, stepping in turn (frames 1-2 the front pairs forward, 3-4 the back pairs), the back's glow pulsing.",
     row(4, 12, 12) + CENTER),
    ("w_boom", "W 自爆蜘蛛爆炸（地上，不跟随），6 帧", "view_effects `league_elise_w_boom`（不跟随，地上；左右对称；大图表）", "22 × 18",
     "小蜘蛛爆炸：地上炸开一团深红色的毒液火光（白芯），一圈扁扁的冲击环在地面扩开，紫色的毒烟往上翻，几块小碎片飞出（参考 W_WaveExplosion、W_Flame_Ring、W_GroundDecal）。**左右对称**。",
     f"{CR} and {VI}",
     f"a SPIDERLING BLAST on the ground, 6 frames, {LR}: 1 a white flash 4 squares on the ground; 2 a crimson fireball 10 squares "
     "across with a white core, a flat ground ring 14 wide and 5 tall; 3 the blast 16 squares, the ring 20 wide; 4 violet smoke "
     "rising at both sides, the ring 22 wide and fading, small bits flying out at mirrored places; 5 smoke and a few embers; "
     "6 the last wisps.",
     row(6, 24, 20) + "; centered across, the ground ring's middle 4 squares above the cell's bottom row."),
    ("w_hit", "W 自爆蜘蛛波及（被炸到的目标身上），3 帧", "view_effects `league_elise_w_hit`（跟随，画在人物上面；左右对称）", "10",
     "被爆炸波及：目标身上一小团深红的毒火闪一下。**左右对称**。约 10 格。", CR,
     f"a SMALL BLAST-HIT on a unit, 3 frames, {LR}: 1 a crimson flash 6 squares with a white core; 2 the flash 10 squares with 4 "
     "short rays; 3 fading embers.",
     row(3, 12, 12) + CENTER),
    # ---- Rappel, Skittering Frenzy
    ("ce_up", "E 盘丝：升空的蛛丝（她身上，跟随），5 帧", "view_effects `league_elise_ce_up`（跟随她，画在人物上面；左右对称；大图表）", "12 × 60",
     "盘丝：一根白亮的蛛丝从天上垂下来粘在她背上，绷紧，把她拉上去（丝从上往下垂、最后整根往上收回）（参考 E_SoftStrings、E_DebrisString）。**左右对称**，丝在格子正中间竖直。",
     f"{SK} and {CR}",
     f"a SILK THREAD from the sky, 5 frames, {LR}: one vertical grey-white silk thread 1 square thick with a bright white core line, "
     "in the middle column; 1 the thread dropping from the cell's top, its end 20 squares down; 2 the thread reaching down to a "
     "small 4-square web anchor at 16 squares above the cell's bottom (the creature's back), a crimson glint at the anchor; 3 the "
     "thread taut, a few short silk strands at the anchor; 4 the anchor and the thread pulled UP to halfway; 5 only the top of "
     "the thread, pulled up out of sight.",
     row(5, 12, 60) + "; the thread in the middle column of every cell."),
    ("ce_land", "E 盘丝落地（地上，不跟随），6 帧", "view_effects `league_elise_ce_land`（不跟随，地上；左右对称；大图表）", "26 × 12",
     "盘丝落地：地面一圈尘土和碎石溅起，地上留下一张蛛网形状的裂纹，几根断丝飘起（参考 E_FootCrater、E_Rocks_2X2、E_DebrisString）。**左右对称**，中间落地的身体位置留空。",
     f"{ER} and {SK}",
     f"a HEAVY LANDING on the ground, 6 frames, {LR}, the middle above the ground EMPTY (the spider lands there): 1 a flat dust "
     "ring 10 wide and 3 tall; 2 the dust ring 20 wide, 6 rock chips flying up at mirrored places; 3 the dust 26 wide and 8 tall "
     "at both sides, a spider-web crack 16 wide and 4 tall on the ground under it in grey-white silk; 4 the dust settling, the web "
     "crack clear; 5 the web crack and a few broken silk strands floating up; 6 the crack fading.",
     row(6, 28, 14) + "; centered across, the ground crack's middle 3 squares above the cell's bottom row."),
    ("ce_hit", "E 盘丝落地打中（目标身上），4 帧", "view_effects `league_elise_ce_hit`（跟随，画在人物上面；左右对称）", "12",
     "盘丝落地砸中：目标身上一闪深红的冲击光，几根白丝溅开。**左右对称**。约 12 格。", f"{CR} and {SK}",
     f"a LANDING IMPACT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a crimson burst 9 squares with a white core; 3 the "
     "burst 12 squares, 4 short silk strands flying out at mirrored places; 4 fading.",
     row(4, 14, 14) + CENTER),
    ("cw_frenzy", "W 掠行狂暴：狂暴发作（她身上），5 帧", "view_effects `league_elise_cw_frenzy`（跟随她，画在人物上面；左右对称）", "52 × 34",
     "掠行狂暴：蜘蛛身上腾起一圈深红色的狂暴火焰和红色的速度光痕，从身体两边往上冲（参考 W_Glow、W_Sparks）。**左右对称**，中间蜘蛛的身体位置留空（只画外圈）。",
     CR,
     f"a FRENZY FLARE round a wide crouching creature, 5 frames, {LR}, the middle EMPTY (a clear area 44 squares wide and 26 tall "
     "where the creature is, not drawn): 1 crimson sparks at both sides on the ground; 2 crimson flame tongues rising at both "
     "sides 16 squares tall with white cores; 3 the flames 26 squares tall, red speed streaks at mirrored places; 4 the flames "
     "breaking into sparks; 5 a few last sparks.",
     row(5, 52, 34) + "; centered across, the creature's feet on the cell's bottom row."),
    ("cw_on", "W 掠行狂暴：攻速加成（她脚下，循环），4 帧", "view_buffs `league_elise_cw_on`（跟随，画在人物下面；左右对称）", "42 × 8",
     "狂暴中：蜘蛛脚下一圈深红色的光环（扁椭圆，几点红光轮流闪）。**左右对称**。", CR,
     f"a CRIMSON RING under a wide creature's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 40 squares wide and 6 tall "
     "in crimson, 4 bright motes on it at mirrored places taking turns to light up.",
     row(4, 44, 8) + CENTER),
    # ---- the turns, the ult
    ("tf_spider", "变成蜘蛛（她身上，跟随），6 帧", "view_effects `league_elise_tf_spider`（跟随她，画在人物上面；左右对称；大图表）", "44 × 44",
     "人变蜘蛛：一团暗紫色的烟从她身上卷起把她整个盖住，烟里闪着深红的火星，烟散开时露出蜘蛛（参考 Tendril_Smoke、Smoke_01、E_SpiderDesign_BackgroundBlur、R_LensFlare）。**左右对称**。这一下要把她盖住。",
     f"{VI} and {CR}",
     f"a DARK TRANSFORMATION burst over a figure, 6 frames, {LR}: 1 violet smoke tendrils curling up at both sides of the ground; "
     "2 the smoke 24 squares tall, crimson sparks inside; 3 the smoke a full cloud 40 squares wide and 40 tall covering the "
     "middle, a white-crimson flash at its centre; 4 the cloud breaking open from the top, crimson sparks flying out at mirrored "
     "places; 5 smoke wisps low at both sides; 6 the last wisps.",
     row(6, 44, 44) + "; centered across, the cloud's bottom on the cell's bottom row."),
    ("tf_human", "变回人形（她身上，跟随），6 帧", "view_effects `league_elise_tf_human`（跟随她，画在人物上面；左右对称；大图表）", "44 × 44",
     "蜘蛛变回人：暗紫色的烟从地面往上旋起、裹成一个人形高的烟柱，顶上一闪深红的光，烟往上散开（同一套颜色）。**左右对称**。这一下要把她盖住。",
     f"{VI} and {CR}",
     f"a DARK TRANSFORMATION rising over a creature, 6 frames, {LR}: 1 violet smoke spreading flat on the ground 40 squares wide; "
     "2 the smoke swirling up into a column 30 squares tall; 3 the column 40 tall and 24 wide covering the middle, crimson sparks "
     "spiralling in it; 4 a crimson-white flash at the top, the column opening; 5 smoke wisps drifting up at both sides; 6 the "
     "last wisps high up.",
     row(6, 44, 44) + "; centered across, the smoke's bottom on the cell's bottom row."),
    ("r_cast", "大招 茧缚猎杀：发动（她头顶，跟随），5 帧", "view_effects `league_elise_r_cast`（跟随她，画在人物上面；左右对称；大图表）", "20 × 44",
     "茧缚猎杀发动：她头顶浮出一个深红色发光的蜘蛛印记（参考 E_SpiderDesign_BackgroundBlur 的蜘蛛形状），八只红眼一闪，然后化成红光散开。**左右对称**。画在格子上部。",
     f"{CR} and {VI}",
     f"a SPIDER SIGIL over a head, 5 frames, {LR}: 1 a crimson glow 4 squares; 2 a spider-shaped sigil 14 squares wide and 12 tall "
     "(a round body, eight thin legs spread, mirrored) in crimson with a white core outline; 3 the sigil brightest, eight red eye "
     "dots flashing on its head; 4 the sigil breaking into crimson motes; 5 a few last motes.",
     row(5, 20, 44) + "; the sigil's middle 8 squares from the TOP of the cell, centered; the rest of the cell empty."),
]

GROUPS = [
    ("a_spit q_*", ["Elise_Base_BA_Head_01", "Elise_Base_BA_Streak", "Elise_Base_BA_GlowTrail", "Elise_Base_Q_Impact03",
                    "Elise_Base_Q_Mis_Shockwaves", "Elise_Base_Star_Flash"]),
    ("e_*", ["Elise_Base_E_Cocoon", "Elise_Base_E_SpiderWeb_01", "Elise_E_Web", "Elise_Base_E_SoftStrings",
             "Elise_OuterWeb", "Elise_Base_E_Trail"]),
    ("w_* sl_*", ["Elise_Base_W_SpiderShape", "Elise_Base_W_SpiderEyes_01", "EliseSpiderling_base_TX_CM",
                  "Elise_Base_W_WaveExplosion", "Elise_Base_W_Flame_Ring", "Elise_Base_W_GroundDecal"]),
    ("c_* cq_* cw_*", ["Elise_Base_Q_bite", "Elise_Base_Impacts02_ErosionSheet", "Elise_Base_Trail01C",
                       "Elise_Base_W_Glow", "Elise_Base_W_Sparks", "Elise_Base_Q_Sharp"]),
    ("ce_*", ["Elise_Base_E_SoftStrings", "Elise_Base_E_DebrisString", "Elise_Base_E_FootCrater", "Elise_Base_E_Rocks_2X2",
              "Elise_Base_E_Plume_Head", "Elise_Base_E_Mist"]),
    ("tf_* r_*", ["Elise_Base_Tendril_Smoke", "Elise_Base_Smoke_01", "Elise_Base_E_SpiderDesign_BackgroundBlur",
                  "Elise_Base_R_LensFlare", "Elise_Base_SharpSmoke", "Elise_Base_E_OilySmoke_2x2"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_spit：吐毒出手"), ("skill", 3, "q_bolt：神经毒素"), ("skill2", 3, "e_web / w_spider：结茧、自爆蜘蛛"),
         ("transform", 3, "tf_spider：变蜘蛛（烟盖住她）"), ("c_attack", 3, "c_hit：刺击"), ("c_skill", 4, "cq_hit：剧毒之蜇"),
         ("c_skill2", 4, "ce_up：盘丝升空"), ("c_land", 2, "ce_land：落地"), ("c_transform", 3, "tf_human：变回人")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Elise_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    """The 1x frames of a tag, read from the sheet and the fanim."""
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
    """Her 1x idles (both forms) at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter."""
    import tfm2_ase as T
    figs = [first_1x("idle"), first_1x("c_idle")]
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
    d.text((8, 36), f"人形 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连背后的蜘蛛腿），蜘蛛 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape, figs[1].shape


def shots_sheet(path):
    """The finished action frames at 4x (the 1x sheet), her standing point as a cyan cross."""
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
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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


def document(shapes):
    (hh, hw), (ch, cw) = (s[:2] for s in shapes)
    L = []
    a = L.append
    a("# 蜘蛛女皇 伊莉丝：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/elise_idle.png`：人形 3/4 正面待机，背后六条蜘蛛腿；蜘蛛 3/4 视角朝右）。"
      f"她在游戏里是**高清**的（每个游戏格子里 1.8×1.8 个细像素），人形连背后的蜘蛛腿 {hh} 格高、{hw} 格宽，蜘蛛 {ch} 格高、{cw} 格长；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/elise_size.png`：两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/elise_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里伊莉丝自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**毒液和撕咬是深红色的光（白芯）配紫色的毒烟**，**茧和蛛丝是灰白色的丝（白芯）带一点红光**，"
      "**小蜘蛛是黑色的、背上发红光**，**变身是暗紫色的烟加深红的火星**。")
    a("> - **特效要亮**：每团光、每根丝都要有白色或最亮一档的芯，暗底上一眼能看见（她本人很暗，特效尤其要亮）。")
    a("> - **围着人的光圈、火焰只画外圈和两边，中间身体位置留空**（变身 `tf_spider` / `tf_human` 例外：那一下就是要把她盖住；"
      "茧 `e_hit` 的丝可以横着盖过身体，但要有空隙）。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_spit`、`q_bolt`、`e_web`、`w_spider`（从上往下看的小蜘蛛）画成朝右，**上下对称**（往左飞时会上下翻）。"
      "其余所有画面（打中、身上、脚下、头顶、地上的爆炸和落地、蛛丝）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）——刺痕、毒牙一律两边同时合拢，不要画成往一个方向斜的。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `elise_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `elise_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「蜘蛛女皇」 | 人形吐毒液 / 蜘蛛前腿刺击；人形技能命中积攒小蜘蛛，蜘蛛普攻时小蜘蛛扑上去撕咬 | `a_spit` · `a_hit` · `c_hit` · `sl_bite1` · `sl_bite2` · `sl_bite3` |")
    a("| 技能 1 = Q「神经毒素 / 剧毒之蜇」 | 人形：毒液弹；蜘蛛：扑上去咬 | `q_bolt` · `q_hit` · `cq_hit` |")
    a("| 技能 2 = E「结茧」+ W「自爆蜘蛛」/ E「盘丝」+ W「掠行狂暴」 | 人形：吐茧晕眩、放会爆炸的小蜘蛛；蜘蛛：顺着丝升空落到英雄身上、狂暴加攻速 | "
      "`e_web` · `e_hit` · `w_spider` · `w_boom` · `w_hit` · `ce_up` · `ce_land` · `ce_hit` · `cw_frenzy` · `cw_on` |")
    a("| 变身（普攻时自动）+ 大招「蜘蛛形态」茧缚猎杀 | 人和蜘蛛来回切换；5 级大招吐茧、变蜘蛛、盘丝落到英雄身上咬 | `tf_spider` · `tf_human` · `r_cast` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火星、蛛丝、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（小蜘蛛例外：它的黑色身体可以有一圈深色边）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("深红毒液（毒液、撕咬、狂暴）", CRIMSON), ("紫色毒烟（毒烟、变身）", VIOLET), ("蛛丝（茧、盘丝的丝）", SILK),
                        ("小蜘蛛的身体", CHITIN), ("尘土（落地）", EARTH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人或蜘蛛**（小蜘蛛的几张除外：小蜘蛛本身就是特效）。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：人形普攻距离 50000，"
      "结茧射程 75000，自爆蜘蛛爆炸半径 10000，盘丝落地半径 12000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `elise_fx_{name}.png`：{title}\n")
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
        a(f"| `elise_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_elise_fx`（小的）和 `league_elise_big`（w_boom、ce_up、ce_land、tf_spider、tf_human、r_cast），tag = 名字（build_elise.py 的 views）。")
    a("- `a_spit`、`q_bolt`、`e_web`、`w_spider` 是飞行投射物，画面朝飞行方向转；`w_boom`、`ce_land` 不跟随；`cw_on` 脚下 buff（z -1）；`r_cast` 头顶；`e_hit` 第 4 帧拉长到晕眩的 100 tick。")
    a("- 用 `pixel_1x/` 切格（import_nidalee 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="elise_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "elise_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/el_work/fx_ref_el.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hum = np.asarray(Image.open(lp(os.path.join(HD, "human.png"))).convert("RGBA"))
    spi = np.asarray(Image.open(lp(os.path.join(HD, "spider.png"))).convert("RGBA"))
    H = max(hum.shape[0], spi.shape[0])
    both = np.zeros((H, hum.shape[1] + 12 + spi.shape[1], 4), np.uint8)
    both[H - hum.shape[0]:, :hum.shape[1]] = hum
    both[H - spi.shape[0]:, hum.shape[1] + 12:] = spi
    Image.fromarray(np.repeat(np.repeat(both, 3, 0), 3, 1)).save(os.path.join(out, "design", "elise_idle.png"))
    shapes = size_sheet(os.path.join(out, "design", "elise_size.png"))
    shots_sheet(os.path.join(out, "design", "elise_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"elise_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shapes)
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
