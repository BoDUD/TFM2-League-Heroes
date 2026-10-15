#!/usr/bin/env python3
"""Build katarina_fx_pack.zip: step 3 of Katarina's sprite - Codex draws her effects (tools/art/pack_jayce_fx.py's way:
effects at game pixels, plus pictures drawn into her own dense frames).

    python tools/art/pack_katarina_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name katarina_fx_redo_pack]

The pack (%LOCALAPPDATA%/Temp/kt_packs/fx/katarina_fx_pack, zipped into --out, default %LOCALAPPDATA%/Temp/kt_packs)
holds PROMPTS.md (also written to assets/source/katarina/PROMPTS_FX.md), design/katarina_designs.png (the front and
side designs at 3x), design/katarina_size.png (her 1x idle at 4x on the arena colour with the feet line, a 10-px ruler
and the base fighter), design/katarina_shots.png (finished action frames, 1x at 4x, the points her pictures start from),
bake/katarina_bake_<name>_<n>.png (the frame a picture is drawn INTO: her finished dense frame - the hd_ tag of
league/champions/league_katarina, 1.5 squares a game pixel - faded on a guide canvas at BAKE_PX px a square, the point
it starts from as a cross) and refs/lol_fx_ref.png (League's own particle textures for Katarina, grouped by the effect
of ours they inform; Riot's art, local only: %LOCALAPPDATA%/Temp/kt_packs/fxref, from Temp/kt_packs/fx/fx_ref_kt.py).
The effects are the views the kit binds (tools/kit/build_katarina.py: view_projectiles q_blade, r_dagger; view_effects
a_hit, q_hit, q_arc, d_fall, d_stuck, p_hit, spin, e_out, e_in, e_hit, w_toss, p_reset, r_hit, r_lotus; view_buffs
w_ms, r_gw) and the pictures drawn into her frames at import (BAKE): the client mirrors her frames with her facing and
never an effect picture, so whatever has a front and a back on her - the thrust's streak, the throw's arc, Shunpo's
slash - rides in the frames (art-spec, league_jayce / league_milio).
League's colours: Katarina's blade light is crimson with white-hot cores (her R_Color / CritTrail), her daggers silver,
Shunpo's smoke dark crimson, the dagger on the ground a gold fire line (Dagger_FireLine). Light gets no outline. Red
side: projectiles symmetric for their turn (the spinning blade the same turned half round, the flying dagger top to
bottom); pictures on a unit, on the ground and the buffs symmetric left to right.
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
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "kt_packs")
REF = os.path.join(TMP, "fxref")
SRC = os.path.join(ROOT, "assets", "source", "katarina")
DOC = os.path.join(SRC, "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_katarina")
HD = os.path.join(SRC, "hd")
PRE = chr(92) * 2 + "?" + chr(92)
FEET = 11.5                         # 1x px from the pivot down to the soles' bottom edge
HD_PPU = P.PPU["katarina"]          # her finished dense frames (1.5 squares a game pixel)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


CRIM = "#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18"      # her blade light: white core, pink, crimson, wine
STEEL = "#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A"              # her daggers' silver
SMOKE = "#FFD6DC, #E8455A, #A8203A, #6C1428, #3A0C18"              # Shunpo's crimson smoke
GOLD = "#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E"                # the dagger's fire line on the ground (League's FireLine)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and "
        "a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, {px} px a square)"
CR_ = f"a crimson blade-light ramp ({CRIM})"
ST_ = f"a dagger-steel ramp ({STEEL})"
SM_ = f"a crimson smoke ramp ({SMOKE})"
GO_ = f"a gold fire ramp ({GOLD})"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
PT = ("POINT-SYMMETRIC in every frame: it looks exactly the same turned half round about its centre, square for square "
      "(the game turns it to its flight; flying left it is upside down)")
TB = "SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight)"
CENTER = "; centered in every cell."


def row(n, cw, ch, px=16):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * px, h=ch * px, cw=cw * px, ch=ch * px, px=px)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- in flight (turned to their flight)
    ("q_blade", "Q 弹射之刃：旋转飞行的匕首（循环），4 帧",
     "view_projectiles `league_katarina_q_blade`（朝飞行方向转；转半圈看起来一样）", "11 × 11",
     "Q 扔出的匕首在空中高速旋转：两把交叉的银白弯刃组成的小风车，刃尖带一圈深红的刀光残影（参考 Q_Blade_Trail、Q_Blade_Loopies）。"
     "**转半圈看起来一样（点对称）**，4 帧依次转 45°，无缝循环。约 11 格见方。", f"{ST_} and {CR_}",
     f"a SPINNING THROWN DAGGER, 4 frames, a seamless loop, {PT}: two curved silver blades crossed at the centre "
     "(a small pinwheel 11 squares across), a thin crimson blur arc trailing each blade's tip; each frame turned 45 "
     "degrees further than the last.",
     row(4, 13, 13) + CENTER),
    ("r_dagger", "R 死亡莲华：飞向敌人的匕首（循环），2 帧",
     "view_projectiles `league_katarina_r_dagger`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 4",
     "死亡莲华每 1/6 秒掷向敌人的匕首：一把朝右飞的细长银白匕首，后面一条深红的刀光尾巴（参考 R_Mis_Trail、R_BlurryBlade）。"
     "**上下对称**。2 帧（尾巴一闪）。约 10 格长、4 格高。", f"{ST_} and {CR_}",
     f"a FLYING DAGGER to the RIGHT, 2 frames, {TB}: a slim silver blade 5 squares long with a white edge pointing "
     "right, a dark hilt 1 square, a crimson trail 5 squares long tapering behind it; the trail flickers.",
     row(2, 12, 6) + "; the blade's point 1 square from the RIGHT edge, vertically centered, in every cell."),
    # ---- on a target (follow, over the figure)
    ("a_hit", "普攻刺中（目标身上），4 帧", "view_effects `league_katarina_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "匕首刺中：一个白亮的小十字闪光，两道交叉的深红刀痕（X 形）（参考 z_hit_flash、CritTrail）。**左右对称**。约 12 格。", CR_,
     f"a DAGGER HIT, 4 frames, {LR}: 1 a white star flash 4 squares across; 2 two crossed crimson slash marks (an X) 11 "
     "squares across with white cores; 3 the X at its brightest with 4 tiny sparks; 4 the X fading to wine red.",
     row(4, 14, 14) + CENTER),
    ("q_hit", "Q 飞刀打中（每个目标身上），4 帧", "view_effects `league_katarina_q_hit`（跟随，画在人物上面；左右对称）", "12",
     "旋转的匕首打中：一圈横着的深红刀光划过，中间一个白闪（参考 Q_Blade_Glows、z_hit_flash）。**左右对称**。约 12 格。",
     f"{CR_} and {ST_}",
     f"a SPINNING-BLADE HIT, 4 frames, {LR}: 1 a white flash 4 squares; 2 a flat crimson slash ring 12 squares wide and "
     "4 tall round the flash; 3 the ring with silver glints at its two ends; 4 fading.",
     row(4, 14, 14) + CENTER),
    ("q_arc", "Q 匕首从第一个目标身上弹起、飞向空中（目标处，不跟随），5 帧",
     "view_effects `league_katarina_q_arc`（不跟随，画在人物上面；左右对称）", "8 × 30",
     "飞刀打中第一个目标后匕首往天上弹起：一把旋转的银白匕首从下往上飞出画面，拖一道竖直的深红刀光（参考 Q_Blade_Trail）。"
     "**左右对称**（匕首画成竖直、刀光在正中）。约 8 格宽、30 格高。", f"{ST_} and {CR_}",
     f"a DAGGER FLYING STRAIGHT UP, 5 frames, {LR}: an upright silver dagger 6 squares long spinning end over end (drawn "
     "point-up or point-down, centered) rising from the bottom of the cell to the top over the 5 frames, a thin crimson "
     "trail 2 squares wide below it growing longer then fading; in frame 5 only the trail's top is left.",
     row(5, 10, 32) + "; centered across; frame 1's dagger on the cell's bottom rows."),
    ("p_hit", "捡起匕首旋斩打中的敌人（每个目标身上），3 帧",
     "view_effects `league_katarina_p_hit`（跟随，画在人物上面；左右对称）", "12",
     "旋斩扫到的敌人：一道横着的深红刀痕，中间白闪（参考 Dagger_Pickup_Slash）。**左右对称**。约 12 格。", CR_,
     f"a SWEEPING SLASH HIT, 3 frames, {LR}: 1 a flat crimson slash line 12 squares wide and 2 tall with a white core; 2 "
     "the line with a white flash 4 squares in its middle; 3 fading.",
     row(3, 14, 10) + CENTER),
    ("e_hit", "E 瞬步落地打中的敌人（目标身上），4 帧", "view_effects `league_katarina_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "瞬步落地顺手一刀：一道竖着的深红刀光劈下，带几缕暗红烟（参考 E_LeadingEdge、z_hit_flash）。**左右对称**。约 14 格。",
     f"{CR_} and {SM_}",
     f"a SHUNPO STRIKE, 4 frames, {LR}: 1 a white flash 4 squares; 2 a crimson V-shaped double slash 14 squares across "
     "with white cores; 3 the slash fading, 4 small crimson smoke puffs at mirrored places; 4 smoke fading.",
     row(4, 16, 16) + CENTER),
    ("r_hit", "R 每把匕首打中（目标身上），3 帧", "view_effects `league_katarina_r_hit`（跟随，画在人物上面；左右对称）", "8",
     "死亡莲华每把匕首打中：一个小小的白闪 + 深红刀痕（参考 R_Tar_Impact）。**左右对称**。约 8 格（一秒打好几下，要小）。", CR_,
     f"a SMALL DAGGER HIT, 3 frames, {LR}: 1 a white flash 3 squares; 2 a small crimson X slash 8 squares across; 3 fading.",
     row(3, 10, 10) + CENTER),
    # ---- on her (casts)
    ("e_out", "E 瞬步消失（她原来站的地方，不跟随），5 帧",
     "view_effects `league_katarina_e_out`（不跟随，画在人物上面；左右对称）", "20 × 30",
     "瞬步离开的一瞬：她站的地方炸开一团深红的烟，几道往外散的刀光残影，烟往上飘散（参考 base_z_smoke、E_trail、E_LeadingEdge）。"
     "**左右对称**，中间人形位置**留空**（8 格宽）。约 20 格宽、30 格高。", f"{SM_} and {CR_}",
     f"a SHUNPO VANISH, 5 frames, {LR}, a clear upright gap 8 squares wide in the middle (where she stood): 1 a ring of "
     "crimson smoke puffs at her feet 20 squares across; 2 the smoke rising up both sides to 26 squares with 4 crimson "
     "streaks flying out; 3 the smoke at full height 30 squares; 4 thinning; 5 the last wisps at the top.",
     row(5, 22, 32) + "; centered across, the smoke's foot on the cell's bottom rows."),
    ("e_in", "E 瞬步出现（她落地的地方，不跟随），4 帧",
     "view_effects `league_katarina_e_in`（不跟随，画在人物上面；左右对称）", "22 × 24",
     "瞬步落地：从上往下一道深红的刀光闪下，脚下炸开一圈暗红烟和刀光（参考 E_Mis_Ring、E_LeadingEdge、base_z_smoke）。"
     "**左右对称**，中间人形位置**留空**（8 格宽）。约 22 格宽、24 格高。", f"{SM_} and {CR_}",
     f"a SHUNPO ARRIVAL, 4 frames, {LR}, a clear upright gap 8 squares wide in the middle: 1 two crimson streaks diving "
     "down both sides to her feet; 2 a flat burst of crimson smoke and slash light at her feet 22 squares across; 3 the "
     "burst spreading, 6 tiny sparks; 4 wisps fading.",
     row(4, 24, 26) + "; centered across, the burst on the cell's bottom rows."),
    ("w_toss", "W 伺机待发：抛向空中的匕首（她身边，不跟随），6 帧",
     "view_effects `league_katarina_w_toss`（不跟随，画在人物上面；左右对称）", "8 × 40",
     "W 把匕首往正上方抛：一把银白匕首旋转着往天上飞出画面，带一道细细的深红光（参考 Q_Blade_Trail、R_BlurryBlade）。"
     "**左右对称**（匕首竖直、在正中）。约 8 格宽、40 格高（底部在她举起的手的高度）。", f"{ST_} and {CR_}",
     f"a DAGGER TOSSED STRAIGHT UP, 6 frames, {LR}: an upright silver dagger 6 squares long spinning end over end, rising "
     "from the bottom of the cell to the top over the 6 frames, a thin crimson glint trail 1-2 squares wide under it; in "
     "frame 6 only a glint at the very top.",
     row(6, 10, 42) + "; centered across; frame 1's dagger on the cell's bottom rows."),
    ("d_fall", "匕首落地（地上，不跟随），4 帧", "view_effects `league_katarina_d_fall`（不跟随，地上；左右对称）", "14 × 22",
     "Q / W 的匕首从天上落下、插进地面：一把竖直的银白匕首从上往下扎进地里，落点一圈尘土和金色火线（参考 Dagger_FireLine、Q_Blade_Ground_Crack）。"
     "**左右对称**。约 14 格宽、22 格高。", f"{ST_}, {GO_} and {CR_}",
     f"a DAGGER FALLING INTO THE GROUND, 4 frames, {LR}: 1 an upright silver dagger point-down near the top of the cell; "
     "2 the dagger halfway down, a thin gold streak above it; 3 the dagger stuck point-down in the ground (its point on "
     "the bottom row), a flat ring of gold sparks and dust 14 squares wide round its foot; 4 the dagger stuck, the "
     "ring fading.",
     row(4, 16, 24) + "; centered across, the ground on the cell's bottom rows."),
    ("d_stuck", "插在地上的匕首（地上，不跟随，每 2/3 秒重放一次，等她来捡），4 帧",
     "view_effects `league_katarina_d_stuck`（不跟随，地上；左右对称）", "10 × 14",
     "插在地上的匕首：一把竖直的银白匕首刀尖朝下插在地上，刀柄朝上，脚下一小圈金色火线一闪一闪（参考 Dagger_FireLine、R_Ring_Pickup）。"
     "**左右对称**。约 10 格宽、14 格高。4 帧连起来正好 2/3 秒（每帧约 10 tick）。", f"{ST_} and {GO_}",
     f"a DAGGER STUCK IN THE GROUND, 4 frames, {LR}: an upright silver dagger 11 squares tall point-down in the ground "
     "(the point on the bottom row, the dark hilt up), the same in every frame; a flat ring of gold fire 10 squares "
     "wide and 3 tall at its foot glowing brighter and dimmer frame by frame.",
     row(4, 12, 16) + "; centered across, the ground on the cell's bottom rows."),
    ("p_reset", "被动贪婪刷新（她身上，跟随），5 帧", "view_effects `league_katarina_p_reset`（跟随，画在人物上面；左右对称）", "26 × 34",
     "击杀刷新冷却：她身上一圈深红光往上一冲，几把小小的光刃绕着她转一下（参考 R_Reset_Ground、R_Success_Ray）。**左右对称**，"
     "中间人形位置**留空**（10 格宽）。约 26 格宽、34 格高。", CR_,
     f"a RESET SURGE, 5 frames, {LR}, a clear upright gap 10 squares wide in the middle: 1 a flat crimson ring at her feet "
     "20 squares across; 2 crimson rays rising up both sides 20 squares; 3 the rays at 34 squares with 4 small white "
     "blade glints at mirrored places; 4 the rays fading upward; 5 a few sparks at the top.",
     row(5, 28, 36) + "; centered across, the ring on the cell's bottom rows."),
    ("spin", "捡起匕首旋斩（她身边一圈，不跟随，大），5 帧",
     "view_effects `league_katarina_spin`（大表；不跟随，画在人物上面；左右对称）", "60 × 26",
     "捡起匕首原地旋身一斩：围着她一圈扁扁的深红刀光（从斜上方看的椭圆），刀光前沿白亮，后面拖着淡下去（参考 Dagger_Pickup_Slash、"
     "R_BlurryBlades）。**左右对称**，中间人形位置**留空**（12 格宽）。约 60 格宽、26 格高。", f"{CR_} and {ST_}",
     f"a SPIN SLASH round her, 5 frames, {LR}, a clear upright gap 12 squares wide in the middle: a flat ellipse of crimson "
     "blade light 60 squares wide and 22 tall seen from above at a slant (the ring's front half lower, the back half "
     "higher), drawn as two mirrored arcs sweeping from the back round both sides to the front; 1 short arcs at the back; "
     "2 the arcs halfway round with white leading edges; 3 the full ring, 6 silver glints; 4 the ring fading; 5 wisps.",
     row(5, 64, 30, 8) + "; centered, the ring's bottom 2 squares above the cell's bottom."),
    ("r_lotus", "R 死亡莲华：围着她旋转的刀圈（跟随，引导时每半秒重放），6 帧",
     "view_effects `league_katarina_r_lotus`（大表；跟随，画在人物上面；左右对称）", "50 × 30",
     "死亡莲华：她身边一圈快速旋转的刀光——扁椭圆上几把模糊的银白刀刃和深红残影一圈圈转，脚下一圈暗红光（参考 R_BlurryBlades_v2–v5、"
     "R_Ring_Indicator、R_Color）。**左右对称**，中间人形位置**留空**（12 格宽）。约 50 格宽、30 格高。6 帧正好半秒、首尾无缝。",
     f"{CR_} and {ST_}",
     f"a WHIRL OF BLADES round her, 6 frames, a seamless loop, {LR}, a clear upright gap 12 squares wide in the middle: a "
     "flat ellipse 50 squares wide and 20 tall seen from above (back half higher, front half lower) of 6 blurred silver "
     "blades with crimson trails sweeping round it, placed in mirrored pairs and moving round a step each frame; a "
     "faint crimson ring at her feet 40 squares wide.",
     row(6, 54, 34, 8) + "; centered, the feet ring 2 squares above the cell's bottom."),
    # ---- buffs
    ("w_ms", "W 的加速（她脚下，跟随，循环），4 帧", "view_buffs `league_katarina_w_ms`（她脚下；左右对称）", "20 × 8",
     "伺机待发的加速：她脚下两边几缕往后飘的深红风痕（参考 Global_SpeedBuff_Swirl，换成深红）。**左右对称**，中间留空 8 格。"
     "约 20 格宽、8 格高。", CR_,
     f"a SPEED SWIRL at the feet, 4 frames, a seamless loop, {LR}, a clear gap 8 squares wide in the middle: 2-3 short "
     "curved crimson wisps at each side near the ground, drifting outward and up a little each frame.",
     row(4, 22, 10) + "; centered across, the wisps on the cell's bottom rows."),
    ("r_gw", "R 的重伤（敌人头上，跟随，循环），4 帧", "view_buffs `league_katarina_r_gw`（敌人头上；左右对称）", "10",
     "重伤（治疗减少）：敌人头上一个小小的深红破碎心形 / 裂开的十字标记一闪一闪（参考英雄联盟的重伤图标）。**左右对称**。约 10 格。",
     CR_,
     f"a GRIEVOUS WOUNDS mark, 4 frames, a seamless loop, {LR}: a small crimson cracked heart 8 squares across with a "
     "dark crack down its middle and a white glint, pulsing brighter and dimmer.",
     row(4, 12, 12) + CENTER),
]
BIG = {"spin", "r_lotus"}



BAKE_PX = 6                          # guide px a square: 256 x 170 squares (or 170 x 256) on Codex's 1536 x 1024
LAND = (256, 170, (128, 85))         # canvas squares, the pivot's square (his frame centred on it)
PORT = (170, 256, (85, 128))
# the pictures drawn INTO her dense frames (they have a front and a back: the client mirrors her frames, not effects)
BAKE = [
    ("a_slash", "attack", (3,), "over", "普攻：匕首刺击的刀光（画进普攻第 3 帧）",
     "匕首往前刺到最远（青色十字是刀尖）：刀尖后面一道往前刺的细长深红刀光（直的，从她手边到刀尖再往前 6 格），刀尖一个白闪。画在她**上面**，别挡住脸。",
     CR_, {3: "a THRUST TRAIL along the dagger: a straight crimson streak of light 3-4 squares thick from her hand to "
              "the cyan cross (the dagger's point) and 6 squares beyond it, a white core, a small white star flash at the "
              "cyan cross; nothing over her face."}, "right"),
    ("q_throw", "skill", (3,), "over", "Q：甩出飞刀的一瞬（画进 Q 第 3 帧）",
     "空手往前甩出（青色十字是她伸出去的手）：手前方一道往前弯的深红刀光弧，手边一个白闪（匕首已经飞走，不画匕首）。画在她**上面**，别挡住脸。",
     CR_, {3: "a THROW ARC in front of the flung hand: a curved crimson arc of light 3 squares thick sweeping from above "
              "her shoulder down to the cyan cross (her empty hand) and 8 squares past it, a white flash 6 squares across "
              "at the cyan cross; no dagger; nothing over her face."}, "right"),
    ("e_slash", "blink", (2,), "over", "E 瞬步落地挥刀（画进瞬步第 2 帧）",
     "落地顺势往前挥（青色十字是前手的刀尖）：刀尖划出一道往右上弯的深红刀光弧，脚边几缕暗红烟。画在她**上面**，别挡住脸。",
     f"{CR_} and {SM_}", {2: "a SLASH ARC: a curved crimson arc of blade light 3-4 squares thick swept from low behind "
                             "her up to the cyan cross (the front dagger's point), a white leading edge at the cyan cross, "
                             "4 small crimson smoke puffs low at her feet; nothing over her face."}, "right"),
]
GROUPS = [
    ("blades / trails", ["Katarina_Base_Q_Blade_Trail", "Katarina_Base_Q_BladeTrail_Mult", "Katarina_Base_Q_Blade_Loopies",
                         "Katarina_Base_R_Mis_Trail", "Katarina_Base_R_BlurryBlade_v2", "Katarina_CritTrail"]),
    ("hits / slashes", ["Katarina_Base_z_hit_flash", "Katarina_Base_Dagger_Pickup_Slash", "Katarina_Base_R_Tar_Impact",
                        "Katarina_Base_Q_Blade_Glows", "Katarina_Base_E_Mis_Ring", "Katarina_Base_W_BlastShape"]),
    ("shunpo", ["Katarina_Base_E_LeadingEdge", "Katarina_Base_E_trail", "Katarina_base_z_smoke", "Katarina_Base_Q_Glow"]),
    ("dagger on the ground", ["Katarina_Base_Dagger_FireLine", "Katarina_Base_Q_Blade_Ground_Crack",
                              "Katarina_Base_R_Ring_Pickup", "Katarina_Base_R_Reset_Ground"]),
    ("death lotus", ["Katarina_Base_R_BlurryBlades_V2", "Katarina_Base_R_BlurryBlades_v3", "Katarina_Base_R_BlurryBlades_v4",
                     "Katarina_Base_R_BlurryBlades_v5", "Katarina_Base_R_Ring_Indicator_V2", "Katarina_Base_R_Success_Ray"]),
]
# where the pictures on her start (tag, frame, what, marks)
SHOTS = [("idle", 1, "w_ms / r_gw / e_in / e_out / p_reset / spin / r_lotus：她或目标身上（脚底在红线上）", "feet"),
         ("skill", 3, "q_blade：从甩出去的手飞出", ("q_throw", 3, "cyan")),
         ("attack", 3, "a_hit：刀尖", ("a_slash", 3, "cyan"))]

CELLS = {}                         # bake_guides' cells, for SHOTS' marks taken from them


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Katarina_Base_", "").replace("Katarina_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


SHEETS = {}


def frames_of(tag):
    if not SHEETS:
        SHEETS.update(P.read_sheet(SHEET))
    return [a for a, _ in SHEETS[tag]]


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def designs(path):
    pics = [crop(np.asarray(Image.open(os.path.join(HD, f)).convert("RGBA")))
            for f in ("front.png", "side.png")]
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + 12 * (len(pics) - 1)
    both = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        both[H - p.shape[0]:, x:x + p.shape[1]] = p
        x += p.shape[1] + 12
    Image.fromarray(np.repeat(np.repeat(both, 3, 0), 3, 1)).save(path)


def size_sheet(path):
    """His 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter."""
    import tfm2_ase as T
    fig = crop(frames_of("idle")[0])
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    kn = crop(np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA")))
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    top = max(fig.shape[0], kn.shape[0])
    img = Image.new("RGBA", (max(W * Z, 760), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
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
    d.text((8, 36), f"卡特琳娜 {fig.shape[1]}×{fig.shape[0]} 格（连匕首），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """Finished action frames (1x) at 4x, each picture's starting point as a cyan cross."""
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, marks in SHOTS:
        f = np.pad(frames_of(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px, py = f.shape[1] / 2.0, f.shape[0] / 2.0
        if marks == "feet":
            pts = [(px, py + FEET)]
        else:                          # a point of a bake guide (its dense frame centred on the pivot) in 1x px
            bn, bk, col = marks
            c = CELLS[(bn, bk)]
            x0, y0, W, H = c["frame"]
            cx, cy = c[col]
            pts = [(px + (cx + 0.5 - x0 - W / 2.0) / HD_PPU, py + (cy + 0.5 - y0 - H / 2.0) / HD_PPU)]
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


def bake_points(name, tag, k, a):
    """{"cyan": (x, y)} on the dense frame a (its pixels): the weapon's tip by the BAKE entry's rule - "right" the
    rightmost squares, "top" the topmost, "right_low" the rightmost of the lowest 40 %, "top_right" the squares furthest
    up and right (x - y)."""
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    rule = next(b[8] for b in BAKE if b[0] == name)
    if rule == "right":
        sel = xs >= xs.max() - 2
    elif rule == "top":
        sel = ys <= ys.min() + 2
    elif rule == "right_low":
        low = ys >= ys.max() - 0.4 * (ys.max() - ys.min())
        sel = low & (xs >= xs[low].max() - 2)
    else:
        v = xs - ys
        sel = v >= v.max() - 3
    return {"cyan": (float(xs[sel].mean()), float(ys[sel].mean()))}


def bake_guides(out):
    """bake/katarina_bake_<name>_<n>.png: the finished dense frame faded on the guide canvas (LAND or PORT squares at
    BAKE_PX, her pivot on the canvas' pivot square), a light grid every 10 squares, the ground line red, the frame's box
    grey, the points as crosses. -> {(name, n): {"canvas": [w, h], "frame": [x0, y0, w, h], "cyan" / "yellow": [x, y]}}."""
    cells = {}
    for name, tag, ks, *_ in BAKE:
        for k in ks:
            a = frames_of("hd_" + tag)[k - 1]
            H, W = a.shape[:2]
            CW, CH, (gx, gy) = LAND if H / 2 <= LAND[2][1] - 4 and W / 2 <= LAND[2][0] else PORT
            x0, y0 = gx - W // 2, gy - H // 2
            assert x0 >= 0 and y0 >= 0 and x0 + W <= CW and y0 + H <= CH, (name, k, W, H)
            can = np.zeros((CH, CW, 4), np.uint8)
            can[y0:y0 + H, x0:x0 + W] = a
            img = Image.new("RGB", (CW * BAKE_PX, CH * BAKE_PX), (36, 40, 52))
            g = np.asarray(Image.fromarray(can).resize((CW * BAKE_PX, CH * BAKE_PX), Image.NEAREST)).astype(float)
            m = g[..., 3:] / 255.0
            grey = g[..., :3].mean(-1, keepdims=True) * 0.35 + 70
            base = np.asarray(img).astype(float)
            img = Image.fromarray((base * (1 - m) + grey * m).astype(np.uint8))
            d = ImageDraw.Draw(img)
            for x in range(0, CW + 1, 10):
                d.line([(x * BAKE_PX, 0), (x * BAKE_PX, img.height)], fill=(52, 58, 72))
            for y in range(0, CH + 1, 10):
                d.line([(0, y * BAKE_PX), (img.width, y * BAKE_PX)], fill=(52, 58, 72))
            ground = y0 + H / 2.0 + FEET * HD_PPU
            d.line([(0, ground * BAKE_PX), (img.width, ground * BAKE_PX)], fill=(150, 60, 60), width=2)
            d.rectangle([x0 * BAKE_PX, y0 * BAKE_PX, (x0 + W) * BAKE_PX - 1, (y0 + H) * BAKE_PX - 1],
                        outline=(96, 100, 112))
            pts = bake_points(name, tag, k, a)
            cell = {"canvas": [CW, CH], "px": BAKE_PX, "frame": [x0, y0, W, H], "into": f"hd_{tag} {k}",
                    "ppu": HD_PPU}
            for colour, rgb in (("cyan", (0, 255, 255)), ("yellow", (255, 220, 40))):
                if colour not in pts:
                    continue
                px_, py_ = pts[colour]
                cx, cy = int(round(px_ + x0)), int(round(py_ + y0))
                cell[colour] = [cx, cy]
                X, Y = (cx + 0.5) * BAKE_PX, (cy + 0.5) * BAKE_PX
                d.line([(X - 18, Y), (X + 18, Y)], fill=rgb, width=3)
                d.line([(X, Y - 18), (X, Y + 18)], fill=rgb, width=3)
            img.save(os.path.join(out, f"katarina_bake_{name}_{k}.png"))
            cells[(name, k)] = cell
    return cells


def document(shape, cells):
    h, w = shape[:2]
    L = []
    a = L.append
    n_bake = sum(len(b[2]) for b in BAKE)
    a("# 卡特琳娜：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图 + {n_bake} 张画进她动作帧的图。** 造型和动作已定（`design/katarina_designs.png`：正面、侧身；"
      "动作都是侧身朝右）。**全部用生图（image_gen）画，不要用代码拼方块。**")
    a(f"> - 她在游戏里是**高清**的：每个游戏像素里 1.5×1.5 个细格子；1 倍时待机 {w}×{h} 格（连匕首）。")
    a("> - **两种画法**：")
    a(f"> 1. 第一部分 {len(FX)} 张普通特效（飞刀、刀光、打中、瞬步的烟、地上的匕首、旋斩、死亡莲华的刀圈、身上的 buff）**照常按游戏格子画**"
      "（1 格 = 1 个游戏像素），不用画成高清。大小对照 `design/katarina_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，"
      "右边是原版斗士）；`design/katarina_shots.png` 是定稿动作（4 倍），青色十字是飞刀飞出、刀尖的位置。")
    a("> 2. 第二部分是**画进她自己动作帧**的图（她的帧会随朝向镜像，特效图不会，所以刺击的刀光、甩刀的光弧、瞬步挥刀这些有方向的东西"
      "必须画进帧里）。这些按**她的高清细格子**画：`bake/katarina_bake_<名字>_<帧>.png` 是那一帧的定位图"
      f"（横图 {LAND[0]}×{LAND[1]} 格或竖图 {PORT[0]}×{PORT[1]} 格，每格 {BAKE_PX} 像素；她本人画成淡灰色、只用来对位置；灰框是这一帧的范围，"
      "红线是地面，每 10 格一道浅线；青色十字是起点：刀尖或甩出去的手）。**在同样大小、同样格子的图上只画特效，背景透明，不要画她本人**；"
      "Claude 按格子取回，直接叠进她的帧。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡特琳娜自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**刀光是深红，芯是白亮的**；**匕首是银白的钢**；**瞬步是暗红的烟**；**地上的匕首脚下一圈金色火线**。")
    a("> - **特效要亮**：每道刀光、每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画两边，中间身体位置留空**；旋斩和死亡莲华的刀圈是扁椭圆、中间留空，不要涂满。")
    a("> - **方向（重要，红色方不会镜像）**：旋转的飞刀画成**转半圈看起来一样（点对称）**；死亡莲华飞出的匕首画成**朝右飞、上下对称**"
      "（游戏会把它们转向飞行方向）；打中、目标身上、地上的画面、瞬步、旋斩、刀圈和身上的 buff 都要**严格左右对称**（逐格对称）。"
      "第二部分画进帧里的图照定位图的方向画（往右），不用对称。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `katarina_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），"
      f"以及 `katarina_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（{LAND[0]}×{LAND[1]} 或 "
      f"{PORT[0]}×{PORT[1]}）。透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`（**原样，不要自己整理**），"
      "打包成 `outputs/katarina_fx_pack_done.zip`。**每张图单独交付，不要只给一张总览图**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「贪婪」 | 匕首刺击；被她伤过的英雄阵亡时 Q、W 刷新、瞬步就绪；地上的匕首她走过去就捡起、原地旋斩 | "
      "`a_slash`（帧里）· `a_hit` · `p_reset` · `d_fall` · `d_stuck` · `spin` · `p_hit` |")
    a("| 技能 1 = Q「弹射之刃」（+ E 瞬步跳到匕首） | 甩出旋转的匕首打中目标、再弹两个敌人；匕首从第一个目标身上弹到天上、落在他站的地方 | "
      "`q_throw`（帧里）· `q_blade` · `q_hit` · `q_arc` · `d_fall` · `e_out` · `e_in` |")
    a("| 技能 2 = W「伺机待发」（+ E 瞬步切入） | 先瞬步到敌方英雄身边砍一刀，再把匕首抛到天上、1.25 秒后落回原地，加速 | "
      "`e_out` · `e_in` · `e_slash`（帧里）· `e_hit` · `w_toss` · `d_fall` · `w_ms` |")
    a("| 大招「死亡莲华」 | 原地旋转 2.5 秒，不停向周围的敌方英雄掷出匕首，附带重伤 | `r_lotus` · `r_dagger` · `r_hit` · `r_gw` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、光、火星、烟都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（匕首本身是实物，刀柄可以有深色）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("深红刀光", CRIM), ("匕首的钢", STEEL), ("瞬步的暗红烟", SMOKE), ("地上匕首的金色火线", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。")
    a("- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 第一部分：特效（{len(FX)} 张，游戏格子）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位："
      "捡刀旋斩半径 30000）。大图（" + "、".join(sorted(BIG)) + "）按每格 8 像素画，其余每格 16 像素。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `katarina_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a(f"## 第二部分：画进她动作帧的图（{n_bake} 张，她的高清格子）\n")
    a(f"每张都在对应的定位图 `bake/katarina_bake_<名字>_<帧>.png` 上画：同样大小（横图 {LAND[0] * BAKE_PX}×{LAND[1] * BAKE_PX}、竖图 "
      f"{PORT[0] * BAKE_PX}×{PORT[1] * BAKE_PX} 像素）、每格 {BAKE_PX} 像素，格子和定位图完全对齐；**只画特效，不画她**，背景透明。"
      "她本人在定位图里是淡灰色，只用来对位置。青色十字是起点（刀尖或甩出去的手）。画在她**上面**的会盖住她（所以都别盖住她的脸）。"
      "尽量画在灰框里，往前的刀光可以伸出灰框。注意这里 1 格只有游戏里的 0.67 个像素，所以线条至少 3 格粗，太细的进游戏就看不见了。\n")
    k0 = len(FX)
    for name, tag, ks, layer, title, zh, ramps, effects, _ in BAKE:
        k0 += 1
        a(f"### {k0}. {title}\n")
        a(zh + "\n")
        for k in ks:
            c = cells[(name, k)]
            where = f"青色十字在第 {c['cyan'][0]} 列、第 {c['cyan'][1]} 行"
            a(f"**`katarina_bake_{name}_{k}.png`**（定位图 `bake/katarina_bake_{name}_{k}.png`，{c['canvas'][0]}×{c['canvas'][1]} 格，{where}）：\n")
            crosses = f"the cyan cross of the guide is at square ({c['cyan'][0]}, {c['cyan'][1]})"
            a("```text")
            a(LEAD.format(ramps=ramps).replace("VFX sprite sheet", "VFX overlay on a character frame"))
            a(f"Effect: {effects[k]}")
            a(f"Layout: ONE image {c['canvas'][0] * BAKE_PX}x{c['canvas'][1] * BAKE_PX}, the same size and {BAKE_PX}-px "
              f"square grid as the guide picture (a {c['canvas'][0]} x {c['canvas'][1]} square grid); {crosses}, counted "
              "from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the "
              f"cross or the lines. {TAIL}")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `katarina_fx_{name}` | {bind} | {size} |")
    for name, tag, ks, layer, *_ in BAKE:
        a(f"| `katarina_bake_{name}_<帧>` | 画进 `hd_{tag}` 第 {'、'.join(str(k) for k in ks)} 帧（{'人物上面' if layer == 'over' else '人物后面'}） | 高清格子 |")
    a("")
    a("- 两张表：`asset/league/effects/league_katarina_fx`（小的）和 `league_katarina_big`（" + "、".join(sorted(BIG)) +
      "），tag = 名字（build_katarina.py 的 views）。")
    a("- 目标身上的画面、地上的 d_fall / d_stuck、她身上的 e_out / e_in / p_reset / spin / r_lotus 底边放在脚底线（站位点下方 11.5 格）；"
      "q_arc / w_toss 底边放在她手（或目标身体中部）的高度；d_stuck 4 帧摊满 40 tick（主包每 40 tick 重放一次）；r_lotus 6 帧摊满 30 tick；"
      "飞刀的 y_offset 按 `design/katarina_shots.png` 的出手高度重设（build_katarina q_y / r_y）。")
    a("- 画进帧的图在 restyle 之后（rig_katarina.py --pinholes 那一步）按 `fx_bake_cells.json` 从画布上切下这一帧的范围，叠到 "
      "`assets/source/ppu/katarina_<tag>.png` 的高清帧上，伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新（rig_jayce.bake 的做法）。")
    a("- 用 `pixel_1x/` 切格（import_jayce_fx 的做法；Codex 自己读回太小太糊时从 raw 重读），断言对称；清掉 Codex 给光描的最深色边；"
      "核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, BAKE
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="katarina_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=TMP, help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run Temp/kt_packs/fx/fx_ref_kt.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs", "bake"):
        os.makedirs(os.path.join(out, sub))
    designs(os.path.join(out, "design", "katarina_designs.png"))
    shape = size_sheet(os.path.join(out, "design", "katarina_size.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    cells = bake_guides(os.path.join(out, "bake"))
    CELLS.update(cells)
    shots_sheet(os.path.join(out, "design", "katarina_shots.png"))
    doc = document(shape, cells)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"katarina_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "sheet": "big" if x[0] in BIG else "fx"} for x in FX] +
                  [{"file": f"katarina_bake_{b[0]}_{k}.png", "into": f"hd_{b[1]} {k}", "layer": b[3]}
                   for b in BAKE for k in b[2]], f, ensure_ascii=False, indent=1)
    cells_json = {f"{n}_{k}": c for (n, k), c in cells.items()}
    for path in (os.path.join(out, "bake_cells.json"),) + (() if a.only else
                                                          (os.path.join(SRC, "fx_bake_cells.json"),)):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cells_json, f, indent=1)
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
