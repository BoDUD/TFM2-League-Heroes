#!/usr/bin/env python3
"""Build thex_fx_pack.zip: step 3 of T-Hex's sprite - Codex draws its effects and its three skill icons (the tft
heroes' way).

    python tools/lol/fx_ref_thex.py            # the particle references -> C:/t/tx_work/fxref
    python tools/art/pack_thex_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name thex_fx_redo_pack]

The pack (C:/t/tx_work/fx/thex_fx_pack, zipped into --out, default D:/TFM2-Workshop/thex_packs) holds PROMPTS.md
(also written to assets/source/thex/PROMPTS_FX.md), design/thex_design.png (the approved idle at 4x on its own
squares), design/thex_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/tft_fx_ref.png (its own set-16 particle textures and Viktor's - grey shapes the game tints,
grouped by the effect they inform). The effects are the views the kit binds (the user's pick 2026-11-02: top, plan A
「海克斯军械库」): view_effects a_hit, a_crit, q_launch, q_fall (the ult's missiles r_fall reuse it), e_dash, e_hit,
r_hit, p_blast; view_projectiles a_bullet, r_beam; view_buffs e_slow, r_shield. Plus the three skill icons.
Its colours: hextech blue (its panels, the laser), its copper armour, the gatling's yellow-orange muzzle fire, grey
smoke.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying bullet and the laser bolt are symmetric top to bottom, pointing right.
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

TMP = "C:/t/tx_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "thex", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "thex", "hd")
NAME = "thex_fx_pack"
PPU = 1.9

HEX = "#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E"            # hextech blue: its panels, the laser, the shield
COPPER = "#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618"         # its copper armour, the missiles' casings
FIRE = "#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416"           # the gatling's muzzle fire, the blasts
SMOKE = "#ECE9E2, #B4B0A8, #7A7670, #474440"                   # smoke and dust
HX = f"a hextech blue ramp ({HEX})"
CU = f"a copper ramp ({COPPER})"
FI = f"a muzzle-fire ramp ({FIRE})"
SM = f"a smoke ramp ({SMOKE})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): "
         "crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal "
         "shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves")
HIM = ("the mech stands in the middle, not drawn: about 53 squares wide and 40 tall, crouched on two bird legs, its "
       "gatling in front, its tail behind, its helmeted head at the top right")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark copper frame with little "
        "blue hextech corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 "
        "px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_bullet", "普攻「加特林弹幕」：飞行的子弹，2 帧循环", "view_projectiles `tft_thex_a_bullet`（追踪弹道，随飞行方向旋转；上下对称、朝右）",
     "10 × 4",
     "加特林射出的一颗子弹：**一道短短的亮黄白色曳光**（往右飞），后面拖着橙色的尾巴。**上下对称、朝右**，2 帧循环（尾巴长短交替）。",
     FI,
     "A GATLING TRACER ROUND, 2 looping frames, " + TB + ": a small bright pale-yellow bullet head 2 squares tall in the "
     "right part of the cell, a straight yellow-orange tracer streak behind it to the left (6 squares in frame 1, 8 in "
     "frame 2), fading to orange at its tail. " + MAGIC + ".",
     row(2, 10, 4) + CENTER),
    ("a_hit", "普攻「加特林弹幕」：子弹打中，3 帧", "view_effects `tft_thex_a_hit`（跟随目标，z 2；左右对称）", "10 × 10",
     "子弹打中：一个小小的黄白火花，几粒火星往两边溅开。**左右对称**，3 帧（每次攻击会连着打中 4 下，要小、要快）。",
     FI,
     "A SMALL BULLET IMPACT, 3 frames, " + LR + ": 1 a tiny pale-yellow flash 3 squares across with four short rays; 2 a "
     "yellow-orange spark burst 8 squares across, a few single sparks flying out to both sides (mirrored); 3 the last "
     "sparks falling outward, orange and dim. Small and quick. " + MAGIC + ".",
     row(3, 10, 10) + CENTER),
    ("a_crit", "普攻：每第四下的强化子弹打中（枪手），4 帧", "view_effects `tft_thex_a_crit`（跟随目标，z 2；左右对称）", "20 × 18",
     "每第四次攻击的最后一颗子弹多打一下：**一圈海克斯蓝色的六边形冲击**炸开，中间奶白色的闪光，几块铜色碎片往两边飞。"
     "**左右对称**，4 帧。",
     HX + ", " + FI + ", " + CU,
     "A HEXTECH ROUND IMPACT, 4 frames, " + LR + ": 1 a pale white-blue flash 6 squares across; 2 a bright hextech-blue "
     "HEXAGON burst 14 squares across with a yellow core, short blue rays, two copper shards flying out (mirrored); 3 "
     "the hexagon ring 18 squares across and thinning, small blue sparks; 4 the last ring fragments and sparks. "
     + MAGIC + ".",
     row(4, 20, 18) + CENTER),
    ("q_launch", "技能 1「追踪导弹」：背上导弹舱发射，5 帧", "view_effects `tft_thex_q_launch`（跟随海克斯霸龙，画在它身上，z 2；左右对称）",
     "40 × 44",
     "导弹从它背上发射：**格子下半部是它的身体位置（留空）**，**上半部两枚小导弹冒着火光和白烟往上窜出去**（一左一右，对称），"
     "发射口一下橙色火光，烟往上拖。**左右对称**，5 帧。",
     CU + ", " + FI + ", " + SM + ", " + HX,
     "MISSILES LAUNCHING UPWARD, 5 frames, " + LR + ": the lower half of the cell is the mech's body (not drawn, EMPTY); "
     "from the middle of the cell: 1 two orange muzzle flashes 5 squares across, side by side (mirrored); 2 two small "
     "copper missiles (3 squares wide, 7 tall, nose up, a blue light on each) leaving the flashes, short flame tails and "
     "grey smoke puffs under them; 3 the missiles halfway to the top, the smoke trails longer and spreading; 4 the "
     "missiles leaving the top of the cell, two tall smoke trails; 5 the smoke trails thinning. " + MAGIC + ".",
     row(5, 40, 44) + CENTER),
    ("q_fall", "技能 1「追踪导弹」：导弹落下炸开，7 帧（大招的导弹也用这张）", "view_effects `tft_thex_q_fall` 和 `tft_thex_r_fall`（大表，放在落点的地面上，不跟随，z 2；画面最下面是地面；左右对称）",
     "24 × 52",
     "导弹从天上落下来：**一枚铜色小导弹头朝下、从格子最上面直直落下来**（尾巴带着火光和一道白烟），砸在格子最下面的地上，"
     "**炸开一团橙黄色的火光、外圈一圈海克斯蓝的冲击、几块铜色碎片**，然后剩一团烟。**左右对称**，7 帧。",
     CU + ", " + FI + ", " + HX + ", " + SM,
     "A FALLING MISSILE, 7 frames, " + LR + ": the bottom of the cell is the ground: 1 a small copper MISSILE nose down (4 "
     "squares wide, 9 tall, a blue light at its tail fins) at the very top of the cell, a short flame and smoke streak "
     "above it; 2 the missile a third of the way down, the smoke streak longer (straight up above it); 3 the missile two "
     "thirds down; 4 the missile hitting the ground at the bottom, a white-yellow flash; 5 a round yellow-orange BLAST 16 "
     "squares wide at the bottom, a thin hextech-blue ring round it, copper shards flying out low to both sides "
     "(mirrored); 6 the blast turning to a grey smoke cloud, the shards falling; 7 the last smoke. " + MAGIC + ".",
     row(7, 24, 52) + CENTER),
    ("e_dash", "技能 2「霸龙冲撞」：冲出去时脚下扬尘，5 帧", "view_effects `tft_thex_e_dash`（放在它起步的地面上，不跟随，z -1；左右对称）",
     "40 × 12",
     "它蹬地冲出去：脚下**一圈尘土往两边低低地扬起**，几道蓝色的短速度线。**只在地面和低处**。**左右对称**，5 帧。",
     SM + ", " + HX,
     "A DASH-OFF DUST BURST, 5 frames, " + LR + ": on the GROUND and low above it: 1 a short pale flash under the feet (an "
     "ellipse 14 squares wide); 2 grey dust puffs bursting out low to both sides (mirrored), two short hextech-blue speed "
     "streaks on each side; 3 the dust 32 squares wide, rolling; 4 the dust 38 squares wide and thinning; 5 the last "
     "dust. " + MAGIC + ".",
     row(5, 40, 12) + CENTER),
    ("e_hit", "技能 2「霸龙冲撞」：一口咬中，4 帧", "view_effects `tft_thex_e_hit`（跟随目标，z 2；左右对称）", "24 × 22",
     "一口咬中：**上下两排白色的三角牙印一下合拢**（像一张大嘴咬下去的形状），中间一下橙黄色的冲击闪光，几块铜色碎片和火星往两边飞。"
     "**左右对称**，4 帧。",
     FI + ", " + CU + ", " + HX,
     "A MECHANICAL BITE, 4 frames, " + LR + ": 1 two rows of white triangle TEETH shapes, one row at the top of the cell "
     "pointing down and one at the bottom pointing up, wide apart (each row 16 squares wide, five teeth); 2 the two rows "
     "snapped together in the middle, a bright yellow-white impact flash between them, short hextech-blue rays; 3 the "
     "teeth fading, an orange spark burst 20 squares across, copper shards flying out to both sides (mirrored); 4 the "
     "last sparks. " + MAGIC + ".",
     row(4, 24, 22) + CENTER),
    ("e_slow", "技能 2「霸龙冲撞」：减速，6 帧循环", "view_buffs `tft_thex_e_slow`（跟随被减速的人，脚下，z 3；左右对称）", "24 × 8",
     "被减速的人：脚边**一圈噼啪作响的海克斯蓝色小电火花**和几块小铜碎片，像被机械咬伤的余电。很淡、只在脚下。**左右对称**，6 帧循环。",
     HX + ", " + CU,
     "HEXTECH STATIC AT THE FEET, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): on "
     "EACH side (mirrored) two or three tiny crackling hextech-blue sparks (2-3 square zigzags) and one small copper "
     "chip by the ankle line; frames 1-6 the sparks jumping to new spots and flickering (every frame left-right "
     "symmetric). Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("r_beam", "大招「海克斯军械库」：激光，3 帧循环", "view_projectiles `tft_thex_r_beam`（大表，直线弹道，从嘴里射出飞得很快，随飞行方向旋转；上下对称、朝右）",
     "56 × 10",
     "大招每秒射出的激光：**一长条奶白芯、海克斯蓝色的光束**（往右射），边上噼啪的蓝色细电弧，最前端一个亮点。"
     "**上下对称、朝右**，3 帧循环（电弧位置轮换）。",
     HX,
     "A HEXTECH LASER BOLT, 3 looping frames, " + TB + ": a long straight BEAM across the cell - a white core 2 squares "
     "thick, bright hextech blue round it (6 squares thick in all), its front end at the right a round bright head 8 "
     "squares across, the tail end at the left tapering off; thin blue crackling arcs along its top and bottom edges "
     "(mirrored); frames 1-3 the arcs moving along it and the core flickering a shade. " + MAGIC + ".",
     row(3, 56, 10) + CENTER),
    ("r_hit", "大招「海克斯军械库」：被激光烧到，4 帧", "view_effects `tft_thex_r_hit`（跟随目标，z 2；左右对称）", "20 × 20",
     "被激光打中的人：**一下海克斯蓝色的灼烧闪光**，几道蓝色小电弧往外跳，一缕白烟往上飘。**左右对称**，4 帧。",
     HX + ", " + SM,
     "A LASER BURN, 4 frames, " + LR + ": 1 a white-blue flash 8 squares across; 2 a hextech-blue burst 16 squares across "
     "with a white core, four short crackling arcs jumping out (mirrored); 3 the burst fading to small blue embers, a "
     "thin grey smoke wisp rising from the middle; 4 the last embers and smoke. " + MAGIC + ".",
     row(4, 20, 20) + CENTER),
    ("r_shield", "大招「海克斯军械库」：海克斯护盾，6 帧循环", "view_buffs `tft_thex_r_shield`（大表，跟随海克斯霸龙，z 3；左右对称）",
     "64 × 50",
     "大招的护盾：身子外面**一圈由小六边形拼成的海克斯蓝色护罩**（横着的椭圆，只画外圈：一圈蓝色六边形格子，边缘奶白），"
     "六边形一格一格轮流亮起来。**里面它的身体位置留空**。**左右对称**，6 帧循环。",
     HX,
     "A HEXTECH HEX SHIELD, 6 looping frames, " + LR + ": round " + HIM + ": a ring of small HEXAGON cells (an ellipse 60 "
     "squares wide and 46 tall, only its 3-square rim drawn, made of hexagons 4 squares across with thin bright edges), "
     "hextech blue with pale white edges along the outside; frames 1-6 a few hexagons lighting up white in turn round the "
     "ring (mirrored pairs) and a soft sweep of brighter blue climbing both sides (every frame left-right symmetric). "
     "INSIDE the ring stays EMPTY (its body). " + MAGIC + ".",
     row(6, 64, 50) + CENTER),
    ("p_blast", "被动「驾驶员弹射」：机甲爆开，7 帧", "view_effects `tft_thex_p_blast`（大表，放在它倒下的地方，不跟随，z 2；画面最下面是地面；左右对称）",
     "80 × 56",
     "它被击倒时机甲爆开、把周围的人震飞：一下巨大的奶白闪光，**一团橙黄色的大火球爆开**，外面**一圈海克斯蓝的冲击环**贴着地面推开，"
     "铜色的装甲碎片和齿轮往两边飞，最后一团灰烟。**左右对称**，7 帧。",
     FI + ", " + HX + ", " + CU + ", " + SM,
     "A MECH EXPLOSION, 7 frames, " + LR + ": the bottom of the cell is the ground: 1 a big white-yellow flash 20 squares "
     "across at the middle bottom; 2 a round yellow-orange FIREBALL 34 squares across, a thick hextech-blue SHOCKWAVE "
     "RING bursting open on the ground round it (an ellipse 50 squares wide, 14 tall), copper armour plates and small "
     "gears flying out to both sides (mirrored); 3 the fireball 44 squares and turning orange, the ring 72 squares wide, "
     "the pieces flying higher; 4 the fireball breaking into grey smoke with orange inside, the ring at the cell's edge "
     "and thinning, the pieces falling; 5 a big grey smoke cloud, a few orange embers; 6 the smoke thinning, the pieces "
     "on the ground at the bottom corners; 7 the last smoke. " + MAGIC + ".",
     row(7, 80, 56) + CENTER),
]
ICONS = [
    ("skill", "技能 1「追踪导弹」图标", "skill_icons[0] `asset/tft/icons/tft_thex_skill`",
     ICON + ": three small copper missiles with blue-lit fins arcing up and over to the right, white smoke trails "
               "curving behind them, a small orange flame at each tail."),
    ("skill2", "技能 2「霸龙冲撞」图标", "skill_icons[1] `asset/tft/icons/tft_thex_skill2`",
     ICON + ": a copper mechanical T-rex head with a blue visor charging to the right, its steel jaws wide open with "
               "white triangle teeth, hextech-blue speed lines behind it."),
    ("ult", "大招「海克斯军械库」图标", "skill_icons[2] `asset/tft/icons/tft_thex_ult`",
     ICON + ": a bright hextech-blue laser beam with a white core shooting to the right from the lower left, two small "
               "missiles rising beside it, a ring of small blue hexagons behind."),
]
BIG_FX = ["q_fall", "r_beam", "r_shield", "p_blast"]
FLYING = ("a_bullet", "r_beam")

GROUPS = [
    ("a_bullet a_hit a_crit (the gatling)",
     ["tft_zeri_base_muzzleflash03_nocolor", "tft_base_muzzleflash_backdrop", "tft16_sparks01", "tft16_base_throw_sparks",
      "tft16_flash_06"]),
    ("q_launch q_fall (the missiles)",
     ["tft16_thex_base_thex_missile", "tft16_smoke_2x2", "tft16_pdm_cosmic_smoketip_erosion", "tft_smoke_erosion",
      "tft13_lieutenant_base_flare"]),
    ("r_beam r_hit (the laser)",
     ["lux_skin16_lazurbeam01", "tft16_beam_mult", "dragon_elder_laserbeamglow", "viktor_base_e_flare",
      "evillasercannon_lightning01"]),
    ("r_shield e_slow (hextech)",
     ["warwick_skin06_temp_w_deflectionbubble", "tft14_galio_base_w_glow_shield_02", "caitlyn_skin50_hextechstar01",
      "zeri_base_lightning_flipbook", "tft16_thex_base_em"]),
    ("e_dash e_hit p_blast (the charge, the bite, the burst)",
     ["tft16_swoosh", "tft15_galio_base_wind_horizontal", "monkeyking_skin07_r_hit02", "tft_sb_cloud03_a",
      "tft16_erosionshapes01_128"]),
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
    """T-Hex at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"海克斯霸龙 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 海克斯霸龙：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/thex_design.png`："
      "3/4 朝右、机械霸王龙：深藏青机身盖着铜色装甲、嵌着海克斯蓝色发光面板，背上一排蓝色水晶尖刺；铜色恐龙头盔、蓝色面罩、白眼红眶、"
      "钢灰紫大下颌和白色三角牙；近处的前爪是六管加特林，远处是机械爪；鸟腿、铜色三趾爪脚、长机械尾巴）。"
      f"海克斯霸龙在游戏里是**高清**的（每个游戏格子里约 1.9×1.9 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/thex_size.png`：海克斯霸龙缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是海克斯霸龙自己（金铲铲的枪口火光、曳光、导弹、烟、激光、护盾）和维克托（激光、电弧）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **海克斯霸龙是皮尔特沃夫的海克斯机甲，特效都是它的味道**：奶白芯的**海克斯蓝**光、小六边形、加特林**黄橙色的枪口火光**、"
      "铜色金属碎片、灰色的烟；不要绿色、不要紫色魔法、不要树叶。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了飞行的子弹 `a_bullet` 和激光 `r_beam`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `thex_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `thex_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「驾驶员弹射」 | 阵亡时驾驶员被弹出，机甲爆开，把附近敌人击退并晕眩 | `p_blast` |")
    a("| 普攻「加特林弹幕」 | 每次攻击连射 4 颗子弹；每第四次攻击最后一颗多打一下（枪手） | `a_bullet` · `a_hit` · `a_crit` |")
    a("| 技能 1 =「追踪导弹」 | 背上导弹舱翻开，导弹落在附近的敌人身上 | `q_launch` · `q_fall` |")
    a("| 技能 2 =「霸龙冲撞」 | 冲向目标一口咬住：伤害、击退、减速 | `e_dash` · `e_hit` · `e_slow` |")
    a("| 大招 =「海克斯军械库」 | 获得护盾，导弹舱全开：每秒一道贯穿激光（每多穿一人伤害递减）+ 一串导弹落在附近的敌人身上 | "
      "`r_shield` · `r_beam` · `r_hit` · `q_fall` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海克斯蓝（面板、激光、护盾）", HEX), ("铜（装甲、导弹壳、碎片）", COPPER), ("枪口火光、爆炸", FIRE), ("烟和尘土", SMOKE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `thex_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `thex_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `thex_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `thex_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_thex_fx`（小的）和 `tft_thex_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- a_bullet、r_beam 断言上下对称（朝右），其余断言左右对称。")
    a("- e_dash 放在地面上（不跟随，z -1）；q_fall（= r_fall）、p_blast 放在落点（不跟随）；q_launch 跟随它；r_shield 是它身上的 buff；"
      "e_slow 是敌人身上的 buff；a_bullet 是追踪弹道，r_beam 是直线弹道（从嘴里射出）。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="thex_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/thex_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_thex.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "thex_design.png"))
    shape = size_sheet(os.path.join(out, "design", "thex_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"thex_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"thex_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
