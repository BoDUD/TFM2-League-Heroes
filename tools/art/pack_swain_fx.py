#!/usr/bin/env python3
"""Build swain_fx_pack.zip: step 3 of Swain's sprite - Codex draws his effects (pack_reksai_fx.py's way).

    python work/swa/fx_ref_swa.py            # League's particle textures -> %TEMP%/swa_work/fxref (Riot's art, local only)
    python tools/art/pack_swain_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name swain_fx_redo_pack]

The pack (%TEMP%/swa_work/fx/swain_fx_pack, zipped into --out, default dist/swain_packs) holds PROMPTS.md (also written to
assets/source/swain/PROMPTS_FX.md), design/swain_idle.png (his two forms at 4x: the demon with the wings' aura),
design/swain_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/swain_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Swain grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_swain.py: view_projectiles a_bolt, q_bolts, e_out, e_back;
view_effects a_hit, q_hit, e_hit, e_pull, w_eye, w_hit, p_frag, r_cast, r_drain, r_flare, r_fl_hit). The wings' aura
(view_buffs r_on -> r_wings) is not Codex's: tools/art/rig_swain.py draws it from B-1's own wings. League's colours: the
demon's crimson soulfire with a white core and hot magenta at the claws, the ravens and the demon's shadow black-violet;
light gets no outline.
Red side: the flying pictures (a_bolt, q_bolts, e_out, e_back) symmetric top to bottom (they turn with the flight), every
picture on a unit, on him and on the ground symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "swa_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "swain", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_swain")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


CRIM = "#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614"      # the demon's soulfire: white core to deep crimson
MAG = "#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52"                # the demon claw's hot magenta
SHADE = "#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A"              # ravens, smoke, the demon's shadow (black-violet)
VIOL = "#FFFFFF, #E2D4FF, #A88BFF, #6A4BE0, #3A2290"               # Demonflare's violet-blue core (R_Nova_Mis_Core)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
CR = f"a crimson soulfire ramp ({CRIM})"
MG = f"a hot magenta ramp ({MAG})"
SH = f"a black-violet shadow ramp ({SHADE})"
VI = f"a violet-blue ramp ({VIOL})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
FIG = "an upright figure 26 squares wide and 40 tall stands in the middle, not drawn"
UNIT = "an upright figure 14 squares wide and 24 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack (Ravenous Flock's raven bolt from the demon hand)
    ("a_bolt", "普攻：恶魔手射出的乌鸦弹（飞行，循环），4 帧", "view_projectiles `league_swain_a_bolt`（朝目标飞，画面随方向转；上下对称）",
     "10 × 7",
     "从恶魔手掌心射出的一只**小乌鸦**：从上往下看的黑紫色乌鸦，两只翅膀**上下对称**地张开，胸口一团红白色的魂火，身后拖一小段深红尾迹，"
     "翅膀一扇一扇（参考 BA_Front、BA_mis_trail、BA_leadingedge_add）。**朝右飞，上下对称**。约 10 格长。",
     f"{SH} and {CR}",
     f"a small RAVEN OF SOULFIRE flying to the RIGHT, 4 frames, a seamless loop, {TB}: a black-violet raven seen from above, "
     "its head (2 squares) pointing right, its two wings spread symmetrically up and down (each 3 squares long, the wing "
     "tips beating: open, half, closed, half), a crimson-white glowing core at its chest (2 squares, white centre), a "
     "short crimson trail of 3 fading squares behind its tail.",
     row(4, 12, 9) + "; the raven's beak 1 square from the RIGHT edge, vertically centered."),
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_swain_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "乌鸦弹打中：一团深红的魂火炸开，四片黑羽毛往外飞散（参考 BA_Flash_sharp、BA_Spark_cas）。**左右对称**。约 10 格。",
     f"{CR} and {SH}",
     f"a SOULFIRE HIT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 a crimson burst 8 squares with a white core; "
     "3 the burst 10 squares, 4 small black-violet feathers (2 squares each) flying out at mirrored places; 4 fading "
     "crimson motes and two falling feathers.",
     row(4, 12, 12) + CENTER),
    # ---- Q Death's Hand
    ("q_bolts", "Q 解脱之触：五道恶魔之力扇形飞出（飞行，播一次），5 帧",
     "view_projectiles `league_swain_q_bolts`（朝目标飞，画面随方向转；上下对称；不循环）", "20 × 20",
     "五道**深红到洋红的恶魔闪电**一起朝前飞、越飞越散开成扇形：第 1 帧五道挤在一起，到第 5 帧上下张开约 18 格；每道是一条带白芯的闪电短箭"
     "（参考 Q_lightning2、Q_lightning3、Q_energyBall）。**朝右飞，上下对称**（中间一道，上下各两道对称）。",
     f"{CR} and {MG}",
     f"FIVE DEMONIC LIGHTNING BOLTS flying to the RIGHT and fanning out, 5 frames, played once, {TB}: five short bolts "
     "pointing right (each a jagged crimson-magenta lightning streak 6 squares long with a white core, a bright head at "
     "its right end), one in the middle and two above and two below it, symmetric: frame 1 their heads 2 squares apart "
     "(the five bunched, 9 squares tall in all), 2 four squares apart, 3 six, 4 eight, 5 nine squares apart (the fan 19 "
     "squares tall), the bolts a little longer each frame.",
     row(5, 20, 20) + "; the bolts' heads 1 square from the RIGHT edge, vertically centered."),
    ("q_hit", "Q 命中（目标身上），4 帧", "view_effects `league_swain_q_hit`（跟随，画在人物上面；左右对称）", "12",
     "恶魔闪电打中：一团洋红深红的闪电炸开，几道细闪电往外窜（参考 Q_hit_flash、Q_hit_flash_large、Q_Crack）。**左右对称**。约 12 格。",
     f"{CR} and {MG}",
     f"a DEMONIC LIGHTNING HIT on a unit, 4 frames, {LR}: 1 a white-magenta flash 4 squares; 2 a crimson burst 10 squares "
     "with a white core and 4 short magenta lightning forks at mirrored places; 3 the burst 12 squares, the forks longer; "
     "4 fading crimson sparks.",
     row(4, 14, 14) + CENTER),
    # ---- E Nevermove
    ("e_out", "E 永不复行：飞出去的恶魔之手（飞行，循环），4 帧",
     "view_projectiles `league_swain_e_out`（朝目标飞，画面随方向转；上下对称）", "16 × 14",
     "一只**张开的恶魔手**朝前飞：深红到洋红的魂火手掌，五根长爪**上下对称**地张开（中间一根朝前，上下各两根），身后拖一团黑紫色的烟"
     "（参考 E_birdshape、E_birdshape2_tip、E_wisps）。**朝右飞，上下对称**。",
     f"{MG} and {CR} and {SH}",
     f"an OPEN DEMON HAND flying to the RIGHT, 4 frames, a seamless loop, {TB}: a spectral palm of crimson-magenta soulfire "
     "(6 squares, a white core) with five long curved claws reaching forward and spreading symmetrically up and down (the "
     "middle claw 6 squares long pointing right, two above and two below curving outward, each 4-5 squares, bright "
     "magenta tips), a trail of black-violet smoke and crimson wisps 6 squares long behind the palm, flickering.",
     row(4, 18, 16) + "; the middle claw's tip 1 square from the RIGHT edge, vertically centered."),
    ("e_back", "E：恶魔之手收回来（飞行，循环），4 帧",
     "view_projectiles `league_swain_e_back`（飞回斯维因，画面随方向转；上下对称）", "16 × 14",
     "同一只恶魔手**攥着往回飞**：爪子收拢成一个钩爪（上下对称），身后的烟更长更乱（参考 E_return_mis_mult、E_turning_mis_flash）。"
     "画成**朝右飞、上下对称**（游戏会把它转向飞回的方向）。",
     f"{MG} and {CR} and {SH}",
     f"the DEMON HAND CLOSING as it flies back, drawn flying to the RIGHT, 4 frames, a seamless loop, {TB}: the same "
     "crimson-magenta palm (6 squares, white core) with its five claws curled forward into a hooked grasp (symmetric up "
     "and down, the claw tips meeting in front of the palm), a longer trail of black-violet smoke and crimson wisps 8 "
     "squares behind it, flickering.",
     row(4, 18, 16) + "; the claws' front 1 square from the RIGHT edge, vertically centered."),
    ("e_hit", "E 命中：被禁锢（目标身上，1.5 秒），6 帧", "view_effects `league_swain_e_hit`（跟随，画在人物脚下到腰；左右对称）",
     "22 × 26",
     f"从地面伸出几只**深红的恶魔爪**抓住目标的腿，黑紫色的烟缠在脚边，最后三帧保持抓住的样子（参考 E_hit_ground、E_Tar_BlastShapes、"
     f"E_Deathshards）。**左右对称**，中间身体位置留空（{UNIT}）。",
     f"{CR} and {MG} and {SH}",
     f"DEMON CLAWS ROOTING a unit, 6 frames, {LR} ({UNIT}): 1 a crimson crack ring on the ground round the feet (an "
     "ellipse 16 squares wide, 4 tall); 2 four crimson-magenta claws rising out of it at mirrored places beside the legs "
     "(each 5 squares tall); 3 the claws 9 squares tall curling in over the shins, black-violet smoke at the feet; 4-6 the "
     "claws closed round the legs (up to knee height), flickering softly, the smoke curling (frames 4-6 nearly the same: "
     "the hold).",
     row(6, 24, 28) + "; centered across, the ground ring's middle 3 squares above the cell's bottom row."),
    ("e_pull", "E 拉拽（目标身上），4 帧", "view_effects `league_swain_e_pull`（跟随，画在人物上面；左右对称）", "14",
     "目标被拽向斯维因时：一团深红的魂火炸开，几片黑羽毛和魂火往两边甩（参考 E_DemonDrainSwoosh、E_Explode_Shards）。**左右对称**。约 14 格。",
     f"{CR} and {SH}",
     f"a SOUL TORN OUT of a unit, 4 frames, {LR}: 1 a white-crimson flash 5 squares at its chest; 2 a crimson burst 12 "
     "squares, a small crimson soul shard (3 squares, white core) at the top; 3 the burst ring 14 squares, 6 black-violet "
     "feathers flung out at mirrored places, the shard higher; 4 fading crimson wisps.",
     row(4, 16, 16) + CENTER),
    # ---- W Vision of Empire (fired by the passive)
    ("w_eye", "W 帝国视界：地上睁开的恶魔之眼（地上，不跟随，约 1.6 秒），8 帧", "view_effects `league_swain_w_eye`（不跟随，画在人物下面；左右对称；大图表）",
     "60 × 36",
     "地上睁开一只**巨大的恶魔之眼**（从斜上方看，是个扁的椭圆）：先是一道深红裂缝，眼皮张开，露出黑紫色的眼白圈和发光的深红虹膜、"
     "白色竖瞳，一闪一闪地盯着，最后一帧收缩后爆成一团深红的光柱（参考 W_Eye_Alpha_V02、W_Eye_Alpha_V03、W_Explode_Iris、"
     "W_Ground_Circle_Alpha_V01、W_portal_ring_colors、W_Pulses_V02）。**左右对称**。约 60 格宽。",
     f"{CR} and {MG} and {SH}",
     f"a GIANT DEMON EYE OPENING ON THE GROUND seen from above at an angle, 8 frames, {LR}: 1 a thin crimson crack 30 "
     "squares wide on the ground; 2 the crack opening into an almond-shaped eye 40 squares wide and 8 tall, dark lids "
     "with a crimson rim; 3 the eye 56 squares wide and 16 tall: a black-violet sclera ring, a glowing crimson iris (an "
     "ellipse 20 wide and 10 tall) with a white vertical slit pupil (2 squares wide, 8 tall), a faint crimson glow ring "
     "round the whole eye; 4 the same, the iris brighter, two thin magenta pulse rings round it; 5 the same as 3; 6 the "
     "same as 4; 7 the eye narrowing to a slit, the iris a bright white-crimson line; 8 a burst: a white-crimson flash "
     "ellipse 50 squares wide and 14 tall on the ground with a light column 12 squares wide and 20 tall rising from its "
     "middle.",
     row(8, 64, 40) + "; centered across, the eye's middle 10 squares above the cell's bottom row."),
    ("w_hit", "W 命中（目标身上），4 帧", "view_effects `league_swain_w_hit`（跟随，画在人物上面；左右对称）", "12",
     "恶魔之眼爆炸打中：一团深红的光炸开，一圈洋红的波纹往外扩（减速），参考 W_Flash_tar、W_Spark_cas。**左右对称**。约 12 格。",
     f"{CR} and {MG}",
     f"an EYE BLAST HIT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a crimson burst 10 squares with a white "
     "core; 3 a magenta ripple ring 12 squares round it, crimson sparks; 4 the ring fading.",
     row(4, 14, 14) + CENTER),
    # ---- the passive's fragment
    ("p_frag", "被动 狂食鸦群：乌鸦叼来魂屑（他身上，跟随），6 帧", "view_effects `league_swain_p_frag`（跟随，画在人物上面；左右对称）",
     "40 × 40",
     f"两只**小黑乌鸦**从左右两边飞进来，各叼着一团深红的魂屑，飞到他胸口时魂屑合成一团红光被吸进身体，乌鸦往上飞走（参考 W_Raven_TX_CM、"
     f"Z_SoulWispsAlpha、R_Feathers）。**左右对称**，中间身体位置留空（{FIG}）。",
     f"{SH} and {CR}",
     f"TWO RAVENS BRINGING A SOUL FRAGMENT to a figure, 6 frames, {LR} ({FIG}): 1 two small black-violet ravens (5 squares "
     "each, wings spread) at the left and right edges at chest height, each carrying a crimson soul spark (2 squares, "
     "white core); 2 the ravens halfway in; 3 the ravens at the figure's sides, the sparks touching its chest; 4 the "
     "sparks merged into one crimson glow 6 squares at the chest middle, the ravens rising; 5 the glow sinking into the "
     "chest (smaller), the ravens higher at the top corners; 6 a few crimson motes, the ravens leaving the cell.",
     row(6, 44, 44) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- R Demonic Ascension / Demonflare
    ("r_cast", "R 恶魔升华：变身爆发（他身上，不跟随），6 帧", "view_effects `league_swain_r_cast`（他身上播一次，不跟随；左右对称；大图表）",
     "56 × 52",
     f"他化身恶魔的一瞬间：一圈深红的魂火和黑羽毛从他身上往外爆开，地上裂出一圈红色裂纹，几道深红闪电往上窜（参考 R_Cast_Dust_v03、"
     f"R_Cas_Symbol_V01、R_Lightning、R_Shockwave、R_Feathers）。**左右对称**，中间身体位置留空（{FIG}）。",
     f"{CR} and {MG} and {SH}",
     f"a DEMONIC TRANSFORMATION BURST round a figure, 6 frames, {LR} ({FIG}): 1 a crimson flash ring on the ground round "
     "the feet (an ellipse 20 wide, 5 tall); 2 black-violet smoke and crimson soulfire bursting out on both sides of the "
     "figure up to its shoulders, a ring of red ground cracks 36 squares wide; 3 the burst at its widest: soulfire flames "
     "16 squares tall on both sides, 6 crimson-magenta lightning bolts rising at mirrored places above the shoulders, 10 "
     "black-violet feathers flying out; 4 the flames lower, the feathers further out; 5 smoke and falling feathers; 6 "
     "fading cracks and embers.",
     row(6, 56, 52) + "; centered across, the figure's feet (the ground ring's middle) 4 squares above the cell's bottom row."),
    ("r_drain", "R 吸取（被吸的目标身上，跟随），4 帧", "view_effects `league_swain_r_drain`（跟随，画在人物上面；左右对称）", "14 × 20",
     "被恶魔吸取：目标身上冒出几缕深红的魂魄往上飘、打着旋（参考 R_DemonDrainSwoosh、R_drainRing、R_Absorb_Scroll_Alpha）。**左右对称**。",
     f"{CR} and {SH}",
     f"SOUL WISPS DRAWN OUT of a unit, 4 frames, {LR}: crimson soul wisps (each a curl 2 squares wide and 5 tall, white "
     "core) rising from the unit's chest at mirrored places, spiralling up and fading at the top; a faint black-violet "
     "smoke ring round the chest; each frame the wisps a little higher (a loop that also reads played once).",
     row(4, 16, 22) + "; centered across, the wisps' start 8 squares above the cell's bottom row."),
    ("r_flare", "R 恶魔耀光：魂火新星（他身上，不跟随），6 帧", "view_effects `league_swain_r_flare`（他身上播一次，不跟随；左右对称；大图表）",
     "120 × 52",
     f"举起恶魔爪放出的**魂火新星**：从他身上炸开一圈深红的火环（内缘蓝紫色，和英雄联盟的恶魔耀光一样），在地上（从斜上方看的扁椭圆）越扩越大，环上跳着洋红的闪电，"
     f"最后剩一圈余烬（参考 R_Nova_Mis_Core、R_Nova_Mis_Energy、R_Nova_Mis_Front、R_Nova_Mis_Dark_Background、R_Ring_Shockwave）。"
     f"**左右对称**，环的中间留空（{FIG}）。",
     f"{CR} and {VI} and {MG}",
     f"a NOVA OF SOULFIRE spreading on the ground round a figure, 6 frames, {LR} ({FIG}): 1 a white and violet-blue "
     "flash 12 squares at the figure's chest; 2 a ring of crimson fire on the ground (an ellipse 40 wide, 12 tall, flames 4 "
     "squares tall) with a violet-blue inner edge; 3 the ring 72 wide and 22 tall, crimson flames with a violet-blue inner "
     "glow, magenta lightning crackling on it at mirrored places; 4 the ring 100 wide and 30 tall, the flames 6 squares "
     "tall; 5 the ring 116 wide and 36 tall, thinner; 6 a fading ring of crimson and violet embers.",
     row(6, 124, 56) + "; centered across, the ring's middle (the figure's feet) 18 squares above the cell's bottom row."),
    ("r_fl_hit", "R 恶魔耀光命中（目标身上），4 帧", "view_effects `league_swain_r_fl_hit`（跟随，画在人物上面；左右对称）", "14",
     "被魂火新星打中：一团深红的火焰炸开，暗紫色的火星往外飞（减速），参考 R_tar_Flash、R_Tar_Impact。**左右对称**。约 14 格。",
     f"{CR} and {SH}",
     f"a SOULFIRE BURN on a unit, 4 frames, {LR}: 1 a white-crimson flash 5 squares; 2 crimson flames 12 squares rising "
     "round the unit's middle with a white core; 3 the flames 14 squares, dark violet sparks flying out at mirrored "
     "places; 4 fading embers.",
     row(4, 16, 16) + CENTER),
]
BIG_FX = ("w_eye", "r_cast", "r_flare")
NAME = "swain_fx_pack"
# why an effect is drawn again (a redraw pack, --only): what the first delivery measured at game size (2026-10-17)
REDO = {
    "a_bolt": "第一版每帧只有约 13 个像素，几乎全是最深的两档黑紫，放在游戏地面上看不见。这次乌鸦要**实心**：身体加两只翅膀铺满约 10×7 格，"
              "胸口的红白魂火至少 2×2 格（白芯），身后 3 格亮红拖尾；整体要比第一版亮很多（乌鸦用黑紫里较亮的三档，边缘可以有一圈深色）。",
    "w_eye": "第一版第 3–6 帧的眼睛实际只有 36×22 格（要求 56 格宽），画在人物脚下时被身体挡住大半。W 的爆炸范围是直径 60 格，"
             "**眼睛外圈要铺到 56 格宽、16 格高**（第 3–6 帧量一下实际像素），深红光圈再往外 2 格；第 8 帧的爆炸椭圆 50 格宽。",
    "e_hit": "第一版的爪子太细太散（每只 1–2 格宽，加起来像几粒散点）。这次每只爪子 **2–3 格宽、7–9 格高的实心深红/洋红爪子**，白色爪尖，"
             "第 1 帧地上的裂纹圈连成一圈完整的亮红椭圆（16×4 格）；中间 14 格宽的腿部位置照样留空。",
}
GROUPS = [
    ("a_bolt a_hit", ["Swain_Base_BA_Front", "Swain_Base_BA_mis_trail", "Swain_Base_BA_leadingedge_add",
                      "Swain_Base_BA_Flash_sharp", "Swain_Base_BA_Spark_cas"]),
    ("q_bolts q_hit", ["Swain_Base_Q_lightning2", "Swain_Base_Q_lightning3", "Swain_Base_Q_energyBall",
                       "Swain_Base_Q_hit_flash", "Swain_Base_Q_hit_flash_large", "Swain_Base_Q_Crack"]),
    ("e_out e_back", ["Swain_Base_E_birdshape", "Swain_Base_E_birdshape2_tip", "Swain_Base_E_return_mis_mult",
                      "Swain_Base_E_turning_mis_flash", "Swain_Base_E_wisps"]),
    ("e_hit e_pull", ["Swain_Base_E_hit_ground", "Swain_Base_E_Tar_BlastShapes", "Swain_Base_E_Deathshards",
                      "Swain_Base_E_DemonDrainSwoosh", "Swain_Base_E_Explode_Shards"]),
    ("w_eye w_hit", ["Swain_Base_W_Eye_Alpha_V02", "Swain_Base_W_Eye_Alpha_V03", "Swain_Base_W_Explode_Iris",
                     "Swain_Base_W_Ground_Circle_Alpha_V01", "Swain_Base_W_portal_ring_colors", "Swain_Base_W_Pulses_V02"]),
    ("p_frag", ["Swain_Base_W_Raven_TX_CM", "Swain_Base_Z_SoulWispsAlpha", "Swain_Base_R_Feathers"]),
    ("r_cast", ["Swain_Base_R_Cast_Dust_v03", "Swain_Base_R_Cas_Symbol_V01", "Swain_Base_R_Lightning",
                "Swain_Base_R_Shockwave"]),
    ("r_drain", ["Swain_Base_R_DemonDrainSwoosh", "Swain_Base_R_drainRing", "Swain_Base_R_Absorb_Scroll_Alpha"]),
    ("r_flare r_fl_hit", ["Swain_Base_R_Nova_Mis_Core", "Swain_Base_R_Nova_Mis_Energy", "Swain_Base_R_Nova_Mis_Front",
                          "Swain_Base_R_Nova_Mis_Dark_Background", "Swain_Base_R_Ring_Shockwave", "Swain_Base_R_tar_Flash"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_bolt：乌鸦弹从恶魔手掌心射出"), ("skill", 3, "q_bolts：五道闪电从手掌扇形射出"),
         ("skill2", 3, "e_out：恶魔之手从手掌飞出"), ("ult", 4, "r_cast：变身恶魔（翅膀光环 Claude 做）"),
         ("r_flare", 2, "r_flare：举爪放出魂火新星"), ("r_attack", 3, "恶魔形态的普攻"),
         ("dead", 4, "（参考）跪地举爪"), ("hit", 2, "（参考）受击")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Swain_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"斯维因 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    """His two forms at 4x: the idle and the demon (the demon arm out, eyes lit, the wings' aura behind)."""
    import ppu_rig as R
    import rig_swain as S
    ps = S.Poser()
    a = ps.rig.finish(ps.pose("A"))
    b = ps.rig.finish(ps.pose("B", arm=0))
    wing = R.compose(ps.rig, [(ps.aura, dict())])
    m = b[..., 3] > 0
    wing[m] = b[m]
    tiles = []
    for c in (a, wing):
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


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 诺克萨斯统领 斯维因：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/swain_idle.png`：3/4 正面朝右的高个将军，银白长发，近黑紫灰长大衣、暗红内衬，"
      f"古铜胸甲；右边是他化身恶魔的样子：画面右边那只手是赤红的恶魔手臂，眼睛发红光，身后的黑红翅膀是大招期间的光环，**翅膀 Claude 自己做，不用画**）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/swain_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/swain_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。**他出招用的是画面右边那只恶魔手**（普攻、Q、E 都从这只手的手掌射出）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里斯维因自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**恶魔的魂火是深红（白芯）**，**恶魔手和闪电带亮洋红**，**乌鸦、烟和恶魔的影子是黑紫色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`q_bolts`、`e_out`、`e_back` 都画成朝右，**上下对称**（往左时会上下翻）。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 15]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `swain_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，" f"打包成 `{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「狂食鸦群」 | 恶魔手射出乌鸦弹；打中英雄、W 和 E 抓到英雄、英雄阵亡时，乌鸦叼来魂屑：回血、加最大生命 | `a_bolt` · `a_hit` · `p_frag` |")
    a("| 技能 1 = Q「解脱之触」 | 恶魔手往前射出五道扇形散开的恶魔闪电 | `q_bolts` · `q_hit` |")
    a("| 技能 2 = E「永不复行」 | 恶魔之手飞出去再飞回来，路上的敌人被禁锢，被禁锢的英雄被拽近 | `e_out` · `e_back` · `e_hit` · `e_pull` |")
    a("| 被动自动放的 W「帝国视界」 | 远处地上睁开一只恶魔之眼，1.5 秒后爆炸、减速 | `w_eye` · `w_hit` |")
    a("| 大招「恶魔升华」 | 化身恶魔（身后黑红翅膀），持续吸取周围敌人的生命，再放出恶魔耀光（魂火新星） | `r_cast` · `r_drain` · `r_flare` · `r_fl_hit`（翅膀光环 Claude 做） |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（乌鸦和羽毛例外：实心的东西可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("深红魂火", CRIM), ("亮洋红（恶魔爪、闪电）", MAG), ("黑紫（乌鸦、烟、恶魔的影子）", SHADE),
                        ("蓝紫（只用在恶魔耀光的内缘）", VIOL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 52000，"
      "解脱之触扇形 62000 长，永不复行 70000 长，帝国视界半径 30000，恶魔升华吸取和恶魔耀光半径 60000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `swain_fx_{name}.png`：{title}\n")
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
        a(f"| `swain_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_swain_fx`（小的）和 `league_swain_big`（{'、'.join(BIG_FX)}，还有 Claude 从 B-1 的翅膀做的 `r_wings` 光环），"
      "tag = 名字（build_swain.py 的 views；r_wings 绑在 buff `league_swain_r_on`）。")
    a("- 投射物 `a_bolt`、`q_bolts`、`e_out`、`e_back` 画面朝方向转；`w_eye`、`r_cast`、`r_flare` 不跟随（地上 / 他身上的晚播画面，红色方规则）；"
      "`w_eye`、`e_hit` 的地面部分画在人物下面（z -1）。")
    a("- 用 `pixel_1x/` 切格（import_rell_fx / import_urgot_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="swain_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "swain_packs"), help="folder for the zip")
    a = ap.parse_args()
    global NAME
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/swa/fx_ref_swa.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "swain_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "swain_size.png"))
    shots_sheet(os.path.join(out, "design", "swain_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"swain_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
