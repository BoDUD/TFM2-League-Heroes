#!/usr/bin/env python3
"""Build gwen_fx_pack.zip: step 3 of Gwen's sprite - Codex draws her effects (after tools/art/pack_samira_fx.py).

    python tools/art/pack_gwen_fx.py [--no-zip] [--out DIR] [--only a_hit,q_snip --name gwen_fx_redo_pack]

The pack (%TEMP%/gw_work/fx/gwen_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/gwen/PROMPTS_FX.md), design/gwen_design.png (8x), design/gwen_size.png (the design at 4x on the arena
colour with the feet line, a 10-px ruler and the base fighter beside her), design/gwen_shots.png (the finished action
frames at 4x - tools/art/rig_gwen.py - with the point each picture drawn on her starts from) and refs/lol_fx_ref.png
(League's own particle textures for Gwen, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/gw_work/fxref, extracted from Gwen.wad.client by the session's fx_ref_gw.py).
The effects are the views the kit binds (tools/kit/build_gwen.py: view_projectiles r_v1, r_v2, r_v3 - the three
volleys' LineRangeProjectiles, drawn as r_v1 / r_v3 / r_v5 by their needle count -; view_effects a_hit, q_hit, q_true,
r_hit, w_mist; view_buffs qs1..qs4 (one sheet of four slots), e_on, w_in, r_slow) and the pictures drawn into her own
frames at import (a_snip at the scissors' point, q_snip / q_final in front of the blades, e_dash behind the skip: the
client mirrors her frames with her facing and never an effect picture, so whatever points must ride in the frames -
league_jhin's). League's colours: the scissors' and needles' holy light white to cyan, the Hallowed Mist a pale white
blue, the needles silver. Light, cuts and mist get no outline (the bright-effects lesson); only the Q stack marks have a
dark outline, to read over the battle.
"""
import argparse
import json
import math
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gw_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "gwen", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "gwen_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


HOLY = "#FFFFFF, #E6FFFF, #A8F4FF, #4CD8F2, #1E9ECB, #105C8E"     # the scissors' and needles' holy light
SILVER = "#FFFFFF, #EEF2FF, #C4CCEC, #8C96C4, #565E94"            # the needles themselves
MIST = "#FFFFFF, #E2F6FA, #B4E2EE, #7CC0DA, #4C8CB4"              # the Hallowed Mist
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, cuts, threads, mist or sparks, BRIGHT colours (each shape lit with its lightest shades "
        "and a white-hot core - it must read on a dark battlefield), colours only from {ramps}.")
LEAD_MARKS = ("Pixel art game UI sprite sheet for a small tactics game: chunky square pixels, hard edges, no "
              "anti-aliasing, small bold marks with a 1-square dark outline #0A1A2A so they read over the battle, "
              "colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
FIG = "do NOT draw the figure; leave its place empty"
HL = f"a holy-light ramp ({HOLY})"
SV = f"a silver ramp ({SILVER})"
MS_ = f"a pale holy-mist ramp ({MIST})"


def row(n, cw, ch):
    """One row of n cells of cw x ch squares at 16 px a square."""
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return (f"one horizontal row of {n} equal {shape} cells, image size {n * cw * 16}x{ch * 16} (each cell "
            f"{cw * 16}x{ch * 16}, 16 px a square)")


def column(n, cw, ch):
    """One column of n cells (long lines: a row of them would be too wide to draw)."""
    return (f"one vertical column of {n} equal {cw}:{ch} cells, image size {cw * 16}x{n * ch * 16} (each cell "
            f"{cw * 16}x{ch * 16}, 16 px a square), frame 1 at the top")


def grid(n, cols, cw, ch):
    rows = -(-n // cols)
    return (f"{rows} rows of {cols} equal {cw}:{ch} cells, image size {cols * cw * 16}x{rows * ch * 16} (each cell "
            f"{cw * 16}x{ch * 16}, 16 px a square), read left to right, the top row first")


def needles_fx(k, wid):
    offs = {1: "on the center line", 3: "on the center line and 6 squares above and below it",
            5: "on the center line and 5.5 and 11 squares above and below it"}[k]
    many = "ONE GLOWING NEEDLE" if k == 1 else f"{k} GLOWING NEEDLES side by side (parallel, {offs})"
    return (f"{many} flying along a line to the RIGHT, the picture SYMMETRIC TOP AND BOTTOM (it is turned to face the "
            "cast direction), 6 frames: each needle 8 squares long and 1-2 squares thick, a white-hot point at its RIGHT "
            "end, a silver body, a tapering cyan light trail 10 squares long behind it; 1 the needles appearing at the "
            "left end; 2-5 the needles 15 squares further right each frame; 6 the needles at the right end, fading.")


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- drawn into her own frames (they point: the client mirrors her frames, never an effect picture)
    ("a_snip", "普攻剪击：剪尖的剪切闪光（画进她自己的出手帧），3 帧",
     "画进 `gwen_attack` 第 4 帧起（剪尖，`design/gwen_shots.png` attack 4 的十字；导入时烘进精灵帧）", "18 × 12",
     "普攻往前一刺、剪刀在尖端剪一下：剪尖前面一个很短的青白色 X 形剪痕（两片刀刃合上时擦出的亮痕），几点细小的白色火星"
     "（参考 Q_1_Decal04、Gwen_Base_BA_Throw_Sparks、WeaponTrail05_Mesh）。**朝右**（剪尖在格子左边中间）。3 帧：1 X 形亮痕最亮，"
     "2 变细往右散开、几点火星，3 几点火星淡去。约 18 格宽、12 格高。",
     HL,
     "a SCISSOR SNIP FLASH at a blade's point, pointing RIGHT, 3 frames: the point 2 squares from the LEFT edge, "
     "vertically centered; 1 two short crossing white-cyan cut streaks (a flat X 10 squares long and 6 tall) just right "
     "of the point, a white-hot crossing; 2 the streaks thinner, drifting right, 3 small white sparks; 3 a few fading "
     "sparks.",
     row(3, 20, 14) + "; the point 2 squares from the left edge, vertically centered, in every cell."),
    ("q_snip", "Q 快刀剪乱：每一下小剪的 X 剪痕（画进她的剪合帧），3 帧",
     "画进 `gwen_skill` 第 3、5 帧起（`design/gwen_shots.png` skill 3 的十字：剪刃中段；导入时烘进精灵帧）", "30 × 20",
     "Q 的每一下小剪：剪刀在她面前一张一合，前面闪过一个青白色的大 X 剪痕（两道交叉、微微弯的刀光，像剪刀在空中剪了一下），交叉点最亮，"
     "几缕白丝往外飘（参考 Q_1_Decal01、Q_1_Decal03、Q_MeshTrail01、Q_MeshTrail03、Q_Ground_Scratch）。**朝右**：交叉点在格子左边三分之一处"
     "（剪刃中段），X 往右张开。3 帧：1 X 最亮，2 变细、白丝往右散，3 淡去。约 30 格宽、20 格高。",
     HL,
     "a SCISSOR CUT 'X' in front of the blades, facing RIGHT, 3 frames: the crossing point 1/3 of the way across, "
     "vertically centered; 1 two crossing, slightly curved white-cyan cut streaks forming a wide X 26 squares long and 18 "
     "tall, 2-3 squares thick at the crossing and tapering to sharp points, a white-hot crossing; 2 the streaks thinner, "
     "a few white thread wisps drifting right; 3 fading wisps.",
     row(3, 32, 22) + "; the crossing point 1/3 of the way across, vertically centered, in every cell."),
    ("q_final", "Q 最后一大剪：又大又亮的 X 剪痕（画进她的大剪帧），4 帧",
     "画进 `gwen_skill` 第 7 帧起（`design/gwen_shots.png` skill 7 的十字：剪刃中段；导入时烘进精灵帧）", "44 × 32",
     "Q 的最后一剪：剪刀张到最大再狠狠合上，面前一个又大又亮的 X 剪痕，交叉点一团白光，一圈细细的青色丝线和光点往外散。交叉点是造成真实伤害的地方，"
     "要最亮（参考 Q_1_Decal04_Glowouter、Q_MeshTrail02、Generic_GlowFlare、GroundImpactGlow）。**朝右**：交叉点在格子左边三分之一处。"
     "4 帧：1 大 X 最亮、交叉处白光，2 X 变细、一圈丝线和光点往外散，3 只剩交叉处的光和丝线，4 淡去。约 44 格宽、32 格高。",
     HL,
     "a BIG FINAL SCISSOR CUT, facing RIGHT, 4 frames: the crossing point 1/3 of the way across, vertically centered; 1 "
     "a big X of two crossing curved cut streaks of white-cyan light, 40 squares long and 30 tall, 3-4 squares thick at "
     "the crossing, a white-hot flare 8 squares across at the crossing; 2 the streaks thinner, a ring of thin cyan "
     "threads and 6 light motes spreading from the crossing; 3 only the crossing's glow and drifting threads; 4 fading "
     "motes.",
     row(4, 46, 34) + "; the crossing point 1/3 of the way across, vertically centered, in every cell."),
    ("e_dash", "E 断续疾走：往前跳时身后的丝线拖尾（画进她自己的跳跃帧），3 帧",
     "画进 `gwen_skill2` 第 1–3 帧（`design/gwen_shots.png` skill2 1 的十字是站位点，拖尾往左；导入时烘进精灵帧）", "36 × 22",
     "E 往前一跳：她身后（左边）拖出几道青白色的丝线和光尘，像针线划过空气，脚下几个白色光点（参考 Generic_String_Strands、"
     "Generic_TrailCigSmoke_Connected、Swipe_Trail_Vert、Generic_HolyStrings_Hori）。中间是人，不要画人。**朝右跳**：拖尾全在站位点的"
     "**左边**。3 帧：1 丝线从膝盖、腰、胸口的高度起，2 拖尾最长（往左约 30 格），3 变淡、散成光点。约 36 格宽、22 格高，站位点在格子右边往左 6 格、"
     "底部往上 3 格。",
     HL,
     f"a THREAD TRAIL behind a figure skipping to the RIGHT ({FIG}), 3 frames: 1 three thin white-cyan thread streaks "
     "starting at the figure's knee, waist and chest height, a few light motes at the feet; 2 the threads at their "
     "longest, trailing 30 squares to the LEFT of the standing point, gently wavy, brightest near the figure; 3 the "
     "threads fading into drifting motes.",
     row(3, 38, 24) + "; the standing point 6 squares from the right edge and 3 squares above the bottom in every cell."),
    # ---- on the targets
    ("a_hit", "普攻剪中（目标身上），4 帧", "view_effects `league_gwen_a_hit`（跟随，画在人物上面）", "14",
     "剪刀剪中：一个小小的青白色 X 剪痕，几点白色火星（参考 Q_1_Decal04、Gwen_Base_BA_Throw_Sparks）。约 14 格，居中画。",
     HL,
     "a SNIP HIT, 4 frames: 1 a small white-cyan X cut 10 squares across at the center, a white-hot crossing; 2 the X "
     "thinner, 4 white sparks flying out; 3 sparks further out; 4 fading motes.",
     row(4, 16, 16) + "; centered in every cell."),
    ("q_hit", "Q 小剪剪中（目标身上），3 帧", "view_effects `league_gwen_q_hit`（跟随，画在人物上面）", "12",
     "Q 每一下小剪剪中：一道斜着的青色剪痕一闪（参考 Q_Ground_Scratch、Greyscale_SharpLine）。约 12 格，居中画。",
     HL,
     "a QUICK CUT HIT, 3 frames: 1 a diagonal white-cyan cut streak 10 squares long through the center (from the top "
     "right down to the bottom left), a white-hot core; 2 the streak thinner, 3 sparks; 3 fading.",
     row(3, 14, 14) + "; centered in every cell."),
    ("q_true", "Q 中心的真实伤害（目标身上），4 帧", "view_effects `league_gwen_q_true`（跟随，画在人物上面）", "20",
     "被最后一大剪的中心剪中（真实伤害）：一团白热的光爆开，四道尖锐的白光往外刺，一圈青色光环，几根白线飘散（参考 Generic_GlowFlare_Bloom、"
     "common_flareblue、3026_ItemsPointStarAdd、GroundImpactGlow）。要比普通剪中亮很多。约 20 格，居中画。",
     HL,
     "a TRUE-DAMAGE BURST, 4 frames: 1 a white-hot four-pointed star flare 14 squares across; 2 a thin cyan ring 18 "
     "squares across spreading, 4 long white rays; 3 the ring fading, white thread wisps drifting; 4 fading motes.",
     row(4, 22, 22) + "; centered in every cell."),
    ("r_hit", "R 针打中（敌人身上），4 帧", "view_effects `league_gwen_r_hit`（跟随，画在人物上面）", "12",
     "被针扎中：一根白色的针斜着扎进去一闪，一小团青色光点，一缕丝线飘开（参考 Gwen_Base_BA_Throw_Sparks、UIFX_Debuff、"
     "Generic_String_Strands）。约 12 格，居中画。",
     f"{HL} and {SV}",
     "a NEEDLE HIT, 4 frames: 1 a short white needle streak 8 squares long stabbing in diagonally to the center, a white "
     "flash 6 squares across; 2 a small burst of cyan motes, a thin thread curling off; 3 motes drifting; 4 fading.",
     row(4, 14, 14) + "; centered in every cell."),
    # ---- W: the mist on the ground
    ("w_mist", "W 丝缕缠流：地上的圣霭（落脚处，持续 4 秒，大），8 帧",
     "view_effects `league_gwen_w_mist`（BIG，画在人物下面，不跟随；左右对称；导入时第 3–6 帧循环铺满 4 秒）", "76 × 34",
     "W 的圣霭：她落脚的地方升起一大片白中带青的雾，地上一圈若隐若现的细光环，雾里飘着几缕发光的白丝线，边缘几个小光点（参考 "
     "Generic_SmokeScroll_Hori、Generic_HolyStrings、Generic_RingIndicator、Generic_WIndicator_Corner、2x2_CircleStrings、"
     "Gwen_2x2_Smoke_Soft）。从斜上方看是扁的椭圆（约 74 格宽、30 格高），**左右对称**。雾画在人下面，不会挡人，可以画满，但中间淡一点。"
     "8 帧（上下两排各 4 格）：1 雾从中心冒出（一半大），2 铺满椭圆、光环亮起，3–6 雾和丝线慢慢飘动（**这 4 帧要能无缝循环**），7 雾变淡，"
     "8 只剩几缕。椭圆居中。",
     MS_,
     "a HALLOWED MIST zone on the ground seen from above at an angle, SYMMETRIC LEFT AND RIGHT, 8 frames: a flat ellipse "
     "74 squares wide and 30 tall of pale white-blue holy mist, a thin glowing ring along its edge, 4-6 glowing white "
     "thread wisps drifting inside, a few motes at the rim, the middle a little fainter; 1 the mist rising from the "
     "center (half size); 2 the full ellipse, the ring lighting up; 3-6 the mist and threads drifting slowly (these four "
     "frames loop seamlessly); 7 the mist fading; 8 a few last wisps.",
     grid(8, 4, 78, 36) + "; the ellipse centered in every cell."),
    # ---- on her: the Q stacks, E's speed, inside the mist; the slowed enemies
    ("qs_marks", "Q 层数：头顶的小剪刃记号（她身上，常驻），4 格（每格一个位置）",
     "view_buffs `league_gwen_qs1`…`qs4`（第 k 格是第 k 层的记号，画在第 k 个位置；几层就同时亮几格，叠起来是一排；画在头顶，不旋转）",
     "24 × 8",
     "Q 的层数：每打中一下普攻叠一层（最多 4 层），在她头顶横排显示小记号。4 个格子一样大，**第 k 格只画第 k 个记号**（从左往右第 k 个位置，"
     "其他位置留空），游戏里几层就同时显示前几格，叠起来正好是一排。每个记号是一片竖着的小剪刃（或一根短针），白色的尖、青色的身，约 5 格高、"
     "2 格宽，四个一模一样（参考 Q_1_Decal01、W_UntargetIcon）。记号要有 1 格深色描边才能在战斗里看清。",
     HL,
     "FOUR STACK MARKS, one per cell: four slots in a row at 3, 9, 15 and 21 squares from each cell's left edge, "
     "vertically centered; cell k shows ONLY the mark in slot k, every other slot empty; each mark a tiny upright scissor "
     "blade / needle 5 squares tall and 2 wide, a white tip and a cyan body, a 1-square dark outline; the four marks "
     "identical.",
     row(4, 24, 8) + "."),
    ("e_on", "E 加速：她身上的丝线光（循环），4 帧", "view_buffs `league_gwen_e_on`（循环，画在人物上面；左右对称）", "30 × 40",
     "E 之后 4 秒攻速变快：她身边绕着两三缕细细的青白色丝线和几个小光点往上飘（参考 Generic_String_Strands、2x2_CircleStrings、"
     "Generic_GlowFlare）。不要挡住人：只画细线和光点，人的位置留空。**左右对称**。4 帧无缝循环。约 30 格宽、40 格高，站位点在格子底部往上 "
     "3 格的中间。",
     HL,
     f"THREAD GLINTS round a figure ({FIG}; only thin lines and motes), SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless "
     "loop: 2-3 thin white-cyan threads curling upward round the figure's place from the knees to the shoulders, 4-6 "
     "tiny light motes rising, moving up a little each frame; the figure's place stays empty.",
     row(4, 30, 40) + "; the standing point 3 squares above the bottom, horizontally centered, in every cell."),
    ("w_in", "W 雾中：她身上的圣霭护罩（循环），4 帧", "view_buffs `league_gwen_w_in`（循环，画在人物上面；左右对称）", "36 × 46",
     "站在圣霭里时（远处的敌人看不到她、双抗提高）：她身体外面一层淡淡的白雾，几缕雾在她脚下和身边绕，头顶一个很小的白色十字丝线结（参考 "
     "W_UntargetIcon、Gwen_2x2_Smoke_Soft、Generic_HolyStrings_Support）。不要挡住人：雾只在身体外围，人的位置留空。**左右对称**。"
     "4 帧无缝循环。约 36 格宽、46 格高，站位点在格子底部往上 3 格的中间。",
     MS_,
     f"a HOLY MIST VEIL round a figure ({FIG}; only round it), SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: soft "
     "white-blue mist wisps hugging the outside of the figure's silhouette from the feet to the shoulders, a low swirl of "
     "mist 30 squares wide at the feet, a tiny white four-pointed thread knot 5 squares across above the head (36 squares "
     "above the standing point); the wisps drift each frame; the figure's place stays empty.",
     row(4, 36, 46) + "; the standing point 3 squares above the bottom, horizontally centered, in every cell."),
    ("r_slow", "R 减速：被针线缠住的敌人脚下（循环），4 帧", "view_buffs `league_gwen_r_slow`（循环，画在人物上面；左右对称）", "26 × 12",
     "被 R 的针扎中减速时：脚踝上绕着两圈发光的青色丝线，像被缝住了，几个针头一闪一闪（参考 Generic_String_Strands、UIFX_Debuff、"
     "2x2_CircleStrings）。**左右对称**。4 帧无缝循环。丝线圈从斜上方看是扁的椭圆，站位点在格子中间。约 26 格宽、12 格高。",
     f"{HL} and {SV}",
     "a THREAD BIND at a figure's feet, SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: two flat ellipses of glowing "
     "cyan thread 22 squares wide and 6 tall wound round the ankles (the standing point at the center), crossing each "
     "other, 3 tiny white needle glints along them that move round a little each frame.",
     row(4, 26, 12) + "; the standing point at the center of every cell."),
    # ---- R: the three volleys (LineRangeProjectile pictures: turned to the cast direction)
    ("r_v1", "R 引针簇射第 1 波：1 根针沿直线飞（按方向转动，大），6 帧",
     "view_projectiles `league_gwen_r_v1`（BIG，LineRangeProjectile 80000 长、5000 宽：画面按方向转动，**上下必须对称**）", "80 × 6",
     "R 第一波：一根发光的白针从左端（她的位置）沿直线往右飞到右端：白热的针尖、银色针身，后面拖一条青色的光线（参考 "
     "Gwen_Base_BA_Throw_Sparks、Greyscale_SharpLine、Generic_RibbonMask01、MeshTrail_Mask01）。整张会按施放方向转动，所以**上下要对称**。"
     "6 帧（竖着排一列）：1 针在左端出现，2–5 每帧往右飞约 15 格（拖尾跟着），6 针到右端、变淡。约 80 格长、6 格高，线在格子正中。",
     f"{HL} and {SV}", needles_fx(1, 6),
     column(6, 82, 8) + "; the line along the horizontal center of every cell, from 1 square inside the left edge to 1 "
     "square inside the right edge."),
    ("r_v3", "R 第 2 波：3 根针并排飞（按方向转动，大），6 帧",
     "view_projectiles `league_gwen_r_v2`（BIG，LineRangeProjectile 80000 长、15000 宽：画面按方向转动，**上下必须对称**）", "80 × 16",
     "R 第二波：3 根针并排沿直线往右飞（中间一根，上下各一根，隔 6 格），画法和第 1 波一样。**上下对称**。6 帧（竖着排一列）。约 80 格长、"
     "16 格高。",
     f"{HL} and {SV}", needles_fx(3, 16),
     column(6, 82, 18) + "; the middle needle along the horizontal center of every cell."),
    ("r_v5", "R 第 3 波：5 根针并排飞（按方向转动，大），6 帧",
     "view_projectiles `league_gwen_r_v3`（BIG，LineRangeProjectile 80000 长、25000 宽：画面按方向转动，**上下必须对称**）", "80 × 26",
     "R 第三波：5 根针并排沿直线往右飞（中间一根，上下各两根，隔 5.5 格），画法和第 1 波一样，可以稍亮一点。**上下对称**。6 帧（竖着排一列）。"
     "约 80 格长、26 格高。",
     f"{HL} and {SV}", needles_fx(5, 26),
     column(6, 82, 28) + "; the middle needle along the horizontal center of every cell."),
]

GROUPS = [
    ("snip", ["Q_1_Decal01", "Q_1_Decal03", "Q_1_Decal04", "Q_1_Decal04_Glowouter", "Q_Ground_Scratch",
              "Gwen_Base_BA_Throw_Sparks"]),
    ("trail", ["Q_MeshTrail01", "Q_MeshTrail02", "Q_MeshTrail03", "WeaponTrail05_Mesh", "Swipe_Trail_Vert",
               "Greyscale_SharpLine"]),
    ("flare", ["Generic_GlowFlare_Bloom", "common_flareblue", "3026_ItemsPointStarAdd", "GroundImpactGlow",
               "Generic_RibbonMask01", "MeshTrail_Mask01"]),
    ("mist", ["Generic_SmokeScroll_Hori", "Gwen_2x2_Smoke_Soft", "Generic_HolyStrings", "Generic_HolyStrings_Support",
              "Generic_RingIndicator", "Generic_WIndicator_Corner"]),
    ("thread", ["Generic_String_Strands", "2x2_CircleStrings", "Generic_TrailCigSmoke_Connected",
                "Generic_HolyStrings_Hori", "W_UntargetIcon", "UIFX_Debuff"]),
]


def rig_points():
    """Where the pictures drawn on her start, from the rig: (tag, frame, what, [(x, y) on the 128 canvas])."""
    import rig_gwen as R
    P = R.Parts()

    def blade(tag, k, frac):
        pose = R.STAND[tag][k - 1]
        deg, sdeg, _ = pose["far"]
        _, _, hand = R.arm_cells(P, R.FAR_SH, deg)
        t = math.radians(sdeg)
        d = R.BLADE_FROM + frac * R.SC_LEN
        mx, my = pose.get("move", (0, 0))
        return [(hand[0] + d * math.cos(t) + mx, hand[1] + d * math.sin(t) + my)]

    feet = [(R.PIVOT[0], R.SOLES + 1)]
    return P, R, [("attack", 4, "a_snip: 剪尖", blade("attack", 4, 1.0)),
                  ("skill", 3, "q_snip: 剪刃中段", blade("skill", 3, 0.5)),
                  ("skill", 7, "q_final: 剪刃中段", blade("skill", 7, 0.5)),
                  ("skill2", 1, "e_dash: 站位点（拖尾往左）", feet),
                  ("skill2", 6, "w_mist: 站位点（椭圆中心）", feet),
                  ("ult", 4, "r 针：从她站的位置往前飞", feet),
                  ("idle", 1, "qs 记号 / w_in 的结：头顶", [(R.PIVOT[0], 52)])]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Gwen_Base_", "").replace("Generic_", "")[:26],
                   fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"格温 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (rig_gwen.py), each picture's starting point as a cyan cross."""
    P, R, shots = rig_points()
    built = {}
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, pts in shots:
        if tag not in built:
            built[tag] = R.frames(P, tag)
        f = built[tag][k - 1]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 230), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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
    a("# 灵罗娃娃 格温：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/gwen_design.png`，8 倍，{h} 行）。")
    a(f"> - 大小对照 `design/gwen_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。格温 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/gwen_shots.png`：定稿动作（4 倍），青色十字是特效的起点（剪尖、剪刃中段、脚下、头顶），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里格温自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**剪刀和针的光是白到青色的圣光；W 的圣霭是淡淡的白蓝色雾；针本身是银白色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白热的芯，暗底上一眼能看见。")
    a("> - **挂在她身上的画面只画外围，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要）**：画进她自己动作帧的（`a_snip`、`q_snip`、`q_final`、`e_dash`）都画成**朝右**。R 的三波针画成朝右飞，游戏会按施放方向转，而且要**上下对称**。挂在她身上循环的画面（`e_on`、`w_in`）、地上的 `w_mist`、敌人脚下的 `r_slow` 要**左右对称**。Q 层数的记号不旋转。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `gwen_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等大的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`gwen_fx_done.zip`）放在 outputs 里，或放在 `outputs/gwen-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「千穿百孔」 | 近身用大剪刀剪；每次剪中附加魔法伤害，对英雄再造成最大生命值的真实伤害并回血；每次普攻叠一层 Q（最多 4 层） | `a_snip` · `a_hit` · `qs_marks` |")
    a("| 技能 1 = Q「快刀剪乱」 | 在面前剪 1 + 层数下小剪，最后一大剪，剪中间的敌人受到真实伤害 | `q_snip` · `q_final` · `q_hit` · `q_true` |")
    a("| 技能 2 = E「断续疾走」→ W「丝缕缠流」 | 跳向敌方英雄，之后 4 秒攻速变快；落地处升起圣霭 4 秒，她站在里面时远处的敌人看不见她、双抗提高 | `e_dash` · `e_on` · `w_mist` · `w_in` |")
    a("| 大招 = R「引针簇射」 | 朝一个方向连扔三波针：1 根、3 根、5 根，打中的敌人减速 | `r_v1` · `r_v3` · `r_v5` · `r_hit` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、剪痕、丝线、雾、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。只有 Q 层数的记号有 1 格深色描边（`#0A1A2A`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("圣光（剪痕、针的光、丝线、真实伤害）", HOLY), ("银色（针本身）", SILVER), ("圣霭（W 的雾和护罩）", MIST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 24000，"
      "Q 面前扇形半径 30000、中心真实伤害在前方 16000 处，W 圣霭半径 37000，R 每波 80000 长、宽 5000 / 15000 / 25000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `gwen_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a((LEAD_MARKS if name == "qs_marks" else LEAD).format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `gwen_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 画进精灵帧的（`a_snip`、`q_snip`、`q_final`、`e_dash`）写进 `assets/source/native/gwen_bake.json`，`import_native.py` 烘进 attack / skill / "
      "skill2 的帧（客户端只镜像英雄自己的帧，不镜像特效图：烬的枪口火光）；`e_dash` 烘进后去掉 kit 里的 `cview(\"e_dash\")`；光在动作帧之内结束。")
    a("- 按定稿动作重排 kit 的时间：普攻在 attack 第 4 帧出手，Q 的小剪对上 skill 第 3、5 帧、最后一剪对上第 7 帧，E 落地在 skill2 第 4 帧、W 举剪在第 6 帧，R 每波对上 ult 第 4 帧。")
    a("- `w_mist` 不跟随、画在人物下面，3–6 帧循环铺满 w_t（240 tick），第 7–8 帧收尾；`qs_marks` 拆成 qs1…qs4 四个 tag（每个 1 帧循环），画在头顶（站位点上面约 48 格）；"
      "`e_on`、`w_in`、`r_slow` 循环、左右对称。")
    a("- `r_v1`/`r_v3`/`r_v5` 绑到 r_v1/r_v2/r_v3（LineRangeProjectile，80 格长，锚点在线的中心），导入后用 `lint_mod.py` 量上下翻转后的差别（要几乎为 0）；"
      "帧长铺满 r_delay + r_apply。")
    a("- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，Q 层数记号保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，"
      "和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="gwen_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Gwen's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "gwen_design.png"))
    shape = size_sheet(os.path.join(out, "design", "gwen_size.png"))
    shots_sheet(os.path.join(out, "design", "gwen_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"gwen_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
