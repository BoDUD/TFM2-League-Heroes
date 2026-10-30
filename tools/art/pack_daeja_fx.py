#!/usr/bin/env python3
"""Build daeja_fx_pack.zip: step 3 of Daeja's sprite - Codex draws his effects and his three skill icons
(pack_nomsy_fx.py's way).

    python tools/lol/fx_ref_daeja.py            # the particle references -> C:/t/dj_work/fxref
    python tools/art/pack_daeja_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name daeja_fx_redo_pack]

The pack (C:/t/dj_work/fx/daeja_fx_pack, zipped into --out, default D:/TFM2-Workshop/daeja_packs) holds PROMPTS.md
(also written to assets/source/daeja/PROMPTS_FX.md), design/daeja_design.png (the approved idle at 4x on its own
squares), design/daeja_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (his own set-7 particle textures - grey shapes the game tints, grouped by the
effect they inform). The effects are the views the kit binds (tools/kit/build_daeja.py, the user's picks 2026-10-30:
bottom lane, plan A 「罡风弹幕」): view_projectiles a_bolt, p_bolt, q_wave, e_gust, r_wave (q_wave / r_wave flown by
tft.dll); view_effects a_hit, p_hit, q_hit, r_hit; view_buffs p_shred, e_slow, r_fly. Plus the three skill icons.
His colours: white and pale cyan wind, the Mirage's violet at the edges, the magenta of his eyes for the shred.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying pictures (FLYING) point right and are symmetric top to bottom (the game turns them with the cast).
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

TMP = "C:/t/dj_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "daeja", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "daeja", "hd")
NAME = "daeja_fx_pack"
PPU = 1.72

WIND = "#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6"              # his wind: white, pale cyan, sky blue
MIRA = "#F6EBFF, #D8B2FF, #A878F2, #6E48C8"                      # the Mirage's violet (his wings' membranes)
EYE = "#FFE2FF, #FF7AF0, #E81CE8"                                # the magenta of his eyes (the shred's mark)
WI = f"a wind ramp ({WIND})"
MI = f"a mirage violet ramp ({MIRA})"
EY = f"a magenta ramp ({EYE})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, "
         "small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no "
         "red, no gold, no smooth neon beams")
HIM = "the dragon-man stands in the middle, not drawn: 34 squares wide and 40 tall, his head in the middle"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little "
        "violet corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at "
        "2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_bolt", "普攻：风弹，4 帧循环", "view_projectiles `tft_daeja_a_bolt`（飞向目标，随方向旋转；上下对称、朝右）", "10 × 8",
     "他拳头推出去的**风弹**：一颗白色芯的青色小风球，后面拖着两三道弯弯的气流尾巴。**朝右、上下对称**，4 帧循环（气流转动）。",
     WI,
     "A WIND BOLT, 4 looping frames, " + TB + ": a small ball of wind 5 squares across with a white core at the right, "
     "two or three short curling air streaks trailing behind it to the left (one above, one below, mirrored); frames "
     "1-4 the streaks swirling. " + MAGIC + ".",
     row(4, 10, 8) + CENTER),
    ("a_hit", "普攻：风弹打中，4 帧", "view_effects `tft_daeja_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "风弹打中：一下白光，一圈青色的小气流往外散开，几缕风丝四射。**左右对称**，4 帧。",
     WI,
     "A WIND HIT, 4 frames, " + LR + ": 1 a white flash 4 squares across; 2 a small ring of cyan air bursting out round "
     "it, short wind wisps flying out in a symmetric star; 3 the ring wider and thinner; 4 a few fading wisps. "
     + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("p_bolt", "被动：三连弹幕的小风弹，4 帧循环", "view_projectiles `tft_daeja_p_bolt`（飞向目标，随方向旋转；上下对称、朝右）", "8 × 6",
     "被动「三连弹幕」的**小风弹**：比普攻的风弹小一圈，带一点幻镜紫色的边，后面一道细细的气流。**朝右、上下对称**，4 帧循环。",
     WI + ", " + MI,
     "A SMALL BARRAGE BOLT, 4 looping frames, " + TB + ": a tiny dart of wind 3 squares tall with a white tip at the "
     "right and a thin violet rim, one thin air streak trailing behind it to the left; frames 1-4 the streak flickering. "
     + MAGIC + ".",
     row(4, 8, 6) + CENTER),
    ("p_hit", "被动：小风弹打中，3 帧", "view_effects `tft_daeja_p_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "小风弹打中：一个小小的青紫色闪光，两三缕风丝。**左右对称**，3 帧。",
     WI + ", " + MI,
     "A SMALL WIND HIT, 3 frames, " + LR + ": 1 a small white-cyan flash 3 squares across with a violet rim; 2 four "
     "tiny wisps flying out in a symmetric cross; 3 the wisps fading. " + MAGIC + ".",
     row(3, 10, 10) + CENTER),
    ("p_shred", "被动：魔抗被削（可叠加），6 帧循环", "view_buffs `tft_daeja_p_shred`（跟随被打中的人，头顶上，z 3；左右对称）", "14 × 30",
     "魔抗被削：被打中的人**头顶上**一个小小的品红色裂开的魔法符印（一个圆形的符，中间一道裂缝），两边一点紫色的风丝慢慢转。"
     "**只在头顶**，身体位置留空。**左右对称**，6 帧循环（符印一闪一闪）。",
     EY + ", " + MI,
     "A BROKEN MAGIC WARD, 6 looping frames, " + LR + ": on " + TARGET + "; ABOVE THE HEAD only (the top 8 squares of "
     "the cell): a small round magenta rune 6 squares across split by a crack down its middle (the magic resistance "
     "broken), two thin violet wisps circling it, one each side; frames 1-6 the rune flickering bright and dim. The "
     "body area below stays EMPTY. " + MAGIC + ".",
     row(6, 14, 30) + CENTER),
    ("q_wave", "罡风轰击：飞出去的风波，4 帧循环", "view_projectiles `tft_daeja_q_wave`（大表，穿透的直线风波，随方向旋转；上下对称、朝右）", "16 × 22",
     "罡风轰击的**风波**：一道竖起来的大月牙形狂风（像一把弯刀，凸的一面朝右，往前冲），月牙里面是白色到青色的气流，"
     "边缘一点幻镜紫色，后面拖着几道横向的速度线。**朝右、上下对称**，4 帧循环（气流翻滚）。",
     WI + ", " + MI,
     "A WIND BLAST WAVE, 4 looping frames, " + TB + ": a tall CRESCENT of storming wind 20 squares tall and 7 thick, "
     "its bulge facing RIGHT (rushing forward), white along its front edge, cyan in its body, a violet rim at its two "
     "tips; behind it to the left three horizontal speed streaks (one in the middle, two mirrored); frames 1-4 the air "
     "inside rolling. " + MAGIC + ".",
     row(4, 16, 22) + CENTER),
    ("q_hit", "罡风轰击：打中，5 帧", "view_effects `tft_daeja_q_hit`（在被穿过的人身上，z 3；左右对称）", "20 × 20",
     "风波打中：一下白色强光，一圈青色的气浪炸开，几片小云往外飞。**左右对称**，5 帧。",
     WI,
     "A WIND BLAST HIT, 5 frames, " + LR + ": 1 a white flash 6 squares across; 2-3 a ring of cyan air bursting out to "
     "18 squares wide, small puffs of cloud and wind wisps flying out symmetrically; 4-5 the ring breaking into fading "
     "wisps. " + MAGIC + ".",
     row(5, 20, 20) + CENTER),
    ("e_gust", "振翼退风：往前扇出的一阵减速的风，6 帧", "view_projectiles `tft_daeja_e_gust`（大表，从他身上指向目标的一条线，随方向旋转；上下对称、朝右）", "46 × 16",
     "他振翅往前扇出的**一阵风**：从左端（他身前）往右吹出一道越来越宽的风带，里面是一道道弯弯的白色和青色气流，几片小云，"
     "右端散开。左端窄（约 6 格高），右端宽（约 14 格高）。**朝右、上下对称**，6 帧（吹出去、散开）。",
     WI + ", " + MI,
     "A WING GUST, 6 frames, " + TB + ": a band of wind blowing from the LEFT edge (6 squares tall there: in front of "
     "him) to the RIGHT, widening to 14 squares tall at the right end; inside it curving streaks of white and cyan air "
     "and a few small cloud puffs, violet at its outer edges; 1-2 the gust pushing out from the left, 3-4 filling the "
     "whole length, 5-6 thinning and breaking into wisps at the right. " + MAGIC + ".",
     row(6, 46, 16) + CENTER),
    ("e_slow", "振翼退风：被风缠住减速，6 帧循环", "view_buffs `tft_daeja_e_slow`（跟随被减速的人，脚下地面，z 3；左右对称）", "20 × 10",
     "被减速：被吹到的人脚下一圈绕着打转的青色旋风（从斜上方看的椭圆，宽是高的 3 倍），风丝缠着往下压。**左右对称**，6 帧循环（旋风转动）。",
     WI,
     "A CLINGING WIND, 6 looping frames, " + LR + ": on the GROUND round the unit's feet, an ellipse seen from above, "
     "about 18 squares wide and 6 tall: a ring of swirling cyan wind wisps winding round the feet, a few small "
     "downward-curling streaks; frames 1-6 the wisps circling (keep every frame left-right symmetric). Nothing above "
     "the feet. " + MAGIC + ".",
     row(6, 20, 10) + CENTER),
    ("r_wave", "苍穹罡风：大冲击波，4 帧循环", "view_projectiles `tft_daeja_r_wave`（大表，穿透的直线大冲击波，随方向旋转；上下对称、朝右）", "22 × 30",
     "大招的**大冲击波**：比罡风轰击更大更猛的一道双层月牙形狂风（一大一小两道月牙叠着，凸的一面朝右），白色的芯、"
     "青色的身子、幻镜紫色的边，前面一圈压出来的气浪，后面几道长长的速度线。**朝右、上下对称**，4 帧循环。",
     WI + ", " + MI,
     "A SKY GALE WAVE, 4 looping frames, " + TB + ": TWO nested CRESCENTS of storming wind, the big one 28 squares tall "
     "and 8 thick, a smaller one inside it, their bulges facing RIGHT; white along the front edges, cyan bodies, "
     "violet rims and tips; a thin pressure ring just in front of them; long horizontal speed streaks trailing behind "
     "to the left (mirrored); frames 1-4 the air rolling. " + MAGIC + ".",
     row(4, 22, 30) + CENTER),
    ("r_hit", "苍穹罡风：打中，6 帧", "view_effects `tft_daeja_r_hit`（大表，在被穿过的人身上，z 3；左右对称）", "30 × 30",
     "大冲击波打中：一下大白光，一圈青紫的气浪炸开，往上卷起一个小旋风，碎云四散。**左右对称**，6 帧。",
     WI + ", " + MI,
     "A SKY GALE HIT, 6 frames, " + LR + ": 1 a big white flash 8 squares across; 2-3 a ring of cyan and violet air "
     "bursting out to 28 squares wide, a small whirlwind twisting up from the middle; 4-6 the ring and the whirl "
     "breaking into fading cloud puffs and wisps. " + MAGIC + ".",
     row(6, 30, 30) + CENTER),
    ("r_fly", "苍穹罡风：飞行时脚下的旋风，6 帧循环", "view_buffs `tft_daeja_r_fly`（跟随他，在他身后，z -1；左右对称）", "44 × 14",
     "他飞在空中时，**脚下**一大圈被翅膀扇起来的旋风（从斜上方看的椭圆，宽是高的 3 倍），风丝和小云绕着转，边上一点紫色。"
     "**左右对称**，6 帧循环（风绕着转）。",
     WI + ", " + MI,
     "A DOWNDRAFT, 6 looping frames, " + LR + ": round " + HIM + " - only UNDER his feet: an ellipse seen from above, "
     "about 42 squares wide and 12 tall, a ring of swirling cyan wind with small cloud puffs blown out to both sides, "
     "violet at its rim; frames 1-6 the wisps circling (keep every frame left-right symmetric). Nothing above the "
     "ellipse. " + MAGIC + ".",
     row(6, 44, 14) + CENTER),
]
ICONS = [
    ("skill", "技能 1「罡风轰击」图标", "skill_icons[0] `asset/tft/icons/tft_daeja_skill`",
     ICON + ": a big white-and-cyan wind crescent rushing to the right, speed streaks behind it, three small violet "
               "figures' outlines in a row being struck by it."),
    ("skill2", "技能 2「振翼退风」图标", "skill_icons[1] `asset/tft/icons/tft_daeja_skill2`",
     ICON + ": one blue-violet dragon wing (a dark violet bone, a cyan-to-violet fan membrane) beating, a gust of "
               "white wind blowing to the right from it and a curved arrow pointing back to the left."),
    ("ult", "大招「苍穹罡风」图标", "skill_icons[2] `asset/tft/icons/tft_daeja_ult`",
     ICON + ": a pair of blue-violet dragon wings spread wide high in a night sky, three wind crescents shooting out "
               "below them to the right."),
]
BIG_FX = ["q_wave", "e_gust", "r_wave", "r_hit"]
FLYING = ("a_bolt", "p_bolt", "q_wave", "e_gust", "r_wave")

GROUPS = [
    ("a_bolt a_hit p_bolt p_hit (his wind bolts)",
     ["tft7_dragonblue_base_q_mote", "tft7_dragonblue_base_q_glow", "tft7_dragonblue_base_r_hit_spark",
      "tft_hit32"]),
    ("q_wave r_wave (the blasts)",
     ["tft7_dragonblue_base_q_shockwave", "tft7_dragonblue_base_q_streaks", "tft7_dragonblue_base_speedlines_mult",
      "tft7_dragonblue_base_q_innerhead_2"]),
    ("e_gust e_slow r_fly (gusts and clouds)",
     ["tft7_dragonblue_base_q_clouds", "tft7_dragonblue_base_cloud_02", "tft7_dragonblue_base_q_smoketrail_02",
      "tft7_dragonblue_base_q_cas_tunnel_smoke"]),
    ("q_hit r_hit p_shred (bursts, sparks, runes)",
     ["tft7_dragonblue_base_r_sharp_sparks", "tft7_dragonblue_blast_nova_bunny_04", "tft7_dragonblue_base_tattoos",
      "tft_base_swirltext01"]),
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
    """Daeja at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"迭嘉 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 迭嘉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/daeja_design.png`："
      "3/4 朝右、直立站着的蓝色水晶龙人：冰蓝皮肤、深蓝紫的人字形胸甲、古铜尖刺；古铜面甲下品红发光的眼睛，浅青蓝的大团鬃毛；"
      "两只发光的青色水晶拳；背后两片高高竖起的翅膀（深紫翼骨、青到紫的扇形翼膜）；尾巴尖一片古铜尾鳍）。"
      f"迭嘉在游戏里是**高清**的（每个游戏格子里约 1.72×1.72 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/daeja_size.png`：迭嘉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里迭嘉自己的特效贴图（罡风轰击的冲击波、速度线、云、烟、大招的火花）"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **迭嘉是幻镜龙，特效都是风的魔法**：白色、浅青、天蓝的风和气流，弯弯的月牙形冲击波，小团的云，"
      "边上点缀他翅膀的**幻镜紫**；削魔抗的符印用他眼睛的**品红**；不要火、不要红色、不要金色，不要光滑的霓虹光束。")
    a("> - **特效要亮**：每团风都有最亮一档或白色的芯，暗底上一眼能看见。**风、冲击波、云没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下，身体位置留空**，不要盖住人。")
    a("> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；"
      f"**飞行的画面（{'、'.join(FLYING)}）朝右、严格上下对称**（游戏会按方向转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `daeja_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `daeja_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「风弹」 | 拳头往前一推，射出一颗风弹 | `a_bolt` · `a_hit` |")
    a("| 被动「三连弹幕」 | 每次普攻再追加 3 颗小风弹，各带少量魔法伤害并削减魔抗（可叠加） | `p_bolt` · `p_hit` · `p_shred` |")
    a("| 技能 1 =「罡风轰击」 | 双翼往前一扫，朝敌人最多的直线打出一道穿透的风波 | `q_wave` · `q_hit` |")
    a("| 技能 2 =「振翼退风」 | 振翅朝敌人扇出一阵减速的风，自己往后跳 | `e_gust` · `e_slow` |")
    a("| 大招 =「苍穹罡风」 | 展开双翼飞起来，朝敌人最多的直线连续轰出 3 道大冲击波，然后落地 | `r_fly` · `r_wave` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("风（白、浅青、天蓝）", WIND), ("幻镜紫（边上、翼膜的颜色）", MIRA), ("他眼睛的品红（削魔抗的符印）", EYE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `daeja_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `daeja_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `daeja_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `daeja_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_daeja_fx`（小的）和 `tft_daeja_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- q_wave、r_wave 由 tft.dll 发出（朝敌人最多的直线飞的穿透风波）；e_gust 是从他身上出发的一条线（左端对着他身前）；"
      "p_shred 是叠加的减魔抗 buff（每层一个，画面会叠在一起：画得淡一点）；r_fly 是他飞行时身上的 caster buff（z -1，在他身后）。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="daeja_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/daeja_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_daeja.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "daeja_design.png"))
    shape = size_sheet(os.path.join(out, "design", "daeja_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"daeja_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"daeja_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
