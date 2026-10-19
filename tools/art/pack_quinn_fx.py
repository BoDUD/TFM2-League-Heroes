#!/usr/bin/env python3
"""Build quinn_fx_pack.zip: step 3 of Quinn's sprite - Codex draws her effects (pack_rammus_fx.py's way, its sheets reused).

    python <scratchpad>/fx_ref_qn.py           # League's particle textures -> C:/t/qn_work/fxref (Riot's art, local only)
    python tools/art/pack_quinn_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name quinn_fx_redo_pack]

The pack (C:/t/qn_work/fx/quinn_fx_pack, zipped into --out, default dist/quinn_packs) holds PROMPTS.md (also written to
assets/source/quinn/PROMPTS_FX.md), design/quinn_idle.png (her idle at 4x, the design's own squares),
design/quinn_valor.png (Valor's approved design at 4x: the eagle in q_bird, p_dive and the circling buff),
design/quinn_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/quinn_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Quinn and Valor grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_quinn.py): view_projectiles a_bolt, q_bird (Valor flying out
and home); view_effects a_hit, p_dive, p_hit, q_burst, q_hit, e_hit, r_call, r_land, r_hit and the add-on's r_mount_fx;
view_buffs valor (circling over her head), q_blind, e_slow, w_haste. League's colours: Valor's deep blue-violet feathers
with bright blue tips and a gold beak (the design's), her bolts gold and steel, wind in white-blue, Skystrike's rays
gold. Red side: the client never mirrors an effect picture, so every hit, buff and ground picture is symmetric left to
right (Valor circling is a loop that looks the same either way: it alone needs no per-frame symmetry); a projectile's
picture is turned with its flight (drawn flying right), so it is symmetric top to bottom instead - Valor in flight is
seen from directly above, his wings mirror-images up and down.
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/qn_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "quinn", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_quinn")
VALOR = os.path.join(ROOT, "assets", "source", "quinn", "hd", "valor.png")
NAME = "quinn_fx_pack"

FEATHER = "#FFFFFF, #8EC8FF, #0DA3FD, #0A6EFC, #0151FB, #0527B5, #2D0D72, #1C0D3A"   # Valor's blue feathers (the design)
PLUME = "#FFFFFF, #E2D4FF, #A98CF0, #7A4FD8, #530B97, #2D0D72"                      # violet feather tips
GOLD = "#FFFFFF, #FFF4C8, #FFD870, #F2B030, #DC9440, #BF781E, #7A4410"              # bolt heads, beak, Skystrike's rays
WIND = "#FFFFFF, #EEF6FF, #C8E2FF, #8FC0F5, #5A8FD8"                                # white-blue wind
STEEL = "#F2F6FA, #C0CAD8, #8A96AA, #5A6478, #343A4A"                               # the bolt's shaft (solid)
RED = "#FFFFFF, #FFC0B4, #FF6A55, #D0302A, #7A1414"                                 # the disarm's X
FE = f"Valor's blue feather ramp ({FEATHER})"
PL = f"a violet feather-tip ramp ({PLUME})"
GO = f"a gold light ramp ({GOLD})"
WI = f"a white-blue wind ramp ({WIND})"
ST = f"a steel ramp ({STEEL})"
RE = f"a red ramp ({RED})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, energy, wind, sparks, rings or shockwaves (the eagle, the feathers, the "
                       "bolt and the eye are solid things: a 1-square near-black #090013 outline round them)")
LR = RF.LR
TB = ("flying RIGHT, the tail on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the "
      "picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
HER = ("the young ranger stands in the middle, not drawn: 38 squares from her winged visor to the ground (the cell's "
       "bottom row is the ground), about 24 squares wide")
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack, Harrier, W
    ("a_bolt", "普攻：弩箭（弹道，循环），2 帧",
     "view_projectiles `league_quinn_a_bolt`（跟着弹道转向；上下对称）", "12 × 5",
     "她手腕弩射出的箭：金色的箭头、钢色的箭杆、尾部上下各一小片羽，后面拖一道很短的白蓝色风痕（参考 ba_arrow、ba_glow_arrow）。"
     "**朝右飞，箭头在右，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的），2 帧循环（风痕闪动）。",
     f"{GO}, {ST} and {WI}",
     "A CROSSBOW BOLT, 2 frames, a seamless loop, " + TB + ": a gold arrowhead 3 squares long at the right, a 6-square "
     "steel shaft, a tiny fletching square above and below its tail, a short white-blue streak behind it; the streak "
     "flickers between the frames.",
     row(2, 12, 5) + "; the shaft on the cell's middle row, the arrowhead's tip 1 square from the right edge."),
    ("a_hit", "普攻：箭打中目标，3 帧", "view_effects `league_quinn_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "10 × 10",
     "箭打中的一下：白金色的十字星闪（参考 ba_hit_hitflash、ba_pointstaradd），溅出几粒金色的碎光。**左右对称**。",
     GO,
     "A SMALL BOLT HIT, 3 frames, " + LR + ": 1 a white-gold four-pointed star flash 5 squares across; 2 the star 9 "
     "across with 4 gold sparks flying out; 3 only the sparks further out, fading.",
     row(3, 10, 10) + CENTER),
    ("p_dive", "侵扰：华洛俯冲到被标记的目标头上，6 帧",
     "view_effects `league_quinn_p_dive`（大表，在目标身上 z 3；左右对称）", "24 × 34",
     "侵扰：每 8 秒华洛标记一次目标，下一箭时他从高处笔直俯冲到目标头上再拉起来（参考 quinn_w_falconsharp 的鹰头、feathers）。"
     "**画正面（迎面看着他扑下来），左右对称**；华洛照 `design/quinn_valor.png`（深蓝紫色羽毛、亮蓝的翅尖、金色的喙和爪），"
     "格子最下面 6 行的中间是目标的头顶（不画目标）。",
     f"{FE}, {PL} and {GO}",
     "AN EAGLE DIVING ON A TARGET, seen from the front, 6 frames, " + LR + ": the eagle (deep blue-violet feathers, "
     "bright blue wing tips, a gold beak and gold talons - the attached Valor design) 1 small and high at the top of the "
     "cell, wings folded; 2 diving straight down, bigger, wings swept back in a V; 3 just over the bottom middle (the "
     "target's head), wings opening, talons forward; 4 wings wide open (the full cell width), 3-4 blue feathers flying "
     "off; 5 rising again, wings beating down; 6 only the drifting feathers, fading.",
     row(6, 24, 34) + "; the target's head at the middle of the bottom 6 rows, not drawn."),
    ("p_hit", "侵扰：带标记的一箭打中（多一段伤害），4 帧",
     "view_effects `league_quinn_p_hit`（跟随目标 z 2；左右对称）", "16 × 16",
     "侵扰那一箭的命中：比普攻大一圈的白金星闪，后面闪过一个蓝色的鹰头剪影和一对金色的眼睛（参考 quinn_w_falconsharp、"
     "quinn_w_falconbloom），四周飞出几片蓝紫色的羽毛。**左右对称**。",
     f"{GO}, {FE} and {PL}",
     "A HARRIER HIT, 4 frames, " + LR + ": 1 a white-gold star flash 7 squares across; 2 a blue eagle's head silhouette "
     "10 squares wide appears behind the flash, two gold eyes glowing; 3 the head fading, 6 blue-violet feathers flying "
     "out; 4 only the feathers further out, fading.",
     row(4, 16, 16) + CENTER),
    ("w_haste", "W 敏锐感知：加速时她脚下（循环），4 帧",
     "view_buffs `league_quinn_w_haste`（画在人物下面 z -1；左右对称）", "22 × 7",
     "侵扰命中后 2 秒加攻速和移速：她脚下一圈金色的光环，两端升起两道白蓝色的短速度线（参考 quinn_w_enhanced_pulsewave、"
     "w_enhanced_sparks）。从斜上方看的扁椭圆，**左右对称**。",
     f"{GO} and {WI}",
     "A HASTE RING on the ground, 4 frames, a seamless loop, " + LR + ": a flat gold ellipse 20 squares wide and 5 tall, "
     "open in the middle, with short white-blue speed lines rising from both ends; the gold brightens and the lines shift "
     "upward each frame.",
     row(4, 22, 7) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- Q Blinding Assault
    ("q_bird", "Q 炫目攻势：华洛飞出去（弹道，循环），4 帧",
     "view_projectiles `league_quinn_q_bird`（飞回来的 q_home 也用它；跟着弹道转向；上下对称）", "22 × 18",
     "华洛向前飞出去，打完再飞回她身边。**从正上方往下看**的华洛（两边翅膀向上、向下张开，互为镜像），这样上下对称：游戏按飞行"
     "方向转这张图，往左飞时整个倒过来也看不出来。头朝右、尾巴在左，翅膀扇动 4 帧循环，翅尖后面拖两道白蓝色的风痕。"
     "颜色照 `design/quinn_valor.png`。",
     f"{FE}, {PL}, {GO} and {WI}",
     "AN EAGLE FLYING, SEEN FROM DIRECTLY ABOVE, 4 frames, a seamless loop, " + TB + ": the eagle's body along the middle "
     "row (the head with its gold beak at the right, the tail fan at the left), the two wings spread up and down as "
     "mirror-images of each other (deep blue-violet feathers, bright blue tips); a wing beat: 1 wings fully spread (16 "
     "squares tip to tip), 2 wings half drawn in, 3 wings narrow (10 squares), 4 half; two short white-blue wind "
     "streaks behind the wing tips.",
     row(4, 22, 18) + "; the body on the cell's middle row, the beak 2 squares from the right edge."),
    ("q_burst", "Q：华洛在第一个敌人处爆开（地上，不跟随），6 帧",
     "view_effects `league_quinn_q_burst`（大表，打中的地点，不跟随 z 2；左右对称）", "40 × 28",
     "华洛在第一个敌人处爆开：一团深蓝色的气浪带着白蓝色的风刃向外炸开，羽毛四散（参考 q_explosion_smoke、q_wind、feathers、"
     "q_stars）。**左右对称**，中心在格子中下部（爆开的地点），落到地上是斜着看的扁椭圆。",
     f"{FE}, {PL} and {WI}",
     "A WIND-AND-FEATHER BURST, 6 frames, " + LR + ": 1 a white-blue flash 8 squares across at the centre; 2 a dark blue "
     "puff 16 squares across with 6 white wind slashes curving outward; 3 the puff 26 across, the slashes longer, 8 "
     "blue-violet feathers flying out; 4 a flat ellipse of dark blue wind 36 across on the ground, feathers at its edges; "
     "5 the ellipse thinning, feathers drifting down; 6 a few feathers and wisps fading.",
     row(6, 40, 28) + "; centered across, the burst's middle 9 squares above the cell's bottom row (the point on the "
     "ground)."),
    ("q_hit", "Q：爆开打中的每个敌人身上，3 帧", "view_effects `league_quinn_q_hit`（跟随目标 z 2；左右对称）", "14 × 14",
     "爆开打中的敌人身上：两道交叉成 X 的深蓝色爪痕，白色的芯，飞出几片羽毛（参考 q_slash_dark）。**左右对称**。",
     f"{FE}, {PL} and {WI}",
     "A TALON SLASH HIT, 3 frames, " + LR + ": 1 two dark blue claw slashes crossing in an X 8 squares across with white "
     "cores; 2 the X 12 across, 4 blue-violet feathers flying out; 3 the slashes fading, the feathers further out.",
     row(3, 14, 14) + CENTER),
    ("q_blind", "Q：被缴械的英雄头上（循环），4 帧", "view_buffs `league_quinn_q_blind`（头上 z 3；左右对称）", "12 × 9",
     "被华洛打中的英雄缴械 0.75 秒（英雄联盟是致盲，我们改成不能普攻）：头上一只打了叉的眼睛（参考 q_tar_blind_icon，"
     "英雄联盟的致盲图标），**叉是左右对称的红色 X**，眼睛白色、瞳孔深蓝。4 帧循环（叉一闪一闪）。",
     f"{RE}, {WI} and {FE}",
     "A BLINDED-EYE ICON over a head, 4 frames, a seamless loop, " + LR + ": a white almond-shaped eye 9 squares wide "
     "with a dark blue pupil, a red X 9 squares across over it; the X glows brighter on frames 2 and 3.",
     row(4, 12, 9) + CENTER),
    # ---- E Vault
    ("e_hit", "E 旋翔掠杀：踢中目标，4 帧", "view_effects `league_quinn_e_hit`（跟随目标 z 2；左右对称）", "18 × 18",
     "冲到目标身上踢中的一下：一团白蓝色的冲击闪光，外面一圈细的风环（参考 e_dash_flash、quinvalor_e_dash_shockwave），"
     "几道短风刃。**左右对称**。",
     WI,
     "A KICK IMPACT, 4 frames, " + LR + ": 1 a white-blue flash 6 squares across; 2 the flash 10 across inside a thin "
     "wind ring 14 across, 4 short white wind slashes; 3 the ring 17 across breaking into arcs, the flash gone; 4 the "
     "arcs fading.",
     row(4, 18, 18) + CENTER),
    ("e_slow", "E：被减速的目标脚下（循环），4 帧", "view_buffs `league_quinn_e_slow`（画在人物下面 z -1；左右对称）",
     "16 × 7",
     "被踢中减速的目标：脚边绕着几缕白蓝色的风，带两片小羽毛，慢慢转（参考 e_end_wind、e_end_trail）。从斜上方看的扁椭圆，"
     "**左右对称**，中间上沿留空（目标的腿）。",
     f"{WI} and {FE}",
     "A SLOWING WIND round the feet, 4 frames, a seamless loop, " + LR + ": a thin flat ellipse of white-blue wind wisps "
     "16 squares wide and 5 tall on the ground with 2 small blue feathers; the wisps travel round the ellipse frame by "
     "frame; the middle 6 squares of its top edge empty (the target's legs).",
     row(4, 16, 7) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- R Behind Enemy Lines
    ("r_call", "R 深入敌后：召唤华洛（围着她），6 帧",
     "view_effects `league_quinn_r_call`（大表，跟随她 z 2；左右对称）", "34 × 46",
     "她举弩召唤，华洛从天上盘旋下来接她：一道从天上落到她身边的金色光柱，两侧各一缕向下旋的白蓝色风，几片羽毛飘落（参考 "
     "r_light、r_channel_whisp、r_energylines）。" + "**她站在格子中间，不画人**，身体位置留空；**左右对称**。",
     f"{GO}, {WI} and {FE}",
     "A CALL FROM THE SKY round a standing figure, 6 frames, " + LR + ": 1 a thin gold light beam from the top of the "
     "cell down to the figure's head; 2 the beam wider, two white-blue wind wisps spiralling down on both sides; 3 the "
     "wisps reach her shoulders, 4 blue feathers falling; 4 a gold flash at her feet 20 squares wide, the wisps round "
     "her waist; 5 the beam fading upward, feathers drifting; 6 a few feathers and sparks fading. The figure's body (the "
     "middle 14 columns from row 10 down) stays EMPTY except the beam above her head and the thin wisps passing in "
     "front.",
     row(6, 34, 46) + "; " + HER + "."),
    ("r_land", "R：鹰翼天翔落地（她脚下的地面），6 帧",
     "view_effects `league_quinn_r_land`（大表，她脚下 z -1；左右对称）", "64 × 26",
     "骑到敌人身边后施放鹰翼天翔：她从华洛背上跃下落地，地面炸开一圈放射状的金色光芒，外面一圈深蓝色的风浪向外翻滚，羽毛飞起"
     "（参考 r_cas_fin_decal 的放射光、q_wind、feathers）。从斜上方看的扁椭圆，**左右对称**，画在她脚下（在人物下面）。",
     f"{GO}, {FE} and {WI}",
     "A SKY-STRIKE LANDING on the ground, 6 frames, " + LR + ": 1 a white-gold flash 12 squares wide on the ground; 2 "
     "radial gold light rays bursting out in a flat ellipse 36 squares wide and 12 tall; 3 the rays 50 wide, a ring of "
     "dark blue wind 54 wide and 16 tall rolling outward, 8 feathers flying up; 4 the wind ring 62 wide at the edges, "
     "the rays dimming, the feathers high; 5 the ring breaking into wisps, feathers falling; 6 a few wisps and feathers "
     "fading.",
     row(6, 64, 26) + "; centered across, the ellipse's middle 7 squares above the cell's bottom row (her feet)."),
    ("r_hit", "R：鹰翼天翔打中的敌人身上，3 帧", "view_effects `league_quinn_r_hit`（跟随目标 z 2；左右对称）", "16 × 16",
     "落地打中的每个敌人：一道向上冲的金色爪痕光（对称的 V 形），带一点风和几片羽毛。**左右对称**。",
     f"{GO}, {FE} and {WI}",
     "A GOLD STRIKE HIT, 3 frames, " + LR + ": 1 a white-gold vertical flash 4 squares wide and 10 tall; 2 two gold talon "
     "streaks in a V 14 across, 4 blue feathers flying out; 3 the V fading, the feathers further out.",
     row(3, 16, 16) + CENTER),
    # ---- Valor over her head (the main pack) and the add-on's mount
    ("valor", "华洛：在她头顶上空盘旋（循环），8 帧",
     "view_buffs `league_quinn_valor`（大表，跟随她、画在上面 z 3；整圈循环，单帧不用对称）", "40 × 18",
     "华洛平时在她头顶上空盘旋：一只**小的**华洛（翼展约 13 格，照 `design/quinn_valor.png` 缩小重画：深蓝紫色羽毛、亮蓝"
     "翅尖、金色的喙）沿着头顶上方的扁椭圆绕圈：往右飞时侧身朝右、往左飞时朝左，飞到前面稍大、绕到后面稍小稍暗。8 帧循环。"
     "格子最下一行在她头顶上方 2 格处。（这一张是整圈循环，单帧不用左右对称。）",
     f"{FE}, {PL} and {GO}",
     "A SMALL EAGLE CIRCLING over a head, 8 frames, a seamless loop: a small eagle (wingspan about 13 squares, deep "
     "blue-violet feathers, bright blue wing tips, a gold beak - the attached Valor design drawn small) flying round a "
     "flat ellipse 32 squares wide and 8 tall: 1 at the far right, banking, seen from below; 2 back-right, flying LEFT, "
     "a bit smaller and darker (behind the head); 3 back centre, flying left, smallest; 4 back-left, flying left; 5 at "
     "the far left, banking; 6 front-left, flying RIGHT, bigger; 7 front centre, flying right, biggest, wings spread; 8 "
     "front-right, flying right. No left-right symmetry needed within a frame.",
     row(8, 40, 18) + "; the ellipse centered across, its bottom 2 squares above the cell's bottom row (the top of her "
     "head is just under the cell)."),
    ("r_mount_fx", "附加包：骑上华洛的一下（围着她），5 帧",
     "view_effects `league_quinn_r_mount_fx`（附加包，大表，跟随她 z 2；左右对称）", "40 × 40",
     "附加包里大招是骑着华洛跑几秒（英雄联盟的玩法）：骑上去的一下，一圈蓝色羽毛和白蓝色的风向外炸开（参考 "
     "quinvalor_e_dash_shockwave、feathers）。围着她，**中间人的位置留空**，**左右对称**。",
     f"{FE}, {PL} and {WI}",
     "A MOUNTING BURST round a figure, 5 frames, " + LR + ": 1 a white-blue flash ring 16 squares across round the "
     "middle; 2 the ring 26 across, 8 blue-violet feathers bursting outward; 3 the ring 34 across breaking into wind "
     "arcs, the feathers further out; 4 the arcs fading, feathers drifting; 5 a few feathers fading. The middle 18 x 22 "
     "squares stay EMPTY (the rider).",
     row(5, 40, 40) + CENTER),
]
BIG_FX = ["p_dive", "q_burst", "r_call", "r_land", "valor", "r_mount_fx"]
FLYING = ["a_bolt", "q_bird"]
LOOP_ONLY = ["valor"]                 # a loop symmetric as a whole: no per-frame mirror check
GROUPS = [
    ("a_bolt a_hit p_hit", ["quinn_base_ba_arrow", "quinn_base_ba_glow_arrow", "quinn_base_ba_hit_hitflash",
                            "quinn_base_ba_pointstaradd", "quinn_w_falconsharp", "quinn_w_falconbloom"]),
    ("p_dive q_bird valor", ["quinn_base_q_mis_valor", "feathers", "quinnvalor_basicattack_01", "quinn_w_target_new",
                             "quinn_w_target_wing_new", "quinn_base_r_channel_valor_shadow"]),
    ("q_burst q_hit q_blind", ["quinn_base_q_explosion_smoke_mult", "quinn_base_q_wind", "quinn_base_q_stars",
                               "quinn_base_q_slash_dark", "quinn_base_q_tar_blind_icon", "quinn_base_q_tar_blind_flash"]),
    ("e_hit e_slow w_haste", ["quinn_base_e_dash_flash", "quinvalor_e_dash_shockwave", "quinn_base_e_end_wind",
                              "quinn_base_e_end_trail_01", "quinn_w_enhanced_pulsewave", "quinn_w_enhanced_sparks"]),
    ("r_call r_land r_hit r_mount_fx", ["quinn_base_r_light", "quinn_base_r_channel_whisp", "quinn_base_r_energylines",
                                        "quinn_base_r_cas_fin_decal", "quinn_w_enhanced_starflash", "feathers"]),
]
SHOTS = [("attack", 3, "a_bolt：弩前端射出箭；a_hit / p_hit 在目标身上"),
         ("skill", 2, "q_bird：华洛从她身边向前飞出；q_burst / q_hit 在落点"),
         ("skill2", 1, "e_hit：冲到目标身上踢中（目标身上）"), ("ult", 4, "r_call：单膝跪地举弩召唤华洛（围着她）"),
         ("ult_land", 4, "r_land：落地（她脚下）；r_hit 在敌人身上"), ("r_run", 1, "r_mount_fx：附加包里骑上华洛（围着她）"),
         ("run", 1, "w_haste：脚下的加速光环"), ("idle", 1, "valor：华洛在头顶盘旋（待机，大小参考）")]


def configure():
    """pack_rammus_fx's sheets drawn from Quinn's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "奎因"


def big(t, path):
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def design_sheet(path):
    """Her idle at 4x, the design's own squares."""
    import rig_quinn as Q
    F = Q.form()
    c = F.rig.finish(Q.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    big(c[ys.min():ys.max() + 1, xs.min():xs.max() + 1], path)


def valor_sheet(path):
    """Valor's approved design (V-2) at 4x."""
    big(np.asarray(Image.open(RF.lp(VALOR)).convert("RGBA")), path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 德玛西亚之翼 奎因：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/quinn_idle.png`：3/4 正面朝右的年轻游侠，金色鹰翼面甲、深蓝"
      f"兜帽、金色羽毛肩甲、蓝紫披风、棕色皮甲，右手腕上一把金钢色的弩向前平举；`design/quinn_valor.png`：她的鹰华洛，深蓝紫色羽毛、"
      f"亮蓝的翅尖、金色的喙和爪）。她在游戏里是**高清**的（每个游戏格子里有好几个细像素），约 38 格高（连面甲），图上的待机是"
      f" {h} 格高、{w} 格宽（连弩）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/quinn_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/quinn_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奎因和华洛自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了"
      "行，只在本地用，不要提交。颜色照英雄联盟原版：**华洛是深蓝紫色的羽毛、亮蓝的翅尖、金色的喙**，**她的箭是金色箭头、钢色箭杆**，"
      "**风是白蓝色的**，**鹰翼天翔的放射光是金色的**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、头上、脚下、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（箭、飞行的华洛）"
      "**朝右飞、尾巴在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的；所以飞行的华洛画成从正上方往下看）。"
      "只有头顶盘旋的华洛（`valor`）是整圈循环，单帧不用对称。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `quinn_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有"
      " 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）"
      f"和生图原稿 `raw/`，都放在 `outputs/quinn_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「侵扰」、W「敏锐感知」在里面） | 弩箭；每 8 秒华洛标记一次，下一箭时他俯冲到目标头上，多一段伤害，之后她加攻速移速 | "
      "`a_bolt` · `a_hit` · `p_dive` · `p_hit` · `w_haste` |")
    a("| 技能 1 = Q「炫目攻势」 | 华洛飞出去，在第一个敌人处爆开，打中的英雄缴械 0.75 秒；然后飞回她头顶 | `q_bird` · `q_burst` · "
      "`q_hit` · `q_blind` |")
    a("| 技能 2 = E「旋翔掠杀」 | 冲到目标身上踢一下（打断、减速），再向后空翻拉开 | `e_hit` · `e_slow` |")
    a("| 大招「深入敌后」 | 召唤华洛骑上，冲向敌方英雄，落地施放鹰翼天翔 | `r_call` · `r_land` · `r_hit` |")
    a("| 平时 | 华洛在她头顶盘旋（Q 飞出去、骑乘时不在） | `valor` |")
    a("| 附加包：骑乘 | 大招骑着华洛跑几秒，下一次普攻或技能施放鹰翼天翔 | `r_mount_fx` · `r_land` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、风、火花、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**；"
      "**华洛、羽毛、箭、眼睛是实体，外面一圈 1 格近黑色 `#090013` 描边**（和她本人的描边一样）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("华洛的蓝色羽毛（照定稿）", FEATHER), ("紫色的羽尖", PLUME), ("金色的光、箭头、喙", GOLD),
                        ("白蓝色的风", WIND), ("钢色的箭杆", STEEL), ("缴械的红叉", RED)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（加速光环、减速的风、落地的冲击）是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 52500，华洛最远飞 "
      "102500，鹰翼天翔半径 14000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `quinn_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `quinn_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_quinn_fx`（小的）和 `league_quinn_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_quinn.py 的 views；`q_home` 用 `q_bird` 的图）。")
    a(f"- 弹道图（{'、'.join(FLYING)}）断言上下对称，`valor` 不断言，其余断言左右对称；`q_burst` 不跟随（打中的地点）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回"
      "（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="quinn_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "quinn_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run fx_ref_qn.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "quinn_idle.png"))
    valor_sheet(os.path.join(out, "design", "quinn_valor.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "quinn_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "quinn_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"quinn_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "loop" if x[0] in LOOP_ONLY else "left-right"}
                   for x in FX], f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(RF.lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(RF.lp(zpath)):
            os.remove(RF.lp(zpath))
        with zipfile.ZipFile(RF.lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(RF.lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
