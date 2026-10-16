#!/usr/bin/env python3
"""Build reksai_fx_pack.zip: step 3 of Rek'Sai's sprite - Codex draws her effects (pack_urgot_fx.py's way).

    python work/rs/fx_ref_rs.py             # League's particle textures -> %TEMP%/rk_work/fxref (Riot's art, local only)
    python tools/art/pack_reksai_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name reksai_fx_redo_pack]

The pack (%TEMP%/rk_work/fx/reksai_fx_pack, zipped into --out, default dist/reksai_packs) holds PROMPTS.md (also written
to assets/source/reksai/PROMPTS_FX.md), design/reksai_idle.png (her designs A and B at 4x), design/reksai_size.png (the
1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter), design/reksai_shots.png (the
finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for Rek'Sai
grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_reksai.py: view_projectiles q2_shot; view_effects a_hit, q_hit,
e_hit, q2_cast, q2_hit, w_dig, w_burst, w_up, w_heal, r_dive, r_burst, r_hit; view_buffs p_full, q_buff, r_mark) and two
the add-on plays (addons/league_reksai: e_tunnel, a tunnel entrance, and e_break, one caving in). League's colours: the
Void violet-magenta with a white core, cyan-blue at the tips of Void Rush's claws, the earth she breaks dirt brown (her
design B's own browns); light gets no outline.
Red side: the flying picture (q2_shot) symmetric top to bottom (it turns with the flight), every picture on a unit, on
her, on the ground and every buff symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rk_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "reksai", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_reksai")
HD = os.path.join(ROOT, "assets", "source", "reksai", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VOID = "#FFFFFF, #F6D8FF, #E07CFF, #B03CF0, #6A1FB8, #2E0E5E"      # the Void: white core, lilac to deep violet
PINK = "#FFFFFF, #FFD0F4, #FF6FD8, #D62AA8, #7A1368"                # her fury: hot magenta (her mouth and crest)
BLUE = "#FFFFFF, #CFF8FF, #6FE0FF, #2F9CFF, #1B4FC8"                # Void Rush's claw tips, her carapace's cyan
DIRT = "#D9A57E, #B87A55, #7A4A38, #543027, #2E1A16"                # the earth she breaks (design B's browns)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, dust or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VO = f"a Void violet ramp ({VOID})"
PK = f"a fury magenta ramp ({PINK})"
BL = f"a cyan-blue ramp ({BLUE})"
DI = f"a dirt ramp ({DIRT})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
FIG = "a low wide beast 44 squares wide and 37 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack, Queen's Wrath, Furious Bite
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_reksai_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "爪子和牙咬中：一团紫色的虚空火花炸开，几道短短的爪痕光往外飞（参考 BA_tar_flash、BA_tar_gather、BA_tar_spark）。**左右对称**。约 10 格。",
     VO,
     f"a VOID CLAW HIT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 a violet burst 8 squares with a white core; 3 "
     "the burst 10 squares, 6 short lilac claw-streak sparks flying out at mirrored places; 4 fading violet motes.",
     row(4, 12, 12) + CENTER),
    ("q_hit", "Q 女王之怒：强化攻击溅射命中（目标身上），4 帧",
     "view_effects `league_reksai_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "女王之怒的强化攻击打中（周围的敌人也会被溅到）：一团更大的洋红到紫色的虚空爆炸，一圈紫色的冲击环，几道弧形的爪痕光（参考 Q_Swipe、Q_Hit_Spark、Q_Dark_Swirl、Q_electric）。**左右对称**。约 16 格。",
     f"{PK} and {VO}",
     f"a VOID SWIPE BURST on a unit, 4 frames, {LR}: 1 a white-magenta flash 5 squares; 2 a hot magenta burst 12 squares with a "
     "white core and two curved violet claw arcs at both sides (mirrored); 3 a violet shockwave ring 16 squares across, small "
     "lilac lightning crackles at mirrored places; 4 the ring fading, violet motes.",
     row(4, 18, 18) + CENTER),
    ("e_hit", "E 狂野之噬：满怒啃咬（目标身上，真实伤害），5 帧",
     "view_effects `league_reksai_e_hit`（跟随，画在人物上面；左右对称）", "20",
     "满怒时的狂野之噬：一张亮洋红色的大嘴从上下合拢咬住目标——上面一排、下面一排骨白色的尖牙（像她自己的獠牙）猛地合上，然后炸开一团白色和洋红色的光（真实伤害），几滴紫色的火花溅开（参考 E_Splash_tar、R_Hit_tar_impact）。**左右对称**。约 20 格。",
     f"{PK} and {VO}",
     f"a GIANT BITE closing on a unit, 5 frames, {LR}: 1 two rows of 5 bone-white fangs (each 2 squares wide, 4 tall), the upper "
     "row pointing down at the cell's top, the lower row pointing up at its bottom, hot magenta gums behind them; 2 the two rows "
     "halfway closed; 3 the fangs meeting in the middle with a white flash 8 squares; 4 a white and hot magenta burst 18 "
     "squares, violet sparks flying out at mirrored places; 5 fading magenta motes.",
     row(5, 20, 20) + CENTER),
    # ---- Prey Seeker
    ("q2_cast", "Q 猎物搜寻：她钻进土里打出冲击波（她身上，不跟随），4 帧",
     "view_effects `league_reksai_q2_cast`（她钻下去时画在她站的地方，不跟随，画在她下面；左右对称）", "36 × 16",
     "猎物搜寻出手：她半个身子钻进土里，地面拱起一圈碎土，中间一下紫色的闪光，几块土块往上飞（参考 Burrowed_Q_muzz_flash、Burrowed_Q_nova_flash、Burrowed_Q_Ground_Clump）。**左右对称**，只画地上的土和光（她自己的身体不画）。",
     f"{DI} and {VO}",
     f"a GROUND ERUPTION round a beast half sunk in the earth, 4 frames, {LR}: 1 a flat ring of dirt clods 30 squares wide and 6 "
     "tall bulging up from the ground, a violet flash 8 squares in the middle; 2 the ring 36 wide, 6 dirt chunks (2-3 squares) "
     "thrown up at mirrored places, the violet flash 12 squares; 3 the chunks at their highest, the flash fading to violet dust; "
     "4 the chunks falling, the dust thinning.",
     row(4, 38, 18) + "; centered across, the ground ring's middle 4 squares above the cell's bottom row."),
    ("q2_shot", "Q 猎物搜寻：飞出去的虚空冲击波（朝目标飞，循环），4 帧",
     "view_projectiles `league_reksai_q2_shot`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 9",
     "从土里打出的一团充满虚空能量的冲击波：一颗亮紫色的能量球（白芯）裹着几块旋转的土块和石子往右飞，后面拖一条紫色的光尾和尘土（参考 Q_Sphere_mis、Burrowed_Q_Splash_tar、Burrowed_Q_Ground_Clump）。**上下对称**。",
     f"{VO} and {DI}",
     f"a VOID-CHARGED BURST OF EARTH flying to the RIGHT, 4 frames, a seamless loop, {TB}: a bright violet energy orb 6 squares "
     "with a white core near the RIGHT end, 4 dirt clods (2 squares) circling it at mirrored places, turning a little each "
     "frame; a violet light trail 8 squares behind it, thinning, with a few dust motes.",
     row(4, 18, 10) + "; the orb's front 1 square from the RIGHT edge, vertically centered."),
    ("q2_hit", "Q 猎物搜寻：命中（目标身上），5 帧", "view_effects `league_reksai_q2_hit`（跟随，画在人物上面；左右对称）", "16",
     "冲击波打中：紫色的虚空爆炸里混着土块和尘土溅开（参考 Burrowed_Q_hit_tar、Burrowed_Q_tar_Explosion_nova、Burrowed_Q_tar_Crown_Dirt、Burrowed_Q_tar_dust）。**左右对称**。约 16 格。",
     f"{VO} and {DI}",
     f"an EARTH AND VOID BURST on a unit, 5 frames, {LR}: 1 a white-violet flash 5 squares; 2 a violet burst 12 squares with a "
     "white core; 3 a crown of dirt chunks 16 squares across thrown up and out at mirrored places, violet sparks; 4 brown dust "
     "puffs and falling clods; 5 fading dust.",
     row(5, 18, 18) + CENTER),
    # ---- Burrow / Unburrow
    ("w_dig", "W 遁地：钻进地里（她身上，不跟随），5 帧",
     "view_effects `league_reksai_w_dig`（她开始钻时画在她站的地方，不跟随，画在她下面；左右对称；大图表）", "50 × 22",
     "她一头钻进地里：地面炸开一圈碎土和石块往两边、往上飞，中间是一个冒着紫色微光的土坑（参考 W_ground_hole、I_Down_move_dust、I_Down_Crack_4x1、RekSai_base_I_Clumps）。**左右对称**，只画地上的土坑和飞起的土（她自己的身体不画）。",
     f"{DI} and {VO}",
     f"DIRT SPRAYING UP as a beast dives into the ground, 5 frames, {LR}: 1 the ground cracking: a flat dark hole 20 squares "
     "wide and 4 tall, crack lines out to both sides; 2 a fountain of dirt clods and stones thrown up and out to both sides, "
     "40 squares wide and 16 tall, a faint violet glow in the hole; 3 the spray at its widest, 50 squares, clods at their "
     "highest; 4 clods falling, brown dust puffs at both ends; 5 a low heap of loose earth 30 wide and 4 tall left, dust "
     "thinning.",
     row(5, 52, 24) + "; centered across, the ground (the hole) 3 squares above the cell's bottom row."),
    ("w_burst", "W 破土而出：从地下冲出（她身上，不跟随），6 帧",
     "view_effects `league_reksai_w_burst`（到达目标时画在她身上，不跟随，画在她下面；左右对称；大图表）", "44 × 36",
     "破土而出：地面猛地炸开，碎石和土块往上喷，夹着紫色的虚空能量和一圈紫色的冲击环在地上扩开（击飞范围约 34 格宽），中间一道往上冲的紫色光柱（参考 Burrowed_W_nova_flash、Burrowed_W_knock_up_Ring、Burrowed_W_Fin_debris、W_StoneShard、Reksai_Base_Burrowed_W_Plasma）。**左右对称**。",
     f"{DI} and {VO}",
     f"an EARTH ERUPTION, 6 frames, {LR}: 1 a white-violet flash 10 squares on the ground; 2 a violet light column 10 squares "
     "wide shooting up 30 squares, stone shards and dirt chunks bursting up at mirrored places, a flat violet ring 20 wide and "
     "6 tall on the ground; 3 the ring 34 wide and 10 tall with a bright lilac rim, shards at their highest; 4 the column "
     "breaking into violet plasma wisps, chunks falling; 5 the ring 44 wide and fading, dust puffs at both ends; 6 a few "
     "falling pebbles and violet motes.",
     row(6, 46, 38) + "; centered across, the ground ring's middle 5 squares above the cell's bottom row."),
    ("w_up", "W 破土而出：被击飞（目标身上），5 帧", "view_effects `league_reksai_w_up`（跟随，画在人物上面；左右对称）", "20 × 18",
     "被破土击飞的目标：脚下一圈紫色的光环，几块尖石从地下戳上来，目标周围飞着碎石（参考 W_knock_up_tar、W_knock_up_glow、W_StoneShard、Burrowed_W_Fin）。**左右对称**，中间身体位置留空（一个约 14 格宽、24 格高的人），要淡一点。",
     f"{VO} and {DI}",
     f"a KNOCK-UP UNDER a unit, 5 frames, {LR} (an upright figure 14 squares wide and 24 tall stands in the middle, not drawn): "
     "1 a violet ring 18 squares wide and 5 tall at the feet; 2 three stone spikes (3 squares wide, 6 tall) jutting up from "
     "the ring at both sides and the middle-back, pebbles flying up at mirrored places; 3 the spikes at full height, violet "
     "sparks; 4 the spikes crumbling, pebbles falling; 5 the ring fading.",
     row(5, 20, 26) + "; centered across, the ring's middle 2 squares above the cell's bottom row."),
    ("w_heal", "被动 艾克塞之怒：钻地时消耗怒气回血（她身上，跟随），6 帧",
     "view_effects `league_reksai_w_heal`（跟随，画在她身上；左右对称）", "50 × 42",
     "钻地时怒气化成血：她周围升起一圈洋红到紫色的光点，几道光往上飘，身体两侧一闪一闪的回复光（参考 Q_Core_Glow、I_Fin_Spark）。"
     f"**左右对称**，中间身体位置留空（{FIG}），光要淡一点、不要盖住她。",
     f"{PK} and {VO}",
     f"a FURY HEAL GLOW round a low wide beast, 6 frames, {LR} ({FIG}): 1 magenta light motes rising from the ground at both "
     "sides; 2 the motes 10 squares up, a faint magenta glow line along the ground 40 wide; 3 the motes at the beast's back "
     "height, small plus-shaped sparkles at mirrored places; 4 the brightest, the motes over the top; 5-6 the motes fading "
     "upward.",
     row(6, 52, 44) + "; centered across, the beast's feet on the cell's bottom row."),
    # ---- Void Rush
    ("r_dive", "R 虚空猛冲：钻进虚空（她身上，不跟随），6 帧",
     "view_effects `league_reksai_r_dive`（大招开始时画在她站的地方，不跟随，画在她下面；左右对称；大图表）", "40 × 18",
     "她钻进地底（不可选取）：地面裂开一个深紫色的虚空洞口，边缘一圈亮紫色的光，周围的尘土往洞里吸（参考 R_ground_burn、Burrowed_Q_tar_Suck_in、Burrowed_W_tremor_ring、R_End_Dust）。**左右对称**，只画地上的洞和吸进去的尘土。",
     f"{VO} and {DI}",
     f"a VOID HOLE OPENING in the ground, 6 frames, {LR}: 1 a violet crack 16 squares wide on the ground; 2 a dark violet "
     "ellipse hole 26 wide and 7 tall with a bright lilac rim; 3 the hole 36 wide and 9 tall, dust and pebbles being sucked "
     "toward it from both sides; 4 the hole at its widest, 40 wide, violet wisps swirling in; 5 the hole shrinking, the rim "
     "dimming; 6 a faint violet scorch ellipse 24 wide left.",
     row(6, 42, 20) + "; centered across, the hole's middle 6 squares above the cell's bottom row."),
    ("r_burst", "R 虚空猛冲：从虚空里扑出（她身上，不跟随），5 帧",
     "view_effects `league_reksai_r_burst`（扑到目标时画在她身上，不跟随；左右对称；大图表）", "36 × 32",
     "她从地底的虚空隧道里扑出来：一团紫色和青蓝色的隧道火花爆开，地上一圈紫色冲击环，碎土往两边飞（参考 R_Hit_tunnel_Spark、R_Basic_Impact_ring、R_End_Dust）。**左右对称**。",
     f"{VO} and {BL} and {DI}",
     f"a VOID TUNNEL EXIT BURST, 5 frames, {LR}: 1 a white flash 8 squares on the ground; 2 a violet and cyan spark burst 24 "
     "squares wide and 26 tall rising from the ground, a flat violet ring 20 wide on the ground; 3 the burst 32 tall, the ring "
     "36 wide with a lilac rim, dirt chunks thrown out at mirrored places; 4 sparks falling, the ring fading; 5 cyan and violet "
     "motes.",
     row(5, 38, 34) + "; centered across, the ring's middle 4 squares above the cell's bottom row."),
    ("r_hit", "R 虚空猛冲：扑击命中（目标身上），6 帧", "view_effects `league_reksai_r_hit`（跟随，画在人物上面；左右对称；大图表）", "30",
     "虚空猛冲的重击：目标身上交叉划过两组巨大的紫色爪痕（左上到右下、右上到左下各三道，成一个 X），爪痕尖端是青蓝色的亮光，中间炸开一团白色和紫色的光，外面一圈紫色冲击环（参考 R_Swipe、R_SwipeAdd、R_Hit_tar_impact、R_Basic_Impact_ring）。**左右对称**。约 30 格。",
     f"{VO} and {BL}",
     f"a GIANT CROSSED CLAW STRIKE on a unit, 6 frames, {LR}: 1 a white flash 6 squares; 2 three parallel violet claw slashes "
     "from the upper left to the lower right AND their mirror from the upper right to the lower left, forming an X 26 squares "
     "across, cyan-white light at the slashes' ends; 3 a white and violet burst 16 squares in the middle of the X, a violet "
     "shockwave ring 30 squares across; 4 the slashes fading to lilac, the ring breaking into violet shards at mirrored places; "
     "5 violet smoke wisps; 6 fading cyan and violet motes.",
     row(6, 32, 32) + CENTER),
    # ---- buffs
    ("p_full", "被动 艾克塞之怒：怒气满（她头顶，跟随，循环），4 帧",
     "view_buffs `league_reksai_f4`（怒气满的时候，跟随，画在她背上鳍冠的上方；左右对称）", "18 × 10",
     "怒气满了：她背上鳍冠上方一小簇洋红色的虚空火焰在跳，几颗紫色火星往上飘，提醒下一口是狂野之噬（参考 I_Fin_Spark、Q_Core_Glow）。**左右对称**，要小，只画这一小簇火。",
     f"{PK} and {VO}",
     f"a SMALL CROWN OF FURY FLAMES, 4 frames, a seamless loop, {LR}: three hot magenta flame tongues (the middle 7 squares "
     "tall, the side ones 5) with white-pink cores, flickering in height frame by frame; 3-4 violet sparks rising above them at "
     "mirrored places, taking turns.",
     row(4, 18, 12) + "; centered across, the flames' base on the cell's bottom row."),
    ("q_buff", "Q 女王之怒：强化攻击期间（她脚下，跟随，循环），4 帧",
     "view_buffs `league_reksai_q_as`（跟随，画在她下面；左右对称）", "48 × 12",
     "女王之怒的 3 秒里：她脚下一圈洋红色的虚空旋风（扁椭圆），几道弧形的光在圈上转（参考 Q_ground_wind、Q_Circle_normal、Q_Dark_Swirl）。**左右对称**，只画地上的圈，中间身体位置不画东西，要淡一点。",
     f"{PK} and {VO}",
     f"a FAINT VOID WHIRL on the ground round a figure, 4 frames, a seamless loop, {LR}: a flat magenta ellipse ring 46 "
     "squares wide and 10 tall, 1-2 squares thick, half transparent-looking (use the darker shades), 4 short curved violet arcs "
     "on it at mirrored places moving round frame by frame, a few lilac motes.",
     row(4, 48, 12) + "; centered."),
    ("r_mark", "R：被标记为猎物（目标头顶，跟随，循环），4 帧",
     "view_buffs `league_reksai_r_mark`（跟随，画在人物头顶；左右对称）", "12 × 12",
     "被雷克塞伤到的英雄头顶出现猎物标记：英雄联盟里是三道并排的紫色爪痕（参考 R_Mark、R_Mark_BG）——这里画成**左右对称**的三道竖着的爪痕，外面一圈淡紫色的光，在一明一暗地呼吸。要小。",
     VO,
     f"a SMALL PREY MARK, 4 frames, a seamless loop, {LR}: three vertical violet claw scratches side by side (the middle one 9 "
     "squares tall, the side ones 7, curving slightly outward and tapering at both ends) with white-lilac cores, a faint violet "
     "halo round them; the brightness pulsing (frames 2-3 brightest).",
     row(4, 12, 12) + CENTER),
    # ---- the add-on's tunnels
    ("e_tunnel", "附加包 挖掘隧道：隧道入口（地上，循环），4 帧",
     "view_effects `league_reksai_e_tunnel`（附加包反复播放在入口处，不跟随，画在人物下面；左右对称）", "24 × 10",
     "隧道的入口：地上一个圆圆的土坑，边上一圈拱起的碎土，坑里深紫色、透出一点紫色微光在呼吸（参考 E_Tunnel_Enable_purple、Burrowed_E_Tunnel_ground、E_Tunnel_Crack）。**左右对称**，扁椭圆。",
     f"{DI} and {VO}",
     f"a TUNNEL ENTRANCE on the ground, 4 frames, a seamless loop, {LR}: a flat ellipse hole 18 squares wide and 6 tall, dark "
     "violet inside with a faint violet glow at its bottom, a rim of heaped dirt clods round it 24 wide and 9 tall; the glow's "
     "brightness pulsing (frames 2-3 brightest), 1-2 violet motes rising from it.",
     row(4, 26, 12) + "; centered."),
    ("e_break", "附加包 挖掘隧道：隧道被踩塌（地上），5 帧",
     "view_effects `league_reksai_e_break`（附加包在入口被毁时播放，不跟随；左右对称）", "26 × 16",
     "敌人站在入口上把隧道踩塌：土坑往里塌，一团尘土和紫色的烟冒起来，然后只剩一小堆平平的土（参考 E_Tunnel_Explosion、E_Tunnel_Smoke）。**左右对称**。",
     f"{DI} and {VO}",
     f"a TUNNEL CAVING IN, 5 frames, {LR}: 1 the entrance (a dirt-rimmed hole 24 wide and 9 tall) cracking; 2 the rim falling "
     "in, a brown dust puff 16 squares rising with violet smoke in it; 3 the dust 26 wide and 14 tall, violet smoke wisps; 4 "
     "the dust thinning; 5 a flat patch of loose earth 20 wide and 3 tall.",
     row(5, 28, 18) + "; centered across, the ground 3 squares above the cell's bottom row."),
]
BIG_FX = ("w_dig", "w_burst", "r_dive", "r_burst", "r_hit")
GROUPS = [
    ("a_hit", ["RekSai_Base_BA_tar_flash", "RekSai_Base_BA_tar_gather", "RekSai_Base_BA_tar_impact", "RekSai_Base_BA_tar_spark"]),
    ("q_hit q_buff", ["RekSai_Base_Q_Swipe", "RekSai_Base_Q_Hit_Spark", "RekSai_Base_Q_Dark_Swirl", "Reksai_Base_Q_electric",
                      "RekSai_Base_Q_ground_wind", "RekSai_Base_Q_Circle_normal"]),
    ("e_hit p_full w_heal", ["RekSai_Base_E_Splash_tar", "RekSai_Base_R_Hit_tar_impact", "RekSai_Base_I_Fin_Spark",
                             "RekSai_Base_Q_Core_Glow"]),
    ("q2_cast q2_shot q2_hit", ["RekSai_Base_Burrowed_Q_muzz_flash", "RekSai_Base_Q_Sphere_mis",
                                "RekSai_Base_Burrowed_Q_Ground_Clump", "RekSai_Base_Burrowed_Q_hit_tar",
                                "RekSai_Base_Burrowed_Q_tar_Explosion_nova", "RekSai_Base_Burrowed_Q_tar_Crown_Dirt"]),
    ("w_dig", ["RekSai_Base_W_ground_hole", "RekSai_Base_I_Down_move_dust", "RekSai_Base_I_Down_Crack_4x1",
               "RekSai_base_I_Clumps"]),
    ("w_burst w_up", ["RekSai_Base_Burrowed_W_nova_flash", "RekSai_Base_Burrowed_W_knock_up_Ring",
                      "RekSai_Base_Burrowed_W_Fin_debris", "RekSai_Base_W_StoneShard", "Reksai_Base_Burrowed_W_Plasma",
                      "RekSai_Base_W_knock_up_tar"]),
    ("r_dive r_burst", ["RekSai_Base_R_ground_burn", "RekSai_Base_Burrowed_Q_tar_Suck_in", "RekSai_Base_R_Hit_tunnel_Spark",
                        "RekSai_Base_R_Basic_Impact_ring", "RekSai_Base_R_End_Dust"]),
    ("r_hit r_mark", ["RekSai_Base_R_Swipe", "RekSai_Base_R_SwipeAdd", "RekSai_Base_R_Mark", "RekSai_Base_R_Mark_BG"]),
    ("e_tunnel e_break", ["RekSai_Base_E_Tunnel_Enable_purple", "RekSai_Base_Burrowed_E_Tunnel_ground",
                          "RekSai_Base_E_Tunnel_Crack", "RekSai_Base_E_Tunnel_Explosion", "RekSai_Base_E_Tunnel_Smoke"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_hit：咬中"), ("skill", 3, "q_hit：女王之怒扑下"), ("skill_q2", 3, "q2_cast / q2_shot：钻进土里打出冲击波"),
         ("bite", 3, "e_hit：满怒啃咬"), ("skill2", 2, "w_dig：钻进地里"), ("skill2_up", 2, "w_burst：破土而出"),
         ("ult", 2, "r_dive：钻进虚空"), ("ult_hit", 3, "r_burst / r_hit：扑击")]


def ref_sheet(path):
    S, LW = 180, 170
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
            d.text((LW + c * S + 4, y + 2), nm.replace("RekSai_Base_", "").replace("Reksai_Base_", "")[:26],
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
    d.text((8, 36), f"雷克塞 {figs[0].shape[1]}×{figs[0].shape[0]} 格（连鳍冠和尾巴），原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is her pivot, FEET rows over the ground
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


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 虚空遁地兽 雷克塞：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/reksai_idle.png`：3/4 正面朝右，四肢着地的虚空掘地巨兽，"
      f"靛蓝甲壳带青色高光，背上洋红到蓝的镰刀鳍冠，没有眼睛的头盔、洋红的嘴和骨白獠牙，长尾巴；右边是她钻在地下的样子 B）。她在游戏里是**高清**的"
      f"（每个游戏格子里约 1.58×1.58 个细像素），连鳍冠和尾巴 {h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/reksai_size.png`：她的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/reksai_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。**钻地时的土堆已经画进她自己的帧里了**（她沉进地里时身上盖着一堆碎土），特效只画额外飞起的土、光和冲击。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里雷克塞自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**虚空能量是紫色到洋红（白芯）**，**她的怒气是亮洋红**，**虚空猛冲的爪痕尖端是青蓝色**，**钻地的土是褐色**（和她钻地造型 B 里的土一样）。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住人。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `q2_shot` 画成朝右，**上下对称**（往左时会上下翻）。其余所有画面（打中、身上、脚下、地上、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `reksai_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `reksai_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「艾克塞之怒」 | 爪咬；攻击和技能命中攒怒气，满怒时下一口是狂野之噬（真实伤害）；钻地时消耗怒气回血 | `a_hit` · `e_hit` · `p_full` · `w_heal` |")
    a("| 技能 1 = Q「女王之怒 / 猎物搜寻」 | 近身：接下来 3 次攻击溅射周围；远处：钻进土里打出一道虚空冲击波 | `q_hit` · `q_buff` · `q2_cast` · `q2_shot` · `q2_hit` |")
    a("| 技能 2 = W「遁地 / 破土而出」 | 钻进地里从地下冲到目标脚下，破土击飞 | `w_dig` · `w_burst` · `w_up` |")
    a("| 大招「虚空猛冲」 | 打到过的英雄被标记；钻进虚空不可选取，再扑出来按最大生命重击 | `r_mark` · `r_dive` · `r_burst` · `r_hit` |")
    a("| 附加包「挖掘隧道」 | 钻地留下隧道入口，敌人站上去会踩塌 | `e_tunnel` · `e_break` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（土块、石块和獠牙例外：实心的东西可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空紫", VOID), ("怒气洋红", PINK), ("青蓝（爪痕尖、甲壳）", BLUE), ("泥土（和她的造型 B 一样）", DIRT)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 26000，"
      "女王之怒溅射半径 16000，猎物搜寻 64000 长、半宽 4500，破土击飞半径 17000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `reksai_fx_{name}.png`：{title}\n")
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
        a(f"| `reksai_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_reksai_fx`（小的）和 `league_reksai_big`（{'、'.join(BIG_FX)}），tag = 名字（build_reksai.py 的 views；"
      "p_full 绑在 buff `league_reksai_f4`，q_buff 绑在 `league_reksai_q_as`）。")
    a("- `q2_shot` 是投射物，画面朝方向转；`q2_cast`、`w_dig`、`w_burst`、`r_dive`、`r_burst` 不跟随（她身上的晚播画面，红色方规则）；`w_dig`、`w_burst`、`r_dive`、`q2_cast`、`q_buff`、`e_tunnel` 画在人物下面（z -1）；"
      "`p_full` 放在她鳍冠上方（HEAD 点），`r_mark` 放在目标头顶。")
    a("- `e_tunnel` / `e_break` 只有附加包播放（native play_view_effect），主包里也要有 view 条目。")
    a("- 用 `pixel_1x/` 切格（import_urgot_fx / import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="reksai_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "reksai_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/rs/fx_ref_rs.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    dA = np.asarray(Image.open(lp(os.path.join(HD, "design_A.png"))).convert("RGBA"))
    dB = np.asarray(Image.open(lp(os.path.join(HD, "design_B.png"))).convert("RGBA"))
    both = np.zeros((dA.shape[0], dA.shape[1] + 6 + dB.shape[1], 4), np.uint8)
    both[:, :dA.shape[1]] = dA
    both[dA.shape[0] - dB.shape[0]:, dA.shape[1] + 6:] = dB
    Image.fromarray(np.repeat(np.repeat(both, 4, 0), 4, 1)).save(os.path.join(out, "design", "reksai_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "reksai_size.png"))
    shots_sheet(os.path.join(out, "design", "reksai_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"reksai_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
