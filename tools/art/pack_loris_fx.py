#!/usr/bin/env python3
"""Build loris_fx_pack.zip: step 3 of Loris's sprite - Codex draws his effects and his three skill icons
(pack_maddie_fx.py's way).

    python tools/lol/fx_ref_loris.py            # his TFT particle textures -> C:/t/lo_work/fxref
    python tools/art/pack_loris_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name loris_fx_redo_pack]

The pack (C:/t/lo_work/fx/loris_fx_pack, zipped into --out, default dist/loris_packs) holds PROMPTS.md (also written
to assets/source/loris/PROMPTS_FX.md), design/loris_design.png (the approved idle at 4x on its own squares),
design/loris_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (his own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_loris.py, the user's picks 2026-10-27: support,
plan A 「神盾使·皮城争斗」): view_effects a_hit, q_shield, q_dash, q_hit, e_land, r_slam, r_hit and tft.dll's p_burst;
view_buffs q_stun, e_guard, r_taunt, r_wall, p_shield. Plus the three skill icons. He throws nothing: no projectile
pictures.
His colours: the BRONZE-GOLD of his shield, Piltover HEXTECH CYAN (the gem on his shield), the pale blue-white of a
SHIELD barrier, a TAUNT red, dust brown.
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

TMP = "C:/t/lo_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "loris", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "loris", "hd")
NAME = "loris_fx_pack"
PPU = 2.0

BRONZE = "#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810"            # his shield's bronze-gold
HEX = "#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A"              # Piltover hextech cyan (the gem on his shield)
BARRIER = "#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8"          # a shield barrier's pale blue-white
TAUNT = "#FFE4D8, #FF8A6A, #E8382C, #A01822, #4C0A10"            # the taunt red
DUST = "#F0E2C8, #C8AE88, #9A7E5C, #64503A"                       # dust and grit
BZ = f"a bronze-gold ramp ({BRONZE})"
HX = f"a hextech cyan ramp ({HEX})"
BR = f"a shield-barrier blue-white ramp ({BARRIER})"
TR = f"a taunt red ramp ({TAUNT})"
DS = f"a dust brown ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan "
         "energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit "
         "where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams")
HIM = "the broad man stands in the middle, not drawn: 22 squares wide and 42 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little riveted "
        "corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：盾击打中，4 帧", "view_effects `tft_loris_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "巨盾砸在人身上：一下白色的闪光，几块铜色的碎光往两边崩开，一小圈冲击环。**左右对称**，4 帧。",
     BZ + ", " + DS,
     "A HEAVY SHIELD BASH IMPACT, 4 frames, " + LR + ": 1 a white star flash 8 squares across; 2 a short bronze shock "
     "ring 12 squares wide and 6 tall, bronze chips flying out to both sides (mirrored); 3 the ring thinner and wider, "
     "the chips farther, a little dust in the middle; 4 the last dust fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_shield", "皮城争斗：身上亮起护盾，6 帧", "view_effects `tft_loris_q_shield`（跟随他，z 3；左右对称）", "32 × 52",
     "洛里斯放技能 1 时身上「嗡」地亮起一层**蓝白色的六边形护盾**：从胸前的一点光往外张开成一个包住全身的竖椭圆，"
     "六边形的格子一闪一闪地拼上去，最后只剩一圈淡淡的外轮廓。身体位置留空（只画外圈）。**左右对称**，6 帧。",
     BR + ", " + HX + ", " + BZ,
     "A SHIELD BARRIER SNAPPING ON, 6 frames, " + LR + ", " + HIM + ": 1 a small cyan-white spark at his chest; 2 a "
     "ring of light bursting out from it; 3 a tall upright ellipse 30 squares wide and 50 tall around him, its edge "
     "made of pale blue-white HEXAGON tiles (each 3-4 squares), a few tiles bright; 4 the hexagon tiles lighting in a "
     "wave from the bottom to the top (mirrored); 5 the whole edge bright, a bronze glint at the top; 6 settling to a "
     "thin pale outline. Only the outer edge: the middle (the body) left empty. " + MAGIC + ".",
     row(6, 32, 52) + CENTER),
    ("q_dash", "皮城争斗：冲锋起步踢起的尘土，5 帧", "view_effects `tft_loris_q_dash`（留在起跑的地上，z 1；左右对称）", "32 × 14",
     "冲锋起步那一脚：地上「轰」地踢起一团尘土和碎石，往两边扩散开再落下。留在他起跑的地上（不跟着他），画成圆的，"
     "往哪边冲都能用。**左右对称**，5 帧。",
     DS + ", " + BZ,
     "A CHARGE'S KICK-OFF DUST, 5 frames, " + LR + ": everything " + GROUND_E + ": 1 a burst of dust 10 squares wide "
     "at the bottom middle, two small grit stones flung up to both sides (mirrored); 2 the dust spreading 20 squares "
     "wide and 8 tall, rolling puffs; 3 30 squares wide, the stones falling; 4 thinning; 5 the last thin puffs. "
     + MAGIC + ".",
     row(5, 32, 14) + CENTER),
    ("q_hit", "皮城争斗：冲锋撞中（击退 + 晕眩），5 帧", "view_effects `tft_loris_q_hit`（跟随被撞的人，z 2；左右对称）", "24 × 24",
     "巨盾冲锋撞中：一下大大的白色闪光，铜色的盾形冲击波往两边炸开，青蓝色的电火花四溅，留一点尘土。比普攻更狠。**左右对称**，5 帧。",
     BZ + ", " + HX + ", " + DS,
     "A SHIELD CHARGE SLAMMING INTO A UNIT, 5 frames, " + LR + ": 1 a big white flash 12 squares across; 2 a bronze "
     "shock wave in the shape of the shield's outline (a tall shape 10 wide and 16 tall) bursting out, hextech cyan "
     "sparks flying out to both sides (mirrored); 3 a wide bronze shock ring 22 squares wide and 10 tall, the sparks "
     "farther; 4 the ring thin, dust puffs in the middle; 5 the dust fading. " + MAGIC + ".",
     row(5, 24, 24) + CENTER),
    ("q_stun", "皮城争斗：晕眩，6 帧循环", "view_buffs `tft_loris_q_stun`（跟随被晕的人，z 3；左右对称）", "18 × 44",
     "被撞晕的人：头顶上一圈**铜金色的小星星**和小齿轮绕着转。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。",
     BZ + ", " + HX,
     "A STUNNED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 10 squares of the cell) a "
     "flat ring of three small bronze-gold STARS and two tiny GEARS (each 3x3 squares) circling round, seen from the "
     "side (an ellipse 14 wide and 4 tall), a tiny cyan glint; frames 1-6 them moving round the ring (the ones in "
     "front brighter, mirrored positions). The rest of the cell empty. " + MAGIC + ".",
     row(6, 18, 44) + CENTER),
    ("e_land", "盾卫：落到队友身边，两人得到护盾，6 帧", "view_effects `tft_loris_e_land`（跟随被守护的队友，z 3；左右对称）", "34 × 46",
     "洛里斯冲到队友身边、把盾往地上一立：地上「咚」地一圈**铜色的冲击环**，接着一面**淡蓝白色的六边形护盾**从地面往上升，"
     "包住被守护的队友，最后变成一圈淡淡的光。身体位置留空。**左右对称**，6 帧。",
     BZ + ", " + BR + ", " + HX,
     "A GUARD LANDING, 6 frames, " + LR + ", " + TARGET + ": 1 a bronze impact flash " + GROUND_E + " 14 squares "
     "wide; 2 a bronze shock ring on the ground 30 squares wide and 8 tall, dust to both sides; 3 a pale blue-white "
     "wall of HEXAGON tiles rising from the ring around the unit, as high as its waist; 4 the hexagon wall reaching "
     "over its head, a bright cyan gem glint at the top; 5 the wall bright; 6 settling to a thin pale outline. Only "
     "the edges: the middle (the body) left empty. " + MAGIC + ".",
     row(6, 34, 46) + CENTER),
    ("e_guard", "盾卫：被守护中（替他承受伤害），6 帧循环", "view_buffs `tft_loris_e_guard`（跟随被守护的队友，z 3；左右对称）",
     "20 × 44",
     "被洛里斯守护的队友：头顶上方一枚小小的**铜金色盾牌徽章**（中间一点青蓝），脚下一圈淡淡的蓝色光圈，慢慢一明一暗。"
     "身体位置留空。**左右对称**，6 帧循环。",
     BZ + ", " + HX + ", " + BR,
     "A GUARDED ALLY, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 9 squares of the cell) a "
     "small bronze TOWER SHIELD badge 6 squares wide and 8 tall with a cyan dot in its middle, and a faint pale blue "
     "ring " + GROUND_E + " 16 squares wide and 4 tall at the bottom; frames 1-6 the badge bobbing one square and "
     "glinting, the ring breathing. The middle (the body) left empty. Subtle. " + MAGIC + ".",
     row(6, 20, 44) + CENTER),
    ("r_slam", "钢铁防线：巨盾砸地的冲击波，8 帧", "view_effects `tft_loris_r_slam`（大表，留在他脚下的地上，z -1；左右对称）",
     "84 × 30",
     "大招：巨盾狠狠砸进地里，**地面炸开一圈很大的冲击波**（从中间往外推的铜色和青蓝色的环），地上裂开几道裂缝，尘土和碎石往四周飞，"
     "最后裂缝慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（他的脚下）。**左右对称**，8 帧。",
     BZ + ", " + HX + ", " + DS,
     "A GROUND SHOCKWAVE, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell "
     "(his feet): 1 a white-bronze flash 16 squares wide; 2 a thick bronze shock ring 36 squares wide and 12 tall with "
     "a hextech cyan inner edge, CRACKS (dark brown lines 1 square wide) starting out from the middle (mirrored); 3 the "
     "ring 56 wide and 18 tall, the cracks longer, dust and grit flung up to both sides; 4 the ring 76 wide and 26 tall, "
     "thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the cracks "
     "glowing cyan; 7 the cracks dimming; 8 faint cracks and thin dust. " + MAGIC + ".",
     row(8, 84, 30) + CENTER),
    ("r_hit", "钢铁防线：被击飞，4 帧", "view_effects `tft_loris_r_hit`（跟随被击飞的人，z 2；左右对称）", "18 × 20",
     "被冲击波掀起来的人：脚下「砰」地一下铜色的闪光，尘土往上喷，两边几颗碎石。**左右对称**，4 帧。",
     BZ + ", " + DS,
     "A UNIT THROWN UP, 4 frames, " + LR + ": 1 a bronze-white flash at the bottom middle 10 squares wide; 2 a jet of "
     "dust shooting upward 14 squares high, grit stones to both sides (mirrored); 3 the dust spreading and thinning; 4 "
     "the last puffs. " + MAGIC + ".",
     row(4, 18, 20) + CENTER),
    ("r_taunt", "钢铁防线：被嘲讽（只能打他），6 帧循环", "view_buffs `tft_loris_r_taunt`（跟随被嘲讽的人，z 4；左右对称）", "16 × 44",
     "被嘲讽的人：头顶一个**红色的愤怒标记**（一个十字形的「青筋」符号），一跳一跳的，脚下一圈淡红色的光圈。身体位置留空。"
     "**左右对称**，6 帧循环。",
     TR + ", " + BZ,
     "A TAUNTED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 9 squares of the cell) a red "
     "ANGER MARK (the comic 'cross vein' symbol: four short curved red strokes in a cross, 7 squares across) with a "
     "bronze glint, and a faint red ring " + GROUND_E + " 14 squares wide and 4 tall at the bottom; frames 1-6 the mark "
     "throbbing bigger and smaller, the ring pulsing. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 16, 44) + CENTER),
    ("r_wall", "钢铁防线：钢铁之躯（减伤），6 帧循环", "view_buffs `tft_loris_r_wall`（跟随他，z 3；左右对称）", "34 × 50",
     "大招后洛里斯减伤：身体两侧各有两三块**铜色的六边形装甲片**慢慢上下浮动，边上带一点青蓝光；脚下一圈铜色的光圈。"
     "身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。",
     BZ + ", " + HX,
     "AN IRON STANCE, 6 looping frames, " + LR + ", " + HIM + ": at both sides of him (mirrored) three bronze HEXAGON "
     "ARMOUR PLATES (each 5 squares across, a cyan rim) floating at his shoulder, waist and knee height, and a bronze "
     "ring " + GROUND_E + " 26 squares wide and 6 tall at the bottom; frames 1-6 the plates bobbing up and down one "
     "square in turn, a glint running along them. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 34, 50) + CENTER),
    ("p_shield", "神盾使：护盾在身（跟着护盾一起消失），6 帧循环", "view_buffs `tft_loris_p_shield`（跟随他，z 3；左右对称）", "30 × 50",
     "神盾使给的护盾还在：他外面一层**很淡的蓝白色六边形护盾轮廓**（竖椭圆），上面偶尔有一两格六边形亮一下。不要太显眼。"
     "身体位置留空（只画外圈）。**左右对称**，6 帧循环。",
     BR + ", " + HX,
     "A SHIELD BARRIER HOLDING, 6 looping frames, " + LR + ", " + HIM + ": a faint thin upright ellipse 28 squares wide "
     "and 48 tall around him, its edge a line of pale blue-white HEXAGON tiles; frames 1-6 one or two tiles at mirrored "
     "places lighting up brighter in turn, a soft glint running round. Subtle: thin, few squares. The middle (the body) "
     "left empty. " + MAGIC + ".",
     row(6, 30, 50) + CENTER),
    ("p_burst", "神盾使：血量掉到 75% / 25% 时触发护盾，6 帧", "view_effects `tft_loris_p_burst`（跟随他，z 3；左右对称）", "34 × 52",
     "神盾使触发：他身前「当」地一下亮出一枚**大大的铜金色盾牌徽章**（中间一颗青蓝宝石），徽章碎成光点散开，变成一圈蓝白色的六边形护盾包住他。"
     "身体位置留空（徽章只在前两帧挡一下胸口，之后散开）。**左右对称**，6 帧。",
     BZ + ", " + HX + ", " + BR,
     "A WARDEN'S SHIELD BURSTING ON, 6 frames, " + LR + ", " + HIM + ": 1 a big bronze TOWER SHIELD EMBLEM 12 squares "
     "wide and 16 tall with a glowing cyan gem, flashing over his chest; 2 it rings bright white at the edges; 3 it "
     "shatters into bronze and cyan sparks flying out to both sides (mirrored); 4 the sparks join into a tall upright "
     "ellipse of pale blue-white HEXAGON tiles 32 wide and 50 tall around him; 5 the whole ellipse bright; 6 settling "
     "to a thin outline. After frame 2 the middle (the body) left empty. " + MAGIC + ".",
     row(6, 34, 52) + CENTER),
]
ICONS = [
    ("skill", "技能 1「皮城争斗」图标", "skill_icons[0] `asset/tft/icons/tft_loris_skill`",
     "一面铜金色的巨盾正面朝右前方猛冲过来，盾后面拖着几道速度线和尘土，盾边亮着蓝白色的护盾光。",
     ICON + ": a big bronze TOWER SHIELD (navy panels, a cyan gem in a star emblem) charging forward toward the lower "
     "right, a pale blue-white barrier glow along its rim, bold speed lines and dust trailing behind it to the upper "
     "left. Colours: " + BZ + ", " + HX + ", " + BR + "."),
    ("skill2", "技能 2「盾卫」图标", "skill_icons[1] `asset/tft/icons/tft_loris_skill2`",
     "一面铜金色的巨盾立在前面，后面护着一个小小的蓝色人影，人影周围一圈六边形护盾光。",
     ICON + ": a bronze TOWER SHIELD standing upright in front at the right, behind it a small blue silhouette of an ally "
     "wrapped in a pale blue-white ring of HEXAGON tiles, a cyan glint on the shield's gem. Colours: " + BZ + ", " + BR
     + ", " + HX + "."),
    ("ult", "大招「钢铁防线」图标", "skill_icons[2] `asset/tft/icons/tft_loris_ult`",
     "巨盾的下沿狠狠砸进地里，地面炸开一圈铜色和青蓝色的冲击波，裂缝四散，碎石飞起。",
     ICON + ": the bottom edge of a bronze TOWER SHIELD slammed into the ground at the centre, a bronze-and-cyan "
     "SHOCKWAVE ring bursting out flat around it, cracks spreading through the ground, grit stones flying up. "
     "Colours: " + BZ + ", " + HX + ", " + DS + "."),
]
BIG_FX = ["r_slam"]

GROUPS = [
    ("q_shield e_land p_shield p_burst (barrier)", ["tft3_trait_shield_1", "tft3_trait_shield_2", "tft3_trait_shield_3",
                                                     "tft3_trait_shield_10_5", "tft6_trait_scrap_shield_star"]),
    ("q_dash q_hit (charge)", ["tft16_loris_base_charge_missile", "tft16_loris_base_q_dash_head_mesh",
                               "tft16_loris_base_q_line_02", "tft16_loris_base_multi_line", "tft16_loris_q_mesh"]),
    ("a_hit q_hit r_hit (impacts)", ["tft13_beardy_base_q_hit_mask02", "tft12_camille_base_p_wind_hookshot_hit_tar_flash",
                                     "flash_02", "common_flashyellow"]),
    ("r_slam (shockwave)", ["tft13_beardy_base_w_fistwaves_03", "tft13_beardy_w_rays_colormap", "tft16_base_ring_decal_01",
                            "sett_base_mid_decal_edge", "tft16_base_w_waveglow_blend_01"]),
    ("dust smoke", ["tft16_smoke_01", "tft16_loris_mist", "tft16_loris_base_q_wisp_panner", "velkoz_skin11_smoke_mult"]),
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
    """Loris at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"洛里斯 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 洛里斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/loris_design.png`："
      "拿巨型塔盾的大胡子皮城执法官，蓝头巾、宝蓝镶铜边的盔甲，铜金色的巨盾上一颗青蓝宝石）。"
      f"洛里斯在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/loris_size.png`：洛里斯缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里洛里斯自己的特效贴图（**灰色的形状，游戏里再染色**：护盾、冲锋、撞击、冲击波、尘土），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **洛里斯是皮尔特沃夫的神盾使，特效都是他的巨盾**：铜金色的金属、盾上宝石的**海克斯青蓝**、**蓝白色的六边形护盾**、"
      "盾砸地时的尘土和碎石，嘲讽是红色的愤怒标记；不要火焰，不要魔法符文，不要光滑的霓虹光束。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、护盾、冲击波、尘土没有黑描边**（徽章、星星、齿轮、装甲片这些实物可以有一圈深色描边）。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `loris_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `loris_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「神盾使」 | 每条命第一次掉到 75% 和 25% 血时各得一层最大生命的护盾 | `p_burst` · `p_shield` |")
    a("| 普攻 | 巨盾从身侧抡过来砸人 | `a_hit` |")
    a("| 技能 1 =「皮城争斗」 | 身上亮起护盾，举盾往前冲锋，撞到的敌人被击退、晕眩、受到魔法伤害 | `q_shield` · `q_dash` · `q_hit` · `q_stun` |")
    a("| 技能 2 =「盾卫」 | 冲到血量最低的队友身边把盾一立，两人都得护盾，之后 4 秒替他承受 30% 伤害 | `e_land` · `e_guard` |")
    a("| 大招 =「钢铁防线」 | 把巨盾举过头顶砸进地里，冲击波击飞周围的敌人并嘲讽他们 2 秒，自己减伤 | `r_slam` · `r_hit` · `r_taunt` · `r_wall` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、护盾、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("铜金（盾、徽章、冲击环、图标边框）", BRONZE), ("海克斯青蓝（盾上的宝石）", HEX), ("护盾蓝白", BARRIER),
                        ("嘲讽红", TAUNT), ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `loris_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `loris_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `loris_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `loris_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_loris_fx`（小的）和 `tft_loris_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- p_burst / e_land 由 tft.dll 在神盾使触发、盾卫落地时播；q_shield 在技能 1 出手时播。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="loris_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "loris_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_loris.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "loris_design.png"))
    shape = size_sheet(os.path.join(out, "design", "loris_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"loris_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"loris_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
