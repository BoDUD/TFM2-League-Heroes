#!/usr/bin/env python3
"""Build silco_fx_pack.zip: step 3 of Silco's sprite - Codex draws his effects and his three skill icons
(pack_alune_fx.py's way).

    python tools/lol/fx_ref_silco.py            # his TFT particle textures + the monstrosity -> C:/t/sc_work/fxref
    python tools/art/pack_silco_fx.py [--no-zip] [--out DIR] [--only a_hit,q_burst --name silco_fx_redo_pack]

The pack (C:/t/sc_work/fx/silco_fx_pack, zipped into --out, default dist/silco_packs) holds PROMPTS.md (also written to
assets/source/silco/PROMPTS_FX.md), design/silco_design.png (the approved idle at 4x on its own squares),
design/silco_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter), refs/tft_fx_ref.png (his own TFT particle textures - grey shapes the game tints - grouped by the effect they
inform) and refs/monstrosity_*.png (TFT's monstrosity model: the purple grub his canister lets out). The effects are
the views the kit binds (tools/kit/build_silco.py, the user's picks 2026-10-27: mid, plan A 「统领·畸变体」):
view_projectiles a_vial, q_can, r_can; view_effects a_hit, q_warn, q_burst, r_warn, r_burst and tft.dll's m_leap,
m_bite (drawn on the victim's LEFT; the import mirrors it into m_bite_r), m_die, r_fog, e_dose, e_crash; view_buffs
e_shimmer, p_shield, p_dom (d5), r_slow. Plus the three skill icons.
His colours: SHIMMER (glowing magenta-purple), Zaun's CHEMICAL GREEN, the COPPER of his canisters, the monstrosity's
violet flesh and gold teeth, and his waistcoat's GOLD for the icons' frames.
Red side: the client never mirrors an effect picture, so every hit, buff, ground and falling picture is symmetric left
to right (m_bite excepted: its two sides are two pictures); the flying ones point right and are symmetric top to bottom
(the game turns them).
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
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/sc_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "silco", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "silco", "hd")
NAME = "silco_fx_pack"
PPU = 2.0

SHIM = "#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070"           # Shimmer: glowing magenta-purple
CHEM = "#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412"            # Zaun's chemical green
COPPER = "#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C"           # the canisters' copper and iron
FLESH = "#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C"            # the monstrosity's violet flesh
TEETH = "#FFF6C8, #F0C850, #B0882A"                             # its gold teeth
SMOG = "#E4ECD8, #AEBE98, #76866A, #46523E"                     # grey-green smog
GOLD = "#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A"             # his waistcoat's gold trim (icon frames)
SH = f"a Shimmer magenta ramp ({SHIM})"
CH = f"a chemical green ramp ({CHEM})"
CO = f"a copper and iron ramp ({COPPER})"
FL = f"a violet flesh ramp ({FLESH})"
TE = f"a gold teeth ramp ({TEETH})"
SM = f"a grey-green smog ramp ({SMOG})"
GD = f"a gold ramp ({GOLD})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
TB = ("pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns "
      "it to its flight)")
MAGIC = ("everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN "
         "gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat "
         "shades, crisp shapes; no smooth neon beams, no fire")
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
GRUB = ("a MONSTROSITY: a stubby violet GRUB about 9 squares long and 6 thick (darker violet back, paler belly), its "
        "front end one big ROUND MOUTH ringed with GOLD fangs, a small glowing PINK eye above the mouth (refs "
        "monstrosity_*.png)")
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted "
        "corners, a murky dark green-black inside, the symbol big and centred, lit from the upper left; pixel art at "
        "2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_vial", "普攻：飞出去的微光药剂瓶，4 帧循环", "view_projectiles `tft_silco_a_vial`（弹道，z 2；朝右、上下对称）", "12 × 6",
     "他甩出去的**微光药剂瓶**：一支横着飞的小玻璃瓶，铜盖朝前（右边），瓶里发光的洋红液体在晃，后面拖两三滴紫色的液滴。"
     "**朝右飞，上下对称**，4 帧循环（液体的高光来回晃）。",
     SH + ", " + CO,
     "A FLYING SHIMMER VIAL, 4 looping frames, " + TB + ": a small glass vial lying along the flight (8 squares long, 3 "
     "tall), its copper cap at the FRONT (right), glowing magenta liquid inside with a white highlight, two or three "
     "magenta droplets trailing 3 squares behind it; frames 1-4 the highlight sliding back and forth in the liquid. " +
     MAGIC + ".",
     row(4, 12, 6) + CENTER),
    ("a_hit", "普攻：药剂瓶打中，4 帧", "view_effects `tft_silco_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "药剂瓶在人身上碎开：一下洋红的闪光，玻璃碎片和紫色液体往两边溅开，冒一点点紫烟。**左右对称**，4 帧。",
     SH + ", " + SM,
     "A SHATTERING VIAL, 4 frames, " + LR + ": 1 a magenta-white flash 6 squares across; 2 tiny white glass shards and "
     "magenta droplets bursting out to both sides (mirrored) 12 across; 3 droplets falling, a small puff of purple "
     "vapour in the middle; 4 the vapour fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_can", "罐装畸变体：飞出去的储罐，4 帧循环", "view_projectiles `tft_silco_q_can`（抛物线弹道，z 2；朝右、上下对称）", "12 × 10",
     "他扔出去的**储罐**：一个小铁皮罐（铜色的箍、中间一扇发绿光的玻璃窗，窗里隐约有个扭动的影子），横着翻滚着飞。"
     "**朝右飞，上下对称**，4 帧循环（窗里的绿光一明一暗）。",
     CO + ", " + CH + ", " + FL,
     "A THROWN CANISTER, 4 looping frames, " + TB + ": a small metal canister lying along the flight (9 squares long, 7 "
     "tall), dark iron ends with copper bands, one round glowing GREEN GLASS WINDOW in its middle with a dim violet "
     "squirming shape behind it; frames 1-4 the window's green glow pulsing brighter and dimmer, a thin green vapour "
     "wisp trailing from the left end. " + MAGIC + ".",
     row(4, 12, 10) + CENTER),
    ("q_warn", "罐装畸变体：地上的落点，4 帧循环", "view_effects `tft_silco_q_warn`（落点，地面，z -2，不跟随；左右对称）", "26 × 10",
     "储罐要落下的地方：地上一圈细细的**绿色化学警示圈**（从斜上方看的椭圆），圈里几点绿色光斑。**左右对称**，4 帧循环。",
     CH + ", " + SM,
     "A TARGET MARK, 4 looping frames, " + LR + ", " + GROUND_E + ": a thin dashed ring of chemical green light 22 "
     "squares wide and 7 tall, four small brighter green ticks at its left, right, front and back; frames 1-4 the "
     "dashes running round and the ticks blinking. " + MAGIC + ".",
     row(4, 26, 10) + CENTER),
    ("q_burst", "罐装畸变体：储罐炸开，7 帧", "view_effects `tft_silco_q_burst`（大表，落点，z 3，不跟随；左右对称）", "40 × 34",
     "储罐砸到地上炸开：铜色的碎铁片往两边飞，一团**翻滚的绿色化学气体**冲起来，洋红的液体溅开（畸变体本身是另外的图）。"
     "砸的地方在格子底部往上 4 格。**左右对称**，7 帧。",
     CH + ", " + CO + ", " + SH,
     "A BURSTING CANISTER, 7 frames, " + LR + ": the burst sits on the ground line 4 squares above the bottom. 1 a "
     "white-green flash 10 squares across; 2 jagged copper and iron shards flying out to both sides (mirrored), a "
     "round billow of chemical GREEN GAS 18 across rising; 3 the gas 30 across and 20 tall, magenta Shimmer splashes "
     "thrown to both sides, a green ring 34 wide and 8 tall on the ground; 4 the gas at its biggest (36 x 26), "
     "shards falling; 5-6 the gas thinning into rolling grey-green puffs; 7 a few last wisps. " + MAGIC + ".",
     row(7, 40, 34) + CENTER),
    ("m_leap", "畸变体：扑到人身上，5 帧", "view_effects `tft_silco_m_leap`（跟随被扑的人，z 3；左右对称）", "22 × 46",
     "一只**畸变体**（参考 `refs/monstrosity_*.png`：一条粗短的紫色蠕虫，前端一张圆嘴、一圈金色尖牙，嘴上面一只发光的粉色小眼睛）"
     "从高处扑下来：圆嘴张开朝下，落到人的头肩上（最后一帧落到头顶的高度，溅开一点紫色黏液）。**正面看，左右对称**；身体位置留空。5 帧。",
     FL + ", " + TE + ", " + SH,
     "A POUNCING MONSTROSITY, 5 frames, " + LR + ", " + TARGET + ": " + GRUB + ", seen from the front, its round mouth "
     "wide open and pointing DOWN; 1 it appears at the top of the cell curled up; 2-3 it drops straight down the middle, "
     "stretching out, the mouth gaping; 4 it lands on the top of the unit's head (the top 12 squares of the cell), a "
     "small splash of violet slime; 5 it squashes down, fangs clamped, slime drops falling at mirrored places. The "
     "middle below the head left empty. " + MAGIC + ".",
     row(5, 22, 46) + CENTER),
    ("m_bite", "畸变体：咬住不放，4 帧循环", "view_effects `tft_silco_m_bite_l`（跟随被咬的人，z 3）；导入时左右翻转一份给 "
     "`tft_silco_m_bite_r`（咬在右边的那只）", "24 × 38",
     "畸变体**咬在人身体的左边**（画面左边、腰和肩之间）：身子挂在人身上、尾巴往外甩，圆嘴咬住人的身侧，一口一口地啃（嘴一张一合、"
     "身子一缩一伸，溅出几滴紫色黏液）。**这一张不对称**：畸变体在左边、嘴朝右（朝着身体）。身体位置留空。4 帧循环。",
     FL + ", " + TE + ", " + SH,
     "A GNAWING MONSTROSITY, 4 looping frames, NOT symmetric, " + TARGET + ": " + GRUB + ", clinging to the LEFT side "
     "of the unit's body between the hip and the shoulder (its mouth at the body's left edge, about 6 squares left of "
     "the middle, its tail curling out to the image left); 1 the mouth wide open; 2 the mouth clamped on, the body "
     "squeezing shorter; 3 the body pulling back, two violet slime drops flying; 4 the mouth opening again. The "
     "middle (the body) left empty, only the grub's mouth overlaps its edge. " + MAGIC + ".",
     row(4, 24, 38) + CENTER),
    ("m_die", "畸变体：化掉，5 帧", "view_effects `tft_silco_m_die`（地面，z 2，不跟随；左右对称）", "18 × 12",
     "畸变体咬完了化成一摊**紫色黏液**：缩成一团、塌下去、在地上冒泡、蒸发成几缕紫烟。**正面看，左右对称**，5 帧。",
     FL + ", " + SH + ", " + SM,
     "A MELTING MONSTROSITY, 5 frames, " + LR + ": on the ground line 2 squares above the bottom. 1 a curled violet "
     "grub 8 squares across seen from the front, its gold fangs showing; 2 it sags and spreads into a violet slime "
     "puddle 12 wide; 3 the puddle 16 wide and 4 tall, bubbles popping, the fangs sinking; 4 the puddle shrinking, "
     "thin purple wisps rising; 5 the last wisps. " + MAGIC + ".",
     row(5, 18, 12) + CENTER),
    ("e_dose", "微光注射：药剂打在队友身上，5 帧", "view_effects `tft_silco_e_dose`（跟随队友，z 3；左右对称）", "20 × 44",
     "希尔科抛来的药剂瓶在队友头顶碎开：洋红的微光液体浇下来，身体两边一下亮起一道道**发光的紫色血管纹**，往上冒一股洋红的蒸汽。"
     "身体位置留空。**左右对称**，5 帧。",
     SH + ", " + CO,
     "A SHIMMER DOSE, 5 frames, " + LR + ", " + TARGET + ": 1 a small vial over the unit's head (the top of the cell) "
     "shattering in a magenta-white flash; 2 glowing magenta liquid pouring down both sides of the body (mirrored); 3 "
     "jagged glowing purple VEIN lines lighting up along both sides of the body like cracks of light, a burst of "
     "magenta vapour rising; 4 the veins at their brightest; 5 the veins fading to thin lines, the vapour drifting up. "
     "The middle (the body) left empty. " + MAGIC + ".",
     row(5, 20, 44) + CENTER),
    ("e_shimmer", "微光注射：药效（攻速、移速加成），6 帧循环", "view_buffs `tft_silco_e_shimmer`（跟随队友，z 3；左右对称）",
     "26 × 42",
     "嗑了微光的人：脚下一圈洋红的光（从斜上方看的椭圆），身体两边一缕缕**洋红的微光蒸汽**往上飘，几颗洋红的光点一闪一闪。"
     "身体位置留空。**左右对称**，6 帧循环。",
     SH,
     "A SHIMMER HIGH, 6 looping frames, " + LR + ", " + TARGET + ": a faint magenta ring " + GROUND_E + " 22 squares "
     "wide and 7 tall, thin wavy wisps of glowing magenta vapour rising on both sides of the body (mirrored) up to the "
     "shoulders, three small magenta sparks; frames 1-6 the wisps flowing upward and the sparks winking in turn. The "
     "middle (the body) left empty. " + MAGIC + ".",
     row(6, 26, 42) + CENTER),
    ("e_crash", "微光注射：药效过去（掉血），5 帧", "view_effects `tft_silco_e_crash`（跟随队友，z 3；左右对称）", "22 × 30",
     "药效过去的那一下：一股**灰紫色的烟**从人身上往下沉、散开，头顶冒两三个灰色的小泡泡（虚脱）。身体位置留空。**左右对称**，5 帧。",
     SM + ", " + SH,
     "A SHIMMER COMEDOWN, 5 frames, " + LR + ", the unit stands in the middle, not drawn (its top 30 squares fill the "
     "cell): 1 a dull purple flash at the chest; 2 a heavy grey-purple smoke sinking down both sides of the body "
     "(mirrored); 3 the smoke pooling at the bottom, two small grey bubbles over the head; 4-5 the smoke and bubbles "
     "fading. The middle (the body) left empty. " + MAGIC + ".",
     row(5, 22, 30) + CENTER),
    ("r_can", "炼金狂潮：飞出去的巨型储罐，4 帧循环", "view_projectiles `tft_silco_r_can`（大表，抛物线弹道，z 2；朝右、上下对称）",
     "22 × 18",
     "大招扔出去的**巨型储罐**：和小储罐一样的样子，大一倍多，铁皮上有铆钉和凹痕，三扇发绿光的玻璃窗，窗里挤着好几条扭动的紫色影子，"
     "罐口漏出绿色的气。**朝右飞，上下对称**，4 帧循环。",
     CO + ", " + CH + ", " + FL,
     "A HUGE THROWN CANISTER, 4 looping frames, " + TB + ": a big riveted, dented metal canister lying along the flight "
     "(18 squares long, 13 tall), iron ends with copper bands, THREE round glowing GREEN windows along its side with "
     "dim violet squirming shapes behind them, green gas leaking from its left end; frames 1-4 the windows pulsing and "
     "the gas streaming back. " + MAGIC + ".",
     row(4, 22, 18) + CENTER),
    ("r_warn", "炼金狂潮：地上的预警圈，6 帧", "view_effects `tft_silco_r_warn`（大表，落点，地面，z -2，不跟随；左右对称）", "60 × 22",
     "巨型储罐要砸下来的地方：地上一圈越来越亮的**绿色危险圈**（从斜上方看的椭圆），圈边一圈黄黑相间的警示条纹，圈里一片绿色的影子慢慢变大。"
     "最大 **横 54 格、纵 18 格**。**左右对称**，6 帧。",
     CH + ", " + SM + ", " + GD,
     "A HAZARD ZONE, 6 frames, " + LR + ", " + GROUND_E + ": 1 a thin chemical green ring 20 squares wide; 2 the ring 36 "
     "wide, a faint green shadow inside it; 3 the ring 54 wide and 18 tall with short yellow-and-black hazard stripes "
     "around its edge, the green shadow filling it; 4-6 the ring brightening, the shadow darkening, little green "
     "bubbles rising from the edge. " + MAGIC + ".",
     row(6, 60, 22) + CENTER),
    ("r_burst", "炼金狂潮：巨型储罐炸开，10 帧", "view_effects `tft_silco_r_burst`（大表，落点，z 3，不跟随；左右对称）", "72 × 60",
     "巨型储罐砸地炸开：一大团**翻滚的绿色化学气体**像蘑菇云一样冲起来，铜铁碎片和洋红的液体往四周飞，地上一圈绿色冲击波，"
     "气体里四条畸变体的影子一闪（畸变体本身是另外的图）。砸的地方在格子底部往上 6 格。**左右对称**，10 帧。",
     CH + ", " + CO + ", " + SH + ", " + SM,
     "A GIANT CHEMICAL BLAST, 10 frames, " + LR + ": the blast sits on the ground line 6 squares above the bottom. 1 a "
     "white-green flash 20 squares across; 2 big copper and iron shards flying out to both sides (mirrored), a billow "
     "of chemical GREEN GAS 30 across rising; 3 the gas 50 across and 34 tall like a mushroom, magenta Shimmer splashes "
     "thrown wide, a green shockwave ellipse 60 wide and 14 tall on the ground; 4 the gas at its biggest (64 x 48), "
     "four dark violet grub silhouettes flashing inside it at mirrored places; 5-6 shards falling, the gas rolling; 7-9 "
     "the gas thinning into grey-green puffs that settle low; 10 low wisps. Frames 3-6 MUST fill 60 squares across. " +
     MAGIC + ".",
     row(10, 72, 60) + CENTER),
    ("r_fog", "炼金狂潮：微光毒雾，6 帧循环", "view_effects `tft_silco_r_fog`（大表，落点，地面，z -2，不跟随，每秒重播一次；左右对称）",
     "84 × 32",
     "巨型储罐炸完后留在地上的**微光毒雾**：一层贴着地面、慢慢翻滚的绿色雾（从斜上方看的椭圆，横约 80 格、纵约 26 格），"
     "雾里夹着几缕洋红的微光，几个绿泡泡冒上来破掉。这一张会**接着重播**（6 帧循环，头尾接得上）。**左右对称**。",
     CH + ", " + SM + ", " + SH,
     "A LINGERING SHIMMER FOG, 6 looping frames (the last flows into the first), " + LR + ", " + GROUND_E + ": a low "
     "layer of rolling chemical green fog filling an ellipse 80 squares wide and 26 tall, its edge made of soft "
     "billows, a few thin magenta Shimmer streaks inside it, small green bubbles rising and popping at mirrored places; "
     "frames 1-6 the billows rolling slowly outward and back, the bubbles rising in turn. Mostly flat shades, its "
     "middle a little thinner so the units standing in it stay readable. " + MAGIC + ".",
     row(6, 84, 32) + CENTER),
    ("r_slow", "炼金狂潮：毒雾里的减速，4 帧循环", "view_buffs `tft_silco_r_slow`（跟随被减速的人，z 3；左右对称）", "20 × 14",
     "站在毒雾里的人：**脚边缠着一圈绿色的雾**，几个小绿泡往上冒。身体位置留空（只画脚下这一截）。**左右对称**，4 帧循环。",
     CH + ", " + SM,
     "A CHOKING FOG AT THE FEET, 4 looping frames, " + LR + ": a band of chemical green fog wrapped round the unit's "
     "feet " + GROUND_E + " 18 squares wide and 6 tall, two small green bubbles rising at mirrored places; frames 1-4 "
     "the fog curling and the bubbles rising. The upper part of the cell empty. " + MAGIC + ".",
     row(4, 20, 14) + CENTER),
    ("p_shield", "统领：护盾，6 帧循环", "view_buffs `tft_silco_p_shield`（跟随他，护盾在就一直在，z 3；左右对称）", "28 × 46",
     "统领的护盾：一层**洋红色的六边形光壳**罩住他（只画外圈的轮廓和几块亮一点的六边形，身体位置留空），光壳上流过一道亮光。"
     "**左右对称**，6 帧循环。",
     SH + ", " + GD,
     "A DOMINATOR'S SHIELD, 6 looping frames, " + LR + ", " + TARGET + ": a tall oval shell of light around the whole "
     "unit (26 squares wide, 44 tall) drawn as a ring of small HEXAGON outlines in glowing magenta, a few hexagons "
     "filled a shade brighter, a thin gold glint; frames 1-6 a bright band sweeping up the shell from the bottom to "
     "the top. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 28, 46) + CENTER),
    ("p_dom", "统领：叠满 5 层，6 帧循环", "view_buffs `tft_silco_d5`（tag p_dom，跟随他，z 4；左右对称）", "16 × 48",
     "统领的法强叠满 5 层：**他头顶上方一只发光的橙红伤疤眼印记**（一只横着的眼睛形状，周围一圈暗紫的裂纹），慢慢一明一暗，"
     "两三缕洋红的微光往上飘。**身体位置留空**，印记在格子最上面 10 格里。**左右对称**，6 帧循环。",
     SH + ", " + GD + ", " + FL,
     "A DOMINATOR'S EYE, 6 looping frames, " + LR + ", " + TARGET + ": over the unit's head (the top 10 squares of the "
     "cell) a glowing ORANGE-RED EYE sigil 8 squares wide and 5 tall seen from the front, ringed by thin dark purple "
     "cracks, two or three thin magenta wisps rising from it at mirrored places; frames 1-6 the eye brightening and "
     "dimming slowly, the wisps rising. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 16, 48) + CENTER),
]
ICONS = [
    ("skill", "技能 1「罐装畸变体」图标", "skill_icons[0] `asset/tft/icons/tft_silco_skill`",
     "一个铁皮储罐裂开，一只畸变体（紫色蠕虫，圆嘴金牙）从绿光里扑出来。",
     ICON + ": a cracked metal CANISTER with copper bands, its glowing green window burst open, a violet MONSTROSITY "
     "grub with a round mouth of gold fangs lunging out of it toward the viewer in a puff of green gas. Colours: " +
     CO + ", " + CH + ", " + FL + ", " + TE + ", " + GD + "."),
    ("skill2", "技能 2「微光注射」图标", "skill_icons[1] `asset/tft/icons/tft_silco_skill2`",
     "一支发洋红光的微光药剂瓶斜放着，瓶口滴下一滴发光的液体，周围几道洋红的蒸汽。",
     ICON + ": a glowing magenta SHIMMER VIAL with a copper cap, tilted, one glowing drop falling from it, wavy magenta "
     "vapour curling around it, two small sparks. Colours: " + SH + ", " + CO + ", " + GD + "."),
    ("ult", "大招「炼金狂潮」图标", "skill_icons[2] `asset/tft/icons/tft_silco_ult`",
     "一个巨型储罐在绿色的化学蘑菇云里炸开，碎片飞出，几只畸变体的影子。",
     ICON + ": a HUGE riveted canister bursting apart in a rising mushroom of chemical GREEN gas, copper shards flying, "
     "two dark violet grub silhouettes in the gas, magenta splashes. Colours: " + CO + ", " + CH + ", " + SH + ", " +
     FL + ", " + GD + "."),
]
BIG_FX = ["q_burst", "r_can", "r_warn", "r_burst", "r_fog"]
FLYING = ["a_vial", "q_can", "r_can"]
ASYM = ["m_bite"]

GROUPS = [
    ("a_vial a_hit e_dose e_shimmer (Shimmer)", ["tft13_silco_base_shimmer", "tft13_renataglasc_base_e_splash_01",
                                                 "tft13_renataglasc_base_e_splat_02", "tft_common_bubble"]),
    ("q_can q_burst r_can r_burst (canisters)", ["drmundo_base_r_chemical_mult",
                                                 "tft13_renataglasc_base_e_bubble_alpha_2",
                                                 "tft_leesin_boom_erosionshapes01", "tft11_udyr_base_impact_flare"]),
    ("m_leap m_bite m_die (monstrosities)", ["sru_horde_base_splashes", "sru_horde_droplets_round",
                                             "sru_horde_mini_base_erosion02_01",
                                             "sru_horde_mini_base_gradient_pinkpurple"]),
    ("r_warn r_fog r_slow e_crash (fog)", ["rumble_skin04_z_oilysmoke_erode", "vex_skin01_e_smokeedge",
                                          "petchibikaisa_skin3_emote_smoke_trail", "tft12_veigar_base_ground_splashes"]),
    ("p_shield p_dom (Dominator)", ["3155_skin04_shield_wipe", "sru_cemtechdragon_circularshape", "tft6_silco_base_ash",
                                    "tft12_galio_base_r_glow"]),
]
MON_REFS = ("monstrosity_35.png", "monstrosity_90.png", "monstrosity_0.png")


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Silco at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x()]
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
    d.text((8, 36), f"希尔科 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 希尔科：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/silco_design.png`："
      "拄着黑手杖、举着微光药剂瓶的祖安化工男爵，往后梳的黑发、橙红伤疤眼，洋红衬衫、金边棕马甲）。"
      f"希尔科在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/silco_size.png`：希尔科缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里希尔科自己的特效贴图（**灰色的形状，游戏里再染色**：微光液体、化学气体、黏液、护盾），"
      "按用在我们哪张特效分好了行；`refs/monstrosity_35.png` / `_90.png` / `_0.png` 是金铲铲里他的**畸变体**模型（一条粗短的紫色蠕虫，"
      "前端一张圆嘴、一圈金色尖牙，嘴上面一只粉色小眼睛）。只在本地用。")
    a("> - **希尔科是祖安的化工男爵，特效都是他的炼金术**：发光的洋红**微光**液体和蒸汽、有毒的**化学绿**气体、凹凸不平的铜铁储罐、"
      "紫色的畸变体；不要光滑的霓虹光束，不要火。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、气体、液体没有黑描边**（畸变体、储罐、药剂瓶这些实物可以有一圈深色描边）。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了弹道和 `m_bite`，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道 `a_vial`、`q_can`、"
      "`r_can` 朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。`m_bite` 是畸变体咬在人的左边，**不对称**（我导入时左右翻转一份当右边那只）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `silco_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `silco_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「统领」 | 每次出生 / 复活得到一层护盾；每放一次技能叠一层法强，叠满 5 层头顶亮起伤疤眼印记 | `p_shield` · `p_dom` |")
    a("| 普攻 | 甩出一支微光药剂瓶 | `a_vial` · `a_hit` |")
    a("| 技能 1 =「罐装畸变体」 | 扔一个储罐，砸地炸开，放出 2 只畸变体扑到附近的敌人身上连咬几口，咬死了就跳到下一个 | `q_can` · `q_warn` · `q_burst` · `m_leap` · `m_bite` · `m_die` |")
    a("| 技能 2 =「微光注射」 | 把药剂瓶抛给身边攻击力最高的队友（没有就自己）：攻速、移速提高，药效过去掉一点血 | `e_dose` · `e_shimmer` · `e_crash` |")
    a("| 大招 =「炼金狂潮」 | 扔一个巨型储罐：地上预警，砸地大爆炸，放出 4 只畸变体，地上留一片减速的微光毒雾 | `r_can` · `r_warn` · `r_burst` · `r_fog` · `r_slow` · `m_*` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、气体、液体没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("微光（洋红）", SHIM), ("化学绿", CHEM), ("铜铁（储罐）", COPPER), ("畸变体的紫色", FLESH),
                        ("畸变体的金牙", TEETH), ("灰绿烟雾", SMOG), ("金色（图标边框）", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆炸居中画，不旋转；地面上的圈（落点、预警圈、冲击圈、毒雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `silco_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, zh, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `silco_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `silco_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `silco_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_silco_fx`（小的）和 `tft_silco_big`（{'、'.join(BIG_FX)}），tag = 名字；"
      "m_bite 切成 m_bite（tag，m_bite_l 用它）和左右翻转的 m_bite_r；p_dom 是 view_buffs 里 d5 的 tag。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；m_bite 不断言；其余断言左右对称。")
    a("- q_warn 在储罐飞行的 q_fall 帧里一直显示、r_warn 在 r_fall 帧里（拉长到那么长）；r_fog 每 60 拍由 tft.dll 重播一次（6 帧放满 60 拍）；"
      "m_bite 每口（m_gap 拍）播一遍。")
    a("- 用 `pixel_1x/` 切格（import_locke_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="silco_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "silco_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    RF.REF, RF.GROUPS = REF, GROUPS
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_silco.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "silco_design.png"))
    shape = size_sheet(os.path.join(out, "design", "silco_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    for name in MON_REFS:
        shutil.copyfile(os.path.join(REF, name), os.path.join(out, "refs", name))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"silco_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "none" if x[0] in ASYM else "left-right"}
                   for x in FX] +
                  ([{"file": f"silco_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
                   if not a.only else []), f, ensure_ascii=False, indent=1)
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
