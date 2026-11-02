#!/usr/bin/env python3
"""Build brock_fx_pack.zip: step 3 of Brock's sprite - Codex draws his effects and his three skill icons (the tft
heroes' way).

    python tools/lol/fx_ref_brock.py            # the particle references -> C:/t/br_work/fxref
    python tools/art/pack_brock_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name brock_fx_redo_pack]

The pack (C:/t/br_work/fx/brock_fx_pack, zipped into --out, default D:/TFM2-Workshop/brock_packs) holds PROMPTS.md
(also written to assets/source/brock/PROMPTS_FX.md), design/brock_design.png (the approved idle at 4x on its own
squares), design/brock_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (his own set-16 particle textures and Malphite's, Ornn's and Ivern's - grey
shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds (the user's picks
2026-11-02: top, plan A 「震地猛击」): view_effects a_hit, a_quake, q_hit, e_vine, r_jump, r_slam, r_rock;
view_projectiles q_rock; view_buffs a_up, q_slow, e_root, e_shield, r_hit. Plus the three skill icons.
His colours: the warm amber-orange of his face plate, his slate-teal stone, his brown roots and bright green leaves,
grey-brown dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying boulder is symmetric top to bottom, pointing right.
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

TMP = "C:/t/br_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "brock", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "brock", "hd")
NAME = "brock_fx_pack"
PPU = 1.16

AMBER = "#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C"           # his face plate's glow: the earth's warm light
STONE = "#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647"           # his slate-teal stone, light to dark
ROOT = "#E0A262, #CD8544, #AB6A37, #814A29, #603521"            # his roots and the bark
LEAF = "#D8FF8A, #A1F75C, #5CD14A, #1D8C4E, #0D4A4E"            # his leaves and moss
DUST = "#E2DACA, #B3A992, #7D7464, #4C473E"                     # the dust his slams throw up
AM = f"a warm amber earth-glow ramp ({AMBER})"
ST = f"a slate stone ramp ({STONE})"
RO = f"a root-brown ramp ({ROOT})"
LE = f"a leaf-green ramp ({LEAF})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): "
         "chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, "
         "bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no "
         "smooth neon beams")
HIM = ("the golem stands in the middle, not drawn: about 59 squares wide and 44 tall, upright, his two huge stone fists "
       "hanging wide at his sides, his small hooded head in the middle of the top")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little "
        "amber corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px "
        "a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「震地拳」：石拳砸中，4 帧", "view_effects `tft_brock_a_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "石拳砸中：一下琥珀色的闪光，几块青灰色的碎石和一团尘土往两边崩开。**左右对称**，4 帧。",
     AM + ", " + ST + ", " + DU,
     "A STONE FIST IMPACT, 4 frames, " + LR + ": 1 a pale amber-white flash 5 squares across; 2 a short burst of warm "
     "amber light with four stubby rays, 12 squares across, a few slate stone chips flying out to both sides "
     "(mirrored); 3 the chips falling outward, a low puff of grey-brown dust at the bottom; 4 the last dust and one "
     "falling chip on each side. " + MAGIC + ".",
     row(4, 18, 16) + CENTER),
    ("a_quake", "普攻「震地拳」：周围一圈溅射的震波，5 帧", "view_effects `tft_brock_a_quake`（放在目标脚下的地面上，不跟随，z -1；左右对称）",
     "40 × 14",
     "拳头砸地震出的一小圈震波（目标周围的溅射伤害）：地面上**一圈带短裂缝的震波环**往外推开（从斜上方看的椭圆，宽是高的 3 倍），"
     "裂缝透着琥珀色的光，几块碎石跳起来。**只在地面上**。**左右对称**，5 帧。",
     AM + ", " + ST + ", " + DU,
     "A SMALL GROUND QUAKE RING, 5 frames, " + LR + ": on the GROUND only, seen from above at a slant: 1 a short amber "
     "flash in the middle, 8 squares wide; 2 a thin ring of short jagged cracks glowing amber (an ellipse 22 squares "
     "wide, 7 tall), a few stone chips jumping up along it; 3 the ring 34 squares wide, a little dust rolling out on "
     "both sides (mirrored); 4 the ring at 38 squares and fading, the chips falling; 5 a few dim cracks. The middle "
     "stays clear after frame 1. " + MAGIC + ".",
     row(5, 40, 14) + CENTER),
    ("a_up", "普攻「震地拳」：第三下击飞，4 帧", "view_buffs `tft_brock_a_up`（跟随被击飞的人，脚下，z 3；左右对称）", "22 × 10",
     "每第三下普攻把目标击飞：目标**脚下地面一下拱起、几块碎石和尘土往上蹦**。只在脚下。**左右对称**，4 帧。",
     ST + ", " + DU + ", " + AM,
     "A GROUND JOLT, 4 frames, " + LR + ": low under a unit's feet only (the unit not drawn): 1 a short amber crack "
     "flash on the ground; 2 the ground bulging up in a low stone hump 12 squares wide, small chips and pebbles "
     "jumping up on both sides (mirrored), a puff of dust; 3 the pebbles at their highest, the dust spreading; 4 the "
     "pebbles falling, the last dust. " + MAGIC + ".",
     row(4, 22, 10) + CENTER),
    ("q_rock", "技能 1「巨岩投掷」：飞行的大石头，4 帧循环", "view_projectiles `tft_brock_q_rock`（直线弹道，随飞行方向旋转；上下对称、朝右）",
     "20 × 14",
     "他扔出去的大石头：**一块圆滚滚、缠着两道树根的青灰色大石头**在翻滚着飞（往右飞），后面拖着一小股尘土和两三块小碎石。"
     "**上下对称、朝右**，4 帧循环（翻滚靠石头上的高光和裂纹位置轮换来表现）。",
     ST + ", " + RO + ", " + DU,
     "A FLYING BOULDER, 4 looping frames, " + TB + ": a ROUND slate-teal BOULDER 11 squares across in the right part of "
     "the cell, two brown ROOT bands wrapped round it (mirrored top and bottom), a few dark cracks; behind it on the left "
     "a short trail of grey-brown dust and two small chips (one above, one below, mirrored); frames 1-4 the boulder "
     "tumbling - its light patches and cracks shifting round it in turn (every frame top-bottom symmetric). " + MAGIC + ".",
     row(4, 20, 14) + CENTER),
    ("q_hit", "技能 1「巨岩投掷」：石头砸中碎开，5 帧", "view_effects `tft_brock_q_hit`（跟随目标，z 2；左右对称）", "30 × 22",
     "大石头砸中：一下琥珀色的闪光，**石头碎成好几大块往两边崩开**，一团尘土炸开，几段断掉的树根飞出去。**左右对称**，5 帧。",
     AM + ", " + ST + ", " + RO + ", " + DU,
     "A BOULDER SMASH, 5 frames, " + LR + ": 1 a bright amber-white flash 8 squares across in the middle; 2 the boulder "
     "bursting: five or six big slate stone chunks flying out to both sides (mirrored), a ring of grey-brown dust, two "
     "short broken root pieces spinning out; 3 the chunks further out and falling, the dust cloud 26 squares wide; 4 the "
     "chunks on the ground at the bottom corners, the dust thinning; 5 the last dust. " + MAGIC + ".",
     row(5, 30, 22) + CENTER),
    ("q_slow", "技能 1「巨岩投掷」：减速，6 帧循环", "view_buffs `tft_brock_q_slow`（跟随被减速的人，脚下，z 3；左右对称）", "24 × 8",
     "被减速的人：脚边**几块碎石和一层尘土压着脚**，像被碎石绊住。很淡、只在脚下。**左右对称**，6 帧循环。",
     ST + ", " + DU,
     "RUBBLE AT THE FEET, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): on EACH side "
     "(mirrored) two or three small slate stone chunks and pebbles lying against the ankle line, a faint low dust haze "
     "between them; frames 1-6 the pebbles shifting a square and the dust drifting (every frame left-right symmetric). "
     "Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("e_vine", "技能 2「苔藤缠握」：树根破土而出，6 帧", "view_effects `tft_brock_e_vine`（放在目标脚下的地面上，不跟随，z 2；左右对称）",
     "30 × 30",
     "树根从目标脚下的地里钻出来：地面一下裂开透出琥珀光，**四五根粗壮的棕色树根从两边破土冲上来、往中间弯过来卷住**，"
     "带着几片绿叶和泥土碎块。**中间人站的地方（身体）留空**，树根只到腰。**左右对称**，6 帧。",
     RO + ", " + LE + ", " + AM + ", " + DU,
     "ROOTS BURSTING FROM THE GROUND, 6 frames, " + LR + ": round " + CHAMP + " (only its lower half matters): 1 an "
     "amber crack opening on the ground under its feet (an ellipse 20 squares wide, 6 tall); 2 the tips of four thick "
     "BROWN ROOTS breaking out of the ground, two on each side (mirrored), clods of earth jumping; 3 the roots shooting "
     "up 14 squares, curling inward toward the middle; 4 the roots at their tallest (up to the waist, 18 squares) "
     "hooking over, a few green leaves on them; 5 the roots settling into a cage round the legs; 6 the roots still, the "
     "crack's glow gone. The middle above the knees stays EMPTY. " + MAGIC + ".",
     row(6, 30, 30) + CENTER),
    ("e_root", "技能 2「苔藤缠握」：被树根定住，6 帧循环", "view_buffs `tft_brock_e_root`（跟随被定身的人，腿部，z 3；左右对称）", "24 × 16",
     "被定身的人：**几道棕色树根缠在小腿和脚踝上**（两边各两道，往中间绕），根上冒出两三片绿叶，一点点琥珀光在根缝里闪。"
     "只缠在腿上，上身留空。**左右对称**，6 帧循环。",
     RO + ", " + LE + ", " + AM,
     "ROOTS BINDING THE LEGS, 6 looping frames, " + LR + ": low round a unit's legs only (the unit not drawn, the cell's "
     "bottom is its soles): on EACH side (mirrored) two thick brown roots coming out of the ground and winding inward "
     "round the shins up to 12 squares high, two small green leaves sprouting on them, a few amber glints in the root "
     "cracks; frames 1-6 the roots tightening a square and loosening, the glints moving, the leaves trembling (every "
     "frame left-right symmetric). " + MAGIC + ".",
     row(6, 24, 16) + CENTER),
    ("e_shield", "技能 2「苔藤缠握」：苔石护盾，6 帧循环", "view_buffs `tft_brock_e_shield`（大表，跟随岩宝，z 3；左右对称）", "72 × 54",
     "他自己的护盾：身子外面**一圈长满青苔和小叶子的石板**围成的护壳（竖着的椭圆，只画外圈：一块块青灰石板，石板上铺着绿苔，"
     "石缝里透着琥珀光），叶子一闪一闪轻轻摇。**里面他的身体位置留空**。**左右对称**，6 帧循环。",
     ST + ", " + LE + ", " + AM,
     "A MOSSY STONE SHELL, 6 looping frames, " + LR + ": round " + HIM + ": a ring of STONE PLATES (an upright ellipse "
     "68 squares wide and 50 tall, only its 3-square rim drawn, made of ten slate-teal stone slabs with dark seams), "
     "bright green MOSS and small leaves growing on the slabs, a thin warm amber light line in the seams and along the "
     "inner edge; frames 1-6 the amber seams lighting up in turn round the ring (mirrored pairs) and the leaves swaying "
     "a square (every frame left-right symmetric). INSIDE the ring stays EMPTY (his body). " + MAGIC + ".",
     row(6, 72, 54) + CENTER),
    ("r_jump", "大招「震地猛击」：起跳，5 帧", "view_effects `tft_brock_r_jump`（放在他起跳的地面上，不跟随，z -1；左右对称）", "60 × 16",
     "他蹬地跳起：脚下地面**一下崩出一圈尘土和碎石**，地面裂开几道琥珀色的短缝。**只在地面和低处**。**左右对称**，5 帧。",
     DU + ", " + ST + ", " + AM,
     "A LAUNCH BURST, 5 frames, " + LR + ": on the GROUND and low above it: 1 a short amber crack flash under the feet "
     "(an ellipse 24 squares wide); 2 a puff of grey-brown dust bursting out low to both sides (mirrored), stone chips "
     "and pebbles jumping up, three short amber cracks on the ground; 3 the dust rolling out 50 squares wide, the chips "
     "at their highest; 4 the dust 58 squares wide and thinning, the chips falling; 5 the last dust, the cracks dim. "
     + MAGIC + ".",
     row(5, 60, 16) + CENTER),
    ("r_slam", "大招「震地猛击」：落地猛砸，6 帧", "view_effects `tft_brock_r_slam`（大表，放在他落地砸下的地面上，不跟随，z -1；左右对称）",
     "110 × 44",
     "他从空中砸进地面：一下巨大的琥珀色闪光，地面上**一个很大的震波环**炸开，大块的石板翘起、碎石和尘土往两边飞，"
     "地上留下一圈透着琥珀光的裂缝，几片绿叶被震飞。**只在地面和低处**。**左右对称**，6 帧。",
     AM + ", " + ST + ", " + DU + ", " + LE,
     "A HUGE EARTH SHOCKWAVE, 6 frames, " + LR + ": on the GROUND and low above it, seen from above at a slant: 1 a big "
     "amber-white flash at the middle bottom, 22 squares wide, short rays; 2 a thick bright amber SHOCKWAVE RING "
     "bursting open on the ground (an ellipse 56 squares wide, 18 tall, 3 squares thick), big slate STONE SLABS tilting "
     "up out of the ground on both sides (mirrored), chips and a few green leaves flying; 3 the ring 96 squares wide, a "
     "ring of glowing amber CRACKS left inside it, grey dust billowing out low; 4 the ring at the cell's edge and "
     "thinning, the slabs sinking, the chips falling; 5 the cracks' glow and the settling dust; 6 a few dim cracks. "
     + MAGIC + ".",
     row(6, 110, 44) + CENTER),
    ("r_hit", "大招「震地猛击」：被震飞，5 帧", "view_buffs `tft_brock_r_hit`（跟随被击飞的人，z 3；左右对称）", "22 × 26",
     "被震地猛击击飞的人：脚下**地面一下崩起、几根短石刺冲上来**、一道琥珀光往上喷，碎石往两边飞。**人站的地方留空**。**左右对称**，5 帧。",
     AM + ", " + ST + ", " + DU,
     "AN EARTH ERUPTION, 5 frames, " + LR + ": round " + CHAMP + ": 1 an amber crack flash on the ground under its feet; "
     "2 three short slate STONE SPIKES shooting up beside its feet (one each side, one small in front, mirrored), a "
     "column of warm amber light rising up its sides; 3 the spikes at their tallest (9 squares), chips flying out; 4 the "
     "spikes crumbling, the light fading upward; 5 falling chips and dust. The middle of the cell (its body) stays "
     "EMPTY. " + MAGIC + ".",
     row(5, 22, 26) + CENTER),
    ("r_rock", "大招「震地猛击」：天上落下的石头，7 帧", "view_effects `tft_brock_r_rock`（放在落点的地面上，不跟随，z 2；画面最下面是地面；左右对称）",
     "22 × 52",
     "砸地之后天上掉下来的碎石：**一块青灰色的大石头从格子最上面直直落下来**（后面拖一道短短的尘土尾巴），砸在格子最下面的地上，"
     "碎成几块、一圈尘土炸开、地上一道琥珀色的小裂缝。**左右对称**，7 帧。",
     ST + ", " + DU + ", " + AM,
     "A FALLING ROCK, 7 frames, " + LR + ": the bottom of the cell is the ground: 1 a round slate BOULDER 9 squares across "
     "at the very top of the cell, a short dust streak above it; 2 the boulder a third of the way down, the streak "
     "longer (straight up above it); 3 the boulder two thirds down; 4 the boulder hitting the ground at the bottom, an "
     "amber-white flash under it; 5 the boulder burst into four chunks flying out low to both sides (mirrored), a ring of "
     "dust 20 squares wide, a short amber crack; 6 the chunks on the ground, the dust thinning; 7 the last dust and the "
     "dim crack. " + MAGIC + ".",
     row(7, 22, 52) + CENTER),
]
ICONS = [
    ("skill", "技能 1「巨岩投掷」图标", "skill_icons[0] `asset/tft/icons/tft_brock_skill`",
     ICON + ": a big round slate-teal boulder wrapped in two brown roots flying to the upper right, a trail of grey-brown "
               "dust and chips behind it, a warm amber glint on its edge."),
    ("skill2", "技能 2「苔藤缠握」图标", "skill_icons[1] `asset/tft/icons/tft_brock_skill2`",
     ICON + ": thick brown roots bursting out of a glowing amber crack in the ground and curling up into a grasping hand "
               "shape, small bright green leaves on them."),
    ("ult", "大招「震地猛击」图标", "skill_icons[2] `asset/tft/icons/tft_brock_ult`",
     ICON + ": a huge slate-teal stone fist smashing down into the ground, a bright amber shockwave ring and cracks "
               "bursting out under it, small rocks falling from the top."),
]
BIG_FX = ["e_shield", "r_slam", "r_rock", "r_jump"]
FLYING = ("q_rock",)

GROUPS = [
    ("a_hit q_hit r_hit (the fist, the boulder, the eruption)",
     ["malphite_base_z_sparks", "malphite_base_x_small_stone", "ornn_base_q_hit_flash", "ornn_base_q_hit3_spikes",
      "ornn_base__z_rockdebris"]),
    ("a_quake r_slam r_jump (the ground pounds)",
     ["ornn_base_e_explosion_groundcrack", "ornn_base_r_impact_wave", "tft16_shockwave_01", "malphite_base_r_rock_debris",
      "ornn_base_q_dustcloud"]),
    ("q_rock r_rock (the boulders)",
     ["tft16_ixtal_stone", "tft16_pebbles_2x2", "petstyletwogaren_skin2_vfx_stone", "malphite_base_z_seismicshard",
      "sru_clumps"]),
    ("e_vine e_root e_shield (roots, leaves, the mossy shell)",
     ["ivern_base_q_mis_vines_1x4_test", "ivern_base_thorns2", "ivern_base_r_leaves", "malphite_base_p_shield_circle",
      "malphite_base_p_rocks"]),
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
    """Brock at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"岩宝 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 岩宝：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/brock_design.png`："
      "3/4 朝右、深青灰板岩色的大块头岩石魔像：两只巨大的石拳垂在身体两侧；棕色树根缠满肩膀、手臂和腰；肩上亮绿叶丛和小盆景树；"
      "小头缩在两肩之间：灰蓝石兜帽、发光的橙色脸板、两只黄色圆环眼睛；胸口紫色三角水晶纹章）。"
      f"岩宝在游戏里是**高清**的（每个游戏格子里约 1.16×1.16 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/brock_size.png`：岩宝缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是岩宝自己（金铲铲的碎石、尘土、冲击波）、熔岩巨兽（碎石、石盾）、奥恩（地面裂缝、冲击波、石刺）和艾翁（树根、叶子）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **岩宝是丛林里长满树根和叶子的岩石魔像，特效都是他的味道**：成块的青灰色碎石石板、地面上透着**暖琥珀橙色**光的裂缝、"
      "棕色树根、亮绿叶子、灰褐色的尘土；不要火焰、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了飞行的大石头 `q_rock`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `brock_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `brock_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「岩心不动」 | 不受控制效果影响 | （不用图） |")
    a("| 普攻「震地拳」 | 双拳举过头顶砸下，目标周围一小圈溅射；每第三下把目标短暂击飞 | `a_hit` · `a_quake` · `a_up` |")
    a("| 技能 1 =「巨岩投掷」 | 抡起一块大石头扔向目标：伤害并减速 | `q_rock` · `q_hit` · `q_slow` |")
    a("| 技能 2 =「苔藤缠握」 | 树根从最近的敌人脚下钻出把他定住，自己获得苔石护盾 | `e_vine` · `e_root` · `e_shield` |")
    a("| 大招 =「震地猛击」 | 高高跃起砸进敌群：范围伤害（离落点越远越低），第一次被砸中的敌人被击飞，随后天上落下一阵碎石 | "
      "`r_jump` · `r_slam` · `r_hit` · `r_rock` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("琥珀光（他的脸板、地缝里的光）", AMBER), ("石头（他的青灰板岩）", STONE), ("树根", ROOT), ("叶子和青苔", LEAF), ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `brock_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `brock_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `brock_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `brock_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_brock_fx`（小的）和 `tft_brock_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- q_rock 断言上下对称（朝右），其余断言左右对称。")
    a("- a_quake、r_jump、r_slam 放在地面上（不跟随，z -1）；e_vine、r_rock 放在落点（不跟随）；e_shield 是他身上的 buff；"
      "a_up、q_slow、e_root、r_hit 是敌人身上的 buff；q_rock 是直线弹道。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="brock_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/brock_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_brock.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "brock_design.png"))
    shape = size_sheet(os.path.join(out, "design", "brock_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"brock_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"brock_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
