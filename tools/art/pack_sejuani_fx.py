#!/usr/bin/env python3
"""Build sejuani_fx_pack.zip: step 3 of Sejuani's sprite - Codex draws her effects (pack_aurelionsol_fx.py's way).

    python tools/lol/fx_ref_sejuani.py         # League's particle textures -> C:/t/se_work/fxref (Riot's art, local only)
    python tools/art/pack_sejuani_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name sejuani_fx_redo_pack]

The pack (C:/t/se_work/fx/sejuani_fx_pack, zipped into --out, default dist/sejuani_packs) holds PROMPTS.md (also written to
assets/source/sejuani/PROMPTS_FX.md), design/sejuani_design.png (the idle at 4x, its own squares), design/sejuani_size.png
(at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Sejuani, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_sejuani.py, the user's picks 2026-10-24: jungle, layout A - Q /
W / R, Permafrost in the passive): view_projectiles w_line, r_bola; view_effects a_hit, q_dash, q_hit, f_mark, w_sweep
(big), w_hit, e_freeze, sh_hit, r_hit, r_storm (big); view_buffs fa_armour (fa), slow (w_slow, r_slow), frost (the
add-on's Frost stack on an enemy).
League's colours: white and pale ICE BLUE frost, glowing CYAN ice light, deep blue shadows in the ice, white SNOW and grey-
blue snow powder. Red side: the client never mirrors an effect picture, so every hit, buff, ground and body picture is
symmetric left to right; a projectile is turned with its flight, so it is drawn flying right and symmetric top to bottom
(the bola is round: both). Lasting pictures (the ice storm 2 s, the Frost Armour, the slow, the Frost stack) are a few
looping frames the import stretches to the zone's or the buff's life.
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

TMP = "C:/t/se_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "sejuani", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "sejuani", "hd")
NAME = "sejuani_fx_pack"
PPU = 2.0

ICE = "#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A"     # white to deep ice blue
GLOW = "#E8FFFF, #8AF4FF, #2ED0F0, #1488B8"                      # glowing cyan ice light
SNOW = "#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0"             # snow and grey-blue snow powder
DEEP = "#0A2A5A, #143C7A, #2A5CA8"                               # deep blue shadows inside the ice
FLASH = "#FFFFFF, #F4FBFF, #DCF0FF"                              # white flashes
IC = f"an ice ramp from white to deep blue ({ICE})"
GL = f"a glowing cyan ramp ({GLOW})"
SN = f"a snow ramp ({SNOW})"
DP = f"a deep blue ramp for shadows in the ice ({DEEP})"
FL = f"a white flash ramp ({FLASH})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
BOTH = ("ROUND: SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (the game turns it with its "
        "flight)")
CENTER = RF.CENTER
row = RF.row
FROST = ("everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, "
         "white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HER = "Sejuani on her boar stands in the middle, not drawn: 41 squares wide and 36 tall (the ice horn's tip to the hooves)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：冰锤砸中，3 帧", "view_effects `league_sejuani_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "冰锤头砸中敌人（参考 basicattack_trail、frostcrystals、sparkles）：中间一下白色闪光，炸开**几块淡蓝色的碎冰**和一点白色雪粉。"
     "**左右对称**，3 帧。",
     FL + ", " + IC + ", " + SN,
     "AN ICE SMACK, 3 frames, " + LR + ": 1 a white flash 6 squares across; 2 a burst 13 across - four to six pale blue "
     "angular ice shards flying out at mirrored places with a puff of white snow powder; 3 the shards further out and "
     "smaller, fading. " + FROST + ". " + TARGET + ".",
     row(3, 14, 14) + CENTER),
    # ---- Q Arctic Assault
    ("q_dash", "极寒突袭：起冲时踢起的雪，4 帧", "view_effects `league_sejuani_q_dash`（起冲的地方，不跟随，z -1；左右对称）",
     "40 × 12",
     "钢鬃起冲时蹄子底下**踢起一大片雪雾和冰碴**（参考 dust_01、z_smoke_4x4、flurrys）：贴着地面往两边散开的白色雪粉，几块小冰碴飞起来。"
     "**左右对称**，4 帧。",
     SN + ", " + IC,
     "A SNOW KICK-UP, 4 frames, " + LR + ": " + FEET + ", 1 a low puff of white snow 16 squares wide; 2 the snow powder "
     "spreading to both sides 30 wide and 8 tall, a few small ice chips flying up at mirrored places; 3 38 wide, thinner; "
     "4 fading wisps at both ends. " + FROST + ".",
     row(4, 40, 12) + CENTER),
    ("q_hit", "极寒突袭：撞飞，4 帧", "view_effects `league_sejuani_q_hit`（跟随目标，z 2；左右对称）", "20 × 22",
     "被钢鬃撞中挑飞（参考 hiteffect、z_iceshards、sejuani_frostout）：白色的冲击闪光，**一圈冰碴和雪粉往上溅**，像被撞上天。"
     "**左右对称**，4 帧。",
     FL + ", " + IC + ", " + SN,
     "A TUSK IMPACT, 4 frames, " + LR + ": 1 a white impact flash 10 squares across low on the target; 2 ice shards and "
     "snow powder bursting UP and out 18 across in a V at mirrored places; 3 the shards high, 21 tall; 4 fading snow "
     "specks. " + FROST + ". " + TARGET + ".",
     row(4, 20, 22) + CENTER),
    ("f_mark", "极寒突袭：撞中英雄的一闪，3 帧", "view_effects `league_sejuani_f_mark`（跟随目标，z 3；左右对称）", "10 × 10",
     "冲锋撞中第一个英雄时，敌人头上一闪的**小冰晶**（参考 e_frostcrystal、sparkles）。**左右对称**，3 帧。",
     GL + ", " + FL,
     "A FROST GLINT, 3 frames, " + LR + ": 1 a tiny white sparkle 3 squares; 2 a cyan six-pointed ice crystal 9 across "
     "with a white centre; 3 the crystal fading. " + FROST + ".",
     row(3, 10, 10) + CENTER),
    # ---- W Winter's Wrath
    ("w_sweep", "凛冬之怒：链枷横扫一圈，5 帧", "view_effects `league_sejuani_w_sweep`（大表，在她脚下，跟随，z -1；左右对称）",
     "60 × 24",
     "凛冬之怒第一下（参考 w_swipe_01、w2a_swipe、w_swipepan_mask）：链枷在她身边**横扫一圈**，地上留下一道**冰蓝色的弧形风雪**，"
     "弧的两头甩出雪粉和冰碴。从斜上方看是一个扁椭圆的环。**左右对称**，5 帧。",
     IC + ", " + SN + ", " + GL,
     "A SWEEPING FROST ARC, 5 frames, " + LR + ": " + FEET + ", 1 a thin pale blue arc starting at the front 20 squares "
     "wide; 2 the arc grown into a ring 50 wide and 16 tall, white at its leading edges, snow powder streaming off it; "
     "3 the full ring 58 wide and 22 tall, cyan ice light along it, ice chips flung out at mirrored places; 4 the ring "
     "breaking into snow; 5 fading. The middle (her body) left empty. " + FROST + ". " + HER + ".",
     row(5, 60, 24) + CENTER),
    ("w_line", "凛冬之怒：往前砸出的一道冰，3 帧循环",
     "view_projectiles `league_sejuani_w_line`（直线弹道，很快，z 2；上下对称）", "40 × 10",
     "凛冬之怒第二下（参考 w_tar_hit_flash、w_swipe_01、z_iceshards）：链枷往前猛砸，**一排冰刺沿着地面往前冲**——"
     "前头一块大冰刺，后面一串越来越小的冰碴和雪粉。**朝右飞、上下对称**，3 帧循环。",
     IC + ", " + SN + ", " + FL,
     "A RACING LINE OF ICE, 3 looping frames, " + TB + ": a jagged pale blue ice spike 8 squares long at the front (white "
     "glints on its edges), behind it on the left a row of smaller ice shards and white snow powder 30 long, the shards "
     "getting smaller toward the tail; the shards flicker and shift a step back frame to frame. " + FROST + ".",
     row(3, 40, 10) + CENTER),
    ("w_hit", "凛冬之怒：被链枷打中，3 帧", "view_effects `league_sejuani_w_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被链枷打中（参考 w_tar_sphere、w_tar_hit_flash）：一团**冰蓝色的光球**炸开，几片碎冰往外飞。**左右对称**，3 帧。",
     FL + ", " + IC + ", " + GL,
     "A FROST BURST, 3 frames, " + LR + ": 1 a white-cyan sphere of light 7 squares across on the target's chest; 2 the "
     "sphere bursting 15 across into pale blue ice shards at mirrored places; 3 the shards out and fading. " + FROST + ". "
     + TARGET + ".",
     row(3, 16, 16) + CENTER),
    # ---- passive: Permafrost, the shatter, Frost Armour
    ("e_freeze", "永冻领域：冻住，5 帧", "view_effects `league_sejuani_e_freeze`（跟随目标，z 2；左右对称；约 1 秒）", "24 × 40",
     "霜冻叠满被冻住（参考 e_icering、e_frostcrystal、r_frostmaterial、frostcrystals）：脚下一圈冰环亮起，**一根根冰柱从地上往上长**，"
     "围着敌人结成冰笼（**冰柱在两边，身体中间留空**），顶上几颗冰晶闪光。最后一帧冰笼完整、停住。**左右对称**，5 帧。",
     IC + ", " + GL + ", " + DP + ", " + FL,
     "A FREEZE, 5 frames, " + LR + ": 1 a cyan ice ring " + FEET + " 20 wide; 2 short pale blue ice spikes rising from the "
     "ring on both sides, 10 tall; 3 the spikes 24 tall leaning in round the body, deep blue inside the ice, white "
     "glints on the edges; 4 the ice cage 36 tall with a few crystals sparkling on top; 5 the full cage held (the last "
     "frame, it stays while the stun lasts). The body area in the middle left EMPTY (the unit stays visible through "
     "it). " + FROST + ". " + TARGET + ".",
     row(5, 24, 40) + CENTER),
    ("sh_hit", "碎冰：冰碎开，4 帧", "view_effects `league_sejuani_sh_hit`（跟随目标，z 2；左右对称）", "28 × 32",
     "碎冰（参考 z_iceshards、frostout、shockwave）：被冻住的敌人身上**冰块炸成碎片**——白色闪光，大小冰片往四周飞，下面一圈雪粉。"
     "**左右对称**，4 帧。",
     FL + ", " + IC + ", " + SN,
     "A SHATTER, 4 frames, " + LR + ": 1 a white flash 12 squares across on the target; 2 big pale blue ice chunks "
     "breaking apart and flying out 26 across at mirrored places, a ring of snow powder at the feet; 3 the chunks smaller "
     "and further out, 30 tall; 4 a few last shards and snow specks fading. " + FROST + ". " + TARGET + ".",
     row(4, 28, 32) + CENTER),
    ("fa_armour", "冰霜护甲：她身上的冰霜，4 帧循环",
     "view_buffs `league_sejuani_fa`（tag `fa_armour`，跟随，z 3；左右对称）", "46 × 40",
     "冰霜护甲在身时（参考 passive_shield、passive_shield_activated、sejuani_sheen）：**她和钢鬃外圈一层淡淡的冰蓝色霜光**，"
     "几颗小冰晶在外圈一闪一闪。**只画外圈，身体位置留空**。**左右对称**，4 帧循环。",
     GL + ", " + IC + ", " + FL,
     "A FROST ARMOUR SHEEN, 4 looping frames, " + LR + ": a thin broken outline of pale cyan frost light round the unit "
     "(1 square thick, gaps in it), 44 squares wide and 38 tall, with three or four small white-cyan ice crystals at "
     "mirrored places on it twinkling in turn; the middle EMPTY. " + FROST + ". " + HER + ".",
     row(4, 46, 40) + CENTER),
    ("frost", "霜冻层数：敌人头上的雪花，2 帧循环",
     "view_buffs `league_sejuani_frost`（附加包的霜冻层，跟随，头上，z 3；左右对称）", "7 × 7",
     "附加包里每层霜冻挂在敌人身上：头上一个**小雪花**（参考 e_stack_1_c…e_stack_4_c）。**左右对称**，2 帧循环。",
     GL + ", " + FL,
     "A SNOWFLAKE MARK, 2 looping frames, " + LR + ": a small six-armed cyan-white snowflake 7 squares across; frame 2 "
     "its centre one shade brighter. Drawn at the TOP of the cell (it sits over the unit's head). " + FROST + ".",
     row(2, 7, 7) + CENTER),
    ("slow", "减速：脚下的风雪，4 帧循环",
     "view_buffs `league_sejuani_w_slow` / `league_sejuani_r_slow`（tag `slow`，跟随，脚下，z -1；左右对称）", "18 × 7",
     "被减速的敌人脚下：一圈**白色雪粉和冰碴**绕着脚慢慢转。**左右对称**，4 帧循环。",
     SN + ", " + IC,
     "A SNOW SNARE, 4 looping frames, " + LR + ": a flat ring of white snow powder and small pale blue ice chips " + FEET +
     " 16 wide and 5 tall, the chips at mirrored places stepping round frame to frame. " + FROST + ".",
     row(4, 18, 7) + CENTER),
    # ---- R Glacial Prison
    ("r_bola", "极冰寒狱：飞出去的冰套索，3 帧循环", "view_projectiles `league_sejuani_r_bola`（直线弹道，z 2；圆形，两个方向都对称）",
     "14 × 14",
     "甩出去的**冰套索**（参考 r_smallbola、r_mis_bolablur、bola_flash）：中间一颗冰蓝色的冰球，外面一圈旋转的白色模糊光环（像绳子转成的圈）。"
     "**圆的：左右、上下都对称**，3 帧循环。",
     IC + ", " + GL + ", " + FL,
     "A SPINNING ICE BOLA, 3 looping frames, " + BOTH + ": a pale blue ice ball 6 squares across with a white glint in "
     "the middle, a spinning white-cyan blur ring round it 13 across, its brighter arcs at mirrored places moving round "
     "frame to frame (each frame itself symmetric). " + FROST + ".",
     row(3, 14, 14) + CENTER),
    ("r_hit", "极冰寒狱：套中冻住，5 帧", "view_effects `league_sejuani_r_hit`（跟随目标，z 2；左右对称）", "28 × 44",
     "套索打中第一个英雄（参考 r_groundfreeze、r_groundfreezeflash、r_frostmaterial、frostcrystals）：白色闪光，**大块的冰晶从地上猛地长起来把它冻在里面**"
     "（比永冻领域的冰笼更大更粗），脚下一片冰面。**冰在两边，身体中间留空**。**左右对称**，5 帧。",
     FL + ", " + IC + ", " + DP + ", " + GL,
     "A GLACIAL PRISON, 5 frames, " + LR + ": 1 a white flash 14 squares across; 2 a frozen patch " + FEET + " 26 wide and "
     "big pale blue ice crystals bursting up on both sides 20 tall; 3 the crystals 36 tall, thick and angular, deep blue "
     "inside, white edges; 4 the prison 42 tall with cyan light along the cracks; 5 the prison held, a few glints (the "
     "last frame). The body area in the middle left EMPTY. " + FROST + ". " + TARGET + ".",
     row(5, 28, 44) + CENTER),
    ("r_storm", "极冰寒狱：冰风暴，6 帧循环", "view_effects `league_sejuani_r_storm`（大表，落点的地上，不跟随，z -1；左右对称；约 2 秒）",
     "64 × 30",
     "套索落下的地方（参考 r_groundfreeze、flurrys、clouds、sejuani_mist、temp_r_tempsnow_chunks）：地上冻出一大片**冰面**，"
     "上面**风雪在转圈**——白色雪粉和冰碴沿着圈旋转，边上几块冰晶竖起来。要持续 2 秒，画成循环。**左右对称**，6 帧循环。",
     IC + ", " + SN + ", " + GL,
     "AN ICE STORM ON THE GROUND, 6 looping frames, " + LR + ": " + FEET + ", a frozen pale blue patch 50 squares wide and "
     "16 tall with cyan cracks, white snow powder and small ice chips swirling round it in a ring 62 wide and 28 tall (in "
     "frame k the left and right halves mirror each other, the specks a step further round each frame), a few short ice "
     "crystals standing at the rim at mirrored places. " + FROST + ".",
     row(6, 64, 30) + CENTER),
]
BIG_FX = ["w_sweep", "r_storm"]
FLYING = ["w_line"]
ROUND = ["r_bola"]
FORWARD = []

GROUPS = [
    ("a_hit (the flail)", ["sejuani_basicattack_trail_01", "sejuani_base_frostcrystals", "sejuani_base_sparkles",
                           "sejuani_base_z_iceshards"]),
    ("q_dash q_hit f_mark (Arctic Assault)", ["sejuani_dust_01", "sejuani_base_z_smoke_4x4", "sejuani_flurrys",
                                              "sejuani_frostout"]),
    ("w_sweep w_line w_hit (Winter's Wrath)", ["sejuani_base_w_swipe_01", "sejuani_base_w2a_swipe",
                                               "sejuani_base_w_tar_hit_flash", "sejuani_base_w_tar_sphere"]),
    ("e_freeze frost (Permafrost)", ["sejuani_base_e_icering", "sejuani_base_e_frostcrystal", "sejuani_base_e_stack_4_c",
                                     "sejuani_base_r_frostmaterial"]),
    ("sh_hit fa_armour (shatter, Frost Armour)", ["sejuani_shockwave", "sejuani_base_passive_shield",
                                                  "sejuani_base_passive_shield_activated", "sejuani_sheen"]),
    ("r_bola r_hit (Glacial Prison)", ["sejuani_base_r_smallbola", "sejuani_base_r_mis_bolablur", "sejuani_bola_flash",
                                       "sejuani_base_r_groundfreezeflash"]),
    ("r_storm slow (the ice storm)", ["sejuani_base_r_groundfreeze", "sejuani_base_clouds", "sejuani_mist",
                                      "sejuani_base_temp_r_tempsnow_chunks"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", ppu=PPU):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / ppu, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Sejuani at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"瑟庄妮 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 北地之怒 瑟庄妮：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/sejuani_design.png`：Q 版的瑟庄妮——青铜金头盔、两只蓝冰角、紫皮甲、"
      "米白毛领、棕黑相间的链枷和蓝色冰锤头——骑在灰蓝毛、白鬃毛、两根象牙色大獠牙的野猪钢鬃背上）。"
      f"她在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），{h} 格高、{w} 格宽（高×宽，冰角尖到蹄子）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sejuani_size.png`：瑟庄妮放大 4 倍，最低点在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里瑟庄妮自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。"
      "**瑟庄妮是北地之怒**：她的力量是**冰霜**——白色到淡蓝的**有棱角的冰晶和冰碴**、**青色的冰光**、冰里深蓝的暗部、**白色的雪粉和风雪**；"
      "不要火、不要电、不要烟。")
    a("> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。")
    a("> - **冰、雪、冲击都没有黑描边**（用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（冻住的冰笼也是：冰在两边，中间留空）。")
    a("> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）；`" + "`、`".join(ROUND) +
      "` 是圆的，**左右、上下都对称**。")
    a("> - **持续的画面**（冰风暴 2 秒、冰霜护甲、减速、霜冻层数）只画几帧循环，Claude 导入时按时长拉开循环；冻住的两张（`e_freeze`、`r_hit`）最后一帧会停住。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sejuani_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/sejuani_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 冰锤链枷砸下 | `a_hit` |")
    a("| 被动「北地之怒」 | 脱战时冰霜护甲（免疫减速）；霜冻叠满冻住（永冻领域）；打晕住的敌人碎冰 | `fa_armour` · `frost` · `e_freeze` · `sh_hit` |")
    a("| 技能 1 =「极寒突袭」 | 钢鬃冲锋，撞飞路上的敌人，撞到英雄停下 | `q_dash` · `q_hit` · `f_mark` |")
    a("| 技能 2 =「凛冬之怒」 | 链枷先横扫一圈，再往前砸出一道冰；减速、叠霜冻 | `w_sweep` · `w_line` · `w_hit` · `slow` |")
    a("| 大招 =「极冰寒狱」 | 甩出冰套索，冻住第一个英雄，落点冰风暴减速 | `r_bola` · `r_hit` · `r_storm` · `slow` |\n")
    a("连招：**Q 撞飞 → 马上 W**，**W 叠满霜冻 → 冻住**，**晕住（谁晕的都算）→ 碎冰**，**R 冻住 → Q 冲过去**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**冰、雪、冲击没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂；冰晶是有棱角的块，不是圆团。")
    a("- **要亮**：每个形状都有最亮一档或白色的亮点。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("冰·白到深蓝", ICE), ("冰光·青", GLOW), ("雪·白到灰蓝", SNOW), ("冰里的暗部·深蓝", DEEP),
                        ("闪光·白", FLASH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的东西（横扫的环、冰风暴、脚下的冰环）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sejuani_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `sejuani_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_sejuani_fx`（小的）和 `league_sejuani_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_sejuani.py 的 views；w_slow 和 r_slow 用 `slow`，fa 用 `fa_armour`，附加包的 frost 用 `frost`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称，{'、'.join(ROUND)} 两个方向都对称；其余断言左右对称。r_storm 循环 r_storm（120 tick），"
      "fa_armour / slow / frost 循环；e_freeze 的最后一帧停到 e_stun，r_hit 的最后一帧停到 r_stun。")
    a("- 用 `pixel_1x/` 切格（import_belveth_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sejuani_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "sejuani_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_sejuani.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "sejuani_design.png"))
    shape = size_sheet(os.path.join(out, "design", "sejuani_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sejuani_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("both" if x[0] in ROUND else
                                                                ("none (forward)" if x[0] in FORWARD else "left-right"))}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
