#!/usr/bin/env python3
"""Build maokai_fx_pack.zip: step 3 of Maokai's sprite - Codex draws his effects (pack_jarvaniv_fx.py's way).

    python work/mko/fx_ref_mko.py            # League's particle textures -> C:/t/mko_work/fxref (Riot's art, local only)
    python tools/art/pack_maokai_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name maokai_fx_redo_pack]

The pack (C:/t/mko_work/fx/maokai_fx_pack, zipped into --out, default dist/maokai_packs) holds PROMPTS.md (also written
to assets/source/maokai/PROMPTS_FX.md), design/maokai_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/maokai_sapling.png (the sapling's design, 8x), design/maokai_size.png (the 1x idle at 4x on the arena colour with
the feet line, a 10-px ruler and the base fighter), design/maokai_shots.png (the finished action frames the pictures
start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for Maokai grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_maokai.py): projectiles e_lob (the sapling thrown), q_wave
(the shockwave), w_trail (him as a mass of roots under the ground), r_wall (the bramble wall); view_effects a_hit,
p_hit, p_heal, q_cast, q_hit, w_land, w_hit, e_land, e_idle, e_burst, e_hit, r_cast, r_hit; view_buffs q_slow, root,
e_slow, r_haste. League's colours: nature magic green-teal (the passive's heal, the sapling's blast), Bramble Smash
olive-brown dust with white light spikes, Twisted Advance bark roots with cyan veins and dirt, Nature's Grasp thorny
roots with teal glowing cracks. Light gets no outline, solid things (the sapling, roots, bark, rocks) may.
Red side: the client never mirrors an effect picture, so every picture is symmetric left to right, and the sapling on
the ground faces the viewer (front view, league_ekko's hologram rule); a flying picture turns with its flight, so the
four projectiles are drawn pointing right and symmetric top to bottom.
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
TMP = "C:/t/mko_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "maokai", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_maokai")
SAPLING = os.path.join(ROOT, "assets", "source", "maokai", "hd", "design_C.png")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "maokai_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


NATURE = "#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48"     # the passive's heal, nature magic
TEAL = "#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58"       # the sapling's blast, the glowing cracks and veins
DUST = "#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E"       # Bramble Smash's dust, dirt, rock
BARK = "#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C"       # roots, bark, wood chips
LEAF = "#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E"       # leaves, moss, thorny brambles
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
NA = f"a green-teal nature magic ramp ({NATURE})"
TE = f"a bright teal glow ramp ({TEAL})"
DU = f"an olive-brown dust and dirt ramp ({DUST})"
BA = f"a bark and root ramp ({BARK})"
LE = f"a leaf and moss green ramp ({LEAF})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("pointing RIGHT (the way it flies) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns "
      "it to its flight, so flying left it is drawn upside down)")
CENTER = "; centered in every cell."
HIM = "a huge hunched tree creature 38 squares wide and 40 tall stands in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
SAP = ("HIS SAPLING (the attached design picture, 8x: a small wooden seedling with a carved face, one glowing blue eye, a "
       "young leaf on top, two leaves as arms, a pointed root) seen FROM THE FRONT: its face looking at the viewer, "
       "symmetric left to right, about 8 squares wide and 12 tall, in its own colours (pale brown and yellow-green wood, "
       "a bright blue eye glint, green leaves) with a 1-square dark outline (it is a solid thing)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack + the passive
    ("a_hit", "普攻命中：巨臂砸中（目标身上），4 帧", "view_effects `league_maokai_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "巨大的木头手臂砸中目标：一团偏黄绿的白色闪光，几块浅褐色的木屑和尘土往外飞（参考 BA_Hit_flash、BA_Hitorbs）。**左右对称**。"
     "约 12 格。",
     f"{NA} and {BA}",
     f"a HEAVY WOODEN BLOW on a unit, 4 frames, {LR}: 1 a white flash 5 squares with a pale green rim; 2 a pale "
     "green-white burst 10 squares, 4 light brown wood chips flying out at mirrored places; 3 the burst thinner and 12 "
     "squares, the chips farther, a little dust; 4 fading chips and dust.",
     row(4, 12, 12) + CENTER),
    ("p_hit", "被动「吸元秘术」强化普攻命中（目标身上），5 帧",
     "view_effects `league_maokai_p_hit`（跟随，画在人物上面；左右对称）", "16",
     "吸元秘术这一下额外的魔法伤害：目标身上一团绿色的自然魔法爆开，几缕绿色光丝往外甩，绿色的星形闪光（参考 Passive_Heal_Impact_"
     "sparkle、flash_core、P_Soraka_Skin04_R_SparkleGreen）。**左右对称**。约 16 格。",
     NA,
     f"a NATURE MAGIC BURST on a unit, 5 frames, {LR}: 1 a white-green flash 5 squares; 2 a green burst 11 squares with "
     "a white core, 4 green star sparkles at mirrored places; 3 thin green wisps (curved strands 1 square thick) "
     "flung out at mirrored angles, the burst 14 squares; 4 the wisps farther and fading; 5 a few green sparkles.",
     row(5, 16, 16) + CENTER),
    ("p_heal", "被动「吸元秘术」回血（他身上，跟随），6 帧",
     "view_effects `league_maokai_p_heal`（跟随，画在他上面 z 2；左右对称；大图表）", "50 × 48",
     f"吸元秘术给他回血：一股绿色的光从他脚下往上卷（两边各一道螺旋的绿色光丝，只画在身体两侧和头顶上方），绿色的十字闪光一闪一闪，"
     f"最后在头顶散成光点（参考 Passive_Heal_Impact_Vortex、Wisps、Beam、sparkle）。**左右对称**，中间身体位置留空（{HIM}）。",
     NA,
     f"A HEALING SURGE round a figure, 6 frames, {LR} ({HIM}): 1 a green glow ring on the ground at its feet (an ellipse "
     "30 squares wide and 7 tall, white inner edge); 2 two green spiralling wisps rising from the ring along both sides "
     "of the figure (1-2 squares thick, the inside left empty), 6 green cross sparkles at mirrored places; 3 the wisps at "
     "the figure's middle, brightest; 4 the wisps at its top, curling inward over its head; 5 the wisps breaking into "
     "green motes above its head, the ring faded; 6 a few rising motes.",
     row(6, 50, 48) + "; centered across, the figure's feet (the ring's middle) 4 squares above the cell's bottom row."),
    # ---- Q Bramble Smash
    ("q_cast", "Q 荆棘重击：拳头砸地（他脚下，跟随），6 帧",
     "view_effects `league_maokai_q_cast`（跟随，画在人物下面 z -1；左右对称；大图表）", "60 × 28",
     "他把巨拳砸进地里：落拳处一道白光，几道白色光刺往上冲，地面裂开一道道裂纹，一圈橄榄褐的尘土和冲击环往外扩（把身边的敌人推开），"
     "小石块和泥块往外飞（参考 Q_flash、Q_cas_lightspikes、Q_groundcracks、Q_dustcloud、Q_Cas_aoering、W_dirtbits）。"
     "**左右对称**（从斜上方看，地上的环是扁椭圆）。",
     f"{DU} and {NA}",
     f"A FIST SLAMMED INTO THE GROUND seen from above at an angle, 6 frames, {LR}: 1 a white flash 10 squares at the "
     "ground's middle, 4 white light spikes shooting UP from it (1-2 squares thick, 6-10 tall, at mirrored places); 2 "
     "dark ground cracks running out at mirrored angles, an olive-brown dust ring starting (an ellipse 24 squares wide and "
     "7 tall with a pale inner edge); 3 the dust ring 40 wide and 12 tall, small stones and dirt clods flying up and out "
     "at mirrored places; 4 the ring 54 wide and 16 tall, thinner, the stones at their highest; 5 dust settling, stones "
     "falling; 6 faint dust and the cracks fading.",
     row(6, 60, 28) + "; centered across, the ellipse's middle 8 squares above the cell's bottom row."),
    ("q_wave", "Q 冲击波：沿地面往前推的冲击（投射物，向前飞），4 帧循环",
     "view_projectiles `league_maokai_q_wave`（画在人物下面 z -1；**朝右画、上下对称**：图跟着飞行方向转；大图表）", "20 × 14",
     "Q 的冲击波沿着地面往前推出去（会打中前面一段的敌人）：一道往前（画面右边）推进的弧形尘土冲击前沿，前沿亮（白黄色），后面拖着"
     "橄榄褐的尘土和碎石，几道小小的绿色荆棘刺（参考 Q_leadingedge、Q_mis_groundcracks、Q_mis_sand、Q_mis_wake_tex）。"
     "**朝右画、上下对称**（游戏会把图转到飞行方向）。4 帧循环。",
     f"{DU} and {LE}",
     f"A GROUND SHOCKWAVE travelling forward, 4 frames, a seamless loop, {TB}: a curved bright front 3 squares thick at "
     "the cell's right part (pale yellow-white, an arc bulging to the right, 12 squares tall), behind it (to the left) "
     "rolling olive-brown dust and small stones fading out to the left, 4 small green bramble thorns sticking out of the "
     "dust at mirrored places (top and bottom); each frame the dust and stones churn (frame 4 flows back into frame 1).",
     row(4, 20, 14) + CENTER),
    ("q_hit", "Q 命中（目标身上），4 帧", "view_effects `league_maokai_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "冲击波打中并推开敌人：一团尘土炸开，几块碎石，中间一道白黄色的闪光，几根绿色荆棘刺扎出来（参考 Q_tar_shards、Q_Tar_glow）。"
     "**左右对称**。约 14 格。",
     f"{DU} and {LE}",
     f"a BRAMBLE SHOCK HIT on a unit, 4 frames, {LR}: 1 a pale yellow-white flash 5 squares; 2 an olive-brown dust "
     "burst 10 squares, 4 green thorns jutting out at mirrored angles (1 square thick, 4 long); 3 the dust 14 squares, "
     "small stones flying out at mirrored places; 4 settling dust.",
     row(4, 14, 14) + CENTER),
    ("q_slow", "Q 减速（敌人脚下，循环），4 帧",
     "view_buffs `league_maokai_q_s1`（跟随，画在人物下面；左右对称；循环）", "16 × 8",
     "被荆棘重击减速的敌人：脚下缠着几根带刺的绿色荆棘藤，一闪一闪。**左右对称**，只画在脚下。",
     f"{LE} and {BA}",
     f"BRAMBLES SLOWING a unit at its feet, 4 frames, a seamless loop, {LR}: on the ground a tangle of thorny green "
     "bramble vines (an ellipse 14 squares wide and 4 tall made of curling vines 1 square thick with small thorns), "
     "brown root bits under them; 1 dim, 2 brighter, 3 brightest (the thorns' tips lit), 4 like 2.",
     row(4, 16, 8) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
    # ---- W Twisted Advance
    ("w_trail", "W 扭曲突刺：化作树根在地下穿行（投射物，向前飞），4 帧循环",
     "view_projectiles `league_maokai_w_trail`（画在人物下面 z -1；**朝右画、上下对称**；大图表）", "24 × 16",
     "他化作一团扭动的树根钻进地里冲向目标（他自己在冲刺时看不见，这一团就是他）：一团纠缠在一起的深褐色树根，根上有青色的发光纹路，"
     "往前（画面右边）扭动，前面带起泥块和碎石，后面拖一道浅浅的土痕（参考 W_Tar_Root_TX、w_mis_leadingedge、W_dirtbits、W_rocks）。"
     "**朝右画、上下对称**。4 帧循环。",
     f"{BA} and {TE} and {DU}",
     f"A WRITHING MASS OF ROOTS burrowing forward, 4 frames, a seamless loop, {TB}: a tangle of dark brown bark roots "
     "16 squares long and 10 tall in the middle (thick roots 2 squares wide twisting round each other, thin glowing teal "
     "veins along them, a 1-square dark outline: solid things), the front end (right) a bulge of roots pushing forward "
     "with dirt clods and small stones thrown out at mirrored places (top and bottom), behind it (left) a faint trail of "
     "dirt; each frame the roots twist a little (frame 4 flows back into frame 1).",
     row(4, 24, 16) + CENTER),
    ("w_land", "W 冲到目标处：树根从地里冒出（地上，跟随），6 帧",
     "view_effects `league_maokai_w_land`（跟随，画在人物下面 z -1；左右对称；大图表）", "48 × 30",
     "他在目标身边从地里冒出来：地面裂开，一圈粗树根从地里猛地刺出来（左右各几根往上冲，带青色光纹），泥块和碎石往外飞，最后树根缩回地下，"
     "留下一点尘土（参考 W_Tar_Root_TX、w_targround、W_rocks、W_dirtbits）。**左右对称**，中间留空（他从中间冒出来）。",
     f"{BA} and {TE} and {DU}",
     f"ROOTS BURSTING OUT OF THE GROUND seen from above at an angle, 6 frames, {LR}: the middle 16 squares wide left "
     "empty (he rises there); 1 dark cracks opening on the ground (an ellipse 30 squares wide and 8 tall) with a teal "
     "glow in them; 2 thick bark roots stabbing UP out of the ground along both sides of the ellipse (2-3 squares thick, "
     "8-14 squares tall, teal veins, a 1-square dark outline), dirt clods flying; 3 the roots at their tallest, stones "
     "and dirt at their highest, a dust ring 40 wide; 4 the roots sinking back; 5 the roots half gone, dust settling; 6 "
     "faint dust and cracks.",
     row(6, 48, 30) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
    ("w_hit", "W 禁锢命中（目标身上），4 帧", "view_effects `league_maokai_w_hit`（跟随，画在人物上面；左右对称）", "14",
     "扭曲突刺打中目标：一道青色的闪光，几根深褐色的根刺从目标身上往外扎，青色火星（参考 E_tar_hitspikes）。**左右对称**。约 14 格。",
     f"{BA} and {TE}",
     f"a ROOT STRIKE on a unit, 4 frames, {LR}: 1 a teal-white flash 5 squares; 2 a teal burst 10 squares with a white "
     "core, 4 dark root spikes jutting out at mirrored angles (2 squares thick at the base, 5 long, a dark outline); 3 "
     "the spikes withdrawing, teal sparks at mirrored places; 4 fading sparks.",
     row(4, 14, 14) + CENTER),
    ("root", "W / R 禁锢：缠住敌人脚的树根（敌人脚下，循环），4 帧",
     "view_buffs `league_maokai_w_bound` 和 `league_maokai_r_bound`（同一张图，跟随，画在人物上面；左右对称；循环）", "22 × 16",
     f"被扭曲突刺或自然之握禁锢的敌人：几根深褐色的粗树根从地里伸出来缠住他的腿和脚（左右两边各两根往上弯，缠到膝盖高度），根上的青色光纹"
     f"一明一暗。**左右对称**，中间人的腿留出来（{CHAMP}，只画在他小腿和脚的两边和前面，不要盖住上身）。",
     f"{BA} and {TE}",
     f"ROOTS BINDING a unit's legs, 4 frames, a seamless loop, {LR} ({CHAMP}): from the ground round its feet thick "
     "dark bark roots (2 squares thick, a 1-square dark outline) curling up both sides of its legs to knee height (about "
     "12 squares up), two on each side, their tips hooking inward; a ring of disturbed earth on the ground (an ellipse 20 "
     "wide and 5 tall); thin teal veins on the roots: 1 dim, 2 brighter, 3 brightest, 4 like 2.",
     row(4, 22, 16) + "; centered across, the feet (the ellipse's middle) 2 squares above the cell's bottom row."),
    # ---- E Sapling Toss
    ("e_lob", "E 树苗投掷：飞出去的树苗（投射物，向前飞），4 帧循环",
     "view_projectiles `league_maokai_e_lob`（画在人物上面；**朝右画、上下对称**：图跟着飞行方向转）", "12 × 12",
     "扔出去的树苗在空中翻滚着飞：树苗缩成一团（叶子包着木头身体，一点蓝色眼睛的光），整团是圆的、**上下对称**，后面拖一道淡绿的光痕"
     "（参考 E_SaplingTrail_ColorBlur、E_Miss_trail）。4 帧循环（翻滚）。",
     f"{BA} and {LE} and {TE}",
     f"A SAPLING TUMBLING THROUGH THE AIR, 4 frames, a seamless loop, {TB}: a round curled-up sapling 7 squares across "
     "in the cell's right part (pale brown wood wrapped in green leaves, a 1-square dark outline, one bright blue glint "
     "on its middle), a soft pale green trail 4 squares long behind it (left); each frame the leaves are turned a little "
     "(a tumbling look) while the whole stays symmetric top to bottom.",
     row(4, 12, 12) + CENTER),
    ("e_land", "E 树苗落地扎根（地上，不跟随），4 帧",
     "view_effects `league_maokai_e_land`（不跟随，画在人物下面 z 0；左右对称）", "18 × 18",
     f"树苗落地、扎进土里：第 1 帧一团泥土溅起；第 2 帧树苗从泥土里冒出（正面朝前）；第 3 帧站直，顶上的叶子一抖，几片小叶子飘起；"
     f"第 4 帧站好，和下面的「站岗」第 1 帧一样。树苗是{SAP.split(' seen FROM THE FRONT')[0]}的样子，但**正面朝前**（左右对称：游戏在红色方"
     f"不会把图镜像），约 8 格宽、12 格高。",
     f"{BA} and {LE} and {TE} and {DU}",
     f"A SAPLING LANDING AND TAKING ROOT on the ground, 4 frames, {LR}: 1 a dirt splash on the ground (an ellipse 12 "
     f"squares wide and 4 tall, dirt clods flying up at mirrored places); 2 {SAP} rising halfway out of the soil; 3 the "
     "sapling standing, its top leaf shaking, 4 tiny leaves floating up at mirrored places; 4 the sapling standing still "
     "exactly as in the first frame of the next sheet (e_idle). Its root tip on the cell's bottom row.",
     row(4, 18, 18) + "; centered across."),
    ("e_idle", "E 树苗站岗（地上，不跟随，循环），4 帧",
     "view_effects `league_maokai_e_idle`（不跟随，画在人物下面 z 0；左右对称；每 0.5 秒重放一次，所以 4 帧要能首尾相接）", "14 × 16",
     f"树苗插在地上戒备，最多站 12 秒：{SAP.split(' seen FROM THE FRONT')[0]}，**正面朝前**、左右对称。4 帧循环：顶上的叶子轻轻晃，"
     f"身体上下起伏 1 格，蓝眼睛一亮一暗，脚下一小圈青色的光（参考 E_TEAMID_Ring）。第 4 帧接得回第 1 帧。",
     f"{BA} and {LE} and {TE}",
     f"A SAPLING STANDING GUARD on the ground, 4 frames, a seamless loop, {LR}: {SAP}, standing with its root tip on the "
     "cell's bottom row; a faint teal ring on the ground round its root (an ellipse 10 squares wide and 3 tall); 1 still; "
     "2 its body a square lower, its top leaf tilted, the eye brighter; 3 like 1 with the eye brightest; 4 like 2 with "
     "the eye dimmer (frame 4 flows back into frame 1).",
     row(4, 14, 16) + "; centered across."),
    ("e_burst", "E 树苗扑向敌人爆炸（敌人身上，不跟随），6 帧",
     "view_effects `league_maokai_e_burst`（不跟随，画在人物上面 z 2；左右对称；大图表）", "48 × 40",
     f"有敌人靠近，树苗跳起来扑到他身上炸开：第 1 帧树苗（正面朝前）跳在敌人头顶上方；第 2 帧往下扑，身上裂缝发青光；第 3 帧一个青绿色的"
     f"魔法爆炸（白芯，外面一圈青色的爆炸环，参考 E_BigExplosion_Blast_Ring、Maokai_base_E_tar_clouds）；第 4 帧爆炸最大（扁圆形，"
     f"约 44 格宽），木屑、叶子往外飞；第 5 帧变淡，叶子飘落；第 6 帧几片叶子和光点。**左右对称**，中间敌人的位置在爆炸里（{CHAMP}）。",
     f"{TE} and {NA} and {LE} and {BA}",
     f"A SAPLING POUNCING AND EXPLODING on a unit, 6 frames, {LR} ({CHAMP}): 1 {SAP} leaping, high over the champion's "
     "head (near the cell's top); 2 the sapling diving down onto it, glowing teal cracks across its body; 3 a teal-green "
     "magic explosion at the champion's middle, a white core 10 squares, a bright teal blast ring round it (an ellipse 28 "
     "squares wide and 18 tall); 4 the blast at its biggest (44 wide and 26 tall), wood chips and green leaves flying out "
     "at mirrored places; 5 the blast faded, leaves drifting down; 6 a few leaves and teal motes.",
     row(6, 48, 40) + "; centered across, the champion's feet 2 squares above the cell's bottom row."),
    ("e_hit", "E 爆炸命中（敌人身上），4 帧", "view_effects `league_maokai_e_hit`（跟随，画在人物上面；左右对称）", "14",
     "树苗的爆炸炸到附近的敌人：一团青绿色的闪光，几片叶子和木屑（参考 Maokai_base_E_tar_clouds、E_Sapling_Bits）。**左右对称**。约 14 格。",
     f"{TE} and {LE}",
     f"a SAPLING BLAST HIT on a unit, 4 frames, {LR}: 1 a teal-white flash 5 squares; 2 a teal-green burst 10 squares "
     "with a white core, 4 green leaves at mirrored places; 3 the burst 14 squares and thinner, leaves and wood chips "
     "flying out; 4 fading leaves.",
     row(4, 14, 14) + CENTER),
    ("e_slow", "E 减速（敌人脚下，循环），4 帧",
     "view_buffs `league_maokai_e_slow`（跟随，画在人物下面；左右对称；循环）", "16 × 8",
     "被树苗炸到的敌人减速：脚下一摊发青光的黏液和几片落叶，一明一暗。**左右对称**，只画在脚下。",
     f"{TE} and {LE}",
     f"STICKY SAP SLOWING a unit at its feet, 4 frames, a seamless loop, {LR}: on the ground a puddle of glowing teal sap "
     "(an ellipse 14 squares wide and 4 tall) with 4 small green leaves on it at mirrored places; 1 dim, 2 brighter, 3 "
     "brightest, 4 like 2.",
     row(4, 16, 8) + "; centered across, the ellipse's middle 2 squares above the cell's bottom row."),
    # ---- R Nature's Grasp
    ("r_cast", "R 自然之握：两臂砸地召唤（他脚下，跟随），6 帧",
     "view_effects `league_maokai_r_cast`（跟随，画在人物下面 z -1；左右对称；大图表）", "64 × 30",
     "他两臂砸地召唤荆棘墙：落点一道青白光，地面裂开一圈发青光的裂纹（参考 R_Crater_01、R_Trail_Cracks_Glow），一圈尘土和碎石往外炸开"
     "（参考 R_rock_debris、R_clouds），几根带刺的树根从裂缝里冒头。**左右对称**（地上的圈是扁椭圆）。",
     f"{TE} and {DU} and {BA}",
     f"A GROUND-SHAKING SUMMONING seen from above at an angle, 6 frames, {LR}: 1 a teal-white flash 12 squares at the "
     "ground's middle; 2 a ring of glowing teal cracks opening on the ground (an ellipse 30 squares wide and 9 tall, the "
     "cracks jagged lines 1 square thick), dust bursting; 3 the cracks out to 46 wide, grey-brown rock debris and dust "
     "flying out at mirrored places, 4 short thorny root tips poking up out of the cracks (dark bark, a dark outline); 4 "
     "a dust ring 60 wide, the debris at its highest; 5 dust settling, the cracks' glow dimmer; 6 faint glowing cracks.",
     row(6, 64, 30) + "; centered across, the ellipse's middle 8 squares above the cell's bottom row."),
    ("r_wall", "R 自然之握：慢慢往前推进的荆棘墙（投射物，向前飞），4 帧循环",
     "view_projectiles `league_maokai_r_wall`（画在人物下面 z -1；**朝右画、上下对称**：图跟着飞行方向转，斜着放就是斜的墙；大图表）",
     "18 × 60",
     "一道很宽的荆棘墙贴着地面慢慢往前（画面右边）推：墙是**竖着的一条宽带**（画面里竖着约 56 格长、10 格宽：游戏里它横在前进方向上，"
     "所以朝右飞的时候是竖的），由纠缠的带刺树根和荆棘组成（深褐色树根、绿色荆棘、青色发光的刺尖），墙的前沿（右边）有一点尘土翻起，"
     "后面（左边）拖一道发青光的裂纹（参考 R_Root_A、Maokai_Skin04_R_Root_A、R_Trail_Cracks_Glow、R_sparklines）。"
     "**朝右画、上下对称**（游戏会把图转到飞行方向）。4 帧循环（树根扭动、刺尖一闪一闪）。",
     f"{BA} and {LE} and {TE} and {DU}",
     f"A WALL OF BRAMBLES advancing, 4 frames, a seamless loop, {TB}: a tall vertical band in the middle of the cell, 10 "
     "squares wide and 56 squares tall, made of thick twisting dark bark roots (2-3 squares thick, a 1-square dark "
     "outline: solid things) woven with green thorny bramble vines, thorn tips glowing bright teal all along it; at its "
     "right edge (the front) dust and dirt clods kicked up; behind it (left) a thin trail of glowing teal ground cracks 4 "
     "squares long; each frame the roots writhe and different thorn tips glint (frame 4 flows back into frame 1).",
     row(4, 18, 60) + CENTER),
    ("r_hit", "R 荆棘墙撞到敌人（敌人身上），4 帧", "view_effects `league_maokai_r_hit`（跟随，画在人物上面；左右对称）", "16",
     "荆棘墙撞到敌人：青色的闪光，几根带刺的树根从下往上扎（参考 E_tar_hitspikes、R_sparklines），绿色和青色的碎光。**左右对称**。"
     "约 16 格。",
     f"{TE} and {BA} and {LE}",
     f"a BRAMBLE IMPACT on a unit, 4 frames, {LR}: 1 a teal-white flash 6 squares; 2 a teal burst 11 squares with a "
     "white core, 4 thorny root spikes stabbing up and out at mirrored angles (dark bark, a dark outline, glowing teal "
     "tips); 3 the spikes withdrawing, teal and green sparks at mirrored places; 4 fading sparks.",
     row(4, 16, 16) + CENTER),
    ("r_haste", "R 撞到英雄后的加速（他脚下，循环），4 帧",
     "view_buffs `league_maokai_r_h2`（跟随，画在人物下面 z -1；左右对称；循环）", "40 × 12",
     f"自然之握撞到敌方英雄后他跑得更快：脚下一圈绿色的风，几片叶子往后飘（左右两边一样）。**左右对称**，只画在脚下（{HIM}）。",
     f"{NA} and {LE}",
     f"A NATURE'S HASTE at a huge figure's feet, 4 frames, a seamless loop, {LR} ({HIM}): a green wind ring on the ground "
     "(an ellipse 34 squares wide and 7 tall, 1 square thick, brighter on its near side), 6 small green leaves riding it "
     "at mirrored places, each frame a little farther round (frame 4 flows back into frame 1).",
     row(4, 40, 12) + "; centered across, the ellipse's middle 3 squares above the cell's bottom row."),
]
BIG_FX = ["p_heal", "q_cast", "q_wave", "w_trail", "w_land", "e_burst", "r_cast", "r_wall", "r_haste"]
REDO = {}
GROUPS = [
    ("a_hit p_hit p_heal", ["Maokai_Base_BA_Hit_flash", "Maokai_Base_BA_Hitorbs", "Maokai_Base_Passive_Heal_Impact_Vortex",
                            "Maokai_Base_Passive_Heal_Impact_Wisps_2x2", "Maokai_Base_Passive_Heal_Impact_sparkle_2x2",
                            "Maokai_Base_Passive_Heal_Impact_flash_core_2x2", "Maokai_Base_P_Soraka_Skin04_R_SparkleGreen"]),
    ("q_cast q_wave q_hit q_slow", ["Maokai_Base_Q_flash", "Maokai_Base_Q_cas_lightspikes", "Maokai_Base_Q_groundcracks",
                                    "Maokai_Base_Q_dustcloud", "Maokai_Base_Q_Cas_aoering", "Maokai_Base_Q_leadingedge",
                                    "Maokai_Base_Q_mis_wake_tex", "Maokai_Base_Q_tar_shards"]),
    ("w_trail w_land w_hit root", ["Maokai_Base_W_Tar_Root_TX", "Maokai_Base_w_mis_leadingedge", "Maokai_Base_W_dirtbits",
                                   "Maokai_Base_W_rocks", "Maokai_Base_w_targround", "Maokai_Base_E_tar_hitspikes"]),
    ("e_lob e_land e_idle e_burst e_hit e_slow", ["Maokai_Base_E_SaplingTrail_ColorBlur", "Maokai_Base_E_Sapling_Bits",
                                                  "Maokai_Base_E_Sapling_GrownUp_Leaf", "Maokai_Base_E_TEAMID_Ring",
                                                  "Maokai_Base_E_BigExplosion_Blast_Ring", "Maokai_base_E_tar_clouds",
                                                  "Maokai_Base_leaf"]),
    ("r_cast r_wall r_hit r_haste", ["Maokai_Base_R_Crater_01", "Maokai_Base_R_Trail_Cracks_Glow", "Maokai_Base_R_Root_A",
                                     "Maokai_Skin04_R_Root_A_TX_CM_V03", "Maokai_Base_R_rock_debris", "Maokai_Base_R_clouds",
                                     "Maokai_Base_R_sparklines"]),
]
FEET = 11                                             # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit / p_hit：巨臂砸中前方的目标"), ("idle", 1, "p_heal：回血的光从他脚下往上卷"),
         ("skill", 3, "q_cast：拳头砸地；q_wave 从这里往前推"), ("skill2", 2, "W：钻进地里，w_trail 在地下冲向目标"),
         ("skill2_land", 3, "w_land：在目标身边冒出来"), ("skill_e", 3, "e_lob：爪子把树苗扔出去"),
         ("ult", 4, "r_cast：两臂砸地；r_wall 从这里往前推"), ("run", 1, "r_haste：加速时脚下的风")]


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
                sys.exit(f"missing reference {p}")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Maokai_Base_", "").replace("Maokai_base_", "")
                   .replace("Maokai_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"茂凯 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    import rig_maokai as M
    F = M.form()
    c = F.rig.finish(F.pose())
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)).save(path)


def sapling_sheet(path):
    """The sapling's design (the user's step-1 pick C-2), 8x on grey."""
    s = np.asarray(Image.open(lp(SAPLING)).convert("RGBA"))
    big = Image.fromarray(np.repeat(np.repeat(s, 8, 0), 8, 1))
    bg = Image.new("RGBA", (big.width + 32, big.height + 32), (225, 225, 225, 255))
    bg.alpha_composite(big, (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 茂凯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/maokai_idle.png`：3/4 正面朝右的巨大树精，背上青绿苔藓树冠，"
      f"脸长在树干中间、两只蓝眼睛，近侧一条巨大的浅褐色木头手臂、拳头上刻着发蓝光的鬼脸，远侧绿爪子拿着小树苗，背后树枝挂着蓝色水晶灯笼，"
      f"腰间紫布）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**"
      f"（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/maokai_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/maokai_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - `design/maokai_sapling.png`：**树苗的造型**（8 倍）。和树苗有关的几张（`e_land`、`e_idle`、`e_burst`）照它的样子画，"
      "但**地上的树苗要画成正面朝前、左右对称**（脸朝着看的人：游戏在红色方不会把图镜像，侧面的树苗到了红色方会朝反方向）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里茂凯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**被动回血是绿色的自然魔法**，**荆棘重击是橄榄褐的尘土加白色光刺**，**扭曲突刺是带青色光纹的树根和泥土**，"
      "**树苗的爆炸是青绿色**，**自然之握是带刺的树根、绿色荆棘和发青光的裂纹**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。")
    a("> - **地上、身上的图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。")
    a("> - **4 张飞出去的图（`e_lob`、`q_wave`、`w_trail`、`r_wall`）朝右画、严格上下对称**：游戏会把它们转到飞行方向，往左飞的时候是上下颠倒的，"
      "所以上下必须一样。荆棘墙 `r_wall` 在图里是**竖着的一条宽带**（游戏里它横在前进方向上）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 15]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `maokai_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/maokai_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。"
      "中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「吸元秘术」 | 巨臂砸击；技能打中敌人后，下一次普攻额外造成魔法伤害并给自己回血 | `a_hit` · `p_hit` · `p_heal` |")
    a("| 技能 1 = Q「荆棘重击」 | 拳头砸地，推开身边的敌人，一道冲击波沿地面往前推，打中的敌人减速 | `q_cast` · `q_wave` · `q_hit` · `q_slow` |")
    a("| 技能 2 = W「扭曲突刺」 | 化作树根钻进地里冲向敌方英雄（冲刺时他看不见、免伤），冒出来禁锢目标 | `w_trail` · `w_land` · `w_hit` · `root` |")
    a("| 自动放的 E「树苗投掷」 | 把树苗扔到敌人脚下，树苗扎根站岗，敌人靠近就扑上去爆炸，炸到的敌人减速 | `e_lob` · `e_land` · `e_idle` · `e_burst` · "
      "`e_hit` · `e_slow` |")
    a("| 大招「自然之握」 | 两臂砸地，一道很宽的荆棘墙慢慢往前推，碰到的敌人受伤并被禁锢（推得越远禁锢越久），撞到英雄后他加速 | `r_cast` · "
      "`r_wall` · `r_hit` · `root` · `r_haste` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：树苗、树根、树皮、石块可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("绿色自然魔法（被动、加速）", NATURE), ("青色发光（树苗爆炸、发光的裂纹和根上的纹路）", TEAL),
                        ("橄榄褐尘土泥块（荆棘重击、落地的尘土）", DUST), ("树皮树根（树根、木屑）", BARK),
                        ("叶子苔藓荆棘（叶子、荆棘藤）", LEAF)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：荆棘重击推开半径 16000、冲击波宽 "
      "20000，树苗爆炸半径 24000，荆棘墙宽 56000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `maokai_fx_{name}.png`：{title}\n")
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
        a(f"| `maokai_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_maokai_fx`（小的）和 `league_maokai_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_maokai.py 的 views；`q_slow` 绑 buff `q_s1`，`r_haste` 绑 `r_h2`，`root` 绑 `w_bound` 和 `r_bound`）。")
    a("- 投射物（`e_lob`、`q_wave`、`w_trail`、`r_wall`）朝右、上下对称；`e_land`、`e_idle`、`e_burst` 不跟随（地上的晚播画面）；"
      "`e_idle` 每 30 tick 重放一次（e_link），4 帧共 0.5 秒。")
    a("- 用 `pixel_1x/` 切格（import_nasus_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="maokai_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "maokai_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/mko/fx_ref_mko.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "maokai_idle.png"))
    sapling_sheet(os.path.join(out, "design", "maokai_sapling.png"))
    shape = size_sheet(os.path.join(out, "design", "maokai_size.png"))
    shots_sheet(os.path.join(out, "design", "maokai_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"maokai_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
