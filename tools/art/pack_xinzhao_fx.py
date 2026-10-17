#!/usr/bin/env python3
"""Build xinzhao_fx_pack.zip: step 3 of Xin Zhao's sprite - Codex draws his effects (pack_tryndamere_fx.py's layout).

    python tools/art/pack_xinzhao_fx.py [--no-zip] [--out DIR] [--only a_hit,w_thrust --name xinzhao_fx_redo_pack]

The pack (%TEMP%/xz_work/fx/xinzhao_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/xinzhao/PROMPTS_FX.md), design/xinzhao_design.png (8x), design/xinzhao_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside him), design/xinzhao_shots.png (the finished
action frames at 4x - tools/art/rig_xinzhao.py - with the point each caster picture starts from) and refs/lol_fx_ref.png
(League's own particle textures for Xin Zhao, grouped by the effect of ours they inform; Riot's art, local only: they
are read from XinZhao.wad.client into %TEMP%/xz_work/fxref first).
The effects are the views the kit binds (tools/kit/build_xinzhao.py: view_effects a_hit, p_hit, p_heal, q_hit, q3_up,
e_dash, e_land, e_hit, w_slash, w_hit, w_hit2, r_tell, r_sweep, r_hit; view_projectiles w_thrust; view_buffs q_1..q_3,
e_slow, w_slow, r_chal, r_guard). League's colours: Demacian gold with white-hot cores (Three Talon Strike's sparks,
Determination's swipe, the challenge mark, the guard's wing symbol) and electric blue-white (Wind Becomes Lightning's
thrust, the charge's streak, Crescent Guard's sweep). Light, slashes and sparks get no outline.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "xz_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "xinzhao", "PROMPTS_FX.md")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "xinzhao_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08"     # Q, the passive, the challenge, the guard
STORM = "#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A"    # W's lightning, the charge, the crescent
DUSK = "#6A5AC8, #4A3A9A, #2E2468, #1C1640"                       # the slows, dust and shadow on the ground
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark "
        "outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a "
        "dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h}"
FIG = "do NOT draw the figure; leave its place empty"
GC = f"a Demacian gold ramp ({GOLD})"
SC = f"an electric blue-white ramp ({STORM})"
DC = f"a dusk violet ramp ({DUSK})"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻刺中（目标身上），4 帧", "view_effects `league_xinzhao_a_hit`（跟随，画在人物上面）", "14",
     "长枪刺中：一道从左往右的白金色突刺光，刺中的地方一下白色闪光，几点金色火星往前飞（参考 HIT02、Spark_Vertical、Star）。约 14 格，"
     "居中画。",
     f"{GC}",
     "a SPEAR THRUST HIT, 4 frames: 1 a short straight streak of white-gold light 12 squares long coming in from the left "
     "to the center; 2 a white four-pointed star flash at the center 8 squares across, 5 gold sparks flying out to the "
     "right; 3 the flash gone, sparks further out; 4 a few fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("p_hit", "被动「果决」第三下打中（目标身上），5 帧", "view_effects `league_xinzhao_p_hit`（跟随，画在人物上面）", "20",
     "每第三下：长枪大挥砍中，一道从上往下的宽金色月牙弧光，砍中处白光炸开，金色火星四散（参考 Passive_Swipe_B_Alpha、BlastShapes、"
     "Z_StarGlow）。约 20 格，居中画。",
     f"{GC}",
     "a HEAVY SPEAR SWING HIT, 5 frames: 1 a wide crescent arc of gold light 18 squares long sweeping from the upper left "
     "down through the center; 2 a white burst at the center 12 squares across, the arc thinning; 3 eight gold sparks and "
     "four small four-pointed stars flying out; 4 sparks further out; 5 fading sparks.",
     ROW.format(n=5, shape="square", w=1280, h=256) + "; centered in every cell."),
    ("p_heal", "被动「果决」回血（施法者身上），5 帧",
     "view_effects `league_xinzhao_p_heal`（施法者身上，不跟随；格子中心放到他的胸口）", "22 × 32",
     "第三下回血：他身上一下暖金色的光，几个金色光点和小「+」形火花从身上往上升（参考 Q_StarGlow、Z_Glow01、Passive_heal）。中间是人，"
     "不要画人。左右对称。5 帧：1 胸口金光，2–4 光点和「+」往上升，5 淡去。约 22 格宽、32 格高，胸口在格子中间偏下（格子底部往上 12 格）。",
     f"{GC}",
     f"a WARM GOLDEN HEAL on a figure ({FIG}; symmetric left and right), 5 frames: 1 a soft gold glow at the chest point "
     "10 squares across; 2 six small gold plus-shaped sparks and light motes rising from it; 3 the sparks 8-16 squares "
     "above the chest; 4 near the top of the cell; 5 fading.",
     ROW.format(n=5, shape="11:16", w=1100, h=320) + " (each cell 220x320); the chest point 12 squares (96 px) above the "
     "bottom, horizontally centered, in every cell."),
    # ---- E + Q: Audacious Charge, Three Talon Strike
    ("e_dash", "E 无畏冲锋：冲刺时身后的光痕（施法者身上，跟着冲过去），5 帧",
     "view_effects `league_xinzhao_e_dash`（BIG，施法者身上，跟随；格子里的站位点放到他的站位点）", "44 × 24",
     "E「无畏冲锋」：他持枪飞身往前扑，身后拖着一道蓝白色的电光冲刺痕，枪头前一点金光（参考 E_Wave_Texture、W_SpearSmear、Typhoon、"
     "R_frost_line）。画在人物上面，中间是人，不要画人：光痕从人的位置往**左后方**拖出去，人前面（右边）只有一点枪头的金光。5 帧：1 光痕"
     "出现，2–3 最长（约 30 格），4 变短、碎成电光丝，5 散去。约 44 格宽、24 格高，站位点在格子底部往上 4 格、左右正中。",
     f"{SC} and {GC}",
     f"a CHARGE STREAK behind a leaping figure ({FIG}), 5 frames: 1 a streak of electric blue-white light appears behind "
     "the figure's place; 2-3 the streak at its longest, trailing 30 squares to the LEFT behind the figure at waist "
     "height (7-12 squares above the standing point), thin white lightning threads along it, a small gold glint at the "
     "spear's point 8 squares right of the figure; 4 the streak shorter, breaking into blue threads; 5 fading threads.",
     ROW.format(n=5, shape="11:6", w=1760, h=192) + " (each cell 352x192); the standing point 4 squares (32 px) above the "
     "bottom, horizontally centered, in every cell."),
    ("e_land", "E 落地：脚下的冲击圈（落地点，不跟随，画在人物下面），5 帧",
     "view_effects `league_xinzhao_e_land`（BIG，施法者脚下，不跟随，z -1）", "44 × 20",
     "冲到目标身边落地：脚下一圈蓝白色的冲击波往外扩（从斜上方看是扁椭圆，宽是高的 2 倍，约 40 格宽），带一点金色火星和地面的裂纹尘土"
     "（参考 E_Nova_Mult、BA_Underglow、Q_WallDestruction、Z_explosion_smoke）。中间是人，不要画人。左右对称。5 帧：1 脚下白光，2–3 "
     "圈往外扩，4 圈到边变细、尘土，5 散去。约 44 格宽、20 格高，圈的中心在格子正中。",
     f"{SC}, {GC} and {DC}",
     f"a LANDING SHOCKWAVE on the ground round a figure's feet ({FIG}; symmetric left and right), seen from above at an "
     "angle, 5 frames: 1 a white flash at the center; 2-3 a ring of electric blue-white light expanding over a flattened "
     "ellipse twice as wide as tall up to 40 squares wide, gold sparks thrown up along it; 4 the ring thin at its edge, "
     "violet dust; 5 fading dust.",
     ROW.format(n=5, shape="11:5", w=1760, h=160) + " (each cell 352x160); the ellipse's center at the center of every "
     "cell."),
    ("e_hit", "E 冲锋命中（敌人身上），4 帧", "view_effects `league_xinzhao_e_hit`（跟随，画在人物上面）", "16",
     "冲锋撞到周围的敌人：一下蓝白色的电光爆开，几道短短的闪电和金色火星（参考 R_Braum_Base_E_Block_Spark、W_Global_SS_Ghost_Swirl）。"
     "约 16 格，居中画。",
     f"{SC} and {GC}",
     "a CHARGE IMPACT, 4 frames: 1 a white flash at the center 8 squares across; 2 an electric blue-white burst 14 "
     "squares across with 4 short jagged lightning threads, 3 gold sparks; 3 the burst breaking up; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("e_slow", "E 减速：脚下的标记（敌人身上，循环 0.5 秒），4 帧", "view_buffs `league_xinzhao_e_slow`（循环，画在脚下）",
     "16 × 6",
     "被冲锋减速：脚下一圈淡蓝紫色的光圈，几道短短的电光丝往下滑。中间是人，不要画人。左右对称，4 帧无缝循环。约 16 格宽、6 格高，贴着地面。",
     f"{SC} and {DC}",
     f"a SLOW MARK at a figure's feet ({FIG}; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse "
     "of pale blue-violet light on the ground round the feet (twice as wide as tall, 14 squares wide), 3 short blue "
     "streaks sliding DOWN into it a square each frame.",
     ROW.format(n=4, shape="8:3", w=2048, h=192) + " (each cell 512x192); the ellipse at the bottom middle of every cell."),
    ("q_marks", "Q 三重爪击：头上的剩余次数标记（自己身上，循环），3 行 × 4 帧",
     "view_buffs `league_xinzhao_q_1` / `q_2` / `q_3`（循环，画在人物上面，头顶）", "14 × 8",
     "冲锋落地后接三重爪击：他头顶亮着金色的爪印标记，还剩几下就有几道（第 1 行 3 道、第 2 行 2 道、第 3 行 1 道，每道是一条斜着的金色"
     "光爪痕），金光一明一暗（参考 Q_StarGlow、Q_Spark、Z_Streak）。每行 4 帧无缝循环。约 14 格宽、8 格高，标记的底边在格子底部"
     "（导入时放到头顶）。**三行的爪痕大小、位置要一样**，只差道数。",
     f"{GC}",
     "COMBO COUNT MARKS over a head, 3 rows of 4 frames, each row a seamless loop: row 1 THREE short slanted claw strokes "
     "of gold light side by side (each 6 squares tall, 3 squares apart, leaning right like talon marks, white cores), "
     "row 2 the same marks but only the left TWO, row 3 only the left ONE, in the same places; in each row a soft gold "
     "glow pulsing brighter and dimmer, a tiny spark twinkling.",
     "a grid of 3 rows x 4 columns of equal 7:4 cells, image size 1792x768 (each cell 448x256); the marks centered, their "
     "bottom near the bottom of every cell."),
    ("q_hit", "Q 三重爪击前两下打中（敌人身上），4 帧", "view_effects `league_xinzhao_q_hit`（跟随，画在人物上面）", "16",
     "三重爪击的强化刺击：一道金色的爪痕突刺光，刺中处金星闪光（参考 Q_Swipe_C、Q_2_Swipe_Mid、Q_StarGlow）。比普攻的刺中亮、金。约 16 格，"
     "居中画。",
     f"{GC}",
     "an EMPOWERED THRUST HIT, 4 frames: 1 three parallel slanted gold claw streaks 12 squares long striking into the "
     "center; 2 a bright gold star flash at the center 10 squares across; 3 gold sparks flying out; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("q3_up", "Q 第三下击飞（敌人身上），5 帧", "view_effects `league_xinzhao_q3_up`（跟随，画在人物上面）", "20 × 32",
     "第三下把敌人挑上天：从脚下往上一道竖直的金色上挑弧光，脚下一圈尘土，几块碎石和金色火星往上飞（参考 Q_Swipe_B、Q_Mound_Shadow、"
     "Q_Smoke_3、Q_WallDestruction）。中间是人，不要画人。5 帧：1 脚下金光和尘土，2 上挑的弧光从下往上冲到头顶，3 最高、火星往上，"
     "4 尘土落下，5 散去。约 20 格宽、32 格高，人的脚在格子底部往上 4 格的中间。",
     f"{GC} and {DC}",
     f"a KNOCK-UP STRIKE on a figure ({FIG}), 5 frames: 1 a gold flash and a puff of violet dust at the feet; 2 a tall "
     "upward crescent slash of gold light rising from the feet past the head (28 squares tall); 3 the slash at its top, "
     "gold sparks and small rock chips flying up; 4 the dust settling, sparks falling; 5 fading.",
     ROW.format(n=5, shape="5:8", w=1000, h=320) + " (each cell 200x320); the figure's feet 4 squares (32 px) above the "
     "bottom, horizontally centered, in every cell."),
    # ---- W: Wind Becomes Lightning
    ("w_slash", "W 风斩：身前的横扫月牙（施法者身上，不跟随），4 帧",
     "view_effects `league_xinzhao_w_slash`（BIG，施法者身上，不跟随；格子里的站位点放到他的站位点）", "40 × 30",
     "W「风斩电刺」的第一下：长枪在**身前**横扫出一道宽的半月形风刃，金白色的刃带一点蓝色的风（参考 W_swipe、W_Swipe_B_Dissolve、"
     "Typhoon、Z_SwipeText01）。半月从他身后上方扫到身前下方，开口朝左，刃在右半边。不要画人。4 帧：1 刃从上方出现，2 扫满半圈（最亮），"
     "3 变细、风丝飘散，4 散去。约 40 格宽、30 格高，站位点在格子底部往上 4 格、左边 12 格处（刃在人前面）。",
     f"{GC} and {SC}",
     f"a WIDE CRESCENT WIND SLASH in front of a figure ({FIG}), 4 frames: 1 the head of a broad crescent blade of white-gold "
     "light appears above the figure's place; 2 the full crescent sweeping round in FRONT of the figure (on the right side "
     "of it), 26 squares tall and 22 wide, its opening facing left toward the figure, thin blue wind strands along its "
     "outer edge; 3 the crescent thinning, the wind strands drifting off to the right; 4 fading strands.",
     ROW.format(n=4, shape="4:3", w=1280, h=240) + " (each cell 320x240); the figure's standing point 4 squares (32 px) "
     "above the bottom and 12 squares (96 px) from the cell's left edge."),
    ("w_thrust", "W 电刺：向前直刺出去的闪电（一条线，按方向转动），5 帧",
     "view_projectiles `league_xinzhao_w_thrust`（BIG，LineRangeProjectile 60000 长：画面按方向转动，所以**上下必须对称**）", "60 × 10",
     "W 的第二下：从他身前往前射出一道长长的蓝白色电光枪刺，像一支闪电化成的长枪往前冲，尖头在右（参考 W_Mis_Base、W_Mis_BrightLead、"
     "W_SpearSmear_v2、W_LungeMult、R_frost_line）。这张会按施放方向转动（朝左放时转半圈），所以**上下要对称**（上面和下面一样，"
     "不分上下）。5 帧：1 左端一点白光，2 电光枪往右冲到一半，3 冲满整条（约 58 格长，枪尖在右端），4 变细、碎成电光丝，5 散去。"
     "约 60 格长、10 格高，整条居中画。",
     f"{SC}",
     "a LIGHTNING SPEAR THRUST along a line, 5 frames, the picture SYMMETRIC TOP AND BOTTOM (it is turned to face the cast "
     "direction): 1 a white spark at the left end of the line; 2 a long spear-shaped bolt of electric blue-white light "
     "shooting right, reaching the middle, a white core, short lightning threads above and below it mirrored; 3 the bolt "
     "along the whole line, 58 squares long, its sharp white point at the right end, 7 squares thick at its widest; 4 the "
     "bolt thinning, breaking into blue threads; 5 fading threads.",
     ROW.format(n=5, shape="6:1", w=3840, h=128) + " (each cell 768x128 - keep the 6:1 shape); the line along the "
     "horizontal center of every cell, from 1 square inside the left edge to 1 square inside the right edge."),
    ("w_hit", "W 风斩打中（敌人身上），4 帧", "view_effects `league_xinzhao_w_hit`（跟随，画在人物上面）", "14",
     "被横扫的风刃扫到：一道金白色的横斩光和几缕风（参考 W_swipe、Typhoon）。约 14 格，居中画。",
     f"{GC} and {SC}",
     "a SLASH HIT, 4 frames: 1 a horizontal white-gold slash streak 14 squares long through the center; 2 a white flash "
     "at the center 7 squares across, thin blue wind wisps; 3 sparks and wisps drifting; 4 fading.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("w_hit2", "W 电刺打中（敌人身上），4 帧", "view_effects `league_xinzhao_w_hit2`（跟随，画在人物上面）", "16",
     "被电光枪刺中：一下蓝白色的电光爆开，几道闪电劈出去（参考 R_Braum_Base_E_Block_Spark、W_Global_SS_Ghost_Swirl、W_PassiveMark）。"
     "约 16 格，居中画。",
     f"{SC}",
     "a LIGHTNING THRUST HIT, 4 frames: 1 a white flash at the center 8 squares across; 2 an electric blue-white burst "
     "with 5 jagged lightning threads 8 squares long forking out; 3 the threads flickering, smaller; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("w_slow", "W 减速：脚下的标记（敌人身上，循环 1.5 秒），4 帧", "view_buffs `league_xinzhao_w_slow`（循环，画在脚下）",
     "18 × 8",
     "被电刺减速：脚下一圈蓝白色的电光圈，几道细闪电在圈上跳。中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、8 格高，贴着地面。",
     f"{SC} and {DC}",
     f"a SHOCK SLOW MARK at a figure's feet ({FIG}; symmetric left and right), 4 frames, a seamless loop: a flattened "
     "ellipse of electric blue light on the ground round the feet (twice as wide as tall, 16 squares wide), 3 tiny "
     "lightning threads jumping along it, moving each frame.",
     ROW.format(n=4, shape="9:4", w=2304, h=256) + " (each cell 576x256); the ellipse at the bottom middle of every cell."),
    # ---- R: Crescent Guard
    ("r_tell", "R 新月护卫起手：长枪转动的金光（施法者身上，跟随），4 帧",
     "view_effects `league_xinzhao_r_tell`（BIG，施法者身上，跟随；格子中心放到他的胸口）", "30 × 30",
     "R 起手：他把长枪抡起来，身边一圈金色的转动光（像枪头转出来的圆，参考 R_Tell_WeaponSpin、R_Tell_WeaponSpin_EndGlow、R_Cas_Edge）。"
     "中间是人，不要画人。4 帧：亮的弧头每帧转 90°，后面拖着变暗的弧。约 30 格见方，胸口在格子正中。",
     f"{GC} and {SC}",
     f"a SPINNING SPEAR GLOW round a figure's chest ({FIG}), 4 frames: a ring path 26 squares across round the center; a "
     "bright white-gold arc head moving a quarter turn each frame along it, a fading gold and pale blue trail behind it "
     "covering half the ring; small sparks thrown off.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; the ring centered in every cell."),
    ("r_sweep", "R 新月护卫：绕身一圈的新月刃光（施法者脚下，不跟随），6 帧",
     "view_effects `league_xinzhao_r_sweep`（BIG，施法者身上，不跟随；格子里的站位点放到他的站位点）", "76 × 44",
     "R「新月护卫」：长枪绕着身体横扫一圈，地面上划出一圈蓝白色的新月形刃光（从斜上方看是扁椭圆，宽是高的 2 倍，半径约 36 格，所以约 "
     "72 格宽），刃的外沿是金色的亮边，冲击把尘土往外推（参考 R_BladeSwipe、R_BladeSwipe_AddLayer、R_Credscent_FlashFrame、R_GroundSwipe、"
     "R_Blast_Ring、R_ring）。中间是人，不要画人：前面一段从人身前（下方）经过，后面一段在人身后（上方）。6 帧：1 一段刃光在右边出现，"
     "2–3 扫满一圈（亮的刃头每帧转小半圈），4 整圈一下闪亮、往外冲，5 变细、尘土往外，6 散去。约 76 格宽、44 格高，站位点在格子正中偏下"
     "（格子底部往上 20 格）。",
     f"{SC}, {GC} and {DC}",
     f"a CRESCENT SWEEP all round a figure ({FIG}), seen from above at an angle, 6 frames: 1 the bright head of a "
     "crescent blade of blue-white light with a gold outer edge appears at the right of the figure's place on the ground; "
     "2-3 it sweeps round a flattened ellipse 72 squares wide and 36 tall (twice as wide as tall) round the standing "
     "point, a fading blue trail behind it; 4 the whole ring flashing bright white-blue at once, a pale shockwave pushing "
     "outward; 5 the ring thin, violet dust thrown outward; 6 fading dust.",
     ROW.format(n=6, shape="19:11", w=3648, h=528) + " (each cell 608x352 - keep the 19:11 shape); the figure's standing "
     "point 20 squares (160 px) above the bottom, horizontally centered, in every cell."),
    ("r_hit", "R 横扫打中（敌人身上），4 帧", "view_effects `league_xinzhao_r_hit`（跟随，画在人物上面）", "16",
     "被新月刃扫中：一道蓝白色的弧形斩光，金色火花（参考 R_Impact_Slash、R_Block_Spark）。约 16 格，居中画。",
     f"{SC} and {GC}",
     "a CRESCENT SLASH HIT, 4 frames: 1 a curved slash streak of blue-white light with a gold edge 14 squares long through "
     "the center; 2 a white flash at the center 8 squares across; 3 blue and gold sparks flying out; 4 fading.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    ("r_chal", "R 挑战标记（被挑战的敌人身上，头顶，循环 1.5 秒），4 帧",
     "view_buffs `league_xinzhao_r_chal`（循环，画在人物上面，头顶）", "12 × 12",
     "被他挑战、留在身边单挑的那个敌人：头顶一个金色的德玛西亚式挑战纹章（两把交叉的长枪，中间一个小盾，有 1 格深色描边），金光一明一暗"
     "（参考 W_PassiveMark、W_Marker_Cross、R_EyeforanEye01）。4 帧无缝循环。约 12 格见方，纹章的底边在格子底部（导入时放到头顶）。",
     f"{GC} and {SC}",
     "a CHALLENGE EMBLEM over a head, 4 frames, a seamless loop: a small gold emblem 10 squares tall - two crossed spears "
     "behind a tiny shield, a 1-square dark outline #10102A - with a white glint; a soft gold glow round it pulsing "
     "brighter and dimmer; the emblem bobs a square.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; the emblem centered, its bottom near the bottom of every cell."),
    ("r_guard", "R 之后 3 秒：身上的护卫光（循环），4 帧",
     "view_buffs `league_xinzhao_r_guard`（BIG，循环，画在人物下面，z -1）", "30 × 44",
     "R 之后 3 秒减伤：他身后一道金橙色的护卫光——身后背上一对展开的金色光翼标志（参考 R_InvulnShield_Symbol 的橙金色翼形），身体两边"
     "一圈淡淡的金色光罩边，脚下一圈扁的金光（参考 R_InvulnShield_Sphere、R_Aura_Self、R_Braum_Base_I_shield_glow）。画在人物下面，"
     "所以只有从人身边、头顶露出来的部分看得见。中间是人，不要画人。**左右对称**（人朝左朝右都用同一张）。4 帧无缝循环（光罩边一明一暗、"
     "光翼微微扇动）。约 30 格宽、44 格高，脚在格子底部往上 4 格的中间。",
     f"{GC}",
     f"a GUARDIAN AURA round a standing figure ({FIG}; symmetric left and right), 4 frames, a seamless loop: behind the "
     "figure's upper body a pair of spread wing shapes of orange-gold light (each 10 squares long, rising from the "
     "shoulders' height outward and up, like a heraldic winged emblem), a thin dome-shaped rim of pale gold light round "
     "the figure's place (28 squares wide, 40 tall, edge only, the middle empty), a flattened ellipse of gold light on the "
     "ground round the feet; the rim and wings pulse a little each frame.",
     ROW.format(n=4, shape="15:22", w=960, h=352) + " (each cell 240x352); the figure's feet 4 squares (32 px) above the "
     "bottom, horizontally centered, in every cell."),
]

GROUPS = [
    ("thrust", ["XinZhaoRework_Base_HIT02", "XinZhaoRework_Base_Spark_Vertical", "XinZhaoRework_Base_Star",
                "XinZhaoRework_Base_Z_Streak", "XinZhaoRework_Base_Passive_Swipe_B_Alpha", "XinZhaoRework_Base_BlastShapes"]),
    ("talon", ["XinZhaoRework_Base_Q_Swipe_C", "XinZhaoRework_Base_Q_2_Swipe_Mid", "XinZhaoRework_Base_Q_Swipe_B",
               "XinZhaoRework_Rework_Base_Q_StarGlow", "XinZhaoRework_Rework_Base_Q_Spark", "XinZhaoRework_Base_Q_Smoke_3"]),
    ("charge", ["XinZhaoRework_Base_E_Wave_Texture", "XinZhaoRework_Base_E_Nova_Mult", "XinZhaoRework_Base_Typhoon",
                "XinZhaoRework_Base_BA_Underglow", "XinZhaoRework_Base_R_Braum_Base_E_Block_Spark",
                "XinZhaoRework_Base_Q_WallDestruction"]),
    ("lightning", ["XinZhaoRework_Base_W_Mis_Base", "XinZhaoRework_Base_W_Mis_BrightLead",
                   "XinZhaoRework_Base_W_SpearSmear_v2", "XinZhaoRework_Base_W_WeaponGlow",
                   "XinZhaoRework_Base_W_Global_SS_Ghost_Swirl", "XinZhaoRework_Base_W_PassiveMark"]),
    ("crescent", ["XinZhaoRework_Base_R_BladeSwipe", "XinZhaoRework_Base_R_Credscent_FlashFrame",
                  "XinZhaoRework_Base_R_Tell_WeaponSpin", "XinZhaoRework_Base_R_Impact_Slash",
                  "XinZhaoRework_Base_R_Blast_Ring", "XinZhaoRework_Base_R_EyeforanEye01"]),
    ("guard", ["XinZhaoRework_Base_R_InvulnShield_Symbol", "XinZhaoRework_Base_R_InvulnShield_Symbol_AddLayer",
               "XinZhaoRework_Base_R_Aura_Self", "XinZhaoRework_Base_R_Braum_Base_I_shield_glow",
               "XinZhaoRework_Rework_Base_R_StarShape", "XinZhaoRework_Rework_Base_Z_StarGlow"]),
]
# where the caster pictures go: (tag, frame, what, mark) - "feet" = the standing point, "chest", "waist"
CHEST, WAIST = (66, 80), (64, 86)
SHOTS = [("skill", 2, "e_dash: 站位点（光痕往左后方拖）", "feet"), ("skill", 4, "e_land: 站位点（脚下的冲击圈）", "feet"),
         ("skill2", 4, "w_slash: 站位点（刃在身前）", "feet"), ("skill2", 5, "w_thrust: 从站位点往前一条线", "feet"),
         ("ult", 1, "r_tell: 胸口", "chest"), ("ult", 3, "r_sweep: 站位点（绕身一圈）", "feet"),
         ("attack_p", 4, "p_heal: 胸口", "chest"), ("idle", 1, "r_guard / q_marks: 脚下 / 头顶", "feet")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    on_disk = {os.path.splitext(f)[0] for f in os.listdir(REF)}
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            nm = next((x for x in sorted(on_disk) if x.lower() == nm.lower()), nm)
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("XinZhaoRework_", "").replace("Base_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
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
    d.text((8, 36), f"赵信 {fig.shape[1]}×{fig.shape[0]} 格（含长枪），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (rig_xinzhao), the point each caster picture starts from as a cyan cross."""
    import rig_xinzhao as R
    P = R.Parts()
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, mark in SHOTS:
        f = R.frames(P, tag)[k - 1]
        mx, my = {"feet": R.PIVOT, "chest": CHEST, "waist": WAIST}[mark]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0, x1 = min(xs.min(), mx) - 3, max(xs.max(), mx) + 4
        y0, y1 = min(ys.min(), my) - 3, max(ys.max(), my) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 260), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = (mx - x0) * Z + Z // 2, (my - y0) * Z + Z // 2 + 24
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
    a("# 德邦总管 赵信：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/xinzhao_design.png`，8 倍，{h} 行）。")
    a(f"> - 大小对照 `design/xinzhao_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。赵信 {w}×{h} 格（含斜架在身后的长枪，人约 30 格宽）。每条写的大小都是游戏像素（格）。")
    a("> - `design/xinzhao_shots.png`：E、W、R、被动第三下和待机的定稿动作（4 倍），青色十字是特效的起点（站位点或胸口），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里赵信自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**普攻、Q 三重爪击、被动、挑战标记、大招护卫光是德玛西亚金色（白色的芯）；W 的电刺、E 的冲锋、R 的新月刃光是电光蓝白色（带一点金边）；减速和尘土用暗蓝紫色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **绕着人的刃光、围着人的光只画边，中间留空**，不然会把人整个挡住。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `xinzhao_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`xinzhao_fx_done.zip`）放在 outputs 里。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「果决」 | 长枪突刺；每第三下大挥，额外伤害并回血 | `xinzhao_fx_a_hit` · `xinzhao_fx_p_hit` · `xinzhao_fx_p_heal` |")
    a("| 技能 1 = E「无畏冲锋」+ Q「三重爪击」 | 冲向目标，落地时周围敌人受到伤害并减速；之后 3 下强化普攻，第 3 下击飞 | `xinzhao_fx_e_dash` · `xinzhao_fx_e_land` · `xinzhao_fx_e_hit` · `xinzhao_fx_e_slow` · `xinzhao_fx_q_marks` · `xinzhao_fx_q_hit` · `xinzhao_fx_q3_up` |")
    a("| 技能 2 = W「风斩电刺」 | 先在身前横扫一刀，再往前直刺一道电光，打中的减速 | `xinzhao_fx_w_slash` · `xinzhao_fx_w_thrust` · `xinzhao_fx_w_hit` · `xinzhao_fx_w_hit2` · `xinzhao_fx_w_slow` |")
    a("| 大招 = R「新月护卫」 | 绕身横扫一圈，被挑战的目标留在身边，其余敌人被击退；之后 3 秒减伤 | `xinzhao_fx_r_tell` · `xinzhao_fx_r_sweep` · `xinzhao_fx_r_hit` · `xinzhao_fx_r_chal` · `xinzhao_fx_r_guard` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刃光、光、闪电、尘土、火花没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的挑战纹章有 1 格深色描边（`#10102A`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("德玛西亚金（普攻、Q、被动、挑战、护卫光）", GOLD), ("电光蓝白（W 电刺、E 冲锋、R 新月刃光）", STORM),
                        ("暗蓝紫（减速、尘土、阴影）", DUSK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。")
    a("- **`w_thrust` 上下必须对称**：它是一条直线的画面，游戏里会按施放方向转动，朝左放时整张转半圈，不对称的话会上下颠倒（红色方朝左放最常见）。")
    a("- 画在他身上或脚下的画面（`e_dash`、`e_land`、`w_slash`、`p_heal`、`r_tell`、`r_sweep`、`r_guard`）按每条写的站位画，**格子里留出空的人形位置，不要画人**。挂在人身上或脚下的循环画面（`r_guard`、`q_marks`、`r_chal`、`e_slow`、`w_slow`）左右对称或不分左右，因为人朝左朝右都用同一张。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：E 落地的范围半径 20000、W 电刺长 60000、R 横扫半径 36000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `xinzhao_fx_{name}.png`：{title}\n")
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
        a(f"| `xinzhao_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `q_marks` 的三行拆成 view_buffs `q_1`（3 道）、`q_2`（2 道）、`q_3`（1 道）；`r_guard`、`e_land` 的 z 是 -1（人物下面），`q_marks`、`r_chal` 画在头顶。")
    a("- 施法者身上的画面按 `design/xinzhao_shots.png` 的十字把起点挪过去；晚于第一 tick 播放的（`p_heal`、`e_land`、`w_slash`、`r_sweep`）`is_follow` 为 false（红方方向）；`e_dash`、`r_tell` 在动作第一 tick 播、跟随。")
    a("- `w_thrust` 是 LineRangeProjectile 的画面：60 格长、按方向转动，导入后用 `lint_mod.py` 量它上下翻转后的差别（要几乎为 0）。")
    a("- 清掉 Codex 给光和闪电描的最深色边（`import_riven.py` 的 `unrim`，挑战纹章保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="xinzhao_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Xin Zhao's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "xinzhao_design.png"))
    shape = size_sheet(os.path.join(out, "design", "xinzhao_size.png"))
    shots_sheet(os.path.join(out, "design", "xinzhao_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"xinzhao_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
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
