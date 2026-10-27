#!/usr/bin/env python3
"""Build vander_fx_pack.zip: step 3 of Vander's sprite - Codex draws his effects and his three skill icons
(pack_loris_fx.py's way).

    python tools/lol/fx_ref_vander.py           # his TFT particle textures -> C:/t/vd_work/fxref
    python tools/art/pack_vander_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name vander_fx_redo_pack]

The pack (C:/t/vd_work/fx/vander_fx_pack, zipped into --out, default dist/vander_packs) holds PROMPTS.md (also written
to assets/source/vander/PROMPTS_FX.md), design/vander_design.png (the approved idle at 4x on its own squares),
design/vander_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (his own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_vander.py, the user's picks 2026-10-27:
jungle, plan A 「监察·地下猎犬」): view_effects a_hit, q_guard_in, q_hit, e_dash, e_hit, r_slam, r_hit; view_buffs
q_guard, q_ready, q_taunt, e_stun, r_hold, p_watch. Plus the three skill icons. He throws nothing: no projectile
pictures.
His colours: the BRASS of his gauntlet, the gauntlet's RED panels, a hot IMPACT orange-white, Zaun dust, a TAUNT red,
the Watcher's cold STEEL blue.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture; nothing here points).
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

TMP = "C:/t/vd_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "vander", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "vander", "hd")
NAME = "vander_fx_pack"
PPU = 2.0

BRASS = "#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C"             # his gauntlet's brass frame and bolts
GRED = "#FFD8C8, #FF6A4A, #D8262A, #8E1220, #460812"              # the gauntlet's red panels
IMPACT = "#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C"            # a hot punch impact
DUST = "#F0E2C8, #C8AE88, #9A7E5C, #64503A"                       # Zaun dust and grit
TAUNT = "#FFE4D8, #FF8A6A, #E8382C, #A01822, #4C0A10"            # the taunt red
STEEL = "#F2F8FF, #C8DCEE, #8EAACC, #56709A, #2C3C5C"            # the Watcher's cold steel blue
BS = f"a brass ramp ({BRASS})"
RD = f"a gauntlet red ramp ({GRED})"
IM = f"a hot impact ramp ({IMPACT})"
DS = f"a dust brown ramp ({DUST})"
TR = f"a taunt red ramp ({TAUNT})"
ST = f"a cold steel blue ramp ({STEEL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red "
         "metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, "
         "no smooth neon beams, no fire columns")
HIM = "the broad man stands in the middle, not drawn: 40 squares wide and 40 tall (a low wide fighting stance)"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRASS frame with little riveted "
        "corners, a deep rust-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")
GAUNTLET = ("his IRON GAUNTLET (an octagonal brass frame, two red panels, gold hexagonal bolts, brass knuckle plates, a "
            "purple bracer at the wrist)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：铁拳打中，4 帧", "view_effects `tft_vander_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "拳套砸在人身上：一下白热的闪光，几颗黄铜和红色的火星往两边崩开，一小圈冲击环。**左右对称**，4 帧。",
     IM + ", " + BS,
     "A HEAVY PUNCH IMPACT, 4 frames, " + LR + ": 1 a white-hot star flash 8 squares across; 2 a short orange shock "
     "ring 12 squares wide and 6 tall, brass and red sparks flying out to both sides (mirrored); 3 the ring thinner and "
     "wider, the sparks farther, a puff of dust in the middle; 4 the last dust fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_guard_in", "地下猎犬：跳进防御姿态的一下，5 帧", "view_effects `tft_vander_q_guard_in`（跟随他，z 3；左右对称）", "44 × 48",
     "范德尔放技能 1 时重重一踏摆出防御架势：脚下「咚」地一圈黄铜色冲击环和尘土，身体外面一层**钢蓝色的波纹轮廓**往外一荡（像挡下攻击的气墙），"
     "两边各有一道向上的短光。身体位置留空。**左右对称**，5 帧。",
     ST + ", " + BS + ", " + DS,
     "A FIGHTER DROPPING INTO HIS GUARD, 5 frames, " + LR + ", " + HIM + ": 1 a brass flash " + GROUND_E + " 16 "
     "squares wide; 2 a brass shock ring on the ground 36 squares wide and 10 tall, dust puffs to both sides; 3 a "
     "steel-blue RIPPLE outline (two or three thin wavy lines) bulging out round him, a wide dome 42 squares wide and 44 "
     "tall, short upward streaks at both sides (mirrored); 4 the ripple wider and thinner; 5 fading to a few steel "
     "glints. Only the edges: the middle (the body) left empty. " + MAGIC + ".",
     row(5, 44, 48) + CENTER),
    ("q_guard", "地下猎犬：防御姿态（加双抗），6 帧循环", "view_buffs `tft_vander_q_guard`（跟随他，z 3；左右对称）", "44 × 48",
     "防御姿态还在：他身体两侧各一道**钢蓝色的弧形波纹**（像挡在身前的气墙），慢慢一荡一荡，脚下一圈淡淡的黄铜光圈。"
     "身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。",
     ST + ", " + BS,
     "A HELD GUARD, 6 looping frames, " + LR + ", " + HIM + ": at both sides of him (mirrored) a tall curved steel-blue "
     "RIPPLE arc (two thin wavy lines, 30 squares tall) like a wall of force, and a faint brass ring " + GROUND_E +
     " 34 squares wide and 8 tall at the bottom; frames 1-6 the arcs wavering out and in, a glint running up them. The "
     "middle (the body) left empty. Subtle. " + MAGIC + ".",
     row(6, 44, 48) + CENTER),
    ("q_ready", "地下猎犬：下一拳是重击（蓄着劲），6 帧循环", "view_buffs `tft_vander_q_ready`（跟随他，z 3；左右对称）", "20 × 48",
     "重击还没打出去：他头顶上方一枚小小的**黄铜色拳头徽记**（红色的指节），一跳一跳地发着热光，周围几点橙色火星往上飘。"
     "身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。",
     BS + ", " + RD + ", " + IM,
     "A PUNCH CHARGED, 6 looping frames, " + LR + ", the broad man stands in the middle, not drawn, 40 squares tall: "
     "over the head (the top 10 squares of the cell) a small brass FIST emblem seen from the front, 7 squares wide and "
     "7 tall, red knuckle plates, a white-hot glint, and two or three orange embers drifting up beside it (mirrored); "
     "frames 1-6 the fist throbbing one square bigger and back, the embers rising. The rest of the cell empty. "
     + MAGIC + ".",
     row(6, 20, 48) + CENTER),
    ("q_hit", "地下猎犬：重击打中，6 帧", "view_effects `tft_vander_q_hit`（跟随目标，z 2；左右对称）", "30 × 30",
     "蓄好的那一记重击：一下很大的白热闪光，一个**红铜色的八角形冲击波**（拳套的形状）往外炸开，橙色火星和碎石四溅，留一团尘土。"
     "比普攻狠得多。**左右对称**，6 帧。",
     IM + ", " + RD + ", " + BS + ", " + DS,
     "A CRUSHING GAUNTLET BLOW, 6 frames, " + LR + ": 1 a big white-hot flash 14 squares across; 2 an OCTAGONAL "
     "red-and-brass shock wave (the gauntlet's outline) 16 squares across bursting out, orange sparks flying out to both "
     "sides (mirrored); 3 a wide orange shock ring 28 squares wide and 12 tall, the sparks farther, grit stones; 4 the "
     "ring thin, dust puffs in the middle; 5 the dust spreading; 6 the dust fading. " + MAGIC + ".",
     row(6, 30, 30) + CENTER),
    ("q_taunt", "地下猎犬：被嘲讽（只能打他），6 帧循环", "view_buffs `tft_vander_q_taunt`（跟随被嘲讽的人，z 4；左右对称）", "16 × 44",
     "被嘲讽的人：头顶一个**红色的愤怒标记**（十字形的「青筋」符号），一跳一跳的，脚下一圈淡红色的光圈。身体位置留空。"
     "**左右对称**，6 帧循环。",
     TR + ", " + BS,
     "A TAUNTED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 9 squares of the cell) a red "
     "ANGER MARK (the comic cross-vein symbol: four short curved red strokes in a cross, 7 squares across) with a "
     "brass glint, and a faint red ring " + GROUND_E + " 14 squares wide and 4 tall at the bottom; frames 1-6 the mark "
     "throbbing bigger and smaller, the ring pulsing. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 16, 44) + CENTER),
    ("e_dash", "铁拳突进：起步踢起的尘土，5 帧", "view_effects `tft_vander_e_dash`（留在起跑的地上，z 1；左右对称）", "32 × 14",
     "冲出去那一脚：地上「轰」地踢起一团尘土和碎石，往两边扩散开再落下。留在他起跑的地上（不跟着他），画成圆的，往哪边冲都能用。"
     "**左右对称**，5 帧。",
     DS + ", " + BS,
     "A DASH'S KICK-OFF DUST, 5 frames, " + LR + ": everything " + GROUND_E + ": 1 a burst of dust 10 squares wide "
     "at the bottom middle, two small grit stones flung up to both sides (mirrored); 2 the dust spreading 20 squares "
     "wide and 8 tall, rolling puffs; 3 30 squares wide, the stones falling; 4 thinning; 5 the last thin puffs. "
     + MAGIC + ".",
     row(5, 32, 14) + CENTER),
    ("e_hit", "铁拳突进：上勾拳打中（晕眩），5 帧", "view_effects `tft_vander_e_hit`（跟随目标，z 2；左右对称）", "22 × 32",
     "上勾拳从下往上打中：一道**竖直往上的白热光柱**，橙色和黄铜色的火星呈 V 字往两边上方喷出，脚下一小圈冲击环。**左右对称**，5 帧。",
     IM + ", " + BS + ", " + DS,
     "AN UPPERCUT HIT, 5 frames, " + LR + ": 1 a white-hot flash in the middle 8 squares across; 2 a tall narrow "
     "vertical streak of light shooting UP 24 squares from the middle, orange and brass sparks spraying up and out in a "
     "V to both sides (mirrored), a small shock ring at the bottom 14 squares wide and 4 tall; 3 the streak thinner, "
     "the sparks higher; 4 the sparks falling, dust at the bottom; 5 the last sparks fading. " + MAGIC + ".",
     row(5, 22, 32) + CENTER),
    ("e_stun", "铁拳突进：晕眩，6 帧循环", "view_buffs `tft_vander_e_stun`（跟随被晕的人，z 3；左右对称）", "18 × 44",
     "被打晕的人：头顶上一圈**黄铜色的小星星**和小螺栓绕着转。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。",
     BS + ", " + IM,
     "A STUNNED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 10 squares of the cell) a "
     "flat ring of three small brass STARS and two tiny hexagonal BOLTS (each 3x3 squares) circling round, seen from "
     "the side (an ellipse 14 wide and 4 tall), a tiny white glint; frames 1-6 them moving round the ring (the ones in "
     "front brighter, mirrored positions). The rest of the cell empty. " + MAGIC + ".",
     row(6, 18, 44) + CENTER),
    ("r_slam", "桥头死守：拳套砸地的冲击波，8 帧", "view_effects `tft_vander_r_slam`（大表，留在他脚下的地上，z -1；左右对称）",
     "88 × 30",
     "大招：从半空落下，拳套狠狠砸进地面，**地面炸开一圈很大的冲击波**（从中间往外推的橙红色和黄铜色的环），地上裂开几道裂缝，"
     "碎石和尘土往四周飞，裂缝里透出一点橙红的热光，最后慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（他的脚下）。"
     "**左右对称**，8 帧。",
     IM + ", " + BS + ", " + DS,
     "A GROUND SHOCKWAVE, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell "
     "(his feet): 1 a white-hot flash 16 squares wide; 2 a thick orange shock ring 36 squares wide and 12 tall with a "
     "brass outer edge, CRACKS (dark brown lines 1 square wide) starting out from the middle (mirrored); 3 the ring 58 "
     "wide and 18 tall, the cracks longer, chunks of stone and dust flung up to both sides; 4 the ring 80 wide and 26 "
     "tall, thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the "
     "cracks glowing orange; 7 the cracks dimming; 8 faint cracks and thin dust. " + MAGIC + ".",
     row(8, 88, 30) + CENTER),
    ("r_hit", "桥头死守：被击飞，4 帧", "view_effects `tft_vander_r_hit`（跟随被击飞的人，z 2；左右对称）", "18 × 20",
     "被冲击波掀起来的人：脚下「砰」地一下橙色的闪光，尘土往上喷，两边几颗碎石。**左右对称**，4 帧。",
     IM + ", " + DS,
     "A UNIT THROWN UP, 4 frames, " + LR + ": 1 an orange-white flash at the bottom middle 10 squares wide; 2 a jet of "
     "dust shooting upward 14 squares high, grit stones to both sides (mirrored); 3 the dust spreading and thinning; 4 "
     "the last puffs. " + MAGIC + ".",
     row(4, 18, 20) + CENTER),
    ("r_hold", "桥头死守：死守（减伤），6 帧循环", "view_buffs `tft_vander_r_hold`（跟随他，z 3；左右对称）", "44 × 50",
     "砸地之后范德尔死守在原地：脚下一圈**橙红色的热光圈**，身体两侧有几点**橙色的火星**慢慢往上飘，外面一层很淡的钢蓝色轮廓。"
     "身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。",
     IM + ", " + ST + ", " + BS,
     "A LAST STAND, 6 looping frames, " + LR + ", " + HIM + ": a glowing orange-red ring " + GROUND_E + " 36 squares "
     "wide and 8 tall at the bottom, at both sides of him (mirrored) a few orange EMBERS (1-2 squares) drifting upward "
     "from the ring to his shoulders, and a faint thin steel-blue outline arc at each side; frames 1-6 the embers "
     "rising and new ones starting, the ring breathing. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 44, 50) + CENTER),
    ("p_watch", "监察：减伤（一直在，血多时更强），6 帧循环", "view_buffs `tft_vander_p_watch`（跟随他，z 1；左右对称）", "40 × 12",
     "监察的被动一直挂着，所以**要很淡**：只在他脚下一圈细细的**钢蓝色光圈**，一个亮点沿着光圈慢慢转。不要画在身上。"
     "**左右对称**，6 帧循环。",
     ST,
     "A WATCHER'S CALM GUARD, 6 looping frames, " + LR + ": only a thin steel-blue ring " + GROUND_E + " 34 squares "
     "wide and 8 tall at the bottom of the cell, one square thick; frames 1-6 two bright glints at mirrored places "
     "sliding round the ring. Very subtle: thin, few squares, nothing above the ground. " + MAGIC + ".",
     row(6, 40, 12) + CENTER),
]
ICONS = [
    ("skill", "技能 1「地下猎犬」图标", "skill_icons[0] `asset/tft/icons/tft_vander_skill`",
     "红铜色的大铁拳套竖着举在前面挡住，后面一道钢蓝色的弧形波纹，拳套边上一点白热的光。",
     ICON + ": " + GAUNTLET + " raised upright in front as a guard, filling the middle, a curved steel-blue ripple of "
     "force behind it, a white-hot glint on its knuckles. Colours: " + BS + ", " + RD + ", " + ST + "."),
    ("skill2", "技能 2「铁拳突进」图标", "skill_icons[1] `asset/tft/icons/tft_vander_skill2`",
     "一只缠着绷带的拳头从左下往右上勾出去，后面拖着橙色的速度线和尘土。",
     ICON + ": a big fist wrapped in grey-white bandages driving UP from the lower left to the upper right in an "
     "uppercut, bold orange speed lines and a puff of dust trailing behind it, a white-hot flash at the knuckles. "
     "Colours: " + IM + ", " + DS + "."),
    ("ult", "大招「桥头死守」图标", "skill_icons[2] `asset/tft/icons/tft_vander_ult`",
     "大铁拳套从上往下砸进地面，地面炸开一圈橙红和黄铜色的冲击波，裂缝四散，碎石飞起。",
     ICON + ": " + GAUNTLET + " smashing DOWN into the ground at the centre, an orange-and-brass SHOCKWAVE ring "
     "bursting out flat around it, cracks spreading through the ground, grit stones flying up. Colours: " + BS + ", "
     + RD + ", " + IM + ", " + DS + "."),
]
BIG_FX = ["r_slam"]

GROUPS = [
    ("q_guard_in q_guard r_hold p_watch (the guard)", ["warwick_skin06_temp_p_deflectionbubble",
                                                       "warwick_skin06_temp_p_deflectionripples", "aura_self_128_5",
                                                       "tft13_prime_base_q_cas_decal"]),
    ("a_hit q_hit e_hit r_hit (impacts)", ["hiteffect_128", "sett_base_hit_spark", "yasuo_skin55_animeshapes02_128",
                                          "tft13_kaisa_skin26_glassshapes", "lux_skin07_glow_outer"]),
    ("r_slam e_dash (ground)", ["base_ring_02", "garen_skin22_rock_debris", "sion_skin05_sl_dust_011_256_1",
                                "thresh_base_q_backdrop_64"]),
    ("dust smoke", ["tft13_prime_base_q_smokeerosion02", "smokeerode", "tft_base_erosionshapes01",
                    "petchibiezreal_skin2_finisher_smoke01"]),
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
    """Vander at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"范德尔 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 范德尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/vander_design.png`："
      "祖安地下城的老拳手，往后梳的头发、短络腮胡、焦橙色皮夹克，一只手戴着黄铜框红面板的大铁拳套，屈膝压低的格斗架势）。"
      f"范德尔在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/vander_size.png`：范德尔缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里范德尔自己的特效贴图（**灰色的形状，游戏里再染色**：防御波纹、打击、冲击环、碎石、尘土），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **范德尔是祖安的老拳手，特效都是他的铁拳**：白热的拳光、黄铜和红色的金属火星、厚重的冲击环、祖安的尘土和碎石；"
      "防御姿态和监察是冷冷的钢蓝色波纹，嘲讽是红色的愤怒标记；不要魔法符文，不要光滑的霓虹光束，不要火柱。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、波纹、冲击波、尘土没有黑描边**（拳头徽记、星星、螺栓这些实物可以有一圈深色描边）。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `vander_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `vander_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「监察」 | 一直少受伤害，血量高于一半时减得更多 | `p_watch` |")
    a("| 普攻 | 戴拳套的手抡一记重拳 | `a_hit` |")
    a("| 技能 1 =「地下猎犬」 | 摆出防御姿态，嘲讽身边的敌人，加护甲魔抗；下一拳换成一记重击 | `q_guard_in` · `q_guard` · `q_taunt` · `q_ready` · `q_hit` |")
    a("| 技能 2 =「铁拳突进」 | 冲到敌人身上打一记上勾拳，晕眩，周围的敌人一起挨一部分 | `e_dash` · `e_hit` · `e_stun` |")
    a("| 大招 =「桥头死守」 | 跳进敌群，拳套砸地，冲击波击飞周围的敌人；之后几秒减伤（身边敌人越多减得越多） | `r_slam` · `r_hit` · `r_hold` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、波纹、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("黄铜（拳套框、螺栓、图标边框）", BRASS), ("拳套红", GRED), ("白热拳光", IMPACT), ("尘土", DUST),
                        ("嘲讽红", TAUNT), ("钢蓝（防御、监察）", STEEL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `vander_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `vander_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `vander_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `vander_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_vander_fx`（小的）和 `tft_vander_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- p_watch 由 tft.dll 按血量挂上（一直在）；r_hold 由 tft.dll 在砸地时挂上；q_guard_in 在技能 1 出手时播。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="vander_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "vander_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_vander.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "vander_design.png"))
    shape = size_sheet(os.path.join(out, "design", "vander_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"vander_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"vander_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
