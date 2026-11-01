#!/usr/bin/env python3
"""Build gromp_fx_pack.zip: step 3 of Gromp's sprite - Codex draws its effects and its three skill icons (the tft
heroes' way).

    python tools/lol/fx_ref_gromp.py            # the particle references -> C:/t/gp_work/fxref
    python tools/art/pack_gromp_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name gromp_fx_redo_pack]

The pack (C:/t/gp_work/fx/gromp_fx_pack, zipped into --out, default D:/TFM2-Workshop/gromp_packs) holds PROMPTS.md
(also written to assets/source/gromp/PROMPTS_FX.md), design/gromp_design.png (the approved idle at 4x on its own
squares), design/gromp_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/tft_fx_ref.png (Kog'Maw's splashes, puddle and fog, Zac's goo, Cassiopeia's poison ring and
shockwaves - grey shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds
(tools/kit/build_gromp.py, the user's picks 2026-11-01: bottom lane, plan A 「打嗝泡泡」): view_projectiles a_spit,
q_bubble, e_glob; view_effects a_hit, q_hit, r_hit, q_burst, e_land, e_pool, r_cast, r_fog (the last five on the big
sheet); view_buffs p_ap, q_poison, e_slow, r_slow. Plus the three skill icons. Its colours: the toxic yellow-green of
its eyes and its poison, the swamp purple of its skin and of Purple Buff, the olive of its belly and its slime.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture), the flying ones top to
bottom, pointing right (turned with their flight).
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

TMP = "C:/t/gp_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "gromp", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "gromp", "hd")
NAME = "gromp_fx_pack"
PPU = 1.69

TOXIC = "#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C"          # its glowing eyes, its poison and bubbles
SWAMP = "#EBD2FF, #B884EE, #8048BE, #4E267C, #261240"          # its purple skin, Purple Buff
SLIME = "#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A"          # its olive belly, the slime
TX = f"a toxic yellow-green ramp ({TOXIC})"
SW = f"a swamp purple ramp ({SWAMP})"
SL = f"an olive slime ramp ({SLIME})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright "
         "highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp "
         "blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams")
HIM = ("the toad sits in the middle, not drawn: about 62 squares wide and 32 tall, a squat fat toad, its round belly and "
       "flat head at the right, the mushrooms on its back at the upper left, its feet on the bottom line of the cell")
UNIT = "a champion 16 squares wide and 36 tall stands in the middle, not drawn, its feet on the bottom line of the cell"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive frame with little "
        "yellow-green corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel "
        "art at 2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_spit", "普攻「毒涎吐射」：飞出去的毒口水，4 帧循环",
     "view_projectiles `tft_gromp_a_spit`（追踪弹道，随飞行方向转；上下对称、朝右）", "12 × 6",
     "一团**黄绿色的毒口水**往右飞：前头圆、后面拖两三滴小水珠，中间一点近白的高光。**上下对称、朝右**，4 帧循环（水团微微抖动）。",
     TX + ", " + SL,
     "A FLYING GOB OF SPIT, 4 looping frames, " + TB + ": a round wet toxic yellow-green GOB 5 squares across at the "
     "right with a near-white highlight square, two or three small droplets trailing behind it to the left in a line "
     "along the middle; frames 1-4 the gob wobbling (round, a little squashed, round, a little stretched) and the "
     "droplets trailing. " + MAGIC + ".",
     row(4, 12, 6) + CENTER),
    ("q_bubble", "技能 1「打嗝泡泡」：飞出去的毒泡泡，4 帧循环",
     "view_projectiles `tft_gromp_q_bubble`（直线弹道，随飞行方向转；上下对称、朝右）", "14 × 12",
     "一个**圆滚滚的毒泡泡**往右飞：泡泡壁是亮黄绿色的一圈，里面一团紫色的毒雾在转，前缘正中一块近白的高光，后面拖两个小泡泡。**上下对称、朝右**，4 帧循环。",
     TX + ", " + SW,
     "A FLYING POISON BUBBLE, 4 looping frames, " + TB + ": a round BUBBLE 10 squares across at the right, its skin a "
     "ring of bright toxic yellow-green, its inside dark green with a swirl of SWAMP PURPLE poison turning in it, a "
     "near-white highlight on the bubble's front edge (on the middle line, so it stays symmetric), two tiny bubbles "
     "trailing behind it to the left; frames 1-4 the purple swirl turning and the bubble wobbling slightly. " + MAGIC + ".",
     row(4, 14, 12) + CENTER),
    ("e_glob", "技能 2「黏液沼泽」：飞出去的一团黏液，4 帧循环",
     "view_projectiles `tft_gromp_e_glob`（抛物线弹道，随飞行方向转；上下对称、朝右）", "12 × 8",
     "一大团**橄榄色的黏液**往右飞：黏糊糊的一坨，前面圆、后面拉出黏丝，表面几个黄绿色的小气泡。**上下对称、朝右**，4 帧循环。",
     SL + ", " + TX,
     "A FLYING GLOB OF SLIME, 4 looping frames, " + TB + ": a big sticky OLIVE SLIME GLOB 7 squares across at the "
     "right, two stringy slime strands stretching back to the left, a few small toxic yellow-green bubbles on its "
     "surface; frames 1-4 the glob wobbling and the strands stretching. " + MAGIC + ".",
     row(4, 12, 8) + CENTER),
    ("a_hit", "普攻：毒口水溅开，4 帧", "view_effects `tft_gromp_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "口水打中：**一团黄绿色的水花溅开**，四周飞出几滴小水珠。**左右对称**，4 帧。",
     TX + ", " + SL,
     "A SPIT SPLAT, 4 frames, " + LR + ": 1 a round yellow-green gob 5 squares across with a near-white core; 2 it "
     "splatting flat into a star-shaped splash 10 squares across; 3 four droplets flying out (two to each side, "
     "mirrored), the splash thinning; 4 the droplets falling, a small olive stain. " + MAGIC + ".",
     row(4, 12, 12) + CENTER),
    ("q_hit", "技能 1：泡泡砸中，5 帧", "view_effects `tft_gromp_q_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "毒泡泡砸在第一个敌人身上：**泡泡一下撑大、啪地破开**，黄绿色的泡泡壁碎成一圈小水珠，中间冒出一团紫色毒雾。**左右对称**，5 帧。",
     TX + ", " + SW,
     "A BUBBLE POPPING, 5 frames, " + LR + ": 1 a round bubble 10 squares across, yellow-green skin, purple swirl "
     "inside; 2 it swelling to 14 squares, the skin stretched thin; 3 POP: the skin bursting into a ring of yellow-green "
     "droplets, a puff of swamp purple poison in the middle; 4 the droplets flying out, the purple puff spreading; 5 the "
     "last droplets and a fading purple wisp. " + MAGIC + ".",
     row(5, 16, 16) + CENTER),
    ("q_burst", "技能 1：泡泡炸开的毒圈，6 帧",
     "view_effects `tft_gromp_q_burst`（大表，放在泡泡停下的地方，不跟随，z 2；左右对称）", "50 × 30",
     "泡泡停下的地方炸开（半径约 25 格内的敌人中毒）：**一圈紫绿色的毒雾往外推开**，地上溅出一圈黄绿色的毒液水花，几个小毒泡泡往上飘。从斜上方看，扁一点。**左右对称**，6 帧。",
     TX + ", " + SW,
     "A POISON BURST, 6 frames, " + LR + ": seen from above at a slant, centred on the bottom middle: 1 a bright "
     "yellow-green flash 8 squares across; 2 a flat RING of swamp purple and toxic green poison mist pushing out, 30 "
     "squares wide and 12 tall, yellow-green splash droplets thrown up round its edge; 3 the ring 46 squares wide, "
     "several small poison bubbles rising out of it; 4 the mist thinning, the bubbles higher; 5 the bubbles popping; 6 "
     "the last purple wisps low on the ground. " + MAGIC + ".",
     row(6, 50, 30) + CENTER),
    ("e_land", "技能 2：黏液落地溅开，5 帧",
     "view_effects `tft_gromp_e_land`（大表，放在落点的地面上，不跟随，z -1；左右对称）", "52 × 20",
     "黏液团砸到地上：**啪地摊开成一大滩**，四周溅起几团黏液，往两边甩出黏丝。从斜上方看。**左右对称**，5 帧。",
     SL + ", " + TX,
     "A SLIME SPLASH, 5 frames, " + LR + ": on the GROUND seen from above at a slant: 1 a glob of olive slime 8 "
     "squares across hitting the bottom middle; 2 it splashing flat, 30 squares wide, thick blobs flying up on both "
     "sides (mirrored); 3 the puddle spreading to 50 squares wide and 12 tall, sticky strands flung out and falling; 4 "
     "the blobs landing round the edge; 5 the puddle settled, a few yellow-green bubbles on it. " + MAGIC + ".",
     row(5, 52, 20) + CENTER),
    ("e_pool", "技能 2：地上的黏液沼泽，6 帧循环",
     "view_effects `tft_gromp_e_pool`（大表，放在地面上，不跟随，z -2，每 0.25 秒重放一次；左右对称）", "52 × 18",
     "地上躺着的一大滩**黏液沼泽**（站进去的敌人被大幅减速）：椭圆形的橄榄色黏液，边缘深、中间亮，表面不停地冒出黄绿色小气泡、啵地破掉。从斜上方看。**左右对称**，6 帧循环（首尾接得上）。",
     SL + ", " + TX,
     "A SLIME SWAMP, 6 looping frames, " + LR + ": on the GROUND seen from above at a slant: a flat OVAL PUDDLE of "
     "sticky olive slime 50 squares wide and 14 tall, darker at the rim and lighter in the middle, a glossy highlight "
     "streak; frames 1-6 small toxic yellow-green bubbles rising, swelling and popping on its surface in turn (placed "
     "mirrored), the last frame running back into the first. " + MAGIC + ".",
     row(6, 52, 18) + CENTER),
    ("r_cast", "大招「毒沼大嗝」：打嗝的冲击，6 帧", "view_effects `tft_gromp_r_cast`（大表，跟随它，z 3；左右对称）", "84 × 44",
     "它仰头打出大嗝的一下：**围着它的身子炸开一圈黄绿色的冲击波**，紫色的毒孢子往四周喷出去。**它的身体位置留空**。**左右对称**，6 帧。",
     TX + ", " + SW,
     "A BIG BELCH SHOCKWAVE, 6 frames, " + LR + ": round " + HIM + ": 1 a few yellow-green flecks at the top of its "
     "outline; 2 a flat oval SHOCKWAVE RING of toxic yellow-green bursting out round its body at mid height, 70 squares "
     "wide; 3 the ring at the cell's width, swamp purple poison SPORES spraying out from it to both sides (mirrored); 4 "
     "the ring breaking into arcs, the spores drifting; 5 the arcs fading, purple puffs hanging; 6 the last spores. The "
     "middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 84, 44) + CENTER),
    ("r_hit", "大招：毒雾喷中，5 帧", "view_effects `tft_gromp_r_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "大嗝喷中：**一团紫绿色的毒雾糊在身上**，溅出几点黄绿色的毒液，两个小泡泡冒出来破掉。**左右对称**，5 帧。",
     TX + ", " + SW,
     "A POISON BLAST HIT, 5 frames, " + LR + ": 1 a yellow-green flash 6 squares across; 2 a cloud of swamp purple "
     "and toxic green poison 14 squares across puffing out, yellow-green droplets to both sides (mirrored); 3 the cloud "
     "rolling, two small bubbles rising in it; 4 the bubbles popping, the cloud thinning; 5 the last purple wisps. "
     + MAGIC + ".",
     row(5, 18, 16) + CENTER),
    ("r_fog", "大招：留在地上的毒雾，6 帧循环",
     "view_effects `tft_gromp_r_fog`（大表，放在瞄准的地方，不跟随，z 3，每 0.25 秒重放一次；左右对称）", "64 × 40",
     "大嗝喷出去后留在地上的**一大片毒雾**（站在里面持续掉血）：低低的紫绿色雾团一团一团地翻滚，里面飘着黄绿色的毒孢子和小泡泡。从斜上方看，下面浓、上面淡。**左右对称**，6 帧循环（首尾接得上）。",
     SW + ", " + TX,
     "A LINGERING POISON CLOUD, 6 looping frames, " + LR + ": a low wide cloud of rolling swamp purple and toxic "
     "green MIST lumps, 60 squares wide, thick near the ground and thinning upward to 36 squares high, toxic "
     "yellow-green SPORES and small bubbles drifting up through it; frames 1-6 the lumps rolling and the spores "
     "rising (placed mirrored), the last frame running back into the first. Soft-edged lumps but still blocky pixel "
     "art. " + MAGIC + ".",
     row(6, 64, 40) + CENTER),
    ("p_ap", "被动「紫霸符」：叠法强的紫色符文，6 帧循环", "view_buffs `tft_gromp_p_ap`（跟随它，z 3；左右对称）", "70 × 50",
     "紫霸符（战斗里每 4 秒叠一层法强）：它**背上方飘着一个紫色的发光符文**（像峡谷 buff 那样的一圈，但是紫色），慢慢转，周围几点紫色小火星往上飘。**它的身体位置留空**。**左右对称**，6 帧循环。",
     SW,
     "PURPLE BUFF, 6 looping frames, " + LR + ": round " + HIM + ": above its back, in the top middle of the cell, a "
     "glowing SWAMP PURPLE RUNE 14 squares across (a ring with four short spikes, like a jungle buff's crest, seen "
     "slightly from above), near-white at its core; a few small purple sparks rising round its body's outline; frames "
     "1-6 the rune slowly turning (its spikes stepping round, every frame left-right symmetric) and pulsing, the sparks "
     "drifting up. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 70, 50) + CENTER),
    ("q_poison", "技能 1：中毒的敌人身上冒泡，6 帧循环", "view_buffs `tft_gromp_q_poison`（跟随中毒的人，z 3；左右对称）",
     "20 × 40",
     "中了打嗝泡泡的毒：**身子两边冒出黄绿色的小毒泡泡**一个个往上飘、破掉，头顶一缕紫色毒烟。**身体位置留空**。**左右对称**，6 帧循环。",
     TX + ", " + SW,
     "POISONED, 6 looping frames, " + LR + ": round " + UNIT + ": small toxic yellow-green BUBBLES (1x1 to 3x3 "
     "squares, each with a near-white highlight) rising along both sides of its outline (mirrored) and popping near the "
     "top, a thin swamp purple wisp above its head; frames 1-6 the bubbles rising and popping in turn. The middle of "
     "the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 20, 40) + CENTER),
    ("e_slow", "技能 2：被黏住减速，6 帧循环", "view_buffs `tft_gromp_e_slow`（跟随被减速的人，z 3；左右对称）", "24 × 10",
     "陷在黏液里：**脚下一圈黏糊糊的橄榄色黏液**，两边拉起几根黏丝粘在脚上，偶尔冒个泡。**只在脚下**。**左右对称**，6 帧循环。",
     SL + ", " + TX,
     "STUCK IN SLIME, 6 looping frames, " + LR + ": at the bottom of the cell round a unit's feet (the feet 8 squares "
     "apart in the middle, not drawn): a flat oval of sticky olive slime 22 squares wide and 4 tall, slime strings "
     "stretching up 4 squares on both sides (mirrored) as if clinging to the feet, one small yellow-green bubble; "
     "frames 1-6 the strings stretching and sagging, the bubble rising and popping. " + MAGIC + ".",
     row(6, 24, 10) + CENTER),
    ("r_slow", "大招：毒雾减速，6 帧循环", "view_buffs `tft_gromp_r_slow`（跟随被减速的人，z 3；左右对称）", "24 × 24",
     "被大嗝的毒雾喷中减速：**身子周围缠着几缕紫绿色的毒雾**慢慢绕圈，飘着几点黄绿色的孢子。**身体位置留空**。**左右对称**，6 帧循环。",
     SW + ", " + TX,
     "CHOKED BY POISON, 6 looping frames, " + LR + ": round a unit standing in the middle (16 squares wide, its lower "
     "body in this cell, not drawn): two thin wisps of swamp purple and toxic green mist curling round its legs and "
     "waist on both sides (mirrored), a few yellow-green spores floating; frames 1-6 the wisps curling round and the "
     "spores drifting. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 24, 24) + CENTER),
]
ICONS = [
    ("skill", "技能 1「打嗝泡泡」图标", "skill_icons[0] `asset/tft/icons/tft_gromp_skill`",
     ICON + ": an orange-headed toad's wide open mouth at the lower left belching a big round toxic yellow-green "
               "BUBBLE with a purple swirl inside toward the upper right, small bubbles trailing."),
    ("skill2", "技能 2「黏液沼泽」图标", "skill_icons[1] `asset/tft/icons/tft_gromp_skill2`",
     ICON + ": a big splash of sticky olive slime spread on the ground, slime strings and yellow-green bubbles, a "
               "small footprint stuck in it."),
    ("ult", "大招「毒沼大嗝」图标", "skill_icons[2] `asset/tft/icons/tft_gromp_ult`",
     ICON + ": a huge fat toad with an olive belly blown up round and a flat orange head with glowing yellow-green "
               "eyes, mouth wide open, a wave of purple-green poison mist bursting out of it."),
]
BIG_FX = ["q_burst", "e_land", "e_pool", "r_cast", "r_fog"]
FLYING = ("a_spit", "q_bubble", "e_glob")

GROUPS = [
    ("a_spit q_bubble e_glob a_hit q_hit (the spit, the bubble, the splats)",
     ["kogmaw_base_splash_2x2_pink", "zac_goo_02", "zac_goo_03", "kogmaw_base_w_bitsdissolve_01",
      "kogmaw_base_lantern_ring_01"]),
    ("q_burst r_cast r_hit (the bursts)",
     ["common_shockwave", "kogmaw_skin05_z_concentricrings", "cassiopeia_base_p_dc_ceremony_poisonring_pulse",
      "aatrox_base_p_smokeerode"]),
    ("e_land e_pool e_slow (the slime)",
     ["zac_goo_e_pool", "kogmaw_base_r_floor_puddle_erode", "zac_goo_e", "zac_blob_health"]),
    ("r_fog q_poison r_slow p_ap (the clouds, the poison, Purple Buff)",
     ["kogmaw_base_fog", "kogmaw_base_w_buff_smoke", "kogmaw_base_w_electric_arcs", "kalista_skin01_p_glow"]),
]


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
    """The toad at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"魔沼蛙 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 魔沼蛙：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定，见 `design/gromp_design.png`：")
    a(">   - 3/4 朝右、蹲着的**大胖蛤蟆**；")
    a(">   - 前面一个又圆又鼓的**橄榄褐大肚子**，橙色的扁头压在上面；")
    a(">   - **发黄绿色光的眼睛**、两根淡黄獠牙；")
    a(">   - 深紫色疙瘩皮，背上一丛紫色和蓝色的大蘑菇。")
    a(f">\n> 魔沼蛙在游戏里是**高清**的（每个游戏格子里约 {PPU}×{PPU} 个细像素），{h} 格高、{w} 格宽（高×宽）。"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/gromp_size.png`：魔沼蛙缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是大嘴（水花、地上的水洼、毒雾）、扎克（黏液）、卡西奥佩娅（毒圈）和冲击波的特效贴图。"
      "这些是**灰色的形状，游戏里再染色**，已经按用在我们哪张特效分好了行。只在本地用。")
    a("> - **魔沼蛙是峡谷里的大蛤蟆，特效都是它的味道**：湿乎乎的口水和黏液、圆滚滚带高光的毒泡泡、像它眼睛一样的**黄绿色毒**、"
      "**沼泽紫**的毒雾和孢子、橄榄色的黏液。不要闪电、不要光滑的霓虹光束；只有紫霸符那一个符文。")
    a("> - **特效要亮**：每个光都有最亮一档或近白的芯，暗底上一眼能看见。**光、雾、水花没有黑描边**。")
    a("> - **围着它的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住它。")
    a(f"> - **对称**：飞行的三张（{'、'.join(FLYING)}）**上下对称、朝右**（游戏按飞行方向转）；其余所有画面都**严格左右对称**"
      "（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 交付方式：")
    a(">   - 每张生成后按格子取回（每格取多数颜色）。")
    a(">   - 交付 8 倍的 `gromp_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。")
    if n_ic:
        a(">   - 图标交付 `gromp_icon_<名字>.png`（64×64）。")
    a(">   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。")
    a(f">   - 都放在 `outputs/{NAME.replace('_pack', '')}/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。")
    a(">   - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「毒涎吐射」 | 远程吐毒口水 | `a_spit` · `a_hit` |")
    a("| 被动「紫霸符」 | 战斗里每 4 秒叠一层法强，有上限 | `p_ap` |")
    a("| 技能 1 =「打嗝泡泡」 | 吐一个毒泡泡，碰到第一个敌人炸开，周围一圈中毒 | `q_bubble` · `q_hit` · `q_burst` · `q_poison` |")
    a("| 技能 2 =「黏液沼泽」 | 往敌人脚下吐一滩黏液，站进去大幅减速 | `e_glob` · `e_land` · `e_pool` · `e_slow` |")
    a("| 大招 =「毒沼大嗝」 | 仰头鼓肚子变大，打一个大嗝：前方扇形毒雾伤害减速，毒雾留在地上 | "
      "`r_cast` · `r_hit` · `r_fog` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、水花没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("毒绿（眼睛、毒、泡泡）", TOXIC), ("沼泽紫（皮肤、毒雾、紫霸符）", SWAMP),
                        ("黏液橄榄（肚子、黏液）", SLIME)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中的画面居中画，不旋转；地面上的水花、水洼、毒雾是从斜上方看的扁平一团。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `gromp_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `gromp_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `gromp_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `gromp_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_gromp_fx`（小的）和 `tft_gromp_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- a_spit 是普攻的追踪弹道，q_bubble 是不穿透的直线弹道（停下时放 q_burst），e_glob 是抛物线；a_hit、q_hit、r_hit 在被打中的人身上；"
      "q_burst、e_land、e_pool、r_fog 放在地面上（不跟随）；r_cast 跟随它；p_ap 是 tft.dll 叠的法强 buff；q_poison、e_slow、r_slow 在敌人身上。")
    a("- 用 `pixel_1x/` 切格（import_raptor_fx 的做法，改成 import_gromp_fx）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="gromp_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/gromp_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_gromp.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "gromp_design.png"))
    shape = size_sheet(os.path.join(out, "design", "gromp_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"gromp_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"gromp_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
