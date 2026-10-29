#!/usr/bin/env python3
"""Build idas_fx_pack.zip: step 3 of Idas's sprite - Codex draws her effects and her three skill icons
(pack_nomsy_fx.py's way).

    python tools/lol/fx_ref_idas.py            # the particle references -> C:/t/id_work/fxref
    python tools/art/pack_idas_fx.py [--no-zip] [--out DIR] [--only a_hit,r_burst --name idas_fx_redo_pack]

The pack (C:/t/id_work/fx/idas_fx_pack, zipped into --out, default D:/TFM2-Workshop/idas_packs) holds PROMPTS.md
(also written to assets/source/idas/PROMPTS_FX.md), design/idas_design.png (the approved idle at 4x on its own
squares), design/idas_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/tft_fx_ref.png (her own set-7 particle textures and Rakan's shields - grey shapes the game
tints, grouped by the effect they inform). The effects are the views the kit binds (tools/kit/build_idas.py, the
user's picks 2026-10-30: support, plan A 「黄金守护」): view_projectiles q_breath; view_effects a_hit, p_burst
(tft.dll's), e_roar, r_burst, r_heal; view_buffs q_shred, e_slow, e_shield, p_shield (tft.dll's), r_wrap, r_shield.
Plus the three skill icons.
Her colours: molten GOLD and golden light (her scales), her CYAN gems, a fresh green for the heal, light dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying picture (FLYING) points right and is symmetric top to bottom (the game turns it with the cast).
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

TMP = "C:/t/id_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "idas", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "idas", "hd")
NAME = "idas_fx_pack"
PPU = 2.45

GOLD = "#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08"     # molten gold, golden light, her scales
CYAN = "#F0FFFF, #9AF6FA, #2ED2E0, #108A9E"                      # her gems, crest and eyes
HEAL = "#F8FFE8, #D6F79A, #8EDC5E, #3E9E4A"                      # the heal's fresh green (with her gold)
DUST = "#F6EAC8, #CDB88A, #92784E"                               # the roar's dust
GO = f"a golden light ramp ({GOLD})"
CY = f"a cyan gem ramp ({CYAN})"
HE = f"a fresh green healing ramp ({HEAL})"
DU = f"a light dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small "
         "angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp "
         "angular shapes; no fire, no red, no purple, no smooth neon beams")
HER = "the golden dragon stands in the middle, not drawn: 52 squares wide and 40 tall, her head at the upper right"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
SHIELD = ("a SHIELD round the unit: only an OUTLINE of overlapping faceted golden scale plates (a tall egg shape round "
          "the unit, 2 squares thick), the inside EMPTY so the unit shows through")
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little "
        "cyan gem corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at "
        "2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：龙爪打中，4 帧", "view_effects `tft_idas_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "龙爪打中：三道金色的爪痕交叉成一个对称的「米」字闪光，中间一下白光，几片小金鳞崩飞出去。**左右对称**，4 帧。",
     GO,
     "A CLAW HIT, 4 frames, " + LR + ": 1 a white-gold flash 4 squares across; 2 three short golden claw rakes "
     "crossing over it in a symmetric star (one upright, two leaning out to each side), a few tiny golden scale chips "
     "flying out; 3 the rakes thinner, the chips farther; 4 a few fading gold sparks. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_breath", "黄金龙息：喷出的金色龙息，6 帧循环", "view_projectiles `tft_idas_q_breath`（大表，一道从她嘴边指向目标的线，随方向旋转；上下对称、朝右）", "56 × 22",
     "她喷出的**金色龙息**：从左端（她的嘴）往右喷出一道越来越宽的熔金洪流，像一把扇子，里面翻滚着金光、熔化的金滴和几片金鳞，"
     "边上一点青色的光。左端窄（嘴边约 6 格高），右端最宽（约 20 格高）。**朝右、上下对称**，6 帧循环（洪流翻滚）。",
     GO + ", " + CY,
     "A GOLDEN DRAGON BREATH, 6 looping frames, " + TB + ": a cone of MOLTEN GOLD breath pouring out from the LEFT "
     "edge (6 squares tall there: her mouth) to the RIGHT, widening to 20 squares tall at the right end like a fan; "
     "inside it rolling waves of golden light with a white-gold core along the middle, drops of molten gold and a few "
     "small golden scales tumbling in it, a thin cyan glint along its two edges; frames 1-6 the waves rolling to the "
     "right. " + MAGIC + ".",
     row(6, 56, 22) + CENTER),
    ("q_shred", "黄金龙息：护甲被熔，6 帧循环", "view_buffs `tft_idas_q_shred`（跟随被喷到的人，身上，z 3；左右对称）", "18 × 26",
     "护甲被熔化：被喷到的人肩头和胸前粘着几块正在往下滴的熔金，旁边一块裂开的小金色盾牌碎片（表示护甲降低），"
     "每隔一会儿掉下一滴金。**左右对称**，6 帧循环。" + "身体位置留空。",
     GO,
     "MOLTEN ARMOUR, 6 looping frames, " + LR + ": on " + TARGET + "; molten gold clinging to the unit's shoulders "
     "(two small blobs, one each side, 3 squares across) dripping down the sides, a tiny CRACKED golden shield shard "
     "above the head (4 squares, split by a crack) showing the armour broken; frames 1-6 one drop of gold running down "
     "and falling off each side. Only at the shoulders, the sides and above the head: the body area stays EMPTY. "
     + MAGIC + ".",
     row(6, 18, 26) + CENTER),
    ("e_roar", "龙威振翅：振翅一吼的冲击波，6 帧", "view_effects `tft_idas_e_roar`（大表，在她身上，z 3；左右对称）", "64 × 44",
     "她振翅一吼：她身边炸开一圈金色的冲击波（一个往外扩的椭圆环，宽是高的 2 倍左右），两边各一道金色的翅风弧线往外扫，"
     "环上带几片金鳞和一点尘土。她在中间，**身体位置留空**。**左右对称**，6 帧（环越扩越大、越来越淡）。",
     GO + ", " + DU,
     "A DRAGON'S ROAR SHOCKWAVE, 6 frames, " + LR + ": round " + HER + "; 1 a bright golden ring tight round her body "
     "(an ellipse twice as wide as tall), 2-3 the ring bursting outward to 60 squares wide, two sweeping golden "
     "wind arcs (one each side) curving out from her wings, a few golden scales and puffs of light dust riding on the "
     "ring; 4-6 the ring at the cell's edge, thinner, breaking into fading golden dashes. The ring only: her body area "
     "stays EMPTY. " + MAGIC + ".",
     row(6, 64, 44) + CENTER),
    ("e_slow", "龙威振翅：被震慑减速，6 帧循环", "view_buffs `tft_idas_e_slow`（跟随被减速的人，脚下地面，z -1；左右对称）", "20 × 10",
     "被减速：被吼到的人脚下一圈沉甸甸的金色鳞片（一个从斜上方看的椭圆，宽是高的 3 倍），鳞片之间压着几道往下的金色小箭头。"
     "**左右对称**，6 帧循环（鳞片微微闪光）。",
     GO,
     "A HEAVY SLOW, 6 looping frames, " + LR + ": on the GROUND under the unit's feet, an ellipse seen from above, "
     "about 18 squares wide and 6 tall: a ring of heavy faceted golden scales lying on the ground, between them three "
     "small golden arrows pointing DOWN; frames 1-6 a glint running round the scales. Nothing above the feet. "
     + MAGIC + ".",
     row(6, 20, 10) + CENTER),
    ("e_shield", "龙威振翅：队友的小护盾，6 帧循环", "view_buffs `tft_idas_e_shield`（跟随被套盾的队友，z 3；左右对称）", "22 × 38",
     "队友身上的小护盾：一圈淡淡的、由一片片金色小鳞片拼成的蛋形护盾轮廓，**里面是空的**，人从中间露出来；轮廓上一点青色宝石光。"
     "**左右对称**，6 帧循环（一道光沿着轮廓转）。",
     GO + ", " + CY,
     "A LIGHT SCALE SHIELD, 6 looping frames, " + LR + ": round " + TARGET + "; " + SHIELD + ", thin and pale (the "
     "lighter golden shades), one small cyan gem at its top; frames 1-6 a glint running up both sides together. "
     + MAGIC + ".",
     row(6, 22, 38) + CENTER),
    ("p_burst", "护卫之誓：护盾亮起，5 帧", "view_effects `tft_idas_p_burst`（tft.dll 播，在她和被保护的队友身上，z 3；左右对称）", "30 × 38",
     "护卫之誓触发：一下金光闪亮，一片片金色鳞片从四周飞回来、合成一圈蛋形的护盾，最后亮一下。人在中间，**身体位置留空**。**左右对称**，5 帧。",
     GO + ", " + CY,
     "A GUARDIAN'S VOW FLASH, 5 frames, " + LR + ": round " + TARGET + "; 1 a white-gold flash round the unit; 2-3 "
     "golden scale plates flying IN from all sides and locking together into " + SHIELD + "; 4 the shield complete and "
     "shining, a cyan gem flaring at its top; 5 the shine fading. " + MAGIC + ".",
     row(5, 30, 38) + CENTER),
    ("p_shield", "护卫之誓：护盾在身上，6 帧循环", "view_buffs `tft_idas_p_shield`（tft.dll 挂，跟随她和被保护的队友，z 3；左右对称）", "24 × 40",
     "护卫之誓的护盾：比小护盾更厚、更亮的一圈金鳞蛋形护盾轮廓，顶上一颗青色宝石，**里面是空的**。**左右对称**，6 帧循环（鳞片一片片轮流闪光）。",
     GO + ", " + CY,
     "A GUARDIAN'S SCALE SHIELD, 6 looping frames, " + LR + ": round " + TARGET + "; " + SHIELD + ", bold and bright "
     "(the brightest golden shades), a cyan gem at its top; frames 1-6 the scales lighting up one pair at a time from "
     "the bottom to the top. " + MAGIC + ".",
     row(6, 24, 40) + CENTER),
    ("r_wrap", "黄金龙鳞：裹翼时的金鳞外壳，6 帧循环", "view_buffs `tft_idas_r_wrap`（跟随她，z 3；左右对称）", "58 × 46",
     "她用双翼裹住自己时：她身外罩着一个由大片金鳞拼成的半透明感的**穹顶外壳轮廓**（只有外圈，像金色的龙鳞铠甲把她包起来），"
     "外圈上的鳞片一片片闪光，脚下一圈金光。**身体位置留空**。**左右对称**，6 帧循环。",
     GO + ", " + CY,
     "A GOLDEN SCALE SHELL, 6 looping frames, " + LR + ": round " + HER + " crouching (about 32 squares tall); a DOME "
     "of big overlapping faceted golden scale plates arching over her, only its OUTLINE (3 squares thick) from the "
     "ground on the left over her to the ground on the right, a short golden glow line on the ground under her, two "
     "small cyan gems on the dome; frames 1-6 a glint sweeping across the plates. The inside stays EMPTY. "
     + MAGIC + ".",
     row(6, 58, 46) + CENTER),
    ("r_burst", "黄金龙鳞：外壳炸开，7 帧", "view_effects `tft_idas_r_burst`（大表，在她身上，z 3；左右对称）", "76 × 52",
     "她展开双翼的一下：金鳞外壳往外炸开，一大圈金光冲击波，几十片金鳞和金币往四周飞散，中间一道往上冲的金光。"
     "**身体位置留空**。**左右对称**，7 帧。",
     GO + ", " + CY,
     "THE SHELL BURSTS, 7 frames, " + LR + ": round " + HER + "; 1 the dome of golden scales (as in a crouching "
     "shell) cracking with white-gold light; 2 a white-gold flash, the plates blowing OUTWARD; 3-4 a wide golden "
     "shockwave ring (an ellipse 70 squares wide) with dozens of golden scales and a few gold coins flying out to both "
     "sides, a golden light beam rising above her; 5-7 the ring at the edge thinning, the scales falling and fading "
     "into gold sparks. Her body area stays EMPTY. " + MAGIC + ".",
     row(7, 76, 52) + CENTER),
    ("r_heal", "黄金龙鳞：回血，6 帧", "view_effects `tft_idas_r_heal`（在她身上，z 3；左右对称）", "32 × 40",
     "她回血：身边升起几道金绿色的光柱和一颗颗往上飘的小十字、小金鳞。**身体位置留空**。**左右对称**，6 帧。",
     HE + ", " + GO,
     "A GOLDEN HEAL, 6 frames, " + LR + ": round " + TARGET + "; at both sides of the unit thin rising columns of "
     "green-gold light, small green plus signs and tiny golden scales floating up; 1 low at the feet, 2-4 rising "
     "past the shoulders, 5-6 fading above the head. The body area stays EMPTY. " + MAGIC + ".",
     row(6, 32, 40) + CENTER),
    ("r_shield", "黄金龙鳞：队友的护盾 + 攻速，6 帧循环", "view_buffs `tft_idas_r_shield`（跟随被套盾的队友，护盾在时一直在，z 3；左右对称）", "26 × 40",
     "队友身上大招的护盾：金鳞蛋形护盾轮廓，**里面是空的**，两侧各有两道往上冲的金色速度线（表示攻速提高），顶上一颗青色宝石。"
     "**左右对称**，6 帧循环。",
     GO + ", " + CY,
     "A GOLDEN SCALES SHIELD WITH HASTE, 6 looping frames, " + LR + ": round " + TARGET + "; " + SHIELD + ", bright, a "
     "cyan gem at its top, outside it on each side two short golden SPEED LINES streaking UPWARD; frames 1-6 the speed "
     "lines running up and starting again, a glint running round the shield. " + MAGIC + ".",
     row(6, 26, 40) + CENTER),
]
ICONS = [
    ("skill", "技能 1「黄金龙息」图标", "skill_icons[0] `asset/tft/icons/tft_idas_skill`",
     ICON + ": at the left a golden dragon's open jaws (a cyan crest above them), a wide cone of molten golden breath "
               "pouring out to the right with a cracked shield shard in it."),
    ("skill2", "技能 2「龙威振翅」图标", "skill_icons[1] `asset/tft/icons/tft_idas_skill2`",
     ICON + ": a pair of golden wings (rows of gold feather-blades) spread wide, a golden shockwave ring bursting out "
               "between them."),
    ("ult", "大招「黄金龙鳞」图标", "skill_icons[2] `asset/tft/icons/tft_idas_ult`",
     ICON + ": a big shield made of overlapping faceted golden dragon scales with a cyan gem in its middle, golden "
               "light rays behind it."),
]
BIG_FX = ["q_breath", "e_roar", "r_burst"]
FLYING = ("q_breath",)

GROUPS = [
    ("a_hit q_breath q_shred (claws, the golden breath, molten armour)",
     ["tft7_dragongold_base_q_webfluid32", "tft7_dragongold_base_q_armordebuff", "tft7_dragongold_base_waterspike32",
      "tft7_dragongold_base_r_energystreaksadd"]),
    ("e_roar e_slow r_burst (shockwaves, scales, coins)",
     ["slayer_shockwave_128_1", "tft7_dragongold_base_dragonskin", "coin", "tft14_braum_base_q_coin_5x5"]),
    ("e_shield p_burst p_shield r_wrap r_shield (the scale shields)",
     ["tft7_dragongold_base_q_template_shield", "warwick_base_r_deflectionbubble", "rakan_base_e_shield_mult",
      "rakan_base_p_shield_circle"]),
    ("r_heal, glow, sparks",
     ["rakan_base_w_sparks", "rakan_base_q_heal_trans_rgb", "ha_ap_poro_base_sparkle", "glow-soft"]),
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
    """Idas at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"艾达丝 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 艾达丝：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/idas_design.png`："
      "正侧面朝右、两条反关节腿直立的金色巨龙，有棱角的金鳞甲、深棕的胸腹、青蓝宝石，龙头上青蓝的鬃冠和角，发光的青蓝眼睛；"
      "两只翅膀手臂，前臂上是金色的羽刃翼，手腕上是深灰三指爪；长尾巴尖上一片刀刃）。"
      f"艾达丝在游戏里是**高清**的（每个游戏格子里约 2.45×2.45 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/idas_size.png`：艾达丝缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里艾达丝自己的特效贴图（熔金的流体、降护甲的标记、护盾模板、龙鳞、金币）和英雄联盟里洛（Rakan）护盾、回血的贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **艾达丝是金鳞龙，特效都是金色的龙的魔法**：熔金、金光、一片片**有棱角的金色龙鳞**（像她身上的鳞甲）、几枚闪光的金币，"
      "点缀她自己的**青蓝色**（宝石、鬃冠的颜色）；不要火、不要红色、不要紫色，不要光滑的霓虹光束。")
    a("> - **特效要亮**：每团光都有最亮一档或白金色的芯，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**。")
    a("> - **护盾和围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；"
      f"**飞行的画面（{'、'.join(FLYING)}）朝右、严格上下对称**（游戏会按方向转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `idas_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `idas_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「护卫之誓」 | 血量低于一半时，她和最近的一名队友各得一层金鳞护盾（30 秒一次） | `p_burst` · `p_shield` |")
    a("| 普攻「龙爪」 | 往前扑一爪 | `a_hit` |")
    a("| 技能 1 =「黄金龙息」 | 往前喷一片扇形的熔金龙息：魔法伤害、降低护甲 | `q_breath` · `q_shred` |")
    a("| 技能 2 =「龙威振翅」 | 振翅一吼：附近敌人眩晕一下并减速，她和附近队友得一层小护盾 | `e_roar` · `e_slow` · `e_shield` |")
    a("| 大招 =「黄金龙鳞」 | 双翼裹身、金鳞外壳减伤 2 秒，然后外壳炸开：回血，附近队友得护盾，护盾在时攻速提高 | `r_wrap` · `r_burst` · `r_heal` · `r_shield` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色（熔金、金光、金鳞、金币）", GOLD), ("她的青蓝（宝石、边上的光、图标的角）", CYAN), ("回血的绿光", HEAL),
                        ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `idas_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `idas_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `idas_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `idas_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_idas_fx`（小的）和 `tft_idas_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- p_burst、p_shield 由 tft.dll 播 / 挂（护卫之誓）；q_breath 是从她嘴边出发的一条只有画面的线（它的左端对着她的嘴）；"
      "e_roar、r_burst 是她身上的 CasterViewEffect；r_wrap 是她身上的 caster buff；r_shield 是 WithShield buff（护盾在时一直在）。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="idas_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/idas_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_idas.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "idas_design.png"))
    shape = size_sheet(os.path.join(out, "design", "idas_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"idas_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"idas_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
