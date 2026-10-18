#!/usr/bin/env python3
"""Build wukong_fx_pack.zip: step 3 of Wukong's sprite - Codex draws his effects (pack_maokai_fx.py's way).

    python work/wk/fx_ref_wk.py              # League's particle textures -> C:/t/wk_work/fxref (Riot's art, local only)
    python tools/art/pack_wukong_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name wukong_fx_redo_pack]

The pack (C:/t/wk_work/fx/wukong_fx_pack, zipped into --out, default dist/wukong_packs) holds PROMPTS.md (also written
to assets/source/wukong/PROMPTS_FX.md), design/wukong_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/wukong_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/wukong_shots.png (the finished action frames the pictures start from, 4x), design/wukong_front_ref.png (League's
own Wukong seen from the front: the clone is drawn from the front) and refs/lol_fx_ref.png (League's own particle
textures for Wukong grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_wukong.py): view_effects a_hit, q_hit, e_cloud, e_land, e_hit,
w_poof, w_clone, w_clone_atk, w_clone_spin, w_hit, r_hit; view_buffs q_shred (Crushing Blow's armour break), r_on (the
whirl round him while he spins) and p_stone (Stone Skin at five stacks: the buff league_wukong_s_5). League's colours:
the staff's strikes and Cyclone orange-gold light with white cores, the Nimbus clouds white with pale blue shadows, the
decoy's poof grey-white smoke, the armour break a red cracked shield, Stone Skin grey stone.
Red side: the client never mirrors an effect picture, so every picture is symmetric left to right; the clone left on
the ground faces the viewer (front view, league_ekko's hologram rule) - turned to his side it would face away from the
enemies on the red side.
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
TMP = "C:/t/wk_work"
REF = os.path.join(TMP, "fxref")
FRONT = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "wk_work", "wukong_pack0", "refs", "2_wukong_frontal.png")
DOC = os.path.join(ROOT, "assets", "source", "wukong", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_wukong")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "wukong_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12"      # the staff's strikes, Cyclone, the clone's flashes
CLOUD = "#FFFFFF, #F4F6FF, #D8E2F4, #AFC2E2, #8197C4, #56688F"     # the Nimbus clouds
SMOKE = "#F4F2EE, #D6D2CC, #AEA8A2, #86807C, #5E5A58, #3A3838"     # the decoy's poof
RED = "#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08"       # the armour break
STONE = "#F0ECE4, #CBC3B6, #A1978A, #786E64, #534B45, #322D2A"     # Stone Skin
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
FIG = ("Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a "
       "1-square near-black outline round the figure, flat 3-4 step shading per material, the colours of the attached "
       "design picture.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"an orange-gold light ramp ({GOLD})"
CL = f"a white cloud ramp with pale blue shadows ({CLOUD})"
SM = f"a grey-white smoke ramp ({SMOKE})"
RE = f"a red ramp ({RED})"
ST = f"a grey stone ramp ({STONE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HIM = "the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
CLONE = ("HIS DECOY CLONE: the SAME monkey king as the attached design picture (brown fur, spiky dark-brown hair, a pale "
         "monkey face with TWO GREEN EYES, a red scarf, huge gold-and-red arm guards with silver rosettes, a gold chest "
         "plate, a long gold tabard with a red border over a dark maroon robe, purple shoes, a long brown tail, his staff: "
         "red ends with gold bands and a grey steel middle) seen FROM THE FRONT, facing the viewer, SYMMETRIC LEFT TO "
         "RIGHT (the tail rising straight up behind his head), 38 squares from his hair to his soles (his feet on one "
         "ground line), in his own colours - the clone looks exactly like him")

# name, title (zh), binding, size (game px), description (zh), ramps (None: a figure), effect, layout
FX = [
    # ---- the attack
    ("a_hit", "普攻命中：金箍棒打中（目标身上），4 帧", "view_effects `league_wukong_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "金箍棒打中目标：一团橙金色的星形闪光，中间白色，几道短短的橙色光条往外甩，几颗火星（参考 E_Impact_Flash、Flare-Omnimax、"
     "Wukong_Base_Glow）。**左右对称**。约 12 格。",
     GO,
     f"a HEAVY STAFF BLOW on a unit, 4 frames, {LR}: 1 a white flash 5 squares with a gold rim; 2 an orange-gold star "
     "burst 10 squares with a white core, 4 short orange light streaks flung out at mirrored angles; 3 the burst thinner "
     "and 12 squares, a few gold sparks at mirrored places; 4 fading sparks.",
     row(4, 12, 12) + CENTER),
    # ---- Q Crushing Blow
    ("q_hit", "Q 粉碎打击命中：伸长的棒狠狠戳中（目标身上），5 帧",
     "view_effects `league_wukong_q_hit`（跟随，画在人物上面；左右对称）", "18",
     "伸长的金箍棒狠狠戳中目标、打碎他的护甲：一道大的白金色冲击闪光，一圈橙金色的冲击环往外扩，几块红色的盔甲碎片往外飞（参考 "
     "Wukong_Base_R_Suck_flash、Wukong_Base_Shockwave1、MonkeyKing_metal_shards）。**左右对称**。约 18 格。",
     f"{GO} and {RE}",
     f"a CRUSHING STAFF THRUST on a unit, 5 frames, {LR}: 1 a white flash 7 squares; 2 a gold-white star burst 14 "
     "squares, a thin orange shock ring starting round it; 3 the ring 18 squares (1 square thick), 4 small red armour "
     "shards (2x2 squares, a dark red edge) flying out at mirrored places; 4 the ring fading, the shards farther; 5 a few "
     "sparks and shards.",
     row(5, 18, 18) + CENTER),
    ("q_shred", "Q 破甲（敌人头顶，循环），4 帧",
     "view_buffs `league_wukong_q_shred`（跟随，画在人物上面；左右对称；循环）", "12 × 46",
     f"被粉碎打击打掉护甲的敌人：头顶上方浮着一个**红色的盾牌，中间一道裂缝**，一闪一闪（参考 Jarvan_Base_P_armor_shred、"
     f"MonkeyKing_armordebuff）。**左右对称**，只画在头顶上方（{CHAMP}，盾牌在他头顶上面 2 格）。",
     RE,
     f"an ARMOUR BREAK MARK floating over a unit's head, 4 frames, a seamless loop, {LR} ({CHAMP}): a small red shield 8 "
     "squares wide and 9 tall (a pale red rim, darker red inside) with a jagged white crack down its middle, its bottom "
     "edge 2 squares above the champion's head (38 squares above the cell's bottom row); 1 dim, 2 brighter, 3 brightest "
     "(the crack flashing white), 4 like 2; nothing below it.",
     row(4, 12, 46) + "; centered across, the shield's bottom edge 38 squares above the cell's bottom row."),
    # ---- E Nimbus Strike
    ("e_cloud", "E 腾云突击：脚下的筋斗云（他身上，跟随），5 帧",
     "view_effects `league_wukong_e_cloud`（跟随，画在人物下面 z 2 前后都可；左右对称；大图表）", "56 × 24",
     f"他冲向目标时脚下踩着一朵白色的筋斗云：一团圆滚滚的白云（几团云朵叠在一起，淡蓝的阴影，边缘一圈白），左右两边拖着淡淡的风线，"
     f"云团里有几颗金色的光点（参考 Wukong_Base_Clouds、Clouds2、NimbusSides、E_Mis_self_01_Wind）。**左右对称**（游戏在红色方不会镜像，"
     f"所以云不能只往一边拖），画在他脚下（{HIM}，云在他脚下和小腿两边，上半身留空）。",
     f"{CL} and {GO}",
     f"A NIMBUS CLOUD under a figure's feet, 5 frames, {LR} ({HIM}): a puffy white cloud 40 squares wide and 10 tall made "
     "of round cloud puffs (pale blue shadows underneath, white tops, no outline) under its feet, a few gold sparkles in "
     "the puffs, thin pale wind streaks trailing out to BOTH sides (mirrored); 1 the cloud forming (24 wide); 2 full; 3 "
     "full, the puffs rolled a little; 4 like 2; 5 the cloud thinning out at both sides.",
     row(5, 56, 24) + "; centered across, the figure's feet 8 squares above the cell's bottom row."),
    ("e_land", "E 落地：云朵四散（他脚下，不跟随），5 帧",
     "view_effects `league_wukong_e_land`（不跟随，画在人物下面 z -1；左右对称；大图表）", "50 × 26",
     "他落到目标身边：脚下一圈白云猛地往两边炸开（扁椭圆的云环），中间一道金色闪光，几团小云朵往外飘、慢慢散掉（参考 Wukong_Base_Clouds、"
     "FloorShockwave、Flare-Rainbow）。**左右对称**，中间留空（他站在中间）。",
     f"{CL} and {GO}",
     f"CLOUDS BURSTING OUT AT A LANDING seen from above at an angle, 5 frames, {LR}: the middle 14 squares wide left "
     "empty above the ground (he lands there); 1 a gold-white flash on the ground 12 squares wide; 2 a ring of white "
     "cloud puffs bursting out (an ellipse 30 squares wide and 8 tall, pale blue shadows); 3 the ring 44 wide and 12 "
     "tall, small puffs drifting out at mirrored places; 4 the puffs thinning; 5 faint wisps.",
     row(5, 50, 26) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("e_hit", "E 分身打中（目标和身边敌人身上），4 帧",
     "view_effects `league_wukong_e_hit`（跟随，画在人物上面；左右对称）", "16",
     "腾云突击的分身打中敌人：一个金色半透明的猴子剪影一闪（只是一团金色光的轮廓，不用画细节）扑到目标身上，一道金色斜劈闪光，"
     "一小团白云散开（参考 MonkeyKing_shadow_step、Wukong_Base_Flicker、Wukong_Base_Clouds）。**左右对称**。约 16 格。",
     f"{GO} and {CL}",
     f"a GOLDEN CLONE STRIKE on a unit, 4 frames, {LR}: 1 a pale gold glow 8 squares (a soft monkey-like silhouette of "
     "light, no details); 2 a gold-white flash 12 squares, two gold slash streaks crossing in an X (mirrored); 3 a small "
     "white cloud puff bursting at the middle, gold sparks at mirrored places; 4 the puff and the sparks fading.",
     row(4, 16, 16) + CENTER),
    # ---- W Warrior Trickster
    ("w_poof", "W 真假猴王：隐身的一团烟（他身上，不跟随），5 帧",
     "view_effects `league_wukong_w_poof`（不跟随，画在人物上面 z 2；左右对称；大图表）", "44 × 50",
     f"他隐身冲走的那一下：在他站的地方嘭地冒出一团灰白色的烟（几团圆滚滚的烟朵），里面一道金色闪光，烟往两边和上面散开，留下分身站在"
     f"原地（参考 MonkeyKing_Poof、P_Smoke01、P_SmokeErode、MonkeyKing_monkey_king_P）。**左右对称**，烟围着人，中间偏下可以盖住身体"
     f"（{HIM}）。",
     f"{SM} and {GO}",
     f"A SMOKE POOF round a figure, 5 frames, {LR} ({HIM}): 1 a gold-white flash at the figure's chest 10 squares; 2 a "
     "burst of round grey-white smoke puffs (each puff 6-10 squares, white tops, grey shadows, no outline) round the "
     "figure 30 squares wide and 34 tall, covering it; 3 the puffs 40 wide, opening in the middle; 4 the puffs drifting "
     "out and up at both sides, thinning; 5 a few small wisps at the sides.",
     row(5, 44, 50) + "; centered across, the figure's feet 4 squares above the cell's bottom row."),
    ("w_clone", "W 分身：站着（地上，不跟随），4 帧（每段 1/3 秒反复播）",
     "view_effects `league_wukong_w_clone`（不跟随，画在人物位置 z 1；**正面、左右对称**；大图表）", "44 × 48",
     "留在原地的分身站着：**正面朝前**（脸对着看的人，左右对称），两只手叠在一起拄着竖立在身前正中的金箍棒（棒子立在两脚中间的地上，"
     "棒顶到胸口），尾巴从背后正中竖起来；轻轻地一起一伏（呼吸），尾巴尖左右摆一点也要对称（或者不摆）。**分身和悟空本人一模一样**"
     "（颜色、护臂、前襟、眼睛），参考 `design/wukong_idle.png`（他侧身的定稿，颜色和细节照它）和 `design/wukong_front_ref.png`"
     "（英雄联盟里他正面的样子）。**按游戏格子画**：头发尖到鞋底 38 格。",
     None,
     f"{CLONE}. Standing still, 4 frames, a seamless loop: BOTH HANDS stacked on top of his staff, which stands upright on "
     "the ground in front of him between his feet (its top at his chest), his elbows out; 1 standing; 2 his body a square "
     "lower (breathing); 3 like 2; 4 like 1.",
     row(4, 44, 48) + "; centered across, his soles 1 square above the cell's bottom row."),
    ("w_clone_atk", "W 分身：出手打人（地上，不跟随），4 帧（1/3 秒）",
     "view_effects `league_wukong_w_clone_atk`（不跟随；**正面、左右对称**；大图表）", "48 × 60",
     "分身每秒打一下身边的敌人：还是**正面朝前、左右对称**，两手横握金箍棒举过头顶，然后竖着往身前正中砸下去，砸到地上冒一点金光和尘土，"
     "再收回。分身和悟空一模一样，头发尖到鞋底 38 格。",
     None,
     f"{CLONE}. A two-handed overhead smash, 4 frames: 1 both hands holding the staff LEVEL high above his head (the staff "
     "36 squares long, centered); 2 the staff brought down halfway, still level, in front of his face; 3 the staff "
     "slammed down UPRIGHT in front of him in the middle (its foot on the ground between his feet), his body a square "
     "lower, a small gold flash and a puff of dust at its foot (mirrored); 4 standing again, both hands on the upright "
     "staff as in the standing pose.",
     row(4, 48, 60) + "; centered across, his soles 1 square above the cell's bottom row."),
    ("w_clone_spin", "W 分身：跟着大招转棒（地上，不跟随），4 帧（1/3 秒反复播）",
     "view_effects `league_wukong_w_clone_spin`（不跟随；**正面、左右对称**；大图表）", "84 × 48",
     "悟空放大招时分身也跟着转：**正面朝前、左右对称**，两手在腰前横握伸长的金箍棒，棒子两头伸得很长，转起来：长、短（转到朝着看的人，"
     "看起来变短）、长、短，身边一圈橙金色的弧形风（参考 Wukong_Base_RStaffSwirl、Swirl3/4/5）。分身和悟空一模一样。",
     f"{GO}",
     f"{CLONE}. Whirling his lengthened staff level at his waist with both hands, 4 frames, a seamless loop: 1 the staff "
     "LEVEL and LONG, 70 squares, centered; 2 the staff foreshortened (turned toward the viewer) to 24 squares; 3 like 1; "
     "4 like 2; round him an orange-gold whirl of curved streaks (an ellipse 76 squares wide and 18 tall at his waist, "
     "crescent shapes, white edges, no outline) in every frame, turned a little each frame; the figure itself with a "
     "1-square dark outline, the whirl without.",
     row(4, 84, 48) + "; centered across, his soles 1 square above the cell's bottom row."),
    ("w_hit", "W 分身打中（目标身上），4 帧", "view_effects `league_wukong_w_hit`（跟随，画在人物上面；左右对称）", "12",
     "分身的棒子打中敌人：比普攻小一点的金色闪光，带一点淡金色的残影（参考 Wukong_Base_Flicker、Glow2）。**左右对称**。约 12 格。",
     GO,
     f"a LIGHT STAFF TAP on a unit, 4 frames, {LR}: 1 a pale gold flash 4 squares; 2 a gold burst 9 squares with a white "
     "core; 3 a thin gold ring 11 squares, a few sparks at mirrored places; 4 fading.",
     row(4, 12, 12) + CENTER),
    # ---- R Cyclone
    ("r_on", "R 大闹天宫：转棒时身边的旋风（他身上，跟随，循环），4 帧",
     "view_buffs `league_wukong_r_on`（跟随，画在人物下面 z -1；左右对称；循环；大图表）", "76 × 40",
     f"他伸长金箍棒转起来的时候，身边一圈橙金色的旋风：一圈扁扁的金色弧形风（几道月牙形的光，白色的亮边，像棒子转过留下的残影），"
     f"脚下一圈淡淡的尘土，一帧一帧转（参考 Wukong_Base_RStaffSwirl、RStaffSwirl_、Swirl、Swirl3/4/5、MonkeyKing_staff_twirl、P_Swoop）。"
     f"**左右对称**，中间身体位置留空（{HIM}，风圈在他腰和脚的高度绕一圈）。",
     f"{GO} and {SM}",
     f"A WHIRLWIND OF STAFF STREAKS round a figure, 4 frames, a seamless loop, {LR} ({HIM}): an orange-gold ring of "
     "crescent-shaped light streaks (an ellipse 70 squares wide and 16 tall at the figure's waist, the streaks 1-2 "
     "squares thick with white edges, no outline), the middle 30 squares wide left empty where it crosses the body, a "
     "faint dust ring on the ground (an ellipse 56 wide and 8 tall); each frame the streaks moved along the ring (frame 4 "
     "flows back into frame 1).",
     row(4, 76, 40) + "; centered across, the figure's feet 4 squares above the cell's bottom row."),
    ("r_hit", "R 命中：被转棒扫中（目标身上），4 帧", "view_effects `league_wukong_r_hit`（跟随，画在人物上面；左右对称）", "16",
     "被大闹天宫扫中的敌人：一道金色的弧形横扫闪光（左右对称的两道弧），中间白色，几颗火星（参考 Wukong_Base_Swirl、R_Suck_flash）。"
     "**左右对称**。约 16 格。",
     GO,
     f"a SWEEPING STAFF HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 two gold crescent slashes curving "
     "away from the middle (mirrored, 14 squares across, white edges); 3 the crescents thinner and wider, gold sparks at "
     "mirrored places; 4 fading sparks.",
     row(4, 16, 16) + CENTER),
    # ---- passive Stone Skin
    ("p_stone", "被动金刚不坏：叠满 5 层时的石皮（他身上，跟随，循环），4 帧",
     "view_buffs `league_wukong_s_5`（tag p_stone；跟随，画在人物上面 z 2；左右对称；循环）", "50 × 50",
     f"金刚不坏叠满 5 层（护甲最高）时：他身边浮着几块灰色的小石片，绕着他慢慢转，石片上一闪一闪的白色高光，脚下一圈淡淡的灰色石尘"
     f"（参考 P_Rocks、P_rock_debris、P_shield_circle）。**左右对称**，中间身体位置留空（{HIM}，石片只在身体两边和头顶上方）。",
     ST,
     f"FLOATING STONE CHIPS round a figure, 4 frames, a seamless loop, {LR} ({HIM}): 6 small grey stone chips (3x3 to "
     "4x4 squares, a light top face, a darker side, a 1-square dark outline: solid things) floating at both sides of the "
     "figure and over its head at mirrored places, a white glint on 2 of them; a faint grey dust ring at its feet (an "
     "ellipse 30 wide and 6 tall); each frame the chips bob up or down a square (mirrored).",
     row(4, 50, 50) + "; centered across, the figure's feet 4 squares above the cell's bottom row."),
]
BIG_FX = ["e_cloud", "e_land", "w_poof", "w_clone", "w_clone_atk", "w_clone_spin", "r_on"]
REDO = {}
GROUPS = [
    ("a_hit w_hit", ["MonkeyKing_Base_E_Impact_Flash", "Flare-Omnimax", "Wukong_Base_Glow", "Wukong_Base_Glow2",
                     "Wukong_Base_Flicker", "Wukong_Base_BA_trail"]),
    ("q_hit q_shred", ["Wukong_Base_R_Suck_flash", "Wukong_Base_Shockwave1", "MonkeyKing_metal_shards_mk",
                       "Jarvan_Base_P_armor_shred", "MonkeyKing_armordebuff"]),
    ("e_cloud e_land e_hit", ["Wukong_Base_Clouds", "Wukong_Base_Clouds2", "Wukong_Base_NimbusSides",
                              "MonkeyKing_Base_E_Mis_self_01_Wind", "MonkeyKing_shadow_step_26", "Wukong_Base_FloorShockwave",
                              "MonkeyKing_Flare-Rainbow_white_05"]),
    ("w_poof", ["MonkeyKing_Poof", "MonkeyKing_Base_P_Smoke01", "MonkeyKing_Base_P_SmokeErode",
                "MonkeyKing_monkey_king_Poof_02"]),
    ("r_on r_hit w_clone_spin", ["Wukong_Base_RStaffSwirl", "Wukong_Base_RStaffSwirl_add", "Wukong_Base_Swirl",
                                 "Wukong_Base_Swirl3", "Wukong_Base_Swirl4", "MonkeyKing_staff_twirl_04",
                                 "MonkeyKing_Skin05_R_Hit_Swipe"]),
    ("p_stone", ["MonkeyKing_Base_P_Rocks", "MonkeyKing_Base_P_rock_debris", "MonkeyKing_Base_P_shield_circle",
                 "Aura_Self_02"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：金箍棒扫中前方的目标"), ("q_attack", 3, "q_hit / q_shred：伸长的棒戳中目标"),
         ("skill", 2, "e_cloud：腾空前冲，筋斗云在他脚下跟着他"), ("skill", 4, "e_land：落地；e_hit 打在目标和身边的敌人身上"),
         ("skill2", 2, "w_poof：他隐身冲走；原地留下正面的分身 w_clone"), ("spin", 1, "r_on：转棒时身边的旋风；r_hit 打在周围的敌人身上"),
         ("idle", 1, "p_stone：被动叠满 5 层时身边的石片"), ("ult", 1, "大招起手（不需要特效）")]


def ref_sheet(path):
    S, LW = 170, 200
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
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
            d.text((LW + c * S + 4, y + 2), nm.replace("Wukong_Base_", "").replace("MonkeyKing_Base_", "").replace("MonkeyKing_", "")[:26],
                   fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"悟空 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    import rig_wukong as M
    F = M.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 齐天大圣 悟空：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/wukong_idle.png`：3/4 正面朝右的猴王，棕色猴毛、尖刺头发、"
      f"绿眼睛、红围巾、金红护臂、金色前襟、暗红褐长袍、紫鞋，背后翘着长尾巴，手里竖着一根金箍棒：红色两头、金箍、灰钢中段）。他在游戏里是"
      f"**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/wukong_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/wukong_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - **三张分身图（`w_clone`、`w_clone_atk`、`w_clone_spin`）是他本人的样子**：W 留在原地的分身和悟空一模一样（英雄联盟里就是这样），"
      "但要**画成正面朝前、左右对称**（游戏在红色方不会把图镜像，侧身的分身到了红色方会背对敌人）。颜色和细节照 `design/wukong_idle.png`，"
      "正面的样子参考 `design/wukong_front_ref.png`（英雄联盟里他的正面）。分身**有一圈深色描边**（他是实心的人），"
      "头发尖到鞋底 38 格（按游戏格子画，不是高清）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里悟空自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**金箍棒的打击和大闹天宫是橙金色的光**，**筋斗云是白云带淡蓝阴影**，**真假猴王的烟是灰白色**，"
      "**破甲是一个裂开的红盾**，**金刚不坏是灰色的石头**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人（`w_poof` 例外：那团烟就是要把他盖住）。")
    a("> - **所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 14]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `wukong_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/wukong_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。"
      "中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + Q「粉碎打击」 | 金箍棒横扫；Q 好了的那一下棒子伸长戳出去，打掉目标的护甲 | `a_hit` · `q_hit` · `q_shred` |")
    a("| 技能 1 = E「腾云突击」 | 踩着筋斗云冲到目标身边，分身打中目标和身边最多两个敌人，之后攻速变快 | `e_cloud` · `e_land` · `e_hit` |")
    a("| 技能 2 = W「真假猴王」 | 嘭的一团烟隐身冲到目标身后，原地留下一个一模一样的分身（站着、每秒打一下身边的敌人；悟空放大招时也跟着转） | "
      "`w_poof` · `w_clone` · `w_clone_atk` · `w_clone_spin` · `w_hit` |")
    a("| 大招「大闹天宫」 | 金箍棒伸长转两秒，第一下把身边的敌人击飞，转完还能再转一次 | `r_on` · `r_hit` |")
    a("| 被动「金刚不坏」 | 打中英雄叠护甲，叠满 5 层时身边浮着石片 | `p_stone` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、云、风、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：分身本人、盔甲碎片、石片、破甲盾牌可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("橙金色的光（打击、大招旋风、分身的闪光）", GOLD), ("白云（筋斗云）", CLOUD), ("灰白烟（真假猴王）", SMOKE),
                        ("红色（破甲、盔甲碎片）", RED), ("灰色石头（金刚不坏）", STONE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**（三张分身图除外：那就是要画的人）。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头（光的特效一段，三张分身图另一段）。大小写在每条里（1 个游戏像素约等于 1000 距离单位："
      "大闹天宫的半径 28000，E 分身打中的半径 22000，分身打人的范围 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `wukong_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(FIG if ramps is None else LEAD.format(ramps=ramps) + (" The figure: " + FIG if name == "w_clone_spin" else ""))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `wukong_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_wukong_fx`（小的）和 `league_wukong_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_wukong.py 的 views；`p_stone` 绑 buff `league_wukong_s_5`）。")
    a("- `w_clone`、`w_clone_atk`、`w_clone_spin` 每段 20 tick（W 的 w_slot）：4 帧共 333 毫秒，分身站的地方由锚点（W 的 w_anchor）定，"
      "脚底对齐落点；`e_land`、`w_poof` 不跟随（晚播画面）。")
    a("- 用 `pixel_1x/` 切格（import_maokai_fx 的做法），断言左右对称；清掉 Codex 给光描的最深色边（分身、碎片、石片、盾牌保留描边）；"
      "核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="wukong_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "wukong_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/wk/fx_ref_wk.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "wukong_idle.png"))
    if os.path.isfile(FRONT):
        shutil.copyfile(FRONT, os.path.join(out, "design", "wukong_front_ref.png"))
    else:
        sys.exit(f"missing {FRONT} (tools/art/pack_wukong_picture.py renders it)")
    shape = size_sheet(os.path.join(out, "design", "wukong_size.png"))
    shots_sheet(os.path.join(out, "design", "wukong_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"wukong_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
