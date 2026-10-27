#!/usr/bin/env python3
"""Build kobuko_fx_pack.zip: step 3 of Kobuko's sprite - Codex draws his effects and his three skill icons
(pack_loris_fx.py's way).

    python tools/lol/fx_ref_kobuko.py            # his TFT particle textures -> C:/t/kb_work/fxref
    python tools/art/pack_kobuko_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name kobuko_fx_redo_pack]

The pack (C:/t/kb_work/fx/kobuko_fx_pack, zipped into --out, default dist/kobuko_packs) holds PROMPTS.md (also written
to assets/source/kobuko/PROMPTS_FX.md), design/kobuko_design.png (the approved idle at 4x on its own squares),
design/kobuko_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (his own TFT particle textures, sets 15 and 14 - grey shapes the game tints - grouped
by the effect they inform). The effects are the views the kit binds (tools/kit/build_kobuko.py, the user's picks
2026-10-27: top, plan A 「金爪宗师」): view_effects a_hit, q_shield, q_hit, e_land, e_hit, r_jump, r_mark, r_slam, r_hit
and tft.dll's p_burst; view_buffs q_on, q_stun, p_rage. Plus the three skill icons. He throws nothing: no projectile
pictures.
His colours: the warm GOLD of his golden claw (the spiral on his palms), the FLAME orange-red of his fur when enraged,
dust and broken stone where he lands.
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

TMP = "C:/t/kb_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "kobuko", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "kobuko", "hd")
NAME = "kobuko_fx_pack"
PPU = 2.0

GOLD = "#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A"              # the golden claw, the palm spiral
FLAME = "#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E"             # his flame-pattern fur, the rage
DUST = "#F0E2C8, #C8AE88, #9A7E5C, #64503A"                       # dust
STONE = "#D8D0C0, #A89C88, #74695A, #463E34"                      # broken stones, cracks
GO = f"a golden chi ramp ({GOLD})"
FL = f"a flame orange-red ramp ({FLAME})"
DS = f"a dust brown ramp ({DUST})"
ST = f"a broken stone grey-brown ramp ({STONE})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral "
         "on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and "
         "broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams")
HIM = "the round, broad cat master stands in the middle, not drawn: 38 squares wide and 40 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little round "
        "spiral corners, a deep warm brown-red inside, the symbol big and centred, lit from the upper left; pixel art at "
        "2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：猫爪掌打中，4 帧", "view_effects `tft_kobuko_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "大爪子一掌拍中：一下白色的闪光，一圈金橙色的冲击环，几点火星往两边崩开。**左右对称**，4 帧。",
     GO + ", " + FL,
     "A HEAVY PALM STRIKE IMPACT, 4 frames, " + LR + ": 1 a white star flash 8 squares across; 2 a short golden shock "
     "ring 12 squares wide and 6 tall, orange sparks flying out to both sides (mirrored); 3 the ring thinner and wider, "
     "the sparks farther; 4 the last sparks fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_shield", "金爪真言：身上套上金色护盾，6 帧", "view_effects `tft_kobuko_q_shield`（跟随他，z 3；左右对称）", "44 × 48",
     "可酷伯放技能 1 时双臂一张，身上「嗡」地套上一层**金色的气劲护盾**：从胸前一点金光往外张开成一个包住全身的圆罩，"
     "罩边上转着几个金色的漩涡纹，最后只剩一圈淡淡的金色外轮廓。身体位置留空（只画外圈）。**左右对称**，6 帧。",
     GO,
     "A GOLDEN CHI SHIELD SNAPPING ON, 6 frames, " + LR + ", " + HIM + ": 1 a small white-gold spark at his chest; 2 a "
     "ring of golden light bursting out from it; 3 a round dome 42 squares wide and 46 tall around him, its edge a "
     "golden band 2 squares thick with four round SPIRAL swirls on it (each 5 squares across, at mirrored places); 4 "
     "the spirals turning, light running round the edge; 5 the whole edge bright with a white rim; 6 settling to a "
     "thin pale gold outline. Only the outer edge: the middle (the body) left empty. " + MAGIC + ".",
     row(6, 44, 48) + CENTER),
    ("q_on", "金爪真言：金爪蓄好（下一掌加强），6 帧循环", "view_buffs `tft_kobuko_q_on`（跟随他，z 3；左右对称）", "40 × 48",
     "技能 1 之后、下一掌打出去之前：他头顶上方转着一个**金色的漩涡印记**（和他掌心的漩涡一样），身体两侧往上飘几点金色光点。"
     "身体位置留空。不要太显眼。**左右对称**，6 帧循环。",
     GO,
     "A CHARGED GOLDEN CLAW, 6 looping frames, " + LR + ", " + HIM + ": over his head (the top 8 squares of the cell) a "
     "golden SPIRAL sigil 7 squares across, glowing; at both sides of him (mirrored) a few golden motes (1-2 squares) "
     "drifting up; frames 1-6 the spiral pulsing brighter and back, the motes rising and fading in turn. The middle "
     "(the body) left empty. Subtle. " + MAGIC + ".",
     row(6, 40, 48) + CENTER),
    ("q_hit", "金爪重掌：打中（加伤 + 晕眩），5 帧", "view_effects `tft_kobuko_q_hit`（跟随被打的人，z 2；左右对称）", "26 × 26",
     "金爪重掌打中：一下大大的白金色闪光，中间印出一个**金色的漩涡掌印**，金色的冲击环往外炸开，火星四溅。比普攻狠得多。**左右对称**，5 帧。",
     GO + ", " + FL,
     "A GOLDEN CLAW SLAMMING INTO A UNIT, 5 frames, " + LR + ": 1 a big white-gold flash 14 squares across; 2 a golden "
     "SPIRAL imprint 12 squares across glowing in the middle, a golden shock ring bursting out, orange sparks flying "
     "out to both sides (mirrored); 3 a wide gold ring 24 squares wide and 12 tall, the spiral turning, the sparks "
     "farther; 4 the ring thin, the spiral fading; 5 the last sparks. " + MAGIC + ".",
     row(5, 26, 26) + CENTER),
    ("q_stun", "金爪真言：晕眩，6 帧循环", "view_buffs `tft_kobuko_q_stun`（跟随被晕的人，z 3；左右对称）", "18 × 44",
     "被拍晕的人：头顶上一圈**金色的小星星**和小漩涡绕着转。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。",
     GO,
     "A STUNNED UNIT, 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 10 squares of the cell) a "
     "flat ring of three small golden STARS and two tiny SPIRALS (each 3x3 squares) circling round, seen from the side "
     "(an ellipse 14 wide and 4 tall); frames 1-6 them moving round the ring (the ones in front brighter, mirrored "
     "positions). The rest of the cell empty. " + MAGIC + ".",
     row(6, 18, 44) + CENTER),
    ("e_land", "猛虎扑：落地的冲击，6 帧", "view_effects `tft_kobuko_e_land`（留在他落地的地上，z -1；左右对称）", "44 × 16",
     "可酷伯扑到敌人身上落地：地上「咚」地一圈**金橙色的冲击环**往外推开，尘土和小石块往两边飞，再落下。画在**地上**（扁椭圆），中心在格子底部中间。**左右对称**，6 帧。",
     GO + ", " + DS + ", " + ST,
     "A POUNCE LANDING, 6 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell: 1 a "
     "white-gold flash 12 squares wide; 2 a golden shock ring 24 squares wide and 8 tall, dust puffs to both sides "
     "(mirrored); 3 the ring 36 wide and 12 tall, small stones flung up; 4 the ring 42 wide, thinner, the stones "
     "falling; 5 dust settling; 6 the last thin dust. " + MAGIC + ".",
     row(6, 44, 16) + CENTER),
    ("e_hit", "猛虎扑：被击飞，4 帧", "view_effects `tft_kobuko_e_hit`（跟随被击飞的人，z 2；左右对称）", "18 × 20",
     "被扑击掀起来的人：脚下「砰」地一下金色的闪光，尘土往上喷，两边几颗小石头。**左右对称**，4 帧。",
     GO + ", " + DS,
     "A UNIT THROWN UP, 4 frames, " + LR + ": 1 a gold-white flash at the bottom middle 10 squares wide; 2 a jet of "
     "dust shooting upward 14 squares high, small stones to both sides (mirrored); 3 the dust spreading and thinning; "
     "4 the last puffs. " + MAGIC + ".",
     row(4, 18, 20) + CENTER),
    ("r_jump", "游戏结束！：一跃冲天的起跳尘土，5 帧", "view_effects `tft_kobuko_r_jump`（留在起跳的地上，z 1；左右对称）",
     "32 × 30",
     "可酷伯从这里一跃冲天：地上「轰」地踢起一圈尘土，几道金色的风线往上直冲出去（他已经飞走了，不画他）。**左右对称**，5 帧。",
     GO + ", " + DS,
     "A MIGHTY LEAP'S TAKE-OFF, 5 frames, " + LR + ": 1 a burst of dust 14 squares wide at the bottom middle " +
     GROUND_E + ", two golden WIND STREAKS (1 square wide) shooting straight up from it 20 squares high (mirrored); 2 "
     "the dust ring 26 wide and 8 tall, the streaks reaching the top of the cell; 3 the streaks thinning and breaking "
     "upward, the dust 32 wide; 4 the streaks gone, the dust rolling; 5 the last thin dust. " + MAGIC + ".",
     row(5, 32, 30) + CENTER),
    ("r_mark", "游戏结束！：落点预警，6 帧", "view_effects `tft_kobuko_r_mark`（跟随被砸的目标，z -1；左右对称）", "30 × 12",
     "他在天上的这一会儿，目标脚下出现一个**金橙色的落点圈**，从大往小收紧、越来越亮（中间一个金色漩涡），提示他要从天而降砸在这里。"
     "画在**地上**（扁椭圆）。**左右对称**，6 帧。",
     GO + ", " + FL,
     "A LANDING WARNING ON THE GROUND, 6 frames, " + LR + ": everything " + GROUND_E + ", centred in the cell: 1 a "
     "thin golden ring 28 squares wide and 10 tall; 2-5 the ring tightening frame by frame to 14 wide and 5 tall, "
     "thicker and brighter, turning orange, a golden SPIRAL 6 wide and 2 tall appearing in its middle; 6 the ring "
     "small and blazing white-gold. " + MAGIC + ".",
     row(6, 30, 12) + CENTER),
    ("r_slam", "游戏结束！：从天而降砸地的冲击波，8 帧", "view_effects `tft_kobuko_r_slam`（大表，留在他砸落的地上，z -1；左右对称）",
     "90 × 32",
     "大招：可酷伯从天而降砸在敌人身上，**地面炸开一圈很大的冲击波**（从中间往外推的金色和橙红色的环），地上裂开几道裂缝，"
     "尘土和碎石往四周飞，最后裂缝慢慢暗下去。这是画在**地上**的（扁椭圆），中心在格子底部中间。**左右对称**，8 帧。",
     GO + ", " + FL + ", " + DS + ", " + ST,
     "A GROUND-SHATTERING CRASH, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the "
     "cell: 1 a white-gold flash 18 squares wide; 2 a thick golden shock ring 38 squares wide and 12 tall with a flame "
     "orange outer edge, CRACKS (dark stone lines 1 square wide) starting out from the middle (mirrored); 3 the ring "
     "58 wide and 20 tall, the cracks longer, dust and broken stones flung up to both sides; 4 the ring 80 wide and 28 "
     "tall, thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the "
     "cracks glowing gold; 7 the cracks dimming; 8 faint cracks and thin dust. " + MAGIC + ".",
     row(8, 90, 32) + CENTER),
    ("r_hit", "游戏结束！：被砸飞，4 帧", "view_effects `tft_kobuko_r_hit`（跟随被击飞的人，z 2；左右对称）", "20 × 24",
     "被砸落的冲击掀起来的人：脚下「砰」地一下金橙色的大闪光，尘土和碎石往上喷。比猛虎扑更猛。**左右对称**，4 帧。",
     GO + ", " + FL + ", " + DS,
     "A UNIT BLASTED UP, 4 frames, " + LR + ": 1 a big gold-white flash at the bottom middle 14 squares wide; 2 a jet of "
     "dust and flame-orange sparks shooting upward 18 squares high, broken stones to both sides (mirrored); 3 the dust "
     "spreading and thinning; 4 the last puffs. " + MAGIC + ".",
     row(4, 20, 24) + CENTER),
    ("p_burst", "第二阶段：血量掉到一半，进入狂怒，6 帧", "view_effects `tft_kobuko_p_burst`（跟随他，z 3；左右对称）", "46 × 52",
     "第二阶段触发：可酷伯怒吼一声，身上「轰」地炸开一圈**橙红色的火焰**，一圈冲击环往外推，火舌往上窜，最后剩下身边几簇火苗。"
     "身体位置留空（只画外圈和上面的火舌）。**左右对称**，6 帧。",
     FL + ", " + GO,
     "A ROARING RAGE BURSTING OUT, 6 frames, " + LR + ", " + HIM + ": 1 a white-orange flash ring around his chest; 2 a "
     "ring of FLAME orange-red fire bursting out to 44 squares wide, a golden shock ring on the ground; 3 tall flame "
     "TONGUES licking up at both sides of him (mirrored) to over his head; 4 the flames at their tallest, sparks flying "
     "up; 5 the flames dropping; 6 a few small flames left at his sides and feet. After frame 1 the middle (the body) "
     "left empty. " + MAGIC + ".",
     row(6, 46, 52) + CENTER),
    ("p_rage", "第二阶段：狂怒中，6 帧循环", "view_buffs `tft_kobuko_p_rage`（跟随他，z 3；左右对称）", "42 × 48",
     "狂怒中的可酷伯：身体两侧各有几簇**橙红色的火苗**往上窜，脚下一圈暗红色的火圈，火星往上飘。身体位置留空（只画两侧和脚下）。"
     "**左右对称**，6 帧循环。",
     FL,
     "AN ENRAGED AURA, 6 looping frames, " + LR + ", " + HIM + ": at both sides of him (mirrored) three small flame "
     "TONGUES (each 4 squares wide and 6-9 tall) at his shoulder, waist and knee height, and a dark red ring of fire " +
     GROUND_E + " 34 squares wide and 6 tall at the bottom; frames 1-6 the flames flickering up and down in turn, sparks "
     "drifting up. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 42, 48) + CENTER),
]
ICONS = [
    ("skill", "技能 1「金爪真言」图标", "skill_icons[0] `asset/tft/icons/tft_kobuko_skill`",
     "一只火焰纹的大猫爪张开、掌心朝前，掌心一个发光的金色漩涡，四周一圈金色的护盾光。",
     ICON + ": a big flame-patterned CAT PAW (orange-red fur, short black claws) open with the palm to the viewer, a "
     "glowing GOLDEN SPIRAL on the palm, a round golden chi shield ring around it. Colours: " + GO + ", " + FL + "."),
    ("skill2", "技能 2「猛虎扑」图标", "skill_icons[1] `asset/tft/icons/tft_kobuko_skill2`",
     "一只张开爪子的大猫爪从左上方扑下来，爪尖拖着金色的速度线，下面一圈尘土。",
     ICON + ": a big flame-patterned CAT PAW with its black claws spread, pouncing down from the upper left toward the "
     "lower right, golden speed lines trailing behind it, a burst of dust under it. Colours: " + FL + ", " + GO + ", " + DS
     + "."),
    ("ult", "大招「游戏结束！」图标", "skill_icons[2] `asset/tft/icons/tft_kobuko_ult`",
     "一只巨大的猫爪从天上砸进地里，地面炸开一圈金色和橙红色的冲击波，裂缝四散，碎石飞起。",
     ICON + ": a huge flame-patterned CAT PAW slammed down from above into the ground at the centre, a gold-and-orange "
     "SHOCKWAVE ring bursting out flat around it, cracks spreading through the ground, broken stones flying up. "
     "Colours: " + GO + ", " + FL + ", " + ST + "."),
]
BIG_FX = ["r_slam"]

GROUPS = [
    ("q_shield q_on (golden chi shield)", ["tft15_kobuko_rework_base_shield_pan", "leona_skin21_shield01",
                                            "lux_skin29_shield_edges", "blitzcrank_skin11_z_shield_rim",
                                            "tft12_annie_base_banshee_veil_template_shield"]),
    ("q_hit a_hit (the golden palm)", ["tft11_fortuneyord_base_palm", "tft14_kobuko_base_spell_hand",
                                       "tft15_kobuko_base_spike_01", "brand_skin33_impactspike_01",
                                       "belveth_skin01_e_impact"]),
    ("q_stun (stars)", ["tft10_caitlyn_base_ba_buff_lilstar_4x2", "spark", "base_brightspark_11",
                        "hecarim_skin04_sparkle_2x4"]),
    ("e_land r_slam r_mark (the ground)", ["tft15_kobuko_rework_base_rocks_2x2", "tft8_alistar_base_cracks_glow",
                                           "tft5_dmg_skin36_ground_cracknoise_mult", "rock_debris",
                                           "tft_ring_glow_thicker", "brand_skin06_w_ring"]),
    ("p_burst p_rage (second phase)", ["tft14_kobuko_2ndstage_floor", "tft14_kobuko_base_r_flash_sharp",
                                       "tft14_kobuko_base_ringa_4x2", "yasuo_skin55_fire_trail_up_2",
                                       "z_glow_aura_self"]),
    ("dust smoke (e_hit r_jump r_hit)", ["tft_vi_smoke_2x2", "smokeerode", "rumble_skin04_z_oilysmoke_erode"]),
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
    """Kobuko at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"可酷伯 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 可酷伯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/kobuko_design.png`："
      "金橙色的约德尔功夫老猫，雪白的胡子和发髻，火焰纹的粗手臂，掌心一个金色漩涡，蓝白短褂）。"
      f"可酷伯在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/kobuko_size.png`：可酷伯缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里可酷伯自己的特效贴图（第 15、14 赛季，**灰色的形状，游戏里再染色**：金色护盾、掌击、星星、地面冲击、第二阶段的火、尘土），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **可酷伯是功夫老宗师，特效都是他的气劲**：温暖的**金色**光和圆圆的**漩涡纹**（和他掌心的金色漩涡一样）、狂怒时**橙红色的火焰**（和他手臂的火焰纹一样）、"
      "落地砸地时的尘土和碎石；不要蓝色，不要魔法符文，不要光滑的霓虹光束。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、护盾、冲击波、尘土没有黑描边**（星星、漩涡印记、石块这些实物可以有一圈深色描边）。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kobuko_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `kobuko_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「第二阶段」 | 每条命第一次掉到一半血时怒吼，进入狂怒直到死亡：攻速、吸血 | `p_burst` · `p_rage` |")
    a("| 普攻 | 大爪子一掌拍出去 | `a_hit` |")
    a("| 技能 1 =「金爪真言」 | 双臂一张套上金色护盾，下一掌变成金爪重掌：额外伤害 + 晕眩 | `q_shield` · `q_on` · `q_hit` · `q_stun` |")
    a("| 技能 2 =「猛虎扑」 | 扑到一个敌人身上，落地把周围的敌人击飞 | `e_land` · `e_hit` |")
    a("| 大招 =「游戏结束！」 | 一跃冲天（目标脚下出现落点圈），从天而降砸在目标身上，冲击波击飞周围的敌人 | `r_jump` · `r_mark` · `r_slam` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、护盾、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色气劲（护盾、掌印、漩涡、冲击环、图标边框）", GOLD), ("火焰橙红（狂怒、火星）", FLAME),
                        ("尘土", DUST), ("碎石、裂缝", STONE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `kobuko_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `kobuko_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `kobuko_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `kobuko_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_kobuko_fx`（小的）和 `tft_kobuko_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- p_burst 由 tft.dll 在第二阶段触发时播；q_shield 在技能 1 出手时播；r_jump 在大招起跳时留在原地，r_mark 跟着目标。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="kobuko_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "kobuko_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_kobuko.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "kobuko_design.png"))
    shape = size_sheet(os.path.join(out, "design", "kobuko_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"kobuko_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"kobuko_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
