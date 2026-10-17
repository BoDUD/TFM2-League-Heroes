#!/usr/bin/env python3
"""Build smolder_fx_pack.zip: step 3 of Smolder's sprite - Codex draws his effects (tools/art/pack_malzahar_fx.py's way).

    python tools/art/pack_smolder_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name smolder_fx_redo_pack]

The pack (%TEMP%/sm_work/fx/smolder_fx_pack, zipped into --out, default dist/smolder_packs) holds PROMPTS.md (also
written to assets/source/smolder/PROMPTS_FX.md), design/smolder_idle.png (his dense design at 6x),
design/smolder_size.png (his idle as the game shows it - PPU 1.5 - at 4x a game pixel on the arena colour with the
feet line, a 10-px ruler and the base fighter beside him), design/smolder_shots.png (the action frames the pictures
start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for Smolder, grouped by the effect of ours they
inform; Riot's art, local only: %TEMP%/sm_work/fxref from Smolder.wad.client's base-skin particles,
%TEMP%/sm_work/fx/fx_ref_sm.py).
The effects are the views the kit binds (tools/kit/build_smolder.py): league_smolder_fx - view_projectiles a_bolt,
q_bolt, w_bolt, e_shot; view_effects a_hit, q_hit, q_t2_hit, q_burn, w_hit, e_hit, r_hit, r_heal, p_up; view_buffs
slow, e_haste - and league_smolder_big - q_t1, w_boom (view_effects on the spot), q_t2, r_fire, r_mom
(view_projectiles: turned with the cast). League's colours: his orange-yellow fire with white-hot cores, the pink-violet
of his top-tier flame, soot, his mother's dark shadow. Light gets no outline. Red side: the flying and turned pictures
symmetric top to bottom, every other picture symmetric left to right.
He is about 40 x 30 game px in game (PPU 1.5).
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sm_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "smolder", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_smolder")
HD_FRONT = os.path.join(ROOT, "assets", "source", "smolder", "hd", "front.png")   # the approved dense design
SHOWN = 1.5                     # his dense squares a shown game pixel
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


FIRE = "#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E"     # his orange-yellow fire, white-hot core
TIER = "#FFF0FA, #FFB0DC, #FF6FC0, #E0409E, #A0287E, #5E1A6E"              # the pink-violet of his top-tier flame
SOOT = "#B8A89E, #7A6A62, #4A3A38, #2A1C22"                                # smoke and soot
SHADE = "#5A3A6A, #3E2450, #2A1638, #180C22"                               # his mother's shadow
HEAL = "#FFFFFF, #FFE6EE, #FFB8CC, #FF86A8, #E85A86"                       # the heal's warm pink
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their "
        "edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark "
        "battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, {px} px a square)"
FR = f"an orange-yellow fire ramp ({FIRE})"
TR = f"a pink-violet hot-flame ramp ({TIER})"
SO = f"a soot ramp ({SOOT})"
SH = f"a dark shadow ramp ({SHADE})"
HE = f"a warm pink heal ramp ({HEAL})"


def row(n, cw, ch, px=16):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * px, h=ch * px, cw=cw * px, ch=ch * px, px=px)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_bolt", "普攻：吐出去的小火球（朝目标飞，循环），4 帧",
     "view_projectiles `league_smolder_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "9 × 6",
     "从嘴里吐出去的一颗小火球：白黄色的火芯，外面一层橙红色的火，后面拖一小截火尾和两三个小火星（参考 BA_Sparks、MisLead_Mask、YoungDragon_Q_Mis_Lvl1_Lead）。**上下对称**，朝右飞。",
     FR,
     f"a SMALL FIREBALL flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-yellow core 3 squares across at "
     "the front inside an orange flame, a short tapering flame tail 4 squares behind it, 2 tiny embers flickering in "
     "turn behind the tail.",
     row(4, 10, 8) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_smolder_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "小火球打中：目标身上白黄色的光一闪，炸成一小团橙色火花（参考 BA_tar_alpha、BA_muzzle_flash）。**左右对称**，居中画。",
     FR,
     f"a SMALL FIRE HIT on a unit, 4 frames, {LR}: 1 a white-yellow flash 3 squares; 2 an orange four-pointed burst "
     "8 squares across with a white core; 3 the burst breaking into 6 small orange sparks at mirrored places, 10 squares "
     "across; 4 two fading embers.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- Q Super Scorcher Breath
    ("q_bolt", "Q 超级灼热龙息：喷出去的大火球（朝目标飞，循环），4 帧",
     "view_projectiles `league_smolder_q_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "14 × 9",
     "龙息喷出的大火球：前头一团白黄色的火芯，外面一层层橙色到红色的火焰，像一颗往前冲的火流星，后面拖一条波浪形的火尾，尾巴边上一点点粉紫色（他叠层后的火，参考 Q_Mis_Lvl2_Lead、Q_Mis_Lvl3_Lead、Q_Mis_FireNoise_Horiz）。**上下对称**，朝右飞。",
     f"{FR} and {TR}",
     f"a BIG FIREBALL flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-yellow core 5 squares across at the "
     "front wrapped in orange then red flame, a wavy flame tail 8 squares long behind it whose edges are mirrored top to "
     "bottom, a little pink-violet flame at the tail's tips, 3 embers trailing.",
     row(4, 16, 11) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_hit", "Q 打中（目标身上），4 帧", "view_effects `league_smolder_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "大火球打中：目标身上白黄色的火一炸，散成一圈橙红色的火舌（参考 Q_Tar、Q_CenterShine_Tar、Q_Impactspike）。**左右对称**。",
     FR,
     f"a FIRE BLAST on a unit, 4 frames, {LR}: 1 a white-yellow flash 6 squares; 2 an orange burst 14 squares across "
     "with a white core and 6 short flame tongues; 3 the burst opening into a ring of flame tongues 16 squares across at "
     "mirrored places; 4 fading embers.",
     row(4, 18, 18) + "; centered in every cell."),
    ("q_t1", "Q 一段（10 层起）：火球在目标处炸开（地上，不跟随），6 帧",
     "view_effects `league_smolder_q_t1`（不跟随，画在人物上面；左右对称）；表 `league_smolder_big`", "44 × 26",
     "火球在目标处爆炸：地上一圈橙红色的冲击波往外扩（从斜上方看的扁椭圆，约 44 格宽），中间一团白黄色的火往上冒成一朵小火焰蘑菇，地上留一圈焦黑的痕迹，几块火星往两边飞（参考 Q_AoE_WaveOut、Q_AoE_ScorchDecal、Q_AoE_GroundEdge、Q_AoETar）。**左右对称**。",
     f"{FR} and {SO}",
     f"a FIRE EXPLOSION on the ground, 6 frames, {LR}: a flat ellipse 44 squares wide and 14 tall on the ground; 1 a "
     "white-yellow flash 8 squares at the center; 2 an orange fire burst rising 16 squares tall, a bright ring starting "
     "on the ground; 3 the shockwave ring 30 squares wide, the fire burst at its biggest with a white core; 4 the ring "
     "44 squares wide and thinner, the burst breaking into flame tongues and embers flying out at mirrored places; 5 a "
     "dark soot scorch ellipse left on the ground with a few small flames; 6 the scorch fading.",
     row(6, 46, 28) + "; centered across, the ground ellipse's center 7 squares above the cell's bottom."),
    ("q_t2", "Q 二段（25 层起）：三颗回火弹从爆炸处往后飞散（朝施法方向转），5 帧",
     "view_projectiles `league_smolder_q_t2`（朝施法方向转，画成朝右；上下对称；从格子左边开始）；表 `league_smolder_big`", "46 × 18",
     "爆炸后往后弹出的三颗回火弹：从**格子左边**（爆炸的地方）出发，往右（远离斯莫德的方向）飞散成一个扇形——中间一颗直着飞，上下两颗斜着飞（**上下对称**），每颗是一个带短火尾的小火球，越飞越远、最后炸成小火花（参考 Q_Mis_Lvl2_Lead、Sparks_2x2）。",
     FR,
     f"THREE BLOWBACK FIREBALLS fanning out to the RIGHT, 5 frames, {TB}: they start together at the LEFT edge "
     "(vertically centered) and fly right in a fan - one straight along the middle, two at mirrored angles up and down "
     "(15 degrees); each fireball a white-yellow core 3 squares across in orange flame with a short flame tail; 1 the "
     "three just leaving the left edge; 2 at 12 squares; 3 at 24 squares, the fan 10 squares tall; 4 at 36 squares; 5 "
     "each bursting into small orange sparks at the right end, the fan 16 squares tall.",
     row(5, 48, 20) + "; vertically centered in every cell."),
    ("q_t2_hit", "Q 二段：回火弹打中身后的敌人（目标身上），3 帧",
     "view_effects `league_smolder_q_t2_hit`（跟随，画在人物上面；左右对称）", "10",
     "回火弹打中：目标身上一小团橙色火花一炸。**左右对称**。",
     FR,
     f"a SMALL FIRE POP on a unit, 3 frames, {LR}: 1 a white-yellow flash 4 squares; 2 an orange burst 9 squares with 4 "
     "sparks at mirrored places; 3 fading embers.",
     row(3, 12, 12) + "; centered in every cell."),
    ("q_burn", "Q 三段（40 层起）：目标身上的灼烧（目标身上，每秒放一次，持续 3 秒），4 帧",
     "view_effects `league_smolder_q_burn`（跟随，画在人物上面；左右对称；4 帧约 1 秒）", "18 × 22",
     "被灼烧：目标身上两边一缕缕粉紫色和橙色的火苗往上蹿（他最高一段的火，参考 Q_Burn_ColorMask、Q_Mis_Lvl3_ColorMask、4x4Fire），中间人形位置留空。**左右对称**。",
     f"{TR} and {FR}",
     f"HOT FLAMES licking up a unit, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 8 squares "
     "wide and 18 tall): at each side 2-3 flame tongues 6-10 squares tall, pink-violet at their roots turning orange and "
     "white-yellow at their tips, flickering a step each frame (every frame mirrored), a few embers rising.",
     row(4, 20, 24) + "; centered across, the flames' roots 2 squares above the cell's bottom."),
    # ---- W Achooo!
    ("w_bolt", "W 阿嚏：喷嚏喷出去的一团火（朝目标飞，循环），4 帧",
     "view_projectiles `league_smolder_w_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 10",
     "一个喷嚏打出去的火团：一团不太规整、圆鼓鼓的橙黄色火（像打喷嚏喷出的一口火，前头最亮），周围一圈灰白色的烟和几颗小火星，后面拖一小截烟尾（参考 W_Mis_FireMask、W_FlameBits、W_PopLead、YoungDragon_W_FlameOutline）。**上下对称**，朝右飞。",
     f"{FR} and {SO}",
     f"a SNEEZED FIRE PUFF flying to the RIGHT, 4 frames, a seamless loop, {TB}: a lumpy round puff of orange and "
     "yellow fire 8 squares across, brightest (white-yellow) at its front, a ring of grey-white smoke puffs round it and "
     "a short smoke tail behind, 3 tiny embers popping in turn.",
     row(4, 18, 12) + "; the puff's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_hit", "W 打中（目标身上），4 帧", "view_effects `league_smolder_w_hit`（跟随，画在人物上面；左右对称）", "12",
     "喷嚏火团打中：目标身上一小团火和烟炸开。**左右对称**。",
     f"{FR} and {SO}",
     f"a FIRE-AND-SMOKE POP on a unit, 4 frames, {LR}: 1 a yellow flash 4 squares; 2 an orange puff 10 squares with grey "
     "smoke round it; 3 the puff opening, 4 embers at mirrored places; 4 fading smoke.",
     row(4, 14, 14) + "; centered in every cell."),
    ("w_boom", "W 打中英雄后的爆炸（地上，不跟随），6 帧",
     "view_effects `league_smolder_w_boom`（不跟随，画在人物上面；左右对称）；表 `league_smolder_big`", "50 × 28",
     "喷嚏打中英雄后炸开：一朵大的火焰爆炸，橙黄色的火团往上鼓起来，地上一圈岩浆一样的火浪往外推，外圈一圈灰烟，地上留焦痕（参考 W_AoE_PraxisFire、W_AoE_PraxisMagma_Dissolve、W_Cas_GroundScorch）。**左右对称**，约 50 格宽。",
     f"{FR} and {SO}",
     f"a BIG FIRE EXPLOSION on the ground, 6 frames, {LR}: a flat ellipse 50 squares wide and 16 tall on the ground; 1 a "
     "white-yellow flash 10 squares; 2 a round orange fireball 20 squares rising with a white core, a lava-like fire "
     "ring starting on the ground; 3 the fireball at its biggest (24 squares tall), the fire ring 36 squares wide; 4 the "
     "ring 50 squares wide with flame tongues at mirrored places, grey smoke puffs round its edge; 5 the fire sinking, a "
     "dark scorch ellipse; 6 smoke and the scorch fading.",
     row(6, 52, 30) + "; centered across, the ground ellipse's center 8 squares above the cell's bottom."),
    # ---- E Flap, Flap, Flap
    ("e_shot", "E 飞行时往下吐的小火球（朝目标飞，循环），3 帧",
     "view_projectiles `league_smolder_e_shot`（朝飞行方向转，画成朝右飞；上下对称）", "7 × 5",
     "飞行时连吐的小火球：比普攻的更小，白黄色的芯，橙色的火，一小截火尾（参考 E_Mis_Head_Te、E_GlowStar）。**上下对称**，朝右飞。",
     FR,
     f"a TINY FIREBALL flying to the RIGHT, 3 frames, a seamless loop, {TB}: a white-yellow core 2 squares across inside "
     "orange flame, a 3-square flame tail flickering.",
     row(3, 8, 6) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_hit", "E 小火球打中（目标身上），3 帧", "view_effects `league_smolder_e_hit`（跟随，画在人物上面；左右对称）", "8",
     "小火球打中：一小下火花。**左右对称**。",
     FR,
     f"a TINY FIRE SPARK on a unit, 3 frames, {LR}: 1 a white-yellow dot 3 squares; 2 an orange four-pointed spark 7 "
     "squares; 3 two fading embers.",
     row(3, 10, 10) + "; centered in every cell."),
    ("e_haste", "E 飞行时的加速（他身下，循环），4 帧",
     "view_buffs `league_smolder_e_haste`（跟随，画在人物下面；左右对称；飞行时一直放）", "30 × 8",
     "扑棱翅膀飞的时候，他身下地面上一圈被翅膀扇起来的风和火星：扁扁的一圈浅色气流（从斜上方看的椭圆），几道弯弯的风线，几颗橙色火星被吹起来（参考 SwirlLead、TinySparks）。**左右对称**。",
     f"{FR} and {SO}",
     f"a WIND RING of flapping wings on the ground, 4 frames, a seamless loop, {LR}: a flat ring 30 squares wide and 8 "
     "tall drawn as 4-6 short curved pale grey-white wind strokes at mirrored places turning a step each frame, 3-4 "
     "small orange embers blown up from it.",
     row(4, 32, 10) + "; centered in every cell."),
    # ---- R MMOOOMMMM!
    ("r_mom", "R 妈----！：妈妈从头顶飞过的影子（沿施法方向飞，循环），4 帧",
     "view_projectiles `league_smolder_r_mom`（朝飞行方向转，画成朝右飞；上下对称）；表 `league_smolder_big`", "48 × 40",
     "斯莫德的妈妈（一条巨大的成年龙）从高空飞过，地上看到的是她的**影子**：一个从正上方看下去的大龙剪影——头朝右，长脖子，两只巨大的翅膀往上下两边张开，后面一条长尾巴（参考 R_Mom_MisMask_v3 这张就是她的影子）。影子是深紫黑色，边缘一圈淡淡的橙红色火光（她嘴里的火映出来的），翅膀一帧一帧扇动。**上下对称**（两只翅膀是镜像），朝右飞。",
     f"{SH} and {FR}",
     f"the SHADOW OF A HUGE DRAGON flying to the RIGHT seen from straight above, 4 frames, a seamless loop of wing beats, "
     f"{TB}: her head and long neck pointing right, two enormous wings spread up and down (mirrored), a long tail "
     "trailing left, the whole silhouette dark shadow purple-black with a soft 1-square orange glow rim; 1 the wings "
     "spread widest (40 squares tip to tip); 2 the wings sweeping back; 3 the wings folded half (28 squares); 4 the "
     "wings coming forward again.",
     row(4, 50, 42) + "; the head 2 squares from the RIGHT edge, vertically centered, in every cell."),
    ("r_fire", "R：妈妈喷在地上的一整条火线（沿施法方向，约 0.75 秒），4 帧",
     "view_projectiles `league_smolder_r_fire`（朝施法方向转，画成朝右；上下对称；画在人物下面；一整条铺满格子）；表 `league_smolder_big`",
     "132 × 24",
     "妈妈喷下来的龙息在地上烧成一整条火带：**横着铺满整个格子**（从斯莫德脚下一直到 130 格外），带子中间一条最亮的白黄色火线（中线，伤害更高），两边橙红色的火焰往上蹿，边缘是熔岩一样的暗红和一点焦黑（参考 R_GroundTrail_Burn、R_FireNoise_2x2、R_GeneralFire_2x2、R_LavaNoise、R_AoE_PraxisMagma）。**上下对称**。四帧：点燃 → 烧到最旺 → 还在烧 → 熄灭成焦痕。",
     f"{FR} and {SO}",
     f"a LONG BAND OF DRAGON FIRE on the ground, 4 frames, {TB}: a horizontal band across the WHOLE cell width (132 "
     "squares) and 22 squares tall: a bright white-yellow center line 3 squares thick along its whole length, orange "
     "and red flames licking up and down from it (mirrored), lava-like dark red and a little soot at its two edges; 1 "
     "the fire catching, thinner (14 squares), brightest at the center line; 2 the fire at its fullest; 3 still burning, "
     "the flame tongues shifted; 4 burning out to a dark red scorched band with a few embers.",
     row(4, 132, 24, 8) + "; the band vertically centered, touching both the LEFT and the RIGHT edge, in every cell."),
    ("r_hit", "R 火线烧到（目标身上），4 帧", "view_effects `league_smolder_r_hit`（跟随，画在人物上面；左右对称）", "16",
     "被妈妈的火烧到：目标身上一团大火一炸。**左右对称**。",
     FR,
     f"a BIG FIRE HIT on a unit, 4 frames, {LR}: 1 a white-yellow flash 6 squares; 2 an orange-red burst 14 squares with "
     "a white core; 3 6 flame tongues at mirrored places, 16 squares; 4 fading embers.",
     row(4, 18, 18) + "; centered in every cell."),
    ("r_heal", "R 站在中线上回血（他身上），5 帧",
     "view_effects `league_smolder_r_heal`（跟随，画在人物上面；左右对称）", "16 × 22",
     "站在妈妈的火的中线上被治疗：他身上冒起一颗暖粉色的小爱心，周围几颗小亮点往上飘（参考 R_Heal_Heart、HealWisps）。**左右对称**，中间人形位置留空，爱心在头顶上方。",
     f"{HE} and {FR}",
     f"a WARM HEAL rising round a small figure, 5 frames, {LR}, the middle EMPTY (a clear upright area 8 squares wide and "
     "14 tall): 1 4 warm pink sparkles at mirrored places low at both sides; 2 the sparkles rising, a small pink heart 5 "
     "squares wide appearing above the empty area with a white core; 3 the heart 7 squares wide, brightest; 4 the heart "
     "rising 2 squares, sparkles at the top; 5 fading sparkles.",
     row(5, 18, 24) + "; centered across, the empty area's bottom on the cell's bottom row."),
    # ---- the passive, slows
    ("p_up", "被动 龙之研习：升段（10 / 25 / 40 层）时他身上的火焰闪光，6 帧",
     "view_effects `league_smolder_p_up`（跟随，画在人物上面；左右对称）", "32 × 34",
     "叠层升段：他身边一圈火焰旋转着往上冲，头顶一闪，两边飞出火星，最后散开（参考 Base_E_GlowStar、SwirlLead、Sparks_2x2、Q_Mis_Lvl3_ColorMask 的粉紫）。火从橙色变成一点粉紫色（他越叠越强）。**左右对称**，中间人形位置留空。",
     f"{FR} and {TR}",
     f"a POWER-UP FLARE round a small figure, 6 frames, {LR}, the middle EMPTY (a clear area 22 squares wide and 22 "
     "tall): 1 a ring of small orange flames on the ground round the empty area; 2 the flames rising at both sides 12 "
     "squares; 3 the flames 26 squares tall, pink-violet at their tips, meeting above the area; 4 a white-yellow "
     "four-pointed star flash 8 squares above the area, sparks flying out at mirrored places; 5 sparks falling; 6 a few "
     "fading embers.",
     row(6, 34, 36) + "; centered across, the empty area's bottom 2 squares above the cell's bottom."),
    ("slow", "减速（W、R 打中的人身上，循环），4 帧",
     "view_buffs `league_smolder_w_slow` / `league_smolder_r_slow`（跟随，画在人物下面；左右对称；减速期间一直放）", "18 × 6",
     "被减速：目标脚下一圈焦黑的烟灰和几颗暗红的余烬，烟一缕缕往上冒一点（参考 Smoke_4x4、R_SmokeTrail）。**左右对称**。",
     f"{SO} and {FR}",
     f"SMOULDERING SOOT at a unit's feet, 4 frames, a seamless loop, {LR}: a flat dark soot ring 18 squares wide and 6 "
     "tall, small grey smoke wisps rising 3 squares from it at mirrored places, 4 tiny dull red embers glowing in turn.",
     row(4, 20, 8) + "; centered in every cell."),
]

GROUPS = [
    ("a_* e_*", ["Smolder_Base_BA_Sparks_2x2", "Smolder_Base_BA_muzzle_fla", "Smolder_Base_BA_tar_alpha",
                 "Smolder_Base_MisLead_Mask", "YoungDragon_Q_Mis_Lvl1_Lead", "Smolder_Base_E_Mis_Head_Te",
                 "Smolder_Base_E_GlowStar", "Smolder_Base_SwirlLead"]),
    ("q_*", ["Smolder_Q_Mis_Lvl2_Lead", "Smolder_Q_Mis_Lvl3_Lead", "Smolder_Q_Mis_Lvl3_ColorMask", "Smolder_Q_AoE_WaveOut",
             "Smolder_Q_AoE_ScorchDecal", "Smolder_Q_AoETar", "Smolder_Q_Burn_ColorMask", "Smolder_Base_4x4Fire"]),
    ("w_*", ["Smolder_W_Mis_FireMask", "Smolder_Base_W_FlameBits", "Smolder_W_PopLead", "YoungDragon_W_FlameOutline",
             "Smolder_W_AoE_PraxisFire", "Smolder_W_AoE_PraxisMagma_Dissolve", "Smolder_W_Cas_GroundScorch",
             "Smolder_Smoke_4x4"]),
    ("r_* p_*", ["Smolder_R_Mom_MisMask_v3", "Smolder_R_GroundTrail_Burn", "Smolder_R_FireNoise_2x2",
                 "Smolder_R_GeneralFire_2x2", "Smolder_Base_R_LavaNoise_v", "Smolder_R_Heal_Heart",
                 "Smolder_Base_HealWisps", "Smolder_Base_R_SmokeTrail"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_bolt：从嘴里吐出"),
         ("skill", 3, "q_bolt：张大嘴喷出"),
         ("skill2", 4, "w_bolt：打喷嚏喷出"),
         ("skill2_e", 4, "e_shot：飞在空中往下吐"),
         ("ult", 3, "R：大喊，妈妈飞过来")]


def ref_name(nm):
    """A reference texture's file (the extraction's names; a prefix is enough)."""
    for f in sorted(os.listdir(REF)):
        if f.startswith(nm) and f.endswith(".png"):
            return os.path.join(REF, f)
    raise SystemExit(f"no reference texture {nm} in {REF}")


def ref_sheet(path):
    S, LW = 170, 90
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 14, 24, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(ref_name(nm)).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Smolder_", "").replace("Base_", "")[:24],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def hd_idle():
    import ppu_hd as P
    s = P.read_sheet(SHEET)
    f = s["hd_idle"][0][0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His idle as the game shows it (dense squares at 1 / SHOWN a game pixel) at 4x a game pixel on the arena colour,
    the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = hd_idle()
    Z, pad = 4, 6
    fw, fh = int(round(fig.shape[1] / SHOWN)), int(round(fig.shape[0] / SHOWN))
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    W = pad + fw + pad + kn.shape[1] + pad
    img = Image.new("RGBA", (max(W * Z, 760), (pad + max(fh, kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fh, kn.shape[0])
    img.alpha_composite(Image.fromarray(fig).resize((fw * Z, fh * Z), Image.NEAREST), (pad * Z, (base - fh) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fw) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fw + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"斯莫德 约 {fw}×{fh} 格（游戏里的大小），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（都是 4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return (fh, fw)


def shots_sheet(path):
    """The finished action frames as the game shows them, 4x a game pixel, his standing point as a cyan cross."""
    import ppu_hd as P
    s = P.read_sheet(SHEET)
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = s["hd_" + tag][k - 1][0]
        H, W = f.shape[:2]
        gw, gh = int(round(W / SHOWN * Z)), int(round(H / SHOWN * Z))
        im = Image.new("RGBA", (max(gw, 330), gh + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(f).resize((gw, gh), Image.NEAREST), ((max(gw, 330) - gw) // 2, 24))
        d = ImageDraw.Draw(im)
        cx = (max(gw, 330) - gw) // 2 + gw // 2
        cy = 24 + gh // 2 + int(round(11.5 * Z))     # the pivot is the frame's centre, the ground 11.5 game px under it
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
    a("# 炽炎雏龙 斯莫德：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/smolder_idle.png`：游戏里的 3/4 正面待机，四条腿站着的小龙）。他在游戏里约 {w} 格宽、{h} 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素）。")
    a("> - 大小对照 `design/smolder_size.png`：他在游戏里的样子放大 4 倍，红线是地面，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/smolder_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里斯莫德自己的特效贴图（火球、喷嚏的火、爆炸、妈妈的影子 `R_Mom_MisMask_v3`、地上的火带、回血的爱心），按用在我们哪张特效分好了行；只在本地用，不要提交。"
      "颜色照英雄联盟原版：**橙黄色的火、白热的火芯、他叠满层后火里的粉紫色、烟灰、妈妈深紫黑的影子**。")
    a("> - **特效要亮**：每团火都要有白黄色或最亮一档的芯，暗底上一眼能看见；烟和影子旁边要有亮一点的边或火光，不然在暗底上看不见。")
    a("> - **围着人的火、回血、升段闪光只画外圈，中间人形位置留空**。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`q_bolt`、`w_bolt`、`e_shot`、`r_mom` 和跟着施法方向转的 `q_t2`、`r_fire` 画成朝右，**上下对称**（往左时会上下翻）。"
      "其余所有画面（打中、身上、脚下、地上的爆炸）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `smolder_fx_<名字>.png`（`r_fire` 交 4 倍）和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `smolder_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「龙之研习」 | 吐小火球；技能打中英雄、Q 击杀叠层，10 / 25 / 40 层各升一段 | `a_bolt` · `a_hit` · `p_up` |")
    a("| 技能 1 = Q「超级灼热龙息」 | 大火球；一段在目标处爆炸，二段三颗回火弹往后飞散，三段附带灼烧 | `q_bolt` · `q_hit` · `q_t1` · `q_t2` · `q_t2_hit` · `q_burn` |")
    a("| 技能 2 = W「阿嚏！」+ E「扑棱，扑棱，扑棱！」 | 喷嚏火团（减速，打中英雄再爆炸）；E 起飞、加速、连吐 5 颗小火球 | `w_bolt` · `w_hit` · `w_boom` · `slow` · `e_shot` · `e_hit` · `e_haste` |")
    a("| 大招 = R「妈----！」 | 妈妈从头顶飞过，沿一条线喷火（减速），他站在中线上回血 | `r_mom` · `r_fire` · `r_hit` · `r_heal` · `slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、火花都没有黑描边，也不要用最深的颜色给火描一圈边**（烟、影子可以用自己最深一档收边）。")
    a("- **要亮**：每团火都有白黄色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火", FIRE), ("叠满层的粉紫火", TIER), ("烟灰", SOOT), ("妈妈的影子", SHADE), ("回血", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的爆炸、风圈、烟圈是从斜上方看的椭圆（宽是高的 2.5–3 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，"
      "Q 一段爆炸半径 22000，W 爆炸半径 25000，R 火线长 130000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `smolder_fx_{name}.png`：{title}\n")
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
        a(f"| `smolder_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_smolder_fx`（小的）和 `league_smolder_big`（q_t1、q_t2、w_boom、r_mom、r_fire），tag = 名字（build_smolder.py 的 views；"
      "`e_shotm` 绑到 `e_shot`、`w_xhit` 绑到 `w_hit`、`w_slow` / `r_slow` 绑到 `slow`）。")
    a("- 飞行的 `a_bolt`、`q_bolt`、`w_bolt`、`e_shot`、`r_mom` 朝飞行方向转；`q_t2`（从爆炸点往后的线，图从格子左边起）和 `r_fire`（LineRangeProjectile 画在整条线的中点：130000 长的线，图铺满格子）朝施法方向转；"
      "`q_t1`、`w_boom` 不跟随；`q_burn` 4 帧约 1 秒（灼烧每 60 tick 放一次）；`r_fire` 拼到 45 tick（build_smolder r_pic）。")
    a("- 用 `pixel_1x/` 切格（import_bard_fx 的做法），断言对称；必要时从 raw 重读（Codex 的读回可能清掉中间）；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="smolder_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "smolder_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/sm_work/fx/fx_ref_sm.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 6, 0), 6, 1)).save(os.path.join(out, "design", "smolder_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "smolder_size.png"))
    shots_sheet(os.path.join(out, "design", "smolder_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    shutil.copyfile(ref_name("Smolder_R_Mom_MisMask_v3"), os.path.join(out, "refs", "mom_shadow.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"smolder_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
