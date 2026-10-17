#!/usr/bin/env python3
"""Build anivia_fx_pack.zip: step 3 of Anivia's sprite - Codex draws her effects (pack_nasus_fx.py's way).

    python work/av/fx_ref_av.py              # League's particle textures -> %TEMP%/av_work/fxref (Riot's art, local only)
    python tools/art/pack_anivia_fx.py [--no-zip] [--out DIR] [--only a_hit,q_blast --name anivia_fx_redo_pack]

The pack (%TEMP%/av_work/fx/anivia_fx_pack, zipped into --out, default dist/anivia_packs) holds PROMPTS.md (also written
to assets/source/anivia/PROMPTS_FX.md), design/anivia_idle.png (the bird and the Rebirth egg at 4x), design/anivia_size.png
(both 1x idles at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/anivia_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures and models for Anivia grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_anivia.py): view_projectiles a_bolt, q_ball, e_shard (the
combo's shard too); view_effects a_hit, q_stun, q_blast, w_wall, e_hit, e_iced, r_cast, r_storm, r_formed, p_egg_in,
p_hatch; view_buffs iced. League's colours: ice white and cyan to a deep blue, the storm's ground a dark frost blue;
light gets no outline.
Red side: the projectiles are turned with their flight (drawn pointing right, symmetric top to bottom); every other
picture (on a unit, on her, on the ground) is symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "av_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "anivia", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_anivia")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "anivia_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ICE = "#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6"      # ice: white core, cyan, deep blue
SNOW = "#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E"     # snow, frost mist, wind
DEEP = "#BFD9F2, #7FA6D6, #4D6FB0, #2E4A8A, #1B2E60, #0E1A3A"     # the storm's frozen ground, its shadowed rim
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
IC = f"an ice ramp ({ICE})"
SN = f"a snow and frost-mist ramp ({SNOW})"
DE = f"a deep frost-blue ramp ({DEEP})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("drawn FLYING TO THE RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with "
      "its flight: flying left it is upside down)")
CENTER = "; centered in every cell."
HER = "a large ice phoenix 61 squares wide and 38 tall hovers in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack: an ice bolt
    ("a_bolt", "普攻冰弹（飞行物，循环），4 帧", "view_projectiles `league_anivia_a_bolt`（随飞行方向旋转：画成朝右飞、上下对称）", "12 × 6",
     "一小枚冰弹往右飞：尖尖的冰晶头（白芯、青色身体），后面拖 3 格霜雾和两三粒雪星，每帧闪光不一样（参考 IceArrow03、FrostCrystals）。"
     "**画成朝右飞，上下对称**（游戏会按飞行方向转它）。",
     f"{IC} and {SN}",
     f"an ICE BOLT, a seamless loop of 4 frames, {TB}: a pointed ice crystal 6 squares long and 3 tall at the right with a "
     "white core and a cyan body, a short trail of frost mist 4 squares long behind it to the left with two or three tiny "
     "snow sparkles (mirrored top to bottom), the sparkles twinkling differently in each frame.",
     row(4, 12, 6) + "; the bolt's tip 1 square from the cell's right edge, its middle on the cell's middle row."),
    ("a_hit", "普攻命中：冰屑炸开（目标身上），4 帧", "view_effects `league_anivia_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "冰弹打中：一闪白光，碎冰屑和雪星往四周溅开（参考 FrostCrystals、Flare-Rainbow_frost）。**左右对称**。约 10 格。",
     f"{IC} and {SN}",
     f"an ICE BOLT HIT on a unit, 4 frames, {LR}: 1 a white four-pointed flash 4 squares; 2 a burst of cyan ice chips 8 "
     "squares wide with a white core; 3 the chips flying out at mirrored places, snow sparkles; 4 fading frost mist.",
     row(4, 10, 10) + CENTER),
    # ---- Q Flash Frost
    ("q_ball", "Q 寒冰闪耀：大冰球（飞行物，循环），4 帧",
     "view_projectiles `league_anivia_q_ball`（随飞行方向旋转：画成朝右飞、上下对称）", "18 × 12",
     "一颗大冰球往右飞（英雄联盟里是一颗晶莹的冰晶球，外面一层霜气）：球直径约 9 格，表面有冰晶的棱面，白芯；后面拖着一大团霜雾和"
     "雪星，冰屑在球边上转（参考 Q_TX、Q_Tar_Sphere、DirtBits_frost、snowflake）。**画成朝右飞，上下对称**。",
     f"{IC} and {SN}",
     f"a FLASH FROST ORB, a seamless loop of 4 frames, {TB}: a big round ice orb 9 squares wide at the right of the cell, "
     "faceted like a crystal (bright facets, a white core, a deep blue rim), a thick trail of frost mist 8 squares long "
     "and tapering to the left, small ice chips and snow sparkles circling the orb at mirrored places (top and bottom), "
     "the mist and the sparkles different in each frame.",
     row(4, 18, 12) + "; the orb's right edge 1 square from the cell's right edge, its middle on the cell's middle row."),
    ("q_blast", "Q 引爆：冰爆（落点处，不跟随），6 帧", "view_effects `league_anivia_q_blast`（不跟随，画在人物上面；左右对称；大图表）",
     "40 × 36",
     "冰球炸开：一团白光，一圈冰碴往外飞，地上冒出一圈尖冰（扁椭圆，宽 30 格），霜雾腾起再散（参考 Q_GroundLight、groundflash、"
     "DirtBits_frost、Flare-Rainbow_frost）。**左右对称**。",
     f"{IC} and {SN}",
     f"a FLASH FROST DETONATION at a spot on the ground, 6 frames, {LR}: 1 a white flash 10 squares with short white rays; "
     "2 a cyan-white burst 20 squares, a ring of ice shards flying out; 3 the shards 30 squares wide, a ring of sharp ice "
     "spikes jutting up from the ground (an ellipse 30 squares wide and 10 tall, spikes 4 to 8 squares tall), frost mist "
     "billowing; 4 the spikes at their tallest, the mist 36 squares wide; 5 the spikes cracking, the mist thinning; 6 a "
     "few ice chips and faint mist on the ground.",
     row(6, 40, 36) + "; centered across, the ground ellipse's middle 10 squares above the cell's bottom row."),
    ("q_stun", "Q 冰冻眩晕（被晕的目标身上，约 1.1 秒），6 帧", "view_effects `league_anivia_q_stun`（跟随，画在人物上面；左右对称）",
     "22 × 40",
     f"被寒冰闪耀晕住的人：脚下迅速冻起一层冰壳（到膝盖高），身边竖起几根冰晶，头顶冒冷气；最后冰壳裂开碎掉（参考 FrostCrystals、"
     f"IceShards、snowdust）。**左右对称**，中间身体位置留空（{CHAMP}），冰壳画在脚和小腿的外缘、两边。",
     f"{IC} and {SN}",
     f"a FREEZE round a stunned champion, 6 frames, {LR} ({CHAMP}): 1 frost creeping out round the feet (a pale ellipse "
     "16 squares wide and 4 tall); 2 an ice crust growing up both sides of the legs to the knees (12 squares tall), 3 "
     "sharp ice crystals 6 to 8 squares tall at its sides, cold mist curling over the head; 3 and 4 the crust whole and "
     "glinting (a white glint moving up it); 5 the crust cracked with white lines; 6 shattering into ice chips flying "
     "out at mirrored places.",
     row(6, 22, 40) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- W Crystallize (rides on Q)
    ("w_wall", "W 寒冰屏障：一排冰墙（墙心在落点，不跟随，5 秒），8 帧（1–2 长出、3–6 循环、7–8 融化碎掉）",
     "view_effects `league_anivia_w_wall`（不跟随，画在人物上面；左右对称；大图表；3–6 帧循环铺满 5 秒）", "20 × 76",
     "一面**竖着的冰墙**：英雄联盟里是一排冰块（附图 iceblock：一根高高的锯齿状冰柱，旁边几根小冰晶，底下一圈雪）。在我们的画面里墙是"
     "**沿着屏幕上下方向排开的 5 根冰柱**（远的在上、近的在下，互相叠一点），每根约 12 格高、10 格宽；墙心（落点）在格子中间那一行，"
     "最上面一根冰柱的底在墙心上方 25 格，最下面一根的底在墙心下方 25 格。第 1 帧冰柱从地里冒出来（矮，冰屑飞溅）；第 2 帧长到全高；"
     "第 3–6 帧循环（冰柱上的高光一闪一闪、地面冒冷气，第 6 帧接得回第 3 帧）；第 7 帧冰柱出现裂纹、变矮；第 8 帧碎成冰碴。"
     "**左右对称**（每根冰柱都画成左右对称的）。",
     f"{IC} and {SN}",
     f"an ICE WALL, 8 frames (1-2 it rises, 3-6 a seamless loop, 7-8 it breaks), {LR}: five upright ice pillars in a "
     "vertical column down the cell (the far ones higher up, the near ones lower down, each overlapping the one behind), "
     "each pillar a tall jagged ice crystal 12 squares tall and 10 wide with two small crystals at its foot and a ring of "
     "snow at its base, white-cyan facets, a white glint, a deep blue shadowed side (each pillar symmetric left to right); "
     "the pillars' bases on rows 13, 25, 38, 50 and 63 of the cell (row 38 the wall's middle); 1 the pillars only 4 "
     "squares tall bursting from the ground with ice chips flying; 2 full height; 3, 4, 5, 6 the loop: glints running up "
     "the pillars, cold mist at their feet, different in each frame (6 flows back into 3); 7 the pillars cracked with "
     "white lines and a little shorter; 8 shattered into falling ice chips and mist.",
     row(8, 20, 76) + "; centered across; the wall's middle (where it was cast) on the cell's middle row (row 38)."),
    # ---- E Frostbite
    ("e_shard", "E 霜寒刺骨：冰锥（飞行物，循环），3 帧", "view_projectiles `league_anivia_e_shard`（随飞行方向旋转：画成朝右飞、上下对称）",
     "14 × 6",
     "一根冰锥往右飞：长 10 格的尖冰锥（白色刃边、青色锥身），后面一小缕霜雾（参考 IceArrow03、E_GroundLight）。**画成朝右飞，上下对称**。",
     f"{IC} and {SN}",
     f"a FROSTBITE ICICLE, a seamless loop of 3 frames, {TB}: a sharp icicle 10 squares long and 3 tall pointing right, "
     "white edges, a cyan body, a white glint, a thin wisp of frost mist 3 squares long behind it, the glint and the wisp "
     "different in each frame.",
     row(3, 14, 6) + "; the tip 1 square from the cell's right edge, its middle on the cell's middle row."),
    ("e_hit", "E 命中：冰锥碎裂（目标身上），4 帧", "view_effects `league_anivia_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "冰锥打中碎开：白光一闪，尖冰碎片往外飞，冷气散开。**左右对称**。约 14 格。",
     f"{IC} and {SN}",
     f"an ICICLE SHATTERING on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 a cyan-white burst 10 squares, sharp "
     "ice splinters; 3 the splinters 14 squares out at mirrored places, frost mist; 4 fading mist and two or three chips.",
     row(4, 14, 14) + CENTER),
    ("e_iced", "E 打冰冻目标：加倍的冰爆（目标身上），5 帧", "view_effects `league_anivia_e_iced`（跟随，画在人物上面；左右对称）", "20",
     "打中被冻住的目标（伤害翻倍）：比普通命中大一圈的冰爆，中间闪出一枚大雪花，冰碴和雪星往外炸（参考 snowflake、"
     "Flare-Rainbow_frost、frost_sprites）。**左右对称**。约 20 格。",
     f"{IC} and {SN}",
     f"a DOUBLED FROSTBITE on a frozen unit, 5 frames, {LR}: 1 a white star flash 8 squares; 2 a big six-armed snowflake "
     "14 squares wide flashing white-cyan, a cyan burst behind it; 3 the snowflake 18 squares, ice shards bursting out at "
     "mirrored places; 4 the snowflake breaking into sparkles, the shards 20 squares out; 5 fading sparkles and mist.",
     row(5, 20, 20) + CENTER),
    # ---- R Glacial Storm
    ("r_cast", "R 冰川风暴施法：双翼卷起风雪（她身上，跟随），6 帧", "view_effects `league_anivia_r_cast`（跟随，画在人物上面；左右对称）",
     "70 × 52",
     f"她高举双翼召唤风暴：身边卷起两股风雪，从地面往上盘旋到翅膀高处，雪花、冷风纹绕着她飞，最后散开（参考 R_Frost、wind_streaks、"
     f"WindSwirl、snowdust）。**左右对称**，中间她的位置留空（{HER}），风雪画在她两边和身后的外缘。",
     f"{SN} and {IC}",
     f"a BLIZZARD CALLED round a hovering phoenix, 6 frames, {LR} ({HER}): 1 a cold gust ring on the ground under her (an "
     "ellipse 40 squares wide and 8 tall of white wind streaks); 2 two spirals of snow and wind rising on both sides from "
     "the ground; 3 the spirals up to her wings' height (40 squares), snowflakes swirling; 4 the widest, wind streaks "
     "curving round her; 5 the spirals breaking into snow; 6 falling snowflakes.",
     row(6, 70, 52) + "; centered across, her lowest point (the ground) on the cell's bottom row."),
    ("r_storm", "R 风暴生长：从小变大（落点，不跟随，1.5 秒），6 帧", "view_effects `league_anivia_r_storm`（不跟随，画在人物下面；左右对称；大图表）",
     "72 × 48",
     "冰川风暴落地、一点点变大：每两帧大一档（地面上冻结的圆：宽 26 → 38 → 50 格），圆里地面结霜发暗，边上一圈白色风雪往里打旋，"
     "风雪柱 8–14 格高（参考 R_Frost、R_Ground_Darkness、wind_Streaks、snowdust）。**左右对称**。",
     f"{DE}, {SN} and {IC}",
     f"a GLACIAL STORM GROWING on the ground seen from above at an angle, 6 frames, {LR}: frames 1-2 a frozen disc (an "
     "ellipse 26 squares wide and 10 tall: frosted ground in the deep blue ramp, darker at its rim) with a ring of white "
     "snow and wind swirling round its edge 8 squares tall; frames 3-4 the same 38 squares wide and 14 tall, the swirl 11 "
     "squares tall; frames 5-6 50 squares wide and 18 tall, the swirl 14 squares tall; snowflakes and wind streaks "
     "different in each frame, sparkling ice crystals at the rim.",
     row(6, 72, 48) + "; centered across, the ellipse's middle 14 squares above the cell's bottom row."),
    ("r_formed", "R 风暴成形：大暴风雪（落点，不跟随，约 4.5 秒），8 帧（1–2 长满、3–6 循环、7–8 散去）",
     "view_effects `league_anivia_r_formed`（不跟随，画在人物下面；左右对称；大图表；3–6 帧循环铺满）", "76 × 52",
     "风暴长满（伤害变 3 倍）：一大片冻住的地面（宽 64 格），整圈白色暴风雪墙往上卷到 20 格高，冰晶在边上闪，雪花在圈里飞；"
     "第 1 帧一道白蓝的闪光表示成形；第 3–6 帧循环（第 6 帧接得回第 3 帧）；第 7–8 帧风雪变弱、散开。**左右对称**。",
     f"{DE}, {SN} and {IC}",
     f"a FULL GLACIAL STORM on the ground seen from above at an angle, 8 frames (1-2 it forms, 3-6 a seamless loop, 7-8 "
     f"it dies), {LR}: a frozen disc (an ellipse 64 squares wide and 24 tall, frosted ground in the deep blue ramp, its "
     "rim darker), a wall of white blizzard swirling round its whole edge up to 20 squares tall (snow, wind streaks, the "
     "near side brighter), ice crystals glinting at the rim, snowflakes flying inside; 1 a white-blue flash ring as it "
     "forms; 2 the blizzard rising; 3, 4, 5, 6 the loop, the swirl turning (6 flows back into 3); 7 the blizzard low, the "
     "disc fading; 8 a faint frosted ellipse and falling snow.",
     row(8, 76, 52) + "; centered across, the ellipse's middle 14 squares above the cell's bottom row."),
    # ---- the Iced mark (Flash Frost / the formed storm struck the champion: Frostbite doubles)
    ("iced", "冰冻标记：头顶的雪花（被冻住的英雄身上，约 3 秒，循环），4 帧",
     "view_buffs `league_anivia_iced`（跟随，画在人物上面；左右对称；循环）", "20 × 44",
     f"被寒冰闪耀或成形的风暴冻住的英雄（这时霜寒刺骨伤害翻倍）：头顶浮着一枚冰蓝色的雪花，一亮一暗；身上飘几粒雪星，脚边一圈淡淡的白霜"
     f"（参考 snowflake、frost_sprites）。**左右对称**，中间身体位置留空（{CHAMP}）。",
     f"{IC} and {SN}",
     f"an ICED MARK on a champion, 4 frames, a seamless loop, {LR} ({CHAMP}): a six-armed ice-blue snowflake 7 squares "
     "wide floating over its head (1 dim, 2 bright, 3 brightest with a white centre, 4 bright), two or three tiny snow "
     "sparkles drifting down past the body's sides, a faint white frost ellipse round the feet (14 squares wide, 3 tall).",
     row(4, 20, 44) + "; centered across, the figure's feet on the cell's bottom row, the snowflake's top 1 square under "
                      "the cell's top."),
    # ---- Rebirth (the add-on's egg; pictures in the main pack)
    ("p_egg_in", "寒霜涅槃：变成冰蛋的冰爆（她身上，跟随），4 帧", "view_effects `league_anivia_p_egg_in`（跟随，画在人物上面；左右对称）",
     "64 × 48",
     f"受到致命伤害、缩进冰蛋的一瞬间：一团白光把她整个包住，冰晶从四周往中间合拢，冷气爆开，最后剩一圈霜雾（这团冰爆要盖住"
     f"「鸟变成蛋」的那一下）（参考 FrostOut、SoftShockwave、snowdust、英雄联盟碎蛋 egg_break）。**左右对称**（{HER}，"
     f"这次**要**盖住她）。",
     f"{IC} and {SN}",
     f"a REBIRTH FLASH: a hovering phoenix turning into an ice egg, 4 frames, {LR} ({HER}; this one DOES cover her): 1 a "
     "big white-cyan flash 40 squares wide covering her body; 2 ice crystals closing in from all sides towards the "
     "middle, a white core 30 squares; 3 the crystals meeting low in the middle (where the egg will sit, 27 squares wide "
     "and 19 tall on the ground), cold mist bursting out; 4 a ring of frost mist settling round the bottom.",
     row(4, 64, 48) + "; centered across, the ground on the cell's bottom row."),
    ("p_hatch", "寒霜涅槃：破壳孵化（她身上，跟随），4 帧", "view_effects `league_anivia_p_hatch`（跟随，画在人物上面；左右对称）",
     "40 × 32",
     "冰蛋撑过去、破壳：蛋壳碎片往上、往两边飞，白光一闪，雪星和冷气散开（参考 egg_break、IceShards、snowdust）。"
     "**左右对称**。",
     f"{IC} and {SN}",
     f"an ICE EGG HATCHING, 4 frames, {LR}: 1 a white flash 14 squares low in the middle (where an egg 27 squares wide "
     "and 19 tall sat on the ground); 2 curved shell fragments (pale ice blue with frosty white edges) flying up and out "
     "at mirrored places, snow sparkles; 3 the fragments 36 squares apart and falling, cold mist; 4 a few fragments and "
     "sparkles on the ground.",
     row(4, 40, 32) + "; centered across, the ground on the cell's bottom row."),
]
BIG_FX = ["q_blast", "w_wall", "r_storm", "r_formed"]
REDO = {}
GROUPS = [
    ("a_bolt a_hit", ["common_IceArrow03", "Anivia_Base_Z_FrostCrystals", "common_Flare-Rainbow_frost_01",
                      "common_frost_sprites_01"]),
    ("q_ball q_blast q_stun", ["Anivia_Base_Q_TX", "Anivia_Base_Q_Tar_Sphere", "Anivia_Base_Q_GroundLight_01",
                               "common_DirtBits_frost_01", "Anivia_Base_groundflash", "common_snowflake_sam_04"]),
    ("w_wall", ["iceblock", "Anivia_Skn5_IceShards_TX", "common_snowdust"]),
    ("e_shard e_hit e_iced", ["common_IceArrow03", "Anivia_Base_E_GroundLight_01", "common_Flare-Rainbow_blue_01",
                              "common_snowflake_sam_04"]),
    ("r_cast r_storm r_formed", ["Anivia_Base_R_Frost", "Anivia_Base_R_Ground_Darkness", "common_wind_Streaks_03",
                                 "common_wind_streaks", "Anivia_Base_Z_WindSwirl01", "common_snowdust"]),
    ("iced", ["common_snowflake_sam_04", "common_frost_sprites_01"]),
    ("p_egg_in p_hatch", ["egg_break", "Anivia_FrostOut", "Anivia_skn5_SoftShockwave", "common_snowdust"]),
]
FEET = 11                                             # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_bolt：冰弹在这帧出手，飞向前方的目标"), ("skill", 3, "q_ball：冰球在这帧出手，飞到落点引爆"),
         ("skill2", 3, "e_shard：冰锥在这帧出手"), ("ult", 2, "r_cast：双翼高举，风暴落在目标处"),
         ("egg_in", 1, "p_egg_in：从这只鸟变成蛋（盖住这一下）"), ("egg_in", 2, "（参考）冰蛋"),
         ("hatch", 3, "p_hatch：蛋破、她冲出来"), ("idle", 1, "（参考）待机")]


def ref_sheet(path):
    S, LW = 180, 190
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                sys.exit(f"missing reference {p}")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Anivia_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    figs = [first_1x("idle"), first_1x("egg")]
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
    d.text((8, 36), f"艾尼维亚 {figs[0].shape[1]}×{figs[0].shape[0]} 格，冰蛋 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape, figs[1].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(f.shape[0] / 2 + FEET))
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 260), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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
    """The bird and the egg at 4x, the designs' own squares (PPU 1.2: 1.2 squares a game pixel)."""
    import rig_anivia as A
    F = A.form_a()
    E = A.Egg(F)
    tiles = []
    for f in (F, E):
        c = f.rig.finish(f.pose())
        ys, xs = np.nonzero(c[..., 3] > 0)
        tiles.append(c[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    H = max(t.shape[0] for t in tiles)
    W = sum(t.shape[1] for t in tiles) + 8
    can = np.zeros((H, W, 4), np.uint8)
    x = 0
    for t in tiles:
        can[H - t.shape[0]:, x:x + t.shape[1]] = t
        x += t.shape[1] + 8
    Image.fromarray(np.repeat(np.repeat(can, 4, 0), 4, 1)).save(path)


def document(shapes):
    (h, w), (bh, bw) = shapes[0][:2], shapes[1][:2]
    L = []
    a = L.append
    a("# 冰晶凤凰 艾尼维亚：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/anivia_idle.png`：3/4 正面朝右的冰晶凤凰，冰蓝色的冰晶羽毛，"
      f"冰刺头冠、紫色额晶、洋红眼睛，近侧翅膀向下展开、远侧翅膀扬起；右边是寒霜涅槃的冰蛋）。她在游戏里是**高清**的"
      f"（每个游戏格子里 1.2×1.2 个细像素），{h} 格高、{w} 格宽，冰蛋 {bh} 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），"
      f"不用画成高清。")
    a("> - 大小对照 `design/anivia_size.png`：鸟和冰蛋的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/anivia_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效在哪一帧、出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里艾尼维亚自己的特效贴图和模型（大多是灰度或单色的形状，游戏里再上色；`iceblock` 是"
      "冰墙的冰块模型，`egg_break` 是冰蛋碎开的一帧），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版："
      "**冰是白芯、青色、深蓝**，**雪和霜雾是白到淡蓝灰**，**风暴的地面是暗一些的霜蓝**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人（变蛋那张例外，写在那条里）。")
    a("> - **飞行物（a_bolt、q_ball、e_shard）画成往右飞、上下对称**：游戏按飞行方向转它，往左飞时整张图转半圈，上下对称才不会倒过来。")
    a("> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，她和目标朝左时也是同一张图。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 15]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `anivia_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/anivia_fx/` 里，再打包成 `outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 一枚冰弹飞向目标 | `a_bolt` · `a_hit` |")
    a("| 技能 1 = Q「寒冰闪耀」 | 大冰球飞向落点，碰到第一个英雄或到点就引爆，范围眩晕；晕到英雄时顺带 W「寒冰屏障」在原地竖起一面冰墙 5 秒 | `q_ball` · `q_blast` · `q_stun` · `w_wall` |")
    a("| 技能 2 = E「霜寒刺骨」 | 一根冰锥打一个目标，打冻住的目标伤害翻倍 | `e_shard` · `e_hit` · `e_iced` |")
    a("| 大招「冰川风暴」 | 目标处落下暴风雪，1.5 秒里从小长大，长满后伤害变 3 倍 | `r_cast` · `r_storm` · `r_formed` |")
    a("| 冰冻标记 | 被 Q 或长满的风暴打中的英雄 3 秒里头顶一枚雪花（这时 E 翻倍） | `iced` |")
    a("| 被动「寒霜涅槃」（扩展包） | 受到致命伤害变成冰蛋，撑过去就孵化 | `p_egg_in` · `p_hatch` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冰的反光、雪、霜雾、风、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（冰柱、冰晶这种实心的东西可以有深蓝的暗面，但不要一圈黑）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("冰（冰弹、冰球、冰锥、冰墙、冰爆）", ICE), ("雪、霜雾、风（拖尾、冷气、暴风雪）", SNOW),
                        ("风暴冻住的地面", DEEP)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 的爆炸半径 14000，"
      "冰墙长 50000，风暴半径 12000 → 32000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `anivia_fx_{name}.png`：{title}\n")
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
        a(f"| `anivia_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_anivia_fx`（小的）和 `league_anivia_big`（{'、'.join(BIG_FX)}），tag = 名字（build_anivia.py 的 views）。")
    a("- 飞行物 a_bolt、q_ball、e_shard（连招的 e_combo 用 e_shard 的 tag）随飞行方向旋转，导入时断言上下对称；其余断言左右对称。"
      "`q_blast`、`w_wall`、`r_storm`、`r_formed` 不跟随（地上的画面）；`r_storm`、`r_formed` 画在人物下面（z -1）；`w_wall` 第 3–6 帧循环铺满 5 秒"
      "（w_t 300 tick），`r_formed` 第 3–6 帧循环铺满 r_t - 3 r_grow = 270 tick；`r_storm` 6 帧铺满 3 r_grow = 90 tick；`q_stun` 铺满 q_stun 66 tick。")
    a("- 用 `pixel_1x/` 切格（import_nasus_fx / import_swain_fx 的做法），清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="anivia_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "anivia_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/av/fx_ref_av.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "anivia_idle.png"))
    shapes = size_sheet(os.path.join(out, "design", "anivia_size.png"))
    shots_sheet(os.path.join(out, "design", "anivia_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"anivia_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
